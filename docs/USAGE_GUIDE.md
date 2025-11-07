# Usage Guide — v16.16G

## Cloud (ChatGPT) Mode
Entry point: `run_report(intent="weekly")`
- Fetches live athlete data via Intervals.icu plugin
- Executes Tier-0 → Tier-2 audit chain
- Calls `render_unified_report.py` to produce 10-section Markdown report
- No local setup required

## Local Python Mode
Entry point: `python report.py`
- Executes `run_report()` from `audit_core/report_controller.py`
- Runs the complete Tier-0 → Tier-2 audit chain locally
- Produces `/output/report.json` (raw metrics) and `/output/report.md` (rendered report)
- Mirrors ChatGPT execution, including adaptive actions and render validation
- Developer utility `run_audit.py` can still call individual tiers for debugging

## Data Sources
- Activities and wellness via `intervals_icu__jit_plugin`
- Ruleset and manifest via `api_github_com__jit_plugin`
- OAuth handled by `oauth_token_fetcher.py`

## File Outputs
| Type | Description | Location |
|:--|:--|:--|
| `report.json` | Raw audit metrics | `/output/` |
| `report.md` | Rendered Markdown report | `/output/` |
| `compliance.log` | Tier integrity + validation log | `/logs/` |

## References
For full chain details see:
- `docs/audit_chain_overview.md`
- `docs/mapping-table.md`
