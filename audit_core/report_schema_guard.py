"""
report_schema_guard.py — v16.1-patched
Schema-level validation of report output fields.
"""

from audit_core.utils import debug

FRAMEWORK_SCHEMA = {
    "header": ["athlete", "period", "discipline"],
    "summary": ["totalHours", "totalTss", "variance", "zones"],
    "metrics": ["derived", "load", "adaptation", "trend", "correlation"],
    "actions_block": ["list"],   # dict form for schema
    "footer": ["framework", "version"]
}

def enforce_report_schema(report):
    print("\n[DEBUG-GUARD] --- Report schema diagnostic ---")
    print("[DEBUG-GUARD] Report top-level keys:", list(report.keys()))

    for section, keys in FRAMEWORK_SCHEMA.items():
        if section not in report:
            raise ValueError(f"❌ Missing section: {section}")

        section_data = report[section]
        if not isinstance(section_data, dict):
            print(f"[SCHEMA] Skipping non-dict section '{section}' ({type(section_data).__name__})")
            continue

        for key in keys:
            if key not in section_data:
                # --- Auto-fix only for noncritical footer keys ---
                if section == "footer":
                    defaults = {
                        "framework": "IntervalsICU-GPTCoach",
                        "version": "3.9.13-dual-mode",
                        "build": "season-lite",
                        "validated": True,
                    }
                    if key in defaults:
                        section_data[key] = defaults[key]
                        print(f"⚠️ Auto-fix: injected missing key '{key}' in section '{section}' → {defaults[key]}")
                        continue
                # --- Fail for any other missing key ---
                raise KeyError(f"❌ Missing key '{key}' in section '{section}'")

    # ✅ Dual actions structure enforcement
    if "actions" not in report and "actions_block" not in report:
        raise ValueError("❌ Both 'actions' and 'actions_block' missing — schema invalid")

    if "actions_block" in report and not isinstance(report["actions_block"], dict):
        raise TypeError("❌ actions_block must be a dict")

    print("[DEBUG-GUARD] ✅ Schema validation passed for all sections\n")
    return True


