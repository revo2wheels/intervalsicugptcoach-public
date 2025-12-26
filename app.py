# ─────────────────────────────────────────────
# 📡 Railway Deployment API Endpoints
# Base URL: https://intervalsicugptcoach-public-production.up.railway.app
# ─────────────────────────────────────────────

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
import io, os, sys, json
from contextlib import redirect_stdout
import pandas as pd
import numpy as np
from datetime import datetime, date

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

app = FastAPI(title="IntervalsICU GPTCoach API", version="1.4")

# ─────────────────────────────────────────────
# PREFETCH NORMALIZATION
# ─────────────────────────────────────────────

def normalize_prefetched_context(prefetch_context: dict):
    """Normalize prefetched datasets to match tier0_pre_audit structure."""

    def normalize_dates(df, col_names=("date", "start_date_local", "start_date")):
        for c in col_names:
            if c in df.columns:
                df[c] = pd.to_datetime(df[c], errors="coerce")
        return df

    def normalize_numeric(df, cols=None):
        if cols is None:
            cols = df.columns
        for c in cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="ignore")
        return df

    # --- Wellness normalization ---
    if "wellness" in prefetch_context and isinstance(prefetch_context["wellness"], list):
        df_well = pd.DataFrame(prefetch_context["wellness"])
        df_well = normalize_dates(df_well)
        for col in ("ctl", "atl", "tsb"):
            if col in df_well.columns:
                df_well[col] = pd.to_numeric(
                    df_well[col].apply(
                        lambda v: v.get("value") if isinstance(v, dict) and "value" in v else v
                    ),
                    errors="coerce"
                )
        prefetch_context["wellness"] = df_well.to_dict(orient="records")

    # --- Activities (light + full) ---
    def normalize_activities(data):
        if not isinstance(data, list):
            return data
        df = pd.DataFrame(data)
        df = normalize_dates(df, ["start_date_local", "date", "start_date"])
        for col in ["tss", "icu_training_load", "distance", "moving_time", "average_heartrate", "IF"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df.to_dict(orient="records")

    for key in ("activities_light", "activities_full"):
        if key in prefetch_context:
            prefetch_context[key] = normalize_activities(prefetch_context[key])

    # --- Calendar normalization ---
    if "calendar" in prefetch_context and isinstance(prefetch_context["calendar"], list):
        df_cal = pd.DataFrame(prefetch_context["calendar"])
        df_cal = normalize_dates(df_cal, ["date", "start_date_local"])
        prefetch_context["calendar"] = df_cal.to_dict(orient="records")

    # --- Optional debug: verify shapes after normalization ---
    try:
        debug(
            {"debug_trace": []},
            "[NORM] ✅ Normalization summary → "
            f"wellness={len(prefetch_context.get('wellness', []))} rows, "
            f"activities_light={len(prefetch_context.get('activities_light', []))}, "
            f"activities_full={len(prefetch_context.get('activities_full', []))}, "
            f"calendar={len(prefetch_context.get('calendar', []))}"
        )
        if "wellness" in prefetch_context:
            import json
            sample = json.dumps(prefetch_context["wellness"][:2], indent=2, default=str)
            debug({"debug_trace": []}, f"[NORM] wellness sample (first 2 rows):\n{sample}")
    except Exception as e:
        print(f"[NORM] Debug normalization preview failed: {e}")

    return prefetch_context


# ─────────────────────────────────────────────
# SANITISER
# ─────────────────────────────────────────────

def sanitize(obj, seen=None):
    """Safe JSON sanitation."""
    import math
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return None
        return obj
    if isinstance(obj, (datetime, date, pd.Timestamp)):
        return obj.isoformat()
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


# ─────────────────────────────────────────────
# RUN FULL AUDIT
# ─────────────────────────────────────────────

def _run_full_audit(range: str, output_format="markdown", prefetch_context=None):
    os.environ["REPORT_TYPE"] = range.lower()
    buffer = io.StringIO()

    with redirect_stdout(buffer):
        if prefetch_context:
            prefetch_context = normalize_prefetched_context(prefetch_context)
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

    context = report.get("context", {}) if isinstance(report, dict) else {}
    markdown = report.get("markdown", "") if isinstance(report, dict) else str(report)

    context["render_options"] = {
        "verbose_events": True,
        "include_all_events": True,
        "return_format": "markdown",
    }

    semantic_graph = build_semantic_json(context)
    return report, compliance, logs, context, semantic_graph, markdown


# ─────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "IntervalsICU GPTCoach API running 🚴"}


@app.get("/run")
def run_audit(
    range: str = Query("weekly", enum=["weekly", "season", "wellness", "summary"]),
    format: str = Query("markdown", enum=["markdown", "json", "semantic"]),
):
    try:
        report, compliance, logs, context, sg, markdown = _run_full_audit(range, format)
        if format.lower() in ("json", "semantic"):
            return JSONResponse({
                "status": "ok",
                "report_type": range,
                "output_format": "semantic_json",
                "semantic_graph": sanitize(sg),
                "compliance": compliance,
                "logs": logs[-20000:]
            })
        return JSONResponse({
            "status": "ok",
            "report_type": range,
            "output_format": "markdown",
            "markdown": markdown,
            "compliance": compliance,
            "logs": logs[-20000:]
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
        data = json.loads(raw)

        report_range = data.get("range", "weekly")
        fmt = data.get("format", "markdown").lower()

        prefetch_context = {
            k: v for k, v in {
                "activities_light": data.get("activities_light"),
                "activities_full": data.get("activities_full"),
                "wellness": data.get("wellness"),
                "calendar": data.get("calendar"),
                "athlete": data.get("athlete"),
            }.items() if v is not None
        }

        if prefetch_context:
            prefetch_context = normalize_prefetched_context(prefetch_context)

        with redirect_stdout(buffer):
            report, compliance = run_report(
                reportType=report_range,
                output_format=fmt,
                include_coaching_metrics=True,
                **(prefetch_context or {})
            )

        logs = buffer.getvalue()
        context = report.get("context", {}) if isinstance(report, dict) else {}

        if fmt in ("json", "semantic"):
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
            "logs": buffer.getvalue()[-20000:] if buffer else None,
        },
    )
