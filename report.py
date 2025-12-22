#!/usr/bin/env python3
"""
Generate audit reports (weekly, season, wellness, summary)
Captures both stdout logs and the rendered markdown or semantic report into one file.

Usage:
    python report.py --range weekly --format markdown
    python report.py --range weekly --format semantic
    python report.py --range weekly --format semantic --prefetch
    python report.py --range weekly --format semantic --prefetch --staging
"""

import io
import os
import sys
import json
import argparse
import requests
from datetime import datetime
from contextlib import redirect_stdout
from pathlib import Path

# Import project modules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from audit_core.report_controller import run_report
from audit_core.utils import debug

sys.stdout.reconfigure(encoding="utf-8")

# ─────────────────────────────────────────────
# DEBUG REPRTS
# ─────────────────────────────────────────────

def fetch_debug_report(report_type, format="semantic", staging=False):
    """Fetch report and debug logs directly from Railway's /debug endpoint."""
    base = "https://intervalsicugptcoach-public-production.up.railway.app"
    if staging:
        base = "https://intervalsicugptcoach-public-staging.up.railway.app"

    url = f"{base}/debug?range={report_type}&format={format}"
    headers = {
        "Authorization": f"Bearer {os.getenv('ICU_OAUTH', '')}",
        "User-Agent": "IntervalsGPTCoachLocal/1.0"
    }

    print(f"[DEBUG ENDPOINT] Fetching {report_type} report with logs from {url}")
    resp = requests.get(url, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    outname = f"report_{report_type}_{'staging' if staging else 'prod'}_{format}_debug.json"
    with open(outname, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"[DEBUG ENDPOINT] ✅ Saved {outname}")
    print(f"[DEBUG ENDPOINT] keys={list(data.keys())}")
    if "logs" in data:
        print(f"[DEBUG ENDPOINT] 📜 Logs captured: {len(data['logs'].splitlines())} lines")

    return data


# ─────────────────────────────────────────────
# PREFETCH HELPER — Cloudflare Worker Schema
# ─────────────────────────────────────────────
def fetch_remote_report(report_type, fmt="semantic", staging=False):
    """Fetch a full rendered URF report (semantic+markdown+logs) from Cloudflare Worker."""
    base = f"https://intervalsicugptcoach.clive-a5a.workers.dev/run_{report_type}"
    if staging:
        base += "?staging=1"

    headers = {
        "Authorization": f"Bearer {os.getenv('ICU_OAUTH', '')}",
        "User-Agent": "IntervalsGPTCoachLocal/1.0"
    }

    print(f"[REMOTE] Fetching full {report_type} report (staging={staging}) from {base}")
    resp = requests.get(base, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    outname = f"report_{report_type}_{'staging' if staging else 'prod'}_{fmt}.json"
    Path("reports").mkdir(exist_ok=True)
    Path(f"reports/{outname}").write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"[REMOTE] ✅ Saved {outname}")
    print(f"[REMOTE] keys={list(data.keys())}")
    return data

# ─────────────────────────────────────────────
# MAIN REPORT GENERATION
# ─────────────────────────────────────────────
def generate_full_report(report_type="weekly", output_path=None, output_format="markdown",
                         prefetch=False, staging=False):
    """Run report and capture logs and output into one file."""
    buffer = io.StringIO()
    os.environ["REPORT_TYPE"] = report_type.lower()

    if not output_path:
        Path("reports").mkdir(parents=True, exist_ok=True)
        suffix = ""
        if prefetch:
            suffix = "_prefetch_staging" if staging else "_prefetch_prod"
        output_path = Path("reports") / f"report_{report_type}{suffix}.{output_format}"

    if prefetch:
        print(f"[PREFETCH] Using Worker prehydrated report (staging={staging})")
        data = fetch_remote_report(report_type, fmt=output_format, staging=staging)

        log_output = data.get("logs", "")
        if output_format == "semantic":
            full_output = {
                "status": data.get("status", "ok"),
                "message": f"{report_type.title()} report (prefetched)",
                "semantic_graph": data.get("semantic_graph", {}),
                "logs": log_output,
            }
        else:
            md_output = data.get("markdown", "")
            full_output = (
                f"# 🧾 {report_type.title()} Audit Report (Prefetch)\n\n"
                "## Execution Logs\n\n"
                "```\n" + log_output + "\n```\n\n"
                "## Rendered Markdown Report\n\n"
                + md_output.strip()
            )

    else:
        debug({}, f"🧭 Generating {report_type.title()} Report (local mode)")
        with redirect_stdout(buffer):
            result = run_report(
                reportType=report_type,
                include_coaching_metrics=True,
                output_format=output_format,
            )

        if isinstance(result, tuple):
            report = result[0]
            logs = buffer.getvalue()
        else:
            report = result
            logs = buffer.getvalue()

        raw_logs = logs.splitlines()
        skip_terms = ["snapshot", "trace", "json", "context", "activities_full", "DataFrame"]
        log_output = "\n".join(
            [line for line in raw_logs if not any(term in line.lower() for term in skip_terms)]
        ).strip()

        if isinstance(report, dict):
            if output_format == "semantic":
                semantic_output = report.get("semantic_graph", {})
                full_output = {
                    "status": "ok",
                    "message": f"{report_type.title()} report generated",
                    "semantic_graph": semantic_output,
                    "logs": log_output,
                }
            else:
                md_output = report.get("markdown", "")
                full_output = (
                    f"# 🧾 {report_type.title()} Audit Report\n\n"
                    "## Execution Logs\n\n"
                    "```\n" + log_output + "\n```\n\n"
                    "## Rendered Markdown Report\n\n"
                    + md_output.strip()
                )
        else:
            full_output = {"markdown": str(report), "logs": log_output}

    # ─── Write to disk
    if isinstance(full_output, dict):
        Path(output_path).write_text(json.dumps(full_output, indent=2, default=str), encoding="utf-8")
    else:
        Path(output_path).write_text(full_output, encoding="utf-8")

    print(f"✅ {report_type.title()} report written to {Path(output_path).resolve()}")

# ─────────────────────────────────────────────
# CLI ENTRY POINT
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Generate audit reports for different data ranges.")
    parser.add_argument("--range", type=str.lower,
                        choices=["weekly", "season", "wellness", "summary"],
                        default="weekly")
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--format", type=str.lower,
                        choices=["markdown", "semantic"],
                        default="semantic",
                        help="Output format (default: semantic)")
    parser.add_argument("--prefetch", action="store_true",
                        help="Use prehydrated dataset from Railway proxy")
    parser.add_argument("--staging", action="store_true",
                        help="Use staging Railway proxy instead of production")

    args = parser.parse_args()
    generate_full_report(report_type=args.range,
                         output_path=args.output,
                         output_format=args.format,
                         prefetch=args.prefetch,
                         staging=args.staging)

if __name__ == "__main__":
    main()
