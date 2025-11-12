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
    """Zone intensity ratio (ZQI)."""
    zcols = [c for c in df.columns if c.lower().startswith("z")]
    if not zcols:
        return np.nan
    total = df[zcols].sum(axis=1).sum()
    high = safe(df, "z5") + safe(df, "z6") + safe(df, "z7")
    return round(high / total if total > 0 else 0, 3)


def compute_fatox_efficiency(df):
    """Compute FatOx efficiency safely from available zone or load data."""
    if not isinstance(df, pd.DataFrame):
        return 0.0
    total_load = safe(df, "icu_training_load")
    z2 = safe(df, "z2")
    z3 = safe(df, "z3")
    if total_load == 0:
        return 0.0
    fatox_eff = (z2 + z3) / total_load
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

def compute_recovery_index(monotony):
    return round(1 - (monotony / 5), 3)


def compute_derived_metrics(df_events, context):
    """Main entry for Tier-2 derived metric computation."""
    if df_events is None or df_events.empty:
        context["derived_metrics"] = {"status": "no data"}
        return context

    thresholds = safe_get(CHEAT_SHEET, "thresholds", {})
    baseline_days = safe_get(HEURISTICS, "baseline_window_days", 28)
    acwr_window = safe_get(HEURISTICS, "acwr_window_days", 7)

    df_events["date"] = pd.to_datetime(df_events["date"])
    df_daily = df_events.groupby("date")["icu_training_load"].sum().reset_index()
    load_series = df_daily["icu_training_load"].fillna(0)

    # Core metrics
    acwr = compute_acwr(load_series, acwr_window, baseline_days)
    monotony = compute_monotony(load_series)
    strain = compute_strain(load_series)
    fatigue_trend = compute_fatigue_trend(df_daily)
    zqi = compute_zone_intensity(df_events)
    fatox_eff = compute_fatox_efficiency(df_events)
    polarisation = compute_polarisation(df_events)
    recovery_index = compute_recovery_index(monotony)

    # Metabolic and efficiency extensions
    foxi = round(fatox_eff * 100, 2)
    cur = round((1 - fatox_eff) * 250, 1)
    gr = round(fatox_eff / (1 - fatox_eff + 1e-6), 2)
    mes = round(foxi * (1 - fatigue_trend), 2)

    # Risk and tolerance
    acwr_risk = "⚠️" if acwr > thresholds.get("acwr_risk_high", 1.5) else "✅"
    stress_tolerance = round((strain / (monotony + 1e-6)) / 100, 2)

    # Store metrics
    context["derived_metrics"] = {
        "ACWR": acwr,
        "Monotony": monotony,
        "Strain": strain,
        "FatigueTrend": fatigue_trend,
        "ZQI": zqi,
        "FatOxEfficiency": fatox_eff,
        "Polarisation": polarisation,
        "FOxI": foxi,
        "CUR": cur,
        "GR": gr,
        "MES": mes,
        "RecoveryIndex": recovery_index,
        "ACWR_Risk": acwr_risk,
        "StressTolerance": stress_tolerance,
    }

    context["trend_series"] = {
        "load_series": load_series.tail(14).tolist(),
        "fatigue_trend": fatigue_trend,
        "polarisation": polarisation,
        "mes": mes,
    }

    # --- Align with framework validator schema ---
    context.setdefault("metrics", {})
    context["metrics"]["derived_metrics"] = context["derived_metrics"]

    # Safety defaults for required keys
    for key in ["ACWR", "Monotony", "Strain", "Polarisation", "RecoveryIndex"]:
        if key not in context["metrics"]["derived_metrics"]:
            context["metrics"]["derived_metrics"][key] = 0.0

    # --- Sync and sanitize derived metrics for validator ---
    derived = context.get("derived_metrics", {})

    # Promote derived metrics to top-level
    for key, val in derived.items():
        try:
            # convert safely to float
            context[key] = float(val)
            if math.isnan(context[key]):
                context[key] = 0.0
        except (TypeError, ValueError):
            # fallback if invalid type
            context[key] = 0.0

    debug(context,"[DEBUG] Derived metrics synced:", {k: context[k] for k in ["ACWR", "Monotony", "Strain", "Polarisation", "RecoveryIndex"] if k in context})

    # --- Preserve CTL/ATL/TSB from earlier tiers ---
    existing_load = context.get("load_metrics", {}).copy()

    # --- Build unified load metrics ---
    context["load_metrics"] = {
        "CTL": existing_load.get("CTL", {"value": 0, "status": "ok"}),
        "ATL": existing_load.get("ATL", {"value": 0, "status": "ok"}),
        "TSB": existing_load.get("TSB", {"value": 0, "status": "ok"}),
        "ACWR": {"value": acwr, "status": "ok"},
        "Monotony": {"value": monotony, "status": "ok"},
        "Strain": {"value": strain, "status": "ok"},
        "Polarisation": {"value": polarisation, "status": "ok"},
        "RecoveryIndex": {"value": recovery_index, "status": "ok"},
    }

    debug(context,"[DEBUG-T2X] post-extended load_metrics:", context["load_metrics"])
    return context

