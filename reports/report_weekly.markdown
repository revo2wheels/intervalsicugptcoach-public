# 🧾 Weekly Audit Report

## Execution Logs

```
✅ Renderer source: Tier-2 enforced totals (canonical dataset)
[FINALIZER] Enforcing markdown-only return (season-safe mode)
[FINALIZER] Markdown-only return OK — len=5403, ctx_keys=88
✅ Renderer source: Tier-2 enforced totals (canonical dataset)
[FINALIZER] Enforcing markdown-only return (season-safe mode)
[FINALIZER] Markdown-only return OK — len=5403, ctx_keys=88
```

## Rendered Markdown Report

# 🧭 Weekly Training Report — URF v5.1
**Athlete:** Clive King
**Period:** 2025-12-04 → 2025-12-10
**Timezone:** Europe/Zurich
**Generated:** 2025-12-10T08:31:31.991662

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
| Hours | 5.73 |
| Distance (km) | 184.0 |
| TSS | 235 |
| Sessions | 4 |



## 🧮 Derived Metric Audit (EWMA-based ACWR)

| Metric | Value | Status | Context |
|:-- |:-- |:-- |:--|
| ACWR | 0.93 | 🟢 productive | EWMA Acute:Chronic Load Ratio — compares 7-day vs 28-day weighted loads. 0.8–1.3 = productive training, <0.8 = recovery or detraining, >1.5 = overload/injury risk. |
| Monotony | 0.7 | 🟢 optimal | 1–2 shows healthy variation; >2.5 means repetitive stress pattern. |
| Strain | 23.5 | 🟢 optimal | Product of load × monotony; >3500 signals potential overreach. |
| FatigueTrend | 9.6 | 🔴 accumulating | FatigueTrend is calculated as the percentage change between the 7-day and 28-day moving averages. A 0% change indicates balance, while a positive percentage change indicates accumulating fatigue, and a negative percentage change indicates recovery. |
| ZQI | 0.0 | 🔴 low | Zone Quality Index (%) 5-15 high-intensity time is normal <3% too easy, >20% too intense or erratic pacing. |
| FatOxEfficiency | 0.61 | 🟢 optimal | 0.4–0.8 means balanced fat oxidation; lower = carb dependence. |
| Polarisation | 0.9 | 🟢 polarised | 0.75–0.9 matches Seiler 80/20 distribution; <0.7 = too intense. |
| FOxI | 61.0 | 🟠 moderate | FatOx index %; higher values mean more efficient aerobic base. |
| CUR | 39.0 | 🟢 optimal | Carbohydrate Utilisation Ratio; 30-80 balanced metabolic use. |
| GR | 1.63 | 🟢 optimal | Glucose Ratio; >2 indicates excess glycolytic bias. |
| MES | 22.5 | 🟢 optimal | Metabolic Efficiency Score; >20 is good endurance economy. |
| RecoveryIndex | 0.86 | 🟢 optimal | 0.6–1.0 means recovered; <0.5 = heavy fatigue. |
| StressTolerance | 2.0 | 🟢 optimal | 2–8 indicates sustainable training strain capacity. |


### Power Zones
| Zone | % Time |
|:-- |:--|
| power_z1 | 14.3 |
| power_z2 | 69.2 |
| power_z3 | 10.2 |
| power_z4 | 2.5 |
| power_z5 | 0.0 |
| power_z6 | 0.0 |
| power_z7 | 0.0 |
| power_z8 | 3.7 |


### Heart Rate Zones
| Zone | % Time |
|:-- |:--|
| hr_z1 | 77.8 |
| hr_z2 | 15.4 |
| hr_z3 | 4.3 |
| hr_z4 | 2.4 |
| hr_z5 | 0.0 |
| hr_z6 | 0.0 |
| hr_z7 | 0.0 |


_No pace zone data available._


## ⚠️ Outlier Events

_No outliers detected._


## 💓 Wellness & Recovery

- Rest Days: 3
- Resting HR: 43.0 bpm
- HRV: 37.0 ms (→ stable, prev 36.0 ms)
- Fatigue: 1.5/5
- Stress: 1.6/5
- Readiness: nan/5
- ATL: 78.06 · CTL: 87.47 · TSB: 9.41


## 🧠 Performance & Coaching Actions


**Recommended Actions:**
1. ✅ Maintain ≥70 % Z1–Z2 volume (Seiler 80/20).
2. ⚠ Improve Zone 2 efficiency: extend duration or adjust IF.
3. ✅ FatigueTrend (9.6%) — Increasing fatigue trend. Consider adjusting intensity or recovery.
4. ✅ Durability improving (1.00) — maintain current long-ride structure.
5. ⚠ Load intensity too high (LIR=2.00) — reduce intensity or monitor recovery.
6. ✅ Efficiency drift stable (0.00%).
7. ✅ Polarisation optimal (90%).
8. ✅ Recovery Index healthy (0.86).
9. ---
10. 📊 Metric-based Feedback:
11. ✅ Monotony (0.7) — If Monotony > 2.5, introduce more variation in training or implement a deload week to reduce repetitive stress.
12. ✅ Strain (23.5) — If Strain > 3000, monitor for signs of overreach and consider more rest or deloading. If Strain > 3500, consider reducing volume or intensity temporarily.
13. ✅ FatOxEfficiency (0.61) — If FatOxEfficiency is low (<0.6), focus on improving aerobic base with longer, low-intensity efforts.
14. ✅ CUR (39.0) — If CUR is outside the green zone (30-70), adjust carbohydrate intake and fueling strategy to ensure balanced metabolic use during long sessions.
15. ✅ GR (1.63) — If GR exceeds 2.0, focus on reducing glycolytic intensity and increase aerobic work. Ensure sufficient recovery to avoid over-reliance on carbs.
16. ✅ MES (22.5) — If MES is below 20, work on improving metabolic efficiency by increasing endurance training with a focus on aerobic base and fat metabolism.
17. ✅ RecoveryIndex (0.86) — If RecoveryIndex is low (<0.7), ensure adequate rest and recovery, and avoid heavy training loads.
18. ✅ StressTolerance (2.0) — If StressTolerance is high (>8), reduce overall load and increase recovery time. If it's low (<2), ensure proper training load progression.


## 🚴 Weekly Events Summary

| date | name | icu_training_load | moving_time | distance |
|:-- |:-- |:-- |:-- |:--|
| 2025-12-09 | Zwift - Group Workout: BaseCamp Aerobic Endurance with Cadence Builds | 59 | 01:00:49 | 32.5 |
| 2025-12-08 | Zwift - nope | 39 | 00:55:41 | 36.4 |
| 2025-12-07 | Otto walk | 19 | 00:45:31 | 3.9 |
| 2025-12-07 | Zwift - Group Ride: Flanders Coffee Ride en France | 118 | 03:01:36 | 111.2 |

**Cycling Totals:** 4.97 h · 180.1 km · 216 TSS · 3 sessions**
**All Activities:** 5.73 h · 184.0 km · 235 TSS · 4 sessions**
_Note: CTL/ATL/TSB values include **all activities**._

---
✅ **Audit Completed:** 2025-12-10T08:31:31.996321
**Framework:** URF v5.1 · Core: v16.14 · Enforcement: —