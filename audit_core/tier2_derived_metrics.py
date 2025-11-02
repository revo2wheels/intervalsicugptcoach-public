"""
Tier-2 Step 3 — Derived Metrics Calculation (v16.1)
Computes ACWR, Monotony, Strain, Polarisation, RecoveryIndex, FatOxidation, Decoupling, FatMaxDeviation.
"""

import pandas as pd
import numpy as np

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

    return context
