# 🧾 Weekly Audit Report

## Execution Logs

```
✅ Renderer source: Tier-2 enforced totals (canonical dataset)
[FINALIZER] Enforcing markdown-only return (season-safe mode)
[FINALIZER] Markdown-only return OK — len=3734, ctx_keys=75
✅ Renderer source: Tier-2 enforced totals (canonical dataset)
[FINALIZER] Enforcing markdown-only return (season-safe mode)
[FINALIZER] Markdown-only return OK — len=3734, ctx_keys=75
```

## Rendered Markdown Report

# 🧭 Weekly Training Report — URF v5.1
**Athlete:** Clive King
**Period:** 2025-11-13 → 2025-11-19
**Timezone:** Europe/Zurich
**Generated:** 2025-11-19T10:31:04.148240

---


## 🧩 Tier-0 Dataset Integrity

- Activities fetched: 5
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
| ACWR | 0.94 |  ok | EWMA Acute:Chronic Load Ratio — compares 7-day vs 28-day weighted loads. 0.8–1.3 = productive training, <0.8 = recovery or detraining, >1.5 = overload/injury risk. |
| Monotony | 1.72 |  ok | 1–2 shows healthy variation; >2.5 means repetitive stress pattern. |
| Strain | 192.6 |  ok | Product of load × monotony; >3500 signals potential overreach. |
| FatigueTrend | nan |  ok | 0±0.2 indicates balance; positive trend means accumulating fatigue. |
| ZQI | 7970.0 |  ok | Zone Quality Index (%) 5-15 high-intensity time is normal <3% too easy, >20% too intense or erratic pacing. |
| FatOxEfficiency | 0.717 |  ok | 0.4–0.8 means balanced fat oxidation; lower = carb dependence. |
| Polarisation | 0.9 |  ok | 0.75–0.9 matches Seiler 80/20 distribution; <0.7 = too intense. |
| FOxI | 71.7 |  ok | FatOx index %; higher values mean more efficient aerobic base. |
| CUR | 28.3 |  ok | Carbohydrate Utilisation Ratio; 30-80 balanced metabolic use. |
| GR | 1.91 |  ok | Glucose Ratio; >2 indicates excess glycolytic bias. |
| MES | 22.5 |  ok | Metabolic Efficiency Score; >20 is good endurance economy. |
| RecoveryIndex | 0.656 |  ok | 0.6–1.0 means recovered; <0.5 = heavy fatigue. |
| ACWR_Risk | nan |  ok | Used internally for stability check. |
| StressTolerance | 1.12 |  ok | 2–8 indicates sustainable training strain capacity. |


### Power Zones
| Zone | % Time |
|:-- |:--|
| power_z1 | 25.3 |
| power_z2 | 38.7 |
| power_z3 | 14.2 |
| power_z4 | 4.7 |
| power_z5 | 5.2 |
| power_z6 | 5.2 |
| power_z7 | 0.9 |
| power_z8 | 5.7 |


### Heart Rate Zones
| Zone | % Time |
|:-- |:--|
| hr_z1 | 70.5 |
| hr_z2 | 12.0 |
| hr_z3 | 3.3 |
| hr_z4 | 6.9 |
| hr_z5 | 2.6 |
| hr_z6 | 3.1 |
| hr_z7 | 1.6 |


_No pace zone data available._


## ⚠️ Outlier Events

| Date | Event | Issue | Observation |
|:-- |:-- |:-- |:--|
| 2025-11-15 | Perry | TSS outlier | TSS=178 |


## 💓 Wellness & Recovery

- Rest Days: 2
- Resting HR: 43.4 bpm
- HRV: 47.0 ms (↑ improving (+3.0 ms), prev 44.0 ms)
- Fatigue: 1.5/5
- Stress: 1.5/5
- Readiness: nan/5
- ATL: 81.26 · CTL: 89.08 · TSB: 7.82


## 🧠 Performance & Coaching Actions


**Recommended Actions:**
1. ✅ Maintain ≥70 % Z1–Z2 volume (Seiler 80/20).
2. ⚠ Improve Zone 2 efficiency: extend duration or adjust IF.
3. ✅ Durability improving (1.00) — maintain current long-ride structure.
4. ⚠ Load intensity low (LIR=0.00) — add tempo or sweet-spot intervals.
5. ✅ Endurance reserve strong (1.00).
6. ✅ Efficiency drift stable (0.00%).
7. ✅ Polarisation optimal (90%).
8. 🟠 Recovery Index moderate (0.66) — monitor fatigue trend.


## 🚴 Weekly Events Summary

| date | name | icu_training_load | moving_time | distance |
|:-- |:-- |:-- |:-- |:--|
| 2025-11-18 | Zwift - base | 56 | 01:05:39 | 44.7 |
| 2025-11-17 | Holo intervals | 98 | 01:20:04 | 46.9 |
| 2025-11-15 | Perry | 178 | 02:24:04 | 67.5 |
| 2025-11-15 | Otto walk | 28 | 01:26:29 | 6.9 |
| 2025-11-13 | Zwift - Group Ride: DBR Base Endurance Ride | 88 | 01:31:47 | 58.3 |

**Totals:** 7.80 h · 224.3 km · 448 TSS · 0 sessions**

---
✅ **Audit Completed:** 2025-11-19T10:31:04.150872
**Framework:** URF v5.1 · Core: v16.14 · Enforcement: —