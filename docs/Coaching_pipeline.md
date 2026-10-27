Below is a **clean consolidation document** for **PI + ESPEv1 → ESPEv2 → ADE**, aligned with the pipeline architecture on your site and consistent with the URF system you already run. The goal is to turn the scattered design notes into **one coherent technical specification** you can publish or keep as the internal canonical reference.

---

# Montis Coaching Intelligence Stack

## Performance Intelligence → Energy System Progression → Adaptive Decision Engine

### System Version Context

* **URF v5** → Tactical reporting engine
* **URF v6** → Adaptive performance engine

The current system has reached **Tier-3 capability modelling** through Performance Intelligence (PI) and **ESPE v1**.
The next step is the **Adaptive Decision Engine (ADE)**, which converts analysis into deterministic coaching adjustments.

---

# 1. Unified Coaching Intelligence Architecture

## Full Pipeline

```
User → GPT Interface
        ↓
Cloudflare Worker (Data Layer)
        ↓
Railway Tier-0  Normalization
        ↓
Railway Tier-1  Canonical Metrics
        ↓
Railway Tier-2  Derived Metrics
        ↓
Railway Tier-3  Performance Intelligence + ESPE
        ↓
Adaptive Decision Engine (ADE)
        ↓
Semantic Graph (URF v6)
        ↓
Deterministic GPT Rendering
```

### Design principles

1. **Deterministic compute**
2. **Externalized analytics (Railway)**
3. **Stateless renderer**
4. **Controller-owned calculations**
5. **Semantic graph contract**
6. **No GPT metric computation**

GPT only renders structured intelligence.

---

# 2. Tier-3 Performance Intelligence (PI)

Performance Intelligence evaluates **how fitness behaves under stress**, not simply how much load is applied.

PI complements Tier-1 and Tier-2 metrics by modelling **structural capabilities**.

Three models form the foundation.

---

# 2.1 WDRM — Anaerobic Repeatability

### W′ Depletion & Recovery Model

**Purpose**

Measures how aggressively and repeatedly the athlete depletes anaerobic work capacity.

This evaluates **repeatable supra-threshold resilience**, not peak sprint power.

### Core Signals

```
icu_max_wbal_depletion
icu_pm_w_prime
icu_joules_above_ftp
```

### Interpretation

| Signal             | Meaning                        |
| ------------------ | ------------------------------ |
| High depletion     | deep anaerobic effort          |
| repeated depletion | repeatability                  |
| joules above FTP   | supra-threshold stress density |

### Weekly Scope

7-day **FULL dataset**

Captures acute anaerobic stress behaviour.

### Season Scope

90-day **LIGHT aggregation**

Captures chronic anaerobic exposure.

---

# 2.2 ISDM — Durability

### Intensity Sustainability & Drift Model

Measures how well the athlete maintains output under fatigue.

This captures **aerobic durability**.

### Core Signals

```
decoupling
moving_time
long_session_count
```

### Interpretation

| Metric              | Meaning                   |
| ------------------- | ------------------------- |
| mean_decoupling     | cardiovascular drift      |
| high_drift_sessions | fatigue exposure          |
| long_sessions       | structural endurance load |

### Weekly Scope

Acute durability state.

### Season Scope

Chronic durability trend.

---

# 2.3 NDLI — Neural Density

### Neural Load Density Index

Models **clustering of high-intensity stress**.

This detects **central fatigue accumulation**.

### Core Signals

```
icu_joules_above_ftp
IF
high_intensity_session_frequency
```

### Interpretation

| Signal         | Meaning                  |
| -------------- | ------------------------ |
| rolling joules | neural load accumulation |
| intensity days | clustering risk          |
| mean IF        | central fatigue pressure |

### Weekly Scope

Acute neural stress pattern.

### Season Scope

Chronic intensity distribution.

---

# 3. Energy System Progression Engine (ESPE)

## Purpose

ESPE tracks **physiological adaptation across energy systems**.

While PI analyses stress behaviour, ESPE evaluates **performance progression**.

ESPE is **stateless**, **deterministic**, and **power-curve driven**.

---

# 3.1 ESPE v1 (Current Implementation)

### Core Principle

Adaptation is determined through **rolling power-curve comparison**.

```
adaptation = current_curve − previous_curve
```

### Window Strategy

| Report | Window              |
| ------ | ------------------- |
| Weekly | 84d vs previous 84d |
| Season | s1 vs s0            |

Rationale:

* 84 days ≈ macro block
* stable enough for adaptation detection
* responsive enough for trend changes

---

# 3.2 Power Curve Contract

Injected into context as:

```
power_curve
 └─ Ride
     ├─ current
     ├─ previous
     └─ window_days
```

Anchor durations:

```
5s
30s
1m
5m
20m
60m
```

These represent major energy system domains.

---

# 3.3 Energy System Domains

| Duration | System               |
| -------- | -------------------- |
| 5s       | neuromuscular        |
| 30s      | anaerobic            |
| 1m       | anaerobic capacity   |
| 5m       | VO2max               |
| 20m      | threshold            |
| 60m      | endurance durability |

---

# 3.4 ESPE Output

```
energy_system_progression
 └─ sports
     └─ Ride
         ├─ delta_percent
         ├─ system_status
         ├─ derived_metrics
         ├─ plateau_detected
         ├─ adaptation_bias
         └─ adaptation_state
```

### Example

```
threshold +2.1%
vo2 +1.3%
anaerobic −4.7%
```

### Derived metrics

```
curve_regression
curve_quality
power_model
curve_profile
```

---

# 3.5 Why Only Two Curves Are Used

ESPE intentionally ignores:

| curve    | reason                    |
| -------- | ------------------------- |
| lifetime | historical peaks          |
| season   | mixed adaptation periods  |
| event    | race outliers             |
| best     | contaminated by freshness |

Only **two rolling windows** provide meaningful adaptation velocity.

---

# 4. ESPE v2 (Planned Expansion)

ESPE v2 adds **curve structural analysis**.

### Additional signals

```
curve_regression_slope
curve_R2
curve_volatility
fatigue_curve_shift
durability_index
```

### Additional outputs

```
adaptation_velocity
curve_stability
performance_expression
```

### Example insight

```
VO2 rising
threshold stable
durability rising
```

Interpretation:

**aerobic adaptation**

---

# 5. Adaptive Decision Engine (ADE)

ADE converts analysis into **training prescription logic**.

This transforms the system from **analysis engine → coaching engine**.

---

# 5.1 ADE Inputs

ADE receives signals from:

```
Tier-1 load metrics
Tier-2 physiology metrics
Tier-3 performance intelligence
ESPE progression
```

### Key inputs

```
ACWR
FatigueTrend
HRV
NDLI
WDRM
ISDM
ESPE adaptation state
```

---

# 5.2 Example Rule

```
IF
    NDLI high
AND WDRM repeatability decreasing
AND FatigueTrend > 20%

THEN
    reduce VO2 interval duration by 15%
    convert tempo → endurance
    insert recovery day
```

Rules are executed **in Railway**, never by GPT.

---

# 5.3 ADE Output

```
adaptive_layer
 ├─ progression_state
 ├─ neural_state
 ├─ durability_state
 ├─ metabolic_state
 └─ prescription_adjustment
```

---

# 6. System Intelligence Layers

The full intelligence stack becomes:

| Layer                    | Purpose                    |
| ------------------------ | -------------------------- |
| Load Metrics             | quantify training stress   |
| Physiology               | measure recovery response  |
| Performance Intelligence | stress behaviour modelling |
| ESPE                     | adaptation progression     |
| ADE                      | training decision logic    |

This forms a **closed-loop coaching system**.

---

# 7. Strategic System Evolution

### URF v5

```
Load monitoring
+ physiology metrics
+ performance diagnostics
```

### URF v6

```
Load monitoring
+ performance modelling
+ adaptation tracking
+ decision intelligence
```

---

# 8. Implementation Roadmap

Recommended build order.

### Phase 1

Complete PI models.

```
WDRM
NDLI
ISDM
```

### Phase 2

Energy System Progression.

```
ESPE v1
ESPE v2
```

### Phase 3

Adaptive Decision Engine.

```
ADE rule framework
adaptive_layer semantic block
training prescription logic
```

---

# 9. System Philosophy

The system is intentionally designed to avoid typical analytics mistakes.

### Principles

• Load metrics alone do not measure adaptation
• Power curves alone do not measure fatigue
• HRV alone does not measure training readiness

The Montis system integrates:

```
load
+ physiology
+ performance expression
```

to determine **true adaptation state**.

---

# 10. Strategic Outcome

The system evolves from:

```
Training analytics dashboard
```

to

```
Deterministic adaptive coaching engine
```

Capabilities unlocked:

* adaptation detection
* durability modelling
* intensity clustering control
* automated prescription logic
* race-readiness monitoring

---

# Final Summary

**Performance Intelligence (PI)** models how fitness behaves under stress.

**ESPE** measures whether training is producing physiological progression.

**ADE** converts those signals into deterministic coaching decisions.

Together they form the core of the **Montis Adaptive Coaching Engine**.

---

If you want, the **next useful step** is to write a **one-page “Montis Intelligence Stack” diagram** that visually explains:

```
Load → Physiology → Performance → Adaptation → Decision
```

                 ┌──────────────────────────┐
                 │        Athlete Data      │
                 │  (Intervals / Sensors)   │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │     Cloudflare Worker    │
                 │      Data Layer          │
                 │  - API orchestration     │
                 │  - Power curve windows   │
                 │  - Prefetch payload      │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │      Railway Engine      │
                 │  Tier-0 Normalization    │
                 │  - schema alignment      │
                 │  - activity expansion    │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │     Tier-1 Canonical     │
                 │        Metrics           │
                 │  - TSS                   │
                 │  - CTL / ATL / TSB       │
                 │  - Load distributions    │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │     Tier-2 Derived       │
                 │        Metrics           │
                 │  - ACWR                  │
                 │  - Monotony / Strain     │
                 │  - lactate calibration   │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │ Tier-3 Performance Intel │
                 │                          │
                 │  WDRM  → anaerobic load  │
                 │  ISDM  → durability      │
                 │  NDLI  → neural density  │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │ Energy System Progression│
                 │        Engine (ESPE)     │
                 │                          │
                 │  Power-curve adaptation  │
                 │  84d window comparison   │
                 │                          │
                 │  Neuromuscular           │
                 │  Anaerobic               │
                 │  VO2                     │
                 │  Threshold               │
                 │  Endurance               │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │ Adaptive Decision Engine │
                 │           (ADE)          │
                 │                          │
                 │ deterministic rules      │
                 │ training modification    │
                 │ load control logic       │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │     Semantic Graph       │
                 │        URF v6            │
                 │ structured output layer  │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │   GPT Deterministic      │
                 │        Renderer          │
                 │  coaching interpretation │
                 └──────────────────────────┘


Training Load
      │
      ▼
Physiology Response
      │
      ▼
Performance Intelligence
      │
      ▼
Energy System Progression
      │
      ▼
Adaptive Decision Engine
      │
      ▼
Training Adjustment
      │
      └───────────────→ next training cycle
