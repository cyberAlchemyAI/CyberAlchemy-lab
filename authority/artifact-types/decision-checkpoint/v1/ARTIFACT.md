<!-- GENERATED FILE: canonical data is artifact.json. -->

# Decision Checkpoint Artifact Type v1

- Type: `cal.artifact-type.decision-checkpoint/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.decision-checkpoint@1.0.0-candidate.1`

## Distinct validation purpose

The one place in a workflow where the person is asked to decide. Calling it a checkpoint avoids confusing where the question appears with what the person is allowed to authorize.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.governed-by` | `source` | `policy` |

## Non-collapse boundaries

- `decision-checkpoint` remains distinct from `decision-bundle`.
- `decision-checkpoint` remains distinct from `workflow-decision-profile`.

## Orthogonality rules

- **DECISION-CHECKPOINT-IDENTITY**: A Decision Checkpoint retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **DECISION-CHECKPOINT-RELATIONS**: Every global semantic connection requires one exact admitted Relation Kind and a separate Typed Relation identity; contract-local references remain closed schema fields.
- **DECISION-CHECKPOINT-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **DECISION-CHECKPOINT-NON-COLLAPSE**: Decision Checkpoint remains distinct from decision-bundle, workflow-decision-profile.

## Typed residue

- `DECISION-CHECKPOINT-R1` (role:artifact-type-owner): Owner admission for exact Decision Checkpoint/v1 bytes. Consequence: Carrier remains candidate-only.
- `DECISION-CHECKPOINT-R2` (role:migration-consumer-owner): Separate instance, Typed Relation, transaction application, and runtime decisions where applicable. Consequence: No operational state changes.

## Claim ceiling

This candidate Decision Checkpoint/v1 carrier binds the exact Definition and candidate relation surface. PASS admits nothing.
