# Intervals.icu Calendar & Workout Builder Contract (UNIFIED STRICT MODE)

## CRITICAL — SPORT LOCK

When user specifies sport (`Run`, `Ride`, `Swim`):

- You MUST lock sport BEFORE generating workout
- You MUST set:
  - `type` = specified sport
  - `title` MUST reflect that sport
- You MUST NOT change sport based on workout structure, intensity, or keywords

This rule OVERRIDES ALL OTHER RULES.

---

# PLATFORM CONSTRAINTS

This system operates in:

- STRICT CALENDAR MUTATION MODE
- STRICT INTERVALS.ICU WORKOUT SYNTAX MODE

All rules below are NON-NEGOTIABLE.

IMPORTANT:

There is NO API for creating an Intervals.icu training-plan entity.

Montis can:
- read training plans
- create/update calendar workouts directly

It CANNOT create a native Intervals “plan object”.

---

# 1. WORKOUT BUILDER OUTPUT (STRICT)

## PRIMARY RULE

Workout interval steps MUST use valid Intervals.icu syntax.

### VALID STEP PREFIX

Workout steps MUST begin with:

- `-` interval line
- OR repeat block header (`5x`, `Main Set 5x`)
- OR markdown/text formatting supported by Intervals.icu

---

# 2. INTERVAL STEP FORMAT

## Canonical Format

```text
- [optional cue text] [duration OR distance] [target] [optional cadence]
```

Examples:

```text
- Warmup 10m 60%
- 5m30s 60% 90rpm
- 1km 70% HR
- 500mtr 5:00/km Pace
- 12m 85% 90-100rpm
```

---

# 3. DURATION & DISTANCE RULES

## TIME

Valid:

```text
1h
10m
30s
5m30s
1h2m30s
5'
30"
1'30"
```

## DISTANCE

Metric:

```text
500mtr
2km
10km
```

Imperial:

```text
1mi
4.5mi
```

IMPORTANT:

- `m` = minutes
- `mtr` = meters

---

# 4. TARGETS / INTENSITY MODELS

Each interval MUST use EXACTLY ONE intensity anchor.

NO mixed anchors.

---

## A. POWER (cycling default)

### Valid

```text
75%
95-105%
220w
200-240w
Z2
Z3-Z4
60% MMP 5m
50-60% MMP 3m
CZ1
CZ2-CZ3
```

### Examples

```text
- 10m ramp 60%-85%
- 4m 115%
- 4m 55%
- 20m 220w
- 15m Z2
```

---

## B. HEART RATE

### Valid

```text
70% HR
75-80% HR
95% LTHR
90-95% LTHR
Z2 HR
Z2-Z3 HR
70% HRmax
```

### STRICT RULES

- `HR`
- `LTHR`
- `HRmax`
- `Z2 HR`

are DISTINCT anchors.

Model MUST NOT convert between them.

---

## C. PACE (running/swimming)

### Valid

```text
60% Pace
78-82% Pace
Z2 Pace
Z2-Z3 Pace
5:00 Pace
5:00/km Pace
3:00/100m Pace
3:00/100m-4:00/100m Pace
```

### Pace Units

Common units:

```text
/km
/mi
/100m
/500m
/400m
/250m
```

If omitted:
- Intervals.icu uses sport default pace unit

---

# 5. CADENCE SUPPORT

Cadence MAY appear after target.

## Valid

```text
- 10m 75% 90rpm
- 12m 85% 90-100rpm
- 15m ramp 60%-90% 85rpm
```

---

# 6. RAMP RULES

Use `ramp` for gradual transitions.

Case insensitive.

## Valid

```text
- 10m ramp 50%-75%
- 15m ramp 60%-90% 85rpm
- 10m ramp 60-80% Pace
```

## STRICT RULES

- Ramps MUST include duration
- Ramp target MUST use ONE anchor only
- Ramp MUST remain on ONE interval line

---

# 7. FREERIDE SUPPORT

ERG disabled:

```text
- 20m freeride
```

---

# 8. REPEATS

## Supported

### Header repeat

```text
Main Set 4x
- 2m 95%
- 2m 55%
```

### Standalone repeat

```text
5x
- 30s 120%
- 30s 50%
```

## STRICT RULES

- Leave ONE blank line before and after repeat blocks
- Nested repeats are NOT supported

---

# 9. STEP CUES / PROMPTS

Any text BEFORE duration becomes cue text.

## Example

```text
- Warmup 10m 60%
- Recovery 3m 50%
```

Cue rendered:
- Warmup
- Recovery

---

# 10. TIMED TEXT PROMPTS

## Syntax

```text
- [prompt] 33^prompt <!> 10m ramp 25-75%
```

## Example

```text
- Start easy 33^Increase cadence 120^Stand up <!> 10m ramp 25-75%
```

## RULES

- Prompt times are seconds from step start
- `<!>` is REQUIRED when timed prompts are used

---

# 11. TEXT FORMATTING SUPPORT

Intervals.icu allows markdown formatting.

Supported:

## Titles

```md
# H1
### H3
###### H6
```

## Bold / Italic

```md
**bold**
*italic*
***bold italic***
```

## Links

```md
[link](https://example.com)
```

## Tables

```md
| Item | Value |
|------|------|
| A | 123 |
```

## Separators

```md
---
```

## Vuetify Classes

```html
<p class="text-red">Red text</p>
<span class="d-none">Hidden text</span>
```

---

# 12. STRICT INTENSITY ENFORCEMENT

## HARD RULES

Each interval MUST contain:

- ONE duration or distance
- ONE intensity anchor
- OPTIONAL cadence
- OPTIONAL plain-text cue

NOTHING ELSE.

---

# 13. FORBIDDEN MIXED METRICS

## INVALID

```text
- 10m 70% HRmax 200w
- 5m 85% FTP 160bpm
- 10m 4:30/km Pace 85% HRmax
```

---

# 14. RUN DEFAULT RULES

If `type = Run`:

- Prefer numeric Pace
- Pace SHOULD include `Pace`
- MUST NOT use FTP unless explicitly requested
- HR allowed ONLY if explicitly requested

---

# 15. HR DEFAULT LOGIC

If user says:

- “HR based”
- “heart rate”

WITHOUT specifying model:

THEN:

- endurance → `Z2 HR`
- steady → `% HR`
- threshold → `% LTHR`

DO NOT default to `HRmax`.

---

# 16. OPTIONAL CUE TEXT

Cue text MAY appear before duration.

Examples:

```text
- Warmup 10m 60%
- Recovery 5m 50%
- Tempo 20m 85%
```

Cue text:
- MUST be plain text
- MAY contain spaces
- MUST NOT contain additional metrics

---

# 17. DURATION INTEGRITY

- Total duration MUST equal sum of intervals
- No implied durations
- No inferred recovery

---

# 18. OFF / REST DAYS

OFF days MUST be written EXACTLY as:

```text
- OFF
```

---

# 19. CALENDAR EVENT CLASSIFICATION

Infer `category` and `type` deterministically from title/description.

Case-insensitive.

---

## RACE

```text
"A race"
"priority"
"main event"
```

→ `RACE_A`

```text
"B race"
```

→ `RACE_B`

```text
"C race"
```

→ `RACE_C`

Generic:

```text
race
event
competition
gran fondo
marathon
triathlon
```

Resolution:
- run → `RACE_A / Run`
- swim → `RACE_A / Swim`
- else → `RACE_A / Ride`

---

## WORKOUT — RUN

Keywords:

```text
run
jog
trail
track
```

Resolution:
- trail → `WORKOUT / TrailRun`
- else → `WORKOUT / Run`

---

## WORKOUT — CYCLING

Keywords:

```text
ride
bike
zwift
trainer
```

Resolution:
- virtual → `WORKOUT / VirtualRide`
- mountain → `WORKOUT / MountainBikeRide`
- gravel → `WORKOUT / GravelRide`
- else → `WORKOUT / Ride`

---

## WORKOUT — SWIM

Keywords:

```text
swim
laps
pool
open water
```

Resolution:
- open → `WORKOUT / OpenWaterSwim`
- else → `WORKOUT / Swim`

---

## STRENGTH / MOBILITY

```text
weight
gym
strength
lifting
squat
deadlift
```

→ `WORKOUT / WeightTraining`

```text
core
mobility
yoga
stretch
pilates
rehab
```

→ `WORKOUT / Yoga`

---

## OTHER

```text
hike
walk
```

→ `WORKOUT / Hike`

```text
rest
recovery
off
easy
```

→ `NOTE / Other`

```text
holiday
vacation
travel
```

→ `HOLIDAY / Other`

```text
sick
ill
flu
```

→ `SICK / Other`

```text
injury
rehab
```

→ `INJURED / Other`

```text
ftp test
max hr
fitness test
```

→ `SET_EFTP / Ride`

```text
plan
schedule
block
```

→ `PLAN / Other`

Fallback:

```text
NOTE / Other
```

---

# 20. CALENDAR METADATA (REQUIRED)

Each planned event MUST include:

- Date
- Title
- Type
- Category
- Intended duration
- Description
- Optional TSS
- carbs_per_hour

---

# 21. CARB FUELING LOGIC

## Formula

```text
load_per_hour = TSS / (duration_minutes / 60)
```

## Duration Bands

```text
A = <90
B = 90–150
C = >150
```

## Intensity Bands

```text
0 = <40
1 = 40–65
2 = 65–85
3 = >85
```

## Lookup

| Int\Dur | A | B | C |
|---|---|---|---|
| 0 | 35 | 45 | 55 |
| 1 | 55 | 67 | 77 |
| 2 | 67 | 82 | 87 |
| 3 | 80 | 92 | 100 |

Rules:
- Clamp 30–110 g/h
- Exclude NOTE/HOLIDAY/SICK/INJURED

---
# 22. CALENDAR UPDATE / DELETE RULES

# A. MOVE / UPDATE EXISTING EVENT

Move, reschedule, rename, retime, edit, change, update, or modify an existing event is ALWAYS an UPDATE.

Workflow:

```text
READ CALENDAR → FIND EXACT EVENT → UPDATE BY ID
```

Rules:
- If exactly one matching event is found and it has an ID, MUST update by ID.
- MUST call calendar write/update with the existing event ID.
- MUST NOT call delete for move/update/edit/rename/retime/change/modify.
- MUST NOT delete and recreate.
- MUST NOT use replacement workflow.
- MUST preserve all existing fields unless explicitly changed.
- If update by ID fails: ABORT.
- DO NOT create a fallback event.

---

# B. REPLACE EXISTING EVENT WITHOUT ID

Only use this when the user explicitly says replace/swap and no event ID is available after reading calendar.

```text
MATCH → DELETE → VERIFY DELETE → CREATE
```

Rules:
- Match by same date + same sport/type + strong title similarity.
- If no safe match exists: ABORT.
- If delete fails: ABORT.
- DO NOT create replacement.
- NO fallback creation.
- NO duplicates.

---

# C. ADD MODE

If user says:

```text
add
create
schedule
another
keep existing
```

THEN:
- CREATE only.
- DO NOT delete existing events.
- DO NOT replace existing events.

---

# D. DELETE SPECIFIC EVENT

Delete ONLY when the user explicitly asks to delete/remove/cancel an event.

Delete ONLY matching events.

NEVER delete entire day unless explicitly requested.

---

# E. DELETE ALL EVENTS

ONLY if user explicitly says:

```text
clear day
delete all
remove everything
wipe
```

---

# F. SAFETY RULE

NEVER perform date-only deletion unless explicitly requested.

If ambiguous:
- delete ONLY matching events.

NEVER perform date-only deletion unless explicitly requested.

If ambiguous:
- delete ONLY matching events

---

# 23. FORWARD PLANNING CONTEXT

For future planning:

- historical phases
- semantic reports
- load context
- fatigue state
- target events

MUST be considered before generating recommendations.

# 24. WORKOUT LIBRARY

This section defines canonical workout templates for Montis calendar writing.

Selection rules:

- Prefer these library workouts before generating custom sessions.
- Lock sport before selecting workout.
- Use `Type` exactly as written unless user explicitly requests another sport.
- Use only the interval text inside the workout description when writing to calendar.
- Do not pass estimated TSS. Intervals.icu calculates load from the workout prescription.
- Do not mix intensity anchors inside a single interval.
- Do not infer missing recovery.
- Total duration must equal the sum of listed intervals.

Phase use:

| Phase | Prefer |
|---|---|
| Recovery | REC, END easy, NEURO light, OFF |
| Base | END, TOR, TEM |
| Build | TEM, SS, THR |
| Specialty | THR, UO, VO2, RACE-specific |
| Peak | OPEN, RACE-specific, short THR/VO2 maintenance |
| Transition | REC, END easy, OFF |

---

# A. RIDE WORKOUTS

---

## RIDE-REC-001 Recovery Spin

Type: Ride
Duration: 45m

```text
- Easy spin 45m 50%
```

---

## RIDE-REC-002 Recovery With Cadence

Type: Ride
Duration: 60m

```text
- Easy spin 20m 50% 85rpm
- Cadence focus 20m 55% 95-105rpm
- Easy spin 20m 50% 85rpm
```

---

## RIDE-END-001 Aerobic Foundation

Type: Ride
Duration: 60m

```text
- Warmup 10m 55%
- Endurance 40m 65%
- Cooldown 10m 50%
```

---

## RIDE-END-002 Endurance Builder

Type: Ride
Duration: 90m

```text
- Warmup 15m 55%
- Endurance 30m 65%
- Endurance 30m 70%
- Cooldown 15m 50%
```

---

## RIDE-END-003 Progressive Endurance

Type: Ride
Duration: 90m

```text
- Warmup 15m 55%
- Endurance 20m 65%
- Endurance 20m 70%
- Endurance 20m 75%
- Cooldown 15m 50%
```

---

## RIDE-END-004 Long Endurance

Type: Ride
Duration: 120m

```text
- Warmup 15m 55%
- Endurance 90m 65-72%
- Cooldown 15m 50%
```

---

## RIDE-END-005 Long Aerobic Durability

Type: Ride
Duration: 180m

```text
- Warmup 20m 55%
- Endurance 130m 65-72%
- Steady finish 20m 75%
- Cooldown 10m 50%
```

---

## RIDE-END-006 Endurance With Tempo Finish

Type: Ride
Duration: 120m

```text
- Warmup 15m 55%
- Endurance 70m 65%
- Tempo finish 25m 80%
- Cooldown 10m 50%
```

---

## RIDE-END-007 Aerobic Cadence Control

Type: Ride
Duration: 75m

```text
- Warmup 10m 55% 85rpm
- Endurance 20m 65% 90rpm
- Cadence focus 20m 65% 95-105rpm
- Endurance 15m 70% 90rpm
- Cooldown 10m 50%
```

---

## RIDE-TOR-001 Low Cadence Endurance

Type: Ride
Duration: 75m

```text
- Warmup 15m 55%

Main Set 5x
- Torque 6m 80% 60rpm
- Recovery 3m 55%

- Cooldown 15m 50%
```

---

## RIDE-TOR-002 Big Gear Tempo

Type: Ride
Duration: 90m

```text
- Warmup 15m 55%

Main Set 3x
- Big gear 12m 82% 60rpm
- Recovery 5m 55%

- Endurance 9m 65%
- Cooldown 15m 50%
```

---

## RIDE-TOR-003 Strength Endurance

Type: Ride
Duration: 90m

```text
- Warmup 15m 55%

Main Set 4x
- Strength endurance 8m 85% 60rpm
- Recovery 4m 55%

- Endurance 12m 65%
- Cooldown 15m 50%
```

---

## RIDE-TEM-001 Tempo Intro

Type: Ride
Duration: 75m

```text
- Warmup 15m 55%

Main Set 2x
- Tempo 15m 82%
- Recovery 5m 55%

- Endurance 10m 65%
- Cooldown 10m 50%
```

---

## RIDE-TEM-002 Tempo Builder

Type: Ride
Duration: 90m

```text
- Warmup 15m 55%

Main Set 3x
- Tempo 15m 83%
- Recovery 5m 55%

- Cooldown 15m 50%
```

---

## RIDE-TEM-003 Long Tempo

Type: Ride
Duration: 120m

```text
- Warmup 15m 55%

Main Set 2x
- Tempo 35m 82-85%
- Recovery 10m 55%

- Cooldown 15m 50%
```

---

## RIDE-TEM-004 Continuous Tempo

Type: Ride
Duration: 90m

```text
- Warmup 15m 55%
- Tempo 60m 82%
- Cooldown 15m 50%
```

---

## RIDE-TEM-005 Tempo Progression

Type: Ride
Duration: 105m

```text
- Warmup 15m 55%
- Tempo 20m 80%
- Tempo 20m 83%
- Tempo 20m 86%
- Endurance 15m 65%
- Cooldown 15m 50%
```

---

## RIDE-SS-001 Sweet Spot Intro

Type: Ride
Duration: 75m

```text
- Warmup 15m 55%

Main Set 3x
- Sweet spot 10m 88-92%
- Recovery 4m 55%

- Endurance 8m 65%
- Cooldown 10m 50%
```

---

## RIDE-SS-002 Sweet Spot Standard

Type: Ride
Duration: 90m

```text
- Warmup 15m 55%

Main Set 3x
- Sweet spot 15m 88-92%
- Recovery 5m 55%

- Cooldown 15m 50%
```

---

## RIDE-SS-003 Sweet Spot Progression

Type: Ride
Duration: 105m

```text
- Warmup 15m 55%

Main Set 3x
- Sweet spot 18m 88-92%
- Recovery 5m 55%

- Endurance 6m 65%
- Cooldown 15m 50%
```

---

## RIDE-SS-004 Sweet Spot Long

Type: Ride
Duration: 100m

```text
- Warmup 10m 55%

Main Set 2x
- Sweet spot 25m 90%
- Recovery 8m 55%

- Endurance 14m 65%
- Cooldown 10m 50%
```

---

## RIDE-SS-005 Sweet Spot Continuous

Type: Ride
Duration: 90m

```text
- Warmup 15m 55%
- Sweet spot 45m 88-92%
- Endurance 15m 65%
- Cooldown 15m 50%
```

---

## RIDE-SS-006 Sweet Spot Pyramid

Type: Ride
Duration: 95m

```text
- Warmup 15m 55%
- Sweet spot 10m 88%
- Sweet spot 15m 90%
- Sweet spot 20m 92%
- Sweet spot 15m 90%
- Sweet spot 10m 88%
- Cooldown 10m 50%
```

---

## RIDE-THR-001 Threshold Intro

Type: Ride
Duration: 75m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-85%
- Recovery 5m 55%

Main Set 3x
- Threshold 8m 98-102%
- Recovery 4m 55%

- Cooldown 14m 50%
```

---

## RIDE-THR-002 Threshold Builder

Type: Ride
Duration: 90m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 4x
- Threshold 8m 100%
- Recovery 4m 55%

- Endurance 10m 65%
- Cooldown 7m 50%
```

---

## RIDE-THR-003 Threshold Progression

Type: Ride
Duration: 95m

```text
- Warmup 10m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 2x
- Threshold 20m 98-100%
- Recovery 8m 55%

- Endurance 14m 65%
- Cooldown 5m 50%
```

---

## RIDE-THR-004 Threshold TTE

Type: Ride
Duration: 105m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 3x
- Threshold 15m 95-100%
- Recovery 5m 55%

- Endurance 15m 65%
- Cooldown 5m 50%
```

---

## RIDE-THR-005 Long Threshold

Type: Ride
Duration: 90m

```text
- Warmup 20m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%
- Threshold 35m 95-100%
- Endurance 15m 65%
- Cooldown 10m 50%
```

---

## RIDE-UO-001 Under Over Intro

Type: Ride
Duration: 75m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 4x
- Under 3m 90%
- Over 1m 110%
- Recovery 3m 55%

- Endurance 12m 65%
- Cooldown 10m 50%
```

---

## RIDE-UO-002 Under Over Standard

Type: Ride
Duration: 90m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 5x
- Under 4m 92%
- Over 1m 110%
- Recovery 3m 55%

- Endurance 10m 65%
- Cooldown 15m 50%
```

---

## RIDE-UO-003 Lactate Clearance

Type: Ride
Duration: 95m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 4x
- Over 1m 115%
- Under 4m 92%
- Recovery 4m 55%

- Endurance 24m 65%
- Cooldown 10m 50%
```

---

## RIDE-UO-004 Race Under Overs

Type: Ride
Duration: 100m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 3x
- Under 6m 92%
- Over 2m 108%
- Recovery 5m 55%

- Endurance 26m 65%
- Cooldown 10m 50%
```

---

## RIDE-VO2-001 VO2 Intro

Type: Ride
Duration: 60m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 5x
- VO2 2m 115%
- Recovery 3m 55%

- Cooldown 10m 50%
```

---

## RIDE-VO2-002 VO2 Standard

Type: Ride
Duration: 75m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 5x
- VO2 3m 115%
- Recovery 3m 55%

- Endurance 10m 65%
- Cooldown 10m 50%
```

---

## RIDE-VO2-003 Five By Five

Type: Ride
Duration: 85m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 5x
- VO2 5m 110-115%
- Recovery 5m 55%

- Cooldown 10m 50%
```

---

## RIDE-VO2-004 Long VO2

Type: Ride
Duration: 90m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 4x
- VO2 6m 106-110%
- Recovery 4m 55%

- Endurance 15m 65%
- Cooldown 10m 50%
```

---

## RIDE-VO2-005 Microbursts

Type: Ride
Duration: 75m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 15x
- Hard 30s 125%
- Easy 30s 50%

- Recovery 10m 55%

Main Set 10x
- Hard 30s 125%
- Easy 30s 50%

- Cooldown 15m 50%
```

---

## RIDE-VO2-009 Forty Twenty VO2

Type: Ride
Duration: 70m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 12x
- Hard 40s 120%
- Easy 20s 50%

- Recovery 8m 55%

Main Set 8x
- Hard 40s 120%
- Easy 20s 50%

- Cooldown 12m 50%
```

---

## RIDE-VO2-010 Forty Forty VO2

Type: Ride
Duration: 75m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 10x
- Hard 40s 120%
- Easy 40s 50%

- Recovery 8m 55%

Main Set 8x
- Hard 40s 120%
- Easy 40s 50%

- Cooldown 7m 50%
```
---

## RIDE-NEURO-001 Sprint Recruitment

Type: Ride
Duration: 60m

```text
- Warmup 20m 55%

Main Set 8x
- Sprint 10s 150%
- Recovery 3m 50%

- Endurance 7m 65%
- Cooldown 7m40s 50%
```

---

## RIDE-NEURO-002 Standing Starts

Type: Ride
Duration: 60m

```text
- Warmup 20m 55%

Main Set 8x
- Standing start 15s 140%
- Recovery 3m 50%

- Endurance 6m 65%
- Cooldown 8m 50%
```

---

## RIDE-NEURO-003 High Cadence Primers

Type: Ride
Duration: 50m

```text
- Warmup 15m 55%

Main Set 6x
- High cadence 20s 90% 115-125rpm
- Recovery 2m 50%

- Endurance 12m 65%
- Cooldown 9m 50%
```

---

## RIDE-OPEN-001 Race Openers

Type: Ride
Duration: 60m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-85%
- Recovery 5m 55%

Main Set 3x
- Opener 1m 120%
- Recovery 4m 55%

Main Set 3x
- Sprint 10s 150%
- Recovery 3m 50%

- Cooldown 10m30s 50%
```

---

## RIDE-OPEN-002 Activation Ride

Type: Ride
Duration: 45m

```text
- Warmup 10m 55%
- Endurance 20m 65%

Main Set 4x
- Activation 30s 120%
- Recovery 2m 55%

- Cooldown 5m 50%
```

---

## RIDE-RACE-TT-001 TT Specific

Type: Ride
Duration: 75m

```text
- Warmup 12m 55%
- Prep 4m ramp 60%-90%
- Recovery 4m 55%

Main Set 2x
- TT effort 12m 95-100%
- Recovery 6m 55%

- Endurance 9m 65%
- Cooldown 10m 50%
```

---

## RIDE-RACE-FONDO-001 Fondo Durability

Type: Ride
Duration: 240m

```text
- Warmup 20m 55%
- Endurance 160m 65-72%
- Tempo finish 45m 80%
- Cooldown 15m 50%
```

---

## RIDE-RACE-CRIT-001 Crit Repeatability

Type: Ride
Duration: 75m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 12x
- Surge 30s 140%
- Recovery 90s 60%

- Endurance 16m 65%
- Cooldown 10m 50%
```

---

## RIDE-END-008 Long Endurance Plus

Type: Ride
Duration: 150m

```text
- Warmup 20m 55%
- Endurance 110m 65-72%
- Steady finish 10m 75%
- Cooldown 10m 50%
```

---

## RIDE-END-009 Endurance With Tempo Inserts

Type: Ride
Duration: 105m

```text
- Warmup 15m 55%
- Endurance 25m 65%
- Tempo 5m 82%
- Endurance 25m 65%
- Tempo 5m 82%
- Endurance 20m 65%
- Cooldown 10m 50%
```

---

## RIDE-END-010 Fondo Base Ride

Type: Ride
Duration: 210m

```text
- Warmup 20m 55%
- Endurance 150m 65-72%
- Tempo finish 30m 80%
- Cooldown 10m 50%
```

---

## RIDE-TOR-004 Torque Builder

Type: Ride
Duration: 75m

```text
- Warmup 15m 55%

Main Set 4x
- Torque 8m 80% 60rpm
- Recovery 4m 55%

- Cooldown 12m 50%
```

---

## RIDE-TOR-005 Long Torque Tempo

Type: Ride
Duration: 100m

```text
- Warmup 15m 55%

Main Set 3x
- Big gear tempo 15m 82% 60rpm
- Recovery 5m 55%

- Endurance 15m 65%
- Cooldown 10m 50%
```

---

## RIDE-TEM-006 Tempo Overload

Type: Ride
Duration: 100m

```text
- Warmup 15m 55%

Main Set 4x
- Tempo 12m 85%
- Recovery 4m 55%

- Endurance 11m 65%
- Cooldown 10m 50%
```

---

## RIDE-TEM-007 Tempo Durability

Type: Ride
Duration: 135m

```text
- Warmup 20m 55%
- Endurance 45m 65%
- Tempo 45m 82-85%
- Endurance 15m 65%
- Cooldown 10m 50%
```

---

## RIDE-SS-007 Sweet Spot Overload

Type: Ride
Duration: 120m

```text
- Warmup 20m 55%

Main Set 4x
- Sweet spot 15m 88-92%
- Recovery 4m 55%

- Endurance 14m 65%
- Cooldown 10m 50%
```

---

## RIDE-SS-008 Sweet Spot Fatigue Resistance

Type: Ride
Duration: 135m

```text
- Warmup 15m 55%
- Endurance 40m 65%

Main Set 2x
- Sweet spot 25m 88-92%
- Recovery 8m 55%

- Endurance 9m 65%
- Cooldown 5m 50%
```

---

## RIDE-SS-009 Sweet Spot With Surges

Type: Ride
Duration: 95m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-85%
- Recovery 5m 55%

Main Set 4x
- Sweet spot 8m 90%
- Surge 1m 105%
- Recovery 4m 55%

- Cooldown 18m 50%
```

---

## RIDE-THR-006 Threshold Overload

Type: Ride
Duration: 100m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 5x
- Threshold 7m 100-105%
- Recovery 4m 55%

- Endurance 15m 65%
- Cooldown 5m 50%
```

---

## RIDE-THR-007 Threshold Fatigue Resistance

Type: Ride
Duration: 120m

```text
- Warmup 15m 55%
- Endurance 30m 65%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 2x
- Threshold 18m 95-100%
- Recovery 7m 55%

- Endurance 5m 65%
- Cooldown 10m 50%
```

---

## RIDE-THR-008 Threshold Maintenance

Type: Ride
Duration: 70m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 3x
- Threshold 6m 100%
- Recovery 4m 55%

- Endurance 5m 65%
- Cooldown 10m 50%
```

---

## RIDE-UO-005 Over Under Threshold

Type: Ride
Duration: 95m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 3x
- Over 2m 110%
- Under 6m 92%
- Recovery 5m 55%

- Endurance 20m 65%
- Cooldown 11m 50%
```

---

## RIDE-UO-006 Progressive Under Overs

Type: Ride
Duration: 105m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 4x
- Under 5m 92%
- Over 2m 108%
- Recovery 4m 55%

- Endurance 24m 65%
- Cooldown 12m 50%
```

---

## RIDE-VO2-006 VO2 Repeatability

Type: Ride
Duration: 80m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 6x
- VO2 3m 115%
- Recovery 3m 55%

- Endurance 13m 65%
- Cooldown 6m 50%
```

---

## RIDE-VO2-007 VO2 Aerobic Power

Type: Ride
Duration: 95m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 5x
- VO2 4m 112%
- Recovery 4m 55%

- Endurance 20m 65%
- Cooldown 10m 50%
```

---

## RIDE-VO2-008 Short VO2 Microbursts

Type: Ride
Duration: 60m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%

Main Set 20x
- Hard 20s 130%
- Easy 40s 50%

- Endurance 5m 65%
- Cooldown 10m 50%
```

---

## RIDE-NEURO-004 Sprint Endurance

Type: Ride
Duration: 75m

```text
- Warmup 20m 55%

Main Set 10x
- Sprint 12s 150%
- Recovery 3m 50%

- Endurance 15m 65%
- Cooldown 8m 50%
```

---

## RIDE-RACE-TT-002 TT Overload

Type: Ride
Duration: 95m

```text
- Warmup 15m 55%
- Prep 5m ramp 60%-90%
- Recovery 5m 55%
- TT effort 25m 95-100%
- Recovery 8m 55%
- TT effort 20m 95-100%
- Endurance 7m 65%
- Cooldown 10m 50%
```


---

# B. RUN WORKOUTS

---

## RUN-REC-001 Easy Recovery Run

Type: Run
Duration: 30m

```text
- Easy run 30m Z1 Pace
```

---

## RUN-REC-002 Recovery Jog

Type: Run
Duration: 40m

```text
- Easy jog 35m Z1 Pace
- Walk 5m Z1 Pace
```

---

## RUN-END-001 Easy Aerobic Run

Type: Run
Duration: 45m

```text
- Easy run 45m Z2 Pace
```

---

## RUN-END-002 Aerobic Base Run

Type: Run
Duration: 60m

```text
- Warmup 10m Z1 Pace
- Endurance 40m Z2 Pace
- Cooldown 10m Z1 Pace
```

---

## RUN-END-003 Long Aerobic Run

Type: Run
Duration: 90m

```text
- Warmup 10m Z1 Pace
- Endurance 70m Z2 Pace
- Cooldown 10m Z1 Pace
```

---

## RUN-END-004 Progressive Endurance Run

Type: Run
Duration: 75m

```text
- Warmup 10m Z1 Pace
- Endurance 25m Z2 Pace
- Steady 25m Z2-Z3 Pace
- Cooldown 15m Z1 Pace
```

---

## RUN-TEM-001 Tempo Intro

Type: Run
Duration: 50m

```text
- Warmup 15m Z1 Pace
- Tempo 15m Z3 Pace
- Easy jog 10m Z1 Pace
- Cooldown 10m Z1 Pace
```

---

## RUN-TEM-002 Tempo Builder

Type: Run
Duration: 60m

```text
- Warmup 15m Z1 Pace

Main Set 2x
- Tempo 12m Z3 Pace
- Easy jog 4m Z1 Pace

- Cooldown 13m Z1 Pace
```

---

## RUN-TEM-003 Long Tempo

Type: Run
Duration: 70m

```text
- Warmup 15m Z1 Pace
- Tempo 30m Z3 Pace
- Easy jog 10m Z1 Pace
- Cooldown 15m Z1 Pace
```

---

## RUN-THR-001 Cruise Intervals

Type: Run
Duration: 60m

```text
- Warmup 15m Z1 Pace

Main Set 4x
- Threshold 6m Z4 Pace
- Easy jog 2m Z1 Pace

- Cooldown 13m Z1 Pace
```

---

## RUN-THR-002 Threshold Builder

Type: Run
Duration: 70m

```text
- Warmup 15m Z1 Pace

Main Set 3x
- Threshold 10m Z4 Pace
- Easy jog 3m Z1 Pace

- Cooldown 16m Z1 Pace
```

---

## RUN-THR-003 Threshold Progression

Type: Run
Duration: 75m

```text
- Warmup 15m Z1 Pace
- Steady 10m Z2-Z3 Pace

Main Set 3x
- Threshold 8m Z4 Pace
- Easy jog 3m Z1 Pace

- Cooldown 17m Z1 Pace
```

---

## RUN-HILL-001 Hill Strength

Type: Run
Duration: 55m

```text
- Warmup 15m Z1 Pace

Main Set 8x
- Hill repeat 45s Z5 Pace
- Easy jog 2m Z1 Pace

- Endurance 12m Z2 Pace
- Cooldown 6m Z1 Pace
```

---

## RUN-HILL-002 Hill Threshold

Type: Run
Duration: 65m

```text
- Warmup 15m Z1 Pace

Main Set 6x
- Hill threshold 3m Z4 Pace
- Easy jog 2m Z1 Pace

- Endurance 12m Z2 Pace
- Cooldown 8m Z1 Pace
```

---

## RUN-VO2-001 VO2 Intro

Type: Run
Duration: 50m

```text
- Warmup 15m Z1 Pace

Main Set 6x
- VO2 2m Z5 Pace
- Easy jog 2m Z1 Pace

- Cooldown 11m Z1 Pace
```

---

## RUN-VO2-002 VO2 Standard

Type: Run
Duration: 60m

```text
- Warmup 15m Z1 Pace

Main Set 5x
- VO2 3m Z5 Pace
- Easy jog 3m Z1 Pace

- Cooldown 15m Z1 Pace
```

---

## RUN-VO2-003 Long VO2

Type: Run
Duration: 70m

```text
- Warmup 15m Z1 Pace

Main Set 5x
- VO2 4m Z5 Pace
- Easy jog 3m Z1 Pace

- Endurance 10m Z2 Pace
- Cooldown 10m Z1 Pace
```

---

## RUN-SPEED-001 Strides

Type: Run
Duration: 45m

```text
- Warmup 15m Z1 Pace

Main Set 8x
- Stride 20s Z5 Pace
- Easy jog 1m40s Z1 Pace

- Endurance 10m Z2 Pace
- Cooldown 4m Z1 Pace
```

---

## RUN-SPEED-002 Neuromuscular Speed

Type: Run
Duration: 50m

```text
- Warmup 15m Z1 Pace

Main Set 10x
- Fast stride 15s Z5 Pace
- Easy jog 1m45s Z1 Pace

- Endurance 10m Z2 Pace
- Cooldown 5m Z1 Pace
```

---

## RUN-OPEN-001 Run Openers

Type: Run
Duration: 40m

```text
- Warmup 15m Z1 Pace

Main Set 4x
- Opener 30s Z5 Pace
- Easy jog 2m30s Z1 Pace

- Endurance 5m Z2 Pace
- Cooldown 8m Z1 Pace
```

---

## RUN-RACE-5K-001 5K Specific

Type: Run
Duration: 60m

```text
- Warmup 15m Z1 Pace

Main Set 5x
- Race pace 3m Z5 Pace
- Easy jog 2m Z1 Pace

- Endurance 10m Z2 Pace
- Cooldown 10m Z1 Pace
```

---

## RUN-RACE-10K-001 10K Specific

Type: Run
Duration: 70m

```text
- Warmup 15m Z1 Pace

Main Set 4x
- Race pace 5m Z4-Z5 Pace
- Easy jog 3m Z1 Pace

- Endurance 13m Z2 Pace
- Cooldown 10m Z1 Pace
```

---

## RUN-RACE-HALF-001 Half Marathon Specific

Type: Run
Duration: 85m

```text
- Warmup 15m Z1 Pace

Main Set 3x
- Race pace 12m Z3-Z4 Pace
- Easy jog 4m Z1 Pace

- Endurance 12m Z2 Pace
- Cooldown 10m Z1 Pace
```

---

## RUN-RACE-MAR-001 Marathon Specific

Type: Run
Duration: 110m

```text
- Warmup 15m Z1 Pace
- Endurance 35m Z2 Pace
- Marathon effort 40m Z3 Pace
- Endurance 10m Z2 Pace
- Cooldown 10m Z1 Pace
```

---

## RUN-END-005 Long Run

Type: Run
Duration: 105m

```text
- Warmup 10m Z1 Pace
- Endurance 85m Z2 Pace
- Cooldown 10m Z1 Pace
```

---

## RUN-END-006 Long Run With Steady Finish

Type: Run
Duration: 100m

```text
- Warmup 10m Z1 Pace
- Endurance 65m Z2 Pace
- Steady finish 15m Z2-Z3 Pace
- Cooldown 10m Z1 Pace
```

---

## RUN-TEM-004 Tempo Intervals

Type: Run
Duration: 65m

```text
- Warmup 15m Z1 Pace

Main Set 3x
- Tempo 10m Z3 Pace
- Easy jog 3m Z1 Pace

- Cooldown 11m Z1 Pace
```

---

## RUN-TEM-005 Continuous Tempo

Type: Run
Duration: 60m

```text
- Warmup 15m Z1 Pace
- Tempo 25m Z3 Pace
- Easy jog 10m Z1 Pace
- Cooldown 10m Z1 Pace
```

---

## RUN-THR-004 Threshold Maintenance

Type: Run
Duration: 55m

```text
- Warmup 15m Z1 Pace

Main Set 3x
- Threshold 5m Z4 Pace
- Easy jog 2m Z1 Pace

- Endurance 9m Z2 Pace
- Cooldown 10m Z1 Pace
```

---

## RUN-THR-005 Threshold Extension

Type: Run
Duration: 80m

```text
- Warmup 15m Z1 Pace

Main Set 2x
- Threshold 15m Z4 Pace
- Easy jog 5m Z1 Pace

- Endurance 15m Z2 Pace
- Cooldown 10m Z1 Pace
```

---

## RUN-HILL-003 Hill Sprints

Type: Run
Duration: 45m

```text
- Warmup 15m Z1 Pace

Main Set 8x
- Hill sprint 20s Z5 Pace
- Easy jog 2m10s Z1 Pace

- Endurance 5m Z2 Pace
- Cooldown 5m Z1 Pace
```

---

## RUN-VO2-004 Short VO2

Type: Run
Duration: 55m

```text
- Warmup 15m Z1 Pace

Main Set 10x
- Fast 1m Z5 Pace
- Easy jog 1m Z1 Pace

- Endurance 10m Z2 Pace
- Cooldown 10m Z1 Pace
```

---

## RUN-SPEED-003 Speed Endurance

Type: Run
Duration: 60m

```text
- Warmup 15m Z1 Pace

Main Set 6x
- Fast 2m Z5 Pace
- Easy jog 3m Z1 Pace

- Endurance 5m Z2 Pace
- Cooldown 10m Z1 Pace
```

---

## RUN-RACE-HILL-001 Hilly Race Specific

Type: Run
Duration: 75m

```text
- Warmup 15m Z1 Pace

Main Set 5x
- Uphill effort 4m Z4 Pace
- Easy jog 3m Z1 Pace

- Endurance 15m Z2 Pace
- Cooldown 10m Z1 Pace
```


---

# C. REST / OFF

---

## OFF-001 Off Day

Type: Other
Duration: 0m

```text
- OFF
```

# 25. FRIEL-ALIGNED WORKOUT LIBRARY ADDENDUM

This addendum keeps the Friel-style physiological families while preserving strict Intervals.icu syntax:

- AE = aerobic endurance / aerobic threshold
- ME = muscular endurance / tempo / threshold / sweet spot
- AnE = anaerobic endurance / VO2 / race-like surges
- MF = muscular force / force reps / hill force
- NM = neuromuscular speed / cadence / jumps

Rules:

- Use `Type` exactly as written.
- Use only the interval text inside the workout description when writing to calendar.
- Do not pass estimated TSS.
- Do not mix intensity anchors inside a single interval.
- Do not infer missing recovery.
- Total duration must equal the sum of listed intervals.

---

# FRIEL AE — AEROBIC ENDURANCE

---

## FRIEL-AE-001 Recovery Ride HR

Type: Ride
Duration: 60m

```text
- Recovery 60m 65-80% LTHR
```

---

## FRIEL-AE-002 Aerobic Threshold Ride

Type: Ride
Duration: 120m

```text
- Warmup 15m 55%
- Aerobic threshold 90m 65-75%
- Cooldown 15m 50%
```

---

## FRIEL-AE-003 Intensive Endurance

Type: Ride
Duration: 95m

```text
- Warmup 15m 55%
- Intensive endurance 60m 76-90%
- Cooldown 20m 50%
```

---

## FRIEL-AE-004 Aerobic Pacing

Type: Ride
Duration: 120m

```text
- Warmup 13m ramp 50%-60% 70-100rpm
- Aerobic pacing 99m 56-75%
- Cooldown 8m 50% 70-100rpm
```

---

## FRIEL-AE-005 Aerobic Threshold HR

Type: Ride
Duration: 120m

```text
- Warmup 15m 60% LTHR 70-100rpm
- Aerobic threshold 90m 81-85% LTHR
- Cooldown 15m 60% HR 90-100rpm
```

---

# FRIEL ME — MUSCULAR ENDURANCE

---

## FRIEL-ME-001 Threshold Intervals

Type: Ride
Duration: 105m

```text
- Warmup 15m ramp 50%-75%

Main Set 5x
- Threshold 12m 91-105%
- Recovery 3m 55%

- Cooldown 15m 50%
```

---

## FRIEL-ME-002 Cruise Intervals

Type: Ride
Duration: 63m

```text
- Warmup 15m ramp 50%-75%

Main Set 5x
- Cruise 6m 95-100%
- Recovery 1m30s 55%

- Cooldown 10m30s 50%
```

---

## FRIEL-ME-003 Sweet Spot Intervals

Type: Ride
Duration: 85m

```text
- Warmup 15m ramp 50%-75%

Main Set 2x
- Sweet spot 20m 88-97%
- Recovery 5m 55%

- Cooldown 20m 50%
```

---

## FRIEL-ME-004 Tempo Zone 3 Intervals

Type: Ride
Duration: 105m

```text
- Warmup 10m 55%

Main Set 4x
- Tempo 15m 76-90%
- Recovery 5m 55%

- Cooldown 15m 50%
```

---

## FRIEL-ME-005 Sweet Spot Twenty Minute Repeats

Type: Ride
Duration: 85m

```text
- Warmup 15m 55%

Main Set 2x
- Sweet spot 20m 88-97%
- Recovery 5m 55%

- Cooldown 20m 50%
```

---

# FRIEL ANE — ANAEROBIC ENDURANCE / VO2

---

## FRIEL-ANE-001 Group Ride Simulation

Type: Ride
Duration: 120m

```text
- Warmup 20m 55%
- Endurance 20m 65%

Main Set 8x
- Race surge 1m 120%
- Recovery 4m 65%

- Endurance 30m 65-75%
- Cooldown 10m 50%
```

---

## FRIEL-ANE-002 VO2max Intervals

Type: Ride
Duration: 72m

```text
- Warmup 20m 55%

Main Set 8x
- VO2 2m 106-120%
- Recovery 2m 55%

- Cooldown 20m 50%
```

---

## FRIEL-ANE-003 Pyramid Intervals

Type: Ride
Duration: 80m

```text
- Warmup 20m ramp 50%-75%
- Hard 1m 106-120% 105rpm
- Recovery 1m 55% 105rpm
- Hard 2m 106-120% 105rpm
- Recovery 2m 55% 105rpm
- Hard 3m 106-120% 105rpm
- Recovery 3m 55% 105rpm
- Hard 4m 106-120% 105rpm
- Recovery 4m 55% 105rpm
- Hard 4m 106-120% 105rpm
- Recovery 4m 55% 105rpm
- Hard 3m 106-120% 105rpm
- Recovery 3m 55% 105rpm
- Hard 2m 106-120% 105rpm
- Recovery 2m 55% 105rpm
- Hard 1m 106-120% 105rpm
- Recovery 1m 55% 105rpm
- Cooldown 20m 50%
```

---

## FRIEL-ANE-004 Hill Intervals

Type: Ride
Duration: 55m

```text
- Warmup 20m ramp 50%-75%

Main Set 5x
- Hill interval 1m30s 106-120% 95-105rpm
- Recovery 1m30s 55%

- Cooldown 20m 50%
```

---

## FRIEL-ANE-005 VO2max Three Minute Repeats

Type: Ride
Duration: 80m

```text
- Warmup 20m 55%

Main Set 8x
- VO2 3m 106-120%
- Recovery 3m 55%

- Cooldown 12m 50%
```

---

# FRIEL MF — MUSCULAR FORCE

---

## FRIEL-MF-001 Flat Force Reps

Type: Ride
Duration: 45m

```text
- Warmup 15m 55%

Main Set 4x
- Force rep 5s 200% 50-70rpm
- Recovery 4m25s 50%

- Cooldown 12m 50%
```

---

## FRIEL-MF-002 Hill Force Reps

Type: Ride
Duration: 45m

```text
- Warmup 15m 55%

Main Set 3x
- Hill force 6s 200% 50-70rpm
- Recovery 5m24s 50%

- Cooldown 13m30s 50%
```

---

## FRIEL-MF-003 Hill Repeats 70rpm

Type: Ride
Duration: 60m

```text
- Warmup 15m 55%

Main Set 8x
- Hill repeat 25s 106-120% 70rpm
- Recovery 4m 50%

- Cooldown 9m40s 50%
```

---

## FRIEL-MF-004 Force Reps Three Sets

Type: Ride
Duration: 60m

```text
- Warmup 12m 55%

Set One 3x
- Force rep 30s 200% 50-70rpm
- Recovery 3m 50%

- Set recovery 3m 50%

Set Two 3x
- Force rep 30s 200% 50-70rpm
- Recovery 3m 50%

- Set recovery 3m 50%

Set Three 3x
- Force rep 30s 200% 50-70rpm
- Recovery 3m 50%

- Cooldown 10m30s 50%
```

---

# FRIEL NM — NEUROMUSCULAR SKILLS

---

## FRIEL-NM-001 High Cadence Drill

Type: Ride
Duration: 50m

```text
- Warmup 15m 55% 90rpm

Main Set 3x
- Spin up 10s 55% 90rpm
- High cadence 3m 55% 110-150rpm
- Recovery 5m 55% 90rpm

- Cooldown 10m30s 50%
```

---

## FRIEL-NM-002 Hill Sprints

Type: Ride
Duration: 45m

```text
- Warmup 20m 55%

Main Set 9x
- Hill sprint 7s 300%
- Recovery 1m53s 50%

- Cooldown 7m 50%
```

---

## FRIEL-NM-003 Jumps

Type: Ride
Duration: 45m

```text
- Warmup 15m 55%

Main Set 10x
- Jump 5s 150% 120rpm
- Recovery 1m25s 50%

- Endurance 10m 65%
- Cooldown 5m 50%
```

---

## FRIEL-NM-004 Cadence And Jump Skills

Type: Ride
Duration: 60m

```text
- Warmup 15m 55% 90rpm

Main Set 4x
- High cadence 2m 60% 110-120rpm
- Recovery 3m 55% 90rpm

Main Set 6x
- Jump 8s 150% 120rpm
- Recovery 1m52s 50%

- Endurance 8m 65%
- Cooldown 5m 50%
```

# 26. RUN WORKOUT LIBRARY ADDENDUM — NORWEGIAN SINGLES METHOD

This addendum adds strict Intervals.icu-safe run workouts based on Norwegian-style single-session subthreshold training.

Use cases:

- Threshold development without double-threshold loading
- Controlled subthreshold work
- Build and specialty phases
- Run-focused athletes with reliable pace zones
- Athletes needing lower-risk threshold exposure than maximal interval sessions

Selection rules:

- Prefer Pace-based versions for Run unless the user explicitly asks for HR-based workouts.
- Use HR-based aerobic runs only when the user asks for heart-rate based prescription.
- Do not mix HR and Pace anchors in one workout.
- Do not pass estimated TSS. Intervals.icu calculates load from the prescription.
- Total duration must equal the sum of listed intervals.

---

# NORWEGIAN SUBTHRESHOLD RUN WORKOUTS

---

## RUN-NOR-SUB-001 Subthreshold 2x10

Type: Run
Duration: 68m

```text
- Warmup 22m 60-70% Pace

Main Set 2x
- Subthreshold 10m 92-95% Pace
- Easy jog 2m 60-70% Pace

- Cooldown 22m 60-70% Pace
```

---

## RUN-NOR-SUB-002 Subthreshold 3x6

Type: Run
Duration: 65m

```text
- Warmup 22m 60-70% Pace

Main Set 3x
- Subthreshold 6m 94-97.5% Pace
- Easy jog 1m 60-70% Pace

- Cooldown 22m 60-70% Pace
```

---

## RUN-NOR-SUB-003 Subthreshold 4x5

Type: Run
Duration: 68m

```text
- Warmup 22m 60-70% Pace

Main Set 4x
- Subthreshold 5m 94-97.5% Pace
- Easy jog 1m 60-70% Pace

- Cooldown 22m 60-70% Pace
```

---

## RUN-NOR-SUB-004 Subthreshold 7x3

Type: Run
Duration: 72m

```text
- Warmup 22m 60-70% Pace

Main Set 7x
- Subthreshold 3m 96-100.5% Pace
- Easy jog 1m 60-70% Pace

- Cooldown 22m 60-70% Pace
```

---

# NORWEGIAN AEROBIC SUPPORT RUNS

---

## RUN-NOR-AE-001 Easy Run HR

Type: Run
Duration: 40m

```text
- Easy run 40m 60-70% HR
```

---

## RUN-NOR-AE-002 Easy Run Pace

Type: Run
Duration: 40m

```text
- Easy run 40m 74% Pace
```

---

## RUN-NOR-AE-003 Long Run HR

Type: Run
Duration: 90m

```text
- Long run 90m 60-70% HR
```

---

## RUN-NOR-AE-004 Long Run Pace

Type: Run
Duration: 90m

```text
- Long run 90m 74% Pace
```

