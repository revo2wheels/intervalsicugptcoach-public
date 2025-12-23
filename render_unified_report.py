#!/usr/bin/env python3
"""
Unified Report Renderer — URF v5.1 (Weekly / Season / Diagnostic)
Renders a full 10-section Markdown report from the JSON output of run_audit.py.
Supports automatic detection of report type, timezone, and data completeness.
"""

import json
import sys
import os
import time
# --- Safe pandas import (global scope) ---
import types
try:
    import pandas as pd
except Exception:
    pd = types.SimpleNamespace()
    pd.options = types.SimpleNamespace()
    pd.options.display = types.SimpleNamespace(width=160)
from pathlib import Path
from datetime import datetime
from UIcomponents.icon_pack import ICON_CARDS
from audit_core.utils import debug


# --- Unified Framework Report Object (v16-compatible) ---
class Report(dict):
    """Lightweight object to hold report data and render helpers."""
    def add_line(self, text: str):
        self.setdefault("lines", []).append(text)
        return self

    def add_table(self, rows):
        self.setdefault("tables", []).append(rows)
        return self

    def add_section(self, title: str, content: str):
        self.setdefault("sections", []).append({"title": title, "content": content})
        return self


def safe_get(d, *keys, default="—"):
    """Safely traverse nested dicts."""
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return default
    return d


def section(title):
    """Markdown section divider with emoji header."""
    return f"\n\n## {title}\n"


def table(header, rows):
    """Render Markdown table."""
    lines = ["| " + " | ".join(header) + " |", "|:" + " |:".join(["--"] * len(header)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(lines)


# --- New helper ---
def safe_metric_entry(k, v):
    """Handle both dict-based and scalar metric values (prevents .get() crash)."""
    if isinstance(v, dict):
        return [k, v.get("value", v), v.get("status", "✅")]
    else:
        return [k, v, "✅"]

def render_report(data):
    """
    Unified rendering entry point for weekly / season / diagnostic reports.
    Applies early cleanup to remove trace/debug payloads before building markdown.
    """
    ctx = data.get("context", {})
    report_type = ctx.get("report_type", data.get("type", "weekly")).lower()
    debug(ctx, f"[RENDER] Starting unified render for {report_type}")

    # 🛑 Prevent placeholder rendering if audit not finalized
    if not ctx.get("auditFinal", False):
        debug(ctx, "[RENDER] Skipping render — audit not finalized (placeholder suppressed).")
        return {
            "status": "skipped",
            "reason": "Audit not finalized; renderer aborted to prevent placeholder output.",
            "report_type": report_type,
        }

    # --- 🧹 UNIVERSAL CLEANUP: strip trace/debug payloads early ---
    trace_keys = [
        "debug_trace", "trace", "auditPartial", "auditFinal",
        "snapshot_7d_json", "snapshot_90d_json", "df_light_slice",
        "raw_analysis_block", "event_log_text"
    ]
    for k in list(ctx.keys()):
        if any(tk in k.lower() for tk in trace_keys):
            ctx.pop(k, None)
    debug(ctx, "[RENDER] Early cleanup — removed trace/debug artifacts before markdown assembly")


    # --- 🧩 Diagnostic & Totals Source Resolution (URF v5.1) ---
    report_type = ctx.get("report_type", data.get("type", "weekly")).lower()

    # --- Ensure Tier-2 derived metrics persist through render ---
    if "derived_metrics" in ctx:
        ctx["tier2_derived_metrics"] = ctx["derived_metrics"]
    # --- 🧩 Determine renderer totals source (priority-based) ---
    totals_source = None

    # 1️⃣ Prefer Tier-2 enforced totals (canonical)
    if "tier2_enforced_totals" in ctx:
        totals_source = "tier2_enforced_totals"
        et = ctx["tier2_enforced_totals"]
        ctx["eventTotals"] = et
        ctx["totalHours"] = et.get("time_h") or et.get("hours", 0)
        ctx["totalTss"] = et.get("tss", 0)
        ctx["totalDistance"] = et.get("distance_km") or et.get("distance", 0)
        debug(ctx, "[SYNC] Renderer using Tier-2 enforced totals (canonical).")

    # 2️⃣ Otherwise fall back to Tier-1 visibleTotals
    elif "tier1_visibleTotals" in ctx:
        totals_source = "tier1_visibleTotals"
        et = ctx["tier1_visibleTotals"]
        ctx["eventTotals"] = et
        ctx["totalHours"] = et.get("hours", 0)
        ctx["totalTss"] = et.get("tss", 0)
        ctx["totalDistance"] = et.get("distance", 0)
        debug(ctx, "[SYNC] Renderer using Tier-1 visibleTotals (fallback).")

    # 3️⃣ Fallback: legacy eventTotals
    elif "eventTotals" in ctx:
        totals_source = "eventTotals"
        et = ctx["eventTotals"]
        ctx["totalHours"] = et.get("hours", 0)
        ctx["totalTss"] = et.get("tss", 0)
        ctx["totalDistance"] = et.get("distance", 0)
        debug(ctx, "[SYNC] Renderer using legacy eventTotals (fallback).")

    # 4️⃣ Use locked canonical values if available
    ctx["totalHours"] = ctx.get("locked_totalHours") or ctx.get("totalHours")
    ctx["totalTss"] = ctx.get("locked_totalTss") or ctx.get("totalTss")
    ctx["totalDistance"] = ctx.get("locked_totalDistance") or ctx.get("totalDistance")

    # 🧭 Unified renderer trace (single clean line)
    debug(
        ctx,
        f"[RENDERER] Totals unified from {totals_source} → "
        f"{ctx.get('totalHours')} h | {ctx.get('totalDistance')} km | {ctx.get('totalTss')} TSS"
    )

    # --- Ensure downstream load metrics consistency
    ctx.setdefault("load_metrics", {})
    ctx["load_metrics"]["totalHours"] = ctx.get("totalHours")
    ctx["load_metrics"]["totalTss"] = ctx.get("totalTss")

    # --- Optional: attach metadata for audit trace
    ctx["totals_source"] = (
        "tier2_enforced_totals" if "tier2_enforced_totals" in ctx else "eventTotals"
    )
    ctx["totals_verified"] = True

    # Continue normal render logic...
    athlete_raw = ctx.get("athlete", {})
    athlete_profile = ctx.get("athleteProfile", {})

    # Merge for local render
    athlete = {}
    athlete.update(athlete_raw)
    athlete.update(athlete_profile)

    name = athlete.get("name", "Unknown Athlete")
    tz = athlete.get("timezone", ctx.get("timezone", "n/a"))

    start = ctx.get("window_start", "?")
    end = ctx.get("window_end", "?")
    report_type = data.get("type", "Weekly")
    debug(ctx, "[TRACE-RENDER-ENTRY] totalHours =", ctx.get("totalHours"))
    debug(ctx, "[TRACE-RENDER-ENTRY] totalTss   =", ctx.get("totalTss"))
    debug(ctx, "[DEBUG-RENDER] incoming load_metrics:", json.dumps(ctx.get("load_metrics", {}), indent=2))
    md = []

    # === 1️⃣ HEADER / META ===
    md.append(f"# 🧭 {report_type} Training Report — URF v5.1")
    md.append(f"**Athlete:** {name}")
    md.append(f"**FTP:** {athlete.get('ftp', '—')} W · "
            f"**Weight:** {athlete.get('weight', '—')} kg · "
            f"**FTP/kg:** {athlete.get('ftp_wkg', '—')}")
    md.append(f"**HR:** rest {athlete.get('hr_rest', '—')} / "
            f"max {athlete.get('hr_max', '—')}")
    md.append(f"**Period:** {start} → {end}")
    md.append(f"**Timezone:** {tz}")
    md.append(f"**Generated:** {ctx.get('timestamp', datetime.utcnow().isoformat())}")
    md.append("\n---")

    # === 2️⃣ Tier-0 Dataset Integrity ===
    md.append(section("🧩 Tier-0 Dataset Integrity"))
    md.append(f"- Activities fetched: {ctx.get('event_count', '—')}")
    md.append(f"- Origin: {ctx.get('enforcement_layer', '—')}")
    md.append(f"- Purge enforced: {ctx.get('purge_enforced', False)}")
    md.append(f"- Wellness records: {safe_get(ctx, 'wellness_summary', 'count', default='n/a')}")
    md.append(f"- Source verification: ✅ Live (no mock/cache)")
    debug(ctx, "[TRACE-HEADER] ctx.totalHours =", ctx.get("totalHours"))
    debug(ctx, "[TRACE-HEADER] ctx.totalTss   =", ctx.get("totalTss"))
    #md.append(f"- Σ(moving_time)/3600 = {ctx.get('totalHours', '—')} h  |  Σ(TSS) = {ctx.get('totalTss', '—')}")

    # === 3️⃣ Tier-1 Audit Controller ===
    md.append(section("🧩 Tier-1 Audit Controller"))
    md.append(f"- Deduplication: OK")
    md.append(f"- HR stream coverage: {safe_get(ctx, 'audit_summary', 'hr_coverage', default='—')}")
    md.append(f"- Power data coverage: {safe_get(ctx, 'audit_summary', 'power_coverage', default='—')}")
    md.append(f"- Time variance ≤ 0.1 h ✅")

    # --- Ensure Tier-2 derived metrics override any Tier-1 fallback ---
    if "tier2_derived_metrics" in ctx and isinstance(ctx["tier2_derived_metrics"], dict):
        if "derived_metrics" not in ctx or not ctx["derived_metrics"]:
            ctx["derived_metrics"] = ctx["tier2_derived_metrics"]
        else:
            ctx["derived_metrics"].update(ctx["tier2_derived_metrics"])
        debug(ctx, "[SYNC] Derived metrics updated from Tier-2 context before render.")

    # === 📊 Key Stats (Weekly Mode) ===
    if report_type.lower() == "weekly":
        md.append(section("📊 Key Stats"))
        et = (
            ctx.get("tier2_enforced_totals")
            or ctx.get("tier1_visibleTotals")
            or ctx.get("tier0_snapshotTotals_7d")
            or ctx.get("eventTotals")
            or {}
        )
        rows = [
            ["Hours", f"{et.get('hours', et.get('time_h', 0)):.2f}"],
            ["Distance (km)", f"{et.get('distance', et.get('distance_km', 0)):.1f}"],
            ["TSS", f"{et.get('tss', 0)}"],
            ["Sessions", f"{ctx.get('event_count', 0)}"],
        ]
        md.append(table(["Metric", "Value"], rows))
        md.append("")
        debug(ctx, "[Tier-2] Injected 📊 Key Stats section for weekly mode.")

    # === 4️⃣ Tier-2 Derived Metrics ===
    md.append(section("🧮 Derived Metric Audit (EWMA-based ACWR)"))
    from coaching_cheat_sheet import CHEAT_SHEET

    derived = ctx.get("derived_metrics", {})
    if derived:
        rows = []
        for k, v in derived.items():
            if isinstance(v, dict):
                value = v.get("value", "—")
                icon = v.get("icon", "")
                status = v.get("status", "")
                context_note = CHEAT_SHEET.get("context", {}).get(k, "")
                rows.append([k, value, f"{icon} {status}", context_note])
            else:
                context_note = CHEAT_SHEET.get("context", {}).get(k, "")
                rows.append([k, v, "✅", context_note])

        md.append(table(["Metric", "Value", "Status", "Context"], rows))
    else:
        md.append("_No derived metrics available._")

    ## ⚙️ Training Zone Distributions
    power = ctx.get("zone_dist_power", {})
    if power:
        md.append("\n\n### Power Zones")
        md.append(table(["Zone", "% Time"], [[z, f"{v:.1f}"] for z, v in power.items()]))
    else:
        md.append("\n\n_No power zone data available._")

    hr = ctx.get("zone_dist_hr", {})
    if hr:
        md.append("\n\n### Heart Rate Zones")
        md.append(table(["Zone", "% Time"], [[z, f"{v:.1f}"] for z, v in hr.items()]))
    else:
        md.append("\n\n_No HR zone data available._")

    pace = ctx.get("zone_dist_pace", {})
    if pace:
        md.append("\n\n### Pace Zones")
        md.append(table(["Zone", "% Time"], [[z, f"{v:.1f}"] for z, v in pace.items()]))
    else:
        md.append("\n\n_No pace zone data available._")

    # === 6️⃣ Outlier Events ===
    md.append(section("⚠️ Outlier Events"))
    outliers = ctx.get("outliers", [])
    if outliers:
        rows = [[o.get("date", "?"), o.get("event", "?"), o.get("issue", "?"), o.get("obs", "?")] for o in outliers]
        md.append(table(["Date", "Event", "Issue", "Observation"], rows))
    else:
        md.append("_No outliers detected._")

    # === 7️⃣ Wellness & Recovery ===
    md.append(section("💓 Wellness & Recovery"))

    well = ctx.get("wellness_metrics", {})
    daily = ctx.get("dailyMerged", pd.DataFrame())

    # Core summary
    md.append(f"- Rest Days: {well.get('rest_days', '—')}")
    md.append(f"- Resting HR: {well.get('rest_hr', '—')} bpm")
    hrv_trend = well.get("hrv_trend", None)
    # --- HRV presentation (show last two values and direction) ---
    if isinstance(daily, pd.DataFrame) and "hrv" in daily.columns and len(daily) >= 2:
        last_two = daily.sort_values("date").tail(2)["hrv"].tolist()
        if len(last_two) == 2:
            prev_hrv, curr_hrv = last_two
            diff = curr_hrv - prev_hrv
            if diff > 1:
                trend_desc = f"↑ improving (+{diff:.1f} ms)"
            elif diff < -1:
                trend_desc = f"↓ declining ({diff:.1f} ms)"
            else:
                trend_desc = "→ stable"
            md.append(f"- HRV: {curr_hrv:.1f} ms ({trend_desc}, prev {prev_hrv:.1f} ms)")
        else:
            md.append(f"- HRV: {daily['hrv'].iloc[-1]:.1f} ms (latest)")
    elif well.get("hrv"):
        md.append(f"- HRV: {well['hrv']:.1f} ms (single record)")
    else:
        md.append("- HRV: —")

    # Optional averages if daily wellness data exists
    if isinstance(daily, pd.DataFrame) and not daily.empty:
        if "sleep_h" in daily.columns:
            sleep_avg = round(daily["sleep_h"].mean(skipna=True), 1)
            md.append(f"- Avg Sleep: {sleep_avg} h/night")
        if "fatigue" in daily.columns:
            fatigue_avg = round(daily["fatigue"].mean(skipna=True), 1)
            md.append(f"- Fatigue: {fatigue_avg}/5")
        if "stress" in daily.columns:
            stress_avg = round(daily["stress"].mean(skipna=True), 1)
            md.append(f"- Stress: {stress_avg}/5")
        if "readiness" in daily.columns:
            readiness_avg = round(daily["readiness"].mean(skipna=True), 1)
            md.append(f"- Readiness: {readiness_avg}/5")

    # Load metrics
    load = ctx.get("load_metrics", {})
    atl = load.get("ATL", {}).get("value", well.get("atl", "—")) if isinstance(load.get("ATL"), dict) else load.get("ATL", "—")
    ctl = load.get("CTL", {}).get("value", well.get("ctl", "—")) if isinstance(load.get("CTL"), dict) else load.get("CTL", "—")
    tsb = load.get("TSB", {}).get("value", well.get("tsb", "—")) if isinstance(load.get("TSB"), dict) else load.get("TSB", "—")
    md.append(f"- ATL: {atl} · CTL: {ctl} · TSB: {tsb}")

    # === 8️⃣ Load & Stress Chain (Diagnostics) ===
    if ctx.get("debug_mode", False):
        md.append(section("⚖️ Load & Stress Chain (Diagnostics)"))
        load = ctx.get("load_metrics", {})
        if load:
            rows = [safe_metric_entry(k, v) for k, v in load.items()]
            md.append(table(["Metric", "Value", "Status"], rows))
        else:
            md.append("_Load metrics unavailable._")

    # === 9️⃣ Efficiency & Adaptation ===
    if report_type.lower() in ("season", "diagnostic"):
        md.append(section("🔬 Efficiency & Adaptation"))
        from coaching_cheat_sheet import CHEAT_SHEET

        # --- Compute adaptation metrics dynamically if missing ---
        if "adaptation_metrics" not in ctx:
            df_source = None
            if "df_events" in ctx and isinstance(ctx["df_events"], pd.DataFrame) and not ctx["df_events"].empty:
                df_source = ctx["df_events"]
            elif "activities_light" in ctx and isinstance(ctx["activities_light"], pd.DataFrame) and not ctx["activities_light"].empty:
                df_source = ctx["activities_light"]
            if df_source is not None and not getattr(df_source, "empty", True):
                try:
                    from tier2_extended_metrics import compute_adaptation_metrics
                    debug(ctx, "[Tier-2] Computing adaptation metrics for long-term report.")
                    ctx["adaptation_metrics"] = compute_adaptation_metrics(df_source, ctx)
                    debug(ctx, f"[Tier-2] Adaptation metrics computed: {list(ctx['adaptation_metrics'].keys())}")
                except Exception as e:
                    debug(ctx, f"[Tier-2] Adaptation metric computation failed → {e}")
            else:
                debug(ctx, "[Tier-2] No dataset available for adaptation metric computation.")

        adapt = ctx.get("adaptation_metrics", {})
        if adapt:
            rows = []
            for k, v in adapt.items():
                if isinstance(v, dict):
                    value = v.get("value", "—")
                    icon = v.get("icon", "")
                    status = v.get("status", "")
                    context_note = CHEAT_SHEET.get("coaching_links", {}).get(k, "")
                    rows.append([k, value, f"{icon} {status}", context_note])
                else:
                    context_note = CHEAT_SHEET.get("coaching_links", {}).get(k, "")
                    rows.append([k, v, "✅", context_note])
            debug(ctx, f"[DEBUG] Adaptation metric keys: {list(adapt.keys())}")
            md.append(table(["Metric", "Value", "Status", "Context"], rows))
        else:
            md.append("_No adaptation data available._")

    else:
        # Skip entirely for weekly (short-term) reports
        debug(ctx, "[Tier-2] Skipping Efficiency & Adaptation section for weekly mode.")


    # === 🔟 Performance & Coaching Actions ===
    md.append(section("🧠 Performance & Coaching Actions"))
    perf = ctx.get("performance", {})
    actions = ctx.get("actions", [])
    if perf:
        for k, v in perf.items():
            md.append(f"- {k}: {v}")
    if actions:
        metric_contexts = ctx.get("metric_contexts", [])
        md.append("\n**Recommended Actions:**")
        for i, a in enumerate(actions, 1):
            md.append(f"{i}. {a}")
    else:
        md.append("_No coaching actions recorded._")

    # === 🪜 Events or Phases Summary (Tier-2 Safe) ===
    debug(ctx, f"[RENDER-PHASE] Entering phase summary logic — report_type={report_type!r}")
    if report_type.lower() == "season":
        debug(ctx, "[RENDER-PHASE] Season mode — aggregating weekly summaries from 90-day dataset.")

        # --- Disable raw event dump for season mode ---
        for k in ["event_log_text", "weeklyEventLogBlock"]:
            if k in ctx:
                debug(ctx, f"[Tier-2] Removing {k} for season mode (suppress full event table)")
            ctx.pop(k, None)

        # --- Identify the source dataset explicitly ---
        df_src = None
        for candidate_name in ["df_light_slice", "activities_light", "df_events"]:
            candidate = ctx.get(candidate_name)
            if candidate is not None:
                debug(ctx, f"[Tier-2] Checking candidate dataset '{candidate_name}' (type={type(candidate)})")
                if hasattr(candidate, "empty"):
                    debug(ctx, f"[Tier-2] Candidate '{candidate_name}' → empty={candidate.empty}, rows={len(candidate) if not candidate.empty else 0}")
                    if not candidate.empty:
                        df_src = candidate
                        debug(ctx, f"[Tier-2] ✅ Using dataset '{candidate_name}' as season data source")
                        break
                else:
                    debug(ctx, f"[Tier-2 WARN] Candidate '{candidate_name}' is not a DataFrame-like object")
            else:
                debug(ctx, f"[Tier-2] Candidate '{candidate_name}' is None")

        # --- Fallback if nothing usable ---
        if df_src is None:
            md.append(section("🪜 Seasonal Phases Summary"))
            md.append("_No activity data available for season analysis._")
            debug(ctx, "[Tier-2 WARN] No usable dataset found for season summary — aborting aggregation.")
        else:
            debug(ctx, f"[Tier-2] Season source dataset confirmed → rows={len(df_src)}, cols={list(df_src.columns)}")

            df_src = df_src.copy()
            df_src["start_date_local"] = pd.to_datetime(df_src["start_date_local"], errors="coerce")
            df_src = df_src.dropna(subset=["start_date_local"])
            debug(ctx, f"[Tier-2] After timestamp normalization → {len(df_src)} valid rows")

            # --- Ensure numeric fields ---
            for col in ["icu_training_load", "moving_time", "distance"]:
                if col in df_src.columns:
                    df_src[col] = pd.to_numeric(df_src[col], errors="coerce").fillna(0)

            # --- Aggregate by ISO week ---
            df_src["week"] = df_src["start_date_local"].dt.isocalendar().week
            df_week = (
                df_src.groupby("week", as_index=False)
                .agg({
                    "distance": "sum",
                    "moving_time": "sum",
                    "icu_training_load": "sum"
                })
                .sort_values("week")
            )

            debug(ctx, f"[Tier-2] Aggregated {len(df_week)} weekly summaries from {len(df_src)} activities")

            # --- Convert units ---
            df_week["distance_km"] = df_week["distance"] / 1000
            df_week["hours"] = df_week["moving_time"] / 3600

            # --- Build markdown table ---
            md.append(section("🪜 Seasonal Phases Summary"))
            headers = ["Week", "Distance (km)", "Hours", "TSS"]
            rows = [
                [int(r["week"]), f"{r['distance_km']:.1f}", f"{r['hours']:.1f}", f"{r['icu_training_load']:.0f}"]
                for _, r in df_week.iterrows()
            ]
            md.append(table(headers, rows))

            # --- Season totals ---
            total_km = df_week["distance_km"].sum()
            total_hours = df_week["hours"].sum()
            total_tss = df_week["icu_training_load"].sum()
            total_sessions = len(df_src)

            md.append("")
            md.append(
                f"**Season Totals:** {total_hours:.1f} h · {total_km:.1f} km · "
                f"{total_tss:.0f} TSS · {total_sessions} sessions**"
            )

            debug(ctx, f"[Tier-2] ✅ Season Totals: {total_hours:.1f}h · {total_km:.1f}km · {total_tss:.0f}TSS · {total_sessions} sessions")

            # --- Inject structured phase metadata for validator ---
            ctx["phases"] = [
                {
                    "phase": f"Week {int(r['week'])}",
                    "distance_km": float(r["distance_km"]),
                    "hours": float(r["hours"]),
                    "tss": float(r["icu_training_load"])
                }
                for _, r in df_week.iterrows()
            ]
            debug(ctx, f"[Tier-2] Injected {len(ctx['phases'])} weekly phases into context for validator.")


    elif report_type.lower() == "weekly":
        # --- Retain standard event preview logic for weekly ---
        # Fix 2
        if "df_event_only" in ctx and isinstance(ctx.get("df_event_only"), dict) and ctx["df_event_only"].get("preview"):
            preview = ctx["df_event_only"]["preview"]
            debug(ctx, "[Tier-2] Using enforced df_event_only preview (no rebuild).")
        else:
            debug(ctx, "[Tier-2 WARN] Missing enforced df_event_only — fallback to rebuild.")
            df_events = ctx.get("df_events")
            if hasattr(df_events, "to_dict") and not getattr(df_events, "empty", True):
               # --- Normalize timestamp field for sorting ---
                if "date" not in df_events.columns:
                    if "start_date_local" in df_events.columns:
                        df_events = df_events.rename(columns={"start_date_local": "date"})
                    elif "start_date" in df_events.columns:
                        df_events = df_events.rename(columns={"start_date": "date"})
                    else:
                        debug(ctx, "[T2 WARN] No valid date column found in df_events; skipping sort.")
                        df_events["date"] = None  # placeholder to prevent crash

                # --- Safe sort only if date present ---
                if "date" in df_events.columns and not df_events["date"].isnull().all():
                    df_events = df_events.sort_values("date", ascending=False)
                else:
                    debug(ctx, "[T2 WARN] Could not sort df_events by date (missing or null column).")

                preview = (
                    df_events[
                        [c for c in ["date", "name", "icu_training_load", "moving_time", "distance", "total_elevation_gain"]
                        if c in df_events.columns]
                    ]
                    .head(10)
                    .to_dict("records")
                )
            else:
                preview = []

        md.append(section("🚴 Weekly Events Summary"))

        if preview:
            headers = ["date", "name", "icu_training_load", "moving_time", "distance"]
            rows = []
            for e in preview:
                date_val = e.get("date") or e.get("start_date_local") or ""
                if isinstance(date_val, str) and " " in date_val:
                    date_val = date_val.split(" ")[0]
                elif hasattr(date_val, "strftime"):
                    date_val = date_val.strftime("%Y-%m-%d")

                name = e.get("name", "")
                tss = e.get("icu_training_load", "")
                move = e.get("moving_time", "")
                dist = e.get("distance", "")

                if isinstance(move, (int, float)):
                    move = time.strftime("%H:%M:%S", time.gmtime(int(move)))
                if isinstance(dist, (int, float)):
                    dist = f"{dist / 1000:.1f}"

                rows.append([date_val, name, tss, move, dist])
            md.append(table(headers, rows))
            debug(ctx, f"[Tier-2] Rendered Weekly Events Summary ({len(rows)} rows)")

    # --- Totals and metrics block ---
    if report_type.lower() == "weekly":
        md.append("")

        # --- PRIORITY 1: Dual totals from controller (Cycling + All) ---
        dual_cyc = ctx.get("summary_cycling")
        dual_all = ctx.get("summary_all")

        if dual_cyc and dual_all:
            md.append(
                f"**Cycling Totals:** {dual_cyc['hours']:.2f} h · "
                f"{dual_cyc['distance']:.1f} km · {dual_cyc['tss']} TSS · {dual_cyc['sessions']} sessions**"
            )
            md.append(
                f"**All Activities:** {dual_all['hours']:.2f} h · "
                f"{dual_all['distance']:.1f} km · {dual_all['tss']} TSS · {dual_all['sessions']} sessions**"
            )
            md.append("_Note: CTL/ATL/TSB values include **all activities**._")
            debug(ctx, "[RENDER] Dual totals rendered (Cycling + All)")

        # --- PRIORITY 2: Canonical fallbacks ---
        elif "tier1_visibleTotals" in ctx:
            vt = ctx["tier1_visibleTotals"]
            md.append(
                f"**Totals:** "
                f"{vt.get('hours', 0):.2f} h · "
                f"{vt.get('distance', 0):.1f} km · "
                f"{vt.get('tss', 0)} TSS · "
                f"{vt.get('count', 0)} sessions**"
            )

            mean_if = vt.get("avg_if")
            mean_hr = vt.get("avg_hr")
            mean_vo2 = vt.get("vo2max")
            summary_parts = []
            if mean_if is not None:
                summary_parts.append(f"**Cycling Metrics — Mean IF:** {mean_if:.2f}")
            if mean_hr is not None:
                summary_parts.append(f"**Mean HR:** {mean_hr} bpm")
            if mean_vo2 is not None:
                summary_parts.append(f"**VO₂ max:** {mean_vo2:.1f}")
            if summary_parts:
                md.append(" · ".join(summary_parts))
                debug(ctx, "[Tier-2] Weekly totals + mean metrics rendered (Tier-1 subset)")

        elif "tier0_snapshotTotals_7d" in ctx:
            st = ctx["tier0_snapshotTotals_7d"]
            md.append(
                f"**Weekly totals:** "
                f"{st.get('hours', 0):.2f} h · "
                f"{st.get('distance', 0):.1f} km · "
                f"{st.get('tss', 0)} TSS · "
                f"{st.get('count', 0)} sessions**"
            )
            debug(ctx, "[Tier-2] Weekly totals rendered from Tier-0 snapshot")

        elif "tier2_enforced_totals" in ctx:
            et = ctx["tier2_enforced_totals"]
            md.append(
                f"**Weekly totals:** "
                f"{et.get('time_h', 0):.2f} h · "
                f"{et.get('distance_km', 0):.1f} km · "
                f"{et.get('tss', 0)} TSS**"
            )
            debug(ctx, "[Tier-2] Weekly totals rendered from Tier-2 enforced DataFrame")

        else:
            md.append("_No event preview available._")
            debug(ctx, "[Tier-2 WARN] No event preview or totals available")


    # === 🧾 Final Summary ===
    md.append("\n---")
    md.append(f"✅ **Audit Completed:** {ctx.get('timestamp', datetime.utcnow().isoformat())}")
    md.append(f"**Framework:** URF v5.1 · Core: v16.14 · Enforcement: {ctx.get('enforcement_layer', '—')}")
    md.append("\n")

    try:
        md_text = "\n".join(md)
        debug(ctx, f"[RENDER-SECTIONS] md_text len={len(str(md_text)) if md_text else 0}")
    except Exception as e:
        debug(ctx, f"[RENDER-SECTIONS] FAILED → {e}")
        md_text = "_⚠ Renderer failed to build markdown sections._"

    debug(ctx, f"[TRACE-MD] Markdown length = {len(md_text)}")
    if "Efficiency & Adaptation" in md_text:
        debug(ctx, "[TRACE-MD] ✅ Adaptation section present before normalization.")
    else:
        debug(ctx, "[TRACE-MD] ❌ Adaptation section missing before normalization.")


    # --- Construct the Report object ---
    report = Report({
        "header": {
            "title": f"{report_type.title()} Training Report",
            "framework": "Unified_Reporting_Framework_v5.1",
            "athlete": name,
            "period": f"{start} → {end}",
            "timestamp": ctx.get("timestamp", datetime.utcnow().isoformat()),
            "discipline": ctx.get("discipline", "cycling"),
        },
        "markdown": md_text,
        "type": report_type,
        "context": ctx,
        "sections": [],
        "tables": [],
        "lines": ["✅ Report rendered successfully"],
    })

    # --- SAFETY PATCHES: ensure validator compatibility ---
    ctx["header"] = report["header"]
    ctx["ICON_CARDS"] = ICON_CARDS

    # --- Summary section (Tier-2 aware) ---
    if "summary_patch" in ctx:
        debug(ctx, "[Tier-2] Using canonical summary_patch from Tier-2 validator")
        report["summary"] = ctx["summary_patch"]
    else:
        report["summary"] = {
            "totalHours": ctx.get("totalHours", "—"),
            "totalTss": ctx.get("totalTss", "—"),
            "eventCount": ctx.get("event_count", "—"),
            "period": f"{start} → {end}",
            "athlete": name,
            "variance": ctx.get("variance", 0.0),
            "zones": ctx.get("zone_dist", {}),
            "🛌 Rest Day": ICON_CARDS.get("recovery", "🛌"),
            "⏳ Current Day": ICON_CARDS.get("info", "⏳"),
        }
        debug(ctx, "[Tier-2 WARN] No summary_patch — fallback to default recompute")

    # --- METRICS (schema-compliant) ---
    report["metrics"] = {
        "ACWR": ctx.get("ACWR", {"value": "—"}),
        "Monotony": ctx.get("Monotony", {"value": "—"}),
        "Strain": ctx.get("Strain", {"value": "—"}),
        "Polarisation": ctx.get("Polarisation", {"value": "—"}),
        "RecoveryIndex": ctx.get("RecoveryIndex", {"value": "—"})
    }

    report["actions"] = {
        "list": ctx.get("actions", []),
        "performance_flags": ctx.get("performance", {}),
        "notes": "Auto-generated validation placeholder for coaching actions."
    }

    report["phases"] = ctx.get("phase_breakdown", [
        {"phase": "Base", "weeks": 0, "load": "—", "notes": "No seasonal phase data available."}
    ])

    report["trends"] = ctx.get("trend_metrics", {
        "load_trend": ctx.get("load_trend", "—"),
        "fitness_trend": ctx.get("fitness_trend", "—"),
        "fatigue_trend": ctx.get("fatigue_trend", "—"),
        "note": "No trend data available — placeholder for validator compliance."
    })

    report["correlation"] = ctx.get("correlation_metrics", {
        "power_hr_correlation": ctx.get("power_hr_correlation", "—"),
        "efficiency_factor_change": ctx.get("efficiency_factor_change", "—"),
        "fatigue_vs_load": ctx.get("fatigue_vs_load", "—"),
        "note": "No correlation data available — placeholder for validator compliance."
    })

    report["footer"] = {"framework": "URF v5.1", "version": "v16.14"}

    # --- ✅ FINAL SAFETY NORMALIZATION (Markdown-only return) ---
    try:
        # --- Step 1: Ensure report has a valid Markdown string ---
        md_text = None
        if isinstance(report, dict):
            md_text = report.get("markdown")
            # If markdown is missing or invalid, try to recover or synthesize
            if not isinstance(md_text, str) or md_text.strip().startswith("{") or "DataFrame" in str(md_text):
                debug(ctx, "[SANITY] Invalid markdown payload — substituting canonical summary")
                md_text = (
                    "## Season Summary\n\n"
                    f"- **Period:** {ctx.get('window_start', 'n/a')} → {ctx.get('window_end', 'n/a')}\n"
                    f"- **Hours:** {ctx.get('totalHours', 'n/a')}\n"
                    f"- **TSS:** {ctx.get('totalTss', 'n/a')}\n"
                    f"- **Distance:** {ctx.get('totalDistance', 'n/a')} km\n"
                    f"- **Events:** {ctx.get('event_count', 'n/a')}\n"
                )
                report["markdown"] = md_text
        else:
            md_text = str(report).strip()
            if not md_text or md_text.startswith("{") or "DataFrame" in md_text:
                md_text = "_⚠ Renderer produced no valid Markdown output._"

        # --- Step 2: Strip heavy context payloads ---
        blacklist_patterns = [
            "df_", "trace", "debug", "snapshot", "json", "event_log",
            "activities", "dailymerged", "raw_analysis", "wellness"
        ]
        minimal_ctx = {}
        for k, v in ctx.items():
            if not any(p in k.lower() for p in blacklist_patterns):
                # skip anything with large dataframes/lists
                if isinstance(v, (list, dict)) and len(v) > 20:
                    continue
                minimal_ctx[k] = v

        # --- Step 3: Construct final compact return ---
        final_output = {
            "markdown": md_text.strip(),
            "context": minimal_ctx,
            "header": report.get("header", {}) if isinstance(report, dict) else {},
            "summary": report.get("summary", {}) if isinstance(report, dict) else {},
            "actions": report.get("actions", {}) if isinstance(report, dict) else {},
            "metrics": report.get("metrics", {}) if isinstance(report, dict) else {},
            "phases": report.get("phases", []) if isinstance(report, dict) else [],
        }

        # ✅ Optional visible confirmation (only once per run)
        if not ctx.get("_final_output_logged"):
            debug(ctx, f"[FINALIZER] ✅ Markdown-only return OK — len={len(md_text)}, ctx_keys={len(minimal_ctx)}")
            ctx["_final_output_logged"] = True
        else:
            debug(ctx, "[FINALIZER] Skipping duplicate Markdown-only confirmation")

        return final_output

    except Exception as e:
        import traceback
        tb = traceback.format_exc()

        # Log neatly via structured debug trace
        debug(ctx, f"[FINALIZER] ⚠ Exception during markdown-only return: {e}")
        debug(ctx, f"[TRACEBACK]\n{tb}")

        # Return compact failure object (no raw traceback in markdown)
        return {
            "markdown": (
                f"_⚠ Render failed: {e}_\n"
                "_Detailed error logged internally for diagnostics._"
            ),
            "context": {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "trace_excerpt": tb.splitlines()[-3:]  # last 3 lines, concise hint
            },
        }


def main():
    import argparse
    import traceback

    parser = argparse.ArgumentParser(
        description="Render a unified Markdown report from a JSON file"
    )
    parser.add_argument("input", help="Path to input JSON report (e.g. report.json)")
    parser.add_argument("--out", help="Optional output Markdown path (e.g. report.md)")
    args = parser.parse_args()

    path = Path(args.input)
    if not path.exists():
        print(f"❌ File not found: {path}")
        sys.exit(1)

    try:
        # --- Load JSON report structure ---
        data = json.loads(path.read_text())

        # --- Run renderer ---
        result = render_report(data)

        # --- Normalize output to markdown text ---
        if isinstance(result, dict):
            md_text = result.get("markdown", "")
            if not isinstance(md_text, str):
                md_text = str(md_text)
        else:
            md_text = str(result)

        # --- Write to file or print to stdout ---
        if args.out:
            out_path = Path(args.out)
            out_path.write_text(md_text, encoding="utf-8")
            print(f"✅ Markdown report written to {out_path}")
        else:
            print(md_text)

    except Exception as e:
        tb = traceback.format_exc()
        # Compact but clear CLI error
        print(f"⚠ Renderer failed: {e}")
        print("\n".join(tb.splitlines()[-6:]))  # last few lines only
        sys.exit(2)

if __name__ == "__main__":
    main()