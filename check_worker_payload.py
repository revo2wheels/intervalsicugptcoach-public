import os, requests, json

headers = {
    "Authorization": f"Bearer {os.getenv('ICU_OAUTH', '')}",
    "User-Agent": "IntervalsGPTCoachLocal/1.0"
}

# Montis maintainers only: the staging Worker URL comes from the environment.
base = os.getenv("MONTIS_STAGING_WORKER_URL", "").strip().rstrip("/")
if not base:
    raise SystemExit("Set MONTIS_STAGING_WORKER_URL first.")

r = requests.get(f"{base}/run_weekly", headers=headers)
print("STATUS", r.status_code)
data = r.json()
print("TOP LEVEL KEYS:", list(data.keys()))
print("\nFIRST 1500 CHARS OF semantic_graph:\n")
print(json.dumps(data.get("semantic_graph", {}), indent=2)[:1500])
