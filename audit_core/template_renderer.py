"""
Template Renderer Shim (Semantic Mode Only)
Simplified: drops all legacy Markdown render logic.
Ensures Tier-2 context is passed cleanly to semantic_json_builder.
"""

import numpy as np
from audit_core.utils import debug


class Report(dict):
    """Lightweight container for semantic report output."""
    def add_line(self, line: str):
        self.setdefault("trace", []).append(line)


def render_template(report_type: str, framework: str, context: dict):
    """Semantic-only renderer entrypoint — skips legacy Markdown paths entirely."""
    debug(context, "[Renderer shim] Semantic-only mode: skipping render_unified_report")

    # Sanitize NumPy scalars and nested dicts for JSON serialization
    def _sanitize(obj):
        if isinstance(obj, dict):
            return {k: _sanitize(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_sanitize(x) for x in obj]
        elif isinstance(obj, np.generic):
            return obj.item()
        return obj

    context = _sanitize(context)

    report = Report()
    report["context"] = context
    report["note"] = "Semantic-only mode — no markdown render executed"
    report.add_line("✅ Semantic renderer active, legacy markdown skipped")

    return report
