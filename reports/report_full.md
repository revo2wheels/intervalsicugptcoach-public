# 🧾 Full Weekly Audit Report

## Execution Logs

```
🧭 Running Weekly Report (auditFinal=True, render_mode=full)
🧩 Tier-0 reset: cleared totalHours/TSS/distance before aggregation
🧹 Tier-0 purge enforced — previous cache cleared.
[T0] Fetching athlete profile via OAuth2: https://intervals.icu/api/v1/athlete/0/profile
[T0] Athlete profile fetched successfully — id=1914741 name=Clive King
[Tier-0 fetch] chunk_start=2025-11-06  chunk_end=2025-11-12
🧩 Tier-0 deduplication: 0 duplicates removed.
[T0] Canonical slice → 10/10 rows retained (2025-11-06–2025-11-12, tz=Europe/Zurich)
[DEBUG-T0] Expanded icu_zone_times → 8 numeric columns
[DEBUG-T0] Expanded icu_hr_zone_times → 7 numeric columns
[T0] Diagnostic: true Σ(event.moving_time)=50173 s → 13.94 h
[T0] Canonical totals → Σ(TSS)=640.0
[T0-ACWR] Fetching historical load window 2025-10-16 → 2025-11-05
[T0-ACWR] Appended 30 historical activities (28-day total window).
[T0-WELLNESS] Final wellness shape=(7, 43), columns=['date', 'ctl', 'atl', 'rampRate', 'ctlLoad', 'atlLoad', 'sportInfo', 'updated', 'weight', 'restingHR', 'hrv', 'hrvSDNN', 'menstrualPhase', 'menstrualPhasePredicted', 'kcalConsumed', 'sleepSecs', 'sleepScore', 'sleepQuality', 'avgSleepingHR', 'soreness', 'fatigue', 'stress', 'mood', 'motivation', 'injury', 'spO2', 'systolic', 'diastolic', 'hydration', 'hydrationVolume', 'readiness', 'baevskySI', 'bloodGlucose', 'lactate', 'bodyFat', 'abdomen', 'vo2max', 'comments', 'steps', 'respiration', 'locked', 'tempWeight', 'tempRestingHR']
[DEBUG] wellness raw: <class 'pandas.core.frame.DataFrame'> 7
[DEBUG] wellness columns: ['date', 'ctl', 'atl', 'rampRate', 'ctlLoad', 'atlLoad', 'sportInfo', 'updated', 'weight', 'restingHR', 'hrv', 'hrvSDNN', 'menstrualPhase', 'menstrualPhasePredicted', 'kcalConsumed', 'sleepSecs', 'sleepScore', 'sleepQuality', 'avgSleepingHR', 'soreness', 'fatigue', 'stress', 'mood', 'motivation', 'injury', 'spO2', 'systolic', 'diastolic', 'hydration', 'hydrationVolume', 'readiness', 'baevskySI', 'bloodGlucose', 'lactate', 'bodyFat', 'abdomen', 'vo2max', 'comments', 'steps', 'respiration', 'locked', 'tempWeight', 'tempRestingHR']
[DEBUG] wellness head:
          date       ctl         atl  ...  locked  tempWeight  tempRestingHR
0  2025-11-06  88.85163   76.529590  ...    None        True          False
1  2025-11-07  90.94914   90.037544  ...    None        True          False
2  2025-11-08  91.67972   94.292450  ...    None       False          False
3  2025-11-09  92.95778  101.175865  ...    None        True          False
4  2025-11-10  90.77064   87.707120  ...    None       False          False

[5 rows x 43 columns]
[T0] Pre-audit complete: activities=40, wellness_rows=7
⚙️ Normalization: detected seconds, no conversion (max=15204)
[T1] Columns at entry: ['id', 'start_date_local', 'icu_training_load', 'name', 'moving_time', 'origin', 'elapsed_time', 'start_date', 'distance', 'icu_zone_times', 'icu_hr_zone_times', 'date', 'power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8', 'hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7']
🧮 Tier-1: using enforced seconds→hours conversion (Σmoving_time=184546 s → 51.26 h)
[T1] Wellness alignment window (tz-aware): 2025-10-16 15:25:13+02:00 → 2025-11-11 17:52:01+01:00
[T1] Wellness date range: 2025-11-06 → 2025-11-12
✅ Wellness alignment check passed.
[T1] Wellness summary → rest_days=1, rest_hr=43.1, hrv_trend=-0.005
[DEBUG-T1] merging load metrics from wellness: ['ctl', 'atl']
[DEBUG-T1] derived TSB column added from CTL-ATL.
[DEBUG-T1] promoted CTL=91.4 ATL=92.12 TSB=-0.72 to context.
[DEBUG-T1] injected load_metrics for renderer: {'CTL': {'value': 91.4, 'status': 'ok'}, 'ATL': {'value': 92.12, 'status': 'ok'}, 'TSB': {'value': -0.72, 'status': 'ok'}}
[DEBUG-T1] sample merged CTL/ATL/TSB:         date  ctl  atl
0 2025-11-04  NaN  NaN
1 2025-11-04  NaN  NaN
2 2025-11-03  NaN  NaN
3 2025-11-03  NaN  NaN
4 2025-11-03  NaN  NaN
[DEBUG-T1] sanity check before Step 6b — rows in df_activities: 40
[DEBUG-T1] athleteProfile present: True
[DEBUG-T1] athleteProfile keys: ['athlete_id', 'name', 'discipline', 'ftp', 'weight', 'hr_rest', 'hr_max', 'ftp_wkg', 'hr_reserve', 'zone_model', 'training_age_years', 'preferred_units', 'environment', 'timezone', 'updated']
[DEBUG-T1] Starting zone distribution extraction...
[DEBUG-T1] Activity columns sample: ['id', 'start_date_local', 'icu_training_load', 'name', 'moving_time', 'origin', 'elapsed_time', 'start_date', 'distance', 'icu_zone_times', 'icu_hr_zone_times', 'date', 'power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8', 'hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7', 'ctl', 'atl', 'tsb']
[DEBUG-ZONE] Available columns: ['id', 'start_date_local', 'icu_training_load', 'name', 'moving_time', 'origin', 'elapsed_time', 'start_date', 'distance', 'icu_zone_times', 'icu_hr_zone_times', 'date', 'power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8', 'hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7', 'ctl', 'atl', 'tsb']
[DEBUG-ZONE] Detected Power zone columns: ['icu_zone_times', 'power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8']
[DEBUG-ZONE] Detected HR zone columns: ['icu_hr_zone_times', 'hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7']
[DEBUG-ZONE] Detected Pace zone columns: []
[DEBUG-ZONES] power zones computed: {'power_z1': 26.6, 'power_z2': 28.4, 'power_z3': 18.3, 'power_z4': 7.9, 'power_z5': 2.6, 'power_z6': 2.7, 'power_z7': 0.6, 'power_z8': 12.9}
[DEBUG-ZONES] hr zones computed: {'hr_z1': 65.6, 'hr_z2': 18.7, 'hr_z3': 5.5, 'hr_z4': 5.3, 'hr_z5': 2.0, 'hr_z6': 1.5, 'hr_z7': 1.4}
[DEBUG-ZONES] No pace columns found — skipping.
[DEBUG-T1] Completed zone distribution extraction.
[DEBUG-T1] Zone distributions now in context:
  zone_dist_power: {'power_z1': 26.6, 'power_z2': 28.4, 'power_z3': 18.3, 'power_z4': 7.9, 'power_z5': 2.6, 'power_z6': 2.7, 'power_z7': 0.6, 'power_z8': 12.9}
  zone_dist_hr: {'hr_z1': 65.6, 'hr_z2': 18.7, 'hr_z3': 5.5, 'hr_z4': 5.3, 'hr_z5': 2.0, 'hr_z6': 1.5, 'hr_z7': 1.4}
  zone_dist_pace: {}
[DEBUG-OUTLIER] Starting detection on 40 rows
[DEBUG-T1] Outlier events detected: 4
[DEBUG-OUTLIER] mean TSS=63.7, std=54.9, threshold=82.4
[DEBUG-OUTLIER] min/max TSS: 1 / 208
None [T2] Daily completeness summary built — 23 rows
📁 Tier-2 module loaded from: C:\Users\user\onedrive\documents\git\revo2wheels\intervalsicugptcoach\audit_core\tier2_enforce_event_only_totals.py
🔍 Tier-2 enforcement source: Tier-2 validated events (40 rows)
origin counts:
 origin
event    40
Name: count, dtype: int64
moving_time stats:
 count       40.000000
mean      4613.650000
std       3416.304598
min        251.000000
25%       1957.750000
50%       3973.500000
75%       5740.000000
max      15204.000000
Name: moving_time, dtype: float64
🧮 Tier-2: Σ(moving_time)=184546s → 51.26h (Intervals seconds source)
[DEBUG-T2] injected df_event_only preview: 10 rows (sorted by start_date_local)
[DEBUG-T2] enforced load_metrics sync in context: {'CTL': {'value': 91.4, 'status': 'ok'}, 'ATL': {'value': 92.12, 'status': 'ok'}, 'TSB': {'value': -0.72, 'status': 'ok'}}
[T1] Wellness alignment window (tz-aware): 2025-10-16 15:25:13+02:00 → 2025-11-11 17:52:01+01:00
[T1] Wellness date range: 2025-11-06 → 2025-11-12
✅ Wellness alignment check passed.
[DEBUG] Derived metrics synced: {'ACWR': 1.08, 'Monotony': 2.25, 'Strain': 5733.0, 'Polarisation': 0.892, 'RecoveryIndex': 0.55}
[DEBUG-T2X] post-extended load_metrics: {'CTL': {'value': 91.4, 'status': 'ok'}, 'ATL': {'value': 92.12, 'status': 'ok'}, 'TSB': {'value': -0.72, 'status': 'ok'}, 'ACWR': {'value': np.float64(1.08), 'status': 'ok'}, 'Monotony': {'value': np.float64(2.25), 'status': 'ok'}, 'Strain': {'value': np.float64(5733.0), 'status': 'ok'}, 'Polarisation': {'value': 0.892, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.55), 'status': 'ok'}}
[T2-ACTIONS] Integrated derived metrics:
{'ACWR': np.float64(1.08), 'Monotony': np.float64(2.25), 'Strain': np.float64(5733.0), 'FatigueTrend': np.float64(-0.422), 'ZQI': nan, 'FatOxEfficiency': 0.0, 'Polarisation': 0.892, 'FOxI': 0.0, 'CUR': 250.0, 'GR': 0.0, 'MES': np.float64(0.0), 'RecoveryIndex': np.float64(0.55), 'ACWR_Risk': '✅', 'StressTolerance': np.float64(25.48)}
[T2-ACTIONS] Integrated extended metrics:
{}
[PATCH-LOCK] Preserved load_metrics before validator: {'CTL': {'value': 91.4, 'status': 'ok'}, 'ATL': {'value': 92.12, 'status': 'ok'}, 'TSB': {'value': -0.72, 'status': 'ok'}, 'ACWR': {'value': np.float64(1.08), 'status': 'ok'}, 'Monotony': {'value': np.float64(2.25), 'status': 'ok'}, 'Strain': {'value': np.float64(5733.0), 'status': 'ok'}, 'Polarisation': {'value': 0.892, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.55), 'status': 'ok'}}
[DEBUG] Derived metrics synced: {'ACWR': 1.08, 'Monotony': 2.25, 'Strain': 5733.0, 'Polarisation': 0.892, 'RecoveryIndex': 0.55}
[DEBUG-T2X] post-extended load_metrics: {'CTL': {'value': 91.4, 'status': 'ok'}, 'ATL': {'value': 92.12, 'status': 'ok'}, 'TSB': {'value': -0.72, 'status': 'ok'}, 'ACWR': {'value': np.float64(1.08), 'status': 'ok'}, 'Monotony': {'value': np.float64(2.25), 'status': 'ok'}, 'Strain': {'value': np.float64(5733.0), 'status': 'ok'}, 'Polarisation': {'value': 0.892, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.55), 'status': 'ok'}}
🧩 Render mode forced to full+metrics for Unified 10-section layout
[TRACE-RUNTIME] entering finalize_and_validate_render()
[TRACE-RUNTIME] context type = <class 'dict'>
[TRACE-RUNTIME] df_events type = <class 'pandas.core.frame.DataFrame'>
[TRACE-RUNTIME] df_events.shape = (40, 27)
[TRACE-RUNTIME] Σ moving_time/3600 = 51.26 h
[TRACE-RUNTIME] Σ icu_training_load = 2548
[DEBUG-FINALIZER-ENTRY] load_metrics: {'CTL': {'value': 91.4, 'status': 'ok'}, 'ATL': {'value': 92.12, 'status': 'ok'}, 'TSB': {'value': -0.72, 'status': 'ok'}, 'ACWR': {'value': np.float64(1.08), 'status': 'ok'}, 'Monotony': {'value': np.float64(2.25), 'status': 'ok'}, 'Strain': {'value': np.float64(5733.0), 'status': 'ok'}, 'Polarisation': {'value': 0.892, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.55), 'status': 'ok'}}
✅ Loaded ICON_CARDS from UIcomponents.icon_pack
🔎 Render pre-flight — totals by source:
   df_events Σmoving_time = 51.26277777777778
   df_events Σicu_training_load = 2548
   eventTotals(hours) = 51.26

[Tier-2 context diagnostic]
derived_metrics: True
load_metrics: True
adaptation_metrics: True
trend_metrics: True
correlation_metrics: True
[DEBUG] report_header injected: {'athlete': 'Clive King', 'discipline': 'cycling', 'report_type': 'weekly', 'framework': 'Unified_Reporting_Framework_v5.1', 'timezone': 'Europe/Zurich', 'date_range': '2025-11-06 → 2025-11-12'}
[DEBUG-FINALIZER] pre-render load_metrics: {'CTL': {'value': 91.4, 'status': 'ok'}, 'ATL': {'value': 92.12, 'status': 'ok'}, 'TSB': {'value': -0.72, 'status': 'ok'}, 'ACWR': {'value': np.float64(1.08), 'status': 'ok'}, 'Monotony': {'value': np.float64(2.25), 'status': 'ok'}, 'Strain': {'value': np.float64(5733.0), 'status': 'ok'}, 'Polarisation': {'value': 0.892, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.55), 'status': 'ok'}}
[STATE-GUARD] _locked_load_metrics set (prevents recomputation)
[CANONICAL PROPAGATION] hours=51.26, tss=2548
[LOCK] Tier-2 canonical totals re-locked before render
[TRACE-DF] Σ df_events(moving_time)/3600 = 51.26 h
[TRACE-DF] Σ df_events(icu_training_load) = 2548
[TRACE-CONTEXT] totalHours (context) = 51.26
[TRACE-CONTEXT] totalTss (context) = 2548
[TRACE-CONTEXT] eventTotals(hours,tss) = 51.26, 2548
[ZONE-PATCH] missing zone_dist, using empty dict
[Renderer shim] Delegating to render_report() in render_unified_report.py

[DEBUG-TEMPLATE: PRE-CALL]
Keys in context: ['merge_events', 'render_summary', 'include_coaching_metrics', 'postRenderAudit', 'debug_trace', 'totalDistance', 'auditPartial', 'auditFinal', 'purge_enforced', 'timezone', 'athleteProfile', 'athlete', 'report_mode', 'window_start', 'window_end', 'window_summary', 'knowledge', 'tier1_eventTotals', 'df_events', 'wellness_metrics', 'dailyMerged', 'ctl', 'atl', 'tsb', 'load_metrics', 'zone_dist_power', 'zone_dist_hr', 'zone_dist_pace', 'outliers', 'totalHours', 'totalTss', 'eventTotals', 'df_event_only', 'enforcement_layer', '_locked_totals', 'locked_totalHours', 'locked_totalTss', 'locked_totalDistance', 'event_count', 'trace', 'derived_metrics', 'trend_series', 'metrics', 'ACWR', 'Monotony', 'Strain', 'FatigueTrend', 'ZQI', 'FatOxEfficiency', 'Polarisation', 'FOxI', 'CUR', 'GR', 'MES', 'RecoveryIndex', 'ACWR_Risk', 'StressTolerance', 'phases', 'ui_flag', 'actions', '_locked_load_metrics', 'adaptation_metrics', 'trend_metrics', 'correlation_metrics', 'render_mode', 'Duration_total', 'icon_pack', 'force_icon_pack', 'event_log_text', 'report_header', 'summary_patch', 'zone_dist']
load_metrics pre-pass: {'CTL': {'value': 91.4, 'status': 'ok'}, 'ATL': {'value': 92.12, 'status': 'ok'}, 'TSB': {'value': -0.72, 'status': 'ok'}, 'ACWR': {'value': np.float64(1.08), 'status': 'ok'}, 'Monotony': {'value': np.float64(2.25), 'status': 'ok'}, 'Strain': {'value': np.float64(5733.0), 'status': 'ok'}, 'Polarisation': {'value': 0.892, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.55), 'status': 'ok'}, 'totalHours': np.float64(51.26), 'totalTss': 2548}
_locked_load_metrics pre-pass: {'totalHours': np.float64(51.26), 'totalTss': 2548, 'source': 'tier2_final_lock'}
Report type: weekly
------------------------------------------------------------
[SYNC] Legacy totals restored from eventTotals
[TRACE-RENDER-ENTRY] totalHours = 51.26
[TRACE-RENDER-ENTRY] totalTss   = 2548
[DEBUG-RENDER] incoming load_metrics: {
  "CTL": {
    "value": 91.4,
    "status": "ok"
  },
  "ATL": {
    "value": 92.12,
    "status": "ok"
  },
  "TSB": {
    "value": -0.72,
    "status": "ok"
  },
  "ACWR": {
    "value": 1.08,
    "status": "ok"
  },
  "Monotony": {
    "value": 2.25,
    "status": "ok"
  },
  "Strain": {
    "value": 5733.0,
    "status": "ok"
  },
  "Polarisation": {
    "value": 0.892,
    "status": "ok"
  },
  "RecoveryIndex": {
    "value": 0.55,
    "status": "ok"
  },
  "totalHours": 51.26,
  "totalTss": 2548
}
[TRACE-HEADER] ctx.totalHours = 51.26
[TRACE-HEADER] ctx.totalTss   = 2548
[Tier-2] Using enforced df_event_only preview (no rebuild).
[Tier-2] Rendered Weekly Events Summary (10 rows)
[Tier-2] Totals appended under event log
[Tier-2] Using canonical summary_patch from Tier-2 validator
[TRACE-DESERIALIZE] wrapped.context totals=51.26, 2548

[DEBUG-TEMPLATE: POST-CALL]
Renderer function executed: render_report
Result type: Report
Result keys: ['header', 'markdown', 'type', 'context', 'sections', 'tables', 'lines', 'summary', 'metrics', 'actions', 'phases', 'trends', 'correlation', 'footer']
load_metrics still in context: True
load_metrics post-render: {'CTL': {'value': 91.4, 'status': 'ok'}, 'ATL': {'value': 92.12, 'status': 'ok'}, 'TSB': {'value': -0.72, 'status': 'ok'}, 'ACWR': {'value': 1.08, 'status': 'ok'}, 'Monotony': {'value': 2.25, 'status': 'ok'}, 'Strain': {'value': 5733.0, 'status': 'ok'}, 'Polarisation': {'value': 0.892, 'status': 'ok'}, 'RecoveryIndex': {'value': 0.55, 'status': 'ok'}, 'totalHours': 51.26, 'totalTss': 2548}
------------------------------------------------------------
[DEBUG-TEMPLATE] Renderer returned dict — updating report.

[DEBUG-TEMPLATE: FINAL]
Final report keys: ['header', 'markdown', 'type', 'context', 'sections', 'tables', 'lines', 'summary', 'metrics', 'actions', 'phases', 'trends', 'correlation', 'footer']
Final context load_metrics: {'CTL': {'value': 91.4, 'status': 'ok'}, 'ATL': {'value': 92.12, 'status': 'ok'}, 'TSB': {'value': -0.72, 'status': 'ok'}, 'ACWR': {'value': 1.08, 'status': 'ok'}, 'Monotony': {'value': 2.25, 'status': 'ok'}, 'Strain': {'value': 5733.0, 'status': 'ok'}, 'Polarisation': {'value': 0.892, 'status': 'ok'}, 'RecoveryIndex': {'value': 0.55, 'status': 'ok'}, 'totalHours': 51.26, 'totalTss': 2548}
================================================================================
[TRACE-POST-RENDER-CHECK] header={'title': 'Weekly Training Report', 'framework': 'Unified_Reporting_Framework_v5.1', 'athlete': '90 avec Jacques', 'period': '2025-11-06 → 2025-11-12', 'timestamp': '2025-11-12T07:56:01.644916', 'discipline': 'cycling'}
[TRACE-POST-RENDER-CHECK] summary={'totalHours': np.float64(51.26), 'totalTss': 2548, 'eventCount': 40, 'period': '2025-11-06 → 2025-11-12'}
[POST-RENDER] Canonical event-only totals enforced → header + summary synced
[PATCH] header rebuilt for schema compliance: {'title': 'Weekly Training Report', 'framework': 'Unified_Reporting_Framework_v5.1', 'athlete': '90 avec Jacques', 'period': '2025-11-06 → 2025-11-12', 'timestamp': '2025-11-12T07:56:01.644916', 'discipline': 'cycling', 'Total Hours': '51.26 h', 'Total Load (TSS)': 2548}
[PATCH] summary rebuilt for schema compliance: {'totalHours': np.float64(51.26), 'totalTss': 2548, 'eventCount': 40, 'period': '2025-11-06 → 2025-11-12', 'variance': 0.0, 'zones': {}}
[PATCH] Tier-2 summary override applied → canonical event-only totals enforced
[PATCH] actions dual-structure applied → 9 items
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
  - wellness_metrics
  - window_end
  - window_start
  - window_summary
  - zone_dist
  - zone_dist_hr
  - zone_dist_pace
  - zone_dist_power
[DEBUG] End of context key list

✅ Report passed framework + schema validation (event-only, markdown).
[TRACE-FINAL] totalHours = 51.26
[TRACE-FINAL] totalTss   = 2548
[TRACE-FINAL] eventTotals(hours,tss) = 51.26 2548
[TRACE-FINAL] summary_patch = {'totalHours': np.float64(51.26), 'totalTss': 2548, 'eventCount': 40, 'period': '2025-11-06 → 2025-11-12', 'variance': 0.0, 'zones': {}}

```

## Rendered Markdown Report

# 🧭 weekly Training Report — URF v5.1
**Athlete:** Clive King
**Period:** 2025-11-06 → 2025-11-12
**Timezone:** Europe/Zurich
**Generated:** 2025-11-12T07:56:01.644169

---


## 🧩 Tier-0 Dataset Integrity

- Activities fetched: 40
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
| ACWR | 1.08 | ✅ |
| Monotony | 2.25 | ✅ |
| Strain | 5733.0 | ✅ |
| FatigueTrend | -0.422 | ✅ |
| ZQI | nan | ✅ |
| FatOxEfficiency | 0.0 | ✅ |
| Polarisation | 0.892 | ✅ |
| FOxI | 0.0 | ✅ |
| CUR | 250.0 | ✅ |
| GR | 0.0 | ✅ |
| MES | 0.0 | ✅ |
| RecoveryIndex | 0.55 | ✅ |
| ACWR_Risk | ✅ | ✅ |
| StressTolerance | 25.48 | ✅ |


### Power Zones
| Zone | % Time |
|:-- |:--|
| power_z1 | 26.6 |
| power_z2 | 28.4 |
| power_z3 | 18.3 |
| power_z4 | 7.9 |
| power_z5 | 2.6 |
| power_z6 | 2.7 |
| power_z7 | 0.6 |
| power_z8 | 12.9 |


### Heart Rate Zones
| Zone | % Time |
|:-- |:--|
| hr_z1 | 65.6 |
| hr_z2 | 18.7 |
| hr_z3 | 5.5 |
| hr_z4 | 5.3 |
| hr_z5 | 2.0 |
| hr_z6 | 1.5 |
| hr_z7 | 1.4 |


_No pace zone data available._


## ⚠️ Outlier Events

| Date | Event | Issue | Observation |
|:-- |:-- |:-- |:--|
| 2025-11-01 | 3 hours endurance | TSS outlier | TSS=155 |
| 2025-10-19 | Paccots MTB | TSS outlier | TSS=190 |
| 2025-10-16 | Jorat mtb / hardtail | TSS outlier | TSS=208 |
| 2025-11-07 | Zwift - Race: Zwift Epic Race - Fuhgeddaboudit B=A | TSS outlier | TSS=161 |


## 💓 Wellness & Recovery

- Rest Days: 1
- Resting HR: 43.1 bpm
- HRV: 54.0 ms (↓ declining (-3.0 ms), prev 57.0 ms)
- Avg Sleep: 7.9 h/night
- Fatigue: 2.0/5
- Stress: 2.0/5
- Readiness: nan/5
- ATL: 92.12 · CTL: 91.4 · TSB: -0.72


## ⚖️ Load & Stress Chain

| Metric | Value | Status |
|:-- |:-- |:--|
| CTL | 91.4 | ok |
| ATL | 92.12 | ok |
| TSB | -0.72 | ok |
| ACWR | 1.08 | ok |
| Monotony | 2.25 | ok |
| Strain | 5733.0 | ok |
| Polarisation | 0.892 | ok |
| RecoveryIndex | 0.55 | ok |
| totalHours | 51.26 | ✅ |
| totalTss | 2548 | ✅ |


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
1. ✅ Maintain ≥70 % Z1–Z2 volume (Seiler 80/20).
2. ⚠ Improve Zone 2 efficiency: extend duration or adjust IF.
3. ⚠ Apply 10–15 % deload (Friel microcycle logic).
4. ✅ Durability improving (1.00) — maintain current long-ride structure.
5. ⚠ Load intensity low (LIR=0.00) — consider adding tempo or sweet-spot intervals.
6. ✅ Endurance reserve strong (1.00).
7. ✅ Efficiency drift stable (0.00%).
8. ✅ Polarisation optimal (89%).
9. ⚠ Recovery Index poor (0.55) — insert deload or reduce intensity.


## 🚴 Weekly Events Summary

| date | name | icu_training_load | moving_time | distance |
|:-- |:-- |:-- |:-- |:--|
| 2025-11-11 | Otto Walk | 20 | 01:31:04 | 7.0 |
| 2025-11-11 | Zwift - Tick Tock in Watopia | 6 | 00:10:13 | 6.4 |
| 2025-11-11 | zAlp low cadence | 88 | 01:23:00 | 35.9 |
| 2025-11-09 | Otto walk | 17 | 01:07:49 | 6.1 |
| 2025-11-09 | Rathvel | 129 | 02:07:33 | 54.9 |
| 2025-11-08 | Otto walk | 12 | 01:10:39 | 6.6 |
| 2025-11-08 | 2hrs in the sunshine | 110 | 02:22:48 | 59.3 |
| 2025-11-07 | Zwift - Tempus Fugit in Watopia | 17 | 00:26:22 | 15.9 |
| 2025-11-07 | Zwift - Race: Zwift Epic Race - Fuhgeddaboudit B=A | 161 | 02:00:38 | 82.3 |
| 2025-11-06 | 90 avec Jacques | 80 | 01:36:07 | 65.3 |

**Totals for reporting period:** 51.26 h · 2548 TSS · 339.6 km**

---
✅ **Audit Completed:** 2025-11-12T07:56:01.644897
**Framework:** URF v5.1 · Core: v16.14 · Enforcement: tier2_enforce_event_only_totals

