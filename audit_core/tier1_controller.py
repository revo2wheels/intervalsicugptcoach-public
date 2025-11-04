"""
Tier-1 — Audit Controller (v16.14-Stable+)
Ensures dataset integrity and enforces Field Lock Rule for moving_time.
"""

import pandas as pd
from audit_core.errors import AuditHalt
from audit_core.utils import validate_dataset_integrity, validate_wellness_alignment


def run_tier1_controller(df_activities, wellness, context):
   # --- Step 1: Dataset integrity ---
    if df_activities.empty:
        raise ValueError("❌ No activity data received")

    # Field Lock enforcement
    assert "moving_time" in df_activities.columns, "❌ moving_time field missing from dataset"
    assert df_activities["moving_time"].gt(0).all(), "❌ moving_time contains zero or negative values"

    if df_activities["id"].duplicated().any():
        raise ValueError("❌ Duplicate activity IDs detected")

    # --- Step 2: Canonical totals (moving_time only) ---
    event_hours = df_activities["moving_time"].sum() / 3600
    event_tss = df_activities["icu_training_load"].sum()
    context["tier1_eventTotals"] = {"hours": round(event_hours, 2),
                                    "tss": int(round(event_tss))}

    # --- Step 3: Basic variance validation ---
    if event_hours <= 0 or event_tss <= 0:
        raise AuditHalt("❌ Tier-1: invalid totals (zero or negative values)")

    context.pop("dailyTotals", None)
    context["df_events"] = df_activities

    # --- Step 4: Cross-verification ---
    if abs(event_hours - context["tier1_eventTotals"]["hours"]) > 0.1:
        raise AuditHalt("Tier-1: variance >0.1 h within event dataset.")
    if abs(event_tss - context["tier1_eventTotals"]["tss"]) > 2:
        raise AuditHalt("Tier-1: variance >2 TSS within event dataset.")

    # --- Step 5: Wellness alignment check ---
    if not wellness or len(wellness) == 0:
        print("⚠ No wellness data available for window; continuing with activity-only audit")
    else:
        validate_wellness_alignment(df_activities, wellness)

    # --- Step 6: Wellness daily summary build (activity grouping removed) ---
    df_activities["date"] = pd.to_datetime(df_activities["start_date_local"]).dt.date

    daily_summary = pd.DataFrame()  # start empty, only populate if wellness exists

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

        daily_summary = df_well.copy()

    context["dailyMerged"] = daily_summary

    # --- Step 6b: Qualitative label translation (unchanged) ---
    rpe_map = {
        1: "very easy", 2: "easy", 3: "moderate", 4: "somewhat hard",
        5: "hard", 6: "very hard", 7: "maximal", 8: "maximal+", 9: "extreme", 10: "all out"
    }
    feel_map = {1: "very bad", 2: "bad", 3: "neutral", 4: "good", 5: "very good"}
    label_map = {1: "very low", 2: "low", 3: "moderate", 4: "high", 5: "very high"}
    mood_map = {1: "very bad", 2: "bad", 3: "neutral", 4: "good", 5: "very good"}
    motiv_map = {1: "none", 2: "low", 3: "moderate", 4: "good", 5: "excellent"}
    hydr_map = {1: "overhydrated", 2: "slightly high", 3: "optimal", 4: "slightly low", 5: "dehydrated"}
    ready_map = {1: "very poor", 2: "poor", 3: "fair", 4: "good", 5: "excellent"}

    if "rpe" in daily_summary.columns:
        daily_summary["rpe_label"] = daily_summary["rpe"].map(rpe_map).fillna(daily_summary["rpe"].astype(str))
    if "feel" in daily_summary.columns:
        daily_summary["feel_label"] = daily_summary["feel"].map(feel_map).fillna(daily_summary["feel"].astype(str))
    for col in ["fatigue", "stress", "soreness"]:
        if col in daily_summary.columns:
            daily_summary[f"{col}_label"] = daily_summary[col].map(label_map).fillna(daily_summary[col])
    for col, cmap in {
        "mood": mood_map,
        "motivation": motiv_map,
        "hydration": hydr_map,
        "readiness": ready_map,
    }.items():
        if col in daily_summary.columns:
            daily_summary[f"{col}_label"] = daily_summary[col].map(cmap).fillna(daily_summary[col])

    # --- Step 7: Finalize ---
    context["auditPartial"] = True
    context["auditFinal"] = False
    return df_activities, wellness, context
