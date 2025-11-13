# 🧾 Full Weekly Audit Report

## Execution Logs

```
🧭 Running Weekly Report (auditFinal=True, render_mode=full)
[T0-LIGHT] Fetching lightweight 28-day dataset via /activities → https://intervals.icu/api/v1/athlete/0/activities?oldest=2025-10-16&newest=2025-11-13
[T0-LIGHT] Trimmed columns for lightweight mode: ['id', 'name', 'type', 'start_date_local', 'distance', 'moving_time', 'icu_training_load', 'IF', 'average_heartrate', 'VO2MaxGarmin']
[T0-SLICE] 7-day window: 2025-11-07 → 2025-11-14 (10 activities selected)
[T0-SLICE] 7-day window: 2025-11-07 → 2025-11-14 (10 activities selected)
[T0-DEDUP] Dropped 0 duplicates → 10 unique events
🧭 Tier-0: 7-day subset (lightweight) = 13.9 h | 334.8 km | 623 TSS (10 events)
[T0] Fetching athlete profile via OAuth2: https://intervals.icu/api/v1/athlete/0/profile
[T0] Athlete profile fetched successfully — id=1914741 name=Clive King
[Tier-0 fetch] chunk_start=2025-11-07  chunk_end=2025-11-13
🧩 Tier-0 deduplication: 0 duplicates removed.
[T0] Canonical slice → 10/10 rows retained (2025-11-07–2025-11-13, tz=Europe/Zurich)
None [T0] Expanded icu_zone_times safely → 8 cols, max depth=8
None [T0] Expanded icu_hr_zone_times safely → 7 cols, max depth=7
[T0] Diagnostic: true Σ(event.moving_time)=50035 s → 13.90 h
[T0] Canonical totals → Σ(TSS)=623.0
[T0-ACWR] Fetching historical load window 2025-10-17 → 2025-11-06
[T0-ACWR] Stored 30 baseline activities (ACWR only).
[T0-WELLNESS] Final wellness shape=(7, 43), columns=['date', 'ctl', 'atl', 'rampRate', 'ctlLoad', 'atlLoad', 'sportInfo', 'updated', 'weight', 'restingHR', 'hrv', 'hrvSDNN', 'menstrualPhase', 'menstrualPhasePredicted', 'kcalConsumed', 'sleepSecs', 'sleepScore', 'sleepQuality', 'avgSleepingHR', 'soreness', 'fatigue', 'stress', 'mood', 'motivation', 'injury', 'spO2', 'systolic', 'diastolic', 'hydration', 'hydrationVolume', 'readiness', 'baevskySI', 'bloodGlucose', 'lactate', 'bodyFat', 'abdomen', 'vo2max', 'comments', 'steps', 'respiration', 'locked', 'tempWeight', 'tempRestingHR']
[DEBUG] wellness raw: <class 'pandas.core.frame.DataFrame'> 7
[DEBUG] wellness columns: ['date', 'ctl', 'atl', 'rampRate', 'ctlLoad', 'atlLoad', 'sportInfo', 'updated', 'weight', 'restingHR', 'hrv', 'hrvSDNN', 'menstrualPhase', 'menstrualPhasePredicted', 'kcalConsumed', 'sleepSecs', 'sleepScore', 'sleepQuality', 'avgSleepingHR', 'soreness', 'fatigue', 'stress', 'mood', 'motivation', 'injury', 'spO2', 'systolic', 'diastolic', 'hydration', 'hydrationVolume', 'readiness', 'baevskySI', 'bloodGlucose', 'lactate', 'bodyFat', 'abdomen', 'vo2max', 'comments', 'steps', 'respiration', 'locked', 'tempWeight', 'tempRestingHR']
[DEBUG] wellness head:
          date        ctl         atl  ...  locked  tempWeight  tempRestingHR
0  2025-11-07  90.949140   90.037544  ...    None        True          False
1  2025-11-08  91.679720   94.292450  ...    None       False          False
2  2025-11-09  92.957780  101.175865  ...    None        True          False
3  2025-11-10  90.770640   87.707120  ...    None       False          False
4  2025-11-11  91.317184   91.207280  ...    None        True          False

[5 rows x 43 columns]
[T0] Diagnostic only: 10 rows fetched, moving_time present=True
[T0] Pre-audit complete: activities=10, wellness_rows=7
⚙️ Normalization: detected seconds, no conversion (max=8568)
[T1] Columns at entry: ['id', 'start_date_local', 'icu_training_load', 'elapsed_time', 'name', 'start_date', 'distance', 'moving_time', 'date', 'origin', 'power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8', 'hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7']
[Tier-1] Visible subset unified: 13.90 h | 334.8 km | 623 TSS | IF=None HR=None VO₂=None
✅ Tier-1 finalization: 10 events | 13.9 h | 623 TSS
🧩 Tier-1 variance check passed (Δh=0.00, ΔTSS=0.0)
[T1] Wellness alignment window (tz-aware): 2025-11-07 17:52:06+01:00 → 2025-11-12 16:55:11+01:00
[T1] Wellness date range: 2025-11-07 → 2025-11-13
✅ Wellness alignment check passed.
[T1] Wellness summary → rest_days=1, rest_hr=42.9, hrv_trend=-0.007
[DEBUG-T1] merging load metrics from wellness: ['ctl', 'atl']
[DEBUG-T1] derived TSB column added from CTL-ATL.
[DEBUG-T1] promoted CTL=91.58 ATL=93.21 TSB=-1.63 to context.
[DEBUG-T1] injected load_metrics for renderer: {'CTL': {'value': 91.58, 'status': 'ok'}, 'ATL': {'value': 93.21, 'status': 'ok'}, 'TSB': {'value': -1.63, 'status': 'ok'}}
[DEBUG-T1] sample merged CTL/ATL/TSB:         date        ctl         atl
0 2025-11-12  90.650930   87.452270
1 2025-11-11  91.317184   91.207280
2 2025-11-11  91.317184   91.207280
3 2025-11-11  91.317184   91.207280
4 2025-11-09  92.957780  101.175865
[DEBUG-T1] sanity check before Step 6b — rows in df_activities: 10
[DEBUG-T1] athleteProfile present: True
[DEBUG-T1] athleteProfile keys: ['athlete_id', 'name', 'discipline', 'ftp', 'weight', 'hr_rest', 'hr_max', 'ftp_wkg', 'hr_reserve', 'zone_model', 'training_age_years', 'preferred_units', 'environment', 'timezone', 'updated']
[DEBUG-T1] Starting zone distribution extraction...
[DEBUG-T1] Activity columns sample: ['id', 'start_date_local', 'icu_training_load', 'elapsed_time', 'name', 'start_date', 'distance', 'moving_time', 'date', 'origin', 'power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8', 'hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7', 'ctl', 'atl', 'tsb']
[DEBUG-ZONE] Available columns: ['id', 'start_date_local', 'icu_training_load', 'elapsed_time', 'name', 'start_date', 'distance', 'moving_time', 'date', 'origin', 'power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8', 'hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7', 'ctl', 'atl', 'tsb']
[DEBUG-ZONE] Detected Power zone columns: ['power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8']
[DEBUG-ZONE] Detected HR zone columns: ['hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7']
[DEBUG-ZONE] Detected Pace zone columns: []
[DEBUG-ZONES] power zones computed: {'power_z1': 27.2, 'power_z2': 30.5, 'power_z3': 15.7, 'power_z4': 7.9, 'power_z5': 2.6, 'power_z6': 2.7, 'power_z7': 0.6, 'power_z8': 12.7}
[DEBUG-ZONES] hr zones computed: {'hr_z1': 71.8, 'hr_z2': 12.5, 'hr_z3': 5.4, 'hr_z4': 5.3, 'hr_z5': 2.0, 'hr_z6': 1.5, 'hr_z7': 1.5}
[DEBUG-ZONES] No pace columns found — skipping.
[DEBUG-T1] Completed zone distribution extraction.
[DEBUG-T1] Zone distributions now in context:
  zone_dist_power: {'power_z1': 27.2, 'power_z2': 30.5, 'power_z3': 15.7, 'power_z4': 7.9, 'power_z5': 2.6, 'power_z6': 2.7, 'power_z7': 0.6, 'power_z8': 12.7}
  zone_dist_hr: {'hr_z1': 71.8, 'hr_z2': 12.5, 'hr_z3': 5.4, 'hr_z4': 5.3, 'hr_z5': 2.0, 'hr_z6': 1.5, 'hr_z7': 1.5}
  zone_dist_pace: {}
[DEBUG-OUTLIER] Starting detection on 10 rows
[DEBUG-T1] Outlier events detected: 1
[DEBUG-OUTLIER] mean TSS=62.3, std=56.5, threshold=84.7
[DEBUG-OUTLIER] min/max TSS: 6 / 161
None [T2] Daily completeness summary built — 5 rows
📁 Tier-2 module loaded from: C:\Users\user\onedrive\documents\git\revo2wheels\intervalsicugptcoach\audit_core\tier2_enforce_event_only_totals.py
🔍 Tier-2 enforcement source: Tier-2 validated events (10 rows)
origin counts:
 origin
event    10
Name: count, dtype: int64
moving_time stats:
 count      10.000000
mean     5003.500000
std      2533.404966
min       613.000000
25%      4111.500000
50%      5222.000000
75%      6835.750000
max      8568.000000
Name: moving_time, dtype: float64
🧮 Tier-2: Σ(moving_time)=50035s → 13.90h (Intervals seconds source)
[DEBUG-T2] injected df_event_only preview: 10 rows (sorted by start_date_local)
[DEBUG-T2] enforced load_metrics sync in context: {'CTL': {'value': 91.58, 'status': 'ok'}, 'ATL': {'value': 93.21, 'status': 'ok'}, 'TSB': {'value': -1.63, 'status': 'ok'}}
[T2] Enriched load_metrics propagated to renderer
[T1] Wellness alignment window (tz-aware): 2025-11-07 17:52:06+01:00 → 2025-11-12 16:55:11+01:00
[T1] Wellness date range: 2025-11-07 → 2025-11-13
✅ Wellness alignment check passed.
[T2-ACWR] EWMA model applied → acute=126.84, chronic=160.93, ratio=0.79
[DEBUG] Derived metrics synced: {'ACWR': 0.0, 'Monotony': 0.0, 'Strain': 0.0, 'Polarisation': 0.0, 'RecoveryIndex': 0.0}
[DEBUG-T2X] post-extended load_metrics: {'CTL': {'value': 91.58, 'status': 'ok'}, 'ATL': {'value': 93.21, 'status': 'ok'}, 'TSB': {'value': -1.63, 'status': 'ok'}, 'ACWR': {'value': 0.79, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.93), 'status': 'ok'}, 'Strain': {'value': np.float64(1825.4), 'status': 'ok'}, 'Polarisation': {'value': 0.729, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.414), 'status': 'ok'}}
[T2-ACTIONS] Integrated derived metrics:
{'ACWR': {'value': 0.79, 'status': 'borderline', 'icon': '🟠'}, 'Monotony': {'value': np.float64(2.93), 'status': 'out of range', 'icon': '🔴'}, 'Strain': {'value': np.float64(1825.4), 'status': 'optimal', 'icon': '🟢'}, 'FatigueTrend': {'value': np.float64(-0.36), 'status': 'borderline', 'icon': '🟠'}, 'ZQI': {'value': 6.8, 'status': 'optimal', 'icon': '🟢'}, 'FatOxEfficiency': {'value': 0.53, 'status': 'optimal', 'icon': '🟢'}, 'Polarisation': {'value': 0.729, 'status': 'borderline', 'icon': '🟠'}, 'FOxI': {'value': 53.0, 'status': 'optimal', 'icon': '🟢'}, 'CUR': {'value': 47.0, 'status': 'optimal', 'icon': '🟢'}, 'GR': {'value': 0.89, 'status': 'optimal', 'icon': '🟢'}, 'MES': {'value': np.float64(33.9), 'status': 'optimal', 'icon': '🟢'}, 'RecoveryIndex': {'value': np.float64(0.414), 'status': 'borderline', 'icon': '🟠'}, 'ACWR_Risk': {'value': '✅', 'status': 'no data', 'icon': '⚪'}, 'StressTolerance': {'value': np.float64(6.23), 'status': 'optimal', 'icon': '🟢'}}
[T2-ACTIONS] Integrated extended metrics:
{}
[PATCH-LOCK] Preserved load_metrics before validator: {'CTL': {'value': 91.58, 'status': 'ok'}, 'ATL': {'value': 93.21, 'status': 'ok'}, 'TSB': {'value': -1.63, 'status': 'ok'}, 'ACWR': {'value': 0.79, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.93), 'status': 'ok'}, 'Strain': {'value': np.float64(1825.4), 'status': 'ok'}, 'Polarisation': {'value': 0.729, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.414), 'status': 'ok'}}
[T2-ACWR] EWMA model applied → acute=126.84, chronic=160.93, ratio=0.79
[DEBUG] Derived metrics synced: {'ACWR': 0.0, 'Monotony': 0.0, 'Strain': 0.0, 'Polarisation': 0.0, 'RecoveryIndex': 0.0}
[DEBUG-T2X] post-extended load_metrics: {'CTL': {'value': 91.58, 'status': 'ok'}, 'ATL': {'value': 93.21, 'status': 'ok'}, 'TSB': {'value': -1.63, 'status': 'ok'}, 'ACWR': {'value': 0.79, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.93), 'status': 'ok'}, 'Strain': {'value': np.float64(1825.4), 'status': 'ok'}, 'Polarisation': {'value': 0.729, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.414), 'status': 'ok'}}
🧩 Render mode forced to full+metrics for Unified 10-section layout
[SYNC] URF renderer context overridden with tier1_visibleTotals
[TRACE-RUNTIME] entering finalize_and_validate_render()
[TRACE-RUNTIME] context type = <class 'dict'>
[TRACE-RUNTIME] df_events type = <class 'pandas.core.frame.DataFrame'>
[TRACE-RUNTIME] df_events.shape = (10, 25)
[TRACE-RUNTIME] Σ moving_time/3600 = 13.90 h
[TRACE-RUNTIME] Σ icu_training_load = 623
[DEBUG-FINALIZER-ENTRY] load_metrics: {'CTL': {'value': 91.58, 'status': 'ok'}, 'ATL': {'value': 93.21, 'status': 'ok'}, 'TSB': {'value': -1.63, 'status': 'ok'}, 'ACWR': {'value': 0.79, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.93), 'status': 'ok'}, 'Strain': {'value': np.float64(1825.4), 'status': 'ok'}, 'Polarisation': {'value': 0.729, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.414), 'status': 'ok'}}
✅ Loaded ICON_CARDS from UIcomponents.icon_pack
🔎 Render pre-flight — totals by source:
   df_events Σmoving_time = 13.89861111111111
   df_events Σicu_training_load = 623
   eventTotals(hours) = 13.9

[Tier-2 context diagnostic]
derived_metrics: True
load_metrics: True
adaptation_metrics: True
trend_metrics: True
correlation_metrics: True
[DEBUG] report_header injected: {'athlete': 'Clive King', 'discipline': 'cycling', 'report_type': 'weekly', 'framework': 'Unified_Reporting_Framework_v5.1', 'timezone': 'Europe/Zurich', 'date_range': '2025-11-07 → 2025-11-13'}
[DEBUG-FINALIZER] pre-render load_metrics: {'CTL': {'value': 91.58, 'status': 'ok'}, 'ATL': {'value': 93.21, 'status': 'ok'}, 'TSB': {'value': -1.63, 'status': 'ok'}, 'ACWR': {'value': 0.79, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.93), 'status': 'ok'}, 'Strain': {'value': np.float64(1825.4), 'status': 'ok'}, 'Polarisation': {'value': 0.729, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.414), 'status': 'ok'}}
[STATE-GUARD] _locked_load_metrics set (prevents recomputation)
[CANONICAL PROPAGATION] hours=13.9, tss=623
[LOCK] Tier-2 canonical totals re-locked before render
[TRACE-DF] Σ df_events(moving_time)/3600 = 13.90 h
[TRACE-DF] Σ df_events(icu_training_load) = 623
[TRACE-CONTEXT] totalHours (context) = 13.9
[TRACE-CONTEXT] totalTss (context) = 623
[TRACE-CONTEXT] eventTotals(hours,tss) = 13.9, 623
[ZONE-PATCH] missing zone_dist, using empty dict
[Renderer shim] Delegating to render_report() in render_unified_report.py

[DEBUG-TEMPLATE: PRE-CALL]
Keys in context: ['debug_mode', 'merge_events', 'render_summary', 'include_coaching_metrics', 'postRenderAudit', 'debug_trace', 'tier0_snapshotTotals_7d', 'snapshot_7d_json', 'timezone', 'athleteProfile', 'athlete', 'report_mode', 'window_start', 'window_end', 'df_acwr_base', 'auditPartial', 'auditFinal', 'window_summary', 'knowledge', 'tier1_visibleTotals', 'weeklyEventLogBlock', 'df_events', 'wellness_metrics', 'dailyMerged', 'ctl', 'atl', 'tsb', 'load_metrics', 'zone_dist_power', 'zone_dist_hr', 'zone_dist_pace', 'outliers', 'totalHours', 'totalTss', 'totalDistance', 'eventTotals', 'df_event_only', 'enforcement_layer', '_locked_totals', 'locked_totalHours', 'locked_totalTss', 'locked_totalDistance', 'event_count', 'trace', 'derived_metrics', 'trend_series', 'metrics', 'ACWR', 'Monotony', 'Strain', 'FatigueTrend', 'ZQI', 'FatOxEfficiency', 'Polarisation', 'FOxI', 'CUR', 'GR', 'MES', 'RecoveryIndex', 'ACWR_Risk', 'StressTolerance', 'phases', 'metric_contexts', 'ui_flag', 'actions', '_locked_load_metrics', 'adaptation_metrics', 'trend_metrics', 'correlation_metrics', 'render_mode', 'totalSessions', 'Duration_total', 'icon_pack', 'force_icon_pack', 'event_log_text', 'report_header', 'summary_patch', 'zone_dist']
load_metrics pre-pass: {'CTL': {'value': 91.58, 'status': 'ok'}, 'ATL': {'value': 93.21, 'status': 'ok'}, 'TSB': {'value': -1.63, 'status': 'ok'}, 'ACWR': {'value': 0.79, 'status': 'ok'}, 'Monotony': {'value': np.float64(2.93), 'status': 'ok'}, 'Strain': {'value': np.float64(1825.4), 'status': 'ok'}, 'Polarisation': {'value': 0.729, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.414), 'status': 'ok'}, 'totalHours': np.float64(13.9), 'totalTss': 623}
_locked_load_metrics pre-pass: {'totalHours': np.float64(13.9), 'totalTss': 623, 'source': 'tier2_final_lock'}
Report type: weekly
------------------------------------------------------------
[VERIFY] Renderer using Tier-1 visibleTotals for totals and metrics.
✅ Renderer source: Tier-1 visibleTotals (lightweight 7-day dataset)
[SYNC] Unified totals from tier1_visibleTotals
[SYNC] Legacy totals restored from eventTotals
[TRACE-RENDER-ENTRY] totalHours = 13.9
[TRACE-RENDER-ENTRY] totalTss   = 623
[DEBUG-RENDER] incoming load_metrics: {
  "CTL": {
    "value": 91.58,
    "status": "ok"
  },
  "ATL": {
    "value": 93.21,
    "status": "ok"
  },
  "TSB": {
    "value": -1.63,
    "status": "ok"
  },
  "ACWR": {
    "value": 0.79,
    "status": "ok"
  },
  "Monotony": {
    "value": 2.93,
    "status": "ok"
  },
  "Strain": {
    "value": 1825.4,
    "status": "ok"
  },
  "Polarisation": {
    "value": 0.729,
    "status": "ok"
  },
  "RecoveryIndex": {
    "value": 0.414,
    "status": "ok"
  },
  "totalHours": 13.9,
  "totalTss": 623
}
[TRACE-HEADER] ctx.totalHours = 13.9
[TRACE-HEADER] ctx.totalTss   = 623
[DEBUG] Adaptation metric keys: ['Efficiency Factor', 'Fatigue Resistance', 'Endurance Decay', 'Z2 Stability', 'Aerobic Decay']
[Tier-2] Using enforced df_event_only preview (no rebuild).
[Tier-2] Rendered Weekly Events Summary (10 rows)
[Tier-2] Weekly totals + mean metrics rendered (Tier-1 subset)
[Tier-2] Using canonical summary_patch from Tier-2 validator
[TRACE-DESERIALIZE] wrapped.context totals=13.9, 623

[DEBUG-TEMPLATE: POST-CALL]
Renderer function executed: render_report
Result type: Report
Result keys: ['header', 'markdown', 'type', 'context', 'sections', 'tables', 'lines', 'summary', 'metrics', 'actions', 'phases', 'trends', 'correlation', 'footer']
load_metrics still in context: True
load_metrics post-render: {'CTL': {'value': 91.58, 'status': 'ok'}, 'ATL': {'value': 93.21, 'status': 'ok'}, 'TSB': {'value': -1.63, 'status': 'ok'}, 'ACWR': {'value': 0.79, 'status': 'ok'}, 'Monotony': {'value': 2.93, 'status': 'ok'}, 'Strain': {'value': 1825.4, 'status': 'ok'}, 'Polarisation': {'value': 0.729, 'status': 'ok'}, 'RecoveryIndex': {'value': 0.414, 'status': 'ok'}, 'totalHours': 13.9, 'totalTss': 623}
------------------------------------------------------------
[DEBUG-TEMPLATE] Renderer returned dict — updating report.

[DEBUG-TEMPLATE: FINAL]
Final report keys: ['header', 'markdown', 'type', 'context', 'sections', 'tables', 'lines', 'summary', 'metrics', 'actions', 'phases', 'trends', 'correlation', 'footer']
Final context load_metrics: {'CTL': {'value': 91.58, 'status': 'ok'}, 'ATL': {'value': 93.21, 'status': 'ok'}, 'TSB': {'value': -1.63, 'status': 'ok'}, 'ACWR': {'value': 0.79, 'status': 'ok'}, 'Monotony': {'value': 2.93, 'status': 'ok'}, 'Strain': {'value': 1825.4, 'status': 'ok'}, 'Polarisation': {'value': 0.729, 'status': 'ok'}, 'RecoveryIndex': {'value': 0.414, 'status': 'ok'}, 'totalHours': 13.9, 'totalTss': 623}
================================================================================
[TRACE-POST-RENDER-CHECK] header={'title': 'Weekly Training Report', 'framework': 'Unified_Reporting_Framework_v5.1', 'athlete': 'Zwift - Tempus Fugit in Watopia', 'period': '2025-11-07 → 2025-11-13', 'timestamp': '2025-11-13T11:45:00.033859', 'discipline': 'cycling'}
[TRACE-POST-RENDER-CHECK] summary={'totalHours': np.float64(13.9), 'totalTss': 623, 'eventCount': 10, 'period': '2025-11-07 → 2025-11-13'}
[POST-RENDER] Canonical event-only totals enforced → header + summary synced
[PATCH] header rebuilt for schema compliance: {'title': 'Weekly Training Report', 'framework': 'Unified_Reporting_Framework_v5.1', 'athlete': 'Zwift - Tempus Fugit in Watopia', 'period': '2025-11-07 → 2025-11-13', 'timestamp': '2025-11-13T11:45:00.033859', 'discipline': 'cycling', 'Total Hours': '13.90 h', 'Total Load (TSS)': 623}
[PATCH] summary rebuilt for schema compliance: {'totalHours': np.float64(13.9), 'totalTss': 623, 'eventCount': 10, 'period': '2025-11-07 → 2025-11-13', 'variance': 0.0, 'zones': {}}
[PATCH] Tier-2 summary override applied → canonical event-only totals enforced
[PATCH] actions dual-structure applied → 24 items
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
  - debug_mode
  - debug_trace
  - derived_metrics
  - df_acwr_base
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
  - metric_contexts
  - metrics
  - outliers
  - phases
  - postRenderAudit
  - render_mode
  - render_summary
  - report_header
  - report_mode
  - snapshot_7d_json
  - summary_patch
  - tier0_snapshotTotals_7d
  - tier1_visibleTotals
  - timezone
  - totalDistance
  - totalHours
  - totalSessions
  - totalTss
  - totals_source
  - totals_verified
  - trace
  - trend_metrics
  - trend_series
  - tsb
  - ui_flag
  - weeklyEventLogBlock
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
[TRACE-FINAL] totalHours = 13.9
[TRACE-FINAL] totalTss   = 623
[TRACE-FINAL] eventTotals(hours,tss) = 13.9 623
[TRACE-FINAL] summary_patch = {'totalHours': np.float64(13.9), 'totalTss': 623, 'eventCount': 10, 'period': '2025-11-07 → 2025-11-13', 'variance': 0.0, 'zones': {}}

```

## Rendered Markdown Report

# 🧭 weekly Training Report — URF v5.1
**Athlete:** Clive King
**Period:** 2025-11-07 → 2025-11-13
**Timezone:** Europe/Zurich
**Generated:** 2025-11-13T11:45:00.033037

---


## 🧩 Tier-0 Dataset Integrity

- Activities fetched: 10
- Origin: tier2_enforce_event_only_totals
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
| ACWR | 0.79 | 🟠 borderline | EWMA Acute:Chronic Load Ratio — compares 7-day vs 28-day weighted loads. 0.8–1.3 = productive training, <0.8 = recovery or detraining, >1.5 = overload/injury risk. |
| Monotony | 2.93 | 🔴 out of range | 1–2 shows healthy variation; >2.5 means repetitive stress pattern. |
| Strain | 1825.4 | 🟢 optimal | Product of load × monotony; >3500 signals potential overreach. |
| FatigueTrend | -0.36 | 🟠 borderline | 0±0.2 indicates balance; positive trend means accumulating fatigue. |
| ZQI | 680.0 | 🟢 optimal | Zone Quality Index (%) 5-15 high-intensity time is normal <3% too easy, >20% too intense or erratic pacing. |
| FatOxEfficiency | 0.53 | 🟢 optimal | 0.4–0.8 means balanced fat oxidation; lower = carb dependence. |
| Polarisation | 0.729 | 🟠 borderline | 0.75–0.9 matches Seiler 80/20 distribution; <0.7 = too intense. |
| FOxI | 53.0 | 🟢 optimal | FatOx index %; higher values mean more efficient aerobic base. |
| CUR | 47.0 | 🟢 optimal | Carbohydrate Utilisation Ratio; 30-80 balanced metabolic use. |
| GR | 0.89 | 🟢 optimal | Glucose Ratio; >2 indicates excess glycolytic bias. |
| MES | 33.9 | 🟢 optimal | Metabolic Efficiency Score; >20 is good endurance economy. |
| RecoveryIndex | 0.414 | 🟠 borderline | 0.6–1.0 means recovered; <0.5 = heavy fatigue. |
| ACWR_Risk | ✅ | ⚪ no data | Used internally for stability check. |
| StressTolerance | 6.23 | 🟢 optimal | 2–8 indicates sustainable training strain capacity. |


### Power Zones
| Zone | % Time |
|:-- |:--|
| power_z1 | 27.2 |
| power_z2 | 30.5 |
| power_z3 | 15.7 |
| power_z4 | 7.9 |
| power_z5 | 2.6 |
| power_z6 | 2.7 |
| power_z7 | 0.6 |
| power_z8 | 12.7 |


### Heart Rate Zones
| Zone | % Time |
|:-- |:--|
| hr_z1 | 71.8 |
| hr_z2 | 12.5 |
| hr_z3 | 5.4 |
| hr_z4 | 5.3 |
| hr_z5 | 2.0 |
| hr_z6 | 1.5 |
| hr_z7 | 1.5 |


_No pace zone data available._


## ⚠️ Outlier Events

| Date | Event | Issue | Observation |
|:-- |:-- |:-- |:--|
| 2025-11-07 | Zwift - Race: Zwift Epic Race - Fuhgeddaboudit B=A | TSS outlier | TSS=161 |


## 💓 Wellness & Recovery

- Rest Days: 1
- Resting HR: 42.9 bpm
- HRV: 53.0 ms (→ stable, prev 54.0 ms)
- Avg Sleep: 7.9 h/night
- Fatigue: 2.0/5
- Stress: 2.0/5
- Readiness: nan/5
- ATL: 93.21 · CTL: 91.58 · TSB: -1.63


## ⚖️ Load & Stress Chain (Diagnostics)

| Metric | Value | Status |
|:-- |:-- |:--|
| CTL | 91.58 | ok |
| ATL | 93.21 | ok |
| TSB | -1.63 | ok |
| ACWR | 0.79 | ok |
| Monotony | 2.93 | ok |
| Strain | 1825.4 | ok |
| Polarisation | 0.729 | ok |
| RecoveryIndex | 0.414 | ok |
| totalHours | 13.9 | ✅ |
| totalTss | 623 | ✅ |


## 🔬 Efficiency & Adaptation

| Metric | Value | Status | Context |
|:-- |:-- |:-- |:--|
| Efficiency Factor | 1.9 | ✅ | Ratio of power to heart rate — higher indicates improved aerobic efficiency. |
| Fatigue Resistance | 0.95 | ✅ | Ability to maintain power over time; >0.9 shows strong endurance resilience. |
| Endurance Decay | 0.02 | ✅ | Rate of endurance loss; <0.05 indicates sustainable aerobic base. |
| Z2 Stability | 0.04 | ✅ | Consistency in Zone 2 heart rate vs. power; <0.05 suggests steady aerobic control. |
| Aerobic Decay | 0.02 | ✅ | Long-term aerobic deterioration rate; <0.03 means stable base conditioning. |


## 🧠 Performance & Coaching Actions


**Recommended Actions:**
1. ✅ Maintain ≥70 % Z1–Z2 volume (Seiler 80/20).
2. ⚠ Improve Zone 2 efficiency: extend duration or adjust IF.
3. ⚠ Apply 10–15 % deload (Friel microcycle logic).
4. ✅ Durability improving (1.00) — maintain current long-ride structure.
5. ⚠ Load intensity low (LIR=0.00) — consider adding tempo or sweet-spot intervals.
6. ✅ Endurance reserve strong (1.00).
7. ✅ Efficiency drift stable (0.00%).
8. ✅ Polarisation optimal (73%).
9. ⚠ Recovery Index poor (0.41) — insert deload or reduce intensity.
10. ---
11. 📊 Metric-based Feedback:
12. ⚠ ACWR (0.79) — Guides short-term vs. chronic load balance adjustments.
13. ⚠ Monotony (2.93) — Used to determine need for rest or deload variation.
14. ✅ Strain (1825.4) — Informs total stress tolerance and recovery planning.
15. ⚠ FatigueTrend (-0.36) — Signals need for load stabilization or downshift.
16. ✅ ZQI (6.8) — Represents proportion of high-intensity time; 5–15 % indicates balanced intensity distribution.
17. ✅ FatOxEfficiency (0.53) — Drives aerobic base and metabolic conditioning feedback.
18. ⚠ Polarisation (0.729) — Determines intensity mix correction (Seiler balance).
19. ✅ FOxI (53.0) — Helps assess Zone 2 progression and fat adaptation.
20. ✅ CUR (47.0) — Advises on fueling strategy and carbohydrate dependency.
21. ✅ GR (0.89) — Glucose Ratio; gauges glycolytic bias — higher values indicate heavy carbohydrate reliance.
22. ✅ MES (33.9) — Summarizes efficiency adaptation response.
23. ⚠ RecoveryIndex (0.414) — Influences rest day scheduling and microcycle tapering.
24. ✅ StressTolerance (6.23) — Reflects sustainable strain capacity; 2–8 indicates robust adaptation to training load.


## 🚴 Weekly Events Summary

| date | name | icu_training_load | moving_time | distance |
|:-- |:-- |:-- |:-- |:--|
| 2025-11-12 | Zwift - 90 base sometimes with coco | 63 | 01:33:49 | 60.4 |
| 2025-11-11 | zAlp low cadence | 88 | 01:23:00 | 35.9 |
| 2025-11-11 | Zwift - Tick Tock in Watopia | 6 | 00:10:13 | 6.4 |
| 2025-11-11 | Otto Walk | 20 | 01:31:04 | 7.0 |
| 2025-11-09 | Rathvel | 129 | 02:07:33 | 54.9 |
| 2025-11-09 | Otto walk | 17 | 01:07:49 | 6.1 |
| 2025-11-08 | 2hrs in the sunshine | 110 | 02:22:48 | 59.3 |
| 2025-11-08 | Otto walk | 12 | 01:10:39 | 6.6 |
| 2025-11-07 | Zwift - Race: Zwift Epic Race - Fuhgeddaboudit B=A | 161 | 02:00:38 | 82.3 |
| 2025-11-07 | Zwift - Tempus Fugit in Watopia | 17 | 00:26:22 | 15.9 |

**Weekly totals:** 13.90 h · 334.8 km · 623 TSS · 10 sessions**
**Cycling Metrics — Mean IF:** 0.71 · **Mean HR:** 116 bpm · **VO₂ max:** 68.6

---
✅ **Audit Completed:** 2025-11-13T11:45:00.033841
**Framework:** URF v5.1 · Core: v16.14 · Enforcement: tier2_enforce_event_only_totals

