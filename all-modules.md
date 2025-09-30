<!-- Renderer binding block -->
# 🧭 Module Source Map PUBLIC
manifest_origin: github
manifest_source: live
manifest_mode: dual
manifest_usage: chatgpt+local
framework_version: "Unified Reporting Framework v5.1"
ruleset_version: "v16.16G"
manifest_note: "Dual-path manifest with explicit ChatGPT and Local modes; full GitHub URLs, relative local bindings, and corrected documentation."

---
# Unified Module Load Order

**Purpose:** Define strict initialization order and canonical dependencies for the Intervals.icu GPT Coach.  
**Applies to:** both local runtime and ChatGPT plugin configuration.  

---

## 📦 Load Sequence (Logical Pipeline)

| **Priority** | **Stage** | **Description** | **Layer** |
|:--|:--|:--|:--|
| 1 | Schema (`Schema_3_9_18.json`) | Intervals.icu OpenAPI schema (activities, wellness, profile) | API Core |
| 2 | Tier-0 (`tier0_pre_audit`) | Fetch profile, activities (light+full), wellness; build snapshots | Tier-0 |
| 3 | Tier-1 (`tier1_controller`) | Dataset validation, visible totals, event log block | Tier-1 |
| 4 | Tier-2 (all `tier2_*` modules) | Data integrity, completeness, enforced totals, metrics, actions | Tier-2 |
| 5 | Renderer (`render_unified_report`) | Build URF v5.1 markdown + Report object | Render |
| 6 | URF Spec (`Unified Reporting Framework.md`) | Canonical 10-section layout and metric semantics | Spec |
| 7 | Coaching Modules | Profile, heuristics, cheat sheet, narrative | Coaching |
| 8 | Glossary & Placeholders | Token / flag definitions for all tiers | Reference |

---

## 🧩 Runtime Execution Chain

Schema → Tier-0 → Tier-1 → Tier-2 → URF Renderer → Coaching Modules → Output

---

## 🗃 Deprecated / Archived Modules

| **Deprecated File** | **Replaced By** |
|:--|:--|
| `Coaching Heuristics Pack.md` | `audit_core/coaching_heuristics.py` |

---

## 🔒 Enforcement Rules

- `report_controller.py` loads and executes modules **in order**.  
- Each layer must confirm success before advancing.  
- Any failure in Tier-2, URF, or Coaching halts execution with `AuditHalt`.  
- `Glossary & Placeholders.md` always loaded last.  
- Schema and Tier-0 are immutable once loaded.  

---


## 📄 Documentation References
README: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/README.md  
Instructions v16.13: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/instructionsv16.13.md  
License: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/LICENSE  
Docs/audit_chain_overview: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/docs/audit_chain_overview.md  
Docs/COMPLIANCE_LOG_GUIDE: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/docs/COMPLIANCE_LOG_GUIDE.md  
Docs/TIER_MODULE_DETAILS: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/docs/TIER_MODULE_DETAILS.md  
Docs/USAGE_GUIDE: https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/docs/USAGE_GUIDE.md  

---

# 📘 All Modules Index — v16.16G (Dual Mode)
Authoritative reference for all modules used by **IntervalsICU GPT Coach** for ChatGPT and local execution.

---

## 🧩 Audit Core Modules
| Tier / Step | Module | Function | File Path |
|:--|:--|:--|:--|
| Controller — Report Entry | run_report | Unified controller for all report types | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/report_controller.py |
| Tier-0 — Pre-Audit | run_tier0_pre_audit | Fetch athlete context, activities, wellness | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier0_pre_audit.py |
| Tier-1 — Audit Controller | run_tier1_controller | Validate dataset integrity | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier1_controller.py |
| Tier-2 — Data Integrity | validate_data_integrity | Verify dataset count, duplication | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_data_integrity.py |
| Tier-2 — Event Completeness | validate_event_completeness | Ensure no missing or duplicate events | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_event_completeness.py |
| Tier-2 — Enforce Event-Only Totals | enforce_event_only_totals | Aggregate totals from event-level data | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_enforce_event_only_totals.py |
| Tier-2 — Calculation Integrity | validate_calculation_integrity | Ensure variance ≤ 0.1h / 2TSS | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_calculation_integrity.py |
| Tier-2 — Derived Metrics | compute_derived_metrics | Recompute ACWR, Strain, Polarisation | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_derived_metrics.py |
| Tier-2 — Extended Metrics | compute_extended_metrics | Compute durability, hybrid modes | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_extended_metrics.py |
| Tier-2 — Actions | evaluate_actions | Generate adaptive coaching actions | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_actions.py |
| Tier-2 — Renderer Validator | finalize_and_validate_render | Validate render before output | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/tier2_render_validator.py |
| Schema Guard | validate_report_schema | Ensure Unified Framework compliance | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/report_schema_guard.py |

---

## 🧠 Coaching & Profile Modules
| Module | Purpose | File Path |
|:--|:--|:--|
| Athlete Profile | Athlete identity & training history | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/athlete_profile.py |
| Coaching Profile | Coach heuristics & adaptive logic | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/coaching_profile.py |
| Coaching Heuristics | Phase evaluation & trend derivation | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/coaching_heuristics.py |
| Coaching Cheat Sheet | Load classification tools | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/coaching_cheat_sheet.py |

## Coaching Markdown Reference Modules
| Module | Purpose | File Path |
|:--|:--|:--|
| Unified Reporting Framework | Canonical metric definitions and 10-section layout | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Unified%20Reporting%20Framework.md |
| Coaching Profile | Coach heuristics & adaptive logic | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/coaching%20profile.md |
| Glossary & Placeholders | Audit state/context tokens (Tier-0 ↔ Tier-1 bridge) | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Glossary%20&%20Placeholders.md |
| Coaching Cheat Sheet | Narrative templates, tone, and persona  | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Coaching%20Cheat%20Sheet.md |

---

## 🎨 Renderer & UI Modules
| Component | Purpose | File Path |
|:--|:--|:--|
| Unified Renderer | Combines audit and UI output | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/render_unified_report.py |
| Icon Pack | UI icons and metrics logic | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/UIcomponents/icon_pack.py |
| Layout Schema | Section & card layout map | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/UIcomponents/layout.yaml |
| Color Schema | Defines UI color variables | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/UIcomponents/color_schema.json |
| Renderer Config | Renderer layout specification | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/UIcomponents/renderer.json |
| Typography | Font and text styles | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/UIcomponents/typography.json |

---

## 🌐 System Interfaces & Plugins
| Interface | Purpose | File Path |
|:--|:--|:--|
| GitHub API Plugin | Loads ruleset manifests | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/api_github_com__jit_plugin/__init__.py |
| Intervals.icu API Plugin | Fetches athlete data and wellness | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/intervals_icu__jit_plugin/__init__.py |
| OAuth Token Fetcher | Secure API authentication | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/oauth_token_fetcher.py |

---

## 🧭 Unified Report Entry
| Component | Function | File Path |
|:--|:--|:--|
| Report Dispatcher (ChatGPT) | run_report | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/audit_core/report_controller.py |
| Local Report Entry (Primary) | report.py → run_report() | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/report.py |
| Audit Runner (Developer Utility) | run_audit.py | https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/run_audit.py |

---

## ✅ Validation Summary
- Framework: Unified Reporting Framework v5.1  
- Version: v16.16G — Dual-path ChatGPT + Local ready  
- Status: Fully validated with documentation and schema bindings  

---

## 🧩 Usage (Dual Mode)

### ChatGPT Instruction Mode
Used for live audit rendering and report orchestration.

# ChatGPT environment automatically reads all-modules.md
# No manual imports required.

### Local Python Execution Mode

# --- Core Audit Flow ---
from audit_core.tier0_pre_audit import run_tier0_pre_audit
from audit_core.tier1_controller import run_tier1_controller
from audit_core.tier2_data_integrity import validate_data_integrity
from audit_core.tier2_event_completeness import validate_event_completeness
from audit_core.tier2_enforce_event_only_totals import enforce_event_only_totals
from audit_core.tier2_calculation_integrity import validate_calculation_integrity
from audit_core.tier2_derived_metrics import compute_derived_metrics
from audit_core.tier2_extended_metrics import compute_extended_metrics
from audit_core.tier2_actions import evaluate_actions
from audit_core.tier2_render_validator import finalize_and_validate_render

# --- Renderer ---
from render_unified_report import render_full_report

# --- Unified Report Entry ---
from report import run_report

# --- System Interfaces ---
from intervals_icu__jit_plugin import listActivities, listWellness, getAthleteProfile
from api_github_com__jit_plugin import loadAllRules
from oauth_token_fetcher import fetch_token
