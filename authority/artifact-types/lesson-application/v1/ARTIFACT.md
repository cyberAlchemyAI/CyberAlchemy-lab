<!-- GENERATED FILE: canonical data is artifact.json. -->

# Lesson Application Artifact Type v1

- Type: `cal.artifact-type.lesson-application/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.lesson-application@1.0.0-candidate.1`

## Distinct validation purpose

A Lesson Application is an immutable record that one exact Operational Lesson revision was selected and actually used or deliberately not used for one later Session or Action. Selection, presentation, applicability, use, compliance, and success are separate facts.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.applies-lesson` | `source` | `operational-lesson` |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.evaluates` | `target` | `lesson-outcome-assessment` |
| `relation.produces` | `target` | `agent-action` |
| `relation.successor-of` | `source` | `lesson-application` |
| `relation.successor-of` | `target` | `lesson-application` |

## Non-collapse boundaries

- `lesson-application` remains distinct from `operational-lesson`.
- `lesson-application` remains distinct from `lesson-outcome-assessment`.

## Orthogonality rules

- **LESSON-APPLICATION-IDENTITY**: A Lesson Application instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **LESSON-APPLICATION-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **LESSON-APPLICATION-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **LESSON-APPLICATION-NON-COLLAPSE**: Lesson Application remains distinct from operational-lesson, lesson-outcome-assessment.

## Typed residue

- `LESSON-APPLICATION-R1` (role:artifact-type-owner): Owner admission for exact Lesson Application/v1 bytes. Consequence: Carrier remains candidate-only.
- `LESSON-APPLICATION-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Lesson Application/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
