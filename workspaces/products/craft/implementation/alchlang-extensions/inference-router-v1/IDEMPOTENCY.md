# Bounded idempotency and attempt tracking

Status: local in-memory candidate. Owner: inference implementation owner.
Authority effect: none. No restart persistence, paid calls or deployment.

`idempotency-policy.alch` owns the decision table and compiles through the bound
DomainSpec compiler. `idempotency.mjs` supplies bounded native storage, serialized
key reservation, source-input fingerprinting and custody of execution outcomes.
The wrapper invokes the compiled policy; it does not replace it with a duplicate
native decision table. `dispatch.test.mjs` demonstrates composition of the policy,
selector, request/response/delta handlers and dispatcher.

## Request behavior

Use `createIdempotentDispatcher({dispatch, policy, token, ...limits})`, then
`run({request, catalog, messages, idempotencyKey?, signal?})`. Inputs are normalized
trusted-host objects, not the future public API. The host must authenticate and
check current tenant authorization before every request, including replay.

Keys are tenant scoped. The fingerprint canonicalizes object-key ordering and
materializes stream:false and max_output_tokens:256 defaults. Message ordering
and text are preserved. Client request_id is excluded: the wrapper assigns a new
UUID on reservation and replays that same ID. Catalog snapshots are excluded so
an existing result cannot reroute when policy/catalog versions change; the first
execution records its selected binding and policy version. Other normalized
request fields, including context estimates, participate in the fingerprint.

The compiled decisions are:

- Unseen key: reserve before calling dispatch.
- Same retained key with different canonical input: IDEMPOTENCY_CONFLICT.
- Matching unresolved request: REQUEST_IN_PROGRESS with the original request ID.
- Matching successful JSON: return a copy of the retained result without execution.
- Matching retained stream: STREAM_NOT_REPLAYABLE after settlement.
- Matching failed request: PREVIOUS_REQUEST_FAILED; no implicit retry.

Requests without a key execute independently and receive distinct tracked IDs.
Transport calls remain limited to one attempt. An ambiguous timeout marks failure
but keeps the record unresolved until transport settlement; it cannot expire and
start a second execution while the original transport is still active.

## Storage and tracking

Defaults: 128 records, a reservation queue of at most 128 jobs, a 64 KiB canonical
request/result limit, a 128-byte key limit and 60-second retention after local
settlement. New work rejects when storage or the reservation queue is full;
unresolved records are never evicted. Retention uses a monotonic clock.
Expired settled keys may execute again, so this is bounded deduplication, not an
exactly-once guarantee. A permanently uncooperative transport can keep a slot
occupied; operator recovery is a future operational concern.

`inspect()` returns copies of request/attempt metadata, not stored results,
request fingerprints, messages or secrets. Metadata includes request ID, local
state, timestamps, binding/version, policy version and usage provenance. A
completed provider result is marked reported-complete; failures and cancellations
retain unknown remote completion. Locally settled does not prove remote work or
billing stopped. Streams track completion/error/cancellation without storing text.
JSON replay results are intentionally held in bounded memory during retention.

## Verification and construction state

Run `node run.mjs test` using the compiler bindings in PROTOTYPE.md. Tests compile
the authored idempotency policy and compose it with actual generated handlers.
They exercise concurrent duplicates, conflicting inputs, tenant isolation, copied
replay results, expiry, pending-key retention, queue/storage limits, defaults,
unkeyed requests, failed attempts, ambiguous deadlines and stream non-reexecution.
JSON/SSE/selector regression tests remain included. `idempotency-evidence.json`
pins the exact tested files. Earlier evidence documents remain historical epochs.

D65 chain: candidate definitions and business/product scaffolds -> authored Alch
idempotency policy -> compiled DomainSpec policy handler -> native bounded custody
and dispatch lifecycle observations -> local product tests. This does not imply
canonical admission, product approval, public API readiness or durable storage.

Product frontier: D7 bounded local deduplication and tracking. Runnable next:
D8 public host adapter with tenant authentication, request normalization and
catalog/discovery endpoints. There is no current blocker for local host fixtures.

Operational support: inference operator/product owner selects live providers,
budgets, production limits and retention; storage owner selects restart durability
before production claims; VPS/product owners own later deployment. Those decisions
are deferred and do not block the next local host prototype.

## Open Questions

- Which storage backend and replay guarantees should survive restart or span hosts?
- What production retention, capacity and recovery rules apply to stuck requests?
- Which real providers, public aliases and tokenizer estimates should be configured?
- Which provider-specific non-execution evidence can permit safe fallback?
- Is durable Define-session continuity needed beyond its in-memory workflow?

Local prototypes answer only the in-memory portion of the earlier retention and
idempotency questions. The original Define output remains unchanged; no production
choice has been inferred from these test defaults.

Current generated binding and conformance evidence: [ISB-07 custody](custody/README.md).
