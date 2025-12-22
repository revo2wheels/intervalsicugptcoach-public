import os, requests, json

headers = {
    "Authorization": f"Bearer {os.getenv('ICU_OAUTH', '')}",
    "User-Agent": "IntervalsGPTCoachLocal/1.0"
}

r = requests.get("https://intervalsicugptcoach.clive-a5a.workers.dev/run_weekly?staging=1", headers=headers)
print("STATUS", r.status_code)
data = r.json()
print("TOP LEVEL KEYS:", list(data.keys()))
print("\nFIRST 1500 CHARS OF semantic_graph:\n")
print(json.dumps(data.get("semantic_graph", {}), indent=2)[:1500])
