"""
tier3_future_forecast.py
------------------------

Tier-3: Future Forecast Module (local + staging safe)
-----------------------------------------------------
- Computes future load forecasts (CTL, ATL, TSB projections)
- Auto-fetches planned events via Cloudflare Worker if missing in context
- Uses audit_core.utils.debug() for unified logging
"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os, requests, json, traceback
from audit_core.utils import debug, resolve_prefetched

CLOUDFLARE_BASE = os.getenv("CLOUDFLARE_BASE", "https://intervalsicugptcoach.clive-a5a.workers.dev")
ICU_TOKEN = os.getenv("ICU_OAUTH")


# ---------------------------------------------------------------------
# ⚙️ Cloudflare Fallback Loader
# ---------------------------------------------------------------------
def fetch_calendar_fallback(context, days=14, owner="intervals"):
    """Fetch planned events from Cloudflare Worker if not prefetched."""
    start = datetime.now().date().isoformat()
    end = (datetime.now().date() + timedelta(days=days)).isoformat()
    url = f"{CLOUDFLARE_BASE}/calendar/read?start={start}&end={end}&owner={owner}"
    headers = {"content-type": "application/json"}
    if ICU_TOKEN:
        headers["Authorization"] = f"Bearer {ICU_TOKEN}"

    debug(context, f"[T3] 🔄 Fetching fallback calendar from Cloudflare: {url}")

    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        # 🔄 Inject into context for JSON builder compatibility
        context["calendar"] = data
        debug(context, f"[T3] 📥 Injected {len(data)} fetched calendar events into context for JSON builder")
        if len(data) > 0:
            preview = json.dumps(data[0], indent=2)[:300]
            debug(context, f"[T3] Example event preview: {preview} ...")
        return data
    except Exception as e:
        debug(context, f"[T3] ⚠️ Calendar fallback fetch failed: {e}")
        traceback.print_exc()
        return []

from audit_core.utils import debug, resolve_prefetched
from audit_core.tier3_future_forecast import fetch_calendar_fallback

def resolve_calendar(context, forecast_days=14):
    """
    Tier-3 calendar resolver using the shared resolve_prefetched() utility.
    """
    planned = resolve_prefetched("calendar", context, fetch_fn=fetch_calendar_fallback, days=forecast_days)

    if isinstance(planned, list) and len(planned) > 0:
        debug(context, f"[T3-RESOLVE] Calendar resolved ({len(planned)} events)")
    else:
        debug(context, "[T3-RESOLVE] ⚠️ No planned events available after prefetch resolution")

    return planned



# ---------------------------------------------------------------------
# 🚀 Main Forecast Runner
# ---------------------------------------------------------------------
def run_future_forecast(context, forecast_days=14):
    """
    Compute future forecast metrics:
    - Projected CTL/ATL/TSB
    - Rolling fatigue/recovery estimates
    - Forward coaching actions
    """

    # ───────────────────────────────────────────────
    debug(context, "───────────────────────────────────────────────")
    debug(context, f"[T3] 🧭 Starting Future Forecast (window={forecast_days} d)")
    debug(context, f"[T3] Context keys (first 12): {list(context.keys())[:12]}")

    # -----------------------------------------------------------------
    # 🔍 Prefetch status summary — checks prefetched + local calendars
    # -----------------------------------------------------------------
    prefetched = context.get("prefetched", {})
    pre_calendar = prefetched.get("calendar") if isinstance(prefetched, dict) else None
    local_calendar = context.get("calendar")

    has_prefetch = isinstance(pre_calendar, list) and len(pre_calendar) > 0
    has_local = isinstance(local_calendar, list) and len(local_calendar) > 0
    pre_keys = list(prefetched.keys()) if isinstance(prefetched, dict) else []

    debug(context, f"[T3] Prefetch keys: {pre_keys}")
    debug(
        context,
        f"[T3] Calendar sources → prefetched: {has_prefetch} "
        f"({len(pre_calendar) if has_prefetch else 0}), "
        f"local: {has_local} ({len(local_calendar) if has_local else 0})"
    )

    if has_prefetch:
        debug(context, f"[T3] ✅ Using prefetched calendar from Cloudflare ({len(pre_calendar)} events)")
    elif has_local:
        debug(context, f"[T3] ⚙️ Using local calendar ({len(local_calendar)} events)")
    else:
        debug(context, "[T3] ⚠️ No usable calendar detected — fallback or abort expected")


    # -----------------------------------------------------------------
    # 1️⃣ Acquire planned events (using shared resolver)
    # -----------------------------------------------------------------

    planned = resolve_prefetched(
        "calendar",
        context,
        fetch_fn=fetch_calendar_fallback,
        days=forecast_days
    )

    # -----------------------------------------------------------------
    # 2️⃣ Safety check
    # -----------------------------------------------------------------
    if not isinstance(planned, list) or len(planned) == 0:
        debug(context, "[T3] ⚠️ No usable calendar data available for future forecast → aborting.")
        return {
            "future_forecast": {},
            "actions_future": []
        }

    debug(context, f"[T3] 📅 {len(planned)} planned events loaded for forecast window")


    # -----------------------------------------------------------------
    # 3️⃣ Build forward projection series (final safe + full debug)
    # -----------------------------------------------------------------
    debug(context, f"[T3] 🧮 Building forward projection ({forecast_days}d window) …")

    try:
        # -----------------------------------------------------------------
        # Rebuild DataFrame inside try block to ensure df is in local scope
        # -----------------------------------------------------------------
        df = pd.DataFrame(planned)
        if "icu_training_load" not in df.columns:
            df["icu_training_load"] = df.get("tss", 0)
        df["date"] = pd.to_datetime(df["start_date_local"].astype(str).str[:10], errors="coerce", utc=False)
        df = df.dropna(subset=["date"])

        debug(context, f"[T3] 🧾 DataFrame shape: {df.shape}, columns={list(df.columns)[:8]}…")

        if df.empty:
            debug(context, "[T3] ⚠️ No valid dates found in planned events — aborting forecast.")
            return {"future_forecast": {}, "actions_future": []}

        # Aggregate training load by date
        daily_load = (
            df.groupby("date", as_index=True)["icu_training_load"]
            .sum(numeric_only=True)
            .astype(float)
            .sort_index()
        )

        # Generate continuous daily range from min to +N days
        start_date = daily_load.index.min().date()
        end_date = daily_load.index.max().date() + timedelta(days=forecast_days)
        forecast_window = pd.date_range(start=start_date, end=end_date, freq="D")

        # 🔧 Fix: ensure both are datetime64[ns] and reindex with explicit fill_value
        daily_load.index = pd.to_datetime(daily_load.index)
        load_series = daily_load.reindex(pd.to_datetime(forecast_window), fill_value=0.0)

        debug(
            context,
            f"[T3] 🧮 Load series built → {len(load_series)} days, "
            f"total_load={load_series.sum():.1f}, "
            f"range={start_date} → {end_date}"
        )

        ctl = float(context.get("wellness_summary", {}).get("ctl", 70.0))
        atl = float(context.get("wellness_summary", {}).get("atl", 65.0))
        tsb = ctl - atl

        debug(context, f"[T3] ⚙️ Initial CTL={ctl:.2f}, ATL={atl:.2f}, TSB={tsb:.2f}")

        ctl_values, atl_values, tsb_values = [], [], []

        for load in load_series:
            atl = atl + (load - atl) / 7.0
            ctl = ctl + (load - ctl) / 42.0
            tsb = ctl - atl
            ctl_values.append(ctl)
            atl_values.append(atl)
            tsb_values.append(tsb)

        debug(context, f"[T3] 📈 Computed {len(ctl_values)} projection points")
        debug(context, f"[T3] 🏁 Final CTL={ctl_values[-1]:.2f}, ATL={atl_values[-1]:.2f}, TSB={tsb_values[-1]:.2f}")

        # -----------------------------------------------------------------
        # Summarize forecast
        # -----------------------------------------------------------------
        future_state = {
            "days": forecast_days,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "CTL_future": round(float(ctl_values[-1]), 2),
            "ATL_future": round(float(atl_values[-1]), 2),
            "TSB_future": round(float(tsb_values[-1]), 2),
            "load_trend": "increasing" if ctl_values[-1] > ctl_values[0] else "declining",
            "fatigue_class": (
                "overreaching" if tsb_values[-1] < -10 else
                "fresh" if tsb_values[-1] > 5 else
                "balanced"
            ),
        }

        # Coaching actions
        actions = []
        if future_state["fatigue_class"] == "overreaching":
            actions.append({
                "priority": "high",
                "title": "Reduce intensity early next week",
                "reason": "Predicted ATL exceeds recovery capacity",
                "date_range": f"{future_state['start_date']} → {future_state['end_date']}"
            })
        elif future_state["fatigue_class"] == "fresh":
            actions.append({
                "priority": "normal",
                "title": "Consider small intensity bump",
                "reason": "Future TSB indicates low fatigue, high freshness"
            })

        # -----------------------------------------------------------------
        # Final Debug Snapshot
        # -----------------------------------------------------------------
        debug(context, "[T3] ✅ Forecast completed successfully.")
        debug(context, f"[T3] 📊 Future forecast summary:\n{json.dumps(future_state, indent=2)}")
        debug(context, f"[T3] 🧭 Generated {len(actions)} future coaching actions.")

        return {
            "future_forecast": future_state,
            "actions_future": actions
        }

    except Exception as e:
        debug(context, f"[T3] ❌ Forecast computation failed: {type(e).__name__}: {e}")
        return {"future_forecast": {}, "actions_future": []}




    # -----------------------------------------------------------------
    # 4️⃣ Summarize & classify
    # -----------------------------------------------------------------
    future_state = {
        "days": forecast_days,
        "start_date": str(forecast_window[0].date()),
        "end_date": str(forecast_window[-1].date()),
        "CTL_future": round(float(ctl_values[-1]), 2),
        "ATL_future": round(float(atl_values[-1]), 2),
        "TSB_future": round(float(tsb_values[-1]), 2),
        "load_trend": "increasing" if ctl_values[-1] > ctl_values[0] else "declining",
        "fatigue_class": (
            "overreaching" if tsb_values[-1] < -10 else
            "fresh" if tsb_values[-1] > 5 else
            "balanced"
        ),
    }

    debug(context, f"[T3] 🔍 Future load trend: {future_state['load_trend']} | Fatigue class={future_state['fatigue_class']}")

    # -----------------------------------------------------------------
    # 5️⃣ Coaching actions
    # -----------------------------------------------------------------
    actions = []
    if future_state["fatigue_class"] == "overreaching":
        actions.append({
            "priority": "high",
            "title": "Reduce intensity early next week",
            "reason": "Predicted ATL exceeds recovery capacity",
            "date_range": f"{future_state['start_date']} → {future_state['end_date']}"
        })
    elif future_state["fatigue_class"] == "fresh":
        actions.append({
            "priority": "normal",
            "title": "Consider small intensity bump",
            "reason": "Future TSB indicates low fatigue, high freshness"
        })
    elif future_state["fatigue_class"] == "balanced":
        actions.append({
            "priority": "normal",
            "title": "Maintain current plan",
            "reason": "Fatigue and freshness remain in equilibrium"
        })

    debug(context, f"[T3] ✅ Extended forecast ready → phase={future_state['fatigue_class']}")
    debug(context, f"[T3] Actions: {len(actions)} generated")

    return {
        "future_forecast": future_state,
        "actions_future": actions
    }
