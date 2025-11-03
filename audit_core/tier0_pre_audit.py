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
    for attempt in range(max_retries + 1):
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp
        if attempt < max_retries:
            continue
    return resp


def run_tier0_pre_audit(user_cmd: str, context: dict):
    if not ICU_TOKEN:
        raise EnvironmentError("Missing Intervals.icu token. Set ICU_OAUTH or ICU_API_KEY env var.")

    headers = {"Authorization": f"Bearer {ICU_TOKEN}"}

    # --- Step 1: Fetch athlete profile with retry ---
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

    # --- Step 3: Fetch activities with retry ---
    acts_url = f"{INTERVALS_API}/activities?oldest={oldest}&newest={newest}"
    acts_resp = fetch_with_retry(acts_url, headers)
    if acts_resp.status_code != 200:
        raise AuditHalt(f"❌ Failed to fetch activities ({acts_resp.status_code})")

    df_activities = pd.DataFrame(acts_resp.json())
    if df_activities.empty or "start_date" not in df_activities.columns:
        raise AuditHalt("❌ No valid activities returned from Intervals.icu API")

    df_activities["start_date_local"] = (
        pd.to_datetime(df_activities["start_date"])
        .dt.tz_localize("UTC")
        .dt.tz_convert(context["timezone"])
    )
    df_activities["date"] = df_activities["start_date_local"].dt.date
    df_activities["origin"] = "event"

    # --- Step 4: Fetch wellness with retry ---
    well_url = f"{INTERVALS_API}/athlete/{athlete['id']}/wellness?oldest={oldest}&newest={newest}"
    well_resp = fetch_with_retry(well_url, headers)
    wellness = well_resp.json() if well_resp.status_code == 200 else []
    if not wellness:
        print("⚠ No wellness data available after retry.")

    # --- Step 5: Finalize context ---
    context.update({"auditPartial": False, "auditFinal": False})
    context["window_summary"] = {"mode": mode, "start": str(oldest), "end": str(newest)}

    return df_activities, wellness, context, context["auditPartial"], context["auditFinal"]