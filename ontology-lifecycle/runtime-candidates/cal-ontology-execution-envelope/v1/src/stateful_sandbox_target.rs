//! Non-live state-bearing L4 sandbox target and bounded activation harness.
//!
//! Unlike the L3 rehearsal, activation state survives the activation call so a
//! caller can inspect it before explicit teardown. The adapter owns its process-
//! temporary root and has no path, credential, network, production-data, live,
//! migration, or cutover surface. The existing ten-step engine intentionally
//! refuses this distinct binding.

use crate::{
    EventCut, ExecutionFailure, ExecutionMode, ExecutionStepId, ExecutionTargetAdapter,
    PrototypeTargetBinding, RuntimePointer, TargetSnapshot,
};
use cal_ontology_lifecycle::canonical_json;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};

pub const STATEFUL_SANDBOX_CANDIDATE_ID: &str =
    "CAL-D65-EPOCH-003-STATE-BEARING-SANDBOX-PROTOTYPE-005";
pub const STATEFUL_SANDBOX_IDENTITY: &str =
    "cal.prototype.rust-state-bearing-sandbox-target/epoch-003";
pub const L4_SELECTION_DECISION_DIGEST: &str =
    "405b0a017038f85faea86f686e1289f330375587982772172947577a4c5227dc";
pub const L4_SELECTION_VALIDATION_DIGEST: &str =
    "cfb97c8d5ea8e0a338a37a1abd6530bcc0d3ba1023223fe10a2c150cfbd6ee87";
pub const L3_FILESYSTEM_RECEIPT_DIGEST: &str =
    "24168bc1b692b8ed1893372201349f46e75955aab9c3dd173dc2a32e576f77fc";

const STATE_FILE: &str = "sandbox-state.json";
static NEXT_SANDBOX_ID: AtomicU64 = AtomicU64::new(1);

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct SandboxActivationRequest {
    pub schema_version: String,
    pub candidate_id: String,
    pub decision_digest: String,
    pub decision_validation_digest: String,
    pub selected_option_id: String,
    pub mode: ExecutionMode,
    pub target: PrototypeTargetBinding,
    pub source_cut: EventCut,
    pub staged_cut: EventCut,
    pub observation_policy: String,
    pub teardown_policy: String,
    pub live_execution_ready: bool,
    pub authority_effect: String,
}

impl SandboxActivationRequest {
    pub fn exact() -> Self {
        Self {
            schema_version: "cal.d65-state-bearing-sandbox-activation/v1".to_owned(),
            candidate_id: STATEFUL_SANDBOX_CANDIDATE_ID.to_owned(),
            decision_digest: L4_SELECTION_DECISION_DIGEST.to_owned(),
            decision_validation_digest: L4_SELECTION_VALIDATION_DIGEST.to_owned(),
            selected_option_id: "L4TGT-1".to_owned(),
            mode: ExecutionMode::Prototype,
            target: PrototypeTargetBinding::exact_stateful_sandbox(),
            source_cut: EventCut::exact_source(),
            staged_cut: EventCut::exact_target(),
            observation_policy: "state-must-survive-activation-call".to_owned(),
            teardown_policy: "explicit-exact-restore-then-remove".to_owned(),
            live_execution_ready: false,
            authority_effect: "none".to_owned(),
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct SandboxSnapshot {
    pub state_bytes: Vec<u8>,
    pub state_digest: String,
}

#[derive(Debug)]
pub struct StatefulSandboxTarget {
    root: PathBuf,
    initial: SandboxSnapshot,
    fault_at: Option<ExecutionStepId>,
    cleaned: bool,
}

impl StatefulSandboxTarget {
    pub fn new() -> Result<Self, ExecutionFailure> {
        Self::create(None)
    }

    pub fn with_fault(step: ExecutionStepId) -> Result<Self, ExecutionFailure> {
        Self::create(Some(step))
    }

    fn create(fault_at: Option<ExecutionStepId>) -> Result<Self, ExecutionFailure> {
        let id = NEXT_SANDBOX_ID.fetch_add(1, Ordering::Relaxed);
        let root = std::env::temp_dir().join(format!(
            "cal-d65-state-bearing-sandbox-{}-{id}",
            std::process::id()
        ));
        fs::create_dir(&root).map_err(|error| io_failure("CREATE_SANDBOX_ROOT_FAILED", error))?;
        let mut target = Self {
            root,
            initial: SandboxSnapshot {
                state_bytes: Vec::new(),
                state_digest: String::new(),
            },
            fault_at,
            cleaned: false,
        };
        target.write_state(&source_state())?;
        target.initial = target.snapshot_bytes()?;
        Ok(target)
    }

    pub fn root(&self) -> &Path {
        &self.root
    }

    pub fn state(&self) -> Result<TargetSnapshot, ExecutionFailure> {
        serde_json::from_slice(&self.state_bytes()?).map_err(|error| {
            ExecutionFailure::new("DECODE_SANDBOX_STATE_FAILED", error.to_string())
        })
    }

    pub fn state_bytes(&self) -> Result<Vec<u8>, ExecutionFailure> {
        fs::read(self.state_path()).map_err(|error| io_failure("READ_SANDBOX_STATE_FAILED", error))
    }

    pub fn state_digest(&self) -> Result<String, ExecutionFailure> {
        Ok(digest_bytes(&self.state_bytes()?))
    }

    pub fn teardown(mut self) -> Result<SandboxTeardownReceipt, ExecutionFailure> {
        let initial = self.initial.clone();
        self.restore(&initial)?;
        self.verify_rollback(&initial)?;
        let restored_digest = self.state_digest()?;
        self.remove_root()?;
        let cleanup_verified = !self.root.exists();
        Ok(SandboxTeardownReceipt {
            restored_preimage_exact: restored_digest == initial.state_digest,
            restored_state_digest: restored_digest,
            cleanup_verified,
            external_effects: false,
            authority_effect: "none".to_owned(),
        })
    }

    fn state_path(&self) -> PathBuf {
        self.root.join(STATE_FILE)
    }

    fn snapshot_bytes(&self) -> Result<SandboxSnapshot, ExecutionFailure> {
        let state_bytes = self.state_bytes()?;
        Ok(SandboxSnapshot {
            state_digest: digest_bytes(&state_bytes),
            state_bytes,
        })
    }

    fn write_state(&mut self, state: &TargetSnapshot) -> Result<(), ExecutionFailure> {
        if self.root.parent() != Some(std::env::temp_dir().as_path()) {
            return Err(ExecutionFailure::new(
                "SANDBOX_PATH_BOUNDARY_VIOLATION",
                "sandbox root is outside the process temporary directory",
            ));
        }
        let serialized = canonical_json(state).map_err(|error| {
            ExecutionFailure::new("ENCODE_SANDBOX_STATE_FAILED", error.to_string())
        })?;
        let pending = self.root.join("sandbox-state.next");
        fs::write(&pending, serialized.as_bytes())
            .map_err(|error| io_failure("WRITE_SANDBOX_STATE_FAILED", error))?;
        fs::rename(&pending, self.state_path())
            .map_err(|error| io_failure("COMMIT_SANDBOX_STATE_FAILED", error))
    }

    fn fail_if_requested(&self, step: ExecutionStepId) -> Result<(), ExecutionFailure> {
        if self.fault_at == Some(step) {
            return Err(ExecutionFailure::new(
                "INJECTED_STATEFUL_SANDBOX_FAILURE",
                format!("{step:?}"),
            ));
        }
        Ok(())
    }

    fn remove_root(&mut self) -> Result<(), ExecutionFailure> {
        if self.root.exists() {
            fs::remove_dir_all(&self.root)
                .map_err(|error| io_failure("REMOVE_SANDBOX_ROOT_FAILED", error))?;
        }
        self.cleaned = true;
        Ok(())
    }
}

impl Drop for StatefulSandboxTarget {
    fn drop(&mut self) {
        if !self.cleaned && self.root.exists() {
            let _ = fs::remove_dir_all(&self.root);
        }
    }
}

impl ExecutionTargetAdapter for StatefulSandboxTarget {
    type Snapshot = SandboxSnapshot;

    fn binding(&self) -> PrototypeTargetBinding {
        PrototypeTargetBinding::exact_stateful_sandbox()
    }

    fn capture_preimage(&self) -> Self::Snapshot {
        self.snapshot_bytes().unwrap_or_else(|_| SandboxSnapshot {
            state_bytes: Vec::new(),
            state_digest: String::new(),
        })
    }

    fn verify_preimage(&self, expected: &EventCut) -> Result<(), ExecutionFailure> {
        let state = self.state()?;
        if &state.active_cut != expected
            || state.runtime != RuntimePointer::source()
            || state.staged_cut.is_some()
            || state.external_effects
        {
            return Err(ExecutionFailure::new(
                "SANDBOX_PREIMAGE_MISMATCH",
                "state-bearing sandbox target",
            ));
        }
        Ok(())
    }

    fn stage(&mut self, candidate: &EventCut) -> Result<(), ExecutionFailure> {
        self.fail_if_requested(ExecutionStepId::Stage)?;
        let mut state = self.state()?;
        state.staged_cut = Some(candidate.clone());
        self.write_state(&state)
    }

    fn activate(&mut self) -> Result<(), ExecutionFailure> {
        self.fail_if_requested(ExecutionStepId::Activate)?;
        let mut state = self.state()?;
        state.runtime.generation = "epoch-002".to_owned();
        state.runtime.runtime_state = "prototype-sandbox-active".to_owned();
        self.write_state(&state)
    }

    fn migrate(&mut self) -> Result<(), ExecutionFailure> {
        Err(ExecutionFailure::new(
            "STATEFUL_SANDBOX_MIGRATION_FORBIDDEN",
            STATEFUL_SANDBOX_IDENTITY,
        ))
    }

    fn verify_target(&self, expected: &EventCut) -> Result<(), ExecutionFailure> {
        let state = self.state()?;
        if state.staged_cut.as_ref() != Some(expected) {
            return Err(ExecutionFailure::new(
                "SANDBOX_STAGED_CUT_MISMATCH",
                expected.event_set_digest.clone(),
            ));
        }
        Ok(())
    }

    fn cutover(&mut self) -> Result<(), ExecutionFailure> {
        Err(ExecutionFailure::new(
            "STATEFUL_SANDBOX_CUTOVER_FORBIDDEN",
            STATEFUL_SANDBOX_IDENTITY,
        ))
    }

    fn verify_postimage(&self, expected: &EventCut) -> Result<(), ExecutionFailure> {
        self.verify_target(expected)
    }

    fn restore(&mut self, preimage: &Self::Snapshot) -> Result<(), ExecutionFailure> {
        fs::write(self.state_path(), &preimage.state_bytes)
            .map_err(|error| io_failure("RESTORE_SANDBOX_STATE_FAILED", error))
    }

    fn verify_rollback(&self, preimage: &Self::Snapshot) -> Result<(), ExecutionFailure> {
        let current = self.state_bytes()?;
        if current != preimage.state_bytes || digest_bytes(&current) != preimage.state_digest {
            return Err(ExecutionFailure::new(
                "SANDBOX_PREIMAGE_RESTORE_MISMATCH",
                STATEFUL_SANDBOX_IDENTITY,
            ));
        }
        Ok(())
    }

    fn emergency_restore(&mut self, preimage: &Self::Snapshot) {
        let _ = fs::write(self.state_path(), &preimage.state_bytes);
    }
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct SandboxActivationObservation {
    pub preimage_digest: String,
    pub activated_state_digest: String,
    pub active_cut_unchanged: bool,
    pub staged_cut_exact: bool,
    pub sandbox_activation_observed: bool,
    pub state_survives_observation: bool,
    pub explicit_teardown_required: bool,
    pub migration_performed: bool,
    pub cutover_performed: bool,
    pub runtime_activated: bool,
    pub external_effects: bool,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct SandboxTeardownReceipt {
    pub restored_preimage_exact: bool,
    pub restored_state_digest: String,
    pub cleanup_verified: bool,
    pub external_effects: bool,
    pub authority_effect: String,
}

#[derive(Clone, Copy, Debug, Default)]
pub struct SandboxActivationHarness;

impl SandboxActivationHarness {
    pub fn activate(
        &self,
        request: &SandboxActivationRequest,
        target: &mut StatefulSandboxTarget,
    ) -> Result<SandboxActivationObservation, ExecutionFailure> {
        self.preflight(request, target)?;
        let preimage = target.capture_preimage();
        let transition = (|| -> Result<SandboxActivationObservation, ExecutionFailure> {
            target.stage(&request.staged_cut)?;
            target.activate()?;
            target.verify_target(&request.staged_cut)?;
            let state = target.state()?;
            let activated_state_digest = target.state_digest()?;
            let observation = SandboxActivationObservation {
                preimage_digest: preimage.state_digest.clone(),
                activated_state_digest,
                active_cut_unchanged: state.active_cut == request.source_cut,
                staged_cut_exact: state.staged_cut.as_ref() == Some(&request.staged_cut),
                sandbox_activation_observed: state.runtime.generation == "epoch-002"
                    && state.runtime.runtime_state == "prototype-sandbox-active"
                    && state.runtime.traffic_target == "epoch-001"
                    && !state.runtime.live,
                state_survives_observation: target.root().is_dir() && target.state_path().is_file(),
                explicit_teardown_required: true,
                migration_performed: false,
                cutover_performed: false,
                runtime_activated: false,
                external_effects: false,
            };
            if !observation.active_cut_unchanged
                || !observation.staged_cut_exact
                || !observation.sandbox_activation_observed
                || !observation.state_survives_observation
            {
                return Err(ExecutionFailure::new(
                    "SANDBOX_ACTIVATION_OBSERVATION_MISMATCH",
                    request.candidate_id.clone(),
                ));
            }
            Ok(observation)
        })();
        if transition.is_err() {
            target.emergency_restore(&preimage);
        }
        transition
    }

    fn preflight(
        &self,
        request: &SandboxActivationRequest,
        target: &StatefulSandboxTarget,
    ) -> Result<(), ExecutionFailure> {
        if request.mode == ExecutionMode::Live {
            return Err(ExecutionFailure::new(
                "STATEFUL_SANDBOX_LIVE_MODE_FORBIDDEN",
                STATEFUL_SANDBOX_IDENTITY,
            ));
        }
        if request != &SandboxActivationRequest::exact() {
            return Err(ExecutionFailure::new(
                "STATEFUL_SANDBOX_REQUEST_MISMATCH",
                request.candidate_id.clone(),
            ));
        }
        if target.binding() != request.target
            || request.target.live
            || request.target.production_data
            || request.target.credential_kind != "none"
            || request.target.external_effects
        {
            return Err(ExecutionFailure::new(
                "STATEFUL_SANDBOX_BOUNDARY_VIOLATION",
                request.target.identity.clone(),
            ));
        }
        target.verify_preimage(&request.source_cut)
    }
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct StatefulSandboxReportBody {
    pub schema_version: String,
    pub candidate_id: String,
    pub selected_option_id: String,
    pub selection_decision_digest: String,
    pub selection_validation_digest: String,
    pub predecessor_receipt_digest: String,
    pub target_binding: PrototypeTargetBinding,
    pub observation: SandboxActivationObservation,
    pub teardown: SandboxTeardownReceipt,
    pub path_policy: String,
    pub local_disposable_filesystem_effects: bool,
    pub live_execution_ready: bool,
    pub product_approved: bool,
    pub adapter_admitted: bool,
    pub result: String,
    pub authority_effect: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct StatefulSandboxReport {
    #[serde(flatten)]
    pub body: StatefulSandboxReportBody,
    pub report_digest: String,
}

impl StatefulSandboxReport {
    pub fn canonical_json(&self) -> Result<String, ExecutionFailure> {
        canonical_json(self).map_err(|error| {
            ExecutionFailure::new(
                "STATEFUL_SANDBOX_REPORT_SERIALIZATION_FAILED",
                error.to_string(),
            )
        })
    }
}

pub fn rehearse_stateful_sandbox() -> Result<StatefulSandboxReport, ExecutionFailure> {
    let mut target = StatefulSandboxTarget::new()?;
    let observation =
        SandboxActivationHarness.activate(&SandboxActivationRequest::exact(), &mut target)?;
    let teardown = target.teardown()?;
    let passed = observation.state_survives_observation
        && observation.sandbox_activation_observed
        && observation.active_cut_unchanged
        && observation.staged_cut_exact
        && !observation.runtime_activated
        && teardown.restored_preimage_exact
        && teardown.cleanup_verified;
    let body = StatefulSandboxReportBody {
        schema_version: "cal.d65-state-bearing-sandbox-report/v1".to_owned(),
        candidate_id: STATEFUL_SANDBOX_CANDIDATE_ID.to_owned(),
        selected_option_id: "L4TGT-1".to_owned(),
        selection_decision_digest: L4_SELECTION_DECISION_DIGEST.to_owned(),
        selection_validation_digest: L4_SELECTION_VALIDATION_DIGEST.to_owned(),
        predecessor_receipt_digest: L3_FILESYSTEM_RECEIPT_DIGEST.to_owned(),
        target_binding: PrototypeTargetBinding::exact_stateful_sandbox(),
        observation,
        teardown,
        path_policy: "adapter-created-process-temporary-directory".to_owned(),
        local_disposable_filesystem_effects: true,
        live_execution_ready: false,
        product_approved: false,
        adapter_admitted: false,
        result: if passed { "PASS" } else { "BLOCK" }.to_owned(),
        authority_effect: "none".to_owned(),
    };
    let report_digest = digest_serialized(&body)?;
    Ok(StatefulSandboxReport {
        body,
        report_digest,
    })
}

fn source_state() -> TargetSnapshot {
    TargetSnapshot {
        active_cut: EventCut::exact_source(),
        runtime: RuntimePointer::source(),
        staged_cut: None,
        external_effects: false,
    }
}

fn digest_bytes(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

fn digest_serialized<T: Serialize>(value: &T) -> Result<String, ExecutionFailure> {
    let serialized = canonical_json(value).map_err(|error| {
        ExecutionFailure::new(
            "STATEFUL_SANDBOX_REPORT_SERIALIZATION_FAILED",
            error.to_string(),
        )
    })?;
    Ok(digest_bytes(serialized.as_bytes()))
}

fn io_failure(code: &str, error: std::io::Error) -> ExecutionFailure {
    ExecutionFailure::new(code, error.to_string())
}
