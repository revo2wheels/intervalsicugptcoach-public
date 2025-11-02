"""
Tier-0 — Pre-Audit (v16)
Fetches live activity and wellness data, sets timezone and base context.
"""

import pandas as pd
from intervals_icu__jit_plugin import listActivities, listWellness, getAthleteProfile

def run_tier0_pre_audit(oldest, newest, context):
    profile = getAthleteProfile()
    athlete = profile["athlete"]
    tz = athlete.get("timezone", "Europe/Zurich")
    context["athlete"] = athlete
    context["timezone"] = tz if isinstance(tz, str) and len(tz) >= 3 else "Europe/Zurich"

    activities = listActivities(oldest=oldest, newest=newest, auto=True)
    wellness = listWellness(oldest=oldest, newest=newest)

    df = pd.DataFrame(activities)
    df["start_date_local"] = pd.to_datetime(df["start_date"]).dt.tz_convert(context["timezone"])
    df["date"] = df["start_date_local"].dt.date
    df_activities = df.copy(deep=True)

    auditPartial = False
    auditFinal = False
    return df_activities, wellness, context, auditPartial, auditFinal
