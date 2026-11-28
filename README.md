# webhook-inbox

A small Flask server that receives order-status events as JSON, refuses duplicates and older versions, verifies HMAC signatures with replay protection, enforces size limits, and saves events to SQLite. This is a learning project and it is a work in progress.

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
- **Idempotency & Deduplication:** Duplicates get a success answer (`200`) and change nothing; each event keeps a receive count; the same `event_id` with a different body is refused with a `409 Conflict` status.
- **ACID-Compliant SQLite Storage:** Saves events and order state into SQLite (`inbox.db`), ensuring data survives restarts and concurrent safe updates.
- **Automated Attack Tests:** A dedicated test suite (`attack-tests/run_attacks.py`) that runs security and idempotency scenarios, verifying that the same event sent 5 times results in 1 row and 1 change.

### Security Test Results

| Attack Scenario                      | Expected | Got | Result |
| :----------------------------------- | :------: | :-: | :----: |
| control: a normal letter             |   201    | 201 |  PASS  |
| forged signature (wrong key)         |   401    | 401 |  PASS  |
| tampered body, old stamp             |   401    | 401 |  PASS  |
| replay: signed, but 6 min old        |   401    | 401 |  PASS  |
| future time (1 hr ahead)             |   401    | 401 |  PASS  |
| time header swapped                  |   401    | 401 |  PASS  |
| no signature header                  |   401    | 401 |  PASS  |
| no time header                       |   401    | 401 |  PASS  |
| strange time (abc)                   |   401    | 401 |  PASS  |
| strange signature (accent/invalid)   |   401    | 401 |  PASS  |
| boundary: 9 KB under limit           |   201    | 201 |  PASS  |
| boundary: 2 MB over limit            |   413    | 413 |  PASS  |
| control again: server still alive    |   201    | 201 |  PASS  |
| idempotency duplicate event          |   200    | 200 |  PASS  |
| body conflict same id different body |   409    | 409 |  PASS  |

## Not built yet

- Failed-event list and admin replay
- Automated tests (pytest), CI

## Known limits

- Versions are compared per `event_id`, not per order yet
- Event IDs and their body fingerprints are retained in the database for 30 days to balance storage costs against late-retry protection.
- Maximum body size: 10 KB.
- The server runs with debug mode on, which is only safe on my own laptop

## How to run

Tested on Windows with Python 3.14.

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
