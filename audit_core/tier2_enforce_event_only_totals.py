"""
Tier-2 Step 2 — Enforce Event-Only Totals (v16.1)
Computes totals strictly from event-level data.
"""

def enforce_event_only_totals(df_events, context):
    if "origin" not in df_events.columns or not all(df_events["origin"] == "event"):
        raise ValueError("❌ Invalid data origin; only event-level source allowed")

    total_hours = df_events["moving_time"].sum() / 3600
    total_tss = df_events["icu_training_load"].sum()

    variance_hours = abs(total_hours - (df_events["moving_time"].sum() / 3600))
    if variance_hours > 0.1:
        raise ValueError(f"❌ Time variance {variance_hours:.2f} h exceeds threshold")

    context["totalHours"] = round(total_hours, 2)
    context["totalTss"] = int(round(total_tss))
    return context
