# IntervalsICU GPT Coach v16.1 — Usage Guide

## Overview
This guide describes how to use the IntervalsICU GPT Coach framework for analyzing athlete data, generating metrics, and reviewing reports.

It applies to both:
- **Private repo** (`intervalsicugptcoach`) → full audit and rendering functionality  
- **Public repo** (`intervalsicugptcoach-public`) → documentation-only view  

---

## Repository Contents
| File / Module | Purpose |
|---------------|---------|
| README.md | Framework overview, v16.1 summary |
| all-modules.md | Master module map, bindings, Tier-0 → Tier-2 load order |
| Coach profile.md | Markers, frameworks, skill mapping |
| Glossary & Placeholders.md | Input/output tokens for reports |
| Coaching Cheat Sheet.md | Thresholds for load, recovery, quality |
| Coaching Heuristics Pack.md | Decision logic and phase rules |
| Advanced Marker Reference.md | Derived metric definitions |
| Unified Reporting Framework.md | Report structure, placeholders, icons |

---

## Running / Viewing the System

### Private Repo
- Full Python audit modules available
- Steps:
  1. Fetch all modules via `loadAllRules`
  2. Run Tier-0 → Tier-2 audit chain:
     - `tier0_pre_audit()`
     - `tier1_controller()`
     - Tier-2 Steps 1 → 8 sequentially
  3. Validate `auditFinal=True` for report rendering
  4. Render Weekly, Seasonal, and Executive Reports
- Outputs include:
  - Derived metrics: ACWR, Monotony, Strain, Polarisation, Recovery Index, FatOxidationIndex, W′, BenchmarkIndex, SubjectiveReadinessIndex, HybridMode
  - Rest Day 🛌 and Current Day ⏳ icons

### Public Repo
- Python audit modules are **not included**
- Users can:
  - Inspect documentation
  - Review module bindings, markers, thresholds
  - Examine placeholder definitions
  - Understand workflow and data flow diagrams
- Note: **Reports cannot be executed in public repo**

---

## Key Concepts
- Event-only totals (moving_time, distance, TSS)
- Derived metrics computed per event, validated through audit chain
- Placeholders populate all report sections
- Decision rules from Heuristics Pack classify training load, recovery, and quality

---

## References
- Seiler, S. — 80/20 Polarisation Principle  
- Banister, E. — TRIMP Load Model  
- Foster, C. — Monotony & Strain Concepts  
- Mujika & Padilla — Evidence-Based Tapering Protocols  
- Sandbakk, Ø. — Durability & Fatigue Resistance Frameworks  

---

## Notes
- Public and private usage guide are identical; only Python execution differs
- Diagrams, flowcharts, and Mermaid visualizations are included in `/docs/`
