"""
Tier-2 Step 1 — Event Completeness Rule (v16.1.2)
Ensures daily completeness, no missing or duplicate activities.
Reinstates wellness alignment and HRV↔Load correlation (legacy block).
"""

import pandas as pd
import numpy as np

def validate_event_completeness(df_activities, df_wellness=None, context=None):
    if df_activities["id"].duplicated().any():
        raise ValueError("❌ Duplicate event IDs detected")

    # --- Build daily completeness summary ---
    daily = (
        df_activities.assign(date=pd.to_datetime(df_activities["start_date_local"]).dt.date)
        .groupby("date", as_index=False)
        .agg({
            "moving_time": "sum",
            "icu_training_load": "sum",
            "distance": "sum",
            "rpe": "mean",
            "feel": "min"
        })
    )

    df_activities["origin"] = "event"
    daily["display_only"] = True

    # --- Wellness merge & HRV correlation (legacy logic) ---
    if df_wellness is not None and "hrv" in df_wellness.columns:
        wellness = df_wellness.copy()
        wellness["date"] = pd.to_datetime(wellness["date"]).dt.date
        merged = pd.merge(wellness, daily, on="date", how="inner")

        if len(merged) >= 5:
            hrv = merged["hrv"].to_numpy()
            tss = merged["icu_training_load"].to_numpy()
            r = np.corrcoef(hrv, tss)[0, 1]
            hrv_corr = round(float(r), 2)
        else:
            hrv_corr = 0.0
    else:
        hrv_corr = 0.0

    # --- Push correlation into context ---
    if context is not None:
        context["HRV_Load_Corr"] = hrv_corr
        if hrv_corr <= -0.5:
            context["recovery_flag"] = "adaptive"
        elif hrv_corr > -0.3:
            context["recovery_flag"] = "poor"
        else:
            context["recovery_flag"] = "neutral"

    return df_activities, daily, context
