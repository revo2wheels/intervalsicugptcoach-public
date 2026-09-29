# The Montis coaching platform

Coach your athletes in the Montis App. Each athlete keeps their own Intervals.icu account and shares it with you through a Montis invite link. Montis analyses their training and shows you everything in one place: who needs you this week, what each athlete did against the plan, and what comes next.

**Guides (PDF)**

- [Coaching athletes with Montis.icu](https://github.com/revo2wheels/intervalsicugptcoach-public/blob/main/docs/Coaching_Athletes.pdf): invite links, accepting an invite, managing your athletes, branding and privacy.
- [The Montis coaching platform](https://github.com/revo2wheels/intervalsicugptcoach-public/blob/main/docs/Coaching_Platform.pdf): Coach Cockpit, the AI roster review, the Coaching Workflow, email reports and working as an athlete.

## What you get

| Feature | What it does |
|---|---|
| **Coach Roster** | Lists your athletes. Pick one and the whole app switches to them. |
| **Coach Cockpit** | A weekly overview of all your athletes, with the ones who need you first. |
| **Cockpit AI Roster Review** | The AI Coach reviews your whole roster and puts your athletes in priority order. |
| **Coaching Workflow** | One athlete's week in six sections, with a branded email report you can send them. |
| **Session Intensity Lab analysis email** | Send the athlete the AI Coach's analysis of one of their activities. |
| **Everything else** | Dashboards, Wellness, Athlete Profile, Workout Builder, AI Builder v2 and the rest, for the athlete you picked. |

## Who can use it

- Coaching needs an active **Montis Subscriber** membership. Athletes use Montis free.
- Athletes join with an invite link. See [Coached athletes setup](coached_athletes_setup.md).
- The AI features use the shared Montis AI key that comes with the Subscriber membership, up to its monthly allowance. You can also use your own Gemini key.

## Where the numbers come from

Every number comes from the Montis coaching engine, which reads the athlete's Intervals.icu data. The AI Coach explains those results. It is told to use them as they are and not to recalculate them.

Intervals.icu stays the source of truth. Anything you plan or change for an athlete appears in their Intervals.icu calendar.

## In this guide

1. [Coach Roster and Acting as an Athlete](#coach-roster-and-acting-as-an-athlete)
2. [Coach Cockpit](#coach-cockpit)
3. [Cockpit AI Roster Review](#cockpit-ai-roster-review)
4. [Coaching Workflow and Email Report](#coaching-workflow-and-email-report)
5. [Session Intensity Lab Analysis Email](#session-intensity-lab-analysis-email)

Every screenshot uses made-up athletes and a made-up coach, Anna Weber Coaching. The AI answers shown are examples. The same pages are in the Montis App under **Help** → **Guide** → **Coaching Athletes**.

---

## Coach Roster and Acting as an Athlete

The **Coach Roster** lists the athletes who share their training with you. Pick one and the app switches to that athlete: you see their data, and the planning tools write to their calendar.

### Open the roster

1. In the sidebar, open **Coaches** → **Coach Roster**.
2. The **Coaching Roster** panel lists your **Managed Athletes**. Search by name or ID in **Search roster...**.
3. The refresh icon loads the list again.

- **Primary Account** takes you back to your own data.
- **Invite athletes** opens the Montis hub at [https://montis.icu/app](https://montis.icu/app), where you create invite links. See [Coached athletes setup](coached_athletes_setup.md).

![The Coaching Roster panel with five athletes](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/coaching-platform/coach-roster.png)

The **Coaches** menu is for Montis Subscribers. Without a Subscriber membership it shows a coffee cup instead, with a link to the membership.

### Act as an athlete

1. Click an athlete in the roster. The roster closes.
2. The header shows **Acting as:** and the athlete's name.
3. The app loads the athlete's latest reports and opens **Horizon Dashboard** → **Coaching**.

You can also open an athlete from the **Coach Cockpit** by clicking their photo or name.

To go back to your own data, press the **X** on the **Acting as** badge, or choose **Primary Account** in the roster. On a phone the badge is hidden; the roster marks the athlete you're working on as **Active**.

![Acting as Lena Brandt: her Overview dashboard](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/coaching-platform/acting-as-overview.png)

### What switches to the athlete

| Where | What you see |
|---|---|
| **Horizon Dashboard** | **Coaching**, **Overview**, **Micro**, **Meso**, **Macro**, **Calendar**, **Readiness** and **Sandbox**, all for the athlete |
| **Athlete Profile** | Their biometrics, physiology and sport settings |
| **Wellness** | Their Physiology Drill-Down: HRV, sleep, resting heart rate and more |
| **Skills** | **Workout Builder**, **Workout Library**, **AI Builder v2**, **Session Intensity Lab** and **Performance Progression** |
| **History** | Their saved history |
| **AI Coach Chat** | A separate conversation for each athlete. The AI Coach knows you are their coach. |

#### The dashboard tabs

- **Coaching**: the athlete's week, with the email report. See **Coaching Workflow and Email Report**.
- **Overview**: this week at a glance: sessions done, weekly load against the target, and the wellness vitals.
- **Micro**: the current seven days in detail.
- **Meso**: roughly the last three months (the season).
- **Macro**: the last year.
- **Calendar**: planned workouts ahead. Drag a workout to move it; click it to edit or delete it.
- **Readiness**: how ready the athlete is for a chosen event.
- **Sandbox**: what-if simulations.

#### The ATHLETE / COACH switch

The switch sits above the dashboard tabs. **COACH** adds AI Coach panels to the tabs (for example **Microcycle AI Coach**, **Forecast AI Coach** and **Readiness AI Coach**) and switches some views to a coach layout. It doesn't change which athlete you're working on.

### Changing the athlete's calendar

While you act as an athlete, these actions write straight to their Intervals.icu calendar:

- **Workout Builder**: **COMMIT TO CALENDAR** and **SAVE CHANGES**. **DELETE WORKOUT**, then **CONFIRM DELETE**, removes a workout.
- **Calendar** tab: dragging a workout moves it at once.
- **AI Coach Chat**: **Add to Calendar** on a suggested workout.
- **AI Builder v2**: committing a plan first removes the existing workouts on the dates of the weeks you selected, then writes the new plan.
- **Coaching Workflow**: **Delete Target Event**, then **Confirm Delete**, removes a target event.
- **The AI Coach** (the chat and the AI Coach panels) can add, change or delete workouts, and send the athlete a message in Intervals.icu chat, when you ask it to. It doesn't ask you to confirm first, so say exactly what you want.

Changes show in the athlete's Intervals.icu straight away.

---

## Coach Cockpit

The **Coach Cockpit** puts all your athletes' weeks on one page, with the athletes who need attention first.

### Open it

In the sidebar, open **Coaches** → **Coach Cockpit**.

The header shows your logo and website (if you set them in the hub), the number of connected athletes, and when the overview was last updated.

- The cockpit shows up to 25 athletes.
- Montis keeps the overview in your browser for 24 hours. The refresh button fetches a new one.
- **AI COACH** opens the AI review of your whole roster. See **Cockpit AI Roster Review**.

![The Coach Cockpit with five athletes](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/coaching-platform/coach-cockpit.png)

### The order

Athletes with data come first. Then the order is: most critical flags, most watch flags, weakest physiology, soonest event. Athletes without recent data come last, marked **INSUFFICIENT DATA**, and can't be opened.

### Reading a row

1. **Sport · FTP · W/kg**.
2. The **physiology state** (for example **STABLE**, **WATCH** or **STRAINED**) in green, amber or red. Then the **ADE** score and label (Adaptive Decision Engine), the load state (for example **LOAD_ACCEPTING**), and the phase the athlete needs now with **ALIGNED** (green) or **MISALIGNED** (red) against their plan.
3. **Critical** and **Watch** flag counts, **Upcoming** events and **TSB** (form).
   - **PHASE OVERRIDE**: the athlete needs to taper or recover now, so that phase takes priority over the usual guidance. The Decision Engine card shows the required phase.
   - **HIGH EXT LOAD**: environmental load, such as heat or climbing, was high this week. The External Context card has the details.
4. **Next Action** from the engine, and the next event: name, category (for example **RACE_A**), days to go (**T-27**) and readiness.

### Buttons on a row

- **Click the row** to open the athlete's cards (below). The arrow shows whether the row is open.
- **Click the photo or name** to act as that athlete. See **Coach Roster and Acting as an Athlete**.
- **The sparkle button** opens a **Coach Review** of that athlete: the AI Coach reads their cockpit data and gives a decision, the reason, the evidence, a coach action and what to watch next.

### The athlete's cards

![Lena Brandt's row opened, showing the nine cards](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/coaching-platform/coach-cockpit-athlete.png)

| Card | What it shows |
|---|---|
| **Tier 5 · Decision Engine** (Adaptive Decision Engine) | The engine's guidance for the week, the required phase, the forecast trend and whether a phase override is on. |
| **Coach Flags** (Critical & Watch Flags) | Each flag with its value, time window and the data it's based on. Red is critical, amber is watch. Positive flags are listed under a fold. |
| **Tier 1 · Load State** (Training Load) | The week's hours, TSS and distance; CTL, ATL, TSB, ACWR, strain and fatigue trend; and compliance with the weekly target: target and done, projected week, and the gap. |
| **Tier 2 · Autonomic Readiness** (Physiology Reserve) | HRV ratio and trend, resting heart rate and its change, sleep score, what it means, and how many days have data (coverage). |
| **Tier 4 · System Progression** (Phase Alignment) | Required phase, alignment, plan pattern, current state, the last block and the phase streak. |
| **Tier 3 · Cognitive Fitness** (Performance Forecast) | CTL, ATL and TSB at the end of the forecast (14 days), the load trend and fatigue class, and the next action with its reason. |
| **Adaptation Profile** | The current adaptation state and bias, the power-curve profile, and the status of each energy system (for example improving or stable). |
| **Target Events & Schedule** | The next target event (category, type, days to go, readiness, form and limiting factors) and the next upcoming events. |
| **External Context** (Environmental Load) | Only when there's data: the dominant stressor, the heat and environmental load index over 7 days, and the mean climbing rate (VAM). |

### Terms

- **CTL**: fitness, the 42-day training load.
- **ATL**: fatigue, the 7-day training load.
- **TSB**: form, CTL minus ATL.
- **ACWR**: acute to chronic workload ratio, this week's load against the longer-term load.
- **TSS**: training stress score.
- **ADE**: the Adaptive Decision Engine, which turns the athlete's data into the week's decision.

---

## Cockpit AI Roster Review

The AI Coach reviews your whole roster from the cockpit data and tells you who needs you first.

### Run it

1. Open **Coaches** → **Coach Cockpit**.
2. Press **AI COACH** in the cockpit header. The **Roster AI Coach Review** panel opens and the review starts by itself.

![The Roster AI Coach Review with the athletes in priority order](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/coaching-platform/cockpit-roster-review.png)

### What you get

- For each athlete: **Decision**, **Reason**, **Evidence**, **Coach action** and **Watch next**.
- Your athletes in priority order.
- Key facts from the answer as chips. Click a chip to ask about it.

The AI Coach uses only the cockpit data. It is told not to recalculate readiness, risk, compliance, phase or training load. It answers in the app's language.

The example in the picture is illustrative. The review is written fresh from your athletes' data each time.

### Keep going

- Ask follow-up questions in **Message your Montis Coach...**. While it answers, the AI Coach can look up more of your athletes' data with Montis tools.
- The copy button copies the answer. The retry button asks again. The bin clears the conversation.
- The model badge shows which Gemini model answered. It follows the **Lite**, **Flash** or **Adv** mode on the **AI Coach** card.
- The conversation stays in this browser for 24 hours.

### AI key and usage

- Subscribers use the shared Montis AI key, up to the monthly allowance of their membership. When the allowance runs out, the app asks for your own Gemini key.
- You can use your own Gemini key at any time: **Settings & API Key** (the gear on the **AI Coach** card).
- The **Adv** model needs your own pay-as-you-go Gemini key.

---

## Coaching Workflow and Email Report

The **Coaching Workflow** puts one athlete's week on one page, from what they did against the plan to what comes next. You can email it to the athlete as a report with your branding.

### Open it

1. Act as the athlete. See **Coach Roster and Acting as an Athlete**.
2. Open **Horizon Dashboard** → **Coaching**. Subscribers land here when they pick an athlete.

The header shows the athlete, the report period, your logo and website, and the athlete's FTP, W′ (anaerobic capacity), lactate threshold heart rate and weight. **Sync Workflow** reloads the athlete's latest weekly and wellness reports.

![The Coaching Workflow for Lena Brandt](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/coaching-platform/coaching-workflow.png)

### The six sections

| Section | What it shows |
|---|---|
| **1. Training Execution vs Prescription** | Hours, TSS and distance; compliance with the weekly target (green from 85% to 115%); remaining and projected TSS; the planned weeks; completed workouts, each with **Analyse** (opens the Session Intensity Lab); and planned sessions. |
| **2. Fatigue and Recovery Trends** | CTL, ATL and TSB; ACWR, fatigue trend, Foster strain and monotony, polarisation, ZQI and stress tolerance; metabolic indicators; the week's daily load; and a 14-day fatigue forecast. |
| **3. Athlete Readiness** | Readiness balance; the engine's decisions and interventions; the decision context and phase alignment; training guidelines and limits; and target events. |
| **4. HRV / Wellness** | HRV (latest, 42-day mean and ratio), resting heart rate, sleep, the watch list and positive markers, and environmental stressors. |
| **5. Weekly Performance Progression** | Adaptation state, power-curve changes, anaerobic repeatability, durability and neural load (WDRM, ISDM and NDLI), lactate thresholds (LT1 and LT2), the three-zone intensity split and the recent training phases. |
| **6. Future Periodisation** | The coming phases with projected hours, TSS, CTL, ATL and TSB. **Change Periodisation** opens AI Builder v2. |

### Send the email report

The email box is at the top right of the Coaching Workflow.

![The email box: the athlete's address, SEND and your commentary](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/coaching-platform/workflow-email-box.png)

1. Check the address. Montis fills in the athlete's email, and you can change it.
2. Add a comment if you like. It goes at the top of the email as **Coach Commentary**.
3. Press **SEND**.

The athlete gets the **Coaching Workflow Report**:

- A header in your brand colour, with your logo, name and website. Without a brand colour it's Montis green.
- The period and the athlete, then FTP and W′.
- Your **Coach Commentary**.
- Sections 1 to 6, then **Coaching Verdict & Guidance**.

![The Coaching Workflow Report email](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/coaching-platform/workflow-email-report.png)

- You get a copy (CC).
- The subject is **MONTIS COACHING WORKFLOW REPORT - [ATHLETE]**.
- The email comes from noreply@montis.icu, so ask athletes to reply to you directly.
- Montis only sends to your own Intervals.icu email, or to the Intervals.icu email of an athlete you coach, as Montis knows it. Any other address is refused.
- The email always uses your current branding. Set your logo, website and brand colour in the hub at [https://montis.icu/app](https://montis.icu/app) (**Coaching** tab, **Your coach branding**).

---

## Session Intensity Lab Analysis Email

Ask the AI Coach to analyse one of the athlete's activities in the **Session Intensity Lab**, then send the analysis to the athlete as an email with your branding.

### Analyse an activity

1. Act as the athlete. See **Coach Roster and Acting as an Athlete**.
2. Open an activity: press **Analyse** next to a completed workout in the **Coaching Workflow**, or open **Skills** → **Session Intensity Lab** and pick one from the list.
3. Open the **AI Coach** tab (the last tab).
4. Choose a suggestion such as **ANALYSE ACTIVITY**, or type your question. Here the AI Coach doesn't start by itself.

![The Session Intensity Lab's AI Coach tab with an analysis](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/coaching-platform/sil-ai-coach.png)

The AI Coach sees the activity's thresholds, power, heart rate and load; the power, heart-rate and pace curves; segments, intervals and repeatability; and the zone histograms.

The other tabs show the activity itself: **Metrics**, **Intensity** (zones), **Route Lab** (the map), **Power Curve**, **HR Curve**, **Pace Curve**, **Segments** (Strava activities only) and **Intervals**.

### Email the analysis

1. Under the answer you want to send, press **Email**. This only shows while you act as an athlete.
2. **Email AI Coach Response to [athlete]** opens with:
   - **Athlete email address**, filled in for you.
   - **Subject**, for example **Montis AI Coach Analysis - Sweet Spot 3x12**.
   - **Message body (editable before send)**: the AI Coach's answer. Add your own note or change anything.
3. Press **Send Email**.

![The email composer with the athlete's address, subject and message](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/coaching-platform/sil-email-composer.png)

The athlete gets an email with your branded header, the activity name, the athlete, and a **Coach Analysis & Notes** box with the message you sent.

![The analysis email as the athlete sees it](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/coaching-platform/sil-email.png)

- Unlike the workflow report, you don't get a copy.
- The same address rules apply: your own Intervals.icu email, or the Intervals.icu email of an athlete you coach.
- The email comes from noreply@montis.icu, so ask athletes to reply to you directly.

