<!-- GENERATED FILE: canonical data is artifact.json. -->

# Drift Assessment Artifact Type v1

- Type: `cal.artifact-type.drift-assessment/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.drift-assessment@1.0.0-candidate.1`

## Distinct validation purpose

A Drift Assessment is an evidence-bounded comparison between declared and observed versions, conditions, bindings, meanings, behavior, or currentness at an exact time. Mismatch does not by itself establish cause, severity, failure, correction authority, or required remediation.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.derives-from` | `target` | `improvement-signal` |
| `relation.evidence-bears-on` | `target` | `evidence-set, feedback-record, finding, measurement-result, observation, operational-observation` |
| `relation.originates-from` | `source` | `source` |
| `relation.produces` | `target` | `agent-action` |
| `relation.successor-of` | `source` | `drift-assessment` |
| `relation.successor-of` | `target` | `drift-assessment` |

## Non-collapse boundaries

- `drift-assessment` remains distinct from `failure-assessment`.
- `drift-assessment` remains distinct from `finding`.

## Orthogonality rules

- **DRIFT-ASSESSMENT-IDENTITY**: A Drift Assessment instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **DRIFT-ASSESSMENT-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **DRIFT-ASSESSMENT-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **DRIFT-ASSESSMENT-NON-COLLAPSE**: Drift Assessment remains distinct from failure-assessment, finding.

## Typed residue

- `DRIFT-ASSESSMENT-R1` (role:artifact-type-owner): Owner admission for exact Drift Assessment/v1 bytes. Consequence: Carrier remains candidate-only.
- `DRIFT-ASSESSMENT-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Drift Assessment/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
