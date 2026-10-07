<!-- GENERATED FILE: canonical data is artifact.json. -->

# Decision Scope Artifact Type v1

- Type: `cal.artifact-type.decision-scope/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.decision-scope@1.0.0-candidate.1`

## Distinct validation purpose

Decision Scope is the closed set of exact subjects, action or effect kinds, time bounds, authority boundary, and exclusions to which one Decision may apply. Shared ownership, batch presentation, or similar subject labels do not expand the scope.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.scopes-authority-over` | `target` | `authority-claim` |

## Non-collapse boundaries

- `decision-scope` remains distinct from `decision`.
- `decision-scope` remains distinct from `authority-claim`.

## Orthogonality rules

- **DECISION-SCOPE-IDENTITY**: A Decision Scope instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **DECISION-SCOPE-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **DECISION-SCOPE-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **DECISION-SCOPE-NON-COLLAPSE**: Decision Scope remains distinct from decision, authority-claim.

## Typed residue

- `DECISION-SCOPE-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Decision Scope/v1 candidate. Consequence: The carrier remains candidate-only.
- `DECISION-SCOPE-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Decision Scope/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
