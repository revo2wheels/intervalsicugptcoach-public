# 🧪 Developer Deployment & Testing

### Unified Reporting Framework (URF v5.1) — Developer Operations Reference

This section explains how developers and maintainers can deploy, test, and validate URF execution paths across all supported environments.

----

## ⚙️ 1. Local Python Execution

Local execution provides full deterministic parity with the Railway backend.
All Tier-0 → Tier-2 audit modules run locally, without cloud dependencies.

### Run Examples

#### Weekly Report

```
python report.py --range weekly --format semantic
```

#### Weekly Report (prefetch via Worker)

```
python report.py --range weekly --format semantic --prefetch
```

#### Wellness Summary

```
python report.py --range wellness --format semantic
```

#### Staging QA Run (restricted to maintainers)

```
python report.py --range weekly --format semantic --prefetch --staging
```

**Outputs:**

* `/output/report.json` — canonical semantic JSON
* `/output/report.md` — markdown summary
* `/logs/compliance.log` — audit integrity trace

**Notes:**

* `--prefetch` pulls cached datasets via the Worker (Tier-0 snapshot).
* `--staging` triggers the same logic as Cloudflare’s route (restricted).

---

## ☁️ 2. Cloudflare Worker → Railway (Production)

All ChatGPT and public API traffic defaults to **production**.

### Execution Path

```
ChatGPT → Cloudflare Worker → Railway Production (app.py → run_report)
```

### Manual Trigger (curl)

```
curl -X POST "https://intervalsicugptcoach.clive-a5a.workers.dev/run_weekly"
```

### Expected Worker Log

```
[ROUTE → PRODUCTION] /run_weekly | Target=Railway Production
```

### Example ChatGPT Prompt

> “Run a full weekly report.”
> “Show me wellness for this week.”

ChatGPT will always use the **production** route unless explicitly overridden for staging (maintainer only).

---

## 🧩 3. Cloudflare Worker → Railway (Staging, Restricted Access)

Staging mirrors production logic but runs against **staging branches** and isolated data stores.
Access is limited to authorized maintainers

### Execution Path

```
ChatGPT (maintainer intent) → Cloudflare Worker → Railway Staging (restricted)
```

### Manual Trigger (CLI / curl)

```
curl -X POST "https://intervalsicugptcoach.clive-a5a.workers.dev/run_weekly?staging=1&secret"
```

### Expected Worker Log

```
[ROUTE → STAGING-OWNER] /run_weekly?staging=1 | Target=Railway Staging (restricted)
```

### Expected ChatGPT Output Header

```
Framework: Unified Reporting Framework v5.1 (staging – restricted)
```

> ⚠️ **Important:** Unauthorized users attempting `?staging=1` will be automatically routed to production.
> Worker silently strips unverified staging flags to prevent leakage.

---

## 🚀 4. Backend Deployment Commands (Railway)

### Deploy to Production

```
railway up --service intervalsicugptcoach-public-production
```

### Deploy to Staging (maintainers only)

```
railway up --service intervalsicugptcoach-public-staging
```

Both services share the same container image and codebase, but staging may point to:

* different environment variables
* alternate data tokens or OAuth keys
* temporary experimental renderer branches

---

## 🧭 5. ChatGPT Intents Mapping

| Intent                                                | Action                                      | Route      | Notes                      |
| ----------------------------------------------------- | ------------------------------------------- | ---------- | -------------------------- |
| “Run a full weekly report”                            | `runWeeklyReportV2()`                       | Production | Default path               |
| “Run a full weekly report in staging”                 | `runWeeklyReportV2(staging=1, secret)`      | Staging    | Maintainer-only            |
| “Show my wellness data for this week”                 | `runWellnessReportV2()`                     | Production | 42-day window              |
| “Summarize my last 90 days”                           | `runSeasonReportV2()`                       | Production | 90-day full dataset        |
| “Show my training summary”                            | `runSummaryReportV2()`                      | Production | Profile-based summary only |

---

## 🔧 6. Debugging & Validation

### Worker Console Log

```
[ROUTE → PRODUCTION] /run_weekly | UA=ChatGPT | Ref=https://chat.openai.com/
```

### Railway Application Log

```
[APP] Received POST /run_weekly
[CONTROLLER] Executing Tier-0 → Tier-2 pipeline
[SEMANTIC] auditFinal=True | variant=weekly
[FINALIZER] Returning canonical JSON (audit passed)
```

### Local Debug Example

```
python report.py --range weekly --format semantic --prefetch
```

Expected log tail:

```
[SEMANTIC] auditFinal=True
[REPORT] Saved report.json (canonical)
[COMPLIANCE] All Tier checks passed.
```

---

## 🧱 7. Validation Rules

| Layer      | Validation Type  | Description                            |
| ---------- | ---------------- | -------------------------------------- |
| Worker     | Routing & Auth   | Ensures valid environment and OAuth    |
| Tier-0     | Data Integrity   | Normalizes and validates completeness  |
| Tier-1     | Canonical Totals | Confirms metric accuracy and alignment |
| Tier-2     | Derived Metrics  | Computes fatigue, ACWR, trends         |
| Renderer   | URF v5.1 Layout  | Generates Markdown from JSON           |
| AuditFinal | Final Sanity     | Confirms no missing canonical data     |

---

## 🧾 8. Summary of Responsibilities

| Component                       | Role                                 |
| ------------------------------- | ------------------------------------ |
| ChatGPT                         | User intent + report request         |
| Cloudflare Worker               | Auth, routing, environment control   |
| Railway (app.py)                | Full audit engine & semantic builder |
| audit_core/report_controller.py | Pipeline coordinator                 |
| semantic_json_builder.py        | Canonical dataset construction       |
| report.py                       | Local entry point for developers     |

---

## ✅ Best Practices

* Always use **local mode** for pre-commit validation of metrics.
* Use **production** for user-facing tests.
* Use **staging** only for renderer or logic branch testing (maintainers only).
* Validate that Worker logs show correct route before QA testing.

---

## 🧩 Quick Environment Recap

| Route                 | Access     | Entry Point                                 | Example           |
| --------------------- | ---------- | ------------------------------------------- | ----------------- |
| Local Python          | Public     | `python report.py`                          | local offline run |
| ChatGPT (Prod)        | Public     | `runWeeklyReportV2`                         | production        |
| ChatGPT (Staging)     | Restricted | `runWeeklyReportV2(staging=1, secret)`      | internal QA       |
| Bash / Curl (Prod)    | Public     | `curl …/run_weekly`                         | production        |
| Bash / Curl (Staging) | Restricted | `curl …/run_weekly?staging=1&secret`        | staging QA        |

---

### 🧭 End of Developer Deployment & Testing Section

**Version:** URF v5.1 — Usage Guide v17.2
**Maintainer Access:** Restricted

---
