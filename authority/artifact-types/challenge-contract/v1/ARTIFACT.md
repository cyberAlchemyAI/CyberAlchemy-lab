<!-- GENERATED FILE: canonical data is artifact.json. -->

# Challenge Contract Artifact Type v1

- Type: `cal.artifact-type.challenge-contract/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.challenge-contract@1.0.0-candidate.1`

## Distinct validation purpose

A Challenge Contract is a closed versioned Policy-bound mechanism defining challengeable subjects, eligible challengers, grounds, evidence, response modes, owner route, resolution gate, timing, and unresolved residue handling. A route string alone is not a Challenge Contract, and filing a challenge does not automatically suspend or reverse the subject.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.governed-by` | `source` | `policy` |
| `relation.governed-by` | `target` | `challenge-event` |
| `relation.successor-of` | `source` | `challenge-contract` |
| `relation.successor-of` | `target` | `challenge-contract` |
| `relation.violates` | `target` | `failure-occurrence` |

## Non-collapse boundaries

- `challenge-contract` remains distinct from `policy`.
- `challenge-contract` remains distinct from `challenge-event`.

## Orthogonality rules

- **CHALLENGE-CONTRACT-IDENTITY**: A Challenge Contract instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **CHALLENGE-CONTRACT-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **CHALLENGE-CONTRACT-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **CHALLENGE-CONTRACT-NON-COLLAPSE**: Challenge Contract remains distinct from policy, challenge-event.

## Typed residue

- `CHALLENGE-CONTRACT-R1` (role:artifact-type-owner): Owner admission for exact Challenge Contract/v1 bytes. Consequence: Carrier remains candidate-only.
- `CHALLENGE-CONTRACT-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Challenge Contract/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
