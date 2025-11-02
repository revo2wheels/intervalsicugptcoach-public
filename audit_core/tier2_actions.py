"""
Tier-2 Step 4 — Evaluate Coaching Actions (v16.1)
Applies heuristics to validated derived metrics and outputs recommendations.
"""

def evaluate_actions(context):
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

    # --- Final status ---
    context["actions"] = actions
    return context
