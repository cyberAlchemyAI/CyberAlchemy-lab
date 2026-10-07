<!-- GENERATED FILE: canonical data is artifact.json. -->

# Relation Kind Artifact Type v1

- Type: `cal.artifact-type.relation-kind/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.relation-kind@1.0.0-candidate.1`

## Distinct validation purpose

A Relation Kind is a versioned semantic-axis contract asking one unique directional question through a finite closed set of exact ordered endpoint-kind pairs and pair-specific qualifier rules. It is neither a relation instance, specialized binding, Ontology edge, wildcard endpoint family, nor inferred Cartesian product.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.declares-effect-on` | `target` | `decision` |
| `relation.governed-by` | `source` | `constitution` |
| `relation.originates-from` | `source` | `source` |
| `relation.successor-of` | `source` | `relation-kind` |
| `relation.successor-of` | `target` | `relation-kind` |

## Non-collapse boundaries

- `relation-kind` remains distinct from `typed-relation`.
- `relation-kind` remains distinct from `schema`.

## Orthogonality rules

- **RELATION-KIND-IDENTITY**: A Relation Kind instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **RELATION-KIND-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **RELATION-KIND-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **RELATION-KIND-NON-COLLAPSE**: Relation Kind remains distinct from typed-relation, schema.

## Typed residue

- `RELATION-KIND-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Relation Kind/v1 candidate. Consequence: The carrier remains candidate-only.
- `RELATION-KIND-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Relation Kind/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
