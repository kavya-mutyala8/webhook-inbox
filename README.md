# webhook-inbox

A small Flask server that receives order-status events as JSON, refuses duplicates and older versions, and saves events to a file. This is a learning project and it is a work in progress.

## What works today

- Accepts an event sent as JSON (`event_id`, `order_id`, `status`, `version`)
- Rejects a request with no JSON body
- Rejects an event with a missing field
- Rejects a version that is not a number
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

## How to run

Tested on Windows with Python 3.14.

```
python -m venv venv
venv\Scripts\activate
pip install flask requests
python app.py
```

In a second terminal (with the venv active), run `python sender.py` to send a test event. The file `data.json` is created on the first save.

## AI help

I wrote the code myself. I used Claude as a tutor and reviewer: it explained concepts with small examples, gave hints, and reviewed my code. .
