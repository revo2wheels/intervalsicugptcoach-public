"""
semantic_json_builder.py
------------------------

Builds a FULL semantic DICT coaching graph based on the Unified Reporting
Framework v5.1, Coaching Profile, Coaching Cheat Sheet, and all Tier-2 modules.

Includes (URF v5.1 Canonical Layout):
 - Authoritative totals (hours, TSS, distance)
 - Derived metrics (Tier-2 + contextual)
 - Extended metrics (e.g., lactate, endurance zones)
 - Adaptation metrics
 - Trend metrics
 - Correlation metrics
 - Wellness (sanitised + HRV integration)
 - Thresholds / interpretations / coaching links
 - Insights (aggregated + classification)
 - Insight view (UI-ready grouping)
 - Coaching actions (Tier-2 guidance + future actions)
 - Phase detection (Base → Build → Peak → Taper → Recovery)
 - Phases weekly summary (for seasonal and summary reports)
 - Event previews (stable canonical structure)
 - Planned events + daily load summaries
 - Future forecast (Tier-3 projections)
 - Athlete identity / profile / context (flattened Intervals.icu schema)
 - Zones (power / HR / pace + calibration metadata)
 - Meta header (URF v5.1 framework + reporting window + scope)
"""


import json, math
from datetime import datetime, date, timezone
import pandas as pd
from math import isnan
from coaching_cheat_sheet import CHEAT_SHEET
from coaching_profile import COACH_PROFILE, REPORT_HEADERS, REPORT_RESOLUTION, REPORT_CONTRACT
from audit_core.utils import debug
import numpy as np
from math import isnan
import pytz
from audit_core.tier2_derived_metrics import classify_marker
from textwrap import dedent

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
    """
    Builds semantic envelope for a single metric.
    100% data-driven: thresholds, phase overrides, and interpretations
    are all defined in coaching_cheat_sheet.py.
    """
    import math

    metric_name = str(name).strip()
    thresholds = CHEAT_SHEET["thresholds"].get(metric_name, {})
    phase_thresholds = CHEAT_SHEET.get("phase_thresholds", {}).get(metric_name, {})
    profile_desc = COACH_PROFILE["markers"].get(metric_name, {})

    interpretation = (
        CHEAT_SHEET["context"].get(metric_name)
        or profile_desc.get("interpretation")
    )
    coaching_link = (
        CHEAT_SHEET["coaching_links"].get(metric_name)
        or profile_desc.get("coaching_implication")
    )
    display_name = CHEAT_SHEET.get("display_names", {}).get(metric_name, metric_name)

    phase = (
        context.get("current_phase")
        or context.get("phase_name")
        or ""
    ).lower()

    classification = "unknown"

    try:
        if value is None or (isinstance(value, (float, int)) and math.isnan(value)):
            classification = "undefined"
        else:
            v = float(value)

            # Pull the correct thresholds dynamically
            active_thresholds = (
                phase_thresholds.get(phase)
                if metric_name in phase_thresholds and phase in phase_thresholds
                else thresholds
            )

            green = active_thresholds.get("green")
            amber = active_thresholds.get("amber")

            if green and green[0] <= v <= green[1]:
                classification = "green"
            elif amber and amber[0] <= v <= amber[1]:
                classification = "amber"
            else:
                classification = "red"

    except Exception:
        classification = "unknown"

    return {
        "name": metric_name,
        "display_name": display_name,
        "value": convert_to_str(value),
        "framework": profile_desc.get("framework") or "Unknown",
        "formula": profile_desc.get("formula"),
        "thresholds": thresholds,
        "phase_context": phase,
        "classification": classification,
        "interpretation": interpretation,
        "coaching_implication": coaching_link,
        "related_metrics": profile_desc.get("criteria", {}),
    }

# ---------------------------------------------------------
# 🔬 Zone semantics helpers (CHEAT_SHEET–driven)
# ---------------------------------------------------------
zone_semantics = CHEAT_SHEET.get("zone_semantics", {})

def zone_block(key, dist, thresholds):
    meta = zone_semantics.get(key, {})
    return {
        "label": meta.get("label"),
        "description": meta.get("description"),
        "distribution": dist or {},
        "thresholds": thresholds or [],
    }

def rename_z8_to_ss(dist: dict):
    """
    Semantic-only rename for Sweet Spot (power only).

    Rules:
    - z8               -> SS
    - _fused_power_z8   -> _fused_power_SS

    Non-destructive, presentation layer only.
    """
    if not isinstance(dist, dict):
        return dist

    out = {}
    for k, v in dist.items():
        # --- Power Sweet Spot (canonical) ---
        if k == "z8":
            out["SS"] = v

        # --- Fused Power Sweet Spot ---
        elif k == "_fused_power_z8":
            out["_fused_power_SS"] = v

        else:
            out[k] = v

    return out

# ---------------------------------------------------------
# Insights Builder
# ---------------------------------------------------------

def build_insights(semantic):
    """
    Build high-level coaching insights using canonical thresholds
    from Coaching Cheat Sheet + Coaching Profile.
    """
    insights = {}
    report_type = semantic.get("meta", {}).get("report_type", "weekly")

    # 🧠 Adaptive window duration by report type
    window_map = {
        "weekly": "7d",
        "wellness": "42d",
        "season": "90d",
        "summary": "365d"
    }
    window = window_map.get(report_type, "7d")

    # Polarisation and load-distribution metrics are short-term (7-day)
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

    # ======================================================
    # 🔬 Adaptation Metrics (Fatigue Resistance, Efficiency)
    # ======================================================
    adaptation = semantic.get("adaptation_metrics", {})

    # --- Fatigue Resistance ---
    if "Fatigue Resistance" in adaptation:
        fr_val = adaptation.get("Fatigue Resistance")
        fr_block = semantic_block_for_metric("FatigueResistance", fr_val, semantic)
        insights["fatigue_resistance"] = {
            "value": fr_val,
            "window": window,
            "basis": "EndurancePower / ThresholdPower",
            "classification": fr_block.get("classification"),
            "interpretation": fr_block.get("interpretation"),
            "coaching_implication": fr_block.get("coaching_implication"),
        }

    # --- Efficiency Factor ---
    if "Efficiency Factor" in adaptation:
        ef_val = adaptation.get("Efficiency Factor")
        ef_block = semantic_block_for_metric("EfficiencyFactor", ef_val, semantic)
        insights["efficiency_factor"] = {
            "value": ef_val,
            "window": window,
            "basis": "Power / HeartRate",
            "classification": ef_block.get("classification"),
            "interpretation": ef_block.get("interpretation"),
            "coaching_implication": ef_block.get("coaching_implication"),
        }

    # ======================================================
    # 🌿 WELLNESS INSIGHTS (Coach-Profile & Cheat-Sheet Aligned)
    # ======================================================
    if report_type == "wellness":
        wellness = semantic.get("wellness", {})

        # Ensure TSB available for recovery_index
        tsb = (
            wellness.get("tsb")
            or wellness.get("TSB")
            or semantic.get("wellness_summary", {}).get("tsb")
            or 0
        )

        # --- HRV Advanced Insights ---
        if wellness.get("hrv_available"):
            hrv_mean = wellness.get("hrv_mean")
            hrv_latest = wellness.get("hrv_latest")
            hrv_series = wellness.get("hrv_series", [])

            # --- HRV Recovery Balance (ratio, not %)
            if hrv_mean and hrv_latest:
                hrv_ratio = round(hrv_latest / hrv_mean, 2)
                hrv_block = semantic_block_for_metric("HRVBalance", hrv_ratio, semantic)
                insights["hrv_recovery_balance"] = {
                    "value": hrv_ratio,
                    "window": "42d",
                    "basis": "Latest / Mean HRV (ratio)",
                    "classification": hrv_block.get("classification"),
                    "interpretation": hrv_block.get("interpretation"),
                    "coaching_implication": hrv_block.get("coaching_implication"),
            }

            # 2️⃣ Stability Index (1 - rolling std / mean)
            if hrv_series and len(hrv_series) >= 7:
                import pandas as pd, numpy as np
                df_hrv = pd.DataFrame(hrv_series)
                df_hrv["hrv"] = pd.to_numeric(df_hrv["hrv"], errors="coerce")
                recent = df_hrv.tail(14)["hrv"].dropna()
                if len(recent) >= 5:
                    mean_val = recent.mean()
                    std_val = recent.std()
                    stability = round((1 - (std_val / mean_val)), 3)
                    stab_block = semantic_block_for_metric("HRVStability", stability, semantic)
                    insights["hrv_stability_index"] = {
                        "value": stability,
                        "window": "14d",
                        "basis": "1 - (std / mean)",
                        "classification": stab_block.get("classification"),
                        "interpretation": stab_block.get("interpretation"),
                        "coaching_implication": stab_block.get("coaching_implication"),
                    }

            # 3️⃣ Trend (slope of last 7 days)
            if hrv_series and len(hrv_series) >= 7:
                import numpy as np
                vals = [h.get("hrv") for h in hrv_series[-7:] if h.get("hrv")]
                if len(vals) == 7:
                    x = np.arange(7)
                    slope = round(np.polyfit(x, vals, 1)[0], 2)
                    trend_block = semantic_block_for_metric("HRVTrend", slope, semantic)
                    insights["hrv_trend_7d"] = {
                        "value": slope,
                        "window": "7d",
                        "basis": "HRV slope (ms/day)",
                        "classification": trend_block.get("classification"),
                        "interpretation": trend_block.get("interpretation"),
                        "coaching_implication": trend_block.get("coaching_implication"),
                    }

        # --- Resting HR Trend ---
        if "resting_hr_delta" in wellness:
            delta_rhr = round(wellness["resting_hr_delta"], 1)
            rhr_block = semantic_block_for_metric("RestingHR", delta_rhr, semantic)
            insights["resting_hr_trend"] = {
                "value": delta_rhr,
                "window": "7d vs 28d",
                "basis": "Δ Resting HR",
                "classification": rhr_block.get("classification"),
                "interpretation": rhr_block.get("interpretation"),
                "coaching_implication": rhr_block.get("coaching_implication"),
            }


        # --- Sleep Quality ---
        if "sleep_score" in wellness:
            sleep_val = wellness.get("sleep_score")
            sleep_block = semantic_block_for_metric("SleepQuality", sleep_val, semantic)
            insights["sleep_quality"] = {
                "value": sleep_val,
                "window": "14d",
                "basis": "Average Sleep Score",
                "classification": sleep_block.get("classification"),
                "interpretation": sleep_block.get("interpretation"),
                "coaching_implication": sleep_block.get("coaching_implication"),
            }

        # --- Recovery Index (HRV × TSB composite)
        if hrv_mean and hrv_latest and tsb is not None:
            rec_index = round((hrv_latest / hrv_mean) * (1 + (tsb / 100)), 2)
            rec_block = semantic_block_for_metric("RecoveryIndex", rec_index, semantic)
            insights["recovery_index"] = {
                "value": rec_index,
                "window": "42d",
                "basis": "HRV × TSB composite",
                "classification": rec_block.get("classification"),
                "interpretation": rec_block.get("interpretation"),
                "coaching_implication": rec_block.get("coaching_implication"),
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
            # --- Framework identity ---
            "framework": CHEAT_SHEET["meta"].get(
                "framework", "Unified Reporting Framework"
            ),
            "version": CHEAT_SHEET["meta"].get("version"),

            # --- Methodology (coach + cheat sheet) ---
            "methodology": {
                "source": CHEAT_SHEET["meta"].get("source"),
                "summary": COACH_PROFILE["bio"]["summary"],
                "principles": COACH_PROFILE["bio"]["principles"],
            },

            # --- Generation context ---
            "generated_at": {
                "local": (
                    datetime.now(
                        pytz.timezone(context.get("timezone", "UTC"))
                        if context.get("timezone") else pytz.UTC
                    )
                    .replace(microsecond=0)
                    .isoformat()
                )
            },

            # --- Environment ---
            "timezone": context.get("timezone"),

            # --- Athlete placeholder (filled later) ---
            "athlete": {
                "identity": {},
                "profile": {},
            },
        },
   
        # ---------------------------------------------------------
        # METRICS CONTAINERS
        # ---------------------------------------------------------

        "metrics": {},
        "extended_metrics": {},
        "adaptation_metrics": {},
        "trend_metrics": {},
        "correlation_metrics": {},

        # ---------------------------------------------------------
        # 🔬 Zones — Power, HR, Pace, Swim + Calibration
        # ---------------------------------------------------------
        "zones": {
            "power": zone_block(
                "power",
                rename_z8_to_ss(context.get("zone_dist_power")),
                #context.get("zone_dist_power"),  
                context.get("icu_power_zones") or context.get("athlete_power_zones"),
            ),
            "hr": zone_block(
                "hr",
                rename_z8_to_ss(context.get("zone_dist_hr")),
                #context.get("zone_dist_hr"),
                context.get("icu_hr_zones") or context.get("athlete_hr_zones"),
            ),
            "pace": zone_block(
                "pace",
                rename_z8_to_ss(context.get("zone_dist_pace")),
                #context.get("zone_dist_pace"),
                context.get("icu_pace_zones") or context.get("athlete_pace_zones"),
            ),
            "swim": zone_block(
                "swim",
                rename_z8_to_ss(context.get("zone_dist_swim")),
                #context.get("zone_dist_swim"),
                context.get("icu_swim_zones") or context.get("athlete_swim_zones"),
            ),
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
        #PHASE BASED APPROACH
        #Issurin (2008) — macro/micro distinction between period blocks and load cycles.
        #Seiler (2019) — mesocycle-level trend and micro-level workload separation.
        #Mujika & Padilla (2003) — tapering and recovery phases as distinct block summaries.
        "phases": [
            {
                "phase": p.get("phase"),
                "start": p.get("start"),
                "end": p.get("end"),
                "duration_days": p.get("duration_days"),
                "duration_weeks": p.get("duration_weeks"),
            }
            for p in context.get("phases", [])
        ],
    }

    # ---------------------------------------------------------
    # 🧩 Inject Fused Zone Distribution (Power + HR per sport)
    # ---------------------------------------------------------
    try:
        if context.get("zone_dist_fused"):
            semantic["zones"]["fused"] = {
                "per_sport": {
                    sport: rename_z8_to_ss(dist)
                    for sport, dist in context["zone_dist_fused"].items()
                },
                "dominant_sport": context.get("polarisation_sport", "Unknown"),
                "basis": "Sport-specific fusion of power and HR zones (power preferred, HR fallback)",
            }
            debug(context, f"[SEMANTIC] Injected fused zones → sports={list(context['zone_dist_fused'].keys())}")
        else:
            semantic["zones"]["fused"] = {
                "per_sport": {},
                "dominant_sport": None,
                "basis": "unavailable",
            }
    except Exception as e:
        debug(context, f"[SEMANTIC] ⚠️ Could not inject fused zones: {e}")


    # ---------------------------------------------------------
    # 🧩 Inject Combined Zones (Tier-2 authoritative)
    # ---------------------------------------------------------
    try:
        zc = context.get("zone_dist_combined")

        if isinstance(zc, dict) and zc.get("distribution"):
            semantic["zones"]["combined"] = {
                "label": CHEAT_SHEET["zone_semantics"]["combined"]["label"],
                "description": CHEAT_SHEET["zone_semantics"]["combined"]["description"],
                "distribution": rename_z8_to_ss(zc["distribution"]),
                "basis": zc.get("basis"),
            }
            debug(context, "[SEMANTIC] ✅ Injected combined zones from Tier-2 (authoritative)")
        else:
            semantic["zones"]["combined"] = {
                "distribution": {"power": {}, "hr": {}},
                "basis": "unavailable",
                "model_description": "No valid data",
            }

    except Exception as e:
        debug(context, f"[SEMANTIC] ⚠️ Combined zone injection failed: {e}")




    # ---------------------------------------------------------
    # 🧭 Polarisation Variants (Tier-2 authoritative values only)
    # ---------------------------------------------------------
    try:
        polarisation_variants = {}
        cs = CHEAT_SHEET  # alias for brevity

        def build_variant(metric_key: str, value: float, basis: str, source: str):
            """
            Universal polarisation variant builder.
            Purely interpretative — no math. Uses Tier-2 values.
            """
            block = semantic_block_for_metric(metric_key, value, context)

            # canonical enrichment — merge with COACH_PROFILE definitions
            profile_def = COACH_PROFILE["markers"].get(metric_key, {})

            block.update({
                "display_name": cs["display_names"].get(metric_key, metric_key),
                "basis": basis,
                "source": source,
                "framework": profile_def.get("framework", "Physiological"),
                "formula": profile_def.get("formula"),
                "thresholds": (
                    cs["thresholds"].get(metric_key)
                    or profile_def.get("criteria")
                ),
                "interpretation": (
                    cs["context"].get(metric_key)
                    or profile_def.get("interpretation")
                ),
                "coaching_implication": (
                    cs["coaching_links"].get(metric_key)
                    or profile_def.get("coaching_implication")
                ),
                "related_metrics": profile_def.get("criteria", {}),
            })

            # 🧭 Phase-awareness
            block["phase_context"] = (
                context.get("current_phase")
                or (semantic.get("phases", [{}])[-1].get("phase") if semantic.get("phases") else "")
                or ""
            )

            return block

        # --- Fused (sport-specific HR+Power)
        pi_fused = context.get("Polarisation_fused") or context.get("Polarisation")
        if pi_fused is not None:
            polarisation_variants["fused"] = build_variant(
                "Polarisation_fused",
                pi_fused,
                f"Fused HR+Power (dominant sport: {context.get('polarisation_sport', 'Unknown')})",
                "zones.fused",
            )
            debug(context, f"[SEMANTIC] Polarisation_fused={pi_fused}")

        # --- Combined (multi-sport HR+Power)
        pi_combined = context.get("Polarisation_combined") or context.get("PolarisationIndex")
        if pi_combined is not None:
            polarisation_variants["combined"] = build_variant(
                "Polarisation_combined",
                pi_combined,
                "Power where available, HR otherwise (multi-sport weighted)",
                "zones.combined",
            )
            debug(context, f"[SEMANTIC] Polarisation_combined={pi_combined}")

        # --- Inject into semantic
        if polarisation_variants:
            semantic.setdefault("metrics", {})
            semantic["metrics"]["Polarisation_variants"] = polarisation_variants
            debug(
                context,
                f"[SEMANTIC] ✅ Injected Polarisation variants → {list(polarisation_variants.keys())}"
            )
        else:
            debug(context, "[SEMANTIC] ⚠️ No valid Polarisation variants found in context")

    except Exception as e:
        debug(context, f"[SEMANTIC] ⚠️ Could not build polarisation variants: {e}")

    # ------------------------------------------------------------------
    # 🧬 Lactate, HRV and Threshold Integration (Cheat-Sheet aligned)
    # ------------------------------------------------------------------
    try:
        # --- Lactate defaults (only if derived metrics didn't set them)
        if "lactate_thresholds_dict" not in context:
            lac_defaults = CHEAT_SHEET["thresholds"].get("Lactate", {})
            context["lactate_thresholds_dict"] = {
                "lt1_mmol": lac_defaults.get("lt1_mmol", 2.0),
                "lt2_mmol": lac_defaults.get("lt2_mmol", 4.0),
                "corr_threshold": lac_defaults.get("corr_threshold", 0.6),
                "notes": CHEAT_SHEET.get("context", {}).get("Lactate", "Lactate thresholds derived from cheat-sheet."),
            }

        # --- HRV defaults (always safe to include)
        hrv_profile = COACH_PROFILE.get("markers", {}).get("HRV", {})
        hrv_defaults = CHEAT_SHEET["thresholds"].get("HRV", {})
        semantic["hrv_defaults"] = {
            "optimal": hrv_profile.get("criteria", {}).get("optimal")
                        or hrv_defaults.get("optimal")
                        or [60, 90],
            "low": hrv_profile.get("criteria", {}).get("low")
                        or hrv_defaults.get("low")
                        or [0, 40],
        }

        debug(context,
            f"[SEMANTIC] Lactate defaults (fallback) → LT1={context['lactate_thresholds_dict'].get('lt1_mmol')}, "
            f"LT2={context['lactate_thresholds_dict'].get('lt2_mmol')}, "
            f"corr≥{context['lactate_thresholds_dict'].get('corr_threshold')}")
        debug(context,
            f"[SEMANTIC] HRV defaults → optimal={semantic['hrv_defaults']['optimal']}, low={semantic['hrv_defaults']['low']}")

    except Exception as e:
        debug(context, f"[SEMANTIC] ⚠️ Lactate/HRV threshold integration failed: {e}")

    # --- Derive report period and meta window ---
    report_type = context.get("report_type", "weekly").lower()
    df_ref = None

    # --- Select dataset based on report type ---
    if report_type in ("season", "summary"):
        # ✅ Prefer the preserved full dataset if available (all activity types)
        if "_df_scope_full" in context and isinstance(context["_df_scope_full"], pd.DataFrame) and not context["_df_scope_full"].empty:
            df_ref = context["_df_scope_full"]
            debug(context, f"[SEMANTIC-FORCE] Using _df_scope_full for summary (rows={len(df_ref)})")
        elif "activities_full" in context and isinstance(context["activities_full"], list) and len(context["activities_full"]) > 0:
            df_ref = pd.DataFrame(context["activities_full"])
            debug(context, f"[SEMANTIC-FORCE] Using activities_full for summary (rows={len(df_ref)})")
        elif "df_light" in context and isinstance(context["df_light"], pd.DataFrame) and not context["df_light"].empty:
            df_ref = context["df_light"]
            debug(context, f"[SEMANTIC-FORCE] Fallback to df_light (rows={len(df_ref)})")
        elif isinstance(context.get("activities_light"), list) and context["activities_light"]:
            df_ref = pd.DataFrame(context["activities_light"])
            debug(context, f"[SEMANTIC-FORCE] Fallback to activities_light (rows={len(df_ref)})")

    elif report_type == "wellness":
        df_well = context.get("df_wellness")
        if isinstance(df_well, pd.DataFrame) and not df_well.empty:
            df_ref = df_well
        elif isinstance(context.get("wellness"), list) and len(context["wellness"]) > 0:
            df_ref = pd.DataFrame(context["wellness"])

    else:
        df_master = context.get("df_master")
        if isinstance(df_master, pd.DataFrame) and not df_master.empty:
            df_ref = df_master
        elif isinstance(context.get("activities_full"), list) and len(context["activities_full"]) > 0:
            df_ref = pd.DataFrame(context["activities_full"])


    # --- Fallback: preserved df_scope_full (Railway safe)
    if df_ref is None and "_df_scope_full" in context and isinstance(context["_df_scope_full"], pd.DataFrame):
        df_ref = context["_df_scope_full"]
    
    # --- Compute report period from reference dataset ---
    if report_type in ("season", "summary") and context.get("window_start") and context.get("window_end"):
        # 🔒 Controller-defined window is authoritative
        context["period"] = {
            "start": pd.to_datetime(context["window_start"]).strftime("%Y-%m-%d"),
            "end": pd.to_datetime(context["window_end"]).strftime("%Y-%m-%d"),
        }
        debug(
            context,
            f"[SEMANTIC] Preserved controller window for {report_type} → "
            f"{context['period']['start']} → {context['period']['end']}"
        )

    elif isinstance(df_ref, pd.DataFrame) and not df_ref.empty:
        date_col = (
            "date"
            if "date" in df_ref.columns
            else "start_date_local"
            if "start_date_local" in df_ref.columns
            else df_ref.columns[0]
        )
        start_date = pd.to_datetime(df_ref[date_col], errors="coerce").min().strftime("%Y-%m-%d")
        end_date = pd.to_datetime(df_ref[date_col], errors="coerce").max().strftime("%Y-%m-%d")
        context["period"] = {"start": start_date, "end": end_date}
        debug(context, f"[SEMANTIC] Derived period from {report_type} dataset → {start_date} → {end_date}")

    else:
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        context["period"] = {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
        }
        debug(context, "[SEMANTIC] Defaulted weekly period to last 7 days")



    # --- Enrich meta block from authoritative REPORT_HEADERS ---
    semantic.setdefault("meta", {})
    window_days = (pd.to_datetime(context["period"]["end"]) - pd.to_datetime(context["period"]["start"])).days

    header = REPORT_HEADERS.get(report_type, {})
    semantic["meta"]["report_type"] = report_type
    semantic["meta"]["window_days"] = window_days
    semantic["meta"]["period"] = f"{context['period']['start']} → {context['period']['end']}"
    semantic["meta"]["scope"] = header.get("scope", "Custom analysis window")
    semantic["meta"]["data_sources"] = header.get("data_sources", f"{window_days}-day mixed dataset")
    semantic["meta"]["report_header"] = header


    # --- Mark summary reports as image-ready for ChatGPT ---
    if report_type == "summary":
        semantic["meta"]["summary_card_ready"] = True
        debug(context, "[SEMANTIC] Marked summary report as summary_card_ready=True")
    else:
        semantic["meta"]["summary_card_ready"] = False
    
    # ---------------------------------------------------------
    # WELLNESS BLOCK
    # ---------------------------------------------------------
    semantic["wellness"] = {
        k: handle_missing_data(v, None)
        for k, v in context.get("wellness_summary", {}).items()
    }

    # ---------------------------------------------------------
    # 🧹 Inject DAILY wellness fields (wellness report only)
    # ---------------------------------------------------------
    if (
        context.get("report_type") == "wellness"
        and "wellness_daily" in context
        and context["wellness_daily"]
    ):
        cleaned_daily = []

        for row in context["wellness_daily"]:
            cleaned = {
                k: v
                for k, v in row.items()
                if v is not None
                and not (isinstance(v, float) and math.isnan(v))
            }
            if cleaned:
                cleaned_daily.append(cleaned)

        semantic["wellness"]["daily"] = cleaned_daily

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

    # ---------------------------------------------------------
    # WEEKLY TOTALS (Tier-2 ONLY) - SEASON AND SUMMARY ARE IN PHASES
    # ---------------------------------------------------------

    if report_type not in ("season", "summary"):
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

    # --- Lactate-derived power zones (LT1-based)
    if context.get("power_lactate"):
        semantic.setdefault("extended_metrics", {})
        semantic["extended_metrics"]["power_lactate"] = context["power_lactate"]

        debug(
            context,
            f"[SEMANTIC] Injected power_lactate → "
            f"Z2={context['power_lactate'].get('z2_start_w')}–"
            f"{context['power_lactate'].get('z2_end_w')}W, "
            f"r={context['power_lactate'].get('confidence_r')}"
        )


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
    lactate_mmol_l = custom_fields.get("HrtLndLt1")
    lactate_power = custom_fields.get("HrtLndLt1p")

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
            "lactate_power": lactate_power,
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
            "ss", "ss_cp", "ss_w", "ss_pmax",
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

        # ✅ Add meta info for structured UI rendering
        semantic["meta"]["events"] = {
            "is_event_block": True,
            "event_block_count": len(semantic["events"]),
            "render": True,
            "notes": "Canonical activity/event block (URF v5.2) — intended for ChatGPT / structured UI rendering."
         }

        debug(
            context,
            f"[SEMANTIC] EVENTS: populated semantic.events with {len(semantic['events'])} entries"
        )
    else:
        debug(context, "[SEMANTIC] EVENTS: no df_events available or empty DataFrame")


    # --- Prevent override by short df_scope_full for season/summary ---
    if semantic["meta"]["report_type"] in ("season", "summary"):
        if (
            "df_light" in context
            and isinstance(context["df_light"], pd.DataFrame)
            and len(context["df_light"]) > 100
        ):
            df_ref = context["df_light"]
            debug(context, f"[SEMANTIC-OVERRIDE] Using df_light ({len(df_ref)} rows) for summary/season instead of short _df_scope_full")
        elif (
            "_df_scope_full" in context
            and isinstance(context["_df_scope_full"], pd.DataFrame)
            and len(context["_df_scope_full"]) > 100
        ):
            df_ref = context["_df_scope_full"]
            debug(context, f"[SEMANTIC-OVERRIDE] Using _df_scope_full ({len(df_ref)} rows) for summary/season")
        else:
            debug(context, "[SEMANTIC-OVERRIDE] No valid long-frame dataset found — fallback to df_master")



    # ---------------------------------------------------------
    # 🧩 DEBUG — verify light vs full data sources (before weekly aggregation)
    # ---------------------------------------------------------
    if semantic["meta"]["report_type"] in ("season", "summary"):
        debug(context, "🔍 [DATASET-DIAG] Checking available data sources:")

        for name in ["df_light", "activities_light", "_df_scope_full", "df_master", "df_events"]:
            candidate = context.get(name)
            if isinstance(candidate, pd.DataFrame):
                debug(context, f"🔍 [DATASET-DIAG] {name}: DataFrame rows={len(candidate)}, cols={list(candidate.columns)[:8]}")
                if not candidate.empty:
                    debug(
                        context,
                        f"🔍 [DATASET-DIAG] {name}: "
                        f"min={pd.to_datetime(candidate.iloc[0].get('start_date_local', candidate.iloc[0].get('date', 'NA')), errors='coerce')}, "
                        f"max={pd.to_datetime(candidate.iloc[-1].get('start_date_local', candidate.iloc[-1].get('date', 'NA')), errors='coerce')}"
                    )
            elif isinstance(candidate, list):
                debug(context, f"🔍 [DATASET-DIAG] {name}: list length={len(candidate)}")
                if len(candidate) > 0:
                    sample = candidate[0]
                    debug(context, f"🔍 [DATASET-DIAG] {name}: sample keys={list(sample.keys())[:10]}")
            else:
                debug(context, f"🔍 [DATASET-DIAG] {name}: type={type(candidate).__name__}, value={str(candidate)[:80]}")

        # Explicit check for df_ref after it’s chosen
        if "df_ref" in locals() and isinstance(df_ref, pd.DataFrame):
            debug(
                context,
                f"🔍 [DATASET-DIAG] df_ref resolved → rows={len(df_ref)}, "
                f"cols={list(df_ref.columns)[:6]}, "
                f"date-range={pd.to_datetime(df_ref['start_date_local'] if 'start_date_local' in df_ref else df_ref['date']).agg(['min','max']).to_dict()}"
            )
        else:
            debug(context, "⚠️ [DATASET-DIAG] df_ref not resolved or empty.")



    # ---------------------------------------------------------
    # 🪜 Weekly Phases Summary (URF v5.2 canonical)
    # ---------------------------------------------------------
    if semantic["meta"]["report_type"] in ("season", "summary"):
        # --- Force authoritative dataset for season/summary totals ---
        if "df_light" in context and isinstance(context["df_light"], pd.DataFrame) and len(context["df_light"]) > 100:
            df_ref = context["df_light"]
            debug(context, f"[FORCE] Overriding df_ref with df_light ({len(df_ref)} rows) for totals aggregation")
        elif isinstance(context.get("activities_light"), list) and len(context["activities_light"]) > 0:
            df_ref = pd.DataFrame(context["activities_light"])
            debug(context, f"[FORCE] Overriding df_ref with activities_light ({len(df_ref)} rows) for totals aggregation)")

        df_src = None
        if "df_ref" in locals() and isinstance(df_ref, pd.DataFrame) and not df_ref.empty:
            df_src = df_ref.copy()
            debug(context, f"[WEEKLY] Using df_ref with {len(df_src)} rows for weekly aggregation")
        else:
            for candidate_name in ["df_light", "activities_light", "_df_scope_full"]:
                candidate = context.get(candidate_name)
                if isinstance(candidate, pd.DataFrame) and not candidate.empty:
                    df_src = candidate.copy()
                    debug(context, f"[WEEKLY] Using fallback dataset: {candidate_name} ({len(df_src)} rows)")
                    break

        if df_src is not None and "start_date_local" in df_src.columns:
            df_src["start_date_local"] = pd.to_datetime(df_src["start_date_local"], errors="coerce")
            df_src = df_src.dropna(subset=["start_date_local"])

            # ✅ Coerce numeric and fill NaNs
            for col in ["icu_training_load", "moving_time", "distance"]:
                if col in df_src.columns:
                    df_src[col] = (
                        pd.to_numeric(df_src[col], errors="coerce")
                        .fillna(0)
                        .astype(float)
                    )

            # 🔍 Pre-aggregation sanity check
            debug(
                context,
                f"[CHECK] Before weekly aggregation → {len(df_src)} rows | "
                f"Dist={df_src['distance'].sum()/1000:.1f} km | "
                f"Hours={df_src['moving_time'].sum()/3600:.1f} h | "
                f"TSS={df_src['icu_training_load'].sum():.0f}"
            )

            iso = df_src["start_date_local"].dt.isocalendar()
            df_src["year_week"] = iso["year"].astype(str) + "-W" + iso["week"].astype(str)
            df_week = (
                df_src.groupby("year_week", as_index=False)
                .agg({
                    "distance": "sum",
                    "moving_time": "sum",
                    "icu_training_load": "sum"
                })
                .sort_values("year_week")
            )

            # 🔍 Post-aggregation sanity check
            debug(
                context,
                f"[CHECK] After weekly aggregation → {len(df_week)} weeks | "
                f"Dist={df_week['distance'].sum()/1000:.1f} km | "
                f"Hours={df_week['moving_time'].sum()/3600:.1f} h | "
                f"TSS={df_week['icu_training_load'].sum():.0f}"
            )

            # --- Phase linkage: map each week to its detected macro phase ---
            def get_phase_for_week(week_label):
                try:
                    year, week = week_label.split("-W")
                    week_start = pd.Timestamp.fromisocalendar(int(year), int(week), 1)
                except Exception:
                    return "Unclassified"

                for p in context.get("phases", []):
                    s = pd.to_datetime(p.get("start"))
                    e = pd.to_datetime(p.get("end"))
                    if s <= week_start <= e:
                        return p.get("phase")
                return "Unclassified"

            # --- Build unified weekly phase summary + compute totals ---
            total_hours = 0.0
            total_tss = 0.0
            total_distance = 0.0
            weekly_phases = []

            for _, r in df_week.iterrows():
                week_data = {
                    "week": r["year_week"],
                    "phase": get_phase_for_week(r["year_week"]),
                    "distance_km": round(r["distance"] / 1000, 1),
                    "hours": round(r["moving_time"] / 3600, 1),
                    "tss": round(r["icu_training_load"], 0)
                }

                weekly_phases.append(week_data)

                # 🔢 Increment totals directly
                total_hours += week_data["hours"]
                total_tss += week_data["tss"]
                total_distance += week_data["distance_km"]

            semantic["weekly_phases"] = weekly_phases

            # ✅ Store canonical totals
            semantic["hours"] = round(total_hours, 2)
            semantic["tss"] = round(total_tss, 0)
            semantic["distance_km"] = round(total_distance, 2)

            # 🔒 Mirror totals into context (so finalizer sees them)
            context["locked_totalHours"] = semantic["hours"]
            context["locked_totalTss"] = semantic["tss"]
            context["locked_totalDistance"] = semantic["distance_km"]

            semantic.setdefault("summary", {}).update({
                "totalHours": semantic["hours"],
                "totalTss": semantic["tss"],
                "totalDistance": semantic["distance_km"],
            })

            debug(
                context,
                f"[WEEKLY] ✅ Aggregated {len(weekly_phases)} weeks → "
                f"{semantic['distance_km']} km / {semantic['hours']} h / {semantic['tss']} TSS"
            )

        else:
            debug(context, "[WEEKLY] ❌ No valid df_src found for weekly aggregation")

    if "df_src" in locals() and isinstance(df_src, pd.DataFrame):
        debug(
            context,
            f"[WEEKLY-TRACE] df_src rows={len(df_src)}, "
            f"total distance={df_src['distance'].sum()/1000:.1f} km, "
            f"hours={df_src['moving_time'].sum()/3600:.1f}, "
            f"tss={df_src['icu_training_load'].sum():.0f}"
        )

    if "df_week" in locals() and isinstance(df_week, pd.DataFrame):
        debug(
            context,
            f"[WEEKLY-TRACE] df_week rows={len(df_week)}, "
            f"grouped distance={df_week['distance'].sum()/1000:.1f} km, "
            f"hours={df_week['moving_time'].sum()/3600:.1f}, "
            f"tss={df_week['icu_training_load'].sum():.0f}"
        )

    # ---------------------------------------------------------
    # DERIVED EVENT SUMMARIES — W' Balance & Performance
    # ---------------------------------------------------------

    report_type = semantic["meta"]["report_type"]

    # =========================================================
    # WEEKLY → per-session mean (robust to mixed sports)
    # =========================================================
    if semantic["meta"]["report_type"] == "weekly":
        df_ev = df_events.copy()

        if {
            "icu_pm_w_prime",
            "icu_max_wbal_depletion",
            "icu_joules_above_ftp",
        } <= set(df_ev.columns):

            df_ev = df_ev[
                df_ev["icu_pm_w_prime"].notna()
                & df_ev["icu_max_wbal_depletion"].notna()
                & df_ev["icu_joules_above_ftp"].notna()
            ]

            if not df_ev.empty:
                with np.errstate(divide="ignore", invalid="ignore"):
                    wbal_pct = df_ev["icu_max_wbal_depletion"] / df_ev["icu_pm_w_prime"]
                    anaerobic_pct = df_ev["icu_joules_above_ftp"] / df_ev["icu_pm_w_prime"]

                semantic["wbal_summary"] = {
                    "mean_wbal_depletion_pct": round(float(wbal_pct.mean()), 3),
                    "mean_anaerobic_contrib_pct": round(float(anaerobic_pct.mean()), 3),
                    "sessions_with_wbal_data": int(len(df_ev)),
                    "basis": "per-session mean (W′-capable sessions only)",
                    "window": "weekly",
                }



    # =========================================================
    # SEASON / SUMMARY → weekly peak session model (UNCHANGED)
    # =========================================================
    elif report_type in ("season", "summary"):
        df = context.get("df_light")

        if (
            isinstance(df, pd.DataFrame)
            and not df.empty
            and {
                "start_date_local",
                "icu_pm_w_prime",
                "icu_max_wbal_depletion",
                "icu_joules_above_ftp",
            } <= set(df.columns)
        ):
            df = df.copy()
            df["start_date_local"] = pd.to_datetime(df["start_date_local"], errors="coerce")
            df = df.dropna(subset=["start_date_local"])

            # 🔑 FILTER TO WBAL-CAPABLE SESSIONS (this is the missing piece)
            df = df[
                df["icu_pm_w_prime"].notna()
                & df["icu_max_wbal_depletion"].notna()
                & df["icu_joules_above_ftp"].notna()
            ]

            if df.empty:
                return  # or just skip silently

            iso = df["start_date_local"].dt.isocalendar()
            df["year_week"] = iso["year"].astype(str) + "-W" + iso["week"].astype(str)

            with np.errstate(divide="ignore", invalid="ignore"):
                df["wbal_pct"] = df["icu_max_wbal_depletion"] / df["icu_pm_w_prime"]
                df["anaerobic_pct"] = df["icu_joules_above_ftp"] / df["icu_pm_w_prime"]

            weekly = (
                df.sort_values("wbal_pct", ascending=False)
                .groupby("year_week", as_index=False)
                .first()
            )

            semantic["wbal_summary"] = {
                "mean_wbal_depletion_pct": round(float(weekly["wbal_pct"].mean()), 3),
                "mean_anaerobic_contrib_pct": round(float(weekly["anaerobic_pct"].mean()), 3),
                "weeks_with_wbal_data": int(len(weekly)),
                "basis": "weekly peak session",
                "window": "per-week max over season",
            }


    # =========================================================
    # GENERAL PERFORMANCE SUMMARIES (unchanged)
    # =========================================================
    df_ev = pd.DataFrame(semantic["events"])
    if not df_ev.empty:
        perf_fields = {
            "IF": "mean_IF",
            "icu_intensity": "mean_intensity",
            "icu_efficiency_factor": "mean_efficiency_factor",
            "decoupling": "mean_decoupling",
            "icu_power_hr": "mean_power_hr_ratio",
        }

        perf_summary = {}
        for in_name, out_name in perf_fields.items():
            if in_name in df_ev.columns:
                debug(context, f"[SEMANTIC-SUMMARY] Computing mean for {in_name}, dtype={df_ev[in_name].dtype}")
                try:
                    val_series = pd.to_numeric(df_ev[in_name], errors="coerce")
                    perf_summary[out_name] = round(float(val_series.mean(skipna=True) or 0), 3)
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

        # ---------------------------------------------------------
        # 🔮 Tier-3 FUTURE FORECAST (PLAN-AWARE, CORRECT LOCATION)
        # ---------------------------------------------------------
        context["calendar"] = calendar_data  # ✅ REQUIRED — Tier-3 reads THIS

        if not context.get("future_forecast"):
            from audit_core.tier3_future_forecast import run_future_forecast
            forecast_output = run_future_forecast(context)

            if isinstance(forecast_output, dict):
                context.update(forecast_output)
                semantic["future_forecast"] = forecast_output.get("future_forecast", {})
            else:
                semantic["future_forecast"] = {}
        else:
            semantic["future_forecast"] = context.get("future_forecast", {})

        # ✅ Meta info for structured UI rendering
        semantic["meta"]["planned_events"] = {
            "is_planned_events_block": True,
            "planned_events_block_count": len(semantic["planned_events"]),
            "notes": "Canonical planned events block (URF v5.2) — intended for ChatGPT / structured UI rendering."
        }

    else:
        semantic["planned_events"] = []
        semantic["planned_summary_by_date"] = {}
        semantic["future_forecast"] = {}
        semantic["meta"]["planned_events"] = {
            "is_planned_events_block": False,
            "planned_events_block_count": 0,
            "notes": "No planned events found or calendar source unavailable."
        }
        debug(context, "[SEMANTIC] ⚠️ No valid planned events found")

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

    # ---------------------------------------------------------
    # ✅ SAFETY PATCH — Ensure Polarisation metric uses CHEAT_SHEET metadata only
    # ---------------------------------------------------------
    try:
        # Prefer most specific Tier-2 values in priority order
        value = (
            context.get("Polarisation_seiler")
            or context.get("Polarisation")
            or context.get("Polarisation_fused")
            or context.get("Polarisation_combined")
        )

        # Detect which variant name is available in context
        variant = next(
            (k for k in [
                "Polarisation_seiler",
                "Polarisation",
                "Polarisation_fused",
                "Polarisation_combined"
            ] if k in context),
            "Polarisation"
        )

        if value is not None:
            # --- Build metric block dynamically ---
            metric_block = semantic_block_for_metric("Polarisation", value, context)

            # All metadata dynamically pulled from CHEAT_SHEET
            display_name = CHEAT_SHEET["display_names"].get(variant, variant)
            thresholds = CHEAT_SHEET["thresholds"].get(variant, CHEAT_SHEET["thresholds"].get("Polarisation", {}))
            context_text = CHEAT_SHEET["context"].get(variant, CHEAT_SHEET["context"].get("Polarisation"))
            coaching_text = CHEAT_SHEET["coaching_links"].get(variant, CHEAT_SHEET["coaching_links"].get("Polarisation"))

            metric_block.update({
                "display_name": display_name,
                "framework": "Seiler 80/20 Model",
                "thresholds": thresholds,
                "interpretation": context_text,
                "coaching_implication": coaching_text,
            })

            semantic["metrics"]["Polarisation"] = metric_block
            debug(context, f"[SEMANTIC] ✅ Polarisation ({variant}) injected = {value}")

        else:
            debug(context, "[SEMANTIC] ⚠️ No Polarisation value found in context")

    except Exception as e:
        debug(context, f"[SEMANTIC] ❌ Polarisation patch failed: {e}")



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
    # 🌤️ Copy future actions to semantic structure
    # ---------------------------------------------------------
    if context.get("actions_future"):
        semantic["future_actions"] = context["actions_future"]
        debug(context, f"[SEMANTIC] 🌤️ Added {len(context['actions_future'])} future actions to semantic JSON.")
    else:
        semantic["future_actions"] = []
        debug(context, "[SEMANTIC] ⚠️ No future actions found for semantic JSON.")


    # ---------------------------------------------------------
    # 🧭 COACHING ACTIONS (Tier-2 guidance)
    # ---------------------------------------------------------
    semantic["actions"] = context.get("actions", [])
    
    # ---------------------------------------------------------
    # 🧩 Merge Tier-3 Future Actions (if available)
    # ---------------------------------------------------------
#    if context.get("actions_future"):
#        debug(
#            context,
#            f"[SEMANTIC] 🔮 Merging {len(context['actions_future'])} future actions into canonical list."
#        )
#        semantic.setdefault("actions", [])
#       semantic["actions"].extend(context["actions_future"])
#   else:
#        debug(context, "[SEMANTIC] ⚠️ No actions_future found after Tier-3 injection.")

    # ---------------------------------------------------------
    # 🧠 INSIGHTS (computed once, after all metrics resolved)
    # ---------------------------------------------------------
    # ✅ pass weekly phase detail (not macro) to insight view
    full_phases_for_view = (
        semantic.get("weekly_phases")
        or semantic.get("phases_detail")
        or []
    )
    semantic["insight_view"] = build_insight_view({
        **semantic,
        "phases_detail": full_phases_for_view
    })

    semantic["context_ref"] = context


    # ---------------------------------------------------------
    # 🧹 CLEANUP — ensure only one authoritative actions section
    # ---------------------------------------------------------
    if "insight_view" in semantic and isinstance(semantic["insight_view"], dict):
        if "actions" in semantic["insight_view"]:
            del semantic["insight_view"]["actions"]

    if "actions" in semantic and isinstance(semantic["actions"], list):
        semantic.setdefault("meta", {})
        semantic["meta"]["has_actions"] = bool(semantic["actions"])

    # ----------------------------------------------------------
    # Cleanup Phases for weekly and wellness
    # ----------------------------------------------------------
    if semantic["meta"]["report_type"] in ("weekly", "wellness"):
        if "insight_view" in semantic and "phases" in semantic["insight_view"]:
            del semantic["insight_view"]["phases"]
            debug(context, "[SEMANTIC] Pruned phases from insight_view (short-term report)")

    # ---------------------------------------------------------
    # 🧩 Echo render options for transparency
    # ---------------------------------------------------------
    if "render_options" in context:
        semantic["options"] = context["render_options"]

    # ---------------------------------------------------------
    # 🧭 Phase Structure Normalisation (URF v5.1 — Science-Aligned)
    # ---------------------------------------------------------
    """
    Scientific alignment:
    - Issurin, V. (2008): Block Periodization of Training Cycles
    - Seiler, S. (2010, 2019): Hierarchical Organization of Endurance Training
    - Mujika & Padilla (2003): Tapering and Peaking for Performance
    - Banister, E.W. (1975): Impulse–Response Model
    - Foster, C. et al. (2001): Monitoring Training Load with session RPE

    ✅ phases → week-by-week (TSS, hours, distance, CTL, ATL, TSB)
    ✅ phases_summary → macro roll-up (duration, total load, descriptors)
    """

    report_type = semantic["meta"].get("report_type")


    # ---------------------------------------------------------
    # 🌍 Season / Summary → full weekly + roll-up
    # ---------------------------------------------------------
    if report_type in ("season", "summary"):
        raw_weeks = semantic.get("weekly_phases", [])
        if not raw_weeks:
            debug(context, "[PHASES] ⚠️ No weekly data; skipping normalisation")
            semantic["phases_summary"], semantic["phases"] = [], []
        else:
            df_weeks = pd.DataFrame(raw_weeks)

            # Derive start/end for each ISO week
            def week_to_dates(week_label):
                try:
                    y, wk = str(week_label).split("-W")
                    start = pd.Timestamp.fromisocalendar(int(y), int(wk), 1)
                    end = start + pd.Timedelta(days=6)
                    return start, end
                except Exception:
                    return pd.NaT, pd.NaT

            df_weeks[["start", "end"]] = df_weeks["week"].apply(lambda w: pd.Series(week_to_dates(w)))

            # -----------------------------------------------------
            # 🧩 Inject CTL/ATL/TSB per week (from df_light / df_master)
            # -----------------------------------------------------
            ctl_src = pd.DataFrame()
            for key in ["df_light", "df_master"]:
                if isinstance(context.get(key), pd.DataFrame) and not context[key].empty:
                    df_tmp = context[key].copy()

                    # Normalise Intervals fields
                    rename_map = {
                        "icu_ctl": "CTL",
                        "icu_atl": "ATL",
                        "icu_training_load": "tss"
                    }
                    df_tmp.rename(columns=rename_map, inplace=True)

                    # Compute TSB dynamically if missing
                    if "TSB" not in df_tmp.columns and all(c in df_tmp.columns for c in ["CTL", "ATL"]):
                        df_tmp["TSB"] = df_tmp["CTL"] - df_tmp["ATL"]

                    # Find the best date column
                    date_col = None
                    for c in ["start_date_local", "start_date", "date"]:
                        if c in df_tmp.columns:
                            date_col = c
                            break

                    if date_col:
                        ctl_src = df_tmp[[date_col, "CTL", "ATL", "TSB"]].copy()
                        ctl_src.rename(columns={date_col: "date"}, inplace=True)
                    break

            # -----------------------------------------------------
            # Aggregate by ISO week
            # -----------------------------------------------------
            if not ctl_src.empty:
                ctl_src["date"] = pd.to_datetime(ctl_src["date"], errors="coerce")
                ctl_src["year_week"] = (
                    ctl_src["date"].dt.isocalendar().year.astype(str)
                    + "-W"
                    + ctl_src["date"].dt.isocalendar().week.astype(str)
                )
                df_ctl = (
                    ctl_src.groupby("year_week", as_index=False)
                    .agg({"CTL": "mean", "ATL": "mean", "TSB": "mean"})
                )
                df_ctl.columns = ["week", "ctl", "atl", "tsb"]
                df_weeks = df_weeks.merge(df_ctl, on="week", how="left")

                # Diagnostic
                debug(
                    context,
                    f"[PHASES] ✅ Injected CTL/ATL/TSB from {key} "
                    f"({len(df_ctl)} weekly rows) — mean TSB={df_ctl['tsb'].mean():.2f}"
                )
            else:
                ctl_val = semantic.get("extended_metrics", {}).get("CTL", {}).get("value", 0.0)
                atl_val = semantic.get("extended_metrics", {}).get("ATL", {}).get("value", 0.0)
                tsb_val = ctl_val - atl_val
                df_weeks["ctl"], df_weeks["atl"], df_weeks["tsb"] = ctl_val, atl_val, tsb_val
                debug(context, "[PHASES] ⚠️ No df_light/df_master — fallback static CTL/ATL/TSB")

            # -----------------------------------------------------
            # Classify per week using TSB thresholds
            # -----------------------------------------------------
            tsb_thresholds = CHEAT_SHEET.get("thresholds", {}).get("TSB", {})

            def classify_tsb(tsb_value):
                for label, (lo, hi) in tsb_thresholds.items():
                    if lo <= tsb_value < hi:
                        return label.capitalize()
                return "Unknown"

            df_weeks["classification"] = df_weeks["tsb"].apply(classify_tsb)

            # -----------------------------------------------------
            # 🔗 Propagate calc_method / calc_context from detect_phases()
            # -----------------------------------------------------
            if "phases" in context and isinstance(context["phases"], list) and len(context["phases"]) > 0:
                df_detected = pd.DataFrame(context["phases"])
                if not df_detected.empty:
                    # 🩹 Ensure columns exist in df_weeks before assignment
                    if "calc_method" not in df_weeks.columns:
                        df_weeks["calc_method"] = None
                    if "calc_context" not in df_weeks.columns:
                        df_weeks["calc_context"] = None

                    # Match by overlapping date ranges
                    for idx, row in df_weeks.iterrows():
                        wk_start, wk_end = row["start"], row["end"]
                        matched = df_detected[
                            (pd.to_datetime(df_detected["start"]) <= wk_end)
                            & (pd.to_datetime(df_detected["end"]) >= wk_start)
                        ]
                        if not matched.empty:
                            df_weeks.at[idx, "calc_method"] = matched.iloc[-1].get("calc_method")

                            context_val = matched.iloc[-1].get("calc_context")
                            # ✅ Safe assignment for dict values (keeps them scalar)
                            df_weeks.at[idx, "calc_context"] = (
                                context_val if isinstance(context_val, (dict, type(None))) else dict(context_val)
                            )

                    debug(context, f"[PHASES] 🔄 Propagated calc_method/context into weekly roll-up")



            # -----------------------------------------------------
            # 🧮 Macro-level roll-up (phases_summary) — sequential, boundary-aware
            # -----------------------------------------------------
            summaries = []
            advice = CHEAT_SHEET.get("advice", {}).get("PhaseAdvice", {})

            # 🧭 Sort by start date for deterministic order
            df_weeks = df_weeks.sort_values("start").reset_index(drop=True)

            current_phase = None
            segment_rows = []

            for _, wk in df_weeks.iterrows():
                # fill Unclassified with previous phase if possible (prevents fragmentation)
                if wk["phase"] == "Unclassified" and current_phase is not None:
                    wk["phase"] = current_phase

                if current_phase is None:
                    current_phase = wk["phase"]
                    segment_rows = [wk]
                    continue

                # 🚧 Phase change — flush previous block
                if wk["phase"] != current_phase:
                    seg = pd.DataFrame(segment_rows)
                    if not seg.empty:
                        summaries.append({
                            "phase": current_phase,
                            "start": seg["start"].min().strftime("%Y-%m-%d"),
                            "end": seg["end"].max().strftime("%Y-%m-%d"),
                            "duration_days": int((seg["end"].max() - seg["start"].min()).days) + 1,
                            "duration_weeks": round((seg["end"].max() - seg["start"].min()).days / 7, 1),
                            "tss_total": round(seg["tss"].sum(), 1),
                            "hours_total": round(seg["hours"].sum(), 1),
                            "distance_km_total": round(seg["distance_km"].sum(), 1),
                            "descriptor": advice.get(
                                current_phase, f"{current_phase} phase — maintain adaptive consistency."
                            ),
                            "calc_method": seg["calc_method"].iloc[-1] if "calc_method" in seg else None,
                            "calc_context": (
                                seg["calc_context"].iloc[-1]
                                if "calc_context" in seg and not isinstance(seg["calc_context"].iloc[-1], list)
                                else None
                            ),
                        })

                    # start new block
                    current_phase = wk["phase"]
                    segment_rows = [wk]
                else:
                    segment_rows.append(wk)

            # 🧩 Flush final open segment
            if segment_rows:
                seg = pd.DataFrame(segment_rows)
                summaries.append({
                    "phase": current_phase,
                    "start": seg["start"].min().strftime("%Y-%m-%d"),
                    "end": seg["end"].max().strftime("%Y-%m-%d"),
                    "duration_days": int((seg["end"].max() - seg["start"].min()).days) + 1,
                    "duration_weeks": round((seg["end"].max() - seg["start"].min()).days / 7, 1),
                    "tss_total": round(seg["tss"].sum(), 1),
                    "hours_total": round(seg["hours"].sum(), 1),
                    "distance_km_total": round(seg["distance_km"].sum(), 1),
                    "descriptor": advice.get(
                        current_phase, f"{current_phase} phase — maintain adaptive consistency."
                    ),
                    "calc_method": seg["calc_method"].iloc[-1] if "calc_method" in seg else None,
                    "calc_context": (
                        seg["calc_context"].iloc[-1]
                        if "calc_context" in seg and not isinstance(seg["calc_context"].iloc[-1], list)
                        else None
                    ),
                })

            # 🔒 Mirror totals for easy debugging and validation
            semantic["meta"]["phases_summary"] = {
                "is_phase_block": True,
                "phase_block_count": len(summaries),
                "notes": "Macro-level sequential phase summary — validated and boundary-corrected.",
            }

            semantic["phases_summary"] = summaries

            debug(
                context,
                f"[PHASES] ✅ Created {len(summaries)} macro phase blocks (merged unclassified weeks where needed)"
            )


            # Save to semantic
            semantic["meta"]["phases_summary"] = {
                "is_phase_block": True,
                "phase_block_count": len(summaries),
                "notes": "Macro-level sequential phase summary, intended for ChatGPT / structured UI rendering."
            }
            debug(context, f"[PHASES] ✅ Created {len(summaries)} sequential phase blocks (no overlaps)")
            semantic["phases_summary"] = summaries
            # -----------------------------------------------------
            # 🧩 Weekly-level detail (phases, cleaned for output)
            # -----------------------------------------------------
            df_weeks = df_weeks.sort_values(by=["start", "week"], ascending=[True, True]).reset_index(drop=True)

            # Format + clean
            weekly_output = (
                df_weeks.assign(
                    start=lambda x: pd.to_datetime(x["start"]).dt.strftime("%Y-%m-%d"),
                    end=lambda x: pd.to_datetime(x["end"]).dt.strftime("%Y-%m-%d"),
                    ctl=lambda x: x["ctl"].round(2),
                    atl=lambda x: x["atl"].round(2),
                    tsb=lambda x: x["tsb"].round(2)
                )[
                    [
                        "week", "start", "end",
                        "distance_km", "hours", "tss",
                        "ctl", "atl", "tsb", "classification"
                    ]
                ].to_dict(orient="records")
            )

            semantic["phases"] = weekly_output
            debug(context, f"[PHASES] ✅ Cleaned weekly phase output ({len(weekly_output)} weeks)")

            # ---------------------------------------------------------
            # 📈 Season / Summary Trend Metrics (URF-canonical)
            # MUST run AFTER final semantic["phases"] is built
            # ---------------------------------------------------------
            if report_type in ("season", "summary") and semantic.get("phases"):
                df = pd.DataFrame(semantic["phases"])

                def slope(series):
                    s = pd.to_numeric(series, errors="coerce").dropna()
                    if len(s) < 4:
                        return "—"
                    x = np.arange(len(s))
                    return round(float(np.polyfit(x, s, 1)[0]), 3)

                semantic["trend_metrics"] = {
                    "load_trend": slope(df["tss"]),
                    "fitness_trend": slope(df["ctl"]),
                    "fatigue_trend": slope(df["atl"]),
                }

                debug(
                    context,
                    "[TREND] Derived from FINAL weekly phases → "
                    f"{semantic['trend_metrics']}"
                )


            # -----------------------------------------------------
            # Enforce output ordering (summary before phases)
            # -----------------------------------------------------
            ordered = {}
            for k, v in semantic.items():
                if k not in ("phases_summary", "phases"):
                    ordered[k] = v
            ordered["phases_summary"] = semantic["phases_summary"]
            ordered["phases"] = semantic["phases"]

            semantic.clear()
            semantic.update(ordered)


    # ---------------------------------------------------------
    # ✅ Contract Enforcement
    # ---------------------------------------------------------
    return apply_report_type_contract(semantic)


# ==============================================================
# build_insight_view (URF v5.2+)
# Clean version – no embedded phases
# ==============================================================
from coaching_cheat_sheet import CLASSIFICATION_ALIASES

def build_insight_view(semantic):
    insights = semantic.get("insights", {})

    critical, watch, positive = [], [], []

    for key, ins in insights.items():
        cls = ins.get("classification")
        if not cls:
            continue

        color = CLASSIFICATION_ALIASES.get(cls, cls)

        entry = {
            "name": key,
            "classification": cls,
            "interpretation": ins.get("interpretation"),
            "coaching_implication": ins.get("coaching_implication"),
        }

        if color == "red":
            critical.append(entry)
        elif color == "amber":
            watch.append(entry)
        elif color == "green":
            positive.append(entry)

    if not (critical or watch or positive):
        return {
            "state": "clear",
            "message": "No items require immediate attention at this time.",
            "critical": [],
            "watch": [],
            "positive": [],
        }

    return {
        "critical": critical,
        "watch": watch,
        "positive": positive,
    }




def apply_report_type_contract(semantic: dict) -> dict:
    """
    Enforce report-type-specific semantic exposure (URF v5.1).

    Responsibilities:
    - Filter top-level semantic keys according to REPORT_CONTRACT
    - Attach renderer instructions as DATA (not enforced here)

    NOTE:
    - renderer_instructions must be promoted to a system-role message
      at the ChatGPT call site.
    """
    report_type = semantic.get("meta", {}).get("report_type", "weekly")

    # --- Enrich meta with header + resolution
    semantic["meta"]["report_header"] = REPORT_HEADERS.get(report_type, {})
    semantic["meta"]["resolution"] = REPORT_RESOLUTION.get(report_type, {})
    semantic["header"] = semantic["meta"]["report_header"]

    # --- Apply contract filtering
    allowed_keys = REPORT_CONTRACT.get(report_type, semantic.keys())
    filtered = {k: v for k, v in semantic.items() if k in allowed_keys}

    # --- Attach renderer instructions (DATA ONLY)
    filtered["renderer_instructions"] = build_system_prompt_from_header(
        report_type,
        REPORT_HEADERS.get(report_type, {})
    )

    # --- Optional contract drift detection
    unexpected = set(semantic.keys()) - set(allowed_keys)
    if unexpected:
        from audit_core.utils import debug
        debug(
            {},
            f"[CONTRACT] ⚠️ Unexpected keys in '{report_type}' report: {unexpected}"
        )

    return filtered

def build_system_prompt_from_header(report_type: str, header: dict) -> str:
    """
    Build deterministic renderer instructions for GPT based on the
    URF v5.1 report contract.

    This output is DATA ONLY and must be used as a system-role message
    by the caller.
    """
    from coaching_profile import RENDERER_PROFILES
    from textwrap import dedent

    title = header.get("title", f"{report_type.title()} Report")
    scope = header.get("scope", "Training and wellness summary")
    sources = header.get("data_sources", "Intervals.icu activity and wellness datasets")
    intended = header.get("intended_use", "General endurance coaching insight")
    contract_sections = REPORT_CONTRACT.get(report_type, [])
    contract_version = "URF v5.1"

    # --------------------------------------------------
    # Resolve section order from contract
    # --------------------------------------------------
    if isinstance(contract_sections, dict):
        section_order = list(contract_sections.keys())
    else:
        section_order = contract_sections or ["Summary", "Metrics", "Actions"]

    manifest_lines = [f"{i}. {section}" for i, section in enumerate(section_order, start=1)]

    # --------------------------------------------------
    # Resolve renderer profiles
    # --------------------------------------------------
    global_profile = RENDERER_PROFILES.get("global", {})
    report_profile = RENDERER_PROFILES.get(report_type, {})

    hard_rules = global_profile.get("hard_rules", [])
    list_rules = global_profile.get("list_rules", [])
    tone_rules = global_profile.get("tone_rules", [])

    interpretation_rules = report_profile.get("interpretation_rules", [])
    allowed_enrichment = report_profile.get("allowed_enrichment", [])

    coaching_cfg = report_profile.get("coaching_sentences", {})
    coaching_enabled = coaching_cfg.get("enabled", False)
    coaching_max = coaching_cfg.get("max_per_section", 0)

    section_handling = report_profile.get("section_handling", {})

    # ➕ NEW: presentation config (read directly, no helpers)
    state_presentation = global_profile.get("state_presentation", {})
    emphasis = report_profile.get("emphasis", {})
    framing = report_profile.get("framing", {})

    # --------------------------------------------------
    # Optional blocks (existing)
    # --------------------------------------------------
    coaching_block = ""
    if coaching_enabled and coaching_max > 0:
        coaching_block = dedent(f"""
        COACHING INTERPRETATION RULES:
        - You MAY include up to {coaching_max} short coaching sentence(s) per section.
        - Coaching sentences MUST be directly anchored to values, states, or interpretation fields in that section.
        - Coaching sentences MUST be descriptive or conditional, not predictive.
        - Coaching sentences MUST appear immediately after the section’s data and before the next divider.
        - Coaching sentences MUST NOT introduce new metrics.
        """).strip()

    enrichment_block = ""
    if allowed_enrichment:
        enrichment_block = dedent(f"""
        ALLOWED ENRICHMENT:
        {chr(10).join(f"- {r}" for r in allowed_enrichment)}
        """).strip()

    section_handling_block = ""
    if section_handling:
        section_handling_block = dedent(f"""
        SECTION HANDLING RULES:
        {chr(10).join(f"- {k}: {v}" for k, v in section_handling.items())}

        Handling meanings:
        - full: render entire section exactly as provided
        - summary: summarise using existing semantic aggregates only
        - forbid: do NOT render this section

        EVENTS (WEEKLY — NON-NEGOTIABLE):
        - The events section MUST be rendered as a Markdown table.
        - EVERY event in the semantic JSON MUST appear as exactly one row.
        - The events section MUST NOT be summarised, renamed, grouped, or rewritten.
        - Bullet points, highlights, or narrative descriptions of events are FORBIDDEN.
        - Coaching sentences for events, if enabled, MUST appear AFTER the table.
        - Convert duration from seconds to minutes at render time.
        - Display as integer minutes by default.
        - Use one decimal only if duration < 30 minutes and precision is useful.
        - Label column as Duration (min).
        PLANNED EVENTS (WEEKLY — NON-NEGOTIABLE):
        - The planned_events section MUST be rendered as a Markdown table.
        - EVERY planned event in the semantic JSON MUST appear as exactly one row.
        - The planned_events section MUST NOT be summarised, renamed, grouped, or rewritten.
        - Narrative descriptions of planned events are FORBIDDEN.
        - Coaching sentences for planned_events, if enabled, MUST appear AFTER the table.
        """).strip()

    # --------------------------------------------------
    # inline presentation blocks
    # --------------------------------------------------
    state_presentation_block = ""
    if state_presentation.get("enabled"):
        state_presentation_block = dedent(f"""
        STATE PRESENTATION:
        - Present a concise, single-sentence state banner at the top of the report.
        - Use ONLY semantic states already present in the data.
        - Do NOT derive, compute, or infer new states.
        - Style: {state_presentation.get("style")}
        """).strip()

    emphasis_block = ""
    if emphasis:
        emphasis_block = dedent(f"""
        EMPHASIS GUIDANCE:
        The following sections should receive proportional narrative and visual emphasis.
        This does NOT change section order, inclusion, or data fidelity.
        {chr(10).join(f"- {k}: {v}" for k, v in emphasis.items())}
        """).strip()

    framing_block = ""
    if framing:
        framing_block = dedent(f"""
        FRAMING INTENT:
        - Interpret and summarise this report through the following intent:
          {framing.get("intent")}
        - This intent guides prioritisation and narrative focus only.        
        """).strip()

    # --------------------------------------------------
    # Assemble final prompt
    # --------------------------------------------------
    prompt = dedent(f"""
    You are a deterministic URF renderer.

    You must render a **{title}** using the embedded system context.
    This report follows the **Unified Reporting Framework ({contract_version})**.

    **Scope:** {scope}
    **Data Sources:** {sources}
    **Intended Use:** {intended}

    HARD RULES:
    {chr(10).join(f"- {r}" for r in hard_rules)}

    INTERPRETATION RULES:
    {chr(10).join(f"- {r}" for r in interpretation_rules)}

    {coaching_block}

    {enrichment_block}

    {state_presentation_block}

    {emphasis_block}

    {framing_block}

    {section_handling_block}

    LIST RENDERING RULES (NON-NEGOTIABLE):
    {chr(10).join(f"- {r}" for r in list_rules)}

    TONE AND STYLE:
    {chr(10).join(f"- {r}" for r in tone_rules)}

    SECTION ORDER (INSTRUCTIONAL — DO NOT NUMBER HEADERS):
    {chr(10).join(manifest_lines)}

    End with a factual closing note on recovery or adaptation
    based strictly on the provided data.
    """).strip()

    return prompt





