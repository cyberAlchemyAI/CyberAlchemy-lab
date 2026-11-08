# Alch event execution v1

Status: product-construction prototype; authority effect: none.

## Meaning and construction frontier

An execution binding selects a declared Operation, its transport, identity fields,
and total Alch mappings for persisted state and event payload. The generated
handler evaluates declared input types, actors, grants, SFOL rules, and permissions
before its transaction. Producer state and outbox are atomic; consumer state and
inbox receipt are atomic. Same message ID with different content is rejected.

Operation → ExecutionBinding → Mapping → Entity and Operation → Event → Consumer
are prototype navigation relationships, not newly admitted ontology records.
DomainSpec still owns the compiled provider-neutral message contracts. Mapping
field clauses use the existing Alch mapping AST; no embedded TypeScript or Rust
is accepted in the source. Portable execution initially supports a closed subset
of SFOL; unsupported operators are rejected during construction.

Runnable product construction: generated Node/Rust handlers, durable SQLite
transactions, restart and cross-language parity tests. Operational support:
Craft historical source-binding migration and cloud provider integration remain
separate. No production deployment or runtime admission is claimed.

## Open Questions

Cloud event-source adapters, production storage topology and observer export
remain later work. Local SQLite durability is not a cloud storage guarantee.

## Source and generated artifacts

[order-events.alch](order-events.alch) contains all business fields, rules,
permissions, event channels, delivery policies, observations, and execution mappings.
[place-order.request.json](place-order.request.json) is a local invocation fixture.
The generated Node module exports `handler(request, context, options)`; the Rust
crate exports `handler(request, context, database, failpoint)`. Both also have a
one-invocation JSON stdin entry point, suitable for a trusted host adapter.

From the repository root, build the CLI and a bundle:

```bash
npm run build --prefix cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/implementation
node cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/implementation/dist/cli.js build cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/event-execution-v1/order-events.alch --out /tmp/my-order-event-function
ALCH_EVENT_DATABASE=/tmp/my-orders.sqlite node /tmp/my-order-event-function/handler.mjs < cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/event-execution-v1/place-order.request.json
ALCH_EVENT_DATABASE=/tmp/my-orders.sqlite /tmp/my-order-event-function/alch-event < cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/event-execution-v1/place-order.request.json
```

The first invocation commits state and outbox; the second recognizes the same
committed message. The bundle contains both standalone entries, the Rust source
crate and Cargo.lock, DomainSpec contracts, config, deployment description, and
file-hash manifest. Offline compilation needs cached pinned Rust dependencies.
The compiled binary is local-platform-specific. The generated-source directory
in this extension omits the native binary; build a bundle for executable delivery.

## Runtime protocol

`invoke` selects a declared operation. Producers accept typed `facts` and an
`expected_version`; consumers accept the six-field DomainSpec message envelope.
All mutation requests carry consistent `now` epoch milliseconds and canonical UTC
`at` timestamps. The runtime enforces the declared operation's SFOL preconditions
against invocation facts; optimistic version checks protect stored state.

`claim` selects one pending or expired-leased outbox message for `worker`.
`settle` requires `worker`, `message_id`, `attempt`, and an unexpired matching lease.
Its outcome is `provider-accepted` or `unknown`. A host transport adapter must
supply actual acceptance evidence; a client assertion is not provider evidence.
Unknown outcomes use bounded exponential retry and terminate as local `dead` rows.
`inspect` returns state, outbox, inbox, observations, and observation accounting.

The host supplies trusted context separately: Alch `actor` and `grants` for
business operations; `transport_grants` containing the declared transport ID for
inspect/claim/settle. The stdin wrapper accepts this context only as a local test
and host-integration interface. Do not populate it from an untrusted HTTP body.
No public HTTP endpoint, authentication provider, broker, or cloud deployment is
created by this extension.

State, outbox, and observation writes share the producer transaction. State,
inbox, and successful consumer observations share the consumer transaction.
Consumer failure observations are retained in a separate transaction after
rollback; an observer failure cannot turn rollback into a commit claim.
Message-ID reuse with different content is rejected. The consumer deduplication
key includes its operation identity. SQLite WAL and FULL synchronization are
used; separate processes and targets can share the same database schema.

## Portable subset and evidence boundaries

Execution requires one producer, one consumer, one transport, and total mappings.
Identity fields must be preserved by the event payload mapping. Supported SFOL
operators are eq, neq, and, or, not, exists, and absent; unsupported forms reject
at compile time. Fields support string, identifier, timestamp, boolean, integer,
and record. All JSON numbers, including nested records, must be safe integers;
use integer minor units for monetary values in this prototype.

ORODI observations retain simulation mode, correlation, cardinality limits, and
pending telemetry accounting. They are not admitted runtime evidence. The
existing DomainSpec persistence selection remains a predecessor contract; this
prototype's Rust realization is tested locally, not separately registry-admitted.
Provider retention, real dead-letter routing, cloud durability, and deployment
remain outside this local execution boundary. No prior admission is expanded.

## Craft coordination

This extension is related construction under the existing Craft ORODI capabilities.
See [Craft related work](/home/vlad_/projects/cyberAlchemy-v2/product/craft/capabilities/orodi/RELATED-WORK.md). Historical source-binding migration
remains operational support and does not block this prototype.

## Validation

Validation results, the test log, and the selected-source manifest are recorded
alongside this document. The tests execute generated programs in separate
processes and compare Node/Rust state and observations, including cross-target
reopen, duplicate/conflicting IDs, atomic failure, caller checks, stale leases,
retry termination, numeric bounds, and concurrent optimistic-version conflicts.
