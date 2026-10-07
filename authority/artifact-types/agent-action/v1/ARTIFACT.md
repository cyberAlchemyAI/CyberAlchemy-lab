<!-- GENERATED FILE: canonical data is artifact.json. -->

# Agent Action Artifact Type v1

- Type: `cal.artifact-type.agent-action/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.agent-action@1.0.0-candidate.1`

## Distinct validation purpose

An Agent Action is an immutable attributable record of one proposed, attempted, completed, rejected, or failed operation by an Agent Instance within one Session. Every Agent Action is attributed to one exact Agent Instance inside one exact active Session.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.contributes-to` | `source` | `goal, product` |
| `relation.derives-from` | `target` | `agent-reflection` |
| `relation.evaluates` | `target` | `work-outcome-assessment` |
| `relation.governed-by` | `source` | `policy` |
| `relation.instance-of` | `source` | `classification-value` |
| `relation.member-of` | `source` | `agent-session` |
| `relation.occurs-during` | `target` | `failure-occurrence` |
| `relation.performs` | `target` | `agent-instance` |
| `relation.produces` | `source` | `agent-reflection, challenge-event, classification-assignment, definition, drift-assessment, evidence-set, failure-assessment, failure-occurrence, feedback-record, finding, generated-output, improvement-signal, lesson-application, measurement-result, observation, operational-lesson, operational-observation, typed-relation, work-outcome-assessment` |
| `relation.responds-to` | `source` | `failure-occurrence, incident` |
| `relation.successor-of` | `source` | `agent-action` |
| `relation.successor-of` | `target` | `agent-action` |
| `relation.uses-method` | `source` | `method` |
| `relation.uses-tool` | `source` | `implementation, tool` |

## Non-collapse boundaries

- `agent-action` remains distinct from `work`.
- `agent-action` remains distinct from `decision`.

## Orthogonality rules

- **AGENT-ACTION-IDENTITY**: A Agent Action instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **AGENT-ACTION-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **AGENT-ACTION-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **AGENT-ACTION-NON-COLLAPSE**: Agent Action remains distinct from work, decision.

## Typed residue

- `AGENT-ACTION-R1` (role:artifact-type-owner): Owner admission for exact Agent Action/v1 bytes. Consequence: Carrier remains candidate-only.
- `AGENT-ACTION-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Agent Action/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
