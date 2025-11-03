# Framework → Marker → Report Section Map — v16.1

This document provides a detailed mapping of each coaching framework used in the Intervals.icu GPT Coach v16.1, including markers, computation source, report placement, and placeholders.

---

## 1. Seiler 80/20 Polarisation

**Purpose:** Maintain correct intensity distribution (low vs high intensity) across the training week.

**Derived Markers / Metrics:**
- `PolarisationIndex`
- `QualitySessionBalance`

**Computation Source:** Event-level power/HR data; derived weekly distribution.

**Report Placement:**
- Weekly Report → Training Quality → Intensity Balance
- Seasonal Report → Phase Summary

**Placeholders:** `{polarisationIndex}`, `{qualitySessionBalance}`

---

## 2. Banister TRIMP

**Purpose:** Quantify training load and monitor load trends.

**Derived Markers / Metrics:**
- `ACWR`
- `TRIMP`

**Computation Source:** Event-level HR & duration data; 7-day & 28-day rolling sums.

**Report Placement:**
- Weekly Report → Load Management
- Seasonal Report → Load Trend

**Placeholders:** `{acwr}`, `{trimpLoad}`

---

## 3. Foster Monotony / Strain

**Purpose:** Detect load variability and risk of overtraining.

**Derived Markers / Metrics:**
- `Monotony`
- `Strain`

**Computation Source:** Derived from 7-day rolling mean and SD of TSS/event load.

**Report Placement:**
- Weekly Report → Load Stability Panel
- Weekly Report → Recovery Analysis

**Placeholders:** `{monotony}`, `{strain}`

---

## 4. Iñigo San Millán Zone 2 Fat-Oxidation

**Purpose:** Assess aerobic durability, mitochondrial efficiency, and fat oxidation.

**Derived Markers / Metrics:**
- `FatOxidationIndex`
- `avgDecoupling`

**Computation Source:** Event-level Z2 power/HR rides; decoupling and IF analysis.

**Report Placement:**
- Weekly Report → Training Quality → Advanced Efficiency
- Seasonal Report → Phase Summary

**Placeholders:** `{fatOxidationIndexRaw}`, `{fatOxidationIndexEval}`, `{avgDecoupling}`

---

## 5. Joe Friel Benchmarking / Periodisation

**Purpose:** Monitor aerobic progression, phase specificity, and consistency.

**Derived Markers / Metrics:**
- `BenchmarkIndex`
- `SpecificityIndex`
- `ConsistencyIndex`
- `AgeFactor`
- `MicrocycleRecoveryWeek`
- `PhaseType`

**Computation Source:** Derived from event-level load, periodic tests, and phase plan data.

**Report Placement:**
- Weekly Report → Key Stats
- Seasonal Report → Phase Summary
- Seasonal Report → Advanced Markers → Adaptation Trend

**Placeholders:** `{benchmarkIndex}`, `{specificityIndex}`, `{consistencyIndex}`, `{ageFactor}`, `{microcycleRecoveryWeek}`, `{phaseType}`

---

## 6. Sandbakk Durability Framework

**Purpose:** Evaluate fatigue resistance in long-duration events.

**Derived Markers / Metrics:**
- `DurabilityIndex`
- `DurabilityTrend`

**Computation Source:** Event-level long ride power analysis; percent power drop computation.

**Report Placement:**
- Weekly Report → Training Quality → Durability Section
- Seasonal Report → Phase Summary

**Placeholders:** `{durabilityIndex}`, `{durabilityTrend}`

---

## 7. Skiba W′ / Critical Power

**Purpose:** Track anaerobic reserve and recovery during high-intensity efforts.

**Derived Markers / Metrics:**
- `WprimeSpent`
- `WprimeRecoveryRatio`
- `W'bal`

**Computation Source:** Event-level interval power vs CP; cumulative W′ expenditure and recovery.

**Report Placement:**
- Weekly Report → Interval Analysis → Anaerobic Reserve
- Weekly Report → Load Management

**Placeholders:** `{wPrimeSpent}`, `{wPrimeRecoveryRatio}`, `{wPrimeBalance}`

---

## 8. Coggan Power Zones

**Purpose:** Ensure power zone compliance and support polarisation analysis.

**Derived Markers / Metrics:**
- `PowerZoneCompliance`
- Time-in-Zone distribution

**Computation Source:** Event-level power data; compare planned vs actual Z1–Z7 duration.

**Report Placement:**
- Weekly Report → Training Quality → Intensity Compliance
- Seasonal Report → Phase Summary → Intensity Distribution

**Placeholders:** `{powerZoneCompliance}`, `{timeInZone}`

---

## 9. Noakes Central Governor

**Purpose:** Integrate subjective readiness with load management.

**Derived Markers / Metrics:**
- `SubjectiveReadinessIndex` / `ReadinessIndex`

**Computation Source:** Subjective inputs: mood, sleep, stress, soreness.

**Report Placement:**
- Weekly Report → Recovery / Readiness Section
- Tier-2 Heuristic Overrides → Load Adjustment

**Placeholders:** `{readinessIndex}`, `{subjectiveReadinessIndex}`

---

## 10. Hybrid Polarised–Sweet Spot

**Purpose:** Adaptive intensity distribution for low-volume athletes.

**Derived Markers / Metrics:**
- `HybridMode` flag
- Adjusted Z1/Z2/Z3 ratio

**Computation Source:** Derived from total weekly volume and intensity distribution.

**Report Placement:**
- Weekly Report → Training Quality → Hybrid Mode Section
- Seasonal Report → Phase Summary

**Placeholders:** `{hybridMode}`, `{z1Adjusted}`, `{z2Adjusted}`, `{z3Adjusted}`

---

### Notes

- **Event-Level Source:** All markers are computed from raw activity data (power, HR, distance, moving time).  
- **Derived Metrics:** ACWR, Monotony, Strain, FatOxidationIndex, W′bal, DurabilityIndex, PolarisationIndex.  
- **Subjective Inputs:** Noakes Central Governor, RPE, Mood, Sleep, Fatigue.  
- **Integration:** All placeholders map directly to `all-modules.md` v16.1 rules for Tier-2 audit validation.
