# Run the Montis coaching engine on your own computer

You can run the same coaching engine that powers Montis on your own computer, on your own Intervals.icu data. It produces the weekly, season, wellness, summary and data-quality reports as JSON files.

In this mode the engine talks only to Intervals.icu, with your own API key. Nothing is sent to Montis, and no Montis account or key is needed.

## 1. Install Python

You need Python 3.11 or newer.

- **Windows:** download it from [python.org](https://www.python.org/downloads/windows/) and run the installer. On the first screen, tick **Add python.exe to PATH**.
- **Mac:** download it from [python.org](https://www.python.org/downloads/macos/), or run `brew install python`.
- **Linux:** use your package manager, for example `sudo apt install python3 python3-venv`.

## 2. Get the code

```bash
git clone https://github.com/revo2wheels/intervalsicugptcoach-public.git
cd intervalsicugptcoach-public
```

No git? On GitHub, use **Code → Download ZIP**, unzip it and open a terminal in that folder.

## 3. Install what the engine needs

This creates a private Python environment in the folder, so nothing is installed system-wide.

**Windows (PowerShell):**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell refuses to run `Activate.ps1`, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then try again.

**Mac and Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Next time, you only need to activate the environment again (the second line).

## 4. Add your Intervals.icu API key

1. In Intervals.icu, open **Settings → Developer Settings**.
2. Copy your **API key**, or generate one if there isn't one yet.
3. Set it in the same terminal window you run the engine from:

**Windows (PowerShell):**

```powershell
$env:ICU_API_KEY = "your-api-key"
```

**Mac and Linux:**

```bash
export ICU_API_KEY="your-api-key"
```

The key gives read and write access to your Intervals.icu account, so keep it private. Don't paste it into files you share or commit. The engine only reads.

If you have your own Intervals.icu OAuth app, you can set `ICU_OAUTH` to an access token instead. When both are set, `ICU_OAUTH` is used.

## 5. Run a report

```bash
python report.py --range weekly --direct
```

| Report | Command |
|---|---|
| Weekly (the last 7 days, ending today) | `python report.py --range weekly --direct` |
| Season | `python report.py --range season --direct` |
| Wellness (42 days) | `python report.py --range wellness --direct` |
| Summary | `python report.py --range summary --direct` |
| Data quality check | `python report.py --range data_quality --direct` |

To report on a past week, add `--start YYYY-MM-DD`. The week runs 7 days from that date. For a summary, give both `--start` and `--end`.

Each run writes a JSON file to the `reports` folder, for example `reports/report_weekly_direct_intervals_semantic.json`. The engine opens the file when it's done. To stop that, set `OPEN_REPORT` to `0` the same way you set the API key.

## What the engine reads

It reads your Intervals.icu profile, activities, wellness records, power curves and planned events for the next 14 days. A weekly report reads about 90 days of activities, and a season report reads more. It only reads; it never changes anything in Intervals.icu.

## Intervals.icu API limits

Intervals.icu limits how often a personal API key can call its API. In October 2026 the limits were 5,000 requests a day (reset at midnight UTC) and 2,500 in any 15 minutes, plus 10 requests a second from one IP address. The current figures are in the [API access post](https://forum.intervals.icu/t/api-access-to-intervals-icu/609) on the Intervals.icu forum.

A report makes about 9 requests, one after another, so normal use stays far below the limits.

- Run one report at a time. Don't run reports in a loop or from several terminals at once.
- Other scripts and apps that use the same API key count towards the same limits.
- If you go over, Intervals.icu answers `429 Too Many Requests`. The engine tries twice more straight away, then usually stops without saving a report. If only the power curves or planned events are refused, the report is saved without them.

## If something goes wrong

| Message | What to do |
|---|---|
| `No Intervals.icu credentials` | Set `ICU_API_KEY` in the same terminal window, then run again. |
| `401` or `403` from intervals.icu | The key is wrong or was regenerated. Copy it again from Settings → Developer Settings. |
| `429` or `Too Many Requests` from intervals.icu | You've hit an [Intervals.icu API limit](#intervalsicu-api-limits). Wait a few minutes, or until after midnight UTC if you used the daily limit, then run one report at a time. |
| `No activity data found for this period` | There are no activities in that window. Try `--start` with a week that has activities. |
| `ModuleNotFoundError` | The environment isn't active. Run the activate line from step 3 again. |
| `--direct runs everything on your computer…` | Leave out `--prefetch`, `--staging`, `--gpt`, `--debug` and `--strava-test`. Those options use Montis's own servers. |

## Other modes

Without `--direct`, `report.py` uses the Montis hosted service. Those modes are for Montis maintainers only.
