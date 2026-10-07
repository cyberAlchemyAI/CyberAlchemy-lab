<!-- GENERATED FILE: canonical data is artifact.json. -->

# Decision Artifact Type v1

- Type: `cal.artifact-type.decision/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.decision@1.0.0-candidate.1`

## Distinct validation purpose

A Decision is an attributable authority act that selects an outcome, interpretation, permission, priority, or lifecycle effect for exact subjects within a declared scope and evidence basis. A Decision is distinct from evidence, recommendation, preference, Agent output, execution, and proof that the selected effect occurred.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.declares-effect-on` | `source` | `artifact-type, capability-realization-binding, definition, effect, governed-model, product-capability, relation-kind` |

## Non-collapse boundaries

- `decision` remains distinct from `decision-checkpoint`.
- `decision` remains distinct from `effect`.

## Orthogonality rules

- **DECISION-IDENTITY**: A Decision instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **DECISION-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **DECISION-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **DECISION-NON-COLLAPSE**: Decision remains distinct from decision-checkpoint, effect.

## Typed residue

- `DECISION-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Decision/v1 candidate. Consequence: The carrier remains candidate-only.
- `DECISION-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Decision/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
