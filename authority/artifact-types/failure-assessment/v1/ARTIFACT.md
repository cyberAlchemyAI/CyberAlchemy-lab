<!-- GENERATED FILE: canonical data is artifact.json. -->

# Failure Assessment Artifact Type v1

- Type: `cal.artifact-type.failure-assessment/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.failure-assessment@1.0.0-candidate.1`

## Distinct validation purpose

A Failure Assessment is a versioned evidence-bounded evaluation of one Failure Occurrence or declared cohort across independent occurrence, mode, cause, impact, containment, recovery, and uncertainty postures. No posture may be inferred from another; recovery can coexist with unresolved cause and residue.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.declares-effect-on` | `target` | `decision` |
| `relation.derives-from` | `target` | `agent-reflection, improvement-signal, operational-lesson` |
| `relation.evaluates` | `source` | `failure-occurrence` |
| `relation.evidence-bears-on` | `target` | `evidence-set, feedback-record, finding, measurement-result, observation, operational-observation` |
| `relation.governed-by` | `source` | `policy` |
| `relation.produces` | `target` | `agent-action` |
| `relation.successor-of` | `source` | `failure-assessment` |
| `relation.successor-of` | `target` | `failure-assessment` |

## Non-collapse boundaries

- `failure-assessment` remains distinct from `finding`.
- `failure-assessment` remains distinct from `decision`.

## Orthogonality rules

- **FAILURE-ASSESSMENT-IDENTITY**: A Failure Assessment instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **FAILURE-ASSESSMENT-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **FAILURE-ASSESSMENT-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **FAILURE-ASSESSMENT-NON-COLLAPSE**: Failure Assessment remains distinct from finding, decision.

## Typed residue

- `FAILURE-ASSESSMENT-R1` (role:artifact-type-owner): Owner admission for exact Failure Assessment/v1 bytes. Consequence: Carrier remains candidate-only.
- `FAILURE-ASSESSMENT-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Failure Assessment/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
