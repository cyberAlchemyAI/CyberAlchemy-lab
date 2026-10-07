<!-- GENERATED FILE: canonical data is artifact.json. -->

# Effect Artifact Type v1

- Type: `cal.artifact-type.effect/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.effect@1.0.0-candidate.1`

## Distinct validation purpose

An Effect is a declared change in governed state, rights, obligations, external condition, or interpretation that a Decision or Action intends, authorizes, records, or observes under an exact effect kind. Declaring, authorizing, attempting, delivering, and observing an Effect are separate facts.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.declares-effect-on` | `target` | `decision` |

## Non-collapse boundaries

- `effect` remains distinct from `decision`.
- `effect` remains distinct from `execution`.

## Orthogonality rules

- **EFFECT-IDENTITY**: A Effect instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **EFFECT-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **EFFECT-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **EFFECT-NON-COLLAPSE**: Effect remains distinct from decision, execution.

## Typed residue

- `EFFECT-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Effect/v1 candidate. Consequence: The carrier remains candidate-only.
- `EFFECT-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Effect/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
