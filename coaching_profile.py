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
