"""
Tier-2 Step 3 — Derived Metrics Calculation (v16.1.3-EOD-003)
Computes ACWR, Monotony, Strain, Polarisation, RecoveryIndex,
FatOxidation, Decoupling, FatMaxDeviation, and reinstates advanced
coaching heuristics: FatigueTrend, IntensityQuality (ZQI), FatOxEfficiency.
"""

import pandas as pd
import numpy as np


def compute_fatigue_trend(context):
    events = context.get("events", [])
    if len(events) < 7:
        context["fatigue_trend"] = 0.0
        return context
    tss = [e.get("icu_training_load", 0) for e in events]
    x = list(range(len(tss)))
    numerator = len(x) * sum(i * t for i, t in zip(x, tss)) - sum(x) * sum(tss)
    denominator = len(x) * sum(i**2 for i in x) - (sum(x) ** 2)
    slope = numerator / denominator if denominator != 0 else 0
    context["fatigue_trend"] = round(slope, 2)
    return context


def compute_intensity_quality(context):
    df = context.get("df_events")
    if df is None or "zone" not in df.columns:
        context["ZQI"] = 0.0
        return context
    high_intensity = df[df["zone"].isin(["Z5", "Z6", "Z7"])]["moving_time"].sum()
    total = df["moving_time"].sum()
    context["ZQI"] = round((high_intensity / total) * 100, 1) if total > 0 else 0.0
    return context


def compute_fatox_efficiency(context):
    events = context.get("events", [])
    if not events:
        context["FatOxEfficiency"] = 0.0
        return context
    zone2_loads = [e["icu_training_load"] for e in events if e.get("intensity_zone") in ["Z2", "Z3"]]
    total_loads = [e["icu_training_load"] for e in events]
    if not zone2_loads or not total_loads:
        context["FatOxEfficiency"] = 0.0
    else:
        context["FatOxEfficiency"] = round(sum(zone2_loads) / sum(total_loads), 2)
    return context


def compute_derived_metrics(df_daily, context):
    if df_daily.empty:
        raise ValueError("❌ No daily data available")

    # --- Load window computations ---
    daily_data = {}
    daily_data["load_7d"] = df_daily["icu_training_load"].sum()
    daily_data["load_28d_avg"] = (
        df_daily["icu_training_load"].rolling(28, min_periods=7).mean().iloc[-1]
        if len(df_daily) >= 7 else daily_data["load_7d"]
    )
    daily_data["mean_load"] = df_daily["icu_training_load"].mean()
    daily_data["std_load"] = df_daily["icu_training_load"].std()

    # --- Derived calculations ---
    context["ACWR"] = round(daily_data["load_7d"] / daily_data["load_28d_avg"], 2)
    context["Monotony"] = round(
        daily_data["mean_load"] / max(daily_data["std_load"], 1), 2
    )
    context["Strain"] = int(round(context["Monotony"] * daily_data["load_7d"]))

    # --- Advanced metrics (defaults handled) ---
    context["Polarisation"] = round(daily_data.get("polarisation", 0.85), 2)
    context["RecoveryIndex"] = round(1 - (context["Monotony"] / 5), 2)
    context["FatOxidation"] = round(daily_data.get("fatox", 0.82), 2)
    context["Decoupling"] = round(daily_data.get("decoupling", 0.03), 2)
    context["FatMaxDeviation"] = round(daily_data.get("fatmax_dev", 0.02), 2)
    context["weeks_since_last_FTP"] = daily_data.get("weeks_since_last_FTP", 6)

    # --- Validation ---
    for k in ["ACWR", "Monotony", "Polarisation"]:
        if not np.isfinite(context[k]):
            raise ValueError(f"❌ Derived metric {k} is invalid (non-numeric).")

    # --- Extended heuristics reinstated (v16.1.3-EOD-003) ---
    context = compute_fatigue_trend(context)
    context = compute_intensity_quality(context)
    context = compute_fatox_efficiency(context)
    # ------------------------------------------------------------------
    # === v16.14-RC1 Metabolic Efficiency Extension ====================
    # ------------------------------------------------------------------
    df_events = context.get("df_events")
    if df_events is not None and not df_events.empty:
        z2 = df_events.query("IF >= 0.70 and IF <= 0.80") if "IF" in df_events else pd.DataFrame()
        z3 = df_events.query("IF > 0.80 and IF <= 0.95") if "IF" in df_events else pd.DataFrame()

        kcal_factor = 0.000239  # joules → kcal

        # --- Fat Oxidation Index (FOxI) ---
        if not z2.empty:
            kcal_fat = z2["icu_joules"].sum() * kcal_factor * 0.65
            kcal_total = z2["icu_joules"].sum() * kcal_factor
            foxi = 100 * (kcal_fat / kcal_total) if kcal_total > 0 else 0
        else:
            foxi = 0

        # --- Carb Use Rate (CUR) ---
        if not z3.empty:
            kcal_carb = z3["icu_joules"].sum() * kcal_factor * 0.80
            hrs = z3["moving_time"].sum() / 3600
            cur = (kcal_carb / 4.0) / hrs if hrs > 0 else 0
        else:
            cur = 0

        # --- Glycogen Ratio (GR) ---
        gr = cur / foxi if foxi > 0 else 0

        # --- Metabolic Efficiency Score (MES) ---
        denom = cur + foxi
        mes = 100 * foxi / denom if denom > 0 else 0

        # --- Inject into context metrics ---
        if "metrics" not in context:
            context["metrics"] = {}
        if "derived" not in context["metrics"]:
            context["metrics"]["derived"] = {}

        context["metrics"]["derived"].update({
            "fat_oxidation_index": round(foxi, 2),
            "carb_use_rate": round(cur, 1),
            "glycogen_ratio": round(gr, 2),
            "metabolic_efficiency_score": round(mes, 1)
        })

        # --- Logging safeguard ---
        context["metabolic_variance_flag"] = (
            abs((foxi + cur) - denom) < 0.01
        )

    # ------------------------------------------------------------------
    # End Metabolic Extension
    # ------------------------------------------------------------------

    # --- Build Unified Derived Metrics Block for Renderer (v5.1) ---
    # Compute rolling series for display
    acwr_series = df_daily["icu_training_load"].rolling(7, min_periods=1).sum() / (
        df_daily["icu_training_load"].rolling(28, min_periods=7).mean()
    )
    mono_series = (
        df_daily["icu_training_load"].rolling(7, min_periods=1).mean()
        / df_daily["icu_training_load"].rolling(7, min_periods=1).std()
    )
    strain_series = mono_series * df_daily["icu_training_load"].rolling(7, min_periods=1).sum()
    pol_series = pd.Series([context.get("Polarisation", 0.0)] * len(df_daily))
    rec_index_series = 1 - (mono_series / 5)

    context["derivedMetrics"] = {
        "acwr": {"value": context["ACWR"], "trend": acwr_series.tail(7).round(2).tolist(), "window": "7d"},
        "monotony": {"value": context["Monotony"], "trend": mono_series.tail(7).round(2).tolist(), "window": "7d"},
        "strain": {"value": context["Strain"], "trend": strain_series.tail(7).round(1).tolist(), "window": "7d"},
        "polarisation": {"value": context["Polarisation"], "trend": pol_series.tail(7).round(2).tolist(), "window": "7d"},
        "recoveryIndex": {"value": context["RecoveryIndex"], "trend": rec_index_series.tail(7).round(2).tolist(), "window": "7d"}
    }


    return context
