# Coaching Framework Map v17

## Overview
This document outlines the coaching framework, which leverages performance metrics and audit outputs to guide decision-making in athlete training. The framework consists of several key modules and actions, including adaptive training load adjustments, periodisation, and fatigue resistance, all driven by audit outputs from the **Audit Chain**.

The audit outputs—derived from **Tier-2 actions** such as **ACWR**, **Strain**, **Monotony**, **TRIMP**—influence coaching decisions related to **load management**, **periodisation**, and **athlete readiness**. These decisions are influenced by both **Cloud execution** via a backend API (ChatGPT → Worker → backend), with data fetching and module loading performed server-side and **Local Python Execution** (where data is fetched locally or from cached sources).

---

## 🧭 Seiler 80/20 Polarisation Model

### Framework Description
The **Seiler 80/20 Polarisation Model** proposes that approximately **80%** of endurance training should be performed at **low intensity (Zone 1)** and **20%** at **high intensity (Zone 3)**, with minimal training in the **moderate intensity (Zone 2)** range. Seiler's 80/20 counts **sessions, not minutes** (Seiler 2010).  
The engine collapses the 7 zones into Seiler's 3: **Seiler Z1 = Z1+Z2** (below LT1), **Seiler Z2 = Z3+Z4** (LT1–LT2), **Seiler Z3 = Z5–Z7** (above LT2 ≈ FTP), the same grouping as Intervals.icu's Polarization Index, renormalised so Z1+Z2+Z3 = 1.  
This structure maximises aerobic development, improves metabolic efficiency, and reduces threshold fatigue.

---

### 🔢 Key Metrics

**Audit Metrics:**
- **Monotony** *(Tier-2)* — Measures the variation in daily training load (mean ÷ SD).  
  - High monotony (>2.5) → risk of repetitive stress or inadequate variation.
- **Strain** *(Tier-2)* — Represents total stress load (`Σ(Load) × Monotony`).  
  - Indicates whether total load is within sustainable limits.
- **ACWR** *(Tier-2)* — Ensures week-over-week progression is safe (`EWMA₇d / EWMA₂₈d`).

**Derived Intensity Metrics:**
- **Polarisation (Seiler 3-zone distribution)** — value = `% of time in Seiler Z1` (Seiler 2010; Stöggl & Sperlich 2015).  
  `semantic_state` = distribution type from zone order (Intervals.icu rules, checked in order): **hiit** (Z3 > Z2 and Z3 > 0.499 × (Z1+Z2)); **polarised** (Z3 > Z2 and Z1 > Z2); **base** (Z1 > 3.99 × Z2 and Z1 > 3 × (Z2+Z3)); **pyramidal** (1.4 × Z2 < Z1 < 3.01 × Z2 and Z2 > 1.4 × Z3); **threshold** (Z1 < 4 × Z2 and Z2 > 0.5 × Z3); otherwise **unique**.  
  Informational (no good/bad bands). Power-based; Ride HR zones only when no power.
- **PolarisationIndex (Treff et al. 2019)** — `log10((Z1 / Z2) × Z3 × 100)` on the 3-zone fractions.  
  If Z2 = 0: `log10(Z1 / 0.01 × (Z3 − 0.01) × 100)`; if Z3 = 0: PI = 0; if Z3 > Z1: not valid (null).  
  PI > 2.00 = polarised, ≤ 2.00 = not polarised (informational). Power-based; Ride HR zones only when no power.  
  **Polarisation_fused** applies the same index to `zones.fused` (dominant sport; power where available, HR otherwise) and **Polarisation_combined** to `zones.combined` (all endurance sports; lower-confidence summary), with the same > 2.00 cut-off.
- **QualitySessionBalance** — Measures the relationship between high-quality (interval) sessions and recovery sessions.

---

### 🧩 Derived Markers / Relationships

| Metric | Purpose | Target Range |
|:--|:--|:--|
| **Polarisation** | Seiler Z1 time share + distribution type (hiit / polarised / base / pyramidal / threshold / unique) | Informational (no bands) |
| **PolarisationIndex** | Treff PI on Seiler 3-zone fractions | > 2.00 = polarised, ≤ 2.00 = not polarised (informational) |
| **Monotony** | Load variation (day-to-day balance) | ≤ 2.0 |
| **Strain** | Cumulative training stress | ≤ 3500 |
| **ACWR** | Acute:Chronic Load Ratio | 0.8–1.3 productive |
| **QualitySessionBalance** | Session quality-to-recovery ratio | Balanced = 1.0 ± 0.1 |

---

### ⚙️ Integration of Audit Outputs

- **ACWR** governs progression rate — maintaining safe 7d:28d ratios (<1.3).  
- **Strain** combined with **Monotony** ensures variability in load while keeping total stress below overload thresholds.  
- **Polarisation** and **Polarisation Index** are read together:  
  - The **distribution type** (e.g. threshold or pyramidal) shows where moderate (Seiler Z2) work dominates.  
  - **PI > 2.00** confirms a polarised distribution; ≤ 2.00 means not polarised. Neither is scored good/bad.  
- **Action Logic** from `tier2_actions.py` treats both as informational context for intensity-distribution advice, not as pass/fail thresholds.

---

### 📊 Report Placement

| Metric | Report Section | Description |
|:--|:--|:--|
| **ACWR** | Load Management | Acute-to-chronic workload monitoring |
| **Monotony** | Load Variability | Daily training variation index |
| **Strain** | Training Load | Composite of total volume × monotony |
| **Polarisation** | Training Intensity Distribution | % time in Seiler Z1 + distribution type |
| **PolarisationIndex** | Training Intensity Distribution | Treff PI (> 2.00 = polarised) |
| **QualitySessionBalance** | Session Quality | Ratio of intense vs recovery sessions |

---

### 🧠 Coaching Implication
> “If the distribution is **threshold** or **PI ≤ 2.00** and a polarised structure is the goal, shift moderate (Seiler Z2) time into Z1 and separate low/high-intensity days clearly.  
> Judge 80/20 by **sessions, not minutes** (Seiler 2010); the metrics are informational, not good/bad scores.”

---

## Banister TRIMP Model
### Framework Description:
**TRIMP (Training Impulse)** is used to calculate **training load** by taking into account both **intensity** and **duration**. Banister’s model helps manage the training load over time to avoid **overtraining**.

### Key Metrics:
- **Audit Metrics**:
  - **ACWR** (Tier-2): Used to assess the risk of overtraining by comparing the training load over time.
  - **Strain** (Tier-2): Monitors fatigue levels and informs whether the **TRIMP** calculation should adjust the intensity/duration of the training.

### Derived Markers / Metrics:
- **TRIMP (Training Load)**: Directly derived from **Strain** and **duration**, representing total training load over a specific period.
- **Recovery Stress Index**: Calculated from the balance of high-intensity work and rest periods.

### Integration of Audit Outputs:
- **TRIMP** is directly influenced by **Strain** and **ACWR** from the audit output. **Strain** influences when the athlete is nearing their capacity for **intensity** and needs recovery, while **ACWR** prevents excessive increases in load.
- **`tier1_controller.py`** helps assess overall **load balance** and adjusts recovery periods based on **ACWR** thresholds.

### Report Placement:
- **ACWR** and **Strain** appear in the **Load Management** and **Recovery Phase** sections of the **Unified Report**.
- **TRIMP** is referenced in the **Training Load Analysis** section.
- **Recovery Stress Index** is used in the **Recovery Status** section.

---

## Foster Monotony and Strain Model
### Framework Description:
**Monotony** is a metric that quantifies the **variation in training intensity**. **Strain** evaluates the **accumulated load** over time. The **Foster Model** helps avoid excessive training monotony and balances intensity levels to prevent overtraining.

### Key Metrics:
- **Audit Metrics**:
  - **Monotony** (Tier-2): Measures the consistency of intensity in the athlete's training. High monotony suggests that the athlete may be exposed to too much repetitive stress.
  - **Strain** (Tier-2): Tracks the overall stress on the athlete based on the accumulated workload over time.

### Derived Markers / Metrics:
- **Training Intensity Variability**: A marker used to measure how much the intensity changes over a given period. High variability is linked to effective load management.
- **Fatigue Index**: A derived marker indicating when an athlete is approaching fatigue based on **Strain** and **Monotony**.

### Integration of Audit Outputs:
- **Strain** and **Monotony** directly inform the **Foster Model**. If **Monotony** is high or **Strain** is too high, the coach should adjust the training intensity, either by adding recovery phases or reducing the intensity of sessions.
- **Coaching heuristics** in **`coaching_heuristics.py`** provide thresholds for when training load should be adjusted based on **Monotony**.

### Report Placement:
- **Monotony** and **Strain** are placed in the **Load Management** section of the final report.  
- **Monotony** is also referenced in the **Training Consistency** section.
- **Training Intensity Variability** and **Fatigue Index** are placed in the **Fatigue Monitoring** section.

---

## San Millán Metabolic Flexibility Model
### Framework Description:
This model focuses on **metabolic flexibility** and the ability of endurance athletes to adapt their fuel utilization (aerobic vs. anaerobic). It emphasizes training the body's ability to switch between energy systems.

### Key Metrics:
- **Audit Metrics**:
  - **FatOxidationIndex** (Tier-2): Assesses the ability of an athlete to utilize fat for energy, indicating metabolic flexibility.
  - **Strain** (Tier-2): Helps track overall metabolic stress, which can indicate the need for **lower-intensity aerobic training** to improve fat oxidation.

### Derived Markers / Metrics:
- **Aerobic Threshold**: A marker derived from the **FatOxidationIndex** and **Strain**, representing the point at which the body switches from predominantly fat-burning to glycogen-burning.
- **Metabolic Flexibility Index**: A derived marker used to assess how efficiently the athlete can switch between aerobic and anaerobic energy systems.

### Integration of Audit Outputs:
- **FatOxidationIndex** is directly impacted by training intensity, which is monitored by **Strain**. This metric helps decide whether an athlete’s intensity should be adjusted to further develop **fat oxidation**.

### Report Placement:
- **FatOxidationIndex** appears in the **Metabolic Efficiency** section of the **Unified Report**.  
- **Strain** is featured in the **Fatigue Resistance** section.
- **Aerobic Threshold** and **Metabolic Flexibility Index** are placed in the **Metabolic Adaptation** section.

---

## Friel Periodisation Model
### Framework Description:
**Periodisation** is the systematic planning of training to maximize performance and prevent overtraining. This framework divides the training cycle into distinct phases (e.g., base, build, peak).

### Key Metrics:
- **Audit Metrics**:
  - **ACWR** (Tier-2): Ensures training load follows an appropriate progression, preventing overtraining during periods of high intensity.
  - **Monotony** (Tier-2): Guides when to vary training intensity to avoid plateauing during the **base phase**.

### Derived Markers / Metrics:
- **Peak Load**: A marker indicating the maximum training load before tapering, based on **ACWR** and **Monotony**.
- **Recovery Readiness**: A derived marker showing how ready the athlete is for recovery based on **Strain** and **Monotony**.

### Integration of Audit Outputs:
- **ACWR** and **Monotony** help structure the **periodisation** model by informing when load adjustments should occur to maximize training benefits and minimize the risk of overtraining.

### Report Placement:
- **ACWR** and **Monotony** appear in the **Training Load** and **Periodisation Phases** sections of the final report.
- **Peak Load** and **Recovery Readiness** are referenced in the **Training Phases** and **Recovery** sections.

---

## Skiba Critical Power Model
### Framework Description:
The **Critical Power (CP) Model** involves the measurement of **Wprime** (work done above CP) to assess **endurance** and **anaerobic capacity**.

### Key Metrics:
- **Audit Metrics**:
  - **WprimeSpent** and **WprimeRecovery** (Tier-2): Used to determine the athlete's capacity for high-intensity efforts.
  - **Strain** (Tier-2): Tracks fatigue and guides when to incorporate **lower-intensity** training to recover from high-intensity efforts.

### Derived Markers / Metrics:
- **Critical Power**: A derived marker that assesses an athlete’s **maximum sustainable intensity**.
- **Wprime Depletion Rate**: Tracks how quickly an athlete depletes **Wprime** during high-intensity efforts.

### Integration of Audit Outputs:
- **Wprime** metrics are calculated using **interval power** data, which is integrated into **Strain** and **Monotony** metrics to monitor overall fatigue levels.

### Report Placement:
- **WprimeSpent** and **WprimeRecovery** appear in the **High-Intensity Training** section of the **Unified Report**.  
- **Strain** and **Monotony** are integrated into the **Fatigue Monitoring** and **Load Management** sections.

---

## Key Differences Between Cloud and Local Coaching Frameworks

| Feature | Cloud Execution | Local Execution |
|:--|:--|:--|
| Orchestration | ChatGPT → Worker → backend | Direct Python execution |
| Data Fetching | Backend API (Intervals.icu, GitHub JIT) | Local or cached |
| Audit Execution | Backend Tier-0 → Tier-2 | Local Tier-0 → Tier-2 |
| Canonical Output | Semantic JSON | Semantic JSON |
| Rendering | Optional, derived from JSON | Optional, derived from JSON |
| Coaching Actions | Derived from semantic metrics | Identical logic |


## Conclusion
The **coaching framework** operates similarly in both Cloud and Local modes, using **audit-derived metrics** (ACWR, Strain, Monotony, FatOxidationIndex) to adjust **training load**, **fatigue resistance**, and **readiness**. The main difference lies in orchestration and runtime environment; audit logic and coaching semantics are identical. Both modes ensure coaches can make data-driven, adaptive decisions to optimize athlete training and performance.

---
