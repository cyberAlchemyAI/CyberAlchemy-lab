<!-- GENERATED FILE: canonical data is artifact.json. -->

# Hypothesis Artifact Type v1

- Type: `cal.artifact-type.hypothesis/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.hypothesis@1.0.0-candidate.1`

## Distinct validation purpose

A hypothesis is an idea framed so evidence can test it, not an assumption the project has already chosen to rely on.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.evidence-bears-on` | `target` | `evidence-set, measurement-result, observation` |

## Non-collapse boundaries

- `hypothesis` remains distinct from `product-thesis`.
- `hypothesis` remains distinct from `premise`.

## Orthogonality rules

- **HYPOTHESIS-IDENTITY**: A Hypothesis instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **HYPOTHESIS-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **HYPOTHESIS-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **HYPOTHESIS-NON-COLLAPSE**: Hypothesis remains distinct from product-thesis, premise.

## Typed residue

- `HYPOTHESIS-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Hypothesis/v1 candidate. Consequence: The carrier remains candidate-only.
- `HYPOTHESIS-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Hypothesis/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
