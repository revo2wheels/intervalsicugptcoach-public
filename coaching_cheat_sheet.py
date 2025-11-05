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
