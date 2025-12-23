# tier3_future_forecast.py
# forecast trend and actions
#
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from audit_core.utils import debug

def compute_future_forecast(context, forecast_days: int = 14):
    """Compute forward ATL/CTL/TSB + fatigue and readiness metrics."""
    debug(context, f"[T3] 🚀 Starting extended future forecast (window={forecast_days}d)")

    df_daily = context.get("df_daily")
    if df_daily is None or getattr(df_daily, "empty", True):
        debug(context, "[T3] ⚠️ No df_daily found — aborting forecast.")
        return context

    planned_summary = context.get("planned_summary_by_date", {}) or {}
    last_date = pd.to_datetime(df_daily["date"].max())
    today = pd.Timestamp.now().normalize()
    forecast_start = max(last_date, today)
    forecast_dates = pd.date_range(start=forecast_start, periods=forecast_days + 1, freq="D")[1:]

    # Build load profile
    planned_loads = []
    for d in forecast_dates:
        iso = d.date().isoformat()
        load = float(planned_summary.get(iso, {}).get("total_load", 0))
        planned_loads.append({"date": d, "icu_training_load": load})
    df_future = pd.DataFrame(planned_loads)

    if df_future.empty:
        debug(context, "[T3] ⚠️ No future load data to forecast.")
        return context

    ctl_start = float(context.get("wellness_summary", {}).get("ctl", 0) or 0)
    atl_start = float(context.get("wellness_summary", {}).get("atl", 0) or 0)
    k_ctl, k_atl = 1/42, 1/7

    df_all = pd.concat([df_daily[["date","icu_training_load"]], df_future]).sort_values("date").reset_index(drop=True)
    ctl, atl = [ctl_start], [atl_start]

    for i in range(1, len(df_all)):
        load = df_all.loc[i-1, "icu_training_load"]
        ctl.append(ctl[-1] + k_ctl*(load - ctl[-1]))
        atl.append(atl[-1] + k_atl*(load - atl[-1]))

    df_all["CTL"], df_all["ATL"] = ctl, atl
    df_all["TSB"] = df_all["CTL"] - df_all["ATL"]

    # Extract forecast segment
    df_future_metrics = df_all[df_all["date"].isin(df_future["date"])].copy()
    df_future_metrics["FatigueIndex"] = (df_future_metrics["ATL"] - df_future_metrics["CTL"]) / df_future_metrics["CTL"] * 100
    df_future_metrics["RampRate"] = df_future_metrics["CTL"].diff(7).fillna(0)
    df_future_metrics["FormTrend"] = df_future_metrics["TSB"].diff().rolling(3).mean()
    mean_load, std_load = df_future_metrics["icu_training_load"].mean(), df_future_metrics["icu_training_load"].std(ddof=0)
    monotony = (mean_load / std_load) if std_load > 0 else 0
    strain = mean_load * monotony

    phase = "recovery" if df_future_metrics["TSB"].iloc[-1] > 10 else \
            "productive" if df_future_metrics["TSB"].iloc[-1] > -10 else "overreaching"

    forecast = {
        "forecast_window_days": forecast_days,
        "projected_ctl": round(df_future_metrics["CTL"].iloc[-1], 1),
        "projected_atl": round(df_future_metrics["ATL"].iloc[-1], 1),
        "projected_tsb": round(df_future_metrics["TSB"].iloc[-1], 1),
        "projected_fatigue_index": round(df_future_metrics["FatigueIndex"].iloc[-1], 1),
        "projected_phase": phase,
        "ramp_rate_7d": round(df_future_metrics["RampRate"].iloc[-1], 1),
        "monotony": round(monotony, 2),
        "strain": round(strain, 1),
        "daily_projection": [
            {
                "date": d.date().isoformat(),
                "load": float(l),
                "ctl": round(c, 1),
                "atl": round(a, 1),
                "tsb": round(t, 1),
                "fatigue_index": round(f, 1),
            }
            for d, l, c, a, t, f in zip(
                df_future_metrics["date"],
                df_future_metrics["icu_training_load"],
                df_future_metrics["CTL"],
                df_future_metrics["ATL"],
                df_future_metrics["TSB"],
                df_future_metrics["FatigueIndex"],
            )
        ],
    }

    context["future_forecast"] = forecast
    context["actions_future"] = generate_future_actions(forecast)
    debug(context, f"[T3] ✅ Extended forecast ready → phase={phase}")
    return context


def generate_future_actions(forecast: dict):
    """Contextual recommendations from forecast metrics."""
    actions = []
    tsb, fatigue = forecast["projected_tsb"], forecast["projected_fatigue_index"]
    ramp, monotony = forecast["ramp_rate_7d"], forecast["monotony"]

    if tsb < -15 or fatigue > 20:
        actions.append("⚠️ High fatigue expected — consider recovery or deload.")
    elif tsb > 10:
        actions.append("✅ Freshness rising — plan quality session or test.")
    if ramp > 6:
        actions.append("📈 Load ramp accelerating — monitor closely.")
    if monotony > 2:
        actions.append("⚖️ Training monotony high — vary sessions to reduce risk.")

    if not actions:
        actions.append("Load and recovery appear balanced.")
    return actions
