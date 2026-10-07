<!-- GENERATED FILE: canonical data is artifact.json. -->

# Agent Session Artifact Type v1

- Type: `cal.artifact-type.agent-session/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.agent-session@1.0.0-candidate.1`

## Distinct validation purpose

An Agent Session is a bounded execution context binding one Agent Instance to one Assignment, Context View, Ontology View, Policy set, authority envelope, inputs, budgets, cursor, Session Memory, and termination state. A Session binds exactly one concrete Agent Instance to exact Assignment, Context View, Ontology View, Policies, authority, inputs, budgets, cursor, and termination state.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.affects` | `target` | `failure-occurrence, incident` |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.consumes-view` | `source` | `context-view, ontology-view` |
| `relation.derives-from` | `target` | `agent-reflection` |
| `relation.governed-by` | `source` | `policy` |
| `relation.member-of` | `target` | `agent-action, agent-instance` |
| `relation.occurs-during` | `target` | `failure-occurrence` |
| `relation.successor-of` | `source` | `agent-session` |
| `relation.successor-of` | `target` | `agent-session` |
| `relation.uses-tool` | `source` | `implementation, tool` |

## Non-collapse boundaries

- `agent-session` remains distinct from `agent-instance`.
- `agent-session` remains distinct from `project-state`.

## Orthogonality rules

- **AGENT-SESSION-IDENTITY**: A Agent Session instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **AGENT-SESSION-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **AGENT-SESSION-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **AGENT-SESSION-NON-COLLAPSE**: Agent Session remains distinct from agent-instance, project-state.

## Typed residue

- `AGENT-SESSION-R1` (role:artifact-type-owner): Owner admission for exact Agent Session/v1 bytes. Consequence: Carrier remains candidate-only.
- `AGENT-SESSION-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Agent Session/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
