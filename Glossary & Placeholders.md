# 📖 Glossary & Placeholders

🔗 Related files:

- See **Advanced Markers** for derived metrics (ACWR, Strain, Monotony, Durability).
- See **Coaching Heuristics Pack** for decision rules and sport adaptations.
- See **Coaching Cheat Sheet** for quick traffic-light thresholds.

...

## 🔑 General Placeholders

- `{athleteNameOrId}` → Athlete identifier (default = athlete 0, current user).
- `{dateRangeStart}` / `{dateRangeEnd}` → Start and end of the report window.
- `{executiveSummaryText}` → 2–3 sentence integrated overview across reports.

## 🧮 Audit & System Flags

| Placeholder | Definition |
|:--|:--|
| `{auditPartial}` | Boolean flag set to True after successful Tier 1 audit (partial verification complete). |
| `{auditFinal}` | Boolean flag set to True after Tier 2 audit passes and all checks validated. |
| `{auditStatus}` | Text or emoji summary (✅ / ⚠️ / ❌) representing overall audit result. |
| `{integrityFlag}` | Data integrity validation state (live / partial / invalid). |
| `{integrityNote}` | Short explanation of data completeness or fetch origin. |

## Data Structure Definitions (moved from Core Rules)
- **Activities:** dist, move time, TSS, power, HR, RPE, Feel, elev, VO₂max, PerfCond, ftp, IF from `listActivities`
- **Wellness:** CTL, ATL, Form, Ramp, weight, sleep, HRV, RestHR, comments from `listWellness`

## Totals vs Trends (moved from Core Rules)
Defines how different datasets aggregate values across time.

- **Activities:** represent totals (e.g., sum of TSS, sum of hours, sum of km).  
- **Wellness:** represents trends (e.g., CTL, ATL, Form, HRV) computed as start→end change.  
- Never cross-sum these datasets; totals and trends are treated independently.

## Precision Standards
- Distance: 2 decimals  
- TSS = SUM(icu_training_load)  
- Move time formatted hh:mm:ss.

## Date Windows (moved from Final Instructions)
Defines default dynamic reporting periods used across all audits.
- **Weekly:** today − 6 → today  
- **Season:** today − 41 → today (default)  
- **Wellness:** same as Season  
- All date ranges computed dynamically at runtime using local athlete timezone.

## 📊 Key Stats

- `{totalHours}` → Total training hours in period.
- `{ridesKm}` / `{runsKm}` / `{swimsKm}` → Discipline-specific volume in km.
- `{totalTss}` → Total training stress score in period.
- `{ctlStart}` / `{ctlEnd}` → Fitness (chronic load) start and end values.
- `{atlStart}` / `{atlEnd}` → Fatigue (acute load) start and end values.
- `{formStart}` / `{formEnd}` → Form (CTL–ATL) start and end values.
- `{hrvStart}` / `{hrvEnd}` → Heart rate variability trend (ms).
- `{restingHrStart}` / `{restingHrEnd}` → Resting heart rate trend (bpm).
- `{sleepHoursAvg}` → Average sleep hours.
- `{sleepScoreAvg}` → Average sleep quality/score if available.
- `{vo2maxStart}` / `{vo2maxEnd}` → Cycling VO₂max trend.
- `{acwrRaw}` → float, computed ACWR ratio (ATL ÷ CTL)
- `{acwrEval}` → classification per Adaptive Load & Strain Scaling (Green / Amber / Red)
- `{monotonyRaw}` → float, mean daily load ÷ SD daily load
- `{monotonyEval}` → classification per Adaptive Load & Strain Scaling
- `{strainRaw}` → float, Σ icu_training_load (weekly TSS total)
- `{strainEval}` → classification per Adaptive Load & Strain Scaling
- `{recoveryIndexRaw}` → float, composite index (HRV + RestHR + Form)
- `{recoveryIndexEval}` → classification per Adaptive Load & Strain Scaling
Always sum exact values from activities. Do not round. Do not estimate. Weekly totals must equal the sum of listed Events.

## ⚡ Efficiency & Endurance

- `{avgDecoupling}` → Average aerobic decoupling in % (durability marker).
- `{polarisationIndex}` → Polarisation index of training intensity.
- `{durabilityIndex}` → Average decoupling % across endurance sessions >2h (lower = stronger durability).
- `{trainingDistributionModel}` → Classification of training intensity balance (Polarised, Pyramidal, or Threshold-heavy).
- `{qualitySessionCount}` → Number of quality sessions (long endurance + intensity intervals) completed per week.
- `{qualitySessionBalance}` → Classification of quality session balance (adequate, missing intensity, missing long endurance).

* * *

## 🧠 Subjective / Wellness

- `{feelingCounts}` → Count of “poor / good / strong” feeling ratings.
- `{avgRpe}` → Average RPE score.
- `{feelTrend}` → Description of trend in Feel (easy/moderate/hard).
- `{moodTrend}` → Description of trend in mood logs.
- `{rpeDistribution}` → Histogram/distribution of RPE values across period.
- `{moodSorenessStressSummary}` → Summary of wellness notes.
- `{weightStart}` / `{weightEnd}` → Weight change over the period.

* * *

## 📅 Events

- `{trainingEvent}` → Activity event (ride, run, etc.).
- `{eventDate}` → Date of the event.
- `{eventDescription}` → Short description (duration, load, conditions).
- `{wellnessEvent}` → Wellness log event (e.g. poor rating, high stress).
- `{sleepEvent}` → Sleep-related event (short night, poor sleep).
- `{sleepDescription}` → Sleep details (hours, quality).
- `{restDayEvent}` → 🛌 Rest Day (no training logged on that date).

* * *

## 🪜 Season / Phases

- `{phaseDates}` → Date range of each block/phase (build/overload/deload/consolidation).
- `{phaseOneSummary}` / `{phaseTwoSummary}` / `{phaseThreeSummary}` / `{phaseFourSummary}` → Summary of each phase.
- `{acwrTrendValues}` → ACWR trend over the season.
- `{acwrTrendInterpretation}` → Interpretation of ACWR trend.
- `{monotonyRangeValues}` → Range of monotony values in block.
- `{monotonyRangeInterpretation}` → Interpretation of monotony range.
- `{strainPeakValues}` → Peaks in strain across season.
- `{strainPeakInterpretation}` → Interpretation of strain peaks.
- `{recoveryIndexPhaseInterpretation}` → Phase-by-phase interpretation of Recovery Index.

* * *

## 📉 Trends

- `{trendMetric}` → Metric being tracked (e.g. CTL, HRV, RPE).
- `{trendDirection}` → Direction (up, down, stable).
- `{trendWindow}` → Time window (7 days, 42 days, etc.).
- `{trendMagnitude}` → Numeric change over the window.
- `{trendComment}` → Interpretation of the trend.

* * *

## ✅ Actions

- `{actionOne}` / `{actionTwo}` / `{actionThree}` → Weekly forward-looking actions.
- `{seasonActionOne}` / `{seasonActionTwo}` / `{seasonActionThree}` → Season-level actions.
- `{wellnessActionOne}` / `{wellnessActionTwo}` / `{wellnessActionThree}` → Wellness-specific actions.

## Event Icon Mapping

- Ride, VirtualRide → 🚴
- Run, VirtualRun → 🏃
- Swim → 🏊
- Hike → 🚶
- Ski → 🎿
- SUP → 🏄
- Strength → 🏋
- Yoga → 🧘
- Other → 🟢
- Rest Day → 🛌
- Current Day → ⏳

## 🧠 Subjective Metrics

### **RPE — Rate of Perceived Exertion (1–10 Scale)**
> Subjective measure of workout intensity (Borg CR10 scale).  
> Used for internal load validation, ACWR moderation, and effort classification.  
> Typically correlates with %VO₂max or %HRmax when averaged across sessions.

| Value | Label | Descriptor |
|:--:|:--|:--|
| 1 | Very Easy | Recovery spin / minimal effort |
| 2 | Easy | Sustainable endurance |
| 3 | Moderate | Aerobic base work |
| 4 | Somewhat Hard | Tempo / sub-threshold |
| 5 | Hard | Threshold effort |
| 6 | Very Hard | Above threshold sustained |
| 7 | Severe | VO₂ interval intensity |
| 8 | Very Severe | Anaerobic burst / short |
| 9 | Near Max | Race-level maximal work |
| 10 | Maximal Effort | All-out exhaustion, sprint or test |

**Usage Notes**
- Use **RPE = mean** for daily merge logic (not max).  
- RPE < 3 with TSS > 150 → ⚠ possible under-reporting.  
- RPE ≥ 8 with TSS < 50 → ⚠ possible non-physiological stress.

---

### **Feel — Subjective Readiness (1–5 Scale)**
> Perceived daily wellbeing and recovery (Intervals.icu convention).  
> Independent of training intensity.  
> Lower = better readiness.

| Value | Label | Descriptor |
|:--:|:--|:--|
| 1 | Strong | Excellent readiness; high energy |
| 2 | Good | Normal condition; mild fatigue |
| 3 | Normal | Slightly tired; moderate recovery |
| 4 | Poor | Flat, sore, or fatigued |
| 5 | Weak | Unrecovered, ill, or overstressed |

**Usage Notes**
- Use **Feel = min** for daily merge logic (lowest readiness).  
- Feel ≥ 4 with normal TSS → ⚠ possible external stress or under-recovery.  
- Feel 1–2 sustained ≥ 5 days → ✅ high adaptation readiness.


## 🚴 Ride Intensity Classification

{rideTypeLabel} → Text label derived from IF value.\*

IF range {rideTypeLabel} Description  
<0.60 Recovery Very easy spin, active recovery only  
0.60–0.75 Endurance/Base Aerobic base, Z2 steady work  
0.76–0.90 Tempo Sub-threshold sustainable intensity  
0.91–1.05 Threshold Race-pace or FTP-level efforts  
\>1.05 VO₂max / Anaerobic High-intensity intervals

## 🧩 Unified Reporting Framework Extensions

This section lists all new placeholders and markers introduced in the **Unified Reporting Framework v5.1**, supporting Seiler, San Millán, and Friel integrations.  
These are **render-time** tokens only — they do not replace existing audit-level placeholders.

| Placeholder | Definition |
|:--|:--|
| `{fatOxidationIndexRaw}` | Calculated Fat-Oxidation efficiency score (San Millán model) |
| `{fatOxidationIndexEval}` | Traffic-light classification (≥ 0.80 ✅ / 0.60–0.79 ⚠️ / < 0.60 ❌) |
| `{avgDecoupling}` | Mean HR–Power drift (%) for long Z2 rides |
| `{fatMaxValidationNote}` | Accuracy of FatMax calibration (± 5 %) |
| `{fatOxidationQualityNote}` | Text summary of Z2 metabolic execution quality |
| `{benchmarkIndex}` | Functional Benchmark progress metric (Friel model) |
| `{benchmarkPrev}` / `{ΔBenchmark}` | Previous Benchmark value and delta |
| `{benchmarkFlag}` | Benchmark trend classification |
| `{specificityIndex}` | Race-specific training ratio |
| `{specificityPrev}` / `{ΔSpecificity}` | Historical comparison of specificity |
| `{specificityFlag}` | Specificity alignment flag |
| `{consistencyIndex}` | Session adherence ratio (completed ÷ planned) |
| `{consistencyPrev}` / `{ΔConsistency}` | Historical adherence delta |
| `{consistencyFlag}` | Adherence compliance flag |
| `{sessionIntensityRatio}` | Ratio of low-intensity sessions (Z1–Z2 ÷ total) — Seiler 80/20 marker |
| `{microcycleRecoveryWeek}` | Flag for deload or recovery microcycle (Friel model) |
| `{totalZ2h}` | Total Zone 2 duration (hours) for the reporting window |
| `{z12h}` / `{z12pct}` | Combined Z1–Z2 hours and percent |
| `{z35h}` / `{z35pct}` | Combined Z3–Z5 hours and percent |
| `{polarisationIndex}` / `{polarisationFlag}` | Intensity distribution score and flag |
| `{durabilityIndex}` / `{durabilityFlag}` | Aerobic durability score and flag |
| `{recoveryIndex}` / `{recoveryStatus}` | Composite recovery index and classification |

**Note:**  
These tokens are consumed by:
- `Unified_Reporting_Framework_v5.1.md`
- `Weekly_Report_v5.1.md`
- `Season_Report_v5.1.md`
- `Executive_Summary_v5.1.md`

and require audit ✅ before render.

---

