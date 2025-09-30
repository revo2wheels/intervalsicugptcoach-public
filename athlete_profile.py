#!/usr/bin/env python3
"""
coaching_profile.py — Framework Reference Model
Defines athlete-specific parameter fields.
Values are dynamically populated at runtime from athlete profile context.
"""

ATHLETE_PROFILE = {
    # --- Identity ---
    "athlete_id": None,
    "name": None,
    "discipline": "cycling",
    "timezone": None,
    "updated": None,

    # --- Physiology ---
    "ftp": None,
    "indoor_ftp": None,
    "weight": None,
    "hr_rest": None,
    "hr_max": None,

    # --- Derived (computed later if inputs exist) ---
    "ftp_wkg": None,
    "hr_reserve": None,

    # --- Zone model (sportSettings-derived, ordered thresholds) ---
    "zone_model": {
        "type": "power_zones",      # or "hr_zones"
        "schema": "Coggan_7Z",
        "zones": [],               # e.g. [55, 75, 90, 105, 120, 150]
        "names": []                # e.g. ["Z1", "Z2", ...]
    },

    # --- Optional / future ---
    "training_age_years": None,
    "preferred_units": "metric",
}


def map_icu_athlete_to_profile(icu_athlete: dict) -> dict:
    import copy
    profile = copy.deepcopy(ATHLETE_PROFILE)

    # -------------------------------------------------
    # Identity
    # -------------------------------------------------
    profile["athlete_id"] = icu_athlete.get("id")
    profile["name"] = icu_athlete.get("name")
    profile["discipline"] = "cycling"
    profile["timezone"] = icu_athlete.get("timezone")
    profile["updated"] = icu_athlete.get("icu_last_seen")

    # -------------------------------------------------
    # Physiology — SUPPORT BOTH RAW ICU + DERIVED KEYS
    # -------------------------------------------------
    profile["weight"] = (
        icu_athlete.get("icu_weight")
        or icu_athlete.get("weight")
    )

    profile["hr_rest"] = (
        icu_athlete.get("icu_resting_hr")
        or icu_athlete.get("restingHR")
    )

    # -------------------------------------------------
    # sportSettings — SUPPORT BOTH SHAPES
    # -------------------------------------------------
    sport_settings = icu_athlete.get("sportSettings") or []

    cycling = next(
        (
            s for s in sport_settings
            if s.get("type") == "Ride"
            or "Ride" in s.get("types", [])
        ),
        None
    )

    if cycling:
        profile["ftp"] = cycling.get("ftp") or profile["ftp"]
        profile["indoor_ftp"] = cycling.get("indoor_ftp")

        profile["hr_max"] = (
            cycling.get("max_hr")
            or cycling.get("maxHR")
        )

        profile["zone_model"]["zones"] = (
            cycling.get("power_zones")
            or cycling.get("powerZones")
            or []
        )

        profile["zone_model"]["names"] = (
            cycling.get("power_zone_names")
            or cycling.get("powerZoneNames")
            or []
        )

    # -------------------------------------------------
    # Derived values (only if inputs exist)
    # -------------------------------------------------
    if isinstance(profile["ftp"], (int, float)) and isinstance(profile["weight"], (int, float)):
        profile["ftp_wkg"] = round(profile["ftp"] / profile["weight"], 2)

    if isinstance(profile["hr_max"], (int, float)) and isinstance(profile["hr_rest"], (int, float)):
        profile["hr_reserve"] = profile["hr_max"] - profile["hr_rest"]

    return profile

def map_icu_athlete_to_identity(icu_athlete: dict) -> dict:
    return {
        "id": icu_athlete.get("id"),
        "name": icu_athlete.get("name"),
        "profile_medium": icu_athlete.get("profile_medium"),
        "city": icu_athlete.get("city"),
        "state": icu_athlete.get("state"),
        "country": icu_athlete.get("country"),
        "timezone": icu_athlete.get("timezone"),
        "sex": icu_athlete.get("sex"),
        "bio": icu_athlete.get("bio"),
        "website": icu_athlete.get("website"),
        "email": icu_athlete.get("email"),
    }

