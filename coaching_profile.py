#!/usr/bin/env python3
"""
coaching_profile.py — Unified Coaching Profile (v17-Sync)
Structured reference of frameworks, formulas, and methodology anchors. UPD
"""

# coaching_profile.py

REPORT_CONTRACT = {

    "weekly": [
        "meta",

        # 🧭 TRAINING LOAD
        "training_volume",
        "metrics_groups",
        "daily_load",
        "events",
        "planned_events_7d",

        # 🫀 PHYSIOLOGY RESPONSE
        "wellness",
        #"insights", //old - good for wellness report though
        "insight_view",

        # ⚙️ PERFORMANCE INTELLIGENCE
        "performance_intelligence",
        "wbal_summary",

        # 📈 ADAPTATION
        "energy_system_progression",
        "physiology",
        "zones",
        "phases_summary",

        # 🎯 ADAPTIVE DECISIONS
        "actions",
        "event_targets",
        "phase_alignment",
        "training_guidance",
        "decision_context",

        "current_ISO_weekly_microcycle",
        "planned_summary_by_iso_week",
        "future_forecast",
        "future_actions",
        "phases_future"
    ],

    "weekly_lite": [
        "meta",

        # 🧭 TRAINING LOAD
        "training_volume",
        "metrics_groups",
        "events",

        # 🫀 PHYSIOLOGY RESPONSE
        "wellness",
        "insight_view",

        # ⚙️ PERFORMANCE INTELLIGENCE
        "performance_intelligence",

        # 📈 ADAPTATION
        "energy_system_progression",

        # 🎯 ADAPTIVE DECISIONS
        "actions",
        "event_targets",
        "phase_alignment",
        "training_guidance",
        "decision_context",
    ],

    "weekly_overview": [
        "meta",

        # 🧭 TRAINING LOAD / LOAD STATE
        "training_volume",
        "metrics_groups",
        "daily_load",

        # 🫀 PHYSIOLOGY
        "wellness",
        "insight_view",

        # ⚙️ PERFORMANCE INTELLIGENCE
        "performance_intelligence",

        # 📈 ADAPTATION / ESPE
        "energy_system_progression",

        # 🎯 ADE / GOVERNANCE
        "actions",
        "training_guidance",
        "decision_context",
        "event_targets",
        "phase_alignment",

        # 🔮 CURRENT PLAN CONTEXT
        "current_ISO_weekly_microcycle",
        "planned_summary_by_iso_week",
        "future_forecast",
        "future_actions",
        "phases_future",
    ],

    "weekly_workflow": [
        "meta",

        # 1. Training execution vs prescription
        "training_volume",
        "events",
        "planned_events_7d",
        "current_ISO_weekly_microcycle",
        "planned_summary_by_iso_week",

        # 2. Fatigue and recovery trends
        "metrics_groups",
        "daily_load",
        "future_forecast",
        "phases_future",

        # 3. Athlete readiness
        "actions",
        "training_guidance",
        "decision_context",
        "phase_alignment",
        "event_targets",

        # 4. HRV / wellness
        "wellness",
        "insight_view",

        # 5. Weekly performance progression
        "performance_intelligence",
        "energy_system_progression",
        "physiology",
        "zones",
        "phases_summary",
    ],

    "season": [
        "meta",

        # 🧭 TRAINING LOAD
        "training_volume",
        "metrics_groups",
        #"events",
        "trend_metrics",

        # 🫀 PHYSIOLOGY RESPONSE
        "wellness",
        "insight_view",
        "insights",

        # ⚙️ PERFORMANCE INTELLIGENCE
        "performance_intelligence",
        "wbal_summary",

        # 📈 ADAPTATION
        "energy_system_progression",
        "physiology",
        "phases_summary",
        #"phases",
        #"weekly_phases",
        "phases_future",
        
        # 🎯 ADAPTIVE DECISIONS
        "actions",
        "event_targets",
        "current_ISO_weekly_microcycle",
        "planned_summary_by_iso_week",
        "future_forecast",
        "future_actions",
        "phase_alignment",
        "training_guidance",
        "decision_context"
    ],

    "season_lite": [
        "meta",

        # 🧭 TRAINING LOAD
        "training_volume",
        "metrics_groups",
        "trend_metrics",

        # 🫀 PHYSIOLOGY RESPONSE
        "wellness",

        # ⚙️ PERFORMANCE INTELLIGENCE
        "performance_intelligence",

        # 📈 ADAPTATION
        "energy_system_progression",
        "phases_summary",

        # 🎯 ADAPTIVE DECISIONS
        "actions",
        "event_targets",
        "future_forecast",
        "future_actions",
        "phase_alignment",
        "training_guidance",
        "decision_context"
    ],

    "summary": [
        "meta",

        # 🧭 TRAINING LOAD
        "training_volume",
        "outliers",

        # 🫀 PHYSIOLOGY RESPONSE
        "wellness",
        "insights",

        # ⚙️ PERFORMANCE INTELLIGENCE
        "performance_summary",
        "performance_intelligence",

        # 📈 ADAPTATION
        "phases",
        "phases_summary",
        "current_ISO_weekly_microcycle"
    ],


    "wellness": [
        "meta",

        # 🫀 PHYSIOLOGY RESPONSE
        "wellness",
        "wellness_summary",
        "insights",
        "insight_view",

        # ⚙️ PERFORMANCE INTELLIGENCE
        "performance_intelligence"
    ]
}

# ─────────────────────────────────────────────
# PRUNE RULES (exact current manual reductions) INSIDE CONTRACT TYPE
# ─────────────────────────────────────────────

PRUNE_RULES = {
    "weekly": {
        "meta": [
            "methodology",
            "planned_events"
        ],
        "wellness": [
            "hrv_series"
        ],
        "meta.athlete.context": [
            "platforms",
            "wellness_features",
            "equipment_summary",
            "activity_scope",
            "training_environment",
        ],
    },

    "weekly_lite": {
        "wellness": [
            "hrv_series"
        ],
        "meta": [
            "phases_summary",
            "planned_events"
        ],
        "meta.athlete": [
            "profiles",
        ],
        "meta.athlete.context": [
            "platforms",
            "wellness_features",
            "equipment_summary",
            "activity_scope",
            "training_environment",
        ],
    },

    "weekly_overview": {
        "meta": [
            "methodology",
            "planned_events",
            "phases_summary",
            "events",
        ],
        "meta.athlete": [
            "profiles",
        ],
        "meta.athlete.context": [
            "platforms",
            "wellness_features",
            "equipment_summary",
            "activity_scope",
            "training_environment",
        ],
        "wellness": [
            "hrv_series",
            "daily",
        ],
        #"performance_intelligence": [
        #    "acute",
        #   "chronic",
        #],
    },

    "weekly_workflow": {
        "meta": [
            "methodology",
            "planned_events",
        ],
        "wellness": [
            "hrv_series",
            "daily",
        ],
        "meta.athlete": [
            "profiles",
        ],
        "meta.athlete.context": [
            "platforms",
            "wellness_features",
            "equipment_summary",
            "activity_scope",
            "training_environment",
        ],
        "performance_intelligence": [
            "acute",
            "chronic",
        ],
    },

    "season": {
        "wellness": [
            "hrv_series"
        ],
        "meta": [
            "events",
            "planned_events"
        ],
        "meta.athlete.context": [
            "platforms",
            "wellness_features",
            "equipment_summary",
            "activity_scope",
            "training_environment",
        ],
    },

    "season_lite": {
        "wellness": [
            "hrv_series"
        ],
        "meta": [
            "events",
            "planned_events"
        ],
        "meta.athlete": [
            "profiles",
        ],
        "meta.athlete.context": [
            "platforms",
            "wellness_features",
            "equipment_summary",
            "activity_scope",
            "training_environment",
        ],
    },

    "summary": {
        "meta": [
            "events",
            "planned_events"
        ],
        "meta.athlete": [
            "profiles",
        ],
        "wellness": [
            "hrv_series"
        ],
        "meta.athlete.context": [
            "platforms",
            "wellness_features",
            "equipment_summary",
            "activity_scope",
            "training_environment",
        ],
    },
}


RENDERER_PROFILES = {

    # ==============================================================
    # Global rules (apply to ALL report types)
    # ==============================================================
    "global": {
        "hard_rules": [
            "Render exactly ONE report.",
            "All sections MUST appear under their corresponding stack layer header.",
            "Stack layer headers MUST be rendered using the provided stack labels in uppercase.",
            "Do NOT add numeric prefixes to section headers.",
            "Use emoji-based section headers only.",
            "Preserve section order exactly as defined by the contract.",
            "Metric context MUST be derived exclusively from each metric’s `context_window` and `confidence_model` fields.",
            "When both wellness signals and performance_intelligence metrics are present, interpret recovery state as the physiological response to recent training stress. Insights should reconcile these layers rather than repeating them independently."
        ],
        "list_rules": [
            "If a section value is a JSON array (list), render it as a Markdown table.",
            "Render EVERY element in the array.",
            "Preserve one row per array element.",
            "Do NOT summarise the list unless explicitly allowed by section handling.",
            "Do NOT replace lists with prose unless explicitly allowed.",
            "Do NOT omit rows for brevity."
        ],
        "tone_rules": [
            "Keep tone factual, supportive, neutral, and coach-like.",
        ],

        # NEW (presentation only)
        "state_presentation": {
            "enabled": True,
            "style": "single_sentence_banner",
            "source": "semantic_states_only",   # no derivation
        }
    },

    # ==============================================================
    # Weekly workflow CONTRACT
    # ==============================================================

    "weekly_workflow": {
        "framing": {
            "intent": "weekly_workflow_review",
            "purpose": (
                "Render the weekly report around the athlete workflow: "
                "execution vs prescription, fatigue/recovery trends, readiness, "
                "HRV/wellness, and weekly performance progression."
            ),
            "required_opening": (
                "One-line verdict covering execution, recovery, readiness, and progression."
            ),
        },

        "layout": {
            "style": "workflow_review",
            "required_sections": [
                "Training Execution vs Prescription",
                "Fatigue and Recovery Trends",
                "Athlete Readiness",
                "HRV / Wellness",
                "Weekly Performance Progression",
                "Coach Verdict",
            ],
        },

        "stack_structure": {
            "execution_vs_prescription": [
                "training_volume",
                "events",
                "planned_events_7d",
                "current_ISO_weekly_microcycle",
                "planned_summary_by_iso_week",
            ],
            "fatigue_recovery_trends": [
                "metrics_groups.load",
                "metrics_groups.capacity",
                "metrics_groups.variability",
                "daily_load",
                "future_forecast",
                "phases_future",
            ],
            "athlete_readiness": [
                "actions",
                "training_guidance",
                "decision_context",
                "phase_alignment",
                "event_targets",
            ],
            "hrv_wellness": [
                "wellness",
                "insight_view",
            ],
            "weekly_performance_progression": [
                "performance_intelligence",
                "energy_system_progression",
                "physiology",
                "zones",
                "phases_summary",
            ],
        },

        "stack_labels": {
            "execution_vs_prescription": "📋 TRAINING EXECUTION VS PRESCRIPTION",
            "fatigue_recovery_trends": "🧭 FATIGUE AND RECOVERY TRENDS",
            "athlete_readiness": "🎯 ATHLETE READINESS",
            "hrv_wellness": "🫀 HRV / WELLNESS",
            "weekly_performance_progression": "📈 WEEKLY PERFORMANCE PROGRESSION",
        },

        "interpretation_rules": [
            "Render exactly one workflow report.",
            "Use the five workflow headings exactly as defined in stack_labels.",
            "Do not render generic Montis stack headings in this profile.",
            "Start with a one-line verdict covering execution, fatigue, readiness, wellness, and progression.",
            "Training Execution vs Prescription MUST compare completed events against planned_events_7d when both exist.",
            "If planned_events_7d is missing, state that prescription comparison is unavailable; do not infer it.",
            "Fatigue and Recovery Trends MUST use metrics_groups.load, metrics_groups.capacity, daily_load, and future_forecast where present.",
            "Athlete Readiness MUST use adaptive_summary from actions, training_guidance, decision_context, phase_alignment, and event_targets.",
            "Do not use actions[0] blindly; find the action where type == adaptive_summary.",
            "HRV / Wellness MUST use wellness.physiology_state, HRV ratio/trend, resting HR delta, sleep, and insight_view where present.",
            "Weekly Performance Progression MUST use performance_intelligence and energy_system_progression as the primary sources.",
            "Do not recompute ADE score, CTL, ATL, TSB, ACWR, HRV ratio, or ESPE deltas.",
            "When phase governance conflicts with apparent readiness, state both truths clearly.",
            "Final Coach Verdict MUST classify the week as Productive, High Strain, Under-Recovered, or Misaligned.",
        ],

        "section_handling": {
            "meta": "summary",
            "training_volume": "summary",
            "events": "summary",
            "planned_events_7d": "summary",
            "current_ISO_weekly_microcycle": "summary",
            "planned_summary_by_iso_week": "summary",

            "metrics_groups": "summary",
            "daily_load": "compact_timeline",
            "future_forecast": "summary",

            "actions": "summary",
            "training_guidance": "headline",
            "decision_context": "headline",
            "phase_alignment": "headline",
            "event_targets": "summary",

            "wellness": "summary",
            "insight_view": "summary",

            "performance_intelligence": "summary",
            "energy_system_progression": "summary",
            "physiology": "summary",
            "zones": "summary",
            "phases_summary": "summary",

            "phases": "forbid",
            "insights": "forbid",
            "wbal_summary": "forbid",
        },

        "preferred_markdown_shape": [
            "Opening one-line verdict.",
            "## 📋 Training Execution vs Prescription",
            "Compact comparison: completed load, planned load, missed/extra sessions, prescription alignment.",
            "## 🧭 Fatigue and Recovery Trends",
            "Compact load/fatigue table plus daily_load timeline.",
            "## 🎯 Athlete Readiness",
            "ADE score, operational state, phase alignment, event readiness, final guidance.",
            "## 🫀 HRV / Wellness",
            "HRV, resting HR, sleep, physiology state, wellness signal interpretation.",
            "## 📈 Weekly Performance Progression",
            "Performance intelligence, durability, neural density, W′/anaerobic signal, ESPE progression.",
            "## ✅ Coach Verdict",
            "One short verdict with next action.",
        ],

        "closing_note": {
            "required": True,
            "verdict_rule": (
                "State whether the week matched the intended prescription and whether the athlete is ready to progress."
            ),
            "classification_required": [
                "Productive",
                "High Strain",
                "Under-Recovered",
                "Misaligned",
            ],
            "focus": "workflow_alignment",
            "anchor_metrics": [
                "events",
                "planned_events_7d",
                "ACWR",
                "FatigueTrend",
                "wellness.physiology_state",
                "performance_intelligence.training_state",
                "energy_system_progression",
                "actions",
                "phase_alignment",
            ],
            "intent_rule": (
                "Assess whether execution, fatigue, wellness, and progression support the next training decision."
            ),
            "max_sentences": 4,
        },
    },

    "weekly_overview": {
        "framing": {
            "intent": "bento_weekly_overview",
            "purpose": "Compact ChatGPT weekly dashboard. Summarise, do not expand into full report.",
            "required_opening": "One-line state summary combining physiology + governance."
        },

        "layout": {
            "style": "compact_dashboard",
            "columns": 2,
            "max_cards": 6,
            "card_order": [
                "athlete_context",
                "adaptive_decision_engine",
                "training_load",
                "physiology_reserve",
                "performance_intelligence",
                "adaptation_progression"
            ],
            "required_sections": [
                "Athlete Context",
                "Adaptive Decision Engine",
                "Weekly Load",
                "Physiology",
                "Adaptation",
                "Decision / Event Focus"
            ]
        },

        "card_rules": {
            "athlete_context": [
                "This card MUST be rendered first.",
                "Use meta.athlete.identity and meta.athlete.profile.",
                "Show athlete name, primary_sport, dominant_sport.",
                "Show FTP, eFTP, FTP/kg, LTHR, max HR, VO2max Garmin when present.",
                "Show lactate_mmol_l and lactate_power when present.",
                "Preferred format: compact table.",
                "Do not render full athlete profile, full context, platforms, equipment, or activity_scope."
            ],
            "adaptive_decision_engine": [
                "This card MUST be rendered immediately after Athlete Context.",
                "Use actions item where type == adaptive_summary; do not assume actions[0] unless it matches adaptive_summary.",
                "Use training_guidance as the final coaching directive when present.",
                "Do not replace the card title with taper/override text.",
                "Card title must remain: ADAPTIVE DECISION ENGINE.",
                "MUST render ADE score from adaptive_summary.ade_base_score.value and adaptive_summary.ade_base_score.label.",
                "Preferred score format: '62 / 100 — CAUTION'.",
                "Do not recompute ADE score.",
                "MUST render operational_state.",
                "MUST render resolution.",
                "MUST render phase_constraint or decision_context.required_phase.",
                "MUST render phase_alignment or decision_context.alignment.",
                "MUST render forecast_context and load_trend when present.",
                "If resolution == overridden_by_phase, show phase override state clearly inside the card.",
                "If taper_governance.state == taper_load_conflict, show conflict reason and recommended adjustment.",
                "Show both truths: physiology state and plan governance, e.g. LOAD ACCEPTING + TAPER MISALIGNED.",
                "Do not present adaptive_summary.directive as fully honoured when resolution == overridden_by_phase."
            ],

            "training_load": [
                "Use training_volume and metrics_groups.load.",
                "Show weekly hours, total TSS, distance.",
                "Show CTL / ATL / TSB if present from training_volume.",
                "Show ACWR, StressTolerance, Strain, Monotony and FatigueTrend when present.",
                "Show load_pattern label/status if present.",
                "Show compact 7d daily_load trajectory if present.",
                "Do not list all events in overview mode."
            ],

            "physiology_reserve": [
                "Use wellness.physiology_state and wellness summary fields.",
                "Show HRV ratio, sleep score, resting HR delta if present.",
                "Use performance_intelligence.training_state.signals if needed for HRV/ATL/CTL context.",
                "Use insight_view only for critical/watch/positive summary counts or short labels.",
                "Do not render HRV series.",
                "Mention heat/external load only if performance_intelligence.external_load_context is present."
            ],

            "performance_intelligence": [
                "Use performance_intelligence.training_state as the headline.",
                "Show readiness_signal, operational_state, load_recovery_state.",
                "Show external_load_context if present: heat/load/cardiac drift.",
                "Do not render full WDRM/ISDM/NDLI tables in overview mode.",
                "If durability drift is present, mention it as a limiter."
            ],

            "adaptation_progression": [
                "Use energy_system_progression.",
                "Show dominant sport, adaptation_state/system_state, and system_guidance.",
                "Show key direction only: threshold, VO2, sprint, durability, repeatability if present.",
                "Keep message short; truncate only visually, not in data."
            ],

            "decision_event_focus": [
                "Use event_targets.next_event when present.",
                "Show next A/B/C event name, date, days_to_event, event_demand or race_type.",
                "Use training_guidance as the final action line.",
                "If taper_governance.recommended_adjustment exists, show it as the action.",
                "End with reflection question only if actions contains type == reflection."
            ]
        },

        "required_fields": {
            "athlete_context": [
                "meta.athlete.identity.name",
                "meta.athlete.profile.primary_sport",
                "meta.athlete.profile.dominant_sport",
                "meta.athlete.profile.ftp",
                "meta.athlete.profile.eftp",
                "meta.athlete.profile.ftp_kg",
                "meta.athlete.profile.lthr",
                "meta.athlete.profile.max_hr",
                "meta.athlete.profile.vo2max_garmin",
                "meta.athlete.profile.lactate_mmol_l",
                "meta.athlete.profile.lactate_power"
            ],
            "adaptive_decision_engine": [
                "adaptive_summary.ade_base_score.value",
                "adaptive_summary.ade_base_score.label",
                "adaptive_summary.operational_state",
                "adaptive_summary.resolution",
                "adaptive_summary.phase_constraint",
                "adaptive_summary.phase_alignment",
                "adaptive_summary.forecast_context",
                "adaptive_summary.load_trend",
                "training_guidance"
            ],
            "taper_conflict_if_present": [
                "adaptive_summary.taper_governance.state",
                "adaptive_summary.taper_governance.reason",
                "adaptive_summary.taper_governance.recommended_adjustment"
            ]
        },

        "preferred_markdown_shape": [
            "Opening one-line summary.",
            "## 👤 Athlete Context",
            "Compact athlete table showing name, sport, FTP, eFTP, FTP/kg, LTHR, max HR, VO2max Garmin, lactate power if present.",
            "## 🎯 Adaptive Decision Engine",
            "ADE score table including score, state, resolution, required phase, alignment, forecast trend.",
            "Final guidance line using training_guidance.",
            "Conflict line if taper_governance exists.",
            "## 🧭 Weekly Load",
            "Compact load table.",
            "## 🫀 Physiology",
            "Compact physiology table.",
            "## 📈 Adaptation",
            "Compact adaptation table.",
            "## 🎯 Decision / Event Focus",
            "Action and next event."
        ],

        "override_rules": [
            "If decision_context.phase_override is true, training_guidance is the final directive.",
            "If adaptive_summary.resolution == overridden_by_phase, do not present ADE directive as fully honoured.",
            "Precedence for final directive: training_guidance > adaptive_summary.taper_governance.recommended_adjustment > adaptive_summary.directive.",
            "Positive readiness must be qualified when plan governance is misaligned.",
            "If physiology is load_accepting but phase_alignment is misaligned, state both clearly.",
            "If taper_governance.state == taper_load_conflict, the overview must say the plan is misaligned with taper freshness."
        ],

        "section_handling": {
            "events": "forbid",
            "planned_events_7d": "forbid",
            "phases": "forbid",
            "phases_summary": "forbid",
            "zones": "forbid",
            "daily_load": "compact_timeline",
            "metrics_groups": "summary",
            "wellness": "summary",
            "performance_intelligence": "summary",
            "energy_system_progression": "summary",
            "actions": "summary",
            "training_guidance": "headline",
            "decision_context": "headline",
            "future_forecast": "summary",
            "event_targets": "summary"
        },

        "forbidden_behaviour": [
            "Do not omit ADE score.",
            "Do not render a full event list.",
            "Do not render full zones.",
            "Do not render full phase tables.",
            "Do not render full PI metric tables.",
            "Do not say the plan is simply fine when resolution == overridden_by_phase.",
            "Do not use actions[0] blindly if adaptive_summary is elsewhere in actions."
        ]
    },

    # ==============================================================
    # Weekly report (FULL DETAIL, SESSION-LEVEL)
    # ==============================================================
    "weekly": {
        "stack_structure": {
            "meta_context": [
                "meta",
            ],
            "training_load": [
                "training_volume",
                "metrics_groups.load",
                "metrics_groups.intensity",
                "metrics_groups.variability",
                "metrics_groups.metabolic",
                "metrics_groups.capacity",
                "daily_load",
                "events",
                "planned_events_7d",
            ],

            "physiology_response": [
                "wellness",
                "insight_view",
                "performance_intelligence.external_load_context"
            ],

            "performance_intelligence": [
                "performance_intelligence",
                "wbal_summary"
            ],

            "adaptation": [
                "energy_system_progression",
                # physiological calibration
                "physiology",
                "zones",
                "phases_summary"
            ],

            "adaptive_decisions": [
                "actions",
                "event_targets",
                "phase_alignment",
                #"decision_context",
                "planned_summary_by_date",
                "current_ISO_weekly_microcycle",
                "planned_summary_by_iso_week",
                "future_forecast",
                "future_actions",
                "training_guidance",
                "future_phases"
            ]
        },
        "stack_labels": {
            "meta_context": "📊 REPORT CONTEXT",
            "training_load": "🧭 TRAINING LOAD",
            "physiology_response": "🫀 PHYSIOLOGY RESPONSE",
            "performance_intelligence": "⚙️ PERFORMANCE INTELLIGENCE",
            "adaptation": "📈 ADAPTATION",
            "adaptive_decisions": "🎯 ADAPTIVE DECISIONS"
        },
        "coaching_sentences": {
            "enabled": True,
            "max_per_section": 5,
            "placement": "after_data"
        },
        "interpretation_rules": [
            "Interpretations must be descriptive/conditional, not predictive.",
            "Render all meta.athlete.identity and always notes in REPORT CONTEXT when present",
            "Render training_volume as: Hours | TSS | Distance when present.",
            "Render wbal_summary.temporal_pattern as a 1-line block timeline (▂ ▃ ▇ → none/low/moderate/high).",
            "Render daily_load as fixed-width timeline (labels, blocks, TSS aligned). NEVER list/table.",
            "If daily_load + CTL + ATL exist, add fatigue row (↑ ↓ —) using sign(ATL−CTL) only.",
            "Daily_load rows must use fixed-width columns for alignment.",
            "EVENTS icons require a single legend line under the section header.",
            "Render zone distributions as fixed-width ASCII bars with exact % (no derived metrics).",
            "If lactate_calibration.available, show mean, latest, samples, LT1 (no derivation).",
            "Render performance_intelligence as WDRM / ISDM / NDLI only (no recompute/merge).",
            "If high_dep_sessions>0 AND high_drift_sessions>0 → note neuromuscular+metabolic overlap.",
            "Cross-section interpretation allowed when describing same physiology.",
            "When energy_system_progression exists: If delta_percent is null → describe as 'baseline established' with no adaptation direction. If delta_percent exists → summarise adaptation direction using system_status and adaptation_state.",
            "Prioritise ESPE signals when delta_percent exists; otherwise treat ESPE as baseline reference only.",
            "Render power anchors as [<power> W](link) when activity_link exists, else plain.",
            "Title current_ISO_weekly_microcycle as 'Current ISO Week ## (Mon-Sun)'.",
            "If a section is marked full, render every entity and field exactly as present in the semantic data",
            "If actions[0].resolution == 'overridden_by_phase':",
            "- required_phase overrides ADE directive in interpretation.",
            "- Any positive load statement MUST be qualified by fatigue/phase context.",
            "- Do NOT present training as fully acceptable without qualification.",
            "Precedence: required_phase > ADE.directive > performance_intelligence.training_state > metrics.",
            # ADAPTIVE DECISIONS
            "Render adaptive_decisions as compact dashboard tables (no narrative).",
            "adaptive_decisions MUST be rendered as STATE, OPERATIONS, TRAINING_GUIDANCE, PHASE ALIGNMENT, DECISION CONTEXT, FUTURE ACTIONS, PHASES SUMMARY and EVENT TARGETS (where it exists) tables.",
            "STATE MUST NOT exceed 4 columns per table.",
            "STATE MUST be split into multiple tables when more than 4 fields are present.",
            "STATE tables MUST follow this fixed grouping:",
            "STATE SNAPSHOT: ADE directive, state, resolution, load_trend.",
            "ADAPTATION RESPONSE: adaptation_focus, key_constraint, next_action, dominant_signal.",
            "OPERATIONS table MUST contain week_delta, planned_load (current → next), and 14 day forecast summary (CTL / TSB / fatigue_class).",
            "training_guidance MUST be rendered as a single-row table with column: Directive.",
            "phase_alignment MUST be rendered as a single-row table with columns: Required Phase, Recent Load Alignment, Past Pattern, Phase Streak.",
            "When actions[0].ade_base_score exists, render it in Adaptive Decisions before STATE SNAPSHOT as: ADE SCORE | Score | Label | Scope | Penalties. Use backend values only; do not recompute; do not merge with phase_alignment/resolution.",
            #"decision_context MUST be rendered as a single-row table with columns: ADE Directive, Phase Requirement, Alignment",
            "future_actions MUST be rendered as a table with columns: Priority, Action, Reason.",
            "Do NOT render state_action, system_guidance, or reflection as separate sections.",
            "Do NOT render paragraph explanations for adaptive_decisions.",
            #ADAPTATION
            "phases_summary MUST be rendered as a compact table (max 4 rows) with columns: Phase, Duration, Trend",
            "Phases should always be sequential dated phases",
            "energy_system_progression MUST be rendered as compact adaptation table(s); when Ride fatigue_resistance exists, render only one summary row for eack after_kj with evaluated kJ, state, limiter, current/previous retention, change, trend and confidence, excluding fatigued_power_w.",
            "Table MUST include key systems (aerobic, threshold, vo2, anaerobic) and overall phase/adaptation_state.",
            "lactate_calibration when available MUST be rendered as a single compact adaptation table before suppression.",
            "Do NOT render narrative or subsection breakdown when table is present.",
            #PERFORMANCE INTELLIGENCE
            "performance_intelligence MUST be rendered as compact dashboard tables (may be split if too wide).",
            "WDRM, ISDM, and NDLI MUST NOT be rendered as separate sections when sufficient data exists.",
            "They MUST be projected into a SYSTEM STATE table and a LOAD SIGNATURE table.",
            "performance_intelligence MUST include operational_state in the SYSTEM STATE table.",
            "operational_state MUST be rendered as the primary state indicator (first column).",
            "All original semantic values MUST still be represented (no omission).",
            "Do NOT summarise or drop metrics — only change layout.",
            "If a table has more than 4 columns, split it into multiple tables (max 4 columns each).",
            "When a group contains a resolved 'state' field, it MUST be used as the sole authoritative interpretation. Do NOT infer or recompute interpretation from underlying metrics.",
            "Metrics may be displayed for context, but MUST NOT define or override narrative conclusions when a state is present."
        ],
        "allowed_enrichment": [
            "Restate semantic interpretation fields.",
            "Explain what a value indicates within its known threshold or state.",
            "derive_stepwise_forecast"
        ],
        "section_handling": {
            "meta": "full",
            "training_volume": "full",
            "events": "full",
            "planned_events_7d": "full",
            "current_ISO_weekly_microcycle": "forbid",
            "daily_load": "full",
            "metrics_groups": "table_summary",
            "performance_intelligence": "full",
            "energy_system_progression": "full",
            "zones": "forbid",
            "physiology": "full",
            "wellness": "summary",
            "phases": "forbid",
            "phase_alignment": "headline",
            "decision_context": "headline",
            "phases_summary": "summary",
            #"planned_events": "forbid",
            #"planned_summary_by_date": "forbid",
            "planned_summary_by_iso_week": "forbid",
            "actions": "table_summary",
            "event_targets": "table_summary",
            "actions.0": "full",
            "actions.0.ade_base_score": "full",
            "actions.0.adaptive_summary": "full",
            "actions.1.state_action": "full",
            "actions.3.system_guidance": "full",
            "actions.4.reflection": "full",
            "training_guidance": "headline",
            "future_forecast": "forbid",
            "future_actions": "full",
            "insights": "forbid",
            "insight_view": "summary"
        },

        "emphasis": {
            "metrics_groups": "high",
            "actions": "high",
            "events": "medium",
            "wellness": "medium",
            "adaptation": "high",
            "phases_summary": "low"
        },

        "events_rule": {
            "column_order": [
                "Date",
                "Activity",
                "Duration (min)",
                "Distance",
                "TSS",
                "IF",
                "NP",
                "HRR60"
            ],

            "duration_conversion": [
                "The semantic field `duration_seconds` MUST be converted to minutes at render time.",
                "This conversion applies ONLY to duration.",
                "Display as integer minutes by default.",
                "Use one decimal only if duration < 30 minutes and precision is useful.",
                "Label column as Duration (min). Show HRR60 column when values exist."
            ],

            "icons": [
                "⚡ Efficient (optimal efficiency factor)",
                "🟢 Aerobic (low IF with stable decoupling)",
                "💥 Anaerobic (heavy W′ engagement)",
                "🔁 Repeated (repeated W′ depletion pattern)",
                "📈 Progressive (progressive W′ engagement)",
                "🧘 Recovery (very low intensity recovery session)",
                "❤️ Heart_rate_recovery_60s (Heart Rate Recovery within 60s)"
            ],

            "rules": [
                "Render EVENTS as a Markdown table only.",
                "1 event = 1 row; no omissions.",
                "No summarising, grouping, renaming, or narrative text.",
                "Coaching sentences (if any) appear AFTER the table.",
                "Use fixed column order.",
                "Icons: prefix in Activity column from semantic fields; multiple allowed; fixed order.",
                "Icons are additive only (no replacement/suppression of values or rows).",
                "Append rpe_emoji + feel_emoji to TSS.",
                "If activity_link exists, render as [name](link) with icons before link.",
                "Render a single legend line directly below the table."
            ]
        },

        "planned_events_rule": [
            "The planned_events_7d section MUST be rendered as a Markdown table.",
            "Each planned event MUST appear as exactly one row."
            "Column order MUST be: Date | Day | Name | Category | Duration (min) | TSS | CTL | ATL",
            "Do NOT summarise, group, or narrate planned events.",
            "Coaching sentences for planned_events, if enabled, MUST appear AFTER the table."
        ],

        "framing": {
            "intent": "tactical_weekly_control"
        },
        "question_rule": {
            "fatigue",
            "adaptation",
            "training load",
            "perceived exertion (RPE / feel)"
        },
        "closing_note": {
            "required": True,
            "verdict_rule": "State clearly whether last week’s training load was handled appropriately.",
            "classification_required": [
                "Productive",
                "High Strain",
                "Overreached"
            ],
            "focus": "tactical_alignment",
            "anchor_metrics": [
                "ACWR",
                "FatigueTrend",
                "NDLI",
                "Durability",
                "performance_intelligence.training_state",
                "energy_system_progression",
                "actions"

            ],
            "intent_rule": "Assess whether acute load and recovery state align with immediate training intent.",
            "max_sentences": 4
        },
        "post_render": {
            "explore_deeper": {
                "enabled": True,
                "style": "command_suggestions",
                "placement": "after_report",
                "commands": [
                    "show full physiology_response",
                    "show full performance_intelligence",
                    "show full adaptation",
                    "show full adaptive_decisions",
                    "load planned events",
                    "show power curves",
                    "load athlete profiles",
                    "load last activity and analyse",
                    "show me more command questions"
                ]
            }
        }
    },

    # ==============================================================
    # Season report (PHASE-LEVEL, STRATEGIC)
    # ==============================================================
    "season": {
        "stack_structure": {
            "meta_context": [
                "meta",
            ],
            "training_load": [
                "training_volume",
                "metrics",
                "trend_metrics",
                "phases_future"            ],

            "physiology_response": [
                "wellness",
                "insights_view",
                "performance_intelligence.external_load_context"
            ],

            "performance_intelligence": [
                "performance_intelligence",
                "wbal_summary"
            ],

            "adaptation": [
                "energy_system_progression",
                "physiology",
                "phases",
                "phases_summary"
            ],

            "adaptive_decisions": [
                "actions",
                "event_targets",
                "current_ISO_weekly_microcycle",
                "planned_summary_by_iso_week",
                "future_forecast",
                "future_actions",
                "phase_alignment",
                "training_guidance",
                #"decision_context"
            ]
        },

        "stack_labels": {
            "meta_context": "📊 REPORT CONTEXT",
            "training_load": "🧭 TRAINING LOAD",
            "physiology_response": "🫀 PHYSIOLOGY RESPONSE",
            "performance_intelligence": "⚙️ PERFORMANCE INTELLIGENCE",
            "adaptation": "📈 ADAPTATION",
            "adaptive_decisions": "🎯 ADAPTIVE DECISIONS"
        },

        "coaching_sentences": {
            "enabled": True,
            "max_per_section": 5,
            "placement": "after_data"
        },
        "interpretation_rules": [
            "Render all meta.athlete.identity and always notes in REPORT CONTEXT when present",
            "If semantic.training_volume exists, render it under the header 'Training Volume' with three stacked metrics: Hours, Training Load (TSS), Distance.",
            "Focus on trends, phases, and accumulated load.",
            "Avoid session-level or daily commentary.",
            "If performance_intelligence exists, render chronic signals (90d) first, then acute signals (7d). Emphasise contrast between long-term capacity and current stress.",
            "Interpretation may combine signals across sections when they describe the same physiological process (e.g. fatigue, adaptation, durability).",
            "When energy_system_progression exists: If delta_percent is null → describe as 'baseline established' with no adaptation direction. If delta_percent exists → summarise adaptation direction using system_status and adaptation_state.",
            "Insights SHOULD prioritise adaptation signals (ESPE) before repeating metric definitions.",
            "Ensure current_ISO_weekly_microcycle is totled as 'Current ISO Week ## (Mon-Sun)'",
            "If actions[0].resolution == 'overridden_by_phase':",
            "- required_phase overrides ADE directive in interpretation.",
            "- Any positive load statement MUST be qualified by fatigue/phase context.",
            "- Do NOT present training as fully acceptable without qualification.",
            "Precedence: required_phase > ADE.directive > performance_intelligence.training_state > metrics.",
            # ADAPTIVE DECISIONS
            "Render adaptive_decisions as compact dashboard tables (no narrative).",
            "adaptive_decisions MUST be rendered as STATE, OPERATIONS, TRAINING_GUIDANCE, PHASE ALIGNMENT, DECISION CONTEXT, FUTURE ACTIONS, PHASES SUMMARY and EVENT TARGETS (where it exists) tables.",
            "STATE MUST NOT exceed 4 columns per table.",
            "STATE MUST be split into multiple tables when more than 4 fields are present.",
            "STATE tables MUST follow this fixed grouping:",
            "STATE SNAPSHOT: ADE directive, state, resolution, load_trend.",
            "ADAPTATION RESPONSE: adaptation_focus, key_constraint, next_action, dominant_signal.",
            "OPERATIONS table MUST contain week_delta, planned_load (current → next), and 14 day forecast summary (CTL / TSB / fatigue_class).",
            "training_guidance MUST be rendered as a single-row table with column: Directive.",
            "phase_alignment MUST be rendered as a single-row table with columns: Required Phase, Recent Load Alignment, Past Pattern, Phase Streak.",
            #"decision_context MUST be rendered as a single-row table with columns: ADE Directive, Phase Requirement, Alignment",
            "future_actions MUST be rendered as a table with columns: Priority, Action, Reason.",
            "Do NOT render state_action, system_guidance, or reflection as separate sections.",
            "Do NOT render paragraph explanations for adaptive_decisions.",
            #ADAPTATION
            "phases_summary MUST be rendered as a compact table (max 4 rows) with columns: Phase, Duration, Trend",
            "Phases should always be sequential dated phases",
            "energy_system_progression MUST be rendered as compact adaptation table(s); when Ride fatigue_resistance exists, render only one summary row per after_kj with evaluated kJ, state, limiter, current/previous retention, change, trend and confidence, excluding fatigued_power_w.",
            "Table MUST include key systems (aerobic, threshold, vo2, anaerobic) and overall phase/adaptation_state.",
            "lactate_calibration when available MUST be rendered as a single compact adaptation table before suppression.",
            "Do NOT render narrative or subsection breakdown when table is present.",
            #PERFORMANCE INTELLIGENCE
            "performance_intelligence MUST be rendered as compact dashboard tables (may be split if too wide).",
            "WDRM, ISDM, and NDLI MUST NOT be rendered as separate sections when sufficient data exists.",
            "They MUST be projected into a SYSTEM STATE table and a LOAD SIGNATURE table.",
            "performance_intelligence MUST include operational_state in the SYSTEM STATE table.",
            "operational_state MUST be rendered as the primary state indicator (first column).",
            "All original semantic values MUST still be represented (no omission).",
            "Do NOT summarise or drop metrics — only change layout.",
            "If a table has more than 4 columns, split it into multiple tables (max 4 columns each).",
            "When a group contains a resolved 'state' field, it MUST be used as the sole authoritative interpretation. Do NOT infer or recompute interpretation from underlying metrics.",
            "Metrics may be displayed for context, but MUST NOT define or override narrative conclusions when a state is present."
        ],
        "allowed_enrichment": [
            "Restate phase descriptors already present in semantic data."
        ],
        "section_handling": {
            "meta": "full",
            "training_volume": "full",
            "events": "forbid",
            "daily_load": "forbid",
            "weekly_phases": "forbid",
            "phases": "forbid",
            "phase_alignment": "headline",
            "decision_context": "headline",
            "phases_summary": "summary",
            "metrics_groups": "table_summary",
            "performance_intelligence": "full",
            "current_ISO_weekly_microcycle": "forbid",
            "planned_summary_by_iso_week": "forbid",
            "future_forecast": "forbid",
            "energy_system_progression": "summary",
            "physiology": "summary",
            "wellness": "headline",
            "actions": "full",
            "event_targets": "table_summary",
            "future_actions": "full",
            "insights": "forbid",
            "insight_view": "summary",
        },

        "emphasis": {
            "metrics": "high",
            "actions": "high",
            "events": "medium",
            "wellness": "medium",
            "adaptation": "high",
            "phases_summary": "high",
            "trend_metrics": "high"
        },

        "framing": {
            "intent": "medium_term_block_assessment"
        },
        "question_rule": {
            "adaptation",
            "training progression",
            "durability",
            "fatigue accumulation"
        },
        "closing_note": {
            "required": True,
            "verdict_rule": "Classify the training block adaptation trajectory.",
            "classification_required": [
                "Adaptive Growth",
                "Adaptive Maintenance",
                "Adaptive Saturation"
            ],
            "focus": "adaptation_trajectory",
            "anchor_metrics": [
                "load_trend",
                "fitness_trend",
                "fatigue_trend",
                "Efficiency_Factor",
                "Fatigue_Resistance",
                "phases_summary",
                "performance_intelligence.chronic",
                "performance_intelligence.acute",
                "performance_intelligence.training_state",
                "actions",
                "energy_system_progression",
            ],
            "intent_rule": "Determine whether the training block reflects expansion, consolidation, or plateau.",
            "max_sentences": 6
        },
        "post_render": {
            "explore_deeper": {
                "enabled": True,
                "style": "command_suggestions",
                "placement": "after_report",
                "commands": [
                    "show full physiology_response",
                    "show full performance_intelligence",
                    "show full adaptation",
                    "show full adaptive_decisions",
                    "load planned events",
                    "show power curves",
                    "load athlete profiles",
                    "load last activity and analyse",
                    "show me more command questions"
                ]
            }
        }
    },

    # ==============================================================
    # Wellness report (URF v5.2 — SIGNAL-FIRST, MULTI-LAYER RECOVERY)
    # ==============================================================
    
    "wellness": {

        "stack_structure": {
            "meta_context": [
                "meta",
            ],
            "physiology_response": [
                "wellness",
                "insight_view",
                "insights"
            ],

            "performance_intelligence": [
                "performance_intelligence",
                "performance_intelligence.nutrition"
            ]
        },

        "stack_labels": {
            "meta_context": "📊 REPORT CONTEXT",
            "physiology_response": "🫀 PHYSIOLOGY RESPONSE",
            "performance_intelligence": "⚙️ TRAINING STRESS CONTEXT"
        },

        "coaching_sentences": {
            "enabled": True,
            "max_per_section": 4,
            "placement": "after_data"
        },

        # ----------------------------------------------------------
        # Signal hierarchy (used by prompt builder)
        # ----------------------------------------------------------

        "signal_hierarchy": [
            "Autonomic signals (HRV, HRV stability, resting HR, sleep)",
            "Load context (CTL, ATL, TSB)",
            "Training stress mechanisms (from performance_intelligence: neural density, durability drift, anaerobic depletion)"
        ],

        # ----------------------------------------------------------
        # Interpretation rules
        # ----------------------------------------------------------

        "interpretation_rules": [
            "Render all meta.athlete.identity and always notes in REPORT CONTEXT when present",
            "Interpret recovery primarily using autonomic and subjective signals (HRV, resting HR, sleep, subjective recovery scores).",
            "Prioritise autonomic signals over training load metrics when determining recovery state.",
            "Explain HRV behaviour using trends, means, variability, and recent values relative to baseline.",
            "Use CTL, ATL, and TSB only as contextual load indicators, not as primary fatigue determinants.",
            "Avoid day-by-day narration when aggregates or trends exist.",
            "When HRV remains stable despite elevated ATL, describe this as maintenance-under-load adaptation.",
            "When autonomic signals disagree with load signals, prioritise autonomic interpretation.",
            "Performance intelligence metrics must only provide context explaining training stress exposure.",
            "performance_intelligence MUST be rendered as a single LOAD CONTEXT table (max 3 columns).",
            "Do NOT render narrative interpretation for performance_intelligence.",
            "wellness MUST be rendered as STATE and SIGNALS tables before any interpretation.",
            "Include in SIGNALS table wellness.recovery_markers",
            "STATE table MUST summarise HRV, resting HR, sleep, load context, and recovery_state.",
            "SIGNALS table MUST list key metrics with value and qualitative signal (green/amber/red).",
            "Interpretation MUST be ≤3 bullet points (no paragraphs).",
            "insight_view MUST be merged into SIGNALS or INTERPRETATION (not separate section).",
        ],

        # ----------------------------------------------------------
        # Allowed enrichment
        # ----------------------------------------------------------

        "allowed_enrichment": [
            "Summarise HRV behaviour using peaks, troughs, variability, and clustering.",
            "Explain physiological meaning of HRV suppression relative to personal baseline.",
            "Describe maintenance-under-load states when CTL≈ATL and HRV is stable.",
            "Explain interaction between HRV behaviour and training load.",
            "Include sleep and resting heart rate analysis when available.",
            "Highlight absence of subjective recovery data when relevant.",
            "Describe possible neural or durability fatigue only when supported by insight metrics.",
            "Reference performance_intelligence stress metrics when explaining recovery tolerance."
        ],

        # ----------------------------------------------------------
        # Section rendering
        # ----------------------------------------------------------

        "section_handling": {
            "meta": "full",
            "wellness": "full",
            "wellness.recovery_markers": "full",
            "hrv_daily": "forbid",
            "performance_intelligence": "headine",
            "performance_intelligence.nutrition": "full",
            "insights": "forbid",
            "insight_view": "forbid",
            "events": "forbid",
            "daily_load": "forbid",
            "metrics": "forbid",
            "zones": "forbid",
            "phases": "forbid"
        },

        # ----------------------------------------------------------
        # Narrative emphasis
        # ----------------------------------------------------------

        "emphasis": {
            "wellness": "high",
            "insights": "high",
            "autonomic_signals": "high",
            "performance_intelligence": "low",
            "performance_intelligence.training_state:": "high",
            "load_context": "low",
            "stress_mechanisms": "low"
        },

        # ----------------------------------------------------------
        # Framing intent
        # ----------------------------------------------------------

        "framing": {
            "intent": "recovery_signal_interpretation",
            "model": "multi_layer_recovery"
        },

        # ----------------------------------------------------------
        # Fatigue interpretation guardrails
        # ----------------------------------------------------------

        "fatigue_logic": [
            "Do not infer fatigue from load metrics alone.",
            "Autonomic suppression combined with elevated ATL indicates recovery pressure.",
            "Stable HRV despite elevated ATL indicates productive adaptation under load."
        ],
        "question_rule": {
            "recovery",
            "fatigue perception",
            "sleep quality",
            "morning readiness"
        },

        # ----------------------------------------------------------
        # Closing note
        # ----------------------------------------------------------

        "closing_note": {

            "required": True,

            "classification_required": [
                "Adapting Well",
                "Adaptation Under Pressure",
                "Maladaptation Risk"
            ],

            "verdict_rule":
                "State clearly whether current recovery status supports or constrains ongoing training.",

            "focus": "recovery_validation",

            "anchor_metrics": [
                "HRV",
                "HRV_stability",
                "Autonomic_ratio",
                "Resting_HR_delta",
                "Sleep_score",
                "CTL",
                "ATL",
                "TSB",
                "performance_intelligence"
            ],

            "intent_rule":
                "Assess whether autonomic and recovery markers support or constrain training intent.",

            "exact_sentences": 5,

            "sentence_structure": [
                "1. State classification.",
                "2. Describe HRV behaviour relative to baseline.",
                "3. Describe interaction with CTL, ATL, and TSB.",
                "4. Explain physiological meaning (autonomic balance or strain).",
                "5. Translate into plain language (how the body is coping).",
                "6. Provide concrete guidance for the next 24–72 hours."
            ]
        },
        "post_render": {
            "explore_deeper": {
                "enabled": True,
                "style": "command_suggestions",
                "placement": "after_report",
                "commands": [
                    "show full physiology_response",
                    "show full training stress",
                    "show me more wellness command questions"
                ]
            }
        }
    },

    # ==============================================================
    # Summary report (ANNUAL / EXECUTIVE)
    # ==============================================================
    "summary": {
        "stack_structure": {

            "meta_context": [
                "meta"
            ],

            "training_load": [
                "training_volume",
                "outliers"
            ],

            "physiology_response": [
                "wellness",
                "insights"
            ],

            "performance_intelligence": [
                "performance_intelligence",
                "performance_summary"
            ],

            "adaptation": [
                "phases",
                "phases_summary",
                "current_ISO_weekly_microcycle"
            ]
        },

        "stack_labels": {
            "meta_context": "📊 REPORT CONTEXT",
            "training_load": "🧭 TRAINING LOAD",
            "physiology_response": "🫀 PHYSIOLOGY RESPONSE",
            "performance_intelligence": "⚙️ PERFORMANCE INTELLIGENCE",
            "adaptation": "📈 ADAPTATION"
        },

        "coaching_sentences": {
            "enabled": True,
            "max_per_section": 5,
            "placement": "after_data"
        },
        "interpretation_rules": [
            "If semantic.training_volume exists, render it under the header 'Training Volume' with three stacked metrics: Hours, Training Load (TSS), Distance.",
            "High-level descriptive interpretation only.",
            "Avoid granular metrics or micro-coaching."
            "phases_summary MUST be rendered as a compact table (max 10 rows) with columns: Phase, Duration, Trend",
            "phases_summary should always be sequential dated phases"
        ],
        "allowed_enrichment": [
            "Restate high-level trends explicitly present in semantic data.",
            "show full phases in markdown table."
        ],
        "section_handling": {
            "meta": "full",
            "training_volume": "full",
            "daily_load": "forbid",
            "wellness": "headline",
            "phases": "forbid",
            "phases_summary": "full",
            "insight_view": "forbid",
            "insights": "headline",
            "performance_summary": "full",
            "performance_intelligence.chronic": "summary",
            "current_ISO_weekly_microcycle": "forbid",
        },
        
        "emphasis": {
            "phases_summary": "high",
            "performance_summary": "high",
            "metrics": "low"
        },

        "framing": {
            "intent": "annual_system_health_review"
        },
        "question_rule": {
            "long-term training sustainability",
            "adaptation progression",
            "training consistency",
            "fatigue management across the season"
        },
        "closing_note": {
            "required": True,
            "verdict_rule": "Deliver a clear system-level sustainability verdict.",
            "classification_required": [
                "Sustainable Growth",
                "Stable Maintenance",
                "Drift Risk"
            ],
            "focus": "system_health",
            "anchor_metrics": [
                "phases",
                "performance_summary",
                "wellness_summary"
            ],
            "intent_rule": "Assess overall system health and sustainability across the review period.",
            "max_sentences": 5
        },
        "post_render": {
            "explore_deeper": {
                "enabled": True,
                "style": "command_suggestions",
                "placement": "after_report",
                "commands": [
                    "summarize my training year",
                    "what is my current training state",
                    "is my system improving or plateauing",
                    "how consistent is my training",
                    "show me more command questions"
                ]
            }
        }
    }
}


REPORT_RESOLUTION = {

    "weekly": {
        "CTL": "authoritative",
        "ATL": "authoritative",
        "TSB": "authoritative",
        "zones": "authoritative",
        "derived_metrics": "full",
        "performance_intelligence": "acute_full_7d or 90d_light_fallback",
        "energy_system_progression": "full",
        "insights": "tactical",
    },

    "season": {
        "CTL": "authoritative",
        "ATL": "authoritative",
        "TSB": "authoritative",
        "zones": "not_available",
        "derived_metrics": "trend_only",
        "performance_intelligence": "acute_7d_plus_chronic_90d",
        "energy_system_progression": "adaptation",
        "insights": "strategic",
    },

    "wellness": {
        "CTL": "icu_only",
        "ATL": "icu_only",
        "TSB": "icu_only",
        "zones": "not_applicable",
        "derived_metrics": "wellness_only",
        "performance_intelligence": "acute_full_7d or 90d_light_fallback",
        "insights": "recovery",
    },

    "summary": {
        "CTL": "icu_only",
        "ATL": "icu_only",
        "TSB": "icu_only",
        "zones": "suppressed",
        "derived_metrics": "suppressed",
        "insights": "executive",
    },
}

REPORT_HEADERS = {
    "weekly": {
        "title": "Weekly Training Report",
        "scope": "Detailed analysis of the last 7 days of training activity",
        "data_sources": "7-day full activities, 42-day wellness, 90 day light activities",
        "intended_use": (
            "Day-to-day coaching decisions, intensity balance, "
            "short-term fatigue and recovery management"
        ),
    },

    "season": {
        "title": "Season Training Overview",
        "scope": "Medium-term fitness, fatigue and progression trends",
        "data_sources": "90-day light activities, 42-day wellness, weekly aggregates",
        "intended_use": (
            "Strategic assessment of training progression, "
            "load management and phase direction"
        ),
    },

    "wellness": {
        "title": "Wellness & Recovery Status",
        "scope": "Physiological and subjective recovery indicators",
        "data_sources": "42-day wellness records (Intervals native)",
        "intended_use": (
            "Monitoring readiness, recovery balance "
            "and non-training stress"
        ),
    },

    "summary": {
        "title": "Training Summary",
        "scope": "High-level overview of current training state",
        "data_sources": "Authoritative totals, wellness indicators, derived insights",
        "intended_use": (
            "Executive summary and coaching narrative synthesis"
        ),
    },
}


"""
Scientific alignment (URF v5.3)
-------------------------------
• Issurin, V. (2008) – Block Periodization of Training Cycles
• Seiler, S. (2010, 2019) – Hierarchical Organization of Endurance Training
• Mujika & Padilla (2003) – Tapering and Peaking for Performance
• Banister, E.W. (1975) – Impulse–Response Model of Training
• Foster, C. et al. (2001) – Monitoring Training Load with Session RPE

Summary:
✅ phases         → macro-level blocks (Base, Build, Peak, etc.)
✅ phases_detail  → weekly micro-level metrics (TSS, hours, distance)
"""

COACH_PROFILE = {
    "version": "v17.0",

    "bio": {
        "summary": (
            "Deterministic endurance coaching system combining load modelling, "
            "physiological response, performance intelligence, and adaptive decision logic."
        ),
        "domains": [
            "Cycling", "Running", "Endurance"
        ],
        "principles": [
            "Load–Recovery Balance",
            "Polarised Intensity Distribution",
            "Progressive Overload",
            "Durability under Fatigue",
            "Energy System Specificity"
        ]
    },

    "science": {
        "models": [
            "Banister Load Model (CTL / ATL / TSB, EWMA)",
            "ACWR (Acute:Chronic Workload Ratio)",
            "Foster Monotony & Strain",
            "Seiler 3-Zone Intensity Distribution",
            "Treff Polarisation Index (2019)",
            "Critical Power Model (Skiba CP / W′)"
        ],
        "tier3_models": [
            "WDRM (Anaerobic Repeatability)",
            "ISDM (Durability / Decoupling)",
            "NDLI (Neural Load Density)",
            "ESPE (Energy System Progression)"
        ],
        "nutrition_model": [
            "IOC / ACSM Carbohydrate Availability",
            "Fuel Availability vs Training Load Matching"
        ],
        "decision_model": "Adaptive Decision Engine (ADE)"
    },


    "skills_matrix": {
        "load_management": [
            "ACWR", "Strain", "Monotony", "CTL", "ATL", "Form", "TRIMP", "W′/CP Modeling"
        ],
        "recovery_analysis": [
            "LoadVariabilityIndex", "HRV Integration", "Fatigue Detection", "Sleep Quality", "Readiness Tracking"
        ],
        "training_quality": [
            "Polarisation (Seiler 3-zone)",
            "PolarisationIndex (Treff 2019)",
            "DurabilityIndex",
            "SessionQualityRatio",
            "FatOxidationIndex"
        ],
        "performance_benchmarking": [
            "BenchmarkIndex", "SpecificityIndex", "ConsistencyIndex", "AgeFactor", "MicrocycleRecoveryWeek"
        ]
    },

    "markers": {
        "ACWR": {
            "framework": "Banister Load Ratio",
            "formula": "EWMA(Acute) / EWMA(Chronic)",
            "criteria": {
                "recovery": "<0.8",
                "productive": "0.8–1.3",
                "aggressive": "1.3–1.5",
                "overload": ">1.5"
            },
            "related_metrics": ["ATL", "CTL", "TSS_7d"]
        },

        "Monotony": {
            "framework": "Foster 2001",
            "formula": "Mean_7d / SD_7d",
            "criteria": {
                "optimal": "0–2",
                "moderate": "2.1–2.5",
                "high": ">2.5"
            },
            "related_metrics": ["TSS_7d"]
        },

        "Strain": {
            "framework": "Modified Foster 2001 (TSS-based)",
            "formula": "Monotony × ΣTSS_7d",
            "criteria": {
                "low": "<2000",
                "moderate": "2000–3000",
                "high": "3000–4000",
                "very_high": ">4000"
            },
            "related_metrics": ["Monotony", "TSS_7d"]
        },

        "FatigueTrend": {
            "framework": "7d vs prior 21d Load Delta",
            "formula": "(Mean_recent_7d - Mean_prior_21d) / Mean_prior_21d × 100",
            "criteria": {
                "balanced": "-10–10",
                "moderate_low": "-20–-10",
                "moderate_high": "10–20",
                "accumulating": "20–40",
                "extreme_accumulation": ">40",
                "recovering": "<-20"
            },
            "related_metrics": ["ATL", "CTL"]
        },

        "StressTolerance": {
            "framework": "Banister Capacity-Adjusted Load Ratio",
            "formula": "ΣTSS_7d / (CTL × 7)",
            "criteria": {
                "underload": "<0.8",
                "optimal": "0.8–1.2",
                "aggressive": "1.2–1.4",
                "overreach_risk": ">1.4"
            },
            "related_metrics": ["CTL", "TSS_7d"]
        },

        "FatigueResistance": {
            "framework": "Durability / Endurance Resilience Model",
            "formula": "EndurancePower / ThresholdPower",
            "criteria": {
                "low": "<0.8",
                "stable": "0.8–0.9",
                "optimal": "0.9–1.1",
                "high": "1.1–1.2",
                "extreme": ">1.2"
            },
            "related_metrics": ["ThresholdPower"]
        },

        "EfficiencyFactor": {
            "framework": "Aerobic Efficiency Index",
            "formula": "Power / HeartRate",
            "criteria": {
                "low": "<1.5",
                "moderate": "1.5–1.8",
                "optimal": "1.8–2.2",
                "high": "2.2–2.5",
                "extreme": ">2.5"
            },
            "related_metrics": ["HeartRate", "Power"]
        },

        "LoadVariabilityIndex": {
            "framework": "Foster Load Variability (Inverse Monotony)",
            "formula": "1 - (Monotony / 5)",
            "criteria": {
                "optimal": "0.7–1.0",
                "moderate": "0.4–0.69",
                "low": "<0.4"
            },
            "related_metrics": ["Monotony"]
        },
        "FatOxidationIndex": {
            "framework": "San Millán Zone 2 Model",
            "formula": "(1 - |IF - 0.7| / 0.1) × (1 - Decoupling / 10)",
            "criteria": {
                "optimal": ">=0.80",
                "moderate": "0.60–0.79",
                "low": "<0.60"
            },
            "placement": "Training Quality section",
        },
        "FatOxEfficiency": {
            "framework": "San Millán 2020",
            "formula": "Derived from IF × 0.9",
            "criteria": {
                "optimal": "0.60–0.80",
                "moderate": "0.50–0.59",
                "low": "<0.50"
            },
            "related_metrics": ["IF"]
        },

        "FOxI": {
            "framework": "Internal Derived Metric",
            "formula": "FatOxEfficiency × 100",
            "criteria": {
                "optimal": ">=70",
                "moderate": "50–69",
                "low": "<50"
            },
            "related_metrics": ["FatOxEfficiency"]
        },

        "CUR": {
            "framework": "Internal Derived Metric",
            "formula": "100 - FOxI",
            "criteria": {
                "balanced": "30–70",
                "moderate_low": "20–29",
                "moderate_high": "71–80",
                "low_carb_bias": "<20",
                "high_carb_bias": ">80"
            },
            "related_metrics": ["FOxI", "GR"]
        },

        "GR": {
            "framework": "Internal Derived Metric",
            "formula": "IF × 2.4",
            "criteria": {
                "optimal": "1.5–2.1",
                "moderate": "1.2–1.49",
                "high": ">2.1",
                "low": "<1.2"
            },
            "related_metrics": ["IF"]
        },

        "MES": {
            "framework": "Internal Derived Metric",
            "formula": "(FatOxEfficiency × 60) / GR",
            "criteria": {
                "optimal": ">=20",
                "moderate": "10–19",
                "low": "<10"
            },
            "related_metrics": ["FatOxEfficiency", "GR"]
        },
        "ZQI": {
            "framework": "Seiler Intensity Distribution (power-zone mapped)",
            "formula": "% time in Z4–Z7 (proxy for Seiler Z3 high-intensity)",
            "criteria": {
                "low": "<5",
                "optimal": "5–15",
                "high": "15–25",
                "excessive": ">25"
            }
        },
        "DurabilityIndex": {
            "framework": "Sandbakk Durability",
            "formula": "1 - (PowerDrop% / 100)",
        },
        "Polarisation": {
            "framework": "Seiler 3-Zone Contrast Model",
            "formula": "(Z1 + Z3+) / (2 × Z2)  (3-zone collapsed, renormalised)",
            "criteria": {
                "z2_dominant": "< 0.65",
                "pyramidal": "0.65–0.84",
                "polarised": "0.85–1.25",
                "high_contrast": "> 1.25"
            },
        },
        "PolarisationIndex": {
            "framework": "Treff 2019 Polarization-Index",
            "formula": "log10( Z1 / (Z2 × Z3) × 100 )  (3-zone collapsed)",
            "criteria": {
                "threshold_dominant": "< 1.5",
                "pyramidal": "1.5–1.99",
                "polarised": "≥ 2.0"
            },
        },
        "Polarisation_fused": {
            "framework": "Seiler / Stöggl / Issurin (HR+Power fused)",
            "formula": "Normalized intensity-domain distribution (fused HR+Power)",
            "criteria": {
                "polarised": "≥ 0.80",
                "pyramidal": "0.65–0.79",
                "threshold_dominant": "< 0.65"
            },
        },
        "Polarisation_combined": {
            "framework": "Seiler / Stöggl / Issurin (multi-sport combined)",
            "formula": "Normalized global intensity-domain distribution",
            "criteria": {
                "polarised": "≥ 0.78",
                "pyramidal": "0.65–0.77",
                "threshold_dominant": "< 0.65"
            },
        },
        "TRIMP": {
            "framework": "Banister Load Model",
            "formula": "Duration × HR_ratio × e^(1.92 × HR_ratio)",
        },
        "Readiness": {
            "framework": "Noakes Central Governor",
            "formula": "0.3×Mood + 0.3×Sleep + 0.2×Stress + 0.2×Fatigue",
        },
        "BenchmarkIndex": {
            "framework": "Friel Functional Benchmarking",
            "formula": "(FTP_current / FTP_prior) - 1",
            "criteria": {
                "productive": "+2–5%",
                "stagnant": "0%",
                "regression": ">−3%"
            },
        },
        "SpecificityIndex": {
            "framework": "Friel Specificity Ratio",
            "formula": "race_specific_hours / total_hours",
            "criteria": {
                "peak": "0.70–0.90",
                "build": "0.50–0.69",
                "base": "<0.50"
            },
        },
        "ConsistencyIndex": {
            "framework": "Friel Consistency Metric",
            "formula": "completed_sessions / planned_sessions",
            "criteria": {
                "consistent": ">=0.90",
                "variable": "0.75–0.89",
                "inconsistent": "<0.75"
            },
        },
        "AgeFactor": {
            "framework": "Friel Aging Adaptation",
            "formula": "ATL_adj = ATL × (1 - 0.005 × (Age - 40))",
        },
        # --- Supplemental markers synced from CHEAT_SHEET thresholds ---
        "Durability": {
            "framework": "Sandbakk Durability",
            "formula": "Power_stability under fatigue",
            "criteria": {
                "optimal": ">=0.90",
                "moderate": "0.70–0.89",
                "low": "<0.70"
            }
        },
        "LIR": {
            "framework": "Load Intensity Ratio",
            "formula": "Intensity / Duration",
            "criteria": {
                "balanced": "0.8–1.2",
                "high": ">1.2",
                "low": "<0.8"
            }
        },
        "EnduranceReserve": {
            "framework": "Durability Reserve Index",
            "formula": "AerobicDurability / FatigueIndex",
            "criteria": {
                "strong": ">=1.2",
                "moderate": "0.8–1.19",
                "depleted": "<0.8"
            }
        },
        "IFDrift": {
            "framework": "Efficiency Drift",
            "formula": "ΔIF over time",
            "criteria": {
                "stable": "0.0–0.05",
                "moderate": "0.05–0.10",
                "high": ">0.10"
            }
        },
        "Lactate": {
            "framework": "Mader-Heck 1986",
            "formula": "LT1/LT2 correlation threshold",
            "criteria": {
                "low": "<2.0",
                "moderate": "2.0–4.0",
                "high": ">4.0"
            }
        },
        "HRV": {
            "framework": "Autonomic Recovery Model",
            "formula": "Mean vs Latest HRV (ms)",
            "criteria": {
                "optimal": ">=60",
                "moderate": "40–59",
                "low": "<40"
            },
            "related_metrics": ["RestingHR", "HRVBalance", "HRVTrend", "SleepQuality"]
        },

        "RestingHR": {
            "framework": "Cardiac Recovery Model",
            "formula": "Resting HR (bpm)",
            "criteria": {
                "optimal": "32–60",
                "moderate": "61–70",
                "high": ">70"
            },
            "related_metrics": ["HRV"]
        },

        "RestingHRDelta": {
            "framework": "Cardiac Recovery Trend",
            "formula": "Δ7–28 day Resting HR",
            "criteria": {
                "optimal": "-2–2",
                "moderate": "2–5",
                "high": ">5"
            },
            "related_metrics": ["RestingHR"]
        },

        "SleepQuality": {
            "framework": "Sleep Hygiene & Recovery Model",
            "formula": "Average Sleep Score (14 days)",
            "criteria": {
                "optimal": "80–100",
                "moderate": "65–79",
                "low": "<65"
            },
            "related_metrics": ["HRV"]
        },

        "HRVBalance": {
            "framework": "Autonomic Recovery Model",
            "formula": "Latest HRV / Mean HRV",
            "criteria": {
                "optimal": "1.0–1.3",
                "moderate": "0.9–0.99",
                "low": "<0.9"
            },
            "related_metrics": ["HRV"]
        },

        "HRVStability": {
            "framework": "Variability Index",
            "formula": "1 - (std / mean) (14d)",
            "criteria": {
                "optimal": ">=0.85",
                "moderate": "0.7–0.84",
                "low": "<0.7"
            },
            "related_metrics": ["HRV"]
        },

        "HRVTrend": {
            "framework": "Short-Term HRV Trend",
            "formula": "Linear slope (7d)",
            "criteria": {
                "optimal": ">=0",
                "moderate": "-2–-0.01",
                "low": "<-2"
            },
            "related_metrics": ["HRV"]
        },
        "vo2_reserve_ratio": {
            "framework": "Critical Power / VO₂ Reserve Model",
            "formula": "P5m / CP",
            "interpretation": "Ratio of 5-minute power to Critical Power reflecting VO₂ headroom above threshold.",
            "coaching_implication": "Lower ratios indicate fatigue or VO₂ limitation.",
        },

        "pdr_5m": {
            "framework": "Power Duration Reserve",
            "formula": "P5m − CP",
            "interpretation": "Difference between 5-minute power and Critical Power representing VO₂ reserve capacity.",
            "coaching_implication": "Higher reserve suggests strong VO₂ capacity above threshold.",
        },

        "durability_gradient": {
            "framework": "Durability Gradient Model",
            "formula": "P60 / P20",
            "interpretation": "Ratio of 60-minute power to 20-minute power reflecting fatigue resistance across prolonged efforts.",
            "coaching_implication": "Lower gradients indicate durability decline during long efforts.",
        },

        "glycolytic_bias_ratio": {
            "framework": "Energy System Balance Model",
            "formula": "P1m / CP",
            "interpretation": "Ratio of short-duration power to threshold power indicating glycolytic dominance.",
            "coaching_implication": "High values suggest anaerobic bias relative to aerobic capacity.",
        },

        "aerobic_durability_ratio": {
            "framework": "Durability / Endurance Model",
            "formula": "P60 / CP",
            "interpretation": "Ratio of 60-minute power to 5-minute power reflecting endurance durability across prolonged efforts.",
            "coaching_implication": "Lower ratios suggest fatigue-driven endurance drop-off.",
        },

        "system_balance_score": {
            "framework": "Energy System Balance Composite",
            "formula": "Composite ESPE score across anaerobic, VO₂, threshold and durability systems",
            "interpretation": "Composite indicator describing balance of energy system development.",
            "coaching_implication": "Values closer to 1 indicate balanced development across systems.",
        },
        "LoadRecoveryState": {
            "framework": "HRV–Load Interaction Model (Plews 2013; Banister 1975)",
            "formula": "HRV_autonomic_ratio interpreted alongside ATL − CTL load pressure",
            "interpretation": (
                "Qualitative state describing the interaction between autonomic recovery "
                "(HRV relative to baseline) and current training load pressure (ATL vs CTL)."
            ),
            "criteria": {
                "balanced": "Recovery signals aligned with training load.",
                "productive_load": "Training load elevated but autonomic recovery stable.",
                "adaptation_pressure": "Autonomic recovery suppressed under elevated load.",
                "maladaptation_risk": "Recovery breakdown relative to training stress."
            },
            "coaching_implication": (
                "Helps determine whether current training load is being productively absorbed "
                "or whether recovery capacity is being exceeded."
            )
        },
        # ---------------------------------------------------------
        # 🧠 Performance Intelligence — Context Metrics (Interpretation-driven)
        # ---------------------------------------------------------

        "mean_depletion_pct_7d": {
            "framework": "W′ Depletion & Repeatability Model (WDRM)",
            "formula": "Mean W′ depletion across sessions (7d)",
            "criteria": {
                "low": "<0.2 — minimal anaerobic strain",
                "moderate": "0.2–0.45 — controlled anaerobic contribution",
                "high": ">0.45 — repeated deep depletion"
            },
            "interpretation": "Average depth of anaerobic reserve usage across recent sessions.",
            "coaching_implication": "Higher values reflect repeated supra-threshold stress and increased recovery demand."
        },

        "mean_decoupling_signed_7d": {
            "framework": "Intensity Stability & Durability Model (ISDM)",
            "formula": "Signed HR–Power decoupling (%) (7d)",
            "criteria": {},
            "interpretation": (
                "Direction of efficiency change. Negative values indicate improving efficiency; "
                "positive values indicate cardiovascular drift."
            ),
            "coaching_implication": (
                "Use to determine whether durability is improving or deteriorating under load."
            )
        },
        "mean_decoupling_signed_90d": {
            "framework": "Intensity Stability & Durability Model (ISDM)",
            "formula": "Signed HR–Power decoupling (%) (90d)",
            "criteria": {},
            "interpretation": (
                "Long-term direction of efficiency change. Negative values indicate improving "
                "efficiency across training blocks; positive values indicate persistent "
                "cardiovascular drift."
            ),
            "coaching_implication": (
                "Indicates whether durability is improving or degrading over time. "
                "Use alongside acute (7d) values to assess recent vs long-term adaptation."
            )
        },

        "mean_depletion_pct_90d": {
            "framework": "W′ Depletion & Repeatability Model (WDRM)",
            "formula": "Mean W′ depletion across sessions (90d)",
            "criteria": {
                "low": "<0.15 — minimal anaerobic reliance",
                "moderate": "0.15–0.35 — balanced long-term profile",
                "high": ">0.35 — sustained anaerobic bias"
            },
            "interpretation": "Long-term average depth of anaerobic reserve usage.",
            "coaching_implication": "Indicates whether training is predominantly aerobic or consistently drawing on anaerobic reserves."
        },

        "max_depletion_pct_7d": {
            "framework": "W′ Depletion & Repeatability Model (WDRM)",
            "formula": "Max W′ depletion observed (7d)",
            "criteria": {
                "low": "<0.3 — shallow depletion",
                "moderate": "0.3–0.6 — meaningful anaerobic stimulus",
                "high": ">0.6 — deep depletion event"
            },
            "interpretation": "Peak anaerobic depletion reached in recent sessions.",
            "coaching_implication": (
                "Higher values reflect greater reliance on anaerobic contribution "
                "and increased recovery demand."
            )
        },

        "mean_decoupling_7d": {
            "framework": "Intensity Stability & Durability Model (ISDM)",
            "formula": "Mean HR–Power decoupling magnitude (%) (7d)",
            "interpretation": (
                "Absolute decoupling magnitude. Does not indicate direction. "
                "Use durability state to determine whether efficiency is improving or deteriorating."
            ),
            "coaching_implication": (
                "Higher values indicate greater instability in effort sustainability, "
                "but must be interpreted alongside durability state."
            )
        },

        "mean_decoupling_90d": {
            "framework": "Intensity Stability & Durability Model (ISDM)",
            "formula": "Mean HR–Power decoupling magnitude (%) (90d)",

            "interpretation": (
                "Long-term decoupling magnitude. Reflects accumulated durability behaviour over time. "
                "Durability state is the authoritative assessment."
            ),
            "coaching_implication": (
                "Use to contextualise long-term durability trends only. "
                "Do not interpret in isolation."
            )
        },

        "max_decoupling_90d": {
            "framework": "Intensity Stability & Durability Model (ISDM)",
            "formula": "Max HR–Power decoupling magnitude (%) (90d)",

            "interpretation": (
                "Peak long-term decoupling magnitude observed. "
                "Does not indicate direction of change."
            ),
            "coaching_implication": (
                "Indicates exposure to high drift events over time. "
                "Must be interpreted alongside durability state."
            )
        },

        "total_joules_above_ftp_7d": {
            "framework": "W′ / High-Intensity Load",
            "formula": "Total work above FTP (7d)",
            "criteria": {
                "low": "<100kJ — low anaerobic stimulus",
                "moderate": "100–250kJ — structured intensity",
                "high": ">250kJ — heavy anaerobic load"
            },
            "interpretation": "Total accumulated supra-threshold work.",
            "coaching_implication": "Higher values increase recovery demand and neuromuscular strain."
        },

        "mean_if_7d": {
            "framework": "Neural Density Load Index (NDLI)",
            "formula": "Mean Intensity Factor (7d)",
            "criteria": {
                "low": "<0.65 — low intensity bias",
                "moderate": "0.65–0.8 — endurance mix",
                "high": ">0.8 — intensity heavy"
            },
            "interpretation": "Average session intensity across the week.",
            "coaching_implication": "Higher values reflect greater intensity density and recovery demand."
        },

        "mean_efficiency_factor_7d": {
            "framework": "Neural Density Load Index (NDLI)",
            "formula": "Mean Efficiency Factor (7d)",
            "criteria": {
                "low": "<1.7 — low aerobic efficiency",
                "moderate": "1.7–2.1 — stable efficiency",
                "high": ">2.1 — strong aerobic efficiency"
            },
            "interpretation": "Relationship between power output and heart rate.",
            "coaching_implication": (
                "Higher values generally indicate improved aerobic efficiency, "
                "but should be interpreted alongside intensity and terrain context."
            )
        },

        "mean_variability_index_7d": {
            "framework": "Neural Density Load Index (NDLI)",
            "formula": "Mean Variability Index (7d)",
            "criteria": {
                "steady": "<1.05 — steady pacing",
                "moderate": "1.05–1.15 — mixed intensity",
                "high": ">1.15 — stochastic / variable load"
            },
            "interpretation": "Reflects variability of power output within sessions.",
            "coaching_implication": "Higher values indicate stochastic efforts and increased neuromuscular demand."
        },

        "long_sessions_7d": {
            "framework": "Durability Exposure",
            "formula": "Count of long endurance sessions (7d)",
            "interpretation": "Exposure to prolonged endurance stress.",
            "coaching_implication": "Supports durability development but increases cumulative fatigue."
        },
        #NUTRITION MARKERS (NOT THRESHOLDS)
        "ProteinIntake": {
            "framework": "Recovery Nutrition (ISSN / IOC consensus)",
            "unit": "g/kg",
            "formula": "Daily protein intake (g) ÷ body mass (kg)",
            "criteria": {
                "low": "<1.6 — insufficient for recovery support",
                "optimal": "1.6–2.2 — supports repair and adaptation",
                "high": ">2.2 — no additional recovery benefit"
            },
            "interpretation": "Protein intake (≈1.6–2.2 g/kg; ISSN/IOC consensus) supports muscle repair and adaptation to training load.",
            "coaching_implication": "Increase intake during high load or recovery phases to support adaptation (ISSN/IOC guidance).",
            "related_metrics": ["HRV", "SleepQuality", "FatigueTrend"]
        },

        "CarbohydrateAvailability": {
            "framework": "Fuel Availability (IOC / ACSM Sports Nutrition)",
            "unit": "g/kg_relative_to_demand",
            "formula": "Actual carbohydrate intake (g/kg) − required carbohydrate demand (g/kg), with requirement derived from recent daily training duration and intensity",
            "criteria": {
                "severely_underfuelled": "<-3 g/kg vs demand — large glycogen deficit",
                "underfuelled": "-3 to -1 g/kg vs demand — insufficient for load",
                "balanced": "-1 to +1.5 g/kg vs demand — aligned with demand",
                "overfuelled": ">+1.5 g/kg vs demand — intake exceeds requirement"
            },
            "interpretation": "Carbohydrate availability (≈3–10 g/kg depending on training load; IOC/ACSM guidelines) determines glycogen replenishment and endurance capacity.",
            "coaching_implication": "Align carbohydrate intake with training demand (IOC/ACSM) to maintain glycogen availability, recovery, and performance capacity.",
            "related_metrics": ["HRV", "SleepQuality", "TrainingLoad"]
        },

        "FatIntake": {
            "framework": "Energy Balance (Endocrine support)",
            "unit": "g/kg",
            "formula": "Daily fat intake (g) ÷ body mass (kg)",
            "criteria": {
                "low": "<0.8 — may impact hormonal function",
                "optimal": "0.8–1.2 — supports endocrine stability",
                "high": ">1.2 — elevated energy density"
            },
            "interpretation": "Fat intake supports hormonal function and long-term energy balance (general sports nutrition consensus).",
            "coaching_implication": "Maintain sufficient intake to support endocrine health and overall energy availability.",
            "related_metrics": []
        }
    },
    "metadata": {
        "framework_chain": [
            "Seiler", "Treff 2019", "Banister", "Foster", "San Millán",
            "Friel", "Sandbakk", "Skiba", "Coggan", "Noakes","Plews–Banister Interaction Framework"
        ],
        "unified_framework": "v5.1",
        "audit_validation": "Tier-2 verified, event-only totals enforced",
        "variance": "<= 2%",
        "last_revision": "2026-03-19"
    },

    "nutrition_demand_model": {

        "carbohydrates": {
            "method": "session_based",

            "duration_bands": [
                {"max_hours": 1.0, "gkg": 3.5},
                {"max_hours": 2.0, "gkg": 5.0},
                {"max_hours": 3.0, "gkg": 6.0},
                {"max_hours": 4.0, "gkg": 7.0},
                {"max_hours": 24.0, "gkg": 8.5}
            ],

            "intensity_adjustment": {
                "high_if": {"threshold": 0.85, "delta": 0.5},
                "low_if": {"threshold": 0.65, "delta": -0.5}
            },

            "bounds": {
                "min": 3.0,
                "max": 10.0
            }
        },

        "protein": {
            "baseline": 1.6,
            "elevated_recovery": 2.0
        },

        "fat": {
            "baseline": 1.0
        },
    }
}
# Alias for compatibility with derived metrics imports
PROFILE_DATA = COACH_PROFILE
