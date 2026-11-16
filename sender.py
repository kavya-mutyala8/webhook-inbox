import os
import json
import hmac
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("WEBHOOK_SECRET")

data_to_send = {
    "event_id": "evt_1001",
    "order_id": "ord_879788",
    "status": "placed",
    "version": 1,
    "timestamp": "2026-11-11T10:30:00Z",
    "source": "payment"
}

payload_string = json.dumps(data_to_send)

signature = hmac.new(
    SECRET_KEY.encode("utf-8"), 
    payload_string.encode("utf-8"), 
    hashlib.sha256
).hexdigest()

headers = {
    "X-Sign": signature,
    "Content-Type": "application/json"
}

url = "http://127.0.0.1:5000/webhook"
response = requests.post(url, data=payload_string, headers=headers)

print("Flask echoed back:")
print("Status code:", response.status_code)
print("Raw text response:", response.text)