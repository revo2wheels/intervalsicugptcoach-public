from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
import io
import os
import sys
from contextlib import redirect_stdout
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "audit_core"))

# Core audit pipeline
from audit_core.report_controller import run_report
from audit_core.utils import debug

# Semantic JSON builder
from semantic_json_builder import build_semantic_json

# ─────────────────────────────────────────────
# 🧩 Startup debug — verify environment variable
# ─────────────────────────────────────────────
print("[DEBUG] Starting IntervalsICU GPTCoach API")
icuoauth = os.getenv("ICU_OAUTH")
if icuoauth:
    print("[DEBUG] ICU_OAUTH ENV VAR detected:", icuoauth[:20], "...")
else:
    print("[WARN] ICU_OAUTH ENV VAR missing — Intervals.icu calls may fail!")

# ─────────────────────────────────────────────
# 🚀 FastAPI app init
# ─────────────────────────────────────────────
app = FastAPI(title="IntervalsICU GPTCoach API", version="1.3")

# ─────────────────────────────────────────────
# 🔧 Helper: run full audit and build semantic graph
# ─────────────────────────────────────────────
def log_to_markdown(content: str, filename="debug_report.md"):
    """Log debug content to a markdown file."""
    with open(filename, "a") as f:
        f.write(f"### {content}\n")
        f.write("\n")

def _run_full_audit(range: str, prefetch_context: dict | None = None):
    """
    Centralised execution for all endpoints:
      - Runs Tier-0 → Tier-1 → Tier-2 → Renderer
      - Returns (report, compliance, logs, context, semantic_graph)
    """
    os.environ["REPORT_TYPE"] = range.lower()

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        if prefetch_context:
            report, compliance = run_report(reportType=range, include_coaching_metrics=True, prefetch_context=prefetch_context)
        else:
            report, compliance = run_report(reportType=range, include_coaching_metrics=True)

    logs = buffer.getvalue()

    if isinstance(report, dict):
        context = report.get("context", {}) or {}
        markdown = report.get("markdown", "")
    else:
        context = {}
        markdown = str(report)

    # Log context to markdown file
    log_to_markdown(f"Context before generating semantic graph: {context}")

    semantic_graph = build_semantic_json(context)
    return report, compliance, logs, context, semantic_graph, markdown

# ─────────────────────────────────────────────
# 0️⃣ Root check
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "IntervalsICU GPTCoach API running 🚴"}

# ─────────────────────────────────────────────
# 1️⃣ GET /run — markdown or semantic JSON
# ─────────────────────────────────────────────
@app.get("/run")
def run_audit(range: str = Query("weekly", enum=["weekly", "season", "wellness", "summary"]), format: str = Query("markdown", enum=["markdown", "json", "semantic"])):
    report, compliance, logs, context, semantic_graph, markdown = _run_full_audit(range=range)

    if format.lower() in ("json", "semantic"):
        return JSONResponse(content={
            "status": "ok", "report_type": range, "output_format": "semantic_json", 
            "semantic_graph": semantic_graph, "compliance": compliance, "logs": logs[:20000]
        })

    return JSONResponse(content={
        "status": "ok", "report_type": range, "output_format": "markdown", 
        "compliance": compliance, "markdown": markdown, "logs": logs[:20000]
    })

# ─────────────────────────────────────────────
# 2️⃣ POST /run — Cloudflare Worker mode
# ─────────────────────────────────────────────
@app.post("/run")
async def run_audit_with_data(request: Request):
    """Accept pre-fetched data to bypass OAuth fetching."""
    try:
        data = await request.json()
        range = data.get("range", "weekly")
        output_format = data.get("format", "markdown").lower()

        prefetch_context = {
            "activities_light": data.get("activities_light", []),
            "activities_full": data.get("activities_full", []),
            "wellness": data.get("wellness", []),
            "athlete": data.get("athlete", {}),
        }

        report, compliance, logs, context, semantic_graph, markdown = _run_full_audit(range=range, prefetch_context=prefetch_context)

        if output_format in ("json", "semantic"):
            return JSONResponse(content={
                "status": "ok", "report_type": range, "output_format": "semantic_json", 
                "semantic_graph": semantic_graph, "compliance": compliance, "logs": logs[:20000]
            })

        return JSONResponse(content={
            "status": "ok", "report_type": range, "output_format": "markdown", 
            "compliance": compliance, "markdown": markdown, "logs": logs[:20000]
        })

    except Exception as e:
        debug({}, f"❌ Error in run_audit_with_data: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

# ─────────────────────────────────────────────
# 3️⃣ /debug_env — unchanged
# ─────────────────────────────────────────────
@app.get("/debug_env")
def debug_env():
    token = os.getenv("ICU_OAUTH")
    return {
        "ICU_OAUTH_loaded": bool(token),
        "ICU_OAUTH_prefix": token[:10] if token else None,
        "PORT": os.getenv("PORT"),
    }

# ─────────────────────────────────────────────
# 🧩 /debug — trigger debug and capture logs
# ─────────────────────────────────────────────
@app.get("/debug")
def debug_endpoint(range: str = Query("weekly", enum=["weekly", "season", "wellness", "summary"])):
    """
    This endpoint triggers the debugging function, captures logs, and returns them.
    """
    # Debugging the context
    report, compliance, logs, context, semantic_graph, markdown = _run_full_audit(range=range)
    
    # Store the debug information in a markdown file
    log_to_markdown(f"Triggered debug for range={range}. Context: {context}")
    
    # Return the debug logs and semantic graph for inspection
    return JSONResponse(content={
        "status": "ok", 
        "message": "Debug triggered and logs captured.",
        "context": context,
        "semantic_graph": semantic_graph,
        "logs": logs[:20000]
    })


# ─────────────────────────────────────────────
# 🅰️ /semantic — dedicated semantic endpoint
# ─────────────────────────────────────────────
@app.get("/semantic")
def get_semantic(range: str = Query("weekly", enum=["weekly", "season", "wellness", "summary"])):
    _, compliance, logs, _, semantic_graph, _ = _run_full_audit(range=range)
    return JSONResponse(content={
        "status": "ok", "report_type": range, "output_format": "semantic_json", 
        "semantic_graph": semantic_graph, "compliance": compliance, "logs": logs[:20000]
    })

# ─────────────────────────────────────────────
# 🅱️ /metrics — semantic metric graph only
# ─────────────────────────────────────────────
@app.get("/metrics")
def get_metrics(range: str = Query("weekly", enum=["weekly", "season", "wellness", "summary"])):
    _, compliance, logs, _, semantic_graph, _ = _run_full_audit(range=range)
    return JSONResponse(content={
        "status": "ok", "report_type": range, "metrics": semantic_graph.get("metrics", {}),
        "extended_metrics": semantic_graph.get("extended_metrics", {}),
        "trend_metrics": semantic_graph.get("trend_metrics", {}),
        "adaptation_metrics": semantic_graph.get("adaptation_metrics", {}),
        "correlation_metrics": semantic_graph.get("correlation_metrics", {}),
        "compliance": compliance, "logs": logs[:20000]
    })

# ─────────────────────────────────────────────
# 🅲️ /phases — periodisation / phase info
# ─────────────────────────────────────────────
@app.get("/phases")
def get_phases(range: str = Query("weekly", enum=["weekly", "season", "wellness", "summary"])):
    _, compliance, logs, _, semantic_graph, _ = _run_full_audit(range=range)
    return JSONResponse(content={
        "status": "ok", "report_type": range, "phases": semantic_graph.get("phases", []),
        "actions": semantic_graph.get("actions", []), "compliance": compliance, "logs": logs[:20000]
    })

# ─────────────────────────────────────────────
# 🅳️ /compare — expose Tier-2 trend/delta metrics
# (week vs prior baselines, as already computed by Tier-2)
# ─────────────────────────────────────────────
@app.get("/compare")
def compare_periods(range: str = Query("weekly", enum=["weekly", "season", "wellness", "summary"])):
    _, compliance, logs, _, semantic_graph, _ = _run_full_audit(range=range)

    trend_metrics = semantic_graph.get("trend_metrics", {})
    metrics = semantic_graph.get("metrics", {})

    return JSONResponse(content={
        "status": "ok", "report_type": range, "trend_metrics": trend_metrics,
        "core_metrics": metrics, "compliance": compliance, "logs": logs[:20000]
    })

# ─────────────────────────────────────────────
# 🅴️ /insights — AI-ready highlights (flags / hotspots)
# ─────────────────────────────────────────────
@app.get("/insights")
def get_insights(range: str = Query("weekly", enum=["weekly", "season", "wellness", "summary"])):
    _, compliance, logs, _, semantic_graph, _ = _run_full_audit(range=range)

    metrics = semantic_graph.get("metrics", {})
    actions = semantic_graph.get("actions", [])
    phases = semantic_graph.get("phases", [])

    red, amber, green = [], [], []
    for name, m in metrics.items():
        cls = m.get("classification")
        entry = {
            "name": name,
            "value": m.get("value"),
            "framework": m.get("framework"),
            "interpretation": m.get("interpretation"),
            "coaching_implication": m.get("coaching_implication"),
        }
        if cls == "red":
            red.append(entry)
        elif cls == "amber":
            amber.append(entry)
        elif cls == "green":
            green.append(entry)

    return JSONResponse(content={
        "status": "ok", "report_type": range,
        "insights": {"critical": red, "watch": amber, "positive": green, "actions": actions, "phases": phases},
        "compliance": compliance, "logs": logs[:20000]
    })
