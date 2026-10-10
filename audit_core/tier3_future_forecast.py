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
from audit_core.intervals_auth import intervals_auth_headers

# ---------------------------------------------------------------------
# ⚙️ Cloudflare Calendar Fallback Loader
# ---------------------------------------------------------------------
def fetch_calendar_fallback(context, days=14, owner="intervals"):
    """Fetch planned events via Cloudflare Worker if not prefetched."""
    start = datetime.now().date().isoformat()
    end = (datetime.now().date() + timedelta(days=days)).isoformat()
    intervals_api = os.getenv("INTERVALS_API", "")
    if "intervals.icu/api" in intervals_api:
        # report.py --direct: the standard Intervals.icu events list, as the Worker's /calendar/read returns.
        url = f"{intervals_api}/athlete/0/events?oldest={start}&newest={end}"
    else:
        url = f"{CLOUDFLARE_BASE}/calendar/read?start={start}&end={end}&owner={owner}"
    headers = {"content-type": "application/json"}
    headers.update(intervals_auth_headers()) 

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
    # 2️⃣ Determine forecast horizon (max 14 days, none if no plan)
    # -----------------------------------------------------------------

    start_date = datetime.now().date()

    if forecast_days == "auto":

        future_df = df[df["date"].dt.date >= start_date]

        if future_df.empty:
            forecast_days = 0
        else:
            last_event_date = future_df["date"].max().date()
            forecast_days = (last_event_date - start_date).days

            # Cap to planning window
            forecast_days = min(forecast_days, 14)

    end_date = start_date + timedelta(days=forecast_days)

    if forecast_days > 0:
        forecast_window = pd.date_range(
            start=start_date,
            end=end_date,
            freq="D"
        )
    else:
        forecast_window = pd.DatetimeIndex([])

    # -------------------------------------------------
    # Restrict plan to forecast window
    # -------------------------------------------------

    df_future = df[
        (df["date"].dt.date >= start_date) &
        (df["date"].dt.date <= end_date)
    ]

    if df_future.empty:
        debug(context, "[T3] ⚠️ No planned events inside forecast window")
        return {"future_forecast": {}, "actions_future": []}

    # -----------------------------------------------------------------
    # 3️⃣ Seed CTL/ATL from latest or fallback
    # -----------------------------------------------------------------
    ctl = float(df["icu_ctl"].dropna().iloc[-1]) if "icu_ctl" in df.columns and df["icu_ctl"].notna().any() else float(context.get("wellness_summary", {}).get("ctl", 70.0))
    atl = float(df["icu_atl"].dropna().iloc[-1]) if "icu_atl" in df.columns and df["icu_atl"].notna().any() else float(context.get("wellness_summary", {}).get("atl", 65.0))
    tsb = ctl - atl
    debug(context, f"[T3] ⚙️ Seeded CTL={ctl:.2f}, ATL={atl:.2f}, TSB={tsb:.2f}")

    # -----------------------------------------------------------------
    # 4️⃣ Use Intervals projected CTL/ATL directly
    # -----------------------------------------------------------------

    def _safe_float(v, fallback):
        try:
            v = float(v)
            if np.isnan(v):
                return float(fallback)
            return v
        except (TypeError, ValueError):
            return float(fallback)


    last_row = df_future.iloc[-1]

    ctl_future = _safe_float(last_row.get("icu_ctl"), ctl)
    atl_future = _safe_float(last_row.get("icu_atl"), atl)
    latest_tsb = ctl_future - atl_future
    
    # determine trend vs current CTL
    current_ctl = _safe_float(
        context.get("wellness_summary", {}).get("ctl"),
        ctl_future
    )
    load_trend = "increasing" if ctl_future > current_ctl else "declining"
    # -----------------------------------------------------------------
    # 6️⃣ Derive fatigue/form zone aligned with Intervals.icu categories
    # -----------------------------------------------------------------
    thresholds = CHEAT_SHEET.get("thresholds", {}).get("TSB", {})
    
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
        "CTL_future": round(ctl_future, 2),
        "ATL_future": round(atl_future, 2),
        "TSB_future": round(latest_tsb, 2),
        "load_trend": load_trend,
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
