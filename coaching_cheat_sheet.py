#!/usr/bin/env python3
"""
coaching_cheat_sheet.py — Unified v16.17 Coaching Reference
Contains static thresholds, labels, and helper summaries for derived metrics.
"""
import pandas as pd

# --- Global Coaching Cheat Sheet Dictionary ---
CHEAT_SHEET = {}

CHEAT_SHEET["meta"] = {
    "version": "v16.17",
    "last_updated": "2025-12-30",
    "source": "Unified Coaching Reference (Intervals + Seiler + Banister)"
}

# === Thresholds ===
CHEAT_SHEET["thresholds"] = {
    "ACWR": {"green": (0.8, 1.3), "amber": (0.6, 1.5)},
    "Monotony": {"green": (1.0, 2.0), "amber": (0.8, 2.5)},
    "Strain": {"green": (0, 3000), "amber": (3000, 4000)},
#    "Polarisation": {"green": (0.75, 0.90), "amber": (0.65, 0.95)},   # Seiler ratio (% displayed)
#    "PolarisationIndex": {"green": (0.75, 1.00), "amber": (0.60, 0.75)},  # Normalized index (0–1)
    "FatigueTrend": {"green": (-10, 10), "amber": (-20, 20)},  # Updated to percentage scale
    "StressTolerance": {"green": (2.0, 8.0), "amber": (1.0, 10.0)},
    "LIR": {"green": (0.8, 1.2), "amber": (0.6, 1.4), "red": (0.0, 0.6)},
    "EnduranceReserve": {"green": (1.2, 2.0), "amber": (0.8, 1.2), "red": (0.0, 0.8)},
    "FatOxEfficiency": {"green": (0.4, 0.8), "amber": (0.3, 0.9)},
    "FOxI": {"green": (30, 80), "amber": (20, 90)},          # FatOx Index %
    "CUR": {"green": (30, 70), "amber": (20, 80)},        # Carbohydrate Utilisation Ratio
    "GR": {"green": (0.5, 2.0), "amber": (0.3, 3.0)},         # Glucose Ratio
    "MES": {"green": (20, 100), "amber": (10, 120)},          # Metabolic Efficiency Score
    "ACWR_Risk": {"green": (0, 1), "amber": (1, 1)},          # Placeholder to silence undefined
    "ZQI": {"green": (5, 15), "amber": (3, 20)},               #% now
    "Durability": {"green": (0.9, 1.2),"amber": (0.7, 0.9),"red": (0.0, 0.7)},
    "IFDrift": {"green": (0.0, 0.05), "amber": (0.05, 0.10), "red": (0.10, 1.0)},
    "Lactate": {"lt1_mmol": 2.0,"lt2_mmol": 4.0,"corr_threshold": 0.6},
    "FatigueResistance": {"green": (0.9, 1.1), "amber": (0.8, 1.2)},  # ratio of long vs short power
    "EfficiencyFactor": {"green": (1.8, 2.2), "amber": (1.5, 2.5)},   # Power-to-HR ratio
    # === Wellness Metrics ===
    "HRV": {"green": (60, 90), "amber": (40, 60)},  # ms
    "RestingHR": {"green": (40, 55), "amber": (56, 65)},  # bpm
    "SleepQuality": {"green": (80, 100), "amber": (65, 80)},  # score out of 100
    "RecoveryIndex": {"green": [0.9, 1.3],"amber": [0.8, 0.9],"red": [0.0, 0.8]},
    # --- HRV family ---
    "HRVBalance": {"green": [1.0, 1.3],"amber": [0.9, 1.0],"red": [0.0, 0.9]},
    "HRVStability": {"green": (0.85, 1.0), "amber": (0.7, 0.85)},
    "HRVTrend": {"green": (0.0, 5.0), "amber": (-2.0, 0.0)},
    # --- Power-based (Seiler) ---
    "Polarisation": {"green": (0.75, 0.90), "amber": (0.65, 0.95)},  # Seiler ratio (Power only)
    "PolarisationIndex": {"green": (0.75, 1.00), "amber": (0.60, 0.75)},  # Normalized Power Index

    # --- Fused HR+Power (sport-specific) ---
    "Polarisation_fused": {"green": (0.80, 1.00), "amber": (0.65, 0.80)},  # Slightly higher tolerance

    # --- Combined HR+Power (multi-sport) ---
    "Polarisation_combined": {"green": (0.78, 1.00), "amber": (0.60, 0.78)},  # Slightly looser due to sport mix
    "TSB": {
        "transition": [10, 999],     # Very fresh, low load (fitness declining)
        "fresh": [5, 10],            # Race-ready freshness
        "grey": [-5, 5],             # Balanced / neutral training
        "optimal": [-30, -5],        # Productive training fatigue (good zone)
        "high_risk": [-999, -30],    # Overreached / excessive fatigue
    },
}

# === Phase-Aware Threshold Adjustments (optional overrides) ===
CHEAT_SHEET["phase_thresholds"] = {
    "Polarisation": {
        "base":  {"green": (0.60, 0.80), "amber": (0.50, 0.90)},
        "build": {"green": (0.75, 1.00), "amber": (0.60, 0.75)},
        "peak":  {"green": (0.80, 1.00), "amber": (0.65, 0.80)},
        "recovery": {"green": (0.70, 0.95), "amber": (0.55, 0.75)},
    },
    "PolarisationIndex": {
        "base":  {"green": (0.60, 0.80), "amber": (0.50, 0.90)},
        "build": {"green": (0.75, 1.00), "amber": (0.60, 0.75)},
        "peak":  {"green": (0.80, 1.00), "amber": (0.65, 0.80)},
        "recovery": {"green": (0.70, 0.95), "amber": (0.55, 0.75)},
    },
}
# === Polarisation Model Mapping (canonical) ===
CHEAT_SHEET["polarisation_models"] = {
    "PolarisationIndex": [
        {"label": "polarised", "range": (0.75, 1.00), "description": "80/20 intensity structure — strong aerobic bias"},
        {"label": "pyramidal", "range": (0.65, 0.75), "description": "Mixed Z2/Z3 structure — transitional base conditioning"},
        {"label": "threshold", "range": (0.00, 0.65), "description": "Threshold-heavy distribution — higher anaerobic load"},
    ],
    "Polarisation": [
        {"label": "polarised", "range": (1.00, 9.99), "description": "Classic Seiler ratio (Z1+Z3)/(2×Z2) ≥1 — clear 80/20 split"},
        {"label": "pyramidal", "range": (0.70, 1.00), "description": "Moderate-intensity dominant — typical base adaptation phase"},
        {"label": "threshold", "range": (0.00, 0.70), "description": "Z2-heavy structure — use intentionally for aerobic foundation"},
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
    # --- Green (good / optimal states)
    "productive": "green",
    "optimal": "green",
    "recovering": "green",
    "good": "green",
    "balanced": "green",
    "healthy": "green",
    "normal": "green",

    # --- Amber (watch / moderate / caution)
    "amber": "amber",
    "moderate": "amber",
    "borderline": "amber",
    "watch": "amber",
    "fatigued": "amber",
    "pyramidal": "amber",

    # --- Red (critical / bad)
    "red": "red",
    "poor": "red",
    "overreached": "red",
    "critical": "red",
    "threshold": "red",      # For low polarisation
    "intensity-focused": "red"
}


# === Context ===
CHEAT_SHEET["context"] = {
    "ACWR": (
    "EWMA Acute:Chronic Load Ratio — compares 7-day vs 28-day weighted loads. "
    "0.8–1.3 = productive training, <0.8 = recovery or detraining, >1.5 = overload/injury risk."
),
    "Monotony": "1–2 shows healthy variation; >2.5 means repetitive stress pattern.",
    "Strain": "Product of load × monotony; >3500 signals potential overreach.",
    "FatigueTrend": "FatigueTrend is calculated as the percentage change between the 7-day and 28-day moving averages. A 0% change indicates balance, while a positive percentage change indicates accumulating fatigue, and a negative percentage change indicates recovery.",
    "ZQI": "Zone Quality Index (%) 5-15 high-intensity time is normal <3% too easy, >20% too intense or erratic pacing.",
    "FatOxEfficiency": "0.4–0.8 means balanced fat oxidation; lower = carb dependence.",
    "FOxI": "FatOx index %; higher values mean more efficient aerobic base.",
    "CUR": "Carbohydrate Utilisation Ratio; 30-80 balanced metabolic use.",
    "GR": "Glucose Ratio; >2 indicates excess glycolytic bias.",
    "MES": "Metabolic Efficiency Score; >20 is good endurance economy.",
    "RecoveryIndex": "0.6–1.0 means recovered; <0.5 = heavy fatigue.",
    "ACWR_Risk": "Used internally for stability check.",
    "StressTolerance": "2–8 indicates sustainable training strain capacity.",
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
    "RecoveryIndex": "Composite of HRV and TSB to reflect overall readiness to train.",
    "HRVBalance": "HRV compared to 42-day mean — shows short-term recovery status.",
    "HRVStability": "Consistency of HRV — lower variability = better physiological stability.",
    "HRVTrend": "Direction of HRV change — rising indicates improving recovery.",
    # --- Polarisation Variants (clarified sources) ---
    "Polarisation": (
        "Power-based Seiler Polarisation Ratio (Z1 + Z3) / (2 × Z2), showing the balance "
        "between low- and high-intensity work relative to moderate (Z2) training. "
        "≥1.0 = polarised (80/20), 0.7–0.99 = mixed, <0.7 = Z2-dominant. "
        "⚙️ *Power-only metric — HR ignored.* Use primarily during power-measured cycling phases."
    ),
    "PolarisationIndex": (
        "Power-based normalized Polarisation Index (0–1). Reflects the proportion of total training "
        "time in Z1 + Z2 relative to total. ≥0.75 = strong aerobic bias, <0.60 = intensity-heavy. "
        "⚙️ *Power-only metric; dependent on accurate FTP calibration.*"
    ),
    "Polarisation_fused": (
        "Dominant-sport Polarisation Index derived from fused HR+Power data. "
        "Represents how the athlete distributes intensity within the primary discipline. "
        "≥0.80 = polarised, 0.65–0.79 = pyramidal, <0.65 = threshold-dominant. "
        "⚙️ *HR fills gaps when power unavailable.*"
    ),
    "Polarisation_combined": (
        "Global HR+Power combined Polarisation Index across all sports. "
        "Reflects total weekly distribution and load balance for multi-sport athletes. "
        "≥0.80 = polarised, 0.65–0.79 = pyramidal, <0.65 = threshold-heavy. "
        "⚙️ *Cross-discipline index — lower precision, but best overall summary of load contrast.*"
    ),
}

CHEAT_SHEET["coaching_links"] = {
    # --- Derived Metric Coaching Links ---
    "ACWR": "If ACWR > 1.5, reduce intensity and focus on recovery to avoid overload. If ACWR < 0.8, gradually increase training load with controlled progression to build endurance.",
    "Monotony": "If Monotony > 2.5, introduce more variation in training or implement a deload week to reduce repetitive stress.",
    "Strain": "If Strain > 3000, monitor for signs of overreach and consider more rest or deloading. If Strain > 3500, consider reducing volume or intensity temporarily.",
    "RecoveryIndex": "If RecoveryIndex is low (<0.7), ensure adequate rest and recovery, and avoid heavy training loads.",
    "FatigueTrend": "If FatigueTrend is negative (e.g., below -0.2), this indicates a recovering state. Continue with controlled training load and focus on recovery to ensure sustained progress. Avoid aggressive increases in load.",
    "FatOxEfficiency": "If FatOxEfficiency is low (<0.6), focus on improving aerobic base with longer, low-intensity efforts.",
    "ZQI": "If ZQI > 20%, review pacing strategy; excessive high-intensity time could indicate erratic pacing or overtraining. Aim for 5-15% ZQI for balanced training.",
    "FOxI": "If FOxI is increasing, continue to prioritize low-intensity work to enhance fat metabolism. If it decreases, consider increasing your Zone 2 training duration.",
    "CUR": "If CUR is outside the green zone (30-70), adjust carbohydrate intake and fueling strategy to ensure balanced metabolic use during long sessions.",
    "GR": "If GR exceeds 2.0, focus on reducing glycolytic intensity and increase aerobic work. Ensure sufficient recovery to avoid over-reliance on carbs.",
    "MES": "If MES is below 20, work on improving metabolic efficiency by increasing endurance training with a focus on aerobic base and fat metabolism.",
    "StressTolerance": "If StressTolerance is high (>8), reduce overall load and increase recovery time. If it's low (<2), ensure proper training load progression.",
    "FatigueResistance": "If FatigueResistance <0.9, add longer sub-threshold intervals or extended endurance sessions. Maintain >0.95 to support long-duration performance.",
    "EfficiencyFactor": "If EfficiencyFactor is declining, focus on aerobic conditioning and recovery. Stable or increasing EF indicates improving endurance efficiency.",
    "RecoveryIndex": "If RecoveryIndex is low, ensure adequate rest and recovery. If high, maintain load and monitor for overreaching.",
    # --- Polarisation Variants Coaching Links ---
    "Polarisation": (
        "If Polarisation <0.7 during base, this reflects aerobic Z2 dominance (✅ normal). "
        "If in Build/Peak, reduce Z2 time and increase Z1/Z3 contrast. "
        "Maintain ≥1.0 for ideal 80/20 balance in power-measured disciplines."
    ),
    "PolarisationIndex": (
        "If PolarisationIndex <0.60 during base, increase Z1 time to reinforce aerobic bias. "
        "If low in Build, acceptable for intensity focus. "
        "Target ≥0.75 in base and recovery blocks for efficient endurance adaptation."
    ),
    "Polarisation_fused": (
        "If fused Polarisation Index <0.65, the dominant sport is intensity-heavy — "
        "increase Z1/Z2 duration or insert a recovery microcycle. "
        "Maintain ≥0.80 for a robust endurance foundation."
    ),
    "Polarisation_combined": (
        "If combined Polarisation Index <0.65, total weekly load is intensity-heavy. "
        "Add endurance-focused sessions or recovery days to preserve a healthy 80/20 ratio. "
        "Ideal global range ≥0.78 for mixed-sport athletes."
    ),
}

CHEAT_SHEET["display_names"] = {
    "Polarisation": "Polarisation (Power-based, Seiler ratio)",
    "PolarisationIndex": "Polarisation Index (Power-based, normalized)",
    "Polarisation_fused": "Polarisation Index (Fused HR+Power, sport-specific)",
    "Polarisation_combined": "Polarisation Index (Combined HR+Power, multi-sport)",
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
    # Base metric: Polarisation (Power-only)
    "Polarisation": {
        "low": "⚠ Polarisation low ({:.2f}) — increase Z1–Z3 contrast unless in base phase.",
        "z2_base": "🧱 Z2-base dominant ({:.2f}) — appropriate for aerobic foundation phase.",
        "optimal": "✅ Polarisation optimal ({:.2f}) — strong 80/20 intensity structure."
    },
    # Power-normalized index variant
    "PolarisationIndex": {
        "low": "⚠ Polarisation Index low ({:.2f}) — intensity-heavy pattern; monitor Zone 2 volume.",
        "z2_base": "🧱 Aerobic bias strong ({:.2f}) — excellent for base or recovery blocks.",
        "optimal": "✅ Polarisation Index optimal ({:.2f}) — balanced endurance distribution."
    },
    # Fused HR+Power variant (sport-specific)
    "Polarisation_fused": {
        "low": "⚠ Fused Polarisation Index low ({:.2f}) — dominant sport intensity heavy; add endurance work.",
        "z2_base": "🧱 Fused Polarisation Index ({:.2f}) — Z2-base dominant, normal for aerobic development.",
        "optimal": "✅ Fused Polarisation Index optimal ({:.2f}) — maintain current intensity mix."
    },
    # Multi-sport combined variant
    "Polarisation_combined": {
        "low": "⚠ Combined Polarisation Index low ({:.2f}) — total weekly load intensity-heavy; increase endurance ratio.",
        "z2_base": "🧱 Combined Polarisation Index ({:.2f}) — pyramidal distribution, acceptable in build weeks.",
        "optimal": "✅ Combined Polarisation Index optimal ({:.2f}) — balanced global load contrast."
    },
        # --- Multi-variant Polarisation summary ---
    "Polarisation_summary": {
        "low": (
            "⚠ Polarisation metrics low ({}) — review endurance–intensity balance across sports. "
            "Multiple discipline indices below target indicate overall Z2 dominance or insufficient intensity contrast."
        ),
        "mixed": (
            "🟠 Polarisation mixed ({}) — sport-specific imbalances detected; "
            "ensure HR and power distributions align with phase goals."
        ),
        "balanced": (
            "✅ Polarisation balanced ({}) — endurance and intensity distribution consistent across sports."
        )
    },
    # --- Recovery Index ---
    "RecoveryIndex": {
        "poor": "⚠ Recovery Index poor ({:.2f}) — insert deload or reduce intensity.",
        "moderate": "🟠 Recovery Index moderate ({:.2f}) — monitor fatigue trend.",
        "healthy": "✅ Recovery Index healthy ({:.2f})."
    },

    # --- FatigueTrend ---
    "FatigueTrend": {
        "recovery": "⚠ FatigueTrend ({:.2f}%) — Recovery phase detected. Maintain steady training load and prioritize recovery.",
        "increasing": "✅ FatigueTrend ({:.2f}%) — Increasing fatigue trend. Consider adjusting intensity or recovery."
    },

    # --- Phase Detection --- (Seasonal Phase Advice)
    "PhaseAdvice": {
        "Base": "🧱 **Base phase detected** — focus on aerobic volume (Z1–Z2 ≥ 70%), maintain ACWR ≤ 1.0.",
        "Build": "📈 **Build phase detected** — progressive overload active; maintain ACWR ≤ 1.3.",
        "Peak": "🏁 **Peak phase detected** — high-intensity emphasis; monitor fatigue (RI ≥ 0.6).",
        "Taper": "📉 **Taper phase detected** — reduce ATL by 30–50%, maintain intensity; expected RI ↑.",
        "Recovery": "💤 **Recovery phase detected** — active regeneration; target RI ≥ 0.8 and low monotony.",
        "Deload": "🧘 **Deload phase detected** — reduced load, maintain frequency; transition readiness improving.",
        "Continuous Load": "🔁 **Continuous Load** — steady training; insert variation if fatigue rises."
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
    }   
}

# =========================================================
# 🏷️ SPORT GROUP CANONICAL MAPS (for zone, polarisation, etc.)
# =========================================================
CHEAT_SHEET["sport_groups"] = {
    "Ride": [
        "Ride", "VirtualRide", "GravelRide", "MountainBikeRide",
        "TrackRide", "EBikeRide", "EMountainBikeRide", "Velomobile", "Handcycle"
    ],
    "Run": [
        "Run", "TrailRun", "VirtualRun", "Hike", "Walk"
    ],
    "Swim": [
        "Swim", "OpenWaterSwim", "VirtualSwim"
    ],
    "Excluded": [
        "WeightTraining", "Crossfit", "Yoga", "Pilates", "Golf", "Workout",
        "Rowing", "VirtualRow", "Kayaking", "StandUpPaddling", "Surfing",
        "TableTennis", "Tennis", "Squash", "Padel", "Pickleball", "Badminton",
        "Soccer", "Hockey", "Rugby", "RockClimbing", "Snowboard", "Ski",
        "BackcountrySki", "NordicSki", "RollerSki", "Snowshoe"
    ]
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
    "grey": {
        "title": "Grey Zone / Balanced Training",
        "reason": "Training stimulus and recovery are balanced; neutral load trend.",
        "priority": "normal"
    },
    "optimal": {
        "title": "Optimal training zone",
        "reason": "Form indicates productive training load; continue structured progression.",
        "priority": "normal"
    },
    "high_risk": {
        "title": "High Risk / Overreaching",
        "reason": "Form suggests significant fatigue; consider recovery actions.",
        "priority": "high"
    },
}

CHEAT_SHEET["future_labels"] = {
    "transition": "Very fresh — light training phase",
    "fresh": "Fresh — well recovered",
    "grey": "Neutral — balanced load",
    "optimal": "Optimal — productive training zone",
    "high_risk": "High fatigue — risk of overreaching"
}

CHEAT_SHEET["future_colors"] = {
    "transition": "#66ccff",
    "fresh": "#99ff99",
    "grey": "#cccccc",
    "optimal": "#ffcc66",
    "high_risk": "#ff6666"
}

# --- Backward compatibility aliases ---
if "IFDrift" in CHEAT_SHEET["advice"]:
    CHEAT_SHEET["advice"]["EfficiencyDrift"] = CHEAT_SHEET["advice"]["IFDrift"]
if "IFDrift" in CHEAT_SHEET["thresholds"]:
    CHEAT_SHEET["thresholds"]["EfficiencyDrift"] = CHEAT_SHEET["thresholds"]["IFDrift"]


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

