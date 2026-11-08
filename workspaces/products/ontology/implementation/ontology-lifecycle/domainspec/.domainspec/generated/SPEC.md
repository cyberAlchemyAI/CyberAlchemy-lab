# Ontology Lifecycle Runtime Specification

Generated human view. Canonical semantics live in the project-local machine sources.
Graph digest: `3fd9db1221b1cfdcd0ad780e5f435923da0e851120ff9b3de6e8310ac2023c3c`.

## Nodes

| Node | Kind | Intent |
| --- | --- | --- |
| `ontology-lifecycle.AppendSemanticEventRequest` | Operation | Propose one canonical complete-state semantic event at the next graph cursor without changing earlier bytes. |
| `ontology-lifecycle.CalculatedProjection` | Entity | Identify one rebuildable machine or human view derived from a consistent ontology cut with no independent semantic authority. |
| `ontology-lifecycle.ChallengeContract` | Value Object | Declare the complete CAV2-D40 challenge response, modes, typed edges, owner, resolution gate, blocking questions, and residue route without becoming confidence or authority. |
| `ontology-lifecycle.CommitmentConfidence` | Value Object | Represent the responsible owner's willingness to rely on one exact semantic epoch independently of evidence strength and every other governance axis. |
| `ontology-lifecycle.ConsistentOntologyCut` | Value Object | Represent every latest subject state through one exact cursor after relation endpoint validation succeeds. |
| `ontology-lifecycle.ContextProjection` | Entity | Render one deterministic, source-traceable, non-canonical context slice from a single consistent ontology cut with explicit forbidden authority moves. |
| `ontology-lifecycle.ContextSelector` | Value Object | Request one bounded ontology view by exact semantic cursor, required subjects, exact governance join policy, intended use, and closed projection profile. |
| `ontology-lifecycle.EvidenceConfidence` | Value Object | Represent evidence support for one exact semantic epoch independently of commitment, lifecycle, maturity, promotion, and authority. |
| `ontology-lifecycle.ExactSemanticEventReference` | Value Object | Identify one semantic event epoch with the indivisible event ID, canonical digest, and graph commit cursor tuple. |
| `ontology-lifecycle.GovernanceEvent` | Event | Record one immutable complete resulting governance state in a stream separate from semantic ontology history. |
| `ontology-lifecycle.GovernanceEventReference` | Value Object | Join governance evidence to exactly one semantic event through event ID, canonical file digest, and graph cursor. |
| `ontology-lifecycle.GovernedOntologyNodeView` | Entity | Expose one deterministic governed node read model with exact semantic epoch, valid governance join, calculated digest, and optional context selector traceability. |
| `ontology-lifecycle.GraphCommitCursor` | Value Object | Place every semantic event in the first witness into one contiguous graph-wide total order beginning at 1. |
| `ontology-lifecycle.LatestSubjectSnapshot` | Entity | Cache one rebuildable latest state per subject to accelerate reads without becoming canonical input. |
| `ontology-lifecycle.OntologyAtCursor` | Query | Return one consistent ontology cut at an exact cursor or fail atomically with a replay failure. |
| `ontology-lifecycle.OntologyGovernanceState` | Value Object | Carry the complete calculated governance facet for one exact semantic event while keeping provenance, authority, confidence, challenge, conflict, drift, invalidation, and residue explicit and separate. |
| `ontology-lifecycle.OntologyLifecycleState` | Value Object | Store exactly active, retired, or terminal removed lifecycle state under GONLIFE-1; absent is a lookup result and created is a transition. |
| `ontology-lifecycle.OntologyNodeSemanticState` | Value Object | Carry the complete meaning-bearing state of one ontology node after one canonical semantic event, excluding every governance field. |
| `ontology-lifecycle.OntologyRelationSemanticState` | Value Object | Carry one relation identity, selected lifecycle, exact source and target node identities, direction, closed properties, and forbidden collapses. |
| `ontology-lifecycle.OntologySubject` | Entity | Identify one ontology node or relation whose complete semantic history belongs to one canonical subject event stream. |
| `ontology-lifecycle.OntologySubjectIdentity` | Value Object | Identify one ontology node or relation with the stable subject ID, ontology ID, subject kind, and exact type reference selected by GONDEF-1. |
| `ontology-lifecycle.ReconstructGovernedOntologyState` | Calculation | Deterministically reduce canonical subject event streams through one requested graph commit cursor and supply the ontology-at-cursor query without reading projections as source. |
| `ontology-lifecycle.RelationEndpointIntegrity` | Rule | Require both endpoints of every active relation to be active node subjects in the same ontology cut. |
| `ontology-lifecycle.ReplayFailure` | Event | Report one deterministic fail-closed reason without returning a partial ontology cut. |
| `ontology-lifecycle.ResultingSubjectState` | Value Object | Carry the complete node or relation state produced by applying one semantic event. |
| `ontology-lifecycle.SemanticEvent` | Event | Record one immutable complete resulting state for one ontology subject at one graph commit cursor. |
| `ontology-lifecycle.SubjectEventStream` | Entity | Preserve the append-only digest chain of semantic events for exactly one ontology subject. |
| `ontology-lifecycle.TypedResidue` | Value Object | Preserve one typed unresolved remainder with its source operation, expectation, observation, evidence, owner, and treatment. |

## Edges

| Edge | From | Type | To |
| --- | --- | --- | --- |
| `ontology-lifecycle.edge.append-proposes-event` | `ontology-lifecycle.AppendSemanticEventRequest` | `proposes` | `ontology-lifecycle.SemanticEvent` |
| `ontology-lifecycle.edge.context-projection-from-cut` | `ontology-lifecycle.ContextProjection` | `derives-from` | `ontology-lifecycle.ConsistentOntologyCut` |
| `ontology-lifecycle.edge.context-projection-renders-view` | `ontology-lifecycle.ContextProjection` | `renders` | `ontology-lifecycle.GovernedOntologyNodeView` |
| `ontology-lifecycle.edge.cursor-orders-event` | `ontology-lifecycle.GraphCommitCursor` | `orders` | `ontology-lifecycle.SemanticEvent` |
| `ontology-lifecycle.edge.cut-satisfies-integrity` | `ontology-lifecycle.ConsistentOntologyCut` | `satisfies` | `ontology-lifecycle.RelationEndpointIntegrity` |
| `ontology-lifecycle.edge.event-applies-subject` | `ontology-lifecycle.SemanticEvent` | `applies-to` | `ontology-lifecycle.OntologySubject` |
| `ontology-lifecycle.edge.event-carries-node-state` | `ontology-lifecycle.SemanticEvent` | `carries` | `ontology-lifecycle.OntologyNodeSemanticState` |
| `ontology-lifecycle.edge.event-carries-relation-state` | `ontology-lifecycle.SemanticEvent` | `carries` | `ontology-lifecycle.OntologyRelationSemanticState` |
| `ontology-lifecycle.edge.event-carries-state` | `ontology-lifecycle.SemanticEvent` | `carries` | `ontology-lifecycle.ResultingSubjectState` |
| `ontology-lifecycle.edge.exact-reference-identifies-event` | `ontology-lifecycle.ExactSemanticEventReference` | `identifies` | `ontology-lifecycle.SemanticEvent` |
| `ontology-lifecycle.edge.governance-carries-reference` | `ontology-lifecycle.GovernanceEvent` | `carries-reference` | `ontology-lifecycle.ExactSemanticEventReference` |
| `ontology-lifecycle.edge.governance-carries-state` | `ontology-lifecycle.GovernanceEvent` | `carries` | `ontology-lifecycle.OntologyGovernanceState` |
| `ontology-lifecycle.edge.governance-reference-identifies-event` | `ontology-lifecycle.GovernanceEventReference` | `identifies` | `ontology-lifecycle.SemanticEvent` |
| `ontology-lifecycle.edge.governance-state-contains-challenge` | `ontology-lifecycle.OntologyGovernanceState` | `contains` | `ontology-lifecycle.ChallengeContract` |
| `ontology-lifecycle.edge.governance-state-joins-reference` | `ontology-lifecycle.OntologyGovernanceState` | `joins-through` | `ontology-lifecycle.ExactSemanticEventReference` |
| `ontology-lifecycle.edge.governance-state-keeps-commitment` | `ontology-lifecycle.OntologyGovernanceState` | `keeps-separate` | `ontology-lifecycle.CommitmentConfidence` |
| `ontology-lifecycle.edge.governance-state-keeps-evidence` | `ontology-lifecycle.OntologyGovernanceState` | `keeps-separate` | `ontology-lifecycle.EvidenceConfidence` |
| `ontology-lifecycle.edge.governance-state-routes-residue` | `ontology-lifecycle.OntologyGovernanceState` | `routes` | `ontology-lifecycle.TypedResidue` |
| `ontology-lifecycle.edge.governed-view-from-cut` | `ontology-lifecycle.GovernedOntologyNodeView` | `derives-from` | `ontology-lifecycle.ConsistentOntologyCut` |
| `ontology-lifecycle.edge.node-state-has-lifecycle` | `ontology-lifecycle.OntologyNodeSemanticState` | `has-lifecycle` | `ontology-lifecycle.OntologyLifecycleState` |
| `ontology-lifecycle.edge.node-state-identified-by` | `ontology-lifecycle.OntologyNodeSemanticState` | `identified-by` | `ontology-lifecycle.OntologySubjectIdentity` |
| `ontology-lifecycle.edge.projection-from-cut` | `ontology-lifecycle.CalculatedProjection` | `derives-from` | `ontology-lifecycle.ConsistentOntologyCut` |
| `ontology-lifecycle.edge.projection-renders-view` | `ontology-lifecycle.CalculatedProjection` | `renders` | `ontology-lifecycle.GovernedOntologyNodeView` |
| `ontology-lifecycle.edge.query-fails-replay` | `ontology-lifecycle.OntologyAtCursor` | `fails-with` | `ontology-lifecycle.ReplayFailure` |
| `ontology-lifecycle.edge.query-returns-cut` | `ontology-lifecycle.OntologyAtCursor` | `returns` | `ontology-lifecycle.ConsistentOntologyCut` |
| `ontology-lifecycle.edge.reconstructor-calculates-view` | `ontology-lifecycle.ReconstructGovernedOntologyState` | `calculates` | `ontology-lifecycle.GovernedOntologyNodeView` |
| `ontology-lifecycle.edge.reconstructor-from-stream` | `ontology-lifecycle.ReconstructGovernedOntologyState` | `reconstructs-from` | `ontology-lifecycle.SubjectEventStream` |
| `ontology-lifecycle.edge.reconstructor-supplies-query` | `ontology-lifecycle.ReconstructGovernedOntologyState` | `supplies` | `ontology-lifecycle.OntologyAtCursor` |
| `ontology-lifecycle.edge.relation-state-has-lifecycle` | `ontology-lifecycle.OntologyRelationSemanticState` | `has-lifecycle` | `ontology-lifecycle.OntologyLifecycleState` |
| `ontology-lifecycle.edge.relation-state-identified-by` | `ontology-lifecycle.OntologyRelationSemanticState` | `identified-by` | `ontology-lifecycle.OntologySubjectIdentity` |
| `ontology-lifecycle.edge.selector-produces-context-projection` | `ontology-lifecycle.ContextSelector` | `produces` | `ontology-lifecycle.ContextProjection` |
| `ontology-lifecycle.edge.selector-selects-cut` | `ontology-lifecycle.ContextSelector` | `selects` | `ontology-lifecycle.ConsistentOntologyCut` |
| `ontology-lifecycle.edge.snapshot-accelerates-query` | `ontology-lifecycle.LatestSubjectSnapshot` | `accelerates` | `ontology-lifecycle.OntologyAtCursor` |
| `ontology-lifecycle.edge.snapshot-from-stream` | `ontology-lifecycle.LatestSubjectSnapshot` | `derives-from` | `ontology-lifecycle.SubjectEventStream` |
| `ontology-lifecycle.edge.stream-of-subject` | `ontology-lifecycle.SubjectEventStream` | `stream-of` | `ontology-lifecycle.OntologySubject` |
| `ontology-lifecycle.edge.stream-records-event` | `ontology-lifecycle.SubjectEventStream` | `records` | `ontology-lifecycle.SemanticEvent` |
| `ontology-lifecycle.edge.subject-has-lifecycle` | `ontology-lifecycle.OntologySubject` | `has-lifecycle` | `ontology-lifecycle.OntologyLifecycleState` |
| `ontology-lifecycle.edge.subject-identified-by-identity` | `ontology-lifecycle.OntologySubject` | `identified-by` | `ontology-lifecycle.OntologySubjectIdentity` |

This file is generated; edit machine sources and rebuild.
