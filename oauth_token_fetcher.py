#!/usr/bin/env python3
"""
Intervals.icu OAuth Token Fetcher (Final Stable)
Exchanges authorization code for access and refresh tokens.
Configured for redirect_uri=http://localhost/callback
"""

import os
import sys
import requests
import json
sys.stdout.reconfigure(encoding='utf-8')

# --- Environment Variables ---
client_id = os.getenv("ICU_CLIENT_ID")
client_secret = os.getenv("ICU_CLIENT_SECRET")
redirect_uri = os.getenv("ICU_REDIRECT_URI", "http://localhost/callback")
auth_code = os.getenv("ICU_AUTH_CODE") or (sys.argv[1] if len(sys.argv) > 1 else None)

if not all([client_id, client_secret, redirect_uri, auth_code]):
    sys.exit(
        "❌ Missing required vars. Export ICU_CLIENT_ID, ICU_CLIENT_SECRET, ICU_REDIRECT_URI, and ICU_AUTH_CODE or pass code as argument."
    )

token_url = "https://intervals.icu/api/oauth/token"

payload = {
    "grant_type": "authorization_code",
    "code": auth_code,
    "client_id": client_id,
    "client_secret": client_secret,
    "redirect_uri": redirect_uri,
    "scope": "ACTIVITY:READ,WELLNESS:READ,SETTINGS:READ",
}

headers = {"Content-Type": "application/x-www-form-urlencoded"}

print(f" Requesting OAuth token for client_id={client_id} using redirect_uri={redirect_uri} ...")

response = requests.post(token_url, data=payload, headers=headers)
if response.status_code != 200:
    sys.exit(f"❌ Token request failed ({response.status_code}) — {response.text}")

token_data = response.json()

print("\n Token exchange successful:")
print(json.dumps(token_data, indent=2))

# --- Save to .env.intervals ---
with open(".env.intervals", "w", encoding="utf-8") as f:
    f.write(f"ICU_OAUTH={token_data.get('access_token')}\n")
    f.write(f"ICU_REFRESH={token_data.get('refresh_token')}\n")
    f.write(f"ICU_EXPIRES_IN={token_data.get('expires_in')}\n")

print("\n Saved credentials → .env.intervals")
