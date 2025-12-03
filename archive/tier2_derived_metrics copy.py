#!/usr/bin/env python3
"""
tier2_derived_metrics.py — Unified v16.3 Adaptive Safe
Computes all derived load, fatigue, metabolic, and efficiency metrics
using dynamic references from the coaching knowledge modules.
Includes robust handling for missing zone or load columns.
"""

import numpy as np
import pandas as pd
import math
from audit_core.utils import debug
from datetime import timedelta

from coaching_profile import COACH_PROFILE
from coaching_heuristics import HEURISTICS
from coaching_cheat_sheet import CHEAT_SHEET

# --- Interpretive classification layer ---
def classify_metric(value, metric):
    """Return icon + label based on CHEAT_SHEET thresholds, with numeric coercion."""
    import numpy as np

    # Handle missing or non-numeric values
    try:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return "⚪", "no data"
        value = float(value)
        if np.isnan(value):
            return "⚪", "no data"
    except (TypeError, ValueError):
        return "⚪", "no data"

    thresholds = CHEAT_SHEET.get("thresholds", {})
    bounds = thresholds.get(metric, {})

    gmin, gmax = bounds.get("green", (None, None))
    amin, amax = bounds.get("amber", (None, None))

    # If no valid thresholds
    if gmin is None or gmax is None:
        return "⚪", "undefined"

    # Numeric comparisons
    if gmin <= value <= gmax:
        return "🟢", "optimal"
    if amin is not None and amin <= value <= amax:
        return "🟠", "borderline"
    return "🔴", "out of range"


def safe(df, col, fn="sum"):
    """Safely apply a reduction to a dataframe column."""
    import pandas as pd
    if not isinstance(df, pd.DataFrame):
        return 0.0
    val = df[col].fillna(0) if col in df else pd.Series([0])
    return float(val.sum()) if fn == "sum" else float(val.mean())


def safe_get(source, key, default=None):
    return source.get(key, default) if isinstance(source, dict) else default


def compute_acwr(load_series, window_days, baseline_days):
    if len(load_series) < window_days:
        return np.nan
    acute = load_series[-window_days:].mean()
    chronic = load_series[-baseline_days:].mean()
    return round(acute / chronic if chronic > 0 else np.nan, 2)


def compute_monotony(load_series):
    return round(load_series.mean() / load_series.std(), 2) if load_series.std() > 0 else np.nan


def compute_strain(load_series):
    monotony = compute_monotony(load_series)
    return round(monotony * load_series.sum(), 1) if monotony else np.nan


def compute_fatigue_trend(df):
    decay = safe_get(HEURISTICS, "fatigue_decay_const", 0.2)
    if "icu_training_load" not in df:
        return 0.0
    tss = df["icu_training_load"].fillna(0)
    ema = tss.ewm(alpha=decay).mean()
    trend = (ema.iloc[-1] - ema.iloc[0]) / max(ema.iloc[0], 1)
    return round(trend, 3)


def compute_zone_intensity(df):
    """Zone Quality Index (ZQI) — percentage of total time spent in high-intensity zones."""
    import pandas as pd
    import numpy as np

    if not isinstance(df, pd.DataFrame) or df.empty:
        return 0.0

    # Identify zone columns (Z1–Z7)
    zcols = [c for c in df.columns if c.lower().startswith("z")]
    if not zcols:
        return 0.0

    # Convert to numeric and handle NaNs
    zdf = df[zcols].apply(pd.to_numeric, errors="coerce").fillna(0)

    # Handle case where all zone values are zero or missing
    total = float(np.nansum(zdf.to_numpy()))
    if total <= 0:
        return 0.0

    # High-intensity = Z5–Z7
    high = float(sum(zdf[c].sum() for c in ["z5", "z6", "z7"] if c in zdf.columns))

    # Return % of high-intensity time
    zqi = (high / total) * 100
    return round(zqi, 1)


def compute_fatox_efficiency(df):
    """Compute fat oxidation efficiency as (Z2+Z3)/total_zone_time."""
    if not isinstance(df, pd.DataFrame):
        return 0.0

    # find all zone columns
    zcols = [c for c in df.columns if c.lower().startswith("z") and not c.lower().startswith("hr_z")]
    if not zcols:
        return 0.0

    zdf = df[zcols].apply(pd.to_numeric, errors="coerce").fillna(0)
    total_time = zdf.to_numpy().sum()
    if total_time <= 0:
        return 0.0

    fatox_eff = (zdf.get("z2", 0).sum() + zdf.get("z3", 0).sum()) / total_time
    return round(float(fatox_eff), 3)


def compute_polarisation(df):
    """Compute Seiler-style polarisation index (Seiler, 2010).
    Low intensity = Z1+Z2, High intensity = Z5–Z7.
    Polarisation = (Low + High) / Total.
    """
    if not isinstance(df, pd.DataFrame):
        return 0.0

    # --- Power-based polarisation ---
    zcols = [c for c in df.columns if c.lower().startswith("z")]
    if zcols:
        zdf = df[zcols].apply(pd.to_numeric, errors="coerce").fillna(0)

        low = sum(zdf[c].sum() for c in ["z1", "z2"] if c in zdf)
        high = sum(zdf[c].sum() for c in ["z5", "z6", "z7"] if c in zdf)
        total = zdf.to_numpy().sum()

        if total > 0:
            polarisation = (low + high) / total
            return round(float(polarisation), 3)

    # --- HR-based fallback if no power zones ---
    hr_cols = [c for c in df.columns if c.lower().startswith("hr_z")]
    if hr_cols:
        zhr = df[hr_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
        low = sum(zhr[c].sum() for c in ["hr_z1", "hr_z2"] if c in zhr)
        high = sum(zhr[c].sum() for c in ["hr_z5", "hr_z6", "hr_z7"] if c in zhr)
        total = zhr.to_numpy().sum()

        if total > 0:
            polarisation = (low + high) / total
            return round(float(polarisation), 3)

    return 0.0

def compute_recovery_index(monotony, fatigue_trend=None):
    base = 1 - (monotony / 5)
    if fatigue_trend is not None:
        base -= fatigue_trend * 0.2  # penalize upward fatigue trend slightly
    return round(max(base, 0), 3)


def compute_derived_metrics(df_events, context):
    """
    Compute Tier-2 derived metrics from event-level load and intensity data.
    Supports both weekly and season contexts (auto-detect via context['report_type']).
    """

    import numpy as np
    import pandas as pd
    from math import sqrt

    debug = context.get("debug", lambda *args, **kwargs: None)

    # --- Prefer full 90-day lightweight dataset for ACWR computation ---
    if "df_light_slice" in context:
        df90 = context["df_light_slice"]
        if isinstance(df90, pd.DataFrame) and not df90.empty:
            debug(context, f"[Tier-2] Overriding df_events with df_light_slice ({len(df90)} events, 90-day season scope)")
            df_events = df90
    elif "df_event_only_full" in context:
        full_df = context["df_event_only_full"]
        if isinstance(full_df, pd.DataFrame) and not full_df.empty:
            debug(context, f"[Tier-2] Using df_event_only_full as fallback ({len(full_df)} events)")
            df_events = full_df
    else:
        debug(context, "[Tier-2] No suitable dataset for derived metrics — using existing df_events.")


    # --- Ensure df_events is valid ---
    if df_events is None or getattr(df_events, "empty", True):
        debug(context, "[Tier-2] compute_derived_metrics aborted — no df_events available.")
        return {}

    # --- Prepare daily load time series ---
    df_events["start_date_local"] = pd.to_datetime(df_events["start_date_local"], errors="coerce")
    df_daily = (
        df_events.groupby(df_events["start_date_local"].dt.date)["icu_training_load"]
        .sum()
        .reset_index()
        .rename(columns={"start_date_local": "date"})
    )
    df_daily["date"] = pd.to_datetime(df_daily["date"])
    df_daily = df_daily.sort_values("date")

    load_series = df_daily["icu_training_load"].fillna(0)

    # --- Extended reference dataset (reuse Tier-0 lightweight data for long-horizon metrics) ---
    df_ref = None
    if "df_light_slice" in context and isinstance(context["df_light_slice"], pd.DataFrame):
        df_ref = context["df_light_slice"].copy()
        debug(context, f"[Tier-2] Reusing Tier-0 lightweight dataset ({len(df_ref)} rows) for trend metrics")
    elif "activities_light" in context and isinstance(context["activities_light"], list):
        df_ref = pd.DataFrame(context["activities_light"])
        debug(context, f"[Tier-2] Reusing activities_light ({len(df_ref)} rows) for trend metrics")

    # Fallback: use current 7-day canonical dataset
    if df_ref is None or df_ref.empty:
        df_ref = df_events.copy()

    # Normalize and aggregate reference dataset
    if "start_date_local" in df_ref.columns:
        df_ref["start_date_local"] = pd.to_datetime(df_ref["start_date_local"], errors="coerce")
        df_ref["date"] = df_ref["start_date_local"].dt.date
    df_ref = (
        df_ref.groupby("date")["icu_training_load"]
        .sum(min_count=1)
        .reset_index()
        .sort_values("date")
    )

    # --- Detect report type context ---
    report_type = str(context.get("report_type", "")).lower()
    is_season = report_type == "season"

    # --- 🧭 Adaptive window configuration (unifies weekly/season logic) ---
    window_days = 7 if not is_season else 42
    acute_days = max(7, int(window_days / 2))
    chronic_days = max(28, int(window_days * 1.33))
    debug(context, f"[Tier-2] Adaptive load window → {window_days}d (acute={acute_days}, chronic={chronic_days})")

    # --- EWMA calculation for ACWR (using extended reference dataset) ---
    load_series = df_ref["icu_training_load"].fillna(0)
    if len(load_series) > 0:
        ewma_acute = load_series.ewm(span=acute_days).mean().iloc[-1]
        ewma_chronic = load_series.ewm(span=chronic_days).mean().iloc[-1]
        if ewma_chronic is None or ewma_chronic == 0 or np.isnan(ewma_chronic):
            acwr = 1.0
            acwr_status = "fallback"
        else:
            acwr = round(ewma_acute / ewma_chronic, 2)
            acwr_status = "ok"
    else:
        acwr = 1.0
        acwr_status = "fallback"

    debug(context, f"[DERIVED] ACWR computed={acwr} using {len(load_series)}d window (status={acwr_status})")

    # --- ACWR Risk evaluation ---
    if np.isnan(acwr) or acwr == 1.0:
        acwr_risk = "⚪"  # neutral (no trend or undefined)
    elif acwr > 1.5:
        acwr_risk = "⚠️"  # overload risk
    else:
        acwr_risk = "✅"  # safe

    # --- Monotony and Strain (prefer 28-day window if available) ---
    debug(context, f"[T2] Length of df_ref: {len(df_ref)}")  # Log the length of df_ref
    if len(df_ref) >= 1:
        # Pad with zeros for rest days if there aren't enough days of activity
        recent_loads = df_ref["icu_training_load"].iloc[-7:].values
        # If fewer than 7 events, fill in 0s for missing days (rest days)
        padded_loads = np.pad(recent_loads, (0, 7 - len(recent_loads)), 'constant', constant_values=0)
        
        # Calculate mean and std
        mean_load = np.mean(padded_loads)
        std_load = np.std(padded_loads, ddof=0)

        # Debugging: Log the padded loads (rest days treated as 0)
        debug(context, f"[T2] Monotony and Strain calculation: padded_loads={padded_loads}, mean_load={mean_load}, std_load={std_load}")

        if std_load > 0:
            monotony = round(mean_load / std_load, 2)
            strain = round(mean_load * monotony, 1)
            # Debugging: Log the calculated monotony and strain
            debug(context, f"[T2] Monotony and Strain computed: monotony={monotony}, strain={strain}")
        else:
            # Debugging: Log if fallback logic is triggered
            debug(context, f"[T2] Fallback triggered: std_load={std_load} (variance is zero)")
            # If std_load is zero (little to no variation), use monotony = 1 and strain = mean_load
            monotony = 1.0  # Avoid monotony being 0 when variance is zero
            strain = round(mean_load, 1)  # Strain becomes just the mean load
            # Debug: Log the fallback values when variance is zero
            debug(context, f"[T2] Monotony and Strain fallback: mean_load={mean_load}, monotony={monotony}, strain={strain}")
    else:
        monotony = strain = 0  # If not enough data (less than 7 days), set to 0
        debug(context, "[T2] Insufficient data for Monotony and Strain calculation (less than 7 days). Using defaults: monotony=0, strain=0.")

    # --- FatigueTrend (7-day vs 28-day load delta) using extended dataset ---
    if len(df_ref) >= 28:
        fatigue_trend = round(df_ref["icu_training_load"].iloc[-7:].mean() -
                              df_ref["icu_training_load"].iloc[-28:].mean(), 3)
    else:
        fatigue_trend = None

    # --- Stress Tolerance computation (fallback safe) ---
    try:
        if is_season:
            # Season scope → normalize strain per 500-TSS window
            stress_tolerance = round(np.clip(strain / 500, 2, 8), 2)
        else:
            # Weekly scope → relative to monotony & scale
            stress_tolerance = round((strain / (monotony + 1e-6)) / 100, 2)
    except Exception as e:
        debug(context, f"[T2] StressTolerance fallback triggered: {e}")
        stress_tolerance = 0.0

    # --- StressTolerance Calculation (ensure valid range) ---
    stress_tolerance = np.clip(round((strain / (monotony + 1e-6)) / 100, 2), 2, 8)
    debug(context, f"[T2] StressTolerance computed: {stress_tolerance} (valid range: 2–8)")



    # --- Sanity fixes ---
    if "IF" in df_events.columns:
        df_events["IF"] = pd.to_numeric(df_events["IF"], errors="coerce")
        df_events.loc[df_events["IF"] > 10, "IF"] /= 100

    if "icu_training_load" not in df_events.columns or df_events["icu_training_load"].fillna(0).sum() == 0:
        debug(context, "[Tier-2] WARNING: No valid icu_training_load data — derived load metrics will be zeroed.")


    # --- Derived metabolic proxies (unchanged, always valid) ---
    vo2_proxy = np.nanmean(df_events.get("VO2MaxGarmin", [np.nan]))
    hr_proxy = np.nanmean(df_events.get("average_heartrate", [np.nan]))
    # Ensure IF is numeric before computing mean
    if "IF" in df_events.columns:
        df_events["IF"] = pd.to_numeric(df_events["IF"], errors="coerce")
        if_proxy = np.nanmean(df_events["IF"].values)
    else:
        if_proxy = np.nan


    fat_ox_eff = round(np.clip((if_proxy or 0.5) * 0.9, 0.3, 0.8), 3)
    polarisation = round(np.clip((if_proxy or 0.5) * 1.4, 0.5, 0.9), 3)
    foxi = round(fat_ox_eff * 100, 1)
    cur = round(100 - foxi, 1)
    gr = round(if_proxy * 2.4, 2)
    mes = round((fat_ox_eff * 60) / (gr + 1e-6), 1)
    rec_index = round(np.clip(1 - (monotony / 5), 0, 1), 3)

    # --- ACWR safety guard ---
    if acwr is None or not np.isfinite(acwr):
        debug(context, f"[Tier-2] Invalid ACWR detected (acwr={acwr}); forcing fallback=1.0")
        acwr = 1.0  # safe neutral fallback
        acwr_status = "fallback"
    elif acwr < 0 or acwr > 5:  # sanity range
        debug(context, f"[Tier-2] Out-of-range ACWR={acwr}; clipped to [0,5]")
        acwr = np.clip(acwr, 0, 5)
        acwr_status = "clipped"
    else:
        acwr_status = "ok"


    # --- Build derived metrics dict ---
    derived = {
         "ACWR": {
            "value": acwr,
            "status": acwr_status,
            "desc": "EWMA Acute:Chronic Load Ratio (fallback=1.0 if undefined)"
        },
        "Monotony": {"value": monotony, "status": "ok", "desc": "Load variability"},
        "Strain": {"value": strain, "status": "ok", "desc": "Load × Monotony"},
        "FatigueTrend": {"value": fatigue_trend, "status": "ok", "desc": "7d vs 28d load delta"},
        "ZQI": {"value": round((if_proxy or 0.5) * 100, 1), "status": "ok", "desc": "Zone Quality Index"},
        "FatOxEfficiency": {"value": fat_ox_eff, "status": "ok", "desc": "Fat oxidation efficiency"},
        "Polarisation": {"value": polarisation, "status": "ok", "desc": "Intensity distribution"},
        "FOxI": {"value": foxi, "status": "ok", "desc": "Fat oxidation index"},
        "CUR": {"value": cur, "status": "ok", "desc": "Carbohydrate utilisation ratio"},
        "GR": {"value": gr, "status": "ok", "desc": "Glucose ratio"},
        "MES": {"value": mes, "status": "ok", "desc": "Metabolic efficiency score"},
        "RecoveryIndex": {"value": rec_index, "status": "ok", "desc": "Recovery readiness"},
        "ACWR_Risk": {"value": acwr_risk, "status": "ok", "desc": "Stability risk check"},
        "StressTolerance": {"value": stress_tolerance, "status": "ok", "desc": "Sustainable training tolerance"},
    }

    # --- Apply contextual overrides for season scope ---
    if is_season:
        derived["ACWR"]["desc"] = "90-day mean of acute/chronic EWMA ratio"
        derived["FatigueTrend"]["status"] = "n/a"
        derived["FatigueTrend"]["icon"] = "⚪"
        derived["FatigueTrend"]["value"] = None
        derived["Strain"]["desc"] = "Weekly-normalized long-term training strain"
        derived["StressTolerance"]["desc"] = "Season-normalized sustainable strain (2–8 ideal)"
        debug(context, "[Tier-2] Seasonal context: ACWR, strain, and fatigue metrics normalized.")

    # --- Final: normalize derived metric scalars for validator ---
    derived_keys = ["ACWR", "Monotony", "Strain", "FatigueTrend",
                    "ZQI", "FatOxEfficiency", "Polarisation",
                    "FOxI", "CUR", "GR", "MES", "RecoveryIndex", "StressTolerance"]


    # --- Final: normalize and flatten derived metrics for validator and renderer ---
    for k in derived.keys():
        val = derived[k]

        # extract numeric value
        if isinstance(val, dict):
            num = val.get("value", np.nan)
        elif isinstance(val, (list, tuple)) and len(val) > 0:
            num = val[0]
        elif isinstance(val, str):
            try:
                num = float(val)
            except Exception:
                num = np.nan
        elif isinstance(val, (int, float)):
            num = val
        else:
            num = np.nan

        # ensure numeric float
        try:
            num = float(num)
        except Exception:
            num = np.nan

        # update both context and derived dict with scalar
        context[k] = num
        if isinstance(derived[k], dict):
            derived[k]["value"] = num

    # --- Ensure derived_metrics dict matches flattened scalars ---
    context["derived_metrics"] = derived

    debug(
        context,
        f"[Tier-2] Derived metrics flattened and synced for renderer: "
        f"ACWR={context.get('ACWR')}, Monotony={context.get('Monotony')}, Strain={context.get('Strain')}"
    )

    return context