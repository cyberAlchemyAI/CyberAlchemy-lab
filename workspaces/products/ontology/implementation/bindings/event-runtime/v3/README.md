# Source ontology importer v3 — test candidate

This successor imports actual node and relation records, not just the navigation
map. It runs beside binding v2 and does not modify its code, source documents,
adoption decisions or active event store.

## Try the prototype

From the Lab root:

```bash
cargo run --offline --locked --quiet --manifest-path implementation/bindings/ontology-product-event-runtime/v3/Cargo.toml -- observe .local/ontology-source-importer-v3-prototype
```

Use `export` instead of `observe` to print the original records reconstructed
from event-calculated state. Both commands accept an optional exact package key
from `source-manifest.json`. An unknown package fails rather than returning an
empty success. Commands run on demand; no background service is installed.

To independently import into your own NEW directory with an existing parent:

```bash
cargo run --offline --locked --quiet --manifest-path implementation/bindings/ontology-product-event-runtime/v3/Cargo.toml -- import implementation/bindings/ontology-product-event-runtime/v3/source-manifest.json /tmp/my-ontology-import
```

The target must not exist. Do not rerun import into the demonstration directory.
An interrupted import is marked incomplete and preserved, not silently resumed.

## Model

```text
exact source manifest --selects--> profile-qualified packages
package node/relation records --preserved in--> source-record envelopes
envelopes --carried by--> complete-state semantic events
source-owner provenance --joined by--> governance events
Rust replay --calculates--> latest subject snapshots
selected snapshots --project into--> Context
source export --compares with--> every selected original record
```

The isolated kernel is a copy of the existing 2,216-line Rust library, with
a prototype closed source-record profile and a pure import-history preflight.
The original kernel is unchanged. `kernel-provenance.json` binds that base.

The property envelope has exactly two fields: `source_record` (the complete JSON
object) and `source_binding` (package key, source path, document SHA, JSON pointer,
and record SHA). JSON value types and nested fields are retained. This is
lossless data preservation, **not** semantic validation of every source ontology
schema or an admitted DomainSpec profile. Original challenge contracts,
confidence, lifecycle and authority fields remain original source data.
The importer itself grants no authority, chooses no lineage winner, and does
not activate imported challenge contracts. Runtime lifecycle 'active' means the
imported representation exists; it does not promote the source lifecycle.

## Coverage and limitations

The manifest selects 16 packages: 15 legacy registries plus the tested Lab
Ontology Product foundation. All 11 identically named DomainSpec profiles retain
distinct path-qualified package identities. Five specialized legacy packages
are listed in `unsupported`, including the Define cross-package graphs.
No source records from those five are claimed imported.

Each selected nodes/relations array is covered completely, with no row dropping.
Registry-level metadata, separate rule files, definitions, source documents,
and vocabulary arrays are not themselves reconstructed by this version.
Their references remain in source records; reference targets are not implicitly
loaded, admitted, or asserted dependency-closed.

The supported relation mappings require endpoints within their selected package.
Cross-package endpoint adapters remain explicit work. Initial import and read-only
inspection are implemented; a public incremental-update CLI is not. The kernel
test verifies latest-event snapshot behavior, not a new admitted writer API.

## Verification and construction lanes

```bash
PYTHONDONTWRITEBYTECODE=1 python3 implementation/bindings/ontology-product-event-runtime/v3/validate.py
```

The validator checks frozen bytes, runs 16 Rust tests, imports the real corpus
twice, compares event files byte-for-byte, restarts replay, exports and compares
every original record, and checks Context selection and v2 preservation.

Product construction: this bounded importer is the testable candidate.
Runnable follow-on construction: adapters for the five explicitly listed
packages and richer domain-specific property validation. These are not claimed
completed by this candidate.

Operational support: the isolated prototype demonstration is owned by the
runtime owner. Final Product review is not inferred. Admission, cutover,
source retirement and publication remain deferred owner work and do not block
prototype construction. Existing sources and the active v2 instance are retained.
