<!-- GENERATED FILE: canonical data is artifact.json. -->

# Agent Instance Artifact Type v1

- Type: `cal.artifact-type.agent-instance/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.agent-instance@1.0.0-candidate.1`

## Distinct validation purpose

An Agent Instance is one time-bounded concrete realization of Agent, bound to a Profile, Implementation, capability set, accountable Principal, owner route, and lifecycle. Agent Instance is the concrete time-bounded operational identity; it is not its Person, Principal, Profile, model, Implementation, Session, or authority grant.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.acts-for` | `source` | `principal` |
| `relation.assigned-to` | `source` | `responsibility, role` |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.governed-by` | `source` | `policy` |
| `relation.has-capability` | `source` | `agent-capability` |
| `relation.instance-of` | `source` | `classification-value` |
| `relation.member-of` | `source` | `agent-session` |
| `relation.performs` | `source` | `agent-action, experiment-run, research-run, review, work` |
| `relation.profiled-by` | `source` | `agent-profile` |
| `relation.successor-of` | `source` | `agent-instance` |
| `relation.successor-of` | `target` | `agent-instance` |

## Non-collapse boundaries

- `agent-instance` remains distinct from `agent-profile`.
- `agent-instance` remains distinct from `agent-session`.

## Orthogonality rules

- **AGENT-INSTANCE-IDENTITY**: A Agent Instance instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **AGENT-INSTANCE-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **AGENT-INSTANCE-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **AGENT-INSTANCE-NON-COLLAPSE**: Agent Instance remains distinct from agent-profile, agent-session.

## Typed residue

- `AGENT-INSTANCE-R1` (role:artifact-type-owner): Owner admission for exact Agent Instance/v1 bytes. Consequence: Carrier remains candidate-only.
- `AGENT-INSTANCE-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Agent Instance/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
