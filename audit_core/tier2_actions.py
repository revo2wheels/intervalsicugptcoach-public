"""
Tier-2 Step 7 — Evaluate Actions (v16)
Generates adaptive coaching actions and triggers renderer gate.
"""

def evaluate_actions(context, auditFinal=True, reportType="weekly"):
    actions = []

    if context.get("Polarisation", 0) >= 0.7:
        actions.append("✅ Maintain ≥70 % Z1–Z2 volume (Seiler 80/20).")
    else:
        actions.append("⚠ Increase Z1–Z2 share to ≥70 % (Seiler 80/20).")

    if context.get("FatOxidation", 0) >= 0.8 and context.get("Decoupling", 1) <= 0.05:
        actions.append("✅ Metabolic efficiency maintained (San Millán Zone 2).")
    else:
        actions.append("⚠ Improve Zone 2 efficiency: extend duration or adjust IF.")

    if context.get("RecoveryIndex", 1) < 0.6:
        if context.get("ACWR", 1) > 1.2:
            actions.append("⚠ Apply 30–40 % deload (Friel microcycle logic).")
        else:
            actions.append("⚠ Apply 10–15 % deload (Friel microcycle logic).")

    if context.get("weeks_since_last_FTP", 0) >= 6:
        actions.append("🔄 Retest FTP/LT1 for updated benchmarks.")

    if abs(context.get("FatMaxDeviation", 1)) <= 0.05 and context.get("Decoupling", 1) <= 0.05:
        actions.append("✅ FatMax calibration verified (± 5 %).")

    context["actions"] = actions

    # --- Renderer Gate ---
    if auditFinal:
        render_template(reportType, framework="Unified_Reporting_Framework_v5.1", context=context)
    else:
        halt("audit❌ Renderer blocked until auditFinal=True")

    return context
