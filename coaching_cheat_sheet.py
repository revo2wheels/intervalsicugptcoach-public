#!/usr/bin/env python3
"""
coaching_cheat_sheet.py — Unified v16.17 Coaching Reference
Contains static thresholds, labels, and helper summaries for derived metrics.
"""
import pandas as pd

# --- Global Coaching Cheat Sheet Dictionary ---
CHEAT_SHEET = {}

CHEAT_SHEET["meta"] = {
    "framework": "V5.1 Unified Reporting Framework",
    "version": "v16.17",
    "last_updated": "2026-03-18",
    "source": "Unified Coaching Reference (Intervals + Seiler + Banister + Treff)"
}

# === Thresholds ===
CHEAT_SHEET["thresholds"] = {
    "ACWR": {"green": (0.8, 1.3), "amber": (0.6, 1.5)},
    "Monotony": {"green": (1.0, 2.0), "amber": (0.8, 2.5)},
    "Strain": {
        "green": (0, 2500),
        "amber": (2500, 4000),
        "red": (4000, 8000)
    },
    "FatigueTrend": {
        "green": (-10, 10),      # stable / balanced
        "amber": (-20, 20),      # moderate unload or accumulation
        "red": (20, 99),         # strong accumulation
    },
    "StressTolerance": {
        "green": (0.8, 1.2),
        "amber": (0.6, 1.4),
        "red": (1.4, 3.0)
    },
    "LIR": {"green": (0.8, 1.2), "amber": (0.6, 1.4), "red": (0.0, 0.6)},
    "EnduranceReserve": {"green": (1.2, 2.0), "amber": (0.8, 1.2), "red": (0.0, 0.8)},
    "FatOxEfficiency": {"green": (0.4, 0.8), "amber": (0.3, 0.9)},
    "FOxI": {"green": (30, 80), "amber": (20, 90)},          # FatOx Index %
    "CUR": {"green": (30, 70), "amber": (20, 80)},        # Carbohydrate Utilisation Ratio
    "GR": {"green": (0.5, 2.0), "amber": (0.3, 3.0)},         # Glucose Ratio
    "MES": {"green": (20, 100), "amber": (10, 120)},          # Metabolic Efficiency Score
    "ACWR_Risk": {"green": (0, 1), "amber": (1, 1)},          # Placeholder to silence undefined
    "ZQI": {
        "green": (5, 15),
        "amber": (3, 5),
        "red": (0, 3)
    },
    "Durability": {"green": (0.9, 1.2),"amber": (0.7, 0.9),"red": (0.0, 0.7)},
    "IFDrift": {"green": (0.0, 0.05), "amber": (0.05, 0.10), "red": (0.10, 1.0)},
    "Lactate": {"lt1_mmol": 2.0,"lt2_mmol": 4.0,"corr_threshold": 0.6},
    "FatigueResistance": {"green": (0.9, 1.1), "amber": (0.8, 1.2)},  # ratio of long vs short power
    "EfficiencyFactor": {
        "green": (1.4, 2.5),
        "amber": (1.0, 1.4),
        "red": (0.0, 1.0)
    },   #Power-to-HR ratio (np / avg HR)
    "LoadVariabilityIndex": {"green": (0.7, 1.0),"amber": (0.4, 0.69),"red": (0.0, 0.39)}, #replaced RI for now
    "EnduranceDecay": {
        "green": (0.0, 0.03),   # <3%
        "amber": (0.03, 0.05),  # 3–5%
        "red": (0.05, 1.0)      # >5%
    },
    # === Wellness Metrics ===
    "HRV": {
        "green": (60, 200),
        "amber": (40, 60),
        "red": (0, 40)
    },
    "RestingHR": {
        "green": (32, 60),
        "amber": (61, 70),
        "red": (71, 200)
    },
    "RestingHRDelta": {
        "green": (-2, 2),
        "amber": (2, 5),
        "red": (5, 50)
    },
    "SleepQuality": {
        "green": (80, 100),
        "amber": (65, 80),
        "red": (0, 65)
    },

    # --- HRV family ---
    "HRVBalance": {
        "green": (1.0, 1.3),
        "amber": (0.9, 1.0),
        "red": (0.0, 0.9)
    },
    "HRVStability": {
        "green": (0.8, 1.0),
        "amber": (0.65, 0.8),
        "red": (0.0, 0.65)
    },
    "HRVTrend": {
        "green": (0.0, 5.0),
        "amber": (-2.0, 0.0),
        "red": (-100.0, -2.0)
    },
    # --- Performance Intelligence ---
    #"mean_depletion_pct_7d": {"green":(0.2,0.45),"amber":(0.45,0.7)},
    "moderate_depletion_sessions_7d": {
        "green": (0, 3),
        "amber": (4, 6),
        "red": (7, 10)
    },
    "high_depletion_sessions_7d": {"green":(0,2),"amber":(3,4)},
    #"mean_depletion_pct_90d": {"green":(0.15,0.35),"amber":(0.35,0.55)},
    "high_depletion_sessions_90d": {"green":(0,6),"amber":(7,10)},
    #"mean_decoupling_7d": {"green":(0,5),"amber":(5,8)},
    "high_drift_sessions_7d": {"green":(0,2),"amber":(3,99)},
    #"mean_decoupling_90d": {"green":(0,4),"amber":(4,7)},
    "high_drift_sessions_90d": {"green":(0,10),"amber":(11,999)},
    "rolling_joules_above_ftp_7d": {
        "green": (0,150000),
        "amber": (150000,250000),
        "red": (250000,1000000),
    },
    "high_intensity_days_7d": {
        "green": (0,2),
        "amber": (3,4),
        "red": (5,7)
    },
    "high_intensity_sessions_90d": {"green":(8,25),"amber":(25,40)},
    "mean_training_load_90d": {"green":(40,70),"amber":(70,90)},
    # --- W′ Balance / Anaerobic Load (Weekly) ---
    "WBalDepletion": {
        "green": (0.0, 0.25),
        "amber": (0.25, 0.45),
        "red": (0.45, 1.0),
    },
    "AnaerobicContribution": {
        "green": (0.0, 0.70),
        "amber": (0.70, 0.90),
        "red": (0.90, 1.0),
    },
    "w_prime_divergence_7d": {
        "green": (-0.10, 0.15),
        "amber": (0.15, 0.30),
        "red": (0.30, 1.00)
    },
    "w_prime_divergence_90d": {
        "green": (-0.1, 0.2),
        "amber": (0.2, 0.5),
        "red": (0.5, 1.0)
    },
    # ---HRV ---
    "HRVDeviation": {
        "green": (-5, 15),
        "amber": (-15, -5),
        "red": (-100, -15),
        "high_spike": (15, 40)
    },
    "AutonomicStatus": {
        "green": (0.97, 1.30),
        "amber": (0.92, 0.97),
        "red": (0.00, 0.92)
    },
    # ================== POLARISATION THRESHOLDS ==================
    # IMPORTANT SEMANTIC NOTE:
    # - "Polarisation" is the Seiler 3-zone intensity distribution (Seiler 2010;
    #   Stöggl & Sperlich 2015): value = % time in Seiler zone 1, semantic_state =
    #   distribution type by zone order. No published good/bad bands, so it has no
    #   thresholds here and classifies as informational.
    #
    # - "PolarisationIndex" is the Treff et al. 2019 Polarization-Index:
    #   log10((Z1 / Z2) × Z3 × 100) on the 3-zone collapse Z1+Z2 | Z3+Z4 | Z5–Z7
    #   (same as Intervals.icu). Single published cut-off: > 2.00 = polarised.
    #
    # - "Polarisation_fused" and "Polarisation_combined" are the same Treff index
    #   computed on zones.fused (dominant sport) and zones.combined (all sports,
    #   HR where no power). Same single cut-off.

    # --- Power-only Treff Polarization-Index (2019) ---
    "PolarisationIndex": {
        # Treff 2019 has one cut-off: > 2.00 = polarised.
        # Below it the distribution is "not polarised" (no good/bad band),
        # so it classifies as informational.
        "green": (2.00, 10.00),  # polarised
    },
    # --- Fused HR + Power (dominant sport), Treff index ---
    "Polarisation_fused": {
        "green": (2.00, 10.00),  # polarised (Treff 2019)
    },
    # --- Combined HR + Power (all sports), Treff index ---
    "Polarisation_combined": {
        "green": (2.00, 10.00),  # polarised (Treff 2019)
    },
    "TSB": {
        "transition": [10, 999],
        "fresh": [5, 10],
        "neutral": [-5, 5],
        "productive_fatigue": [-30, -5],
        "overreached": [-999, -30]
    },
    # ================================================================
    # 🧠 SCIENTIFICALLY VALIDATED PHASE DETECTION (v17.4)
    # ================================================================
    # These PhaseBoundaries are based on:
    # - Banister et al. (1975–1991): Impulse-Response Model (CTL/ATL → TSB)
    # - Mujika & Padilla (2003, 2010): Tapering and Performance Maintenance
    # - Seiler (2010, 2020): Endurance Intensity Distribution (Base/Build/Peak)
    # - Issurin (2008): Block Periodisation Model
    # - Friel (2009): Practical endurance periodisation framework
    #
    # In this model:
    #   trend_min / trend_max  → week-to-week % change in training load (TSS)
    #   acwr_max               → acute:chronic workload ratio (ATL/CTL) ceiling
    #   lvi_min                 → Load Variability Index (fatigue balance) floor
    #
    # These values align with both academic sources and Intervals.icu's
    # TSB (Training Stress Balance) fatigue-freshness mapping:
    #     transition: [10, 999]   → very fresh / detraining
    #     fresh: [5, 10]          → race-ready
    #     grey: [-5, 5]           → balanced / neutral
    #     optimal: [-30, -5]      → productive fatigue
    #     high_risk: [-999, -30]  → overreached
    # ================================================================

   "PhaseBoundaries": {

        # 💤 RECOVERY → extreme unload / detraining
        "Recovery": {
            "trend_min": -1.00,
            "trend_max": -0.50,
            "acwr_max": 1.0,
            "lvi_min": 0.6
        },

        # 📉 TAPER → strong unload (race prep)
        "Taper": {
            "trend_min": -0.50,
            "trend_max": -0.15,
            "acwr_max": 1.1,
            "lvi_min": 0.8
        },

        # 🧘 DELOAD → controlled unload inside block
        "Deload": {
            "trend_min": -0.15,
            "trend_max": -0.05,
            "acwr_max": 1.2,
            "lvi_min": 0.7
        },

        # 🧱 BASE → stable / slight variation
        "Base": {
            "trend_min": -0.05,
            "trend_max": 0.05,
            "acwr_max": 1.2,
            "lvi_min": 0.75
        },

        # 🏁 PEAK → stable but fresh (slight drop or flat)
        "Peak": {
            "trend_min": 0.05,
            "trend_max": 0.10,
            "acwr_max": 1.15,
            "lvi_min": 0.8
        },

        # 📈 BUILD → progressive overload
        "Build": {
            "trend_min": 0.10,
            "trend_max": 0.40,
            "acwr_max": 1.3,
            "lvi_min": 0.65
        }
    },

    # ================================================================
    # 🧠 PHASE DETECTION ENGINE v2.1
    # ================================================================
    # V2 separates:
    #   1) PhaseBoundaries  → raw weekly load-pattern classification
    #   2) PhaseRulesV2     → sequence-aware refinement layer
    #
    # PhaseBoundaries remain deterministic and threshold-based.
    # PhaseRulesV2 is applied AFTER raw phase detection.
    #
    # Core metrics:
    #   tss        → weekly training load
    #   delta      → smoothed week-to-week % change in TSS
    #   ctl        → chronic training load / fitness
    #   atl        → acute training load / fatigue
    #   tsb        → ctl - atl
    #   acwr       → atl / ctl
    #
    # V1 classified load pattern only.
    # V2 classifies load pattern + periodisation context.
    # ================================================================

    "phase_detection_v2": {

        "version": "2.1",

        # ============================================================
        # RAW LOAD-PATTERN CLASSIFIER
        # ============================================================

        "PhaseBoundaries": {

            "Recovery": {
                "trend_min": -1.00,
                "trend_max": -0.30,
                "acwr_max": 0.85,
                "tsb_min": 5
            },

            "Taper": {
                "trend_min": -0.40,
                "trend_max": -0.12,
                "acwr_max": 1.00,
                "tsb_min": 0
            },

            "Deload": {
                "trend_min": -0.12,
                "trend_max": -0.01,
                "acwr_max": 1.10
            },

            "Base": {
                "trend_min": -0.01,
                "trend_max": 0.05,
                "acwr_max": 1.15
            },

            "Peak": {
                "trend_min": -0.15,
                "trend_max": 0.02,
                "acwr_max": 1.00,
                "tsb_min": 8
            },

            "Build": {
                "trend_min": 0.03,
                "trend_max": 0.30,
                "acwr_max": 1.30
            }
        },

        # ============================================================
        # SEQUENCE-AWARE REFINEMENT RULES
        # ============================================================

        "PhaseRulesV2": {

            "version": "phase_rules_v2.1",

            "execution_order": [
                "peak_after_taper",
                "true_recovery_strict",
                "transition_after_recovery",
                "prevent_false_peak",
                "default_raw_phase"
            ],

            # --------------------------------------------------------
            # RULE 1 — PEAK AFTER TAPER
            # --------------------------------------------------------

            "peak_after_taper": {
                "if": {
                    "prev_phase_final": "Taper",
                    "delta_gt": 0.00,
                    "acwr_lte": 1.10
                },
                "then": {
                    "phase_final": "Peak"
                }
            },

            # --------------------------------------------------------
            # RULE 2 — TRUE RECOVERY
            # --------------------------------------------------------

            "true_recovery_strict": {
                "if": {
                    "acwr_lt": 0.65,
                    "delta_lt": -0.10,
                    "tsb_gt": 5
                },
                "then": {
                    "phase_final": "Recovery"
                }
            },

            # --------------------------------------------------------
            # RULE 3 — TRANSITION AFTER RECOVERY
            # --------------------------------------------------------

            "transition_after_recovery": {
                "if": {
                    "prev_phase_final": "Recovery",
                    "abs_delta_lt": 0.15
                },
                "then": {
                    "phase_final": "Transition"
                }
            },

            # --------------------------------------------------------
            # RULE 4 — PREVENT FALSE PEAK
            # --------------------------------------------------------

            "prevent_false_peak": {
                "if": {
                    "phase_raw": "Peak",
                    "tsb_lt": 5
                },
                "then": {
                    "phase_final": "Base"
                }
            },

            # --------------------------------------------------------
            # RULE 5 — DEFAULT
            # --------------------------------------------------------

            "default_raw_phase": {
                "then": {
                    "phase_final": "phase_raw"
                }
            }
        }
    },


    "ESPE": {
        "Ride": {
            "anaerobic": {"strong": 3.0, "moderate": 1.5, "mild": 0.8, "decline": -1.5},
            "vo2": {"strong": 3.0, "moderate": 1.5, "mild": 0.8, "decline": -1.5},
            "threshold": {"strong": 2.0, "moderate": 1.0, "mild": 0.5, "decline": -1.0},
            "aerobic": {"strong": 1.5, "moderate": 0.7, "mild": 0.4, "decline": -1.0}
        },

        "Run": {
            "anaerobic": {"strong": 2.0, "moderate": 1.0, "mild": 0.5, "decline": -1.0},
            "vo2": {"strong": 2.0, "moderate": 1.0, "mild": 0.5, "decline": -1.0},
            "threshold": {"strong": 1.0, "moderate": 0.5, "mild": 0.3, "decline": -0.8},
            "aerobic": {"strong": 1.0, "moderate": 0.5, "mild": 0.3, "decline": -0.8}
        },

        # Cycling curve phenotypes
        "curve_slope_time_trialist": -0.48,
        "curve_slope_endurance_specialist": -0.55,
        "curve_slope_all_rounder": -0.62,
        "curve_slope_punchy_climber": -0.68,
        "curve_slope_punchy": -0.75,
        "curve_slope_anaerobic_specialist": -0.85,

        # Running curve phenotypes
        "run_curve_slope_endurance_runner": -0.42,
        "run_curve_slope_balanced_runner": -0.50,
        "run_curve_slope_punchy_runner": -0.60,

        "neutral_band": 0.75,

        "curve_quality": {
            "excellent": 0.85,
            "good": 0.75
        },
        "system_timeline_map": {
            "strong_gain": "building",
            "moderate_gain": "building",
            "mild_gain": "emerging",
            "stable": "maintaining",
            "decline": "detraining"
        },
        "pdr_reference_duration": "5m",

        "curve_windows": {
            "default_days": 84,
            "comparison_model": "rolling_equal_window"
        },
    }
}

CHEAT_SHEET["training_load_pattern"] = {
    "meta": {
        "name": "Training Load Pattern",
        "scope": "training_load_only",
        "context_window": "7d_with_21_28d_baseline",
        "description": (
            "Current 7-day training-load pattern resolved against recent "
            "baseline and CTL-based capacity metrics."
        ),
        "inputs": {
            "ACWR": "EWMA acute/chronic load ratio, usually 7d vs 28d",
            "StressTolerance": "7d weekly load relative to CTL capacity",
            "Strain": "7d load multiplied by 7d monotony",
            "FatigueTrend": "recent 7d daily load average vs prior 21d daily baseline"
        }
    },

    "states": {
        "balanced_load": {
            "label": "BALANCED LOAD",
            "status": "balanced",
            "meaning": (
                "Current 7-day load is stable against recent baseline "
                "and current capacity."
            )
        },

        "controlled_unload": {
            "label": "CONTROLLED UNLOAD",
            "status": "unloading",
            "meaning": (
                "Current 7-day load is below the prior 21-day baseline "
                "while acute/chronic and capacity ratios remain safe."
            )
        },

        "building_load": {
            "label": "BUILDING LOAD",
            "status": "building",
            "meaning": (
                "Current 7-day load is rising above the prior 21-day baseline "
                "while acute/chronic balance remains controlled."
            )
        },

        "high_strain": {
            "label": "HIGH STRAIN",
            "status": "strain",
            "meaning": (
                "Current 7-day load pattern is elevated through acute load, "
                "capacity pressure, strain, or recent load trend."
            )
        },

        "overload_risk": {
            "label": "OVERLOAD RISK",
            "status": "risk",
            "meaning": (
                "Current load exceeds safe acute, capacity, strain, "
                "or recent trend limits."
            )
        },

        "under_stimulus": {
            "label": "UNDER-STIMULUS",
            "status": "low",
            "meaning": (
                "Current 7-day load is low relative to chronic baseline "
                "and prior 21-day trend."
            )
        },

        "load_unknown": {
            "label": "LOAD UNKNOWN",
            "status": "unknown",
            "meaning": "Insufficient load diagnostics to resolve pattern."
        }
    },

    "rules": {
        "overload_risk": {
            "priority": 1,
            "any": {
                "ACWR_gt": 1.5,
                "StressTolerance_gt": 1.4,
                "Strain_gt": 4000,
                "FatigueTrend_gt": 40
            }
        },

        "high_strain": {
            "priority": 2,
            "any": {
                "ACWR_gt": 1.3,
                "StressTolerance_gt": 1.2,
                "Strain_gt": 3000,
                "FatigueTrend_gt": 20
            }
        },

        "under_stimulus": {
            "priority": 3,
            "all": {
                "ACWR_lt": 0.8,
                "FatigueTrend_lt": -20
            }
        },

        "controlled_unload": {
            "priority": 4,
            "all": {
                "ACWR_between": [0.8, 1.3],
                "StressTolerance_between": [0.8, 1.2],
                "FatigueTrend_lte": -10
            }
        },

        "building_load": {
            "priority": 5,
            "all": {
                "ACWR_between": [0.8, 1.3],
                "StressTolerance_between": [0.8, 1.2],
                "FatigueTrend_between": [10, 20]
            }
        },

        "balanced_load": {
            "priority": 6,
            "all": {
                "ACWR_between": [0.8, 1.3],
                "StressTolerance_between": [0.8, 1.2],
                "Strain_lt": 2500,
                "FatigueTrend_between": [-10, 10]
            }
        }
    }
}

CHEAT_SHEET["physiology_state"] = {
    "meta": {
        "name": "Physiology State",
        "scope": "wellness_physiology_only",
        "context_window": "42d wellness with current load state",
        "description": (
            "Current physiology response resolved from autonomic, recovery, sleep, "
            "resting HR, subjective, and load-pressure signals."
        ),
        "inputs": {
            "hrv_ratio": "latest HRV divided by 42-day HRV mean",
            "hrv_trend": "recent HRV direction",
            "resting_hr_delta": "recent resting HR versus baseline",
            "sleep_score": "recent sleep quality score",
            "tsb": "current training stress balance",
            "subjective": "fatigue, stress, soreness, mood, motivation when available"
        }
    },

    "states": {
        "fresh_stable": {
            "label": "FRESH / STABLE",
            "status": "positive",
            "meaning": "Autonomic markers are favourable and load pressure is low."
        },
        "stable": {
            "label": "STABLE",
            "status": "neutral",
            "meaning": "Physiology markers are broadly normal with no clear suppression signal."
        },
        "watch": {
            "label": "WATCH",
            "status": "watch",
            "meaning": "One or more physiology markers show mild strain or recovery inconsistency."
        },
        "suppressed": {
            "label": "SUPPRESSED",
            "status": "risk",
            "meaning": "Autonomic or recovery markers suggest suppressed physiology under load."
        },
        "strained": {
            "label": "STRAINED",
            "status": "strain",
            "meaning": "Recovery markers and load pressure indicate elevated physiological strain."
        },
        "unknown": {
            "label": "UNKNOWN",
            "status": "unknown",
            "meaning": "Insufficient wellness data to resolve physiology state."
        }
    }
}

CHEAT_SHEET["metric_groups"] = {
    # --- WDRM ---
    "mean_depletion_pct_7d": "AnaerobicRepeatability",
    "max_depletion_pct_7d": "AnaerobicRepeatability",
    "moderate_depletion_sessions_7d": "AnaerobicRepeatability",
    "high_depletion_sessions_7d": "AnaerobicRepeatability",
    "mean_depletion_pct_90d": "AnaerobicRepeatability",
    "max_depletion_pct_90d": "AnaerobicRepeatability",
    "moderate_depletion_sessions_90d": "AnaerobicRepeatability",
    "high_depletion_sessions_90d": "AnaerobicRepeatability",
    # --- ISDM ---
    "mean_decoupling_7d": "DurabilityProfile",
    "mean_decoupling_signed_7d": "DurabilityProfile",
    "max_decoupling_7d": "DurabilityProfile",
    "high_drift_sessions_7d": "DurabilityProfile",

    "mean_decoupling_90d": "DurabilityProfile",
    "mean_decoupling_signed_90d": "DurabilityProfile",
    "high_drift_sessions_90d": "DurabilityProfile",
    # --- NDLI ---
    "rolling_joules_above_ftp_7d": "NeuralDensity",
    "high_intensity_days_7d": "NeuralDensity",
    "high_intensity_sessions_90d": "NeuralDensity",
    "mean_variability_index_7d": "NeuralDensity",
    "mean_efficiency_factor_7d": "NeuralDensity",
    # --- Alignment ---
    "delta_ratio": "LoadAlignment",
}


# === Phase-Aware Threshold Adjustments (optional overrides) ===
CHEAT_SHEET["phase_thresholds"] = {}

CHEAT_SHEET["subjective_scales"] = {

    # 1–4 scales
    "soreness": {
        1: "low",
        2: "avg",
        3: "high",
        4: "extreme"
    },

    "fatigue": {
        1: "low",
        2: "avg",
        3: "high",
        4: "extreme"
    },

    "stress": {
        1: "low",
        2: "avg",
        3: "high",
        4: "extreme"
    },

    "mood": {
        1: "great",
        2: "good",
        3: "ok",
        4: "grumpy"
    },

    "motivation": {
        1: "extreme",
        2: "high",
        3: "avg",
        4: "low"
    },

    "injury": {
        1: "none",
        2: "niggle",
        3: "poor",
        4: "injured"
    },

    "hydration": {
        1: "good",
        2: "ok",
        3: "poor",
        4: "bad"
    },

    # 1–5 scale (separate)
    "readiness": {
        1: "very poor",
        2: "poor",
        3: "fair",
        4: "good",
        5: "excellent"
    },
    "icu_rpe": {
        1: "nothing at all",
        2: "very easy",
        3: "easy",
        4: "comfortable",
        5: "slightly challenging",
        6: "difficult",
        7: "hard",
        8: "very hard",
        9: "extremely hard",
        10: "max effort"
    },
    "rpe_emoji": {
        1: "1️⃣",
        2: "2️⃣",
        3: "3️⃣",
        4: "4️⃣",
        5: "5️⃣",
        6: "6️⃣",
        7: "7️⃣",
        8: "8️⃣",
        9: "9️⃣",
        10: "🔟"
    },
    "feel": {
        5: "weak",
        4: "poor",
        3: "normal",
        2: "good",
        1: "strong"
    },
    "feel_emoji": {
        5: "😞",
        4: "🙁",
        3: "😐",
        2: "🙂",
        1: "😄"
    }
}
# === Polarisation Model Mapping (canonical) ===
CHEAT_SHEET["polarisation_models"] = {
    "PolarisationIndex": [
        {
            "label": "not_polarised",
            "range": (0.00, 2.00),
            "description": "Not polarised (Treff 2019, PI ≤ 2.00)."
        },
        {
            "label": "polarised",
            "range": (2.00, 10.00),
            "description": "Treff-defined polarised intensity distribution (PI > 2.00)."
        },
    ],
    "Polarisation": [
        {"label": "hiit", "rule": "Z3 > Z2 and Z3 > 0.499 × (Z1 + Z2)", "description": "High-intensity dominant distribution."},
        {"label": "polarised", "rule": "Z3 > Z2 and Z1 > Z2", "description": "Polarised: mostly low intensity, more high than moderate."},
        {"label": "base", "rule": "Z1 > 3.99 × Z2 and Z1 > 3 × (Z2 + Z3)", "description": "Base: low intensity strongly dominant."},
        {"label": "pyramidal", "rule": "1.4 × Z2 < Z1 < 3.01 × Z2 and Z2 > 1.4 × Z3", "description": "Pyramidal: low > moderate > high."},
        {"label": "threshold", "rule": "Z1 < 4 × Z2 and Z2 > 0.5 × Z3", "description": "Threshold: substantial moderate (LT1–LT2) work."},
        {"label": "unique", "rule": "none of the above", "description": "Does not match a standard distribution type."},
    ],
}

# ------------------------------------------------------------
# Qualitative → Traffic-light classification aliases
# ------------------------------------------------------------
# These map descriptive metric "state" or "status" labels
# (e.g. "productive", "optimal", "fatigued") to UI colors.
# Used by build_insight_view() and other semantic builders.
# ------------------------------------------------------------

CLASSIFICATION_ALIASES = {

    # ---------------------------
    # GREEN (Desirable states)
    # ---------------------------
    "productive": "green",
    "optimal": "green",
    "balanced": "green",
    "healthy": "green",
    "normal": "green",
    "recovering": "green",
    "polarised": "green",
    "aligned": "green",
    "strong": "green",
    "consistent": "green",
    "low": "green",
    "green": "green",
    "productive_load": "green",

    # ---------------------------
    # AMBER (Watch / transitional)
    # ---------------------------
    "moderate": "amber",
    "borderline": "amber",
    "pyramidal": "amber",
    "aggressive": "amber",
    "variable": "amber",
    "underload": "amber",
    "high_polarised": "amber",
    "threshold": "amber",
    "moderate_low": "amber",
    "moderate_high": "amber",
    "accumulating": "amber",
    "amber": "amber",
    "adaptation_pressure": "amber",

    # ---------------------------
    # RED (Risk / undesirable)
    # ---------------------------
    "overload": "red",
    "overreach": "red",
    "overreach_risk": "red",
    "overreached": "red",
    "inconsistent": "red",
    "depleted": "red",
    "critical": "red",
    "extreme": "red",
    "high": "red",
    "extreme_accumulation": "red",
    "red": "red",
    "maladaptation_risk": "red"
}

# === Context ===
CHEAT_SHEET["context"] = {
    "ACWR": (
        "EWMA Acute:Chronic Load Ratio — compares acute vs chronic weighted loads. "
        "0.8–1.3 = productive training, <0.8 = recovery or detraining, >1.5 = overload/injury risk."
    ),
    "Monotony": "1–2 shows healthy variation; >2.5 means repetitive stress pattern.",
    "Strain": (
        "Modified Foster Strain (ΣTSS_7d × Monotony). "
        "Values >3500 indicate elevated combined load and variability risk; "
        "interpret relative to athlete baseline."
    ),
    "FatigueTrend": (
        "FatigueTrend is calculated as the percentage change between the most recent "
        "7-day daily load average and the preceding 21-day daily load average. "
        "A value near 0% indicates stable load, a positive value indicates recent "
        "load accumulation, and a negative value indicates unloading."
    ),
    "ZQI": "Zone Quality Index (%) 5-15 high-intensity time is normal <3% too easy, >20% too intense or erratic pacing.",
    "FatOxEfficiency": "0.4–0.8 means balanced fat oxidation; lower = carb dependence.",
    "FOxI": "FatOx index %; higher values mean more efficient aerobic base.",
    "CUR": "Carbohydrate Utilisation Ratio; 30–70 indicates balanced metabolic use.",
    "GR": "Glucose Ratio; >2 indicates excess glycolytic bias.",
    "MES": "Metabolic Efficiency Score; >20 is good endurance economy.",
    "ACWR_Risk": "Used internally for stability check.",
    "StressTolerance": (
        "Capacity-adjusted weekly load ratio (ΣTSS_7d / (CTL × 7)). "
        "1.0 indicates weekly load equals chronic fitness baseline. "
        "Values >1.2 reflect overload relative to adaptive capacity; "
        "<0.8 indicates under-stimulation."
    ),
    "Durability": "Durability index — ratio of power/HR stability under fatigue; >0.9 indicates good endurance robustness.",
    "LIR": "Load Intensity Ratio — ratio of total intensity to total duration; 0.8–1.2 indicates balanced training intensity distribution.",
    "EnduranceReserve": "Endurance Reserve — ratio of aerobic durability to fatigue index; >1.2 indicates strong endurance foundation.",
    "IFDrift": "IF Drift — change in Intensity Factor (power vs HR) over time; <5% stable, >10% indicates endurance fatigue or overheating.",
    "Lactate": (
        "Standard lab defaults (Mader & Heck, 1986). "
        "LT1≈2 mmol/L corresponds to the first sustained rise in blood lactate, "
        "while LT2≈4 mmol/L approximates the maximal lactate steady-state (MLSS). "
        "Override with athlete-specific testing or field protocols."),
    "FatigueResistance": (
        "Ratio of endurance (long-duration) power to threshold (short-duration) power. "
        "Values near 1.0 indicate strong fatigue resistance — ability to sustain output under fatigue. "
        "<0.9 suggests drop-off under endurance load."
    ),
    "EfficiencyFactor": (
        "Ratio of power to heart rate, representing aerobic efficiency. "
        "Higher values indicate improved aerobic conditioning and cardiovascular economy. "
        "Values between 1.8–2.2 are typical for trained endurance athletes."
    ),
    "HRV": "Heart-rate variability balance — indicator of parasympathetic recovery.",
    "RestingHR": "Resting heart rate trend — elevated HR indicates fatigue or stress.",
    "SleepQuality": "Average Garmin sleep score — proxy for sleep recovery and readiness.",
    "LoadVariabilityIndex": (
            "Inverse Monotony model (Foster 2001): 1 - (Monotony / 5). "
            "Represents weekly load variability. "
            "Higher values indicate healthier variation in daily training load."
    ),
    "HRVBalance": "HRV compared to 42-day mean — shows short-term recovery status.",
    "HRVStability": "Consistency of HRV — lower variability = better physiological stability.",
    "HRVTrend": "Direction of HRV change — rising indicates improving recovery.",
    # --- Polarisation Variants (clarified sources) ---
    "Polarisation": (
        "Seiler 3-zone intensity distribution (Seiler 2010; Stöggl & Sperlich 2015). "
        "7 power zones are collapsed to Seiler's 3 (Z1+Z2 | Z3+Z4 | Z5–Z7, same grouping as Intervals.icu). "
        "The value is the % of training time in Seiler zone 1 (below LT1); the distribution type "
        "(polarised, pyramidal, threshold, base, HIIT or unique) comes from the zone order, using "
        "Intervals.icu's rules. ⚙️ *Power-based; HR used only when no power.*"
    ),
    "PolarisationIndex": (
        "Treff Polarization-Index (Treff et al. 2019). "
        "Calculated as log10((z1 / z2) × z3 × 100) after collapsing 7-zone power data "
        "to the 3-zone Seiler model (z1=Z1+Z2, z2=Z3+Z4, z3=Z5+Z6+Z7; the same grouping Intervals.icu uses), "
        "then renormalising the collapsed zones so z1+z2+z3=1 before applying the formula. "
        "If z2 = 0, Treff's Eq. 2 is used: log10(z1 / 0.01 × (z3 − 0.01) × 100). "
        "If z3 = 0 the index is 0 by definition; it is not valid (null) when z3 > z1. "
        ">2.00 = polarised distribution; ≤2.00 = not polarised. "
        "⚙️ Power-only metric using normalised 3-zone distribution."
    ),
    "Polarisation_fused": (
        "Treff 2019 Polarization-Index computed on the dominant sport's fused zones "
        "(power where available, HR otherwise), using the same 3-zone collapse (Z1+Z2 | Z3+Z4 | Z5–Z7). "
        ">2.00 = polarised; ≤2.00 = not polarised. "
        "⚙️ *HR-based zones have no published 7-to-3 mapping, so treat HR-only values as indicative.*"
    ),
    "Polarisation_combined": (
        "Treff 2019 Polarization-Index computed on the combined distribution across all endurance "
        "sports (power where available, HR otherwise), using the same 3-zone collapse. "
        "Intended for athletes training mostly without power, or mixed. "
        ">2.00 = polarised; ≤2.00 = not polarised. "
        "⚙️ *Cross-discipline summary — lower precision than the power-based index.*"
    ),
    "WBalDepletion": (
        "Mean weekly W′ balance depletion expressed as a fraction of total W′ capacity. "
        "Represents how deeply anaerobic reserves are typically drawn during W′-capable sessions. "
        "<25% indicates light or controlled anaerobic exposure; >45% indicates repeated deep depletion."
    ),

    "AnaerobicContribution": (
        "Proportion of work above critical power relative to total W′ capacity during W′-engaged sessions. "
        "Values >0.90 indicate highly anaerobic-dominant intensity distribution when intensity is present."
    ),

    "WBalPattern": (
        "Temporal distribution pattern of W′ depletion across the reporting window. "
        "Used to identify clustering (e.g. weekend stacking) versus evenly distributed anaerobic stress."
    ),
    "AnaerobicRepeatability": (
        "WDRM (W′ Depletion & Repeatability Metric) quantifies depth and frequency "
        "of anaerobic reserve depletion across sessions. Higher values reflect repeated "
        "deep supra-threshold exposure."
    ),
    "DurabilityProfile": (
        "ISDM (Intensity Stability & Durability Model) reflects stability of effort over time. "
        "Decoupling magnitude indicates how stable the effort is. "
        "Durability state provides the resolved interpretation and must be used as the authoritative assessment."
    ),
    "NeuralDensity": (
        "NDLI (Neural Density Load Index) captures clustering of high-intensity "
        "work within short time windows (e.g. 72h). High density increases recovery demand."
    ),
    "LoadAlignment": (
        "Acute vs Chronic alignment compares current 7-day load expression "
        "against 90-day baseline. Ratios >1.4 suggest overload; <0.8 under-stimulation."
    ),
    "HRVDeviation": (
        "Percentage deviation of latest HRV from 42-day mean. "
        "Positive values suggest improved autonomic readiness; "
        "negative values suggest suppression."
    ),
    "AutonomicStatus": (
        "Ratio of latest HRV to 42-day mean. "
        "Values near 1.0 indicate stable autonomic balance. "
        "Suppression below 0.92 may indicate fatigue."
    ),
    "RestingHRDelta": (
        "Resting heart rate trend — elevated HR indicates fatigue or stress."
    ),
    "w_prime_divergence_7d": (
        "Difference between observed W′ depletion behaviour and expected endurance baseline. "
        "Positive values indicate higher-than-normal anaerobic utilisation, "
        "while negative values indicate lower-than-expected supra-threshold engagement."
    ),
    "w_prime_divergence_90d": (
        "Relative difference between rolling CP-derived W′ (performance model) "
        "and athlete profile W′ setting. Measures coherence between model-estimated "
        "anaerobic capacity and configured profile capacity."
    ),
    "load_recovery_state": (
        "Load–Recovery state describing the interaction between training load "
        "(ATL vs CTL) and autonomic recovery (HRV ratio). "
        "Balanced indicates load and recovery aligned. "
        "Productive_load indicates elevated load with stable recovery. "
        "Adaptation_pressure indicates recovery suppression under load. "
        "Maladaptation_risk indicates recovery breakdown relative to training stress."
    ),
    "EnduranceDecay": (
        "Endurance Decay represents aerobic durability measured as heart-rate decoupling "
        "during sustained efforts. Values below ~3% indicate strong durability and stable "
        "aerobic efficiency, while values above ~5% suggest cardiovascular drift and reduced "
        "fatigue resistance during prolonged work."
    ),
    "ProteinIntake": "Adequate protein intake (≈1.6–2.2 g/kg; ACSM/ISSN consensus) supports recovery, muscle repair, and adaptation to training load.",
    "CarbohydrateAvailability": "Carbohydrate availability (≈3–10 g/kg depending on training load; IOC/ACSM guidelines) determines glycogen replenishment and endurance capacity.",
    "FatIntake": "Fat intake (≈0.8–1.2 g/kg; sports nutrition consensus) contributes to hormonal stability and long-term energy balance."
}

CHEAT_SHEET["coaching_links"] = {
    # --- Derived Metric Coaching Links ---
    "ACWR": "If ACWR > 1.5, reduce intensity and focus on recovery to avoid overload. If ACWR < 0.8, gradually increase training load with controlled progression to build endurance.",
    "Monotony": "If Monotony > 2.5, introduce more variation in training or implement a deload week to reduce repetitive stress.",
    "Strain": "If Strain > 3000, monitor for signs of overreach and consider more rest or deloading. If Strain > 3500, consider reducing volume or intensity temporarily.",
    "FatigueTrend": (
        "If FatigueTrend drops below -10%, recent 7-day load is below the prior "
        "21-day baseline, indicating unloading or reduced training stimulus. "
        "If FatigueTrend rises above +10%, recent load is accumulating relative "
        "to the prior baseline — monitor recovery, intensity density, and planned load."
    ),
    "FatOxEfficiency": "If FatOxEfficiency is low (<0.6), focus on improving aerobic base with longer, low-intensity efforts.",
    "ZQI": "If ZQI > 20%, review pacing strategy; excessive high-intensity time could indicate erratic pacing or overtraining. Aim for 5-15% ZQI for balanced training.",
    "FOxI": "If FOxI is increasing, continue to prioritize low-intensity work to enhance fat metabolism. If it decreases, consider increasing your Zone 2 training duration.",
    "CUR": "If CUR is outside the green zone (30-70), adjust carbohydrate intake and fueling strategy to ensure balanced metabolic use during long sessions.",
    "GR": "If GR exceeds 2.0, focus on reducing glycolytic intensity and increase aerobic work. Ensure sufficient recovery to avoid over-reliance on carbs.",
    "MES": "If MES is below 20, work on improving metabolic efficiency by increasing endurance training with a focus on aerobic base and fat metabolism.",
    "StressTolerance": (
        "If StressTolerance >1.4, weekly load significantly exceeds chronic capacity — "
        "reduce volume or intensity and monitor recovery. "
        "If <0.8, stimulus may be insufficient for adaptation."
    ),
    "FatigueResistance": "If FatigueResistance <0.9, add longer sub-threshold intervals or extended endurance sessions. Maintain >0.95 to support long-duration performance.",
    "EfficiencyFactor": "If EfficiencyFactor is declining, focus on aerobic conditioning and recovery. Stable or increasing EF indicates improving endurance efficiency.",
    "LoadVariabilityIndex": "Low values indicate load is exceeding current physiological tolerance; moderate values suggest manageable stress; high values reflect positive load variability with adequate systemic capacity.",
        # --- Polarisation Variants Coaching Links ---
    "Polarisation": (
        "Read the distribution type against the training phase: base, pyramidal or threshold "
        "weeks are normal in foundation blocks; a polarised structure is typical in build or peak "
        "phases when high-intensity work is prescribed. Seiler's 80/20 refers to sessions, not minutes."
    ),
    "PolarisationIndex": (
        "PolarisationIndex >2.00 means a polarised week (Treff 2019); ≤2.00 means not polarised, "
        "which is normal for base or pyramidal blocks. "
        "Interpret alongside the 3-zone split (Z1+Z2 | Z3+Z4 | Z5–Z7), not as a target on its own."
    ),
    "Polarisation_fused": (
        "Fused Polarization-Index >2.00 means the dominant sport's week is polarised (Treff 2019); "
        "≤2.00 means not polarised, which is normal for base or pyramidal blocks."
    ),
    "Polarisation_combined": (
        "Combined Polarization-Index >2.00 means the whole week across sports is polarised (Treff 2019); "
        "≤2.00 means not polarised. Use as a summary; it should not trigger changes on its own."
    ),
    "WBalDepletion": (
        "High W′ depletion (>45%) indicates repeated deep anaerobic stress. "
        "If clustered, monitor recovery closely; if sustained week-over-week, consider redistributing intensity."
    ),
    "AnaerobicContribution": (
        "Very high anaerobic contribution (>90%) means intensity sessions are highly glycolytic. "
        "This is appropriate for race-specific or VO₂ blocks but should not dominate base phases."
    ),
    "WBalPattern": (
        "Clustered anaerobic patterns (e.g. weekend stacking) increase short-term fatigue risk "
        "but can be effective when followed by sufficient recovery."
    ),
    "AnaerobicRepeatability": (
        "If WDRM high week-over-week, monitor recovery and avoid stacking "
        "deep W′ sessions without adequate low-intensity support."
    ),
    "DurabilityProfile": (
        "Use durability state to guide action. "
        "If durability is drifting, reduce intensity density or extend aerobic work. "
        "If stable or improving, maintain current structure."
    ),
    "NeuralDensity": (
        "If neural density clustered, insert recovery microcycles or "
        "redistribute intensity to prevent cumulative fatigue."
    ),
    "LoadAlignment": (
        "If acute > chronic (>1.4), reduce intensity density or volume. "
        "If acute < chronic (<0.8), consider progressive overload."
    ),
    "HRVStability": (
        "If HRV stability drops below 0.85, recovery variability is increasing. "
        "Ensure consistent sleep and reduce high-intensity density."
    ),
    "AutonomicStatus": (
        "If autonomic ratio drops below 0.92, reduce intensity density. "
        "Stable or elevated values support normal training."
    ),
    "HRVDeviation": (
        "If HRV deviation is negative beyond -10%, reduce intensity "
        "and prioritise sleep. Positive deviation suggests readiness."
    ),
    "w_prime_divergence_7d": {
        "green": "Anaerobic utilisation within normal endurance range.",
        "amber": "Elevated W′ usage — indicates VO₂max or anaerobic stimulus.",
        "red": "Very high W′ utilisation — likely race load or repeated high-intensity sessions."
    },
    "w_prime_divergence_90d": {
        "green": "Model windows aligned — W′ setting reflects the current power curve.",
        "amber": "Mild divergence — monitor CP curve stability or review W′ setting.",
        "red": "Large mismatch between rolling CP W′ and athlete profile W′ — depletion metrics may be distorted. Review W′ calibration."
    },
    "pdr_5m": (
        "Power Duration Reserve at 5 minutes. "
        "Calculated as P5m minus Critical Power (CP). "
        "Represents the athlete's supra-threshold energy reserve available "
        "during high-intensity aerobic/VO2 efforts."
    ),
    "curve_window": (
        "Rolling power-duration curve comparison window used by ESPE. "
        "Two equal windows are compared (current vs previous) using best power "
        "values for standard durations (5s, 1m, 5m, 20m, 60m). "
        "Windows are anchored to the report end date and typically span 84–90 days."
    ),
    "FFT_CURVES": (
        "Power-duration model derived from FFT curve fitting in Intervals.icu. "
        "Provides estimated Critical Power (CP), W′, maximal sprint power (Pmax), "
        "and FTP using best efforts across the rolling curve window."
    ),
    "vo2_reserve_ratio": (
        "Ratio of 5-minute power to Critical Power (P5m / CP). "
        "Represents supra-threshold aerobic reserve and VO₂ capacity headroom. "
        "Values around 1.15–1.30 typical for trained endurance athletes."
    ),
    "glycolytic_bias_ratio": (
        "Ratio of short-duration power relative to threshold power. "
        "Indicates glycolytic dominance versus aerobic contribution. "
        "Higher values suggest stronger anaerobic contribution to the power curve."
    ),
    "aerobic_durability_ratio": (
        "Ratio of long-duration power relative to threshold power. "
        "Represents aerobic durability and the ability to sustain output "
        "during prolonged efforts."
    ),
    "durability_gradient": (
        "Durability gradient calculated as P60 divided by P20. "
        "Reflects fatigue resistance across prolonged efforts. "
        "Values closer to 1 indicate stronger endurance durability."
    ),
    "system_balance_score": (
        "Composite balance indicator across anaerobic, VO₂, threshold, "
        "and durability systems derived from the power-duration curve. "
        "Values closer to 1 indicate balanced development across systems."
    ),
    "load_recovery_state": (
        "Balanced — training load and recovery are aligned. Maintain planned structure.\n"
        "Productive_load — load elevated but recovery stable; continue progression while monitoring HRV.\n"
        "Adaptation_pressure — recovery signals falling under load; reduce intensity density or insert recovery.\n"
        "Maladaptation_risk — recovery suppressed relative to load; prioritize rest or deload."
    ),
    "EnduranceDecay": (
        "If EnduranceDecay exceeds ~5%, prioritise longer steady Z2 endurance sessions "
        "and reduce excessive intensity density. Improving aerobic durability reduces "
        "cardiovascular drift during long efforts."
    ),
    "ProteinIntake": "Increase intake during high load or recovery phases (ACSM/ISSN) to support adaptation and repair.",
    "CarbohydrateAvailability": "Align carbohydrate intake with training demand (IOC/ACSM) to maintain glycogen availability and performance capacity.",
    "FatIntake": "Maintain sufficient intake (sports nutrition consensus) to support hormonal health and energy balance."
}

CHEAT_SHEET["display_names"] = {
    "Polarisation": "Polarisation (Seiler 3-zone distribution)",
    "PolarisationIndex": "Polarisation Index (Treff 2019, Power 3-zone)",
    "Polarisation_fused": "Polarisation Index (Fused HR+Power, sport-specific)",
    "Polarisation_combined": "Polarisation Index (Combined HR+Power, multi-sport)",
    "WBalDepletion": "W′ Balance Depletion (Weekly Mean)",
    "AnaerobicContribution": "Anaerobic Contribution (W′-engaged)",
    "WBalPattern": "Anaerobic Load Pattern",
    "anaerobic_repeatability": "Anaerobic Repeatability (WDRM)",
    "durability_profile": "Durability Profile (ISDM)",
    "neural_density": "Neural Load Density (NDLI)",
    "load_alignment": "Acute vs Chronic Load Alignment",
    "wdrm_7d": "Anaerobic Repeatability (7-day)",
    "wdrm_90d": "Anaerobic Repeatability (90-day)",
    "w_prime_divergence_7d": "W′ Utilisation Divergence (7-day)",
    "w_prime_divergence_90d": "W′ Model Coherence (90-day)",
    # WDRM metrics
    "max_depletion_pct_7d": "Max W′ Depletion (7-day)",
    "mean_depletion_pct_7d": "Mean W′ Depletion (7-day)",
    "moderate_depletion_sessions_7d": "Moderate W′ Depletion Sessions (7-day)",
    "high_depletion_sessions_7d": "High W′ Depletion Sessions (7-day)",
    "total_joules_above_ftp_7d": "Total Work Above FTP (7-day)",

    # ISDM metrics 7d
    "mean_decoupling_7d": "Mean Decoupling (abs, 7-day)",
    "mean_decoupling_signed_7d": "Decoupling Direction (7-day)",
    "max_decoupling_7d": "Max Decoupling (7-day)",
    "high_drift_sessions_7d": "High Drift Sessions (7-day)",
    "long_sessions_7d": "Long Endurance Sessions (7-day)",

    # NDLI metrics
    "rolling_joules_above_ftp_7d": "Rolling Work Above FTP (7-day)",
    "high_intensity_days_7d": "High-Intensity Days (7-day)",
    "mean_if_7d": "Mean Intensity Factor (7-day)",
    "mean_variability_index_7d": "Mean Variability Index (7-day)",
    "mean_efficiency_factor_7d": "Mean Efficiency Factor (7-day)",

    # WDRM metrics (90d)
    "max_depletion_pct_90d": "Max W′ Depletion (90-day)",
    "mean_depletion_pct_90d": "Mean W′ Depletion (90-day)",
    "high_depletion_sessions_90d": "High W′ Depletion Sessions (90-day)",
    "total_joules_above_ftp_90d": "Total Work Above FTP (90-day)",

    # ISDM metrics (90d)
    "mean_decoupling_90d": "Mean Decoupling (abs, 90-day)",
    "mean_decoupling_signed_90d": "Decoupling Direction (90-day)",
    "max_decoupling_90d": "Max Decoupling (90-day)",
    "high_drift_sessions_90d": "High Drift Sessions (90-day)",

    # NDLI metrics (90d)
    "high_intensity_sessions_90d": "High-Intensity Sessions (90-day)",
    "mean_if_90d": "Mean Intensity Factor (90-day)",
    "mean_training_load_90d": "Mean Training Load (90-day)",
    "mean_efficiency_factor_90d": "Mean Efficiency Factor (90-day)",
    "mean_variability_index_90d": "Mean Variability Index (90-day)"
}

CHEAT_SHEET["advice"] = {
    # --- Durability ---
    "Durability": {
        "low": "⚠ Durability low ({:.2f}) — extend steady-state endurance or increase time-in-zone.",
        "improving": "✅ Durability improving ({:.2f}) — maintain current long-ride structure."
    },
    # --- Load Intensity Ratio (LIR) ---
    "LIR": {
        "high": "⚠ Load intensity too high (LIR={:.2f}) — reduce intensity or monitor recovery.",
        "low": "⚠ Load intensity low (LIR={:.2f}) — add tempo or sweet-spot intervals.",
        "balanced": "✅ Load intensity balanced (LIR={:.2f})."
    },
    # --- Endurance Reserve ---
    "EnduranceReserve": {
        "depleted": "⚠ Endurance reserve depleted ({:.2f}) — add recovery or split long sessions.",
        "strong": "✅ Endurance reserve strong ({:.2f})."
    },
    # --- Efficiency Drift ---
    "IFDrift": {
        "stable": "✅ IF Drift stable ({:.2%}) — aerobic durability solid.",
        "high": "⚠ IF Drift high ({:.2%}) — improve aerobic durability or reduce fatigue load."
    },
    # Base metric: Polarisation (Seiler 3-zone distribution type)
    "Polarisation": {
        "threshold": "🟠 Seiler threshold distribution — substantial LT1–LT2 work; fine if phase-intentional.",
        "pyramidal": "🧱 Seiler pyramidal distribution — low > moderate > high; typical of base and build blocks.",
        "polarised": "✅ Seiler polarised distribution — mostly easy, with more hard than moderate work.",
        "base": "🧱 Seiler base distribution — low intensity strongly dominant.",
        "hiit": "⚠ High-intensity dominant distribution — monitor recovery.",
        "unique": "ℹ️ Distribution does not match a standard Seiler type."
    },
    # Fused HR+Power variant (dominant sport, Treff index)
    "Polarisation_fused": {
        "polarised": "✅ Dominant sport polarised (Treff index {:.2f} > 2.00).",
        "not_polarised": "ℹ️ Dominant sport not polarised (Treff index {:.2f} ≤ 2.00) — normal for base or pyramidal blocks."
    },
    # Multi-sport combined variant (Treff index)
    "Polarisation_combined": {
        "polarised": "✅ Combined week polarised (Treff index {:.2f} > 2.00).",
        "not_polarised": "ℹ️ Combined week not polarised (Treff index {:.2f} ≤ 2.00) — summary only."
    },
    # --- Load Variability Index ---
    "LoadVariabilityIndex": {
        "poor": "⚠ Load Variability Index suppressed ({:.2f}) — current load structure exceeds physiological tolerance; reduce intensity clustering and smooth load distribution.",
        "moderate": "🟠 Load Variability Index moderate ({:.2f}) — load manageable but monitor fatigue accumulation and ACWR trend.",
        "healthy": "✅ Load Variability Index aligned ({:.2f}) — load variability matches systemic capacity."
    },
    # --- FatigueTrend ---
    "FatigueTrend": {
        "recovery": "⚠ FatigueTrend ({:.2f}%) — Recovery phase detected. Maintain steady training load and prioritize recovery.",
        "increasing": "✅ FatigueTrend ({:.2f}%) — Increasing fatigue trend. Consider adjusting intensity or recovery."
    },
    # --- Phase Detection --- (Seasonal Phase Advice)
    "PhaseAdvice": {
        "Base": "🧱 **Base phase detected** — prioritise aerobic volume (Z1–Z2 ≥ 70%) and stable load progression (ACWR ≤ 1.0).",

        "Build": "📈 **Build phase detected** — progressive overload active; maintain ACWR ≤ 1.3 and manage intensity density.",

        "Peak": "🏁 **Peak phase detected** — high-intensity emphasis; monitor fatigue signals (NDLI, durability, FatigueTrend).",

        "Taper": "📉 **Taper phase detected** — reduce ATL by ~30–50% while maintaining intensity; expect freshness to rise (TSB ↑, fatigue ↓).",

        "Recovery": "💤 **Recovery phase detected** — reduce load and prioritise recovery; target low monotony and declining load trend.",

        "Deload": "🧘 **Deload phase detected** — controlled reduction in load while maintaining frequency; prepare for next progression block."
    },
    #Lactate-based training advice and reasoning
    "Lactate": {
        "low": (
            "Average lactate <2 mmol/L — effort likely below LT1. "
            "Excellent for aerobic base work and fat-oxidation efficiency."
        ),
        "moderate": (
            "Lactate 2–4 mmol/L — around the aerobic-anaerobic transition (Z2–Z3). "
            "Good for tempo and extensive endurance; monitor fatigue."
        ),
        "high": (
            "Lactate >4 mmol/L — above LT2 (anaerobic). "
            "Limit sustained exposure; use for threshold or VO₂ intervals."
        ),
        "correlation_strong": (
            "Lactate-power correlation strong (r > 0.6) — physiological calibration reliable."
        ),
        "correlation_weak": (
            "Lactate-power correlation weak — revert to FTP-based zones until more data available."
        ),
        "no_data": (
            "No lactate data detected — FTP defaults used for zone calibration."
        ),
    },
    "AnaerobicRepeatability": {
        "low": "Anaerobic exposure controlled — maintain structure.",
        "moderate": "Moderate anaerobic load — ensure recovery spacing.",
        "high": "High W′ depletion — monitor recovery and intensity stacking."
    },
    "DurabilityProfile": {
        "stable": "Durability stable — cardiovascular drift controlled.",
        "stable_improving": "Durability stable and improving — efficiency trending positively.",
        "drifting": "Elevated drift — expected under load. Monitor trend, not single-week values.",
        "improving": "Durability improving — strong efficiency adaptation.",
        "logic": "Durability state is pre-resolved. Do not infer interpretation from decoupling metrics."
    },
    "NeuralDensity": {
        "balanced": "Intensity density well distributed.",
        "clustered": "High short-term clustering — monitor recovery.",
        "overloaded": "Neural load accumulation high — reduce intensity density."
    },
    "LoadAlignment": {
        "underload": "Acute below baseline — safe to build.",
        "aligned": "Acute aligned with chronic baseline.",
        "overreach": "Acute significantly above baseline — recovery advised."
    },
    "LoadRecoveryState": {
        "balanced": "Training load and recovery signals aligned.",
        "productive_load": "Recovery stable under elevated load — productive adaptation likely.",
        "adaptation_pressure": "Recovery markers suppressed under load — monitor fatigue and reduce intensity density.",
        "maladaptation_risk": "Recovery breakdown detected — deload or recovery advised."
    },
}

# =========================================================
# 🏷️ SPORT GROUP CANONICAL MAPS (Intervals.icu canonical)
# Used for zones, fusion, polarisation, reporting
# =========================================================
CHEAT_SHEET["sport_groups"] = {

    # -----------------------------
    # 🚴 CYCLING (POWER FIRST)
    # -----------------------------
    "Ride": [
        "Ride",
        "VirtualRide",
        "GravelRide",
        "MountainBikeRide",
        "TrackCycling",
        "EBikeRide",
        "EMountainBikeRide",
        "Handcycle",
        "Velomobile",
    ],

    # -----------------------------
    # 🏃 RUNNING (HR / PACE)
    # -----------------------------
    "Run": [
        "Run",
        "TrailRun",
        "VirtualRun",
    ],

    # -----------------------------
    # 🏊 SWIMMING
    # -----------------------------
    "Swim": [
        "Swim",
        "OpenWaterSwim",
        "VirtualSwim",
    ],

    # -----------------------------
    # ⛷️ SKI / SNOW
    # -----------------------------
    "Ski": [
        "AlpineSki",
        "BackcountrySki",
        "NordicSki",
        "RollerSki",
        "Snowboard",
        "VirtualSki",
        "Snowshoe",
    ],

    # -----------------------------
    #  HIKE
    # -----------------------------
    "Hike": [
        "Walk",
        "Hike",
    ],

    # -----------------------------
    # 🚣 ROWING
    # -----------------------------
    "Row": [
        "Row",
        "VirtualRow",
    ],

    # -----------------------------
    # 🚫 EXCLUDED FROM ZONE / POL
    # -----------------------------
    "Excluded": [
        "WeightTraining",
        "Crossfit",
        "Yoga",
        "Pilates",
        "Golf",
        "Workout",
        "HIIT",
        "Elliptical",
        "StairStepper",
        "Tennis",
        "TableTennis",
        "Squash",
        "Padel",
        "Pickleball",
        "Badminton",
        "Soccer",
        "Hockey",
        "Rugby",
        "RockClimbing",
        "Kayaking",
        "StandUpPaddling",
        "Surfing",
        "Windsurf",
        "Sail",
        "Canoeing",
    ],
}
CHEAT_SHEET["zone_semantics"] = {
    "power": {
        "label": "Cycling Power Zones",
        "description": (
            "Distribution of training time by cycling power zones. Derived from Intervals.icu power zone times for Ride-based activities. "
            "SS = Sweetspot"
        ),
    },
    "hr": {
        "label": "Cycling Heart Rate Zones",
        "description": "Distribution of training time by heart rate zones. Restricted to Ride-based activities for physiological comparability."
    },
    "pace": {
        "label": "Run Pace Zones",
        "description": "Distribution of training time by pace zones. Used primarily for Run-based activities."
    },
    "swim": {
        "label": "Swim Pace Zones",
        "description": "Distribution of training time by swim pace zones for pool and open water swims."
    },
    "fused": {
        "label": "Fused Intensity Zones",
        "description": (
            "Sport-specific fusion of power and heart-rate intensity zones. "
            "Within each activity, power is used when available; heart rate is "
            "used otherwise. Time-in-zone is normalised per sport before aggregation. "
            "This follows established endurance physiology practice where intensity "
            "distribution is defined by time spent in intensity domains, with sensors "
            "treated as interchangeable proxies rather than distinct categories "
            "(Seiler 2010; Stöggl & Sperlich 2015; Issurin 2008) "
            "SS = Sweetspot."
        ),
    },
    "combined": {
        "label": "Combined Intensity Distribution",
        "description": (
            "Global distribution of training time across intensity zones "
            "for all endurance activities. Power is prioritised where available, "
            "heart rate otherwise. Normalised once across total training time "
            "(Seiler / Stöggl / Issurin methodology) "
            "SS = Sweetspot."
        ),
    },
}

# === Labels ===
CHEAT_SHEET["labels"] = {
    "acwr_risk": "EWMA Acute:Chronic Load Ratio",
    "strain": "Load × Monotony",
    "fatigue_trend": "EMA(Load, decay=0.2) (Percentage change)",
}
CHEAT_SHEET["future_actions"] = {

    "transition": {
        "title": "Transition / Recovery",
        "reason": "Training load is low; focus on maintaining activity and recovery.",
        "priority": "low"
    },

    "fresh": {
        "title": "Freshness high",
        "reason": "You are well recovered; training is going well.",
        "priority": "normal"
    },

    "neutral": {
        "title": "Neutral load",
        "reason": "Training stimulus and recovery are balanced.",
        "priority": "normal"
    },

    "productive_fatigue": {
        "title": "Productive training fatigue",
        "reason": "Training load is high but within a productive overload zone.",
        "priority": "normal"
    },

    "overreached": {
        "title": "High fatigue risk",
        "reason": "Form suggests significant fatigue; consider recovery actions.",
        "priority": "high"
    }
}

CHEAT_SHEET["future_labels"] = {
    "transition": "Very fresh — light training phase",
    "fresh": "Fresh — well recovered",
    "neutral": "Neutral — balanced load",
    "productive_fatigue": "Productive fatigue — overload zone",
    "overreached": "High fatigue — risk of overreaching"
}

CHEAT_SHEET["future_colors"] = {
    "transition": "#66ccff",
    "fresh": "#99ff99",
    "neutral": "#cccccc",
    "productive_fatigue": "#ffcc66",
    "overreached": "#ff6666"
}

CHEAT_SHEET["wbal_patterns"] = {
    "even": {
        "label": "Evenly Distributed",
        "description": "Anaerobic load spread consistently across the week."
    },
    "clustered_weekend": {
        "label": "Weekend Clustered",
        "description": "Anaerobic stress concentrated late in the week."
    },
    "single_day_spike": {
        "label": "Single-Day Spike",
        "description": "One dominant anaerobic session defines weekly load."
    },
}

# ============================================================
# 🔎 Metric Confidence & Applicability Rules (Contextual Model)
# ============================================================
# These rules define WHEN a metric is actionable vs contextual.
# They do NOT change values, thresholds, or classifications.
# ============================================================

CHEAT_SHEET["metric_confidence"] = {

    # --- Power-only Seiler Ratio ---
    "Polarisation": {
        "default": "contextual",
        "high_confidence_when": {
            "phases": ["Build", "Peak"],
            "min_sessions": 4,
            "min_intensity_sessions": 2
        },
        "notes": (
            "The Seiler distribution type is only actionable when "
            "intensity contrast is intentionally prescribed. "
            "Base, pyramidal or threshold types are expected during base, recovery, "
            "or durability-focused weeks."
        )
    },
    # --- Power-normalised index ---
    "PolarisationIndex": {
        "default": "contextual",
        "high_confidence_when": {
            "phases": ["Build", "Peak"],
            "min_sessions": 3
        },
        "notes": (
            "Treff Polarization-Index reflects structural intensity contrast using "
            "normalised 3-zone power distribution (z1+z2+z3=1 after collapse). "
            "High confidence when at least 4 sessions and ≥2 high-intensity sessions exist."
        )
    },
    # --- Fused HR + Power (dominant sport) ---
    "Polarisation_fused": {
        "default": "contextual",
        "high_confidence_when": {
            "phases": ["Build", "Peak"],
            "dominant_sport_required": True,
            "min_sessions": 4
        },
        "notes": (
            "Fused Treff index reflects intensity distribution within "
            "the dominant sport. Confidence depends on signal quality "
            "(power over HR), not volume."
        )
    },
    # --- Combined multi-sport ---
    "Polarisation_combined": {
        "default": "informational",
        "notes": (
            "Combined polarisation is a global summary metric and "
            "should never trigger corrective actions on its own."
        )
    },
    # --- W bal -------
    "WBalDepletion": {
    "default": "contextual",
    "high_confidence_when": {
        "phases": ["Build", "Peak"],
        "min_intensity_sessions": 2,
        "min_sessions": 4,
    },
    "notes": (
        "W′ balance metrics are only meaningful when sufficient supra-threshold "
        "work is present. Low values during base or recovery are expected."
    ),
    },
    "AnaerobicContribution": {
        "default": "contextual",
        "high_confidence_when": {
            "min_intensity_sessions": 2,
        },
    },
    "AnaerobicRepeatability": {
        "default": "contextual",
        "high_confidence_when": {
            "min_intensity_sessions": 2,
            "min_sessions": 4
        },
        "notes": (
            "WDRM requires repeated supra-threshold exposure to be meaningful. "
            "Low values during base or recovery are expected."
        )
    },
    "DurabilityProfile": {
        "default": "contextual",
        "high_confidence_when": {
            "min_sessions": 3
        },
        "notes": (
            "Durability (ISDM) meaningful when steady-state aerobic work "
            "exists. Not valid in short, high-intensity-only weeks."
        )
    },
    "NeuralDensity": {
        "default": "contextual",
        "high_confidence_when": {
            "min_intensity_sessions": 2
        },
        "notes": (
            "NDLI reflects clustering of high-intensity sessions. "
            "Interpret relative to recovery spacing."
        )
    },
    "LoadAlignment": {
        "default": "informational",
        "notes": (
            "Acute vs chronic alignment is directional. "
            "Should not trigger action in isolation."
        )
    },
    "HRVDeviation": {
        "default": "high",
        "high_confidence_when": {"min_samples": 7},
    },

    "HRVStability": {
        "default": "high",
        "high_confidence_when": {"min_samples": 10},
    },

    "RestingHRTrend": {
        "default": "moderate",
        "high_confidence_when": {"min_samples": 7},
    },

    "SleepQuality": {
        "default": "moderate",
        "high_confidence_when": {"min_samples": 7},
    },
    "w_prime_divergence_7d": {
        "default": "contextual",
        "notes": (
            "Indicator of anaerobic load exposure. Should be interpreted "
            "alongside W′ depletion and high-intensity session counts."
        )
    },
    "w_prime_divergence_90d": {
        "default": "informational",
        "notes": (
            "Model coherence diagnostic only. Does not directly indicate fatigue or performance change."
        )
    },
}



# --- Backward compatibility aliases ---
if "IFDrift" in CHEAT_SHEET["advice"]:
    CHEAT_SHEET["advice"]["EfficiencyDrift"] = CHEAT_SHEET["advice"]["IFDrift"]
if "IFDrift" in CHEAT_SHEET["thresholds"]:
    CHEAT_SHEET["thresholds"]["EfficiencyDrift"] = CHEAT_SHEET["thresholds"]["IFDrift"]

CHEAT_SHEET["primary_messages"] = {
    "build_deload": {
        "status": (
            "Your training structure and durability are improving, "
            "but recovery is lagging slightly."
        ),
        "action": (
            "Take a short 10–15% deload to consolidate gains."
        ),
        "next": (
            "Once recovered, resume progression with slightly more "
            "intensity contrast and continued Zone 2 focus."
        ),
    },
    "overreach_deload": {
        "status": (
            "Training load has exceeded recovery capacity and fatigue "
            "is accumulating."
        ),
        "action": (
            "Apply a stronger 30–40% deload to restore recovery."
        ),
        "next": (
            "Resume training conservatively once recovery stabilises."
        ),
    },
}



# === Cheat Sheet Accessor ===
def summarize_load_block(context):
    """
    Summarize current training block load distribution using CHEAT_SHEET_RULES.
    Supports both numeric and structured ACWR contexts.
    """

    load = context.get("totalTss", 0)
    duration = context.get("totalHours", 0)
    acwr_raw = context.get("ACWR", 1.0)

    # Handle new structured ACWR (dict with ratio)
    if isinstance(acwr_raw, dict):
        acwr = float(acwr_raw.get("ratio", 1.0) or 1.0)
    else:
        try:
            acwr = float(acwr_raw or 1.0)
        except (TypeError, ValueError):
            acwr = 1.0

    # --- Classification ---
    if acwr > 1.5:
        load_type = "🚨 High Load / Overreaching"
    elif acwr < 0.8:
        load_type = "🟢 Recovery / Underload"
    else:
        load_type = "⚖️ Stable / Productive"

    return {
        "summary": f"{load_type} — {load:.1f} TSS over {duration:.1f} h (ACWR={acwr:.2f})",
        "load_type": load_type,
        "acwr": acwr,
    }

