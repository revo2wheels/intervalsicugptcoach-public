# Audit Framework Map — v17

## Overview

This document provides a **conceptual architecture overview** of the Intervals.icu GPT Coaching Framework.
It illustrates how audit, metric derivation, and coaching logic interact across execution environments.

This document is **descriptive**, not executable.
It does not define runtime order, deployment topology, or API wiring.

---

## Execution Environments

The framework supports two execution environments with **identical audit and coaching semantics**:

- **Cloud Execution**: ChatGPT → Cloudflare Worker → Backend API
- **Local Execution**: Direct Python runtime

In both cases, the **Tier-0 → Tier-2 audit chain** and **semantic output** are identical.

---

## Cloud Execution Architecture (Authoritative)

In Cloud execution, **all computation occurs in the backend runtime**.

### Responsibilities by Layer

**ChatGPT**
- Issues report intent (weekly, season, etc.)
- Consumes semantic JSON output
- May request Markdown rendering
- Does not execute audits or calculations

**Cloudflare Worker**
- OAuth token exchange
- Request validation
- Routing to backend
- No audit or computation logic

**Backend Runtime (FastAPI / Python)**
- Fetches data (Intervals.icu, GitHub JIT)
- Executes Tier-0 → Tier-2 audit chain
- Builds semantic JSON output
- Optionally renders Markdown from JSON

---

## Canonical Audit & Coaching Flow

```mermaid
graph TB
    A[ChatGPT Intent] --> B[Cloudflare Worker]
    B --> C[Backend API entry: app.py]
    C --> D[run_report()]
    D --> E[Tier-0 Pre-Audit]
    E --> F[Tier-1 Controller]
    F --> G[Tier-2 Validation & Metrics]
    G --> H[Semantic JSON Builder]
    H --> I[Adaptive Coaching Actions]
    I --> J[Optional Markdown Rendering]
```

Local execution mirrors Cloud execution without orchestration layers.
```mermaid
graph TB
    A[report.py] --> B[run_report()]
    B --> C[Tier-0 Pre-Audit]
    C --> D[Tier-1 Controller]
    D --> E[Tier-2 Validation & Metrics]
    E --> F[Semantic JSON Builder]
    F --> G[Adaptive Coaching Actions]
    G --> H[Optional Markdown Rendering]
```