<!-- GENERATED FILE: canonical data is artifact.json. -->

# Operational Observation Artifact Type v1

- Type: `cal.artifact-type.operational-observation/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.operational-observation@1.0.0-candidate.1`

## Distinct validation purpose

An Operational Observation is an attributable bounded datum recorded during ordinary Project work outside the Research or Experiment-specific Observation boundary. It records what was observed, not its cause, importance, correctness, lesson, failure classification, or required response.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.derives-from` | `target` | `agent-reflection, classification-assignment, improvement-signal` |
| `relation.evidence-bears-on` | `source` | `challenge-event, classification-assignment, drift-assessment, failure-assessment, failure-occurrence, improvement-signal, lesson-outcome-assessment, operational-lesson, preference-application-assessment, work-outcome-assessment` |
| `relation.originates-from` | `source` | `source` |
| `relation.produces` | `target` | `agent-action` |
| `relation.successor-of` | `source` | `operational-observation` |
| `relation.successor-of` | `target` | `operational-observation` |

## Non-collapse boundaries

- `operational-observation` remains distinct from `observation`.
- `operational-observation` remains distinct from `finding`.

## Orthogonality rules

- **OPERATIONAL-OBSERVATION-IDENTITY**: A Operational Observation instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **OPERATIONAL-OBSERVATION-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **OPERATIONAL-OBSERVATION-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **OPERATIONAL-OBSERVATION-NON-COLLAPSE**: Operational Observation remains distinct from observation, finding.

## Typed residue

- `OPERATIONAL-OBSERVATION-R1` (role:artifact-type-owner): Owner admission for exact Operational Observation/v1 bytes. Consequence: Carrier remains candidate-only.
- `OPERATIONAL-OBSERVATION-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Operational Observation/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
