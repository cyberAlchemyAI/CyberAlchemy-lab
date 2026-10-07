<!-- GENERATED FILE: canonical data is artifact.json. -->

# Review Artifact Type v1

- Type: `cal.artifact-type.review/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.review@1.0.0-candidate.1`

## Distinct validation purpose

A Review is an attributable bounded assessment of exact subject versions against declared questions, criteria, evidence, alternatives, and a claim ceiling. A Review is not admission, approval, validation, fact, or execution unless a separate Decision grants that effect.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.frames` | `target` | `context` |

## Non-collapse boundaries

- `review` remains distinct from `evaluation`.
- `review` remains distinct from `finding`.

## Orthogonality rules

- **REVIEW-IDENTITY**: A Review instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **REVIEW-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **REVIEW-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **REVIEW-NON-COLLAPSE**: Review remains distinct from evaluation, finding.

## Typed residue

- `REVIEW-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Review/v1 candidate. Consequence: The carrier remains candidate-only.
- `REVIEW-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Review/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
