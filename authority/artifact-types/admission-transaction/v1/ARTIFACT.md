<!-- GENERATED FILE: canonical data is artifact.json. -->

# Admission Transaction Artifact Type v1

- Type: `cal.artifact-type.admission-transaction/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.admission-transaction@1.0.0-candidate.1`

## Distinct validation purpose

The one atomic operation that turns an already approved bundle into admitted repository state. It checks exactly what was approved, applies all of it together, records the resulting events and state, and adds no new approval of its own.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.governed-by` | `source` | `policy` |
| `relation.materializes-consequence` | `source` | `generated-output, project-governance-event-history, project-semantic-event-history, project-state` |

## Non-collapse boundaries

- `admission-transaction` remains distinct from `decision`.
- `admission-transaction` remains distinct from `agent-action`.
- `admission-transaction` remains distinct from `project-state`.

## Orthogonality rules

- **ADMISSION-TRANSACTION-IDENTITY**: A Admission Transaction retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **ADMISSION-TRANSACTION-RELATIONS**: Every global semantic connection requires one exact admitted Relation Kind and a separate Typed Relation identity; contract-local references remain closed schema fields.
- **ADMISSION-TRANSACTION-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **ADMISSION-TRANSACTION-NON-COLLAPSE**: Admission Transaction remains distinct from decision, agent-action, project-state.

## Typed residue

- `ADMISSION-TRANSACTION-R1` (role:artifact-type-owner): Owner admission for exact Admission Transaction/v1 bytes. Consequence: Carrier remains candidate-only.
- `ADMISSION-TRANSACTION-R2` (role:migration-consumer-owner): Separate instance, Typed Relation, transaction application, and runtime decisions where applicable. Consequence: No operational state changes.

## Claim ceiling

This candidate Admission Transaction/v1 carrier binds the exact Definition and candidate relation surface. PASS admits nothing.
