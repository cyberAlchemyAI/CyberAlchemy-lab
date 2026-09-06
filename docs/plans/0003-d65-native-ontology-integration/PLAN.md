# D65-native CyberAlchemy ontology runtime integration

Status: D65-S5 admitted; exact implementation binding blocked at `G-D65-BINDING`
Authority effect: none
Canonical source: `d65-plan.json`

## Outcome

Integrate the accepted event-sourced ontology runtime into CyberAlchemy through
one direct `CAV2-D65` chain. CyberAlchemy contexts will consume projections
calculated from canonical per-node and per-relation events at one exact cut;
contexts never become alternate ontology truth or replay sources.

Invoke is not part of this lifecycle. It is neither a predecessor, authoring
requirement, validator, admission source, nor execution route.

## Owning Project and Goal

`PRJINT-1` selected the existing
`CA2-PROJECT-CYBERALCHEMY-LAB-ONTOLOGY-LIFECYCLE` as the sole owning Project.
The narrower integration result is registered as draft Goal
`CA2-GOAL-CYBERALCHEMY-LAB-ONTOLOGY-RUNTIME-INTEGRATION`.

This repairs the invalid proposed `CAL-PROJECT-*` alias and avoids a duplicate
Project for the same ontology-lifecycle ownership boundary. The carriers are
authored and discovered. The definitions-governance and product-owner source
epochs are reconciled, the product-thesis validator passes, and the Goals
validator reports no error in this Goal's selected dependency set.

`G-PROJECT-OWNER` is therefore `PASS` for this exact Goal. The Goals aggregate
still has 19 unrelated blockers; they remain diagnostic and grant no package-wide
admission, construction authority, or implementation authority.

## Direct D65 chain

```text
owning Project and Goal
  -> canonical definitions
  -> CyberAlchemy product ontology
  -> capability-local business ontology / business-system bridge
  -> DomainSpec v2 authored source
  -> deterministic compiled graph and system-runtime ontology
  -> exact accepted implementation binding
  -> bridge and context-adapter implementation
  -> independent static conformance and bounded runtime evidence
  -> separate admission/cutover owner decision
```

| Stage | Primary result | Gate | Current state |
| --- | --- | --- | --- |
| `D65-P0` | Owning Project and Goal | `G-PROJECT-OWNER` | `PASS` |
| `D65-S1` | Exact integration definitions | `G-D65-DEFINITIONS` | `PASS` |
| `D65-S2` | Product Capability and product ontology | `G-D65-PRODUCT` | `PASS` |
| `D65-S3` | Business-system bridge ontology | `G-D65-BUSINESS` | `PASS` |
| `D65-S4` | DomainSpec v2 bridge/runtime source | `G-D65-DOMAINSPEC-SOURCE` | `PASS` |
| `D65-S5` | Byte-identical graph and system ontology | `G-D65-COMPILE` | `PASS` |
| `D65-S6` | Project-owned exact implementation binding | `G-D65-BINDING` | `BLOCK` |
| `D65-S7` | Bridge and context adapters | `G-D65-IMPLEMENTATION` | `not_evaluable` |
| `D65-S8` | Independent integration conformance | `G-D65-CONFORMANCE` | `not_evaluable` |

## Definition candidate

`D65DEF-1` selected
`CAL-DEFINE-PACK-ONTOLOGY-RUNTIME-INTEGRATION-001` through exact decision
`CAL-D65DEF-0015`. The pack validates `PASS` and reuses five exact canonical meanings (`CAV2-D19`,
`CAV2-D26`, `CAV2-D40`, `CAV2-D65`, and `CAV2-D66`), specializes five meanings
for this context, and proposes three integration-local meanings. Every local
meaning has formal, plain-language, and domain voices plus explicit boundaries.

The selection does not alter or promote canonical definitions. Concurrent
post-`CAV2-D81` additions lie outside the selected definition selectors and
remain with their active writer.

## Product Capability and product ontology candidate

The Lab-local package
`ontology-lifecycle/product-ontology/cal-ontology-runtime-integration-epoch-001`
now represents the D65-S2 product meaning. It defines Product Capability
`CA2-CAP-CONSUME-GOVERNED-EVENT-CALCULATED-ONTOLOGY-PROJECTIONS`, 16 nodes,
seven relation types, 15 relations, 13 exact handled-definition bindings, five
owner lanes, and four visible residue items.

Its product promise is bounded: a governed Context can consume a challengeable,
deterministic ontology projection from canonical per-node and per-relation
events at one exact event cut. A Context, projection, snapshot, compiled graph,
or system ontology never becomes canonical truth. Invalid or unverifiable cuts
must be rejected.

The package validator is `PASS`. Exact owner decision `CAL-D65PROD-0016`
records the explicit `D65PROD-1` selection and admits these exact candidate
bytes for integration epoch 001. The candidate files remain immutable
preselection evidence; admission is carried by the owner decision and plan.

This passes `G-D65-PRODUCT` only. It does not turn the product model into a
business ontology, DomainSpec source, compiled system ontology, or runtime.

## Capability-local business ontology candidate

The D65-S3 package
`ontology-lifecycle/business-ontology/cal-ontology-runtime-integration-epoch-001`
defines the business-system bridge without claiming a system endpoint or
runtime realization. It contains 26 typed business nodes, 12 relation types,
35 relations, eight contracts, three policies, two workflows, 13 fail-closed
failure outcomes, and five explicit residue items.

The bridge binds governed Context identity, an exact selector, one canonical
event cut, deterministic event-calculated projection behavior, exact
governance joins, and a typed challenge route. It also states the requirements
that a future system endpoint must satisfy. No `realized_by` relation or
system-runtime component is present, so the candidate cannot be mistaken for
the D65-S4 authored source or a runtime implementation.

The package validator is `PASS`, including source-currentness, endpoint and
relation closure, contract/workflow closure, fail-closed outcomes, and the
non-vacuous future-system boundary. The decision prefilter admitted all four
owner choices. Exact owner decision `CAL-D65BIZ-0018` records the explicit
`D65BIZ-1` selection and admits the exact candidate bytes for integration epoch
001. The immutable candidate remains preselection evidence; admission is
carried by the owner decision and continuous plan.

This passes `G-D65-BUSINESS` only. The admitted bridge remains a business
contract: it does not claim a system endpoint, DomainSpec realization,
system-runtime ontology, implementation binding, or Rust implementation.

## D65-S4 DomainSpec source candidate

The package
`ontology-lifecycle/domainspec-source/cal-ontology-runtime-integration-epoch-001`
now translates the admitted business ontology into DomainSpec v2 authored
source. It maps all 26 business nodes, 35 relations, eight contracts, and 13
failure conditions, and adds the typed operations, calculations, events,
rules, policies, and workflows needed to express the event-calculated model.

The minted project contains 41 nodes and 43 canonical DomainSpec edges. Its
event-sourcing contract declares separate entity/relation semantic and
governance streams, complete-resulting-state events, node and relation latest
snapshots, one governed ontology projection, exact governance joins, and one
global commit-position cut.

Positive validation is `PASS`. The minted compiler and Event Sourcing Contract
compiler each produced byte-identical in-memory results across two runs. Three
hostile checks also passed by rejecting selected-source digest drift, a missing
business-relation mapping, and an injected generated graph.

Exact owner decision `CAL-D65SRC-0019` records the repeated explicit approval
as `D65SRC-1` and admits the exact source candidate for integration epoch 001.
The development profile binding is admitted only for this source epoch; it is
not released or generally admitted.

This passes `G-D65-DOMAINSPEC-SOURCE` only and does not itself admit a compiled
graph or system ontology or authorize implementation.

## D65-S5 compiled graph and system-ontology candidate

The isolated package
`ontology-lifecycle/system-ontology/cal-ontology-runtime-integration-epoch-001`
composes the DomainSpec minted-project compiler and Event Sourcing Contract
compiler against the exact D65-S4 source admitted by `CAL-D65SRC-0019`.

The candidate materializes 41 graph nodes, 43 canonical graph edges, 84 source
provenance records, five streams, five events, three projections, two exact
governance joins, and 12 runtime obligations. Internal and external double
compilation are byte-identical. The system ontology repeats the exact graph and
compiled event contract without adding independently authored product meaning.
Its subject-calculation view resolves each entity, relation, and process stream
to the projections that calculate its latest state.

Positive validation is `PASS`. All graph IDs have source provenance; graph and
system-ontology nodes and edges are equal; the event contract and projection
calculus close. Three hostile cases also pass by rejecting selected-source
digest drift, removal of a system-ontology node, and tampering with the
materialized graph.

Decision request `CAL-D65SYS-REQUEST-001` presents `D65SYS-1` through
`D65SYS-4`. Exact owner decision `CAL-D65SYS-0020` records the explicit
`D65SYS-1` admission. This passes `G-D65-COMPILE` for the exact integration
epoch 001 candidate and makes D65-S6 eligible; it does not author or accept an
implementation binding.

Version `cal-ontology-runtime-integration-v1` preserves a byte-identical copy
of the admitted 41-node, 43-edge graph plus a complete readable Markdown edge
projection. The copy is provenance-bound to `CAL-D65SYS-0020`, validates
`PASS`, and is explicitly not a canonical replay source.

## First bounded action

At `G-D65-BINDING`, D65-S6 needs one Project-owned exact implementation-binding
candidate that binds the admitted system ontology to the accepted W8 Rust
runtime and planned Context adapters. Its authorship must use exactly one
bounded native helper, followed by independent parent validation and a
separate implementation-owner acceptance decision. This plan transition does
not authorize that authorship or any Rust or Context mutation. Source-epoch
decision `CA2-DECISION-ONTOLOGY-RUNTIME-INTEGRATION-SOURCE-EPOCHS-002`
reconciles the current Product Thesis `## Thesis` selector and its matching
revision 3 machine record. Aggregate Goals remains `BLOCK` on unrelated items,
but this Goal's selected Product Thesis dependency is current.

## Terminal boundary

Even a future `G-D65-CONFORMANCE` PASS produces candidate integration evidence
only. `G-INTEGRATION-ADMISSION-CUTOVER` remains a separate owner decision with
admit-without-cutover, bounded cutover, amend, defer, and stop outcomes.

No publication, release, deployment, credential use, destructive action, or
external effect is authorized.
