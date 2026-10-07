<!-- GENERATED FILE: canonical data is artifact.json. -->

# Ontology Node Artifact Type v1

- Type: `cal.artifact-type.ontology-node/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.ontology-node@1.0.0-candidate.1`

## Distinct validation purpose

An Ontology Node is an independently identified governed representation of one exact subject revision within one Ontology, with provenance, confidence, lifecycle, branch, and contestability state. It is not the represented subject, its identity carrier, its Definition, or proof that its claims are globally true.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.member-of` | `source` | `ontology` |

## Non-collapse boundaries

- `ontology-node` remains distinct from `ontology`.
- `ontology-node` remains distinct from `typed-relation`.

## Orthogonality rules

- **ONTOLOGY-NODE-IDENTITY**: A Ontology Node instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **ONTOLOGY-NODE-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **ONTOLOGY-NODE-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **ONTOLOGY-NODE-NON-COLLAPSE**: Ontology Node remains distinct from ontology, typed-relation.

## Typed residue

- `ONTOLOGY-NODE-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Ontology Node/v1 candidate. Consequence: The carrier remains candidate-only.
- `ONTOLOGY-NODE-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Ontology Node/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
