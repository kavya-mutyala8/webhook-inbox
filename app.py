import json
import os
from flask import Flask, request

app = Flask(__name__)

DATA_FILE = "data.json"

ALLOWED_STATUSES = [
    "placed", "paid", "packed", 
    "out_for_delivery", "delivered", "cancelled"
]
ALLOWED_SOURCES = ["payment", "warehouse", "rider"]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return []
    return []

def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(events, file, indent=4)

events = load_data()

@app.route("/event", methods=["POST"])
def receive_event():
    incoming_data = request.get_json(silent=True)
    if not isinstance(incoming_data, dict):
        return {"error": "Invalid or missing JSON object"}, 400

    required_fields = ["event_id", "order_id", "status", "version", "source", "timestamp"]
    for field in required_fields:
        if field not in incoming_data:
            return {"error": f"Missing field: {field}"}, 400

    event_id = incoming_data.get("event_id")
    order_id = incoming_data.get("order_id")
    status = incoming_data.get("status")
    raw_version = incoming_data.get("version")
    source = incoming_data.get("source")
    timestamp = incoming_data.get("timestamp")

    if not isinstance(event_id, str) or not event_id.strip() or len(event_id) > 64:
        return {"error": "event_id must be non-empty text (max 64 chars)"}, 400

    if not isinstance(order_id, str) or not order_id.strip() or len(order_id) > 64:
        return {"error": "order_id must be non-empty text (1 to 64 chars)"}, 400

    if not isinstance(timestamp, str) or not timestamp.strip():
        return {"error": "timestamp must be non-empty text"}, 400

    if status not in ALLOWED_STATUSES:
        return {"error": f"Invalid status. Allowed: {ALLOWED_STATUSES}"}, 400

    if source not in ALLOWED_SOURCES:
        return {"error": f"Invalid source. Allowed: {ALLOWED_SOURCES}"}, 400

    if type(raw_version) is not int or raw_version < 1:
        return {"error": "version must be an integer greater than or equal to 1"}, 400

    incoming_version = raw_version

    for i, record in enumerate(events):
        if record.get("event_id") == event_id:
            try:
                stored_version = int(record.get("version", 0))
            except (TypeError, ValueError):
                stored_version = 0

            if incoming_version > stored_version:
                events[i] = incoming_data
                save_data()
                return {"Message": "updated", "data": incoming_data}, 200
            else:
                return {"error": "Duplicate or older version"}, 400
            
    events.append(incoming_data)
    save_data()

    return {"Message": "success", "data": incoming_data}, 201
 
if __name__ == "__main__":
    app.run(debug=True)

