"""
Tier-2 Enforcement — Event-Only Totals (v16.15-PATCH)
Computes canonical totals using Tier-2 validated event dataset if available.
🧩 Updated: 7d FULL dataset excluded from totals — only 7d LIGHT slice allowed.
"""
import os
import pandas as pd
from audit_core.utils import debug
from audit_core.errors import AuditHalt


def enforce_event_only_totals(df_events, context):
    debug(context, "📁 Tier-2 module loaded from:", os.path.abspath(__file__))  
    import pandas as pd

    # --- Step 1: Acquire source dataset -------------------------------------
    report_type = context.get("report_type", "").lower() if isinstance(context, dict) else ""

    # 🧩 PATCH — Prefer 7-day light slice for totals (never totalize full dataset)
    if report_type in ["weekly", "week", "7d"]:
        if "df_light_slice" in context and isinstance(context["df_light_slice"], pd.DataFrame):
            df_source = context["df_light_slice"].copy()
            source_label = "Tier-0 LIGHT 7d slice (safe totals)"
            debug(context, "[T2] ✅ Using df_light_slice for total enforcement (full dataset skipped).")
        else:
            df_source = df_events if df_events is not None and not df_events.empty else context.get("df_raw_activities")
            source_label = "⚠️ Missing df_light_slice — fallback to Tier-2 events"
            debug(context, "[T2 WARN] df_light_slice missing — fallback to df_events/raw_activities.")
    else:
        # SEASON MODE — MUST use 90d dataset (never df_events)
        if "snapshot_90d_json" in context:
            df_source = pd.read_json(context["snapshot_90d_json"])
            source_label = "Tier-2 season snapshot (90d)"
        elif "df_light_full" in context and isinstance(context["df_light_full"], pd.DataFrame):
            df_source = context["df_light_full"].copy()
            source_label = "Tier-0 LIGHT 90d slice"
        else:
            raise AuditHalt("❌ Season report requires 90d dataset; none found")

    debug(context, f"🔍 Tier-2 enforcement source: {source_label} ({df_source.shape[0]} rows)")

    # --- Step 2: Diagnostics -------------------------------------------------
    if "origin" in df_source.columns:
        debug(context, "origin counts:\n", df_source["origin"].value_counts(dropna=False))
    else:
        debug(context, "⚠️  'origin' column missing in dataset")

    if "moving_time" in df_source.columns:
        debug(context, "moving_time stats:\n", df_source["moving_time"].describe())
    else:
        debug(context, "⚠️  'moving_time' column missing")

    # =========================================================
    # 🩵 SAFETY PATCH — Ensure moving_time column integrity
    # =========================================================
    if "moving_time" not in df_source.columns:
        debug(context, "[T2-PATCH] ⚠️ 'moving_time' column completely missing → injecting zeros.")
        df_source["moving_time"] = 0.0
    else:
        # Coerce to numeric and fill any nulls or strings
        df_source["moving_time"] = pd.to_numeric(df_source["moving_time"], errors="coerce").fillna(0.0)
        # If all values are zero, warn so the audit log can show it
        if (df_source["moving_time"] == 0).all():
            debug(context, "[T2-PATCH] ⚠️ 'moving_time' present but all zeros — likely HR-only or manual activities.")

    # Always enforce numeric dtype
    if not pd.api.types.is_numeric_dtype(df_source["moving_time"]):
        df_source["moving_time"] = pd.to_numeric(df_source["moving_time"], errors="coerce").fillna(0.0)

    debug(context, (
        f"[T2-PATCH] ✅ moving_time validated → "
        f"non-null={df_source['moving_time'].notna().sum()}, "
        f"min={df_source['moving_time'].min()}, "
        f"max={df_source['moving_time'].max()}, "
        f"mean={df_source['moving_time'].mean():.1f}"
    ))

    # --- Step 3: Adaptive event-only enforcement ----------------------------
    if report_type == "season":
        debug(context, "🧩 Tier-2 override: retaining full df_source for season summary (no 7-day enforcement).")
        df_event_only = (
            df_source.loc[
                (df_source.get("origin", "event") == "event")
                & (df_source["moving_time"] > 120)
                & (df_source["icu_training_load"] > 0)
            ]
            .drop_duplicates(subset=["id"], keep="first")
            .copy()
        )
    else:
        # ✅ FIX: In weekly mode, treat df_source as the *light* slice (already filtered)
        df_event_only = (
            df_source.loc[
                (df_source["moving_time"] > 120)
                & (df_source["icu_training_load"] > 0)
            ]
            .drop_duplicates(subset=["id"], keep="first")
            .copy()
        )

        debug(
            context,
            f"🧩 Tier-2 weekly/calendar: using {len(df_event_only)} light-slice rows "
            f"for totals (full 7d dataset excluded)."
        )

    # --- Step 4: Canonical recomputation ------------------------------------
    if "moving_time" not in df_event_only.columns:
        raise AuditHalt("❌ enforce_event_only_totals: missing moving_time column")

    df_event_only["moving_time"] = pd.to_timedelta(df_event_only["moving_time"], unit="s").dt.total_seconds()

    raw_sum = df_event_only["moving_time"].sum()
    event_hours = round(raw_sum / 3600, 2)
    event_tss = df_event_only["icu_training_load"].sum()
    event_distance = (
        df_event_only["distance"].sum() / 1000 if "distance" in df_event_only else 0
    )

    if report_type == "season":
        debug(context, f"🧮 Tier-2 (season): Σ(moving_time)={raw_sum:.0f}s → {event_hours:.2f}h, "
              f"Σ(TSS)={event_tss:.1f}, Σ(Distance)={event_distance:.1f} km")
    else:
        debug(context, f"🧮 Tier-2 (weekly, light slice): Σ(moving_time)={raw_sum:.0f}s → {event_hours:.2f}h "
              f"Σ(TSS)={event_tss:.0f} Σ(Distance)={event_distance:.1f} km (safe scalar fields)")

    # --- Step 5 onward: keep existing validation and injection logic unchanged ---

    # --- Step 5: Compare vs Tier-1 snapshot ---------------------------------
    tier1_totals = context.get("tier1_visibleTotals", context.get("tier1_eventTotals", {}))
    validated = False
    if tier1_totals:
        diff_hours = abs(event_hours - tier1_totals.get("hours", 0))
        diff_tss   = abs(event_tss - tier1_totals.get("tss", 0))
        diff_dist  = abs(event_distance - tier1_totals.get("distance", 0))
        if diff_hours < 0.05 and diff_tss < 10 and diff_dist < 2:
            validated = True
            debug(context, f"[T2] Tier-1 totals validated (Δh={diff_hours:.2f}, ΔTSS={diff_tss:.1f}, Δd={diff_dist:.1f})")
        else:
            context.setdefault("audit_flags", []).append(
                f"⚠️ Tier-2 correction applied: Δh={diff_hours:.2f}, ΔTSS={diff_tss:.1f}"
            )

    # --- Step 6: Canonical injection (fixed for season scope) ---------------
    if report_type == "season":
        # ✅ Always override Tier-1 snapshot with full 90-day recompute
        context["totalHours"] = round(event_hours, 2)
        context["totalTss"] = int(round(event_tss))
        context["totalDistance"] = round(event_distance, 1)

        context["tier2_enforced_totals"] = {
            "hours": context["totalHours"],
            "tss": context["totalTss"],
            "distance": context["totalDistance"],
            "source": f"{source_label} • 90-day canonical",
            "validated": True,
        }

        # 🔒 HARD LOCK — prevents weekly bleed-through
        context["locked_totalHours"] = context["totalHours"]
        context["locked_totalTss"] = context["totalTss"]
        context["locked_totalDistance"] = context["totalDistance"]

        context["tier1_visibleTotals"] = context["tier2_enforced_totals"]
        context["eventTotals"] = context["tier2_enforced_totals"]

        debug(context, "[T2] Season mode → forced 90-day canonical totals override.")
        # --- Step 6.1 Trace annotation (mode-safe) ---
        if report_type == "season":
            context.setdefault("trace", []).append(
                f"T2 totals computed from {source_label} "
                f"(season mode, events={len(df_event_only)})"
            )
        else:
            context.setdefault("trace", []).append(
                f"T2 totals computed from {source_label} "
                f"(Δh={diff_hours:.2f}, ΔTSS={diff_tss:.1f}, events={len(df_event_only)})"
            )
    else:
        # Weekly / Calendar logic
        if validated:
            context["tier2_enforced_totals"] = tier1_totals
            context["tier1_visibleTotals"]["validated"] = True
            context["eventTotals"] = tier1_totals
            debug(context, "[T2] Retaining Tier-1 totals as validated canonical snapshot.")
        else:
            # Canonical Tier-2 totals
            context["totalHours"]     = round(event_hours, 2)
            context["totalTss"]       = int(round(event_tss))
            context["totalDistance"]  = round(event_distance, 1)

            context["tier2_enforced_totals"] = {
                "hours": context["totalHours"],
                "tss": context["totalTss"],
                "distance": context["totalDistance"],
                "source": source_label,
                "validated": False,
            }
            context["tier1_visibleTotals"] = context["tier2_enforced_totals"]
            context["eventTotals"]         = context["tier2_enforced_totals"]

            debug(context, "[T2] Overrode Tier-1 totals with Tier-2 enforced canonical values.")
        
    # --- JSON-safe event preview for renderer (lightweight only) -----------------
    try:
        sort_col = "start_date_local" if "start_date_local" in df_event_only.columns else "date"
        cols = [
            c for c in [
                "date", "start_date_local", "name",
                "icu_training_load", "moving_time", "distance",
                "total_elevation_gain", "total_elev_gain"
            ]
            if c in df_event_only.columns
        ]

        df_preview = (
            df_event_only[cols]
            .sort_values(sort_col, ascending=False)
            .head(10)
            .reset_index(drop=True)
        )

        # ✅ Inject lightweight JSON-safe preview for downstream renderers
        context["df_event_only_preview"] = df_preview.to_dict("records")

        # ❌ Do NOT store full DataFrame in context (causes markdown dump bloat)
        debug(
            context,
            f"[DEBUG-T2] injected lightweight df_event_only preview ({len(df_preview)} rows); "
            f"full dataset retained only in memory (not serialized)"
        )

    except Exception as e:
        debug(context, f"[DEBUG-T2] could not build df_event_only preview: {e}")
        context["df_event_only_preview"] = []


    # --- Step 7 moved to end -----------

    # --- Step 8: Trace annotation -------------------------------------------
    context["event_count"] = len(df_event_only)
    context.setdefault("trace", []).append(
        f"T2 totals computed from {source_label} "
        f"(Δh={diff_hours:.2f}, ΔTSS={diff_tss:.1f}, events={len(df_event_only)})"
    )

    # --- Step 9: Recompute derived metrics using proper 90d frame (FIX) -----
    try:
        from audit_core.tier2_derived_metrics import compute_derived_metrics

        if report_type == "season" and "dervied_metrics" not in context:
            df_for_metrics = None
            if "snapshot_90d_json" in context:
                from io import StringIO
                df_for_metrics = pd.read_json(StringIO(context["snapshot_90d_json"]))
                debug(context, "[T2] Season mode → derived metrics using 90d snapshot JSON.")
            elif "df_light_slice" in context:
                df_for_metrics = context["df_light_slice"]
                debug(context, "[T2] Season mode → derived metrics using df_light_slice fallback.")
            else:
                df_for_metrics = df_event_only
                debug(context, "[T2 WARN] Season mode fallback to df_event_only (no 90d source found).")

            derived_metrics = compute_derived_metrics(df_for_metrics, context)
            context["derived_metrics"] = derived_metrics
            debug(context, f"[T2] Recomputed derived metrics for season: {list(derived_metrics.keys())}")

    except Exception as e:
        debug(context, f"[T2 WARN] Failed to recompute derived metrics: {e}")

    # --- Step 10: removced load_metrics sync - set at T1 -----------------------------------

    # --- Step 11: Propagate enriched derived metrics to renderer - removed ------------

    # --- Step 12: Lock canonical totals (safe) ---
    canonical_totals = context.get("tier2_enforced_totals") or context.get("eventTotals") or {}
    context["locked_totalHours"] = context.get("totalHours", canonical_totals.get("time_h", 0))
    context["locked_totalTss"] = context.get("totalTss", canonical_totals.get("tss", 0))
    context["locked_totalDistance"] = context.get("totalDistance", canonical_totals.get("distance_km", 0))

    debug(
        context,
        f"[T2] Locked canonical totals — Hours={context['locked_totalHours']}, "
        f"TSS={context['locked_totalTss']}, Dist={context['locked_totalDistance']} km"
    )

    return context