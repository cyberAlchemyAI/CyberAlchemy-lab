<!-- GENERATED FILE: canonical data is artifact.json. -->

# Agent Reflection Artifact Type v1

- Type: `cal.artifact-type.agent-reflection/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.agent-reflection@1.0.0-candidate.1`

## Distinct validation purpose

An Agent Reflection is an attributable revisable diagnostic interpretation of exact Agent Sessions, Actions, outputs, observations, feedback, evidence, and residue. It is not hidden chain of thought, Observation, Finding, Decision, Definition, Policy, proof of improvement, or authority.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.derives-from` | `source` | `agent-action, agent-session, evidence-set, failure-assessment, feedback-record, finding, observation, operational-observation, work-outcome-assessment` |
| `relation.derives-from` | `target` | `operational-lesson` |
| `relation.produces` | `target` | `agent-action` |
| `relation.successor-of` | `source` | `agent-reflection` |
| `relation.successor-of` | `target` | `agent-reflection` |

## Non-collapse boundaries

- `agent-reflection` remains distinct from `finding`.
- `agent-reflection` remains distinct from `operational-lesson`.

## Orthogonality rules

- **AGENT-REFLECTION-IDENTITY**: A Agent Reflection instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **AGENT-REFLECTION-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **AGENT-REFLECTION-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **AGENT-REFLECTION-NON-COLLAPSE**: Agent Reflection remains distinct from finding, operational-lesson.

## Typed residue

- `AGENT-REFLECTION-R1` (role:artifact-type-owner): Owner admission for exact Agent Reflection/v1 bytes. Consequence: Carrier remains candidate-only.
- `AGENT-REFLECTION-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Agent Reflection/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
