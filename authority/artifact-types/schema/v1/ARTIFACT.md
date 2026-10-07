<!-- GENERATED FILE: canonical data is artifact.json. -->

# Schema Artifact Type v1

- Type: `cal.artifact-type.schema/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.schema@1.0.0-candidate.1`

## Distinct validation purpose

The form the evidence must fit. A schema says what kinds of thing there may be,
what may go inside them, and how they may be wired together — and nothing at all
about whether any of it is true, owned, or approved.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.binds-implementation` | `target` | `implementation` |
| `relation.successor-of` | `source` | `schema` |
| `relation.successor-of` | `target` | `schema` |

## Non-collapse boundaries

- `schema` remains distinct from `artifact-type`.
- `schema` remains distinct from `contract`.

## Orthogonality rules

- **SCHEMA-IDENTITY**: A Schema instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **SCHEMA-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **SCHEMA-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **SCHEMA-NON-COLLAPSE**: Schema remains distinct from artifact-type, contract.

## Typed residue

- `SCHEMA-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Schema/v1 candidate. Consequence: The carrier remains candidate-only.
- `SCHEMA-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Schema/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
