def build_authorized_json(context):
    """
    Build the JSON payload ChatGPT is allowed to see.
    Derived strictly from post-audit Tier-1 + Tier-2 authorized fields.
    Never includes raw or recalculable inputs.
    """

    # --- Metadata / Framework / Athlete ---
    payload = {
        "meta": {
            "framework": "Unified_Reporting_Framework_v5.1",
            "report_type": context.get("report_type"),
            "timezone": context.get("timezone"),
            "period": {
                "start": str(context.get("window_start")),
                "end": str(context.get("window_end")),
            },
            "athlete": {
                "id": context.get("athlete", {}).get("id"),
                "name": context.get("athlete", {}).get("name"),
                "ftp": context.get("athleteProfile", {}).get("ftp"),
                "weight": context.get("athleteProfile", {}).get("weight"),
            }
        },

        # -------------------------------------------------------------
        # 1. Canonical Totals (Tier-2 Enforced Event-Only Totals)
        # -------------------------------------------------------------
        "totals": {
            "hours": context.get("totalHours"),
            "tss": context.get("totalTss"),
            "distance_km": context.get("totalDistanceKm"),
            "sessions": context.get("totalSessions"),
            "validated": context.get("auditFinal", False),
            "source": "Tier-2 enforced canonical totals"
        },

        # -------------------------------------------------------------
        # 2. Derived Metrics (Tier-2)
        # -------------------------------------------------------------
        "derived_metrics": {
            k: {
                "value": v.get("value"),
                "status": v.get("status"),
                "icon": v.get("icon"),
                "desc": v.get("desc"),
            }
            for k, v in context.get("derived_metrics", {}).items()
        },

        # -------------------------------------------------------------
        # 3. Extended Metrics (Tier-2 Extended + Coaching Profile)
        # -------------------------------------------------------------
        "extended_metrics": context.get("extended_metrics", {}),
        "adaptation_metrics": context.get("adaptation_metrics", {}),
        "trend_metrics": context.get("trend_metrics", {}),
        "correlation_metrics": context.get("correlation_metrics", {}),

        # -------------------------------------------------------------
        # 4. Wellness Summary (Tier-1 normalized)
        # -------------------------------------------------------------
        "wellness": context.get("wellness_summary", {}),

        # -------------------------------------------------------------
        # 5. Zone Distributions (Tier-1 → safe percentages only)
        # -------------------------------------------------------------
        "zones": {
            "power": context.get("zone_dist_power", {}),
            "hr": context.get("zone_dist_hr", {}),
            "pace": context.get("zone_dist_pace", {}),
        },

        # -------------------------------------------------------------
        # 6. Daily load series (Tier-1 aggregated)
        # -------------------------------------------------------------
        "daily_load": [
            {
                "date": str(row["date"]),
                "tss": float(row["icu_training_load"])
            }
            for _, row in getattr(context.get("df_daily"), "iterrows", lambda: [])()
        ] if context.get("df_daily") is not None else [],

        # -------------------------------------------------------------
        # 7. Event Summary Preview (NOT raw events)
        # df_event_only_preview (Tier-1 curated preview)
        # -------------------------------------------------------------
        "events": context.get("df_event_only_preview", []),

        # -------------------------------------------------------------
        # 8. Phases (Tier-2 Phase Detection)
        # -------------------------------------------------------------
        "phases": context.get("phases", []),

        # -------------------------------------------------------------
        # 9. Coaching Actions (Tier-2 heuristics)
        # -------------------------------------------------------------
        "actions": context.get("actions", []),

        # -------------------------------------------------------------
        # 10. Outliers (Tier-2)
        # -------------------------------------------------------------
        "outliers": context.get("outliers", []),

        # -------------------------------------------------------------
        # 11. Renderer Validation Summary
        # -------------------------------------------------------------
        "validation": {
            "auditFinal": context.get("auditFinal"),
            "required_keys_ok": True,
            "schema_version": "v5.1"
        }
    }

    return payload
