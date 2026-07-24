# Lactate Integration & Personalised Zone 2

Montis uses optional blood lactate measurements to refine your aerobic training zone, particularly Zone 2 around LT1. Lactate is not required. When usable lactate and power data are available, Montis can personalise the zone; otherwise it safely falls back to FTP-based zones.

### Add the LT1 Fields in Intervals.icu
* Open **Athlete → Settings** using the gear icon.
* Scroll to **Custom Fields**.
![Custom Fields overview](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/lactate-lt1/scroll-to-custom-fields.png)
* Use the search icon and enter `HRTLNDLT1`.
* Add both custom fields:
  * **HRTLNDLT1** — LT1 lactate concentration in mmol/L.
  * **HRTLNDLT1P** — power recorded with the LT1 sample in watts.

![Custom Fields overview](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/lactate-lt1/custom-fields-overview.png)

![Search for the LT1 fields](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/lactate-lt1/search-lt1-fields.png)

* Open each field with the edit icon and confirm its settings.
* Click **OK**, tick the checkbox to activate the field, and then click **Close** to save.

![LT1 field settings](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/lactate-lt1/lt1-field-settings.png)

![LT1 power field settings](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/lactate-lt1/lt1-power-field-settings.png)

![Enabled activity fields](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/lactate-lt1/enabled-activity-fields.png)

### Enter Your LT1 and Power Values
* In **Athlete Settings → Custom Fields**, locate `HRTLNDLT1`.
* Enter your latest LT1 value in mmol/L, for example `2.0`.
* Enter the matching LT1 power in `HRTLNDLT1P`, for example `195` watts.
* Click **Save**.

A typical LT1 value is approximately **1.5-2.5 mmol/L**. When no tested value is available, the guide uses **2.0 mmol/L** as the standard aerobic-threshold starting point.

### Apply the Fields to Activities
* Open a recent activity containing power data.
* Scroll to the bottom and open **Custom**.
* Enable `HRTLNDLT1` and `HRTLNDLT1P` for the activity and future activities.
* Refresh the page. The values should then populate automatically on new activities.
* When values do not appear, reload the activity from its source or temporarily edit an interval to force the activity fields to refresh.

![Activity Custom menu](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/lactate-lt1/activity-custom-menu.png)

### Keep the Values Updated
Update `HRTLNDLT1` and `HRTLNDLT1P` in **Athlete Settings → Custom Fields** whenever you complete a new lactate or endurance test.

The updated values flow into:
* Future activities.
* The Montis reporting pipeline.
* Personalised endurance-zone calibration.

FTP acts as the LT2 anchor, while `HRTLNDLT1` and `HRTLNDLT1P` define the aerobic base used to shape your personalised Zone 2 range.

### Field Summary

| Field | Example | Unit | Purpose |
|---|---:|---|---|
| VO2Max | 66 | - | Current aerobic capacity |
| HRTLNDLT1 | 2.0 | mmol/L | Aerobic threshold, approximately the top of easy endurance |
| HRTLNDLT1P | 195 | W | Power paired with the LT1 lactate value |
| FTP | 300 | W | Functional Threshold Power, used as the approximate LT2 anchor |

### How Montis Interprets the Data
Montis summarises the available lactate observations and checks whether usable power pairs exist.

The guide's example contains one lactate point:
* **Average lactate:** 2.0 mmol/L.
* **Latest lactate:** 2.0 mmol/L.
* **Range:** 2.0-2.0 mmol/L.
* **Samples detected:** 1.
* **Correlation with power:** `r = 0.0`.
* **Lactate-power model:** FTP-based fallback.

With only one profile-default sample, there is no measurable lactate-power relationship. The system therefore retains FTP-based zones rather than treating the value as a measured lactate curve.

### Threshold Calibration Example

| Threshold | Example value | Description |
|---|---:|---|
| LT1 | 2.0 mmol/L | Aerobic threshold where lactate first rises above baseline; approximately 200 W in the example |
| LT2 | 4.0 mmol/L | Anaerobic threshold near maximal steady state; approximately 300 W in the example |
| Calibration source | FTP-based default | Standard defaults are used because no strong lactate-power relationship is available |
| Confidence | 0% | The example has no usable power correlation |

### Interpretation
* The example indicates Z2-dominant aerobic-base training intended to improve LT1.
* The example fat-oxidation efficiency value of `0.59` sits close to the stated fat/carbohydrate crossover area around LT1.
* The example shows no threshold overload or excessive glycolytic work.

### Coach Recommendations
* **Refine LT1:** Ride steadily for 30-40 minutes at approximately 200-220 W and monitor heart-rate stability and drift below 5%.
* **Refine LT2:** Complete short threshold intervals around 300 W and observe the heart-rate response. A rapid rise may indicate a slightly lower true LT2.
* **Improve confidence:** Add more paired lactate and power observations. The system can then replace FTP defaults with athlete-specific calibration when the data is sufficiently consistent.

### Bottom Line
* Lactate data is optional.
* `HRTLNDLT1` stores the lactate value.
* `HRTLNDLT1P` stores the paired power value.
* FTP remains the LT2 anchor.
* A single or unpaired value is summarised but does not provide a reliable lactate-power model.
* Multiple consistent lactate-power samples allow more precise Zone 2 calibration.
