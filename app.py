from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
import os
import io
from contextlib import redirect_stdout
from audit_core.report_controller import run_report
from audit_core.utils import debug

app = FastAPI(title="IntervalsICU GPTCoach API", version="1.1")

@app.get("/")
def root():
    return {"message": "IntervalsICU GPTCoach API running 🚴"}

# ─────────────────────────────────────────────
# 1️⃣ Existing GET endpoint
# ─────────────────────────────────────────────
@app.get("/run")
def run_audit(
    range: str = Query("weekly", enum=["weekly", "season", "wellness", "summary"])
):
    os.environ["REPORT_TYPE"] = range.lower()
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        report, compliance = run_report(reportType=range, include_coaching_metrics=True)
    logs = buffer.getvalue()
    markdown = report.get("markdown", "") if isinstance(report, dict) else str(report)
    return JSONResponse(
        content={
            "status": "ok",
            "report_type": range,
            "compliance": compliance,
            "markdown": markdown,
            "logs": logs,
        }
    )

# ─────────────────────────────────────────────
# 2️⃣ New POST endpoint (Cloudflare Worker mode)
# ─────────────────────────────────────────────
@app.post("/run")
async def run_audit_with_data(request: Request):
    """
    Accepts pre-fetched JSON data (activities, wellness, profile)
    from Cloudflare Worker to bypass OAuth fetching.
    """
    try:
        data = await request.json()
        range = data.get("range", "weekly")

        # Inject Cloudflare-supplied prefetch context
        context = {
            "activities_light": data.get("activities_light", []),
            "activities_full": data.get("activities_full", []),
            "wellness": data.get("wellness", []),
            "athlete": data.get("athlete", {}),
        }

        # Run report in "prefetched mode"
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            report, compliance = run_report(
                reportType=range,
                include_coaching_metrics=True,
                prefetch_context=context,   # 🧩 bypasses Tier-0 fetching
            )
        logs = buffer.getvalue()

        markdown = report.get("markdown", "") if isinstance(report, dict) else str(report)

        return JSONResponse(
            content={
                "status": "ok",
                "report_type": range,
                "compliance": compliance,
                "markdown": markdown,
                "logs": logs,
            }
        )

    except Exception as e:
        debug({}, f"❌ Error in run_audit_with_data: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)},
        )
