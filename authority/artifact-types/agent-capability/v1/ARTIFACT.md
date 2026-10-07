<!-- GENERATED FILE: canonical data is artifact.json. -->

# Agent Capability Artifact Type v1

- Type: `cal.artifact-type.agent-capability/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.agent-capability@1.0.0-candidate.1`

## Distinct validation purpose

An Agent Capability is a bounded class of action or interpretation that an Agent may be technically able to attempt under exact input, output, evidence, and failure contracts. Agent Capability states a bounded class of attempt and must declare inputs, outputs, evidence, failure modes, and implementation bindings.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.affects` | `target` | `failure-occurrence, incident` |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.declares-effect-on` | `target` | `decision` |
| `relation.has-capability` | `target` | `agent-instance, agent-profile` |
| `relation.successor-of` | `source` | `agent-capability` |
| `relation.successor-of` | `target` | `agent-capability` |

## Non-collapse boundaries

- `agent-capability` remains distinct from `product-capability`.
- `agent-capability` remains distinct from `authority-claim`.

## Orthogonality rules

- **AGENT-CAPABILITY-IDENTITY**: A Agent Capability instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **AGENT-CAPABILITY-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **AGENT-CAPABILITY-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **AGENT-CAPABILITY-NON-COLLAPSE**: Agent Capability remains distinct from product-capability, authority-claim.

## Typed residue

- `AGENT-CAPABILITY-R1` (role:artifact-type-owner): Owner admission for exact Agent Capability/v1 bytes. Consequence: Carrier remains candidate-only.
- `AGENT-CAPABILITY-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Agent Capability/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
