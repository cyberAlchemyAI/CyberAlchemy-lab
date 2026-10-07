<!-- GENERATED FILE: canonical data is artifact.json. -->

# Implementation Artifact Type v1

- Type: `cal.artifact-type.implementation/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.implementation@1.0.0-candidate.1`

## Distinct validation purpose

An Implementation is a governed technical realization with stable identity, version, owner, lifecycle, source binding, build or deployment posture, interfaces, and evidence bindings. It is distinct from Product, Product Capability, Agent, model, Tool, runtime instance, and proof of conformance or value.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.binds-implementation` | `source` | `ontology, schema` |
| `relation.instance-of` | `source` | `governed-model, product-capability` |
| `relation.realizes` | `source` | `product-capability` |

## Non-collapse boundaries

- `implementation` remains distinct from `capability-realization-binding`.
- `implementation` remains distinct from `schema`.

## Orthogonality rules

- **IMPLEMENTATION-IDENTITY**: A Implementation instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **IMPLEMENTATION-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **IMPLEMENTATION-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **IMPLEMENTATION-NON-COLLAPSE**: Implementation remains distinct from capability-realization-binding, schema.

## Typed residue

- `IMPLEMENTATION-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Implementation/v1 candidate. Consequence: The carrier remains candidate-only.
- `IMPLEMENTATION-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Implementation/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
