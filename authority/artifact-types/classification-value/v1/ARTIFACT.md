<!-- GENERATED FILE: canonical data is artifact.json. -->

# Classification Value Artifact Type v1

- Type: `cal.artifact-type.classification-value/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.classification-value@1.0.0-candidate.1`

## Distinct validation purpose

A Classification Value is one governed allowed answer under one exact Classification Axis and Scheme version, with stable identity, meaning, applicability, exclusions, and mappings. Its label is not its identity, and similar labels across axes do not collapse their meanings.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.instance-of` | `target` | `agent-action, agent-instance, failure-mode, failure-occurrence, improvement-target, operational-lesson` |
| `relation.member-of` | `source` | `classification-scheme` |
| `relation.successor-of` | `source` | `classification-value` |
| `relation.successor-of` | `target` | `classification-value` |

## Non-collapse boundaries

- `classification-value` remains distinct from `definition`.
- `classification-value` remains distinct from `classification-assignment`.

## Orthogonality rules

- **CLASSIFICATION-VALUE-IDENTITY**: A Classification Value instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **CLASSIFICATION-VALUE-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **CLASSIFICATION-VALUE-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **CLASSIFICATION-VALUE-NON-COLLAPSE**: Classification Value remains distinct from definition, classification-assignment.

## Typed residue

- `CLASSIFICATION-VALUE-R1` (role:artifact-type-owner): Owner admission for exact Classification Value/v1 bytes. Consequence: Carrier remains candidate-only.
- `CLASSIFICATION-VALUE-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Classification Value/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
