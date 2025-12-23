"""
Template Renderer Shim (v17.0 — Semantic Mode)
Ensures Tier-2 live context (CTL/ATL/TSB, totals, etc.) is preserved.
Skips legacy Markdown render unless explicitly requested.
Adds compact debug logging for traceability.
"""

import importlib
import numpy as np
import sys
from audit_core.utils import debug
from render_unified_report import Report

# Ensure no cached copy interferes
if "render_unified_report" in sys.modules:
    del sys.modules["render_unified_report"]


def render_template(report_type: str, framework: str, context: dict):
    """Dispatch rendering call, skipping legacy Markdown path in semantic mode."""

    # --- 🧩 Skip legacy markdown render when semantic_json_enabled=True ---
    if context.get("semantic_json_enabled", True):
        debug(context, "[Renderer shim] Skipping render_unified_report (semantic_json_enabled=True)")
        report = Report()
        report["context"] = context
        report["note"] = "semantic JSON mode active — markdown renderer skipped"
        return report

    # --- Otherwise fallback to legacy Markdown renderer ---
    try:
        renderer = importlib.import_module("render_unified_report")
    except ModuleNotFoundError:
        debug(context, "⚠ render_unified_report.py not found — returning context only.")
        report = Report()
        report["context"] = context
        return report

    result = None
    for candidate in ("render_unified_report", "render_report", "main"):
        if hasattr(renderer, candidate):
            func = getattr(renderer, candidate)
            debug(context, f"[Renderer shim] Delegating to {candidate}() in render_unified_report.py")

            try:
                # ✅ Wrap in dict because renderer expects data.get("context")
                wrapped = {"context": context, "type": report_type}

                # --- PRE-CALL DEBUG ---
                debug(context, f"[DEBUG-TEMPLATE: PRE] report_type={report_type}, keys={len(context.keys())}")
                if "load_metrics" in context:
                    debug(context, f"load_metrics pre-pass: {context.get('load_metrics')}")

                # --- Sanitize NumPy scalars and nested dicts ---
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
                debug(context, f"[TRACE] Renderer call succeeded via {candidate}")

            except Exception as e:
                debug(context, f"⚠ Renderer call failed: {e}")
                return Report()

            break
    else:
        debug(context, "⚠ No valid renderer entry found — returning context only.")
        report = Report()
        report["context"] = context
        return report

    # --- Normalize to Report object ---
    if isinstance(result, Report):
        debug(context, "[Renderer shim] Renderer returned a Report object.")
        return result

    report = Report()
    if isinstance(result, str):
        report["markdown"] = result
    elif isinstance(result, dict):
        report.update(result)
    else:
        report["content"] = str(result)

    # ✅ Preserve context + trace info
    report["context"] = context
    report.add_line("✅ Auto-wrapped by template_renderer (live context preserved)")

    debug(context, "[Renderer shim] Completed render_template normalization.")
    return report
