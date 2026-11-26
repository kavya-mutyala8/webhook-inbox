import os
import time
import hmac
import hashlib
from flask import Flask, request
from dotenv import load_dotenv
from database import init_db, get_event_by_id, save_event_and_state

load_dotenv()
SECRET_KEY = os.getenv("WEBHOOK_SECRET")

if not SECRET_KEY:
    raise RuntimeError("CRITICAL: WEBHOOK_SECRET is missing from environment variables or .env file!")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024

init_db()

def verify(secret: str, message: bytes, provided_signature: str) -> bool:
    if not provided_signature or not isinstance(provided_signature, str):
        return False
    try:
        expected_signature = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_signature, provided_signature)
    except Exception:
        return False

ALLOWED_STATUSES = [
    "placed", "paid", "packed", 
    "out_for_delivery", "delivered", "cancelled"
]
ALLOWED_SOURCES = ["payment", "warehouse", "rider"]

WINDOW_SECONDS = 300
FUTURE_SECONDS = 60

@app.route("/event", methods=["POST"])
def receive_event():
    raw_data = request.data
    incoming_sign = request.headers.get("X-Signature", "")
    incoming_timestamp_str = request.headers.get("X-Timestamp", "")

    if not incoming_timestamp_str or not incoming_timestamp_str.isdigit():
        return {"error": "Unauthorized"}, 401

    try:
        incoming_timestamp = int(incoming_timestamp_str)
    except ValueError:
        return {"error": "Unauthorized"}, 401

    combined_message = f"{incoming_timestamp_str}.".encode("utf-8") + raw_data

    if not verify(SECRET_KEY, combined_message, incoming_sign):
        return {"error": "Unauthorized"}, 401

    current_time = int(time.time())

    if current_time - incoming_timestamp > WINDOW_SECONDS:
        return {"error": "Unauthorized"}, 401

    if incoming_timestamp - current_time > FUTURE_SECONDS:
        return {"error": "Unauthorized"}, 401

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

    existing_event = get_event_by_id(event_id)
    
    if existing_event:
        stored_version = existing_event[3]

        if incoming_version > stored_version:
            save_result = save_event_and_state(event_id, order_id, status, incoming_version, source, timestamp)
            if save_result == "success":
                return {"Message": "updated", "data": incoming_data}, 200
            elif save_result == "duplicate":
                return {"error": "Duplicate event_id"}, 400
            else:
                return {"error": "Service Unavailable (Database Error)"}, 503
        else:
            return {"error": "Duplicate or older version"}, 400
            
    save_result = save_event_and_state(event_id, order_id, status, incoming_version, source, timestamp)
    
    if save_result == "success":
        return {"Message": "success", "data": incoming_data}, 201
    elif save_result == "duplicate":
        return {"error": "Duplicate event_id"}, 400
    else:
        return {"error": "Service Unavailable (Database Error)"}, 503

@app.errorhandler(413)
def request_entity_too_large(error):
    return {"error": "Payload too large (max limit is 10KB)"}, 413

if __name__ == "__main__":
    app.run(debug=True)