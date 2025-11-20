# 🧾 Weekly Audit Report

## Execution Logs

```
✅ Renderer source: Tier-2 enforced totals (canonical dataset)
[FINALIZER] Enforcing markdown-only return (season-safe mode)
[FINALIZER] Markdown-only return OK — len=5674, ctx_keys=74
✅ Renderer source: Tier-2 enforced totals (canonical dataset)
[FINALIZER] Enforcing markdown-only return (season-safe mode)
[FINALIZER] Markdown-only return OK — len=5674, ctx_keys=74
```

## Rendered Markdown Report

# 🧭 Weekly Training Report — URF v5.1
**Athlete:** Clive King
**Period:** 2025-11-14 → 2025-11-20
**Timezone:** Europe/Zurich
**Generated:** 2025-11-20T14:36:20.504175

---


## 🧩 Tier-0 Dataset Integrity

- Activities fetched: 6
- Origin: —
- Purge enforced: False
- Wellness records: n/a
- Source verification: ✅ Live (no mock/cache)


## 🧩 Tier-1 Audit Controller

- Deduplication: OK
- HR stream coverage: —
- Power data coverage: —
- Time variance ≤ 0.1 h ✅


## 🧮 Derived Metric Audit (EWMA-based ACWR)

| Metric | Value | Status | Context |
|:-- |:-- |:-- |:--|
| ACWR | 0.83 | 🟢 productive | EWMA Acute:Chronic Load Ratio — compares 7-day vs 28-day weighted loads. 0.8–1.3 = productive training, <0.8 = recovery or detraining, >1.5 = overload/injury risk. |
| Monotony | 0.99 | 🟢 optimal | 1–2 shows healthy variation; >2.5 means repetitive stress pattern. |
| Strain | 67.3 | 🟢 optimal | Product of load × monotony; >3500 signals potential overreach. |
| FatigueTrend | -13.8 | 🟠 recovering | FatigueTrend is calculated as the percentage change between the 7-day and 28-day moving averages. A 0% change indicates balance, while a positive percentage change indicates accumulating fatigue, and a negative percentage change indicates recovery. |
| ZQI | 11.8 | 🟢 optimal | Zone Quality Index (%) 5-15 high-intensity time is normal <3% too easy, >20% too intense or erratic pacing. |
| FatOxEfficiency | 0.745 | 🟢 optimal | 0.4–0.8 means balanced fat oxidation; lower = carb dependence. |
| Polarisation | 0.9 | 🟢 polarised | 0.75–0.9 matches Seiler 80/20 distribution; <0.7 = too intense. |
| FOxI | 74.5 | 🟢 optimal | FatOx index %; higher values mean more efficient aerobic base. |
| CUR | 25.5 | 🟢 optimal | Carbohydrate Utilisation Ratio; 30-80 balanced metabolic use. |
| GR | 1.99 | 🟢 optimal | Glucose Ratio; >2 indicates excess glycolytic bias. |
| MES | 22.5 | 🟢 optimal | Metabolic Efficiency Score; >20 is good endurance economy. |
| RecoveryIndex | 0.802 | 🟢 optimal | 0.6–1.0 means recovered; <0.5 = heavy fatigue. |
| StressTolerance | 2.0 | 🟢 optimal | 2–8 indicates sustainable training strain capacity. |


### Power Zones
| Zone | % Time |
|:-- |:--|
| power_z1 | 29.6 |
| power_z2 | 24.1 |
| power_z3 | 12.6 |
| power_z4 | 11.1 |
| power_z5 | 8.0 |
| power_z6 | 5.2 |
| power_z7 | 0.6 |
| power_z8 | 8.9 |


### Heart Rate Zones
| Zone | % Time |
|:-- |:--|
| hr_z1 | 68.5 |
| hr_z2 | 10.0 |
| hr_z3 | 3.0 |
| hr_z4 | 8.1 |
| hr_z5 | 3.5 |
| hr_z6 | 4.6 |
| hr_z7 | 2.3 |


_No pace zone data available._


## ⚠️ Outlier Events

| Date | Event | Issue | Observation |
|:-- |:-- |:-- |:--|
| 2025-11-15 | Perry | TSS outlier | TSS=178 |


## 💓 Wellness & Recovery

- Rest Days: 2
- Resting HR: 43.7 bpm
- HRV: 53.0 ms (↑ improving (+6.0 ms), prev 47.0 ms)
- Fatigue: 1.3/5
- Stress: 1.3/5
- Readiness: nan/5
- ATL: 81.16 · CTL: 88.91 · TSB: 7.75


## 🧠 Performance & Coaching Actions


**Recommended Actions:**
1. ✅ Maintain ≥70 % Z1–Z2 volume (Seiler 80/20).
2. ⚠ Improve Zone 2 efficiency: extend duration or adjust IF.
3. ⚠ FatigueTrend (-13.8%) — Recovery phase detected. Maintain steady training load and prioritize recovery.
4. ✅ Durability improving (1.00) — maintain current long-ride structure.
5. ⚠ Load intensity low (LIR=0.00) — add tempo or sweet-spot intervals.
6. ✅ Endurance reserve strong (1.00).
7. ✅ Efficiency drift stable (0.00%).
8. ✅ Polarisation optimal (90%).
9. ✅ Recovery Index healthy (0.80).
10. ---
11. 📊 Metric-based Feedback:
12. ✅ Monotony (0.99) — If Monotony > 2.5, introduce more variation in training or implement a deload week to reduce repetitive stress.
13. ✅ Strain (67.3) — If Strain > 3000, monitor for signs of overreach and consider more rest or deloading. If Strain > 3500, consider reducing volume or intensity temporarily.
14. ✅ ZQI (11.8) — If ZQI > 20%, review pacing strategy; excessive high-intensity time could indicate erratic pacing or overtraining. Aim for 5-15% ZQI for balanced training.
15. ✅ FatOxEfficiency (0.745) — If FatOxEfficiency is low (<0.6), focus on improving aerobic base with longer, low-intensity efforts.
16. ✅ FOxI (74.5) — If FOxI is increasing, continue to prioritize low-intensity work to enhance fat metabolism. If it decreases, consider increasing your Zone 2 training duration.
17. ✅ CUR (25.5) — If CUR is outside the green zone (30-70), adjust carbohydrate intake and fueling strategy to ensure balanced metabolic use during long sessions.
18. ✅ GR (1.99) — If GR exceeds 2.0, focus on reducing glycolytic intensity and increase aerobic work. Ensure sufficient recovery to avoid over-reliance on carbs.
19. ✅ MES (22.5) — If MES is below 20, work on improving metabolic efficiency by increasing endurance training with a focus on aerobic base and fat metabolism.
20. ✅ RecoveryIndex (0.802) — If RecoveryIndex is low (<0.7), ensure adequate rest and recovery, and avoid heavy training loads.
21. ✅ StressTolerance (2.0) — If StressTolerance is high (>8), reduce overall load and increase recovery time. If it's low (<2), ensure proper training load progression.


## 🚴 Weekly Events Summary

| date | name | icu_training_load | moving_time | distance |
|:-- |:-- |:-- |:-- |:--|
| 2025-11-20 | Otto walk | 15 | 01:33:05 | 6.2 |
| 2025-11-19 | Zwift - Oh Hill No x3 💥 | 101 | 01:17:49 | 35.5 |
| 2025-11-18 | Zwift - base | 56 | 01:05:39 | 44.7 |
| 2025-11-17 | Holo intervals | 98 | 01:20:04 | 46.9 |
| 2025-11-15 | Perry | 178 | 02:24:04 | 67.5 |
| 2025-11-15 | Otto walk | 28 | 01:26:29 | 6.9 |

**Totals:** 9.12 h · 207.7 km · 476 TSS · 0 sessions**

---
✅ **Audit Completed:** 2025-11-20T14:36:20.508942
**Framework:** URF v5.1 · Core: v16.14 · Enforcement: —