"""
Tier-2 Step 3.5 — Detect Phases (legacy-compatible, reinstated v16.1.1)
Infers phase segments from validated event-level load data.
Derived directly from legacy v15.4 inline logic.
"""
import numpy as np
import pandas as pd
from audit_core.utils import debug
from datetime import datetime, timedelta
from coaching_cheat_sheet import CHEAT_SHEET
METRIC_ACTION_MAP = CHEAT_SHEET.get("coaching_links", {})

def metric_value(context, key, default=0.0):
    """Return numeric metric value, handling None, NaN, and dict forms safely."""
    val = context.get(key, default)
    if isinstance(val, dict):
        val = val.get("value", default)
    try:
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return default
        return float(val)
    except (TypeError, ValueError):
        return default


def detect_phases(context, events):
    """
    Tier-2 Phase Detection (URF v5.4)
    Derives macrocycle phases: Base, Build, Peak, Taper, Recovery
    using *weekly-aggregated* TSS trends across the entire dataset
    (90-day or 365-day "light" activity feed).

    Rationale:
    ----------
    - Aggregates activity TSS (icu_training_load) by ISO week
    - Detects major week-to-week deltas (growth/decline patterns)
    - Modulates classification using ACWR and RecoveryIndex if present
    - Works for variable durations (season or annual)
    - Never outputs "No Data" unless dataset truly empty
    """

    debug(context, "[PHASES] ---- Phase detection start ----")

    # --- Validate input
    if not events or not isinstance(events, (list, tuple)):
        debug(context, "[PHASES] No event list provided")
        context["phases"] = [{"phase": "No Data", "start": None, "end": None, "delta": 0.0}]
        return context

    # --- Extract load + timestamp
    df = pd.DataFrame(events)
    if df.empty or "icu_training_load" not in df.columns:
        debug(context, "[PHASES] Empty DataFrame or no icu_training_load field")
        context["phases"] = [{"phase": "No Data", "start": None, "end": None, "delta": 0.0}]
        return context

    # --- Normalize timestamps
    date_col = "start_date_local" if "start_date_local" in df.columns else "start_date"
    df["date"] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=["date"])
    df = df.sort_values("date")

    # --- Aggregate by ISO week
    df["week_start"] = df["date"].dt.to_period("W").apply(lambda r: r.start_time)
    df_week = (
        df.groupby("week_start")
          .agg({"icu_training_load": "sum"})
          .reset_index()
          .rename(columns={"icu_training_load": "tss"})
    )
    debug(context, f"[PHASES] Aggregated {len(df_week)} weekly points from {len(df)} activities")

    if df_week.empty:
        context["phases"] = [{"phase": "No Data", "start": None, "end": None, "delta": 0.0}]
        return context

    # --- Compute week-to-week deltas
    df_week["delta"] = df_week["tss"].pct_change().fillna(0)
    df_week["delta"] = df_week["delta"].clip(-1, 2)  # prevent crazy spikes

    # --- Contextual modifiers
    acwr = context.get("ACWR", 1.0)
    ri = context.get("RecoveryIndex", 0.8)

    # --- Dynamic threshold scaling (auto-adjust for dataset variance)
    var_tss = df_week["tss"].std() / max(df_week["tss"].mean(), 1)
    scale = 0.20 if var_tss > 0.3 else 0.15 if var_tss > 0.15 else 0.10

    debug(context, f"[PHASES] Variability={round(var_tss,3)} → Δ threshold scale={scale}")

    # --- Classify each transition
    phases = []
    start_idx = 0

    for i in range(1, len(df_week)):
        delta = df_week.iloc[i]["delta"]
        label = None

        if delta > scale and acwr <= 1.3:
            label = "Build"
        elif delta > scale and acwr > 1.3:
            label = "Overreach"
        elif delta < -scale and ri >= 0.8:
            label = "Recovery"
        elif delta < -scale and ri < 0.6:
            label = "Taper"
        elif abs(delta) <= scale / 2:
            label = "Base"

        if label:
            start = df_week.iloc[start_idx]["week_start"]
            end = df_week.iloc[i]["week_start"]
            phases.append({
                "phase": label,
                "start": start.strftime("%Y-%m-%d"),
                "end": end.strftime("%Y-%m-%d"),
                "delta": round(float(delta), 3)
            })
            debug(context, f"[PHASES] Δ{round(delta,3)} → {label} ({start} → {end})")
            start_idx = i

    # --- Detect sustained plateau (Peak)
    if phases:
        last_phase = phases[-1]["phase"]
        if last_phase in ["Build", "Overreach"]:
            mean_recent = df_week["tss"].tail(4).mean()
            mean_prior = df_week["tss"].head(4).mean()
            if abs(mean_recent - mean_prior) / max(mean_prior, 1) < 0.05:
                phases.append({
                    "phase": "Peak",
                    "start": df_week["week_start"].iloc[-4].strftime("%Y-%m-%d")
                            if len(df_week) >= 4 else df_week["week_start"].iloc[-1].strftime("%Y-%m-%d"),
                    "end": df_week["week_start"].iloc[-1].strftime("%Y-%m-%d"),
                    "delta": 0.0
                })
                debug(context, "[PHASES] Added Peak phase at stable high-load region")

    # --- Fallback
    if not phases:
        debug(context, "[PHASES] No distinct transitions — continuous pattern assumed")
        phases.append({
            "phase": "Continuous Load",
            "start": df_week["week_start"].iloc[0].strftime("%Y-%m-%d"),
            "end": df_week["week_start"].iloc[-1].strftime("%Y-%m-%d"),
            "delta": 0.0
        })

    # --- Add duration metadata for interpretability ---
    for p in phases:
        try:
            start_dt = pd.to_datetime(p.get("start"))
            end_dt = pd.to_datetime(p.get("end"))
            if pd.notna(start_dt) and pd.notna(end_dt):
                p["duration_days"] = int((end_dt - start_dt).days)
                p["duration_weeks"] = round(p["duration_days"] / 7, 1)
            else:
                p["duration_days"] = None
                p["duration_weeks"] = None
        except Exception as e:
            debug(context, f"[PHASES] Duration calc failed for {p}: {e}")
            p["duration_days"] = None
            p["duration_weeks"] = None

    # --- Finalize
    context["phases"] = phases
    debug(context, f"[PHASES] Completed detection → {len(phases)} phases")
    for p in phases:
        debug(context, f"[PHASES] → {p}")
    debug(context, "[PHASES] ---- Phase detection end ----")

    return context



"""
Tier-2 Step 4 — Evaluate Coaching Actions (v16.1.1)
Applies heuristics to validated derived metrics, outputs recommendations.
Now includes automatic phase detection from event-level data.
"""


def evaluate_actions(context):
    events = context.get("events", [])
    context = detect_phases(context, events)

    # --- Integrate Derived + Extended Metrics (URF v5.1) ---
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

    debug(context, f"[DEBUG-T2-ACTIONS] Integrated derived metrics sample type={type(derived)} content={str(derived)[:200]}")
    debug(context, f"[DEBUG-T2-ACTIONS] Integrated extended metrics sample type={type(extended)} content={str(extended)[:200]}")

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

    # --- FatigueTrend (Action based on recovery status) ---
    fatigue_trend = metric_value(context, "FatigueTrend", 0.0)
    if fatigue_trend < -0.2:
        actions.append(f"⚠ FatigueTrend ({fatigue_trend}%) — Recovery phase detected. Maintain steady training load and prioritize recovery.")
    elif fatigue_trend >= 0.2:
        actions.append(f"✅ FatigueTrend ({fatigue_trend}%) — Increasing fatigue trend. Consider adjusting intensity or recovery.")

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
    if "LoadIntensityRatio" not in context:
        context["LoadIntensityRatio"] = context.get("StressTolerance", 0.0)

    lir = metric_value(context, "LoadIntensityRatio", 0.0)
    er = metric_value(context, "EnduranceReserve", 1.0)
    drift = metric_value(context, "IFDrift", 0.0)
    pol = metric_value(context, "Polarisation", None)
    if not pol:
        pol = metric_value(context, "PolarisationIndex", 0.0)
    context["Polarisation"] = pol  # ensure key exists for validator
    debug(context, f"[T2-ACTIONS] Polarisation value (safe) = {pol}")
    ri = metric_value(context, "RecoveryIndex", 1.0)

    ri = metric_value(context, "RecoveryIndex", 1.0)

    from coaching_cheat_sheet import CHEAT_SHEET

    # --- Durability ---
    if dur < CHEAT_SHEET["thresholds"]["Durability"]["amber"][0]:
        actions.append(CHEAT_SHEET["advice"]["Durability"]["low"].format(dur))
    elif dur >= CHEAT_SHEET["thresholds"]["Durability"]["green"][0]:
        actions.append(CHEAT_SHEET["advice"]["Durability"]["improving"].format(dur))

    # --- Load Intensity Ratio (LIR) ---
    if lir > CHEAT_SHEET["thresholds"]["LIR"]["amber"][0]:
        actions.append(CHEAT_SHEET["advice"]["LIR"]["high"].format(lir))
    elif lir < CHEAT_SHEET["thresholds"]["LIR"]["green"][0]:
        actions.append(CHEAT_SHEET["advice"]["LIR"]["low"].format(lir))
    else:
        actions.append(CHEAT_SHEET["advice"]["LIR"]["balanced"].format(lir))

    # --- Endurance Reserve ---
    if er < CHEAT_SHEET["thresholds"]["EnduranceReserve"]["amber"][0]:
        actions.append(CHEAT_SHEET["advice"]["EnduranceReserve"]["depleted"].format(er))
    elif er >= CHEAT_SHEET["thresholds"]["EnduranceReserve"]["green"][0]:
        actions.append(CHEAT_SHEET["advice"]["EnduranceReserve"]["strong"].format(er))

    # --- Efficiency Drift ---
    if drift > CHEAT_SHEET["thresholds"]["IFDrift"]["amber"][0]:
        actions.append(CHEAT_SHEET["advice"]["EfficiencyDrift"]["high"].format(drift))
    else:
        actions.append(CHEAT_SHEET["advice"]["EfficiencyDrift"]["stable"].format(drift))

    # --- Polarisation ---
    if pol < CHEAT_SHEET["thresholds"]["Polarisation"]["amber"][0]:
        actions.append(CHEAT_SHEET["advice"]["Polarisation"]["low"].format(pol))
    else:
        actions.append(CHEAT_SHEET["advice"]["Polarisation"]["optimal"].format(pol))

    # --- Recovery Index ---
    if ri < CHEAT_SHEET["thresholds"]["RecoveryIndex"]["amber"][0]:
        actions.append(CHEAT_SHEET["advice"]["RecoveryIndex"]["poor"].format(ri))
    elif ri < CHEAT_SHEET["thresholds"]["RecoveryIndex"]["green"][0]:
        actions.append(CHEAT_SHEET["advice"]["RecoveryIndex"]["moderate"].format(ri))
    else:
        actions.append(CHEAT_SHEET["advice"]["RecoveryIndex"]["healthy"].format(ri))


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
