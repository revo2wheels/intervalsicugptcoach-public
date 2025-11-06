"""
coaching_profile.py — Unified Coaching Profile (v16.1)
Structured reference of frameworks, formulas, and methodology anchors.
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


COACH_PROFILE = {
    "version": "v16.1",
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
        "FatOxidationIndex": {
            "framework": "San Millán Zone 2 Model",
            "formula": "(1 - |IF - 0.7| / 0.1) × (1 - Decoupling / 10)",
            "criteria": {"optimal": ">=0.80", "moderate": "0.60–0.79", "low": "<0.60"},
            "placement": "Training Quality section",
        },
        "BenchmarkIndex": {
            "framework": "Friel Functional Benchmarking",
            "formula": "(FTP_current / FTP_prior) - 1",
            "criteria": { "productive": "+2–5%", "stagnant": "0%", "regression": ">−3%" },
        },
        "SpecificityIndex": {
            "framework": "Friel Specificity Ratio",
            "formula": "race_specific_hours / total_hours",
            "criteria": {"peak": "0.70–0.90", "build": "0.50–0.69", "base": "<0.50"},
        },
        "ConsistencyIndex": {
            "framework": "Friel Consistency Metric",
            "formula": "completed_sessions / planned_sessions",
            "criteria": {"consistent": ">=0.90", "variable": "0.75–0.89", "inconsistent": "<0.75"},
        },
        "AgeFactor": {
            "framework": "Friel Aging Adaptation",
            "formula": "ATL_adj = ATL × (1 - 0.005 × (Age - 40))",
        },
        "PolarisationIndex": {
            "framework": "Seiler 80/20 Model",
            "formula": "((Z1% + Z3%) - Z2%) / 100",
            "criteria": {"polarised": ">0.50", "mixed": "0.30–0.49", "threshold": "<0.30"},
        },
        "Monotony": {
            "framework": "Foster Monotony",
            "formula": "Mean_7d / SD_7d",
        },
        "Strain": {
            "framework": "Foster Strain",
            "formula": "Monotony × ΣLoad_7d",
        },
        "DurabilityIndex": {
            "framework": "Sandbakk Durability",
            "formula": "1 - (PowerDrop% / 100)",
        },
        "TRIMP": {
            "framework": "Banister Load Model",
            "formula": "Duration × HR_ratio × e^(1.92 × HR_ratio)",
        },
        "Readiness": {
            "framework": "Noakes Central Governor",
            "formula": "0.3×Mood + 0.3×Sleep + 0.2×Stress + 0.2×Fatigue",
        }
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
