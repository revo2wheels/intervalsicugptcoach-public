"""
Unified Icon Pack — v16.1.3-EOD-004
Purpose:
  Provides standardized icons for all report and audit sections.
  Activated when `force_icon_pack=True` in render context.
  Compatible with Unified Reporting Framework v5.1.
"""

ICON_CARDS = {
    "ok": "✅",
    "warn": "⚠️",
    "info": "ℹ️",
    "fatigue": "🩵",
    "load": "📈",
    "polarisation": "🎯",
    "recovery": "🛌",
    "retest": "🔄",
    "performance": "🚴‍♂️",
    "summary": "🧩",
    "efficiency": "⚙️",
    "quality": "🎯",
    "wellness": "💤",
    "actions": "🧭",
    "audit": "🧩",
    "rest_day": "🛌",
}

# --- Compatibility aliases for validator checks ---
ICON_CARDS["🛌 Rest Day"] = "🛌"
ICON_CARDS["Rest Day"] = "🛌"
ICON_CARDS["🛌"] = "🛌"


ICON_LEGEND = """
## 🧭 Icon Legend (Reporting Sections)

| Icon | Section |
|:--|:--|
| 🧭 | Header / Metadata |
| 📊 | Key Stats |
| 📅 | Event Log |
| 🧩 | Training Quality |
| 🔋 | Fat-Oxidation Block |
| 🔬 | Efficiency & Adaptation |
| 💓 | Recovery & Wellness |
| ⚖️ | Load Balance |
| 🧠 | Performance Insights |
| 🪜 | Actions |
"""

def get_icon(key: str) -> str:
    """Return icon for a given key, or empty string if undefined."""
    return ICON_CARDS.get(key, "")

def render_icon_legend() -> str:
    """Return formatted legend markdown."""
    return ICON_LEGEND
