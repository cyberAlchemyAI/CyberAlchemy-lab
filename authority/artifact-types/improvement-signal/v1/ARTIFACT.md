<!-- GENERATED FILE: canonical data is artifact.json. -->

# Improvement Signal Artifact Type v1

- Type: `cal.artifact-type.improvement-signal/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.improvement-signal@1.0.0-candidate.1`

## Distinct validation purpose

An Improvement Signal is a provenance-bound indication of a possible recurring weakness or opportunity that can be deduplicated, assessed, and routed. It asserts neither cause, recurrence, expected benefit, priority, permission, nor an Improvement Target.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.derives-from` | `source` | `drift-assessment, failure-assessment, operational-observation, work-outcome-assessment` |
| `relation.derives-from` | `target` | `improvement-target` |
| `relation.evidence-bears-on` | `target` | `evidence-set, feedback-record, finding, measurement-result, observation, operational-observation` |
| `relation.produces` | `target` | `agent-action` |
| `relation.successor-of` | `source` | `improvement-signal` |
| `relation.successor-of` | `target` | `improvement-signal` |

## Non-collapse boundaries

- `improvement-signal` remains distinct from `improvement-target`.
- `improvement-signal` remains distinct from `failure-occurrence`.

## Orthogonality rules

- **IMPROVEMENT-SIGNAL-IDENTITY**: A Improvement Signal instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **IMPROVEMENT-SIGNAL-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **IMPROVEMENT-SIGNAL-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **IMPROVEMENT-SIGNAL-NON-COLLAPSE**: Improvement Signal remains distinct from improvement-target, failure-occurrence.

## Typed residue

- `IMPROVEMENT-SIGNAL-R1` (role:artifact-type-owner): Owner admission for exact Improvement Signal/v1 bytes. Consequence: Carrier remains candidate-only.
- `IMPROVEMENT-SIGNAL-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Improvement Signal/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
