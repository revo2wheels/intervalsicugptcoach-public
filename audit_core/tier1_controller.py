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

    # Attach full wellness fieldset for Unified Framework v5.1
    if wellness and len(wellness) > 0:
        df_well = pd.DataFrame(wellness)[[
            "id", "sleepSecs", "sleepScore", "hrv", "restingHR",
            "fatigue", "stress", "mood", "motivation",
            "hydration", "soreness", "injury", "readiness"
        ]]
        df_well.rename(columns={"id": "date"}, inplace=True)
        df_well["date"] = pd.to_datetime(df_well["date"]).dt.date
        df_well["sleep_h"] = (df_well["sleepSecs"] / 3600).round(2)
        df_well.drop(columns=["sleepSecs"], inplace=True)
        daily_summary = pd.merge(daily_summary, df_well, on="date", how="left")

    context["dailyMerged"] = daily_summary

    # --- Inline translation of RPE and FEEL to qualitative labels ---
    if "rpe" in daily_summary.columns:
        rpe_map = {
            1: "very easy", 2: "easy", 3: "moderate", 4: "somewhat hard",
            5: "hard", 6: "very hard", 7: "maximal", 8: "maximal+", 9: "extreme", 10: "all out"
        }
        daily_summary["rpe_label"] = daily_summary["rpe"].map(rpe_map).fillna(daily_summary["rpe"].astype(str))

    if "feel" in daily_summary.columns:
        feel_map = {
            1: "very bad", 2: "bad", 3: "neutral", 4: "good", 5: "very good"
        }
        daily_summary["feel_label"] = daily_summary["feel"].map(feel_map).fillna(daily_summary["feel"].astype(str))

    # --- Inline qualitative translation for subjective 1–5 markers ---
    label_map = {
        1: "very low", 2: "low", 3: "moderate", 4: "high", 5: "very high"
    }

    for col in ["fatigue", "stress", "soreness"]:
        if col in daily_summary.columns:
            daily_summary[f"{col}_label"] = daily_summary[col].map(label_map).fillna(daily_summary[col])

    mood_map = {1:"very bad",2:"bad",3:"neutral",4:"good",5:"very good"}
    motiv_map = {1:"none",2:"low",3:"moderate",4:"good",5:"excellent"}
    hydr_map = {1:"overhydrated",2:"slightly high",3:"optimal",4:"slightly low",5:"dehydrated"}
    ready_map = {1:"very poor",2:"poor",3:"fair",4:"good",5:"excellent"}

    for col, cmap in {
        "mood": mood_map, "motivation": motiv_map, "hydration": hydr_map, "readiness": ready_map
    }.items():
        if col in daily_summary.columns:
            daily_summary[f"{col}_label"] = daily_summary[col].map(cmap).fillna(daily_summary[col])

    # --- Step 7: Finalize ---
    context["auditPartial"] = True
    context["auditFinal"] = False
    return df_activities, wellness, context
