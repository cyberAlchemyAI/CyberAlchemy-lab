<!-- GENERATED FILE: canonical data is artifact.json. -->

# Source Artifact Type v1

- Type: `cal.artifact-type.source/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.source@1.0.0-candidate.1`

## Distinct validation purpose

A Source is an exact provenance-bearing origin from which content, evidence, data, or a claim was obtained, identified by a resolvable reference and integrity boundary. Being a Source does not make content true, current, complete, authoritative, admissible, or licensed for every use.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.derives-from` | `target` | `generated-output` |
| `relation.originates-from` | `target` | `artifact-type, definition, finding, relation-kind` |

## Non-collapse boundaries

- `source` remains distinct from `evidence-set`.
- `source` remains distinct from `generated-output`.

## Orthogonality rules

- **SOURCE-IDENTITY**: A Source instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **SOURCE-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **SOURCE-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **SOURCE-NON-COLLAPSE**: Source remains distinct from evidence-set, generated-output.

## Typed residue

- `SOURCE-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Source/v1 candidate. Consequence: The carrier remains candidate-only.
- `SOURCE-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Source/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
