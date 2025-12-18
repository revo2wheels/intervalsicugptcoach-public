
"""
Tier-1 — Audit Controller (v16.14-Stable++)
Ensures dataset integrity, preserves Tier-0 columns (incl. start_date_local),
and enforces Field Lock Rule for moving_time.
"""
import json
import sys
import pandas as pd
import numpy as np
from audit_core.utils import debug
from audit_core.errors import AuditHalt
from audit_core.utils import validate_dataset_integrity, validate_wellness_alignment

def apply_event_filter(df):
    """Tier-1 proxy to isolate visible endurance events for renderer."""
    # Accept all valid sessions except system sync or nulls
    include_types = [
        "Ride", "VirtualRide", "GravelRide",
        "Hike", "Run", "TrailRun", "Walk"
    ]

    # Filter by sport type when present
    if "type" in df.columns:
        df = df[df["type"].isin(include_types)]

    # Drop duplicates on canonical identifiers
    df = df.drop_duplicates(subset=["id", "start_date_local"], keep="first")

    # Remove ignored, null, or zero-duration records
    if "moving_time" in df.columns:
        df = df[df["moving_time"] > 0]

    return df



def collect_zone_distributions(df_master, athlete_profile, context):
    """Compute separate zone distributions for Power, HR, and Pace."""

    if df_master is None or df_master.empty:
        debug(context,"⚠ collect_zone_distributions: empty df_master")
        context["zone_dist_power"] = {}
        context["zone_dist_hr"] = {}
        context["zone_dist_pace"] = {}
        return context

    # --- Initialize output ---
    context["zone_dist_power"] = {}
    context["zone_dist_hr"] = {}
    context["zone_dist_pace"] = {}

    # --- Debug: show available columns ---
    debug(context,"[DEBUG-ZONE] Available columns:", df_master.columns.tolist())

    # --- POWER ZONES ---
    power_cols = [
        c for c in df_master.columns
        if c.lower().startswith(("power_z", "icu_power_z", "icu_zone_times"))
    ]
    debug(context,"[DEBUG-ZONE] Detected Power zone columns:", power_cols)

    # --- HEART RATE ZONES ---
    hr_cols = [
        c for c in df_master.columns
        if c.lower().startswith(("hr_z", "icu_hr_zone_times"))
    ]
    debug(context,"[DEBUG-ZONE] Detected HR zone columns:", hr_cols)

    # --- PACE ZONES ---
    pace_cols = [
        c for c in df_master.columns
        if c.lower().startswith(("pace_z", "pace_zone_times", "gap_zone_times"))
    ]
    debug(context,"[DEBUG-ZONE] Detected Pace zone columns:", pace_cols)

    # --- Zone Distribution Helper ---
    def compute_zone_dist(cols, label):
        if not cols:
            debug(context,f"[DEBUG-ZONES] No {label} columns found — skipping.")
            return {}
        subset = df_master[cols].select_dtypes(include=[np.number])
        total = subset.sum().sum()
        if total <= 0:
            debug(context,f"[DEBUG-ZONES] No valid data for {label} zones — total=0.")
            return {}
        dist = (subset.sum() / total * 100).round(1).to_dict()
        debug(context,f"[DEBUG-ZONES] {label} zones computed: {dist}")
        return dist

    # --- Compute all zone distributions ---
    context["zone_dist_power"] = compute_zone_dist(power_cols, "power")
    context["zone_dist_hr"] = compute_zone_dist(hr_cols, "hr")
    context["zone_dist_pace"] = compute_zone_dist(pace_cols, "pace")

    return context


    # --- Fallback using athlete profile if no explicit zone data ---
    if not any([context["zone_dist_power"], context["zone_dist_hr"], context["zone_dist_pace"]]):
        debug(context,"⚠ No zone columns found — using athlete profile thresholds if available.")
        if athlete_profile:
            context["zone_dist_power"] = athlete_profile.get("power_zones", {})
            context["zone_dist_hr"] = athlete_profile.get("hr_zones", {})
            context["zone_dist_pace"] = athlete_profile.get("pace_zones", {})

    return context

def run_tier1_controller(df_master, wellness, context):
    import pandas as pd
    from audit_core.errors import AuditHalt
    df_well=None
    debug(context, "[T1] Running Tier-1 controller (weekly mode)")

    # --- 🧩 Canonical Light+Full filter (use merged Tier-0 dataset if available)
    if "df_raw_activities" in context:
        df_raw = context["df_raw_activities"]
        if isinstance(df_raw, pd.DataFrame) and not df_raw.empty:
            debug(context, f"[T1] Using merged df_raw_activities ({len(df_raw)} rows) as base dataset.")
            df_master = df_raw.copy()

            # Apply event-only filter
            if "origin" in df_master.columns:
                before = len(df_master)
                df_master = df_master[df_master["origin"] == "event"].reset_index(drop=True)
                after = len(df_master)
                debug(context, f"[T1] Filtered origin=='event' → {after}/{before} rows retained.")
        else:
            debug(context, "[T1] df_raw_activities found but empty — continuing with Tier-0 df_master.")
    else:
        debug(context, "[T1] No df_raw_activities in context — using direct df_master from Tier-0.")

    # --- Early rehydration of wellness from context if dropped ---
    if (wellness is None or not isinstance(wellness, pd.DataFrame) or wellness.empty):
        if isinstance(context.get("wellness"), pd.DataFrame):
            wellness = context["wellness"]
            debug(context, f"[T1] Recovered wellness from context ({len(wellness)} rows)")


    # Defensive copy of the input DataFrame
    if isinstance(df_master, pd.DataFrame):
        df_master = df_master.copy()
    else:
        raise AuditHalt("❌ Tier-1 received invalid or missing df_master dataset")

    # --- Tier-1 early restoration safeguards ---
    # Rehydrate wellness if dropped during Tier-0 fallback
    if (wellness is None or (isinstance(wellness, pd.DataFrame) and wellness.empty)) \
       and "wellness" in context and isinstance(context["wellness"], pd.DataFrame):
        wellness = context["wellness"].copy()
        debug(context, "[T1] Rehydrated wellness DataFrame from context.")

    # Restore zone/time columns if fallback dataset arrived stripped
    if not df_master.empty:
        zone_cols = [c for c in df_master.columns if c.startswith("icu_zone_") or c.startswith("icu_hr_zone_")]
        if not zone_cols and "icu_zone_times" in context:
            debug(context, "[T1] Rehydrating zone columns from context.")
            try:
                df_master = pd.concat([df_master, context["icu_zone_times"]], axis=1)
            except Exception as e:
                debug(context, f"[T1-WARN] Zone column merge failed: {e}")


    # --- Step 0: Defensive copy (preserve all Tier-0 columns)
    df_master = df_master.copy()
    if "start_date_local" not in df_master.columns:
        raise AuditHalt("❌ Tier-1 missing start_date_local column — verify Tier-0 output")
    debug(context,f"[T1] Columns at entry: {list(df_master.columns)}")

    # --- Step 1: Dataset integrity ---
    if df_master.empty:
        raise ValueError("❌ No activity data received")

    assert "moving_time" in df_master.columns, "❌ moving_time field missing from dataset"
    assert df_master["moving_time"].gt(0).all(), "❌ moving_time contains zero or negative values"

    if df_master["id"].duplicated().any():
        raise ValueError("❌ Duplicate activity IDs detected")

    report_type = str(context.get("report_type", "")).lower()

    # --- 🧩 Tier-1 normalization for snapshot sources ---
    if report_type == "season":
        # Map Tier-0 42-day totals → expected 7-day key (totals only)
        if context.get("tier0_snapshotTotals_42d"):
            context["tier0_snapshotTotals_7d"] = context.get("tier0_snapshotTotals_42d")

        # Only backfill snapshot_7d_json if it is missing
        if not context.get("snapshot_7d_json"):
            snap42 = context.get("snapshot_42d_json")
            if snap42:
                context["snapshot_7d_json"] = snap42
                debug(context, "[T1] snapshot_7d_json backfilled from snapshot_42d_json")

        # Build per-week rollup for season totals (independent of snapshot_7d_json)
        snap42 = context.get("snapshot_42d_json")
        if snap42:
            import pandas as pd
            df = pd.DataFrame(snap42)
            if not df.empty and "start_date_local" in df.columns:
                df["start_date_local"] = pd.to_datetime(
                    df["start_date_local"], errors="coerce"
                )
                df["week"] = df["start_date_local"].dt.isocalendar().week

                weekly = df.groupby("week", as_index=False).agg({
                    "moving_time": "sum",
                    "distance": "sum",
                    "icu_training_load": "sum"
                })

                context["tier1_weekly_summary"] = weekly.to_dict(orient="records")
                context["tier1_visibleTotals"] = {
                    "hours": weekly["moving_time"].sum() / 3600,
                    "distance": weekly["distance"].sum() / 1000,
                    "tss": weekly["icu_training_load"].sum(),
                    "weeks": len(weekly),
                    "source": "Tier-1 seasonal weekly roll-up"
                }

                debug(context, f"[T1] Built seasonal weekly roll-up ({len(weekly)} weeks)")


    # --- Step 2: Unified totals initialisation (linked to Tier-0 lightweight snapshot) ---
    import pandas as pd, json
    from io import StringIO

    # Validate Tier-0 context
    if "tier0_snapshotTotals_7d" not in context:
        raise AuditHalt("❌ Tier-1: missing Tier-0 7-day snapshot totals")

    # --- Unified visible totals with mean metrics ----
    t0 = (context.get("tier0_snapshotTotals_7d") or {}).copy()

    # Ensure the 7-day snapshot JSON exists
    if "snapshot_7d_json" not in context or not context["snapshot_7d_json"]:
        raise AuditHalt("❌ Tier-1: missing snapshot_7d_json for visible subset mean metrics")

    # --- Safely rehydrate snapshot_7d_json ----
    snapshot = context["snapshot_7d_json"]
    if isinstance(snapshot, (list, dict)):
        visible_events = pd.DataFrame(snapshot)
    elif isinstance(snapshot, str):
        try:
            visible_events = pd.read_json(StringIO(snapshot))
        except ValueError as e:
            raise AuditHalt(f"❌ Tier-1: invalid JSON in snapshot_7d_json → {e}")
    else:
        raise AuditHalt(f"❌ Tier-1: unsupported type for snapshot_7d_json → {type(snapshot)}")

    # Validate schema before continuing
    if not isinstance(visible_events, pd.DataFrame) or "type" not in visible_events.columns:
        raise AuditHalt(
            f"❌ Tier-1: snapshot_7d_json missing required 'type' column "
            f"(columns={visible_events.columns.tolist() if hasattr(visible_events, 'columns') else 'N/A'})"
        )

    # Ensure numeric for mean computations
    for col in ["IF", "average_heartrate", "VO2MaxGarmin"]:
        if col in visible_events.columns:
            visible_events[col] = pd.to_numeric(visible_events[col], errors="coerce").fillna(0)

    # Placeholder before cycling refinement
    t0["avg_if"] = None
    t0["avg_hr"] = None
    t0["vo2max"] = None
    context["tier1_visibleTotals"] = t0

    debug(
        context,
        f"[Tier-1] Visible subset unified: {t0.get('hours', 0):.2f} h | "
        f"{t0.get('distance', 0):.1f} km | {t0.get('tss', 0)} TSS | "
        f"IF={t0.get('avg_if')} HR={t0.get('avg_hr')} VO₂={t0.get('vo2max')}"
    )

    # --- Cycling-only refinement for mean metrics ---
    cycling_subset = visible_events[visible_events["type"].isin(["Ride", "VirtualRide", "Workout"])].copy()
    if not cycling_subset.empty:
        context["tier1_visibleTotals"].update({
            "avg_if": round(cycling_subset["IF"].mean(), 2)
            if "IF" in cycling_subset.columns else 0,
            "avg_hr": int(cycling_subset["average_heartrate"].mean())
            if "average_heartrate" in cycling_subset.columns else None,
            "vo2max": round(
                cycling_subset.loc[cycling_subset["VO2MaxGarmin"] > 30, "VO2MaxGarmin"].mean(), 1
            )
            if "VO2MaxGarmin" in cycling_subset.columns else None,
        })

    # Serialize validated event log for renderer
    context["weeklyEventLogBlock"] = json.loads(
        visible_events.to_json(orient="records", double_precision=2)
    )

    required_keys = ["weeklyEventLogBlock", "tier1_visibleTotals"]
    if not all(k in context for k in required_keys) or len(context["weeklyEventLogBlock"]) == 0:
        raise AuditHalt("❌ Tier-1: missing or empty event data before render")

    # Confirm audit completion
    context["auditFinal"] = True
    debug(
        context,
        f"✅ Tier-1 finalization: {len(context['weeklyEventLogBlock'])} events | "
        f"{context['tier1_visibleTotals']['hours']} h | "
        f"{context['tier1_visibleTotals']['tss']} TSS"
    )

   # --- Step 3: Basic variance validation (unified) ---
    t1_hours = context.get("tier1_visibleTotals", {}).get("hours", 0)
    t1_tss = context.get("tier1_visibleTotals", {}).get("tss", 0)

    if t1_hours <= 0 or t1_tss <= 0:
        raise AuditHalt("❌ Tier-1: invalid or missing canonical totals from Tier-0 snapshot")

    context.pop("dailyTotals", None)
    context["df_events"] = df_master

    # --- Step 4: Cross-verification (unified) ---
    # Compare Tier-0 snapshot vs Tier-1 revalidated totals
    t0_hours = context.get("tier0_snapshotTotals_7d", {}).get("hours", 0)
    t0_tss = context.get("tier0_snapshotTotals_7d", {}).get("tss", 0)
    diff_hours = abs(t0_hours - t1_hours)
    diff_tss = abs(t0_tss - t1_tss)

    if diff_hours > 0.1:
        raise AuditHalt(f"❌ Tier-1 cross-check variance >0.1 h (Δ={diff_hours:.2f})")
    if diff_tss > 2:
        raise AuditHalt(f"❌ Tier-1 cross-check variance >2 TSS (Δ={diff_tss:.1f})")

    debug(context, f"🧩 Tier-1 variance check passed (Δh={diff_hours:.2f}, ΔTSS={diff_tss:.1f})")

    # --- Step 4.5: Normalize and pre-merge wellness with activities ---
    if isinstance(wellness, pd.DataFrame) and not wellness.empty:
        debug(context, "[T1] Normalizing and merging wellness with activity dataset before alignment check.")
        try:
            # Normalize merge keys to dates (no timezone)
            if "start_date_local" in df_master.columns:
                df_master["merge_date"] = pd.to_datetime(df_master["start_date_local"], errors="coerce").dt.date
            elif "date" in df_master.columns:
                df_master["merge_date"] = pd.to_datetime(df_master["date"], errors="coerce").dt.date

            wellness["merge_date"] = pd.to_datetime(wellness["date"], errors="coerce").dt.date

            # Merge wellness data into df_master for enriched downstream analysis
            df_master = pd.merge(
                df_master,
                wellness,
                on="merge_date",
                how="left",
                suffixes=("", "_well"),
            )

            debug(context, f"[T1] Wellness merged successfully — shape={df_master.shape}")
        except Exception as e:
            debug(context, f"[T1-WELLNESS-MERGE-WARN] Failed to merge wellness data: {e}")
    else:
        debug(context, "[T1] No valid wellness data found pre-merge; skipping normalization.")


    # --- Step 5: Wellness alignment check ---
    if wellness is None or (isinstance(wellness, pd.DataFrame) and wellness.empty):
        debug(context,"⚠ No wellness data available for window; continuing with activity-only audit")
    else:
        validate_wellness_alignment(df_master, wellness)

        # --- Step 6: Daily wellness normalization & summary build ---
    df_master["date"] = pd.to_datetime(df_master["start_date_local"]).dt.date
    daily_summary = pd.DataFrame()

    if isinstance(wellness, (list, pd.DataFrame)) and len(wellness) > 0:
        df_well = pd.DataFrame(wellness).copy()
        df_well.columns = [c.lower() for c in df_well.columns]

        # --- Normalize field names for consistency ---
        rename_map = {
        "restinghr": "rest_hr",
        "fatigue_score": "fatigue",
        "stress_score": "stress",
        "readiness_score": "readiness",
        "atl_load": "atl",
        "ctl_load": "ctl",
        "atlload": "atl",
        "ctlload": "ctl",
        }

        df_well.rename(columns={k: v for k, v in rename_map.items() if k in df_well.columns}, inplace=True)

        # --- Guarantee a valid date column ---
        if "date" not in df_well.columns:
            if "id" in df_well.columns:
                df_well.rename(columns={"id": "date"}, inplace=True)
                debug(context, "[T1] Wellness 'id' renamed to 'date'.")
            else:
                debug(context, "[T1] Wellness missing date/id — inserting placeholder.")
                df_well["date"] = pd.NaT
        df_well["date"] = pd.to_datetime(df_well["date"], errors="coerce")

        for col in ["fatigue", "stress", "readiness", "atl", "ctl", "rest_hr", "hrv"]:
            if col in df_well.columns:
                try:
                    df_well[col] = pd.to_numeric(df_well[col], errors="coerce")
                except Exception as e:
                    debug(context, f"[T1-WELLNESS] numeric coercion failed for {col}: {e}")


        # --- Derived wellness metrics ---
        rest_hr = round(df_well["rest_hr"].tail(7).mean(skipna=True), 1) if "rest_hr" in df_well.columns else np.nan
        hrv_trend = np.nan
        if "hrv" in df_well.columns and df_well["hrv"].count() >= 2:
            last_two = df_well["hrv"].dropna().tail(2).tolist()
            if len(last_two) == 2:
                hrv_trend = round(last_two[-1] - last_two[-2], 1)

        fatigue_avg = round(df_well["fatigue"].mean(skipna=True), 1) if "fatigue" in df_well.columns else np.nan
        stress_avg = round(df_well["stress"].mean(skipna=True), 1) if "stress" in df_well.columns else np.nan
        readiness_avg = round(df_well["readiness"].mean(skipna=True), 1) if "readiness" in df_well.columns else np.nan

        # --- Objective + subjective rest-day logic ---
        today = pd.Timestamp.now().normalize()
        mask_past = df_well["date"] < today

        load_col = None
        for candidate in ["load", "icu_training_load", "atl", "ctl"]:
            if candidate in df_well.columns:
                load_col = candidate
                break

       # --- Determine rest days based on *no training load* days before today ---
        debug(context, "[T1-REST] Starting rest day calculation from df_master.")

        # ------------------------------------------------------------
        # Rest-day base dataset (authoritative)
        # Weekly  → df_master (7d full)
        # Season  → df_light   (90d light)
        # ------------------------------------------------------------
        if context.get("report_type") == "season" and isinstance(context.get("df_light"), pd.DataFrame):
            rest_df = context["df_light"].copy()
            debug(context, "[T1-REST] Season mode → using df_light for rest-day calculation")
        else:
            rest_df = df_master.copy()
            debug(context, "[T1-REST] Weekly mode → using df_master for rest-day calculation")

        # Normalize dates
        rest_df["date"] = (
            pd.to_datetime(rest_df["start_date_local"], errors="coerce")
            .dt.tz_localize(None)
            .dt.normalize()
        )

        window_start = rest_df["date"].min()
        today = pd.Timestamp.now().normalize()
        date_range = pd.date_range(window_start, today, freq="D")


        # ------------------------------------------------------------
        # Aggregate daily load correctly (scope-aware)
        # Weekly  → df_master (7-day full)
        # Season  → df_light  (90-day light)
        # ------------------------------------------------------------

        if context.get("report_type") == "season" and isinstance(context.get("df_light"), pd.DataFrame):
            rest_df = context["df_light"].copy()
            debug(context, "[T1-REST] Season mode → using df_light for rest-day calculation")
        else:
            rest_df = df_master.copy()
            debug(context, "[T1-REST] Weekly mode → using df_master for rest-day calculation")

        # Normalize dates
        rest_df["date"] = (
            pd.to_datetime(rest_df["start_date_local"], errors="coerce")
            .dt.tz_localize(None)
            .dt.normalize()
        )

        window_start = rest_df["date"].min()
        today = pd.Timestamp.now().normalize()
        date_range = pd.date_range(window_start, today, freq="D")

        # --- Aggregate daily load ---
        if "icu_training_load" in rest_df.columns:
            debug(context, "[T1-REST] Using icu_training_load as primary load source.")
            daily_load = (
                rest_df.groupby("date")["icu_training_load"]
                .sum(min_count=1)
                .reindex(date_range, fill_value=0)
            )
        elif "tss" in rest_df.columns:
            debug(context, "[T1-REST] Fallback: using TSS as load source.")
            daily_load = (
                rest_df.groupby("date")["tss"]
                .sum(min_count=1)
                .reindex(date_range, fill_value=0)
            )
        else:
            debug(context, "[T1-REST] ❌ No valid load column found (icu_training_load/TSS).")
            daily_load = pd.Series(dtype=float, index=date_range)

        debug(context, f"[T1-REST] Daily load sample (last 7 days): {daily_load.tail(7).to_dict()}")

        mask_past = daily_load.index < today
        rest_days = int((daily_load.loc[mask_past] < 1).sum())
        rest_dates = [
            d.strftime("%Y-%m-%d")
            for d, v in daily_load.loc[mask_past].items()
            if v < 1
        ]

        debug(context, f"[T1-REST] Counted rest days: {rest_days} → Dates: {rest_dates}")


        # --- Debug readiness data completeness ---
        debug(context, f"[T1-READINESS] readiness column summary: "
                    f"exists={'readiness' in df_well.columns}, "
                    f"non-null count={df_well['readiness'].notna().sum() if 'readiness' in df_well.columns else 0}, "
                    f"values={df_well['readiness'].dropna().tolist() if 'readiness' in df_well.columns else 'n/a'}")


        # --- Build wellness summary block ---
        context["wellness_metrics"] = {
            "rest_hr": rest_hr,
            "hrv_trend": hrv_trend,
            "rest_days": rest_days,
            "fatigue": fatigue_avg,
            "stress": stress_avg,
            "readiness": readiness_avg,
        }
        context["wellness_summary"] = context["wellness_metrics"]
        context["wellness"] = context["wellness_metrics"]

        debug(context, f"[T1] Wellness summary → rest_days={rest_days}, rest_hr={rest_hr}, hrv_trend={hrv_trend}")

        daily_summary = df_well.copy()
    else:
        context["wellness_metrics"] = {
            "rest_hr": np.nan, "hrv_trend": np.nan,
            "rest_days": 0, "fatigue": np.nan, "stress": np.nan, "readiness": np.nan,
        }
        context["wellness_summary"] = context["wellness_metrics"]

    context["dailyMerged"] = daily_summary

    # --- Step 6a: Extract CTL / ATL / TSB from *latest* wellness record only (AUTHORITATIVE) ---
    if isinstance(wellness, pd.DataFrame) and not wellness.empty:
        df_well = wellness.copy()
        df_well.columns = [c.strip().lower() for c in df_well.columns]

        # Identify date column
        date_col = next(
            (c for c in ("date", "day", "start_date_local", "start_date") if c in df_well.columns),
            None
        )

        if date_col:
            df_well[date_col] = pd.to_datetime(df_well[date_col], errors="coerce")
            df_well = df_well.sort_values(date_col)

        last = df_well.iloc[-1]

        ctl = pd.to_numeric(last.get("ctl"), errors="coerce")
        atl = pd.to_numeric(last.get("atl"), errors="coerce")
        tsb = pd.to_numeric(last.get("tsb"), errors="coerce") if "tsb" in df_well.columns else None

        if pd.isna(tsb) and pd.notna(ctl) and pd.notna(atl):
            tsb = ctl - atl

        context["ctl"] = float(ctl) if pd.notna(ctl) else None
        context["atl"] = float(atl) if pd.notna(atl) else None
        context["tsb"] = float(tsb) if pd.notna(tsb) else None

        # 🔒 AUTHORITATIVE wellness snapshot ONLY
        context["wellness_summary"] = {
            "ctl": context["ctl"],
            "atl": context["atl"],
            "tsb": context["tsb"],
            "recovery": last.get("recovery"),
            "fatigue": last.get("fatigue"),
            "fitness": last.get("fitness"),
            "form": last.get("form"),
        }

        # For renderer / UI only — Tier-2 must stay source of truth
        context["load_metrics"] = {
            "CTL": {"value": context["ctl"], "status": "icu"},
            "ATL": {"value": context["atl"], "status": "icu"},
            "TSB": {"value": context["tsb"], "status": "icu"},
        }

        debug(
            context,
            f"[T1-WELLNESS-LATEST] CTL={context['ctl']} ATL={context['atl']} TSB={context['tsb']}"
        )
    else:
        debug(context, "[T1] No valid wellness DataFrame — skipping wellness hydration")


    # --- Step 6b: Build HR / Power / Pace zone distributions ---

    debug(context, f"[DEBUG-T1] sanity check before Step 6b — rows in df_master: {len(df_master)}")
    athleteProfile = context.get("athleteProfile", {}) or {}

    try:
        debug(context, "[DEBUG-T1] Starting zone distribution extraction...")

        report_type = str(context.get("report_type", "")).lower()
        zone_df = df_master
        scope = "7d"

        if report_type == "season" and isinstance(context.get("df_light"), pd.DataFrame):
            candidate = context["df_light"]

            zone_cols = [
                c for c in candidate.columns
                if c.lower().startswith(("power_z", "icu_power_z", "icu_zone_times", "hr_z", "icu_hr_zone_times"))
            ]

            if zone_cols:
                zone_df = candidate
                scope = "90d"
                debug(context, "[T1-ZONE] Season mode → using df_light for zone distributions")
            else:
                debug(context, "[T1-ZONE] df_light has no zone cols → fallback to df_master")

        # --- Compute into temp context ---
        tmp = {}
        tmp = collect_zone_distributions(zone_df, athleteProfile, tmp)

        # 🔒 CANONICAL KEYS (Tier-2 depends on these)
        context["zone_dist_power"] = tmp.get("zone_dist_power") or {}
        context["zone_dist_hr"]    = tmp.get("zone_dist_hr") or {}
        context["zone_dist_pace"]  = tmp.get("zone_dist_pace") or {}

        # 🧭 Scoped copies for debugging / UI
        context[f"zone_dist_power_{scope}"] = context["zone_dist_power"]
        context[f"zone_dist_hr_{scope}"]    = context["zone_dist_hr"]
        context[f"zone_dist_pace_{scope}"]  = context["zone_dist_pace"]
        context["zone_scope"] = scope

        debug(context, f"[T1-ZONE] Completed zone dist extraction (scope={scope})")
        debug(context, f"  power: {context['zone_dist_power']}")
        debug(context, f"  hr:    {context['zone_dist_hr']}")

    except Exception as e:
        debug(context, f"⚠ Zone distribution collection failed: {e}")
        context["zone_dist_power"] = {}
        context["zone_dist_hr"] = {}
        context["zone_dist_pace"] = {}
        context["zone_scope"] = "none"

    # --- Step 6c: Outlier Detection ---
    try:
        df = df_master.copy()
        debug(context, f"[DEBUG-OUTLIER] Starting detection on {len(df)} rows")
        if "icu_training_load" in df.columns:
            mean_tss = df["icu_training_load"].mean()
            std_tss = df["icu_training_load"].std()
            threshold = 1.5 * std_tss  # slightly more sensitive than 2σ

            outliers = df[
                (df["icu_training_load"] > mean_tss + threshold) |
                (df["icu_training_load"] < mean_tss - threshold)
            ][["id", "name", "start_date_local", "icu_training_load"]]

            outliers_formatted = []
            for _, o in outliers.iterrows():
                outliers_formatted.append({
                    "date": str(o.get("start_date_local", "?")).split(" ")[0],
                    "event": o.get("name", "?"),
                    "issue": "TSS outlier",
                    "obs": f"TSS={o.get('icu_training_load', '?')}"
                })
            context["outliers"] = outliers_formatted

            debug(context, f"[DEBUG-T1] Outlier events detected: {len(outliers)}")
            debug(context, f"[DEBUG-OUTLIER] mean TSS={mean_tss:.1f}, std={std_tss:.1f}, threshold={threshold:.1f}")
            debug(context, f"[DEBUG-OUTLIER] min/max TSS: {df['icu_training_load'].min()} / {df['icu_training_load'].max()}")
        else:
            context["outliers"] = []
            debug(context, "[DEBUG-OUTLIER] No icu_training_load column found.")
    except Exception as e:
        debug(context, f"⚠ Outlier detection failed: {e}")
        context["outliers"] = []


    # --- Step 7: Qualitative label translation ---
    rpe_map = {1: "very easy", 2: "easy", 3: "moderate", 4: "somewhat hard",
               5: "hard", 6: "very hard", 7: "maximal", 8: "maximal+",
               9: "extreme", 10: "all out"}
    feel_map = {1: "very bad", 2: "bad", 3: "neutral", 4: "good", 5: "very good"}
    label_map = {1: "very low", 2: "low", 3: "moderate", 4: "high", 5: "very high"}
    mood_map = {1: "very bad", 2: "bad", 3: "neutral", 4: "good", 5: "very good"}
    motiv_map = {1: "none", 2: "low", 3: "moderate", 4: "good", 5: "excellent"}
    hydr_map = {1: "overhydrated", 2: "slightly high", 3: "optimal", 4: "slightly low", 5: "dehydrated"}
    ready_map = {1: "very poor", 2: "poor", 3: "fair", 4: "good", 5: "excellent"}

    for col, cmap in {
        "rpe": rpe_map, "feel": feel_map,
        "fatigue": label_map, "stress": label_map, "soreness": label_map,
        "mood": mood_map, "motivation": motiv_map,
        "hydration": hydr_map, "readiness": ready_map,
    }.items():
        if col in daily_summary.columns:
            daily_summary[f"{col}_label"] = daily_summary[col].map(cmap).fillna(daily_summary[col])

    # --- Step 8: Finalize ---
    context["auditPartial"] = True
    context["auditFinal"] = False

    # --- Inject 90-day lightweight dataset forward for Tier-2 derived metrics ---
    try:
        if "df_light_slice" not in context:
            if "activities_light" in context and isinstance(context["activities_light"], pd.DataFrame):
                context["df_light_slice"] = context["activities_light"]
                debug(context, f"[TRACE] Injected df_light_slice from activities_light → {len(context['df_light_slice'])} rows.")
            elif "snapshot_90d_json" in context:
                from io import StringIO
                import pandas as pd
                df90 = pd.read_json(StringIO(context["snapshot_90d_json"]))
                context["df_light_slice"] = df90
                debug(context, f"[TRACE] Rehydrated df_light_slice from snapshot_90d_json → {len(df90)} rows.")
        else:
            debug(context, f"[TRACE] df_light_slice already present → {len(context['df_light_slice'])} rows.")
    except Exception as e:
        debug(context, f"[TRACE] Failed to ensure df_light_slice for Tier-2: {e}")

    # --- 🧩 Final Tier-1 event summary
    if isinstance(df_master, pd.DataFrame) and not df_master.empty:
        total_h = df_master["moving_time"].sum() / 3600 if "moving_time" in df_master else 0
        total_tss = df_master["icu_training_load"].sum() if "icu_training_load" in df_master else 0
        total_km = df_master["distance"].sum() / 1000 if "distance" in df_master else 0
        debug(context, f"[T1] Summary → {len(df_master)} events | {total_h:.2f} h | {total_tss:.0f} TSS | {total_km:.1f} km")

    return df_master, wellness, context