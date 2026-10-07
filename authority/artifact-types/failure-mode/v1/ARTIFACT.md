<!-- GENERATED FILE: canonical data is artifact.json. -->

# Failure Mode Artifact Type v1

- Type: `cal.artifact-type.failure-mode/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.failure-mode@1.0.0-candidate.1`

## Distinct validation purpose

A Failure Mode is a versioned reusable design-time contract for one distinct way a declared subject kind can fail an exact boundary under stated conditions. A Failure Mode can predate occurrences and does not establish that any occurrence happened.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.controls` | `target` | `failure-control-binding` |
| `relation.declares-effect-on` | `target` | `decision` |
| `relation.governed-by` | `source` | `policy` |
| `relation.instance-of` | `source` | `classification-value` |
| `relation.instance-of` | `target` | `failure-occurrence` |
| `relation.successor-of` | `source` | `failure-mode` |
| `relation.successor-of` | `target` | `failure-mode` |

## Non-collapse boundaries

- `failure-mode` remains distinct from `failure-occurrence`.
- `failure-mode` remains distinct from `operational-lesson`.

## Orthogonality rules

- **FAILURE-MODE-IDENTITY**: A Failure Mode instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **FAILURE-MODE-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **FAILURE-MODE-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **FAILURE-MODE-NON-COLLAPSE**: Failure Mode remains distinct from failure-occurrence, operational-lesson.

## Typed residue

- `FAILURE-MODE-R1` (role:artifact-type-owner): Owner admission for exact Failure Mode/v1 bytes. Consequence: Carrier remains candidate-only.
- `FAILURE-MODE-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Failure Mode/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
