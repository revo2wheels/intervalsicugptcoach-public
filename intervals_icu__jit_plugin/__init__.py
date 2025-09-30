# intervals_icu__jit_plugin/__init__.py
# Compatibility stub for Railway backend — GPT no longer uses governance mode.

from datetime import datetime

def _now():
    return datetime.utcnow().isoformat() + "Z"

def get_schema_version():
    return "4.0.0"

def getAthleteProfile():
    return {
        "athlete": {
            "id": "0",
            "name": "Local Athlete",
            "timezone": "Europe/Zurich",
        }
    }

# --- SAFE PLACEHOLDERS EXPECTED BY RAILWAY BACKEND ---

def listActivities(**kwargs):
    return {
        "meta": {
            "schema_version": get_schema_version(),
            "source": "stub",
            "generated": _now(),
        },
        "activities": [],
        "eventTotals": {
            "distance_km": 0.0,
            "moving_time_h": 0.0,
            "tss": 0,
        },
    }

def listWellness(**kwargs):
    return {
        "meta": {
            "schema_version": get_schema_version(),
            "source": "stub",
            "generated": _now(),
        },
        "wellness": [],
    }

# Backward compatibility aliases kept for Railway imports:
listActivitiesLight = listActivities
listActivitiesFull = listActivities
