"""
Tier-2 Enforcement — Event-Only Totals (v16.14-Independent)
Recomputes canonical totals strictly from raw Tier-0 event-level data.
No normalization, interpolation, or legacy fallback.
Ensures independence from Tier-1 context.
"""

from audit_core.errors import AuditHalt


def enforce_event_only_totals(df_unused, context):
    # --- Step 1: Acquire and validate raw source -----------------------------
    df_raw = context.get("df_raw_activities")
    if df_raw is None or df_raw.empty:
        raise AuditHalt("❌ enforce_event_only_totals: no raw activity dataset in context")

    # --- DEBUG / DIAGNOSTIC INSPECTION ---------------------------------------
    print("🔍 Tier-2 input shape:", df_raw.shape)
    if "origin" in df_raw.columns:
        print("origin counts:\n", df_raw["origin"].value_counts(dropna=False))
    else:
        print("⚠️  'origin' column missing in raw data")

    if "type" in df_raw.columns:
        print("type counts:\n", df_raw["type"].value_counts(dropna=False))

    if "moving_time" in df_raw.columns:
        print("moving_time stats:\n", df_raw["moving_time"].describe())
    else:
        print("⚠️  'moving_time' column missing")


    # --- Step 2: Build canonical event-only subset ---------------------------
    #   Always rebuild from raw; ignore any Tier-1 filtered frames.
    df_event_only = (
        df_raw.copy()
        .loc[
            (df_raw["origin"] == "event")
            & (df_raw["moving_time"] > 120)
            & (df_raw["icu_training_load"] > 0)
        ]
        .drop_duplicates(subset=["start_date_local", "elapsed_time"], keep="first")
    )

    if df_event_only.empty:
        raise AuditHalt("❌ enforce_event_only_totals: no valid event rows after filtering")

    # --- Step 3: Canonical recomputation ------------------------------------
    event_hours = df_event_only["moving_time"].sum() / 3600
    event_tss = df_event_only["icu_training_load"].sum()
    event_distance = df_event_only["distance"].sum() / 1000 if "distance" in df_event_only else 0

    if event_hours <= 0 or event_tss <= 0:
        raise AuditHalt("❌ enforce_event_only_totals: invalid totals (zero or negative values)")

    # --- Step 4: Compare with Tier-1 snapshot --------------------------------
    tier1_totals = context.get("tier1_eventTotals", {})
    diff_hours = diff_tss = 0
    if tier1_totals:
        diff_hours = abs(event_hours - tier1_totals.get("hours", 0))
        diff_tss = abs(event_tss - tier1_totals.get("tss", 0))
        if diff_hours > 0.1 or diff_tss > 2:
            context.setdefault("audit_flags", []).append(
                f"⚠️ Tier-2 correction applied: Δh={diff_hours:.2f}, "
                f"ΔTSS={diff_tss:.1f} (Tier-1 replaced with event-only recompute)"
            )

    # --- Step 5: Canonical injection (always overwrite) ---------------------
    for key in ["dailyTotals", "totalHours", "totalTss"]:
        context.pop(key, None)

    context["totalHours"] = round(event_hours, 2)
    context["totalTss"] = int(round(event_tss))
    context["totalDistance"] = round(event_distance, 1)

    context["eventTotals"] = {
        "hours": context["totalHours"],
        "tss": context["totalTss"],
        "distance": context["totalDistance"],
        "source": "tier2_enforce_event_only_totals",
    }
    context["df_event_only"] = df_event_only
    context["enforcement_layer"] = "tier2_enforce_event_only_totals"

    # --- Step 6: Hard-lock canonical totals ----------------------------------
    context.setdefault("_locked_totals", True)
    context["locked_totalHours"] = context["totalHours"]
    context["locked_totalTss"] = context["totalTss"]
    context["locked_totalDistance"] = context["totalDistance"]

    # --- Step 7: Annotate audit trace ----------------------------------------
    context["event_count"] = len(df_event_only)
    context.setdefault("trace", []).append(
        f"T2 independent recompute executed "
        f"(Δh={diff_hours:.2f}, ΔTSS={diff_tss:.1f}, events={len(df_event_only)})"
    )

    return context
