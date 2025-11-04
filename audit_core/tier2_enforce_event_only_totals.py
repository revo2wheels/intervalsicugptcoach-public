"""
Tier-2 Enforcement — Event-Only Totals (v16.14-Stable)
Recomputes canonical totals strictly from event-level data.
No normalization, interpolation, or legacy fallback.
"""

from audit_core.errors import AuditHalt


def enforce_event_only_totals(df, context):
    # --- Step 1: Validate input source ---
    if df is None or df.empty:
        raise AuditHalt("❌ enforce_event_only_totals: no df_events provided")

    if "origin" not in df.columns or not all(df["origin"] == "event"):
        raise AuditHalt("❌ enforce_event_only_totals: invalid data origin (non-event rows detected)")

    if "moving_time" not in df.columns or "icu_training_load" not in df.columns:
        raise AuditHalt("❌ enforce_event_only_totals: missing required columns (moving_time, icu_training_load)")

    # --- Step 2: Canonical recomputation ---
    total_hours = df["moving_time"].sum() / 3600
    total_tss = df["icu_training_load"].sum()

    if total_hours <= 0 or total_tss <= 0:
        raise AuditHalt("❌ enforce_event_only_totals: invalid totals (zero or negative values)")

    # --- Step 3: Compare with Tier-1 snapshot before overwrite ---
    tier1_totals = context.get("tier1_eventTotals", {}).copy()
    if tier1_totals:
        diff_hours = abs(total_hours - tier1_totals.get("hours", 0))
        diff_tss = abs(total_tss - tier1_totals.get("tss", 0))
        if diff_hours > 0.1:
            raise AuditHalt(f"❌ Tier-1 vs Tier-2 mismatch > 0.1 h (Δ={diff_hours:.2f})")
        if diff_tss > 2:
            raise AuditHalt(f"❌ Tier-1 vs Tier-2 mismatch > 2 TSS (Δ={diff_tss:.1f})")

    # --- Step 4: Context purge + canonical injection (v16.14-FIX-B) ---
    for key in ["dailyTotals", "totalHours", "totalTss"]:
        context.pop(key, None)

    # use the verified event-only DataFrame
    df_verified = context.get("df_event_only", context.get("df_events"))

    if df_verified is None or df_verified.empty:
        raise AuditHalt("❌ Tier-2: verified df_event_only missing before canonical injection")

    total_hours = df_verified["moving_time"].sum() / 3600
    total_tss = df_verified["icu_training_load"].sum()
    total_distance = (
        df_verified["distance"].sum() / 1000 if "distance" in df_verified else 0
    )
 
    context["totalHours"] = round(total_hours, 2)
    context["totalTss"] = int(round(total_tss))
    context["totalDistance"] = round(total_distance, 1)

    context["eventTotals"] = {
        "hours": context["totalHours"],
        "tss": context["totalTss"],
        "distance": context["totalDistance"],
        "source": "tier2_enforce_event_only_totals",
    }
    context["enforcement_layer"] = "tier2_enforce_event_only_totals"


    # --- Step 5: Annotate audit trace ---
    context["enforcement_layer"] = "tier2_enforce_event_only_totals"
    context["event_count"] = len(df)

    # --- Step 6: Return validated canonical context ---
    return context
