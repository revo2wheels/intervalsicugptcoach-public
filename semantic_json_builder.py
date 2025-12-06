"""
semantic_json_builder.py
------------------------

Builds a FULL semantic DICT coaching graph based on the Unified Reporting
Framework v5.1, Coaching Profile, Coaching Cheat Sheet, and all Tier-2 modules.

This is the DICT ChatGPT was designed to consume — NOT raw data, NOT totals-only.

It includes:
 - Authoritative totals
 - Derived metrics
 - Extended metrics
 - Trend metrics
 - Correlations
 - Framework metadata
 - Thresholds
 - Interpretations
 - Coaching implications
 - Phase detection
 - Actions (with reasoning)
 - Event previews (safe)
 - Daily load summaries
"""
import json
from datetime import datetime, date
import pandas as pd  # Ensure pandas is imported for Timestamp handling
from math import isnan  # To handle NaN values
from coaching_cheat_sheet import CHEAT_SHEET  # :contentReference[oaicite:5]{index=5}
from coaching_profile import COACH_PROFILE    # :contentReference[oaicite:6]{index=6}
from audit_core.utils import debug

def handle_missing_data(value, default_value=None):
    """Handles missing data like None or NaN."""
    if value is None or isinstance(value, float) and isnan(value):
        return default_value
    return value

# Helper function to convert Timestamp or datetime to string
def convert_to_str(value):
    """Convert datetime, Timestamp, or date objects to ISO format string."""
    if isinstance(value, (datetime,)):  # If the value is a datetime object
        return value.isoformat()  # Converts to ISO 8601 string
    elif isinstance(value, pd.Timestamp):  # Handle pandas Timestamp objects
        return value.isoformat()  # Convert to string
    elif isinstance(value, date):  # Handle date objects as well
        return value.isoformat()  # Convert to string
    return value

def semantic_block_for_metric(name, value, context):
    """Build the semantic envelope for a single metric."""
    thresholds = CHEAT_SHEET["thresholds"].get(name, {})
    interpretation = CHEAT_SHEET["context"].get(name)
    coaching_link = CHEAT_SHEET["coaching_links"].get(name)
    profile_desc = COACH_PROFILE["markers"].get(name, {})

    classification = None
    if thresholds:
        try:
            green = thresholds.get("green")
            amber = thresholds.get("amber")
            if green and green[0] <= float(value) <= green[1]:
                classification = "green"
            elif amber and amber[0] <= float(value) <= amber[1]:
                classification = "amber"
            else:
                classification = "red"
        except Exception:
            classification = "unknown"

    return {
        "name": name,
        "value": convert_to_str(value),  # Convert np.float64 to regular float or datetime to string
        "framework": profile_desc.get("framework") or "Unknown",
        "formula": profile_desc.get("formula"),
        "thresholds": thresholds,
        "classification": classification,
        "interpretation": interpretation,
        "coaching_implication": coaching_link,
        "related_metrics": profile_desc.get("criteria", {}),
    }

def build_semantic_json(context):
    """
    Build the FULL semantic coaching graph used by ChatGPT, using matching sources to render_unified_report.
    """

    # -------------------------------
    # 0. Metadata
    # -------------------------------
    semantic = {
        "meta": {
            "framework": "Unified Reporting Framework v5.1",
            "version": "v16.17",
            "generated_at": datetime.utcnow().isoformat(),
            "report_type": context.get("report_type"),
            "period": {
                "start": convert_to_str(context.get("window_start")),
                "end": convert_to_str(context.get("window_end")),
            },
            "timezone": context.get("timezone"),
            "athlete": context.get("athlete", {}),
        },

        # -------------------------------
        # 1. Authoritative Totals (Tier-2)
        # -------------------------------
        "hours": handle_missing_data(
            context.get("totalHours")  # ← canonical, created by render_unified_report
            or context.get("tier2_enforced_totals", {}).get("time_h")
            or context.get("tier1_visibleTotals", {}).get("hours")
            or context.get("eventTotals", {}).get("hours"),
            0
        ),

        "tss": handle_missing_data(
            context.get("totalTss")
            or context.get("tier2_enforced_totals", {}).get("tss")
            or context.get("tier1_visibleTotals", {}).get("tss")
            or context.get("eventTotals", {}).get("tss"),
            0
        ),

        "distance_km": handle_missing_data(
            context.get("totalDistance")
            or context.get("tier2_enforced_totals", {}).get("distance_km")
            or context.get("tier1_visibleTotals", {}).get("distance")
            or context.get("eventTotals", {}).get("distance"),
            0
        ),
        # -------------------------------
        # 2. Semantic Derived Metrics
        # -------------------------------
        "metrics": {},

        # -------------------------------
        # 3. Extended, Adaptation, Trends, Correlations
        # -------------------------------
        "extended_metrics": context.get("extended_metrics", {}),
        "adaptation_metrics": context.get("adaptation_metrics", {}),
        "trend_metrics": context.get("trend_metrics", {}),
        "correlation_metrics": context.get("correlation_metrics", {}),

        # -------------------------------
        # 4. Zone Distribution (% only)
        # -------------------------------
        "zones": {
            "power": context.get("zone_dist_power", {}),
            "hr": context.get("zone_dist_hr", {}),
        },

        # -------------------------------
        # 5. Daily Load (TSS only)
        # -------------------------------
        "daily_load": [
            {
                "date": row["date"],  # These will be handled automatically
                "tss": float(row["icu_training_load"])
            }
            for _, row in getattr(context.get("df_daily"), "iterrows", lambda: [])()
        ] if context.get("df_daily") is not None else [],

        # -------------------------------
        # 6. Event Preview (safe)
        # -------------------------------
        "events": [
            {
                "start_date_local": event.get("start_date_local"),  # These will be handled automatically
                **event
            }
            for event in context.get("df_event_only_preview", [])
        ],

        # -------------------------------
        # 7. Phases (Periodisation)
        # -------------------------------
        "phases": context.get("phases", []),

        # -------------------------------
        # 8. Actions (with reasoning)
        # -------------------------------
        "actions": context.get("actions", []),

        # -------------------------------
        # 9. Wellness summary
        # -------------------------------
        "wellness": context.get("wellness_summary", {}),
    }

    # -------------------------------
    # Populate semantic metric descriptors
    # -------------------------------
    derived = context.get("derived_metrics", {})
    for metric_name, info in derived.items():
        semantic["metrics"][metric_name] = {
            "name": metric_name,
            "value": handle_missing_data(info.get("value"), 0),
            "classification": info.get("classification", "unknown"),
            "interpretation": info.get("interpretation", ""),
            "coaching_implication": info.get("coaching_implication", ""),
            "related_metrics": info.get("related_metrics", {}),
        }

    # -------------------------------
    # Integrate secondary markers
    # -------------------------------
    secondary_keys = [
        "FatOxEfficiency", "FOxI", "CUR", "GR", "MES",
        "StressTolerance", "RecoveryIndex", "ZQI", "Polarisation"
    ]
    for k in secondary_keys:
        if k in context:
            semantic["metrics"][k] = semantic_block_for_metric(k, context.get(k), context)

    # Return the semantic graph as a dictionary directly, not as a JSON string
    return semantic
