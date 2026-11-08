use std::collections::{BTreeMap, BTreeSet};
use std::fmt::{self, Display};
use std::fs;
use std::os::unix::process::CommandExt;
use std::path::{Component, Path, PathBuf};
use std::process::{Command, Stdio};
use std::thread;
use std::time::{Duration, Instant};

use serde_json::{Value, json};

use crate::identity::{canonical_digest, exact_ref, sha256_bytes, verify_exact_ref};
use crate::model::*;
use crate::store::StagingRun;

#[derive(Clone, Debug)]
pub struct EvfError {
    pub code: String,
    pub message: String,
}

impl EvfError {
    pub fn new(code: impl Into<String>, error: impl Display) -> Self {
        Self {
            code: code.into(),
            message: error.to_string(),
        }
    }

    pub fn message(code: impl Into<String>, message: impl Into<String>) -> Self {
        Self {
            code: code.into(),
            message: message.into(),
        }
    }
}

impl Display for EvfError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(formatter, "{}: {}", self.code, self.message)
    }
}

impl std::error::Error for EvfError {}

#[derive(Clone, Debug)]
pub struct RunResult {
    pub aggregate: AggregateReceipt,
    pub run_path: PathBuf,
}

fn is_id(value: &str) -> bool {
    !value.is_empty()
        && value.len() <= 240
        && value.bytes().all(|byte| {
            byte.is_ascii_alphanumeric() || matches!(byte, b'.' | b'_' | b':' | b'/' | b'-')
        })
        && value.as_bytes()[0].is_ascii_alphanumeric()
}

fn safe_working_directory(value: &str) -> bool {
    let path = Path::new(value);
    !value.is_empty()
        && !path.is_absolute()
        && !path.components().any(|part| {
            matches!(
                part,
                Component::ParentDir | Component::RootDir | Component::Prefix(_)
            )
        })
}

pub fn validate_profile(profile: &EnforcementProfile) -> Result<(), EvfError> {
    if profile.schema_version != "evf.enforcement-profile/v1" {
        return Err(EvfError::message(
            "PROFILE_SCHEMA_VERSION_INVALID",
            &profile.schema_version,
        ));
    }
    if !is_id(&profile.profile_id) || profile.subject.is_empty() || profile.claim_ceiling.is_empty()
    {
        return Err(EvfError::message(
            "PROFILE_IDENTITY_INVALID",
            &profile.profile_id,
        ));
    }
    if profile.authority_effect != "none" {
        return Err(EvfError::message(
            "PROFILE_AUTHORITY_EFFECT_FORBIDDEN",
            &profile.authority_effect,
        ));
    }
    if profile.repetitions != 2 {
        return Err(EvfError::message(
            "PROFILE_REPETITION_DENOMINATOR_INVALID",
            profile.repetitions.to_string(),
        ));
    }
    if profile.stages.len() != STAGE_IDS.len() {
        return Err(EvfError::message(
            "PROFILE_STAGE_DENOMINATOR_INVALID",
            profile.stages.len().to_string(),
        ));
    }
    for (expected, stage) in STAGE_IDS.iter().zip(&profile.stages) {
        if stage.stage_id != *expected || !stage.required {
            return Err(EvfError::message(
                "PROFILE_STAGE_ORDER_INVALID",
                &stage.stage_id,
            ));
        }
    }
    if profile.semantic_refs.is_empty() || profile.binding_refs.is_empty() {
        return Err(EvfError::message(
            "PROFILE_EXACT_REF_DENOMINATOR_EMPTY",
            &profile.profile_id,
        ));
    }
    if profile.obligation_ids.is_empty()
        || profile.obligation_denominator != profile.obligation_ids.len()
    {
        return Err(EvfError::message(
            "OBLIGATION_DENOMINATOR_MISMATCH",
            &profile.profile_id,
        ));
    }
    let obligation_ids: BTreeSet<_> = profile.obligation_ids.iter().collect();
    if obligation_ids.len() != profile.obligation_ids.len() {
        return Err(EvfError::message(
            "OBLIGATION_ID_DUPLICATE",
            &profile.profile_id,
        ));
    }
    if profile.checks.is_empty() || profile.mutations.is_empty() {
        return Err(EvfError::message(
            "PROFILE_EXECUTION_DENOMINATOR_EMPTY",
            &profile.profile_id,
        ));
    }
    let mut check_ids = BTreeSet::new();
    let mut provider_ids = BTreeSet::new();
    for check in &profile.checks {
        if !is_id(&check.check_id)
            || !is_id(&check.provider_id)
            || !check_ids.insert(check.check_id.as_str())
        {
            return Err(EvfError::message(
                "CHECK_ID_INVALID_OR_DUPLICATE",
                &check.check_id,
            ));
        }
        provider_ids.insert(check.provider_id.as_str());
        if check.runtime.argv.is_empty()
            || !safe_working_directory(&check.runtime.working_directory)
            || check.runtime.timeout_ms == 0
            || check.runtime.max_output_bytes < 256
            || check.runtime.network != "forbidden"
            || check.runtime.isolation.mechanism != "linux-user-and-network-namespace"
        {
            return Err(EvfError::message(
                "RUNTIME_CONTRACT_INVALID",
                &check.check_id,
            ));
        }
    }
    let mut mutant_ids = BTreeSet::new();
    for mutant in &profile.mutations {
        if !is_id(&mutant.mutant_id)
            || !mutant_ids.insert(mutant.mutant_id.as_str())
            || !check_ids.contains(mutant.check_id.as_str())
            || mutant.expected_rejection_code.is_empty()
        {
            return Err(EvfError::message(
                "MUTATION_CONTRACT_INVALID",
                &mutant.mutant_id,
            ));
        }
    }
    let composition_ids: BTreeSet<_> = profile
        .composition
        .provider_ids
        .iter()
        .map(String::as_str)
        .collect();
    if composition_ids != provider_ids {
        return Err(EvfError::message(
            "COMPOSITION_PROVIDER_DENOMINATOR_MISMATCH",
            &profile.profile_id,
        ));
    }
    match profile.composition.mode.as_str() {
        "single" if provider_ids.len() == 1 => {}
        "all_equal"
            if provider_ids.len() >= 2 && !profile.composition.compare_fields.is_empty() => {}
        _ => {
            return Err(EvfError::message(
                "COMPOSITION_MODE_INVALID",
                &profile.composition.mode,
            ));
        }
    }
    Ok(())
}

fn all_profile_refs(profile: &EnforcementProfile) -> Vec<ExactRef> {
    let mut refs = Vec::new();
    refs.extend(profile.semantic_refs.clone());
    refs.extend(profile.binding_refs.clone());
    refs.extend(profile.composition.comparability_refs.clone());
    refs.push(profile.producer.executable_ref.clone());
    refs.push(profile.verifier.executable_ref.clone());
    for check in &profile.checks {
        refs.push(check.input_ref.clone());
        refs.push(check.runtime.executable_ref.clone());
        refs.push(check.runtime.isolation.unshare_ref.clone());
        refs.extend(check.runtime.tool_refs.clone());
    }
    refs.extend(
        profile
            .mutations
            .iter()
            .map(|mutant| mutant.input_ref.clone()),
    );
    refs
}

fn verify_refs(root: &Path, refs: &[ExactRef]) -> Result<(), EvfError> {
    for reference in refs {
        verify_exact_ref(root, reference)?;
    }
    Ok(())
}

fn stage_digest(receipt: &StageReceipt) -> Result<String, EvfError> {
    let mut value = serde_json::to_value(receipt)
        .map_err(|error| EvfError::new("SERIALIZATION_FAILED", error))?;
    value
        .as_object_mut()
        .expect("stage receipt object")
        .remove("receipt_payload_digest");
    canonical_digest(&value)
}

fn make_stage(
    profile: &EnforcementProfile,
    stage_id: &str,
    state: StageState,
    previous: Option<&StageReceipt>,
    evidence_refs: Vec<ExactRef>,
    reason_codes: Vec<String>,
    residue: Vec<String>,
    details: BTreeMap<String, Value>,
) -> Result<StageReceipt, EvfError> {
    let mut input_stage_receipt_digests = BTreeMap::new();
    if let Some(previous) = previous {
        input_stage_receipt_digests.insert(
            previous.stage_id.clone(),
            previous.receipt_payload_digest.clone(),
        );
    }
    let mut receipt = StageReceipt {
        schema_version: "evf.stage-receipt/v1".to_owned(),
        stage_id: stage_id.to_owned(),
        profile_id: profile.profile_id.clone(),
        route: profile.route.clone(),
        state,
        input_stage_receipt_digests,
        evidence_refs,
        reason_codes,
        residue,
        details,
        claim_ceiling: profile.claim_ceiling.clone(),
        authority_effect: "none".to_owned(),
        receipt_payload_digest: String::new(),
    };
    receipt.receipt_payload_digest = stage_digest(&receipt)?;
    Ok(receipt)
}

fn expand_arg(root: &Path, input: &Path, value: &str) -> String {
    value
        .replace("{input}", &input.to_string_lossy())
        .replace("{repo_root}", &root.to_string_lossy())
}

fn run_provider(
    root: &Path,
    check: &CheckSpec,
    input_ref: &ExactRef,
    expected: &Value,
) -> Result<ProviderObservation, EvfError> {
    let executable = verify_exact_ref(root, &check.runtime.executable_ref)?;
    let unshare = verify_exact_ref(root, &check.runtime.isolation.unshare_ref)?;
    let tool_paths: BTreeSet<PathBuf> = check
        .runtime
        .tool_refs
        .iter()
        .map(|tool| verify_exact_ref(root, tool))
        .collect::<Result<_, _>>()?;
    let input = verify_exact_ref(root, input_ref)?;
    let working_directory = root.join(&check.runtime.working_directory);
    let expanded_args: Vec<String> = check
        .runtime
        .argv
        .iter()
        .map(|value| expand_arg(root, &input, value))
        .collect();
    for argument in &expanded_args {
        let path = Path::new(argument);
        if path.is_absolute() {
            let resolved = fs::canonicalize(path)
                .map_err(|error| EvfError::new("RUNTIME_ARGUMENT_PATH_MISSING", error))?;
            if resolved != input && !tool_paths.contains(&resolved) {
                return Err(EvfError::message(
                    "RUNTIME_ARGUMENT_NOT_EXACT_BOUND",
                    argument,
                ));
            }
        }
    }
    let mut command = Command::new(unshare);
    command
        .arg("--user")
        .arg("--map-root-user")
        .arg("--net")
        .arg("--")
        .arg(executable)
        .args(expanded_args)
        .current_dir(working_directory)
        .env_clear()
        .envs(&check.runtime.environment)
        .process_group(0)
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let mut child = match command.spawn() {
        Ok(child) => child,
        Err(_) => {
            return Ok(ProviderObservation {
                check_id: check.check_id.clone(),
                provider_id: check.provider_id.clone(),
                exit_code: None,
                timed_out: false,
                stdout_sha256: sha256_bytes(&[]),
                stderr_sha256: sha256_bytes(&[]),
                output: Value::Null,
                matched_expected: false,
                error_code: Some("PROVIDER_SPAWN_FAILED".to_owned()),
            });
        }
    };
    let started = Instant::now();
    let mut timed_out = false;
    loop {
        if child
            .try_wait()
            .map_err(|error| EvfError::new("PROVIDER_WAIT_FAILED", error))?
            .is_some()
        {
            break;
        }
        if started.elapsed() >= Duration::from_millis(check.runtime.timeout_ms) {
            timed_out = true;
            let process_group = -(child.id() as i32);
            // SAFETY: the child is placed in a fresh process group immediately before spawn,
            // and the negative id targets only that bounded provider group.
            let term_result = unsafe { libc::kill(process_group, libc::SIGTERM) };
            if term_result != 0 {
                return Err(EvfError::new(
                    "PROVIDER_TERMINATION_FAILED",
                    std::io::Error::last_os_error(),
                ));
            }
            let grace_started = Instant::now();
            while grace_started.elapsed() < Duration::from_millis(250) {
                if child
                    .try_wait()
                    .map_err(|error| EvfError::new("PROVIDER_WAIT_FAILED", error))?
                    .is_some()
                {
                    break;
                }
                thread::sleep(Duration::from_millis(10));
            }
            if child
                .try_wait()
                .map_err(|error| EvfError::new("PROVIDER_WAIT_FAILED", error))?
                .is_none()
            {
                // SAFETY: same bounded process group as above; ESRCH means it exited
                // between the non-blocking wait and the signal and is therefore harmless.
                let kill_result = unsafe { libc::kill(process_group, libc::SIGKILL) };
                if kill_result != 0
                    && std::io::Error::last_os_error().raw_os_error() != Some(libc::ESRCH)
                {
                    return Err(EvfError::new(
                        "PROVIDER_KILL_FAILED",
                        std::io::Error::last_os_error(),
                    ));
                }
            }
            break;
        }
        thread::sleep(Duration::from_millis(10));
    }
    let output = child
        .wait_with_output()
        .map_err(|error| EvfError::new("PROVIDER_WAIT_FAILED", error))?;
    let output_bytes = output.stdout.len() + output.stderr.len();
    let (value, error_code) = if output_bytes as u64 > check.runtime.max_output_bytes {
        (
            Value::Null,
            Some("PROVIDER_OUTPUT_LIMIT_EXCEEDED".to_owned()),
        )
    } else if timed_out {
        (Value::Null, Some("PROVIDER_TIMEOUT".to_owned()))
    } else if !output.status.success() {
        (Value::Null, Some("PROVIDER_EXIT_NONZERO".to_owned()))
    } else {
        match serde_json::from_slice(&output.stdout) {
            Ok(value) => (value, None),
            Err(_) => (Value::Null, Some("PROVIDER_OUTPUT_MALFORMED".to_owned())),
        }
    };
    let matched_expected = error_code.is_none() && value == *expected;
    Ok(ProviderObservation {
        check_id: check.check_id.clone(),
        provider_id: check.provider_id.clone(),
        exit_code: output.status.code(),
        timed_out,
        stdout_sha256: sha256_bytes(&output.stdout),
        stderr_sha256: sha256_bytes(&output.stderr),
        matched_expected,
        error_code,
        output: value,
    })
}

fn repeated_provider(
    root: &Path,
    profile: &EnforcementProfile,
    check: &CheckSpec,
    input_ref: &ExactRef,
    expected: &Value,
) -> Result<(Vec<ProviderObservation>, bool), EvfError> {
    let mut observations = Vec::new();
    for _ in 0..profile.repetitions {
        observations.push(run_provider(root, check, input_ref, expected)?);
    }
    let digests: Result<Vec<_>, _> = observations
        .iter()
        .map(|item| canonical_digest(&item.output))
        .collect();
    let digests = digests?;
    let replay_equal = digests.windows(2).all(|pair| pair[0] == pair[1]);
    Ok((observations, replay_equal))
}

fn aggregate_state(stages: &[StageReceipt]) -> StageState {
    if stages.iter().any(|stage| stage.state == StageState::Failed) {
        StageState::Failed
    } else if stages
        .iter()
        .any(|stage| stage.state == StageState::Blocked)
    {
        StageState::Blocked
    } else if stages
        .iter()
        .any(|stage| stage.state == StageState::Indeterminate)
    {
        StageState::Indeterminate
    } else {
        StageState::Passed
    }
}

fn details(entries: impl IntoIterator<Item = (&'static str, Value)>) -> BTreeMap<String, Value> {
    entries
        .into_iter()
        .map(|(key, value)| (key.to_owned(), value))
        .collect()
}

fn invoke_verifier(
    root: &Path,
    profile: &EnforcementProfile,
    provisional_path: &Path,
) -> Result<VerificationReceipt, EvfError> {
    let verifier = verify_exact_ref(root, &profile.verifier.executable_ref)?;
    let output = Command::new(verifier)
        .arg("--repo-root")
        .arg(root)
        .arg("--bundle")
        .arg(provisional_path)
        .env_clear()
        .output()
        .map_err(|error| EvfError::new("VERIFIER_SPAWN_FAILED", error))?;
    if !output.status.success() {
        return Err(EvfError::message(
            "INDEPENDENT_VERIFIER_FAILED",
            String::from_utf8_lossy(&output.stderr).trim().to_owned(),
        ));
    }
    serde_json::from_slice(&output.stdout)
        .map_err(|error| EvfError::new("VERIFIER_OUTPUT_MALFORMED", error))
}

fn aggregate_digest(receipt: &AggregateReceipt) -> Result<String, EvfError> {
    let mut value = serde_json::to_value(receipt)
        .map_err(|error| EvfError::new("SERIALIZATION_FAILED", error))?;
    value
        .as_object_mut()
        .expect("aggregate object")
        .remove("evidence_payload_digest");
    canonical_digest(&value)
}

pub fn run_profile(
    root: &Path,
    profile_path: &Path,
    store: &Path,
    attempt_id: &str,
) -> Result<RunResult, EvfError> {
    let root = fs::canonicalize(root)
        .map_err(|error| EvfError::new("REPOSITORY_ROOT_UNAVAILABLE", error))?;
    let profile_path =
        fs::canonicalize(profile_path).map_err(|error| EvfError::new("PROFILE_MISSING", error))?;
    let profile: EnforcementProfile = serde_json::from_slice(
        &fs::read(&profile_path).map_err(|error| EvfError::new("PROFILE_UNREADABLE", error))?,
    )
    .map_err(|error| EvfError::new("PROFILE_INVALID", error))?;
    validate_profile(&profile)?;
    let profile_ref = exact_ref(&root, &profile_path)?;
    verify_refs(&root, &all_profile_refs(&profile))?;
    let staging = StagingRun::create(store, attempt_id)?;

    let mut stages = Vec::new();
    stages.push(make_stage(
        &profile,
        "S0",
        StageState::Passed,
        None,
        profile.semantic_refs.clone(),
        vec![],
        vec![],
        details([("semantic_ref_count", json!(profile.semantic_refs.len()))]),
    )?);
    stages.push(make_stage(
        &profile,
        "S1",
        StageState::Passed,
        stages.last(),
        vec![profile_ref.clone()],
        vec![],
        vec![],
        details([("selected_route", json!(profile.route))]),
    )?);
    stages.push(make_stage(
        &profile,
        "S2",
        StageState::Passed,
        stages.last(),
        profile.semantic_refs.clone(),
        vec![],
        vec![],
        details([
            ("obligation_ids", json!(profile.obligation_ids)),
            (
                "obligation_denominator",
                json!(profile.obligation_denominator),
            ),
        ]),
    )?);
    stages.push(make_stage(
        &profile,
        "S3",
        StageState::Passed,
        stages.last(),
        profile.binding_refs.clone(),
        vec![],
        vec![],
        details([("binding_ref_count", json!(profile.binding_refs.len()))]),
    )?);
    let check_input_refs = profile
        .checks
        .iter()
        .map(|check| check.input_ref.clone())
        .collect();
    stages.push(make_stage(
        &profile,
        "S4",
        StageState::Passed,
        stages.last(),
        check_input_refs,
        vec![],
        vec![],
        details([(
            "check_ids",
            json!(
                profile
                    .checks
                    .iter()
                    .map(|item| &item.check_id)
                    .collect::<Vec<_>>()
            ),
        )]),
    )?);
    let mut runtime_refs = Vec::new();
    for check in &profile.checks {
        runtime_refs.push(check.runtime.executable_ref.clone());
        runtime_refs.push(check.runtime.isolation.unshare_ref.clone());
        runtime_refs.extend(check.runtime.tool_refs.clone());
    }
    stages.push(make_stage(
        &profile,
        "S5",
        StageState::Passed,
        stages.last(),
        runtime_refs,
        vec![],
        vec![],
        details([
            ("provider_count", json!(profile.checks.len())),
            ("network", json!("forbidden")),
            ("isolation", json!("linux-user-and-network-namespace")),
        ]),
    )?);

    let mut positive = BTreeMap::<String, Vec<ProviderObservation>>::new();
    let mut positive_replay_equal = true;
    for check in &profile.checks {
        let (observations, replay_equal) = repeated_provider(
            &root,
            &profile,
            check,
            &check.input_ref,
            &check.expected_output,
        )?;
        positive_replay_equal &= replay_equal;
        positive.insert(check.check_id.clone(), observations);
    }
    let positive_passed = positive
        .values()
        .flatten()
        .all(|item| item.matched_expected)
        && positive_replay_equal;
    stages.push(make_stage(
        &profile,
        "S6",
        if positive_passed {
            StageState::Passed
        } else {
            StageState::Failed
        },
        stages.last(),
        profile
            .checks
            .iter()
            .map(|item| item.input_ref.clone())
            .collect(),
        if positive_passed {
            vec![]
        } else {
            vec!["POSITIVE_EXECUTION_MISMATCH".to_owned()]
        },
        vec![],
        details([
            ("observations", json!(positive)),
            ("replay_equal", json!(positive_replay_equal)),
        ]),
    )?);

    let mut mutation_observations = Vec::new();
    let mut negative_replay_equal = true;
    if positive_passed {
        for mutant in &profile.mutations {
            let check = profile
                .checks
                .iter()
                .find(|item| item.check_id == mutant.check_id)
                .ok_or_else(|| EvfError::message("MUTATION_CHECK_MISSING", &mutant.check_id))?;
            let (observations, replay_equal) = repeated_provider(
                &root,
                &profile,
                check,
                &mutant.input_ref,
                &mutant.expected_output,
            )?;
            negative_replay_equal &= replay_equal;
            let killed = replay_equal && observations.iter().all(|item| item.matched_expected);
            mutation_observations.push(MutationObservation {
                mutant_id: mutant.mutant_id.clone(),
                check_id: mutant.check_id.clone(),
                expected_rejection_code: mutant.expected_rejection_code.clone(),
                observations,
                killed_for_declared_cause: killed,
            });
        }
    }
    let negative_passed = positive_passed
        && mutation_observations.len() == profile.mutations.len()
        && mutation_observations
            .iter()
            .all(|item| item.killed_for_declared_cause)
        && negative_replay_equal;
    stages.push(make_stage(
        &profile,
        "S7",
        if !positive_passed {
            StageState::Blocked
        } else if negative_passed {
            StageState::Passed
        } else {
            StageState::Failed
        },
        stages.last(),
        profile
            .mutations
            .iter()
            .map(|item| item.input_ref.clone())
            .collect(),
        if !positive_passed {
            vec!["POSITIVE_EXECUTION_REQUIRED".to_owned()]
        } else if negative_passed {
            vec![]
        } else {
            vec!["NEGATIVE_CONTROL_SURVIVED_OR_WRONG_CAUSE".to_owned()]
        },
        vec![],
        details([
            ("mutations", json!(mutation_observations)),
            ("mutation_denominator", json!(profile.mutations.len())),
            ("replay_equal", json!(negative_replay_equal)),
        ]),
    )?);

    let normalization_passed = positive_passed && negative_passed;
    stages.push(make_stage(
        &profile,
        "S8",
        if normalization_passed {
            StageState::Passed
        } else {
            StageState::Blocked
        },
        stages.last(),
        vec![],
        if normalization_passed {
            vec![]
        } else {
            vec!["NATIVE_RESULT_NOT_NORMALIZABLE".to_owned()]
        },
        vec![],
        details([(
            "normalized_outcome",
            json!(if normalization_passed {
                "PASS_BOUNDED"
            } else {
                "NON_PASS"
            }),
        )]),
    )?);

    let composition_passed = if normalization_passed && profile.composition.mode == "single" {
        true
    } else if normalization_passed {
        let first = profile
            .checks
            .first()
            .and_then(|check| positive.get(&check.check_id))
            .and_then(|items| items.first());
        profile.composition.compare_fields.iter().all(|field| {
            first
                .and_then(|item| item.output.get(field))
                .is_some_and(|expected| {
                    profile.checks.iter().all(|check| {
                        positive
                            .get(&check.check_id)
                            .and_then(|items| items.first())
                            .and_then(|item| item.output.get(field))
                            == Some(expected)
                    })
                })
        })
    } else {
        false
    };
    stages.push(make_stage(
        &profile,
        "S9",
        if !normalization_passed {
            StageState::Blocked
        } else if composition_passed {
            StageState::Passed
        } else {
            StageState::Failed
        },
        stages.last(),
        profile.composition.comparability_refs.clone(),
        if !normalization_passed {
            vec!["NORMALIZED_RESULTS_REQUIRED".to_owned()]
        } else if composition_passed {
            vec![]
        } else {
            vec!["PROVIDER_RESULTS_INCOMPARABLE_OR_DISAGREE".to_owned()]
        },
        vec![],
        details([
            ("mode", json!(profile.composition.mode)),
            ("provider_ids", json!(profile.composition.provider_ids)),
            ("compare_fields", json!(profile.composition.compare_fields)),
        ]),
    )?);
    stages.push(make_stage(
        &profile,
        "S10",
        StageState::Passed,
        stages.last(),
        vec![profile.producer.executable_ref.clone()],
        vec![],
        vec![],
        details([("constructed_stage_receipts", json!(10))]),
    )?);

    let provisional = ProvisionalBundle {
        schema_version: "evf.provisional-bundle/v1".to_owned(),
        profile: profile.clone(),
        profile_ref: profile_ref.clone(),
        producer_aggregate_state: aggregate_state(&stages),
        denominator: Denominator {
            stages: 13,
            checks: profile.checks.len(),
            mutations: profile.mutations.len(),
        },
        stage_receipts: stages.clone(),
        authority_effect: "none".to_owned(),
    };
    let provisional_path = staging.write_json("PROVISIONAL.json", &provisional)?;
    let verification = invoke_verifier(&root, &profile, &provisional_path)?;
    staging.write_json("VERIFICATION.json", &verification)?;
    stages.push(make_stage(
        &profile,
        "S11",
        if verification.verdict == "passed" {
            StageState::Passed
        } else {
            StageState::Failed
        },
        stages.last(),
        vec![profile.verifier.executable_ref.clone()],
        verification.reason_codes.clone(),
        vec![],
        details([("verified_stage_ids", json!(verification.verified_stage_ids))]),
    )?);
    stages.push(make_stage(
        &profile,
        "S12",
        if verification.all_refs_current && verification.replay_equal {
            StageState::Passed
        } else {
            StageState::Failed
        },
        stages.last(),
        all_profile_refs(&profile),
        if verification.all_refs_current && verification.replay_equal {
            vec![]
        } else {
            vec!["CURRENTNESS_OR_REPLAY_FAILED".to_owned()]
        },
        vec![],
        details([
            ("all_refs_current", json!(verification.all_refs_current)),
            ("replay_equal", json!(verification.replay_equal)),
        ]),
    )?);

    let mut aggregate = AggregateReceipt {
        schema_version: "evf.evolvable-validation-receipt/v1".to_owned(),
        receipt_id: format!("evf.{}.aggregate.v1", profile.profile_id),
        profile_id: profile.profile_id.clone(),
        route: profile.route.clone(),
        profile_ref,
        aggregate_state: aggregate_state(&stages),
        all_required_stages_present: stages
            .iter()
            .map(|stage| stage.stage_id.as_str())
            .eq(STAGE_IDS),
        denominator: Denominator {
            stages: 13,
            checks: profile.checks.len(),
            mutations: profile.mutations.len(),
        },
        verification_receipt: verification,
        evidence_payload_digest: String::new(),
        authority_effect: "none".to_owned(),
        release_admission: "not-granted".to_owned(),
        claim_ceiling: profile.claim_ceiling.clone(),
        stage_receipts: stages,
    };
    aggregate.evidence_payload_digest = aggregate_digest(&aggregate)?;
    staging.write_json("EVIDENCE.json", &aggregate)?;
    let run_path = staging.finalize(&aggregate.evidence_payload_digest)?;
    Ok(RunResult {
        aggregate,
        run_path,
    })
}
