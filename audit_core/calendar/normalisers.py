def normalize_event_payload(e):
    """Ensure consistent structure for Intervals events."""
    cat = (e.get("category") or "NOTE").strip().upper()
    if cat in ["NOTES", "MEMO"]:
        cat = "NOTE"

    start_date_local = (
        e.get("start_date_local") or f"{e.get('date', '')}T00:00:00"
    )

    return {
        "category": cat,
        "start_date_local": start_date_local,
        "name": e.get("title") or e.get("name") or "Untitled",
        "description": e.get("notes") or e.get("description") or "",
        "duration_minutes": e.get("duration_minutes", 0),
    }
