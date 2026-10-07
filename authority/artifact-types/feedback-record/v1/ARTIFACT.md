<!-- GENERATED FILE: canonical data is artifact.json. -->

# Feedback Record Artifact Type v1

- Type: `cal.artifact-type.feedback-record/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.feedback-record@1.0.0-candidate.1`

## Distinct validation purpose

A Feedback Record is an attributable immutable record of a correction, rejection, edit, preference expression, requirement change, or other response bound to an exact source, target, time, and context. Feedback is not automatically fact, Policy, Decision, stable preference, lesson, or permission.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.derives-from` | `target` | `agent-reflection, classification-assignment, operational-lesson` |
| `relation.evidence-bears-on` | `source` | `challenge-event, classification-assignment, drift-assessment, failure-assessment, failure-occurrence, improvement-signal, lesson-outcome-assessment, operational-lesson, preference-application-assessment, work-outcome-assessment` |
| `relation.governed-by` | `source` | `policy` |
| `relation.originates-from` | `source` | `source` |
| `relation.produces` | `target` | `agent-action` |
| `relation.successor-of` | `source` | `feedback-record` |
| `relation.successor-of` | `target` | `feedback-record` |

## Non-collapse boundaries

- `feedback-record` remains distinct from `decision`.
- `feedback-record` remains distinct from `communication-preference`.

## Orthogonality rules

- **FEEDBACK-RECORD-IDENTITY**: A Feedback Record instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **FEEDBACK-RECORD-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **FEEDBACK-RECORD-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **FEEDBACK-RECORD-NON-COLLAPSE**: Feedback Record remains distinct from decision, communication-preference.

## Typed residue

- `FEEDBACK-RECORD-R1` (role:artifact-type-owner): Owner admission for exact Feedback Record/v1 bytes. Consequence: Carrier remains candidate-only.
- `FEEDBACK-RECORD-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Feedback Record/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
