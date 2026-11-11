import requests

url = "http://127.0.0.1:5000/event"

data_to_send = {
    "event_id": "evt_1001",
    "order_id": "ord_879788",
    "status": "placed",
    "version": 1,
    "timestamp": "2026-11-11T10:30:00Z",
    "source": "payment"
}

response = requests.post(url, json=data_to_send)

print("Flask echoed back: ")
print("Status code:", response.status_code)
print("Raw text response:", response.text)

try:
    print(response.json())
except Exception:
    print("Response was not JSON")
