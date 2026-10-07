<!-- GENERATED FILE: canonical data is artifact.json. -->

# Project State Artifact Type v1

- Type: `cal.artifact-type.project-state/v2`
- Version: `2.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.project-state@1.0.0-candidate.1`

## Distinct validation purpose

Project State is the durable governed external state of a Project, including versioned artifacts, Definitions, decisions, evidence, event histories, relations, and other records. Project State belongs to the governed Project and its artifact owners, never to an Agent or model.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.materializes-consequence` | `target` | `admission-transaction` |
| `relation.member-of` | `source` | `project` |
| `relation.successor-of` | `source` | `project-state` |
| `relation.successor-of` | `target` | `project-state` |

## Non-collapse boundaries

- `project-state` remains distinct from `session-memory`.
- `project-state` remains distinct from `context-view`.

## Orthogonality rules

- **PROJECT-STATE-IDENTITY**: A Project State instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **PROJECT-STATE-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **PROJECT-STATE-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **PROJECT-STATE-NON-COLLAPSE**: Project State remains distinct from session-memory, context-view.

## Typed residue

- `PROJECT-STATE-V2-R1` (role:artifact-type-owner): Owner admission for this exact endpoint-role successor. Consequence: The admitted v1 carrier remains current.

## Claim ceiling

This candidate Project State/v2 successor widens only the exact closed relation-role surface required by the governance transaction extension. It admits nothing.
