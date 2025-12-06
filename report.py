#!/usr/bin/env python3
"""
Generate audit reports (weekly, season, wellness, summary)
Captures both stdout logs and the rendered markdown or semantic report into one file.

Usage:
    python report.py --range weekly --format markdown
    python report.py --range season --format markdown
    python report.py --range wellness --format markdown
    python report.py --range summary --format markdown
    python report.py --range weekly --format semantic
    python report.py --range season --format semantic
"""

import io, os
import sys
import json
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import argparse
from contextlib import redirect_stdout
from pathlib import Path
from audit_core.report_controller import run_report
from audit_core.utils import debug

# Ensure proper UTF-8 handling for terminal and markdown
sys.stdout.reconfigure(encoding="utf-8")

def generate_full_report(report_type="weekly", output_path=None, output_format="markdown"):
    """Run the chosen report range and save logs + output."""
    buffer = io.StringIO()

    # --- Determine output location ---
    if not output_path:
        output_dir = Path("reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"report_{report_type}.{output_format}"

    # Export report type for downstream modules
    os.environ["REPORT_TYPE"] = report_type.lower()
    debug({}, f"🧭 Generating {report_type.title()} Report")

    # --- Capture logs during execution ---
    with redirect_stdout(buffer):
        # Unpack all values returned by run_report
        result = run_report(
            reportType=report_type,
            include_coaching_metrics=True,
            output_format=output_format,  # Pass the output format
        )

        # Handle two or three returned values from run_report
        if len(result) == 3:
            report, compliance, logs = result
        else:
            report, compliance = result
            logs = ""  # Set logs to empty if not provided

        # Ensure context is extracted from report
        context = report.get("context", {})

    # --- Extract captured logs ---
    raw_logs = buffer.getvalue().splitlines()

    skip_terms = [
        "snapshot", "trace", "json", "context", "activities_full",
        "df_event", "icu_training_load", "event_log_text", "DataFrame"
    ]
    log_output = "\n".join(
        [line for line in raw_logs if not any(term in line.lower() for term in skip_terms)]
    ).strip()

    # --- Ensure the report is a dictionary before accessing keys ---
    if isinstance(report, dict):
        debug({}, f"Context before generating semantic graph: {context}")  # Debug context
        if output_format == "semantic":
            semantic_output = report.get("semantic_graph", {})
            debug({}, f"[REPORT.PY] JSON length after extraction: {len(str(semantic_output))}")

            # --- Return the final Semantic JSON output ---
            full_output = {
                "status": "ok",
                "message": f"{report_type.title()} report generated",
                "semantic_graph": semantic_output,
                "logs": log_output
            }
        elif output_format == "markdown":
            # Existing logic for Markdown output
            md_output = report.get("markdown", "")
            full_output = (
                f"# 🧾 {report_type.title()} Audit Report\n\n"
                "## Execution Logs\n\n"
                "```\n" + log_output + "\n```\n\n"
                "## Rendered Markdown Report\n\n"
                + md_output.strip()
            )
    else:
        # Fallback in case the report is not a dictionary (for debugging purposes)
        full_output = {"markdown": str(report), "context": {}}

    # --- Write to disk ---
    # --- Normalise full_output so .get() works safely ---
    if not isinstance(full_output, dict):
        # full_output is a string or unexpected type → wrap it
        full_output = {"markdown": str(full_output)}

    # --- Now safe to access full_output.get(...) ---
    if output_format == "markdown":
        Path(output_path).write_text(
            full_output.get("markdown", ""),
            encoding="utf-8"
        )

    elif output_format == "semantic":
        Path(output_path).write_text(
            json.dumps(full_output, indent=2, default=str),
            encoding="utf-8"
        )


    print(f"✅ {report_type.title()} report written to {Path(output_path).resolve()}")


def sanitize_for_json(obj, seen=None):
    """Remove circular references & non-serializable objects."""
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        return "<circular>"
    seen.add(obj_id)

    # Primitives
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj

    # Datetime-like
    if hasattr(obj, "isoformat"):
        try:
            return obj.isoformat()
        except:
            return str(obj)

    # pandas / numpy
    try:
        import pandas as pd
        import numpy as np
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient="records")
        if isinstance(obj, pd.Series):
            return obj.to_dict()
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj)
    except:
        pass

    # dict
    if isinstance(obj, dict):
        return {sanitize_for_json(k, seen): sanitize_for_json(v, seen) for k, v in obj.items()}

    # list / tuple
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(i, seen) for i in obj]

    # fallback
    return str(obj)



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
        help="Select which report range to run (default: weekly)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional custom output file path"
    )
    parser.add_argument(
        "--format",
        type=str.lower,
        choices=["markdown", "semantic"],
        default="markdown",
        help="Select output format (default: markdown)"
    )

    args = parser.parse_args()
    generate_full_report(report_type=args.range, output_path=args.output, output_format=args.format)

if __name__ == "__main__":
    main()
