# Montis.icu Usage Guide

### Unified Reporting Framework (URF v5.1)

**Architecture:** Cloudflare Edge Services + Railway deterministic coaching engine

## Architecture overview

Montis.icu separates transport, identity and interface concerns from physiological computation and coaching governance.

`Intervals.icu → Cloudflare Edge Services → Railway Engine → governed semantic output → App / ChatGPT / Claude / API`

A language model is not responsible for computing athlete state. The Montis engine validates and resolves the available evidence first; downstream AI explains and discusses that governed result.

## Railway execution

**Backend entry point:** `app.py`

`app.py` receives normalized/prefetched request data and invokes `run_report()` from `audit_core/report_controller.py`.

The controller currently executes:

1. **Tier-0** — data acquisition/normalization and canonical data windows.
2. **Tier-1** — dataset integrity and audit preparation.
3. **Tier-2** — event-only totals, derived metrics, deterministic actions and extended metrics.
4. **Tier-3 Performance Intelligence** — durability, repeatability and acute/chronic performance context.
5. **Tier-3 ESPE** — energy-system and power-curve progression where the required evidence is available.
6. **Tier-3 Future Forecast** — forward load/event context.
7. **Tier-3 ADE** — adaptive decision resolution using current capacity, recovery, phase and event governance.
8. **Semantic assembly** — `semantic_json_builder.py` produces the governed machine-readable output used by downstream interfaces.

Current source versions:

- Performance Intelligence: `PI_v1.62`
- ESPE: `espe_v1.21`
- Adaptive Decision Engine: `ade_v2.21`

## Cloudflare Edge Services

Cloudflare is the edge and integration layer. Depending on the route/interface it handles responsibilities such as authentication, OAuth, request validation, routing, prefetch/integration work and MCP resources before requests reach the Railway engine.

It is not the canonical physiological calculation engine. Coaching computation and decision resolution remain in the backend engine.

## Local engineering execution

Local engineering uses the same core controller rather than a separate coaching implementation.

- `report.py` — local CLI/report execution.
- `report_api.py` — engineering-console/local API execution.
- `audit_core/report_controller.py` — shared canonical execution controller.

These entry points are distinct from Railway boot (`app.py`) but should converge on the same deterministic audit/intelligence logic.

## Data windows and evidence

The controller preserves different evidence windows for different purposes. In the current implementation, weekly analysis uses high-resolution recent activity data while longer-range analysis preserves a broader light dataset for chronic/adaptation context.

Power-curve, calendar, wellness and athlete-profile data are incorporated when available. Missing evidence is not silently replaced by invented physiological state; downstream modules can skip, degrade or lower confidence when their required evidence is absent.

## Implementation tiers vs product intelligence stack

The internal Tier-0/Tier-1/Tier-2/Tier-3 execution labels are implementation stages. They are not the same as the product-level five-layer Montis Intelligence Stack:

1. Training Load
2. Physiology Response
3. Performance Intelligence
4. Adaptation Progression (ESPE)
5. Adaptive Decision Engine (ADE)

The AI interface is downstream of this intelligence stack.

## Semantic output

`semantic_json_builder.py` assembles the governed semantic result after the core analysis/intelligence chain has run.

For reporting use, presentation is downstream of the semantic result. The language model may explain, summarize, question and discuss the result, but it is not the authority for the underlying athlete state or coaching decision.

## Runtime resources

Do not treat every Markdown file as ordinary documentation. The files listed in [`../runtime-list.md`](../runtime-list.md) are operational resources used by Cloudflare MCP or OpenAI GPT configuration and must retain their current names/paths unless the external configuration is changed at the same time.

## Legacy pre-Railway architecture

`all-modules.md` and `api_github_com__jit_plugin/` belong to the earlier GPT/JIT orchestration model. They are not referenced by the current `app.py`, `report.py`, `report_api.py` or `audit_core` execution paths and should not be described as current Railway dependencies.

The same caution applies to older documentation that describes Tier-0 → Tier-2 as the complete coaching architecture. Tier-2 remains important, but the current controller continues into Performance Intelligence, ESPE, forecast and ADE before semantic output.

## Staging and production

Production and staging should run the same core coaching code, while environment routing, credentials and datasets remain isolated as appropriate. Edge routing and environment controls are operational concerns; they do not change the coaching authority of the Railway engine.

## Related documentation

- [Documentation Index](README.md)
- [Audit Chain Overview](audit_chain_overview.md)
- [Compliance Log Guide](COMPLIANCE_LOG_GUIDE.md)
- [Unified Reporting Framework](../Unified%20Reporting%20Framework.md)
- [Runtime Resource List](../runtime-list.md)

Public product documentation:

- https://www.montis.icu/
- https://www.montis.icu/science.html
- https://www.montis.icu/pipeline.html
