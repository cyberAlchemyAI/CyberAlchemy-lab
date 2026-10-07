<!-- GENERATED FILE: canonical data is artifact.json. -->

# Person Artifact Type v1

- Type: `cal.artifact-type.person/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.person@1.0.0-candidate.1`

## Distinct validation purpose

A person is the human being, not their account, role, or database record.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.asserts-identity-of` | `target` | `person-reference` |

## Non-collapse boundaries

- `person` remains distinct from `person-reference`.
- `person` remains distinct from `agent`.

## Orthogonality rules

- **PERSON-IDENTITY**: A Person instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **PERSON-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **PERSON-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **PERSON-NON-COLLAPSE**: Person remains distinct from person-reference, agent.

## Typed residue

- `PERSON-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Person/v1 candidate. Consequence: The carrier remains candidate-only.
- `PERSON-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Person/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
