# Compatible Alch revision upgrades

Private product-construction candidate. Owner: Alch host implementation; Craft
ORODI consumes related evidence. Authority effect: none.

Compatible revisions now share one function-owned database. Updating v1 to v2 and
rolling back to v1 preserves orders, state versions, outbox messages and inbox
receipts. Selected hosts restart before the control plane starts listening, so
pending event delivery resumes without an incoming function call.

This successor reuses [asynchronous builds](../async-control-plane-v1/README.md),
the existing DomainSpec 1.0.0 compiler, Rust event runtime, Bubblewrap invocation
boundary, and RWO/Ansible provisioning. Previous candidate packages remain intact.

## Compatibility is deliberately strict

[compatibility.py](compatibility.py) derives a digest from:

- The entire compiled event configuration, excluding only its source-binding digest.
- Function identity, runtime, event/isolation selection, operation, actor/boundary,
  consumer and transport bindings.
- Generated Rust runtime source, Cargo manifest/lock, and the local worker source.

Consequently the first supported changes are comments and host timeout/request-size
limits. Changes to fields, rules, mappings, events, message identities, delivery
policies, consumers, or runtime implementation are rejected as
`INCOMPATIBLE_REVISION`. Even harmless rearrangements may be rejected by this exact
comparison. This is not a general schema migration or behavioral-equivalence proof.

[orders-v1.alch](orders-v1.alch) and [orders-v2.alch](orders-v2.alch) demonstrate a
five-second to six-second invocation deadline change with the same business and
storage contract. Their generated source digests differ; their compatibility
contract is identical. No application logic is rewritten in the host.

## Handoff DAG

```mermaid
flowchart LR
  C[Verify candidate and compatibility] --> Q[Pause old producer]
  Q --> D[Finish in-flight calls and drain outbox]
  D --> L[Stop old host and release state lock]
  L --> H[Start candidate on the same database]
  H --> V[Verify isolated runtime readiness]
  V --> R[Commit selected route]
  R --> T[Upgrade, rollback and restart tests]
```

[definitions.md](definitions.md) defines function-owned state, compatibility,
drained handoff and compatible rollback with formal, plain-language and Alch-context
voices. [ontology.json](ontology.json) is an agent navigation scaffold linking the
business/product contract to existing Alch/DomainSpec and compiled runtime surfaces.
[PLAN.json](PLAN.json) separates product construction from operational support.
No canonical definition, ontology admission or operational authority is promoted.

The storage key is derived from `(control-plane root, tenant, project, function)`.
Revisions do not enter that key. RWO/Ansible provisions the corresponding opaque
local root. Its function binding records the compatibility digest and state key;
the generated Rust executable mounts only its runtime data directory. The host
holds an exclusive provisioning-root lock for its entire lifetime.

Activation checks compatibility before pausing the old host. Its private drain
endpoint rejects new producer calls and waits for the invocation slot and outbox.
The existing claim/consumer/settlement adapter handles every message; the controller
never forces a queue row into a completed state. A `dead` row or stopped delivery
worker returns `DRAIN_BLOCKED`. Remaining work after 35 seconds returns
`DRAIN_TIMEOUT`. The old route stays selected and the producer is resumed.

After successful draining, the controller stops the old host and waits for its
lock to be released. It starts the candidate against the same database and runs a
real isolated Rust inspection before declaring readiness. Only then does a SQLite
transaction update the selected route and journal. There is a bounded interruption
between hosts; this prototype does not claim zero-downtime upgrades.

If startup or route selection fails, the controller reads the durable route and
restores the revision actually selected there. A recovery failure is recorded as
`host-recovery-required`; it cannot turn into a successful activation response.
If the controller dies before the route transaction, the old revision remains
selected. If it dies after the transaction, the new revision is selected. Managed
hosts receive the existing Linux parent-death signal, and startup replays the
selected route against the shared state. Startup refuses to serve if a selected
host cannot be restored.

A first activation that fails after initializing a storage binding may leave its
private root bound to that compatibility contract. It is not automatically wiped
or repurposed. Existing-root cleanup/migration needs a separate operator procedure.

Rollback uses the same activation endpoint and handoff. It changes the selected
code revision and retains the current database; it does not restore an older data
snapshot. Completed message fingerprints and inbox receipts remain valid across
all accepted revisions. Earlier observations retain their original source digest.

## Running and using revisions

Use the predecessor's Node 26.8.1, Rust 1.95.0, cached Cargo, Bubblewrap and built
RWO bridge prerequisites, plus its
[operator configuration](../local-control-plane-v1/operator.example.json).
Select a **new private mode-0700 control-plane root**. Synchronous and asynchronous
prototype stores are not migrated automatically. The persisted support marker
binds this successor, its host/compatibility modules and its predecessor code.

From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/compatible-upgrades-v1/control_plane.py \
  --root /tmp/alch-compatible-demo --config /path/to/private-operator.json
```

The upload/status/activation/invocation endpoints and bearer-token scopes are those
of the [asynchronous API](../async-control-plane-v1/README.md#running-and-api):

1. Create a project and upload `orders-v1.alch`; poll until ready, then activate it.
2. Invoke `place-order` through `/v1/projects/shop/functions/orders-local/invoke`.
3. Upload `orders-v2.alch`; poll until ready and activate its revision ID.
4. Invoke again with the next expected version and a new message ID.
5. Activate the v1 revision ID to roll back code while retaining both commits.

For a repeated request, reuse exactly the original facts, message ID and expected
version; the Rust producer returns `already-committed`. Reusing a message ID with
different facts remains a conflict. An activation timeout/connection loss has an
unknown client outcome: read the project's selected route before deciding to retry.

Activation returns the selected revision and opaque `state_key`. Internal drain
and resume endpoints live only on the host's private bearer-protected listener;
they are not forwarded through the tenant API. Tenant credentials and operator
policy cannot be overridden by uploaded Alch source. Different tenants using the
same project/function names get different state keys and databases.

## Recovery and tests

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/compatible-upgrades-v1 \
  -p test_upgrades.py -v
```

The tests build real Alch sources, run RWO/Ansible and isolated Rust hosts, and
check durable SQLite effects. They cover v1 -> v2 -> v1, producer replay, consumer
deduplication, rejection of an incompatible mapping, separate tenant storage,
eager pending delivery after restart, draining a scheduled pending message,
readiness failure with restoration of the old host, a committed consumer with lost
settlement, and dead-message rejection. Compatibility mutation checks also bind
model, execution/identity, transport and runtime bytes.

Delayed availability, expired leases and dead rows are injected only into owned
test databases; runtime producer/consumer calls create the business data. The
readiness failure is injected after starting a real candidate host and before
route selection. It does not claim exhaustive process-crash testing at every
instruction. See validation.json (referenced result or source binding is not imported), [source-manifest.json](source-manifest.json),
and test-results.log (result record excluded) for the exact evidence.

## Limits and remaining work

| Lane | Frontier or residue | Owner | Stage |
| --- | --- | --- | --- |
| Product construction | Compatible state-preserving handoff and eager delivery recovery | Alch host owner | Candidate and product tests |
| Product construction | Explicit state migrations and wider compatibility rules | Alch/DomainSpec owners | Runnable successor design |
| Product construction | Bounded concurrent HTTP requests and multiple credentials | Alch host owner | Runnable successor design |
| Operational support | Existing per-revision data migration, cleanup and backup policy | Alch operator | Deferred; new-root prototype has no migration prerequisite |
| Operational support | Public hosting, aggregate quotas and security review | Platform/security owner | Deferred public deployment |
| Operational support | Live ORODI health evaluation | Craft ORODI owner | Deferred runtime evidence |

The service remains loopback-only. Builds remain asynchronous with the same queue
limits; HTTP requests serialize, including drain/startup during activation. At most
eight function hosts run per controller. No aggregate cgroup/filesystem quota,
remote deployment, general migration, or independent live ORODI readiness claim
follows from these local tests.

## Open Questions

- Which authored DomainSpec migration contract can safely widen compatibility to changed rules and state shapes?
- What explicit resolution contract should handle dead messages before an upgrade?
- Should draining and activation become asynchronous jobs with a bounded concurrent API?
- Which ORODI profile should expose handoff failures, pending delivery and state-binding health?
