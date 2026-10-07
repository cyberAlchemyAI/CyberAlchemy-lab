<!-- GENERATED FILE: canonical data is artifact.json. -->

# Preference Application Assessment Artifact Type v1

- Type: `cal.artifact-type.preference-application-assessment/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.preference-application-assessment@1.0.0-candidate.1`

## Distinct validation purpose

A Preference Application Assessment is a request-bound determination of whether one exact Communication Preference revision applies, conflicts, is overridden, or is infeasible for one output. It neither rewrites the preference nor proves user satisfaction or authorization.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.evaluates` | `source` | `communication-preference` |
| `relation.evidence-bears-on` | `target` | `evidence-set, feedback-record, finding, measurement-result, observation, operational-observation` |
| `relation.successor-of` | `source` | `preference-application-assessment` |
| `relation.successor-of` | `target` | `preference-application-assessment` |

## Non-collapse boundaries

- `preference-application-assessment` remains distinct from `communication-preference`.
- `preference-application-assessment` remains distinct from `decision`.

## Orthogonality rules

- **PREFERENCE-APPLICATION-ASSESSMENT-IDENTITY**: A Preference Application Assessment instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **PREFERENCE-APPLICATION-ASSESSMENT-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **PREFERENCE-APPLICATION-ASSESSMENT-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **PREFERENCE-APPLICATION-ASSESSMENT-NON-COLLAPSE**: Preference Application Assessment remains distinct from communication-preference, decision.

## Typed residue

- `PREFERENCE-APPLICATION-ASSESSMENT-R1` (role:artifact-type-owner): Owner admission for exact Preference Application Assessment/v1 bytes. Consequence: Carrier remains candidate-only.
- `PREFERENCE-APPLICATION-ASSESSMENT-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Preference Application Assessment/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
