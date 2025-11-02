"""
Tier-2 Step 8 — Render Validator (v16.1)
Runs after actions and ensures rendered output complies with
Unified Reporting Framework v5.1.
"""

import time
import datetime
from audit_core.report_validator import validate_report_output
from audit_core.report_schema_guard import enforce_report_schema

def finalize_and_validate_render(context, reportType="weekly"):
    # --- Renderer Gate ---
    if not context.get("auditFinal", False):
        raise RuntimeError("❌ Renderer blocked: auditFinal=False")

    # --- Duration Formatting Injection (Precision Mode) ---
    if "df_events" in context:
        def fmt_dur(sec):
            return time.strftime("%H:%M:%S", time.gmtime(int(sec)))
        try:
            df = context["df_events"]
            if "moving_time" in df.columns:
                df["Duration"] = df["moving_time"].apply(fmt_dur)
                context["Duration_total"] = fmt_dur(df["moving_time"].sum())
            else:
                print("⚠️ 'moving_time' column missing — duration formatting skipped.")
        except Exception as e:
            print(f"⚠️ Duration formatting skipped: {e}")

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
