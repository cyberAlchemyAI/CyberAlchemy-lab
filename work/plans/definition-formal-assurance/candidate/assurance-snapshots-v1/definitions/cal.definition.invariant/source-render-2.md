<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Invariant

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.invariant`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.shared-authority`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Invariant is the normalized definition identified by semantic.invariant, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D54 without silently merging it with another target.

Bound source-semantic basis:

An invariant is a **condition on the system's own behavior or artifacts that must
remain true** across a declared scope of decisions, transformations, or states —
such that a violation is **drift or a defect**. Its defining subject is the
**system**: unlike an axiom (`CAV2-D53`), which the system is built around, an
invariant is something the system **must satisfy** and can fail to. An invariant is
the checkable *what-must-stay-true* that a constitution rule (`CAV2-D58`)
operationalizes and a validator or gate (`CAV2-D37`) enforces.

```text
```text
invariant I:  ∀ state/transition s in scope(I):  must-hold(I, s)
subject(I) = the system            (its behavior / artifacts)
system can violate I?  Yes — a violation is drift/defect (a bug)
grounded-by:        an axiom (CAV2-D53) answering "why must I hold?"
operationalized-by: constitution rule (CAV2-D58)
enforced-by:        validator / gate (CAV2-D37)
```

CyberAlchemy v2 already carries specific invariants — `CAV2-D16` typed coupling,
`CAV2-D29` axis orthogonality, `CAV2-D38` claim ≤ proof, `CAV2-D49` closed
authority-kind enumeration; this definition is their generic parent.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.invariant | Stable normalized identity for Invariant. |
| CAV2-D54 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- An invariant is **not** an axiom (`CAV2-D53`): same-input-same-output is a system
must-hold; "unreproducible results cannot be trusted" is the world-truth behind it.
It is **not** a constitution (`CAV2-D58`): the invariant is one must-hold
proposition, the constitution is the scoped, composable rulebook that
operationalizes many invariants with selectors, examples, validation modes, and
precedence. It is **not** a validator or gate (`CAV2-D37`): the invariant states
what must be true, the validator is the check that enforces it. It is **not**
automatically authority — an invariant governs only through its owner route.

### Testable conditions

- The candidate identity remains cal.definition.invariant.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

A condition the system must keep true — "same input, same output." Break it and
you have a bug. It is the *what must stay true*, sitting below the axiom that
says *why* and above the rulebook that says *how*.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Invariant is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

In CyberAlchemy v2, invariant is the middle of the `axiom → invariant →
constitution → validator` chain: the checkable anchor that a constitution may
operationalize and a selected validator or gate may enforce, and the parent
genus of the already-promoted invariant instances
(`CAV2-D16`/`D29`/`D38`/`D49`). An invariant with no axiom under it is unjustified;
an invariant with no validation mode is un-enforceable (`none-yet`, per
constitution-governance).

### Examples

- Resolve semantic.invariant by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Invariant.

## Applicability

Use "invariant" for a single must-hold truth about the system that is, in
principle, checkable and whose breach is a defect. Two tests: (1) can the system
violate it (is a breach a bug)? If yes, it is an invariant; if the system cannot
make it false, it is an axiom. (2) Is it one condition (invariant) or a bundle of
authoritative rules with selectors and modes (a constitution, `CAV2-D58`)? Each
invariant should trace *up* to an axiom (its "why") and *down* to a validation
mode.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- An invariant is **not** an axiom (`CAV2-D53`): same-input-same-output is a system
must-hold; "unreproducible results cannot be trusted" is the world-truth behind it.
It is **not** a constitution (`CAV2-D58`): the invariant is one must-hold
proposition, the constitution is the scoped, composable rulebook that
operationalizes many invariants with selectors, examples, validation modes, and
precedence. It is **not** a validator or gate (`CAV2-D37`): the invariant states
what must be true, the validator is the check that enforces it. It is **not**
automatically authority — an invariant governs only through its owner route.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D54 | ## CAV2-D54: Invariant | `722012e8ba37de92d0f13886380e8510db2ebec622f679f45b7a875a698945de` | `candidate-unadmitted` |

## Primary consumers

- semantic.axiom
- semantic.constitution
- semantic.hypothesis
- semantic.premise
- semantic.schema

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.invariant@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.invariant | cyberalchemy-v2:CAV2-D54 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-invariant/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
