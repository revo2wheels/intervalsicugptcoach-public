"""
Tier-2 Enforcement — Event-Only Totals (v16.14-Integrated)
Computes canonical totals using Tier-2 validated event dataset if available.
Falls back to raw Tier-0 data only if no DataFrame is passed.
"""
import os
print("📁 Tier-2 module loaded from:", os.path.abspath(__file__))

from audit_core.errors import AuditHalt


def enforce_event_only_totals(df_events, context):
    # --- Step 1: Acquire source dataset -------------------------------------
    if df_events is not None and not df_events.empty:
        df_source = df_events.copy()
        source_label = "Tier-2 validated events"
    else:
        df_source = context.get("df_raw_activities")
        source_label = "raw Tier-0 activities (fallback)"
        if df_source is None or df_source.empty:
            raise AuditHalt("❌ enforce_event_only_totals: no dataset available from Tier-2 or Tier-0")

    print(f"🔍 Tier-2 enforcement source: {source_label} ({df_source.shape[0]} rows)")

    # --- Step 2: Diagnostics -------------------------------------------------
    if "origin" in df_source.columns:
        print("origin counts:\n", df_source["origin"].value_counts(dropna=False))
    else:
        print("⚠️  'origin' column missing in dataset")

    if "moving_time" in df_source.columns:
        print("moving_time stats:\n", df_source["moving_time"].describe())
    else:
        print("⚠️  'moving_time' column missing")

    # --- Step 3: Filter to valid event rows ---------------------------------
    df_event_only = (
        df_source.loc[
            (df_source.get("origin", "event") == "event")
            & (df_source["moving_time"] > 120)
            & (df_source["icu_training_load"] > 0)
        ]
        .drop_duplicates(subset=["start_date_local", "elapsed_time"], keep="first")
        .copy()
    )

    if df_event_only.empty:
        raise AuditHalt("❌ enforce_event_only_totals: no valid event rows after filtering")

    # --- Step 4: Canonical recomputation ------------------------------------
    event_hours = df_event_only["moving_time"].sum() / 3600
    event_tss = df_event_only["icu_training_load"].sum()
    event_distance = (
        df_event_only["distance"].sum() / 1000 if "distance" in df_event_only else 0
    )

    if event_hours <= 0 or event_tss <= 0:
        raise AuditHalt("❌ enforce_event_only_totals: invalid totals (zero or negative values)")

    # --- Step 5: Compare vs Tier-1 snapshot ---------------------------------
    tier1_totals = context.get("tier1_eventTotals", {})
    diff_hours = diff_tss = 0
    if tier1_totals:
        diff_hours = abs(event_hours - tier1_totals.get("hours", 0))
        diff_tss = abs(event_tss - tier1_totals.get("tss", 0))
        if diff_hours > 0.1 or diff_tss > 2:
            context.setdefault("audit_flags", []).append(
                f"⚠️ Tier-2 correction applied: Δh={diff_hours:.2f}, "
                f"ΔTSS={diff_tss:.1f} (Tier-1 replaced with event totals)"
            )

    # --- Step 6: Canonical injection ----------------------------------------
    for key in ["dailyTotals", "totalHours", "totalTss"]:
        context.pop(key, None)

    context["totalHours"] = round(event_hours, 2)
    context["totalTss"] = int(round(event_tss))
    context["totalDistance"] = round(event_distance, 1)

    context["eventTotals"] = {
        "hours": context["totalHours"],
        "tss": context["totalTss"],
        "distance": context["totalDistance"],
        "source": source_label,
    }
    context["df_event_only"] = df_event_only
    context["enforcement_layer"] = "tier2_enforce_event_only_totals"

    # --- Step 7: Hard-lock canonical totals ---------------------------------
    context["_locked_totals"] = True
    context["locked_totalHours"] = context["totalHours"]
    context["locked_totalTss"] = context["totalTss"]
    context["locked_totalDistance"] = context["totalDistance"]

    # --- Step 8: Trace annotation -------------------------------------------
    context["event_count"] = len(df_event_only)
    context.setdefault("trace", []).append(
        f"T2 totals computed from {source_label} "
        f"(Δh={diff_hours:.2f}, ΔTSS={diff_tss:.1f}, events={len(df_event_only)})"
    )

    return context
