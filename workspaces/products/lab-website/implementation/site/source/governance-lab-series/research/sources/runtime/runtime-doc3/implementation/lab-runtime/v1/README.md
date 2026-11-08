# CyberAlchemy Lab operational runtime candidate

An on-demand local CLI for source-bound state inspection, exact authorized transactions, verified replay, and ephemeral Agent context. The repository baseline is Decision 0074. The implementation is a candidate; source admissions do not admit this implementation or activate a product service.

The [reviewed plan](../../../docs/plans/0008-lab-operational-runtime/PLAN.md), [implementation analysis](../../../docs/plans/0008-lab-operational-runtime/IMPLEMENTATION-ANALYSIS.md), [plan review](../../../docs/plans/0008-lab-operational-runtime/PLAN-REVIEW.md), [profile](profile.json), and [protocol contract](CONTRACT.md) define its boundary.

## Inspect the real repository

From repository root, using Python 3 and the packages in `requirements.txt`:

```bash
python3 implementation/lab-runtime/v1/lab.py verify
python3 implementation/lab-runtime/v1/lab.py status
python3 implementation/lab-runtime/v1/lab.py catalog --category definition --current
python3 implementation/lab-runtime/v1/lab.py inspect product-capability:cyberalchemy-lab:governed-knowledge-lifecycle --record
python3 implementation/lab-runtime/v1/lab.py query Lifecycle
python3 implementation/lab-runtime/v1/lab.py query Authority
python3 implementation/lab-runtime/v1/lab.py query Provenance
python3 implementation/lab-runtime/v1/lab.py query product-capability:cyberalchemy-lab:governed-knowledge-lifecycle --direction outgoing --depth 1 --predicate relation.derives-from
python3 implementation/lab-runtime/v1/lab.py rebuild --out .local/lab-runtime/governance-graph.json
```

Reads work before store initialization. The profile binds four exact admission bundle roots, their files, the current registries and dependencies, implementation evidence, and this runtime's selected implementation files. Every current source is checked again. A stale store can report its frozen records and drift, but emits no confirmed current traversal paths. Writes, context preparation, verification and graph rebuilding require current source bytes.

Queries preserve kind/status/confidence/commitment/provenance/owner/residue independently. They report source candidate fields separately from effective admission and retain the closed D73 Agent disposition. Confirmed global edges bind exact versions and qualifiers. The historical D73 predecessor-version discrepancy is visible as a diagnostic. Local `transition-from` paths bind exact Project history events; they do not create a replacement global `successor-of` relation.

## Provision a local operational branch

Choose a store identity and operator identity. Provisioning a public key declares who may approve **that local store's** allowed effects and scope. The runtime authenticates approvals within this explicitly provisioned boundary; it is not a general organization permission evaluator or external identity verifier. Private keys stay outside the repository and store.

```bash
mkdir -p "$HOME/.config/cyberalchemy-lab"
chmod 700 "$HOME/.config/cyberalchemy-lab"
python3 implementation/lab-runtime/v1/lab.py keygen \
  --private "$HOME/.config/cyberalchemy-lab/local-owner.pem" \
  --public "$HOME/.config/cyberalchemy-lab/local-owner.pub"
python3 implementation/lab-runtime/v1/lab.py init \
  --id lab-local --owner role:repository-owner \
  --public-key "$HOME/.config/cyberalchemy-lab/local-owner.pub"
```

The default store is `.local/lab-runtime/store`, already ignored by Git. Use global `--store PATH` before the command for a separate operational branch. An existing store is never overwritten. An incomplete genesis is preserved for inspection; initialize a fresh path rather than guessing its state. A future repository epoch requires an explicitly reviewed source-profile update and a new baseline/store; this version never silently rebases committed local history.

## Prepare, review, authorize and apply

`example` creates a planned Work record with no asserted completion. The proposal is inert until an exact signed approval is supplied.

```bash
python3 implementation/lab-runtime/v1/lab.py example --id first-local-work --out .local/lab-runtime/first-work.json
python3 implementation/lab-runtime/v1/lab.py review .local/lab-runtime/first-work.json
# Inspect the exact proposal JSON before this operator authorization command.
python3 implementation/lab-runtime/v1/lab.py authorize .local/lab-runtime/first-work.json \
  --private-key "$HOME/.config/cyberalchemy-lab/local-owner.pem" \
  --out .local/lab-runtime/first-work-approval.json
python3 implementation/lab-runtime/v1/lab.py apply \
  .local/lab-runtime/first-work.json .local/lab-runtime/first-work-approval.json
python3 implementation/lab-runtime/v1/lab.py verify
python3 implementation/lab-runtime/v1/lab.py status
```

The signature binds the complete proposal, stable independent Decision cores, approval time, owner, store, policy, challenge route, scope, expected HEAD and frozen source snapshot. One approval can cover multiple independent targets. One atomic Admission Transaction appends both histories, creates the successor Project State, binds registry/index outputs, and records the receipt. It also materializes inspectable Decisions, exact scopes, the resolved bundle/checkpoint/authority boundary, and six declared existing-axis connections for membership, succession and deterministic outputs. `review` lists these consequences before authorization. They need no second approval or bookkeeping Decision. Repeating identical applied bytes returns the same receipt; conflicting ID reuse fails.

Supported target categories are artifact instances, Typed Relations, Definitions, Artifact Type registrations and Relation Kinds. Operations are admission, exact revision and withdrawal. Historical source bytes remain unchanged. New records use current carriers. New type packages use the admitted metamodel's explicit `registered_types` descriptor schema plus a closed runtime package binding; this does not assert that the descriptor is a full canonical metamodel instance. Relation extensions require declared endpoint carriers and directional roles; actual connections must also satisfy the current Typed Relation schema, exact versions and qualifier contract. Existing unresolved source relations remain diagnostics and cannot justify new edges.

The new local state always reports its store identity and local admission boundary. It does not rewrite the admitted repository or manufacture a Decision 0075. Adopting the implementation, publishing operational records back into repository authority, or activating an external consumer requires its own exact review and Decision.

## Recovery

Transactions are immutable. An exclusive OS file lock serializes writers. A complete transaction and pending record are synchronized before one atomic `HEAD.json` replacement publishes every consequence. Readers bind one HEAD and replay its committed chain. Runtime source links name the store, transaction file and JSON selector; their digest covers canonical selected record bytes. Pending/orphan files never become visible as committed state. After interruption, `status` reports recovery material; writes stop until recovery.

```bash
python3 implementation/lab-runtime/v1/lab.py status
python3 implementation/lab-runtime/v1/lab.py recover --expected-head EXACT_HEAD_DIGEST_FROM_STATUS
python3 implementation/lab-runtime/v1/lab.py verify
```

Recovery validates committed history and the expected HEAD, preserves all committed transactions, and removes only recognized pending/staging material or the immediate uncommitted next transaction. Unknown future transactions are preserved for inspection. File and directory synchronization are implemented; the verification scope is local process interruption on this filesystem. Power-loss durability and multi-host writes are not established.

## Agent context and memory

```bash
python3 implementation/lab-runtime/v1/lab.py session product:cyberalchemy-lab --ttl 900
```

Inside the process, enter `context`, `note TEXT`, `memory`, or `close`. EOF also closes it. `--context-only` exports a schema-valid candidate Context View, Ontology/View/Cut, projected Nodes/Edges and Agent records, then immediately closes the session. The packet states that disposition; it is a historical preparation result, not an active session credential.

Context binds the committed HEAD, selected source bytes and separate event cursors. A changed HEAD, source drift or TTL expiry invalidates use. Notes live only in process memory, are bounded, and are erased on close/expiry. The next session starts empty and reconstructs context from Project State. A lesson, failure assessment, observation or work outcome can become durable through an explicit schema-backed proposal and approval; a note itself never changes Project State.

## Repeatable validation

```bash
python3 implementation/lab-runtime/v1/validate.py --write-receipt
python3 implementation/lab-runtime/v1/demo.py
```

The suite reads real D74 sources and uses temporary stores and owner keys for all writes. It covers all five target categories, revisions/withdrawal, explicit relation extension, signed multi-target admission, malformed/stale requests, source drift, exclusive writers, tampering, fresh-process replay, interruption before/after HEAD, recovery, context invalidation and session memory expiry. The demonstration does a real local work admission and opens/closes context in a disposable store. Neither operation changes repository authority.
