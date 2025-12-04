# 🧾 Weekly Audit Report

## Execution Logs

```
✅ Renderer source: Tier-2 enforced totals (canonical dataset)
[FINALIZER] Enforcing markdown-only return (season-safe mode)
[FINALIZER] Markdown-only return OK — len=5245, ctx_keys=84
✅ Renderer source: Tier-2 enforced totals (canonical dataset)
[FINALIZER] Enforcing markdown-only return (season-safe mode)
[FINALIZER] Markdown-only return OK — len=5245, ctx_keys=84
```

## Rendered Markdown Report

# 🧭 Weekly Training Report — URF v5.1
**Athlete:** Clive King
**Period:** 2025-11-28 → 2025-12-04
**Timezone:** Europe/Zurich
**Generated:** 2025-12-04T14:50:52.903788

---


## 🧩 Tier-0 Dataset Integrity

- Activities fetched: 4
- Origin: —
- Purge enforced: False
- Wellness records: n/a
- Source verification: ✅ Live (no mock/cache)


## 🧩 Tier-1 Audit Controller

- Deduplication: OK
- HR stream coverage: —
- Power data coverage: —
- Time variance ≤ 0.1 h ✅


## 📊 Key Stats

| Metric | Value |
|:-- |:--|
| Hours | 5.78 |
| Distance (km) | 160.1 |
| TSS | 260 |
| Sessions | 4 |



## 🧮 Derived Metric Audit (EWMA-based ACWR)

| Metric | Value | Status | Context |
|:-- |:-- |:-- |:--|
| ACWR | 1.0 | 🟢 productive | EWMA Acute:Chronic Load Ratio — compares 7-day vs 28-day weighted loads. 0.8–1.3 = productive training, <0.8 = recovery or detraining, >1.5 = overload/injury risk. |
| Monotony | 0.41 | 🟢 optimal | 1–2 shows healthy variation; >2.5 means repetitive stress pattern. |
| Strain | 15.2 | 🟢 optimal | Product of load × monotony; >3500 signals potential overreach. |
| FatigueTrend | nan | ⚪ undefined | FatigueTrend is calculated as the percentage change between the 7-day and 28-day moving averages. A 0% change indicates balance, while a positive percentage change indicates accumulating fatigue, and a negative percentage change indicates recovery. |
| ZQI | 2.1 | 🔴 low | Zone Quality Index (%) 5-15 high-intensity time is normal <3% too easy, >20% too intense or erratic pacing. |
| FatOxEfficiency | 0.658 | 🟢 optimal | 0.4–0.8 means balanced fat oxidation; lower = carb dependence. |
| Polarisation | 0.9 | 🟢 polarised | 0.75–0.9 matches Seiler 80/20 distribution; <0.7 = too intense. |
| FOxI | 65.8 | 🟠 moderate | FatOx index %; higher values mean more efficient aerobic base. |
| CUR | 34.2 | 🟢 optimal | Carbohydrate Utilisation Ratio; 30-80 balanced metabolic use. |
| GR | 1.75 | 🟢 optimal | Glucose Ratio; >2 indicates excess glycolytic bias. |
| MES | 22.6 | 🟢 optimal | Metabolic Efficiency Score; >20 is good endurance economy. |
| RecoveryIndex | 0.918 | 🟢 optimal | 0.6–1.0 means recovered; <0.5 = heavy fatigue. |
| StressTolerance | 2.0 | 🟢 optimal | 2–8 indicates sustainable training strain capacity. |


### Power Zones
| Zone | % Time |
|:-- |:--|
| power_z1 | 21.5 |
| power_z2 | 41.8 |
| power_z3 | 18.1 |
| power_z4 | 5.9 |
| power_z5 | 2.4 |
| power_z6 | 1.9 |
| power_z7 | 0.1 |
| power_z8 | 8.4 |


### Heart Rate Zones
| Zone | % Time |
|:-- |:--|
| hr_z1 | 85.9 |
| hr_z2 | 10.3 |
| hr_z3 | 2.2 |
| hr_z4 | 1.3 |
| hr_z5 | 0.1 |
| hr_z6 | 0.1 |
| hr_z7 | 0.0 |


_No pace zone data available._


## ⚠️ Outlier Events

_No outliers detected._


## 💓 Wellness & Recovery

- Rest Days: 3
- Resting HR: 42.8 bpm
- HRV: nan ms (→ stable, prev 43.0 ms)
- Fatigue: 1.4/5
- Stress: 1.7/5
- Readiness: nan/5
- ATL: 83.89 · CTL: 89.51 · TSB: 5.62


## 🧠 Performance & Coaching Actions


**Recommended Actions:**
1. ✅ Maintain ≥70 % Z1–Z2 volume (Seiler 80/20).
2. ⚠ Improve Zone 2 efficiency: extend duration or adjust IF.
3. ✅ Durability improving (1.00) — maintain current long-ride structure.
4. ⚠ Load intensity too high (LIR=2.00) — reduce intensity or monitor recovery.
5. ✅ Efficiency drift stable (0.00%).
6. ✅ Polarisation optimal (90%).
7. ✅ Recovery Index healthy (0.92).
8. ---
9. 📊 Metric-based Feedback:
10. ✅ Monotony (0.41) — If Monotony > 2.5, introduce more variation in training or implement a deload week to reduce repetitive stress.
11. ✅ Strain (15.2) — If Strain > 3000, monitor for signs of overreach and consider more rest or deloading. If Strain > 3500, consider reducing volume or intensity temporarily.
12. ✅ FatOxEfficiency (0.658) — If FatOxEfficiency is low (<0.6), focus on improving aerobic base with longer, low-intensity efforts.
13. ✅ CUR (34.2) — If CUR is outside the green zone (30-70), adjust carbohydrate intake and fueling strategy to ensure balanced metabolic use during long sessions.
14. ✅ GR (1.75) — If GR exceeds 2.0, focus on reducing glycolytic intensity and increase aerobic work. Ensure sufficient recovery to avoid over-reliance on carbs.
15. ✅ MES (22.6) — If MES is below 20, work on improving metabolic efficiency by increasing endurance training with a focus on aerobic base and fat metabolism.
16. ✅ RecoveryIndex (0.918) — If RecoveryIndex is low (<0.7), ensure adequate rest and recovery, and avoid heavy training loads.
17. ✅ StressTolerance (2.0) — If StressTolerance is high (>8), reduce overall load and increase recovery time. If it's low (<2), ensure proper training load progression.


## 🚴 Weekly Events Summary

| date | name | icu_training_load | moving_time | distance |
|:-- |:-- |:-- |:-- |:--|
| 2025-12-01 | Zwift - Volcano laps with Jacques | 63 | 01:17:26 | 52.4 |
| 2025-11-30 | Zwift - Genie Volcano laps | 57 | 01:05:46 | 43.0 |
| 2025-11-30 | Otto walk | 14 | 01:18:45 | 6.5 |
| 2025-11-29 | Winter lap | 126 | 02:05:01 | 58.2 |

**Cycling Totals:** 4.47 h · 153.6 km · 246 TSS · 3 sessions**
**All Activities:** 5.78 h · 160.1 km · 260 TSS · 4 sessions**
_Note: CTL/ATL/TSB values include **all activities**._

---
✅ **Audit Completed:** 2025-12-04T14:50:52.907844
**Framework:** URF v5.1 · Core: v16.14 · Enforcement: —