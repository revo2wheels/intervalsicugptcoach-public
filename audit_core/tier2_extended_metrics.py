def compute_extended_metrics(context):
    """
    Tier-3 Extended Metrics for URF v5.1
    ------------------------------------
    MUST use df_light (90-day dataset), not df_events (7-day),
    otherwise adaptation / trends / correlations all collapse to {}.

    Produces:
      • CTL / ATL / TSB
      • Adaptation metrics
      • Trend metrics
      • Correlation metrics
    """

    # ---------------------------------------------------------
    # 1️⃣ SOURCE DATA: must use df_light (long horizon)
    # ---------------------------------------------------------
    df_light = context.get("df_light")
    if df_light is None or isinstance(df_light, list):
        try:
            df_light = pd.DataFrame(df_light)
        except Exception:
            df_light = pd.DataFrame()

    if df_light is None or df_light.empty:
        debug(context, "[EXT] ERROR: df_light missing — extended metrics unavailable.")
        context["extended_metrics"] = {}
        return context

    # ---------------------------------------------------------
    # 2️⃣ Build DAILY LOAD TABLE required for CTL/ATL
    # ---------------------------------------------------------
    df_daily = (
        df_light[["start_date_local", "icu_training_load"]]
        .rename(columns={"start_date_local": "date"})
        .copy()
    )

    df_daily["date"] = pd.to_datetime(df_daily["date"]).dt.date
    df_daily = df_daily.groupby("date")["icu_training_load"].sum().reset_index()
    context["df_daily"] = df_daily

    # ---------------------------------------------------------
    # 3️⃣ LOAD METRICS: CTL / ATL / TSB
    # ---------------------------------------------------------
    from coaching_cheat_sheet import summarize_load_block
    load = summarize_load_block(context)

    context["load_metrics"] = {
        "CTL": {"value": load.get("ctl", 0), "status": "ok"},
        "ATL": {"value": load.get("atl", 0), "status": "ok"},
        "TSB": {"value": load.get("tsb", 0), "status": "ok"},
    }

    # ---------------------------------------------------------
    # 4️⃣ ADAPTATION METRICS (profile-based)
    # ---------------------------------------------------------
    from coaching_profile import get_profile_metrics
    profile = get_profile_metrics(context)

    context["adaptation_metrics"] = {
        "Efficiency Factor": profile.get("eff_factor", "—"),
        "Fatigue Resistance": profile.get("fatigue_resistance", "—"),
        "Endurance Decay": profile.get("endurance_decay", "—"),
        "Z2 Stability": profile.get("z2_stability", "—"),
        "Aerobic Decay": profile.get("aerobic_decay", "—"),
    }

    # ---------------------------------------------------------
    # 5️⃣ TREND METRICS (42-day behaviour)
    # ---------------------------------------------------------
    from coaching_heuristics import derive_trends
    trend = derive_trends(context)

    context["trend_metrics"] = {
        "load_trend": trend.get("load_trend", "—"),
        "fitness_trend": trend.get("fitness_trend", "—"),
        "fatigue_trend": trend.get("fatigue_trend", "—"),
    }

    # ---------------------------------------------------------
    # 6️⃣ CORRELATION METRICS
    # ---------------------------------------------------------
    from coaching_heuristics import derive_correlations
    corr = derive_correlations(context)

    context["correlation_metrics"] = {
        "power_hr_correlation": corr.get("power_hr_correlation", "—"),
        "efficiency_factor_change": corr.get("efficiency_factor_change", "—"),
        "fatigue_vs_load": corr.get("fatigue_vs_load", "—"),
    }

    # ---------------------------------------------------------
    # 7️⃣ EXTENDED METRIC OUTPUT (no duplication)
    # ---------------------------------------------------------
    context["extended_metrics"] = {
        # Load block
        "CTL": context["load_metrics"]["CTL"],
        "ATL": context["load_metrics"]["ATL"],
        "TSB": context["load_metrics"]["TSB"],

        # Adaptation
        "EfficiencyFactor": context["adaptation_metrics"]["Efficiency Factor"],
        "FatigueResistance": context["adaptation_metrics"]["Fatigue Resistance"],
        "EnduranceDecay": context["adaptation_metrics"]["Endurance Decay"],
        "Z2Stability": context["adaptation_metrics"]["Z2 Stability"],
        "AerobicDecay": context["adaptation_metrics"]["Aerobic Decay"],

        # Trends
        "LoadTrend": context["trend_metrics"]["load_trend"],
        "FitnessTrend": context["trend_metrics"]["fitness_trend"],
        "FatigueTrend": context["trend_metrics"]["fatigue_trend"],

        # Correlations
        "PowerHRCorr": context["correlation_metrics"]["power_hr_correlation"],
        "EfficiencyFactorChange": context["correlation_metrics"]["efficiency_factor_change"],
        "FatigueVsLoad": context["correlation_metrics"]["fatigue_vs_load"],
    }

    debug(context, "[EXT] Extended metrics computed successfully (90-day horizon).")
    return context
