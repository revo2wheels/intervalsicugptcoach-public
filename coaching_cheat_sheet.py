#!/usr/bin/env python3
"""
coaching_cheat_sheet.py — Unified v16.17 Coaching Reference
Contains static thresholds, labels, and helper summaries for derived metrics.
"""
import pandas as pd

# --- Global Coaching Cheat Sheet Dictionary ---
CHEAT_SHEET = {}

# === Thresholds ===
CHEAT_SHEET["thresholds"] = {
    "ACWR": {"green": (0.8, 1.3), "amber": (0.6, 1.5)},
    "Monotony": {"green": (1.0, 2.0), "amber": (0.8, 2.5)},
    "Strain": {"green": (0, 3000), "amber": (3000, 4000)},
    "RecoveryIndex": {"green": (0.6, 1.0), "amber": (0.4, 0.6)},
    "Polarisation": {"green": (0.75, 0.90), "amber": (0.65, 0.95)},   # Seiler ratio (% displayed)
    "PolarisationIndex": {"green": (0.75, 1.00), "amber": (0.60, 0.75)},  # Normalized index (0–1)
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
    "Lactate": {"lt1_mmol": 2.0,"lt2_mmol": 4.0,"corr_threshold": 0.6}
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
    "Polarisation": (
        "Seiler Polarisation Ratio showing the balance of low- and high-intensity work "
        "relative to moderate-intensity (Z2) training. "
        "≥1.0 indicates a well-polarised (80/20) structure; 0.7–0.99 = mixed; <0.7 = threshold-heavy. "
        "Displayed in reports as a percentage (e.g., 0.78 → 78%)."
    ),
    "PolarisationIndex": (
        "Normalized time-in-zone index (0–1) showing total proportion of training spent "
        "in low and moderate intensities (Z1+Z2). "
        "≥0.75 indicates strong aerobic bias, 0.6–0.74 = mixed distribution, <0.6 = threshold dominance."
    ),
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
}

CHEAT_SHEET["coaching_links"] = {
    # --- Derived Metric Coaching Links ---
    "ACWR": "If ACWR > 1.5, reduce intensity and focus on recovery to avoid overload. If ACWR < 0.8, gradually increase training load with controlled progression to build endurance.",
    "Monotony": "If Monotony > 2.5, introduce more variation in training or implement a deload week to reduce repetitive stress.",
    "Strain": "If Strain > 3000, monitor for signs of overreach and consider more rest or deloading. If Strain > 3500, consider reducing volume or intensity temporarily.",
    "RecoveryIndex": "If RecoveryIndex is low (<0.7), ensure adequate rest and recovery, and avoid heavy training loads.",
    "FatigueTrend": "If FatigueTrend is negative (e.g., below -0.2), this indicates a recovering state. Continue with controlled training load and focus on recovery to ensure sustained progress. Avoid aggressive increases in load.",
    "FatOxEfficiency": "If FatOxEfficiency is low (<0.6), focus on improving aerobic base with longer, low-intensity efforts.",
    "Polarisation": (
        "If Polarisation <0.7, increase low-intensity (Z1) aerobic volume and distinct "
        "high-intensity (Z3) sessions to achieve ≥1.0. "
        "Maintain ≥1.0 for a balanced 80/20 distribution. "
        "Reported as a percentage (e.g., 0.78 → 78%)."
    ),
    "PolarisationIndex": (
        "If PolarisationIndex <0.60, training load is too threshold-heavy. "
        "Rebalance toward greater Z1 endurance and reduced Z2 time. "
        "Target ≥0.75 for efficient aerobic adaptation and recovery balance."
    ),
    "ZQI": "If ZQI > 20%, review pacing strategy; excessive high-intensity time could indicate erratic pacing or overtraining. Aim for 5-15% ZQI for balanced training.",
    "FOxI": "If FOxI is increasing, continue to prioritize low-intensity work to enhance fat metabolism. If it decreases, consider increasing your Zone 2 training duration.",
    "CUR": "If CUR is outside the green zone (30-70), adjust carbohydrate intake and fueling strategy to ensure balanced metabolic use during long sessions.",
    "GR": "If GR exceeds 2.0, focus on reducing glycolytic intensity and increase aerobic work. Ensure sufficient recovery to avoid over-reliance on carbs.",
    "MES": "If MES is below 20, work on improving metabolic efficiency by increasing endurance training with a focus on aerobic base and fat metabolism.",
    "StressTolerance": "If StressTolerance is high (>8), reduce overall load and increase recovery time. If it's low (<2), ensure proper training load progression.",
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
    "EfficiencyDrift": {
        "high": "⚠ Efficiency drift high ({:.2%}) — improve aerobic durability or reduce fatigue load.",
        "stable": "✅ Efficiency drift stable ({:.2%})."
    },

    "Polarisation": {
        "low": "⚠ Polarisation low ({:.0%}) — increase Z1–Z2 share toward ≥70 %. ",
        "optimal": "✅ Polarisation optimal ({:.0%})."
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

# === Labels ===
CHEAT_SHEET["labels"] = {
    "acwr_risk": "EWMA Acute:Chronic Load Ratio",
    "strain": "Load × Monotony",
    "fatigue_trend": "EMA(Load, decay=0.2) (Percentage change)",
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

