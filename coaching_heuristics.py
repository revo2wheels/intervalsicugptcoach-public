HEURISTICS = {
    "acwr_window_days": 7,
    "baseline_window_days": 28,
    "fatigue_decay_const": 0.2,
    "stress_tolerance_scale": 100,
    "polarisation_target": 0.85,
    "recovery_floor": 0.75,
    "efficiency_smoothing": 0.15,
}

# === Heuristic Accessors ===

def derive_trends(context):
    """
    Compute simplified load and adaptation trends using rolling averages
    and heuristics defined in HEURISTICS_TABLES.
    """
    import numpy as np
    df = context.get("df_events")
    if df is None or df.empty:
        return {"trend_load": None, "trend_fatigue": None}

    try:
        df = df.sort_values("date")
        df["load_rolling"] = df["icu_training_load"].rolling(window=7, min_periods=3).mean()
        df["fatigue_trend"] = df["load_rolling"].pct_change().fillna(0)
        return {
            "trend_load": round(df["load_rolling"].iloc[-1], 2),
            "trend_fatigue": round(df["fatigue_trend"].iloc[-1], 3),
        }
    except Exception:
        return {"trend_load": None, "trend_fatigue": None}


def derive_correlations(context):
    """
    Compute correlations (e.g. fatigue vs load) using recent data.
    """
    import numpy as np
    df = context.get("df_events")
    if df is None or df.empty:
        return {"fatigue_vs_load": None, "power_hr_corr": None}

    try:
        fatigue = df["fatigue"].values if "fatigue" in df else None
        load = df["icu_training_load"].values
        hr = df["hr"].values if "hr" in df else None
        power = df["power"].values if "power" in df else None

        results = {}
        if fatigue is not None:
            results["fatigue_vs_load"] = float(np.corrcoef(fatigue, load)[0, 1])
        if hr is not None and power is not None:
            results["power_hr_corr"] = float(np.corrcoef(power, hr)[0, 1])
        return results
    except Exception:
        return {"fatigue_vs_load": None, "power_hr_corr": None}
