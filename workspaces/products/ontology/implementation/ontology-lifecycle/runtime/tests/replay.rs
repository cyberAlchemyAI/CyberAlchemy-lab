use cal_ontology_lifecycle::{
    AppendGovernanceEventRequest, AppendSemanticEventRequest, AuthorityEffect,
    AuthorityKindAndPosture, ChallengeContract, ChallengeMode, ConfidenceReference,
    ContextSelector, DefinitionReference, EventFamily, EventStore, EventTail,
    ExactSemanticEventReference, GovernanceEvent, GovernanceJoinPolicy, Lifecycle,
    OntologyGovernanceState, OntologyNodeSemanticState, OntologyRelationSemanticState,
    OntologySemanticState, OntologySubjectIdentity, ProjectionProfile, ProvenanceEntry,
    RelationDirection, SemanticEvent, SourceKind, SubjectKind, TypedPropertySet, ZERO_DIGEST,
    canonical_json, human_projection, machine_projection, seal_governance_event,
    seal_semantic_event,
};
use serde_json::json;
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
        ontology_id: "cal-test".to_owned(),
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

fn empty_properties() -> TypedPropertySet {
    TypedPropertySet {
        profile_ref: "test-empty-profile/v1".to_owned(),
        values: BTreeMap::new(),
    }
}

fn node_state(
    identity: OntologySubjectIdentity,
    lifecycle: Lifecycle,
    label: &str,
) -> OntologySemanticState {
    OntologySemanticState::Node(OntologyNodeSemanticState {
        identity,
        lifecycle,
        label: label.to_owned(),
        definition_or_claim: format!("{label} is a bounded ontology node."),
        scope: "W5 runtime conformance".to_owned(),
        semantic_components: vec![],
        semantic_definition_refs: vec![DefinitionReference {
            definition_id: "CAL-GON-D002".to_owned(),
            selector_sha256: "b".repeat(64),
        }],
        typed_properties: empty_properties(),
        use_obligations: vec![],
        forbidden_collapse: vec![],
        profile_ref: "test-empty-profile/v1".to_owned(),
    })
}

fn relation_state(lifecycle: Lifecycle, target: &str) -> OntologySemanticState {
    OntologySemanticState::Relation(OntologyRelationSemanticState {
        identity: relation_ab(),
        lifecycle,
        source_node_id: "node-a".to_owned(),
        target_node_id: target.to_owned(),
        direction: RelationDirection::Directed,
        typed_properties: empty_properties(),
        forbidden_collapse: vec![],
    })
}

fn semantic_event(
    event_id: &str,
    cursor: u64,
    identity: OntologySubjectIdentity,
    previous_event_digest: Option<String>,
    state: OntologySemanticState,
) -> SemanticEvent {
    let mut event = SemanticEvent {
        source_kind: SourceKind::CanonicalEvent,
        event_family: EventFamily::Semantic,
        event_id: event_id.to_owned(),
        event_digest: ZERO_DIGEST.to_owned(),
        stream_id: identity.semantic_stream_id(),
        subject_identity: identity,
        previous_event_digest,
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
            source_ref: "fixture-w5".to_owned(),
            relation: "derived-from".to_owned(),
            operation: "construct".to_owned(),
            owner_route: "CA2-ROUTE-IMPLEMENT".to_owned(),
            posture: "candidate".to_owned(),
        }],
        owner_route: "CyberAlchemy-Lab-ontology-owner".to_owned(),
        candidate_or_maturity_status: "candidate".to_owned(),
        promotion_state_or_handle: "not-promoted".to_owned(),
        authority_kind_and_posture: AuthorityKindAndPosture {
            kind: "test-candidate".to_owned(),
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
            valid_challenge_modes: vec![
                ChallengeMode::Evidence,
                ChallengeMode::Contradiction,
                ChallengeMode::OwnerReview,
            ],
            contradiction_edges: vec![],
            validation_edges: vec![],
            owner_route: "CyberAlchemy-Lab-ontology-owner".to_owned(),
            resolution_gate: "G-W6".to_owned(),
            blocking_questions: vec![],
            challenge_residue_route: "CyberAlchemy-Lab-residue-owner".to_owned(),
        },
        residue: vec![],
        conflicts: vec![],
        drift_owner: "CyberAlchemy-Lab-ontology-owner".to_owned(),
        invalidation_route: "CyberAlchemy-Lab-ontology-owner".to_owned(),
    }
}

fn governance_event(
    event_id: &str,
    cursor: u64,
    semantic: &SemanticEvent,
    previous_event_digest: Option<String>,
) -> GovernanceEvent {
    let reference = exact_ref(semantic);
    let mut event = GovernanceEvent {
        source_kind: SourceKind::CanonicalEvent,
        event_family: EventFamily::Governance,
        event_id: event_id.to_owned(),
        event_digest: ZERO_DIGEST.to_owned(),
        stream_id: semantic.subject_identity.governance_stream_id(),
        semantic_ref: reference.clone(),
        governance_cursor: cursor,
        previous_event_digest,
        complete_resulting_governance_state: governance_state(reference),
    };
    seal_governance_event(&mut event).expect("seal governance event");
    event
}

fn write_semantic(directory: &Path, event: &SemanticEvent) -> PathBuf {
    let path = directory.join(format!(
        "{:08}-{}.json",
        event.semantic_cursor, event.event_id
    ));
    fs::write(
        &path,
        canonical_json(event).expect("canonical semantic event"),
    )
    .expect("write semantic event");
    path
}

fn write_governance(directory: &Path, event: &GovernanceEvent) -> PathBuf {
    let path = directory.join(format!(
        "{:08}-{}.json",
        event.governance_cursor, event.event_id
    ));
    fs::write(
        &path,
        canonical_json(event).expect("canonical governance event"),
    )
    .expect("write governance event");
    path
}

fn read_semantic(path: &Path) -> SemanticEvent {
    serde_json::from_slice(&fs::read(path).expect("semantic bytes")).expect("semantic event")
}

fn read_governance(path: &Path) -> GovernanceEvent {
    serde_json::from_slice(&fs::read(path).expect("governance bytes")).expect("governance event")
}

fn make_fixture() -> Fixture {
    let temporary = tempfile::tempdir().expect("temporary fixture");
    let semantic = temporary.path().join("semantic-events");
    let governance = temporary.path().join("governance-events");
    fs::create_dir_all(&semantic).expect("semantic directory");
    fs::create_dir_all(&governance).expect("governance directory");

    let first = semantic_event(
        "semantic-0001",
        1,
        node_a(),
        None,
        node_state(node_a(), Lifecycle::Active, "Node A"),
    );
    let second = semantic_event(
        "semantic-0002",
        2,
        node_b(),
        None,
        node_state(node_b(), Lifecycle::Active, "Node B"),
    );
    let third = semantic_event(
        "semantic-0003",
        3,
        relation_ab(),
        None,
        relation_state(Lifecycle::Active, "node-b"),
    );
    let fourth = semantic_event(
        "semantic-0004",
        4,
        node_a(),
        Some(first.event_digest.clone()),
        node_state(node_a(), Lifecycle::Active, "Node A revised"),
    );
    for event in [&first, &second, &third, &fourth] {
        write_semantic(&semantic, event);
    }
    for event in [
        governance_event("governance-0001", 1, &fourth, None),
        governance_event("governance-0002", 2, &second, None),
        governance_event("governance-0003", 3, &third, None),
    ] {
        write_governance(&governance, &event);
    }
    Fixture {
        _temporary: temporary,
        semantic,
        governance,
    }
}

fn load_fixture(fixture: &Fixture) -> EventStore {
    EventStore::load(&fixture.semantic, &fixture.governance).expect("fixture must load")
}

fn selector(cursor: u64) -> ContextSelector {
    ContextSelector {
        semantic_cursor: cursor,
        required_subject_set: vec![node_a(), node_b(), relation_ab()],
        governance_join_policy: GovernanceJoinPolicy::RequireExact,
        intended_use: "w5-validation".to_owned(),
        projection_profile: ProjectionProfile::TestCompleteV1,
    }
}

fn semantic_path(fixture: &Fixture, cursor: u64, event_id: &str) -> PathBuf {
    fixture
        .semantic
        .join(format!("{cursor:08}-{event_id}.json"))
}

fn governance_path(fixture: &Fixture, cursor: u64, event_id: &str) -> PathBuf {
    fixture
        .governance
        .join(format!("{cursor:08}-{event_id}.json"))
}

fn reseal_and_write_semantic(path: &Path, event: &mut SemanticEvent) {
    seal_semantic_event(event).expect("reseal semantic event");
    fs::write(
        path,
        canonical_json(event).expect("canonical semantic event"),
    )
    .expect("write semantic event");
}

fn reseal_and_write_governance(path: &Path, event: &mut GovernanceEvent) {
    seal_governance_event(event).expect("reseal governance event");
    fs::write(
        path,
        canonical_json(event).expect("canonical governance event"),
    )
    .expect("write governance event");
}

fn rebind_governance(
    fixture: &Fixture,
    governance_cursor: u64,
    governance_event_id: &str,
    semantic: &SemanticEvent,
) {
    let path = governance_path(fixture, governance_cursor, governance_event_id);
    let mut event = read_governance(&path);
    event.semantic_ref = exact_ref(semantic);
    event.complete_resulting_governance_state.semantic_ref = event.semantic_ref.clone();
    reseal_and_write_governance(&path, &mut event);
}

#[test]
fn deterministic_rebuilds_match_for_all_read_models() {
    let fixture = make_fixture();
    let first = load_fixture(&fixture);
    let second = load_fixture(&fixture);
    let first_cut = first.ontology_at(4).expect("first cut");
    let second_cut = second.ontology_at(4).expect("second cut");
    assert_eq!(first_cut, second_cut);
    assert_eq!(
        machine_projection(&first_cut).expect("machine projection"),
        machine_projection(&second_cut).expect("machine projection")
    );
    assert_eq!(human_projection(&first_cut), human_projection(&second_cut));

    let first_view = first
        .governed_node_view(&node_a(), 4, None)
        .expect("governed view");
    let second_view = second
        .governed_node_view(&node_a(), 4, None)
        .expect("governed view");
    assert_eq!(first_view, second_view);

    let first_context = first
        .context_projection("selector-w5", &selector(4))
        .expect("context projection");
    let second_context = second
        .context_projection("selector-w5", &selector(4))
        .expect("context projection");
    assert_eq!(first_context, second_context);
}

#[test]
fn latest_snapshots_are_per_subject_and_keep_tombstones() {
    let fixture = make_fixture();
    let mut store = load_fixture(&fixture);
    let latest = store.semantic_events()[3].event.clone();
    let removed = semantic_event(
        "semantic-0005",
        5,
        node_a(),
        Some(latest.event_digest),
        node_state(node_a(), Lifecycle::Removed, "Node A tombstone"),
    );
    store
        .append_semantic_batch(
            &fixture.semantic,
            vec![AppendSemanticEventRequest {
                expected_stream_version: 2,
                event: removed,
            }],
        )
        .expect("append removal");
    let snapshots = store.latest_subject_snapshots(5).expect("snapshots");
    assert_eq!(snapshots.len(), 3);
    let node = snapshots
        .iter()
        .find(|snapshot| snapshot.identity == node_a())
        .expect("node A snapshot");
    assert_eq!(node.semantic_state.lifecycle(), Lifecycle::Removed);
    assert!(
        store
            .ontology_at(5)
            .expect_err("active relation must fail after endpoint removal")
            .code
            == "RELATION_ENDPOINT_INTEGRITY"
    );
}

#[test]
fn checkpoint_tail_matches_empty_rebuild_and_rejects_drift() {
    let fixture = make_fixture();
    let store = load_fixture(&fixture);
    let checkpoint = store.checkpoint_at(3).expect("checkpoint");
    assert_eq!(
        store
            .ontology_from_checkpoint(&checkpoint, 4)
            .expect("checkpoint plus tail"),
        store.ontology_at(4).expect("empty rebuild")
    );
    let mut drifted = checkpoint;
    drifted.source_event_set_digest = "0".repeat(64);
    assert_eq!(
        store
            .ontology_from_checkpoint(&drifted, 4)
            .expect_err("drifted checkpoint must fail")
            .code,
        "CHECKPOINT_INVALID"
    );
}

#[test]
fn file_tail_loads_only_after_the_checkpoint_and_preserves_chain_validation() {
    let fixture = make_fixture();
    let store = load_fixture(&fixture);
    let checkpoint = store.checkpoint_at(3).expect("checkpoint");
    let boundary = store.tail_boundary_at(3, 0).expect("tail boundary");
    let tail = EventTail::load(&fixture.semantic, &fixture.governance, boundary, 4, 3)
        .expect("validated tail");
    assert_eq!(tail.semantic_events().len(), 1);
    assert_eq!(tail.governance_events().len(), 3);
    assert_eq!(tail.target_governance_cursor(), 3);
    assert_eq!(
        tail.ontology_from_checkpoint(&checkpoint)
            .expect("checkpoint plus file tail"),
        store.ontology_at(4).expect("full replay")
    );

    let corrupt_fixture = make_fixture();
    let corrupt_store = load_fixture(&corrupt_fixture);
    let corrupt_boundary = corrupt_store.tail_boundary_at(3, 0).expect("tail boundary");
    let path = semantic_path(&corrupt_fixture, 4, "semantic-0004");
    let mut event = read_semantic(&path);
    event.previous_event_digest = Some("0".repeat(64));
    reseal_and_write_semantic(&path, &mut event);
    assert_eq!(
        EventTail::load(
            &corrupt_fixture.semantic,
            &corrupt_fixture.governance,
            corrupt_boundary,
            4,
            3,
        )
        .expect_err("broken prefix-to-tail chain must fail")
        .code,
        "SUBJECT_EVENT_CHAIN_BROKEN"
    );
}

#[test]
fn event_digest_contract_is_verified_and_non_vacuous() {
    let fixture = make_fixture();
    let path = semantic_path(&fixture, 2, "semantic-0002");
    let mut event = read_semantic(&path);
    if let OntologySemanticState::Node(state) = &mut event.complete_resulting_semantic_state {
        state.label = "Mutated without resealing".to_owned();
    }
    fs::write(&path, canonical_json(&event).expect("canonical bytes")).expect("write mutation");
    assert_eq!(
        EventStore::load(&fixture.semantic, &fixture.governance)
            .expect_err("stale digest must fail")
            .code,
        "EVENT_DIGEST_MISMATCH"
    );
}

#[test]
fn noncanonical_json_and_projection_replay_sources_fail_closed() {
    let fixture = make_fixture();
    let path = semantic_path(&fixture, 1, "semantic-0001");
    let mut bytes = fs::read(&path).expect("event bytes");
    bytes.push(b' ');
    fs::write(&path, bytes).expect("write noncanonical bytes");
    assert_eq!(
        EventStore::load(&fixture.semantic, &fixture.governance)
            .expect_err("noncanonical bytes must fail")
            .code,
        "NON_CANONICAL_JSON"
    );

    let fixture = make_fixture();
    let snapshot = load_fixture(&fixture)
        .latest_subject_snapshots(4)
        .expect("snapshot")
        .remove(0);
    fs::write(
        fixture.semantic.join("00000005-projection.json"),
        machine_projection(&snapshot).expect("projection bytes"),
    )
    .expect("write projection as replay input");
    assert_eq!(
        EventStore::load(&fixture.semantic, &fixture.governance)
            .expect_err("projection replay must fail")
            .code,
        "NONCANONICAL_REPLAY_SOURCE"
    );
}

#[test]
fn cursor_identity_stream_and_chain_mutations_each_fail() {
    let fixture = make_fixture();
    let path = semantic_path(&fixture, 2, "semantic-0002");
    let mut event = read_semantic(&path);
    event.semantic_cursor = 3;
    reseal_and_write_semantic(&path, &mut event);
    assert_eq!(
        EventStore::load(&fixture.semantic, &fixture.governance)
            .expect_err("cursor gap must fail")
            .code,
        "GRAPH_CURSOR_NOT_CONTIGUOUS"
    );

    let fixture = make_fixture();
    let path = semantic_path(&fixture, 2, "semantic-0002");
    let mut event = read_semantic(&path);
    event.event_id = "semantic-0001".to_owned();
    reseal_and_write_semantic(&path, &mut event);
    assert_eq!(
        EventStore::load(&fixture.semantic, &fixture.governance)
            .expect_err("duplicate event ID must fail")
            .code,
        "SEMANTIC_EVENT_ID_DUPLICATE"
    );

    let fixture = make_fixture();
    let path = semantic_path(&fixture, 4, "semantic-0004");
    let mut event = read_semantic(&path);
    event.stream_id = node_b().semantic_stream_id();
    reseal_and_write_semantic(&path, &mut event);
    assert_eq!(
        EventStore::load(&fixture.semantic, &fixture.governance)
            .expect_err("stream identity must fail")
            .code,
        "SUBJECT_STREAM_ID_MISMATCH"
    );

    let fixture = make_fixture();
    let path = semantic_path(&fixture, 4, "semantic-0004");
    let mut event = read_semantic(&path);
    event.previous_event_digest = Some("f".repeat(64));
    reseal_and_write_semantic(&path, &mut event);
    assert_eq!(
        EventStore::load(&fixture.semantic, &fixture.governance)
            .expect_err("chain continuity must fail")
            .code,
        "SUBJECT_EVENT_CHAIN_BROKEN"
    );
}

#[test]
fn resulting_state_identity_kind_and_closed_properties_fail_closed() {
    let fixture = make_fixture();
    let path = semantic_path(&fixture, 2, "semantic-0002");
    let mut event = read_semantic(&path);
    if let OntologySemanticState::Node(state) = &mut event.complete_resulting_semantic_state {
        state.identity = node_a();
    }
    reseal_and_write_semantic(&path, &mut event);
    assert_eq!(
        EventStore::load(&fixture.semantic, &fixture.governance)
            .expect_err("state identity mismatch must fail")
            .code,
        "RESULTING_STATE_IDENTITY_MISMATCH"
    );

    let fixture = make_fixture();
    let path = semantic_path(&fixture, 2, "semantic-0002");
    let mut event = read_semantic(&path);
    if let OntologySemanticState::Node(state) = &mut event.complete_resulting_semantic_state {
        state.identity.subject_kind = SubjectKind::Relation;
        event.subject_identity.subject_kind = SubjectKind::Relation;
        event.stream_id = event.subject_identity.semantic_stream_id();
    }
    reseal_and_write_semantic(&path, &mut event);
    assert_eq!(
        EventStore::load(&fixture.semantic, &fixture.governance)
            .expect_err("node/relation kind collapse must fail")
            .code,
        "SUBJECT_KIND_MISMATCH"
    );

    let fixture = make_fixture();
    let path = semantic_path(&fixture, 2, "semantic-0002");
    let mut event = read_semantic(&path);
    if let OntologySemanticState::Node(state) = &mut event.complete_resulting_semantic_state {
        state
            .typed_properties
            .values
            .insert("unknown".to_owned(), json!(true));
    }
    reseal_and_write_semantic(&path, &mut event);
    assert_eq!(
        EventStore::load(&fixture.semantic, &fixture.governance)
            .expect_err("untyped property must fail")
            .code,
        "UNTYPED_RESIDUE"
    );
}

#[test]
fn lifecycle_creation_and_terminal_removal_are_enforced() {
    let fixture = make_fixture();
    let path = semantic_path(&fixture, 1, "semantic-0001");
    let mut event = read_semantic(&path);
    if let OntologySemanticState::Node(state) = &mut event.complete_resulting_semantic_state {
        state.lifecycle = Lifecycle::Retired;
    }
    reseal_and_write_semantic(&path, &mut event);
    assert_eq!(
        EventStore::load(&fixture.semantic, &fixture.governance)
            .expect_err("creation must produce active")
            .code,
        "LIFECYCLE_TRANSITION_INVALID"
    );

    let fixture = make_fixture();
    let store = load_fixture(&fixture);
    let current = store.semantic_events()[3].event.clone();
    let removed = semantic_event(
        "semantic-0005",
        5,
        node_a(),
        Some(current.event_digest),
        node_state(node_a(), Lifecycle::Removed, "Node A tombstone"),
    );
    let reactivated = semantic_event(
        "semantic-0006",
        6,
        node_a(),
        Some(removed.event_digest.clone()),
        node_state(node_a(), Lifecycle::Active, "Invalid return"),
    );
    write_semantic(&fixture.semantic, &removed);
    write_semantic(&fixture.semantic, &reactivated);
    assert_eq!(
        EventStore::load(&fixture.semantic, &fixture.governance)
            .expect_err("removed is terminal")
            .code,
        "LIFECYCLE_TRANSITION_INVALID"
    );
}

#[test]
fn missing_retired_and_removed_relation_endpoints_fail_closed() {
    let fixture = make_fixture();
    let path = semantic_path(&fixture, 3, "semantic-0003");
    let mut event = read_semantic(&path);
    event.complete_resulting_semantic_state = relation_state(Lifecycle::Active, "missing-node");
    reseal_and_write_semantic(&path, &mut event);
    rebind_governance(&fixture, 3, "governance-0003", &event);
    let store = EventStore::load(&fixture.semantic, &fixture.governance).expect("history loads");
    assert_eq!(
        store
            .ontology_at(4)
            .expect_err("missing endpoint must fail")
            .code,
        "RELATION_ENDPOINT_INTEGRITY"
    );

    for lifecycle in [Lifecycle::Retired, Lifecycle::Removed] {
        let fixture = make_fixture();
        let path = semantic_path(&fixture, 4, "semantic-0004");
        let mut event = read_semantic(&path);
        if let OntologySemanticState::Node(state) = &mut event.complete_resulting_semantic_state {
            state.lifecycle = lifecycle;
        }
        reseal_and_write_semantic(&path, &mut event);
        rebind_governance(&fixture, 1, "governance-0001", &event);
        let store = EventStore::load(&fixture.semantic, &fixture.governance)
            .expect("semantic history remains valid");
        assert_eq!(
            store
                .ontology_at(4)
                .expect_err("inactive endpoint must fail")
                .code,
            "RELATION_ENDPOINT_INTEGRITY"
        );
    }
}

#[test]
fn exact_governance_reference_mutations_each_fail() {
    for field in ["id", "digest", "cursor"] {
        let fixture = make_fixture();
        let path = governance_path(&fixture, 2, "governance-0002");
        let mut event = read_governance(&path);
        match field {
            "id" => event.semantic_ref.semantic_event_id = "missing-event".to_owned(),
            "digest" => event.semantic_ref.semantic_event_digest = "f".repeat(64),
            "cursor" => event.semantic_ref.semantic_cursor = 1,
            _ => unreachable!(),
        }
        event.complete_resulting_governance_state.semantic_ref = event.semantic_ref.clone();
        reseal_and_write_governance(&path, &mut event);
        let failure = EventStore::load(&fixture.semantic, &fixture.governance)
            .expect_err("exact tuple mutation must fail");
        assert_eq!(
            failure.code,
            if field == "id" {
                "GOVERNANCE_REFERENCE_MISSING"
            } else {
                "GOVERNANCE_REFERENCE_MISMATCH"
            }
        );
    }
}

#[test]
fn complete_governance_state_and_challenge_contract_are_non_vacuous() {
    let fixture = make_fixture();
    let path = governance_path(&fixture, 2, "governance-0002");
    let mut event = read_governance(&path);
    event
        .complete_resulting_governance_state
        .semantic_ref
        .semantic_event_digest = "f".repeat(64);
    reseal_and_write_governance(&path, &mut event);
    assert_eq!(
        EventStore::load(&fixture.semantic, &fixture.governance)
            .expect_err("outer/state reference mismatch must fail")
            .code,
        "GOVERNANCE_STATE_REFERENCE_MISMATCH"
    );

    let fixture = make_fixture();
    let path = governance_path(&fixture, 2, "governance-0002");
    let mut event = read_governance(&path);
    event
        .complete_resulting_governance_state
        .challenge_contract
        .valid_challenge_modes = vec![ChallengeMode::Evidence, ChallengeMode::Evidence];
    reseal_and_write_governance(&path, &mut event);
    assert_eq!(
        EventStore::load(&fixture.semantic, &fixture.governance)
            .expect_err("duplicate challenge mode must fail")
            .code,
        "CHALLENGE_MODES_INVALID"
    );

    let fixture = make_fixture();
    let path = governance_path(&fixture, 2, "governance-0002");
    let mut value: serde_json::Value =
        serde_json::from_slice(&fs::read(&path).expect("governance bytes"))
            .expect("governance JSON");
    value.as_object_mut().expect("governance object").insert(
        "semantic_state_patch".to_owned(),
        json!({"label":"forbidden"}),
    );
    fs::write(
        &path,
        format!("{}\n", serde_json::to_string(&value).expect("JSON")),
    )
    .expect("write unknown field");
    assert_eq!(
        EventStore::load(&fixture.semantic, &fixture.governance)
            .expect_err("governance semantic patch must fail")
            .code,
        "GOVERNANCE_EVENT_DECODE_FAILED"
    );
}

#[test]
fn event_identity_is_unique_across_stream_families() {
    let fixture = make_fixture();
    let path = governance_path(&fixture, 1, "governance-0001");
    let mut event = read_governance(&path);
    event.event_id = "semantic-0001".to_owned();
    reseal_and_write_governance(&path, &mut event);
    assert_eq!(
        EventStore::load(&fixture.semantic, &fixture.governance)
            .expect_err("global event identity must be unique")
            .code,
        "GLOBAL_EVENT_ID_DUPLICATE"
    );
}

#[test]
fn expected_version_and_atomic_semantic_batch_are_enforced() {
    let fixture = make_fixture();
    let mut store = load_fixture(&fixture);
    let before = fs::read_dir(&fixture.semantic)
        .expect("semantic directory")
        .count();
    let current = store.semantic_events()[1].event.clone();
    let event = semantic_event(
        "semantic-0005",
        5,
        node_b(),
        Some(current.event_digest),
        node_state(node_b(), Lifecycle::Active, "Node B revised"),
    );
    assert_eq!(
        store
            .append_semantic_batch(
                &fixture.semantic,
                vec![AppendSemanticEventRequest {
                    expected_stream_version: 9,
                    event,
                }],
            )
            .expect_err("wrong expected version must fail")
            .code,
        "EXPECTED_STREAM_VERSION_MISMATCH"
    );
    assert_eq!(
        fs::read_dir(&fixture.semantic)
            .expect("semantic directory")
            .count(),
        before
    );

    let current_b = store.semantic_events()[1].event.clone();
    let current_a = store.semantic_events()[3].event.clone();
    let first = semantic_event(
        "semantic-0005",
        5,
        node_b(),
        Some(current_b.event_digest),
        node_state(node_b(), Lifecycle::Active, "Node B revised"),
    );
    let second = semantic_event(
        "semantic-0006",
        6,
        node_a(),
        Some("f".repeat(64)),
        node_state(node_a(), Lifecycle::Active, "Node A invalid tail"),
    );
    assert_eq!(
        store
            .append_semantic_batch(
                &fixture.semantic,
                vec![
                    AppendSemanticEventRequest {
                        expected_stream_version: 1,
                        event: first,
                    },
                    AppendSemanticEventRequest {
                        expected_stream_version: 2,
                        event: second,
                    },
                ],
            )
            .expect_err("invalid second event must reject whole batch")
            .code,
        "SUBJECT_EVENT_CHAIN_BROKEN"
    );
    assert_eq!(
        fs::read_dir(&fixture.semantic)
            .expect("semantic directory")
            .count(),
        before
    );
    assert_eq!(current_a.semantic_cursor, 4);
}

#[test]
fn valid_semantic_and_governance_appends_are_immediately_replayable() {
    let fixture = make_fixture();
    let mut store = load_fixture(&fixture);
    let current = store.semantic_events()[1].event.clone();
    let event = semantic_event(
        "semantic-0005",
        5,
        node_b(),
        Some(current.event_digest),
        node_state(node_b(), Lifecycle::Active, "Node B revised"),
    );
    let receipts = store
        .append_semantic_batch(
            &fixture.semantic,
            vec![AppendSemanticEventRequest {
                expected_stream_version: 1,
                event: event.clone(),
            }],
        )
        .expect("semantic append");
    assert_eq!(receipts[0].event_digest, event.event_digest);

    let previous_governance_digest = store
        .governance_events()
        .iter()
        .find(|loaded| loaded.event.event_id == "governance-0002")
        .expect("node B governance event")
        .event
        .event_digest
        .clone();
    let governance = governance_event(
        "governance-0004",
        4,
        &event,
        Some(previous_governance_digest),
    );
    store
        .append_governance_batch(
            &fixture.governance,
            vec![AppendGovernanceEventRequest {
                expected_stream_version: 1,
                event: governance,
            }],
        )
        .expect("governance append");
    let rebuilt = EventStore::load(&fixture.semantic, &fixture.governance).expect("rebuild");
    assert_eq!(
        rebuilt
            .governed_node_view(&node_b(), 5, None)
            .expect("governed node")
            .semantic_event_id,
        "semantic-0005"
    );
}

#[test]
fn append_lock_blocks_partial_reads() {
    let fixture = make_fixture();
    fs::write(fixture.semantic.join(".append.lock"), "").expect("append lock");
    assert_eq!(
        EventStore::load(&fixture.semantic, &fixture.governance)
            .expect_err("read during batch must fail")
            .code,
        "APPEND_IN_PROGRESS"
    );
}

#[test]
fn governed_view_requires_governance_for_the_exact_latest_epoch() {
    let fixture = make_fixture();
    fs::remove_file(governance_path(&fixture, 1, "governance-0001"))
        .expect("remove exact governance event");
    fs::remove_file(governance_path(&fixture, 2, "governance-0002"))
        .expect("remove second governance event");
    fs::remove_file(governance_path(&fixture, 3, "governance-0003"))
        .expect("remove third governance event");
    fs::create_dir_all(&fixture.governance).expect("governance directory");
    let store = EventStore::load(&fixture.semantic, &fixture.governance).expect("event store");
    assert_eq!(
        store
            .governed_node_view(&node_a(), 4, None)
            .expect_err("missing exact governance must fail")
            .code,
        "EXACT_GOVERNANCE_STATE_MISSING"
    );
}

#[test]
fn context_projection_uses_one_consistent_cut_and_exact_governance() {
    let fixture = make_fixture();
    let store = load_fixture(&fixture);
    let projection = store
        .context_projection("selector-w5", &selector(4))
        .expect("context projection");
    assert_eq!(projection.source_cursor, 4);
    assert_eq!(projection.selected_node_ids, vec!["node-a", "node-b"]);
    assert_eq!(projection.selected_relation_ids, vec!["relation-ab"]);
    assert_eq!(projection.projection_body.subjects.len(), 3);
    assert!(
        projection
            .forbidden_authority_moves
            .contains(&"admission-from-projection".to_owned())
    );

    let mut fractured = selector(3);
    fractured.required_subject_set = vec![node_a()];
    assert_eq!(
        store
            .context_projection("selector-fractured", &fractured)
            .expect_err("governance for cursor 4 cannot govern cursor 1")
            .code,
        "EXACT_GOVERNANCE_STATE_MISSING"
    );

    let mut duplicate = selector(4);
    duplicate.required_subject_set.push(node_a());
    assert_eq!(
        store
            .context_projection("selector-duplicate", &duplicate)
            .expect_err("duplicate subject must fail")
            .code,
        "CONTEXT_REQUIRED_SUBJECT_DUPLICATE"
    );

    let mut missing = selector(4);
    missing.required_subject_set = vec![identity(
        SubjectKind::Node,
        "missing-node",
        "test-node-type/v1",
    )];
    assert_eq!(
        store
            .context_projection("selector-missing", &missing)
            .expect_err("missing subject must fail")
            .code,
        "REQUIRED_SUBJECT_MISSING"
    );
}

#[test]
fn out_of_range_cursor_never_returns_partial_state() {
    let fixture = make_fixture();
    let store = load_fixture(&fixture);
    for cursor in [0, 5] {
        assert_eq!(
            store
                .ontology_at(cursor)
                .expect_err("out of range cursor")
                .code,
            "CURSOR_OUT_OF_RANGE"
        );
    }
}

#[test]
fn compiled_schema_positive_shapes_deserialize_and_unknown_fields_do_not() {
    let baseline_path =
        PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../fixtures/w1/positive-baseline.json");
    let baseline: serde_json::Value =
        serde_json::from_slice(&fs::read(baseline_path).expect("W1 baseline"))
            .expect("W1 baseline JSON");
    for value in baseline["semantic_events"]
        .as_array()
        .expect("semantic events")
    {
        let _: SemanticEvent = serde_json::from_value(value.clone()).expect("semantic shape");
    }
    let _: GovernanceEvent =
        serde_json::from_value(baseline["governance_event"].clone()).expect("governance shape");

    let mut unknown = baseline["semantic_events"][0].clone();
    unknown
        .as_object_mut()
        .expect("semantic object")
        .insert("implementation_only".to_owned(), json!(true));
    assert!(serde_json::from_value::<SemanticEvent>(unknown).is_err());
}
