#!/usr/bin/env python3
"""
Unified URF v5.1 Report Runner
==============================

Command-line tool for generating and retrieving Montis URF v5.1 training reports.

The runner can operate in two modes:

• Local generation (direct Python execution via audit_core)
• Remote generation (prefetched dataset via Cloudflare Worker → Railway)

It supports optional GPT rendering, debug execution traces, synthetic dataset
testing, and custom reporting windows.


───────────────────────────────────────────────
SYSTEM ARCHITECTURE
───────────────────────────────────────────────

Local mode
    CLI → audit_core.run_report()

Remote mode
    CLI → Cloudflare Worker → Railway /run → audit_core pipeline

The Worker acts as a unified API gateway.


───────────────────────────────────────────────
ENDPOINTS
───────────────────────────────────────────────

Railway Production
https://intervalsicugptcoach-public-production.up.railway.app

Railway Staging
https://intervalsicugptcoach-public-staging.up.railway.app

Cloudflare Worker (API Gateway)
https://intervalsicugptcoach.clive-a5a.workers.dev

Cloudflare Worker (Staging)
https://intervalsicugptcoach-staging.clive-a5a.workers.dev


───────────────────────────────────────────────
WORKER ROUTES
───────────────────────────────────────────────

/run_weekly
    7-day training load and fatigue analysis.

/run_season
    Long-term performance progression and adaptation trends.

/run_wellness
    Physiological recovery indicators (HRV, RHR, fatigue, sleep).

/run_summary
    High-level overview of athlete state and key metrics.

/run_data_quality
    Dataset integrity audit without building a full report.


───────────────────────────────────────────────
QUERY PARAMETERS (Worker)
───────────────────────────────────────────────

render=gpt
    Enables GPT Markdown rendering.

    Response:
    {
        "markdown": "...",
        "semantic_graph": {...},
        "logs": "...",
        "status": "ok"
    }

debug=true
    Executes the debug pipeline and returns full execution logs.

    Response:
    {
        "status": "ok",
        "report_type": "...",
        "semantic_graph": {...},
        "compliance": {...},
        "logs": "..."
    }

start=YYYY-MM-DD
end=YYYY-MM-DD
    Overrides the reporting window.

    Supported reports:
        weekly
        summary

    Weekly reports automatically expand the window to 7 days.

test=strava*
    Injects synthetic STRAVA-only dataset scenarios for pipeline testing.


───────────────────────────────────────────────
CLI MODES
───────────────────────────────────────────────

LOCAL MODE
    Runs the full pipeline directly in Python.

    Output files:
        report_<range>_prod_semantic.json
        report_<range>_prod_markdown.md


PREFETCH MODE (REMOTE)
    Fetches a prefetched dataset through the Worker.

    Output files:
        report_<range>_prefetch_prod_semantic.json

    With GPT rendering:
        report_<range>_prefetch_prod_gpt.md
        report_<range>_prefetch_prod_semantic.json


DEBUG MODE
    Fetches the debug execution trace from the Worker.

    Output files:
        report_<range>_<env>_debug.json
        report_<range>_<env>_debug.log


───────────────────────────────────────────────
CLI USAGE EXAMPLES
───────────────────────────────────────────────

Local semantic report
python report.py --range weekly


Local markdown report
python report.py --range weekly --format markdown


Remote report (Worker → Railway)
python report.py --range weekly --prefetch


Remote staging report
python report.py --range weekly --prefetch --staging


Remote GPT-rendered report
python report.py --range season --prefetch --gpt


Custom window (summary)
python report.py --range summary --start 2025-01-01 --end 2025-12-31


Weekly window override
python report.py --range weekly --start 2026-03-01


Debug execution trace
python report.py --range weekly --debug --staging


Data quality audit
python report.py --range data_quality --prefetch


───────────────────────────────────────────────
TEST SCENARIOS
───────────────────────────────────────────────

Synthetic STRAVA-only datasets can be simulated using the CLI flag
`--strava-test`.

| CLI flag             | Worker param   | Scenario                                  | Expected behaviour |
|----------------------|---------------|--------------------------------------------|-------------------|
| --strava-test stub   | test=strava   | All activities are STRAVA API stub rows    | Hard stop: STRAVA_API_RESTRICTED |
| --strava-test 1      | test=strava1  | Only light activities present              | Soft halt: insufficient detailed data |
| --strava-test 2      | test=strava2  | Full dataset empty after filtering         | Soft halt: no usable activities |
| --strava-test 3      | test=strava3  | Activities missing key metrics             | Report runs with degraded metrics |
| --strava-test 4      | test=strava4  | Partial wellness or athlete metadata       | Report runs with degraded data quality |
| --strava-test 5      | test=strava5  | Mixed valid and stub activities            | Report runs with warnings |
| --strava-test demo   | test=demo     | Demo dataset                               | Demo report generated |


───────────────────────────────────────────────
OUTPUT LOCATION
───────────────────────────────────────────────

All reports are written to:

./reports/

Debug runs generate two files:

    semantic report
    execution log


───────────────────────────────────────────────
NOTES
───────────────────────────────────────────────

• Local semantic reports never use GPT.

• Prefetch + GPT writes both Markdown and semantic JSON.

• Debug mode captures full pipeline execution logs (Tier-0 → Tier-3).

• The CLI runner doubles as an integration harness for Worker
  and Railway pipelines.
"""


import io
import os
import sys
import json
import argparse
import requests
import webbrowser
from datetime import datetime
from contextlib import redirect_stdout
from pathlib import Path
from app import normalize_prefetched_context
from audit_core.errors import AuditHalt
import pandas as pd

# --- Token estimation ---
try:
    import tiktoken
    _ENC = tiktoken.encoding_for_model("gpt-5")
except Exception:
    _ENC = None


def estimate_tokens_from_json(data):
    if _ENC is None:
        return None

    text = json.dumps(data, default=str, separators=(",", ":"))
    return len(_ENC.encode(text))

print("ARGV:", sys.argv)
# Import project modules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from audit_core.report_controller import run_report
from audit_core.utils import debug
from audit_core.utils import set_time_context

sys.stdout.reconfigure(encoding="utf-8")

#---------------------------------------------
#  Resolve correct Cloudflare Worker base URL.
#----------------------------------------------
def get_worker_base(staging=False):

    if staging:
        return "https://staging.montis.icu"
    return "https://montis.icu"

#---------------------------------------------
#  OPEN report helper
#----------------------------------------------

def open_report(path):
    if os.getenv("OPEN_REPORT", "1") == "1":
        try:
            webbrowser.open(Path(path).resolve().as_uri())
        except Exception:
            pass


# ─────────────────────────────────────────────
# PREFETCH HELPER — Cloudflare Worker Schema
# ─────────────────────────────────────────────
def fetch_remote_report(
    report_type,
    staging=False,
    gpt=False,
    provider=None,
    model=None,
    start=None,
    end=None,
    strava_test=False,
    lite=False,
    overview=False,
    workflow=False
):
    """
    Fetch a URF report (semantic+markdown) from Cloudflare Worker.
    If GPT rendering is enabled (?render=gpt), the Worker now returns both
    markdown and semantic JSON in a single JSON envelope.
    """
    worker_base = get_worker_base(staging)
    base = f"{worker_base}/run_{report_type}"
    # Build query params
    params = []
    if gpt:
        params.append("render=gpt")

        if provider:
            params.append(f"provider={provider}")

        if model:
            params.append(f"model={model}")
    if start:
        params.append(f"start={start}")
    if end:
        params.append(f"end={end}")
    if strava_test:
        # Accept: stub, 1–5
        if strava_test == "stub":
            params.append("test=strava-stub")
        elif strava_test == "demo":
            params.append("test=demo")
        elif strava_test in ["0","1", "2", "3", "4", "5"]:
            params.append(f"test=strava{strava_test}")
        else:
            raise ValueError(
                "Invalid --strava-test value. Use: stub, demo, 0,1,2,3,4,5"
            )
    if overview:
        params.append("overview=true")
    elif lite:
        params.append("lite=true")
    elif workflow:
        params.append("workflow=true")

    query = "&".join(params)
    url = f"{base}?{query}" if query else base

    # ------------------------------------------------
    # 🔒 EARLY HALT — GPT requires internal auth
    # ------------------------------------------------
    if gpt:
        internal_key = os.getenv("MONTIS_INTERNAL_KEY")

        if not internal_key:
            raise RuntimeError(
                "[CONFIG ERROR] --gpt requested but MONTIS_INTERNAL_KEY is not set.\n"
                "Set it via:\n"
                "bash: export MONTIS_INTERNAL_KEY=\"your_key\""
            )
    headers = {
        "Authorization": f"Bearer {os.getenv('ICU_OAUTH', '')}",
        "x-montis-internal": os.getenv("MONTIS_INTERNAL_KEY"),
        "User-Agent": "IntervalsGPTCoachLocal/1.0"
    }

    env = "staging" if staging else "prod"
    print(f"[REMOTE] env={env} report={report_type} gpt={gpt}")
    print(f"[REMOTE] → {url}")

    resp = requests.get(url, headers=headers, timeout=120)

    print(f"[REMOTE] HTTP {resp.status_code}")

    # Only crash for true server failures
    if resp.status_code >= 500:
        resp.raise_for_status()

    content_type = resp.headers.get("content-type", "")

    # Try to parse JSON if possible
    try:
        data = resp.json()
        data["_trace"] = {
            "worker_url": url,
            "type": "REMOTE"
        }
    except Exception:
        # Surface Worker error text instead of crashing
        text = resp.text
        print("[REMOTE] Non-JSON response from Worker:")
        print(text)
        return {"status": "error", "raw": text}

    Path("reports").mkdir(exist_ok=True)
    env_tag = "staging" if staging else "prod"

    content_type = resp.headers.get("content-type", "")

    # 🔥 Handle unified JSON payload (markdown + semantic)
    if "application/json" in content_type:

        markdown = data.get("markdown")
        semantic = data.get("semantic_graph")
        # --- Token estimate ---
        if semantic:
            token_count = estimate_tokens_from_json(semantic)
            if token_count:
                print(f"[TOKENS][REMOTE] semantic_graph = {token_count:,}")


        mode = "prefetch"
        env_tag = "staging" if staging else "prod"

        # ------------------------------------------------
        # Write semantic JSON (always if present)
        # ------------------------------------------------
        if semantic:

            json_out = f"report_{report_type}_{mode}_{env_tag}_semantic.json"
            json_path = Path("reports") / json_out

            json_path.write_text(
                json.dumps(semantic, indent=2),
                encoding="utf-8"
            )

            print(f"[REMOTE] ✅ Semantic JSON saved → {json_out}")
            open_report(json_path)

        # ------------------------------------------------
        # Write markdown if GPT requested
        # ------------------------------------------------
        if gpt:

            md_out = f"report_{report_type}_{mode}_{env}_gpt_{provider}_{model}.md"
            md_path = Path("reports") / md_out

            if markdown:
                md_path.write_text(markdown, encoding="utf-8")
                print(f"[REMOTE] ✅ Markdown saved → {md_out}")
            else:
                md_path.write_text(
                    "# LLM render unavailable\n\n"
                    "The worker did not return markdown.\n"
                    "Check semantic JSON for details.",
                    encoding="utf-8"
                )
                print(f"[REMOTE] ⚠️ Markdown missing — placeholder written → {md_out}")

            open_report(md_path)

        return data

    # Legacy markdown-only fallback
    if "text/markdown" in content_type:
        text = resp.text
        md_out = f"report_{report_type}_prefetch_{env_tag}_gpt.md"
        Path(f"reports/{md_out}").write_text(text, encoding="utf-8")
        print(f"[REMOTE] ✅ Markdown saved (legacy) → {md_out}")
        return {"markdown": text, "status": resp.status_code}

    # Default JSON flow (no GPT)

    json_out = f"report_{report_type}_prefetch_{env_tag}_semantic.json"
    Path(f"reports/{json_out}").write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[REMOTE] ✅ Semantic JSON saved → {json_out}")
    return data


# ─────────────────────────────────────────────
# DEBUG REPORTS
# ─────────────────────────────────────────────
def fetch_debug_report(report_type, staging=False, prefetch=False):
    """
    Fetch debug report via Cloudflare Worker (prefetch + debug routing).
    Splits semantic report and debug logs into separate files.
    """

    worker_base = get_worker_base(staging)
    url = f"{worker_base}/run_{report_type}?debug=true&format=semantic"

    headers = {
        "Authorization": f"Bearer {os.getenv('ICU_OAUTH', '')}",
        "X-Montis-Internal": os.getenv("MONTIS_INTERNAL_KEY"),
        "User-Agent": "IntervalsGPTCoachLocal/1.0"
    }

    env = "staging" if staging else "prod"

    print(f"[DEBUG] env={env} report={report_type}")
    print(f"[DEBUG] → {url}")

    resp = requests.get(url, headers=headers, timeout=120)
    resp.raise_for_status()

    data = resp.json()
    data["_trace"] = {
        "worker_url": url,
        "type": "DEBUG"
    }

    Path("reports").mkdir(exist_ok=True)

    # ------------------------------------------------
    # Extract components
    # ------------------------------------------------
    logs = data.get("logs", "")
    semantic = data.get("semantic_graph", {})

    report_payload = {
        "status": data.get("status"),
        "report_type": data.get("report_type"),
        "semantic_graph": semantic,
        "compliance": data.get("compliance", {}),
        "_trace": data.get("_trace")
    }

  # ------------------------------------------------
    # Save semantic report
    # ------------------------------------------------
    mode = "prefetch" if prefetch else "local"

    json_name = f"report_{report_type}_{mode}_{env}_debug.json"
    json_path = Path("reports") / json_name

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_payload, f, indent=2)

    print(f"[DEBUG] ✅ Semantic report saved → {json_name}")
    open_report(json_path)

    # ------------------------------------------------
    # Save logs separately
    # ------------------------------------------------
    log_name = f"report_{report_type}_{mode}_{env}_debug.log"
    log_path = Path("reports") / log_name

    with open(log_path, "w", encoding="utf-8") as f:
        f.write(logs)

    print(f"[DEBUG] 📜 Logs saved → {log_name}")
    open_report(log_path)

    if logs:
        print(f"[DEBUG] 📜 Logs captured: {len(logs.splitlines())} lines")

    return report_payload


def fetch_worker_prefetch_dataset(report_type, staging=False, start=None, end=None):
    """
    Fetch RAW dataset from Worker (NOT report).
    Worker must return prefetched payload.
    """

    worker_base = get_worker_base(staging)
    url = f"{worker_base}/run_{report_type}?prefetch=true"

    if start:
        url += f"&start={start}"
    if end:
        url += f"&end={end}"

    token = os.getenv("ICU_OAUTH")

    if not token:
        raise RuntimeError("ICU_OAUTH not set")

    token = token.strip()

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "IntervalsGPTCoachLocal/1.0"
    }

    print("[AUTH OK]", token[:12], "...")

    print(f"[PREFETCH] → {url}")

    resp = requests.get(url, headers=headers, timeout=120)
    resp.raise_for_status()

    data = resp.json()

    data["_trace"] = {
        "worker_url": url,
        "type": "PREFETCH"
    }

    return data

# ─────────────────────────────────────────────
# PREFETCH HELPER — Cloudflare Worker Schema
# ─────────────────────────────────────────────
def generate_full_report(
    report_type="weekly",
    output_path=None,
    output_format="markdown",
    prefetch=False,
    staging=False,
    start=None,
    end=None,
    gpt=False,
    provider=None,
    model=None,
    strava_test=False,
    debug_mode=False,
    lite=False,
    overview=False,
    workflow=False
):
    buffer = io.StringIO()
    logs = ""
    os.environ["REPORT_TYPE"] = report_type.lower()
    Path("reports").mkdir(parents=True, exist_ok=True)

    # ============================================================
    # 🌐 REMOTE MODE — Worker → Railway
    # ============================================================
    if prefetch:
        print(f"[PREFETCH] Using Worker prehydrated report (staging={staging}, gpt={gpt})")

        data = fetch_remote_report(
            report_type,
            staging=staging,
            gpt=gpt,
            provider=provider,
            model=model,
            start=start,
            end=end,
            strava_test=strava_test,
            lite=lite,
            overview=overview,
            workflow=workflow
        )

        if gpt:
            print("[GPT] ✅ Worker already saved Markdown + Semantic JSON")

            # still return trace for UI/debug visibility
            return {
                "status": "ok",
                "_trace": data.get("_trace"),
                "mode": "gpt_prefetch"
            }

        if data.get("status") != "ok":
            full_output = data
        else:
            log_output = data.get("logs", "")
            semantic = data.get("semantic_graph", {})

            full_output = {
                "status": data.get("status", "ok"),
                "message": data.get("message", f"{report_type.title()} report (prefetched)"),
                "error_type": data.get("error_type"),
                "severity": data.get("severity"),
                "semantic_graph": semantic,
                "logs": log_output,
                "_trace": data.get("_trace")
            }

    # ============================================================
    # 💻 LOCAL MODE — Worker prefetch dataset → local run_report
    # ============================================================
    else:
        print("[LOCAL] Running LOCAL compute with Worker dataset")

        dataset = fetch_worker_prefetch_dataset(
            report_type,
            staging=staging,
            start=start,
            end=end
        )
        trace = dataset.get("_trace")
        # --------------------------------------------------------
        # 🔧 NORMALISE (same as Railway)
        # --------------------------------------------------------
        prefetch_context = normalize_prefetched_context(dataset)

        # --------------------------------------------------------
        # 🔑 Inject required execution keys
        # --------------------------------------------------------

        prefetch_context = dict(prefetch_context)
        prefetch_context["prefetch_done"] = True

        # --------------------------------------------------------
        # 🗓️ LOCAL CLI WINDOW OVERRIDE
        # Worker received --start/--end, but local run_report also
        # needs the range in context or it defaults to today.
        # --------------------------------------------------------
        if start:
            
            start_dt = pd.to_datetime(start)

            if end:
                end_dt = pd.to_datetime(end)
            elif report_type == "weekly":
                end_dt = start_dt + pd.Timedelta(days=6)
            else:
                end_dt = start_dt

            prefetch_context["range"] = {
                "light_start": start_dt.strftime("%Y-%m-%d"),
                "light_end": end_dt.strftime("%Y-%m-%d"),
                "full_start": start_dt.strftime("%Y-%m-%d"),
                "full_end": end_dt.strftime("%Y-%m-%d"),
                "lightDays": 90 if report_type == "weekly" else 365,
                "fullDays": 7,
                "wellnessDays": 42,
                "custom": True,
                "chunk": False,
            }

            prefetch_context["window_start"] = start_dt.strftime("%Y-%m-%d")
            prefetch_context["window_end"] = end_dt.strftime("%Y-%m-%d")

            print(
                f"[LOCAL-RANGE] forced run_report window "
                f"{prefetch_context['range']['light_start']} → "
                f"{prefetch_context['range']['light_end']}"
            )

        # --------------------------------------------------------
        # 🧯 LOCAL PREFETCH REPAIR
        # Full-detail rows can exist but miss canonical totals.
        # Merge canonical load/time/distance from LIGHT rows by id.
        # This mirrors the Railway-safe path and prevents Tier-1
        # seeing 8 events but 0 h / 0 TSS.
        # --------------------------------------------------------

        def _repair_full_from_light(ctx: dict) -> dict:
            df_full = ctx.get("df_master")
            df_light = ctx.get("df_light")

            if not isinstance(df_full, pd.DataFrame) or df_full.empty:
                return ctx

            if not isinstance(df_light, pd.DataFrame) or df_light.empty:
                return ctx

            if "id" not in df_full.columns or "id" not in df_light.columns:
                return ctx

            canonical_cols = [
                "moving_time",
                "distance",
                "icu_training_load",
                "icu_atl",
                "icu_ctl",
                "icu_intensity",
                "average_heartrate",
                "VO2MaxGarmin",
            ]

            light_cols = ["id"] + [c for c in canonical_cols if c in df_light.columns]
            if len(light_cols) <= 1:
                return ctx

            before_tss = (
                pd.to_numeric(df_full.get("icu_training_load", 0), errors="coerce")
                .fillna(0)
                .sum()
                if "icu_training_load" in df_full.columns
                else 0
            )

            before_hours = (
                pd.to_numeric(df_full.get("moving_time", 0), errors="coerce")
                .fillna(0)
                .sum() / 3600
                if "moving_time" in df_full.columns
                else 0
            )

            # Only repair when full rows exist but totals are zero/broken.
            if before_tss > 0 and before_hours > 0:
                return ctx

            light_fix = df_light[light_cols].copy()

            merged = df_full.merge(
                light_fix,
                on="id",
                how="left",
                suffixes=("", "_light")
            )

            for c in canonical_cols:
                lc = f"{c}_light"
                if lc not in merged.columns:
                    continue

                if c not in merged.columns:
                    merged[c] = merged[lc]
                else:
                    base = pd.to_numeric(merged[c], errors="coerce")
                    repl = pd.to_numeric(merged[lc], errors="coerce")
                    merged[c] = base.where(base.fillna(0) > 0, repl)

                merged.drop(columns=[lc], inplace=True, errors="ignore")

            after_tss = (
                pd.to_numeric(merged.get("icu_training_load", 0), errors="coerce")
                .fillna(0)
                .sum()
                if "icu_training_load" in merged.columns
                else 0
            )

            after_hours = (
                pd.to_numeric(merged.get("moving_time", 0), errors="coerce")
                .fillna(0)
                .sum() / 3600
                if "moving_time" in merged.columns
                else 0
            )

            ctx["df_master"] = merged
            ctx["_df_scope_full"] = merged.copy()
            ctx["activities_full"] = merged.to_dict(orient="records")

            # Rebuild Tier-1 snapshot from repaired full dataset.
            ctx["snapshot_7d_json"] = merged.to_dict(orient="records")
            ctx["tier0_snapshotTotals_7d"] = {
                "tss": float(after_tss),
                "hours": float(after_hours),
                "distance_km": (
                    float(pd.to_numeric(merged.get("distance", 0), errors="coerce").fillna(0).sum()) / 1000
                    if "distance" in merged.columns
                    else 0
                ),
                "sessions": int(len(merged)),
            }

            print(
                f"[LOCAL-REPAIR] full totals repaired from light: "
                f"TSS {before_tss:.1f} → {after_tss:.1f}, "
                f"hours {before_hours:.2f} → {after_hours:.2f}"
            )

            return ctx

        prefetch_context = _repair_full_from_light(prefetch_context)

        def _is_empty_dataset(x):
            return (
                x is None or
                (isinstance(x, list) and len(x) == 0) or
                (isinstance(x, pd.DataFrame) and x.empty)
            )


        light = prefetch_context.get("activities_light")
        full = prefetch_context.get("activities_full")

        light_empty = _is_empty_dataset(light)
        full_empty = _is_empty_dataset(full)

        if report_type == "weekly" and not light_empty and full_empty:
            last_date = None

            try:
                dates = [
                    pd.to_datetime(a.get("start_date_local"))
                    for a in light
                    if isinstance(a, dict) and a.get("start_date_local")
                ]
                if dates:
                    last_date = max(dates)
            except Exception:
                pass

            if last_date is not None:
                last_date_str = last_date.strftime("%Y-%m-%d")
                suggested_start = (last_date - pd.Timedelta(days=6)).strftime("%Y-%m-%d")

                raise AuditHalt(
                    (
                        f"No weekly full-detail activities were retrieved for this period. "
                        f"Last light activity seen is {last_date_str}. "
                        f"Try: --start {suggested_start} --end {last_date_str}"
                    ),
                    code="FULL_DATA_UNAVAILABLE",
                    severity="info"
                )

            raise AuditHalt(
                "No weekly full-detail activities were retrieved for this period.",
                code="FULL_DATA_UNAVAILABLE",
                severity="info"
            )

        if light_empty and full_empty:
            raise AuditHalt(
                "No activity data found for this period.",
                code="NO_ACTIVITY_DATA",
                severity="info"
            )

        # --------------------------------------------------------
        # 🧠 SINGLE LOCAL PIPELINE EXECUTION
        # --------------------------------------------------------
        run_kwargs = dict(
            reportType=report_type,
            include_coaching_metrics=True,
            output_format=output_format,
            render_mode="workflow" if workflow else "overview" if overview else "lite" if lite else "full+metrics",
            **prefetch_context
        )

        try:
            if debug_mode:
                with redirect_stdout(buffer):
                    result = run_report(**run_kwargs)
                logs = buffer.getvalue()
            else:
                result = run_report(**run_kwargs)
                logs = ""

        except AuditHalt as e:
            logs = buffer.getvalue() if debug_mode else ""

            result = {
                "status": "halted",
                "code": getattr(e, "code", "AUDIT_HALT"),
                "severity": getattr(e, "severity", "info"),
                "message": str(e),
                "_trace": trace,
            }

            if output_format == "semantic_json":
                return result

            print(result["message"])
            return result

        raw_logs = logs.splitlines()
        skip_terms = ["snapshot", "trace", "json", "context", "activities_full", "DataFrame"]

        log_output = "\n".join(
            [line for line in raw_logs if not any(term in line.lower() for term in skip_terms)]
        ).strip()

        if isinstance(result, tuple):
            report, summary = result
        else:
            report = result

        if isinstance(report, dict):

            if output_format == "semantic":
                semantic_output = report.get("semantic_graph", {})

                token_count = estimate_tokens_from_json(semantic_output)
                if token_count:
                    print(f"[TOKENS][LOCAL] semantic_graph = {token_count:,}")

                full_output = {
                    "status": "ok",
                    "message": f"{report_type.title()} report generated (local)",
                    "semantic_graph": semantic_output,
                    "_debug": {
                        "tokens": token_count,
                    "_trace": trace
                    }
                }

            else:
                md_output = report.get("markdown", "")

                full_output = (
                    f"# 🧾 {report_type.title()} Audit Report\n\n"
                    f"🗓️ Date Range: {start} → {end}\n\n" if start and end else ""
                ) + (
                    "## Execution Logs\n\n"
                    "```\n" + log_output + "\n```\n\n"
                    "## Rendered Markdown Report\n\n"
                    + md_output.strip()
                )

        else:
            full_output = {"markdown": str(report), "logs": log_output}

    # ============================================================
    # 💾 FILE WRITING (UNCHANGED)
    # ============================================================
    if prefetch and gpt:
        print("[SAFEGUARD] 🛑 Prefetch GPT detected — skipping local file writing entirely.")
        return None

    mode = "prefetch" if prefetch else "local"
    env_tag = "staging" if staging else "prod"
    gpt_tag = "_gpt" if gpt else ""

    base_name = f"report_{report_type}_{mode}_{env_tag}{gpt_tag}_{output_format}"

    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    if output_format == "semantic":
        out_path = reports_dir / f"{base_name}.json"

        def json_default(obj):
            import datetime as dt
            import numpy as np

            if isinstance(obj, (pd.Timestamp, dt.date, dt.datetime)):
                return obj.isoformat()

            if isinstance(obj, np.integer):
                return int(obj)

            if isinstance(obj, np.floating):
                return float(obj)

            if isinstance(obj, np.ndarray):
                return obj.tolist()

            return str(obj)

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(full_output, f, indent=2, default=json_default)

        print(f"[LOCAL] ✅ Saved semantic JSON → {out_path}")

    else:
        out_path = reports_dir / f"{base_name}.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(full_output)
        print(f"[LOCAL] ✅ Saved markdown report → {out_path}")

    open_report(out_path)

    return full_output

# ─────────────────────────────────────────────
# CLI ENTRY POINT
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Generate audit reports for different data ranges.")
    parser.add_argument("--range", type=str.lower,
                        choices=["weekly", "season", "wellness", "summary", "data_quality"],
                        default="weekly")
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--format", type=str.lower,
                        choices=["markdown", "semantic"],
                        default="semantic",
                        help="Output format (default: semantic)")
    parser.add_argument("--prefetch", action="store_true",
                        help="Use prehydrated dataset from Railway proxy (via Worker)")
    parser.add_argument("--staging", action="store_true",
                        help="Request staging environment (Worker will decide access)")
    parser.add_argument("--start", type=str, help="Custom start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, help="Custom end date (YYYY-MM-DD)")
    parser.add_argument("--gpt", action="store_true",
                        help="Request GPT-rendered report from Cloudflare Worker (adds ?render=gpt)")
    parser.add_argument("--provider", type=str,
                        choices=["openai","anthropic","google"],
                        help="LLM provider")
    parser.add_argument("--model", type=str,
                        help="LLM model")    
    parser.add_argument("--debug", action="store_true",
                        help="Run any report type in debug mode (via Railway /debug endpoint if available)")
    parser.add_argument(
        "--strava-test",
        type=str,
        choices=["stub", "demo", "0", "1", "2", "3", "4", "5"],
        help=(
            "Simulate Strava-only scenarios:\n"
            "  stub → all activities are STRAVA API stubs (hard stop)\n"
            "  0    -> light and full empty - no data at all "
            "  1    → light-only dataset, no full activities\n"
            "  2    → full dataset empty after filtering\n"
            "  3    → activities present but missing key metrics\n"
            "  4    → partial wellness or athlete metadata\n"
            "  5    → mixed valid + stub activities (degraded state)"
            "  demo → demo"
        ),
    )
    parser.add_argument(
        "--lite",
        action="store_true",
        help="Run weekly report in lite mode (reduced semantic contract)"
    )
    parser.add_argument(
        "--overview",
        action="store_true",
        help="Run weekly report in overview mode (compact Bento-style semantic contract)"
    )
    parser.add_argument(
        "--workflow",
        action="store_true",
        help="Run weekly report in workflow mode"
    )
    
    args = parser.parse_args()

    if args.overview and args.lite:
        print("[CLI] --overview selected; ignoring --lite")
        args.lite = False

    if args.workflow and args.lite:
        print("[CLI] --workflow selected; ignoring --lite")
        args.lite = False

    # 🧠 Debug + Prefetch → run BOTH (semantic + debug)
    if args.debug and args.prefetch:

        os.environ["PREFETCH_MODE"] = "1"

        print(f"[CLI] 🧠 Prefetch debug mode for '{args.range}' (staging={args.staging})")

        # 1️⃣ ALWAYS create semantic report
        generate_full_report(
            report_type=args.range,
            output_path=args.output,
            output_format=args.format,
            prefetch=args.prefetch,
            staging=args.staging,
            start=args.start,
            end=args.end,
            gpt=args.gpt,
            provider=args.provider,
            model=args.model,
            strava_test=args.strava_test,
            debug_mode=False,   
            lite=args.lite,
            overview=args.overview,
            workflow=args.workflow
        )

        # 2️⃣ THEN fetch debug logs
        fetch_debug_report(
            args.range,
            staging=args.staging,
            prefetch=args.prefetch
        )

        return


    # 🧩 Normal flow
    generate_full_report(
        report_type=args.range,
        output_path=args.output,
        output_format=args.format,
        prefetch=args.prefetch,
        staging=args.staging,
        start=args.start,
        end=args.end,
        gpt=args.gpt,
        provider=args.provider,
        model=args.model,
        strava_test=args.strava_test,
        debug_mode=args.debug,
        lite=args.lite,
        overview=args.overview,
        workflow=args.workflow
    )

if __name__ == "__main__":
    main()
