# 📊 Intervals.icu GPT Coaching Framework v16.1  

A deterministic, rules-based audit and reporting engine for [Intervals.icu](https://intervals.icu).  
It combines live athlete data, evidence-based coaching heuristics, and an automated multi-tier validation chain to generate fully compliant endurance training reports.  
https://github.com/revo2wheels/intervalsicugptcoach-public/blob/main/README.md
---

## 🧭 About  

The **Intervals.icu GPT Coach** transforms athlete data into reproducible, validated insights.  
It operates as an autonomous audit and analytics layer built on the **Unified Reporting Framework v5.1**, ensuring integrity, transparency, and traceability for endurance coaching decisions.  

All computations use **event-only totals** and enforce <2 % variance across all metrics.  
No data smoothing, interpolation, or load-based hour conversions are ever applied.  

---

## 🧩 Core Function  

1. Fetch live activities and wellness data from Intervals.icu.  
2. Validate integrity, completeness, and discipline consistency.  
3. Compute derived metrics (ACWR, Monotony, Strain, Polarisation, Durability Index, FatOxidationIndex, W′, BenchmarkIndex, Subjective Readiness).  
4. Run compliance checks through a multi-tier audit chain.  
5. Render structured 8-section reports via the Unified Reporting Framework.  

---

## 🧱 Coaching Framework Stack  

The system operates on **ten integrated frameworks**, defined in `all-modules.md` and loaded dynamically on initialization:

| Framework | Purpose |
|:--|:--|
| **Glossary & Placeholders** | Defines all report tokens, metrics, and variable placeholders used across audits and renderers. |
| **Coaching Cheat Sheet** | Quick-reference table of thresholds for load, recovery, and training quality classifications. |
| **Coaching Heuristics Pack** | Deep decision logic covering phase-based load tolerance, recovery windows, and periodisation rules (Seiler, Foster, Banister, Friel). |
| **Advanced Marker Reference** | Mathematical and physiological definitions for derived metrics: ACWR, Monotony, Strain, Polarisation, Durability Index, Recovery Index, FatOxidationIndex, W′, BenchmarkIndex, Subjective Readiness, HybridMode. |
| **Coach Profile** | Frameworks applied, theoretical background, and sport-specific expertise model (triathlon, cycling, running). |
| **Unified Reporting Framework v5.1** | Standardized reporting architecture ensuring consistency across weekly, seasonal, and event-level reports. |
| **Sandbakk Durability** | Fatigue resistance, long-duration power drop analysis, durability trend. |
| **Skiba W′ / Critical Power** | Anaerobic reserve, interval W′ expenditure, and recovery monitoring. |
| **Coggan Power Zones** | Z1–Z7 compliance, polarisation distribution, and Hybrid mode validation. |
| **Noakes Central Governor** | Integrates subjective readiness (mood, fatigue, sleep, stress) into adaptive load modulation. |

Together these frameworks create a **closed-loop decision system** that links raw athlete data to interpretable coaching outcomes.

---

## ⚙️ System Architecture  

Intervals.icu API
↓
Tier-0 → Tier-1 → Tier-2 (Audit Core Modules)
↓
Derived Metrics Engine
↓
Unified Reporting Framework v5.1
↓
Final Render (Text / UI v5.1)

| Component | Function | Source |
|:--|:--|:--|
| **Intervals.icu API** | Retrieves live event + wellness data | `listActivities`, `listWellness` |
| **Audit Core (Tier-0 → Tier-2)** | Validates integrity, completeness, and derived metrics | `/audit_core/*.py` |
| **Action Evaluator** | Generates adaptive recommendations | `/audit_core/tier2_actions.py` |
| **Derived Metrics Module** | Computes ACWR, Strain, Monotony, Polarisation, Recovery Index, FatOxidationIndex, DurabilityIndex, W′, BenchmarkIndex | `/audit_core/tier2_derived_metrics.py` |
| **Unified Reporting Framework v5.1** | Renders and validates full athlete reports | `/Unified Reporting Framework.md` |

---

## 🔍 Audit Chain  

| Tier | Purpose | Halt Condition |
|:--|:--|:--|
| **Tier-0 — Pre-Audit** | Fetches and verifies live data origin | Mock/cache/sandbox data detected |
| **Tier-1 — Audit Controller** | Validates dataset integrity and time variance | > 0.1 h deviation or missing discipline |
| **Tier-2 — Event Audit** | Enforces event-only totals and derived metric accuracy | Metric mismatch > 1 % |
| **Render Gate** | Generates report after auditFinal = True | Missing or invalid section in output |

All halts trigger a compliance log entry and prevent report release until resolved.

---

## 🧮 Computation Rules  

- **Totals:** Σ(event-level `moving_time`, `distance`, `icu_training_load`)  
- **Duration:** Σ(moving_time) / 3600 h  
- **Load:** Σ(icu_training_load)  
- **No interpolation** or ATL/CTL smoothing  
- **Variance gates:**  
  - Time ≤ 0.1 h  
  - Load ≤ 2 TSS  
  - Derived metrics ≤ 1 % deviation  

---

## 🧠 Core Coaching Concepts  

| Category | Key Metrics |
|:--|:--|
| **Load Management** | CTL, ATL, ACWR, Monotony, Strain, Durability Index, W′ |
| **Recovery** | HRV, Resting HR, Sleep, Recovery Index, Subjective Readiness |
| **Training Quality** | Polarisation Index, Durability Index, Quality Session Balance, FatOxidationIndex, HybridMode |
| **Periodisation** | Build → Overload → Deload → Consolidation, PhaseType, MicrocycleRecoveryWeek |
| **Event Preparation** | Taper protocols, BenchmarkIndex, race-phase sharpening |

---

## 🚦 Operational Workflow  

1. Input → Load, wellness, subjective metrics  
2. Compute → Derived markers (ACWR, Strain, Polarisation, Recovery Index, FatOxidationIndex, DurabilityIndex, W′, BenchmarkIndex, Subjective Readiness, HybridMode)  
3. Apply → Decision logic from *Heuristics Pack*  
4. Classify → Thresholds from *Cheat Sheet*  
5. Report → Full structured output validated by the *Unified Framework*  

---

## 🏋️ Supported Sports  

| Discipline | Focus Areas |
|:--|:--|
| **Triathlon** | Periodised build, overload/deload cycles, HRV readiness |
| **Cycling** | Gran Fondo, road, TT load profiles, W′, Power Zones compliance |
| **Running** | Marathon, ultra, and 10 k taper frameworks, FatOxidationIndex |

---

## ✅ Usage  

- Use **Cheat Sheet** for threshold-based assessment.  
- Use **Heuristics Pack** for phase-based decision logic.  
- Use **Glossary & Placeholders** to generate consistent report tokens.  
- Use **Advanced Marker Reference** for formula validation.  
- Review **Coach Profile** for underlying scientific methodology.  
- Monitor **DurabilityIndex, W′, FatOxidationIndex, HybridMode** in weekly/seasonal reports.  

---

## 📜 References  

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
- **Coggan, A. R. & Seiler, S. (2018).** *Hybrid Polarised vs Sweet Spot Endurance Training Analysis.* Presentation, ACSM Annual Meeting.

---

## 🔖 Versioning  

- **Ruleset:** v16.1-EOD-001  
- **Framework:** Unified Reporting Framework v5.1  
- **Audit Modules:** Tier 0 → 2 compliant  
- **Render Mode:** full · UTF-8 · icons enabled  
