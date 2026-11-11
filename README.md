# webhook-inbox

A small Flask server that receives order-status events as JSON, refuses duplicates and older versions, and saves events to a file. This is a learning project and it is a work in progress.

## What works today

- `POST /event` accepts a JSON object with `event_id`, `order_id`, `status`, `version`, `timestamp` and `source`
- Rejects an empty body, broken JSON, or JSON that is not an object (400)
- Rejects a missing field and names it
- `event_id` and `order_id` must be non-empty text, at most 64 characters
- `status` must be one of: placed, paid, packed, out_for_delivery, delivered, cancelled
- `source` must be one of: payment, warehouse, rider
- `version` must be a whole number of 1 or more (`true`, decimals and text are rejected)
- Refuses a duplicate or an older version (returns 400) and accepts a newer version
- Saves events to `data.json`, so they are still there after a restart

## Not built yet

- HMAC signature check
- Timestamp / replay window
- SQLite storage
- Failed-event list and admin replay
- Automated tests (pytest), attack tests, threat model, CI

## Known limits

- Anyone who can reach the server can send events (there is no signature check yet)
- Versions are compared per `event_id`, not per order yet
- Events are stored in a JSON file, which is not safe if many requests arrive at the same time
- A duplicate and an older version get the same 400 answer
- The server runs with debug mode on, which is only safe on my own laptop
- `timestamp` is only checked to be non-empty text for now (a real date check comes with the replay window)

## How to run

Tested on Windows with Python 3.14.

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

In a second terminal (with the venv active), run `python sender.py` to send a test event. The file `data.json` is created on the first save.

## AI help

I wrote the code myself. I used Claude as a tutor and reviewer: it explained concepts with small examples, gave hints, and reviewed my code. .
