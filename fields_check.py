import os
import requests
import pandas as pd

ICU_TOKEN = os.getenv("ICU_OAUTH")
INTERVALS_API = "https://intervals.icu/api/v1"

headers = {"Authorization": f"Bearer {ICU_TOKEN}"}
fields = "id,name,type,start_date_local,distance,moving_time,icu_training_load,IF,average_heartrate,VO2MaxGarmin"

url = (
    f"{INTERVALS_API}/athlete/0/activities?"
    f"oldest=2025-10-15&newest=2025-11-13&fields={fields}"
)

print(f"Requesting: {url}")
resp = requests.get(url, headers=headers)
print(f"HTTP {resp.status_code}")

data = resp.json()
df = pd.DataFrame(data)

print("Columns returned from API:")
print(df.columns.tolist())
print(f"Row count: {len(df)}")
