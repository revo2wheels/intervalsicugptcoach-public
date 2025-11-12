#!/usr/bin/env python3
"""
coaching_cheat_sheet.py — Unified v16.17 Coaching Reference
Contains static thresholds, labels, and helper summaries for derived metrics.
"""

# --- Global Coaching Cheat Sheet Dictionary ---
CHEAT_SHEET = {}

# === Thresholds ===
CHEAT_SHEET["thresholds"] = {
    "ACWR": {"green": (0.8, 1.3), "amber": (0.6, 1.5)},
    "Monotony": {"green": (1.0, 2.0), "amber": (0.8, 2.5)},
    "Strain": {"green": (0, 3000), "amber": (3000, 4000)},
    "RecoveryIndex": {"green": (0.6, 1.0), "amber": (0.4, 0.6)},
    "Polarisation": {"green": (0.75, 0.90), "amber": (0.65, 0.95)},
    "FatigueTrend": {"green": (-0.2, 0.2), "amber": (-0.4, 0.4)},
    "StressTolerance": {"green": (2.0, 8.0), "amber": (1.0, 10.0)},
    "FatOxEfficiency": {"green": (0.4, 0.8), "amber": (0.3, 0.9)},
    "FOxI": {"green": (30, 80), "amber": (20, 90)},          # FatOx Index %
    "CUR": {"green": (30, 70), "amber": (20, 80)},        # Carbohydrate Utilisation Ratio
    "GR": {"green": (0.5, 2.0), "amber": (0.3, 3.0)},         # Glucose Ratio
    "MES": {"green": (20, 100), "amber": (10, 120)},          # Metabolic Efficiency Score
    "ACWR_Risk": {"green": (0, 1), "amber": (1, 1)},          # Placeholder to silence undefined
    "ZQI": {"green": (5, 15), "amber": (3, 20)},               #% now
}

CHEAT_SHEET["context"] = {
    "ACWR": (
    "EWMA Acute:Chronic Load Ratio — compares 7-day vs 28-day weighted loads. "
    "0.8–1.3 = productive training, <0.8 = recovery or detraining, >1.5 = overload/injury risk."
),
    "Monotony": "1–2 shows healthy variation; >2.5 means repetitive stress pattern.",
    "Strain": "Product of load × monotony; >3500 signals potential overreach.",
    "FatigueTrend": "0±0.2 indicates balance; positive trend means accumulating fatigue.",
    "ZQI": "Zone Quality Index (%) 5-15 high-intensity time is normal <3% too easy, >20% too intense or erratic pacing.",
    "FatOxEfficiency": "0.4–0.8 means balanced fat oxidation; lower = carb dependence.",
    "Polarisation": "0.75–0.9 matches Seiler 80/20 distribution; <0.7 = too intense.",
    "FOxI": "FatOx index %; higher values mean more efficient aerobic base.",
    "CUR": "Carbohydrate Utilisation Ratio; 30-80 balanced metabolic use.",
    "GR": "Glucose Ratio; >2 indicates excess glycolytic bias.",
    "MES": "Metabolic Efficiency Score; >20 is good endurance economy.",
    "RecoveryIndex": "0.6–1.0 means recovered; <0.5 = heavy fatigue.",
    "ACWR_Risk": "Used internally for stability check.",
    "StressTolerance": "2–8 indicates sustainable training strain capacity.",
}

CHEAT_SHEET["coaching_links"] = {
    # --- Derived Metric Coaching Links ---
    "ACWR": "Guides short-term vs. chronic load balance adjustments.",
    "Monotony": "Used to determine need for rest or deload variation.",
    "Strain": "Informs total stress tolerance and recovery planning.",
    "RecoveryIndex": "Influences rest day scheduling and microcycle tapering.",
    "FatigueTrend": "Signals need for load stabilization or downshift.",
    "Polarisation": "Determines intensity mix correction (Seiler balance).",
    "FatOxEfficiency": "Drives aerobic base and metabolic conditioning feedback.",
    "FOxI": "Helps assess Zone 2 progression and fat adaptation.",
    "CUR": "Advises on fueling strategy and carbohydrate dependency.",
    "MES": "Summarizes efficiency adaptation response.",

    # --- Efficiency & Adaptation Coaching Links ---
    "Efficiency Factor": "Ratio of power to heart rate — higher indicates improved aerobic efficiency.",
    "Fatigue Resistance": "Ability to maintain power over time; >0.9 shows strong endurance resilience.",
    "Endurance Decay": "Rate of endurance loss; <0.05 indicates sustainable aerobic base.",
    "Z2 Stability": "Consistency in Zone 2 heart rate vs. power; <0.05 suggests steady aerobic control.",
    "Aerobic Decay": "Long-term aerobic deterioration rate; <0.03 means stable base conditioning.",
    "StressTolerance": "Reflects sustainable strain capacity; 2–8 indicates robust adaptation to training load.",
    "ZQI": "Represents proportion of high-intensity time; 5–15 % indicates balanced intensity distribution.",
    "GR": "Glucose Ratio; gauges glycolytic bias — higher values indicate heavy carbohydrate reliance.",
}

# === Labels ===
CHEAT_SHEET["labels"] = {
    "acwr_risk": "EWMA Acute:Chronic Load Ratio",
    "strain": "Load × Monotony",
    "fatigue_trend": "EMA(Load, decay=0.2)",
}

# === Cheat Sheet Accessor ===
def summarize_load_block(context):
    """
    Summarize current training block load distribution using CHEAT_SHEET_RULES.
    """
    load = context.get("totalTss", 0)
    duration = context.get("totalHours", 0)
    acwr = context.get("ACWR", 1.0)

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
