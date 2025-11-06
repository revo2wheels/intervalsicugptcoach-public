"""
report_schema_guard.py — v16.1
Schema-level validation of report output fields.
"""

FRAMEWORK_SCHEMA = {
    "header": ["athlete", "period", "discipline"],
    "summary": ["totalHours", "totalTss", "variance", "zones"],
    "metrics": ["derived", "load", "adaptation", "trend", "correlation"],
    "actions": ["list"],
    "footer": ["framework", "version"]
}

def enforce_report_schema(report):
    for section, keys in FRAMEWORK_SCHEMA.items():
        if section not in report:
            raise ValueError(f"❌ Missing section: {section}")
        for key in keys:
            if key not in report[section]:
                raise KeyError(f"❌ Missing key {key} in section {section}")
    print("✅ Report schema validated.")
    return True
