<!-- GENERATED FILE: canonical data is artifact.json. -->

# Typed Relation Artifact Type v1

- Type: `cal.artifact-type.typed-relation/v3`
- Version: `3.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.typed-relation@1.0.0-candidate.1`

## Distinct validation purpose

Typed Relation/v2 records one independently identified global connection whose Relation Kind fixes the exact ordered endpoint pair and closed qualifier object.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.member-of` | `source` | `ontology` |

## Non-collapse boundaries

- `typed-relation` remains distinct from `relation-kind`.
- `typed-relation` remains distinct from `ontology-node`.

## Orthogonality rules

- **TYPED-RELATION-IDENTITY**: A Typed Relation instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **TYPED-RELATION-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **TYPED-RELATION-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **TYPED-RELATION-NON-COLLAPSE**: Typed Relation remains distinct from relation-kind, ontology-node.

## Typed residue

- `TYPED-RELATION-V3-R1` (role:artifact-type-owner): Owner admission for this exact representation-closure successor. Consequence: Typed Relation/v2 remains current until the atomic transaction is applied.

## Claim ceiling

This candidate Typed Relation/v3 successor adds only the closed representation of the already reviewed materializes-consequence axis. It creates no new semantic relation, instance, authority, admission, inference, runtime, or external effect.
