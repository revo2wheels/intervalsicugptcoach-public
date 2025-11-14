#!/usr/bin/env python3
"""
Generate audit reports (weekly, season, wellness, summary)
Captures both stdout logs and the rendered markdown report into one .md file.
Usage:
    python report.py --range weekly
    python report.py --range season
    python report.py --range wellness
    python report.py --range summary
"""

import io
import sys
import argparse
from contextlib import redirect_stdout
from pathlib import Path
from audit_core.report_controller import run_report
from audit_core.utils import debug

# Ensure proper UTF-8 handling for terminal and markdown
sys.stdout.reconfigure(encoding="utf-8")


def generate_full_report(report_type="weekly", output_path=None):
    """Run the chosen report range and save logs + markdown."""
    buffer = io.StringIO()

    # Default dynamic output file naming
    if not output_path:
        output_dir = Path("reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"report_{report_type}.md"

    debug({}, f"🧭 Generating {report_type.title()} Report")

    # Capture all logs
    with redirect_stdout(buffer):
        report, compliance = run_report(
            reportType=report_type,
            include_coaching_metrics=True,
        )

    # Extract log and markdown report
    log_output = buffer.getvalue()
    md_output = report.get("markdown", "")

    # Fallback if Markdown not included
    if not md_output and isinstance(report, str):
        md_output = report

    # Combine both log + markdown
    full_output = (
        f"# 🧾 {report_type.title()} Audit Report\n\n"
        "## Execution Logs\n\n"
        "```\n" + log_output + "\n```\n\n"
        "## Rendered Markdown Report\n\n"
        + md_output
    )

    # Write to disk
    Path(output_path).write_text(full_output, encoding="utf-8")
    print(f"✅ {report_type.title()} report written to {Path(output_path).resolve()}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate audit reports for different data ranges."
    )
    parser.add_argument(
        "--range",
        type=str.lower,
        choices=["weekly", "season", "wellness", "summary"],
        default="weekly",
        help="Select which report range to run (default: weekly)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional path for the output markdown file",
    )

    args = parser.parse_args()

    generate_full_report(report_type=args.range, output_path=args.output)


if __name__ == "__main__":
    main()
