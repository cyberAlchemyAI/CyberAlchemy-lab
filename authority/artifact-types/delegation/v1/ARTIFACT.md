<!-- GENERATED FILE: canonical data is artifact.json. -->

# Delegation Artifact Type v1

- Type: `cal.artifact-type.delegation/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.delegation@1.0.0-candidate.1`

## Distinct validation purpose

A Delegation is an explicit scope-bounded and time-bounded authorization from a Principal or authority owner to an Agent or Agent Instance for named action kinds under exact Policies, gates, evidence, revocation, and claim ceilings. The delegator must possess delegable authority for every included action kind, subject, scope, and time interval.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.declares-effect-on` | `target` | `decision` |
| `relation.successor-of` | `source` | `delegation` |
| `relation.successor-of` | `target` | `delegation` |

## Non-collapse boundaries

- `delegation` remains distinct from `authority-claim`.
- `delegation` remains distinct from `role-assignment`.

## Orthogonality rules

- **DELEGATION-IDENTITY**: A Delegation instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **DELEGATION-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **DELEGATION-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **DELEGATION-NON-COLLAPSE**: Delegation remains distinct from authority-claim, role-assignment.

## Typed residue

- `DELEGATION-R1` (role:artifact-type-owner): Owner admission for exact Delegation/v1 bytes. Consequence: Carrier remains candidate-only.
- `DELEGATION-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Delegation/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
