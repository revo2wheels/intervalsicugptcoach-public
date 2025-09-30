#!/usr/bin/env python3
import os, hashlib, json, sys
from audit_core.utils import debug

MODULE_DIR = os.path.dirname(__file__)
MODULES = [
    "tier0_pre_audit.py",
    "tier1_controller.py",
    "tier2_event_completeness.py",
    "tier2_enforce_event_only_totals.py",
    "tier2_derived_metrics.py",
    "tier2_actions.py",
    "tier2_render_validator.py",
    "report_validator.py"
]

OUT_FILE = os.path.join(MODULE_DIR, ".integrity.json")

def sha256sum(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    baseline = {}
    for mod in MODULES:
        full = os.path.join(MODULE_DIR, mod)
        if os.path.exists(full):
            baseline[os.path.splitext(mod)[0]] = sha256sum(full)
        else:
            debug(context,f"⚠ Missing: {mod}")
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(baseline, f, indent=2)
        debug(context,f"Integrity baseline written to {OUT_FILE}")
        debug(context,f"{len(baseline)} modules hashed successfully.")

if __name__ == "__main__":
    sys.exit(main())
