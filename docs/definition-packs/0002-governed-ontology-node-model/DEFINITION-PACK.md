# Governed Ontology Node Definition Pack

Pack: `DEFINE-PACK-CAL-GOVERNED-ONTOLOGY-NODE-002`

Status: `validated-candidate-pending-owner-review`

Authority effect: `none`

## Outcome

Define the smallest stable governed ontology node, relation, challenge, confidence, residue, lifecycle, exact-reference, and context-selection semantics selected by CAL-GONA-0005 before executable schema or runtime work.

This pack defines the candidate meaning that executable node, relation, governance, challenge, exact-reference, and context-projection schemas must preserve. It does not implement those schemas.

## Stable model

```text
semantic subject events -> OntologySemanticState
governance events --exact event id + digest + cursor--> OntologyGovernanceState
identity + semantic state + governance state -> GovernedOntologyNodeView
ContextSelector + governed views -> ContextProjection
```

Canonical events remain the replay source. Nodes, snapshots, indexes, governed views, and context projections are calculated read models.

## Confidence-axis correction

The source plan used `semantic confidence` and `governance confidence`. Those phrases are rejected aliases because they hide the selected `CAV2-D23` separation:

- `evidence_confidence` states how strongly current evidence supports one exact semantic claim epoch.
- `commitment_confidence` states how strongly the responsible owner is prepared to rely on that epoch.
- `evidence_strength` assesses one evidence item's support under declared conditions. It informs evidence confidence but is not another confidence axis.

## Definition registry

| ID | Term | Disposition | Plain-language voice |
|---|---|---|---|
| `ontology-lifecycle.ontology-subject` | OntologySubject | `propose` | The specific node or relation whose history we are following. |
| `ontology-lifecycle.ontology-node` | OntologyNode | `propose` | A typed meaning-bearing item whose current state comes from its own event history. |
| `ontology-lifecycle.ontology-relation` | OntologyRelation | `propose` | A relationship with its own identity and history, not a loose link hidden inside a node. |
| `ontology-lifecycle.ontology-subject-identity` | OntologySubjectIdentity | `propose` | The permanent address of one node or relation. |
| `ontology-lifecycle.ontology-semantic-state` | OntologySemanticState | `propose` | Everything the node or relation means after one event. |
| `ontology-lifecycle.ontology-governance-state` | OntologyGovernanceState | `propose` | The current governed posture attached to one exact version of meaning. |
| `ontology-lifecycle.governed-ontology-node-view` | GovernedOntologyNodeView | `propose` | The complete calculated node that a governed consumer can read. |
| `ontology-lifecycle.challenge-contract` | ChallengeContract | `reuse` | The node's instructions for how to disagree with it correctly. |
| `ontology-lifecycle.relation-endpoint` | RelationEndpoint | `propose` | One of the two exact nodes that a relation connects. |
| `ontology-lifecycle.relation-endpoint-integrity` | RelationEndpointIntegrity | `propose` | A live relation cannot point to a missing node. |
| `ontology-lifecycle.context-selector` | ContextSelector | `propose` | A precise request for which part of the ontology a context needs and at what point. |
| `ontology-lifecycle.context-projection` | ContextProjection | `propose` | The exact slice of the ontology calculated for one context. |
| `ontology-lifecycle.exact-semantic-event-reference` | ExactSemanticEventReference | `propose` | The three-part exact address of one version of semantic state. |
| `ontology-lifecycle.authority-lifecycle-axis` | AuthorityLifecycleAxis | `reuse` | Useful, trusted, finished, owned, and canonical are different claims. |
| `ontology-lifecycle.evidence-confidence` | EvidenceConfidence | `specialize` | How confident the evidence lets us be about this exact version of meaning. |
| `ontology-lifecycle.commitment-confidence` | CommitmentConfidence | `specialize` | How strongly the owner is prepared to rely on this exact version. |
| `ontology-lifecycle.evidence-strength` | EvidenceStrength | `propose` | How much support one piece of evidence actually provides for one claim. |
| `ontology-lifecycle.typed-residue` | TypedResidue | `specialize` | The meaningful leftover, recorded with what it is and who must handle it. |
| `ontology-lifecycle.ontology-lifecycle-state` | OntologyLifecycleState | `propose` | Whether this node or relation exists for use at this point in its history. |
| `ontology-lifecycle.use-obligation` | UseObligation | `propose` | A rule the consumer must follow when it uses this meaning. |
| `ontology-lifecycle.forbidden-collapse` | ForbiddenCollapse | `propose` | A warning that two similar-looking things must stay different. |
| `ontology-lifecycle.provenance` | Provenance | `reuse` | The receipt trail for where the object came from and how it changed. |
| `ontology-lifecycle.governance-event` | GovernanceEvent | `propose` | A permanent governance update about one exact version of a node or relation. |

## Definition voices

### OntologySubject (`ontology-lifecycle.ontology-subject`)

Normative: An OntologySubject is one identity-bearing node or relation whose semantic history is recorded in exactly one canonical subject event stream.

Formal: `OntologySubject = OntologyNode | OntologyRelation; canonical_stream_count(subject) = 1.`

Operational: Use the subject identity to select the event chain that calculates one node or relation state.

Plain language: The specific node or relation whose history we are following.

CyberAlchemy Lab context: In CyberAlchemy Lab, the reducer calculates each subject independently before it assembles an ontology cut.

Boundary: A subject is not its mutable document, latest snapshot, projection row, label, or directory path.

### OntologyNode (`ontology-lifecycle.ontology-node`)

Normative: An OntologyNode is an OntologySubject that carries one stable node identity and a complete resulting semantic state specialized by one closed ontology-type profile.

Formal: `OntologyNode = (OntologySubjectIdentity, OntologySemanticState, profile_ref), where profile_ref resolves to one closed profile.`

Operational: Append a complete semantic state event when the node meaning changes; calculate the current node by replaying its stream.

Plain language: A typed meaning-bearing item whose current state comes from its own event history.

CyberAlchemy Lab context: CyberAlchemy ontology nodes may represent business meaning, runtime meaning, premises, authority, evidence, projections, or residue through closed profiles.

Boundary: A node is not its governance posture and must not infer authority from status, location, shared context, or label equality.

### OntologyRelation (`ontology-lifecycle.ontology-relation`)

Normative: An OntologyRelation is a first-class OntologySubject whose complete semantic state names one typed directed or symmetric link and its exact source and target node identities.

Formal: `OntologyRelation = (identity, relation_type_ref, lifecycle, source_node_id, target_node_id, direction, typed_properties, forbidden_collapse).`

Operational: Give each relation its own semantic event stream and validate both endpoints in the same ontology cut.

Plain language: A relationship with its own identity and history, not a loose link hidden inside a node.

CyberAlchemy Lab context: CyberAlchemy Lab replays relation subjects beside node subjects and rejects active relations whose endpoints are absent from the selected cut.

Boundary: Do not infer a relation from labels, directories, co-occurrence, shared context, or an embedded challenge graph.

### OntologySubjectIdentity (`ontology-lifecycle.ontology-subject-identity`)

Normative: OntologySubjectIdentity is the stable tuple that identifies one node or relation independently of its label, lifecycle, current state, location, and projections.

Formal: `OntologySubjectIdentity = (subject_id, ontology_id, subject_kind, type_ref), with subject_id unique within ontology_id.`

Operational: Use the tuple to derive the subject stream and to reject cross-ontology or cross-kind identity collisions.

Plain language: The permanent address of one node or relation.

CyberAlchemy Lab context: For a node, subject_id is node_id and type_ref is node_type_ref; for a relation, they are relation_id and relation_type_ref.

Boundary: Identity does not change when a label, definition, status, owner, or projection changes.

### OntologySemanticState (`ontology-lifecycle.ontology-semantic-state`)

Normative: OntologySemanticState is the complete meaning-bearing state that one accepted semantic event says an OntologySubject has after that event.

Formal: `state(subject, event_n) = event_n.complete_resulting_semantic_state; prior state is not patched at read time.`

Operational: Validate the whole resulting state, append it, and select the latest valid event at or before the requested cursor.

Plain language: Everything the node or relation means after one event.

CyberAlchemy Lab context: For nodes this includes lifecycle, label, definition or claim, scope, semantic components, definition references, typed properties, use obligations, and forbidden collapses.

Boundary: Semantic state excludes provenance, confidence, promotion, authority, challenge handling, conflicts, and governance residue.

### OntologyGovernanceState (`ontology-lifecycle.ontology-governance-state`)

Normative: OntologyGovernanceState is the calculated governance facet for one exact semantic event epoch, derived only from valid governance events that reference that epoch exactly.

Formal: `governance_state(e) = fold(valid governance events g where g.semantic_ref = (id(e), digest(e), cursor(e))).`

Operational: Validate each exact reference before applying provenance, owner, status, authority, confidence, challenge, conflict, drift, invalidation, or residue changes.

Plain language: The current governed posture attached to one exact version of meaning.

CyberAlchemy Lab context: CyberAlchemy Lab calculates this facet separately so governance work cannot rewrite semantic history.

Boundary: Governance state is not semantic state, does not grant authority by itself, and cannot join by subject ID alone.

### GovernedOntologyNodeView (`ontology-lifecycle.governed-ontology-node-view`)

Normative: GovernedOntologyNodeView is a deterministic read model that combines one node identity, its latest valid semantic state through a selected cursor, the valid governance state for that exact semantic epoch, and source projection metadata.

Formal: `view(node,c) = identity(node) + latest_semantic(node,c) + governance(exact_ref(latest_semantic)) + projection_metadata.`

Operational: Build the view from canonical event streams and fail closed when a selected semantic or governance dependency is missing, stale, ambiguous, or mismatched.

Plain language: The complete calculated node that a governed consumer can read.

CyberAlchemy Lab context: This is the object exposed to CyberAlchemy contexts; it carries source cursor and digest data so consumers can trace it back to events.

Boundary: The view is not a replay source, independent truth, promotion verdict, or alternate context-owned node.

### ChallengeContract (`ontology-lifecycle.challenge-contract`)

Normative: This pack reuses CAV2-D40 without amendment: a challenge contract declares how an object can be challenged, contradicted, validated, blocked, or routed for owner review without silently changing meaning or confidence.

Formal: `ChallengeContract = (challenge_response, valid_challenge_modes, contradiction_edges, validation_edges, owner_route, resolution_gate, blocking_questions, challenge_residue_route).`

Operational: Require the complete contract when a candidate node may become load-bearing, and route every unresolved challenge through its named gate or residue route.

Plain language: The node's instructions for how to disagree with it correctly.

CyberAlchemy Lab context: The governed-node model stores the challenge contract beside confidence and residue, never inside either one.

Boundary: It is not confidence, proof, a verdict, promotion, authority, or the object's own residue.

### RelationEndpoint (`ontology-lifecycle.relation-endpoint`)

Normative: A RelationEndpoint is an exact OntologyNode identity occupying the source or target role of one OntologyRelation.

Formal: `RelationEndpoint = (role in {source,target}, node_id, ontology_id); endpoint.ontology_id = relation.ontology_id.`

Operational: Resolve both endpoint identities in the same selected ontology cut before admitting an active relation into that cut.

Plain language: One of the two exact nodes that a relation connects.

CyberAlchemy Lab context: CyberAlchemy Lab uses endpoint identities instead of embedded node copies or label-based joins.

Boundary: An endpoint is not a label, selector result, directory path, or implied node.

### RelationEndpointIntegrity (`ontology-lifecycle.relation-endpoint-integrity`)

Normative: RelationEndpointIntegrity is the invariant that every active relation has valid source and target node identities present and active in the same consistent ontology cut.

Formal: `active(r,cut) implies exists active source(r) in cut and exists active target(r) in cut.`

Operational: Reject or classify as typed residue any relation whose endpoint cannot be resolved at the selected cursor.

Plain language: A live relation cannot point to a missing node.

CyberAlchemy Lab context: The ontology-at-cursor projection checks endpoint integrity after calculating node and relation states at one cut.

Boundary: Endpoint presence at another cursor or in another context does not satisfy this invariant.

### ContextSelector (`ontology-lifecycle.context-selector`)

Normative: A ContextSelector is a source-bound request for one bounded ontology view that names an exact semantic cursor, required subject set, governance join policy, intended use, and projection profile.

Formal: `ContextSelector = (semantic_cursor, required_subject_set, governance_join_policy, intended_use, projection_profile).`

Operational: Resolve every required subject and valid governance join at the named cursor, then apply only the selected projection profile.

Plain language: A precise request for which part of the ontology a context needs and at what point.

CyberAlchemy Lab context: A CyberAlchemy Context uses the selector to calculate a view without creating its own ontology truth.

Boundary: A selector does not add canonical fields, fork identity, change lifecycle, or grant authority.

### ContextProjection (`ontology-lifecycle.context-projection`)

Normative: A ContextProjection is a deterministic bounded read model produced by one ContextSelector and carrying the source cursor, event-set digest, selected subject identities, and forbidden authority moves.

Formal: `ContextProjection = project(ontology_at(selector.cursor), selector.subjects, selector.profile, selector.join_policy).`

Operational: Filter or render the consistent source view while retaining the metadata needed to reproduce and audit the result.

Plain language: The exact slice of the ontology calculated for one context.

CyberAlchemy Lab context: Two CyberAlchemy contexts may calculate different projections from the same event history without forking that history.

Boundary: A context projection is not canonical state, a replay source, a lifecycle verdict, or an authority decision.

### ExactSemanticEventReference (`ontology-lifecycle.exact-semantic-event-reference`)

Normative: An ExactSemanticEventReference is the indivisible tuple of semantic event identity, semantic event digest, and graph commit cursor that identifies one semantic event epoch across stream boundaries.

Formal: `ExactSemanticEventReference = (semantic_event_id, semantic_event_digest, semantic_cursor), and every component must match one stored semantic event.`

Operational: Reject a governance join when any tuple component is absent, stale, ambiguous, or belongs to a different event.

Plain language: The three-part exact address of one version of semantic state.

CyberAlchemy Lab context: CyberAlchemy Lab uses this reference so a governance event cannot attach to a convenient but different node version.

Boundary: Subject ID, cursor, event ID, or digest alone is not an exact reference.

### AuthorityLifecycleAxis (`ontology-lifecycle.authority-lifecycle-axis`)

Normative: This pack reuses CAV2-D23 without amendment: kind, status, evidence confidence, commitment, provenance, owner, and residue remain separate authority-lifecycle dimensions.

Formal: `L(a) = (kind, status, evidence, commitment, provenance, owner, residue), with no implicit cross-axis movement.`

Operational: Record which governance dimension changed and leave every other dimension unchanged unless an explicit typed coupling says otherwise.

Plain language: Useful, trusted, finished, owned, and canonical are different claims.

CyberAlchemy Lab context: The governed-node view carries separate fields so node maturity cannot impersonate evidence or authority.

Boundary: The axis is not a complete status taxonomy and does not turn every artifact into an ontology node.

### EvidenceConfidence (`ontology-lifecycle.evidence-confidence`)

Normative: EvidenceConfidence is the CAV2-D23 evidence axis applied to how strongly current evidence supports the semantic claim represented by one exact ontology subject epoch.

Formal: `evidence_confidence(subject_epoch) is independent of commitment_confidence, lifecycle, status, authority, and challenge outcome.`

Operational: Update the evidence axis through governance events bound to the exact semantic event; do not rewrite semantic state.

Plain language: How confident the evidence lets us be about this exact version of meaning.

CyberAlchemy Lab context: CyberAlchemy Lab stores evidence confidence in the governance stream, even though it assesses a semantic claim.

Boundary: Do not call this semantic confidence, because that phrase hides its evidence basis and suggests confidence lives in semantic state.

### CommitmentConfidence (`ontology-lifecycle.commitment-confidence`)

Normative: CommitmentConfidence is the CAV2-D23 commitment axis applied to the responsible owner's declared willingness to rely on or act from one exact ontology subject epoch.

Formal: `commitment_confidence(subject_epoch) is independent of evidence_confidence, lifecycle, status, promotion, and authority effect.`

Operational: Record owner commitment as a governance posture and never infer it from evidence strength or maturity.

Plain language: How strongly the owner is prepared to rely on this exact version.

CyberAlchemy Lab context: A CyberAlchemy owner may have high commitment to a low-evidence premise, but the two axes remain visible.

Boundary: Do not call this governance confidence, because governance state contains many non-confidence fields and does not form one aggregate score.

### EvidenceStrength (`ontology-lifecycle.evidence-strength`)

Normative: EvidenceStrength is an evidence-object assessment of how directly, reliably, and currently one evidence item supports or contradicts one stated claim under declared observation conditions.

Formal: `evidence_strength(evidence, claim, conditions) is an assessment input to evidence_confidence; it is not evidence_confidence itself.`

Operational: Assess evidence items first, preserve provenance and conditions, then let an owner-controlled assessment update evidence confidence separately.

Plain language: How much support one piece of evidence actually provides for one claim.

CyberAlchemy Lab context: CyberAlchemy Lab can compare evidence items without collapsing their strength into the node's confidence or the owner's commitment.

Boundary: Evidence strength is not truth, confidence, commitment, authority, maturity, or a promotion verdict.

### TypedResidue (`ontology-lifecycle.typed-residue`)

Normative: TypedResidue is CAV2-D18 residue attached to an ontology subject or operation with its source operation, expected preservation condition, observed remainder, residue type, evidence, owner route, and treatment stated explicitly.

Formal: `TypedResidue = (source_operation, expected_condition, observed_remainder, residue_type, evidence_ref, owner_route, treatment).`

Operational: Preserve any unknown, conflicting, unmapped, or unvalidated structure as typed residue and route it instead of dropping it into an untyped property bag.

Plain language: The meaningful leftover, recorded with what it is and who must handle it.

CyberAlchemy Lab context: CyberAlchemy Lab uses typed residue for schema gaps, stale joins, migration mismatches, unresolved challenges, and authority gaps.

Boundary: Residue is not any uncertainty, automatic failure, novelty proof, generic notes, or permission to proceed.

### OntologyLifecycleState (`ontology-lifecycle.ontology-lifecycle-state`)

Normative: OntologyLifecycleState is the semantic state of whether an OntologySubject exists for use at a selected cursor under one owner-defined closed vocabulary.

Formal: `lifecycle(subject,cursor) belongs to one closed vocabulary and is independent of candidate status, maturity, promotion, projection state, and authority posture.`

Operational: Calculate lifecycle from the subject's semantic event stream and use it when determining node membership and relation endpoint integrity.

Plain language: Whether this node or relation exists for use at this point in its history.

CyberAlchemy Lab context: The exact lifecycle values remain an open owner decision before executable schema authoring.

Boundary: Lifecycle does not mean reviewed, trusted, promoted, projected, mature, or authoritative.

### UseObligation (`ontology-lifecycle.use-obligation`)

Normative: A UseObligation is a typed condition that a consumer must preserve or satisfy when using one ontology subject for a stated purpose.

Formal: `use(subject,purpose) is permitted only if every applicable obligation(subject,purpose) is satisfied or explicitly blocked.`

Operational: Carry obligations in semantic state and evaluate them in the consuming context without converting them into authority.

Plain language: A rule the consumer must follow when it uses this meaning.

CyberAlchemy Lab context: A context projection retains the obligations needed for its intended use even when it filters other fields.

Boundary: A use obligation is not a governance verdict, global policy, implied permission, or hidden implementation requirement.

### ForbiddenCollapse (`ontology-lifecycle.forbidden-collapse`)

Normative: A ForbiddenCollapse is an explicit declaration that one term, field, state, relation, or authority posture must not be treated as equivalent to another named concept.

Formal: `ForbiddenCollapse(a,b) asserts a is not equivalent to b for the declared context and intended use.`

Operational: Use the declarations to design negative fixtures that reject field aliases, inferred relationships, or state transitions that erase required distinctions.

Plain language: A warning that two similar-looking things must stay different.

CyberAlchemy Lab context: The governed-node model uses these rules to keep confidence axes, lifecycle, maturity, authority, challenge, residue, and projections separate.

Boundary: It is not a claim that the concepts never interact; explicit typed couplings may relate them without merging them.

### Provenance (`ontology-lifecycle.provenance`)

Normative: This pack reuses CAV2-D35 without amendment: provenance is the declared typed origin and transformation chain for the ontology subject, event, projection, evidence, decision, or residue.

Formal: `Prov(x) = [(source_i, relation_i, operation_i, owner_i, posture_i)]*; missing segments are typed residue.`

Operational: Retain source references, transformations, owners, and posture changes so every calculated view can be audited to its origin.

Plain language: The receipt trail for where the object came from and how it changed.

CyberAlchemy Lab context: Governance events carry typed provenance without turning a complete source trail into proof or authority.

Boundary: Provenance is not proof, trust, validation, authority, or credit assignment by itself.

### GovernanceEvent (`ontology-lifecycle.governance-event`)

Normative: A GovernanceEvent is an immutable typed record of one governance-state change or observation in a governance-owned stream, bound to one semantic event epoch through an ExactSemanticEventReference.

Formal: `GovernanceEvent = (event_identity, governance_stream_identity, exact_semantic_reference, complete_resulting_governance_state, ordering_metadata).`

Operational: Validate the exact semantic reference and stream continuity before using the event to calculate governance state.

Plain language: A permanent governance update about one exact version of a node or relation.

CyberAlchemy Lab context: CyberAlchemy Lab keeps this event outside the semantic subject stream so governance owners cannot silently edit meaning.

Boundary: A governance event is not a semantic event, authority grant, promotion verdict, or replay source for semantic state.

## Schema-semantics coverage

The definition-level contract contains `9` closed record meanings, `8` cross-record invariants, and `12` required negative witnesses.

Executable status:

- JSON Schema: `not_evaluable_under_CA2-ROUTE-DEFINE`
- Negative fixtures: `requirements-authored_fixtures-not_implemented`

## Open questions

- `GON-OQ-001`: Which closed OntologyLifecycleState values represent creation, active use, retirement, and removal in semantic event payloads? Blocks: Executable node and relation JSON Schema. Owner: CyberAlchemy Lab ontology lifecycle owner.
- `GON-OQ-002`: Which typed rubric assesses EvidenceStrength for each evidence profile? Blocks: Cross-profile evidence-strength comparison, but not the definition-level distinction. Owner: CyberAlchemy Lab evidence owner.
- `GON-OQ-003`: Which exact closed typed-property schemas belong to each selected ontology profile? Blocks: Executable profile schemas. Owner: Each ontology-type profile owner.

## Drift audit

Selected-scope findings: `7`; open: `4`; handled: `3`.

- `DRIFT-GON-001` (`handled-in-pack`): The plan says semantic confidence, governance confidence, and evidence strength must remain distinct. Remediation: Use evidence_confidence, commitment_confidence, and evidence_strength in successor authored source. Treat semantic confidence and governance confidence as rejected aliases.
- `DRIFT-GON-002` (`open`): The source separates lifecycle axes but does not select the closed semantic lifecycle values for event payloads. Remediation: Resolve one exact lifecycle vocabulary before JSON Schema implementation; do not reuse package workflow status values implicitly.
- `DRIFT-GON-003` (`not_evaluable-under-current-route`): The current runtime schemas implement the thin mechanics witness and do not carry the complete selected governed-node facets. Remediation: Under a later CA2-ROUTE-IMPLEMENT authorization, replace or version the thin payload contract from schema-semantics.json and implement every NEG-GON witness.
- `DRIFT-GON-004` (`deferred-to-W7`): Existing CyberAlchemy-v2 ontology packages use divergent node fields, relation forms, lifecycle labels, and confidence shapes. Remediation: Inventory and map each package only after the governed-node witness is accepted; route unknown fields to TypedResidue.
- `DRIFT-GON-005` (`handled-by-exact-decision-reference`): The immutable proposal still says not-selected because it records its pre-decision candidate epoch. Remediation: Consumers must join the proposal to CAL-GONA-0005 rather than infer current selection from the proposal status field.
- `DRIFT-GON-006` (`open-nonblocking-for-candidate-pack`): No accepted Ontology Lifecycle Language Context View exists. Remediation: Keep ASD-STE100-style direct prose as a candidate presentation rule until a language context view is owner-selected.
- `DRIFT-GON-007` (`handled-in-pack-with-successor-remediation`): The proposal requires typed residue but its definition evidence selector list omits canonical CAV2-D18. Remediation: This pack binds CAV2-D18 explicitly. A future proposal successor or source-map refresh should add the selector without rewriting CAL-PROP-0004.

## W1 result

- `SWU-W1-001`: `validated-candidate-pending-definition-owner-review`
- `SWU-W1-002`: `definition-level-schema-contract-prepared_executable-schema-and-negative-fixtures-not_evaluable`
- `G-W1`: `BLOCK`

Remaining blockers:

- definition owner selection or admission absent
- executable schema and negative fixtures not authored
- OntologyLifecycleState vocabulary unresolved

## Claim ceiling

This pack proves current, dependency-closed candidate definitions and definition-level schema semantics only. It does not promote definitions, pass G-W1, implement schemas or fixtures, admit DomainSpec intent, authorize W2, or establish runtime conformance.
