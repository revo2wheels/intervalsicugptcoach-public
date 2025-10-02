import re
from datetime import datetime, timedelta

class ReportValidationError(Exception):
    """Custom error for audit validation failures."""
    pass


def validate_report(payload: dict):
    """
    Validate GPT-generated report against audit rules.

    Payload expected structure:
    {
      "reportText": "...",   # GPT report output (Markdown string)
      "reportType": "season", # one of: weekly, season, block, event
      "startDate": "2025-08-21",
      "endDate": "2025-10-02"
    }
    """
    report = payload.get("reportText", "")
    report_type = payload.get("reportType", "").lower()
    start_date = payload.get("startDate")
    end_date = payload.get("endDate")

    # === Audit presence ===
    if "Audit:" not in report:
        raise ReportValidationError("❌ Missing Audit section.")

    # === Core sections required ===
    required_sections = ["Key Stats", "Events", "Sections"]
    for sec in required_sections:
        if sec not in report:
            raise ReportValidationError(f"❌ Missing required section: {sec}")

    # === Report type specific checks ===
    if report_type == "weekly":
        if start_date and end_date:
            delta = (datetime.fromisoformat(end_date) - datetime.fromisoformat(start_date)).days + 1
            if delta != 7:
                raise ReportValidationError(f"❌ Weekly report must be 7 days, got {delta} days.")

    elif report_type == "season":
        # Season reports must have all 4 phases
        for phase in ["Build", "Overload", "Deload", "Consolidation"]:
            if phase not in report:
                raise ReportValidationError(f"❌ Missing Season phase: {phase}")

        # Enforce default 42-day window if no explicit dates provided
        if not (start_date and end_date):
            today = datetime.today().date()
            expected_start = (today - timedelta(days=41)).isoformat()
            expected_end = today.isoformat()
            if f"{expected_start} → {expected_end}" not in report:
                raise ReportValidationError(
                    f"❌ Default 42-day window not applied. Expected {expected_start} → {expected_end}"
                )

    elif report_type == "block":
        if "progression" not in report.lower():
            raise ReportValidationError("❌ Block report missing progression summary.")

    elif report_type == "event":
        if "Event" not in report and "event" not in report.lower():
            raise ReportValidationError("❌ Event report missing event log.")

    return { "status": "✅ Validation Passed" }
