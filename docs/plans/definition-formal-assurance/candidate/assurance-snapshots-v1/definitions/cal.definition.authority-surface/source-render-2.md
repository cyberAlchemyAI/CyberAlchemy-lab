<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Authority Surface

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.authority-surface`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.shared-authority`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Authority Surface is the normalized definition identified by semantic.authority-surface, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D3 without silently merging it with another target.

Bound source-semantic basis:

An authority layer is a project-local surface that is allowed to define
normative meaning, structural rules, promotion decisions, or contracts for a
specific scope.

```text
semantic.authority-surface := (semantic_kind=definition, carrier=type.definition, owner_scope=scope.shared-authority, source_set={CAV2-D3}). Identity, carrier, and owner scope are independent axes; equality of labels does not establish equality of concepts.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.authority-surface | Stable normalized identity for Authority Surface. |
| CAV2-D3 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- An authority layer can cite evidence, but evidence does not become authority
unless the responsible owner promotes it.

### Testable conditions

- The candidate identity remains cal.definition.authority-surface.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

An authority layer says which document is allowed to count.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Authority Surface is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

In CyberAlchemy v2, the authority layers are currently
`authority/definitions/`, `authority/constitutions/`, `disciplines/`,
`authority/decisions/`, and later promoted `specs/`.

### Examples

- Resolve semantic.authority-surface by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Authority Surface.

## Applicability

Use authority layers to prevent research, inventory, ontology, observability,
memory, generated projections, and implementation evidence from silently
rewriting definitions or rules.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- An authority layer can cite evidence, but evidence does not become authority
unless the responsible owner promotes it.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D3 | ## CAV2-D3: Authority Layer | `81cc1c09c3e4261be700b1d504fc5e5e5129ef5aaee5f6723adbbd4561351ae2` | `candidate-unadmitted` |

## Primary consumers

- semantic.authority
- semantic.authority-claim
- semantic.responsibility

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.authority-surface@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.authority-surface | cyberalchemy-v2:CAV2-D3 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-authority-surface/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
