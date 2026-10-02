# 🚦 Coaching Cheat Sheet  
*Quick thresholds for classifying training load, recovery, and quality*  

🔗 Related files:  
- See **Glossary & Placeholders** for report placeholders.  
- See **Advanced Markers** for definitions and thresholds.  
- See **Coaching Heuristics Pack** for full reasoning and coaching context.  

# Coaching Cheat Sheet (v16.17)

## 1. Overview
Unified interpretation and reporting framework for endurance performance metrics. Designed for alignment with Tier-0 through Tier-2 audit pipelines and ChatGPT Coach.

---

## 2. Key Training Load Metrics

| Metric | Formula | Ideal Range | Notes |
|:--|:--|:--|:--|
| **TSS (Training Stress Score)** | Provided directly by Intervals.icu | — | No recomputation required |
| **CTL (Chronic Training Load)** | 42-day exponentially weighted TSS average | — | Reflects long-term load |
| **ATL (Acute Training Load)** | 7-day exponentially weighted TSS average | — | Reflects short-term fatigue |
| **TSB (Training Stress Balance)** | `CTL - ATL` | — | Positive = freshness; Negative = fatigue |
| **ACWR (Acute:Chronic Workload Ratio)** | `ATL / CTL` | 0.8–1.3 | Monitors short-term load relative to capacity |

---

## 3. Load Health Metrics

| Metric | Formula | Ideal Range | Interpretation |
|:--|:--|:--|:--|
| **Monotony** | Mean(Load) / SD(Load) | < 2.0 | Training variety and load variation |
| **Strain** | Monotony × Total Load | Contextual | Measures combined stress magnitude |
| **Load Status** | Derived from ACWR, Monotony, and Strain | — | Categorizes adaptive state |

---

## 4. Polarization & Intensity Distribution

| Metric | Formula | Range | Target |
|:--|:--|:--|:--|
| **Polarisation (Seiler 3-zone)** | % of time in Seiler Z1; Seiler Z1 = Z1+Z2, Z2 = Z3+Z4, Z3 = Z5–Z7 (renormalised to 1) | 0–100 % | Type from zone order (Intervals.icu rules, in order): hiit, polarised, base, pyramidal, threshold, else unique. Informational, no good/bad band. Power-based; Ride HR zones only when no power |
| **Polarization Index (PI)** | Treff 2019: `log10((Z1 / Z2) × Z3 × 100)` on Seiler 3-zone fractions. Z2 = 0 → `log10(Z1 / 0.01 × (Z3 − 0.01) × 100)`; Z3 = 0 → 0; Z3 > Z1 → not calculated | — | > 2.00 = polarised; ≤ 2.00 = not polarised (informational). Power-based; Ride HR only when no power. Fused (dominant sport) and combined (all endurance, lower confidence) use the same index and cut-off |
| **Zone Distribution** | Based on Power or HR zones | — | Endurance ≥ 60 % Z1–Z2 |
| **SS Zone Fraction (Sweet Spot)** | Own % of the Z1–Z7 total; overlaps Z3/Z4, not added to the total (Z1–Z7 = 100 %) | 0–25 % | Overuse reduces recovery |

---

## 5. FatOx & Efficiency Metrics

| Metric | Formula | Ideal Range | Notes |
|:--|:--|:--|:--|
| **FatOx Efficiency (FOxI)** | `Joules / kcal × aerobic_fraction` | 0.7–1.3 | Estimates aerobic efficiency |
| **Efficiency Factor (EF)** | `NP / HR` | Contextual | Tracks aerobic endurance improvement |
| **Decoupling (%)** | `|HR drift|` | < 5 % | Stability of effort |

---

## 6. Recovery & Wellness Integration

| Metric | Formula | Ideal Range | Notes |
|:--|:--|:--|:--|
| **HRV Trend (7-day)** | `%Δ HRV mean` | — | +ve trend = improved recovery |
| **RestHR Trend** | `%Δ RestHR mean` | — | Rising = fatigue |
| **Sleep Quality Index** | `(SleepScore × (SleepSecs / 8h)) / 100` | 0–1 | Proxy for sleep recovery potential |
| **Mood, Stress, Motivation** | Scaled 1–5 | — | Used in qualitative load state estimation |

---

## 7. Durability & Fatigue Resistance *(Coach-only interpretive)*

| Metric | Formula | Range | Interpretation |
|:--|:--|:--|:--|
| **Durability Index (DI)** | `(LastHourPower / FirstHourPower)` | 0.8–1.0 | Stability of power over duration |
| **Power Decay Rate** | `ΔPower / ΔTime` | — | Slope of fatigue curve |
| **Heart Rate Stability** | `ΔHR / ΔPower` | < 0.1 | Cardiovascular stability marker |

---

## 8. Zone Distribution Reference

| Zone | % of Session Time | Training Effect |
|:--|:--:|:--|
| Z1 | 30–60 % | Aerobic base, recovery |
| Z2 | 25–40 % | Aerobic endurance |
| Z3 | 10–20 % | Tempo (Sweet Spot overlaps Z3/Z4) |
| Z4 | 5–10 % | Threshold development |
| Z5–Z7 | < 5 % | VO₂ / anaerobic capacity |

---

## 9. Taper & Recovery Guidance *(Coach-only interpretive)*

| Phase | Definition | Load Ratio (vs Peak) | Guidance |
|:--|:--|:--:|:--|
| **Base** | Aerobic capacity build | 0.6–0.8 | Emphasize Z2 volume |
| **Build** | Threshold & fatigue resistance | 0.8–1.0 | Introduce Z3–Z4 |
| **Peak** | Race-specific intensity | 0.9–1.1 | Sharpen VO₂ / anaerobic |
| **Taper** | Pre-event load reduction | 0.5–0.7 | Maintain intensity, cut volume |
| **Recovery** | Post-event regeneration | < 0.5 | Active recovery, HRV ↑ expected |

---

## 10. 🧭 Training Quality & Load Management

### Training Quality Index (TQI)

| Metric | Formula | Target Range | Status |
|:--|:--|:--|:--|
| TQI | `(TSS / Hours) × FOxI × (Z2% + Z3%)` | 100–180 | Session efficiency and pacing execution |
| FOxI | `FatOxEfficiency / 100` | 0.8–1.2 | Fat oxidation efficiency normalized factor |
| Z2% + Z3% | Proportion of aerobic & tempo zone time | ≥ 60 % | Optimal endurance distribution |

**Interpretation:**
- `< 80`: Under-paced or incomplete session.  
- `80–120`: Normal endurance session.  
- `120–180`: High-quality aerobic or race-specific load.  
- `> 180`: Over-reaching or pacing error; review plan.

## 11. 🧩 Periodisation Framework

| Cycle Type | Duration | Focus | Load Pattern | Typical Distribution | Notes |
|:--|:--:|:--|:--|:--|:--|
| **Microcycle** | 7 days | Specific workouts | 3:1 (Load:Recovery) | 3 loading + 1 recovery day | Used in short-term planning |
| **Mesocycle** | 3–5 weeks | Performance block | 2–3:1 (Load:Recovery) | 2–3 build weeks + 1 deload | Aligns with ACWR monitoring |
| **Macrocycle** | 12–24 weeks | Seasonal plan | 3–4 Mesocycles | Base → Build → Peak → Taper | Reflects annual plan progression |
| **Transition** | 2–4 weeks | Regeneration / Rebuild | Reduced | Aerobic only, HRV ↑ | Optional between seasons |

**Coach Use Guidance**
- Maintain *ACWR ≤ 1.3* across cycles.  
- Use *TSB ≥ 0* to schedule performance tests or events.  
- Taper phase reduces ATL by 30–50 % while maintaining intensity.  
- Base → Build → Peak → Taper → Transition forms one complete macrocycle.

---

## 12. 🧠 Adaptive Recommendations Logic (ChatGPT Coach Layer)

| State Detected | AI Guidance Summary |
|:--|:--|
| **Overload** | Prioritize recovery; monitor HRV and fatigue markers. |
| **Underload** | Introduce moderate volume block; focus on Z2. |
| **High Quality / Excellent** | Maintain plan; verify sleep and HR stability. |
| **Low Quality** | Review pacing, intensity control, and external stressors. |
| **Fatigued / Poor Recovery** | Delay next HI session; increase recovery frequency. |

---

## 13. 📘 References
- Friel, J. *The Cyclist’s Training Bible.* 2022 Edition.  
- Bannister, E. “Modeling Human Performance and Fatigue.” *Eur J Appl Physiol*, 1975.  
- Impellizzeri et al. “Use of RPE and Load Metrics in Endurance Training.” *Sports Med*, 2019.  
- Seiler, S. *Int J Sports Physiol Perform*, 2010 (80/20 counts sessions, not minutes). https://pubmed.ncbi.nlm.nih.gov/20861519/  
- Stöggl & Sperlich. *Front Physiol*, 2015. https://pubmed.ncbi.nlm.nih.gov/26578968/  
- Treff et al. *Front Physiol* 10:707, 2019 (Polarization Index). https://pubmed.ncbi.nlm.nih.gov/31249533/  
- Intervals.icu Knowledge Base and API Schema Reference (2024).  
- ChatGPT Coach Training State Heuristic Model (v16.17).

---

### Load Management Rules

| Metric | Formula | Reference Range | Interpretation |
|:--|:--|:--|:--|
| **ACWR (Acute : Chronic Workload Ratio)** | `ATL / CTL` | 0.8–1.3 | Balance zone; >1.5 = risk of over-reaching |
| **Monotony** | `Mean(Load) / SD(Load)` | < 2.0 | Higher = less variety, ↑ injury risk |
| **Strain** | `Monotony × Total Load` | — | Quantifies combined stress from volume + repetition |
| **Load Status** | derived | — | “Optimal”, “High Risk”, “Under-reached”, or “Recovery” based on above three |

**Load State Table**

| ACWR | Monotony | Strain | Load Status |
|:--:|:--:|:--:|:--|
| 0.8–1.3 | < 2.0 | Moderate | ✅ Optimal |
| > 1.5 | > 2.0 | High | ⚠ Overload / Injury Risk |
| < 0.8 | — | Low | ⬇ Underload / Maintenance |
| 1.0–1.2 & Strain ↓ | < 1.5 | Low-Moderate | 💤 Recovery |

---

### Metabolic Adaptation Metrics

| Metric | Range | Meaning |
|:--|:--:|:--|
| **CUR (Carbohydrate Utilisation Ratio)** | 30–80 | Balanced substrate use |
| **GR (Glucose Ratio)** | 0.5–2.0 | >2 = glycolytic bias |
| **MES (Metabolic Efficiency Score)** | 20–100 | >20 = endurance economy |
| **StressTolerance** | 2–8 | Sustainable strain capacity |
| **ZQI (Zone Quality Index)** | Informational | % of time in Seiler zone 3 (Z5–Z7, above LT2 ≈ FTP). No good/bad bands (none are published); for reference, elites spend ~1–8 % of time above LT2 by time in zone, polarised blocks ~15–20 % by session goal |

### AI Load Summary Logic

| ACWR Range | Classification | Example Output |
|:--:|:--|:--|
| > 1.5 | 🚨 High Load / Overreaching | “🚨 High Load / Overreaching — 620 TSS over 12 h (ACWR 1.56)” |
| 0.8–1.5 | ⚖️ Stable / Productive | “⚖️ Stable / Productive — 480 TSS / 10 h (ACWR 1.10)” |
| < 0.8 | 🟢 Recovery / Underload | “🟢 Recovery / Underload — 300 TSS / 8 h (ACWR 0.72)” |

---

### Recovery & Readiness Indices

| Metric | Formula | Scale | Notes |
|:--|:--|:--|:--|
| **Recovery Index (RI)** | `(HRV × Sleep × RestHR_baseline_ratio)` | 0–1 | Global readiness composite |
| **Sleep Index** | `(SleepScore × (SleepSecs / 8 h)) / 100` | 0–1 | Proxy for recovery potential |
| **RestHR Deviation** | `(RestHR − Baseline) / Baseline` | ± 10 % | > +10 % → fatigue; < −10 % → super-compensation |
| **HRV Trend (7-day)** | `%Δ HRV mean` | — | ↓ persistent = maladaptation; ↑ = resilience |

**Readiness State Table**

| Recovery Index | Interpretation |
|:--:|:--|
| > 0.8 | Excellent readiness |
| 0.6–0.8 | Normal / Maintain |
| 0.4–0.6 | Fatigued — adjust load |
| < 0.4 | Poor recovery — rest day |

---

### Age-Adjusted Load and Recovery Modifiers (Friel Reference)

| Age | ATL Multiplier | ACWR Cap | Recovery Frequency | Notes |
|:--|:--|:--|:--|:--|
| < 35 | 1.00 | 1.5 | 4-week | Standard progression |
| 35–49 | 0.95 | 1.4 | 3–4-week | Slight recovery emphasis |
| 50–59 | 0.90 | 1.3 | 3-week | Reduce HI frequency by 25 % |
| 60–69 | 0.85 | 1.2 | 2-week | Maintain intensity, lower volume |
| ≥ 70 | 0.75 | 1.1 | 2-week | Prioritize recovery, add aerobic maintenance |

---

### Training Quality State Labels *(ChatGPT Coach interpretive layer)*

| TQI Range | Label | Action |
|:--:|:--|:--|
| < 80 | Low Quality | Reassess pacing / fatigue |
| 80–120 | Solid | Maintain plan |
| 120–160 | High Quality | Progress load gradually |
| 160–200 | Excellent | Maintain within recovery envelope |
| > 200 | Overload | Insert rest or taper |

---

### Performance Zone Crosswalk

| Zone | Physiological Focus | Fatigue Cost | Adaptation Pathway |
|:--|:--|:--|:--|
| Z1 | Active recovery / base | Low | Mitochondrial density |
| Z2 | Endurance capacity | Moderate | Aerobic enzyme development |
| Z3 | Tempo / muscular endurance | High | Glycogen sparing, fatigue resistance |
| Z4 | Threshold | Very High | Lactate tolerance |
| Z5 | VO₂max | Extreme | Cardiorespiratory capacity |
| Z6–Z7 | Anaerobic / neuromuscular | Maximal | Power and speed sharpening |

---

### Coach Action Framework

| State | Primary Focus | Example Interventions |
|:--|:--|:--|
| **Overload** | Recovery | Add rest day, reduce intensity |
| **Optimal** | Progression | Maintain volume, add stimulus |
| **Underload** | Activation | Add moderate-intensity block |
| **Fatigued** | Restoration | Extend low-intensity duration |
| **Excellent** | Maintenance | Sustain pattern, monitor HRV |

---
