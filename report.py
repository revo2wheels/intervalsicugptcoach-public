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
import os
from contextlib import redirect_stdout
from pathlib import Path
from audit_core.report_controller import run_report
from audit_core.utils import debug

# Ensure proper UTF-8 handling for terminal and markdown
sys.stdout.reconfigure(encoding="utf-8")


def generate_full_report(report_type="weekly", output_path=None):
    """Run the chosen report range and save logs + markdown output."""
    buffer = io.StringIO()

    # --- Determine output location ---
    if not output_path:
        output_dir = Path("reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"report_{report_type}.md"

    # Export report type for downstream modules
    os.environ["REPORT_TYPE"] = report_type.lower()
    debug({}, f"🧭 Generating {report_type.title()} Report")

    # --- Capture logs during execution ---
    with redirect_stdout(buffer):
        report, compliance = run_report(
            reportType=report_type,
            include_coaching_metrics=True,
        )

    # --- Extract captured logs ---
    raw_logs = buffer.getvalue().splitlines()

    # Filter out bulky debug or dataset prints
    skip_terms = [
        "snapshot", "trace", "json", "context", "activities_full",
        "df_event", "icu_training_load", "event_log_text", "DataFrame"
    ]
    log_output = "\n".join(
        [line for line in raw_logs if not any(term in line.lower() for term in skip_terms)]
    ).strip()

    # --- Safely extract Markdown from report object ---
    md_output = ""
    if isinstance(report, dict):
        # Most common unified case (post-finalizer)
        if "markdown" in report and isinstance(report["markdown"], str):
            md_output = report["markdown"]
        elif "markdown" in report and isinstance(report["markdown"], dict):
            # Nested markdown dicts (rare legacy case)
            md_output = str(report["markdown"].get("markdown", ""))
        elif isinstance(report.get("markdown"), str):
            md_output = report.get("markdown", "").strip()
        else:
            # Final fallback: convert safely
            md_output = str(report.get("markdown", "")) if "markdown" in report else ""
    elif hasattr(report, "to_markdown"):
        md_output = report.to_markdown()
    elif isinstance(report, str):
        md_output = report.strip()
    else:
        md_output = "_⚠ Unsupported report format._"

    # --- Enforce Markdown type and minimal content ---
    if not isinstance(md_output, str):
        md_output = str(md_output)
    if not md_output.strip():
        md_output = "_⚠ Renderer returned empty Markdown._"

    debug({}, f"[REPORT.PY] Markdown length after extraction: {len(md_output)}")

    # --- Build the final Markdown report file ---
    full_output = (
        f"# 🧾 {report_type.title()} Audit Report\n\n"
        "## Execution Logs\n\n"
        "```\n" + log_output + "\n```\n\n"
        "## Rendered Markdown Report\n\n"
        + md_output.strip()
    )

    # --- Write to disk ---
    Path(output_path).write_text(full_output, encoding="utf-8")
    print(f"✅ {report_type.title()} report written to {Path(output_path).resolve()}")


def main():
    """Parse CLI arguments and trigger report generation."""
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
        help="Optional custom output file path",
    )

    args = parser.parse_args()
    generate_full_report(report_type=args.range, output_path=args.output)


if __name__ == "__main__":
    main()
