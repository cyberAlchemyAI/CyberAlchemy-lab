<!-- GENERATED FILE: canonical data is artifact.json. -->

# Failure Occurrence Artifact Type v1

- Type: `cal.artifact-type.failure-occurrence/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.failure-occurrence@1.0.0-candidate.1`

## Distinct validation purpose

A Failure Occurrence is an immutable attributable episode in which evidence indicates or suspects that an exact subject revision violated an exact expected boundary under declared conditions. It may remain suspected or indeterminate and does not by itself prove mode, cause, impact extent, containment, or recovery.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.affects` | `source` | `agent-capability, agent-session, artifact-type, generated-output, implementation, ontology, person-reference, product, product-capability, project, work` |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.declares-effect-on` | `target` | `decision` |
| `relation.evaluates` | `target` | `failure-assessment` |
| `relation.evidence-bears-on` | `target` | `evidence-set, feedback-record, finding, measurement-result, observation, operational-observation` |
| `relation.governed-by` | `source` | `policy` |
| `relation.instance-of` | `source` | `classification-value, failure-mode` |
| `relation.member-of` | `source` | `incident` |
| `relation.occurs-during` | `source` | `agent-action, agent-session, experiment-run, research-run, work` |
| `relation.produces` | `target` | `agent-action` |
| `relation.responds-to` | `target` | `agent-action` |
| `relation.successor-of` | `source` | `failure-occurrence` |
| `relation.successor-of` | `target` | `failure-occurrence` |
| `relation.violates` | `source` | `challenge-contract, contract, policy, schema` |

## Non-collapse boundaries

- `failure-occurrence` remains distinct from `incident`.
- `failure-occurrence` remains distinct from `observation`.

## Orthogonality rules

- **FAILURE-OCCURRENCE-IDENTITY**: A Failure Occurrence instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **FAILURE-OCCURRENCE-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **FAILURE-OCCURRENCE-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **FAILURE-OCCURRENCE-NON-COLLAPSE**: Failure Occurrence remains distinct from incident, observation.

## Typed residue

- `FAILURE-OCCURRENCE-R1` (role:artifact-type-owner): Owner admission for exact Failure Occurrence/v1 bytes. Consequence: Carrier remains candidate-only.
- `FAILURE-OCCURRENCE-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Failure Occurrence/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
