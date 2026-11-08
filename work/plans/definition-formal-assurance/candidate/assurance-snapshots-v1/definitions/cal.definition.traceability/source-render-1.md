<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Traceability

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.traceability`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.lineage`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Traceability is the normalized definition identified by semantic.traceability, owned within scope.lineage, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D36 without silently merging it with another target.

Bound source-semantic basis:

Traceability is the ability to follow explicit, typed links across intent,
source evidence, provenance, definitions, rules, methods, artifacts, gates,
validation, decisions, residue, and next routes so that a later human or agent
can answer why something exists, what it depends on, what it affects, and where
to continue.

Traceability is satisfied only when the relevant chain has enough link targets,
relation types, authority postures, and residue markers to be traversed without
hidden conversation context.

```text
For a work object `x` and a review question `q`, traceability holds when there
is a declared path:

```text
trace_q(x) = x -> link_1 -> link_2 -> ... -> answer_or_residue
```

Each `link_i` must have a target, relation type, and authority posture. If the
path breaks, the break must be recorded as typed residue or a named gap.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.traceability | Stable normalized identity for Traceability. |
| CAV2-D36 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- Traceability is not the same as provenance. Provenance records origin and
transformation history; traceability tests whether the project can navigate the
relevant links for a question. Traceability is also not proof, completeness, or
approval.

### Testable conditions

- The candidate identity remains cal.definition.traceability.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

Traceability means you can follow the thread from "why are we doing this?" to
"what changed?" to "what happens next?"

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Traceability is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

In CyberAlchemy v2, traceability turns the stable repository objective into a
navigation requirement. It binds CAV2 definitions, source clusters, import
manifests, Craft contexts, inventory cards, ontology projections, handoffs, and
validation evidence into routes that future work can traverse without replaying
the original conversation.

### Examples

- Resolve semantic.traceability by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Traceability.

## Applicability

Use traceability when deciding whether CyberAlchemy v2 is navigable enough to
resume, validate, publish, extract, or hand off. It is the check that source
receipts, definitions, Craft state, decisions, and validation evidence are
connected rather than merely present.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- Traceability is not the same as provenance. Provenance records origin and
transformation history; traceability tests whether the project can navigate the
relevant links for a question. Traceability is also not proof, completeness, or
approval.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D36 | ## CAV2-D36: Traceability | `b26a51020545d55d5636e1bff0fd7ecf5ad32c9299ab116a31a28c3a6baf8af7` | `candidate-unadmitted` |

## Primary consumers

- semantic.artifact-lifetime

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.traceability@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.traceability | cyberalchemy-v2:CAV2-D36 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-traceability/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
