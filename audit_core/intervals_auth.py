# audit_core/intervals_auth.py — how the engine signs in to Intervals.icu
import base64
import os


def intervals_auth_headers() -> dict:
    """Authorization header for Intervals.icu.

    ICU_OAUTH: an Intervals.icu OAuth access token, sent as Bearer (used first when both are set).
    ICU_API_KEY: your personal API key (Intervals.icu → Settings → Developer Settings), sent as
    Basic auth with the user name API_KEY, as Intervals.icu expects.
    Returns {} when neither is set.
    """
    token = (os.getenv("ICU_OAUTH") or "").strip()
    if token:
        return {"Authorization": f"Bearer {token}"}
    api_key = (os.getenv("ICU_API_KEY") or "").strip()
    if api_key:
        encoded = base64.b64encode(f"API_KEY:{api_key}".encode("utf-8")).decode("ascii")
        return {"Authorization": f"Basic {encoded}"}
    return {}


def intervals_auth_kind() -> str:
    """Which credential is in use, for log lines (never the value)."""
    if (os.getenv("ICU_OAUTH") or "").strip():
        return "OAuth token (ICU_OAUTH)"
    if (os.getenv("ICU_API_KEY") or "").strip():
        return "personal API key (ICU_API_KEY)"
    return "none"
