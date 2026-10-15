# Storage option comparison

## Verified current implementation

- [Ontology v4 storage](../../../implementation/bindings/ontology-product-event-runtime/v4/src/storage.rs) persists immutable transaction frames with semantic/governance pairs, a digest chain, writer lock and atomic HEAD. It is a filesystem event store.
- Its [README](../../../implementation/bindings/ontology-product-event-runtime/v4/README.md) limits source-record import to selected packages/envelopes. Domain conformance, transitive closure and source admission are not supplied by that representation store.
- The [ontology graph read model](../../../ontology-lifecycle/runtime-candidates/cal-ontology-graph-read-model/v1/README.md) is a disposable Rust index with `canonical_replay_source: false`. It is not an SQLite implementation.
- [Lab v2 storage](../../../implementation/lab-runtime/v2/lab_runtime/store.py) embeds target records, approvals and consequences in immutable local transactions and independently verifies replay. Local effects do not become repository admission effects.
- [Source capture](../../../implementation/lab-runtime/v2/lab_runtime/sources.py) retains parsed JSON and byte hashes; it does not retain every original material's raw bytes. A generalized exact-file reconstruction promise requires additional content closure.

## Alternatives

| Criterion | A: canonical SQLite events/content, generated files | B: individual canonical files, SQLite index | C: immutable transaction packages, SQLite index, selective files |
| --- | --- | --- | --- |
| Event sourcing possible | Yes, using append-only application event tables | Yes, through existing transaction history | Yes; extends the existing transaction pattern |
| Canonical commit | SQLite transaction | Existing file/bundle commit | Verified package/history commit |
| Exact content | Store original BLOBs, contracts and all replay inputs | Preserve original files | Preserve exact bytes inside packages and complete pinned dependencies |
| Query access | SQL directly, with explicit state projections | Rebuildable SQL projection | Rebuildable SQL projection |
| File quantity | Few database/runtime files; exports selective | Canonical file quantity remains | Fewer files for new operational records by packing; growth still needs a policy |
| Git review | Explicit logical export/diff; binary DB is not a useful semantic merge | Fits current repository review | Authored files retained; package changes require logical target diffs |
| Recovery dependency | DB custody, migrations and consistent backup/restore | Existing files/transactions | Existing transaction discipline plus new package/byte closure |
| Migration burden | Highest: shifts canonical storage/custody | Lowest, but does not solve file proliferation | Moderate, incremental and selected |
| Fit now | Possible future route requiring explicit Product selection and proof | Good initial index-only slice | Recommended target architecture; construction still required |

A remains a valid architectural option. SQLite supports local application formats, containers and internal analytical storage; its documentation supports those uses. This is not evidence that A is faster for this repository. [SQLite use cases](https://www.sqlite.org/whentouse.html).

SQLite permits multiple readers and one write transaction at a time. WAL can allow readers during writes, but does not create application-level semantic event history. Its concurrency and same-host constraints must be considered if later selected. No WAL configuration or dependency version is adopted here. [SQLite transactions](https://www.sqlite.org/lang_transaction.html), [SQLite WAL](https://www.sqlite.org/wal.html).

## Why C is the current recommendation

It preserves exact review and immutable transaction semantics while providing structured artifact queries. It allows new high-volume operational content to be packaged rather than generating one filesystem file per artifact. It preserves authoring and Git review where those are valuable. The ontology remains a representation with exact input bindings instead of becoming the authority owner for every artifact type.

The performance verdict is **not evaluated**. No comparative latency, throughput, file-count or storage benchmark has run for this architecture. The verdict is design fit, supported by current implementation inspection and an independent critique.

## Conditions that would favor canonical SQLite

Reconsider A when the Product explicitly selects database-first custody, managed application writes, database migrations and verified backup/restore; uses Git mainly for code and logical exports; and measurements show that transaction volume/inode pressure make package files inferior. Require exact-content export/import, authorization/replay parity and proven failure recovery before changing canonical storage.

Choosing SQLite as canonical storage does not require abandoning event sourcing. It requires an exact storage migration and trust/recovery design. Putting projected ontology state in a database alone does not establish a canonical artifact event store.

## Separate effects on quantity and space

- SQL indexing improves discovery and joins; it leaves canonical file count unchanged.
- Packaging controls files generated for new committed content.
- Selective materialization avoids creating every JSON/Markdown view by default.
- Byte-addressed deduplication may reduce repeated content, but indexes, caches and the proposed base64 transport can increase total space. Base64 has encoding overhead; no storage saving is claimed.
- One package per transaction still grows with transaction count. Segment rotation/archival needs separate design if measurements justify it. No existing source or committed history deletion is proposed.
- Existing cumulative history carriers may require full version content. Replacing them with deltas or derivation recipes needs exact carrier/generator fit; this proposal does not silently change them or claim bounded growth.
