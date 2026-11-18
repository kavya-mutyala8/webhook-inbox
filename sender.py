import os
import json
import hmac
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("WEBHOOK_SECRET")

if not SECRET_KEY:
    raise RuntimeError("CRITICAL: WEBHOOK_SECRET is missing from environment variables or .env file!")

data_to_send = {
    "event_id": "evt_1001",
    "order_id": "ord_879788",
    "status": "placed",
    "version": 1,
    "timestamp": "2026-11-18T12:00:00Z",
    "source": "payment"
}

payload_string = json.dumps(data_to_send)
payload_bytes = payload_string.encode("utf-8")

signature = hmac.new(
    SECRET_KEY.encode("utf-8"), 
    payload_bytes, 
    hashlib.sha256
).hexdigest()

headers = {
    "X-Signature": signature,
    "Content-Type": "application/json"
}

# 6. Send POST request to the /event route
url = "http://127.0.0.1:5000/event"
response = requests.post(url, data=payload_bytes, headers=headers)

print("--- Sender Report ---")
print("Status code:", response.status_code)
print("Response Body:", response.text)