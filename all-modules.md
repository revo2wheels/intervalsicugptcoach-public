## Governance Manifest v3.9.12
```json
{
  "$schema": "https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/Schema_3_9_12.json",
  "version": "3.9.12",
  "description": "Custom Governance Manifest for Unified Reporting Framework v5.1",
  "governance": {
    "auditRequired": true,
    "renderMode": "full",
    "tierEnforce": true,
    "intentRouter": "v1.1",
    "xValidationRef": "./Schema_3_9_12.json#/x-validation-rules"
  },
  "enforcement": {
    "auditFinal": true,
    "auditPartial": true,
    "force_analysis": true,
    "preRenderAudit": true,
    "tier2_enforce_event_only_totals": true,
    "render_mode": "full",
    "autoCommit": true,
    "suppressPrompts": true
  },
  "audit": {
    "tier0": { "enabled": true, "ruleset": "pre_audit_integrity" },
    "tier1": { "enabled": true, "ruleset": "dataset_consistency" },
    "tier2": { "enabled": true, "ruleset": "derived_metrics_validation" }
  },
  "derived": {
    "enableFatOx": true,
    "enableCarbOx": true,
    "enableVO2Estimation": true,
    "enableEnergyMix": true,
    "enableLactateModel": true
  },
  "reporting": {
    "defaultIntent": "weekly",
    "supportedIntents": ["weekly", "season", "wellness"],
    "autoCommit": true
  },
  "output": {
    "render_mode": "full",
    "icons": true,
    "include_metabolic_panel": true,
    "include_energy_mix_chart": true,
    "validateDerivedMetabolic": true
  },
  "permissions": {
    "roles": ["administrator", "auditor"],
    "accessLevels": { "weekly": "read", "season": "read", "audit": "write" }
  },
  "x-actions": {
    "run_audit_pipeline": {
      "type": "python",
      "entrypoint": "run_audit_pipeline",
      "args": {
        "conn": "intervals_icu__jit_plugin",
        "src": "intervals"
      }
    }
  },
  "x-intents": [
    {
      "trigger": ["weekly report", "season report", "wellness report"],
      "action": "run_audit_pipeline"
    }
  ],
  "manifest_signature": {
    "schemaVersion": "3.9.12",
    "rulesetVersion": "v16.16G",
    "validatedBy": "Unified Reporting Framework v5.1",
    "checksum": "auto"
  },
  "timestamps": {
    "created": "2025-11-07T00:00:00Z",
    "updated": "2025-11-07T00:00:00Z"
  }
}
