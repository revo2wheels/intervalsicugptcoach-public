"""
tier3_future_forecast.py
------------------------

Tier-3: Future Forecast Module (Unified Coaching Framework v5.1)
---------------------------------------------------------------
- Projects CTL/ATL/TSB using Banister impulse-response model.
- Pulls dynamic thresholds and coaching actions from CHEAT_SHEET.
- Auto-fetches planned calendar events via Cloudflare Worker.
- Returns canonical keys for semantic_json_builder.py integration.
"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os, requests, json, traceback
from audit_core.utils import debug, resolve_prefetched
from coaching_cheat_sheet import CHEAT_SHEET

CLOUDFLARE_BASE = os.getenv("CLOUDFLARE_BASE", "https://intervalsicugptcoach.clive-a5a.workers.dev")
ICU_TOKEN = os.getenv("ICU_OAUTH")

# ---------------------------------------------------------------------
# ⚙️ Cloudflare Calendar Fallback Loader
# ---------------------------------------------------------------------
def fetch_calendar_fallback(context, days=14, owner="intervals"):
    """Fetch planned events via Cloudflare Worker if not prefetched."""
    start = datetime.now().date().isoformat()
    end = (datetime.now().date() + timedelta(days=days)).isoformat()
    url = f"{CLOUDFLARE_BASE}/calendar/read?start={start}&end={end}&owner={owner}"
    headers = {"content-type": "application/json"}
    if ICU_TOKEN:
        headers["Authorization"] = f"Bearer {ICU_TOKEN}" 

    try:
        debug(context, f"[T3] 🔄 Fetching fallback calendar ({days}d)...")
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        context["calendar"] = data
        debug(context, f"[T3] 📥 Injected {len(data)} planned events into context")
        return data
    except Exception as e:
        debug(context, f"[T3] ⚠️ Calendar fallback fetch failed: {e}")
        traceback.print_exc()
        return []

# ---------------------------------------------------------------------
# 📅 Calendar Resolver
# ---------------------------------------------------------------------
def resolve_calendar(context, forecast_days=14):
    """Resolve planned calendar from prefetched or fallback source."""
    planned = resolve_prefetched("calendar", context, fetch_fn=fetch_calendar_fallback, days=forecast_days)
    if isinstance(planned, list) and len(planned) > 0:
        debug(context, f"[T3] ✅ Calendar resolved ({len(planned)} events)")
    else:
        debug(context, "[T3] ⚠️ No planned events available after resolution")
    return planned

# ---------------------------------------------------------------------
# 🚀 Tier-3 Future Forecast
# ---------------------------------------------------------------------
def run_future_forecast(context, forecast_days="auto"):
    """
    Compute Tier-3 forecast metrics:
    - CTL, ATL, and TSB forward projections
    - Fatigue classification via CHEAT_SHEET thresholds
    - Future-oriented coaching actions (actions_future)
    """

    debug(context, "───────────────────────────────────────────────")
    debug(context, f"[T3] 🧭 Starting Future Forecast (mode={forecast_days})")

    # -----------------------------------------------------------------
    # 1️⃣ Acquire planned events
    # -----------------------------------------------------------------
    planned = resolve_calendar(context, 14 if forecast_days == "auto" else forecast_days)
    if not isinstance(planned, list) or len(planned) == 0:
        debug(context, "[T3] ⚠️ No planned events found → aborting forecast.")
        return {"future_forecast": {}, "actions_future": []}

    df = pd.DataFrame(planned)
    if df.empty:
        return {"future_forecast": {}, "actions_future": []}

    if "icu_training_load" not in df.columns:
        df["icu_training_load"] = df.get("tss", 0)

    df["date"] = pd.to_datetime(df["start_date_local"].astype(str).str[:10], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")
    if df.empty:
        debug(context, "[T3] ⚠️ No valid event dates → abort.")
        return {"future_forecast": {}, "actions_future": []}

    # -----------------------------------------------------------------
    # 2️⃣ Determine forecast horizon
    # -----------------------------------------------------------------
    if forecast_days == "auto":
        distinct_days = len(df["date"].dt.date.unique())
        forecast_days = max(7, distinct_days)
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=forecast_days)
    forecast_window = pd.date_range(start=start_date, end=end_date, freq="D")

    # -----------------------------------------------------------------
    # 3️⃣ Seed CTL/ATL from latest or fallback
    # -----------------------------------------------------------------
    ctl = float(df["icu_ctl"].dropna().iloc[-1]) if "icu_ctl" in df.columns and df["icu_ctl"].notna().any() else float(context.get("wellness_summary", {}).get("ctl", 70.0))
    atl = float(df["icu_atl"].dropna().iloc[-1]) if "icu_atl" in df.columns and df["icu_atl"].notna().any() else float(context.get("wellness_summary", {}).get("atl", 65.0))
    tsb = ctl - atl
    debug(context, f"[T3] ⚙️ Seeded CTL={ctl:.2f}, ATL={atl:.2f}, TSB={tsb:.2f}")

    # -----------------------------------------------------------------
    # 4️⃣ Build daily load series
    # -----------------------------------------------------------------
    daily_load = (
        df.groupby("date", as_index=True)["icu_training_load"]
        .sum(numeric_only=True)
        .astype(float)
        .sort_index()
    )
    load_series = daily_load.reindex(forecast_window, fill_value=0.0)

    # -----------------------------------------------------------------
    # 5️⃣ Compute CTL/ATL/TSB via Banister model
    # -----------------------------------------------------------------
    ctl_values, atl_values, tsb_values = [], [], []
    for load in load_series:
        atl = atl + (load - atl) / 7.0
        ctl = ctl + (load - ctl) / 42.0
        tsb = ctl - atl
        ctl_values.append(ctl)
        atl_values.append(atl)
        tsb_values.append(tsb)

    # -----------------------------------------------------------------
    # 6️⃣ Derive fatigue/form zone aligned with Intervals.icu categories
    # -----------------------------------------------------------------
    thresholds = CHEAT_SHEET.get("thresholds", {}).get("TSB", {})
    latest_tsb = tsb_values[-1]
    fatigue_class = "grey"  # default fallback

    # Dynamically classify based on Cheat Sheet numeric ranges
    for zone, (low, high) in thresholds.items():
        if low <= latest_tsb <= high:
            fatigue_class = zone
            break

    # Ensure zone is recognized in future_actions definitions
    if fatigue_class not in CHEAT_SHEET.get("future_actions", {}):
        debug(context, f"[T3] ⚠️ Fatigue class '{fatigue_class}' not found in CHEAT_SHEET.future_actions")
        fatigue_class = "grey"

    debug(
        context,
        f"[T3] 🧠 Intervals-aligned Fatigue/Form classification → "
        f"{fatigue_class.upper()} (TSB={latest_tsb:.2f})"
    )


    # -----------------------------------------------------------------
    # 7️⃣ Future state summary
    # -----------------------------------------------------------------
    future_state = {
        "start_date": str(start_date),
        "end_date": str(end_date),
        "horizon_days": forecast_days,
        "CTL_future": round(float(ctl_values[-1]), 2),
        "ATL_future": round(float(atl_values[-1]), 2),
        "TSB_future": round(float(latest_tsb), 2),
        "load_trend": "increasing" if ctl_values[-1] > ctl_values[0] else "declining",
        "fatigue_class": fatigue_class,
    }
    # -----------------------------------------------------------------
    # 8️⃣ Coaching actions (canonical from CHEAT_SHEET with labels/colors)
    # -----------------------------------------------------------------

    cheat_actions = CHEAT_SHEET.get("future_actions", {})
    future_labels = CHEAT_SHEET.get("future_labels", {})
    future_colors = CHEAT_SHEET.get("future_colors", {})

    actions_future = []
    fatigue_class = future_state.get("fatigue_class", "grey")

    if fatigue_class in cheat_actions:
        fa_def = cheat_actions[fatigue_class]
        actions_future.append({
            "priority": fa_def.get("priority", "normal"),
            "title": fa_def.get("title", fatigue_class.title()),
            "reason": fa_def.get("reason", ""),
            "label": future_labels.get(fatigue_class, fatigue_class.title()),
            "color": future_colors.get(fatigue_class, "#cccccc"),
            "date_range": f"{future_state['start_date']} → {future_state['end_date']}"
        })
    else:
        actions_future.append({
            "priority": "normal",
            "title": "Maintain current plan",
            "reason": f"No mapped future action for class '{fatigue_class}'.",
            "label": fatigue_class.title(),
            "color": "#999999",
            "date_range": f"{future_state['start_date']} → {future_state['end_date']}"
        })

    debug(context, f"[T3] ✅ Forecast ready — class={fatigue_class}, actions={len(actions_future)}")
    debug(context, f"[T3] Summary: {json.dumps(future_state, indent=2)}")
    debug(context, f"[T3] Future action: {actions_future[0]['title']}")

    # Inject into context so the semantic builder picks it up
    context["future_forecast"] = future_state
    context["actions_future"] = actions_future

    return {
        "future_forecast": future_state,
        "actions_future": actions_future
    }
