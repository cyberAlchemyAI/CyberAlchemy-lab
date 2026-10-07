<!-- GENERATED FILE: canonical data is artifact.json. -->

# Contract Artifact Type v1

- Type: `cal.artifact-type.contract/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.contract@1.0.0-candidate.1`

## Distinct validation purpose

A Contract is a versioned governed statement of obligations, permissions, prohibitions, interfaces, boundaries, evidence requirements, parties or subjects, and breach handling. A Contract is neither its implementation, compliance evidence, Policy issuer, nor proof that obligations were satisfied.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.conforms-to` | `target` | `capability-instance` |
| `relation.inherits-contract` | `target` | `capability-instance` |
| `relation.successor-of` | `source` | `contract` |
| `relation.successor-of` | `target` | `contract` |

## Non-collapse boundaries

- `contract` remains distinct from `challenge-contract`.
- `contract` remains distinct from `policy`.

## Orthogonality rules

- **CONTRACT-IDENTITY**: A Contract instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **CONTRACT-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **CONTRACT-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **CONTRACT-NON-COLLAPSE**: Contract remains distinct from challenge-contract, policy.

## Typed residue

- `CONTRACT-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Contract/v1 candidate. Consequence: The carrier remains candidate-only.
- `CONTRACT-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Contract/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
