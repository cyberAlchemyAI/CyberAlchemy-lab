# Proposed storage schemas

These are implementation protocol drafts. They do not replace or admit domain Artifact Type contracts.

| Schema | Purpose | Principal fields |
| --- | --- | --- |
| [Artifact content entry](schemas/artifact-content-entry.schema.json) | Preserve exact bytes in packed content | Content ref, media type, byte SHA-256, size, base64 data, optional separately bound semantic digest |
| [Artifact package manifest](schemas/artifact-package-manifest.schema.json) | Bind review/committed package material and dependencies | Input source cut, content file hash, materials, exact carrier/schema selectors, dependency bindings, transaction/commit refs |
| [Projection generation](schemas/projection-generation.schema.json) | Describe one disposable artifact read-model cut | Source cut, pinned projector, catalog/row hashes, source verification, coverage and posture; no replay authority |
| [File generation](schemas/file-generation.schema.json) | Describe selective byte-exact or rendered outputs | Selection, source cut, exact output paths/hashes, input hashes and pinned renderer where applicable |
| [SQLite read model](schemas/sqlite-read-model.sql) | Store structured disposable query rows | Generation/watermarks, byte cache, revisions/heads, typed relations, contracts, reference resolution, authority evidence, ontology joins and gaps |

## SQL tables

1. `projection_generation`: independently source-bound generation metadata.
2. `stream_watermark`: distinct stream cursors and head hashes.
3. `content_cache`: optional exact bytes indexed by digest; not the sole retained content.
4. `artifact_revision`: heterogeneous carrier bodies, exact revisions and separate status facets.
5. `artifact_head`: calculated current revision per scoped identity at the selected generation.
6. `typed_relation_projection`: exact global relation identity, kind revision, endpoint revisions and qualifier bytes.
7. `contract_binding_projection`: schema bytes/selectors, identity extraction and discriminator mapping.
8. `reference_resolution`: resolved, historical, excluded, ambiguous or missing references.
9. `authority_fact_projection`: evidence of selected Decisions and their scoped outcomes.
10. `ontology_representation_link`: exact represented artifact and independent ontology cursors/mapping.
11. `projection_gap`: unresolved obligations and permitted-use blocking information.
12. `active_generation`: a read-model pointer; no canonical admission effect.

There is no SQL table that gives an Agent a persistent working memory. Eligible session/audit artifacts are ordinary governed revisions. Ephemeral working memory remains outside durable artifact persistence.

## Required checks beyond JSON Schema / SQL

- Decode base64 strictly and compare original byte hash/length; `contentEncoding` is an annotation, not sufficient validation.
- Verify whole content file hash, exact material membership, uniqueness and manifest/body agreement.
- Resolve schema content, carrier version, identity selector, every required dependency and endpoint; validate each body under its exact schema.
- Establish actual authorization, trust roots, expected head, effect scope, replay and deterministic consequences.
- Verify semantic digest only with its exact selected algorithm; do not substitute it for original-byte verification.
- For byte-exact outputs, require equal input/output hashes; for rendering, require the pinned renderer and exact input selection.
- Verify managed paths and reject traversal, symlink escapes, duplicate output paths and collisions with authored/unmanaged files.
- Compare projection rows/gaps with independent canonical replay; a valid database/foreign-key graph is not authority evidence.

## Example and validation ceiling

[Exact-content example](examples/content-entry.json) wraps original bytes of the existing first governed Work record. It is transport material with no new admission. The authoring receipt checks schema well-formedness, this example's byte round trip, SQL DDL creation in a temporary in-memory database, source bindings and local links.

That receipt does not demonstrate a complete package, database projector, publisher, rendering runtime, crash recovery, admission, migration or performance. The proposal does not rerun or modify the frozen Lab/ontology runtime packages.
