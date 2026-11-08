use serde_json::Value;
use std::path::PathBuf;
use std::process::Command;
use tempfile::tempdir;

fn run(arguments: &[&str]) -> Value {
    let output = Command::new(env!("CARGO_BIN_EXE_cal-ontology-graph-read-model"))
        .args(arguments)
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    serde_json::from_slice(&output.stdout).unwrap()
}

#[test]
fn summary_is_runnable_and_non_authoritative() {
    let output = run(&["summary"]);
    assert_eq!(output["canonical_replay_source"], false);
    assert_eq!(output["authority_effect"], "none");
    assert_eq!(output["result"]["semantic_cursor"], 47);
    assert_eq!(output["result"]["node_count"], 23);
    assert_eq!(output["result"]["relation_count"], 24);
}

#[test]
fn outgoing_and_challenge_commands_return_real_w7_data() {
    let outgoing = run(&["outgoing", "CA2-PRODUCT-ONTOLOGY", "includes_capability"]);
    assert_eq!(outgoing["result"].as_array().unwrap().len(), 5);
    let challenge = run(&["challenge", "CA2-PRODUCT-ONTOLOGY"]);
    assert_eq!(
        challenge["result"]["valid_challenge_modes"]
            .as_array()
            .unwrap()
            .len(),
        3
    );
}

#[test]
fn unknown_command_blocks_without_mutation() {
    let output = Command::new(env!("CARGO_BIN_EXE_cal-ontology-graph-read-model"))
        .arg("mutate")
        .output()
        .unwrap();
    assert_eq!(output.status.code(), Some(2));
    let error: Value = serde_json::from_slice(&output.stderr).unwrap();
    assert_eq!(error["result"], "BLOCK");
    assert_eq!(error["code"], "COMMAND_UNKNOWN");
}

#[test]
fn recover_files_runs_in_a_fresh_process_and_binds_the_w7_expectation() {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let fixture = root.join("../../../migration/cal-w7-ontology-product-epoch-001/fixtures/output");
    let output = run(&[
        "recover-files",
        fixture.join("semantic-events").to_str().unwrap(),
        fixture.join("governance-events").to_str().unwrap(),
        root.join("recovery-expectation-w7.json").to_str().unwrap(),
    ]);
    assert_eq!(output["command"], "recover-files");
    assert_eq!(
        output["result"]["recovery_strategy"],
        "full_rebuild_from_canonical_event_files"
    );
    assert_eq!(output["result"]["semantic_cursor"], 47);
    assert_eq!(
        output["result"]["rebuilt_index_digest"],
        "7887a81f39664e8b38cbd00201970625741192a80fed889e51d8342a05797fb5"
    );
    assert_eq!(output["result"]["checkpoint_used"], false);
    assert!(output["result"]["event_store_load_ns"].as_u64().unwrap() > 0);
    assert!(output["result"]["graph_rebuild_ns"].as_u64().unwrap() > 0);
}

#[test]
fn recover_files_rejects_missing_event_directories() {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let output = Command::new(env!("CARGO_BIN_EXE_cal-ontology-graph-read-model"))
        .args([
            "recover-files",
            root.join("missing-semantic-events").to_str().unwrap(),
            root.join("missing-governance-events").to_str().unwrap(),
            root.join("recovery-expectation-w7.json").to_str().unwrap(),
        ])
        .output()
        .unwrap();
    assert_eq!(output.status.code(), Some(2));
    let error: Value = serde_json::from_slice(&output.stderr).unwrap();
    assert_eq!(error["result"], "BLOCK");
    assert_ne!(error["code"], Value::Null);
}

#[test]
fn checkpoint_cli_round_trip_is_disposable_and_tail_equivalent() {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let fixture = root.join("../../../migration/cal-w7-ontology-product-epoch-001/fixtures/output");
    let temporary = tempdir().unwrap();
    let checkpoint = temporary.path().join("checkpoint.json");

    let created = run(&[
        "checkpoint-create",
        fixture.join("semantic-events").to_str().unwrap(),
        fixture.join("governance-events").to_str().unwrap(),
        "23",
        "23",
        checkpoint.to_str().unwrap(),
    ]);
    assert_eq!(created["command"], "checkpoint-create");
    assert_eq!(
        created["result"]["checkpoint_kind"],
        "disposable-calculated-read-model-cache"
    );
    assert_eq!(created["result"]["canonical_replay_source"], false);
    assert_eq!(created["result"]["authority_effect"], "none");
    assert_eq!(created["result"]["semantic_cursor"], 23);

    let recovered = run(&[
        "recover-checkpoint-tail",
        checkpoint.to_str().unwrap(),
        fixture.join("semantic-events").to_str().unwrap(),
        fixture.join("governance-events").to_str().unwrap(),
        root.join("recovery-expectation-w7.json").to_str().unwrap(),
        "47",
    ]);
    assert_eq!(recovered["command"], "recover-checkpoint-tail");
    assert_eq!(
        recovered["result"]["recovery_strategy"],
        "verified_disposable_checkpoint_plus_canonical_event_tail"
    );
    assert_eq!(recovered["result"]["checkpoint_used"], true);
    assert_eq!(recovered["result"]["canonical_replay_source"], false);
    assert_eq!(recovered["result"]["exact_index_digest_match"], true);
    assert_eq!(recovered["result"]["semantic_cursor"], 47);
    assert_eq!(recovered["result"]["loaded_semantic_tail_event_count"], 24);
    assert_eq!(
        recovered["result"]["loaded_governance_tail_event_count"],
        24
    );
}

#[test]
fn checkpoint_create_refuses_to_replace_an_existing_file() {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let fixture = root.join("../../../migration/cal-w7-ontology-product-epoch-001/fixtures/output");
    let temporary = tempdir().unwrap();
    let checkpoint = temporary.path().join("checkpoint.json");
    std::fs::write(&checkpoint, b"preserve-me").unwrap();

    let output = Command::new(env!("CARGO_BIN_EXE_cal-ontology-graph-read-model"))
        .args([
            "checkpoint-create",
            fixture.join("semantic-events").to_str().unwrap(),
            fixture.join("governance-events").to_str().unwrap(),
            "23",
            "23",
            checkpoint.to_str().unwrap(),
        ])
        .output()
        .unwrap();
    assert_eq!(output.status.code(), Some(2));
    let error: Value = serde_json::from_slice(&output.stderr).unwrap();
    assert_eq!(error["result"], "BLOCK");
    assert_eq!(error["code"], "CHECKPOINT_CREATE_FAILED");
    assert_eq!(std::fs::read(checkpoint).unwrap(), b"preserve-me");
}

#[test]
fn atomic_checkpoint_cli_survives_both_injected_interruption_boundaries() {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let fixture = root.join("../../../migration/cal-w7-ontology-product-epoch-001/fixtures/output");
    let temporary = tempdir().unwrap();
    let checkpoint = temporary.path().join("checkpoint.json");
    let binary = env!("CARGO_BIN_EXE_cal-ontology-graph-read-model");
    let base_arguments = |semantic_cursor: &str, governance_cursor: &str| {
        vec![
            "checkpoint-write-atomic".to_owned(),
            fixture.join("semantic-events").display().to_string(),
            fixture.join("governance-events").display().to_string(),
            semantic_cursor.to_owned(),
            governance_cursor.to_owned(),
            checkpoint.display().to_string(),
        ]
    };

    let created = Command::new(binary)
        .args(base_arguments("15", "15"))
        .output()
        .unwrap();
    assert!(created.status.success());
    let created_output: Value = serde_json::from_slice(&created.stdout).unwrap();
    assert_eq!(created_output["result"]["disposition"], "created");
    assert_eq!(created_output["result"]["parent_directory_synced"], true);
    let checkpoint_15 = std::fs::read(&checkpoint).unwrap();

    let staged = Command::new(binary)
        .env("CAL_CHECKPOINT_ATOMIC_FAULT", "after-stage-sync")
        .args(base_arguments("23", "23"))
        .output()
        .unwrap();
    assert_eq!(staged.status.code(), Some(2));
    let staged_error: Value = serde_json::from_slice(&staged.stderr).unwrap();
    assert_eq!(
        staged_error["code"],
        "CHECKPOINT_FAULT_INJECTED_AFTER_STAGE_SYNC"
    );
    assert_eq!(std::fs::read(&checkpoint).unwrap(), checkpoint_15);

    let recovered_old = run(&[
        "recover-checkpoint-tail",
        checkpoint.to_str().unwrap(),
        fixture.join("semantic-events").to_str().unwrap(),
        fixture.join("governance-events").to_str().unwrap(),
        root.join("recovery-expectation-w7.json").to_str().unwrap(),
        "47",
    ]);
    assert_eq!(recovered_old["result"]["exact_index_digest_match"], true);
    assert_eq!(
        recovered_old["result"]["loaded_semantic_tail_event_count"],
        32
    );

    let replaced = Command::new(binary)
        .args(base_arguments("23", "23"))
        .output()
        .unwrap();
    assert!(replaced.status.success());
    let replaced_output: Value = serde_json::from_slice(&replaced.stdout).unwrap();
    assert_eq!(replaced_output["result"]["disposition"], "replaced");

    let renamed = Command::new(binary)
        .env(
            "CAL_CHECKPOINT_ATOMIC_FAULT",
            "after-rename-before-directory-sync",
        )
        .args(base_arguments("35", "35"))
        .output()
        .unwrap();
    assert_eq!(renamed.status.code(), Some(2));
    let renamed_error: Value = serde_json::from_slice(&renamed.stderr).unwrap();
    assert_eq!(
        renamed_error["code"],
        "CHECKPOINT_FAULT_INJECTED_AFTER_RENAME"
    );

    let recovered_new = run(&[
        "recover-checkpoint-tail",
        checkpoint.to_str().unwrap(),
        fixture.join("semantic-events").to_str().unwrap(),
        fixture.join("governance-events").to_str().unwrap(),
        root.join("recovery-expectation-w7.json").to_str().unwrap(),
        "47",
    ]);
    assert_eq!(recovered_new["result"]["exact_index_digest_match"], true);
    assert_eq!(
        recovered_new["result"]["loaded_semantic_tail_event_count"],
        12
    );

    let unchanged = Command::new(binary)
        .args(base_arguments("35", "35"))
        .output()
        .unwrap();
    assert!(unchanged.status.success());
    let unchanged_output: Value = serde_json::from_slice(&unchanged.stdout).unwrap();
    assert_eq!(unchanged_output["result"]["disposition"], "unchanged");
    let checkpoint_35 = std::fs::read(&checkpoint).unwrap();

    let stale = Command::new(binary)
        .args(base_arguments("23", "23"))
        .output()
        .unwrap();
    assert_eq!(stale.status.code(), Some(2));
    let stale_error: Value = serde_json::from_slice(&stale.stderr).unwrap();
    assert_eq!(stale_error["code"], "CHECKPOINT_REPLACEMENT_REGRESSION");
    assert_eq!(std::fs::read(checkpoint).unwrap(), checkpoint_35);
}
