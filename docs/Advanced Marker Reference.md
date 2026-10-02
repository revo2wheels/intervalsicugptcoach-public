# 📊 Advanced Markers v1.1

🔗 Related files:  
- See **Coaching Heuristics Pack** for decision rules using these markers.  
- See **Coaching Cheat Sheet** for quick classification thresholds.  

Composite and derived training metrics used for deeper analysis.  

---

## Load & Stress Metrics

### Adaptive Load & Strain Scaling
All TSS-based metrics scale to athlete volume. Use average weekly hours to select thresholds.

| Athlete Type | Hours/wk | ✅ Green | ⚠️ Amber | ❌ Red |
|:--|--:|--:|--:|--:|
| Recreational | 4–7 | <700 | 700–1000 | >1000 |
| Competitive Amateur | 8–14 | <1200 | 1200–1600 | >1600 |
| High-Volume / Elite | 15–20 | <1800 | 1800–2200 | >2200 |
| Professional | >20 | <2200 | 2200–2700 | >2700 |

Apply these scaling rows for:
- **Weekly Load (TSS)** = total 7-day training load.  
- **Weekly Strain** = Σ weekly load, used for block monitoring.  
- **ACWR, Monotony, and Recovery Index** follow same scaled banding.

---

### ACWR — Acute:Chronic Workload Ratio  
**Definition:** Ratio of short-term (ATL) to long-term (CTL) training load.  

| Status | Threshold | Coaching Insight |
|--------|-----------|------------------|
| ✅ Green | 0.8–1.3  | Balanced progression |
| ⚠️ Amber | 1.3–1.5 | Overreaching, short-term risk |
| ❌ Red   | >1.5    | High injury/illness risk |

---

### Monotony  
**Definition:** Mean daily load ÷ Standard deviation of daily load.  

| Status | Threshold | Coaching Insight |
|--------|-----------|------------------|
| ✅ Green | <1.5     | Healthy day-to-day variation |
| ⚠️ Amber | 1.5–2.0 | Training becoming repetitive |
| ❌ Red   | >2.0     | High monotony, illness risk |

---

### Recovery Index  
**Definition:** Composite score of HRV, RestHR, and Form.  

| Status | Threshold | Coaching Insight |
|--------|-----------|------------------|
| ✅ Green | HRV stable, RestHR steady, Form ≥0 | Recovery adequate |
| ⚠️ Amber | HRV ↓15–25%, RestHR +5 bpm        | Partial strain, monitor load |
| ❌ Red   | HRV ↓>25% or RestHR +10 bpm        | Non-functional overreaching |

---

## ⚡ Efficiency & Endurance Metrics  

### Polarisation Index  
**Definition:** Treff et al. 2019 index on Seiler 3-zone fractions (Z1 = Z1+Z2, Z2 = Z3+Z4, Z3 = Z5–Z7; renormalised to sum to 1).  
**Calculation:** PI = log10((Z1 / Z2) × Z3 × 100). If Z2 = 0: log10(Z1 / 0.01 × (Z3 − 0.01) × 100). Power-based; Ride HR zones only when no power.  

| Status | Threshold | Coaching Insight |
|--------|-----------|------------------|
| Polarised | PI > 2.00 | Polarised distribution |
| Not polarised | PI ≤ 2.00 | Not polarised (informational) |
| PI = 0 | Z3 = 0 | No time above LT2, by definition |
| Not calculated | Z3 > Z1 | Index not valid (null) |

*Informational only — no good/bad bands. `Polarisation_fused` (dominant sport) and `Polarisation_combined` (all endurance sports, lower confidence) use the same index and > 2.00 cut-off.*  
References: [Treff et al. 2019](https://pubmed.ncbi.nlm.nih.gov/31249533/)

---

### Durability Index (avgDecoupling)  
**Calculation:** Average decoupling % across endurance sessions >2h.  

| Status | Threshold | Coaching Insight |
|--------|-----------|------------------|
| ✅ Green | ≤5% drift | Strong aerobic durability |
| ⚠️ Amber | 5–7%      | Aerobic base under moderate strain |
| ❌ Red   | >7%       | Aerobic base not resilient |

---

### Training Distribution Model  
**Definition:** Seiler 3-zone distribution type (Seiler Z1 = Z1+Z2, Z2 = Z3+Z4, Z3 = Z5–Z7), using Intervals.icu's rules. `Polarisation` value = % of time in Seiler Z1. Power-based; Ride HR zones only when no power.  

- **Types (checked in this order):**  
  - HIIT (Z3 > Z2 and Z3 > 0.499 × (Z1+Z2)).  
  - Polarised (Z3 > Z2 and Z1 > Z2).  
  - Base (Z1 > 3.99 × Z2 and Z1 > 3 × (Z2+Z3)).  
  - Pyramidal (1.4 × Z2 < Z1 < 3.01 × Z2 and Z2 > 1.4 × Z3).  
  - Threshold (Z1 < 4 × Z2 and Z2 > 0.5 × Z3).  
  - Unique (none of the above).  

*Note: Classification only — no good/bad bands. Seiler's "80/20" counts sessions, not minutes. Sweet Spot overlaps Z3/Z4 and is not added to the Z1–Z7 total.*  
References: [Seiler 2010](https://pubmed.ncbi.nlm.nih.gov/20861519/), [Stöggl & Sperlich 2015](https://pubmed.ncbi.nlm.nih.gov/26578968/)

---

### Quality Session Balance  
**Definition:** Ratio of long endurance sessions (2h+) and interval sessions (VO₂max/threshold) per week.  

| Status | Threshold | Coaching Insight |
|--------|-----------|------------------|
| ✅ Green | ≥2 quality sessions/week (≥1 long, ≥1 interval) | Balanced stimulus for durability + intensity |
| ⚠️ Amber | 1 quality session/week | Missing either endurance or intensity |
| ❌ Red   | 0 quality sessions | Lack of key adaptation stimulus |

## Report Output Template (moved from Final Instructions)
> Defines the full post-audit report layout and all marker placeholders.

⚠️ Use only **after Audit Enforcement passes**  
- **Mood Field:** if `{moodTrend}` = null or "no data", omit from report  
- Row Count Lock  
- Load First, Filter After  
- Combined totals = exact sum of subtotals  
- Cycling, Running, Swimming, Other always present  
- ❌ Halt if mismatch or missing category  

Knowledge: Strictly follows **Knowledge Reference Rule** (icons, thresholds, definitions, heuristics applied in priority order)

**Audit:** {auditStatus}

### Key Stats
- **Volume:** {totalHours}h  
  {ridesKmBlock: ({ridesKm} km ride)}  
  {runsKmBlock: ({runsKm} km run)}  
  {swimsKmBlock: ({swimsKm} km swim)}  
  {otherKmBlock: ({otherKm} km other)}  
- **Load:** {totalTss} TSS, CTL {ctlStart}→{ctlEnd}, ATL {atlStart}→{atlEnd}, Form {formStart}→{formEnd}  
- **Recovery:** HRV {hrvStart}→{hrvEnd}, RestHR {restingHrStart}→{restingHrEnd}, Sleep avg {sleepHoursAvg}h  
- **Fitness:** VO₂max {vo2maxStart}→{vo2maxEnd}, PerfCond {perfCondMin}→{perfCondMax}, Cycling Decoup {avgPwHrDecoupling}%, Running Decoup {avgPaHrDecoupling}%, Polarisation Index (Treff) {polarisationIndex}  
- **Subjective:** Feel ratings {feelingCounts}, RPE avg {avgRpe}, Feel trend {feelTrend}, Mood trend {moodTrend}  
- **Advanced:** ACWR {acwrRaw} ({acwrEval}), Monotony {monotonyRaw} ({monotonyEval}), Strain {strainRaw} ({strainEval}), Recovery Index {recoveryIndexRaw} ({recoveryIndexEval})

### Events (daily log)
{dayLogBlock: Mon{event}, Tue{event}, Wed{event}, Thu{event}, Fri{event}, Sat{event}, Sun{event}}

### Sections
- Load vs Recovery → {summaryText}  
- Green Flags → ✅ or none  
- Red/Amber → ❌ / ⚠️ or none  
- Trends → {metric, dir, window, comment}  
- Actions → 3 max  

### Unified Metric References
Include optional derived markers if data present:
- Training Distribution: classify Seiler 3-zone type — HIIT / Polarised / Base / Pyramidal / Threshold / Unique.  
- Durability Index (>2h decoupling): Stable / Declining / Improving.  
- VO₂max & PerfCond: trend if logged else “no data”.  
- Mood / Stress / Soreness: daily trend if wellness logged else “no data”.  
- Weekly Strain (Scaled): render from Adaptive Load & Strain Scaling.


