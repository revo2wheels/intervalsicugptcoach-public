"""
Unified Weekly Audit Runner — v16.14-Independent
Executes Tier-0 → Tier-2 pipeline and writes verified Unified Framework JSON output.
Ensures Tier-2 canonical totals are enforced using raw Tier-0 data.
"""

import os
import json
import argparse
import numpy as np#
from audit_core.utils import debug
from datetime import datetime, timezone, date
from audit_core import (
    tier0_pre_audit,
    tier1_controller,
    tier2_event_completeness,
    tier2_enforce_event_only_totals,
    tier2_derived_metrics,
    tier2_actions,
)

def print_totals(tag, df=None, context=None):
    debug(context,f"\n🔹 [Totals Debug — {tag}]")
    if df is not None and not df.empty:
        if "moving_time" in df.columns:
            total_hours = df["moving_time"].sum() / 3600
            debug(context,f"   Σ(moving_time)/3600 = {total_hours:.2f}")
        if "icu_training_load" in df.columns:
            total_tss = df["icu_training_load"].sum()
            debug(context,f"   Σ(icu_training_load) = {total_tss:.1f}")
    if context:
        if "totalHours" in context or "totalTss" in context:
            debug(context,f"   context → totalHours={context.get('totalHours')} totalTss={context.get('totalTss')}")
    debug(context,"--------------------------------------------------")


def main():
    parser = argparse.ArgumentParser(description="Run v16.14 full audit chain (independent Tier-2)")
    parser.add_argument("--start", required=True, help="Oldest date YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="Newest date YYYY-MM-DD")
    parser.add_argument("--type", default="Weekly", help="Report type label")

    # 👇 Diagnostic flag
    parser.add_argument("--diag", action="store_true", help="Enable diagnostic mode and verbose Tier-2 debug prints")

    args = parser.parse_args()

    os.makedirs("reports", exist_ok=True)

    # 👇 Diagnostic context toggle
    if args.diag:
        debug(context,"🧩 Diagnostic mode enabled — verbose Tier-2 debug active.")
        context = {"diag": True}
    else:
        context = {}

    debug(context,f"🟢 Starting audit chain {args.type} ({args.start} → {args.end})")

    # --- Tier 0: Pre-Audit ---------------------------------------------------
    df_activities, wellness, context, auditPartial, auditFinal = tier0_pre_audit.run_tier0_pre_audit(
        args.start, args.end, context
    )
    print_totals("Tier-0 (raw activities)", df_activities)

    # store the raw activities for Tier-2 independence
    context["df_raw_activities"] = df_activities.copy()

    # --- Tier 1: Integrity Controller ----------------------------------------
    df_activities, wellness, context = tier1_controller.run_tier1_controller(
        df_activities, wellness, context
    )
    print_totals("Tier-1 (raw activities)", df_activities)

    # --- Tier 2: Event completeness & independent totals ---------------------
    df_events, df_daily = tier2_event_completeness.validate_event_completeness(df_activities)
    print_totals("Tier-2 (raw activities)", df_activities)

    # 🔄 Use the validated Tier-2 events dataset directly (no independent rebuild)
    context = tier2_enforce_event_only_totals.enforce_event_only_totals(df_events, context)

    # --- Tier 2: Derived metrics ---------------------------------------------
    context = tier2_derived_metrics.compute_derived_metrics(df_daily, context)
    print_totals("Tier-2 (raw activities)", df_activities)

    # --- Tier 2: Actions -----------------------------------------------------
    context = tier2_actions.evaluate_actions(context)

    # --- Safety Enforcement --------------------------------------------------
    # Ensure canonical totals exist even if earlier steps were bypassed.
    if "totalHours" not in context or "totalTss" not in context:
        debug(context,"⚙️  Enforcing canonical totals before finalization …")
        try:
            context = tier2_enforce_event_only_totals.enforce_event_only_totals(None, context)
        except Exception as e:
            debug(context,f"⚠️  Tier-2 enforcement fallback failed: {e}")

    # --- Finalize ------------------------------------------------------------
    context["auditFinal"] = True
    context["timestamp"] = datetime.now(timezone.utc).isoformat()

    # 🧹 Remove or summarize DataFrames before JSON serialization
    for key in list(context.keys()):
        if str(context[key].__class__.__name__) == "DataFrame":
            context[key] = {
                "rows": len(context[key]),
                "columns": list(context[key].columns),
                "preview": context[key].head(3).to_dict(orient="records"),
            }

    report = {
        "type": args.type,
        "window": [args.start, args.end],
        "athlete": context.get("athlete", {}).get("id", "unknown"),
        "context": context,
    }

    # --- JSON-safe serializer for datetime/date ---
    def safe_json(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
            return None
        raise TypeError(f"Type {obj.__class__.__name__} not serializable")

    outpath = f"reports/{args.type.lower()}_{args.start}_{args.end}.json"

    try:
        with open(outpath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=safe_json, allow_nan=False)
    except Exception as e:
        debug(context,f"❌ JSON dump failed: {e}")
        debug(context,"🩹 Attempting fallback with NaN-safe sanitization …")

        def sanitize(o):
            """Recursively make object JSON-safe (handles numpy, NaN, inf, datetime, bool)."""
            if isinstance(o, dict):
                return {str(k): sanitize(v) for k, v in o.items()}
            elif isinstance(o, list):
                return [sanitize(v) for v in o if v is not None]
            elif isinstance(o, float):
                if np.isnan(o) or np.isinf(o):
                    return 0.0
                return float(o)
            elif isinstance(o, (np.integer, int)):
                return int(o)
            elif isinstance(o, (np.bool_, bool)):
                return bool(o)
            elif isinstance(o, (datetime, date)):
                return o.isoformat()
            elif o is None:
                return None
            else:
                try:
                    json.dumps(o)
                    return o
                except Exception:
                    return str(o)

        cleaned = sanitize(report)

        tmp_path = outpath + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, indent=2, ensure_ascii=False)

        # ✅ Validation step — verify JSON is actually valid before replacing the file
        import json as _json
        try:
            with open(tmp_path, "r", encoding="utf-8") as f:
                _json.load(f)
            os.replace(tmp_path, outpath)
            debug(context,"✅ JSON validation passed. Safe fallback file written.")
        except Exception as ve:
            debug(context,f"❌ Validation failed: {ve}")
            debug(context,f"⚠️ Corrupted JSON output — see {tmp_path} for debugging.")
            raise

    debug(context,"✅ Audit completed. Canonical totals enforced (Tier-2 integrated).")
    debug(context,f"📁 Output written to {outpath}")


# --- Safe exit wrapper ----------------------------------------------------
if __name__ == "__main__":
    import sys
    try:
        main()
        sys.exit(0)
    except Exception as e:
        debug(context,f"❌ Audit runner failed: {e}")
        sys.exit(1)
