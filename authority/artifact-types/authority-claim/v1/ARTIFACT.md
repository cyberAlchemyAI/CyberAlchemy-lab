<!-- GENERATED FILE: canonical data is artifact.json. -->

# Authority Claim Artifact Type v1

- Type: `cal.artifact-type.authority-claim/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.authority-claim@1.0.0-candidate.1`

## Distinct validation purpose

It is a precise statement that someone has a particular right in a particular scope; making the statement does not prove it is valid.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.evidence-bears-on` | `target` | `evidence-set, measurement-result, observation` |
| `relation.scopes-authority-over` | `source` | `decision-scope, role-assignment` |

## Non-collapse boundaries

- `authority-claim` remains distinct from `identity-claim`.
- `authority-claim` remains distinct from `role-assignment`.

## Orthogonality rules

- **AUTHORITY-CLAIM-IDENTITY**: A Authority Claim instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **AUTHORITY-CLAIM-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **AUTHORITY-CLAIM-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **AUTHORITY-CLAIM-NON-COLLAPSE**: Authority Claim remains distinct from identity-claim, role-assignment.

## Typed residue

- `AUTHORITY-CLAIM-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Authority Claim/v1 candidate. Consequence: The carrier remains candidate-only.
- `AUTHORITY-CLAIM-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Authority Claim/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
