<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Provenance

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.provenance`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.lineage`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Provenance is the normalized definition identified by semantic.provenance, owned within scope.lineage, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D35 without silently merging it with another target.

Bound source-semantic basis:

Provenance is the declared origin and transformation chain for a term, artifact,
claim, rule, decision, relation, validation result, or residue. It records where
the object came from, which sources or prior objects it depends on, which
operations changed it, which owners or processes handled it, and which
authority posture it held at each relevant step.

Provenance must identify source references and relation types with enough
precision that a later reviewer can distinguish source evidence, local
adaptation, promotion, demotion, translation, derivation, validation, and
generated projection.

```text
For object `x`, provenance is a typed path:

```text
Prov(x) = [(source_i, relation_i, operation_i, owner_i, posture_i)]*
```

The path may be incomplete only if the missing segment is explicitly recorded
as residue with an owner route. Untyped "came from" language is not sufficient
for authority-bearing use.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.provenance | Stable normalized identity for Provenance. |
| CAV2-D35 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- Provenance is not proof, not authority, not trust, not validation, and not
credit assignment by itself. A perfect source trail can still point to a false,
unpromoted, private, or unusable claim. It only tells the project where meaning
and transformations came from.

### Testable conditions

- The candidate identity remains cal.definition.provenance.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

Provenance is the receipt trail for where something came from and how it got
here.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Provenance is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

In CyberAlchemy v2, provenance is the lower-level basis for
`CAV2-D24` provenance-first navigation, authority imports, source clusters,
inventory evidence cards, Craft links, handoffs, and future extraction review.
It lets v2 import scattered work without flattening source ownership or
pretending that source evidence has already become local authority.

### Examples

- Resolve semantic.provenance by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Provenance.

## Applicability

Use provenance before promoting, adapting, importing, validating, or publishing
anything. Provenance answers what source material is being used, what happened
to it, and where the current object should be audited if it drifts.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- Provenance is not proof, not authority, not trust, not validation, and not
credit assignment by itself. A perfect source trail can still point to a false,
unpromoted, private, or unusable claim. It only tells the project where meaning
and transformations came from.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D35 | ## CAV2-D35: Provenance | `b7855fd81c1ed14fe1bdb097fddfa2b1d32c2f88c8dc2f56dbf131f0164c5439` | `candidate-unadmitted` |

## Primary consumers

- semantic.artifact
- semantic.canonical-representation-invariant

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.provenance@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.provenance | cyberalchemy-v2:CAV2-D35 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-provenance/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
