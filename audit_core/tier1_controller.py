
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
    """
    Compute separate zone distributions for Power, HR, and Pace (Intervals.icu safe).
    Supports both Power.Z1 and power_z1 naming.
    Always uses 7-day df_master (never 90-day light).
    """

    import pandas as pd, numpy as np, re, json, ast

    # --- Basic validation ---
    if df_master is None or df_master.empty:
        debug(context, "⚠ collect_zone_distributions: empty df_master")
        for key in ("zone_dist_power", "zone_dist_hr", "zone_dist_pace"):
            context[key] = {}
        return context

    # --- 🧩 Normalize all possible dot/space/prefix variants ---
    df_master = df_master.copy()
    df_master.columns = [
        c.replace("Power.Z", "power_z")
         .replace("power.Z", "power_z")
         .replace("HR.Z", "hr_z")
         .replace("Hr.Z", "hr_z")
         .replace("Pace.Z", "pace_z")
         .replace(".", "_")
         .strip()
         .lower()
        for c in df_master.columns
    ]

    debug(context, f"[ZONES] Normalized columns → {len(df_master.columns)} total")

    # --- 🩹 Expand icu_zone_times only if not already flattened ---
    if "power_z1" not in df_master.columns and "icu_zone_times" in df_master.columns:
        debug(context, "[DEBUG-ZONES] Found icu_zone_times — attempting to expand.")
        import pandas as pd, ast, json, numpy as np

        def safe_parse_zone(x):
            if isinstance(x, (dict, list)):
                return x
            if isinstance(x, str):
                x = x.strip()
                if x.startswith('"[{') or x.startswith("'[{"):
                    try:
                        x = json.loads(x)
                    except Exception:
                        pass
                for parser in (json.loads, ast.literal_eval):
                    try:
                        val = parser(x)
                        if isinstance(val, (dict, list)):
                            return val
                    except Exception:
                        continue
            return None

        parsed = df_master["icu_zone_times"].dropna().apply(safe_parse_zone)
        parsed = parsed.dropna()

        if not parsed.empty:
            try:
                sample = parsed.iloc[0]
                debug(context, f"[DEBUG-ZONES] sample type={type(sample)} content={str(sample)[:1000]}")

                # ✅ CASE 1: Already flattened (dict-of-dicts or ICU JSON)
                if isinstance(sample, dict):
                    zone_df = pd.json_normalize(parsed)
                    zone_df.columns = [f"power_{str(c).lower()}" for c in zone_df.columns]
                    df_master = pd.concat([df_master, zone_df], axis=1)
                    debug(context, f"[DEBUG-ZONES] ✅ Expanded dict-based icu_zone_times → {len(zone_df.columns)} new columns")

                # ✅ CASE 2: List of dicts (Intervals-style [{'id':'Z1','secs':...}, ...])
                elif isinstance(sample, list) and all(isinstance(z, dict) for z in sample):
                    # --- 🩹 FIX: Expand icu_zone_times for every row, not just one sample ---
                    def expand_row(zlist):
                        row = {}
                        if isinstance(zlist, list):
                            for z in zlist:
                                zid = str(z.get("id", "")).strip().upper()
                                secs = float(z.get("secs", 0))
                                if zid.startswith("Z"):
                                    row[f"power_z{zid[1:]}"] = secs
                                elif zid == "SS":
                                    row["power_sweetspot"] = secs
                        return row

                    try:
                        expanded = df_master["icu_zone_times"].apply(expand_row)
                        zone_df = pd.DataFrame(list(expanded)).fillna(0)

                        # 🩹 Ensure index alignment before concatenation
                        zone_df.reset_index(drop=True, inplace=True)
                        df_master.reset_index(drop=True, inplace=True)

                        # 🩹 Rename Z8 → power_sweetspot for consistency (Intervals often use Z8 = SS)
                        if "power_z8" in zone_df.columns and "power_sweetspot" not in zone_df.columns:
                            zone_df.rename(columns={"power_z8": "power_sweetspot"}, inplace=True)

                        # 🩹 Merge into master frame
                        df_master = pd.concat([df_master, zone_df], axis=1)

                        debug(
                            context,
                            f"[DEBUG-ZONES] ✅ Expanded icu_zone_times row-wise for {len(zone_df)} rows "
                            f"→ {list(zone_df.columns)}"
                        )

                        # 🧩 Extra visibility for validation
                        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                            debug(
                                context,
                                f"[DEBUG-ZONES] FULL power dataset:\n{df_master[[c for c in zone_df.columns if c in df_master]].to_string(index=True)}"
                            )

                    except Exception as e:
                        debug(context, f"[DEBUG-ZONES] ⚠️ Row-wise expansion failed: {e}")

            except Exception as e:
                debug(context, f"[DEBUG-ZONES] ⚠️ Failed to expand icu_zone_times ({e})")


    # --- 🔍 Helper: detect zone columns by prefix ---
    def detect(prefixes):
        cols = []
        for c in df_master.columns:
            if any(c.startswith(p) for p in prefixes):
                cols.append(c)
        return sorted(cols)

    # --- Detect columns ---
    power_cols = detect(["power_z", "icu_power_z", "zones_power_z"])
    hr_cols    = detect(["hr_z", "icu_hr_zone", "zones_hr_z"])
    pace_cols  = detect(["pace_z", "zones_pace_z", "gap_zone", "gap_zone_times", "pace_zone_times"])
    swim_cols = detect(["swim_z", "zones_swim_z", "swim_pace_z"])

    debug(context, f"[DEBUG-ZONES] Power cols={power_cols}")
    debug(context, f"[DEBUG-ZONES] HR cols={hr_cols}")
    debug(context, f"[DEBUG-ZONES] Pace cols={pace_cols}")
    debug(context, f"[DEBUG-ZONES] Swim cols={swim_cols}")

    # --- 🧮 Compute zone distributions ---
    def compute(cols, label):
        if not cols:
            debug(context, f"[DEBUG-ZONES] ❌ No {label} columns found — skipping.")
            return {}

        # 🩹 Optional cleanup: remove any non-time columns like icu_power_zones
        cols = [c for c in cols if c.lower() != "icu_power_zones"]

        # Function to extract seconds from zones, handling missing or None data
        def extract_secs(value):
            if isinstance(value, list):  # If it's a list (like the railway data)
                #debug(context, f"[DEBUG-ZONES] Extracting 'secs' from list: {value}")
                # Handle missing or invalid entries inside the list
                total_secs = 0
                for entry in value:
                    if isinstance(entry, dict) and "secs" in entry:
                        total_secs += entry["secs"]
#                    else:
#                       debug(context, f"[DEBUG-ZONES] Invalid entry in zone: {entry}")
                return total_secs
#           debug(context, f"[DEBUG-ZONES] Value is not a list: {value}")
            return value if isinstance(value, (int, float)) else 0  # Default to 0 for non-numeric values

        # Apply the function to handle the lists and convert all data to numeric
        subset = df_master[cols].applymap(extract_secs).apply(pd.to_numeric, errors="coerce").fillna(0)

        # Debugging full table for raw data and subset
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            raw_data = df_master[cols].to_string(index=False)
        debug(context, f"[DEBUG-ZONES] FULL {label} dataset:\n{raw_data}")
        debug(context, f"[DEBUG-ZONES] Processed subset:\n{subset}")

        # Calculate total sum and check if valid data exists
        total = subset.sum().sum()

        if total <= 0:
            debug(context, f"[DEBUG-ZONES] ⚠ No valid {label} data — total=0")
            return {}

        # Calculate and return distribution
        dist = (subset.sum() / total * 100).round(1).to_dict()

        # Debug output for the result
        debug(context, f"[DEBUG-ZONES] ✅ {label} zones computed → {dist}")
        return dist

    debug(
        context,
        f"[ZONE-DEBUG] df_master columns (sample {min(10, len(df_master.columns))}/{len(df_master.columns)}): "
        f"{list(df_master.columns)[:10]}"
    )
    debug(context, f"[ZONE-DEBUG] Power cols detected → {power_cols}")

    # --- Compute all three ---
    context["zone_dist_power"] = compute(power_cols, "power")
    context["zone_dist_hr"]    = compute(hr_cols, "hr")
    context["zone_dist_pace"]  = compute(pace_cols, "pace")
    context["zone_dist_swim"] = compute(swim_cols, "swim")

    # --- 🩵 HR Zone Fallback from average_heartrate ---
    if (not context.get("zone_dist_hr")) and "average_heartrate" in df_master.columns:
        hr_zones = context.get("icu_hr_zones") or context.get("athlete_hr_zones") or []
        if hr_zones:
            try:
                import pandas as pd
                df_hr = df_master.copy()
                df_hr["average_heartrate"] = pd.to_numeric(df_hr["average_heartrate"], errors="coerce")
                df_hr = df_hr.dropna(subset=["average_heartrate"])
                if not df_hr.empty:
                    bins = [0] + hr_zones + [float("inf")]
                    labels = [f"hr_z{i+1}" for i in range(len(bins)-1)]
                    dist = (
                        pd.cut(df_hr["average_heartrate"], bins=bins, labels=labels)
                        .value_counts(normalize=True)
                        .mul(100)
                        .round(1)
                        .to_dict()
                    )
                    context["zone_dist_hr"] = dist
                    debug(context, f"[ZONES-FALLBACK] Built HR zone distribution from average_heartrate → {dist}")
            except Exception as e:
                debug(context, f"[ZONES-FALLBACK] ⚠ Failed HR zone fallback: {e}")

    # --- Fallback to athlete profile if truly no zone data ---
    has_zone_cols = any([power_cols, hr_cols, pace_cols])
    has_valid_data = any([
        bool(context["zone_dist_power"]),
        bool(context["zone_dist_hr"]),
        bool(context["zone_dist_pace"]),
    ])

    if has_zone_cols and not has_valid_data:
        debug(context, "⚠️ Zone columns detected but compute() returned empty — keeping raw context to avoid data loss.")
    else:
        if not has_valid_data:
            debug(context, "⚠️ No zone columns found — falling back to athlete_profile.")
            prof = athlete_profile or context.get("athlete_profile", {}) or {}
            context["zone_dist_power"] = prof.get("power_zones", {})
            context["zone_dist_hr"] = prof.get("hr_zones", {})
            context["zone_dist_pace"] = prof.get("pace_zones", {})

    # --- Canonical packaging ---
    context["zones"] = {
        "power": dict(context.get("zone_dist_power") or {}),
        "hr":    dict(context.get("zone_dist_hr") or {}),
        "pace":  dict(context.get("zone_dist_pace") or {}),
    }
    # Rename Z8 → Sweet Spot for clarity (non-destructive)
    if "power_z8" in context["zone_dist_power"]:
        val = context["zone_dist_power"].pop("power_z8")
        context["zone_dist_power"]["power_sweetspot"] = val
        context["zones"]["power"]["power_sweetspot"] = val
        debug(context, f"[DEBUG-ZONES] 🩵 Renamed power_z8 → power_sweetspot ({val}%)")

    debug(
        context,
        f"[DEBUG-ZONES] Final packaged zones → "
        f"power={len(context['zones']['power'])}, "
        f"hr={len(context['zones']['hr'])}, "
        f"pace={len(context['zones']['pace'])}"
    )    # ✅ Extract from athlete profile (multi-sport aware)
    athlete = context.get("athlete_raw", {}) or context.get("athlete", {})
    sport_settings = athlete.get("sportSettings", [])

    context["icu_zones"] = {}  # unified multi-sport container

    if sport_settings:
        for sport in sport_settings:
            # --- Normalize sport identification ---
            sport_name = str(sport.get("sport") or sport.get("name") or "").strip().lower()
            sport_types = [t.lower() for t in sport.get("types", []) if isinstance(t, str)]
            type_set = set(sport_types + [sport_name])

            if any(t in type_set for t in ["ride", "virtualride", "gravelride"]):
                sport_key = "ride"
            elif any(t in type_set for t in ["run", "trailrun", "virtualrun"]):
                sport_key = "run"
            elif any(t in type_set for t in ["swim", "openwaterswim"]):
                sport_key = "swim"
            else:
                sport_key = "other"

            # --- Extract zone sets ---
            sport_entry = {}
            if "power_zones" in sport and isinstance(sport["power_zones"], list):
                sport_entry["power"] = sport["power_zones"]
            if "hr_zones" in sport and isinstance(sport["hr_zones"], list):
                sport_entry["hr"] = sport["hr_zones"]
            if "pace_zones" in sport and isinstance(sport["pace_zones"], list):
                sport_entry["pace"] = sport["pace_zones"]
            if "paceZones" in sport and isinstance(sport["paceZones"], list):
                sport_entry["pace"] = sport["paceZones"]

            if sport_entry:
                context["icu_zones"][sport_key] = sport_entry
                debug(context, f"[ZONE-CONTEXT] Added zones for {sport_key} → {sport_entry}")

        # --- Backward compatibility for single-sport context ---
        report_type = (context.get("report_sport") or "ride").lower()
        fallback_sport = "run" if report_type == "run" else "ride"
        active_zones = (
            context["icu_zones"].get(report_type)
            or context["icu_zones"].get(fallback_sport)
            or {}
        )

        context["icu_power_zones"] = active_zones.get("power", [])
        context["icu_hr_zones"] = active_zones.get("hr", [])
        context["icu_pace_zones"] = active_zones.get("pace", [])

    else:
        debug(context, "[ZONE-CONTEXT] ⚠️ No sportSettings found in athlete profile.")

    # ✅ Extract from athlete profile (multi-sport aware)
    athlete = context.get("athlete_raw", {}) or context.get("athlete", {})
    sport_settings = athlete.get("sportSettings", [])

    context["icu_zones"] = {}  # new multi-sport container

    if sport_settings:
        for sport in sport_settings:
            types = [t.lower() for t in sport.get("types", [])]
            sport_key = "ride" if any(t in types for t in ["ride", "virtualride"]) else \
                        "run" if any(t in types for t in ["run", "virtualrun", "trailrun"]) else \
                        "swim" if any(t in types for t in ["swim", "openwaterswim"]) else \
                        "other"

            sport_entry = {}

            if "power_zones" in sport and isinstance(sport["power_zones"], list):
                sport_entry["power"] = sport["power_zones"]
            if "hr_zones" in sport and isinstance(sport["hr_zones"], list):
                sport_entry["hr"] = sport["hr_zones"]
            if "pace_zones" in sport and isinstance(sport["pace_zones"], list):
                sport_entry["pace"] = sport["pace_zones"]
            if "paceZones" in sport and isinstance(sport["paceZones"], list):
                sport_entry["pace"] = sport["paceZones"]

            if sport_entry:
                context["icu_zones"][sport_key] = sport_entry
                debug(context, f"[ZONE-CONTEXT] Added zones for {sport_key} → {sport_entry}")

        # --- Backward compatibility for flat context fields
        # Pick dominant sport type for current report
        report_type = (context.get("report_sport") or "ride").lower()
        fallback_sport = "run" if report_type == "run" else "ride"
        active_zones = context["icu_zones"].get(report_type) or context["icu_zones"].get(fallback_sport) or {}

        context["icu_power_zones"] = active_zones.get("power", [])
        context["icu_hr_zones"] = active_zones.get("hr", [])
        context["icu_pace_zones"] = active_zones.get("pace", [])

    else:
        debug(context, "[ZONE-CONTEXT] ⚠️ No sportSettings found in athlete profile.")


    # --- 🧹 Context-aware cleanup of raw nested zone columns ---
    import os

    is_railway = os.environ.get("RAILWAY_ENVIRONMENT", "").lower() in ("production", "staging")
    if is_railway:
        for col in ["icu_power_zones", "icu_zone_times", "icu_hr_zone_times", "pace_zone_times"]:
            if col in df_master.columns:
                df_master.drop(columns=[col], inplace=True, errors="ignore")
                debug(context, f"[T1-ZONES] Dropped raw nested zone column (Railway): {col}")
    else:
        debug(context, "[T1-ZONES] Local mode — keeping raw nested zone columns for expansion.")

    debug(context, f"[ZONE-FINAL] icu_power_zones={context.get('icu_power_zones')}")
    debug(context, f"[ZONE-FINAL] icu_hr_zones={context.get('icu_hr_zones')}")
    debug(context, f"[ZONE-FINAL] power_dist={context.get('zone_dist_power')}")
    debug(context, f"[ZONE-FINAL] hr_dist={context.get('zone_dist_hr')}")

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
    debug(context, f"[DEBUG-T1-COLUMNS] sample type={type(df_master)} content={str(list(df_master.columns))[:100]}")

    # --- Step 1: Dataset integrity ---
    if df_master.empty:
        raise ValueError("❌ No activity data received")

    # --- Tier-1 defensive normalization (athlete-safe) ---
    if "moving_time" not in df_master.columns:
        debug(context, "[T1-FIX] moving_time missing → injecting zeros")
        df_master["moving_time"] = 0

    if "icu_training_load" not in df_master.columns:
        debug(context, "[T1-FIX] icu_training_load missing → injecting zeros")
        df_master["icu_training_load"] = 0

    if "distance" not in df_master.columns:
        df_master["distance"] = 0

    # Drop invalid zero-duration rows *after* normalization
    df_master = df_master[df_master["moving_time"] > 0]

    if df_master.empty:
        raise AuditHalt("❌ Tier-1: no valid activities after moving_time normalization")

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
        warn_msg = (
            "⚠️ Tier-1 detected missing or zero canonical totals.\n"
            "This often occurs if recent activities have no Training Load (TSS) or HR zone data.\n"
            "If you're using a smartwatch such as Amazfit that only records HR, "
            "Intervals.icu may not compute load metrics.\n\n"
            "👉 Please check:\n"
            " • At least one activity in the past 7 days has valid TSS or HR-based load\n"
            " • Your FTP and HR zones are set in Intervals.icu → Athlete → Settings → Zones\n"
            " • Try ‘Re-analyze’ or ‘Estimate load from HR’ on recent activities\n\n"
            "Then re-run the report."
        )
        context["tier1_warning"] = warn_msg

        # Instead of halting, produce a minimal fallback report
        context["tier1_visibleTotals"] = {"hours": 0, "tss": 0, "km": 0}
        context["df_events"] = df_master.head(0)  # empty dataframe
        log.warn(warn_msg)

        # Return gracefully — don't raise AuditHalt
        return {
            "status": "warning",
            "message": "Tier-1 skipped due to incomplete training load data",
            "details": warn_msg,
            "semantic_graph": {},
            "logs": "\n".join(context.get("logs", [])) if "logs" in context else "",
        }

    # Continue if totals are valid
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

        # ------------------------------------------------------------
        # ✅ Ensure daily_load & df_daily are bound even in prefetch mode
        # ------------------------------------------------------------
        if "daily_load" not in context or not context["daily_load"]:
            try:
                df_daily = daily_load.reset_index()
                df_daily.columns = ["date", "icu_training_load"]
                context["df_daily"] = df_daily

                context["daily_load"] = [
                    {"date": str(d.date()), "tss": float(t)} for d, t in daily_load.items()
                ]

                debug(
                    context,
                    f"[T1-REST] Exported daily_load into context ({len(context['daily_load'])} days)"
                )
            except Exception as e:
                debug(context, f"[T1-REST] ⚠️ Failed to bind daily_load in prefetch mode: {e}")


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

        # --- 🩵 HRV summary (vendor-agnostic, uses Tier-2 derived metrics normalization) ---
        if "df_wellness" in context and not context["df_wellness"].empty:
            dfw = context["df_wellness"]
            if "hrv" in dfw.columns:
                vals = pd.to_numeric(dfw["hrv"], errors="coerce").dropna()
                if len(vals) > 0:
                    context["hrv_mean"] = round(vals.mean(), 1)
                    context["hrv_latest"] = round(vals.iloc[-1], 1)
                    context["hrv_trend_7d"] = (
                        round(vals.tail(7).mean() - vals.head(7).mean(), 1)
                        if len(vals) >= 14 else None
                    )
                    debug(
                        context,
                        f"[T1] HRV summary → mean={context['hrv_mean']}, "
                        f"latest={context['hrv_latest']}, trend_7d={context['hrv_trend_7d']}, "
                        f"source={context.get('hrv_source', 'unknown')}"
                    )
                else:
                    context["hrv_mean"] = context["hrv_latest"] = context["hrv_trend_7d"] = None
            else:
                context["hrv_mean"] = context["hrv_latest"] = context["hrv_trend_7d"] = None

        daily_summary = df_well.copy()
        context["df_wellness"] = df_well
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
    debug(context, f"[DEBUG-T1] Sanity check before Step 6b — rows in df_master: {len(df_master)}")

    # Ensure athlete profile is available
    athleteProfile = context.get("athleteProfile", {}) or {}

    try:
        debug(context, "[DEBUG-T1] Starting zone distribution extraction...")

        report_type = str(context.get("report_type", "")).lower()
        zone_df = df_master
        scope = "7d"

        # Check if context has 'df_light' for the season mode and use it
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
        debug(
            context,
            f"[ZONES-RAW] Columns before zone dist (sample {min(10, len(df_master.columns))}/{len(df_master.columns)}): "
            f"{list(df_master.columns)[:10]}"
        )
        
        # Log some sample values from critical columns to verify data
        if 'icu_power_zones' in df_master.columns:
            debug(context, f"[ZONES-RAW] icu_power_zones sample: {df_master['icu_power_zones'].head(13).tolist()}")
        else:
            debug(context, "[ZONES-RAW] 'icu_power_zones' column not found in df_master.")
            
        if 'icu_zone_times' in df_master.columns:
            debug(context, f"[ZONES-RAW] icu_zone_times sample: {df_master['icu_zone_times'].head(13).tolist()}")
        else:
            debug(context, "[ZONES-RAW] 'icu_zone_times' column not found in df_master.")
        
        # Sanity check for missing or NaN values in critical columns
        missing_icu_power_zones = df_master['icu_power_zones'].isnull().sum() if 'icu_power_zones' in df_master.columns else 0
        missing_icu_zone_times = df_master['icu_zone_times'].isnull().sum() if 'icu_zone_times' in df_master.columns else 0
        debug(context, f"[DEBUG-T1] Missing values: icu_power_zones: {missing_icu_power_zones}, icu_zone_times: {missing_icu_zone_times}")
        
        # Check if columns have at least some data
        debug(context, f"[DEBUG-T1] First few rows of icu_power_zones: {df_master['icu_power_zones'].head() if 'icu_power_zones' in df_master.columns else 'n/a'}")
        debug(context, f"[DEBUG-T1] First few rows of icu_zone_times: {df_master['icu_zone_times'].head() if 'icu_zone_times' in df_master.columns else 'n/a'}")
       
        # For df_master['icu_power_zones'], replace NaN or None with 0.0, but log the changes for visibility
        if 'icu_power_zones' in df_master.columns:
            missing_power_zones = df_master['icu_power_zones'].isnull().sum()
            debug(context, f"[DEBUG-T1] Missing values in icu_power_zones: {missing_power_zones}")
            
            df_master['icu_power_zones'] = df_master['icu_power_zones'].fillna(0.0)
            debug(context, f"[DEBUG-T1] After fillna, icu_power_zones sample: {df_master['icu_power_zones'].head()}")

        # For icu_zone_times, process the list of dictionaries, replacing None values with 0.0, and logging transformations
        def process_zone_times(zone_times):
            if isinstance(zone_times, list):
                # Process the list of dictionaries and replace None values inside the dictionaries with 0.0
                transformed = [{k: (0.0 if v is None else v) for k, v in zone.items()} for zone in zone_times]
                debug(context, f"[DEBUG-ZONES] Transformed icu_zone_times: {transformed}")
                return transformed
            return zone_times  # Return the value as is if it's not a list

        if 'icu_zone_times' in df_master.columns:
            missing_zone_times = df_master['icu_zone_times'].isnull().sum()
            debug(context, f"[DEBUG-T1] Missing values in icu_zone_times: {missing_zone_times}")
            
            df_master['icu_zone_times'] = df_master['icu_zone_times'].apply(process_zone_times)
            debug(context, f"[DEBUG-T1] After processing, icu_zone_times sample: {df_master['icu_zone_times'].head()}")

        # Initialize tmp dictionary to store the results
        tmp = {}

        # Proceed to compute zone distributions
        tmp = collect_zone_distributions(zone_df, athleteProfile, tmp)

        # Final logging for results
        context["zone_dist_power"] = tmp.get("zone_dist_power") or {}
        context["zone_dist_hr"] = tmp.get("zone_dist_hr") or {}
        context["zone_dist_pace"] = tmp.get("zone_dist_pace") or {}

        # 🧭 Scoped copies for debugging / UI
        context[f"zone_dist_power_{scope}"] = context["zone_dist_power"]
        context[f"zone_dist_hr_{scope}"] = context["zone_dist_hr"]
        context[f"zone_dist_pace_{scope}"] = context["zone_dist_pace"]
        context["zone_scope"] = scope

        debug(context, f"[T1-ZONE] Completed zone dist extraction (scope={scope})")
        debug(context, f"  power: {context['zone_dist_power']}")
        debug(context, f"  hr:    {context['zone_dist_hr']}")

    except Exception as e:
        debug(context, f"[ERROR] Exception while computing zone distributions: {str(e)}")

        # Handle the case where tmp was never initialized or failed in processing
        context["zone_dist_power"] = {}
        context["zone_dist_hr"] = {}
        context["zone_dist_pace"] = {}
        context["zone_scope"] = "none"

        # 🧭 Scoped copies for debugging / UI
        context[f"zone_dist_power_{scope}"] = context["zone_dist_power"]
        context[f"zone_dist_hr_{scope}"] = context["zone_dist_hr"]
        context[f"zone_dist_pace_{scope}"] = context["zone_dist_pace"]
        context["zone_scope"] = scope

        debug(context, f"[T1-ZONE] Completed zone dist extraction (scope={scope})")
        debug(context, f"  power: {context['zone_dist_power']}")
        debug(context, f"  hr:    {context['zone_dist_hr']}")


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


    # --- Step 7: Qualitative label translation ----
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