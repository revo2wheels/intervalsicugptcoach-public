# Montis.icu Documentation

This directory contains technical, coaching and historical documentation for the Montis.icu coaching engine.

## Current architecture

Montis.icu does not expose raw Intervals.icu data directly to a language model and ask the model to invent a coaching interpretation. Athlete evidence is validated and resolved by the Montis engine first; AI is a downstream interface for explanation and dialogue.

**Current flow**

`Intervals.icu → Cloudflare Edge Services → Railway Engine → governed coaching intelligence → AI / app / API`

The Railway backend starts from `app.py` and dispatches into `audit_core/report_controller.py`. Local engineering execution uses `report.py` or `report_api.py` where applicable.

The controller currently executes:

1. Tier-0 — acquisition, normalization and canonical data windows.
2. Tier-1 — dataset integrity and audit preparation.
3. Tier-2 — totals enforcement, derived and extended metrics, and deterministic actions.
4. Tier-3 — Performance Intelligence, ESPE, future forecast and the Adaptive Decision Engine.
5. Semantic output — `semantic_json_builder.py` assembles the governed result consumed by downstream interfaces.

Current intelligence versions in source:

- Performance Intelligence: `PI_v1.62`
- ESPE: `espe_v1.21`
- Adaptive Decision Engine: `ade_v2.21`

## Current documentation

| Document | Purpose |
|---|---|
| [README](../README.md) | Project overview and current architecture |
| [Usage Guide](USAGE_GUIDE.md) | Railway, local engineering and interface execution model |
| [Audit Chain Overview](audit_chain_overview.md) | Current Tier-0 → Tier-3 execution flow |
| [Compliance Log Guide](COMPLIANCE_LOG_GUIDE.md) | Audit/compliance ownership and traceability |
| [Unified Reporting Framework](../Unified%20Reporting%20Framework.md) | URF v5.1 reporting contract |

## Runtime resources — do not move or rename during documentation cleanup

The files listed in [`runtime-list.md`](../runtime-list.md) are operational resources, not ordinary documentation.

Current protected resources are:

**Cloudflare MCP resources**

- `tools_mcp.md`
- `workoutsv2.md`
- `question_bank_coaching.md`
- `question_bank_what_next.md`
- `montis_icu_claude_skill_mcp_resource.md`

**OpenAI GPT instructions**

- `OPENAI/instructionsv17.md`

Their paths are part of external/runtime configuration and must not be changed as part of documentation tidying.

## Coaching intelligence model

The product-level Montis Intelligence Stack is distinct from the internal Tier-0/Tier-1/Tier-2/Tier-3 implementation labels.

1. **Training Load** — load pattern, recent stress and capacity context.
2. **Physiology Response** — recovery, autonomic and wellness response.
3. **Performance Intelligence** — acute performance behaviour, durability and repeatability evidence.
4. **Adaptation Progression (ESPE)** — longitudinal power-curve and energy-system progression.
5. **Adaptive Decision Engine (ADE)** — capacity, phase, recovery and event governance resolved into the coaching directive.

The language model is not a sixth intelligence tier. It receives governed output and turns it into useful conversation.

## Legacy / review-required material

Some documents remain in the repository for historical or reference purposes but still describe the earlier GPT/JIT or Tier-0 → Tier-2-only architecture. They should not be treated as the current architecture until reviewed or archived.

Known examples include:

- `all-modules.md` — pre-Railway GPT/JIT orchestration manifest.
- `api_github_com__jit_plugin/` — compatibility shim for the old `all-modules.md` loading model.
- `coach_framework-map.md`
- `coach_mapping-table.md`
- `mapping-table.md`
- older coaching guides and framework notes that pre-date the current PI / ESPE / ADE stack.

Before moving or deleting any historical file, confirm that it is not referenced by an active runtime path or external Cloudflare/OpenAI configuration.

## Public product documentation

- Product: https://www.montis.icu/
- Science: https://www.montis.icu/science.html
- Technical Design: https://www.montis.icu/pipeline.html
- Public source repository: https://github.com/revo2wheels/intervalsicugptcoach-public
