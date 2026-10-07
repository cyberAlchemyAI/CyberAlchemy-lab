<!-- GENERATED FILE: canonical data is artifact.json. -->

# Decision Scope Artifact Type v1

- Type: `cal.artifact-type.decision-scope/v2`
- Version: `2.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.decision-scope@1.0.0-candidate.1`

## Distinct validation purpose

Decision Scope is the closed set of exact subjects, action or effect kinds, time bounds, authority boundary, and exclusions to which one Decision may apply. Shared ownership, batch presentation, or similar subject labels do not expand the scope.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.scopes-authority-over` | `target` | `authority-boundary, authority-claim` |
| `relation.successor-of` | `source` | `decision-scope` |
| `relation.successor-of` | `target` | `decision-scope` |

## Non-collapse boundaries

- `decision-scope` remains distinct from `decision`.
- `decision-scope` remains distinct from `authority-claim`.

## Orthogonality rules

- **DECISION-SCOPE-IDENTITY**: A Decision Scope instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **DECISION-SCOPE-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **DECISION-SCOPE-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **DECISION-SCOPE-NON-COLLAPSE**: Decision Scope remains distinct from decision, authority-claim.

## Typed residue

- `DECISION-SCOPE-V2-R1` (role:artifact-type-owner): Owner admission for this exact endpoint-role successor. Consequence: The admitted v1 carrier remains current.

## Claim ceiling

This candidate Decision Scope/v2 successor widens only the exact closed relation-role surface required by the governance transaction extension. It admits nothing.
