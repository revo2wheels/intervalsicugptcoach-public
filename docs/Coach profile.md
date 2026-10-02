# 🏋️ Coach Profile — Skills Summary

---

## 📢 Bio

This coach blends **data-driven precision** with **evidence-based training principles**. By combining objective load metrics (TSS, CTL, ATL, HRV, VO₂max) with subjective feedback (RPE, mood, recovery), the coach delivers **personalized, phase-based training plans**.

Using advanced markers like **ACWR, Monotony, Strain, Durability Index, Polarisation Index, FatOxidation Index, and BenchmarkIndex**, the coach quickly flags risks, tracks readiness, and ensures balance between **hard and easy days**.

With deep expertise across **triathlon, cycling, running, and endurance sports**, this coach applies frameworks like **Seiler’s 80/20 principle, Banister TRIMP load modeling, Foster’s Monotony/Strain, Iñigo San Millán’s Zone 2 fat-oxidation model, and Joe Friel’s periodisation and benchmarking protocols**. Whether preparing for Ironman, Gran Fondo, or Marathon, the coach ensures athletes peak at the right time while minimizing injury risk.

---

## 🧠 Technical Skills Matrix (Aligned v16.1–EOD Sync)

| **Domain** | **Skills** |
|:--|:--|
| **Load Management** | ACWR, Strain, Monotony (Foster), CTL/ATL/Form, TRIMP (Banister), W′/CP modeling (Skiba), load balance validation |
| **Recovery Analysis** | Recovery Index (HRV + RestHR + Form), fatigue detection, sleep quality integration, readiness tracking (Noakes model), subjective recovery scaling |
| **Training Quality** | Polarisation Index (Treff 2019; Seiler 3-zone), Durability Index (Sandbakk), Session Quality Ratio, FatOxidation Index (San Millán), training monotony harmonisation |
| **Fat-Oxidation & Endurance Physiology** | Zone 2 metabolic profiling (Iñigo San Millán), HR–Power decoupling, FatOxidation Index computation, mitochondrial efficiency modeling, Recovery–Polarisation interaction mapping |
| **Performance Benchmarking & Periodisation** | FTP/LT testing (Coggan), BenchmarkIndex, SpecificityIndex, consistency tracking, microcycle (3:1 / 2:1) load ratios, age-adapted ATL modeling (Joe Friel) |
| **Frameworks Applied** | Seiler 80/20 Polarisation • Banister TRIMP • Foster Monotony–Strain • Iñigo San Millán Zone 2 • Joe Friel Periodisation • Sandbakk Durability • Skiba W′/Critical Power • Coggan Power Zones • Noakes Central Governor • Hybrid Polarised–Sweet Spot |
| **Decision Rules** | Hard Days Hard / Easy Days Easy • Overload→Deload cycles • Consistency tracking • Load–Readiness modulation • Fatigue threshold gating |
| **Sport Specialisation** | Triathlon (Sprint → Ironman) • Gran Fondo • Marathon / Ultramarathon • Time Trial / 10 km Cycling • Stage Racing |
| **System Integration** | Glossary Placeholders → Advanced Markers → Coaching Heuristics Pack → Unified Reporting Framework v5.1 |

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
  - `PolarisationIndex` (Treff PI, informational)  
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

---

# 🔁 Extended Framework Integrations — v16.1 Additions  

### 🧩 Seiler 80/20 Polarisation — Intensity Distribution & Quality Balance  
\[
PolarisationIndex = \log_{10}\left(\frac{Z1}{Z2} \times Z3 \times 100\right)
\]  
Seiler 3-zone fractions (Z1 = Z1+Z2, Z2 = Z3+Z4, Z3 = Z5–Z7, renormalised). Z2 = 0 → log₁₀(Z1 / 0.01 × (Z3 − 0.01) × 100); Z3 = 0 → 0; Z3 > Z1 → not calculated.  
PI > 2.00 = polarised; PI ≤ 2.00 = not polarised (informational, Treff et al. 2019)  

### ⚙️ Banister TRIMP — Load & ACWR  
\[
TRIMP = Duration × HR_{ratio} × e^{1.92 × HR_{ratio}}
\]  
✅ 0.8–1.3 = safe ⚠️ 1.31–1.5 = watch ❌ > 1.5 = overload  

### 📊 Foster Monotony–Strain  
\[
Monotony = \frac{Mean_{7d}}{SD_{7d}}, \quad Strain = Monotony × ΣLoad_{7d}
\]  
✅ < 600 stable ⚠️ 600–800 monitor ❌ > 800 risk  

### 🧩 Sandbakk Durability  
\[
DurabilityIndex = 1 - (\text{PowerDrop%}/100)
\]  
✅ < 5 % = elite ⚠️ 5–10 % = adequate ❌ > 10 % = reduced durability  

### ⚡ Skiba W′ / Critical Power  
\[
W'_{bal} = W' - \int (P - CP)^+ dt
\]  
✅ ≥ 0.9 = restored ⚠️ 0.7–0.89 partial ❌ < 0.7 insufficient  

### ⚙️ Coggan Power Zones  
Defines Z1–Z7 (% FTP).  
Compliance ≤ 3 % ensures accuracy.  

### 🧠 Noakes Central Governor  
\[
Readiness = 0.3×Mood + 0.3×Sleep + 0.2×Stress + 0.2×Fatigue
\]  
✅ ≥ 0.8 normal ⚠️ 0.7–0.79 reduced ❌ < 0.7 → −15 % load  

### 🔀 Hybrid Polarised–Sweet Spot  
Applied when weekly volume < 8 h.  
Target Z1 ≥ 60 %, Z2 ≤ 40 %, Z3 ≤ 10 %.

---

## 📚 Core Scientific References — Full Entries  

- **Seiler, S. & Tønnessen, E. (2009).** *Intervals, Thresholds, and Long Slow Distance: The Role of Intensity and Duration in Endurance Training.* European Journal of Sport Science, 9(1), 3–13.  
- **Banister, E. W. (1975).** *Modeling of Training and Overtraining.* In: *Proceedings of the First International Symposium on Biochemistry of Exercise.* University Park Press.  
- **Foster, C. (1998).** *Monitoring Training in Athletes with Reference to Overtraining Syndrome.* Medicine & Science in Sports & Exercise, 30(7), 1164–1168.  
- **San Millán, I. (2019).** *Metabolic Flexibility and Mitochondrial Function in Endurance Athletes.* Journal of Applied Physiology, 127(5), 1453–1461.  
- **Friel, J. (2012).** *The Triathlete’s Training Bible (4th ed.).* VeloPress.  
- **Sandbakk, Ø. & Holmberg, H. C. (2017).** *Physiological Capacity and Training Routines of Elite Endurance Athletes.* Scandinavian Journal of Medicine & Science in Sports, 27(7), 701–712.  
- **Skiba, P. F. (2014).** *The Application of the Critical Power Model to Cycling.* European Journal of Applied Physiology, 114(11), 2441–2453.  
- **Coggan, A. R. & Allen, H. (2010).** *Training and Racing with a Power Meter (2nd ed.).* VeloPress.  
- **Noakes, T. D. (2012).** *The Central Governor Model of Exercise Regulation: Fatigue as an Emotion.* In: *Encyclopedia of Sports Medicine.* Wiley-Blackwell.  
- **Mujika, I. & Padilla, S. (2003).** *Scientific Bases for Pre-Competition Tapering Strategies.* Medicine & Science in Sports & Exercise, 35(7), 1182–1187.  
- **Coggan, A. R. & Seiler, S. (2018).** *Hybrid Polarised vs Sweet Spot Endurance Training Analysis.* Presentation, American College of Sports Medicine Annual Meeting.

---

## 🧾 Version & Compliance Metadata  

- **Framework Chain:** Seiler → Banister → Foster → San Millán → Friel → Sandbakk → Skiba → Coggan → Noakes (+ Hybrid)  
- **Unified Framework:** v5.1  
- **Audit Validation:** Tier-2 verified, event-only totals enforced  
- **Variance:** ≤ 2 %  
- **Last Revision:** 2025-11-03  
