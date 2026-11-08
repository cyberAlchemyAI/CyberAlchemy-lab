# Durable inference request custody

SQLite now preserves idempotency reservations, provider-attempt records, terminal
outcomes and completed JSON results across restart. The existing generated policy
still decides execute/replay/reject. Tenant/principal scope remains trusted host
input, and replay still requires current authorization.

Select the backend explicitly when building and binding the application:

```js
const generated = await buildPublicPolicy(output, {
  protectedService: true,
  durableCustody: true,
});
const handler = createProtectedHandler({
  ...generated,
  ...operatorConfiguration,
  store: {durable: {path: absoluteCustodyPath, key: custodyKeyBuffer}},
});
// Drain all requests/streams before handler.close().
```

The operator supplies a dedicated absolute database path in an existing private
directory and a separately retained 32-byte key. Do not reuse the authentication
database. `durable-request-custody.alch` declares `bounded-sqlite`; the factory
rejects a memory/durable backend mismatch. Existing memory declarations remain
valid. The durable binding uses wall-clock milliseconds and rejects changed
retention/capacity/byte configuration when reopening an existing store.

`createIdempotentDispatcher` exposes `close()`. The protected server closes its
store when its listener closes; drain streams first. Browser composition also
closes the inference store through its existing close method. Keys and results
are encrypted at rest; secrets are never copied to evidence.

A request interrupted before an outcome and transport settlement remains pending,
even after restart or normal retention time. A duplicate receives
REQUEST_IN_PROGRESS and cannot execute again. Inspection reports remote completion
as unknown. Completed streams never replay, failed requests retain their failure,
and matching completed JSON replays without a second provider call. These are
local custody guarantees, not exactly-once remote execution.

[Tests](custody.test.mjs) exercise actual SQLite and generated Alch policy,
including process termination, competing connections, replay reauthorization,
retention, encryption, lock failure and cancellation. RESULT.json (result record excluded)
binds the current candidate and regression evidence. Historical compiler and
inventory evidence remains historical; this successor changes only the declared
custody compiler/backend surfaces.

## Open Questions

Owned by [PLAN.md](PLAN.md#open-questions): operator reconciliation of uncertain
outcomes, key/backup operations, wall-clock discipline, multi-host coordination
and deployment. No existing host or database is switched by this candidate.
