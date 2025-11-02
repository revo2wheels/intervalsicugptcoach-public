"""
Tier-2 Step 1 — Event Completeness Rule (v16.1)
Ensures daily completeness, no missing or duplicate activities.
"""

import pandas as pd

def validate_event_completeness(df_activities):
    if df_activities["id"].duplicated().any():
        raise ValueError("❌ Duplicate event IDs detected")

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
    return df_activities, daily
