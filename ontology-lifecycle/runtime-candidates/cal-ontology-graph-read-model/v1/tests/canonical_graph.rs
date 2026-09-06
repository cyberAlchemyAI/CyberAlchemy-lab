use cal_ontology_graph_read_model::{
    AtomicCheckpointFault, CalculatedGraphDelta, CalculatedSubjectChange, ConcurrentGraphReadModel,
    DeltaSubjectResult, GraphReadModel, MAX_QUERY_PAGE_SIZE, ProjectedChallengeContract,
    RUNTIME_IDENTITY, RecoveryExpectation, SubjectKey, decode_checkpoint, encode_checkpoint,
    write_checkpoint_atomically,
};
use cal_ontology_lifecycle::{
    AuthorityEffect, ChallengeMode, EventStore, EventTail, OntologySemanticState,
};
use std::path::PathBuf;
use std::sync::{Arc, mpsc};
use std::thread;
use tempfile::tempdir;

const ONTOLOGY_ID: &str = "cav2.ontology-product";

fn store() -> EventStore {
    let (semantic, governance) = fixture_paths();
    EventStore::load(semantic, governance).unwrap()
}

fn fixture_paths() -> (PathBuf, PathBuf) {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../../../migration/cal-w7-ontology-product-epoch-001/fixtures/output");
    (root.join("semantic-events"), root.join("governance-events"))
}

fn key(subject_id: &str) -> SubjectKey {
    SubjectKey::new(ONTOLOGY_ID, subject_id)
}

#[test]
fn atomic_checkpoint_replacement_preserves_a_valid_old_or_new_target() {
    let store = store();
    let temporary = tempdir().unwrap();
    let target = temporary.path().join("checkpoint.json");
    let checkpoint_15 = GraphReadModel::create_checkpoint(&store, 15, 15).unwrap();
    let checkpoint_23 = GraphReadModel::create_checkpoint(&store, 23, 23).unwrap();
    let checkpoint_35 = GraphReadModel::create_checkpoint(&store, 35, 35).unwrap();

    let created =
        write_checkpoint_atomically(&target, &checkpoint_15, AtomicCheckpointFault::None).unwrap();
    assert_eq!(created.disposition, "created");
    assert!(created.staged_file_synced);
    assert!(created.atomic_rename_completed);
    assert!(created.parent_directory_synced);
    let original = std::fs::read(&target).unwrap();

    let interrupted = write_checkpoint_atomically(
        &target,
        &checkpoint_23,
        AtomicCheckpointFault::AfterStageSync,
    )
    .unwrap_err();
    assert_eq!(
        interrupted.code,
        "CHECKPOINT_FAULT_INJECTED_AFTER_STAGE_SYNC"
    );
    assert_eq!(std::fs::read(&target).unwrap(), original);
    let stage_count = std::fs::read_dir(temporary.path())
        .unwrap()
        .filter_map(Result::ok)
        .filter(|entry| {
            entry
                .file_name()
                .to_string_lossy()
                .starts_with(".checkpoint.json.stage.")
        })
        .count();
    assert_eq!(stage_count, 1);

    let replaced =
        write_checkpoint_atomically(&target, &checkpoint_23, AtomicCheckpointFault::None).unwrap();
    assert_eq!(replaced.disposition, "replaced");
    assert_eq!(replaced.prior_semantic_cursor, Some(15));
    assert_eq!(replaced.semantic_cursor, 23);

    let interrupted = write_checkpoint_atomically(
        &target,
        &checkpoint_35,
        AtomicCheckpointFault::AfterRenameBeforeDirectorySync,
    )
    .unwrap_err();
    assert_eq!(interrupted.code, "CHECKPOINT_FAULT_INJECTED_AFTER_RENAME");
    let current = decode_checkpoint(&std::fs::read(&target).unwrap()).unwrap();
    assert_eq!(current.body.tail_boundary.semantic_cursor, 35);

    let unchanged =
        write_checkpoint_atomically(&target, &checkpoint_35, AtomicCheckpointFault::None).unwrap();
    assert_eq!(unchanged.disposition, "unchanged");
    assert!(!unchanged.staged_file_synced);
    assert!(!unchanged.atomic_rename_completed);
    assert!(!unchanged.parent_directory_synced);

    let before_regression = std::fs::read(&target).unwrap();
    let regression =
        write_checkpoint_atomically(&target, &checkpoint_23, AtomicCheckpointFault::None)
            .unwrap_err();
    assert_eq!(regression.code, "CHECKPOINT_REPLACEMENT_REGRESSION");
    assert_eq!(std::fs::read(&target).unwrap(), before_regression);

    let incomparable = GraphReadModel::create_checkpoint(&store, 40, 30).unwrap();
    let failure = write_checkpoint_atomically(&target, &incomparable, AtomicCheckpointFault::None)
        .unwrap_err();
    assert_eq!(failure.code, "CHECKPOINT_REPLACEMENT_INCOMPARABLE");
    assert_eq!(std::fs::read(&target).unwrap(), before_regression);
}

#[test]
fn atomic_checkpoint_replacement_preserves_an_invalid_existing_target() {
    let store = store();
    let temporary = tempdir().unwrap();
    let target = temporary.path().join("checkpoint.json");
    std::fs::write(&target, b"invalid-existing-checkpoint").unwrap();
    let replacement = GraphReadModel::create_checkpoint(&store, 23, 23).unwrap();

    let failure = write_checkpoint_atomically(&target, &replacement, AtomicCheckpointFault::None)
        .unwrap_err();
    assert_eq!(failure.code, "CHECKPOINT_EXISTING_INVALID");
    assert_eq!(
        std::fs::read(&target).unwrap(),
        b"invalid-existing-checkpoint"
    );
}

#[cfg(unix)]
#[test]
fn atomic_checkpoint_replacement_refuses_a_symlink_target() {
    use std::os::unix::fs::symlink;

    let store = store();
    let temporary = tempdir().unwrap();
    let victim = temporary.path().join("victim.json");
    let target = temporary.path().join("checkpoint.json");
    std::fs::write(&victim, b"do-not-touch").unwrap();
    symlink(&victim, &target).unwrap();
    let replacement = GraphReadModel::create_checkpoint(&store, 23, 23).unwrap();

    let failure = write_checkpoint_atomically(&target, &replacement, AtomicCheckpointFault::None)
        .unwrap_err();
    assert_eq!(failure.code, "CHECKPOINT_TARGET_SYMLINK_FORBIDDEN");
    assert_eq!(std::fs::read(victim).unwrap(), b"do-not-touch");
}

fn projected_challenges(
    store: &EventStore,
    subjects: &[cal_ontology_lifecycle::ProjectedSubject],
) -> Vec<ProjectedChallengeContract> {
    subjects
        .iter()
        .map(|subject| {
            let governance = store
                .governance_events()
                .iter()
                .find(|loaded| {
                    loaded.event.semantic_ref.semantic_event_id == subject.source_event_id
                        && loaded.event.semantic_ref.semantic_event_digest
                            == subject.source_event_digest
                        && loaded.event.semantic_ref.semantic_cursor == subject.source_cursor
                })
                .unwrap();
            ProjectedChallengeContract {
                subject: SubjectKey::of(subject),
                semantic_event_id: subject.source_event_id.clone(),
                semantic_event_digest: subject.source_event_digest.clone(),
                semantic_cursor: subject.source_cursor,
                contract: governance
                    .event
                    .complete_resulting_governance_state
                    .challenge_contract
                    .clone(),
            }
        })
        .collect()
}

fn w7_relation_addition_delta(store: &EventStore, model: &GraphReadModel) -> CalculatedGraphDelta {
    let target_cut = store.ontology_at(47).unwrap();
    let mut changes = target_cut
        .subjects
        .iter()
        .filter(|subject| subject.source_cursor > 23)
        .map(|subject| {
            let governance = store
                .governance_events()
                .iter()
                .find(|loaded| {
                    loaded.event.semantic_ref.semantic_event_id == subject.source_event_id
                        && loaded.event.semantic_ref.semantic_event_digest
                            == subject.source_event_digest
                        && loaded.event.semantic_ref.semantic_cursor == subject.source_cursor
                })
                .unwrap();
            let subject_key = SubjectKey::of(subject);
            CalculatedSubjectChange {
                subject: subject_key.clone(),
                expected_previous: None,
                semantic_change_cursor: Some(subject.source_cursor),
                resulting: Some(DeltaSubjectResult {
                    subject: subject.clone(),
                    challenge: ProjectedChallengeContract {
                        subject: subject_key,
                        semantic_event_id: subject.source_event_id.clone(),
                        semantic_event_digest: subject.source_event_digest.clone(),
                        semantic_cursor: subject.source_cursor,
                        contract: governance
                            .event
                            .complete_resulting_governance_state
                            .challenge_contract
                            .clone(),
                    },
                }),
            }
        })
        .collect::<Vec<_>>();
    changes.sort_by(|left, right| left.subject.cmp(&right.subject));
    CalculatedGraphDelta {
        schema_version: "cal-calculated-graph-delta/v1-prototype".to_owned(),
        delta_id: "w7-relations-24-through-47".to_owned(),
        authority_effect: AuthorityEffect::None,
        from_semantic_cursor: model.metadata().semantic_cursor,
        from_source_event_count: model.metadata().source_event_count,
        from_source_event_set_digest: model.metadata().source_event_set_digest.clone(),
        to_semantic_cursor: target_cut.semantic_cursor,
        to_source_event_count: target_cut.source_event_count,
        to_source_event_set_digest: target_cut.source_event_set_digest,
        changes,
    }
}

#[test]
fn canonical_rebuild_has_exact_event_cut_and_governance_coverage() {
    let model = GraphReadModel::rebuild(&store(), 47).unwrap();
    let metadata = model.metadata();
    assert_eq!(metadata.semantic_cursor, 47);
    assert_eq!(metadata.source_event_count, 47);
    assert_eq!(
        metadata.source_event_set_digest,
        "7a1089513ef4ed74bf70d6ed724d78f42a0e15cd267ac141213880026f06d6e2"
    );
    assert_eq!(metadata.node_count, 23);
    assert_eq!(metadata.relation_count, 24);
    assert_eq!(metadata.exact_governance_join_count, 47);
    assert!(!metadata.canonical_replay_source);
    assert_eq!(metadata.authority_effect, "none");
}

#[test]
fn canonical_queries_cover_neighbors_paths_types_context_and_challenges() {
    let model = GraphReadModel::rebuild(&store(), 47).unwrap();
    let capabilities =
        model.outgoing_neighbors(&key("CA2-PRODUCT-ONTOLOGY"), "includes_capability");
    assert_eq!(capabilities.len(), 5);

    let path = vec!["develops".to_owned(), "includes_capability".to_owned()];
    let traversed = model.traverse(&key("CA2-PROJECT-ONTOLOGY-PRODUCT"), &path);
    assert_eq!(traversed.len(), 5);
    assert_eq!(model.subjects_by_type(ONTOLOGY_ID, "actor").len(), 4);

    let members = model.context_members(ONTOLOGY_ID, "CA2-PROJECT-ONTOLOGY-PRODUCT");
    assert!(
        members
            .iter()
            .any(|subject| subject.identity.subject_id == "CA2-GOAL-ONTOLOGY-PRODUCT-FOUNDATION")
    );

    let challenge = model
        .challenge_contract(&key("CA2-PRODUCT-ONTOLOGY"))
        .unwrap();
    assert_eq!(challenge.valid_challenge_modes.len(), 3);
    assert!(
        challenge
            .valid_challenge_modes
            .contains(&ChallengeMode::Evidence)
    );
    assert!(
        challenge
            .valid_challenge_modes
            .contains(&ChallengeMode::Contradiction)
    );
    assert!(
        challenge
            .valid_challenge_modes
            .contains(&ChallengeMode::OwnerReview)
    );
    assert!(challenge.contradiction_edges.is_empty());
    assert!(challenge.validation_edges.is_empty());
    assert_eq!(
        model
            .subjects_supporting_challenge_mode(ChallengeMode::Evidence)
            .len(),
        47
    );
}

#[test]
fn incremental_event_application_equals_full_rebuild() {
    let store = store();
    let mut incremental = GraphReadModel::rebuild(&store, 23).unwrap();
    incremental.advance(&store, 47).unwrap();
    let rebuilt = GraphReadModel::rebuild(&store, 47).unwrap();
    assert_eq!(incremental, rebuilt);
    assert_eq!(
        incremental.metadata().index_digest,
        rebuilt.metadata().index_digest
    );
}

#[test]
fn repeated_rebuild_is_byte_deterministic_at_the_digest_surface() {
    let store = store();
    let first = GraphReadModel::rebuild(&store, 47).unwrap();
    let second = GraphReadModel::rebuild(&store, 47).unwrap();
    assert_eq!(
        first.metadata().index_digest,
        second.metadata().index_digest
    );
    assert_eq!(first.subjects(), second.subjects());
}

#[test]
fn restart_recovery_rebuilds_exact_w7_state_without_a_checkpoint() {
    let store = store();
    let cut = store.ontology_at(47).unwrap();
    let challenges = projected_challenges(&store, &cut.subjects);
    let expected = GraphReadModel::rebuild(&store, 47).unwrap();
    let expectation = RecoveryExpectation {
        runtime_identity: RUNTIME_IDENTITY.to_owned(),
        semantic_cursor: cut.semantic_cursor,
        source_event_count: cut.source_event_count,
        source_event_set_digest: cut.source_event_set_digest.clone(),
        expected_index_digest: expected.metadata().index_digest.clone(),
    };

    let (recovered, receipt) =
        GraphReadModel::recover_from_calculated_cut(cut, challenges, &expectation).unwrap();

    assert_eq!(recovered, expected);
    assert_eq!(
        receipt.recovery_strategy,
        "full_rebuild_from_verified_calculated_cut"
    );
    assert!(receipt.exact_index_digest_match);
    assert!(!receipt.checkpoint_used);
    assert!(!receipt.canonical_replay_source);
    assert_eq!(receipt.authority_effect, "none");

    let (from_files, file_receipt) =
        GraphReadModel::recover_from_event_store(&store, &expectation).unwrap();
    assert_eq!(from_files, expected);
    assert_eq!(
        file_receipt.recovery_strategy,
        "full_rebuild_from_canonical_event_files"
    );
    assert!(!file_receipt.checkpoint_used);
}

#[test]
fn disposable_checkpoint_plus_canonical_tail_equals_full_w7_replay() {
    let store = store();
    let expected = GraphReadModel::rebuild(&store, 47).unwrap();
    let checkpoint = GraphReadModel::create_checkpoint(&store, 23, 23).unwrap();
    assert!(!checkpoint.canonical_replay_source);
    assert_eq!(checkpoint.authority_effect, "none");
    assert_eq!(checkpoint.body.projection.source_cursor, 23);

    let encoded = encode_checkpoint(&checkpoint).unwrap();
    let decoded = decode_checkpoint(encoded.as_bytes()).unwrap();
    assert_eq!(decoded, checkpoint);

    let (semantic, governance) = fixture_paths();
    let tail = EventTail::load(
        semantic,
        governance,
        checkpoint.body.tail_boundary.clone(),
        47,
        47,
    )
    .unwrap();
    let expectation = RecoveryExpectation {
        runtime_identity: RUNTIME_IDENTITY.to_owned(),
        semantic_cursor: expected.metadata().semantic_cursor,
        source_event_count: expected.metadata().source_event_count,
        source_event_set_digest: expected.metadata().source_event_set_digest.clone(),
        expected_index_digest: expected.metadata().index_digest.clone(),
    };
    let (recovered, receipt) =
        GraphReadModel::recover_from_checkpoint_and_tail(&checkpoint, &tail, &expectation).unwrap();
    assert_eq!(recovered, expected);
    assert_eq!(
        receipt.recovery_strategy,
        "verified_disposable_checkpoint_plus_canonical_event_tail"
    );
    assert!(receipt.checkpoint_used);
    assert!(!receipt.canonical_replay_source);

    let mut corrupt = checkpoint;
    corrupt.body.base_expectation.expected_index_digest = "0".repeat(64);
    assert_eq!(
        GraphReadModel::recover_from_checkpoint_and_tail(&corrupt, &tail, &expectation)
            .unwrap_err()
            .code,
        "CHECKPOINT_BODY_DIGEST_MISMATCH"
    );
}

#[test]
fn restart_recovery_rejects_changed_source_governance_and_result_expectations() {
    let store = store();
    let cut = store.ontology_at(47).unwrap();
    let challenges = projected_challenges(&store, &cut.subjects);
    let expected = GraphReadModel::rebuild(&store, 47).unwrap();
    let expectation = RecoveryExpectation {
        runtime_identity: RUNTIME_IDENTITY.to_owned(),
        semantic_cursor: cut.semantic_cursor,
        source_event_count: cut.source_event_count,
        source_event_set_digest: cut.source_event_set_digest.clone(),
        expected_index_digest: expected.metadata().index_digest.clone(),
    };

    let mut wrong_runtime = expectation.clone();
    wrong_runtime.runtime_identity = "another.runtime/v1".to_owned();
    let failure = GraphReadModel::recover_from_calculated_cut(
        cut.clone(),
        challenges.clone(),
        &wrong_runtime,
    )
    .unwrap_err();
    assert_eq!(failure.code, "RECOVERY_RUNTIME_IDENTITY_MISMATCH");

    let mut changed_source = expectation.clone();
    changed_source.source_event_set_digest = "changed".to_owned();
    let failure = GraphReadModel::recover_from_calculated_cut(
        cut.clone(),
        challenges.clone(),
        &changed_source,
    )
    .unwrap_err();
    assert_eq!(failure.code, "RECOVERY_SOURCE_ENVELOPE_MISMATCH");

    let mut corrupt_governance = challenges.clone();
    corrupt_governance[0].semantic_event_digest = "corrupt".to_owned();
    let failure =
        GraphReadModel::recover_from_calculated_cut(cut.clone(), corrupt_governance, &expectation)
            .unwrap_err();
    assert_eq!(failure.code, "GOVERNANCE_REFERENCE_MISMATCH");

    let mut wrong_result = expectation;
    wrong_result.expected_index_digest = "0".repeat(64);
    let failure =
        GraphReadModel::recover_from_calculated_cut(cut, challenges, &wrong_result).unwrap_err();
    assert_eq!(failure.code, "RECOVERY_INDEX_DIGEST_MISMATCH");
}

#[test]
fn cursor_regression_is_fail_closed() {
    let store = store();
    let mut model = GraphReadModel::rebuild(&store, 47).unwrap();
    let failure = model.advance(&store, 23).unwrap_err();
    assert_eq!(failure.code, "READ_MODEL_CURSOR_REGRESSION");
}

#[test]
fn calculated_cut_constructor_requires_exact_governance_references() {
    let store = store();
    let cut = store.ontology_at(47).unwrap();
    let mut challenges = cut
        .subjects
        .iter()
        .map(|subject| {
            let governance = store
                .governance_events()
                .iter()
                .find(|loaded| {
                    loaded.event.semantic_ref.semantic_event_id == subject.source_event_id
                        && loaded.event.semantic_ref.semantic_event_digest
                            == subject.source_event_digest
                        && loaded.event.semantic_ref.semantic_cursor == subject.source_cursor
                })
                .unwrap();
            ProjectedChallengeContract {
                subject: SubjectKey::new(
                    subject.identity.ontology_id.clone(),
                    subject.identity.subject_id.clone(),
                ),
                semantic_event_id: subject.source_event_id.clone(),
                semantic_event_digest: subject.source_event_digest.clone(),
                semantic_cursor: subject.source_cursor,
                contract: governance
                    .event
                    .complete_resulting_governance_state
                    .challenge_contract
                    .clone(),
            }
        })
        .collect::<Vec<_>>();
    let calculated = GraphReadModel::from_calculated_cut(cut.clone(), challenges.clone()).unwrap();
    assert_eq!(calculated, GraphReadModel::rebuild(&store, 47).unwrap());

    challenges[0].semantic_event_digest = "wrong".to_owned();
    let failure = GraphReadModel::from_calculated_cut(cut, challenges).unwrap_err();
    assert_eq!(failure.code, "GOVERNANCE_REFERENCE_MISMATCH");
}

#[test]
fn bounded_type_identity_pages_are_complete_and_cursor_stable() {
    let model = GraphReadModel::rebuild(&store(), 47).unwrap();
    let full_ids = model
        .subjects_by_type(ONTOLOGY_ID, "actor")
        .into_iter()
        .map(|subject| subject.identity.subject_id)
        .collect::<Vec<_>>();
    let first = model
        .subject_keys_by_type(ONTOLOGY_ID, "actor", None, 2)
        .unwrap();
    assert_eq!(first.items.len(), 2);
    assert!(first.next_after.is_some());
    let second = model
        .subject_keys_by_type(ONTOLOGY_ID, "actor", first.next_after.as_ref(), 2)
        .unwrap();
    assert_eq!(second.items.len(), 2);
    assert!(second.next_after.is_none());
    let paged_ids = first
        .items
        .into_iter()
        .chain(second.items)
        .map(|key| key.subject_id)
        .collect::<Vec<_>>();
    assert_eq!(paged_ids, full_ids);
}

#[test]
fn bounded_identity_pages_reject_invalid_limits_and_foreign_cursors() {
    let model = GraphReadModel::rebuild(&store(), 47).unwrap();
    let zero = model
        .subject_keys_by_type(ONTOLOGY_ID, "actor", None, 0)
        .unwrap_err();
    assert_eq!(zero.code, "QUERY_PAGE_LIMIT_OUT_OF_RANGE");
    let oversized = model
        .subject_keys_by_type(ONTOLOGY_ID, "actor", None, MAX_QUERY_PAGE_SIZE + 1)
        .unwrap_err();
    assert_eq!(oversized.code, "QUERY_PAGE_LIMIT_OUT_OF_RANGE");
    let foreign = SubjectKey::new("another.ontology", "actor-1");
    let mismatch = model
        .subject_keys_by_type(ONTOLOGY_ID, "actor", Some(&foreign), 2)
        .unwrap_err();
    assert_eq!(mismatch.code, "QUERY_PAGE_CURSOR_ONTOLOGY_MISMATCH");
}

#[test]
fn calculated_relation_addition_delta_equals_full_w7_rebuild() {
    let store = store();
    let mut incremental = GraphReadModel::rebuild(&store, 23).unwrap();
    let before = incremental.clone();
    let delta = w7_relation_addition_delta(&store, &incremental);
    let mut stale = delta.clone();
    stale.from_source_event_set_digest = "stale".to_owned();
    let failure = incremental.apply_calculated_delta(&stale).unwrap_err();
    assert_eq!(failure.code, "DELTA_BASE_MISMATCH");
    assert_eq!(incremental, before);

    let mut missing_endpoint = delta.clone();
    if let OntologySemanticState::Relation(relation) = &mut missing_endpoint.changes[0]
        .resulting
        .as_mut()
        .unwrap()
        .subject
        .semantic_state
    {
        relation.target_node_id = "missing-node".to_owned();
    }
    let failure = incremental
        .apply_calculated_delta(&missing_endpoint)
        .unwrap_err();
    assert_eq!(failure.code, "DELTA_RELATION_ENDPOINT_MISSING");
    assert_eq!(incremental, before);

    let mut wrong_projection = delta.clone();
    wrong_projection.to_source_event_set_digest = "0".repeat(64);
    let failure = incremental
        .apply_calculated_delta(&wrong_projection)
        .unwrap_err();
    assert_eq!(failure.code, "DELTA_TARGET_PROJECTION_DIGEST_MISMATCH");
    assert_eq!(incremental, before);

    let receipt = incremental.apply_calculated_delta(&delta).unwrap();
    assert_eq!(receipt.added, 24);
    assert_eq!(receipt.updated, 0);
    assert_eq!(receipt.removed, 0);
    assert_eq!(receipt.governance_replaced, 0);
    assert_eq!(receipt.transaction_strategy, "bounded_rollback_journal");
    assert_eq!(receipt.staged_previous_subject_count, 0);
    assert!(!receipt.full_model_clone);
    assert_eq!(incremental, GraphReadModel::rebuild(&store, 47).unwrap());
}

#[test]
fn governance_only_delta_replaces_exact_contract_without_semantic_cursor_change() {
    let store = store();
    let mut model = GraphReadModel::rebuild(&store, 47).unwrap();
    let key = key("CA2-PRODUCT-ONTOLOGY");
    let expected = model.expected_subject_version(&key).unwrap().unwrap();
    let subject = model.subject(&key).unwrap().clone();
    let mut contract = model.challenge_contract(&key).unwrap().clone();
    contract.challenge_response = "Replacement benchmark challenge response.".to_owned();
    let delta = CalculatedGraphDelta {
        schema_version: "cal-calculated-graph-delta/v1-prototype".to_owned(),
        delta_id: "w7-governance-replacement".to_owned(),
        authority_effect: AuthorityEffect::None,
        from_semantic_cursor: 47,
        from_source_event_count: 47,
        from_source_event_set_digest: model.metadata().source_event_set_digest.clone(),
        to_semantic_cursor: 47,
        to_source_event_count: 47,
        to_source_event_set_digest: model.metadata().source_event_set_digest.clone(),
        changes: vec![CalculatedSubjectChange {
            subject: key.clone(),
            expected_previous: Some(expected),
            semantic_change_cursor: None,
            resulting: Some(DeltaSubjectResult {
                subject: subject.clone(),
                challenge: ProjectedChallengeContract {
                    subject: key.clone(),
                    semantic_event_id: subject.source_event_id,
                    semantic_event_digest: subject.source_event_digest,
                    semantic_cursor: subject.source_cursor,
                    contract: contract.clone(),
                },
            }),
        }],
    };
    let mut invalid = delta.clone();
    let invalid_subject = &mut invalid.changes[0].resulting.as_mut().unwrap().subject;
    if let OntologySemanticState::Node(node) = &mut invalid_subject.semantic_state {
        node.label = "Illicit semantic mutation without a new event.".to_owned();
    }
    let before = model.clone();
    let failure = model.apply_calculated_delta(&invalid).unwrap_err();
    assert_eq!(failure.code, "GOVERNANCE_CHANGE_MUTATES_SEMANTIC_STATE");
    assert_eq!(model, before);

    let receipt = model.apply_calculated_delta(&delta).unwrap();
    assert_eq!(receipt.governance_replaced, 1);
    assert_eq!(receipt.transaction_strategy, "bounded_rollback_journal");
    assert_eq!(receipt.staged_previous_subject_count, 1);
    assert!(!receipt.full_model_clone);
    assert_eq!(receipt.from_semantic_cursor, receipt.to_semantic_cursor);
    assert_eq!(model.challenge_contract(&key), Some(&contract));
}

#[test]
fn versioned_snapshots_retain_old_generation_during_publication() {
    let store = store();
    let initial = GraphReadModel::rebuild(&store, 23).unwrap();
    let delta = w7_relation_addition_delta(&store, &initial);
    let expected = GraphReadModel::rebuild(&store, 47).unwrap();
    let publisher = Arc::new(ConcurrentGraphReadModel::new(initial));

    let held_snapshot = publisher.snapshot().unwrap();
    assert_eq!(held_snapshot.generation(), 0);
    assert_eq!(held_snapshot.semantic_cursor(), 23);
    assert_eq!(held_snapshot.metadata().relation_count, 0);

    let (started_tx, started_rx) = mpsc::channel();
    let writer_publisher = Arc::clone(&publisher);
    let writer = thread::spawn(move || {
        started_tx.send(()).unwrap();
        writer_publisher.apply_calculated_delta(&delta)
    });
    started_rx.recv().unwrap();
    let receipt = writer.join().unwrap().unwrap();
    assert_eq!(held_snapshot.semantic_cursor(), 23);
    assert_eq!(held_snapshot.metadata().relation_count, 0);

    assert_eq!(receipt.from_generation, 0);
    assert_eq!(receipt.published_generation, 1);
    assert_eq!(receipt.from_semantic_cursor, 23);
    assert_eq!(receipt.published_semantic_cursor, 47);
    assert_eq!(
        receipt.published_index_digest,
        expected.metadata().index_digest
    );
    assert_eq!(
        receipt.publication_strategy,
        "structurally_shared_arc_snapshot"
    );
    assert!(!receipt.staged_full_model_clone);
    assert!(receipt.old_snapshots_remain_readable);
    assert_eq!(receipt.structural_sharing.previous_subject_count, 23);
    assert_eq!(receipt.structural_sharing.shared_subject_count, 23);
    assert_eq!(
        receipt.structural_sharing.previous_challenge_contract_count,
        23
    );
    assert_eq!(
        receipt.structural_sharing.shared_challenge_contract_count,
        23
    );
    assert!(receipt.structural_sharing.previous_index_bucket_count > 0);
    assert!(receipt.structural_sharing.shared_index_bucket_count > 0);
    assert!(
        receipt.structural_sharing.shared_index_bucket_count
            <= receipt.structural_sharing.previous_index_bucket_count
    );
    assert!(!receipt.canonical_replay_source);
    assert_eq!(receipt.authority_effect, "none");

    let published = publisher.snapshot().unwrap();
    assert_eq!(published.generation(), 1);
    assert_eq!(published.semantic_cursor(), 47);
    assert_eq!(published.model(), &expected);
    assert_eq!(held_snapshot.generation(), 0);
    assert_eq!(held_snapshot.semantic_cursor(), 23);
}

#[test]
fn failed_publication_preserves_generation_and_snapshot() {
    let store = store();
    let initial = GraphReadModel::rebuild(&store, 23).unwrap();
    let mut stale = w7_relation_addition_delta(&store, &initial);
    stale.from_source_event_set_digest = "stale".to_owned();
    let expected_digest = initial.metadata().index_digest.clone();
    let publisher = ConcurrentGraphReadModel::new(initial);

    let failure = publisher.apply_calculated_delta(&stale).unwrap_err();
    assert_eq!(failure.code, "DELTA_BASE_MISMATCH");
    let snapshot = publisher.snapshot().unwrap();
    assert_eq!(snapshot.generation(), 0);
    assert_eq!(snapshot.semantic_cursor(), 23);
    assert_eq!(snapshot.index_digest(), expected_digest);
}
