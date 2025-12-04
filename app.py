from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import os
import io
from contextlib import redirect_stdout
from report import generate_full_report
from audit_core.report_controller import run_report
from audit_core.utils import debug

app = FastAPI(title="IntervalsICU GPTCoach API", version="1.0")

@app.get("/")
def root():
    return {"message": "IntervalsICU GPTCoach API running 🚴"}

@app.get("/run")
def run_audit(
    range: str = Query("weekly", enum=["weekly", "season", "wellness", "summary"])
):
    """
    Run a full audit and return both Markdown + structured JSON results.
    Example: http://localhost:8000/run?range=weekly
    """

    os.environ["REPORT_TYPE"] = range.lower()

    # Capture output logs during execution
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        report, compliance = run_report(reportType=range, include_coaching_metrics=True)

    logs = buffer.getvalue()

    if isinstance(report, dict):
        markdown = report.get("markdown", "")
    else:
        markdown = str(report)

    return JSONResponse(
        content={
            "status": "ok",
            "report_type": range,
            "compliance": compliance,
            "markdown": markdown,
            "logs": logs,
        }
    )
