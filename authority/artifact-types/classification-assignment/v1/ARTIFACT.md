<!-- GENERATED FILE: canonical data is artifact.json. -->

# Classification Assignment Artifact Type v1

- Type: `cal.artifact-type.classification-assignment/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.classification-assignment@1.0.0-candidate.1`

## Distinct validation purpose

A Classification Assignment is an immutable attributable binding of one exact subject revision to one exact Scheme version, Axis, and Value with basis, evidence, lifecycle, owner, and challenge route. Correction creates a successor assignment; the assignment does not change subject identity or imply facts from other axes.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.declares-effect-on` | `target` | `decision` |
| `relation.derives-from` | `source` | `evidence-set, feedback-record, finding, measurement-result, observation, operational-observation, source` |
| `relation.evidence-bears-on` | `target` | `evidence-set, feedback-record, finding, measurement-result, observation, operational-observation` |
| `relation.governed-by` | `source` | `classification-scheme, policy` |
| `relation.produces` | `target` | `agent-action` |
| `relation.successor-of` | `source` | `classification-assignment` |
| `relation.successor-of` | `target` | `classification-assignment` |

## Non-collapse boundaries

- `classification-assignment` remains distinct from `typed-relation`.
- `classification-assignment` remains distinct from `identity-claim`.

## Orthogonality rules

- **CLASSIFICATION-ASSIGNMENT-IDENTITY**: A Classification Assignment instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **CLASSIFICATION-ASSIGNMENT-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **CLASSIFICATION-ASSIGNMENT-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **CLASSIFICATION-ASSIGNMENT-NON-COLLAPSE**: Classification Assignment remains distinct from typed-relation, identity-claim.

## Typed residue

- `CLASSIFICATION-ASSIGNMENT-R1` (role:artifact-type-owner): Owner admission for exact Classification Assignment/v1 bytes. Consequence: Carrier remains candidate-only.
- `CLASSIFICATION-ASSIGNMENT-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Classification Assignment/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
