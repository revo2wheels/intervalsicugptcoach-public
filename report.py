#!/usr/bin/env python3
"""
Generate full weekly audit report (Markdown + logs)
Captures both stdout logs and the rendered markdown report into one .md file.
"""

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

# Import your core report runner
from audit_core.report_controller import run_report


def generate_full_report(output_path="report_full.md"):
    """Run the weekly report and save both logs + markdown output."""
    buffer = io.StringIO()

    # Capture all printed output during the report execution
    with redirect_stdout(buffer):
        report = run_report(
            "weekly",
            auditFinal=True,
            force_analysis=True,
            preRenderAudit=True,
            tier2_enforce_event_only_totals=True,
            render_mode="full",
        )

    # Collect captured log text and markdown body
    log_output = buffer.getvalue()
    md_output = report.get("markdown", "")

    # Combine into a single Markdown file
    full_output = (
        "# 🧾 Full Weekly Audit Report\n\n"
        "## Execution Logs\n\n"
        "```\n" + log_output + "\n```\n\n"
        "## Rendered Markdown Report\n\n"
        + md_output
    )

    # Write to file
    output_file = Path(output_path)
    output_file.write_text(full_output, encoding="utf-8")

    print(f"✅ Full report (logs + markdown) written to {output_file.resolve()}")


if __name__ == "__main__":
    generate_full_report()
