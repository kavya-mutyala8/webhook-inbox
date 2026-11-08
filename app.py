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
def file_json():
    incoming_data = request.get_json()
    if not incoming_data:
        return {"error": "Invalid or missing JSON"}, 400

    incoming_event_id = incoming_data.get("event_id")
    raw_version = incoming_data.get("version")

    try:
        incoming_version = int(raw_version)
    except (TypeError, ValueError):
        return {"error": "Invalid or non-numeric version"}, 400


    for i, record in enumerate(events):
        if record.get("event_id") == incoming_event_id:
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

