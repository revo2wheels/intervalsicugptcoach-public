"""
Tier-2 Step 3.5 — Detect Phases (legacy-compatible, reinstated v16.1.1)
Infers phase segments from validated event-level load data.
Derived directly from legacy v15.4 inline logic.
"""
import numpy as np
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
    """
    Tier-2 Phase Detection (URF v5.3)
    Derives macrocycle phases: Base, Build, Peak, Taper, Recovery
    using 7-day rolling TSS averages and ACWR thresholds.
    """

    loads = [(e["start_date"], e.get("icu_training_load", 0)) for e in events if "icu_training_load" in e]
    loads.sort(key=lambda x: x[0])
    if not loads:
        context["phases"] = [{"phase": "No Data", "start": None, "end": None, "delta": 0.0}]
        return context

    # --- Compute rolling 7-day mean TSS ---
    avg7 = []
    for i in range(len(loads)):
        current_date = datetime.fromisoformat(loads[i][0].replace("Z", "+00:00"))
        window = [
            v for d, v in loads
            if 0 <= (current_date - datetime.fromisoformat(d.replace("Z", "+00:00"))).days <= 7
        ]
        avg7.append(sum(window) / max(len(window), 1))

    # --- Detect transitions using load delta + ACWR heuristics ---
    phases = []
    start_idx = 0
    acwr = context.get("ACWR", 1.0)
    ri = context.get("RecoveryIndex", 0.8)

    for i in range(1, len(avg7)):
        prev = avg7[i - 1]
        delta = (avg7[i] - prev) / max(prev, 1)

        if delta > 0.20 and acwr <= 1.3:
            label = "Build"
        elif delta > 0.20 and acwr > 1.3:
            label = "Overreach"
        elif delta < -0.20 and ri >= 0.8:
            label = "Recovery"
        elif delta < -0.20 and ri < 0.6:
            label = "Taper"
        elif 0.05 < delta <= 0.20:
            label = "Base"
        else:
            label = None

        if label:
            phases.append({
                "phase": label,
                "start": loads[start_idx][0],
                "end": loads[i][0],
                "delta": round(delta, 2)
            })
            start_idx = i

    # --- Assign Peak if late-season sustained high load ---
    if phases and phases[-1]["phase"] in ["Build", "Overreach"]:
        last_delta = phases[-1]["delta"]
        if abs(last_delta) <= 0.05 and acwr >= 1.0 and ri >= 0.7:
            phases.append({
                "phase": "Peak",
                "start": loads[-7][0] if len(loads) > 7 else loads[-1][0],
                "end": loads[-1][0],
                "delta": 0.0
            })

    # --- Fallback continuous load pattern ---
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

    # --- Integrate Derived + Extended Metrics (URF v5.1)
    derived = context.get("derived_metrics", {})
    extended = context.get("extended_metrics", {})

    # Promote metrics only if context lacks a scalar version
    for k in ["ACWR", "Monotony", "Strain", "Polarisation", "RecoveryIndex"]:
        if k not in context or isinstance(context[k], dict):
            if k in derived and isinstance(derived[k], dict):
                val = derived[k].get("value", np.nan)
                if isinstance(val, (int, float)) and not np.isnan(val):
                    context[k] = float(val)

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

    # --- Visual Fatigue Flag (legacy cosmetic) ---
    ri = metric_value(context, "RecoveryIndex", 1.0)
    if ri < 0.6:
        context["ui_flag"] = "🔴 Overreached"
    elif ri < 0.8:
        context["ui_flag"] = "🟠 Fatigued"
    else:
        context["ui_flag"] = "🟢 Normal"

    # --- New Heuristics (URF v5.1 enhancement) ---
    dur = metric_value(context, "Durability", 1.0)
    lir = metric_value(context, "LoadIntensityRatio", 0.0)
    er = metric_value(context, "EnduranceReserve", 1.0)
    drift = metric_value(context, "IFDrift", 0.0)
    pol = metric_value(context, "Polarisation", 0.0)
    ri = metric_value(context, "RecoveryIndex", 1.0)

    if dur < 0.8:
        actions.append(f"⚠ Durability low ({dur:.2f}) — extend steady-state endurance or increase time-in-zone.")
    elif dur >= 1.0:
        actions.append(f"✅ Durability improving ({dur:.2f}) — maintain current long-ride structure.")

    if lir > 1.2:
        actions.append(f"⚠ Load intensity too high (LIR={lir:.2f}) — reduce threshold/VO₂ blocks.")
    elif lir < 0.8:
        actions.append(f"⚠ Load intensity low (LIR={lir:.2f}) — add tempo or sweet-spot intervals.")
    else:
        actions.append(f"✅ Load intensity balanced (LIR={lir:.2f}).")

    if er < 0.8:
        actions.append(f"⚠ Endurance reserve depleted ({er:.2f}) — add recovery or split long sessions.")
    elif er >= 1.0:
        actions.append(f"✅ Endurance reserve strong ({er:.2f}).")

    if drift > 0.06:
        actions.append(f"⚠ Efficiency drift high ({drift:.2%}) — improve aerobic durability or reduce fatigue load.")
    else:
        actions.append(f"✅ Efficiency drift stable ({drift:.2%}).")

    if pol < 0.7:
        actions.append(f"⚠ Polarisation low ({pol:.0%}) — increase Z1–Z2 share toward ≥70 %.") 
    else:
        actions.append(f"✅ Polarisation optimal ({pol:.0%}).")

    if ri < 0.6:
        actions.append(f"⚠ Recovery Index poor ({ri:.2f}) — insert deload or reduce intensity.")
    elif ri < 0.8:
        actions.append(f"🟠 Recovery Index moderate ({ri:.2f}) — monitor fatigue trend.")
    else:
        actions.append(f"✅ Recovery Index healthy ({ri:.2f}).")

    # ===================================================================
    # 🪜 SEASONAL PHASE ANALYSIS (Aligned with Coaching Cheat Sheet)
    # ===================================================================
    report_type = str(context.get("report_type", "")).lower()
    if report_type == "season" and "phases" in context:
        actions.append("---")
        actions.append("🪜 **Seasonal Phase Analysis**")

        for ph in context["phases"]:
            phase = ph.get("phase", "Unknown")
            delta = ph.get("delta", 0)
            start = ph.get("start", "")
            end = ph.get("end", "")
            acwr = context.get("ACWR", 1.0)
            ri = context.get("RecoveryIndex", 0.8)

            # --- Map phase to coaching heuristic ---
            if phase == "Base":
                actions.append(f"🧱 **Base phase detected** ({start} → {end}) — focus on aerobic volume (Z1–Z2 ≥ 70%), maintain ACWR ≤ 1.0.")
            elif phase == "Build":
                actions.append(f"📈 **Build phase detected** ({start} → {end}, Δ+{delta*100:.0f}%) — progressive overload active; maintain ACWR ≤ 1.3.")
            elif phase == "Peak":
                actions.append(f"🏁 **Peak phase detected** ({start} → {end}) — high-intensity emphasis; monitor fatigue (RI ≥ 0.6).")
            elif phase == "Taper":
                actions.append(f"📉 **Taper phase detected** ({start} → {end}) — reduce ATL by 30–50%, maintain intensity; expected RI ↑.")
            elif phase == "Recovery":
                actions.append(f"💤 **Recovery phase detected** ({start} → {end}) — active regeneration; target RI ≥ 0.8 and low monotony.")
            elif phase == "Deload":
                actions.append(f"🧘 **Deload phase detected** ({start} → {end}) — reduced load, maintain frequency; transition readiness improving.")
            else:
                actions.append(f"🔁 **Continuous Load** ({start} → {end}) — steady training; insert variation if fatigue rises.")

        # --- Summary coach note (directly from cheat sheet logic) ---
        actions.append("")
        actions.append("📘 **Coach Note:**")
        actions.append(
            "Phases correspond to the macrocycle model (Base → Build → Peak → Taper → Recovery). "
            "Maintain ACWR ≤ 1.3, positive TSB for freshness, and use taper reduction of ATL by 30–50%. "
            "Derived from Friel / Seiler / Bannister periodisation heuristics."
        )

        actions.append("✅ Reference: Coaching Cheat Sheet — Periodisation & Load Ratios (Section 9–11)")

    # --- Merge metric-based feedback ---
    if "metric_contexts" in context and context["metric_contexts"]:
        actions.extend([
            "---",
            "📊 Metric-based Feedback:"
        ] + context["metric_contexts"])

    # Sync derived_metrics with latest scalar values
    for k in ["ACWR", "Monotony", "Strain", "Polarisation", "RecoveryIndex"]:
        if k in derived and isinstance(derived[k], dict):
            derived[k]["value"] = context.get(k, derived[k].get("value", np.nan))
    context["derived_metrics"] = derived

    # --- Finalize ---
    context["actions"] = actions
    return context

def generate_coaching_actions(context):
    """
    Unified Tier-2 coaching action generator.
    Bridges phase detection, fatigue, load summaries, and adaptive hints.
    Safe to call from report_controller for all report types.
    """
    try:
        # Phase detection (seasonal only)
        if context.get("report_type", "").lower() == "season":
            if "df_events" in context and not context["df_events"].empty:
                from audit_core.tier2_actions import detect_phases
                context["phase_analysis"] = detect_phases(context["df_events"])
                debug(context, f"[ACTIONS] Phase analysis complete ({len(context['phase_analysis'])} phases)")
            else:
                debug(context, "[ACTIONS] Skipped phase detection — df_events missing or empty.")

        # Load summary
        from coaching_cheat_sheet import summarize_load_block
        context["load_summary"] = summarize_load_block(context)

        debug(context, "[ACTIONS] Coaching actions synthesized successfully.")
        return context

    except Exception as e:
        debug(context, f"[ACTIONS ERROR] Failed to build coaching actions → {e}")
        return context
