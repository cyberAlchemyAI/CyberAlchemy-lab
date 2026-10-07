<!-- GENERATED FILE: canonical data is artifact.json. -->

# Work Outcome Assessment Artifact Type v1

- Type: `cal.artifact-type.work-outcome-assessment/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.work-outcome-assessment@1.0.0-candidate.1`

## Distinct validation purpose

A Work Outcome Assessment is an evidence-bounded comparison between one Work item or Agent Action’s declared expected result and its observed result. It does not by itself establish lesson value, causal attribution, Product value, acceptance, or authority effect.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.derives-from` | `target` | `agent-reflection, improvement-signal` |
| `relation.evaluates` | `source` | `agent-action, work` |
| `relation.evidence-bears-on` | `target` | `evidence-set, feedback-record, finding, measurement-result, observation, operational-observation` |
| `relation.produces` | `target` | `agent-action` |
| `relation.successor-of` | `source` | `work-outcome-assessment` |
| `relation.successor-of` | `target` | `work-outcome-assessment` |

## Non-collapse boundaries

- `work-outcome-assessment` remains distinct from `lesson-outcome-assessment`.
- `work-outcome-assessment` remains distinct from `evaluation`.

## Orthogonality rules

- **WORK-OUTCOME-ASSESSMENT-IDENTITY**: A Work Outcome Assessment instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **WORK-OUTCOME-ASSESSMENT-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **WORK-OUTCOME-ASSESSMENT-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **WORK-OUTCOME-ASSESSMENT-NON-COLLAPSE**: Work Outcome Assessment remains distinct from lesson-outcome-assessment, evaluation.

## Typed residue

- `WORK-OUTCOME-ASSESSMENT-R1` (role:artifact-type-owner): Owner admission for exact Work Outcome Assessment/v1 bytes. Consequence: Carrier remains candidate-only.
- `WORK-OUTCOME-ASSESSMENT-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Work Outcome Assessment/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
