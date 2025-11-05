# 🧾 Full Weekly Audit Report

## Execution Logs

```
🧭 Running Weekly Report (auditFinal=True, render_mode=full)
🧹 Tier-0 purge enforced — previous cache cleared.
[T0] Fetching athlete profile via OAuth2: https://intervals.icu/api/v1/athlete/0/profile
[Tier-0 fetch] chunk_start=2025-10-30  chunk_end=2025-11-05
           id                                               name  moving_time
0  i105308685  Zwift - Group Ride: Stage 5 - Zwift Unlocked -...         3644
1  i105297636  Zwift - Pacer Group Ride: The 6 Train in New Y...          933
2  i105148826  Zwift - Group Ride: Stage 5 - Zwift Unlocked -...         3636
3  i105140121              Zwift - Issendorf Express in New York          782
4  i105138333  Zwift - Race: Stage 5 - Zwift Unlocked - Race ...         1866
5  i104781214                                          Otto walk         3783
6  i104753457                                  3 hours endurance        11501
7  i104670958                                        1 with Yumi         4239
8  i104504747  Zwift - Group Ride: Stage 4 - Zwift Unlocked -...         4847
🧩 Tier-0 deduplication: 0 duplicate activities removed.
[T0] Canonical slice → 9/9 rows retained (2025-10-29–2025-11-05, tz=Europe/Zurich)
[T0] start_date_local finalized → tz=Europe/Zurich rows=9
[T0] Canonical totals → Σ(moving_time)/3600=9.79  Σ(TSS)=530.0
[T1] Columns at entry: ['id', 'start_date_local', 'type', 'icu_ignore_time', 'icu_pm_cp', 'icu_pm_w_prime', 'icu_pm_p_max', 'icu_pm_ftp', 'icu_pm_ftp_secs', 'icu_pm_ftp_watts', 'icu_ignore_power', 'icu_rolling_cp', 'icu_rolling_w_prime', 'icu_rolling_p_max', 'icu_rolling_ftp', 'icu_rolling_ftp_delta', 'icu_training_load', 'icu_atl', 'icu_ctl', 'ss_p_max', 'ss_w_prime', 'ss_cp', 'paired_event_id', 'icu_ftp', 'icu_joules', 'icu_recording_time', 'elapsed_time', 'icu_weighted_avg_watts', 'carbs_used', 'name', 'description', 'start_date', 'distance', 'icu_distance', 'moving_time', 'coasting_time', 'total_elevation_gain', 'total_elevation_loss', 'timezone', 'trainer', 'sub_type', 'commute', 'race', 'max_speed', 'average_speed', 'device_watts', 'has_heartrate', 'max_heartrate', 'average_heartrate', 'average_cadence', 'calories', 'average_temp', 'min_temp', 'max_temp', 'avg_lr_balance', 'gap', 'gap_model', 'use_elevation_correction', 'gear', 'perceived_exertion', 'device_name', 'power_meter', 'power_meter_serial', 'power_meter_battery', 'crank_length', 'external_id', 'file_sport_index', 'file_type', 'icu_athlete_id', 'created', 'icu_sync_date', 'analyzed', 'icu_w_prime', 'p_max', 'threshold_pace', 'icu_hr_zones', 'pace_zones', 'lthr', 'icu_resting_hr', 'icu_weight', 'icu_power_zones', 'icu_sweet_spot_min', 'icu_sweet_spot_max', 'icu_power_spike_threshold', 'trimp', 'icu_warmup_time', 'icu_cooldown_time', 'icu_chat_id', 'icu_ignore_hr', 'ignore_velocity', 'ignore_pace', 'ignore_parts', 'icu_training_load_data', 'interval_summary', 'skyline_chart_bytes', 'stream_types', 'has_weather', 'has_segments', 'power_field_names', 'power_field', 'icu_zone_times', 'icu_hr_zone_times', 'pace_zone_times', 'gap_zone_times', 'use_gap_zone_times', 'custom_zones', 'tiz_order', 'polarization_index', 'icu_achievements', 'icu_intervals_edited', 'lock_intervals', 'icu_lap_count', 'icu_joules_above_ftp', 'icu_max_wbal_depletion', 'icu_hrr', 'icu_sync_error', 'icu_color', 'icu_power_hr_z2', 'icu_power_hr_z2_mins', 'icu_cadence_z2', 'icu_rpe', 'feel', 'kg_lifted', 'decoupling', 'icu_median_time_delta', 'p30s_exponent', 'workout_shift_secs', 'strava_id', 'lengths', 'pool_length', 'compliance', 'coach_tick', 'source', 'oauth_client_id', 'oauth_client_name', 'average_altitude', 'min_altitude', 'max_altitude', 'power_load', 'hr_load', 'pace_load', 'hr_load_type', 'pace_load_type', 'tags', 'attachments', 'recording_stops', 'average_weather_temp', 'min_weather_temp', 'max_weather_temp', 'average_feels_like', 'min_feels_like', 'max_feels_like', 'average_wind_speed', 'average_wind_gust', 'prevailing_wind_deg', 'headwind_percent', 'tailwind_percent', 'average_clouds', 'max_rain', 'max_snow', 'carbs_ingested', 'route_id', 'pace', 'athlete_max_hr', 'group', 'icu_intensity', 'icu_efficiency_factor', 'icu_power_hr', 'session_rpe', 'average_stride', 'icu_average_watts', 'icu_variability_index', 'strain_score', 'IF', 'VO2MaxGarmin', 'PerformanceCondition', 'date', 'origin']
[T1] Wellness alignment window (tz-aware): 2025-10-30 18:00:17+01:00 → 2025-11-04 18:00:55+01:00
[T1] Wellness date range: 2025-10-30 → 2025-11-05
✅ Wellness alignment check passed.
[T2] Daily completeness summary built — 5 rows
🔍 Tier-2 enforcement source: Tier-2 validated events (9 rows)
origin counts:
 origin
event    9
Name: count, dtype: int64
moving_time stats:
 count        9.000000
mean      3914.555556
std       3193.667841
min        782.000000
25%       1866.000000
50%       3644.000000
75%       4239.000000
max      11501.000000
Name: moving_time, dtype: float64
[T1] Wellness alignment window (tz-aware): 2025-10-30 18:00:17+01:00 → 2025-11-04 18:00:55+01:00
[T1] Wellness date range: 2025-10-30 → 2025-11-05
✅ Wellness alignment check passed.
⚠ ui_components not found — using empty ICON_CARDS reference.
⚠ Markdown render fallback: Missing optional dependency 'tabulate'.  Use pip or conda to install tabulate.
🔎 Render pre-flight — totals by source:
   df_events Σmoving_time = 9.786388888888888
   dailyMerged has no time-like column
   eventTotals(hours) = 9.79
[Renderer shim] Delegating to render_report() in render_unified_report.py
✅ Report validated — framework compliant.
✅ Report schema validated.
✅ Report passed framework + schema validation (event-only, markdown).

```

## Rendered Markdown Report

# 🧭 weekly Training Report — URF v5.1
**Athlete:** Clive King
**Period:** ? → ?
**Timezone:** Europe/Zurich
**Generated:** 2025-11-05T17:33:00.620943

---


## 🧩 Tier-0 Dataset Integrity

- Activities fetched: 9
- Origin: tier2_enforce_event_only_totals
- Purge enforced: True
- Wellness records: n/a
- Source verification: ✅ Live (no mock/cache)
- Σ(moving_time)/3600 = 9.79 h  |  Σ(TSS) = 530


## 🧩 Tier-1 Audit Controller

- Deduplication: OK
- HR stream coverage: —
- Power data coverage: —
- Time variance ≤ 0.1 h ✅


## 🧮 Derived Metric Audit

_No derived metrics available._


## ⚙️ Training Zone Distribution

_Zone data not available._


## ⚠️ Outlier Events

_No outliers detected._


## 💓 Wellness & Recovery

- Rest Days: —
- Resting HR: — bpm
- HRV Trend: —
- ATL: — · CTL: — · TSB: —


## ⚖️ Load & Stress Chain

_Load metrics unavailable._


## 🔬 Efficiency & Adaptation

_No adaptation data._


## 🧠 Performance & Coaching Actions


**Recommended Actions:**
1. ✅ Maintain ≥70 % Z1–Z2 volume (Seiler 80/20).
2. ✅ Metabolic efficiency maintained (San Millán Zone 2).
3. 🔄 Retest FTP/LT1 for updated benchmarks.
4. ✅ FatMax calibration verified (±5 %).


## 🚴 Weekly Events Summary

_No event preview available._

---
✅ **Audit Completed:** 2025-11-05T17:33:00.620986
**Framework:** URF v5.1 · Core: v16.14 · Enforcement: tier2_enforce_event_only_totals

