use cal_ontology_graph_read_model::{
    BoundedGraphIngestion, CalculatedGraphBatch, CalculatedGraphDelta, CalculatedSubjectChange,
    DeltaSubjectResult, GraphReadModel, IngestionLifecycle, ProjectedChallengeContract, SubjectKey,
};
use cal_ontology_lifecycle::{AuthorityEffect, EventStore, ProjectedSubject};
use std::collections::{BTreeMap, BTreeSet};
use std::path::PathBuf;
use std::sync::{Arc, Barrier};
use std::thread;
use std::time::Duration;

fn store() -> EventStore {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../../../migration/cal-w7-ontology-product-epoch-001/fixtures/output");
    EventStore::load(root.join("semantic-events"), root.join("governance-events")).unwrap()
}

fn subjects(model: &GraphReadModel) -> BTreeMap<SubjectKey, ProjectedSubject> {
    model
        .subjects()
        .into_iter()
        .map(|subject| (SubjectKey::of(&subject), subject))
        .collect()
}

fn projected(model: &GraphReadModel, subject: &ProjectedSubject) -> DeltaSubjectResult {
    let key = SubjectKey::of(subject);
    DeltaSubjectResult {
        subject: subject.clone(),
        challenge: ProjectedChallengeContract {
            subject: key.clone(),
            semantic_event_id: subject.source_event_id.clone(),
            semantic_event_digest: subject.source_event_digest.clone(),
            semantic_cursor: subject.source_cursor,
            contract: model.challenge_contract(&key).unwrap().clone(),
        },
    }
}

fn delta_between(from: &GraphReadModel, to: &GraphReadModel) -> CalculatedGraphDelta {
    let from_subjects = subjects(from);
    let to_subjects = subjects(to);
    let keys = from_subjects
        .keys()
        .chain(to_subjects.keys())
        .cloned()
        .collect::<BTreeSet<_>>();
    let mut changes = Vec::new();
    for key in keys {
        let previous = from_subjects.get(&key);
        let resulting = to_subjects.get(&key);
        let semantic_changed = previous != resulting;
        let governance_changed = match (previous, resulting) {
            (Some(previous), Some(resulting)) if previous == resulting => {
                from.challenge_contract(&key) != to.challenge_contract(&key)
            }
            _ => false,
        };
        if !semantic_changed && !governance_changed {
            continue;
        }
        changes.push(CalculatedSubjectChange {
            subject: key.clone(),
            expected_previous: from.expected_subject_version(&key).unwrap(),
            semantic_change_cursor: semantic_changed.then_some(to.metadata().semantic_cursor),
            resulting: resulting.map(|subject| projected(to, subject)),
        });
    }
    CalculatedGraphDelta {
        schema_version: "cal-calculated-graph-delta/v1-prototype".to_owned(),
        delta_id: format!(
            "w7-ingestion-{}-{}",
            from.metadata().semantic_cursor,
            to.metadata().semantic_cursor
        ),
        authority_effect: AuthorityEffect::None,
        from_semantic_cursor: from.metadata().semantic_cursor,
        from_source_event_count: from.metadata().source_event_count,
        from_source_event_set_digest: from.metadata().source_event_set_digest.clone(),
        to_semantic_cursor: to.metadata().semantic_cursor,
        to_source_event_count: to.metadata().source_event_count,
        to_source_event_set_digest: to.metadata().source_event_set_digest.clone(),
        changes,
    }
}

fn batches(store: &EventStore, from: u64, to: u64) -> Vec<CalculatedGraphBatch> {
    (from + 1..=to)
        .map(|cursor| {
            let previous = GraphReadModel::rebuild(store, cursor - 1).unwrap();
            let next = GraphReadModel::rebuild(store, cursor).unwrap();
            CalculatedGraphBatch {
                delta: delta_between(&previous, &next),
                governance_cursor: cursor,
            }
        })
        .collect()
}

#[test]
fn bounded_ingestion_applies_backpressure_and_publishes_exact_snapshots() {
    let store = store();
    let initial = GraphReadModel::rebuild(&store, 15).unwrap();
    let expected = GraphReadModel::rebuild(&store, 47).unwrap();
    let mut batches = batches(&store, 15, 47).into_iter();
    let mut ingestion = BoundedGraphIngestion::new_paused(initial, 15, 4).unwrap();
    let graph = ingestion.graph();
    let old_snapshot = graph.snapshot().unwrap();

    let mut accepted = Vec::new();
    for _ in 0..4 {
        let batch = batches.next().unwrap();
        let receipt = ingestion.enqueue(batch).unwrap();
        assert_eq!(receipt.disposition, "accepted");
        accepted.push(receipt.sequence.unwrap());
    }
    let overloaded_batch = batches.next().unwrap();
    let overloaded = ingestion.enqueue(overloaded_batch.clone()).unwrap();
    assert_eq!(overloaded.disposition, "rejected_overload");
    assert_eq!(overloaded.code, "INGESTION_QUEUE_FULL");
    assert!(overloaded.retryable);
    assert_eq!(overloaded.sequence, None);

    let paused = ingestion.status().unwrap();
    assert_eq!(paused.lifecycle, IngestionLifecycle::Paused);
    assert_eq!(paused.pending_batch_count, 4);
    assert_eq!(paused.maximum_pending_batch_count, 4);
    assert_eq!(paused.semantic_cursor_lag, 4);
    assert_eq!(paused.governance_cursor_lag, 4);
    assert_eq!(
        ingestion
            .wait_until_projected(1, Duration::from_millis(5))
            .unwrap_err()
            .code,
        "INGESTION_WAIT_TIMEOUT"
    );

    let duplicate = CalculatedGraphBatch {
        delta: delta_between(
            &GraphReadModel::rebuild(&store, 15).unwrap(),
            &GraphReadModel::rebuild(&store, 16).unwrap(),
        ),
        governance_cursor: 16,
    };
    assert_eq!(
        ingestion.enqueue(duplicate).unwrap_err().code,
        "INGESTION_DUPLICATE_DELTA"
    );

    let readers_start = Arc::new(Barrier::new(5));
    let readers = (0..4)
        .map(|_| {
            let graph = Arc::clone(&graph);
            let readers_start = Arc::clone(&readers_start);
            thread::spawn(move || {
                readers_start.wait();
                for _ in 0..500 {
                    let snapshot = graph.snapshot().unwrap();
                    assert!((15..=47).contains(&snapshot.semantic_cursor()));
                    assert_eq!(snapshot.generation(), snapshot.semantic_cursor() - 15);
                    assert!(!snapshot.index_digest().is_empty());
                    thread::yield_now();
                }
            })
        })
        .collect::<Vec<_>>();
    readers_start.wait();
    ingestion.resume().unwrap();
    ingestion
        .wait_until_projected(*accepted.last().unwrap(), Duration::from_secs(5))
        .unwrap();

    let retried = ingestion.enqueue(overloaded_batch).unwrap();
    assert_eq!(retried.disposition, "accepted");
    let mut last_sequence = retried.sequence.unwrap();
    ingestion
        .wait_until_projected(last_sequence, Duration::from_secs(5))
        .unwrap();
    for batch in batches {
        let receipt = ingestion.enqueue(batch).unwrap();
        assert_eq!(receipt.disposition, "accepted");
        last_sequence = receipt.sequence.unwrap();
        ingestion
            .wait_until_projected(last_sequence, Duration::from_secs(5))
            .unwrap();
    }
    for reader in readers {
        reader.join().unwrap();
    }

    let receipt = ingestion.shutdown().unwrap();
    assert_eq!(receipt.result, "PASS");
    assert_eq!(receipt.accepted_batch_count, 32);
    assert_eq!(receipt.projected_batch_count, 32);
    assert_eq!(receipt.rejected_overload_count, 1);
    assert!(receipt.drained_exactly);
    assert_eq!(receipt.final_generation, 32);
    assert_eq!(receipt.final_semantic_cursor, 47);
    assert_eq!(receipt.final_governance_cursor, 47);
    assert_eq!(receipt.maximum_pending_batch_count, 4);
    assert_eq!(receipt.final_index_digest, expected.metadata().index_digest);
    assert_eq!(graph.snapshot().unwrap().model(), &expected);
    assert_eq!(old_snapshot.semantic_cursor(), 15);
    assert_eq!(old_snapshot.generation(), 0);
    assert!(!receipt.canonical_replay_source);
    assert_eq!(receipt.authority_effect, "none");
}

#[test]
fn ingestion_watermarks_and_worker_failures_are_fail_closed_and_observable() {
    let store = store();
    let initial = GraphReadModel::rebuild(&store, 15).unwrap();
    assert_eq!(
        BoundedGraphIngestion::new(initial.clone(), 15, 0)
            .unwrap_err()
            .code,
        "INGESTION_QUEUE_CAPACITY_ZERO"
    );

    let mut ingestion = BoundedGraphIngestion::new_paused(initial, 15, 2).unwrap();
    let mut first = batches(&store, 15, 16).pop().unwrap();
    first.governance_cursor = 14;
    assert_eq!(
        ingestion.enqueue(first).unwrap_err().code,
        "INGESTION_GOVERNANCE_WATERMARK_REGRESSION"
    );

    let mut corrupt = batches(&store, 15, 16).pop().unwrap();
    corrupt.delta.to_source_event_set_digest = "0".repeat(64);
    let accepted = ingestion.enqueue(corrupt).unwrap();
    assert_eq!(accepted.disposition, "accepted");
    ingestion.resume().unwrap();
    let failure = ingestion
        .wait_until_projected(accepted.sequence.unwrap(), Duration::from_secs(5))
        .unwrap_err();
    assert_eq!(failure.code, "INGESTION_WORKER_FAILED");
    let status = ingestion.status().unwrap();
    assert_eq!(status.lifecycle, IngestionLifecycle::Failed);
    assert_eq!(status.projected_batch_count, 0);
    assert_eq!(status.pending_batch_count, 1);
    assert_eq!(
        status.failure.unwrap().code,
        "DELTA_TARGET_PROJECTION_DIGEST_MISMATCH"
    );
    assert_eq!(
        ingestion
            .enqueue(batches(&store, 16, 17).pop().unwrap())
            .unwrap_err()
            .code,
        "INGESTION_WORKER_FAILED"
    );
    assert_eq!(
        ingestion.shutdown().unwrap_err().code,
        "INGESTION_WORKER_FAILED"
    );
}
