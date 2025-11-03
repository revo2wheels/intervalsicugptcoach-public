<!-- Renderer binding block -->
# 🧭 Module Source Map PUBLIC
manifest_origin: github
module_base: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/

bindings:
  Glossary & Placeholders: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Glossary%20%26%20Placeholders.md
  Coaching Cheat Sheet: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Coaching%20Cheat%20Sheet.md
  Coaching Heuristics Pack: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Coaching%20Heuristics%20Pack.md
  Advanced Marker Reference: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Advanced%20Marker%20Reference.md
  Coach Profile: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Coach%20profile.md
  Unified Reporting Framework: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Unified%20Reporting%20Framework.md
  Unified_UI_v5.1: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Unified_UI_v5.1/

---

# 📘 All Modules Index — v16.1 (Public)
Authoritative reference for all modules used by the **IntervalsICU GPT Coach v16.1**.  
Each module is stored in the **root** or **/audit_core/** directory and dynamically loaded.

---

## 🔗 Module References

| Module | Purpose | File Path |
|:--|:--|:--|
| **1. Glossary & Placeholders** | Core tokens, data placeholders, and variable mappings for audits and reports (includes new markers: FatOxidationIndex, W′bal, BenchmarkIndex, SubjectiveReadinessIndex, HybridMode) | [Glossary & Placeholders.md](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Glossary%20%26%20Placeholders.md) |
| **2. Coaching Cheat Sheet** | Thresholds and classification tables for load, recovery, and training quality, updated for new markers | [Coaching Cheat Sheet.md](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Coaching%20Cheat%20Sheet.md) |
| **3. Coaching Heuristics Pack** | Decision logic, sport-specific heuristics, phase rules (Seiler, Friel, Banister, Foster), including Hybrid Polarised–Sweet Spot rules | [Coaching Heuristics Pack.md](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Coaching%20Heuristics%20Pack.md) |
| **4. Advanced Marker Reference** | Derived metrics and computation definitions (ACWR, Monotony, Strain, Polarisation, Durability Index, Recovery Index, FatOxidationIndex, W′, BenchmarkIndex, SubjectiveReadinessIndex, HybridMode) | [Advanced Marker Reference.md](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Advanced%20Marker%20Reference.md) |
| **5. Coach Profile** | Coach expertise, frameworks, and marker integration models (including Sandbakk, Skiba, Coggan, Noakes, Hybrid) | [Coach profile.md](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Coach%20profile.md) |
| **6. Unified Reporting Framework** | Standardized output schema for Weekly, Seasonal, and Executive Reports, including new markers | [Unified Reporting Framework.md](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Unified%20Reporting%20Framework.md) |

---

## 🧩 Audit Core (Python Modules)

| Tier / Step | Module | Function | File Path |
|:--|:--|:--|:--|
| **Tier-0 — Pre-Audit** | run_tier0_pre_audit | Fetch athlete context, activities, wellness; initialize audit state | [tier0_pre_audit.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier0_pre_audit.py) |
| **Tier-1 — Audit Controller** | run_tier1_controller | Validate dataset integrity, duplicates, total time variance | [tier1_controller.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier1_controller.py) |
| **Tier-2 Step-1 — Data Integrity** | validate_data_integrity | Verify API count matches DataFrame count; halt on missing discipline or date gaps | [tier2_data_integrity.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_data_integrity.py) |
| **Tier-2 Step-2 — Event Completeness** | validate_event_completeness | Ensures each event is valid; builds display-only daily summary | [tier2_event_completeness.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_event_completeness.py) |
| **Tier-2 Step-3 — Enforce Event-Only Totals** | enforce_event_only_totals | Compute totalHours, totalTss strictly from event-level data | [tier2_enforce_event_only_totals.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_enforce_event_only_totals.py) |
| **Tier-2 Step-4 — Calculation Integrity** | validate_calculation_integrity | Confirm Σ(moving_time), Σ(TSS), Σ(distance); halt if variance > 0.1 h | [tier2_calc_integrity.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_calc_integrity.py) |
| **Tier-2 Step-5 — Wellness Validation** | validate_wellness | Align wellness window; refetch/truncate; ignore nulls if load < 40 | [tier2_wellness_validation.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_wellness_validation.py) |
| **Tier-2 Step-6 — Derived Metrics** | compute_derived_metrics | Calculates ACWR, Monotony, Strain, Polarisation, Recovery Index, FatOxidationIndex, DurabilityIndex, W′, BenchmarkIndex, SubjectiveReadinessIndex, HybridMode | [tier2_derived_metrics.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_derived_metrics.py) |
| **Tier-2 Step-7 — Evaluate Actions** | evaluate_actions | Generates adaptive coaching actions from verified metrics | [tier2_actions.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_actions.py) |
| **Tier-2 Step-8 — Render Validator** | finalize_and_validate_render | Validates report sections, placeholders, icons, and derived metrics before release | [tier2_render_validator.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_render_validator.py) |

---

## 🧩 Load Order

1. Glossary & Placeholders.md  
2. Coaching Cheat Sheet.md  
3. Coaching Heuristics Pack.md  
4. Advanced Marker Reference.md  
5. Coach profile.md  
6. Unified Reporting Framework.md  
7. Sandbakk Durability module  
8. Skiba W′ / Critical Power module  
9. Coggan Power Zones module  
10. Noakes Central Governor module  
11. Hybrid Polarised–Sweet Spot module  
12. audit_core/tier0_pre_audit.py  
13. audit_core/tier1_controller.py  
14. audit_core/tier2_data_integrity.py  
15. audit_core/tier2_event_completeness.py  
16. audit_core/tier2_enforce_event_only_totals.py  
17. audit_core/tier2_calc_integrity.py  
18. audit_core/tier2_wellness_validation.py  
19. audit_core/tier2_derived_metrics.py  
20. audit_core/tier2_actions.py  
21. audit_core/tier2_render_validator.py  

---

## ⚙️ Version and Integrity
- Ruleset Version: **v16.1-EOD-001**  
- Framework Version: **Unified Reporting Framework v5.1**  
- Audit Modules: **full v16.1 Tier-0 → Tier-2 chain**  
- Halt Condition: any missing or invalid module reference

---

## ✅ Usage
All modules and markers are dynamically fetched and executed in the strict sequence above to guarantee **Tier-2 audit compliance** and **v16.1 report validity**.

```python
from audit_core.tier0_pre_audit import run_tier0_pre_audit
from audit_core.tier1_controller import run_tier1_controller
from audit_core.tier2_data_integrity import validate_data_integrity
from audit_core.tier2_event_completeness import validate_event_completeness
from audit_core.tier2_enforce_event_only_totals import enforce_event_only_totals
from audit_core.tier2_calc_integrity import validate_calculation_integrity
from audit_core.tier2_wellness_validation import validate_wellness
from audit_core.tier2_derived_metrics import compute_derived_metrics
from audit_core.tier2_actions import evaluate_actions
from audit_core.tier2_render_validator import finalize_and_validate_render
