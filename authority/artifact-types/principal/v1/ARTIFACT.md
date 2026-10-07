<!-- GENERATED FILE: canonical data is artifact.json. -->

# Principal Artifact Type v1

- Type: `cal.artifact-type.principal/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.principal@1.0.0-candidate.1`

## Distinct validation purpose

A Principal is a governed identity recognized by an authentication, authorization, ownership, or accountability boundary. Principal identity is recognized only inside exact authentication, authorization, ownership, or accountability boundaries.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.acts-for` | `target` | `agent-instance` |
| `relation.asserts-identity-of` | `target` | `principal-reference` |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.successor-of` | `source` | `principal` |
| `relation.successor-of` | `target` | `principal` |

## Non-collapse boundaries

- `principal` remains distinct from `person`.
- `principal` remains distinct from `role`.

## Orthogonality rules

- **PRINCIPAL-IDENTITY**: A Principal instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **PRINCIPAL-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **PRINCIPAL-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **PRINCIPAL-NON-COLLAPSE**: Principal remains distinct from person, role.

## Typed residue

- `PRINCIPAL-R1` (role:artifact-type-owner): Owner admission for exact Principal/v1 bytes. Consequence: Carrier remains candidate-only.
- `PRINCIPAL-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Principal/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
