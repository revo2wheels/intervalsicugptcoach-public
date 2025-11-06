CHEAT_SHEET = {
    "thresholds": {
        "acwr_risk_high": 1.5,
        "acwr_optimal": (0.8, 1.3),
        "monotony_alert": 2.0,
        "strain_critical": 700,
        "fatigue_high": 0.25,
        "recovery_index_low": 0.7,
        "polarisation_default": 0.85,
    },
    "labels": {
        "acwr_risk": "Acute:Chronic Load Ratio",
        "strain": "Load × Monotony",
        "fatigue_trend": "EMA(Load, decay=0.2)",
    },
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
