<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Project Governance Event History

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.project-governance-event-history`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:project-governance-event-history-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Project Governance Event History is the canonical append-only governance history for Project State transitions, binding each governance event to one exact semantic event tuple, owner decision, authorization, Policy, Challenge Contract, and upstream evidence. It records why and under which authority a Project State transition was accepted; it cannot patch semantic state or originate authority by itself.

```text
ProjectGovernanceEventHistory(x) => append_only(x) and digest_bound(x); ProjectGovernanceEventHistory(x) =/=> authority_effect(x).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One history evaluated under the Project Governance Event History Definition. |

### Boundary conditions

- A Project Governance Event History is the canonical append-only governance history for Project State transitions, binding each governance event to one exact semantic event tuple, owner decision, authorization, Policy, Challenge Contract, and upstream evidence.
- It records why and under which authority a Project State transition was accepted; it cannot patch semantic state or originate authority by itself.
- Identity, evidence, authority, and lifecycle effects remain separately governed.

### Testable conditions

- Every event has one cursor, predecessor digest, event digest, and exact record reference.
- Every use resolves this admitted Definition version or a later admitted successor.
- No consumer infers authority, runtime activation, or ontology truth from the term alone.

## Plain-language voice

A Project Governance Event History is the canonical append-only governance history for Project State transitions, binding each governance event to one exact semantic event tuple, owner decision, authorization, Policy, Challenge Contract, and upstream evidence. It records why and under which authority a Project State transition was accepted; it cannot patch semantic state or originate authority by itself.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

In the Lab, Project Governance Event History supplies the replay surface needed by immutable Project State successors.

### Examples

- The first governance event binds the Decision 0071 owner authorization and immutable admission bundle to semantic event 1.

## Applicability

A Project Governance Event History is the canonical append-only governance history for Project State transitions, binding each governance event to one exact semantic event tuple, owner decision, authorization, Policy, Challenge Contract, and upstream evidence.

### Exclusions

- It records why and under which authority a Project State transition was accepted; it cannot patch semantic state or originate authority by itself.
- This Definition does not create an Artifact Type, instance, Typed Relation, runtime, authority grant, or external effect.

## Boundaries

- It records why and under which authority a Project State transition was accepted; it cannot patch semantic state or originate authority by itself.
- The term supplies meaning only; carrier shape, admission, relation availability, runtime behavior, and authority effect require separate admitted contracts.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.decision-0071-operational-foundation | whole-file | `0ac9897c473b60906149e249e51211e516dd26181f5cf79094c7f253a7cf5b30` | `admitted` |

## Primary consumers

- cal.artifact-type.project-state/v1

## Lookup and drift

- Index: `authority/definitions/DEFINITIONS-INDEX.md` / `cal.definition.project-governance-event-history@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0013-integrated-lab-definition-model/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- docs/decisions/0071-cyberalchemy-lab-operational-foundation-admission/decision.json
- authority/admissions/cyberalchemy-lab-operational-foundation/v1/bundle.json

## Residue

- Definition and carrier admission are atomic in Decision 0072.
- Runtime consumption and later state transitions remain separate.

## Claim ceiling

This candidate defines Project Governance Event History for the Decision 0071 bootstrap only. It creates no admission, Project State transition, relation, runtime, or external effect.
