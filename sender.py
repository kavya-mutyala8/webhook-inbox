import requests

url = "http://127.0.0.1:5000/file"

data_to_send = {
    "event_id": "798727",
    "order_id": "879788",
    "status": "In progress",
    "version": 4
}

response = requests.post(url, json=data_to_send)

print("Falsk echoed back: ")
print("Status code:", response.status_code)
print("Raw text response:", response.text)

try:
    print(response.json())
except Exception:
    print("Response was not JSON")

#f5