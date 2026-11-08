<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Semantic Event History

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.semantic-event-history`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:semantic-event-history-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Semantic Event History is the canonical append-only replay history of complete resulting semantic states for one Ontology subject under exact ordering and integrity rules. It does not own Governance decisions, and its calculated snapshots or views are not competing replay sources.

```text
SemanticEventHistory(x) => governed_identity_or_record(x) and bounded_scope(x); SemanticEventHistory(x) =/=> authority_effect(x).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Semantic Event History Definition. |

### Boundary conditions

- A Semantic Event History is the canonical append-only replay history of complete resulting semantic states for one Ontology subject under exact ordering and integrity rules.
- It does not own Governance decisions, and its calculated snapshots or views are not competing replay sources.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

### Testable conditions

- Every use of Semantic Event History resolves to this exact Definition version or an admitted successor.
- Every claimed instance or use stays within the applicability statement and exclusions.
- No consumer infers admission, authority, success, identity equivalence, or external effect from the term alone.

## Plain-language voice

A Semantic Event History is the canonical append-only replay history of complete resulting semantic states for one Ontology subject under exact ordering and integrity rules. It does not own Governance decisions, and its calculated snapshots or views are not competing replay sources.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

In the Lab, Semantic Event History supplies one distinct semantic responsibility in the integrated model. Its carrier and relations remain separate governed contracts.

### Examples

- The history for node:artifact-type-definition records each complete resulting semantic state and digest in cursor order.

## Applicability

A Semantic Event History is the canonical append-only replay history of complete resulting semantic states for one Ontology subject under exact ordering and integrity rules.

### Exclusions

- It does not own Governance decisions, and its calculated snapshots or views are not competing replay sources.
- This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect.

## Boundaries

- It does not own Governance decisions, and its calculated snapshots or views are not competing replay sources.
- The term supplies meaning only; carrier shape, relation availability, runtime behavior, and authority effect require separate admitted contracts.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.interaction-model-review@2026-10-05 | whole-file | `3c6e2afff90d07c7ea30f40bf7f3e2df8a05a7ff3e9da38c8ffdfd1d717b2c0f` | `candidate-unadmitted` |

## Primary consumers

- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md

## Lookup and drift

- Index: `authority/definitions/candidates/0013-integrated-lab-definition-model/DEFINITIONS-INDEX.md` / `cal.definition.semantic-event-history@1.0.0-candidate.1`
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

This candidate defines Semantic Event History for review only. It does not admit the Definition or any carrier, instance, relation, Policy, Decision, runtime behavior, authority, publication, release, deployment, or external effect.
