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
from audit_core.utils import debug  # ✅ Use shared debug utility

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

    debug(context, "───────────────────────────────────────────────")
    debug(context, f"[T3] 🧭 Starting Future Forecast (window={forecast_days}d)")
    debug(context, f"[T3] Context keys: {list(context.keys())[:12]}")
    debug(context, f"[T3] Prefetched calendar present: {'calendar' in context and isinstance(context.get('calendar'), list)}")

    # -----------------------------------------------------------------
    # 1️⃣ Acquire planned events (prefetched → local → skip external fetch)
    # -----------------------------------------------------------------
    planned = None

    # ✅ 1. Try Cloudflare-prefetched payload first (nested)
    pre = context.get("prefetched", {})
    if isinstance(pre, dict) and isinstance(pre.get("calendar"), list) and len(pre["calendar"]) > 0:
        planned = pre["calendar"]
        debug(context, f"[T3] 🧩 Using Cloudflare-prefetched calendar ({len(planned)} events)")

    # ✅ 2. If not found, try top-level (for local or fallback-injected)
    if not planned and isinstance(context.get("calendar"), list) and len(context["calendar"]) > 0:
        planned = context["calendar"]
        debug(context, f"[T3] 🧩 Using local context calendar ({len(planned)} events)")

    # ✅ 3. If neither available, only fetch in local mode
    if not planned:
        if "prefetched" in context:
            debug(context, "[T3] 🚫 Skipping external fetch (prefetched Railway mode detected)")
            planned = []
        else:
            debug(context, "[T3] ⚙️ No prefetched calendar found — using fallback Cloudflare fetch.")
            planned = fetch_calendar_fallback(context, days=forecast_days, owner=context.get("owner", "intervals"))

    # -----------------------------------------------------------------
    # 2️⃣ Safety check
    # -----------------------------------------------------------------
    if not planned or not isinstance(planned, list) or len(planned) == 0:
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
