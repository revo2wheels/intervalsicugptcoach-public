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

header_mode: metadata_only
header_allow_totals: false
header_allow_summary: false

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

**Render Binding:**  
- Renderer must confirm `context["render_source"] == "audit_tier2"`.  
- If absent or mismatched → ❌ Halt render.  
- No fallback narrative generation permitted.

---

## 🧱 Structure Overview  
Every report inherits the following structure:  
1. **Header** — athlete metadata, discipline, audit status, and Friel age modifiers.  
2. **Key Stats** — load, recovery, intensity distribution, and core metrics.  
3. **Event Log** — lists each activities never merged sessions post Tier-2 audit.  
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
*(Runtime variables injected into the unified report context after each tier executes.)*

| Key | Tier | Type | Description |
|:--|:--|:--|:--|
| **`tier1_eventTotals`** | Tier-1 | `dict` | Canonical event totals (`hours`, `tss`, `distance`) validated after Tier-1 dataset integrity check. Used for variance comparison. |
| **`tier2_eventTotals`** | Tier-2 | `dict` | ✅ Final enforced event totals (Σ of event-level metrics from validated dataset). Primary source for URF Key Stats section. |
| **`load_metrics`** | Tier-1 | `dict` | CTL / ATL / TSB / Form values merged from wellness feed for renderer and adaptive logic. |
| **`outliers`** | Tier-1 | `list[dict]` | Detected TSS / IF outliers ± 1.5 σ (`{date, event, metric, observed, expected}`). |
| **`zone_dist_power`**, **`zone_dist_hr`**, **`zone_dist_pace`** | Tier-2 | `dict` | Percent zone distributions expanded from normalized training zone arrays. |
| **`recovery_flag`** | Tier-2 | `str` | Adaptive recovery classification from HRV ↔ Load correlation (`adaptive`, `neutral`, `poor`). |

#### Renderer Context Binding (URF Runtime Contract)
All variables listed above are guaranteed available to the URF renderer once `auditFinal=True`.  
Tier-2 variables take precedence where overlap exists.

---

## 2. 📊 Key Stats
| Metric | Value | Δ | Status |
|:--|--:|:--:|:--:|
| Volume (h) | {{ (context.get("tier2_eventTotals", {}).get("hours", 0)) | round(2) }} | {{ ΔHours | round(1) }} | — |
| Load (TSS) | {{ (context.get("tier2_eventTotals", {}).get("tss", 0)) | round(0) }} | {{ ΔTss | round(0) }} | — |
| Distance (km) | {{ (context.get("tier2_eventTotals", {}).get("distance", 0)) | round(1) }} | — | — |
| Avg IF | {{ (context.get("tier2_eventTotals", {}).get("avg_if", 0)) | round(2) }} | — | — |
| Avg HR | {{ (context.get("tier2_eventTotals", {}).get("avg_hr", 0)) | round(0) }} | — | — |
| VO₂max | {{ (context.get("tier2_eventTotals", {}).get("vo2max", 0)) | round(1) }} | — | — |
| ACWR | {{ acwr | round(2) }} | — | {{ acwrFlag }} |
| Monotony | {{ monotony | round(2) }} | — | {{ monotonyFlag }} |
| Strain | {{ strain | round(0) }} | — | — |
| Recovery Index | {{ recoveryIndex | round(2) }} | — | {{ recoveryStatus }} |
| Fat Ox Index | {{ fatOxidationIndexRaw | round(2) }} | — | {{ fatOxidationIndexEval }} |
| Polarisation Index | {{ polarisationIndex | round(2) }} | — | {{ polarisationFlag }} |
| Durability Index | {{ durabilityIndex | round(2) }} | — | {{ durabilityFlag }} |
| Benchmark Index | {{ benchmarkIndex | round(2) }} | {{ ΔBenchmark | round(2) }} | {{ benchmarkFlag }} |
| Specificity Index | {{ specificityIndex | round(2) }} | — | {{ specificityFlag }} |
| Consistency Index | {{ consistencyIndex | round(2) }} | — | {{ consistencyFlag }} |
| Normalised Power (NP) | {{ np | round(0) }} | — | — |
| Intensity Factor (IF) | {{ if | round(2) }} | — | — |


> **Reference:** Coggan Power Metrics — NP, IF, and TSS definitions integrated from Dr. Andrew Coggan’s framework.  

---

## 3. 📅 Event Log
Displays validated, per-session events after the Event Completeness Rule.

| Date | Name | Duration | Load (TSS) | Distance (km) |
|:--|:--|:--|--:|--:|
| {rows from weeklyEventLogBlock} |

**Cycling Totals:** {summary_cycling.hours} h · {summary_cycling.distance} km · {summary_cycling.tss} TSS · {summary_cycling.sessions} sessions  
**All Activities:** {summary_all.hours} h · {summary_all.distance} km · {summary_all.tss} TSS · {summary_all.sessions} sessions

**Render logic:**
- `weeklyEventLogBlock` = last N validated events in the report window (Tier-2 enforced), one row per event.
- `Cycling Totals` row uses `context["summary_cycling"]` (cycling-only activities in the window).
- `All Activities` row uses `context["summary_all"]` (all activities in the window).
- Appears only when `report_type == "weekly"`.
- RPE = max per day; Feel = min per day; IF = mean.  

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

## ⚙️ Orchestration Enforcement — `orchestrate_fetch_context()`

**Purpose:** Guarantee that all required endpoints are fetched in the correct order for both ChatGPT (Worker-based) and local runs **before Tier-1 validation begins**.

### Enforcement Rules

1. **Execution Order (hard-coded):**
- /athlete/0/profile
- /athlete/0/activities_t0light ← 90-day lightweight
- /athlete/0/wellness ← 42-day wellness
- /athlete/0/activities ← 7-day full

These four endpoints **must** be executed sequentially by the ChatGPT→Worker pipeline  
(or locally via `run_tier0_pre_audit`) before Tier-1 starts.

2. **Coverage Thresholds**

- Each dataset must return ≥ 85 % of expected event coverage by date range.  
- If coverage < 85 %, the controller must retry that endpoint once.  
- If still incomplete, halt execution with `AuditHalt: Tier-0 coverage failure`.

3. **Report-Type Invariance**

- Overrides by `reportType` are **not permitted**.  
- Even `season` or `wellness` reports must include all four datasets so Tier-1 and Tier-2  
  can correlate correctly.

4. **Worker Binding**

- When invoked from ChatGPT, `loadAllRules()` exposes this orchestration map as  
  `rules['enforcement']['orchestrate_fetch_context']`.
- The ChatGPT app uses that list to call each Worker endpoint in order  
  (`profile → activities_t0light → wellness → activities`).

5. **Tier-1 Entry Gate**

- Tier-1 (`run_tier1_controller`) only executes when  
  `orchestrate_fetch_context()` returns `status: complete`.

6. **Local Runtime Mirror**

- Local Python mode (`report.py`) mirrors the same sequence using the same ruleset,  
  ensuring dual-mode parity (manifest_mode = dual).

7. **Retry & Logging**

- All retries logged under `Tier-0 Retry Sequence` in compliance logs.  
- Failures escalate to `AuditCoreHalt` and prevent renderer activation.

---

### Example `loadAllRules()` Output Snippet

```json
{
"ruleset_version": "v16.17-AUDITCORE-SYNC",
"enforcement": {
 "orchestrate_fetch_context": {
   "sequence": [
     "/athlete/0/profile",
     "/athlete/0/activities_t0light",
     "/athlete/0/wellness",
     "/athlete/0/activities"
   ],
   "coverage_threshold": 0.85,
   "retries": 1,
   "reportType_locked": true
 }
}
}
```
audit_chain_source: intervalsicugptcoach.clive-a5a.workers.dev
orchestration_mode: chained_auto

---

### Version and Compliance  
Unified Reporting Framework **v5.1 (current active schema)** — ruleset `v16.13-EOD-003`.  
All icons 🧭 📊 📅 🧩 🔬 🔋 💓 ⚖️ 🧠 🪜 must render.  
Audit variance limit ≤ 1 %.  
All twelve coaching frameworks covered.
Tier-2 verification token: {{ context.get("auditFinal", False) }}

