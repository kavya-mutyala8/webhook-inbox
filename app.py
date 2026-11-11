import json
import os
from flask import Flask, request

app = Flask(__name__)

# f1
@app.route("/hello")
def hello():
    return "hi"

#f2
@app.route("/about")
def about():
    return "Gizmo-01"

#f3
@app.route("/event")
def event():
    return {
        "event-id": "798727",
        "order-id": "879788",
        "status": "In progress",
        "version": 1
    }

#f4 
@app.route("/echo", methods=["POST"])
def echo_json():
    data = request.get_json()
    if not data:
        return {"error": "Invalid or missing JSON"}, 400
    return data

#f6
@app.route("/events", methods=["POST"])
def events_json():
    report = request.get_json()
    if not report:
        return {"error": "Invalid or missing JSON"}, 400

    required_keys = ["event_id", "order-id", "status", "version"]
    if all(key in report for key in required_keys):
        return {"Message": "event-id, order-id, status and version are in data"}, 200
    else:
        return {"Message": "event-id, order-id, status and version are not in data"}, 400

#f7
My_Storage = [
    {
        "event_id": 797293,
        "order_id": 879373,
        "status": "In progress",
        "version": "MEC-42873"
    },
    
    {
        "event_id": 797294,
        "order_id": 879374,
        "status": "shipped",
        "version": "MEC-42874"
    },

    {
        "event_id": 797293,
        "order_id": 879375,
        "status": "In progress",
        "version": "MEC-42875"
    },

    {
        "event_id": 797295,
        "order_id": 879375,
        "status": "shipped",
        "version": "MEC-42875"
    },

    {
        "event_id": 797293,
        "order_id": 879376,
        "status": "shipped",
        "version": "MEC-42876"
    }
]

@app.route("/events1", methods=["POST", "GET"])
def show_storage():
    return My_Storage

#f8, f9 and f10
events = [
    {
        "event_id": 797293,
        "order_id": 879373,
        "status": "In progress",
        "version": "MEC-42873"
    },
    
    {
        "event_id": 797294,
        "order_id": 879374,
        "status": "shipped",
        "version": "MEC-42874"
    },

    {
        "event_id": 797293,
        "order_id": 879375,
        "status": "In progress",
        "version": "MEC-42875"
    },

    {
        "event_id": 797295,
        "order_id": 879375,
        "status": "shipped",
        "version": "MEC-42875"
    },

    {
        "event_id": 797293,
        "order_id": 879376,
        "status": "shipped",
        "version": "MEC-42876"
    }
]

DATA_FILE = "data.json"

ALLOWED_STATUSES = [
    "placed", "paid", "packed", "In progress", 
    "shipped", "out_for_delivery", "delivered", "cancelled"
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

@app.route("/file", methods=["POST"])
def receive_event():
    incoming_data = request.get_json(silent=True)
    if not isinstance(incoming_data, dict):
        return {"error": "Invalid or missing JSON object"}, 400

    required_fields = ["event_id", "order_id", "status", "version", "source"]
    for field in required_fields:
        if field not in incoming_data:
            return {"error": f"Missing field: {field}"}, 400

    event_id = incoming_data.get("event_id")
    order_id = incoming_data.get("order_id")
    status = incoming_data.get("status")
    raw_version = incoming_data.get("version")
    source = incoming_data.get("source")

    if not isinstance(event_id, str) or not event_id.strip() or len(event_id) > 64:
        return {"error": "event_id must be non-empty text (max 64 chars)"}, 400

    if not isinstance(order_id, str) or not (1 <= len(order_id) <= 64):
        return {"error": "order_id must be text between 1 and 64 characters"}, 400

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

