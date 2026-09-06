use cal_ontology_graph_read_model::{
    BoundedGraphIngestion, CalculatedGraphBatch, CalculatedGraphDelta, CalculatedSubjectChange,
    DeltaSubjectResult, GraphReadModel, ProjectedChallengeContract, SubjectKey,
    calculated_projection_digest,
};
use cal_ontology_lifecycle::{
    AuthorityEffect, ChallengeContract, ChallengeMode, ConsistentOntologyCut, Lifecycle,
    OntologyNodeSemanticState, OntologySemanticState, OntologySubjectIdentity, ProjectedSubject,
    SubjectKind, TypedPropertySet,
};
use serde::Serialize;
use serde_json::json;
use std::collections::BTreeMap;
use std::env;
use std::process::ExitCode;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::{Arc, Barrier};
use std::thread;
use std::time::{Duration, Instant};

const ONTOLOGY_ID: &str = "benchmark.synthetic.ingestion";

#[derive(Serialize)]
struct SustainedIngestionReport {
    schema_version: String,
    result: String,
    batch_count: usize,
    queue_capacity: usize,
    reader_threads: usize,
    reader_observations: u64,
    invalid_reader_observations: u64,
    accepted_batch_count: u64,
    projected_batch_count: u64,
    rejected_overload_count: u64,
    deterministic_initial_overload: bool,
    overload_retry_succeeded: bool,
    maximum_pending_batch_count: usize,
    pending_bound: usize,
    pending_bound_observed: bool,
    final_semantic_cursor: u64,
    final_governance_cursor: u64,
    final_generation: u64,
    final_index_digest: String,
    expected_index_digest: String,
    exact_final_rebuild_equivalence: bool,
    old_snapshot_retained: bool,
    drained_exactly: bool,
    final_semantic_cursor_lag: u64,
    final_governance_cursor_lag: u64,
    ingestion_elapsed_ns: u128,
    maximum_projection_latency_ns: u128,
    throughput_batches_per_second: f64,
    canonical_replay_source: bool,
    authority_effect: String,
    claim_ceiling: String,
}

fn main() -> ExitCode {
    match run() {
        Ok(report) => {
            println!(
                "{}",
                serde_json::to_string_pretty(&report).expect("serializable report")
            );
            ExitCode::SUCCESS
        }
        Err(detail) => {
            eprintln!(
                "{}",
                serde_json::to_string(&json!({
                    "result": "BLOCK",
                    "code": "SUSTAINED_INGESTION_FAILED",
                    "detail": detail,
                }))
                .expect("serializable error")
            );
            ExitCode::from(2)
        }
    }
}

fn run() -> Result<SustainedIngestionReport, String> {
    let arguments = env::args().skip(1).collect::<Vec<_>>();
    if arguments.len() != 3 {
        return Err("expected <batch-count> <queue-capacity> <reader-thread-count>".to_owned());
    }
    let batch_count = parse_positive(&arguments[0], "batch count")?;
    let queue_capacity = parse_positive(&arguments[1], "queue capacity")?;
    let reader_threads = parse_positive(&arguments[2], "reader thread count")?;
    if batch_count <= queue_capacity {
        return Err("batch count must exceed queue capacity".to_owned());
    }

    let (initial, batches, expected) = generated_workload(batch_count)?;
    let expected_index_digest = expected.metadata().index_digest.clone();
    let mut ingestion = BoundedGraphIngestion::new_paused(initial, 0, queue_capacity)
        .map_err(|failure| failure.to_string())?;
    let graph = ingestion.graph();
    let old_snapshot = graph.snapshot().map_err(|failure| failure.to_string())?;
    let readers_start = Arc::new(Barrier::new(reader_threads + 1));
    let readers_done = Arc::new(AtomicBool::new(false));
    let observations = Arc::new(AtomicU64::new(0));
    let invalid = Arc::new(AtomicU64::new(0));
    let readers = (0..reader_threads)
        .map(|_| {
            let graph = Arc::clone(&graph);
            let start = Arc::clone(&readers_start);
            let done = Arc::clone(&readers_done);
            let observations = Arc::clone(&observations);
            let invalid = Arc::clone(&invalid);
            thread::spawn(move || {
                start.wait();
                while !done.load(Ordering::Acquire) {
                    match graph.snapshot() {
                        Ok(snapshot) => {
                            let metadata = snapshot.metadata();
                            let consistent = snapshot.generation() == snapshot.semantic_cursor()
                                && metadata.source_event_count as u64 == snapshot.semantic_cursor()
                                && metadata.node_count as u64 == snapshot.semantic_cursor()
                                && metadata.relation_count == 0
                                && metadata.exact_governance_join_count as u64
                                    == snapshot.semantic_cursor()
                                && !snapshot.index_digest().is_empty()
                                && !metadata.canonical_replay_source
                                && metadata.authority_effect == "none";
                            observations.fetch_add(1, Ordering::Relaxed);
                            if !consistent {
                                invalid.fetch_add(1, Ordering::Relaxed);
                            }
                        }
                        Err(_) => {
                            observations.fetch_add(1, Ordering::Relaxed);
                            invalid.fetch_add(1, Ordering::Relaxed);
                        }
                    }
                    thread::yield_now();
                }
            })
        })
        .collect::<Vec<_>>();

    readers_start.wait();
    let started = Instant::now();
    let mut batches = batches.into_iter();
    let mut last_sequence = 0;
    for _ in 0..queue_capacity {
        let receipt = ingestion
            .enqueue(batches.next().expect("capacity is below batch count"))
            .map_err(|failure| failure.to_string())?;
        if receipt.disposition != "accepted" {
            return Err("paused queue did not accept its declared capacity".to_owned());
        }
        last_sequence = receipt.sequence.expect("accepted sequence");
    }
    let overflow_batch = batches.next().expect("batch count exceeds capacity");
    let overload = ingestion
        .enqueue(overflow_batch.clone())
        .map_err(|failure| failure.to_string())?;
    let deterministic_initial_overload = overload.disposition == "rejected_overload"
        && overload.code == "INGESTION_QUEUE_FULL"
        && overload.retryable
        && overload.sequence.is_none();
    if !deterministic_initial_overload {
        return Err("paused queue did not expose deterministic overload".to_owned());
    }
    ingestion.resume().map_err(|failure| failure.to_string())?;
    let sequence = enqueue_with_retry(&mut ingestion, overflow_batch, Duration::from_secs(30))?;
    let overload_retry_succeeded = true;
    last_sequence = last_sequence.max(sequence);
    for batch in batches {
        let sequence = enqueue_with_retry(&mut ingestion, batch, Duration::from_secs(30))?;
        last_sequence = sequence;
    }
    let final_status = ingestion
        .wait_until_projected(last_sequence, Duration::from_secs(60))
        .map_err(|failure| failure.to_string())?;
    let elapsed = started.elapsed();
    readers_done.store(true, Ordering::Release);
    for reader in readers {
        reader
            .join()
            .map_err(|_| "reader thread panicked".to_owned())?;
    }
    let shutdown = ingestion
        .shutdown()
        .map_err(|failure| failure.to_string())?;
    let final_snapshot = graph.snapshot().map_err(|failure| failure.to_string())?;
    let exact_final_rebuild_equivalence = final_snapshot.model() == &expected;
    let old_snapshot_retained = old_snapshot.generation() == 0
        && old_snapshot.semantic_cursor() == 0
        && old_snapshot.metadata().source_event_count == 0;
    let pending_bound = queue_capacity + 1;
    let pending_bound_observed = shutdown.maximum_pending_batch_count <= pending_bound;
    let throughput = batch_count as f64 / elapsed.as_secs_f64();
    let passed = deterministic_initial_overload
        && overload_retry_succeeded
        && shutdown.accepted_batch_count == batch_count as u64
        && shutdown.projected_batch_count == batch_count as u64
        && shutdown.rejected_overload_count >= 1
        && shutdown.drained_exactly
        && shutdown.final_generation == batch_count as u64
        && shutdown.final_semantic_cursor == batch_count as u64
        && shutdown.final_governance_cursor == batch_count as u64
        && final_status.semantic_cursor_lag == 0
        && final_status.governance_cursor_lag == 0
        && invalid.load(Ordering::Relaxed) == 0
        && exact_final_rebuild_equivalence
        && old_snapshot_retained
        && pending_bound_observed;

    Ok(SustainedIngestionReport {
        schema_version: "cal-sustained-ingestion-report/v1-prototype".to_owned(),
        result: if passed { "PASS" } else { "BLOCK" }.to_owned(),
        batch_count,
        queue_capacity,
        reader_threads,
        reader_observations: observations.load(Ordering::Relaxed),
        invalid_reader_observations: invalid.load(Ordering::Relaxed),
        accepted_batch_count: shutdown.accepted_batch_count,
        projected_batch_count: shutdown.projected_batch_count,
        rejected_overload_count: shutdown.rejected_overload_count,
        deterministic_initial_overload,
        overload_retry_succeeded,
        maximum_pending_batch_count: shutdown.maximum_pending_batch_count,
        pending_bound,
        pending_bound_observed,
        final_semantic_cursor: shutdown.final_semantic_cursor,
        final_governance_cursor: shutdown.final_governance_cursor,
        final_generation: shutdown.final_generation,
        final_index_digest: shutdown.final_index_digest,
        expected_index_digest,
        exact_final_rebuild_equivalence,
        old_snapshot_retained,
        drained_exactly: shutdown.drained_exactly,
        final_semantic_cursor_lag: final_status.semantic_cursor_lag,
        final_governance_cursor_lag: final_status.governance_cursor_lag,
        ingestion_elapsed_ns: elapsed.as_nanos(),
        maximum_projection_latency_ns: shutdown.maximum_projection_latency_ns,
        throughput_batches_per_second: throughput,
        canonical_replay_source: false,
        authority_effect: "none".to_owned(),
        claim_ceiling: "local_synthetic_single_writer_sustained_ingestion_prototype_evidence_only"
            .to_owned(),
    })
}

fn enqueue_with_retry(
    ingestion: &mut BoundedGraphIngestion,
    batch: CalculatedGraphBatch,
    timeout: Duration,
) -> Result<u64, String> {
    let deadline = Instant::now() + timeout;
    loop {
        let receipt = ingestion
            .enqueue(batch.clone())
            .map_err(|failure| failure.to_string())?;
        match receipt.disposition.as_str() {
            "accepted" => return Ok(receipt.sequence.expect("accepted sequence")),
            "rejected_overload" if receipt.retryable => {
                if Instant::now() >= deadline {
                    return Err(format!("overload retry timed out for {}", receipt.delta_id));
                }
                thread::sleep(Duration::from_micros(100));
            }
            _ => {
                return Err(format!(
                    "unexpected enqueue receipt for {}",
                    receipt.delta_id
                ));
            }
        }
    }
}

fn generated_workload(
    batch_count: usize,
) -> Result<(GraphReadModel, Vec<CalculatedGraphBatch>, GraphReadModel), String> {
    let empty_subjects = Vec::new();
    let empty_digest =
        calculated_projection_digest(&empty_subjects).map_err(|failure| failure.to_string())?;
    let base_cut = ConsistentOntologyCut {
        schema_version: "cal-consistent-ontology-cut/v1-prototype".to_owned(),
        authority_effect: AuthorityEffect::None,
        semantic_cursor: 0,
        source_event_count: 0,
        source_event_set_digest: empty_digest.clone(),
        subjects: empty_subjects,
    };
    let initial = GraphReadModel::from_calculated_cut(base_cut, Vec::new())
        .map_err(|failure| failure.to_string())?;
    let mut subjects = Vec::with_capacity(batch_count);
    let mut challenges = Vec::with_capacity(batch_count);
    let mut batches = Vec::with_capacity(batch_count);
    let mut from_digest = empty_digest;
    for cursor in 1..=batch_count as u64 {
        let subject = generated_subject(cursor);
        let challenge = generated_challenge(&subject);
        subjects.push(subject.clone());
        challenges.push(challenge.clone());
        let to_digest =
            calculated_projection_digest(&subjects).map_err(|failure| failure.to_string())?;
        batches.push(CalculatedGraphBatch {
            governance_cursor: cursor,
            delta: CalculatedGraphDelta {
                schema_version: "cal-calculated-graph-delta/v1-prototype".to_owned(),
                delta_id: format!("synthetic-ingestion-{cursor:08}"),
                authority_effect: AuthorityEffect::None,
                from_semantic_cursor: cursor - 1,
                from_source_event_count: cursor as usize - 1,
                from_source_event_set_digest: from_digest,
                to_semantic_cursor: cursor,
                to_source_event_count: cursor as usize,
                to_source_event_set_digest: to_digest.clone(),
                changes: vec![CalculatedSubjectChange {
                    subject: SubjectKey::of(&subject),
                    expected_previous: None,
                    semantic_change_cursor: Some(cursor),
                    resulting: Some(DeltaSubjectResult { subject, challenge }),
                }],
            },
        });
        from_digest = to_digest;
    }
    let expected_cut = ConsistentOntologyCut {
        schema_version: "cal-consistent-ontology-cut/v1-prototype".to_owned(),
        authority_effect: AuthorityEffect::None,
        semantic_cursor: batch_count as u64,
        source_event_count: batch_count,
        source_event_set_digest: from_digest,
        subjects,
    };
    let expected = GraphReadModel::from_calculated_cut(expected_cut, challenges)
        .map_err(|failure| failure.to_string())?;
    Ok((initial, batches, expected))
}

fn generated_subject(cursor: u64) -> ProjectedSubject {
    let identity = OntologySubjectIdentity {
        subject_id: format!("ingested-node-{cursor:08}"),
        ontology_id: ONTOLOGY_ID.to_owned(),
        subject_kind: SubjectKind::Node,
        type_ref: "ingested_node".to_owned(),
    };
    let mut values = BTreeMap::new();
    values.insert("ingestion_partition".to_owned(), json!(cursor % 8));
    ProjectedSubject {
        identity: identity.clone(),
        source_event_id: format!("synthetic-event-{cursor:08}"),
        source_event_digest: format!("{cursor:064x}"),
        source_cursor: cursor,
        semantic_state: OntologySemanticState::Node(OntologyNodeSemanticState {
            identity,
            lifecycle: Lifecycle::Active,
            label: format!("Synthetic ingested node {cursor}"),
            definition_or_claim: "Synthetic sustained-ingestion fixture.".to_owned(),
            scope: "local prototype benchmark only".to_owned(),
            semantic_components: Vec::new(),
            semantic_definition_refs: Vec::new(),
            typed_properties: TypedPropertySet {
                profile_ref: "benchmark.synthetic.ingestion-properties/v1".to_owned(),
                values,
            },
            use_obligations: Vec::new(),
            forbidden_collapse: Vec::new(),
            profile_ref: "benchmark.synthetic.ingested-node/v1".to_owned(),
        }),
    }
}

fn generated_challenge(subject: &ProjectedSubject) -> ProjectedChallengeContract {
    ProjectedChallengeContract {
        subject: SubjectKey::of(subject),
        semantic_event_id: subject.source_event_id.clone(),
        semantic_event_digest: subject.source_event_digest.clone(),
        semantic_cursor: subject.source_cursor,
        contract: ChallengeContract {
            challenge_response: "Expose sustained-ingestion evidence.".to_owned(),
            valid_challenge_modes: vec![ChallengeMode::Evidence],
            contradiction_edges: Vec::new(),
            validation_edges: Vec::new(),
            owner_route: "prototype-benchmark-owner".to_owned(),
            resolution_gate: "none".to_owned(),
            blocking_questions: Vec::new(),
            challenge_residue_route: "sustained-ingestion-report".to_owned(),
        },
    }
}

fn parse_positive(value: &str, name: &str) -> Result<usize, String> {
    value
        .parse::<usize>()
        .ok()
        .filter(|parsed| *parsed > 0)
        .ok_or_else(|| format!("invalid {name}: {value}"))
}
