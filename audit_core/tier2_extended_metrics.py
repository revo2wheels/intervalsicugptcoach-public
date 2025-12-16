# audit_core/tier2_extended_metrics.py

from audit_core.utils import debug


def compute_extended_metrics(context):
    """
    Tier-2 Extended Metrics for URF v5.1
    ------------------------------------
    CONSUMES authoritative CTL / ATL / TSB from context["load_metrics"]
    DOES NOT calculate training load.
    """

    # ---------------------------------------------------------
    # 0️⃣ REQUIRE authoritative load_metrics
    # ---------------------------------------------------------
    lm = context.get("load_metrics", {})

    if not all(k in lm for k in ("CTL", "ATL", "TSB")):
        debug(context, "[EXT-FATAL] load_metrics missing CTL/ATL/TSB — upstream injection failed")
        context.setdefault("extended_metrics", {})
        context.setdefault("adaptation_metrics", {})
        context.setdefault("trend_metrics", {})
        context.setdefault("correlation_metrics", {})
        return context

    debug(
        context,
        f"[EXT-LOAD] Using injected load_metrics "
        f"CTL={lm['CTL'].get('value')} "
        f"ATL={lm['ATL'].get('value')} "
        f"TSB={lm['TSB'].get('value')}"
    )

    # ---------------------------------------------------------
    # 1️⃣ ADAPTATION METRICS
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
    # 2️⃣ TREND METRICS
    # ---------------------------------------------------------
    from coaching_heuristics import derive_trends
    trend = derive_trends(context)

    context["trend_metrics"] = {
        "load_trend": trend.get("load_trend", "—"),
        "fitness_trend": trend.get("fitness_trend", "—"),
        "fatigue_trend": trend.get("fatigue_trend", "—"),
    }

    # ---------------------------------------------------------
    # 3️⃣ CORRELATION METRICS
    # ---------------------------------------------------------
    from coaching_heuristics import derive_correlations
    corr = derive_correlations(context)

    context["correlation_metrics"] = {
        "power_hr_correlation": corr.get("power_hr_correlation", "—"),
        "efficiency_factor_change": corr.get("efficiency_factor_change", "—"),
        "fatigue_vs_load": corr.get("fatigue_vs_load", "—"),
    }

    # ---------------------------------------------------------
    # 4️⃣ EXTENDED METRICS (authoritative assembly)
    # ---------------------------------------------------------
    context["extended_metrics"] = {
        # Load (from ICU)
        "CTL": lm["CTL"],
        "ATL": lm["ATL"],
        "TSB": lm["TSB"],

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

    debug(context, "[EXT] Extended metrics assembled (ICU authoritative load)")
    return context
