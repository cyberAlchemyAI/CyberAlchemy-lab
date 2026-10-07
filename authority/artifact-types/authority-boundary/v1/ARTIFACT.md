<!-- GENERATED FILE: canonical data is artifact.json. -->

# Authority Boundary Artifact Type v1

- Type: `cal.artifact-type.authority-boundary/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.authority-boundary@1.0.0-candidate.1`

## Distinct validation purpose

The exact limit around what a particular owner is allowed to decide. It says who can decide what; it does not say when a workflow asks them.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.governed-by` | `source` | `policy` |
| `relation.scopes-authority-over` | `source` | `decision-scope` |

## Non-collapse boundaries

- `authority-boundary` remains distinct from `authority-claim`.
- `authority-boundary` remains distinct from `decision-scope`.

## Orthogonality rules

- **AUTHORITY-BOUNDARY-IDENTITY**: A Authority Boundary retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **AUTHORITY-BOUNDARY-RELATIONS**: Every global semantic connection requires one exact admitted Relation Kind and a separate Typed Relation identity; contract-local references remain closed schema fields.
- **AUTHORITY-BOUNDARY-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **AUTHORITY-BOUNDARY-NON-COLLAPSE**: Authority Boundary remains distinct from authority-claim, decision-scope.

## Typed residue

- `AUTHORITY-BOUNDARY-R1` (role:artifact-type-owner): Owner admission for exact Authority Boundary/v1 bytes. Consequence: Carrier remains candidate-only.
- `AUTHORITY-BOUNDARY-R2` (role:migration-consumer-owner): Separate instance, Typed Relation, transaction application, and runtime decisions where applicable. Consequence: No operational state changes.

## Claim ceiling

This candidate Authority Boundary/v1 carrier binds the exact Definition and candidate relation surface. PASS admits nothing.
