# The Montis coaching platform

Coach your athletes in the Montis App. Each athlete keeps their own Intervals.icu account and shares it with you through a Montis invite link. Montis analyses their training and shows you everything in one place: who needs you this week, what each athlete did against the plan, and what comes next.

**Guides (PDF)**

- [Coaching athletes with Montis.icu](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/docs/Coaching_Athletes.pdf): invite links, accepting an invite, managing your athletes, branding and privacy.
- [The Montis coaching platform](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/docs/Coaching_Platform.pdf): Coach Cockpit, the AI roster review, the Coaching Workflow, email reports, Coach Plans and working as an athlete.

## What you get

| Feature | What it does |
|---|---|
| **Coach Roster** | Lists your athletes. Pick one and the whole app switches to them. |
| **Coach Cockpit** | A weekly overview of all your athletes, with the ones who need you first. For an athlete on a coach plan, it shows how each planned workout went. |
| **Cockpit AI Roster Review** | The AI Coach reviews your whole roster and puts your athletes in priority order. |
| **Coaching Workflow** | One athlete's week in six sections, with a branded email report you can send them. |
| **Session Intensity Lab analysis email** | Send the athlete the AI Coach's analysis of one of their activities. |
| **Coach Plans** | Build a plan once in AI Builder v2, in weeks or up to a race or camp. Assign it to your athletes, or yourself, in their own targets, and undo it if needed. **Events** puts a race, camp or holiday on several calendars at once. |
| **Everything else** | Dashboards, Wellness, Athlete Profile, Workout Builder, AI Builder v2 and the rest, for the athlete you picked. |

## Who can use it

- Coaching needs an active **Montis Subscriber** membership. Athletes use Montis free. See **Membership and AI Allowance**.
- Athletes join with an invite link. See [Coached athletes setup](coached_athletes_setup.md).
- The AI features use the shared Montis AI key that comes with the Subscriber membership, up to its monthly allowance. You can also use your own Gemini key (see **Montis Gemini App Setup**).

## Where the numbers come from

Every number comes from the Montis coaching engine, which reads the athlete's Intervals.icu data. The AI Coach explains those results. It is told to use them as they are and not to recalculate them.

Intervals.icu stays the source of truth. Anything you plan or change for an athlete appears in their Intervals.icu calendar.

## In this guide

1. [Coach Roster and Acting as an Athlete](#coach-roster-and-acting-as-an-athlete)
2. [Coach Cockpit](#coach-cockpit)
3. [Cockpit AI Roster Review](#cockpit-ai-roster-review)
4. [Coaching Workflow and Email Report](#coaching-workflow-and-email-report)
5. [Session Intensity Lab Analysis Email](#session-intensity-lab-analysis-email)
6. [Coach Plans](#coach-plans)

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
2. The top bar shows **Acting as** and the athlete's name, with **Back to me**. On a phone it is a bar under the header.
3. The app loads the athlete's latest reports and opens **Horizon Dashboard** → **Coaching**.

You can also open an athlete from the **Coach Cockpit** by clicking their photo or name.

To go back to your own data, press **Back to me**, or choose **Primary Account** in the roster. The roster marks the athlete you're working on as **Active**.

![Acting as Lena Brandt, with Back to me at the top: her Overview dashboard](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/coaching-platform/acting-as-overview.png)

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
- **The AI Coach** (the chat and the AI Coach panels) can add, change or delete workouts when you ask it to. It asks first: a card shows what will change and whose calendar, with **Confirm** and **Cancel**. Nothing changes until you press **Confirm**.

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
   - **HIGH EXT LOAD**: heat load was high this week. The External Context card has the details.
4. **Next Action** from the engine, and the next event: name, category (for example **RACE_A**), days to go (**T-27**) and readiness.

### Buttons on a row

- **Click the row** to open the athlete's cards (below). The arrow shows whether the row is open.
- **Click the photo or name** to act as that athlete. See **Coach Roster and Acting as an Athlete**.
- **The sparkle button** opens a **Coach Review** of that athlete: the AI Coach reads their cockpit data and gives a decision, the reason, the evidence, a coach action and what to watch next.

### Coach summary

Opening a row starts with three boxes, all from the athlete's Cockpit report:

- **This week's call**: the phase the athlete needs now (for example **Recovery**), **Phase override** when it applies, the ADE score, the engine's guidance in one sentence, and the next action.
- **Load this week**: TSS done against the week's target (the line marks the projected week), the projected total, and TSB, ACWR and CTL now and at the end of the forecast.
- **Watch**: critical (red) and watch (amber) flags in plain words, readiness (HRV, resting HR, sleep, or "no data" with how many days have data), and the next race.

Hovering a row, and the opened athlete, shows a coloured band with an accent edge.

### Plan execution (athletes on a coach plan)

When an athlete has a plan from **Coach Plans** assigned, their row shows it under their name, for example **Winter Base (Adv) v1 · wk 3/12 · 3 of 4 done**. The dot is green when this week's workouts so far are done, amber when one was cut short or missed.

Opening the row shows **Plan execution** above the cards:

- **This week**, day by day: each plan workout with its planned load and time, and how it went. Intervals.icu matches each ride to its planned workout and gives a **compliance** %: **Done** is 80% or more, **Partly** 50–79%, **Missed** under 50% or no ride once the day has passed. Rest days show as **Rest**.
- **Not in the plan**: rides with no planned workout matched to them, with their load and IF.
- **Easy ridden hard**: an easy plan workout ridden at an IF 0.10 or more above its plan.
- **Plan to date** (the last 6 weeks on a longer plan): done against planned load per week, workouts done, **hard sessions** done (a plan workout with 5 minutes or more in Z4 or above), the average compliance of the rides, and the rides not in the plan.
- **Plan check** opens the AI Coach on these figures and the cockpit data: is the athlete on track, what was missed, cut short or added, and what to change in the coming days. The Full Roster AI review gets one plan line per athlete too.
- A plan that starts next week shows **starts Mon 2 Nov** and its first week.
- **Open in Coach Plans** goes to the plan.

All figures come from Intervals.icu and the plan; Montis doesn't estimate any. A missing one shows **---**.

### The athlete's cards

Under **All engine details** (open on a computer, folded on a phone; tap to show or hide):

![Lena Brandt's row opened: the coach summary, then the engine cards](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/coaching-platform/coach-cockpit-athlete.png)

| Card | What it shows |
|---|---|
| **Decision engine** | The engine's guidance for the week, the required phase, the forecast trend and whether a phase override is on. |
| **Flags** | Each flag with its value, time window and the data it's based on. Red is critical, amber is watch. Positive flags are listed under a fold. |
| **Training load** | The week's hours, TSS and distance; CTL, ATL, TSB, ACWR, strain and fatigue trend; and compliance with the weekly target: target and done, projected week, and the gap. |
| **Readiness** | HRV ratio and trend, resting heart rate and its change, sleep score, what it means, and how many days have data (coverage). |
| **Phase alignment** | Required phase, alignment, plan pattern, current state, the last block and the phase streak. |
| **Forecast** | CTL, ATL and TSB at the end of the forecast (14 days), the load trend and fatigue class, and the next action with its reason. |
| **Adaptation Profile** | The current adaptation state and bias, the power-curve profile, and the status of each energy system (for example improving or stable). |
| **Events** | The next target event (category, type, days to go, readiness, form and limiting factors) and the next upcoming events. |
| **External context** | Only when there's data: the dominant stressor, the heat and environmental load index, and the mean climbing rate (VAM). |

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
- You can use your own Gemini key at any time: **Settings & API Key** (the gear on the **AI Coach** card). See **Montis Gemini App Setup**.
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
| **2. Fatigue and Recovery Trends** | CTL, ATL and TSB; ACWR, fatigue trend, Foster strain and monotony, and stress tolerance; the intensity distribution (Seiler week type, Treff polarization index and ZQI, with Treff for the athlete's main sport and for all endurance); the week's daily load; a 14-day fatigue forecast; and ride fatigue resistance. Hover or tap the ⓘ next to a figure for what it means and how it's calculated. |
| **3. Athlete Readiness** | Readiness balance; the engine's decisions and interventions; the decision context and phase alignment; training guidelines and limits; and target events. |
| **4. HRV / Wellness** | HRV (latest, 42-day mean and ratio), resting heart rate, sleep, the watch list and positive markers, and environmental stressors. |
| **5. Weekly Performance Progression** | Adaptation state, power-curve changes, anaerobic repeatability, durability and neural load (WDRM, ISDM and NDLI), lactate thresholds (LT1 and LT2) and the recent training phases. |
| **6. Future Periodisation** | The coming phases with projected hours, TSS, CTL, ATL and TSB. **Change Periodisation** opens AI Builder v2. |

### Send the email report

The email box is at the top right of the Coaching Workflow.

![The email box: the athlete's address, SEND and your commentary](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/coaching-platform/workflow-email-box.png)

1. Check the address. Montis fills in the athlete's email. You can type over it, but only with an address Montis allows (see below).
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
- Montis only sends to your own Intervals.icu email, or to the Intervals.icu email of an athlete you coach, as Montis knows it. Use one address.
- If any address is not allowed, nothing is sent. You see **Failed to send email** with the refused address, and **SEND** turns red and shows **FAILED**.
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

---

## Coach Plans

Build a training plan once in **AI Builder v2**, then assign it to any of your athletes. Each athlete gets the plan in their own power, heart-rate or pace targets, lined up with their own dates, and you can undo it at any time.

### Open it

In the sidebar, open **Coaches** → **Coach Plans**.

The list shows each plan with its **Theme**, **Length**, **Weekly load** and who it is **Assigned** to. **Assign** sends the whole plan to athletes straight from the list. **Open** takes you back into the plan, to change it or to send only some weeks or workouts. On a phone each plan is a card with the same buttons.

![Coach Plans: two plans, with each athlete's version, dates and volume](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/coaching-platform/coach-plans-list.png)

- Plans are saved in Montis for your account, so they show on every device.
- Coach Plans needs an active **Montis Subscriber** membership, like the rest of coaching.

### Build a plan

**New plan** opens AI Builder v2 without an athlete, with a **Plan name** box. The label at the top, next to **Workout intelligence**, reads **Coach plan · *plan name***; an athlete's own builder reads **Athlete · *name*** instead. To go back to an athlete's builder, pick **AI Builder v2** in the sidebar.

You get the same inputs as an athlete's plan: theme, length (weeks or up to a date), weekly load (TSS and hours), sport, growth, strength and the other extras, Montis folders, and **Plan rules**. Inputs that belong to one athlete are left out: target events, fatigue and the what-if.

- **Plan length**: **Weeks**, or **Up to a date** with **Plan starts**, **Target date** and what is on it: **A race (taper)**, **Training camp (arrive fresh)** or **Nothing**. The weeks still show Day 1 to Day 7; the dates only set the length and the default line-up when you assign.
- **Ends with an A race (taper in the last week)** (Weeks only): tick it when the plan should finish with a race. The last week becomes the taper.
- **Plan rules**: write the rules the AI must follow, for example "2 strength sessions a week, never the day before VO2". **+ Rønnestad VO2** adds the VO2 rule described below.
- **Generate coach plan** builds the weeks. They show **Day 1** to **Day 7**, because dates come later, per athlete.
- Every target is written as a **% of threshold** or a zone (**Z1** to **Z7**), never in watts, heart rate or pace. That is what lets one plan fit every athlete.

The plan saves itself to Coach Plans once it has weeks. Until you name it, it is called after its theme and length, for example **Build · 8 weeks**.

#### Generating again

If the plan already has weeks, **Generate coach plan** asks first:

- **Replace "plan name"**: the new weeks replace the old ones in the same plan.
- **Save as a new plan**: the old plan stays as it is, and the new weeks go into a copy.
- **Cancel**.

### Assign it to athletes

Tap **Assign** next to a plan in Coach Plans to send the whole plan. To send only some weeks or workouts, **Open** the plan instead: under the weeks, **Assign chosen weeks to athletes** replaces the usual Commit. Pick the weeks and workouts to send, then tick the athletes. **Me (your name)** is first in the list, so you can follow a plan yourself, with the same checks, **Undo** and **Update**.

1. **Line up the plan**
   - **Week 1 starts on a date**: you choose each athlete's Monday.
   - **Last week ends before the plan's target** (plans made **Up to a date**, and then the default): week 1 starts on the plan's own start for everyone, so the last week ends right before the target. Change the date for an athlete whose camp or race differs.
   - **Last week ends on each athlete's A race**: the last week lines up with their next A race in Intervals.icu. An athlete with no A race starts on the date you choose.
2. **Targets**: by default each athlete gets their **load order** from Intervals.icu (power, heart rate or pace). You can choose one for everyone per sport. "110%" becomes their own watts; "Z2" becomes their own heart-rate or pace zone. An athlete without that threshold is flagged, for example **no FTP set**.
3. **Volume**: 70% to 130% per athlete. It lengthens or shortens the easy parts of each session. Intervals and their recoveries stay as written.
4. **Check each athlete** before you assign:
   - **Their state now**: ACWR (acute to chronic load) and form from their last 90 days.
   - **With this plan**: where ACWR peaks once the plan is added. Above **1.30** the row turns red and suggests a lower volume.
   - **Their calendar**: how many workouts are already on those days. Untick **Replace** to keep them.
5. **Assign** writes the workouts to each athlete's Intervals.icu calendar.

![Assign: you and two athletes ticked, each with their dates, targets and load check](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/coaching-platform/coach-plans-assign.png)

Assigning a plan to an athlete again (for example after **Generate coach plan**) replaces their earlier assignment of it: its future workouts are removed, and Coach Plans shows only the new one.

Rest days are written as notes, never as workouts.

**Double booking safeguard, per athlete.** The same rules as Commit in AI Builder v2: workouts on the plan's days are replaced (unless you untick Replace), days you didn't choose keep what is there, race markers and diary notes are never touched, and days before today are skipped.

### Events: races, camps and holidays for several athletes

The **Events** tab adds one entry to the calendars of the athletes you tick, all at once.

1. **New event**, then pick what it is: **Race A**, **Race B**, **Race C**, **Note** (a training camp, for example), **Holiday**, **Sickness** or **Injury**.
2. Give it a name and dates (a race has one day and a sport), a **colour** and a description. For a camp, include the travel days: start the note on the day the athletes travel (often 1 to 2 days before).
3. For a note, holiday, sickness or injury, choose the **training availability**: **Available to train**, **Limited** or **Unavailable**. With **Limited** you can also set the most training a day (hours) and the sports they can do, as in Intervals.icu. The engine reads it.
4. Tick the athletes (**Me** puts it on your own calendar too) and tap **Add to N calendars**.

![The Events tab: a race, a holiday with limited training, a camp and an A race](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/coaching-platform/coach-plans-events.png)

Each event row lists its athletes, with **Calendar** and **Remove** (takes it off that athlete's calendar only). **Edit** changes it on every athlete's calendar; untick an athlete there to take it off theirs. **Delete event** removes it from every calendar. **Plan up to it** (races and notes) opens a new coach plan **Up to a date** on the event, and when you act as one of those athletes, the event shows as a quick pick in their own **Up to a date**.

### Montis templates

The **Montis templates** tab, next to **My plans**, holds ready-made plans from Montis, such as **Winter Base Building (Adv)**.

- **Import to my plans** adds a copy to My plans as v1, not assigned, named after the template. Open, change, assign and update it like any plan you built.
- Once imported, the template shows **✓ In my plans**. Later changes to the template do not change copies already imported; **Import again** gets the new one as a separate plan.

**For admins.** Under each of your plans in My plans:

- **Share as template** asks for a template name and what it is for (shown to coaches), then shares the plan's weeks, inputs and Plan rules. Your athletes and assignments are not shared.
- **Update template** changes the name or description, and shares your plan's latest version over the old one. To change the weeks, generate your plan again first.
- **Stop sharing** removes it from Montis templates. Copies coaches already imported stay.

### Versions

Each **Generate coach plan** with **Replace** makes the plan its next version: **v1**, **v2**, **v3**. The version shows next to the plan name, with the time it was generated. Changing only the name does not make a new version, and **Save as a new plan** starts again at v1.

Each athlete's line shows which version they have:

- **v3 · current** (green): they have the latest.
- **v1 · old** (amber), with "Plan changed since: now v3": their calendar still has the earlier version. **Update to v3** opens Assign with them ticked and their dates, volume and targets filled in. Assign then replaces their future workouts from the earlier version; past days stay.

Plans and assignments made before versions existed count as v1.

### View and undo

- **View calendar** switches Montis to that athlete and opens their Calendar.
- **Undo for (athlete)** appears straight after assigning, and later as **Undo assignment** in Coach Plans.
- Undo removes only the workouts that assignment wrote that are still in the future. Workouts already done, races, notes and anything else stay. Workouts that the plan replaced are not brought back, and the confirm step says so.

### Change one workout for one athlete

To change a single day for one athlete, change it on their calendar, not in the plan:

1. Open the athlete's **Calendar** (the **Calendar** link on their line in Coach Plans).
2. Tap the workout. The edit window opens with **Builder** and **Library**.
3. Either pick a different workout in **Library** (it loads into Builder), or change the steps in **Builder**.
4. Keep the date and tap **Save changes**. The new workout replaces the old one on that day.

If you close the window with changes not saved, Montis asks first. The plan and your other athletes don't change. The workout still belongs to the assignment, so **Undo** or **Update to vN** later replaces it too.

### The science behind a coach plan

Here is a plan built the Montis way, with the research behind each choice. It is an example, not a rule.

#### Example: 8-week cyclocross build

**Weekly pattern** (weeks 1–3 and 5–7):

| Day | Session | Why |
|---|---|---|
| 1 | Rest or easy spin | Recovery after the weekend |
| 2 | **VO2** (see below) | Hardest session, on fresh legs |
| 3 | Easy endurance (Z2) + **strength** | Strength 3 h or more apart from the ride |
| 4 | Endurance with tempo blocks (Z2, short Z3) | Aerobic base |
| 5 | Easy or rest | Strength never the day before VO2 |
| 6 | **CX skills / race simulation** | Sport-specific work |
| 7 | Long endurance (Z2) + **strength** | Volume |

Week 4 is a lighter week. Week 8 is the taper when the plan ends with an A race.

**VO2 progression**

| Weeks | Session |
|---|---|
| 1–3 | **30/15**: 30 s at 120%, 15 s at 50%, 13 reps. 2 sets in week 1, then 3. 3 min easy between sets. Each set opens with 1.5 min at 120%. |
| 4 | Lighter week: one short 30/15 set, or none |
| 5–7 | **Fast-start 5-min intervals**: 1.5 min at 120%, then 3.5 min at 105%. 4 to 5 of them. |
| 8 | Taper: short, sharp openers only |

The **+ Rønnestad VO2** button adds this rule to **Plan rules**:

> VO2 Rule (Rønnestad): Weeks 1–3, 30/15 (30 s at 120%, 15 s at 50%, 13 reps, 2–3 sets, 3 min easy between), each set opening with 1.5 min at 120%. From week 5, 5-min intervals: 1.5 min at 120%, then 3.5 min at 105%. Strength never the day before VO2.

The **+ Durability** button adds this rule to **Plan rules**:

> Durability Rule: Once a week in loading weeks, one fatigued-intervals session, indoors or outdoors: 60–75 min at 75–85% FTP on the turbo, or a 2–3 h endurance ride outdoors, then straight into either 3x5 min at 105–110% or 2x10 min at 95–100%. Not in recovery or taper weeks, and not the day before VO2.

#### What the research says

- **Short intervals (30/15).** Well-trained cyclists who did short 30 s/15 s intervals twice a week improved more than those doing long intervals at the same effort, over 10 weeks ([Rønnestad 2015](https://pubmed.ncbi.nlm.nih.gov/24382021/)). It held in elite cyclists doing 3 × 13 × 30/15 ([Rønnestad 2020](https://pubmed.ncbi.nlm.nih.gov/31977120/)) and in a one-week block of five sessions ([Rønnestad 2021](https://pubmed.ncbi.nlm.nih.gov/33735833/)).
- **Fast start.** Starting each interval hard and then settling gives more time near VO2max: in cyclists with varied power inside the work intervals ([Bossi 2020](https://pubmed.ncbi.nlm.nih.gov/32244222/)), and in skiers with a fast start ([Rønnestad 2020](https://pubmed.ncbi.nlm.nih.gov/31621643/)) or speed changes ([Rønnestad 2022](https://pubmed.ncbi.nlm.nih.gov/34814113/)).
- **Durability (fatigued intervals).** How well power holds after long or hard work separates riders with the same fresh FTP ([Maunder 2021](https://pubmed.ncbi.nlm.nih.gov/33886100/)). Two hours of heavy riding cut critical power by about 8% and W′ by about 20% ([Clark 2018](https://pubmed.ncbi.nlm.nih.gov/29521722/)), and riders whose training was more polarised kept more of their power when fatigued ([Spragg 2023](https://pubmed.ncbi.nlm.nih.gov/35239466/)). Indoors, 60–75 min at 75–85% is a compressed way to build that fatigue before the efforts.
- **Fuelling.** In 15 trained men riding 4 hours with intervals, 100 g of carbohydrate an hour instead of 60 g left more power for a 15-minute time trial at the end: it fell 6.4% instead of 9.3%, about 9 W ([Mazza 2026](https://pubmed.ncbi.nlm.nih.gov/42841583/), men only, glucose and fructose mix). **+ Fuelling** adds: 90–100 g an hour on rides over 2 hours and durability sessions, built up in training.
- **Easy days easy.** In 30 under-23 professionals over a season, more time below the first threshold went with better 2-minute power after 2,000 kJ, and a more polarised mix with better 12-minute power ([Spragg 2023](https://pubmed.ncbi.nlm.nih.gov/35239466/); associations, not proof). **+ Easy days easy** keeps endurance and recovery rides in Z1–Z2 with no tempo creep.
- **Durability check.** The same study measured fatigued power as the best 5 and 12 minutes after 2,000 kJ. **+ Durability check** adds one such effort every 4–6 weeks, so fatigued power can be tracked; it also gives Intervals.icu the fatigued power curves that the engine's fatigue resistance needs.
- **Strength.** Heavy strength training adds to cycling performance ([Rønnestad & Mujika 2014](https://pubmed.ncbi.nlm.nih.gov/23914932/)). Endurance work doesn't hold back maximal strength or muscle size, but explosive strength gains are smaller when both are done in the same session; 3 h or more apart avoids that ([Schumann 2022](https://pubmed.ncbi.nlm.nih.gov/34757594/)).
- **Mostly easy (80/20).** Elite endurance athletes do most of their sessions easy and a small share hard ([Seiler 2006](https://pubmed.ncbi.nlm.nih.gov/16430681/)). A polarised mix beat threshold, high-volume and high-intensity-only training in a 9-week study ([Stöggl 2014](https://www.frontiersin.org/articles/10.3389/fphys.2014.00033/full)).

#### Good to know

- The studies set intensity by effort (as hard as can be held for the session), not by % FTP. The **120%**, **105%** and **50%** are Montis numbers that put those efforts into a plan. Watch how your athletes cope and adjust.
- No study has tested a fast start inside a 30/15 set. The plan combines two separate findings.
- No study has tested the durability session itself (a pre-load then hard intervals). It combines the findings above. It isn't a warm-up: a short hard effort before intervals helps only after about 9 minutes or more of recovery ([Bailey 2009](https://pubmed.ncbi.nlm.nih.gov/19797685/)); the pre-load here is meant to tire the athlete first.
- The skier studies are about skiing; the cycling evidence for a fast start is Bossi 2020.

