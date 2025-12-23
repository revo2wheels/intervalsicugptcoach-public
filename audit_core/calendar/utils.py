from datetime import datetime, timedelta

def build_headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def get_date_range(days_ahead=14):
    today = datetime.utcnow()
    start = today.date().isoformat()
    end = (today + timedelta(days=days_ahead)).date().isoformat()
    return start, end
