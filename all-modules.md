<!-- Renderer binding block -->
# 🧭 Module Source Map
manifest_origin: github
module_base: https://raw.githubusercontent.com/<org>/<repo>/main/

bindings:
  Glossary & Placeholders: https://raw.githubusercontent.com/<org>/<repo>/main/Glossary%20%26%20Placeholders.md
  Coaching Cheat Sheet: https://raw.githubusercontent.com/<org>/<repo>/main/Coaching%20Cheat%20Sheet.md
  Coaching Heuristics Pack: https://raw.githubusercontent.com/<org>/<repo>/main/Coaching%20Heuristics%20Pack.md
  Advanced Marker Reference: https://raw.githubusercontent.com/<org>/<repo>/main/Advanced%20Marker%20Reference.md
  Coach Profile: https://raw.githubusercontent.com/<org>/<repo>/main/Coach%20profile.md
  Unified Reporting Framework: https://raw.githubusercontent.com/<org>/<repo>/main/Unified%20Reporting%20Framework.md
  Unified_UI_v5.1: https://raw.githubusercontent.com/<org>/<repo>/main/Unified_UI_v5.1/

---

# 📘 All Modules Index — v16
This document defines the authoritative reference chain for all rule and knowledge modules used by the **IntervalsICU GPT Coach**.  
Each module is stored separately in the **root directory** of this repository and is dynamically fetched by the app.

---

## 🔗 Module References

| Module | Purpose | File Path |
|:--|:--|:--|
| **1. Glossary & Placeholders** | Core tokens, data placeholders, and variable mappings for audits and reports. | [Glossary & Placeholders.md](https://raw.githubusercontent.com/<org>/<repo>/main/Glossary%20%26%20Placeholders.md) |
| **2. Coaching Cheat Sheet** | Quick reference thresholds and classification tables (load, recovery, quality). | [Coaching Cheat Sheet.md](https://raw.githubusercontent.com/<org>/<repo>/main/Coaching%20Cheat%20Sheet.md) |
| **3. Coaching Heuristics Pack** | Decision logic, sport-specific heuristics, and phase rules (Seiler, Friel). | [Coaching Heuristics Pack.md](https://raw.githubusercontent.com/<org>/<repo>/main/Coaching%20Heuristics%20Pack.md) |
| **4. Advanced Marker Reference** | Derived metrics and computation definitions (ACWR, Monotony, Strain, Durability, FatOx). | [Advanced Marker Reference.md](https://raw.githubusercontent.com/<org>/<repo>/main/Advanced%20Marker%20Reference.md) |
| **5. Coach Profile** | Coach’s expertise, frameworks, and marker integration models. | [Coach profile.md](https://raw.githubusercontent.com/<org>/<repo>/main/Coach%20profile.md) |
| **6. Unified Reporting Framework** | Standardized output schema for Weekly, Seasonal, and Executive Reports. | [Unified Reporting Framework.md](https://raw.githubusercontent.com/<org>/<repo>/main/Unified%20Reporting%20Framework.md) |

---

## 🧩 Load Order
1. Glossary & Placeholders.md  
2. Coaching Cheat Sheet.md  
3. Coaching Heuristics Pack.md  
4. Advanced Marker Reference.md  
5. Coach profile.md  
6. Unified Reporting Framework.md

---

## ⚙️ Version and Integrity
- Ruleset Version: v16
- Framework Version: Unified Reporting Framework v5.1  
- Audit Requirement: All modules must exist and be accessible.  
- Failure Condition: Missing file → halt report generation.

---

## ✅ Usage
When called via the loadAllRules operation, each referenced module is fetched individually from the root of the repository.  
all-modules.md serves as a manifest and version validator, not as a merged file.

---
📄 *End of Index — v16*
