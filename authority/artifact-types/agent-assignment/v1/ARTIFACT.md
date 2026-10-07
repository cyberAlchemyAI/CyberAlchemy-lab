<!-- GENERATED FILE: canonical data is artifact.json. -->

# Agent Assignment Artifact Type v1

- Type: `cal.artifact-type.agent-assignment/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.agent-assignment@1.0.0-candidate.1`

## Distinct validation purpose

An Agent Assignment is a time-bounded owner-qualified binding of an Agent to an Intent, Goal, Project, Work item, Run, Role, or Responsibility. Assignment binds expected participation to exact subjects, scope, owner, period, deliverables or responsibilities, and stop conditions.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.addresses-intent` | `source` | `intent` |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.member-of` | `source` | `project` |
| `relation.successor-of` | `source` | `agent-assignment` |
| `relation.successor-of` | `target` | `agent-assignment` |

## Non-collapse boundaries

- `agent-assignment` remains distinct from `role-assignment`.
- `agent-assignment` remains distinct from `delegation`.

## Orthogonality rules

- **AGENT-ASSIGNMENT-IDENTITY**: A Agent Assignment instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **AGENT-ASSIGNMENT-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **AGENT-ASSIGNMENT-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **AGENT-ASSIGNMENT-NON-COLLAPSE**: Agent Assignment remains distinct from role-assignment, delegation.

## Typed residue

- `AGENT-ASSIGNMENT-R1` (role:artifact-type-owner): Owner admission for exact Agent Assignment/v1 bytes. Consequence: Carrier remains candidate-only.
- `AGENT-ASSIGNMENT-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Agent Assignment/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
