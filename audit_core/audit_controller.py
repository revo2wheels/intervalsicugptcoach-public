# audit_core/report_controller.py
from api_github_com__jit_plugin import loadAllRules
from audit_core.tier0_pre_audit import run_tier0_pre_audit
from audit_core.tier1_controller import run_tier1_controller
from audit_core.tier2_data_integrity import validate_data_integrity
from audit_core.tier2_event_completeness import validate_event_completeness
from audit_core.tier2_enforce_event_only_totals import enforce_event_only_totals
from audit_core.tier2_calc_integrity import validate_calculation_integrity
from audit_core.tier2_wellness_validation import validate_wellness
from audit_core.tier2_derived_metrics import compute_derived_metrics
from audit_core.tier2_actions import evaluate_actions
from audit_core.tier2_render_validator import finalize_and_validate_render


def run_report(user_cmd: str):
    """Unified entry for any report type (season, block, weekly, custom)."""
    # Tier-0 — Ruleset and pre-audit
    loadAllRules()
    context = {}
    df_activities, wellness, context, auditPartial, auditFinal = run_tier0_pre_audit(user_cmd, context)

    # Tier-1 — Dataset validation
    context = run_tier1_controller(df_activities, wellness, context)

    # Tier-2 — Full audit chain
    validate_data_integrity(df_activities, wellness, context)
    validate_event_completeness(df_activities, context)
    enforce_event_only_totals(df_activities, context)
    validate_calculation_integrity(df_activities, context)
    validate_wellness(wellness, context)
    compute_derived_metrics(df_activities, wellness, context)
    evaluate_actions(context)
    finalize_and_validate_render(context)

    return context


if __name__ == "__main__":
    # Example run
    run_report("season report")
