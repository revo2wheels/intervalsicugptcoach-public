# Coached Athletes Setup

Montis allows a coach to access explicitly shared athletes through the `Coached_Athletes` folder in Intervals.icu. Access requires both private folder sharing and authentication through the Montis app.

### Create the Required Folder
* Open **Library** in Intervals.icu.
* Create a folder named exactly:

```text
Coached_Athletes
```

* The name is case-sensitive and must match exactly.

![Create the Coached_Athletes folder](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/coached-athletes/create-coached-athletes-folder.png)

### Set the Folder to Private
* Open the folder sharing settings.
* Set **Visibility** to **Private**.
* Do not use a public or generally shared folder.

![Set the folder visibility to Private](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/coached-athletes/share-folder-private.png)

### Share the Folder with Coached Athletes
* Click **Add Coached** and select **All coached athletes**, or add athletes individually.
* Confirm the required athlete is listed.
* Set the athlete permission to **Viewer**.

### Athlete Connection
Each coached athlete must connect their own Intervals.icu account to Montis:

1. Open [https://montis.icu/app](https://montis.icu/app).
2. Click **Connect Intervals**.
3. Authenticate and approve access.
4. The window can then be closed.

This connection allows Montis to access that athlete's data for the coach, in the same controlled relationship already established in Intervals.icu.

### Coach Connection
The coach must also connect through Montis:

1. Open [https://montis.icu/app](https://montis.icu/app).
2. Click **Connect Intervals**.
3. Authenticate and approve access.
4. Open the **Coaching Access** section.

The coach will see connected and disconnected coached athletes, including their name and athlete ID.

![Montis Coaching Access list](https://raw.githubusercontent.com/revo2wheels/intervalsicugptcoach-public/main/assets/user-guides/coached-athletes/coaching-access-list.png)

### Security Model
Coaching access requires both conditions:

#### Folder Rule
* The athlete is shared through `Coached_Athletes`.
* The folder visibility is **Private**.

#### Authentication Rule
* The athlete has connected their Intervals.icu account through the Montis app.

Folder sharing alone is not enough.

### If an Athlete Disconnects
* The athlete is removed immediately from Montis Coaching Access.
* Remaining in the Intervals.icu folder does not preserve access after disconnection.

### Troubleshooting
Check these items when an athlete does not appear:

* The folder name is exactly `Coached_Athletes`.
* The folder visibility is **Private**.
* The athlete is shared in that folder.
* The athlete connected successfully at [https://montis.icu/app](https://montis.icu/app).
* The coach also connected successfully through the app.

### Important
* Only authenticated athletes appear.
* Only athletes explicitly shared by the coach are visible.
* Athletes cannot see one another through this setup.
* Coached Athlete tools are available through supported Montis access channels, including ChatGPT, Claude MCP, and the Gemini app.
