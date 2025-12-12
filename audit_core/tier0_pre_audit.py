# audit_core/tier0_pre_audit.py — v16.14-OAUTH-STRICT + Canonical TZ Enforcement
import os
import sys
import requests
import pandas as pd
from audit_core.utils import debug
from datetime import datetime, timedelta
from audit_core.errors import AuditHalt
import json
import numpy as np

INTERVALS_API = os.getenv("INTERVALS_API", "https://intervalsicugptcoach.clive-a5a.workers.dev")

ICU_TOKEN = os.getenv("ICU_OAUTH")  # OAuth-only


def resolve_report_trigger(user_cmd: str, tz: str):
    today = datetime.now().astimezone().date()
    cmd = user_cmd.lower().strip()

    if any(k in cmd for k in ["rolling", "last 7", "past 7"]):
        mode = "rolling"
        start = today - timedelta(days=6)
        end = today
    elif any(k in cmd for k in ["calendar", "monday", "iso week"]):
        mode = "calendar"
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
    elif any(k in cmd for k in ["season", "block"]):
        mode = "season"
        start = today - timedelta(days=42)
        end = today
    else:
        mode = "rolling"
        start = today - timedelta(days=6)
        end = today

    return mode, start, end


def fetch_with_retry(url: str, headers: dict, max_retries: int = 2):
    """Low-level retry for individual API calls."""
    for attempt in range(max_retries + 1):
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp
        if attempt < max_retries:
            continue
    return resp


def estimate_payload_size(days: int, dataset: str):
    """Heuristic payload size estimator to prevent connector overflow."""
    if dataset == "wellness":
        return days * 30000  # wellness heavier
    else:
        return days * 12000  # activities lighter

# WELLNESS FETCH CHUNKED (optimized to single 42-day window)
def fetch_wellness_chunked(athlete_id, oldest, newest, headers, context=None, max_retries=2):
    """
    Adaptive and retryable fetch for wellness data.
    Normally just one call for 42 days, but retains chunk loop structure
    for consistency and safety.
    """
    import pandas as pd
    from datetime import timedelta

    wellness = []
    df_well = pd.DataFrame()

    total_days = (newest - oldest).days + 1

    # 🧩 Determine effective wellness window length
    default_wellness_days = context.get("range", {}).get("wellnessDays", 42)

    if total_days > default_wellness_days:
        debug(context, f"[T0-WELLNESS] Requested range {total_days}d exceeds default {default_wellness_days}d — using full requested span.")
    else:
        debug(context, f"[T0-WELLNESS] Using wellness window {total_days}d (default={default_wellness_days}d)")

    # Keep single fetch structure, but adjust dynamically
    well_chunk_days = total_days if total_days <= default_wellness_days else default_wellness_days
    debug(context, f"[T0-WELLNESS] Fetching wellness for {total_days}d range, chunk size={well_chunk_days}d")

    well_chunk_days = 42  # single chunk, safe payload size
    debug(context, f"[T0-WELLNESS] Fetching wellness for {total_days}d range, chunk size={well_chunk_days}d")

    for meta_attempt in range(max_retries + 1):
        try:
            for offset in range(0, total_days, well_chunk_days):
                chunk_start = oldest + timedelta(days=offset)
                chunk_end = min(newest, chunk_start + timedelta(days=well_chunk_days - 1))

                url = (
                    f"{INTERVALS_API}/athlete/{athlete_id}/wellness?"
                    f"oldest={chunk_start.strftime('%Y-%m-%d')}&newest={chunk_end.strftime('%Y-%m-%d')}"
                )
                debug(context, f"[T0-WELLNESS] Fetching chunk → {url}")

                resp = fetch_with_retry(url, headers)
                if resp.status_code != 200:
                    raise AuditHalt(f"❌ Wellness fetch failed ({resp.status_code}) → {resp.text[:200]}")

                payload = resp.json()
                if isinstance(payload, list) and payload:
                    wellness.extend(payload)

            if wellness:
                df_well = pd.DataFrame(wellness)
                break  # success → exit retry loop

        except Exception as e:
            debug(context, f"[T0-WELLNESS] Meta-attempt {meta_attempt+1} failed: {e}")
            if meta_attempt == max_retries:
                raise AuditHalt(f"❌ Wellness fetch failed after {max_retries + 1} meta-retries: {e}")
            continue

    # --- Normalize columns --------------------------------------------------
    if df_well.empty:
        debug(context, "[T0-WELLNESS] No data returned — creating empty frame.")
        df_well = pd.DataFrame(columns=["date", "ctl", "atl", "form", "fatigue"])
    else:
        if "date" not in df_well.columns:
            debug(context, "[T0-WELLNESS] Missing 'date' column — coercing.")
            if "id" in df_well.columns:
                df_well.rename(columns={"id": "date"}, inplace=True)
            else:
                df_well["date"] = pd.NaT

    debug(context, f"[T0-WELLNESS] Final wellness shape={df_well.shape}, columns={df_well.columns.tolist()}")
    return df_well


def fetch_activities_chunked(athlete_id, oldest, newest, headers, context=None, max_retries=2):
    """
    Adaptive and retryable chunked fetch for activities.
    - Season mode (light_mode=True): single 90-day lightweight call via /activities_t0light
    - Weekly/full mode: chunked 7d (or smaller) fetches via /activities
    """
    import numpy as np, json
    from datetime import timedelta

    # --- Determine mode ------------------------------------------------------
    light_mode = False
    if context and isinstance(context, dict):
        report_type = context.get("report_type", "").lower()
        if report_type == "season":
            light_mode = True
            context["fetch_mode"] = "light"
            debug(context, "🧩 Tier-0: Lightweight season fetch detected → single-call mode (no chunking).")
        else:
            context["fetch_mode"] = "full"

    total_days = (newest - oldest).days + 1
    est_payload_acts = estimate_payload_size(total_days, "activities")

    # --- Chunking strategy ---------------------------------------------------
    if light_mode:
        act_chunk_days = total_days  # single call for 90d
        debug(context, f"[T0] Lightweight fetch: single API call for {total_days} days (no chunking).")
    else:
        act_chunk_days = 7 if est_payload_acts < 200000 else 3
        debug(context, f"[T0] Full fetch: chunking {total_days} days into {int(np.ceil(total_days/act_chunk_days))} parts.")

    df_activities_list = []

    # --- Fetch loop ----------------------------------------------------------
    for meta_attempt in range(max_retries + 1):
        try:
            for offset in range(0, total_days, act_chunk_days):
                chunk_start = oldest + timedelta(days=offset)
                chunk_end = min(newest, chunk_start + timedelta(days=act_chunk_days)) - timedelta(seconds=1)

                # --- Choose correct route for mode ---
                if light_mode:
                    acts_url = (
                        f"{INTERVALS_API}/athlete/{athlete_id}/activities_t0light?"
                        f"oldest={chunk_start.strftime('%Y-%m-%d')}&newest={chunk_end.strftime('%Y-%m-%d')}"
                        "&fields=id,name,type,start_date_local,distance,moving_time,"
                        "icu_training_load,IF,average_heartrate,VO2MaxGarmin"
                    )
                else:
                    acts_url = (
                        f"{INTERVALS_API}/athlete/{athlete_id}/activities?"
                        f"oldest={chunk_start.strftime('%Y-%m-%d')}&newest={chunk_end.strftime('%Y-%m-%d')}"
                    )

                debug(context, f"[Tier-0 fetch] → {acts_url}")

                acts_resp = fetch_with_retry(acts_url, headers)
                if acts_resp.status_code != 200:
                    raise AuditHalt(f"❌ Failed to fetch activities ({acts_resp.status_code}) → {acts_resp.text[:200]}")

                payload = acts_resp.json()
                if not isinstance(payload, list) or not payload:
                    continue

                if "icu_training_load_data" in payload[0] and "icu_training_load" not in payload[0]:
                    for r in payload:
                        r["icu_training_load"] = r.pop("icu_training_load_data")

                # --- Safe normalization to handle nested dict/list rows ---
                try:
                    df_chunk = pd.json_normalize(payload, max_level=1)
                except Exception as e:
                    debug(context, f"[T0] Normalization fallback due to {e}")
                    # Fallback: flatten nested dicts manually if json_normalize fails
                    def flatten_dict(d):
                        flat = {}
                        for k, v in d.items():
                            if isinstance(v, dict):
                                for subk, subv in v.items():
                                    flat[f"{k}_{subk}"] = subv
                            else:
                                flat[k] = v
                        return flat
                    df_chunk = pd.DataFrame([flatten_dict(r) for r in payload])

                if not df_chunk.empty:
                    df_activities_list.append(df_chunk)

                if light_mode:
                    break  # single call for season

            break  # success
        except Exception as e:
            debug(context, f"[T0-FETCH-RETRY] Attempt {meta_attempt+1} failed: {e}")
            if meta_attempt == max_retries:
                raise AuditHalt(f"❌ Activities fetch failed after {max_retries + 1} attempts: {e}")
            continue

    if not df_activities_list:
        debug(context, "⚠ No activity chunks returned from API (all payloads empty).")
        return pd.DataFrame()

    # --- Merge and normalize -------------------------------------------------
    df_activities = pd.concat(df_activities_list, ignore_index=True)

    if "id" in df_activities.columns:
        before = len(df_activities)
        df_activities.drop_duplicates(subset=["id"], inplace=True)
        debug(context, f"[T0] Deduplicated {before - len(df_activities)} duplicate activities.")

    # --- Normalize time units ---
    if "moving_time" in df_activities.columns:
        max_val = df_activities["moving_time"].max()
        if max_val < 1000:
            df_activities["moving_time"] *= 3600
            debug(context, f"[T0] Converted moving_time hours→seconds (max={max_val})")

    # --- Normalize timezone and dates ---
    tz = context.get("timezone", "Europe/Zurich")
    if "start_date" in df_activities.columns:
        df_activities["start_date_local"] = pd.to_datetime(
            df_activities["start_date"], utc=True, errors="coerce"
        ).dt.tz_convert(tz)
    elif "start_date_local" in df_activities.columns:
        df_activities["start_date_local"] = pd.to_datetime(df_activities["start_date_local"], errors="coerce")

    df_activities["date"] = df_activities["start_date_local"].dt.date
    df_activities["origin"] = "event"

    # --- Optional: Expand zones in full mode only ---
    if not light_mode:
        def expand_zones(df, field, prefix):
            def safe_parse(x):
                if x in [None, "null", "None", np.nan]:
                    return []
                if isinstance(x, str):
                    try:
                        x = json.loads(x)
                    except Exception:
                        return []
                if isinstance(x, list):
                    flat = []
                    for z in x:
                        if isinstance(z, dict):
                            flat.append(z.get("secs", 0))
                        elif isinstance(z, (int, float)):
                            flat.append(z)
                    return flat
                return []
            try:
                parsed = df[field].apply(safe_parse)
                max_len = parsed.map(len).max() if not parsed.empty else 0
                if max_len == 0:
                    return df
                z = pd.DataFrame(parsed.tolist(), index=df.index)
                z = z.reindex(columns=range(max_len)).fillna(0).astype(float)
                z.columns = [f"{prefix}_z{i+1}" for i in range(max_len)]
                df = pd.concat([df.drop(columns=[field]), z], axis=1)
                debug(context, f"[T0] Expanded {field} → {len(z.columns)} cols")
            except Exception as e:
                debug(context, f"[T0] Zone expansion failed for {field}: {e}")
            return df

        df_activities = expand_zones(df_activities, "icu_zone_times", "power")
        df_activities = expand_zones(df_activities, "icu_hr_zone_times", "hr")
        df_activities = expand_zones(df_activities, "pace_zone_times", "pace")

    # --- Diagnostics ---
    total_tss = df_activities["icu_training_load"].sum() if "icu_training_load" in df_activities else 0
    total_time = df_activities["moving_time"].sum() / 3600 if "moving_time" in df_activities else 0
    debug(context, f"[T0] Diagnostics → Σ(TSS)={total_tss:.1f}, Σ(Time)={total_time:.2f}h")

    debug(context, f"[T0] Completed {'lightweight' if light_mode else 'full'} fetch → {len(df_activities)} records.")
    return df_activities




#FETCH AHLETEPROFILE
def fetch_athlete_profile(headers, context=None):
    """Fetch and normalize the athlete profile via OAuth2."""
    profile_url = f"{INTERVALS_API}/athlete/0/profile"
    debug(context,f"[T0] Fetching athlete profile via OAuth2: {profile_url}")

    profile_resp = fetch_with_retry(profile_url, headers)
    if profile_resp.status_code != 200:
        raise AuditHalt(
            f"❌ Failed to fetch athlete profile ({profile_resp.status_code}) → {profile_resp.text[:200]}"
        )

    profile_json = profile_resp.json()
    athlete = profile_json.get("athlete", profile_json)

    if not isinstance(athlete, dict):
        raise AuditHalt("❌ Invalid athlete profile format — expected dictionary payload")

    # Default ID handling
    if "id" not in athlete or athlete["id"] in [None, "", "unknown"]:
        debug(context,"⚠️ No athlete.id found — assigning default ID 0 (current athlete).")
        athlete["id"] = 0

    # Reject invalid sources
    if athlete.get("source") in ["mock", "cache", "sandbox"]:
        raise AuditHalt("❌ Tier-0 halted: invalid data origin (mock/cache/sandbox)")

    # Assign timezone
    tz = athlete.get("timezone", "Europe/Zurich")
    context = context or {}
    context["timezone"] = tz if isinstance(tz, str) and len(tz) >= 3 else "Europe/Zurich"

    # Merge static profile baseline
    from athlete_profile import ATHLETE_PROFILE
    merged_profile = ATHLETE_PROFILE.copy()
    merged_profile.update({
        "athlete_id": athlete.get("id", 0),
        "name": athlete.get("name", "Unknown Athlete"),
        "discipline": athlete.get("sport", "cycling"),
        "ftp": athlete.get("ftp", None),
        "weight": athlete.get("weight", None),
        "hr_rest": athlete.get("resting_hr", None),
        "hr_max": athlete.get("max_hr", None),
        "timezone": context["timezone"],
        "updated": athlete.get("updated"),
    })

    # Store in context for downstream
    context["athleteProfile"] = merged_profile
    context["athlete"] = athlete

    debug(context,f"[T0] Athlete profile fetched successfully — id={athlete['id']} name={athlete.get('name')}")
    return athlete, context

def run_tier0_pre_audit(start: str, end: str, context: dict):
    """Tier-0: OAuth-only Pre-audit fetch chain with adaptive chunking and meta-retry."""

    # =======================================================
    # CLOUDFLARE MODE → SKIP FETCHES ONLY
    # but still run:
    # - slicing
    # - dedupe
    # - totals
    # - range alignment
    # - df_master construction
    # - wellness clipping
    # - snapshot creation
    # =======================================================
    # ============================================================
    # CLOUD-FLARE MODE → Skip fetches but still build full Tier-0
    # ============================================================
    if context.get("cloudflare_mode"):
        debug(context, "[T0] Cloudflare mode → using injected datasets (no API calls)")

        df_light = pd.DataFrame(context.get("cf_light", []))
        df_full = pd.DataFrame(context.get("cf_full", []))
        wellness = pd.DataFrame(context.get("cf_wellness", []))

        # Parse dates for slicing
        if "start_date_local" in df_light.columns:
            df_light["start_date_local"] = pd.to_datetime(df_light["start_date_local"], errors="coerce")

            end_dt = pd.to_datetime(end)
            start_dt = end_dt - pd.Timedelta(days=6)

            df_light_slice = df_light[
                (df_light["start_date_local"] >= start_dt)
                & (df_light["start_date_local"] <= end_dt)
            ].copy()
        else:
            df_light_slice = df_light.copy()

        report_type = context.get("report_type", "").lower()

        if report_type in ("season", "season_phases", "season_summary"):
            # NEVER use df_full for season
            df_master = df_light.copy()
            debug(context, f"[T0-CF] Season mode → df_master=90d light ({len(df_master)} rows)")
        else:
            # weekly / summary / wellness
            df_master = df_full.copy() if not df_full.empty else df_light_slice.copy()

        # Inject back into context
        context["df_light"] = df_light
        context["df_light_slice"] = df_light_slice
        context["df_master"] = df_master
        context["wellness"] = wellness
        context["athlete"] = context.get("cf_athlete", {})

        # Create Tier-0 snapshot
        context["snapshot_7d_json"] = df_master.to_json(orient="records")
        context["tier0_snapshotTotals_7d"] = {
            "hours": df_master["moving_time"].sum() / 3600 if "moving_time" in df_master else 0,
            "tss": df_master["icu_training_load"].sum() if "icu_training_load" in df_master else 0,
            "sessions": len(df_master)
        }

        # Return directly into Tier-1
        return df_master, wellness, context, False, False



    if not ICU_TOKEN:
        raise EnvironmentError("Missing Intervals.icu OAuth token. Set ICU_OAUTH env var.")
    debug(context, f"[Tier-0] Using API endpoint: {INTERVALS_API}")

    # --- Step 0b: Lightweight 28-day or 90-day snapshot (via proxy GET) ---
    headers = {"Authorization": f"Bearer {ICU_TOKEN}"}
    report_type = context.get("report_type", "").lower() if isinstance(context, dict) else "weekly"

    # Preserve controller-defined range; only fill defaults if missing
    context.setdefault("range", {})
    context["range"].setdefault("lightDays", 90 if report_type == "season" else 90)
    context["range"].setdefault("fullDays", 42 if report_type == "season" else 7)
    context["range"].setdefault("chunk", True if report_type == "season" else False)

    # Ensure df_light always exists
    df_light = pd.DataFrame()
    df_acts = pd.DataFrame()
    df_light_slice = pd.DataFrame()


    # --- Allow refetch for season mode ---
    if context.get("report_type", "").lower() == "season":
        debug(context, "[T0-LIGHT] Forcing re-fetch for season mode (ignoring prefetch_done flag).")
        context["prefetch_done"] = False

    # prevent redundant prefetch when this function re-enters (e.g., weekly summaries)
    if context.get("prefetch_done", False):
        debug(context, "[T0-LIGHT] Prefetch already completed — skipping redundant lightweight call.")
    else:
        context["prefetch_done"] = True


        fields = (
            "id,name,type,start_date_local,distance,moving_time,"
            "icu_training_load,IF,average_heartrate,VO2MaxGarmin"
        )
        # 🧭 use actual arguments instead of hardcoded offset
        oldest = pd.to_datetime(start).strftime("%Y-%m-%d")
        newest = pd.to_datetime(end).strftime("%Y-%m-%d")

        debug(context, f"[T0-LIGHT] Using controller-supplied range oldest={oldest} newest={newest}")

        light_url = (
            f"{INTERVALS_API}/athlete/0/activities_t0light?"
            f"oldest={oldest}&newest={newest}&fields={fields}"
        )
        debug(context, f"[T0-LIGHT] Fetching lightweight dataset → {light_url}")
        resp = fetch_with_retry(light_url, headers)
        if resp.status_code != 200:
            raise AuditHalt(f"❌ Tier-0 lightweight fetch failed → {resp.status_code}: {resp.text[:200]}")

        payload = resp.json()
        if not payload:
            raise AuditHalt("❌ Tier-0 lightweight fetch returned no data")

        df_light = pd.DataFrame(payload)
        context["df_light_full"] = df_light.copy()
        df_acts = df_light.copy()
        debug(context, f"[T0-LIGHT] Retrieved {len(df_light)} activities with {len(df_light.columns)} fields")

        # --- Diagnostic: check dataset contents early ---
        if df_light.empty:
            debug(context, "[T0-LIGHT-DIAG] ❌ df_light is EMPTY — Intervals.icu returned no activities.")
        else:
            debug(context, f"[T0-LIGHT-DIAG] ✅ df_light populated. First 3 rows:\n{df_light.head(3).to_string(index=False)}")
            debug(context, f"[T0-LIGHT-DIAG] Columns: {df_light.columns.tolist()}")

        # --- Ensure df_light_slice exists (initialize from df_light) ---
        df_light_slice = df_light.copy()
        debug(context, f"[T0-INIT] Created df_light_slice from df_light → {len(df_light_slice)} rows.")
        debug(context, f"[T0-DIAG] Pre-slice df_light rows={len(df_light)}; "
                    f"min={df_light['start_date_local'].min() if 'start_date_local' in df_light else 'n/a'}, "
                    f"max={df_light['start_date_local'].max() if 'start_date_local' in df_light else 'n/a'}")


        # --- Adaptive window based on report_type ---
        report_type = context.get("report_type", "").lower() if isinstance(context, dict) else "weekly"

        df_light["start_date_local"] = pd.to_datetime(
            df_light["start_date_local"], errors="coerce"
        ).dt.tz_localize(None)

        if report_type == "season":
            slice_days = 90
            debug(context, f"🧩 Tier-0 override: using {slice_days}-day slice for season report.")
        else:
            slice_days = 7

        window_end_exclusive = pd.to_datetime(end) + pd.Timedelta(days=1)
        window_start = pd.to_datetime(end) - pd.Timedelta(days=slice_days - 1)

        # --- Slice to adaptive subset (skip slicing for season mode) ---
        if report_type == "season":
            df_light_slice = df_light.copy()
            debug(context, f"[T0-SLICE] Season mode: using full {len(df_light)}-row dataset (no date filter).")
        else:
            df_light_slice = df_light[
                (df_light["start_date_local"] >= window_start)
                & (df_light["start_date_local"] < window_end_exclusive)
            ].copy()
            debug(
                context,
                f"[T0-SLICE] {slice_days}-day window: {window_start.date()} → {window_end_exclusive.date()} "
                f"({len(df_light_slice)} activities selected)"
            )       

        # --- Deduplicate before totals ---
        if "id" in df_light_slice.columns:
            before_dedup = len(df_light_slice)
            df_light_slice = df_light_slice.drop_duplicates(subset=["id"], keep="first")
            after_dedup = len(df_light_slice)
            debug(context, f"[T0-DEDUP] Dropped {before_dedup - after_dedup} duplicates → {after_dedup} unique events")

        # --- Numeric conversion ---
        for col in ["moving_time", "distance", "icu_training_load"]:
            if col in df_light_slice.columns:
                df_light_slice[col] = pd.to_numeric(df_light_slice[col], errors="coerce").fillna(0)

        # --- Compute adaptive totals ---
        totals_key = f"tier0_snapshotTotals_{slice_days}d"
        context[totals_key] = {
            "hours": round(df_light_slice["moving_time"].sum() / 3600, 2),
            "distance": round(df_light_slice["distance"].sum() / 1000, 1),
            "tss": int(df_light_slice["icu_training_load"].sum()),
            "count": len(df_light_slice),
            "start": str(window_start.date()),
            "end": str(window_end_exclusive.date())
        }

        debug(
            context,
            f"🧭 Tier-0: {slice_days}-day subset (lightweight) = "
            f"{context[totals_key]['hours']} h | "
            f"{context[totals_key]['distance']} km | "
            f"{context[totals_key]['tss']} TSS "
            f"({context[totals_key]['count']} events)"
        )

        # --- Serialize for Tier-1 use ---
        context["snapshot_7d_json"] = df_light_slice.to_json(orient="records")

    # --- Preserve full 90-day dataset BEFORE any 7-day filtering ---
    if report_type == "season":
        try:
            if "df_light_slice" not in locals() or not isinstance(df_light_slice, pd.DataFrame):
                df_light_slice = df_light.copy() if isinstance(df_light, pd.DataFrame) else pd.DataFrame()

            if isinstance(df_light, pd.DataFrame) and len(df_light) > 28:
                context["df_light_slice"] = df_light.copy()
                context["activities_light"] = df_light.copy()
                debug(context, f"[T0] Preserved full 90-day df_light for Tier-1/Tier-2 ({len(df_light)} rows)")
            else:
                context["df_light_slice"] = df_light_slice.copy()
                context["activities_light"] = df_light_slice.copy()
                debug(context, f"[T0] Fallback preserved df_light_slice for Tier-1/Tier-2 ({len(df_light_slice)} rows)")

        except Exception as e:
            debug(context, f"[T0] Failed to preserve 90-day dataset → {e}")

    # --- Step 1: Fetch athlete profile ---
    athlete, context = fetch_athlete_profile(headers, context)

    # --- Step 2: Define canonical date window (metadata only) ---
    if context.get("report_type", "").lower() == "season":
        mode = "season"
        oldest = pd.Timestamp.now() - pd.Timedelta(days=90)
        newest = pd.Timestamp.now()
        debug(context, f"🧩 Tier-0: defining 90-day window context for season mode (no data reslice).")
    else:
        mode, oldest, newest = resolve_report_trigger("weekly", context["timezone"])

    context.update({"report_mode": mode, "window_start": oldest, "window_end": newest})

    # --- Step 3: Fetch activities using adaptive method ---
    report_type = str(context.get("report_type", "")).lower()
    debug(context, f"[T0-FETCH] Adaptive method for report_type={report_type}")

    if report_type == "season":
        debug(context, "[T0-LIGHT] Season mode → using 90-day lightweight dataset only (no full fetch).")
        if "df_light_slice" not in locals():
            df_light_slice = context.get("df_light_slice", pd.DataFrame())
        df_activities = df_light_slice.copy()
        try:
            from audit_core.utils_season_summary import summarize_season_blocks
            df_activities = summarize_season_blocks(df_activities)
            debug(context, f"[T0-SUMMARY] Aggregated season summary: {len(df_activities)} weekly/phase blocks.")
        except ImportError:
            debug(context, "[T0-SUMMARY] summarize_season_blocks() unavailable — using raw 90-day dataset.")
    else:
        debug(context, "[T0-FETCH] Weekly mode → combining lightweight (for totals) + 7-day full fetch (for detail).")

        # --- Perform full 7-day detailed fetch first ---
        df_activities = fetch_activities_chunked(athlete["id"], oldest, newest, headers, context)
        debug(context, f"[T0-FETCH] Full 7-day fetch complete: {len(df_activities)} activities.")

        # --- 🧩 Merge Light + Full safely (pre-Tier1 canonicalization)
        try:
            df_light = context.get("df_light_slice", pd.DataFrame())
            df_full = df_activities.copy()

            # Ensure both are valid DataFrames before merging
            if isinstance(df_light, pd.DataFrame) and isinstance(df_full, pd.DataFrame) and not df_light.empty and not df_full.empty:
                df_light["origin"] = "light"
                df_full["origin"] = "event"

                # ✅ SAFE MERGE using concat — avoids "mixing dicts" bug
                df_merged = pd.concat([df_light, df_full], ignore_index=True)

                # --- Deduplicate canonical IDs
                before_dedup = len(df_merged)
                df_merged = df_merged.drop_duplicates(subset=["id"], keep="last").reset_index(drop=True)
                dropped = before_dedup - len(df_merged)

                # --- Store canonical frames in context
                context["df_raw_activities"] = df_merged
                context["df_light_slice"] = df_light
                context["df_full_slice"] = df_full
                context["activities_light"] = df_light
                context["activities_full"] = df_full

                # ✅ Tag dataset as full verified source for audit gate
                context["data_source"] = "full_7d"

                debug(context, f"[T0-MERGE] ✅ Light+Full merged successfully: {len(df_merged)} rows (dropped {dropped})")
                debug(context, f"[T0-MERGE] Σh={df_merged['moving_time'].sum()/3600:.2f}h ΣTSS={df_merged['icu_training_load'].sum():.0f}")
            else:
                debug(context, "[T0-MERGE] ⚠ Missing light or full dataset — merge skipped.")
                context["data_source"] = "light_fallback"
        except Exception as e:
            context["data_source"] = "light_fallback"
            debug(context, f"[T0-MERGE] ❌ Failed during Light+Full merge: {e}")

        # --- Determine which dataset should feed Tier-1 snapshot ---
        report_type = str(context.get("report_type", "")).lower().strip()

        if report_type in ["weekly", "week", "7d"]:
            # WEEKLY → use full 7-day detailed dataset
            source_df = df_activities
            debug(context, f"[T0] Weekly mode → using FULL 7-day dataset for snapshot_7d_json ({len(source_df)} rows)")
        elif report_type in ["season", "block", "90d"]:
            # SEASON → use lightweight 90-day dataset
            source_df = df_light_slice
            debug(context, f"[T0] Season mode → using LIGHT 90-day dataset for snapshot_7d_json ({len(source_df)} rows)")
        else:
            # fallback default
            source_df = df_light_slice
            debug(context, f"[T0] Unknown report_type='{report_type}' → defaulting to LIGHT dataset ({len(source_df)} rows)")

        # --- Validate before serializing ---
        if source_df.empty:
            raise AuditHalt(f"❌ Tier-0: snapshot source empty before serialization (report_type={report_type})")
        if "type" not in source_df.columns:
            raise AuditHalt(
                f"❌ Tier-0: missing 'type' column in source_df before snapshot_7d_json "
                f"(columns={list(source_df.columns)})"
            )

    # --- Serialize for Tier-1 ---
    # --- Fallback handling for season mode ---
    if "source_df" not in locals() or source_df is None:
        debug(context, "[T0-FIX] source_df undefined — using df_light as fallback (season mode).")
        source_df = df_light.copy() if "df_light" in locals() else pd.DataFrame()

    # Defensive serialization
    if not source_df.empty:
        context["snapshot_7d_json"] = source_df.to_json(orient="records")
        debug(context, f"[T0-FIX] snapshot_7d_json serialized from fallback source ({len(source_df)} rows).")
    else:
        debug(context, "[T0-FIX] No valid source_df available for snapshot_7d_json — created empty frame.")
        context["snapshot_7d_json"] = "[]"

    # --- Step 4: Fetch wellness with adaptive chunking + meta-retry ---
    wellness_days = context.get("range", {}).get("wellnessDays", 42)
    today = pd.Timestamp.now().normalize()
    wellness_newest = today
    wellness_oldest = wellness_newest - pd.Timedelta(days=wellness_days)

    debug(context, f"[T0] Fetching wellness for {wellness_days} days → {wellness_oldest} → {wellness_newest}")

    wellness = fetch_wellness_chunked(athlete["id"], wellness_oldest, wellness_newest, headers, context)

    if isinstance(wellness, pd.DataFrame) and not wellness.empty:
        context["wellness"] = wellness
        debug(context, f"[T0] Stored wellness in context ({len(wellness)} rows)")
    else:
        raise AuditHalt("❌ No wellness data returned after chunked fetch")

    # --- Step 4b: Enforce correct dataset range alignment ---------------------
    try:
        if isinstance(df_activities, pd.DataFrame) and not df_activities.empty \
           and isinstance(wellness, pd.DataFrame) and not wellness.empty:

            start_acts = df_activities["start_date_local"].min()
            end_acts = df_activities["start_date_local"].max()
            start_well = wellness["date"].min()
            end_well = wellness["date"].max()

            debug(context, f"[T0] Activities range: {start_acts.date()} → {end_acts.date()}")
            debug(context, f"[T0] Wellness range: {start_well} → {end_well}")

            # Clip wellness to last 42 days relative to the activity window
            from datetime import timedelta
            cutoff_date = pd.to_datetime(end_acts.date()) - timedelta(days=42)
            wellness = wellness[wellness["date"] >= cutoff_date.strftime("%Y-%m-%d")]

            debug(
                context,
                f"[T0] Clipped wellness to last 42 days relative to activities end date ({cutoff_date.date()} onward) → {len(wellness)} rows."
            )

            context["wellness"] = wellness.reset_index(drop=True)

        else:
            debug(context, "[T0 WARN] Skipped range alignment — missing activity or wellness data.")
    except Exception as e:
        debug(context, f"[T0 WARN] Failed to align wellness range: {e}")


    # --- Debug inspection ---
    debug(context,"[DEBUG] wellness raw:", type(wellness), len(wellness))
    if isinstance(wellness, pd.DataFrame):
        debug(context,"[DEBUG] wellness columns:", wellness.columns.tolist())
        debug(context,"[DEBUG] wellness head:\n", wellness.head())
        
    # --- Step 5: Finalize context ---
    context.update({"auditPartial": False, "auditFinal": False})
    context["window_summary"] = {"mode": mode, "start": str(oldest), "end": str(newest)} 

    debug(context, f"[T0] Diagnostic only: {len(df_activities)} rows fetched, moving_time present={ 'moving_time' in df_activities }")

    # Normalize wellness payload to DataFrame for Tier-1 compatibility
    if isinstance(wellness, list):
        if len(wellness) > 0:
            wellness = pd.DataFrame(wellness)
        else:
            wellness = pd.DataFrame(columns=["date", "fatigue", "sleep", "hrv", "recovery"])

    # --- Safety fix for missing wellness 'date' column ---
    if isinstance(wellness, pd.DataFrame):
        if "id" in wellness.columns and "date" not in wellness.columns:
            wellness.rename(columns={"id": "date"}, inplace=True)
        if "date" not in wellness.columns:
            debug(context, "[T0] Wellness missing 'date' column — inserting placeholder.")
            wellness["date"] = pd.NaT
    else:
        wellness = pd.DataFrame(columns=["date", "ctl", "atl", "tsb"])

    debug(context, f"[T0] Pre-audit complete: activities={len(df_activities)}, wellness_rows={len(wellness)}")

    # --- Preserve wellness for Tier-1 ---
    if isinstance(wellness, pd.DataFrame) and not wellness.empty:
        context["wellness"] = wellness
        debug(context, f"[T0] Stored wellness for Tier-1 ({len(wellness)} rows)")

    # --- 🧮 Mode-specific snapshot & totals creation ---
    report_type = context.get("report_type", "").lower() or os.environ.get("REPORT_TYPE", "weekly")

    if not df_light.empty:
        if report_type == "season":
            # 42-day visible slice from 90-day lightweight fetch
            df_snap = df_light.tail(42)
            context["snapshot_42d_json"] = df_snap.to_dict(orient="records")
            context["tier0_snapshotTotals_42d"] = {
                "hours": df_snap["moving_time"].sum() / 3600,
                "distance": df_snap["distance"].sum() / 1000,
                "tss": df_snap["icu_training_load"].sum(),
                "weeks": df_snap["start_date_local"].dt.isocalendar().week.nunique(),
                "source": "Tier-0 lightweight 90-day dataset"
            }
            debug(context, f"[T0] Created 42d snapshot for season ({len(df_snap)} rows)")
        else:
            # Weekly: 7-day visible slice from 28-day lightweight fetch
            df_snap = df_light.tail(7)
            context["snapshot_7d_json"] = df_snap.to_dict(orient="records")
            context["tier0_snapshotTotals_7d"] = {
                "hours": df_snap["moving_time"].sum() / 3600,
                "distance": df_snap["distance"].sum() / 1000,
                "tss": df_snap["icu_training_load"].sum(),
                "count": len(df_snap),
                "source": "Tier-0 lightweight 28-day dataset"
            }
            debug(context, f"[T0] Created 7d snapshot for weekly ({len(df_snap)} rows)")
    else:
        debug(context, "[T0] ⚠ No df_light data available to build snapshots")

    # --- Final sanity: ensure 'start_date_local' exists for Tier-1 ---
    if "start_date_local" not in df_activities.columns:
        debug(context, "⚠️ 'start_date_local' missing — attempting reconstruction from 'start_date' or 'date'.")
        if "start_date" in df_activities.columns:
            df_activities["start_date_local"] = pd.to_datetime(df_activities["start_date"], errors="coerce")
        elif "date" in df_activities.columns:
            df_activities["start_date_local"] = pd.to_datetime(df_activities["date"], errors="coerce")
        else:
            df_activities["start_date_local"] = pd.Timestamp.now()
        df_activities["start_date_local"] = df_activities["start_date_local"].dt.tz_localize(None)
        debug(context, f"[T0-FIX] Injected synthetic start_date_local for {len(df_activities)} activities.")

    # --- Season-mode extended snapshot (42-day full fetch) ---
    if report_type == "season":
        try:
            df_season_full = df_activities.copy()

            # Store extended snapshot for Tier-1 normalization
            context["snapshot_42d_json"] = df_season_full.to_dict(orient="records")

            context["tier0_snapshotTotals_42d"] = {
                "hours": df_season_full["moving_time"].sum() / 3600,
                "distance": df_season_full["distance"].sum() / 1000,
                "tss": df_season_full["icu_training_load"].sum(),
                "count": len(df_season_full),
                "source": "Tier-0 42d full dataset",
            }

            debug(context, "[T0-SEASON] Exported snapshot_42d_json + tier0_snapshotTotals_42d for season mode.")
        except Exception as e:
            debug(context, f"[T0-SEASON WARN] Failed to create season snapshot: {e}")

    # ------------------------------------------------------------
    # PRESERVE REAL 90-DAY DATASET (for extended metrics)
    # ------------------------------------------------------------

    # If we captured df_light_full earlier, use it.
    if "df_light_full" in context and isinstance(context["df_light_full"], pd.DataFrame):
        context["df_light"] = context["df_light_full"].copy()      # <-- 90-day dataset
        context["activities_light"] = context["df_light_full"].copy()
    else:
        # Fallback: use whatever df_light is
        context["df_light"] = df_light
        context["activities_light"] = df_light.copy()

    # Always preserve the sliced window too
    context["df_light_slice"] = df_light_slice

    # Full detailed 7-day dataset
    context["df_master"] = df_activities

    return df_activities, wellness, context, context.get("auditPartial"), context.get("auditFinal")