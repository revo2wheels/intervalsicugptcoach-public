# audit_core/utils.py

import pandas as pd
from audit_core.errors import AuditHalt


def validate_dataset_integrity(df: pd.DataFrame) -> bool:
    """Basic dataset sanity check — ensures no NaNs in critical fields."""
    required = ["moving_time", "icu_training_load"]
    if not all(col in df.columns for col in required):
        raise ValueError(f"Missing required columns in dataset: {required}")
    if df[required].isnull().values.any():
        raise ValueError("Null values detected in dataset integrity check.")
    return True


def validate_wellness_alignment(activity_df: pd.DataFrame, wellness_df: pd.DataFrame) -> bool:
    """Ensure wellness data covers the same date window as activity dataset."""

    # --- Defensive guards ---
    if activity_df is None or activity_df.empty:
        print("⚠ No activity data provided — skipping wellness alignment.")
        return True
    if wellness_df is None or (isinstance(wellness_df, pd.DataFrame) and wellness_df.empty):
        print("⚠ No wellness data provided — skipping wellness alignment.")
        return True

    df = activity_df.copy()
    if "start_date_local" not in df.columns:
        raise AuditHalt("❌ validate_wellness_alignment: start_date_local missing from activity_df")

        # --- Determine activity window ---
    start = pd.to_datetime(df["start_date_local"]).min()
    end = pd.to_datetime(df["start_date_local"]).max()
    print(f"[T1] Wellness alignment window (tz-aware): {start} → {end}")

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
            print("⚠ Wellness data missing date/id column — cannot align.")
            return False

    w_dates = pd.to_datetime(wellness_df["date"], errors="coerce").dropna().sort_values()
    if w_dates.empty:
        print("⚠ Wellness dataset contains no valid dates.")
        return False

    # Convert wellness timestamps to naive dates
    w_start_date = w_dates.min().date()
    w_end_date = w_dates.max().date()
    print(f"[T1] Wellness date range: {w_start_date} → {w_end_date}")

    # --- Compare as naive date objects ---
    if w_start_date > end_date or w_end_date < start_date:
        print(f"⚠ Wellness window misaligned ({w_start_date}–{w_end_date} vs {start_date}–{end_date})")
        return False

    print("✅ Wellness alignment check passed.")
    return True
