use cal_ontology_graph_read_model::{
    AtomicCheckpointFault, GraphReadModel, RecoveryExpectation, RecoveryReceipt, SubjectKey,
    decode_checkpoint, encode_checkpoint, write_checkpoint_atomically,
};
use cal_ontology_lifecycle::{EventStore, EventTail};
use serde::Serialize;
use serde_json::{Value, json};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::process::ExitCode;
use std::time::Instant;
use std::{env, fs};

const ONTOLOGY_ID: &str = "cav2.ontology-product";

#[derive(Serialize)]
struct Output<T: Serialize> {
    schema_version: &'static str,
    canonical_replay_source: bool,
    authority_effect: &'static str,
    command: String,
    result: T,
}

#[derive(Serialize)]
struct FileRecoveryResult {
    #[serde(flatten)]
    receipt: RecoveryReceipt,
    event_store_load_ns: u128,
    graph_rebuild_ns: u128,
}

#[derive(Serialize)]
struct CheckpointCreationResult {
    checkpoint_path: String,
    checkpoint_bytes: usize,
    body_digest_sha256: String,
    semantic_cursor: u64,
    governance_cursor: u64,
    source_event_count: usize,
    source_event_set_digest: String,
    expected_index_digest: String,
    checkpoint_kind: String,
    canonical_replay_source: bool,
    authority_effect: String,
}

#[derive(Serialize)]
struct CheckpointTailRecoveryResult {
    #[serde(flatten)]
    receipt: RecoveryReceipt,
    checkpoint_read_decode_ns: u128,
    canonical_tail_load_ns: u128,
    graph_rebuild_ns: u128,
    checkpoint_body_digest_sha256: String,
    checkpoint_semantic_cursor: u64,
    checkpoint_governance_cursor: u64,
    loaded_semantic_tail_event_count: usize,
    loaded_governance_tail_event_count: usize,
}

fn main() -> ExitCode {
    match run(env::args().skip(1).collect()) {
        Ok(value) => {
            println!(
                "{}",
                serde_json::to_string_pretty(&value).expect("serializable output")
            );
            ExitCode::SUCCESS
        }
        Err((code, detail)) => {
            eprintln!(
                "{}",
                serde_json::to_string(&json!({"result":"BLOCK", "code":code, "detail":detail}))
                    .expect("serializable error")
            );
            ExitCode::from(2)
        }
    }
}

fn run(arguments: Vec<String>) -> Result<Output<Value>, (String, String)> {
    let command = arguments.first().map(String::as_str).unwrap_or("summary");
    if command == "recover-files" {
        return recover_files(&arguments);
    }
    if command == "checkpoint-create" {
        return checkpoint_create(&arguments);
    }
    if command == "checkpoint-write-atomic" {
        return checkpoint_write_atomic(&arguments);
    }
    if command == "recover-checkpoint-tail" {
        return recover_checkpoint_tail(&arguments);
    }
    let (semantic, governance) = fixture_paths();
    let store = EventStore::load(&semantic, &governance)
        .map_err(|failure| (failure.code, failure.detail))?;
    let cursor = store
        .semantic_events()
        .last()
        .map(|loaded| loaded.event.semantic_cursor)
        .ok_or_else(|| {
            (
                "EVENT_STORE_EMPTY".to_owned(),
                semantic.display().to_string(),
            )
        })?;
    let model = GraphReadModel::rebuild(&store, cursor)
        .map_err(|failure| (failure.code, failure.detail))?;
    let result = match command {
        "summary" => serde_json::to_value(model.metadata()),
        "node" => {
            let subject_id = required(&arguments, 1, "node <subject-id>")?;
            serde_json::to_value(
                model
                    .subject(&SubjectKey::new(ONTOLOGY_ID, subject_id))
                    .ok_or_else(|| ("SUBJECT_NOT_FOUND".to_owned(), subject_id.to_owned()))?,
            )
        }
        "outgoing" => {
            let subject_id = required(&arguments, 1, "outgoing <subject-id> <relation-type>")?;
            let relation_type = required(&arguments, 2, "outgoing <subject-id> <relation-type>")?;
            serde_json::to_value(
                model.outgoing_matches(&SubjectKey::new(ONTOLOGY_ID, subject_id), relation_type),
            )
        }
        "incoming" => {
            let subject_id = required(&arguments, 1, "incoming <subject-id> <relation-type>")?;
            let relation_type = required(&arguments, 2, "incoming <subject-id> <relation-type>")?;
            serde_json::to_value(
                model.incoming_matches(&SubjectKey::new(ONTOLOGY_ID, subject_id), relation_type),
            )
        }
        "traverse" => {
            let subject_id = required(&arguments, 1, "traverse <subject-id> <type,type,...>")?;
            let path = required(&arguments, 2, "traverse <subject-id> <type,type,...>")?
                .split(',')
                .filter(|value| !value.is_empty())
                .map(str::to_owned)
                .collect::<Vec<_>>();
            if path.is_empty() {
                return Err(("RELATION_PATH_EMPTY".to_owned(), arguments[2].clone()));
            }
            serde_json::to_value(model.traverse(&SubjectKey::new(ONTOLOGY_ID, subject_id), &path))
        }
        "type" => {
            let type_ref = required(&arguments, 1, "type <type-ref>")?;
            serde_json::to_value(model.subjects_by_type(ONTOLOGY_ID, type_ref))
        }
        "property" => {
            let name = required(&arguments, 1, "property <name> <json-value>")?;
            let raw_value = required(&arguments, 2, "property <name> <json-value>")?;
            let value = serde_json::from_str(raw_value)
                .map_err(|error| ("PROPERTY_VALUE_INVALID_JSON".to_owned(), error.to_string()))?;
            serde_json::to_value(
                model
                    .subjects_by_property(ONTOLOGY_ID, name, &value)
                    .map_err(|failure| (failure.code, failure.detail))?,
            )
        }
        "context" => {
            let context_id = required(&arguments, 1, "context <context-id>")?;
            serde_json::to_value(model.context_members(ONTOLOGY_ID, context_id))
        }
        "challenge" => {
            let subject_id = required(&arguments, 1, "challenge <subject-id>")?;
            serde_json::to_value(
                model
                    .challenge_contract(&SubjectKey::new(ONTOLOGY_ID, subject_id))
                    .ok_or_else(|| {
                        (
                            "CHALLENGE_CONTRACT_NOT_FOUND".to_owned(),
                            subject_id.to_owned(),
                        )
                    })?,
            )
        }
        _ => {
            return Err((
                "COMMAND_UNKNOWN".to_owned(),
                "expected summary|node|outgoing|incoming|traverse|type|property|context|challenge|recover-files|checkpoint-create|checkpoint-write-atomic|recover-checkpoint-tail"
                    .to_owned(),
            ));
        }
    }
    .map_err(|error| ("OUTPUT_SERIALIZATION_FAILED".to_owned(), error.to_string()))?;

    Ok(Output {
        schema_version: "cal-ontology-graph-query-output/v1-prototype",
        canonical_replay_source: false,
        authority_effect: "none",
        command: command.to_owned(),
        result,
    })
}

fn checkpoint_write_atomic(arguments: &[String]) -> Result<Output<Value>, (String, String)> {
    let usage = "checkpoint-write-atomic <semantic-events-dir> <governance-events-dir> <semantic-cursor> <governance-cursor> <checkpoint-json>";
    let semantic = PathBuf::from(required(arguments, 1, usage)?);
    let governance = PathBuf::from(required(arguments, 2, usage)?);
    let semantic_cursor = parse_cursor(required(arguments, 3, usage)?, "semantic")?;
    let governance_cursor = parse_cursor(required(arguments, 4, usage)?, "governance")?;
    let checkpoint_path = PathBuf::from(required(arguments, 5, usage)?);
    let fault = match env::var("CAL_CHECKPOINT_ATOMIC_FAULT") {
        Err(env::VarError::NotPresent) => AtomicCheckpointFault::None,
        Ok(value) if value == "after-stage-sync" => AtomicCheckpointFault::AfterStageSync,
        Ok(value) if value == "after-rename-before-directory-sync" => {
            AtomicCheckpointFault::AfterRenameBeforeDirectorySync
        }
        Ok(value) => {
            return Err((
                "CHECKPOINT_FAULT_INVALID".to_owned(),
                format!("CAL_CHECKPOINT_ATOMIC_FAULT={value}"),
            ));
        }
        Err(error) => {
            return Err(("CHECKPOINT_FAULT_INVALID".to_owned(), error.to_string()));
        }
    };
    let terminate_after_fault = match env::var("CAL_CHECKPOINT_ATOMIC_TERMINATE") {
        Err(env::VarError::NotPresent) => false,
        Ok(value) if value == "exit-75" => true,
        Ok(value) => {
            return Err((
                "CHECKPOINT_FAULT_TERMINATION_INVALID".to_owned(),
                format!("CAL_CHECKPOINT_ATOMIC_TERMINATE={value}"),
            ));
        }
        Err(error) => {
            return Err((
                "CHECKPOINT_FAULT_TERMINATION_INVALID".to_owned(),
                error.to_string(),
            ));
        }
    };
    let store = EventStore::load(&semantic, &governance)
        .map_err(|failure| (failure.code, failure.detail))?;
    let checkpoint = GraphReadModel::create_checkpoint(&store, semantic_cursor, governance_cursor)
        .map_err(|failure| (failure.code, failure.detail))?;
    let receipt = match write_checkpoint_atomically(&checkpoint_path, &checkpoint, fault) {
        Ok(receipt) => receipt,
        Err(failure)
            if terminate_after_fault
                && matches!(
                    failure.code.as_str(),
                    "CHECKPOINT_FAULT_INJECTED_AFTER_STAGE_SYNC"
                        | "CHECKPOINT_FAULT_INJECTED_AFTER_RENAME"
                ) =>
        {
            std::process::exit(75)
        }
        Err(failure) => return Err((failure.code, failure.detail)),
    };
    Ok(Output {
        schema_version: "cal-ontology-graph-query-output/v1-prototype",
        canonical_replay_source: false,
        authority_effect: "none",
        command: "checkpoint-write-atomic".to_owned(),
        result: serde_json::to_value(receipt)
            .map_err(|error| ("OUTPUT_SERIALIZATION_FAILED".to_owned(), error.to_string()))?,
    })
}

fn checkpoint_create(arguments: &[String]) -> Result<Output<Value>, (String, String)> {
    let usage = "checkpoint-create <semantic-events-dir> <governance-events-dir> <semantic-cursor> <governance-cursor> <checkpoint-json>";
    let semantic = PathBuf::from(required(arguments, 1, usage)?);
    let governance = PathBuf::from(required(arguments, 2, usage)?);
    let semantic_cursor = parse_cursor(required(arguments, 3, usage)?, "semantic")?;
    let governance_cursor = parse_cursor(required(arguments, 4, usage)?, "governance")?;
    let checkpoint_path = PathBuf::from(required(arguments, 5, usage)?);

    let store = EventStore::load(&semantic, &governance)
        .map_err(|failure| (failure.code, failure.detail))?;
    let checkpoint = GraphReadModel::create_checkpoint(&store, semantic_cursor, governance_cursor)
        .map_err(|failure| (failure.code, failure.detail))?;
    let encoded =
        encode_checkpoint(&checkpoint).map_err(|failure| (failure.code, failure.detail))?;
    let mut target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&checkpoint_path)
        .map_err(|error| {
            (
                "CHECKPOINT_CREATE_FAILED".to_owned(),
                format!("{}: {error}", checkpoint_path.display()),
            )
        })?;
    target.write_all(encoded.as_bytes()).map_err(|error| {
        (
            "CHECKPOINT_WRITE_FAILED".to_owned(),
            format!("{}: {error}", checkpoint_path.display()),
        )
    })?;
    target.sync_all().map_err(|error| {
        (
            "CHECKPOINT_SYNC_FAILED".to_owned(),
            format!("{}: {error}", checkpoint_path.display()),
        )
    })?;

    let result = CheckpointCreationResult {
        checkpoint_path: checkpoint_path.display().to_string(),
        checkpoint_bytes: encoded.len(),
        body_digest_sha256: checkpoint.body_digest_sha256,
        semantic_cursor: checkpoint.body.tail_boundary.semantic_cursor,
        governance_cursor: checkpoint.body.tail_boundary.governance_cursor,
        source_event_count: checkpoint.body.base_expectation.source_event_count,
        source_event_set_digest: checkpoint.body.base_expectation.source_event_set_digest,
        expected_index_digest: checkpoint.body.base_expectation.expected_index_digest,
        checkpoint_kind: checkpoint.checkpoint_kind,
        canonical_replay_source: checkpoint.canonical_replay_source,
        authority_effect: checkpoint.authority_effect,
    };
    Ok(Output {
        schema_version: "cal-ontology-graph-query-output/v1-prototype",
        canonical_replay_source: false,
        authority_effect: "none",
        command: "checkpoint-create".to_owned(),
        result: serde_json::to_value(result)
            .map_err(|error| ("OUTPUT_SERIALIZATION_FAILED".to_owned(), error.to_string()))?,
    })
}

fn recover_checkpoint_tail(arguments: &[String]) -> Result<Output<Value>, (String, String)> {
    let usage = "recover-checkpoint-tail <checkpoint-json> <semantic-events-dir> <governance-events-dir> <expectation-json> <target-governance-cursor>";
    let checkpoint_path = PathBuf::from(required(arguments, 1, usage)?);
    let semantic = PathBuf::from(required(arguments, 2, usage)?);
    let governance = PathBuf::from(required(arguments, 3, usage)?);
    let expectation_path = PathBuf::from(required(arguments, 4, usage)?);
    let target_governance_cursor = parse_cursor(required(arguments, 5, usage)?, "governance")?;

    let checkpoint_started = Instant::now();
    let checkpoint_bytes = fs::read(&checkpoint_path).map_err(|error| {
        (
            "CHECKPOINT_READ_FAILED".to_owned(),
            format!("{}: {error}", checkpoint_path.display()),
        )
    })?;
    let checkpoint =
        decode_checkpoint(&checkpoint_bytes).map_err(|failure| (failure.code, failure.detail))?;
    let checkpoint_read_decode_ns = checkpoint_started.elapsed().as_nanos();
    let expectation: RecoveryExpectation =
        serde_json::from_slice(&fs::read(&expectation_path).map_err(|error| {
            (
                "RECOVERY_EXPECTATION_READ_FAILED".to_owned(),
                format!("{}: {error}", expectation_path.display()),
            )
        })?)
        .map_err(|error| {
            (
                "RECOVERY_EXPECTATION_INVALID".to_owned(),
                format!("{}: {error}", expectation_path.display()),
            )
        })?;

    let tail_started = Instant::now();
    let tail = EventTail::load(
        &semantic,
        &governance,
        checkpoint.body.tail_boundary.clone(),
        expectation.semantic_cursor,
        target_governance_cursor,
    )
    .map_err(|failure| (failure.code, failure.detail))?;
    let canonical_tail_load_ns = tail_started.elapsed().as_nanos();
    let loaded_semantic_tail_event_count = tail.semantic_events().len();
    let loaded_governance_tail_event_count = tail.governance_events().len();
    let rebuild_started = Instant::now();
    let (_, receipt) =
        GraphReadModel::recover_from_checkpoint_and_tail(&checkpoint, &tail, &expectation)
            .map_err(|failure| (failure.code, failure.detail))?;
    let graph_rebuild_ns = rebuild_started.elapsed().as_nanos();
    let result = CheckpointTailRecoveryResult {
        receipt,
        checkpoint_read_decode_ns,
        canonical_tail_load_ns,
        graph_rebuild_ns,
        checkpoint_body_digest_sha256: checkpoint.body_digest_sha256,
        checkpoint_semantic_cursor: checkpoint.body.tail_boundary.semantic_cursor,
        checkpoint_governance_cursor: checkpoint.body.tail_boundary.governance_cursor,
        loaded_semantic_tail_event_count,
        loaded_governance_tail_event_count,
    };
    Ok(Output {
        schema_version: "cal-ontology-graph-query-output/v1-prototype",
        canonical_replay_source: false,
        authority_effect: "none",
        command: "recover-checkpoint-tail".to_owned(),
        result: serde_json::to_value(result)
            .map_err(|error| ("OUTPUT_SERIALIZATION_FAILED".to_owned(), error.to_string()))?,
    })
}

fn recover_files(arguments: &[String]) -> Result<Output<Value>, (String, String)> {
    let semantic = PathBuf::from(required(
        arguments,
        1,
        "recover-files <semantic-events-dir> <governance-events-dir> <expectation-json>",
    )?);
    let governance = PathBuf::from(required(
        arguments,
        2,
        "recover-files <semantic-events-dir> <governance-events-dir> <expectation-json>",
    )?);
    let expectation_path = PathBuf::from(required(
        arguments,
        3,
        "recover-files <semantic-events-dir> <governance-events-dir> <expectation-json>",
    )?);
    let expectation: RecoveryExpectation =
        serde_json::from_slice(&fs::read(&expectation_path).map_err(|error| {
            (
                "RECOVERY_EXPECTATION_READ_FAILED".to_owned(),
                format!("{}: {error}", expectation_path.display()),
            )
        })?)
        .map_err(|error| {
            (
                "RECOVERY_EXPECTATION_INVALID".to_owned(),
                format!("{}: {error}", expectation_path.display()),
            )
        })?;
    let load_started = Instant::now();
    let store = EventStore::load(&semantic, &governance)
        .map_err(|failure| (failure.code, failure.detail))?;
    let event_store_load_ns = load_started.elapsed().as_nanos();
    let rebuild_started = Instant::now();
    let (_, receipt) = GraphReadModel::recover_from_event_store(&store, &expectation)
        .map_err(|failure| (failure.code, failure.detail))?;
    let graph_rebuild_ns = rebuild_started.elapsed().as_nanos();
    let result = serde_json::to_value(FileRecoveryResult {
        receipt,
        event_store_load_ns,
        graph_rebuild_ns,
    })
    .map_err(|error| ("OUTPUT_SERIALIZATION_FAILED".to_owned(), error.to_string()))?;
    Ok(Output {
        schema_version: "cal-ontology-graph-query-output/v1-prototype",
        canonical_replay_source: false,
        authority_effect: "none",
        command: "recover-files".to_owned(),
        result,
    })
}

fn required<'a>(
    arguments: &'a [String],
    index: usize,
    usage: &str,
) -> Result<&'a str, (String, String)> {
    arguments
        .get(index)
        .map(String::as_str)
        .ok_or_else(|| ("COMMAND_ARGUMENT_MISSING".to_owned(), usage.to_owned()))
}

fn parse_cursor(value: &str, label: &str) -> Result<u64, (String, String)> {
    value.parse::<u64>().map_err(|error| {
        (
            "CURSOR_INVALID".to_owned(),
            format!("{label} cursor {value:?}: {error}"),
        )
    })
}

fn fixture_paths() -> (PathBuf, PathBuf) {
    let root = env::var_os("CAL_ONTOLOGY_FIXTURE_ROOT")
        .map(PathBuf::from)
        .unwrap_or_else(|| {
            PathBuf::from(env!("CARGO_MANIFEST_DIR"))
                .join("../../../migration/cal-w7-ontology-product-epoch-001/fixtures/output")
        });
    (root.join("semantic-events"), root.join("governance-events"))
}
