# Plan review after implementation analysis

Reviewed 2026-10-07 against `IMPLEMENTATION-ANALYSIS.md`. Outcome: proceed with the full local runtime DAG after these corrections.

1. **Currentness:** seed at D74, not the D73 examples in Plan 0007. The historical D73 version mismatch remains a diagnostic; it is not silently fixed.
2. **Scope retained:** deliver reads, reusable governed changes, both histories, Project State, receipts, concurrency/recovery, and ephemeral Agent contexts. Completing the read CLI alone is insufficient.
3. **Contract fit:** dispatch through exact current type contracts and identity/discriminator rules; use JSON Pointer for composite schemas. Preserve historical types for historical reads. Closed Typed Relation qualifiers and exact endpoint versions are mandatory for writes.
4. **Authority boundary:** provision a local owner's public key and declared allowed effects at store initialization. Approval signs exact proposal digest, base HEAD, source snapshot, scope and stable Decision cores. Candidate authoring is not approval. No general identity/permission claim is made.
5. **Atomicity:** replace cross-file exception rollback as the new runtime's commit strategy with immutable whole-transaction records and one atomic HEAD. Directory synchronization, pending detection, explicit recovery, idempotency and stale-head checks are required before session integration.
6. **Graph semantics:** use closed ontology-local edges for source/contract/Decision/implementation traceability; project global Typed Relations only with exact endpoint/qualifier resolution. Unknowns are visible. No catch-all global kind is created.
7. **Memory:** session memory is ephemeral and never a Project State input by itself. A proposed lesson, failure record, or work output becomes durable only through an exact authorized transaction under its admitted carrier.
8. **Reuse choice:** build the initial CLI/read model in Python; retain the Rust graph adapter as future technology integration. Tests must cover actual multi-step transitions and fresh-process replay, not just serializer parity.

The reviewed DAG is unchanged in dependencies: A→B→C→D, then E/F, G/H, I→J, K→L. D includes the ontology profile that Plan 0007 calls C2. E/F/G deliver its effective-state, catalog and graph obligations. A later admission review can reuse this implementation evidence without treating it as admission.

## Schema-fit correction from implementation probes

The metamodel v3 schema fixes its own identity/name/version and cannot validate an arbitrary type declaration as that root instance. Its explicitly declared `registered_types` item schema does validate registration descriptors. New local type packages therefore use that exact schema slot and a closed runtime binding for instance identity/discriminator, schema digest, and directional relation roles. The descriptor is reported as a local registration; it is never presented as an admitted canonical metamodel root instance. Existing canonical Definition records retain v1 representations; new writes validate against the current v2 carrier. These corrections retain type/Definition management in the runtime scope without relaxing canonical schemas.

## Completion contract

Every A–L node must have concrete file/command/test evidence. Verify the real D74 state and catalog; deterministic graph queries with exact status; signed multi-target transaction and declared consequences; stale/malformed/unauthorized writes rejected without HEAD changes; process interruption and recovery; tamper detection; bounded views and ephemeral memory; CLI help, operator examples and final audit. Full-scope completion remains unproven until those checks pass.
