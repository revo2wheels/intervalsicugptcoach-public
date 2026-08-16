# Compliance & Traceability Guide

## Overview

Montis.icu treats audit integrity and traceability as backend responsibilities. Validation, metric computation and coaching-decision state are produced by the deterministic engine; conversational AI is not the source of those results.

This guide describes ownership and traceability at a system level. Exact emitted fields can evolve with the implementation and should be verified against the current backend code when debugging a specific contract.

## Execution ownership

### Cloud execution

Typical flow:

`Client → Cloudflare Edge Services → Railway app.py → audit_core/report_controller.py`

Responsibilities are separated:

- **Cloudflare Edge Services** — authentication/OAuth, request validation, routing, integration/prefetch work and MCP resources as appropriate to the route.
- **Railway backend** — canonical audit execution, derived metrics, Performance Intelligence, ESPE, forecast, ADE and semantic assembly.
- **AI/client interface** — explanation, presentation and interaction with governed output.

The language model does not generate canonical audit state or replace backend validation.

## Current engine trace

The current controller executes these major stages:

1. Tier-0 — acquisition, normalization and canonical evidence windows.
2. Tier-1 — dataset integrity and audit preparation.
3. Tier-2 — totals enforcement, derived/extended metrics and deterministic actions.
4. Tier-3 Performance Intelligence.
5. Tier-3 ESPE when required evidence is available.
6. Tier-3 future forecast.
7. Tier-3 Adaptive Decision Engine.
8. Semantic assembly.

Current intelligence versions in source are:

- `PI_v1.62`
- `espe_v1.21`
- `ade_v2.21`

## Compliance principles

A compliant execution should preserve the following principles:

- source evidence remains distinguishable from derived state;
- validation occurs before downstream interpretation;
- missing evidence is not silently replaced with invented physiology;
- event/totals checks remain explicit;
- degraded or skipped analysis is represented as such where applicable;
- coaching-decision state is produced by backend logic before conversational rendering;
- presentation does not become a second source of truth.

## Semantic output

`semantic_json_builder.py` assembles the downstream machine-readable result after the analysis/intelligence chain has run.

Semantic output is intended to provide the governed contract consumed by reports and conversational interfaces. A client may summarize or explain that contract, but should not silently recompute or redefine the underlying athlete state.

## Local engineering execution

Local engineering entry points (`report.py` and `report_api.py`) should use the same canonical controller and preserve the same audit/intelligence semantics as Railway execution.

Local execution may provide additional developer-visible logging or artifacts, but those diagnostics do not change the coaching authority of the core engine.

## Legacy architecture note

Older documentation described compliance as a Tier-0 → Tier-2-only chain and referenced the pre-Railway `all-modules.md` / GitHub JIT model. That is no longer the full current architecture.

The current execution path continues into Tier-3 Performance Intelligence, ESPE, forecast and ADE before semantic output.

## Debugging guidance

When validating a production or engineering run, trace the request in this order:

1. confirm edge request/auth/routing context;
2. confirm `app.py` received the expected prefetched/input contract;
3. confirm `report_controller.py` established Tier-0/Tier-1 data windows;
4. confirm Tier-2 totals and derived/extended metrics;
5. confirm PI/ESPE/forecast/ADE execution or explicit skip/degradation;
6. confirm semantic assembly contains the expected governed state;
7. only then inspect client/LLM presentation.

This order prevents presentation-layer behaviour from being mistaken for a backend computation problem.

## Related documentation

- [Documentation Index](README.md)
- [Usage Guide](USAGE_GUIDE.md)
- [Audit Chain Overview](audit_chain_overview.md)
- [Runtime Resource List](../runtime-list.md)
