#!/usr/bin/env python3
"""
coaching_profile.py — Unified Coaching Profile (v16.1-Sync)
Structured reference of frameworks, formulas, and methodology anchors.
Machine-synced with coach_profile.md (2025-11-03).
"""

def get_profile_metrics(context):
    """Return adaptive coaching metrics based on context and COACH_PROFILE."""
    return {
        "eff_factor": context.get("efficiency_factor", 1.9),
        "fatigue_resistance": context.get("fatigue_resistance", 0.95),
        "endurance_decay": context.get("aerobic_decay", 0.02),
        "z2_stability": context.get("z2_variance", 0.04),
        "aerobic_decay": context.get("aerobic_decay", 0.02),
    }

# coaching_profile.py

RENDERER_PROFILES = {

    # ==============================================================
    # Global rules (apply to ALL report types)
    # ==============================================================
    "global": {
        "hard_rules": [
            "Treat the provided semantic JSON as canonical truth.",
            "Do NOT compute, infer, or modify metrics.",
            "Do NOT introduce new metrics, thresholds, or comparisons.",
            "Render exactly ONE report.",
            "Do NOT add numeric prefixes to section headers.",
            "Use emoji-based section headers only.",
            "Preserve section order exactly as defined by the contract."
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
            "Keep tone factual, neutral, and coach-like.",
            "No speculation or prediction beyond the provided semantic data."
        ]
    },

    # ==============================================================
    # Weekly report (FULL DETAIL, SESSION-LEVEL)
    # ==============================================================
    "weekly": {
        "coaching_sentences": {
            "enabled": True,
            "max_per_section": 3,
            "placement": "after_data"
        },
        "interpretation_rules": [
            "Interpretations must be directly anchored to values, states, or interpretation fields.",
            "Interpretations may be descriptive or conditional, not predictive.",
            "No cross-section synthesis."
        ],
        "allowed_enrichment": [
            "Restate semantic interpretation fields.",
            "Explain what a value indicates within its known threshold or state."
        ],
        "section_handling": {
            "events": "full",
            "daily_load": "full",
            "metrics": "full",
            "extended_metrics": "full",
            "zones": "full",
            "wellness": "full",
            "phases": "forbid"
        }
    },

    # ==============================================================
    # Season report (PHASE-LEVEL, STRATEGIC)
    # ==============================================================
    "season": {
        "coaching_sentences": {
            "enabled": True,
            "max_per_section": 3,
            "placement": "after_data"
        },
        "interpretation_rules": [
            "Focus on trends, phases, and accumulated load.",
            "Avoid session-level or daily commentary."
        ],
        "allowed_enrichment": [
            "Restate phase descriptors already present in semantic data."
        ],
        "section_handling": {
            "events": "forbid",
            "daily_load": "forbid",
            "weekly_phases": "forbid",
            "phases": "full",
            "metrics": "full",
            "extended_metrics": "full",
            "zones": "summary",
            "wellness": "summary"
        }
    },

    # ==============================================================
    # Wellness report (PROD-ALIGNED, SIGNAL-FIRST)
    # ==============================================================
    "wellness": {

        "coaching_sentences": {
            "enabled": True,
            "max_per_section": 5,
            "placement": "after_data"
        },

        "interpretation_rules": [
            "Interpret recovery using trends, means, and latest values together.",
            "Explain HRV behaviour (variability, clustering, suppression) when present.",
            "Integrate HRV with CTL, ATL, and TSB within the same section.",
            "Avoid day-by-day narration when aggregates or trends exist."
        ],

        "allowed_enrichment": [
            "Summarise HRV behaviour using peaks, troughs, variability, and clustering.",
            "Explain physiological meaning of HRV suppression vs personal baseline.",
            "Describe maintenance-under-load states when CTL≈ATL and HRV is falling.",
            "Highlight absence of subjective recovery data if present in semantic data.",
            "Include short, non-predictive coach recommendations grounded in signals."
        ],

        "section_handling": {
            "meta": "full",
            "wellness": "full",
            "hrv_daily": "summary",
            "insights": "full",
            "insight_view": "full",
            "events": "forbid",
            "daily_load": "forbid",
            "metrics": "forbid",
            "extended_metrics": "forbid",
            "zones": "forbid",
            "phases": "forbid"
        }
    },


    # ==============================================================
    # Summary report (EXECUTIVE)
    # ==============================================================
    "summary": {
        "coaching_sentences": {
            "enabled": True,
            "max_per_section": 3,
            "placement": "after_data"
        },
        "interpretation_rules": [
            "High-level descriptive interpretation only.",
            "Avoid granular metrics or micro-coaching."
        ],
        "allowed_enrichment": [
            "Restate high-level trends explicitly present in semantic data."
        ],
        "section_handling": {
            "events": "forbid",
            "daily_load": "forbid",
            "metrics": "summary",
            "extended_metrics": "forbid",
            "zones": "summary",
            "wellness": "summary",
            "phases": "summary"
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
        "extended_metrics": "limited",
        "insights": "tactical",
    },

    "season": {
        "CTL": "authoritative",
        "ATL": "authoritative",
        "TSB": "authoritative",
        "zones": "not_available",
        "derived_metrics": "trend_only",
        "extended_metrics": "full",
        "insights": "strategic",
    },

    "wellness": {
        "CTL": "icu_only",
        "ATL": "icu_only",
        "TSB": "icu_only",
        "zones": "not_applicable",
        "derived_metrics": "wellness_only",
        "extended_metrics": "none",
        "insights": "recovery",
    },

    "summary": {
        "CTL": "icu_only",
        "ATL": "icu_only",
        "TSB": "icu_only",
        "zones": "suppressed",
        "derived_metrics": "suppressed",
        "extended_metrics": "suppressed",
        "insights": "executive",
    },
}

REPORT_HEADERS = {
    "weekly": {
        "title": "Weekly Training Report",
        "scope": "Detailed analysis of the last 7 days of training activity",
        "data_sources": "7-day full activities, 42-day wellness, zone distributions",
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


REPORT_CONTRACT = {
    "weekly": [
        "meta", "hours", "tss", "distance_km",
        "metrics", "extended_metrics",
        "zones", "daily_load",
        "wellness", "insights",
        "events", "actions",
        "planned_events", "planned_summary_by_date",
        "future_forecast"
    ],

    "season": [
        "meta", "hours", "tss", "distance_km",
        "metrics", "extended_metrics",
        "adaptation_metrics", "trend_metrics",
        "phases", "phases_summary",
        "wbal_summary", "performance_summary",
        "insights", "insights_view" "actions", "future_forecast"
    ],

    "summary": [
        "meta", "hours", "tss", "distance_km",
        "wellness", "insights", "insight_view",
        "phases", "phases_summary",
        "wbal_summary", "performance_summary",
        "actions"
    ],

    "wellness": [
        "meta", "wellness", "insights", "insight_view"
    ]
}



COACH_PROFILE = {
    "version": "v17",
    "bio": {
        "summary": (
            "Data-driven endurance coaching blending objective load metrics "
            "(TSS, CTL, ATL, HRV, VO₂max) with subjective readiness (RPE, mood, recovery). "
            "Implements evidence-based frameworks for phase-specific training adaptation."
        ),
        "domains": [
            "Triathlon", "Cycling", "Running", "Endurance", "Ironman", "Gran Fondo", "Marathon"
        ],
        "principles": [
            "Seiler 80/20 Polarisation", "Banister TRIMP", "Foster Monotony/Strain",
            "San Millán Zone 2", "Friel Periodisation", "Sandbakk Durability",
            "Skiba Critical Power", "Coggan Power Zones", "Noakes Central Governor"
        ]
    },

    "skills_matrix": {
        "load_management": [
            "ACWR", "Strain", "Monotony", "CTL", "ATL", "Form", "TRIMP", "W′/CP Modeling"
        ],
        "recovery_analysis": [
            "RecoveryIndex", "HRV Integration", "Fatigue Detection", "Sleep Quality", "Readiness Tracking"
        ],
        "training_quality": [
            "PolarisationIndex", "DurabilityIndex", "SessionQualityRatio", "FatOxidationIndex"
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
                "productive": "0.8–1.3",
                "recovery": "<0.8",
                "overload": ">1.5"
            },
        },
        "Monotony": {
            "framework": "Foster 2001",
            "formula": "Mean_7d / SD_7d",
            "criteria": {
                "optimal": "0–2",
                "moderate": "2.1–2.5",
                "high": ">2.5"
            },
        },
        "Strain": {
            "framework": "Foster 2001",
            "formula": "Monotony × ΣLoad_7d",
            "criteria": {
                "optimal": "<600",
                "moderate": "600–800",
                "high": ">800"
            },
        },
        "FatigueTrend": {
            "framework": "Banister EWMA Delta",
            "formula": "Mean(7d) – Mean(28d)",
            "criteria": {
                "balanced": "-0.2–+0.2",
                "accumulating": ">+0.2",
                "recovering": "<-0.2"
            },
        },
        "StressTolerance": {
            "framework": "Adaptive Load Tolerance",
            "formula": "(strain / monotony) / 100",
            "criteria": {
                "low": "<3",
                "optimal": "3–6",
                "high": ">6"
            }
        },
        "FatigueResistance": {
            "framework": "Durability / Endurance Resilience Model",
            "formula": "EndurancePower / ThresholdPower",
            "criteria": {
                "low": "<0.9",
                "stable": "0.9–1.0",
                "high": ">1.0"
            },
            "interpretation": (
                "Ratio of endurance to threshold power. "
                "High values indicate preserved performance over long durations."
            ),
            "coaching_implication": (
                "If below 0.9, increase steady endurance work; maintain 0.95–1.0 for optimal durability."
            ),
        },
        "EfficiencyFactor": {
            "framework": "Aerobic Efficiency Index",
            "formula": "Power / HeartRate",
            "criteria": {
                "low": "<1.6",
                "moderate": "1.6–1.8",
                "optimal": "1.8–2.2",
                "high": ">2.2"
            },
            "interpretation": (
                "Power-to-HR ratio indicating aerobic conditioning. "
                "Higher EF suggests improved aerobic efficiency and cardiac economy."
            ),
            "coaching_implication": (
                "If EF decreases, focus on aerobic base and recovery. "
                "Stable or rising EF = strong aerobic fitness trend."
            ),
        },
        "RecoveryIndex": {
            "framework": "Noakes Central Governor",
            "formula": "HRV / RestHR × readiness",
            "criteria": {
                "optimal": "0.8–1.0",
                "moderate": "0.7–0.79",
                "low": "<0.7"
            },
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
                "optimal": "0.6–0.8",
                "low": "<0.5"
            },
        },
                "FOxI": {
            "framework": "Internal Derived Metric",
            "formula": "FatOxEfficiency × 100",
            "criteria": {
                "optimal": ">=70",
                "moderate": "50–69",
                "low": "<50"
            },
            "placement": "Training Quality section"
        },
        "CUR": {
            "framework": "Internal Derived Metric",
            "formula": "100 - FOxI",
            "criteria": {
                "optimal": "20–60",
                "high": ">80",
                "low": "<20"
            },
            "placement": "Training Quality section"
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
            "placement": "Metabolic section"
        },
        "MES": {
            "framework": "Internal Derived Metric",
            "formula": "(FatOxEfficiency × 60) / GR",
            "criteria": {
                "optimal": ">=20",
                "moderate": "10–19",
                "low": "<10"
            },
            "placement": "Metabolic section"
        },
        "ZQI": {
            "framework": "Seiler Intensity Distribution",
            "formula": "High-intensity time (%)",
            "criteria": {
                "optimal": "5–15",
                "moderate": "15–25",
                "low": "<5"
            },
            "placement": "Training Quality section",
        },
        "DurabilityIndex": {
            "framework": "Sandbakk Durability",
            "formula": "1 - (PowerDrop% / 100)",
        },
        "Polarisation": {
            "framework": "Seiler 80/20 Model (Ratio)",
            "formula": "(Z1 + Z3) / (2 × Z2)",
            "criteria": {
                "polarised": "≥ 1.0",
                "mixed": "0.7–0.99",
                "z2_base": "0.35–0.69",   # Added contextual category
                "threshold": "< 0.35"
            },
            "interpretation": (
                "Seiler Polarisation Ratio showing the balance of low- and high-intensity "
                "training (Z1 + Z3) relative to moderate-intensity work (Z2). "
                "≥1.0 = polarised (80/20), 0.7–0.99 = mixed, 0.35–0.69 = Z2-base dominant "
                "(normal in aerobic foundation), <0.35 = true threshold-heavy pattern."
            ),
            "coaching_implication": (
                "If Polarisation <0.7 and current block = Base, interpret as Z2-base dominant "
                "(✅ aerobic focus). If in Build or Peak, reduce mid-zone load and increase Z1 "
                "and Z3 contrast. Maintain ≥1.0 for fully polarised 80/20 structure in race phases."
            ),
        },
        "PolarisationIndex": {
            "framework": "Z1+Z2 Normalized Index",
            "formula": "(Z1 + Z2) / Total zone time",
            "criteria": {
                "aerobic": "≥ 0.75",
                "mixed": "0.6–0.74",
                "intensity_focused": "< 0.6"
            },
            "interpretation": (
                "Normalized time-in-zone index (0–1) representing the proportion of training "
                "spent in low and moderate intensities (Z1+Z2). ≥0.75 = strong aerobic bias "
                "(ideal for Base/Recovery), 0.60–0.74 = balanced, <0.60 = intensity-focused "
                "(typical in Build or Peak phases)."
            ),
            "coaching_implication": (
                "If PolarisationIndex <0.60 and current block = Base, rebalance toward Z1 endurance "
                "and reduce Z2. If <0.60 in Build/Peak, acceptable due to intensity focus. "
                "Target ≥0.75 for strong aerobic adaptation in Base/Recovery."
            ),
        },
        "Polarisation_fused": {
            "framework": "Seiler 80/20 (HR+Power Fusion)",
            "formula": "(Z1 + Z3) / (2 × Z2) [applied to fused HR+Power zones]",
            "criteria": {
                "polarised": "≥ 1.0",
                "mixed": "0.7–0.99",
                "z2_base": "0.35–0.69",
                "threshold": "< 0.35"
            },
            "interpretation": (
                "Derived per sport from HR+Power fusion. Reflects dominant-sport load separation. "
                "Higher values indicate clear low/high intensity contrast."
            ),
            "coaching_implication": (
                "If <0.7 in Base → aerobic focus (✅). "
                "If <0.7 in Build/Peak → excessive mid-zone; rebalance toward Z1/Z3 contrast."
            ),
        },
        "Polarisation_combined": {
            "framework": "Seiler 80/20 (Multi-sport Weighted)",
            "formula": "(Z1 + Z3) / (2 × Z2) [multi-sport weighted]",
            "criteria": {
                "polarised": "≥ 1.0",
                "mixed": "0.7–0.99",
                "z2_base": "0.35–0.69",
                "threshold": "< 0.35"
            },
            "interpretation": (
                "Weighted mean of sport-specific fused indices. Represents overall cross-sport "
                "intensity distribution. Lower values indicate too much threshold work globally."
            ),
            "coaching_implication": (
                "Maintain ≥0.8 global balance for healthy load variation. "
                "If <0.65 → add Z1 endurance days or rest."
            ),
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
            "criteria": {"low": "<40", "optimal": "60–90"},
        },
        "RestingHR": {
            "framework": "Cardiac Recovery Model",
            "formula": "Δ7–28 day Resting HR",
            "criteria": {"low": ">5", "optimal": "<=0"},
        },
        "SleepQuality": {
            "framework": "Sleep Hygiene & Recovery Model",
            "formula": "Average Sleep Score (14 days)",
            "criteria": {"low": "<70", "optimal": ">=80"},
        },
        "RecoveryIndex": {
            "framework": "TSB–HRV Composite Index",
            "formula": "(HRV / HRV_mean) × (TSB / 10)",
            "criteria": {"low": "<0.5", "optimal": "0.6–0.9"},
        },
        "HRVBalance": {
        "framework": "Autonomic Recovery Model",
        "formula": "Latest HRV / Mean HRV × 100",
        "criteria": {"low": "<90", "optimal": "100–125"},
        },
        "HRVStability": {
            "framework": "Variability Index",
            "formula": "1 - (std / mean) (14d)",
            "criteria": {"low": "<0.7", "optimal": ">0.85"},
        },
        "HRVTrend": {
            "framework": "Short-Term HRV Trend",
            "formula": "Linear slope (7d)",
            "criteria": {"low": "<0", "optimal": ">=0"},
        },

    },

    "metadata": {
        "framework_chain": [
            "Seiler", "Banister", "Foster", "San Millán", "Friel",
            "Sandbakk", "Skiba", "Coggan", "Noakes"
        ],
        "unified_framework": "v5.1",
        "audit_validation": "Tier-2 verified, event-only totals enforced",
        "variance": "<= 2%",
        "last_revision": "2025-11-03"
    }
}

# Alias for compatibility with derived metrics imports
PROFILE_DATA = COACH_PROFILE
