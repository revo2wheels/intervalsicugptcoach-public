"""
Tier-1 — Audit Controller (v16.1.4-EOD-005)
Validates dataset integrity before Tier-2 and enforces event-only totals.
"""

import pandas as pd
from audit_core.errors import AuditHalt
from audit_core.utils import validate_dataset_integrity, validate_wellness_alignment
from audit_core.tier2_enforce_event_only_totals import enforce_event_only_totals

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
        raise ValueError(f"❌ Time variance {variance_hours:.2f} h exceeds 0.1 h threshold")

    # --- Step 3: Event-only totals enforcement ---
    event_hours = df_activities["moving_time"].sum() / 3600
    event_tss = df_activities["icu_training_load"].sum()

    context["eventTotals"] = {"hours": event_hours, "tss": event_tss}
    context.pop("dailyTotals", None)

    # --- Step 4: Re-validate totals with unified Tier-2 enforcement ---
    context["df_events"] = df_activities
    context = enforce_event_only_totals(df_activities, context)

    # --- Step 5: Cross-verification ---
    if abs(context["eventTotals"]["hours"] - context["totalHours"]) > 0.1:
        raise AuditHalt("Tier-1: variance >0.1 h between events and context.")
    if abs(context["eventTotals"]["tss"] - context["totalTss"]) > 2:
        raise AuditHalt("Tier-1: variance >2 TSS between events and context.")

    # --- Step 6: Wellness alignment check ---
    if not wellness or len(wellness) == 0:
        print("⚠ No wellness data available for window; continuing with activity-only audit")
    else:
        validate_wellness_alignment(df_activities, wellness)

    # --- Step 6b: Build merged daily summary for renderer ---
    df_activities["date"] = pd.to_datetime(df_activities["start_date_local"]).dt.date
    daily_summary = (
        df_activities.groupby("date")
        .agg({
            "icu_training_load": "sum",
            "moving_time": lambda x: round(x.sum() / 3600, 2),
            "name": lambda x: ", ".join(x.head(2)),  # up to 2 event names/day
        })
        .rename(columns={"icu_training_load": "load", "moving_time": "hours"})
        .reset_index()
    )

    # Attach wellness fields if available
    if wellness and len(wellness) > 0:
        df_well = pd.DataFrame(wellness)[["id", "sleepSecs", "sleepScore", "hrv", "restingHR"]]
        df_well.rename(columns={"id": "date"}, inplace=True)
        df_well["date"] = pd.to_datetime(df_well["date"]).dt.date
        df_well["sleep_h"] = (df_well["sleepSecs"] / 3600).round(2)
        df_well.drop(columns=["sleepSecs"], inplace=True)
        daily_summary = pd.merge(daily_summary, df_well, on="date", how="left")

    context["dailyMerged"] = daily_summary

    # --- Step 7: Finalize ---
    context["auditPartial"] = True
    context["auditFinal"] = False
    return df_activities, wellness, context
