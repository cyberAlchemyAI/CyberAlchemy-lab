<!-- GENERATED FILE: canonical data is artifact.json. -->

# Project Semantic Event History Artifact Type v1

- Type: `cal.artifact-type.project-semantic-event-history/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.project-semantic-event-history@1.0.0-candidate.1`

## Distinct validation purpose

Canonical append-only replay history for complete Project State semantic transitions.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |

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

- `PROJECT-SEMANTIC-EVENT-HISTORY-R1` (role:artifact-type-owner): Exact Decision 0072 atomic admission. Consequence: Carrier and instances remain candidate-only.

## Claim ceiling

Candidate Project Semantic Event History/v1 carrier. PASS proves only the exact schema, Definition binding, fixtures, event integrity, and projections; it does not admit the type or any instance.
