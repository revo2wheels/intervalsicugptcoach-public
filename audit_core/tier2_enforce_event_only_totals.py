"""
Tier-2 Step 3 — Enforce Event-Only Totals (v16 absolute)
Computes Σ(volume, load) strictly from event-level data.
"""

def enforce_event_only_totals(df_events, context):
    df_events.origin = "event"
    total_hours = df_events["moving_time"].sum() / 3600
    total_tss = df_events["icu_training_load"].sum()

    if df_events["id"].duplicated().any():
        raise ValueError("❌ Duplicate event IDs detected.")

    variance = abs(total_hours - (df_events["moving_time"].sum() / 3600))
    if variance > 0.1:
        raise ValueError(f"❌ Time variance {variance:.2f} h exceeds 0.1h threshold.")

    if total_hours <= 0 or total_tss <= 0:
        raise ValueError("❌ Invalid totals; dataset empty or zero.")

    context["totalHours"] = round(total_hours, 2)
    context["totalTss"] = int(round(total_tss))
    return context
