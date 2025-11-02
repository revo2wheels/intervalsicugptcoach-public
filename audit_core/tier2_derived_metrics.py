"""
Tier-2 Step 6 — Derived Metrics (v16)
Calculates ACWR, Monotony, Strain, Polarisation, Recovery Index, FatOxidation, Decoupling, FatMaxDeviation.
"""

def compute_derived_metrics(daily_data, context):
    # Compute all numeric metrics here
    # Example placeholders; replace with real math
    context["ACWR"] = round(daily_data["load_7d"] / daily_data["load_28d_avg"], 2)
    context["Monotony"] = round(daily_data["mean_load"] / max(daily_data["std_load"], 1), 2)
    context["Strain"] = int(round(context["Monotony"] * daily_data["load_7d"]))
    context["Polarisation"] = round(daily_data.get("polarisation", 0.85), 2)
    context["RecoveryIndex"] = round(1 - (context["Monotony"] / 5), 2)
    context["FatOxidation"] = round(daily_data.get("fatox", 0.82), 2)
    context["Decoupling"] = round(daily_data.get("decoupling", 0.03), 2)
    context["FatMaxDeviation"] = round(daily_data.get("fatmax_dev", 0.02), 2)
    context["weeks_since_last_FTP"] = daily_data.get("weeks_since_last_FTP", 6)
    return context
