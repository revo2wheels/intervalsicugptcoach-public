"""
semantic_json_builder.py
------------------------

Builds a FULL semantic DICT coaching graph based on the Unified Reporting
Framework v5.1, Coaching Profile, Coaching Cheat Sheet, and all Tier-2/3 modules.

"""
import json, math, copy
from datetime import datetime, date, timezone, timedelta
import pandas as pd
from math import isnan
from coaching_cheat_sheet import CHEAT_SHEET
from coaching_profile import COACH_PROFILE, REPORT_HEADERS, REPORT_RESOLUTION, REPORT_CONTRACT, PRUNE_RULES
from audit_core.utils import debug
import numpy as np
from math import isnan
import pytz
from audit_core.tier2_derived_metrics import classify_marker
from textwrap import dedent
from questions_engine import detect_signals, select_question, generate_question, dominant_signal
from audit_core.utils import set_time_context
from prompt_builder import build_system_prompt_from_header
from audit_core.tier3_trail_execution import (
    evaluate_rules,
    classify_execution
)
from coach_trail_rules import TRAIL_DEFAULTS
from audit_core.tier3_future_forecast import run_future_forecast
from audit_core.tier2_actions import build_future_projected_weeks
from audit_core.event_readiness import estimate_event_ctl_atl_from_calendar_ewma

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def classify_wbal_pattern(row: dict) -> dict:
    """
    Classify W′ engagement pattern for a single activity.
    Deterministic, Tier-2 safe.
    """
    wprime = row.get("icu_pm_w_prime")
    max_dep = row.get("icu_max_wbal_depletion")
    joules = row.get("icu_joules_above_ftp")
    duration = row.get("moving_time") or 0
    strain = row.get("strain_score") or 0
    IF = row.get("icu_intensity") or 0

    if wprime is None or max_dep is None or joules is None:
        return {
            "wbal_engagement": "none",
            "wbal_pattern": "none",
            "wbal_depth_pct": 0.0,
        }

    depth_pct = max_dep / wprime
    density = joules / max(duration, 1)

    # --- engagement ---
    thr = CHEAT_SHEET["thresholds"]["WBalDepletion"]
    g_low, g_high = thr["green"]
    a_low, a_high = thr["amber"]

    if depth_pct < g_high:
        engagement = "light"
    elif depth_pct < a_high:
        engagement = "moderate"
    else:
        engagement = "heavy"

    # --- pattern ---
    if joules < 0.1 * wprime:
        pattern = "single"
    elif density > 5 and IF > 0.85: #changed from strain to IF
        pattern = "stochastic"
    elif duration > 3600 and depth_pct > 0.3:
        pattern = "progressive"
    else:
        pattern = "repeated"

    return {
        "wbal_engagement": engagement,
        "wbal_pattern": pattern,
        "wbal_depth_pct": round(depth_pct, 3),
    }

def classify_event_efficiency(ev: dict) -> dict:
    """
    Classify per-activity efficiency using icu_efficiency_factor.
    Uses canonical thresholds from CHEAT_SHEET.
    """

    ef = ev.get("icu_efficiency_factor")

    if ef is None:
        return {
            "event_efficiency": "unknown",
            "event_efficiency_value": None,
        }

    try:
        ef = float(ef)
    except Exception:
        return {
            "event_efficiency": "unknown",
            "event_efficiency_value": None,
        }

    thr = CHEAT_SHEET["thresholds"]["EfficiencyFactor"]

    g_low, g_high = thr["green"]
    a_low, a_high = thr["amber"]
    r_low, r_high = thr["red"]

    if g_low <= ef <= g_high:
        state = "efficient"
    elif a_low <= ef < g_low:
        state = "moderate"
    elif r_low <= ef < a_low:
        state = "inefficient"
    else:
        state = "unknown"

    return {
        "event_efficiency": state,
        "event_efficiency_value": round(ef, 3),
    }


def resolve_metric_confidence(metric_key, context, cheat_sheet):
    rules = cheat_sheet.get("metric_confidence", {}).get(metric_key)
    if not rules:
        return "high"

    confidence = rules.get("default", "high")
    conditions = rules.get("high_confidence_when", {})

    phase = context.get("current_phase")
    total_sessions = context.get("total_sessions", 0)
    intensity_sessions = context.get("intensity_sessions", 0)
    dominant_sport = context.get("dominant_sport")

    if conditions:
        if phase not in conditions.get("phases", [phase]):
            return confidence
        if total_sessions < conditions.get("min_sessions", 0):
            return confidence
        if intensity_sessions < conditions.get("min_intensity_sessions", 0):
            return confidence
        if conditions.get("dominant_sport_required") and not dominant_sport:
            return confidence

        return "high"

    return confidence


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
    import math

    metric_name = str(name).strip()

    # 🔥 NEW: pull derived metric context
    derived_info = context.get("derived_info", {})

    # --- Canonical resolution (for context + coaching only) ---
    canonical_map = CHEAT_SHEET.get("metric_groups", {})
    canonical_name = canonical_map.get(metric_name, metric_name)

    # --- Thresholds MUST use metric_name ---
    base_thresholds = copy.deepcopy(
        CHEAT_SHEET["thresholds"].get(metric_name, {})
    )

    # --- Phase overrides (only if defined per metric) ---
    phase_overrides = CHEAT_SHEET.get("phase_thresholds", {}).get(metric_name, {})

    profile_desc = COACH_PROFILE["markers"].get(metric_name, {})

    # 🔥 UPDATED: merge priority (Tier → Cheat Sheet → Profile)
    interpretation = (
        derived_info.get("interpretation")
        or derived_info.get("notes")
        or CHEAT_SHEET["context"].get(canonical_name)
        or profile_desc.get("interpretation")
    )

    coaching_link = (
        derived_info.get("coaching_implication")
        or CHEAT_SHEET["coaching_links"].get(canonical_name)
        or profile_desc.get("coaching_implication")
    )

    display_name = CHEAT_SHEET.get("display_names", {}).get(metric_name, metric_name)

    phase = (
        context.get("current_phase")
        or context.get("phase_name")
    )

    if phase:
        phase = phase.lower()

    semantic_state = None
    classification = "unknown"
    active_thresholds = {}

    try:
        if value is None or (isinstance(value, (float, int)) and math.isnan(value)):
            classification = "undefined"
        else:
            v = float(value)

            # --- Phase override ---
            if phase and phase in phase_overrides:
                active_thresholds = copy.deepcopy(phase_overrides[phase])
                debug(context, f"[THRESHOLDS][{metric_name}] Using PHASE override", active_thresholds)
            else:
                active_thresholds = base_thresholds
                debug(context, f"[THRESHOLDS][{metric_name}] Using BASE thresholds", active_thresholds)

            debug(context, f"[THRESHOLDS][{metric_name}] Value", v)

            if not active_thresholds:
                debug(context, f"[THRESHOLDS][{metric_name}] EMPTY THRESHOLDS")
                # 🧠 CRITERIA FALLBACK
                criteria = profile_desc.get("criteria", {})

                semantic_state = None

                if criteria:
                    try:
                        for key, rule in criteria.items():
                            rule_clean = rule.replace("–", "-")

                            if "<" in rule_clean:
                                limit = float(rule_clean.split("<")[1].split()[0])
                                if v < limit:
                                    semantic_state = key
                                    break

                            elif ">" in rule_clean:
                                limit = float(rule_clean.split(">")[1].split()[0])
                                if v > limit:
                                    semantic_state = key
                                    break

                            elif "-" in rule_clean:
                                low, high = rule_clean.split("-")
                                low = float(low)
                                high = float(high.split()[0])

                                if low <= v <= high:
                                    semantic_state = key
                                    break

                        # 🔥 KEY: NO traffic light mapping
                        classification = "informational"

                    except Exception as e:
                        debug(context, f"[CRITERIA][{metric_name}] ERROR", str(e))
                        classification = "informational"
                        semantic_state = None
                else:
                    classification = "informational"
                    semantic_state = None
            else:
                green = active_thresholds.get("green")
                amber = active_thresholds.get("amber")
                red = active_thresholds.get("red")

                debug(context, f"[THRESHOLDS][{metric_name}] Bands",
                      f"green={green}",
                      f"amber={amber}",
                      f"red={red}")

                if green and green[0] <= v <= green[1]:
                    classification = "green"
                elif amber and amber[0] <= v <= amber[1]:
                    classification = "amber"
                elif red and red[0] <= v <= red[1]:
                    classification = "red"
                else:
                    # 🔥 FIX: directional overflow handling
                    if green:
                        if v < green[0]:
                            classification = "amber" if amber else "informational"
                        elif v > green[1]:
                            classification = "amber" if amber else "informational"
                        else:
                            classification = "informational"
                    else:
                        classification = "informational"

                debug(context, f"[THRESHOLDS][{metric_name}] Classification → {classification}")

    except Exception as e:
        debug(context, f"[THRESHOLDS][{metric_name}] ERROR", str(e))
        classification = "unknown"

    if metric_name == "FatigueTrend":
        classification= "informational"
        active_thresholds = {}

    return {
        "name": metric_name,
        "display_name": display_name,
        "value": convert_to_str(value),
        "framework": profile_desc.get("framework") or derived_info.get("framework") or "Unknown",
        "formula": profile_desc.get("formula"),
        "criteria": profile_desc.get("criteria", {}),
        "semantic_state": semantic_state if semantic_state else None,
        "thresholds": active_thresholds,
        "phase_context": phase,
        "classification": classification,
        "metric_confidence": resolve_metric_confidence(canonical_name, context, CHEAT_SHEET),
        "interpretation": interpretation,
        "coaching_implication": coaching_link,
        "related_metrics": profile_desc.get("related_metrics", [])
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

def resolve_planned_duration_minutes(e: dict):
    """
    Resolve planned duration from canonical schema fields.

    Priority:
    1) moving_time seconds
    2) time_target seconds
    3) duration_minutes explicit value
    4) end_date_local - start_date_local ONLY for WORKOUT

    Races may use explicit duration fields.
    Races must NOT infer duration from calendar span.
    Notes / holidays / availability markers must not create duration.
    """

    category = str(e.get("category") or "").upper()

    if e.get("moving_time") not in (None, "", 0):
        try:
            return round(float(e["moving_time"]) / 60, 1)
        except Exception:
            pass

    if e.get("time_target") not in (None, "", 0):
        try:
            return round(float(e["time_target"]) / 60, 1)
        except Exception:
            pass

    if e.get("duration_minutes") not in (None, "", 0):
        try:
            return round(float(e["duration_minutes"]), 1)
        except Exception:
            pass

    # Only workouts can infer duration from start/end.
    # Race_A/B/C can have explicit duration, but not inferred all-day/multi-day span.
    if category != "WORKOUT":
        return None

    try:
        if e.get("start_date_local") and e.get("end_date_local"):
            start = pd.to_datetime(e["start_date_local"])
            end = pd.to_datetime(e["end_date_local"])
            mins = round((end - start).total_seconds() / 60, 1)

            # Prevent accidental all-day / multi-day calendar spans.
            if 0 < mins <= 480:
                return mins
    except Exception:
        pass

    return None

def resolve_training_load_pattern(metrics_groups, cheat_sheet):
    """
    Resolve a UI-safe Training Load pattern.
    This is NOT Training State and does NOT override PI/ADE.
    It only summarises the load diagnostics block.
    """

    def val(group, key):
        try:
            return metrics_groups.get(group, {}).get(key, {}).get("value")
        except Exception:
            return None

    acwr = val("load", "ACWR")
    strain = val("load", "Strain")
    fatigue = val("load", "FatigueTrend")
    stress = val("capacity", "StressTolerance")

    values = {
        "ACWR": acwr,
        "StressTolerance": stress,
        "Strain": strain,
        "FatigueTrend": fatigue,
    }

    if any(v is None for v in values.values()):
        state_key = "load_unknown"
    elif acwr > 1.5 or stress > 1.4 or strain > 4000 or fatigue > 40:
        state_key = "overload_risk"
    elif acwr > 1.3 or stress > 1.2 or strain > 3000 or fatigue > 20:
        state_key = "high_strain"
    elif acwr < 0.8 and fatigue < -20:
        state_key = "under_stimulus"
    elif 0.8 <= acwr <= 1.3 and 0.8 <= stress <= 1.2 and fatigue <= -10:
        state_key = "controlled_unload"
    elif 0.8 <= acwr <= 1.3 and 10 <= fatigue <= 20:
        state_key = "building_load"
    elif 0.8 <= acwr <= 1.3 and 0.8 <= stress <= 1.2 and strain < 2500 and -10 <= fatigue <= 10:
        state_key = "balanced_load"
    else:
        state_key = "balanced_load"

    cfg = cheat_sheet.get("training_load_pattern", {})
    meta = cfg.get("meta", {})
    states = cfg.get("states", {})

    state = states.get(state_key, states.get("load_unknown", {}))

    return {
        "key": state_key,
        "label": state.get("label", "LOAD UNKNOWN"),
        "status": state.get("status", "unknown"),
        "meaning": state.get("meaning"),
        "basis": "metrics_groups.load + metrics_groups.capacity",

        # from cheat sheet meta
        "scope": meta.get("scope", "training_load_only"),
        "context_window": meta.get("context_window", "7d_with_21_28d_baseline"),
        "description": meta.get("description"),

        # explicit non-conflict contract
        "does_not_override": [
            "performance_intelligence.training_state",
            "actions.adaptive_summary",
            "training_guidance"
        ],

        "inputs": values
    }

def resolve_physiology_state(wellness, cheat_sheet):
    """
    Resolve wellness-only physiology state.
    Does NOT override Training Load, PI training_state, or ADE.
    """

    cfg = cheat_sheet.get("physiology_state", {})
    meta = cfg.get("meta", {})
    states = cfg.get("states", {})

    def num(v):
        try:
            return float(v) if v is not None else None
        except Exception:
            return None

    hrv_ratio = num(wellness.get("hrv_ratio"))

    # Fallback: derive from nested wellness.hrv block if flat hrv_ratio is missing
    if hrv_ratio is None:
        hrv_block = wellness.get("hrv", {}) or {}
        hrv_mean = num(hrv_block.get("mean"))
        hrv_latest = num(hrv_block.get("latest"))

        if hrv_mean not in (None, 0) and hrv_latest is not None:
            hrv_ratio = round(hrv_latest / hrv_mean, 2)

    hrv_trend = num(
        wellness.get("hrv_trend")
        or wellness.get("hrv_trend_7d")
        or wellness.get("hrv", {}).get("trend_7d")
    )
    def first_present(*vals):
        for v in vals:
            if v is not None:
                return v
        return None

    rest_delta = num(first_present(
        wellness.get("resting_hr_delta"),
        wellness.get("cardiac", {}).get("resting_hr_delta")
    ))

    sleep_score = num(first_present(
        wellness.get("sleep_score"),
        wellness.get("sleep", {}).get("average_score")
    ))
    tsb = num(wellness.get("tsb"))

    subjective = wellness.get("subjective", {}) or {}
    fatigue_label = (
        subjective.get("fatigue", {}).get("label")
        if isinstance(subjective.get("fatigue"), dict)
        else None
    )
    stress_label = (
        subjective.get("stress", {}).get("label")
        if isinstance(subjective.get("stress"), dict)
        else None
    )
    soreness_label = (
        subjective.get("soreness", {}).get("label")
        if isinstance(subjective.get("soreness"), dict)
        else None
    )

    inputs = {
        "hrv_ratio": hrv_ratio,
        "hrv_trend": hrv_trend,
        "resting_hr_delta": rest_delta,
        "sleep_score": sleep_score,
        "tsb": tsb,
        "subjective_fatigue": fatigue_label,
        "subjective_stress": stress_label,
        "subjective_soreness": soreness_label,
    }

    required = [hrv_ratio, rest_delta, sleep_score, tsb]
    if all(v is None for v in required):
        state_key = "unknown"

    elif (
        hrv_ratio is not None and hrv_ratio >= 1.05
        and (rest_delta is None or rest_delta <= 2)
        and (sleep_score is None or sleep_score >= 75)
        and (tsb is None or tsb >= 0)
        and fatigue_label in (None, "low")
        and stress_label in (None, "low")
    ):
        state_key = "fresh_stable"

    elif (
        hrv_ratio is not None and hrv_ratio < 0.92
        and (rest_delta is not None and rest_delta >= 5)
    ):
        state_key = "suppressed"

    elif (
        (hrv_ratio is not None and hrv_ratio < 0.97)
        or (rest_delta is not None and rest_delta >= 3)
        or (sleep_score is not None and sleep_score < 70)
        or fatigue_label in ("high", "very_high")
        or stress_label in ("high", "very_high")
        or soreness_label in ("high", "very_high")
    ):
        state_key = "watch"

    elif (
        tsb is not None and tsb < -10
        and (
            (hrv_ratio is not None and hrv_ratio < 1.0)
            or (sleep_score is not None and sleep_score < 75)
            or (rest_delta is not None and rest_delta > 2)
        )
    ):
        state_key = "strained"

    else:
        state_key = "stable"

    state = states.get(state_key, states.get("unknown", {}))

    return {
        "key": state_key,
        "label": state.get("label", "UNKNOWN"),
        "status": state.get("status", "unknown"),
        "meaning": state.get("meaning"),
        "basis": "HRV ratio + resting HR delta + sleep + TSB + subjective signals",
        "scope": meta.get("scope", "wellness_physiology_only"),
        "context_window": meta.get("context_window", "42d wellness with current load state"),
        "description": meta.get("description"),
        "does_not_override": [
            "training_volume.load_pattern",
            "performance_intelligence.training_state",
            "actions.adaptive_summary",
            "training_guidance"
        ],
        "inputs": inputs,
        "confidence": "high" if state_key != "unknown" else "low"
    }

def apply_report_recency_governance(semantic: dict) -> dict:
    """
    Prevent stale historical weekly blocks from being interpreted
    as current tactical coaching guidance.
    """

    meta = semantic.setdefault("meta", {})

    report_type = meta.get("report_type")
    period = meta.get("period") or meta.get("date_range")
    generated_at = meta.get("generated_at", {})

    if report_type != "weekly":
        return semantic

    # Parse report end date from "YYYY-MM-DD → YYYY-MM-DD"
    report_end = None
    if isinstance(period, str) and "→" in period:
        try:
            report_end_str = period.split("→")[-1].strip()
            report_end = datetime.fromisoformat(report_end_str).date()
        except Exception:
            report_end = None

    # Parse generated local date
    generated_date = None
    local_ts = generated_at.get("local") if isinstance(generated_at, dict) else None
    if local_ts:
        try:
            generated_date = datetime.fromisoformat(local_ts).date()
        except Exception:
            generated_date = None

    if report_end is None or generated_date is None:
        meta["recency"] = {
            "mode": "unknown",
            "is_current": False,
            "staleness_days": None,
            "guidance_validity": "unknown"
        }
        return semantic

    staleness_days = (generated_date - report_end).days

    is_current = staleness_days <= 8

    meta["recency"] = {
        "mode": "current" if is_current else "historical",
        "is_current": is_current,
        "staleness_days": staleness_days,
        "report_end": report_end.isoformat(),
        "generated_date": generated_date.isoformat(),
        "guidance_validity": "current_tactical" if is_current else "historical_block_review"
    }

    if is_current:
        return semantic

    # Mark future/current planning fields as unavailable for historical blocks
    semantic["future_forecast"] = {}
    semantic["future_actions"] = []
    semantic["planned_events_7d"] = []
    semantic["planned_summary_by_iso_week"] = {}
    semantic["current_ISO_weekly_microcycle"] = None

    # STRICT: historical reports must not expose live race readiness
    semantic["event_targets"] = {
        "exists": False,
        "historical_context": True,
        "guidance_validity": "historical_block_review",
        "note": (
            "Event readiness suppressed for historical weekly block. "
            "Use a current weekly report for live race-readiness guidance."
        )
    }

    # Downgrade ADE current directive semantics
    actions = semantic.get("actions", [])
    if isinstance(actions, list):
        for action in actions:
            if isinstance(action, dict) and action.get("type") == "adaptive_summary":
                action["historical_context"] = True
                action["guidance_validity"] = "historical_block_review"
                action["directive_at_time"] = action.get("directive")
                action["directive"] = "Historical block review — not current coaching guidance"
                action["resolution"] = "historical_only"
                action["phase_constraint"] = None
                action["phase_alignment"] = "historical_only"

                # STRICT: suppress live target-event/taper guidance inside ADE too
                action["target_event_at_time"] = action.get("target_event")
                action["taper_governance_at_time"] = action.get("taper_governance")

                action["target_event"] = {
                    "exists": False,
                    "historical_context": True,
                    "guidance_validity": "historical_block_review",
                    "note": (
                        "Target-event guidance suppressed for historical weekly block. "
                        "Use a current weekly report for live event guidance."
                    )
                }

                action["taper_governance"] = {
                    "state": "historical_only",
                    "historical_context": True,
                    "guidance_validity": "historical_block_review",
                    "required_phase": None,
                    "form_status": None,
                    "event_tsb": None,
                    "target_tsb_range": None,
                    "reason": None,
                    "recommended_adjustment": None
                }

                action["recency_note"] = (
                    f"This weekly block ended {staleness_days} days before report generation. "
                    "ADE describes the historical block state only and must not be used as today's training directive."
                )


    # Replace training_guidance
    semantic["training_guidance"] = (
        "Historical weekly block only. Use current weekly report for today's coaching guidance."
    )

    return semantic

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

    if report_type != "wellness":

        # --- Metabolic (FOxI proxy) ---
        foxi = semantic.get("metrics", {}).get("FOxI", {}).get("value")

        if isinstance(foxi, (int, float)):
            foxi_block = semantic_block_for_metric("FOxI", foxi, semantic)

            insights["fat_oxidation_index"] = {
                "value": foxi,
                "window": window,
                "basis": "FOxI",
                "classification": foxi_block.get("classification"),
                "interpretation": foxi_block.get("interpretation"),
                "coaching_implication": foxi_block.get("coaching_implication"),
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
            ef_obj = adaptation.get("Efficiency Factor")

            if isinstance(ef_obj, dict):
                ef_val = ef_obj.get("value")
                ef_window = ef_obj.get("window")
                ef_basis = ef_obj.get("basis")
            else:
                ef_val = ef_obj
                ef_window = window
                ef_basis = "Power / HeartRate"

            if isinstance(ef_val, (int, float)):
                ef_block = semantic_block_for_metric("EfficiencyFactor", ef_val, semantic)

                insights["efficiency_factor"] = {
                    "value": ef_val,
                    "window": ef_window,
                    "basis": ef_basis,
                    "classification": ef_block.get("classification"),
                    "interpretation": ef_block.get("interpretation"),
                    "coaching_implication": ef_block.get("coaching_implication"),
                }

        # --- Endurance Decay (cardiac drift / decoupling) ---
        if "Endurance Decay" in adaptation:
            dec_obj = adaptation.get("Endurance Decay")

            if isinstance(dec_obj, dict):
                dec_val = dec_obj.get("value")
                dec_window = dec_obj.get("window")
                dec_basis = dec_obj.get("basis")
            else:
                dec_val = dec_obj
                dec_window = window
                dec_basis = "Cardiac drift / power–HR decoupling"

            if isinstance(dec_val, (int, float)):
                dec_block = semantic_block_for_metric("EnduranceDecay", dec_val, semantic)

                insights["endurance_decay"] = {
                    "value": dec_val,
                    "window": dec_window,
                    "basis": dec_basis,
                    "classification": dec_block.get("classification"),
                    "interpretation": dec_block.get("interpretation"),
                    "coaching_implication": dec_block.get("coaching_implication"),
                }

        trend = semantic.get("trend_metrics", {})

        # --------------------------------------------------
        # Load Trend
        # --------------------------------------------------
        lt = trend.get("load_trend")

        if isinstance(lt, (int, float)):

            insights["load_trend"] = {
                "value": round(lt, 1),
                "window": "7d vs 28d",
                "basis": "Training load change relative to baseline",
                "interpretation":
                    "Recent load rising rapidly" if lt > 20
                    else "Progressive load increase" if lt > 10
                    else "Stable training load" if lt > -10
                    else "Training load decreasing",
                "coaching_implication":
                    "Monitor fatigue accumulation if sustained."
                    if lt > 20
                    else "Healthy progression."
                    if lt > 10
                    else "Stable workload."
                    if lt > -10
                    else "Recovery phase active."
            }


        # --------------------------------------------------
        # Fitness Trend
        # --------------------------------------------------
        ft = trend.get("fitness_trend")

        if isinstance(ft, (int, float)):

            insights["fitness_trend"] = {
                "value": round(ft, 2),
                "window": "CTL slope",
                "basis": "Change in chronic training load",
                "interpretation":
                    "Fitness building steadily" if ft > 0.3
                    else "Fitness stable",
                "coaching_implication":
                    "Continue progressive overload."
                    if ft > 0.3
                    else "Maintain training consistency."
            }


        # --------------------------------------------------
        # Fatigue Trend
        # --------------------------------------------------
        fat = trend.get("fatigue_trend")

        if isinstance(fat, (int, float)):

            insights["fatigue_trend"] = {
                "value": round(fat, 2),
                "window": "ATL slope",
                "basis": "Change in short-term training stress",
                "interpretation":
                    "Fatigue accumulating" if fat > 5
                    else "Stable fatigue load",
                "coaching_implication":
                    "Monitor recovery if fatigue continues rising."
                    if fat > 5
                    else "Load appears manageable."
            }

    wellness = semantic.get("wellness", {})

    # --------------------------------------------------
    # HRV Insights (only if available)
    # --------------------------------------------------

    # --------------------------------------------------
    # Derive Resting HR delta (7d vs 28d) with fallback
    # --------------------------------------------------
    daily = semantic.get("_wellness_daily_clean", [])
    athlete_fallback_rhr = (
        semantic.get("meta", {})
        .get("athlete", {})
        .get("profile", {})
        .get("resting_hr")
    )

    rhr_7d = None
    rhr_28d = None

    if daily:
        df = pd.DataFrame(daily)

        if "rest_hr" in df.columns:
            df["rest_hr"] = pd.to_numeric(df["rest_hr"], errors="coerce")
            df = df.dropna(subset=["rest_hr"])

            if len(df) >= 7:
                rhr_7d = df.tail(7)["rest_hr"].mean()

            if len(df) >= 28:
                rhr_28d = df.tail(28)["rest_hr"].mean()

    # Primary case: full delta available
    if rhr_7d is not None and rhr_28d is not None:
        wellness["resting_hr_delta"] = round(rhr_7d - rhr_28d, 1)

    # Fallback case: no wellness data → use athlete profile RHR
    elif athlete_fallback_rhr is not None:
        wellness["resting_hr_baseline"] = round(float(athlete_fallback_rhr), 1)


    # --------------------------------------------------
    # Derive Sleep Score average (14d)
    # --------------------------------------------------
    if daily:
        df = pd.DataFrame(daily)

        if "sleepscore" in df.columns:
            df["sleepscore"] = pd.to_numeric(df["sleepscore"], errors="coerce")
            df = df.dropna(subset=["sleepscore"])

            if len(df) >= 14:
                wellness["sleep_score"] = round(
                    df.tail(14)["sleepscore"].mean(),
                    1
                )

    if wellness.get("hrv_available"):

        hrv_block = wellness.get("hrv", {})

        hrv_mean = hrv_block.get("mean")
        hrv_latest = hrv_block.get("latest")
        hrv_series = wellness.get("hrv_series", [])


        samples = (
            wellness.get("hrv_samples")
            if wellness.get("hrv_samples") is not None
            else hrv_block.get("samples", 0)
        )


        # --- HRV Deviation (authoritative Tier-2 value)
        hrv_deviation_pct = (
            semantic.get("wellness", {}).get("HRVDeviation")
            or semantic.get("wellness", {}).get("hrv_deviation")
        )


        if hrv_deviation_pct is not None:

            block = semantic_block_for_metric(
                "HRVDeviation",
                hrv_deviation_pct,
                semantic
            )

            insights["hrv_deviation_pct"] = {
                "value": hrv_deviation_pct,
                "window": "42d",
                "basis": "((latest - mean) / mean) × 100",
                "classification": block.get("classification"),
                "interpretation": block.get("interpretation"),
                "coaching_implication": block.get("coaching_implication"),
            }


        # --- HRV Stability (14d CV)
        if hrv_series and len(hrv_series) >= 7:

            df_hrv = pd.DataFrame(hrv_series)
            df_hrv["hrv"] = pd.to_numeric(df_hrv["hrv"], errors="coerce")

            recent = df_hrv.tail(14)["hrv"].dropna()

            if len(recent) >= 5:
                mean_val = recent.mean()
                std_val = recent.std()

                if mean_val > 0:
                    stability = round(1 - (std_val / mean_val), 3)
                else:
                    stability = None
                block = semantic_block_for_metric(
                    "HRVStability",
                    stability,
                    semantic
                )

                insights["hrv_stability_index"] = {
                    "value": stability,
                    "window": "14d",
                    "basis": "1 - (std / mean)",
                    "classification": block.get("classification"),
                    "interpretation": block.get("interpretation"),
                    "coaching_implication": block.get("coaching_implication"),
                }

        # --- Autonomic Status (threshold-driven)
        if hrv_mean is not None and hrv_latest is not None:

            ratio = round(hrv_latest / hrv_mean, 3)

            block = semantic_block_for_metric(
                "AutonomicStatus",
                ratio,
                semantic
            )

            insights["autonomic_status"] = {
                "value": ratio,
                "window": "42d",
                "basis": "HRV relative to 42-day mean",
                "classification": block.get("classification"),
                "interpretation": block.get("interpretation"),
                "coaching_implication": block.get("coaching_implication"),
                "confidence": block.get("metric_confidence"),
            }


    # --------------------------------------------------
    # Resting HR Delta (supports nested wellness structure)
    # --------------------------------------------------

    delta_rhr = wellness.get("resting_hr_delta")

    if delta_rhr is None:
        delta_rhr = wellness.get("cardiac", {}).get("resting_hr_delta")

    if delta_rhr is not None:

        delta_rhr = round(float(delta_rhr), 1)

        rhr_block = semantic_block_for_metric(
            "RestingHRDelta",
            delta_rhr,
            semantic
        )

        insights["resting_hr_delta"] = {
            "value": delta_rhr,
            "window": "7d vs 28d",
            "basis": "Δ Resting HR",
            "classification": rhr_block.get("classification"),
            "interpretation": rhr_block.get("interpretation"),
            "coaching_implication": rhr_block.get("coaching_implication"),
        }


    # --------------------------------------------------
    # Sleep (supports nested wellness structure)
    # --------------------------------------------------
    sleep_val = (
        wellness.get("sleep_score")
        or wellness.get("sleep", {}).get("average_score")
    )

    if sleep_val is not None:

        sleep_block = semantic_block_for_metric(
            "SleepQuality",
            sleep_val,
            semantic
        )

        insights["sleep_quality"] = {
            "value": sleep_val,
            "window": "14d",
            "basis": "Average Sleep Score",
            "classification": sleep_block.get("classification"),
            "interpretation": sleep_block.get("interpretation"),
            "coaching_implication": sleep_block.get("coaching_implication"),
        }

    # --------------------------------------------------
    # NORMALISE WELLNESS SIGNALS (NEW)
    # --------------------------------------------------

    wellness_signals = {}

    if "autonomic_status" in insights:
        wellness_signals["autonomic_status"] = insights["autonomic_status"].get("classification")

    if "hrv_stability_index" in insights:
        wellness_signals["hrv_stability"] = insights["hrv_stability_index"].get("classification")

    if "sleep_quality" in insights:
        wellness_signals["sleep_quality"] = insights["sleep_quality"].get("classification")

    if "resting_hr_delta" in insights:
        wellness_signals["resting_hr"] = insights["resting_hr_delta"].get("classification")

    semantic["wellness_signals"] = wellness_signals

    # --------------------------------------------------
    # RECOVERY STATE (duplicates what we have already)
    # --------------------------------------------------

#    training_state = (
#        semantic.get("performance_intelligence", {})
#        .get("training_state", {})
#    )

#    wellness_signals = semantic.get("wellness_signals", {}) or {}
#    semantic.setdefault("performance_intelligence", {})

#    semantic["performance_intelligence"]["recovery_state"] = {
#        "state_label": training_state.get("state_label"),
#        "operational_state": training_state.get("operational_state"),
#        "autonomic_status": wellness_signals.get("autonomic_status"),
#        "hrv_stability": wellness_signals.get("hrv_stability"),
#        "sleep_quality": wellness_signals.get("sleep_quality"),
#        "resting_hr_status": wellness_signals.get("resting_hr"),
#        "load_context": training_state.get("signals", {}).get("load_recovery_state"),
#        "confidence": training_state.get("confidence")
#    }


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
    render_mode = context.get("render_mode") or options.get("render_mode", "default")
    context = set_time_context(context)
    now = context["athlete_now"]
    today = context["athlete_today"]
    tz = context["timezone"]

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
        "adaptation_metrics": {},
        "trend_metrics": {},
        "correlation_metrics": {},
        "performance_intelligence": {
            "acute": {},
            "chronic": {}
        },

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
            {
                "date": str(row.get("date")),
                "tss": float(row["icu_training_load"])
                if row.get("icu_training_load") not in (None, "")
                and not pd.isna(row.get("icu_training_load"))
                else 0.0
            }
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
                #"dominant_sport": context.get("polarisation_sport", "Unknown"),
                "basis": "Sport-specific fusion of power and HR zones (power preferred, HR fallback)",
            }
            debug(context, f"[SEMANTIC] Injected fused zones → sports={list(context['zone_dist_fused'].keys())}")
        else:
            semantic["zones"]["fused"] = {
                "per_sport": {},
                #"dominant_sport": None,
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
            block["metric_confidence"] = resolve_metric_confidence(
                metric_key,
                context,
                CHEAT_SHEET
            )

            # canonical enrichment — merge with COACH_PROFILE definitions
            profile_def = COACH_PROFILE["markers"].get(metric_key, {})

            block.update({
                "display_name": cs["display_names"].get(metric_key, metric_key),
                "basis": basis,
                "source": source,
                "framework": profile_def.get("framework", "Physiological"),
                "formula": profile_def.get("formula"),
                "thresholds": copy.deepcopy(block.get("thresholds", {})),
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
                f"Fused HR+Power",
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

        # --- Explicit context window for Polarisation variants (weekly, contextual)
        if "Polarisation_variants" in semantic.get("metrics", {}):
            for v in semantic["metrics"]["Polarisation_variants"].values():
                if isinstance(v, dict):
                    v["context_window"] = "7d"

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
        # Weekly report:
        # - FULL 7d is for execution/events
        # - LIGHT 90d is for athlete sport identity / dominant sport
        df_light_90d = context.get("_df_light_90d")
        df_light = context.get("df_light")

        if isinstance(df_light_90d, pd.DataFrame) and not df_light_90d.empty:
            df_ref = df_light_90d
            debug(context, f"[SEMANTIC] Weekly profile sport source → _df_light_90d rows={len(df_ref)}")

        elif isinstance(df_light, pd.DataFrame) and not df_light.empty:
            df_ref = df_light
            debug(context, f"[SEMANTIC] Weekly profile sport source → df_light rows={len(df_ref)}")

        elif isinstance(context.get("activities_light"), list) and len(context["activities_light"]) > 0:
            df_ref = pd.DataFrame(context["activities_light"])
            debug(context, f"[SEMANTIC] Weekly profile sport source → activities_light rows={len(df_ref)}")

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
    if report_type == "weekly":
        # 🔒 Weekly report period must always be the 7-day report window.
        # Do NOT derive it from df_ref, because df_ref may be 105d light history
        # used for sport identity / phase context.
        if context.get("start") and context.get("end"):
            context["period"] = {
                "start": pd.to_datetime(context["start"]).strftime("%Y-%m-%d"),
                "end": pd.to_datetime(context["end"]).strftime("%Y-%m-%d"),
            }
            debug(
                context,
                f"[SEMANTIC] Weekly period locked from context start/end → "
                f"{context['period']['start']} → {context['period']['end']}"
            )

        elif context.get("range", {}).get("full_start") and context.get("range", {}).get("full_end"):
            context["period"] = {
                "start": pd.to_datetime(context["range"]["full_start"]).strftime("%Y-%m-%d"),
                "end": pd.to_datetime(context["range"]["full_end"]).strftime("%Y-%m-%d"),
            }
            debug(
                context,
                f"[SEMANTIC] Weekly period locked from full range → "
                f"{context['period']['start']} → {context['period']['end']}"
            )

        else:
            start_date = today - pd.Timedelta(days=6)
            end_date = today
            context["period"] = {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
            }
            debug(context, "[SEMANTIC] Weekly period defaulted to last 7 days")

    elif report_type in ("season", "summary") and context.get("window_start") and context.get("window_end"):
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
        start_date = today - pd.Timedelta(days=7)
        end_date = today
        context["period"] = {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
        }
        debug(context, "[SEMANTIC] Defaulted report period to fallback window")



    # --- Enrich meta block from authoritative REPORT_HEADERS ---
    semantic.setdefault("meta", {})
    window_days = (pd.to_datetime(context["period"]["end"]) - pd.to_datetime(context["period"]["start"])).days + 1

    header = REPORT_HEADERS.get(report_type, {})
    semantic["meta"]["report_type"] = report_type
    semantic["meta"]["render_mode"] = render_mode
    semantic["meta"]["window_days"] = window_days
    semantic["meta"]["period"] = f"{context['period']['start']} → {context['period']['end']}"
    # ---------------------------------------------------------
    # Fix header date_range (if not passed)
    # ---------------------------------------------------------
    header = context.get("report_header", {}) or {}
    period = context.get("period") or {}

    period_start = period.get("start")
    period_end = period.get("end")

    if isinstance(header, dict) and period_start and period_end:
        if header.get("date_range") in (None, "", "unknown", "not_passed"):
            header["date_range"] = f"{period_start} → {period_end}"

    semantic["meta"]["report_header"] = header

    # --- Mark summary reports as image-ready for ChatGPT ---
    if report_type == "summary":
        semantic["meta"]["summary_card_ready"] = True
    
    # ---------------------------------------------------------
    # WELLNESS BLOCK
    # ---------------------------------------------------------
    semantic["wellness"] = {
        k: handle_missing_data(v, None)
        for k, v in context.get("wellness_summary", {}).items()
    }

    # ---------------------------------------------------------
    # 📊 Wellness Coverage (Tier-2 authoritative)
    # ---------------------------------------------------------
    if "wellness_coverage" in context:
        semantic["wellness"]["coverage"] = context["wellness_coverage"]

    # ---------------------------------------------------------
    # 🧠 BUILD DAILY WELLNESS (ALL REPORTS)
    # ---------------------------------------------------------
    daily_cleaned = []

    if "wellness_daily" in context and context["wellness_daily"]:

        for row in context["wellness_daily"]:
            cleaned = {
                k: v
                for k, v in row.items()
                if v is not None
                and not (isinstance(v, float) and math.isnan(v))
            }
            if cleaned:
                daily_cleaned.append(cleaned)

    # 🔑 store for internal use (derivations)
    context["_wellness_daily_clean"] = daily_cleaned
    semantic["_wellness_daily_clean"] = daily_cleaned
    # ---------------------------------------------------------
    # 🧹 EXPOSE DAILY (WELLNESS REPORT ONLY)
    # ---------------------------------------------------------
    if context.get("report_type") == "wellness":
        semantic["wellness"]["daily"] = context.get("_wellness_daily_clean", [])

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
                    "hrv_series": dfw[["date", "hrv"]]
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
    # 🧠 Wrap subjective markers (with scale + label)
    # ---------------------------------------------------------

    SUBJECTIVE_SCALES = CHEAT_SHEET.get("subjective_scales", {})

    subjective_block = {}

    subjective_source = (
        context.get("subjective_metrics")
        or context.get("wellness_summary")
        or {}
    )

    for k, v in subjective_source.items():

        # Only process defined subjective fields
        if k not in SUBJECTIVE_SCALES:
            continue

        # 🔒 Normalize Series → scalar
        if isinstance(v, pd.Series):
            v = v.dropna()
            v = v.iloc[-1] if not v.empty else None

        # Skip invalid / empty
        if (
            v is None
            or (isinstance(v, (float, int)) and pd.isna(v))
            or (isinstance(v, (list, dict, np.ndarray)) and len(v) == 0)
            or (isinstance(v, str) and v == "")
        ):
            continue

        numeric_value = float(v)

        # Round for categorical mapping
        rounded_value = int(round(numeric_value))

        label = SUBJECTIVE_SCALES[k].get(rounded_value)

        subjective_block[k] = {
            "value": round(numeric_value, 1),
            "label": label
        }

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
        semantic["training_volume"] = {
            "hours": handle_missing_data(context.get("totalHours"), 0),
            "tss": handle_missing_data(context.get("totalTss"), 0),
            "distance_km": handle_missing_data(context.get("totalDistance"), 0),
        }

    # ---------------------------------------------------------
    # AUTHORITATIVE Tier-2 metric injection
    # ---------------------------------------------------------
    for k in (
        "trend_metrics",
        "correlation_metrics",
    ):
        if isinstance(context.get(k), dict) and context[k]:
            semantic[k] = context[k]
        else:
            semantic[k] = {}

    # ---------------------------------------------------------
    # 🧪 Lactate Measurement & Personalized Endurance Zone
    # ---------------------------------------------------------

    lactate_block = {}

    # --- Lactate summary injection
    if "lactate_summary" in context and context["lactate_summary"]:
        lactate_block["lactate"] = context["lactate_summary"]

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
        lactate_block["personalized_z2"] = context["personalized_z2"]

        debug(
            context,
            f"[SEMANTIC] Injected personalized_z2 → "
            f"{context['personalized_z2'].get('start_w')}–{context['personalized_z2'].get('end_w')}W "
            f"({context['personalized_z2'].get('start_pct')}–"
            f"{context['personalized_z2'].get('end_pct')}%), "
            f"method={context['personalized_z2'].get('method')}"
        )
    else:
        debug(context, "[SEMANTIC] No personalized_z2 data available in context")


    # --- Lactate-derived power zones
    if context.get("power_lactate"):
        lactate_block["power_lactate"] = context["power_lactate"]

        debug(
            context,
            f"[SEMANTIC] Injected power_lactate → "
            f"LT1={context['power_lactate'].get('lt1_w')}W, "
            f"LT2={context['power_lactate'].get('lt2_w')}W, "
            f"r={context['power_lactate'].get('confidence_r')}"
        )


    # --- Only attach if something exists
    if lactate_block:
        semantic.setdefault("physiology", {})
        semantic["physiology"]["lactate_calibration"] = lactate_block

    # ---------------------------------------------------------
    # 🔗 ATHLETE: identity + multi-sport profiles + context
    # ---------------------------------------------------------
    athlete = context.get("athlete_raw") or context.get("athlete") or {}

    # ---------------------------------------------------------
    # 🔧 NORMALISE sportSettings shape (list OR dict)
    # ---------------------------------------------------------
    raw_sports = athlete.get("sportSettings") or []

    if isinstance(raw_sports, dict):
        # already normalised → {ride:{}, run:{}}
        sports = list(raw_sports.values())
    elif isinstance(raw_sports, list):
        # raw Intervals format
        sports = raw_sports
    else:
        sports = []

    # ---------------------------------------------------------
    # 🧠 SPORT GROUP MAPPING (ALWAYS defined)
    # ---------------------------------------------------------
    sport_groups = CHEAT_SHEET.get("sport_groups", {})

    def match_group(types):
        if not types:
            return None

        # ensure iterable
        if isinstance(types, str):
            types = [types]

        types = set(types)

        for group, group_types in sport_groups.items():
            if types & set(group_types):
                return group

        return None

    # -----------------------------------------------------
    # 🏁 DOMINANT SPORT (LOAD-BASED)
    # -----------------------------------------------------
    load_by_group = {}

    if isinstance(df_ref, pd.DataFrame) and not df_ref.empty:
        for _, row in df_ref.iterrows():
            activity_type = row.get("type")
            if not activity_type:
                continue
            g = match_group([activity_type])
            if not g:
                continue
            load = row.get("icu_training_load", 0)

            if pd.isna(load):
                load = 0
            load_by_group[g] = load_by_group.get(g, 0) + load
    debug(context, f"[SPORT-LOAD] load_by_group={load_by_group}")
    dominant_sport_label = (
        max(load_by_group, key=load_by_group.get).lower()
        if load_by_group else None
    )

    # -----------------------------------------------------
    # ⚙️ BUILD ALL SPORT PROFILES (CONTROLLED + COMPLETE)
    # -----------------------------------------------------
    sport_profiles = {}

    for s in sports:
        if not isinstance(s, dict):
            continue

        group = match_group(s.get("types"))
        if not group:
            continue

        key = group.lower()
        mmp_model = s.get("mmp_model", {}) or {}
        custom_fields = s.get("custom_field_values", {}) or {}

        threshold_pace = s.get("threshold_pace")
        pace_units = s.get("pace_units")

        # Intervals stores run threshold pace internally as m/s
        if key == "run" and threshold_pace:
            pace_units = "M_PER_SEC"

        sport_profiles[key] = {
            # -----------------------------
            # Core physiology
            # -----------------------------
            "ftp": s.get("ftp"),
            "eftp": mmp_model.get("ftp"),
            "w_prime": s.get("w_prime"),
            "p_max": s.get("p_max"),
            "lthr": s.get("lthr"),
            "max_hr": s.get("max_hr"),

            # -----------------------------
            # Pace (THIS is what you were missing)
            # -----------------------------
            "threshold_pace": threshold_pace,
            "pace_units": pace_units,
            "pace_zones": s.get("pace_zones"),
            "pace_zone_names": s.get("pace_zone_names"),
            "pace_load_type": s.get("pace_load_type"),
            "gap_model": s.get("gap_model"),

            # -----------------------------
            # Zones
            # -----------------------------
            "power_zones": s.get("power_zones"),
            "power_zone_names": s.get("power_zone_names"),
            "hr_zones": s.get("hr_zones"),
            "hr_zone_names": s.get("hr_zone_names"),

            # -----------------------------
            # Key metadata (minimal but useful)
            # -----------------------------
            "types": s.get("types"),
            "load_order": s.get("load_order"),
            "tiz_order": s.get("tiz_order"),

            # -----------------------------
            # Performance model
            # -----------------------------
            "mmp_model": mmp_model,

            # -----------------------------
            # Custom physiology
            # -----------------------------
            "vo2max_garmin": custom_fields.get("VO2MaxGarmin"),
            "lactate_mmol_l": custom_fields.get("HrtLndLt1"),
            "lactate_power": custom_fields.get("HrtLndLt1p"),
        }
    # -----------------------------------------------------
    # 🧭 Resolve active (dominant) profile
    # -----------------------------------------------------
    if dominant_sport_label == "excluded":
        dominant_sport_label = None

    if dominant_sport_label and dominant_sport_label in sport_profiles:
        active_profile_key = dominant_sport_label
    elif "ride" in sport_profiles:
        active_profile_key = "ride"
    elif "run" in sport_profiles:
        active_profile_key = "run"
    elif sport_profiles:
        active_profile_key = next((k for k in sport_profiles.keys() if k != "excluded"), None)
    else:
        active_profile_key = None

    active_profile = sport_profiles.get(active_profile_key, {})

    # -----------------------------------------------------
    # 🌍 GLOBAL physiology (non sport-specific)
    # -----------------------------------------------------
    global_profile = {
        "resting_hr": athlete.get("icu_resting_hr"),
        "weight": athlete.get("icu_weight"),
        "height": athlete.get("height"),
        "sex": athlete.get("sex"),
    }

    # Extract commonly used values for backward compatibility
    ftp = active_profile.get("ftp")
    eftp = active_profile.get("eftp")
    lthr = active_profile.get("lthr")
    max_hr = active_profile.get("max_hr")

    vo2max_garmin = active_profile.get("vo2max_garmin")
    lactate_mmol_l = active_profile.get("lactate_mmol_l")
    lactate_power = active_profile.get("lactate_power")


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
            "email": athlete.get("email"),
            "notes": athlete.get("icu_notes"),
        },

        # -----------------------------------------------------
        # ⚙️ PROFILE (CORE PERFORMANCE MARKERS)
        # -----------------------------------------------------
        "profile": {
            # Active sport profile (backward compatible)
            "ftp": ftp,
            "eftp": eftp,
            "ftp_kg": (
                round((ftp or 0) / athlete.get("icu_weight", 1), 2)
                if ftp and athlete.get("icu_weight") else None
            ),
            "lthr": lthr,
            "max_hr": max_hr,
            "threshold_pace": active_profile.get("threshold_pace"),
            "pace_units": active_profile.get("pace_units"),

            # Sport context
            "primary_sport": active_profile_key,
            "dominant_sport": dominant_sport_label,

            # Extended fields
            "vo2max_garmin": vo2max_garmin,
            "lactate_mmol_l": lactate_mmol_l,
            "lactate_power": lactate_power,
        },

        # NEW: expose all sport profiles
        "profiles": sport_profiles,

        # NEW: expose global physiology
        "global": global_profile,

    
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
    # EVENTS (canonical → render-optimised)
    # ---------------------------------------------------------
    df_events = (
        context.get("_df_light_90d")
        if context.get("report_type") == "season"
        else context.get("_df_scope_full")
    )

    if isinstance(df_events, pd.DataFrame) and not df_events.empty:

        debug(
            context,
            f"[DEBUG-EVENTS] rows={len(df_events)} cols_sample={str(list(df_events.columns))[:100]}"
        )

        semantic["events"] = []

        for _, row in df_events.iterrows():

            ev = {}

            # ---------------------------------------------------------
            # 1️⃣ Identity
            # ---------------------------------------------------------
            name = row.get("name")
            if not name:
                continue

            ev["name"] = name
            ev["type"] = row.get("type")

            if pd.notna(row.get("start_date_local")):
                ev["start_date_local"] = convert_to_str(row["start_date_local"])

            # ---------------------------------------------------------
            # 2️⃣ Activity link + ID
            # ---------------------------------------------------------
            activity_id = row.get("id") or row.get("activity_id")

            if pd.notna(activity_id):
                try:
                    clean_id = str(int(float(activity_id)))  # removes .0 safely
                except:
                    clean_id = str(activity_id).strip()

                # raw ID (no prefix)
                ev["activity_id"] = clean_id

                # link ID (with 'i' prefix)
                link_id = clean_id if clean_id.startswith("i") else f"i{clean_id}"
                if report_type != "season":
                    ev["activity_link"] = f"https://intervals.icu/activities/{link_id}"
            else:
                ev["activity_id"] = None

            # ---------------------------------------------------------
            # 3️⃣ Core render fields (SAFE)
            # ---------------------------------------------------------
            val = row.get("moving_time")
            ev["duration"] = int(val) if pd.notna(val) else 0

            val = row.get("distance")
            ev["distance"] = round(float(val) / 1000, 1) if pd.notna(val) else 0

            val = row.get("icu_training_load")
            ev["tss"] = int(val) if pd.notna(val) else 0

            val = row.get("icu_atl")
            ev["icu_atl"] = float(val) if pd.notna(val) else 0.0

            val = row.get("icu_ctl")
            ev["icu_ctl"] = float(val) if pd.notna(val) else 0.0

            val = row.get("paired_event_id")
            ev["paired_event_id"] = str(int(val)) if pd.notna(val) else None

            val = row.get("compliance")
            ev["compliance"] = round(float(val), 2) if pd.notna(val) else None

            # ---------------------------------------------------------
            # 4️⃣ IF (icu_intensity ONLY — canonical)
            # ---------------------------------------------------------
            val = row.get("icu_intensity")

            if pd.notna(val):
                try:
                    val = float(val)
                    if val > 2:
                        val = val / 100
                    ev["IF"] = round(val, 2)
                except Exception:
                    pass

            # ---------------------------------------------------------
            # NP (SAFE)
            # ---------------------------------------------------------
            val = row.get("icu_weighted_avg_watts")
            if pd.notna(val):
                ev["NP"] = int(val)

            # ---------------------------------------------------------
            # 5️⃣ HRR (SAFE)
            # ---------------------------------------------------------
            hrr = row.get("icu_hrr.hrr")
            if pd.notna(hrr):
                ev["HRR60"] = int(hrr)

            # ---------------------------------------------------------
            # 6️⃣ Subjective (emoji only)
            # ---------------------------------------------------------
            rpe = row.get("icu_rpe")
            feel = row.get("feel")

            if pd.notna(rpe):
                try:
                    ev["rpe_emoji"] = CHEAT_SHEET["subjective_scales"]["rpe_emoji"].get(int(rpe))
                except Exception:
                    pass

            if pd.notna(feel):
                try:
                    ev["feel_emoji"] = CHEAT_SHEET["subjective_scales"]["feel_emoji"].get(int(feel))
                except Exception:
                    pass

            # ---------------------------------------------------------
            # 7️⃣ Flags (for icons only)
            # ---------------------------------------------------------

            report_type = str(context.get("report_type", "")).lower()

            # season → suppress flags entirely
            if report_type != "season":

                flags = []

                wbal = classify_wbal_pattern(row)
                if wbal.get("wbal_pattern") == "repeated":
                    flags.append("repeated")

                eff = classify_event_efficiency(row)
                if eff.get("event_efficiency") == "efficient":
                    flags.append("efficient")

                if pd.notna(hrr):
                    flags.append("hrr")

                if flags:
                    ev["flags"] = flags

            # ---------------------------------------------------------
            # Append
            # ---------------------------------------------------------
            semantic["events"].append(ev)

        # ---------------------------------------------------------
        # META
        # ---------------------------------------------------------
        semantic["meta"]["events"] = {
            "is_event_block": True,
            "event_block_count": len(semantic["events"]),
            "render": True
        }

        debug(
            context,
            f"[SEMANTIC] EVENTS: {len(semantic['events'])} events (optimised)"
        )

    else:
        debug(context, "[SEMANTIC] EVENTS: no data")

    # --- Prevent override by short df_scope_full for season/summary ---
    if semantic["meta"]["report_type"] in ("season", "summary"):
        if (
            "df_light" in context
            and isinstance(context["df_light"], pd.DataFrame)
            and not context["df_light"].empty
        ):
            df_ref = context["df_light"]
            debug(
                context,
                f"[SEMANTIC-OVERRIDE] Using df_light ({len(df_ref)} rows) "
                f"for summary/season instead of short _df_scope_full"
            )

        elif (
            "_df_scope_full" in context
            and isinstance(context["_df_scope_full"], pd.DataFrame)
            and not context["_df_scope_full"].empty
        ):
            df_ref = context["_df_scope_full"]
            debug(
                context,
                f"[SEMANTIC-OVERRIDE] Using _df_scope_full ({len(df_ref)} rows) "
                f"for summary/season"
            )

        else:
            debug(
                context,
                "[SEMANTIC-OVERRIDE] No usable season/summary dataset found — keeping existing df_ref"
            )



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
    if semantic["meta"]["report_type"] in ("season", "summary", "weekly"):

        # --- Force authoritative dataset for season/summary totals + phase aggregation ---
        if semantic["meta"]["report_type"] in ("season", "summary"):
            if (
                "df_light" in context
                and isinstance(context["df_light"], pd.DataFrame)
                and not context["df_light"].empty
            ):
                df_ref = context["df_light"]
                debug(
                    context,
                    f"[FORCE] Overriding df_ref with df_light ({len(df_ref)} rows) "
                    f"for totals/phase aggregation"
                )

            elif (
                isinstance(context.get("activities_light"), list)
                and len(context["activities_light"]) > 0
            ):
                df_ref = pd.DataFrame(context["activities_light"])
                debug(
                    context,
                    f"[FORCE] Overriding df_ref with activities_light ({len(df_ref)} rows) "
                    f"for totals/phase aggregation"
                )
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

            debug(
                context,
                f"[WEEKLY] weekly_phases sample="
                f"{weekly_phases[:2] if weekly_phases else 'EMPTY'}"
            )

            # --- Build unified weekly phase summary ---
            semantic["weekly_phases"] = weekly_phases

            # Only set totals for season / summary
            if semantic["meta"]["report_type"] in ("season", "summary"):
                total_hours = round(total_hours, 2)
                total_tss = round(total_tss, 0)
                total_distance = round(total_distance, 2)

                semantic.setdefault("training_volume", {}).update({
                    "totalHours": total_hours,
                    "totalTss": total_tss,
                    "totalDistance": total_distance,
                })

                context["locked_totalHours"] = total_hours
                context["locked_totalTss"] = total_tss
                context["locked_totalDistance"] = total_distance

                debug(
                    context,
                    f"[WEEKLY] ✅ Aggregated {len(weekly_phases)} weeks "
                    f"(weekly breakdown only — totals sourced from Tier-2 context)"
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

        semantic["wbal_summary"] = {}  # default safe

        required_cols = {
            "icu_pm_w_prime",
            "icu_max_wbal_depletion",
            "icu_joules_above_ftp",
            "start_date_local",
        }

        if isinstance(df_ev, pd.DataFrame) and not df_ev.empty and required_cols <= set(df_ev.columns):

            df_ev = df_ev[
                df_ev["icu_pm_w_prime"].notna()
                & df_ev["icu_max_wbal_depletion"].notna()
                & df_ev["icu_joules_above_ftp"].notna()
            ]

            if not df_ev.empty:

                with np.errstate(divide="ignore", invalid="ignore"):
                    wbal_pct = (
                        df_ev["icu_max_wbal_depletion"] / df_ev["icu_pm_w_prime"]
                    ).replace([np.inf, -np.inf], np.nan)

                    anaerobic_pct = (
                        df_ev["icu_joules_above_ftp"] / df_ev["icu_pm_w_prime"]
                    ).replace([np.inf, -np.inf], np.nan)

                df_ev["date"] = pd.to_datetime(df_ev["start_date_local"]).dt.date
                df_ev["depth_pct"] = wbal_pct

                daily = (
                    df_ev.groupby("date")
                    .agg({
                        "depth_pct": "max",
                        "icu_joules_above_ftp": "sum"
                    })
                    .reset_index()
                )

                def day_level(depth):
                    if pd.isna(depth):
                        return "unknown"
                    elif depth < 0.15:
                        return "low"
                    elif depth < 0.35:
                        return "moderate"
                    else:
                        return "high"

                daily["engagement"] = daily["depth_pct"].apply(day_level)

                semantic["wbal_summary"] = {
                    "mean_wbal_depletion_pct": round(float(wbal_pct.mean()), 3)
                        if not wbal_pct.dropna().empty else None,
                    "mean_anaerobic_contrib_pct": round(float(anaerobic_pct.mean()), 3)
                        if not anaerobic_pct.dropna().empty else None,
                    "sessions_with_wbal_data": int(len(df_ev)),
                    "basis": "per-session mean (W′-capable sessions only)",
                    "window": "weekly",
                    "temporal_pattern": {
                        str(r["date"]): r["engagement"]
                        for _, r in daily.iterrows()
                    },
                    "dominant_pattern": (
                        "clustered_weekend"
                        if daily["engagement"].tail(2).isin(["high"]).any()
                        else "distributed"
                    )
                }


    # =========================================================
    # SEASON / SUMMARY → weekly peak session model
    # =========================================================
    elif report_type in ("season", "summary"):

        semantic["wbal_summary"] = {}  # default safe

        df = context.get("df_light")

        required_cols = {
            "start_date_local",
            "icu_pm_w_prime",
            "icu_max_wbal_depletion",
            "icu_joules_above_ftp",
        }

        if (
            isinstance(df, pd.DataFrame)
            and not df.empty
            and required_cols <= set(df.columns)
        ):

            df = df.copy()
            df["start_date_local"] = pd.to_datetime(df["start_date_local"], errors="coerce")
            df = df.dropna(subset=["start_date_local"])

            df = df[
                df["icu_pm_w_prime"].notna()
                & df["icu_max_wbal_depletion"].notna()
                & df["icu_joules_above_ftp"].notna()
            ]

            if not df.empty:

                iso = df["start_date_local"].dt.isocalendar()
                df["year_week"] = (
                    iso["year"].astype(str) + "-W" + iso["week"].astype(str)
                )

                with np.errstate(divide="ignore", invalid="ignore"):
                    df["wbal_pct"] = (
                        df["icu_max_wbal_depletion"] / df["icu_pm_w_prime"]
                    ).replace([np.inf, -np.inf], np.nan)

                    df["anaerobic_pct"] = (
                        df["icu_joules_above_ftp"] / df["icu_pm_w_prime"]
                    ).replace([np.inf, -np.inf], np.nan)

                weekly = (
                    df.sort_values("wbal_pct", ascending=False)
                    .groupby("year_week", as_index=False)
                    .first()
                )

                semantic["wbal_summary"] = {
                    "mean_wbal_depletion_pct": round(float(weekly["wbal_pct"].mean()), 3)
                        if not weekly["wbal_pct"].dropna().empty else None,
                    "mean_anaerobic_contrib_pct": round(float(weekly["anaerobic_pct"].mean()), 3)
                        if not weekly["anaerobic_pct"].dropna().empty else None,
                    "weeks_with_wbal_data": int(len(weekly)),
                    "basis": "weekly peak session",
                    "window": "per-week max over season",
                }


    # =========================================================
    # GENERAL PERFORMANCE SUMMARIES (weekly = FULL, season = LIGHT)
    # =========================================================

    report_type = semantic["meta"]["report_type"]

    # --- Dataset selection ---
    if report_type in ("season", "summary"):
        df_ev = context.get("df_light")
    else:
        df_ev = pd.DataFrame(semantic["events"])

    if isinstance(df_ev, pd.DataFrame) and not df_ev.empty:

        # --- Fields allowed per mode ---
        if report_type in ("season", "summary"):
            perf_fields = {
                "icu_intensity": "mean_IF",
                "decoupling": "mean_decoupling",
                "icu_pm_w_prime": "mean_w_prime",
                "icu_joules_above_ftp": "mean_joules_above_ftp",
            }
        else:
            perf_fields = {
                "icu_intensity": "mean_IF",
                "icu_intensity": "mean_intensity",
                "icu_efficiency_factor": "mean_efficiency_factor",
                "decoupling": "mean_decoupling",
                "icu_power_hr": "mean_power_hr_ratio",
            }

        perf_summary = {}

        for in_name, out_name in perf_fields.items():
            if in_name in df_ev.columns:
                try:
                    val_series = pd.to_numeric(df_ev[in_name], errors="coerce")
                    perf_summary[out_name] = round(
                        float(val_series.mean(skipna=True) or 0), 3
                    )
                except Exception:
                    perf_summary[out_name] = 0

        if perf_summary:
            semantic["performance_summary"] = perf_summary

    # ---------------------------------------------------------
    # 🗓️ PLANNED EVENTS — Grouped by Date (Calendar Context)
    # ---------------------------------------------------------

    planned_events = []
    planned_summary_by_date = {}

    calendar_data = context.get("calendar")

    consumed_ids = set()

    df_actual = context.get("_df_scope_full")
    if isinstance(df_actual, pd.DataFrame) and not df_actual.empty:
        for _, row in df_actual.iterrows():
            paired_id = row.get("paired_event_id")
            if paired_id:
                consumed_ids.add(paired_id)

    if isinstance(calendar_data, list) and len(calendar_data) > 0:
        planned_by_date = {}

        for e in calendar_data:

            if not isinstance(e, dict):
                continue

            planned_id = e.get("id")

            if planned_id in consumed_ids:
                continue

            start = e.get("start_date_local") or e.get("date")

            if not start:
                continue

            # normalize to YYYY-MM-DD
            if isinstance(start, datetime):
                start = start.date().isoformat()
            elif isinstance(start, str) and "T" in start:
                start = start.split("T")[0]

            # -------------------------------------------------
            # Restrict calendar to planned horizon
            # -------------------------------------------------

            period = semantic.get("meta", {}).get("period", "")

            if "→" in period:
                _, end_str = [x.strip() for x in period.split("→")]
                report_end = pd.to_datetime(end_str).date()
            else:
                report_end = pd.to_datetime(context.get("end")).date()
            planned_start = report_end
            planned_end = report_end + pd.Timedelta(days=14)

            try:
                event_date = pd.to_datetime(start).date()
            except Exception:
                continue

            if not (planned_start <= event_date <= planned_end):
                continue
            if isinstance(start, datetime):
                start = start.date().isoformat()
            elif isinstance(start, str) and "T" in start:
                start = start.split("T")[0]

            event = {
                "id": e.get("id"),
                "uid": e.get("uid"),
                "date": start,
                "category": e.get("category", "OTHER"),
                "type": e.get("type"),
                "name": e.get("name") or e.get("title") or "Untitled",
                "description": e.get("description") or e.get("notes") or "",
                "start_date_local": e.get("start_date_local"),
                "end_date_local": e.get("end_date_local"),
                "duration_minutes": resolve_planned_duration_minutes(e),
                "icu_training_load": e.get("icu_training_load") or e.get("tss"),
                "icu_atl":  e.get("icu_atl"),
                "icu_ctl": e.get("icu_ctl"),
                "load_target": e.get("load_target"),
                "time_target": e.get("time_target"),
                "distance_target": e.get("distance_target"),
                "icu_intensity": e.get("icu_intensity"),
                "strain_score": e.get("strain_score"),
                "plan_name": e.get("plan_name"),
                "plan_workout_id": e.get("plan_workout_id"),
                "paired_activity_id": e.get("paired_activity_id"),
                "color": e.get("color"),
                "tags": e.get("tags"),
                "day_of_week": (
                    datetime.fromisoformat(start).strftime("%A")
                    if isinstance(start, str) and len(start) == 10
                    else None
                ),
            }

            # 🧹 Remove all null/NaN/empty values
            KEEP_NULL_KEYS = {"paired_activity_id"}

            event = {
                k: v
                for k, v in event.items()
                if (
                    k in KEEP_NULL_KEYS
                    or (v not in (None, "", [], {}) and not (isinstance(v, float) and isnan(v)))
                )
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

        # ---------------------------------------------------------
        # 🧠 TRAINING CONTEXT (LLM CONTROL SIGNAL — NOT CONTRACT DATA)
        # ---------------------------------------------------------

        next_3d = []
        next_7d = []

        today = pd.Timestamp.now().date()

        for e in planned_events:
            try:
                d = pd.to_datetime(e.get("start_date_local")).date()
            except Exception:
                continue

            delta = (d - today).days

            if 0 <= delta <= 3:
                next_3d.append(e)

            if 0 <= delta <= 7:
                next_7d.append(e)

        next_3d_load = sum(e.get("icu_training_load", 0) for e in next_3d)
        next_7d_load = sum(e.get("icu_training_load", 0) for e in next_7d)

        debug(
            context,
            "[SEMANTIC][CTX_MID_LOOP]",
            f"next_3d_load={next_3d_load}",
            f"next_7d_load={next_7d_load}",
            f"events_so_far={len(planned_events)}"
        )

        context["training_context"] = {
            "short_term": {
                "window": "3d",
                "load": next_3d_load,
                "sessions": len(next_3d),
                "status": (
                    "high" if next_3d_load > 180
                    else "moderate" if next_3d_load > 100
                    else "low"
                ),
                "instruction": (
                    "absorb_load"
                    if next_3d_load > 180
                    else "normal"
                )
            },
            "weekly_shape": {
                "window": "7d",
                "load": next_7d_load,
                "sessions": len(next_7d),
                "density": (
                    "dense" if len(next_7d) >= 5
                    else "balanced" if len(next_7d) >= 3
                    else "sparse"
                )
            }
        }

        # ---------------------------------------------------------
        # 🎯 EVENT TARGETS (COMPRESSED FOR LLM) + RACE CLASSIFICATION
        # ---------------------------------------------------------

        def classify_race_type(e, name):

            sport = str(e.get("type") or "").lower()

            moving_time = e.get("moving_time")
            distance = e.get("distance")

            duration_h = (
                float(moving_time) / 3600
                if moving_time is not None
                else None
            )

            distance_km = (
                float(distance) / 1000
                if distance is not None
                else None
            )

            # -----------------------------
            # 🚴 RIDING
            # -----------------------------
            if "ride" in sport:

                # Explicit intent — strongest signal
                if any(k in name for k in ["tt", "time trial"]):
                    return "tt"

                if any(k in name for k in ["crit", "circuit", "loop"]):
                    return "crit"

                if any(k in name for k in [
                    "fondo",
                    "gran fondo",
                    "sportive",
                    "etape",
                    "étape"
                ]):
                    return "fondo"

                # Structured duration fallback — only when duration exists
                if duration_h is not None:
                    if duration_h >= 3.5:
                        return "fondo"

                    if duration_h <= 1.5:
                        return "short_ride"

                    return "tt"

                # No race-shape evidence
                return "ride_general"

            # -----------------------------
            # 🏃 RUNNING
            # -----------------------------
            if "run" in sport:

                # Distance classification only when distance exists
                if distance_km is not None:
                    if distance_km >= 30:
                        return "run_marathon"
                    if distance_km >= 18:
                        return "run_half"
                    if distance_km <= 6:
                        return "run_5k"
                    if distance_km <= 12:
                        return "run_10k"

                return "run_general"

            return "unknown"


        RACE_PROFILES = {
            "fondo": {
                "priority_systems": ["durability", "aerobic"],
                "targets": {"tsb": [5, 15], "ndli": "low", "wdrm": "low-moderate"},
                "durability_bounds": {"excellent": 3, "good": 5, "moderate": 8}
            },
            "tt": {
                "priority_systems": ["threshold"],
                "targets": {"tsb": [8, 18], "ndli": "low", "wdrm": "low"},
                "durability_bounds": {"excellent": 2, "good": 4, "moderate": 6}
            },
            "crit": {
                "priority_systems": ["anaerobic", "neural"],
                "targets": {"tsb": [10, 20], "ndli": "controlled", "wdrm": "moderate"},
                "durability_bounds": {"excellent": 4, "good": 7, "moderate": 10}
            },
            "run_marathon": {
                "priority_systems": ["durability"],
                "targets": {"tsb": [5, 15], "ndli": "low", "wdrm": "low"},
                "durability_bounds": {"excellent": 3, "good": 5, "moderate": 8}
            },
            "run_half": {
                "priority_systems": ["durability"],
                "targets": {"tsb": [5, 15], "ndli": "low", "wdrm": "low"},
                "durability_bounds": {"excellent": 3, "good": 5, "moderate": 8}
            },
            "run_10k": {
                "priority_systems": ["vo2"],
                "targets": {"tsb": [8, 18], "ndli": "controlled", "wdrm": "moderate"},
                "durability_bounds": {"excellent": 4, "good": 7, "moderate": 10}
            },
            "run_5k": {
                "priority_systems": ["anaerobic", "vo2"],
                "targets": {"tsb": [10, 20], "ndli": "controlled", "wdrm": "moderate"},
                "durability_bounds": {"excellent": 5, "good": 8, "moderate": 12}
            }
        }

        event_targets = {
            "exists": False,
            "next_event": {
                "id": None,
                "shared_event_id": None,
                "name": None,
                "category": None,
                "priority": None,
                "icu_atl": None,
                "icu_ctl": None,
                "type": None,
                "load": None,
                "intensity": None,
                "distance": None,
                "moving_time": None,
                "date": None,
                "days_to_event": None,
                "training_bias": None,
                "taper_state": "none",
                "race_type": None,
                "race_profile": None
            },
            "upcoming": []
        }

        calendar_data = context.get("calendar") or []
        today = pd.Timestamp.now().date()

        candidates = []

        for e in calendar_data:

            if not isinstance(e, dict):
                continue

            category = str(e.get("category") or "").upper()
            if category not in ("RACE_A", "RACE_B", "RACE_C"):
                continue

            date_raw = e.get("start_date_local") or e.get("date")
            if not date_raw:
                continue

            try:
                dt = pd.to_datetime(str(date_raw)[:10]).date()
            except:
                continue

            if dt < today:
                continue

            name_raw = e.get("name") or "Untitled"
            name = name_raw.lower()

            # -----------------------------
            # training bias (existing)
            # -----------------------------
            if "climb" in name:
                training_bias = "durability"
            elif "tt" in name or "threshold" in name:
                training_bias = "ftp"
            elif "vo2" in name:
                training_bias = "anaerobic"
            elif "sprint" in name:
                training_bias = "neuromuscular"
            else:
                training_bias = "mixed"

            # -----------------------------
            # race classification (NEW)
            # -----------------------------
            race_type = classify_race_type(e, name)
            race_profile = RACE_PROFILES.get(race_type, {})

            priority = category.split("_")[-1]
            days_to_event = (dt - today).days

            # -----------------------------
            # taper logic (existing)
            # -----------------------------
            taper_state = "none"

            if days_to_event is not None:
                if priority == "A":
                    if days_to_event <= 10:
                        taper_state = "taper"
                    elif days_to_event <= 21:
                        taper_state = "pre_taper"
                elif priority == "B":
                    if days_to_event <= 5:
                        taper_state = "taper"
                    elif days_to_event <= 10:
                        taper_state = "pre_taper"


            estimated = estimate_event_ctl_atl_from_calendar_ewma(
                context=context,
                event_date=dt
            )

            event_ctl = estimated["ctl"]
            event_atl = estimated["atl"]

            candidates.append({
                "id": e.get("id"),
                "shared_event_id": e.get("shared_event_id"),
                "name": name_raw,
                "category": e.get("category"),
                "priority": priority,
                "icu_atl": event_atl,
                "icu_ctl": event_ctl,
                "type": e.get("type"),
                "load": e.get("icu_training_load"),
                "intensity": e.get("icu_intensity"),
                "distance": e.get("distance"),
                "moving_time": e.get("moving_time"),
                "date": dt.isoformat(),
                "days_to_event": days_to_event,
                "training_bias": training_bias,
                "taper_state": taper_state,

                # ✅ NEW
                "race_type": race_type,
                "race_profile": race_profile
            })

        candidates = sorted(candidates, key=lambda x: x["date"])

        if candidates:
            next_event = candidates[0]

            event_targets["exists"] = True

            for k in event_targets["next_event"].keys():
                event_targets["next_event"][k] = next_event.get(k)

        event_targets["upcoming"] = [
            {
                k: c.get(k)
                for k in [
                    "id","shared_event_id","name","category","priority","icu_atl","icu_ctl",
                    "type","load","intensity","distance","moving_time",
                    "date","days_to_event","training_bias",
                    "race_type","race_profile"
                ]
            }
            for c in candidates[1:10]
        ]

        context["event_targets"] = event_targets
        semantic["event_targets"] = event_targets

        # ---------------------------------------------------------
        # Determine current ISO week (microcycle already covered)
        # ---------------------------------------------------------

        period = semantic.get("meta", {}).get("period", "")

        if "→" in period:
            _, end_str = [x.strip() for x in period.split("→")]
            report_end = pd.to_datetime(end_str).date()
        else:
            report_end = pd.to_datetime(context.get("end")).date()


        # ---------------------------------------------------------
        # Determine report week vs real current week
        # ---------------------------------------------------------

        report_iso = pd.Timestamp(report_end).isocalendar()
        report_week_key = f"{report_iso.year}-W{report_iso.week:02d}"

        now = pd.Timestamp.now(tz=context.get("timezone") or "UTC")
        current_iso = now.isocalendar()
        current_week_key = f"{current_iso.year}-W{current_iso.week:02d}"


        # ---------------------------------------------------------
        # 📊 PLANNED SUMMARY — ISO WEEK (Future Weeks Only)
        # ---------------------------------------------------------

        today = context["athlete_today"]
        planned_summary_by_iso_week = {}
        if pd.Timestamp(report_end) < (today - pd.Timedelta(days=6)):
            semantic["planned_summary_by_iso_week"] = {}
        else:

            planned_by_week = {}

            for day, events in planned_by_date.items():

                try:
                    d = pd.to_datetime(day)
                    iso_year, iso_week, _ = d.isocalendar()
                    week_key = f"{iso_year}-W{iso_week:02d}"
                except Exception:
                    continue

                # Skip the current microcycle week
                #if week_key == current_week_key:
                #    continue

                planned_by_week.setdefault(week_key, []).extend(events)

            # ---------------------------------------------------------
            # 🧱 DROP LAST ISO WEEK IF WINDOW TRUNCATED
            # ---------------------------------------------------------

            if planned_by_week:

                last_week = sorted(planned_by_week.keys())[-1]

                max_date = max(pd.to_datetime(d).date() for d in planned_by_date.keys())

                iso_year, iso_week, _ = max_date.isocalendar()
                last_week_from_data = f"{iso_year}-W{iso_week:02d}"

                week_end = max_date + timedelta(days=(7 - max_date.isoweekday()))

                #if max_date < week_end:
                #    planned_by_week.pop(last_week_from_data, None)

                planned_summary_by_iso_week = {}

                for week, events in planned_by_week.items():

                    total_load = sum((e.get("icu_training_load") or 0) for e in events)

                    is_current = (week == current_week_key)

                    planned_summary_by_iso_week[week] = {
                        "total_events": len(events),
                        "total_duration_minutes": sum((e.get("duration_minutes") or 0) for e in events),

                        # 🔥 KEY FIX
                        "remaining_load" if is_current else "planned_load": total_load,

                        "categories": sorted({e.get("category") for e in events if e.get("category")}),
                        "is_current_week": is_current
                    }

            semantic["planned_summary_by_iso_week"] = dict(
                sorted(planned_summary_by_iso_week.items())
            )

        semantic["planned_events"] = planned_events
        semantic["planned_summary_by_date"] = planned_summary_by_date

        # ---------------------------------------------------------
        # 🎯 DERIVED VIEW: next 7 days (ONLY for current week)
        # ---------------------------------------------------------
        today = context.get("athlete_today")
        is_recent = pd.Timestamp(report_end) >= (today - pd.Timedelta(days=6))

        if is_recent:

            semantic["planned_events_7d"] = []

            try:
                today = context.get("athlete_today")

                if today:
                    today_dt = pd.to_datetime(today)
                    cutoff_dt = today_dt + pd.Timedelta(days=7)

                    semantic["planned_events_7d"] = [
                        e for e in semantic.get("planned_events", [])
                        if e.get("date")
                        and today_dt <= pd.to_datetime(e["date"]) < cutoff_dt
                    ]

                    semantic["planned_events_7d"] = sorted(
                        semantic["planned_events_7d"],
                        key=lambda x: x.get("date")
                    )

            except Exception as e:
                debug(context, f"[PLANNED_EVENTS_7D] ⚠️ failed: {e}")

        else:
            #do NOT create the field at all
            semantic.pop("planned_events_7d", None)
        
        # ---------------------------------------------------------
        # 🔮 Tier-3 FUTURE FORECAST (only if report window is recent)
        # ---------------------------------------------------------
        
        semantic["future_forecast"] = {}
        semantic["future_actions"] = []

        try:
            period = semantic.get("meta", {}).get("period", "")
            if "→" in period:
                end_str = period.split("→")[1].strip()
                report_end = pd.Timestamp(pd.to_datetime(end_str))
                today = context["athlete_today"]

                if report_end >= (today - pd.Timedelta(days=6)):

                    context["calendar"] = calendar_data

                    forecast_output = run_future_forecast(context)

                    if isinstance(forecast_output, dict):
                        semantic["future_forecast"] = forecast_output.get("future_forecast", {})
                        semantic["future_actions"] = forecast_output.get("actions_future", [])
                else:
                    # 🔥 CRITICAL: clear stale Tier-3 state
                    context.pop("future_forecast", None)
                    context.pop("actions_future", None)

        except Exception as e:
            debug(context, f"[FORECAST] ⚠️ {e}")

        # ✅ Meta info for structured UI rendering
        semantic["meta"]["planned_events"] = {
            "is_planned_events_block": True,
            "planned_events_block_count": len(semantic["planned_events"]),
            "notes": "Canonical planned events block (URF v5.2) — intended for ChatGPT / structured UI rendering."
        }

    else:
        semantic["planned_events"] = []
        semantic["planned_summary_by_date"] = {}
        semantic["planned_summary_by_iso_week"] = {}
        semantic["future_forecast"] = {}
        semantic["meta"]["planned_events"] = {
            "is_planned_events_block": False,
            "planned_events_block_count": 0,
            "notes": "No planned events found or calendar source unavailable."
        }
        semantic["training_guidance"] = []
        debug(context, "[SEMANTIC] ⚠️ No valid planned events found")

    # ---------------------------------------------------------
    # DERIVED METRICS
    # ---------------------------------------------------------
    for metric_name, info in context.get("derived_metrics", {}).items():

        merged_context = {
            **context,
            "derived_info": info
        }

        block = semantic_block_for_metric(
            metric_name,
            info.get("value"),
            merged_context
        )

        # 🔴 CRITICAL: re-inject derived intelligence (ONLY if present)
        if info.get("interpretation"):
            block["interpretation"] = info["interpretation"]

        if info.get("coaching_implication"):
            block["coaching_implication"] = info["coaching_implication"]

        semantic["metrics"][metric_name] = block
        
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
    # NON-BREAKING METRIC GROUPING (FINAL STEP)
    # ---------------------------------------------------------

    semantic["metrics_groups"] = {
        "load": {
            "ACWR": semantic["metrics"].get("ACWR"),
            "Strain": semantic["metrics"].get("Strain"),
            "FatigueTrend": semantic["metrics"].get("FatigueTrend"),
        },
        "intensity": {
            "ZQI": semantic["metrics"].get("ZQI"),
            "Polarisation": semantic["metrics"].get("Polarisation"),
            "PolarisationIndex": semantic["metrics"].get("PolarisationIndex"),
            "Polarisation_variants": semantic["metrics"].get("Polarisation_variants"),
        },
        "variability": {
            "Monotony": semantic["metrics"].get("Monotony"),
        },
        "metabolic": {
            "FOxI": semantic["metrics"].get("FOxI"),
            "CUR": semantic["metrics"].get("CUR"),
            "GR": semantic["metrics"].get("GR"),
            "MES": semantic["metrics"].get("MES"),
            "FatOxEfficiency": semantic["metrics"].get("FatOxEfficiency"),
        },
        "capacity": {
            "StressTolerance": semantic["metrics"].get("StressTolerance"),
        }
    }

    # ---------------------------------------------------------
    # 🧮 CTL / ATL / TSB RESOLUTION (AUTHORITATIVE + FALLBACK)
    # ---------------------------------------------------------
    semantic.setdefault("wellness", {})
    semantic.setdefault("training_volume", {})

    ws = context.get("wellness_summary", {}) or {}

    def _round_or_none(v, ndigits=2):
        try:
            return round(float(v), ndigits) if v is not None else None
        except Exception:
            return None

    semantic["training_volume"]["CTL"] = _round_or_none(ws.get("ctl"), 2)
    semantic["training_volume"]["ATL"] = _round_or_none(ws.get("atl"), 2)
    semantic["training_volume"]["TSB"] = _round_or_none(ws.get("tsb"), 2)
    semantic["training_volume"]["load_state"] = context.get("load_state", {})

    semantic["training_volume"]["load_pattern"] = resolve_training_load_pattern(
        semantic.get("metrics_groups", {}),
        CHEAT_SHEET
    )

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
    # 🧠 Performance Intelligence (Tier-3)
    # ---------------------------------------------------------

    pi = context.get("performance_intelligence", {}) or {}

    semantic["performance_intelligence"]["version"] = context.get("PI_VERSION")

    acute_pi = {}
    chronic_pi = {}

    # Weekly + chronic fallback
    if "chronic_context" in pi:

        acute_pi = copy.deepcopy({
            k: v for k, v in pi.items()
            if k not in (
                "chronic_context",
                "acute_context_window",
                "chronic_context_window",
            )
        })

        chronic_pi = copy.deepcopy(pi.get("chronic_context", {}))

    # Weekly structure
    elif "anaerobic_repeatability" in pi:
        acute_pi = copy.deepcopy(pi)

    # Season structure
    elif "chronic_state" in pi or "acute_overlay" in pi:
        chronic_pi = copy.deepcopy(pi.get("chronic_state", {}))
        acute_pi   = copy.deepcopy(pi.get("acute_overlay", {}))

    if isinstance(pi, dict) and pi:

        report_type = semantic["meta"]["report_type"]

        # -----------------------------------------------------
        # 1️⃣ Inject Raw Model Metrics (WDRM / ISDM / NDLI)
        # -----------------------------------------------------

        PI_GROUPS = {
            "anaerobic_repeatability": {
                "framework": "W′ Depletion & Repeatability Model (WDRM)",
                "cheatsheet_key": "anaerobic_repeatability",
                "context_key": "AnaerobicRepeatability",
                "advice_key": "AnaerobicRepeatability",
            },
            "model_diagnostics": {
                "framework": "Skiba Critical Power",
                "cheatsheet_key": "model_diagnostics",
                "context_key": "ModelDiagnostics",
                "advice_key": "ModelDiagnostics",
            },
            "durability": {
                "framework": "Intensity Stability & Durability Model (ISDM)",
                "cheatsheet_key": "durability",
                "context_key": "DurabilityProfile",
                "advice_key": "DurabilityProfile",
            },
            "neural_density": {
                "framework": "Neural Density Load Index (NDLI)",
                "cheatsheet_key": "neural_density",
                "context_key": "NeuralDensity",
                "advice_key": "NeuralDensity",
            },
        }

        def wrap_pi_block(pi_block, window_label):
            wrapped = {}

            for group_name, metrics in (pi_block or {}).items():

                if group_name not in PI_GROUPS:
                    continue

                if metrics is None:
                    continue

                group_meta = PI_GROUPS[group_name]
                wrapped[group_name] = {}

                # -----------------------------
                # GROUP HEADER FIRST (ORDER FIX)
                # -----------------------------
                if group_name in ("anaerobic_repeatability", "neural_density"):

                    wrapped[group_name]["interpretation"] = (
                        CHEAT_SHEET["context"].get(group_meta["context_key"])
                    )

                    wrapped[group_name]["coaching_implication"] = (
                        CHEAT_SHEET["advice"].get(group_meta["advice_key"])
                        or CHEAT_SHEET["coaching_links"].get(group_meta["advice_key"])
                    )

                # -----------------------------
                # FIRST PASS: build metrics
                # -----------------------------
                for metric_name, metric_value in metrics.items():

                    # pass-through for pre-structured blocks (like durability.state)
                    if isinstance(metric_value, dict) and "value" in metric_value:
                        wrapped[group_name][metric_name] = metric_value
                        continue

                    if metric_name in ("state", "durability_state_7d", "durability_state_90d"):
                        wrapped[group_name][metric_name] = metric_value
                        continue

                    block = semantic_block_for_metric(metric_name, metric_value, semantic)

                    # 🚨 HARD REMOVE for durability
                    if group_name == "durability":
                        block.pop("coaching_implication", None)

                    block["framework"] = group_meta["framework"]

                    metric_context = CHEAT_SHEET["context"].get(metric_name)
                    group_context = CHEAT_SHEET["context"].get(group_meta["context_key"])

                    metric_advice = (
                        CHEAT_SHEET["advice"].get(metric_name)
                        or CHEAT_SHEET["coaching_links"].get(metric_name)
                    )

                    group_advice = (
                        CHEAT_SHEET["advice"].get(group_meta["advice_key"])
                        or CHEAT_SHEET["coaching_links"].get(group_meta["advice_key"], {})
                    )

                    block["interpretation"] = metric_context or group_context

                    # 🚨 REMOVE durability coaching here
                    if group_name != "durability":
                        block["coaching_implication"] = metric_advice or group_advice

                    block["context_window"] = window_label

                    wrapped[group_name][metric_name] = block

                    if group_name in ("anaerobic_repeatability", "neural_density"):
                        block.pop("interpretation", None)
                        block.pop("coaching_implication", None)

                # -----------------------------
                # SECOND PASS: durability ONLY
                # -----------------------------
                if group_name == "durability":

                    state = wrapped[group_name].get("state")

                    if state:
                        wrapped[group_name]["state"] = {
                            "value": state,
                            "coaching_implication": CHEAT_SHEET["advice"]["DurabilityProfile"].get(state)
                        }
            return wrapped


        # -----------------------------------------------------
        # Window labelling
        # -----------------------------------------------------
        # Acute always means 7d FULL.
        # Chronic is 90d LIGHT, only populated when acute has no useful signal.
        semantic["performance_intelligence"]["acute"] = wrap_pi_block(acute_pi, "7d")
        semantic["performance_intelligence"]["chronic"] = wrap_pi_block(chronic_pi, "90d")
       
        # -----------------------------------------------------
        # Load Distribution (from T1)
        # -----------------------------------------------------

        load_dist = context.get("load_distribution") or {}

        if load_dist:

            semantic.setdefault("performance_intelligence", {})

            semantic["performance_intelligence"]["load_distribution"] = {
                "rest_days": load_dist.get("rest_days"),
                "context_window": {
                    "weekly": "7d",
                    "wellness": "42d",
                    "season": "90d",
                    "summary": "full"
                }.get(context.get("report_type"), "unknown")
            }

            debug(
                context,
                f"[SEMANTIC] Injected load_distribution → rest_days={load_dist.get('rest_days')}"
            )
        # -----------------------------------------------------
        # External Load Context (SCIENCE-ALIGNED)
        # -----------------------------------------------------

        external = pi.get("external_load_context")

        if external:

            semantic["performance_intelligence"]["external_load_context"] = {

                # -------------------------------------------------
                # TRUE external load (thermal only)
                # -------------------------------------------------
                "env_load_index_7d": external.get("env_load_index_7d"),
                "heat_load_index_7d": external.get("heat_load_index_7d"),

                # -------------------------------------------------
                # THERMAL SOURCE (CRITICAL)
                # -------------------------------------------------
                "thermal_source": external.get("thermal_source"),
                "thermal_source_confidence": external.get("thermal_source_confidence"),

                # -------------------------------------------------
                # CONTEXT (NOT load)
                # -------------------------------------------------
                "terrain_context_7d": external.get("terrain_context_7d"),
                "vam_mean_7d": external.get("vam_mean_7d"),

                # -------------------------------------------------
                # EXPOSURE (max session stress — NOT averaged)
                # -------------------------------------------------
                "exposure": external.get("exposure"),

                # -------------------------------------------------
                # INTERPRETATION
                # -------------------------------------------------
                "dominant_stressor": external.get("dominant_stressor"),
                "classification": external.get("classification"),

                # -------------------------------------------------
                # PHYSIOLOGICAL MODIFIERS
                # -------------------------------------------------
                "modifiers": external.get("modifiers"),

                # -------------------------------------------------
                # META
                # -------------------------------------------------
                "confidence": external.get("thermal_source_confidence") or external.get("confidence"),
                "context_window": external.get("context_window"),
            }

            debug(
                context,
                f"[SEMANTIC] Injected external_load_context → "
                f"{external.get('classification')} ({external.get('dominant_stressor')})"
            )

        # -----------------------------------------------------
        # 2️⃣ Inject Interpretation → Action Layer
        # -----------------------------------------------------

        training_state = context.get("training_state")

        if training_state:

            load_state = training_state.get("load_recovery_state")
            classification = CLASSIFICATION_ALIASES.get(load_state)

            semantic["performance_intelligence"]["training_state"] = {
                "framework": "Autonomic–Load Interaction Model",

                # -------------------------------------------------
                # Scientific interpretation
                # -------------------------------------------------

                "interpretation": CHEAT_SHEET["context"].get("load_recovery_state"),

                "coaching_implication": CHEAT_SHEET["advice"]
                    .get("LoadRecoveryState", {})
                    .get(load_state),

                "context_window": "current_microcycle",

                # -------------------------------------------------
                # Classification layer
                # -------------------------------------------------

                "classification": classification,
                "classification_source": "load_recovery_state",

                # -------------------------------------------------
                # Coaching state
                # -------------------------------------------------

                "state_label": training_state.get("state_label"),
                "operational_state": training_state.get("operational_state"),
                "confidence": training_state.get("confidence"),

                # -------------------------------------------------
                # Signals used
                # -------------------------------------------------

                "signals": {
                    "readiness_signal": training_state.get("readiness"),
                    "adaptation_signal": training_state.get("adaptation"),
                    "load_recovery_state": load_state,

                    # physiological signals used for decision
                    "hrv_ratio": (training_state.get("signals") or {}).get("hrv_ratio"),
                    "atl": (training_state.get("signals") or {}).get("atl"),
                    "ctl": (training_state.get("signals") or {}).get("ctl"),
                },

                # -------------------------------------------------
                # Operational context (NEW)
                # -------------------------------------------------

                "operational_context": (
                    training_state.get("operational_state_context")
                    or context.get("operational_state_context")
                ),

                # -------------------------------------------------
                # Recommended action
                # -------------------------------------------------

                "recommended_action": {
                    "recommendation": training_state.get("recommendation"),
                    "next_session": training_state.get("next_session")
                },

                "phase_context": training_state.get("phase_context")
            }

            debug(
                context,
                f"[SEMANTIC] Injected training_state → "
                f"{training_state.get('state_label')} | "
                f"{training_state.get('next_session')}"
            )
            
            # -----------------------------------------------------
            # 3️⃣ Inject Nutrition (carbohydrate classification)
            # -----------------------------------------------------

            nutrition = context.get("nutrition_balance")
            nutrition_demand = context.get("nutrition_demand")
            weight = (context.get("athlete") or {}).get("icu_weight")

            if nutrition and nutrition_demand:

                classification = nutrition.get("status")
                protein_status = nutrition.get("protein_status")

                # -------------------------------------------------
                # FIXED MARKER — carbohydrate availability
                # -------------------------------------------------

                marker = (
                    COACH_PROFILE
                    .get("markers", {})
                    .get("CarbohydrateAvailability", {})
                )

                interpretation = marker.get("interpretation")
                coaching = marker.get("coaching_implication")
                formula = marker.get("formula")
                framework = marker.get("framework")

                def _to_grams(value_gkg):
                    if value_gkg is None or weight is None or weight <= 0:
                        return None
                    return round(value_gkg * weight, 0)

                semantic["performance_intelligence"]["nutrition"] = {

                    # -------------------------------------------------
                    # Carbohydrate marker
                    # -------------------------------------------------

                    "framework": framework,
                    "interpretation": interpretation,
                    "coaching_implication": coaching,
                    "formula": formula,

                    "context_window": "rolling_3d_completed_days",
                    "signals_basis": "average_daily_intake",

                    # -------------------------------------------------
                    # Classification
                    # -------------------------------------------------

                    "classification": classification,
                    "classification_scope": "carbohydrate_availability",
                    "classification_source": "nutrition_balance",

                    # Protein is reported separately and does not
                    # control the carbohydrate classification.
                    "protein_status": protein_status,

                    # -------------------------------------------------
                    # Confidence
                    # -------------------------------------------------

                    "confidence": nutrition.get("confidence"),

                    # -------------------------------------------------
                    # Signals
                    # -------------------------------------------------

                    "signals": {
                        "carbs_actual_g": _to_grams(
                            nutrition.get("carbs_gkg_actual")
                        ),
                        "protein_actual_g": _to_grams(
                            nutrition.get("protein_gkg_actual")
                        ),
                        "fat_actual_g": _to_grams(
                            nutrition.get("fat_gkg_actual")
                        ),

                        "carbs_required_g": _to_grams(
                            nutrition_demand.get("carbs_gkg_required")
                        ),
                        "protein_required_g": _to_grams(
                            nutrition_demand.get("protein_gkg_required")
                        ),
                        "fat_required_g": _to_grams(
                            nutrition_demand.get("fat_gkg_target")
                        ),

                        "carbs_delta_g": _to_grams(
                            nutrition.get("carbs_delta")
                        ),
                        "protein_delta_g": _to_grams(
                            nutrition.get("protein_delta")
                        ),
                        "fat_delta_g": _to_grams(
                            nutrition.get("fat_delta")
                        ),
                    }
                }

                debug(
                    context,
                    "[SEMANTIC] Injected nutrition →",
                    f"carbs={classification}",
                    f"protein={protein_status}",
                    f"confidence={nutrition.get('confidence')}"
                )
 
    # ---------------------------------------------------------
    # 🧭 Tier-3 State → Primary Action
    # ---------------------------------------------------------
    training_state = context.get("training_state")
    if training_state:

        primary_action = training_state.get("recommendation")
        readiness = training_state.get("readiness")

        if primary_action:

            semantic.setdefault("actions", [])

            semantic["actions"].insert(0, {
                "type": "state_action",
                "priority": "supporting",
                "label": "Training State",
                "source": "tier3_training_state",
                "model": "Seiler Load Governance",
                "recommendation": primary_action,
                "readiness_signal": readiness,
                "state_label": training_state.get("state_label"),
                "operational_state": training_state.get("operational_state"),
                "operational_context": (
                    training_state.get("operational_state_context")
                    or context.get("operational_state_context")
                    or semantic.get("performance_intelligence", {})
                        .get("training_state", {})
                        .get("operational_context")
                )
            })

    # ---------------------------------------------------------
    # 🧠 Energy System Progression (Tier-3 ESPE)
    # ---------------------------------------------------------

    espe = context.get("energy_system_progression")

    if isinstance(espe, dict) and espe:

        semantic["energy_system_progression"] = espe

        debug(
            context,
            "[SEMANTIC] Injected energy_system_progression → "
            f"sports={list(espe.get('sports', {}).keys())}"
        )

    else:

        debug(context, "[SEMANTIC] energy_system_progression not present")

    # ---------------------------------------------------------
    # ⚡ ESPE → Coaching Action(s)
    # ---------------------------------------------------------

    espe = context.get("energy_system_progression") or {}
    sports = espe.get("sports") or {}

    for sport, block in sports.items():

        if not isinstance(block, dict):
            continue

        if not block.get("supported"):
            continue

        system_guidance = block.get("system_guidance")
        system_state = block.get("adaptation_state")

        if not system_guidance:
            continue

        semantic.setdefault("actions", [])

        semantic["actions"].append({
            "type": "system_guidance",
            "priority": "supporting",
            "label": "Energy System Direction",
            "sport": sport,
            "source": "energy_system_progression",
            "model": "Energy System Progression Engine",
            "system_state": system_state,
            "message": system_guidance
        })

    # ---------------------------------------------------------
    # 🧭 Closing Reflection (Tier-2 guidance)
    # ---------------------------------------------------------

    signals = detect_signals(semantic)
    question = generate_question(semantic, signals)

    if question:
        semantic.setdefault("actions", [])
        semantic["actions"].append({
            "type": "reflection",
            "priority": "supporting",
            "source": "montis_question_engine",
            "signal": dominant_signal(signals),
            "question": question
        })

    # ---------------------------------------------------------
    # 🔬 Adaptation Metrics (derived from performance signals)
    # ---------------------------------------------------------
    adaptation = {}

    pi = semantic.get("performance_intelligence", {}) or {}
    report_type = semantic.get("meta", {}).get("report_type")

    acute = pi.get("acute", {}) or {}
    chronic = pi.get("chronic", {}) or {}

    def extract_metric_value(metric):
        if isinstance(metric, dict):
            return metric.get("value")
        return metric

    def add_adaptation_metric(key, value, window, basis, ndigits=2):
        if value is None:
            return

        try:
            adaptation[key] = {
                "value": round(float(value), ndigits),
                "window": window,
                "basis": basis
            }
        except Exception:
            pass


    # ---------------------------------------------------------
    # Weekly reports should use acute 7d signals.
    # Season / summary should use chronic 90d signals.
    # ---------------------------------------------------------

    if report_type == "weekly":

        # ---- Efficiency Factor: 7d ----
        ef_metric = (
            acute
            .get("neural_density", {})
            .get("mean_efficiency_factor_7d")
        )

        add_adaptation_metric(
            "Efficiency Factor",
            extract_metric_value(ef_metric),
            "7d",
            "acute.neural_density.mean_efficiency_factor_7d",
            ndigits=2
        )

        # ---- Endurance Decay: 7d ----
        dec_metric = (
            acute
            .get("durability", {})
            .get("mean_decoupling_7d")
        )

        add_adaptation_metric(
            "Endurance Decay",
            extract_metric_value(dec_metric),
            "7d",
            "acute.durability.mean_decoupling_7d",
            ndigits=1
        )

    else:

        # ---- Efficiency Factor: 90d ----
        ef_metric = (
            chronic
            .get("neural_density", {})
            .get("mean_efficiency_factor_90d")
        )

        add_adaptation_metric(
            "Efficiency Factor",
            extract_metric_value(ef_metric),
            "90d",
            "chronic.neural_density.mean_efficiency_factor_90d",
            ndigits=2
        )

        # ---- Endurance Decay: 90d ----
        dec_metric = (
            chronic
            .get("durability", {})
            .get("mean_decoupling_90d")
        )

        add_adaptation_metric(
            "Endurance Decay",
            extract_metric_value(dec_metric),
            "90d",
            "chronic.durability.mean_decoupling_90d",
            ndigits=1
        )

    semantic["adaptation_metrics"] = adaptation

    # ---------------------------------------------------------
    # 🧬 WELLNESS CONSOLIDATION (URF v5.2 canonical structure)
    # ---------------------------------------------------------
    if semantic["meta"].get("report_type") in ("weekly", "season", "wellness"):

        wellness = semantic.setdefault("wellness", {})

        # --- 42-day window anchor ---
        wellness["window_days"] = 42

        # -----------------------------------------------------
        # 2️⃣ HRV Structure
        # -----------------------------------------------------
        if wellness.get("hrv_available"):
            wellness["hrv"] = {
                "mean": wellness.get("hrv_mean"),
                "latest": wellness.get("hrv_latest"),
                "trend_7d": wellness.get("hrv_trend_7d"),
                "samples": wellness.get("hrv_samples"),
                "source": wellness.get("hrv_source"),
            }


        # -----------------------------------------------------
        # 3️⃣ Sleep + Cardiac
        # -----------------------------------------------------
        if "sleep_score" in wellness:
            wellness["sleep"] = {
                "average_score": wellness.get("sleep_score"),
            }

        if "resting_hr_delta" in wellness:
            wellness["cardiac"] = {
                "resting_hr_delta": wellness.get("resting_hr_delta"),
            }

        # -----------------------------------------------------
        # 4️⃣ Recovery Markers (from canonical metrics layer)
        # -----------------------------------------------------
        recovery_metric_keys = [
            "StressTolerance",
            "Monotony",
            "Strain",
        ]

        recovery_block = {}

        for key in recovery_metric_keys:
            if key in semantic.get("metrics", {}):
                m = semantic["metrics"][key]
                recovery_block[key] = {
                    "value": m.get("value"),
                    "state": m.get("state"),
                    "framework": m.get("framework"),
                }

        if recovery_block:
            wellness["recovery_markers"] = recovery_block


        # -----------------------------------------------------
        # 5️⃣ Clean up flat fields (optional but cleaner)
        # -----------------------------------------------------
        for k in [
            "hrv_mean",
            "hrv_latest",
            "hrv_trend_7d",
            "hrv_samples",
            "hrv_source",
            #"sleep_score",
            #"resting_hr_delta",
        ]:
            wellness.pop(k, None)


    # ---------------------------------------------------------
    #  Echo render options for transparency
    # ---------------------------------------------------------
    if "render_options" in context:
        semantic["options"] = context["render_options"]

    # ---------------------------------------------------------
    # 🗓️ Microcycle Execution Model (ISO Aligned)
    # ---------------------------------------------------------
    if semantic["meta"].get("report_type") in ("weekly", "season", "summary"):

        semantic["current_ISO_weekly_microcycle"] = None

        tz = context.get("timezone") or "UTC"
        today = context["athlete_today"]

        period_meta = semantic.get("meta", {}).get("period")

        if isinstance(period_meta, str) and "→" in period_meta:
            report_end = pd.to_datetime(period_meta.split("→")[1].strip(), errors="coerce").date()
        else:
            report_end = pd.to_datetime(context.get("period", {}).get("end"), errors="coerce").date()

        if pd.notna(report_end):

            today_iso  = today.isocalendar()
            report_iso = report_end.isocalendar()

            # Allow microcycle if report is recent (within 6 days)
            if pd.Timestamp(report_end) >= (today - pd.Timedelta(days=6)):

                iso = today_iso

                monday = pd.Timestamp.fromisocalendar(int(iso.year), int(iso.week), 1)
                sunday = monday + pd.Timedelta(days=6)

                current_ISO_weekly_microcycle = {
                    "week_iso": f"{iso.year}-W{iso.week}",
                    "weekly_target_tss": 0.0,
                    "completed_tss": 0.0,
                    "planned_remaining_tss": 0.0,
                    "projected_total_tss": 0.0,
                    "delta_to_target": 0.0,
                    "basis": "The microcycle is based on the current ISO week (Monday to Sunday) and includes planned and completed with compliance,"
                }

                try:
                    # -------------------------------------------------
                    # 1️⃣ ISO week (TRUE current week — time anchored)
                    # -------------------------------------------------

                    week_label = f"{iso.year}-W{iso.week}"
                    current_ISO_weekly_microcycle["week_iso"] = week_label

                    monday = pd.Timestamp.fromisocalendar(int(iso.year), int(iso.week), 1)
                    sunday = monday + pd.Timedelta(days=6)

                    # -------------------------------------------------
                    # 2️⃣ Completed TSS (ISO week)
                    # -------------------------------------------------
                    df_actual = context.get("_df_scope_full")
                    week_df = pd.DataFrame()

                    if isinstance(df_actual, pd.DataFrame) and not df_actual.empty:
                        df_actual = df_actual.copy()
                        df_actual["date_only"] = pd.to_datetime(
                            df_actual["start_date_local"], errors="coerce"
                        ).dt.date

                        week_df = df_actual[
                            (df_actual["date_only"] >= monday.date()) &
                            (df_actual["date_only"] <= sunday.date())
                        ]

                        completed = float(
                            pd.to_numeric(
                                week_df.get("icu_training_load", 0),
                                errors="coerce"
                            ).fillna(0).sum()
                        )

                        current_ISO_weekly_microcycle["completed_tss"] = round(completed, 1)


                    # -------------------------------------------------
                    # 3️⃣ Weekly Target (Plan Reconstruction)
                    # -------------------------------------------------
                    #
                    # Because Cloudflare only forwards future calendar events,
                    # executed planned sessions from earlier in the ISO week are
                    # no longer present in the calendar feed.
                    #
                    # Therefore we reconstruct the original planned load using:
                    #
                    # planned_load = actual_load / (compliance / 100)
                    #
                    # Data sources
                    # ------------
                    # remaining plan → context["calendar"]
                    # executed plan  → week_df + paired_event_id + compliance
                    #
                    # -------------------------------------------------

                    weekly_target = 0.0
                    planned_remaining = 0.0
                    missed_planned = 0.0

                    calendar_events = context.get("calendar", []) or []

                    debug(context, f"[MICROCYCLE-CALENDAR] events={len(calendar_events)}")

                    for ce in calendar_events:
                        debug(
                            context,
                            f"[MICROCYCLE-CALENDAR] id={ce.get('id')} "
                            f"date={ce.get('start_date_local')} "
                            f"load={ce.get('icu_training_load',0)} "
                            f"name={ce.get('name')}"
                        )
                    # -------------------------------------------------
                    # identify planned sessions already executed
                    # -------------------------------------------------

                    consumed_plan_ids = set()

                    if not week_df.empty:
                        for _, row in week_df.iterrows():

                            paired_id = row.get("paired_event_id")

                            if pd.notna(paired_id):
                                consumed_plan_ids.add(int(float(paired_id)))
                    # -------------------------------------------------
                    # remaining calendar sessions / future only from today
                    # -------------------------------------------------
                    planned_remaining = 0.0

                    for ce in calendar_events:

                        ce_date = pd.to_datetime(ce.get("start_date_local"), errors="coerce")
                        if pd.isna(ce_date):
                            continue

                        ce_date = ce_date.date()

                        # ✅ LIMIT TO THIS ISO WEEK
                        if ce_date < monday.date() or ce_date > sunday.date():
                            continue

                        # ✅ FUTURE ONLY
                        if ce_date < today.date():
                            continue

                        # ✅ STRICT pairing rule
                        ce_id = ce.get("id")
                        if ce_id in consumed_plan_ids:
                            continue

                        load = float(ce.get("icu_training_load", 0) or 0)
                        planned_remaining += load

                    # -------------------------------------------------
                    # ❗ MISSED planned sessions (past but not executed)
                    # -------------------------------------------------

                    for ce in calendar_events:

                        ce_date = pd.to_datetime(ce.get("start_date_local"), errors="coerce")
                        if pd.isna(ce_date):
                            continue

                        ce_date = ce_date.date()

                        # same ISO week only
                        if ce_date < monday.date() or ce_date > sunday.date():
                            continue

                        ce_id = ce.get("id")

                        # skip executed planned sessions
                        if ce_id in consumed_plan_ids:
                            continue

                        # 🔴 ONLY past days (missed)
                        if ce_date < today.date():

                            load = float(ce.get("icu_training_load", 0) or 0)
                            missed_planned += load

                    # -------------------------------------------------
                    # executed planned sessions (reconstruct original plan)
                    # -------------------------------------------------

                    if not week_df.empty:

                        for _, row in week_df.iterrows():

                            paired_id = row.get("paired_event_id")

                            # skip unplanned activities
                            if pd.isna(paired_id):
                                continue

                            # -------------------------------------------------
                            # safe actual load
                            # -------------------------------------------------
                            actual = pd.to_numeric(
                                row.get("icu_training_load"),
                                errors="coerce"
                            )

                            if pd.isna(actual):
                                actual = 0.0
                            else:
                                actual = float(actual)

                            # -------------------------------------------------
                            # safe compliance
                            # -------------------------------------------------
                            compliance = row.get("compliance")

                            compliance_val = pd.to_numeric(
                                compliance,
                                errors="coerce"
                            )

                            if pd.notna(compliance_val) and compliance_val > 0:

                                planned_equivalent = (
                                    actual / (float(compliance_val) / 100.0)
                                )

                            else:
                                planned_equivalent = actual

                            # -------------------------------------------------
                            # final NaN guard
                            # -------------------------------------------------
                            if pd.isna(planned_equivalent):
                                planned_equivalent = 0.0

                            weekly_target += planned_equivalent
                            weekly_target = round(float(weekly_target), 1)

                    # -------------------------------------------------
                    # 4️⃣ Projection + Delta
                    # -------------------------------------------------

                    completed_val = current_ISO_weekly_microcycle.get("completed_tss", 0.0)

                    projected_total = completed_val + planned_remaining
                    full_week_target = weekly_target + planned_remaining + missed_planned
                    delta = projected_total - full_week_target

                    current_ISO_weekly_microcycle["projected_total_tss"] = round(projected_total, 1)
                    current_ISO_weekly_microcycle["delta_to_target"] = round(delta, 1)
                    current_ISO_weekly_microcycle["weekly_target_tss"] = round(full_week_target, 1)
                    current_ISO_weekly_microcycle["planned_remaining_tss"] = round(planned_remaining, 1)
                    current_ISO_weekly_microcycle["missed_tss"] = round(missed_planned, 1)

                    # -------------------------------------------------
                    # 6️⃣ Projected Hours (reconstructed from compliance)
                    # -------------------------------------------------

                    completed_seconds = 0.0
                    planned_seconds = 0.0

                    if not week_df.empty:

                        for _, row in week_df.iterrows():

                            moving_time = float(row.get("moving_time", 0) or 0)

                            completed_seconds += moving_time

                            paired_id = row.get("paired_event_id")

                            if pd.isna(paired_id):
                                continue

                            #compliance = row.get("compliance")

                            #try:
                            #    compliance_val = float(compliance)
                            #except Exception:
                            #    compliance_val = None

                            #if compliance_val and compliance_val > 0:

                            #    planned_seconds += moving_time / (compliance_val / 100.0)

                            #else:
                            #    planned_seconds += moving_time

                    # -------------------------------------------------
                    # 6b️⃣ Add remaining planned calendar sessions
                    # -------------------------------------------------

                    calendar_events = context.get("calendar", []) or []

                    for ce in calendar_events:

                        ce_date = pd.to_datetime(ce.get("start_date_local"), errors="coerce")
                        if pd.isna(ce_date):
                            continue

                        ce_date = ce_date.date()

                        if monday.date() <= ce_date <= sunday.date():

                            ce_id = ce.get("id")

                            # skip already executed planned sessions
                            if ce_id in consumed_plan_ids:
                                continue

                            # -------------------------------------------------
                            # PRIMARY: use moving_time if available
                            # -------------------------------------------------
                            mt = ce.get("moving_time")

                            if mt:
                                planned_seconds += float(mt)

                    completed_hours = round(completed_seconds / 3600.0, 2)
                    projected_hours = round((completed_seconds + planned_seconds) / 3600.0, 2)

                    current_ISO_weekly_microcycle["completed_hours"] = completed_hours
                    current_ISO_weekly_microcycle["projected_hours"] = projected_hours


                except Exception as e:
                    debug(context, f"[MICROCYCLE] ❌ {type(e).__name__}: {e}")

                semantic["current_ISO_weekly_microcycle"] = current_ISO_weekly_microcycle
                debug(context, f"[MICROCYCLE] {current_ISO_weekly_microcycle}")


    # ---------------------------------------------------------
    # 📊 Projected end-of-week state (from calendar truth)
    # ---------------------------------------------------------

    projected_state = None

    try:
        cal = context.get("calendar") or context.get("prefetched", {}).get("calendar")

        def _finite_float(v):
            try:
                f = float(v)
                if pd.isna(f) or not np.isfinite(f):
                    return None
                return f
            except Exception:
                return None

        if isinstance(cal, list) and len(cal) > 0:

            df = pd.DataFrame(cal)

            if "start_date_local" in df.columns:

                df["date"] = pd.to_datetime(df["start_date_local"], errors="coerce")
                df = df.dropna(subset=["date"]).sort_values("date")

                # Use athlete-local today, not machine-local today
                today = pd.Timestamp(context["athlete_today"]).normalize()
                week_start = today.to_period("W").start_time
                week_end = week_start + pd.Timedelta(days=6)

                df_week = df[
                    (df["date"] >= week_start) &
                    (df["date"] <= week_end)
                ].copy()

                if (
                    not df_week.empty
                    and "icu_ctl" in df_week.columns
                    and "icu_atl" in df_week.columns
                ):
                    # Keep only calendar rows with valid projected CTL/ATL.
                    # This skips swim/hike/run placeholders or notes with no load/state.
                    df_week["_ctl_valid"] = df_week["icu_ctl"].apply(_finite_float)
                    df_week["_atl_valid"] = df_week["icu_atl"].apply(_finite_float)

                    df_valid = df_week.dropna(subset=["_ctl_valid", "_atl_valid"])

                    if not df_valid.empty:
                        last = df_valid.iloc[-1]

                        ctl = _finite_float(last.get("_ctl_valid"))
                        atl = _finite_float(last.get("_atl_valid"))

                        if ctl is not None and atl is not None:
                            projected_state = {
                                "ctl": round(ctl, 2),
                                "atl": round(atl, 2),
                                "tsb": round(ctl - atl, 2),
                                "source": "calendar"
                            }

                            debug(
                                context,
                                f"[WEEK_PROJECTION] calendar projected_state "
                                f"CTL={ctl:.2f} ATL={atl:.2f} TSB={ctl - atl:.2f}"
                            )
                    else:
                        debug(
                            context,
                            "[WEEK_PROJECTION] no valid calendar CTL/ATL rows in current week"
                        )

    except Exception as e:
        debug(context, f"[WEEK_PROJECTION] ⚠️ {e}")

    # Store for debug / downstream fallback
    context["_week_projected_state"] = projected_state

    # Attach to microcycle only if it already exists.
    # This avoids KeyError and avoids creating a fake empty microcycle.
    if isinstance(semantic.get("current_ISO_weekly_microcycle"), dict):
        semantic["current_ISO_weekly_microcycle"]["projected_state"] = projected_state

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
    # 🌍 Season / Summary / Weekly → full weekly + roll-up
    # ---------------------------------------------------------
    if report_type in ("season", "summary", "weekly"):
        debug(context, f"[PHASES] raw weekly_phases rows BEFORE normalisation = {len(semantic.get('weekly_phases', []))}")
        debug(context, f"[PHASES] context phases blocks = {len(context.get('phases', []))}")
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
                        required = [date_col, "CTL", "ATL", "TSB"]
                        missing = [c for c in required if c not in df_tmp.columns]

                        if missing:
                            debug(
                                context,
                                f"[PHASES] ⚠️ Skipping {key}: missing={missing}"
                            )
                            continue

                        ctl_src = df_tmp[required].copy()
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
                # ensure chronological order
                ctl_src = ctl_src.sort_values("date")

                df_ctl = (
                    ctl_src.groupby("year_week", as_index=False)
                    .last()[["year_week", "CTL", "ATL", "TSB"]]
                )

                df_ctl.columns = ["week", "ctl", "atl", "tsb"]
                df_weeks = df_weeks.merge(df_ctl, on="week", how="left")

                # -----------------------------------------------------
                # 🧠 Stabilise TSB for phase detection (prevent spikes)
                # -----------------------------------------------------

                # smooth short-term spikes (2-week rolling)
                df_weeks["tsb_smooth"] = df_weeks["tsb"].rolling(2, min_periods=1).mean()

                # cap extreme physiological outliers
                df_weeks["tsb_capped"] = df_weeks["tsb_smooth"].clip(-50, 50)

                # -----------------------------------------------------
                # 🧠 Fill missing CTL/ATL/TSB (no-activity weeks)
                # -----------------------------------------------------

                # 🧭 Sort by start date for deterministic order
                df_weeks = df_weeks.sort_values("start").reset_index(drop=True)

                # ✅ FIX: normalise projection flag (prevents 7-day fragmentation)
                df_weeks["is_projected"] = df_weeks.get("is_projected", False)
                df_weeks["is_projected"] = df_weeks["is_projected"].fillna(False).astype(bool)

                # track which rows were real measurements
                measured_mask = df_weeks["ctl"].notna()

                # forward fill physiological state
                df_weeks[["ctl", "atl", "tsb"]] = df_weeks[["ctl", "atl", "tsb"]].ffill()

                # optional: tag source (debugging / future use)
                df_weeks["state_source"] = np.where(
                    measured_mask,
                    "measured_activity",
                    "carry_forward_gap"
                )

                # -----------------------------------------------------
                # 🔮 Append future projected ISO weeks
                # -----------------------------------------------------

                future_weeks = build_future_projected_weeks(
                    context=context,
                    weekly_phases=df_weeks.to_dict(orient="records")
                )

                # -----------------------------------------------------
                # 🔮 Store future projected ISO weeks separately
                # -----------------------------------------------------

                semantic["phases_future"] = []

                if future_weeks:

                    df_future = pd.DataFrame(future_weeks)

                    if not df_future.empty:

                        df_future["start"] = pd.to_datetime(
                            df_future["start"],
                            errors="coerce"
                        )

                        df_future["end"] = pd.to_datetime(
                            df_future["end"],
                            errors="coerce"
                        )

                        df_future = (
                            df_future
                            .sort_values("start")
                            .reset_index(drop=True)
                        )

                        semantic["phases_future"] = (
                            df_future.assign(
                                start=lambda x: pd.to_datetime(x["start"]).dt.strftime("%Y-%m-%d"),
                                end=lambda x: pd.to_datetime(x["end"]).dt.strftime("%Y-%m-%d"),
                                ctl=lambda x: pd.to_numeric(x["ctl"], errors="coerce").round(2),
                                atl=lambda x: pd.to_numeric(x["atl"], errors="coerce").round(2),
                                tsb=lambda x: pd.to_numeric(x["tsb"], errors="coerce").round(2),
                            ).to_dict(orient="records")
                        )

                        debug(
                            context,
                            f"[FUTURE] ✅ Stored "
                            f"{len(semantic['phases_future'])} future ISO weeks"
                        )

                # -----------------------------------------------------
                # 🧠 Adjust CURRENT ISO week load using projected plan
                # -----------------------------------------------------

                micro = semantic.get("current_ISO_weekly_microcycle")

                if micro and micro.get("week_iso"):

                    current_week = micro["week_iso"]

                    projected_tss = micro.get("projected_total_tss")
                    projected_hours = micro.get("projected_hours")

                    completed_tss = micro.get("completed_tss")
                    planned_remaining_tss = micro.get("planned_remaining_tss")

                    if projected_tss and projected_tss > 0:

                        # -----------------------------
                        # update dataframe representation
                        # -----------------------------
                        mask = df_weeks["week"] == current_week

                        if mask.any():

                            df_weeks.loc[mask, "tss"] = projected_tss

                            if projected_hours:
                                df_weeks.loc[mask, "hours"] = projected_hours

                            df_weeks.loc[mask, "is_projected"] = True
                            df_weeks.loc[mask, "projection_basis"] = "planned_remaining"

                            # optional transparency fields
                            df_weeks.loc[mask, "completed_tss"] = completed_tss
                            df_weeks.loc[mask, "planned_remaining_tss"] = planned_remaining_tss
                            df_weeks.loc[mask, "projected_total_tss"] = projected_tss
                            # -------------------------------------------------
                            # ALIGN WEEKLY phase TO projected summary phase
                            # -------------------------------------------------
                            proj = micro.get("projected_state")

                            if proj:
                                tsb_proj = float(proj.get("tsb") or 0)

                                if tsb_proj < -30:
                                    df_weeks.loc[mask, "phase"] = "Overreached"
                                elif tsb_proj < -5:
                                    df_weeks.loc[mask, "phase"] = "Build"
                                elif tsb_proj <= 5:
                                    df_weeks.loc[mask, "phase"] = "Base"
                                else:
                                    df_weeks.loc[mask, "phase"] = "Recovery"
                            

                        # -----------------------------
                        # update original weekly source
                        # -----------------------------
                        for wk in raw_weeks:
                            if wk.get("week") == current_week:

                                wk["tss"] = projected_tss

                                if projected_hours:
                                    wk["hours"] = projected_hours

                                wk["is_projected"] = True
                                wk["projection_basis"] = "planned_remaining"

                                wk["completed_tss"] = completed_tss
                                wk["planned_remaining_tss"] = planned_remaining_tss
                                wk["projected_total_tss"] = projected_tss

                                break

                        # -----------------------------
                        # mark microcycle projection
                        # -----------------------------
                        micro["is_projected"] = True

                        debug(
                            context,
                            f"[PHASES] 🔧 Current week projection applied "
                            f"(TSS={projected_tss}, hours={projected_hours}, "
                            f"completed={completed_tss}, remaining={planned_remaining_tss})"
                        )

                # Diagnostic
                debug(
                    context,
                    f"[PHASES] ✅ Injected CTL/ATL/TSB from {key} "
                    f"({len(df_ctl)} weekly rows) — mean TSB={df_ctl['tsb'].mean():.2f}"
                )
            else:
                ws = context.get("wellness_summary", {})
                ctl_val = float(ws.get("ctl", 0.0) or 0.0)
                atl_val = float(ws.get("atl", 0.0) or 0.0)
                tsb_val = float(ws.get("tsb", ctl_val - atl_val) or (ctl_val - atl_val))
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

            df_weeks["classification"] = df_weeks["tsb_capped"].apply(classify_tsb)
            # -----------------------------------------------------
            # 🔒 CLIP TO ISO WINDOW (REPORT-SPECIFIC)
            # -----------------------------------------------------

            debug(
                context,
                "[DEBUG] df_weeks pre-clip:",
                df_weeks[["week","start","end","phase"]].to_dict(orient="records")
            )
            report_type = semantic.get("meta", {}).get("report_type")

            if report_type in ("weekly", "season"):

                today = pd.Timestamp(context["athlete_today"]).normalize()

                # ✅ ISO-aligned week start (Monday)
                current_week_start = today - pd.Timedelta(days=today.weekday())

                weeks_back = 13

                start_week = current_week_start - pd.Timedelta(weeks=weeks_back)
                end_week   = current_week_start

                df_weeks = df_weeks[
                    (df_weeks["start"] >= start_week) &
                    (df_weeks["start"] <= end_week)
                ].reset_index(drop=True)

                debug(
                    context,
                    f"[PHASES] 🧹 ISO CLIP APPLIED → {start_week.date()} → {end_week.date()} "
                    f"(rows={len(df_weeks)})"
                )
                        

            # -----------------------------------------------------
            # 🔗 Propagate phase / calc_method / calc_context from detect_phases()
            # -----------------------------------------------------
            if "phases" in context and isinstance(context["phases"], list) and len(context["phases"]) > 0:
                df_detected = pd.DataFrame(context["phases"])
                if not df_detected.empty:
                    # 🩹 Ensure columns exist in df_weeks before assignment
                    if "phase" not in df_weeks.columns:
                        df_weeks["phase"] = None
                    if "calc_method" not in df_weeks.columns:
                        df_weeks["calc_method"] = None
                    if "calc_context" not in df_weeks.columns:
                        df_weeks["calc_context"] = None

                    # Match by overlapping date ranges
                    for idx, row in df_weeks.iterrows():

                        # 🔒 KEEP projected week phase exactly as already set
                        if row.get("is_projected") is True:
                            continue

                        wk_start, wk_end = row["start"], row["end"]
                        matched = df_detected[
                            (pd.to_datetime(df_detected["start"]) <= wk_end)
                            & (pd.to_datetime(df_detected["end"]) >= wk_start)
                        ]
                        if not matched.empty:
                            df_weeks.at[idx, "phase"] = matched.iloc[-1].get("phase")
                            df_weeks.at[idx, "calc_method"] = matched.iloc[-1].get("calc_method")

                            context_val = matched.iloc[-1].get("calc_context")
                            df_weeks.at[idx, "calc_context"] = (
                                context_val if isinstance(context_val, (dict, type(None))) else dict(context_val)
                            )

                    debug(context, f"[PHASES] 🔄 Propagated phase/calc_method/calc_context into weekly roll-up")
                    debug(
                        context,
                        "[PHASES] weekly propagated phases:",
                        df_weeks[["week", "phase", "calc_method"]].to_dict(orient="records")
                    )



            # -----------------------------------------------------
            # 🧮 Macro-level roll-up (phases_summary) — sequential, boundary-aware
            # -----------------------------------------------------
            summaries = []
            advice = CHEAT_SHEET.get("advice", {}).get("PhaseAdvice", {})

            # 🧭 Sort by start date for deterministic order
            df_weeks = df_weeks.sort_values("start").reset_index(drop=True)

            current_phase = None
            segment_rows = []

            for wk in df_weeks.sort_values("start").to_dict(orient="records"):
                phase = wk.get("phase")
                is_proj = wk.get("is_projected", False)

                # fill Unclassified with previous phase if possible (prevents fragmentation)
                if phase == "Unclassified" and current_phase is not None:
                    phase = current_phase

                wk["phase"] = phase

                if current_phase is None:
                    current_phase = phase
                    current_is_proj = None
                    segment_rows = [wk]
                    continue

                # 🚧 Phase change — flush previous block
                if (
                    phase != current_phase
                    or is_proj != current_is_proj
                ):
                    seg = pd.DataFrame(segment_rows)
                    if not seg.empty:
                        summaries.append({
                            "phase": current_phase,
                            "start": seg["start"].min().strftime("%Y-%m-%d"),
                            "end": seg["end"].max().strftime("%Y-%m-%d"),
                            "duration_days": int((seg["end"].max() - seg["start"].min()).days) + 1,
                            "duration_weeks": round(((seg["end"].max() - seg["start"].min()).days + 1) / 7, 1),
                            "tss_total": round(seg["tss"].sum(), 1),
                            "hours_total": round(seg["hours"].sum(), 1),
                            "distance_km_total": round(seg["distance_km"].sum(), 1),
                            "ctl_end": round(float(seg["ctl"].iloc[-1]), 2) if "ctl" in seg and pd.notna(seg["ctl"].iloc[-1]) else None,
                            "atl_end": round(float(seg["atl"].iloc[-1]), 2) if "atl" in seg and pd.notna(seg["atl"].iloc[-1]) else None,
                            "tsb_end": round(float(seg["tsb"].iloc[-1]), 2) if "tsb" in seg and pd.notna(seg["tsb"].iloc[-1]) else None,
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

                    current_phase = phase
                    current_is_proj = is_proj
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
                    "duration_weeks": round(((seg["end"].max() - seg["start"].min()).days + 1) / 7, 1),
                    "tss_total": round(seg["tss"].sum(), 1),
                    "hours_total": round(seg["hours"].sum(), 1),
                    "distance_km_total": round(seg["distance_km"].sum(), 1),
                    "ctl_end": round(float(seg["ctl"].iloc[-1]), 2) if "ctl" in seg and pd.notna(seg["ctl"].iloc[-1]) else None,
                    "atl_end": round(float(seg["atl"].iloc[-1]), 2) if "atl" in seg and pd.notna(seg["atl"].iloc[-1]) else None,
                    "tsb_end": round(float(seg["tsb"].iloc[-1]), 2) if "tsb" in seg and pd.notna(seg["tsb"].iloc[-1]) else None,
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

            # -----------------------------------------------------
            # 🔧 PATCH projection metadata into summary
            # -----------------------------------------------------

            micro = semantic.get("current_ISO_weekly_microcycle")

            if micro and micro.get("week_iso"):

                iso_week = micro["week_iso"]

                for block in summaries:

                    # derive ISO week from block start date
                    block_start = pd.Timestamp(block["start"])
                    block_end   = pd.Timestamp(block["end"])

                    micro_start = pd.Timestamp.fromisocalendar(
                        int(iso_week.split("-W")[0]),
                        int(iso_week.split("-W")[1]),
                        1
                    )
                    micro_end = micro_start + pd.Timedelta(days=6)

                    if block_start <= micro_end and block_end >= micro_start:

                        block["is_projected"] = True
                        block["projection_basis"] = "planned_remaining"

                        block["completed_tss"] = micro.get("completed_tss")
                        block["planned_remaining_tss"] = micro.get("planned_remaining_tss")
                        block["projected_total_tss"] = micro.get("projected_total_tss")

                        block["completed_hours"] = micro.get("completed_hours")
                        block["projected_hours"] = micro.get("projected_hours")

                        # ensure totals reflect projected state
                        if micro.get("projected_total_tss") is not None:
                            block["tss_total"] = micro["projected_total_tss"]

                        if micro.get("projected_hours") is not None:
                            block["hours_total"] = round(micro["projected_hours"], 1)

                        block["distance_km_total"] = None

                        # -------------------------------------------------
                        # 🧮 PHYSIOLOGICAL PROJECTION (RAILWAY SAFE)
                        # -------------------------------------------------

                        proj = micro.get("projected_state")

                        # 🔒 HARD NORMALISATION (structure)
                        if not isinstance(proj, dict):
                            proj = None

                        # 🔒 HARD NORMALISATION (values)
                        def _to_float(v):
                            try:
                                if v is None:
                                    return None
                                if isinstance(v, str):
                                    v = v.strip()
                                    if v == "":
                                        return None
                                f = float(v)
                                if pd.isna(f):
                                    return None
                                return f
                            except Exception:
                                return None

                        if proj:
                            ctl = _to_float(proj.get("ctl"))
                            atl = _to_float(proj.get("atl"))
                            tsb = _to_float(proj.get("tsb"))

                            # only accept if at least tsb is valid
                            if tsb is not None:
                                block["projected_state"] = {
                                    "ctl": ctl,
                                    "atl": atl,
                                    "tsb": tsb,
                                    "source": proj.get("source", "unknown")
                                }

                                # 🔒 SAFE CLASSIFICATION
                                if tsb < -30:
                                    block["phase"] = "Overreached"
                                elif tsb < -5:
                                    block["phase"] = "Build"
                                elif tsb <= 5:
                                    block["phase"] = "Base"
                                else:
                                    block["phase"] = "Recovery"

                            else:
                                # tsb invalid → drop projection
                                block["projected_state"] = None
                        else:
                            block["projected_state"] = None

                        # -------------------------------------------------
                        # 📊 Projection intent (keep)
                        # -------------------------------------------------
                        block["projection_intent"] = {
                            "direction": (
                                "increase"
                                if micro.get("projected_total_tss", 0) > micro.get("completed_tss", 0)
                                else "stable"
                            ),
                            "remaining_load": micro.get("planned_remaining_tss", 0)
                        }

                        # -------------------------------------------------
                        # 🔎 Traceability (keep)
                        # -------------------------------------------------
                        block["calc_method"] = "projection_forecast"
                        block["calc_context"] = None

                        # -------------------------------------------------
                        # 🧠 Descriptor aligned to FINAL phase (important)
                        # -------------------------------------------------
                        if block.get("phase"):
                            block["descriptor"] = advice.get(
                                block["phase"],
                                f"{block['phase']} phase — maintain adaptive consistency."
                            )

                        break

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
                        "ctl", "atl", "tsb", "phase", "classification"
                    ]
                ].to_dict(orient="records")
            )
            micro = semantic.get("current_ISO_weekly_microcycle")

            if micro and micro.get("week_iso"):

                for row in weekly_output:

                    if row["week"] == micro["week_iso"]:

                        row["is_projected"] = True
                        row["completed_tss"] = micro.get("completed_tss")
                        row["planned_remaining_tss"] = micro.get("planned_remaining_tss")
                        row["projected_total_tss"] = micro.get("projected_total_tss")
                        row["projected_hours"] = micro.get("projected_hours")

                        break

            semantic["phases"] = weekly_output
            debug(context, f"[PHASES] ✅ Cleaned weekly phase output ({len(weekly_output)} weeks)")

            # ---------------------------------------------------------
            # 📈 Season / Summary Trend Metrics (URF-canonical)
            # MUST run AFTER final semantic["phases"] is built
            # ---------------------------------------------------------
            if report_type in ("season", "summary", "weekly") and semantic.get("phases"):
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
            # Enforce output ordering
            # phases_summary → phases → phases_future
            # -----------------------------------------------------

            ordered = {}

            for k, v in semantic.items():
                if k not in (
                    "phases_summary",
                    "phases",
                    "phases_future"
                ):
                    ordered[k] = v

            if "phases_summary" in semantic:
                ordered["phases_summary"] = semantic["phases_summary"]

            if "phases" in semantic:
                ordered["phases"] = semantic["phases"]

            if "phases_future" in semantic:
                ordered["phases_future"] = semantic["phases_future"]

            semantic.clear()
            semantic.update(ordered)

    # ---------------------------------------------------------
    # 🧠 INSIGHTS (computed once, after all metrics resolved)
    # ---------------------------------------------------------
    semantic["insights"] = build_insights(semantic)

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

    # ---------------------------------------------------------
    # 🫀 FINAL Physiology State resolution
    # Must run AFTER build_insights(), because build_insights()
    # injects resting_hr_delta and sleep_score into wellness.
    # ---------------------------------------------------------
    if "wellness" in semantic:
        semantic["wellness"]["physiology_state"] = resolve_physiology_state(
            semantic["wellness"],
            CHEAT_SHEET
        )

        debug(
            context,
            f"[SEMANTIC] FINAL wellness physiology_state → "
            f"{semantic['wellness']['physiology_state'].get('key')} / "
            f"{semantic['wellness']['physiology_state'].get('label')} | "
            f"rest_delta={semantic['wellness']['physiology_state']['inputs'].get('resting_hr_delta')} "
            f"sleep={semantic['wellness']['physiology_state']['inputs'].get('sleep_score')}"
        )

    
    # ---------------------------------------------------------
    # 📊 Metric Signals (Tier-2 commentary → insight_view)
    # ---------------------------------------------------------

    metric_signals = context.get("metric_signals", []) or []

    if metric_signals:

        insight_view = semantic.setdefault(
            "insight_view",
            {"critical": [], "watch": [], "positive": []}
        )

        for s in metric_signals:

            if not isinstance(s, dict):
                continue

            metric = s.get("metric")
            state = s.get("state")
            value = s.get("value")

            if not metric:
                continue

            interpretation = CHEAT_SHEET["context"].get(metric)
            coaching = CHEAT_SHEET["coaching_links"].get(metric)

            classification = CLASSIFICATION_ALIASES.get(state, "green")

            entry = {
                "name": metric,
                "classification": classification,
                "interpretation": interpretation,
                "coaching_implication": coaching,
            }

            if value is not None:
                entry["value"] = value

            insight_view["positive"].append(entry)

    # ---------------------------------------------------------
    # ADE → SEMANTIC ACTION
    # ---------------------------------------------------------

    ade = context.get("adaptive_decision")

    if ade:
        semantic.setdefault("actions", [])

        semantic["actions"].insert(0, {
            "type": "adaptive_summary",
            "role": "directive",
            "priority": "primary",
            "label": "Coaching Directive",
            "source": "adaptive_decision_engine",

            **ade
        })

    # ---------------------------------------------------------
    # 🧭 PHASE CONTEXT (PAST → CURRENT → FUTURE ALIGNMENT)
    # ---------------------------------------------------------
    phase_override = False
    try:

        phases = semantic.get("phases", [])
        summaries = semantic.get("phases_summary", [])
        ts = context.get("training_state", {})
        micro = semantic.get("current_ISO_weekly_microcycle", {})

        # -----------------------------
        # Past pattern (sequence + streak)
        # -----------------------------
        recent = phases[-6:]
        recent_labels = [p.get("classification") for p in recent if p.get("classification")]

        fatigue_labels = {"Overreached"}

        fatigue_streak = 0
        for label in reversed(recent_labels):
            if label in fatigue_labels:
                fatigue_streak += 1
            else:
                break

        if fatigue_streak >= 2:
            past_pattern = "fatigue_streak"   # already concerning
        elif fatigue_streak == 1:
            past_pattern = "overreach_event"  # normal if followed by recovery
        elif "Recovery" in recent_labels:
            past_pattern = "recovery_present"
        else:
            past_pattern = "mixed"

        # -----------------------------
        # Block context (REMOVE projected)
        # -----------------------------
        real_blocks = [b for b in summaries if not b.get("is_projected")]

        recent_blocks = real_blocks[-4:] if real_blocks else []
        last_block = recent_blocks[-1] if recent_blocks else {}

        last_block_phase = last_block.get("phase")
        last_block_days = last_block.get("duration_days", 0)

        # -----------------------------
        # Current
        # -----------------------------
        operational_state = ts.get("operational_state")
        current_state = ts.get("state_label")

        # -----------------------------
        # Future (planned) — source of truth = projected block + forecast
        # -----------------------------
        planned_pattern = "unknown"

        forecast_block = semantic.get("future_forecast", {})
        summaries = semantic.get("phases_summary", [])

        forecast_load_trend = forecast_block.get("load_trend")
        forecast_fatigue_class = forecast_block.get("fatigue_class")
        ade_action = next(
            (
                a for a in semantic.get("actions", [])
                if isinstance(a, dict) and a.get("type") == "adaptive_summary"
            ),
            {}
        )

        taper_governance = ade_action.get("taper_governance") or {}
        taper_governance_state = taper_governance.get("state")

        allows_taper_sharpening = taper_governance_state in {
            "taper_sharpening_required",
            "freshness_above_target",
        }

        projected_block = next((b for b in summaries if b.get("is_projected")), None)
        projected_phase = (
            (projected_block.get("phase") if projected_block else None)
            or last_block_phase
            or ""
        ).lower()

        # Structural intent first
        if projected_phase in {"recovery", "deload", "taper"}:
            planned_pattern = "reduced"
        elif projected_phase in {"build", "peak"}:
            planned_pattern = "increasing"
        elif forecast_load_trend == "declining":
            planned_pattern = "reduced"
        elif forecast_load_trend == "increasing":
            planned_pattern = "increasing"
        elif forecast_load_trend == "stable":
            planned_pattern = "stable"

        # -----------------------------
        # Required phase (physiology FIRST)
        # -----------------------------
        current_phase = (projected_phase or "").lower()
        last_phase = (last_block_phase or "").lower()

        if last_phase in {"recovery", "deload", "taper"}:
            required_phase = "recovery"
        else:
            required_phase = current_phase or "build"

        # Fatigue-class fallback only if still unknown
        # No further fallback — unknown stays unknown
        # -----------------------------
        # Required phase (SAFE + PRIORITY)
        # -----------------------------
        required_phase = None

        # -------------------------
        # Phase context
        # -------------------------
        current_phase = (projected_phase or "").lower()
        last_phase = (last_block_phase or "").lower()

        # -------------------------
        # Recovery gating (PHASE ONLY)
        # -------------------------
        # Required phase priority
        # 1. A-race taper window
        # 2. Recovery / deload projected phase
        # 3. Projected current phase
        # -------------------------

        target_event = ade.get("target_event", {}) if isinstance(ade, dict) else {}
        taper_state = target_event.get("taper_state")
        days_to_event = target_event.get("days_to_event")

        if (
            taper_state == "taper"
            and days_to_event is not None
            and days_to_event <= 10
        ):
            required_phase = "taper"

        elif projected_phase in {"recovery", "deload"}:
            required_phase = "recovery"

        elif projected_phase == "taper":
            required_phase = "taper"

        else:
            required_phase = current_phase or "build"

        # -----------------------------
        # Alignment (phase vs plan direction)
        # -----------------------------
        alignment = "aligned"

        if planned_pattern == "unknown":
            alignment = "unknown"

        elif required_phase in {"recovery", "taper"}:

            # Taper exception:
            # if athlete is too fresh and ADE says sharpening is required,
            # increasing load is not automatically misaligned.
            if planned_pattern == "increasing" and allows_taper_sharpening:
                alignment = "aligned_with_sharpening"

            elif planned_pattern == "increasing":
                alignment = "misaligned"

            else:
                alignment = "aligned"

        else:  # build / base / peak

            # Base exception:
            # reduced load during Base is not a hard plan-governance conflict.
            # It is a soft underload / reduced-base warning.
            if required_phase == "base" and planned_pattern == "reduced":
                alignment = "underload_watch"

            else:
                alignment = "misaligned" if planned_pattern == "reduced" else "aligned"

        # -----------------------------
        # Output FIRST (important)
        # -----------------------------
        semantic["phase_alignment"] = {
            "past_pattern": past_pattern,
            "current_state": current_state,
            "operational_state": operational_state,
            "planned_pattern": planned_pattern,
            "required_phase": required_phase,
            "alignment": alignment,
            "phase_streak": {
                "type": "fatigue" if fatigue_streak else "none",
                "length": fatigue_streak
            },
            "last_block": {
                "phase": last_block_phase,
                "duration_days": last_block_days
            }
        }

        # ---------------------------------------------------------
        # 🧭 TRAINING GUIDANCE (FINAL — GOVERNED + MODULATED)
        # ---------------------------------------------------------

        ade_directive = ade["directive"]
        phase = semantic["phase_alignment"]["required_phase"]

        future_action = semantic.get("future_actions", [{}])[0]
        future_title = future_action.get("title", "").lower()

        base_guidance = ade_directive
        phase_override = False

        # -------------------------
        # HARD RULE (PHASE = SHOULD, ALWAYS APPLIED)
        # -------------------------
        if phase == "taper":

            if allows_taper_sharpening:
                decision = (
                    f"{base_guidance} — keep controlled race-specific sharpening "
                    "and avoid excess endurance volume"
                )
            else:
                decision = f"{base_guidance} — prioritise taper freshness and maintain low load"

            phase_override = True

        elif phase == "recovery":
            decision = f"{base_guidance} — prioritise recovery"

            if "neutral" in future_title:
                decision += " and maintain low load"
            elif "increase" in future_title or "build" in future_title:
                decision += " despite upcoming load progression"
            elif "recovery" in future_title:
                decision += " and allow full adaptation"

            phase_override = True

        # -------------------------
        # SOFT RULE (FORECAST via ACTION)
        # -------------------------
        else:
            decision = base_guidance
            if "neutral" in future_title:
                decision += " — maintain balanced load"
            elif "increase" in future_title or "build" in future_title:
                decision += " — progress load carefully"
            elif "recovery" in future_title:
                decision += " — allow for recovery adaptation"

        # -------------------------
        # FINAL (CAN vs SHOULD)
        # -------------------------
        final_guidance = f"Can: {ade_directive} | Should: {phase.capitalize()} → {decision}"

        semantic["training_guidance"] = final_guidance

        semantic["decision_context"] = {
            "ade_directive": ade_directive,
            "required_phase": phase,
            "alignment": alignment,
            "phase_override": phase_override,
            "forecast_trend": forecast_block.get("load_trend")
        }
        debug(context, f"[PHASE_ALIGNMENT] required={phase} alignment={alignment}")

    except Exception as e:
        debug(context, f"[PHASE_ALIGNMENT] ⚠️ failed: {e}")

    # ---------------------------------------------------------
    # ALIGN ADE ACTION WITH PHASE GOVERNANCE (CRITICAL)
    # ---------------------------------------------------------

    if semantic.get("actions"):
        ade_action = next(
            (
                a for a in semantic["actions"]
                if isinstance(a, dict) and a.get("type") == "adaptive_summary"
            ),
            None
        )

        if ade_action:
            ade_action["phase_constraint"] = phase
            ade_action["phase_alignment"] = alignment

            if alignment == "aligned_with_sharpening":
                ade_action["resolution"] = "honoured_with_sharpening"
                semantic.pop("conflict", None)

            elif phase_override:
                ade_action["resolution"] = "overridden_by_phase"

                semantic["conflict"] = {
                    "metrics_state": ade.get("operational_state"),
                    "phase_requirement": phase,
                    "resolution": "override"
                }

            else:
                ade_action["resolution"] = "honoured"
                semantic.pop("conflict", None)

    # ---------------------------------------------------------
    # 🎯 EVENT READINESS GOVERNANCE SYNC
    # ---------------------------------------------------------
    # Adds display-safe event readiness governance.
    # Does not recompute race score.
    # Prevents UI showing plain READY when ADE has taper conflict.
    # ---------------------------------------------------------

    try:
        event_targets = semantic.get("event_targets") or {}
        next_event = event_targets.get("next_event") or {}

        actions = semantic.get("actions") or []
        adaptive_summary = next(
            (
                a for a in actions
                if isinstance(a, dict) and a.get("type") == "adaptive_summary"
            ),
            {}
        )

        taper_governance = adaptive_summary.get("taper_governance") or {}
        decision_context = semantic.get("decision_context") or {}

        has_event = bool(event_targets.get("exists")) and bool(next_event.get("name"))

        taper_state = taper_governance.get("state")

        has_taper_conflict = taper_state in {
            "taper_load_conflict",
            "taper_load_risk",
        }

        has_taper_sharpening = taper_state in {
            "taper_sharpening_required",
            "freshness_above_target",
        }

        if has_event:

            governance_status = "aligned"
            readiness_label = "READY"
            readiness_modifier = None
            limiting_factors = []

            tsb_target = (
                next_event.get("race_profile", {})
                .get("targets", {})
                .get("tsb")
            )

            event_ctl = next_event.get("icu_ctl")
            event_atl = next_event.get("icu_atl")

            event_tsb = None
            try:
                if event_ctl is not None and event_atl is not None:
                    event_tsb = round(float(event_ctl) - float(event_atl), 2)
            except Exception:
                event_tsb = None

            form_status = None

            if (
                isinstance(tsb_target, list)
                and len(tsb_target) == 2
                and event_tsb is not None
            ):
                low, high = tsb_target

                if event_tsb < low:
                    form_status = "too_fatigued"
                    limiting_factors.append("TSB below event target")
                elif event_tsb > high:
                    form_status = "too_fresh"
                    limiting_factors.append("TSB above event target")
                else:
                    form_status = "target_range"

                if has_taper_conflict:
                    governance_status = "taper_misaligned"
                    readiness_label = "CONDITIONALLY_READY"
                    readiness_modifier = "plan_risk"

                    reason = taper_governance.get("reason")
                    limiting_factors.insert(0, reason or "Taper load conflict")

                elif has_taper_sharpening:
                    governance_status = "sharpening_required"
                    readiness_label = "READY_WITH_SHARPENING"
                    readiness_modifier = "freshness_above_target"

                    reason = taper_governance.get("reason")
                    if reason:
                        limiting_factors.insert(0, reason)

            durability_state = (
                semantic.get("performance_intelligence", {})
                .get("acute", {})
                .get("durability", {})
                .get("state", {})
            )

            if isinstance(durability_state, dict):
                dur_value = durability_state.get("value")
                if dur_value in ("drifting", "declining"):
                    limiting_factors.append("Durability drift")

            next_event["readiness_governance"] = {
                "status": governance_status,
                "readiness_label": readiness_label,
                "readiness_modifier": readiness_modifier,
                "form_status": form_status,
                "event_tsb": event_tsb,
                "target_tsb_range": tsb_target,
                "phase_required": (
                    adaptive_summary.get("phase_constraint")
                    or decision_context.get("required_phase")
                    or next_event.get("taper_state")
                ),
                "phase_alignment": (
                    adaptive_summary.get("phase_alignment")
                    or decision_context.get("alignment")
                ),
                "resolution": adaptive_summary.get("resolution"),
                "taper_governance": taper_governance or None,
                "limiting_factors": list(dict.fromkeys([
                    x for x in limiting_factors if x
                ])),
                "display_rule": (
                    "If readiness_label is READY_WITH_SHARPENING, UI must not display plain READY. "
                    "Show race score unchanged, but qualify readiness as ready with controlled sharpening."
                )
            }

            event_targets["next_event"] = next_event
            semantic["event_targets"] = event_targets

            debug(
                context,
                "[EVENT_READINESS_GOVERNANCE] "
                f"{next_event.get('name')} → "
                f"{next_event['readiness_governance']['readiness_label']} / "
                f"{next_event['readiness_governance']['status']}"
            )

    except Exception as e:
        debug(context, f"[EVENT_READINESS_GOVERNANCE] ⚠️ failed: {e}")


    # --------------------------------------------------
    # 🔥 Outliers (365d)
    # --------------------------------------------------
    outliers = context.get("outliers")

    if outliers:
        semantic.setdefault("outliers", {
            "block_type": "outliers",
            "version": "v1",
            "items": outliers,
            "summary": context.get("outlier_summary", {}),
        })

    # ---------------------------------------------------------
    # 🧠 LLM CONTROL SIGNALS (FINAL PROMOTION)
    # MUST BE LAST STEP BEFORE RETURN
    # ---------------------------------------------------------

    # Training context (correct as-is)
    if context.get("training_context"):
        semantic["training_context"] = context["training_context"]


    # ---------------------------------------------------------
    # ✅ Contract Enforcement
    # ---------------------------------------------------------

    def safe_len(x):
        try:
            if hasattr(x, "shape"):
                return int(x.shape[0])
            if isinstance(x, (list, tuple, dict)):
                return len(x)
        except Exception:
            pass
        return 0

    light_src = context.get("activities_light")
    if light_src is None:
        light_src = context.get("df_light")

    wellness_src = context.get("wellness_daily")
    if wellness_src is None:
        wellness_src = context.get("df_wellness")

    summary = {
        "status": "ok",
        "note": "semantic JSON finalized (markdown skipped)",
        "rows": {
            "full": safe_len(df_events),
            "light": safe_len(light_src),
            "wellness": safe_len(wellness_src),
            "power_curves": safe_len(context.get("power_curve")),
        }
    }
    semantic = apply_report_type_contract(semantic)
    semantic["summary"] = summary
    return semantic


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
        confidence = ins.get("metric_confidence", "high")

        if confidence == "contextual":
            continue

        if not cls:
            continue

        color = CLASSIFICATION_ALIASES.get(cls, cls)

        entry = {
            "name": key,
            "classification": cls,
            "interpretation": ins.get("interpretation"),
            "coaching_implication": ins.get("coaching_implication"),
        }

        for extra_key in ("value", "window", "basis"):
            if ins.get(extra_key) is not None:
                entry[extra_key] = ins.get(extra_key)

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
    Enforce report-type-specific semantic exposure (URF v5.1)
    + apply nested prune rules (PRUNE_RULES)

    Single execution point.
    """

    report_type = semantic.get("meta", {}).get("report_type", "weekly")
    render_mode = semantic.get("meta", {}).get("render_mode", "full+metrics")

    if render_mode == "overview":
        contract_key = f"{report_type}_overview"
    elif render_mode == "lite":
        contract_key = f"{report_type}_lite"
    elif render_mode == "workflow":
        contract_key = f"{report_type}_workflow"
    else:
        contract_key = report_type

    # ── Enrich meta
    semantic["meta"]["report_header"] = REPORT_HEADERS.get(report_type, {})
    semantic["meta"]["resolution"] = REPORT_RESOLUTION.get(report_type, {})
    semantic["header"] = semantic["meta"]["report_header"]

    # ── Recency governance
    # Must run BEFORE contract filtering so stale weekly reports
    # cannot expose current/live ADE guidance.
    semantic = apply_report_recency_governance(semantic)

    # ── Top-level filtering (contract)
    allowed_keys = REPORT_CONTRACT.get(contract_key, semantic.keys())
    filtered = {k: v for k, v in semantic.items() if k in allowed_keys}

    # ─────────────────────────────────────────────
    # 🔥 APPLY PRUNE RULES (inline, no helper)
    # ─────────────────────────────────────────────
    prune_map = PRUNE_RULES.get(contract_key, {})

    for path, keys in prune_map.items():
        ref = filtered

        # walk dot path safely
        for part in path.split("."):
            if not isinstance(ref, dict):
                ref = None
                break
            ref = ref.get(part)

        if isinstance(ref, dict):
            for k in keys:
                ref.pop(k, None)

    # ── Renderer instructions (DATA ONLY)
    filtered["renderer_instructions"] = build_system_prompt_from_header(
        contract_key,
        REPORT_HEADERS.get(report_type, {})
    )

    # ── Contract drift detection
    unexpected = set(semantic.keys()) - set(allowed_keys)
    if unexpected:
        from audit_core.utils import debug
        debug(
            {},
            f"[CONTRACT] ⚠️ Unexpected keys in '{report_type}' report: {unexpected}"
        )

    return filtered



