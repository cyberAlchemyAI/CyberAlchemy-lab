# Sibling ontology import completed

`../cyberAlchemy-v2 -> exact source manifest -> Lab event store -> verified export`

**Import** means the selected source data now exists in a persistent Lab event store and can be read back through the runtime.

Imported 20 legacy ontology packages plus the Lab foundation: 815 nodes, 1,210 relations and 422 supporting documents. The import uses 418 distinct source files. All source hashes matched before and after execution.

The source manifest changes only the legacy root location from the approved v4 manifest. The approved implementation and original evidence remain byte-identical.

## Read the imported data

From the Lab root:

```bash
implementation/bindings/ontology-product-event-runtime/v4/target/release/cal-ontology-source-runtime summary .local/ontology-source-runtime-v4-sibling-import
```

Replace `summary` with `export` for complete records and documents, or `observe` for the Context projection. These commands do not change the store.

## Verification

All 23 Rust tests passed. Two temporary imports produced identical files. Every exported record and document matched its source. A fresh process replayed the persistent import to the same result. Create/update/retire was exercised only in temporary storage. The persistent corpus has no extra demonstration records.

[execution.json](execution.json) records the candidate, manifest, binary and event-file hashes. [verification.json](verification.json) binds the current test log and execution receipt.

Local Rust was present outside PATH. A missing dependency was fetched using the unchanged lockfile. GCC and libc development files were extracted under `.tmp/import-toolchain` to supply the missing linker without system installation. The event store lives under ignored `.local/`; execution evidence is stored here for review.

## Remaining migration scope

This completes the approved manifest's ontology-data import. It does not mean that every file in the sibling repository has migrated, or that imported source definitions have become active Lab definitions. Source files are retained and no consumers were switched.

`Imported source data -> reconstruct remaining Lab artifact families -> verify their behavior`

The separate reconstruction ledger covers 195 normalized targets across definitions, artifact types, profiles, relation kinds and derived surfaces. Those targets require comparison against current Lab packages before selecting the next import batch; event-store coverage alone does not establish their completion.

## Open questions

The broader migration inventory and source-owner interpretation questions remain owned by the reconstruction ledger and ontology review index in `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/`. Consumer cutover remains a separate runtime/consumer-owner task.
