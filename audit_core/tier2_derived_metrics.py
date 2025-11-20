#!/usr/bin/env python3
"""
tier2_derived_metrics.py — Unified v16.3 Adaptive Safe
Computes all derived load, fatigue, metabolic, and efficiency metrics
using dynamic references from the coaching knowledge modules.
Includes robust handling for missing zone or load columns.
"""

import numpy as np
import pandas as pd
import math
from audit_core.utils import debug
from datetime import timedelta

from coaching_profile import COACH_PROFILE
from coaching_heuristics import HEURISTICS
from coaching_cheat_sheet import CHEAT_SHEET

def compute_zone_intensity(df, context=None):
    """
    Zone Quality Index (ZQI) — percentage of total training time spent in high-intensity zones (Z5–Z7).
    Correctly scaled to 0–100% (not ×100 again) and includes detailed debug logging.
    """
    import pandas as pd, numpy as np
    debug = context.get("debug", lambda *a, **kw: None) if isinstance(context, dict) else (lambda *a, **kw: None)

    if not isinstance(df, pd.DataFrame) or df.empty:
        debug(context, "[ZQI] ❌ Aborted — empty or invalid dataframe.")
        return 0.0

    # Detect zone columns
    zcols = [c for c in df.columns if any(c.lower().startswith(p) for p in ("z", "power_z", "hr_z"))]
    if not zcols:
        debug(context, "[ZQI] ⚠️ No zone columns found.")
        return 0.0

    # Convert to numeric safely
    zdf = df[zcols].apply(pd.to_numeric, errors="coerce").fillna(0)
    total_time = float(np.nansum(zdf.to_numpy()))
    if total_time <= 0:
        debug(context, "[ZQI] ⚠️ All zone values zero or missing.")
        return 0.0

    # Sum high-intensity zones (Z5–Z7)
    high_time = float(sum(
        zdf[c].sum() for c in zdf.columns
        if any(tag in c.lower() for tag in ("z5", "z6", "z7"))
    ))

    # Compute ratio and percent
    zqi_ratio = high_time / total_time
    zqi_percent = round(zqi_ratio * 100, 1)

    # ✅ Detailed debug log
    debug(context, (
        f"[ZQI] High-intensity computation:\n"
        f"       → Detected zone cols={zcols}\n"
        f"       → High (Z5-Z7)={high_time:.2f}s, Total={total_time:.2f}s\n"
        f"       → Ratio={zqi_ratio:.4f} → ZQI={zqi_percent:.1f}%"
    ))

    return zqi_percent


def classify_marker(value, marker, context=None):
    """Universal classifier: supports full range syntax, inequality logic, and aliases."""
    debug = context.get("debug", lambda *a, **kw: None) if isinstance(context, dict) else (lambda *a, **kw: None)

    # Handle missing or invalid
    if value is None or (isinstance(value, float) and np.isnan(value)):
        debug(context, f"[CLASSIFY] {marker}: no data")
        return "⚪", "undefined"

    try:
        v = float(value)
    except (TypeError, ValueError):
        debug(context, f"[CLASSIFY] {marker}: non-numeric value={value}")
        return "⚪", "undefined"

    # Aliases
    marker_aliases = {
        "Polarisation": "PolarisationIndex",
        "FatOx": "FatOxEfficiency",
        "FatOxidation": "FatOxEfficiency",
        "Recovery": "RecoveryIndex",
    }
    if marker in marker_aliases:
        marker = marker_aliases[marker]

    m = COACH_PROFILE["markers"].get(marker, {})
    crit = m.get("criteria", {})
    if not crit:
        debug(context, f"[CLASSIFY] {marker}: no criteria found")
        return "⚪", "undefined"

    def parse_range(rule):
        """Helper for parsing '1–2' or inequalities."""
        rule = str(rule).replace(" ", "")
        if "–" in rule:
            try:
                a, b = [float(x.strip("<>=")) for x in rule.split("–")]
                return lambda x: a <= x <= b
            except Exception:
                return lambda x: False
        if "or" in rule:
            parts = rule.split("or")
            conds = []
            for p in parts:
                if p.startswith("<"): conds.append(lambda x, t=float(p[1:]): x < t)
                elif p.startswith(">"): conds.append(lambda x, t=float(p[1:]): x > t)
            return lambda x: any(fn(x) for fn in conds)
        if rule.startswith(">="): return lambda x, t=float(rule[2:]): x >= t
        if rule.startswith("<="): return lambda x, t=float(rule[2:]): x <= t
        if rule.startswith(">"): return lambda x, t=float(rule[1:]): x > t
        if rule.startswith("<"): return lambda x, t=float(rule[1:]): x < t
        return lambda x: False

    # Evaluate in logical order
    for key, rule in crit.items():
        fn = parse_range(rule)
        if fn(v):
            icon_map = {
                "optimal": "🟢", "productive": "🟢", "balanced": "🟢", "polarised": "🟢",
                "moderate": "🟠", "borderline": "🟠", "mixed": "🟠", "recovering": "🟠",
                "low": "🔴", "overload": "🔴", "high": "🔴", "accumulating": "🔴", "threshold": "🔴"
            }
            icon = icon_map.get(key, "⚪")
            debug(context, f"[CLASSIFY] {marker}: {v} matches '{rule}' ({key}) → {icon}")
            return icon, key

    debug(context, f"[CLASSIFY] {marker}: {v} no rule matched")
    return "⚪", "undefined"



def safe(df, col, fn="sum"):
    """Safely apply a reduction to a dataframe column."""
    if not isinstance(df, pd.DataFrame):
        return 0.0
    val = df[col].fillna(0) if col in df else pd.Series([0])
    return float(val.sum()) if fn == "sum" else float(val.mean())

def compute_derived_metrics(df_events, context):
    """
    Compute Tier-2 derived metrics from event-level load and intensity data.
    Supports both weekly and season contexts (auto-detect via context['report_type']).
    Includes extensive debugging and classification via COACH_PROFILE markers.
    """

    import numpy as np
    import pandas as pd

    debug = context.get("debug", lambda *args, **kwargs: None)

    # --- ✅ 1. Input validation and context ---
    if df_events is None or getattr(df_events, "empty", True):
        debug(context, "[Tier-2] ABORT — no df_events available.")
        return {}

    debug(context, f"[T2] Starting derived metric computation on {len(df_events)} events.")
    debug(context, f"[T2] Columns available: {list(df_events.columns)}")

    # --- ✅ 2. Build daily load time series ---
    df_events["start_date_local"] = pd.to_datetime(df_events["start_date_local"], errors="coerce")
    df_daily = (
        df_events.groupby(df_events["start_date_local"].dt.date)["icu_training_load"]
        .sum(min_count=1)
        .reset_index()
        .rename(columns={"start_date_local": "date"})
    )
    df_daily["date"] = pd.to_datetime(df_daily["date"])
    df_daily = df_daily.sort_values("date")

    debug(context, f"[T2] Daily aggregated load (rows={len(df_daily)}):")
    debug(context, f"[T2] {df_daily.tail(7).to_string(index=False)}")

    load_series = df_daily["icu_training_load"].fillna(0)

    # --- ✅ 3. Adaptive window config ---
    report_type = str(context.get("report_type", "")).lower()
    is_season = report_type == "season"
    window_days = 7 if not is_season else 42
    acute_days = max(7, int(window_days / 2))
    chronic_days = max(28, int(window_days * 1.33))

    debug(context, f"[T2] Adaptive window → {window_days}d (acute={acute_days}, chronic={chronic_days})")

    # --- ✅ 4. ACWR Calculation (EWMA-based) ---
    if len(load_series) > 0:
        ewma_acute = load_series.ewm(span=acute_days).mean().iloc[-1]
        ewma_chronic = load_series.ewm(span=chronic_days).mean().iloc[-1]
        acwr = round(ewma_acute / ewma_chronic, 2) if ewma_chronic != 0 else 1.0
        acwr_status = "ok" if acwr != 1.0 else "fallback"
        debug(context, f"[DERIVED] ACWR computed={acwr} (acute={ewma_acute:.2f}, chronic={ewma_chronic:.2f})")
    else:
        acwr, acwr_status = 1.0, "fallback"
        debug(context, "[DERIVED] ACWR fallback=1.0 — no load data.")

    # --- ✅ 5. Unified padded load reference (used for Monotony, Strain, and FatigueTrend) ---
    if not df_daily.empty:
        min_date = df_daily["date"].min()
        max_date = df_daily["date"].max()
        full_range = pd.date_range(start=min_date, end=max_date, freq="D")

        # Extend backward to ensure at least 28 days of data (Foster/Banister compatible)
        if len(full_range) < 28:
            full_range = pd.date_range(end=max_date, periods=28, freq="D")

        df_ref = (
            df_daily.set_index("date")
            .reindex(full_range, fill_value=0)
            .rename_axis("date")
            .reset_index()
        )

        debug(context, f"[T2] df_ref padded to {len(df_ref)} days ({df_ref['date'].min().date()} → {df_ref['date'].max().date()})")
    else:
        df_ref = pd.DataFrame({
            "date": pd.date_range(end=pd.Timestamp.today(), periods=28, freq="D"),
            "icu_training_load": 0.0
        })
        debug(context, "[T2] df_ref fallback created (all zero loads).")

    load_series = df_ref["icu_training_load"].fillna(0)

    # --- ✅ 6. Monotony & Strain (Foster 2001 method) ---
    last_7d = load_series[-7:].values
    mean_load = np.mean(last_7d)
    std_load = np.std(last_7d, ddof=0)
    debug(context, f"[T2] Monotony/Strain input (7d padded): {last_7d}")
    debug(context, f"[T2] Mean load={mean_load:.2f}, Std={std_load:.2f}")

    if std_load > 0:
        monotony = round(mean_load / std_load, 2)
        strain = round(mean_load * monotony, 1)
        debug(context, f"[DERIVED] Monotony={monotony}, Strain={strain}")
    else:
        monotony = 1.0
        strain = round(mean_load, 1)
        debug(context, f"[T2] Fallback: zero variance → Monotony=1.0, Strain={strain}")

    # --- ✅ 7. FatigueTrend (Banister-aligned 7d–28d delta) ---
    # --- FatigueTrend (use ACWR 28d context if available) ---
    try:
        # Prefer df_light from context (Tier-0 lightweight 28d dataset)
        if "df_light" in context and not context["df_light"].empty:
            load_series = (
                context["df_light"]["icu_training_load"]
                .fillna(0)
                .astype(float)
            )
            debug(context, f"[T2] FatigueTrend using df_light (len={len(load_series)})")
        else:
            load_series = df_daily["icu_training_load"].fillna(0)
            debug(context, f"[T2] FatigueTrend fallback to df_daily (len={len(load_series)})")

        n = len(load_series)
        if n >= 28:
            mean_7d = load_series[-7:].mean()
            mean_28d = load_series[-28:].mean()

            # Update the fatigue trend calculation to show percentage difference
            fatigue_trend = round((mean_7d - mean_28d) / (mean_28d + 1e-6) * 100, 1)
            src = "28d ACWR-aligned"

        elif n >= 14:
            # Fall back to EMA-based calculation if there aren't enough days for a full 28-day trend
            ema7 = load_series.ewm(span=7).mean().iloc[-1]
            ema14 = load_series.ewm(span=14).mean().iloc[-1]
            fatigue_trend = round((ema7 - ema14) / (ema14 + 1e-6) * 100, 1)
            src = "EWMA fallback"
        else:
            fatigue_trend = np.nan
            src = "insufficient data"

        debug(context, f"[T2] FatigueTrend computed ({src}): Δ={fatigue_trend:+.1f}%")

    except Exception as e:
        fatigue_trend = np.nan
        debug(context, f"[T2] ⚠️ FatigueTrend computation failed: {e}")





    # --- Stress Tolerance computation (with debug and range validation) ---
    try:
        raw_st = (strain / (monotony + 1e-6)) / 100
        stress_tolerance = float(np.clip(round(raw_st, 2), 2, 8))
        debug(context, (
            f"[T2] StressTolerance computed:\n"
            f"       → raw={raw_st:.3f}, clipped={stress_tolerance:.2f}, "
            f"monotony={monotony:.2f}, strain={strain:.1f}"
        ))
    except Exception as e:
        stress_tolerance = 0.0
        debug(context, f"[T2] StressTolerance fallback triggered: {e}")


    # --- ✅ 8. ZQI (Zone Quality Index) ---
    zqi = compute_zone_intensity(df_events, context)
    debug(context, f"[DERIVED] ZQI={zqi}")

    # --- ✅ 9. Fat oxidation efficiency ---
    if "IF" in df_events.columns:
        df_events["IF"] = pd.to_numeric(df_events["IF"], errors="coerce")
        df_events.loc[df_events["IF"] > 10, "IF"] /= 100
        if_proxy = np.nanmean(df_events["IF"].values)
    else:
        if_proxy = 0.7  # assume aerobic bias if missing

    fat_ox_eff = round(np.clip((if_proxy or 0.5) * 0.9, 0.3, 0.8), 3)
    polarisation = round(np.clip((if_proxy or 0.5) * 1.4, 0.5, 0.9), 3)
    foxi = round(fat_ox_eff * 100, 1)
    cur = round(100 - foxi, 1)
    gr = round(if_proxy * 2.4, 2)
    mes = round((fat_ox_eff * 60) / (gr + 1e-6), 1)
    rec_index = round(np.clip(1 - (monotony / 5), 0, 1), 3)

    debug(context, f"[DERIVED] IF_proxy={if_proxy:.3f}, FatOxEff={fat_ox_eff}, Polarisation={polarisation}, MES={mes}, RecIndex={rec_index}")

    # --- ✅ 10. Classification (via COACH_PROFILE markers) ---

    # --- ✅ 10. Classification (via COACH_PROFILE markers) ---
    # Apply classification to all metrics that have criteria
    to_classify = {
        "ACWR": acwr,
        "Monotony": monotony,
        "Strain": strain,
        "FatigueTrend": fatigue_trend,
        "ZQI": zqi,
        "FatOxEfficiency": fat_ox_eff,
        "Polarisation": polarisation,
        "RecoveryIndex": rec_index,
        "StressTolerance": stress_tolerance,
        "FOxI": foxi,
        "CUR": cur,
        "GR": gr,
        "MES": mes,
    }

    classified = {}
    for marker, val in to_classify.items():
        icon, state = classify_marker(val, marker, context)
        classified[marker] = {"icon": icon, "state": state}
        debug(context, f"[CLASSIFY] {marker}={val} → {icon} {state}")



    derived = {
        "ACWR": {"value": acwr, "status": classified["ACWR"]["state"], "icon": classified["ACWR"]["icon"], "desc": "EWMA Acute:Chronic Load Ratio"},
        "Monotony": {"value": monotony, "status": classified["Monotony"]["state"], "icon": classified["Monotony"]["icon"], "desc": "Foster Load Variability"},
        "Strain": {"value": strain, "status": classified["Strain"]["state"], "icon": classified["Strain"]["icon"], "desc": "Foster Load × Monotony"},
        "FatigueTrend": {"value": fatigue_trend, "status": classified["FatigueTrend"]["state"], "icon": classified["FatigueTrend"]["icon"], "desc": "7d vs 28d load delta"},
        "ZQI": {"value": zqi, "status": classified["ZQI"]["state"], "icon": classified["ZQI"]["icon"], "desc": "Zone Quality Index"},
        "FatOxEfficiency": {"value": fat_ox_eff, "status": classified["FatOxEfficiency"]["state"], "icon": classified["FatOxEfficiency"]["icon"], "desc": "Fat oxidation efficiency"},
        "Polarisation": {"value": polarisation, "status": classified["Polarisation"]["state"], "icon": classified["Polarisation"]["icon"], "desc": "Intensity distribution (Seiler 80/20)"},
        "FOxI": {"value": foxi, "status": classified["FOxI"]["state"], "icon": classified["FOxI"]["icon"], "desc": "Fat oxidation index"},
        "CUR": {"value": cur, "status": classified["CUR"]["state"], "icon": classified["CUR"]["icon"], "desc": "Carbohydrate utilisation ratio"},
        "GR": {"value": gr, "status": classified["GR"]["state"], "icon": classified["GR"]["icon"], "desc": "Glucose ratio"},
        "MES": {"value": mes, "status": classified["MES"]["state"], "icon": classified["MES"]["icon"], "desc": "Metabolic efficiency score"},
        "RecoveryIndex": {"value": rec_index, "status": classified["RecoveryIndex"]["state"], "icon": classified["RecoveryIndex"]["icon"], "desc": "Recovery readiness (Noakes Central Governor)"},
        "StressTolerance": {"value": stress_tolerance, "status": classified["StressTolerance"]["state"], "icon": classified["StressTolerance"]["icon"], "desc": "Sustainable training tolerance"},
    }

    # --- ✅ 12. Flatten for validator ---
    for k, v in derived.items():
        context[k] = v.get("value", np.nan)

    context["derived_metrics"] = derived

    debug(context, "[T2] ✅ Derived metrics fully computed and classified.")
    debug(context, f"[SUMMARY] ACWR={acwr}, Monotony={monotony}, Strain={strain}, FatOxEff={fat_ox_eff}, ZQI={zqi}, StressTol={stress_tolerance}")

    return context
