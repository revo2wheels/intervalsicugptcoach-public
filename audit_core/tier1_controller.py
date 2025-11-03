from audit_core.errors import AuditHalt
from audit_core.utils import validate_dataset_integrity, validate_wellness_alignment

"""
Tier-1 — Audit Controller (v16.1-EOD-002)
Validates dataset integrity before Tier-2 and enforces event-only totals.
"""

import pandas as pd

def run_tier1_controller(df_activities, wellness, context):
    # --- Step 1: Dataset integrity ---
    if df_activities.empty:
        raise ValueError("❌ No activity data received")

    if df_activities["id"].duplicated().any():
        raise ValueError("❌ Duplicate activity IDs detected")

    total_time_h = df_activities["moving_time"].sum() / 3600
    if total_time_h <= 0:
        raise ValueError("❌ Invalid total moving time")

    # --- Step 2: Basic variance validation ---
    variance_hours = abs(total_time_h - (df_activities["moving_time"].sum() / 3600))
    if variance_hours > 0.1:
        raise ValueError(f"❌ Time variance {variance_hours:.2f} h exceeds 0.1h threshold")

    # --- Step 3: Event-only totals enforcement (new) ---
    event_hours = df_activities["moving_time"].sum() / 3600
    event_tss = df_activities["icu_training_load"].sum()

    context["eventTotals"] = {"hours": event_hours, "tss": event_tss}
    context.pop("dailyTotals", None)  # remove legacy derived data

    # Cross-verify totals consistency
    if abs(event_hours - context["eventTotals"]["hours"]) > 0.1:
        raise AuditHalt("Tier-1: variance >0.1 h between events and context.")
    if abs(event_tss - context["eventTotals"]["tss"]) > 2:
        raise AuditHalt("Tier-1: variance >2 TSS between events and context.")

    # --- Step 4: Wellness alignment check ---
    if not wellness or len(wellness) == 0:
        print("⚠ No wellness data available for window; continuing with activity-only audit")
    else:
        validate_wellness_alignment(df_activities, wellness)

    # --- Step 5: Finalize ---
    context["auditPartial"] = True
    context["auditFinal"] = False
    return df_activities, wellness, context

