"""
semantic_json_builder.py
------------------------

Builds a FULL semantic JSON coaching graph based on the Unified Reporting
Framework v5.1, Coaching Profile, Coaching Cheat Sheet, and all Tier-2 modules.

This is the JSON ChatGPT was designed to consume — NOT raw data, NOT totals-only.

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

from datetime import datetime
from coaching_cheat_sheet import CHEAT_SHEET  # :contentReference[oaicite:5]{index=5}
from coaching_profile import COACH_PROFILE    # :contentReference[oaicite:6]{index=6}
from audit_core.utils import debug


def semantic_block_for_metric(name, value, context):
    """
    Build the semantic envelope for a single metric.
    Each metric contains:
      - numeric value
      - framework (from Coaching Profile or URF)
      - thresholds (from cheat sheet)
      - classification
      - interpretation
      - coaching implication
      - related metrics
    """

    thresholds = CHEAT_SHEET["thresholds"].get(name, {})
    interpretation = CHEAT_SHEET["context"].get(name)
    coaching_link = CHEAT_SHEET["coaching_links"].get(name)
    profile_desc = COACH_PROFILE["markers"].get(name, {})

    # Classification helper
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
        "value": value,
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
    Build the FULL semantic coaching graph used by ChatGPT.
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
                "start": str(context.get("window_start")),
                "end": str(context.get("window_end")),
            },
            "timezone": context.get("timezone"),
            "athlete": context.get("athlete", {}),
        },

        # -------------------------------
        # 1. Authoritative Totals (Tier-2)
        # -------------------------------
        "totals": {
            "hours": context.get("totalHours"),
            "tss": context.get("totalTss"),
            "distance_km": context.get("totalDistanceKm"),
            "sessions": context.get("totalSessions"),
            "validated": context.get("auditFinal", False),
            "source": "Tier-2 Canonical Event Totals"
        },

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
                "date": str(row["date"]),
                "tss": float(row["icu_training_load"])
            }
            for _, row in getattr(context.get("df_daily"), "iterrows", lambda: [])()
        ] if context.get("df_daily") is not None else [],

        # -------------------------------
        # 6. Event Preview (safe)
        # -------------------------------
        "events": context.get("df_event_only_preview", []),

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

    # Debug: Log context before populating semantic graph
    debug(context, "[DEBUG] Full context before building semantic graph:", context)

    # -------------------------------
    # Populate semantic metric descriptors
    # -------------------------------
    derived = context.get("derived_metrics", {})
    for metric_name, info in derived.items():
        semantic["metrics"][metric_name] = semantic_block_for_metric(
            metric_name,
            info.get("value"),
            context
        )

    # -------------------------------
    # Integrate secondary markers
    # (FatOxI, CUR, MES, GR, Durability…)
    # -------------------------------
    secondary_keys = [
        "FatOxEfficiency", "FOxI", "CUR", "GR", "MES",
        "StressTolerance", "RecoveryIndex", "ZQI", "Polarisation"
    ]
    for k in secondary_keys:
        if k in context:
            semantic["metrics"][k] = semantic_block_for_metric(k, context.get(k), context)

    # Debug: Log generated semantic graph
    debug(semantic, "[DEBUG] Generated semantic graph:", semantic)

    return semantic

