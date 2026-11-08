# Durable session and revocation candidate

Established browser sessions and revoked token identifiers now survive process
restart. Separate connections observe logout, including during an in-flight
permission check or inference response. All grants still come from current
operator policy and Auth Foundation's Rust authorization service.

Use `createDurableBrowserInference` from [the browser binding](../browser/binding.mjs)
with the existing inference configuration plus `statePath` (absolute DB path in
an existing owner-only directory) and `stateKey` (a separately retained 32-byte
Buffer). It returns `handler`, `enrollment`, `stateMode: 'sqlite-encrypted'`, and
`close()`. Drain the listener before closing. Startup failure does not fall back
to memory. Existing `createBrowserInference` without a state parameter remains
the explicitly reported `ephemeral` predecessor mode; no running host is switched.

The operator owns the database directory and separate key. Do not place the key
in source, logs, browser responses or the database. Reusing the key and database
restores established sessions only until their existing expiry; it does not
extend access tokens or create grants. SQLite is local, not a distributed store.

State adapter (source binding requires reconciliation)
and tests (source binding requires reconciliation)
use actual SQLite with disposable fixtures. Issuer and provider behavior in these
restart tests is simulated. Historical [real HTTPS evidence](../ingress/README.md)
remains historical; this change is verified with the successor source inventory.
Current validation is recorded in RESULT.json (result record excluded).

## Open Questions

Owned by [the bounded plan](PLAN.md#open-questions): renewal, key operations,
backup rollback, multi-host coordination, login affinity, issuer logout and
inference request custody. Nothing is deployed or promoted by this candidate.

Run from the CyberAlchemy checkout:

```sh
node --test ../domainspec-core/projects/auth-foundation/implementation/inference-browser/consumer.test.mjs ../domainspec-core/projects/auth-foundation/implementation/inference-browser/state.test.mjs
TMPDIR=/dev/shm tools/toolchain/run node language/capabilities/alchlang/plans/general-compiler-v1/extensions/inference-router-v1/run.mjs test
```
