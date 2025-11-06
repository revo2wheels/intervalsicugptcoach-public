# 🧾 Full Weekly Audit Report

## Execution Logs

```
🧭 Running Weekly Report (auditFinal=True, render_mode=full)
🧹 Tier-0 purge enforced — previous cache cleared.
[T0] Fetching athlete profile via OAuth2: https://intervals.icu/api/v1/athlete/0/profile
[Tier-0 fetch] chunk_start=2025-10-31  chunk_end=2025-11-06
           id                                               name  moving_time
0  i105308685  Zwift - Group Ride: Stage 5 - Zwift Unlocked -...         3644
1  i105297636  Zwift - Pacer Group Ride: The 6 Train in New Y...          933
2  i105148826  Zwift - Group Ride: Stage 5 - Zwift Unlocked -...         3636
3  i105140121              Zwift - Issendorf Express in New York          782
4  i105138333  Zwift - Race: Stage 5 - Zwift Unlocked - Race ...         1866
5  i104781214                                          Otto walk         3783
6  i104753457                                  3 hours endurance        11501
7  i104670958                                        1 with Yumi         4239
🧩 Tier-0 deduplication: 0 duplicate activities removed.
[T0] Canonical slice → 8/8 rows retained (2025-10-30–2025-11-06, tz=Europe/Zurich)
[T0] start_date_local finalized → tz=Europe/Zurich rows=8
[T0] Canonical totals → Σ(moving_time)/3600=8.44  Σ(TSS)=424.0
[DEBUG] wellness raw: <class 'pandas.core.frame.DataFrame'> 7
[DEBUG] wellness columns: ['id', 'ctl', 'atl', 'rampRate', 'ctlLoad', 'atlLoad', 'sportInfo', 'updated', 'weight', 'restingHR', 'hrv', 'hrvSDNN', 'menstrualPhase', 'menstrualPhasePredicted', 'kcalConsumed', 'sleepSecs', 'sleepScore', 'sleepQuality', 'avgSleepingHR', 'soreness', 'fatigue', 'stress', 'mood', 'motivation', 'injury', 'spO2', 'systolic', 'diastolic', 'hydration', 'hydrationVolume', 'readiness', 'baevskySI', 'bloodGlucose', 'lactate', 'bodyFat', 'abdomen', 'vo2max', 'comments', 'steps', 'respiration', 'locked', 'tempWeight', 'tempRestingHR']
[DEBUG] wellness head:
            id        ctl        atl  ...  locked  tempWeight  tempRestingHR
0  2025-10-31  91.069214  86.061030  ...    None        True          False
1  2025-11-01  93.091020  98.167015  ...    None       False          False
2  2025-11-02  90.900740  85.098816  ...    None       False          False
3  2025-11-03  91.914795  91.608640  ...    None        True          False
4  2025-11-04  91.210950  87.667076  ...    None        True          False

[5 rows x 43 columns]
[T1] Columns at entry: ['id', 'start_date_local', 'type', 'icu_ignore_time', 'icu_pm_cp', 'icu_pm_w_prime', 'icu_pm_p_max', 'icu_pm_ftp', 'icu_pm_ftp_secs', 'icu_pm_ftp_watts', 'icu_ignore_power', 'icu_rolling_cp', 'icu_rolling_w_prime', 'icu_rolling_p_max', 'icu_rolling_ftp', 'icu_rolling_ftp_delta', 'icu_training_load', 'icu_atl', 'icu_ctl', 'ss_p_max', 'ss_w_prime', 'ss_cp', 'paired_event_id', 'icu_ftp', 'icu_joules', 'icu_recording_time', 'elapsed_time', 'icu_weighted_avg_watts', 'carbs_used', 'name', 'description', 'start_date', 'distance', 'icu_distance', 'moving_time', 'coasting_time', 'total_elevation_gain', 'total_elevation_loss', 'timezone', 'trainer', 'sub_type', 'commute', 'race', 'max_speed', 'average_speed', 'device_watts', 'has_heartrate', 'max_heartrate', 'average_heartrate', 'average_cadence', 'calories', 'average_temp', 'min_temp', 'max_temp', 'avg_lr_balance', 'gap', 'gap_model', 'use_elevation_correction', 'gear', 'perceived_exertion', 'device_name', 'power_meter', 'power_meter_serial', 'power_meter_battery', 'crank_length', 'external_id', 'file_sport_index', 'file_type', 'icu_athlete_id', 'created', 'icu_sync_date', 'analyzed', 'icu_w_prime', 'p_max', 'threshold_pace', 'icu_hr_zones', 'pace_zones', 'lthr', 'icu_resting_hr', 'icu_weight', 'icu_power_zones', 'icu_sweet_spot_min', 'icu_sweet_spot_max', 'icu_power_spike_threshold', 'trimp', 'icu_warmup_time', 'icu_cooldown_time', 'icu_chat_id', 'icu_ignore_hr', 'ignore_velocity', 'ignore_pace', 'ignore_parts', 'icu_training_load_data', 'interval_summary', 'skyline_chart_bytes', 'stream_types', 'has_weather', 'has_segments', 'power_field_names', 'power_field', 'icu_zone_times', 'icu_hr_zone_times', 'pace_zone_times', 'gap_zone_times', 'use_gap_zone_times', 'custom_zones', 'tiz_order', 'polarization_index', 'icu_achievements', 'icu_intervals_edited', 'lock_intervals', 'icu_lap_count', 'icu_joules_above_ftp', 'icu_max_wbal_depletion', 'icu_hrr', 'icu_sync_error', 'icu_color', 'icu_power_hr_z2', 'icu_power_hr_z2_mins', 'icu_cadence_z2', 'icu_rpe', 'feel', 'kg_lifted', 'decoupling', 'icu_median_time_delta', 'p30s_exponent', 'workout_shift_secs', 'strava_id', 'lengths', 'pool_length', 'compliance', 'coach_tick', 'source', 'oauth_client_id', 'oauth_client_name', 'average_altitude', 'min_altitude', 'max_altitude', 'power_load', 'hr_load', 'pace_load', 'hr_load_type', 'pace_load_type', 'tags', 'attachments', 'recording_stops', 'average_weather_temp', 'min_weather_temp', 'max_weather_temp', 'average_feels_like', 'min_feels_like', 'max_feels_like', 'average_wind_speed', 'average_wind_gust', 'prevailing_wind_deg', 'headwind_percent', 'tailwind_percent', 'average_clouds', 'max_rain', 'max_snow', 'carbs_ingested', 'route_id', 'pace', 'athlete_max_hr', 'group', 'icu_intensity', 'icu_efficiency_factor', 'icu_power_hr', 'session_rpe', 'average_stride', 'icu_average_watts', 'icu_variability_index', 'strain_score', 'IF', 'VO2MaxGarmin', 'PerformanceCondition', 'date', 'origin']
[T1] Wellness alignment window (tz-aware): 2025-10-31 18:35:54+01:00 → 2025-11-04 18:00:55+01:00
[T1] Wellness date range: 2025-10-31 → 2025-11-06
✅ Wellness alignment check passed.
[DEBUG-T1] merging load metrics from wellness: ['ctl', 'atl']
[DEBUG-T1] derived TSB column added from CTL-ATL.
[DEBUG-T1] promoted CTL=91.93 ATL=91.57 TSB=0.36 to context.
[DEBUG-T1] injected load_metrics for renderer: {'CTL': {'value': 91.93, 'status': 'ok'}, 'ATL': {'value': 91.57, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}}
[DEBUG-T1] sample merged CTL/ATL/TSB:         date        ctl        atl
0 2025-11-04  91.210950  87.667076
1 2025-11-04  91.210950  87.667076
2 2025-11-03  91.914795  91.608640
3 2025-11-03  91.914795  91.608640
4 2025-11-03  91.914795  91.608640
⚠ No zone columns (Z1–Z7) found in dataset
[T2] Daily completeness summary built — 4 rows
🔍 Tier-2 enforcement source: Tier-2 validated events (8 rows)
origin counts:
 origin
event    8
Name: count, dtype: int64
moving_time stats:
 count        8.000000
mean      3798.000000
std       3393.649111
min        782.000000
25%       1632.750000
50%       3640.000000
75%       3897.000000
max      11501.000000
Name: moving_time, dtype: float64
[DEBUG-T2] enforced load_metrics sync in context: {'CTL': {'value': 91.93, 'status': 'ok'}, 'ATL': {'value': 91.57, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}}
[T1] Wellness alignment window (tz-aware): 2025-10-31 18:35:54+01:00 → 2025-11-04 18:00:55+01:00
[T1] Wellness date range: 2025-10-31 → 2025-11-06
✅ Wellness alignment check passed.
[DEBUG] Derived metrics synced: {'ACWR': 0.0, 'Monotony': 1.77, 'Strain': 750.5, 'Polarisation': 0.0, 'RecoveryIndex': 0.646}
[DEBUG-T2X] post-extended load_metrics: {'CTL': {'value': 91.93, 'status': 'ok'}, 'ATL': {'value': 91.57, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(1.77), 'status': 'ok'}, 'Strain': {'value': np.float64(750.5), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.646), 'status': 'ok'}}
[PATCH-LOCK] Preserved load_metrics before validator: {'CTL': {'value': 91.93, 'status': 'ok'}, 'ATL': {'value': 91.57, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(1.77), 'status': 'ok'}, 'Strain': {'value': np.float64(750.5), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.646), 'status': 'ok'}}
[DEBUG] Derived metrics synced: {'ACWR': 0.0, 'Monotony': 1.77, 'Strain': 750.5, 'Polarisation': 0.0, 'RecoveryIndex': 0.646}
[DEBUG-T2X] post-extended load_metrics: {'CTL': {'value': 91.93, 'status': 'ok'}, 'ATL': {'value': 91.57, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(1.77), 'status': 'ok'}, 'Strain': {'value': np.float64(750.5), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.646), 'status': 'ok'}}
[PATCH-LOCKPOSTEXTENDED] Preserved load_metrics after extended: {'CTL': {'value': 91.93, 'status': 'ok'}, 'ATL': {'value': 91.57, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(1.77), 'status': 'ok'}, 'Strain': {'value': np.float64(750.5), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.646), 'status': 'ok'}}
[PATCH-RESTORE] Reinstated locked load_metrics before finalizer: {'CTL': {'value': 91.93, 'status': 'ok'}, 'ATL': {'value': 91.57, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(1.77), 'status': 'ok'}, 'Strain': {'value': np.float64(750.5), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.646), 'status': 'ok'}}
[DEBUG-FINALIZER-ENTRY] load_metrics: {'CTL': {'value': 91.93, 'status': 'ok'}, 'ATL': {'value': 91.57, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(1.77), 'status': 'ok'}, 'Strain': {'value': np.float64(750.5), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.646), 'status': 'ok'}}
⚠ uicomponents not found — using empty ICON_CARDS reference.
🔎 Render pre-flight — totals by source:
   df_events Σmoving_time = 8.44
   dailyMerged has no time-like column
   eventTotals(hours) = 8.44

[Tier-2 context diagnostic]
derived_metrics: True
load_metrics: True
adaptation_metrics: True
trend_metrics: True
correlation_metrics: True
[DEBUG-FINALIZER] pre-render load_metrics: {'CTL': {'value': 91.93, 'status': 'ok'}, 'ATL': {'value': 91.57, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(1.77), 'status': 'ok'}, 'Strain': {'value': np.float64(750.5), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.646), 'status': 'ok'}}
[Renderer shim] Delegating to render_report() in render_unified_report.py

[DEBUG-TEMPLATE: PRE-CALL]
Keys in context: ['auditPartial', 'auditFinal', 'purge_enforced', 'timezone', 'athleteProfile', 'athlete', 'report_mode', 'window_start', 'window_end', 'window_summary', 'knowledge', 'tier1_eventTotals', 'df_events', 'dailyMerged', 'ctl', 'atl', 'tsb', 'load_metrics', 'zone_dist', 'outliers', 'totalHours', 'totalTss', 'totalDistance', 'eventTotals', 'df_event_only', 'enforcement_layer', '_locked_totals', 'locked_totalHours', 'locked_totalTss', 'locked_totalDistance', 'event_count', 'trace', 'derived_metrics', 'trend_series', 'metrics', 'ACWR', 'Monotony', 'Strain', 'FatigueTrend', 'ZQI', 'FatOxEfficiency', 'Polarisation', 'FOxI', 'CUR', 'GR', 'MES', 'RecoveryIndex', 'ACWR_Risk', 'StressTolerance', 'phases', 'ui_flag', 'actions', '_locked_load_metrics', 'adaptation_metrics', 'trend_metrics', 'correlation_metrics', 'Duration_total', 'icon_pack', 'force_icon_pack', 'event_log_text']
load_metrics pre-pass: {'CTL': {'value': 91.93, 'status': 'ok'}, 'ATL': {'value': 91.57, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(1.77), 'status': 'ok'}, 'Strain': {'value': np.float64(750.5), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.646), 'status': 'ok'}}
_locked_load_metrics pre-pass: {'CTL': {'value': 91.93, 'status': 'ok'}, 'ATL': {'value': 91.57, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(1.77), 'status': 'ok'}, 'Strain': {'value': np.float64(750.5), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.646), 'status': 'ok'}}
Report type: weekly
------------------------------------------------------------
[DEBUG-RENDER] incoming load_metrics: {
  "CTL": {
    "value": 91.93,
    "status": "ok"
  },
  "ATL": {
    "value": 91.57,
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
    "value": 1.77,
    "status": "ok"
  },
  "Strain": {
    "value": 750.5,
    "status": "ok"
  },
  "Polarisation": {
    "value": 0.0,
    "status": "ok"
  },
  "RecoveryIndex": {
    "value": 0.646,
    "status": "ok"
  }
}

[DEBUG-TEMPLATE: POST-CALL]
Renderer function executed: render_report
Result type: Report
Result keys: ['header', 'markdown', 'type', 'context', 'sections', 'tables', 'lines', 'summary', 'metrics', 'actions', 'phases', 'trends', 'correlation', 'footer']
load_metrics still in context: True
load_metrics post-render: {'CTL': {'value': 91.93, 'status': 'ok'}, 'ATL': {'value': 91.57, 'status': 'ok'}, 'TSB': {'value': 0.36, 'status': 'ok'}, 'ACWR': {'value': nan, 'status': 'ok'}, 'Monotony': {'value': np.float64(1.77), 'status': 'ok'}, 'Strain': {'value': np.float64(750.5), 'status': 'ok'}, 'Polarisation': {'value': 0.0, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.646), 'status': 'ok'}}
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
  - zone_dist
[DEBUG] End of context key list

✅ Report passed framework + schema validation (event-only, markdown).

```

## Rendered Markdown Report

# 🧭 weekly Training Report — URF v5.1
**Athlete:** Clive King
**Period:** ? → ?
**Timezone:** Europe/Zurich
**Generated:** 2025-11-06T14:11:14.655460

---


## 🧩 Tier-0 Dataset Integrity

- Activities fetched: 8
- Origin: tier2_enforce_event_only_totals
- Purge enforced: True
- Wellness records: n/a
- Source verification: ✅ Live (no mock/cache)
- Σ(moving_time)/3600 = 8.44 h  |  Σ(TSS) = 424


## 🧩 Tier-1 Audit Controller

- Deduplication: OK
- HR stream coverage: —
- Power data coverage: —
- Time variance ≤ 0.1 h ✅


## 🧮 Derived Metric Audit

| Metric | Value | Status |
|:-- |:-- |:--|
| ACWR | nan | ✅ |
| Monotony | 1.77 | ✅ |
| Strain | 750.5 | ✅ |
| FatigueTrend | 1.05 | ✅ |
| ZQI | nan | ✅ |
| FatOxEfficiency | 0.0 | ✅ |
| Polarisation | 0.0 | ✅ |
| FOxI | 0.0 | ✅ |
| CUR | 250.0 | ✅ |
| GR | 0.0 | ✅ |
| MES | -0.0 | ✅ |
| RecoveryIndex | 0.646 | ✅ |
| ACWR_Risk | ✅ | ✅ |
| StressTolerance | 4.24 | ✅ |


## ⚙️ Training Zone Distribution

_Zone data not available._


## ⚠️ Outlier Events

_No outliers detected._


## 💓 Wellness & Recovery

- Rest Days: —
- Resting HR: — bpm
- HRV Trend: —
- ATL: 91.57 · CTL: 91.93 · TSB: 0.36


## ⚖️ Load & Stress Chain

| Metric | Value | Status |
|:-- |:-- |:--|
| CTL | 91.93 | ok |
| ATL | 91.57 | ok |
| TSB | 0.36 | ok |
| ACWR | nan | ok |
| Monotony | 1.77 | ok |
| Strain | 750.5 | ok |
| Polarisation | 0.0 | ok |
| RecoveryIndex | 0.646 | ok |


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


## 🚴 Weekly Events Summary

_No event preview available._

---
✅ **Audit Completed:** 2025-11-06T14:11:14.655544
**Framework:** URF v5.1 · Core: v16.14 · Enforcement: tier2_enforce_event_only_totals

