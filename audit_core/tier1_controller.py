
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
from coaching_cheat_sheet import CHEAT_SHEET
from audit_core.utils import set_time_context

# ======================================================
# 🧩 SPORT GROUP RESOLUTION (CHEAT_SHEET AUTHORITATIVE)
# ======================================================

SPORT_GROUPS = CHEAT_SHEET.get("sport_groups", {})

def resolve_sport_group(activity_type: str):
    """
    Return canonical sport group name for an activity type
    using CHEAT_SHEET sport_groups.
    """
    if not activity_type:
        return None

    t = str(activity_type).strip()
    for group, members in SPORT_GROUPS.items():
        if t in members:
            return group
    return None

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

        # --- 🩵 Expand icu_hr_zone_times if present ---
        if "hr_z1" not in df_master.columns and "icu_hr_zone_times" in df_master.columns:
            debug(context, "[DEBUG-ZONES] Found icu_hr_zone_times — attempting to expand.")
            import pandas as pd, numpy as np, json, ast

            def safe_parse_hr(x):
                if isinstance(x, list):
                    return x
                if isinstance(x, str):
                    s = x.strip()
                    if s.startswith("[") and s.endswith("]"):
                        for parser in (json.loads, ast.literal_eval):
                            try:
                                val = parser(s)
                                if isinstance(val, list):
                                    return val
                            except Exception:
                                continue
                return []

            parsed = df_master["icu_hr_zone_times"].dropna().apply(safe_parse_hr)
            parsed = parsed.dropna()

            if not parsed.empty:
                sample = parsed.iloc[0]
                debug(context, f"[DEBUG-ZONES] HR sample type={type(sample)} content={str(sample)[:1000]}")

                # ✅ CASE 1: List of dicts — Intervals-style [{'secs':123}, ...]
                if isinstance(sample, list) and all(isinstance(z, dict) for z in sample):
                    def expand_hr_row(zlist):
                        row = {}
                        for i, z in enumerate(zlist, start=1):
                            row[f"hr_z{i}"] = float(z.get("secs", 0))
                        return row

                    expanded = df_master["icu_hr_zone_times"].apply(expand_hr_row)
                    hr_df = pd.DataFrame(list(expanded)).fillna(0)
                    hr_df.reset_index(drop=True, inplace=True)
                    df_master.reset_index(drop=True, inplace=True)
                    df_master = pd.concat([df_master, hr_df], axis=1)

                    debug(context, f"[DEBUG-ZONES] ✅ Expanded icu_hr_zone_times → {len(hr_df.columns)} HR cols")
                    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                        debug(context, f"[DEBUG-ZONES] FULL HR dataset:\n{df_master[[c for c in hr_df.columns]].to_string(index=True)}")

                # ✅ CASE 2: List of numbers — simplified Intervals HR array
                elif isinstance(sample, list) and all(isinstance(z, (int, float)) for z in sample):
                    cols = [f"hr_z{i+1}" for i in range(len(sample))]
                    hr_df = pd.DataFrame(parsed.tolist(), columns=cols).fillna(0)
                    df_master = pd.concat([df_master.reset_index(drop=True), hr_df.reset_index(drop=True)], axis=1)
                    debug(context, f"[DEBUG-ZONES] ✅ Expanded numeric icu_hr_zone_times → {len(cols)} HR cols")

                else:
                    debug(context, f"[DEBUG-ZONES] ⚠️ Unrecognized HR zone structure: {type(sample)}")

            else:
                debug(context, "[DEBUG-ZONES] ⚠️ No HR data found to expand.")

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

    # ======================================================
    # 🧩 Sensor Exclusivity Enforcement (FUSION ONLY)
    # Preserve raw HR for reporting
    # ======================================================
    try:
        pcols = [c for c in df_master.columns if c.startswith("power_z")]
        hcols = [c for c in df_master.columns if c.startswith("hr_z")]

        # Create fused copies ONCE
        for c in pcols + hcols:
            fused_col = f"_fused_{c}"
            if fused_col not in df_master.columns:
                df_master[fused_col] = df_master[c]

        for idx, row in df_master.iterrows():
            has_power = pcols and pd.to_numeric(row[pcols], errors="coerce").fillna(0).sum() > 0
            has_hr = hcols and pd.to_numeric(row[hcols], errors="coerce").fillna(0).sum() > 0

            # Apply exclusivity ONLY to fused columns
            if has_power:
                for h in hcols:
                    df_master.at[idx, f"_fused_{h}"] = 0.0
            elif has_hr:
                for p in pcols:
                    df_master.at[idx, f"_fused_{p}"] = 0.0
            else:
                for c in pcols + hcols:
                    df_master.at[idx, f"_fused_{c}"] = 0.0

        debug(context, "[ZONES-FIX] ✅ Sensor exclusivity applied to fused columns only")

    except Exception as e:
        import traceback
        debug(context, f"[ZONES-FIX] ❌ Fusion exclusivity failed: {e}\n{traceback.format_exc()}")


    # --- 🧮 Compute zone distributions ---
    def compute(df, cols, label):
        if not cols:
            debug(context, f"[DEBUG-ZONES] ❌ No {label} columns found — skipping.")
            return {}

        # 🩹 Remove non-zone config keys (e.g., icu_hr_zones, thresholds)
        cols = [c for c in cols if re.match(r'.*_z\d+$', c)]

        # Function to extract seconds from zones, handling missing or None data
        def extract_secs(value):
            """
            Extract seconds from Intervals zone structures, handling both:
            - List of dicts (local JSON shape)
            - Flat numeric lists (Railway JSON shape)
            Includes detailed debug output for data visualization and auditing.
            """
            try:
                if isinstance(value, list):
                    preview = value[:5] if len(value) > 5 else value
                    debug(
                        context,
                        f"[DEBUG-ZONES] extract_secs() input type="
                        f"{type(value[0]) if value else None}, sample={preview}"
                    )

                    if len(value) > 0 and isinstance(value[0], dict) and "secs" in value[0]:
                        total = sum(int(entry.get("secs", 0)) for entry in value)
                        debug(context, f"[DEBUG-ZONES] ✅ Parsed dict-style zones → total_secs={total}")
                        return total

                    elif all(isinstance(x, (int, float)) for x in value):
                        total = sum(value)
                        debug(context, f"[DEBUG-ZONES] ✅ Parsed numeric-style zones → total_secs={total}")
                        return total

                    else:
                        debug(context, f"[DEBUG-ZONES] ⚠️ Unexpected zone entry shape: {preview}")
                        return 0

                elif isinstance(value, (int, float)):
                    return float(value)

                else:
                    debug(context, f"[DEBUG-ZONES] ⚠️ Non-list, non-numeric input={value}")
                    return 0

            except Exception as e:
                debug(context, f"[DEBUG-ZONES] ⚠️ extract_secs() exception: {e}")
                return 0

        # ✅ THE FIX: USE df, NOT df_master
        subset = (
            df[cols]
            .apply(lambda col: col.map(extract_secs))  # ✅ pandas 2.x safe
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0)
        )

        # Debugging full table for raw data and subset
        with pd.option_context("display.max_rows", None, "display.max_columns", None):
            raw_data = df[cols].to_string(index=False)

        debug(context, f"[DEBUG-ZONES] FULL {label} dataset:\n{raw_data}")
        debug(context, f"[DEBUG-ZONES] Processed subset:\n{subset}")

        total = subset.sum().sum()

        if total <= 0:
            debug(context, f"[DEBUG-ZONES] ⚠ No valid {label} data — total=0")
            return {}

        dist = (subset.sum() / total * 100).round(1).to_dict()

        debug(context, f"[DEBUG-ZONES] ✅ {label} zones computed → {dist}")
        return dist

    debug(
        context,
        f"[ZONE-DEBUG] df_master columns (sample {min(10, len(df_master.columns))}/{len(df_master.columns)}): "
        f"{list(df_master.columns)[:10]}"
    )
    debug(context, f"[ZONE-DEBUG] Power cols detected → {power_cols}")

    # ======================================================
    # 🩺 HR ZONES — CHEAT_SHEET SPORT-AWARE FILTER
    # ======================================================

    df_hr_scope = df_master.copy()

    if "type" in df_master.columns:
        df_hr_scope["sport_group"] = df_hr_scope["type"].apply(resolve_sport_group)

        # HR zones are only physiologically comparable for cycling
        df_hr_scope = df_hr_scope[df_hr_scope["sport_group"] == "Ride"]

        debug(
            context,
            f"[ZONES-HR] HR zones restricted to CHEAT_SHEET Ride group → "
            f"{sorted(df_hr_scope['type'].unique().tolist())}"
        )


    context["zone_dist_power"] = compute(df_master, power_cols, "power")

    context["zone_dist_hr"] = compute(
        df_hr_scope,
        [c for c in hr_cols if c in df_hr_scope.columns],
        "hr"
    )

    context["zone_dist_pace"] = compute(df_master, pace_cols, "pace")
    context["zone_dist_swim"] = compute(df_master, swim_cols, "swim")


    # --- ✅ Normalize zone keys for Tier-2 fusion parity ---
    import re

    def strip_prefix_keys(dist):
        """Remove power_/hr_ prefixes so Tier-2 fusion can align keys."""
        if not isinstance(dist, dict):
            return dist
        return {re.sub(r'^(power_|hr_)', '', k): v for k, v in dist.items()}

    context["zone_dist_power"] = strip_prefix_keys(context.get("zone_dist_power", {}))
    context["zone_dist_hr"]    = strip_prefix_keys(context.get("zone_dist_hr", {}))


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
    )
    
    # ---------------------------------------------------------
    # ✅ Extract zones from athlete profile (multi-sport safe)
    # ---------------------------------------------------------

    athlete = context.get("athlete") or context.get("athlete_raw") or {}

    sport_settings = athlete.get("sportSettings", [])
    debug(context, f"[ZONE-CONTEXT] sportSettings count → {len(sport_settings)}")

    context["icu_zones"] = {}

    if sport_settings:
        # ----------------------------
        # Build zone map per sport
        # ----------------------------
        for sport in sport_settings:

            raw_sport = (
                sport.get("sport")
                or sport.get("name")
                or (sport.get("types") or [None])[0]
            )

            sport_key = resolve_sport_group(raw_sport)

            if not sport_key:
                continue

            sport_key = str(sport_key).lower()

            entry = {}

            if isinstance(sport.get("power_zones"), list):
                entry["power"] = sport["power_zones"]

            if isinstance(sport.get("hr_zones"), list):
                entry["hr"] = sport["hr_zones"]

            if isinstance(sport.get("pace_zones"), list):
                entry["pace"] = sport["pace_zones"]

            if isinstance(sport.get("paceZones"), list):
                entry["pace"] = sport["paceZones"]

            if entry:
                existing = context["icu_zones"].get(sport_key, {})
                existing.update(entry)
                context["icu_zones"][sport_key] = existing
                debug(context, f"[ZONE-CONTEXT] Added zones for {sport_key}")

        # ----------------------------
        # Resolve active sport
        # ----------------------------
        raw_report_sport = context.get("report_sport") or "ride"
        report_type = resolve_sport_group(raw_report_sport) or raw_report_sport
        report_type = str(report_type).lower()

        debug(context, f"[ZONE-FINAL] available keys → {list(context['icu_zones'].keys())}")
        debug(context, f"[ZONE-FINAL] report_type → {report_type}")

        active_zones = (
            context["icu_zones"].get(report_type)
            or context["icu_zones"].get("ride")
            or context["icu_zones"].get("run")
            or {}
        )

        context["icu_power_zones"] = active_zones.get("power", [])
        context["icu_hr_zones"] = active_zones.get("hr", [])
        context["icu_pace_zones"] = active_zones.get("pace", [])

    else:
        debug(context, "[ZONE-CONTEXT] ⚠️ No sportSettings found in athlete profile.")
        context["icu_power_zones"] = []
        context["icu_hr_zones"] = []
        context["icu_pace_zones"] = []

    # --- Ensure Tier-2 sees flat zone_dist_* dicts ---
    zones = context.get("zones", {})

    if "zone_dist_power" not in context:
        context["zone_dist_power"] = zones.get("power", {}).get("distribution", {})
    if "zone_dist_hr" not in context:
        context["zone_dist_hr"] = zones.get("hr", {}).get("distribution", {})

    # --- Enforce numeric and strip prefixes (idempotent) ---
    import re
    def strip_prefix_keys(d):
        return {re.sub(r'^(power_|hr_)', '', k): float(v) for k, v in d.items() if v is not None}

    context["zone_dist_power"] = strip_prefix_keys(context["zone_dist_power"])
    context["zone_dist_hr"]    = strip_prefix_keys(context["zone_dist_hr"])

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
    context = set_time_context(context)
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

    # --- 🔧 SNAPSHOT SCHEMA FALLBACK (controlled degradation) ---
    REQUIRED_EVENT_FIELDS = ["type", "moving_time", "icu_training_load"]

    missing = [c for c in REQUIRED_EVENT_FIELDS if c not in visible_events.columns]

    if missing:
        debug(
            context,
            f"[T1-SNAPSHOT-FIX] Injecting missing fields → {missing} "
            f"(cols={list(visible_events.columns)})"
        )

        for col in missing:
            if col == "type":
                visible_events[col] = "Unknown"
            elif col in ("moving_time", "icu_training_load"):
                visible_events[col] = 0.0

    # Validate schema before continuing
    #if not isinstance(visible_events, pd.DataFrame) or "type" not in visible_events.columns:
    #    raise AuditHalt(
    #        f"❌ Tier-1: snapshot_7d_json missing required 'type' column "
    #        f"(columns={visible_events.columns.tolist() if hasattr(visible_events, 'columns') else 'N/A'})"
    #    )

    # Ensure numeric for mean computations
    for col in ["icu_intensity", "average_heartrate", "VO2MaxGarmin"]:
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
        f"icu_intensity={t0.get('avg_if')} HR={t0.get('avg_hr')} VO₂={t0.get('vo2max')}"
    )

    # --- Cycling-only refinement for mean metrics ---
    cycling_subset = visible_events.copy()
    cycling_subset["sport_group"] = cycling_subset["type"].apply(resolve_sport_group)
    cycling_subset = cycling_subset[cycling_subset["sport_group"] == "Ride"]
    if not cycling_subset.empty:
        context["tier1_visibleTotals"].update({
            "avg_if": round(cycling_subset["icu_intensity"].mean(), 2)
            if "icu_intensity" in cycling_subset.columns else 0,
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

    if report_type == "weekly":

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

    report_type = str(context.get("report_type", "")).lower()

    # 🔒 Weekly canonical 7-day totals
    if report_type == "weekly":

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
            debug(context, f"[T1-WARN] {warn_msg}")

            raise AuditHalt("🚫 Audit Halt: Missing or Zero Canonical Totals")

    # ✅ Summary does NOT gate on 7-day totals


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
    # --- Step 4.5: Wellness kept separate (no merge into df_master) ---
    if isinstance(wellness, pd.DataFrame) and not wellness.empty:
        debug(context, "[T1] Wellness dataset detected — kept separate from activities.")
    else:
        debug(context, "[T1] No valid wellness dataset available.")
    # ======================================================================
    # 🌿 WELLNESS METRICS (42-day context enrichment for insights builder)
    # ======================================================================
    try:
        import pandas as pd, numpy as np

        # Accept multiple input formats
        if isinstance(wellness, pd.DataFrame):
            dfw = wellness.copy()
        elif isinstance(wellness, list):
            dfw = pd.DataFrame(wellness)
        elif isinstance(wellness, dict) and "series" in wellness:
            dfw = pd.DataFrame(wellness["series"])
        else:
            dfw = None

        # --------------------------------------------------------------
        # 🩵 Resting HR Delta (7d vs 28d)
        # --------------------------------------------------------------
        if dfw is not None and "restingHR" in dfw.columns:
            dfw["restingHR"] = pd.to_numeric(dfw["restingHR"], errors="coerce")
            dfw = dfw.dropna(subset=["restingHR"])
            if "date" in dfw.columns:
                dfw = dfw.sort_values("date")
            elif "id" in dfw.columns:
                dfw = dfw.sort_values("id")

            if len(dfw) >= 14:
                recent_7d = dfw.tail(7)["restingHR"].mean()
                baseline_28d = dfw.tail(28)["restingHR"].mean()
                resting_hr_delta = round(recent_7d - baseline_28d, 1)

                context.setdefault("wellness", {})
                context["wellness"]["resting_hr_delta"] = resting_hr_delta
                context["wellness"]["rest_hr"] = float(dfw["restingHR"].iloc[-1])

                debug(
                    context,
                    f"[T1-WELLNESS] ✅ Derived resting_hr_delta={resting_hr_delta} "
                    f"(7d={recent_7d:.1f}, 28d={baseline_28d:.1f})"
                )

        # --------------------------------------------------------------
        # 💓 HRV Metrics Normalization
        # --------------------------------------------------------------
        hrv_mean = None
        hrv_latest = None
        hrv_series = []

        if isinstance(wellness, dict):
            hrv_mean = wellness.get("hrv_mean") or wellness.get("HRV_mean")
            hrv_latest = wellness.get("hrv_latest") or wellness.get("HRV_latest")
            hrv_series = wellness.get("hrv_series", [])

        elif dfw is not None and "hrv" in dfw.columns:
            hrv_series = dfw[["date", "hrv"]].to_dict(orient="records")
            hrv_latest = float(dfw["hrv"].iloc[-1])
            hrv_mean = float(dfw["hrv"].mean())

        if (
            hrv_mean is not None
            and hrv_latest is not None
            and pd.notna(hrv_mean)
            and pd.notna(hrv_latest)
            and float(hrv_mean) > 0
        ):
            hrv_mean = float(hrv_mean)
            hrv_latest = float(hrv_latest)

            hrv_ratio = round(hrv_latest / hrv_mean, 2)

            context.setdefault("wellness_summary", {})["hrv_ratio"] = hrv_ratio
            debug(context, f"[T1-WELLNESS] HRV ratio computed → {hrv_ratio:.2f}")

    except Exception as e:
        debug(context, f"[T1-WELLNESS] ⚠️ Wellness processing failed: {e}")


    # --- Step 5: Wellness alignment check ---
    if wellness is None or (isinstance(wellness, pd.DataFrame) and wellness.empty):
        debug(context,"⚠ No wellness data available for window; continuing with activity-only audit")
    else:
        validate_wellness_alignment(df_master, wellness, context)

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

        # 🔎 Remove duplicate columns caused by lowercase + rename collisions
        if df_well.columns.duplicated().any():
            debug(context, "[T1] Duplicate columns detected in df_well after normalization — removing")
            df_well = df_well.loc[:, ~df_well.columns.duplicated()]

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
        soreness_avg = round(df_well["soreness"].mean(skipna=True), 1) \
            if "soreness" in df_well.columns else np.nan
        mood_avg = round(df_well["mood"].mean(skipna=True), 1) \
            if "mood" in df_well.columns else np.nan
        motivation_avg = round(df_well["motivation"].mean(skipna=True), 1) \
            if "motivation" in df_well.columns else np.nan
        hydration_avg = round(df_well["hydration"].mean(skipna=True), 1) \
            if "hydration" in df_well.columns else np.nan
        injury_avg = round(df_well["injury"].mean(skipna=True), 1) \
            if "injury" in df_well.columns else np.nan

        # --- Objective + subjective rest-day logic ---
        today = context["athlete_today"]
        mask_past = df_well["date"] < today

        load_col = None
        for candidate in ["load", "icu_training_load", "atl", "ctl"]:
            if candidate in df_well.columns:
                load_col = candidate
                break

        # --- Determine rest days based on *no training load* days before today ---
        debug(context, "[T1-REST] Starting rest day calculation from df_master.")

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
        today = context["athlete_today"]
        report_type = context.get("report_type")

        if report_type == "weekly":
            window_days = 6
            rest_df = df_master.copy()

        elif report_type == "wellness":
            window_days = 41
            rest_df = context.get("df_light", df_master).copy()

        elif report_type == "season":
            window_days = 89
            rest_df = context.get("df_light", df_master).copy()

        elif report_type == "summary":
            rest_df = context.get("df_light", df_master).copy()

        else:
            window_days = 6
            rest_df = df_master.copy()

        # ------------------------------------------------------------
        # ✅ NORMALIZE DATES FIRST (fixes your error)
        # ------------------------------------------------------------
        rest_df["date"] = (
            pd.to_datetime(rest_df["start_date_local"], errors="coerce")
            .dt.tz_localize(None)
            .dt.normalize()
        )

        # ------------------------------------------------------------
        # Window logic
        # ------------------------------------------------------------
        if report_type == "summary":
            window_start = rest_df["date"].min()
        else:
            window_start = today - pd.Timedelta(days=window_days)

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
            daily_load = pd.Series(0, index=date_range)

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
        subjective_fields = [
            "fatigue",
            "stress",
            "soreness",
            "mood",
            "motivation",
            "injury",
            "hydration",
            "readiness"
        ]

        subjective_metrics = {}
        today_subjective = df_well.loc[df_well["date"].dt.date == today.date()]

        for field in subjective_fields:
            if field in today_subjective.columns:
                values = pd.to_numeric(today_subjective[field], errors="coerce").dropna()
                if not values.empty:
                    subjective_metrics[field] = round(float(values.iloc[-1]), 1)

        wellness_metrics = {
            "rest_hr": rest_hr,
            "hrv_trend": hrv_trend,
        }
        context["load_distribution"] = {
        "rest_days": rest_days
        }
        
        context["wellness_metrics"] = wellness_metrics
        context.setdefault("wellness_summary", {}).update(wellness_metrics)

        # keep subjective values but outside the wellness summary
        context["subjective_metrics"] = subjective_metrics

        debug(context, f"[T1] Wellness summary → rest_days={rest_days}, rest_hr={rest_hr}, hrv_trend={hrv_trend}")

        # --- 🩵 HRV summary (vendor-agnostic, uses Tier-2 derived metrics normalization) ---
        if "df_wellness" in context and not context["df_wellness"].empty:
            dfw = context["df_wellness"]

            if "hrv" in dfw.columns:
                vals = pd.to_numeric(dfw["hrv"], errors="coerce").dropna()

                if len(vals) > 0:
                    context["hrv_mean"] = round(vals.mean(), 1)
                    context["hrv_latest"] = round(vals.iloc[-1], 1)

                    hrv_ratio = (
                        round(float(context["hrv_latest"]) / float(context["hrv_mean"]), 2)
                        if context["hrv_mean"] not in (None, 0)
                        else None
                    )

                    if len(vals) >= 90:
                        trend = vals.tail(30).mean() - vals.head(30).mean()
                    elif len(vals) >= 28:
                        trend = vals.tail(14).mean() - vals.head(14).mean()
                    elif len(vals) >= 14:
                        trend = vals.tail(7).mean() - vals.head(7).mean()
                    else:
                        trend = None

                    context["hrv_trend_7d"] = round(trend, 1) if trend is not None else None

                    # ✅ Preserve for PI + semantic wellness
                    existing_ws = context.get("wellness_summary", {}) or {}

                    context["wellness_summary"] = {
                        **existing_ws,
                        "hrv_ratio": hrv_ratio,
                        "hrv_trend": context["hrv_trend_7d"],
                    }

                    debug(
                        context,
                        f"[T1] HRV summary → mean={context['hrv_mean']}, "
                        f"latest={context['hrv_latest']}, ratio={hrv_ratio}, "
                        f"trend_7d={context['hrv_trend_7d']}, "
                        f"source={context.get('hrv_source', 'unknown')}"
                    )

                else:
                    context["hrv_mean"] = None
                    context["hrv_latest"] = None
                    context["hrv_trend_7d"] = None

            else:
                context["hrv_mean"] = None
                context["hrv_latest"] = None
                context["hrv_trend_7d"] = None

        daily_summary = df_well.copy()
        context["df_wellness"] = df_well
    else:
        context["wellness_metrics"] = {
            "rest_hr": np.nan, "hrv_trend": np.nan,
            "rest_days": 0, "fatigue": np.nan, "stress": np.nan, "readiness": np.nan,
        }
        existing_ws = context.get("wellness_summary", {}) or {}

        context["wellness_summary"] = {
            **existing_ws,
            **context.get("wellness_metrics", {})
        }

    context["dailyMerged"] = daily_summary

    # --- Step 6a: Extract CTL / ATL / TSB from   yesterday + today's completed load ---
    """
    ## mode

    | mode | Meaning |
    |---|---|
    | `sunrise_decay` | CTL/ATL derived from overnight EWMA decay from previous day |
    | `planned_completed` | CTL/ATL sourced from completed activity linked to a planned calendar event |
    | `unplanned_completed` | CTL/ATL sourced from completed activity not linked to a planned calendar event |
    | `fallback_wellness` | CTL/ATL sourced from latest available wellness snapshot fallback |

    ## day_context

    | day_context | Meaning |
    |---|---|
    | `normal_day` | No remaining planned workouts after current state |
    | `mixed_day` | Completed activity exists AND additional planned workouts still remain |

    ## meaning

    | meaning | Meaning |
    |---|---|
    | `sunrise` | Start-of-day freshness before load |
    | `actual_sunset` | Post-completed-activity physiological state |
    | `unknown_current_state` | Fallback state with uncertain freshness/load interpretation |

    ## Example combinations

    | mode | day_context | Interpretation |
    |---|---|---|
    | `sunrise_decay` | `normal_day` | Morning freshness before training |
    | `planned_completed` | `normal_day` | Planned workout completed; no remaining workouts |
    | `planned_completed` | `mixed_day` | Planned workout completed but more planned workouts remain |
    | `unplanned_completed` | `normal_day` | Unplanned activity completed; no remaining workouts |
    | `unplanned_completed` | `mixed_day` | Unplanned activity completed while planned workouts still remain |
    """


    if isinstance(wellness, pd.DataFrame) and not wellness.empty:
        df_well = wellness.copy()
        df_well.columns = [c.strip().lower() for c in df_well.columns]

        date_col = next(
            (c for c in ("date", "day", "start_date_local", "start_date") if c in df_well.columns),
            None
        )

        if date_col:
            df_well[date_col] = pd.to_datetime(df_well[date_col], errors="coerce")
            df_well = df_well.dropna(subset=[date_col]).sort_values(date_col)
            df_well["_date"] = df_well[date_col].dt.date
        else:
            df_well["_date"] = pd.NaT

        today = pd.to_datetime(context.get("athlete_today")).date()

        # ---------------------------------------------------------
        # TRUE SUNRISE
        # yesterday sunset carried into today with decay only
        # ---------------------------------------------------------
        df_past = df_well[df_well["_date"] < today]

        if not df_past.empty:
            sunrise = df_past.iloc[-1]
        else:
            sunrise = df_well.iloc[-1]

        ctl_y = pd.to_numeric(
            sunrise.get("ctl"),
            errors="coerce"
        )

        atl_y = pd.to_numeric(
            sunrise.get("atl"),
            errors="coerce"
        )

        ctl_sunrise = None
        atl_sunrise = None
        tsb_sunrise = None

        if pd.notna(ctl_y) and pd.notna(atl_y):

            tau_ctl = 42.0
            tau_atl = 7.0

            # overnight decay only
            ctl_sunrise = float(
                ctl_y - (ctl_y / tau_ctl)
            )

            atl_sunrise = float(
                atl_y - (atl_y / tau_atl)
            )

            tsb_sunrise = (
                ctl_sunrise - atl_sunrise
            )

        # --- today's COMPLETED load only from activities ---
        today_tss = 0.0

        if isinstance(df_master, pd.DataFrame) and not df_master.empty:
            df_master = df_master.copy()
            df_master["_date"] = pd.to_datetime(
                df_master["start_date_local"], errors="coerce"
            ).dt.date

            today_tss = pd.to_numeric(
                df_master.loc[df_master["_date"] == today, "icu_training_load"],
                errors="coerce"
            ).fillna(0).sum()

        # ---------------------------------------------------------
        # Prefer authoritative CTL / ATL from latest activity today
        # ---------------------------------------------------------
        ctl_today = None
        atl_today = None
        tsb_today = None

        if isinstance(df_master, pd.DataFrame) and not df_master.empty:

            df_today = df_master.loc[df_master["_date"] == today].copy()

            if not df_today.empty:

                df_today["icu_ctl"] = pd.to_numeric(
                    df_today["icu_ctl"],
                    errors="coerce"
                )

                df_today["icu_atl"] = pd.to_numeric(
                    df_today["icu_atl"],
                    errors="coerce"
                )

                df_today = df_today.sort_values(
                    "start_date_local"
                )

                valid = df_today[
                    df_today["icu_ctl"].notna() &
                    df_today["icu_atl"].notna()
                ]

                if not valid.empty:
                    latest = valid.iloc[-1]

                    ctl_today = float(latest["icu_ctl"])
                    atl_today = float(latest["icu_atl"])
                    tsb_today = ctl_today - atl_today

        # ---------------------------------------------------------
        # No completed activity today:
        # use SUNRISE state from wellness
        # ---------------------------------------------------------
        if ctl_today is None or atl_today is None:

            if pd.notna(ctl_sunrise) and pd.notna(atl_sunrise):

                ctl_today = float(ctl_sunrise)
                atl_today = float(atl_sunrise)
                tsb_today = float(tsb_sunrise)

        context["ctl"] = round(float(ctl_today), 2) if ctl_today is not None else None
        context["atl"] = round(float(atl_today), 2) if atl_today is not None else None
        context["tsb"] = round(float(tsb_today), 2) if tsb_today is not None else None

        load_snapshot = {
            "ctl": context["ctl"],
            "atl": context["atl"],
            "tsb": context["tsb"],
        }

        existing_ws = context.get("wellness_summary", {}) or {}

        context["wellness_summary"] = {
            **existing_ws,
            **load_snapshot
        }

        context["load_metrics"] = {
            "CTL": {"value": context["ctl"], "status": "authoritative_activity"},
            "ATL": {"value": context["atl"], "status": "authoritative_activity"},
            "TSB": {"value": context["tsb"], "status": "derived"},
        }

        # ---------------------------------------------------------
        # Semantic meaning of current CTL / ATL / TSB state
        # ---------------------------------------------------------

        # ---------------------------------------------------------
        # Determine active CTL / ATL state meaning
        # ---------------------------------------------------------
        has_completed_activity = False
        activity_type = "none"

        if (
            "df_today" in locals()
            and "valid" in locals()
            and not df_today.empty
            and not valid.empty
        ):

            latest = valid.iloc[-1]

            paired_event_id = latest.get("paired_event_id")

            has_completed_activity = True

            activity_type = (
                "planned_completed"
                if pd.notna(paired_event_id)
                else "unplanned_completed"
            )

        state_mode = (
            activity_type
            if has_completed_activity
            else "sunrise_decay"
        )

        # ---------------------------------------------------------
        # Detect remaining planned workouts today
        # ---------------------------------------------------------
        has_remaining_planned = False

        calendar_events = context.get("calendar", [])

        if isinstance(calendar_events, list):

            for ev in calendar_events:

                ev_date = pd.to_datetime(
                    ev.get("start_date_local"),
                    errors="coerce"
                )

                if pd.isna(ev_date):
                    continue

                if ev_date.date() != today:
                    continue

                # planned but not completed
                if not ev.get("paired_activity_id"):
                    has_remaining_planned = True
                    break

        # ---------------------------------------------------------
        # Day context
        # ---------------------------------------------------------
        day_context = (
            "mixed_day"
            if has_completed_activity and has_remaining_planned
            else state_mode
        )

        context["load_state"] = {
            "mode": state_mode,

            "day_context": day_context,

            "meaning": (
                "actual_sunset"
                if has_completed_activity
                else "sunrise"
            ),

            "source": (
                "latest_completed_activity"
                if has_completed_activity
                else "ewma_decay_from_previous_day"
            ),

            "method": (
                "authoritative_activity"
                if has_completed_activity
                else "pure_ewma_decay"
            ),

            "tau_ctl": (
                None
                if has_completed_activity
                else 42.0
            ),

            "tau_atl": (
                None
                if has_completed_activity
                else 7.0
            ),

            "includes_planned_load": False,

            "includes_completed_load": has_completed_activity,
        }

        debug(
            context,
            f"[T1-WELLNESS-OBSERVED] "
            f"mode={state_mode} "
            f"sunrise_date={sunrise.get('_date')} "
            f"today_tss={today_tss} "
            f"CTL={context['ctl']} "
            f"ATL={context['atl']} "
            f"TSB={context['tsb']}"
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
        context = collect_zone_distributions(zone_df, athleteProfile, context)

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

    # =========================================================
    # 🔥 OUTLIER DETECTION (MULTI-FACTOR LOAD-ORDER MODEL)
    # =========================================================
    try:
        import numpy as np

        # -----------------------------------------------------
        # 1️⃣ Correct dataset
        # -----------------------------------------------------
        df = context.get("df_light_full")

        if df is None or df.empty:
            df = context.get("_df_light_90d")

        if df is None or df.empty:
            df = df_master

        df = df.copy()

        debug(context, f"[OUTLIERS] Dataset rows={len(df)}")

        # -----------------------------------------------------
        # 2️⃣ Athlete sport settings
        # -----------------------------------------------------
        athlete = context.get("athlete") or {}

        sport_settings = athlete.get("sportSettings", [])

        debug(
            context,
            f"[OUTLIERS] sportSettings={len(sport_settings)}"
        )

        # -----------------------------------------------------
        # Build sport lookup
        # -----------------------------------------------------
        sport_lookup = {}

        for s in sport_settings:

            for t in s.get("types", []):

                sport_lookup[t] = s

        debug(
            context,
            f"[OUTLIERS] sport_lookup_types={list(sport_lookup.keys())[:10]}"
        )

        # -----------------------------------------------------
        # 3️⃣ Guardrails
        # -----------------------------------------------------
        required = [
            "icu_training_load",
            "moving_time"
        ]

        if not all(c in df.columns for c in required):

            context["outliers"] = []
            context["outlier_summary"] = {}

            debug(
                context,
                "[OUTLIERS] Missing required columns"
            )

        else:

            # -------------------------------------------------
            # Filter invalid sessions
            # -------------------------------------------------
            df = df[
                (df["icu_training_load"] > 20) &
                (df["moving_time"] > 1800)
            ].copy()

            if df.empty:

                context["outliers"] = []
                context["outlier_summary"] = {}

                debug(
                    context,
                    "[OUTLIERS] No valid rows"
                )

            else:

                # -------------------------------------------------
                # 4️⃣ Derived metrics
                # -------------------------------------------------
                df["hours"] = df["moving_time"] / 3600

                df["density"] = np.where(
                    df["hours"] > 0,
                    df["icu_training_load"] / df["hours"],
                    0
                )

                # -------------------------------------------------
                # Optional columns
                # -------------------------------------------------
                optional_cols = [
                    "icu_weighted_avg_watts",
                    "average_heartrate",
                    "average_speed"
                ]

                for col in optional_cols:

                    if col not in df.columns:
                        df[col] = np.nan

                # -------------------------------------------------
                # 5️⃣ Baselines
                # -------------------------------------------------
                def safe_stats(series):

                    s = pd.to_numeric(
                        series,
                        errors="coerce"
                    ).dropna()

                    if s.empty:
                        return {
                            "mean": 0,
                            "std": 0
                        }

                    return {
                        "mean": float(s.mean()),
                        "std": float(s.std())
                    }

                stats = {

                    "tss":
                        safe_stats(df["icu_training_load"]),

                    "density":
                        safe_stats(df["density"]),

                    "power":
                        safe_stats(df["icu_weighted_avg_watts"]),

                    "hr":
                        safe_stats(df["average_heartrate"]),

                    "pace":
                        safe_stats(
                            df.get("pace", df.get("average_speed"))
                        )
                }

                debug(
                    context,
                    f"[OUTLIERS] stats={stats}"
                )

                # -------------------------------------------------
                # 6️⃣ Safe zscore helper
                # -------------------------------------------------
                def safe_z(v, mean_v, std_v):

                    if (
                        std_v == 0 or
                        pd.isna(std_v) or
                        pd.isna(v)
                    ):
                        return 0

                    return (v - mean_v) / std_v

                # -------------------------------------------------
                # 7️⃣ Resolve metric chain
                # -------------------------------------------------
                def resolve_metric_chain(load_order):

                    if not load_order:
                        return ["HR"]

                    return (
                        str(load_order)
                        .upper()
                        .split("_")
                    )

                # -------------------------------------------------
                # 8️⃣ Per-row analysis
                # -------------------------------------------------
                rows = []

                for _, o in df.iterrows():

                    sport = str(
                        o.get("type", "Unknown")
                    )

                    sport_cfg = sport_lookup.get(sport, {})

                    load_order = sport_cfg.get(
                        "load_order",
                        "HR"
                    )

                    metric_chain = resolve_metric_chain(
                        load_order
                    )

                    # ---------------------------------------------
                    # Core zscores
                    # ---------------------------------------------
                    z_tss = safe_z(
                        o["icu_training_load"],
                        stats["tss"]["mean"],
                        stats["tss"]["std"]
                    )

                    z_density = safe_z(
                        o["density"],
                        stats["density"]["mean"],
                        stats["density"]["std"]
                    )

                    # ---------------------------------------------
                    # Primary metric resolution
                    # ---------------------------------------------
                    z_primary = 0
                    primary_label = "none"

                    power_val = pd.to_numeric(
                        o["icu_weighted_avg_watts"],
                        errors="coerce"
                    )

                    hr_val = pd.to_numeric(
                        o["average_heartrate"],
                        errors="coerce"
                    )

                    pace_val = pd.to_numeric(
                        o.get("pace", o.get("average_speed")),
                        errors="coerce"
                    )

                    for metric in metric_chain:

                        # -----------------------------------------
                        # POWER
                        # -----------------------------------------
                        if (
                            metric == "POWER" and
                            pd.notna(power_val) and
                            power_val > 0
                        ):

                            z_primary = safe_z(
                                power_val,
                                stats["power"]["mean"],
                                stats["power"]["std"]
                            )

                            primary_label = "power"

                            break

                        # -----------------------------------------
                        # PACE
                        # -----------------------------------------
                        elif (
                            metric == "PACE" and
                            pd.notna(pace_val) and
                            pace_val > 0
                        ):

                            z_primary = safe_z(
                                pace_val,
                                stats["pace"]["mean"],
                                stats["pace"]["std"]
                            )

                            primary_label = "pace"

                            break

                        # -----------------------------------------
                        # HR
                        # -----------------------------------------
                        elif (
                            metric == "HR" and
                            pd.notna(hr_val) and
                            hr_val > 0
                        ):

                            z_primary = safe_z(
                                hr_val,
                                stats["hr"]["mean"],
                                stats["hr"]["std"]
                            )

                            primary_label = "hr"

                            break


                    # ---------------------------------------------
                    # Composite score
                    # ---------------------------------------------
                    zscore = np.sqrt(
                        (
                            (z_tss ** 2) * 0.45 +
                            (z_density ** 2) * 0.35 +
                            (z_primary ** 2) * 0.20
                        )
                    )

                    direction = (
                        "high"
                        if z_tss >= 0
                        else "low"
                    )

                    rows.append({

                        **o,

                        "sport":
                            sport,

                        "primary_metric":
                            primary_label,

                        "z_tss":
                            z_tss,

                        "z_density":
                            z_density,

                        "z_primary":
                            z_primary,

                        "zscore":
                            zscore,

                        "direction":
                            direction
                    })

                # -------------------------------------------------
                # 9️⃣ Final dataframe
                # -------------------------------------------------
                scored = pd.DataFrame(rows)

                outliers = scored[
                    scored["zscore"] >= 1.75
                ].copy()

                if outliers.empty:

                    context["outliers"] = []

                    context["outlier_summary"] = {

                        "count": 0,

                        "mean_tss":
                            round(
                                stats["tss"]["mean"],
                                1
                            ),

                        "std_tss":
                            round(
                                stats["tss"]["std"],
                                1
                            )
                    }

                else:

                    outliers = outliers.sort_values(
                        "zscore",
                        ascending=False
                    )

                    TOP_N = 5

                    outliers = outliers.head(TOP_N)

                    formatted = []

                    for _, o in outliers.iterrows():

                        raw_id = (
                            o.get("id") or
                            o.get("activity_id")
                        )

                        activity_id = None
                        activity_link = None

                        if pd.notna(raw_id):

                            activity_id = str(raw_id)

                            if not activity_id.startswith("i"):
                                activity_id = f"i{activity_id}"

                            activity_link = (
                                f"https://intervals.icu/activities/{activity_id}"
                            )

                        z = round(
                            float(o["zscore"]),
                            2
                        )

                        severity = "normal"

                        if z >= 4:
                            severity = "extreme"

                        elif z >= 3:
                            severity = "significant"

                        elif z >= 2:
                            severity = "notable"

                        formatted.append({

                            "date":
                                str(
                                    o.get(
                                        "start_date_local",
                                        "?"
                                    )
                                )[:10],

                            "title":
                                o.get("name", "?"),

                            "activity_id":
                                activity_id,

                            "activity_link":
                                activity_link,

                            "sport":
                                o.get("sport"),

                            "primary_metric":
                                o.get("primary_metric"),

                            "tss":
                                float(
                                    o.get(
                                        "icu_training_load",
                                        0
                                    )
                                ),

                            "load_vs_mean":
                                round(
                                    o["icu_training_load"] /
                                    stats["tss"]["mean"],
                                    2
                                ),

                            "zscore":
                                z,

                            "severity":
                                severity,

                            "type":
                                o["direction"],

                            "components": {

                                "z_tss":
                                    round(
                                        float(o["z_tss"]),
                                        2
                                    ),

                                "z_density":
                                    round(
                                        float(o["z_density"]),
                                        2
                                    ),

                                "z_primary":
                                    round(
                                        float(o["z_primary"]),
                                        2
                                    )
                            }
                        })

                    # -------------------------------------------------
                    # 🔟 Store
                    # -------------------------------------------------
                    context["outliers"] = formatted

                    context["outlier_summary"] = {

                        "count":
                            int(len(outliers)),

                        "mean_tss":
                            round(
                                stats["tss"]["mean"],
                                1
                            ),

                        "std_tss":
                            round(
                                stats["tss"]["std"],
                                1
                            ),

                        "model":
                            "multifactor_load_order_v2"
                    }

                    debug(
                        context,
                        f"[OUTLIERS] "
                        f"Found {len(formatted)} outliers"
                    )

    except Exception as e:

        debug(
            context,
            f"⚠ Outlier detection failed: {e}"
        )

        context["outliers"] = []
        context["outlier_summary"] = {}
    # ------------------------------------------------------------
    # 🔎 Defensive sanity check before qualitative mapping
    # ------------------------------------------------------------

    if isinstance(daily_summary, pd.DataFrame):

        # 1️⃣ Remove duplicate columns (prevents DataFrame-return bug)
        if daily_summary.columns.duplicated().any():
            debug(context, f"[T1-DEBUG] Duplicate columns detected → removing")
            daily_summary = daily_summary.loc[:, ~daily_summary.columns.duplicated()]

        # 2️⃣ Log structure once (not per column)
        debug(context, f"[T1-DEBUG] daily_summary columns → {list(daily_summary.columns)}")



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
