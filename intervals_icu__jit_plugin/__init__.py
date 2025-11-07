import json

# Load current Intervals schema
with open("Schema_3_9_12.json", "r", encoding="utf-8") as f:
    SCHEMA = json.load(f)

def get_schema_version():
    return SCHEMA.get("info", {}).get("version", "3.9.12")

def getAthleteProfile():
    # Minimal valid local profile
    profile_schema = SCHEMA["components"]["schemas"]["AthleteProfile"]
    return {
        "athlete": {
            "id": "0",
            "name": "Local Athlete",
            "timezone": "Europe/Zurich",
        },
        "sharedFolders": [],
        "customItems": [],
    }

def listActivities(**kwargs):
    # Structure aligned to Schema 3.9.12 Activity object
    return []

def listWellness(**kwargs):
    return []
