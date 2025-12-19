# Coaching Framework Map v17

## Overview
This document outlines the coaching framework, which leverages performance metrics and audit outputs to guide decision-making in athlete training. The framework consists of several key modules and actions, including adaptive training load adjustments, periodisation, and fatigue resistance, all driven by audit outputs from the **Audit Chain**.

The audit outputs—derived from **Tier-2 actions** such as **ACWR**, **Strain**, **Monotony**, **TRIMP**—influence coaching decisions related to **load management**, **periodisation**, and **athlete readiness**. These decisions are influenced by both **Cloud execution** via a backend API (ChatGPT → Worker → backend), with data fetching and module loading performed server-side and **Local Python Execution** (where data is fetched locally or from cached sources).

---

## Seiler 80/20 Polarization Model
### Framework Description:
The **80/20 Polarization Model** suggests that **80%** of endurance training should be at **low intensity**, while **20%** should be at **high intensity**. This distribution helps improve endurance without overloading the athlete.

### Key Metrics:
- **Audit Metrics**:
  - **Monotony** (Tier-2): Used to assess the consistency of the training load. A high monotony indicates that training intensity may be too repetitive, leading to potential overtraining.
  - **Strain** (Tier-2): Helps ensure that the **low-intensity** training makes up 80% of the athlete's load, while the **high-intensity** (20%) is appropriately managed.

### Derived Markers / Metrics:
- **PolarisationIndex**: Calculated from the balance between **low-intensity** and **high-intensity** training sessions. Indicates whether the athlete is adhering to the **80/20** rule of training.
- **QualitySessionBalance**: A measure of how well the athlete is balancing high-quality training (e.g., intervals) with recovery sessions.

### Integration of Audit Outputs:
- **ACWR** helps maintain a **safe progression** of training load. High **Strain** combined with **Monotony** can suggest overtraining, leading to a reduction in high-intensity sessions.
- **Action Logic** from **`t2_actions.py`** evaluates changes to **training load** based on **Monotony** and **Strain**.

### Report Placement:
- **Monotony** and **Strain** will appear in the **Unified Report** as part of the **Training Load** and **Fatigue Resistance** sections.  
- **ACWR** is featured in the **Load Management** section.
- **PolarisationIndex** is placed in the **Training Intensity Distribution** section.
- **QualitySessionBalance** appears in the **Session Quality** section.

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
