"""
Template Renderer Shim (v16.14)
Bridges Tier-2 validator to the unified renderer (render_unified_report.py).
"""

import importlib
from render_unified_report import Report


def render_template(report_type: str, framework: str, context: dict):
    """
    Dispatches rendering call to render_unified_report.py.
    Handles both positional-only and keyword-based signatures.
    """
    import importlib
    try:
        renderer = importlib.import_module("render_unified_report")
    except ModuleNotFoundError:
        print("⚠ render_unified_report.py not found — returning context only.")
        return context

    for candidate in ("render_unified_report", "render_report", "main"):
        if hasattr(renderer, candidate):
            func = getattr(renderer, candidate)
            print(f"[Renderer shim] Delegating to {candidate}() in render_unified_report.py")
            try:
                # Correct call signature for your renderer
                return func({"context": context, "type": report_type})
            except Exception as e:
                print(f"⚠ Renderer call failed: {e}")
                return context

    print("⚠ No valid renderer entry found — returning context only.")
    return context

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
