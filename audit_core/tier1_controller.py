"""
Tier-1 — Audit Controller (v16)
Verifies basic integrity and data completeness.
"""

def run_tier1_controller(df_activities):
    total_time = df_activities["moving_time"].sum() / 3600
    if total_time <= 0:
        raise ValueError("❌ No activity time recorded.")
    if df_activities["id"].duplicated().any():
        raise ValueError("❌ Duplicate activity IDs detected.")
    return True  # Passes Tier-1 validation
