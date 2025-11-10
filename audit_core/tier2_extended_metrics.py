"""
Tier-2 Extended Metrics (v16.14-integrated)
Bridges derived_metrics with higher-order coaching, trend, and correlation layers.
Builds on Tier-2 Step 3 (Derived Metrics Calculation).
"""
from audit_core.utils import debug
from audit_core.tier2_derived_metrics import compute_derived_metrics
from coaching_profile import COACH_PROFILE, get_profile_metrics
from coaching_heuristics import HEURISTICS, derive_trends, derive_correlations
from coaching_cheat_sheet import CHEAT_SHEET, summarize_load_block


def compute_extended_metrics(df_daily, context):
    """Integrate derived metrics with Tier-3 knowledge modules."""

    # Step 1 — Core derived metrics (Tier-2)
    context = compute_derived_metrics(df_daily, context)

    # Step 2 — Tier-3: Load block insights (CTL, ATL, TSB)
    load_data = summarize_load_block(context)
    context["load_metrics"] = {
        "CTL": {"value": load_data.get("ctl", 0), "status": "ok"},
        "ATL": {"value": load_data.get("atl", 0), "status": "ok"},
        "TSB": {"value": load_data.get("tsb", 0), "status": "ok"},
        "ACWR": {"value": context.get("ACWR", 1.0), "status": "ok"},
        "Monotony": {"value": context.get("Monotony", 1.0), "status": "ok"},
        "Strain": {"value": context.get("Strain", 0), "status": "ok"},
        "Polarisation": {"value": context.get("Polarisation", 0), "status": "ok"},
        "RecoveryIndex": {"value": context.get("RecoveryIndex", 0), "status": "ok"},
    }

    # Step 3 — Tier-3: Coaching profile metrics
    profile = get_profile_metrics(context)
    context["adaptation_metrics"] = {
        "Efficiency Factor": profile.get("eff_factor", "—"),
        "Fatigue Resistance": profile.get("fatigue_resistance", "—"),
        "Endurance Decay": profile.get("endurance_decay", "—"),
        "Z2 Stability": profile.get("z2_stability", "—"),
        "Aerobic Decay": profile.get("aerobic_decay", "—"),
    }

    # Step 4 — Tier-3: Trends
    trend = derive_trends(context)
    context["trend_metrics"] = {
        "load_trend": trend.get("load_trend", "—"),
        "fitness_trend": trend.get("fitness_trend", "—"),
        "fatigue_trend": trend.get("fatigue_trend", "—"),
        "note": trend.get("note", ""),
    }

    # Step 5 — Tier-3: Correlations
    corr = derive_correlations(context)
    context["correlation_metrics"] = {
        "power_hr_correlation": corr.get("power_hr_correlation", "—"),
        "efficiency_factor_change": corr.get("efficiency_factor_change", "—"),
        "fatigue_vs_load": corr.get("fatigue_vs_load", "—"),
        "note": corr.get("note", ""),
    }

    return context
