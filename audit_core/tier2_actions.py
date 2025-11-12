"""
Tier-2 Step 3.5 — Detect Phases (legacy-compatible, reinstated v16.1.1)
Infers phase segments from validated event-level load data.
Derived directly from legacy v15.4 inline logic.
"""

from audit_core.utils import debug
from datetime import datetime, timedelta
from coaching_cheat_sheet import CHEAT_SHEET
METRIC_ACTION_MAP = CHEAT_SHEET.get("coaching_links", {})


def metric_value(context, key, default=0.0):
    """Return numeric metric value, handling both scalar and dict forms."""
    val = context.get(key, default)
    if isinstance(val, dict):
        return val.get("value", default)
    return val


def detect_phases(context, events):
    # --- Extract event dates and loads ---
    loads = [(e["start_date"], e["icu_training_load"]) for e in events if "icu_training_load" in e]
    loads.sort(key=lambda x: x[0])
    if not loads:
        context["phases"] = [{"phase": "No Data", "start": None, "end": None, "delta": 0.0}]
        return context

    # --- Compute 7-day rolling TSS average ---
    avg7 = []
    for i in range(len(loads)):
        current_date = datetime.fromisoformat(loads[i][0].replace("Z", "+00:00"))
        window = [
            v for d, v in loads
            if 0 <= (current_date - datetime.fromisoformat(d.replace("Z", "+00:00"))).days <= 7
        ]
        avg7.append(sum(window) / len(window))

    # --- Detect inflection points (>±15 % change) ---
    phases = []
    start_idx = 0
    for i in range(1, len(avg7)):
        prev = avg7[i - 1]
        delta = (avg7[i] - prev) / max(prev, 1)
        if abs(delta) > 0.15:
            label = "Build" if delta > 0 else "Deload"
            phases.append({
                "phase": label,
                "start": loads[start_idx][0],
                "end": loads[i][0],
                "delta": round(delta, 2)
            })
            start_idx = i

    # --- Fallback if no detectable phase transitions ---
    if not phases:
        phases.append({
            "phase": "Continuous Load",
            "start": loads[0][0],
            "end": loads[-1][0],
            "delta": 0.0
        })

    context["phases"] = phases
    return context


"""
Tier-2 Step 4 — Evaluate Coaching Actions (v16.1.1)
Applies heuristics to validated derived metrics, outputs recommendations.
Now includes automatic phase detection from event-level data.
"""


def evaluate_actions(context):
    events = context.get("events", [])
    context = detect_phases(context, events)

    # --- Integrate Derived + Extended Metrics (URF v5.2+)
    derived = context.get("derived_metrics", {})
    extended = context.get("extended_metrics", {})

    # Promote key metrics into root context for easier heuristic access
    for k in ["ACWR", "Monotony", "Strain", "Polarisation", "RecoveryIndex"]:
        if k in derived:
            context[k] = derived[k]
    for k in ["Durability", "LoadIntensityRatio", "EnduranceReserve", "IFDrift", "FatOxidation"]:
        if k in extended:
            context[k] = extended[k]

    debug(context, "[T2-ACTIONS] Integrated derived metrics:")
    debug(context, derived)
    debug(context, "[T2-ACTIONS] Integrated extended metrics:")
    debug(context, extended)

    actions = []

    # --- Metric Context Summary (link metrics to coaching relevance) ---
    from coaching_cheat_sheet import CHEAT_SHEET
    metric_links = CHEAT_SHEET.get("coaching_links", {})
    derived = context.get("derived_metrics", {})
    adapt = context.get("adaptation_metrics", {})

    metric_contexts = []
    actions = []

    def summarize_metric(k, v):
        """Generate human-readable, context-aware recommendation for each metric."""
        if not isinstance(v, dict):
            return None
        val = v.get("value")
        icon = v.get("icon", "")
        status = v.get("status", "")
        desc = metric_links.get(k, "")

        if status in ["out of range", "borderline"]:
            return f"⚠ {k} ({val}) — {desc}"
        elif status == "optimal":
            return f"✅ {k} ({val}) — {desc}"
        return None

    # Derived and adaptation metrics combined
    for metrics in [derived, adapt]:
        for k, v in metrics.items():
            rec = summarize_metric(k, v)
            if rec:
                metric_contexts.append(rec)

    context["metric_contexts"] = metric_contexts

    # --- Polarisation / Intensity Balance ---
    if metric_value(context, "Polarisation") >= 0.7:
        actions.append("✅ Maintain ≥70 % Z1–Z2 volume (Seiler 80/20).")
    else:
        actions.append("⚠ Increase Z1–Z2 share to ≥70 % (Seiler 80/20).")

    # --- Metabolic Efficiency ---
    if metric_value(context, "FatOxidation") >= 0.8 and metric_value(context, "Decoupling", 1.0) <= 0.05:
        actions.append("✅ Metabolic efficiency maintained (San Millán Zone 2).")
    else:
        actions.append("⚠ Improve Zone 2 efficiency: extend duration or adjust IF.")

    # --- Recovery and Load Balance ---
    if metric_value(context, "RecoveryIndex", 1.0) < 0.6:
        if metric_value(context, "ACWR", 1.0) > 1.2:
            actions.append("⚠ Apply 30–40 % deload (Friel microcycle logic).")
        else:
            actions.append("⚠ Apply 10–15 % deload (Friel microcycle logic).")

    # --- Benchmark Maintenance ---
    if context.get("weeks_since_last_FTP", 0) >= 6:
        actions.append("🔄 Retest FTP/LT1 for updated benchmarks.")

    # --- FatMax Verification ---
    if abs(metric_value(context, "FatMaxDeviation", 1.0)) <= 0.05 and metric_value(context, "Decoupling", 1.0) <= 0.05:
        actions.append("✅ FatMax calibration verified (±5 %).")

    # --- Visual Fatigue Flag (v16.1.3 legacy cosmetic) ---
    ri = metric_value(context, "RecoveryIndex", 1.0)
    if ri < 0.6:
        context["ui_flag"] = "🔴 Overreached"
    elif ri < 0.8:
        context["ui_flag"] = "🟠 Fatigued"
    else:
        context["ui_flag"] = "🟢 Normal"

    # --- New Heuristics (URF v5.2 enhancement with metric values) ---

    # Durability / Fatigue Resistance
    dur = metric_value(context, "Durability", 1.0)
    if dur < 0.8:
        actions.append(f"⚠ Durability low ({dur:.2f}) — extend steady-state endurance or increase time-in-zone.")
    elif dur >= 1.0:
        actions.append(f"✅ Durability improving ({dur:.2f}) — maintain current long-ride structure.")

    # Load Intensity Ratio (LIR)
    lir = metric_value(context, "LoadIntensityRatio", 0.0)
    if lir > 1.2:
        actions.append(f"⚠ Load intensity too high (LIR={lir:.2f}) — risk of overreaching; reduce threshold/VO₂ blocks.")
    elif lir < 0.8:
        actions.append(f"⚠ Load intensity low (LIR={lir:.2f}) — consider adding tempo or sweet-spot intervals.")
    else:
        actions.append(f"✅ Load intensity balanced (LIR={lir:.2f}).")

    # Endurance Reserve
    er = metric_value(context, "EnduranceReserve", 1.0)
    if er < 0.8:
        actions.append(f"⚠ Endurance reserve depleted ({er:.2f}) — add recovery or split long sessions.")
    elif er >= 1.0:
        actions.append(f"✅ Endurance reserve strong ({er:.2f}).")

    # IF Drift (efficiency decay)
    drift = metric_value(context, "IFDrift", 0.0)
    if drift > 0.06:
        actions.append(f"⚠ Efficiency drift high ({drift:.2%}) — improve aerobic durability or reduce fatigue load.")
    else:
        actions.append(f"✅ Efficiency drift stable ({drift:.2%}).")

    # Polarisation feedback (reinforces Seiler balance)
    pol = metric_value(context, "Polarisation", 0.0)
    if pol < 0.7:
        actions.append(f"⚠ Polarisation low ({pol:.0%}) — increase Z1–Z2 share toward ≥70 %.")
    else:
        actions.append(f"✅ Polarisation optimal ({pol:.0%}).")

    # Recovery Index review
    ri = metric_value(context, "RecoveryIndex", 1.0)
    if ri < 0.6:
        actions.append(f"⚠ Recovery Index poor ({ri:.2f}) — insert deload or reduce intensity.")
    elif ri < 0.8:
        actions.append(f"🟠 Recovery Index moderate ({ri:.2f}) — monitor fatigue trend.")
    else:
        actions.append(f"✅ Recovery Index healthy ({ri:.2f}).")

    # --- Merge dynamic metric feedback into action list ---
    if "metric_contexts" in context and context["metric_contexts"]:
        actions.extend([
            "---",
            "📊 Metric-based Feedback:"
        ] + context["metric_contexts"])

    # --- Finalize and inject ---
    context["actions"] = actions
    return context

