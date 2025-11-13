# 📖 Glossary & Placeholders (Core Runtime Reference)
**Version:** v16.18  
**Layer:** Tier-0 → Tier-1 context only  
**Owner:** `audit_core`

---

### ⚙️ System Context Tokens
| Token | Description |
|:--|:--|
| `{auditPartial}` | Boolean flag — Tier-1 complete |
| `{auditFinal}` | Boolean flag — Tier-2 complete |
| `{auditStatus}` | Text state summary (“in progress”, “passed”, “halted”) |
| `{integrityFlag}` | Tier-1 integrity check outcome |
| `{integrityNote}` | Audit variance note (≤0.1 h or ≤2 TSS allowed) |

---

### 🗂 Dataset Metadata
| Token | Description |
|:--|:--|
| `{eventCount}` | Count of valid events fetched in analysis window |
| `{dateRangeStart}` / `{dateRangeEnd}` | Temporal window bounds |
| `{dataSource}` | Source label (Intervals.icu / sandbox / cache) |
| `{schemaVersion}` | Active schema (e.g. 3.9.12) |
| `{rulesetVersion}` | Active rule version (e.g. v16.18) |

---

### 🧭 Athlete Context
| Token | Description |
|:--|:--|
| `{athleteName}` | Athlete display name |
| `{athleteId}` | Numeric athlete ID |
| `{timezone}` | Athlete timezone (default Zurich) |

---

⚠️ **Note**  
No totals, averages, or metrics appear here.  
All quantitative fields (hours, TSS, distance, IF, HR, VO₂ max, etc.) are owned by the **Unified Reporting Framework v5.2** and exposed through its `{URF:metrics}` namespace during render.
