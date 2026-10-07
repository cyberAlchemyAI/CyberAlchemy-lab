<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Lesson Application

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.lesson-application`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:lesson-application-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Lesson Application is an immutable record that one exact Operational Lesson revision was selected and actually used or deliberately not used for one later Session or Action. Selection, presentation, applicability, use, compliance, and success are separate facts.

```text
LessonApplication(x) => governed_identity_or_record(x) and bounded_scope(x); LessonApplication(x) =/=> authority_effect(x).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Lesson Application Definition. |

### Boundary conditions

- A Lesson Application is an immutable record that one exact Operational Lesson revision was selected and actually used or deliberately not used for one later Session or Action.
- Selection, presentation, applicability, use, compliance, and success are separate facts.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

### Testable conditions

- Every use of Lesson Application resolves to this exact Definition version or an admitted successor.
- Every claimed instance or use stays within the applicability statement and exclusions.
- No consumer infers admission, authority, success, identity equivalence, or external effect from the term alone.

## Plain-language voice

A Lesson Application is an immutable record that one exact Operational Lesson revision was selected and actually used or deliberately not used for one later Session or Action. Selection, presentation, applicability, use, compliance, and success are separate facts.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

In the Lab, Lesson Application supplies one distinct semantic responsibility in the integrated model. Its carrier and relations remain separate governed contracts.

### Examples

- A later relation audit records that OL-07 was presented, applicable, and used to resolve the effective predecessor.

## Applicability

A Lesson Application is an immutable record that one exact Operational Lesson revision was selected and actually used or deliberately not used for one later Session or Action.

### Exclusions

- Selection, presentation, applicability, use, compliance, and success are separate facts.
- This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect.

## Boundaries

- Selection, presentation, applicability, use, compliance, and success are separate facts.
- The term supplies meaning only; carrier shape, relation availability, runtime behavior, and authority effect require separate admitted contracts.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.learning-model-review@2026-10-05 | whole-file | `e2fe199f3affffdc272d37bf59749b202884ea0e8fa8b48357e867c0962e2bf9` | `candidate-unadmitted` |

## Primary consumers

- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md

## Lookup and drift

- Index: `authority/definitions/candidates/0013-integrated-lab-definition-model/DEFINITIONS-INDEX.md` / `cal.definition.lesson-application@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0013-integrated-lab-definition-model/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- .arcanum/ontology-vault/2026-10-05-agent-operational-learning-model-review.md
- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md
- .arcanum/ontology-vault/2026-10-06-lab-semantic-gap-audit.md

## Residue

- Definition-owner review and exact admission remain required.
- Artifact Type carrier, relation, qualifier, ontology, runtime, and consumer decisions remain separate.

## Claim ceiling

This candidate defines Lesson Application for review only. It does not admit the Definition or any carrier, instance, relation, Policy, Decision, runtime behavior, authority, publication, release, deployment, or external effect.
