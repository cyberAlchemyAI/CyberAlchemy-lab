<!-- GENERATED FILE: canonical data is artifact.json. -->

# Generated Output Artifact Type v1

- Type: `cal.artifact-type.generated-output/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.generated-output@1.0.0-candidate.1`

## Distinct validation purpose

A Generated Output is a reproducible product derived from exact canonical inputs by an exact governed generator version and bound to lineage and parity checks. It is not a second semantic authority and is canonical only when an explicit Artifact Type contract says so.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.derives-from` | `source` | `source` |

## Non-collapse boundaries

- `generated-output` remains distinct from `source`.
- `generated-output` remains distinct from `evidence-set`.

## Orthogonality rules

- **GENERATED-OUTPUT-IDENTITY**: A Generated Output instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **GENERATED-OUTPUT-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **GENERATED-OUTPUT-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **GENERATED-OUTPUT-NON-COLLAPSE**: Generated Output remains distinct from source, evidence-set.

## Typed residue

- `GENERATED-OUTPUT-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Generated Output/v1 candidate. Consequence: The carrier remains candidate-only.
- `GENERATED-OUTPUT-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Generated Output/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
