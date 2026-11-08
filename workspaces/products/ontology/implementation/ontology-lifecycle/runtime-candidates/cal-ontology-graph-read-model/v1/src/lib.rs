use cal_ontology_lifecycle::{
    AuthorityEffect, ChallengeContract, ChallengeMode, EventStore, EventTail, EventTailBoundary,
    Lifecycle, OntologySemanticState, ProjectedSubject, ProjectionCheckpoint,
    ProjectionSubjectReference, ReplayFailure, SubjectKind, canonical_json,
};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::error::Error;
use std::fmt::{self, Display};
use std::fs::{self, File, OpenOptions};
use std::io::Write;
use std::ops::Bound::{Excluded, Unbounded};
use std::ops::Deref;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Arc, Condvar, Mutex, RwLock, mpsc};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

pub const CANDIDATE_ID: &str = "CAL-ONTOLOGY-GRAPH-READ-MODEL-PROTOTYPE-001";
pub const RUNTIME_IDENTITY: &str = "cal.prototype.ontology-graph-read-model/v1";
pub const AUTHORITY_EFFECT: &str = "none";
pub const MAX_QUERY_PAGE_SIZE: usize = 4096;

static CHECKPOINT_STAGE_SEQUENCE: AtomicU64 = AtomicU64::new(0);

#[derive(Clone, Debug, Deserialize, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(deny_unknown_fields)]
pub struct SubjectKey {
    pub ontology_id: String,
    pub subject_id: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct SubjectKeyPage {
    pub schema_version: String,
    pub items: Vec<SubjectKey>,
    pub limit: usize,
    pub next_after: Option<SubjectKey>,
}

impl SubjectKey {
    pub fn new(ontology_id: impl Into<String>, subject_id: impl Into<String>) -> Self {
        Self {
            ontology_id: ontology_id.into(),
            subject_id: subject_id.into(),
        }
    }

    pub fn of(subject: &ProjectedSubject) -> Self {
        Self::new(
            subject.identity.ontology_id.clone(),
            subject.identity.subject_id.clone(),
        )
    }
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct GraphReadModelMetadata {
    pub schema_version: String,
    pub candidate_id: String,
    pub runtime_identity: String,
    pub canonical_replay_source: bool,
    pub authority_effect: String,
    pub semantic_cursor: u64,
    pub source_event_count: usize,
    pub source_event_set_digest: String,
    pub node_count: usize,
    pub relation_count: usize,
    pub exact_governance_join_count: usize,
    pub index_digest: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct RelationMatch {
    pub relation: ProjectedSubject,
    pub neighbor: ProjectedSubject,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ChallengeView {
    pub subject: SubjectKey,
    pub contract: ChallengeContract,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProjectedChallengeContract {
    pub subject: SubjectKey,
    pub semantic_event_id: String,
    pub semantic_event_digest: String,
    pub semantic_cursor: u64,
    pub contract: ChallengeContract,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ExpectedSubjectVersion {
    pub subject: SubjectKey,
    pub semantic_event_id: String,
    pub semantic_event_digest: String,
    pub semantic_cursor: u64,
    pub challenge_contract_digest: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct DeltaSubjectResult {
    pub subject: ProjectedSubject,
    pub challenge: ProjectedChallengeContract,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct CalculatedSubjectChange {
    pub subject: SubjectKey,
    pub expected_previous: Option<ExpectedSubjectVersion>,
    pub semantic_change_cursor: Option<u64>,
    pub resulting: Option<DeltaSubjectResult>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct CalculatedGraphDelta {
    pub schema_version: String,
    pub delta_id: String,
    pub authority_effect: AuthorityEffect,
    pub from_semantic_cursor: u64,
    pub from_source_event_count: usize,
    pub from_source_event_set_digest: String,
    pub to_semantic_cursor: u64,
    pub to_source_event_count: usize,
    pub to_source_event_set_digest: String,
    pub changes: Vec<CalculatedSubjectChange>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct DeltaApplyReceipt {
    pub schema_version: String,
    pub delta_id: String,
    pub delta_digest: String,
    pub from_semantic_cursor: u64,
    pub to_semantic_cursor: u64,
    pub added: usize,
    pub updated: usize,
    pub removed: usize,
    pub governance_replaced: usize,
    pub transaction_strategy: String,
    pub staged_previous_subject_count: usize,
    pub full_model_clone: bool,
    pub resulting_index_digest: String,
    pub canonical_replay_source: bool,
    pub authority_effect: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct SnapshotPublicationReceipt {
    pub schema_version: String,
    pub from_generation: u64,
    pub published_generation: u64,
    pub from_semantic_cursor: u64,
    pub published_semantic_cursor: u64,
    pub published_index_digest: String,
    pub publication_strategy: String,
    pub staged_full_model_clone: bool,
    pub old_snapshots_remain_readable: bool,
    pub structural_sharing: StructuralSharingStats,
    pub delta: DeltaApplyReceipt,
    pub canonical_replay_source: bool,
    pub authority_effect: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct StructuralSharingStats {
    pub previous_subject_count: usize,
    pub shared_subject_count: usize,
    pub previous_challenge_contract_count: usize,
    pub shared_challenge_contract_count: usize,
    pub previous_index_bucket_count: usize,
    pub shared_index_bucket_count: usize,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct RecoveryExpectation {
    pub runtime_identity: String,
    pub semantic_cursor: u64,
    pub source_event_count: usize,
    pub source_event_set_digest: String,
    pub expected_index_digest: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct RecoveryReceipt {
    pub schema_version: String,
    pub recovery_strategy: String,
    pub runtime_identity: String,
    pub semantic_cursor: u64,
    pub source_event_count: usize,
    pub source_event_set_digest: String,
    pub rebuilt_index_digest: String,
    pub exact_index_digest_match: bool,
    pub checkpoint_used: bool,
    pub canonical_replay_source: bool,
    pub authority_effect: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct GraphCheckpointBody {
    pub runtime_identity: String,
    pub base_expectation: RecoveryExpectation,
    pub projection: ProjectionCheckpoint,
    pub tail_boundary: EventTailBoundary,
    pub challenges: Vec<ProjectedChallengeContract>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct GraphCheckpointEnvelope {
    pub schema_version: String,
    pub checkpoint_kind: String,
    pub canonical_replay_source: bool,
    pub authority_effect: String,
    pub body_digest_sha256: String,
    pub body: GraphCheckpointBody,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum AtomicCheckpointFault {
    None,
    AfterStageSync,
    AfterRenameBeforeDirectorySync,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct AtomicCheckpointWriteReceipt {
    pub schema_version: String,
    pub disposition: String,
    pub target_path: String,
    pub checkpoint_file_digest_sha256: String,
    pub checkpoint_body_digest_sha256: String,
    pub prior_semantic_cursor: Option<u64>,
    pub prior_governance_cursor: Option<u64>,
    pub semantic_cursor: u64,
    pub governance_cursor: u64,
    pub checkpoint_bytes: usize,
    pub replacement_strategy: String,
    pub staged_file_synced: bool,
    pub atomic_rename_completed: bool,
    pub parent_directory_synced: bool,
    pub canonical_replay_source: bool,
    pub authority_effect: String,
}

#[derive(Debug)]
struct PublishedGraphState {
    generation: u64,
    model: Arc<GraphReadModel>,
}

#[derive(Debug)]
pub struct ConcurrentGraphReadModel {
    state: RwLock<PublishedGraphState>,
    writer: Mutex<()>,
}

#[derive(Clone, Debug)]
pub struct GraphReadSnapshot {
    generation: u64,
    model: Arc<GraphReadModel>,
}

#[derive(Clone, Debug)]
pub struct CalculatedGraphBatch {
    pub delta: CalculatedGraphDelta,
    pub governance_cursor: u64,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct IngestionEnqueueReceipt {
    pub schema_version: String,
    pub disposition: String,
    pub code: String,
    pub delta_id: String,
    pub sequence: Option<u64>,
    pub semantic_cursor: u64,
    pub governance_cursor: u64,
    pub retryable: bool,
    pub queue_capacity: usize,
    pub pending_batch_count: usize,
    pub canonical_replay_source: bool,
    pub authority_effect: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum IngestionLifecycle {
    Paused,
    Running,
    Draining,
    Stopped,
    Failed,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct IngestionFailureRecord {
    pub sequence: u64,
    pub delta_id: String,
    pub code: String,
    pub detail: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct IngestionStatus {
    pub schema_version: String,
    pub lifecycle: IngestionLifecycle,
    pub queue_capacity: usize,
    pub accepted_batch_count: u64,
    pub projected_batch_count: u64,
    pub rejected_overload_count: u64,
    pub pending_batch_count: usize,
    pub maximum_pending_batch_count: usize,
    pub accepted_semantic_cursor: u64,
    pub projected_semantic_cursor: u64,
    pub semantic_cursor_lag: u64,
    pub accepted_governance_cursor: u64,
    pub projected_governance_cursor: u64,
    pub governance_cursor_lag: u64,
    pub last_projection_latency_ns: u128,
    pub maximum_projection_latency_ns: u128,
    pub failure: Option<IngestionFailureRecord>,
    pub canonical_replay_source: bool,
    pub authority_effect: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct IngestionShutdownReceipt {
    pub schema_version: String,
    pub result: String,
    pub accepted_batch_count: u64,
    pub projected_batch_count: u64,
    pub rejected_overload_count: u64,
    pub drained_exactly: bool,
    pub final_generation: u64,
    pub final_semantic_cursor: u64,
    pub final_governance_cursor: u64,
    pub final_index_digest: String,
    pub maximum_pending_batch_count: usize,
    pub maximum_projection_latency_ns: u128,
    pub canonical_replay_source: bool,
    pub authority_effect: String,
}

#[derive(Debug)]
struct IngestionMessage {
    sequence: u64,
    batch: CalculatedGraphBatch,
    accepted_at: Instant,
}

#[derive(Debug)]
struct IngestionControlState {
    lifecycle: IngestionLifecycle,
    accepted_batch_count: u64,
    projected_batch_count: u64,
    rejected_overload_count: u64,
    next_sequence: u64,
    maximum_pending_batch_count: usize,
    accepted_semantic_cursor: u64,
    projected_semantic_cursor: u64,
    accepted_governance_cursor: u64,
    projected_governance_cursor: u64,
    last_projection_latency_ns: u128,
    maximum_projection_latency_ns: u128,
    failure: Option<IngestionFailureRecord>,
}

#[derive(Debug)]
struct IngestionControl {
    state: Mutex<IngestionControlState>,
    changed: Condvar,
    worker_gate: Mutex<bool>,
    worker_gate_changed: Condvar,
}

#[derive(Debug)]
pub struct BoundedGraphIngestion {
    graph: Arc<ConcurrentGraphReadModel>,
    sender: Option<mpsc::SyncSender<IngestionMessage>>,
    accepted_delta_ids: BTreeSet<String>,
    control: Arc<IngestionControl>,
    worker: Option<JoinHandle<()>>,
    queue_capacity: usize,
}

impl ConcurrentGraphReadModel {
    pub fn new(model: GraphReadModel) -> Self {
        Self {
            state: RwLock::new(PublishedGraphState {
                generation: 0,
                model: Arc::new(model),
            }),
            writer: Mutex::new(()),
        }
    }

    pub fn snapshot(&self) -> Result<GraphReadSnapshot, GraphFailure> {
        let state = self.state.read().map_err(|_| {
            GraphFailure::new(
                "CONCURRENT_GRAPH_LOCK_POISONED",
                "read snapshot is unavailable",
            )
        })?;
        Ok(GraphReadSnapshot {
            generation: state.generation,
            model: Arc::clone(&state.model),
        })
    }

    pub fn apply_calculated_delta(
        &self,
        delta: &CalculatedGraphDelta,
    ) -> Result<SnapshotPublicationReceipt, GraphFailure> {
        let _writer = self.writer.lock().map_err(|_| {
            GraphFailure::new(
                "CONCURRENT_GRAPH_WRITER_POISONED",
                "delta staging is unavailable",
            )
        })?;
        let (from_generation, base) = {
            let state = self.state.read().map_err(|_| {
                GraphFailure::new(
                    "CONCURRENT_GRAPH_LOCK_POISONED",
                    "delta base snapshot is unavailable",
                )
            })?;
            (state.generation, Arc::clone(&state.model))
        };
        let published_generation = from_generation.checked_add(1).ok_or_else(|| {
            GraphFailure::new("PUBLICATION_GENERATION_EXHAUSTED", delta.delta_id.clone())
        })?;
        let from_semantic_cursor = base.metadata().semantic_cursor;
        let mut next = (*base).clone();
        let delta_receipt = next.apply_calculated_delta(delta)?;
        let structural_sharing = base.structural_sharing_with(&next);
        let published_semantic_cursor = next.metadata().semantic_cursor;
        let published_index_digest = next.metadata().index_digest.clone();
        let mut state = self.state.write().map_err(|_| {
            GraphFailure::new(
                "CONCURRENT_GRAPH_LOCK_POISONED",
                "delta publication is unavailable",
            )
        })?;
        if state.generation != from_generation || !Arc::ptr_eq(&state.model, &base) {
            return Err(GraphFailure::new(
                "PUBLICATION_BASE_CHANGED",
                delta.delta_id.clone(),
            ));
        }
        state.generation = published_generation;
        state.model = Arc::new(next);
        Ok(SnapshotPublicationReceipt {
            schema_version: "cal-graph-snapshot-publication-receipt/v1-prototype".to_owned(),
            from_generation,
            published_generation,
            from_semantic_cursor,
            published_semantic_cursor,
            published_index_digest,
            publication_strategy: "structurally_shared_arc_snapshot".to_owned(),
            staged_full_model_clone: false,
            old_snapshots_remain_readable: true,
            structural_sharing,
            delta: delta_receipt,
            canonical_replay_source: false,
            authority_effect: AUTHORITY_EFFECT.to_owned(),
        })
    }
}

impl BoundedGraphIngestion {
    pub fn new(
        model: GraphReadModel,
        initial_governance_cursor: u64,
        queue_capacity: usize,
    ) -> Result<Self, GraphFailure> {
        Self::build(model, initial_governance_cursor, queue_capacity, false)
    }

    pub fn new_paused(
        model: GraphReadModel,
        initial_governance_cursor: u64,
        queue_capacity: usize,
    ) -> Result<Self, GraphFailure> {
        Self::build(model, initial_governance_cursor, queue_capacity, true)
    }

    fn build(
        model: GraphReadModel,
        initial_governance_cursor: u64,
        queue_capacity: usize,
        paused: bool,
    ) -> Result<Self, GraphFailure> {
        if queue_capacity == 0 {
            return Err(GraphFailure::new(
                "INGESTION_QUEUE_CAPACITY_ZERO",
                "queue capacity must be greater than zero",
            ));
        }
        let initial_semantic_cursor = model.metadata().semantic_cursor;
        let graph = Arc::new(ConcurrentGraphReadModel::new(model));
        let control = Arc::new(IngestionControl {
            state: Mutex::new(IngestionControlState {
                lifecycle: if paused {
                    IngestionLifecycle::Paused
                } else {
                    IngestionLifecycle::Running
                },
                accepted_batch_count: 0,
                projected_batch_count: 0,
                rejected_overload_count: 0,
                next_sequence: 1,
                maximum_pending_batch_count: 0,
                accepted_semantic_cursor: initial_semantic_cursor,
                projected_semantic_cursor: initial_semantic_cursor,
                accepted_governance_cursor: initial_governance_cursor,
                projected_governance_cursor: initial_governance_cursor,
                last_projection_latency_ns: 0,
                maximum_projection_latency_ns: 0,
                failure: None,
            }),
            changed: Condvar::new(),
            worker_gate: Mutex::new(!paused),
            worker_gate_changed: Condvar::new(),
        });
        let (sender, receiver) = mpsc::sync_channel(queue_capacity);
        let worker_graph = Arc::clone(&graph);
        let worker_control = Arc::clone(&control);
        let worker = thread::Builder::new()
            .name("cal-graph-ingestion".to_owned())
            .spawn(move || ingestion_worker(worker_graph, worker_control, receiver))
            .map_err(|error| {
                GraphFailure::new("INGESTION_WORKER_START_FAILED", error.to_string())
            })?;
        Ok(Self {
            graph,
            sender: Some(sender),
            accepted_delta_ids: BTreeSet::new(),
            control,
            worker: Some(worker),
            queue_capacity,
        })
    }

    pub fn graph(&self) -> Arc<ConcurrentGraphReadModel> {
        Arc::clone(&self.graph)
    }

    pub fn resume(&self) -> Result<(), GraphFailure> {
        {
            let mut gate = self.control.worker_gate.lock().map_err(|_| {
                GraphFailure::new("INGESTION_CONTROL_POISONED", "worker gate unavailable")
            })?;
            *gate = true;
            self.control.worker_gate_changed.notify_all();
        }
        let mut state = self.control.state.lock().map_err(|_| {
            GraphFailure::new("INGESTION_CONTROL_POISONED", "ingestion state unavailable")
        })?;
        if state.lifecycle == IngestionLifecycle::Paused {
            state.lifecycle = IngestionLifecycle::Running;
            self.control.changed.notify_all();
        }
        Ok(())
    }

    pub fn enqueue(
        &mut self,
        batch: CalculatedGraphBatch,
    ) -> Result<IngestionEnqueueReceipt, GraphFailure> {
        let delta_id = batch.delta.delta_id.clone();
        let semantic_cursor = batch.delta.to_semantic_cursor;
        let governance_cursor = batch.governance_cursor;
        let mut state = self.control.state.lock().map_err(|_| {
            GraphFailure::new("INGESTION_CONTROL_POISONED", "ingestion state unavailable")
        })?;
        match state.lifecycle {
            IngestionLifecycle::Paused | IngestionLifecycle::Running => {}
            IngestionLifecycle::Failed => {
                let detail = state
                    .failure
                    .as_ref()
                    .map(|failure| format!("{}: {}", failure.code, failure.detail))
                    .unwrap_or_else(|| "worker failed without a receipt".to_owned());
                return Err(GraphFailure::new("INGESTION_WORKER_FAILED", detail));
            }
            IngestionLifecycle::Draining | IngestionLifecycle::Stopped => {
                return Err(GraphFailure::new(
                    "INGESTION_NOT_ACCEPTING",
                    format!("lifecycle is {:?}", state.lifecycle),
                ));
            }
        }
        if self.accepted_delta_ids.contains(&delta_id) {
            return Err(GraphFailure::new("INGESTION_DUPLICATE_DELTA", delta_id));
        }
        if batch.delta.from_semantic_cursor != state.accepted_semantic_cursor {
            return Err(GraphFailure::new(
                "INGESTION_SEMANTIC_WATERMARK_MISMATCH",
                format!(
                    "expected {}; received {} for {delta_id}",
                    state.accepted_semantic_cursor, batch.delta.from_semantic_cursor
                ),
            ));
        }
        if governance_cursor < state.accepted_governance_cursor {
            return Err(GraphFailure::new(
                "INGESTION_GOVERNANCE_WATERMARK_REGRESSION",
                format!(
                    "{} -> {governance_cursor} for {delta_id}",
                    state.accepted_governance_cursor
                ),
            ));
        }
        let sequence = state.next_sequence;
        let next_sequence = sequence
            .checked_add(1)
            .ok_or_else(|| GraphFailure::new("INGESTION_SEQUENCE_EXHAUSTED", delta_id.clone()))?;
        let message = IngestionMessage {
            sequence,
            batch,
            accepted_at: Instant::now(),
        };
        let sender = self
            .sender
            .as_ref()
            .ok_or_else(|| GraphFailure::new("INGESTION_NOT_ACCEPTING", "sender is closed"))?;
        match sender.try_send(message) {
            Ok(()) => {
                state.next_sequence = next_sequence;
                state.accepted_batch_count += 1;
                state.accepted_semantic_cursor = semantic_cursor;
                state.accepted_governance_cursor = governance_cursor;
                let pending = pending_batch_count(&state);
                state.maximum_pending_batch_count = state.maximum_pending_batch_count.max(pending);
                self.accepted_delta_ids.insert(delta_id.clone());
                self.control.changed.notify_all();
                Ok(IngestionEnqueueReceipt {
                    schema_version: "cal-graph-ingestion-enqueue-receipt/v1-prototype".to_owned(),
                    disposition: "accepted".to_owned(),
                    code: "INGESTION_ACCEPTED".to_owned(),
                    delta_id,
                    sequence: Some(sequence),
                    semantic_cursor,
                    governance_cursor,
                    retryable: false,
                    queue_capacity: self.queue_capacity,
                    pending_batch_count: pending,
                    canonical_replay_source: false,
                    authority_effect: AUTHORITY_EFFECT.to_owned(),
                })
            }
            Err(mpsc::TrySendError::Full(_)) => {
                state.rejected_overload_count += 1;
                Ok(IngestionEnqueueReceipt {
                    schema_version: "cal-graph-ingestion-enqueue-receipt/v1-prototype".to_owned(),
                    disposition: "rejected_overload".to_owned(),
                    code: "INGESTION_QUEUE_FULL".to_owned(),
                    delta_id,
                    sequence: None,
                    semantic_cursor,
                    governance_cursor,
                    retryable: true,
                    queue_capacity: self.queue_capacity,
                    pending_batch_count: pending_batch_count(&state),
                    canonical_replay_source: false,
                    authority_effect: AUTHORITY_EFFECT.to_owned(),
                })
            }
            Err(mpsc::TrySendError::Disconnected(_)) => {
                Err(GraphFailure::new("INGESTION_WORKER_UNAVAILABLE", delta_id))
            }
        }
    }

    pub fn status(&self) -> Result<IngestionStatus, GraphFailure> {
        let state = self.control.state.lock().map_err(|_| {
            GraphFailure::new("INGESTION_CONTROL_POISONED", "ingestion state unavailable")
        })?;
        Ok(ingestion_status(&state, self.queue_capacity))
    }

    pub fn wait_until_projected(
        &self,
        sequence: u64,
        timeout: Duration,
    ) -> Result<IngestionStatus, GraphFailure> {
        let deadline = Instant::now() + timeout;
        let mut state = self.control.state.lock().map_err(|_| {
            GraphFailure::new("INGESTION_CONTROL_POISONED", "ingestion state unavailable")
        })?;
        loop {
            if state.projected_batch_count >= sequence {
                return Ok(ingestion_status(&state, self.queue_capacity));
            }
            if let Some(failure) = &state.failure {
                return Err(GraphFailure::new(
                    "INGESTION_WORKER_FAILED",
                    format!("{}: {}", failure.code, failure.detail),
                ));
            }
            let now = Instant::now();
            if now >= deadline {
                return Err(GraphFailure::new(
                    "INGESTION_WAIT_TIMEOUT",
                    format!("sequence {sequence}"),
                ));
            }
            let wait = deadline.saturating_duration_since(now);
            let (next, timed) = self
                .control
                .changed
                .wait_timeout(state, wait)
                .map_err(|_| {
                    GraphFailure::new("INGESTION_CONTROL_POISONED", "projection wait unavailable")
                })?;
            state = next;
            if timed.timed_out() && state.projected_batch_count < sequence {
                return Err(GraphFailure::new(
                    "INGESTION_WAIT_TIMEOUT",
                    format!("sequence {sequence}"),
                ));
            }
        }
    }

    pub fn shutdown(mut self) -> Result<IngestionShutdownReceipt, GraphFailure> {
        self.close_and_join()?;
        let status = self.status()?;
        if let Some(failure) = status.failure {
            return Err(GraphFailure::new(
                "INGESTION_WORKER_FAILED",
                format!("{}: {}", failure.code, failure.detail),
            ));
        }
        let snapshot = self.graph.snapshot()?;
        let drained_exactly = status.accepted_batch_count == status.projected_batch_count
            && status.pending_batch_count == 0;
        if !drained_exactly {
            return Err(GraphFailure::new(
                "INGESTION_DRAIN_INCOMPLETE",
                format!(
                    "accepted {}; projected {}",
                    status.accepted_batch_count, status.projected_batch_count
                ),
            ));
        }
        Ok(IngestionShutdownReceipt {
            schema_version: "cal-graph-ingestion-shutdown-receipt/v1-prototype".to_owned(),
            result: "PASS".to_owned(),
            accepted_batch_count: status.accepted_batch_count,
            projected_batch_count: status.projected_batch_count,
            rejected_overload_count: status.rejected_overload_count,
            drained_exactly,
            final_generation: snapshot.generation(),
            final_semantic_cursor: snapshot.semantic_cursor(),
            final_governance_cursor: status.projected_governance_cursor,
            final_index_digest: snapshot.index_digest().to_owned(),
            maximum_pending_batch_count: status.maximum_pending_batch_count,
            maximum_projection_latency_ns: status.maximum_projection_latency_ns,
            canonical_replay_source: false,
            authority_effect: AUTHORITY_EFFECT.to_owned(),
        })
    }

    fn close_and_join(&mut self) -> Result<(), GraphFailure> {
        if self.worker.is_none() {
            return Ok(());
        }
        {
            let mut state = self.control.state.lock().map_err(|_| {
                GraphFailure::new("INGESTION_CONTROL_POISONED", "ingestion state unavailable")
            })?;
            if !matches!(state.lifecycle, IngestionLifecycle::Failed) {
                state.lifecycle = IngestionLifecycle::Draining;
            }
            self.control.changed.notify_all();
        }
        {
            let mut gate = self.control.worker_gate.lock().map_err(|_| {
                GraphFailure::new("INGESTION_CONTROL_POISONED", "worker gate unavailable")
            })?;
            *gate = true;
            self.control.worker_gate_changed.notify_all();
        }
        self.sender.take();
        if self
            .worker
            .take()
            .expect("worker existence checked")
            .join()
            .is_err()
        {
            return Err(GraphFailure::new(
                "INGESTION_WORKER_PANICKED",
                "projection worker did not close normally",
            ));
        }
        Ok(())
    }
}

impl Drop for BoundedGraphIngestion {
    fn drop(&mut self) {
        let _ = self.close_and_join();
    }
}

fn ingestion_worker(
    graph: Arc<ConcurrentGraphReadModel>,
    control: Arc<IngestionControl>,
    receiver: mpsc::Receiver<IngestionMessage>,
) {
    let mut gate = match control.worker_gate.lock() {
        Ok(gate) => gate,
        Err(_) => return,
    };
    while !*gate {
        gate = match control.worker_gate_changed.wait(gate) {
            Ok(gate) => gate,
            Err(_) => return,
        };
    }
    drop(gate);

    while let Ok(message) = receiver.recv() {
        let delta_id = message.batch.delta.delta_id.clone();
        match graph.apply_calculated_delta(&message.batch.delta) {
            Ok(_) => {
                let elapsed = message.accepted_at.elapsed().as_nanos();
                let mut state = match control.state.lock() {
                    Ok(state) => state,
                    Err(_) => return,
                };
                state.projected_batch_count = message.sequence;
                state.projected_semantic_cursor = message.batch.delta.to_semantic_cursor;
                state.projected_governance_cursor = message.batch.governance_cursor;
                state.last_projection_latency_ns = elapsed;
                state.maximum_projection_latency_ns =
                    state.maximum_projection_latency_ns.max(elapsed);
                control.changed.notify_all();
            }
            Err(failure) => {
                let mut state = match control.state.lock() {
                    Ok(state) => state,
                    Err(_) => return,
                };
                state.lifecycle = IngestionLifecycle::Failed;
                state.failure = Some(IngestionFailureRecord {
                    sequence: message.sequence,
                    delta_id,
                    code: failure.code,
                    detail: failure.detail,
                });
                control.changed.notify_all();
                return;
            }
        }
    }
    if let Ok(mut state) = control.state.lock() {
        if state.lifecycle != IngestionLifecycle::Failed {
            state.lifecycle = IngestionLifecycle::Stopped;
        }
        control.changed.notify_all();
    }
}

fn pending_batch_count(state: &IngestionControlState) -> usize {
    state
        .accepted_batch_count
        .saturating_sub(state.projected_batch_count) as usize
}

fn ingestion_status(state: &IngestionControlState, queue_capacity: usize) -> IngestionStatus {
    IngestionStatus {
        schema_version: "cal-graph-ingestion-status/v1-prototype".to_owned(),
        lifecycle: state.lifecycle.clone(),
        queue_capacity,
        accepted_batch_count: state.accepted_batch_count,
        projected_batch_count: state.projected_batch_count,
        rejected_overload_count: state.rejected_overload_count,
        pending_batch_count: pending_batch_count(state),
        maximum_pending_batch_count: state.maximum_pending_batch_count,
        accepted_semantic_cursor: state.accepted_semantic_cursor,
        projected_semantic_cursor: state.projected_semantic_cursor,
        semantic_cursor_lag: state
            .accepted_semantic_cursor
            .saturating_sub(state.projected_semantic_cursor),
        accepted_governance_cursor: state.accepted_governance_cursor,
        projected_governance_cursor: state.projected_governance_cursor,
        governance_cursor_lag: state
            .accepted_governance_cursor
            .saturating_sub(state.projected_governance_cursor),
        last_projection_latency_ns: state.last_projection_latency_ns,
        maximum_projection_latency_ns: state.maximum_projection_latency_ns,
        failure: state.failure.clone(),
        canonical_replay_source: false,
        authority_effect: AUTHORITY_EFFECT.to_owned(),
    }
}

impl GraphReadSnapshot {
    pub fn generation(&self) -> u64 {
        self.generation
    }

    pub fn semantic_cursor(&self) -> u64 {
        self.model.metadata().semantic_cursor
    }

    pub fn index_digest(&self) -> &str {
        &self.model.metadata().index_digest
    }

    pub fn model(&self) -> &GraphReadModel {
        &self.model
    }
}

impl Deref for GraphReadSnapshot {
    type Target = GraphReadModel;

    fn deref(&self) -> &Self::Target {
        self.model()
    }
}

#[derive(Clone, Debug)]
struct DeltaRollbackEntry {
    subject: ProjectedSubject,
    challenge: ChallengeContract,
}

type SharedSubjects = Arc<BTreeMap<SubjectKey, Arc<ProjectedSubject>>>;
type SharedChallenges = Arc<BTreeMap<SubjectKey, Arc<ChallengeContract>>>;
type SharedIndex<K> = Arc<BTreeMap<K, Arc<BTreeSet<SubjectKey>>>>;

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
struct DigestMaterial {
    semantic_cursor: u64,
    source_event_count: usize,
    source_event_set_digest: String,
    subjects: Vec<ProjectedSubject>,
    challenge_contracts: Vec<ChallengeView>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct GraphReadModel {
    metadata: GraphReadModelMetadata,
    subjects: SharedSubjects,
    challenge_contracts: SharedChallenges,
    by_type: SharedIndex<(String, String)>,
    by_property: SharedIndex<(String, String, String)>,
    outgoing: SharedIndex<(SubjectKey, String)>,
    incoming: SharedIndex<(SubjectKey, String)>,
    outgoing_relations: SharedIndex<(SubjectKey, String)>,
    incoming_relations: SharedIndex<(SubjectKey, String)>,
    context_members: SharedIndex<(String, String)>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct GraphFailure {
    pub code: String,
    pub detail: String,
}

impl GraphFailure {
    fn new(code: &str, detail: impl Into<String>) -> Self {
        Self {
            code: code.to_owned(),
            detail: detail.into(),
        }
    }
}

impl From<ReplayFailure> for GraphFailure {
    fn from(failure: ReplayFailure) -> Self {
        Self::new(&failure.code, failure.detail)
    }
}

impl Display for GraphFailure {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(formatter, "{}: {}", self.code, self.detail)
    }
}

impl Error for GraphFailure {}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum ChangeKind {
    Added,
    Updated,
    Removed,
    GovernanceReplaced,
}

impl GraphReadModel {
    pub fn rebuild(store: &EventStore, cursor: u64) -> Result<Self, GraphFailure> {
        let cut = store.ontology_at(cursor)?;
        let subjects = subject_map(&cut.subjects)?;
        let challenge_contracts = exact_governance_joins(store, &subjects)?;
        Self::from_verified_cut(cut, subjects, challenge_contracts)
    }

    pub fn from_calculated_cut(
        cut: cal_ontology_lifecycle::ConsistentOntologyCut,
        projected_challenges: Vec<ProjectedChallengeContract>,
    ) -> Result<Self, GraphFailure> {
        let subjects = subject_map(&cut.subjects)?;
        let mut challenge_contracts = BTreeMap::new();
        for projected in projected_challenges {
            let subject = subjects.get(&projected.subject).ok_or_else(|| {
                GraphFailure::new(
                    "GOVERNANCE_SUBJECT_NOT_IN_CUT",
                    projected.subject.subject_id.clone(),
                )
            })?;
            if projected.semantic_event_id != subject.source_event_id
                || projected.semantic_event_digest != subject.source_event_digest
                || projected.semantic_cursor != subject.source_cursor
            {
                return Err(GraphFailure::new(
                    "GOVERNANCE_REFERENCE_MISMATCH",
                    projected.subject.subject_id.clone(),
                ));
            }
            if challenge_contracts
                .insert(projected.subject.clone(), projected.contract)
                .is_some()
            {
                return Err(GraphFailure::new(
                    "DUPLICATE_GOVERNANCE_SUBJECT",
                    projected.subject.subject_id,
                ));
            }
        }
        if challenge_contracts.len() != subjects.len() {
            let missing = subjects
                .keys()
                .find(|key| !challenge_contracts.contains_key(*key))
                .map(|key| key.subject_id.clone())
                .unwrap_or_else(|| "unknown".to_owned());
            return Err(GraphFailure::new("EXACT_GOVERNANCE_STATE_MISSING", missing));
        }
        Self::from_verified_cut(cut, subjects, challenge_contracts)
    }

    pub fn recover_from_calculated_cut(
        cut: cal_ontology_lifecycle::ConsistentOntologyCut,
        projected_challenges: Vec<ProjectedChallengeContract>,
        expectation: &RecoveryExpectation,
    ) -> Result<(Self, RecoveryReceipt), GraphFailure> {
        validate_recovery_runtime(expectation)?;
        if cut.semantic_cursor != expectation.semantic_cursor
            || cut.source_event_count != expectation.source_event_count
            || cut.source_event_set_digest != expectation.source_event_set_digest
        {
            return Err(GraphFailure::new(
                "RECOVERY_SOURCE_ENVELOPE_MISMATCH",
                format!(
                    "expected cursor {} count {} digest {}; received cursor {} count {} digest {}",
                    expectation.semantic_cursor,
                    expectation.source_event_count,
                    expectation.source_event_set_digest,
                    cut.semantic_cursor,
                    cut.source_event_count,
                    cut.source_event_set_digest
                ),
            ));
        }
        let model = Self::from_calculated_cut(cut, projected_challenges)?;
        let receipt = recovery_receipt(
            &model,
            expectation,
            "full_rebuild_from_verified_calculated_cut",
            false,
        )?;
        Ok((model, receipt))
    }

    pub fn recover_from_event_store(
        store: &EventStore,
        expectation: &RecoveryExpectation,
    ) -> Result<(Self, RecoveryReceipt), GraphFailure> {
        validate_recovery_runtime(expectation)?;
        let model = Self::rebuild(store, expectation.semantic_cursor)?;
        let receipt = recovery_receipt(
            &model,
            expectation,
            "full_rebuild_from_canonical_event_files",
            false,
        )?;
        Ok((model, receipt))
    }

    pub fn create_checkpoint(
        store: &EventStore,
        semantic_cursor: u64,
        governance_cursor: u64,
    ) -> Result<GraphCheckpointEnvelope, GraphFailure> {
        let projection = store.checkpoint_at(semantic_cursor)?;
        let tail_boundary = store.tail_boundary_at(semantic_cursor, governance_cursor)?;
        let model = Self::rebuild(store, semantic_cursor)?;
        let base_expectation = RecoveryExpectation {
            runtime_identity: RUNTIME_IDENTITY.to_owned(),
            semantic_cursor: model.metadata.semantic_cursor,
            source_event_count: model.metadata.source_event_count,
            source_event_set_digest: model.metadata.source_event_set_digest.clone(),
            expected_index_digest: model.metadata.index_digest.clone(),
        };
        let body = GraphCheckpointBody {
            runtime_identity: RUNTIME_IDENTITY.to_owned(),
            base_expectation,
            projection,
            tail_boundary,
            challenges: model.projected_challenges(),
        };
        let body_digest_sha256 = digest_serializable(&body)?;
        Ok(GraphCheckpointEnvelope {
            schema_version: "cal-graph-checkpoint-envelope/v1-prototype".to_owned(),
            checkpoint_kind: "disposable-calculated-read-model-cache".to_owned(),
            canonical_replay_source: false,
            authority_effect: AUTHORITY_EFFECT.to_owned(),
            body_digest_sha256,
            body,
        })
    }

    pub fn recover_from_checkpoint_and_tail(
        checkpoint: &GraphCheckpointEnvelope,
        tail: &EventTail,
        expectation: &RecoveryExpectation,
    ) -> Result<(Self, RecoveryReceipt), GraphFailure> {
        validate_checkpoint(checkpoint)?;
        if tail.boundary() != &checkpoint.body.tail_boundary {
            return Err(GraphFailure::new(
                "CHECKPOINT_TAIL_BOUNDARY_MISMATCH",
                checkpoint.body.projection.source_cursor.to_string(),
            ));
        }
        let final_cut = tail.ontology_from_checkpoint(&checkpoint.body.projection)?;
        let challenges = checkpoint_challenges_after_tail(checkpoint, tail, &final_cut)?;
        let model = Self::from_calculated_cut(final_cut, challenges)?;
        let receipt = recovery_receipt(
            &model,
            expectation,
            "verified_disposable_checkpoint_plus_canonical_event_tail",
            true,
        )?;
        Ok((model, receipt))
    }

    pub fn projected_challenges(&self) -> Vec<ProjectedChallengeContract> {
        self.subjects
            .iter()
            .filter_map(|(key, subject)| {
                self.challenge_contracts
                    .get(key)
                    .map(|contract| ProjectedChallengeContract {
                        subject: key.clone(),
                        semantic_event_id: subject.source_event_id.clone(),
                        semantic_event_digest: subject.source_event_digest.clone(),
                        semantic_cursor: subject.source_cursor,
                        contract: contract.as_ref().clone(),
                    })
            })
            .collect()
    }

    pub fn advance(&mut self, store: &EventStore, target_cursor: u64) -> Result<(), GraphFailure> {
        if target_cursor < self.metadata.semantic_cursor {
            return Err(GraphFailure::new(
                "READ_MODEL_CURSOR_REGRESSION",
                format!("{} -> {target_cursor}", self.metadata.semantic_cursor),
            ));
        }
        if target_cursor == self.metadata.semantic_cursor {
            return Ok(());
        }

        let mut next_subjects = self
            .subjects
            .iter()
            .map(|(key, subject)| (key.clone(), subject.as_ref().clone()))
            .collect::<BTreeMap<_, _>>();
        for loaded in store.semantic_events().iter().filter(|loaded| {
            loaded.event.semantic_cursor > self.metadata.semantic_cursor
                && loaded.event.semantic_cursor <= target_cursor
        }) {
            let key = SubjectKey::new(
                loaded.event.subject_identity.ontology_id.clone(),
                loaded.event.subject_identity.subject_id.clone(),
            );
            next_subjects.remove(&key);
            if loaded.event.complete_resulting_semantic_state.lifecycle() == Lifecycle::Active {
                next_subjects.insert(
                    key,
                    ProjectedSubject {
                        identity: loaded.event.subject_identity.clone(),
                        source_event_id: loaded.event.event_id.clone(),
                        source_event_digest: loaded.event.event_digest.clone(),
                        source_cursor: loaded.event.semantic_cursor,
                        semantic_state: loaded.event.complete_resulting_semantic_state.clone(),
                    },
                );
            }
        }

        let cut = store.ontology_at(target_cursor)?;
        let expected = cut
            .subjects
            .iter()
            .cloned()
            .map(|subject| (SubjectKey::of(&subject), subject))
            .collect::<BTreeMap<_, _>>();
        if next_subjects != expected {
            return Err(GraphFailure::new(
                "INCREMENTAL_REBUILD_DIVERGENCE",
                format!("incremental state differs from canonical cut {target_cursor}"),
            ));
        }
        let subjects = subject_map(&cut.subjects)?;
        let challenge_contracts = exact_governance_joins(store, &subjects)?;
        *self = Self::from_verified_cut(cut, subjects, challenge_contracts)?;
        Ok(())
    }

    pub fn expected_subject_version(
        &self,
        key: &SubjectKey,
    ) -> Result<Option<ExpectedSubjectVersion>, GraphFailure> {
        self.subjects
            .get(key)
            .map(|subject| {
                let contract = self.challenge_contracts.get(key).ok_or_else(|| {
                    GraphFailure::new("EXACT_GOVERNANCE_STATE_MISSING", key.subject_id.clone())
                })?;
                Ok(ExpectedSubjectVersion {
                    subject: key.clone(),
                    semantic_event_id: subject.source_event_id.clone(),
                    semantic_event_digest: subject.source_event_digest.clone(),
                    semantic_cursor: subject.source_cursor,
                    challenge_contract_digest: digest_serializable(contract.as_ref())?,
                })
            })
            .transpose()
    }

    pub fn apply_calculated_delta(
        &mut self,
        delta: &CalculatedGraphDelta,
    ) -> Result<DeltaApplyReceipt, GraphFailure> {
        self.validate_delta_envelope(delta)?;
        let mut semantic_cursors = BTreeSet::new();
        let mut previous_key: Option<&SubjectKey> = None;
        let mut added = 0;
        let mut updated = 0;
        let mut removed = 0;
        let mut governance_replaced = 0;

        for change in &delta.changes {
            if previous_key.is_some_and(|previous| previous >= &change.subject) {
                return Err(GraphFailure::new(
                    "DELTA_CHANGES_NOT_STRICTLY_ORDERED",
                    change.subject.subject_id.clone(),
                ));
            }
            previous_key = Some(&change.subject);
            self.validate_subject_change(change)?;
            let semantic_change = semantic_change_kind(change)?;
            match semantic_change {
                ChangeKind::Added => added += 1,
                ChangeKind::Updated => updated += 1,
                ChangeKind::Removed => removed += 1,
                ChangeKind::GovernanceReplaced => governance_replaced += 1,
            }
            if semantic_change != ChangeKind::GovernanceReplaced {
                let cursor = change.semantic_change_cursor.ok_or_else(|| {
                    GraphFailure::new(
                        "SEMANTIC_CHANGE_CURSOR_MISSING",
                        change.subject.subject_id.clone(),
                    )
                })?;
                if cursor <= delta.from_semantic_cursor || cursor > delta.to_semantic_cursor {
                    return Err(GraphFailure::new(
                        "SEMANTIC_CHANGE_CURSOR_OUT_OF_RANGE",
                        format!("{} at {cursor}", change.subject.subject_id),
                    ));
                }
                if !semantic_cursors.insert(cursor) {
                    return Err(GraphFailure::new(
                        "SEMANTIC_CHANGE_CURSOR_DUPLICATE",
                        cursor.to_string(),
                    ));
                }
                if let Some(resulting) = &change.resulting
                    && resulting.subject.source_cursor != cursor
                {
                    return Err(GraphFailure::new(
                        "RESULTING_SUBJECT_CURSOR_MISMATCH",
                        change.subject.subject_id.clone(),
                    ));
                }
            } else if change.semantic_change_cursor.is_some() {
                return Err(GraphFailure::new(
                    "GOVERNANCE_CHANGE_HAS_SEMANTIC_CURSOR",
                    change.subject.subject_id.clone(),
                ));
            }
        }

        let semantic_change_count = added + updated + removed;
        if delta.to_semantic_cursor != delta.from_semantic_cursor + semantic_change_count as u64
            || delta.to_source_event_count != delta.from_source_event_count + semantic_change_count
        {
            return Err(GraphFailure::new(
                "DELTA_SEMANTIC_COUNT_MISMATCH",
                format!("declared {semantic_change_count} semantic changes"),
            ));
        }
        let expected_cursors =
            ((delta.from_semantic_cursor + 1)..=delta.to_semantic_cursor).collect::<BTreeSet<_>>();
        if semantic_cursors != expected_cursors {
            return Err(GraphFailure::new(
                "DELTA_SEMANTIC_CURSOR_GAP",
                delta.delta_id.clone(),
            ));
        }

        validate_delta_relation_endpoints(&self.subjects, &delta.changes)?;
        let calculated_digest = projection_digest_after_delta(&self.subjects, &delta.changes)?;
        if calculated_digest != delta.to_source_event_set_digest {
            return Err(GraphFailure::new(
                "DELTA_TARGET_PROJECTION_DIGEST_MISMATCH",
                format!(
                    "expected {}; calculated {calculated_digest}",
                    delta.to_source_event_set_digest
                ),
            ));
        }
        let delta_digest = digest_serializable(delta)?;
        let previous_metadata = self.metadata.clone();
        let rollback = self.delta_rollback_journal(&delta.changes)?;
        if let Err(failure) = self.commit_calculated_delta(delta) {
            self.restore_delta(&delta.changes, &rollback, previous_metadata)?;
            return Err(failure);
        }
        self.metadata.semantic_cursor = delta.to_semantic_cursor;
        self.metadata.source_event_count = delta.to_source_event_count;
        self.metadata.source_event_set_digest = delta.to_source_event_set_digest.clone();
        self.metadata.exact_governance_join_count = self.challenge_contracts.len();
        match self.calculate_digest() {
            Ok(digest) => self.metadata.index_digest = digest,
            Err(failure) => {
                self.restore_delta(&delta.changes, &rollback, previous_metadata)?;
                return Err(failure);
            }
        }
        let resulting_index_digest = self.metadata.index_digest.clone();
        Ok(DeltaApplyReceipt {
            schema_version: "cal-graph-delta-apply-receipt/v1-prototype".to_owned(),
            delta_id: delta.delta_id.clone(),
            delta_digest,
            from_semantic_cursor: delta.from_semantic_cursor,
            to_semantic_cursor: delta.to_semantic_cursor,
            added,
            updated,
            removed,
            governance_replaced,
            transaction_strategy: "bounded_rollback_journal".to_owned(),
            staged_previous_subject_count: rollback.len(),
            full_model_clone: false,
            resulting_index_digest,
            canonical_replay_source: false,
            authority_effect: AUTHORITY_EFFECT.to_owned(),
        })
    }

    fn delta_rollback_journal(
        &self,
        changes: &[CalculatedSubjectChange],
    ) -> Result<BTreeMap<SubjectKey, DeltaRollbackEntry>, GraphFailure> {
        changes
            .iter()
            .filter_map(|change| {
                self.subjects.get(&change.subject).map(|subject| {
                    let challenge =
                        self.challenge_contracts
                            .get(&change.subject)
                            .ok_or_else(|| {
                                GraphFailure::new(
                                    "EXACT_GOVERNANCE_STATE_MISSING",
                                    change.subject.subject_id.clone(),
                                )
                            })?;
                    Ok((
                        change.subject.clone(),
                        DeltaRollbackEntry {
                            subject: subject.as_ref().clone(),
                            challenge: challenge.as_ref().clone(),
                        },
                    ))
                })
            })
            .collect()
    }

    fn commit_calculated_delta(
        &mut self,
        delta: &CalculatedGraphDelta,
    ) -> Result<(), GraphFailure> {
        for change in &delta.changes {
            match semantic_change_kind(change)? {
                ChangeKind::GovernanceReplaced => {
                    let contract = change
                        .resulting
                        .as_ref()
                        .expect("validated governance replacement has a result")
                        .challenge
                        .contract
                        .clone();
                    Arc::make_mut(&mut self.challenge_contracts)
                        .insert(change.subject.clone(), Arc::new(contract));
                }
                ChangeKind::Added => {
                    let resulting = change
                        .resulting
                        .as_ref()
                        .expect("validated addition has a result");
                    self.insert_subject(
                        resulting.subject.clone(),
                        resulting.challenge.contract.clone(),
                    )?;
                }
                ChangeKind::Updated => {
                    self.remove_subject(&change.subject)?;
                    let resulting = change
                        .resulting
                        .as_ref()
                        .expect("validated update has a result");
                    self.insert_subject(
                        resulting.subject.clone(),
                        resulting.challenge.contract.clone(),
                    )?;
                }
                ChangeKind::Removed => self.remove_subject(&change.subject)?,
            }
        }
        Ok(())
    }

    fn restore_delta(
        &mut self,
        changes: &[CalculatedSubjectChange],
        rollback: &BTreeMap<SubjectKey, DeltaRollbackEntry>,
        previous_metadata: GraphReadModelMetadata,
    ) -> Result<(), GraphFailure> {
        for change in changes.iter().rev() {
            if self.subjects.contains_key(&change.subject) {
                self.remove_subject(&change.subject)?;
            }
        }
        for (key, entry) in rollback {
            debug_assert_eq!(key, &SubjectKey::of(&entry.subject));
            self.insert_subject(entry.subject.clone(), entry.challenge.clone())?;
        }
        self.metadata = previous_metadata;
        Ok(())
    }

    fn validate_delta_envelope(&self, delta: &CalculatedGraphDelta) -> Result<(), GraphFailure> {
        if delta.schema_version != "cal-calculated-graph-delta/v1-prototype" {
            return Err(GraphFailure::new(
                "DELTA_SCHEMA_VERSION_UNSUPPORTED",
                delta.schema_version.clone(),
            ));
        }
        if delta.authority_effect != AuthorityEffect::None {
            return Err(GraphFailure::new(
                "DELTA_AUTHORITY_EFFECT_FORBIDDEN",
                delta.delta_id.clone(),
            ));
        }
        if delta.changes.is_empty() {
            return Err(GraphFailure::new("DELTA_EMPTY", delta.delta_id.clone()));
        }
        if delta.from_semantic_cursor != self.metadata.semantic_cursor
            || delta.from_source_event_count != self.metadata.source_event_count
            || delta.from_source_event_set_digest != self.metadata.source_event_set_digest
        {
            return Err(GraphFailure::new(
                "DELTA_BASE_MISMATCH",
                delta.delta_id.clone(),
            ));
        }
        if delta.to_semantic_cursor < delta.from_semantic_cursor
            || delta.to_source_event_count < delta.from_source_event_count
        {
            return Err(GraphFailure::new(
                "DELTA_TARGET_REGRESSION",
                delta.delta_id.clone(),
            ));
        }
        Ok(())
    }

    fn validate_subject_change(
        &self,
        change: &CalculatedSubjectChange,
    ) -> Result<(), GraphFailure> {
        let current_subject = self.subjects.get(&change.subject);
        let current_contract = self.challenge_contracts.get(&change.subject);
        match (&change.expected_previous, current_subject, current_contract) {
            (None, None, None) => {}
            (None, _, _) => {
                return Err(GraphFailure::new(
                    "DELTA_ADDITION_ALREADY_EXISTS",
                    change.subject.subject_id.clone(),
                ));
            }
            (Some(expected), Some(subject), Some(contract)) => {
                if expected.subject != change.subject
                    || expected.semantic_event_id != subject.source_event_id
                    || expected.semantic_event_digest != subject.source_event_digest
                    || expected.semantic_cursor != subject.source_cursor
                    || expected.challenge_contract_digest != digest_serializable(contract.as_ref())?
                {
                    return Err(GraphFailure::new(
                        "DELTA_EXPECTED_VERSION_MISMATCH",
                        change.subject.subject_id.clone(),
                    ));
                }
            }
            (Some(_), _, _) => {
                return Err(GraphFailure::new(
                    "DELTA_EXPECTED_SUBJECT_MISSING",
                    change.subject.subject_id.clone(),
                ));
            }
        }
        if let Some(resulting) = &change.resulting {
            if SubjectKey::of(&resulting.subject) != change.subject {
                return Err(GraphFailure::new(
                    "DELTA_RESULT_SUBJECT_MISMATCH",
                    change.subject.subject_id.clone(),
                ));
            }
            if resulting.subject.semantic_state.lifecycle() != Lifecycle::Active {
                return Err(GraphFailure::new(
                    "DELTA_RESULT_NOT_ACTIVE",
                    change.subject.subject_id.clone(),
                ));
            }
            if current_subject.is_some_and(|current| {
                current.identity.subject_kind != resulting.subject.identity.subject_kind
            }) {
                return Err(GraphFailure::new(
                    "DELTA_SUBJECT_KIND_CHANGED",
                    change.subject.subject_id.clone(),
                ));
            }
            validate_indexable_subject(&resulting.subject)?;
            validate_projected_challenge(&resulting.subject, &resulting.challenge)?;
            if let Some(current) = current_subject {
                let same_semantic_version = current.source_event_id
                    == resulting.subject.source_event_id
                    && current.source_event_digest == resulting.subject.source_event_digest
                    && current.source_cursor == resulting.subject.source_cursor;
                if same_semantic_version && current.as_ref() != &resulting.subject {
                    return Err(GraphFailure::new(
                        "GOVERNANCE_CHANGE_MUTATES_SEMANTIC_STATE",
                        change.subject.subject_id.clone(),
                    ));
                }
            }
            if current_subject.map(Arc::as_ref) == Some(&resulting.subject)
                && current_contract.map(Arc::as_ref) == Some(&resulting.challenge.contract)
            {
                return Err(GraphFailure::new(
                    "DELTA_CHANGE_IS_NO_OP",
                    change.subject.subject_id.clone(),
                ));
            }
        } else if change.expected_previous.is_none() {
            return Err(GraphFailure::new(
                "DELTA_CHANGE_HAS_NO_PRIOR_OR_RESULT",
                change.subject.subject_id.clone(),
            ));
        }
        Ok(())
    }

    fn from_verified_cut(
        cut: cal_ontology_lifecycle::ConsistentOntologyCut,
        subjects: BTreeMap<SubjectKey, ProjectedSubject>,
        challenge_contracts: BTreeMap<SubjectKey, ChallengeContract>,
    ) -> Result<Self, GraphFailure> {
        if cut.authority_effect != AuthorityEffect::None {
            return Err(GraphFailure::new(
                "READ_MODEL_AUTHORITY_EFFECT_FORBIDDEN",
                format!(
                    "unexpected authority effect at cursor {}",
                    cut.semantic_cursor
                ),
            ));
        }
        let subjects: SharedSubjects = Arc::new(
            subjects
                .into_iter()
                .map(|(key, subject)| (key, Arc::new(subject)))
                .collect(),
        );
        validate_active_relation_endpoints(&subjects)?;
        let challenge_contracts: SharedChallenges = Arc::new(
            challenge_contracts
                .into_iter()
                .map(|(key, contract)| (key, Arc::new(contract)))
                .collect(),
        );
        let mut model = Self {
            metadata: GraphReadModelMetadata {
                schema_version: "cal-ontology-graph-read-model/v1-prototype".to_owned(),
                candidate_id: CANDIDATE_ID.to_owned(),
                runtime_identity: RUNTIME_IDENTITY.to_owned(),
                canonical_replay_source: false,
                authority_effect: AUTHORITY_EFFECT.to_owned(),
                semantic_cursor: cut.semantic_cursor,
                source_event_count: cut.source_event_count,
                source_event_set_digest: cut.source_event_set_digest,
                node_count: 0,
                relation_count: 0,
                exact_governance_join_count: challenge_contracts.len(),
                index_digest: String::new(),
            },
            subjects,
            challenge_contracts,
            by_type: Arc::new(BTreeMap::new()),
            by_property: Arc::new(BTreeMap::new()),
            outgoing: Arc::new(BTreeMap::new()),
            incoming: Arc::new(BTreeMap::new()),
            outgoing_relations: Arc::new(BTreeMap::new()),
            incoming_relations: Arc::new(BTreeMap::new()),
            context_members: Arc::new(BTreeMap::new()),
        };
        model.build_indices()?;
        model.metadata.index_digest = model.calculate_digest()?;
        Ok(model)
    }

    fn build_indices(&mut self) -> Result<(), GraphFailure> {
        let subjects = self.subjects.values().cloned().collect::<Vec<_>>();
        for subject in &subjects {
            let key = SubjectKey::of(subject);
            shared_index_insert(
                &mut self.by_type,
                (key.ontology_id.clone(), subject.identity.type_ref.clone()),
                key.clone(),
            );
            match &subject.semantic_state {
                OntologySemanticState::Node(node) => {
                    self.metadata.node_count += 1;
                    index_properties(&mut self.by_property, &key, &node.typed_properties.values)?;
                    index_context_properties(
                        &mut self.context_members,
                        &key,
                        &node.typed_properties.values,
                    );
                }
                OntologySemanticState::Relation(relation) => {
                    self.metadata.relation_count += 1;
                    index_properties(
                        &mut self.by_property,
                        &key,
                        &relation.typed_properties.values,
                    )?;
                    index_context_properties(
                        &mut self.context_members,
                        &key,
                        &relation.typed_properties.values,
                    );
                    let source = SubjectKey::new(&key.ontology_id, &relation.source_node_id);
                    let target = SubjectKey::new(&key.ontology_id, &relation.target_node_id);
                    let relation_type = subject.identity.type_ref.clone();
                    shared_index_insert(
                        &mut self.outgoing,
                        (source.clone(), relation_type.clone()),
                        target.clone(),
                    );
                    shared_index_insert(
                        &mut self.incoming,
                        (target.clone(), relation_type.clone()),
                        source.clone(),
                    );
                    shared_index_insert(
                        &mut self.outgoing_relations,
                        (source, relation_type.clone()),
                        key.clone(),
                    );
                    shared_index_insert(
                        &mut self.incoming_relations,
                        (target.clone(), relation_type.clone()),
                        key.clone(),
                    );
                    if relation_type == "belongs_to" {
                        shared_index_insert(
                            &mut self.context_members,
                            (key.ontology_id.clone(), target.subject_id),
                            SubjectKey::new(&key.ontology_id, &relation.source_node_id),
                        );
                    }
                }
            }
        }
        Ok(())
    }

    fn insert_subject(
        &mut self,
        subject: ProjectedSubject,
        challenge: ChallengeContract,
    ) -> Result<(), GraphFailure> {
        let key = SubjectKey::of(&subject);
        if self.subjects.contains_key(&key) {
            return Err(GraphFailure::new(
                "DELTA_INSERT_SUBJECT_ALREADY_EXISTS",
                key.subject_id,
            ));
        }
        self.index_subject(&key, &subject)?;
        Arc::make_mut(&mut self.subjects).insert(key.clone(), Arc::new(subject));
        Arc::make_mut(&mut self.challenge_contracts).insert(key, Arc::new(challenge));
        Ok(())
    }

    fn index_subject(
        &mut self,
        key: &SubjectKey,
        subject: &ProjectedSubject,
    ) -> Result<(), GraphFailure> {
        shared_index_insert(
            &mut self.by_type,
            (key.ontology_id.clone(), subject.identity.type_ref.clone()),
            key.clone(),
        );
        match &subject.semantic_state {
            OntologySemanticState::Node(node) => {
                self.metadata.node_count += 1;
                index_properties(&mut self.by_property, key, &node.typed_properties.values)?;
                index_context_properties(
                    &mut self.context_members,
                    key,
                    &node.typed_properties.values,
                );
            }
            OntologySemanticState::Relation(relation) => {
                self.metadata.relation_count += 1;
                index_properties(
                    &mut self.by_property,
                    key,
                    &relation.typed_properties.values,
                )?;
                index_context_properties(
                    &mut self.context_members,
                    key,
                    &relation.typed_properties.values,
                );
                let source = SubjectKey::new(&key.ontology_id, &relation.source_node_id);
                let target = SubjectKey::new(&key.ontology_id, &relation.target_node_id);
                let relation_type = subject.identity.type_ref.clone();
                shared_index_insert(
                    &mut self.outgoing,
                    (source.clone(), relation_type.clone()),
                    target.clone(),
                );
                shared_index_insert(
                    &mut self.incoming,
                    (target.clone(), relation_type.clone()),
                    source.clone(),
                );
                shared_index_insert(
                    &mut self.outgoing_relations,
                    (source, relation_type.clone()),
                    key.clone(),
                );
                shared_index_insert(
                    &mut self.incoming_relations,
                    (target.clone(), relation_type.clone()),
                    key.clone(),
                );
                if relation_type == "belongs_to" {
                    shared_index_insert(
                        &mut self.context_members,
                        (key.ontology_id.clone(), target.subject_id),
                        SubjectKey::new(&key.ontology_id, &relation.source_node_id),
                    );
                }
            }
        }
        Ok(())
    }

    fn remove_subject(&mut self, key: &SubjectKey) -> Result<(), GraphFailure> {
        let subject = self.subjects.get(key).cloned().ok_or_else(|| {
            GraphFailure::new("DELTA_REMOVE_SUBJECT_MISSING", key.subject_id.clone())
        })?;
        remove_index_value(
            &mut self.by_type,
            &(key.ontology_id.clone(), subject.identity.type_ref.clone()),
            key,
        );
        match &subject.semantic_state {
            OntologySemanticState::Node(node) => {
                self.metadata.node_count -= 1;
                deindex_properties(&mut self.by_property, key, &node.typed_properties.values)?;
                deindex_context_properties(
                    &mut self.context_members,
                    key,
                    &node.typed_properties.values,
                );
            }
            OntologySemanticState::Relation(relation) => {
                self.metadata.relation_count -= 1;
                deindex_properties(
                    &mut self.by_property,
                    key,
                    &relation.typed_properties.values,
                )?;
                deindex_context_properties(
                    &mut self.context_members,
                    key,
                    &relation.typed_properties.values,
                );
                let source = SubjectKey::new(&key.ontology_id, &relation.source_node_id);
                let target = SubjectKey::new(&key.ontology_id, &relation.target_node_id);
                let relation_type = subject.identity.type_ref.clone();
                let outgoing_key = (source.clone(), relation_type.clone());
                let incoming_key = (target.clone(), relation_type.clone());
                remove_index_value(&mut self.outgoing_relations, &outgoing_key, key);
                remove_index_value(&mut self.incoming_relations, &incoming_key, key);
                let parallel_outgoing = self
                    .outgoing_relations
                    .get(&outgoing_key)
                    .into_iter()
                    .flat_map(|values| values.iter())
                    .any(|relation_key| {
                        self.subjects.get(relation_key).is_some_and(|candidate| {
                            matches!(
                                &candidate.semantic_state,
                                OntologySemanticState::Relation(candidate_relation)
                                    if candidate_relation.target_node_id == relation.target_node_id
                            )
                        })
                    });
                if !parallel_outgoing {
                    remove_index_value(&mut self.outgoing, &outgoing_key, &target);
                    remove_index_value(&mut self.incoming, &incoming_key, &source);
                }
                if relation_type == "belongs_to"
                    && !parallel_outgoing
                    && !self.subject_has_explicit_context(&source, &target.subject_id)
                {
                    remove_index_value(
                        &mut self.context_members,
                        &(key.ontology_id.clone(), target.subject_id),
                        &source,
                    );
                }
            }
        }
        Arc::make_mut(&mut self.subjects).remove(key);
        Arc::make_mut(&mut self.challenge_contracts).remove(key);
        Ok(())
    }

    fn subject_has_explicit_context(&self, key: &SubjectKey, context_id: &str) -> bool {
        self.subjects.get(key).is_some_and(|subject| {
            let properties = match &subject.semantic_state {
                OntologySemanticState::Node(node) => &node.typed_properties.values,
                OntologySemanticState::Relation(relation) => &relation.typed_properties.values,
            };
            ["context_id", "context_ref", "context"].iter().any(|name| {
                properties.get(*name).and_then(serde_json::Value::as_str) == Some(context_id)
            })
        })
    }

    fn calculate_digest(&self) -> Result<String, GraphFailure> {
        let material = DigestMaterial {
            semantic_cursor: self.metadata.semantic_cursor,
            source_event_count: self.metadata.source_event_count,
            source_event_set_digest: self.metadata.source_event_set_digest.clone(),
            subjects: self
                .subjects
                .values()
                .map(|subject| subject.as_ref().clone())
                .collect(),
            challenge_contracts: self
                .challenge_contracts
                .iter()
                .map(|(subject, contract)| ChallengeView {
                    subject: subject.clone(),
                    contract: contract.as_ref().clone(),
                })
                .collect(),
        };
        let bytes = serde_json::to_vec(&material).map_err(|error| {
            GraphFailure::new("INDEX_DIGEST_SERIALIZATION_FAILED", error.to_string())
        })?;
        Ok(format!("{:x}", Sha256::digest(bytes)))
    }

    pub fn metadata(&self) -> &GraphReadModelMetadata {
        &self.metadata
    }

    pub fn structural_sharing_with(&self, next: &Self) -> StructuralSharingStats {
        StructuralSharingStats {
            previous_subject_count: self.subjects.len(),
            shared_subject_count: shared_value_count(&self.subjects, &next.subjects),
            previous_challenge_contract_count: self.challenge_contracts.len(),
            shared_challenge_contract_count: shared_value_count(
                &self.challenge_contracts,
                &next.challenge_contracts,
            ),
            previous_index_bucket_count: self.by_type.len()
                + self.by_property.len()
                + self.outgoing.len()
                + self.incoming.len()
                + self.outgoing_relations.len()
                + self.incoming_relations.len()
                + self.context_members.len(),
            shared_index_bucket_count: shared_value_count(&self.by_type, &next.by_type)
                + shared_value_count(&self.by_property, &next.by_property)
                + shared_value_count(&self.outgoing, &next.outgoing)
                + shared_value_count(&self.incoming, &next.incoming)
                + shared_value_count(&self.outgoing_relations, &next.outgoing_relations)
                + shared_value_count(&self.incoming_relations, &next.incoming_relations)
                + shared_value_count(&self.context_members, &next.context_members),
        }
    }

    pub fn subject(&self, key: &SubjectKey) -> Option<&ProjectedSubject> {
        self.subjects.get(key).map(Arc::as_ref)
    }

    pub fn subjects(&self) -> Vec<ProjectedSubject> {
        self.subjects
            .values()
            .map(|subject| subject.as_ref().clone())
            .collect()
    }

    pub fn estimated_string_payload_bytes(&self) -> usize {
        let subject_bytes = self
            .subjects
            .values()
            .map(|subject| serde_json::to_vec(subject.as_ref()).map_or(0, |bytes| bytes.len()))
            .sum::<usize>();
        let challenge_bytes = self
            .challenge_contracts
            .iter()
            .map(|(key, contract)| {
                key.ontology_id.len()
                    + key.subject_id.len()
                    + serde_json::to_vec(contract.as_ref()).map_or(0, |bytes| bytes.len())
            })
            .sum::<usize>();
        let set_bytes = |set: &BTreeSet<SubjectKey>| {
            set.iter()
                .map(|key| key.ontology_id.len() + key.subject_id.len())
                .sum::<usize>()
        };
        let pair_index_bytes = |index: &BTreeMap<
            (SubjectKey, String),
            Arc<BTreeSet<SubjectKey>>,
        >| {
            index
                .iter()
                .map(|((key, label), values)| {
                    key.ontology_id.len() + key.subject_id.len() + label.len() + set_bytes(values)
                })
                .sum::<usize>()
        };
        subject_bytes
            + challenge_bytes
            + pair_index_bytes(&self.outgoing)
            + pair_index_bytes(&self.incoming)
            + pair_index_bytes(&self.outgoing_relations)
            + pair_index_bytes(&self.incoming_relations)
            + self
                .by_type
                .iter()
                .map(|((ontology, type_ref), values)| {
                    ontology.len() + type_ref.len() + set_bytes(values)
                })
                .sum::<usize>()
            + self
                .by_property
                .iter()
                .map(|((ontology, name, value), values)| {
                    ontology.len() + name.len() + value.len() + set_bytes(values)
                })
                .sum::<usize>()
            + self
                .context_members
                .iter()
                .map(|((ontology, context), values)| {
                    ontology.len() + context.len() + set_bytes(values)
                })
                .sum::<usize>()
    }

    pub fn subjects_by_type(&self, ontology_id: &str, type_ref: &str) -> Vec<ProjectedSubject> {
        self.lookup_keys(
            self.by_type
                .get(&(ontology_id.to_owned(), type_ref.to_owned()))
                .map(Arc::as_ref),
        )
    }

    pub fn subject_keys_by_type(
        &self,
        ontology_id: &str,
        type_ref: &str,
        after: Option<&SubjectKey>,
        limit: usize,
    ) -> Result<SubjectKeyPage, GraphFailure> {
        self.key_page(
            self.by_type
                .get(&(ontology_id.to_owned(), type_ref.to_owned()))
                .map(Arc::as_ref),
            ontology_id,
            after,
            limit,
        )
    }

    pub fn subjects_by_property(
        &self,
        ontology_id: &str,
        property_name: &str,
        value: &serde_json::Value,
    ) -> Result<Vec<ProjectedSubject>, GraphFailure> {
        let encoded = canonical_value(value)?;
        Ok(self.lookup_keys(
            self.by_property
                .get(&(ontology_id.to_owned(), property_name.to_owned(), encoded))
                .map(Arc::as_ref),
        ))
    }

    pub fn subject_keys_by_property(
        &self,
        ontology_id: &str,
        property_name: &str,
        value: &serde_json::Value,
        after: Option<&SubjectKey>,
        limit: usize,
    ) -> Result<SubjectKeyPage, GraphFailure> {
        let encoded = canonical_value(value)?;
        self.key_page(
            self.by_property
                .get(&(ontology_id.to_owned(), property_name.to_owned(), encoded))
                .map(Arc::as_ref),
            ontology_id,
            after,
            limit,
        )
    }

    pub fn outgoing_neighbors(
        &self,
        start: &SubjectKey,
        relation_type: &str,
    ) -> Vec<ProjectedSubject> {
        self.lookup_keys(
            self.outgoing
                .get(&(start.clone(), relation_type.to_owned()))
                .map(Arc::as_ref),
        )
    }

    pub fn incoming_neighbors(
        &self,
        target: &SubjectKey,
        relation_type: &str,
    ) -> Vec<ProjectedSubject> {
        self.lookup_keys(
            self.incoming
                .get(&(target.clone(), relation_type.to_owned()))
                .map(Arc::as_ref),
        )
    }

    pub fn outgoing_matches(&self, start: &SubjectKey, relation_type: &str) -> Vec<RelationMatch> {
        self.relation_matches(start, relation_type, true)
    }

    pub fn incoming_matches(&self, target: &SubjectKey, relation_type: &str) -> Vec<RelationMatch> {
        self.relation_matches(target, relation_type, false)
    }

    pub fn traverse(&self, start: &SubjectKey, relation_path: &[String]) -> Vec<ProjectedSubject> {
        let mut frontier = BTreeSet::from([start.clone()]);
        for relation_type in relation_path {
            frontier = frontier
                .iter()
                .flat_map(|key| {
                    self.outgoing
                        .get(&(key.clone(), relation_type.clone()))
                        .into_iter()
                        .flat_map(|values| values.iter())
                        .cloned()
                })
                .collect();
        }
        self.lookup_keys(Some(&frontier))
    }

    pub fn context_members(&self, ontology_id: &str, context_id: &str) -> Vec<ProjectedSubject> {
        self.lookup_keys(
            self.context_members
                .get(&(ontology_id.to_owned(), context_id.to_owned()))
                .map(Arc::as_ref),
        )
    }

    pub fn challenge_contract(&self, key: &SubjectKey) -> Option<&ChallengeContract> {
        self.challenge_contracts.get(key).map(Arc::as_ref)
    }

    pub fn subjects_supporting_challenge_mode(&self, mode: ChallengeMode) -> Vec<ProjectedSubject> {
        let keys = self
            .challenge_contracts
            .iter()
            .filter(|(_, contract)| contract.valid_challenge_modes.contains(&mode))
            .map(|(key, _)| key.clone())
            .collect::<BTreeSet<_>>();
        self.lookup_keys(Some(&keys))
    }

    fn lookup_keys(&self, keys: Option<&BTreeSet<SubjectKey>>) -> Vec<ProjectedSubject> {
        keys.into_iter()
            .flatten()
            .filter_map(|key| {
                self.subjects
                    .get(key)
                    .map(|subject| subject.as_ref().clone())
            })
            .collect()
    }

    fn key_page(
        &self,
        keys: Option<&BTreeSet<SubjectKey>>,
        ontology_id: &str,
        after: Option<&SubjectKey>,
        limit: usize,
    ) -> Result<SubjectKeyPage, GraphFailure> {
        if limit == 0 || limit > MAX_QUERY_PAGE_SIZE {
            return Err(GraphFailure::new(
                "QUERY_PAGE_LIMIT_OUT_OF_RANGE",
                format!("requested {limit}; required range is 1..={MAX_QUERY_PAGE_SIZE}"),
            ));
        }
        if let Some(after) = after
            && after.ontology_id != ontology_id
        {
            return Err(GraphFailure::new(
                "QUERY_PAGE_CURSOR_ONTOLOGY_MISMATCH",
                after.ontology_id.clone(),
            ));
        }
        let lower = after.cloned().map(Excluded).unwrap_or(Unbounded);
        let mut selected = keys
            .map(|values| {
                values
                    .range((lower, Unbounded))
                    .take(limit + 1)
                    .cloned()
                    .collect::<Vec<_>>()
            })
            .unwrap_or_default();
        let has_more = selected.len() > limit;
        selected.truncate(limit);
        let next_after = has_more.then(|| selected.last().cloned()).flatten();
        Ok(SubjectKeyPage {
            schema_version: "cal-subject-key-page/v1-prototype".to_owned(),
            items: selected,
            limit,
            next_after,
        })
    }

    fn relation_matches(
        &self,
        endpoint: &SubjectKey,
        relation_type: &str,
        outgoing: bool,
    ) -> Vec<RelationMatch> {
        let relation_index = if outgoing {
            &self.outgoing_relations
        } else {
            &self.incoming_relations
        };
        relation_index
            .get(&(endpoint.clone(), relation_type.to_owned()))
            .into_iter()
            .flat_map(|values| values.iter())
            .filter_map(|relation_key| {
                let relation = self.subjects.get(relation_key)?.as_ref().clone();
                let relation_state = match &relation.semantic_state {
                    OntologySemanticState::Relation(state) => state,
                    OntologySemanticState::Node(_) => return None,
                };
                let neighbor_id = if outgoing {
                    &relation_state.target_node_id
                } else {
                    &relation_state.source_node_id
                };
                let neighbor = self
                    .subjects
                    .get(&SubjectKey::new(&endpoint.ontology_id, neighbor_id))?
                    .as_ref()
                    .clone();
                Some(RelationMatch { relation, neighbor })
            })
            .collect()
    }
}

fn shared_value_count<K: Ord, V>(
    previous: &BTreeMap<K, Arc<V>>,
    next: &BTreeMap<K, Arc<V>>,
) -> usize {
    previous
        .iter()
        .filter(|(key, value)| {
            next.get(*key)
                .is_some_and(|candidate| Arc::ptr_eq(value, candidate))
        })
        .count()
}

pub fn encode_checkpoint(checkpoint: &GraphCheckpointEnvelope) -> Result<String, GraphFailure> {
    validate_checkpoint(checkpoint)?;
    canonical_json(checkpoint).map_err(GraphFailure::from)
}

pub fn decode_checkpoint(bytes: &[u8]) -> Result<GraphCheckpointEnvelope, GraphFailure> {
    let checkpoint: GraphCheckpointEnvelope = serde_json::from_slice(bytes)
        .map_err(|error| GraphFailure::new("CHECKPOINT_DECODE_FAILED", error.to_string()))?;
    let canonical = canonical_json(&checkpoint)?;
    if bytes != canonical.as_bytes() {
        return Err(GraphFailure::new(
            "CHECKPOINT_NON_CANONICAL_JSON",
            "checkpoint bytes are not the deterministic cache format",
        ));
    }
    validate_checkpoint(&checkpoint)?;
    Ok(checkpoint)
}

pub fn write_checkpoint_atomically(
    target: impl AsRef<Path>,
    checkpoint: &GraphCheckpointEnvelope,
    fault: AtomicCheckpointFault,
) -> Result<AtomicCheckpointWriteReceipt, GraphFailure> {
    let target = target.as_ref();
    let encoded = encode_checkpoint(checkpoint)?;
    let parent = target
        .parent()
        .filter(|path| !path.as_os_str().is_empty())
        .unwrap_or_else(|| Path::new("."));
    if !parent.is_dir() {
        return Err(GraphFailure::new(
            "CHECKPOINT_PARENT_DIRECTORY_MISSING",
            parent.display().to_string(),
        ));
    }
    let file_name = target.file_name().ok_or_else(|| {
        GraphFailure::new(
            "CHECKPOINT_TARGET_NAME_MISSING",
            target.display().to_string(),
        )
    })?;
    let lock_path = parent.join(format!(".{}.lock", file_name.to_string_lossy()));
    let lock_file = OpenOptions::new()
        .read(true)
        .write(true)
        .create(true)
        .truncate(false)
        .open(&lock_path)
        .map_err(|error| {
            GraphFailure::new(
                "CHECKPOINT_LOCK_OPEN_FAILED",
                format!("{}: {error}", lock_path.display()),
            )
        })?;
    lock_file.try_lock().map_err(|error| {
        GraphFailure::new(
            "CHECKPOINT_WRITER_BUSY",
            format!("{}: {error}", lock_path.display()),
        )
    })?;

    let mut disposition = "created";
    let mut prior_semantic_cursor = None;
    let mut prior_governance_cursor = None;
    if let Ok(metadata) = fs::symlink_metadata(target) {
        if metadata.file_type().is_symlink() {
            return Err(GraphFailure::new(
                "CHECKPOINT_TARGET_SYMLINK_FORBIDDEN",
                target.display().to_string(),
            ));
        }
        if !metadata.is_file() {
            return Err(GraphFailure::new(
                "CHECKPOINT_TARGET_NOT_FILE",
                target.display().to_string(),
            ));
        }
        let existing_bytes = fs::read(target).map_err(|error| {
            GraphFailure::new(
                "CHECKPOINT_EXISTING_READ_FAILED",
                format!("{}: {error}", target.display()),
            )
        })?;
        let existing = decode_checkpoint(&existing_bytes).map_err(|failure| {
            GraphFailure::new(
                "CHECKPOINT_EXISTING_INVALID",
                format!("{}: {}: {}", target.display(), failure.code, failure.detail),
            )
        })?;
        prior_semantic_cursor = Some(existing.body.tail_boundary.semantic_cursor);
        prior_governance_cursor = Some(existing.body.tail_boundary.governance_cursor);
        if existing_bytes == encoded.as_bytes() {
            return Ok(AtomicCheckpointWriteReceipt {
                schema_version: "cal-atomic-checkpoint-write-receipt/v1-prototype".to_owned(),
                disposition: "unchanged".to_owned(),
                target_path: target.display().to_string(),
                checkpoint_file_digest_sha256: format!("{:x}", Sha256::digest(encoded.as_bytes())),
                checkpoint_body_digest_sha256: checkpoint.body_digest_sha256.clone(),
                prior_semantic_cursor,
                prior_governance_cursor,
                semantic_cursor: checkpoint.body.tail_boundary.semantic_cursor,
                governance_cursor: checkpoint.body.tail_boundary.governance_cursor,
                checkpoint_bytes: encoded.len(),
                replacement_strategy: "same_directory_synced_stage_atomic_rename".to_owned(),
                staged_file_synced: false,
                atomic_rename_completed: false,
                parent_directory_synced: false,
                canonical_replay_source: false,
                authority_effect: AUTHORITY_EFFECT.to_owned(),
            });
        }
        validate_checkpoint_replacement(&existing, checkpoint)?;
        disposition = "replaced";
    } else if let Err(error) = fs::symlink_metadata(target)
        && error.kind() != std::io::ErrorKind::NotFound
    {
        return Err(GraphFailure::new(
            "CHECKPOINT_TARGET_INSPECTION_FAILED",
            format!("{}: {error}", target.display()),
        ));
    }

    let stage_path = checkpoint_stage_path(parent, file_name);
    let write_result = write_synced_checkpoint_stage(&stage_path, encoded.as_bytes());
    if let Err(failure) = write_result {
        let _ = fs::remove_file(&stage_path);
        return Err(failure);
    }
    if fault == AtomicCheckpointFault::AfterStageSync {
        return Err(GraphFailure::new(
            "CHECKPOINT_FAULT_INJECTED_AFTER_STAGE_SYNC",
            stage_path.display().to_string(),
        ));
    }
    if let Err(error) = fs::rename(&stage_path, target) {
        let _ = fs::remove_file(&stage_path);
        return Err(GraphFailure::new(
            "CHECKPOINT_ATOMIC_RENAME_FAILED",
            format!("{} -> {}: {error}", stage_path.display(), target.display()),
        ));
    }
    if fault == AtomicCheckpointFault::AfterRenameBeforeDirectorySync {
        return Err(GraphFailure::new(
            "CHECKPOINT_FAULT_INJECTED_AFTER_RENAME",
            target.display().to_string(),
        ));
    }
    sync_checkpoint_parent(parent)?;
    Ok(AtomicCheckpointWriteReceipt {
        schema_version: "cal-atomic-checkpoint-write-receipt/v1-prototype".to_owned(),
        disposition: disposition.to_owned(),
        target_path: target.display().to_string(),
        checkpoint_file_digest_sha256: format!("{:x}", Sha256::digest(encoded.as_bytes())),
        checkpoint_body_digest_sha256: checkpoint.body_digest_sha256.clone(),
        prior_semantic_cursor,
        prior_governance_cursor,
        semantic_cursor: checkpoint.body.tail_boundary.semantic_cursor,
        governance_cursor: checkpoint.body.tail_boundary.governance_cursor,
        checkpoint_bytes: encoded.len(),
        replacement_strategy: "same_directory_synced_stage_atomic_rename".to_owned(),
        staged_file_synced: true,
        atomic_rename_completed: true,
        parent_directory_synced: true,
        canonical_replay_source: false,
        authority_effect: AUTHORITY_EFFECT.to_owned(),
    })
}

fn validate_checkpoint_replacement(
    existing: &GraphCheckpointEnvelope,
    replacement: &GraphCheckpointEnvelope,
) -> Result<(), GraphFailure> {
    let existing_semantic = existing.body.tail_boundary.semantic_cursor;
    let existing_governance = existing.body.tail_boundary.governance_cursor;
    let replacement_semantic = replacement.body.tail_boundary.semantic_cursor;
    let replacement_governance = replacement.body.tail_boundary.governance_cursor;
    if replacement_semantic == existing_semantic && replacement_governance == existing_governance {
        return Err(GraphFailure::new(
            "CHECKPOINT_SAME_BOUNDARY_CONFLICT",
            format!("semantic {replacement_semantic}; governance {replacement_governance}"),
        ));
    }
    if replacement_semantic < existing_semantic || replacement_governance < existing_governance {
        let code = if replacement_semantic <= existing_semantic
            && replacement_governance <= existing_governance
        {
            "CHECKPOINT_REPLACEMENT_REGRESSION"
        } else {
            "CHECKPOINT_REPLACEMENT_INCOMPARABLE"
        };
        return Err(GraphFailure::new(
            code,
            format!(
                "semantic {existing_semantic}->{replacement_semantic}; governance {existing_governance}->{replacement_governance}"
            ),
        ));
    }
    Ok(())
}

fn checkpoint_stage_path(parent: &Path, file_name: &std::ffi::OsStr) -> PathBuf {
    let timestamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_nanos();
    let sequence = CHECKPOINT_STAGE_SEQUENCE.fetch_add(1, Ordering::Relaxed);
    parent.join(format!(
        ".{}.stage.{}.{}.{}",
        file_name.to_string_lossy(),
        std::process::id(),
        timestamp,
        sequence
    ))
}

fn write_synced_checkpoint_stage(path: &Path, bytes: &[u8]) -> Result<(), GraphFailure> {
    let mut file = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(path)
        .map_err(|error| {
            GraphFailure::new(
                "CHECKPOINT_STAGE_CREATE_FAILED",
                format!("{}: {error}", path.display()),
            )
        })?;
    file.write_all(bytes).map_err(|error| {
        GraphFailure::new(
            "CHECKPOINT_STAGE_WRITE_FAILED",
            format!("{}: {error}", path.display()),
        )
    })?;
    file.sync_all().map_err(|error| {
        GraphFailure::new(
            "CHECKPOINT_STAGE_SYNC_FAILED",
            format!("{}: {error}", path.display()),
        )
    })
}

fn sync_checkpoint_parent(parent: &Path) -> Result<(), GraphFailure> {
    File::open(parent)
        .and_then(|directory| directory.sync_all())
        .map_err(|error| {
            GraphFailure::new(
                "CHECKPOINT_DIRECTORY_SYNC_FAILED",
                format!("{}: {error}", parent.display()),
            )
        })
}

fn validate_checkpoint(checkpoint: &GraphCheckpointEnvelope) -> Result<(), GraphFailure> {
    if checkpoint.schema_version != "cal-graph-checkpoint-envelope/v1-prototype" {
        return Err(GraphFailure::new(
            "CHECKPOINT_SCHEMA_UNSUPPORTED",
            checkpoint.schema_version.clone(),
        ));
    }
    if checkpoint.checkpoint_kind != "disposable-calculated-read-model-cache"
        || checkpoint.canonical_replay_source
        || checkpoint.authority_effect != AUTHORITY_EFFECT
        || checkpoint.body.runtime_identity != RUNTIME_IDENTITY
        || checkpoint.body.base_expectation.runtime_identity != RUNTIME_IDENTITY
    {
        return Err(GraphFailure::new(
            "CHECKPOINT_POSTURE_INVALID",
            checkpoint.checkpoint_kind.clone(),
        ));
    }
    if checkpoint.body.projection.authority != "calculated-cache"
        || checkpoint.body.projection.source_cursor != checkpoint.body.tail_boundary.semantic_cursor
        || checkpoint.body.projection.source_event_set_digest
            != checkpoint.body.tail_boundary.projection_checkpoint_digest
        || checkpoint.body.base_expectation.semantic_cursor
            != checkpoint.body.projection.source_cursor
        || checkpoint.body.base_expectation.source_event_count
            != checkpoint.body.tail_boundary.semantic_event_count
    {
        return Err(GraphFailure::new(
            "CHECKPOINT_SOURCE_BOUNDARY_INVALID",
            checkpoint.body.projection.source_cursor.to_string(),
        ));
    }
    let actual_digest = digest_serializable(&checkpoint.body)?;
    if checkpoint.body_digest_sha256 != actual_digest {
        return Err(GraphFailure::new(
            "CHECKPOINT_BODY_DIGEST_MISMATCH",
            checkpoint.body.body_digest_context(),
        ));
    }
    Ok(())
}

impl GraphCheckpointBody {
    fn body_digest_context(&self) -> String {
        format!(
            "runtime {} at cursor {}",
            self.runtime_identity, self.projection.source_cursor
        )
    }
}

fn checkpoint_challenges_after_tail(
    checkpoint: &GraphCheckpointEnvelope,
    tail: &EventTail,
    final_cut: &cal_ontology_lifecycle::ConsistentOntologyCut,
) -> Result<Vec<ProjectedChallengeContract>, GraphFailure> {
    let mut semantic_subjects = checkpoint
        .body
        .tail_boundary
        .semantic_events_by_id
        .iter()
        .map(|(event_id, boundary)| (event_id.clone(), boundary.subject_identity.clone()))
        .collect::<BTreeMap<_, _>>();
    semantic_subjects.extend(tail.semantic_events().iter().map(|loaded| {
        (
            loaded.event.event_id.clone(),
            loaded.event.subject_identity.clone(),
        )
    }));
    let mut challenges = checkpoint
        .body
        .challenges
        .iter()
        .cloned()
        .map(|challenge| (challenge.subject.clone(), challenge))
        .collect::<BTreeMap<_, _>>();
    for loaded in tail.governance_events() {
        let identity = semantic_subjects
            .get(&loaded.event.semantic_ref.semantic_event_id)
            .ok_or_else(|| {
                GraphFailure::new(
                    "GOVERNANCE_REFERENCE_MISSING",
                    loaded.event.semantic_ref.semantic_event_id.clone(),
                )
            })?;
        let key = SubjectKey::new(&identity.ontology_id, &identity.subject_id);
        challenges.insert(
            key.clone(),
            ProjectedChallengeContract {
                subject: key,
                semantic_event_id: loaded.event.semantic_ref.semantic_event_id.clone(),
                semantic_event_digest: loaded.event.semantic_ref.semantic_event_digest.clone(),
                semantic_cursor: loaded.event.semantic_ref.semantic_cursor,
                contract: loaded
                    .event
                    .complete_resulting_governance_state
                    .challenge_contract
                    .clone(),
            },
        );
    }
    final_cut
        .subjects
        .iter()
        .map(|subject| {
            challenges
                .get(&SubjectKey::of(subject))
                .cloned()
                .ok_or_else(|| {
                    GraphFailure::new(
                        "EXACT_GOVERNANCE_STATE_MISSING",
                        subject.identity.subject_id.clone(),
                    )
                })
        })
        .collect()
}

fn validate_recovery_runtime(expectation: &RecoveryExpectation) -> Result<(), GraphFailure> {
    if expectation.runtime_identity != RUNTIME_IDENTITY {
        return Err(GraphFailure::new(
            "RECOVERY_RUNTIME_IDENTITY_MISMATCH",
            expectation.runtime_identity.clone(),
        ));
    }
    Ok(())
}

fn recovery_receipt(
    model: &GraphReadModel,
    expectation: &RecoveryExpectation,
    strategy: &str,
    checkpoint_used: bool,
) -> Result<RecoveryReceipt, GraphFailure> {
    if model.metadata.semantic_cursor != expectation.semantic_cursor
        || model.metadata.source_event_count != expectation.source_event_count
        || model.metadata.source_event_set_digest != expectation.source_event_set_digest
    {
        return Err(GraphFailure::new(
            "RECOVERY_SOURCE_ENVELOPE_MISMATCH",
            format!(
                "expected cursor {} count {} digest {}; rebuilt cursor {} count {} digest {}",
                expectation.semantic_cursor,
                expectation.source_event_count,
                expectation.source_event_set_digest,
                model.metadata.semantic_cursor,
                model.metadata.source_event_count,
                model.metadata.source_event_set_digest
            ),
        ));
    }
    if model.metadata.index_digest != expectation.expected_index_digest {
        return Err(GraphFailure::new(
            "RECOVERY_INDEX_DIGEST_MISMATCH",
            format!(
                "expected {}; rebuilt {}",
                expectation.expected_index_digest, model.metadata.index_digest
            ),
        ));
    }
    Ok(RecoveryReceipt {
        schema_version: "cal-graph-recovery-receipt/v1-prototype".to_owned(),
        recovery_strategy: strategy.to_owned(),
        runtime_identity: RUNTIME_IDENTITY.to_owned(),
        semantic_cursor: model.metadata.semantic_cursor,
        source_event_count: model.metadata.source_event_count,
        source_event_set_digest: model.metadata.source_event_set_digest.clone(),
        rebuilt_index_digest: model.metadata.index_digest.clone(),
        exact_index_digest_match: true,
        checkpoint_used,
        canonical_replay_source: false,
        authority_effect: AUTHORITY_EFFECT.to_owned(),
    })
}

fn exact_governance_joins(
    store: &EventStore,
    subjects: &BTreeMap<SubjectKey, ProjectedSubject>,
) -> Result<BTreeMap<SubjectKey, ChallengeContract>, GraphFailure> {
    let mut latest_by_semantic_reference = BTreeMap::new();
    for loaded in store.governance_events() {
        let reference = &loaded.event.semantic_ref;
        let reference_key = (
            reference.semantic_event_id.as_str(),
            reference.semantic_event_digest.as_str(),
            reference.semantic_cursor,
        );
        let replace = latest_by_semantic_reference.get(&reference_key).is_none_or(
            |current: &&cal_ontology_lifecycle::LoadedGovernanceEvent| {
                current.event.governance_cursor < loaded.event.governance_cursor
            },
        );
        if replace {
            latest_by_semantic_reference.insert(reference_key, loaded);
        }
    }
    let mut joined = BTreeMap::new();
    for (key, subject) in subjects {
        let governance = latest_by_semantic_reference
            .get(&(
                subject.source_event_id.as_str(),
                subject.source_event_digest.as_str(),
                subject.source_cursor,
            ))
            .ok_or_else(|| {
                GraphFailure::new(
                    "EXACT_GOVERNANCE_STATE_MISSING",
                    format!(
                        "{} at semantic cursor {}",
                        subject.source_event_id, subject.source_cursor
                    ),
                )
            })?;
        joined.insert(
            key.clone(),
            governance
                .event
                .complete_resulting_governance_state
                .challenge_contract
                .clone(),
        );
    }
    Ok(joined)
}

fn semantic_change_kind(change: &CalculatedSubjectChange) -> Result<ChangeKind, GraphFailure> {
    match (&change.expected_previous, &change.resulting) {
        (None, Some(_)) => Ok(ChangeKind::Added),
        (Some(_), None) => Ok(ChangeKind::Removed),
        (Some(expected), Some(resulting)) => {
            let same_semantic_version = expected.semantic_event_id
                == resulting.subject.source_event_id
                && expected.semantic_event_digest == resulting.subject.source_event_digest
                && expected.semantic_cursor == resulting.subject.source_cursor;
            Ok(if same_semantic_version {
                ChangeKind::GovernanceReplaced
            } else {
                ChangeKind::Updated
            })
        }
        (None, None) => Err(GraphFailure::new(
            "DELTA_CHANGE_HAS_NO_PRIOR_OR_RESULT",
            change.subject.subject_id.clone(),
        )),
    }
}

fn validate_projected_challenge(
    subject: &ProjectedSubject,
    projected: &ProjectedChallengeContract,
) -> Result<(), GraphFailure> {
    if projected.subject != SubjectKey::of(subject)
        || projected.semantic_event_id != subject.source_event_id
        || projected.semantic_event_digest != subject.source_event_digest
        || projected.semantic_cursor != subject.source_cursor
    {
        return Err(GraphFailure::new(
            "GOVERNANCE_REFERENCE_MISMATCH",
            subject.identity.subject_id.clone(),
        ));
    }
    Ok(())
}

fn validate_indexable_subject(subject: &ProjectedSubject) -> Result<(), GraphFailure> {
    if subject.semantic_state.identity() != &subject.identity {
        return Err(GraphFailure::new(
            "PROJECTED_SUBJECT_IDENTITY_MISMATCH",
            subject.identity.subject_id.clone(),
        ));
    }
    let kind_matches_state = matches!(
        (&subject.identity.subject_kind, &subject.semantic_state),
        (SubjectKind::Node, OntologySemanticState::Node(_))
            | (SubjectKind::Relation, OntologySemanticState::Relation(_))
    );
    if !kind_matches_state {
        return Err(GraphFailure::new(
            "PROJECTED_SUBJECT_KIND_MISMATCH",
            subject.identity.subject_id.clone(),
        ));
    }
    let properties = match &subject.semantic_state {
        OntologySemanticState::Node(node) => &node.typed_properties.values,
        OntologySemanticState::Relation(relation) => &relation.typed_properties.values,
    };
    for value in properties.values() {
        canonical_value(value)?;
    }
    Ok(())
}

fn validate_delta_relation_endpoints(
    subjects: &BTreeMap<SubjectKey, Arc<ProjectedSubject>>,
    changes: &[CalculatedSubjectChange],
) -> Result<(), GraphFailure> {
    let changes_by_key = changes
        .iter()
        .map(|change| (change.subject.clone(), change))
        .collect::<BTreeMap<_, _>>();
    for (key, subject) in subjects {
        if !changes_by_key.contains_key(key) {
            validate_relation_endpoints_after_delta(subject, subjects, &changes_by_key)?;
        }
    }
    for change in changes {
        if let Some(resulting) = &change.resulting {
            validate_relation_endpoints_after_delta(&resulting.subject, subjects, &changes_by_key)?;
        }
    }
    Ok(())
}

fn validate_relation_endpoints_after_delta(
    subject: &ProjectedSubject,
    subjects: &BTreeMap<SubjectKey, Arc<ProjectedSubject>>,
    changes: &BTreeMap<SubjectKey, &CalculatedSubjectChange>,
) -> Result<(), GraphFailure> {
    let OntologySemanticState::Relation(relation) = &subject.semantic_state else {
        return Ok(());
    };
    for endpoint in [&relation.source_node_id, &relation.target_node_id] {
        let key = SubjectKey::new(&subject.identity.ontology_id, endpoint);
        let candidate = changes
            .get(&key)
            .and_then(|change| change.resulting.as_ref())
            .map(|resulting| &resulting.subject)
            .or_else(|| {
                (!changes.contains_key(&key))
                    .then(|| subjects.get(&key))
                    .flatten()
                    .map(Arc::as_ref)
            });
        let valid = candidate.is_some_and(|candidate| {
            candidate.identity.subject_kind == SubjectKind::Node
                && candidate.semantic_state.lifecycle() == Lifecycle::Active
        });
        if !valid {
            return Err(GraphFailure::new(
                "DELTA_RELATION_ENDPOINT_MISSING",
                format!("{} -> {endpoint}", subject.identity.subject_id),
            ));
        }
    }
    Ok(())
}

fn validate_active_relation_endpoints(
    subjects: &BTreeMap<SubjectKey, Arc<ProjectedSubject>>,
) -> Result<(), GraphFailure> {
    for subject in subjects.values() {
        if let OntologySemanticState::Relation(relation) = &subject.semantic_state {
            for endpoint in [&relation.source_node_id, &relation.target_node_id] {
                let key = SubjectKey::new(&subject.identity.ontology_id, endpoint);
                let valid = subjects.get(&key).is_some_and(|candidate| {
                    candidate.identity.subject_kind == SubjectKind::Node
                        && candidate.semantic_state.lifecycle() == Lifecycle::Active
                });
                if !valid {
                    return Err(GraphFailure::new(
                        "DELTA_RELATION_ENDPOINT_MISSING",
                        format!("{} -> {endpoint}", subject.identity.subject_id),
                    ));
                }
            }
        }
    }
    Ok(())
}

fn projection_digest<'a>(
    subjects: impl Iterator<Item = &'a ProjectedSubject>,
) -> Result<String, GraphFailure> {
    let mut ordered = subjects.collect::<Vec<_>>();
    ordered.sort_by(|left, right| left.identity.cmp(&right.identity));
    let references = ordered
        .into_iter()
        .map(projection_reference)
        .collect::<Vec<_>>();
    digest_serializable(&references)
}

fn projection_digest_after_delta(
    subjects: &BTreeMap<SubjectKey, Arc<ProjectedSubject>>,
    changes: &[CalculatedSubjectChange],
) -> Result<String, GraphFailure> {
    let changed_keys = changes
        .iter()
        .map(|change| change.subject.clone())
        .collect::<BTreeSet<_>>();
    let mut references = subjects
        .iter()
        .filter(|(key, _)| !changed_keys.contains(key))
        .map(|(_, subject)| projection_reference(subject))
        .chain(changes.iter().filter_map(|change| {
            change
                .resulting
                .as_ref()
                .map(|resulting| projection_reference(&resulting.subject))
        }))
        .collect::<Vec<_>>();
    references.sort_by(|left, right| left.identity.cmp(&right.identity));
    digest_serializable(&references)
}

fn projection_reference(subject: &ProjectedSubject) -> ProjectionSubjectReference {
    ProjectionSubjectReference {
        identity: subject.identity.clone(),
        source_event_id: subject.source_event_id.clone(),
        source_event_digest: subject.source_event_digest.clone(),
        source_cursor: subject.source_cursor,
    }
}

/// Calculate the exact active-subject projection digest used by the canonical
/// W7 runtime. This does not admit, persist, or authorize the supplied state.
pub fn calculated_projection_digest(subjects: &[ProjectedSubject]) -> Result<String, GraphFailure> {
    projection_digest(subjects.iter())
}

fn digest_serializable<T: Serialize>(value: &T) -> Result<String, GraphFailure> {
    let mut canonical = serde_json::to_string(value)
        .map_err(|error| GraphFailure::new("DIGEST_SERIALIZATION_FAILED", error.to_string()))?;
    canonical.push('\n');
    Ok(format!("{:x}", Sha256::digest(canonical.as_bytes())))
}

fn subject_map(
    projected_subjects: &[ProjectedSubject],
) -> Result<BTreeMap<SubjectKey, ProjectedSubject>, GraphFailure> {
    let mut subjects = BTreeMap::new();
    for subject in projected_subjects {
        if subject.semantic_state.lifecycle() != Lifecycle::Active {
            return Err(GraphFailure::new(
                "INACTIVE_SUBJECT_IN_CALCULATED_CUT",
                subject.identity.subject_id.clone(),
            ));
        }
        validate_indexable_subject(subject)?;
        let key = SubjectKey::of(subject);
        if subjects.insert(key.clone(), subject.clone()).is_some() {
            return Err(GraphFailure::new(
                "DUPLICATE_SUBJECT_IN_CALCULATED_CUT",
                key.subject_id,
            ));
        }
    }
    Ok(subjects)
}

fn index_properties(
    index: &mut SharedIndex<(String, String, String)>,
    key: &SubjectKey,
    properties: &BTreeMap<String, serde_json::Value>,
) -> Result<(), GraphFailure> {
    for (name, value) in properties {
        shared_index_insert(
            index,
            (
                key.ontology_id.clone(),
                name.clone(),
                canonical_value(value)?,
            ),
            key.clone(),
        );
    }
    Ok(())
}

fn deindex_properties(
    index: &mut SharedIndex<(String, String, String)>,
    key: &SubjectKey,
    properties: &BTreeMap<String, serde_json::Value>,
) -> Result<(), GraphFailure> {
    for (name, value) in properties {
        remove_index_value(
            index,
            &(
                key.ontology_id.clone(),
                name.clone(),
                canonical_value(value)?,
            ),
            key,
        );
    }
    Ok(())
}

fn index_context_properties(
    index: &mut SharedIndex<(String, String)>,
    key: &SubjectKey,
    properties: &BTreeMap<String, serde_json::Value>,
) {
    for name in ["context_id", "context_ref", "context"] {
        if let Some(context) = properties.get(name).and_then(serde_json::Value::as_str) {
            shared_index_insert(
                index,
                (key.ontology_id.clone(), context.to_owned()),
                key.clone(),
            );
        }
    }
}

fn deindex_context_properties(
    index: &mut SharedIndex<(String, String)>,
    key: &SubjectKey,
    properties: &BTreeMap<String, serde_json::Value>,
) {
    let contexts = ["context_id", "context_ref", "context"]
        .iter()
        .filter_map(|name| properties.get(*name).and_then(serde_json::Value::as_str))
        .collect::<BTreeSet<_>>();
    for context in contexts {
        remove_index_value(index, &(key.ontology_id.clone(), context.to_owned()), key);
    }
}

fn shared_index_insert<K: Clone + Ord>(
    index: &mut SharedIndex<K>,
    index_key: K,
    subject: SubjectKey,
) {
    let values = Arc::make_mut(index)
        .entry(index_key)
        .or_insert_with(|| Arc::new(BTreeSet::new()));
    Arc::make_mut(values).insert(subject);
}

fn remove_index_value<K: Clone + Ord>(
    index: &mut SharedIndex<K>,
    index_key: &K,
    subject: &SubjectKey,
) {
    let map = Arc::make_mut(index);
    let remove_entry = map.get_mut(index_key).is_some_and(|values| {
        Arc::make_mut(values).remove(subject);
        values.is_empty()
    });
    if remove_entry {
        map.remove(index_key);
    }
}

fn canonical_value(value: &serde_json::Value) -> Result<String, GraphFailure> {
    serde_json::to_string(value).map_err(|error| {
        GraphFailure::new("PROPERTY_VALUE_SERIALIZATION_FAILED", error.to_string())
    })
}

pub fn is_node(subject: &ProjectedSubject) -> bool {
    subject.identity.subject_kind == SubjectKind::Node
}
