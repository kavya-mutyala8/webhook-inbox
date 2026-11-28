# webhook-inbox

A small Flask server that receives order-status events as JSON, checks they come
from a trusted sender (HMAC signature and a replay window), saves them in SQLite,
and ignores duplicates. This is a learning project and a work in progress.
Details: `docs/EVENT_CONTRACT.md` and `docs/TRADE_OFFS.md`.

## What works today

- `POST /event` accepts a JSON object with `event_id`, `order_id`, `status`, `version`, `timestamp` and `source`
- **HMAC-SHA256 signature check** over a combined message (`timestamp + "." + body`) with a constant-time comparison
- **Replay window:** 5 minutes, with a 1-minute future allowance, using the `X-Timestamp` header
- **Size limit:** 10 KB (`MAX_CONTENT_LENGTH`), with a JSON `413` answer
- Rejects an empty body, broken JSON, or JSON that is not an object (400), and names a missing field
- `event_id` and `order_id` must be non-empty text of at most 64 characters
- `status` must be one of: placed, paid, packed, out_for_delivery, delivered, cancelled
- `source` must be one of: payment, warehouse, rider
- `version` must be a whole number of 1 or more (`true`, decimals and text are rejected)
- **SQLite storage:** events and the current state of each order are saved in `inbox.db`
  **before** the server replies; if the database fails the reply is `503` and nothing is stored
- **Duplicates:** the same `event_id` gets a success answer (`200`) and changes nothing;
  each event keeps a receive count
- **Conflicts:** the same `event_id` with a different body (compared by a fingerprint of the
  raw body) gets `409`
- **Attack tests:** `attack-tests/run_attacks.py` runs security scenarios and writes a report

### Security test results

| Attack scenario                      | Expected | Got | Result |
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

- Version-order tests and the "stale" reply (W9)
- Processing states, failed-event list and admin replay
- Automated tests (pytest), threat model, CI

## Known limits

- SQLite is one file on one machine: no replication, one server only
- Event ids and body fingerprints are kept forever: there is no cleanup job yet
  (a retention window is discussed in `docs/TRADE_OFFS.md`)
- One shared secret in `.env`, no key rotation
- The server runs with debug mode on, which is only safe on my own laptop

## How to run

Tested on Windows with Python 3.14.

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py

## AI help

I wrote the code myself. I used Claude as an reviewer, and
some documentation was drafted with AI help and then edited by me.
```
