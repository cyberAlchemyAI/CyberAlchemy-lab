<!-- Generated from proposal.json by render.py. Do not edit this projection directly. -->

# Governed event-sourced ontology node architecture

- Proposal: `CAL-PROP-0004`
- Schema: `cyberalchemy-lab-architecture-proposal/v0`
- Status: `draft-successor-candidate`
- Decision posture: `not-selected`
- Authority effect: `none`

> This is an unselected successor architecture candidate. It does not rewrite the immutable selected baseline or authorize schema, runtime, migration, publication, release, or deployment effects.

## Immutable predecessor

- Proposal: `CAL-PROP-0001`
- Path: `../0001-context-artifact-architecture/proposal.json`
- SHA-256: `c4174297bfa71818012b77848a7cb8560b47d303b30f062144f2dc03c478932f`
- Posture: `immutable-selected-planning-baseline`
- Rule: This successor does not rewrite, supersede, or amend the accepted predecessor bytes.

## Decision question

How should every CyberAlchemy ontology node preserve typed meaning, contestability, evidence posture, authority boundaries, and context-specific use while canonical events calculate its state?

## Recommendation

Adopt a shared governed-node envelope composed from separately event-sourced semantic and governance facets. Keep ontology-type-specific fields in closed typed profiles, keep relations as first-class subjects, and calculate every context view from one exact semantic cut plus its exact governance join.

## Convention change

- Current rule: The first witness event-sources a thin node or relation resulting state. CyberAlchemy-v2 separately carries richer candidate node conventions for confidence, challenge, provenance, use obligations, residue, authority posture, lifecycle, and non-collapse.
- Proposed rule: The stable node architecture preserves a small universal identity and semantic nucleus, attaches typed profile-specific semantic fields, derives governance facets from a separate governance stream, and exposes only a calculated GovernedOntologyNodeView to contexts and consumers.

## Governed ontology node view

```text
canonical semantic events ──> SemanticNodeState
                                    │
separate governance events ──> GovernanceState
                                    │ exact semantic event ID + digest + cursor
                                    ▼
                         GovernedOntologyNodeView
                                    │ exact Context selector
                                    ▼
                           bounded Context projection
```

### Identity

- node_id
- ontology_id
- node_type_ref

### Semantic state

- lifecycle
- label
- definition_or_claim
- scope
- semantic_components
- semantic_definition_refs
- typed_properties
- use_obligations
- forbidden_collapse

### Governance state

- source_refs_and_typed_provenance
- owner_route
- candidate_or_maturity_status
- promotion_state_or_handle
- authority_kind_and_posture
- authority_effect
- evidence_confidence
- commitment_confidence
- challenge_contract
- residue
- conflicts
- drift_owner
- invalidation_route

### Projection metadata

- semantic_event_id_and_digest
- semantic_cursor
- governance_event_refs
- calculated_view_digest
- context_selector_ref_when_projected

## Challenge contract

- Definition reference: `domainspec-core:CAV2-D40`
- Required when: A candidate ontology node may become load-bearing for a consumer, gate, projection, or authority route.
- Boundary: A challenge contract is not confidence, proof, a verdict, a promotion decision, or authority. It names the valid disagreement and resolution path.

Required fields:

- challenge_response
- valid_challenge_modes
- contradiction_edges
- validation_edges
- owner_route
- resolution_gate
- blocking_questions
- challenge_residue_route

Valid challenge modes:

- evidence
- contradiction
- owner_review

## Typed ontology profiles

- `business-domain`: meaning, actors_or_participants_when_applicable, rules_or_policies_when_applicable, outcomes_or_value_when_applicable
- `system-runtime`: intent, runtime_kind, technical_body, implementation_state, forbidden_inference
- `premise`: supporting_evidence, counterevidence, falsification_criteria, current_use
- `authority-governance`: authority_kind, authority_posture, promotion_handle, allowed_use, blocked_use
- `evidence`: observation_conditions, exact_evidence_refs, claim_ceiling, currentness
- `projection`: source_cursor, source_event_set_digest, allowed_readings, forbidden_authority_moves
- `residue`: residue_type, owner_route, treatment, next_route

## Relation architecture

- Canonicality: Every relation is a first-class ontology subject with its own semantic event stream.
- Integrity: Every active relation endpoint must resolve to an active node in the same consistent ontology cut.
- Challenge edges: challenge_contract contradiction_edges and validation_edges contain relation identities or selectors; they do not embed an independent graph.
- Cycle rule: Value-constraining cycle-permitted relations remain blocked until a contextuality-obstruction review and explicit exception are recorded.

Minimum relation state:

- relation_id
- ontology_id
- relation_type_ref
- lifecycle
- source_node_id
- target_node_id
- direction
- typed_properties
- forbidden_collapse

## Event topology

- Semantic stream: One append-only digest chain per node or relation carries complete resulting semantic state.
- Governance stream: A separate append-only stream carries provenance, confidence, challenge, status, authority, residue, drift, and invalidation changes joined to exact semantic event identity, digest, and cursor.
- Challenge revision: A challenge never edits prior semantic history. An owner-approved revision appends a new semantic event and governance records refer to the old and new exact semantic epochs.
- Calculated view: GovernedOntologyNodeView equals the latest semantic subject state through the selected cursor joined with governance events whose exact semantic references validate.
- Failure policy: A missing, stale, ambiguous, or mismatched selected semantic or governance dependency fails closed; unrelated ambient ontology drift is diagnostic.

## Context interaction

- A CAV2 Context does not own alternate ontology truth and does not add fields to canonical node state.
- A context selector names one exact semantic cursor, required subject set, governance join policy, intended use, and projection profile.
- A context projection may filter or render fields but must retain source cursor, event-set digest, selected node and relation identities, and forbidden authority moves.
- Branch membership is a view classification, not node identity, lifecycle, or authority.
- Two contexts may calculate different bounded views from the same canonical event history without forking ontology truth.

## Invariants

- Canonical semantic events calculate semantic node and relation state; mutable node documents, snapshots, indexes, and context views are not replay sources.
- Semantic meaning and governance posture remain separate event families and join only through exact references.
- Evidence confidence and commitment confidence remain separate axes.
- Challenge contract, node confidence, and node residue remain sibling governance facets.
- Status, maturity, promotion verdict, projection state, and active-or-retired semantic lifecycle never imply one another.
- Schema validity proves shape only and cannot promote, admit, accept, publish, or authorize a node.
- Ontology-type profiles specialize the shared envelope without redefining its identity, challenge, provenance, or authority boundaries.
- No relation is inferred from label equality, directory placement, shared context, or co-occurrence.

## Migration impact

- No existing CyberAlchemy-v2 ontology record is migrated by this proposal.
- The current Lab Rust witness remains a thin mechanics witness and does not conform to the proposed facet-rich node schema yet.
- A successor schema-amendment candidate must define closed semantic and governance event payloads and map existing field aliases without erasing source-local distinctions.
- Legacy node records must be imported as exact source-bound candidates before any semantic normalization or event emission.
- Unknown or conflicting fields become typed residue; they are not dropped into a generic property bag.
- Every migrated relation must preserve endpoint identities, direction, evidence, owner route, authority effect, and cycle policy.

## Required successors

- Owner selection or rejection of this exact successor candidate digest.
- Canonical Lab definitions for the shared node, relation, challenge, confidence, provenance, residue, lifecycle, and context-selector terms.
- A capability-local business ontology and DomainSpec v2 authored model for the facet-rich node and relation contracts.
- Deterministic compilation into a system ontology with exact source-to-symbol bindings.
- Rust semantic and governance payload implementation plus negative tests for stale joins, invalid challenge edges, collapsed confidence axes, and fractured context projections.
- A migration manifest and owner-reviewed mapping for each existing ontology package.

## Rollback

Delete this unselected successor proposal directory and remove its reference from ontology-lifecycle/README.md. The immutable CAL-PROP-0001 baseline and its decision records remain byte-identical.

## Typed residue

### The shared facet-rich node and relation schemas are not authored or admitted.

- Owner needed: CyberAlchemy Lab ontology architecture owner plus definitions and schema owners
- Effect: The architecture is not a runtime payload contract.

### The Rust witness does not yet calculate the full governed node view.

- Owner needed: Ontology Lifecycle runtime owner
- Effect: Current automated PASS remains limited to the thin first witness obligations.

### Existing CyberAlchemy-v2 ontology packages use divergent field names and node shapes.

- Owner needed: Each ontology package owner plus migration owner
- Effect: No bulk normalization or legacy migration is authorized.

### This successor has not been selected against an immutable digest.

- Owner needed: CyberAlchemy Lab architecture owner
- Effect: It may guide review but cannot amend the selected planning baseline.

## Claim ceiling

This successor records an unselected architecture candidate. It does not amend CAL-PROP-0001, admit a node or relation schema, change canonical definitions, migrate ontology records, establish runtime conformance, activate governance, authorize implementation, publish, release, or deploy.
