"""
semantic_json_builder.py
------------------------

Builds a FULL semantic DICT coaching graph based on the Unified Reporting
Framework v5.1, Coaching Profile, Coaching Cheat Sheet, and all Tier-2 modules.

Includes:
 - Authoritative totals
 - Derived metrics
 - Extended metrics
 - Adaptation metrics
 - Trend metrics
 - Correlations
 - Wellness (sanitised)
 - Thresholds / interpretations / coaching links
 - Actions
 - Phase detection
 - Event previews (stable)
 - Daily load summaries
"""

import json
from datetime import datetime, date
import pandas as pd
from math import isnan
from coaching_cheat_sheet import CHEAT_SHEET
from coaching_profile import COACH_PROFILE
from audit_core.utils import debug


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def handle_missing_data(value, default_value=None):
    """Convert NaN or None → safe default."""
    if value is None:
        return default_value
    if isinstance(value, float) and isnan(value):
        return default_value
    return value


def convert_to_str(value):
    """Convert datetime/Timestamp/date → ISO string."""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return value


def semantic_block_for_metric(name, value, context):
    """Builds semantic envelope for a single metric."""
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
        "value": convert_to_str(value),
        "framework": profile_desc.get("framework") or "Unknown",
        "formula": profile_desc.get("formula"),
        "thresholds": thresholds,
        "classification": classification,
        "interpretation": interpretation,
        "coaching_implication": coaching_link,
        "related_metrics": profile_desc.get("criteria", {}),
    }


# ---------------------------------------------------------
# Insights Builder
# ---------------------------------------------------------

def build_insights(semantic):
    insights = {}

    load = semantic.get("extended_metrics", {})
    atl = load.get("ATL", {}).get("value")
    ctl = load.get("CTL", {}).get("value")

    ft = None
    if isinstance(atl, (int, float)) and isinstance(ctl, (int, float)) and ctl > 0:
        ft = round((atl - ctl) / ctl, 3)

    insights["fatigue_trend"] = {
        "value": ft,
        "interpretation": (
            "Positive = accumulating fatigue, negative = recovering, near zero = stable"
            if ft is not None else "Insufficient data"
        )
    }

    # 2 — Load distribution
    zones = semantic.get("zones", {}).get("power", {})
    z1 = zones.get("power_z1", 0)
    z2 = zones.get("power_z2", 0)
    z3plus = sum(zones.get(k, 0) for k in zones if k not in ("power_z1", "power_z2"))

    distribution = "unknown"
    if (z1 + z2) >= 70:
        distribution = "endurance-focused"
    if z3plus >= 30:
        distribution = "threshold-heavy"
    if z1 >= 50 and z3plus >= 20:
        distribution = "polarised"

    insights["load_distribution"] = {
        "zones": {
            "z1_z2": round(z1 + z2, 1),
            "z3_plus": round(z3plus, 1)
        },
        "classification": distribution,
        "interpretation": (
            "Distribution indicates focus on aerobic base"
            if distribution == "endurance-focused"
            else "High intensity bias; increased recovery required"
            if distribution == "threshold-heavy"
            else "Strongly polarised training distribution"
            if distribution == "polarised"
            else "Cannot classify distribution"
        )
    }

    # 3 — Metabolic drift proxy (FOxI based)
    foxi = semantic.get("metrics", {}).get("FOxI", {}).get("value")
    drift = None
    if isinstance(foxi, (int, float)):
        drift = round((70 - foxi) / 70, 3)

    insights["metabolic_drift"] = {
        "value": drift,
        "interpretation": (
            "Lower values indicate good aerobic durability"
            if drift is not None else "Insufficient data"
        )
    }

    # 4 — Fitness phase classification
    acwr = semantic.get("metrics", {}).get("ACWR", {}).get("value")
    phase = "unknown"

    if isinstance(acwr, (int, float)):
        if acwr < 0.8:
            phase = "recovery/deload"
        elif 0.8 <= acwr <= 1.3:
            phase = "productive/loading"
        elif acwr > 1.3:
            phase = "overreaching"

    insights["fitness_phase"] = {
        "phase": phase,
        "interpretation": (
            "Athlete is absorbing training well"
            if phase == "productive/loading"
            else "Athlete is under low load — suitable for recovery"
            if phase == "recovery/deload"
            else "High risk of overtraining — reduce load"
            if phase == "overreaching"
            else "Phase cannot be determined"
        )
    }

    return insights


# ---------------------------------------------------------
# MAIN BUILDER
# ---------------------------------------------------------

def build_semantic_json(context):
    """Build the final semantic graph."""

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

        # Totals
        "hours": handle_missing_data(
            context.get("totalHours")
            or context.get("tier2_enforced_totals", {}).get("time_h")
            or 0
        ),
        "tss": handle_missing_data(
            context.get("totalTss")
            or context.get("tier2_enforced_totals", {}).get("tss")
            or 0
        ),
        "distance_km": handle_missing_data(
            context.get("totalDistance")
            or context.get("tier2_enforced_totals", {}).get("distance_km")
            or 0
        ),

        # Metric containers
        "metrics": {},
        "extended_metrics": context.get("extended_metrics", {}),
        "adaptation_metrics": context.get("adaptation_metrics", {}),
        "trend_metrics": context.get("trend_metrics", {}),
        "correlation_metrics": context.get("correlation_metrics", {}),

        # Zones
        "zones": {
            "power": context.get("zone_dist_power", {}),
            "hr": context.get("zone_dist_hr", {}),
        },

        # Daily load (df_daily optional)
        "daily_load": [
            {
                "date": row["date"],
                "tss": float(row["icu_training_load"])
            }
            for _, row in getattr(context.get("df_daily"), "iterrows", lambda: [])()
        ] if context.get("df_daily") is not None else [],

        # Events — FIXED (canonical df_events)
        "events": [],

        "phases": context.get("phases", []),
        "actions": context.get("actions", []),

        # Wellness — FIXED (NaN sanitised)
        "wellness": {
            k: handle_missing_data(v, None)
            for k, v in context.get("wellness_summary", {}).items()
        },
    }
    # --- FORCE semantic CTL/ATL/TSB to match markdown (Tier-1 canonical load_metrics) ---
    lm = context.get("load_metrics", {})
    if lm:
        semantic.setdefault("extended_metrics", {})

        for key in ("CTL", "ATL", "TSB"):
            if key in lm:
                val = lm[key]["value"] if isinstance(lm[key], dict) else lm[key]
                semantic["extended_metrics"][key] = {
                    "value": val,
                    "source": "tier1"
                }

    # ---------------------------------------------------------
    # Inject canonical CTL/ATL/TSB from Tier-1 load_metrics
    # Ensures semantic = markdown output exactly
    # ---------------------------------------------------------
    lm = context.get("load_metrics", {})

    def extract_load_value(key):
        val = lm.get(key)
        if isinstance(val, dict):
            return val.get("value")
        return val

    ctl = extract_load_value("CTL")
    atl = extract_load_value("ATL")
    tsb = extract_load_value("TSB")

    # Inject into semantic wellness (same as Markdown)
    semantic.setdefault("wellness", {})
    semantic["wellness"]["CTL"] = ctl
    semantic["wellness"]["ATL"] = atl
    semantic["wellness"]["TSB"] = tsb

    # Inject canonical load metrics into extended_metrics (override Tier-2)
    semantic.setdefault("extended_metrics", {})
    semantic["extended_metrics"]["CTL"] = {"value": ctl, "status": "ok"}
    semantic["extended_metrics"]["ATL"] = {"value": atl, "status": "ok"}
    semantic["extended_metrics"]["TSB"] = {"value": tsb, "status": "ok"}


    # ---------------------------------------------------------
    # EVENTS: canonical df_events (FIXED)
    # ---------------------------------------------------------
    df_events = context.get("df_events")
    if isinstance(df_events, pd.DataFrame) and not df_events.empty:
        semantic["events"] = [
            {
                "start_date_local": convert_to_str(row.get("start_date_local")),
                "name": row.get("name"),
                "icu_training_load": row.get("icu_training_load"),
                "moving_time": row.get("moving_time"),
                "distance": row.get("distance"),
            }
            for _, row in df_events.iterrows()
        ]

    # ---------------------------------------------------------
    # DERIVED METRICS
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # SECONDARY METRICS — do NOT overwrite derived metrics (FIXED)
    # ---------------------------------------------------------
    secondary_keys = [
        "FatOxEfficiency", "FOxI", "CUR", "GR", "MES",
        "StressTolerance", "RecoveryIndex", "ZQI", "Polarisation"
    ]

    for k in secondary_keys:
        if k in context and k not in semantic["metrics"]:
            semantic["metrics"][k] = semantic_block_for_metric(k, context.get(k), context)

    # ---------------------------------------------------------
    # Insights (final)
    # ---------------------------------------------------------
    semantic["insights"] = build_insights(semantic)

    return semantic
