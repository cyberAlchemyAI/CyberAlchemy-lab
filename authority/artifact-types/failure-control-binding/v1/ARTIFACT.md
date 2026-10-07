<!-- GENERATED FILE: canonical data is artifact.json. -->

# Failure Control Binding Artifact Type v1

- Type: `cal.artifact-type.failure-control-binding/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.failure-control-binding@1.0.0-candidate.1`

## Distinct validation purpose

A Failure Control Binding is a lifecycle-bearing association between one exact Failure Mode revision and one exact control with exactly one primary role: prevent, detect, contain, recover, or compensate. The binding records intended control and does not prove installation, activation, execution, effectiveness, safety, or authorization.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.controls` | `source` | `failure-mode` |
| `relation.declares-effect-on` | `target` | `decision` |
| `relation.governed-by` | `source` | `policy` |
| `relation.successor-of` | `source` | `failure-control-binding` |
| `relation.successor-of` | `target` | `failure-control-binding` |

## Non-collapse boundaries

- `failure-control-binding` remains distinct from `implementation`.
- `failure-control-binding` remains distinct from `operational-lesson`.

## Orthogonality rules

- **FAILURE-CONTROL-BINDING-IDENTITY**: A Failure Control Binding instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **FAILURE-CONTROL-BINDING-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **FAILURE-CONTROL-BINDING-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **FAILURE-CONTROL-BINDING-NON-COLLAPSE**: Failure Control Binding remains distinct from implementation, operational-lesson.

## Typed residue

- `FAILURE-CONTROL-BINDING-R1` (role:artifact-type-owner): Owner admission for exact Failure Control Binding/v1 bytes. Consequence: Carrier remains candidate-only.
- `FAILURE-CONTROL-BINDING-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Failure Control Binding/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
