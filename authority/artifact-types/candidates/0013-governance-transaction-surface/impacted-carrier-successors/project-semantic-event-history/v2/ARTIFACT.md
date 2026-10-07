<!-- GENERATED FILE: canonical data is artifact.json. -->

# Project Semantic Event History Artifact Type v1

- Type: `cal.artifact-type.project-semantic-event-history/v2`
- Version: `2.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.project-semantic-event-history@1.0.0-candidate.1`

## Distinct validation purpose

Canonical append-only replay history for complete Project State semantic transitions.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.materializes-consequence` | `target` | `admission-transaction` |

## Non-collapse boundaries

- `project-semantic-event-history` remains distinct from `project-state`.
- `project-semantic-event-history` remains distinct from `semantic-event-history`.
- `project-semantic-event-history` remains distinct from `project-governance-event-history`.
- `project-semantic-event-history` remains distinct from `ontology-view`.

## Orthogonality rules

- **PROJECT-SEMANTIC-EVENT-HISTORY-IDENTITY**: Project Semantic Event History retains its own identity and is not Project State, an ontology history, or a derived view.
- **PROJECT-SEMANTIC-EVENT-HISTORY-REPLAY**: Only ordered digest-bound event records are replay sources; projections and indexes are not competing sources.
- **PROJECT-SEMANTIC-EVENT-HISTORY-AUTHORITY**: Schema validity and event presence create no admission, authority, truth, or runtime effect.
- **PROJECT-SEMANTIC-EVENT-HISTORY-NON-COLLAPSE**: Project Semantic Event History remains distinct from project-state, semantic-event-history, project-governance-event-history, ontology-view.

## Typed residue

- `PROJECT-SEMANTIC-EVENT-HISTORY-V2-R1` (role:artifact-type-owner): Owner admission for this exact endpoint-role successor. Consequence: The admitted v1 carrier remains current.

## Claim ceiling

This candidate Project Semantic Event History/v2 successor widens only the exact closed relation-role surface required by the governance transaction extension. It admits nothing.
