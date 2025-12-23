# audit_core/calendar/manager.py
import os, requests

# Base URL for your Cloudflare Worker
WORKER_BASE = os.getenv("CLOUDFLARE_WORKER_BASE", "https://intervalsicugptcoach.clive-a5a.workers.dev")

def _call_worker(path: str, method="POST", payload=None):
    """
    Internal helper to safely call Cloudflare Worker endpoints.
    """
    url = f"{WORKER_BASE}{path}"
    headers = {
        "Content-Type": "application/json",
        "x-railway-origin": "true",
    }
    resp = requests.request(method, url, headers=headers, json=payload)
    try:
        return resp.json()
    except Exception:
        return {"status": resp.status_code, "text": resp.text}


# ─────────────────────────────────────────────
# 🧠 Unified Calendar CRUD
# ─────────────────────────────────────────────
def create_event(event_data):
    """
    Create a new calendar event via Cloudflare.
    """
    return _call_worker("/calendar/write?owner=intervals", "POST", event_data)


def update_event(event_data):
    """
    Update or overwrite an existing event.
    """
    return _call_worker("/calendar/update?owner=intervals", "POST", event_data)


def delete_event(event_id=None, date=None):
    """
    Delete event by ID or by date.
    """
    payload = {}
    if event_id:
        payload["id"] = event_id
    if date:
        payload["date"] = date
    return _call_worker("/calendar/delete?owner=intervals", "POST", payload)
