<!-- GENERATED FILE: edit language.json and rerun generator.py. -->

# Ubiquitous Language: cal.language.ontology-lifecycle

> Generated from `language.json`; this view is not canonical.

- Identity: `cal.language.ontology-lifecycle`
- Version: `1.1.0-candidate.1`
- Status: `candidate-unadmitted`
- Artifact type: `cal.artifact-type.ubiquitous-language/v1`
- Semantic kind: `ubiquitous-language`
- Authority effect: `none`

## Bounded Context Ref

cal.context.ontology-lifecycle/v2

## Concept Refs

- ontology-lifecycle.reconstruct-governed-ontology-state
- ontology-lifecycle.ontology-subject
- ontology-lifecycle.ontology-subject-identity
- ontology-lifecycle.ontology-node
- ontology-lifecycle.ontology-relation
- ontology-lifecycle.ontology-semantic-state
- ontology-lifecycle.semantic-event
- ontology-lifecycle.subject-event-stream
- ontology-lifecycle.ontology-lifecycle-state
- ontology-lifecycle.graph-commit-cursor
- ontology-lifecycle.consistent-ontology-cut
- ontology-lifecycle.relation-endpoint
- ontology-lifecycle.relation-endpoint-integrity
- ontology-lifecycle.governance-event
- ontology-lifecycle.ontology-governance-state
- ontology-lifecycle.exact-semantic-event-reference
- ontology-lifecycle.challenge-contract
- ontology-lifecycle.evidence-confidence
- ontology-lifecycle.commitment-confidence
- ontology-lifecycle.typed-residue
- ontology-lifecycle.context-selector
- ontology-lifecycle.governed-ontology-node-view
- ontology-lifecycle.context-projection
- ontology-lifecycle.replay-failure

## Expression Bindings

```json
[
  {
    "concept_ref": "ontology-lifecycle.reconstruct-governed-ontology-state",
    "disposition": "current",
    "expression": "Reconstruct Governed Ontology State"
  },
  {
    "concept_ref": "ontology-lifecycle.ontology-subject",
    "disposition": "current",
    "expression": "Ontology Subject"
  },
  {
    "concept_ref": "ontology-lifecycle.ontology-subject-identity",
    "disposition": "current",
    "expression": "Ontology Subject Identity"
  },
  {
    "concept_ref": "ontology-lifecycle.ontology-node",
    "disposition": "current",
    "expression": "Ontology Node"
  },
  {
    "concept_ref": "ontology-lifecycle.ontology-relation",
    "disposition": "current",
    "expression": "Ontology Relation"
  },
  {
    "concept_ref": "ontology-lifecycle.ontology-semantic-state",
    "disposition": "current",
    "expression": "Ontology Semantic State"
  },
  {
    "concept_ref": "ontology-lifecycle.semantic-event",
    "disposition": "current",
    "expression": "Semantic Event"
  },
  {
    "concept_ref": "ontology-lifecycle.subject-event-stream",
    "disposition": "current",
    "expression": "Subject Event Stream"
  },
  {
    "concept_ref": "ontology-lifecycle.ontology-lifecycle-state",
    "disposition": "current",
    "expression": "Ontology Lifecycle State"
  },
  {
    "concept_ref": "ontology-lifecycle.graph-commit-cursor",
    "disposition": "current",
    "expression": "Graph Commit Cursor"
  },
  {
    "concept_ref": "ontology-lifecycle.consistent-ontology-cut",
    "disposition": "current",
    "expression": "Consistent Ontology Cut"
  },
  {
    "concept_ref": "ontology-lifecycle.relation-endpoint",
    "disposition": "current",
    "expression": "Relation Endpoint"
  },
  {
    "concept_ref": "ontology-lifecycle.relation-endpoint-integrity",
    "disposition": "current",
    "expression": "Relation Endpoint Integrity"
  },
  {
    "concept_ref": "ontology-lifecycle.governance-event",
    "disposition": "current",
    "expression": "Governance Event"
  },
  {
    "concept_ref": "ontology-lifecycle.ontology-governance-state",
    "disposition": "current",
    "expression": "Ontology Governance State"
  },
  {
    "concept_ref": "ontology-lifecycle.exact-semantic-event-reference",
    "disposition": "current",
    "expression": "Exact Semantic Event Reference"
  },
  {
    "concept_ref": "ontology-lifecycle.challenge-contract",
    "disposition": "current",
    "expression": "Challenge Contract"
  },
  {
    "concept_ref": "ontology-lifecycle.evidence-confidence",
    "disposition": "current",
    "expression": "Evidence Confidence"
  },
  {
    "concept_ref": "ontology-lifecycle.commitment-confidence",
    "disposition": "current",
    "expression": "Commitment Confidence"
  },
  {
    "concept_ref": "ontology-lifecycle.typed-residue",
    "disposition": "current",
    "expression": "Typed Residue"
  },
  {
    "concept_ref": "ontology-lifecycle.context-selector",
    "disposition": "current",
    "expression": "Context Selector"
  },
  {
    "concept_ref": "ontology-lifecycle.governed-ontology-node-view",
    "disposition": "current",
    "expression": "Governed Ontology Node View"
  },
  {
    "concept_ref": "ontology-lifecycle.context-projection",
    "disposition": "current",
    "expression": "Context Projection"
  },
  {
    "concept_ref": "ontology-lifecycle.replay-failure",
    "disposition": "current",
    "expression": "Replay Failure"
  }
]
```

## Relation Bindings

```json
[
  {
    "meaning": "Reconstruct Governed Ontology State reconstructs from a Subject Event Stream.",
    "relation_ref": "CAL-BIZ-REL-001"
  },
  {
    "meaning": "A Subject Event Stream is the stream of one Ontology Subject.",
    "relation_ref": "CAL-BIZ-REL-002"
  },
  {
    "meaning": "An Ontology Subject is identified by an Ontology Subject Identity.",
    "relation_ref": "CAL-BIZ-REL-003"
  },
  {
    "meaning": "An Ontology Node is an Ontology Subject.",
    "relation_ref": "CAL-BIZ-REL-004"
  },
  {
    "meaning": "An Ontology Relation is an Ontology Subject.",
    "relation_ref": "CAL-BIZ-REL-005"
  },
  {
    "meaning": "A Subject Event Stream records Semantic Events.",
    "relation_ref": "CAL-BIZ-REL-006"
  },
  {
    "meaning": "A Semantic Event carries one complete Ontology Semantic State rather than a partial patch.",
    "relation_ref": "CAL-BIZ-REL-007"
  },
  {
    "meaning": "Ontology Semantic State has an explicit Ontology Lifecycle State.",
    "relation_ref": "CAL-BIZ-REL-008"
  },
  {
    "meaning": "A Graph Commit Cursor orders Semantic Events.",
    "relation_ref": "CAL-BIZ-REL-009"
  },
  {
    "meaning": "An Ontology Relation names Relation Endpoints.",
    "relation_ref": "CAL-BIZ-REL-010"
  },
  {
    "meaning": "A Consistent Ontology Cut enforces Relation Endpoint Integrity.",
    "relation_ref": "CAL-BIZ-REL-011"
  },
  {
    "meaning": "A Governance Event carries one complete Ontology Governance State and cannot patch semantic state.",
    "relation_ref": "CAL-BIZ-REL-012"
  },
  {
    "meaning": "A Governance Event joins to semantic history only through an Exact Semantic Event Reference.",
    "relation_ref": "CAL-BIZ-REL-013"
  },
  {
    "meaning": "An Exact Semantic Event Reference identifies one exact Semantic Event.",
    "relation_ref": "CAL-BIZ-REL-014"
  },
  {
    "meaning": "Ontology Governance State contains a Challenge Contract.",
    "relation_ref": "CAL-BIZ-REL-015"
  },
  {
    "meaning": "Ontology Governance State keeps Evidence Confidence separate.",
    "relation_ref": "CAL-BIZ-REL-016"
  },
  {
    "meaning": "Ontology Governance State keeps Commitment Confidence separate.",
    "relation_ref": "CAL-BIZ-REL-017"
  },
  {
    "meaning": "Ontology Governance State routes unresolved material as Typed Residue.",
    "relation_ref": "CAL-BIZ-REL-018"
  },
  {
    "meaning": "Reconstruct Governed Ontology State calculates a Governed Ontology Node View.",
    "relation_ref": "CAL-BIZ-REL-019"
  },
  {
    "meaning": "A Context Selector selects one Consistent Ontology Cut.",
    "relation_ref": "CAL-BIZ-REL-020"
  },
  {
    "meaning": "A Context Selector produces a Context Projection.",
    "relation_ref": "CAL-BIZ-REL-021"
  },
  {
    "meaning": "A Context Projection renders Governed Ontology Node Views.",
    "relation_ref": "CAL-BIZ-REL-022"
  },
  {
    "meaning": "A Context Projection derives from one Consistent Ontology Cut and remains non-canonical.",
    "relation_ref": "CAL-BIZ-REL-023"
  },
  {
    "meaning": "Reconstruct Governed Ontology State fails explicitly with a Replay Failure.",
    "relation_ref": "CAL-BIZ-REL-024"
  }
]
```

## Interpretation Rules

- Interpret every listed expression only inside cal.context.ontology-lifecycle unless the admitted Context Map explicitly translates it.
- The admitted Context Map permits translation of an exact Governance Decision envelope into a local Governance Event while preserving upstream identity, digest, and authority boundary.
- Only complete-state Semantic Events calculate ontology node and relation semantic state; partial patch semantics are invalid.
- Governance Events calculate Ontology Governance State and cannot create or patch Ontology Semantic State or reinterpret a Governance Decision.
- Semantic and governance streams join only through one exact event identity, digest, and cursor tuple.
- Ontology Lifecycle State stores only active, retired, or removed; removed is a terminal tombstone and history remains retained.
- An active Ontology Relation requires active source and target Ontology Nodes in the same Consistent Ontology Cut.
- Challenge Contract, Evidence Confidence, Commitment Confidence, conflict, and Typed Residue remain distinct concerns.
- Context Projections and governed views are deterministic, traceable, rebuildable, non-canonical, and authority-effect none.

## Usage Surfaces

- Ontology Lifecycle Bounded Context canonical artifacts
- semantic and governance event contracts
- replay and consistent-cut validation
- governed ontology views and context projections
- ontology lifecycle conformance evidence
- cal.context-map.governance-ontology-lifecycle/v1 downstream anti-corruption contract

## Owner Refs

- role:ontology-lifecycle-language-owner
- role:ontology-lifecycle-context-owner

## Ambiguity Records

```json
[
  {
    "disposition": "Means a lifecycle record translated from an exact Governance-owned decision envelope. It is not the Governance Decision and cannot grant authority.",
    "expression": "Governance Event"
  },
  {
    "disposition": "Means replay-calculated Ontology Governance State. Governance rules, policies, constitutions, assessments, and owner decisions belong to cal.context.governance.",
    "expression": "Governance State"
  },
  {
    "disposition": "In Context Selector and Context Projection, context means a bounded projection request or result; it is not the identity of a Bounded Context artifact.",
    "expression": "Context"
  },
  {
    "disposition": "Always qualify as Ontology Semantic State, Ontology Governance State, or Ontology Lifecycle State; these axes must not collapse.",
    "expression": "State"
  },
  {
    "disposition": "This context may preserve or reconstruct authority-related evidence, but the authority decision and its meaning remain owned by cal.context.governance.",
    "expression": "Authority"
  }
]
```

## Revision State

candidate-successor-map-bound-unadmitted

## Challenge Route

role:ontology-lifecycle-language-owner

## Evidence

- CAL-CONTEXT-PACK-CTX05-0001
- CAL-DECISION-0023-GOVERNANCE-AND-ONTOLOGY-LIFECYCLE-CONTEXT-PROMOTION
- CAL-DECISION-0024-GOVERNANCE-ONTOLOGY-LIFECYCLE-CONTEXT-MAP-PROMOTION
- cal.language.ontology-lifecycle/v1
- source:cal.ontology-lifecycle.business-domain.v2-candidate

## Residue

- residue:ontology-lifecycle-v2-language-and-context-owner-admission-required
- residue:ontology-lifecycle-business-model-remains-candidate-unadmitted
- residue:runtime-payload-schema-and-anticorruption-adapter-not-authored

## Claim ceiling

This successor candidate preserves the Ontology Lifecycle vocabulary and binds it to the v2 context and admitted Context Map boundary. It does not admit the language or context, admit a global relationship kind, admit the business ontology, authorize a runtime adapter, migration or enforcement, publish, deploy, or establish a stable release.
