# 🧾 Unified Reporting Framework — v5.1 (Seiler | San Millán | Friel)

---

## ⚙️ Purpose
A unified markdown-based reporting schema for all time windows, replacing prior separate templates.  
Used for post-audit data rendering from Tier 2 → Render stage.

Applies to:
- **Weekly Report (Rolling 7d window)** — for short-term load and recovery tracking.
- **Calendar Week Report (Mon–Sun)** — for structured block or phase summaries.
- **Season Report (≥ 42 days)** — for macro-cycle or periodised analysis.
- **Executive Summary** — for multi-report aggregation.

Refer to the **Report Triggers Clarification** section below for operational definitions.

---

## 🧱 Structure Overview
Every report inherits the following structure:
1. **Header** — athlete metadata, discipline, audit status.  
2. **Key Stats** — load, recovery, intensity distribution, markers.  
3. **Training Quality Section** — Zone distribution and Fat-Oxidation performance.  
4. **Efficiency & Adaptation Section** — advanced markers (Benchmark, Specificity, Consistency).  
5. **Recovery & Wellness Section** — HRV, RestHR, Sleep, Mood, Stress.  
6. **Performance Insights** — automated interpretation logic.  
7. **Actions** — next steps (3–5 max).  

---

## 🧾 General Report Template (v5.1)

⚠️ Use only **after Audit Enforcement passes.**

Audit validation ensures:
- API count = DataFrame count.  
- Combined totals = Σ subtotals (Cycling, Running, Swimming, Other).  
- ❌ Halt if mismatch, missing discipline, or volume variance > 0.1h.  

### **Header**
```
Athlete: {id|You}
Discipline: {discipline}
Scope: {reportType}
Window: {start_date} → {end_date}
Audit: {auditStatus} | Data Integrity: {integrityFlag}
```
> **Note:** Age-based load and recovery modifiers (Friel reference) are applied only when your age is known.  
> If not provided, a default value of **35 years** is assumed (no adjustment applied).

### **Key Stats**
| Metric | Value | Trend | Status |
|:--|--:|:--:|:--:|
| Volume (h) | {totalHours} | {ΔHours} | — |
| Load (TSS) | {totalTss} | {ΔTss} | — |
| Avg IF | {avgIF:.2f} | — | — |
| ACWR | {acwr:.2f} | — | {acwrFlag} |
| Monotony | {monotony:.2f} | — | {monotonyFlag} |
| Strain | {strain:.0f} | — | — |
| Recovery Index | {recoveryIndex:.2f} | — | {recoveryStatus} |
| FatOxidation Index | {fatOxidationIndexRaw:.2f} | — | {fatOxidationIndexEval} |
| Polarisation Index | {polarisationIndex:.2f} | — | {polarisationFlag} |
| Durability Index | {durabilityIndex:.2f} | — | {durabilityFlag} |
| Benchmark Index | {benchmarkIndex:.2f} | {ΔBenchmark} | {benchmarkFlag} |
| Specificity Index | {specificityIndex:.2f} | — | {specificityFlag} |
| Consistency Index | {consistencyIndex:.2f} | — | {consistencyFlag} |

---
### **Event Log (Merged Daily View)**
Displays validated, merged daily sessions after the Event Completeness Rule.  
Visible only in weekly reports (7-day rolling or calendar-week mode).

| Date | Discipline | Duration (h) | Load (TSS) | RPE | IF | Feel |
|:--|:--|--:|--:|--:|--:|:--|
{weeklyEventLogBlock}

---

**Render Conditions**
- Source: `daily` DataFrame (merged daily dataset)
- Logic:
  - One row per calendar day
  - Sum moving_time → Duration (h)
  - Sum icu_training_load → Load (TSS)
  - RPE = max per day
  - Feel = min per day
  - IF = mean
- Round:
  - Duration → 2 decimals
  - Load → integer
- Appears **only** when `reportType == "weekly"`

---

### **Training Quality Section**
| Zone | Volume (h) | % Total | Notes |
|:--|:--|:--|:--|
| Z1–Z2 (Endurance) | {z12h:.1f} | {z12pct:.0f}% | Aim ≥ 70 % of total volume (Seiler) |
| Z3–Z5 (Quality) | {z35h:.1f} | {z35pct:.0f}% | Limit ≤ 20 % of sessions |
| Fat-Oxidation Sessions | {z2sessions} | — | {fatOxidationQualityNote} |

### **Zone 2 Fat-Oxidation Block**
| Metric | Value | Status |
|:--|--:|:--:|
| Total Z2 Hours | {totalZ2h} | — |
| Avg FatOxidationIndex | {fatOxidationIndexRaw:.2f} | {fatOxidationIndexEval} |
| Avg HR–Power Decoupling | {avgDecoupling:.1f}% | — |
| FatMax Range Validation | {fatMaxValidationNote} | ✅/⚠️/❌ |

---

### **Efficiency & Adaptation Section**
| Marker | Current | Previous | Δ | Status |
|:--|--:|--:|--:|:--:|
| Benchmark Index | {benchmarkIndex:.2f} | {benchmarkPrev:.2f} | {ΔBenchmark:.2f} | {benchmarkFlag} |
| Specificity Index | {specificityIndex:.2f} | {specificPrev:.2f} | {ΔSpecificity:.2f} | {specificityFlag} |
| Consistency Index | {consistencyIndex:.2f} | {consistencyPrev:.2f} | {ΔConsistency:.2f} | {consistencyFlag} |
| Recovery Index | {recoveryIndex:.2f} | {recoveryPrev:.2f} | {ΔRecovery:.2f} | {recoveryStatus} |

---

### **Recovery & Wellness Section**
| Metric | Avg | Trend | Status |
|:--|--:|--:|:--:|
| HRV | {hrv} | {Δhrv} | {hrvFlag} |
| RestHR | {restingHr} | {ΔrestHr} | — |
| Sleep (h) | {sleepH} | {Δsleep} | — |
| Mood / Motivation | {mood}/{motivation} | — | — |
| Stress / Fatigue | {stress}/{fatigue} | — | — |

---

### ⚖️ Load Balance (Banister / Foster Integration)

| Marker | Current | 7-Day Δ | Status |
|:--|--:|--:|:--:|
| **ACWR (Acute:Chronic Load)** | {acwr:.2f} | {ΔAcwr:.2f} | {acwrFlag} |
| **Monotony** | {monotony:.2f} | — | {monotonyFlag} |
| **Strain** | {strain:.0f} | — | — |


### **Performance Insights (Automated)**

| Model | Metric(s) | Status | Interpretation |
|:--|:--|:--:|:--|
| **Seiler** | PolarisationIndex {polarisationIndex:.2f} | {polarisationFlag} | Endurance distribution quality |
| **San Millán** | FatOx {fatOxidationIndex:.2f} / Decoupling {avgDecoupling:.1f}% | {fatOxidationIndexEval} | Mitochondrial efficiency |
| **Friel** | Benchmark Δ {ΔBenchmark:.2f} / Specificity Δ {ΔSpecificity:.2f} | {frielFlag} | Phase progression |
| **Banister / Foster** | ACWR {acwr:.2f} / Monotony {monotony:.2f} | {banisterFlag} | Load variability balance |

---

### **Actions (Max 5)**
1. Maintain ≥ 70 % Z1–Z2 volume for aerobic durability (**Seiler 80/20** alignment).  
2. Keep **FatOxidation Index ≥ 0.80** and **Decoupling ≤ 5 %** to sustain metabolic efficiency (**San Millán Zone 2**).  
3. If **Recovery Index < 0.6 and ACWR > 1.2** → reduce total load ≈ 30–40 %;  
 if **Recovery Index < 0.6 and ACWR ≤ 1.2** → reduce ≈ 10–15 % (**Friel microcycle logic**).  
4. Retest **FTP / LT1** every 6 weeks or after ≥ 3 microcycles to update Benchmarks.  
5. Validate **FatMax calibration ± 5 %** and confirm HR–Power decoupling ≤ 5 % using endurance field data.

---

## 🧭 Report Triggers Clarification

To avoid ambiguity, the following report triggers and date-window definitions are standardized:

| Term | Date Window | Description |
|:--|:--:|:--|
| **Weekly Report (Rolling 7d)** | today − 6 → today | Dynamic rolling 7-day window ending “now”; used for progress tracking. |
| **Calendar Week Report** | Monday → Sunday | Fixed ISO week; used for periodised summary blocks. |
| **Season Report** | user-defined (default 42d) | Multi-week macro analysis of block or periodisation phase. |

---

## 🧭 Version Control
**Unified Reporting Framework v5.1** — merges General, Weekly, and Season templates.  
Frameworks: **Seiler 80/20 | San Millán Fat-Oxidation | Friel Periodisation | Banister TRIMP | Foster Load Variability**.  
Validated with: Glossary, Heuristics Pack, Cheat Sheet, and Coach Profile.

---

## 🧭 Icon Legend (Reporting Sections)

| Icon | Section |
|:--|:--|
| 🧭 | Header / Metadata |
| 📊 | Key Stats |
| 📅 | Event Log |
| 🧩 | Training Quality |
| 🔋 | Fat-Oxidation Block |
| 🔬 | Efficiency & Adaptation |
| 💓 | Recovery & Wellness |
| ⚖️ | Load Balance |
| 🧠 | Performance Insights |
| 🪜 | Actions |


