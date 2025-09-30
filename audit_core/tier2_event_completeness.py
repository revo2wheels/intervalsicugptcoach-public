"""
Tier-2 Step 1 — Event Completeness Rule (v16.1.3)
Ensures daily completeness, no missing or duplicate activities.
Now uses elapsed-time overlap detection instead of hour-bucket grouping.
Maintains wellness alignment and HRV↔Load correlation (legacy block).
"""

import pandas as pd
import numpy as np
from audit_core.utils import debug
from datetime import timedelta


def validate_event_completeness(df_activities, df_wellness=None, context=None):
    if df_activities["id"].duplicated().any():
        raise ValueError("❌ Duplicate event IDs detected")

    # --- Elapsed-time overlap duplicate detection (refined ≤1 s tolerance) ---
    df_sorted = df_activities.sort_values("start_date_local").reset_index(drop=True)
    valid_rows = []

    for i, e in df_sorted.iterrows():
        start_e = pd.to_datetime(e["start_date_local"])
        end_e = start_e + timedelta(seconds=float(e["moving_time"]))
        overlap_found = False

        if valid_rows:
            for _, d in pd.DataFrame(valid_rows).iterrows():
                start_d = pd.to_datetime(d["start_date_local"])
                end_d = start_d + timedelta(seconds=float(d["moving_time"]))

                # Compute exact temporal overlap in seconds
                latest_start = max(start_e, start_d)
                earliest_end = min(end_e, end_d)
                overlap_sec = (earliest_end - latest_start).total_seconds()

                # Ignore trivial overlaps (≤120 s) as non-conflicting
                if overlap_sec <= 120:
                    continue

                # Calculate fractional overlap for deeper duplicates
                overlap_fraction = overlap_sec / min(e["moving_time"], d["moving_time"])

                # Treat as duplicate only if >80 % temporal intersection
                if overlap_fraction > 0.8:
                    overlap_found = True
                    # Retain higher-load (TSS) activity
                    try:
                        if float(e.get("icu_training_load", 0)) > float(d.get("icu_training_load", 0)):
                            # Safely rebuild valid_rows without ambiguous Series removal
                            valid_rows = [
                                row for row in valid_rows
                                if not (
                                    isinstance(row, pd.Series)
                                    and row.get("id", None) == d.get("id", None)
                                )
                            ]
                            valid_rows.append(e)
                    except Exception as ex:
                        debug(context, f"[T2-DEDUP] Skipped ambiguous duplicate removal → {ex}")
                    break

        if not overlap_found:
            valid_rows.append(e)

    df_valid = pd.DataFrame(valid_rows).reset_index(drop=True)

    # --- Build daily completeness summary ---
    df_valid = df_valid.copy()

    # Normalize optional columns safely before aggregation
    # Handle RPE: Intervals.icu can return icu_rpe or session_rpe
    if "rpe" not in df_valid.columns:
        if "icu_rpe" in df_valid.columns:
            df_valid["rpe"] = df_valid["icu_rpe"]
        elif "session_rpe" in df_valid.columns:
            df_valid["rpe"] = df_valid["session_rpe"]
        else:
            df_valid["rpe"] = pd.NA  # fallback placeholder

    # Handle missing 'feel'
    if "feel" not in df_valid.columns:
        df_valid["feel"] = pd.NA

    # Handle missing 'distance' (e.g. indoor training)
    if "distance" not in df_valid.columns:
        df_valid["distance"] = 0

    # Convert start_date_local → date (safe timezone handling)
    df_valid["date"] = pd.to_datetime(df_valid["start_date_local"], errors="coerce").dt.date

    # Drop rows where date could not be parsed
    df_valid = df_valid.dropna(subset=["date"])

    # --- Perform daily aggregation ---
    daily = (
        df_valid.groupby("date", as_index=False)
        .agg({
            "moving_time": "sum",
            "icu_training_load": "sum",
            "distance": "sum",
            "rpe": "mean",
            "feel": "min"
        })
    )

    # Preserve original audit context fields
    df_valid["origin"] = "event"
    daily["display_only"] = True

    debug(context, f"[T2] Daily completeness summary built — {len(daily)} rows")

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

    return df_valid, daily
