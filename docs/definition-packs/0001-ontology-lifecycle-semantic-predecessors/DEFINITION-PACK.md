# Ontology Lifecycle Semantic Predecessors

Status: **candidate; unadmitted; non-effectful**

This is the human view of `definition-pack.json`. The machine-readable pack and
`handled-definitions.json` preserve the exact candidate records. This view does
not promote a definition, admit a Product Capability or ontology, authorize
DomainSpec source, or authorize implementation.

## Target

- Project: `CA2-PROJECT-CYBERALCHEMY-LAB-ONTOLOGY-LIFECYCLE`
- Goal: `CA2-GOAL-CYBERALCHEMY-LAB-EVENT-SOURCED-ONTOLOGY`
- Bounded context: `CAL-CONTEXT-ONTOLOGY-LIFECYCLE`
- First witness: one small Lab-native ontology; legacy migration is excluded

## Source epoch

`CAL-ESOV-0003` is the immutable selected W0 design source. The current
context-artifact proposal has changed since that decision and is retained only
as explicitly drifted context. Proposal-only claims are not imported into this
pack. The pack binds the decision and all other inputs by exact SHA-256 digest.

## Product Capability candidate

**Reconstruct Governed Ontology State** calculates one governed ontology state
at an exact graph commit cursor from canonical semantic event streams and exact
governance event references. It returns a consistent ontology cut or a replay
failure. It never treats a projection, index, snapshot, generated graph, or
successful replay as canonical semantic authority.

Candidate ID: `CA2-CAP-RECONSTRUCT-GOVERNED-ONTOLOGY-STATE`

## Business ontology candidate

Candidate ID: `cal.ontology-lifecycle.business-domain.v1-candidate`

- **ReconstructGovernedOntologyState** (`ontology-lifecycle.reconstruct-governed-ontology-state`): Rebuild the ontology for one exact point from its events and checked governance links.
- **OntologySubject** (`ontology-lifecycle.ontology-subject`): The node or relation whose history the stream records.
- **SemanticEvent** (`ontology-lifecycle.semantic-event`): One permanent fact that says what one node or relation became at one ordered point.
- **SubjectEventStream** (`ontology-lifecycle.subject-event-stream`): The permanent history for one node or relation.
- **ResultingSubjectState** (`ontology-lifecycle.resulting-subject-state`): The full state the subject has after this event, not only what changed.
- **GraphCommitCursor** (`ontology-lifecycle.graph-commit-cursor`): The shared ordering number that tells the whole ontology which semantic event came first.
- **ConsistentOntologyCut** (`ontology-lifecycle.consistent-ontology-cut`): One whole-ontology view where every node and relation comes from the same ordered point.
- **OntologyAtCursor** (`ontology-lifecycle.ontology-at-cursor`): Ask for the ontology at one exact cursor and get the consistent state or a clear failure.
- **CalculatedProjection** (`ontology-lifecycle.calculated-projection`): A useful generated view that can always be rebuilt from the events.
- **LatestSubjectSnapshot** (`ontology-lifecycle.latest-subject-snapshot`): A cached latest state that makes replay faster but can be discarded and rebuilt.
- **GovernanceEvent** (`ontology-lifecycle.governance-event`): A separate permanent record of a governance action about semantic history.
- **GovernanceEventReference** (`ontology-lifecycle.governance-event-reference`): The three-part exact link from a governance record to one semantic event.
- **AppendSemanticEventRequest** (`ontology-lifecycle.append-semantic-event-request`): Ask to add one complete new event without rewriting history.
- **ReplayFailure** (`ontology-lifecycle.replay-failure`): A clear stop result when the events cannot safely produce the requested ontology.
- **RelationEndpointIntegrity** (`ontology-lifecycle.relation-endpoint-integrity`): Every relation points to nodes that exist in the same ontology cut.

## Invariants

1. Semantic events are the canonical source for semantic ontology state.
2. Each ontology subject has exactly one canonical subject event stream.
3. Every accepted semantic event has a unique graph commit cursor in one strict graph-wide total order.
4. Every semantic event carries the complete resulting state of its subject.
5. `OntologyAtCursor` returns one consistent cut or one replay failure; it never reports partial success.
6. Every relation in a consistent cut has both endpoints in that same cut.
7. Projections and latest-subject snapshots are rebuildable and have no independent semantic authority.
8. Governance streams stay separate and join semantic events only through an exact event ID, digest, and cursor reference.
9. Legacy migration requires a later owner decision and stays outside the first witness.

## Open decisions and construction gaps

- Select whether graph cursor allocation is contiguous or may contain unused values before the runtime event schema.
- Select the exact lifecycle marker for a removed or retired subject before the subject-state schema.
- DomainSpec must gain an admitted reducer dataflow relationship and a current admitted compiler profile before DomainSpec authoring can truthfully begin.
- The architecture owner must refresh or supersede the changed proposal-to-decision bridge before it can be claimed current.
- Snapshot frequency, compaction, retention, and multi-writer allocation are deliberately deferred beyond the first witness.

## D65 result

| Stage | Current result |
| --- | --- |
| Canonical definitions | 15 handled-definition candidates prepared; not promoted |
| Product Capability | one candidate prepared; not admitted |
| Capability-local business ontology | one 15-concept, 16-relationship candidate prepared; not admitted |
| DomainSpec v2 authored source | `not_evaluable` until the predecessors are accepted and DomainSpec gaps close |
| Compiled graph and system ontology | `not_evaluable` |
| Implementation binding | `not_evaluable` |
| Conformance evidence | `not_evaluable` |

## Claim ceiling

This pack may support definition review, product-capability review,
business-ontology review, and later DomainSpec planning. It grants no semantic
authority, governance acceptance, implementation authority, migration,
publication, release, or deployment effect.
