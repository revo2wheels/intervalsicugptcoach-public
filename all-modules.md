<!-- Renderer binding block -->
# 🧭 Module Source Map PUBLIC
manifest_origin: github
manifest_source: live
manifest_mode: dual
manifest_usage: chatgpt+local
framework_version: "Unified Reporting Framework v5.1"
ruleset_version: "v16.16G"
manifest_note: "Dual-path manifest with explicit ChatGPT and Local modes; full GitHub URLs, relative local bindings, and corrected documentation."

## Governance Manifest v3.9.12
```json
{
  "$schema": "https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Schema_3_9_12.json",
  "version": "3.9.12",
  "description": "Custom Governance Manifest for Unified Reporting Framework v5.1",
  "xValidationRef": "./Schema_3_9_12.json#/x-validation-rules",
  "autoload": {
    "enabled": true,
    "on_session_start": "loadAllRules"
  },
  "governance": {
    "auditRequired": true,
    "renderMode": "full",
    "tierEnforce": true,
    "intentRouter": "v1.1",
    "xValidationRef": "./Schema_3_9_12.json#/x-validation-rules"
  },
  "enforcement": {
    "auditFinal": true,
    "auditPartial": true,
    "force_analysis": false,
    "preRenderAudit": true,
    "tier2_event_finalizer_strict": true,
    "tier2_enforce_event_only_totals": true,
    "tier2_event_finalizer_strict": true,
    "tier2_event_totals_lock": true,
    "tier2_disable_discipline_summary": true,
    "tier2_event_collapse": {
      "deduplicate_by": ["id", "start_date_local"],
      "aggregation_method": "first_instance"
        },
    "render_source": "event_totals",
    "enforce_render_source_integrity": true,
    "tier2_event_filter": {
      "field": "origin",
      "include": ["event"],
      "deduplicate": true,
      "deduplicate_keys": ["id", "start_date_local"]
    },
    "render_mode": "full",
    "autoCommit": true,
    "suppressPrompts": true
  },
  "audit": {
    "tier0": { "enabled": true, "ruleset": "pre_audit_integrity" },
    "tier1": { "enabled": true, "ruleset": "dataset_consistency" },
    "tier2": {
      "enabled": true,
      "ruleset": "derived_metrics_validation",
      "rules": [
        "filter_event_origin",
        "collapse_duplicate_events",
        "enforce_event_only_totals",
        "validate_calculation_integrity"
      ]
    }
  },
  "derived": {
    "enableFatOx": true,
    "enableCarbOx": true,
    "enableVO2Estimation": true,
    "enableEnergyMix": true,
    "enableLactateModel": true
  },
  "reporting": {
    "defaultIntent": "weekly",
    "supportedIntents": ["weekly", "season", "wellness"],
    "autoCommit": true
  },
  "output": {
    "render_mode": "full",
    "icons": true,
    "include_metabolic_panel": true,
    "include_energy_mix_chart": true,
    "validateDerivedMetabolic": true,
    "enforce_event_totals_render": true,
    "render_source": "event_totals",
    "require_explicit_flags": false,
    "extended_metrics_default": true,
    "derived_metrics_default": true
  }
  "permissions": {
    "roles": ["administrator", "auditor"],
    "accessLevels": { "weekly": "read", "season": "read", "audit": "write" }
  },
  "x-actions": {
    "run_audit_pipeline": {
      "type": "python",
      "entrypoint": "run_audit_pipeline",
      "args": {
        "conn": "intervals_icu__jit_plugin",
        "src": "intervals"
      }
    }
  },
  "x-intents": [
    {
      "trigger": ["weekly report", "season report", "wellness report"],
      "action": "run_audit_pipeline"
    }
  ],
  "manifest_signature": {
    "schemaVersion": "3.9.12",
    "rulesetVersion": "v16.16G",
    "validatedBy": "Unified Reporting Framework v5.1",
    "checksum": "auto"
  },
  "timestamps": {
    "created": "2025-11-07T00:00:00Z",
    "updated": "2025-11-07T00:00:00Z"
  }
}

---
# Unified Module Load Order — v16.18 (Corrected)

**Purpose:** Define strict initialization order and canonical dependencies for the Intervals.icu GPT Coach.  
**Applies to:** both local runtime and ChatGPT plugin configuration.  

---

## 📦 Load Sequence

| **Priority** | **Module** | **Description** | **Layer** |
|:--|:--|:--|:--|
| 1 | `Schema_3_9_12.json` | Intervals.icu OpenAPI schema (activities, wellness, profile) | API Core |
| 2 | `audit_core/tier0_pre_audit.py` | Data ingestion and lightweight 28-day snapshot (Tier-0 entry) | Tier-0 |
| 3 | `audit_core/fetch_utils.py` *(or equivalent)* | Helper for authenticated HTTP fetches with retry logic | Tier-0 |
| 4 | `audit_core/tier1_controller.py` | Dataset validation and canonical totals registration | Tier-1 |
| 5 | `audit_core/tier2_enforcement.py` | Derived metrics and event-level integrity checks | Tier-2 |
| 6 | `audit_core/render_unified_report.py` | Renderer for Unified Reporting Framework (URF v5.2) | Render |
| 7 | `Unified Reporting Framework v5.2.md` | Canonical metric definitions and 10-section layout | Spec |
| 8 | `coaching_cheat_sheet.py` | RPE, feel, and zone reference scales | Coaching |
| 9 | `coaching_heuristics.py` | Fatigue, ACWR, durability, and recovery logic | Coaching |
| 10 | `coaching_profile.py` | Narrative templates, tone, and persona | Coaching |
| 11 | `Glossary & Placeholders.md` | Audit state/context tokens (Tier-0 ↔ Tier-1 bridge) | Reference |

---

## 🧩 Runtime Execution Chain

Schema → Tier-0 → Tier-1 → Tier-2 → URF Renderer → Coaching Modules → Output

---

## 🗃 Deprecated / Archived Modules

| **Deprecated File** | **Replaced By** |
|:--|:--|
| `Coaching Cheat Sheet.md` | `audit_core/coaching_cheat_sheet.py` |
| `Coaching Heuristics Pack.md` | `audit_core/coaching_heuristics.py` |
| `Coaching Profile.md` | `audit_core/coaching_profile.py` |

> ⚠️ Each deprecated file should begin with the line:  
> `⚠️ DEPRECATED — canonical runtime source: audit_core/coaching_<module>.py`

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
