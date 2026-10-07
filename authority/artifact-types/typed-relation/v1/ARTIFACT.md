<!-- GENERATED FILE: canonical data is artifact.json. -->

# Typed Relation Artifact Type v1

- Type: `cal.artifact-type.typed-relation/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.typed-relation@1.0.0-candidate.1`

## Distinct validation purpose

A Typed Relation is one independently identified global connection between exact source and target instances under one admitted Relation Kind version, exact allowed pair, qualifiers, owner, evidence, lifecycle, and contestability contract. It neither merges endpoint identities nor becomes valid from schema fields, shared paths, Ontology projection, or candidate validation.

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

- `TYPED-RELATION-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Typed Relation/v1 candidate. Consequence: The carrier remains candidate-only.
- `TYPED-RELATION-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Typed Relation/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
