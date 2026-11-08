use std::collections::BTreeMap;

use evf_production_kernel::execute::validate_profile;
use evf_production_kernel::model::*;
use evf_production_kernel::store::{StagingRun, recover_partials};
use serde_json::json;
use tempfile::tempdir;

fn reference(path: &str) -> ExactRef {
    ExactRef {
        path: path.to_owned(),
        sha256: "0".repeat(64),
        size_bytes: 0,
        location: RefLocation::Repository,
        current: true,
    }
}

fn runtime() -> RuntimeSpec {
    RuntimeSpec {
        executable_ref: reference("provider"),
        tool_refs: vec![],
        argv: vec!["--input".to_owned(), "{input}".to_owned()],
        working_directory: ".".to_owned(),
        environment: BTreeMap::new(),
        timeout_ms: 100,
        max_output_bytes: 256,
        network: "forbidden".to_owned(),
        isolation: IsolationSpec {
            mechanism: "linux-user-and-network-namespace".to_owned(),
            unshare_ref: reference("unshare"),
        },
    }
}

fn profile() -> EnforcementProfile {
    EnforcementProfile {
        schema_version: "evf.enforcement-profile/v1".to_owned(),
        profile_id: "test.profile.v1".to_owned(),
        subject: "test subject".to_owned(),
        route: Route::Executable,
        stages: STAGE_IDS
            .iter()
            .map(|stage_id| StageRequirement {
                stage_id: (*stage_id).to_owned(),
                required: true,
            })
            .collect(),
        semantic_refs: vec![reference("semantic")],
        obligation_ids: vec!["obligation.one".to_owned()],
        obligation_denominator: 1,
        binding_refs: vec![reference("binding")],
        checks: vec![CheckSpec {
            check_id: "check.one".to_owned(),
            provider_id: "provider.one".to_owned(),
            runtime: runtime(),
            input_ref: reference("positive"),
            expected_output: json!({"result": true}),
        }],
        mutations: vec![MutationSpec {
            mutant_id: "mutant.one".to_owned(),
            check_id: "check.one".to_owned(),
            input_ref: reference("mutant"),
            expected_output: json!({"result": false}),
            expected_rejection_code: "DECLARED_CAUSE".to_owned(),
        }],
        composition: CompositionSpec {
            mode: "single".to_owned(),
            provider_ids: vec!["provider.one".to_owned()],
            compare_fields: vec![],
            comparability_refs: vec![reference("comparability")],
        },
        producer: ProducerSpec {
            executable_ref: reference("producer"),
        },
        verifier: VerifierSpec {
            executable_ref: reference("verifier"),
        },
        repetitions: 2,
        claim_ceiling: "test only".to_owned(),
        authority_effect: "none".to_owned(),
    }
}

#[test]
fn complete_profile_is_valid() {
    validate_profile(&profile()).expect("complete profile should validate");
}

#[test]
fn missing_stage_is_rejected() {
    let mut profile = profile();
    profile.stages.pop();
    let error = validate_profile(&profile).expect_err("missing stage must fail");
    assert_eq!(error.code, "PROFILE_STAGE_DENOMINATOR_INVALID");
}

#[test]
fn obligation_denominator_drift_is_rejected() {
    let mut profile = profile();
    profile.obligation_denominator = 2;
    let error = validate_profile(&profile).expect_err("denominator drift must fail");
    assert_eq!(error.code, "OBLIGATION_DENOMINATOR_MISMATCH");
}

#[test]
fn duplicate_check_id_is_rejected() {
    let mut profile = profile();
    profile.checks.push(profile.checks[0].clone());
    let error = validate_profile(&profile).expect_err("duplicate check must fail");
    assert_eq!(error.code, "CHECK_ID_INVALID_OR_DUPLICATE");
}

#[test]
fn ambient_network_is_rejected() {
    let mut profile = profile();
    profile.checks[0].runtime.network = "ambient".to_owned();
    let error = validate_profile(&profile).expect_err("ambient network must fail");
    assert_eq!(error.code, "RUNTIME_CONTRACT_INVALID");
}

#[test]
fn partial_run_is_recovered_as_interrupted() {
    let directory = tempdir().unwrap();
    let staging = StagingRun::create(directory.path(), "attempt-001").unwrap();
    staging
        .write_json("PARTIAL.json", &json!({"partial": true}))
        .unwrap();
    drop(staging);

    let recovered = recover_partials(directory.path()).unwrap();
    assert_eq!(recovered.len(), 1);
    let recovery: serde_json::Value =
        serde_json::from_slice(&std::fs::read(recovered[0].join("RECOVERY.json")).unwrap())
            .unwrap();
    assert_eq!(recovery["state"], "interrupted");
    assert_eq!(recovery["authority_effect"], "none");
}

#[test]
fn active_partial_is_not_recovered() {
    let directory = tempdir().unwrap();
    let staging = StagingRun::create(directory.path(), "attempt-active").unwrap();
    staging
        .write_json("PARTIAL.json", &json!({"partial": true}))
        .unwrap();

    let recovered = recover_partials(directory.path()).unwrap();
    assert!(recovered.is_empty());
    assert!(staging.path.exists());

    drop(staging);
    let recovered = recover_partials(directory.path()).unwrap();
    assert_eq!(recovered.len(), 1);
}

#[test]
fn finalized_run_cannot_be_overwritten() {
    let directory = tempdir().unwrap();
    let staging = StagingRun::create(directory.path(), "attempt-001").unwrap();
    staging
        .write_json("EVIDENCE.json", &json!({"state": "passed"}))
        .unwrap();
    let digest = "a".repeat(64);
    staging.finalize(&digest).unwrap();

    let second = StagingRun::create(directory.path(), "attempt-001").unwrap();
    second
        .write_json("EVIDENCE.json", &json!({"state": "failed"}))
        .unwrap();
    let error = second.finalize(&digest).expect_err("overwrite must fail");
    assert_eq!(error.code, "RUN_STORE_FINAL_EXISTS");
}
