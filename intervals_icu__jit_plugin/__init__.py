# intervals_icu__jit_plugin/__init__.py
# Minimal stub — Cloudflare + Railway architecture no longer uses plugin governance layer.

from datetime import datetime

def get_schema_version():
    return "4.0.0"

def _now():
    return datetime.utcnow().isoformat() + "Z"

def getAthleteProfile():
    return {
        "athlete": {
            "id": "0",
            "name": "Local Athlete",
            "timezone": "Europe/Zurich"
        }
    }
