# 🧾 Full Weekly Audit Report

## Execution Logs

```
🧭 Running Weekly Report (auditFinal=True, render_mode=full)
🧩 Tier-0 reset: cleared totalHours/TSS/distance before aggregation
🧹 Tier-0 purge enforced — previous cache cleared.
[T0] Fetching athlete profile via OAuth2: https://intervals.icu/api/v1/athlete/0/profile
[T0] Athlete profile fetched successfully — id=1914741 name=Clive King
[Tier-0 fetch] chunk_start=2025-11-04  chunk_end=2025-11-10
🧩 Tier-0 deduplication: 0 duplicates removed.
[T0] Canonical slice → 9/9 rows retained (2025-11-04–2025-11-10, tz=Europe/Zurich)
[DEBUG-T0] Expanded icu_zone_times → 8 numeric columns
[DEBUG-T0] Expanded icu_hr_zone_times → 7 numeric columns
[T0] Diagnostic: true Σ(event.moving_time)=43693 s → 12.14 h
[T0] Canonical totals → Σ(TSS)=588.0
[DEBUG] wellness raw: <class 'pandas.core.frame.DataFrame'> 7
[DEBUG] wellness columns: ['id', 'ctl', 'atl', 'rampRate', 'ctlLoad', 'atlLoad', 'sportInfo', 'updated', 'weight', 'restingHR', 'hrv', 'hrvSDNN', 'menstrualPhase', 'menstrualPhasePredicted', 'kcalConsumed', 'sleepSecs', 'sleepScore', 'sleepQuality', 'avgSleepingHR', 'soreness', 'fatigue', 'stress', 'mood', 'motivation', 'injury', 'spO2', 'systolic', 'diastolic', 'hydration', 'hydrationVolume', 'readiness', 'baevskySI', 'bloodGlucose', 'lactate', 'bodyFat', 'abdomen', 'vo2max', 'comments', 'steps', 'respiration', 'locked', 'tempWeight', 'tempRestingHR']
[DEBUG] wellness head:
            id       ctl        atl  ...  locked  tempWeight  tempRestingHR
0  2025-11-04  91.21095  87.667076  ...    None        True          False
1  2025-11-05  89.06491  75.996650  ...    None       False          False
2  2025-11-06  88.85163  76.529590  ...    None        True          False
3  2025-11-07  90.94914  90.037544  ...    None        True          False
4  2025-11-08  91.67972  94.292450  ...    None       False          False

[5 rows x 43 columns]
[T0] Pre-audit complete: activities=9, wellness_rows=7
⚙️ Controller normalization: detected seconds, no conversion (max=8568)
[T1] Columns at entry: ['id', 'start_date_local', 'icu_training_load', 'elapsed_time', 'name', 'start_date', 'distance', 'moving_time', 'icu_zone_times', 'icu_hr_zone_times', 'date', 'origin', 'power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8', 'hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7']
🧮 Tier-1: using true Σ(event.moving_time)=43693 s → 12.14 h
[T1] Wellness alignment window (tz-aware): 2025-11-04 17:43:18+01:00 → 2025-11-09 12:14:22+01:00
[T1] Wellness date range: 2025-11-04 → 2025-11-10
✅ Wellness alignment check passed.
[DEBUG-T1] merging load metrics from wellness: ['ctl', 'atl']
[DEBUG-T1] derived TSB column added from CTL-ATL.
[DEBUG-T1] promoted CTL=91.38 ATL=91.43 TSB=-0.05 to context.
[DEBUG-T1] injected load_metrics for renderer: {'CTL': {'value': 91.38, 'status': 'ok'}, 'ATL': {'value': 91.43, 'status': 'ok'}, 'TSB': {'value': -0.05, 'status': 'ok'}}
[DEBUG-T1] sample merged CTL/ATL/TSB:         date       ctl         atl
0 2025-11-09  92.95778  101.175865
1 2025-11-09  92.95778  101.175865
2 2025-11-08  91.67972   94.292450
3 2025-11-08  91.67972   94.292450
4 2025-11-07  90.94914   90.037544
[DEBUG-T1] sanity check before Step 6b — rows in df_activities: 9
[DEBUG-T1] athleteProfile present: True
[DEBUG-T1] athleteProfile keys: ['athlete_id', 'name', 'discipline', 'ftp', 'weight', 'hr_rest', 'hr_max', 'ftp_wkg', 'hr_reserve', 'zone_model', 'training_age_years', 'preferred_units', 'environment', 'timezone', 'updated']
[DEBUG-T1] Starting zone distribution extraction...
[DEBUG-T1] Activity columns sample: ['id', 'start_date_local', 'icu_training_load', 'elapsed_time', 'name', 'start_date', 'distance', 'moving_time', 'icu_zone_times', 'icu_hr_zone_times', 'date', 'origin', 'power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8', 'hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7', 'ctl', 'atl', 'tsb']
[DEBUG-ZONE] Available columns: ['id', 'start_date_local', 'icu_training_load', 'elapsed_time', 'name', 'start_date', 'distance', 'moving_time', 'icu_zone_times', 'icu_hr_zone_times', 'date', 'origin', 'power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8', 'hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7', 'ctl', 'atl', 'tsb']
[DEBUG-ZONE] Detected Power zone columns: ['icu_zone_times', 'power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8']
[DEBUG-ZONE] Detected HR zone columns: ['icu_hr_zone_times', 'hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7']
[DEBUG-ZONE] Detected Pace zone columns: []
[DEBUG-ZONES] power zones computed: {'power_z1': 26.8, 'power_z2': 35.4, 'power_z3': 16.6, 'power_z4': 6.2, 'power_z5': 2.9, 'power_z6': 3.0, 'power_z7': 0.6, 'power_z8': 8.4}
[DEBUG-ZONES] hr zones computed: {'hr_z1': 66.3, 'hr_z2': 18.3, 'hr_z3': 3.7, 'hr_z4': 6.0, 'hr_z5': 2.3, 'hr_z6': 1.7, 'hr_z7': 1.7}
[DEBUG-ZONES] No pace columns found — skipping.
[DEBUG-T1] Completed zone distribution extraction.
[DEBUG-T1] Zone distributions now in context:
  zone_dist_power: {'power_z1': 26.8, 'power_z2': 35.4, 'power_z3': 16.6, 'power_z4': 6.2, 'power_z5': 2.9, 'power_z6': 3.0, 'power_z7': 0.6, 'power_z8': 8.4}
  zone_dist_hr: {'hr_z1': 66.3, 'hr_z2': 18.3, 'hr_z3': 3.7, 'hr_z4': 6.0, 'hr_z5': 2.3, 'hr_z6': 1.7, 'hr_z7': 1.7}
  zone_dist_pace: {}
[DEBUG-T1] Outlier events detected: 0
[DEBUG-OUTLIER] mean TSS: 65.33333333333333 std: 57.19702789481286
[DEBUG-OUTLIER] min/max TSS: 10 / 161
[T2] Daily completeness summary built — 5 rows
🔍 Tier-2 enforcement source: Tier-2 validated events (9 rows)
origin counts:
 origin
event    9
Name: count, dtype: int64
moving_time stats:
 count       9.000000
mean     4854.777778
std      2661.860054
min       933.000000
25%      3644.000000
50%      4239.000000
75%      7238.000000
max      8568.000000
Name: moving_time, dtype: float64
🧮 Tier-2: using true Σ(event.moving_time)=43693 s → 12.14 h
[DEBUG-T2] enforced load_metrics sync in context: {'CTL': {'value': 91.38, 'status': 'ok'}, 'ATL': {'value': 91.43, 'status': 'ok'}, 'TSB': {'value': -0.05, 'status': 'ok'}}
[T1] Wellness alignment window (tz-aware): 2025-11-04 17:43:18+01:00 → 2025-11-09 12:14:22+01:00
[T1] Wellness date range: 2025-11-04 → 2025-11-10
✅ Wellness alignment check passed.
[DEBUG] Derived metrics synced: {'ACWR': 0.0, 'Monotony': 2.48, 'Strain': 1458.2, 'Polarisation': 0.0, 'RecoveryIndex': 0.504}
[DEBUG-T2X] post-extended load_metrics: {'CTL': {'value': 91.38, 'status': 'ok'}, 'ATL': {'value': 91.43, 'status': 'ok'}, 'TSB': {'value': -0.05, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.48), 'status': 'ok'}, 'Strain': {'value': np.float64(1458.2), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.504), 'status': 'ok'}}
[PATCH-LOCK] Preserved load_metrics before validator: {'CTL': {'value': 91.38, 'status': 'ok'}, 'ATL': {'value': 91.43, 'status': 'ok'}, 'TSB': {'value': -0.05, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.48), 'status': 'ok'}, 'Strain': {'value': np.float64(1458.2), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.504), 'status': 'ok'}}
[DEBUG] Derived metrics synced: {'ACWR': 0.0, 'Monotony': 2.48, 'Strain': 1458.2, 'Polarisation': 0.0, 'RecoveryIndex': 0.504}
[DEBUG-T2X] post-extended load_metrics: {'CTL': {'value': 91.38, 'status': 'ok'}, 'ATL': {'value': 91.43, 'status': 'ok'}, 'TSB': {'value': -0.05, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.48), 'status': 'ok'}, 'Strain': {'value': np.float64(1458.2), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.504), 'status': 'ok'}}
[PATCH-LOCKPOSTEXTENDED] Preserved load_metrics after extended: {'CTL': {'value': 91.38, 'status': 'ok'}, 'ATL': {'value': 91.43, 'status': 'ok'}, 'TSB': {'value': -0.05, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.48), 'status': 'ok'}, 'Strain': {'value': np.float64(1458.2), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.504), 'status': 'ok'}}
[PATCH-RESTORE] Reinstated locked load_metrics before finalizer: {'CTL': {'value': 91.38, 'status': 'ok'}, 'ATL': {'value': 91.43, 'status': 'ok'}, 'TSB': {'value': -0.05, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.48), 'status': 'ok'}, 'Strain': {'value': np.float64(1458.2), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.504), 'status': 'ok'}}
[DEBUG-FINALIZER-ENTRY] load_metrics: {'CTL': {'value': 91.38, 'status': 'ok'}, 'ATL': {'value': 91.43, 'status': 'ok'}, 'TSB': {'value': -0.05, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.48), 'status': 'ok'}, 'Strain': {'value': np.float64(1458.2), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.504), 'status': 'ok'}}
⚠ uicomponents not found — using empty ICON_CARDS reference.
🔎 Render pre-flight — totals by source:
   df_events Σmoving_time = 12.136944444444444
   dailyMerged has no time-like column
   eventTotals(hours) = 12.14

[Tier-2 context diagnostic]
derived_metrics: True
load_metrics: True
adaptation_metrics: True
trend_metrics: True
correlation_metrics: True
[DEBUG-FINALIZER] pre-render load_metrics: {'CTL': {'value': 91.38, 'status': 'ok'}, 'ATL': {'value': 91.43, 'status': 'ok'}, 'TSB': {'value': -0.05, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.48), 'status': 'ok'}, 'Strain': {'value': np.float64(1458.2), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.504), 'status': 'ok'}}
[Renderer shim] Delegating to render_report() in render_unified_report.py

[DEBUG-TEMPLATE: PRE-CALL]
Keys in context: ['totalDistance', 'auditPartial', 'auditFinal', 'purge_enforced', 'timezone', 'athleteProfile', 'athlete', 'report_mode', 'window_start', 'window_end', 'window_summary', 'knowledge', 'tier1_eventTotals', 'df_events', 'dailyMerged', 'ctl', 'atl', 'tsb', 'load_metrics', 'zone_dist_power', 'zone_dist_hr', 'zone_dist_pace', 'outliers', 'totalHours', 'totalTss', 'eventTotals', 'df_event_only', 'enforcement_layer', '_locked_totals', 'locked_totalHours', 'locked_totalTss', 'locked_totalDistance', 'event_count', 'trace', 'derived_metrics', 'trend_series', 'metrics', 'ACWR', 'Monotony', 'Strain', 'FatigueTrend', 'ZQI', 'FatOxEfficiency', 'Polarisation', 'FOxI', 'CUR', 'GR', 'MES', 'RecoveryIndex', 'ACWR_Risk', 'StressTolerance', 'phases', 'ui_flag', 'actions', '_locked_load_metrics', 'adaptation_metrics', 'trend_metrics', 'correlation_metrics', 'Duration_total', 'icon_pack', 'force_icon_pack', 'event_log_text']
load_metrics pre-pass: {'CTL': {'value': 91.38, 'status': 'ok'}, 'ATL': {'value': 91.43, 'status': 'ok'}, 'TSB': {'value': -0.05, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.48), 'status': 'ok'}, 'Strain': {'value': np.float64(1458.2), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.504), 'status': 'ok'}}
_locked_load_metrics pre-pass: {'CTL': {'value': 91.38, 'status': 'ok'}, 'ATL': {'value': 91.43, 'status': 'ok'}, 'TSB': {'value': -0.05, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.48), 'status': 'ok'}, 'Strain': {'value': np.float64(1458.2), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.504), 'status': 'ok'}}
Report type: weekly
------------------------------------------------------------
[DEBUG-RENDER] incoming load_metrics: {
  "CTL": {
    "value": 91.38,
    "status": "ok"
  },
  "ATL": {
    "value": 91.43,
    "status": "ok"
  },
  "TSB": {
    "value": -0.05,
    "status": "ok"
  },
  "ACWR": {
    "value": NaN,
    "status": "ok"
  },
  "Monotony": {
    "value": 2.48,
    "status": "ok"
  },
  "Strain": {
    "value": 1458.2,
    "status": "ok"
  },
  "Polarisation": {
    "value": 0.0,
    "status": "ok"
  },
  "RecoveryIndex": {
    "value": 0.504,
    "status": "ok"
  }
}

[DEBUG-TEMPLATE: POST-CALL]
Renderer function executed: render_report
Result type: Report
Result keys: ['header', 'markdown', 'type', 'context', 'sections', 'tables', 'lines', 'summary', 'metrics', 'actions', 'phases', 'trends', 'correlation', 'footer']
load_metrics still in context: True
load_metrics post-render: {'CTL': {'value': 91.38, 'status': 'ok'}, 'ATL': {'value': 91.43, 'status': 'ok'}, 'TSB': {'value': -0.05, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.48), 'status': 'ok'}, 'Strain': {'value': np.float64(1458.2), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.504), 'status': 'ok'}}
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
**Generated:** 2025-11-10T14:57:50.955279

---


## 🧩 Tier-0 Dataset Integrity

- Activities fetched: 9
- Origin: tier2_enforce_event_only_totals
- Purge enforced: True
- Wellness records: n/a
- Source verification: ✅ Live (no mock/cache)
- Σ(moving_time)/3600 = 12.14 h  |  Σ(TSS) = 588


## 🧩 Tier-1 Audit Controller

- Deduplication: OK
- HR stream coverage: —
- Power data coverage: —
- Time variance ≤ 0.1 h ✅


## 🧮 Derived Metric Audit

| Metric | Value | Status |
|:-- |:-- |:--|
| ACWR | nan | ✅ |
| Monotony | 2.48 | ✅ |
| Strain | 1458.2 | ✅ |
| FatigueTrend | 1.034 | ✅ |
| ZQI | nan | ✅ |
| FatOxEfficiency | 0.0 | ✅ |
| Polarisation | 0.0 | ✅ |
| FOxI | 0.0 | ✅ |
| CUR | 250.0 | ✅ |
| GR | 0.0 | ✅ |
| MES | -0.0 | ✅ |
| RecoveryIndex | 0.504 | ✅ |
| ACWR_Risk | ✅ | ✅ |
| StressTolerance | 5.88 | ✅ |
### Power Zones
| Zone | % Time |
|:-- |:--|
| power_z1 | 26.8 |
| power_z2 | 35.4 |
| power_z3 | 16.6 |
| power_z4 | 6.2 |
| power_z5 | 2.9 |
| power_z6 | 3.0 |
| power_z7 | 0.6 |
| power_z8 | 8.4 |

### Heart Rate Zones
| Zone | % Time |
|:-- |:--|
| hr_z1 | 66.3 |
| hr_z2 | 18.3 |
| hr_z3 | 3.7 |
| hr_z4 | 6.0 |
| hr_z5 | 2.3 |
| hr_z6 | 1.7 |
| hr_z7 | 1.7 |
_No pace zone data available._


## ⚠️ Outlier Events

_No outliers detected._


## 💓 Wellness & Recovery

- Rest Days: —
- Resting HR: — bpm
- HRV Trend: —
- ATL: 91.43 · CTL: 91.38 · TSB: -0.05


## ⚖️ Load & Stress Chain

| Metric | Value | Status |
|:-- |:-- |:--|
| CTL | 91.38 | ok |
| ATL | 91.43 | ok |
| TSB | -0.05 | ok |
| ACWR | nan | ok |
| Monotony | 2.48 | ok |
| Strain | 1458.2 | ok |
| Polarisation | 0.0 | ok |
| RecoveryIndex | 0.504 | ok |


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
✅ **Audit Completed:** 2025-11-10T14:57:50.955374
**Framework:** URF v5.1 · Core: v16.14 · Enforcement: tier2_enforce_event_only_totals

