# Architectural Trade-Offs

## Why a duplicate gets a success code

Returning a success code (200) for duplicate events ensures that the sending system knows its message was safely received and processed, preventing unnecessary panic loops or infinite retry storms. Since the original business effect has already been applied, acknowledging the duplicate gracefully preserves system stability without duplicating side effects.

## Why you fingerprint the raw body and not the headers

Fingerprinting the raw request body (`request.data`) via SHA-256 creates a cryptographic checksum of the actual payload content. Headers can easily be altered, stripped, or reordered by proxies, whereas the raw body hash guarantees that any tampering or modification to the payload data itself is reliably caught and rejected.

## How long you remember event IDs

Retaining event IDs indefinitely guarantees protection against ultra-late retries, but it creates an unsustainable storage growth bottleneck over time. Conversely, purging event records too early risks allowing replayed or duplicated events to slip through as "new" after the expiration window. We balance this by archiving or retaining event keys for a managed window (e.g., 30 days).
