# 🧾 Full Weekly Audit Report

## Execution Logs

```
🧭 Running Weekly Report (auditFinal=True, render_mode=full)
🧩 Tier-0 reset: cleared totalHours/TSS/distance before aggregation
🧹 Tier-0 purge enforced — previous cache cleared.
[T0] Fetching athlete profile via OAuth2: https://intervals.icu/api/v1/athlete/0/profile
[T0] Athlete profile fetched successfully — id=1914741 name=Clive King
[Tier-0 fetch] chunk_start=2025-11-05  chunk_end=2025-11-11
🧩 Tier-0 deduplication: 0 duplicates removed.
[T0] Canonical slice → 8/8 rows retained (2025-11-05–2025-11-11, tz=Europe/Zurich)
[T0] Diagnostic: true Σ(event.moving_time)=44580 s → 12.38 h
[T0] Canonical totals → Σ(TSS)=546.0
[DEBUG] wellness raw: <class 'pandas.core.frame.DataFrame'> 7
[DEBUG] wellness columns: ['id', 'ctl', 'atl', 'rampRate', 'ctlLoad', 'atlLoad', 'sportInfo', 'updated', 'weight', 'restingHR', 'hrv', 'hrvSDNN', 'menstrualPhase', 'menstrualPhasePredicted', 'kcalConsumed', 'sleepSecs', 'sleepScore', 'sleepQuality', 'avgSleepingHR', 'soreness', 'fatigue', 'stress', 'mood', 'motivation', 'injury', 'spO2', 'systolic', 'diastolic', 'hydration', 'hydrationVolume', 'readiness', 'baevskySI', 'bloodGlucose', 'lactate', 'bodyFat', 'abdomen', 'vo2max', 'comments', 'steps', 'respiration', 'locked', 'tempWeight', 'tempRestingHR']
[DEBUG] wellness head:
            id       ctl         atl  ...  locked  tempWeight  tempRestingHR
0  2025-11-05  89.06491   75.996650  ...    None       False          False
1  2025-11-06  88.85163   76.529590  ...    None        True          False
2  2025-11-07  90.94914   90.037544  ...    None        True          False
3  2025-11-08  91.67972   94.292450  ...    None       False          False
4  2025-11-09  92.95778  101.175865  ...    None        True          False

[5 rows x 43 columns]
[T0] Pre-audit complete: activities=8, wellness_rows=7
⚙️ Normalization: detected seconds, no conversion (max=8568)
[T1] Columns at entry: ['id', 'start_date_local', 'icu_training_load', 'elapsed_time', 'name', 'start_date', 'distance', 'moving_time', 'icu_hr_zone_times', 'icu_zone_times', 'date', 'origin']
🧮 Tier-1: using enforced seconds→hours conversion (Σmoving_time=44580 s → 12.38 h)
[T1] Wellness alignment window (tz-aware): 2025-11-06 18:16:29+01:00 → 2025-11-11 13:11:48+01:00
[T1] Wellness date range: 2025-11-05 → 2025-11-11
✅ Wellness alignment check passed.
[DEBUG-T1] merging load metrics from wellness: ['ctl', 'atl']
[DEBUG-T1] derived TSB column added from CTL-ATL.
[DEBUG-T1] promoted CTL=91.14 ATL=90.78 TSB=0.36 to context.
[DEBUG-T1] injected load_metrics for renderer: {'CTL': {'value': 91.14, 'status': 'ok'}, 'ATL': {'value': 90.78, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}}
[DEBUG-T1] sample merged CTL/ATL/TSB:         date       ctl         atl
0 2025-11-11  89.10552   78.693810
1 2025-11-09  92.95778  101.175865
2 2025-11-09  92.95778  101.175865
3 2025-11-08  91.67972   94.292450
4 2025-11-08  91.67972   94.292450
[DEBUG-T1] sanity check before Step 6b — rows in df_activities: 8
[DEBUG-T1] athleteProfile present: True
[DEBUG-T1] athleteProfile keys: ['athlete_id', 'name', 'discipline', 'ftp', 'weight', 'hr_rest', 'hr_max', 'ftp_wkg', 'hr_reserve', 'zone_model', 'training_age_years', 'preferred_units', 'environment', 'timezone', 'updated']
[DEBUG-T1] Starting zone distribution extraction...
[DEBUG-T1] Activity columns sample: ['id', 'start_date_local', 'icu_training_load', 'elapsed_time', 'name', 'start_date', 'distance', 'moving_time', 'icu_hr_zone_times', 'icu_zone_times', 'date', 'origin', 'ctl', 'atl', 'tsb']
[DEBUG-ZONE] Available columns: ['id', 'start_date_local', 'icu_training_load', 'elapsed_time', 'name', 'start_date', 'distance', 'moving_time', 'icu_hr_zone_times', 'icu_zone_times', 'date', 'origin', 'ctl', 'atl', 'tsb']
[DEBUG-ZONE] Detected Power zone columns: ['icu_zone_times']
[DEBUG-ZONE] Detected HR zone columns: ['icu_hr_zone_times']
[DEBUG-ZONE] Detected Pace zone columns: []
[DEBUG-ZONES] No valid data for power zones — total=0.
[DEBUG-ZONES] No valid data for hr zones — total=0.
[DEBUG-ZONES] No pace columns found — skipping.
[DEBUG-T1] Completed zone distribution extraction.
[DEBUG-T1] Zone distributions now in context:
  zone_dist_power: {}
  zone_dist_hr: {}
  zone_dist_pace: {}
[DEBUG-T1] Outlier events detected: 0
[DEBUG-OUTLIER] mean TSS: 68.25 std: 59.66513698491416
[DEBUG-OUTLIER] min/max TSS: 12 / 161
None [T2] Daily completeness summary built — 5 rows
📁 Tier-2 module loaded from: C:\Users\user\onedrive\documents\git\revo2wheels\intervalsicugptcoach\audit_core\tier2_enforce_event_only_totals.py
🔍 Tier-2 enforcement source: Tier-2 validated events (8 rows)
origin counts:
 origin
event    8
Name: count, dtype: int64
moving_time stats:
 count       8.00000
mean     5572.50000
std      2270.55116
min      1582.00000
25%      4196.50000
50%      5615.50000
75%      7341.75000
max      8568.00000
Name: moving_time, dtype: float64
🧮 Tier-2: Σ(moving_time)=44580s → 12.38h (Intervals seconds source)
[DEBUG-T2] injected df_event_only preview: 8 rows (sorted by start_date_local)
[DEBUG-T2] enforced load_metrics sync in context: {'CTL': {'value': 91.14, 'status': 'ok'}, 'ATL': {'value': 90.78, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}}
[T1] Wellness alignment window (tz-aware): 2025-11-06 18:16:29+01:00 → 2025-11-11 13:11:48+01:00
[T1] Wellness date range: 2025-11-05 → 2025-11-11
✅ Wellness alignment check passed.
[DEBUG] Derived metrics synced: {'ACWR': 0.0, 'Monotony': 1.78, 'Strain': 971.9, 'Polarisation': 0.0, 'RecoveryIndex': 0.644}
[DEBUG-T2X] post-extended load_metrics: {'CTL': {'value': 91.14, 'status': 'ok'}, 'ATL': {'value': 90.78, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(1.78), 'status': 'ok'}, 'Strain': {'value': np.float64(971.9), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.644), 'status': 'ok'}}
[PATCH-LOCK] Preserved load_metrics before validator: {'CTL': {'value': 91.14, 'status': 'ok'}, 'ATL': {'value': 90.78, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(1.78), 'status': 'ok'}, 'Strain': {'value': np.float64(971.9), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.644), 'status': 'ok'}}
[DEBUG] Derived metrics synced: {'ACWR': 0.0, 'Monotony': 1.78, 'Strain': 971.9, 'Polarisation': 0.0, 'RecoveryIndex': 0.644}
[DEBUG-T2X] post-extended load_metrics: {'CTL': {'value': 91.14, 'status': 'ok'}, 'ATL': {'value': 90.78, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(1.78), 'status': 'ok'}, 'Strain': {'value': np.float64(971.9), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.644), 'status': 'ok'}}
🧩 Render mode forced to full+metrics for Unified 10-section layout
[TRACE-RUNTIME] entering finalize_and_validate_render()
[TRACE-RUNTIME] context type = <class 'dict'>
[TRACE-RUNTIME] df_events type = <class 'pandas.core.frame.DataFrame'>
[TRACE-RUNTIME] df_events.shape = (8, 12)
[TRACE-RUNTIME] Σ moving_time/3600 = 12.38 h
[TRACE-RUNTIME] Σ icu_training_load = 546
[DEBUG-FINALIZER-ENTRY] load_metrics: {'CTL': {'value': 91.14, 'status': 'ok'}, 'ATL': {'value': 90.78, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(1.78), 'status': 'ok'}, 'Strain': {'value': np.float64(971.9), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.644), 'status': 'ok'}}
✅ Loaded ICON_CARDS from UIcomponents.icon_pack
🔎 Render pre-flight — totals by source:
   df_events Σmoving_time = 12.383333333333333
   df_events Σicu_training_load = 546
   eventTotals(hours) = 12.38

[Tier-2 context diagnostic]
derived_metrics: True
load_metrics: True
adaptation_metrics: True
trend_metrics: True
correlation_metrics: True
[DEBUG] report_header injected: {'athlete': 'Clive King', 'discipline': 'cycling', 'report_type': 'weekly', 'framework': 'Unified_Reporting_Framework_v5.1', 'timezone': 'Europe/Zurich', 'date_range': '2025-11-05 → 2025-11-11'}
[DEBUG-FINALIZER] pre-render load_metrics: {'CTL': {'value': 91.14, 'status': 'ok'}, 'ATL': {'value': 90.78, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(1.78), 'status': 'ok'}, 'Strain': {'value': np.float64(971.9), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.644), 'status': 'ok'}}
[STATE-GUARD] _locked_load_metrics set (prevents recomputation)
[CANONICAL PROPAGATION] hours=12.38, tss=546
[LOCK] Tier-2 canonical totals re-locked before render
[TRACE-DF] Σ df_events(moving_time)/3600 = 12.38 h
[TRACE-DF] Σ df_events(icu_training_load) = 546
[TRACE-CONTEXT] totalHours (context) = 12.38
[TRACE-CONTEXT] totalTss (context) = 546
[TRACE-CONTEXT] eventTotals(hours,tss) = 12.38, 546
[ZONE-PATCH] missing zone_dist, using empty dict
[Renderer shim] Delegating to render_report() in render_unified_report.py

[DEBUG-TEMPLATE: PRE-CALL]
Keys in context: ['merge_events', 'render_summary', 'include_coaching_metrics', 'postRenderAudit', 'debug_trace', 'totalDistance', 'auditPartial', 'auditFinal', 'purge_enforced', 'timezone', 'athleteProfile', 'athlete', 'report_mode', 'window_start', 'window_end', 'window_summary', 'knowledge', 'tier1_eventTotals', 'df_events', 'dailyMerged', 'ctl', 'atl', 'tsb', 'load_metrics', 'zone_dist_power', 'zone_dist_hr', 'zone_dist_pace', 'outliers', 'totalHours', 'totalTss', 'eventTotals', 'df_event_only', 'enforcement_layer', '_locked_totals', 'locked_totalHours', 'locked_totalTss', 'locked_totalDistance', 'event_count', 'trace', 'derived_metrics', 'trend_series', 'metrics', 'ACWR', 'Monotony', 'Strain', 'FatigueTrend', 'ZQI', 'FatOxEfficiency', 'Polarisation', 'FOxI', 'CUR', 'GR', 'MES', 'RecoveryIndex', 'ACWR_Risk', 'StressTolerance', 'phases', 'ui_flag', 'actions', '_locked_load_metrics', 'adaptation_metrics', 'trend_metrics', 'correlation_metrics', 'render_mode', 'Duration_total', 'icon_pack', 'force_icon_pack', 'event_log_text', 'report_header', 'summary_patch', 'zone_dist']
load_metrics pre-pass: {'CTL': {'value': 91.14, 'status': 'ok'}, 'ATL': {'value': 90.78, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(1.78), 'status': 'ok'}, 'Strain': {'value': np.float64(971.9), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.644), 'status': 'ok'}, 'totalHours': np.float64(12.38), 'totalTss': 546}
_locked_load_metrics pre-pass: {'totalHours': np.float64(12.38), 'totalTss': 546, 'source': 'tier2_final_lock'}
Report type: weekly
------------------------------------------------------------
[SYNC] Legacy totals restored from eventTotals
[TRACE-RENDER-ENTRY] totalHours = 12.38
[TRACE-RENDER-ENTRY] totalTss   = 546
[DEBUG-RENDER] incoming load_metrics: {
  "CTL": {
    "value": 91.14,
    "status": "ok"
  },
  "ATL": {
    "value": 90.78,
    "status": "ok"
  },
  "TSB": {
    "value": 0.36,
    "status": "ok"
  },
  "ACWR": {
    "value": NaN,
    "status": "ok"
  },
  "Monotony": {
    "value": 1.78,
    "status": "ok"
  },
  "Strain": {
    "value": 971.9,
    "status": "ok"
  },
  "Polarisation": {
    "value": 0.0,
    "status": "ok"
  },
  "RecoveryIndex": {
    "value": 0.644,
    "status": "ok"
  },
  "totalHours": 12.38,
  "totalTss": 546
}
[TRACE-HEADER] ctx.totalHours = 12.38
[TRACE-HEADER] ctx.totalTss   = 546
[Tier-2] Using enforced df_event_only preview (no rebuild).
[Tier-2] Rendered Weekly Events Summary (8 rows)
[Tier-2] Totals appended under event log
[Tier-2] Using canonical summary_patch from Tier-2 validator
[TRACE-DESERIALIZE] wrapped.context totals=12.38, 546

[DEBUG-TEMPLATE: POST-CALL]
Renderer function executed: render_report
Result type: Report
Result keys: ['header', 'markdown', 'type', 'context', 'sections', 'tables', 'lines', 'summary', 'metrics', 'actions', 'phases', 'trends', 'correlation', 'footer']
load_metrics still in context: True
load_metrics post-render: {'CTL': {'value': 91.14, 'status': 'ok'}, 'ATL': {'value': 90.78, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': 1.78, 'status': 'ok'}, 'Strain': {'value': 971.9, 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': 0.644, 'status': 'ok'}, 'totalHours': 12.38, 'totalTss': 546}
------------------------------------------------------------
[DEBUG-TEMPLATE] Renderer returned dict — updating report.

[DEBUG-TEMPLATE: FINAL]
Final report keys: ['header', 'markdown', 'type', 'context', 'sections', 'tables', 'lines', 'summary', 'metrics', 'actions', 'phases', 'trends', 'correlation', 'footer']
Final context load_metrics: {'CTL': {'value': 91.14, 'status': 'ok'}, 'ATL': {'value': 90.78, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': 1.78, 'status': 'ok'}, 'Strain': {'value': 971.9, 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': 0.644, 'status': 'ok'}, 'totalHours': 12.38, 'totalTss': 546}
================================================================================
[TRACE-POST-RENDER-CHECK] header={'title': 'Weekly Training Report', 'framework': 'Unified_Reporting_Framework_v5.1', 'athlete': '90 avec Jacques', 'period': '2025-11-05 → 2025-11-11', 'timestamp': '2025-11-11T15:06:04.634868', 'discipline': 'cycling'}
[TRACE-POST-RENDER-CHECK] summary={'totalHours': np.float64(12.38), 'totalTss': 546, 'eventCount': 8, 'period': '2025-11-05 → 2025-11-11'}
[POST-RENDER] Canonical event-only totals enforced → header + summary synced
[PATCH] header rebuilt for schema compliance: {'title': 'Weekly Training Report', 'framework': 'Unified_Reporting_Framework_v5.1', 'athlete': '90 avec Jacques', 'period': '2025-11-05 → 2025-11-11', 'timestamp': '2025-11-11T15:06:04.634868', 'discipline': 'cycling', 'Total Hours': '12.38 h', 'Total Load (TSS)': 546}
[PATCH] summary rebuilt for schema compliance: {'totalHours': np.float64(12.38), 'totalTss': 546, 'eventCount': 8, 'period': '2025-11-05 → 2025-11-11', 'variance': 0.0, 'zones': {}}
[PATCH] Tier-2 summary override applied → canonical event-only totals enforced
[PATCH] actions dual-structure applied → 2 items
✅ Loaded ICON_CARDS from UIcomponents.icon_pack
✅ Report validated — framework compliant.

[DEBUG-GUARD] --- Report schema diagnostic ---
[DEBUG-GUARD] Report top-level keys: ['header', 'markdown', 'type', 'context', 'sections', 'tables', 'lines', 'summary', 'metrics', 'actions', 'phases', 'trends', 'correlation', 'footer', 'actions_block']
[DEBUG-GUARD] ✅ Schema validation passed for all sections


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
  - debug_trace
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
  - include_coaching_metrics
  - knowledge
  - load_metrics
  - locked_totalDistance
  - locked_totalHours
  - locked_totalTss
  - merge_events
  - metrics
  - outliers
  - phases
  - postRenderAudit
  - purge_enforced
  - render_mode
  - render_summary
  - report_header
  - report_mode
  - summary_patch
  - tier1_eventTotals
  - timezone
  - totalDistance
  - totalHours
  - totalTss
  - totals_source
  - totals_verified
  - trace
  - trend_metrics
  - trend_series
  - tsb
  - ui_flag
  - window_end
  - window_start
  - window_summary
  - zone_dist
  - zone_dist_hr
  - zone_dist_pace
  - zone_dist_power
[DEBUG] End of context key list

✅ Report passed framework + schema validation (event-only, markdown).
[TRACE-FINAL] totalHours = 12.38
[TRACE-FINAL] totalTss   = 546
[TRACE-FINAL] eventTotals(hours,tss) = 12.38 546
[TRACE-FINAL] summary_patch = {'totalHours': np.float64(12.38), 'totalTss': 546, 'eventCount': 8, 'period': '2025-11-05 → 2025-11-11', 'variance': 0.0, 'zones': {}}

```

## Rendered Markdown Report

# 🧭 weekly Training Report — URF v5.1
**Athlete:** Clive King
**Period:** 2025-11-05 → 2025-11-11
**Timezone:** Europe/Zurich
**Generated:** 2025-11-11T15:06:04.634730

---


## 🧩 Tier-0 Dataset Integrity

- Activities fetched: 8
- Origin: tier2_enforce_event_only_totals
- Purge enforced: True
- Wellness records: n/a
- Source verification: ✅ Live (no mock/cache)


## 🧩 Tier-1 Audit Controller

- Deduplication: OK
- HR stream coverage: —
- Power data coverage: —
- Time variance ≤ 0.1 h ✅


## 🧮 Derived Metric Audit

| Metric | Value | Status |
|:-- |:-- |:--|
| ACWR | nan | ✅ |
| Monotony | 1.78 | ✅ |
| Strain | 971.9 | ✅ |
| FatigueTrend | 0.26 | ✅ |
| ZQI | nan | ✅ |
| FatOxEfficiency | 0.0 | ✅ |
| Polarisation | 0.0 | ✅ |
| FOxI | 0.0 | ✅ |
| CUR | 250.0 | ✅ |
| GR | 0.0 | ✅ |
| MES | 0.0 | ✅ |
| RecoveryIndex | 0.644 | ✅ |
| ACWR_Risk | ✅ | ✅ |
| StressTolerance | 5.46 | ✅ |
_No power zone data available._
_No HR zone data available._
_No pace zone data available._


## ⚠️ Outlier Events

_No outliers detected._


## 💓 Wellness & Recovery

- Rest Days: —
- Resting HR: — bpm
- HRV Trend: —
- ATL: 90.78 · CTL: 91.14 · TSB: 0.36


## ⚖️ Load & Stress Chain

| Metric | Value | Status |
|:-- |:-- |:--|
| CTL | 91.14 | ok |
| ATL | 90.78 | ok |
| TSB | 0.36 | ok |
| ACWR | nan | ok |
| Monotony | 1.78 | ok |
| Strain | 971.9 | ok |
| Polarisation | 0.0 | ok |
| RecoveryIndex | 0.644 | ok |
| totalHours | 12.38 | ✅ |
| totalTss | 546 | ✅ |


## 🔬 Efficiency & Adaptation

| Metric | Value | Status |
|:-- |:-- |:--|
| Efficiency Factor | 1.9 | ✅ |
| Fatigue Resistance | 0.95 | ✅ |
| Endurance Decay | 0.02 | ✅ |
| Z2 Stability | 0.04 | ✅ |
| Aerobic Decay | 0.02 | ✅ |


## 🧠 Performance & Coaching Actions


**Recommended Actions:**
1. ⚠ Increase Z1–Z2 share to ≥70 % (Seiler 80/20).
2. ⚠ Improve Zone 2 efficiency: extend duration or adjust IF.


## 🚴 Weekly Events Summary

| date | name | icu_training_load | moving_time | distance |
|:-- |:-- |:-- |:-- |:--|
| 2025-11-11 | Otto Walk | 20 | 01:31:04 | 7.0 |
| 2025-11-09 | Rathvel | 129 | 02:07:33 | 54.9 |
| 2025-11-09 | Otto walk | 17 | 01:07:49 | 6.1 |
| 2025-11-08 | 2hrs in the sunshine | 110 | 02:22:48 | 59.3 |
| 2025-11-08 | Otto walk | 12 | 01:10:39 | 6.6 |
| 2025-11-07 | Zwift - Race: Zwift Epic Race - Fuhgeddaboudit B=A | 161 | 02:00:38 | 82.3 |
| 2025-11-07 | Zwift - Tempus Fugit in Watopia | 17 | 00:26:22 | 15.9 |
| 2025-11-06 | 90 avec Jacques | 80 | 01:36:07 | 65.3 |

**Totals for reporting period:** 12.38 h · 546 TSS · 297.3 km**

---
✅ **Audit Completed:** 2025-11-11T15:06:04.634855
**Framework:** URF v5.1 · Core: v16.14 · Enforcement: tier2_enforce_event_only_totals

