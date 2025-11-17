"""
Tier-2 Enforcement — Event-Only Totals (v16.14-Integrated)
Computes canonical totals using Tier-2 validated event dataset if available.
Falls back to raw Tier-0 data only if no DataFrame is passed.
"""
import os
import pandas as pd
from audit_core.utils import debug
from audit_core.errors import AuditHalt


def enforce_event_only_totals(df_events, context):
    debug(context, "📁 Tier-2 module loaded from:", os.path.abspath(__file__))  
    import pandas as pd

    # --- Step 1: Acquire source dataset -------------------------------------
    if df_events is not None and not df_events.empty:
        df_source = df_events.copy()
        source_label = "Tier-2 validated events"
    else:
        df_source = context.get("df_raw_activities")
        source_label = "raw Tier-0 activities (fallback)"
        if df_source is None or df_source.empty:
            raise AuditHalt("❌ enforce_event_only_totals: no dataset available from Tier-2 or Tier-0")

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

    # --- Step 3: Adaptive event-only enforcement ----------------------------
    report_type = context.get("report_type", "").lower() if isinstance(context, dict) else ""

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
        df_event_only = (
            df_source.loc[
                (df_source.get("origin", "event") == "event")
                & (df_source["moving_time"] > 120)
                & (df_source["icu_training_load"] > 0)
            ]
            .drop_duplicates(subset=["id"], keep="first")
            .copy()
        )
        if len(df_event_only) > 7:
            df_event_only = df_event_only.sort_values("start_date_local", ascending=False).head(7)
        debug(context, "🧩 Tier-2 enforcing canonical 7-day event window.")

    # --- Step 4: Canonical recomputation ------------------------------------
    if "moving_time" not in df_event_only.columns:
        raise AuditHalt("❌ enforce_event_only_totals: missing moving_time column")

    df_event_only["moving_time"] = pd.to_timedelta(df_event_only["moving_time"], unit="s").dt.total_seconds()

    if report_type == "season":
        debug(context, "🧩 Tier-2 override: recomputing canonical totals for season report (full dataset).")
        raw_sum = df_event_only["moving_time"].sum()
        event_hours = round(raw_sum / 3600, 2)
        event_tss = df_event_only["icu_training_load"].sum()
        event_distance = (
            df_event_only["distance"].sum() / 1000 if "distance" in df_event_only else 0
        )
        debug(context, f"🧮 Tier-2 (season): Σ(moving_time)={raw_sum:.0f}s → {event_hours:.2f}h, "
              f"Σ(TSS)={event_tss:.1f}, Σ(Distance)={event_distance:.1f} km")
    else:
        raw_sum = df_event_only["moving_time"].sum()
        event_hours = round(raw_sum / 3600, 2)
        event_tss = df_event_only["icu_training_load"].sum()
        event_distance = (
            df_event_only["distance"].sum() / 1000 if "distance" in df_event_only else 0
        )
        debug(context, f"🧮 Tier-2: Σ(moving_time)={raw_sum:.0f}s → {event_hours:.2f}h (Intervals seconds source)")

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

    # --- JSON-safe preview for renderer -------------------------------------
    try:
        sort_col = "start_date_local" if "start_date_local" in df_event_only.columns else "date"
        cols = [c for c in ["date", "start_date_local", "name", "icu_training_load",
                            "moving_time", "distance", "total_elevation_gain", "total_elev_gain"]
                if c in df_event_only.columns]
        df_preview = df_event_only[cols].sort_values(sort_col, ascending=False).head(10)
        context["df_event_only_preview"] = df_preview.to_dict("records")
        context["df_event_only_full"] = df_event_only
        debug(context, f"[DEBUG-T2] injected preview ({len(df_preview)} rows) and preserved full df_event_only ({len(df_event_only)} rows)")
    except Exception as e:
        debug(context, f"[DEBUG-T2] could not build df_event_only preview: {e}")
        context["df_event_only_preview"] = []
        context["df_event_only_full"] = df_event_only

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

        # --- Step 9: Recompute derived metrics using proper 90d frame (FIX) -----
    try:
        from audit_core.tier2_derived_metrics import compute_derived_metrics

        if report_type == "season":
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

    # --- Step 10: Final load_metrics sync -----------------------------------
    if all(k in context for k in ["ctl", "atl", "tsb"]):
        context["load_metrics"] = {
            "CTL": {"value": round(context.get("ctl", 0), 2), "status": "ok"},
            "ATL": {"value": round(context.get("atl", 0), 2), "status": "ok"},
            "TSB": {"value": round(context.get("tsb", 0), 2), "status": "ok"},
        }
        debug(context, "[DEBUG-T2] enforced load_metrics sync in context:", context["load_metrics"])

    # --- Step 11: Propagate enriched derived metrics to renderer ------------
    if "derived_metrics" in context:
        context.setdefault("load_metrics", {})
        for metric, meta in context["derived_metrics"].items():
            if isinstance(meta, dict):
                context["load_metrics"][metric] = {
                    "value": meta.get("value"),
                    "status": meta.get("status"),
                    "icon": meta.get("icon"),
                }

    debug(context, "[T2] Enriched load_metrics propagated to renderer")

    return context
