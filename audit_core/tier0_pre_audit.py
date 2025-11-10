# audit_core/tier0_pre_audit.py — v16.14-OAUTH-STRICT + Canonical TZ Enforcement
import os
import sys
import requests
import pandas as pd
from audit_core.utils import debug
from datetime import datetime, timedelta
from audit_core.errors import AuditHalt

INTERVALS_API = "https://intervals.icu/api/v1"
ICU_TOKEN = os.getenv("ICU_OAUTH")  # OAuth-only


def resolve_report_trigger(user_cmd: str, tz: str):
    today = datetime.now().astimezone().date()
    cmd = user_cmd.lower().strip()

    if any(k in cmd for k in ["rolling", "last 7", "past 7"]):
        mode = "rolling"
        start = today - timedelta(days=6)
        end = today
    elif any(k in cmd for k in ["calendar", "monday", "iso week"]):
        mode = "calendar"
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
    elif any(k in cmd for k in ["season", "block"]):
        mode = "season"
        start = today - timedelta(days=42)
        end = today
    else:
        mode = "rolling"
        start = today - timedelta(days=6)
        end = today

    return mode, start, end


def fetch_with_retry(url: str, headers: dict, max_retries: int = 2):
    """Low-level retry for individual API calls."""
    for attempt in range(max_retries + 1):
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp
        if attempt < max_retries:
            continue
    return resp


def estimate_payload_size(days: int, dataset: str):
    """Heuristic payload size estimator to prevent connector overflow."""
    if dataset == "wellness":
        return days * 30000  # wellness heavier
    else:
        return days * 12000  # activities lighter

#WELLNESS FETCH CHUNKED
def fetch_wellness_chunked(athlete_id, oldest, newest, headers, context=None, max_retries=2):
    """Adaptive and retryable chunked fetch for wellness data."""
    wellness = []

    for meta_attempt in range(max_retries + 1):
        try:
            est_payload_well = estimate_payload_size((newest - oldest).days + 1, "wellness")
            well_chunk_days = 3 if est_payload_well > 200000 else 7

            for offset in range(0, (newest - oldest).days + 1, well_chunk_days):
                chunk_start = oldest + timedelta(days=offset)
                chunk_end = min(newest, chunk_start + timedelta(days=well_chunk_days - 1))
                url = f"{INTERVALS_API}/athlete/{athlete_id}/wellness?oldest={chunk_start}&newest={chunk_end}"
                resp = fetch_with_retry(url, headers)
                if resp.status_code == 200 and resp.json():
                    wellness.extend(resp.json())

            if wellness:
                df_well = pd.DataFrame(wellness)
                return df_well

        except Exception as e:
            if meta_attempt == max_retries:
                raise AuditHalt(f"❌ Wellness fetch failed after {max_retries + 1} meta-retries: {e}")
            continue

    debug(context,"⚠ No wellness data available after adaptive chunking.")
    if "id" in df_well.columns and "date" not in df_well.columns:
        df_well.rename(columns={"id": "date"}, inplace=True)
    return pd.DataFrame(columns=["date", "ctl", "atl", "tsb"])

def fetch_activities_chunked(athlete_id, oldest, newest, headers, context=None, max_retries=2):
    """
    Adaptive and retryable chunked fetch for activities.
    Handles zone expansion, deduplication, canonical timezone/date normalization,
    and diagnostic summaries exactly as in the original Tier-0 pipeline.
    """
    import json
    from datetime import timedelta

    activities = []
    est_payload_acts = estimate_payload_size((newest - oldest).days + 1, "activities")
    act_chunk_days = 7 if est_payload_acts < 200000 else 3
    total_days = (newest - oldest).days + 1

    for meta_attempt in range(max_retries + 1):
        try:
            df_activities_list = []
            for offset in range(0, total_days, act_chunk_days):
                chunk_start = oldest + timedelta(days=offset)
                chunk_end = min(newest, chunk_start + timedelta(days=act_chunk_days)) - timedelta(seconds=1)

                debug(context,f"[Tier-0 fetch] chunk_start={chunk_start}  chunk_end={chunk_end}")
                fields = (
                    "id,name,start_date,start_date_local,moving_time,elapsed_time,"
                    "icu_training_load,distance,origin,power,hr,avg_power,avg_hr,"
                    "icu_zone_times,icu_hr_zone_times,pace_zone_times"
                )
                acts_url = (
                    f"{INTERVALS_API}/athlete/{athlete_id}/activities?"
                    f"oldest={chunk_start}&newest={chunk_end}&fields={fields}"
                )

                acts_resp = fetch_with_retry(acts_url, headers)
                if acts_resp.status_code != 200:
                    raise AuditHalt(f"❌ Failed to fetch activities ({acts_resp.status_code}) → {acts_resp.text[:200]}")

                df_chunk = pd.DataFrame(acts_resp.json())
                if not df_chunk.empty:
                    df_activities_list.append(df_chunk)

            if not df_activities_list:
                debug(context,"⚠ No activity chunks returned from API.")
                return pd.DataFrame()

            df_activities = pd.concat(df_activities_list, ignore_index=True)

            # --- Deduplication ---
            if "id" in df_activities.columns:
                before = len(df_activities)
                df_activities.drop_duplicates(subset=["id"], keep="first", inplace=True)
                debug(context,f"🧩 Tier-0 deduplication: {before - len(df_activities)} duplicates removed.")

            # --- Unit Normalization: ensure moving_time is in seconds ---
            if "moving_time" in df_activities.columns:
               max_val = df_activities["moving_time"].max()
            if max_val < 1000:  # likely already in hours
               debug(context,f"⚙️ Tier-0 normalization: converting moving_time from hours → seconds (max={max_val})")
               df_activities["moving_time"] *= 3600

            # --- Canonical timezone & date window normalization ---
            context = context or {}
            tz = context.get("timezone", "Europe/Zurich")
            df_activities["start_date_local"] = pd.to_datetime(
                df_activities["start_date"], utc=True, errors="coerce"
            ).dt.tz_convert(tz)

            # Slice to canonical window (inclusive)
            start_date = pd.to_datetime(oldest).date()
            end_date = pd.to_datetime(newest).date()
            before_rows = len(df_activities)
            df_activities = df_activities[
                (df_activities["start_date_local"].dt.date >= start_date)
                & (df_activities["start_date_local"].dt.date <= end_date)
            ]
            sliced_rows = len(df_activities)
            debug(context,f"[T0] Canonical slice → {sliced_rows}/{before_rows} rows retained ({start_date}–{end_date}, tz={tz})")

            # Post-slice dedup
            before = len(df_activities)
            df_activities.drop_duplicates(subset=["id"], keep="first", inplace=True)
            dropped = before - len(df_activities)
            if dropped > 0:
                debug(context,f"[T0] Post-slice deduplication removed {dropped} duplicates.")

            # Canonical columns
            df_activities["date"] = df_activities["start_date_local"].dt.date
            df_activities["origin"] = "event"
            if "elapsed_time" in df_activities.columns and "moving_time" in df_activities.columns:
                df_activities["elapsed_time"] = df_activities["moving_time"]

            # --- Zone array expansion ---
            def expand_zones(df, field, prefix):
                """
                Expands zone arrays (both list-of-dicts and list-of-ints) into numeric columns.
                Handles power_z*, hr_z*, pace_z* forms consistently.
                """
                import numpy as np
                import pandas as pd
                import json

                if field not in df.columns:
                    return df

                try:
                    def parse_entry(x):
                        # Accepts str(JSON), list[dict], list[int]
                        if isinstance(x, str):
                            try:
                                x = json.loads(x)
                            except Exception:
                                return []
                        if isinstance(x, list):
                            # list of dicts → extract 'secs' field
                            if all(isinstance(z, dict) for z in x):
                                return [z.get("secs", 0) for z in x]
                            # list of numeric → keep as-is
                            elif all(isinstance(z, (int, float)) for z in x):
                                return x
                        return []

                    zone_values = df[field].dropna().apply(parse_entry)
                    max_len = zone_values.map(len).max() if not zone_values.empty else 0
                    z = pd.DataFrame(zone_values.tolist(), index=df[field].dropna().index)
                    z = z.reindex(columns=range(max_len)).fillna(0)
                    z.columns = [f"{prefix}_z{i+1}" for i in range(max_len)]

                    df = pd.concat([df, z], axis=1)
                    debug(context,f"[DEBUG-T0] Expanded {field} → {len(z.columns)} numeric columns")
                except Exception as e:
                    debug(context,f"[DEBUG-T0] Failed to expand {field}: {e}")

                return df

            df_activities = expand_zones(df_activities, "icu_zone_times", "power")
            df_activities = expand_zones(df_activities, "icu_hr_zone_times", "hr")
            df_activities = expand_zones(df_activities, "pace_zone_times", "pace")

            # --- Diagnostic summary (true Σ(event.moving_time)) ---
            if "moving_time" in df_activities.columns:
                raw_sum = df_activities["moving_time"].sum()
                max_val = df_activities["moving_time"].max()
                if max_val < 1000:  # hours already
                    total_hours = raw_sum
                    debug(context,f"[T0] Diagnostic: true Σ(event.moving_time)={raw_sum:.2f} h (input already hours)")
                else:
                    total_hours = raw_sum / 3600
                    debug(context,f"[T0] Diagnostic: true Σ(event.moving_time)={raw_sum:.0f} s → {total_hours:.2f} h")
            else:
                total_hours = 0
                debug(context,"[T0] Diagnostic: no moving_time column found")

            total_tss = df_activities["icu_training_load"].sum() if "icu_training_load" in df_activities else 0
            debug(context,f"[T0] Canonical totals → Σ(TSS)={total_tss:.1f}")

            return df_activities

        except Exception as e:
            if meta_attempt == max_retries:
                raise AuditHalt(f"❌ Activities fetch failed after {max_retries + 1} meta-retries: {e}")
            continue

    debug(context,"⚠ No activities data available after chunked fetch.")
    return pd.DataFrame()

#FETCH AHLETEPROFILE
def fetch_athlete_profile(headers, context=None):
    """Fetch and normalize the athlete profile via OAuth2."""
    profile_url = f"{INTERVALS_API}/athlete/0/profile"
    debug(context,f"[T0] Fetching athlete profile via OAuth2: {profile_url}")

    profile_resp = fetch_with_retry(profile_url, headers)
    if profile_resp.status_code != 200:
        raise AuditHalt(
            f"❌ Failed to fetch athlete profile ({profile_resp.status_code}) → {profile_resp.text[:200]}"
        )

    profile_json = profile_resp.json()
    athlete = profile_json.get("athlete", profile_json)

    if not isinstance(athlete, dict):
        raise AuditHalt("❌ Invalid athlete profile format — expected dictionary payload")

    # Default ID handling
    if "id" not in athlete or athlete["id"] in [None, "", "unknown"]:
        debug(context,"⚠️ No athlete.id found — assigning default ID 0 (current athlete).")
        athlete["id"] = 0

    # Reject invalid sources
    if athlete.get("source") in ["mock", "cache", "sandbox"]:
        raise AuditHalt("❌ Tier-0 halted: invalid data origin (mock/cache/sandbox)")

    # Assign timezone
    tz = athlete.get("timezone", "Europe/Zurich")
    context = context or {}
    context["timezone"] = tz if isinstance(tz, str) and len(tz) >= 3 else "Europe/Zurich"

    # Merge static profile baseline
    from athlete_profile import ATHLETE_PROFILE
    merged_profile = ATHLETE_PROFILE.copy()
    merged_profile.update({
        "athlete_id": athlete.get("id", 0),
        "name": athlete.get("name", "Unknown Athlete"),
        "discipline": athlete.get("sport", "cycling"),
        "ftp": athlete.get("ftp", None),
        "weight": athlete.get("weight", None),
        "hr_rest": athlete.get("resting_hr", None),
        "hr_max": athlete.get("max_hr", None),
        "timezone": context["timezone"],
        "updated": athlete.get("updated"),
    })

    # Store in context for downstream
    context["athleteProfile"] = merged_profile
    context["athlete"] = athlete

    debug(context,f"[T0] Athlete profile fetched successfully — id={athlete['id']} name={athlete.get('name')}")
    return athlete, context

def run_tier0_pre_audit(start: str, end: str, context: dict):
    """Tier-0: OAuth-only Pre-audit fetch chain with adaptive chunking and meta-retry."""
    if not ICU_TOKEN:
        raise EnvironmentError("Missing Intervals.icu OAuth token. Set ICU_OAUTH env var.")

    # --- Reset cumulative totals before Tier-0 calculations ---
    context["totalHours"] = 0
    context["totalTss"] = 0
    context["totalDistance"] = 0
    context.pop("eventTotals", None)
    debug(context,"🧩 Tier-0 reset: cleared totalHours/TSS/distance before aggregation")

    # --- Always purge before data fetch ---
    purge_keys = ["eventTotals", "dailyMerged", "df_events", "athleteProfile"]
    for key in purge_keys:
        context.pop(key, None)

    context["auditPartial"] = False
    context["auditFinal"] = False
    context["purge_enforced"] = True
    debug(context,"🧹 Tier-0 purge enforced — previous cache cleared.")

    headers = {"Authorization": f"Bearer {ICU_TOKEN}"}


    # --- Step 1: Fetch athlete profile ---
    athlete, context = fetch_athlete_profile(headers, context)

    # --- Step 2: Determine date window ---
    mode, oldest, newest = resolve_report_trigger("weekly", context["timezone"])
    context.update({"report_mode": mode, "window_start": oldest, "window_end": newest})

    # --- Step 3: Fetch activities using chunked adaptive method ---
    df_activities = fetch_activities_chunked(athlete["id"], oldest, newest, headers, context)
    if df_activities.empty:
        raise AuditHalt("❌ No activity data returned after chunked fetch")

    # --- Step 4: Fetch wellness with adaptive chunking + meta-retry ---
    wellness = fetch_wellness_chunked(athlete["id"], oldest, newest, headers, context)
    if wellness is None or wellness.empty:
        raise AuditHalt("❌ No wellness data returned after chunked fetch")

    # --- Debug inspection ---
    debug(context,"[DEBUG] wellness raw:", type(wellness), len(wellness))
    if isinstance(wellness, pd.DataFrame):
        debug(context,"[DEBUG] wellness columns:", wellness.columns.tolist())
        debug(context,"[DEBUG] wellness head:\n", wellness.head())
        
    # --- Step 5: Finalize context ---
    context.update({"auditPartial": False, "auditFinal": False})
    context["window_summary"] = {"mode": mode, "start": str(oldest), "end": str(newest)} 

    total_hours = df_activities["moving_time"].sum() / 3600 if "moving_time" in df_activities else 0
    sys.stderr.write(
    f"\n[Tier-0 diagnostic] Σ(moving_time)/3600 = {total_hours:.2f}\nRows = {len(df_activities)}\n"
    )

    # Normalize wellness payload to DataFrame for Tier-1 compatibility
    if isinstance(wellness, list):
        if len(wellness) > 0:
            wellness = pd.DataFrame(wellness)
        else:
            wellness = pd.DataFrame(columns=["date", "fatigue", "sleep", "hrv", "recovery"])

    debug(context,f"[T0] Pre-audit complete: activities={len(df_activities)}, wellness_rows={len(wellness)}")



    return df_activities, wellness, context, context["auditPartial"], context["auditFinal"]