"""
Tier-0 — Pre-Audit (v16.1)
Fetch live Intervals.icu data (activities + wellness) and set timezone context.
"""

import os
import requests
import pandas as pd

INTERVALS_API = "https://intervals.icu/api/v1"
ICU_TOKEN = os.getenv("ICU_OAUTH") or os.getenv("ICU_API_KEY")

def run_tier0_pre_audit(oldest, newest, context):
    if not ICU_TOKEN:
        raise EnvironmentError("Missing Intervals.icu token. Set ICU_OAUTH or ICU_API_KEY env var.")

    headers = {"Authorization": f"Bearer {ICU_TOKEN}"}

    # --- Profile ---
    profile = requests.get(f"{INTERVALS_API}/athlete", headers=headers).json()
    athlete = profile.get("athlete", profile)
    tz = athlete.get("timezone", "Europe/Zurich")
    context["athlete"] = athlete
    context["timezone"] = tz if isinstance(tz, str) and len(tz) >= 3 else "Europe/Zurich"

    # --- Activities ---
    acts_url = f"{INTERVALS_API}/activities?oldest={oldest}&newest={newest}"
    df_activities = pd.DataFrame(requests.get(acts_url, headers=headers).json())

    if "start_date" not in df_activities.columns:
        raise ValueError("No valid activities returned from Intervals.icu API")

    df_activities["start_date_local"] = pd.to_datetime(df_activities["start_date"]).dt.tz_localize("UTC").dt.tz_convert(context["timezone"])
    df_activities["date"] = df_activities["start_date_local"].dt.date

    # --- Wellness ---
    well_url = f"{INTERVALS_API}/athlete/{athlete['id']}/wellness?oldest={oldest}&newest={newest}"
    wellness = requests.get(well_url, headers=headers).json()

    auditPartial = False
    auditFinal = False
    return df_activities, wellness, context, auditPartial, auditFinal

