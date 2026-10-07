<!-- GENERATED FILE: canonical data is artifact.json. -->

# Agent Profile Artifact Type v1

- Type: `cal.artifact-type.agent-profile/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.agent-profile@1.0.0-candidate.1`

## Distinct validation purpose

An Agent Profile is a reusable versioned contract for allowed inputs, outputs, behavior, Policies, Context, tool classes, evidence, escalation, and stop conditions. An Agent Profile is durable reusable Project State and is never the active Agent, Instance, Session, model, or Implementation.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.declares-effect-on` | `target` | `decision` |
| `relation.governed-by` | `source` | `policy` |
| `relation.has-capability` | `source` | `agent-capability` |
| `relation.profiled-by` | `target` | `agent-instance` |
| `relation.successor-of` | `source` | `agent-profile` |
| `relation.successor-of` | `target` | `agent-profile` |

## Non-collapse boundaries

- `agent-profile` remains distinct from `agent-instance`.
- `agent-profile` remains distinct from `policy`.

## Orthogonality rules

- **AGENT-PROFILE-IDENTITY**: A Agent Profile instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **AGENT-PROFILE-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **AGENT-PROFILE-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **AGENT-PROFILE-NON-COLLAPSE**: Agent Profile remains distinct from agent-instance, policy.

## Typed residue

- `AGENT-PROFILE-R1` (role:artifact-type-owner): Owner admission for exact Agent Profile/v1 bytes. Consequence: Carrier remains candidate-only.
- `AGENT-PROFILE-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Agent Profile/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
