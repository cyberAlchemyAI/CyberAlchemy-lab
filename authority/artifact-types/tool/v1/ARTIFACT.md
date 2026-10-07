<!-- GENERATED FILE: canonical data is artifact.json. -->

# Tool Artifact Type v1

- Type: `cal.artifact-type.tool/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.tool@1.0.0-candidate.1`

## Distinct validation purpose

A Tool is a governed invocable resource used by an Agent Action through a declared interface, version, input/output contract, failure boundary, and evidence route. Tool availability grants neither Agent Capability nor authority and does not prove correct invocation or effect.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.successor-of` | `source` | `tool` |
| `relation.successor-of` | `target` | `tool` |
| `relation.uses-tool` | `target` | `agent-action, agent-session` |

## Non-collapse boundaries

- `tool` remains distinct from `implementation`.
- `tool` remains distinct from `agent-capability`.

## Orthogonality rules

- **TOOL-IDENTITY**: A Tool instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **TOOL-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **TOOL-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **TOOL-NON-COLLAPSE**: Tool remains distinct from implementation, agent-capability.

## Typed residue

- `TOOL-R1` (role:artifact-type-owner): Owner admission for exact Tool/v1 bytes. Consequence: Carrier remains candidate-only.
- `TOOL-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Tool/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
