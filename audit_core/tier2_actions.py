"""
Tier-2 Step 3.5 — Detect Phases (legacy-compatible, reinstated v16.1.1)
Infers phase segments from validated event-level load data.
Derived directly from legacy v15.4 inline logic.
"""

from datetime import datetime, timedelta

def detect_phases(context, events):
    # --- Extract event dates and loads ---
    loads = [(e["start_date"], e["icu_training_load"]) for e in events if "icu_training_load" in e]
    loads.sort(key=lambda x: x[0])
    if not loads:
        context["phases"] = [{"phase": "No Data", "start": None, "end": None, "delta": 0.0}]
        return context

    # --- Compute 7-day rolling TSS average ---
    avg7 = []
    for i in range(len(loads)):
        current_date = datetime.fromisoformat(loads[i][0].replace("Z", "+00:00"))
        window = [
            v for d, v in loads
            if 0 <= (current_date - datetime.fromisoformat(d.replace("Z", "+00:00"))).days <= 7
        ]
        avg7.append(sum(window) / len(window))

    # --- Detect inflection points (>±15 % change) ---
    phases = []
    start_idx = 0
    for i in range(1, len(avg7)):
        prev = avg7[i-1]
        delta = (avg7[i] - prev) / max(prev, 1)
        if abs(delta) > 0.15:
            label = "Build" if delta > 0 else "Deload"
            phases.append({
                "phase": label,
                "start": loads[start_idx][0],
                "end": loads[i][0],
                "delta": round(delta, 2)
            })
            start_idx = i

    # --- Fallback if no detectable phase transitions ---
    if not phases:
        phases.append({
            "phase": "Continuous Load",
            "start": loads[0][0],
            "end": loads[-1][0],
            "delta": 0.0
        })

    context["phases"] = phases
    return context


"""
Tier-2 Step 4 — Evaluate Coaching Actions (v16.1.1)
Applies heuristics to validated derived metrics, outputs recommendations.
Now includes automatic phase detection from event-level data.
"""

def evaluate_actions(context):
    events = context.get("events", [])
    context = detect_phases(context, events)

    actions = []

    # --- Polarisation / Intensity Balance ---
    if context.get("Polarisation", 0.0) >= 0.7:
        actions.append("✅ Maintain ≥70 % Z1–Z2 volume (Seiler 80/20).")
    else:
        actions.append("⚠ Increase Z1–Z2 share to ≥70 % (Seiler 80/20).")

    # --- Metabolic Efficiency ---
    if context.get("FatOxidation", 0.0) >= 0.8 and context.get("Decoupling", 1.0) <= 0.05:
        actions.append("✅ Metabolic efficiency maintained (San Millán Zone 2).")
    else:
        actions.append("⚠ Improve Zone 2 efficiency: extend duration or adjust IF.")

    # --- Recovery and Load Balance ---
    if context.get("RecoveryIndex", 1.0) < 0.6:
        if context.get("ACWR", 1.0) > 1.2:
            actions.append("⚠ Apply 30–40 % deload (Friel microcycle logic).")
        else:
            actions.append("⚠ Apply 10–15 % deload (Friel microcycle logic).")

    # --- Benchmark Maintenance ---
    if context.get("weeks_since_last_FTP", 0) >= 6:
        actions.append("🔄 Retest FTP/LT1 for updated benchmarks.")

    # --- FatMax Verification ---
    if abs(context.get("FatMaxDeviation", 1.0)) <= 0.05 and context.get("Decoupling", 1.0) <= 0.05:
        actions.append("✅ FatMax calibration verified (±5 %).")

    # --- Visual Fatigue Flag (v16.1.3 legacy cosmetic) ---
    ri = context.get("RecoveryIndex", 1.0)
    if ri < 0.6:
        context["ui_flag"] = "🔴 Overreached"
    elif ri < 0.8:
        context["ui_flag"] = "🟠 Fatigued"
    else:
        context["ui_flag"] = "🟢 Normal"

    # --- Final status ---
    context["actions"] = actions
    return context