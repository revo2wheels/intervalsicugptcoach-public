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

def metric_confidence(context, key, default="high"):
    # Primary: semantic metrics (weekly / seasonal reports)
    metrics = context.get("metrics", {})
    if isinstance(metrics.get(key), dict):
        return metrics[key].get("metric_confidence", default)

    # Fallback: legacy derived_metrics
    dm = context.get("derived_metrics", {})
    if isinstance(dm.get(key), dict):
        return dm[key].get("metric_confidence", default)

    return default

def metric_semantic_value(context, key, default=0.0):
    """
    Read metric value from semantic metrics first, then derived_metrics.
    """
    metrics = context.get("metrics", {})
    if isinstance(metrics.get(key), dict):
        val = metrics[key].get("value", default)
        try:
            return float(val)
        except (TypeError, ValueError):
            return default

    dm = context.get("derived_metrics", {})
    if isinstance(dm.get(key), dict):
        val = dm[key].get("value", default)
        try:
            return float(val)
        except (TypeError, ValueError):
            return default

    return default


# === Dynamic Heuristics from Cheat Sheet ===
def get_dynamic_heuristics():
    th = CHEAT_SHEET["thresholds"]
    return {
        "polarisation_target":
            (sum(th["Polarisation"]["green"]) / 2) if th.get("Polarisation", {}).get("green") else None,
        "recovery_floor":
            th["LoadVariabilityIndex"]["amber"][1],
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
    Tier-2 Phase Detection (v17.9 — Science-Aligned, Traceable)
    ------------------------------------------------------------
    Classifies macrocycle phases (Base, Build, Peak, Taper, Recovery,
    Deload, Continuous Load) using week-to-week training load trends,
    CTL/ATL smoothing (Banister model), and fatigue–freshness (TSB)
    evaluation aligned with Intervals.icu and TrainingPeaks metrics.

    🧠 Scientific Foundations:
        • Banister et al. (1975–1991) – Impulse-Response Model (CTL/ATL/TSB)
        • Seiler (2010, 2020) – Endurance intensity distribution & durability
        • Mujika & Padilla (2003, 2010) – Tapering & performance maintenance
        • Issurin (2008) – Block Periodisation: accumulation → realisation
        • Friel (2009) – Practical macrocycle mapping (Base → Build → Peak)
        • Gabbett (2016) – Acute:Chronic Workload Ratio (ACWR safety)
        • Foster (1998) – Training monotony and load variability

    📚 Adds: calc_method + calc_context per phase for full traceability.
    """

    debug(context, "[PHASES] ---- Phase detection start (v17.9) ----")

    # --- Validate input ----------------------------------------------------
    if not events or not isinstance(events, (list, tuple)):
        debug(context, "[PHASES] ❌ No valid event list")
        context["phases"] = [{"phase": "No Data", "start": None, "end": None, "delta": 0.0}]
        return context

    df = pd.DataFrame(events)
    if df.empty or "icu_training_load" not in df.columns:
        debug(context, "[PHASES] ❌ Missing icu_training_load")
        context["phases"] = [{"phase": "No Data", "start": None, "end": None, "delta": 0.0}]
        return context

    # --- Normalize timestamps ---------------------------------------------
    date_col = "start_date_local" if "start_date_local" in df.columns else "start_date"
    df["date"] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")

    # --- Weekly aggregation ------------------------------------------------
    df["week_start"] = df["date"].dt.to_period("W").apply(lambda r: r.start_time)
    df_week = (
        df.groupby("week_start")
          .agg({"icu_training_load": "sum"})
          .reset_index()
          .rename(columns={"icu_training_load": "tss"})
    )
    if df_week.empty:
        debug(context, "[PHASES] ⚠️ No weekly load data after aggregation")
        context["phases"] = [{"phase": "No Data", "start": None, "end": None, "delta": 0.0}]
        return context

    # --- Compute Banister model metrics -----------------------------------
    # --- Use Intervals CTL/ATL (NOT reconstructed) ------------------------
    if "icu_ctl" in df.columns and "icu_atl" in df.columns:

        df_week = (
            df.groupby("week_start")
            .agg({
                "icu_training_load": "sum",
                "icu_ctl": "last",
                "icu_atl": "last"
            })
            .reset_index()
            .rename(columns={"icu_training_load": "tss"})
        )

        df_week["ctl"] = df_week["icu_ctl"]
        df_week["atl"] = df_week["icu_atl"]

    else:
        # fallback if somehow missing
        df_week["ctl"] = df_week["tss"].ewm(span=6, adjust=False).mean()
        df_week["atl"] = df_week["tss"].ewm(span=2, adjust=False).mean()

    df_week["tsb"] = df_week["ctl"] - df_week["atl"]
    df_week["delta_raw"] = df_week["tss"].pct_change().clip(-1, 2).fillna(0)
    df_week["delta"] = df_week["delta_raw"].ewm(span=3, adjust=False).mean().round(3)

    # --- Compute dynamic ACWR & Foster LVI -----------------------------
    df_week["acwr"] = (df_week["atl"] / df_week["ctl"]).replace([np.inf, -np.inf], np.nan).fillna(1.0).clip(0, 2)
    rolling_mean = df_week["tss"].rolling(3).mean()
    rolling_std  = df_week["tss"].rolling(3).std(ddof=0)

    weekly_monotony = (rolling_mean / (rolling_std + 1e-6)).fillna(1.0)
    df_week["lvi"] = (1 - (weekly_monotony / 5)).clip(0, 1)

    # --- Precompute safe slopes -------------------------------------------
    df_week["ctl_slope"] = df_week["ctl"].diff().fillna(0)
    df_week["atl_slope"] = df_week["atl"].diff().fillna(0)

    # --- Load thresholds ---------------------------------------------------
    phase_thresholds = CHEAT_SHEET["thresholds"]["PhaseBoundaries"]
    phase_advice     = CHEAT_SHEET["advice"]["PhaseAdvice"]

    # --- Phase classification (per-week) ----------------------------------
    labels, methods, traces = [], [], []
    for i in range(len(df_week)):
        d, tss, ctl, atl, tsb = (
            df_week.iloc[i]["delta"],
            df_week.iloc[i]["tss"],
            df_week.iloc[i]["ctl"],
            df_week.iloc[i]["atl"],
            df_week.iloc[i]["tsb"]
        )
        ctl_slope = float(df_week.iloc[i]["ctl_slope"])
        atl_slope = float(df_week.iloc[i]["atl_slope"])
        acwr = float(df_week.iloc[i]["acwr"])
        lvi = float(df_week.iloc[i]["lvi"])

        label = "Transition"
        method_source = "TSB mixed + moderate load"
        method_trace = {
            "delta": round(d, 3),
            "tsb": round(np.clip(tsb, -50, 50), 2),
            "ctl_slope": round(ctl_slope, 2),
            "atl_slope": round(atl_slope, 2),
            "acwr": round(acwr, 2),
            "lvi": round(lvi, 2)
        }

        # --- Primary thresholds
        d = 0.0 if (d is None or (isinstance(d, float) and np.isnan(d))) else float(d)

        for phase, bounds in phase_thresholds.items():
            if bounds["trend_min"] <= d <= bounds["trend_max"]:
                if acwr <= bounds.get("acwr_max", 9) and lvi >= bounds.get("lvi_min", 0):
                    label = phase
                    method_source = f"PhaseBoundaries({phase})"
                    break

        # --- Banister-informed multi-model phase detection system
        '''
        Hybrid endurance periodisation model combining:
        Banister → TSB
        Mujika → taper = unload + freshness
        Gabbett → ACWR controls risk
        Foster → load reduction defines recovery
        - Block periodisation mapping
        - Macrocycle
            └── Mesocycle (Season block)
                └── Phase (Base / Build / etc.)
                    └── Microcycle (Week)
                            └── Sessions
        '''
        # -------------------------------------------------
        # 🎯 Intervals-aligned phase classification
        # -------------------------------------------------

        def get_tsb_zone(tsb):
            if tsb < -30:
                return "deep_fatigue"
            elif tsb < -10:
                return "fatigue"
            elif tsb <= 5:
                return "neutral"
            elif tsb <= 25:
                return "fresh"
            else:
                return "very_fresh"


        zone = get_tsb_zone(tsb)
        load_ratio = tss / (ctl * 7) if ctl > 0 else 0


        # -------------------------------
        # 🔴 DEEP FATIGUE
        # -------------------------------
        if zone == "deep_fatigue":

            if d > 0.15 and acwr >= 1.1:
                label = "Build"
            else:
                label = "Overreached"


        # -------------------------------
        # 🟠 FATIGUE
        # -------------------------------
        elif zone == "fatigue":

            if d > 0.05:
                label = "Build"

            elif d < -0.05:
                if d < -0.12:
                    label = "Deload"
                else:
                    label = "Recovery"

            else:
                label = "Transition"


        # -------------------------------
        # 🟡 NEUTRAL
        # -------------------------------
        elif zone == "neutral":

            if abs(d) < 0.05:
                label = "Base"

            elif d > 0.05:
                label = "Build"

            elif d < -0.08:
                label = "Recovery"

            else:
                label = "Transition"


        # -------------------------------
        # 🟢 FRESH
        # -------------------------------
        elif zone == "fresh":

            if d < -0.10 and load_ratio < 0.75:
                label = "Taper"

            elif d < -0.05:
                label = "Recovery"

            elif d > 0.05:
                label = "Build"

            else:
                label = "Transition"


        # -------------------------------
        # 🔵 VERY FRESH
        # -------------------------------
        elif zone == "very_fresh":

            if load_ratio < 0.60:
                label = "Peak"
            else:
                label = "Transition"


        # -------------------------------------------------
        # 🧠 CANONICAL METHOD SOURCE (SINGLE SOURCE OF TRUTH)
        # -------------------------------------------------

        if zone in ("deep_fatigue", "fatigue"):
            zone_simple = "fatigue"
        elif zone == "neutral":
            zone_simple = "neutral"
        else:
            zone_simple = "fresh"

        if d > 0.05:
            trend = "increasing load"
        elif d < -0.05:
            trend = "unloading"
        else:
            trend = "stable load"

        method_source = f"{zone_simple} + {trend}"

        labels.append(label)
        methods.append(method_source)
        traces.append(method_trace)

    df_week["phase_raw"] = labels
    df_week["calc_method"] = methods
    df_week["calc_context"] = traces

    # --- Merge contiguous same-phase blocks -------------------------------
    zone_counts = {"fatigue": 0, "neutral": 0, "fresh": 0}
    trend_counts = {"increasing load": 0, "stable load": 0, "unloading": 0}
    # --- Merge contiguous same-phase blocks -------------------------------
    merged = []

    zone_counts = {"fatigue": 0, "neutral": 0, "fresh": 0}
    trend_counts = {"increasing load": 0, "stable load": 0, "unloading": 0}
    trace_accumulator = []

    current_phase = None
    start_date = None
    tss_acc = 0

    for i, row in df_week.iterrows():
        ph = row["phase_raw"]

        # ----------------------------
        # PHASE SWITCH FIRST
        # ----------------------------
        if ph != current_phase:

            if current_phase is not None:
                dominant_zone = max(zone_counts, key=zone_counts.get)
                dominant_trend = max(trend_counts, key=trend_counts.get)

                merged.append({
                    "phase": current_phase,
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": prev.strftime("%Y-%m-%d"),
                    "duration_days": (prev - start_date).days,
                    "duration_weeks": round((prev - start_date).days / 7, 1),
                    "tss_total": round(tss_acc, 1),
                    "ctl": round(prev_ctl, 2),
                    "atl": round(prev_atl, 2),
                    "tsb": round(prev_tsb, 2),
                    "calc_method": f"{dominant_zone} + {dominant_trend}",
                    "calc_context": {
                        "weeks": len(trace_accumulator),
                        "mean_delta": round(np.mean([t["delta"] for t in trace_accumulator]), 3),
                        "mean_tsb": round(np.mean([t["tsb"] for t in trace_accumulator]), 2),
                        "mean_acwr": round(np.mean([t["acwr"] for t in trace_accumulator]), 2),
                    },
                    "descriptor": phase_advice.get(current_phase, f"{current_phase} phase detected.")
                })

            # RESET for new phase
            current_phase = ph
            start_date = row["week_start"]
            tss_acc = 0

            zone_counts = {"fatigue": 0, "neutral": 0, "fresh": 0}
            trend_counts = {"increasing load": 0, "stable load": 0, "unloading": 0}
            trace_accumulator = []

        # ----------------------------
        # ADD CURRENT WEEK
        # ----------------------------
        method = row["calc_method"]

        parts = method.split(" + ")
        if len(parts) == 2:
            zone_key, trend_key = parts
        else:
            zone_key, trend_key = "neutral", "stable load"

        zone_counts[zone_key] += 1
        trend_counts[trend_key] += 1

        trace_accumulator.append(row["calc_context"])

        tss_acc += row["tss"]

        prev = row["week_start"]
        prev_ctl = row["ctl"]
        prev_atl = row["atl"]
        prev_tsb = row["tsb"]

    # ----------------------------
    # CLOSE FINAL PHASE
    # ----------------------------
    if current_phase:
        dominant_zone = max(zone_counts, key=zone_counts.get)
        dominant_trend = max(trend_counts, key=trend_counts.get)

        merged.append({
            "phase": current_phase,
            "start": start_date.strftime("%Y-%m-%d"),
            "end": prev.strftime("%Y-%m-%d"),
            "duration_days": (prev - start_date).days,
            "duration_weeks": round((prev - start_date).days / 7, 1),
            "tss_total": round(tss_acc, 1),
            "ctl": round(prev_ctl, 2),
            "atl": round(prev_atl, 2),
            "tsb": round(prev_tsb, 2),
            "calc_method": f"{dominant_zone} + {dominant_trend}",
            "calc_context": {
                "weeks": len(trace_accumulator),
                "mean_delta": round(np.mean([t["delta"] for t in trace_accumulator]), 3),
                "mean_tsb": round(np.mean([t["tsb"] for t in trace_accumulator]), 2),
                "mean_acwr": round(np.mean([t["acwr"] for t in trace_accumulator]), 2),
            },
            "descriptor": phase_advice.get(current_phase, f"{current_phase} phase detected.")
        })
    
    # --- Phase smoothing (prevent flip-flopping) ------------------
    '''
    Banister model → fatigue/adaptation lag (not instant)
    Issurin block periodisation → blocks ≥ 2–4 weeks
    Mujika tapering → taper ≠ 1-week noise flip
    Real coaching practice → phases persist
    '''
    min_block_weeks = 1
    smoothed = []

    for i in range(len(df_week)):
        current = df_week.iloc[i]["phase_raw"]

        if i == 0:
            smoothed.append(current)
            continue

        prev = smoothed[-1]

        # if phase changes too quickly → ignore change
        if current != prev:
            # look ahead to confirm change is real
            future = df_week.iloc[i:i+min_block_weeks]["phase_raw"].tolist()

            if len(future) >= 2 and all(p != current for p in future):
                smoothed.append(prev)   # reject flip
            else:
                smoothed.append(current)
        else:
            smoothed.append(current)

    df_week["phase_raw"] = smoothed

    # -------------------------------------------------
    # 🔁 Post-process: fix misclassified Load Spikes
    # -------------------------------------------------

    for i in range(len(merged)):

        phase = merged[i]["phase"]
        duration = merged[i]["duration_days"]
        ctx = merged[i].get("calc_context", {}) or {}

        delta = ctx.get("delta", 0)
        acwr = ctx.get("acwr", 1.0)
        ctl_slope = ctx.get("ctl_slope", 0)

    # --- Finalization -----------------------------------------------------
    context["phases"] = merged
    debug(context, f"[PHASES] ✅ Completed detection ({len(merged)} merged phases)")
    for p in merged:
        debug(context, f"[PHASES] → {p['phase']} ({p['start']} → {p['end']}) | TSB={p['tsb']}, CTL={p['ctl']} [{p['calc_method']}]")

    debug(context, "[PHASES] ---- Phase detection end ----")
    return context

def classify_phase_v2(row, prev_phase_final=None):
    cfg = CHEAT_SHEET["thresholds"]["phase_detection_v2"]

    boundaries = cfg["PhaseBoundaries"]

    delta = float(row.get("delta", 0) or 0)
    acwr = float(row.get("acwr", 1) or 1)
    tsb = float(row.get("tsb", 0) or 0)

    phase_raw = "Transition"

    for phase, b in boundaries.items():
        if not (b["trend_min"] <= delta <= b["trend_max"]):
            continue

        if acwr > b.get("acwr_max", 999):
            continue

        if "tsb_min" in b and tsb < b["tsb_min"]:
            continue

        if "tsb_max" in b and tsb > b["tsb_max"]:
            continue

        phase_raw = phase
        break

    phase_final = phase_raw

    # RULE 1 — peak after taper
    if (
        prev_phase_final == "Taper"
        and delta > 0
        and acwr <= 1.10
    ):
        phase_final = "Peak"

    # RULE 2 — true recovery
    elif (
        acwr < 0.65
        and delta < -0.10
        and tsb > 5
    ):
        phase_final = "Recovery"

    # RULE 3 — transition after recovery
    elif (
        prev_phase_final == "Recovery"
        and abs(delta) < 0.15
    ):
        phase_final = "Transition"

    # RULE 4 — prevent false peak
    elif (
        phase_raw == "Peak"
        and tsb < 5
    ):
        phase_final = "Base"

    return phase_raw, phase_final

def build_future_projected_weeks(context, weekly_phases):
    """
    Build projected future ISO weeks from planned calendar events.

    Uses calendar-provided icu_ctl / icu_atl as authoritative.
    RETURNS: list[dict]
    """

    debug(context, "[FUTURE] ---- Building projected future ISO weeks ----")

    if not weekly_phases:
        debug(context, "[FUTURE] ⚠️ No weekly_phases found")
        return []

    calendar = context.get("calendar", [])
    if not calendar:
        debug(context, "[FUTURE] ⚠️ No calendar found")
        return []

    df_weeks = pd.DataFrame(weekly_phases).copy()
    df_cal = pd.DataFrame(calendar).copy()

    if df_weeks.empty or df_cal.empty:
        debug(context, "[FUTURE] ⚠️ Empty weekly/calendar dataframe")
        return []

    if "week" not in df_weeks.columns:
        debug(context, "[FUTURE] ❌ weekly_phases missing week")
        return []

    # ---------------------------------------------------------
    # Normalize calendar dates
    # ---------------------------------------------------------

    today = pd.Timestamp(context["athlete_today"]).normalize()

    date_col = "start_date_local" if "start_date_local" in df_cal.columns else "date"

    df_cal["date"] = pd.to_datetime(df_cal[date_col], errors="coerce")
    df_cal = df_cal.dropna(subset=["date"]).sort_values("date")

    # future only
    df_cal = df_cal[df_cal["date"] >= today]

    if df_cal.empty:
        debug(context, "[FUTURE] ⚠️ No future calendar events")
        return []

    # ---------------------------------------------------------
    # Normalize numeric fields
    # ---------------------------------------------------------

    # load/duration fields → safe as zero
    for col in [
        "icu_training_load",
        "moving_time",
        "distance_target",
        "distance"
    ]:
        if col not in df_cal.columns:
            df_cal[col] = 0

        df_cal[col] = pd.to_numeric(
            df_cal[col],
            errors="coerce"
        ).fillna(0)

    # physiology fields → MUST preserve NaN
    for col in ["icu_ctl", "icu_atl"]:
        if col not in df_cal.columns:
            df_cal[col] = np.nan

        df_cal[col] = pd.to_numeric(
            df_cal[col],
            errors="coerce"
        )

    # Prefer distance_target, fallback to distance
    df_cal["distance_for_week"] = df_cal["distance_target"]

    df_cal.loc[
        df_cal["distance_for_week"] <= 0,
        "distance_for_week"
    ] = df_cal.loc[
        df_cal["distance_for_week"] <= 0,
        "distance"
    ]

    # ---------------------------------------------------------
    # ISO week labels
    # ---------------------------------------------------------

    iso = df_cal["date"].dt.isocalendar()

    df_cal["week"] = (
        iso.year.astype(str)
        + "-W"
        + iso.week.astype(str)
    )

    # ---------------------------------------------------------
    # Aggregate weekly planned load
    # ---------------------------------------------------------

    weekly = (
        df_cal.groupby("week", as_index=False)
        .agg({
            "icu_training_load": "sum",
            "moving_time": "sum",
            "distance_for_week": "sum"
        })
        .rename(columns={
            "icu_training_load": "tss",
            "moving_time": "moving_time_total",
            "distance_for_week": "distance_m_total"
        })
    )

    state_rows = df_cal[
        df_cal["icu_ctl"].notna() &
        df_cal["icu_atl"].notna()
    ].copy()

    state_rows = state_rows.sort_values("date")

    weekly_state = (
        state_rows
        .groupby("week", as_index=False)
        .tail(1)[["week", "date", "icu_ctl", "icu_atl"]]
        .rename(columns={
            "date": "state_date",
            "icu_ctl": "ctl",
            "icu_atl": "atl"
        })
    )

    future = weekly.merge(
        weekly_state,
        on="week",
        how="left"
    )

    future = future.sort_values("week")

    future["ctl"] = future["ctl"].ffill()
    future["atl"] = future["atl"].ffill()
    future["state_date"] = future["state_date"].ffill()

    # ---------------------------------------------------------
    # Week boundaries
    # ---------------------------------------------------------

    def week_to_dates(week_label):
        y, wk = str(week_label).split("-W")
        start = pd.Timestamp.fromisocalendar(int(y), int(wk), 1)
        end = start + pd.Timedelta(days=6)
        return start, end

    future[["start", "end"]] = future["week"].apply(
        lambda w: pd.Series(week_to_dates(w))
    )

    # ---------------------------------------------------------
    # Remove already-existing weeks
    # ---------------------------------------------------------

    existing_weeks = set(
        df_weeks["week"]
        .dropna()
        .astype(str)
        .tolist()
    )

    future = future[
        ~future["week"].isin(existing_weeks)
    ].sort_values("start")

    debug(
        context,
        f"[FUTURE] Existing weeks={sorted(existing_weeks)}"
    )

    debug(
        context,
        f"[FUTURE] Remaining projected weeks="
        f"{sorted(future['week'].astype(str).unique().tolist())}"
    )

    if future.empty:
        debug(context, "[FUTURE] ⚠️ No future ISO weeks after overlap removal")
        return []

    def decay_to_week_end(ctl, atl, last_date, week_end):
        """
        Decay CTL/ATL from last valid physiology row to ISO Sunday.
        Assumes zero training load on missing days.
        """

        ctl = float(ctl)
        atl = float(atl)

        if pd.isna(last_date):
            return float(ctl), float(atl)

        last_day = pd.Timestamp(last_date).normalize()
        end_day = pd.Timestamp(week_end).normalize()

        days = max((end_day - last_day).days, 0)

        for _ in range(days):
            ctl = ctl + ((0 - ctl) * (1 / 42))
            atl = atl + ((0 - atl) * (1 / 7))

        return ctl, atl

    projected_rows = []

    for _, wk in future.iterrows():

        ctl = float(wk.get("ctl", 0) or 0)
        atl = float(wk.get("atl", 0) or 0)

        ctl, atl = decay_to_week_end(
            ctl=ctl,
            atl=atl,
            last_date=wk.get("state_date"),
            week_end=wk.get("end")
        )

        tsb = ctl - atl

        tss = float(wk.get("tss", 0) or 0)
        hours = float(wk.get("moving_time_total", 0) or 0) / 3600
        distance_km = float(wk.get("distance_m_total", 0) or 0) / 1000

        acwr = atl / ctl if ctl > 0 else 1.0

        prev_tss = (
            projected_rows[-1]["tss"]
            if projected_rows and projected_rows[-1].get("tss", 0) > 0
            else None
        )

        delta = (
            (tss - prev_tss) / prev_tss
            if prev_tss
            else 0.0
        )

        prev_phase_final = (
            projected_rows[-1]["phase"]
            if projected_rows
            else None
        )

        phase_raw, phase = classify_phase_v2(
            {
                "delta": delta,
                "acwr": acwr,
                "tsb": tsb,
            },
            prev_phase_final=prev_phase_final
        )

        if tsb < -30:
            classification = "High_fatigue"
        elif tsb < -10:
            classification = "Productive_fatigue"
        elif tsb <= 5:
            classification = "Neutral"
        else:
            classification = "Fresh"

        projected_rows.append({
            "week": wk["week"],
            "start": wk["start"].strftime("%Y-%m-%d"),
            "end": wk["end"].strftime("%Y-%m-%d"),

            "distance_km": round(distance_km, 1),
            "hours": round(hours, 2),
            "tss": round(tss, 1),

            "ctl": round(ctl, 2),
            "atl": round(atl, 2),
            "tsb": round(tsb, 2),

            "is_projected": True,
            "projection_basis": "calendar_180d",

            "completed_tss": 0.0,
            "planned_remaining_tss": round(tss, 1),
            "projected_total_tss": round(tss, 1),
            "projected_hours": round(hours, 2),
            "phase_raw": phase_raw,
            "phase": phase,
            "classification": classification,
            "acwr": round(acwr, 2),
            "delta": round(delta, 3)
        })

    debug(
        context,
        f"[FUTURE] ✅ Added {len(projected_rows)} projected ISO weeks"
    )

    if projected_rows:
        last = projected_rows[-1]
        debug(
            context,
            f"[FUTURE] Last projected week → "
            f"{last['week']} "
            f"(CTL={last['ctl']}, ATL={last['atl']}, TSB={last['tsb']})"
        )

    return projected_rows

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
    heur = get_dynamic_heuristics()

    derived = context.get("derived_metrics", {})
    extended = context.get("extended_metrics", {})

    # Promote metrics
    for k in ["ACWR", "Monotony", "Strain", "Polarisation", "LoadVariabilityIndex"]:
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
    metric_signals = []
    primary_message = None

    # ---------------- Stateful DELOAD latch ----------------
    lvi = context.get("LoadVariabilityIndex", 1.0)
    acwr = context.get("ACWR", 1.0)

    phase = (
        context.get("current_phase")
        or (context.get("phases", [{}])[-1].get("phase") if context.get("phases") else "")
    )

    last_phase = context.get("phases", [{}])[-1]
    ctl_slope = (
        last_phase.get("calc_context", {}).get("ctl_slope")
        if isinstance(last_phase.get("calc_context"), dict)
        else context.get("ctl_slope")
    )

    deload = context.get("_deload_state", {
        "active": False,
        "triggered_on": None,
        "reason": None,
    })

    failed_adaptation = (
        lvi < heur["recovery_floor"]
        and ctl_slope is not None
        and ctl_slope <= 0
    )

    phase_allows = phase not in ("Base", "Early Base")

    if not deload["active"] and failed_adaptation and phase_allows:
        deload["active"] = True
        deload["triggered_on"] = context.get("period", {}).get("end")
        deload["reason"] = "Recovery suppressed with no fitness gain"

        msg_key = "build_deload"
        if acwr > heur["acwr_upper"]:
            msg_key = "overreach_deload"

        primary_message = CHEAT_SHEET.get("primary_messages", {}).get(msg_key)

    elif deload["active"]:
        actions.append("🟡 Deload in progress — allow recovery before resuming load.")

    context["_deload_state"] = deload

    # ---------------- Reset DELoad latch ----------------
    if (
        deload["active"]
        and deload.get("triggered_on") != context.get("period", {}).get("end")
    ):
        recovered = (
            lvi >= heur["recovery_floor"]
            and acwr <= heur["acwr_upper"]
        )

        if recovered:
            deload["active"] = False
            deload["reason"] = None
            actions.append("🟢 Recovery restored — deload complete, resume progression.")


    # ---------------- Fatigue Trend ----------------
    ft = context.get("FatigueTrend")
    if ft is None:
        ft = 0.0

    ft_state = (
        context.get("metrics", {})
        .get("FatigueTrend", {})
        .get("semantic_state")
    )

    if ft_state:
        if ft_state in ("recovering", "moderate_low"):
            metric_signals.append(f"⚠ FatigueTrend {ft:.2f} — recovery phase, maintain steady load.")

        elif ft_state in ("moderate_high", "accumulating", "extreme_accumulation"):
            metric_signals.append(f"⚠ FatigueTrend {ft:.2f} — accumulating fatigue, monitor intensity.")

        elif ft_state == "balanced":
            metric_signals.append(f"✅ FatigueTrend {ft:.2f} — balanced load.")
    # ---------------- Benchmark / FatMax ----------------
    if context.get("weeks_since_last_FTP", 0) >= 6:
        metric_signals.append("🔄 Retest FTP/LT1 for updated benchmarks.")
    decoup = context.get("Decoupling")
    if decoup is not None and abs(context.get("FatMaxDeviation", 1.0)) <= 0.05 and decoup <= 0.05:
        metric_signals.append("✅ FatMax calibration verified (±5 %).")

    # ---------------- UI Flag ----------------
    if lvi < 0.6:
        context["ui_flag"] = "🔴 Overreached"
    elif lvi < 0.8:
        context["ui_flag"] = "🟠 Fatigued"
    else:
        context["ui_flag"] = "🟢 Normal"

    # ---------------- Derived Metric Feedback ----------------

    th = CHEAT_SHEET["thresholds"]

    lvi = context.get("LoadVariabilityIndex", 1.0)
    fox = context.get("FatOxidation")
    decoup = context.get("Decoupling")

    # ---- Metabolic efficiency ----
    if fox is not None and decoup is not None:

        if fox >= 0.8 and decoup <= 0.05:

            metric_signals.append({
                "metric": "FatOxidation",
                "state": "efficient"
            })

        else:

            metric_signals.append({
                "metric": "FatOxidation",
                "state": "needs_improvement"
            })

    final_actions = []

    if primary_message and all(k in primary_message for k in ("status", "action", "next")):
        final_actions.extend([
            "### Current status",
            primary_message["status"],
            "",
            "### Primary action",
            primary_message["action"],
            "",
            "### Once recovered",
            primary_message["next"],
            "",
            "---",
        ])

    final_actions.extend(actions)

    context["derived_metrics"] = derived
    context["actions"] = final_actions
    context["metric_signals"] = metric_signals
    return context


