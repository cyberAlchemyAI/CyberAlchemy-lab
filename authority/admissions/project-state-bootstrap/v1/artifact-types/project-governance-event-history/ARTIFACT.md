<!-- GENERATED FILE: canonical data is artifact.json. -->

# Project Governance Event History Artifact Type v1

- Type: `cal.artifact-type.project-governance-event-history/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.project-governance-event-history@1.0.0-candidate.1`

## Distinct validation purpose

Canonical append-only governance history joined to exact Project semantic events and owner authority evidence.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |

## Non-collapse boundaries

- `project-governance-event-history` remains distinct from `project-state`.
- `project-governance-event-history` remains distinct from `governance-event-history`.
- `project-governance-event-history` remains distinct from `project-semantic-event-history`.
- `project-governance-event-history` remains distinct from `policy`.

## Orthogonality rules

- **PROJECT-GOVERNANCE-EVENT-HISTORY-IDENTITY**: Project Governance Event History retains its own identity and is not Project State, an ontology history, or a derived view.
- **PROJECT-GOVERNANCE-EVENT-HISTORY-REPLAY**: Only ordered digest-bound event records are replay sources; projections and indexes are not competing sources.
- **PROJECT-GOVERNANCE-EVENT-HISTORY-AUTHORITY**: Schema validity and event presence create no admission, authority, truth, or runtime effect.
- **PROJECT-GOVERNANCE-EVENT-HISTORY-NON-COLLAPSE**: Project Governance Event History remains distinct from project-state, governance-event-history, project-semantic-event-history, policy.

## Typed residue

- `PROJECT-GOVERNANCE-EVENT-HISTORY-R1` (role:artifact-type-owner): Exact Decision 0072 atomic admission. Consequence: Carrier and instances remain candidate-only.

## Claim ceiling

Candidate Project Governance Event History/v1 carrier. PASS proves only the exact schema, Definition binding, fixtures, event integrity, and projections; it does not admit the type or any instance.
