//! Path-confined disposable filesystem adapter and rehearsal evidence.
//!
//! The adapter creates its own process-temporary directory. It accepts no caller path, network
//! location, credentials, live binding, or production data. A completed rehearsal removes the
//! directory before returning.

use crate::{
    EventCut, ExecutionEngine, ExecutionFailure, ExecutionStepId, ExecutionTargetAdapter,
    PrototypeTargetBinding, RuntimePointer, TargetSnapshot,
};
use cal_ontology_lifecycle::canonical_json;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};

pub const FILESYSTEM_REHEARSAL_CANDIDATE_ID: &str =
    "CAL-D65-EPOCH-002-FILESYSTEM-REHEARSAL-PROTOTYPE-004";
pub const L2_CERTIFICATION_CANDIDATE_ID: &str =
    "CAL-D65-EPOCH-002-ADAPTER-CERTIFICATION-PROTOTYPE-003";
pub const L2_CERTIFICATION_RECEIPT_DIGEST: &str =
    "4046bc8954c232e40e37b0e3b9d8d9f54f0a59b378cabc8f4d9d2d8277ad5080";

const STATE_FILE: &str = "target-state.json";
static NEXT_REHEARSAL_ID: AtomicU64 = AtomicU64::new(1);

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct FilesystemSnapshot {
    pub state_bytes: Vec<u8>,
    pub state_digest: String,
}

#[derive(Debug)]
pub struct DisposableFilesystemTarget {
    root: PathBuf,
    fault_at: Option<ExecutionStepId>,
    cleaned: bool,
}

impl DisposableFilesystemTarget {
    pub fn new() -> Result<Self, ExecutionFailure> {
        Self::create(None)
    }

    pub fn with_fault(step: ExecutionStepId) -> Result<Self, ExecutionFailure> {
        Self::create(Some(step))
    }

    fn create(fault_at: Option<ExecutionStepId>) -> Result<Self, ExecutionFailure> {
        let id = NEXT_REHEARSAL_ID.fetch_add(1, Ordering::Relaxed);
        let root = std::env::temp_dir().join(format!(
            "cal-d65-filesystem-rehearsal-{}-{id}",
            std::process::id()
        ));
        fs::create_dir(&root).map_err(|error| io_failure("CREATE_REHEARSAL_ROOT_FAILED", error))?;
        let mut target = Self {
            root,
            fault_at,
            cleaned: false,
        };
        target.write_state(&TargetSnapshot {
            active_cut: EventCut::exact_source(),
            runtime: RuntimePointer::source(),
            staged_cut: None,
            external_effects: false,
        })?;
        Ok(target)
    }

    pub fn root(&self) -> &Path {
        &self.root
    }

    pub fn state_bytes(&self) -> Result<Vec<u8>, ExecutionFailure> {
        fs::read(self.state_path()).map_err(|error| io_failure("READ_TARGET_STATE_FAILED", error))
    }

    pub fn state_digest(&self) -> Result<String, ExecutionFailure> {
        Ok(digest_bytes(&self.state_bytes()?))
    }

    pub fn cleanup(mut self) -> Result<(), ExecutionFailure> {
        self.remove_root()
    }

    fn state_path(&self) -> PathBuf {
        self.root.join(STATE_FILE)
    }

    fn read_state(&self) -> Result<TargetSnapshot, ExecutionFailure> {
        let bytes = self.state_bytes()?;
        serde_json::from_slice(&bytes)
            .map_err(|error| ExecutionFailure::new("DECODE_TARGET_STATE_FAILED", error.to_string()))
    }

    fn write_state(&mut self, state: &TargetSnapshot) -> Result<(), ExecutionFailure> {
        if self.root.parent() != Some(std::env::temp_dir().as_path()) {
            return Err(ExecutionFailure::new(
                "FILESYSTEM_PATH_BOUNDARY_VIOLATION",
                "rehearsal root is outside the process temporary directory",
            ));
        }
        let serialized = canonical_json(state).map_err(|error| {
            ExecutionFailure::new("ENCODE_TARGET_STATE_FAILED", error.to_string())
        })?;
        let pending = self.root.join("target-state.next");
        fs::write(&pending, serialized.as_bytes())
            .map_err(|error| io_failure("WRITE_TARGET_STATE_FAILED", error))?;
        fs::rename(&pending, self.state_path())
            .map_err(|error| io_failure("COMMIT_TARGET_STATE_FAILED", error))
    }

    fn fail_if_requested(&self, step: ExecutionStepId) -> Result<(), ExecutionFailure> {
        if self.fault_at == Some(step) {
            return Err(ExecutionFailure::new(
                "INJECTED_FILESYSTEM_REHEARSAL_FAILURE",
                format!("{step:?}"),
            ));
        }
        Ok(())
    }

    fn remove_root(&mut self) -> Result<(), ExecutionFailure> {
        if self.root.exists() {
            fs::remove_dir_all(&self.root)
                .map_err(|error| io_failure("REMOVE_REHEARSAL_ROOT_FAILED", error))?;
        }
        self.cleaned = true;
        Ok(())
    }
}

impl Drop for DisposableFilesystemTarget {
    fn drop(&mut self) {
        if !self.cleaned && self.root.exists() {
            let _ = fs::remove_dir_all(&self.root);
        }
    }
}

impl ExecutionTargetAdapter for DisposableFilesystemTarget {
    type Snapshot = FilesystemSnapshot;

    fn binding(&self) -> PrototypeTargetBinding {
        PrototypeTargetBinding::exact_filesystem()
    }

    fn capture_preimage(&self) -> Self::Snapshot {
        let state_bytes = self.state_bytes().unwrap_or_default();
        FilesystemSnapshot {
            state_digest: digest_bytes(&state_bytes),
            state_bytes,
        }
    }

    fn verify_preimage(&self, expected: &EventCut) -> Result<(), ExecutionFailure> {
        let state = self.read_state()?;
        if &state.active_cut != expected
            || state.runtime != RuntimePointer::source()
            || state.staged_cut.is_some()
            || state.external_effects
        {
            return Err(ExecutionFailure::new(
                "TARGET_PREIMAGE_MISMATCH",
                "disposable filesystem target",
            ));
        }
        Ok(())
    }

    fn stage(&mut self, candidate: &EventCut) -> Result<(), ExecutionFailure> {
        self.fail_if_requested(ExecutionStepId::Stage)?;
        let mut state = self.read_state()?;
        state.staged_cut = Some(candidate.clone());
        self.write_state(&state)
    }

    fn activate(&mut self) -> Result<(), ExecutionFailure> {
        self.fail_if_requested(ExecutionStepId::Activate)?;
        let mut state = self.read_state()?;
        state.runtime.generation = "epoch-002".to_owned();
        state.runtime.runtime_state = "prototype-active".to_owned();
        self.write_state(&state)
    }

    fn migrate(&mut self) -> Result<(), ExecutionFailure> {
        self.fail_if_requested(ExecutionStepId::Migrate)?;
        let mut state = self.read_state()?;
        state.active_cut = state
            .staged_cut
            .clone()
            .ok_or_else(|| ExecutionFailure::new("STAGED_CUT_MISSING", "migrate"))?;
        self.write_state(&state)
    }

    fn verify_target(&self, expected: &EventCut) -> Result<(), ExecutionFailure> {
        self.fail_if_requested(ExecutionStepId::VerifyTarget)?;
        let state = self.read_state()?;
        if &state.active_cut != expected {
            return Err(ExecutionFailure::new(
                "TARGET_CUT_MISMATCH",
                state.active_cut.event_set_digest,
            ));
        }
        Ok(())
    }

    fn cutover(&mut self) -> Result<(), ExecutionFailure> {
        self.fail_if_requested(ExecutionStepId::Cutover)?;
        let mut state = self.read_state()?;
        state.runtime.traffic_target = "epoch-002".to_owned();
        self.write_state(&state)
    }

    fn verify_postimage(&self, expected: &EventCut) -> Result<(), ExecutionFailure> {
        self.fail_if_requested(ExecutionStepId::VerifyPostimage)?;
        let state = self.read_state()?;
        if &state.active_cut != expected
            || state.runtime.generation != "epoch-002"
            || state.runtime.runtime_state != "prototype-active"
            || state.runtime.traffic_target != "epoch-002"
            || state.runtime.live
            || state.external_effects
        {
            return Err(ExecutionFailure::new(
                "POSTIMAGE_MISMATCH",
                "disposable filesystem target",
            ));
        }
        Ok(())
    }

    fn restore(&mut self, preimage: &Self::Snapshot) -> Result<(), ExecutionFailure> {
        self.fail_if_requested(ExecutionStepId::Rollback)?;
        fs::write(self.state_path(), &preimage.state_bytes)
            .map_err(|error| io_failure("RESTORE_TARGET_STATE_FAILED", error))
    }

    fn verify_rollback(&self, preimage: &Self::Snapshot) -> Result<(), ExecutionFailure> {
        self.fail_if_requested(ExecutionStepId::VerifyRollback)?;
        let current = self.state_bytes()?;
        if current != preimage.state_bytes || digest_bytes(&current) != preimage.state_digest {
            return Err(ExecutionFailure::new(
                "ROLLBACK_PREIMAGE_MISMATCH",
                "disposable filesystem target bytes",
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
pub struct FilesystemRehearsalReportBody {
    pub schema_version: String,
    pub candidate_id: String,
    pub baseline_candidate_id: String,
    pub baseline_receipt_digest: String,
    pub target_binding: PrototypeTargetBinding,
    pub execution_trace_digest: String,
    pub preimage_digest: String,
    pub final_state_digest: String,
    pub rollback_exact: bool,
    pub cleanup_verified: bool,
    pub path_policy: String,
    pub disposable_local_filesystem_effects: bool,
    pub live_execution_ready: bool,
    pub external_effects: bool,
    pub result: String,
    pub authority_effect: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct FilesystemRehearsalReport {
    #[serde(flatten)]
    pub body: FilesystemRehearsalReportBody,
    pub report_digest: String,
}

impl FilesystemRehearsalReport {
    pub fn canonical_json(&self) -> Result<String, ExecutionFailure> {
        canonical_json(self).map_err(|error| {
            ExecutionFailure::new("FILESYSTEM_REPORT_SERIALIZATION_FAILED", error.to_string())
        })
    }
}

pub fn rehearse_disposable_filesystem() -> Result<FilesystemRehearsalReport, ExecutionFailure> {
    let mut target = DisposableFilesystemTarget::new()?;
    let root = target.root().to_path_buf();
    let preimage_digest = target.state_digest()?;
    let receipt = ExecutionEngine.execute(
        &crate::ExecutionEnvelope::exact_filesystem_rehearsal(),
        &mut target,
    )?;
    let final_state_digest = target.state_digest()?;
    let rollback_exact = preimage_digest == final_state_digest;
    target.cleanup()?;
    let cleanup_verified = !root.exists();
    let body = FilesystemRehearsalReportBody {
        schema_version: "cal.d65-filesystem-rehearsal-report/v1".to_owned(),
        candidate_id: FILESYSTEM_REHEARSAL_CANDIDATE_ID.to_owned(),
        baseline_candidate_id: L2_CERTIFICATION_CANDIDATE_ID.to_owned(),
        baseline_receipt_digest: L2_CERTIFICATION_RECEIPT_DIGEST.to_owned(),
        target_binding: PrototypeTargetBinding::exact_filesystem(),
        execution_trace_digest: receipt.trace_digest,
        preimage_digest,
        final_state_digest,
        rollback_exact,
        cleanup_verified,
        path_policy: "adapter-created-process-temporary-directory".to_owned(),
        disposable_local_filesystem_effects: true,
        live_execution_ready: false,
        external_effects: false,
        result: if rollback_exact && cleanup_verified {
            "PASS".to_owned()
        } else {
            "BLOCK".to_owned()
        },
        authority_effect: "none".to_owned(),
    };
    let report_digest = digest_serialized(&body)?;
    Ok(FilesystemRehearsalReport {
        body,
        report_digest,
    })
}

fn digest_bytes(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

fn digest_serialized<T: Serialize>(value: &T) -> Result<String, ExecutionFailure> {
    let serialized = canonical_json(value).map_err(|error| {
        ExecutionFailure::new("FILESYSTEM_REPORT_SERIALIZATION_FAILED", error.to_string())
    })?;
    Ok(digest_bytes(serialized.as_bytes()))
}

fn io_failure(code: &str, error: std::io::Error) -> ExecutionFailure {
    ExecutionFailure::new(code, error.to_string())
}
