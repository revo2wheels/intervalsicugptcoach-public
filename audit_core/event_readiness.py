from datetime import timedelta
import math
import pandas as pd

from audit_core.utils import debug


def estimate_event_ctl_atl_from_calendar_ewma(context, event_date):
    """
    Estimate target-event SUNRISE CTL / ATL using calendar-derived daily EWMA.

    Rules:
    - Event readiness must use SUNRISE state, not Intervals race-day sunset state.
    - Seed from the latest valid calendar CTL/ATL row strictly BEFORE the event date.
    - Skip rows before today: today's state already holds the past, and a
      missed plan's stored values include load that was never ridden.
    - If no seeded calendar physiology exists, fall back to current authoritative CTL/ATL.
    - Apply planned load on intervening days only.
    - Do NOT apply target event day load.
    - Advance one final zero-load EWMA step into event-day sunrise.

    Daily EWMA, as Intervals works it out:
        CTL = CTL × e^(−1/42) + load × (1 − e^(−1/42))
        ATL = ATL × e^(−1/7) + load × (1 − e^(−1/7))
    """

    calendar = context.get("calendar") or []

    try:
        target_day = pd.to_datetime(event_date).date()
    except Exception:
        return {"ctl": None, "atl": None}

    try:
        today_day = pd.to_datetime(context.get("athlete_today")).date()
    except Exception:
        today_day = None

    rows = []

    for ev in calendar:
        if not isinstance(ev, dict):
            continue

        date_raw = ev.get("start_date_local") or ev.get("date")
        if not date_raw:
            continue

        try:
            day = pd.to_datetime(str(date_raw)[:10], errors="coerce").date()
        except Exception:
            continue

        # Rows after the target event cannot affect its sunrise state
        if day >= target_day:
            continue

        # Rows before today never count: today's state (context ctl/atl)
        # already holds every ride up to last night. A missed plan keeps
        # Intervals' stored CTL/ATL with its planned load in, and rides
        # done without a plan are not on the calendar at all
        if today_day is not None and day < today_day:
            continue

        ctl = pd.to_numeric(ev.get("icu_ctl"), errors="coerce")
        atl = pd.to_numeric(ev.get("icu_atl"), errors="coerce")

        load = pd.to_numeric(
            ev.get("icu_training_load")
            if ev.get("icu_training_load") is not None
            else ev.get("tss"),
            errors="coerce"
        )

        rows.append({
            "date": day,
            "ctl": None if pd.isna(ctl) else float(ctl),
            "atl": None if pd.isna(atl) else float(atl),
            "load": 0.0 if pd.isna(load) else float(load),
        })

    df = pd.DataFrame(rows).sort_values("date") if rows else pd.DataFrame(
        columns=["date", "ctl", "atl", "load"]
    )

    # ---------------------------------------------------------
    # 1. Resolve seed:
    #    latest Intervals calendar CTL/ATL strictly before event
    # ---------------------------------------------------------
    state_rows = df[
        df["ctl"].notna() &
        df["atl"].notna()
    ].copy()

    if not state_rows.empty:
        seed = state_rows.sort_values("date").iloc[-1]

        seed_day = seed["date"]
        ctl = float(seed["ctl"])
        atl = float(seed["atl"])

        debug(
            context,
            f"[EVENT-SUNRISE] Calendar seed → "
            f"event={target_day} seed_day={seed_day} "
            f"ctl={ctl:.2f} atl={atl:.2f}"
        )

    else:
        ctl = (
            context.get("ctl")
            or ((context.get("wellness_summary") or {}).get("ctl"))
        )

        atl = (
            context.get("atl")
            or ((context.get("wellness_summary") or {}).get("atl"))
        )

        try:
            ctl = float(ctl)
            atl = float(atl)
        except Exception:
            debug(
                context,
                f"[EVENT-SUNRISE] No usable CTL/ATL seed for event={target_day}"
            )
            return {"ctl": None, "atl": None}

        today_raw = context.get("athlete_today")
        if today_raw is None:
            return {"ctl": None, "atl": None}

        try:
            seed_day = pd.to_datetime(today_raw).date()
        except Exception:
            return {"ctl": None, "atl": None}

        debug(
            context,
            f"[EVENT-SUNRISE] Current-state fallback seed → "
            f"event={target_day} seed_day={seed_day} "
            f"ctl={ctl:.2f} atl={atl:.2f}"
        )

    # ---------------------------------------------------------
    # 2. Aggregate planned load AFTER seed and BEFORE event
    # ---------------------------------------------------------
    if not df.empty:
        load_by_day = (
            df[
                (df["date"] > seed_day) &
                (df["date"] < target_day)
            ]
            .groupby("date", as_index=True)["load"]
            .sum()
            .to_dict()
        )
    else:
        load_by_day = {}

    # ---------------------------------------------------------
    # 3. Walk from seed sunset → event-day sunrise
    # ---------------------------------------------------------
    current_day = seed_day

    while current_day < target_day:
        current_day = current_day + timedelta(days=1)

        daily_load = (
            0.0
            if current_day == target_day
            else float(load_by_day.get(current_day, 0.0))
        )

        ctl = ctl * math.exp(-1.0 / 42.0) + daily_load * (1.0 - math.exp(-1.0 / 42.0))
        atl = atl * math.exp(-1.0 / 7.0) + daily_load * (1.0 - math.exp(-1.0 / 7.0))

    debug(
        context,
        f"[EVENT-SUNRISE] Result → "
        f"event={target_day} ctl={ctl:.2f} atl={atl:.2f}"
    )

    return {
        "ctl": round(ctl, 2),
        "atl": round(atl, 2),
    }