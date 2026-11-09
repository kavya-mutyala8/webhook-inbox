# Event Contract

Status: target design. Today's code differs (duplicates and older versions return 400, versions are compared per event_id). It will be updated in W2, W8 and W9.

## Purpose

Other systems (payment, warehouse, rider app) send order-status events to
the inbox as HTTP POST requests. The inbox checks each event, saves it,
and applies it to the order only if it is new and not out of date.

## Request

- Method and path: `POST /event`
- Body: JSON, `Content-Type: application/json`

## Fields

| Field     | Type         | Example                | Rules                                                                                                 |
| --------- | ------------ | ---------------------- | ----------------------------------------------------------------------------------------------------- |
| event_id  | text         | "evt_1001"             | required, 1 to 64 characters, unique per event                                                        |
| order_id  | text         | "ord_879788"           | required, 1 to 64 characters                                                                          |
| status    | text         | "packed"               | required, one of the allowed statuses below                                                           |
| version   | whole number | 3                      | required, 1 or more, grows with every change of that order. `true`/`false` and decimals are rejected. |
| timestamp | text         | "2026-11-09T09:30:00Z" | required, ISO 8601 in UTC, when the event happened                                                    |
| source    | text         | "warehouse"            | required, one of: payment, warehouse, rider                                                           |

Note: today's code does not check `timestamp` and `source` yet (planned
for W2).

## Allowed statuses

placed, paid, packed, out_for_delivery, delivered, cancelled

## Limits

- Maximum body size: 10 KB (10,240 bytes).
  Why: a real event is under 1 KB, so 10 KB leaves room but stops abuse.
- Unknown extra fields: ignored and not stored.
  Why: senders may add fields later without breaking us, and we never
  save data we did not ask for.

## Headers (planned for W3 and W4)

- `X-Signature`: HMAC-SHA256 of the exact raw body.
- `X-Timestamp`: when the request was sent, covered by the signature,
  used for the replay window.

Exact formats will be finalised in W3 and W4.

## Responses

| Situation                                        | Code | Reply                              | Why                                                                                                             |
| ------------------------------------------------ | ---- | ---------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| New valid event                                  | 200  | `{"result": "accepted"}`           | Saved, then acknowledged                                                                                        |
| Duplicate event_id                               | 200  | `{"result": "duplicate"}`          | Senders retry on errors. A duplicate means "already got it", so we answer success and no second effect happens. |
| Older or equal version for that order            | 200  | `{"result": "ignored_stale"}`      | Late news is not the sender's mistake. We keep it for audit but never apply it.                                 |
| Malformed or invalid event                       | 400  | `{"error": "...", "field": "..."}` | The sender must fix it. Retrying will not help.                                                                 |
| Missing or wrong signature, or timestamp too old | 401  | `{"error": "unauthorized"}`        | Same generic message for all, so attackers learn nothing.                                                       |
| Body too large                                   | 413  | `{"error": "payload too large"}`   | Stop abuse early.                                                                                               |
| Admin-only action without permission             | 403  | `{"error": "forbidden"}`           | Known caller, not allowed.                                                                                      |
| Our own failure (database down)                  | 503  | `{"error": "try again later"}`     | Event was NOT saved, so the sender should retry.                                                                |

## Order of checks

size, then signature and timestamp, then JSON and field rules, then save
to the database, then reply.

## Examples

Valid:

```json
{
  "event_id": "evt_1001",
  "order_id": "ord_879788",
  "status": "packed",
  "version": 3,
  "timestamp": "2026-11-09T09:30:00Z",
  "source": "warehouse"
}
```

Bad examples:

- `version` is `"abc"` -> 400
- `version` is `true` -> 400
- `status` is `"teleported"` -> 400
- missing `order_id` -> 400
- same `event_id` sent twice -> 200 with `duplicate` the second time
