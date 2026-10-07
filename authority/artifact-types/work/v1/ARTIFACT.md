<!-- GENERATED FILE: canonical data is artifact.json. -->

# Work Artifact Type v1

- Type: `cal.artifact-type.work/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.work@1.0.0-candidate.1`

## Distinct validation purpose

Work is a bounded unit of coordinated effort with a declared purpose, owner, participants, inputs, expected result, constraints, lifecycle, and outcome trace. Work is not necessarily a Project and does not imply authority, completion, successful outcome, or Product value.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.member-of` | `source` | `project` |

## Non-collapse boundaries

- `work` remains distinct from `project`.
- `work` remains distinct from `goal`.

## Orthogonality rules

- **WORK-IDENTITY**: A Work instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **WORK-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **WORK-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **WORK-NON-COLLAPSE**: Work remains distinct from project, goal.

## Typed residue

- `WORK-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Work/v1 candidate. Consequence: The carrier remains candidate-only.
- `WORK-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Work/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
