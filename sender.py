import os
import json
import time
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

current_timestamp = str(int(time.time()))

payload_string = json.dumps(data_to_send)
combined_message = f"{current_timestamp}.".encode("utf-8") + payload_string.encode("utf-8")

signature = hmac.new(
    SECRET_KEY.encode("utf-8"),
    combined_message,
    hashlib.sha256
).hex_digest() if hasattr(hmac.new(SECRET_KEY.encode("utf-8"), combined_message, hashlib.sha256), "hexdigest") else hmac.new(SECRET_KEY.encode("utf-8"), combined_message, hashlib.sha256).hexdigest()

headers = {
    "X-Signature": signature,
    "X-Timestamp": current_timestamp,
    "Content-Type": "application/json"
}

url = "http://127.0.0.1:5000/event"
response = requests.post(url, data=payload_string, headers=headers)

print("--- Sender Report (W4 Step 2) ---")
print("Status code:", response.status_code)
print("Response Body:", response.text)