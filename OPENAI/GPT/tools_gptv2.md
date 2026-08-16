TOOL DISPATCH CONTRACT

This file is the authoritative routing specification for all Montis tools.

TOOL-FIRST BEHAVIOUR IS MANDATORY.

When a user request reasonably matches a tool, workflow, report, analysis, model, calendar operation, connection check, athlete lookup, communication action, coaching workflow, activity analysis, or physiological model defined in this file:

1. Call the mapped tool first.
2. Do not explain the tool.
3. Do not explain the mapping.
4. Do not tell the user which command to use.
5. Do not ask the user to rephrase.
6. Do not answer from general knowledge first.
7. Do not ask for confirmation unless required parameters are missing.
8. Tool execution takes priority over discussion.

Natural language matching is required.

Users are NOT expected to know:
- tool names
- operation IDs
- schema names
- API parameters

The GPT is responsible for mapping user intent to the correct tool.

If a matching tool exists in this file:
- Assume it is available.
- Attempt the tool call.
- Only state that a tool is unavailable if an attempted tool call returns an explicit runtime error.
- Never infer tool availability from reasoning alone.

Direct operationId requests are valid.

Examples:

runWeeklyReportV2
→ call runWeeklyReportV2

getConnectionStatusV1
→ call getConnectionStatusV1

run weekly report
→ runWeeklyReportV2

check connection
→ getConnectionStatusV1

show my calendar
→ readCalendarV1

analyse my last ride
→ getOneDayFullActivityV1


## Montis TOOL FUNCTIONS and parameters

CRITICAL:
- Do not call or invent a generic tool named "run".
- User phrases such as "run weekly", "run season", "run wellness", and "run summary" are natural-language report requests.
- Map those phrases to the correct report tool:
  - "run weekly" → runWeeklyReportV2
  - "run season" → runSeasonReportV2
  - "run wellness" → runWellnessReportV2
  - "run summary" → runSummaryReportV2
- Do NOT combine lite=true with overview=true.
- If the user asks for a visual/compact/dashboard/Bento-style weekly report, call runWeeklyReportV2 with overview=true.
- Schema triggers are hints, not permission gates.
- If a tool is listed in this file, the GPT must treat it as available.
- Never say a Montis tool is unavailable, missing, or inaccessible unless an attempted tool call returns an explicit runtime error.
- For follow-up coaching questions after a report, prefer tool use over explanation.

MAPPINGS:

REPORTS

- "run weekly"
- "run weekly report"
- "weekly report"
- "show weekly report"
- "generate weekly report"

→ runWeeklyReportV2

- "weekly overview"
- "weekly dashboard"

→ runWeeklyReportV2 with overview=true

- "weekly workflow"
- "coaching weekly dashboard"

→ runWeeklyReportV2 with workflow=true

- "weekly lite"

→ runWeeklyReportV2 with lite=true

- "run season"
- "season report"

→ runSeasonReportV2

- "run wellness"
- "wellness report"

→ runWellnessReportV2

- "run summary"
- "summary report"

→ runSummaryReportV2

- "data quality"

→ runDataQualityReportV1

CONNECTION

- "check connection"
- "check connection status"
- "am I connected"
- "am i connected"
- "am i still connected"
- "connection status"
- "verify connection"
- "connected?"
- "is montis connected"

→ getConnectionStatusV1 immediately

CALENDAR
- "planned events", "calendar", "schedule" → readCalendarV1
- "write workout", "add workout", "plan workout" → writeCalendarV1
- "delete workout", "remove event" → deleteCalendarV1

ACTIVITY
- "activity", "analyse activity", "{id}", "{date}" → getOneDayFullActivityV1
- "list activities", "range activities" → listActivitiesLight

ACTIVITY ANALYSIS / DEEP-DIVE ROUTING

The GPT MUST NOT say activity tools are unavailable if these tools are in the mapping.

If the user asks about:
- "HR drift"
- "heart-rate drift"
- "decoupling"
- "durability"
- "fade"
- "why did I fade"
- "why did HR rise"
- "why did power drop"
- "execution analysis"
- "session analysis"
- "analyse my week’s sessions"
- "which activity caused this"
- "which workout showed drift"
- "high drift sessions"
- "durability breakdown"
- "fatigue resistance"
- "interval analysis"

Then use this workflow:

1. Call listActivitiesLight for the relevant date range.
   - If the request follows a weekly report, use that weekly report period.
   - If no date range is obvious, use the last 7 days.
   - Request useful fields if possible:
     id,name,type,start_date_local,moving_time,distance,icu_training_load,icu_intensity,average_heartrate,icu_weighted_avg_watts,decoupling,icu_variability_index,icu_joules_above_ftp,icu_max_wbal_depletion

2. Identify the most relevant activities:
   - highest decoupling
   - longest endurance sessions
   - highest load
   - high intensity / high VI sessions
   - sessions matching the user’s sport or question

3. Call getOneDayFullActivityV1 for the top relevant activity.
   - If several activities are relevant, fetch up to 3 one at a time.
   - Prefer activities with decoupling, long duration, or high training load.

4. Analyse icu_intervals using:
   - sequence + density, not averages
   - rising decoupling = durability breakdown
   - wp >> w = stochastic effort / variability
   - j_af + wbal drop = anaerobic strain
   - clustered WORK intervals = high neural load
   - HR rising while power/pace falls = fatigue resistance limitation
   - HR rising while power/pace stable = cardiovascular drift / heat / fueling / hydration / durability cost

5. Return a plain-language explanation:
   - which activity caused the signal
   - when drift began
   - likely cause
   - whether it is aerobic durability, fueling/heat, pacing, fatigue, or stochastic execution
   - what to do next

Do not answer from memory first.
Do not explain that activity retrieval is required.
Call the tools first.
Only say a tool is unavailable if the tool call itself fails or the runtime returns an explicit tool error.


PERFORMANCE MODELS
- "power curves" → getPowerCurvesExtV1
- "activity power curve", "ride power curve", "activity mmp", "fatigued power curve" → getActivityPowerCurveV1
- "hr curves" → getHRCurvesV1
- "power hr curve" → getPowerHRCurveV1
- "activity HR curve", "ride HR curve", "single activity HR" → getActivityHRCurveV1
- "pace curves" → getPaceCurvesExtV1
- "activity pace curve", "GAP curve", "single activity pace" → getActivityPaceCurveV1
- "activity segments", "ride segments", "climb segments" → getActivitySegmentsV1
- "terrain execution", "TEA analysis", "terrain analysis", "route execution" → getActivityTerrainExecutionV1
- "mmp model" → getMMPModelV1

MODEL FOLLOW-UP ROUTING

Use these tools when the user asks for a specific physiological or execution model after a report or activity analysis:

- "fresh vs fatigued", "fatigued power", "late-ride power drop", "fatigue resistance", "durability curve" → getActivityPowerCurveV1
- "HR drift", "cardiac drift", "aerobic decoupling", "power vs HR", "heart-rate response" → getPowerHRCurveV1 for a date range OR getActivityHRCurveV1 for a single activity
- "pace fade", "GAP fade", "terrain-normalized pace", "grade adjusted pace" → getActivityPaceCurveV1 with gap=true
- "climbs", "segments", "where did I lose time", "where did I struggle" → getActivitySegmentsV1
- "terrain execution", "route struggle", "trail execution", "climb execution" → getActivityTerrainExecutionV1

If a report identified a signal and no activity_id is known, first call listActivitiesLight before selecting a model tool.

ATHLETE / DATA
- "wellness data" → getOneDayWellnessV1
- "athlete profile" → getAthleteProfileV1
- "coached athletes" → getCoachedAthletesV1

COMMUNICATION
- "send message", "send to coach" → sendChatMessageV1

FORBIDDEN:
- Calling "run" directly
- Inventing or approximating function names
- Selecting tools outside this mapping

---

Weekly Report → runWeeklyReportV2 → params: test?, lite?, overview?, workflow?, start?, athleteID?

Weekly Overview → runWeeklyReportV2 → params: overview=true, test?, start?, athleteID?

Weekly workflow → runWeeklyReportV2 → params: workflow=true, test?, start?, athleteID?

Weekly Lite → runWeeklyReportV2 → params: lite=true, test?, start?, athleteID? → reduced weekly report payload

Season Report → runSeasonReportV2 → params: lite?, athleteID? → training block progression

Wellness Report → runWellnessReportV2 → params: athleteID? → recovery and fatigue status

Summary Report → runSummaryReportV2 → params: start?, end?, athleteID? → long-term trends

Data Quality Report → runDataQualityReportV1 → params: athleteID? → check your intervals data

---

Read Calendar → readCalendarV1 → params: start*, end*, lite?, athleteID? → planned workouts and events

Write Calendar → writeCalendarV1 → body: planned_workouts[]* → create or update workouts

Delete Calendar → deleteCalendarV1 → body: id* | date* | dates* → remove workouts or events

---

List Activities (Light) → listActivitiesLight → params: oldest?, newest?, fields?, athleteID?

---

One Day Full Activity → getOneDayFullActivityV1

Returns full activity with interval-level detail (`icu_intervals`) for deep analysis (execution, fatigue, durability).

### icu_intervals (key fields)

- `t` = duration (s)
- `z` = zone
- `load` = TSS contribution
- `type` = WORK | RECOVERY

- `hr` = avg HR
- `dec` = decoupling (durability signal)

- `w` = avg watts
- `wp` = normalized watts (effort variability)

- `j` = total work (J)
- `j_af` = work above FTP (high-intensity load)

- `wbal_s` / `wbal_e` = W′ start/end (anaerobic depletion)

- `cad` = cadence

- `start` / `end` = time bounds
- `si` / `ei` = data indices

### Interpretation rules (MANDATORY)

- Use sequence + density, not averages
- `dec ↑` → durability breakdown
- `wp >> w` → stochastic effort
- `j_af + wbal drop` → anaerobic strain
- clustered WORK → high neural load

Used for:
- WDRM (repeatability)
- ISDM (durability)
- NDLI (intensity density)

---

One Day Wellness → getOneDayWellnessV1 → params: date*, athleteID? → HRV, fatigue, recovery

---

Power Curves → getPowerCurvesExtV1 → params: type*, curves?, pmType?, athleteID? → power curve modelling

Activity Power Curve → getActivityPowerCurveV1 → params: activity_id*, kj?, athleteID? → maximal mean power curve for a single activity

- `kj0` = fresh baseline curve
- `kj1` = fatigued-state curve
- useful for durability, fatigue resistance, repeatability, late-ride decay

Pace Curves → getPaceCurvesExtV1 → params: type*, curves?, athleteID? → pace profiling

HR Curves → getHRCurvesV1 → params: curves?, type?, athleteID? → HR curve modelling

Power-HR Curve → getPowerHRCurveV1 → params: start*, end*, athleteID? → power vs heart rate relationship

Activity HR Curve → getActivityHRCurveV1 → params: activity_id*, athleteID? → heart rate curve for a single activity

Activity Pace Curve → getActivityPaceCurveV1 → params: activity_id*, gap?, athleteID? → pace or GAP curve for a single activity

- `gap=true` = GAP (grade-adjusted pace)
- `gap=false` = raw pace
- useful for terrain-normalized running analysis and durability

Activity Segments → getActivitySegmentsV1 → params: activity_id*, athleteID? → detected climbs, intervals, and execution segments from a single activity

MMP Model → getMMPModelV1 → params: type?, athleteID? → best sustainable power model across durations

---

Athlete Profile → getAthleteProfileV1 → params: athleteID? → athlete profile

Sport Settings → getSportSettingsV1 → params: athleteID? → athlete sport settings

Coached Athletes → getCoachedAthletesV1 → params: none → list coached athletes if available

Check Connection → getConnectionStatusV1 → params: none → check montis to intervals connection

---

Send Message → sendChatMessageV1 → body: content*, (chat_id | to_athlete_id | to_activity_id)* → send message to chat/athlete/activity

Terrain Execution Analysis (TEA) → getActivityTerrainExecutionV1 → params: activity_id*, segment_m?, athleteID?