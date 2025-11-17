# 🧾 Weekly Audit Report

## Execution Logs

```
✅ Renderer source: Tier-1 visibleTotals (fallback)
[FINALIZER] Enforcing markdown-only return (season-safe mode)
[FINALIZER] Markdown-only return OK — len=3941, ctx_keys=71
✅ Renderer source: Tier-1 visibleTotals (fallback)
[FINALIZER] Enforcing markdown-only return (season-safe mode)
[FINALIZER] Markdown-only return OK — len=3941, ctx_keys=71
```

## Rendered Markdown Report

# 🧭 Weekly Training Report — URF v5.1
**Athlete:** Clive King
**Period:** 2025-11-11 → 2025-11-17
**Timezone:** Europe/Zurich
**Generated:** 2025-11-17T13:49:19.189399

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
| ACWR | 1.08 |  ok | EWMA Acute:Chronic Load Ratio — compares 7-day vs 28-day weighted loads. 0.8–1.3 = productive training, <0.8 = recovery or detraining, >1.5 = overload/injury risk. |
| Monotony | 1.89 |  ok | 1–2 shows healthy variation; >2.5 means repetitive stress pattern. |
| Strain | 222.5 |  ok | Product of load × monotony; >3500 signals potential overreach. |
| FatigueTrend | nan |  ok | 0±0.2 indicates balance; positive trend means accumulating fatigue. |
| ZQI | 7280.0 |  ok | Zone Quality Index (%) 5-15 high-intensity time is normal <3% too easy, >20% too intense or erratic pacing. |
| FatOxEfficiency | 0.655 |  ok | 0.4–0.8 means balanced fat oxidation; lower = carb dependence. |
| Polarisation | 0.9 |  ok | 0.75–0.9 matches Seiler 80/20 distribution; <0.7 = too intense. |
| FOxI | 65.5 |  ok | FatOx index %; higher values mean more efficient aerobic base. |
| CUR | 34.5 |  ok | Carbohydrate Utilisation Ratio; 30-80 balanced metabolic use. |
| GR | 1.75 |  ok | Glucose Ratio; >2 indicates excess glycolytic bias. |
| MES | 22.5 |  ok | Metabolic Efficiency Score; >20 is good endurance economy. |
| RecoveryIndex | 0.622 |  ok | 0.6–1.0 means recovered; <0.5 = heavy fatigue. |
| ACWR_Risk | nan |  ok | Used internally for stability check. |
| StressTolerance | 1.18 |  ok | 2–8 indicates sustainable training strain capacity. |


### Power Zones
| Zone | % Time |
|:-- |:--|
| power_z1 | 20.4 |
| power_z2 | 40.6 |
| power_z3 | 13.0 |
| power_z4 | 7.2 |
| power_z5 | 3.1 |
| power_z6 | 2.7 |
| power_z7 | 0.7 |
| power_z8 | 12.3 |


### Heart Rate Zones
| Zone | % Time |
|:-- |:--|
| hr_z1 | 75.0 |
| hr_z2 | 11.5 |
| hr_z3 | 5.5 |
| hr_z4 | 4.8 |
| hr_z5 | 1.7 |
| hr_z6 | 1.3 |
| hr_z7 | 0.3 |


_No pace zone data available._


## ⚠️ Outlier Events

| Date | Event | Issue | Observation |
|:-- |:-- |:-- |:--|
| 2025-11-15 | Perry | TSS outlier | TSS=178 |


## 💓 Wellness & Recovery

- Rest Days: 2
- Resting HR: 42.7 bpm
- HRV: nan ms (→ stable, prev 46.0 ms)
- Fatigue: 1.5/5
- Stress: 1.5/5
- Readiness: nan/5
- ATL: 83.73 · CTL: 89.76 · TSB: 6.03


## 🧠 Performance & Coaching Actions


**Recommended Actions:**
1. ✅ Maintain ≥70 % Z1–Z2 volume (Seiler 80/20).
2. ⚠ Improve Zone 2 efficiency: extend duration or adjust IF.
3. ✅ Durability improving (1.00) — maintain current long-ride structure.
4. ⚠ Load intensity low (LIR=0.00) — add tempo or sweet-spot intervals.
5. ✅ Endurance reserve strong (1.00).
6. ✅ Efficiency drift stable (0.00%).
7. ✅ Polarisation optimal (90%).
8. 🟠 Recovery Index moderate (0.62) — monitor fatigue trend.


## 🚴 Weekly Events Summary

| date | name | icu_training_load | moving_time | distance |
|:-- |:-- |:-- |:-- |:--|
| 2025-11-15 | Perry | 178 | 02:24:04 | 67.5 |
| 2025-11-15 | Otto walk | 28 | 01:26:29 | 6.9 |
| 2025-11-13 | Zwift - Group Ride: DBR Base Endurance Ride | 88 | 01:31:47 | 58.3 |
| 2025-11-12 | Zwift - 90 base sometimes with coco | 63 | 01:33:49 | 60.4 |
| 2025-11-11 | Otto Walk | 20 | 01:31:04 | 7.0 |
| 2025-11-11 | Zwift - Tick Tock in Watopia | 6 | 00:10:13 | 6.4 |
| 2025-11-11 | zAlp low cadence | 88 | 01:23:00 | 35.9 |

**Totals:** 6.25 h · 188.1 km · 310 TSS · 7 sessions**
**Cycling Metrics — Mean IF:** 0.69 · **Mean HR:** 117 bpm · **VO₂ max:** 64.7

---
✅ **Audit Completed:** 2025-11-17T13:49:19.193510
**Framework:** URF v5.1 · Core: v16.14 · Enforcement: —