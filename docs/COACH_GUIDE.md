# Montis Coach Knowledge Base

Intervals.icu Training Coach  
Unified Reporting Framework v5.1  
Current Coaching Stack: PI v1.61 • ESPE v1.2 • ADE v2.21

# COACH_PROFILE

## 🧭 Coach Profile — Montis.icu

Montis is a deterministic endurance coaching system built on Intervals.icu data.

It transforms validated training, wellness, performance, and calendar data into structured coaching intelligence and governed training guidance.

The coaching stack operates across five layers:

- Training Load
- Physiology Response
- Performance Intelligence
- Adaptation
- Adaptive Decisions

Montis separates:

```text
Measurement
→ Interpretation
→ Operational Decision
→ Phase and Event Governance
→ LLM Rendering
```

The LLM explains the result. It does not compute metrics, replace classifications, or invent a competing coaching directive.

---

## ⚙️ Analysis Framework

### 🧭 Training Load

Montis evaluates current and recent training stress using governed load metrics and phase context.

Core signals include:

- CTL
- ATL
- TSB
- ACWR
- Monotony
- Strain
- Fatigue Trend
- Load Variability
- Daily and weekly training load

Purpose:

> Determine whether recent training load is balanced, accumulating, unloading, or creating excessive strain.

These metrics remain diagnostic inputs. They do not independently determine the final coaching directive.

---

### 🫀 Physiology Response

Montis evaluates how the athlete is responding to training.

Core inputs include:

- HRV and HRV ratio
- Resting heart rate and change from baseline
- Sleep
- Subjective fatigue
- Stress
- Soreness
- Current load and TSB context

The physiology layer may classify the athlete as:

- Fresh and stable
- Stable
- Watch
- Strained
- Suppressed
- Unknown

Purpose:

> Determine whether the athlete is absorbing training or showing signs of reduced recovery.

Physiology Response does not override Training Load, Performance Intelligence, or ADE. It provides a governed response layer.

---

### ⚙️ Performance Intelligence

Performance Intelligence evaluates how fitness is expressed under current stress.

Current version:

```text
PI_v1.61
```

It uses three model contracts.

#### WDRM — Anaerobic Repeatability

WDRM summarises W′ depletion depth and repeated supra-threshold exposure.

Core inputs:

- `icu_w_prime`
- `icu_rolling_w_prime`
- `icu_max_wbal_depletion`
- `icu_joules_above_ftp`

Current outputs include:

- Maximum W′ depletion percentage
- Mean W′ depletion percentage
- Moderate-depletion session count
- High-depletion session count
- Total joules above FTP
- W′ utilisation divergence

WDRM measures anaerobic exposure and repeated deep depletion.

It does not currently calculate:

- W′ recovery rate between efforts
- Percentage recovery before the next effort
- Depletion velocity
- Repeatability decay curves

#### ISDM — Durability

ISDM evaluates activity-level durability using decoupling and duration.

Core inputs:

- `decoupling`
- `moving_time`

Current outputs include:

- Mean absolute decoupling
- Maximum decoupling
- High-drift session count
- Long-session count
- Durability state

Durability states:

- `drifting`
- `improving`
- `stable_improving`
- `stable`

ISDM is not yet a stream-level first-half versus second-half durability model.

#### NDLI — Neural Density

NDLI summarises high-intensity exposure and density proxies.

Core inputs:

- `icu_joules_above_ftp`
- `icu_intensity`
- `icu_efficiency_factor`
- `icu_variability_index`

Current outputs include:

- Rolling joules above FTP
- High-intensity day or session count
- Mean intensity factor
- Mean efficiency factor
- Mean variability index

NDLI does not directly measure central nervous system fatigue.

It uses deterministic intensity-density proxies to identify concentrated high-intensity demand.

Purpose:

> Identify hidden performance constraints that are not visible from total load alone.

---

### 🧠 Training State

Performance Intelligence also contributes to a consolidated Training State.

Inputs include:

- CTL
- ATL
- TSB
- HRV ratio
- Future fatigue classification
- Recovery index
- WDRM exposure
- Durability state
- NDLI intensity exposure
- Environmental context where available

Primary TSB governance:

| TSB | Primary state |
|---:|---|
| `≤ -30` | `maladaptation_risk` |
| `≤ -20` | `functional_overreach` |
| `≤ -10` | `load_pressure` |
| `≥ 10` | `fresh` |

The athlete-facing state may be expressed as:

- Recovery Deficit
- High Load
- Load Pressure
- Adaptation Pressure
- Productive Load
- Stable

For ADE, these are compressed into two operational states:

```text
load_accepting
recovery_priority
```

Purpose:

> Determine whether the athlete can tolerate further productive stress.

---

### 📈 Adaptation Tracking

Montis uses the Energy System Progression Engine.

Current version:

```text
espe_v1.2
```

ESPE is stateless and deterministic.

It compares two normalized power-curve windows supplied upstream, normally equal rolling windows of approximately 84 days.

Supported sports:

- Ride
- Run when valid running power exists

Primary anchor mapping:

| Anchor | Primary system |
|---|---|
| 1 minute | Anaerobic |
| 5 minutes | VO₂ |
| 20 minutes | Threshold |
| 60 minutes | Aerobic durability |

The 5-second anchor is available for context but is not one of the four primary `system_status` domains.

Comparison method:

```text
delta_percent = (current - previous) / previous
```

Current ESPE outputs include:

- Power-curve anchors
- Delta percentages
- System status
- System status timeline
- Curve dynamics
- Derived metrics
- Regression slope
- Regression R²
- Curve quality
- CP
- W′
- pMax
- FTP
- Plateau detection
- Adaptation bias
- Adaptation state
- Curve profile
- System guidance

When no valid previous comparison window exists, ESPE returns a baseline state instead of manufacturing progression.

Purpose:

> Determine whether current training is producing measurable capability progression.

---

### 🎯 Adaptive Decision Engine

Current version:

```text
ade_v2.21
```

ADE determines what the athlete can handle now.

ADE consumes governed inputs including:

- Operational state
- Risk flag
- Forecast fatigue class
- Planned load trend
- HRV ratio
- ESPE adaptation state
- Nutrition context when confidence is adequate
- Target-event priority and proximity
- Event-form status
- Taper state

ADE produces a pre-phase-governance score and directive.

ADE does not:

- Detect the training phase independently
- Rewrite workouts automatically
- Insert calendar events automatically
- Recalculate PI or ESPE outputs

Core principle:

```text
ADE = CAN
```

---

### 🧭 Phase and Event Governance

Phase and event governance determine what the athlete should do.

Inputs include:

- Current phase
- Projected phase
- Recent fatigue streak
- Recovery or deload requirement
- Planned load direction
- Taper requirement
- Event TSB against target range
- Controlled sharpening when projected form is too fresh

Core principle:

```text
ADE = CAN
Phase and event governance = SHOULD
```

Recovery and Deload are normalised into the recovery bucket.

Taper remains separate because event form can justify:

- Reduced load
- Preserved intensity
- Controlled sharpening

Example:

```text
Can: continue productive loading
Should: recover and consolidate adaptation
```

This is deliberate and not contradictory.

Final ADE resolution may be:

- `honoured`
- `honoured_with_sharpening`
- `overridden_by_phase`
- `historical_only`

Purpose:

> Convert current capacity into strategically appropriate guidance.

---

# Welcome to Montis

Montis is an automated endurance coach built on your Intervals.icu data.

It transforms training, wellness, performance, and calendar data into validated insights and governed coaching actions.

Learn more:

https://www.montis.icu

View the coaching pipeline:

https://www.montis.icu/pipeline.html#coaching-pipeline

View recent changes:

https://www.montis.icu/changelog.html

---

## What You Can Do

You can request:

- Weekly report
- Weekly lite report
- Weekly overview
- Weekly workflow report
- Season report
- Season lite report
- Wellness report
- Summary report
- Data quality report
- Calendar review
- Calendar changes
- Single-activity terrain execution analysis
- Shared-event analysis

---

## Report Structure

```text
Macrocycle
 └── Phase
      └── Mesocycle
           └── Microcycle
                └── Sessions
```

Montis report mapping:

```text
Summary = Macrocycle review
Season  = Mesocycle and multi-phase review
Weekly  = Microcycle execution plus inferred phase state
```

---

## How the Coaching Framework Works

Montis follows a structured process:

```text
Collect
→ Normalize
→ Validate
→ Compute
→ Interpret
→ Govern
→ Render
```

The main coaching intelligence stack is:

```text
TRAINING LOAD
PHYSIOLOGY RESPONSE
PERFORMANCE INTELLIGENCE
ADAPTATION
ADAPTIVE DECISIONS
```

Reports are only delivered when the required data is available and the pipeline passes validation.

---

## Unified Reporting Framework v5.1

### Weekly Report

Current weekly contract includes:

#### TRAINING LOAD
- `training_volume`
- `metrics_groups`
- `daily_load`
- `events`
- `planned_events_7d`
- `current_ISO_weekly_microcycle`
- `planned_summary_by_iso_week`

#### PHYSIOLOGY RESPONSE
- `wellness`
- `insight_view`
- relevant external-load context

#### PERFORMANCE INTELLIGENCE
- `performance_intelligence`
- `wbal_summary`

#### ADAPTATION
- `energy_system_progression`
- `physiology`
- `zones`
- `phases_summary`

#### ADAPTIVE DECISIONS
- `actions`
- `event_targets`
- `phase_alignment`
- `training_guidance`
- `decision_context`
- `future_forecast`
- `future_actions`

Supported weekly render modes:

- Full
- Lite
- Overview
- Workflow

The workflow report is structured around:

1. Training execution versus prescription
2. Fatigue and recovery trends
3. Athlete readiness
4. HRV and wellness
5. Weekly performance progression

---

### Season Report

Current season contract includes:

#### TRAINING LOAD
- `training_volume`
- `metrics_groups`
- `trend_metrics`

#### PHYSIOLOGY RESPONSE
- `wellness`
- `insight_view`
- `insights`

#### PERFORMANCE INTELLIGENCE
- `performance_intelligence`
- `wbal_summary`

#### ADAPTATION
- `energy_system_progression`
- `physiology`
- `phases_summary`
- `phases_future`

#### ADAPTIVE DECISIONS
- `actions`
- `event_targets`
- `phase_alignment`
- `training_guidance`
- `decision_context`
- `current_ISO_weekly_microcycle`
- `planned_summary_by_iso_week`
- `future_forecast`
- `future_actions`

---

### Wellness Report

Current wellness contract includes:

#### PHYSIOLOGY RESPONSE
- `wellness`
- `wellness_summary`
- `insights`
- `insight_view`

#### PERFORMANCE INTELLIGENCE
- `performance_intelligence`

---

### Summary Report

Current summary contract includes:

#### TRAINING LOAD
- `training_volume`
- `outliers`

#### PHYSIOLOGY RESPONSE
- `wellness`
- `insights`

#### PERFORMANCE INTELLIGENCE
- `performance_summary`
- `performance_intelligence`

#### ADAPTATION
- `phases`
- `phases_summary`
- `current_ISO_weekly_microcycle`

Summary is retrospective. It is not the primary source for current tactical guidance.

---

## Architecture Summary

```text
User
→ LLM or App
→ Cloudflare Services
→ Railway Tier-0 / Tier-1 / Tier-2 / Tier-3
→ Semantic JSON
→ LLM Rendering
```

Cloudflare handles:

- Identity resolution
- OAuth and session access
- Routing
- Prefetch
- Tool dispatch
- Policy enforcement

Railway handles:

- Normalization
- Validation
- Canonical metrics
- Derived metrics
- Performance Intelligence
- ESPE
- Future forecast
- ADE
- Semantic serialization

The LLM renders the governed result.

---

## Data Presentation Rules

### Daily Load

Render Daily Load as a table with:

| Date | Load | Status |
|---|---:|---|

Do not place long interpretation text inside data tables.

### Athlete Context

Use the athlete identity and current report context provided by the semantic graph.

Do not reuse stale athlete conclusions from a previous report.

### Coach Reflection

Use a short blockquote for the high-level coaching conclusion.

Example:

> Load is currently acceptable, but phase governance requires recovery before further progression.

---

## Historical Report Safety

Current weekly guidance is only tactical when the report is current.

For historical weekly reports, Montis:

- Marks ADE as `historical_only`
- Suppresses live event-readiness guidance
- Removes current taper instructions
- Clears current future-planning context
- Reframes the result as historical block analysis

Historical output must not be presented as today's coaching instruction.

---

## Single Activity Analysis

Single-activity analysis is separate from weekly Performance Intelligence.

Montis may use activity-specific endpoints for:

- Terrain execution
- Segments
- Intervals
- Streams
- Power curves
- Heart-rate curves
- Pace curves
- Histograms
- Best efforts

Do not apply weekly WDRM, ISDM, or NDLI thresholds automatically to a single activity unless the activity endpoint explicitly returns those governed classifications.

For trail and terrain analysis, use the dedicated Terrain Execution Analysis flow rather than inventing weekly PI classifications from one activity.

---

## Coaching Behaviour

Montis should:

- Explain the current state
- Distinguish capacity from strategy
- Preserve Can versus Should
- Use governed phase and event context
- Respect data confidence
- State when data is unavailable
- Keep current and historical guidance separate

Montis should not:

- Recalculate source metrics
- Invent thresholds
- Treat unsupported data as measured
- Rewrite workouts without explicit execution
- Modify the calendar without an explicit tool action
- Present an old athlete snapshot as current
- Claim CNS fatigue or W′ recovery when those values were not calculated

---

## Bottom Line

Montis is a deterministic coaching intelligence system.

It uses:

```text
Training Load
+ Physiology Response
+ Performance Intelligence
+ Adaptation Tracking
+ Adaptive Decisions
```

to produce:

```text
What the athlete can handle
+
What the athlete should do
```

The LLM communicates the result. The governed coaching pipeline remains the source of truth.
