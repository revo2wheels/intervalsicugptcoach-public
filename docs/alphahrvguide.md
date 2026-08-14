# AlphaHRV → Intervals.icu → Montis setup guide

## Purpose

This guide exposes useful AlphaHRV workout summaries through the shared Intervals.icu activity fields supplied by Clive King so Montis can retrieve them from the activity API.

The current data path is:

```text
Chest strap RR intervals
        ↓
AlphaHRV Connect IQ data field on Garmin
        ↓
FIT developer fields
        ↓
Intervals.icu activity streams and session fields
        ↓
Shared Intervals.icu activity fields
        ↓
Montis One Day Full or explicitly requested Light fields (at this time its not exposed in reports)
```

## 1. Garmin and AlphaHRV setup

### Requirements

- A Garmin device compatible with the AlphaHRV Connect IQ data field.
- AlphaHRV installed from the Connect IQ Store.
- AlphaHRV added to a data screen in every Garmin sport profile where it will be used.
- A chest strap capable of supplying reliable RR intervals. A high-quality ECG chest strap is strongly recommended; wrist optical HR is not suitable for dependable exercise HRV analysis.
- AlphaHRV paired to the strap according to the application's own ANT+/Bluetooth instructions. AlphaHRV uses its own sensor connection, which is separate from Garmin's native HR connection.

### Recommended AlphaHRV FIT settings for Montis

| AlphaHRV setting | Recommended | Reason |
|---|---:|---|
| Save ALPHA1 to FIT file | On | Required for the Intervals `dfa_a1` stream and all DFA-a1 summaries. |
| Save ARTIFACTS to FIT file | On | Required to assess RR-input quality. |
| Save RESPIRATION RATE to FIT file | On | Required for mean respiration and calculated RRa1. |
| Save RRA1 to FIT file | Optional | The Montis-compatible `MeanRRa1` field is calculated from respiration and DFA-a1. Keep this on only if the native RRA1 developer field is useful elsewhere. |
| Save READINESS to FIT file | On | Required for the activity-level `readiness_alphahrv` session field. |
| Save HEART RATE to FIT file | Off | Garmin already records native HR. Enabling this creates a duplicate AlphaHRV HR field and can cause downstream ambiguity. |
| Show readiness alert panel | Optional | Controls the on-device alert; it is not required merely to expose the saved activity field. |

After changing any setting marked **restart required**:

1. Save the AlphaHRV settings.
2. Synchronise the Garmin device.
3. Fully exit and restart the Garmin activity profile before recording the next activity.

Garmin limits the combined FIT developer fields used by Connect IQ data fields. If the device reports a data-field or FIT-field error, disable non-essential saved fields from AlphaHRV or other Connect IQ data fields.

## 2. Record a test activity

After saving the AlphaHRV settings:

1. Record a new activity with AlphaHRV visible on a Garmin data screen.
2. Use the configured chest strap and confirm that AlphaHRV displays changing values during the activity.
3. Save the activity and allow Garmin Connect to synchronise it to Intervals.icu.

There is no need to inspect the FIT file or look for technical stream names. After adding the shared Intervals fields in the next section, the activity should show values for:

- Mean DFA-a1
- Mean AlphaHRV Respiration
- Mean RRa1
- Mean AlphaHRV Artifacts
- DFA-a1 Coverage
- Readiness (Ra), when AlphaHRV produced a readiness result

Readiness may legitimately remain blank on some activities. The other fields should populate when AlphaHRV recorded successfully and the activity is reprocessed after the shared fields are added.

## 3. Add the shared Intervals activity fields

### Recommended: add the shared fields

In Intervals.icu:

1. Open **Settings** and select the relevant sport settings.
2. Open the sport's **Custom Fields / Activity Fields** selector.
3. Search for `DFA` or `AlphaHRV`.
4. Add the following shared fields authored by **Clive King**:

   - Mean DFA-a1
   - Mean AlphaHRV Respiration
   - Mean RRa1
   - Mean AlphaHRV Artifacts
   - DFA-a1 Coverage

5. Search for and add **Readiness (Ra)** authored by **Clive King**.
6. Repeat this for every sport that records AlphaHRV data.

Adding the fields to a sport causes them to be copied onto new activities for that sport.

### Fields supplied by Clive King

Use the shared fields as supplied. Do not create renamed or duplicate versions because the codes are the API contract with Montis.

| Display name | Required code | Type | Unit | Aggregate |
|---|---|---|---|---|
| Mean DFA-a1 | `MeanDFAa1` | Numeric | `a1` or blank | Average |
| Mean AlphaHRV Respiration | `MeanAlphaHRVRespiration` | Numeric | `brpm` | Average |
| Mean RRa1 | `MeanRRa1` | Numeric | `Hz/a1` | Average |
| Mean AlphaHRV Artifacts | `MeanAlphaHRVArtifacts` | Numeric | `%` | Average |
| DFA-a1 Coverage | `DFAa1Coverage` | Numeric | `%` | Average |
| Readiness (Ra) | `ReadinessRa` | Numeric | `%` | Average |

For all six fields:

- Enable **Inline** if the value should appear in the activity summary.
- Enable **Moving average only counts days with a measurement**.
- Use **Average**, not **Sum**, for aggregation across multiple activities on the same day.
- Visibility can be Private, Followers or Public; it does not affect Montis access to the athlete's authorised API data.

The shared **Readiness (Ra)** field reads the `readiness_alphahrv` FIT session field directly. It intentionally has no script.

## 4. Reprocess and validate

### New activities

New activities should calculate the fields automatically when:

- AlphaHRV was active in the Garmin sport profile.
- The required FIT-save options were enabled before the activity started.
- The activity synchronised to Intervals with the developer fields intact.
- The shared activity fields are assigned to that sport.

### Existing activities

After adding a shared field:

1. Open the activity.
2. Choose **Actions → Reprocess file** or the equivalent re-analyse action.
3. Preserve existing intervals when Intervals offers that option.
4. Refresh the activity and check the custom field values.

Reprocessing cannot create AlphaHRV data that was not recorded in the original FIT file.

### Expected API output

A successfully processed activity can contain:

```json
{
  "MeanDFAa1": 0.6980320887,
  "DFAa1Coverage": 97.6608,
  "MeanAlphaHRVArtifacts": 1.7746,
  "MeanAlphaHRVRespiration": 36.0438,
  "MeanRRa1": 1.565,
  "ReadinessRa": 82
}
```

`ReadinessRa` will be absent when AlphaHRV did not produce or save a readiness result.

## 5. Montis availability

### One Day Full

Montis One Day Full returns the complete top-level Intervals activity object. These fields are therefore exposed automatically whenever Intervals provides non-null values.

### Activities Light

The fields are not included in the default Light response, but can be requested explicitly:

```text
MeanDFAa1,
DFAa1Coverage,
MeanAlphaHRVArtifacts,
MeanAlphaHRVRespiration,
MeanRRa1,
ReadinessRa
```

Supported convenient aliases include:

```text
dfa_a1
dfa_a1_coverage
alphahrv_artifacts
alphahrv_respiration
rra1
readiness_ra
```

### Semantic JSON

These fields are not currently added to Montis semantic JSON or used by ESPE, ISDM or ADE. That is a separate modelling and interpretation decision tracked in Montis enhancement issue #58.

## 6. Interpretation limits

- `MeanDFAa1` is a whole-activity descriptive average. It must not be treated as an LT1 measurement, particularly for mixed-intensity sessions.
- `DFAa1Coverage` and `MeanAlphaHRVArtifacts` must accompany DFA-a1 when assessing data quality. Montis has not yet adopted official pass/fail thresholds.
- `MeanAlphaHRVRespiration` is an AlphaHRV estimate and should be treated as supporting context.
- `MeanRRa1` is an experimental/contextual ratio, not a readiness score and not raw RR data.
- `ReadinessRa` is AlphaHRV's activity-start readiness output. It is a supporting observation and is not equivalent to Montis ADE readiness.
- Missing data should remain missing (`null`/absent). Do not replace missing physiological measurements with zero.

## References

- [AlphaHRV in the Garmin Connect IQ Store](https://apps.garmin.com/en-US/apps/1a69b10a-1d31-4afe-a32f-6a579ae20d9f)
- [Intervals.icu computed activity fields](https://forum.intervals.icu/t/computed-activity-fields/25673)
- [AlphaHRV FIT recording explanation](https://forum.intervals.icu/t/alphahrv-update/27239?page=9)
- [AlphaHRV readiness setup and calculation](https://aiendurance.com/blog/real-time-readiness-with-alphahrv-and-ai-endurance)
- [Montis enhancement issue #58](https://github.com/revo2wheels/intervalsicugptcoach-public/issues/58)
