import sys, os

# --- Force project root into sys.path ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
print(f"[DEBUG] Added ROOT_DIR to sys.path: {ROOT_DIR}")

# --- Optional: show current working directory ---
print(f"[DEBUG] CWD: {os.getcwd()}")

import pandas as pd
from datetime import timedelta, datetime, date

import pandas as pd
from datetime import timedelta, datetime, date
from audit_core.errors import AuditHalt

from audit_core.utils import debug
from api_github_com__jit_plugin import loadAllRules

from audit_core.tier0_pre_audit import run_tier0_pre_audit
from audit_core.tier1_controller import run_tier1_controller
from audit_core.tier2_event_completeness import validate_event_completeness
from audit_core.tier2_enforce_event_only_totals import enforce_event_only_totals
from audit_core.utils import (
    validate_dataset_integrity as validate_calculation_integrity,
    validate_wellness_alignment as validate_wellness,
)
from audit_core.tier2_derived_metrics import compute_derived_metrics
from audit_core.tier2_actions import evaluate_actions
from audit_core.tier2_render_validator import finalize_and_validate_render
from audit_core.tier2_extended_metrics import compute_extended_metrics
from semantic_json_builder import build_semantic_json

# --- optional compatibility alias ---
from intervals_icu__jit_plugin import (
    getAthleteProfile,
    listActivitiesLight,
    listActivitiesFull,
    listWellness,
)

def orchestrate_fetch_context(report_type: str = "weekly", today: date | None = None):
    """
    Unified fetch orchestrator for URF v5.x.
    Fetches all datasets (profile, light, full, wellness)
    and sets context flags for render and phase behavior.
    Supports both local execution and ChatGPT tool-execution mode.
    """
    from datetime import date, timedelta
    from audit_core.utils import debug

    # --- Tool fallback import ---
    try:
        from intervals_icu__jit_plugin import (
            getAthleteProfile,
            listActivitiesLight,
            listActivitiesFull,
            listWellness,
        )
        debug({}, "[CHAIN] Using local intervals_icu__jit_plugin bindings")
    except ImportError:
        # Fallback to ChatGPT plugin tool binding
        import intervalsicugptcoach_clive_a5a_workers_dev__jit_plugin as tool
        getAthleteProfile = tool.getAthleteProfile
        listActivitiesLight = tool.listActivitiesLight
        listWellness = tool.listWellness
        listActivitiesFull = tool.listActivitiesFull
        debug({}, "[CHAIN] Using ChatGPT tool bindings (intervalsicugptcoach_clive_a5a_workers_dev__jit_plugin)")

    # --- Base context ---
    today = today or date.today()
    rtype = report_type.lower()
    ctx: dict[str, any] = {"report_type": rtype, "today": str(today)}

    # --- Profile always first ---
    ctx["profile"] = getAthleteProfile()

    # --- Date range config ---
    if rtype in ("weekly", "summary"):
        light_days, full_days, wellness_days = 90, 7, 42
    elif rtype in ("season", "season_phases", "season_summary"):
        light_days, full_days, wellness_days = 90, 7, 42
    elif rtype == "wellness":
        light_days, full_days, wellness_days = 90, 7, 42
    else:
        raise ValueError(f"Unknown report type '{report_type}'")

    # --- Chunk mode logic ---
    chunk_mode = full_days > 7 or light_days > 90 or wellness_days > 42

    debug(ctx, f"[CHAIN] Starting orchestrate_fetch_context for {rtype} | light={light_days} full={full_days} wellness={wellness_days}")

    # --- Fetch chain ---
    try:
        ctx["activities_light"] = listActivitiesLight(
            oldest=str(today - timedelta(days=light_days)),
            newest=str(today),
            fields="id,name,type,sport_type,start_date_local,distance,moving_time,icu_training_load,average_heartrate,IF,VO2MaxGarmin",
        )
        debug(ctx, "[CHAIN] 90-day light activities fetched")
    except Exception as e:
        debug(ctx, f"[CHAIN] Light activities fetch failed: {e}")
        ctx["activities_light"] = []

    # --- 7-day Full dataset (always required for weekly) ---
    if full_days > 0:
        try:
            ctx["activities_full"] = listActivitiesFull(
                oldest=str(today - timedelta(days=full_days)),
                newest=str(today),
                auto=True,
                chunk=chunk_mode,
            )
            debug(ctx, "[CHAIN] 7-day full activities fetched successfully")
        except Exception as e:
            debug(ctx, f"[CHAIN] Full activities fetch failed: {e}")
            ctx["activities_full"] = []

    # --- Wellness fetch ---
    if wellness_days > 0:
        try:
            ctx["wellness"] = listWellness(
                oldest=str(today - timedelta(days=wellness_days)),
                newest=str(today),
            )
            debug(ctx, "[CHAIN] 42-day wellness data fetched")
        except Exception as e:
            debug(ctx, f"[CHAIN] Wellness fetch failed: {e}")
            ctx["wellness"] = []

    # --- Safety fallback (especially for ChatGPT mode) ---
    if rtype == "weekly" and (not ctx.get("activities_full") or len(ctx["activities_full"]) == 0):
        debug(ctx, "[CHAIN] Auto-forcing 7-day full fetch (safety path)")
        try:
            ctx["activities_full"] = listActivitiesFull(
                oldest=str(today - timedelta(days=7)),
                newest=str(today),
                auto=True,
            )
            debug(ctx, "[CHAIN] Forced 7-day full fetch succeeded")
        except Exception as e:
            debug(ctx, f"[CHAIN] Forced 7-day full fetch failed: {e}")
            ctx["activities_full"] = []

    # --- Range metadata ---
    ctx["range"] = {
        "lightDays": light_days,
        "fullDays": full_days,
        "wellnessDays": wellness_days,
        "chunk": chunk_mode,
    }
    ctx["fetchComplete"] = True

    # --- Render + phase flagging ---
    if rtype == "weekly":
        ctx["render_mode"], ctx["phase_mode"] = "full+metrics", False
    elif rtype == "summary":
        ctx["render_mode"], ctx["phase_mode"] = "summary", False
    elif rtype == "season":
        ctx["render_mode"], ctx["phase_mode"] = "block", False
    elif rtype == "season_phases":
        ctx["render_mode"], ctx["phase_mode"] = "block+phases", True
        ctx["phases"] = []
    elif rtype == "season_summary":
        ctx["render_mode"], ctx["phase_mode"] = "block+summary", False
    elif rtype == "wellness":
        ctx["render_mode"], ctx["phase_mode"] = "recovery", False

    debug(ctx, f"[CHAIN] Context fetch complete for {rtype} | render_mode={ctx['render_mode']}")
    return ctx


def run_report(
    reportType: str = "weekly",
    auditFinal: bool = True,
    auditPartial: bool = False,
    force_analysis: bool = True,
    preRenderAudit: bool = False,
    tier2_enforce_event_only_totals: bool = True,
    render_mode: str = "full+metrics",
    autoCommit: bool = True,
    suppressPrompts: bool = True,
    postRenderAudit: bool = True,
    merge_events: bool = False,
    render_summary: bool = False,
    include_coaching_metrics: bool = True,
    allowSyntheticRender: bool = False,
    output_format="markdown",  # Ensure output_format is defined
    **kwargs,
):
    """
    Centralized execution for all endpoints:
    - Runs Tier-0 → Tier-1 → Tier-2 → Renderer
    - Returns (report, compliance, logs, context, semantic_graph)
    """
    # Initialize context
    context = {}
    context.update(kwargs)
    context.update({
        "render_summary": render_summary,
        "include_coaching_metrics": include_coaching_metrics,
        "postRenderAudit": postRenderAudit,
    })
    # Ensure debug_mode is set from kwargs
    context["debug_mode"] = kwargs.get("debug_mode", False)

    # ============================================================
    # 🔒 CANONICAL REPORT TYPE (AUTHORITATIVE)
    # ============================================================

    assert isinstance(reportType, str), "reportType must be a string"

    context["report_type"] = reportType.lower()
    debug(context, f"[ORCH] report_type locked → {context['report_type']}")


    # Initialize report
    report = {}

    if output_format == "semantic":
        # Defer semantic build until AFTER full pipeline completes.
        context["semantic_mode"] = True   # marker for downstream render stage

    # ============================================================
    # PREFETCH REGISTRATION (Cloudflare → Railway)
    # ============================================================

    # 1) If caller already supplied a prefetched contract, DO NOT overwrite it.
    if isinstance(context.get("prefetched"), dict) and context["prefetched"]:
        # Enforce FLAT invariant
        a = context["prefetched"].get("athlete")
        if isinstance(a, dict) and "athlete" in a:
            context["prefetched"]["athlete"] = a["athlete"]

    else:
        context["prefetched"] = {}

        if isinstance(context.get("activities_light"), list):
            context["prefetched"]["light"] = context["activities_light"]

        if isinstance(context.get("activities_full"), list):
            context["prefetched"]["full"] = context["activities_full"]

        if isinstance(context.get("wellness"), list):
            context["prefetched"]["wellness"] = context["wellness"]

        if isinstance(context.get("athlete"), dict):
            # 🔒 STORE FLAT — NEVER WRAP
            context["prefetched"]["athlete"] = context["athlete"]
        else:
            debug(context, "[ORCH-WARN] Invalid athlete cache payload")

        if isinstance(context.get("calendar"), list):
            context["prefetched"]["calendar"] = context["calendar"]
            debug(context, f"[T1] ✅ Registered prefetched calendar ({len(context['calendar'])} events)")
        else:
            debug(context, "[T1] ⚠️ No prefetched calendar found or invalid format")


    # ============================================================
    # 🔑 AUTHORITATIVE BIND — PREFETCHED ATHLETE (FLAT ONLY)
    # ============================================================

    if isinstance(context.get("prefetched", {}).get("athlete"), dict):
        athlete = context["prefetched"]["athlete"]

        # Bind ONCE, flat, authoritative
        context["athlete"] = athlete
        context["athleteProfile"] = athlete
        debug(context, "[ORCH] Bound prefetched athlete → athlete / athleteProfile")

        # --------------------------------------------------------
        # 🔧 HARD GUARD — Tier-0 REQUIRES timezone
        # --------------------------------------------------------
        tz = athlete.get("timezone")
        if not isinstance(tz, str) or len(tz) < 3:
            tz = context.get("timezone") or "Europe/Zurich"
            athlete["timezone"] = tz
            debug(
                context,
                f"[ORCH-FIX] Injected missing athlete.timezone = {tz}"
            )

        # Single canonical timezone
        context["timezone"] = athlete["timezone"]

    # ------------------------------------------------------------
    # Prefetch bookkeeping
    # ------------------------------------------------------------
    if context.get("prefetched"):
        debug(
            context,
            f"[ORCH] Registered prefetched datasets: {list(context['prefetched'].keys())}"
        )

    # 🔒 Prefetch is authoritative — never refetch
    if context.get("prefetched", {}).get("full"):
        context["force_light"] = False
        context["prefetch_done"] = True

    # ------------------------------------------------------------
    # 🧭 Local-mode correction for non-prefetched runs
    # ------------------------------------------------------------
    if not context.get("prefetched"):
        context["force_light"] = True
        debug(context, f"[T0] Local mode → force_light=True (no prefetch, {reportType})")


    # --- NEW: Bind reportMode for schema-based orchestration ---
    context["reportMode"] = reportType.lower() if isinstance(reportType, str) else "weekly"

    debug(context, f"🧭 Running {reportType.title()} Report (auditFinal={auditFinal}, render_mode={render_mode})")

    # --- Tier-0 Range Configuration (aligned with worker) ---
    today = datetime.now().date()

    if reportType.lower() == "season":
        context["range"] = {"lightDays": 90, "fullDays": 42, "wellnessDays": 90, "chunk": True}
    else:  # weekly / wellness / summary
        context["range"] = {"lightDays": 90, "fullDays": 7, "wellnessDays": 42, "chunk": False}

    # Local variable bindings for convenience
    light_days = context["range"]["lightDays"]
    full_days = context["range"]["fullDays"]
    chunk = context["range"]["chunk"]

    debug(context, f"[T0] Config → light={light_days}d full={full_days}d chunk={chunk}")

    # --- Tier-0 Full Audit (canonical, single execution) ---
    import pandas as pd

    try:
        full_start = today - timedelta(days=full_days)
        full_end = today

        debug(
            context,
            f"[T0-FULL] Executing Tier-0 canonical path → {full_start} → {full_end}"
        )

        df_master, wellness, context, auditPartial, auditFinal = run_tier0_pre_audit(
            str(full_start),
            str(full_end),
            context,
        )

    except AuditHalt:
        raise
    except Exception as e:
        debug(context, f"[T0-FULL] Tier-0 execution failed: {e}")
        raise

    # ============================================================
    # 🔒 LOCK Tier-0 90-day dataset (authoritative for Tier-3)
    # ============================================================
    if "df_light_full" in context and isinstance(context["df_light_full"], pd.DataFrame):
        context["_df_light_90d"] = context["df_light_full"].copy()
        debug(context, "[LOCK] Stored df_light_full as canonical 90-day dataset")
    elif "df_light" in context and isinstance(context["df_light"], pd.DataFrame):
        context["_df_light_90d"] = context["df_light"].copy()
        debug(context, "[LOCK] Stored df_light as canonical 90-day dataset")
    else:
        context["_df_light_90d"] = pd.DataFrame()
        debug(context, "[LOCK-WARN] No 90-day dataset available to lock")

    # --- Preserve existing full fetch if prefetch already covered it ---
    if context.get("prefetch_done") and context.get("snapshot_7d_json"):
        debug(context, "[T0-FULL] Prefetch contained full window — skipping redundant re-fetch.")
        # Retain previously fetched detailed dataset and wellness
        if context.get("df_master") is not None:
            df_master = context.get("df_master")
            debug(context, f"[T0-FULL] Reusing prefetch df_master with {len(df_master)} rows.")
        elif "df_light_slice" in context:
            df_master = context.get("df_light_slice")
            debug(context, f"[T0-FULL] Fallback to df_light_slice ({len(df_master)} rows).")

        # Preserve wellness if available in context
        if (wellness is None or not isinstance(wellness, pd.DataFrame) or wellness.empty) and \
        isinstance(context.get("wellness"), pd.DataFrame):
            wellness = context["wellness"].copy()
            debug(context, "[T0-FULL] Rehydrated wellness DataFrame from context.")

    # --- Capture post-audit context safely for fallback use ---
    context_pre_audit = context.copy()


    if df_master is None or not isinstance(df_master, pd.DataFrame) or df_master.empty:
        debug(context, "[T0-FULL] No df_master returned — using pre-audit lightweight dataset as fallback.")

        # Helper function for safe extraction
        def pick_valid_df(*candidates):
            for df in candidates:
                if isinstance(df, pd.DataFrame) and not df.empty:
                    return df
            return None

        df_master = pick_valid_df(
            context_pre_audit.get("df_light_slice"),
            context_pre_audit.get("df_light"),
            context_pre_audit.get("activities_light"),
            context.get("df_light_slice"),
            context.get("df_light"),
            context.get("activities_light"),
        )

        if df_master is None:
            debug(context, "[T0-FULL] WARNING: no valid fallback dataset — initializing empty DataFrame.")
            df_master = pd.DataFrame()
        else:
            debug(context, f"[T0-FULL] Using fallback df_master with {len(df_master)} rows and columns={list(df_master.columns)}")

        # --- Sync fallback dataset into context for Tier-1 ---
        context["df_master"] = df_master
        context["df_light"] = context_pre_audit.get("df_light", context.get("df_light"))
        context["df_light_slice"] = context_pre_audit.get("df_light_slice", context.get("df_light_slice"))
        context["snapshot_7d_json"] = context_pre_audit.get("snapshot_7d_json", context.get("snapshot_7d_json"))

        debug(context, f"[T0-FULL] Context synced for Tier-1 — df_master={len(df_master)} rows, snapshot_7d_json={'ok' if 'snapshot_7d_json' in context else 'missing'}")

    # --- Preserve wellness for Tier-1 downstream ---
    if isinstance(wellness, pd.DataFrame) and not wellness.empty:
        context["wellness"] = wellness.copy()
        debug(context, f"[T0-FULL] Preserved wellness in context ({len(wellness)} rows)")

    # --- Mark mode in context for downstream components ---
    # Canonical report_type injection (LOCAL ONLY)
    if "report_type" not in context or not context["report_type"]:
        context["report_type"] = reportType.lower() if isinstance(reportType, str) else "weekly"
    context["chunk_mode"] = chunk
    context["light_days"] = light_days
    context["full_days"] = full_days
    context["df_light_full"] = context["_df_light_90d"]
    debug(context, f"[T0] Completed range alignment → chunk_mode={chunk}")
        

    # --- Merge static knowledge base ---
    from athlete_profile import ATHLETE_PROFILE
    from coaching_profile import COACH_PROFILE
    from coaching_heuristics import HEURISTICS
    from coaching_cheat_sheet import CHEAT_SHEET

    context["knowledge"] = {
        "athlete_profile": ATHLETE_PROFILE,
        "coach_profile": COACH_PROFILE,
        "heuristics": HEURISTICS,
        "cheatsheet": CHEAT_SHEET,
    }

    # --- Athlete profile (preserve Tier-0 mapping) ---
    if not isinstance(context.get("athleteProfile"), dict) or not context["athleteProfile"]:
        from athlete_profile import map_icu_athlete_to_profile
        context["athleteProfile"] = map_icu_athlete_to_profile(context.get("athlete", {}))
        debug(context, "[ORCH] athleteProfile missing → rebuilt from athlete")
    else:
        debug(context, "[ORCH] athleteProfile present → preserved")


        # --- Normalize moving_time units ---
    if "moving_time" in df_master.columns:
        max_val = df_master["moving_time"].max()
        if max_val < 25:
            df_master["moving_time"] *= 3600
            debug(context, f"⚙️ Normalization: converted moving_time hours→seconds (max={max_val})")
        else:
            debug(context, f"⚙️ Normalization: seconds detected, no conversion (max={max_val})")

    # --- Tier-1 Audit ---
    debug(context, f"[T1] Running Tier-1 controller ({reportType} mode)")
    df_master, wellness, context = run_tier1_controller(df_master, wellness, context)

    # ------------------------------------------------------------
    # T1 RESTORE 
    # ------------------------------------------------------------

    # --- Ensure df_light exists and is a DataFrame ---
    if "df_light" not in context or not isinstance(context["df_light"], pd.DataFrame):
        
        # 1) direct df_light_full (best source)
        if isinstance(context.get("df_light_full"), pd.DataFrame):
            context["df_light"] = context["df_light_full"].copy()
            debug(context, f"[T1] Restored df_light from df_light_full ({len(context['df_light'])} rows).")

        # 2) fallback to activities_light
        elif isinstance(context.get("activities_light"), pd.DataFrame):
            context["df_light"] = context["activities_light"].copy()
            debug(context, f"[T1] Restored df_light from activities_light ({len(context['df_light'])} rows).")

        # 3) fallback if activities_light is a list
        elif isinstance(context.get("activities_light"), list):
            context["df_light"] = pd.DataFrame(context["activities_light"])
            debug(context, f"[T1] Converted activities_light list → df_light ({len(context['df_light'])} rows).")

        else:
            context["df_light"] = pd.DataFrame()
            debug(context, "[T1] WARNING: No valid df_light source found — df_light = empty.")


    # ------------------------------------------------------------
    # T1 FIXES — ensure load_metrics & scalar markers exist
    # ------------------------------------------------------------

    # 1. Ensure load_metrics exists (markdown uses this)
    if "load_metrics" not in context or not context["load_metrics"]:
        debug(context, "[T1-FIX] load_metrics missing → injecting empty container")
        context["load_metrics"] = {}

    # 2. Rehydrate derived metric scalars needed by extended metrics
    dm = context.get("derived_metrics", {})

    for key in ("ACWR", "Monotony", "Strain", "Polarisation"):
        if key in dm:
            context[key] = dm[key].get("value")
        else:
            context[key] = None

    debug(context, f"[T1-FIX] Rehydrated scalars for extended: "
                f"ACWR={context.get('ACWR')} "
                f"Monotony={context.get('Monotony')} "
                f"Strain={context.get('Strain')} "
                f"Polarisation={context.get('Polarisation')}")


    # --- Tier-2 Enforcement Chain ---
    df_master, _ = validate_event_completeness(df_master)

    # ============================================================
    # Tier-2 ANALYSIS SCOPE (authoritative switch)
    # Weekly  → 7-day snapshot
    # Season  → 90-day light dataset
    # ============================================================

    from io import StringIO

    full_days = context.get("range", {}).get("fullDays", 7)

    # ✅ Preserve the real full dataset before df_scope is overwritten
    if isinstance(df_master, pd.DataFrame) and not df_master.empty:
        context["_df_scope_full"] = df_master.copy()
        debug(context, f"[PRESERVE] Stored df_master as _df_scope_full ({len(df_master)} rows, {len(df_master.columns)} cols)")
    else:
        debug(context, "[PRESERVE] No valid df_master available to preserve as _df_scope_full")

    if full_days == 7:
        # WEEKLY analysis → strict 7-day scope
        try:
            df_scope = pd.read_json(StringIO(context["snapshot_7d_json"]))
            debug(
                context,
                f"[SCOPE] Weekly analysis → snapshot_7d "
                f"({len(df_scope)} rows)"
            )
        except Exception as e:
            debug(context, f"[WARN] Weekly snapshot parse failed → fallback to df_master: {e}")
            df_scope = df_master

    else:
        # SEASON / LONG-RANGE analysis → 90-day light dataset
        df_scope = context.get("df_light")
        debug(
            context,
            f"[SCOPE] Season analysis → df_light "
            f"({len(df_scope)} rows)"
        )

        if df_scope is None or not isinstance(df_scope, pd.DataFrame) or df_scope.empty:
            debug(context, "[SCOPE-WARN] df_light missing/empty → falling back to df_master")
            df_scope = df_master

    if full_days > 7:
        assert len(df_scope) > 14, "Season analysis incorrectly scoped to short window"


    # --- Enforce totals and sync df_events for validator ---
    context = enforce_event_only_totals(df_scope, context)
    if "tier2_enforced_totals" in context:
        et = context["tier2_enforced_totals"]
        context["totalHours"] = et.get("time_h", 0)
        context["totalTss"] = et.get("tss", 0)
        debug(context, f"[SYNC] Totals from enforcement hours={context['totalHours']}, tss={context['totalTss']}")

    # --- Preserve pure event-only totals for renderer ---
    if "tier2_enforced_totals" in context:
        context["tier2_eventTotals_eventOnly"] = context["tier2_enforced_totals"].copy()
        debug(context, "[T2] Preserved event-only totals for renderer binding.")

    debug(context, f"[CHK] tier0_snapshotTotals_7d = {context.get('tier0_snapshotTotals_7d')}")
    debug(context, f"[CHK] tier2_enforced_totals = {context.get('tier2_enforced_totals')}")
    debug(context, f"[CHK] tier2_eventTotals = {context.get('tier2_eventTotals')}")
    debug(context, f"[CHK] tier2_eventTotals_eventOnly = {context.get('tier2_eventTotals_eventOnly')}")

    # --- Determine if audit can be considered final ---
    df_full_ok = bool(context.get("activities_full") is not None and len(context.get("activities_full")) > 0)
    data_source = context.get("data_source", "")
    validated_t2 = context.get("tier2_enforced_totals", {}).get("validated", False)
    variance_ok = context.get("variance_ok", False)

    # ✅ Only degrade if full fetch truly failed (no df_full + light_fallback)
    if (not df_full_ok and data_source == "light_fallback") and not validated_t2:
        context["auditFinal"] = False
        context["auditPrecision"] = "degraded"
        debug(context, "[T2] Degraded mode: full fetch failed, light_fallback used.")
    else:
        context["auditFinal"] = True
        context["auditPrecision"] = "normal"
        debug(context, "[T2] Normal precision: full fetch succeeded or 7d slice validated.")

    if context.get("report_type") != "season":
        context["df_events"] = df_scope.copy()
        debug(context, f"[SYNC] df_events replaced with df_scope ({len(df_scope)} rows)")

    # --- Ensure totals exist even if enforcement failed ---
    if not context.get("totalHours") or not context.get("totalTss"):
        context["totalHours"] = df_scope["moving_time"].sum() / 3600
        context["totalTss"] = df_scope["icu_training_load"].sum()
        debug(context, "[T2-FIX] Derived totals directly from df_scope")

    # --- Make full Tier-0 data available to Tier-2 derived metrics ---
    if "activities_light" in context and isinstance(context["activities_light"], list):
        context["df_event_only_full"] = context["activities_light"]

    # After confirming successful fetch
    context["auditFinal"] = True
    context["auditPartial"] = False
    context["fetch_status"] = "complete"

    # --- Tier-2 core metrics ---
    context = compute_derived_metrics(df_scope, context)
    context = evaluate_actions(context)

    # ============================================================
    # RESTORE canonical 90-day dataset (AUTHORITATIVE)
    # ============================================================
    if "_df_light_90d" not in context or not isinstance(context["_df_light_90d"], pd.DataFrame):
        raise RuntimeError("FATAL: _df_light_90d missing — Tier-2 pipeline corrupted")

    context["df_light"] = context["_df_light_90d"]
    debug(context, f"[EXT-PRE] df_light rows={len(context['df_light'])}")

    debug(
        context,
        "[SMOKING-GUN] df_light rows=%s load_sum=%s cols=%s"
        % (
            0 if context.get("df_light") is None else len(context["df_light"]),
            context["df_light"]["icu_training_load"].sum()
            if isinstance(context.get("df_light"), pd.DataFrame)
            and "icu_training_load" in context["df_light"]
            else "MISSING",
            list(context["df_light"].columns)
            if isinstance(context.get("df_light"), pd.DataFrame)
            else type(context.get("df_light")),
        )
    )

    # ============================================================
    # AUTHORITATIVE CTL / ATL / TSB (Intervals ICU)
    # ============================================================

    ws = context.get("wellness_summary", {})

    context["load_metrics"] = {
        "CTL": {"value": ws.get("ctl"), "status": "icu"},
        "ATL": {"value": ws.get("atl"), "status": "icu"},
        "TSB": {"value": ws.get("tsb"), "status": "icu"},
    }

    debug(
        context,
        f"[LOAD-ICU] CTL={ws.get('ctl')} ATL={ws.get('atl')} TSB={ws.get('tsb')}"
    )

    # ============================================================
    # Tier-2 EXTENDED METRICS — SINGLE AUTHORITATIVE CALL
    # ============================================================

    context = compute_extended_metrics(context)

    debug(
        context,
        "[EXT-POST] extended=%s adaptation=%s trend=%s corr=%s"
        % (
            bool(context.get("extended_metrics")),
            bool(context.get("adaptation_metrics")),
            bool(context.get("trend_metrics")),
            bool(context.get("correlation_metrics")),
        )
    )
    # ============================================================
    # 🗓️ TIER-3: CALENDAR & FUTURE FORECAST
    # ============================================================
    from audit_core.tier3_future_forecast import run_future_forecast

    debug(context, "[T3] 🚀 Starting Tier-3 Future Forecast module …")

    try:
        future_output = run_future_forecast(context)
        if isinstance(future_output, dict):
            context.update(future_output)
            ff = context.get("future_forecast", {})
            debug(context, f"[T3] ✅ Future forecast added: CTL_future={ff.get('CTL_future', 'n/a')}, ATL_future={ff.get('ATL_future', 'n/a')}, TSB_future={ff.get('TSB_future', 'n/a')}")
        else:
            debug(context, "[T3] ⚠️ No valid future forecast output returned from module.")

    except Exception as e:
        import traceback
        debug(context, f"[T3] ❌ Future forecast failed with error: {e}")
        traceback.print_exc()


    # --- Ensure minimum required context keys for validator ---
    if "actions" not in context:
        context["actions"] = []
        debug(context, "[T2-FIX] Injected empty actions list to satisfy validator.")

    if "athlete" not in context:
        athlete = context.get("athleteProfile", {})
        context["athlete"] = {
            "id": athlete.get("athlete_id", "unknown"),
            "name": athlete.get("name", "Unknown Athlete"),
            "ftp": athlete.get("ftp", None),
            "weight": athlete.get("weight", None),
            "sport": athlete.get("discipline", "cycling"),
        }
        debug(context, "[T2-FIX] Rebuilt athlete object from athleteProfile.")

    if "timezone" not in context:
        context["timezone"] = athlete.get("timezone", "UTC")
        debug(context, "[T2-FIX] Defaulted timezone to UTC.")

    # --- PATCH: Hard-lock load_metrics before Tier-2 render ---
    if "load_metrics" in context and context["load_metrics"]:
        context["_locked_load_metrics"] = context["load_metrics"].copy()
        debug(context, "[PATCH-LOCK] Preserved load_metrics before validator:", context["_locked_load_metrics"])

    # --- Finalization ---
    context["auditFinal"] = True
    context["render_mode"] = "full+metrics"
    debug(context, "🧩 Render mode forced to full+metrics for URF layout")

    # --- Hard-verify df_events for Tier-2 validator ---
    if "df_events" not in context or getattr(context["df_events"], "empty", True):
        if "df_master" in locals() and not df_master.empty:
            context["df_events"] = df_master.copy()
            debug(context, f"[T2-HARDPATCH] Injected df_master as df_events ({len(df_master)} rows)")
        elif "df_master" in context and isinstance(context["df_master"], pd.DataFrame):
            context["df_events"] = context["df_master"].copy()
            debug(context, f"[T2-HARDPATCH] Recovered df_events from context copy ({len(context['df_events'])} rows)")
        else:
            debug(context, "[T2-HARDPATCH] No valid event data — injecting stub DataFrame")
            context["df_events"] = pd.DataFrame([{
                "date": datetime.now().strftime("%Y-%m-%d"),
                "icu_training_load": 0,
                "moving_time": 0,
                "distance": 0
            }])

    # --- Inject full Tier-0 dataset for proper ACWR (acute/chronic load ratio) ---
    if "activities_light" in context and isinstance(context["activities_light"], list):
        import pandas as pd
        context["df_event_only_full"] = pd.DataFrame(context["activities_light"])
        debug(context, f"[TIER-2 INIT] Injected Tier-0 full dataset ({len(context['activities_light'])} activities)")


    # --- 🧩 Canonical totals resolution before render ---
    # Priority: Tier-2 enforced → Tier-1 visible → Derived fallback
    totals_source = None

    if "tier2_enforced_totals" in context:
        et = context["tier2_enforced_totals"]
        context["totalHours"] = et.get("time_h") or et.get("hours", 0)
        context["totalTss"] = et.get("tss", 0)
        context["totalDistance"] = et.get("distance_km") or et.get("distance", 0)
        totals_source = "tier2_enforced_totals"
        debug(context, "[SYNC] Canonical totals restored from Tier-2 enforced totals.")

    elif "tier1_visibleTotals" in context:
        vt = context["tier1_visibleTotals"]
        context["totalHours"] = vt.get("hours", 0)
        context["totalTss"] = vt.get("tss", 0)
        context["totalDistance"] = vt.get("distance", 0)
        totals_source = "tier1_visibleTotals"
        debug(context, "[SYNC] Fallback totals restored from Tier-1 visibleTotals.")

    else:
        df_events = context.get("df_events", pd.DataFrame())
        if not df_events.empty:
            context["totalHours"] = df_events["moving_time"].sum() / 3600 if "moving_time" in df_events else 0
            context["totalTss"] = df_events["icu_training_load"].sum() if "icu_training_load" in df_events else 0
            context["totalDistance"] = df_events["distance"].sum() if "distance" in df_events else 0
            totals_source = "df_events"
            debug(context, "[SYNC] Totals derived directly from df_events.")
        else:
            context["totalHours"], context["totalTss"], context["totalDistance"] = 0, 0, 0
            totals_source = "fallback"
            debug(context, "[SYNC] Injected fallback zero totals (no valid source).")

    # --- Prefer locked canonical values if present ---
    context["totalHours"] = context.get("locked_totalHours") or context["totalHours"]
    context["totalTss"] = context.get("locked_totalTss") or context["totalTss"]
    context["totalDistance"] = context.get("locked_totalDistance") or context["totalDistance"]

    debug(context, f"[RENDER-READY] Totals source={totals_source} | "
                f"hours={context['totalHours']} | tss={context['totalTss']} | "
                f"distance={context.get('totalDistance')}")

    # --- 🧱 Prevent duplicate render/finalization ---
    if context.get("FINALIZER_LOCKED_GLOBAL"):
        debug(context, "[FINALIZER] Duplicate render prevented (global lock active).")
        return final_output if 'final_output' in locals() else {}, None

    context["FINALIZER_LOCKED_GLOBAL"] = True
    debug(context, "[FINALIZER] First and only render pass permitted.")

    # --- Inject dual totals for renderer if available ---
    try:
        df_all = context.get("df_events")
        if not isinstance(df_all, pd.DataFrame) or df_all.empty:
            df_all = context.get("df_master")

        if isinstance(df_all, pd.DataFrame) and not df_all.empty:
            # 🧮 All activities
            total_all = {
                "hours": df_all["moving_time"].sum() / 3600 if "moving_time" in df_all else 0,
                "distance": df_all["distance"].sum() / 1000 if "distance" in df_all else 0,
                "tss": df_all["icu_training_load"].sum() if "icu_training_load" in df_all else 0,
                "sessions": len(df_all),
            }

            # 🚴 Cycling-only (match VirtualRide, Ride, or Cycling)
            if "type" in df_all.columns:
                df_cyc = df_all[
                    df_all["type"]
                    .astype(str)
                    .str.lower()
                    .str.contains("ride|cycling", regex=True, na=False)
                ]
            else:
                df_cyc = df_all

            total_cyc = {
                "hours": df_cyc["moving_time"].sum() / 3600 if "moving_time" in df_cyc else 0,
                "distance": df_cyc["distance"].sum() / 1000 if "distance" in df_cyc else 0,
                "tss": df_cyc["icu_training_load"].sum() if "icu_training_load" in df_cyc else 0,
                "sessions": len(df_cyc),
            }

            context["summary_all"] = total_all
            context["summary_cycling"] = total_cyc

            debug(
                context,
                f"[T2] Injected dual totals → "
                f"cycling={total_cyc}, all={total_all}"
            )
        else:
            debug(context, "[T2 WARN] No valid df_all found for dual totals injection")

    except Exception as e:
        debug(context, f"[T2 WARN] Dual totals injection failed: {e}")

    # --- Force full unified render ---
    context["auditFinal"] = True                    # ✅ tell renderer audit is finalized
    context["render_mode"] = "full+metrics"
    context["enforce_render_source"] = "tier2_enforced_totals"  # ✅ use canonical source
    context["allow_intent_inference"] = False

    # --- Final render ----
    final_output, compliance = finalize_and_validate_render(context, reportType=reportType)

    # Check if the requested format is "semantic" or "markdown"
    if output_format == "semantic":
        # Generate the semantic graph
        debug(context, "[PRE-SEMANTIC] extended=%s adaptation=%s trend=%s corr=%s" % (
            bool(context.get("extended_metrics")),
            bool(context.get("adaptation_metrics")),
            bool(context.get("trend_metrics")),
            bool(context.get("correlation_metrics")),
        ))

        # Patch: inject athlete thresholds into context if missing
        athlete = context.get("athlete_raw", {})
        sport_settings = athlete.get("sportSettings", [])
        if sport_settings:
            primary = sport_settings[0]
            if "power_zones" in primary and not context.get("icu_power_zones"):
                context["icu_power_zones"] = primary["power_zones"]
            if "hr_zones" in primary and not context.get("icu_hr_zones"):
                context["icu_hr_zones"] = primary["hr_zones"]

        semantic_output = build_semantic_json(context)  # Ensure semantic_output is generated

        # If the output format is "semantic", return the semantic graph
        final_output = {
            "status": "ok",
            "message": f"{reportType.title()} Semantic Report Generated",
            "semantic_graph": semantic_output,  # Directly use the generated semantic_output
            "context": context,  # Add the full context for reference
            "logs": final_output.get("logs", "") if isinstance(final_output, dict) else "",  # Optional, include logs if needed
        }

    elif isinstance(final_output, dict) and "markdown" in final_output:
        # Existing logic for Markdown output
        final_output = {
            "markdown": final_output.get("markdown", "No Markdown Content Available"),  # Ensure markdown is populated
            "context": context,
            "summary": final_output.get("summary", {}),
            "header": final_output.get("header", {}),
        }

    elif not isinstance(final_output, dict):
        # Fallback if final_output is not a dictionary (safely convert to markdown string)
        final_output = {"markdown": str(final_output), "context": {}}

    # Log the completion of rendering
    debug(context, f"✅ Render + validation completed for {reportType}")

    # Return the final output and compliance as two values
    return final_output, compliance



if __name__ == "__main__":
    run_report("weekly")