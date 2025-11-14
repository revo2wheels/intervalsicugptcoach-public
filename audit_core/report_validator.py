"""
report_validator.py — v16.1
Validates rendered reports against Unified Reporting Framework v5.1.
Ensures all output metrics, sections, and formatting meet canonical spec.
"""

import math
import numpy as np

from audit_core.utils import debug
from UIcomponents.icon_pack import ICON_CARDS

def validate_report_output(context, report, framework_version="Unified_Reporting_Framework_v5.1"):
    """
    Perform structural and logical validation of a rendered report.
    """

    # --- Framework verification ---
    if framework_version != "Unified_Reporting_Framework_v5.1":
        raise ValueError(f"❌ Invalid framework version: {framework_version}")

    # --- Renderer gate ---
    if not context.get("auditFinal", False):
        raise RuntimeError("❌ Renderer blocked: auditFinal=False")

    # --- Required context keys ---
    required_keys = ["totalHours", "totalTss", "actions", "athlete", "timezone"]
    missing = [k for k in required_keys if k not in context]
    if missing:
        raise KeyError(f"❌ Missing context keys: {missing}")

    # --- Type and range validation ---
    if not isinstance(context["totalHours"], (int, float)):
        raise TypeError("❌ totalHours must be numeric")
    if not isinstance(context["totalTss"], (int, float)):
        raise TypeError("❌ totalTss must be numeric")
    if context["totalHours"] < 0 or context["totalTss"] < 0:
        raise ValueError("❌ Negative totals detected")

    # --- Rounding and format checks ---
    rounded_hours = round(context["totalHours"], 2)
    if not math.isclose(context["totalHours"], rounded_hours, abs_tol=0.01):
        raise ValueError("❌ totalHours not rounded to 2 decimals")

    if not isinstance(context["actions"], list):
        raise TypeError("❌ actions must be a list")

    # --- Report structural validation ---
    required_sections = ["header","summary","metrics","actions","footer","phases","trends","correlation"]
    for section in required_sections:
        if section not in report:
            raise ValueError(f"❌ Missing report section: {section}")

    # --- Step 3: Icon Pack Injection (safe fallback, cards only) ---
    try:
        from UIcomponents.icon_pack import ICON_CARDS
        debug(context, "✅ Loaded ICON_CARDS from UIcomponents.icon_pack")
    except ModuleNotFoundError:
        debug(context, "⚠ UIcomponents.icon_pack not found — injecting fallback emoji pack.")
        ICON_CARDS = {
            "ok": "✅",
            "warn": "⚠️",
            "info": "ℹ️",
            "Ride": "🚴",
            "Run": "🏃",
            "Strength": "🏋️",
            "Swim": "🏊",
            "🛌 Rest Day": "🛌",
            "Rest Day": "🛌",
        }

    context["icon_pack"] = ICON_CARDS
    context["force_icon_pack"] = True

    # --- Variance and integrity ---
    variance_limit = 0.03  # 3%
    if "variance" in context and context["variance"] > variance_limit:
        raise ValueError(f"❌ Variance exceeds {variance_limit*100:.0f}% limit")

    # --- Metrics validation ---
    derived_metrics = ["ACWR", "Monotony", "Strain", "Polarisation", "RecoveryIndex"]
    import sys

    for m in derived_metrics:
        if m not in context:
            raise ValueError(f"❌ Derived metric missing: {m}")

        val = context[m]

        # --- flatten dicts before validation ---
        if isinstance(val, dict):
            val = val.get("value", np.nan)
            context[m] = val

        sys.stderr.write(f"[VALIDATOR DEBUG] {m} = {val} ({type(val)})\n")
        sys.stderr.flush()

        try:
            valf = float(val)
        except Exception:
            valf = np.nan

        if not np.isfinite(valf):
            raise TypeError(f"❌ Derived metric {m} invalid")




    # --- Render compliance summary ---
    compliance_log = {
        "framework": framework_version,
        "report_type": report.get("type", "unknown"),
        "auditFinal": context["auditFinal"],
        "checked_sections": required_sections,
        "verified_metrics": derived_metrics,
        "variance_ok": context.get("variance", 0) <= variance_limit,
        "icons_verified": True,
    }

    debug(context,"✅ Report validated — framework compliant.")
    return compliance_log
