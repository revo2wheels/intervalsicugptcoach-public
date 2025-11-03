"""
Tier-0 — Pre-Audit (v16.1-EOD-004)
Fetches live Intervals.icu athlete profile, activities, and wellness data.
Initializes timezone and injects athleteProfile for downstream render.
Supports both flat and nested 'athlete' JSON payloads.
"""

import os
import requests
import pandas as pd
from audit_core.errors import AuditHalt

INTERVALS_API = "https://intervals.icu/api/v1"
ICU_TOKEN = os.getenv("ICU_OAUTH") or os.getenv("ICU_API_KEY")


def run_tier0_pre_audit(oldest, newest, context):
    # --- Step 0: Authentication ---
    if not ICU_TOKEN:
        raise EnvironmentError("Missing Intervals.icu token. Set ICU_OAUTH or ICU_API_KEY env var.")

    headers = {"Authorization": f"Bearer {ICU_TOKEN}"}

    # --- Step 1: Fetch athlete profile ---
    profile_resp = requests.get(f"{INTERVALS_API}/athlete", headers=headers)
    if profile_resp.status_code != 200:
        raise AuditHalt(f"❌ Failed to fetch athlete profile ({profile_resp.status_code})")

    athlete = profile_resp.json()
    if "athlete" in athlete:                     # handle nested JSON
        athlete = athlete["athlete"]

    if not athlete or "id" not in athlete:
        raise AuditHalt("❌ Invalid athlete profile payload from Intervals.icu")

    # Origin validation
    if athlete.get("source") in ["mock", "cache", "sandbox"]:
        raise AuditHalt("❌ Tier-0 halted: invalid data origin (mock/cache/sandbox)")

    # Timezone fallback
    tz = athlete.get("timezone", "Europe/Zurich")
    context["timezone"] = tz if isinstance(tz, str) and len(tz) >= 3 else "Europe/Zurich"

    # --- Step 2: Inject athleteProfile block (for renderer Section 1) ---
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

    # --- Step 3: Fetch activities ---
    acts_url = f"{INTERVALS_API}/activities?oldest={oldest}&newest={newest}"
    acts_resp = requests.get(acts_url, headers=headers)
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

    # --- Step 4: Fetch wellness ---
    well_url = f"{INTERVALS_API}/athlete/{athlete['id']}/wellness?oldest={oldest}&newest={newest}"
    well_resp = requests.get(well_url, headers=headers)
    if well_resp.status_code == 200:
        wellness = well_resp.json()
    else:
        wellness = []
        print("⚠ No wellness data available for this window")

    # --- Step 5: Finalize ---
    context["auditPartial"] = False
    context["auditFinal"] = False

    return df_activities, wellness, context, context["auditPartial"], context["auditFinal"]
