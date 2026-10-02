# 🧠 Coaching Heuristics Pack — v16.1-EOD-002 (Unified & Aligned)

🔗 **Dependencies:**  
- Glossary & Placeholders → variable bindings  
- Advanced Marker Reference → metric definitions  
- Coaching Cheat Sheet → quick classification tables  
- Unified Reporting Framework v5.1 → output compliance  

Purpose: integrate all 10 active coaching frameworks (Seiler, Banister, Foster, San Millán, Friel, Sandbakk, Skiba, Coggan, Noakes, Hybrid Polarised–Sweet Spot) while preserving operational thresholds.

---

## 🔑 Load Management Rules

| Metric | Green | Amber | Red | Framework |
|:--|:--|:--|:--|:--|
| **Strain** | < 1,800 | 1,800–2,200 | > 2,200 | Foster |
| **ACWR** | 0.8–1.3 | 1.3–1.5 | > 1.5 | Banister |
| **Monotony** | < 1.5 | 1.5–2.0 | > 2.0 | Foster |
| **CTL Trend** | +3 – 5 / week | ±2 steady | ↓ > 5 / week | Friel |
| **Durability Index** | ≤ 5 % drift | 5–7 % | > 7 % | Sandbakk |

All aggregation direct from stored event fields. Rounding, smoothing, or estimation prohibited.  
Report blocked if Σ(Event km) ≠ Weekly km or Σ(TSS) ≠ Weekly TSS.

---

## 🔄 Recovery & Adaptation Rules

| Parameter | Green | Amber | Red | Framework |
|:--|:--|:--|:--|:--|
| **Recovery Index** | HRV stable, RestHR steady (Form ≥ 0) | HRV ↓15–25 % / RestHR +5 bpm | HRV ↓> 25 % / RestHR +10 bpm | Noakes |
| **Sleep (hrs avg)** | > 8 h | 7–8 h | < 7 h | Noakes |
| **Consistency** | ≤ 1 missed session | > 2 missed sessions / week | > 1 missed week | Friel |
| **Fatigue Governance** | – | Fatigue ≥ 3 / 10 → deload flag | Fatigue ≥ 5 → halt | Foster + Noakes |

---

## ⚡ Training Quality & Seiler’s Principles

**Seiler 3-zone model** (Seiler 2010; Stöggl & Sperlich 2015)  
- Seiler Z1 = Z1+Z2 (below LT1), Seiler Z2 = Z3+Z4 (LT1–LT2), Seiler Z3 = Z5–Z7 (above LT2 ≈ FTP); fractions renormalised to sum to 1 (same grouping as Intervals.icu's Polarization Index).  
- Sweet Spot overlaps Z3/Z4: reported as its own % of the Z1–Z7 total, never added to it (Z1–Z7 = 100 %).  
- **Polarisation** = % time in Seiler Z1; state = distribution type, checked in order: hiit → polarised → base → pyramidal → threshold → unique (Intervals.icu rules). Informational, no good/bad bands. Power-based; Ride HR zones only when no power.  
- Seiler's "80/20" counts sessions, not minutes.  

**Polarisation Index** (Treff et al. 2019)  
- PI = log10((Z1 / Z2) × Z3 × 100) on the 3-zone fractions. Z2 = 0 → log10(Z1 / 0.01 × (Z3 − 0.01) × 100); Z3 = 0 → PI = 0; Z3 > Z1 → not calculated.  
- PI > 2.00 = polarised; ≤ 2.00 = not polarised (informational, no good/bad band).  
- Power-based (Ride HR zones only when no power). Polarisation_fused = same index on the dominant sport (power, else HR); Polarisation_combined = same index across all endurance sports (lower confidence).  

**ZQI** = % time in Seiler zone 3 (Z5–Z7, above LT2 ≈ FTP). Informational, no good/bad bands (none are published); for reference, elites typically spend ~1–8 % of time above LT2 by time in zone, and polarised blocks ~15–20 % by session goal.  

**Session Goals (Seiler Framework)**  
- Long: 2–6 h low-intensity → build durability.  
- Interval: VO₂max sets (4×8 min @ ~90 % HRmax).  
- Tempo/race-pace: sparingly → specific sharpening.  
→ **Quality Session Balance ≥ 2/week** (1 long + 1 interval).

**Hard Days Hard / Easy Days Easy**  
- Easy days: < 20 % Z3/Z4.  
- Hard days: meaningful intensity or volume.  
Flag recovery days > 20 % Z3/Z4 as violations.

---

## 🧠 Metabolic & Zone 2 Heuristics (San Millán)

| Variable | Target | Interpretation |
|:--|:--|:--|
| **Zone 2 Volume Fraction** | ≥ 20 % weekly duration | sufficient mitochondrial stimulus |
| **FatOxidation Index** | ≥ 0.7 | strong aerobic efficiency |
| **HR–Power Decoupling** | ≤ 5 % | stable fat-oxidation |
| **Z2 Deficit Rule** | if Z2 < 15 % → add 1 low-intensity session / week | |

---

## 📈 Periodisation & Macrocycle Rules (Friel)

| Phase | Load Trend | Key Indicators |
|:--|:--|:--|
| **Build** | CTL ↑ 3–7 / week • ATL < 110 | steady fitness gain |
| **Overload** | ACWR > 1.3 • Strain 1,900–2,200 | HRV dip expected |
| **Deload** | Load ↓ ~40 % • ATL < 80 • HRV rebound ≥ 55 ms | recovery phase |
| **Consolidation** | CTL stable ± 2 • HRV steady • VO₂max preserved | adaptation holding |

**Age Adaptation:**  
ATL scale = 0.95 (< 35 y), 0.85 (35–50 y), 0.75 (> 50 y).

---

## 🏁 Tapering Guidelines
- 10–14 days pre-race: ATL ↓ 40–60 %, intensity maintained, HRV ↑.  
- Red flag → ATL not ↓ ≥ 30 %.  

---

## 🟢 Green Flags
- CTL > 100 sustained → strong base.  
- VO₂max stable / ↑.  
- HRV rebounds post-deload.  
- Quality Session Balance achieved.  
- Durability Index ≤ 5 %.

---

## 🚨 Red & Amber Flags
- **Subjective vs Objective Mismatch**  
  - ⚠️ RPE ≤ 3 but TSS > 150 → under-reporting.  
  - ⚠️ RPE ≥ 8 but TSS < 50 → non-training stress.  
- **Recovery Mismatch**  
  - ❌ HRV < 35 ms > 5 days.  
  - ❌ RestHR + > 10 bpm.  
- **Quality Session Balance**  
  - ⚠️ Only 1 quality session/week.  
  - ❌ None.  
- **Durability Index**  
  - ⚠️ 5–7 % drift.  
  - ❌ > 7 % drift.  

---

## 🧩 Adaptive Logic Layer (Synthesised)

1. If ACWR > 1.5 ∧ Monotony > 1.6 → flag deload.  
2. If Z2 < 15 % → add Zone 2 session.  
3. If DurabilityIndex < 0.75 → increase Z2 duration.  
4. If RecoveryIndex < 0.85 → block intensity sessions.  
5. If available time < 6 h/week → activate Sweet-Spot bias.  
6. If age > 50 → apply ATL × 0.75.  
7. Flag < 3 sessions/week rolling 21 days as inconsistent.  

---

## 🏅 Sport Profiles (unchanged)

### Ironman / Long-Course Triathlon  
- Volume 20–25 h typ.  
- Key: long ride + long run bricks.  
- Taper: 2–3 weeks, load ↓ 50–60 %, intensity maintained.  

### Gran Fondo / Road Cycling  
- Volume 600–900 TSS/week.  
- Polarisation: informational (no target band).  
- Taper: 7–10 days.  

### Marathon  
- Long runs > 30 km.  
- Overload Strain ~ 1,800–2,000.  
- Taper: 2–3 weeks ↓ 40–50 %.  

### Ultramarathon  
- Very high volume → Monotony risk.  
- HRV & sleep = limiters.  
- Taper: 3–4 weeks.  

### Short-Course Tri / TT / 10 k  
- Volume 8–14 h, intensity high.  
- Polarisation: informational (no target band).  
- Taper: 5–7 days.  

---

## 📖 Athlete History Hooks
- Recurring overload/illness alerts.  
- Injury pattern triggers.  
- Readiness vs historical best PRs.  
- Race result trend tracking.

---

**Compliance:**  
✅ Aligned with Coach Profile Framework v16.1  
✅ Valid under Unified Reporting Framework v5.1  
✅ Event-only metrics, no derived duration  
