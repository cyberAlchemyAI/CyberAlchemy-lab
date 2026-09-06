# DomainSpec v2 Axioms

Status: active R1 continuity authority surface
Owner: DomainSpec v2 owner
Machine companion: `AXIOMS.yml`

This file is the human-readable authority companion for DomainSpec v2's
retained R1 axiom-shaped and invariant-shaped rows. `AXIOMS.yml` is the
machine-readable registry for the same authority home. Together they replace
the hand-authored `impl/spec/AXIOMS.md` projection under
`DEC-DSV2-SPEC-HOMING`.

These rows are not standalone glossary definitions. They are local governance
propositions and routed provenance rows used by the local authority model,
constitution, and downstream reformulation work.

## CAV2 Definition Alignment

This file is a DomainSpec v2 R1 continuity surface. It catalogs axiom-shaped
and invariant-shaped R1 rows against the current CAV2 vocabulary.

- CAV2-D53 `axiom`: a world/domain truth held as given, with possible fan-out
  into premises, invariants, and constitution rules.
- CAV2-D54 `invariant`: a checkable must-hold on system behavior or artifacts.
- CAV2-D49 `authority kind`: the closed first-class authority-kind
  enumeration.

Under CAV2-D49, `axiom` and `invariant` are not currently first-class authority
kinds. This surface therefore rolls up under `Definition` for cataloging
purposes only. That rollup does not convert rows into definitions, does not
make `axiom` or `invariant` first-class authority kinds, and does not redefine
CAV2-D53 or CAV2-D54.

`local_role` and `cav2_shape.primary` are compatibility classifications for
this R1 continuity surface only. They do not create a local authority taxonomy,
change CAV2-D49, or bypass CAV2 ownership.

## Namespace Note

References to constitution rules below refer to
`authority/constitutions/domainspec-v2-CONSTITUTION.md` unless another source is
explicitly named. Do not conflate these with `CAV2-C*` umbrella rules or
research-local `RC*` doc-hygiene rules.

## Retained Axioms

| ID | Axiom | Authority statement | Primary binding |
| --- | --- | --- | --- |
| A1 | Semantic Authority Precedes Implementation | Domain semantics are authored in DomainSpec authority, definition, and feature-spec surfaces first. Code, workflows, and automation are downstream realizations and may not become semantic authority by implementation accident. | Source posture and derivation discipline in the local authority model and constitution. |
| A2 | Decisions Belong To The Domain, Not Adapters | Domain policy, invariants, dependency law, and state-transition meaning belong above the adapter line. Infrastructure adapters may realize decisions but may not author them. | C6: forbidden edges are unconstructible; no dependency may cross the adapter line. |
| A3 | Governance Methods Must Be Runnable | A governance method that gates critical behavior must have a runnable or computable validation path. Review-only prose may guide judgement, but it does not close a blocking gate by itself. | Validation governance and build-time fidelity gates. |

### Axiom A1 - Semantic Authority Precedes Implementation

Classification:

- local_role: `invariant-shaped`
- cav2_shape.primary: `CAV2-D54`
- authority_kind_rollup: `Definition`

DomainSpec v2 treats implementation as a realization of governed semantic
surfaces, not as the source of those semantics. This preserves the source-first
rule behind the fork from v1: v1 is harvested precedent, while v2 authority is
owned locally.

Absence failure:

1. Implementation-first edits introduce behavior that the domain did not
   authorize.
2. Alignment drift becomes invisible because code appears more current than the
   authority surface.

### Axiom A2 - Decisions Belong To The Domain, Not Adapters

Classification:

- local_role: `invariant-shaped`
- cav2_shape.primary: `CAV2-D54`
- authority_kind_rollup: `Definition`

Layering is a governance law, not an adapter convention. If the Edge Law forbids
a dependency, that dependency must be unconstructible rather than merely
reported after the fact. This binds directly to C6 in the local constitution.

Absence failure:

1. Adapters accumulate business policy and become hidden domain owners.
2. Cross-layer dependencies become audit findings instead of impossible states.

### Axiom A3 - Governance Methods Must Be Runnable

Classification:

- local_role: `invariant-shaped`
- cav2_shape.primary: `CAV2-D54`
- authority_kind_rollup: `Definition`

Critical governance cannot rest on instruction-only enforcement. When a method
blocks promotion, closeout, or merge, it needs a runnable, computable, or
otherwise checkable path appropriate to the claim being made.

Absence failure:

1. A documented gate looks real while no repeatable check can execute it.
2. Violations are discovered after closeout even though the repo had enough
   information to block earlier.

## Routed Material

The following v1 axiom material is not silently deleted. It is routed by
`DEC-B1-SATURN-AXIOM-SCOPE` and remains visible as provenance until the
owning surface exists.

| Former ID | Former concern | R1 treatment | Owner route |
| --- | --- | --- | --- |
| A4 | Observation independent from execution | Drop from DomainSpec axiom authority with pointer. | Saturn observer/executor split. |
| A5 | Shift-left control plus outer-loop reflection | Split: shift-left blocking remains with DomainSpec validation governance and C5; reflection routes out. | DomainSpec C5 for shift-left; Saturn for reflection loop. |
| A6 | Governance feedback budget | Drop from DomainSpec axiom authority with pointer. | Saturn feedback-budget loop. |

### Routed Classification

- A4: `local_role: routed-pointer`,
  `cav2_shape.primary: not-applicable`,
  `authority_kind_rollup: Definition`.
- A5: `local_role: split-routed-pointer`,
  `cav2_shape.primary: CAV2-D54` for the retained DomainSpec shift-left
  fragment, `not-applicable` for the Saturn reflection fragment,
  `authority_kind_rollup: Definition`.
- A6: `local_role: routed-pointer`,
  `cav2_shape.primary: not-applicable`,
  `authority_kind_rollup: Definition`.

## Closeout Rules

- `impl/spec/AXIOMS.md` is not an authority surface.
- Historical references may keep pointing at the old import evidence when they
  are explicitly about the pre-closeout state.
- Current authority, constitution, source-spine, and future reformulation work
  should cite `AXIOMS.md` for human explanation and `AXIOMS.yml` for structured
  axiom IDs, bindings, and routed-material status.
