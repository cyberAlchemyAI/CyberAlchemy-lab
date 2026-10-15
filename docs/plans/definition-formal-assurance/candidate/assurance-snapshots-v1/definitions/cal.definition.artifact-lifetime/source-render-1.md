<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Artifact Lifetime

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.artifact-lifetime`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.shared-authority`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Artifact Lifetime is the normalized definition identified by semantic.artifact-lifetime, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D52 without silently merging it with another target.

Bound source-semantic basis:

Artifact durability is the axis that classifies a `CAV2-D51` canonical artifact by
**intended lifespan** — `ephemeral` (a work-product meant to be produced,
consumed, and retired) or `perennial` (a standing reference meant to endure and be
maintained). Durability is **orthogonal** to the `authority_kind` (`CAV2-D49`)
and to maturity/status (`CAV2-D23`): two artifacts of the same kind may differ in
durability — a discovery and an inventory index are both `Evidence`, yet the
discovery is ephemeral and the index is perennial.

Durability carries one **contradiction-tolerance** obligation (typed coupling,
`CAV2-D16`):

- an **ephemeral** artifact **may hold live contradictions** — competing
  hypotheses and unresolved tensions are expected and preserved;
- a **perennial** artifact **must not hold live simultaneous contradictions**.
  *Temporal supersession* — a later entry overriding an earlier one in an
  append-only record (`CAV2-D26` ledger), or a decision record narrating the
  contradiction it resolved (`CAV2-D36`) — is **not** a live contradiction and is
  permitted.

```text
```text
durability(a) in { ephemeral, perennial }
durability(a)  orthogonal-to  authority_kind(a)   (CAV2-D29: independent of authority-kind)
durability(a)  orthogonal-to  status(a)         (CAV2-D23: independent of maturity)
perennial(a)   ->  not ( a holds live  P and not-P simultaneously )
ephemeral(a)   ->  a may hold live  P and not-P
temporal supersession ( E_t overrides E_{t-1} ) is not a live contradiction
```
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.artifact-lifetime | Stable normalized identity for Artifact Lifetime. |
| CAV2-D52 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- Artifact durability is **not** maturity/status (`CAV2-D23`): a mature discovery is
still ephemeral, a draft spec is still perennial. It is **not** authority:
perennial does not mean authoritative (a perennial spec may still be a candidate).
It is **not** regenerability: a projection is derived and regenerable, which is a
separate property, not "ephemeral" — durability is about intended lifespan, not
whether the artifact can be rebuilt. The two-value set may later gain an
append-only/monotonic third value if the ledger case proves the live-vs-temporal
refinement insufficient; that is an owner-gated extension.

### Testable conditions

- The candidate identity remains cal.definition.artifact-lifetime.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

Some documents are meant to be used and then set aside once they have done their
job (a discovery); others are meant to stand and be kept true (a spec). The
first kind is allowed to argue with itself; the second is not — though a logbook
is still allowed to record that things changed over time.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Artifact Lifetime is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

In CyberAlchemy v2, durability is a column on
[../../ontology/canonical-kinds/CANONICAL-KINDS.md](../../ontology/canonical-kinds/CANONICAL-KINDS.md). It answers
"how long is this meant to stand, and can it hold contradictions" — a question
neither `CAV2-D49` (what kind) nor `CAV2-D23` (how mature) asks. It is why a
discovery can freely explore contradictions while a spec cannot, and why a ledger
can record superseding events without violating consistency.

### Examples

- Resolve semantic.artifact-lifetime by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Artifact Lifetime.

## Applicability

Assign durability per canonical-kind as a default (spec / definition /
constitution / decision / axiom / ledger -> perennial; discovery / research /
session -> ephemeral), overridable per instance with an owner note. When reviewing
a perennial artifact, treat a live contradiction as a defect to resolve; when
reviewing an ephemeral one, treat contradictions as legitimate exploration to
preserve.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- Artifact durability is **not** maturity/status (`CAV2-D23`): a mature discovery is
still ephemeral, a draft spec is still perennial. It is **not** authority:
perennial does not mean authoritative (a perennial spec may still be a candidate).
It is **not** regenerability: a projection is derived and regenerable, which is a
separate property, not "ephemeral" — durability is about intended lifespan, not
whether the artifact can be rebuilt. The two-value set may later gain an
append-only/monotonic third value if the ledger case proves the live-vs-temporal
refinement insufficient; that is an owner-gated extension.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D52 | ## CAV2-D52: Artifact Durability | `13901f51e52227f10c9dc9aab3d9977d2047127114a82c3aaf6dbdaf17fbf7c5` | `candidate-unadmitted` |

## Primary consumers

- semantic.artifact
- semantic.canonical-representation-invariant

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.artifact-lifetime@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.artifact-lifetime | cyberalchemy-v2:CAV2-D52 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-artifact-lifetime/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
