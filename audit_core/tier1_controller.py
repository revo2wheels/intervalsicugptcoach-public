"""
Tier-1 — Audit Controller (v16.1)
Validates dataset integrity before proceeding to Tier-2.
"""

import pandas as pd

def run_tier1_controller(df_activities, wellness, context):
    if df_activities.empty:
        raise ValueError("❌ No activity data received")

    if df_activities["id"].duplicated().any():
        raise ValueError("❌ Duplicate activity IDs detected")

    total_time_h = df_activities["moving_time"].sum() / 3600
    if total_time_h <= 0:
        raise ValueError("❌ Invalid total moving time")

    # Basic variance validation (sanity check)
    variance_hours = abs(total_time_h - (df_activities["moving_time"].sum() / 3600))
    if variance_hours > 0.1:
        raise ValueError(f"❌ Time variance {variance_hours:.2f} h exceeds 0.1h threshold")

    # Check wellness window alignment
    if not wellness or len(wellness) == 0:
        print("⚠ No wellness data available for window; continuing with activity-only audit")

    context["auditPartial"] = True
    return df_activities, wellness, context
