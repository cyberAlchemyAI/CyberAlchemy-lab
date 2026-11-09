---
title: D65 Export and Cutover Candidate Implementation Layering
status: tested-product-awaiting-approval
updatedAt: 2026-09-03
owner: CyberAlchemy product and ontology-runtime owner
scope: system
---

# D65 export and cutover candidate implementation layering

## Layer decision table

| Layer | After this layer, we know whether... | Minimum working unit | Outcome | Risk reduced | Promotion |
| --- | --- | --- | --- | --- | --- |
| L0 | the admitted v2 contexts can be joined by an exact successor map without altering v1. | Additive v2 map candidate, generated view, validation, and hostile conformance. | Tested v2 coordination prototype. | Endpoint and authority-direction ambiguity. | Continue prototype construction. |
| L1 | the v2 map and existing product meaning compile through a fresh D65 semantic epoch. | Revalidated definitions/product plus new business bridge, DomainSpec source, graph, and system ontology. | One deterministic epoch-002 prototype contract. | Semantic drift and skipped-predecessor risk. | Continue after tested predecessor receipts. |
| L2 | the adapters can be publicly exported without touching the admitted runtime. | Separately versioned candidate crate with public modules and v2 exact-context guards. | Tested executable export prototype. | Accepted-byte loss and accidental cutover. | Continue to product conformance. |
| L3 | the complete candidate is a non-vacuous tested product while admitted bytes remain unchanged. | Independent conformance, mutation tournament, selected-byte freeze, and product-approval request. | Frozen tested product eligible for approval. | Vacuity and replay-divergence risk. | Approve, reject, defer, or amend the exact product. |

## Layer definitions

### L0 — successor Context Map proof

- Included: exact v2 endpoints, existing one-way relationship, map-local
  Published Language/Anti-Corruption Layer classification, generated human
  view, positive validation, wrong-endpoint/reverse-edge/authority-transfer
  hostile probes.
- Deferred: adapter export, payload implementation, new DomainSpec compile,
  migration execution, source relocation, and cutover.
- Exit evidence: candidate bytes and digests, deterministic projection twice,
  validator PASS, hostile conformance PASS, no v1 byte drift.
- Prior guarantees: v1 map unchanged; no reverse edge; no authority transfer.

### L1 — fresh D65 semantic epoch

- Included: reuse-by-exact-identity checks for canonical definitions and Product
  Capability; new capability-local business bridge for v2 map/payload meaning;
  DomainSpec source; deterministic graph/system-ontology compile.
- Deferred: Rust implementation and cutover.
- Exit evidence: tested-prototype receipts at D65-S1 through D65-S5 and
  two-run identical compile output.
- Prior guarantees: all L0 guarantees and event history as canonical truth.

### L2 — isolated Rust export candidate

- Included: a new versioned crate copied from exact D65-S8 preimages; public
  module exports; v2 context versions; tests importing only public crate paths;
  existing replay suite; exact implementation binding.
- Deferred: replacement of `ontology-lifecycle/runtime`, publication, and
  deployment.
- Exit evidence: tested binding, clean candidate build, 22 predecessor tests
  plus new public-export tests, and no changes beneath the admitted runtime.
- Prior guarantees: all L0/L1 guarantees, canonical-source rejection, exact
  governance joins, tombstones, and deterministic replay.

### L3 — product conformance and freeze

- Included: double-run equality, vacuity mutants, frozen-predecessor checks,
  selected-byte immutability, and final product-approval request.
- Deferred: real cutover, deletion, publication, release, and deployment.
- Exit evidence: independent PASS, 4/4 mutation probes, exact manifest digest,
  and one immutable product-owner request.
- Prior guarantees: all L0-L2 guarantees.

## Implementation wave backbone

| Wave | Layer | Goal | Gate |
| --- | --- | --- | --- |
| W0 | L0 | Author and validate the successor v2 Context Map candidate. | `TEST-CTXMAP2-S1` — PASS |
| W1 | L1 | Complete the new D65 semantic and compile chain. | `G-D65-EPOCH-002-COMPILE` |
| W2 | L2 | Bind and build the isolated public-export runtime candidate. | `G-D65-EPOCH-002-IMPLEMENTATION` |
| W3 | L3 | Freeze and independently test the exact product candidate. | `G-D65-EPOCH-002-PRODUCT-APPROVAL` |

## Non-regression guardrails

- Every admitted D65-S8 and v1 Context Map byte remains unchanged.
- Canonical events calculate state; projections and snapshots never become
  replay sources.
- Governance is upstream, Ontology Lifecycle is downstream, and authority does
  not cross the map.
- Missing exact governance joins, missing endpoints, drift, or rollback mismatch
  fail closed.
- Invoke is not a predecessor, route, validator, or authority source.

## Two-lane continuation

The product lane has completed `D65-S1` through `D65-S8`. The exact epoch-002
manifest is frozen and its product-test evidence passes, so the current frontier
is `product_approval`. The revision-1 plan-owner packet remains historical
operational residue. Product approval is still absent; admission, rehearsal,
and cutover remain later separate decisions.
