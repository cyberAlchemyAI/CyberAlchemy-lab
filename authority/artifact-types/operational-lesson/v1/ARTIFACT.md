<!-- GENERATED FILE: canonical data is artifact.json. -->

# Operational Lesson Artifact Type v1

- Type: `cal.artifact-type.operational-lesson/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.operational-lesson@1.0.0-candidate.1`

## Distinct validation purpose

An Operational Lesson is a versioned evidence-bounded and scope-limited candidate for how future Project work may be interpreted or performed, with applicability, exclusions, predicted benefit, and falsifier. Persistence does not make it an instruction, Policy, fact, authority grant, or proof of benefit.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.applies-lesson` | `target` | `lesson-application` |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.declares-effect-on` | `target` | `decision` |
| `relation.derives-from` | `source` | `agent-reflection, evidence-set, failure-assessment, feedback-record, finding, lesson-outcome-assessment` |
| `relation.derives-from` | `target` | `improvement-target` |
| `relation.evidence-bears-on` | `target` | `evidence-set, feedback-record, finding, measurement-result, observation, operational-observation` |
| `relation.governed-by` | `source` | `policy` |
| `relation.instance-of` | `source` | `classification-value` |
| `relation.produces` | `target` | `agent-action` |
| `relation.successor-of` | `source` | `operational-lesson` |
| `relation.successor-of` | `target` | `operational-lesson` |

## Non-collapse boundaries

- `operational-lesson` remains distinct from `policy`.
- `operational-lesson` remains distinct from `session-memory`.

## Orthogonality rules

- **OPERATIONAL-LESSON-IDENTITY**: A Operational Lesson instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **OPERATIONAL-LESSON-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **OPERATIONAL-LESSON-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **OPERATIONAL-LESSON-NON-COLLAPSE**: Operational Lesson remains distinct from policy, session-memory.

## Typed residue

- `OPERATIONAL-LESSON-R1` (role:artifact-type-owner): Owner admission for exact Operational Lesson/v1 bytes. Consequence: Carrier remains candidate-only.
- `OPERATIONAL-LESSON-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Operational Lesson/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
