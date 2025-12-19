# Usage Guide — v17

This guide describes **how the framework executes in Cloud and Local modes** following the v16.16G architecture (Worker-gated backend with deterministic audit execution).

---

## Cloud Mode (ChatGPT → Worker → Backend)

**Logical entry point:** `run_report(intent="weekly")`  
**Physical execution:** Backend API (FastAPI) via Cloudflare Worker

**Flow:**
1. ChatGPT issues a report intent (`weekly`, `season`, etc.).
2. Request is routed through a **Cloudflare Worker**:
   - OAuth token exchange  
   - Request validation  
   - Routing to backend
3. Backend service (`app.py` entry point) receives the request.
4. `run_report()` in `audit_core/report_controller.py` is executed.
5. Full **Tier-0 → Tier-2 audit chain** runs on the backend.
6. **Semantic JSON Builder** assembles the canonical audit output:
   - validated metrics
   - derived values
   - audit flags
   - adaptive actions
7. Structured JSON payload is returned to ChatGPT.
8. Markdown rendering (if requested) is generated **from the semantic JSON**, not from raw metrics.

**Key characteristics:**
- No audit, aggregation, or rendering logic runs in ChatGPT or the Worker.
- JSON is the **canonical output**.
- Markdown is a **presentation layer**, not a source of truth.
- Requires an **always-on backend container** (no sleeping tiers).
- Deterministic execution identical to local mode.

---

## Local Python Mode

**Entry point:**  
python report.py

**Flow:**
1. `report.py` calls `run_report()` from `audit_core/report_controller.py`.
2. Executes the complete **Tier-0 → Tier-2 audit chain locally**.
3. **Semantic JSON Builder** produces the canonical audited dataset.
4. Optional Markdown report is rendered **from the JSON payload**.
5. Outputs are written to disk.

**Characteristics:**
- No cloud dependencies.
- JSON-first execution model.
- Identical audit logic, tolerances, and semantic structure as Cloud mode.
- Developer utility `run_audit.py` may call individual tiers for diagnostics (non-canonical).

---

## Data Sources

- **Activities & Wellness:** `intervals_icu__jit_plugin`
- **Ruleset / Manifest:** `api_github_com__jit_plugin` (consumes `all-modules.md`)
- **OAuth:** handled upstream (Worker in Cloud mode, local helper in Local mode)

---

## File Outputs (Local Mode)

| Type | Description | Location |
|:--|:--|:--|
| `report.json` | Canonical semantic audit output (source of truth) | `/output/` |
| `report.md` | Rendered Markdown (derived from JSON) | `/output/` |
| `compliance.log` | Tier integrity and validation trace | `/logs/` |

> In Cloud mode, the semantic JSON payload is returned directly via the API response.  
> Markdown is generated only when explicitly requested.

---

## References

For canonical execution and data lineage details, see:
- `docs/audit_chain_overview.md`
- `docs/mapping-table.md`
