# audit_core/utils.py

import pandas as pd
from audit_core.errors import AuditHalt
import sys
import datetime
import os
from zoneinfo import ZoneInfo
from datetime import datetime

# ------------------------------------------------------------
# 🌍 Auto-detect Railway environment (staging vs production)
# ------------------------------------------------------------

# Railway provides:
#   RAILWAY_ENVIRONMENT_NAME=staging
#   RAILWAY_ENVIRONMENT_NAME=production

RAILWAY_ENV = os.getenv("RAILWAY_ENVIRONMENT_NAME", "").lower()

# Explicitly suppress debug in production
#IS_DEBUG_ENV = RAILWAY_ENV != "production"
IS_DEBUG_ENV = True # this enabled both prod and staging but stderr is removed. pass ?debug=true


# ------------------------------------------------------------
# Global state
# ------------------------------------------------------------

RUN_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
GLOBAL_LOGFILE = None
GLOBAL_FILE_HANDLE = None
MAX_STDERR_LINES = 2000
STDERR_COUNT = 0

def set_time_context(context):
    athlete_tz = context.get("timezone") or "UTC"

    try:
        tz = ZoneInfo(athlete_tz)
    except Exception:
        athlete_tz = "UTC"
        tz = ZoneInfo("UTC")

    athlete_now = datetime.now(tz)
    athlete_today = pd.Timestamp(athlete_now).tz_localize(None).normalize()

    context["timezone"] = athlete_tz
    context["athlete_now"] = athlete_now
    context["athlete_today"] = athlete_today

    return context



# ------------------------------------------------------------
# 🔎 Debug Logger (Auto-suppressed in Production)
# ------------------------------------------------------------

def debug(*args):

    global GLOBAL_LOGFILE, GLOBAL_FILE_HANDLE, STDERR_COUNT

    if not IS_DEBUG_ENV:
        return

    try:
        if not args:
            return

        if isinstance(args[0], dict):
            context = args[0]
            msgs = args[1:]
        else:
            context = {}
            msgs = args

        report_type = os.getenv("REPORT_TYPE", "unknown").lower()

        if GLOBAL_LOGFILE is None:
            reports_dir = os.path.join(os.getcwd(), "reports")
            os.makedirs(reports_dir, exist_ok=True)
            GLOBAL_LOGFILE = os.path.join(
                reports_dir,
                f"report_{report_type}_local_prod_debug.log"
            )

        ts = datetime.now().strftime("%H:%M:%S")
        msg = " ".join(str(m) for m in msgs)
        msg_out = f"[{ts}] {msg}"

       
        context.setdefault("debug_trace", []).append(msg_out)

        # stdout/stderr → local terminal only (not Railway)
        if not os.getenv("RAILWAY_ENVIRONMENT_NAME"):
            print(msg_out)

            if STDERR_COUNT < MAX_STDERR_LINES:
                sys.stderr.write(msg_out + "\n")
                sys.stderr.flush()
                STDERR_COUNT += 1

        # persistent debug file
        if GLOBAL_FILE_HANDLE is None:
            GLOBAL_FILE_HANDLE = open(GLOBAL_LOGFILE, "w", encoding="utf-8")

        GLOBAL_FILE_HANDLE.write(msg_out + "\n")
        GLOBAL_FILE_HANDLE.flush()

    except Exception as e:
        sys.stderr.write(f"[debug-failure] {e}\n")
        sys.stderr.flush()


def validate_dataset_integrity(df: pd.DataFrame) -> bool:
    """Basic dataset sanity check — ensures no NaNs in critical fields."""
    required = ["moving_time", "icu_training_load"]
    if not all(col in df.columns for col in required):
        raise ValueError(f"Missing required columns in dataset: {required}")
    if df[required].isnull().values.any():
        raise ValueError("Null values detected in dataset integrity check.")
    return True


def validate_wellness_alignment(activity_df: pd.DataFrame, wellness_df: pd.DataFrame, context=None) -> bool:
    """Ensure wellness data covers the same date window as activity dataset."""

    # --- Defensive guards ---
    if activity_df is None or activity_df.empty:
        debug(context or {}, "⚠ No activity data provided — skipping wellness alignment.")
        return True
    if wellness_df is None or (isinstance(wellness_df, pd.DataFrame) and wellness_df.empty):
        debug(context or {}, "⚠ No wellness data provided — skipping wellness alignment.")
        return True

    df = activity_df.copy()
    if "start_date_local" not in df.columns:
        raise AuditHalt("❌ validate_wellness_alignment: start_date_local missing from activity_df")

        # --- Determine activity window ---
    start = pd.to_datetime(df["start_date_local"]).min()
    end = pd.to_datetime(df["start_date_local"]).max()
    debug(context or {}, f"[T1] Wellness alignment window (tz-aware): {start} → {end}")

    # Convert to naive (date only) for fair comparison
    start_date = start.tz_convert(None).date() if start.tzinfo else start.date()
    end_date = end.tz_convert(None).date() if end.tzinfo else end.date()

    # --- Normalize wellness dates ---
    if isinstance(wellness_df, list):
        wellness_df = pd.DataFrame(wellness_df)

    if "date" not in wellness_df.columns:
        if "id" in wellness_df.columns:
            wellness_df["date"] = pd.to_datetime(wellness_df["id"]).dt.date
        else:
            debug(context or {},"⚠ Wellness data missing date/id column — cannot align.")
            return False

    w_dates = pd.to_datetime(wellness_df["date"], errors="coerce").dropna().sort_values()
    if w_dates.empty:
        debug(context or {}, "⚠ Wellness dataset contains no valid dates.")
        return False

    # Convert wellness timestamps to naive dates
    w_start_date = w_dates.min().date()
    w_end_date = w_dates.max().date()
    debug(context or {}, f"[T1] Wellness date range: {w_start_date} → {w_end_date}")

    # --- Compare as naive date objects ---
    if w_start_date > end_date or w_end_date < start_date:
        debug(context or {}, f"⚠ Wellness window misaligned ({w_start_date}–{w_end_date} vs {start_date}–{end_date})")
        return False

    debug(context or {}, "✅ Wellness alignment check passed.")
    return True

# PREFETCH RESOLUTION
def resolve_prefetched(name, context, fetch_fn=None, **kwargs):
    """
    Generic resolver for any prefetched dataset.
    Mirrors T0 resolve_dataset() pattern but works for any name.
    """
    pre = context.get("prefetched", {})

    # ✅ 1. Use prefetched data if available
    if name in pre and pre[name]:
        debug(context, f"[PREFETCH] Using prefetched '{name}' ({len(pre[name])} records)")
        return pre[name]

    # ✅ 2. Never fetch in prefetched (Railway) mode
    #    (report.py --direct has nothing prefetched and reads Intervals.icu itself)
    if "prefetched" in context and not context.get("direct_intervals"):
        debug(context, f"[PREFETCH] Skipping external fetch for '{name}' (prefetched mode)")
        return []

    # ✅ 3. Fallback to fetch_fn only in local/dev
    if fetch_fn:
        debug(context, f"[PREFETCH] Fetching '{name}' via {fetch_fn.__name__}()")
        return fetch_fn(context, **kwargs)

    # 🚫 Safe default
    debug(context, f"[PREFETCH] No prefetched data or fetch function for '{name}'")
    return []

