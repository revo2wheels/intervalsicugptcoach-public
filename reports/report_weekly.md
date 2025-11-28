# 🧾 Weekly Audit Report

## Execution Logs

```
✅ Renderer source: Tier-2 enforced totals (canonical dataset)
[FINALIZER] Enforcing markdown-only return (season-safe mode)
[FINALIZER] Markdown-only return OK — len=6045, ctx_keys=79
✅ Renderer source: Tier-2 enforced totals (canonical dataset)
[FINALIZER] Enforcing markdown-only return (season-safe mode)
[FINALIZER] Markdown-only return OK — len=6045, ctx_keys=79
```

## Rendered Markdown Report

# 🧭 Weekly Training Report — URF v5.1
**Athlete:** Clive King
**Period:** 2025-11-22 → 2025-11-28
**Timezone:** Europe/Zurich
**Generated:** 2025-11-28T08:35:40.652657

---


## 🧩 Tier-0 Dataset Integrity

- Activities fetched: 7
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
| ACWR | 1.0 | 🟢 productive | EWMA Acute:Chronic Load Ratio — compares 7-day vs 28-day weighted loads. 0.8–1.3 = productive training, <0.8 = recovery or detraining, >1.5 = overload/injury risk. |
| Monotony | 0.41 | 🟢 optimal | 1–2 shows healthy variation; >2.5 means repetitive stress pattern. |
| Strain | 29.2 | 🟢 optimal | Product of load × monotony; >3500 signals potential overreach. |
| FatigueTrend | nan | ⚪ undefined | FatigueTrend is calculated as the percentage change between the 7-day and 28-day moving averages. A 0% change indicates balance, while a positive percentage change indicates accumulating fatigue, and a negative percentage change indicates recovery. |
| ZQI | 5.3 | 🟢 optimal | Zone Quality Index (%) 5-15 high-intensity time is normal <3% too easy, >20% too intense or erratic pacing. |
| FatOxEfficiency | 0.644 | 🟢 optimal | 0.4–0.8 means balanced fat oxidation; lower = carb dependence. |
| Polarisation | 0.9 | 🟢 polarised | 0.75–0.9 matches Seiler 80/20 distribution; <0.7 = too intense. |
| FOxI | 64.4 | 🟠 moderate | FatOx index %; higher values mean more efficient aerobic base. |
| CUR | 35.6 | 🟢 optimal | Carbohydrate Utilisation Ratio; 30-80 balanced metabolic use. |
| GR | 1.72 | 🟢 optimal | Glucose Ratio; >2 indicates excess glycolytic bias. |
| MES | 22.5 | 🟢 optimal | Metabolic Efficiency Score; >20 is good endurance economy. |
| RecoveryIndex | 0.918 | 🟢 optimal | 0.6–1.0 means recovered; <0.5 = heavy fatigue. |
| StressTolerance | 2.0 | 🟢 optimal | 2–8 indicates sustainable training strain capacity. |


### Power Zones
| Zone | % Time |
|:-- |:--|
| power_z1 | 14.5 |
| power_z2 | 46.6 |
| power_z3 | 21.0 |
| power_z4 | 5.0 |
| power_z5 | 3.3 |
| power_z6 | 1.7 |
| power_z7 | 0.4 |
| power_z8 | 7.5 |


### Heart Rate Zones
| Zone | % Time |
|:-- |:--|
| hr_z1 | 64.9 |
| hr_z2 | 20.7 |
| hr_z3 | 4.9 |
| hr_z4 | 4.3 |
| hr_z5 | 2.3 |
| hr_z6 | 1.9 |
| hr_z7 | 1.0 |


_No pace zone data available._


## ⚠️ Outlier Events

| Date | Event | Issue | Observation |
|:-- |:-- |:-- |:--|
| 2025-11-23 | Zwift - Group Ride: DIRT The Merge ENDURANCE (C) on Triple Flat Loops | TSS outlier | TSS=158 |


## 💓 Wellness & Recovery

- Rest Days: 1
- Resting HR: 42.9 bpm
- HRV: 47.0 ms (→ stable, prev 46.0 ms)
- Fatigue: 1.5/5
- Stress: 1.8/5
- Readiness: nan/5
- ATL: 87.3 · CTL: 90.68 · TSB: 3.38


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
11. ✅ Strain (29.2) — If Strain > 3000, monitor for signs of overreach and consider more rest or deloading. If Strain > 3500, consider reducing volume or intensity temporarily.
12. ✅ ZQI (5.3) — If ZQI > 20%, review pacing strategy; excessive high-intensity time could indicate erratic pacing or overtraining. Aim for 5-15% ZQI for balanced training.
13. ✅ FatOxEfficiency (0.644) — If FatOxEfficiency is low (<0.6), focus on improving aerobic base with longer, low-intensity efforts.
14. ✅ CUR (35.6) — If CUR is outside the green zone (30-70), adjust carbohydrate intake and fueling strategy to ensure balanced metabolic use during long sessions.
15. ✅ GR (1.72) — If GR exceeds 2.0, focus on reducing glycolytic intensity and increase aerobic work. Ensure sufficient recovery to avoid over-reliance on carbs.
16. ✅ MES (22.5) — If MES is below 20, work on improving metabolic efficiency by increasing endurance training with a focus on aerobic base and fat metabolism.
17. ✅ RecoveryIndex (0.918) — If RecoveryIndex is low (<0.7), ensure adequate rest and recovery, and avoid heavy training loads.
18. ✅ StressTolerance (2.0) — If StressTolerance is high (>8), reduce overall load and increase recovery time. If it's low (<2), ensure proper training load progression.


## 🚴 Weekly Events Summary

| date | name | icu_training_load | moving_time | distance |
|:-- |:-- |:-- |:-- |:--|
| 2025-11-27 | Zwift - Race: Stage 2: NYC Showdown: Prospect Park Loop (A) | 66 | 00:48:31 | 33.0 |
| 2025-11-27 | Zwift - Prospect Park Loop in New York | 14 | 00:15:01 | 9.3 |
| 2025-11-26 | Zwift - Group Ride: Off The MAAP 2025: Stage 1 on Keith Hill After Party | 79 | 01:06:19 | 42.6 |
| 2025-11-25 | Zwift - Race: Stage 1: NYC Showdown: Times Square Circuit (A) | 79 | 01:02:07 | 39.2 |
| 2025-11-25 | Zwift - 1hr Base on Prospect Park Loop in New York | 9 | 00:14:37 | 8.2 |
| 2025-11-23 | Otto walk | 39 | 01:02:26 | 5.3 |
| 2025-11-23 | Zwift - Group Ride: DIRT The Merge ENDURANCE (C) on Triple Flat Loops | 158 | 03:08:45 | 130.5 |
| 2025-11-23 | Zwift - Downtown Eruption in Watopia | 37 | 00:44:43 | 25.6 |
| 2025-11-23 | Zwift - Volcano Flat in Watopia | 2 | 00:07:27 | 3.8 |
| 2025-11-22 | Otto walk | 15 | 01:24:12 | 6.2 |

**Cycling Totals:** 7.46 h · 292.2 km · 444 TSS · 8 sessions**
**All Activities:** 9.90 h · 303.7 km · 498 TSS · 10 sessions**
_Note: CTL/ATL/TSB values include **all activities**._

---
✅ **Audit Completed:** 2025-11-28T08:35:40.656116
**Framework:** URF v5.1 · Core: v16.14 · Enforcement: —