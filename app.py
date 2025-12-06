# ─────────────────────────────────────────────
# 📡 Railway Deployment API Endpoints
# Base URL: https://intervalsicugptcoach-public-production.up.railway.app
# ─────────────────────────────────────────────

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
import io, os, sys
from contextlib import redirect_stdout

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "audit_core"))

# Core audit pipeline
from audit_core.report_controller import run_report
from audit_core.utils import debug

# Semantic JSON builder
from semantic_json_builder import build_semantic_json


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
                prefetch_context=prefetch_context
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

    # Build semantic JSON (NO context logging)
    semantic_graph = build_semantic_json(context)

    return report, compliance, logs, context, semantic_graph, markdown


# ─────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "IntervalsICU GPTCoach API running 🚴"}


# -----------------------------
# GET /run (markdown / semantic)
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
        import traceback
        return JSONResponse(status_code=500, content={
            "error": str(e),
            "trace": traceback.format_exc()
        })


# -----------------------------
# POST /run (Worker mode)
# -----------------------------
@app.post("/run")
async def run_audit_with_data(request: Request):
    try:
        data = await request.json()
        range = data.get("range", "weekly")
        fmt = data.get("format", "markdown").lower()

        prefetch_context = {
            "activities_light": data.get("activities_light", []),
            "activities_full": data.get("activities_full", []),
            "wellness": data.get("wellness", []),
            "athlete": data.get("athlete", {}),
        }

        r, compliance, logs, context, sg, markdown = _run_full_audit(
            range=range,
            output_format=fmt,
            prefetch_context=prefetch_context
        )

        if fmt in ("json", "semantic"):
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
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e)
        })


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

    metrics = sg.get("metrics", {})
    actions = sg.get("actions", [])
    phases = sg.get("phases", [])

    red, amber, green = [], [], []

    for name, m in metrics.items():
        cls = m.get("classification")
        entry = sanitize({
            "name": name,
            "value": m.get("value"),
            "framework": m.get("framework"),
            "interpretation": m.get("interpretation"),
            "coaching_implication": m.get("coaching_implication")
        })

        if cls == "red":
            red.append(entry)
        elif cls == "amber":
            amber.append(entry)
        elif cls == "green":
            green.append(entry)

    return JSONResponse(content={
        "status": "ok",
        "report_type": range,
        "insights": {
            "critical": red,
            "watch": amber,
            "positive": green,
            "actions": sanitize(actions),
            "phases": sanitize(phases),
        },
        "compliance": compliance,
        "logs": logs[:20000]
    })

