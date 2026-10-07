<!-- GENERATED FILE: canonical data is artifact.json. -->

# Intent Resolution Artifact Type v1

- Type: `cal.artifact-type.intent-resolution/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.intent-resolution@1.0.0-candidate.1`

## Distinct validation purpose

An Intent Resolution is an attributable owner decision selecting which governed Product, Project, Goal, Research, Capability, or other output will address one exact Intent and under what satisfaction test. It does not embed Implementation in Intent, prove delivery or satisfaction, or authorize unrelated work.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.declares-effect-on` | `target` | `decision` |
| `relation.successor-of` | `source` | `intent-resolution` |
| `relation.successor-of` | `target` | `intent-resolution` |

## Non-collapse boundaries

- `intent-resolution` remains distinct from `intent`.
- `intent-resolution` remains distinct from `decision`.

## Orthogonality rules

- **INTENT-RESOLUTION-IDENTITY**: A Intent Resolution instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **INTENT-RESOLUTION-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **INTENT-RESOLUTION-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **INTENT-RESOLUTION-NON-COLLAPSE**: Intent Resolution remains distinct from intent, decision.

## Typed residue

- `INTENT-RESOLUTION-R1` (role:artifact-type-owner): Owner admission for exact Intent Resolution/v1 bytes. Consequence: Carrier remains candidate-only.
- `INTENT-RESOLUTION-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Intent Resolution/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
