import serial
import time
import requests
import json
import sys
import os

# --- Config ---
# Load from environment variables or use placeholders
AUTH_KEY_ID = os.getenv("SORACOM_AUTH_KEY_ID", "YOUR_KEY_ID")
AUTH_KEY_SECRET = os.getenv("SORACOM_AUTH_KEY_SECRET", "YOUR_KEY_SECRET")
SIM_ID = os.getenv("SORACOM_SIM_ID", "YOUR_SIM_ID")
API_BASE_URL = "https://g.api.soracom.io/v1"

# SMS Commands
CMD_MOVE = "8050000 180"  # 180s when moving
CMD_STOP = "8090000 600"  # 600s when stopped

def get_token():
    url = f"{API_BASE_URL}/auth"
    payload = {"authKeyId": AUTH_KEY_ID, "authKey": AUTH_KEY_SECRET}
    headers = {"Content-Type": "application/json"}
    try:
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        r.raise_for_status()
        return r.json()["apiKey"], r.json()["token"]
    except Exception as e:
        print(f"Auth Error: {e}")
        return None, None

def check_sim_status(api_key, token, sim_id):
    url = f"{API_BASE_URL}/sims/{sim_id}"
    headers = {
        "X-Soracom-API-Key": api_key,
        "X-Soracom-Token": token,
        "Content-Type": "application/json"
    }
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        status = r.json().get("sessionStatus", {}).get("online", False)
        return status
    except:
        return False

def send_sms(api_key, token, sim_id, message):
    url = f"{API_BASE_URL}/sims/{sim_id}/send_sms"
    body = {"payload": message}
    headers = {
        "X-Soracom-API-Key": api_key,
        "X-Soracom-Token": token,
        "Content-Type": "application/json"
    }
    try:
        r = requests.post(url, data=json.dumps(body), headers=headers)
        print(f"SMS '{message}' -> {r.status_code}")
    except Exception as e:
        print(f"SMS Error: {e}")

def setup_modem():
    print("--- 1. Restoring Modem Settings (LTE Only) ---")
    # ... (Same as connect.py) ...
    # Simplified for template
    print("Please run connect.py first to ensure connectivity.")

def wait_and_config():
    if AUTH_KEY_ID == "YOUR_KEY_ID":
        print("Error: Please set SORACOM_AUTH_KEY_ID and other env vars.")
        return

    print("\n--- 2. Waiting for Online & Configuring Intervals ---")
    api_key, token = get_token()
    if not api_key: return

    print("Waiting for ONLINE status...")
    while True:
        if check_sim_status(api_key, token, SIM_ID):
            print("\n*** ONLINE DETECTED! ***")
            print("Sending interval configuration SMS...")
            time.sleep(10)
            send_sms(api_key, token, SIM_ID, CMD_MOVE)
            time.sleep(5)
            send_sms(api_key, token, SIM_ID, CMD_STOP)
            break
        print(".", end="", flush=True)
        time.sleep(10)

if __name__ == "__main__":
    wait_and_config()