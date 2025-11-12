---
title: Unified Reporting Framework v5.1 (Aligned Schema)
version: v16.13-EOD-003
authors: Seiler | San Millán | Friel | Banister | Foster | Coggan | McGregor | Laursen | Marcora | Stellingwerff | Millet | Kiely
scope: Weekly | Calendar | Season | Executive Summary
integrity: verified
last_updated: 2025-11-04
audit_hash: auto
---

# 🧾 Unified Reporting Framework — **v5.1 (Aligned Schema)**  
**Spec Alignment:** Seiler | San Millán | Friel | Banister | Foster | Coggan | McGregor | Laursen | Marcora | Stellingwerff | Millet | Kiely  
**Patch ID:** v16.13-EOD-003  
**Scope:** Weekly | Calendar | Season | Executive Summary  

---

## ⚙️ Purpose  
A unified Markdown-based reporting schema applicable to all reporting windows.  
Replaces prior standalone templates and governs post-audit data rendering from **Tier 2 → Render** stage.  

Applies to:  
- **Weekly Report (Rolling 7d window)** — for short-term load and recovery tracking.  
- **Calendar Week Report (Mon–Sun)** — for structured block or phase summaries.  
- **Season Report (≥ 42 days)** — for macro-cycle or periodised analysis.  
- **Executive Summary** — for multi-report aggregation.  

Refer to the **Report Triggers Clarification** section for operational definitions.  

---

## 🧱 Structure Overview  
Every report inherits the following structure:  
1. **Header** — athlete metadata, discipline, audit status, and Friel age modifiers.  
2. **Key Stats** — load, recovery, intensity distribution, and core metrics.  
3. **Event Log (Merged Daily View)** — validated merged sessions post Tier-2 audit.  
 3.1 **Event Cards and Relationship Model** — 1:1 mapping between Event Log rows and rendered Event Cards.  
4. **Training Quality Section** — Zone distribution, endurance–quality ratio, and HIIT density index (Seiler, Laursen).  
5. **Efficiency & Adaptation Section** — advanced markers (Benchmark, Specificity, Consistency, Durability).  
6. **Metabolic Efficiency Section** — substrate oxidation, fuel balance, and efficiency metrics (San Millán, Stellingwerff).  
7. **Recovery & Wellness Section** — HRV, RestHR, Sleep, Mood, Stress, RPE bias (Marcora).  
8. **Load Balance Section (Banister / Foster)** — ACWR, Monotony, Strain, TSB integration (McGregor).  
9. **Performance Insights** — automated interpretation logic (Seiler, San Millán, Friel, Kiely).  
10. **Actions** — adaptive next steps (3–5 max) referencing all coaching models.  

---

## 1. 🧭 Header  
```
Athlete: {athleteName|You}
Discipline: {discipline}
Scope: {reportType}
Window: {start_date} → {end_date}
Audit: {auditStatus} | Integrity: {integrityFlag}
```
- Timezone derived from athlete profile.  
- Audit must equal “Tier-2 ✅ Pass” before render. 
- TSS, CTL, ATL → sourced directly from Intervals.icu API; not recomputed locally.

> **Note:** Age-based load and recovery modifiers (Friel reference) are applied only when your age is known.  
> If not provided, a default value of **35 years** is assumed (no adjustment applied).  

---

### 🧩 Context Additions — Runtime Alignment

| Key | Tier | Type | Description |
|:--|:--|:--|:--|
| `tier1_eventTotals` | Tier-1 | dict | Canonical event totals (`hours`, `tss`) sourced directly from Intervals.icu. |
| `load_metrics` | Tier-1 | dict | CTL / ATL / TSB values merged from wellness data for renderer use. |
| `outliers` | Tier-1 | list[dict] | Detected TSS outliers ± 1.5 σ (`{date, event, issue, obs}`). |
| `zone_dist_power`, `zone_dist_hr`, `zone_dist_pace` | Tier-1 | dict | Percent zone distributions expanded from arrays. |
| `recovery_flag` | Tier-2 | str | Adaptive recovery classification from HRV↔Load correlation (`adaptive`, `neutral`, `poor`). |

---

## 2. 📊 Key Stats  
| Metric | Value | Δ | Status |
|:--|--:|:--:|:--:|
| Volume (h) | {{ (context["tier1_eventTotals"]["hours"] if "tier1_eventTotals" in context else 0) | round(2) }} | {{ ΔHours | round(1) }} | — |
| Load (TSS) | {{ (context["tier1_eventTotals"]["tss"] if "tier1_eventTotals" in context else 0) | round(0) }} | {{ ΔTss | round(0) }} | — |
| Avg IF | {{ context.get("avgIF", 0) | round(2) }} | — | — |
| ACWR | {acwr:.2f} | — | {acwrFlag} |
| Monotony | {monotony:.2f} | — | {monotonyFlag} |
| Strain | {strain:.0f} | — | — |
| Recovery Index | {recoveryIndex:.2f} | — | {recoveryStatus} |
| Fat Ox Index | {fatOxidationIndexRaw:.2f} | — | {fatOxidationIndexEval} |
| Polarisation Index | {polarisationIndex:.2f} | — | {polarisationFlag} |
| Durability Index | {durabilityIndex:.2f} | — | {durabilityFlag} |
| Benchmark Index | {benchmarkIndex:.2f} | {ΔBenchmark:.2f} | {benchmarkFlag} |
| Specificity Index | {specificityIndex:.2f} | — | {specificityFlag} |
| Consistency Index | {consistencyIndex:.2f} | — | {consistencyFlag} |
| Normalised Power (NP) | {np:.0f} | — | — |
| Intensity Factor (IF) | {if:.2f} | — | — |

> **Reference:** Coggan Power Metrics — NP, IF, and TSS definitions integrated from Dr. Andrew Coggan’s framework.  

---

## 3. 📅 Event Log
Displays validated, daily sessions after the Event Completeness Rule.

| Date | Discipline | Duration (h) | Load (TSS) | RPE | IF | Feel | Device • Source |
|:--|:--|--:|--:|--:|--:|:--|:--|
| {rows from weeklyEventLogBlock} |

**Render logic:**  
- One row = one calendar day.  
## Duration = context["eventTotals"]["hours"]
## Load = Σ icu_training_load.  
- RPE = max per day; Feel = min per day; IF = mean.  
- Appears only when `reportType == "weekly"`.  

---

### 3.1 Event Cards and Relationship Model  
Each Event Card = rendered instance of a validated Event Log row (1 : 1 mapping).  
Ensures transparent data→render chain for audit traceability.  

**Chain:** API → Tier-2 Audit → Canonical Event Table → Event Card Renderer → Report Section

Rules:  
1. Each card maps uniquely to a single activity_id.
2. No aggregation or daily merging permitted.
3. Card values must equal validated event fields: date, type, duration, TSS, IF, RPE, feel, device_name, source.
4. Card count must equal event row count; mismatch → ❌ Renderer Halt.
5. Visual grouping allowed only for layout purposes, not data combination.
6. Missing provenance → Unknown • Manual.
7. Device provenance must appear consistently at both event and card levels.

---

## 4. 🧩 Training Quality Section  
| Zone | Volume (h) | % Total | Notes |
|:--|--:|--:|:--|
| Z1–Z2 (Endurance) | {z12h:.1f} | {z12pct:.0f}% | Target ≥ 70 % |
| Z3–Z5 (Quality) | {z35h:.1f} | {z35pct:.0f}% | Limit ≤ 20 % |
| Fat-Ox Sessions | {z2sessions} | — | {fatOxidationQualityNote} |

**Reference:** Seiler 80/20 distribution applied for aerobic durability.  
**Addition:** Laursen HIIT Integration — “High-Intensity Session Density Index (HIDI)” computed as Σ(Z4–Z5 sessions)/7.  

---

## 5. 🔬 Efficiency & Adaptation Section  
| Marker | Current | Prev | Δ | Status |
|:--|--:|--:|--:|:--:|
| Benchmark Index | {benchmarkIndex:.2f} | {benchmarkPrev:.2f} | {ΔBenchmark:.2f} | {benchmarkFlag} |
| Specificity Index | {specificityIndex:.2f} | {specificPrev:.2f} | {ΔSpecificity:.2f} | {specificityFlag} |
| Consistency Index | {consistencyIndex:.2f} | {consistencyPrev:.2f} | {ΔConsistency:.2f} | {consistencyFlag} |
| Recovery Index | {recoveryIndex:.2f} | {recoveryPrev:.2f} | {ΔRecovery:.2f} | {recoveryStatus} |
| Durability Index | {durabilityIndex:.2f} | {durabilityPrev:.2f} | {ΔDurability:.2f} | — |

> **References:**  
> - Friel Periodisation Model (Benchmark/Specificity).  
> - Millet Durability Framework for fatigue resistance.  
> - McGregor TSB integration for load adaptation.  

---

## 6. 🔋 Metabolic Efficiency Section  
| Metric | Value | Units | Interpretation |
|:--|--:|:--:|:--|
| Fat Oxidation Index (FOxI) | {fat_oxidation_index:.2f} | % | % of total energy from fat oxidation |
| Carb Use Rate (CUR) | {carb_use_rate:.1f} | g/h | Carbohydrate oxidation rate |
| Glycogen Ratio (GR) | {glycogen_ratio:.2f} | — | CUR / FOxI |
| Metabolic Efficiency Score (MES) | {metabolic_efficiency_score:.1f} | % | 100 × FOxI / (FOxI + CUR) |
| Substrate Efficiency Balance (Stellingwerff Index) | {fuel_efficiency_ratio:.2f} | — | Carb-to-fat utilisation balance |

**Interpretation Guide**  
- FOxI ≥ 65 % → strong fat oxidation capacity.  
- CUR ≤ 80 g/h → balanced substrate usage.  
- MES > 50 % → efficient endurance metabolism.  
- GR > 1.5 → carb-biased adaptation.  
- Stellingwerff Index > 1.2 → energy balance optimal; < 0.9 → fuel deficit risk.  

---

## 7. 💓 Recovery & Wellness Section  
| Metric | Avg | Trend | Status |
|:--|--:|--:|:--:|
| HRV | {hrv} | {Δhrv} | {hrvFlag} |
| RestHR | {restingHr} | {ΔrestHr} | — |
| Sleep (h) | {sleepH} | {Δsleep} | — |
| Mood / Motivation | {mood}/{motivation} | — | — |
| Stress / Fatigue | {stress}/{fatigue} | — | — |
| RPE/Perceptual Load Mapping (Marcora Index) | {rpe_bias:.2f} | — | {rpeBiasFlag} |

> **References:**  
> - Marcora Perception of Effort model for psychophysiological fatigue.  
> - Integration with Recovery Index for total perceived strain.  

---

## 8. ⚖️ Load Balance (Banister / Foster)  
| Marker | Current | 7-Day Δ | Status |
|:--|--:|--:|:--:|
| ACWR | {acwr:.2f} | {ΔAcwr:.2f} | {acwrFlag} |
| Monotony | {monotony:.2f} | — | {monotonyFlag} |
| Strain | {strain:.0f} | — | — |

> **References:**  
> - Banister TRIMP model for acute/chronic load ratios.  
> - Foster Load Variability index.  
> - McGregor integration for TSB correlation.  

---

## 9. 🧠 Performance Insights (Automated)  
| Model | Metric(s) | Status | Interpretation |
|:--|:--|:--:|:--|
| Seiler | Polarisation {polarisationIndex:.2f} | {polarisationFlag} | Endurance distribution |
| San Millán | FatOx {fatOxidationIndex:.2f} / Decouple {avgDecoupling:.1f}% | {fatOxidationIndexEval} | Mitochondrial efficiency |
| Friel | Benchmark Δ {ΔBenchmark:.2f} / Specificity Δ {ΔSpecificity:.2f} | {frielFlag} | Phase progression |
| Banister / Foster | ACWR {acwr:.2f} / Monotony {monotony:.2f} | {banisterFlag} | Load variability |
| Kiely | Adaptive Load Variance {adaptive_variance:.2f} | {adaptationFlag} | Load adaptation stability |

---

## 10. 🪜 Actions (≤ 5)  
1. Maintain ≥ 70 % Z1–Z2 volume (**Seiler 80/20**).  
2. Keep **FOxI ≥ 0.80** and **Decoupling ≤ 5 %** (**San Millán Zone 2**).  
3. Integrate **1–2 HIIT sessions/week** (**Laursen protocol**) maintaining HIDI < 0.35.  
4. Track **RPE bias < 1.2** to ensure perceived effort aligns with objective load (**Marcora alignment**).  
5. Validate **Fuel Efficiency (Stellingwerff)** during endurance sessions and refuel if Index < 1.0.  

---

### Version and Compliance  
Unified Reporting Framework **v5.1 (current active schema)** — ruleset `v16.13-EOD-003`.  
All icons 🧭 📊 📅 🧩 🔬 🔋 💓 ⚖️ 🧠 🪜 must render.  
Audit variance limit ≤ 1 %.  
All twelve coaching frameworks covered.
