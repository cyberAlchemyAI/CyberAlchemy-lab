use cal_ontology_context_adapters_v2::{
    GOVERNANCE_CONTEXT_ID, GOVERNANCE_CONTEXT_VERSION, ONTOLOGY_LIFECYCLE_CONTEXT_ID,
    ONTOLOGY_LIFECYCLE_CONTEXT_VERSION, V2_CONTEXT_MAP,
    governance_v2::{GovernanceContextAdapterV2, GovernanceProjectionRequestV2},
    ontology_lifecycle_v2::{ContextProjectionRequestV2, OntologyLifecycleContextAdapterV2},
};
use cal_ontology_lifecycle::*;
use std::{collections::BTreeMap, fs, path::Path};

fn identity() -> OntologySubjectIdentity {
    OntologySubjectIdentity {
        subject_id: "node-a".into(),
        ontology_id: "cal-d65-epoch-002-test".into(),
        subject_kind: SubjectKind::Node,
        type_ref: "test-node/v1".into(),
    }
}
fn semantic_event() -> SemanticEvent {
    let id = identity();
    let state = OntologySemanticState::Node(OntologyNodeSemanticState {
        identity: id.clone(),
        lifecycle: Lifecycle::Active,
        label: "Node A".into(),
        definition_or_claim: "A test node".into(),
        scope: "D65-S7".into(),
        semantic_components: vec![],
        semantic_definition_refs: vec![DefinitionReference {
            definition_id: "CAL-GON-D002".into(),
            selector_sha256: "b".repeat(64),
        }],
        typed_properties: TypedPropertySet {
            profile_ref: "test-empty-profile/v1".into(),
            values: BTreeMap::new(),
        },
        use_obligations: vec![],
        forbidden_collapse: vec![],
        profile_ref: "test-empty-profile/v1".into(),
    });
    let mut event = SemanticEvent {
        source_kind: SourceKind::CanonicalEvent,
        event_family: EventFamily::Semantic,
        event_id: "semantic-node-a".into(),
        event_digest: ZERO_DIGEST.into(),
        stream_id: id.semantic_stream_id(),
        subject_identity: id,
        previous_event_digest: None,
        semantic_cursor: 1,
        complete_resulting_semantic_state: state,
    };
    seal_semantic_event(&mut event).unwrap();
    event
}
fn governance_event(semantic: &SemanticEvent) -> GovernanceEvent {
    let exact = ExactSemanticEventReference {
        semantic_event_id: semantic.event_id.clone(),
        semantic_event_digest: semantic.event_digest.clone(),
        semantic_cursor: semantic.semantic_cursor,
    };
    let state = OntologyGovernanceState {
        semantic_ref: exact.clone(),
        provenance: vec![ProvenanceEntry {
            source_ref: "d65-s7-public-contract".into(),
            relation: "derived-from".into(),
            operation: "construct".into(),
            owner_route: "CA2-ROUTE-IMPLEMENT".into(),
            posture: "candidate".into(),
        }],
        owner_route: "test-owner".into(),
        candidate_or_maturity_status: "candidate".into(),
        promotion_state_or_handle: "not-promoted".into(),
        authority_kind_and_posture: AuthorityKindAndPosture {
            kind: "candidate".into(),
            posture: "non-authoritative".into(),
        },
        authority_effect: AuthorityEffect::None,
        evidence_confidence: ConfidenceReference {
            scheme_ref: "test/v1".into(),
            level: "supported".into(),
        },
        commitment_confidence: ConfidenceReference {
            scheme_ref: "test/v1".into(),
            level: "experimental".into(),
        },
        challenge_contract: ChallengeContract {
            challenge_response: "route".into(),
            valid_challenge_modes: vec![ChallengeMode::OwnerReview],
            contradiction_edges: vec![],
            validation_edges: vec![],
            owner_route: "test-owner".into(),
            resolution_gate: "G-D65-EPOCH-002-PRODUCT-APPROVAL".into(),
            blocking_questions: vec![],
            challenge_residue_route: "test-owner".into(),
        },
        residue: vec![],
        conflicts: vec![],
        drift_owner: "test-owner".into(),
        invalidation_route: "test-owner".into(),
    };
    let mut event = GovernanceEvent {
        source_kind: SourceKind::CanonicalEvent,
        event_family: EventFamily::Governance,
        event_id: "governance-node-a".into(),
        event_digest: ZERO_DIGEST.into(),
        stream_id: semantic.subject_identity.governance_stream_id(),
        semantic_ref: exact,
        governance_cursor: 1,
        previous_event_digest: None,
        complete_resulting_governance_state: state,
    };
    seal_governance_event(&mut event).unwrap();
    event
}
fn write<T: serde::Serialize>(dir: &Path, name: &str, value: &T) {
    fs::write(dir.join(name), canonical_json(value).unwrap()).unwrap();
}
fn fixture() -> (tempfile::TempDir, EventStore) {
    let temp = tempfile::tempdir().unwrap();
    let semantic_dir = temp.path().join("semantic");
    let governance_dir = temp.path().join("governance");
    fs::create_dir_all(&semantic_dir).unwrap();
    fs::create_dir_all(&governance_dir).unwrap();
    let semantic = semantic_event();
    let governance = governance_event(&semantic);
    write(&semantic_dir, "00000001-semantic.json", &semantic);
    write(&governance_dir, "00000001-governance.json", &governance);
    let store = EventStore::load(&semantic_dir, &governance_dir).unwrap();
    (temp, store)
}
fn selector() -> ContextSelector {
    ContextSelector {
        semantic_cursor: 1,
        required_subject_set: vec![identity()],
        governance_join_policy: GovernanceJoinPolicy::RequireExact,
        intended_use: "d65-s7-public-contract".into(),
        projection_profile: ProjectionProfile::TestCompleteV1,
    }
}
fn ontology_request() -> ContextProjectionRequestV2 {
    ContextProjectionRequestV2 {
        context_id: ONTOLOGY_LIFECYCLE_CONTEXT_ID.into(),
        context_version: ONTOLOGY_LIFECYCLE_CONTEXT_VERSION.into(),
        context_map_ref: V2_CONTEXT_MAP.map_ref.into(),
        direction: V2_CONTEXT_MAP.direction.into(),
        selector_ref: "d65-s7-selector".into(),
        selector: selector(),
    }
}
fn governance_request() -> GovernanceProjectionRequestV2 {
    GovernanceProjectionRequestV2 {
        context_id: GOVERNANCE_CONTEXT_ID.into(),
        context_version: GOVERNANCE_CONTEXT_VERSION.into(),
        context_map_ref: V2_CONTEXT_MAP.map_ref.into(),
        direction: V2_CONTEXT_MAP.direction.into(),
        selector_ref: "d65-s7-selector".into(),
        selector: selector(),
    }
}

#[test]
fn exact_v2_topology_is_public_and_enforced() {
    assert_eq!(
        V2_CONTEXT_MAP.source_context_ref,
        "cal.context.governance/v2"
    );
    assert_eq!(
        V2_CONTEXT_MAP.target_context_ref,
        "cal.context.ontology-lifecycle/v2"
    );
    let (_temp, store) = fixture();
    let mut wrong = ontology_request();
    wrong.context_map_ref = "cal.context-map.governance-ontology-lifecycle/v1".into();
    assert_eq!(
        OntologyLifecycleContextAdapterV2::new(&store)
            .project(&wrong)
            .unwrap_err()
            .code,
        "CONTEXT_MAP_MISMATCH"
    );
    let mut reverse = governance_request();
    reverse.direction = "target-to-source".into();
    assert_eq!(
        GovernanceContextAdapterV2::new(&store)
            .project(&reverse)
            .unwrap_err()
            .code,
        "CONTEXT_DIRECTION_MISMATCH"
    );
}
#[test]
fn both_contexts_share_the_exact_event_cut() {
    let (_temp, store) = fixture();
    let o = OntologyLifecycleContextAdapterV2::new(&store)
        .project(&ontology_request())
        .unwrap();
    let g = GovernanceContextAdapterV2::new(&store)
        .project(&governance_request())
        .unwrap();
    assert_eq!(o.source_cursor, g.source_cursor);
    assert_eq!(o.source_event_set_digest, g.source_event_set_digest);
    assert_eq!(o.projection, g.projection);
    assert_eq!(g.governed_nodes.len(), 1);
}
#[test]
fn projection_is_not_a_replay_source() {
    let (_temp, store) = fixture();
    let o = OntologyLifecycleContextAdapterV2::new(&store)
        .project(&ontology_request())
        .unwrap();
    assert!(!o.canonical_replay_source);
    assert_eq!(o.context_map_ref, V2_CONTEXT_MAP.map_ref);
}
#[test]
fn projection_has_no_authority_effect() {
    let (_temp, store) = fixture();
    let o = OntologyLifecycleContextAdapterV2::new(&store)
        .project(&ontology_request())
        .unwrap();
    let g = GovernanceContextAdapterV2::new(&store)
        .project(&governance_request())
        .unwrap();
    assert_eq!(o.authority_effect, AuthorityEffect::None);
    assert_eq!(g.authority_effect, AuthorityEffect::None);
}
