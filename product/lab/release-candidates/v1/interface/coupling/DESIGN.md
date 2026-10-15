# Signed endpoint coupling for the operator candidate

Status: candidate construction, partial R03 work. Authority effect: none. Actual
owner outcome: absent. This package does not close the complete operator/API
surface or W07 integration by itself.

## Selected semantics

The C14 proposal names two exact mappings:

| Carrier | Raw carrier kind | Endpoint kind | Exact identity field |
| --- | --- | --- | --- |
| Project Identity/v1 | project-identity | project | project_id |
| Product Identity/v2 | product-identity | product | product_id |

Their original schemas, descriptor/Definition revisions and identities remain
separate from represented endpoint kinds. Missing, candidate, withdrawn or stale
mapped inputs fail. New connections require current mapped instances. Existing
exact-version relations may be inspected against eligible historical instances;
the explicit historical read path cannot author a new connection to them.

The immutable foundation overlay already declares its Project/Product subject
kinds. This engine preserves that original projection metadata and the raw
carrier schemas. Newly authored local Project/Product entries retain raw carrier
kinds. The selected mapping validates both forms without rewriting an entry.

The mapping grants no global axis or ordered pair. Existing Relation Kind pairs,
closed qualifier constraints, instance schemas, effect categories, policy,
challenge route, source snapshot and signature checks remain required. Method
carrier/mapping admission and the unselected Authority Boundary/Decision Scope
pair mismatch remain separate integration/review obligations.

## Implementation and source bindings

The candidate captures the exact original v2 package. Five separately bound
candidate file deltas implement mapping dispatch, signed config binding, source
snapshot capture, relation consequences and historical graph inspection. A new
endpoint-mapping module and exact mapping document complete the executable
closure. Original v1/v2 files remain unchanged. The loader captures the complete
candidate into a fresh namespace and verifies an externally supplied manifest,
engine, mapping and profile pin before and after use.

The D75 source profile bytes remain unchanged. The candidate source snapshot adds
the mapping and original C14 proposal to its captured materials/documents. No
new domain subject or canonical authority is inferred from those documents. New
owned configs use a closed `lab-runtime-store-config/v2-candidate` with the exact
engine ID and mapping binding. Config, baseline and HEAD are independently pinned
for cold replay. The config's source snapshot and genesis/head chain bind this
mapping into the actual operator signature. An old store cannot acquire this
coupling by a helper normalization or unsupported rebase.

The inherited schemas in `engine/schemas` describe the original protocol
versions. The exact new coupled config schema is separately materialized at
`schemas/config-v2.schema.json`; `protocols.COUPLED_CONFIG_SCHEMA` validates actual
new configs. This is an implementation protocol proposal, not an admitted domain
Artifact Type or a replacement for its independent owner review.

## Actual owned examples

Engineering and research reuse the exact retained W07 Evidence Set/Experiment
Run and membership relation bodies, plus the original Project Identity body.
Each independent branch explicitly selects the original Project scope. It
records the exact Project body version as a local successor of the original
foundation admission label. Original scope, field content and source body remain
unchanged. The branch's raw Project subject kind is `project-identity`; the signed
membership endpoint remains `project` under this mapping.

The Product example uses the exact admitted Product Identity and existing
capability plus a newly constructed declared member-of relation. It tests Product
coupling; it asserts no original workflow observation or Product benefit.

Every example uses a fresh fixture operator key outside the repository/store,
mode 0600, and a disposable external store. Review displays the source/represented
kind explanation before the fixture signature. The actual signed transaction
advances both histories; retrying the exact original proposal/signature is
idempotent. Original key/store directories are removed. Archives contain only
exact signed public-key/config/baseline/HEAD/transaction originals, with private
candidate visibility and no private key or Session memory.

The recovered engineering example preserves the initial witness-writing error
and its source snapshot. The original signed archive supports independent replay
and exact retry without a new key or semantic transaction. Original domain cases
are never reexecuted. Product's first selection error happened before proposal
or semantic transaction and is retained separately.

## Remaining R03 work

This coupling is a prerequisite for correct operator inspection. The complete
chosen CLI/authenticated stdio interface, all 34 exact API handlers and their
meaningful results/errors, SQLite/canonical query parity, diff/effect/evidence
journeys and complete why-path/receipt integration remain implementation and
verification obligations. The inherited engine CLI is retained for regression;
the selected operator entrypoint and full interface are not yet supplied here.

W07 still needs the integrated signed closure and complete selected workflow
records, including independent Method/schema/reference and case identity
decisions. Isolated pair proofs cannot establish whole-workflow conformance.
All proposed mapping, engine, protocol and example ownership remains S02/R08.
