from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
import io, os, sys, json
from contextlib import redirect_stdout

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "audit_core"))

from audit_core.report_controller import run_report
from audit_core.utils import debug
from semantic_json_builder import build_semantic_json

import pandas as pd
from datetime import datetime, date

print("[DEBUG] Starting IntervalsICU GPTCoach API")
icuoauth = os.getenv("ICU_OAUTH")
if icuoauth:
    print("[DEBUG] ICU_OAUTH ENV VAR detected:", icuoauth[:20], "...")
else:
    print("[WARN] ICU_OAUTH ENV VAR missing — Intervals.icu calls may fail!")

app = FastAPI(title="IntervalsICU GPTCoach API", version="1.3")


def sanitize(obj, seen=None):
    import math, numpy as np

    if isinstance(obj, (str, int, float, bool)) or obj is None:
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return None
        return obj

    if isinstance(obj, (datetime, date, pd.Timestamp)):
        try:
            return obj.isoformat()
        except:
            return str(obj)

    if isinstance(obj, (np.integer, np.floating)):
        return float(obj)

    if seen is None:
        seen = set()

    if isinstance(obj, (dict, list, tuple, pd.DataFrame, pd.Series)):
        oid = id(obj)
        if oid in seen:
            return "<circular>"
        seen.add(oid)

    if isinstance(obj, pd.DataFrame):
        return sanitize(obj.to_dict(orient="records"), seen)
    if isinstance(obj, pd.Series):
        return sanitize(obj.to_dict(), seen)

    if isinstance(obj, dict):
        return {sanitize(k, seen): sanitize(v, seen) for k, v in obj.items()}

    if isinstance(obj, (list, tuple)):
        return [sanitize(i, seen) for i in obj]

    return str(obj)


def normalize_prefetched_context(data):
    def normalize_activities(lst):
        if not isinstance(lst, list):
            return []
        out = []
        for x in lst:
            if not isinstance(x, dict):
                continue
            y = dict(x)
            if "start_date_local" in y:
                try:
                    y["start_date_local"] = pd.to_datetime(y["start_date_local"], errors="coerce").isoformat()
                except Exception:
                    pass
            for k in ("icu_training_load", "IF", "VO2MaxGarmin", "distance", "moving_time", "average_heartrate"):
                if k in y:
                    try:
                        y[k] = float(y[k])
                    except Exception:
                        y[k] = None
            out.append(y)
        return out

    def normalize_wellness(lst):
        if not isinstance(lst, list):
            return []
        out = []
        for x in lst:
            if not isinstance(x, dict):
                continue
            y = dict(x)
            for k in ("fatigue", "form", "sleep", "recovery", "readiness"):
                if k in y:
                    try:
                        y[k] = float(y[k])
                    except Exception:
                        pass
            out.append(y)
        return out

    def normalize_calendar(lst):
        if not isinstance(lst, list):
            return []
        out = []
        for x in lst:
            if not isinstance(x, dict):
                continue
            y = dict(x)
            if "date" in y:
                try:
                    y["date"] = pd.to_datetime(y["date"], errors="coerce").isoformat()
                except Exception:
                    pass
            out.append(y)
        return out

    def normalize_athlete(a):
        if not isinstance(a, dict):
            return {}, {}
        profile = dict(a)
        athlete = {k: v for k, v in a.items() if not isinstance(v, dict)}
        profile.update({
            "zones_power": a.get("zones_power", {}),
            "zones_hr": a.get("zones_hr", {}),
            "ftp": a.get("ftp"),
            "lt1": a.get("lt1"),
            "lt2": a.get("lt2"),
        })
        return athlete, profile

    light = normalize_activities(data.get("activities_light"))
    full = normalize_activities(data.get("activities_full"))
    wellness = normalize_wellness(data.get("wellness"))
    calendar = normalize_calendar(data.get("calendar"))
    athlete, profile = normalize_athlete(data.get("athlete", {}))

    debug({}, f"[NORM] ✅ Normalization summary: light={len(light)}, full={len(full)}, wellness={len(wellness)}, calendar={len(calendar)}, athlete={'ok' if athlete else 'none'}")

    return {
        "activities_light": light,
        "activities_full": full,
        "wellness": wellness,
        "calendar": calendar,
        "athlete": athlete,
        "athleteProfile": profile,
        "prefetch_done": True,
    }


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

    context["render_options"] = {
        "verbose_events": True,
        "include_all_events": True,
        "return_format": "markdown",
    }

    semantic_graph = build_semantic_json(context)

    return report, compliance, logs, context, semantic_graph, markdown


@app.get("/")
def root():
    return {"message": "IntervalsICU GPTCoach API running 🚴"}


@app.get("/run")
def run_audit(range: str = Query("weekly", enum=["weekly", "season", "wellness", "summary"]), format: str = Query("markdown", enum=["markdown", "json", "semantic"])):
    try:
        report, compliance, logs, context, sg, markdown = _run_full_audit(range=range, output_format=format.lower())
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

        prefetch_context = normalize_prefetched_context(data)

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


def error_response(e: Exception, buffer=None, status_code: int = 500):
    import traceback
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "message": str(e),
            "exception_type": type(e).__name__,
            "trace": traceback.format_exc(),
            "logs": (buffer.getvalue()[-20000:] if buffer is not None else None),
        },
    )


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
