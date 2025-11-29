import json
import os
from datetime import datetime

# --- Load schema ---
SCHEMA_PATH = "Schema_3_9_18.json"
if not os.path.exists(SCHEMA_PATH):
    raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    SCHEMA = json.load(f)

# --- Core helpers ---
def get_schema_version():
    """Return current schema version."""
    return SCHEMA.get("info", {}).get("version", "3.9.18")

def _now():
    """Return UTC timestamp in ISO format."""
    return datetime.utcnow().isoformat() + "Z"

# --- API mocks (schema-aligned) ---
def getAthleteProfile():
    """Return minimal valid profile, schema-compliant."""
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
    """
    Schema-compliant local placeholder.
    When called in governance mode, must produce an empty list but preserve field structure.
    """
    return {
        "meta": {
            "schema_version": get_schema_version(),
            "source": "local",
            "generated": _now(),
        },
        "activities": [],
        "eventTotals": {
            "distance_km": 0.0,
            "moving_time_h": 0.0,
            "tss": 0,
        },
        "audit_flags": {
            "tier2_event_finalizer_strict": True,
            "tier2_event_totals_lock": True,
            "render_source": "event_totals",
        },
    }

def listWellness(**kwargs):
    """Schema-aligned placeholder for wellness data."""
    return {
        "meta": {
            "schema_version": get_schema_version(),
            "source": "local",
            "generated": _now(),
        },
        "wellness": [],
    }

# --- Compliance utility ---
def validate_against_schema():
    """
    Verifies that schema definitions required by governance manifest exist.
    Used by loadAllRules() → Tier-0 audit.
    """
    required_sections = [
        "components",
        "paths",
        "x-validation-rules",
    ]
    missing = [r for r in required_sections if r not in SCHEMA]
    if missing:
        raise ValueError(f"Schema missing required sections: {missing}")
    return True


# --- Backward-compatibility aliases (for URF v5.x controllers) ---
# These maintain compatibility with orchestration calls expecting older function names.
listActivitiesLight = listActivities
listActivitiesFull = listActivities
