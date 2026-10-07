<!-- GENERATED FILE: canonical data is artifact.json. -->

# Improvement Target Artifact Type v1

- Type: `cal.artifact-type.improvement-target/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.improvement-target@1.0.0-candidate.1`

## Distinct validation purpose

An Improvement Target is an owner-reviewed deduplicated statement of a recurring weakness or opportunity routed into Research, Experiment, Profile, Policy, validation, or Implementation work. It is neither a self-upgrade authorization nor proof of cause, feasibility, or benefit.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.addresses-improvement-target` | `target` | `research-inquiry` |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.declares-effect-on` | `target` | `decision` |
| `relation.derives-from` | `source` | `improvement-signal, lesson-outcome-assessment, operational-lesson` |
| `relation.instance-of` | `source` | `classification-value` |
| `relation.successor-of` | `source` | `improvement-target` |
| `relation.successor-of` | `target` | `improvement-target` |

## Non-collapse boundaries

- `improvement-target` remains distinct from `goal`.
- `improvement-target` remains distinct from `improvement-signal`.

## Orthogonality rules

- **IMPROVEMENT-TARGET-IDENTITY**: A Improvement Target instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **IMPROVEMENT-TARGET-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **IMPROVEMENT-TARGET-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **IMPROVEMENT-TARGET-NON-COLLAPSE**: Improvement Target remains distinct from goal, improvement-signal.

## Typed residue

- `IMPROVEMENT-TARGET-R1` (role:artifact-type-owner): Owner admission for exact Improvement Target/v1 bytes. Consequence: Carrier remains candidate-only.
- `IMPROVEMENT-TARGET-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Improvement Target/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
