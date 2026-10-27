# Montis.icu Documentation

This directory contains technical, coaching and historical documentation for the Montis.icu coaching engine.

## Current architecture

Montis.icu does not expose raw Intervals.icu data directly to a language model and ask the model to invent a coaching interpretation. Athlete evidence is validated and resolved by the Montis engine first; AI is a downstream interface for explanation and dialogue.

**Current flow**

`Intervals.icu → Cloudflare Edge Services → Railway Engine → governed coaching intelligence → AI / app / API`

The Railway backend starts from `app.py` and dispatches into `audit_core/report_controller.py`. Local engineering execution uses `report.py`; to run it on your own Intervals.icu data, use `report.py --direct` (see [RUN_LOCALLY.md](RUN_LOCALLY.md)).

The controller currently executes:

1. Tier-0 — acquisition, normalization and canonical data windows.
2. Tier-1 — dataset integrity and audit preparation.
3. Tier-2 — totals enforcement, derived and extended metrics, and deterministic actions.
4. Tier-3 — Performance Intelligence, ESPE, future forecast and the Adaptive Decision Engine.
5. Semantic output — `semantic_json_builder.py` assembles the governed result consumed by downstream interfaces.

Current intelligence versions in source:

- Performance Intelligence: `PI_v1.62`
- ESPE: `espe_v1.23`
- Adaptive Decision Engine: `ade_v2.21`

## Current documentation

| Document | Purpose |
|---|---|
| [README](../README.md) | Project overview and current architecture |
| [Usage Guide](USAGE_GUIDE.md) | Railway, local CLI and interface execution model |
| [Audit Chain Overview](audit_chain_overview.md) | Current Tier-0 → Tier-3 execution flow |
| [Compliance Log Guide](COMPLIANCE_LOG_GUIDE.md) | Audit/compliance ownership and traceability |
| [Unified Reporting Framework](../Unified%20Reporting%20Framework.md) | URF v5.1 reporting contract |

## AI integration resources

ChatGPT (the Montis plugin), Claude and other MCP clients use the same Montis MCP service. Their shared knowledge resources and skills are published at:

https://github.com/revo2wheels/montis-mcp-resources

Only the configuration of the legacy Montis GPT (until 11 December 2026) is kept privately. None of these resources are part of the deterministic coaching engine execution path.

The hosted MCP implementation itself is part of the private Montis Cloudflare Edge infrastructure.

## Coaching intelligence model

The product-level Montis Intelligence Stack is distinct from the internal Tier-0/Tier-1/Tier-2/Tier-3 implementation labels.

1. **Training Load** — load pattern, recent stress and capacity context.
2. **Physiology Response** — recovery, autonomic and wellness response.
3. **Performance Intelligence** — acute performance behaviour, durability and repeatability evidence.
4. **Adaptation Progression (ESPE)** — longitudinal power-curve and energy-system progression.
5. **Adaptive Decision Engine (ADE)** — capacity, phase, recovery and event governance resolved into the coaching directive.

The language model is not a sixth intelligence tier. It receives governed output and turns it into useful conversation.

## Historical documentation

Some documents remain for historical or reference purposes and may describe earlier versions of the coaching architecture.

Historical material should not override the current architecture described in the root README, this documentation index, or the current engine source.

## Public product documentation

- Product: https://www.montis.icu/
- Science: https://www.montis.icu/science.html
- Technical Design: https://www.montis.icu/pipeline.html
- Public source repository: https://github.com/revo2wheels/intervalsicugptcoach-public
