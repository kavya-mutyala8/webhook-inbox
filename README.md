# webhook-inbox

A small Flask server that receives order-status events as JSON, refuses duplicates and older versions, verifies HMAC signatures with replay protection, enforces size limits, and saves events to a file. This is a learning project and it is a work in progress.

## What works today# webhook-inbox

A small Flask server that receives order-status events as JSON, refuses duplicates and older versions, verifies HMAC signatures with replay protection, enforces size limits, and saves events to a file. This is a learning project and it is a work in progress.

## What works today

- `POST /event` accepts a JSON object with `event_id`, `order_id`, `status`, `version`, `timestamp` and `source`
- **HMAC-SHA256 Signature Verification:** Validates incoming requests securely using constant-time comparison over a combined message (`timestamp + "." + body`).
- **Replay Window Protection:** Enforces a 5-minute window and 1-minute future buffer using the `X-Timestamp` header.
- **Payload Size Limits:** Configured `MAX_CONTENT_LENGTH` (10 KB limit) with custom `413 Request Entity Too Large` JSON responses to prevent DoS attacks.
- Rejects an empty body, broken JSON, or JSON that is not an object (400)
- Rejects a missing field and names it
- `event_id` and `order_id` must be non-empty text, at most 64 characters
- `status` must be one of: placed, paid, packed, out_for_delivery, delivered, cancelled
- `source` must be one of: payment, warehouse, rider
- `version` must be a whole number of 1 or more (`true`, decimals and text are rejected)
- Refuses a duplicate or an older version (returns 400) and accepts a newer version
- Saves events to `data.json`, so they are still there after a restart
- **Automated Attack Tests:** A dedicated test suite (`attack-tests/run_attacks.py`) that runs security scenarios and generates a verification report.

### Security Test Results

| Attack Scenario                    | Expected | Got | Result |
| :--------------------------------- | :------: | :-: | :----: |
| control: a normal letter           |   201    | 201 |  PASS  |
| forged signature (wrong key)       |   401    | 401 |  PASS  |
| tampered body, old stamp           |   401    | 401 |  PASS  |
| replay: signed, but 6 min old      |   401    | 401 |  PASS  |
| future time (1 hr ahead)           |   401    | 401 |  PASS  |
| time header swapped                |   401    | 401 |  PASS  |
| no signature header                |   401    | 401 |  PASS  |
| no time header                     |   401    | 401 |  PASS  |
| strange time (abc)                 |   401    | 401 |  PASS  |
| strange signature (accent/invalid) |   401    | 401 |  PASS  |
| boundary: 9 KB under limit         |   201    | 201 |  PASS  |
| boundary: 11 KB over limit         |   413    | 413 |  PASS  |
| control again: server still alive  |   201    | 201 |  PASS  |

## Not built yet

- SQLite storage
- Failed-event list and admin replay
- Automated tests (pytest), threat model, CI

## Known limits

- Versions are compared per `event_id`, not per order yet
- Events are stored in a JSON file, which is not safe if many requests arrive at the same time
- A duplicate and an older version get the same 400 answer
- The server runs with debug mode on, which is only safe on my own laptop

## How to run

Tested on Windows with Python 3.14.

````bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py

- `POST /event` accepts a JSON object with `event_id`, `order_id`, `status`, `version`, `timestamp` and `source`
- **HMAC-SHA256 Signature Verification:** Validates incoming requests securely using constant-time comparison over a combined message (`timestamp + "." + body`).
- **Replay Window Protection:** Enforces a 5-minute window and 1-minute future buffer using the `X-Timestamp` header.
- **Payload Size Limits:** Configured `MAX_CONTENT_LENGTH` (10 KB limit) with custom `413 Request Entity Too Large` JSON responses to prevent DoS attacks.
- Rejects an empty body, broken JSON, or JSON that is not an object (400)
- Rejects a missing field and names it
- `event_id` and `order_id` must be non-empty text, at most 64 characters
- `status` must be one of: placed, paid, packed, out_for_delivery, delivered, cancelled
- `source` must be one of: payment, warehouse, rider
- `version` must be a whole number of 1 or more (`true`, decimals and text are rejected)
- Refuses a duplicate or an older version (returns 400) and accepts a newer version
- Saves events to `data.json`, so they are still there after a restart
- **Automated Attack Tests:** A dedicated test suite (`attack-tests/run_attacks.py`) that runs security scenarios and generates a verification report.

### Security Test Results

| Attack Scenario | Expected | Got | Result |
| :--- | :---: | :---: | :---: |
| control: a normal letter | 201 | 201 | PASS |
| forged signature (wrong key) | 401 | 401 | PASS |
| tampered body, old stamp | 401 | 401 | PASS |
| replay: signed, but 6 min old | 401 | 401 | PASS |
| future time (1 hr ahead) | 401 | 401 | PASS |
| time header swapped | 401 | 401 | PASS |
| no signature header | 401 | 401 | PASS |
| no time header | 401 | 401 | PASS |
| strange time (abc) | 401 | 401 | PASS |
| strange signature (accent/invalid) | 401 | 401 | PASS |
| boundary: 9 KB under limit | 201 | 201 | PASS |
| boundary: 11 KB over limit | 413 | 413 | PASS |
| control again: server still alive | 201 | 201 | PASS |

## Not built yet

- SQLite storage
- Failed-event list and admin replay
- Automated tests (pytest), threat model, CI

## Known limits

- Versions are compared per `event_id`, not per order yet
- Events are stored in a JSON file, which is not safe if many requests arrive at the same time
- A duplicate and an older version get the same 400 answer
- The server runs with debug mode on, which is only safe on my own laptop

## How to run

Tested on Windows with Python 3.14.

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
````
