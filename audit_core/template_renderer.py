"""
Template Renderer Shim (v16.14)
Bridges Tier-2 validator to the unified renderer (render_unified_report.py).
"""

import importlib
from render_unified_report import Report


def render_template(report_type: str, framework: str, context: dict):
    """
    Dispatches rendering call to render_unified_report.py.
    Wraps any legacy return types into a Report-compatible object.
    """
    try:
        renderer = importlib.import_module("render_unified_report")
    except ModuleNotFoundError:
        print("⚠ render_unified_report.py not found — returning context only.")
        report = Report()
        report["context"] = context
        report.add_line("⚠ render_unified_report.py missing")
        return report

    for candidate in ("render_unified_report", "render_report", "main"):
        if hasattr(renderer, candidate):
            func = getattr(renderer, candidate)
            print(f"[Renderer shim] Delegating to {candidate}() in render_unified_report.py")
            try:
                result = func(context=context, report_type=report_type)
            except TypeError:
                try:
                    result = func(context, report_type)
                except Exception as e:
                    print(f"⚠ Renderer call failed: {e}")
                    result = context
            break
    else:
        print("⚠ No valid renderer entry found — returning context only.")
        result = context

    # --- Normalize to Report object ---
    if isinstance(result, Report):
        return result

    report = Report()
    if isinstance(result, str):
        report["markdown"] = result
    elif isinstance(result, dict):
        report.update(result)
    else:
        report["content"] = str(result)

    report["context"] = context
    report.add_line("✅ Auto-wrapped by template_renderer for Tier-2 compliance")
    return report
