import pandas as pd
from datetime import timedelta, datetime

from audit_core.utils import debug
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
    auditFinal: bool = False,
    auditPartial: bool = False,
    force_analysis: bool = False,
    preRenderAudit: bool = False,
    tier2_enforce_event_only_totals: bool = False,
    render_mode: str = "full+metrics",
    autoCommit: bool = True,
    suppressPrompts: bool = True,
    postRenderAudit: bool = False,
    merge_events: bool = False,
    render_summary: bool = False,
    include_coaching_metrics: bool = True,
    **kwargs
):
    # --- Initialize and merge context ---
    context = {}
    context.update(kwargs)
    context.update({
        "render_summary": render_summary,
        "include_coaching_metrics": include_coaching_metrics,
        "postRenderAudit": postRenderAudit,
    })
    # --- Debug mode toggle (enables developer-only diagnostics in render) ---
    context["debug_mode"] = kwargs.get("debug_mode", False)

    debug(context, f"🧭 Running {reportType.title()} Report (auditFinal={auditFinal}, render_mode={render_mode})")

    # --- Tier-0 — Ruleset and pre-audit ---
    loadAllRules()
    debug(context, "[T0-LIGHT] Forcing Tier-0 lightweight prefetch before full audit")
    try:
        if reportType.lower() == "season":
            _ = run_tier0_pre_audit(
                str((datetime.now().date() - timedelta(days=90))),
                str(datetime.now().date()),
                context
            )
        else:
            _ = run_tier0_pre_audit(
                str((datetime.now().date() - timedelta(days=28))),
                str(datetime.now().date()),
                context
            )
    except Exception as e:
        debug(context, f"[T0-LIGHT] Prefetch failed (non-fatal): {e}")

     # --- Determine date window based on report type ---
    today = datetime.now().date()

    if reportType.lower() == "weekly":
        start_date = today - timedelta(days=7)
        end_date = today
    elif reportType.lower() == "season":
        start_date = today - timedelta(days=90)
        end_date = today
    else:
        start_date = today - timedelta(days=7)
        end_date = today


    # --- Ensure Tier-0 context carries report type correctly ---
    context["report_type"] = reportType.lower() if isinstance(reportType, str) else "weekly"

    # Run Tier-0 pre-audit
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

    # Normalize athlete profile
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

    # --- Normalize moving_time units before Tier-1 ---
    if "moving_time" in df_master.columns:
        max_val = df_master["moving_time"].max()
        if max_val < 25:
            debug(context, f"⚙️ Normalization: converting moving_time from hours → seconds (max={max_val})")
            df_master["moving_time"] *= 3600
        else:
            debug(context, f"⚙️ Normalization: detected seconds, no conversion (max={max_val})")

    if reportType.lower() == "season":
        debug(context, "[T1] Running Tier-1 controller (season mode, limited metrics).")
    else:
        debug(context, "[T1] Running Tier-1 controller (weekly mode).")

    df_master, wellness, context = run_tier1_controller(df_master, wellness, context)

    
    # --- Tier-2 — Full audit chain ---
    df_master, daily = validate_event_completeness(df_master)
    context = enforce_event_only_totals(df_master, context)
    validate_calculation_integrity(df_master)
    validate_wellness(df_master, wellness)

    # --- Tier-2 core metrics ---
    context = compute_derived_metrics(df_master, context)
    context = evaluate_actions(context)

    # --- PATCH: Hard-lock load_metrics before Tier-2 render ---
    if "load_metrics" in context and context["load_metrics"]:
        context["_locked_load_metrics"] = context["load_metrics"].copy()
        debug(context, "[PATCH-LOCK] Preserved load_metrics before validator:", context["_locked_load_metrics"])

    # --- Tier-2 extended analytics ---
    context = compute_extended_metrics(df_master, context)
    if "_locked_load_metrics" in context:
        context["load_metrics"] = context["_locked_load_metrics"].copy()

    # --- Promote final audit state ---
    context["auditFinal"] = True
    context["render_mode"] = "full+metrics"
    debug(context, "🧩 Render mode forced to full+metrics for Unified 10-section layout")
    
    # --- Tier-1 override for URF renderer (lightweight 7-day totals) ---
    if reportType.lower() == "weekly" and "tier1_visibleTotals" in context:
        vt = context["tier1_visibleTotals"]
        context["totalHours"] = vt.get("hours")
        context["totalTss"] = vt.get("tss")
        context["totalDistance"] = vt.get("distance")
        context["totalSessions"] = vt.get("count", len(context.get("df_events", [])))
        debug(context, "[SYNC] URF renderer context overridden with tier1_visibleTotals")
    else:
        debug(context, "[SYNC] No tier1_visibleTotals found; using canonical totals")

    # --- Final render ---
    report, compliance = finalize_and_validate_render(context, reportType=reportType)
    return report, compliance


if __name__ == "__main__":
    run_report("season report")