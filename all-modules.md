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
  Unified_UI_v5.1: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Unified_UI_v5.1/icon_pack.json

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
| **Controller — Report Entry** | run_report | Unified report controller for all report types; executes Tier-0 → Tier-2 chain | [report_controller.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/report_controller.py) |
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

# 🧩 Load Order — v16.14-Stable  
**Canonical Module Execution Chain (TotalHours-Compliant Build)**  
_Compliant with Unified Reporting Framework v5.1 §2.1.3 and Audit Chain v16.14_

---

## 1. Knowledge & Heuristics Modules
1. `Glossary & Placeholders.md`  
2. `Coaching Cheat Sheet.md`  
3. `Coaching Heuristics Pack.md`  
4. `Advanced Marker Reference.md`  
5. `Coach Profile.md`  
6. `Unified Reporting Framework.md`  
7. `Sandbakk Durability Module`  
8. `Skiba W′ / Critical Power Module`  
9. `Coggan Power Zones Module`  
10. `Noakes Central Governor Module`  
11. `Hybrid Polarised–Sweet Spot Module`  

---

## 2. Audit Core (Python Modules)

| Step | Module Path | Function Entry | Purpose / Output |
|:--:|:--|:--|:--|
| **12** | `audit_core/tier0_pre_audit.py` | `run_tier0_pre_audit(context)` | Fetches live data via `intervals_icu__jit_plugin.listActivities()` and initializes context. **Defines `totalHours = Σ(moving_time)/3600`** and `totalTss = Σ(icu_training_load)`. |
| **13** | `audit_core/tier1_controller.py` | `run_tier1_controller(context)` | Validates dataset integrity, duplicates, and total consistency. Writes verified totals to `context["eventTotals"]`. |
| **14** | `audit_core/tier2_data_integrity.py` | `validate_data_integrity(context)` | Ensures row counts match API results, variance ≤ 0.1 h. |
| **15** | `audit_core/tier2_event_completeness.py` | `validate_event_completeness(context)` | Detects missing days, rest days (🛌), and current day (⏳). |
| **16** | `audit_core/tier2_enforce_event_only_totals.py` | `enforce_event_only_totals(context)` | Computes canonical `Σ(moving_time)` and `Σ(icu_training_load)`; updates `context["eventTotals"]["hours"]` and provenance key `enforcement_layer="tier2_enforce_event_only_totals"`. |
| **17** | `audit_core/tier2_calc_integrity.py` | `validate_calculation_integrity(context)` | Confirms Tier-1 and Tier-2 totals align (Δh ≤ 0.1 / ΔTSS ≤ 2). Halts otherwise. |
| **18** | `audit_core/tier2_wellness_validation.py` | `validate_wellness(context)` | Aligns wellness entries with activity dates; ignores nulls if load < 40. |
| **19** | `audit_core/tier2_derived_metrics.py` | `compute_derived_metrics(context)` | Computes ACWR, Monotony, Strain, Polarisation, Recovery Index. |
| **20** | `audit_core/tier2_actions.py` | `evaluate_actions(context)` | Generates adaptive actions based on derived metrics. |
| **21** | `audit_core/tier2_render_validator.py` | `finalize_and_validate_render(context, reportType)` | Final report assembly. **Rebinds `summary.hours` and `totalHours` from verified event-only totals before template render.** Validates schema and icons, returns Markdown/HTML. |

---

## 3. Compliance Notes
- **Canonical duration source:** `Σ(df["moving_time"]) / 3600` (never `elapsed_time`).  
- **Context propagation:** `totalHours` is written once (Tier-0) and verified only thereafter.  
- **Renderer enforcement:** rebinds from `eventTotals.hours` to `summary.hours` and `totalHours` pre-render.  
- **Audit Final Gate:** passes only when variance ≤ 0.1 h and ≤ 2 TSS.  

---

### ✅ Outcome
This load sequence:
- Eliminates nondeterministic duration drift.  
- Ensures `totalHours` consistent across all sessions.  
- Maintains Tier-2 provenance and Unified Framework v5.1 compliance.  
- Ready for direct commit as `load_order_v16.14.md` in `/docs/` or `/meta/`.


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
