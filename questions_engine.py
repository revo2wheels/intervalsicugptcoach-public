# questions_engine.py
##
"""
Montis Coaching Question Engine
"""

from question_bank import QUESTION_BANK, SIGNAL_MAP, QUESTION_TEMPLATES


# ---------------------------------------------------------
# Question Selection
# ---------------------------------------------------------

def select_question(report, signals):

    if not signals:
        return None

    signals_sorted = sorted(signals, key=lambda x: x[1], reverse=True)

    primary_sig, severity = signals_sorted[0]

    secondary_sig = None
    if len(signals_sorted) > 1:
        secondary_sig = signals_sorted[1][0]

    category = SIGNAL_MAP.get(primary_sig)

    if not category:
        return None

    questions = QUESTION_BANK.get(category)

    if not questions:
        return None

    aligned = [q for q in questions if primary_sig in q["signals"]]

    if not aligned:
        return None

    aligned = sorted(aligned, key=lambda q: q["priority"])

    idx = min(severity - 1, len(aligned) - 1)

    question = aligned[idx]["question"]

    if secondary_sig and secondary_sig in SIGNAL_MAP:

        label = SIGNAL_MAP[secondary_sig]

        if "given the current" not in question:
            question = f"{question} given the current {label}"

    return question


# ---------------------------------------------------------
# Signal Detection
# ---------------------------------------------------------

def detect_signals(report):

    signals = []

    pi_root = report.get("performance_intelligence", {})
    acute = pi_root.get("acute", {})
    chronic = pi_root.get("chronic", {})

    espe = report.get("energy_system_progression", {})
    metrics = report.get("metrics", {})

    # -----------------------------
    # Durability (acute)
    # -----------------------------
    dec = acute.get("durability", {}).get("mean_decoupling_7d")

    if isinstance(dec, dict):
        dec = dec.get("value")

    if dec is not None:

        if dec >= 8:
            signals.append(("durability_decline", 3))

        elif dec >= 5:
            signals.append(("durability_pressure", 2))


    # -----------------------------
    # Durability trend (chronic)
    # -----------------------------
    chronic_dec = chronic.get("durability", {}).get("mean_decoupling_90d")

    if isinstance(chronic_dec, dict):
        chronic_dec = chronic_dec.get("value")

    if chronic_dec is not None:

        if chronic_dec >= 6:
            signals.append(("durability_trend_decline", 2))

        elif chronic_dec <= 3:
            signals.append(("durability_trend_improving", 1))


    # -----------------------------
    # Anaerobic Repeatability
    # -----------------------------
    dep = acute.get("anaerobic_repeatability", {}).get("mean_depletion_pct_7d")

    if isinstance(dep, dict):
        dep = dep.get("value")

    if dep is not None:

        if dep >= 0.60:
            signals.append(("anaerobic_depletion", 3))

        elif dep >= 0.40:
            signals.append(("anaerobic_load", 2))


    # -----------------------------
    # Neural Density
    # -----------------------------
    hi_days = acute.get("neural_density", {}).get("high_intensity_days_7d")

    if isinstance(hi_days, dict):
        hi_days = hi_days.get("value")

    if hi_days is not None:

        if hi_days >= 4:
            signals.append(("intensity_clustering", 3))

        elif hi_days == 3:
            signals.append(("high_intensity_density", 2))


    # -----------------------------
    # Load / Fatigue Metrics
    # -----------------------------
    fatigue = metrics.get("FatigueTrend")
    stress = metrics.get("StressTolerance")

    if isinstance(fatigue, dict):
        fatigue = fatigue.get("value")

    if isinstance(stress, dict):
        stress = stress.get("value")

    if fatigue is not None:

        if fatigue >= 15:
            signals.append(("fatigue_accumulation", 3))

        elif fatigue >= 10:
            signals.append(("fatigue_accumulation", 2))

    if stress is not None:

        if stress >= 1.5:
            signals.append(("load_pressure", 3))

        elif stress >= 1.3:
            signals.append(("load_pressure", 2))


    # -----------------------------
    # ESPE Adaptation Signals
    # -----------------------------
    sports = espe.get("sports", {})

    for sport, system in sports.items():

        if not isinstance(system, dict):
            continue

        state = system.get("adaptation_state")

        if state == "vo2_threshold_decline":
            signals.append(("system_decline", 3))

        elif state in ("vo2_expansion", "anaerobic_build"):
            signals.append(("system_progression", 2))

        elif state == "mixed_adaptation":
            signals.append(("adaptation_fragile", 2))

        elif state == "plateau":
            signals.append(("adaptation_stable", 1))


    return signals


# ---------------------------------------------------------
# Dominant Signal
# ---------------------------------------------------------

def dominant_signal(signals):

    if not signals:
        return None

    signals_sorted = sorted(signals, key=lambda x: x[1], reverse=True)

    return signals_sorted[0][0]


# ---------------------------------------------------------
# Question Generation
# ---------------------------------------------------------

def generate_question(report, signals):

    if not signals:
        return None

    signals_sorted = sorted(signals, key=lambda x: x[1], reverse=True)

    primary = signals_sorted[0][0]

    secondary = None
    if len(signals_sorted) > 1:
        secondary = signals_sorted[1][0]

    key = primary

    if secondary:

        combo_key = f"{primary}+{secondary}"

        if combo_key in QUESTION_TEMPLATES:
            key = combo_key

    template_obj = QUESTION_TEMPLATES.get(key)

    if not template_obj:
        return None

    variants = template_obj.get("question_variants")

    if not variants:
        return None

    period = report.get("meta", {}).get("period", "")

    idx = abs(hash(period + key)) % len(variants)

    question = variants[idx]

    if "{secondary}" in question and secondary:

        label = SIGNAL_MAP.get(secondary, secondary)

        question = question.format(secondary=label)

    return question