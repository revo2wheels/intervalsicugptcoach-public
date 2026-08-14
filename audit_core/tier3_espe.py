"""
Energy System Progression Engine (ESPE)
Version: v1.21

Stateless engine comparing two rolling power-curve windows to track energy system progression.

Consumes:
    power_curve block injected by Worker

Produces:
    energy_system_progression section

v1.2 factored for baseline where no previous exists
"""

from typing import Dict, Any

from coaching_cheat_sheet import CHEAT_SHEET
from audit_core.utils import debug
from coaching_profile import COACH_PROFILE

ESPE_VERSION = "espe_v1.21"

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

    return {
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