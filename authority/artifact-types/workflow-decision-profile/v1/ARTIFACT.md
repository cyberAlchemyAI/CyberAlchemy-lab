<!-- GENERATED FILE: canonical data is artifact.json. -->

# Workflow Decision Profile Artifact Type v1

- Type: `cal.artifact-type.workflow-decision-profile/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.workflow-decision-profile@1.0.0-candidate.1`

## Distinct validation purpose

The workflow type's rules for whether it asks a person, where it is allowed to ask, and what must already exist when it asks.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.governed-by` | `source` | `policy` |

## Non-collapse boundaries

- `workflow-decision-profile` remains distinct from `policy`.
- `workflow-decision-profile` remains distinct from `user-decision-preference`.

## Orthogonality rules

- **WORKFLOW-DECISION-PROFILE-IDENTITY**: A Workflow Decision Profile retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **WORKFLOW-DECISION-PROFILE-RELATIONS**: Every global semantic connection requires one exact admitted Relation Kind and a separate Typed Relation identity; contract-local references remain closed schema fields.
- **WORKFLOW-DECISION-PROFILE-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **WORKFLOW-DECISION-PROFILE-NON-COLLAPSE**: Workflow Decision Profile remains distinct from policy, user-decision-preference.

## Typed residue

- `WORKFLOW-DECISION-PROFILE-R1` (role:artifact-type-owner): Owner admission for exact Workflow Decision Profile/v1 bytes. Consequence: Carrier remains candidate-only.
- `WORKFLOW-DECISION-PROFILE-R2` (role:migration-consumer-owner): Separate instance, Typed Relation, transaction application, and runtime decisions where applicable. Consequence: No operational state changes.

## Claim ceiling

This candidate Workflow Decision Profile/v1 carrier binds the exact Definition and candidate relation surface. PASS admits nothing.
