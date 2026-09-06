use cal_ontology_lifecycle::SubjectKind;
use cal_ontology_product_event_runtime_binding::{
    NAVIGATION_SHA256, ROOT_COMPONENT_ID, load_realized_runtime, parse_navigation,
    realize_navigation, validate_navigation,
};
use std::fs;
use tempfile::tempdir;

const NAVIGATION: &[u8] = include_bytes!(
    "../../../../../product/products/ontology/v1/navigation/cohesive-lab-system/navigation.json"
);

#[test]
fn exact_admitted_navigation_realizes_as_canonical_events() {
    let root = tempdir().unwrap().path().join("runtime");
    let runtime = realize_navigation(NAVIGATION, &root).unwrap();
    let observation = runtime.observation().unwrap();
    assert_eq!(observation.semantic_event_count, 29);
    assert_eq!(observation.governance_event_count, 29);
    assert_eq!(observation.latest_snapshot_count, 29);
    assert_eq!(observation.node_count, 14);
    assert_eq!(observation.relation_count, 15);
    assert_eq!(observation.residue_route_count, 5);
    assert_eq!(observation.child_ontologies_admitted_by_binding, 0);
    assert!(observation.root_admission_preserved);
    assert!(observation.canonical_replay_source_is_event_history);
    assert_eq!(observation.authority_effect, "none");
}

#[test]
fn independent_materializations_are_byte_equivalent() {
    let first = tempdir().unwrap().path().join("first");
    let second = tempdir().unwrap().path().join("second");
    let a = realize_navigation(NAVIGATION, first)
        .unwrap()
        .observation()
        .unwrap();
    let b = realize_navigation(NAVIGATION, second)
        .unwrap()
        .observation()
        .unwrap();
    assert_eq!(a, b);
}

#[test]
fn latest_root_snapshot_is_calculated_from_latest_subject_event() {
    let navigation = parse_navigation(NAVIGATION).unwrap();
    let root_component = navigation
        .components
        .iter()
        .find(|item| item.component_id == ROOT_COMPONENT_ID)
        .unwrap();
    let root = tempdir().unwrap().path().join("runtime");
    let mut runtime = realize_navigation(NAVIGATION, root).unwrap();
    runtime
        .append_root_refresh(root_component, "test-revision-2")
        .unwrap();
    let snapshots = runtime.latest_snapshots().unwrap();
    let snapshot = snapshots
        .iter()
        .find(|item| item.identity.subject_id == ROOT_COMPONENT_ID)
        .unwrap();
    assert_eq!(snapshot.source_cursor, 30);
    assert_eq!(snapshots.len(), 29);
    assert!(
        serde_json::to_string(&snapshot.semantic_state)
            .unwrap()
            .contains("test-revision-2")
    );
    assert_eq!(runtime.observation().unwrap().semantic_cursor, 30);
}

#[test]
fn multiple_root_updates_survive_restart() {
    let navigation = parse_navigation(NAVIGATION).unwrap();
    let root_component = navigation
        .components
        .iter()
        .find(|item| item.component_id == ROOT_COMPONENT_ID)
        .unwrap();
    let root = tempdir().unwrap().path().join("runtime");
    let mut runtime = realize_navigation(NAVIGATION, &root).unwrap();
    runtime
        .append_root_refresh(root_component, "test-revision-2")
        .unwrap();
    runtime
        .append_root_refresh(root_component, "test-revision-3")
        .unwrap();
    let restarted = load_realized_runtime(&root).unwrap();
    let observation = restarted.observation().unwrap();
    assert_eq!(observation.semantic_cursor, 31);
    assert_eq!(observation.semantic_event_count, 31);
    assert_eq!(observation.governance_event_count, 31);
    assert_eq!(observation.latest_snapshot_count, 29);
    let root_snapshot = restarted
        .latest_snapshots()
        .unwrap()
        .into_iter()
        .find(|item| item.identity.subject_id == ROOT_COMPONENT_ID)
        .unwrap();
    assert_eq!(root_snapshot.source_cursor, 31);
    assert!(
        serde_json::to_string(&root_snapshot.semantic_state)
            .unwrap()
            .contains("test-revision-3")
    );
}

#[test]
fn checkpoint_plus_tail_equals_full_replay() {
    let root = tempdir().unwrap().path().join("runtime");
    let runtime = realize_navigation(NAVIGATION, root).unwrap();
    let checkpoint = runtime.store.checkpoint_at(14).unwrap();
    let replay = runtime.store.ontology_at(29).unwrap();
    let recovered = runtime
        .store
        .ontology_from_checkpoint(&checkpoint, 29)
        .unwrap();
    assert_eq!(replay, recovered);
}

#[test]
fn context_projection_contains_all_nodes_and_relations_with_exact_governance() {
    let root = tempdir().unwrap().path().join("runtime");
    let runtime = realize_navigation(NAVIGATION, root).unwrap();
    let projection = runtime.context_projection().unwrap();
    assert_eq!(projection.selected_node_ids.len(), 14);
    assert_eq!(projection.selected_relation_ids.len(), 15);
    assert!(
        projection
            .forbidden_authority_moves
            .contains(&"admission-from-projection".to_owned())
    );
}

#[test]
fn restart_loads_the_same_event_calculated_observation() {
    let root = tempdir().unwrap().path().join("runtime");
    let initial = realize_navigation(NAVIGATION, &root)
        .unwrap()
        .observation()
        .unwrap();
    let restarted = load_realized_runtime(&root).unwrap().observation().unwrap();
    assert_eq!(initial, restarted);
}

#[test]
fn missing_integration_epoch_fails_closed() {
    let root = tempdir().unwrap().path().join("runtime");
    realize_navigation(NAVIGATION, &root).unwrap();
    fs::remove_file(
        root.join("integration-events/00000001-ontology-product-realization-epoch-0001.json"),
    )
    .unwrap();
    let error = load_realized_runtime(&root)
        .err()
        .expect("missing epoch rejected");
    assert_eq!(error.code, "INTEGRATION_EPOCH_MISSING");
}

#[test]
fn missing_event_fails_closed() {
    let root = tempdir().unwrap().path().join("runtime");
    realize_navigation(NAVIGATION, &root).unwrap();
    let path = fs::read_dir(root.join("semantic-events"))
        .unwrap()
        .next()
        .unwrap()
        .unwrap()
        .path();
    fs::remove_file(path).unwrap();
    assert!(load_realized_runtime(&root).is_err());
}

#[test]
fn event_digest_tampering_fails_closed() {
    let root = tempdir().unwrap().path().join("runtime");
    realize_navigation(NAVIGATION, &root).unwrap();
    let path = fs::read_dir(root.join("semantic-events"))
        .unwrap()
        .next()
        .unwrap()
        .unwrap()
        .path();
    let mut value: serde_json::Value = serde_json::from_slice(&fs::read(&path).unwrap()).unwrap();
    value["event_digest"] = serde_json::Value::String("0".repeat(64));
    fs::write(
        path,
        format!("{}\n", serde_json::to_string(&value).unwrap()),
    )
    .unwrap();
    assert!(load_realized_runtime(&root).is_err());
}

#[test]
fn child_authority_inflation_is_rejected() {
    let mut navigation = parse_navigation(NAVIGATION).unwrap();
    let child = navigation
        .components
        .iter_mut()
        .find(|item| item.component_id != ROOT_COMPONENT_ID)
        .unwrap();
    child.effective_authority_state = "admitted-root".to_owned();
    assert_eq!(
        validate_navigation(&navigation).unwrap_err().code,
        "CHILD_AUTHORITY_STATE_CHANGED"
    );
}

#[test]
fn domainspec_collision_cannot_be_removed() {
    let mut navigation = parse_navigation(NAVIGATION).unwrap();
    navigation
        .residue_routes
        .retain(|item| item.residue_id != "CAL-RES-DOMAINSPEC-SUCCESSOR-COLLISION");
    assert!(validate_navigation(&navigation).is_err());
}

#[test]
fn exact_navigation_digest_is_required() {
    let mut bytes = NAVIGATION.to_vec();
    bytes.push(b' ');
    let error = parse_navigation(&bytes).unwrap_err();
    assert_eq!(error.code, "NAVIGATION_DIGEST_MISMATCH");
    assert_eq!(
        cal_ontology_product_event_runtime_binding::sha256(NAVIGATION),
        NAVIGATION_SHA256
    );
}

#[test]
fn nonempty_runtime_target_is_refused() {
    let temporary = tempdir().unwrap();
    let root = temporary.path().join("runtime");
    fs::create_dir_all(&root).unwrap();
    fs::write(root.join("foreign"), b"preserve").unwrap();
    let error = realize_navigation(NAVIGATION, &root)
        .err()
        .expect("nonempty target rejected");
    assert_eq!(error.code, "RUNTIME_ROOT_NOT_EMPTY");
    assert_eq!(fs::read(root.join("foreign")).unwrap(), b"preserve");
}

#[test]
fn projected_subject_kinds_remain_distinct() {
    let root = tempdir().unwrap().path().join("runtime");
    let runtime = realize_navigation(NAVIGATION, root).unwrap();
    let cut = runtime.store.ontology_at(29).unwrap();
    assert_eq!(
        cut.subjects
            .iter()
            .filter(|item| item.identity.subject_kind == SubjectKind::Node)
            .count(),
        14
    );
    assert_eq!(
        cut.subjects
            .iter()
            .filter(|item| item.identity.subject_kind == SubjectKind::Relation)
            .count(),
        15
    );
}
