# 📊 Intervals.icu GPT Coaching Framework — v16.16G

A deterministic, rules-based audit and coaching engine for Intervals.icu.  
Implements the **Unified Reporting Framework v5.1**, providing reproducible load validation, physiological audit integrity, and adaptive coaching decisions.

Supports dual execution modes:  
- **Cloud (ChatGPT)** — automated orchestration via GPT-5.  
- **Local Python Execution** — identical logic via `report.py → run_report()`.

---
## 🧭 About  

The **Intervals.icu GPT Coach** transforms athlete data into reproducible, validated insights.  
It operates as an autonomous audit and analytics layer built on the **Unified Reporting Framework v5.1**, ensuring integrity, transparency, and traceability for endurance coaching decisions.  

All computations use **event-only totals** and enforce <2 % variance across all metrics.  
No data smoothing, interpolation, or load-based hour conversions are ever applied. 

---

## ⚙️ Core Function

The **primary function** is to transform Intervals.icu athlete data into validated, auditable, and interpretable **coaching intelligence** through a deterministic Tier-structured audit and heuristic mapping layer.

**Functional Sequence:**
1. Fetch → activities, wellness, and profile data.  
2. Audit → execute Tier-0 → Tier-2 checks and tolerance validation.  
3. Compute → generate derived training, recovery, and readiness metrics.  
4. Interpret → map metrics through the Coaching Framework Stack.  
5. Render → output adaptive Markdown report and JSON data payload.

---

## ⚙️ System Architecture (Full)

| Layer | Module(s) | Function | Description |
|:--|:--|:--|:--|
| **Data Layer** | `intervals_icu__jit_plugin` | Data Acquisition | Fetches activities, wellness, and profile directly from Intervals.icu. |
| **Ruleset Layer** | `all-modules.md` | Rules & Schema | Defines audit dependencies, flow order, and validation gates. |
| **Tier Controller Layer** | `audit_core/report_controller.py` | Tier Routing | Directs Tier-0 → Tier-2 audit chain execution. |
| **Tier-0 Layer** | `tier0_pre_audit.py` | Initialization | Fetches, cleans, and validates primary data windows. |
| **Tier-1 Layer** | `tier1_controller.py` | Audit Controller | Checks dataset integrity, duplication, and total alignment. |
| **Tier-2 Layer** | `tier2_*` suite | Validation and Metrics | Executes Data Integrity, Totals, Calculation, Wellness, Derived Metrics, and Actions logic. |
| **Derived Metrics Engine** | `tier2_derived_metrics.py` | Metric Computation | Computes ACWR, Strain, Monotony, Fatigue, Recovery, Efficiency, etc. |
| **Adaptive Action Layer** | `tier2_actions.py` | Coaching Logic | Generates adaptive load/recovery/efficiency actions. |
| **Renderer Layer** | `render_unified_report.py` | Markdown Output | Builds full 10-section Unified Report from validated JSON. |
| **Coaching Logic Layer** | `coach_framework-map.md` | Heuristic Context | Links derived metrics to adaptive coaching models. |
| **Framework Stack Layer** | `coach_mapping-table.md` | Framework Integration | Maps metrics to frameworks (Seiler, Banister, Coggan, etc.). |
| **Feedback Integration** | Runtime Loop | Continuous Adaptation | Updates load and readiness patterns for next audit window. |

---

### 🧠 Architecture Flow Diagram

```mermaid
flowchart TD
    subgraph Data_Acquisition
        A1[intervals_icu__jit_plugin] --> A2[Activities / Wellness / Profile Data]
    end

    subgraph Audit_Chain
        A2 --> B1[Tier-0 Pre-Audit]
        B1 --> B2[Tier-1 Controller]
        B2 --> B3[Tier-2 Data Integrity]
        B3 --> B4[Tier-2 Event Completeness]
        B4 --> B5[Tier-2 Totals Enforcement]
        B5 --> B6[Tier-2 Calculation Integrity]
        B6 --> B7[Tier-2 Wellness Validation]
        B7 --> B8[Tier-2 Derived Metrics]
        B8 --> B9[Tier-2 Evaluate Actions]
    end

    subgraph Rendering_and_Coaching
        B9 --> C1[Render Unified Report]
        C1 --> D1[Coaching Framework Map]
        D1 --> D2[Adaptive Coaching Logic]
        D2 --> D3[Feedback Loop Integration]
    end
```
---

## 🧩 Audit Chain Summary

| Tier | Module | Function | Description |
|:--|:--|:--|:--|
| 0 | `tier0_pre_audit.py` | Pre-Audit | Fetches and validates event and wellness data. |
| 1 | `tier1_controller.py` | Controller | Checks dataset integrity and totals. |
| 2.1 | `tier2_data_integrity.py` | Data Validation | Ensures completeness and source consistency. |
| 2.2 | `tier2_event_completeness.py` | Event Alignment | Identifies rest/current days. |
| 2.3 | `tier2_enforce_event_only_totals.py` | Totals Enforcement | Verifies Σ(event) = Σ(weekly totals). |
| 2.4 | `tier2_calculation_integrity.py` | Integrity Check | Verifies distance/time/TSS variance ≤ 1%. |
| 2.5 | `tier2_wellness_validation.py` | Wellness Validation | Aligns HRV, restHR, and sleep data. |
| 2.6 | `tier2_derived_metrics.py` | Derived Metrics | Computes ACWR, Strain, Polarisation, Efficiency. |
| 2.7 | `tier2_actions.py` | Adaptive Actions | Derives next-step coaching logic. |
| Render | `render_unified_report.py` | Renderer | Builds Unified Framework v5.1 Markdown Report. |

---

## 🧮 Computation Rules

| Metric | Formula | Validation |
|:--|:--|:--|
| **ACWR** | `(7d Load / 28d Rolling Load)` | ≤ 2.0 |
| **Monotony** | `Mean Load / SD Load` | Alert > 2.0 |
| **Strain** | `Load × Monotony` | Flag > 500 |
| **Recovery Index** | `(HRV / restHR) × SleepScore` | Baseline normalized |
| **Fatigue Index** | `(7d Load / RecoveryIndex)` | Alert > 2.5 |
| **Readiness** | `(RecoveryIndex × FeelScore) / 100` | Readiness-based load gating |
| **Durability Index** | `Σ(TSS) / Power Decline` | ≥ baseline threshold |
| **Polarisation Index** | `(Z1% + Z3%) / Z2%` | Target 1.8–2.2 |
| **Consistency Index** | `Sessions Completed / Planned` | Compliance tracking |

---

## 🧱 Coaching Framework Stack

The stack integrates **analytical**, **heuristic**, and **behavioral** logic for multi-framework adaptive decision making.

| Layer | Function | Key File |
|:--|:--|:--|
| Tier Engine | Audit Validation | `audit_core/` |
| Derived Metrics | Metric Computation | `tier2_derived_metrics.py` |
| Heuristic Mapping | Rule-based Context | `coach_framework-map.md` |
| Coaching Models | Scientific Foundations | See below |
| Renderer | Markdown Generation | `render_unified_report.py` |
| Feedback Loop | State Adaptation | `runtime/feedback_controller.py` |

---

## 🧭 Coach Framework Model Reference (from `coach_framework-map.md`)

| Model Reference | Framework Link | Metric Source | Output Type | Coaching Role |
|:--|:--|:--|:--|:--|
| **Seiler Polarisation Model** | Polarisation Framework | Zone distribution (Z1–Z3%) | Polarisation Ratio | Intensity distribution validation |
| **Banister Fitness-Fatigue Model** | Load Adaptation | ATL, CTL, TSB | Training Load Model | Predicts adaptation vs fatigue |
| **Coggan Power-Duration Model** | Efficiency Framework | FTP, Power Curve | Efficiency Factor | Tracks metabolic endurance |
| **Foster Overtraining Model** | Recovery Alignment | Strain, Monotony | Overtraining Index | Detects excessive stress |
| **San Millán Metabolic Model** | Metabolic Efficiency | FatOxidationIndex | Mito Efficiency Index | Evaluates fat utilization |
| **Noakes Central Governor Model** | Readiness Forecast | HRV × RPE | CNS Fatigue Index | Detects neural fatigue |
| **Skiba Critical Power Model** | Performance Integration | CP, W' | Fatigue Decay Curve | Predicts limit performance |
| **Mujika Tapering Model** | Periodisation | Load % reduction | Taper Efficiency | Optimizes tapering block |
| **Friel Training Stress Model** | Consistency Framework | TSS, Compliance | Adherence Score | Validates plan execution |
| **Sandbakk-Holmberg Integration** | Action Generation | Multi-framework synthesis | Adaptive Action Score | Generates holistic coaching feedback |

---

## 📚 Documentation Index

Centralized index of all framework, audit, and coaching modules in **Intervals.icu GPT Coaching Framework v16.16G**.  
This section is auto-generated and refreshed via GitHub Actions on commit.

### 🧩 Core Framework Documents
| File | Description |
|:--|:--|
| [all-modules.md](./all-modules.md) | Module list, bindings, and dependency schema. |
| [USAGE_GUIDE.md](./USAGE_GUIDE.md) | Usage for local (`report.py`) and ChatGPT modes. |
| [TIER_MODULE_DETAILS.md](./TIER_MODULE_DETAILS.md) | Tier-0 → Tier-2 audit module descriptions. |
| [audit_chain_overview.md](./audit_chain_overview.md) | End-to-end audit chain visualization. |
| [COMPLIANCE_LOG_GUIDE.md](./COMPLIANCE_LOG_GUIDE.md) | Compliance and audit log schema. |

### 🧱 Coaching Framework Stack
| File | Description |
|:--|:--|
| [coach_framework-map.md](./coach_framework-map.md) | Hierarchical coaching frameworks. |
| [coach_mapping-table.md](./coach_mapping-table.md) | Metric-to-framework mappings. |

### 🔬 Analytical & Mapping Resources
| File | Description |
|:--|:--|
| [mapping-table.md](./mapping-table.md) | Full data lineage diagram and report linkage. |
| [mapping-table-compact.md](./mapping-table-compact.md) | Compact vertical flow diagram (GitHub-optimized). |
| [audit_framework-map.md](./audit_framework-map.md) | Audit tier dependency flow. |

### ⚖️ Governance & Integrity
| File | Description |
|:--|:--|
| [COMPLIANCE_LOG_GUIDE.md](./COMPLIANCE_LOG_GUIDE.md) | Logging and compliance trace rules. |
| [audit_chain_overview.md](./audit_chain_overview.md) | Tier integrity enforcement and validation logic. |

### 🧭 Entry Points
| File | Function |
|:--|:--|
| `report.py` | Primary local execution entry for `run_report()`. |
| `run_audit.py` | Developer diagnostic utility. |
| `audit_core/report_controller.py` | ChatGPT execution controller. |


---

## 📜 References  

- **Seiler, S. & Tønnessen, E. (2009).** *Intervals, Thresholds, and Long Slow Distance: The Role of Intensity and Duration in Endurance Training.* *Eur. J. Sport Sci.*, 9(1), 3–13.  
- **Banister, E. W. (1975).** *Modeling of Training and Overtraining.* *Proc. 1st Int. Symp. Biochem. of Exercise.* Univ. Park Press.  
- **Foster, C. (1998).** *Monitoring Training in Athletes.* *Med. & Sci. Sports Exerc.*, 30(7), 1164–1168.  
- **San Millán, I. (2019).** *Metabolic Flexibility and Mitochondrial Function in Endurance Athletes.* *J. Appl. Physiol.*, 127(5), 1453–1461.  
- **Friel, J. (2012).** *The Triathlete’s Training Bible (4th ed.).* VeloPress.  
- **Sandbakk, Ø. & Holmberg, H. C. (2017).** *Physiological Capacity and Training Routines of Elite Endurance Athletes.* *Scand. J. Med. Sci. Sports*, 27(7), 701–712.  
- **Skiba, P. F. (2014).** *The Application of the Critical Power Model to Cycling.* *Eur. J. Appl. Physiol.*, 114(11), 2441–2453.  
- **Coggan, A. R. & Allen, H. (2010).** *Training and Racing with a Power Meter (2nd ed.).* VeloPress.  
- **Noakes, T. D. (2012).** *The Central Governor Model of Exercise Regulation.* *Wiley-Blackwell.*  
- **Mujika, I. & Padilla, S. (2003).** *Scientific Bases for Pre-Competition Tapering Strategies.* *Med. & Sci. Sports Exerc.*, 35(7), 1182–1187.  
- **Coggan, A. R. & Seiler, S. (2018).** *Hybrid Polarised vs Sweet Spot Endurance Training Analysis.* ACSM Annual Meeting Presentation.

---

**Maintainer:** Intervals ICU GPT Coach Architecture Team  
**Repository:** [revo2wheels/intervalsicugptcoach-public](https://github.com/revo2wheels/intervalsicugptcoach-public)
