# Montis Coaching Intelligence Design

Montis uses a deterministic coaching pipeline that separates measurement, interpretation, operational decision-making, strategic governance, and report rendering.

This document describes the **current production design** and matches the updated Coaching Intelligence Pipeline used on the Montis architecture webpage.

### Current Versions
* **Performance Intelligence:** `PI_v1.61`
* **Energy System Progression Engine:** `espe_v1.2`
* **Adaptive Decision Engine:** `ade_v2.21`
* **Semantic contract:** URF v5.1

## Coaching Intelligence Pipeline

```text
VALIDATED TIER-1 / TIER-2 OUTPUTS
                │
                ▼
Performance Intelligence — PI v1.61
WDRM / ISDM / NDLI
                │
                ▼
Training State
load_accepting / recovery_priority
                │
                ▼
Energy System Progression — ESPE v1.2
Power-curve adaptation state
                │
                ▼
ADE v2.21 BASE DECISION — CAN
Operational capacity and risk
                │
                ▼
PHASE + EVENT GOVERNANCE — SHOULD
Recovery, build, taper and event-form control
                │
                ▼
SEMANTIC OUTPUT
Actions / Guidance / Alignment / Event Context
                │
                ▼
LLM RENDERING
Read-only interpretation
```

The Coaching Intelligence Pipeline operates only on validated outputs from the technical pipeline.

It does not recompute canonical metrics and does not allow the LLM to invent or modify coaching logic.

## Stage 1 — Performance Intelligence

Performance Intelligence evaluates how the athlete expresses fitness under current stress.

It uses three model contracts:

### WDRM — Anaerobic Repeatability

WDRM summarises the depth and frequency of supra-threshold W′ engagement.

#### Core Inputs
* `icu_w_prime`
* `icu_rolling_w_prime`
* `icu_max_wbal_depletion`
* `icu_joules_above_ftp`

#### Current Outputs
* Maximum W′ depletion percentage.
* Mean W′ depletion percentage.
* Moderate-depletion session count.
* High-depletion session count.
* Total joules above FTP.
* W′ utilisation divergence.

WDRM measures anaerobic exposure and repeated deep depletion.

It does not currently calculate:

* W′ recovery rate between efforts.
* Percentage recovery before the next effort.
* Depletion velocity.
* Repeatability decay curves.

### ISDM — Durability

ISDM evaluates cardiovascular and output stability using activity-level decoupling.

#### Core Inputs
* `decoupling`
* `moving_time`

#### Current Outputs
* Mean absolute decoupling.
* Maximum decoupling.
* High-drift session count.
* Long-session count.
* Durability state.

#### Durability States
* `drifting`
* `improving`
* `stable_improving`
* `stable`

ISDM is currently an activity-level durability model.

It does not yet compare first-half versus second-half power or calculate late-session power decay from stream data.

### NDLI — Neural Density

NDLI summarises high-intensity exposure and density proxies.

#### Core Inputs
* `icu_joules_above_ftp`
* `icu_intensity`
* `icu_efficiency_factor`
* `icu_variability_index`

#### Current Outputs
* Rolling joules above FTP.
* High-intensity day or session count.
* Mean intensity factor.
* Mean efficiency factor.
* Mean variability index.

NDLI does not directly measure central nervous system fatigue.

It uses deterministic intensity-density proxies to identify concentrated high-intensity demand.

### Performance Intelligence Scope

| Report | Data scope |
|---|---|
| Weekly | 7-day FULL dataset |
| Season | 90-day LIGHT chronic analysis plus 7-day FULL acute overlay |
| Summary | Chronic analysis plus acute overlay |

Weekly analysis retains the highest available data fidelity and is not reduced to match the season dataset.

## Stage 2 — Training State

Montis combines load, wellness, forecast, and Performance Intelligence into a consolidated Training State.

### Inputs
* CTL.
* ATL.
* TSB.
* HRV ratio.
* Future fatigue classification.
* Recovery index.
* WDRM exposure.
* Durability state.
* NDLI intensity exposure.
* Environmental context where available.

### Primary TSB Governance

| TSB | Primary state |
|---:|---|
| `≤ -30` | `maladaptation_risk` |
| `≤ -20` | `functional_overreach` |
| `≤ -10` | `load_pressure` |
| `≥ 10` | `fresh` |

The final athlete-facing state may also be expressed as:

* Recovery Deficit.
* High Load.
* Load Pressure.
* Adaptation Pressure.
* Productive Load.
* Stable.

For ADE, these are compressed into two operational states:

```text
load_accepting
recovery_priority
```

These states answer:

> Can the athlete tolerate additional training stress?

## Stage 3 — Energy System Progression

ESPE evaluates power-curve progression using two normalized comparison windows.

It is stateless and deterministic.

### Normal Input Contract

```text
power_curve
 └─ Sport
     ├─ current
     ├─ previous
     ├─ window_days
     ├─ models
     └─ curve_regression
```

The normal production configuration uses two equal rolling windows, typically approximately 84 days.

ESPE itself does not decide whether the report is weekly or seasonal. It evaluates the comparison pair supplied upstream.

### Supported Sports
* Ride.
* Run when valid running power exists.

### Anchor Durations
* 5 seconds.
* 1 minute.
* 5 minutes.
* 20 minutes.
* 60 minutes.

### Primary Energy-System Mapping

| Anchor | Primary system |
|---|---|
| 1 minute | Anaerobic |
| 5 minutes | VO₂ |
| 20 minutes | Threshold |
| 60 minutes | Aerobic durability |

The 5-second anchor is available for context but is not one of the four primary `system_status` domains.

### Comparison Method

```text
delta_percent = (current - previous) / previous
```

### Current ESPE Outputs

```text
energy_system_progression
 └─ sports
     └─ Sport
         ├─ supported
         ├─ curve_window
         ├─ power_curve_anchors
         ├─ delta_percent
         ├─ curve_dynamics
         ├─ system_status
         ├─ system_status_timeline
         ├─ derived_metrics
         ├─ curve_regression
         ├─ curve_quality
         ├─ power_model
         ├─ plateau_detected
         ├─ adaptation_bias
         ├─ adaptation_state
         ├─ curve_profile
         └─ system_guidance
```

ESPE already consumes and exposes:

* CP.
* W′.
* pMax.
* FTP.
* Regression slope.
* Regression R².
* Curve quality.
* Curve profile.
* Plateau state.
* Adaptation bias.
* Adaptation state.

When no previous comparison window exists, ESPE returns a baseline state rather than manufacturing progression.

This stage answers:

> Is current training producing measurable adaptation?

## Stage 4 — ADE Base Decision

ADE v2.21 determines what the athlete can handle now.

### ADE Inputs
* Operational state.
* Risk flag.
* Forecast fatigue class.
* Planned load trend.
* HRV ratio.
* ESPE adaptation state.
* Nutrition context when confidence is adequate.
* Target-event priority and proximity.
* Event-form status.
* Taper state.

ADE produces a **pre-phase-governance** score and directive.

### ADE Base Principle

```text
ADE = CAN
```

The ADE base decision represents immediate operational capacity.

## Stage 5 — Phase and Event Governance

Phase and event governance determine what the athlete should do.

### Governance Inputs
* Current phase.
* Projected phase.
* Recent fatigue streak.
* Recovery or deload requirement.
* Planned load direction.
* Taper requirement.
* Event TSB against target range.
* Controlled sharpening when projected form is too fresh.

### Phase Behaviour
* Recovery and Deload map into the recovery bucket.
* Taper remains separate.
* Taper may preserve selective intensity.
* Taper may permit controlled sharpening when event form is projected to be too fresh.

### Governing Principle

```text
ADE = CAN
Phase and event governance = SHOULD
```

Example:

```text
Can: continue productive loading
Should: recover and consolidate adaptation
```

This is not a contradiction. It preserves the difference between physiological capacity and strategic appropriateness.

## Final Resolution

The final ADE action is classified as:

| Resolution | Meaning |
|---|---|
| `honoured` | ADE and strategic governance agree |
| `honoured_with_sharpening` | ADE is retained with controlled taper sharpening |
| `overridden_by_phase` | Phase or event governance overrides the ADE base directive |
| `historical_only` | The report is historical and not valid as current tactical guidance |

## Semantic Output

The current coaching pipeline exposes:

```text
performance_intelligence
energy_system_progression
actions
training_guidance
decision_context
phase_alignment
event_targets
future_forecast
future_actions
```

The semantic layer preserves computed outputs and adds structured context for rendering.

It does not recompute Performance Intelligence, ESPE, or ADE.

## LLM Responsibility

The LLM is a read-only interpretation layer.

It may:

* Explain the governed result.
* Compare Can versus Should.
* Present the training state clearly.
* Summarise the reasons.
* Suggest a calendar change only through an explicit tool action.

It may not:

* Recalculate metrics.
* Replace classifications.
* Invent missing values.
* Override the ADE result.
* Create an alternative coaching directive.
* Modify the training calendar without explicit execution.

## Historical Report Safety

Current weekly guidance is only tactical when the report is current.

For stale historical weekly reports, Montis:

* Marks ADE output as `historical_only`.
* Suppresses live event-readiness guidance.
* Removes current taper instructions.
* Reframes the result as historical block analysis.

Historical output describes the state at that time and must not be presented as today's coaching instruction.

## Bottom Line

* Performance Intelligence evaluates how fitness behaves under stress.
* Training State compresses the current condition into `load_accepting` or `recovery_priority`.
* ESPE evaluates whether capability is progressing.
* ADE determines what the athlete can tolerate.
* Phase and event governance determine what the athlete should do.
* The semantic layer preserves the governed result.
* The LLM renders the result without becoming a computational or prescriptive authority.
