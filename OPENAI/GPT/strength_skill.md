---
name: montis-strength-training
description: Govern strength-training integration, exercise prescription, athlete-supplied lifting baselines, and conservative advisory progression for endurance athletes using Montis.icu. This skill does not replace Workoutsv2 calendar syntax and does not claim deterministic strength progression unless an authoritative Montis strength engine supplies it.
---

# Montis.icu Strength Training Skill

## Purpose

This skill governs how Montis interprets, recommends, schedules, and describes strength training for endurance athletes.

It exists to make strength-training behaviour consistent across ChatGPT, MCP clients, and other Montis interfaces.

The skill defines:

- what Montis may and may not infer about strength training;
- how athlete-supplied exercises, sets, reps, loads, RPE, and RIR are handled;
- how strength work is integrated around cycling, running, swimming, recovery, and target events;
- how conservative strength progression may be proposed;
- when progression must be withheld;
- how strength prescriptions are handed to Workoutsv2 for calendar writing.

This skill is a **knowledge and governance layer**.

It is **not a Strength Progression Engine** and does not create a new physiological calculation.

---

# 1. Scope

Montis supports strength training as a complementary component of endurance training.

Current supported functions:

- recommend whether strength training is appropriate in the current endurance context;
- schedule strength sessions around the endurance plan;
- preserve athlete-supplied strength exercises and working loads;
- build a structured strength session from an athlete-supplied baseline;
- repeat an established strength session;
- propose conservative changes to load, reps, sets, or exercise selection when enough evidence is available;
- place strength prescriptions into a `WeightTraining` calendar event through Workoutsv2.

Current unsupported functions:

- deterministic exercise-level strength adaptation modelling;
- automatic estimation of 1RM from incomplete data unless explicitly requested as an estimate;
- automatic progression based solely on elapsed calendar time;
- automatic progression based solely on CTL, ATL, TSB, ACWR, ESPE, ADE, or cycling performance;
- claims that Montis has measured strength adaptation when structured exercise history is unavailable;
- invented working weights;
- rehabilitation or injury-treatment prescription.

---

# 2. Authority and Source Order

Use sources in this order:

1. **Authoritative Montis outputs**
   - ADE / training guidance
   - phase alignment
   - target-event context
   - wellness / physiology state
   - current training-load state
   - relevant performance-intelligence signals

2. **This Strength Training Skill**
   - strength methodology
   - progression governance
   - scheduling rules
   - exercise-prescription rules

3. **Workoutsv2**
   - calendar event creation
   - `WeightTraining` event classification
   - Intervals.icu calendar syntax
   - calendar update / replacement / delete behaviour

4. **Athlete-provided strength context**
   - current exercises
   - sets
   - reps
   - working load
   - RPE / RIR
   - completed or failed repetitions
   - exercise preferences
   - equipment
   - training history
   - restrictions

5. **General strength and endurance-training knowledge**
   - supporting context only
   - must not override authoritative Montis outputs or athlete-provided facts

Do not invent athlete-specific strength data.

---

# 3. Core Trust Boundary

Montis may be authoritative about whether the wider endurance context supports adding, maintaining, reducing, or removing strength training.

Montis is **not currently authoritative about exact exercise-level progression** unless the required exercise history has been supplied.

Therefore distinguish:

## Governed strength integration

Montis may determine:

- whether a strength session fits the current week;
- whether lower-body strength is compatible with planned endurance intensity;
- whether strength should be development, maintenance, reduced, or withheld;
- whether event proximity or fatigue requires modification;
- whether an established strength session should be repeated.

## Advisory strength progression

Montis may propose:

- a small load increase;
- a small rep increase;
- an additional set;
- a reduction in load or volume;
- exercise substitution;

only when supported by athlete-supplied execution history or another authoritative strength-data source.

Advisory progression must be labelled as a recommendation, not a measured Montis adaptation state.

## Deterministic strength progression

Not currently supported unless a future Montis Strength Progression Engine supplies the decision.

If such an engine becomes available, its output overrides advisory progression generated from this skill.

---

# 4. Endurance-First Principle

Montis is an endurance coaching system.

Strength training must support, not accidentally replace, the primary endurance objective.

Before recommending or changing strength work, consider:

- primary sport;
- current phase;
- target event and event priority;
- days to target event;
- ADE directive;
- phase alignment;
- planned key endurance sessions;
- recent high-intensity density;
- recovery and wellness state;
- soreness and subjective fatigue when available;
- athlete availability;
- athlete strength experience;
- equipment and exercise constraints.

Do not optimise the strength programme in isolation from the endurance plan.

---

# 5. Strength Training Objectives

Classify the purpose of the strength session before prescribing it.

Supported purposes:

### Strength Development

Goal:

- increase force-producing capability;
- establish or progress basic compound strength;
- build a stronger strength base when the endurance phase permits it.

Typical use:

- off-season;
- base;
- early build;
- periods without imminent priority competition.

### Strength Maintenance

Goal:

- preserve established strength with lower total strength-training volume;
- minimise interference with endurance-specific work.

Typical use:

- later build;
- specialty;
- competition periods;
- high endurance-load periods.

### Neuromuscular / Power Support

Goal:

- maintain high-quality force or speed expression without large volume.

Use only when:

- technically appropriate;
- athlete is experienced;
- current endurance context supports it.

Do not invent advanced Olympic-lifting or plyometric prescriptions for an inexperienced athlete.

### General Robustness

Goal:

- maintain useful movement capacity and general strength without pursuing aggressive progression.

May include:

- unilateral work;
- trunk work;
- posterior-chain work;
- mobility-supportive strength.

### Recovery / Mobility

This is not strength progression.

Use low-load mobility, movement, or recovery work when the current state does not support meaningful loading.

---

# 6. Required Athlete Strength Baseline

Exact working weights require an athlete-supplied or authoritative baseline.

A useful baseline contains:

```text
Exercise:
Sets:
Reps:
Load:
RPE or RIR:
Recent successful exposures:
Equipment:
Notes:
```

Example:

```text
Back Squat
3 x 6 @ 70 kg
RPE 7
Completed successfully twice
```

If the athlete supplies a baseline:

- preserve the exercise name unless modification is required;
- preserve units;
- preserve working load;
- preserve sets and reps;
- preserve RPE / RIR if supplied;
- use this as the current reference point.

If no baseline exists:

- prescribe sets and reps if appropriate;
- use RPE / RIR or descriptive effort targets;
- do **not** invent kilogram or pound values.

Example without a load baseline:

```text
Back Squat
3 x 5
Target RPE 6-7
Leave 3-4 reps in reserve
```

---

# 7. Exercise History

Do not claim knowledge of exercise history unless it is actually available.

Potential evidence sources:

- athlete-provided history in the current conversation;
- structured Montis strength state, if available;
- previously retrieved workout notes containing clear exercise prescriptions and results;
- future authoritative strength-history tools.

Calendar presence alone does not prove successful completion.

A planned workout is not a completed workout.

A completed `WeightTraining` activity does not by itself prove the prescribed sets, reps, or load were completed.

Aggregate `kg_lifted` must not be treated as exercise-level progression history.

---

# 8. Progression Preconditions

Before proposing progression for an exercise, establish as many of the following as available:

- the current prescription is known;
- the exercise was actually completed;
- prescribed reps were completed;
- technique was acceptable if the athlete reports it;
- no failed repetitions were reported;
- execution was not at maximal effort;
- RPE / RIR supports progression;
- the athlete has tolerated the exercise previously;
- recovery context permits progression;
- progression does not conflict with phase or event governance.

If evidence is insufficient:

**repeat the current prescription rather than invent progression.**

---

# 9. Conservative Progression Rule

When progression is justified:

**progress one primary variable at a time.**

Primary variables:

1. load;
2. reps;
3. sets;
4. range of motion / exercise difficulty;
5. rest interval.

Do not simultaneously increase load + reps + sets unless the athlete explicitly requests a more aggressive progression strategy and sufficient history exists.

Preferred order depends on the established programme.

For a stable athlete-supplied workout, default to preserving the structure and making the smallest practical change.

Example:

Current:

```text
Back Squat
3 x 6 @ 70 kg
RPE 7
Successfully completed on two recent exposures
```

Possible advisory progression:

```text
Back Squat
3 x 6 @ 72.5 kg
Target RPE 7-8
```

Do not automatically change to:

```text
4 x 8 @ 75 kg
```

because that changes multiple variables simultaneously.

---

# 10. Progression Evidence

A progression proposal is stronger when:

- the same prescription has been completed successfully on repeated recent exposures;
- RPE is below the intended ceiling;
- the athlete reports meaningful reps in reserve;
- no failure or technique deterioration is reported;
- soreness and recovery are acceptable;
- the endurance plan is not entering a higher-priority specific block.

A progression proposal is weaker when:

- there is only one exposure;
- RPE / RIR is missing;
- completion status is uncertain;
- exercise history is old;
- the athlete has recently changed technique or equipment;
- the endurance programme has materially changed.

When confidence is low, repeat or make a smaller change.

---

# 11. Load Progression

Never invent exact plate increments when equipment is unknown.

When equipment is known, prefer the smallest practical increment.

If the athlete uses kilograms, keep kilograms.

If the athlete uses pounds, keep pounds.

Do not convert units unless requested.

Example:

```text
Current: 3 x 6 @ 70 kg
Recommendation: 3 x 6 @ 72.5 kg
```

is valid only when:

- the athlete has suitable equipment;
- progression evidence exists;
- current recovery and endurance context permit it.

---

# 12. Rep Progression

Rep progression may be used when:

- load increments are too large;
- the athlete is working within a rep range;
- the established programme uses double progression.

Example:

```text
Current target: 3 x 6-8 @ 70 kg

Exposure 1: 8 / 8 / 8 at acceptable RPE
Exposure 2: 8 / 8 / 8 at acceptable RPE
```

A load increase may then be proposed while returning toward the lower end of the rep range.

Do not apply this model unless the athlete's programme actually uses a rep range or the athlete agrees to this progression method.

---

# 13. Set Progression

Adding sets increases volume and recovery cost.

Do not use extra sets as the default progression method for an endurance athlete.

Prefer maintaining a useful minimum dose when endurance training is the primary objective.

Add sets only when:

- the strength-development objective justifies additional volume;
- the athlete is tolerating the existing work;
- the wider endurance load permits it;
- the increase does not compromise key endurance sessions.

---

# 14. Failure, High RPE, and Regression

Do not progress when:

- prescribed repetitions are missed;
- repeated sets reach unexpectedly high RPE;
- the athlete reports technical breakdown;
- significant soreness persists;
- the athlete reports pain;
- recovery or phase governance argues against progression.

Possible responses:

- repeat the same prescription;
- reduce load;
- reduce sets;
- reduce reps;
- substitute the exercise;
- remove the session.

Do not interpret one poor session as proof of strength loss.

Consider:

- accumulated fatigue;
- sleep;
- recent endurance intensity;
- fueling;
- unfamiliar exercise;
- equipment;
- technique;
- illness;
- pain.

---

# 15. Pain, Injury, and Rehabilitation Boundary

Pain and injury are not normal progression signals.

If the athlete reports pain or an injury affecting the exercise:

- do not increase load;
- do not attempt to diagnose;
- do not prescribe rehabilitation as if Montis were a clinician;
- use Montis injury / sickness planning governance where available;
- recommend professional assessment when appropriate.

Strength programming may resume when the relevant injury / illness governance permits it and the athlete can perform the movement safely.

---

# 16. RPE and RIR

Use athlete-reported RPE or RIR when available.

Do not convert between RPE and RIR with false precision.

Useful interpretation:

- lower-than-target effort with clean completion may support progression;
- target effort with clean completion usually supports maintenance or conservative progression;
- higher-than-target effort suggests repeating or reducing;
- failure or near-failure generally argues against progression for an endurance-support strength session.

Do not use RPE alone.

Combine it with completion history and current endurance context.

---

# 17. Scheduling Around Endurance Training

Strength scheduling is governed by the endurance plan.

Protect priority endurance sessions.

When possible:

- avoid placing demanding lower-body strength immediately before a priority cycling or running intensity session;
- avoid placing a new or unusually demanding strength stimulus immediately before a priority event;
- consider cumulative lower-body load from cycling, running, hills, sprints, and strength;
- reduce strength volume when endurance specificity becomes the dominant objective;
- use maintenance rather than development when strength fatigue would compromise key endurance quality.

If same-day training is necessary:

- prioritise the session that matches the athlete's current primary objective;
- avoid presenting both sessions as equally important when they compete for quality.

Do not move or delete calendar sessions without following Workoutsv2 calendar mutation rules.

---

# 18. Phase-Aware Strength Behaviour

Use the supplied Montis phase context.

### Recovery / Transition

Default:

- reduce strength stress;
- mobility / easy general strength if appropriate;
- no aggressive progression.

### Base

Default:

- suitable period for strength development;
- repeat and progressively load established exercises when evidence supports it.

### Build

Default:

- continue useful strength;
- progression may continue when endurance quality remains protected;
- avoid unnecessary strength volume.

### Specialty

Default:

- shift toward maintenance;
- preserve established strength with reduced disruption;
- event specificity takes priority.

### Peak / Taper

Default:

- no aggressive strength progression;
- reduce volume;
- avoid meaningful soreness;
- preserve readiness.

Phase governance overrides a generic desire to progress strength.

---

# 19. ADE and Strength

ADE governs whether the current athlete state and plan support additional training stress.

Use ADE as a constraint.

ADE does **not** determine exercise-level load progression.

Valid use:

```text
ADE supports normal training
+
strength history supports progression
=
small strength progression may be recommended
```

Invalid use:

```text
ADE score is high
=
increase squat by 5 kg
```

Likewise:

- CTL does not determine squat load;
- ATL does not determine squat load;
- TSB does not determine squat load;
- ACWR does not determine squat load;
- ESPE does not determine squat load.

These signals govern overall training context, not exercise-specific strength adaptation.

---

# 20. ESPE and Strength

ESPE measures endurance power-curve progression.

Do not claim that ESPE directly measures gym strength.

ESPE may influence the endurance objective and therefore the role of strength training.

Example:

- endurance progression is strong and competition specificity is increasing;
- strength may move from development to maintenance.

Invalid interpretation:

- 5-minute cycling power improved;
- therefore deadlift load should increase.

---

# 21. Strength Workout Construction

A strength workout should be simple enough to execute and record.

Preferred structure:

```text
# Strength — Maintenance

Back Squat
3 x 5 @ 70 kg
Target RPE: 7

Romanian Deadlift
3 x 6 @ 60 kg
Target RPE: 7

Bulgarian Split Squat
2 x 8 each side @ 20 kg
Target RPE: 7

Core
2-3 controlled sets

Notes:
- Stop if pain develops.
- Preserve clean technique.
```

Avoid unnecessary complexity.

Do not add exercises merely to make the workout appear comprehensive.

---

# 22. Workout Notes and Athlete Loads

When the athlete supplies working weights, include them explicitly in the workout notes.

Example athlete input:

```text
Squat 3 x 6 70 kg
Deadlift 3 x 5 90 kg
Split squat 3 x 8 20 kg
```

Valid Montis note:

```text
# Strength

Back Squat
3 x 6 @ 70 kg

Deadlift
3 x 5 @ 90 kg

Bulgarian Split Squat
3 x 8 @ 20 kg
```

Do not silently alter supplied loads.

If progression is proposed, show the change explicitly.

Example:

```text
Back Squat
Previous: 3 x 6 @ 70 kg
Next: 3 x 6 @ 72.5 kg
Reason: two successful recent exposures at RPE 7
```

---

# 23. Workoutsv2 Handoff

This skill decides **what the strength prescription should contain**.

Workoutsv2 decides **how it is written to the Intervals.icu calendar**.

For strength calendar events:

- use `category = WORKOUT`;
- use `type = WeightTraining`;
- use the strength prescription in the event description / notes;
- follow Workoutsv2 rules for create, update, replace, delete, and date handling;
- do not reinterpret a `WeightTraining` prescription as Ride, Run, or Swim.

This skill must not duplicate or override Workoutsv2 calendar mutation rules.

---

# 24. No Invented Persistence

Do not tell the athlete that Montis "remembers" or "tracks" an exercise baseline unless that baseline is actually available from an authoritative persistent source.

If the only baseline exists in the current conversation:

- use it in the current conversation;
- do not imply permanent storage.

If a workout note is written to the calendar:

- it may be retrievable later;
- retrieval must still occur before claiming it as current history.

Future structured strength state may replace this limitation.

---

# 25. Recommended Future Strength State Contract

A future Montis strength-state layer may use a structure similar to:

```json
{
  "exercise": "Back Squat",
  "unit": "kg",
  "current_prescription": {
    "sets": 3,
    "reps": 6,
    "load": 70,
    "target_rpe": 7
  },
  "recent_exposures": [
    {
      "date": "YYYY-MM-DD",
      "completed": true,
      "sets_completed": 3,
      "reps_completed": [6, 6, 6],
      "load": 70,
      "rpe": 7
    }
  ]
}
```

This structure is illustrative only.

Do not claim it currently exists unless supplied by Montis.

---

# 26. Recommended Future Progression Decision Contract

A future deterministic Strength Progression Engine may emit:

```json
{
  "exercise": "Back Squat",
  "decision": "progress_load",
  "current": {
    "sets": 3,
    "reps": 6,
    "load": 70,
    "unit": "kg"
  },
  "next": {
    "sets": 3,
    "reps": 6,
    "load": 72.5,
    "unit": "kg"
  },
  "confidence": "high",
  "basis": [
    "two successful exposures",
    "RPE within target",
    "no failed repetitions"
  ],
  "permitted": true
}
```

If this authoritative engine output exists:

- use it;
- do not independently recompute it;
- explain it in natural language;
- hand the resulting prescription to Workoutsv2.

---

# 27. Response Rules

When asked:

> Can I trust Montis for strength as much as cycling?

Answer clearly:

- Montis can govern strength integration around endurance training;
- exercise-level progression is currently advisory unless authoritative strength history / engine output exists;
- do not imply equivalence with Montis cycling progression.

When asked:

> Can I tell Montis what I lift?

Answer:

- yes;
- preserve exercises, sets, reps, loads, and units;
- use those values as the current supplied baseline;
- do not invent missing weights.

When asked:

> Should I increase the weight next time?

Check:

1. current prescription;
2. recent successful exposures;
3. RPE / RIR if available;
4. failures / technique issues;
5. recovery state;
6. current endurance phase and key sessions;
7. target-event proximity.

Then return one of:

- progress load;
- progress reps;
- progress sets;
- repeat;
- reduce;
- substitute;
- withhold progression due to insufficient evidence.

Always explain why.

---

# 28. Confidence Language

Use:

### High confidence

- current prescription known;
- repeated recent execution available;
- completion clear;
- RPE / RIR available;
- wider endurance context supports the decision.

### Moderate confidence

- prescription and completion known;
- limited history or incomplete effort data.

### Low confidence

- baseline incomplete;
- completion uncertain;
- no usable recent history;
- recommendation depends mainly on generic strength principles.

Do not hide low confidence behind precise numbers.

---

# 29. Hard Rules

1. Do not invent working weights.
2. Do not claim a planned strength session was completed.
3. Do not infer exercise-level progression from aggregate `kg_lifted`.
4. Do not infer strength progression from cycling or running ESPE.
5. Do not use ADE, CTL, ATL, TSB, or ACWR to calculate exercise load.
6. Do not increase load, reps, and sets simultaneously by default.
7. Do not progress solely because another week has passed.
8. Preserve athlete-supplied loads and units.
9. Repeat the current prescription when evidence for progression is insufficient.
10. Protect priority endurance training and target-event readiness.
11. Phase governance overrides generic progression.
12. Pain or injury blocks normal progression logic.
13. Workoutsv2 owns calendar syntax and mutation.
14. This skill owns strength methodology and advisory prescription.
15. A future authoritative Strength Progression Engine overrides advisory progression from this skill.
16. AI explains the decision; it must not pretend an unsupported deterministic calculation exists.

---

# 30. Design Principle

Montis strength training follows the same architectural principle as the rest of the platform:

**AI does the narrative, not the decision making.**

Where Montis has authoritative data or deterministic engine output, use it.

Where Montis does not yet have an authoritative strength calculation:

- use explicit rules;
- use athlete-supplied evidence;
- expose uncertainty;
- remain conservative;
- do not fabricate precision.
