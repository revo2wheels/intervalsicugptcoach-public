# tier3_performance_intelligence.py
"""
Tier 3 — Performance Intelligence

Contracts:
    WDRM → Anaerobic Repeatability (W′ depletion behavior)
    ISDM → Durability (decoupling & session drift)
    NDLI → Neural Density (high-intensity clustering)

Weekly → 7d FULL dataset (high resolution)
Season → 90d LIGHT chronic aggregation + 7d acute overlay
"""


from audit_core.utils import debug
import pandas as pd
import numpy as np
from coaching_profile import COACH_PROFILE
from tier3_trail_execution import run_trail_execution

PI_VERSION = "PI_v1.62"
# ===========================================================
# Public Entry
# ===========================================================

def compute_performance_intelligence(context, contract_type="weekly"):
    """
    Tier-3 Performance Intelligence

    Weekly:
        High-resolution model using 7-day FULL.

    Season:
        Chronic aggregation using 90-day LIGHT
        + Acute overlay using 7-day FULL.
    """

    df_full = context.get("_df_scope_full")
    df_light = context.get("_df_light_90d")

    debug(context, f"[T3] Performance Intelligence start ({contract_type})")

    if contract_type in ("season", "summary"):
        result = _compute_season(context, df_light, df_full)

    else:
        acute = _compute_weekly(context, df_full)

        acute_has_signal = any([
            acute.get("durability", {}).get("state") is not None,
            acute.get("anaerobic_repeatability", {}).get("mean_depletion_pct_7d") is not None,
            (acute.get("neural_density", {}).get("rolling_joules_above_ftp_7d") or 0) > 0,
            acute.get("neural_density", {}).get("mean_efficiency_factor_7d") is not None,
            acute.get("neural_density", {}).get("mean_variability_index_7d") is not None,
        ])

        chronic_context = {}

        if not acute_has_signal and df_light is not None and not df_light.empty:
            season_like = _compute_season(context, df_light, df_full)
            chronic_context = season_like.get("chronic_state") or {}

        result = {
            **acute,
            "chronic_context": chronic_context,
            "acute_context_window": "7d_full",
            "chronic_context_window": "90d_light" if chronic_context else None,
        }

    # ✅ Make result visible to interpreter
    context["performance_intelligence"] = result
    context["PI_VERSION"] = PI_VERSION

    #Enviornmental factors
    compute_external_load_context(
        context,
        df_full
    )

    # --- Terrain Execution (conditional) ---
    run_trail_execution(context)

    # ✅ Now interpret using actual data
    interpretation = interpret_training_state(context)
    context["training_state"] = interpretation
    debug(context, f"[T3 OUTPUT KEYS] {list(result.keys())}")

    compute_nutrition_demand(context)
    compute_nutrition_balance(context)
    return context.get("performance_intelligence", result)


# ===========================================================
# WEEKLY (7-DAY FULL – DO NOT COMPROMISE)
# ===========================================================

def _compute_weekly(context, df_full):

    if df_full is None or df_full.empty:
        debug(context, "[T3] Weekly: No FULL data")
        return _empty_weekly()

    debug(context, f"[T3] Weekly FULL rows: {len(df_full)}")

    w_prime = pd.to_numeric(df_full.get("icu_w_prime"), errors="coerce")
    depletion = pd.to_numeric(df_full.get("icu_max_wbal_depletion"), errors="coerce")
    joules = pd.to_numeric(df_full.get("icu_joules_above_ftp"), errors="coerce")
    decoupling_raw = pd.to_numeric(df_full.get("decoupling"), errors="coerce")
    efficiency = pd.to_numeric(df_full.get("icu_efficiency_factor"), errors="coerce")
    variability = pd.to_numeric(df_full.get("icu_variability_index"), errors="coerce")
    polarisation = pd.to_numeric(df_full.get("polarization_index"), errors="coerce")
    decoupling_signed = decoupling_raw
    decoupling_abs = decoupling_raw.abs()
    if_values = pd.to_numeric(df_full.get("icu_intensity"), errors="coerce")
    # normalize legacy intensity values (sometimes stored as %)
    if if_values is not None and not if_values.dropna().empty and if_values.max() > 2:
        if_values = if_values / 100
    moving_time = pd.to_numeric(df_full.get("moving_time"), errors="coerce")

    depletion_pct = None
    if w_prime is not None and depletion is not None:
        depletion_pct = (depletion / w_prime.replace(0, pd.NA)).clip(upper=1.5)

    # ---------------------------------------------
    # W′ utilization divergence (physiological)
    # ---------------------------------------------

    divergence = None

    if depletion_pct is not None and not depletion_pct.dropna().empty:

        mean_dep = depletion_pct.dropna().mean()

        # expected endurance baseline
        expected = 0.30

        divergence = float(mean_dep - expected)

        debug(
            context,
            "[T3][W′] Utilization divergence",
            f"{divergence:.3f}",
            f"(mean_dep={mean_dep:.3f}, baseline={expected})"
        )


    # --------------------------------------------------
    # ISDM durability classification
    # Preserve existing JSON contract.
    # Raw magnitude remains reported, but state uses signed
    # decoupling and requires repeated evidence.
    # --------------------------------------------------

    mean_signed = _safe_mean(decoupling_signed)
    mean_abs = _safe_mean(decoupling_abs)

    positive_high_drift_sessions = _safe_count(
        decoupling_signed,
        5.0
    ) or 0

    valid_decoupling_sessions = int(
        decoupling_signed.notna().sum()
    ) if isinstance(decoupling_signed, pd.Series) else 0

    durability_state = None

    if mean_signed is not None:

        # Substantial mean positive drift remains meaningful.
        if mean_signed > 10:
            durability_state = "drifting"

        # Moderate drift requires repetition, not one noisy activity.
        elif (
            mean_signed > 5
            and positive_high_drift_sessions >= 2
            and valid_decoupling_sessions >= 3
        ):
            durability_state = "drifting"

        elif mean_signed < -5 and valid_decoupling_sessions >= 2:
            durability_state = "improving"

        elif mean_signed < 0:
            durability_state = "stable_improving"

        else:
            durability_state = "stable"

    weekly_result = {
        "anaerobic_repeatability": {
            "max_depletion_pct_7d": _safe_max(depletion_pct),
            "mean_depletion_pct_7d": _safe_mean(depletion_pct),
            "moderate_depletion_sessions_7d": _safe_count(depletion_pct, 0.5),
            "high_depletion_sessions_7d": _safe_count(depletion_pct, 0.6),
            "total_joules_above_ftp_7d": _safe_sum(joules),
        },
        "model_diagnostics": {
            "w_prime_divergence_7d": divergence,
        },

        "durability": {
            "state": durability_state,
            "mean_decoupling_7d": mean_abs,
            #"mean_decoupling_signed_7d": mean_signed,

            "max_decoupling_7d": _safe_max(decoupling_abs),
            "high_drift_sessions_7d": _safe_count(decoupling_abs, 5.0),
            "long_sessions_7d": _safe_count(moving_time, 7200),
        },
        "neural_density": {
            "rolling_joules_above_ftp_7d": _safe_sum(joules),
            "high_intensity_days_7d": _safe_count(joules, 20000),
            "mean_if_7d": _safe_mean(if_values),

            "mean_efficiency_factor_7d": _safe_mean(efficiency),
            "mean_variability_index_7d": _safe_mean(variability),
        }
    }

    # -----------------------------------------------------------
    # T3 CONTRACT DEBUG — WEEKLY
    # -----------------------------------------------------------

    wdrm = weekly_result["anaerobic_repeatability"]
    isdm = weekly_result["durability"]
    ndli = weekly_result["neural_density"]

    debug(context, "[T3][WDRM] Anaerobic Repeatability (7d)",
        f"max_dep_pct={wdrm['max_depletion_pct_7d']}",
        f"mean_dep_pct={wdrm['mean_depletion_pct_7d']}",
        f"high_dep_sessions={wdrm['high_depletion_sessions_7d']}",
        f"joules_above_ftp={wdrm['total_joules_above_ftp_7d']}")

    debug(context, "[T3][ISDM] Durability (7d)",
        f"mean_decoupling={isdm['mean_decoupling_7d']}",
        f"max_decoupling={isdm['max_decoupling_7d']}",
        f"high_drift_sessions={isdm['high_drift_sessions_7d']}",
        f"long_sessions={isdm['long_sessions_7d']}")

    debug(context, "[T3][NDLI] Neural Density (7d)",
        f"rolling_joules={ndli['rolling_joules_above_ftp_7d']}",
        f"high_intensity_days={ndli['high_intensity_days_7d']}",
        f"mean_if={ndli['mean_if_7d']}")

    return weekly_result


# ===========================================================
# SEASON (90-DAY LIGHT + WEEKLY OVERLAY)
# ===========================================================

def _compute_season(context, df_light, df_full):

    if df_light is None or df_light.empty:
        debug(context, "[T3] Season: No LIGHT data")
        return _empty_season()

    debug(context, f"[T3] Season LIGHT rows: {len(df_light)}")

    # -------- Chronic 90d State --------

    # rolling CP model vs athlete profile W′
    rolling_w_prime = pd.to_numeric(df_light.get("icu_rolling_w_prime"), errors="coerce")
    athlete_w_prime = pd.to_numeric(df_light.get("icu_w_prime"), errors="coerce")

    # ensure Series
    if not isinstance(rolling_w_prime, pd.Series):
        rolling_w_prime = pd.Series([rolling_w_prime] * len(df_light))

    if not isinstance(athlete_w_prime, pd.Series):
        athlete_w_prime = pd.Series([athlete_w_prime] * len(df_light))

    depletion = pd.to_numeric(df_light.get("icu_max_wbal_depletion"), errors="coerce")

    if not isinstance(depletion, pd.Series):
        depletion = pd.Series([depletion] * len(df_light))

    joules = pd.to_numeric(df_light.get("icu_joules_above_ftp"), errors="coerce")
    decoupling = pd.to_numeric(df_light.get("decoupling"), errors="coerce")

    if_values = pd.to_numeric(
        df_light.get("icu_intensity", df_light.get("IF")),
        errors="coerce"
    )

    # normalize legacy IF values
    if if_values is not None and if_values.max() > 2:
        if_values = if_values / 100

    training_load = pd.to_numeric(df_light.get("icu_training_load"), errors="coerce")
    efficiency = pd.to_numeric(df_light.get("icu_efficiency_factor"), errors="coerce")
    variability = pd.to_numeric(df_light.get("icu_variability_index"), errors="coerce")
    polarisation = pd.to_numeric(df_light.get("polarization_index"), errors="coerce")

    # -----------------------------
    # W′ depletion %
    # -----------------------------

    depletion_pct = None
    if rolling_w_prime is not None and depletion is not None:
        depletion_pct = (depletion / rolling_w_prime.replace(0, pd.NA)).clip(upper=1.5)

    # -----------------------------
    # W′ model divergence (90d)
    # -----------------------------

    divergence_90d = None

    if rolling_w_prime is not None and athlete_w_prime is not None:

        rolling_clean = rolling_w_prime.replace(0, pd.NA)
        athlete_clean = athlete_w_prime.replace(0, pd.NA)

        valid_mask = rolling_clean.notna() & athlete_clean.notna()

        if valid_mask.any():

            mean_rolling = rolling_clean[valid_mask].mean()
            mean_athlete = athlete_clean[valid_mask].mean()

            if pd.notna(mean_athlete) and mean_athlete != 0:

                divergence_90d = float((mean_rolling - mean_athlete) / mean_athlete)

                # clamp extreme outliers
                divergence_90d = max(min(divergence_90d, 1.0), -1.0)

                debug(
                    context,
                    "[T3][W′] Model divergence (90d)",
                    f"{divergence_90d:.3f}",
                    f"(rolling={mean_rolling:.0f}, athlete={mean_athlete:.0f})"
                )

    model_diag = {}

    if divergence_90d is not None:
        model_diag["w_prime_divergence_90d"] = divergence_90d

    decoupling_signed = decoupling
    decoupling_abs = decoupling.abs()

    mean_signed = _safe_mean(decoupling_signed)
    mean_abs = _safe_mean(decoupling_abs)

    positive_high_drift_sessions_90d = _safe_count(
        decoupling_signed,
        5.0
    ) or 0

    valid_decoupling_sessions_90d = int(
        decoupling_signed.notna().sum()
    ) if isinstance(decoupling_signed, pd.Series) else 0

    durability_state_90d = None

    if mean_signed is not None:

        if mean_signed > 8:
            durability_state_90d = "drifting"

        elif (
            mean_signed > 5
            and positive_high_drift_sessions_90d >= 3
            and valid_decoupling_sessions_90d >= 5
        ):
            durability_state_90d = "drifting"

        elif mean_signed < -4 and valid_decoupling_sessions_90d >= 3:
            durability_state_90d = "improving"

        elif mean_signed < 0:
            durability_state_90d = "stable_improving"

        else:
            durability_state_90d = "stable"

    chronic = {
        "anaerobic_repeatability": {
            "mean_depletion_pct_90d": _safe_mean(depletion_pct),
            "max_depletion_pct_90d": _safe_max(depletion_pct),
            "moderate_depletion_sessions_90d": _safe_count(depletion_pct, 0.5),
            "high_depletion_sessions_90d": _safe_count(depletion_pct, 0.6),
            "total_joules_above_ftp_90d": _safe_sum(joules),
        },

        "model_diagnostics": model_diag,

        "durability": {
            "state": durability_state_90d,
            "mean_decoupling_90d": mean_abs,
            #"mean_decoupling_signed_90d": mean_signed,

            "max_decoupling_90d": _safe_max(decoupling_abs),
            "high_drift_sessions_90d": _safe_count(decoupling_abs, 5.0),
        },

        "neural_density": {
            "high_intensity_sessions_90d": _safe_count(joules, 20000),
            "mean_if_90d": _safe_mean(if_values),
            "mean_training_load_90d": _safe_mean(training_load),

            "mean_efficiency_factor_90d": _safe_mean(efficiency),
            "mean_variability_index_90d": _safe_mean(variability),
        }
    }

    # -------- Acute Overlay (full fidelity weekly) --------

    if df_full is not None and not df_full.empty:
        acute_overlay = _compute_weekly(context, df_full)
    else:
        acute_overlay = _empty_weekly()

    # -----------------------------------------------------------
    # T3 CONTRACT DEBUG — SEASON (CHRONIC 90D)
    # -----------------------------------------------------------

    wdrm_c = chronic["anaerobic_repeatability"]
    isdm_c = chronic["durability"]
    ndli_c = chronic["neural_density"]

    debug(context, "[T3][SEASON][WDRM] Chronic Anaerobic Repeatability (90d)",
        f"mean_dep_pct={wdrm_c['mean_depletion_pct_90d']}",
        f"max_dep_pct={wdrm_c['max_depletion_pct_90d']}",
        f"moderate_dep_sessions={wdrm_c['moderate_depletion_sessions_90d']}",
        f"high_dep_sessions={wdrm_c['high_depletion_sessions_90d']}",
        f"total_joules_above_ftp={wdrm_c['total_joules_above_ftp_90d']}")

    debug(context, "[T3][SEASON][ISDM] Chronic Durability (90d)",
        f"mean_decoupling={isdm_c['mean_decoupling_90d']}",
        f"max_decoupling={isdm_c['max_decoupling_90d']}",
        f"high_drift_sessions={isdm_c['high_drift_sessions_90d']}")

    debug(context, "[T3][SEASON][NDLI] Chronic Neural Density (90d)",
        f"high_intensity_sessions={ndli_c['high_intensity_sessions_90d']}",
        f"mean_if={ndli_c['mean_if_90d']}",
        f"mean_training_load={ndli_c['mean_training_load_90d']}")

    # -----------------------------------------------------------
    # Acute vs Chronic Delta Debug
    # -----------------------------------------------------------

    if acute_overlay:

        wdrm_a = acute_overlay["anaerobic_repeatability"]
        isdm_a = acute_overlay["durability"]

        # --- W′ (valid numeric comparison) ---
        acute_mean_dep = wdrm_a.get("mean_depletion_pct_7d")
        chronic_mean_dep = wdrm_c.get("mean_depletion_pct_90d")

        dep_ratio = None
        if acute_mean_dep is not None and chronic_mean_dep not in (None, 0):
            dep_ratio = acute_mean_dep / chronic_mean_dep

        # --- DURABILITY (state is the signal) ---
        acute_state = isdm_a.get("state")
        chronic_state = isdm_c.get("state")

        # optional: magnitude context (NOT interpretation)
        acute_stability = isdm_a.get("stability")
        chronic_stability = isdm_c.get("stability")

        stability_ratio = None
        if acute_stability is not None and chronic_stability not in (None, 0):
            stability_ratio = acute_stability / chronic_stability

        debug(
            context,
            "[T3][SEASON][DELTA] Acute vs Chronic",
            f"dep_ratio={dep_ratio}",
            f"acute_state={acute_state}",
            f"chronic_state={chronic_state}",
            f"stability_ratio={stability_ratio}",
        )

    return {
        "chronic_state": chronic,
        "acute_overlay": acute_overlay
    }

def compute_carb_demand_from_sessions(context, model):
    """
    Aligns with IOC/ACSM duration-based fueling
    Uses DAILY demand (not multi-day accumulation)
    """

    df = context.get("_df_scope_full")
    if df is None or df.empty:
        return None

    # --------------------------------------------------
    # PREP
    # --------------------------------------------------
    df = df.sort_values("start_date_local").copy()

    def normalize_intensity(x):
        if x is None:
            return 0
        return x / 100 if x > 2 else x

    df["intensity"] = df["icu_intensity"].apply(normalize_intensity)

    # remove low-intensity non-glycogen work
    df = df[df["intensity"] >= 0.5]

    if df.empty:
        return None

    # --------------------------------------------------
    # DAILY AGGREGATION
    # --------------------------------------------------
    df["date"] = df["start_date_local"].dt.date

    daily = df.groupby("date").apply(
        lambda d: pd.Series({
            "moving_time": d["moving_time"].sum(),
            "weighted_intensity": (d["moving_time"] * d["intensity"]).sum()
        })
    ).sort_index()

    # --------------------------------------------------
    # WINDOW SELECTION
    # --------------------------------------------------
    if len(daily) >= 5:
        daily = daily.tail(7)
    else:
        daily = daily.tail(3)

    if daily.empty:
        return None

    # --------------------------------------------------
    # DAILY NORMALISATION (CRITICAL FIX)
    # --------------------------------------------------
    total_seconds = daily["moving_time"].sum()
    num_days = len(daily)

    if total_seconds == 0 or num_days == 0:
        return None

    avg_hours_per_day = (total_seconds / 3600) / num_days

    weighted_intensity = daily["weighted_intensity"].sum()
    avg_intensity = weighted_intensity / total_seconds

    # --------------------------------------------------
    # CARB MODEL (FROM CONFIG)
    # --------------------------------------------------
    carb_model = model.get("carbohydrates", {})
    bands = carb_model.get("duration_bands", [])

    carbs = None
    for band in bands:
        if avg_hours_per_day <= band["max_hours"]:
            carbs = band["gkg"]
            break

    if carbs is None:
        return None

    # --------------------------------------------------
    # INTENSITY ADJUSTMENT
    # --------------------------------------------------
    adj = carb_model.get("intensity_adjustment", {})

    if avg_intensity > adj.get("high_if", {}).get("threshold", 0.85):
        carbs += adj.get("high_if", {}).get("delta", 0.5)

    elif avg_intensity < adj.get("low_if", {}).get("threshold", 0.65):
        carbs += adj.get("low_if", {}).get("delta", -0.5)

    # --------------------------------------------------
    # CLAMP
    # --------------------------------------------------
    bounds = carb_model.get("bounds", {})
    carbs = max(bounds.get("min", 3.0), min(carbs, bounds.get("max", 10.0)))

    return round(carbs, 2)

def compute_nutrition_demand(context):

    debug(context, "[T3][NUTRITION] Starting demand model")

    model = COACH_PROFILE.get("nutrition_demand_model", {})

    daily = context.get("wellness")

    daily = daily.sort_index().tail(7)
    if daily is None or daily.empty:
        return

    valid_days = daily[
        daily["carbohydrates"].notna() &
        daily["protein"].notna() &
        daily["fatTotal"].notna()
    ]

    if len(valid_days) < 3:
        return

    carb_model = model.get("carbohydrates", {})
    protein_model = model.get("protein", {})
    fat_model = model.get("fat", {})
    load_model = model.get("load_classification", {})

    wellness = context.get("wellness_summary", {}) or {}
    training_state = context.get("training_state", {}) or {}

    ctl = wellness.get("ctl")
    atl = wellness.get("atl")
    fatigue_state = training_state.get("load_recovery_state")

    carbs_req = compute_carb_demand_from_sessions(context, model)
    protein_req = protein_model.get("baseline")

    if fatigue_state in ("adaptation_pressure", "maladaptation_risk"):
        protein_req = protein_model.get("elevated_recovery", protein_req)

    fat_req = fat_model.get("baseline")

    debug(context, f"[T3][NUTRITION] model_keys={list(COACH_PROFILE.keys())}")
    debug(context, f"[T3][NUTRITION] model_loaded={bool(model)}")
    debug(context, f"[T3][NUTRITION] carb_model={carb_model}")


    # --------------------------------------------------
    # Output
    # --------------------------------------------------
    demand = {
        "carbs_gkg_required": carbs_req,
        "protein_gkg_required": protein_req,
        "fat_gkg_target": fat_req,
        "recovery_state": fatigue_state
    }

    context["nutrition_demand"] = demand

    debug(
        context,
        "[T3][NUTRITION] Demand",
        f"carbs={carbs_req}",
        f"protein={protein_req}",
        f"fat={fat_req}"
    )

    return demand

def compute_nutrition_balance(context):

    debug(context, "[T3][NUTRITION] Evaluating balance")

    demand = context.get("nutrition_demand") or {}
    daily = context.get("wellness")

    if daily is None or daily.empty:
        context["nutrition_balance"] = {
            "status": "no_data",
            "confidence": "none"
        }
        return

    daily = daily.sort_index().tail(7) #LIMIT to 7 NOT 42 days

    weight = (context.get("athlete") or {}).get("icu_weight")

    debug(context, f"[T3][NUTRITION] weight={weight}")

    # -----------------------------
    # Validate inputs
    # -----------------------------
    if not demand:
        context["nutrition_balance"] = {
            "status": "unknown",
            "confidence": "none"
        }
        return

    if daily is None or daily.empty:
        context["nutrition_balance"] = {
            "status": "no_data",
            "confidence": "none"
        }
        return

    if weight is None or weight <= 0:
        context["nutrition_balance"] = {
            "status": "invalid_input",
            "confidence": "none"
        }
        return

    # -----------------------------
    # Build valid rolling window (pandas)
    # -----------------------------
    valid_days = daily[
        daily["carbohydrates"].notna() &
        daily["protein"].notna() &
        daily["fatTotal"].notna()
    ]

    debug(context, f"[T3][NUTRITION] total_days={len(daily)}")
    debug(context, f"[T3][NUTRITION] valid_days={len(valid_days)}")

    if valid_days.empty:
        context["nutrition_balance"] = {
            "status": "no_data",
            "confidence": "none"
        }
        return

    window = valid_days.tail(3)

    debug(context, f"[T3][NUTRITION] window_days={len(window)}")

    if len(window) < 3:
        context["nutrition_balance"] = {
            "status": "insufficient_data",
            "confidence": "low"
        }
        return

    # -----------------------------
    # Demand values (no defaults)
    # -----------------------------
    carbs_req = demand.get("carbs_gkg_required")
    protein_req = demand.get("protein_gkg_required")
    fat_req = demand.get("fat_gkg_target")

    if carbs_req is None or protein_req is None:
        context["nutrition_balance"] = {
            "status": "invalid_input",
            "confidence": "none"
        }
        return

    # -----------------------------
    # Rolling averages (g/kg)
    # -----------------------------
    carbs_gkg = window["carbohydrates"].mean() / weight
    protein_gkg = window["protein"].mean() / weight
    fat_gkg = window["fatTotal"].mean() / weight

    carbs_delta = carbs_gkg - carbs_req
    protein_delta = protein_gkg - protein_req
    fat_delta = fat_gkg - fat_req

    # -----------------------------
    # Classification
    # -----------------------------
    status = "balanced"

    if carbs_delta < -3:
        status = "severely_underfuelled"
    elif carbs_delta < -1 or protein_delta < -0.3:
        status = "underfuelled"
    elif carbs_delta > 1.5:
        status = "overfuelled"

    if len(valid_days) >= 5:
        confidence = "high"
    elif len(valid_days) >= 3:
        confidence = "moderate"
    else:
        confidence = "low"

    balance = {
        "carbs_gkg_actual": round(carbs_gkg, 2),
        "protein_gkg_actual": round(protein_gkg, 2),
        "fat_gkg_actual": round(fat_gkg, 2),
        "carbs_delta": round(carbs_delta, 2),
        "protein_delta": round(protein_delta, 2),
        "fat_delta": round(fat_delta, 2),
        "status": status,
        "confidence": confidence
    }

    context["nutrition_balance"] = balance

    debug(context, "[T3][NUTRITION] Balance", f"status={status}", f"conf=moderate")

    return


def interpret_training_state(context):

    # Synthesizes Tier-3 metrics into athlete-facing decisions.

    pi = context.get("performance_intelligence", {})

    # weekly + season compatibility
    if "acute" in pi:
        pi = pi["acute"]
    elif "acute_overlay" in pi:
        pi = pi["acute_overlay"]

    future = context.get("future_forecast", {})
    wellness = context.get("wellness_summary", {})

    phase = (
        context.get("current_phase")
        or context.get("phase_detected")
        or (context.get("phases", [{}])[-1].get("phase") if context.get("phases") else None)
    )

    # --------------------------------------------------
    # Pull signals
    # --------------------------------------------------

    wdrm = (pi.get("anaerobic_repeatability") or {}).get("mean_depletion_pct_7d")
    durability_state = (pi.get("durability") or {}).get("state")
    neural = (pi.get("neural_density") or {}).get("rolling_joules_above_ftp_7d")

    tsb_class = future.get("fatigue_class")
    recovery_index = wellness.get("recovery_index")

    autonomic_ratio = wellness.get("hrv_ratio")
    atl = wellness.get("atl") or wellness.get("ATL")
    ctl = wellness.get("ctl") or wellness.get("CTL")

    # convert Series → scalar if needed
    try:
        if hasattr(atl, "iloc"):
            atl = float(atl.iloc[-1])
        if hasattr(ctl, "iloc"):
            ctl = float(ctl.iloc[-1])
    except Exception:
        pass

    # --------------------------------------------------
    # TSB (hard fatigue signal)
    # --------------------------------------------------

    tsb = None
    try:
        tsb = context.get("tsb") or context.get("TSB") or future.get("tsb")
        if hasattr(tsb, "iloc"):
            tsb = float(tsb.iloc[-1])
        elif tsb is not None:
            tsb = float(tsb)
    except Exception:
        tsb = None

    debug(context, f"[T3-STATE] signals → autonomic={autonomic_ratio}, ATL={atl}, CTL={ctl}, TSB={tsb}")

    # --------------------------------------------------
    # Load vs Recovery detection (TSB governed)
    # --------------------------------------------------

    load_recovery_state = "balanced"
    load_pressure = None

    if atl is not None and ctl is not None:
        load_pressure = atl - ctl

    # --- HARD GOVERNOR (TSB dominates) ---
    if tsb is not None:

        if tsb <= -30:
            load_recovery_state = "maladaptation_risk"

        elif tsb <= -20:
            load_recovery_state = "functional_overreach"

        elif tsb <= -10:
            load_recovery_state = "load_pressure"

        elif tsb >= 10:
            load_recovery_state = "fresh"

    # --- Secondary: autonomic + load interaction ---
    elif autonomic_ratio is not None and load_pressure is not None:

        if load_pressure <= 0:
            load_recovery_state = "balanced"

        elif autonomic_ratio < 0.90 and load_pressure > 10:
            load_recovery_state = "maladaptation_risk"

        elif autonomic_ratio < 0.95 and load_pressure > 5:
            load_recovery_state = "adaptation_pressure"

        elif autonomic_ratio >= 1.05 and load_pressure > 5:
            load_recovery_state = "productive_load"

    # --------------------------------------------------
    # VALIDATION GATE (ACWR + durability)
    # --------------------------------------------------

    acwr = context.get("acwr")

    if load_recovery_state == "maladaptation_risk":

        if (
            acwr is not None and 0.8 <= acwr <= 1.3
            and durability_state in ("stable", "stable_improving")
        ):
            load_recovery_state = "functional_overreach"

    # --------------------------------------------------
    # HRV sanity override
    # --------------------------------------------------

    if autonomic_ratio is not None:

        if autonomic_ratio >= 1.0 and load_recovery_state == "maladaptation_risk":
            load_recovery_state = "functional_overreach"

    # --------------------------------------------------
    # EXTERNAL LOAD CONTEXT (HEAT / ENVIRONMENT)
    # --------------------------------------------------

    external = context.get("performance_intelligence", {}).get("external_load_context", {})

    heat_load = external.get("heat_load_index_7d")
    heat_max = (external.get("exposure") or {}).get("heat_max")
    thermal_source = external.get("thermal_source")

    # --- Heat strain adjustment (ONLY valid external stressor) ---
    heat_flag = False

    if heat_max is not None and heat_max > 1.0:
        heat_flag = True

    elif heat_load is not None and heat_load > 0.8:
        heat_flag = True

    # Apply constraint (does NOT override TSB governor)
    if heat_flag:

        # escalate recovery demand by one level (bounded)
        if load_recovery_state == "productive_load":
            load_recovery_state = "adaptation_pressure"

        elif load_recovery_state == "adaptation_pressure":
            load_recovery_state = "load_pressure"

        # add physiological context
        heat_context_note = True
    else:
        heat_context_note = False

    # --------------------------------------------------
    # Adaptation context
    # --------------------------------------------------

    adapting = "Adaptation signals are stable."

    # Anaerobic signal (still valid)
    if wdrm and wdrm > 0.6:
        adapting = "High anaerobic stimulus detected — adaptation likely but recovery important."

    # Durability (USE STATE — NOT RAW VALUE)

    if durability_state == "drifting":
        adapting = "Durability strain rising — aerobic consolidation advised."

    elif durability_state == "improving":
        adapting = "Efficiency improving under load — strong aerobic adaptation."

    elif durability_state == "stable_improving":
        adapting = "Efficiency stable or improving under load."

    elif durability_state == "stable":
        adapting = "Durability stable — cardiovascular drift controlled."

    # --------------------------------------------------
    # NDLI — intensity density check
    # --------------------------------------------------

    high_intensity_days = (pi.get("neural_density") or {}).get("high_intensity_days_7d")

    if high_intensity_days is not None:

        if high_intensity_days >= 5:

            if load_recovery_state == "functional_overreach":
                load_recovery_state = "adaptation_pressure"

            elif load_recovery_state == "load_pressure":
                load_recovery_state = "adaptation_pressure"

    # --------------------------------------------------
    # Decision Engine
    # --------------------------------------------------

    if load_recovery_state == "maladaptation_risk":

        state_label = "Recovery Deficit"
        readiness = "Recovery is not keeping up with current training load."
        recommendation = "Reduce load and prioritise recovery"
        next_session = "Recovery ride or full rest"

    elif load_recovery_state == "functional_overreach":

        state_label = "High Load"
        readiness = "Training load is very high but still within functional limits."
        recommendation = "Prioritise recovery to absorb load"
        next_session = "Endurance or recovery session"

    elif load_recovery_state == "load_pressure":

        state_label = "Load Pressure"
        readiness = "Training load is high with accumulating fatigue."
        recommendation = "Stabilise load and prioritise recovery"
        next_session = "Endurance or recovery session"

    elif load_recovery_state == "adaptation_pressure":

        state_label = "Adaptation Pressure"
        readiness = "Training load is elevated and approaching recovery limits."
        recommendation = "Hold load and consolidate adaptation"
        next_session = "Moderate endurance or controlled intensity"

    elif load_recovery_state == "productive_load":

        state_label = "Productive Load"
        readiness = "Training load is being absorbed effectively."
        recommendation = "Continue load progression"
        next_session = "Execute planned structured session"

    else:

        state_label = "Stable"
        readiness = "Training load and recovery are balanced."
        recommendation = "Maintain training structure"
        next_session = "Planned structured session"

    # --------------------------------------------------
    # Freshness overlay
    # --------------------------------------------------

    if tsb_class == "overreached" or (recovery_index and recovery_index < 0.8):
        readiness += " Acute fatigue is currently elevated."

    elif tsb_class in ("fresh", "transition"):
        readiness += " Freshness is currently high."

    # --------------------------------------------------
    # HEAT ADJUSTMENT (EXECUTION LAYER — FINAL CONTROL)
    # --------------------------------------------------

    if heat_flag:

        # Highest fatigue state → tighten to full recovery bias
        if load_recovery_state == "maladaptation_risk":

            next_session = "Full rest or very light recovery (heat-adjusted)"

        # Mid states → reduce intensity
        elif load_recovery_state in ("load_pressure", "adaptation_pressure"):

            recommendation = "Prioritise aerobic work and manage heat stress"
            next_session = "Low-intensity aerobic session (heat-adjusted)"

        # Load accepting → constrain progression
        elif load_recovery_state == "productive_load":

            recommendation = "Progress load cautiously due to heat stress"
            next_session = "Controlled endurance or reduced-intensity intervals"

    # --------------------------------------------------
    # HEAT CONTEXT (INTERPRETATION ONLY)
    # --------------------------------------------------

    if heat_context_note:
        readiness += " Environmental heat strain is elevating cardiovascular load."

    # --------------------------------------------------
    # Operational coaching mode (2-state governance)
    # --------------------------------------------------

    operational_state = (
        "recovery_priority"
        if load_recovery_state in ("maladaptation_risk", "adaptation_pressure", "load_pressure")
        else "load_accepting"
    )

    operational_state_context = {
        "framework": "Autonomic–Load Interaction Model",
        "model_basis": "Operational coaching mode derived from autonomic recovery and training load interaction.",
        "signals_used": {
            "hrv_ratio": autonomic_ratio,
            "atl": atl,
            "ctl": ctl,
            "tsb": tsb,
            "load_pressure": load_pressure
        },
        "load_recovery_state": load_recovery_state,
        "operational_state": operational_state,
        "decision_logic": (
            "recovery_priority when fatigue or load exceeds recovery capacity; "
            "load_accepting when athlete is absorbing load effectively"
        )
    }

    context["operational_state"] = operational_state
    context["operational_state_context"] = operational_state_context

    debug(context, f"[T3-STATE] operational_state → {operational_state}")

    # --------------------------------------------------
    # Confidence
    # --------------------------------------------------

    confidence = "moderate"
    if tsb_class and recovery_index:
        confidence = "high"

    return {
        "state_label": state_label,
        "readiness": readiness,
        "adaptation": adapting,
        "recommendation": recommendation,
        "next_session": next_session,
        "confidence": confidence,
        "phase_context": phase,
        "signals": {
            "hrv_ratio": autonomic_ratio,
            "atl": atl,
            "ctl": ctl,
            "tsb": tsb
        },
        "load_recovery_state": load_recovery_state,
        "operational_state": operational_state,
        "operational_state_context": operational_state_context
    }


def compute_external_load_context(context, df_full):
    """
    Tier-3 — External Load Context (SCIENCE-ALIGNED)

    Purpose:
        Quantify TRUE external environmental stress (heat),
        while treating terrain as contextual (not load).

    Principles:
        - Heat = independent physiological stressor (validated)
        - Terrain = already captured in power/load → NOT a load metric
        - Efficiency drift = bridge between external → internal response

    Heat is the only independent environmental stressor here; above ~18 °C cardiovascular strain rises and above ~23 °C performance degradation becomes significant (Cheuvront & Kenefick).
    Elevation/terrain does not add separate “load” because its metabolic cost is already captured in power/TSS; treating it as additional load double-counts stress.
    Terrain instead acts as a **modifier**, influencing internal response (e.g., HR–power decoupling, efficiency drift), not external load itself.
    The correct model is therefore: **heat = external load driver**, **terrain = contextual constraint**, **efficiency/HR response = physiological mediator of both**.

    Output:
        context["performance_intelligence"]["external_load_context"]
    """

    if df_full is None or getattr(df_full, "empty", True):
        return {}

    # --------------------------------------------------
    # SAFE NUMERIC EXTRACTION
    # --------------------------------------------------

    def _num(series):
        return pd.to_numeric(series, errors="coerce") if series is not None else None

    altitude_gain = _num(df_full.get("total_elevation_gain"))
    distance = _num(df_full.get("distance"))
    moving_time = _num(df_full.get("moving_time"))
    power = _num(df_full.get("average_watts"))
    hr = _num(df_full.get("average_heartrate"))
    temp = _num(df_full.get("average_temp"))

    if temp is None:
        temp = _num(df_full.get("temperature"))

    # --------------------------------------------------
    # DERIVED CONTEXT SIGNALS (NOT LOAD)
    # --------------------------------------------------

    # --- Terrain context (m/km) ---
    terrain_index = None
    if altitude_gain is not None and distance is not None:
        with np.errstate(divide="ignore", invalid="ignore"):
            terrain_index = altitude_gain / (distance / 1000.0)
        terrain_index = terrain_index.replace([np.inf, -np.inf], np.nan)

    # --- VAM (m/h) ---
    vam = None
    if altitude_gain is not None and moving_time is not None:
        with np.errstate(divide="ignore", invalid="ignore"):
            vam = altitude_gain / (moving_time / 3600.0)

    # --------------------------------------------------
    # THERMAL SIGNAL RESOLUTION (SCIENCE-ALIGNED)
    # --------------------------------------------------

    def resolve_thermal_signal(df):

        # --------------------------------------------------
        # 1. HEAT TRAINING LOAD (PRIMARY SIGNAL)
        # --------------------------------------------------
        heat_training = _num(df.get("HeatTrainingLoad"))

        if heat_training is not None and heat_training.notna().any():
            return {
                "series": heat_training.clip(0, 2),
                "source": "heat_training_load",
                "confidence": "high",
                "max": float(np.nanmax(heat_training))
            }

        # --------------------------------------------------
        # 2. HEAT STRAIN INDEX (fallback)
        # --------------------------------------------------
        heat_strain = _num(df.get("heat_strain_index"))

        if heat_strain is not None and heat_strain.notna().any():
            return {
                "series": heat_strain.clip(0, 2),
                "source": "heat_strain",
                "confidence": "medium",
                "max": float(np.nanmax(heat_strain))
            }

        # --------------------------------------------------
        # 3. AMBIENT TEMP (last fallback)
        # --------------------------------------------------
        if temp is not None and temp.notna().any():

            series = ((temp - 18.0) / (23.0 - 18.0)).clip(lower=0, upper=2)

            return {
                "series": series,
                "source": "ambient_temp",
                "confidence": "contextual",
                "max": float(np.nanmax(series))
            }

        return None

    thermal = resolve_thermal_signal(df_full)

    heat_index = None
    thermal_source = None
    thermal_confidence = None
    heat_max = None

    if thermal:
        heat_index = thermal["series"]
        thermal_source = thermal["source"]
        thermal_confidence = thermal["confidence"]
        heat_max = thermal["max"]

    # --------------------------------------------------
    # INTERNAL RESPONSE LINK (EFFICIENCY DRIFT)
    # --------------------------------------------------

    efficiency_dev = None

    if power is not None and hr is not None:
        with np.errstate(divide="ignore", invalid="ignore"):
            efficiency = power / hr.replace(0, np.nan)

        if isinstance(efficiency, pd.Series):
            baseline = efficiency.rolling(5, min_periods=2).mean()
            efficiency_dev = efficiency - baseline

    # --------------------------------------------------
    # AGGREGATION (7D)
    # --------------------------------------------------

    def _safe_mean(x):
        if x is None:
            return None

        arr = np.asarray(x)

        if arr.size == 0 or np.isnan(arr).all():
            return None

        return float(np.nanmean(arr))

    heat_load = _safe_mean(heat_index)
    terrain_mean = _safe_mean(terrain_index)
    vam_mean = _safe_mean(vam)
    efficiency_bias = _safe_mean(efficiency_dev)

    # --------------------------------------------------
    # EXPOSURE (CRITICAL — DO NOT AVERAGE AWAY)
    # --------------------------------------------------

    def _safe_max(x):
        if x is None:
            return None

        arr = np.asarray(x)

        if arr.size == 0 or np.isnan(arr).all():
            return None

        return float(np.nanmax(arr))
    terrain_max = _safe_max(terrain_index)
    vam_max = _safe_max(vam)

    # --------------------------------------------------
    # NORMALISED HEAT LOAD (ONLY TRUE LOAD)
    # --------------------------------------------------

    def _scale(val, low, high):
        if val is None:
            return None
        return float(np.clip((val - low) / (high - low), 0, 2))

    # heat_index already scaled 0–2, but stabilise
    heat_score = _scale(heat_load, 0, 1.0)

    # --------------------------------------------------
    # CLASSIFICATION
    # --------------------------------------------------

    def _classify(v):
        if v is None:
            return "unknown"
        if v < 0.5:
            return "low"
        elif v < 1.0:
            return "moderate"
        else:
            return "high"

    classification = _classify(heat_score)

    # --------------------------------------------------
    # MODIFIERS (EXPOSURE-DRIVEN)
    # --------------------------------------------------

    modifiers = {}

    # Heat-driven cardiovascular strain (use exposure, not mean)
    if heat_max is not None and heat_max > 1.0:
        modifiers["cardiovascular_drift"] = "heat_induced"

    # Terrain only matters if it alters physiology
    if terrain_max is not None and terrain_max > 20:
        if efficiency_bias is not None and efficiency_bias < -5:
            modifiers["efficiency_bias"] = "terrain_induced"

    # Combined stress signal
    if (
        heat_max is not None and heat_max > 1.0 and
        efficiency_bias is not None and efficiency_bias < -5
    ):
        modifiers["combined_stress"] = "heat_and_terrain"


    # --------------------------------------------------
    # DOMINANT STRESSOR (EXPOSURE FIRST)
    # --------------------------------------------------

    dominant = None

    if heat_max is not None and heat_max > 1.0:
        dominant = "acute_heat"

    elif heat_score is not None:
        dominant = "heat"

    # --------------------------------------------------
    # FINAL BLOCK
    # --------------------------------------------------

    def _r(val):
        return round(val, 2) if val is not None else None

    block = {
        # --------------------------------------------------
        # TRUE external load (thermal only)
        # --------------------------------------------------
        "env_load_index_7d": _r(heat_score),
        "heat_load_index_7d": _r(heat_score),

        # --------------------------------------------------
        # THERMAL SOURCE (CRITICAL FOR INTERPRETATION)
        # --------------------------------------------------
        "thermal_source": thermal_source,                 
        "thermal_source_confidence": thermal_confidence,  

        # --------------------------------------------------
        # EXPOSURE (DO NOT AVERAGE AWAY)
        # --------------------------------------------------
        "exposure": {
            "terrain_max": _r(terrain_max),
            "heat_max": _r(heat_max),
            "session_avg_vam_max": _r(vam_max)
        },

        # --------------------------------------------------
        # CONTEXT (NOT LOAD)
        # --------------------------------------------------
        "terrain_context_7d": _r(terrain_mean),
        "vam_mean_7d": _r(vam_mean),

        # --------------------------------------------------
        # INTERPRETATION
        # --------------------------------------------------
        "dominant_stressor": dominant,
        "classification": classification,

        # --------------------------------------------------
        # PHYSIOLOGICAL MODIFIERS
        # --------------------------------------------------
        "modifiers": modifiers,

        # --------------------------------------------------
        # META
        # --------------------------------------------------
        "confidence": thermal_confidence or "contextual",
        "context_window": "7d"
    }

    # attach safely
    pi = context.setdefault("performance_intelligence", {})
    pi["external_load_context"] = block

    return block

# ===========================================================
# Utilities
# ===========================================================

def _safe_sum(series):
    if series is None:
        return None
    return float(series.fillna(0).sum())


def _safe_mean(series):
    if series is None or series.dropna().empty:
        return None
    return float(series.mean())


def _safe_max(series):
    if series is None or series.dropna().empty:
        return None
    return float(series.max())


def _safe_count(series, threshold):
    if series is None:
        return None
    return int((series >= threshold).sum())


def _empty_weekly():
    return {
        "anaerobic_repeatability": {},
        "model_diagnostics": {},
        "durability": {},
        "neural_density": {}
    }


def _empty_season():
    return {
        "chronic_state": None,
        "acute_overlay": None
    }
