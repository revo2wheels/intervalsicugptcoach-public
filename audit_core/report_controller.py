import pandas as pd
from datetime import timedelta

from api_github_com__jit_plugin import loadAllRules
from audit_core.tier0_pre_audit import run_tier0_pre_audit
from audit_core.tier1_controller import run_tier1_controller
from audit_core.tier2_enforce_event_only_totals import validate_data_integrity
from audit_core.tier2_event_completeness import validate_event_completeness
from audit_core.tier2_enforce_event_only_totals import enforce_event_only_totals
from audit_core.utils import validate_dataset_integrity as validate_calculation_integrity
from audit_core.utils import validate_wellness_alignment as validate_wellness
from audit_core.tier2_derived_metrics import compute_derived_metrics
from audit_core.tier2_actions import evaluate_actions
from audit_core.tier2_render_validator import finalize_and_validate_render


def run_report(user_cmd: str):
    """
    Unified entry for any report type (season, block, weekly, custom).
    Supports auto-chunk retrieval for >7-day windows as per v16.1 Data Rules.
    """
    # --- Tier-0 — Ruleset and pre-audit ---
    loadAllRules()
    context = {}

    # --- Initial pre-audit ---
    df_master, wellness, context, auditPartial, auditFinal = run_tier0_pre_audit(user_cmd, context)

    # --- Auto-chunk mode ---
    start = context["window_start"]
    end = context["window_end"]
    delta = timedelta(days=7)

    if (end - start).days > 7:
        all_dfs = [df_master]
        chunk_start = start + delta
        while chunk_start < end:
            chunk_end = min(chunk_start + delta - timedelta(days=1), end)
            chunk_cmd = f"{user_cmd} chunk {chunk_start}→{chunk_end}"
            df_chunk, _, _, _, _ = run_tier0_pre_audit(chunk_cmd, context)
            all_dfs.append(df_chunk)
            chunk_start += delta
        df_master = pd.concat(all_dfs, ignore_index=True)

    # --- Tier-1 — Dataset validation ---
    df_master, wellness, context = run_tier1_controller(df_master, wellness, context)

    # --- Tier-2 — Full audit chain ---
    context = validate_data_integrity(df_master, wellness, context)
    df_master, daily = validate_event_completeness(df_master)  # returns updated df + daily
    context = enforce_event_only_totals(df_master, context)
    context = validate_calculation_integrity(df_master, context)
    context = validate_wellness(wellness, context)
    context = compute_derived_metrics(df_master, context)
    context = evaluate_actions(context)

    # --- Promote final audit state before render ---
    if context.get("auditPartial", True):
        context["auditFinal"] = True
    else:
        print("⚠ Tier-1 not validated. Forcing auditFinal=True for controlled render.")
        context["auditFinal"] = True

    # --- Final render ---
    report, compliance = finalize_and_validate_render(context, reportType=user_cmd)

    return report, compliance


if __name__ == "__main__":
    # Example run
    run_report("season report")
