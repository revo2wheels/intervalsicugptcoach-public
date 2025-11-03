# Audit Chain Overview — v16.1

This document explains the Tier-0 → Tier-2 audit chain, halt conditions, and compliance logic.

## Tier-0 — Pre-Audit
- Fetch live activities and wellness data
- Validate data origin
- Initialize audit context
- Halt if mock/cache/sandbox detected

## Tier-1 — Audit Controller
- Validate dataset integrity
- Detect duplicates
- Verify total moving time, TSS, distance
- Halt if >0.1 h deviation or missing discipline

## Tier-2 — Event Audit
1. Data Integrity: confirm API count matches DataFrame
2. Event Completeness: check each event, build daily summary
3. Enforce Event-Only Totals: compute Σ(event-level)
4. Calculation Integrity: validate totals and derived metric consistency
5. Wellness Validation: align wellness window, truncate if needed
6. Derived Metrics: compute ACWR, Monotony, Strain, Polarisation, Recovery Index, FatOxidationIndex, W′, BenchmarkIndex, SubjectiveReadinessIndex, HybridMode
7. Evaluate Actions: generate adaptive coaching actions
8. Render Validator: validate report sections, placeholders, icons

## Compliance Logs
- All halts create an entry in the compliance log
- Prevents report release until resolved
