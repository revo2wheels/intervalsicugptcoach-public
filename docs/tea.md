# Terrain Execution Analysis (TEA)
## Intelligence Framework v1.0

---

# Purpose

Terrain Execution Analysis (TEA) is a single-activity intelligence system designed to explain how an athlete executed a route.

Unlike traditional performance models that focus on fitness, fatigue, readiness, or training load, TEA focuses on execution.

TEA answers:

- What happened on the route?
- Where did it happen?
- Why did it happen?
- What was the primary limiter?
- How effectively did the athlete convert fitness into performance?

TEA is an execution model.

It is not a readiness model.
It is not a forecasting model.
It is not a training load model.
It is not a physiological adaptation model.

---

# Core Philosophy

Fitness determines potential.

Execution determines outcome.

Two athletes with identical:

- FTP
- VO2max
- CTL
- Readiness
- Recovery

can produce dramatically different performances on the same terrain.

TEA exists to explain that difference.

---

# Position Within Montis Intelligence

TEA operates alongside the existing intelligence stack.

| System | Purpose |
|----------|----------|
| Physiological State | Current body condition |
| Performance Intelligence | Load and adaptation interpretation |
| ESPE | Adaptation detection |
| ADE | Decision engine |
| TEA | Route execution intelligence |

TEA answers:

> What happened on the terrain?

Performance Intelligence answers:

> What does it mean?

ESPE answers:

> What adaptation occurred?

ADE answers:

> What should happen next?

---

# Core Principle

TEA evaluates:

```text
Terrain Demand
versus
Athlete Response
```

Execution quality is determined by how effectively the athlete responds to terrain demands.

---

# Terrain Domains

Every activity is decomposed into terrain domains.

## Flat Terrain

Grade:

```text
0–3%
```

Characteristics:

- Aerobic efficiency
- Sustainable pacing
- Mechanical economy

Primary Metrics:

- Speed
- Pace
- Power
- Cadence
- HR

---

## Rolling Terrain

Grade:

```text
3–8%
```

Characteristics:

- Constant terrain transitions
- Rhythm disruption
- Variable energy demands

Primary Metrics:

- Pace stability
- Power variability
- Cadence stability

---

## Climbing Terrain

Grade:

```text
8%+
```

Characteristics:

- High muscular demand
- High cardiovascular demand
- Vertical efficiency

Primary Metrics:

- VAM
- Vertical speed
- Power
- HR
- Cadence

---

## Descending Terrain

Negative grade

Characteristics:

- Eccentric muscle loading
- Neuromuscular control
- Technical execution

Primary Metrics:

- Speed preservation
- Cadence
- Control
- Confidence

---

## Hiking Terrain

Terrain where hiking becomes more economical than running.

Characteristics:

- Vertical efficiency
- Energy conservation
- Muscular endurance

Primary Metrics:

- Vertical gain rate
- Cadence
- HR
- Speed

---

# Route Segmentation

Routes should be segmented into meaningful execution blocks.

Recommended segment size:

```text
100–250 metres
```

Each segment should be independently analysed.

Example:

```text
Segment 1
0.00–0.25 km

Segment 2
0.25–0.50 km

Segment 3
0.50–0.75 km
```

Each segment receives:

- Terrain classification
- Execution classification
- Limiter assessment
- Coaching interpretation

---

# Terrain Demand

Terrain demand represents the challenge imposed by the route.

Demand is influenced by:

- Gradient
- Elevation change
- Terrain variability
- Terrain transitions
- Technicality
- Surface quality
- Environmental stress

Terrain demand is independent of athlete ability.

---

# Execution Quality

Execution quality represents how effectively terrain was managed.

Categories:

## Controlled

Characteristics:

- Stable effort
- Stable mechanics
- Sustainable pacing

Interpretation:

Athlete responded appropriately to terrain demands.

---

## Moderate

Characteristics:

- Minor inefficiencies
- Localised pacing errors
- Mild durability loss

Interpretation:

Execution acceptable but improvable.

---

## Limited

Characteristics:

- Significant efficiency loss
- Performance collapse
- Terrain-specific weakness

Interpretation:

Terrain exceeded current capability.

---

# Terrain Efficiency

Terrain efficiency evaluates how effectively physiological resources are converted into performance.

Examples:

High HR + low speed

→ Poor efficiency

Moderate HR + strong speed

→ High efficiency

High power + low vertical gain

→ Poor climbing efficiency

Moderate power + strong vertical gain

→ High climbing efficiency

---

# Terrain Durability

Terrain durability measures the ability to sustain execution quality throughout the activity.

Key Question:

> Can the athlete maintain performance as fatigue accumulates?

High durability:

- Stable cadence
- Stable pace
- Stable climbing rate
- Stable descending quality

Low durability:

- Speed fade
- VAM fade
- Cadence degradation
- Mechanical deterioration

---

# Durability Markers

## Speed Fade

Speed decreases despite similar terrain.

Possible Causes:

- Fatigue
- Fuel depletion
- Muscular endurance limitation

---

## Climbing Fade

Vertical performance deteriorates over time.

Indicators:

- Reduced VAM
- Reduced climbing speed
- Reduced power

---

## Descending Fade

Downhill capability deteriorates.

Indicators:

- Reduced speed
- Increased caution
- Cadence instability

---

## Stride Degradation

Cadence remains stable.

Speed declines.

Interpretation:

Stride length deterioration.

Often indicates muscular fatigue.

---

# Pacing Intelligence

TEA evaluates pacing quality.

## Controlled

Effort matched terrain demands.

---

## Aggressive

Excessive effort early.

Risk of late collapse.

---

## Conservative

Capacity remained unused.

Potential underperformance.

---

## Positive Split

Performance deteriorates progressively.

---

## Negative Split

Performance improves progressively.

---

## Even Pacing

Stable performance throughout.

---

# Fatigue Analysis

TEA identifies where fatigue emerged.

---

## Muscular Fatigue

Indicators:

- HR available
- Speed falls
- Power falls

Interpretation:

Local muscular limitation.

Typical examples:

- Climbs
- Long descents
- Technical terrain

---

## Metabolic Fatigue

Indicators:

- Rising HR
- Falling speed
- Increasing effort cost

Interpretation:

Aerobic or fueling limitation.

---

## Neuromuscular Fatigue

Indicators:

- Cadence instability
- Reduced coordination
- Descending deterioration

Interpretation:

Nervous system fatigue.

---

## Environmental Fatigue

Indicators:

- Rising HR
- Falling efficiency
- Heat exposure

Interpretation:

Environmental stress.

Examples:

- Heat
- Humidity
- Altitude

---

# Limiter Detection

TEA attempts to identify the dominant limiter.

Only one primary limiter should be assigned.

---

## Aerobic Limiter

Cardiovascular system reaches capacity before terrain performance.

---

## Muscular Endurance Limiter

Muscular fatigue occurs before cardiovascular limitation.

---

## Pacing Limiter

Execution failure caused by pacing decisions.

---

## Fueling Limiter

Execution failure caused by energy depletion.

---

## Mechanical Limiter

Execution failure caused by movement inefficiency.

---

## Skill Limiter

Execution failure caused by technical terrain handling.

---

## Environmental Limiter

Execution failure caused primarily by environmental stress.

---

# Confidence Model

Confidence reflects certainty of interpretation.

## High

Multiple supporting signals.

Consistent evidence.

---

## Moderate

Reasonable evidence.

Some uncertainty.

---

## Low

Limited data.

Interpretation should be treated cautiously.

---

# Segment Intelligence

Each segment should contain:

```json
{
  "terrain": "",
  "grade_pct": 0,
  "elevation_delta_m": 0,
  "execution_state": "",
  "limiter": "",
  "coach_note": ""
}
```

---

# Activity Summary Intelligence

The activity summary should answer:

## Terrain Demand

Low
Moderate
High

---

## Execution Quality

Controlled
Mixed
Limited

---

## Primary Limiter

Most influential factor.

---

## Confidence

Low
Moderate
High

---

# Coaching Interpretation Rules

TEA must always provide:

1. Observation
2. Interpretation
3. Implication

Example:

Observation:

Climbing speed decreased 18% during final third.

Interpretation:

Terrain durability declined as muscular fatigue accumulated.

Implication:

Muscular endurance likely limits sustained climbing performance.

---

# Map Intelligence

TEA is designed primarily for spatial visualisation.

Every interpretation should be traceable to a location on the route.

The map is the primary visual surface.

The summary card is secondary.

Users should be able to answer:

- Where did I perform well?
- Where did I struggle?
- Where did fatigue appear?
- Where did pacing break down?

directly from the map.

---

# Output Philosophy

TEA is diagnostic.

TEA explains execution.

TEA does not prescribe training.

Training recommendations remain the responsibility of:

- Performance Intelligence
- ESPE
- ADE

TEA answers:

> What happened?

The broader Montis intelligence stack determines:

> What should happen next?