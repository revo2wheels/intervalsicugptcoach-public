"""
Template Renderer Shim (v16.14-DebugFinal)
Ensures Tier-2 live context (with CTL/ATL/TSB) is passed correctly
to render_unified_report.py without resetting load_metrics.
Adds full debug logging before, during, and after render call.
"""

import importlib
from render_unified_report import Report


def render_template(report_type: str, framework: str, context: dict):
    """Dispatch rendering call to render_unified_report while preserving live context."""

    try:
        renderer = importlib.import_module("render_unified_report")
    except ModuleNotFoundError:
        print("⚠ render_unified_report.py not found — returning context only.")
        return context

    result = None
    for candidate in ("render_unified_report", "render_report", "main"):
        if hasattr(renderer, candidate):
            func = getattr(renderer, candidate)
            print(f"[Renderer shim] Delegating to {candidate}() in render_unified_report.py")

            try:
                # ✅ Wrap in dict because renderer expects data.get("context")
                wrapped = {"context": context, "type": report_type}

                # --- DEBUG PRE-CALL ---
                print("\n[DEBUG-TEMPLATE: PRE-CALL]")
                print("Keys in context:", list(context.keys()))
                print("load_metrics pre-pass:", context.get("load_metrics"))
                if "_locked_load_metrics" in context:
                    print("_locked_load_metrics pre-pass:", context["_locked_load_metrics"])
                print("Report type:", report_type)
                print("-" * 60)

                # --- CALL RENDERER ---
                result = func(wrapped)

                # --- DEBUG POST-CALL ---
                print("\n[DEBUG-TEMPLATE: POST-CALL]")
                print("Renderer function executed:", candidate)
                print("Result type:", type(result).__name__)
                if isinstance(result, dict):
                    print("Result keys:", list(result.keys()))
                print("load_metrics still in context:",
                      "load_metrics" in context)
                print("load_metrics post-render:", context.get("load_metrics"))
                print("-" * 60)

            except Exception as e:
                print(f"⚠ Renderer call failed: {e}")
                return context
            break
    else:
        print("⚠ No valid renderer entry found — returning context only.")
        return context

    # --- Normalize to Report object ---
    if isinstance(result, Report):
        print("[DEBUG-TEMPLATE] Renderer returned a Report object.")
        return result

    report = Report()
    if isinstance(result, str):
        print("[DEBUG-TEMPLATE] Renderer returned markdown string.")
        report["markdown"] = result
    elif isinstance(result, dict):
        print("[DEBUG-TEMPLATE] Renderer returned dict — updating report.")
        report.update(result)
    else:
        print("[DEBUG-TEMPLATE] Renderer returned unknown type, coercing to string.")
        report["content"] = str(result)

    # ✅ Ensure live context persists
    report["context"] = context
    report.add_line("✅ Auto-wrapped by template_renderer (live context preserved)")

    print("\n[DEBUG-TEMPLATE: FINAL]")
    print("Final report keys:", list(report.keys()))
    print("Final context load_metrics:", context.get("load_metrics"))
    print("=" * 80)

    return report
