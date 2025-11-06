import pandas as pd
from datetime import timedelta

from api_github_com__jit_plugin import loadAllRules
from audit_core.tier0_pre_audit import run_tier0_pre_audit
from audit_core.tier1_controller import run_tier1_controller
from audit_core.tier2_event_completeness import validate_event_completeness
from audit_core.tier2_enforce_event_only_totals import enforce_event_only_totals
from audit_core.utils import validate_dataset_integrity as validate_calculation_integrity
from audit_core.utils import validate_wellness_alignment as validate_wellness
from audit_core.tier2_derived_metrics import compute_derived_metrics
from audit_core.tier2_actions import evaluate_actions
from audit_core.tier2_render_validator import finalize_and_validate_render
from audit_core.tier2_extended_metrics import compute_extended_metrics

def run_report(
    reportType: str = "weekly",
    auditFinal: bool = True,
    auditPartial: bool = True,
    force_analysis: bool = True,
    preRenderAudit: bool = True,
    tier2_enforce_event_only_totals: bool = True,
    render_mode: str = "full",
    autoCommit: bool = True,
    suppressPrompts: bool = True,
    **kwargs
):
    print(f"🧭 Running {reportType.title()} Report (auditFinal={auditFinal}, render_mode={render_mode})")

    # --- Tier-0 — Ruleset and pre-audit ---
    loadAllRules()
    context = {}

    # --- Initial pre-audit ---
    from datetime import datetime, timedelta

    # Determine date window
    if reportType.lower() == "weekly":
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
    elif reportType.lower() == "season":
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=42)
    else:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)

    # Run Tier-0 pre-audit
    df_master, wellness, context, auditPartial, auditFinal = run_tier0_pre_audit(
        str(start_date),
        str(end_date),
        context
    )

    # Run Tier-0 pre-audit to get live data
    df_master, wellness, context, auditPartial, auditFinal = run_tier0_pre_audit(
        str(start_date),
        str(end_date),
        context
    )

    # --- Merge static schema with live athlete and coaching data ---
    from athlete_profile import ATHLETE_PROFILE
    from coaching_profile import COACH_PROFILE, get_profile_metrics
    from coaching_heuristics import HEURISTICS, derive_trends, derive_correlations
    from coaching_cheat_sheet import CHEAT_SHEET, summarize_load_block

    context["knowledge"] = {
        "athlete_profile": ATHLETE_PROFILE,
        "coach_profile": COACH_PROFILE,
        "heuristics": HEURISTICS,
        "cheatsheet": CHEAT_SHEET,
    }

    # Normalize athlete profile into schema
    athlete = context.get("athlete", {})
    profile_ref = ATHLETE_PROFILE.copy()
    profile_ref.update({
        "athlete_id": athlete.get("id"),
        "name": athlete.get("name"),
        "discipline": athlete.get("sport", "cycling"),
        "ftp": athlete.get("ftp"),
        "weight": athlete.get("weight"),
        "hr_rest": athlete.get("resting_hr"),
        "hr_max": athlete.get("max_hr"),
        "timezone": context.get("timezone"),
        "updated": athlete.get("updated"),
    })
    context["athleteProfile"] = profile_ref


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
    df_master, daily = validate_event_completeness(df_master)
    context = enforce_event_only_totals(df_master, context)
    validate_calculation_integrity(df_master)
    validate_wellness(df_master, wellness)

    # --- Tier-2 core metrics ---
    context = compute_derived_metrics(df_master, context)
    context = evaluate_actions(context)

    # --- Tier-2 extended analytics ---
    context = compute_extended_metrics(df_master, context)

    # --- Promote final audit state ---
    context["auditFinal"] = True

    # --- Final render ---
    report, compliance = finalize_and_validate_render(context, reportType=reportType)
    return report, compliance


if __name__ == "__main__":
    # Example run
    run_report("season report")
