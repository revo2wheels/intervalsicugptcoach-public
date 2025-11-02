"""
Tier-2 Step 2 — Event Completeness Rule (v16)
Validates event-level integrity and constructs display-only daily summary.
"""

import pandas as pd

def validate_event_completeness(df_activities):
    df_events = df_activities.copy(deep=True)
    if df_events["id"].duplicated().any():
        raise ValueError("❌ Duplicate event ID detected.")
    df_daily = (
        df_events.assign(date=pd.to_datetime(df_events["start_date"]).dt.date)
        .groupby("date", as_index=False)
        .agg({
            "moving_time": "sum",
            "icu_training_load": "sum",
            "distance": "sum",
            "rpe": "mean",
            "feel": "min"
        })
    )
    df_daily["display_only"] = True
    df_daily.origin = "summary"
    return df_events, df_daily
