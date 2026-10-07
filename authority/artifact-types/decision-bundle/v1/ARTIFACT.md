<!-- GENERATED FILE: canonical data is artifact.json. -->

# Decision Bundle Artifact Type v1

- Type: `cal.artifact-type.decision-bundle/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.decision-bundle@1.0.0-candidate.1`

## Distinct validation purpose

Several exact decisions shown together once. The person sees one interaction, but each decision keeps its own owner, target, and consequence.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.governed-by` | `source` | `policy` |
| `relation.member-of` | `target` | `decision` |

## Non-collapse boundaries

- `decision-bundle` remains distinct from `decision`.
- `decision-bundle` remains distinct from `decision-checkpoint`.

## Orthogonality rules

- **DECISION-BUNDLE-IDENTITY**: A Decision Bundle retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **DECISION-BUNDLE-RELATIONS**: Every global semantic connection requires one exact admitted Relation Kind and a separate Typed Relation identity; contract-local references remain closed schema fields.
- **DECISION-BUNDLE-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **DECISION-BUNDLE-NON-COLLAPSE**: Decision Bundle remains distinct from decision, decision-checkpoint.

## Typed residue

- `DECISION-BUNDLE-R1` (role:artifact-type-owner): Owner admission for exact Decision Bundle/v1 bytes. Consequence: Carrier remains candidate-only.
- `DECISION-BUNDLE-R2` (role:migration-consumer-owner): Separate instance, Typed Relation, transaction application, and runtime decisions where applicable. Consequence: No operational state changes.

## Claim ceiling

This candidate Decision Bundle/v1 carrier binds the exact Definition and candidate relation surface. PASS admits nothing.
