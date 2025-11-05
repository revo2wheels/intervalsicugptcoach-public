"""
Template Renderer Shim (v16.14)
Bridges Tier-2 validator to the actual renderer (render_unified_report.py).
"""

import importlib

def render_template(report_type: str, framework: str, context: dict):
    """
    Dispatch unified rendering call to render_unified_report.py.
    Returns rendered report (dict or Markdown string).
    """
    try:
        renderer = importlib.import_module("render_unified_report")
    except ModuleNotFoundError:
        print("⚠ render_unified_report.py not found — returning context only.")
        return context

    # Try known entry points in render_unified_report.py
    for candidate in ("render_unified_report", "render_report", "main"):
        if hasattr(renderer, candidate):
            func = getattr(renderer, candidate)
            print(f"[Renderer shim] Delegating to {candidate}() in render_unified_report.py")
            return func(context=context, report_type=report_type)

    print("⚠ No valid renderer entry found — returning context.")
    return context
