//! Fail-closed execution-envelope prototype for the admitted epoch-002 ontology runtime.
//!
//! The engine owns transition ordering and rollback, not ontology meaning. Canonical
//! event and projection digests are supplied by the already-tested event runtime.
//! This crate has no filesystem, credential, network, service, or live-target adapter.
//! Its public adapter trait is restricted at runtime to the exact disposable prototype boundary.

use cal_ontology_lifecycle::canonical_json;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;
use std::error::Error;
use std::fmt::{self, Display};

pub const D65CUT_DECISION_DIGEST: &str =
    "f7850289e28ddc71c65ffb76dd753c578d0c12230efd08e63fcf36cf5c69e4e8";
pub const SOURCE_EVENT_SET_DIGEST: &str =
    "89750b83a51b59b4e3501cdc4a0036c74d05c5bf28959ed629f6a94ade530ac6";
pub const TARGET_EVENT_SET_DIGEST: &str =
    "ef9f4cfc0d06268cf7dd32f9f08362778d32752f2cf57a55bae2ba0b0d309658";
pub const TARGET_PROJECTION_DIGEST: &str =
    "207149f7c1383403a9f154def016d2e1e45654d84ab38b35dafaa10552c733db";

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum ExecutionMode {
    Prototype,
    Live,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum ExecutionStepId {
    Preflight,
    CapturePreimage,
    Stage,
    Activate,
    Migrate,
    VerifyTarget,
    Cutover,
    VerifyPostimage,
    Rollback,
    VerifyRollback,
}

pub const EXACT_STEP_ORDER: [ExecutionStepId; 10] = [
    ExecutionStepId::Preflight,
    ExecutionStepId::CapturePreimage,
    ExecutionStepId::Stage,
    ExecutionStepId::Activate,
    ExecutionStepId::Migrate,
    ExecutionStepId::VerifyTarget,
    ExecutionStepId::Cutover,
    ExecutionStepId::VerifyPostimage,
    ExecutionStepId::Rollback,
    ExecutionStepId::VerifyRollback,
];

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct EventCut {
    pub event_count: usize,
    pub event_set_digest: String,
    pub projection_digest: String,
    pub canonical_replay_source: bool,
}

impl EventCut {
    pub fn exact_source() -> Self {
        Self {
            event_count: 7,
            event_set_digest: SOURCE_EVENT_SET_DIGEST.to_owned(),
            projection_digest: "cd48d7b7b3a5b2a12047bd769c629b5b82d8d62cb6226daac58ef56a2adfe6d7"
                .to_owned(),
            canonical_replay_source: true,
        }
    }

    pub fn exact_target() -> Self {
        Self {
            event_count: 11,
            event_set_digest: TARGET_EVENT_SET_DIGEST.to_owned(),
            projection_digest: TARGET_PROJECTION_DIGEST.to_owned(),
            canonical_replay_source: true,
        }
    }
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct PrototypeTargetBinding {
    pub kind: String,
    pub identity: String,
    pub live: bool,
    pub production_data: bool,
    pub credential_kind: String,
    pub external_effects: bool,
}

impl PrototypeTargetBinding {
    pub fn exact() -> Self {
        Self {
            kind: "in-memory-disposable-target".to_owned(),
            identity: "cal.prototype.rust-in-memory-target/epoch-002".to_owned(),
            live: false,
            production_data: false,
            credential_kind: "none".to_owned(),
            external_effects: false,
        }
    }
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ExecutionEnvelope {
    pub schema_version: String,
    pub envelope_id: String,
    pub decision_digest: String,
    pub selected_option_id: String,
    pub mode: ExecutionMode,
    pub target: PrototypeTargetBinding,
    pub source_cut: EventCut,
    pub target_cut: EventCut,
    pub step_order: Vec<ExecutionStepId>,
    pub prototype_execution_ready: bool,
    pub live_execution_ready: bool,
    pub always_rollback_prototype: bool,
    pub authority_effect: String,
}

impl ExecutionEnvelope {
    pub fn exact_prototype() -> Self {
        Self {
            schema_version: "cal-rust-execution-envelope/v1-prototype".to_owned(),
            envelope_id: "CAL-D65-EPOCH-002-RUST-EXECUTION-PROTOTYPE-002".to_owned(),
            decision_digest: D65CUT_DECISION_DIGEST.to_owned(),
            selected_option_id: "D65CUT-1".to_owned(),
            mode: ExecutionMode::Prototype,
            target: PrototypeTargetBinding::exact(),
            source_cut: EventCut::exact_source(),
            target_cut: EventCut::exact_target(),
            step_order: EXACT_STEP_ORDER.to_vec(),
            prototype_execution_ready: true,
            live_execution_ready: false,
            always_rollback_prototype: true,
            authority_effect: "none".to_owned(),
        }
    }
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct RuntimePointer {
    pub generation: String,
    pub runtime_state: String,
    pub traffic_target: String,
    pub live: bool,
}

impl RuntimePointer {
    fn source() -> Self {
        Self {
            generation: "epoch-001".to_owned(),
            runtime_state: "inactive".to_owned(),
            traffic_target: "epoch-001".to_owned(),
            live: false,
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct TargetSnapshot {
    pub active_cut: EventCut,
    pub runtime: RuntimePointer,
    pub staged_cut: Option<EventCut>,
    pub external_effects: bool,
}

/// The complete state-transition boundary required by the execution engine.
///
/// Implementing this trait does not make an adapter eligible for live use. The engine accepts
/// only the exact non-live [`PrototypeTargetBinding`] carried by the execution envelope.
pub trait ExecutionTargetAdapter {
    type Snapshot: Clone;

    fn binding(&self) -> PrototypeTargetBinding;
    fn capture_preimage(&self) -> Self::Snapshot;
    fn verify_preimage(&self, expected: &EventCut) -> Result<(), ExecutionFailure>;
    fn stage(&mut self, candidate: &EventCut) -> Result<(), ExecutionFailure>;
    fn activate(&mut self) -> Result<(), ExecutionFailure>;
    fn migrate(&mut self) -> Result<(), ExecutionFailure>;
    fn verify_target(&self, expected: &EventCut) -> Result<(), ExecutionFailure>;
    fn cutover(&mut self) -> Result<(), ExecutionFailure>;
    fn verify_postimage(&self, expected: &EventCut) -> Result<(), ExecutionFailure>;
    fn restore(&mut self, preimage: &Self::Snapshot) -> Result<(), ExecutionFailure>;
    fn verify_rollback(&self, preimage: &Self::Snapshot) -> Result<(), ExecutionFailure>;
    fn emergency_restore(&mut self, preimage: &Self::Snapshot);
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct InMemoryTarget {
    state: TargetSnapshot,
    fault_at: Option<ExecutionStepId>,
}

impl Default for InMemoryTarget {
    fn default() -> Self {
        Self::new()
    }
}

impl InMemoryTarget {
    pub fn new() -> Self {
        Self {
            state: TargetSnapshot {
                active_cut: EventCut::exact_source(),
                runtime: RuntimePointer::source(),
                staged_cut: None,
                external_effects: false,
            },
            fault_at: None,
        }
    }

    pub fn with_fault(step: ExecutionStepId) -> Self {
        Self {
            fault_at: Some(step),
            ..Self::new()
        }
    }

    pub fn snapshot(&self) -> TargetSnapshot {
        self.state.clone()
    }

    fn fail_if_requested(&self, step: ExecutionStepId) -> Result<(), ExecutionFailure> {
        if self.fault_at == Some(step) {
            return Err(ExecutionFailure::new(
                "INJECTED_PROTOTYPE_FAILURE",
                format!("{step:?}"),
            ));
        }
        Ok(())
    }
}

impl ExecutionTargetAdapter for InMemoryTarget {
    type Snapshot = TargetSnapshot;

    fn binding(&self) -> PrototypeTargetBinding {
        PrototypeTargetBinding::exact()
    }

    fn capture_preimage(&self) -> Self::Snapshot {
        self.snapshot()
    }

    fn verify_preimage(&self, expected: &EventCut) -> Result<(), ExecutionFailure> {
        if &self.state.active_cut != expected
            || self.state.runtime != RuntimePointer::source()
            || self.state.staged_cut.is_some()
            || self.state.external_effects
        {
            return Err(ExecutionFailure::new(
                "TARGET_PREIMAGE_MISMATCH",
                "in-memory target",
            ));
        }
        Ok(())
    }

    fn stage(&mut self, candidate: &EventCut) -> Result<(), ExecutionFailure> {
        self.fail_if_requested(ExecutionStepId::Stage)?;
        self.state.staged_cut = Some(candidate.clone());
        Ok(())
    }

    fn activate(&mut self) -> Result<(), ExecutionFailure> {
        self.fail_if_requested(ExecutionStepId::Activate)?;
        self.state.runtime.generation = "epoch-002".to_owned();
        self.state.runtime.runtime_state = "prototype-active".to_owned();
        Ok(())
    }

    fn migrate(&mut self) -> Result<(), ExecutionFailure> {
        self.fail_if_requested(ExecutionStepId::Migrate)?;
        let staged = self
            .state
            .staged_cut
            .clone()
            .ok_or_else(|| ExecutionFailure::new("STAGED_CUT_MISSING", "migrate"))?;
        self.state.active_cut = staged;
        Ok(())
    }

    fn verify_target(&self, expected: &EventCut) -> Result<(), ExecutionFailure> {
        self.fail_if_requested(ExecutionStepId::VerifyTarget)?;
        if &self.state.active_cut != expected {
            return Err(ExecutionFailure::new(
                "TARGET_CUT_MISMATCH",
                self.state.active_cut.event_set_digest.clone(),
            ));
        }
        Ok(())
    }

    fn cutover(&mut self) -> Result<(), ExecutionFailure> {
        self.fail_if_requested(ExecutionStepId::Cutover)?;
        self.state.runtime.traffic_target = "epoch-002".to_owned();
        Ok(())
    }

    fn verify_postimage(&self, expected: &EventCut) -> Result<(), ExecutionFailure> {
        self.fail_if_requested(ExecutionStepId::VerifyPostimage)?;
        if &self.state.active_cut != expected
            || self.state.runtime.generation != "epoch-002"
            || self.state.runtime.runtime_state != "prototype-active"
            || self.state.runtime.traffic_target != "epoch-002"
            || self.state.runtime.live
            || self.state.external_effects
        {
            return Err(ExecutionFailure::new(
                "POSTIMAGE_MISMATCH",
                "prototype target",
            ));
        }
        Ok(())
    }

    fn restore(&mut self, preimage: &TargetSnapshot) -> Result<(), ExecutionFailure> {
        self.fail_if_requested(ExecutionStepId::Rollback)?;
        self.state = preimage.clone();
        Ok(())
    }

    fn verify_rollback(&self, preimage: &TargetSnapshot) -> Result<(), ExecutionFailure> {
        self.fail_if_requested(ExecutionStepId::VerifyRollback)?;
        if &self.state != preimage {
            return Err(ExecutionFailure::new(
                "ROLLBACK_PREIMAGE_MISMATCH",
                "in-memory target",
            ));
        }
        Ok(())
    }

    fn emergency_restore(&mut self, preimage: &TargetSnapshot) {
        self.state = preimage.clone();
    }
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct StepReceipt {
    pub step_id: ExecutionStepId,
    pub result: String,
    pub detail: BTreeMap<String, String>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ExecutionReceipt {
    pub schema_version: String,
    pub envelope_id: String,
    pub result: String,
    pub mode: ExecutionMode,
    pub trace: Vec<StepReceipt>,
    pub trace_digest: String,
    pub source_event_count: usize,
    pub source_event_set_digest: String,
    pub target_event_count: usize,
    pub target_event_set_digest: String,
    pub target_projection_digest: String,
    pub target_adapter_kind: String,
    pub target_adapter_identity: String,
    pub rollback_result: String,
    pub prototype_execution_ready: bool,
    pub live_execution_ready: bool,
    pub runtime_activated: bool,
    pub migration_performed: bool,
    pub cutover_performed: bool,
    pub external_effects: bool,
    pub authority_effect: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct ExecutionFailure {
    pub code: String,
    pub detail: String,
}

impl ExecutionFailure {
    pub fn new(code: &str, detail: impl Into<String>) -> Self {
        Self {
            code: code.to_owned(),
            detail: detail.into(),
        }
    }
}

impl Display for ExecutionFailure {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(formatter, "{}: {}", self.code, self.detail)
    }
}

impl Error for ExecutionFailure {}

#[derive(Clone, Copy, Debug, Default)]
pub struct ExecutionEngine;

impl ExecutionEngine {
    pub fn execute<T: ExecutionTargetAdapter>(
        &self,
        envelope: &ExecutionEnvelope,
        target: &mut T,
    ) -> Result<ExecutionReceipt, ExecutionFailure> {
        self.preflight(envelope, target)?;
        let mut trace = Vec::new();
        trace.push(step(
            ExecutionStepId::Preflight,
            [("mode", "prototype"), ("target", "in-memory")],
        ));

        let preimage = target.capture_preimage();
        trace.push(step(
            ExecutionStepId::CapturePreimage,
            [
                ("events", &envelope.source_cut.event_count.to_string()),
                ("event_set_digest", &envelope.source_cut.event_set_digest),
            ],
        ));

        let transition = (|| -> Result<(), ExecutionFailure> {
            target.stage(&envelope.target_cut)?;
            trace.push(step(
                ExecutionStepId::Stage,
                [("events", &envelope.target_cut.event_count.to_string())],
            ));

            target.activate()?;
            trace.push(step(
                ExecutionStepId::Activate,
                [("runtime_state", "prototype-active")],
            ));

            target.migrate()?;
            trace.push(step(
                ExecutionStepId::Migrate,
                [
                    (
                        "source_events",
                        &envelope.source_cut.event_count.to_string(),
                    ),
                    (
                        "target_events",
                        &envelope.target_cut.event_count.to_string(),
                    ),
                ],
            ));

            target.verify_target(&envelope.target_cut)?;
            trace.push(step(
                ExecutionStepId::VerifyTarget,
                [
                    ("event_set_digest", &envelope.target_cut.event_set_digest),
                    ("projection_digest", &envelope.target_cut.projection_digest),
                ],
            ));

            target.cutover()?;
            trace.push(step(
                ExecutionStepId::Cutover,
                [("traffic_target", "epoch-002"), ("live", "false")],
            ));

            target.verify_postimage(&envelope.target_cut)?;
            trace.push(step(
                ExecutionStepId::VerifyPostimage,
                [("postimage", "exact")],
            ));

            target.restore(&preimage)?;
            trace.push(step(
                ExecutionStepId::Rollback,
                [("restored", "source-preimage")],
            ));

            target.verify_rollback(&preimage)?;
            trace.push(step(
                ExecutionStepId::VerifyRollback,
                [("bytes", "equivalent"), ("state", "equivalent")],
            ));
            Ok(())
        })();

        if let Err(failure) = transition {
            target.emergency_restore(&preimage);
            return Err(failure);
        }

        let trace_digest = digest_serialized(&trace)?;
        Ok(ExecutionReceipt {
            schema_version: "cal-rust-execution-envelope-receipt/v2-prototype".to_owned(),
            envelope_id: envelope.envelope_id.clone(),
            result: "PASS".to_owned(),
            mode: ExecutionMode::Prototype,
            trace,
            trace_digest,
            source_event_count: envelope.source_cut.event_count,
            source_event_set_digest: envelope.source_cut.event_set_digest.clone(),
            target_event_count: envelope.target_cut.event_count,
            target_event_set_digest: envelope.target_cut.event_set_digest.clone(),
            target_projection_digest: envelope.target_cut.projection_digest.clone(),
            target_adapter_kind: envelope.target.kind.clone(),
            target_adapter_identity: envelope.target.identity.clone(),
            rollback_result: "PASS".to_owned(),
            prototype_execution_ready: true,
            live_execution_ready: false,
            runtime_activated: false,
            migration_performed: false,
            cutover_performed: false,
            external_effects: false,
            authority_effect: "none".to_owned(),
        })
    }

    fn preflight<T: ExecutionTargetAdapter>(
        &self,
        envelope: &ExecutionEnvelope,
        target: &T,
    ) -> Result<(), ExecutionFailure> {
        if envelope.mode == ExecutionMode::Live {
            return Err(ExecutionFailure::new(
                "LIVE_BINDINGS_MISSING",
                "exact target, credential, maintenance, preimage, abort, and validation bindings",
            ));
        }
        if envelope.decision_digest != D65CUT_DECISION_DIGEST
            || envelope.selected_option_id != "D65CUT-1"
        {
            return Err(ExecutionFailure::new(
                "AUTHORIZATION_BINDING_MISMATCH",
                &envelope.decision_digest,
            ));
        }
        if envelope.target != PrototypeTargetBinding::exact()
            || target.binding() != envelope.target
            || envelope.target.live
            || envelope.target.production_data
            || envelope.target.credential_kind != "none"
            || envelope.target.external_effects
        {
            return Err(ExecutionFailure::new(
                "PROTOTYPE_TARGET_BOUNDARY_VIOLATION",
                &envelope.target.identity,
            ));
        }
        if envelope.source_cut != EventCut::exact_source()
            || envelope.target_cut != EventCut::exact_target()
        {
            return Err(ExecutionFailure::new(
                "EVENT_CUT_BINDING_MISMATCH",
                &envelope.target_cut.event_set_digest,
            ));
        }
        if envelope.step_order != EXACT_STEP_ORDER
            || !envelope.prototype_execution_ready
            || envelope.live_execution_ready
            || !envelope.always_rollback_prototype
            || envelope.authority_effect != "none"
        {
            return Err(ExecutionFailure::new(
                "EXECUTION_POLICY_MISMATCH",
                &envelope.envelope_id,
            ));
        }
        target.verify_preimage(&envelope.source_cut)
    }
}

fn step<const N: usize>(step_id: ExecutionStepId, detail: [(&str, &str); N]) -> StepReceipt {
    StepReceipt {
        step_id,
        result: "PASS".to_owned(),
        detail: detail
            .into_iter()
            .map(|(key, value)| (key.to_owned(), value.to_owned()))
            .collect(),
    }
}

fn digest_serialized<T: Serialize>(value: &T) -> Result<String, ExecutionFailure> {
    let serialized = canonical_json(value)
        .map_err(|error| ExecutionFailure::new("TRACE_SERIALIZATION_FAILED", error.to_string()))?;
    Ok(format!("{:x}", Sha256::digest(serialized.as_bytes())))
}
