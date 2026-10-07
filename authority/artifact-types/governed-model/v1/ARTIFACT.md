<!-- GENERATED FILE: canonical data is artifact.json. -->

# Governed Model Artifact Type v1

- Type: `cal.artifact-type.governed-model/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.governed-model@1.0.0-candidate.1`

## Distinct validation purpose

A Governed Model is a versioned explicit representation of concepts, rules, structures, or behavior with scope, owner, sources, assumptions, validation, lifecycle, and challenge route. It is not automatically an Ontology, runtime, Implementation, truth claim, decision, or admitted authority.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.conforms-to` | `target` | `capability-instance` |
| `relation.declares-effect-on` | `target` | `decision` |
| `relation.instance-of` | `target` | `capability-instance, implementation` |
| `relation.successor-of` | `source` | `governed-model` |
| `relation.successor-of` | `target` | `governed-model` |

## Non-collapse boundaries

- `governed-model` remains distinct from `ontology`.
- `governed-model` remains distinct from `schema`.

## Orthogonality rules

- **GOVERNED-MODEL-IDENTITY**: A Governed Model instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **GOVERNED-MODEL-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **GOVERNED-MODEL-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **GOVERNED-MODEL-NON-COLLAPSE**: Governed Model remains distinct from ontology, schema.

## Typed residue

- `GOVERNED-MODEL-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Governed Model/v1 candidate. Consequence: The carrier remains candidate-only.
- `GOVERNED-MODEL-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Governed Model/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
