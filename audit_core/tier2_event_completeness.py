"""
Tier-2 Step 1 — Event Completeness Rule (v16.1.3)
Ensures daily completeness, no missing or duplicate activities.
Now uses elapsed-time overlap detection instead of hour-bucket grouping.
Maintains wellness alignment and HRV↔Load correlation (legacy block).
"""

import pandas as pd
import numpy as np
from datetime import timedelta


def validate_event_completeness(df_activities, df_wellness=None, context=None):
    if df_activities["id"].duplicated().any():
        raise ValueError("❌ Duplicate event IDs detected")

    # --- Elapsed-time overlap duplicate detection ---
    df_sorted = df_activities.sort_values("start_date_local").reset_index(drop=True)
    valid_rows = []
    for i, e in df_sorted.iterrows():
        start_e = pd.to_datetime(e["start_date_local"])
        end_e = start_e + timedelta(seconds=float(e["moving_time"]))
        overlap_found = False

        for _, d in pd.DataFrame(valid_rows).iterrows() if valid_rows else []:
            start_d = pd.to_datetime(d["start_date_local"])
            end_d = start_d + timedelta(seconds=float(d["moving_time"]))
            # Calculate temporal overlap
            latest_start = max(start_e, start_d)
            earliest_end = min(end_e, end_d)
            overlap_sec = max((earliest_end - latest_start).total_seconds(), 0)
            overlap_fraction = overlap_sec / min(e["moving_time"], d["moving_time"])
            if overlap_fraction > 0.8:
                overlap_found = True
                # Keep higher TSS session only
                if e["icu_training_load"] > d["icu_training_load"]:
                    valid_rows.remove(d)
                    valid_rows.append(e)
                break

        if not overlap_found:
            valid_rows.append(e)

    df_valid = pd.DataFrame(valid_rows).reset_index(drop=True)

    # --- Build daily completeness summary ---
    daily = (
        df_valid.assign(date=pd.to_datetime(df_valid["start_date_local"]).dt.date)
        .groupby("date", as_index=False)
        .agg({
            "moving_time": "sum",
            "icu_training_load": "sum",
            "distance": "sum",
            "rpe": "mean",
            "feel": "min"
        })
    )

    df_valid["origin"] = "event"
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

    # --- Update context metadata ---
    if context is not None:
        context["eventCompleteness_checked"] = True
        context["dedup_method"] = "elapsed-time overlap (v16.1.3)"

    return df_valid, daily, context
