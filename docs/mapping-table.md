# 🗂 v16.1 Data Flow Mapping — Inputs to Outputs

| Input Data / Field | Source Module | Processed In | Derived Metrics / Outputs | Render / Report Placement |
|-------------------|---------------|--------------|--------------------------|--------------------------|
| `activity.moving_time` | Intervals.icu API | Tier-2 Step-3: Enforce Event-Only Totals | TotalHours | Weekly / Seasonal Report – Section Summary |
| `activity.distance` | Intervals.icu API | Tier-2 Step-4: Calculation Integrity | TotalDistance | Weekly / Seasonal Report – Section Summary |
| `activity.icu_training_load` | Intervals.icu API | Tier-2 Step-3: Enforce Event-Only Totals | TotalTSS | Weekly / Seasonal Report – Section Summary |
| `wellness.HRV` | Intervals.icu API | Tier-2 Step-5: Wellness Validation | RecoveryIndex | Weekly Report – Recovery Section |
| `wellness.restHR` | Intervals.icu API | Tier-2 Step-5: Wellness Validation | RecoveryIndex | Weekly Report – Recovery Section |
| `wellness.sleep` | Intervals.icu API | Tier-2 Step-5: Wellness Validation | RecoveryIndex | Weekly Report – Recovery Section |
| `RPE`, `Feel` | Subjective Input | Tier-2 Step-6: Derived Metrics | FatOxidationIndex, SubjectiveReadinessIndex | Weekly / Seasonal Report – Training Quality |
| `power/HR` | Activity | Tier-2 Step-6: Derived Metrics | ACWR, Monotony, Strain, Polarisation, DurabilityIndex, FatOxidationIndex, HybridMode | Weekly / Seasonal Report – Metrics Panel |
| `FTP`, `LT1`, `LT2` | Athlete Profile / Test | Tier-2 Step-6: Derived Metrics | BenchmarkIndex, SpecificityIndex, ConsistencyIndex | Seasonal Report – Advanced Markers |
| `age` | Athlete Profile | Tier-2 Step-6: Derived Metrics | AgeFactor adjusted ATL | Seasonal Report – Periodisation / Load Planning |
| `activity.climbing` | Activity | Tier-2 Step-6: Derived Metrics | DurabilityIndex | Weekly / Seasonal Report – Training Quality |
| `discipline` | Activity | Tier-2 Step-1: Data Integrity | Validates dataset split (cycling, running, triathlon) | Weekly Report – Discipline Breakdown |
| `session.type` | Activity | Tier-2 Step-2: Event Completeness | Assigns “Rest Day 🛌”, “Current Day ⏳” icons | Weekly Report – Summary Section |
| Derived `C/R/S` components | Tier-2 Step-6 | Tier-2 Step-4 Calculation Integrity | Combined load totals | Weekly / Seasonal Report – Metrics Panel |
| All event totals | Tier-2 Step-3 | Tier-2 Step-4 Calculation Integrity | Checks variance vs derived totals | Internal Audit / Compliance Log |
| Audit flags | Tier-0 → Tier-2 | Tier-2 Step-7: Evaluate Actions | Adaptive Actions | Weekly / Seasonal Report – Actions Section |
| Placeholders (`{xxx}`) | Glossary & Placeholders | Used across all modules | Populated values for rendering | Unified Reporting Framework v5.1 sections |

```mermaid
flowchart TD
    subgraph Input
        A1[Intervals.icu Activity Data] 
        A2[Intervals.icu Wellness Data] 
        A3[Subjective Inputs: RPE, Feel]
        A4[Athlete Profile: FTP, LT1, LT2, Age]
    end

    subgraph Audit_Core
        B0[Tier-0: Pre-Audit]
        B1[Tier-1: Audit Controller]
        B2[Tier-2 Step-1: Data Integrity]
        B3[Tier-2 Step-2: Event Completeness]
        B4[Tier-2 Step-3: Enforce Event-Only Totals]
        B5[Tier-2 Step-4: Calculation Integrity]
        B6[Tier-2 Step-5: Wellness Validation]
        B7[Tier-2 Step-6: Derived Metrics]
        B8[Tier-2 Step-7: Evaluate Actions]
        B9[Tier-2 Step-8: Render Validator]
    end

    subgraph Derived_Metrics
        C1[TotalHours, TotalDistance, TotalTSS]
        C2[ACWR, Monotony, Strain, Polarisation]
        C3[DurabilityIndex, FatOxidationIndex]
        C4[BenchmarkIndex, SpecificityIndex, ConsistencyIndex]
        C5[SubjectiveReadinessIndex, HybridMode]
        C6[AgeFactor adjusted ATL]
    end

    subgraph Output_Reports
        D1[Weekly Report]
        D2[Seasonal Report]
        D3[Executive Report]
    end

    %% Inputs to Audit
    A1 --> B0
    A2 --> B0
    A3 --> B0
    A4 --> B0

    %% Audit sequence
    B0 --> B1 --> B2 --> B3 --> B4 --> B5 --> B6 --> B7 --> B8 --> B9

    %% Derived metrics
    B7 --> C1
    B7 --> C2
    B7 --> C3
    B7 --> C4
    B7 --> C5
    B7 --> C6

    %% Metrics to report
    C1 --> D1
    C1 --> D2
    C1 --> D3
    C2 --> D1
    C2 --> D2
    C2 --> D3
    C3 --> D1
    C3 --> D2
    C3 --> D3
    C4 --> D2
    C4 --> D3
    C5 --> D1
    C5 --> D2
    C5 --> D3
    C6 --> D2
    C6 --> D3
```mermaid