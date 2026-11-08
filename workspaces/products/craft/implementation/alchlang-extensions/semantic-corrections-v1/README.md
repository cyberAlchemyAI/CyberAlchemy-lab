# Semantic host candidate

`semantic-host-v1` corrects the eight authoring/runtime review findings in a versioned successor. Start with [orders.alch](orders.alch). Its command contains business input only; message identity, expected version and clock belong to the invocation envelope. The compiler derives the schemas and structural mappings from the typed ontology.

The previous `ontology-host-v1` and `event-execution-v1` packages remain historical prototypes. Their green tests did not cover these defects. [counterexamples.json](counterexamples.json) records actual Node **and Rust** reproductions of the incorrect transition, narrowed-input and default behavior; it is explicitly known-failure evidence.

## Authoring

An entity describes stored business state. A command describes exactly what the caller may supply. An event describes a payload projected from committed state. A projection describes consumer-owned state. `from` derives a record shape; an equivalent explicit list of properties is also accepted.

```alch
entity Order:
  orderId: identifier required
  status: string required
  payload: record required
  note: string required default ""

command PlaceOrder:
  orderId: identifier required
  payload: record required
  note: string optional

event OrderPlaced:
  from Order

projection RecordedOrder:
  from OrderPlaced

operation place-order:
  input PlaceOrder
  state Order
  key orderId
  transition status pending -> committed
  emits OrderPlaced
```

See the complete file for the single actor, authority boundary, binding, consumer and delivery declarations. `OrderService` is an explicit actor selection. The host must separately supply that actor and the required grant. Compilation never grants permission.

There is no authored `OutboxMessage` placeholder. Selecting `sqlite-event-store-v2` imports versioned `EventEnvelope`, `OutboxMessage` and `InboxReceipt` definitions. These are a **new local DomainSpec binding-type prototype**, not a claim that the earlier binding already supplied these types or that an upstream type profile is admitted. The bundle includes their provenance and separate Node/Rust adapter descriptions. Public DomainSpec CLI 1.0.0 validates the delivery binding set and generates its TypeScript/Rust contracts.

## Execution

- Producer state is keyed by `(entity:Order, orderId)`; consumer state by `(projection:RecordedOrder, orderId)`.
- A transition compares persisted state inside the SQLite write transaction. A caller cannot provide the lifecycle field. Changing `committed` to `cancelled` changes the actual stored destination.
- A successful producer transaction writes state, version, outbox and delivery history together. A consumer transaction writes projection and inbox together.
- Identical producer retries return `already-committed`; changed facts or versions with the same message ID reject. Consumer retries compare the complete envelope before returning `duplicate`. Retries do not repeat transitions or increment receive counts.
- A default supplies a missing value. It preserves supplied `false`, `0`, and `""`; null rejects. `assign note "fixed"` explicitly overwrites a value. The lifecycle transition owns its field assignment.
- Node executes DomainSpec-generated Mapping functions. Rust lowers the same returned typed Mapping contracts into generated Rust functions. Unsupported expressions reject during generation. Backfills also execute generated DomainSpec Mapping functions.
- `max-attempts` counts issued transport leases. `max-receives` separately bounds validated, authorized, nonduplicate consumer attempts, including business rollback. A separate durable reservation preserves the receive count across business rollback or process death. The business transaction rechecks deduplication after reservation.
- Retention starts at host acceptance time and ends delivery eligibility. Terminal messages are copied into the declared local dead-letter channel. Original outbox/inbox receipts are retained indefinitely; this profile performs no automatic deletion.
- Leases fence stale acknowledgements. Unknown outcomes use bounded exponential retry and reconcile by message identity. A lost acknowledgement after consumer commit safely replays as a duplicate.

`alchlang ontology orders.alch` and `alchlang explain orders.alch` show the generated scaffold, stable identities, authored source locations, derived record relationships, actor/boundary selections, effects, mappings and binding provenance. These views do not confer authority.

## Build and local host

From `implementation/`, with Node and Rust on PATH:

```sh
npm run build
node dist/cli.js check ../extensions/semantic-corrections-v1/orders.alch
node dist/cli.js ontology ../extensions/semantic-corrections-v1/orders.alch
node dist/cli.js build ../extensions/semantic-corrections-v1/orders.alch --out /tmp/orders-semantic-bundle
```

The bundle contains `alch-event` (Rust), `handler.mjs` (Node), typed ontology, independent record schemas, generated mappers and backfills, binding contracts, and an exact file manifest. `serve.py` reuses the existing RWO/Ansible provisioning runtime and local delivery worker with bubblewrap isolation.

The trusted operator supplies `ALCH_HOST_TOKEN` (32–256 URL-safe characters) and `ALCH_HOST_POLICY`:

```json
{"actor":"OrderService","grants":["order-transaction-authority"],"operations":["place-order"],"transport_grants":["orders-local"],"isolation":"bubblewrap","consumer":{"actor":"OrderService","grants":["order-transaction-authority"],"operation":"record-order"}}
```

Start the built host with `python3 /tmp/orders-semantic-bundle/serve.py --run-root /tmp/alch-provision-orders-semantic`. It prints the loopback URL. POST to `/functions/orders-local/place-order` with the bearer token and JSON:

```json
{"facts":{"orderId":"o1","payload":{"quantity":2}},"message_id":"m1","expected_version":0}
```

The host owns the clock. Preserve the message ID, facts and expected version when retrying an uncertain result. Public listeners, credentials and existing installations are outside this construction packet.

## Migration

`migration.py` creates a fresh database generation from an immutable snapshot plan. It never selects a live route or rewrites the source database. Stop the source host and drain all outbox messages first. Name every old operation/storage key and its target entity/projection explicitly. Ambiguous merges reject. Legacy fields removed from the active record are retained in `legacy_states`, with original bytes and versions.

For a schema addition, declare a typed default on the entity, rebuild, and let preparation derive eligible missing-field backfills from the generated ontology and default Mapping contracts. An explicit backfill selection remains available. `prepare(database, bundle, ownership, backfills)` binds the source snapshot and exact target bundle. `apply(database, bundle, plan, new_database)` rechecks both and executes the generated default mappers only for missing fields. Existing values, versions, inbox bodies, outbox bodies and commit fingerprints remain intact. Stale plans, target drift, partial preparation, existing output paths and destructive rollback reject. Test receipts cover the non-effectful generation; live cutover remains an operator task.

## Scope and remaining operational work

This slice supports one producer, one consumer, one local SQLite delivery binding, one lifecycle transition and an optional scalar assignment per operation. General SFOL rule blocks, multiple transports, arbitrary nested business-record inference and remote broker dead-letter publication are unsupported and reject. Opaque JSON objects retain their contents, subject to the existing portable safe-integer numeric boundary. The new profile is built by the CLI and served by its generated local host; earlier multi-tenant controller packages retain their historical profiles; the controller in this directory accepts `semantic-host-v1` in a fresh registry root.

The local binding-type prototype still requires its owner's separate upstream admission decision. Product approval, live migration/cutover, production retention/deletion, public deployment and independent live ORODI integration are not manufactured by these tests. The [DAG](PLAN.md), [definitions](DEFINITIONS.md) and execution receipt (referenced result or source binding is not imported) distinguish implemented construction from remaining work.

## Controller successor

`control_plane.py` reuses the bounded asynchronous build queue and tenant policy checks. Start it with `--root <new-private-registry-directory> --config <operator.json>`. Copy [operator.example.json](operator.example.json) and supply hashes of operator-chosen tokens. The listener remains loopback-only.

The HTTP flow remains:

1. `POST /v1/projects/shop` with `{}`.
2. `POST /v1/projects/shop/revisions` with `{"source":"<complete Alch source>"}`; poll the returned revision until ready.
3. `POST /v1/projects/shop/revisions/<id>/prepare` with `{}` to pin the selected baseline and exact target.
4. `POST /v1/projects/shop/revisions/<id>/activate` with `{}` under the configured activation scope.
5. `POST /v1/projects/shop/functions/orders-local/invoke` with the command/envelope JSON shown above.

Preparation compares typed records and execution contracts. Additive state fields derive their generated backfills automatically; changes to input meaning, delivery, authority, runtime, existing properties or record identities require separate explicit migration intent and reject here. Activation drains the old host, rehearses and installs a fresh generation, and commits route and state selection together. Failure recovery rereads durable selection, including when the commit succeeded but its acknowledgement was lost. Startup restores that selection before listening. Existing installations are not imported automatically.
