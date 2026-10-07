<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Challenge Contract

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.challenge-contract`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:challenge-contract-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Challenge Contract is a closed versioned Policy-bound mechanism defining challengeable subjects, eligible challengers, grounds, evidence, response modes, owner route, resolution gate, timing, and unresolved residue handling. A route string alone is not a Challenge Contract, and filing a challenge does not automatically suspend or reverse the subject.

```text
ChallengeContract(x) => governed_identity_or_record(x) and bounded_scope(x); ChallengeContract(x) =/=> authority_effect(x).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Challenge Contract Definition. |

### Boundary conditions

- A Challenge Contract is a closed versioned Policy-bound mechanism defining challengeable subjects, eligible challengers, grounds, evidence, response modes, owner route, resolution gate, timing, and unresolved residue handling.
- A route string alone is not a Challenge Contract, and filing a challenge does not automatically suspend or reverse the subject.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

### Testable conditions

- Every use of Challenge Contract resolves to this exact Definition version or an admitted successor.
- Every claimed instance or use stays within the applicability statement and exclusions.
- No consumer infers admission, authority, success, identity equivalence, or external effect from the term alone.

## Plain-language voice

A Challenge Contract is a closed versioned Policy-bound mechanism defining challengeable subjects, eligible challengers, grounds, evidence, response modes, owner route, resolution gate, timing, and unresolved residue handling. A route string alone is not a Challenge Contract, and filing a challenge does not automatically suspend or reverse the subject.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

In the Lab, Challenge Contract supplies one distinct semantic responsibility in the integrated model. Its carrier and relations remain separate governed contracts.

### Examples

- The Ontology node contract allows evidence-backed contradiction, routes it to the artifact owner, blocks promotion while unresolved, and preserves residue.

## Applicability

A Challenge Contract is a closed versioned Policy-bound mechanism defining challengeable subjects, eligible challengers, grounds, evidence, response modes, owner route, resolution gate, timing, and unresolved residue handling.

### Exclusions

- A route string alone is not a Challenge Contract, and filing a challenge does not automatically suspend or reverse the subject.
- This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect.

## Boundaries

- A route string alone is not a Challenge Contract, and filing a challenge does not automatically suspend or reverse the subject.
- The term supplies meaning only; carrier shape, relation availability, runtime behavior, and authority effect require separate admitted contracts.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.interaction-model-review@2026-10-05 | whole-file | `3c6e2afff90d07c7ea30f40bf7f3e2df8a05a7ff3e9da38c8ffdfd1d717b2c0f` | `candidate-unadmitted` |

## Primary consumers

- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md

## Lookup and drift

- Index: `authority/definitions/candidates/0013-integrated-lab-definition-model/DEFINITIONS-INDEX.md` / `cal.definition.challenge-contract@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0013-integrated-lab-definition-model/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- .arcanum/ontology-vault/2026-10-05-definition-artifact-relation-interaction-review.md
- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md
- .arcanum/ontology-vault/2026-10-06-lab-semantic-gap-audit.md

## Residue

- Definition-owner review and exact admission remain required.
- Artifact Type carrier, relation, qualifier, ontology, runtime, and consumer decisions remain separate.

## Claim ceiling

This candidate defines Challenge Contract for review only. It does not admit the Definition or any carrier, instance, relation, Policy, Decision, runtime behavior, authority, publication, release, deployment, or external effect.
