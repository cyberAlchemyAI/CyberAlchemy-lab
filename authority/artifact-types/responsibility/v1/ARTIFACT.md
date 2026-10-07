<!-- GENERATED FILE: canonical data is artifact.json. -->

# Responsibility Artifact Type v1

- Type: `cal.artifact-type.responsibility/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.responsibility@1.0.0-candidate.1`

## Distinct validation purpose

Responsibility says what someone must answer for, which is different from what they are allowed to authorize.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.assigned-to` | `target` | `person-reference, team` |
| `relation.member-of` | `source` | `role` |

## Non-collapse boundaries

- `responsibility` remains distinct from `role`.
- `responsibility` remains distinct from `role-assignment`.

## Orthogonality rules

- **RESPONSIBILITY-IDENTITY**: A Responsibility instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **RESPONSIBILITY-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **RESPONSIBILITY-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **RESPONSIBILITY-NON-COLLAPSE**: Responsibility remains distinct from role, role-assignment.

## Typed residue

- `RESPONSIBILITY-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Responsibility/v1 candidate. Consequence: The carrier remains candidate-only.
- `RESPONSIBILITY-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Responsibility/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
