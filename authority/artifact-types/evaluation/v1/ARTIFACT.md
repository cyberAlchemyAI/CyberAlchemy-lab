<!-- GENERATED FILE: canonical data is artifact.json. -->

# Evaluation Artifact Type v1

- Type: `cal.artifact-type.evaluation/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.evaluation@1.0.0-candidate.1`

## Distinct validation purpose

An Evaluation runs a declared set of checks against exact inputs and records every result, including the checks that could not yet be evaluated.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.evaluates` | `source` | `capability-realization-binding, product-capability, product-thesis` |

## Non-collapse boundaries

- `evaluation` remains distinct from `measurement-result`.
- `evaluation` remains distinct from `review`.

## Orthogonality rules

- **EVALUATION-IDENTITY**: A Evaluation instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **EVALUATION-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **EVALUATION-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **EVALUATION-NON-COLLAPSE**: Evaluation remains distinct from measurement-result, review.

## Typed residue

- `EVALUATION-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Evaluation/v1 candidate. Consequence: The carrier remains candidate-only.
- `EVALUATION-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Evaluation/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
