"""
Tier-2 Step 8 — Render Validator (v16.1.4-EOD-005)
Strict event-only enforcement.
Removes legacy load-weighted duration fallback.
"""

import time
from audit_core.errors import AuditHalt
from audit_core.report_validator import validate_report_output
from audit_core.report_schema_guard import enforce_report_schema
from audit_core.tier2_enforce_event_only_totals import enforce_event_only_totals

def finalize_and_validate_render(context, reportType="weekly"):
    # --- Renderer Gate ---
    if not context.get("auditFinal", False):
        raise RuntimeError("❌ Renderer blocked: auditFinal=False")

    # --- Athlete Profile Check ---
    if "athleteProfile" not in context or not context["athleteProfile"]:
        raise AuditHalt("❌ Missing athleteProfile — Section 1 cannot render")

    # --- Refresh Event-Only Totals ---
    try:
        df = context.get("df_events")
        if df is None:
            raise AuditHalt("❌ Missing df_events for totals enforcement")
        context = enforce_event_only_totals(df, context)
    except Exception as e:
        raise AuditHalt(f"❌ Event-only totals enforcement failed before render: {e}")


    # --- Duration Formatting Injection ---
    if "df_events" in context:
        def fmt_dur(sec):
            return time.strftime("%H:%M:%S", time.gmtime(int(sec)))
        df = context["df_events"]
        if "moving_time" in df.columns:
            df["Duration"] = df["moving_time"].apply(fmt_dur)
            context["Duration_total"] = fmt_dur(df["moving_time"].sum())

    # --- Step 1 : Enforce and Clean Totals ---
    total_hours = context.get("totalHours")
    total_tss = context.get("totalTss")
    context.pop("dailyTotals", None)

    # --- STRICT: no fallback or normalization ---
    if total_hours is None or total_tss is None:
        raise AuditHalt("❌ Missing event-only totals for renderer input (Σ event.moving_time / 3600)")

    context["totalHours"] = round(float(total_hours), 2)
    context["totalTss"] = int(round(float(total_tss)))

    # --- Icon Pack Injection ---
    from ui_components.cards.icon_pack import ICON_CARDS, render_icon_legend
    context["icon_pack"] = ICON_CARDS
    context["force_icon_pack"] = True
    context["icon_legend"] = render_icon_legend()

    # --- Step 2 : Generate Report ---
    report = render_template(
        reportType,
        framework="Unified_Reporting_Framework_v5.1",
        context=context,
    )

    # --- Step 3 : Framework Compliance Validation ---
    compliance = validate_report_output(context, report)

    # --- Step 4 : Schema Validation ---
    enforce_report_schema(report)

    # --- Step 5 : Cross-check Consistency ---
    diff_hours = abs(context["totalHours"] - context.get("eventTotals", {}).get("hours", 0))
    diff_tss = abs(context["totalTss"] - context.get("eventTotals", {}).get("tss", 0))
    if diff_hours > 0.1 or diff_tss > 2:
        raise AuditHalt(f"❌ Renderer mismatch Δh={diff_hours:.2f}, ΔTSS={diff_tss:.1f}")

    # --- Step 6 : Finalize Compliance Log ---
    compliance.update({
        "schema_validated": True,
        "framework": "Unified_Reporting_Framework_v5.1",
        "report_type": report.get("type", reportType),
        "validation_status": "✅ Full Framework + Schema Validation Passed",
    })

    print("✅ Report passed both framework and schema validation (event-only mode).")
    return report, compliance
