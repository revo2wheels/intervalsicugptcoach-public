# ─────────────────────────────────────────────
# 📡 Railway Deployment API Endpoints
# Base URL: https://intervalsicugptcoach-public-production.up.railway.app
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# 📡 Railway Deployment API Endpoints
# Base URL: https://intervalsicugptcoach-public-production.up.railway.app
# ─────────────────────────────────────────────

# ROOT
# https://intervalsicugptcoach-public-production.up.railway.app/

# ENV DEBUG
# https://intervalsicugptcoach-public-production.up.railway.app/debug_env

# MAIN RUN ENDPOINTS (markdown, json, semantic)
# https://intervalsicugptcoach-public-production.up.railway.app/run?range=weekly&format=markdown
# https://intervalsicugptcoach-public-production.up.railway.app/run?range=weekly&format=semantic
# https://intervalsicugptcoach-public-production.up.railway.app/run?range=weekly&format=json

# https://intervalsicugptcoach-public-production.up.railway.app/run?range=season&format=markdown
# https://intervalsicugptcoach-public-production.up.railway.app/run?range=season&format=semantic
# https://intervalsicugptcoach-public-production.up.railway.app/run?range=season&format=json

# https://intervalsicugptcoach-public-production.up.railway.app/run?range=wellness&format=markdown
# https://intervalsicugptcoach-public-production.up.railway.app/run?range=wellness&format=semantic
# https://intervalsicugptcoach-public-production.up.railway.app/run?range=wellness&format=json

# https://intervalsicugptcoach-public-production.up.railway.app/run?range=summary&format=markdown
# https://intervalsicugptcoach-public-production.up.railway.app/run?range=summary&format=semantic
# https://intervalsicugptcoach-public-production.up.railway.app/run?range=summary&format=json

# DEBUG ENDPOINT (logs + markdown OR semantic)
# https://intervalsicugptcoach-public-production.up.railway.app/debug?range=weekly&format=markdown
# https://intervalsicugptcoach-public-production.up.railway.app/debug?range=weekly&format=semantic

# https://intervalsicugptcoach-public-production.up.railway.app/debug?range=season&format=markdown
# https://intervalsicugptcoach-public-production.up.railway.app/debug?range=season&format=semantic

# https://intervalsicugptcoach-public-production.up.railway.app/debug?range=wellness&format=markdown
# https://intervalsicugptcoach-public-production.up.railway.app/debug?range=wellness&format=semantic

# https://intervalsicugptcoach-public-production.up.railway.app/debug?range=summary&format=markdown
# https://intervalsicugptcoach-public-production.up.railway.app/debug?range=summary&format=semantic

# SEMANTIC REPORT (semantic JSON)
# https://intervalsicugptcoach-public-production.up.railway.app/semantic?range=weekly
# https://intervalsicugptcoach-public-production.up.railway.app/semantic?range=season
# https://intervalsicugptcoach-public-production.up.railway.app/semantic?range=wellness
# https://intervalsicugptcoach-public-production.up.railway.app/semantic?range=summary

# METRICS ONLY
# https://intervalsicugptcoach-public-production.up.railway.app/metrics?range=weekly
# https://intervalsicugptcoach-public-production.up.railway.app/metrics?range=season
# https://intervalsicugptcoach-public-production.up.railway.app/metrics?range=wellness
# https://intervalsicugptcoach-public-production.up.railway.app/metrics?range=summary

# PHASES (Periodisation)
# https://intervalsicugptcoach-public-production.up.railway.app/phases?range=weekly
# https://intervalsicugptcoach-public-production.up.railway.app/phases?range=season
# https://intervalsicugptcoach-public-production.up.railway.app/phases?range=wellness
# https://intervalsicugptcoach-public-production.up.railway.app/phases?range=summary

# COMPARE (trend/delta metrics)
# https://intervalsicugptcoach-public-production.up.railway.app/compare?range=weekly
# https://intervalsicugptcoach-public-production.up.railway.app/compare?range=season
# https://intervalsicugptcoach-public-production.up.railway.app/compare?range=wellness
# https://intervalsicugptcoach-public-production.up.railway.app/compare?range=summary

# INSIGHTS (AI-ready coaching flags)
# https://intervalsicugptcoach-public-production.up.railway.app/insights?range=weekly
# https://intervalsicugptcoach-public-production.up.railway.app/insights?range=season
# https://intervalsicugptcoach-public-production.up.railway.app/insights?range=wellness
# https://intervalsicugptcoach-public-production.up.railway.app/insights?range=summary


from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
import io, os, sys, json
from contextlib import redirect_stdout

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "audit_core"))

# Core audit pipeline
from audit_core.report_controller import run_report
from audit_core.utils import debug

# Semantic JSON builder
from semantic_json_builder import build_semantic_json
from athlete_profile import map_icu_athlete_to_profile


print("[DEBUG] Starting IntervalsICU GPTCoach API")
icuoauth = os.getenv("ICU_OAUTH")
if icuoauth:
    print("[DEBUG] ICU_OAUTH ENV VAR detected:", icuoauth[:20], "...")
else:
    print("[WARN] ICU_OAUTH ENV VAR missing — Intervals.icu calls may fail!")

app = FastAPI(title="IntervalsICU GPTCoach API", version="1.3")


# ─────────────────────────────────────────────
#  SANITISER — FINAL VERSION
# ─────────────────────────────────────────────
def sanitize(obj, seen=None):
    """
    Safe JSON sanitation:
    - prevents recursion
    - handles pandas, numpy, timestamps
    - normalises NaN/Inf
    - ONLY marks circular on containers
    """
    import math
    import pandas as pd
    import numpy as np
    from datetime import datetime, date

    # ----- PRIMITIVES -----
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return None
        return obj

    # ----- DATETIME -----
    if isinstance(obj, (datetime, date, pd.Timestamp)):
        try:
            return obj.isoformat()
        except:
            return str(obj)

    # ----- NUMPY -----
    if isinstance(obj, (np.integer, np.floating)):
        return float(obj)

    # ----- INIT SEEN -----
    if seen is None:
        seen = set()

    container_types = (dict, list, tuple, pd.DataFrame, pd.Series)

    if isinstance(obj, container_types):
        oid = id(obj)
        if oid in seen:
            return "<circular>"
        seen.add(oid)

    # ----- PANDAS -----
    if isinstance(obj, pd.DataFrame):
        return sanitize(obj.to_dict(orient="records"), seen)

    if isinstance(obj, pd.Series):
        return sanitize(obj.to_dict(), seen)

    # ----- DICT -----
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            out[sanitize(k, seen)] = sanitize(v, seen)
        return out

    # ----- LIST / TUPLE -----
    if isinstance(obj, (list, tuple)):
        return [sanitize(i, seen) for i in obj]

    # ----- FALLBACK -----
    return str(obj)


# ─────────────────────────────────────────────
#  RUN FULL AUDIT — CLEAN VERSION
# ─────────────────────────────────────────────
def _run_full_audit(range: str, output_format="markdown", prefetch_context=None):

    os.environ["REPORT_TYPE"] = range.lower()
    buffer = io.StringIO()

    with redirect_stdout(buffer):
        if prefetch_context:
            report, compliance = run_report(
                reportType=range,
                output_format=output_format,
                include_coaching_metrics=True,
                **prefetch_context
            )
        else:
            report, compliance = run_report(
                reportType=range,
                output_format=output_format,
                include_coaching_metrics=True
            )

    logs = buffer.getvalue()

    if isinstance(report, dict):
        context = report.get("context", {}) or {}
        markdown = report.get("markdown", "")
    else:
        context = {}
        markdown = str(report)

    # -----------------------------------------------------------------
    # 🔧 Force semantic builder options (verbose event listing, etc.)
    # -----------------------------------------------------------------
    context["render_options"] = {
        "verbose_events": True,
        "include_all_events": True,
        "return_format": "markdown",  # or "semantic"
    }

    # Build semantic graph (after options injected)
    semantic_graph = build_semantic_json(context)


    return report, compliance, logs, context, semantic_graph, markdown



# ─────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "IntervalsICU GPTCoach API running 🚴"}


# -----------------------------
# GET /run (markdown / semantic) / CURL / DIRECT
# -----------------------------
@app.get("/run")
def run_audit(
    range: str = Query("weekly", enum=["weekly", "season", "wellness", "summary"]),
    format: str = Query("markdown", enum=["markdown", "json", "semantic"]),
):
    try:
        report, compliance, logs, context, sg, markdown = _run_full_audit(
            range=range,
            output_format=format.lower()
        )

        if format.lower() in ("json", "semantic"):
            return JSONResponse(content={
                "status": "ok",
                "report_type": range,
                "output_format": "semantic_json",
                "semantic_graph": sanitize(sg),
                "compliance": compliance,
                "logs": logs[:20000]
            })

        return JSONResponse(content={
            "status": "ok",
            "report_type": range,
            "output_format": "markdown",
            "markdown": markdown,
            "compliance": compliance,
            "logs": logs[:20000]
        })

    except Exception as e:
        return error_response(e)

# --- HELPER FOR LIST ----
def require_list(name, value):
    if value is None:
        return None
    if isinstance(value, list):
        return value
    raise ValueError(f"{name} must be a list, got {type(value).__name__}")


# -----------------------------
# POST /run (Worker / ChatGPT mode)
# -----------------------------
@app.post("/run")
async def run_audit_with_data(request: Request):
    buffer = io.StringIO()

    try:
        raw = await request.body()
        if not raw:
            raise ValueError("Empty request body received")

        try:
            data = json.loads(raw)
        except Exception as e:
            raise ValueError(f"JSON parse failed: {e}, raw={raw[:200]}")

        report_range = data.get("range", "weekly")
        fmt = data.get("format", "markdown").lower()

        # -----------------------------
        # Canonical prefetch builder
        # -----------------------------
        prefetch_context = {}

        def require_list(name, value):
            if value is None:
                return None
            if isinstance(value, list):
                return value
            raise ValueError(f"{name} must be a list, got {type(value).__name__}")

        # Activities
        activities_light = require_list("activities_light", data.get("activities_light"))
        activities_full  = require_list("activities_full",  data.get("activities_full"))
        wellness          = require_list("wellness",          data.get("wellness"))
        calendar          = require_list("calendar",          data.get("calendar"))

        if activities_light:
            prefetch_context["activities_light"] = activities_light
        if activities_full:
            prefetch_context["activities_full"] = activities_full
        if wellness:
            prefetch_context["wellness"] = wellness
        if calendar:
            prefetch_context["calendar"] = calendar

        # Athlete (FLAT ONLY)
        raw_athlete = data.get("athlete")

        # Accept both nested and flat forms
        if isinstance(raw_athlete, dict):
            # Only unwrap if actually nested
            if "sportSettings" not in raw_athlete and "athlete" in raw_athlete:
                raw_athlete = raw_athlete["athlete"]

            prefetch_context["athlete"] = raw_athlete

            # -------------------------------------------------
            # 🧠 Normalize athlete profile (same as Tier-0 local)
            # -------------------------------------------------
            try:
                from athlete_profile import map_icu_athlete_to_profile

                normalized_profile = map_icu_athlete_to_profile(raw_athlete)
                prefetch_context["athleteProfile"] = normalized_profile

                debug(
                    prefetch_context,
                    f"[RAILWAY] Normalized athleteProfile — ftp={normalized_profile.get('ftp')} "
                    f"indoor_ftp={normalized_profile.get('indoor_ftp')} weight={normalized_profile.get('weight')}"
                )
            except Exception as e:
                debug(prefetch_context, f"[RAILWAY] ⚠️ Failed to normalize athleteProfile: {e}")

        # 🔒 CRITICAL RULE:
        # Empty dict means NO prefetch — force canonical fetch path
        if not prefetch_context:
            prefetch_context = None

        with redirect_stdout(buffer):
            report, compliance = run_report(
                reportType=report_range,
                output_format=fmt,
                include_coaching_metrics=True,
                **(prefetch_context or {})
            )

        logs = buffer.getvalue()

        if fmt in ("json", "semantic"):
            context = report.get("context", {}) if isinstance(report, dict) else {}
            return JSONResponse({
                "status": "ok",
                "report_type": report_range,
                "output_format": "semantic_json",
                # ✅ Use the context returned from _run_full_audit()
                "semantic_graph": sanitize(build_semantic_json(context)),
                "compliance": compliance,
                "logs": logs[-20000:],
            })


        return JSONResponse({
            "status": "ok",
            "report_type": report_range,
            "output_format": "markdown",
            "markdown": report.get("markdown", ""),
            "compliance": compliance,
            "logs": logs[-20000:],
        })

    except Exception as e:
        return error_response(e, buffer)

# -----------------------------
# /ERROR HANDLING
# -----------------------------
def error_response(e: Exception, buffer=None, status_code: int = 500):
    import traceback

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "message": str(e),
            "exception_type": type(e).__name__,
            "trace": traceback.format_exc(),
            "logs": (
                buffer.getvalue()[-20000:]
                if buffer is not None
                else None
            ),
        },
    )


# -----------------------------
# /semantic — full semantic JSON
# -----------------------------
@app.get("/semantic")
def get_semantic(range: str = Query("weekly", enum=["weekly", "season", "wellness", "summary"])):
    _, compliance, logs, _, sg, _ = _run_full_audit(range=range)
    return JSONResponse(content={
        "status": "ok",
        "report_type": range,
        "output_format": "semantic_json",
        "semantic_graph": sanitize(sg),
        "compliance": compliance,
        "logs": logs[:20000]
    })


# -----------------------------
# /metrics — sanitized subgraph
# -----------------------------
@app.get("/metrics")
def get_metrics(range: str = Query("weekly", enum=["weekly", "season", "wellness", "summary"])):
    _, compliance, logs, _, sg, _ = _run_full_audit(range=range)
    return JSONResponse(content={
        "status": "ok",
        "report_type": range,
        "metrics": sanitize(sg.get("metrics", {})),
        "extended_metrics": sanitize(sg.get("extended_metrics", {})),
        "trend_metrics": sanitize(sg.get("trend_metrics", {})),
        "adaptation_metrics": sanitize(sg.get("adaptation_metrics", {})),
        "correlation_metrics": sanitize(sg.get("correlation_metrics", {})),
        "compliance": compliance,
        "logs": logs[:20000]
    })


# -----------------------------
# /phases — sanitized
# -----------------------------
@app.get("/phases")
def get_phases(range: str = Query("weekly", enum=["weekly", "season", "wellness", "summary"])):
    _, compliance, logs, _, sg, _ = _run_full_audit(range=range)
    return JSONResponse(content={
        "status": "ok",
        "report_type": range,
        "phases": sanitize(sg.get("phases", [])),
        "actions": sanitize(sg.get("actions", [])),
        "compliance": compliance,
        "logs": logs[:20000]
    })


# -----------------------------
# /compare — sanitized
# -----------------------------
@app.get("/compare")
def compare_periods(range: str = Query("weekly", enum=["weekly", "season", "wellness", "summary"])):
    _, compliance, logs, _, sg, _ = _run_full_audit(range=range)
    return JSONResponse(content={
        "status": "ok",
        "report_type": range,
        "trend_metrics": sanitize(sg.get("trend_metrics", {})),
        "core_metrics": sanitize(sg.get("metrics", {})),
        "compliance": compliance,
        "logs": logs[:20000]
    })


# -----------------------------
# /insights — sanitized
# -----------------------------
@app.get("/insights")
def get_insights(range: str = Query("weekly", enum=["weekly", "season", "wellness", "summary"])):
    _, compliance, logs, _, sg, _ = _run_full_audit(range=range)

    return JSONResponse(content={
        "status": "ok",
        "report_type": range,
        "insights": sanitize(sg.get("insight_view", {})),
        "compliance": compliance,
        "logs": logs[:20000]
    })


