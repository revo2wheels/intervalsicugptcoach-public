#!/usr/bin/env python3
"""
tier2_derived_metrics.py — Unified v16.2 Adaptive
Computes all derived load, fatigue, metabolic, and efficiency metrics
using dynamic references from the coaching knowledge modules.
"""

import numpy as np
import pandas as pd
from datetime import timedelta

from coaching_profile import PROFILE_DATA
from coaching_heuristics import HEURISTICS
from coaching_cheat_sheet import CHEAT_SHEET


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
    tss = df["icu_training_load"].fillna(0)
    ema = tss.ewm(alpha=decay).mean()
    trend = (ema.iloc[-1] - ema.iloc[0]) / max(ema.iloc[0], 1)
    return round(trend, 3)


def compute_zone_intensity(df):
    zcols = [c for c in df.columns if c.lower().startswith("z")]
    if not zcols:
        return np.nan
    total = df[zcols].sum(axis=1).sum()
    high = df.get("z5", 0) + df.get("z6", 0) + df.get("z7", 0)
    return round(high.sum() / total if total > 0 else 0, 3)


def compute_fatox_efficiency(df):
    z2 = df.get("z2", 0).sum()
    z3 = df.get("z3", 0).sum()
    total = df.filter(like="z").sum().sum()
    return round((z2 + z3) / total if total > 0 else 0, 3)


def compute_polarisation(df):
    high = df.get("z5", 0).sum() + df.get("z6", 0).sum() + df.get("z7", 0).sum()
    low = df.get("z1", 0).sum()
    total = df.filter(like="z").sum().sum()
    return round((high + low) / total if total > 0 else 0, 2)


def compute_recovery_index(monotony):
    return round(1 - (monotony / 5), 3)


def compute_derived_metrics(df_events, context):
    """Main entry for Tier-2 derived metric computation."""
    if df_events is None or df_events.empty:
        context["derived_metrics"] = {"status": "no data"}
        return context

    # Load profile + heuristics
    thresholds = safe_get(CHEAT_SHEET, "thresholds", {})
    baseline_days = safe_get(HEURISTICS, "baseline_window_days", 28)
    acwr_window = safe_get(HEURISTICS, "acwr_window_days", 7)

    # Time window aggregation
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

    # Trend storage
    context["trend_series"] = {
        "load_series": load_series.tail(14).tolist(),
        "fatigue_trend": fatigue_trend,
        "polarisation": polarisation,
        "mes": mes,
    }

    return context
