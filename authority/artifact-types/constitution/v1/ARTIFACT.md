<!-- GENERATED FILE: canonical data is artifact.json. -->

# Constitution Artifact Type v1

- Type: `cal.artifact-type.constitution/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.constitution@1.0.0-candidate.1`

## Distinct validation purpose

A constitution is a named rulebook for named things. It says which rules apply,
to what, under whose authority, and how conflicts and checks work. It is not a
universal prompt for every person, agent, repository, or external system.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.governed-by` | `target` | `artifact-type, definition, relation-kind` |
| `relation.successor-of` | `source` | `constitution` |
| `relation.successor-of` | `target` | `constitution` |

## Non-collapse boundaries

- `constitution` remains distinct from `policy`.
- `constitution` remains distinct from `contract`.

## Orthogonality rules

- **CONSTITUTION-IDENTITY**: A Constitution instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **CONSTITUTION-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **CONSTITUTION-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **CONSTITUTION-NON-COLLAPSE**: Constitution remains distinct from policy, contract.

## Typed residue

- `CONSTITUTION-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Constitution/v1 candidate. Consequence: The carrier remains candidate-only.
- `CONSTITUTION-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Constitution/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
