#!/usr/bin/env python3
"""
coaching_profile.py — Framework Reference Model
Defines athlete-specific parameter fields.
Values are dynamically populated at runtime from athlete profile context.
"""

ATHLETE_PROFILE = {
    # --- Athlete Identification ---
    "athlete_id": None,
    "name": None,
    "discipline": None,   # e.g., 'cycling', 'running', 'triathlon'

    # --- Physiological Parameters ---
    "ftp": None,          # Functional Threshold Power (W)
    "weight": None,       # kg
    "hr_rest": None,      # bpm
    "hr_max": None,       # bpm

    # --- Derived Ratios (auto-calculated if data present) ---
    "ftp_wkg": None,      # computed = ftp / weight
    "hr_reserve": None,   # computed = hr_max - hr_rest

    # --- Zone Model (framework-defined, not fixed values) ---
    "zone_model": {
        "type": "power_zones",   # or "hr_zones"
        "schema": "Coggan_7Z",   # reference model name
        "zones": {}              # populated dynamically
    },

    # --- Adaptation & Metadata ---
    "training_age_years": None,
    "preferred_units": "metric",
    "environment": None,   # e.g., 'indoor', 'outdoor', 'mixed'
    "timezone": None,
    "updated": None,
}
