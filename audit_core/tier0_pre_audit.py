# audit_core/tier0_pre_audit.py — v16.14-OAUTH-STRICT + Canonical TZ Enforcement
import os
import sys
import requests
import pandas as pd
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


def fetch_wellness_chunked(athlete_id, oldest, newest, headers, max_retries=2):
    """Adaptive and retryable chunked fetch for wellness data."""
    for meta_attempt in range(max_retries + 1):
        wellness = []
        try:
            est_payload_well = estimate_payload_size((newest - oldest).days + 1, "wellness")
            well_chunk_days = 3 if est_payload_well > 200000 else 7

            for offset in range(0, (newest - oldest).days + 1, well_chunk_days):
                chunk_start = oldest + timedelta(days=offset)
                chunk_end = min(newest, chunk_start + timedelta(days=well_chunk_days - 1))
                url = f"{INTERVALS_API}/athlete/0/wellness?oldest={chunk_start}&newest={chunk_end}"
                resp = fetch_with_retry(url, headers)
                if resp.status_code == 200 and resp.json():
                    wellness.extend(resp.json())

            if wellness:
                return wellness
        except Exception as e:
            if meta_attempt == max_retries:
                raise AuditHalt(f"❌ Wellness fetch failed after {max_retries + 1} meta-retries: {e}")
            continue

    print("⚠ No wellness data available after adaptive chunking.")
    return []


def run_tier0_pre_audit(start: str, end: str, context: dict):
    """Tier-0: OAuth-only Pre-audit fetch chain with adaptive chunking and meta-retry."""
    if not ICU_TOKEN:
        raise EnvironmentError("Missing Intervals.icu OAuth token. Set ICU_OAUTH env var.")

    # --- Always purge before data fetch ---
    purge_keys = ["eventTotals", "dailyMerged", "df_events", "athleteProfile"]
    for key in purge_keys:
        context.pop(key, None)

    context["auditPartial"] = False
    context["auditFinal"] = False
    context["purge_enforced"] = True
    print("🧹 Tier-0 purge enforced — previous cache cleared.")

    headers = {"Authorization": f"Bearer {ICU_TOKEN}"}

    # --- Step 1: Fetch athlete profile ---
    profile_url = f"{INTERVALS_API}/athlete/0/profile"
    print(f"[T0] Fetching athlete profile via OAuth2: {profile_url}")
    profile_resp = fetch_with_retry(profile_url, headers)
    if profile_resp.status_code != 200:
        raise AuditHalt(f"❌ Failed to fetch athlete profile ({profile_resp.status_code}) → {profile_resp.text[:200]}")

    profile_json = profile_resp.json()
    athlete = profile_json.get("athlete", profile_json)

    if not athlete or "id" not in athlete:
        raise AuditHalt("❌ Invalid athlete profile payload from Intervals.icu")

    if athlete.get("source") in ["mock", "cache", "sandbox"]:
        raise AuditHalt("❌ Tier-0 halted: invalid data origin (mock/cache/sandbox)")

    tz = athlete.get("timezone", "Europe/Zurich")
    context["timezone"] = tz if isinstance(tz, str) and len(tz) >= 3 else "Europe/Zurich"

    context["athleteProfile"] = profile_json
    context["athlete"] = athlete

    # --- Step 2: Determine date window ---
    mode, oldest, newest = resolve_report_trigger("weekly", context["timezone"])
    context.update({"report_mode": mode, "window_start": oldest, "window_end": newest})

    # --- Step 3: Fetch activities ---
    est_payload_acts = estimate_payload_size((newest - oldest).days + 1, "activities")
    act_chunk_days = 7 if est_payload_acts < 200000 else 3

    df_activities_list = []
    total_days = (newest - oldest).days + 1

    for offset in range(0, total_days, act_chunk_days):
        chunk_start = oldest + timedelta(days=offset)
        chunk_end = min(newest, chunk_start + timedelta(days=act_chunk_days)) - timedelta(seconds=1)

        print(f"[Tier-0 fetch] chunk_start={chunk_start}  chunk_end={chunk_end}")

        acts_url = f"{INTERVALS_API}/athlete/0/activities?oldest={chunk_start}&newest={chunk_end}"
        acts_resp = fetch_with_retry(acts_url, headers)
        if acts_resp.status_code != 200:
            raise AuditHalt(f"❌ Failed to fetch activities ({acts_resp.status_code}) → {acts_resp.text[:200]}")

        df_chunk = pd.DataFrame(acts_resp.json())
        if not df_chunk.empty:
            df_activities_list.append(df_chunk)

    df_activities = pd.concat(df_activities_list, ignore_index=True)

    # --- Quick inspection of fetched data ---
    print(df_activities[["id", "name", "moving_time"]])

    # --- Deduplication ---
    if "id" in df_activities.columns:
        before = len(df_activities)
        df_activities.drop_duplicates(subset=["id"], keep="first", inplace=True)
        after = len(df_activities)
        print(f"🧩 Tier-0 deduplication: {before - after} duplicate activities removed.")

    # --- Canonical timezone & date window normalization --------------------
    context.setdefault("timezone", "Europe/Zurich")
    tz = context["timezone"]

    # Normalize timestamps (force UTC then convert to canonical tz)
    df_activities["start_date_local"] = pd.to_datetime(
        df_activities["start_date"], utc=True, errors="coerce"
    ).dt.tz_convert(tz)

    # Strictly enforce local date slicing (include end day fully)
    start_date = pd.to_datetime(start).date()
    end_date = pd.to_datetime(end).date()
    before_rows = len(df_activities)
    df_activities = df_activities[
        (df_activities["start_date_local"].dt.date >= start_date)
        & (df_activities["start_date_local"].dt.date <= end_date)
    ]
    sliced_rows = len(df_activities)
    print(f"[T0] Canonical slice → {sliced_rows}/{before_rows} rows retained "
          f"({start_date}–{end_date}, tz={tz})")

    # Deduplicate again after slicing
    before = len(df_activities)
    df_activities.drop_duplicates(subset=["id"], keep="first", inplace=True)
    dropped = before - len(df_activities)
    if dropped > 0:
        print(f"[T0] Post-slice deduplication removed {dropped} duplicates.")

    # Final canonical columns
    df_activities["date"] = df_activities["start_date_local"].dt.date
    df_activities["origin"] = "event"

    print(f"[T0] start_date_local finalized → tz={tz} rows={len(df_activities)}")

    # Canonical duration field enforcement
    if "elapsed_time" in df_activities.columns and "moving_time" in df_activities.columns:
        df_activities["elapsed_time"] = df_activities["moving_time"]

    # --- Diagnostic summary -------------------------------------------------
    total_hours = df_activities["moving_time"].sum() / 3600
    total_tss = df_activities["icu_training_load"].sum()
    print(f"[T0] Canonical totals → Σ(moving_time)/3600={total_hours:.2f}  Σ(TSS)={total_tss:.1f}")

    # --- Step 4: Fetch wellness with adaptive chunking + meta-retry ---
    wellness = fetch_wellness_chunked(athlete["id"], oldest, newest, headers)

    # --- Step 5: Finalize context ---
    context.update({"auditPartial": False, "auditFinal": False})
    context["window_summary"] = {"mode": mode, "start": str(oldest), "end": str(newest)}

    sys.stderr.write(
        f"\n[Tier-0 diagnostic] Σ(moving_time)/3600 = {total_hours:.2f}\nRows = {len(df_activities)}\n"
    )
    sys.stderr.flush()

    # Normalize wellness payload to DataFrame for Tier-1 compatibility
    if isinstance(wellness, list):
        if len(wellness) > 0:
            wellness = pd.DataFrame(wellness)
        else:
            wellness = pd.DataFrame(columns=["date", "fatigue", "sleep", "hrv", "recovery"])

    return df_activities, wellness, context, context["auditPartial"], context["auditFinal"]
