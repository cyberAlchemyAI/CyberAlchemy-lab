<!-- GENERATED FILE: canonical data is artifact.json. -->

# Lesson Outcome Assessment Artifact Type v1

- Type: `cal.artifact-type.lesson-outcome-assessment/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.lesson-outcome-assessment@1.0.0-candidate.1`

## Distinct validation purpose

A Lesson Outcome Assessment is an evidence-bounded comparison of one Lesson Application’s predicted benefit or falsifier with its observed outcome. Task completion, repetition, Agent self-report, or absence of correction alone does not prove benefit.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.derives-from` | `target` | `improvement-target, operational-lesson` |
| `relation.evaluates` | `source` | `lesson-application` |
| `relation.evidence-bears-on` | `target` | `evidence-set, feedback-record, finding, measurement-result, observation, operational-observation` |
| `relation.successor-of` | `source` | `lesson-outcome-assessment` |
| `relation.successor-of` | `target` | `lesson-outcome-assessment` |

## Non-collapse boundaries

- `lesson-outcome-assessment` remains distinct from `work-outcome-assessment`.
- `lesson-outcome-assessment` remains distinct from `decision`.

## Orthogonality rules

- **LESSON-OUTCOME-ASSESSMENT-IDENTITY**: A Lesson Outcome Assessment instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **LESSON-OUTCOME-ASSESSMENT-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **LESSON-OUTCOME-ASSESSMENT-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **LESSON-OUTCOME-ASSESSMENT-NON-COLLAPSE**: Lesson Outcome Assessment remains distinct from work-outcome-assessment, decision.

## Typed residue

- `LESSON-OUTCOME-ASSESSMENT-R1` (role:artifact-type-owner): Owner admission for exact Lesson Outcome Assessment/v1 bytes. Consequence: Carrier remains candidate-only.
- `LESSON-OUTCOME-ASSESSMENT-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Lesson Outcome Assessment/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
