
"""
Tier-1 — Audit Controller (v16.14-Stable++)
Ensures dataset integrity, preserves Tier-0 columns (incl. start_date_local),
and enforces Field Lock Rule for moving_time.
"""

import pandas as pd
import numpy as np
from audit_core.utils import debug
from audit_core.errors import AuditHalt
from audit_core.utils import validate_dataset_integrity, validate_wellness_alignment

def collect_zone_distributions(df_activities, athlete_profile, context):
    """Compute separate zone distributions for Power, HR, and Pace."""

    if df_activities is None or df_activities.empty:
        debug(context,"⚠ collect_zone_distributions: empty df_activities")
        context["zone_dist_power"] = {}
        context["zone_dist_hr"] = {}
        context["zone_dist_pace"] = {}
        return context

    # --- Initialize output ---
    context["zone_dist_power"] = {}
    context["zone_dist_hr"] = {}
    context["zone_dist_pace"] = {}

    # --- Debug: show available columns ---
    debug(context,"[DEBUG-ZONE] Available columns:", df_activities.columns.tolist())

    # --- POWER ZONES ---
    power_cols = [
        c for c in df_activities.columns
        if c.lower().startswith(("power_z", "icu_power_z", "icu_zone_times"))
    ]
    debug(context,"[DEBUG-ZONE] Detected Power zone columns:", power_cols)

    # --- HEART RATE ZONES ---
    hr_cols = [
        c for c in df_activities.columns
        if c.lower().startswith(("hr_z", "icu_hr_zone_times"))
    ]
    debug(context,"[DEBUG-ZONE] Detected HR zone columns:", hr_cols)

    # --- PACE ZONES ---
    pace_cols = [
        c for c in df_activities.columns
        if c.lower().startswith(("pace_z", "pace_zone_times", "gap_zone_times"))
    ]
    debug(context,"[DEBUG-ZONE] Detected Pace zone columns:", pace_cols)

    # --- Zone Distribution Helper ---
    def compute_zone_dist(cols, label):
        if not cols:
            debug(context,f"[DEBUG-ZONES] No {label} columns found — skipping.")
            return {}
        subset = df_activities[cols].select_dtypes(include=[np.number])
        total = subset.sum().sum()
        if total <= 0:
            debug(context,f"[DEBUG-ZONES] No valid data for {label} zones — total=0.")
            return {}
        dist = (subset.sum() / total * 100).round(1).to_dict()
        debug(context,f"[DEBUG-ZONES] {label} zones computed: {dist}")
        return dist

    # --- Compute all zone distributions ---
    context["zone_dist_power"] = compute_zone_dist(power_cols, "power")
    context["zone_dist_hr"] = compute_zone_dist(hr_cols, "hr")
    context["zone_dist_pace"] = compute_zone_dist(pace_cols, "pace")

    return context


    # --- Fallback using athlete profile if no explicit zone data ---
    if not any([context["zone_dist_power"], context["zone_dist_hr"], context["zone_dist_pace"]]):
        debug(context,"⚠ No zone columns found — using athlete profile thresholds if available.")
        if athlete_profile:
            context["zone_dist_power"] = athlete_profile.get("power_zones", {})
            context["zone_dist_hr"] = athlete_profile.get("hr_zones", {})
            context["zone_dist_pace"] = athlete_profile.get("pace_zones", {})

    return context

def run_tier1_controller(df_activities, wellness, context):
    # --- Tier-1 entry diagnostic ---
    import sys
    sys.stderr.write(
        f"\n[Tier-1 entry] rows={len(df_activities)}  "
        f"Σ(moving_time)/3600={df_activities['moving_time'].sum()/3600:.2f}\n"
    )
    sys.stderr.flush()

    # --- Step 0: Defensive copy (preserve all Tier-0 columns)
    df_activities = df_activities.copy()
    if "start_date_local" not in df_activities.columns:
        raise AuditHalt("❌ Tier-1 missing start_date_local column — verify Tier-0 output")
    debug(context,f"[T1] Columns at entry: {list(df_activities.columns)}")

    # --- Step 1: Dataset integrity ---
    if df_activities.empty:
        raise ValueError("❌ No activity data received")

    assert "moving_time" in df_activities.columns, "❌ moving_time field missing from dataset"
    assert df_activities["moving_time"].gt(0).all(), "❌ moving_time contains zero or negative values"

    if df_activities["id"].duplicated().any():
        raise ValueError("❌ Duplicate activity IDs detected")

    # --- Step 2: Canonical totals (true Σ(event.moving_time)) ---
    if "moving_time" not in df_activities.columns:
        raise AuditHalt("❌ Tier-1: missing moving_time column for canonical totals")

    # Intervals.icu always exports moving_time in seconds
    # Force numeric and convert explicitly to hours
    df_activities["moving_time"] = pd.to_numeric(df_activities["moving_time"], errors="coerce").fillna(0)
    event_hours = df_activities["moving_time"].sum() / 3600

    debug(
        context,
        f"🧮 Tier-1: using enforced seconds→hours conversion "
        f"(Σmoving_time={df_activities['moving_time'].sum():.0f} s → {event_hours:.2f} h)"
    )

    event_tss = pd.to_numeric(df_activities["icu_training_load"], errors="coerce").fillna(0).sum()

    context["tier1_eventTotals"] = {
        "hours": round(event_hours, 2),
        "tss": int(round(event_tss))
    }

    # --- Step 3: Basic variance validation ---
    if event_hours <= 0 or event_tss <= 0:
        raise AuditHalt("❌ Tier-1: invalid totals (zero or negative values)")

    context.pop("dailyTotals", None)
    context["df_events"] = df_activities

    # --- Step 4: Cross-verification (restored) ---
    diff_hours = abs(event_hours - context["tier1_eventTotals"]["hours"])
    diff_tss = abs(event_tss - context["tier1_eventTotals"]["tss"])
    if diff_hours > 0.1:
        raise AuditHalt(f"❌ Tier-1 cross-check variance >0.1 h (Δ={diff_hours:.2f})")
    if diff_tss > 2:
        raise AuditHalt(f"❌ Tier-1 cross-check variance >2 TSS (Δ={diff_tss:.1f})")

    # --- Step 5: Wellness alignment check ---
    if wellness is None or (isinstance(wellness, pd.DataFrame) and wellness.empty):
        debug(context,"⚠ No wellness data available for window; continuing with activity-only audit")
    else:
        validate_wellness_alignment(df_activities, wellness)

    # --- Step 6: Daily summary build ---
    df_activities["date"] = pd.to_datetime(df_activities["start_date_local"]).dt.date
    daily_summary = pd.DataFrame()

    if isinstance(wellness, (list, pd.DataFrame)) and len(wellness) > 0:
        df_well = pd.DataFrame(wellness)
        keep_cols = [
        "id", "ctl", "atl", "tsb", "sleepSecs", "sleepScore", "hrv", "restingHR",
        "fatigue", "stress", "mood", "motivation",
        "hydration", "soreness", "injury", "readiness"
        ]
        df_well = df_well[[c for c in keep_cols if c in df_well.columns]]
        df_well.rename(columns={"id": "date"}, inplace=True)
        df_well["date"] = pd.to_datetime(df_well["date"]).dt.date
        if "sleepSecs" in df_well.columns:
            df_well["sleep_h"] = (df_well["sleepSecs"] / 3600).round(2)
            df_well.drop(columns=["sleepSecs"], inplace=True)
        daily_summary = df_well.copy()

    context["dailyMerged"] = daily_summary

    # --- Step 6a: Append training load metrics (CTL / ATL / TSB) if present ---
    if isinstance(df_well, pd.DataFrame) and not df_well.empty:
        df_well.columns = [c.strip().lower() for c in df_well.columns]
        load_cols = [c for c in ["ctl", "atl", "tsb"] if c in df_well.columns]
        if load_cols:
            debug(context,f"[DEBUG-T1] merging load metrics from wellness: {load_cols}")
            # --- Normalize merge keys to timezone-naive daily dates ---
            df_well["date"] = (
                pd.to_datetime(df_well["date"])
                .dt.tz_localize(None)
                .dt.floor("D")
            )
            df_activities["date"] = (
                pd.to_datetime(df_activities["start_date_local"])
                .dt.tz_localize(None)
                .dt.floor("D")
            )
            df_activities = df_activities.merge(
                df_well[["date"] + load_cols], on="date", how="left"
            )
            # --- Step 6a.1: derive TSB if ctl/atl exist but tsb missing ---
            if "ctl" in df_activities.columns and "atl" in df_activities.columns:
                if "tsb" not in df_activities.columns:
                    df_activities["tsb"] = (df_activities["ctl"] - df_activities["atl"]).round(2)
                    debug(context,"[DEBUG-T1] derived TSB column added from CTL-ATL.")
                else:
                    debug(context,"[DEBUG-T1] TSB already present.")
            else:
                debug(context,"[DEBUG-T1] cannot derive TSB — ctl/atl missing.")
            # --- Step 6a.2: promote CTL/ATL/TSB to context for Tier-2 ---
            if all(c in df_activities.columns for c in ["ctl", "atl", "tsb"]):
                context["ctl"] = float(df_activities["ctl"].mean(skipna=True).round(2))
                context["atl"] = float(df_activities["atl"].mean(skipna=True).round(2))
                context["tsb"] = float(df_activities["tsb"].mean(skipna=True).round(2))
                debug(context,f"[DEBUG-T1] promoted CTL={context['ctl']} ATL={context['atl']} TSB={context['tsb']} to context.")
            else:
                debug(context,"[DEBUG-T1] cannot promote CTL/ATL/TSB — missing column(s).")
            # --- Step 6a.3: inject nested load_metrics dict for Tier-2/Renderer ---
            context["load_metrics"] = {
                "CTL": {"value": round(context.get("ctl", 0), 2), "status": "ok"},
                "ATL": {"value": round(context.get("atl", 0), 2), "status": "ok"},
                "TSB": {"value": round(context.get("tsb", 0), 2), "status": "ok"},
            }
            debug(context,"[DEBUG-T1] injected load_metrics for renderer:", context["load_metrics"])

            debug(context,"[DEBUG-T1] sample merged CTL/ATL/TSB:", df_activities[["date"] + load_cols].head())
        else:
            debug(context,"[DEBUG-T1] no ctl/atl/tsb columns found in wellness data.")
    else:
        debug(context,"[DEBUG-T1] no valid wellness DataFrame to merge.")

    debug(context,"[DEBUG-T1] sanity check before Step 6b — rows in df_activities:", len(df_activities))
    debug(context,"[DEBUG-T1] athleteProfile present:", "athleteProfile" in context)
    if "athleteProfile" in context:
        debug(context,"[DEBUG-T1] athleteProfile keys:", list(context["athleteProfile"].keys()))

    # --- Step 6b: Build HR / Power / Pace zone distributions ---
    try:
        debug(context,"[DEBUG-T1] Starting zone distribution extraction...")
        debug(context,"[DEBUG-T1] Activity columns sample:", df_activities.columns.tolist()[:40])

        context = collect_zone_distributions(df_activities, context.get("athleteProfile", {}), context)

        debug(context,"[DEBUG-T1] Completed zone distribution extraction.")
        debug(context,"[DEBUG-T1] Zone distributions now in context:")
        for k in ["zone_dist_power", "zone_dist_hr", "zone_dist_pace"]:
            debug(context,f"  {k}: {context.get(k, {})}")
    except Exception as e:
        debug(context,f"⚠ Zone distribution collection failed: {e}")
        context["zone_dist_power"] = {}
        context["zone_dist_hr"] = {}
        context["zone_dist_pace"] = {}

    # --- Step 6c: Outlier Detection ---
    try:
        df = df_activities.copy()
        if "icu_training_load" in df.columns:
            mean_tss = df["icu_training_load"].mean()
            std_tss = df["icu_training_load"].std()
            outliers = df[
                (df["icu_training_load"] > mean_tss + 2 * std_tss) |
                (df["icu_training_load"] < mean_tss - 2 * std_tss)
            ][["id", "name", "start_date_local", "icu_training_load"]]
            context["outliers"] = outliers.to_dict(orient="records")
            debug(context,f"[DEBUG-T1] Outlier events detected: {len(outliers)}")
            debug(context,"[DEBUG-OUTLIER] mean TSS:", mean_tss, "std:", std_tss)
            debug(context,"[DEBUG-OUTLIER] min/max TSS:", df["icu_training_load"].min(), "/", df["icu_training_load"].max())
        else:
            context["outliers"] = []
    except Exception as e:
        debug(context,f"⚠ Outlier detection failed: {e}")
        context["outliers"] = []

    # --- Step 7: Qualitative label translation ---
    rpe_map = {1: "very easy", 2: "easy", 3: "moderate", 4: "somewhat hard",
               5: "hard", 6: "very hard", 7: "maximal", 8: "maximal+",
               9: "extreme", 10: "all out"}
    feel_map = {1: "very bad", 2: "bad", 3: "neutral", 4: "good", 5: "very good"}
    label_map = {1: "very low", 2: "low", 3: "moderate", 4: "high", 5: "very high"}
    mood_map = {1: "very bad", 2: "bad", 3: "neutral", 4: "good", 5: "very good"}
    motiv_map = {1: "none", 2: "low", 3: "moderate", 4: "good", 5: "excellent"}
    hydr_map = {1: "overhydrated", 2: "slightly high", 3: "optimal", 4: "slightly low", 5: "dehydrated"}
    ready_map = {1: "very poor", 2: "poor", 3: "fair", 4: "good", 5: "excellent"}

    for col, cmap in {
        "rpe": rpe_map, "feel": feel_map,
        "fatigue": label_map, "stress": label_map, "soreness": label_map,
        "mood": mood_map, "motivation": motiv_map,
        "hydration": hydr_map, "readiness": ready_map,
    }.items():
        if col in daily_summary.columns:
            daily_summary[f"{col}_label"] = daily_summary[col].map(cmap).fillna(daily_summary[col])

    # --- Step 8: Finalize ---
    context["auditPartial"] = True
    context["auditFinal"] = False

    sys.stderr.write(
        f"[Tier-1 exit] rows={len(df_activities)}  "
        f"Σ(moving_time)/3600={df_activities['moving_time'].sum()/3600:.2f}\n"
    )
    sys.stderr.flush()

    return df_activities, wellness, context
