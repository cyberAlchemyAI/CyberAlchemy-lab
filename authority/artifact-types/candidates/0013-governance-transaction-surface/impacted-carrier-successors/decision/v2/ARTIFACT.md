<!-- GENERATED FILE: canonical data is artifact.json. -->

# Decision Artifact Type v1

- Type: `cal.artifact-type.decision/v2`
- Version: `2.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.decision@1.0.0-candidate.1`

## Distinct validation purpose

A Decision is an attributable authority act that selects an outcome, interpretation, permission, priority, or lifecycle effect for exact subjects within a declared scope and evidence basis. A Decision is distinct from evidence, recommendation, preference, Agent output, execution, and proof that the selected effect occurred.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.declares-effect-on` | `source` | `agent-capability, agent-profile, artifact-type, capability-realization-binding, challenge-event, classification-assignment, communication-preference, definition, delegation, effect, failure-assessment, failure-control-binding, failure-mode, failure-occurrence, governed-model, improvement-target, incident, intent-resolution, operational-lesson, product-capability, relation-kind` |
| `relation.member-of` | `source` | `decision-bundle` |
| `relation.successor-of` | `source` | `decision` |
| `relation.successor-of` | `target` | `decision` |

## Non-collapse boundaries

- `decision` remains distinct from `decision-checkpoint`.
- `decision` remains distinct from `effect`.

## Orthogonality rules

- **DECISION-IDENTITY**: A Decision instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **DECISION-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **DECISION-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **DECISION-NON-COLLAPSE**: Decision remains distinct from decision-checkpoint, effect.

## Typed residue

- `DECISION-V2-R1` (role:artifact-type-owner): Owner admission for this exact endpoint-role successor. Consequence: The admitted v1 carrier remains current.

## Claim ceiling

This candidate Decision/v2 successor widens only the exact closed relation-role surface required by the governance transaction extension. It admits nothing.
