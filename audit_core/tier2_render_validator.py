"""
Tier-2 Step 8 — Render Validator (v16.1-EOD-002)
Runs after actions and ensures rendered output complies with
Unified Reporting Framework v5.1.
Event-only totals enforcement active.
"""

import time
import datetime
from audit_core.report_validator import validate_report_output
from audit_core.report_schema_guard import enforce_report_schema
from audit_core.errors import AuditHalt

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

    # --- Step 1: Enforce event-only totals ---
    # Prefer Tier-2 validated totals, fallback to Tier-1 eventTotals
    total_hours = (
        context.get("totalHours")
        or (context.get("eventTotals", {}).get("hours"))
    )
    total_tss = (
        context.get("totalTss")
        or (context.get("eventTotals", {}).get("tss"))
    )

    # Purge legacy or derived data
    context.pop("dailyTotals", None)

    if total_hours is None or total_tss is None:
        raise AuditHalt("❌ Missing event-only totals for renderer input")

    # Inject final clean values
    context["totalHours"] = round(float(total_hours), 2)
    context["totalTss"] = int(round(float(total_tss)))

    # --- Step 2: Generate Report ---
    report = render_template(
        reportType,
        framework="Unified_Reporting_Framework_v5.1",
        context=context,
    )

    # --- Step 3: Framework Compliance Validation ---
    compliance = validate_report_output(context, report)

    # --- Step 4: Schema Validation ---
    enforce_report_schema(report)

    # --- Step 5: Cross-check consistency ---
    diff_hours = abs(context["totalHours"] - context.get("eventTotals", {}).get("hours", 0))
    diff_tss = abs(context["totalTss"] - context.get("eventTotals", {}).get("tss", 0))
    if diff_hours > 0.1 or diff_tss > 2:
        raise AuditHalt(f"❌ Renderer mismatch Δh={diff_hours:.2f}, ΔTSS={diff_tss:.1f}")

    # --- Step 6: Final Compliance Log ---
    compliance["schema_validated"] = True
    compliance["framework"] = "Unified_Reporting_Framework_v5.1"
    compliance["report_type"] = report.get("type", reportType)
    compliance["validation_status"] = "✅ Full Framework + Schema Validation Passed"

    print("✅ Report passed both framework and schema validation (event-only mode).")
    return report, compliance
