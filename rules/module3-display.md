## 📅 Date Windows
- Weekly = today−6 → today.  
- Season = today−41 → today.  
- Wellness = same.  
- Always compute dynamically.  

---

## 📐 Display Rules
- If none → “None detected”.  
- Use ✅ ⚠️ ❌.  
- Trends = start→end.  
- Max 3 actions.  

---

## General Report Template (v12.11)

⚠️ Use only **after Audit Enforcement passes**.  
All report types follow mandatory audit rules:  
- Row Count Lock (DataFrame = API count, no truncation)  
- Load First, Filter After  
- Combined totals = exact sum of subtotals  
- Cycling, Running, Swimming, Other always present  
- ❌ Halt if mismatch or missing category  

---

**Audit:** {auditStatus}  

**Key Stats**  
- **Volume:** {totalHours}h  
  {ridesKmBlock: ({ridesKm} km ride)}  
  {runsKmBlock: ({runsKm} km run)}  
  {swimsKmBlock: ({swimsKm} km swim)}  
  {otherKmBlock: ({otherKm} km other)}  
- **Load:** {totalTss} TSS, CTL {ctlStart}→{ctlEnd}, ATL {atlStart}→{atlEnd}, Form {formStart}→{formEnd}  
- **Recovery:** HRV {hrvStart}→{hrvEnd}, RestHR {restingHrStart}→{restingHrEnd}, Sleep avg {sleepHoursAvg}h  
- **Fitness:** VO₂max {vo2maxStart}→{vo2maxEnd}, PerfCond {perfCondMin}→{perfCondMax}, Cycling Decoup {avgPwHrDecoupling}%, Running Decoup {avgPaHrDecoupling}%, Polarisation {polarisationIndex}  
- **Subjective:** Feel ratings {feelingCounts}, RPE avg {avgRpe}, Feel trend {feelTrend}, Mood trend {moodTrend}  
- **Advanced:** ACWR {acwrValue}, Monotony {monotonyValue}, Strain {strainValue}, Recovery Index {recoveryIndexStatus}  

**Events**  
{cyclingBlock: 🚴 Cycling: {event}}  
{runningBlock: 🏃 Running: {event}}  
{swimmingBlock: 🏊 Swimming: {event}}  
{hikeBlock: 🚶 Hike/Walk: {event}}  
{skiBlock: 🎿 Ski: {event}}  
{supBlock: 🏄 SUP: {event}}  
{strengthBlock: 🏋 Strength: {event}}  
{yogaBlock: 🧘 Yoga: {event}}  
{otherBlock: 🟢 Other: {event}}  
{wellnessBlock: 🟠 Wellness: {event}}  
{restBlock: 🛌 Rest Day: {event}}  
{currentBlock: ⏳ Current Day: {event}}  

**Sections**  
- Load vs Recovery → {summaryText}  
- Green Flags → ✅ or none  
- Red/Amber → ❌ / ⚠️ or none  
- Trends → {metric, dir, window, comment}  
- Actions → 3 max  

---

## 📊 Reports

### 1. Weekly
Trigger: weekly report | last 7 days | training summary  
Header: Athlete: {id|You} — {start} → {end}  
Summary: {seasonSummary}  
→ Uses General Template  

### 2. Season Report (Block Analysis)
Trigger: season report | block analysis | any range >7 days
Default: If the user requests “42-day season report” without dates, use today−41 → today. 
Header: Athlete: {id|You} — {start} → {end}  
Summary: {seasonSummary} (high-level overview of the block: training direction, fatigue/recovery balance, and adaptation trends).  
Phases (mandatory):  
- Build: {dates, summary}  
- Overload: {dates, summary}  
- Deload: {dates, summary}  
- Consolidation: {dates, summary}  
Format (mandatory sequence):  
1. Audit  
2. Key Stats  
3. Phases (must appear here, never omitted)  
4. Events  
5. Sections  
Rules:  
- ❌ Never output a season report in weekly format.  
- ✅ Always include the four phases with dates, even if approximated.  
- ✅ Always include a block-level summary at the top.  


### 3. Wellness Trend
Trigger: wellness report | recovery status | wellness trend  
Header: Athlete: {id|You} — Wellness {start} → {end}  
Summary: {wellnessSummary}  
Metrics: HRV {hrvStart}→{hrvEnd}, RestHR {restingHrStart}→{restingHrEnd}, Sleep avg {sleepHoursAvg}h, Weight {weightStart}→{weightEnd}, Feel {feelingCounts}, RPE {avgRpe}, Feel trend {feelTrend}, Recovery Index {recoveryIndexStatus}, Mood/Soreness/Stress = logs or `no data`  
→ Events + Sections from General Template  

### 4. Executive Summary
Trigger: always before combined outputs  
Header: # 🏋️ Training Analysis Package  
Executive Summary: {summaryText}  
- 2–3 sentences integrating load, wellness, subjective. Must include ACWR, Monotony, Strain, Recovery Index.  

⚠️ Rules: Merge RPE/Feel from activities if missing in wellness. Events = calendar days.  

---

## Polarisation Index Rule
- Calculated only from Cycling, Running, Swimming with intensity.  
- Other excluded (hike, yoga, strength, etc.).  
- If missing → “no data”.  
