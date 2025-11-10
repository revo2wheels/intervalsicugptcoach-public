"""
report_schema_guard.py — v16.1
Schema-level validation of report output fields.
"""

from audit_core.utils import debug

FRAMEWORK_SCHEMA = {
    "header": ["athlete", "period", "discipline"],
    "summary": ["totalHours", "totalTss", "variance", "zones"],
    "metrics": ["derived", "load", "adaptation", "trend", "correlation"],
    "actions_block": ["list"],   # <-- expects dict now
    "footer": ["framework", "version"]
}


def enforce_report_schema(report):
    # --- TEMPORARY DEBUG ---
    print("\n[DEBUG-GUARD] --- Report schema diagnostic ---")
    print("[DEBUG-GUARD] Report top-level keys:", list(report.keys()))
    if "actions" in report:
        print("[DEBUG-GUARD] actions type:", type(report["actions"]))
        if isinstance(report["actions"], dict):
            print("[DEBUG-GUARD] actions keys:", list(report["actions"].keys()))
        else:
            print("[DEBUG-GUARD] actions value (non-dict):", report["actions"])
    else:
        print("[DEBUG-GUARD] 'actions' not in report")
    print("[DEBUG-GUARD] ---------------------------------\n")

    for section, keys in FRAMEWORK_SCHEMA.items():
        if section not in report:
            raise ValueError(f"❌ Missing section: {section}")

        section_data = report[section]

        # Skip validation for non-dict types (e.g. list sections like report["actions"])
        if not isinstance(section_data, dict):
            continue

        for key in keys:
            if key not in section_data:
                raise KeyError(f"❌ Missing key {key} in section {section}")

        return True
