# Generated service-owned SQLite repositories

The candidate ServiceSqlite family derives initial schema migrations, primary
and unique indexes, repository value conversions and Query statement/mapping
APIs from checked `.alch` source. Formal claims are optional.

The source declares Entity fields, identities, unique keys, immutable/version
properties and Queries. A genuine checked technical profile Mapping selects the
family and table prefix. No per-feature SQL, row conversion or business callback
is authored by the application.

## Source and profile ownership

The internal factory `createCommerceSqliteFamilyOwnerV1` requires genuine Core
source, semantic, stage, computation-domain and local-plan owners and a genuine
derived technical family. They must retain the same original source capture.
A descriptor or JSON clone cannot recreate any owner or original handle.

Service entities derive storage ownership from the checked source ownership map.
The three declared application coordination records derive their owner and
physical suffixes from the captured coordination contract. Technical profile
Entities do not become business tables. Missing or foreign ownership and physical
name collisions reject.

`bindService(service)` issues a private schema handle. `emit(handle)` produces
actual codec/repository TypeScript, an initial SQL migration and validated
persistence mapping JSON. `materialize(handle, freshDirectory)` writes fresh
exclusive TypeScript/JavaScript artifacts and retains original physical file
identities. `loadDataComponent(bundle)` loads those actual generated modules.
These functions do not open a database.

The family uses the existing persistence composition/kernel validators and
mapping, identity, index, conversion and migration contracts. Formation metadata
keeps `runtime_guarantees_observed: false`; source and SQL generation are not
transaction evidence. Initial migrations use explicit CREATE statements and a
single local BEGIN/COMMIT. They are forward-only schema artifacts, with no
implicit database creation, replacement, downgrade or auto-migration on open.
Runtime setup and transaction evidence remain the native store owner's work.

## Lossless storage

Each column uses the original generated value codec. Its storage representation
is canonical JSON text, except an outer optional `none`, which is SQL NULL.

| Source shape | Storage and validation |
|---|---|
| UInt64 | Exact canonical decimal wire string inside JSON text; native values stay BigInt. No Number conversion, floating representation or truncation. |
| Bool and bounded text/refinements | Closed original scalar codec, stored as canonical text. Unicode/scalar/byte/refinement limits are retained. |
| Nullary enum | Closed original enum wire string, with no free string substitution. |
| Algebraic enum | Original kind and declared payload fields; unknown/extra fields reject. |
| Value object or embedded source reference | Complete source fields and invariants, encoded through the original codec. Embedding does not grant a foreign row or table capability. |
| Optional | SQL NULL for outer none; some uses the element's canonical JSON value. A text cell containing JSON null cannot substitute for SQL NULL. |
| Bounded List | Canonical array; order and allowed duplicates are preserved, along with source collection predicates. |

Unknown or unimplemented storage shapes, recursive selected representations,
ambiguous nested optionals and payload/discriminator collisions reject. Decoder
checks reject noncanonical cells, wrong types, extra columns and lossy values.
Whole-record validation preserves actual source invariants after field decoding.
Table and column identifiers are compiler-generated and quoted; values are bound
parameters. Identity/unique keys remain exact source keys. Physical column/index
order is recorded separately from the existing mapping contract's set identity.

## Queries and access boundary

`bindQuery(serviceHandle, originalReadHandle)` accepts only the same local-plan
owner/source/service and exact checked Query. The generated mapping preserves
parameter/context scalar expressions, source predicates, projections, guards,
optional-result wrapping and missing/unavailable actions.

SQL generation requires a translated complete identity/unique lookup for every
source row, including bounded joins. An unsupported key cannot become a broader
scan. Additional predicates that require native context methods or expression
execution remain explicit residual requirements. They must be checked by the
original native Query runtime before any candidate becomes a result.

The generated data component supplies:

- `encodeStoredRecord`, `decodeStoredRecord` and `encodeStoredKey`, which convert
  closed typed values and rows without database access.
- `prepareQueryValues`, which produces SQL/typed bound data and flags original
  context/residual requirements. It accepts data, not authentication evidence.
- `queryDisposition` and `queryResultMapping`, which retain the actual source
  missing/failure/projection/guard contracts for native assembly.

These APIs have no DB handle, `open` or `execute` port. Query declarations,
prepared SQL, context-shaped JSON, decoded values and mapping metadata cannot
mint native database, row, principal or authorization custody. Actual protected
row access must join the original registered store and context owners. The
subsequent native Operation/Query assembly owns projection execution and
committed/rejected/failed/indeterminate outcomes.

The required source Queries retain their specific scope: Catalog.ReadQuote
binds quote and customer; Orders.GetOrder binds order and original customer
context; Payments.ReadPayment binds order and attempt; Inventory.ReadReservation
binds its unique order key. Query data from one service cannot bind another
service's repository handle.

## Compatible profile variation

A second genuine family derived from the same checked technical model with
`tablePrefix: sample_` generates different SQL, schema identities and physical
tables. The business source and compiler remain unchanged. This generation
control does not establish the later whole-application profile-equivalence
witness.

## Validation and current scope

The source tests materialize and import actual generated modules, apply their
SQL in fresh isolated SQLite fixtures, perform typed encode/insert/key-select/
decode roundtrips, check actual unique/composite constraints and query predicates,
and compile emitted TypeScript standalone. They do not activate a live business
database, Auth provider or listener.

```sh
cd craft/projects/domainspec-v2/impl/cli
node --import tsx --test test/commerce-sqlite-family-v1.test.ts
node node_modules/typescript/bin/tsc --noEmit --incremental false
```

## Open Questions

The EC16 generation component is tested against actual emitted modules and
SQLite fixtures, including exact physical index metadata. EC17 owns real
reusable local transactions, replay, inbox/outbox and
commit/rollback/unknown evidence. EC18 owns native async assembly and result
execution; EC19 owns public exports/native capture. EC20+ own actual joined
application witnesses. No source mapping or fixture roundtrip replaces those
owners. Local hosting, TDE, EVF, publication, deployment and live identity,
provider, business database and broker activation remain deferred.
