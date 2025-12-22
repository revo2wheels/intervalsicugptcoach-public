# Usage Guide — v17.2

### Unified Reporting Framework (URF v5.1)

**Architecture:** Cloudflare Worker–gated backend with deterministic audit execution

---

## ⚙️ Architecture Overview

The Unified Reporting Framework (URF) operates across **local** and **cloud** environments using a **deterministic audit pipeline**.
All modes produce identical canonical JSON outputs governed by the same Tier-0 → Tier-2 execution model.

**Core components:**

* **`app.py`** — primary FastAPI entry point (Railway backend)
* **`audit_core/report_controller.py`** — orchestrates Tier-0 through Tier-2 audit chain
* **`semantic_json_builder.py`** — compiles the canonical semantic graph
* **`Cloudflare Worker`** — handles OAuth, request validation, and environment routing
* **`report.py`** — local developer entry point for full offline report generation

---

## ☁️ Cloud Mode (ChatGPT → Worker → Backend)

**Logical entry point:**
`run_report(intent="weekly" | "season" | "wellness" | "summary")`

**Physical flow:**

1. ChatGPT issues a report intent.
2. Request is routed through the **Cloudflare Worker**, which handles:

   * OAuth token exchange
   * Validation and dataset prefetch
   * Routing to correct backend (Production or Staging)
3. The **Railway backend** (`app.py`) receives and dispatches the request.
4. `run_report()` in `audit_core/report_controller.py` executes the **full audit chain**:

   * Tier-0: dataset normalization
   * Tier-1: completeness and canonical totals
   * Tier-2: derived metrics, wellness alignment, and actions
5. The **Semantic JSON Builder** (`semantic_json_builder.py`) assembles the authoritative output.
6. Markdown (optional) is rendered only from the semantic JSON — never directly from metrics.
7. The canonical semantic JSON payload is returned to ChatGPT or API caller.

**Characteristics**

* ChatGPT never performs metric computation.
* Worker only routes and validates.
* Railway handles all canonical logic and storage.
* Deterministic and reproducible — identical results to local runs.
* Production and staging use identical audit logic; staging uses isolated dataset branches.

---

## 🧩 Local Python Mode

**Entry point:**
`python report.py [--range weekly|season|wellness|summary] [--format semantic] [--prefetch] [--staging]`

**Flow:**

1. `report.py` invokes `run_report()` from `audit_core/report_controller.py`.
2. Executes the **complete Tier-0 → Tier-2** chain locally.
3. Optionally uses `--prefetch` to pull Worker-cached datasets for reproducible tests.
4. **Semantic JSON Builder** produces the canonical semantic dataset.
5. Optional Markdown is derived from JSON.
6. Results are written to `/output/` and `/logs/`.

**Key advantages:**

* Zero cloud dependency.
* Identical audit and semantic logic as backend.
* Useful for validation, module debugging, or offline analysis.

---

## 🚦 Environment Routing (Worker Logic)

| Layer            | Parameter(s)                          | Routing Decision             |
| ---------------- | ------------------------------------- | ---------------------------- |
| **Worker**       | default                               | → Railway Production         |
|                  | `staging=1 + authorized owner`        | → Railway Staging *(locked)* |
| **CLI**          | `--staging` *(maintainer only)*       | → Railway Staging            |
| **ChatGPT**      | Internal override *(maintainer only)* | → Staging                    |
| **Unauthorized** | `?staging=1` (no owner)               | → Sanitized → Production     |

Worker logs clearly indicate route context:

```
[ROUTE → PRODUCTION] /run_weekly
[ROUTE → STAGING-OWNER] /run_weekly?staging=1   (restricted)
[ROUTE → BLOCKED-STAGING] /run_weekly?staging=1  (unauthorized)
```

**Staging routing** uses a hidden owner validation field.
Unauthorized users cannot access staging, even if `staging=1` is appended.

---

## 🧭 Data Flow Summary

| Stage         | Layer                              | File / Module                             | Function |
| ------------- | ---------------------------------- | ----------------------------------------- | -------- |
| **T0**        | `audit_core/data_normalizer.py`    | Normalizes datasets                       |          |
| **T1**        | `audit_core/metrics_controller.py` | Computes canonical totals                 |          |
| **T2**        | `audit_core/adaptation_engine.py`  | Derives secondary metrics and actions     |          |
| **Finalizer** | `semantic_json_builder.py`         | Builds authoritative semantic JSON        |          |
| **Renderer**  | `app.py` → Markdown handler        | Converts semantic JSON → Markdown summary |          |

---

## 📦 Data Sources

| Type                  | Provider                  | Layer           |
| --------------------- | ------------------------- | --------------- |
| Activities & Wellness | Intervals.icu API         | Worker Prefetch |
| Ruleset / Manifest    | GitHub (`all-modules.md`) | Railway Tier-1  |
| OAuth                 | Cloudflare Worker         | Cloud mode only |
| Local Cache           | `/data/cache/`            | Developer mode  |

---

## 🧾 File Outputs (Local Mode)

| File             | Description                    | Location   |
| ---------------- | ------------------------------ | ---------- |
| `report.json`    | Canonical semantic output      | `/output/` |
| `report.md`      | Markdown summary (derived)     | `/output/` |
| `compliance.log` | Tier-integrity and audit trace | `/logs/`   |

> In Cloud mode, only JSON (and optionally Markdown) is returned via API — no file persistence occurs.

---

## 🧰 Environment Quick Reference

| Mode                         | Route                    | Environment   | Notes             |
| ---------------------------- | ------------------------ | ------------- | ----------------- |
| Local Python                 | `report.py`              | Local         | Offline execution |
| ChatGPT                      | Worker → Railway Prod    | Production    | Default           |
| ChatGPT (maintainer only)    | Worker → Railway Staging | 🔒 Restricted |                   |
| CLI / Bash                   | Worker → Railway Prod    | Production    | Manual            |
| CLI / Bash (maintainer only) | Worker → Railway Staging | 🔒 Restricted |                   |

---

## 🔒 Staging Environment Policy

* Access restricted to maintainers only.
* Requests must originate from authenticated or owner-validated routes.
* Unauthorized `?staging=1` params are stripped automatically.
* Staging logs retained for QA validation only.
* Both environments share identical audit logic — only dataset and renderer branches differ.

---

## 🧭 Debug and Verification

Worker and backend logs explicitly indicate environment context:

```
[ROUTE → PRODUCTION] …Target=Railway Production
[ROUTE → STAGING-OWNER] …Target=Railway Staging (restricted)
```

ChatGPT and Markdown outputs display corresponding framework context:

```
Framework: Unified Reporting Framework v5.1 (production)
```

or

```
Framework: Unified Reporting Framework v5.1 (staging – restricted)
```

---

## 🧱 Summary

This v17.2 usage model ensures:

* Deterministic output across all environments
* Single canonical truth source (`semantic_json_builder.py`)
* Secure staging access limited to maintainers
* Seamless parity between Local Python and Cloud modes

**Staging remains private, production remains public, and all execution is verifiable via audit logs and semantic output integrity.**

---

Would you like me to append a **“Developer Deployment & Testing” section** explaining how to trigger each route (local, staging, production) with CLI examples and ChatGPT intents (for internal README inclusion)?
