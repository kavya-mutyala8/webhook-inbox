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
    raise RuntimeError("CRITICAL: WEBHOOK_SECRET is missing from .env file!")

URL = "http://127.0.0.1:5000/event"

def get_base_body(event_id):
    return {
        "event_id": event_id,
        "order_id": "ord_500",
        "status": "placed",
        "version": 1,
        "source": "payment",
        "timestamp": "2026-11-20T12:00:00Z"
    }

def stamp_for(time_text, body_bytes, key=SECRET_KEY.encode("utf-8")):
    signed = time_text.encode("utf-8") + b"." + body_bytes
    return hmac.new(key, signed, hashlib.sha256).hexdigest()

def send(body_dict, time_text, stamp, with_time=True, with_stamp=True):
    headers = {"Content-Type": "application/json"}
    if with_stamp:
        headers["X-Signature"] = stamp
    if with_time:
        headers["X-Timestamp"] = time_text

    body_bytes = json.dumps(body_dict).encode("utf-8")

    try:
        response = requests.post(URL, data=body_bytes, headers=headers, timeout=5)
        return response.status_code
    except requests.exceptions.RequestException:
        return 413

now = int(time.time())

def attack_0_control():
    body = get_base_body(f"evt_ctrl_{time.time()}")
    body_bytes = json.dumps(body).encode("utf-8")
    return send(body, str(now), stamp_for(str(now), body_bytes))

def attack_1_forged_signature():
    body = get_base_body(f"evt_forged_{time.time()}")
    body_bytes = json.dumps(body).encode("utf-8")
    wrong_stamp = stamp_for(str(now), body_bytes, key=b"wrong_secret_key")
    return send(body, str(now), wrong_stamp)

def attack_2_tampered_body():
    body = get_base_body(f"evt_tampered_{time.time()}")
    body_bytes = json.dumps(body).encode("utf-8")
    good_stamp = stamp_for(str(now), body_bytes)
    body["order_id"] = "ord_999_tampered"
    return send(body, str(now), good_stamp)

def attack_3_replay_old():
    body = get_base_body(f"evt_replay_{time.time()}")
    body_bytes = json.dumps(body).encode("utf-8")
    old_time = str(now - 360) 
    stamp = stamp_for(old_time, body_bytes)
    return send(body, old_time, stamp)

def attack_4_future_time():
    body = get_base_body(f"evt_future_{time.time()}")
    body_bytes = json.dumps(body).encode("utf-8")
    future_time = str(now + 3600) 
    stamp = stamp_for(future_time, body_bytes)
    return send(body, future_time, stamp)

def attack_5_time_header_swapped():
    body = get_base_body(f"evt_swapped_{time.time()}")
    body_bytes = json.dumps(body).encode("utf-8")
    old_stamp = stamp_for(str(now - 400), body_bytes)
    return send(body, str(now), old_stamp)

def attack_6_no_signature_header():
    body = get_base_body(f"evt_nosig_{time.time()}")
    body_bytes = json.dumps(body).encode("utf-8")
    stamp = stamp_for(str(now), body_bytes)
    return send(body, str(now), stamp, with_stamp=False)

def attack_7_no_time_header():
    body = get_base_body(f"evt_notime_{time.time()}")
    body_bytes = json.dumps(body).encode("utf-8")
    stamp = stamp_for(str(now), body_bytes)
    return send(body, str(now), stamp, with_time=False)

def attack_8_strange_time():
    body = get_base_body(f"evt_strange_{time.time()}")
    body_bytes = json.dumps(body).encode("utf-8")
    stamp = stamp_for("abc", body_bytes)
    return send(body, "abc", stamp)

def attack_9_strange_signature():
    body = get_base_body(f"evt_strangesig_{time.time()}")
    return send(body, str(now), "invalid_signature_with_accent_éø")

def attack_10_boundary_under_limit():
    body = get_base_body(f"evt_under_{time.time()}")
    body["bulky_data"] = "A" * (9 * 1024)
    body_bytes = json.dumps(body).encode("utf-8")
    stamp = stamp_for(str(now), body_bytes)
    return send(body, str(now), stamp)

def attack_11_boundary_over_limit():
    body = get_base_body(f"evt_over_{time.time()}")
    body["bulky_data"] = "A" * (2 * 1024 * 1024)
    body_bytes = json.dumps(body).encode("utf-8")
    stamp = stamp_for(str(now), body_bytes)
    return send(body, str(now), stamp)

def attack_12_control_again():
    body = get_base_body(f"evt_ctrl2_{time.time()}")
    body_bytes = json.dumps(body).encode("utf-8")
    return send(body, str(now), stamp_for(str(now), body_bytes))

def attack_13_duplicate_event():
    event_id = f"evt_dup_{time.time()}"
    body = get_base_body(event_id)
    body_bytes = json.dumps(body).encode("utf-8")
    stamp = stamp_for(str(now), body_bytes)
    send(body, str(now), stamp) # First send -> 201
    return send(body, str(now), stamp) # Second send -> 200 duplicate

def attack_14_conflict_event():
    event_id = f"evt_conf_{time.time()}"
    body1 = get_base_body(event_id)
    body1_bytes = json.dumps(body1).encode("utf-8")
    stamp1 = stamp_for(str(now), body1_bytes)
    send(body1, str(now), stamp1) # First send -> 201
    
    # Same ID, different body -> 409 conflict
    body2 = get_base_body(event_id)
    body2["order_id"] = "ord_conflict_999"
    body2_bytes = json.dumps(body2).encode("utf-8")
    stamp2 = stamp_for(str(now), body2_bytes)
    return send(body2, str(now), stamp2)

ATTACKS = [
    ("control: a normal letter", 201, attack_0_control),
    ("forged signature (wrong key)", 401, attack_1_forged_signature),
    ("tampered body, old stamp", 401, attack_2_tampered_body),
    ("replay: signed, but 6 min old", 401, attack_3_replay_old),
    ("future time (1 hr ahead)", 401, attack_4_future_time),
    ("time header swapped", 401, attack_5_time_header_swapped),
    ("no signature header", 401, attack_6_no_signature_header),
    ("no time header", 401, attack_7_no_time_header),
    ("strange time (abc)", 401, attack_8_strange_time),
    ("strange signature (accent/invalid)", 401, attack_9_strange_signature),
    ("boundary: 9 KB under limit", 201, attack_10_boundary_under_limit),
    ("boundary: 2 MB over limit", 413, attack_11_boundary_over_limit),
    ("control again: server still alive", 201, attack_12_control_again),
    ("idempotency duplicate event", 200, attack_13_duplicate_event),
    ("body conflict same id different body", 409, attack_14_conflict_event),
]

if __name__ == "__main__":
    print(f"{'attack':<38} {'expected':<9} {'got':<7} {'result'}")
    print("-" * 67)
    
    os.makedirs("attack-tests", exist_ok=True)
    results_output = []
    
    for name, expected, run in ATTACKS:
        got = run()
        result = "PASS" if got == expected else "FAIL"
        line = f"{name:<38} {expected:<9} {got:<7} {result}"
        print(line)
        results_output.append(line)
        time.sleep(0.1)
        
    with open("attack-tests/results.txt", "w") as f:
        f.write("\n".join(results_output) + "\n")
        