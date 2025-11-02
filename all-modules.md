<!-- Renderer binding block -->
# 🧭 Module Source Map
manifest_origin: github
module_base: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach/main/

bindings:
  Glossary & Placeholders: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach/main/Glossary%20%26%20Placeholders.md
  Coaching Cheat Sheet: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach/main/Coaching%20Cheat%20Sheet.md
  Coaching Heuristics Pack: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach/main/Coaching%20Heuristics%20Pack.md
  Advanced Marker Reference: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach/main/Advanced%20Marker%20Reference.md
  Coach Profile: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach/main/Coach%20profile.md
  Unified Reporting Framework: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach/main/Unified%20Reporting%20Framework.md
  Unified_UI_v5.1: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach/main/Unified_UI_v5.1/

---

# 📘 All Modules Index — v16
This document defines the authoritative reference chain for all rule, computation, and knowledge modules used by the **IntervalsICU GPT Coach**.  
Each module is stored separately in the **root** or **/audit_core/** directory and is dynamically fetched by the app.

---

## 🔗 Module References

| Module | Purpose | File Path |
|:--|:--|:--|
| **1. Glossary & Placeholders** | Core tokens, data placeholders, and variable mappings for audits and reports. | [Glossary & Placeholders.md](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach/main/Glossary%20%26%20Placeholders.md) |
| **2. Coaching Cheat Sheet** | Quick reference thresholds and classification tables (load, recovery, quality). | [Coaching Cheat Sheet.md](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach/main/Coaching%20Cheat%20Sheet.md) |
| **3. Coaching Heuristics Pack** | Decision logic, sport-specific heuristics, and phase rules (Seiler, Friel). | [Coaching Heuristics Pack.md](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach/main/Coaching%20Heuristics%20Pack.md) |
| **4. Advanced Marker Reference** | Derived metrics and computation definitions (ACWR, Monotony, Strain, Durability, FatOx). | [Advanced Marker Reference.md](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach/main/Advanced%20Marker%20Reference.md) |
| **5. Coach Profile** | Coach’s expertise, frameworks, and marker integration models. | [Coach profile.md](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach/main/Coach%20profile.md) |
| **6. Unified Reporting Framework** | Standardized output schema for Weekly, Seasonal, and Executive Reports. | [Unified Reporting Framework.md](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach/main/Unified%20Reporting%20Framework.md) |

---

## 🧩 Audit Core (Python Modules)

| Module | Function | File Path |
|:--|:--|:--|
| **Tier-0 — Pre-Audit** | Fetches athlete context, activities, and wellness; initializes audit state. | [audit_core/tier0_pre_audit.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach/main/audit_core/tier0_pre_audit.py) |
| **Tier-1 — Audit Controller** | Validates dataset integrity, duplicates, and total time variance. | [audit_core/tier1_controller.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach/main/audit_core/tier1_controller.py) |
| **Tier-2 Step-2 — Event Completeness** | Ensures each event is valid, builds display-only daily summary. | [audit_core/tier2_event_completeness.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach/main/audit_core/tier2_event_completeness.py) |
| **Tier-2 Step-3 — Enforce Event-Only Totals** | Computes totalHours and totalTss strictly from event-level data. | [audit_core/tier2_enforce_event_only_totals.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach/main/audit_core/tier2_enforce_event_only_totals.py) |
| **Tier-2 Step-6 — Derived Metrics** | Calculates ACWR, Monotony, Strain, Polarisation, Recovery Index. | [audit_core/tier2_derived_metrics.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach/main/audit_core/tier2_derived_metrics.py) |
| **Tier-2 Step-7 — Evaluate Actions** | Generates adaptive coaching actions from verified metrics. | [audit_core/tier2_actions.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach/main/audit_core/tier2_actions.py) |

---

## 🧩 Load Order
1. Glossary & Placeholders.md  
2. Coaching Cheat Sheet.md  
3. Coaching Heuristics Pack.md  
4. Advanced Marker Reference.md  
5. Coach profile.md  
6. Unified Reporting Framework.md  
7. audit_core/tier0_pre_audit.py  
8. audit_core/tier1_controller.py  
9. audit_core/tier2_event_completeness.py  
10. audit_core/tier2_enforce_event_only_totals.py  
11. audit_core/tier2_derived_metrics.py  
12. audit_core/tier2_actions.py
13. audit_core/tier2_render_validator.py

---

## ⚙️ Version and Integrity
- Ruleset Version: **v16**
- Framework Version: **Unified Reporting Framework v5.1**
- Audit Modules: **audit_core v16 chain (Tier-0 → Tier-2)**
- Halt Condition: any missing or invalid module reference.

---

## ✅ Usage
The `loadAllRules` action now fetches all Markdown and Python modules listed here.  
Audit logic is executed in this strict sequence:

```python
from audit_core.tier0_pre_audit import run_tier0_pre_audit
from audit_core.tier1_controller import run_tier1_controller
from audit_core.tier2_event_completeness import validate_event_completeness
from audit_core.tier2_enforce_event_only_totals import enforce_event_only_totals
from audit_core.tier2_derived_metrics import compute_derived_metrics
from audit_core.tier2_actions import evaluate_actions
