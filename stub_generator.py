# === generate_stubs.py ===
# Creates no-op placeholders for missing audit_core and UIcomponents modules.
# Safe to run once inside ChatGPT or locally 

import os

# Define stub modules
STUB_MODULES = [
    "audit_core.report_controller",
    "audit_core.tier0_pre_audit",
    "audit_core.tier1_controller",
    "audit_core.tier2_data_integrity",
    "audit_core.tier2_event_completeness",
    "audit_core.tier2_enforce_event_only_totals",
    "audit_core.tier2_calculation_integrity",
    "audit_core.tier2_derived_metrics",
    "audit_core.tier2_extended_metrics",
    "audit_core.tier2_actions",
    "audit_core.tier2_render_validator",
    "audit_core.report_schema_guard",
    "audit_core.utils",
    "UIcomponents.icon_pack",
    "athlete_profile",
    "coaching_profile",
    "coaching_heuristics",
    "coaching_cheat_sheet",
]

# Each stub file contents
TEMPLATE = '''"""
Auto-generated stub for {module}.
Ensures import safety in ChatGPT sandbox.
"""
def debug(ctx=None, *msg): 
    print("[DEBUG-STUB]", *msg)

class Report(dict): 
    pass

class AuditHalt(Exception): 
    pass

def enforce_report_schema(report): 
    return True

def validate_report_output(context, report): 
    return {{"validated": True}}

def enforce_event_only_totals(context): 
    return context
'''

for module in STUB_MODULES:
    path = module.replace('.', os.sep) + ".py"
    os.makedirs(os.path.dirname("/stubs"), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(TEMPLATE.format(module=module))
        print(f"✅ Created stub: {path}")
    else:
        print(f"⚠️ Skipped (exists): {path}")

print("\nAll stubs generated successfully.")
