"""
Energy System Progression Engine (ESPE)
Version: v1.23

Stateless engine comparing two rolling power-curve windows to track energy system progression.

Consumes:
    power_curve block injected by Worker

Produces:
    energy_system_progression section

v1.2 factored for baseline where no previous exists
"""

from typing import Dict, Any, Optional

from coaching_cheat_sheet import CHEAT_SHEET
from audit_core.utils import debug
from coaching_profile import COACH_PROFILE

ESPE_VERSION = "espe_v1.23"

# ---------------------------------------------------------------------
# Power Anchor Helpers
# ---------------------------------------------------------------------

def _power(v):
    if isinstance(v, dict):
        return v.get("power")
    return v

def _activity_id(v):
    if isinstance(v, dict):
        return v.get("activity_id")
    return None

def _anchor_meta(v):
    if isinstance(v, dict):
        aid = v.get("activity_id")
        return {
            "power": v.get("power"),
            "activity_id": aid,
            "activity_link": f"https://intervals.icu/activities/{aid}" if aid else None
        }
    return {
        "power": v,
        "activity_id": None,
        "activity_link": None
    }

FATIGUE_ANCHORS = (
    "5s",
    "1m",
    "5m",
    "20m",
    "60m",
)

FATIGUE_DOMAIN_ANCHORS = {
    "short_power": ("5s", "1m"),
    "vo2": ("5m",),
    "threshold": ("20m",),
    "long_duration": ("60m",),
}

# Montis operational deadband for longitudinal retention change.
# This is governance, not a universal physiological threshold.
FATIGUE_TREND_DEADBAND_PP = 2.0


def _median(values):
    numeric = sorted(
        value
        for value in values
        if _is_number(value)
    )

    if not numeric:
        return None

    midpoint = len(numeric) // 2

    if len(numeric) % 2:
        return numeric[midpoint]

    return (
        numeric[midpoint - 1] + numeric[midpoint]
    ) / 2


def _build_fatigue_summary(
    thresholds,
) -> Dict[str, Any]:
    """
    Derive a governed fatigue-resistance summary.

    State and trend are evaluated at the highest athlete-configured
    after_kj threshold for which current and previous fatigued curves
    match. If no previous match exists, use the highest current
    threshold and report a baseline trend.
    """

    if not thresholds:
        return {
            "state": "unknown",
            "primary_limiter": None,
            "confidence": "low",
            "trend": "baseline",
            "evaluated_after_kj": None,
            "overall_retention_percent": None,
            "previous_overall_retention_percent": None,
            "retention_change_pp": None,
            "limiter_retention_percent": None,
        }

    matched_thresholds = [
        threshold
        for threshold in thresholds
        if threshold.get("previous_retention_percent")
    ]

    evaluated = max(
        matched_thresholds or thresholds,
        key=lambda item: item.get("after_kj") or 0,
    )

    retention = (
        evaluated.get("retention_percent")
        or {}
    )

    previous_retention = (
        evaluated.get("previous_retention_percent")
        or {}
    )

    def _domain_values(anchor_retention):
        output = {}

        for domain, anchors in FATIGUE_DOMAIN_ANCHORS.items():
            values = [
                anchor_retention.get(anchor)
                for anchor in anchors
                if _is_number(anchor_retention.get(anchor))
            ]

            domain_value = _median(values)

            if domain_value is not None:
                output[domain] = round(domain_value, 2)

        return output

    domain_retention = _domain_values(retention)
    previous_domain_retention = _domain_values(previous_retention)

    domain_count = len(domain_retention)

    if domain_count < 3:
        return {
            "state": "unknown",
            "primary_limiter": None,
            "confidence": "low",
            "trend": "baseline",
            "evaluated_after_kj": evaluated.get("after_kj"),
            "overall_retention_percent": None,
            "previous_overall_retention_percent": None,
            "retention_change_pp": None,
            "limiter_retention_percent": None,
        }

    overall_retention = round(
        _median(domain_retention.values()),
        2,
    )

    primary_limiter = min(
        domain_retention,
        key=domain_retention.get,
    )

    limiter_retention = domain_retention[
        primary_limiter
    ]

    previous_overall_retention = None
    retention_change_pp = None
    trend = "baseline"

    if len(previous_domain_retention) >= 3:
        previous_overall_retention = round(
            _median(previous_domain_retention.values()),
            2,
        )

        retention_change_pp = round(
            overall_retention - previous_overall_retention,
            2,
        )

        if retention_change_pp >= FATIGUE_TREND_DEADBAND_PP:
            trend = "improving"
        elif retention_change_pp <= -FATIGUE_TREND_DEADBAND_PP:
            trend = "declining"
        else:
            trend = "stable"

    if overall_retention >= 90:
        state = "robust"
    elif overall_retention >= 80:
        state = "moderate"
    else:
        state = "limited"

    if (
        len(matched_thresholds) >= 2
        and domain_count == len(FATIGUE_DOMAIN_ANCHORS)
        and len(previous_domain_retention) == len(FATIGUE_DOMAIN_ANCHORS)
    ):
        confidence = "high"
    elif (
        matched_thresholds
        and domain_count >= 3
        and len(previous_domain_retention) >= 3
    ):
        confidence = "moderate"
    else:
        confidence = "low"

    return {
        "state": state,
        "primary_limiter": primary_limiter,
        "confidence": confidence,
        "trend": trend,
        "evaluated_after_kj": evaluated.get("after_kj"),
        "overall_retention_percent": overall_retention,
        "previous_overall_retention_percent": previous_overall_retention,
        "retention_change_pp": retention_change_pp,
        "limiter_retention_percent": limiter_retention,
    }

def _is_number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
    )

def _build_fatigue_resistance(
    sport: str,
    data: Dict[str, Any],
    current: Dict[str, Any],
    context: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Build compact threshold-specific fatigue-resistance observations.

    kj0/kj1 are source-slot identifiers only.
    after_kj is the authoritative athlete-configured threshold.
    """

    if sport != "Ride":
        return None

    fatigued = data.get("fatigued") or {}
    fatigued_current = fatigued.get("current") or {}
    fatigued_previous = fatigued.get("previous") or {}

    if not isinstance(fatigued_current, dict):
        return None

    if not isinstance(fatigued_previous, dict):
        fatigued_previous = {}

    previous = data.get("previous") or {}

    # Match periods by authoritative athlete-configured kJ value,
    # never by the configurable kj0/kj1 source slot.
    previous_by_kj = {}

    for source_slot, curve in fatigued_previous.items():
        if not isinstance(curve, dict):
            continue

        try:
            after_kj = int(curve.get("after_kj"))
        except (TypeError, ValueError):
            debug(
                context,
                "[ESPE-FR] Ignoring previous fatigued curve with invalid "
                f"after_kj slot={source_slot} value={curve.get('after_kj')}"
            )
            continue

        if 100 <= after_kj <= 9999:
            previous_by_kj[after_kj] = curve

    thresholds = []

    for source_slot, curve in fatigued_current.items():
        if not isinstance(curve, dict):
            continue

        after_kj_raw = curve.get("after_kj")

        try:
            after_kj = int(after_kj_raw)
        except (TypeError, ValueError):
            debug(
                context,
                "[ESPE-FR] Ignoring fatigued curve with invalid "
                f"after_kj slot={source_slot} value={after_kj_raw}"
            )
            continue

        if after_kj < 100 or after_kj > 9999:
            debug(
                context,
                "[ESPE-FR] Ignoring fatigued curve outside supported "
                f"range slot={source_slot} after_kj={after_kj}"
            )
            continue

        fatigued_anchors = curve.get("anchors") or {}
        previous_curve = previous_by_kj.get(after_kj) or {}
        previous_fatigued_anchors = (
            previous_curve.get("anchors") or {}
        )

        fatigued_power_w = {}
        retention_percent = {}
        previous_retention_percent = {}
        retention_change_pp = {}

        for anchor_name in FATIGUE_ANCHORS:
            normal_power = _power(current.get(anchor_name))
            fatigued_power = _power(
                fatigued_anchors.get(anchor_name)
            )

            if (
                not _is_number(normal_power)
                or not _is_number(fatigued_power)
                or normal_power <= 0
                or fatigued_power <= 0
            ):
                continue

            fatigued_power_w[anchor_name] = fatigued_power
            retention_percent[anchor_name] = round(
                (fatigued_power / normal_power) * 100,
                2
            )

            previous_normal_power = _power(
                previous.get(anchor_name)
            )
            previous_fatigued_power = _power(
                previous_fatigued_anchors.get(anchor_name)
            )

            if (
                not _is_number(previous_normal_power)
                or not _is_number(previous_fatigued_power)
                or previous_normal_power <= 0
                or previous_fatigued_power <= 0
            ):
                continue

            previous_anchor_retention = round(
                (
                    previous_fatigued_power
                    / previous_normal_power
                ) * 100,
                2,
            )

            previous_retention_percent[
                anchor_name
            ] = previous_anchor_retention

            retention_change_pp[anchor_name] = round(
                retention_percent[anchor_name]
                - previous_anchor_retention,
                2,
            )

        if not fatigued_power_w:
            debug(
                context,
                "[ESPE-FR] Ignoring fatigued curve with no usable "
                f"anchors slot={source_slot}"
            )
            continue

        threshold_result = {
            "after_kj": after_kj,
            "fatigued_power_w": fatigued_power_w,
            "retention_percent": retention_percent,
        }

        if previous_retention_percent:
            threshold_result[
                "previous_retention_percent"
            ] = previous_retention_percent
            threshold_result[
                "retention_change_pp"
            ] = retention_change_pp

        thresholds.append(threshold_result)

    if not thresholds:
        return None

    thresholds.sort(
        key=lambda threshold: threshold["after_kj"]
    )

    debug(
        context,
        "[ESPE-FR] Fatigued Ride curves processed → "
        f"thresholds={[item['after_kj'] for item in thresholds]} "
        f"matched_previous={len(previous_by_kj)}"
    )

    summary = _build_fatigue_summary(thresholds)

    debug(
        context,
        "[ESPE-FR] Summary → "
        f"state={summary['state']} "
        f"limiter={summary['primary_limiter']} "
        f"trend={summary['trend']} "
        f"change_pp={summary['retention_change_pp']} "
        f"after_kj={summary['evaluated_after_kj']} "
        f"confidence={summary['confidence']}"
    )

    return {
        "supported": True,
        "source": "INTERVALS_FATIGUED_POWER_CURVES",
        "comparison_reference": "current_normal_power_curve",
        "thresholds_are_athlete_configured": True,
        "thresholds": thresholds,
        "summary": summary,
    }


# ---------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------

def run_espe(power_curve_block: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:

    result = {
        "version": ESPE_VERSION,
        "sports": {}
    }

    if not power_curve_block:
        debug(context, "[ESPE] no power_curve block provided")
        return _unsupported("missing power curve data")

    for sport, data in power_curve_block.items():

        debug(context, f"[ESPE] processing sport={sport}")

        current = data.get("current", {})
        previous = data.get("previous", {})

        # --- require CURRENT only ---
        required = ["5m", "20m"] if sport == "Run" else ["1m", "5m", "20m", "60m"]

        has_current = all(
            (_power(current.get(k)) is not None and _power(current.get(k)) > 0)
            for k in required
        )

        if not has_current:
            result["sports"][sport] = _unsupported("missing current power data")
            continue

        # --- check if comparison is possible ---
        has_previous = all(
            (_power(previous.get(k)) is not None and _power(previous.get(k)) > 0)
            for k in required
        )

        result["sports"][sport] = _process_sport(sport, data, context)

    return result


# ---------------------------------------------------------------------
# Core Logic
# ---------------------------------------------------------------------
def _process_sport(sport: str, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:

    current = data["current"]
    previous = data["previous"]

    anchors = {
        "5s": _anchor_meta(current.get("5s")),
        "1m": _anchor_meta(current.get("1m")),
        "5m": _anchor_meta(current.get("5m")),
        "20m": _anchor_meta(current.get("20m")),
        "60m": _anchor_meta(current.get("60m")),
    }

    has_previous = any(
    _power(previous.get(k)) not in (None, 0)
    for k in ("1m", "5m", "20m", "60m")
    )

    delta = _compute_delta_percent(current, previous, context) if has_previous else None

    glycolytic_bias = _safe_ratio(
        _power(current.get("1m")),
        _power(current.get("20m"))
    )

    aerobic_durability = _safe_ratio(
        _power(current.get("60m")),
        _power(current.get("5m"))
    )

    # durability gradient (long-duration sustainability)
    durability_gradient = _safe_ratio(
        _power(current.get("60m")),
        _power(current.get("20m"))
    )

    system_status = (
        _classify_system_status(sport, delta)
        if delta
        else {k: "baseline" for k in ["anaerobic", "vo2", "threshold", "aerobic_durability"]}
    )
    system_timeline = (
        _build_system_timeline(system_status)
        if delta
        else {k: "baseline" for k in system_status.keys()}
    )

    plateau = _detect_plateau(sport, delta, context) if delta else False

    balance_score = _compute_balance_score(glycolytic_bias, aerobic_durability)

    # regression diagnostics
    regression = data.get("curve_regression", {})
    curve_slope = regression.get("slope") or data.get("curve_slope")
    curve_r2 = regression.get("r2") or data.get("curve_fit_r2")

    if curve_r2 is not None:
        curve_r2 = float(curve_r2)

    curve_quality = _classify_curve_quality(curve_r2)
    model_quality = curve_quality

    # FFT_CURVES model
    models = data.get("models", {})
    cp = models.get("cp")
    w_prime = models.get("w_prime")
    pmax = models.get("pmax")
    ftp = models.get("ftp")

    # ---- ESPE v1 derived power metrics ----
    p5m = _power(current.get("5m"))

    pdr_5m = None
    vo2_reserve_ratio = None

    if cp is not None and p5m is not None and cp != 0:
        pdr_5m = round(p5m - cp, 2)
        vo2_reserve_ratio = round(p5m / cp, 3)

    curve_profile = (
        _classify_curve_profile(sport, curve_slope)
        if curve_slope is not None
        else "unknown"
    )

    adaptation_bias = (
        _derive_adaptation_bias(system_status)
        if delta
        else "baseline"
    )
    adaptation_state = (
        classify_adaptation_state(system_status, delta)
        if delta
        else "baseline"
    )

    curve_dynamics = _compute_curve_dynamics(delta or {})

    # Optional fatigued power-curve extension.
    # Returns None for Run or when no usable fatigued curves exist.
    fatigue_resistance = _build_fatigue_resistance(
        sport=sport,
        data=data,
        current=current,
        context=context,
    )

    # ---- curve window definition ----
    window = data.get(
        "window_days",
        CHEAT_SHEET["thresholds"]["ESPE"]["curve_windows"]["default_days"]
    ) or CHEAT_SHEET["thresholds"]["ESPE"]["curve_windows"]["default_days"]
    anchors_context = {
        "window_days": window,
        "description": f"Best power values recorded within the last {window} days"
    }

    if has_previous:
        curve_window = {
            "current_days": window,
            "previous_days": window,
            "comparison": f"{window}d_vs_{window}d",
            "anchor": "report_end",
            "curve_source": "FFT_CURVES"
        }
    else:
        curve_window = {
            "current_days": window,
            "previous_days": None,
            "comparison": f"{window}d_baseline",
            "anchor": "report_end",
            "curve_source": "FFT_CURVES"
        }

    # ---- derived metrics block ----
    markers = COACH_PROFILE.get("markers", {})
    window_label = curve_window["comparison"]

    derived_metrics = {}

    def _metric(name, value):
        meta = markers.get(name, {})
        return {
            "name": name,
            "value": value,
            "framework": meta.get("framework"),
            "interpretation": meta.get("interpretation"),
            "coaching_implication": meta.get("coaching_implication"),
            "related_metrics": {},
            "context_window": window_label,
        }

    if glycolytic_bias is not None:
        derived_metrics["glycolytic_bias_ratio"] = _metric(
            "glycolytic_bias_ratio", round(glycolytic_bias, 3)
        )

    if aerobic_durability is not None:
        derived_metrics["aerobic_durability_ratio"] = _metric(
            "aerobic_durability_ratio", round(aerobic_durability, 3)
        )

    if durability_gradient is not None:
        derived_metrics["durability_gradient"] = _metric(
            "durability_gradient", round(durability_gradient, 3)
        )

    if balance_score is not None:
        derived_metrics["system_balance_score"] = _metric(
            "system_balance_score", round(balance_score, 3)
        )

    if pdr_5m is not None:
        derived_metrics["pdr_5m"] = _metric("pdr_5m", pdr_5m)

    if vo2_reserve_ratio is not None:
        derived_metrics["vo2_reserve_ratio"] = _metric(
            "vo2_reserve_ratio", vo2_reserve_ratio
        )

    debug(
        context,
        f"[ESPE] {sport} bias={adaptation_bias} balance={balance_score}"
    )

    system_guidance = None

    if adaptation_state == "aerobic_consolidation":

        if system_status.get("vo2") == "decline":
            system_guidance = (
            "Aerobic development is progressing, but VO₂ capacity is slipping slightly — reintroduce VO₂ stimulus in the next microcycle."
            )

    elif adaptation_state == "vo2_expansion":

        system_guidance = (
            "VO₂ capacity is improving — support it with threshold work to consolidate gains."
        )

    elif adaptation_state == "anaerobic_build":

        system_guidance = (
            "Anaerobic power is improving — keep short, high-intensity efforts in the mix."
        )

    elif adaptation_state == "mixed_adaptation":

        system_guidance = (
            "Mixed adaptation pattern detected — sprint power has improved, "
            "but anaerobic repeatability and long-duration durability have declined. "
            "Rebalance training with sustained VO₂ and aerobic durability work."
        )

    elif adaptation_state == "vo2_threshold_decline":

        system_guidance = (
            "VO₂ and threshold power are both lower than in the preceding "
            "power-curve comparison window. This indicates reduced recent "
            "high-aerobic performance, but does not by itself confirm fatigue. "
            "Interpret alongside recent training exposure, recovery and wellness."
        )

    elif adaptation_state == "plateau":

        system_guidance = (
            "Power curve is stable across systems — a new stimulus may be needed to restart progression."
        )

    sport_result = {
        "supported": True,

        "curve_window": curve_window,

        "power_curve_anchors": {
            "context": anchors_context,
            "values": anchors
        },

        "delta_percent": delta,

        "curve_dynamics": curve_dynamics,

        "system_status": system_status,
        "system_status_timeline": system_timeline,

        "derived_metrics": derived_metrics,

        "curve_regression": {
            "model": "power_duration_log_regression",
            "slope": curve_slope,
            "r2": curve_r2
        },

        "curve_quality": curve_quality,

        "power_model": {
            "source": "FFT_CURVES",
            "model_quality": model_quality,
            "cp": cp,
            "w_prime": w_prime,
            "pmax": pmax,
            "ftp": ftp
        },

        "plateau_detected": plateau,

        "adaptation_bias": adaptation_bias,
        "adaptation_state": adaptation_state,

        "curve_profile": curve_profile,
        "system_guidance": system_guidance
    }

    if fatigue_resistance is not None:
        sport_result["fatigue_resistance"] = fatigue_resistance

    return sport_result


def _compute_curve_dynamics(delta: Dict[str, float]) -> Dict[str, Any]:

    vals = {
        "short": delta.get("1m"),
        "vo2": delta.get("5m"),
        "thr": delta.get("20m"),
        "long": delta.get("60m"),
    }

    valid = [v for v in vals.values() if v is not None]

    # --- no usable data ---
    if not valid:
        return {
            "vertical_shift_pct": None,
            "rotation_index": None,
            "dominant_shift": "unknown"
        }

    # --- safe numeric fallback for partial data ---
    short = vals["short"] if vals["short"] is not None else 0
    vo2 = vals["vo2"] if vals["vo2"] is not None else 0
    thr = vals["thr"] if vals["thr"] is not None else 0
    long = vals["long"] if vals["long"] is not None else 0

    count = len(valid)

    # --- average shift using only valid signals ---
    vertical_shift = round(sum(valid) / count, 2)

    # --- rotation index (still comparable even with partial data) ---
    rotation_index = round(((short + vo2) / 2) - ((thr + long) / 2), 2)

    # --- classification ---
    if abs(rotation_index) < 0.75:
        dominant = "uniform_shift"
    elif rotation_index > 0:
        dominant = "anaerobic_rotation"
    else:
        dominant = "aerobic_rotation"

    return {
        "vertical_shift_pct": vertical_shift,
        "rotation_index": rotation_index,
        "dominant_shift": dominant
    }

# ---------------------------------------------------------------------
# Calculations
# ---------------------------------------------------------------------

def _compute_delta_percent(
    current: Dict[str, Any],
    previous: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, float]:

    delta = {}

    for k in current:

        cur = _power(current.get(k))
        prev = _power(previous.get(k))

        if cur is None or prev is None or prev <= 0:
            continue

        d = round(((cur - prev) / prev) * 100, 2)

        delta[k] = d
        debug(context, f"[ESPE] delta {k} = {d}%")

    return delta


def _safe_ratio(a: float, b: float) -> float:
    if a is None or b is None or b == 0:
        return None
    return round(a / b, 2)


# ---------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------

def _classify_system_status(
    sport: str,
    delta: Dict[str, float]
) -> Dict[str, str]:

    thresholds = _sport_thresholds(sport)

    return {
        "anaerobic": _band(delta.get("1m"), thresholds["anaerobic"]),
        "vo2": _band(delta.get("5m"), thresholds["vo2"]),
        "threshold": _band(delta.get("20m"), thresholds["threshold"]),
        "aerobic_durability": _band(delta.get("60m"), thresholds["aerobic"])
    }


def _band(value: float, bands: Dict[str, float]) -> str:

    if value is None:
        return "unknown"

    neutral_band = (
        CHEAT_SHEET
        .get("thresholds", {})
        .get("ESPE", {})
        .get("neutral_band", 0.75)
    )

    if abs(value) < neutral_band:
        return "stable"

    strong = bands.get("strong")
    moderate = bands.get("moderate")
    mild = bands.get("mild")
    decline = bands.get("decline")

    # --- gains (ordered safely) ---
    if strong is not None and value >= strong:
        return "strong_gain"

    if moderate is not None and value >= moderate:
        return "moderate_gain"

    if mild is not None and value >= mild:
        return "mild_gain"

    # --- decline ---
    if decline is not None and value <= decline:
        return "decline"

    return "stable"

def _sport_thresholds(sport: str) -> Dict[str, Dict[str, float]]:

    espe = (
        CHEAT_SHEET
        .get("thresholds", {})
        .get("ESPE", {})
    )

    if sport in espe:
        return espe[sport]

    return espe.get("Ride", {})


# ---------------------------------------------------------------------
# Derived Metrics
# ---------------------------------------------------------------------

def _detect_plateau(
    sport: str,
    delta: Dict[str, float],
    context: Dict[str, Any]
) -> bool:

    threshold_gain = delta.get("20m")
    if threshold_gain is None:
        return False

    debug(context, f"[ESPE] plateau check {sport} threshold_delta={threshold_gain}")

    if sport == "Run":
        return threshold_gain < 0.5

    vals = [delta.get(k) for k in ("1m", "5m", "20m", "60m") if delta.get(k) is not None]

    if not vals:
        return False

    return all(abs(v) < 1.0 for v in vals)


def _compute_balance_score(
    glycolytic: float,
    aerobic: float
) -> float:

    ideal = 1.8

    if glycolytic is None:
        return None

    if glycolytic == 0:
        return 0.0

    deviation = abs(glycolytic - ideal) / ideal
    score = max(0.0, 1 - deviation)

    return round(score, 2)


def _derive_adaptation_bias(system_status: Dict[str, str]) -> str:

    if system_status["vo2"] in ("strong_gain", "moderate_gain"):
        return "vo2_dominant"

    if system_status["threshold"] in ("strong_gain", "moderate_gain"):
        return "threshold_dominant"

    return "balanced"

def _classify_curve_profile(sport: str, slope: float) -> str:

    if slope is None:
        return "unknown"

    espe = (
        CHEAT_SHEET
        .get("thresholds", {})
        .get("ESPE", {})
    )

    # -----------------------------
    # Running classification
    # -----------------------------
    if sport == "Run":

        if slope >= espe["run_curve_slope_endurance_runner"]:
            return "endurance_runner"

        if slope >= espe["run_curve_slope_balanced_runner"]:
            return "balanced_runner"

        if slope >= espe["run_curve_slope_punchy_runner"]:
            return "punchy_runner"

        return "speed_runner"

    # -----------------------------
    # Cycling classification
    # -----------------------------

    if slope >= espe["curve_slope_time_trialist"]:
        return "time_trialist"

    if slope >= espe["curve_slope_endurance_specialist"]:
        return "endurance_specialist"

    if slope >= espe["curve_slope_all_rounder"]:
        return "all_rounder"

    if slope >= espe["curve_slope_punchy_climber"]:
        return "punchy_climber"

    if slope >= espe["curve_slope_punchy"]:
        return "punchy"

    if slope >= espe["curve_slope_anaerobic_specialist"]:
        return "anaerobic_specialist"

    return "sprinter"

def classify_adaptation_state(system_status, deltas):

    thr = deltas.get("20m")
    dur = deltas.get("60m")
    vo2 = deltas.get("5m")
    neu = deltas.get("5s")
    ana_1m = deltas.get("1m")

    # concurrent VO2 + threshold decline
    if thr is not None and vo2 is not None and thr < -3 and vo2 < -3:
        return "vo2_threshold_decline"

    # vo2
    if vo2 is not None and vo2 > 3:
        return "vo2_expansion"

    # aerobic
    if thr is not None and dur is not None and thr > 1 and dur > 2:
        return "aerobic_consolidation"

    # mixed adaptation
    # sprint freshness but declining anaerobic repeatability
    if (
        neu is not None and neu > 5 and
        ana_1m is not None and ana_1m < -3
    ):
        return "mixed_adaptation"

    # anaerobic build
    # require both sprint + sustained anaerobic progression
    if (
        neu is not None and neu > 5 and
        ana_1m is not None and ana_1m > 2
    ):
        return "anaerobic_build"

    # plateau
    vals = [v for v in deltas.values() if v is not None]

    if vals and all(abs(v) < 1 for v in vals):
        return "plateau"

    return "mixed_adaptation"

def _classify_curve_quality(r2: float):

    espe = (
        CHEAT_SHEET
        .get("thresholds", {})
        .get("ESPE", {})
    )

    q = espe.get("curve_quality", {})

    if r2 is None:
        return "unknown"

    if r2 >= q.get("excellent", 0.85):
        return "excellent"

    if r2 >= q.get("good", 0.75):
        return "good"

    return "low_confidence"

def _build_system_timeline(system_status: Dict[str, str]):

    mapping = (
        CHEAT_SHEET
        .get("thresholds", {})
        .get("ESPE", {})
        .get("system_timeline_map", {})
    )

    timeline = {}

    for system, state in system_status.items():
        timeline[system] = mapping.get(state, "unknown")

    return timeline

# ---------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------

def _valid_curve_block(
    data: Dict[str, Any],
    context: Dict[str, Any],
    sport: str
) -> bool:

    if "current" not in data or "previous" not in data:
        debug(context, f"[ESPE] missing curve block for {sport}")
        return False

    if sport == "Run":
        required = ["5m", "20m"]
    else:
        required = ["1m", "5m", "20m", "60m"]

    current = data.get("current", {})
    previous = data.get("previous", {})

    for k in required:

        cur = _power(current.get(k))
        prev = _power(previous.get(k))

        if cur is None or cur <= 0:
            debug(context, f"[ESPE] missing anchor {k} for {sport}")
            return False

    return True


# ---------------------------------------------------------------------
# Unsupported
# ---------------------------------------------------------------------

def _unsupported(reason: str) -> Dict[str, Any]:

    return {
        "supported": False,
        "reason": reason
    }
