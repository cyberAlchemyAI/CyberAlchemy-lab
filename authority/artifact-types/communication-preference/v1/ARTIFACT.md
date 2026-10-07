<!-- GENERATED FILE: canonical data is artifact.json. -->

# Communication Preference Artifact Type v1

- Type: `cal.artifact-type.communication-preference/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.communication-preference@1.0.0-candidate.1`

## Distinct validation purpose

A Communication Preference is a scoped expression preference for presentation, language, detail, ordering, or interaction style, with source, audience, target, conditions, strength, expiry, and override rules. It is distinct from current instruction, User Decision Preference, Policy, Operational Lesson, and authority.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.declares-effect-on` | `target` | `decision` |
| `relation.evaluates` | `target` | `preference-application-assessment` |
| `relation.governed-by` | `source` | `policy` |
| `relation.successor-of` | `source` | `communication-preference` |
| `relation.successor-of` | `target` | `communication-preference` |

## Non-collapse boundaries

- `communication-preference` remains distinct from `policy`.
- `communication-preference` remains distinct from `operational-lesson`.

## Orthogonality rules

- **COMMUNICATION-PREFERENCE-IDENTITY**: A Communication Preference instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **COMMUNICATION-PREFERENCE-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **COMMUNICATION-PREFERENCE-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **COMMUNICATION-PREFERENCE-NON-COLLAPSE**: Communication Preference remains distinct from policy, operational-lesson.

## Typed residue

- `COMMUNICATION-PREFERENCE-R1` (role:artifact-type-owner): Owner admission for exact Communication Preference/v1 bytes. Consequence: Carrier remains candidate-only.
- `COMMUNICATION-PREFERENCE-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Communication Preference/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
