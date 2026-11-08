# Generated request custody

ISB-07 completed local candidate.

Validation: **98 inference/service tests**, **14 DomainSpec contract tests** and
**three existing service compatibility tests** pass. [Construction plan](PLAN.md), [evidence](evidence.json),
[authored declaration](../request-custody.alch), [existing policy](../idempotency-policy.alch).

The Alch declaration owns the fingerprint version, request/payload fields,
materialized defaults, exclusion of caller request ID, retention limits and
execute/replay/reject mapping. Its pure policy module makes the duplicate decision.
The generated bundle contains that module, normalized contract, source trace and
hashed inventory. The public host binds DomainSpec's bounded memory store.

Canonical sorted JSON plus SHA-256 identifies normalized request and messages.
Routing strategy stays in the request identity. Catalogs are excluded from the
fingerprint and copied before reservation, so the first execution retains its
catalog snapshot while replay does not route again. Tenant scope and key form
an atomic reservation key; an absent key creates an independent execution.

The store serializes only policy evaluation and reservation. Its bounded queue
retains occupancy while cancelled policy work settles, and checks cancellation
before committing so it cannot later create an orphan reservation. The host
bounds reservation time separately from provider invocation time. Execution
tokens are opaque and store-local. An awaited beginAttempt permits at most one
send and records exact binding, model and policy versions before transport.

A local outcome is write-once. Transport settlement is a separate observation.
Retention starts at the later observation; neither a deadline nor availability
of a streaming Response releases a pending record. A timed-out attempt remains
unknown remotely, and a stream cannot replay. Replayed JSON is copied. Operator
inspection excludes messages, results, fingerprints, tokens and secret fields.

Native code owns canonical byte encoding, hashing, memory synchronization,
clocks and transport effects. It executes the authored custody configuration;
the inference wrapper only wires dependencies. Memory custody provides no
restart or multi-process guarantee. The normalized runtime keeps result/usage
as bounded JSON so each service's generated output schema owns its shape.

Build with `node ../run.mjs build-custody /absolute/new/bundle` from this directory
(or use the repository toolchain launcher). Run all regressions with `node ../run.mjs test`.

## Open Questions

No blocking questions for the memory candidate. Restart recovery, multi-host
storage and durable retention require a separate backend decision. ISB-08 next
proves an independent service fixture and inventories remaining native code.
Tenant authentication and authorization remain ISB-09, last.
