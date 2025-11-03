# Compliance Log Guide — v16.1

## Purpose
Explain interpretation of halt logs and validation errors.

## Log Types
- **Data Source Halt** → Mock/cache/sandbox detected
- **Tier-1 Halt** → Dataset mismatch, duplicate, missing discipline, >0.1 h variance
- **Tier-2 Halt** → Derived metric mismatch >1%
- **Render Halt** → Missing report section or placeholder

## How to Resolve
1. Identify error type
2. Cross-check source data
3. Correct dataset or placeholder
4. Re-run audit chain
