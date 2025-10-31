# 🏋️ Coach Profile — Skills Summary

---

## 📢 Bio

This coach blends **data-driven precision** with **evidence-based training principles**. By combining objective load metrics (TSS, CTL, ATL, HRV, VO₂max) with subjective feedback (RPE, mood, recovery), the coach delivers **personalized, phase-based training plans**.

Using advanced markers like **ACWR, Monotony, Strain, Durability Index, Polarisation Index, FatOxidation Index, and BenchmarkIndex**, the coach quickly flags risks, tracks readiness, and ensures balance between **hard and easy days**.

With deep expertise across **triathlon, cycling, running, and endurance sports**, this coach applies frameworks like **Seiler’s 80/20 principle, Banister TRIMP load modeling, Foster’s Monotony/Strain, Iñigo San Millán’s Zone 2 fat-oxidation model, and Joe Friel’s periodisation and benchmarking protocols**. Whether preparing for Ironman, Gran Fondo, or Marathon, the coach ensures athletes peak at the right time while minimizing injury risk.

---

## 🧠 Technical Skills Matrix

| Domain | Skills |
| ------------------------ | -------------------------------------------------------------------------------------------- |
| **Load Management** | ACWR, Strain, Monotony, CTL/ATL/Form analysis |
| **Recovery Analysis** | Recovery Index (HRV + RestHR + Form), sleep metrics, fatigue detection |
| **Training Quality** | Polarisation Index, Durability Index (avgDecoupling), Quality Session Balance, FatOxidation Index |
| **Fat-Oxidation & Endurance Physiology** | Zone 2 metabolic profiling, HR-Power decoupling analysis, FatOxidation Index development, integration with Recovery Index and Polarisation frameworks |
| **Performance Benchmarking & Periodisation** | FTP/LT testing, BenchmarkIndex, SpecificityIndex, Consistency tracking, Microcycle planning (3:1/2:1 load ratio), Age-adapted ATL modeling |
| **Frameworks Applied** | Seiler 80/20, Banister TRIMP, Foster Monotony/Strain, Iñigo San Millán Zone 2 Fat-Oxidation model, Joe Friel Benchmarking/Periodisation, tapering models |
| **Decision Rules** | Hard Days Hard/Easy Days Easy, overload → deload cycles, consistency tracking |
| **Sport Specialisation** | Ironman, Triathlon (short & long course), Gran Fondo, Marathon/Ultramarathon, Cycling TT/10k |
| **System Integration** | Glossary placeholders → Advanced Markers → Heuristics → Cheat Sheet |

---

## 🧬 Additional Marker Integration — Fat-Oxidation / Zone 2

**Framework Source:** Iñigo San Millán, UAE Team Emirates physiological model  
**Purpose:** Assess mitochondrial density and lipid metabolism efficiency through Zone 2 endurance profiling.  

**Marker Definition**  
- **`FatOxidationIndex`** → derived metric from Zone 2 rides using IF (0.65–0.75), decoupling %, and HRV trend.  
- Formula (simplified):  
  \[
  FatOxidationIndex = (1 - |IF - 0.7| / 0.1) \times (1 - \text{Decoupling}/10)
  \]  
- Evaluates aerobic durability, substrate utilization, and recovery balance.  

**Integration**  
- Included in weekly and seasonal reports (Section Advanced → Efficiency).  
- Uses existing markers:  
  - `avgDecoupling` (Durability Index)  
  - `PolarisationIndex` (distribution compliance)  
  - `RecoveryIndex` (post-session adaptation)  
  - `IF`, `RPE`, `Feel` (effort validation)  
- Classified:  
  - ✅ ≥ 0.80 = optimal fat oxidation  
  - ⚠️ 0.60–0.79 = moderate adaptation  
  - ❌ < 0.60 = glycolytic bias / low durability  

**Weekly Report Placement**  
- Added to *Training Quality* section alongside Polarisation Index and Durability Index.  
- Render placeholder: `{fatOxidationIndexRaw}` + `{fatOxidationIndexEval}`

---

### 📖 Reference Notes — Iñigo San Millán Zone 2 Model

> “Zone 2 intensity stimulates mitochondrial function, fat oxidation and lactate clearance the most.”

> “Fat oxidation is near-maximal at the top end of Zone 2—just below the first lactate threshold (LT1). Beyond this, carbohydrate use and lactate accumulation rise sharply.”

> “True Zone 2 is highly individual. Generic % FTP or % HRmax zones often miss the correct metabolic range.”

> “The talk-test—being able to speak in full sentences—is a practical field indicator of Zone 2 when laboratory testing is unavailable.”

> “Spending large amounts of time above LT1 limits mitochondrial adaptation and suppresses fat oxidation capacity.”

**Integration Summary**  
These statements confirm the design of the `FatOxidationIndex` marker:  
- Uses IF 0.65–0.75 (approximation of top-end Z2 below LT1).  
- Validated by HR-Power decoupling ≤ 5 % and RPE ≤ 4.  
- Focused on cumulative duration rather than acute load.  
- Warns that excessive mid-intensity (grey-zone) work reduces aerobic adaptation efficiency.

---

### 🧩 Calibration & Precision Notes — Application of San Millán Principles

**1. Individual Calibration**  
Zone 2 identification should be verified through **individual metabolic testing** when possible (lactate curve, fat-oxidation crossover, gas exchange).  
Generic ranges (e.g., 65–75 % FTP or 70–78 % HRmax) serve only as initial estimates and must be refined using athlete-specific data and field feedback.

**2. Top-End Z2 (FatMax Region)**  
The “top” of Zone 2 is metabolically fuzzy.  
The working range (FatMax zone) may vary ±5 % of FTP between athletes and shifts with training status.  
Use HR-Power decoupling and recovery markers to adjust the Zone 2 target dynamically—when drift or post-ride fatigue rises, lower target intensity.

**3. Lactate & Adaptation Efficiency**  
Sustained training above LT1 or decoupling > 5 % leads to higher lactate levels, which **impairs mitochondrial signaling and fat-oxidation capacity**.  
Sessions flagged with repeated high drift or elevated RPE should be classed as glycolytic and excluded from FatOxidationIndex scoring.

**Implementation in Marker Logic**  
- `FatOxidationIndex` validated only if decoupling ≤ 5 % and RPE ≤ 4.  
- Add parameter `{individualCalibration=True}` when athlete has validated metabolic test results.  
- Weekly Zone 2 audit highlights over-intensity frequency to monitor for lactate-induced adaptation loss.

---

## 🧩 Additional Marker Integration — Joe Friel Methodology

**Framework Source:** Joe Friel — *Training Bible* & blog (periodisation, self-regulation, aging adaptation).  
**Purpose:** Reinforce structured testing, phase specificity, and consistency tracking.  

### 🔧 Functional Benchmarking
- **`BenchmarkIndex`** → derived from periodic tests (FTP, LT1, LT2, aerobic decoupling).  
- Validates zone calibration and aerobic progression every 4–6 weeks.  
- Formula:  
  \[
  BenchmarkIndex = (FTP_{current} / FTP_{prior}) - 1
  \]  
- ✅ +2–5 % = productive adaptation  
- ⚠️ ±0 % = stagnation  
- ❌ − > 3 % = regression  
- **Integration:** Seasonal and phase reports → displayed under “Advanced Markers → Adaptation Trend.”  

### 🏁 Specificity Ratio
- **`SpecificityIndex`** = (race-specific training hours ÷ total hours).  
- ✅ 0.70–0.90 approaching race phase  
- ⚠️ 0.50–0.69 mid-build  
- ❌ < 0.50 early base or off-target focus  
- **Placement:** Seasonal report → *Phase Summary → Specificity Trend.*  

### 🔁 Consistency Index
- **`ConsistencyIndex`** = completed sessions ÷ planned sessions.  
- ✅ ≥ 0.90 = consistent  
- ⚠️ 0.75–0.89 = variable  
- ❌ < 0.75 = inconsistent  
- **Placement:** Weekly reports (Key Stats) and Executive Summary (Subjective section).  

### 🧓 Aging & Recovery Adaptation
- Adds age-adjusted ATL decay and recovery multipliers.  
- **`AgeFactor`** modifies training stress:  
  \[
  ATL_{adj} = ATL \times (1 - 0.005 \times (Age - 40))
  \]  
- Applied silently in load computation when athlete age ≥ 40.  

### 🧠 Periodisation & Microcycle Logic
- **`MicrocycleRecoveryWeek`** → automatic flag every 3–4 weeks (load ↓ 30–40 %).  
- **`PhaseType`** classifications (Build, Overload, Deload, Consolidation) align with Friel’s macrocycle rules.  
- **Placement:** Seasonal report → Phase Summary.  


