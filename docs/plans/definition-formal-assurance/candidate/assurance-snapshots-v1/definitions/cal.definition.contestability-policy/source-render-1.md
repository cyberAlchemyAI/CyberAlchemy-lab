<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Contestability Policy

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.contestability-policy`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.shared-authority`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Contestability Policy is the normalized policy identified by semantic.contestability-policy, owned within scope.shared-authority, and carried by type.policy. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D40 without silently merging it with another target.

Bound source-semantic basis:

A challenge contract is the explicit review surface attached to a
CyberAlchemy v2 node, candidate, claim, or authority artifact that states how
the object may be challenged, contradicted, validated, blocked, or routed for
owner review without silently changing its meaning or confidence.

A challenge contract must declare the valid challenge response, admissible
challenge modes, contradiction and validation links when present, owner route,
resolution gate, blocking questions, and challenge residue route. It does not
contain the object's own confidence or residue and does not introduce a third
confidence axis. Object confidence remains a sibling posture using the
`evidence_confidence` and `commitment_confidence` split governed by `CAV2-D23`.

```text
An admissible challenge contract has at least:

```text
ChallengeContract =
  (challenge_response, valid_challenge_modes, contradiction_edges,
   validation_edges, owner_route, resolution_gate, blocking_questions,
   challenge_residue_route)
```

where `challenge_residue_route` says where unresolved challenge residue is
handled. The object's own confidence and residue are not part of the challenge
contract. When an object records confidence, active CyberAlchemy v2 uses
`evidence_confidence` for evidence support and `commitment_confidence` for
commitment posture.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.contestability-policy | Stable normalized identity for Contestability Policy. |
| CAV2-D40 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- Challenge contract is not a verdict, not a confidence score, not proof of
truth, not a promotion decision, and not an ontology-owned override of the
relevant owner route. It names the challenge path; owner routes and gates still
decide movement.

### Testable conditions

- The candidate identity remains cal.definition.contestability-policy.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

It is the object's "how to disagree with me correctly" field.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Contestability Policy is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

In CyberAlchemy v2, challenge contract belongs on the ontology candidate node
shape before candidate concepts become load-bearing. It lets the project reuse
challenge responses, `contradicts` and `validates` edges, owner routes, gates,
and residue routing while node confidence remains outside the contract as
`evidence_confidence` and `commitment_confidence`. It is the schema-level answer
to the question: if this node is challenged, who reviews it, with which
evidence, and where does the challenge residue go?

### Examples

- Resolve semantic.contestability-policy by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Contestability Policy.

## Applicability

Use challenge contract when a candidate ontology node, projection, definition
proposal, constitution proposal, research claim, or authority artifact needs to
say what kind of objection is valid and what happens next. A contradiction
edge may block promotion; a validation edge may increase evidence support; a
blocking question may defer the node; and unresolved challenge residue must
remain attached until an owner route closes, waives, or demotes it.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- Challenge contract is not a verdict, not a confidence score, not proof of
truth, not a promotion decision, and not an ontology-owned override of the
relevant owner route. It names the challenge path; owner routes and gates still
decide movement.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D40 | ## CAV2-D40: Challenge Contract | `41b8d50c1a383a7ee163c096d744934ea63a93503d3b9ed63175e0f0dac00205` | `candidate-unadmitted` |

## Primary consumers

None declared.

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.contestability-policy@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.contestability-policy | cyberalchemy-v2:CAV2-D40 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-contestability-policy/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
