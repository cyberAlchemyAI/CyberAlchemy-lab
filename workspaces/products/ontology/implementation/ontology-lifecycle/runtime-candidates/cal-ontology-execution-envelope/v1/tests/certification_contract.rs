use cal_ontology_execution_envelope::certification::{
    CertificationFixture, CertificationHarness, CertificationScenario, CertificationVector,
    REQUIRED_VECTOR_IDS, validate_vector_set,
};
use cal_ontology_execution_envelope::{
    EventCut, ExecutionFailure, ExecutionTargetAdapter, PrototypeTargetBinding,
};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::cell::RefCell;

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
struct VectorDocument {
    schema_version: String,
    vectors: Vec<CertificationVector>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
struct IndependentState {
    active_cut: EventCut,
    generation: String,
    runtime_state: String,
    traffic_target: String,
    staged_cut: Option<EventCut>,
    live: bool,
    external_effects: bool,
}

impl IndependentState {
    fn source() -> Self {
        Self {
            active_cut: EventCut::exact_source(),
            generation: "epoch-001".to_owned(),
            runtime_state: "inactive".to_owned(),
            traffic_target: "epoch-001".to_owned(),
            staged_cut: None,
            live: false,
            external_effects: false,
        }
    }
}

struct IndependentAdapter {
    state: IndependentState,
    binding: PrototypeTargetBinding,
    failure: Option<CertificationScenario>,
    calls: RefCell<Vec<String>>,
}

impl IndependentAdapter {
    fn exact() -> Self {
        Self {
            state: IndependentState::source(),
            binding: PrototypeTargetBinding::exact(),
            failure: None,
            calls: RefCell::new(Vec::new()),
        }
    }

    fn record(&self, call: &str) {
        self.calls.borrow_mut().push(call.to_owned());
    }

    fn fail_if(&self, scenario: CertificationScenario) -> Result<(), ExecutionFailure> {
        if self.failure == Some(scenario) {
            return Err(ExecutionFailure::new(
                "INJECTED_CERTIFICATION_FAILURE",
                format!("{scenario:?}"),
            ));
        }
        Ok(())
    }
}

impl ExecutionTargetAdapter for IndependentAdapter {
    type Snapshot = IndependentState;

    fn binding(&self) -> PrototypeTargetBinding {
        self.binding.clone()
    }

    fn capture_preimage(&self) -> Self::Snapshot {
        self.record("capture-preimage");
        self.state.clone()
    }

    fn verify_preimage(&self, expected: &EventCut) -> Result<(), ExecutionFailure> {
        self.record("preflight");
        if &self.state.active_cut != expected || self.state != IndependentState::source() {
            return Err(ExecutionFailure::new(
                "TARGET_PREIMAGE_MISMATCH",
                "independent fixture",
            ));
        }
        Ok(())
    }

    fn stage(&mut self, candidate: &EventCut) -> Result<(), ExecutionFailure> {
        self.record("stage");
        self.fail_if(CertificationScenario::StageFailure)?;
        self.state.staged_cut = Some(candidate.clone());
        Ok(())
    }

    fn activate(&mut self) -> Result<(), ExecutionFailure> {
        self.record("activate");
        self.fail_if(CertificationScenario::ActivateFailure)?;
        self.state.generation = "epoch-002".to_owned();
        self.state.runtime_state = "prototype-active".to_owned();
        Ok(())
    }

    fn migrate(&mut self) -> Result<(), ExecutionFailure> {
        self.record("migrate");
        self.fail_if(CertificationScenario::MigrateFailure)?;
        self.state.active_cut =
            self.state.staged_cut.clone().ok_or_else(|| {
                ExecutionFailure::new("STAGED_CUT_MISSING", "independent fixture")
            })?;
        Ok(())
    }

    fn verify_target(&self, expected: &EventCut) -> Result<(), ExecutionFailure> {
        self.record("verify-target");
        self.fail_if(CertificationScenario::VerifyTargetFailure)?;
        if &self.state.active_cut != expected {
            return Err(ExecutionFailure::new(
                "TARGET_CUT_MISMATCH",
                "independent fixture",
            ));
        }
        Ok(())
    }

    fn cutover(&mut self) -> Result<(), ExecutionFailure> {
        self.record("cutover");
        self.fail_if(CertificationScenario::CutoverFailure)?;
        self.state.traffic_target = "epoch-002".to_owned();
        Ok(())
    }

    fn verify_postimage(&self, expected: &EventCut) -> Result<(), ExecutionFailure> {
        self.record("verify-postimage");
        self.fail_if(CertificationScenario::VerifyPostimageFailure)?;
        if &self.state.active_cut != expected
            || self.state.generation != "epoch-002"
            || self.state.runtime_state != "prototype-active"
            || self.state.traffic_target != "epoch-002"
            || self.state.live
            || self.state.external_effects
        {
            return Err(ExecutionFailure::new(
                "POSTIMAGE_MISMATCH",
                "independent fixture",
            ));
        }
        Ok(())
    }

    fn restore(&mut self, preimage: &Self::Snapshot) -> Result<(), ExecutionFailure> {
        self.record("rollback");
        self.fail_if(CertificationScenario::RollbackFailure)?;
        self.state = preimage.clone();
        Ok(())
    }

    fn verify_rollback(&self, preimage: &Self::Snapshot) -> Result<(), ExecutionFailure> {
        self.record("verify-rollback");
        self.fail_if(CertificationScenario::VerifyRollbackFailure)?;
        if &self.state != preimage {
            return Err(ExecutionFailure::new(
                "ROLLBACK_PREIMAGE_MISMATCH",
                "independent fixture",
            ));
        }
        Ok(())
    }

    fn emergency_restore(&mut self, preimage: &Self::Snapshot) {
        self.record("emergency-restore");
        self.state = preimage.clone();
    }
}

#[derive(Clone, Copy)]
struct IndependentFixture;

impl CertificationFixture for IndependentFixture {
    type Adapter = IndependentAdapter;

    fn fixture_id(&self) -> &str {
        "cal.certification.independent-disposable-adapter/v1"
    }

    fn build(&self, scenario: CertificationScenario) -> Self::Adapter {
        let mut adapter = IndependentAdapter::exact();
        match scenario {
            CertificationScenario::BindingIdentity => {
                adapter.binding.identity = "cal.unreviewed.adapter".to_owned();
            }
            CertificationScenario::LiveBinding => adapter.binding.live = true,
            CertificationScenario::CredentialBinding => {
                adapter.binding.credential_kind = "token".to_owned();
            }
            CertificationScenario::PreimageDrift => {
                adapter.state.runtime_state = "drifted".to_owned();
            }
            CertificationScenario::StageFailure
            | CertificationScenario::ActivateFailure
            | CertificationScenario::MigrateFailure
            | CertificationScenario::VerifyTargetFailure
            | CertificationScenario::CutoverFailure
            | CertificationScenario::VerifyPostimageFailure
            | CertificationScenario::RollbackFailure
            | CertificationScenario::VerifyRollbackFailure => {
                adapter.failure = Some(scenario);
            }
            CertificationScenario::Baseline
            | CertificationScenario::CallOrder
            | CertificationScenario::ReportDeterminism
            | CertificationScenario::IndependentFixture
            | CertificationScenario::VectorOmission
            | CertificationScenario::VectorMutation => {}
        }
        adapter
    }

    fn state_digest(&self, adapter: &Self::Adapter) -> String {
        let bytes = serde_json::to_vec(&adapter.state).unwrap();
        format!("{:x}", Sha256::digest(bytes))
    }

    fn observed_call_order(&self, adapter: &Self::Adapter) -> Vec<String> {
        adapter.calls.borrow().clone()
    }

    fn external_effects(&self, adapter: &Self::Adapter) -> bool {
        adapter.state.external_effects
    }

    fn independently_authored(&self) -> bool {
        true
    }
}

fn vector_document() -> VectorDocument {
    serde_json::from_str(include_str!("fixtures/certification-vectors.json")).unwrap()
}

fn report() -> cal_ontology_execution_envelope::certification::CertificationReport {
    CertificationHarness
        .certify_twice(&IndependentFixture, &vector_document().vectors)
        .unwrap()
}

#[test]
fn vector_fixture_matches_schema_shape() {
    let document = vector_document();
    let schema: serde_json::Value =
        serde_json::from_str(include_str!("../schemas/certification-vectors.schema.json")).unwrap();
    assert_eq!(
        document.schema_version,
        schema["properties"]["schema_version"]["const"]
    );
    assert_eq!(document.vectors.len(), 18);
    validate_vector_set(&document.vectors).unwrap();
}

#[test]
fn exact_certification_report_passes_all_vectors() {
    let report = report();
    assert_eq!(report.body.result, "PASS");
    assert_eq!(report.body.passed_vectors, 18);
    assert_eq!(report.body.total_vectors, 18);
    assert_eq!(report.body.outcomes.len(), 18);
    assert!(!report.body.external_effects);
    assert_eq!(report.body.authority_effect, "none");
    assert_eq!(report.body.preimage_digest, report.body.final_state_digest);
    assert_eq!(report.report_digest.len(), 64);
}

#[test]
fn certification_report_is_byte_deterministic() {
    let first = report().canonical_json().unwrap();
    let second = report().canonical_json().unwrap();
    assert_eq!(first, second);
    println!("CERTIFICATION_REPORT_JSON={first}");
}

#[test]
fn omitted_vector_is_blocked() {
    let mut vectors = vector_document().vectors;
    vectors.remove(6);
    let failure = CertificationHarness
        .certify_twice(&IndependentFixture, &vectors)
        .unwrap_err();
    assert_eq!(failure.code, "CERTIFICATION_VECTOR_SET_MISMATCH");
}

#[test]
fn reordered_vector_is_blocked() {
    let mut vectors = vector_document().vectors;
    vectors.swap(0, 1);
    let failure = CertificationHarness
        .certify_twice(&IndependentFixture, &vectors)
        .unwrap_err();
    assert_eq!(failure.code, "CERTIFICATION_VECTOR_SET_MISMATCH");
}

#[test]
fn duplicated_vector_is_blocked() {
    let mut vectors = vector_document().vectors;
    vectors[8] = vectors[7].clone();
    let failure = CertificationHarness
        .certify_twice(&IndependentFixture, &vectors)
        .unwrap_err();
    assert_eq!(failure.code, "CERTIFICATION_VECTOR_SET_MISMATCH");
}

#[test]
fn expected_result_substitution_is_blocked() {
    let mut vectors = vector_document().vectors;
    vectors[5].expected_failure_code = Some("WRONG_FAILURE".to_owned());
    let failure = CertificationHarness
        .certify_twice(&IndependentFixture, &vectors)
        .unwrap_err();
    assert_eq!(failure.code, "CERTIFICATION_VECTOR_SET_MISMATCH");
}

#[test]
fn fixture_source_is_independent() {
    let source = include_str!("certification_contract.rs");
    let forbidden = ["InMemory", "Target"].concat();
    assert!(!source.contains(&forbidden));
    assert_eq!(REQUIRED_VECTOR_IDS.len(), 18);
    assert!(IndependentFixture.independently_authored());
}
