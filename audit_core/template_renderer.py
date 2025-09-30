"""
Template Renderer Shim (v16.14-DebugFinal)
Ensures Tier-2 live context (with CTL/ATL/TSB) is passed correctly
to render_unified_report.py without resetting load_metrics.
Adds full debug logging before, during, and after render call.
"""

import importlib
import numpy as np
import sys
from audit_core.utils import debug
from render_unified_report import Report
if "render_unified_report" in sys.modules:
    del sys.modules["render_unified_report"]

def render_template(report_type: str, framework: str, context: dict):
    """Dispatch rendering call to render_unified_report while preserving live context."""

    try:
        renderer = importlib.import_module("render_unified_report")
    except ModuleNotFoundError:
        debug(context,"⚠ render_unified_report.py not found — returning context only.")
        return context

    result = None
    for candidate in ("render_unified_report", "render_report", "main"):
        if hasattr(renderer, candidate):
            func = getattr(renderer, candidate)
            debug(context,f"[Renderer shim] Delegating to {candidate}() in render_unified_report.py")

            try:
                # ✅ Wrap in dict because renderer expects data.get("context")
                wrapped = {"context": context, "type": report_type}

                # --- DEBUG PRE-CALL ---
                debug(context,"\n[DEBUG-TEMPLATE: PRE-CALL]")
                debug(context,"Keys in context:", list(context.keys()))
                debug(context,"load_metrics pre-pass:", context.get("load_metrics"))
                if "_locked_load_metrics" in context:
                    debug(context,"_locked_load_metrics pre-pass:", context["_locked_load_metrics"])
                debug(context,"Report type:", report_type)
                debug(context,"-" * 60)

                # --- SAFETY: sanitize NumPy scalars pre-serialization ---
                for k, v in list(context.items()):
                    if isinstance(v, np.generic):
                        context[k] = v.item()

                # --- Deep sanitize nested dicts like load_metrics or derived_metrics ---
                def _sanitize_nested(obj):
                    if isinstance(obj, dict):
                        return {kk: _sanitize_nested(vv) for kk, vv in obj.items()}
                    elif isinstance(obj, list):
                        return [_sanitize_nested(x) for x in obj]
                    elif isinstance(obj, np.generic):
                        return obj.item()
                    return obj

                context = _sanitize_nested(context)

                # --- CALL RENDERER ---
                result = func(wrapped)
                debug(context, f"[TRACE-DESERIALIZE] wrapped.context totals={wrapped['context'].get('totalHours')}, {wrapped['context'].get('totalTss')}")

                # --- DEBUG POST-CALL ---
                debug(context,"\n[DEBUG-TEMPLATE: POST-CALL]")
                debug(context,"Renderer function executed:", candidate)
                debug(context,"Result type:", type(result).__name__)
                if isinstance(result, dict):
                    debug(context,"Result keys:", list(result.keys()))
                debug(context,"load_metrics still in context:",
                      "load_metrics" in context)
                debug(context,"load_metrics post-render:", context.get("load_metrics"))
                debug(context,"-" * 60)

            except Exception as e:
                debug(context,f"⚠ Renderer call failed: {e}")
                return context
            break
    else:
        debug(context,"⚠ No valid renderer entry found — returning context only.")
        return context

    # --- Normalize to Report object ---
    if isinstance(result, Report):
        debug(context,"[DEBUG-TEMPLATE] Renderer returned a Report object.")
        return result

    report = Report()
    if isinstance(result, str):
        debug(context,"[DEBUG-TEMPLATE] Renderer returned markdown string.")
        report["markdown"] = result
    elif isinstance(result, dict):
        debug(context,"[DEBUG-TEMPLATE] Renderer returned dict — updating report.")
        report.update(result)
    else:
        debug(context,"[DEBUG-TEMPLATE] Renderer returned unknown type, coercing to string.")
        report["content"] = str(result)

    # ✅ Ensure live context persists
    report["context"] = context
    report.add_line("✅ Auto-wrapped by template_renderer (live context preserved)")

    debug(context,"\n[DEBUG-TEMPLATE: FINAL]")
    debug(context,"Final report keys:", list(report.keys()))
    debug(context,"Final context load_metrics:", context.get("load_metrics"))
    debug(context,"=" * 80)

    return report
    debug(context, f"[TRACE-FINAL-RETURN] report.summary={report.get('summary', {})}")
    debug(context, f"[TRACE-FINAL-RETURN] context.totalHours={context.get('totalHours')}, context.totalTss={context.get('totalTss')}")

