#!/usr/bin/env python3
"""
tier2_derived_metrics.py — Unified v16.3 Adaptive Safe
Computes all derived load, fatigue, metabolic, and efficiency metrics
using dynamic references from the coaching knowledge modules.
Includes robust handling for missing zone or load columns.
"""

import numpy as np
import pandas as pd
from audit_core.utils import debug

from coaching_profile import COACH_PROFILE
from coaching_heuristics import HEURISTICS
from coaching_cheat_sheet import CHEAT_SHEET, CLASSIFICATION_ALIASES

def normalise_hrv(df_well, context=None):
    """
    Tier-2 HRV Normalisation — vendor-agnostic harmonisation across Garmin, Whoop, Oura, etc.
    """
    if df_well is None or getattr(df_well, "empty", True):
        return None

    import pandas as pd, numpy as np

    # --- Find plausible HRV columns ---
    hrv_candidates = [
        c for c in df_well.columns
        if any(k in c.lower() for k in [
            "hrv", "rmssd", "recovery_score", "recovery_index",
            "oura", "whoop", "fitbit", "polar",
            "hrv_mean", "hrv_rmssd", "daily_hrv", "hrv_status", "hrvsdnn"
        ])
    ]
    debug(context, f"[T2-HRV] HRV candidates detected: {hrv_candidates}")

    if not hrv_candidates:
        context["hrv_available"] = False
        context["hrv_source"] = "none"
        return df_well

    if "hrv" not in df_well.columns:
        df_well["hrv"] = np.nan

    # --- Iterate through candidate columns ---
    for col in hrv_candidates:
        try:
            col_lower = col.lower()
            raw_vals = df_well[col]
            if not pd.api.types.is_numeric_dtype(raw_vals):
                val = pd.to_numeric(
                    raw_vals.astype(str).str.extract(r"([-+]?\d*\.?\d+)")[0],
                    errors="coerce"
                )
            else:
                val = raw_vals

            # --- Vendor-specific classification ---
            if "whoop" in col_lower and "recovery_score" in col_lower:
                val *= 1.2
                src = "whoop"
            elif any(k in col_lower for k in ["oura", "apple", "fitbit"]):
                src = "oura/apple/fitbit"
            elif "polar" in col_lower:
                src = "polar"
            elif any(k in col_lower for k in ["garmin", "hrv_mean", "hrvsdnn"]) or col_lower == "hrv":
                src = "garmin"
            else:
                src = "generic"

            # --- Assign only once ---
            if df_well["hrv"].isna().all() and val.notna().any():
                df_well["hrv"] = val
                context["hrv_source"] = src
                debug(context, f"[T2-HRV] Using HRV from '{col}' (source={src})")

        except Exception as e:
            debug(context, f"[T2-HRV] HRV normalisation failed for {col}: {e}")

    # --- Final safety check for Garmin default ---
    if df_well["hrv"].notna().any() and not context.get("hrv_source"):
        context["hrv_source"] = "garmin"
        debug(context, "[T2-HRV] Defaulted HRV source to Garmin (detected native HRV data).")

    # --- Preserve known source; do not overwrite ---
    if not context.get("hrv_source"):
        context["hrv_source"] = "unknown"

    df_well["hrv"] = pd.to_numeric(df_well["hrv"], errors="coerce")
    context["hrv_available"] = bool(df_well["hrv"].notna().any())
    context["df_wellness"] = df_well

    debug(context, (
        f"[T2-HRV] Normalised HRV column ready "
        f"(source={context['hrv_source']}, available={context['hrv_available']}, "
        f"non-null={df_well['hrv'].notna().sum()})"
    ))

    return df_well

# =========================================================
# 📊 WELLNESS COVERAGE METRICS (v16.18)
# =========================================================
def compute_wellness_coverage(df_well, context=None):
    """
    Compute % coverage of key wellness signals across window.
    Safe against missing columns.
    """

    if df_well is None or getattr(df_well, "empty", True):
        return {
            "hrv_pct": 0.0,
            "resting_hr_pct": 0.0,
            "sleep_pct": 0.0,
            "subjective_pct": 0.0,
            "total_days": 0,
        }

    df = df_well.copy()
    total_days = len(df)

    def pct(col):
        if col not in df.columns:
            return 0.0
        return round(float(df[col].notna().mean()), 3)

    subjective_cols = [c for c in ["mood", "fatigue", "stress", "motivation"] if c in df.columns]

    subjective_pct = 0.0
    if subjective_cols:
        subjective_pct = round(
            float(df[subjective_cols].notna().any(axis=1).mean()),
            3
        )

    def pct_multi(*cols):
        for col in cols:
            if col in df.columns:
                return round(float(df[col].notna().mean()), 3)
        return 0.0

    coverage = {
        "unit": "proportion",
        "hrv_pct": pct_multi("hrv"),
        "resting_hr_pct": pct_multi("restingHR", "resting_hr", "rest_hr"),
        "sleep_pct": pct_multi("sleepsecs", "sleep_secs", "sleep_seconds"),
        "subjective_pct": subjective_pct,
        "total_days": total_days,
    }


    if context is not None:
        context["wellness_coverage"] = coverage

    return coverage


def compute_zone_intensity(df, context=None):
    """
    Sieler aligned Zone Quality Index (ZQI) — percentage of total training time spent in high-intensity zones (Z4–Z7).
    Correctly scaled to 0–100% (not ×100 again) and includes detailed debug logging.
    """
    import pandas as pd, numpy as np

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

    # Sum high-intensity zones (Z4–Z7)
    high_time = float(sum(
        zdf[c].sum() for c in zdf.columns
        if any(tag in c.lower() for tag in ("z4", "z5", "z6", "z7"))
    ))

    # Compute ratio and percent
    zqi_ratio = high_time / total_time
    zqi_percent = round(zqi_ratio * 100, 1)

    # ✅ Detailed debug log
    debug(context, (
        f"[ZQI] High-intensity computation:\n"
        f"       → Detected zone cols={zcols}\n"
        f"       → High (Z4-Z7)={high_time:.2f}s, Total={total_time:.2f}s\n"
        f"       → Ratio={zqi_ratio:.4f} → ZQI={zqi_percent:.1f}%"
    ))

    return zqi_percent

def compute_polarisation_index(context):
    debug_fn = context.get("debug", lambda *a, **kw: None)

    zones = context.get("zone_dist_power") or {}
    src = "power"
    if not zones:
        zones = context.get("zone_dist_hr") or {}
        src = "hr"

    if zones:
        try:
            def get_zone(z):
                return float(
                    zones.get(f"power_{z}",
                    zones.get(f"hr_{z}",
                    zones.get(z, 0.0)))
                )

            z1, z2, z3 = get_zone("z1"), get_zone("z2"), get_zone("z3")

            denom = z1 + z2 + z3
            if denom > 0:
                pol = round((z1 + z2) / denom, 3)
                debug_fn(context, f"[POL] ({src}) Z1={z1:.1f} Z2={z2:.1f} Z3={z3:.1f} "
                                  f"→ PI={(z1 + z2):.1f}/{denom:.1f} = {pol:.3f}")
                return pol
            else:
                debug_fn(context, f"[POL] ({src}) Z1–Z3 sum=0 → fallback")

        except Exception as e:
            debug_fn(context, f"[POL] ({src}) zone PI computation failed → fallback ({e})")


    # =========================================================
    # 2️⃣ Fallback — IF proxy (weighted by moving_time)
    # =========================================================
    df = context.get("df_events")
    if df is None or getattr(df, "empty", True):
        debug_fn(context, "[POL] ⚠ No df_events for icu_intensity fallback → 0.0")
        return 0.0

    if "icu_intensity" not in df.columns or "moving_time" not in df.columns:
        debug_fn(context, "[POL] ⚠ Missing icu_intensity or moving_time → 0.0")
        return 0.0

    try:
        tmp = df[["icu_intensity", "moving_time"]].copy()
        tmp["icu_intensity"] = pd.to_numeric(tmp["icu_intensity"], errors="coerce")
        tmp["moving_time"] = pd.to_numeric(tmp["moving_time"], errors="coerce").fillna(0)
        tmp = tmp.dropna(subset=["icu_intensity"])
        tmp = tmp[tmp["moving_time"] > 0]
        if tmp.empty:
            debug_fn(context, "[POL] ⚠ icu_intensity fallback has no valid rows → 0.0")
            return 0.0

        tmp.loc[tmp["icu_intensity"] > 10, "icu_intensity"] /= 100.0
        total_time = float(tmp["moving_time"].sum())
        if total_time <= 0:
            return 0.0

        low_time = float(tmp.loc[tmp["icu_intensity"] < 0.85, "moving_time"].sum())
        pol = round(low_time / total_time, 3)
        debug_fn(context, f"[POL] (icu_intensity-fallback) low_time={low_time:.1f}s total={total_time:.1f}s → PI={pol}")
        return pol

    except Exception as e:
        debug_fn(context, f"[POL] ⚠ icu_intensity fallback failed ({e}) → 0.0")
        return 0.0


def classify_marker(value, marker, context=None):
    """Universal classifier: supports range syntax, inequalities, and aliases."""

    if value is None or (isinstance(value, float) and np.isnan(value)):
        debug(context, f"[CLASSIFY] {marker}: no data")
        return "⚪", "undefined"

    try:
        v = float(value)
    except (TypeError, ValueError):
        debug(context, f"[CLASSIFY] {marker}: non-numeric value={value}")
        return "⚪", "undefined"

    # Canonical marker aliases
    marker_aliases = {
        "FatOx": "FatOxEfficiency",
        "FatOxidation": "FatOxEfficiency",
        #"Recovery": "LoadVariabilityIndex",
        "fatigue_trend": "FatigueTrend",
        "FatigueTrend": "FatigueTrend"
    }
    marker = marker_aliases.get(marker, marker)

    # Skip multi-dimensional markers (handled elsewhere)
    MULTI_DIMENSIONAL = {"Polarisation", "PolarisationIndex"}
    if marker in MULTI_DIMENSIONAL:
        debug(context, f"[CLASSIFY] {marker}: skipped (multi-dimensional metric)")
        return "—", "computed"

    # Load criteria from profile (single source of truth)
    marker_def = COACH_PROFILE.get("markers", {}).get(marker, {})
    criteria = marker_def.get("criteria")

    if not criteria:
        debug(context, f"[CLASSIFY] {marker}: no criteria defined")
        return "⚪", "undefined"

    # -------------------------
    # Rule parsing
    # -------------------------
    def parse_rule(rule):
        rule = str(rule).replace(" ", "")
        if "–" in rule:
            lo, hi = map(float, rule.split("–"))
            return lambda x: lo <= x <= hi
        if "or" in rule:
            funcs = [parse_rule(p) for p in rule.split("or")]
            return lambda x: any(f(x) for f in funcs)
        if rule.startswith(">="): return lambda x: x >= float(rule[2:])
        if rule.startswith("<="): return lambda x: x <= float(rule[2:])
        if rule.startswith(">"):  return lambda x: x > float(rule[1:])
        if rule.startswith("<"):  return lambda x: x < float(rule[1:])
        return lambda x: False

    # -------------------------
    # Evaluation
    # -------------------------
    matched_state = None

    for state_label, rule in criteria.items():
        if parse_rule(rule)(v):
            matched_state = state_label
            break

    if matched_state is None:
        debug(context, f"[CLASSIFY] {marker}: {v} no rule matched")
        return "⚪", "undefined"

    # -------------------------
    # Canonical state mapping
    # -------------------------
    canonical_state = CLASSIFICATION_ALIASES.get(
        matched_state.lower(),
        matched_state.lower()
    )

    icon_map = {
        "green": "🟢",
        "amber": "🟠",
        "red": "🔴",
    }

    icon = icon_map.get(canonical_state, "⚪")

    debug(context, f"[CLASSIFY] {marker}: {v} → {matched_state} → {canonical_state}")

    return icon, canonical_state


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

    debug(context, f"[T2-VERIFY-IN] df_events type={type(df_events)} len={(len(df_events) if hasattr(df_events, '__len__') else 'n/a')}")

    if hasattr(df_events, "columns"):
        debug(context, f"[T2-VERIFY-IN] df_events cols={list(df_events.columns)[:10]}")


    # --- ✅ 1. Input validation and context ---
    if df_events is None or getattr(df_events, "empty", True):
        debug(context, "[Tier-2] ABORT — no df_events available.")
        return {}

    debug(context, f"[T2] Starting derived metric computation on {len(df_events)} events.")
    debug(context, f"[T2] Columns available: {list(df_events.columns)}")

    # ✅ Prefer full dataset if available
    if "_df_scope_full" in context and isinstance(context["_df_scope_full"], pd.DataFrame):
        debug(context, f"[DERIVED] Using _df_scope_full (rows={len(context['_df_scope_full'])}, cols={len(context['_df_scope_full'].columns)})")
        df_events = context["_df_scope_full"].copy()

    # --- 🩵 HRV Normalisation (Tier-2 context enrichment) ---
    df_well = context.get("df_wellness")
    if df_well is not None:
        df_well = normalise_hrv(df_well, context)
    else:
        debug(context, "[T2-HRV] No wellness dataframe in context — skipping HRV normalisation.")
    # --- 📊 Wellness Coverage ---
    if df_well is not None:
        compute_wellness_coverage(df_well, context)
    else:
        context["wellness_coverage"] = None

    # ---------------------------------------------------------
    # 🩵 HRV value extraction only (no classification here)
    # ---------------------------------------------------------
    hrv_val = None

    try:
        if df_well is not None and "hrv" in df_well.columns:
            series = pd.to_numeric(df_well["hrv"], errors="coerce").dropna()
            if not series.empty:
                hrv_val = float(series.iloc[-1])  # latest HRV
    except Exception as e:
        debug(context, f"[T2-HRV] Failed to extract HRV value: {e}")

    context["HRV"] = hrv_val
    debug(context, f"[T2-HRV] HRV extracted → {hrv_val}")

    # --- ✅ 2. Build daily load time series ---
    # FIX: convert millis → proper datetime
    df_events["start_date_local"] = pd.to_datetime(
        df_events["start_date_local"], unit="ms", origin="unix", errors="coerce"
    )
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

    # FIX: store df_daily for CTL/ATL/TSB and semantic builder
    context["df_daily"] = df_daily
    debug(context, f"[T2] df_daily stored in context ({len(df_daily)} rows)")

    load_series = df_daily["icu_training_load"].fillna(0)

    # --- ✅ 3. Adaptive window config ---
    report_type = str(context.get("report_type", "")).lower()
    is_season = report_type == "season"
    window_days = 7 if not is_season else 42
    acute_days = max(7, int(window_days / 2))
    chronic_days = max(28, int(window_days * 1.33))

    debug(context, f"[T2] Adaptive window → {window_days}d (acute={acute_days}, chronic={chronic_days})")

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
            "date": pd.date_range(end=context["athlete_today"], periods=28, freq="D"),
            "icu_training_load": 0.0
        })
        debug(context, "[T2] df_ref fallback created (all zero loads).")

    # --- ✅ ACWR Calculation (EWMA-based, corrected + safe) ---

    # Decide source series (do NOT reuse later for other metrics)
    if len(df_daily) < 14:
        acwr_series = df_daily["icu_training_load"].fillna(0)
        debug(context, "[ACWR] Using df_daily (insufficient history)")
    else:
        acwr_series = df_ref["icu_training_load"].fillna(0)
        debug(context, "[ACWR] Using df_ref (padded time-series)")

    # Compute
    if len(acwr_series) > 0:
        ewma_acute = acwr_series.ewm(span=acute_days).mean().iloc[-1]
        ewma_chronic = acwr_series.ewm(span=chronic_days).mean().iloc[-1]

        acwr = round(ewma_acute / ewma_chronic, 2) if ewma_chronic != 0 else 1.0
        acwr_status = "ok" if acwr != 1.0 else "fallback"

        # store windows for downstream (fixes your 7/28 vs 21/55 issue)
        context["acwr_windows"] = {
            "acute_days": acute_days,
            "chronic_days": chronic_days
        }

        debug(context,
            f"[DERIVED] ACWR computed={acwr} "
            f"(acute={ewma_acute:.2f}, chronic={ewma_chronic:.2f}, "
            f"window={acute_days}/{chronic_days})"
        )

    else:
        acwr, acwr_status = 1.0, "fallback"
        context["acwr_windows"] = {
            "acute_days": acute_days,
            "chronic_days": chronic_days
        }
        debug(context, "[DERIVED] ACWR fallback=1.0 — no load data.")

    # --- ✅ 6. Monotony & Strain (Foster 2001 method) ---

    last_7d = df_ref["icu_training_load"].fillna(0).tail(7).astype(float).values

    mean_load = np.mean(last_7d)
    std_load = np.std(last_7d, ddof=1)

    debug(context, f"[T2] Monotony/Strain input (7d padded): {last_7d}")
    debug(context, f"[T2] Mean load={mean_load:.2f}, Std={std_load:.2f}")

    if std_load > 0:
        monotony = round(mean_load / std_load, 2)
        weekly_load = float(np.sum(last_7d))
        strain = round(weekly_load * monotony, 1)

        debug(context, f"[DERIVED] Monotony={monotony}, Strain={strain}")

    else:
        monotony = 1.0
        weekly_load = float(np.sum(last_7d))
        strain = round(weekly_load, 1)

        debug(context, f"[T2] Fallback: zero variance → Monotony=1.0, Strain={strain}")
        
    # --- ✅ 7. FatigueTrend (90d light daily: recent 7d vs prior 21d) ---
    try:
        trend_df = context.get("df_light")

        if isinstance(trend_df, pd.DataFrame) and not trend_df.empty:
            dft = trend_df.copy()

            dft["date"] = pd.to_datetime(
                dft["start_date_local"],
                errors="coerce",
                unit="ms" if pd.api.types.is_numeric_dtype(dft["start_date_local"]) else None
            ).dt.tz_localize(None).dt.normalize()

            dft["icu_training_load"] = pd.to_numeric(
                dft["icu_training_load"],
                errors="coerce"
            ).fillna(0)

            daily = (
                dft.dropna(subset=["date"])
                .groupby("date")["icu_training_load"]
                .sum()
                .sort_index()
            )

            full_range = pd.date_range(daily.index.min(), daily.index.max(), freq="D")
            load_series = daily.reindex(full_range, fill_value=0).astype(float)

            src_base = "df_light"
        else:
            load_series = df_ref.set_index("date")["icu_training_load"].fillna(0).astype(float)
            src_base = "df_ref_fallback"

        if len(load_series) >= 28:
            recent_7d = load_series.tail(7)
            prior_21d = load_series.tail(28).head(21)

            recent_mean = recent_7d.mean()
            baseline_mean = prior_21d.mean()

            fatigue_trend = (
                round(((recent_mean - baseline_mean) / baseline_mean) * 100, 1)
                if baseline_mean > 0 else None
            )

            src = f"{src_base}_recent7_vs_prior21"
        else:
            fatigue_trend = None
            src = f"{src_base}_insufficient"

        debug(
            context,
            f"[T2] FatigueTrend ({src}) → "
            f"days={len(load_series)}, "
            f"recent7_sum={recent_7d.sum() if 'recent_7d' in locals() else None}, "
            f"prior21_sum={prior_21d.sum() if 'prior_21d' in locals() else None}, "
            f"value={fatigue_trend}"
        )

    except Exception as e:
        fatigue_trend = None
        debug(context, f"[T2] ⚠️ FatigueTrend failed: {e}")


    # --- Stress Tolerance computation (Capacity-adjusted weekly load) ---
    try:
        weekly_tss = float(np.sum(last_7d))

        ctl = (
            context.get("ctl")
            or context.get("load_metrics", {}).get("CTL", {}).get("value")
            or context.get("wellness_summary", {}).get("ctl")
            or 0
        )

        if ctl and ctl > 10:
            stress_tolerance = round(weekly_tss / (ctl * 7), 2)
        else:
            stress_tolerance = 0.0

        debug(context, (
            f"[T2] StressTolerance computed:\n"
            f"       → weekly_tss={weekly_tss:.1f}, "
            f"CTL={ctl}, "
            f"stress_tolerance={stress_tolerance}"
        ))

    except Exception as e:
        stress_tolerance = None
        debug(context, f"[T2] StressTolerance fallback triggered: {e}")

    # ======================================================
    # 🩵 HR→Power Equivalence Normalization (optional scaling)
    # ======================================================
    if "power_proxy" in context or (any("hr_z" in c.lower() for c in df_events.columns) and not any("power_z" in c.lower() for c in df_events.columns)):
        context.setdefault("power_proxy", True)
        context.setdefault("hr_power_equiv_factor", 0.93)
        factor = context["hr_power_equiv_factor"]

        hr_zone_cols = [c for c in df_events.columns if c.lower().startswith("hr_z")]
        if hr_zone_cols:
            df_events.loc[:, hr_zone_cols] = df_events[hr_zone_cols].apply(lambda col: col * factor)
            debug(context, f"[T2] ⚙️ Applied HR→Power scaling ×{factor} to HR zones ({len(hr_zone_cols)} cols)")

    # --------------------------------------------------
    # 🔧 Ensure fused zone columns exist (Tier-1 parity)
    # --------------------------------------------------
    for c in df_events.columns:
        if c.startswith("power_z") and f"_fused_{c}" not in df_events.columns:
            df_events[f"_fused_{c}"] = df_events[c]

        if c.startswith("hr_z") and f"_fused_{c}" not in df_events.columns:
            df_events[f"_fused_{c}"] = df_events[c]

    debug(context, "[T2-FUSED] Injected _fused_* columns from raw zones")

    # ======================================================
    # 🧩 Fuse Power + HR zones per sport (URF v5.1 addition)
    # ======================================================
    try:
        from coaching_cheat_sheet import CHEAT_SHEET
        groups = CHEAT_SHEET.get("sport_groups", {})
        fused = {}

        debug(context, f"[T2-FUSED] 🔍 Starting fused zone computation")
        debug(context, f"[T2-FUSED] df_events shape={df_events.shape}")
        debug(context, f"[T2-FUSED] df_events cols sample: {list(df_events.columns)[:30]}")

        # --- Ensure sport type column present
        if "type" not in df_events.columns:
            context.setdefault("sport_type", "Unknown")
            df_events["type"] = context["sport_type"]
            debug(context, f"[T2-FUSED] Injected missing 'type' column → default='{context['sport_type']}'")

        debug(context, f"[T2-FUSED] Unique types before fusion: {df_events['type'].unique().tolist()}")
        debug(context, f"[T2-FUSED] sport_groups available: {list(groups.keys())}")

        # --- Iterate sport groups from cheat sheet
        for sport_group, members in groups.items():
            if sport_group == "Excluded":
                continue

            sub = df_events[df_events["type"].isin(members)]
            debug(context, f"[T2-FUSED] Group '{sport_group}' members={members} → rows={len(sub)}")

            if sub.empty:
                continue

            # Identify possible zone columns
            pcols = [c for c in sub.columns if c.startswith("_fused_power_z")]
            hcols = [c for c in sub.columns if c.startswith("_fused_hr_z")]
            if not pcols and not hcols:
                debug(context, f"[T2-FUSED] ⚠️ No zone columns found for {sport_group}")
                continue

            fused_rows = []
            for idx, row in sub.iterrows():
                # Check availability
                has_power = pcols and pd.to_numeric(row[pcols], errors="coerce").fillna(0).sum() > 0
                has_hr = hcols and pd.to_numeric(row[hcols], errors="coerce").fillna(0).sum() > 0

                # Enforce per-activity exclusivity
                if has_power:
                    chosen = {k: row[k] for k in pcols if pd.notna(row[k])}
                    for h in hcols:  # zero HR values
                        chosen[h] = 0.0
                    source = "power"
                elif has_hr:
                    chosen = {k: row[k] for k in hcols if pd.notna(row[k])}
                    for p in pcols:  # zero power values
                        chosen[p] = 0.0
                    source = "hr"
                else:
                    continue

                fused_rows.append(chosen)
                debug(context, f"[T2-FUSED] Row {idx}: source={source}, has_power={has_power}, has_hr={has_hr}")

            if not fused_rows:
                debug(context, f"[T2-FUSED] ⚠️ No usable zone rows for {sport_group}")
                continue

            fused_df = pd.DataFrame(fused_rows).fillna(0)
            total = fused_df.sum().sum()
            if total <= 0:
                debug(context, f"[T2-FUSED] ⚠️ {sport_group}: total zone sum <= 0, skipping.")
                continue

            # Aggregate and normalize
            dist = (fused_df.sum() / total * 100).round(1).to_dict()
            fused[sport_group] = dist

            # --- Sanity check: warn if both HR and Power > 0
            hr_sum = sum(v for k, v in dist.items() if k.startswith("hr_z"))
            pw_sum = sum(v for k, v in dist.items() if k.startswith("power_z"))
            if hr_sum > 0 and pw_sum > 0:
                debug(context, f"[T2-FUSED] ⚠️ Double-count detected for {sport_group} (HR={hr_sum:.1f}, Power={pw_sum:.1f})")

            # Debug summary
            z1 = dist.get("power_z1", 0) + dist.get("hr_z1", 0)
            z2 = dist.get("power_z2", 0) + dist.get("hr_z2", 0)
            z3p = sum(v for k, v in dist.items() if any(z in k for z in ["z3", "z4", "z5"]))
            debug(context, f"[T2-FUSED] ✅ {sport_group}: Z1={z1:.1f}% Z2={z2:.1f}% Z3+={z3p:.1f}% total=100%")

        # --- Outcome
        if fused:
            dominant = max(fused.keys(), key=lambda k: sum(fused[k].values()))
            context["zone_dist_fused"] = fused
            context["polarisation_sport"] = dominant
            debug(context, f"[T2-FUSED] ✅ Fused zones computed → sports={list(fused.keys())}, dominant={dominant}")
        else:
            debug(context, "[T2-FUSED] ⚠️ No valid fused data produced.")

    except Exception as e:
        import traceback
        debug(context, f"[T2-FUSED] ❌ Zone fusion failed: {e}\n{traceback.format_exc()}")

    # ---------------------------------------------------------
    # 🧩 Combined Zones (ALL sports, fused, time-normalised ONCE)
    # Seiler / Stöggl / Issurin compliant
    # ---------------------------------------------------------
    try:
        debug(context, "[T2-COMBINED] 🔍 Starting combined zone computation (fused → canonical)")

        df = df_events.copy()

        # Operate ONLY on fused columns (already exclusive per activity)
        fused_cols = [c for c in df.columns if c.startswith("_fused_")]

        if not fused_cols:
            debug(context, "[T2-COMBINED] ⚠️ No fused zone columns available")
            context["zone_dist_combined"] = {}

        else:
            zdf = df[fused_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

            total_time = zdf.sum().sum()
            if total_time <= 0:
                debug(context, "[T2-COMBINED] ⚠️ Total fused time = 0")
                context["zone_dist_combined"] = {}

            else:
                # --------------------------------------------------
                # 1️⃣ Normalise ONCE across ALL sports (time-based)
                # --------------------------------------------------
                dist = (zdf.sum() / total_time * 100).to_dict()

                # --------------------------------------------------
                # 2️⃣ Collapse fused power/hr → canonical zones
                #     (zones are physiological, sensors are proxies)
                # --------------------------------------------------
                collapsed = {}

                for k, v in dist.items():
                    key = k
                    if key.startswith("_fused_"):
                        key = key.replace("_fused_", "")
                    if key.startswith("power_"):
                        key = key.replace("power_", "")
                    if key.startswith("hr_"):
                        key = key.replace("hr_", "")

                    collapsed[key] = collapsed.get(key, 0.0) + float(v)

                # --------------------------------------------------
                # 3️⃣ Final normalisation guard (should ≈100 already)
                # --------------------------------------------------
                total = sum(collapsed.values())
                if total > 0:
                    collapsed = {
                        k: round(v / total * 100, 1)
                        for k, v in collapsed.items()
                    }

                # --------------------------------------------------
                # 4️⃣ Store canonical combined distribution
                # --------------------------------------------------
                context["zone_dist_combined"] = {
                    "distribution": collapsed,
                    "basis": (
                        "Time-based intensity distribution across all endurance activities. "
                        "Power used when available, HR otherwise. "
                        "Normalised once across total training time "
                        "(Seiler / Stöggl / Issurin methodology)."
                    ),
                }

                debug(
                    context,
                    f"[T2-COMBINED] ✅ Combined zones computed → "
                    f"{len(collapsed)} zones, total={sum(collapsed.values()):.1f}%"
                )

    except Exception as e:
        import traceback
        debug(context, f"[T2-COMBINED] ❌ Failed: {e}\n{traceback.format_exc()}")




    # --- ✅ 8. ZQI (Zone Quality Index) ---
    zqi = compute_zone_intensity(df_events, context)
    debug(context, f"[DERIVED] ZQI (initial)={zqi}")

    # --- 🩹 Fallback recompute if no zone columns were present ---
    if (zqi == 0.0 or not zqi):
        zones = context.get("zone_dist_power") or context.get("zone_dist_hr") or {}
        if not zones and "zones" in context:
            # try pulling from 'zones' block if collect_zone_distributions() already ran
            zblock = context["zones"]
            if "power" in zblock and isinstance(zblock["power"], dict):
                zones = zblock["power"]
            elif "hr" in zblock and isinstance(zblock["hr"], dict):
                zones = zblock["hr"]

        if zones:
            total = sum(float(v) for v in zones.values())
            if total > 0:
                high = sum(float(zones.get(z, 0)) for z in ["power_z4","power_z5","power_z6","power_z7","hr_z4","hr_z5","hr_z6","hr_z7"])
                zqi = round(high / total * 100, 1)
                debug(context, f"[ZQI] 🩵 Recomputed from zone distributions → {zqi}% (High={high:.1f} / Total={total:.1f})")
                context["ZQI"] = zqi

    # --- ✅ 9. Fat oxidation efficiency ---
    if_proxy = 0.7  # fallback when usable intensity data is unavailable

    if "icu_intensity" in df_events.columns:
        intensity = pd.to_numeric(
            df_events["icu_intensity"],
            errors="coerce"
        )

        intensity.loc[intensity > 10] /= 100
        valid_intensity = intensity.dropna()

        if not valid_intensity.empty:
            if_proxy = float(valid_intensity.mean())

    fat_ox_eff = round(
        float(np.clip(if_proxy * 0.9, 0.3, 0.8)),
        3
    )
    # ---------------------------------------------------------
    # 🧩 Polarisation Metrics (Seiler 3-zone + Treff PI)
    # ---------------------------------------------------------

    # 1️⃣ Get zone dictionary (power preferred)
    zones = (
        context.get("zone_dist_power")
        or context.get("zone_dist_hr")
        or context.get("zones", {}).get("power", {})
        or context.get("zones", {}).get("hr", {})
        or {}
    )

    def get_zone(z):
        if not isinstance(zones, dict):
            return 0.0
        return float(
            zones.get(f"power_{z}",
            zones.get(f"hr_{z}",
            zones.get(z, 0.0)))
        )

    # 2️⃣ Collapse 7-zone → Seiler 3-zone
    z1_raw = get_zone("z1")
    z2_raw = get_zone("z2")
    z3_raw = (
        get_zone("z3")
        + get_zone("z4")
        + get_zone("z5")
        + get_zone("z6")
        + get_zone("z7")
    )

    total = z1_raw + z2_raw + z3_raw

    if total > 0:
        z1 = z1_raw / total
        z2 = z2_raw / total
        z3 = z3_raw / total
    else:
        z1 = z2 = z3 = 0.0

    # -------------------------------------------------
    # 3️⃣ Seiler-style Contrast Ratio
    # (heuristic operationalisation of 3-zone model)
    # -------------------------------------------------
    if z2 > 0:
        polarisation = round((z1 + z3) / (2 * z2), 3)
        debug(context, f"[POL] Seiler 3-zone → Z1={z1:.3f} Z2={z2:.3f} Z3+={z3:.3f} → Ratio={polarisation}")
    else:
        polarisation = 0.0
        debug(context, "[POL] Seiler ratio fallback → Z2=0")

    # -------------------------------------------------
    # 4️⃣ Treff Polarization-Index (2019)
    # PI = log10( Z1 / (Z2 × Z3) × 100 )
    # Requires all 3 collapsed zones to be positive.
    # -------------------------------------------------
    if z1 > 0 and z2 > 0 and z3 > 0:
        polarisation_index = round(
            float(np.log10((z1 / (z2 * z3)) * 100)),
            3
        )
        debug(context, f"[POL] Treff PI → {polarisation_index}")
    else:
        polarisation_index = 0.0
        debug(
            context,
            f"[POL] Treff PI fallback → invalid zone proportions "
            f"Z1={z1:.3f} Z2={z2:.3f} Z3={z3:.3f}"
        )

    # 5️⃣ Register
    context["Polarisation"] = polarisation
    context["PolarisationIndex"] = polarisation_index

    debug(context, f"[DERIVED] Polarisation={polarisation} | TreffPI={polarisation_index}")

    # ======================================================
    # 🧪 Lactate Measurement Integration (df_light ONLY)
    # ======================================================

    df_lac = context.get("df_light")

    if not isinstance(df_lac, pd.DataFrame) or df_lac.empty:
        df_lac = None

    if df_lac is None or df_lac.empty:
        context["lactate_summary"] = {"available": False}
        debug(context, "[LACTATE] no df_light available")

    else:
        df_lac = df_lac.copy()

        if "HrtLndLt1" not in df_lac.columns:
            context["lactate_summary"] = {"available": False}
            debug(context, "[LACTATE] HrtLndLt1 not in df_light columns")

        else:
            # --- Coerce
            df_lac["HrtLndLt1"] = pd.to_numeric(df_lac["HrtLndLt1"], errors="coerce")
            df_lac["HrtLndLt1p"] = (
                pd.to_numeric(df_lac["HrtLndLt1p"], errors="coerce")
                if "HrtLndLt1p" in df_lac.columns
                else np.nan
            )

            # --- Lactate-only samples (DO NOT REQUIRE POWER)
            df_valid = df_lac[df_lac["HrtLndLt1"] > 0]

            samples = len(df_valid)
            debug(context, f"[LACTATE] rows={len(df_lac)} valid_samples={samples}")

            if samples == 0:
                context["lactate_summary"] = {"available": False}
                debug(context, "[LACTATE] no valid lactate samples")

            else:
                lact_vals = df_valid["HrtLndLt1"]

                mean_lac = round(lact_vals.mean(), 2)
                latest_lac = round(lact_vals.iloc[-1], 2)
                min_lac = round(lact_vals.min(), 2)
                max_lac = round(lact_vals.max(), 2)

                # --- Power handling
                paired_power = df_valid["HrtLndLt1p"].dropna()
                paired_with_power = not paired_power.empty

                if paired_with_power:
                    power_vals = paired_power
                    power_spread = [
                        round(power_vals.min(), 1),
                        round(power_vals.max(), 1),
                    ]
                    power_source = "activity_samples"
                else:
                    ftp = context.get("ftp")
                    if isinstance(ftp, (int, float)) and ftp > 0:
                        z2_mid = round(ftp * 0.70, 1)
                        power_vals = pd.Series([z2_mid] * samples)
                        power_spread = [z2_mid, z2_mid]
                        power_source = "ftp_z2_fallback"
                    else:
                        power_vals = None
                        power_spread = None
                        power_source = "unpaired"

                # --- Correlation (safe)
                if (
                    power_vals is not None
                    and lact_vals.nunique() > 1
                    and power_vals.nunique() > 1
                ):
                    corr_val = lact_vals.corr(power_vals)
                    corr_with_power = round(float(corr_val), 3) if pd.notna(corr_val) else 0.0
                else:
                    corr_with_power = 0.0

                # --- Store
                context["lactate_summary"] = {
                    "available": True,
                    "samples": samples,
                    "mean_mmol": mean_lac,
                    "latest_mmol": latest_lac,
                    "range_mmol": [min_lac, max_lac],
                    "paired_with_power": paired_with_power,
                    "power_field": "HrtLndLt1p",
                    "power_spread_w": power_spread,
                    "power_source": power_source,
                    "corr_with_power": corr_with_power,
                    "corr_window_days": 90,
                    "source": "df_light",
                    "mean": mean_lac,
                    "latest": latest_lac,
                }

                debug(context, f"[LACTATE] OK → {context['lactate_summary']}")

                # --- Calibration flag only (no zone mutation)
                corr_threshold = CHEAT_SHEET.get("thresholds", {}).get("Lactate", {}).get("corr_threshold", 0.6)
                context["zones_corr"] = corr_with_power

                if corr_with_power >= corr_threshold:
                    context["zones_source"] = "lactate_test"
                    context["zones_reason"] = f"lactate correlation r={corr_with_power:.2f}"
                else:
                    context["zones_source"] = "ftp_based"
                    context["zones_reason"] = f"lactate weak/assumed power ({power_source})"



    # --- Other metabolic markers ---
    foxi = round(fat_ox_eff * 100, 1)
    cur = round(100 - foxi, 1)
    gr = round(if_proxy * 2.4, 2)
    mes = round((fat_ox_eff * 60) / (gr + 1e-6), 1)
    lvi = round(np.clip(1 - (monotony / 5), 0, 1), 3)

    debug(context,
        f"[DERIVED] IF_proxy={if_proxy:.3f}, FatOxEff={fat_ox_eff}, "
        f"Polarisation={polarisation}, PolarisationIndex={polarisation_index}, "
        f"MES={mes}, LVI={lvi}"
    )

    # --- ✅ 10. Classification (via COACH_PROFILE markers) ---
    # Apply classification to all metrics that have criteria
    to_classify = {
        "HRV": hrv_val,
        "ACWR": acwr,
        "Monotony": monotony,
        "Strain": strain,
        "FatigueTrend": fatigue_trend,
        "ZQI": zqi,
        "FatOxEfficiency": fat_ox_eff,
        "Polarisation": polarisation,
        "PolarisationIndex": polarisation_index,
        #"LoadVariabilityIndex": lvi,  #now internal only
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
        "ACWR": {
            "value": acwr,
            "classification": classified["ACWR"]["state"],
            "icon": classified["ACWR"]["icon"],
            "desc": f"EWMA Acute:Chronic Load Ratio ({acute_days}d / {chronic_days}d)",
            "interpretation": (
                f"EWMA Acute:Chronic Load Ratio — compares {acute_days}-day vs "
                f"{chronic_days}-day weighted loads. "
                "0.8–1.3 = productive training, <0.8 = recovery or detraining, >1.5 = overload/injury risk."
            ),
        },
        "Monotony": {
            "value": monotony,
            "classification": classified["Monotony"]["state"],
            "icon": classified["Monotony"]["icon"],
            "desc": "Foster Load Variability",
        },
        "Strain": {
            "value": strain,
            "classification": classified["Strain"]["state"],
            "icon": classified["Strain"]["icon"],
            "desc": "Foster Load × Monotony",
        },
        "FatigueTrend": {
            "value": fatigue_trend,
            "classification": classified["FatigueTrend"]["state"],
            "icon": classified["FatigueTrend"]["icon"],
            "desc": "Recent 7d vs prior 21d daily load delta",
        },
        "ZQI": {
            "value": zqi,
            "classification": classified["ZQI"]["state"],
            "icon": classified["ZQI"]["icon"],
            "desc": "Zone Quality Index",
        },
        "FatOxEfficiency": {
            "value": fat_ox_eff,
            "classification": classified["FatOxEfficiency"]["state"],
            "icon": classified["FatOxEfficiency"]["icon"],
            "desc": "Fat oxidation efficiency",
        },
        "Polarisation": {
            "value": polarisation,
            "classification": classified["Polarisation"]["state"],
            "icon": classified["Polarisation"]["icon"],
            "desc": "Seiler 3-zone polarisation ratio (Z1+Z3)/(2×Z2)",
        },
        "PolarisationIndex": {
            "value": polarisation_index,
            "classification": classified["PolarisationIndex"]["state"],
            "icon": classified["PolarisationIndex"]["icon"],
            "desc": "Seiler 80/20 intensity distribution compliance",
        },
        "FOxI": {
            "value": foxi,
            "classification": classified["FOxI"]["state"],
            "icon": classified["FOxI"]["icon"],
            "desc": "Fat oxidation index",
        },
        "CUR": {
            "value": cur,
            "classification": classified["CUR"]["state"],
            "icon": classified["CUR"]["icon"],
            "desc": "Carbohydrate utilisation ratio",
        },
        "GR": {
            "value": gr,
            "classification": classified["GR"]["state"],
            "icon": classified["GR"]["icon"],
            "desc": "Glucose ratio",
        },
        "MES": {
            "value": mes,
            "classification": classified["MES"]["state"],
            "icon": classified["MES"]["icon"],
            "desc": "Metabolic efficiency score",
        },
        "StressTolerance": {
            "value": stress_tolerance,
            "classification": classified["StressTolerance"]["state"],
            "icon": classified["StressTolerance"]["icon"],
            "desc": "Sustainable training tolerance",
        },
    }
    # ======================================================
    # 🩵 HR-only Fallback Annotations (metadata for reports)
    # ======================================================
    has_power = any("power_z" in c.lower() for c in df_events.columns)
    has_if = "icu_intensity" in df_events.columns
    has_hr = any("hr_z" in c.lower() for c in df_events.columns)

    context["hr_only_mode"] = bool(has_hr and not has_power)
    context["power_data_present"] = bool(has_power)
    context["if_proxy_used"] = not has_if

    if context["hr_only_mode"]:
        debug(context, "[T2] ⚙️ HR-only fallback mode — metrics derived from HR zones or IF proxy.")
        context["derived_warnings"] = [
            "⚙️ Using HR-only data — FatOx, MES, and Polarisation approximated.",
            "Zone metrics derived from HR response (lag-corrected).",
        ]
    elif context["if_proxy_used"]:
        debug(context, "[T2] ⚙️ IF proxy mode — no direct power or IF data available.")
        context["derived_warnings"] = [
            "⚙️ Intensity Factor proxy (0.7) used — metabolic scores approximate.",
        ]
    else:
        context["derived_warnings"] = []


    # --- ✅ 12. Flatten for validator ---
    for k, v in derived.items():
        context[k] = v.get("value", np.nan)

    context["PolarisationIndex"] = polarisation_index
    context["Polarisation"] = polarisation

    context["derived_metrics"] = derived

    debug(context, "[T2] ✅ Derived metrics fully computed and classified.")
    debug(context, f"[SUMMARY] ACWR={acwr}, Monotony={monotony}, Strain={strain}, FatOxEff={fat_ox_eff}, ZQI={zqi}, StressTol={stress_tolerance}")

    return context
