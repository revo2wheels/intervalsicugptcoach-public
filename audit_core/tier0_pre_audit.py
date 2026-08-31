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
from audit_core.utils import set_time_context

INTERVALS_API = os.getenv("INTERVALS_API", "https://intervalsicugptcoach.clive-a5a.workers.dev")

ICU_TOKEN = os.getenv("ICU_OAUTH")  # OAuth-only

def resolve_dataset(name: str, fetch_fn, context: dict):
    """
    Resolve dataset from prefetched cache if available,
    otherwise fetch via provided fetch_fn.
    """
    prefetched = context.get("prefetched", {})
    if name in prefetched:
        debug(context, f"[T0-RESOLVE] Using prefetched '{name}' dataset")
        return fetch_fn(from_cache=prefetched[name], context=context)
    else:
        debug(context, f"[T0-RESOLVE] Fetching '{name}' dataset")
        return fetch_fn(from_cache=None, context=context)

def resolve_report_trigger(user_cmd: str, context: dict):
    today = context["athlete_today"].date()
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

def fetch_wellness_chunked(
    athlete_id,
    oldest,
    newest,
    headers,
    context=None,
    from_cache=None,
    max_retries=2,
):
    """
    Adaptive and retryable fetch for wellness data.

    - Normally a single 42-day call
    - Retains chunk loop for safety / retries
    - Supports prefetched (Cloudflare) cache
    """

    # =================================================
    # ✅ CACHE PATH (Cloudflare / prefetched)
    # =================================================
    if from_cache is not None:
        df = pd.DataFrame(from_cache)
        debug(context, f"[T0] Loaded cached wellness ({len(df)} rows)")
        return df

    # =================================================
    # 🌐 FETCH PATH (Local / orchestrated)
    # =================================================

    wellness = []
    df_well = pd.DataFrame()

    total_days = (newest - oldest).days + 1

    report_type = context.get("report_type") or context.get("meta", {}).get("report_type")

    default_wellness_days = context.get("range", {}).get("wellnessDays", 42)

    # Summary / annual → fetch entire requested window
    if report_type == "summary":
        well_chunk_days = total_days
    else:
        well_chunk_days = min(total_days, default_wellness_days)

    debug(
        context,
        f"[T0-WELLNESS] Fetching wellness "
        f"({total_days}d requested, chunk={well_chunk_days}d)"
    )

    # --- Fetch loop -----------------------------------
    for meta_attempt in range(max_retries + 1):
        try:
            for offset in range(0, total_days, well_chunk_days):
                chunk_start = oldest + timedelta(days=offset)
                chunk_end = min(
                    newest,
                    chunk_start + timedelta(days=well_chunk_days - 1),
                )

                url = (
                    f"{INTERVALS_API}/athlete/{athlete_id}/wellness?"
                    f"oldest={chunk_start:%Y-%m-%d}&newest={chunk_end:%Y-%m-%d}"
                )

                debug(context, f"[T0-WELLNESS] → {url}")

                resp = fetch_with_retry(url, headers)
                if resp.status_code != 200:
                    raise AuditHalt(
                        f"❌ Wellness fetch failed ({resp.status_code}) → "
                        f"{resp.text[:200]}"
                    )

                payload = resp.json()
                if isinstance(payload, list) and payload:
                    wellness.extend(payload)

            if wellness:
                df_well = pd.DataFrame(wellness)
                break

        except Exception as e:
            debug(context, f"[T0-WELLNESS] Attempt {meta_attempt + 1} failed: {e}")
            if meta_attempt == max_retries:
                raise AuditHalt(
                    f"❌ Wellness fetch failed after {max_retries + 1} attempts: {e}"
                )

        debug(
            context,
            f"[T0-WELLNESS] Final wellness shape={df_well.shape}, "
            f"columns={df_well.columns.tolist()}"
        )

    return df_well



def fetch_activities_chunked(
    athlete_id,
    oldest,
    newest,
    headers,
    context=None,
    from_cache=None,
    max_retries=2,
):
    """
    Adaptive and retryable chunked fetch for activities.

    - Season mode → single 90-day lightweight call (/activities_t0light)
    - Weekly mode → chunked full fetch (/activities)
    """

    # =================================================
    # ✅ CACHE PATH (Cloudflare / prefetched)
    # =================================================
    if from_cache is not None:
        df = pd.DataFrame(from_cache)
        debug(context, f"[T0] Loaded cached activities ({len(df)} rows)")
        return df

    # =================================================
    # 🌐 FETCH PATH (Local / orchestrated)
    # =================================================

    # --- Determine mode (authoritative) -----------------
    light_mode = bool(context.get("force_light", False))

    if light_mode:
        debug(context, "🧩 Tier-0: forced light dataset (90-day)")
    else:
        debug(context, "🧩 Tier-0: forced full dataset (7-day)")


    total_days = (newest - oldest).days #+ 1
    est_payload_acts = estimate_payload_size(total_days, "activities")

    # --- Chunking strategy -----------------------------
    if light_mode:
        act_chunk_days = total_days
        debug(context, f"[T0] Lightweight fetch: single call for {total_days} days")
    else:
        act_chunk_days = 7 if est_payload_acts < 200000 else 3
        debug(
            context,
            f"[T0] Full fetch: {total_days} days → "
            f"{int(np.ceil(total_days / act_chunk_days))} chunks"
        )

    df_activities_list = []

    # --- Fetch loop ------------------------------------
    for meta_attempt in range(max_retries + 1):
        try:
            for offset in range(0, total_days, act_chunk_days):
                chunk_start = oldest + timedelta(days=offset)
                chunk_end = min(
                    newest,
                    chunk_start + timedelta(days=act_chunk_days)
                ) - timedelta(seconds=1)

                if light_mode:
                    acts_url = (
                        f"{INTERVALS_API}/athlete/{athlete_id}/activities_t0light?"
                        f"oldest={chunk_start:%Y-%m-%d}&newest={chunk_end:%Y-%m-%d}"
                        "&fields=id,name,type,sport_type,start_date_local,distance,moving_time,icu_training_load,icu_atl,icu_ctl,icu_intensity,average_heartrate,VO2MaxGarmin,HrtLndLt1,HrtLndLt1p,icu_pm_w_prime,icu_max_wbal_depletion,icu_joules_above_ftp,decoupling,icu_w_prime,icu_rolling_w_prime,icu_efficiency_factor,icu_variability_index,polarization_index"
                    )
                else:
                    acts_url = (
                        f"{INTERVALS_API}/athlete/{athlete_id}/activities?"
                        f"oldest={chunk_start:%Y-%m-%d}&newest={chunk_end:%Y-%m-%d}"
                    )

                debug(context, f"[T0-FETCH] → {acts_url}")

                acts_resp = fetch_with_retry(acts_url, headers)
                if acts_resp.status_code != 200:
                    raise AuditHalt(
                        f"❌ Failed to fetch activities ({acts_resp.status_code}) → "
                        f"{acts_resp.text[:200]}"
                    )

                payload = acts_resp.json()
                if not isinstance(payload, list) or not payload:
                    continue

                # Normalize icu_training_load naming
                if "icu_training_load_data" in payload[0] and "icu_training_load" not in payload[0]:
                    for r in payload:
                        r["icu_training_load"] = r.pop("icu_training_load_data")

                # Safe normalization
                try:
                    df_chunk = pd.json_normalize(payload, max_level=1)
                except Exception as e:
                    debug(context, f"[T0] json_normalize failed → {e}")

                    def flatten_dict(d):
                        flat = {}
                        for k, v in d.items():
                            if isinstance(v, dict):
                                for sk, sv in v.items():
                                    flat[f"{k}_{sk}"] = sv
                            else:
                                flat[k] = v
                        return flat

                    df_chunk = pd.DataFrame([flatten_dict(r) for r in payload])

                if not df_chunk.empty:
                    df_activities_list.append(df_chunk)

                if light_mode:
                    break

            break

        except Exception as e:
            debug(context, f"[T0-FETCH-RETRY] Attempt {meta_attempt + 1} failed: {e}")
            if meta_attempt == max_retries:
                raise AuditHalt(
                    f"❌ Activities fetch failed after {max_retries + 1} attempts: {e}"
                )

    if not df_activities_list:
        debug(context, "⚠ No activity data returned")
        return pd.DataFrame()

    # =================================================
    # 🧹 MERGE + NORMALISE
    # =================================================
    df_activities = pd.concat(df_activities_list, ignore_index=True)

    # --- 🩹 FIX: De-stringify nested zone JSONs coming from Cloudflare ---
    import json, ast

    def safe_eval_zones(x):
        if isinstance(x, str):
            try:
                return json.loads(x)
            except Exception:
                try:
                    return ast.literal_eval(x)
                except Exception:
                    return None
        return x

    for col in ["icu_zone_times", "icu_hr_zone_times", "pace_zone_times"]:
        if col in df_activities.columns:
            df_activities[col] = df_activities[col].apply(safe_eval_zones)
            sample_type = type(df_activities["icu_zone_times"].iloc[0])
    debug(context, f"[T0-FIX] icu_zone_times type after patch → {sample_type}")


    if "id" in df_activities.columns:
        before = len(df_activities)
        df_activities.drop_duplicates(subset=["id"], inplace=True)
        debug(context, f"[T0] Deduplicated {before - len(df_activities)} activities")

    # --- Time normalisation ----------------------------
    if "moving_time" in df_activities.columns:
        if df_activities["moving_time"].max() < 1000:
            df_activities["moving_time"] *= 3600

    tz = context.get("timezone", "Europe/Zurich")
    if "start_date" in df_activities.columns:
        df_activities["start_date_local"] = (
            pd.to_datetime(df_activities["start_date"], utc=True, errors="coerce")
            .dt.tz_convert(tz)
        )
    elif "start_date_local" in df_activities.columns:
        df_activities["start_date_local"] = pd.to_datetime(
            df_activities["start_date_local"], errors="coerce"
        )

    df_activities["date"] = df_activities["start_date_local"].dt.date
    df_activities["origin"] = "event"

    # =================================================
    # ✅ ZONE EXPANSION — FULL MODE ONLY
    # =================================================
    if not light_mode:
        from audit_core.tier0_pre_audit import expand_zones

        df_activities = expand_zones(df_activities, "icu_zone_times", "power")
        df_activities = expand_zones(df_activities, "icu_hr_zone_times", "hr")
        df_activities = expand_zones(df_activities, "pace_zone_times", "pace")

        debug(context, "[T0] Zone columns expanded (full dataset)")

    # =================================================
    # ✅ FINAL
    # =================================================
    # --- Diagnostics ---
    total_tss = df_activities["icu_training_load"].sum() if "icu_training_load" in df_activities else 0
    total_time = df_activities["moving_time"].sum() / 3600 if "moving_time" in df_activities else 0
    debug(context, f"[T0] Diagnostics → Σ(TSS)={total_tss:.1f}, Σ(Time)={total_time:.2f}h")
    debug(
        context,
        f"[T0] Completed {'light' if light_mode else 'full'} fetch → "
        f"{len(df_activities)} rows"
    )

    # 🔒 CRITICAL: persist canonical dataset for Tier-0 re-entry / Tier-1
    if context is not None:
        context["df_master"] = df_activities.copy()
        context["df_raw_activities"] = df_activities.copy()

    # =================================================
    # 🔎 DEBUG: LIGHT DATASET COLUMN AUDIT (AUTHORITATIVE)
    # =================================================
    if light_mode:
        debug(
            context,
            "[T0-LIGHT-COLS] rows=%s cols=%s missing=%s"
            % (
                len(df_activities),
                list(df_activities.columns),
                [c for c in ["HrtLndLt1", "HrtLndLt1p"] if c not in df_activities.columns],
            )
        )

        for c in ["HrtLndLt1", "HrtLndLt1p"]:
            if c in df_activities.columns:
                debug(
                    context,
                    f"[T0-LIGHT-LACTATE] {c} non-null="
                    f"{df_activities[c].notna().sum()}/{len(df_activities)}"
                )


    return df_activities




# FETCH ATHLETE PROFILE
def fetch_athlete_profile(headers, from_cache=None, context=None):
    """Fetch and normalize the athlete profile via OAuth2 OR prefetched cache."""

    context = context or {}
    athlete = None

    # -------------------------------------------------
    # ✅ CACHE PATH (only if VALID athlete exists)
    # -------------------------------------------------
    if (
        isinstance(from_cache, dict)
        and isinstance(from_cache.get("athlete"), dict)
        and from_cache["athlete"].get("id")
    ):
        debug(context, "[T0] Using cached athlete profile")
        athlete = from_cache["athlete"]

    # -------------------------------------------------
    # 🌐 FETCH PATH (fallback if cache invalid or empty)
    # -------------------------------------------------
    if athlete is None:
        profile_url = f"{INTERVALS_API}/athlete/0"
        debug(context, f"[T0] Fetching athlete profile via OAuth2: {profile_url}")

        profile_resp = fetch_with_retry(profile_url, headers)
        if profile_resp.status_code != 200:
            raise AuditHalt(
                f"❌ Failed to fetch athlete profile ({profile_resp.status_code}) → "
                f"{profile_resp.text[:200]}"
            )

        profile_json = profile_resp.json()
        athlete = profile_json.get("athlete", profile_json)
    
    # -------------------------------------------------
    # 🔒 COMMON NORMALISATION (ALWAYS RUNS)
    # -------------------------------------------------
    if not isinstance(athlete, dict):
        raise AuditHalt("❌ Invalid athlete profile format — expected dictionary payload")

    # Default ID handling
    if athlete.get("id") in [None, "", "unknown"]:
        debug(context, "⚠️ No athlete.id found — assigning default ID 0 (current athlete).")
        athlete["id"] = 0

    # Reject invalid sources
    if athlete.get("source") in ["mock", "cache", "sandbox"]:
        raise AuditHalt("❌ Tier-0 halted: invalid data origin (mock/cache/sandbox)")

    # -------------------------------------------------
    # Timezone (MUST BE ON ATHLETE ITSELF)
    # -------------------------------------------------
    tz = athlete.get("timezone")
    if not isinstance(tz, str) or len(tz) < 3:
        tz = "Europe/Zurich"
        athlete["timezone"] = tz   # 🔑 THIS LINE IS THE FIX

    context["timezone"] = tz

    # -------------------------------------------------
    # 🧠 FRAMEWORK PROFILE MAPPING (THE FIX)
    # -------------------------------------------------
    from athlete_profile import map_icu_athlete_to_profile

    merged_profile = map_icu_athlete_to_profile(athlete)

    # -------------------------------------------------
    # 📦 CONTEXT EXPORTS (STRICT ROLES)
    # -------------------------------------------------
    context["athlete_raw"] = athlete          # 🔒 raw ICU athlete (timezone lives here)
    context["athlete"] = context["athlete_raw"]  # 🔑 canonical view for rest of pipeline
    context["athleteProfile"] = merged_profile

    context["athleteIdentity"] = {
        "id": athlete.get("id"),
        "name": athlete.get("name"),
        "profile_medium": athlete.get("profile_medium"),
        "city": athlete.get("city"),
        "state": athlete.get("state"),
        "country": athlete.get("country"),
        "timezone": athlete.get("timezone"),
        "sex": athlete.get("sex"),
        "bio": athlete.get("bio"),
        "website": athlete.get("website"),
        "email": athlete.get("email"),
    }

    debug(
        context,
        f"[T0] Athlete profile ready — id={athlete['id']} name={athlete.get('name')}"
    )
    # --- Log context after updates ---
    debug(context, f"[DEBUG-ATHLETE] sample type={type(context.get('athlete'))} content={str(context.get('athlete'))[:100]}")

    return athlete, context

def fetch_power_curves(headers, context=None, from_cache=None):
    """
    Fetch and normalize the ESPE/FRDM power-curve dataset.

    Direct/local execution path:
        Ride: previous, current, current-kj0, current-kj1
        Run:  previous, current

    Cloudflare-prefetched data is already normalized by app.py and
    remains authoritative when supplied through from_cache.
    """

    context = context or {}

    # =================================================
    # CACHE PATH — already normalized by app.py
    # =================================================
    if from_cache is not None:
        debug(context, "[T0] Loaded cached power_curve dataset")
        return from_cache

    athlete_id = context.get("athlete", {}).get("id", 0)
    curve_string = context.get("espe_curves") or ""
    pm_type = "FFT_CURVES"

    normal_curve_ids = [
        curve_id.strip()
        for curve_id in str(curve_string).split(",")
        if curve_id.strip()
    ]

    if not normal_curve_ids:
        debug(context, "[T0] ⚠ No ESPE curve identifiers configured")
        return {}

    current_curve_id = normal_curve_ids[-1]

    SPORTS = ["Ride", "Run"]
    normalized = {}

    ANCHOR_SECONDS = {
        "5s": 5,
        "1m": 60,
        "5m": 300,
        "20m": 1200,
        "60m": 3600,
    }

    def extract_anchor(block, seconds, allow_closest=True):
        if not isinstance(block, dict):
            return None

        secs = block.get("secs") or []
        vals = block.get("values") or []
        acts = block.get("activity_id") or []

        if not isinstance(secs, list) or not isinstance(vals, list):
            return None

        if not secs or not vals:
            return None

        try:
            idx = secs.index(seconds)
        except ValueError:
            if not allow_closest:
                return None

            idx = min(
                range(len(secs)),
                key=lambda i: abs(secs[i] - seconds)
            )

        if idx >= len(vals):
            return None

        power = vals[idx]
        activity_id = (
            acts[idx]
            if isinstance(acts, list) and idx < len(acts)
            else None
        )

        if activity_id and not str(activity_id).startswith("i"):
            activity_id = f"i{activity_id}"

        return {
            "power": power,
            "activity_id": activity_id,
        }

    def extract_anchors(block, allow_closest=True):
        return {
            name: extract_anchor(
                block,
                seconds,
                allow_closest=allow_closest
            )
            for name, seconds in ANCHOR_SECONDS.items()
        }

    def extract_fft_model(block):
        if not isinstance(block, dict):
            return None

        fft_model = next(
            (
                model
                for model in (block.get("powerModels") or [])
                if model.get("type") == "FFT_CURVES"
            ),
            None
        )

        if not fft_model:
            return None

        return {
            "source": "FFT_CURVES",
            "cp": fft_model.get("criticalPower"),
            "w_prime": fft_model.get("wPrime"),
            "pmax": fft_model.get("pMax"),
            "ftp": fft_model.get("ftp"),
        }

    def fatigue_slot(curve_id):
        curve_id = str(curve_id or "")

        if curve_id.endswith("-kj0"):
            return "kj0"

        if curve_id.endswith("-kj1"):
            return "kj1"

        return None

    for sport in SPORTS:

        requested_curve_ids = list(normal_curve_ids)

        if sport == "Ride":
            requested_curve_ids.extend([
                f"{current_curve_id}-kj0",
                f"{current_curve_id}-kj1",
            ])

        requested_curves = ",".join(requested_curve_ids)

        url = (
            f"{INTERVALS_API}/athlete/{athlete_id}/power-curves-ext"
            f"?type={sport}"
            f"&curves={requested_curves}"
            f"&pmType={pm_type}"
        )

        debug(
            context,
            "[T0] Fetching power curves → "
            f"sport={sport} curves={requested_curve_ids}"
        )

        resp = fetch_with_retry(url, headers)

        if resp.status_code != 200:
            debug(
                context,
                f"[T0] ⚠ Power curve fetch failed for {sport}"
            )
            continue

        payload = resp.json()
        curve_list = payload.get("list") or []

        debug(
            context,
            "[T0] Power curve dataset retrieved → "
            f"sport={sport} count={len(curve_list)}"
        )

        if not isinstance(curve_list, list) or not curve_list:
            debug(
                context,
                f"[T0] ⚠ Empty power_curve payload for {sport}"
            )
            continue

        normal_curve_list = [
            block
            for block in curve_list
            if (
                isinstance(block, dict)
                and fatigue_slot(block.get("id")) is None
            )
        ]

        if not normal_curve_list:
            debug(
                context,
                f"[T0] ⚠ No normal power curves returned for {sport}"
            )
            continue

        normal_curve_list.sort(
            key=lambda block: (
                str(block.get("end_date_local") or ""),
                str(block.get("start_date_local") or ""),
            )
        )

        if len(normal_curve_list) == 1:
            debug(
                context,
                f"[T0] ⚠ Single normal window only for {sport}"
            )
            prev = {}
            curr = normal_curve_list[0]
        else:
            prev = normal_curve_list[-2]
            curr = normal_curve_list[-1]

        normalized_current_curve_id = str(curr.get("id") or "")
        previous_curve_id = str(prev.get("id") or "")

        sport_block = {
            "previous": extract_anchors(
                prev,
                allow_closest=True
            ),
            "current": extract_anchors(
                curr,
                allow_closest=True
            ),
            "window_days": (
                curr.get("days")
                or prev.get("days")
            ),
            "curve_ids": {
                "previous": previous_curve_id or None,
                "current": normalized_current_curve_id or None,
            },
            "curve_regression": {
                "slope": (
                    (curr.get("mapPlot") or {}).get("poSlope")
                ),
                "r2": (
                    (curr.get("mapPlot") or {}).get("poR2")
                ),
            },
        }

        current_fft_model = extract_fft_model(curr)

        if current_fft_model:
            sport_block["models"] = current_fft_model

        # --------------------------------------------
        # Ride fatigued curves
        # --------------------------------------------
        if sport == "Ride":
            fatigued_current = {}

            for fatigue_curve in curve_list:
                if not isinstance(fatigue_curve, dict):
                    continue

                curve_id = str(fatigue_curve.get("id") or "")
                slot = fatigue_slot(curve_id)

                if slot is None:
                    continue

                suffix = f"-{slot}"
                base_curve_id = curve_id[:-len(suffix)]

                if (
                    not normalized_current_curve_id
                    or base_curve_id != normalized_current_curve_id
                ):
                    debug(
                        context,
                        "[T0] Ignoring unmatched fatigued curve "
                        f"id={curve_id} "
                        f"current={normalized_current_curve_id}"
                    )
                    continue

                fatigue_map_plot = (
                    fatigue_curve.get("mapPlot") or {}
                )

                fatigued_current[slot] = {
                    "source_slot": slot,
                    "curve_id": curve_id,
                    "base_curve_id": base_curve_id,
                    "after_kj": fatigue_curve.get("after_kj"),
                    "label": fatigue_curve.get("label"),
                    "start_date_local": (
                        fatigue_curve.get("start_date_local")
                    ),
                    "end_date_local": (
                        fatigue_curve.get("end_date_local")
                    ),
                    "window_days": fatigue_curve.get("days"),
                    "anchors": extract_anchors(
                        fatigue_curve,
                        allow_closest=False
                    ),
                    "models": (
                        extract_fft_model(fatigue_curve) or {}
                    ),
                    "curve_regression": {
                        "slope": fatigue_map_plot.get("poSlope"),
                        "r2": fatigue_map_plot.get("poR2"),
                    },
                }

            sport_block["fatigued"] = {
                "current": fatigued_current
            }

        normalized[sport] = sport_block

        if not sport_block["current"].get("5m"):
            debug(
                context,
                f"[T0] ESPE missing 5m anchor for {sport}"
            )

        debug(
            context,
            f"[T0] Normalized power_curve anchors → {sport}",
            list(sport_block["current"].keys())
        )

        if sport == "Ride":
            debug(
                context,
                "[T0] Fatigued Ride curves normalized → "
                f"{list(sport_block['fatigued']['current'].keys())}"
            )

    return normalized

def run_tier0_pre_audit(start: str, end: str, context: dict):
    """Tier-0: OAuth-only Pre-audit fetch chain with adaptive chunking and meta-retry."""
   # 🔒 CANONICAL: report_type must always exist
    assert "report_type" in context, "FATAL: report_type missing before Tier-0"
    report_type = context["report_type"].lower()
    debug(context, f"[T0] report_type resolved → {report_type}")
    headers = {}
    # 🔒 ALWAYS initialise athlete time context FIRST
    set_time_context(context)
    # 🧩 Enforce CLI explicit date range (authoritative override)
    if (
        "range" in context
        and "light_start" in context["range"]
        and "light_end" in context["range"]
    ):
        start = str(pd.to_datetime(context["range"]["light_start"]).date())
        end = str(pd.to_datetime(context["range"]["light_end"]).date())
        debug(context, f"[T0-FORCE] CLI override enforced → start={start} end={end}")

    # If Railway has a token, send it; otherwise rely on Worker env.ICU_OAUTH
    if ICU_TOKEN and ICU_TOKEN.strip():
        headers["Authorization"] = f"Bearer {ICU_TOKEN.strip()}"
    else:
        # Only warn if we're using the Worker proxy
        if "workers.dev" in INTERVALS_API or "clive-a5a.workers.dev" in INTERVALS_API:
            debug(context, "[T0] ICU_OAUTH missing on Railway — relying on Worker-held token")
        else:
            raise RuntimeError("Missing Intervals.icu OAuth token. Set ICU_OAUTH env var.")

    # ============================================================
    # Tier-0 LIGHT DATASET (90d) — FETCH OR PREFETCH (IDENTICAL)
    # ============================================================

    # Ensure df_light always exists (canonical invariants)
    df_light = pd.DataFrame()
    df_acts = pd.DataFrame()
    df_light_slice = pd.DataFrame()

    # --- REQUIRED: auth header + report type ---
    headers = {"Authorization": f"Bearer {ICU_TOKEN}"}
    context["report_type"] = (context.get("report_type") or "weekly").lower()



    # ============================================================
    # 🔑 AUTHORITATIVE LIGHT SOURCE DECISION
    # ============================================================
    if context.get("prefetch_done", False):

        debug(context, "[T0-LIGHT] Prefetch already completed — skipping redundant lightweight call.")

        # --------------------------------------------------------
        # 🔧 PREFETCH → df_light NORMALISATION (MANDATORY)
        # --------------------------------------------------------
        pref_light = context.get("prefetched", {}).get("light")

        if not isinstance(pref_light, list) or not pref_light:
            raise AuditHalt("❌ Prefetch path selected but prefetched['light'] missing or empty")

        debug(context, "[T0-FIX] Building df_light from prefetched light dataset")

        df_light = pd.DataFrame(pref_light)

        if "start_date_local" not in df_light.columns:
            raise AuditHalt("❌ Prefetched light dataset missing 'start_date_local'")

        df_light["start_date_local"] = pd.to_datetime(
            df_light["start_date_local"], errors="coerce"
        ).dt.tz_localize(None)

        context["df_light"] = df_light.copy()
        context["df_light_full"] = df_light.copy()
        context["activities_light"] = df_light.copy()

    else:
        
        # --------------------------------------------------------
        # 🌐 FETCH LIGHTWEIGHT DATASET (LOCAL / ORCHESTRATED)
        # --------------------------------------------------------
        context["prefetch_done"] = True

        fields = (
            "id,name,type,sport_type,start_date_local,distance,moving_time,icu_training_load,icu_atl,icu_ctl,icu_intensity,average_heartrate,VO2MaxGarmin,HrtLndLt1,HrtLndLt1p,icu_pm_w_prime,icu_max_wbal_depletion,icu_joules_above_ftp,decoupling,icu_w_prime,icu_rolling_w_prime,icu_efficiency_factor,icu_variability_index,polarization_index"
        )

        # 🔧 Determine baseline range (default: from controller start/end)
        oldest = pd.to_datetime(start).strftime("%Y-%m-%d")
        newest = pd.to_datetime(end).strftime("%Y-%m-%d")

        range_cfg = context.get("range", {})

        # ✅ Respect user/CLI-specified override if present
        if range_cfg.get("light_start") and range_cfg.get("light_end"):
            oldest = pd.to_datetime(range_cfg["light_start"]).strftime("%Y-%m-%d")
            newest = pd.to_datetime(range_cfg["light_end"]).strftime("%Y-%m-%d")
            debug(context, f"[T0] ✅ Preserving upstream range override → {oldest} → {newest}")

        # 🚀 Only apply force_light if NO explicit CLI/custom range was given
        elif context.get("force_light", False):
            newest_date = context["athlete_today"].date()
            oldest_date = newest_date - timedelta(days=range_cfg.get("lightDays", 90))
            oldest = oldest_date.strftime("%Y-%m-%d")
            newest = newest_date.strftime("%Y-%m-%d")
            debug(context, f"[T0-FORCE-LIGHT] Overriding controller range → {oldest} → {newest}")

        else:
            debug(context, f"[T0] Using controller-provided window → {oldest} → {newest}")

        debug(context, f"[T0-LIGHT] Using range oldest={oldest} newest={newest}")

        light_url = (
            f"{INTERVALS_API}/athlete/0/activities_t0light?"
            f"oldest={oldest}&newest={newest}&fields={fields}"
        )

        debug(context, f"[T0-LIGHT] Fetching lightweight dataset → {light_url}")

        resp = fetch_with_retry(light_url, headers)
        if resp.status_code != 200:
            raise AuditHalt(
                f"❌ Tier-0 lightweight fetch failed → {resp.status_code}: {resp.text[:200]}"
            )

        payload = resp.json()
        if not payload:
            raise AuditHalt("❌ Tier-0 lightweight fetch returned no data")

        df_light = pd.DataFrame(payload)

        # ------------------------------------------------------------
        # 🔒 Strip STRAVA API stub rows (local canonical path)
        # ------------------------------------------------------------
        if "_note" in df_light.columns:
            strava_note_text = "STRAVA activities are not available via the API"

            before = len(df_light)

            df_light = df_light[
                df_light["_note"].fillna("") != strava_note_text
            ].copy()

            removed = before - len(df_light)

            if removed > 0:
                debug(context, f"[T0] Removed {removed} STRAVA stub rows (local canonical)")

        if "start_date_local" not in df_light.columns:
            raise AuditHalt("❌ Lightweight fetch missing 'start_date_local'")

        df_light["start_date_local"] = pd.to_datetime(
            df_light["start_date_local"], errors="coerce"
        ).dt.tz_localize(None)

        context["df_light"] = df_light.copy()
        context["df_light_full"] = df_light.copy()
        context["activities_light"] = df_light.copy()

        debug(context, f"[T0-LIGHT] Retrieved {len(df_light)} activities")
        debug(
            context,
            "[T0-LIGHT-COLS] rows=%s cols=%s missing_lactate=%s"
            % (
                len(df_light),
                list(df_light.columns),
                [c for c in ["HrtLndLt1", "HrtLndLt1p"] if c not in df_light.columns],
            )
        )

    # ============================================================
    # 🧩 Inject activities_full for Tier-2 enrichment
    # ============================================================
    if "activities_full" not in context:
        try:
            context["activities_full"] = df_light.to_dict(orient="records")
            debug(
                context,
                f"[T0-PATCH] Injected df_light as activities_full for Tier-2 enrichment "
                f"({len(df_light)} rows, {len(df_light.columns)} columns)"
            )
        except Exception as e:
            debug(context, f"[T0-PATCH] Failed to inject df_light as activities_full: {e}")

    # ============================================================
    # 🧮 SLICE LOGIC — IDENTICAL FOR FETCH + PREFETCH
    # ============================================================

    report_type = context["report_type"]

    if report_type == "season":
        slice_days = 90
    else:
        slice_days = 7

    window_end_exclusive = pd.to_datetime(end) + pd.Timedelta(days=1)
    window_start = pd.to_datetime(end) - pd.Timedelta(days=slice_days - 1)

    if report_type == "season":
        df_light_slice = df_light.copy()
        debug(context, f"[T0-SLICE] Season mode → using full {len(df_light)} rows")
    else:
        df_light_slice = df_light[
            (df_light["start_date_local"] >= window_start)
            & (df_light["start_date_local"] < window_end_exclusive)
        ].copy()

        debug(
            context,
            f"[T0-SLICE] {slice_days}-day window {window_start.date()} → "
            f"{window_end_exclusive.date()} ({len(df_light_slice)} rows)"
        )

    # --- Deduplicate ---
    if "id" in df_light_slice.columns:
        df_light_slice = df_light_slice.drop_duplicates(subset=["id"], keep="first")

    # --- Numeric coercion ---
    for col in ("moving_time", "distance", "icu_training_load"):
        if col in df_light_slice.columns:
            df_light_slice[col] = pd.to_numeric(df_light_slice[col], errors="coerce").fillna(0)

    context["df_light_slice"] = df_light_slice.copy()

    # ============================================================
    # 📦 SNAPSHOT + TOTALS (WEEKLY / SUMMARY CONTEXT)
    # ============================================================

    # 🔒 Ensure required columns exist (local mode safety)
    for col in ["moving_time", "distance", "icu_training_load"]:
        if col not in df_light_slice.columns:
            df_light_slice[col] = 0

    context["snapshot_7d_json"] = df_light_slice.to_json(orient="records")

    context["tier0_snapshotTotals_7d"] = {
        "hours": round(df_light_slice["moving_time"].sum() / 3600, 2),
        "distance": round(df_light_slice["distance"].sum() / 1000, 1),
        "tss": int(df_light_slice["icu_training_load"].sum()),
        "count": len(df_light_slice),
        "start": str(window_start.date()),
        "end": str(window_end_exclusive.date()),
    }

    debug(
        context,
        f"🧭 Tier-0 weekly snapshot = "
        f"{context['tier0_snapshotTotals_7d']['hours']}h | "
        f"{context['tier0_snapshotTotals_7d']['tss']} TSS | "
        f"{context['tier0_snapshotTotals_7d']['count']} events"
    )


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
    athlete, context = resolve_dataset(
        "athlete",
        lambda from_cache, context: fetch_athlete_profile(headers, context)
            if from_cache is None else (from_cache, context),
        context,
    )
    # 🔒 Re-apply time context now that athlete timezone is known
    set_time_context(context)
    debug(context, f"[CHECK] athlete name = {context.get('athleteProfile', {}).get('name')}")

    # --- Step 2: Define canonical date window (metadata only) ---
    def fmt_date(x):
        """Safe formatter for date/timestamp objects."""
        try:
            if hasattr(x, "date"):
                return x.date()
            return x
        except Exception:
            return x

    if (
        "range" in context
        and "light_start" in context["range"]
        and "light_end" in context["range"]
    ):
        mode = "custom"
        oldest = pd.to_datetime(context["range"]["light_start"])
        newest = pd.to_datetime(context["range"]["light_end"])
        debug(context, f"[T0-FIX] 🧭 Using explicit user range {fmt_date(oldest)} → {fmt_date(newest)}")

    elif context.get("report_type", "").lower() == "season":
        mode = "season"
        newest = context["athlete_today"]
        oldest = newest - pd.Timedelta(days=90)
        debug(context, f"🧩 Tier-0: defining 90-day window context for season mode (no data reslice).")

    else:
        mode, oldest, newest = resolve_report_trigger("weekly", context)
        debug(context, f"[T0-FIX] Defaulting to weekly/rolling window {fmt_date(oldest)} → {fmt_date(newest)}")

    context.update({"report_mode": mode, "window_start": oldest, "window_end": newest})

    # --- POWER CURVES WINDOW

    ESPE_WINDOW = 84

    end_date = pd.to_datetime(context.get("window_end")).date()

    curr_start = end_date - timedelta(days=ESPE_WINDOW)
    prev_start = end_date - timedelta(days=ESPE_WINDOW * 2)
    prev_end = curr_start

    curves = f"r.{prev_start}.{prev_end},r.{curr_start}.{end_date}"

    context["espe_curves"] = curves

    # --- Step 3: Fetch activities (canonical Tier-0 behaviour) ---
    report_type = str(context.get("report_type", "")).lower()
    debug(context, f"[T0-FETCH] Canonical activity fetch for report_type={report_type}")

    # Tier-0 invariant:
    # - ALWAYS fetch full 7-day detailed dataset
    # - NEVER downgrade based on report_type
    # - Season vs Weekly differences are handled later (Tier-2 scope)

    if "df_master" not in context:
        df_full = resolve_dataset(
            "full",
            lambda from_cache, context: fetch_activities_chunked(
                athlete["id"], oldest, newest, headers, context, from_cache=from_cache
            ),
            context,
        )

        df_activities = df_full.copy()
        context["df_master"] = df_activities.copy()

        debug(context, f"[T0-FETCH] Full 7-day fetch complete: {len(df_activities)} activities.")
    else:
        df_activities = context["df_master"].copy()
        debug(context, "[T0-FETCH] df_master already present — reused canonical dataset")

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

        elif report_type == "summary":
            # SUMMARY → snapshot uses recent 7-day FULL dataset (context window)
            source_df = df_activities
            debug(context, f"[T0] Summary mode → using FULL 7-day context dataset ({len(source_df)} rows)")

        else:
            # fallback default (should not occur)
            source_df = df_light_slice
            debug(context, f"[T0] Unknown report_type='{report_type}' → defaulting to LIGHT dataset ({len(source_df)} rows)")


        # ------------------------------------------------------------------
        # 🛡️ Tier-0 Safety Guard — ensure baseline columns exist & numeric
        # ------------------------------------------------------------------
        required_cols = ["start_date_local", "moving_time", "icu_training_load", "type"]
        for col in required_cols:
            if col not in source_df.columns:
                default_val = 0 if col in ["moving_time", "icu_training_load"] else ""
                debug(context, f"[T0-FIX] Column '{col}' missing — adding default {default_val}")
                source_df[col] = default_val

        # Normalize numeric columns
        for col in ["moving_time", "icu_training_load"]:
            if col in source_df.columns:
                source_df[col] = pd.to_numeric(source_df[col], errors="coerce").fillna(0)

        # Re-check emptiness after coercion
        if not source_df.empty:
            debug(
                context,
                f"[T0-FIX] source_df validated — rows={len(source_df)}, "
                f"ΣTSS={source_df['icu_training_load'].sum():.1f}, "
                f"Σh={source_df['moving_time'].sum()/3600:.2f}"
            )

        # --- Validate before serializing ---
        report_type = str(report_type).lower()

        requires_snapshot = report_type in ["weekly", "season", "wellness" ]

        if requires_snapshot:

            if source_df.empty:
                debug(
                    context,
                    f"[T0-GUARD] snapshot source empty — injecting safe empty frame "
                    f"(report_type={report_type})"
                )

                # Inject minimal schema-safe empty frame
                source_df = pd.DataFrame({
                    "start_date_local": [],
                    "moving_time": [],
                    "icu_training_load": [],
                    "type": [],
                })

            if "type" not in source_df.columns:
                debug(
                    context,
                    "[T0-GUARD] 'type' column missing — injecting default empty string"
                )
                source_df["type"] = ""



    # --- Serialize for Tier-1 ---
    # --- Fallback handling for season mode ---
    if "source_df" not in locals() or source_df is None:
        debug(context, "[T0-FIX] source_df undefined — using df_light as fallback (season mode).")
        source_df = df_light.copy() if "df_light" in locals() else pd.DataFrame()

    # ------------------------------------------------------------
    # Snapshot export — ALWAYS (Tier-1 invariant)
    # ------------------------------------------------------------

    # 🔒 Snapshot always comes from resolved source_df
    snapshot_df = source_df.copy() if isinstance(source_df, pd.DataFrame) else pd.DataFrame()

    context["snapshot_7d_json"] = snapshot_df.to_json(orient="records")

    debug(
        context,
        f"[T0] snapshot_7d_json set ({context.get('report_type')}, {len(snapshot_df)} rows)"
    )

    # --- Step 4: Fetch wellness with adaptive chunking + meta-retry ---
    wellness_days = context.get("range", {}).get("wellnessDays", 42)
    today = context["athlete_today"]
    wellness_newest = today
    wellness_oldest = wellness_newest - pd.Timedelta(days=wellness_days)

    debug(context, f"[T0] Fetching wellness for {wellness_days} days → {wellness_oldest} → {wellness_newest}")

    wellness = resolve_dataset(
        "wellness",
        lambda from_cache, context: fetch_wellness_chunked(
            athlete["id"],
            wellness_oldest,
            wellness_newest,
            headers,
            context,
            from_cache=from_cache,
        ),
        context,
    )

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
        debug(
            context,
            f"[DEBUG] wellness columns (sample {min(10, len(wellness.columns))}/{len(wellness.columns)}): "
            f"{wellness.columns.tolist()[:50]}"
        )
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

    # --- Fetch power curves (ESPE source) ---
    power_curve = resolve_dataset(
        "power_curve",
        lambda from_cache, context: fetch_power_curves(headers, context, from_cache),
        context,
    )

    context["power_curve"] = power_curve

    # ------------------------------------------------------------
    # PRESERVE REAL 90-DAY DATASET (for extended metrics)
    # ------------------------------------------------------------

    # 90-day lightweight dataset (authoritative for season + metrics)
    if "df_light_full" in context and isinstance(context["df_light_full"], pd.DataFrame):
        context["df_light"] = context["df_light_full"].copy()
        context["activities_light"] = context["df_light_full"].copy()
    else:
        context["df_light"] = df_light.copy() if isinstance(df_light, pd.DataFrame) else pd.DataFrame()
        context["activities_light"] = context["df_light"]

    # Always preserve sliced lightweight window (7d or 90d depending on mode)
    context["df_light_slice"] = (
        df_light_slice.copy()
        if isinstance(df_light_slice, pd.DataFrame)
        else pd.DataFrame()
    )

    # ============================================================
    # 🔒 FINAL Tier-1 invariant — snapshot_7d_json MUST be a string
    # ============================================================
    snap = context.get("snapshot_7d_json")

    if not isinstance(snap, str) or not snap.strip():
        if isinstance(context.get("df_light_slice"), pd.DataFrame):
            context["snapshot_7d_json"] = context["df_light_slice"].to_json(orient="records")
            debug(
                context,
                f"[T0-FINAL] snapshot_7d_json forced (string) from df_light_slice "
                f"({len(context['df_light_slice'])} rows)"
            )
        else:
            context["snapshot_7d_json"] = "[]"
            debug(context, "[T0-FINAL] snapshot_7d_json forced to '[]'")

    # ------------------------------------------------------------
    # 🔒 CANONICAL MASTER DATASET (Tier-1 input)
    # ------------------------------------------------------------
    # Only set df_master if it does NOT already exist.
    # Never overwrite canonical state at exit.

    # 🔒 Tier-0 invariant: df_master must already exist and be valid
    if "df_master" not in context:
        raise AuditHalt("Tier-0 invariant violated: df_master missing at exit")

    if not isinstance(context["df_master"], pd.DataFrame):
        raise AuditHalt("Tier-0 invariant violated: df_master is not a DataFrame")

    if context["df_master"].empty:

        light = context.get("activities_light")
        full = context.get("activities_full")

        def is_empty(obj):
            if obj is None:
                return True
            if isinstance(obj, pd.DataFrame):
                return obj.empty
            if isinstance(obj, (list, dict, tuple, set)):
                return len(obj) == 0
            return False

        light_empty = is_empty(light)
        full_empty = is_empty(full)

        if light_empty and full_empty:
            raise AuditHalt(
                "No training activities found. please see https://www.montis.icu/setup.html",
                code="NO_ACTIVITIES_RANGE",
                severity="info"
            )

        # ⚠ DO NOT halt if light exists but full is empty
        # This is valid for summary/wellness reports

#        raise AuditHalt(
#            "Activities were found but none matched the report criteria.",
#            code="ACTIVITIES_FILTERED_OUT",
#            severity="info"
#        )

    # 🔒 Canonical return — only reached if df_master is valid
    return (
        context["df_master"],
        wellness,
        context,
        context.get("auditPartial"),
        context.get("auditFinal"),
    )



# ============================================================
# 🔄 EXPORTED: expand_zones (public helper for zone expansion)
# ============================================================
def expand_zones(df, field, prefix):
    """Public export of the internal expand_zones() used in fetch_activities_chunked()."""
    import numpy as np, pandas as pd, json

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

    if field not in df.columns or df.empty:
        return df

    parsed = df[field].apply(safe_parse)
    max_len = parsed.map(len).max() if not parsed.empty else 0
    if max_len == 0:
        return df

    z = pd.DataFrame(parsed.tolist(), index=df.index)
    z = z.reindex(columns=range(max_len)).fillna(0).astype(float)
    z.columns = [f"{prefix}_z{i+1}" for i in range(max_len)]

    base = df.drop(columns=[field])

    # Only add zone columns that do not already exist
    for col in z.columns:
        if col not in base.columns:
            base[col] = z[col]

    return base


