//! Process-local active ontology runtime candidate.
//!
//! This successor binds the admitted L4 state-bearing sandbox to the deterministic
//! event runtime. It keeps one calculated ontology projection inspectable across
//! multiple commands and requires explicit stop or EOF teardown. It is not a live
//! service, a production adapter, or a source of governance authority.

use cal_ontology_execution_envelope::ExecutionFailure;
use cal_ontology_execution_envelope::stateful_sandbox_target::{
    SandboxActivationHarness, SandboxActivationObservation, SandboxActivationRequest,
    StatefulSandboxTarget,
};
use cal_ontology_lifecycle::{ConsistentOntologyCut, EventStore, machine_projection};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::error::Error;
use std::fmt::{self, Display};
use std::fs;
use std::path::{Path, PathBuf};

pub const ACTIVE_RUNTIME_CANDIDATE_ID: &str =
    "CAL-D65-EPOCH-004-LOCAL-ACTIVE-RUNTIME-PROTOTYPE-006";
pub const ACTIVE_RUNTIME_IDENTITY: &str =
    "cal.prototype.rust-local-active-ontology-runtime/epoch-004";
pub const L4_PRODUCT_APPROVAL_DECISION_DIGEST: &str =
    "6f57ea86f8547fece058fa70e01c7afe4ed65bc97ec6b3a4f66f774a1f6301f3";
pub const L4_PRODUCT_APPROVAL_VALIDATION_DIGEST: &str =
    "a2030d07bcec5e53b41a8754c525166cc56773a1ee3710a656f5a7b1dd81eb96";
pub const L4_ADAPTER_ADMISSION_DECISION_DIGEST: &str =
    "8adade17ddbbdaa9e145a940d3cc2f7245a767aae40411ef961f6368ac022d92";
pub const L4_ADAPTER_ADMISSION_VALIDATION_DIGEST: &str =
    "41beb5b374f5e9fe7124c6929caaebbdcae2145d76755e7ddc983834ce91d523";
pub const CANONICAL_CURSOR: u64 = 47;
pub const CANONICAL_EVENT_COUNT: usize = 47;
pub const CANONICAL_SUBJECT_COUNT: usize = 47;
pub const CANONICAL_EVENT_SET_DIGEST: &str =
    "7a1089513ef4ed74bf70d6ed724d78f42a0e15cd267ac141213880026f06d6e2";

const PROJECTION_FILE: &str = "calculated-projection.json";

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct RuntimeActivationContract {
    pub schema_version: String,
    pub candidate_id: String,
    pub runtime_identity: String,
    pub l4_product_approval_decision_digest: String,
    pub l4_product_approval_validation_digest: String,
    pub l4_adapter_admission_decision_digest: String,
    pub l4_adapter_admission_validation_digest: String,
    pub semantic_cursor: u64,
    pub source_event_count: usize,
    pub subject_count: usize,
    pub source_event_set_digest: String,
    pub interaction: String,
    pub stop_policy: String,
    pub live: bool,
    pub network: bool,
    pub credential_kind: String,
    pub external_effects: bool,
    pub authority_effect: String,
}

impl RuntimeActivationContract {
    pub fn exact() -> Self {
        Self {
            schema_version: "cal.d65-local-active-runtime-contract/v1".to_owned(),
            candidate_id: ACTIVE_RUNTIME_CANDIDATE_ID.to_owned(),
            runtime_identity: ACTIVE_RUNTIME_IDENTITY.to_owned(),
            l4_product_approval_decision_digest: L4_PRODUCT_APPROVAL_DECISION_DIGEST.to_owned(),
            l4_product_approval_validation_digest: L4_PRODUCT_APPROVAL_VALIDATION_DIGEST.to_owned(),
            l4_adapter_admission_decision_digest: L4_ADAPTER_ADMISSION_DECISION_DIGEST.to_owned(),
            l4_adapter_admission_validation_digest: L4_ADAPTER_ADMISSION_VALIDATION_DIGEST
                .to_owned(),
            semantic_cursor: CANONICAL_CURSOR,
            source_event_count: CANONICAL_EVENT_COUNT,
            subject_count: CANONICAL_SUBJECT_COUNT,
            source_event_set_digest: CANONICAL_EVENT_SET_DIGEST.to_owned(),
            interaction: "stdin-json-lines".to_owned(),
            stop_policy: "explicit-stop-or-eof-exact-teardown".to_owned(),
            live: false,
            network: false,
            credential_kind: "none".to_owned(),
            external_effects: false,
            authority_effect: "none".to_owned(),
        }
    }
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct RuntimeStatus {
    pub schema_version: String,
    pub candidate_id: String,
    pub runtime_identity: String,
    pub session_state: String,
    pub prototype_runtime_active: bool,
    pub calculated_projection_available: bool,
    pub semantic_cursor: u64,
    pub source_event_count: usize,
    pub subject_count: usize,
    pub source_event_set_digest: String,
    pub projection_sha256: String,
    pub state_survives_commands: bool,
    pub explicit_stop_required: bool,
    pub product_approved: bool,
    pub governed_runtime_activated: bool,
    pub live_execution_ready: bool,
    pub migration_performed: bool,
    pub cutover_performed: bool,
    pub external_effects: bool,
    pub authority_effect: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct RuntimeStopReceipt {
    pub schema_version: String,
    pub candidate_id: String,
    pub runtime_identity: String,
    pub session_state: String,
    pub prototype_runtime_was_active: bool,
    pub projection_sha256: String,
    pub restored_preimage_exact: bool,
    pub cleanup_verified: bool,
    pub governed_runtime_activated: bool,
    pub live_execution_ready: bool,
    pub external_effects: bool,
    pub authority_effect: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ActiveRuntimeReport {
    pub schema_version: String,
    pub candidate_id: String,
    pub runtime_identity: String,
    pub activation_observation: SandboxActivationObservation,
    pub active_status: RuntimeStatus,
    pub projection_matches_canonical_fixture: bool,
    pub repeated_status_is_stable: bool,
    pub stop: RuntimeStopReceipt,
    pub result: String,
    pub authority_effect: String,
}

impl ActiveRuntimeReport {
    pub fn canonical_json(&self) -> Result<String, ActiveRuntimeFailure> {
        serde_json::to_string(self).map_err(|error| {
            ActiveRuntimeFailure::new("ACTIVE_RUNTIME_REPORT_ENCODE_FAILED", error.to_string())
        })
    }
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct ActiveRuntimeFailure {
    pub code: String,
    pub detail: String,
}

impl ActiveRuntimeFailure {
    fn new(code: &str, detail: impl Into<String>) -> Self {
        Self {
            code: code.to_owned(),
            detail: detail.into(),
        }
    }
}

impl Display for ActiveRuntimeFailure {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(formatter, "{}: {}", self.code, self.detail)
    }
}

impl Error for ActiveRuntimeFailure {}

impl From<ExecutionFailure> for ActiveRuntimeFailure {
    fn from(failure: ExecutionFailure) -> Self {
        Self::new(&failure.code, failure.detail)
    }
}

pub struct ActiveRuntime {
    target: Option<StatefulSandboxTarget>,
    projection: ConsistentOntologyCut,
    projection_json: String,
    projection_sha256: String,
    activation_observation: SandboxActivationObservation,
}

impl ActiveRuntime {
    pub fn start(
        semantic_directory: impl AsRef<Path>,
        governance_directory: impl AsRef<Path>,
        cursor: u64,
    ) -> Result<Self, ActiveRuntimeFailure> {
        let store =
            EventStore::load(semantic_directory, governance_directory).map_err(|failure| {
                ActiveRuntimeFailure::new("ACTIVE_RUNTIME_EVENT_LOAD_FAILED", failure.to_string())
            })?;
        let projection = store.ontology_at(cursor).map_err(|failure| {
            ActiveRuntimeFailure::new("ACTIVE_RUNTIME_PROJECTION_FAILED", failure.to_string())
        })?;
        validate_exact_projection(&projection)?;
        let projection_json = machine_projection(&projection).map_err(|failure| {
            ActiveRuntimeFailure::new(
                "ACTIVE_RUNTIME_PROJECTION_ENCODE_FAILED",
                failure.to_string(),
            )
        })?;
        let projection_sha256 = digest_bytes(projection_json.as_bytes());

        let mut target = StatefulSandboxTarget::new()?;
        let activation_observation =
            SandboxActivationHarness.activate(&SandboxActivationRequest::exact(), &mut target)?;
        let projection_path = target.root().join(PROJECTION_FILE);
        fs::write(&projection_path, projection_json.as_bytes()).map_err(|error| {
            ActiveRuntimeFailure::new("ACTIVE_RUNTIME_PROJECTION_WRITE_FAILED", error.to_string())
        })?;
        if fs::read(&projection_path).ok().as_deref() != Some(projection_json.as_bytes()) {
            return Err(ActiveRuntimeFailure::new(
                "ACTIVE_RUNTIME_PROJECTION_PERSISTENCE_MISMATCH",
                projection_path.display().to_string(),
            ));
        }

        Ok(Self {
            target: Some(target),
            projection,
            projection_json,
            projection_sha256,
            activation_observation,
        })
    }

    pub fn start_canonical() -> Result<Self, ActiveRuntimeFailure> {
        let (semantic, governance) = canonical_w7_event_paths();
        Self::start(semantic, governance, CANONICAL_CURSOR)
    }

    pub fn status(&self) -> Result<RuntimeStatus, ActiveRuntimeFailure> {
        let target = self.target.as_ref().ok_or_else(|| {
            ActiveRuntimeFailure::new("ACTIVE_RUNTIME_ALREADY_STOPPED", ACTIVE_RUNTIME_IDENTITY)
        })?;
        let state = target.state()?;
        let projection_path = target.root().join(PROJECTION_FILE);
        let persisted = fs::read(&projection_path).map_err(|error| {
            ActiveRuntimeFailure::new("ACTIVE_RUNTIME_PROJECTION_READ_FAILED", error.to_string())
        })?;
        let projection_available = persisted == self.projection_json.as_bytes();
        let sandbox_active = state.runtime.runtime_state == "prototype-sandbox-active"
            && !state.runtime.live
            && self.activation_observation.sandbox_activation_observed;
        if !projection_available || !sandbox_active {
            return Err(ActiveRuntimeFailure::new(
                "ACTIVE_RUNTIME_STATE_MISMATCH",
                ACTIVE_RUNTIME_IDENTITY,
            ));
        }
        Ok(RuntimeStatus {
            schema_version: "cal.d65-local-active-runtime-status/v1".to_owned(),
            candidate_id: ACTIVE_RUNTIME_CANDIDATE_ID.to_owned(),
            runtime_identity: ACTIVE_RUNTIME_IDENTITY.to_owned(),
            session_state: "active".to_owned(),
            prototype_runtime_active: true,
            calculated_projection_available: true,
            semantic_cursor: self.projection.semantic_cursor,
            source_event_count: self.projection.source_event_count,
            subject_count: self.projection.subjects.len(),
            source_event_set_digest: self.projection.source_event_set_digest.clone(),
            projection_sha256: self.projection_sha256.clone(),
            state_survives_commands: true,
            explicit_stop_required: true,
            product_approved: false,
            governed_runtime_activated: false,
            live_execution_ready: false,
            migration_performed: false,
            cutover_performed: false,
            external_effects: false,
            authority_effect: "none".to_owned(),
        })
    }

    pub fn projection(&self) -> &ConsistentOntologyCut {
        &self.projection
    }

    pub fn projection_json(&self) -> &str {
        &self.projection_json
    }

    pub fn sandbox_root(&self) -> Result<&Path, ActiveRuntimeFailure> {
        self.target
            .as_ref()
            .map(StatefulSandboxTarget::root)
            .ok_or_else(|| {
                ActiveRuntimeFailure::new("ACTIVE_RUNTIME_ALREADY_STOPPED", ACTIVE_RUNTIME_IDENTITY)
            })
    }

    pub fn activation_observation(&self) -> &SandboxActivationObservation {
        &self.activation_observation
    }

    pub fn stop(mut self) -> Result<RuntimeStopReceipt, ActiveRuntimeFailure> {
        let target = self.target.take().ok_or_else(|| {
            ActiveRuntimeFailure::new("ACTIVE_RUNTIME_ALREADY_STOPPED", ACTIVE_RUNTIME_IDENTITY)
        })?;
        let teardown = target.teardown()?;
        Ok(RuntimeStopReceipt {
            schema_version: "cal.d65-local-active-runtime-stop/v1".to_owned(),
            candidate_id: ACTIVE_RUNTIME_CANDIDATE_ID.to_owned(),
            runtime_identity: ACTIVE_RUNTIME_IDENTITY.to_owned(),
            session_state: "stopped".to_owned(),
            prototype_runtime_was_active: true,
            projection_sha256: self.projection_sha256.clone(),
            restored_preimage_exact: teardown.restored_preimage_exact,
            cleanup_verified: teardown.cleanup_verified,
            governed_runtime_activated: false,
            live_execution_ready: false,
            external_effects: false,
            authority_effect: "none".to_owned(),
        })
    }
}

impl Drop for ActiveRuntime {
    fn drop(&mut self) {
        if let Some(target) = self.target.take() {
            let _ = target.teardown();
        }
    }
}

pub fn canonical_w7_event_paths() -> (PathBuf, PathBuf) {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../../../migration/cal-w7-ontology-product-epoch-001/fixtures/output");
    (root.join("semantic-events"), root.join("governance-events"))
}

pub fn rehearse_active_runtime() -> Result<ActiveRuntimeReport, ActiveRuntimeFailure> {
    let runtime = ActiveRuntime::start_canonical()?;
    let activation_observation = runtime.activation_observation().clone();
    let first_status = runtime.status()?;
    let second_status = runtime.status()?;
    let repeated_status_is_stable = first_status == second_status;
    let projection_matches_canonical_fixture = runtime.projection().semantic_cursor
        == CANONICAL_CURSOR
        && runtime.projection().source_event_count == CANONICAL_EVENT_COUNT
        && runtime.projection().subjects.len() == CANONICAL_SUBJECT_COUNT
        && runtime.projection().source_event_set_digest == CANONICAL_EVENT_SET_DIGEST;
    let stop = runtime.stop()?;
    let passed = first_status.prototype_runtime_active
        && first_status.calculated_projection_available
        && first_status == second_status
        && projection_matches_canonical_fixture
        && stop.restored_preimage_exact
        && stop.cleanup_verified;
    Ok(ActiveRuntimeReport {
        schema_version: "cal.d65-local-active-runtime-report/v1".to_owned(),
        candidate_id: ACTIVE_RUNTIME_CANDIDATE_ID.to_owned(),
        runtime_identity: ACTIVE_RUNTIME_IDENTITY.to_owned(),
        activation_observation,
        active_status: first_status,
        projection_matches_canonical_fixture,
        repeated_status_is_stable,
        stop,
        result: if passed { "PASS" } else { "BLOCK" }.to_owned(),
        authority_effect: "none".to_owned(),
    })
}

fn validate_exact_projection(
    projection: &ConsistentOntologyCut,
) -> Result<(), ActiveRuntimeFailure> {
    let exact = projection.semantic_cursor == CANONICAL_CURSOR
        && projection.source_event_count == CANONICAL_EVENT_COUNT
        && projection.subjects.len() == CANONICAL_SUBJECT_COUNT
        && projection.source_event_set_digest == CANONICAL_EVENT_SET_DIGEST;
    if !exact {
        return Err(ActiveRuntimeFailure::new(
            "ACTIVE_RUNTIME_CANONICAL_CORPUS_MISMATCH",
            format!(
                "cursor={}, events={}, subjects={}, digest={}",
                projection.semantic_cursor,
                projection.source_event_count,
                projection.subjects.len(),
                projection.source_event_set_digest
            ),
        ));
    }
    Ok(())
}

fn digest_bytes(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}
