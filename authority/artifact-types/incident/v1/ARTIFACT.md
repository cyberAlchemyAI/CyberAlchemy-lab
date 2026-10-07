<!-- GENERATED FILE: canonical data is artifact.json. -->

# Incident Artifact Type v1

- Type: `cal.artifact-type.incident/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.incident@1.0.0-candidate.1`

## Distinct validation purpose

An Incident is a governed response and accountability envelope for related Failure Occurrences whose impact or uncertainty requires coordinated ownership, timeline, containment, recovery, communications, decisions, evidence, and closure. Closure does not erase occurrences, residue, unknown delivery, causal uncertainty, or follow-up obligations.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.affects` | `source` | `agent-capability, agent-session, artifact-type, generated-output, implementation, ontology, person-reference, product, product-capability, project, work` |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.declares-effect-on` | `target` | `decision` |
| `relation.governed-by` | `source` | `policy` |
| `relation.member-of` | `target` | `failure-occurrence` |
| `relation.responds-to` | `target` | `agent-action` |
| `relation.successor-of` | `source` | `incident` |
| `relation.successor-of` | `target` | `incident` |

## Non-collapse boundaries

- `incident` remains distinct from `failure-occurrence`.
- `incident` remains distinct from `project`.

## Orthogonality rules

- **INCIDENT-IDENTITY**: A Incident instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **INCIDENT-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **INCIDENT-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **INCIDENT-NON-COLLAPSE**: Incident remains distinct from failure-occurrence, project.

## Typed residue

- `INCIDENT-R1` (role:artifact-type-owner): Owner admission for exact Incident/v1 bytes. Consequence: Carrier remains candidate-only.
- `INCIDENT-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Incident/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
