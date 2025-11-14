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
🧩 Tier-0 override: requesting 90-day dataset from worker for season report.
[Tier-0 DEBUG] Calling lightweight URL → https://intervalsicugptcoach.clive-a5a.workers.dev/athlete/0/activities_t0light?oldest=2025-08-16&newest=2025-11-14&fields=id,name,type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin
[T0-LIGHT] Fetching lightweight 90-day dataset → https://intervalsicugptcoach.clive-a5a.workers.dev/athlete/0/activities_t0light?oldest=2025-08-16&newest=2025-11-14&fields=id,name,type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin
[T0-LIGHT] Direct GET → https://intervalsicugptcoach.clive-a5a.workers.dev/athlete/0/activities_t0light?oldest=2025-08-16&newest=2025-11-14&fields=id,name,type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin
[T0-LIGHT] Retrieved 113 activities with 10 fields
🧩 Tier-0 override: using 90-day slice for season report.
[T0-SLICE] 90-day window: 2025-08-17 → 2025-11-15 (112 activities selected)
[T0-DEDUP] Dropped 0 duplicates → 112 unique events
🧭 Tier-0: 90-day subset (lightweight) = 178.54 h | 3812.7 km | 7753 TSS (112 events)
[T0] Fetching athlete profile via OAuth2: https://intervalsicugptcoach.clive-a5a.workers.dev/athlete/0/profile
[T0] Athlete profile fetched successfully — id=1914741 name=Clive King
🧩 Tier-0 override: using 90-day oldest/newest for season mode.
🧩 Tier-0: Using lightweight activity fetch for season report (no early return).
[Tier-0 fetch] chunk_start=2025-08-16 21:28:48.299947  chunk_end=2025-08-19 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-08-19 21:28:48.299947  chunk_end=2025-08-22 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-08-22 21:28:48.299947  chunk_end=2025-08-25 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-08-25 21:28:48.299947  chunk_end=2025-08-28 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-08-28 21:28:48.299947  chunk_end=2025-08-31 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-08-31 21:28:48.299947  chunk_end=2025-09-03 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-09-03 21:28:48.299947  chunk_end=2025-09-06 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-09-06 21:28:48.299947  chunk_end=2025-09-09 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-09-09 21:28:48.299947  chunk_end=2025-09-12 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-09-12 21:28:48.299947  chunk_end=2025-09-15 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-09-15 21:28:48.299947  chunk_end=2025-09-18 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-09-18 21:28:48.299947  chunk_end=2025-09-21 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-09-21 21:28:48.299947  chunk_end=2025-09-24 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-09-24 21:28:48.299947  chunk_end=2025-09-27 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-09-27 21:28:48.299947  chunk_end=2025-09-30 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-09-30 21:28:48.299947  chunk_end=2025-10-03 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-10-03 21:28:48.299947  chunk_end=2025-10-06 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-10-06 21:28:48.299947  chunk_end=2025-10-09 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-10-09 21:28:48.299947  chunk_end=2025-10-12 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-10-12 21:28:48.299947  chunk_end=2025-10-15 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-10-15 21:28:48.299947  chunk_end=2025-10-18 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-10-18 21:28:48.299947  chunk_end=2025-10-21 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-10-21 21:28:48.299947  chunk_end=2025-10-24 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-10-24 21:28:48.299947  chunk_end=2025-10-27 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-10-27 21:28:48.299947  chunk_end=2025-10-30 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-10-30 21:28:48.299947  chunk_end=2025-11-02 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-11-02 21:28:48.299947  chunk_end=2025-11-05 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-11-05 21:28:48.299947  chunk_end=2025-11-08 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-11-08 21:28:48.299947  chunk_end=2025-11-11 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-11-11 21:28:48.299947  chunk_end=2025-11-14 21:28:47.299947
[Tier-0 fetch] chunk_start=2025-11-14 21:28:48.299947  chunk_end=2025-11-14 21:28:47.300042
🧩 Tier-0 deduplication: 34 duplicates removed.
[T0] Canonical slice → 113/113 rows retained (2025-08-16–2025-11-14, tz=Europe/Zurich)
None [T0] Expanded icu_zone_times safely → 8 cols, max depth=8
None [T0] Expanded icu_hr_zone_times safely → 7 cols, max depth=7
[T0] Diagnostic: true Σ(event.moving_time)=655438 s → 182.07 h
[T0] Canonical totals → Σ(TSS)=7929.0
[T0-WELLNESS] Final wellness shape=(91, 43), columns=['date', 'ctl', 'atl', 'rampRate', 'ctlLoad', 'atlLoad', 'sportInfo', 'updated', 'weight', 'restingHR', 'hrv', 'hrvSDNN', 'menstrualPhase', 'menstrualPhasePredicted', 'kcalConsumed', 'sleepSecs', 'sleepScore', 'sleepQuality', 'avgSleepingHR', 'soreness', 'fatigue', 'stress', 'mood', 'motivation', 'injury', 'spO2', 'systolic', 'diastolic', 'hydration', 'hydrationVolume', 'readiness', 'baevskySI', 'bloodGlucose', 'lactate', 'bodyFat', 'abdomen', 'vo2max', 'comments', 'steps', 'respiration', 'locked', 'tempWeight', 'tempRestingHR']
[DEBUG] wellness raw: <class 'pandas.core.frame.DataFrame'> 91
[DEBUG] wellness columns: ['date', 'ctl', 'atl', 'rampRate', 'ctlLoad', 'atlLoad', 'sportInfo', 'updated', 'weight', 'restingHR', 'hrv', 'hrvSDNN', 'menstrualPhase', 'menstrualPhasePredicted', 'kcalConsumed', 'sleepSecs', 'sleepScore', 'sleepQuality', 'avgSleepingHR', 'soreness', 'fatigue', 'stress', 'mood', 'motivation', 'injury', 'spO2', 'systolic', 'diastolic', 'hydration', 'hydrationVolume', 'readiness', 'baevskySI', 'bloodGlucose', 'lactate', 'bodyFat', 'abdomen', 'vo2max', 'comments', 'steps', 'respiration', 'locked', 'tempWeight', 'tempRestingHR']
[DEBUG] wellness head:
          date         ctl         atl  ...  locked  tempWeight  tempRestingHR
0  2025-08-16  111.555910  103.709360  ...    None        True          False
1  2025-08-17  111.166374  102.549950  ...    None        True          False
2  2025-08-18  111.091870  103.275475  ...    None        True          False
3  2025-08-19  110.125050   98.845770  ...    None        True          False
4  2025-08-20  107.534000   85.687220  ...    None       False          False

[5 rows x 43 columns]
[T0] Diagnostic only: 113 rows fetched, moving_time present=True
[T0] Pre-audit complete: activities=113, wellness_rows=91
⚙️ Normalization: seconds detected, no conversion (max=21383)
[T1] Running Tier-1 controller (season mode)
[T1] Columns at entry: ['id', 'start_date_local', 'type', 'icu_ignore_time', 'icu_pm_cp', 'icu_pm_w_prime', 'icu_pm_p_max', 'icu_pm_ftp', 'icu_pm_ftp_secs', 'icu_pm_ftp_watts', 'icu_ignore_power', 'icu_rolling_cp', 'icu_rolling_w_prime', 'icu_rolling_p_max', 'icu_rolling_ftp', 'icu_rolling_ftp_delta', 'icu_training_load', 'icu_atl', 'icu_ctl', 'ss_p_max', 'ss_w_prime', 'ss_cp', 'paired_event_id', 'icu_ftp', 'icu_joules', 'icu_recording_time', 'elapsed_time', 'icu_weighted_avg_watts', 'carbs_used', 'name', 'description', 'start_date', 'distance', 'icu_distance', 'moving_time', 'coasting_time', 'total_elevation_gain', 'total_elevation_loss', 'timezone', 'trainer', 'sub_type', 'commute', 'race', 'max_speed', 'average_speed', 'device_watts', 'has_heartrate', 'max_heartrate', 'average_heartrate', 'average_cadence', 'calories', 'average_temp', 'min_temp', 'max_temp', 'avg_lr_balance', 'gap', 'gap_model', 'use_elevation_correction', 'gear', 'perceived_exertion', 'device_name', 'power_meter', 'power_meter_serial', 'power_meter_battery', 'crank_length', 'external_id', 'file_sport_index', 'file_type', 'icu_athlete_id', 'created', 'icu_sync_date', 'analyzed', 'icu_w_prime', 'p_max', 'threshold_pace', 'icu_hr_zones', 'pace_zones', 'lthr', 'icu_resting_hr', 'icu_weight', 'icu_power_zones', 'icu_sweet_spot_min', 'icu_sweet_spot_max', 'icu_power_spike_threshold', 'trimp', 'icu_warmup_time', 'icu_cooldown_time', 'icu_chat_id', 'icu_ignore_hr', 'ignore_velocity', 'ignore_pace', 'ignore_parts', 'icu_training_load_data', 'interval_summary', 'skyline_chart_bytes', 'stream_types', 'has_weather', 'has_segments', 'power_field_names', 'power_field', 'pace_zone_times', 'gap_zone_times', 'use_gap_zone_times', 'custom_zones', 'tiz_order', 'polarization_index', 'icu_achievements', 'icu_intervals_edited', 'lock_intervals', 'icu_lap_count', 'icu_joules_above_ftp', 'icu_max_wbal_depletion', 'icu_hrr', 'icu_sync_error', 'icu_color', 'icu_power_hr_z2', 'icu_power_hr_z2_mins', 'icu_cadence_z2', 'icu_rpe', 'feel', 'kg_lifted', 'decoupling', 'icu_median_time_delta', 'p30s_exponent', 'workout_shift_secs', 'strava_id', 'lengths', 'pool_length', 'compliance', 'coach_tick', 'source', 'oauth_client_id', 'oauth_client_name', 'average_altitude', 'min_altitude', 'max_altitude', 'power_load', 'hr_load', 'pace_load', 'hr_load_type', 'pace_load_type', 'tags', 'attachments', 'recording_stops', 'average_weather_temp', 'min_weather_temp', 'max_weather_temp', 'average_feels_like', 'min_feels_like', 'max_feels_like', 'average_wind_speed', 'average_wind_gust', 'prevailing_wind_deg', 'headwind_percent', 'tailwind_percent', 'average_clouds', 'max_rain', 'max_snow', 'carbs_ingested', 'route_id', 'pace', 'athlete_max_hr', 'group', 'icu_intensity', 'icu_efficiency_factor', 'icu_power_hr', 'session_rpe', 'average_stride', 'icu_average_watts', 'icu_variability_index', 'strain_score', 'VO2MaxGarmin', 'PerformanceCondition', 'IF', 'ActivityPowerMeter', 'date', 'origin', 'power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8', 'hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7']
[Tier-1] Visible subset unified: 12.98 h | 295.0 km | 533 TSS | IF=None HR=None VO₂=None
✅ Tier-1 finalization: 112 events | 12.98 h | 533 TSS
🧩 Tier-1 variance check passed (Δh=0.00, ΔTSS=0.0)
[T1] Wellness alignment window (tz-aware): 2025-08-16 11:01:50+02:00 → 2025-11-13 16:59:36+01:00
[T1] Wellness date range: 2025-08-16 → 2025-11-14
✅ Wellness alignment check passed.
[T1] Wellness summary → rest_days=5, rest_hr=41.5, hrv_trend=0.023
[DEBUG-T1] merging load metrics from wellness: ['ctl', 'atl']
[DEBUG-T1] derived TSB column added from CTL-ATL.
[DEBUG-T1] promoted CTL=97.26 ATL=91.2 TSB=6.06 to context.
[DEBUG-T1] injected load_metrics for renderer: {'CTL': {'value': 97.26, 'status': 'ok'}, 'ATL': {'value': 91.2, 'status': 'ok'}, 'TSB': {'value': 6.06, 'status': 'ok'}}
[DEBUG-T1] sample merged CTL/ATL/TSB:         date         ctl         atl
0 2025-08-19  110.125050   98.845770
1 2025-08-18  111.091870  103.275475
2 2025-08-18  111.091870  103.275475
3 2025-08-18  111.091870  103.275475
4 2025-08-17  111.166374  102.549950
[DEBUG-T1] sanity check before Step 6b — rows in df_activities: 113
[DEBUG-T1] athleteProfile present: True
[DEBUG-T1] athleteProfile keys: ['athlete_id', 'name', 'discipline', 'ftp', 'weight', 'hr_rest', 'hr_max', 'ftp_wkg', 'hr_reserve', 'zone_model', 'training_age_years', 'preferred_units', 'environment', 'timezone', 'updated']
[DEBUG-T1] Starting zone distribution extraction...
[DEBUG-T1] Activity columns sample: ['id', 'start_date_local', 'type', 'icu_ignore_time', 'icu_pm_cp', 'icu_pm_w_prime', 'icu_pm_p_max', 'icu_pm_ftp', 'icu_pm_ftp_secs', 'icu_pm_ftp_watts', 'icu_ignore_power', 'icu_rolling_cp', 'icu_rolling_w_prime', 'icu_rolling_p_max', 'icu_rolling_ftp', 'icu_rolling_ftp_delta', 'icu_training_load', 'icu_atl', 'icu_ctl', 'ss_p_max', 'ss_w_prime', 'ss_cp', 'paired_event_id', 'icu_ftp', 'icu_joules', 'icu_recording_time', 'elapsed_time', 'icu_weighted_avg_watts', 'carbs_used', 'name', 'description', 'start_date', 'distance', 'icu_distance', 'moving_time', 'coasting_time', 'total_elevation_gain', 'total_elevation_loss', 'timezone', 'trainer']
[DEBUG-ZONE] Available columns: ['id', 'start_date_local', 'type', 'icu_ignore_time', 'icu_pm_cp', 'icu_pm_w_prime', 'icu_pm_p_max', 'icu_pm_ftp', 'icu_pm_ftp_secs', 'icu_pm_ftp_watts', 'icu_ignore_power', 'icu_rolling_cp', 'icu_rolling_w_prime', 'icu_rolling_p_max', 'icu_rolling_ftp', 'icu_rolling_ftp_delta', 'icu_training_load', 'icu_atl', 'icu_ctl', 'ss_p_max', 'ss_w_prime', 'ss_cp', 'paired_event_id', 'icu_ftp', 'icu_joules', 'icu_recording_time', 'elapsed_time', 'icu_weighted_avg_watts', 'carbs_used', 'name', 'description', 'start_date', 'distance', 'icu_distance', 'moving_time', 'coasting_time', 'total_elevation_gain', 'total_elevation_loss', 'timezone', 'trainer', 'sub_type', 'commute', 'race', 'max_speed', 'average_speed', 'device_watts', 'has_heartrate', 'max_heartrate', 'average_heartrate', 'average_cadence', 'calories', 'average_temp', 'min_temp', 'max_temp', 'avg_lr_balance', 'gap', 'gap_model', 'use_elevation_correction', 'gear', 'perceived_exertion', 'device_name', 'power_meter', 'power_meter_serial', 'power_meter_battery', 'crank_length', 'external_id', 'file_sport_index', 'file_type', 'icu_athlete_id', 'created', 'icu_sync_date', 'analyzed', 'icu_w_prime', 'p_max', 'threshold_pace', 'icu_hr_zones', 'pace_zones', 'lthr', 'icu_resting_hr', 'icu_weight', 'icu_power_zones', 'icu_sweet_spot_min', 'icu_sweet_spot_max', 'icu_power_spike_threshold', 'trimp', 'icu_warmup_time', 'icu_cooldown_time', 'icu_chat_id', 'icu_ignore_hr', 'ignore_velocity', 'ignore_pace', 'ignore_parts', 'icu_training_load_data', 'interval_summary', 'skyline_chart_bytes', 'stream_types', 'has_weather', 'has_segments', 'power_field_names', 'power_field', 'pace_zone_times', 'gap_zone_times', 'use_gap_zone_times', 'custom_zones', 'tiz_order', 'polarization_index', 'icu_achievements', 'icu_intervals_edited', 'lock_intervals', 'icu_lap_count', 'icu_joules_above_ftp', 'icu_max_wbal_depletion', 'icu_hrr', 'icu_sync_error', 'icu_color', 'icu_power_hr_z2', 'icu_power_hr_z2_mins', 'icu_cadence_z2', 'icu_rpe', 'feel', 'kg_lifted', 'decoupling', 'icu_median_time_delta', 'p30s_exponent', 'workout_shift_secs', 'strava_id', 'lengths', 'pool_length', 'compliance', 'coach_tick', 'source', 'oauth_client_id', 'oauth_client_name', 'average_altitude', 'min_altitude', 'max_altitude', 'power_load', 'hr_load', 'pace_load', 'hr_load_type', 'pace_load_type', 'tags', 'attachments', 'recording_stops', 'average_weather_temp', 'min_weather_temp', 'max_weather_temp', 'average_feels_like', 'min_feels_like', 'max_feels_like', 'average_wind_speed', 'average_wind_gust', 'prevailing_wind_deg', 'headwind_percent', 'tailwind_percent', 'average_clouds', 'max_rain', 'max_snow', 'carbs_ingested', 'route_id', 'pace', 'athlete_max_hr', 'group', 'icu_intensity', 'icu_efficiency_factor', 'icu_power_hr', 'session_rpe', 'average_stride', 'icu_average_watts', 'icu_variability_index', 'strain_score', 'VO2MaxGarmin', 'PerformanceCondition', 'IF', 'ActivityPowerMeter', 'date', 'origin', 'power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8', 'hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7', 'ctl', 'atl', 'tsb']
[DEBUG-ZONE] Detected Power zone columns: ['icu_power_zones', 'power_z1', 'power_z2', 'power_z3', 'power_z4', 'power_z5', 'power_z6', 'power_z7', 'power_z8']
[DEBUG-ZONE] Detected HR zone columns: ['hr_z1', 'hr_z2', 'hr_z3', 'hr_z4', 'hr_z5', 'hr_z6', 'hr_z7']
[DEBUG-ZONE] Detected Pace zone columns: ['pace_zones', 'pace_zone_times', 'gap_zone_times']
[DEBUG-ZONES] power zones computed: {'power_z1': 33.3, 'power_z2': 24.3, 'power_z3': 15.6, 'power_z4': 9.2, 'power_z5': 3.7, 'power_z6': 1.7, 'power_z7': 0.4, 'power_z8': 11.8}
[DEBUG-ZONES] hr zones computed: {'hr_z1': 71.6, 'hr_z2': 15.1, 'hr_z3': 4.9, 'hr_z4': 4.9, 'hr_z5': 1.3, 'hr_z6': 1.3, 'hr_z7': 0.8}
[DEBUG-ZONES] No valid data for pace zones — total=0.
[DEBUG-T1] Completed zone distribution extraction.
[DEBUG-T1] Zone distributions now in context:
  zone_dist_power: {'power_z1': 33.3, 'power_z2': 24.3, 'power_z3': 15.6, 'power_z4': 9.2, 'power_z5': 3.7, 'power_z6': 1.7, 'power_z7': 0.4, 'power_z8': 11.8}
  zone_dist_hr: {'hr_z1': 71.6, 'hr_z2': 15.1, 'hr_z3': 4.9, 'hr_z4': 4.9, 'hr_z5': 1.3, 'hr_z6': 1.3, 'hr_z7': 0.8}
  zone_dist_pace: {}
[DEBUG-OUTLIER] Starting detection on 113 rows
[DEBUG-T1] Outlier events detected: 10
[DEBUG-OUTLIER] mean TSS=70.2, std=59.6, threshold=89.4
[DEBUG-OUTLIER] min/max TSS: 1 / 277
None [T2] Daily completeness summary built — 72 rows
[WARN] Could not parse snapshot_7d_json for enforcement: cannot access local variable 'pd' where it is not associated with a value
📁 Tier-2 module loaded from: C:\Users\user\onedrive\documents\git\revo2wheels\intervalsicugptcoach\audit_core\tier2_enforce_event_only_totals.py
🔍 Tier-2 enforcement source: Tier-2 validated events (113 rows)
origin counts:
 origin
event    113
Name: count, dtype: int64
moving_time stats:
 count      113.000000
mean      5800.336283
std       3527.283626
min        251.000000
25%       3783.000000
50%       4802.000000
75%       7437.000000
max      21383.000000
Name: moving_time, dtype: float64
🧩 Tier-2 override: retaining full df_source for season summary (no 7-day enforcement).
🧩 Tier-2 override: recomputing canonical totals for season report (full dataset).
🧮 Tier-2 (season): Σ(moving_time)=655438s → 182.07h, Σ(TSS)=7929.0, Σ(Distance)=3853.8 km
[DEBUG-T2] injected preview (10 rows) and preserved full df_event_only (113 rows)
[DEBUG-T2] enforced load_metrics sync in context: {'CTL': {'value': 97.26, 'status': 'ok'}, 'ATL': {'value': 91.2, 'status': 'ok'}, 'TSB': {'value': 6.06, 'status': 'ok'}}
[T2] Enriched load_metrics propagated to renderer
[SYNC] df_events replaced with df_scope (113 rows) for Tier-2 validator
[T2-ACTIONS] Integrated derived metrics:
{'ACWR': {'value': 0.98, 'status': 'ok', 'desc': '90-day mean of acute/chronic EWMA ratio'}, 'Monotony': {'value': 1.94, 'status': 'ok', 'desc': 'Load variability'}, 'Strain': {'value': 20.8, 'status': 'ok', 'desc': 'Weekly-normalized long-term training strain'}, 'FatigueTrend': {'value': nan, 'status': 'n/a', 'desc': '7d vs 28d load delta', 'icon': '⚪'}, 'ZQI': {'value': 66.9, 'status': 'ok', 'desc': 'Zone Quality Index'}, 'FatOxEfficiency': {'value': 0.602, 'status': 'ok', 'desc': 'Fat oxidation efficiency'}, 'Polarisation': {'value': 0.9, 'status': 'ok', 'desc': 'Intensity distribution'}, 'FOxI': {'value': 60.2, 'status': 'ok', 'desc': 'Fat oxidation index'}, 'CUR': {'value': 39.8, 'status': 'ok', 'desc': 'Carbohydrate utilisation ratio'}, 'GR': {'value': 1.61, 'status': 'ok', 'desc': 'Glucose ratio'}, 'MES': {'value': 22.4, 'status': 'ok', 'desc': 'Metabolic efficiency score'}, 'RecoveryIndex': {'value': 0.612, 'status': 'ok', 'desc': 'Recovery readiness'}, 'ACWR_Risk': {'value': nan, 'status': 'ok', 'desc': 'Stability risk check'}, 'StressTolerance': {'value': 2.0, 'status': 'ok', 'desc': 'Season-normalized sustainable strain (2–8 ideal)'}}
[T2-ACTIONS] Integrated extended metrics:
{}
[PATCH-LOCK] Preserved load_metrics before validator: {'CTL': {'value': 97.26, 'status': 'ok'}, 'ATL': {'value': 91.2, 'status': 'ok'}, 'TSB': {'value': 6.06, 'status': 'ok'}}
🧩 Render mode forced to full+metrics for URF layout
[TRACE-RUNTIME] entering finalize_and_validate_render()
[TRACE-RUNTIME] context type = <class 'dict'>
[TRACE-RUNTIME] df_events type = <class 'pandas.core.frame.DataFrame'>
[TRACE-RUNTIME] df_events.shape = (113, 196)
[TRACE-RUNTIME] Σ moving_time/3600 = 182.07 h
[TRACE-RUNTIME] Σ icu_training_load = 7929
[DEBUG-FINALIZER-ENTRY] load_metrics: {'CTL': {'value': 97.26, 'status': 'ok'}, 'ATL': {'value': 91.2, 'status': 'ok'}, 'TSB': {'value': 6.06, 'status': 'ok'}}
[T2] Season mode → initialized minimal Report object for return.
🧩 [T2] Season mode or empty df_events — skipping Δh/ΔTSS validation.
✅ Render + validation completed for season

```

## Rendered Markdown Report

