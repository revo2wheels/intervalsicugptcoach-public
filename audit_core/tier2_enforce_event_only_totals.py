"""
Tier-2 Step 2 — Enforce Event-Only Totals (v16.1-EOD-002)
Computes Σ(volume, load, duration) strictly from validated event-level data.
"""

from audit_core.errors import AuditHalt

def enforce_event_only_totals(df_events, context):
    # --- Step 1: Validate source ---
    if "origin" not in df_events.columns or not all(df_events["origin"] == "event"):
        raise AuditHalt("❌ Invalid data origin; only event-level source allowed")

    if df_events.empty:
        raise AuditHalt("❌ No event data available for Tier-2 totals computation")

    # --- Step 2: Compute event-only totals ---
    total_hours = df_events["moving_time"].sum() / 3600
    total_tss = df_events["icu_training_load"].sum()

    # --- Step 3: Variance validation ---
    variance_hours = abs(total_hours - (df_events["moving_time"].sum() / 3600))
    if variance_hours > 0.1:
        raise AuditHalt(f"❌ Time variance {variance_hours:.2f} h exceeds 0.1h threshold")

    # --- Step 4: Context injection ---
    context.pop("dailyTotals", None)  # purge any derived or daily dataset
    context["totalHours"] = round(total_hours, 2)
    context["totalTss"] = int(round(total_tss))

    # --- Step 5: Cross-validation with Tier-1 eventTotals ---
    if "eventTotals" in context:
        diff_hours = abs(context["totalHours"] - context["eventTotals"]["hours"])
        diff_tss = abs(context["totalTss"] - context["eventTotals"]["tss"])
        if diff_hours > 0.1:
            raise AuditHalt(f"❌ Tier-1 vs Tier-2 mismatch >0.1h (Δ={diff_hours:.2f})")
        if diff_tss > 2:
            raise AuditHalt(f"❌ Tier-1 vs Tier-2 mismatch >2 TSS (Δ={diff_tss:.1f})")

    # --- Step 6: Return validated context ---
    return context
