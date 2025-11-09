# 🧾 Full Weekly Audit Report

## Execution Logs

```
🧭 Running Weekly Report (auditFinal=True, render_mode=full)
🧩 Tier-0 reset: cleared totalHours/TSS/distance before aggregation
🧹 Tier-0 purge enforced — previous cache cleared.
[T0] Fetching athlete profile via OAuth2: https://intervals.icu/api/v1/athlete/0/profile
[T0] Athlete profile fetched successfully — id=1914741 name=Clive King
[Tier-0 fetch] chunk_start=2025-11-03  chunk_end=2025-11-09
🧩 Tier-0 deduplication: 0 duplicates removed.
[T0] Canonical slice → 10/10 rows retained (2025-11-03–2025-11-09, tz=Europe/Zurich)
[DEBUG-T0] Expanded icu_zone_times → 8 numeric columns
[DEBUG-T0] Expanded icu_hr_zone_times → 7 numeric columns
[T0] Diagnostic: true Σ(event.moving_time)=38255 s → 10.63 h
[T0] Canonical totals → Σ(TSS)=576.0
[DEBUG] wellness raw: <class 'pandas.core.frame.DataFrame'> 7
[DEBUG] wellness columns: ['id', 'ctl', 'atl', 'rampRate', 'ctlLoad', 'atlLoad', 'sportInfo', 'updated', 'weight', 'restingHR', 'hrv', 'hrvSDNN', 'menstrualPhase', 'menstrualPhasePredicted', 'kcalConsumed', 'sleepSecs', 'sleepScore', 'sleepQuality', 'avgSleepingHR', 'soreness', 'fatigue', 'stress', 'mood', 'motivation', 'injury', 'spO2', 'systolic', 'diastolic', 'hydration', 'hydrationVolume', 'readiness', 'baevskySI', 'bloodGlucose', 'lactate', 'bodyFat', 'abdomen', 'vo2max', 'comments', 'steps', 'respiration', 'locked', 'tempWeight', 'tempRestingHR']
[DEBUG] wellness head:
            id        ctl        atl  ...  locked  tempWeight  tempRestingHR
0  2025-11-03  91.914795  91.608640  ...    None        True          False
1  2025-11-04  91.210950  87.667076  ...    None        True          False
2  2025-11-05  89.064910  75.996650  ...    None       False          False
3  2025-11-06  88.851630  76.529590  ...    None        True          False
4  2025-11-07  90.949140  90.037544  ...    None        True          False

[5 rows x 43 columns]
[T0] Pre-audit complete: activities=10, wellness_rows=7
⚙️ Controller normalization: detected seconds, no conversion (max=8568)
[T1] Columns at entry: ['id', 'start_date_local', 'icu_training_load', 'elapsed_time', 'name', 'start_date', 'distance', 'moving_time', 'icu_zone_times', 'icu_hr_zone_times', 'date', 'origin', 'power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8', 'hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7']
🧮 Tier-1: using true Σ(event.moving_time)=38255 s → 10.63 h
[T1] Wellness alignment window (tz-aware): 2025-11-03 17:09:50+01:00 → 2025-11-08 11:49:24+01:00
[T1] Wellness date range: 2025-11-03 → 2025-11-09
✅ Wellness alignment check passed.
[DEBUG-T1] merging load metrics from wellness: ['ctl', 'atl']
[DEBUG-T1] derived TSB column added from CTL-ATL.
[DEBUG-T1] promoted CTL=91.23 ATL=89.53 TSB=1.69 to context.
[DEBUG-T1] injected load_metrics for renderer: {'CTL': {'value': 91.23, 'status': 'ok'}, 'ATL': {'value': 89.53, 'status': 'ok'}, 'TSB': {'value': 1.69, 'status': 'ok'}}
[DEBUG-T1] sample merged CTL/ATL/TSB:         date       ctl        atl
0 2025-11-08  91.67972  94.292450
1 2025-11-08  91.67972  94.292450
2 2025-11-07  90.94914  90.037544
3 2025-11-07  90.94914  90.037544
4 2025-11-06  88.85163  76.529590
[DEBUG-T1] sanity check before Step 6b — rows in df_activities: 10
[DEBUG-T1] athleteProfile present: True
[DEBUG-T1] athleteProfile keys: ['athlete_id', 'name', 'discipline', 'ftp', 'weight', 'hr_rest', 'hr_max', 'ftp_wkg', 'hr_reserve', 'zone_model', 'training_age_years', 'preferred_units', 'environment', 'timezone', 'updated']
[DEBUG-T1] Starting zone distribution extraction...
[DEBUG-T1] Activity columns sample: ['id', 'start_date_local', 'icu_training_load', 'elapsed_time', 'name', 'start_date', 'distance', 'moving_time', 'icu_zone_times', 'icu_hr_zone_times', 'date', 'origin', 'power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8', 'hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7', 'ctl', 'atl', 'tsb']
[DEBUG-ZONE] Available columns: ['id', 'start_date_local', 'icu_training_load', 'elapsed_time', 'name', 'start_date', 'distance', 'moving_time', 'icu_zone_times', 'icu_hr_zone_times', 'date', 'origin', 'power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8', 'hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7', 'ctl', 'atl', 'tsb']
[DEBUG-ZONE] Detected Power zone columns: ['icu_zone_times', 'power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8']
[DEBUG-ZONE] Detected HR zone columns: ['icu_hr_zone_times', 'hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7']
[DEBUG-ZONE] Detected Pace zone columns: []
[DEBUG-ZONES] power zones computed: {'power_z1': 22.1, 'power_z2': 37.0, 'power_z3': 17.9, 'power_z4': 6.6, 'power_z5': 3.8, 'power_z6': 3.3, 'power_z7': 0.5, 'power_z8': 8.8}
[DEBUG-ZONES] hr zones computed: {'hr_z1': 55.6, 'hr_z2': 18.9, 'hr_z3': 5.5, 'hr_z4': 9.3, 'hr_z5': 3.9, 'hr_z6': 3.7, 'hr_z7': 3.3}
[DEBUG-ZONES] No pace columns found — skipping.
[DEBUG-T1] Completed zone distribution extraction.
[DEBUG-T1] Zone distributions now in context:
  zone_dist_power: {'power_z1': 22.1, 'power_z2': 37.0, 'power_z3': 17.9, 'power_z4': 6.6, 'power_z5': 3.8, 'power_z6': 3.3, 'power_z7': 0.5, 'power_z8': 8.8}
  zone_dist_hr: {'hr_z1': 55.6, 'hr_z2': 18.9, 'hr_z3': 5.5, 'hr_z4': 9.3, 'hr_z5': 3.9, 'hr_z6': 3.7, 'hr_z7': 3.3}
  zone_dist_pace: {}
[DEBUG-T1] Outlier events detected: 1
[DEBUG-OUTLIER] mean TSS: 57.6 std: 50.618837073432125
[DEBUG-OUTLIER] min/max TSS: 8 / 161
[T2] Daily completeness summary built — 5 rows
🔍 Tier-2 enforcement source: Tier-2 validated events (10 rows)
origin counts:
 origin
event    10
Name: count, dtype: int64
moving_time stats:
 count      10.00000
mean     3825.50000
std      2680.13475
min       782.00000
25%      1653.00000
50%      3640.00000
75%      5385.00000
max      8568.00000
Name: moving_time, dtype: float64
🧮 Tier-2: using true Σ(event.moving_time)=38255 s → 10.63 h
[DEBUG-T2] enforced load_metrics sync in context: {'CTL': {'value': 91.23, 'status': 'ok'}, 'ATL': {'value': 89.53, 'status': 'ok'}, 'TSB': {'value': 1.69, 'status': 'ok'}}
[T1] Wellness alignment window (tz-aware): 2025-11-03 17:09:50+01:00 → 2025-11-08 11:49:24+01:00
[T1] Wellness date range: 2025-11-03 → 2025-11-09
✅ Wellness alignment check passed.
[DEBUG] Derived metrics synced: {'ACWR': 0.0, 'Monotony': 2.51, 'Strain': 1445.8, 'Polarisation': 0.0, 'RecoveryIndex': 0.498}
[DEBUG-T2X] post-extended load_metrics: {'CTL': {'value': 91.23, 'status': 'ok'}, 'ATL': {'value': 89.53, 'status': 'ok'}, 'TSB': {'value': 1.69, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.51), 'status': 'ok'}, 'Strain': {'value': np.float64(1445.8), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.498), 'status': 'ok'}}
[PATCH-LOCK] Preserved load_metrics before validator: {'CTL': {'value': 91.23, 'status': 'ok'}, 'ATL': {'value': 89.53, 'status': 'ok'}, 'TSB': {'value': 1.69, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.51), 'status': 'ok'}, 'Strain': {'value': np.float64(1445.8), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.498), 'status': 'ok'}}
[DEBUG] Derived metrics synced: {'ACWR': 0.0, 'Monotony': 2.51, 'Strain': 1445.8, 'Polarisation': 0.0, 'RecoveryIndex': 0.498}
[DEBUG-T2X] post-extended load_metrics: {'CTL': {'value': 91.23, 'status': 'ok'}, 'ATL': {'value': 89.53, 'status': 'ok'}, 'TSB': {'value': 1.69, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.51), 'status': 'ok'}, 'Strain': {'value': np.float64(1445.8), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.498), 'status': 'ok'}}
[PATCH-LOCKPOSTEXTENDED] Preserved load_metrics after extended: {'CTL': {'value': 91.23, 'status': 'ok'}, 'ATL': {'value': 89.53, 'status': 'ok'}, 'TSB': {'value': 1.69, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.51), 'status': 'ok'}, 'Strain': {'value': np.float64(1445.8), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.498), 'status': 'ok'}}
[PATCH-RESTORE] Reinstated locked load_metrics before finalizer: {'CTL': {'value': 91.23, 'status': 'ok'}, 'ATL': {'value': 89.53, 'status': 'ok'}, 'TSB': {'value': 1.69, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.51), 'status': 'ok'}, 'Strain': {'value': np.float64(1445.8), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.498), 'status': 'ok'}}
[DEBUG-FINALIZER-ENTRY] load_metrics: {'CTL': {'value': 91.23, 'status': 'ok'}, 'ATL': {'value': 89.53, 'status': 'ok'}, 'TSB': {'value': 1.69, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.51), 'status': 'ok'}, 'Strain': {'value': np.float64(1445.8), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.498), 'status': 'ok'}}
⚠ uicomponents not found — using empty ICON_CARDS reference.
🔎 Render pre-flight — totals by source:
   df_events Σmoving_time = 10.626388888888888
   dailyMerged has no time-like column
   eventTotals(hours) = 10.63

[Tier-2 context diagnostic]
derived_metrics: True
load_metrics: True
adaptation_metrics: True
trend_metrics: True
correlation_metrics: True
[DEBUG-FINALIZER] pre-render load_metrics: {'CTL': {'value': 91.23, 'status': 'ok'}, 'ATL': {'value': 89.53, 'status': 'ok'}, 'TSB': {'value': 1.69, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.51), 'status': 'ok'}, 'Strain': {'value': np.float64(1445.8), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.498), 'status': 'ok'}}
[Renderer shim] Delegating to render_report() in render_unified_report.py

[DEBUG-TEMPLATE: PRE-CALL]
Keys in context: ['totalDistance', 'auditPartial', 'auditFinal', 'purge_enforced', 'timezone', 'athleteProfile', 'athlete', 'report_mode', 'window_start', 'window_end', 'window_summary', 'knowledge', 'tier1_eventTotals', 'df_events', 'dailyMerged', 'ctl', 'atl', 'tsb', 'load_metrics', 'zone_dist_power', 'zone_dist_hr', 'zone_dist_pace', 'outliers', 'totalHours', 'totalTss', 'eventTotals', 'df_event_only', 'enforcement_layer', '_locked_totals', 'locked_totalHours', 'locked_totalTss', 'locked_totalDistance', 'event_count', 'trace', 'derived_metrics', 'trend_series', 'metrics', 'ACWR', 'Monotony', 'Strain', 'FatigueTrend', 'ZQI', 'FatOxEfficiency', 'Polarisation', 'FOxI', 'CUR', 'GR', 'MES', 'RecoveryIndex', 'ACWR_Risk', 'StressTolerance', 'phases', 'ui_flag', 'actions', '_locked_load_metrics', 'adaptation_metrics', 'trend_metrics', 'correlation_metrics', 'Duration_total', 'icon_pack', 'force_icon_pack', 'event_log_text']
load_metrics pre-pass: {'CTL': {'value': 91.23, 'status': 'ok'}, 'ATL': {'value': 89.53, 'status': 'ok'}, 'TSB': {'value': 1.69, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.51), 'status': 'ok'}, 'Strain': {'value': np.float64(1445.8), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.498), 'status': 'ok'}}
_locked_load_metrics pre-pass: {'CTL': {'value': 91.23, 'status': 'ok'}, 'ATL': {'value': 89.53, 'status': 'ok'}, 'TSB': {'value': 1.69, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.51), 'status': 'ok'}, 'Strain': {'value': np.float64(1445.8), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.498), 'status': 'ok'}}
Report type: weekly
------------------------------------------------------------
[DEBUG-RENDER] incoming load_metrics: {
  "CTL": {
    "value": 91.23,
    "status": "ok"
  },
  "ATL": {
    "value": 89.53,
    "status": "ok"
  },
  "TSB": {
    "value": 1.69,
    "status": "ok"
  },
  "ACWR": {
    "value": NaN,
    "status": "ok"
  },
  "Monotony": {
    "value": 2.51,
    "status": "ok"
  },
  "Strain": {
    "value": 1445.8,
    "status": "ok"
  },
  "Polarisation": {
    "value": 0.0,
    "status": "ok"
  },
  "RecoveryIndex": {
    "value": 0.498,
    "status": "ok"
  }
}

[DEBUG-TEMPLATE: POST-CALL]
Renderer function executed: render_report
Result type: Report
Result keys: ['header', 'markdown', 'type', 'context', 'sections', 'tables', 'lines', 'summary', 'metrics', 'actions', 'phases', 'trends', 'correlation', 'footer']
load_metrics still in context: True
load_metrics post-render: {'CTL': {'value': 91.23, 'status': 'ok'}, 'ATL': {'value': 89.53, 'status': 'ok'}, 'TSB': {'value': 1.69, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.51), 'status': 'ok'}, 'Strain': {'value': np.float64(1445.8), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.498), 'status': 'ok'}}
------------------------------------------------------------
[DEBUG-TEMPLATE] Renderer returned a Report object.
✅ Report validated — framework compliant.
✅ Report schema validated.

[DEBUG] Context keys available before finalize_and_validate_render() return:
  - ACWR
  - ACWR_Risk
  - CUR
  - Duration_total
  - FOxI
  - FatOxEfficiency
  - FatigueTrend
  - GR
  - ICON_CARDS
  - MES
  - Monotony
  - Polarisation
  - RecoveryIndex
  - Strain
  - StressTolerance
  - ZQI
  - _locked_load_metrics
  - _locked_totals
  - actions
  - adaptation_metrics
  - athlete
  - athleteProfile
  - atl
  - auditFinal
  - auditPartial
  - correlation_metrics
  - ctl
  - dailyMerged
  - derived_metrics
  - df_event_only
  - df_events
  - enforcement_layer
  - eventTotals
  - event_count
  - event_log_text
  - force_icon_pack
  - header
  - icon_pack
  - knowledge
  - load_metrics
  - locked_totalDistance
  - locked_totalHours
  - locked_totalTss
  - metrics
  - outliers
  - phases
  - purge_enforced
  - report_mode
  - tier1_eventTotals
  - timezone
  - totalDistance
  - totalHours
  - totalTss
  - trace
  - trend_metrics
  - trend_series
  - tsb
  - ui_flag
  - window_end
  - window_start
  - window_summary
  - zone_dist_hr
  - zone_dist_pace
  - zone_dist_power
[DEBUG] End of context key list

✅ Report passed framework + schema validation (event-only, markdown).

```

## Rendered Markdown Report

# 🧭 weekly Training Report — URF v5.1
**Athlete:** Clive King
**Period:** ? → ?
**Timezone:** Europe/Zurich
**Generated:** 2025-11-09T08:21:16.109216

---


## 🧩 Tier-0 Dataset Integrity

- Activities fetched: 10
- Origin: tier2_enforce_event_only_totals
- Purge enforced: True
- Wellness records: n/a
- Source verification: ✅ Live (no mock/cache)
- Σ(moving_time)/3600 = 10.63 h  |  Σ(TSS) = 576


## 🧩 Tier-1 Audit Controller

- Deduplication: OK
- HR stream coverage: —
- Power data coverage: —
- Time variance ≤ 0.1 h ✅


## 🧮 Derived Metric Audit

| Metric | Value | Status |
|:-- |:-- |:--|
| ACWR | nan | ✅ |
| Monotony | 2.51 | ✅ |
| Strain | 1445.8 | ✅ |
| FatigueTrend | -0.107 | ✅ |
| ZQI | nan | ✅ |
| FatOxEfficiency | 0.0 | ✅ |
| Polarisation | 0.0 | ✅ |
| FOxI | 0.0 | ✅ |
| CUR | 250.0 | ✅ |
| GR | 0.0 | ✅ |
| MES | 0.0 | ✅ |
| RecoveryIndex | 0.498 | ✅ |
| ACWR_Risk | ✅ | ✅ |
| StressTolerance | 5.76 | ✅ |
### Power Zones
| Zone | % Time |
|:-- |:--|
| power_z1 | 22.1 |
| power_z2 | 37.0 |
| power_z3 | 17.9 |
| power_z4 | 6.6 |
| power_z5 | 3.8 |
| power_z6 | 3.3 |
| power_z7 | 0.5 |
| power_z8 | 8.8 |

### Heart Rate Zones
| Zone | % Time |
|:-- |:--|
| hr_z1 | 55.6 |
| hr_z2 | 18.9 |
| hr_z3 | 5.5 |
| hr_z4 | 9.3 |
| hr_z5 | 3.9 |
| hr_z6 | 3.7 |
| hr_z7 | 3.3 |
_No pace zone data available._
_No outliers detected._


## 💓 Wellness & Recovery

- Rest Days: —
- Resting HR: — bpm
- HRV Trend: —
- ATL: 89.53 · CTL: 91.23 · TSB: 1.69


## ⚖️ Load & Stress Chain

| Metric | Value | Status |
|:-- |:-- |:--|
| CTL | 91.23 | ok |
| ATL | 89.53 | ok |
| TSB | 1.69 | ok |
| ACWR | nan | ok |
| Monotony | 2.51 | ok |
| Strain | 1445.8 | ok |
| Polarisation | 0.0 | ok |
| RecoveryIndex | 0.498 | ok |


## 🔬 Efficiency & Adaptation

- Efficiency Factor: 1.9
- Fatigue Resistance: 0.95
- Endurance Decay: 0.02
- Z2 Stability: 0.04
- Aerobic Decay: 0.02


## 🧠 Performance & Coaching Actions


**Recommended Actions:**
1. ⚠ Increase Z1–Z2 share to ≥70 % (Seiler 80/20).
2. ⚠ Improve Zone 2 efficiency: extend duration or adjust IF.
3. ⚠ Apply 10–15 % deload (Friel microcycle logic).


## 🚴 Weekly Events Summary

_No event preview available._

---
✅ **Audit Completed:** 2025-11-09T08:21:16.109305
**Framework:** URF v5.1 · Core: v16.14 · Enforcement: tier2_enforce_event_only_totals

