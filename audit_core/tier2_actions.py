"""
Tier-2 Step 3.5 — Detect Phases (legacy-compatible, reinstated v16.1.1)
Infers phase segments from validated event-level load data.
Derived directly from legacy v15.4 inline logic.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from audit_core.utils import debug
from coaching_cheat_sheet import CHEAT_SHEET
from coaching_profile import COACH_PROFILE

# === Dynamic Heuristics from Cheat Sheet ===
def get_dynamic_heuristics():
    th = CHEAT_SHEET["thresholds"]
    return {
        "polarisation_target":
            sum(th["Polarisation"]["green"]) / 2,
        "recovery_floor":
            th["RecoveryIndex"]["amber"][1],
        "fatigue_delta_green":
            th["FatigueTrend"]["green"],
        "acwr_upper":
            th["ACWR"]["green"][1],
        "fatigue_decay_const": 0.2,
        "efficiency_smoothing": 0.15,
    }

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
    """
    Tier-2 Step 4 — Evaluate Coaching Actions (v17 dynamic)
    Fully dynamic thresholds and phase advice integration.
    """
    events = context.get("events", [])
    context = detect_phases(context, events)
    heur = get_dynamic_heuristics()

    derived = context.get("derived_metrics", {})
    extended = context.get("extended_metrics", {})

    # Promote metrics
    for k in ["ACWR", "Monotony", "Strain", "Polarisation", "RecoveryIndex"]:
        if k not in context or isinstance(context[k], dict):
            if k in derived and isinstance(derived[k], dict):
                val = derived[k].get("value", np.nan)
                if isinstance(val, (int, float)) and not np.isnan(val):
                    context[k] = float(val)
    for k in ["Durability", "LoadIntensityRatio", "EnduranceReserve", "IFDrift", "FatOxidation"]:
        if k in extended:
            context[k] = extended[k]

    debug(context, "[T2-ACTIONS] Derived metrics integrated")

    actions = []

    # ---------------- Metric Context Summary ----------------
    metric_links = CHEAT_SHEET.get("coaching_links", {})
    derived = context.get("derived_metrics", {})
    adapt = context.get("adaptation_metrics", {})
    metric_contexts = []

    def summarize_metric(k, v):
        if not isinstance(v, dict):
            return None
        val, status = v.get("value"), v.get("status", "")
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

    # ---------------- Polarisation / Intensity Balance (fully dynamic via Cheat Sheet) ----------------
    adv = CHEAT_SHEET["advice"]
    thr = CHEAT_SHEET["thresholds"]

    # Collect all metrics whose names begin with "Polarisation"
    polarisation_keys = [
        k for k in adv.keys() if k.startswith("Polarisation") and not k.endswith("_summary")
    ]

    polarisations = {
        key: metric_value(context, key, 0.0)
        for key in polarisation_keys
        if metric_value(context, key, 0.0) > 0
    }

    # Evaluate individual metrics with cheat-sheet thresholds + advice
    for key, val in polarisations.items():
        th = thr.get(key, thr.get("Polarisation", {}))
        adv_block = adv.get(key, {})
        if not th or not adv_block:
            continue

        if val < th.get("amber", (0, 1))[0]:
            msg = adv_block.get("low", "").format(val)
        elif val < th.get("green", (0, 1))[0]:
            msg = adv_block.get("z2_base", adv_block.get("low", "")).format(val)
        else:
            msg = adv_block.get("optimal", "").format(val)

        if msg:
            actions.append(msg)

    # Multi-variant summary message (cross-discipline check)
    low_keys = [
        k for k, v in polarisations.items()
        if v < thr.get(k, thr.get("Polarisation", {})).get("amber", (0, 1))[0]
    ]

    if len(low_keys) >= 2 and "Polarisation_summary" in adv:
        vals_fmt = ", ".join(f"{k}:{v:.2f}" for k, v in polarisations.items())
        actions.append(
            adv["Polarisation_summary"]["low"].format(vals_fmt)
        )

    # ---------------- Metabolic Efficiency ----------------
    fox = context.get("FatOxidation", 0.0)
    decoup = context.get("Decoupling", 1.0)
    if fox >= 0.8 and decoup <= 0.05:
        actions.append("✅ Metabolic efficiency maintained (San Millán Z2).")
    else:
        actions.append("⚠ Improve Zone 2 efficiency — extend duration or adjust IF.")

    # ---------------- Recovery / Load Balance ----------------
    ri = context.get("RecoveryIndex", 1.0)
    acwr = context.get("ACWR", 1.0)
    if ri < heur["recovery_floor"]:
        if acwr > heur["acwr_upper"]:
            actions.append(f"⚠ Apply 30–40 % deload (ACWR={acwr:.2f}).")
        else:
            actions.append(f"⚠ Apply 10–15 % deload (ACWR={acwr:.2f}).")

    # ---------------- Fatigue Trend ----------------
    ft_range = heur["fatigue_delta_green"]
    ft = context.get("FatigueTrend", 0.0)
    if ft < ft_range[0]/100:
        actions.append(f"⚠ FatigueTrend {ft:.2f} — recovery phase, maintain steady load.")
    elif ft > ft_range[1]/100:
        actions.append(f"✅ FatigueTrend {ft:.2f} — rising fatigue, monitor intensity.")

    # ---------------- Benchmark / FatMax ----------------
    if context.get("weeks_since_last_FTP", 0) >= 6:
        actions.append("🔄 Retest FTP/LT1 for updated benchmarks.")
    if abs(context.get("FatMaxDeviation", 1.0)) <= 0.05 and decoup <= 0.05:
        actions.append("✅ FatMax calibration verified (±5 %).")

    # ---------------- UI Flag ----------------
    if ri < 0.6:
        context["ui_flag"] = "🔴 Overreached"
    elif ri < 0.8:
        context["ui_flag"] = "🟠 Fatigued"
    else:
        context["ui_flag"] = "🟢 Normal"

    # ---------------- Derived Metric Feedback ----------------
    th = CHEAT_SHEET["thresholds"]
    adv = CHEAT_SHEET["advice"]
    dur = context.get("Durability", 1.0)
    lir = context.get("LoadIntensityRatio", 0.0)
    er = context.get("EnduranceReserve", 1.0)
    drift = context.get("IFDrift", 0.0)

    # Durability
    if dur < th["Durability"]["amber"][0]:
        actions.append(adv["Durability"]["low"].format(dur))
    elif dur >= th["Durability"]["green"][0]:
        actions.append(adv["Durability"]["improving"].format(dur))
    # LIR
    if lir > th["LIR"]["amber"][0]:
        actions.append(adv["LIR"]["high"].format(lir))
    elif lir < th["LIR"]["green"][0]:
        actions.append(adv["LIR"]["low"].format(lir))
    else:
        actions.append(adv["LIR"]["balanced"].format(lir))
    # Endurance Reserve
    if er < th["EnduranceReserve"]["amber"][0]:
        actions.append(adv["EnduranceReserve"]["depleted"].format(er))
    elif er >= th["EnduranceReserve"]["green"][0]:
        actions.append(adv["EnduranceReserve"]["strong"].format(er))
    # Efficiency Drift
    if drift > th["IFDrift"]["amber"][0]:
        actions.append(adv["EfficiencyDrift"]["high"].format(drift))
    else:
        actions.append(adv["EfficiencyDrift"]["stable"].format(drift))
    # Recovery Index
    if ri < th["RecoveryIndex"]["amber"][0]:
        actions.append(adv["RecoveryIndex"]["poor"].format(ri))
    elif ri < th["RecoveryIndex"]["green"][0]:
        actions.append(adv["RecoveryIndex"]["moderate"].format(ri))
    else:
        actions.append(adv["RecoveryIndex"]["healthy"].format(ri))

    # ---------------- Seasonal Phase Analysis ----------------
    phase_adv = adv.get("PhaseAdvice", {})
    report_type = str(context.get("report_type", "")).lower()
    if report_type in ("season", "summary") and "phases" in context:
        actions.append("---")
        actions.append("🪜 **Seasonal Phase Analysis**")
        for ph in context["phases"]:
            phase = ph.get("phase", "Unknown")
            start, end = ph.get("start", ""), ph.get("end", "")
            delta = ph.get("delta", 0)
            msg = phase_adv.get(
                phase,
                f"ℹ {phase} phase ({start} → {end}) Δ {delta*100:.0f}%."
            )
            msg = (msg.replace("{start}", start)
                        .replace("{end}", end)
                        .replace("{delta}", f"{delta*100:.0f}%"))
            actions.append(msg)
        actions.append("")
        actions.append("📘 **Coach Note:** Phase logic aligned with Seiler / Friel periodisation heuristics.")

    # ---------------- Append metric feedback ----------------
    if metric_contexts:
        actions.extend(["---", "📊 Metric-based Feedback:"] + metric_contexts)

    context["derived_metrics"] = derived
    context["actions"] = actions
    return context

