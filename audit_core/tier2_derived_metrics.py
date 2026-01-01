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
from coaching_cheat_sheet import CHEAT_SHEET

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

def compute_zone_intensity(df, context=None):
    """
    Zone Quality Index (ZQI) — percentage of total training time spent in high-intensity zones (Z5–Z7).
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
        debug_fn(context, "[POL] ⚠ No df_events for IF fallback → 0.0")
        return 0.0

    if "IF" not in df.columns or "moving_time" not in df.columns:
        debug_fn(context, "[POL] ⚠ Missing IF or moving_time → 0.0")
        return 0.0

    try:
        tmp = df[["IF", "moving_time"]].copy()
        tmp["IF"] = pd.to_numeric(tmp["IF"], errors="coerce")
        tmp["moving_time"] = pd.to_numeric(tmp["moving_time"], errors="coerce").fillna(0)
        tmp = tmp.dropna(subset=["IF"])
        tmp = tmp[tmp["moving_time"] > 0]
        if tmp.empty:
            debug_fn(context, "[POL] ⚠ IF fallback has no valid rows → 0.0")
            return 0.0

        tmp.loc[tmp["IF"] > 10, "IF"] /= 100.0
        total_time = float(tmp["moving_time"].sum())
        if total_time <= 0:
            return 0.0

        low_time = float(tmp.loc[tmp["IF"] < 0.85, "moving_time"].sum())
        pol = round(low_time / total_time, 3)
        debug_fn(context, f"[POL] (IF-fallback) low_time={low_time:.1f}s total={total_time:.1f}s → PI={pol}")
        return pol

    except Exception as e:
        debug_fn(context, f"[POL] ⚠ IF fallback failed ({e}) → 0.0")
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

    # Canonical aliases
    marker_aliases = {
        "Polarisation": "PolarisationIndex",
        "FatOx": "FatOxEfficiency",
        "FatOxidation": "FatOxEfficiency",
        "Recovery": "RecoveryIndex",
    }
    marker = marker_aliases.get(marker, marker)

    # Skip multi-dimensional markers
    MULTI_DIMENSIONAL = {"Polarisation", "PolarisationIndex"}
    if marker in MULTI_DIMENSIONAL:
        debug(context, f"[CLASSIFY] {marker}: skipped (multi-dimensional metric)")
        return "—", "computed"

    # Marker definition
    marker_def = COACH_PROFILE.get("markers", {}).get(marker, {})
    criteria = marker_def.get("criteria")

    if not criteria:
        debug(context, f"[CLASSIFY] {marker}: no criteria defined")
        return "⚪", "undefined"

    # --- Rule parsing ---
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

    # --- Icon mapping ---
    icon_map = {
        "optimal": "🟢", "productive": "🟢", "balanced": "🟢", "polarised": "🟢",
        "moderate": "🟠", "borderline": "🟠", "mixed": "🟠", "recovering": "🟠",
        "low": "🔴", "high": "🔴", "overload": "🔴", "accumulating": "🔴", "threshold": "🔴"
    }

    # --- Evaluation ---
    for state, rule in criteria.items():
        if parse_rule(rule)(v):
            icon = icon_map.get(state, "⚪")
            debug(context, f"[CLASSIFY] {marker}: {v} → {state}")
            return icon, state

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
            pcols = [c for c in sub.columns if c.startswith("power_z")]
            hcols = [c for c in sub.columns if c.startswith("hr_z")]
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
    # 🧩 Combined Zones (global HR+Power blend across all sports)
    # ---------------------------------------------------------
    try:
        debug(context, "[T2-COMBINED] 🔍 Starting combined zone computation")

        fused = context.get("zone_dist_fused", {})
        combined = {}

        if not fused:
            debug(context, "[T2-COMBINED] ⚠️ No fused zones in context → skipping combination.")
        else:
            debug(context, f"[T2-COMBINED] Found fused sports: {list(fused.keys())}")

            # --- Aggregate all sports’ fused distributions
            all_keys = set()
            for sport_data in fused.values():
                all_keys.update(sport_data.keys())

            debug(context, f"[T2-COMBINED] All zone keys across sports: {sorted(all_keys)}")

            for key in all_keys:
                combined[key] = np.mean([
                    sport_data.get(key, 0.0) for sport_data in fused.values()
                ])

            # --- Optional sanity report
            debug(context, f"[T2-COMBINED] Combined mean zones → sample: "
                           f"{ {k: round(v,1) for k,v in list(combined.items())[:6]} }")

            # --- Compute Polarisation Index (Z1 vs. Z3+)
            z1 = combined.get("hr_z1", 0) + combined.get("power_z1", 0)
            z3p = sum(v for k, v in combined.items()
                      if any(zone in k for zone in ["z3", "z4", "z5"]))
            polarisation_index = round(z1 / (z1 + z3p + 1e-9), 3)

            # --- Simple model classification
            if polarisation_index >= 0.8:
                model = "polarised"
            elif 0.65 <= polarisation_index < 0.8:
                model = "pyramidal"
            else:
                model = "threshold"

            context["zone_dist_combined"] = {
                "distribution": {k: round(v, 2) for k, v in combined.items()},
                "basis": "Power where available, HR otherwise (multi-sport weighted)",
                "polarisation_index": polarisation_index,
                "model": model,
            }

            debug(context,
                  f"[T2-COMBINED] ✅ Combined zones computed → PI={polarisation_index}, model={model}")

    except Exception as e:
        import traceback
        debug(context, f"[T2-COMBINED] ❌ Failed to compute combined zones: {e}\n{traceback.format_exc()}")



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
                high = sum(float(zones.get(z, 0)) for z in ["power_z5","power_z6","power_z7","hr_z5","hr_z6","hr_z7"])
                zqi = round(high / total * 100, 1)
                debug(context, f"[ZQI] 🩵 Recomputed from zone distributions → {zqi}% (High={high:.1f} / Total={total:.1f})")
                context["ZQI"] = zqi

    # --- ✅ 9. Fat oxidation efficiency ---
    if "IF" in df_events.columns:
        df_events["IF"] = pd.to_numeric(df_events["IF"], errors="coerce")
        df_events.loc[df_events["IF"] > 10, "IF"] /= 100
        if_proxy = np.nanmean(df_events["IF"].values)
    else:
        if_proxy = 0.7  # assume aerobic bias if missing

    fat_ox_eff = round(np.clip((if_proxy or 0.5) * 0.9, 0.3, 0.8), 3)
    # ---------------------------------------------------------
    # 🧩 Polarisation Metrics (Seiler ratio + normalized index)
    # ---------------------------------------------------------
    if "to_classify" not in locals():
        to_classify = {}
    if "classified" not in locals():
        classified = {}

    # 🩹 Ensure zone_dist_* are dicts
    for key in ("zone_dist_power", "zone_dist_hr"):
        if key in context and not isinstance(context[key], dict):
            try:
                if hasattr(context[key], "to_dict"):
                    context[key] = context[key].to_dict()
                else:
                    context[key] = dict(context[key])
                debug(context, f"[T2] Rehydrated {key} to dict with {len(context[key])} keys.")
            except Exception as e:
                debug(context, f"[T2] ⚠️ Failed to rehydrate {key}: {e}")
                context[key] = {}

    # 1️⃣ Normalized Polarisation Index
    polarisation_index = compute_polarisation_index(context)

    # 2️⃣ Get zone dictionary
    zones = (
        context.get("zone_dist_power")
        or context.get("zone_dist_hr")
        or context.get("zones", {}).get("power", {})
        or context.get("zones", {}).get("hr", {})
        or {}
    )

    # 3️⃣ Helper for flexible key access
    def get_zone(z):
        if not isinstance(zones, dict):
            return 0.0
        return float(
            zones.get(f"power_{z}",
            zones.get(f"hr_{z}",
            zones.get(z, 0.0)))
        )

    # 4️⃣ Extract and compute Seiler ratio safely
    try:
        z1, z2, z3 = get_zone("z1"), get_zone("z2"), get_zone("z3")
        if z2 > 0 and (z1 > 0 or z3 > 0):
            polarisation = round((z1 + z3) / (2 * z2), 3)
            debug(context, f"[POL] ✅ Seiler ratio computed → (Z1+Z3)/(2×Z2)={polarisation}")
        else:
            polarisation = round(float(polarisation_index or 0.0), 3)
            debug(context, f"[POL] ⚠️ Missing Z2 or empty zones — fallback to PI={polarisation}")
    except Exception as e:
        debug(context, f"[POL] ⚠️ Seiler ratio computation failed → fallback ({e})")
        polarisation = round(float(polarisation_index or 0.0), 3)

    # 5️⃣ Register metrics
    context["Polarisation"] = polarisation
    context["PolarisationIndex"] = polarisation_index

    # 6️⃣ Classify
    to_classify.update({
        "Polarisation": polarisation,
        "PolarisationIndex": polarisation_index,
    })

    for marker in ["Polarisation", "PolarisationIndex"]:
        val = to_classify.get(marker)
        if val is not None:
            icon, state = classify_marker(val, marker, context)
            classified[marker] = {"icon": icon, "state": state}
            debug(context, f"[CLASSIFY] {marker}={val} → {icon} {state}")
        else:
            debug(context, f"[CLASSIFY] ⚠️ Skipped {marker} — no value")

    debug(context, f"[DERIVED] Polarisation={polarisation} | PolarisationIndex={polarisation_index}")


    # ======================================================
    # 🧪 Lactate Measurement Integration (context enrichment)
    # ======================================================
    if "HRTLNDLT1" in df_events.columns:
        try:
            df_events["HRTLNDLT1"] = pd.to_numeric(df_events["HRTLNDLT1"], errors="coerce")
            valid_lac = df_events["HRTLNDLT1"].dropna()
            total_rows = len(df_events)
            valid_count = len(valid_lac)

            debug(context, (
                f"[DERIVED] HRTLNDLT1 found → total={total_rows}, valid={valid_count}, "
                f"values={valid_lac.tolist()[:10]}{'...' if valid_count > 10 else ''}"
            ))

            if not valid_lac.empty:
                mean_lac = round(valid_lac.mean(), 2)
                latest_lac = round(valid_lac.iloc[-1], 2)
                samples = len(valid_lac)
                min_lac, max_lac = round(valid_lac.min(), 2), round(valid_lac.max(), 2)

                thresholds = {"aerobic": 2.0, "anaerobic": 4.0}
                zone_dist = {
                    "below_2mmol": int((valid_lac < thresholds["aerobic"]).sum()),
                    "between_2_4mmol": int(((valid_lac >= thresholds["aerobic"]) &
                                            (valid_lac < thresholds["anaerobic"])).sum()),
                    "above_4mmol": int((valid_lac >= thresholds["anaerobic"]).sum())
                }

                corr_with_power = None
                if "icu_average_watts" in df_events.columns:
                    df_lac = df_events.dropna(subset=["HRTLNDLT1", "icu_average_watts"])
                    if not df_lac.empty:
                        corr_val = df_lac["HRTLNDLT1"].corr(df_lac["icu_average_watts"])
                        if pd.notna(corr_val):
                            corr_with_power = round(float(corr_val), 3)
                        else:
                            corr_with_power = 0.0
                            debug(context, "[DERIVED] Lactate–Power correlation undefined (constant series) → set to 0.0")

                context["lactate_summary"] = {
                    "mean_mmol": mean_lac,
                    "latest_mmol": latest_lac,
                    "samples": samples,
                    "range_mmol": [min_lac, max_lac],
                    "zone_distribution": zone_dist,
                    "corr_with_power": corr_with_power,
                    "available": True
                }
                # Normalize keys for compatibility
                lac = context["lactate_summary"]
                if "mean_mmol" in lac and "mean" not in lac:
                    lac["mean"] = lac["mean_mmol"]
                if "latest_mmol" in lac and "latest" not in lac:
                    lac["latest"] = lac["latest_mmol"]
                context["lactate_summary"] = lac

                debug(context, (
                    f"[DERIVED] HRTLNDLT1 ✓ integrated → mean={mean_lac} mmol/L, "
                    f"latest={latest_lac}, samples={samples}, corr_with_power={corr_with_power}, zones={zone_dist}"
                ))
                # ======================================================
                # 🔄 Lactate Calibration Context Alignment (URF v5.1)
                # ======================================================

                try:
                    lac_thresholds = CHEAT_SHEET["thresholds"].get("Lactate", {})
                    lt1_default = lac_thresholds.get("lt1_mmol", 2.0)
                    lt2_default = lac_thresholds.get("lt2_mmol", 4.0)
                    corr_threshold = lac_thresholds.get("corr_threshold", 0.6)
                    corr_val = context["lactate_summary"].get("corr_with_power")

                    # Store correlation value directly for calibration confidence
                    context["zones_corr"] = corr_val

                    if isinstance(corr_val, (int, float)) and corr_val >= corr_threshold:
                        context["zones_source"] = "lactate_test"
                        context["zones_reason"] = (
                            f"Lactate–power correlation strong (r={corr_val:.2f}≥{corr_threshold})"
                        )
                        context["lactate_thresholds_dict"] = {
                            "lt1_mmol": lt1_default,
                            "lt2_mmol": lt2_default,
                        }
                        debug(context, f"[DERIVED] ✅ Lactate calibration active → LT1={lt1_default}, LT2={lt2_default}, r={corr_val:.2f}")
                    else:
                        context["zones_source"] = "ftp_based"
                        context["zones_reason"] = (
                            f"Lactate–power correlation weak or missing (r={corr_val}) → FTP defaults"
                        )
                        context["lactate_thresholds_dict"] = {
                            "lt1_mmol": lt1_default,
                            "lt2_mmol": lt2_default,
                        }
                        debug(context, f"[DERIVED] ⚠️ Lactate correlation below threshold ({corr_val}) → FTP-based calibration")

                except Exception as e:
                    context["zones_source"] = "ftp_based"
                    context["zones_reason"] = f"Lactate calibration error: {e}"
                    context["lactate_thresholds_dict"] = {}
                    debug(context, f"[DERIVED] ⚠️ Lactate calibration context alignment failed → {e}")

            else:
                context["lactate_summary"] = {"available": False}
                debug(context, "[DERIVED] HRTLNDLT1 present but no valid numeric values.")

        except Exception as e:
            context["lactate_summary"] = {"available": False}
            debug(context, f"[DERIVED] ⚠️ HRTLNDLT1 integration failed → {e}", exc_info=True)
    else:
        context["lactate_summary"] = {"available": False}
        debug(context, "[DERIVED] HRTLNDLT1 column NOT FOUND in df_events.")



    # --- Other metabolic markers ---
    foxi = round(fat_ox_eff * 100, 1)
    cur = round(100 - foxi, 1)
    gr = round(if_proxy * 2.4, 2)
    mes = round((fat_ox_eff * 60) / (gr + 1e-6), 1)
    rec_index = round(np.clip(1 - (monotony / 5), 0, 1), 3)

    debug(context,
        f"[DERIVED] IF_proxy={if_proxy:.3f}, FatOxEff={fat_ox_eff}, "
        f"Polarisation={polarisation}, PolarisationIndex={polarisation_index}, "
        f"MES={mes}, RecIndex={rec_index}"
    )

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
        "PolarisationIndex": polarisation_index,
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
        "ACWR": {
            "value": acwr,
            "classification": classified["ACWR"]["state"],
            "icon": classified["ACWR"]["icon"],
            "desc": "EWMA Acute:Chronic Load Ratio",
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
            "desc": "7d vs 28d load delta",
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
        "RecoveryIndex": {
            "value": rec_index,
            "classification": classified["RecoveryIndex"]["state"],
            "icon": classified["RecoveryIndex"]["icon"],
            "desc": "Recovery readiness (Noakes Central Governor)",
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
    has_if = "IF" in df_events.columns
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
