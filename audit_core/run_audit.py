"""
Unified Weekly Audit Runner — v16.1
Executes Tier-0 → Tier-2 pipeline and writes verified Unified Framework JSON output.
"""

import os
import json
import argparse
from datetime import datetime
from audit_core import (
    tier0_pre_audit,
    tier1_controller,
    tier2_event_completeness,
    tier2_enforce_event_only_totals,
    tier2_derived_metrics,
    tier2_actions
)

def main():
    parser = argparse.ArgumentParser(description="Run v16.1 full audit chain")
    parser.add_argument("--start", required=True, help="Oldest date YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="Newest date YYYY-MM-DD")
    parser.add_argument("--type", default="Weekly", help="Report type label")
    args = parser.parse_args()

    os.makedirs("reports", exist_ok=True)
    context = {}

    print(f"🟢 Starting audit chain {args.type} ({args.start} → {args.end})")

    # --- Tier 0 ---
    df_activities, wellness, context, auditPartial, auditFinal = tier0_pre_audit.run_tier0_pre_audit(
        args.start, args.end, context
    )

    # --- Tier 1 ---
    df_activities, wellness, context = tier1_controller.run_tier1_controller(
        df_activities, wellness, context
    )

    # --- Tier 2: Event completeness & totals ---
    df_events, df_daily = tier2_event_completeness.validate_event_completeness(df_activities)
    context = tier2_enforce_event_only_totals.enforce_event_only_totals(df_events, context)

    # --- Tier 2: Derived metrics ---
    context = tier2_derived_metrics.compute_derived_metrics(df_daily, context)

    # --- Tier 2: Actions ---
    context = tier2_actions.evaluate_actions(context)

    # --- Finalize ---
    context["auditFinal"] = True
    context["timestamp"] = datetime.utcnow().isoformat()

    report = {
        "type": args.type,
        "window": [args.start, args.end],
        "athlete": context.get("athlete", {}).get("id", "unknown"),
        "context": context,
    }

    outpath = f"reports/{args.type.lower()}_{args.start}_{args.end}.json"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"✅ Audit completed. Output written to {outpath}")

if __name__ == "__main__":
    main()
