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
  Framework Map: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/docs/framework-map.md
  Mapping Table: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/docs/mapping-table.md
  Schema JSON: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Schema_3_9_12.json
  Version Manifest: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/version_manifest.yaml

ruleset_version: "v16.15"
manifest_source: live
framework_version: "Unified Reporting Framework v5.1"

---

# 📘 All Modules Index — v16.15 (Public)
Authoritative reference for all modules used by **IntervalsICU GPT Coach v16.15**.  
All previous sections retained; new analytical and UI modules added.

---

## 🔗 Module References

| Module | Purpose | File Path |
|:--|:--|:--|
| **1. Glossary & Placeholders** | Core tokens and variable mappings | [Glossary & Placeholders.md](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Glossary%20%26%20Placeholders.md) |
| **2. Coaching Cheat Sheet** | Threshold tables and readiness indices | [Coaching Cheat Sheet.md](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Coaching%20Cheat%20Sheet.md) |
| **3. Coaching Heuristics Pack** | Decision logic and phase rules | [Coaching Heuristics Pack.md](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Coaching%20Heuristics%20Pack.md) |
| **4. Advanced Marker Reference** | Derived metric definitions | [Advanced Marker Reference.md](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Advanced%20Marker%20Reference.md) |
| **5. Coach Profile** | Coach framework and heuristic weights | [Coach profile.md](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Coach%20profile.md) |
| **6. Unified Reporting Framework** | 10-section output layout schema | [Unified Reporting Framework.md](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Unified%20Reporting%20Framework.md) |

---

## 🧠 Coaching & Profile Modules

| Module | Purpose | File Path |
|:--|:--|:--|
| **Athlete Profile** | Athlete identity and training history | [athlete_profile.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/athlete_profile.py) |
| **Coaching Profile** | Coach heuristics and adaptive logic | [coaching_profile.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/coaching_profile.py) |
| **Coaching Heuristics** | Phase evaluation and trend derivation | [coaching_heuristics.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/coaching_heuristics.py) |
| **Coaching Cheat Sheet** | Load classification and summary tools | [coaching_cheat_sheet.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/coaching_cheat_sheet.py) |
| **Render Unified Report** | Combines audit and UI outputs | [render_unified_report.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/render_unified_report.py) |

---

## 🧩 Audit Core (Python Modules)

| Tier / Step | Module | Function | File Path |
|:--|:--|:--|:--|
| **Controller — Report Entry** | run_report | Main controller | [audit_core/report_controller.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/report_controller.py) |
| **Tier-0 — Pre-Audit** | run_tier0_pre_audit | Fetch context | [audit_core/tier0_pre_audit.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier0_pre_audit.py) |
| **Tier-1 — Audit Controller** | run_tier1_controller | Validate integrity | [audit_core/tier1_controller.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier1_controller.py) |
| **Tier-2 Event Completeness** | validate_event_completeness | Detect gaps 🛌 ⏳ | [audit_core/tier2_event_completeness.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_event_completeness.py) |
| **Tier-2 Enforce Event-Only Totals** | enforce_event_only_totals | Σ(event) totals | [audit_core/tier2_enforce_event_only_totals.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_enforce_event_only_totals.py) |
| **Tier-2 Derived Metrics** | compute_derived_metrics | Base metrics | [audit_core/tier2_derived_metrics.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_derived_metrics.py) |
| **Tier-2 Extended Metrics** | compute_extended_metrics | Durability & Hybrid | [audit_core/tier2_extended_metrics.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_extended_metrics.py) |
| **Tier-2 Actions** | evaluate_actions | Generate actions | [audit_core/tier2_actions.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_actions.py) |
| **Tier-2 Render Validator** | finalize_and_validate_render | Validate layout | [audit_core/tier2_render_validator.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_render_validator.py) |
| **Tier-2 Schema Guard** | validate_report_schema | Schema check | [audit_core/report_schema_guard.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/report_schema_guard.py) |
| **Utility — System Integrity Guard** | verify_environment | Checksum validation | [audit_core/system_integrity_guard.py](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/system_integrity_guard.py) |
| **UI Icon Pack** | ICON_CARDS |  Unified UI v5.1 icons | [UIcomponents/icon_pack.py](UIcomponents/icon_pack.py) |

---

## 🔒 Private Extensions (Local / Private Sync)

| Module | Function | Path | Purpose |
|:--|:--|:--|:--|
| **Dataset Integrity Utils** | validate_dataset_integrity | [audit_core/utils.py](audit_core/utils.py) | Verify Σ(moving_time) / Σ(TSS) |
| **Wellness Alignment** | validate_wellness_alignment | [audit_core/utils.py](audit_core/utils.py) | Align wellness with activities |
| **Renderer (Local)** | render_full_report | [render_unified_report.py](render_unified_report.py) | Extended context diagnostics |
| **Layout Schema** | — | [UIcomponents/layout.yaml](UIcomponents/layout.yaml) | Panel and section layout |
| **Renderer Config** | — | [UIcomponents/renderer.json](UIcomponents/renderer.json) | Render behavior schema |

---

# 🧩 Load Order — v16.15-Stable  
_Canonical execution chain — Unified Reporting Framework v5.1 §2.1.3_

## 1. Knowledge & Heuristics Layer (Auto-Loaded)

| Source | Consumed by | Purpose |
|:--|:--|:--|
| `Glossary & Placeholders.md` | `coaching_profile.py` | Token and variable definitions |
| `Coaching Cheat Sheet.md` | `coaching_cheat_sheet.py` | Threshold and load tables |
| `Coaching Heuristics Pack.md` | `coaching_heuristics.py` | Phase logic rules |
| `Advanced Marker Reference.md` | `coaching_profile.py` | Derived metric definitions |
| `Coach Profile.md` | `coaching_profile.py` | Coach metadata |
| `Unified Reporting Framework.md` | `render_unified_report.py` | Section layout schema |

These files initialize constants  
`ATHLETE_PROFILE`, `COACH_PROFILE`, `HEURISTICS`, `CHEAT_SHEET` before Tier-0.

---

## 2. Audit Core Execution Chain

| Step | Module | Function Entry | Purpose / Output |
|:--:|:--|:--|:--|
| **12** | `tier0_pre_audit.py` | `run_tier0_pre_audit(context)` | Fetch activities/wellness; init totals Σ(time)/Σ(load) |
| **13** | `tier1_controller.py` | `run_tier1_controller(context)` | Validate dataset integrity |
| **14** | `tier2_event_completeness.py` | `validate_event_completeness(context)` | Detect 🛌 rest / ⏳ current days |
| **15** | `tier2_enforce_event_only_totals.py` | `enforce_event_only_totals(context)` | Canonical event totals |
| **16** | `tier2_derived_metrics.py` | `compute_derived_metrics(context)` | Compute ACWR, Monotony, Strain |
| **17** | `tier2_load_metrics.py` | `compute_load_metrics(context)` | Load summary (CTL, ATL, IF) |
| **18** | `tier2_adaptation_metrics.py` | `compute_adaptation_metrics(context)` | Adaptation and readiness indices |
| **19** | `tier2_trend_analysis.py` | `build_trend_analysis(context)` | Trend and regression windows |
| **20** | `tier2_correlations.py` | `compute_correlations(context)` | Load ↔ wellness correlation |
| **21** | `tier2_extended_metrics.py` | `compute_extended_metrics(context)` | DurabilityIndex and HybridMode |
| **22** | `tier2_actions.py` | `evaluate_actions(context)` | Generate adaptive actions |
| **23** | `tier2_render_validator.py` | `finalize_and_validate_render(context)` | Assemble and validate report |
| **24** | `report_schema_guard.py` | `validate_report_schema(report_json)` | Final schema check |

Halt conditions : variance ≤ 0.1 h and ≤ 2 TSS; schema pass required.

---

## ⚙️ Version and Integrity
- Ruleset Version    : v16.15  
- Framework Version   : Unified Reporting Framework v5.1  
- Manifest Source    : live  
- Audit Modules      : Tier-0 → Tier-2 chain verified  
- Halt Condition     : any missing module reference  

---

## ✅ Usage

```python
from audit_core.tier0_pre_audit import run_tier0_pre_audit
from audit_core.tier1_controller import run_tier1_controller
from audit_core.tier2_event_completeness import validate_event_completeness
from audit_core.tier2_enforce_event_only_totals import enforce_event_only_totals
from audit_core.utils import validate_dataset_integrity as validate_calculation_integrity
from audit_core.utils import validate_wellness_alignment as validate_wellness
from audit_core.tier2_derived_metrics import compute_derived_metrics
from audit_core.tier2_extended_metrics import compute_extended_metrics
from audit_core.tier2_actions import evaluate_actions
from audit_core.tier2_render_validator import finalize_and_validate_render
from audit_core.tier2_load_metrics import compute_load_metrics
from audit_core.tier2_adaptation_metrics import compute_adaptation_metrics
from audit_core.tier2_trend_analysis import build_trend_analysis
from audit_core.tier2_correlations import compute_correlations
from audit_core.report_schema_guard import validate_report_schema
from audit_core.system_integrity_guard import verify_environment
from athlete_profile import ATHLETE_PROFILE
from coaching_profile import COACH_PROFILE, get_profile_metrics
from coaching_heuristics import HEURISTICS, derive_trends, derive_correlations
from coaching_cheat_sheet import CHEAT_SHEET, summarize_load_block
from render_unified_report import render_full_report
from UIcomponents.icon_pack import ICON_CARDS
