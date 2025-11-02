"""
Tier-2 Step 8 — Render Validator (v16.1)
Runs after actions and ensures rendered output complies with
Unified Reporting Framework v5.1.
"""

from audit_core.report_validator import validate_report_output
from audit_core.tier2_actions import evaluate_actions

def finalize_and_validate_render(context, reportType="weekly"):
    # --- Ensure audit completion ---
    if not context.get("auditFinal", False):
        raise RuntimeError("❌ Renderer blocked: auditFinal=False")

    # --- Generate report through framework ---
    report = render_template(
        reportType,
        framework="Unified_Reporting_Framework_v5.1",
        context=context,
    )

    # --- Validate report structure and framework compliance ---
    compliance = validate_report_output(context, report)

    return report, compliance
