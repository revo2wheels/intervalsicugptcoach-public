# 📖 Glossary & Placeholders


🔗 Related files:  
- See **Advanced Markers** for derived metrics (ACWR, Strain, Monotony, Durability).  
- See **Coaching Heuristics Pack** for decision rules and sport adaptations.  
- See **Coaching Cheat Sheet** for quick traffic-light thresholds.  

...

## 🔑 General Placeholders

* `{athleteNameOrId}` → Athlete identifier (default = athlete 0, current user).
* `{dateRangeStart}` / `{dateRangeEnd}` → Start and end of the report window.
* `{executiveSummaryText}` → 2–3 sentence integrated overview across reports.

---

## 📊 Key Stats

* `{totalHours}` → Total training hours in period.
* `{ridesKm}` / `{runsKm}` / `{swimsKm}` → Discipline-specific volume in km.
* `{totalTss}` → Total training stress score in period.
* `{ctlStart}` / `{ctlEnd}` → Fitness (chronic load) start and end values.
* `{atlStart}` / `{atlEnd}` → Fatigue (acute load) start and end values.
* `{formStart}` / `{formEnd}` → Form (CTL–ATL) start and end values.
* `{hrvStart}` / `{hrvEnd}` → Heart rate variability trend (ms).
* `{restingHrStart}` / `{restingHrEnd}` → Resting heart rate trend (bpm).
* `{sleepHoursAvg}` → Average sleep hours.
* `{sleepScoreAvg}` → Average sleep quality/score if available.
* `{vo2maxStart}` / `{vo2maxEnd}` → Cycling VO₂max trend.

## ⚡ Efficiency & Endurance

* `{avgDecoupling}` → Average aerobic decoupling in % (durability marker).
* `{polarisationIndex}` → Polarisation index of training intensity.
* `{durabilityIndex}` → Average decoupling % across endurance sessions >2h (lower = stronger durability).
* `{trainingDistributionModel}` → Classification of training intensity balance (Polarised, Pyramidal, or Threshold-heavy).
* `{qualitySessionCount}` → Number of quality sessions (long endurance + intensity intervals) completed per week.
* `{qualitySessionBalance}` → Classification of quality session balance (adequate, missing intensity, missing long endurance).

---

## 🧠 Subjective / Wellness

* `{feelingCounts}` → Count of “poor / good / strong” feeling ratings.
* `{avgRpe}` → Average RPE score.
* `{feelTrend}` → Description of trend in Feel (easy/moderate/hard).
* `{moodTrend}` → Description of trend in mood logs.
* `{rpeDistribution}` → Histogram/distribution of RPE values across period.
* `{moodSorenessStressSummary}` → Summary of wellness notes.
* `{weightStart}` / `{weightEnd}` → Weight change over the period.

---

## 📅 Events

* `{trainingEvent}` → Activity event (ride, run, etc.).
* `{eventDate}` → Date of the event.
* `{eventDescription}` → Short description (duration, load, conditions).
* `{wellnessEvent}` → Wellness log event (e.g. poor rating, high stress).
* `{sleepEvent}` → Sleep-related event (short night, poor sleep).
* `{sleepDescription}` → Sleep details (hours, quality).

---

## 🪜 Season / Phases

* `{phaseDates}` → Date range of each block/phase (build/overload/deload/consolidation).
* `{phaseOneSummary}` / `{phaseTwoSummary}` / `{phaseThreeSummary}` / `{phaseFourSummary}` → Summary of each phase.
* `{acwrTrendValues}` → ACWR trend over the season.
* `{acwrTrendInterpretation}` → Interpretation of ACWR trend.
* `{monotonyRangeValues}` → Range of monotony values in block.
* `{monotonyRangeInterpretation}` → Interpretation of monotony range.
* `{strainPeakValues}` → Peaks in strain across season.
* `{strainPeakInterpretation}` → Interpretation of strain peaks.
* `{recoveryIndexPhaseInterpretation}` → Phase-by-phase interpretation of Recovery Index.

---

## 📉 Trends

* `{trendMetric}` → Metric being tracked (e.g. CTL, HRV, RPE).
* `{trendDirection}` → Direction (up, down, stable).
* `{trendWindow}` → Time window (7 days, 42 days, etc.).
* `{trendMagnitude}` → Numeric change over the window.
* `{trendComment}` → Interpretation of the trend.

---

## ✅ Actions

* `{actionOne}` / `{actionTwo}` / `{actionThree}` → Weekly forward-looking actions.
* `{seasonActionOne}` / `{seasonActionTwo}` / `{seasonActionThree}` → Season-level actions.
* `{wellnessActionOne}` / `{wellnessActionTwo}` / `{wellnessActionThree}` → Wellness-specific actions.
