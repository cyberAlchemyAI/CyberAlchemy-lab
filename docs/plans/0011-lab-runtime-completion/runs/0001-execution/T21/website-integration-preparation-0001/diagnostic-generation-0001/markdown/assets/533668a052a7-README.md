# v4 — migration and update runtime prototype

v4 imports all 20 inventory-listed legacy packages plus the Lab Ontology Product
foundation: 21 exact source-qualified packages. It includes the five adapters
missing from v3, 815 graph nodes, 1,210 relations and 422 supporting documents.
It preserves v2, frozen v3 and all source files.

## Run the demonstration

From the Lab root:

```bash
cargo run --release --offline --locked --quiet --manifest-path implementation/bindings/ontology-product-event-runtime/v4/Cargo.toml -- summary .local/ontology-source-runtime-v4-prototype
```

The persistent prototype contains the imported corpus and one extra demo node,
created and updated through canonical events. A fresh process replays those
events. It is an on-demand CLI, not a daemon or network service.

Use `export` to inspect full records and documents; append a package key from
`source-manifest.json` for one package. Use `observe` for Context references,
including endpoint closure for cross-package relations. Unknown packages fail.

The demonstration record belongs to package:
`pkg-999a52d7101c125757adfff34955144da5a24824d0401caf6dfc839fc3099163`.

The provided `commands/create.json`, `update.json` and `retire.json` show the
closed write request. The first two have already been applied to the demonstration.
Reusing update with expected version 1 should fail, because that subject is at
version 2. To retire only this prototype demo record:

```bash
cargo run --release --offline --locked --quiet --manifest-path implementation/bindings/ontology-product-event-runtime/v4/Cargo.toml -- apply .local/ontology-source-runtime-v4-prototype implementation/bindings/ontology-product-event-runtime/v4/commands/retire.json
```

Retirement changes a calculated representation, not a source document. It writes
a new transaction; never edit an old transaction. Retiring a node with active
incoming or outgoing relations is rejected until those relations are retired.

## Coverage and meaning

`source-manifest.json` is the exact read allowlist. Each registry selector,
field mapping, directional mapping and cross-package alias is explicit.
Relations without declared IDs use a type/source/target tuple hash; duplicates
fail. All 11 DomainSpec profiles retain distinct identities.

The common storage graph namespace is administrative. Package identity stays
in subject IDs and source bindings, with no merging of source meaning or
authority. Supporting documents are inert UTF-8 text with exact original hashes.
This preserves metadata, rule registries, definitions and full Define node
documents. It does not execute their rules or treat references as admitted.

The source-record profile validates a closed JSON envelope and record digest,
not every domain's semantic schema. JSON numbers use arbitrary precision.
Challenge contracts, confidence, forbidden-collapse rules and source lifecycle
are retained as source data. Runtime lifecycle describes representation
existence, not source admission or promotion.

Scope is the exact manifest, not every file in every repository. References to
documents outside this allowlist remain unresolved source references; no
transitive dependency closure, source-current claim for referenced bytes,
DomainSpec compilation, or domain-schema conformance is inferred.

## Transactions and recovery

Each immutable transaction contains exact semantic/governance event pairs.
The transaction digest chain and atomic HEAD switch define committed history.
An exclusive writer lock prevents concurrent writers from bypassing expected
versions. Readers see the committed HEAD snapshot.

A pending file or orphan next transaction is not committed. New writes stop
until recovery. Inspect `HEAD.json`, then use:

```text
recover <runtime-directory> <exact-current-head-digest>
```

Recovery takes the lock, verifies committed history and the expected head,
and removes only PENDING.json, HEAD.pending and the uncommitted next transaction,
if present. It reports the removed files. Committed transactions are retained.
A stale writer lock is never stolen automatically; operator investigation is
required. An interrupted genesis with no committed HEAD is preserved for
inspection, not automatically resumed. These tests are not a power-loss,
multi-host or production durability certification.

## Verify

```bash
PYTHONDONTWRITEBYTECODE=1 python3 implementation/bindings/ontology-product-event-runtime/v4/validate.py
```

The acceptance harness verifies exact candidate material, 23 focused tests,
all source records and documents, deterministic stores, restart, cross-package
Context, real create/update/retire, stale rejection, recovery, and local timing
bounds declared in DEFINITIONS.md before measurement.
Timings use a prebuilt release binary; compilation is excluded. The earlier
debug-build attempt failed the query timing bound and issued no PASS receipt.

DAG construction A–L is tracked in DAG.json. Product approval is deliberately
absent. OPERATIONS.md contains a no-effect cutover/rollback proposal; no
publication, admission, live cutover, or source retirement is performed.
