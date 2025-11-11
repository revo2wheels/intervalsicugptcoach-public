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
[T0] Canonical slice → 7/7 rows retained (2025-11-05–2025-11-11, tz=Europe/Zurich)
[T0] Diagnostic: true Σ(event.moving_time)=39116 s → 10.87 h
[T0] Canonical totals → Σ(TSS)=526.0
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
[T0] Pre-audit complete: activities=7, wellness_rows=7
⚙️ Normalization: detected seconds, no conversion (max=8568)
[T1] Columns at entry: ['id', 'start_date_local', 'icu_training_load', 'elapsed_time', 'name', 'start_date', 'distance', 'moving_time', 'icu_zone_times', 'icu_hr_zone_times', 'date', 'origin']
🧮 Tier-1: using enforced seconds→hours conversion (Σmoving_time=39116 s → 10.87 h)
[T1] Wellness alignment window (tz-aware): 2025-11-06 18:16:29+01:00 → 2025-11-09 12:14:22+01:00
[T1] Wellness date range: 2025-11-05 → 2025-11-11
✅ Wellness alignment check passed.
[DEBUG-T1] merging load metrics from wellness: ['ctl', 'atl']
[DEBUG-T1] derived TSB column added from CTL-ATL.
[DEBUG-T1] promoted CTL=91.43 ATL=92.51 TSB=-1.07 to context.
[DEBUG-T1] injected load_metrics for renderer: {'CTL': {'value': 91.43, 'status': 'ok'}, 'ATL': {'value': 92.51, 'status': 'ok'}, 'TSB': {'value': -1.07, 'status': 'ok'}}
[DEBUG-T1] sample merged CTL/ATL/TSB:         date       ctl         atl
0 2025-11-09  92.95778  101.175865
1 2025-11-09  92.95778  101.175865
2 2025-11-08  91.67972   94.292450
3 2025-11-08  91.67972   94.292450
4 2025-11-07  90.94914   90.037544
[DEBUG-T1] sanity check before Step 6b — rows in df_activities: 7
[DEBUG-T1] athleteProfile present: True
[DEBUG-T1] athleteProfile keys: ['athlete_id', 'name', 'discipline', 'ftp', 'weight', 'hr_rest', 'hr_max', 'ftp_wkg', 'hr_reserve', 'zone_model', 'training_age_years', 'preferred_units', 'environment', 'timezone', 'updated']
[DEBUG-T1] Starting zone distribution extraction...
[DEBUG-T1] Activity columns sample: ['id', 'start_date_local', 'icu_training_load', 'elapsed_time', 'name', 'start_date', 'distance', 'moving_time', 'icu_zone_times', 'icu_hr_zone_times', 'date', 'origin', 'ctl', 'atl', 'tsb']
[DEBUG-ZONE] Available columns: ['id', 'start_date_local', 'icu_training_load', 'elapsed_time', 'name', 'start_date', 'distance', 'moving_time', 'icu_zone_times', 'icu_hr_zone_times', 'date', 'origin', 'ctl', 'atl', 'tsb']
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
[DEBUG-OUTLIER] mean TSS: 75.14285714285714 std: 60.9082057181914
[DEBUG-OUTLIER] min/max TSS: 12 / 161
None [T2] Daily completeness summary built — 4 rows
📁 Tier-2 module loaded from: C:\Users\user\OneDrive\Documents\GIT\revo2wheels\intervalsicugptcoach\audit_core\tier2_enforce_event_only_totals.py
🔍 Tier-2 enforcement source: Tier-2 validated events (7 rows)
origin counts:
 origin
event    7
Name: count, dtype: int64
moving_time stats:
 count       7.000000
mean     5588.000000
std      2452.018352
min      1582.000000
25%      4154.000000
50%      5767.000000
75%      7445.500000
max      8568.000000
Name: moving_time, dtype: float64
🧮 Tier-2: Σ(moving_time)=39116s → 10.87h (Intervals seconds source)
[DEBUG-T2] injected df_event_only preview: 7 rows (sorted by start_date_local)
[DEBUG-T2] enforced load_metrics sync in context: {'CTL': {'value': 91.43, 'status': 'ok'}, 'ATL': {'value': 92.51, 'status': 'ok'}, 'TSB': {'value': -1.07, 'status': 'ok'}}
[T1] Wellness alignment window (tz-aware): 2025-11-06 18:16:29+01:00 → 2025-11-09 12:14:22+01:00
[T1] Wellness date range: 2025-11-05 → 2025-11-11
✅ Wellness alignment check passed.
[DEBUG] Derived metrics synced: {'ACWR': 0.0, 'Monotony': 3.18, 'Strain': 1672.7, 'Polarisation': 0.0, 'RecoveryIndex': 0.364}
[DEBUG-T2X] post-extended load_metrics: {'CTL': {'value': 91.43, 'status': 'ok'}, 'ATL': {'value': 92.51, 'status': 'ok'}, 'TSB': {'value': -1.07, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(3.18), 'status': 'ok'}, 'Strain': {'value': np.float64(1672.7), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.364), 'status': 'ok'}}
[PATCH-LOCK] Preserved load_metrics before validator: {'CTL': {'value': 91.43, 'status': 'ok'}, 'ATL': {'value': 92.51, 'status': 'ok'}, 'TSB': {'value': -1.07, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(3.18), 'status': 'ok'}, 'Strain': {'value': np.float64(1672.7), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.364), 'status': 'ok'}}
[DEBUG] Derived metrics synced: {'ACWR': 0.0, 'Monotony': 3.18, 'Strain': 1672.7, 'Polarisation': 0.0, 'RecoveryIndex': 0.364}
[DEBUG-T2X] post-extended load_metrics: {'CTL': {'value': 91.43, 'status': 'ok'}, 'ATL': {'value': 92.51, 'status': 'ok'}, 'TSB': {'value': -1.07, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(3.18), 'status': 'ok'}, 'Strain': {'value': np.float64(1672.7), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.364), 'status': 'ok'}}
🧩 Render mode forced to full+metrics for Unified 10-section layout
[DEBUG-FINALIZER-ENTRY] load_metrics: {'CTL': {'value': 91.43, 'status': 'ok'}, 'ATL': {'value': 92.51, 'status': 'ok'}, 'TSB': {'value': -1.07, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(3.18), 'status': 'ok'}, 'Strain': {'value': np.float64(1672.7), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.364), 'status': 'ok'}}
✅ Loaded ICON_CARDS from UIcomponents.icon_pack
🔎 Render pre-flight — totals by source:
   df_events Σmoving_time = 10.865555555555556
   df_events Σicu_training_load = 526
   eventTotals(hours) = 10.87

[Tier-2 context diagnostic]
derived_metrics: True
load_metrics: True
adaptation_metrics: True
trend_metrics: True
correlation_metrics: True
[DEBUG] report_header injected: {'athlete': 'Clive King', 'discipline': 'cycling', 'report_type': 'weekly', 'framework': 'Unified_Reporting_Framework_v5.1', 'timezone': 'Europe/Zurich', 'date_range': '2025-11-05 → 2025-11-11'}
[DEBUG-FINALIZER] pre-render load_metrics: {'CTL': {'value': 91.43, 'status': 'ok'}, 'ATL': {'value': 92.51, 'status': 'ok'}, 'TSB': {'value': -1.07, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(3.18), 'status': 'ok'}, 'Strain': {'value': np.float64(1672.7), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.364), 'status': 'ok'}}
[CANONICAL PROPAGATION] totalHours=10.87, totalTss=526
[Renderer shim] Delegating to render_report() in render_unified_report.py

[DEBUG-TEMPLATE: PRE-CALL]
Keys in context: ['merge_events', 'render_summary', 'include_coaching_metrics', 'postRenderAudit', 'debug_trace', 'totalDistance', 'auditPartial', 'auditFinal', 'purge_enforced', 'timezone', 'athleteProfile', 'athlete', 'report_mode', 'window_start', 'window_end', 'window_summary', 'knowledge', 'tier1_eventTotals', 'df_events', 'dailyMerged', 'ctl', 'atl', 'tsb', 'load_metrics', 'zone_dist_power', 'zone_dist_hr', 'zone_dist_pace', 'outliers', 'totalHours', 'totalTss', 'eventTotals', 'df_event_only', 'enforcement_layer', '_locked_totals', 'locked_totalHours', 'locked_totalTss', 'locked_totalDistance', 'event_count', 'trace', 'derived_metrics', 'trend_series', 'metrics', 'ACWR', 'Monotony', 'Strain', 'FatigueTrend', 'ZQI', 'FatOxEfficiency', 'Polarisation', 'FOxI', 'CUR', 'GR', 'MES', 'RecoveryIndex', 'ACWR_Risk', 'StressTolerance', 'phases', 'ui_flag', 'actions', '_locked_load_metrics', 'adaptation_metrics', 'trend_metrics', 'correlation_metrics', 'render_mode', 'Duration_total', 'icon_pack', 'force_icon_pack', 'event_log_text', 'report_header']
load_metrics pre-pass: {'CTL': {'value': 91.43, 'status': 'ok'}, 'ATL': {'value': 92.51, 'status': 'ok'}, 'TSB': {'value': -1.07, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(3.18), 'status': 'ok'}, 'Strain': {'value': np.float64(1672.7), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.364), 'status': 'ok'}, 'totalHours': np.float64(10.87), 'totalTss': 526}
_locked_load_metrics pre-pass: {'CTL': {'value': 91.43, 'status': 'ok'}, 'ATL': {'value': 92.51, 'status': 'ok'}, 'TSB': {'value': -1.07, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(3.18), 'status': 'ok'}, 'Strain': {'value': np.float64(1672.7), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.364), 'status': 'ok'}}
Report type: weekly
------------------------------------------------------------
[DEBUG-RENDER] incoming load_metrics: {
  "CTL": {
    "value": 91.43,
    "status": "ok"
  },
  "ATL": {
    "value": 92.51,
    "status": "ok"
  },
  "TSB": {
    "value": -1.07,
    "status": "ok"
  },
  "ACWR": {
    "value": NaN,
    "status": "ok"
  },
  "Monotony": {
    "value": 3.18,
    "status": "ok"
  },
  "Strain": {
    "value": 1672.7,
    "status": "ok"
  },
  "Polarisation": {
    "value": 0.0,
    "status": "ok"
  },
  "RecoveryIndex": {
    "value": 0.364,
    "status": "ok"
  },
  "totalHours": 10.87,
  "totalTss": 526
}
⚠ Renderer call failed: 'numpy.float64' object has no attribute 'get'
[PATCH] header rebuilt for schema compliance: {'title': 'Weekly Training Report', 'framework': 'Unified_Reporting_Framework_v5.1', 'athlete': 'Clive King', 'discipline': 'cycling', 'period': '2025-11-05 → 2025-11-11', 'timezone': 'Europe/Zurich'}
[PATCH] summary rebuilt for schema compliance: {'totalHours': np.float64(10.87), 'totalTss': 526, 'eventCount': 7, 'period': '2025-11-05 → 2025-11-11', 'variance': 0.0, 'zones': {}}
[PATCH] actions dual-structure applied → 3 items
✅ Loaded ICON_CARDS from UIcomponents.icon_pack
✅ Report validated — framework compliant.

[DEBUG-GUARD] --- Report schema diagnostic ---
[DEBUG-GUARD] Report top-level keys: ['merge_events', 'render_summary', 'include_coaching_metrics', 'postRenderAudit', 'debug_trace', 'totalDistance', 'auditPartial', 'auditFinal', 'purge_enforced', 'timezone', 'athleteProfile', 'athlete', 'report_mode', 'window_start', 'window_end', 'window_summary', 'knowledge', 'tier1_eventTotals', 'df_events', 'dailyMerged', 'ctl', 'atl', 'tsb', 'load_metrics', 'zone_dist_power', 'zone_dist_hr', 'zone_dist_pace', 'outliers', 'totalHours', 'totalTss', 'eventTotals', 'df_event_only', 'enforcement_layer', '_locked_totals', 'locked_totalHours', 'locked_totalTss', 'locked_totalDistance', 'event_count', 'trace', 'derived_metrics', 'trend_series', 'metrics', 'ACWR', 'Monotony', 'Strain', 'FatigueTrend', 'ZQI', 'FatOxEfficiency', 'Polarisation', 'FOxI', 'CUR', 'GR', 'MES', 'RecoveryIndex', 'ACWR_Risk', 'StressTolerance', 'phases', 'ui_flag', 'actions', '_locked_load_metrics', 'adaptation_metrics', 'trend_metrics', 'correlation_metrics', 'render_mode', 'Duration_total', 'icon_pack', 'force_icon_pack', 'event_log_text', 'report_header', 'header', 'summary', 'trends', 'correlation', 'footer', 'actions_block']
[DEBUG-GUARD] actions type: <class 'list'>
[DEBUG-GUARD] actions value (non-dict): ['⚠ Increase Z1–Z2 share to ≥70 % (Seiler 80/20).', '⚠ Improve Zone 2 efficiency: extend duration or adjust IF.', '⚠ Apply 10–15 % deload (Friel microcycle logic).']
[DEBUG-GUARD] ---------------------------------


[DEBUG] Context keys available before finalize_and_validate_render() return:
  - ACWR
  - ACWR_Risk
  - CUR
  - Duration_total
  - FOxI
  - FatOxEfficiency
  - FatigueTrend
  - GR
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
  - actions_block
  - adaptation_metrics
  - athlete
  - athleteProfile
  - atl
  - auditFinal
  - auditPartial
  - correlation
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
  - footer
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
  - summary
  - tier1_eventTotals
  - timezone
  - totalDistance
  - totalHours
  - totalTss
  - trace
  - trend_metrics
  - trend_series
  - trends
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

