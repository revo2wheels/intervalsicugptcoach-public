#!/usr/bin/env python3
"""
Intervals.icu GPTCoach Railway API
Final Unified Version with Prefetch Normalization
Parses prefetched data into identical Tier-0 format as local Python
Ensures parity for daily_load, zone distributions, derived metrics, etc.
"""
import re
from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
import os, sys, io, json, math, pandas as pd, numpy as np
from datetime import datetime, timedelta, date
from contextlib import redirect_stdout

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "audit_core"))

from audit_core.report_controller import run_report
from audit_core.utils import debug
from semantic_json_builder import build_semantic_json
from audit_core.tier0_pre_audit import expand_zones


print("[BOOT] 🚀 Starting IntervalsICU GPTCoach Railway API")
icuoauth = os.getenv("ICU_OAUTH")
if icuoauth:
    print("[BOOT] ICU_OAUTH detected:", icuoauth[:10], "...")
else:
    print("[BOOT-WARN] ICU_OAUTH missing — Intervals.icu calls may fail")

app = FastAPI(title="IntervalsICU GPTCoach Railway API", version="2.0")


# ============================================================
# 🧹 SANITIZER
# ============================================================
def sanitize(obj, seen=None):
    import pandas as pd, numpy as np
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return None
        return obj
    if isinstance(obj, (datetime, date, pd.Timestamp)):
        try:
            return obj.isoformat()
        except Exception:
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


# ============================================================
# 🧩 NORMALIZER — replicate Tier-0 Pre-Audit
# ============================================================
def normalize_prefetched_context(data):
    """Normalize prefetched payload from Cloudflare → local Python shape"""
    context = {}
    try:
        def safe_df(obj):
            if not obj:
                return pd.DataFrame()
            df = pd.DataFrame(obj)
            if "start_date_local" in df.columns:
                df["start_date_local"] = pd.to_datetime(df["start_date_local"], errors="coerce").dt.tz_localize(None)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.tz_localize(None)
            num_cols = [c for c in df.columns if any(x in c.lower() for x in ["distance","moving_time","tss","load","icu_training_load","if","vo2max"])]
            for c in num_cols:
                df[c] = pd.to_numeric(df[c], errors="coerce")
            return df

        # Light / Full / Wellness
        df_light = safe_df(data.get("activities_light"))
        df_full  = safe_df(data.get("activities_full"))
        df_well  = safe_df(data.get("wellness"))
        athlete  = data.get("athlete", {})
        calendar = data.get("calendar", {})

        # ─────────────────────────────────────────────
        # 🩺 Ensure baseline columns exist for Tier-0 stability
        # ─────────────────────────────────────────────
        for df_name, df in {"light": df_light, "full": df_full}.items():
            for col in ["moving_time", "distance", "icu_training_load", "type"]:
                if col not in df.columns:
                    df[col] = 0 if col in ["moving_time", "distance", "icu_training_load"] else ""
            debug({}, f"[NORM] ensured baseline columns exist for df_{df_name} ({len(df)} rows)")

        context["activities_light"] = df_light.to_dict(orient="records")
        context["activities_full"]  = df_full.to_dict(orient="records")
        context["wellness"]         = df_well.to_dict(orient="records")
        context["athlete"]          = athlete
        context["calendar"]         = calendar

        # Derived Tier-0 equivalents
        context["df_light"]  = df_light
        context["df_master"] = df_full
        context["df_wellness"] = df_well

        # Build daily summary if missing
        if not df_full.empty and "icu_training_load" in df_full.columns:
            df_daily = (df_full.groupby(df_full["start_date_local"].dt.date)["icu_training_load"]
                        .sum(min_count=1)
                        .reset_index().rename(columns={"start_date_local": "date"}))
            df_daily["date"] = pd.to_datetime(df_daily["date"], errors="coerce")
            context["df_daily"] = df_daily
            debug(context, f"[NORM] built df_daily {len(df_daily)} days")
        else:
            context["df_daily"] = pd.DataFrame(columns=["date", "icu_training_load"])
            debug(context, "[NORM] df_daily empty — no full data")

        # Snapshot 7d totals
        if not df_full.empty:
            last7 = df_full.tail(7)
            context["tier0_snapshotTotals_7d"] = {
                "tss": float(last7["icu_training_load"].sum()) if "icu_training_load" in last7 else 0,
                "hours": float(last7["moving_time"].sum())/3600 if "moving_time" in last7 else 0,
                "distance_km": float(last7["distance"].sum())/1000 if "distance" in last7 else 0,
                "sessions": len(last7),
            }
            debug(context, f"[NORM] snapshot_7d totals computed: {context['tier0_snapshotTotals_7d']}")
        else:
            context["tier0_snapshotTotals_7d"] = {"tss":0,"hours":0,"distance_km":0,"sessions":0}

        # Timezone
        context["timezone"] = athlete.get("timezone", "UTC")
        context["athleteProfile"] = athlete
        context["athlete_raw"] = athlete
        context["prefetch_done"] = True
        context["semantic_mode"] = True

        # --- Normalize Intervals zone arrays (for HR and Power) ---
        def normalize_zone_fields(df):
            """Convert zone strings to JSON lists if needed (Intervals-prefetched data)."""
            if df.empty:
                return df
            for col in df.columns:
                if "zone_times" in col or "zones" in col:
                    # Convert JSON-encoded strings (e.g., '[{"secs":120},...]') to lists
                    if df[col].dtype == object:
                        df[col] = df[col].apply(
                            lambda x: json.loads(x) if isinstance(x, str) and x.strip().startswith("[") else x
                        )
            return df

        df_full = normalize_zone_fields(df_full)
        df_light = normalize_zone_fields(df_light)
        debug(context, "[NORM] ✅ Normalized zone fields in prefetched context")

        # --- Expand HR/Power/Pace zones to match Tier-0 local parity ---
        try:
            for field, prefix in [
                ("icu_zone_times", "power"),
                ("icu_hr_zone_times", "hr"),
                ("pace_zone_times", "pace"),
            ]:
                if field in df_full.columns and not df_full.empty:
                    expanded = expand_zones(df_full[[field]].copy(), field, prefix)
                    for col in expanded.columns:
                        if col not in df_full.columns:
                            df_full[col] = expanded[col]
                    # 💡 keep the original columns for Tier-1 fusion
            debug(context, "[NORM] ✅ Expanded HR/Power/Pace zones (non-destructive)")

            debug(context, "[NORM] ✅ Expanded HR/Power/Pace zones for Tier-0 parity")
        except Exception as e:
            debug(context, f"[NORM] ⚠️ Zone expansion skipped: {e}")

        # --- Update context after expansion ---
        context["df_full"] = df_full
        context["activities_full"] = df_full.to_dict(orient="records")
        debug(
            context,
            f"[NORM] activities_light={len(df_light)} full={len(df_full)} wellness={len(df_well)} "
            f"athlete_keys={list(athlete.keys()) if athlete else 'none'}"
        )


        debug(context, f"[NORM] activities_light={len(df_light)} full={len(df_full)} wellness={len(df_well)} athlete_keys={list(athlete.keys()) if athlete else 'none'}")
    except Exception as e:
        debug(context, f"[NORM] ❌ Normalization failed: {e}")
    return context


# ============================================================
# 🧠 CORE RUN FUNCTION
# ============================================================
def _run_full_audit(range: str, output_format="markdown", prefetch_context=None):
    os.environ["REPORT_TYPE"] = range.lower()
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        if prefetch_context:
            report, compliance = run_report(reportType=range, output_format=output_format, include_coaching_metrics=True, **prefetch_context)
        else:
            report, compliance = run_report(reportType=range, output_format=output_format, include_coaching_metrics=True)
    logs = buffer.getvalue()

    if isinstance(report, dict):
        context = report.get("context", {}) or {}
        markdown = report.get("markdown", "")
    else:
        context, markdown = {}, str(report)

    context["render_options"] = {"verbose_events": True, "include_all_events": True, "return_format": "markdown"}
    semantic_graph = build_semantic_json(context)
    return report, compliance, logs, context, semantic_graph, markdown


# ============================================================
# 🛰️ ENDPOINTS
# ============================================================
@app.get("/")
def root():
    return {"message": "IntervalsICU GPTCoach Railway API 🧠 Running"}


@app.get("/run")
def run_audit(range: str = Query("weekly"), format: str = Query("markdown")):
    try:
        report, compliance, logs, context, sg, markdown = _run_full_audit(range=range, output_format=format)
        if format in ("json", "semantic"):
            return JSONResponse({"status":"ok","report_type":range,"output_format":"semantic_json",
                "semantic_graph":sanitize(sg),"compliance":compliance,"logs":logs[:20000]})
        return JSONResponse({"status":"ok","report_type":range,"output_format":"markdown","markdown":markdown,"logs":logs[:20000]})
    except Exception as e:
        return error_response(e)


@app.post("/run")
async def run_audit_with_data(request: Request):
    buffer = io.StringIO()
    try:
        raw = await request.body()
        if not raw:
            raise ValueError("Empty request body")
        data = json.loads(raw)
        report_range = data.get("range","weekly")
        fmt = data.get("format","markdown").lower()
        prefetch_context = normalize_prefetched_context(data)
        with redirect_stdout(buffer):
            report, compliance = run_report(reportType=report_range, output_format=fmt, include_coaching_metrics=True, **prefetch_context)
        logs = buffer.getvalue()
        if fmt in ("json","semantic"):
            context = report.get("context",{}) if isinstance(report,dict) else {}
            return JSONResponse({"status":"ok","report_type":report_range,"output_format":"semantic_json",
                "semantic_graph":sanitize(build_semantic_json(context)),"compliance":compliance,"logs":logs[-20000:]})
        return JSONResponse({"status":"ok","report_type":report_range,"output_format":"markdown","markdown":report.get("markdown",""),"logs":logs[-20000:]})
    except Exception as e:
        return error_response(e, buffer)


def error_response(e: Exception, buffer=None, status_code:int=500):
    import traceback
    return JSONResponse(status_code=status_code, content={
        "status":"error","message":str(e),"exception_type":type(e).__name__,
        "trace":traceback.format_exc(),"logs":buffer.getvalue()[-20000:] if buffer else None})


@app.get("/semantic")
def get_semantic(range: str = Query("weekly")):
    _, compliance, logs, _, sg, _ = _run_full_audit(range=range)
    return JSONResponse({"status":"ok","report_type":range,"output_format":"semantic_json","semantic_graph":sanitize(sg),"compliance":compliance,"logs":logs[:20000]})


@app.get("/metrics")
def get_metrics(range: str = Query("weekly")):
    _, compliance, logs, _, sg, _ = _run_full_audit(range=range)
    return JSONResponse({"status":"ok","report_type":range,
        "metrics":sanitize(sg.get("metrics",{})),
        "extended_metrics":sanitize(sg.get("extended_metrics",{})),
        "trend_metrics":sanitize(sg.get("trend_metrics",{})),
        "adaptation_metrics":sanitize(sg.get("adaptation_metrics",{})),
        "correlation_metrics":sanitize(sg.get("correlation_metrics",{})),
        "compliance":compliance,"logs":logs[:20000]})


@app.get("/phases")
def get_phases(range: str = Query("weekly")):
    _, compliance, logs, _, sg, _ = _run_full_audit(range=range)
    return JSONResponse({"status":"ok","report_type":range,
        "phases":sanitize(sg.get("phases",[])),"actions":sanitize(sg.get("actions",[])),
        "compliance":compliance,"logs":logs[:20000]})


@app.get("/compare")
def compare_periods(range: str = Query("weekly")):
    _, compliance, logs, _, sg, _ = _run_full_audit(range=range)
    return JSONResponse({"status":"ok","report_type":range,
        "trend_metrics":sanitize(sg.get("trend_metrics",{})),"core_metrics":sanitize(sg.get("metrics",{})),
        "compliance":compliance,"logs":logs[:20000]})


@app.get("/insights")
def get_insights(range: str = Query("weekly")):
    _, compliance, logs, _, sg, _ = _run_full_audit(range=range)
    return JSONResponse({"status":"ok","report_type":range,"insights":sanitize(sg.get("insight_view",{})),
        "compliance":compliance,"logs":logs[:20000]})

# ============================================================
# 🧠 DEBUG ENDPOINT — Semantic JSON + Logs Only
# ============================================================
@app.get("/debug")
def get_debug(
    range: str = Query("weekly", description="Report type: weekly, season, wellness, summary"),
    format: str = Query("semantic", description="Output format: semantic (ignored for now)")
):
    """
    Debug endpoint for any report type.
    Returns semantic JSON + captured logs.
    Compatible with both local and staging use.
    """
    try:
        report, compliance, logs, context, sg, markdown = _run_full_audit(
            range=range,
            output_format="semantic"
        )

        return JSONResponse({
            "status": "ok",
            "report_type": range,
            "output_format": "semantic_json",
            "semantic_graph": sanitize(sg),
            "logs": logs[-20000:],
        })

    except Exception as e:
        return error_response(e)

