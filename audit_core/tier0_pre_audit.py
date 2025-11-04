import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from audit_core.errors import AuditHalt

INTERVALS_API = "https://intervals.icu/api/v1"
ICU_TOKEN = os.getenv("ICU_OAUTH") or os.getenv("ICU_API_KEY")


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
                url = f"{INTERVALS_API}/athlete/{athlete_id}/wellness?oldest={chunk_start}&newest={chunk_end}"
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


def run_tier0_pre_audit(user_cmd: str, context: dict):
    """Tier-0: Pre-audit fetch chain with adaptive chunking and meta-retry."""
    if not ICU_TOKEN:
        raise EnvironmentError("Missing Intervals.icu token. Set ICU_OAUTH or ICU_API_KEY env var.")

    # --- Enforce clean state before data fetch ---
    if context:
        purge_keys = ["eventTotals", "dailyMerged", "df_events", "athleteProfile"]
        for key in purge_keys:
            if key in context:
                del context[key]
        context["auditPartial"] = False
        context["auditFinal"] = False
        context["purge_enforced"] = True
        print("🧹 Tier-0 purge enforced — previous cache cleared.")

    headers = {"Authorization": f"Bearer {ICU_TOKEN}"}

    # --- Step 1: Fetch athlete profile ---
    profile_resp = fetch_with_retry(f"{INTERVALS_API}/athlete", headers)
    if profile_resp.status_code != 200:
        raise AuditHalt(f"❌ Failed to fetch athlete profile ({profile_resp.status_code})")

    athlete = profile_resp.json()
    if "athlete" in athlete:
        athlete = athlete["athlete"]

    if not athlete or "id" not in athlete:
        raise AuditHalt("❌ Invalid athlete profile payload from Intervals.icu")

    if athlete.get("source") in ["mock", "cache", "sandbox"]:
        raise AuditHalt("❌ Tier-0 halted: invalid data origin (mock/cache/sandbox)")

    tz = athlete.get("timezone", "Europe/Zurich")
    context["timezone"] = tz if isinstance(tz, str) and len(tz) >= 3 else "Europe/Zurich"

    context["athleteProfile"] = {
        "id": athlete.get("id"),
        "name": athlete.get("name", "Unknown"),
        "sex": athlete.get("sex", "U"),
        "age": athlete.get("age"),
        "city": athlete.get("city"),
        "country": athlete.get("country"),
        "timezone": context["timezone"],
        "bio": athlete.get("bio"),
        "website": athlete.get("website"),
    }
    context["athlete"] = context["athleteProfile"]

    # --- Step 2: Determine date window ---
    mode, oldest, newest = resolve_report_trigger(user_cmd, context["timezone"])
    context.update({"report_mode": mode, "window_start": oldest, "window_end": newest})

    # --- Step 3: Fetch activities (adaptive chunking) ---
    est_payload_acts = estimate_payload_size((newest - oldest).days + 1, "activities")
    act_chunk_days = 7 if est_payload_acts < 200000 else 3

    df_activities_list = []
    for offset in range(0, (newest - oldest).days + 1, act_chunk_days):
        chunk_start = oldest + timedelta(days=offset)
        chunk_end = min(newest, chunk_start + timedelta(days=act_chunk_days - 1))
        acts_url = f"{INTERVALS_API}/activities?oldest={chunk_start}&newest={chunk_end}"
        acts_resp = fetch_with_retry(acts_url, headers)
        if acts_resp.status_code != 200:
            raise AuditHalt(f"❌ Failed to fetch activities ({acts_resp.status_code})")
        df_chunk = pd.DataFrame(acts_resp.json())
        if not df_chunk.empty:
            df_activities_list.append(df_chunk)

    df_activities = pd.concat(df_activities_list, ignore_index=True)
    if df_activities.empty or "start_date" not in df_activities.columns:
        raise AuditHalt("❌ No valid activities returned from Intervals.icu API")

    df_activities["start_date_local"] = (
        pd.to_datetime(df_activities["start_date"])
        .dt.tz_localize("UTC")
        .dt.tz_convert(context["timezone"])
    )
    df_activities["date"] = df_activities["start_date_local"].dt.date
    df_activities["origin"] = "event"

    # --- Step 4: Fetch wellness with adaptive chunking + meta-retry ---
    wellness = fetch_wellness_chunked(athlete["id"], oldest, newest, headers)

    # --- Step 5: Finalize context ---
    context.update({"auditPartial": False, "auditFinal": False})
    context["window_summary"] = {"mode": mode, "start": str(oldest), "end": str(newest)}

    return df_activities, wellness, context, context["auditPartial"], context["auditFinal"]
