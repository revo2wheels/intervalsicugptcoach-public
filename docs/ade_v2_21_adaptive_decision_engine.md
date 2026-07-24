# ADE v2.21 — Adaptive Decision Engine

Montis uses ADE as the operational decision layer that determines what an athlete can safely tolerate now, then reconciles that with phase, taper, and event governance to decide what the athlete should do next.

ADE does not replace the training phase model. It produces a base decision that is subsequently checked against the required strategic phase.

### ADE Base Decision — What You Can Handle
ADE combines the current operational and forecast state using:

* **Operational State:** Whether the athlete is `load_accepting` or `recovery_priority`.
* **Risk Flag:** Derived from the future fatigue forecast.
* **Forecast Fatigue:** Green, amber, red, or transition context.
* **Load Trend:** Whether planned load is increasing, stable, decreasing, or missing.
* **HRV Ratio:** Used as an additional physiological modifier when available.
* **Adaptation State:** Supplied by ESPE to show whether energy-system capability is improving, stable, mixed, declining, or still at baseline.
* **Nutrition Context:** Used only when the nutrition signal has adequate confidence.
* **Event Context:** Includes target-event priority, proximity, taper state, and expected event form.

ADE scores the base decision before phase governance is applied.

### Operational States

| State | Meaning |
|---|---|
| `load_accepting` | Current physiology and recent execution support continued productive training |
| `recovery_priority` | Recovery should take priority before further load is added |

The underlying Performance Intelligence state may be more detailed, but ADE consumes this simplified operational state.

### Risk Classification
ADE uses the future fatigue forecast to assign the immediate risk flag:

| Forecast fatigue | ADE risk flag |
|---|---|
| Green or transition | Normal |
| Amber | Moderate |
| Red | High |

ACWR, monotony, strain, fatigue trend, durability, and load variability remain important Montis metrics, but they are not all scored directly inside ADE. They influence upstream phase, load, forecast, and Performance Intelligence layers.

### Adaptation Focus
ADE also consumes the current ESPE adaptation state.

This allows it to distinguish between situations such as:

* Fitness improving with stable recovery.
* Productive load that should be maintained.
* Mixed adaptation requiring consolidation.
* Declining capability that may justify a different training emphasis.
* Baseline or unsupported data where confidence must remain limited.

ADE does not independently recalculate ESPE outputs.

### Target Event and Taper Context
ADE reads target-event information from the calendar and event-readiness layers.

For supported race events it can evaluate:

* Event priority.
* Days to event.
* Training bias.
* Taper state.
* Event TSB relative to the target range.
* Whether the athlete is too fatigued, inside the target range, or too fresh.

Raw calendar CTL and ATL values are not treated as authoritative event form. ADE uses the governed event-readiness context or the event-sunrise forecast state.

### Taper Governance
Taper is handled separately from general recovery.

Possible taper outcomes include:

* **Taper context active:** Maintain reduced load with selective intensity.
* **Taper load risk:** Planned load remains too high for the taper requirement.
* **Taper load conflict:** The planned direction conflicts with the required taper.
* **Taper sharpening required:** The athlete is projected to be too fresh, so controlled race-specific sharpening may be appropriate.
* **Freshness above target:** More unloading is not automatically better.

Recovery and Deload are normalised into the recovery bucket. Taper remains distinct because event form can justify selective sharpening.

### Phase Governance — What You Should Do
Phase governance is applied after the ADE base decision.

It resolves the strategically required phase from:

* Current and projected phase.
* Recent fatigue streak.
* Recovery or deload requirement.
* Planned load direction.
* Taper requirement.
* Event form and sharpening exceptions.

The required phase may be:

* Base.
* Build.
* Peak.
* Recovery.
* Taper.
* Transition.

`required_phase` is not only a block-termination signal. It represents the strategic phase that should govern the next decision.

### Can vs Should
Montis preserves both layers:

| Layer | Question |
|---|---|
| ADE base decision | What can the athlete tolerate now? |
| Phase governance | What should the athlete do to support the current plan and event objective? |

The final guidance can therefore state:

```text
Can: continue productive loading
Should: recover because the current phase requires consolidation
```

This is deliberate, not contradictory.

### Final Resolution
The final ADE action is classified as:

| Resolution | Meaning |
|---|---|
| `honoured` | The ADE base directive agrees with phase governance |
| `honoured_with_sharpening` | The ADE directive is retained with controlled taper sharpening |
| `overridden_by_phase` | Strategic phase requirements override the base operational directive |
| `historical_only` | The report is historical and must not be treated as current guidance |

### Example
An athlete may show:

* ACWR inside the normal range.
* Stable HRV.
* A `load_accepting` operational state.
* No immediate high-risk signal.

ADE may therefore conclude that more load is physiologically tolerable.

However, if the athlete is in a recovery phase after sustained fatigue, the final result can still be:

```text
Can: keep training
Should: reduce load and consolidate adaptation
Resolution: overridden_by_phase
```

During taper, the opposite can also occur. If the athlete is projected to be too fresh, the final result may preserve a small controlled increase:

```text
Can: tolerate race-specific work
Should: taper with selective sharpening
Resolution: honoured_with_sharpening
```

### How ADE Fits the Montis Stack

```text
Training Load
    ↓
Physiology and Wellness
    ↓
Performance Intelligence
    ↓
ESPE Adaptation State
    ↓
ADE Base Decision — CAN
    ↓
Phase and Event Governance — SHOULD
    ↓
Final Training Guidance
```

### Scientific Alignment
ADE is a decision-layer synthesis rather than a new physiological theory.

Its architecture aligns with established concepts:

| Domain | Role in Montis |
|---|---|
| Fitness-fatigue modelling | Separates accumulated fitness from short-term fatigue |
| Load-pattern analysis | Identifies risk and instability upstream |
| Periodisation | Defines the strategic phase and sequence |
| Taper science | Supports fatigue reduction while preserving useful intensity |
| Adaptation modelling | Prevents one system from being optimised without recovery context |
| Event readiness | Adjusts taper decisions using projected event form |

The implementation should therefore be described as a physiology-constrained and phase-governed decision system.

### Historical Report Safety
ADE guidance is only tactical when the weekly report is current.

For stale historical weekly reports Montis:

* Marks the action as `historical_only`.
* Suppresses live event-readiness guidance.
* Removes current taper recommendations.
* Replaces the directive with historical block context.

Historical ADE output describes what the system concluded at that time. It must not be presented as today's instruction.

### Bottom Line
* ADE v2.21 determines immediate operational capacity.
* It consumes governed upstream metrics rather than recalculating them.
* Phase detection happens outside ADE.
* Phase governance is applied after the ADE base score.
* Recovery and Deload share a recovery bucket.
* Taper remains separate and can include selective sharpening.
* The final decision preserves both **Can** and **Should**.
* Strategic phase and event requirements can override apparent short-term readiness.
