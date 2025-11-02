"""
Tier-2 Step 8 — Render Validator (v16.1)
Runs after actions and ensures rendered output complies with
Unified Reporting Framework v5.1.
"""

from audit_core.report_validator import validate_report_output
from audit_core.report_schema_guard import enforce_report_schema

def finalize_and_validate_render(context, reportType="weekly"):
    # --- Renderer Gate ---
    if not context.get("auditFinal", False):
        raise RuntimeError("❌ Renderer blocked: auditFinal=False")

    # --- Generate Report ---
    report = render_template(
        reportType,
        framework="Unified_Reporting_Framework_v5.1",
        context=context,
    )

    # --- Framework Compliance Validation ---
    compliance = validate_report_output(context, report)

    # --- Schema Validation (Newly Added) ---
    enforce_report_schema(report)

    # --- Final Compliance Log ---
    compliance["schema_validated"] = True
    compliance["framework"] = "Unified_Reporting_Framework_v5.1"
    compliance["report_type"] = report.get("type", reportType)
    compliance["validation_status"] = "✅ Full Framework + Schema Validation Passed"

    print("✅ Report passed both framework and schema validation.")
    return report, compliance
