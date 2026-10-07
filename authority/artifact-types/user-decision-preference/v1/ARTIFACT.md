<!-- GENERATED FILE: canonical data is artifact.json. -->

# User Decision Preference Artifact Type v1

- Type: `cal.artifact-type.user-decision-preference/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.user-decision-preference@1.0.0-candidate.1`

## Distinct validation purpose

The user's saved choice for where a particular kind of workflow should ask them. It can move the question only among places the workflow already permits.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.governed-by` | `source` | `policy` |

## Non-collapse boundaries

- `user-decision-preference` remains distinct from `communication-preference`.
- `user-decision-preference` remains distinct from `decision`.

## Orthogonality rules

- **USER-DECISION-PREFERENCE-IDENTITY**: A User Decision Preference retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **USER-DECISION-PREFERENCE-RELATIONS**: Every global semantic connection requires one exact admitted Relation Kind and a separate Typed Relation identity; contract-local references remain closed schema fields.
- **USER-DECISION-PREFERENCE-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **USER-DECISION-PREFERENCE-NON-COLLAPSE**: User Decision Preference remains distinct from communication-preference, decision.

## Typed residue

- `USER-DECISION-PREFERENCE-R1` (role:artifact-type-owner): Owner admission for exact User Decision Preference/v1 bytes. Consequence: Carrier remains candidate-only.
- `USER-DECISION-PREFERENCE-R2` (role:migration-consumer-owner): Separate instance, Typed Relation, transaction application, and runtime decisions where applicable. Consequence: No operational state changes.

## Claim ceiling

This candidate User Decision Preference/v1 carrier binds the exact Definition and candidate relation surface. PASS admits nothing.
