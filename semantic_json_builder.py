"""
semantic_json_builder.py
------------------------

Builds a FULL semantic DICT coaching graph based on the Unified Reporting
Framework v5.1, Coaching Profile, Coaching Cheat Sheet, and all Tier-2 modules.

Includes:
 - Authoritative totals
 - Derived metrics
 - Extended metrics
 - Adaptation metrics
 - Trend metrics
 - Correlations
 - Wellness (sanitised)
 - Thresholds / interpretations / coaching links
 - Actions
 - Phase detection
 - Event previews (stable)
 - Daily load summaries
"""

import json
from datetime import datetime, date, timezone
import pandas as pd
from math import isnan
from coaching_cheat_sheet import CHEAT_SHEET
from coaching_profile import COACH_PROFILE, REPORT_HEADERS, REPORT_RESOLUTION
from audit_core.utils import debug
import numpy as np
from math import isnan
import pytz
from audit_core.tier2_derived_metrics import classify_marker

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def handle_missing_data(value, default_value=None):
    """Convert NaN or None → safe default."""
    if value is None:
        return default_value
    if isinstance(value, float) and isnan(value):
        return default_value
    return value


def convert_to_str(value):
    """Convert datetime/Timestamp/date → ISO string."""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return value


def semantic_block_for_metric(name, value, context):
    """Builds semantic envelope for a single metric."""
    thresholds = CHEAT_SHEET["thresholds"].get(name, {})
    interpretation = CHEAT_SHEET["context"].get(name)
    coaching_link = CHEAT_SHEET["coaching_links"].get(name)
    profile_desc = COACH_PROFILE["markers"].get(name, {})

    classification = None
    if thresholds:
        try:
            green = thresholds.get("green")
            amber = thresholds.get("amber")

            if green and green[0] <= float(value) <= green[1]:
                classification = "green"
            elif amber and amber[0] <= float(value) <= amber[1]:
                classification = "amber"
            else:
                classification = "red"
        except Exception:
            classification = "unknown"

    return {
        "name": name,
        "value": convert_to_str(value),
        "framework": profile_desc.get("framework") or "Unknown",
        "formula": profile_desc.get("formula"),
        "thresholds": thresholds,
        "classification": classification,
        "interpretation": interpretation,
        "coaching_implication": coaching_link,
        "related_metrics": profile_desc.get("criteria", {}),
    }

# ---------------------------------------------------------
# Insights Builder
# ---------------------------------------------------------

def build_insights(semantic):
    """
    Build high-level coaching insights using canonical thresholds
    from Coaching Cheat Sheet + Coaching Profile.
    """
    insights = {}
    report_type = semantic.get("meta", {}).get("report_type")
    window = "90d" if report_type in ("season", "summary") else "7d"
    polarisation_window = "7d"

    # --- Fatigue Trend ---
    atl = (
        semantic.get("extended_metrics", {}).get("ATL", {}).get("value")
        or semantic.get("wellness", {}).get("ATL")
    )
    ctl = (
        semantic.get("extended_metrics", {}).get("CTL", {}).get("value")
        or semantic.get("wellness", {}).get("CTL")
    )
    ft = None
    if isinstance(atl, (int, float)) and isinstance(ctl, (int, float)) and ctl > 0:
        ft = round(((atl - ctl) / ctl) * 100, 1)

    fatigue_block = semantic_block_for_metric("FatigueTrend", ft, semantic)
    insights["fatigue_trend"] = {
        "value_pct": ft,
        "window": window,
        "basis": "ATL vs CTL",
        "classification": fatigue_block.get("classification"),
        "thresholds": fatigue_block.get("thresholds"),
        "interpretation": fatigue_block.get("interpretation"),
        "coaching_implication": fatigue_block.get("coaching_implication"),
    }

    # --- Polarisation ---
    zones = semantic.get("zones", {}).get("power", {}) or {}
    dist = zones.get("distribution", zones)
    z1 = dist.get("power_z1", 0)
    z2 = dist.get("power_z2", 0)
    z3plus = sum(v for k, v in dist.items()
                 if k not in ("power_z1", "power_z2") and isinstance(v, (int, float)))
    pol_val = round((z1 + z2) / (z1 + z2 + z3plus + 1e-6), 3)
    pol_block = semantic_block_for_metric("Polarisation", pol_val, semantic)
    insights["load_distribution"] = {
        "zones_pct": {"z1_z2": round(z1 + z2, 1), "z3_plus": round(z3plus, 1)},
        "window": polarisation_window,
        "basis": "time-in-zone (%)",
        "classification": pol_block.get("classification"),
        "interpretation": pol_block.get("interpretation"),
        "coaching_implication": pol_block.get("coaching_implication"),
    }

    # --- Metabolic Drift (FOxI proxy) ---
    foxi = semantic.get("metrics", {}).get("FOxI", {}).get("value")
    drift = None
    if isinstance(foxi, (int, float)):
        drift = round((70 - foxi) / 70, 3)
    drift_block = semantic_block_for_metric("FOxI", foxi, semantic)
    insights["metabolic_drift"] = {
        "value": drift,
        "window": window,
        "basis": "FOxI proxy",
        "classification": drift_block.get("classification"),
        "interpretation": drift_block.get("interpretation"),
        "coaching_implication": drift_block.get("coaching_implication"),
    }

    # --- Fitness Phase (ACWR classification) ---
    acwr_val = semantic.get("metrics", {}).get("ACWR", {}).get("value")
    acwr_block = semantic_block_for_metric("ACWR", acwr_val, semantic)
    insights["fitness_phase"] = {
        "phase": acwr_block.get("classification"),
        "basis": "ACWR",
        "window": "rolling",
        "interpretation": acwr_block.get("interpretation"),
        "coaching_implication": acwr_block.get("coaching_implication"),
    }

    return insights



# ---------------------------------------------------------
# MAIN BUILDER
# ---------------------------------------------------------

def build_semantic_json(context):
    """Build the final semantic graph."""
    # -----------------------------------------------------------------
    # 🔧 Read render options from context (if provided)
    # -----------------------------------------------------------------
    options = context.get("render_options", {})
    verbose_events = bool(options.get("verbose_events", True))
    include_all_events = bool(options.get("include_all_events", True))
    return_format = options.get("return_format", "semantic")
    render_mode = options.get("render_mode", "default")  # ✅ new line

    # Prefer the preserved full dataset for events
    if "_df_scope_full" in context and isinstance(context["_df_scope_full"], pd.DataFrame):
        df_full = context["_df_scope_full"]
        debug(context, f"[SEMANTIC-FORCE] Using preserved _df_scope_full ({len(df_full)} rows, {len(df_full.columns)} cols)")
    elif "df_scope" in context and isinstance(context["df_scope"], pd.DataFrame):
        df_full = context["df_scope"]
        debug(context, f"[SEMANTIC-FORCE] Using df_scope ({len(df_full)} rows, {len(df_full.columns)} cols)")
    else:
        df_full = context.get("df_events", pd.DataFrame())
        debug(context, f"[SEMANTIC-FORCE] Fallback to df_events ({len(df_full)} rows)")

    # ------------------------------------------------------------------
    # 🧬 Lactate, HRV and Threshold Integration (Cheat-Sheet aligned)
    # ------------------------------------------------------------------
    try:
        lactate_profile = COACH_PROFILE.get("markers", {}).get("Lactate", {})
        lac_defaults = CHEAT_SHEET.get("thresholds", {}).get("Lactate", {})

        lt1_default = (
            lactate_profile.get("criteria", {}).get("lt1_mmol")
            or lac_defaults.get("lt1_mmol")
            or 2.0
        )
        lt2_default = (
            lactate_profile.get("criteria", {}).get("lt2_mmol")
            or lac_defaults.get("lt2_mmol")
            or 4.0
        )
        corr_threshold = lac_defaults.get("corr_threshold") or 0.6

        lactate_notes = (
            CHEAT_SHEET.get("context", {}).get("Lactate")
            or lactate_profile.get("interpretation", "")
            or "Lactate thresholds derived from profile."
        )

        hrv_profile = COACH_PROFILE.get("markers", {}).get("HRV", {})
        hrv_defaults = CHEAT_SHEET.get("thresholds", {}).get("HRV", {})

        hrv_optimal = (
            hrv_profile.get("criteria", {}).get("optimal")
            or hrv_defaults.get("optimal")
            or [60, 90]
        )
        hrv_low = (
            hrv_profile.get("criteria", {}).get("low")
            or hrv_defaults.get("low")
            or [0, 40]
        )

        semantic["lactate_defaults"] = {
            "lt1_mmol": lt1_default,
            "lt2_mmol": lt2_default,
            "corr_threshold": corr_threshold,
            "notes": lactate_notes,
        }
        semantic["hrv_defaults"] = {
            "optimal": hrv_optimal,
            "low": hrv_low,
        }

        debug(context, f"[SEMANTIC] Lactate defaults → LT1={lt1_default}, LT2={lt2_default}, corr>={corr_threshold}")
        debug(context, f"[SEMANTIC] HRV defaults → optimal={hrv_optimal}, low={hrv_low}")

    except Exception as e:
        debug(context, f"[SEMANTIC] ⚠️ Lactate/HRV threshold integration failed: {e}")

    # --- Safe defaults for undefined zone variables ---
    corr = context.get("zones_corr")
    zones_source = context.get("zones_source", "ftp_based")
    zones_reason = context.get("zones_reason", "unknown")
    lactate_thresholds_dict = context.get("lactate_thresholds_dict", {})

    # --- Compute confidence & method
    confidence = (
        round(corr, 3)
        if isinstance(corr, (int, float)) and not pd.isna(corr)
        else None
    )
    method = "physiological" if zones_source == "lactate_test" else "ftp_based"

    # ------------------------------------------------------------------
    # 🧭 Phase Detection (Base → Build → Peak → Taper → Recovery)
    # ------------------------------------------------------------------
    try:
        from audit_core.tier2_actions import detect_phases
        if not context.get("phases"):
            events = context.get("activities_full") or context.get("df_events") or []
            if isinstance(events, pd.DataFrame):
                events = events.to_dict(orient="records")
            context = detect_phases(context, events)
            debug(context, f"[SEMANTIC] Injected detected phases → {len(context.get('phases', []))}")
    except Exception as e:
        debug(context, f"[SEMANTIC] ⚠️ Phase detection failed: {e}")

    # ---------------------------------------------------------
    # BASE SEMANTIC STRUCTURE
    # ---------------------------------------------------------
    semantic = {
        "meta": {
            "framework": "Unified Reporting Framework v5.1",
            "version": "v16.17",
            "generated_at": {
                "local": (
                    datetime.now(
                        pytz.timezone(context.get("timezone", "UTC"))
                        if context.get("timezone") else pytz.UTC
                    ).replace(microsecond=0).isoformat()
                ),
            },
            "report_type": context.get("report_type"),
            "period": {
                "start": context.get("period", {}).get("start"),
                "end": context.get("period", {}).get("end"),
            },
            "timezone": context.get("timezone"),
            "athlete": {"identity": {}, "profile": {}},
            "report_header": {
                "title": None,
                "scope": None,
                "data_sources": None,
                "intended_use": None,
            },
        },

        "metrics": {},
        "extended_metrics": {},
        "adaptation_metrics": {},
        "trend_metrics": {},
        "correlation_metrics": {},

        # ---------------------------------------------------------
        # 🔬 Zones — Power, HR, Pace + Calibration Metadata
        # ---------------------------------------------------------
        "zones": {
            "power": {
                "distribution": context.get("zone_dist_power", {}),
                "thresholds": (
                    context.get("icu_power_zones")
                    or context.get("athlete_power_zones")
                    or []
                ),
            },
            "hr": {
                "distribution": context.get("zone_dist_hr", {}),
                "thresholds": (
                    context.get("icu_hr_zones")
                    or context.get("athlete_hr_zones")
                    or []
                ),
            },
            "pace": {
                "distribution": context.get("zone_dist_pace", {}),
                "thresholds": context.get("icu_pace_zones") or [],
            },
            "calibration": {
                "source": zones_source,
                "method": method,
                "confidence": confidence,
                "reason": zones_reason,
                "lactate_thresholds": lactate_thresholds_dict,
            },
        },

        # ---------------------------------------------------------
        # DAILY LOAD
        # ---------------------------------------------------------
        "daily_load": [
            {"date": row["date"], "tss": float(row["icu_training_load"])}
            for _, row in getattr(context.get("df_daily"), "iterrows", lambda: [])()
        ] if context.get("df_daily") is not None else [],

        "events": [],
        "phases": context.get("phases", []),
    }

    # --- Derive report period and meta window ---
    report_type = context.get("report_type", "weekly").lower()
    df_ref = None

    # --- Select dataset based on report type ---
    if report_type in ("season", "summary"):
        df_light = context.get("df_light")
        if isinstance(df_light, pd.DataFrame) and not df_light.empty:
            df_ref = df_light
        else:
            acts_light = context.get("activities_light")
            if isinstance(acts_light, list) and len(acts_light) > 0:
                df_ref = pd.DataFrame(acts_light)

    elif report_type == "wellness":
        df_well = context.get("df_wellness")
        if isinstance(df_well, pd.DataFrame) and not df_well.empty:
            df_ref = df_well
        else:
            acts_well = context.get("wellness")
            if isinstance(acts_well, list) and len(acts_well) > 0:
                df_ref = pd.DataFrame(acts_well)

    else:
        df_master = context.get("df_master")
        if isinstance(df_master, pd.DataFrame) and not df_master.empty:
            df_ref = df_master
        else:
            acts_full = context.get("activities_full")
            if isinstance(acts_full, list) and len(acts_full) > 0:
                df_ref = pd.DataFrame(acts_full)

    # --- Fallback: preserved df_scope_full (Railway safe)
    if df_ref is None and "_df_scope_full" in context and isinstance(context["_df_scope_full"], pd.DataFrame):
        df_ref = context["_df_scope_full"]

    # --- Compute report period from reference dataset ---
    if isinstance(df_ref, pd.DataFrame) and not df_ref.empty:
        date_col = "date" if "date" in df_ref.columns else "start_date_local" if "start_date_local" in df_ref.columns else df_ref.columns[0]
        start_date = pd.to_datetime(df_ref[date_col], errors="coerce").min().strftime("%Y-%m-%d")
        end_date = pd.to_datetime(df_ref[date_col], errors="coerce").max().strftime("%Y-%m-%d")
        context["period"] = {"start": start_date, "end": end_date}
        debug(context, f"[SEMANTIC-FIX] Derived period from {report_type} dataset → {start_date} → {end_date}")
    else:
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        context["period"] = {"start": start_date.strftime("%Y-%m-%d"), "end": end_date.strftime("%Y-%m-%d")}
        debug(context, "[SEMANTIC-FIX] Could not derive period — defaulted to last 7 days")

    # --- Enrich meta block with descriptive scope ---
    semantic.setdefault("meta", {})
    window_days = (pd.to_datetime(context["period"]["end"]) - pd.to_datetime(context["period"]["start"])).days

    scope_map = {
        "weekly": "Short-term microcycle — acute load and fatigue balance",
        "season": "Medium-term fitness, fatigue and progression trends",
        "summary": "Annual review of training load, adaptation and performance",
        "wellness": "6-week rolling recovery and readiness snapshot",
    }

    semantic["meta"]["report_type"] = report_type
    semantic["meta"]["window_days"] = window_days
    semantic["meta"]["period"] = f"{context['period']['start']} → {context['period']['end']}"
    semantic["meta"]["scope"] = scope_map.get(report_type, "Custom analysis window")
    semantic["meta"]["data_sources"] = (
        f"{window_days}-day light activities, "
        f"{'42-day wellness' if report_type != 'wellness' else 'wellness only'}"
    )

    
    # ---------------------------------------------------------
    # WELLNESS BLOCK
    # ---------------------------------------------------------
    semantic["wellness"] = {
        k: handle_missing_data(v, None)
        for k, v in context.get("wellness_summary", {}).items()
    }

    # 🩵 Inject HRV summary & 42-day series
    if "df_wellness" in context and not getattr(context["df_wellness"], "empty", True):
        dfw = context["df_wellness"]
        if "hrv" in dfw.columns:
            vals = pd.to_numeric(dfw["hrv"], errors="coerce").dropna()
            if len(vals) > 0:
                mean_val = round(vals.mean(), 1)
                latest_val = round(vals.iloc[-1], 1)
                trend_val = (
                    round(vals.tail(7).mean() - vals.head(7).mean(), 1)
                    if len(vals) >= 14 else None
                )

                semantic["wellness"].update({
                    "hrv_mean": mean_val,
                    "hrv_latest": latest_val,
                    "hrv_trend_7d": trend_val,
                    "hrv_source": context.get("hrv_source", "unknown"),
                    "hrv_available": True,
                    "hrv_samples": int(len(vals)),
                    "hrv_series": dfw.tail(42)[["date", "hrv"]]
                        .dropna()
                        .assign(date=lambda x: pd.to_datetime(x["date"]).dt.strftime("%Y-%m-%d"))
                        .to_dict(orient="records"),
                })
                debug(
                    context,
                    f"[SEMANTIC] Injected HRV → mean={mean_val}, latest={latest_val}, "
                    f"trend_7d={trend_val}, samples={len(vals)}, source={context.get('hrv_source')}"
                )

    # ---------------------------------------------------------
    # 🧹 Remove subjective fields from the top-level wellness
    # ---------------------------------------------------------
    for k in ["recovery", "fatigue", "fitness", "form"]:
        semantic["wellness"].pop(k, None)

    # ---------------------------------------------------------
    # 🧠 Wrap subjective markers (and clean nulls)
    # ---------------------------------------------------------
    subjective_fields = ["recovery", "fatigue", "fitness", "form"]
    subjective_block = {}
    for k, v in context.get("wellness_summary", {}).items():
        if (
            k in subjective_fields
            and not (
                v is None
                or (isinstance(v, (float, int)) and pd.isna(v))
                or (isinstance(v, (list, dict, np.ndarray)) and len(v) == 0)
                or v == ""
            )
        ):
            subjective_block[k] = v

    # ✅ Always preserve key for schema consistency
    semantic["wellness"]["subjective"] = subjective_block or {}

    debug(
        context,
        f"[SEMANTIC] Wellness subjective markers → keys={list(semantic['wellness']['subjective'].keys())}"
    )


    # ---------------------------------------------------------
    # AUTHORITATIVE TOTALS (Tier-2 ONLY)
    # ---------------------------------------------------------
    report_type = semantic["meta"]["report_type"]

    if report_type in ("season", "summary"):
        semantic["hours"] = handle_missing_data(context.get("locked_totalHours"), 0)
        semantic["tss"] = handle_missing_data(context.get("locked_totalTss"), 0)
        semantic["distance_km"] = handle_missing_data(context.get("locked_totalDistance"), 0)

    else:  # weekly
        semantic["hours"] = handle_missing_data(context.get("totalHours"), 0)
        semantic["tss"] = handle_missing_data(context.get("totalTss"), 0)
        semantic["distance_km"] = handle_missing_data(context.get("totalDistance"), 0)


    # ---------------------------------------------------------
    # AUTHORITATIVE Tier-2 metric injection
    # ---------------------------------------------------------
    for k in (
        "extended_metrics",
        "adaptation_metrics",
        "trend_metrics",
        "correlation_metrics",
    ):
        if isinstance(context.get(k), dict) and context[k]:
            semantic[k] = context[k]
        else:
            semantic[k] = {}

    # ---------------------------------------------------------
    # 🧪 Lactate Measurement & Personalized Endurance Zone (from derived metrics)
    # ---------------------------------------------------------
    semantic.setdefault("extended_metrics", {})

    # --- Lactate summary injection
    if "lactate_summary" in context and context["lactate_summary"]:
        semantic["extended_metrics"]["lactate"] = context["lactate_summary"]
        debug(
            context,
            f"[SEMANTIC] Injected lactate_summary → mean={context['lactate_summary'].get('mean')}, "
            f"latest={context['lactate_summary'].get('latest')}, "
            f"samples={context['lactate_summary'].get('samples')}"
        )
    else:
        debug(context, "[SEMANTIC] No lactate_summary available in context")

    # --- Personalized endurance zone (Z2)
    if "personalized_z2" in context and context["personalized_z2"]:
        semantic["extended_metrics"]["personalized_z2"] = context["personalized_z2"]
        debug(
            context,
            f"[SEMANTIC] Injected personalized_z2 → "
            f"{context['personalized_z2'].get('start_w')}–{context['personalized_z2'].get('end_w')}W "
            f"({context['personalized_z2'].get('start_pct')}–{context['personalized_z2'].get('end_pct')}%), "
            f"method={context['personalized_z2'].get('method')}"
        )
    else:
        debug(context, "[SEMANTIC] No personalized_z2 data available in context")

    # ---------------------------------------------------------
    # 🔗 ATHLETE: identity + profile + context (UNIVERSAL)
    # ---------------------------------------------------------
    athlete = context.get("athlete_raw") or context.get("athlete") or {}
    sports = athlete.get("sportSettings", []) or []
    primary_sport = sports[0] if sports else {}

    # -----------------------------------------------------
    # ⚙️ PROFILE (CORE PERFORMANCE MARKERS)
    # -----------------------------------------------------
    ftp = None
    eftp = None
    lthr = None

    if isinstance(primary_sport, dict):
        ftp = primary_sport.get("ftp")
        mmp_model = primary_sport.get("mmp_model", {}) or {}
        eftp = mmp_model.get("ftp")
        lthr = primary_sport.get("lthr")

    # Fallbacks
    ftp = ftp or athlete.get("icu_ftp")
    eftp = eftp or ftp
    lthr = lthr or athlete.get("icu_threshold_hr")

    # --- Resolve max HR from primary sport if not on root
    max_hr = athlete.get("max_hr")
    if not max_hr and isinstance(primary_sport, dict):
        max_hr = primary_sport.get("max_hr")

    # --- Custom physiological fields (now pulled from sportSettings)
    custom_fields = {}
    if isinstance(primary_sport, dict):
        custom_fields = primary_sport.get("custom_field_values", {}) or {}

    vo2max_garmin = custom_fields.get("VO2MaxGarmin")
    lactate_mmol_l = custom_fields.get("HRTLNDLT1")

    # -----------------------------------------------------
    # BUILD SEMANTIC BLOCK
    # -----------------------------------------------------
    semantic["meta"]["athlete"] = {
        # -----------------------------------------------------
        # 🪪 IDENTITY
        # -----------------------------------------------------
        "identity": {
            "id": athlete.get("id"),
            "name": athlete.get("name") or f"{athlete.get('firstname', '')} {athlete.get('lastname', '')}".strip(),
            "firstname": athlete.get("firstname"),
            "lastname": athlete.get("lastname"),
            "sex": athlete.get("sex"),
            "dob": athlete.get("icu_date_of_birth"),
            "country": athlete.get("country"),
            "city": athlete.get("city"),
            "timezone": athlete.get("timezone"),
            "profile_image": athlete.get("profile_medium"),
        },

        # -----------------------------------------------------
        # ⚙️ PROFILE (CORE PERFORMANCE MARKERS)
        # -----------------------------------------------------
        "profile": {
            "ftp": ftp,
            "eftp": eftp,
            "ftp_kg": (
                round((ftp or 0) / athlete.get("icu_weight", 1), 2)
                if ftp and athlete.get("icu_weight") else None
            ),
            "weight": athlete.get("icu_weight"),
            "height": athlete.get("height"),
            "lthr": lthr,
            "resting_hr": athlete.get("icu_resting_hr"),
            "max_hr": max_hr,
            "primary_sport": ",".join(primary_sport.get("types", [])) if isinstance(primary_sport, dict) else None,
            # --- Extended physiological fields from custom_field_values
            "vo2max_garmin": vo2max_garmin,
            "lactate_mmol_l": lactate_mmol_l,
            "custom_metrics": custom_fields if custom_fields else None,
        },
    
        # -----------------------------------------------------
        # 🧠 CONTEXT (FOR CHATGPT INTENT ANALYSIS)
        # -----------------------------------------------------
        "context": {
            "platforms": {
                "garmin": athlete.get("icu_garmin_training"),
                "zwift": athlete.get("zwift_sync_activities"),
                "wahoo": athlete.get("wahoo_sync_activities"),
                "strava": athlete.get("strava_sync_activities"),
                "polar": athlete.get("polar_sync_activities"),
                "suunto": athlete.get("suunto_sync_activities"),
                "coros": athlete.get("coros_sync_activities"),
                "concept2": athlete.get("concept2_sync_activities"),
            },
            "wellness_features": {
                "sources": {
                    "garmin": bool(athlete.get("icu_garmin_health")),
                    "whoop": bool(athlete.get("whoop_sync_activities")),
                    "oura": bool(athlete.get("oura_sync_activities")),
                    "fitbit": bool(athlete.get("fitbit_sync_activities")),
                    "polar": bool(athlete.get("polar_sync_activities")),
                    "coros": bool(athlete.get("coros_sync_activities")),
                    "suunto": bool(athlete.get("suunto_sync_activities")),
                },
                "wellness_keys": (
                    athlete.get("icu_garmin_wellness_keys")
                    or athlete.get("wellness_keys")
                    or context.get("wellness_keys")
                    or []
                ),
                "hrv_available": bool(context.get("hrv_available", False)),
                "hrv_source": context.get("hrv_source", "unknown"),
                "weight_sync": athlete.get("icu_weight_sync") or "NONE",
                "resting_hr": athlete.get("icu_resting_hr"),
            },
            "training_environment": {
                "plan": athlete.get("plan"),
                "beta_user": athlete.get("beta_user"),
                "coach_access": athlete.get("icu_coach"),
                "language": athlete.get("locale"),
                "timezone": athlete.get("timezone"),
            },
            "equipment_summary": {
                "bike_count": len(athlete.get("bikes", [])),
                "shoe_count": len(athlete.get("shoes", [])),
                "primary_bike": next(
                    (b.get("name") for b in athlete.get("bikes", []) if b.get("primary")), None
                ),
                "total_bike_distance_km": sum(
                    (b.get("distance", 0) or 0) / 1000 for b in athlete.get("bikes", [])
                ),
            },
            "activity_scope": {
                "primary_sports": [s.get("types", []) for s in athlete.get("sportSettings", [])],
                "active_since": athlete.get("icu_activated"),
                "last_seen": athlete.get("icu_last_seen"),
            },
        },
    }


    # ---------------------------------------------------------
    # EVENTS (canonical)
    # ---------------------------------------------------------
    df_events = context["_df_scope_full"]

    if isinstance(df_events, pd.DataFrame) and not df_events.empty:
        debug(context, f"[DEBUG-EVENTS] sample type={type(df_events)} rows={len(df_events)} cols_sample={str(list(df_events.columns))[:100]}")

        core_fields = [
            "start_date_local", "name", "type",
            "distance", "moving_time", "icu_training_load", "IF",
            "average_heartrate", "average_cadence", "icu_average_watts",
            "strain_score", "trimp", "hr_load",
            "icu_efficiency_factor", "icu_intensity", "icu_power_hr",
            "decoupling", "icu_pm_w_prime", "icu_w_prime",
            "icu_max_wbal_depletion", "icu_joules_above_ftp",
            "total_elevation_gain", "calories", "VO2MaxGarmin",
            "source", "device_name"
        ]

        # Identify which core fields actually exist in the incoming df
        available_fields = [f for f in core_fields if f in df_events.columns]
        missing_fields = [f for f in core_fields if f not in df_events.columns]

        semantic["events"] = []
        for _, row in df_events.iterrows():
            # ✅ Only include fields that have real (non-null, non-NaN, non-empty) values
            ev = {
                k: row[k]
                for k in available_fields
                if pd.notna(row[k]) and row[k] != "" and row[k] is not None
            }

            if "start_date_local" in ev:
                ev["start_date_local"] = convert_to_str(ev["start_date_local"])

            # ✅ Skip events that are completely empty
            if ev:
                semantic["events"].append(ev)

        debug(
            context,
            f"[SEMANTIC] EVENTS: populated semantic.events with {len(semantic['events'])} entries"
        )
    else:
        debug(context, "[SEMANTIC] EVENTS: no df_events available or empty DataFrame")

    # ---------------------------------------------------------
    # 🪜 Weekly Load Aggregation (Season Summary)
    # ---------------------------------------------------------
    if semantic["meta"]["report_type"] == "season":
        df_src = None
        for candidate_name in ["df_light_slice", "activities_light", "_df_scope_full"]:
            candidate = context.get(candidate_name)
            if isinstance(candidate, pd.DataFrame) and not candidate.empty:
                df_src = candidate.copy()
                break

        if df_src is not None and "start_date_local" in df_src.columns:
            df_src["start_date_local"] = pd.to_datetime(df_src["start_date_local"], errors="coerce")
            df_src = df_src.dropna(subset=["start_date_local"])

            for col in ["icu_training_load", "moving_time", "distance"]:
                if col in df_src.columns:
                    df_src[col] = pd.to_numeric(df_src[col], errors="coerce").fillna(0)

            df_src["week"] = df_src["start_date_local"].dt.isocalendar().week
            df_week = (
                df_src.groupby("week", as_index=False)
                .agg({
                    "distance": "sum",
                    "moving_time": "sum",
                    "icu_training_load": "sum"
                })
                .sort_values("week")
            )

            semantic["phases_weekly"] = [
                {
                    "phase": f"Week {int(r['week'])}",
                    "distance_km": round(r["distance"] / 1000, 1),
                    "hours": round(r["moving_time"] / 3600, 1),
                    "tss": round(r["icu_training_load"], 0)
                }
                for _, r in df_week.iterrows()
            ]
        else:
            semantic["phases_weekly"] = [
                {"phase": "No Data", "start": None, "end": None, "delta": 0.0}
            ]


    # ---------------------------------------------------------
    # DERIVED EVENT SUMMARIES — W' Balance & Performance
    # ---------------------------------------------------------
    df_ev = pd.DataFrame(semantic["events"])
    if not df_ev.empty:
        # --- W' (Wbal) summaries ---
        if {"icu_pm_w_prime", "icu_max_wbal_depletion", "icu_joules_above_ftp"} <= set(df_ev.columns):
            with np.errstate(divide="ignore", invalid="ignore"):
                wbal_pct = df_ev["icu_max_wbal_depletion"] / df_ev["icu_pm_w_prime"]
                anaerobic_pct = df_ev["icu_joules_above_ftp"] / df_ev["icu_pm_w_prime"]

            semantic["wbal_summary"] = {
                "mean_wbal_depletion_pct": round(float(wbal_pct.mean(skipna=True) or 0), 3),
                "mean_anaerobic_contrib_pct": round(float(anaerobic_pct.mean(skipna=True) or 0), 3),
                "sessions_with_wbal_data": int(df_ev["icu_max_wbal_depletion"].notna().sum()),
            }

        # --- General performance summaries ---
        perf_fields = {
            "IF": "mean_IF",
            "icu_intensity": "mean_intensity",
            "icu_efficiency_factor": "mean_efficiency_factor",
            "decoupling": "mean_decoupling",
            "icu_power_hr": "mean_power_hr_ratio"
        }

        perf_summary = {}
        for in_name, out_name in perf_fields.items():
            if in_name in df_ev.columns:
                debug(context, f"[SEMANTIC-SUMMARY] Computing mean for {in_name}, dtype={df_ev[in_name].dtype}")
                try:
                    # ✅ Safely coerce to numeric (ignore strings)
                    val_series = pd.to_numeric(df_ev[in_name], errors="coerce")
                    mean_val = float(val_series.mean(skipna=True) or 0)
                    perf_summary[out_name] = round(mean_val, 3)
                except Exception as e:
                    debug(context, f"[SEMANTIC-SUMMARY] Skipped {in_name}: {e}")
                    perf_summary[out_name] = 0


                if perf_summary:
                    semantic["performance_summary"] = perf_summary

    

    # ---------------------------------------------------------
    # 🗓️ PLANNED EVENTS — Grouped by Date (Calendar Context)
    # ---------------------------------------------------------

    planned_events = []
    planned_summary_by_date = {}

    calendar_data = context.get("calendar")

    if isinstance(calendar_data, list) and len(calendar_data) > 0:
        planned_by_date = {}

        for e in calendar_data:
            if not isinstance(e, dict):
                continue

            start = e.get("start_date_local") or e.get("date")
            if isinstance(start, datetime):
                start = start.date().isoformat()
            elif isinstance(start, str) and "T" in start:
                start = start.split("T")[0]

            event = {
                "id": e.get("id"),
                "uid": e.get("uid"),
                "category": e.get("category", "OTHER"),
                "name": e.get("name") or e.get("title") or "Untitled",
                "description": e.get("description") or e.get("notes") or "",
                "start_date_local": e.get("start_date_local"),
                "end_date_local": e.get("end_date_local"),
                "duration_minutes": e.get("duration_minutes"),
                "icu_training_load": e.get("icu_training_load") or e.get("tss"),
                "load_target": e.get("load_target"),
                "time_target": e.get("time_target"),
                "distance_target": e.get("distance_target"),
                "strain_score": e.get("strain_score"),
                "plan_name": e.get("plan_name"),
                "plan_workout_id": e.get("plan_workout_id"),
                "color": e.get("color"),
                "tags": e.get("tags"),
                "day_of_week": (
                    datetime.fromisoformat(start).strftime("%A")
                    if isinstance(start, str) and len(start) == 10
                    else None
                ),
            }

            # 🧹 Remove all null/NaN/empty values
            event = {
                k: v
                for k, v in event.items()
                if v not in (None, "", [], {}) and not (isinstance(v, float) and isnan(v))
            }

            planned_events.append(event)
            if start:
                planned_by_date.setdefault(start, []).append(event)

        planned_summary_by_date = {
            day: {
                "total_events": len(events),
                "total_duration": sum((e.get("duration_minutes") or 0) for e in events),
                "total_load": sum((e.get("icu_training_load") or 0) for e in events),
                "categories": sorted({e.get("category") for e in events if e.get("category")}),
            }
            for day, events in planned_by_date.items()
        }

    semantic["planned_events"] = planned_events
    semantic["planned_summary_by_date"] = planned_summary_by_date
    semantic["future_forecast"] = context.get("future_forecast", {})

    # ---------------------------------------------------------
    # DERIVED METRICS
    # ---------------------------------------------------------
    for metric_name, info in context.get("derived_metrics", {}).items():
        semantic["metrics"][metric_name] = {
            "name": metric_name,
            "value": handle_missing_data(info.get("value"), 0),
            "classification": info.get("classification", "unknown"),
            "interpretation": info.get("interpretation", ""),
            "coaching_implication": info.get("coaching_implication", ""),
            "related_metrics": info.get("related_metrics", {}),
        }
    # ------------------------------------------------------------------
    # 📊 Load-related metrics (cheat-sheet aligned)
    # ------------------------------------------------------------------
    try:
        metric_keys = ["ACWR", "Monotony", "Strain", "FatigueTrend", "ZQI"]

        semantic.setdefault("metrics", {})

        for key in metric_keys:
            val = context.get(key)
            if val is None:
                debug(context, f"[SEMANTIC] ⚠️ {key}: no value in context")
                continue

            profile_def = COACH_PROFILE.get("markers", {}).get(key, {})
            thresholds = CHEAT_SHEET.get("thresholds", {}).get(key, {})

            criteria = profile_def.get("criteria", thresholds)
            notes = (
                profile_def.get("interpretation")
                or CHEAT_SHEET.get("context", {}).get(key)
                or ""
            )
            framework = profile_def.get("framework", "physiological")

            icon, state = classify_marker(val, key, context)

            semantic["metrics"][key] = {
                "value": round(float(val), 3) if isinstance(val, (int, float)) else val,
                "criteria": criteria,
                "state": state,
                "icon": icon,
                "framework": framework,
                "notes": notes,
            }

            debug(context, f"[SEMANTIC] {key}: {val} → {state} ({framework})")

    except Exception as e:
        debug(context, f"[SEMANTIC] ⚠️ Load metric integration failed: {e}")

    # ------------------------------------------------------------------
    # 🧠 Metabolic & Recovery Metrics (cheat-sheet aligned)
    # ------------------------------------------------------------------
    try:
        metric_keys = ["FOxI", "MES", "RecoveryIndex", "StressTolerance"]

        semantic.setdefault("metrics", {})

        for key in metric_keys:
            val = context.get(key)
            if val is None:
                debug(context, f"[SEMANTIC] ⚠️ {key}: no value in context")
                continue

            profile_def = COACH_PROFILE.get("markers", {}).get(key, {})
            thresholds = CHEAT_SHEET.get("thresholds", {}).get(key, {})
            criteria = profile_def.get("criteria", thresholds)

            notes = (
                profile_def.get("interpretation")
                or CHEAT_SHEET.get("context", {}).get(key)
                or ""
            )
            framework = profile_def.get("framework", "physiological")

            icon, state = classify_marker(val, key, context)

            semantic["metrics"][key] = {
                "value": round(float(val), 3) if isinstance(val, (int, float)) else val,
                "criteria": criteria,
                "state": state,
                "icon": icon,
                "framework": framework,
                "notes": notes,
            }

            debug(context, f"[SEMANTIC] {key}: {val} → {state} ({framework})")

    except Exception as e:
        debug(context, f"[SEMANTIC] ⚠️ Metabolic/Recovery metric integration failed: {e}")

    # ---------------------------------------------------------
    # Annotate context windows per metric
    # ---------------------------------------------------------
    metric_windows = {
        # Short-term / 7-day metrics
        "Polarisation": "7d",
        "PolarisationIndex": "7d",
        "FatOxEfficiency": "7d",
        "FOxI": "7d",
        "MES": "7d",
        "CUR": "7d",
        "GR": "7d",
        "RecoveryIndex": "7d",
        "StressTolerance": "7d",
        "ZQI": "7d",

        # Long-term / 90-day metrics
        "CTL": "90d",
        "ATL": "90d",
        "TSB": "90d",
        "RampRate": "90d",
        "FatigueTrend": "90d",
        "AerobicDecay": "90d",
        "Durability": "90d",

        # Rolling or composite metrics
        "ACWR": "rolling",
        "Monotony": "rolling",
        "Strain": "rolling",
    }

    for name, metric in semantic["metrics"].items():
        metric["context_window"] = metric_windows.get(name, "unknown")
        
    # SAFETY PATCH: ensure Polarisation is numeric and preserved
    # ---------------------------------------------------------
    pol_block = semantic["metrics"].get("Polarisation", {})
    pol_val = pol_block.get("value")

    try:
        # Convert safely to float
        pol_val_f = float(pol_val)
        # Clamp absurd values only
        if pol_val_f < 0 or pol_val_f > 5:
            raise ValueError
        # Preserve computed Tier-2 value
        semantic["metrics"]["Polarisation"]["value"] = round(pol_val_f, 3)
    except Exception:
        computed_val = context.get("Polarisation") or 0.0
        debug(context, f"[SEMANTIC] Polarisation invalid ({pol_val}) — using computed {computed_val}")
        semantic["metrics"]["Polarisation"] = semantic_block_for_metric(
            "Polarisation", computed_val, context
        )

    # ---------------------------------------------------------
    # SECONDARY METRICS
    # ---------------------------------------------------------
    secondary_keys = [
        "FatOxEfficiency", "FOxI", "CUR", "GR", "MES",
        "StressTolerance", "RecoveryIndex", "ZQI", "Polarisation"
    ]

    for k in secondary_keys:
        if k in context and k not in semantic["metrics"]:
            semantic["metrics"][k] = semantic_block_for_metric(
                k, context.get(k), context
            )

  
    # ---------------------------------------------------------
    # 🧮 CTL / ATL / TSB RESOLUTION (AUTHORITATIVE + FALLBACK)
    # ---------------------------------------------------------
    semantic.setdefault("wellness", {})
    ext = semantic.get("extended_metrics", {})

    if isinstance(ext, dict) and all(k in ext for k in ("CTL", "ATL", "TSB")):
        semantic["wellness"]["CTL"] = ext["CTL"].get("value")
        semantic["wellness"]["ATL"] = ext["ATL"].get("value")
        semantic["wellness"]["TSB"] = ext["TSB"].get("value")
        debug(context, "[SEM] CTL/ATL/TSB sourced from semantic.extended_metrics")
    else:
        ws = context.get("wellness_summary", {})
        semantic["wellness"]["CTL"] = ws.get("ctl")
        semantic["wellness"]["ATL"] = ws.get("atl")
        semantic["wellness"]["TSB"] = ws.get("tsb")
        debug(context, "[SEM] CTL/ATL/TSB sourced from wellness_summary fallback")

    # ---------------------------------------------------------
    # 🔮 FUTURE FORECAST (Tier-3 projections)
    # ---------------------------------------------------------
    semantic["future_forecast"] = context.get("future_forecast", {}) or {}
    if "actions_future" in context and isinstance(context["actions_future"], list):
        semantic["actions_future"] = context["actions_future"]
    else:
        semantic["actions_future"] = []

    # ---------------------------------------------------------
    # 🧭 COACHING ACTIONS (Tier-2 guidance)
    # ---------------------------------------------------------
    semantic["actions"] = context.get("actions", [])

    # ---------------------------------------------------------
    # 🧠 INSIGHTS (computed once, after all metrics resolved)
    # ---------------------------------------------------------
    semantic["insights"] = build_insights(semantic)
    semantic["insight_view"] = build_insight_view(semantic)

    # ---------------------------------------------------------
    # 🧩 Echo render options for transparency
    # ---------------------------------------------------------
    if "render_options" in context:
        semantic["options"] = context["render_options"]

    return apply_report_type_contract(semantic)


def build_insight_view(semantic):
    """
    Build API/UI-ready insight view.
    NO calculations.
    NO thresholds.
    NO recomputation.
    Pure grouping only.
    """

    metrics = semantic.get("metrics", {})
    actions = semantic.get("actions", [])
    phases = semantic.get("phases", [])

    critical, watch, positive = [], [], []

    for name, m in metrics.items():
        cls = m.get("classification")
        if cls not in ("red", "amber", "green"):
            continue

        entry = {
            "name": name,
            "value": m.get("value"),
            "framework": m.get("framework"),
            "interpretation": m.get("interpretation"),
            "coaching_implication": m.get("coaching_implication"),
        }

        if cls == "red":
            critical.append(entry)
        elif cls == "amber":
            watch.append(entry)
        else:
            positive.append(entry)

    # ✅ Cleaned return (no nested copy of insights)
    return {
        "critical": critical,
        "watch": watch,
        "positive": positive,
        "actions": actions,
        "phases": phases,
    }



def apply_report_type_contract(semantic: dict) -> dict:
    """
    Enforce report-type-specific semantic exposure.
    Does NOT recompute anything.
    """

    report_type = semantic.get("meta", {}).get("report_type")
    semantic["meta"]["report_header"] = REPORT_HEADERS.get(report_type, {})
    semantic["meta"]["resolution"] = REPORT_RESOLUTION.get(report_type, {})

    # promote header for rendering
    semantic["header"] = semantic["meta"]["report_header"]

    # ---------------- WEEKLY ----------------
    if report_type == "weekly" and not semantic.get("phases"):
        semantic["phases"] = [{"phase": "No Data", "start": None, "end": None, "delta": 0.0}]

    # ---------------- SEASON ----------------
    if report_type == "season":
        semantic["events"] = []
        semantic["zones"] = {}
        semantic["daily_load"] = []
        semantic["metrics"] = {
            k: v for k, v in semantic["metrics"].items()
            if k in ("ACWR", "RampRate", "TSB")
        }
        semantic["insights"] = {
            k: v for k, v in semantic["insights"].items()
            if k not in ("load_distribution",)
        }
        return semantic

    # ---------------- WELLNESS ----------------
    if report_type == "wellness":
        return {
            "meta": semantic["meta"],
            "wellness": semantic.get("wellness", {}),
        }
        return semantic
    # ---------------- SUMMARY ----------------
    if report_type == "summary":
        return {
            "meta": semantic["meta"],
            "hours": semantic.get("hours"),
            "tss": semantic.get("tss"),
            "distance_km": semantic.get("distance_km"),
            "wellness": semantic.get("wellness"),
            "insights": semantic.get("insights"),
            "actions": semantic.get("actions"),
        }

    return semantic

