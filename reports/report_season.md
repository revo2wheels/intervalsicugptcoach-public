# 🧾 Season Audit Report

## Execution Logs

```
🧭 Running Season Report (auditFinal=False, render_mode=full+metrics)
[T0-LIGHT] Forcing Tier-0 lightweight prefetch before full audit
[Tier-0] Using API endpoint: https://intervalsicugptcoach.clive-a5a.workers.dev
[Tier-0 DEBUG] Calling lightweight URL → https://intervalsicugptcoach.clive-a5a.workers.dev/athlete/0/activities_t0light?oldest=2025-10-17&newest=2025-11-14&fields=id,name,type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin
[T0-LIGHT] Fetching lightweight 28-day dataset → https://intervalsicugptcoach.clive-a5a.workers.dev/athlete/0/activities_t0light?oldest=2025-10-17&newest=2025-11-14&fields=id,name,type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin
[T0-LIGHT] Direct GET → https://intervalsicugptcoach.clive-a5a.workers.dev/athlete/0/activities_t0light?oldest=2025-10-17&newest=2025-11-14&fields=id,name,type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin
[T0-LIGHT] Retrieved 41 activities with 10 fields
[T0-SLICE] 7-day window: 2025-11-08 → 2025-11-15 (9 activities selected)
[T0-DEDUP] Dropped 0 duplicates → 9 unique events
🧭 Tier-0: 7-day subset (lightweight) = 12.98 h | 295.0 km | 533 TSS (9 events)
[T0] Fetching athlete profile via OAuth2: https://intervalsicugptcoach.clive-a5a.workers.dev/athlete/0/profile
[T0] Athlete profile fetched successfully — id=1914741 name=Clive King
[Tier-0 fetch] chunk_start=2025-11-08  chunk_end=2025-11-14
🧩 Tier-0 deduplication: 0 duplicates removed.
[T0] Canonical slice → 9/9 rows retained (2025-11-08–2025-11-14, tz=Europe/Zurich)
None [T0] Expanded icu_zone_times safely → 8 cols, max depth=8
None [T0] Expanded icu_hr_zone_times safely → 7 cols, max depth=7
[T0] Diagnostic: true Σ(event.moving_time)=46722 s → 12.98 h
[T0] Canonical totals → Σ(TSS)=533.0
[T0-ACWR] Fetching historical load window 2025-10-18 → 2025-11-07
[T0-ACWR] Stored 31 baseline activities (ACWR only).
[T0-WELLNESS] Final wellness shape=(7, 43), columns=['date', 'ctl', 'atl', 'rampRate', 'ctlLoad', 'atlLoad', 'sportInfo', 'updated', 'weight', 'restingHR', 'hrv', 'hrvSDNN', 'menstrualPhase', 'menstrualPhasePredicted', 'kcalConsumed', 'sleepSecs', 'sleepScore', 'sleepQuality', 'avgSleepingHR', 'soreness', 'fatigue', 'stress', 'mood', 'motivation', 'injury', 'spO2', 'systolic', 'diastolic', 'hydration', 'hydrationVolume', 'readiness', 'baevskySI', 'bloodGlucose', 'lactate', 'bodyFat', 'abdomen', 'vo2max', 'comments', 'steps', 'respiration', 'locked', 'tempWeight', 'tempRestingHR']
[DEBUG] wellness raw: <class 'pandas.core.frame.DataFrame'> 7
[DEBUG] wellness columns: ['date', 'ctl', 'atl', 'rampRate', 'ctlLoad', 'atlLoad', 'sportInfo', 'updated', 'weight', 'restingHR', 'hrv', 'hrvSDNN', 'menstrualPhase', 'menstrualPhasePredicted', 'kcalConsumed', 'sleepSecs', 'sleepScore', 'sleepQuality', 'avgSleepingHR', 'soreness', 'fatigue', 'stress', 'mood', 'motivation', 'injury', 'spO2', 'systolic', 'diastolic', 'hydration', 'hydrationVolume', 'readiness', 'baevskySI', 'bloodGlucose', 'lactate', 'bodyFat', 'abdomen', 'vo2max', 'comments', 'steps', 'respiration', 'locked', 'tempWeight', 'tempRestingHR']
[DEBUG] wellness head:
          date        ctl         atl  ...  locked  tempWeight  tempRestingHR
0  2025-11-08  91.679720   94.292450  ...    None       False          False
1  2025-11-09  92.957780  101.175865  ...    None        True          False
2  2025-11-10  90.770640   87.707120  ...    None       False          False
3  2025-11-11  91.317184   91.207280  ...    None        True          False
4  2025-11-12  90.650930   87.452270  ...    None        True          False

[5 rows x 43 columns]
[T0] Diagnostic only: 9 rows fetched, moving_time present=True
[T0] Pre-audit complete: activities=9, wellness_rows=7
[Tier-0] Using API endpoint: https://intervalsicugptcoach.clive-a5a.workers.dev
[Tier-0 DEBUG] Calling lightweight URL → https://intervalsicugptcoach.clive-a5a.workers.dev/athlete/0/activities_t0light?oldest=2025-10-17&newest=2025-11-14&fields=id,name,type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin
[T0-LIGHT] Fetching lightweight 28-day dataset → https://intervalsicugptcoach.clive-a5a.workers.dev/athlete/0/activities_t0light?oldest=2025-10-17&newest=2025-11-14&fields=id,name,type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin
[T0-LIGHT] Direct GET → https://intervalsicugptcoach.clive-a5a.workers.dev/athlete/0/activities_t0light?oldest=2025-10-17&newest=2025-11-14&fields=id,name,type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin
[T0-LIGHT] Retrieved 41 activities with 10 fields
[T0-SLICE] 7-day window: 2025-11-08 → 2025-11-15 (9 activities selected)
[T0-DEDUP] Dropped 0 duplicates → 9 unique events
🧭 Tier-0: 7-day subset (lightweight) = 12.98 h | 295.0 km | 533 TSS (9 events)
[T0] Fetching athlete profile via OAuth2: https://intervalsicugptcoach.clive-a5a.workers.dev/athlete/0/profile
[T0] Athlete profile fetched successfully — id=1914741 name=Clive King
[Tier-0 fetch] chunk_start=2025-11-08  chunk_end=2025-11-14
🧩 Tier-0 deduplication: 0 duplicates removed.
[T0] Canonical slice → 9/9 rows retained (2025-11-08–2025-11-14, tz=Europe/Zurich)
None [T0] Expanded icu_zone_times safely → 8 cols, max depth=8
None [T0] Expanded icu_hr_zone_times safely → 7 cols, max depth=7
[T0] Diagnostic: true Σ(event.moving_time)=46722 s → 12.98 h
[T0] Canonical totals → Σ(TSS)=533.0
[T0-ACWR] Fetching historical load window 2025-10-18 → 2025-11-07
[T0-ACWR] Stored 31 baseline activities (ACWR only).
[T0-WELLNESS] Final wellness shape=(7, 43), columns=['date', 'ctl', 'atl', 'rampRate', 'ctlLoad', 'atlLoad', 'sportInfo', 'updated', 'weight', 'restingHR', 'hrv', 'hrvSDNN', 'menstrualPhase', 'menstrualPhasePredicted', 'kcalConsumed', 'sleepSecs', 'sleepScore', 'sleepQuality', 'avgSleepingHR', 'soreness', 'fatigue', 'stress', 'mood', 'motivation', 'injury', 'spO2', 'systolic', 'diastolic', 'hydration', 'hydrationVolume', 'readiness', 'baevskySI', 'bloodGlucose', 'lactate', 'bodyFat', 'abdomen', 'vo2max', 'comments', 'steps', 'respiration', 'locked', 'tempWeight', 'tempRestingHR']
[DEBUG] wellness raw: <class 'pandas.core.frame.DataFrame'> 7
[DEBUG] wellness columns: ['date', 'ctl', 'atl', 'rampRate', 'ctlLoad', 'atlLoad', 'sportInfo', 'updated', 'weight', 'restingHR', 'hrv', 'hrvSDNN', 'menstrualPhase', 'menstrualPhasePredicted', 'kcalConsumed', 'sleepSecs', 'sleepScore', 'sleepQuality', 'avgSleepingHR', 'soreness', 'fatigue', 'stress', 'mood', 'motivation', 'injury', 'spO2', 'systolic', 'diastolic', 'hydration', 'hydrationVolume', 'readiness', 'baevskySI', 'bloodGlucose', 'lactate', 'bodyFat', 'abdomen', 'vo2max', 'comments', 'steps', 'respiration', 'locked', 'tempWeight', 'tempRestingHR']
[DEBUG] wellness head:
          date        ctl         atl  ...  locked  tempWeight  tempRestingHR
0  2025-11-08  91.679720   94.292450  ...    None       False          False
1  2025-11-09  92.957780  101.175865  ...    None        True          False
2  2025-11-10  90.770640   87.707120  ...    None       False          False
3  2025-11-11  91.317184   91.207280  ...    None        True          False
4  2025-11-12  90.650930   87.452270  ...    None        True          False

[5 rows x 43 columns]
[T0] Diagnostic only: 9 rows fetched, moving_time present=True
[T0] Pre-audit complete: activities=9, wellness_rows=7
⚙️ Normalization: detected seconds, no conversion (max=8568)
[T1] Columns at entry: ['id', 'start_date_local', 'type', 'icu_ignore_time', 'icu_pm_cp', 'icu_pm_w_prime', 'icu_pm_p_max', 'icu_pm_ftp', 'icu_pm_ftp_secs', 'icu_pm_ftp_watts', 'icu_ignore_power', 'icu_rolling_cp', 'icu_rolling_w_prime', 'icu_rolling_p_max', 'icu_rolling_ftp', 'icu_rolling_ftp_delta', 'icu_training_load', 'icu_atl', 'icu_ctl', 'ss_p_max', 'ss_w_prime', 'ss_cp', 'paired_event_id', 'icu_ftp', 'icu_joules', 'icu_recording_time', 'elapsed_time', 'icu_weighted_avg_watts', 'carbs_used', 'name', 'description', 'start_date', 'distance', 'icu_distance', 'moving_time', 'coasting_time', 'total_elevation_gain', 'total_elevation_loss', 'timezone', 'trainer', 'sub_type', 'commute', 'race', 'max_speed', 'average_speed', 'device_watts', 'has_heartrate', 'max_heartrate', 'average_heartrate', 'average_cadence', 'calories', 'average_temp', 'min_temp', 'max_temp', 'avg_lr_balance', 'gap', 'gap_model', 'use_elevation_correction', 'gear', 'perceived_exertion', 'device_name', 'power_meter', 'power_meter_serial', 'power_meter_battery', 'crank_length', 'external_id', 'file_sport_index', 'file_type', 'icu_athlete_id', 'created', 'icu_sync_date', 'analyzed', 'icu_w_prime', 'p_max', 'threshold_pace', 'icu_hr_zones', 'pace_zones', 'lthr', 'icu_resting_hr', 'icu_weight', 'icu_power_zones', 'icu_sweet_spot_min', 'icu_sweet_spot_max', 'icu_power_spike_threshold', 'trimp', 'icu_warmup_time', 'icu_cooldown_time', 'icu_chat_id', 'icu_ignore_hr', 'ignore_velocity', 'ignore_pace', 'ignore_parts', 'icu_training_load_data', 'interval_summary', 'skyline_chart_bytes', 'stream_types', 'has_weather', 'has_segments', 'power_field_names', 'power_field', 'pace_zone_times', 'gap_zone_times', 'use_gap_zone_times', 'custom_zones', 'tiz_order', 'polarization_index', 'icu_achievements', 'icu_intervals_edited', 'lock_intervals', 'icu_lap_count', 'icu_joules_above_ftp', 'icu_max_wbal_depletion', 'icu_hrr', 'icu_sync_error', 'icu_color', 'icu_power_hr_z2', 'icu_power_hr_z2_mins', 'icu_cadence_z2', 'icu_rpe', 'feel', 'kg_lifted', 'decoupling', 'icu_median_time_delta', 'p30s_exponent', 'workout_shift_secs', 'strava_id', 'lengths', 'pool_length', 'compliance', 'coach_tick', 'source', 'oauth_client_id', 'oauth_client_name', 'average_altitude', 'min_altitude', 'max_altitude', 'power_load', 'hr_load', 'pace_load', 'hr_load_type', 'pace_load_type', 'tags', 'attachments', 'recording_stops', 'average_weather_temp', 'min_weather_temp', 'max_weather_temp', 'average_feels_like', 'min_feels_like', 'max_feels_like', 'average_wind_speed', 'average_wind_gust', 'prevailing_wind_deg', 'headwind_percent', 'tailwind_percent', 'average_clouds', 'max_rain', 'max_snow', 'carbs_ingested', 'route_id', 'pace', 'athlete_max_hr', 'group', 'icu_intensity', 'icu_efficiency_factor', 'icu_power_hr', 'session_rpe', 'average_stride', 'icu_average_watts', 'icu_variability_index', 'strain_score', 'IF', 'VO2MaxGarmin', 'PerformanceCondition', 'ActivityPowerMeter', 'date', 'origin', 'power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8', 'hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7']
[Tier-1] Visible subset unified: 12.98 h | 295.0 km | 533 TSS | IF=None HR=None VO₂=None
✅ Tier-1 finalization: 9 events | 12.98 h | 533 TSS
🧩 Tier-1 variance check passed (Δh=0.00, ΔTSS=0.0)
[T1] Wellness alignment window (tz-aware): 2025-11-08 09:56:34+01:00 → 2025-11-13 16:59:36+01:00
[T1] Wellness date range: 2025-11-08 → 2025-11-14
✅ Wellness alignment check passed.
[T1] Wellness summary → rest_days=1, rest_hr=42.4, hrv_trend=0.025
[DEBUG-T1] merging load metrics from wellness: ['ctl', 'atl']
[DEBUG-T1] derived TSB column added from CTL-ATL.
[DEBUG-T1] promoted CTL=91.61 ATL=93.28 TSB=-1.67 to context.
[DEBUG-T1] injected load_metrics for renderer: {'CTL': {'value': 91.61, 'status': 'ok'}, 'ATL': {'value': 93.28, 'status': 'ok'}, 'TSB': {'value': -1.67, 'status': 'ok'}}
[DEBUG-T1] sample merged CTL/ATL/TSB:         date        ctl        atl
0 2025-11-13  90.588560  87.525185
1 2025-11-12  90.650930  87.452270
2 2025-11-11  91.317184  91.207280
3 2025-11-11  91.317184  91.207280
4 2025-11-11  91.317184  91.207280
[DEBUG-T1] sanity check before Step 6b — rows in df_activities: 9
[DEBUG-T1] athleteProfile present: True
[DEBUG-T1] athleteProfile keys: ['athlete_id', 'name', 'discipline', 'ftp', 'weight', 'hr_rest', 'hr_max', 'ftp_wkg', 'hr_reserve', 'zone_model', 'training_age_years', 'preferred_units', 'environment', 'timezone', 'updated']
[DEBUG-T1] Starting zone distribution extraction...
[DEBUG-T1] Activity columns sample: ['id', 'start_date_local', 'type', 'icu_ignore_time', 'icu_pm_cp', 'icu_pm_w_prime', 'icu_pm_p_max', 'icu_pm_ftp', 'icu_pm_ftp_secs', 'icu_pm_ftp_watts', 'icu_ignore_power', 'icu_rolling_cp', 'icu_rolling_w_prime', 'icu_rolling_p_max', 'icu_rolling_ftp', 'icu_rolling_ftp_delta', 'icu_training_load', 'icu_atl', 'icu_ctl', 'ss_p_max', 'ss_w_prime', 'ss_cp', 'paired_event_id', 'icu_ftp', 'icu_joules', 'icu_recording_time', 'elapsed_time', 'icu_weighted_avg_watts', 'carbs_used', 'name', 'description', 'start_date', 'distance', 'icu_distance', 'moving_time', 'coasting_time', 'total_elevation_gain', 'total_elevation_loss', 'timezone', 'trainer']
[DEBUG-ZONE] Available columns: ['id', 'start_date_local', 'type', 'icu_ignore_time', 'icu_pm_cp', 'icu_pm_w_prime', 'icu_pm_p_max', 'icu_pm_ftp', 'icu_pm_ftp_secs', 'icu_pm_ftp_watts', 'icu_ignore_power', 'icu_rolling_cp', 'icu_rolling_w_prime', 'icu_rolling_p_max', 'icu_rolling_ftp', 'icu_rolling_ftp_delta', 'icu_training_load', 'icu_atl', 'icu_ctl', 'ss_p_max', 'ss_w_prime', 'ss_cp', 'paired_event_id', 'icu_ftp', 'icu_joules', 'icu_recording_time', 'elapsed_time', 'icu_weighted_avg_watts', 'carbs_used', 'name', 'description', 'start_date', 'distance', 'icu_distance', 'moving_time', 'coasting_time', 'total_elevation_gain', 'total_elevation_loss', 'timezone', 'trainer', 'sub_type', 'commute', 'race', 'max_speed', 'average_speed', 'device_watts', 'has_heartrate', 'max_heartrate', 'average_heartrate', 'average_cadence', 'calories', 'average_temp', 'min_temp', 'max_temp', 'avg_lr_balance', 'gap', 'gap_model', 'use_elevation_correction', 'gear', 'perceived_exertion', 'device_name', 'power_meter', 'power_meter_serial', 'power_meter_battery', 'crank_length', 'external_id', 'file_sport_index', 'file_type', 'icu_athlete_id', 'created', 'icu_sync_date', 'analyzed', 'icu_w_prime', 'p_max', 'threshold_pace', 'icu_hr_zones', 'pace_zones', 'lthr', 'icu_resting_hr', 'icu_weight', 'icu_power_zones', 'icu_sweet_spot_min', 'icu_sweet_spot_max', 'icu_power_spike_threshold', 'trimp', 'icu_warmup_time', 'icu_cooldown_time', 'icu_chat_id', 'icu_ignore_hr', 'ignore_velocity', 'ignore_pace', 'ignore_parts', 'icu_training_load_data', 'interval_summary', 'skyline_chart_bytes', 'stream_types', 'has_weather', 'has_segments', 'power_field_names', 'power_field', 'pace_zone_times', 'gap_zone_times', 'use_gap_zone_times', 'custom_zones', 'tiz_order', 'polarization_index', 'icu_achievements', 'icu_intervals_edited', 'lock_intervals', 'icu_lap_count', 'icu_joules_above_ftp', 'icu_max_wbal_depletion', 'icu_hrr', 'icu_sync_error', 'icu_color', 'icu_power_hr_z2', 'icu_power_hr_z2_mins', 'icu_cadence_z2', 'icu_rpe', 'feel', 'kg_lifted', 'decoupling', 'icu_median_time_delta', 'p30s_exponent', 'workout_shift_secs', 'strava_id', 'lengths', 'pool_length', 'compliance', 'coach_tick', 'source', 'oauth_client_id', 'oauth_client_name', 'average_altitude', 'min_altitude', 'max_altitude', 'power_load', 'hr_load', 'pace_load', 'hr_load_type', 'pace_load_type', 'tags', 'attachments', 'recording_stops', 'average_weather_temp', 'min_weather_temp', 'max_weather_temp', 'average_feels_like', 'min_feels_like', 'max_feels_like', 'average_wind_speed', 'average_wind_gust', 'prevailing_wind_deg', 'headwind_percent', 'tailwind_percent', 'average_clouds', 'max_rain', 'max_snow', 'carbs_ingested', 'route_id', 'pace', 'athlete_max_hr', 'group', 'icu_intensity', 'icu_efficiency_factor', 'icu_power_hr', 'session_rpe', 'average_stride', 'icu_average_watts', 'icu_variability_index', 'strain_score', 'IF', 'VO2MaxGarmin', 'PerformanceCondition', 'ActivityPowerMeter', 'date', 'origin', 'power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8', 'hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7', 'ctl', 'atl', 'tsb']
[DEBUG-ZONE] Detected Power zone columns: ['icu_power_zones', 'power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8']
[DEBUG-ZONE] Detected HR zone columns: ['hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7']
[DEBUG-ZONE] Detected Pace zone columns: ['pace_zones', 'pace_zone_times', 'gap_zone_times']
[DEBUG-ZONES] power zones computed: {'power_z1': 28.2, 'power_z2': 35.6, 'power_z3': 14.2, 'power_z4': 6.5, 'power_z5': 1.4, 'power_z6': 1.6, 'power_z7': 0.6, 'power_z8': 11.8}
[DEBUG-ZONES] hr zones computed: {'hr_z1': 83.4, 'hr_z2': 11.1, 'hr_z3': 3.8, 'hr_z4': 1.4, 'hr_z5': 0.3, 'hr_z6': 0.1, 'hr_z7': 0.0}
[DEBUG-ZONES] No valid data for pace zones — total=0.
[DEBUG-T1] Completed zone distribution extraction.
[DEBUG-T1] Zone distributions now in context:
  zone_dist_power: {'power_z1': 28.2, 'power_z2': 35.6, 'power_z3': 14.2, 'power_z4': 6.5, 'power_z5': 1.4, 'power_z6': 1.6, 'power_z7': 0.6, 'power_z8': 11.8}
  zone_dist_hr: {'hr_z1': 83.4, 'hr_z2': 11.1, 'hr_z3': 3.8, 'hr_z4': 1.4, 'hr_z5': 0.3, 'hr_z6': 0.1, 'hr_z7': 0.0}
  zone_dist_pace: {}
[DEBUG-OUTLIER] Starting detection on 9 rows
[DEBUG-T1] Outlier events detected: 0
[DEBUG-OUTLIER] mean TSS=59.2, std=46.8, threshold=70.2
[DEBUG-OUTLIER] min/max TSS: 6 / 129
None [T2] Daily completeness summary built — 5 rows
📁 Tier-2 module loaded from: C:\Users\user\onedrive\documents\git\revo2wheels\intervalsicugptcoach\audit_core\tier2_enforce_event_only_totals.py
🔍 Tier-2 enforcement source: Tier-2 validated events (9 rows)
origin counts:
 origin
event    9
Name: count, dtype: int64
moving_time stats:
 count       9.000000
mean     5191.333333
std      2263.835076
min       613.000000
25%      4239.000000
50%      5464.000000
75%      5629.000000
max      8568.000000
Name: moving_time, dtype: float64
🧩 Tier-2 enforcing canonical 7-day event window.
🧮 Tier-2: Σ(moving_time)=33915s → 9.42h (Intervals seconds source)
[DEBUG-T2] injected preview (7 rows) and preserved full df_event_only (7 rows)
[DEBUG-T2] enforced load_metrics sync in context: {'CTL': {'value': 91.61, 'status': 'ok'}, 'ATL': {'value': 93.28, 'status': 'ok'}, 'TSB': {'value': -1.67, 'status': 'ok'}}
[T2] Enriched load_metrics propagated to renderer
[T1] Wellness alignment window (tz-aware): 2025-11-08 09:56:34+01:00 → 2025-11-13 16:59:36+01:00
[T1] Wellness date range: 2025-11-08 → 2025-11-14
✅ Wellness alignment check passed.
[T2-ACWR] EWMA model applied → acute=103.84, chronic=116.72, ratio=0.89
[DEBUG] Derived metrics synced: {'ACWR': 0.0, 'Monotony': 0.0, 'Strain': 0.0, 'Polarisation': 0.0, 'RecoveryIndex': 0.0}
[DEBUG-T2X] post-extended load_metrics: {'CTL': {'value': 91.61, 'status': 'ok'}, 'ATL': {'value': 93.28, 'status': 'ok'}, 'TSB': {'value': -1.67, 'status': 'ok'}, 'ACWR': {'value': 0.89, 'status': 'ok'}, 'Monotony': {'value': np.float64(3.33), 'status': 'ok'}, 'Strain': {'value': np.float64(1774.9), 'status': 'ok'}, 'Polarisation': {'value': 0.764, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.334), 'status': 'ok'}}
[T2-ACTIONS] Integrated derived metrics:
{'ACWR': {'value': 0.89, 'status': 'optimal', 'icon': '🟢'}, 'Monotony': {'value': np.float64(3.33), 'status': 'out of range', 'icon': '🔴'}, 'Strain': {'value': np.float64(1774.9), 'status': 'optimal', 'icon': '🟢'}, 'FatigueTrend': {'value': np.float64(-0.181), 'status': 'optimal', 'icon': '🟢'}, 'ZQI': {'value': 4.0, 'status': 'borderline', 'icon': '🟠'}, 'FatOxEfficiency': {'value': 0.566, 'status': 'optimal', 'icon': '🟢'}, 'Polarisation': {'value': 0.764, 'status': 'optimal', 'icon': '🟢'}, 'FOxI': {'value': 56.6, 'status': 'optimal', 'icon': '🟢'}, 'CUR': {'value': 43.4, 'status': 'optimal', 'icon': '🟢'}, 'GR': {'value': 0.77, 'status': 'optimal', 'icon': '🟢'}, 'MES': {'value': np.float64(46.4), 'status': 'optimal', 'icon': '🟢'}, 'RecoveryIndex': {'value': np.float64(0.334), 'status': 'out of range', 'icon': '🔴'}, 'ACWR_Risk': {'value': '✅', 'status': 'no data', 'icon': '⚪'}, 'StressTolerance': {'value': np.float64(5.33), 'status': 'optimal', 'icon': '🟢'}}
[T2-ACTIONS] Integrated extended metrics:
{}
[PATCH-LOCK] Preserved load_metrics before validator: {'CTL': {'value': 91.61, 'status': 'ok'}, 'ATL': {'value': 93.28, 'status': 'ok'}, 'TSB': {'value': -1.67, 'status': 'ok'}, 'ACWR': {'value': 0.89, 'status': 'ok'}, 'Monotony': {'value': np.float64(3.33), 'status': 'ok'}, 'Strain': {'value': np.float64(1774.9), 'status': 'ok'}, 'Polarisation': {'value': 0.764, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.334), 'status': 'ok'}}
[T2-ACWR] EWMA model applied → acute=103.84, chronic=116.72, ratio=0.89
[DEBUG] Derived metrics synced: {'ACWR': 0.0, 'Monotony': 0.0, 'Strain': 0.0, 'Polarisation': 0.0, 'RecoveryIndex': 0.0}
[DEBUG-T2X] post-extended load_metrics: {'CTL': {'value': 91.61, 'status': 'ok'}, 'ATL': {'value': 93.28, 'status': 'ok'}, 'TSB': {'value': -1.67, 'status': 'ok'}, 'ACWR': {'value': 0.89, 'status': 'ok'}, 'Monotony': {'value': np.float64(3.33), 'status': 'ok'}, 'Strain': {'value': np.float64(1774.9), 'status': 'ok'}, 'Polarisation': {'value': 0.764, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.334), 'status': 'ok'}}
🧩 Render mode forced to full+metrics for Unified 10-section layout
[SYNC] No tier1_visibleTotals found; using canonical totals
[TRACE-RUNTIME] entering finalize_and_validate_render()
[TRACE-RUNTIME] context type = <class 'dict'>
[TRACE-RUNTIME] df_events type = <class 'pandas.core.frame.DataFrame'>
[TRACE-RUNTIME] df_events.shape = (9, 192)
[TRACE-RUNTIME] Σ moving_time/3600 = 12.98 h
[TRACE-RUNTIME] Σ icu_training_load = 533
[DEBUG-FINALIZER-ENTRY] load_metrics: {'CTL': {'value': 91.61, 'status': 'ok'}, 'ATL': {'value': 93.28, 'status': 'ok'}, 'TSB': {'value': -1.67, 'status': 'ok'}, 'ACWR': {'value': 0.89, 'status': 'ok'}, 'Monotony': {'value': np.float64(3.33), 'status': 'ok'}, 'Strain': {'value': np.float64(1774.9), 'status': 'ok'}, 'Polarisation': {'value': 0.764, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.334), 'status': 'ok'}}
🧩 Tier-2 validator override (season): Δh=3.56, ΔTSS=122.0, tolerance h≤10.0, TSS≤200.0
✅ Renderer variance within tolerance Δh=3.56, ΔTSS=122.0
✅ Loaded ICON_CARDS from UIcomponents.icon_pack
🔎 Render pre-flight — totals by source:
   df_events Σmoving_time = 12.978333333333333
   df_events Σicu_training_load = 533
   eventTotals(hours) = 9.42

[Tier-2 context diagnostic]
derived_metrics: True
load_metrics: True
adaptation_metrics: True
trend_metrics: True
correlation_metrics: True
[DEBUG] report_header injected: {'athlete': 'Clive King', 'discipline': 'cycling', 'report_type': 'season', 'framework': 'Unified_Reporting_Framework_v5.1', 'timezone': 'Europe/Zurich', 'date_range': '2025-11-08 → 2025-11-14'}
[DEBUG-FINALIZER] pre-render load_metrics: {'CTL': {'value': 91.61, 'status': 'ok'}, 'ATL': {'value': 93.28, 'status': 'ok'}, 'TSB': {'value': -1.67, 'status': 'ok'}, 'ACWR': {'value': 0.89, 'status': 'ok'}, 'Monotony': {'value': np.float64(3.33), 'status': 'ok'}, 'Strain': {'value': np.float64(1774.9), 'status': 'ok'}, 'Polarisation': {'value': 0.764, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.334), 'status': 'ok'}}
[STATE-GUARD] _locked_load_metrics set (prevents recomputation)
[CANONICAL PROPAGATION] hours=9.42, tss=411
[LOCK] Tier-2 canonical totals re-locked before render
[TRACE-DF] Σ df_events(moving_time)/3600 = 12.98 h
[TRACE-DF] Σ df_events(icu_training_load) = 533
[TRACE-CONTEXT] totalHours (context) = 9.42
[TRACE-CONTEXT] totalTss (context) = 411
[TRACE-CONTEXT] eventTotals(hours,tss) = 9.42, 411
[ZONE-PATCH] missing zone_dist, using empty dict
[Renderer shim] Delegating to render_report() in render_unified_report.py

[DEBUG-TEMPLATE: PRE-CALL]
Keys in context: ['render_summary', 'include_coaching_metrics', 'postRenderAudit', 'debug_mode', 'debug_trace', 'tier0_snapshotTotals_7d', 'snapshot_7d_json', 'timezone', 'athleteProfile', 'athlete', 'report_mode', 'window_start', 'window_end', 'df_acwr_base', 'auditPartial', 'auditFinal', 'window_summary', 'knowledge', 'tier1_visibleTotals', 'weeklyEventLogBlock', 'df_events', 'wellness_metrics', 'dailyMerged', 'ctl', 'atl', 'tsb', 'load_metrics', 'zone_dist_power', 'zone_dist_hr', 'zone_dist_pace', 'outliers', 'totalHours', 'totalTss', 'totalDistance', 'eventTotals', 'df_event_only', 'df_event_only_preview', 'df_event_only_full', 'enforcement_layer', '_locked_totals', 'locked_totalHours', 'locked_totalTss', 'locked_totalDistance', 'event_count', 'trace', 'derived_metrics', 'trend_series', 'metrics', 'ACWR', 'Monotony', 'Strain', 'FatigueTrend', 'ZQI', 'FatOxEfficiency', 'Polarisation', 'FOxI', 'CUR', 'GR', 'MES', 'RecoveryIndex', 'ACWR_Risk', 'StressTolerance', 'phases', 'metric_contexts', 'ui_flag', 'actions', '_locked_load_metrics', 'adaptation_metrics', 'trend_metrics', 'correlation_metrics', 'render_mode', 'Duration_total', 'icon_pack', 'force_icon_pack', 'event_log_text', 'report_header', 'summary_patch', 'zone_dist']
load_metrics pre-pass: {'CTL': {'value': 91.61, 'status': 'ok'}, 'ATL': {'value': 93.28, 'status': 'ok'}, 'TSB': {'value': -1.67, 'status': 'ok'}, 'ACWR': {'value': 0.89, 'status': 'ok'}, 'Monotony': {'value': np.float64(3.33), 'status': 'ok'}, 'Strain': {'value': np.float64(1774.9), 'status': 'ok'}, 'Polarisation': {'value': 0.764, 'status': 'ok'}, 'RecoveryIndex': {'value': np.float64(0.334), 'status': 'ok'}, 'totalHours': np.float64(9.42), 'totalTss': 411}
_locked_load_metrics pre-pass: {'totalHours': np.float64(9.42), 'totalTss': 411, 'source': 'tier2_final_lock'}
Report type: season
------------------------------------------------------------
[VERIFY] Renderer override: using Tier-2 df_events (full dataset) for season summary.
🧩 Renderer override: using Tier-2 df_events (full dataset) for season summary.
[SYNC] Legacy totals restored from eventTotals
[TRACE-RENDER-ENTRY] totalHours = 9.42
[TRACE-RENDER-ENTRY] totalTss   = 411
[DEBUG-RENDER] incoming load_metrics: {
  "CTL": {
    "value": 91.61,
    "status": "ok"
  },
  "ATL": {
    "value": 93.28,
    "status": "ok"
  },
  "TSB": {
    "value": -1.67,
    "status": "ok"
  },
  "ACWR": {
    "value": 0.89,
    "status": "ok"
  },
  "Monotony": {
    "value": 3.33,
    "status": "ok"
  },
  "Strain": {
    "value": 1774.9,
    "status": "ok"
  },
  "Polarisation": {
    "value": 0.764,
    "status": "ok"
  },
  "RecoveryIndex": {
    "value": 0.334,
    "status": "ok"
  },
  "totalHours": 9.42,
  "totalTss": 411
}
[TRACE-HEADER] ctx.totalHours = 9.42
[TRACE-HEADER] ctx.totalTss   = 411
[DEBUG] Adaptation metric keys: ['Efficiency Factor', 'Fatigue Resistance', 'Endurance Decay', 'Z2 Stability', 'Aerobic Decay']
[Tier-2] Rendered Seasonal Phase Summary (2 weeks)
[Tier-2] Weekly totals + mean metrics rendered (Tier-1 subset)
[Tier-2] Using canonical summary_patch from Tier-2 validator
[TRACE-DESERIALIZE] wrapped.context totals=9.42, 411

[DEBUG-TEMPLATE: POST-CALL]
Renderer function executed: render_report
Result type: Report
Result keys: ['header', 'markdown', 'type', 'context', 'sections', 'tables', 'lines', 'summary', 'metrics', 'actions', 'phases', 'trends', 'correlation', 'footer']
load_metrics still in context: True
load_metrics post-render: {'CTL': {'value': 91.61, 'status': 'ok'}, 'ATL': {'value': 93.28, 'status': 'ok'}, 'TSB': {'value': -1.67, 'status': 'ok'}, 'ACWR': {'value': 0.89, 'status': 'ok'}, 'Monotony': {'value': 3.33, 'status': 'ok'}, 'Strain': {'value': 1774.9, 'status': 'ok'}, 'Polarisation': {'value': 0.764, 'status': 'ok'}, 'RecoveryIndex': {'value': 0.334, 'status': 'ok'}, 'totalHours': 9.42, 'totalTss': 411}
------------------------------------------------------------
[DEBUG-TEMPLATE] Renderer returned dict — updating report.

[DEBUG-TEMPLATE: FINAL]
Final report keys: ['header', 'markdown', 'type', 'context', 'sections', 'tables', 'lines', 'summary', 'metrics', 'actions', 'phases', 'trends', 'correlation', 'footer']
Final context load_metrics: {'CTL': {'value': 91.61, 'status': 'ok'}, 'ATL': {'value': 93.28, 'status': 'ok'}, 'TSB': {'value': -1.67, 'status': 'ok'}, 'ACWR': {'value': 0.89, 'status': 'ok'}, 'Monotony': {'value': 3.33, 'status': 'ok'}, 'Strain': {'value': 1774.9, 'status': 'ok'}, 'Polarisation': {'value': 0.764, 'status': 'ok'}, 'RecoveryIndex': {'value': 0.334, 'status': 'ok'}, 'totalHours': 9.42, 'totalTss': 411}
================================================================================
[TRACE-POST-RENDER-CHECK] header={'title': 'Season Training Report', 'framework': 'Unified_Reporting_Framework_v5.1', 'athlete': 'Clive King', 'period': '2025-11-08 → 2025-11-14', 'timestamp': '2025-11-14T14:12:41.216039', 'discipline': 'cycling'}
[TRACE-POST-RENDER-CHECK] summary={'totalHours': np.float64(9.42), 'totalTss': 411, 'eventCount': 7, 'period': '2025-11-08 → 2025-11-14'}
[POST-RENDER] Canonical event-only totals enforced → header + summary synced
[PATCH] header rebuilt for schema compliance: {'title': 'Season Training Report', 'framework': 'Unified_Reporting_Framework_v5.1', 'athlete': 'Clive King', 'period': '2025-11-08 → 2025-11-14', 'timestamp': '2025-11-14T14:12:41.216039', 'discipline': 'cycling', 'Total Hours': '9.42 h', 'Total Load (TSS)': 411}
[PATCH] summary rebuilt for schema compliance: {'totalHours': np.float64(9.42), 'totalTss': 411, 'eventCount': 7, 'period': '2025-11-08 → 2025-11-14', 'variance': 0.0, 'zones': {}}
[PATCH] Tier-2 summary override applied → canonical event-only totals enforced
[PATCH] actions dual-structure applied → 24 items
✅ Loaded ICON_CARDS from UIcomponents.icon_pack
✅ Report validated — framework compliant.

[DEBUG-GUARD] --- Report schema diagnostic ---
[DEBUG-GUARD] Report top-level keys: ['header', 'markdown', 'type', 'context', 'sections', 'tables', 'lines', 'summary', 'metrics', 'actions', 'phases', 'trends', 'correlation', 'footer', 'actions_block']
[DEBUG-GUARD] ✅ Schema validation passed for all sections

✅ Final renderer consistency within tolerance Δh=0.00, ΔTSS=0.0

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
  - df_event_only_full
  - df_event_only_preview
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
[TRACE-FINAL] totalHours = 9.42
[TRACE-FINAL] totalTss   = 411
[TRACE-FINAL] eventTotals(hours,tss) = 9.42 411
[TRACE-FINAL] summary_patch = {'totalHours': np.float64(9.42), 'totalTss': 411, 'eventCount': 7, 'period': '2025-11-08 → 2025-11-14', 'variance': 0.0, 'zones': {}}

```

## Rendered Markdown Report

# 🧭 season Training Report — URF v5.1
**Athlete:** Clive King
**Period:** 2025-11-08 → 2025-11-14
**Timezone:** Europe/Zurich
**Generated:** 2025-11-14T14:12:41.212851

---


## 🧩 Tier-0 Dataset Integrity

- Activities fetched: 7
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
| ACWR | 0.89 | 🟢 optimal | EWMA Acute:Chronic Load Ratio — compares 7-day vs 28-day weighted loads. 0.8–1.3 = productive training, <0.8 = recovery or detraining, >1.5 = overload/injury risk. |
| Monotony | 3.33 | 🔴 out of range | 1–2 shows healthy variation; >2.5 means repetitive stress pattern. |
| Strain | 1774.9 | 🟢 optimal | Product of load × monotony; >3500 signals potential overreach. |
| FatigueTrend | -0.181 | 🟢 optimal | 0±0.2 indicates balance; positive trend means accumulating fatigue. |
| ZQI | 400.0 | 🟠 borderline | Zone Quality Index (%) 5-15 high-intensity time is normal <3% too easy, >20% too intense or erratic pacing. |
| FatOxEfficiency | 0.566 | 🟢 optimal | 0.4–0.8 means balanced fat oxidation; lower = carb dependence. |
| Polarisation | 0.764 | 🟢 optimal | 0.75–0.9 matches Seiler 80/20 distribution; <0.7 = too intense. |
| FOxI | 56.6 | 🟢 optimal | FatOx index %; higher values mean more efficient aerobic base. |
| CUR | 43.4 | 🟢 optimal | Carbohydrate Utilisation Ratio; 30-80 balanced metabolic use. |
| GR | 0.77 | 🟢 optimal | Glucose Ratio; >2 indicates excess glycolytic bias. |
| MES | 46.4 | 🟢 optimal | Metabolic Efficiency Score; >20 is good endurance economy. |
| RecoveryIndex | 0.334 | 🔴 out of range | 0.6–1.0 means recovered; <0.5 = heavy fatigue. |
| ACWR_Risk | ✅ | ⚪ no data | Used internally for stability check. |
| StressTolerance | 5.33 | 🟢 optimal | 2–8 indicates sustainable training strain capacity. |


### Power Zones
| Zone | % Time |
|:-- |:--|
| power_z1 | 28.2 |
| power_z2 | 35.6 |
| power_z3 | 14.2 |
| power_z4 | 6.5 |
| power_z5 | 1.4 |
| power_z6 | 1.6 |
| power_z7 | 0.6 |
| power_z8 | 11.8 |


### Heart Rate Zones
| Zone | % Time |
|:-- |:--|
| hr_z1 | 83.4 |
| hr_z2 | 11.1 |
| hr_z3 | 3.8 |
| hr_z4 | 1.4 |
| hr_z5 | 0.3 |
| hr_z6 | 0.1 |
| hr_z7 | 0.0 |


_No pace zone data available._


## ⚠️ Outlier Events

_No outliers detected._


## 💓 Wellness & Recovery

- Rest Days: 1
- Resting HR: 42.4 bpm
- HRV: 56.0 ms (↑ improving (+3.0 ms), prev 53.0 ms)
- Avg Sleep: 8.0 h/night
- Fatigue: 2.0/5
- Stress: 2.0/5
- Readiness: nan/5
- ATL: 93.28 · CTL: 91.61 · TSB: -1.67


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
8. ✅ Polarisation optimal (76%).
9. ⚠ Recovery Index poor (0.33) — insert deload or reduce intensity.
10. ---
11. 📊 Metric-based Feedback:
12. ✅ ACWR (0.89) — Guides short-term vs. chronic load balance adjustments.
13. ⚠ Monotony (3.33) — Used to determine need for rest or deload variation.
14. ✅ Strain (1774.9) — Informs total stress tolerance and recovery planning.
15. ✅ FatigueTrend (-0.181) — Signals need for load stabilization or downshift.
16. ⚠ ZQI (4.0) — Represents proportion of high-intensity time; 5–15 % indicates balanced intensity distribution.
17. ✅ FatOxEfficiency (0.566) — Drives aerobic base and metabolic conditioning feedback.
18. ✅ Polarisation (0.764) — Determines intensity mix correction (Seiler balance).
19. ✅ FOxI (56.6) — Helps assess Zone 2 progression and fat adaptation.
20. ✅ CUR (43.4) — Advises on fueling strategy and carbohydrate dependency.
21. ✅ GR (0.77) — Glucose Ratio; gauges glycolytic bias — higher values indicate heavy carbohydrate reliance.
22. ✅ MES (46.4) — Summarizes efficiency adaptation response.
23. ⚠ RecoveryIndex (0.334) — Influences rest day scheduling and microcycle tapering.
24. ✅ StressTolerance (5.33) — Reflects sustainable strain capacity; 2–8 indicates robust adaptation to training load.


## 🪜 Seasonal Phases Summary

| Phase | Distance | Hours | TSS |
|:-- |:-- |:-- |:--|
| Week 45 | 126883.5 km | 6.8 h | 268 TSS |
| Week 46 | 168085.6 km | 6.2 h | 265 TSS |

**Totals:** 12.98 h · 295.0 km · 533 TSS · 9 sessions**
**Cycling Metrics — Mean IF:** 0.71 · **Mean HR:** 112 bpm · **VO₂ max:** 68.6

---
✅ **Audit Completed:** 2025-11-14T14:12:41.216003
**Framework:** URF v5.1 · Core: v16.14 · Enforcement: tier2_enforce_event_only_totals

