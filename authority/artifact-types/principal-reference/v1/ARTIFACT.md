<!-- GENERATED FILE: canonical data is artifact.json. -->

# Principal Reference Artifact Type v1

- Type: `cal.artifact-type.principal-reference/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.principal-reference@1.0.0-candidate.1`

## Distinct validation purpose

A Principal Reference is a minimal governed reference to one Principal used by artifacts that need accountability or authorization linkage without copying the Principal’s identity record. A Principal Reference contains only the minimum stable identifier, kind, issuer or registry, resolution route, and integrity data needed by the consumer.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.asserts-identity-of` | `source` | `principal` |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.successor-of` | `source` | `principal-reference` |
| `relation.successor-of` | `target` | `principal-reference` |

## Non-collapse boundaries

- `principal-reference` remains distinct from `person-reference`.
- `principal-reference` remains distinct from `principal`.

## Orthogonality rules

- **PRINCIPAL-REFERENCE-IDENTITY**: A Principal Reference instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **PRINCIPAL-REFERENCE-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **PRINCIPAL-REFERENCE-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **PRINCIPAL-REFERENCE-NON-COLLAPSE**: Principal Reference remains distinct from person-reference, principal.

## Typed residue

- `PRINCIPAL-REFERENCE-R1` (role:artifact-type-owner): Owner admission for exact Principal Reference/v1 bytes. Consequence: Carrier remains candidate-only.
- `PRINCIPAL-REFERENCE-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Principal Reference/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
