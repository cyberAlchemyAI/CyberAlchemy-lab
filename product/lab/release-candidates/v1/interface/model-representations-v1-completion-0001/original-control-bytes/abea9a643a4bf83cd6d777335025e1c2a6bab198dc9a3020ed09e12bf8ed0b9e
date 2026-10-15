pub use cal_ontology_lifecycle::*;

#[path = "../src/context_adapter.rs"]
mod context_adapter;
#[path = "../src/governance_context_adapter.rs"]
mod governance_context_adapter;

use context_adapter::{
    ContextProjectionRequest, ONTOLOGY_LIFECYCLE_CONTEXT_ID, ONTOLOGY_LIFECYCLE_CONTEXT_VERSION,
    OntologyLifecycleContextAdapter,
};
use governance_context_adapter::{
    ExactGovernanceProjectionRequest, GOVERNANCE_CONTEXT_ID, GOVERNANCE_CONTEXT_VERSION,
    GovernanceContextAdapter,
};
use std::collections::BTreeMap;
use std::fs;
use std::path::{Path, PathBuf};
use tempfile::TempDir;

struct Fixture {
    _temporary: TempDir,
    semantic: PathBuf,
    governance: PathBuf,
}

fn identity(kind: SubjectKind, id: &str, type_ref: &str) -> OntologySubjectIdentity {
    OntologySubjectIdentity {
        subject_id: id.to_owned(),
        ontology_id: "cal-d65-s7-test".to_owned(),
        subject_kind: kind,
        type_ref: type_ref.to_owned(),
    }
}

fn node_a() -> OntologySubjectIdentity {
    identity(SubjectKind::Node, "node-a", "test-node-type/v1")
}

fn node_b() -> OntologySubjectIdentity {
    identity(SubjectKind::Node, "node-b", "test-node-type/v1")
}

fn relation_ab() -> OntologySubjectIdentity {
    identity(
        SubjectKind::Relation,
        "relation-ab",
        "test-relation-type/v1",
    )
}

fn properties() -> TypedPropertySet {
    TypedPropertySet {
        profile_ref: "test-empty-profile/v1".to_owned(),
        values: BTreeMap::new(),
    }
}

fn node_state(identity: OntologySubjectIdentity, label: &str) -> OntologySemanticState {
    OntologySemanticState::Node(OntologyNodeSemanticState {
        identity,
        lifecycle: Lifecycle::Active,
        label: label.to_owned(),
        definition_or_claim: format!("{label} is a bounded ontology node."),
        scope: "D65-S7 context binding".to_owned(),
        semantic_components: vec![],
        semantic_definition_refs: vec![DefinitionReference {
            definition_id: "CAL-GON-D002".to_owned(),
            selector_sha256: "b".repeat(64),
        }],
        typed_properties: properties(),
        use_obligations: vec![],
        forbidden_collapse: vec![],
        profile_ref: "test-empty-profile/v1".to_owned(),
    })
}

fn relation_state() -> OntologySemanticState {
    OntologySemanticState::Relation(OntologyRelationSemanticState {
        identity: relation_ab(),
        lifecycle: Lifecycle::Active,
        source_node_id: "node-a".to_owned(),
        target_node_id: "node-b".to_owned(),
        direction: RelationDirection::Directed,
        typed_properties: properties(),
        forbidden_collapse: vec![],
    })
}

fn semantic_event(
    event_id: &str,
    cursor: u64,
    identity: OntologySubjectIdentity,
    state: OntologySemanticState,
) -> SemanticEvent {
    let mut event = SemanticEvent {
        source_kind: SourceKind::CanonicalEvent,
        event_family: EventFamily::Semantic,
        event_id: event_id.to_owned(),
        event_digest: ZERO_DIGEST.to_owned(),
        stream_id: identity.semantic_stream_id(),
        subject_identity: identity,
        previous_event_digest: None,
        semantic_cursor: cursor,
        complete_resulting_semantic_state: state,
    };
    seal_semantic_event(&mut event).expect("seal semantic event");
    event
}

fn exact_ref(event: &SemanticEvent) -> ExactSemanticEventReference {
    ExactSemanticEventReference {
        semantic_event_id: event.event_id.clone(),
        semantic_event_digest: event.event_digest.clone(),
        semantic_cursor: event.semantic_cursor,
    }
}

fn governance_state(reference: ExactSemanticEventReference) -> OntologyGovernanceState {
    OntologyGovernanceState {
        semantic_ref: reference,
        provenance: vec![ProvenanceEntry {
            source_ref: "d65-s7-context-binding".to_owned(),
            relation: "derived-from".to_owned(),
            operation: "construct".to_owned(),
            owner_route: "CA2-ROUTE-IMPLEMENT".to_owned(),
            posture: "candidate".to_owned(),
        }],
        owner_route: "ontology-integration-implementation-owner".to_owned(),
        candidate_or_maturity_status: "candidate".to_owned(),
        promotion_state_or_handle: "not-promoted".to_owned(),
        authority_kind_and_posture: AuthorityKindAndPosture {
            kind: "candidate".to_owned(),
            posture: "non-authoritative".to_owned(),
        },
        authority_effect: AuthorityEffect::None,
        evidence_confidence: ConfidenceReference {
            scheme_ref: "test-confidence/v1".to_owned(),
            level: "supported".to_owned(),
        },
        commitment_confidence: ConfidenceReference {
            scheme_ref: "test-confidence/v1".to_owned(),
            level: "experimental".to_owned(),
        },
        challenge_contract: ChallengeContract {
            challenge_response: "Route supported challenges to the owner.".to_owned(),
            valid_challenge_modes: vec![ChallengeMode::OwnerReview],
            contradiction_edges: vec![],
            validation_edges: vec![],
            owner_route: "ontology-integration-implementation-owner".to_owned(),
            resolution_gate: "G-D65-CONFORMANCE".to_owned(),
            blocking_questions: vec![],
            challenge_residue_route: "independent-integration-conformance-owner".to_owned(),
        },
        residue: vec![],
        conflicts: vec![],
        drift_owner: "ontology-integration-implementation-owner".to_owned(),
        invalidation_route: "ontology-integration-implementation-owner".to_owned(),
    }
}

fn governance_event(event_id: &str, cursor: u64, semantic: &SemanticEvent) -> GovernanceEvent {
    let reference = exact_ref(semantic);
    let mut event = GovernanceEvent {
        source_kind: SourceKind::CanonicalEvent,
        event_family: EventFamily::Governance,
        event_id: event_id.to_owned(),
        event_digest: ZERO_DIGEST.to_owned(),
        stream_id: semantic.subject_identity.governance_stream_id(),
        semantic_ref: reference.clone(),
        governance_cursor: cursor,
        previous_event_digest: None,
        complete_resulting_governance_state: governance_state(reference),
    };
    seal_governance_event(&mut event).expect("seal governance event");
    event
}

fn write_event<T: serde::Serialize>(directory: &Path, cursor: u64, id: &str, event: &T) {
    fs::write(
        directory.join(format!("{cursor:08}-{id}.json")),
        canonical_json(event).expect("canonical event"),
    )
    .expect("write event");
}

fn fixture(include_node_a_governance: bool) -> Fixture {
    let temporary = tempfile::tempdir().expect("temporary fixture");
    let semantic = temporary.path().join("semantic-events");
    let governance = temporary.path().join("governance-events");
    fs::create_dir_all(&semantic).expect("semantic directory");
    fs::create_dir_all(&governance).expect("governance directory");

    let semantic_events = vec![
        semantic_event(
            "semantic-node-a",
            1,
            node_a(),
            node_state(node_a(), "Node A"),
        ),
        semantic_event(
            "semantic-node-b",
            2,
            node_b(),
            node_state(node_b(), "Node B"),
        ),
        semantic_event("semantic-relation-ab", 3, relation_ab(), relation_state()),
    ];
    for event in &semantic_events {
        write_event(&semantic, event.semantic_cursor, &event.event_id, event);
    }

    let selected = if include_node_a_governance {
        vec![
            &semantic_events[0],
            &semantic_events[1],
            &semantic_events[2],
        ]
    } else {
        vec![&semantic_events[1], &semantic_events[2]]
    };
    for (index, semantic_event) in selected.into_iter().enumerate() {
        let cursor = index as u64 + 1;
        let id = format!("governance-{}", semantic_event.subject_identity.subject_id);
        let event = governance_event(&id, cursor, semantic_event);
        write_event(&governance, cursor, &id, &event);
    }

    Fixture {
        _temporary: temporary,
        semantic,
        governance,
    }
}

fn selector() -> ContextSelector {
    ContextSelector {
        semantic_cursor: 3,
        required_subject_set: vec![node_a(), node_b(), relation_ab()],
        governance_join_policy: GovernanceJoinPolicy::RequireExact,
        intended_use: "d65-s7-context-binding".to_owned(),
        projection_profile: ProjectionProfile::TestCompleteV1,
    }
}

fn ontology_request() -> ContextProjectionRequest {
    ContextProjectionRequest {
        context_id: ONTOLOGY_LIFECYCLE_CONTEXT_ID.to_owned(),
        context_version: ONTOLOGY_LIFECYCLE_CONTEXT_VERSION.to_owned(),
        selector_ref: "d65-s7-selector".to_owned(),
        selector: selector(),
    }
}

fn governance_request() -> ExactGovernanceProjectionRequest {
    ExactGovernanceProjectionRequest {
        context_id: GOVERNANCE_CONTEXT_ID.to_owned(),
        context_version: GOVERNANCE_CONTEXT_VERSION.to_owned(),
        selector_ref: "d65-s7-selector".to_owned(),
        selector: selector(),
    }
}

#[test]
fn both_contexts_share_one_exact_cut() {
    let fixture = fixture(true);
    let store = EventStore::load(&fixture.semantic, &fixture.governance).expect("event store");
    let ontology = OntologyLifecycleContextAdapter::new(&store)
        .project(&ontology_request())
        .expect("ontology context projection");
    let governance = GovernanceContextAdapter::new(&store)
        .project(&governance_request())
        .expect("governance context projection");

    assert_eq!(ontology.source_cursor, 3);
    assert_eq!(governance.source_cursor, ontology.source_cursor);
    assert_eq!(
        governance.source_event_set_digest,
        ontology.source_event_set_digest
    );
    assert_eq!(governance.projection, ontology.projection);
    assert_eq!(governance.governed_nodes.len(), 2);
    assert!(
        governance
            .governed_nodes
            .iter()
            .all(|node| node.context_selector_ref.as_deref() == Some("d65-s7-selector"))
    );
    assert_eq!(ontology.authority_effect, AuthorityEffect::None);
    assert_eq!(governance.authority_effect, AuthorityEffect::None);
}

#[test]
fn context_projection_never_becomes_replay_source() {
    let fixture = fixture(true);
    let store = EventStore::load(&fixture.semantic, &fixture.governance).expect("event store");
    let projection = OntologyLifecycleContextAdapter::new(&store)
        .project(&ontology_request())
        .expect("context projection");
    assert!(!projection.canonical_replay_source);

    let replay = tempfile::tempdir().expect("replay directory");
    let semantic = replay.path().join("semantic-events");
    let governance = replay.path().join("governance-events");
    fs::create_dir_all(&semantic).expect("semantic directory");
    fs::create_dir_all(&governance).expect("governance directory");
    write_event(&semantic, 1, "context-projection", &projection);
    assert_eq!(
        EventStore::load(&semantic, &governance)
            .expect_err("projection must not decode as a replay event")
            .code,
        "NONCANONICAL_REPLAY_SOURCE"
    );
}

#[test]
fn missing_exact_governance_join_fails_closed() {
    let fixture = fixture(false);
    let store = EventStore::load(&fixture.semantic, &fixture.governance).expect("event store");
    assert_eq!(
        GovernanceContextAdapter::new(&store)
            .project(&governance_request())
            .expect_err("missing exact governance state must fail")
            .code,
        "EXACT_GOVERNANCE_STATE_MISSING"
    );
}
