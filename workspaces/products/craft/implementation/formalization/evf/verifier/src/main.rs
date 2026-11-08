use std::collections::BTreeSet;
use std::env;
use std::fs;
use std::path::{Component, Path, PathBuf};

use serde_json::{Map, Value, json};
use sha2::{Digest, Sha256};

const PROVISIONAL_STAGE_IDS: [&str; 11] = [
    "S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10",
];
const ALL_STAGE_IDS: [&str; 13] = [
    "S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S12",
];

fn sha256(bytes: &[u8]) -> String {
    Sha256::digest(bytes)
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect()
}

fn canonical(value: &Value) -> Value {
    match value {
        Value::Array(values) => Value::Array(values.iter().map(canonical).collect()),
        Value::Object(values) => {
            let mut keys: Vec<_> = values.keys().collect();
            keys.sort();
            let mut result = Map::new();
            for key in keys {
                result.insert(key.clone(), canonical(&values[key]));
            }
            Value::Object(result)
        }
        value => value.clone(),
    }
}

fn digest(value: &Value) -> Result<String, String> {
    serde_json::to_vec(&canonical(value))
        .map(|bytes| sha256(&bytes))
        .map_err(|error| error.to_string())
}

fn object<'a>(value: &'a Value, label: &str) -> Result<&'a Map<String, Value>, String> {
    value
        .as_object()
        .ok_or_else(|| format!("{label} must be an object"))
}

fn string<'a>(object: &'a Map<String, Value>, key: &str) -> Result<&'a str, String> {
    object
        .get(key)
        .and_then(Value::as_str)
        .ok_or_else(|| format!("{key} must be a string"))
}

fn bool_value(object: &Map<String, Value>, key: &str) -> Result<bool, String> {
    object
        .get(key)
        .and_then(Value::as_bool)
        .ok_or_else(|| format!("{key} must be a boolean"))
}

fn unsigned(object: &Map<String, Value>, key: &str) -> Result<usize, String> {
    object
        .get(key)
        .and_then(Value::as_u64)
        .and_then(|value| usize::try_from(value).ok())
        .ok_or_else(|| format!("{key} must be an unsigned integer"))
}

fn array<'a>(object: &'a Map<String, Value>, key: &str) -> Result<&'a Vec<Value>, String> {
    object
        .get(key)
        .and_then(Value::as_array)
        .ok_or_else(|| format!("{key} must be an array"))
}

fn exact_keys(object: &Map<String, Value>, expected: &[&str], label: &str) -> Result<(), String> {
    let actual: BTreeSet<_> = object.keys().map(String::as_str).collect();
    let expected: BTreeSet<_> = expected.iter().copied().collect();
    if actual != expected {
        return Err(format!("{label} fields differ from the closed contract"));
    }
    Ok(())
}

fn safe_repo_path(root: &Path, text: &str) -> Result<PathBuf, String> {
    let relative = Path::new(text);
    if relative.is_absolute()
        || relative.components().any(|part| {
            matches!(
                part,
                Component::ParentDir | Component::RootDir | Component::Prefix(_)
            )
        })
    {
        return Err(format!("unsafe repository exact ref: {text}"));
    }
    let path = fs::canonicalize(root.join(relative)).map_err(|error| error.to_string())?;
    if !path.starts_with(root) {
        return Err(format!("repository exact ref escapes root: {text}"));
    }
    Ok(path)
}

fn resolve_ref(root: &Path, value: &Value) -> Result<PathBuf, String> {
    let reference = object(value, "exact ref")?;
    let text = string(reference, "path")?;
    if !bool_value(reference, "current")? {
        return Err(format!("stale exact ref: {text}"));
    }
    let location = string(reference, "location")?;
    let path = match location {
        "repository" => safe_repo_path(root, text)?,
        "host" => {
            let path = Path::new(text);
            if !path.is_absolute() {
                return Err(format!("host ref is not absolute: {text}"));
            }
            fs::canonicalize(path).map_err(|error| error.to_string())?
        }
        _ => return Err(format!("invalid ref location: {location}")),
    };
    Ok(path)
}

fn verify_ref(root: &Path, value: &Value) -> Result<(), String> {
    let reference = object(value, "exact ref")?;
    exact_keys(
        reference,
        &["path", "sha256", "size_bytes", "location", "current"],
        "exact ref",
    )?;
    let text = string(reference, "path")?;
    let path = resolve_ref(root, value)?;
    let bytes = fs::read(path).map_err(|error| error.to_string())?;
    let expected_size = reference
        .get("size_bytes")
        .and_then(Value::as_u64)
        .ok_or("size_bytes must be an integer")?;
    if bytes.len() as u64 != expected_size {
        return Err(format!("exact ref size mismatch: {text}"));
    }
    if sha256(&bytes) != string(reference, "sha256")? {
        return Err(format!("exact ref digest mismatch: {text}"));
    }
    Ok(())
}

fn looks_like_ref(object: &Map<String, Value>) -> bool {
    ["path", "sha256", "size_bytes", "location", "current"]
        .iter()
        .all(|key| object.contains_key(*key))
}

fn collect_and_verify_refs(root: &Path, value: &Value, errors: &mut Vec<String>) {
    match value {
        Value::Array(values) => values
            .iter()
            .for_each(|value| collect_and_verify_refs(root, value, errors)),
        Value::Object(values) => {
            if looks_like_ref(values) {
                if let Err(error) = verify_ref(root, value) {
                    errors.push(error);
                }
            } else {
                values
                    .values()
                    .for_each(|value| collect_and_verify_refs(root, value, errors));
            }
        }
        _ => {}
    }
}

fn receipt_digest(value: &Value, field: &str) -> Result<String, String> {
    let mut value = value.clone();
    object(&value, "receipt")?;
    value.as_object_mut().unwrap().remove(field);
    digest(&value)
}

fn unique_strings(values: &[Value], label: &str) -> Result<BTreeSet<String>, String> {
    let mut result = BTreeSet::new();
    for value in values {
        let value = value
            .as_str()
            .ok_or_else(|| format!("{label} contains a non-string"))?;
        if value.is_empty() || !result.insert(value.to_owned()) {
            return Err(format!("{label} contains an empty or duplicate value"));
        }
    }
    Ok(result)
}

fn verify_profile(profile: &Value) -> Result<(), String> {
    let profile = object(profile, "profile")?;
    exact_keys(
        profile,
        &[
            "schema_version",
            "profile_id",
            "subject",
            "route",
            "stages",
            "semantic_refs",
            "obligation_ids",
            "obligation_denominator",
            "binding_refs",
            "checks",
            "mutations",
            "composition",
            "producer",
            "verifier",
            "repetitions",
            "claim_ceiling",
            "authority_effect",
        ],
        "profile",
    )?;
    if string(profile, "schema_version")? != "evf.enforcement-profile/v1"
        || string(profile, "authority_effect")? != "none"
        || string(profile, "profile_id")?.is_empty()
        || string(profile, "subject")?.is_empty()
        || string(profile, "claim_ceiling")?.is_empty()
        || unsigned(profile, "repetitions")? != 2
    {
        return Err("invalid profile base contract".to_owned());
    }
    let route = string(profile, "route")?;
    if !["executable", "theorem", "multi_provider"].contains(&route) {
        return Err("unsupported profile route".to_owned());
    }
    let stages = array(profile, "stages")?;
    if stages.len() != ALL_STAGE_IDS.len() {
        return Err("profile stage denominator mismatch".to_owned());
    }
    for (stage, expected) in stages.iter().zip(ALL_STAGE_IDS) {
        let stage = object(stage, "profile stage")?;
        exact_keys(stage, &["stage_id", "required"], "profile stage")?;
        if string(stage, "stage_id")? != expected || !bool_value(stage, "required")? {
            return Err(format!("invalid required profile stage: {expected}"));
        }
    }
    if array(profile, "semantic_refs")?.is_empty() || array(profile, "binding_refs")?.is_empty() {
        return Err("profile semantic or binding denominator is empty".to_owned());
    }
    let obligations = unique_strings(array(profile, "obligation_ids")?, "obligation_ids")?;
    if obligations.is_empty() || unsigned(profile, "obligation_denominator")? != obligations.len() {
        return Err("obligation denominator mismatch".to_owned());
    }
    let checks = array(profile, "checks")?;
    let mutations = array(profile, "mutations")?;
    if checks.is_empty() || mutations.is_empty() {
        return Err("execution denominator is empty".to_owned());
    }
    let mut check_ids = BTreeSet::new();
    let mut provider_ids = BTreeSet::new();
    for check in checks {
        let check = object(check, "check")?;
        exact_keys(
            check,
            &[
                "check_id",
                "provider_id",
                "runtime",
                "input_ref",
                "expected_output",
            ],
            "check",
        )?;
        let check_id = string(check, "check_id")?;
        let provider_id = string(check, "provider_id")?;
        if !check_ids.insert(check_id.to_owned()) || provider_id.is_empty() {
            return Err("duplicate or empty check identity".to_owned());
        }
        provider_ids.insert(provider_id.to_owned());
        object(
            check
                .get("expected_output")
                .ok_or("expected_output missing")?,
            "expected_output",
        )?;
        let runtime = object(check.get("runtime").ok_or("runtime missing")?, "runtime")?;
        exact_keys(
            runtime,
            &[
                "executable_ref",
                "tool_refs",
                "argv",
                "working_directory",
                "environment",
                "timeout_ms",
                "max_output_bytes",
                "network",
                "isolation",
            ],
            "runtime",
        )?;
        if string(runtime, "network")? != "forbidden"
            || array(runtime, "argv")?.is_empty()
            || unsigned(runtime, "timeout_ms")? == 0
            || unsigned(runtime, "max_output_bytes")? < 256
        {
            return Err("invalid runtime boundary".to_owned());
        }
        let isolation = object(
            runtime.get("isolation").ok_or("isolation missing")?,
            "isolation",
        )?;
        exact_keys(isolation, &["mechanism", "unshare_ref"], "isolation")?;
        if string(isolation, "mechanism")? != "linux-user-and-network-namespace" {
            return Err("invalid isolation mechanism".to_owned());
        }
    }
    let mut mutant_ids = BTreeSet::new();
    for mutation in mutations {
        let mutation = object(mutation, "mutation")?;
        exact_keys(
            mutation,
            &[
                "mutant_id",
                "check_id",
                "input_ref",
                "expected_output",
                "expected_rejection_code",
            ],
            "mutation",
        )?;
        if !mutant_ids.insert(string(mutation, "mutant_id")?.to_owned())
            || !check_ids.contains(string(mutation, "check_id")?)
            || string(mutation, "expected_rejection_code")?.is_empty()
        {
            return Err("invalid mutation identity or binding".to_owned());
        }
    }
    let composition = object(
        profile.get("composition").ok_or("composition missing")?,
        "composition",
    )?;
    exact_keys(
        composition,
        &[
            "mode",
            "provider_ids",
            "compare_fields",
            "comparability_refs",
        ],
        "composition",
    )?;
    let composition_providers =
        unique_strings(array(composition, "provider_ids")?, "provider_ids")?;
    if composition_providers != provider_ids || array(composition, "comparability_refs")?.is_empty()
    {
        return Err("composition provider denominator mismatch".to_owned());
    }
    match string(composition, "mode")? {
        "single" if provider_ids.len() == 1 => {}
        "all_equal"
            if provider_ids.len() >= 2 && !array(composition, "compare_fields")?.is_empty() => {}
        _ => return Err("invalid composition mode".to_owned()),
    }
    for owner in ["producer", "verifier"] {
        let executable = object(
            profile
                .get(owner)
                .ok_or_else(|| format!("{owner} missing"))?,
            owner,
        )?;
        exact_keys(executable, &["executable_ref"], owner)?;
    }
    Ok(())
}

fn verify_denominator(
    container: &Map<String, Value>,
    profile: &Map<String, Value>,
) -> Result<(), String> {
    let denominator = object(
        container.get("denominator").ok_or("denominator missing")?,
        "denominator",
    )?;
    exact_keys(
        denominator,
        &["stages", "checks", "mutations"],
        "denominator",
    )?;
    if unsigned(denominator, "stages")? != ALL_STAGE_IDS.len()
        || unsigned(denominator, "checks")? != array(profile, "checks")?.len()
        || unsigned(denominator, "mutations")? != array(profile, "mutations")?.len()
    {
        return Err("aggregate denominator mismatch".to_owned());
    }
    Ok(())
}

fn verify_stage_chain(
    stages: &[Value],
    expected_ids: &[&str],
    profile_id: &str,
    route: &str,
    claim_ceiling: &str,
) -> Result<(), String> {
    if stages.len() != expected_ids.len() {
        return Err(format!(
            "stage denominator mismatch: {} != {}",
            stages.len(),
            expected_ids.len()
        ));
    }
    let mut previous: Option<(&str, &str)> = None;
    for (stage, expected_id) in stages.iter().zip(expected_ids) {
        let stage_object = object(stage, "stage")?;
        exact_keys(
            stage_object,
            &[
                "schema_version",
                "stage_id",
                "profile_id",
                "route",
                "state",
                "input_stage_receipt_digests",
                "evidence_refs",
                "reason_codes",
                "residue",
                "details",
                "claim_ceiling",
                "authority_effect",
                "receipt_payload_digest",
            ],
            "stage receipt",
        )?;
        let stage_id = string(stage_object, "stage_id")?;
        if stage_id != *expected_id {
            return Err(format!(
                "stage order mismatch: expected {expected_id}, got {stage_id}"
            ));
        }
        if string(stage_object, "schema_version")? != "evf.stage-receipt/v1"
            || string(stage_object, "profile_id")? != profile_id
            || string(stage_object, "route")? != route
            || string(stage_object, "claim_ceiling")? != claim_ceiling
            || string(stage_object, "authority_effect")? != "none"
            || ![
                "passed",
                "failed",
                "blocked",
                "indeterminate",
                "not_applicable",
            ]
            .contains(&string(stage_object, "state")?)
        {
            return Err(format!("stage {stage_id} has authority effect"));
        }
        let declared = string(stage_object, "receipt_payload_digest")?;
        let actual = receipt_digest(stage, "receipt_payload_digest")?;
        if declared != actual {
            return Err(format!("stage digest mismatch: {stage_id}"));
        }
        let inputs = stage_object
            .get("input_stage_receipt_digests")
            .and_then(Value::as_object)
            .ok_or("input digest map missing")?;
        match previous {
            None if !inputs.is_empty() => {
                return Err("S0 must not have an input stage digest".to_owned());
            }
            Some((previous_id, previous_digest)) => {
                if inputs.len() != 1
                    || inputs.get(previous_id).and_then(Value::as_str) != Some(previous_digest)
                {
                    return Err(format!("stage chain mismatch: {stage_id}"));
                }
            }
            _ => {}
        }
        previous = Some((stage_id, declared));
    }
    Ok(())
}

fn aggregate_state(stages: &[Value]) -> Result<&'static str, String> {
    let mut states = Vec::new();
    for stage in stages {
        states.push(string(object(stage, "stage")?, "state")?);
    }
    if states.contains(&"failed") {
        Ok("failed")
    } else if states.contains(&"blocked") {
        Ok("blocked")
    } else if states.contains(&"indeterminate") {
        Ok("indeterminate")
    } else {
        Ok("passed")
    }
}

fn replay_equal(stages: &[Value]) -> Result<bool, String> {
    for id in ["S6", "S7"] {
        let stage = stages
            .iter()
            .find(|stage| stage.get("stage_id").and_then(Value::as_str) == Some(id))
            .ok_or_else(|| format!("missing {id}"))?;
        let details = stage
            .get("details")
            .and_then(Value::as_object)
            .ok_or_else(|| format!("missing {id} details"))?;
        if details.get("replay_equal").and_then(Value::as_bool) != Some(true) {
            return Ok(false);
        }
    }
    Ok(true)
}

fn stage<'a>(stages: &'a [Value], id: &str) -> Result<&'a Map<String, Value>, String> {
    stages
        .iter()
        .find(|stage| stage.get("stage_id").and_then(Value::as_str) == Some(id))
        .ok_or_else(|| format!("missing {id}"))
        .and_then(|stage| object(stage, id))
}

fn observation_matches(
    observation: &Value,
    check_id: &str,
    provider_id: &str,
    expected: &Value,
) -> Result<bool, String> {
    let observation = object(observation, "provider observation")?;
    Ok(string(observation, "check_id")? == check_id
        && string(observation, "provider_id")? == provider_id
        && observation.get("exit_code").and_then(Value::as_i64) == Some(0)
        && observation.get("timed_out").and_then(Value::as_bool) == Some(false)
        && observation.get("matched_expected").and_then(Value::as_bool) == Some(true)
        && observation.get("output") == Some(expected))
}

fn verify_execution_semantics(
    profile: &Map<String, Value>,
    stages: &[Value],
) -> Result<(), String> {
    for id in ["S0", "S1", "S2", "S3", "S4", "S5", "S10"] {
        if string(stage(stages, id)?, "state")? != "passed" {
            return Err(format!("{id} must pass for a producer-complete bundle"));
        }
    }
    let repetitions = unsigned(profile, "repetitions")?;
    let checks = array(profile, "checks")?;
    let mutations = array(profile, "mutations")?;
    let s6 = stage(stages, "S6")?;
    let s6_details = object(s6.get("details").ok_or("S6 details missing")?, "S6 details")?;
    let observations = object(
        s6_details
            .get("observations")
            .ok_or("S6 observations missing")?,
        "S6 observations",
    )?;
    let declared_check_ids: BTreeSet<_> = checks
        .iter()
        .map(|check| {
            object(check, "check").and_then(|check| string(check, "check_id").map(str::to_owned))
        })
        .collect::<Result<_, _>>()?;
    let observed_check_ids: BTreeSet<_> = observations.keys().cloned().collect();
    if observed_check_ids != declared_check_ids {
        return Err("S6 observation denominator mismatch".to_owned());
    }
    let mut positive_passed = true;
    let mut positive_replay_equal = true;
    for check in checks {
        let check = object(check, "check")?;
        let check_id = string(check, "check_id")?;
        let provider_id = string(check, "provider_id")?;
        let expected = check
            .get("expected_output")
            .ok_or("expected_output missing")?;
        let runs = observations
            .get(check_id)
            .and_then(Value::as_array)
            .ok_or_else(|| format!("S6 observations missing for {check_id}"))?;
        if runs.len() != repetitions {
            return Err(format!("S6 repetition denominator mismatch for {check_id}"));
        }
        let mut output_digests = Vec::new();
        for run in runs {
            positive_passed &= observation_matches(run, check_id, provider_id, expected)?;
            output_digests.push(digest(
                run.get("output").ok_or("observation output missing")?,
            )?);
        }
        positive_replay_equal &= output_digests.windows(2).all(|pair| pair[0] == pair[1]);
    }
    positive_passed &= positive_replay_equal;
    if s6_details.get("replay_equal").and_then(Value::as_bool) != Some(positive_replay_equal)
        || string(s6, "state")? != if positive_passed { "passed" } else { "failed" }
    {
        return Err("S6 state does not match independently recomputed observations".to_owned());
    }

    let s7 = stage(stages, "S7")?;
    let s7_details = object(s7.get("details").ok_or("S7 details missing")?, "S7 details")?;
    if unsigned(s7_details, "mutation_denominator")? != mutations.len() {
        return Err("S7 mutation denominator mismatch".to_owned());
    }
    let observed_mutations = array(s7_details, "mutations")?;
    let mut negative_passed = positive_passed && observed_mutations.len() == mutations.len();
    let mut negative_replay_equal = true;
    if positive_passed {
        for mutation in mutations {
            let mutation = object(mutation, "mutation")?;
            let mutant_id = string(mutation, "mutant_id")?;
            let check_id = string(mutation, "check_id")?;
            let declared = observed_mutations
                .iter()
                .find(|candidate| {
                    candidate.get("mutant_id").and_then(Value::as_str) == Some(mutant_id)
                })
                .ok_or_else(|| format!("missing mutation observation: {mutant_id}"))?;
            let declared = object(declared, "mutation observation")?;
            let check = checks
                .iter()
                .find(|check| check.get("check_id").and_then(Value::as_str) == Some(check_id))
                .ok_or_else(|| format!("missing mutation check: {check_id}"))?;
            let check = object(check, "check")?;
            let provider_id = string(check, "provider_id")?;
            let expected = mutation
                .get("expected_output")
                .ok_or("mutation expected_output missing")?;
            let runs = array(declared, "observations")?;
            negative_passed &= string(declared, "check_id")? == check_id
                && string(declared, "expected_rejection_code")?
                    == string(mutation, "expected_rejection_code")?
                && declared
                    .get("killed_for_declared_cause")
                    .and_then(Value::as_bool)
                    == Some(true)
                && runs.len() == repetitions;
            let mut output_digests = Vec::new();
            for run in runs {
                negative_passed &= observation_matches(run, check_id, provider_id, expected)?;
                output_digests.push(digest(run.get("output").ok_or("mutation output missing")?)?);
            }
            negative_replay_equal &= output_digests.windows(2).all(|pair| pair[0] == pair[1]);
        }
    } else if !observed_mutations.is_empty() {
        return Err("S7 executed mutations without a passing S6".to_owned());
    }
    negative_passed &= negative_replay_equal;
    let expected_s7 = if !positive_passed {
        "blocked"
    } else if negative_passed {
        "passed"
    } else {
        "failed"
    };
    if string(s7, "state")? != expected_s7
        || s7_details.get("replay_equal").and_then(Value::as_bool) != Some(negative_replay_equal)
    {
        return Err("S7 state does not match independently recomputed mutations".to_owned());
    }

    let normalized = positive_passed && negative_passed;
    let s8 = stage(stages, "S8")?;
    let s8_details = object(s8.get("details").ok_or("S8 details missing")?, "S8 details")?;
    if string(s8, "state")? != if normalized { "passed" } else { "blocked" }
        || string(s8_details, "normalized_outcome")?
            != if normalized {
                "PASS_BOUNDED"
            } else {
                "NON_PASS"
            }
    {
        return Err("S8 normalization state mismatch".to_owned());
    }

    let composition = object(
        profile.get("composition").ok_or("composition missing")?,
        "composition",
    )?;
    let composition_passed = if !normalized {
        false
    } else if string(composition, "mode")? == "single" {
        true
    } else {
        let fields = array(composition, "compare_fields")?;
        fields.iter().all(|field| {
            field.as_str().is_some_and(|field| {
                let first = checks
                    .first()
                    .and_then(|check| check.get("expected_output"))
                    .and_then(|output| output.get(field));
                first.is_some()
                    && checks.iter().all(|check| {
                        check
                            .get("expected_output")
                            .and_then(|output| output.get(field))
                            == first
                    })
            })
        })
    };
    let expected_s9 = if !normalized {
        "blocked"
    } else if composition_passed {
        "passed"
    } else {
        "failed"
    };
    if string(stage(stages, "S9")?, "state")? != expected_s9 {
        return Err("S9 composition state mismatch".to_owned());
    }
    Ok(())
}

fn verification_receipt(root: &Path, bundle: &Value) -> Result<Value, String> {
    let bundle_object = object(bundle, "bundle")?;
    exact_keys(
        bundle_object,
        &[
            "schema_version",
            "profile",
            "profile_ref",
            "stage_receipts",
            "producer_aggregate_state",
            "denominator",
            "authority_effect",
        ],
        "provisional bundle",
    )?;
    if string(bundle_object, "schema_version")? != "evf.provisional-bundle/v1"
        || string(bundle_object, "authority_effect")? != "none"
    {
        return Err("invalid provisional bundle base contract".to_owned());
    }
    let profile_value = bundle_object.get("profile").ok_or("profile missing")?;
    verify_profile(profile_value)?;
    let profile = object(profile_value, "profile")?;
    verify_denominator(bundle_object, profile)?;
    let profile_ref = bundle_object
        .get("profile_ref")
        .ok_or("profile_ref missing")?;
    verify_ref(root, profile_ref)?;
    let referenced_profile: Value = serde_json::from_slice(
        &fs::read(resolve_ref(root, profile_ref)?).map_err(|error| error.to_string())?,
    )
    .map_err(|error| error.to_string())?;
    if &referenced_profile != profile_value {
        return Err("embedded profile differs from its exact referenced bytes".to_owned());
    }
    let stages = bundle_object
        .get("stage_receipts")
        .and_then(Value::as_array)
        .ok_or("stage_receipts missing")?;
    let mut reasons = Vec::new();
    if let Err(error) = verify_stage_chain(
        stages,
        &PROVISIONAL_STAGE_IDS,
        string(profile, "profile_id")?,
        string(profile, "route")?,
        string(profile, "claim_ceiling")?,
    ) {
        reasons.push(error);
    }
    if let Err(error) = verify_execution_semantics(profile, stages) {
        reasons.push(error);
    }
    let mut ref_errors = Vec::new();
    collect_and_verify_refs(root, bundle, &mut ref_errors);
    reasons.extend(ref_errors.iter().cloned());
    let replay = replay_equal(stages).unwrap_or(false);
    if !replay {
        reasons.push("repeated provider outputs differ".to_owned());
    }
    let recomputed = aggregate_state(stages)?;
    if bundle_object
        .get("producer_aggregate_state")
        .and_then(Value::as_str)
        != Some(recomputed)
    {
        reasons.push("producer aggregate state mismatch".to_owned());
    }
    let reason_codes = if reasons.is_empty() {
        vec![]
    } else {
        vec!["INDEPENDENT_VERIFICATION_FAILED"]
    };
    let mut receipt = json!({
        "schema_version": "evf.verification-receipt/v1",
        "verdict": if reasons.is_empty() { "passed" } else { "failed" },
        "verified_stage_ids": PROVISIONAL_STAGE_IDS,
        "all_refs_current": ref_errors.is_empty(),
        "replay_equal": replay,
        "recomputed_aggregate_state": recomputed,
        "reason_codes": reason_codes,
        "authority_effect": "none",
        "receipt_payload_digest": ""
    });
    let receipt_digest = receipt_digest(&receipt, "receipt_payload_digest")?;
    receipt["receipt_payload_digest"] = Value::String(receipt_digest);
    Ok(receipt)
}

fn verify_final(root: &Path, evidence: &Value) -> Result<Value, String> {
    let aggregate = object(evidence, "aggregate evidence")?;
    exact_keys(
        aggregate,
        &[
            "schema_version",
            "receipt_id",
            "profile_id",
            "route",
            "profile_ref",
            "stage_receipts",
            "aggregate_state",
            "all_required_stages_present",
            "denominator",
            "verification_receipt",
            "evidence_payload_digest",
            "authority_effect",
            "release_admission",
            "claim_ceiling",
        ],
        "aggregate evidence",
    )?;
    if string(aggregate, "schema_version")? != "evf.evolvable-validation-receipt/v1"
        || string(aggregate, "authority_effect")? != "none"
        || string(aggregate, "release_admission")? != "not-granted"
    {
        return Err("invalid aggregate base contract".to_owned());
    }
    let profile_ref = aggregate.get("profile_ref").ok_or("profile_ref missing")?;
    verify_ref(root, profile_ref)?;
    let profile_value: Value = serde_json::from_slice(
        &fs::read(resolve_ref(root, profile_ref)?).map_err(|error| error.to_string())?,
    )
    .map_err(|error| error.to_string())?;
    verify_profile(&profile_value)?;
    let profile = object(&profile_value, "profile")?;
    if string(aggregate, "profile_id")? != string(profile, "profile_id")?
        || string(aggregate, "route")? != string(profile, "route")?
        || string(aggregate, "claim_ceiling")? != string(profile, "claim_ceiling")?
    {
        return Err("aggregate identity differs from its profile".to_owned());
    }
    verify_denominator(aggregate, profile)?;
    if aggregate
        .get("all_required_stages_present")
        .and_then(Value::as_bool)
        != Some(true)
    {
        return Err("aggregate does not declare all required stages".to_owned());
    }
    let stages = aggregate
        .get("stage_receipts")
        .and_then(Value::as_array)
        .ok_or("stage_receipts missing")?;
    verify_stage_chain(
        stages,
        &ALL_STAGE_IDS,
        string(profile, "profile_id")?,
        string(profile, "route")?,
        string(profile, "claim_ceiling")?,
    )?;
    verify_execution_semantics(profile, stages)?;
    let mut ref_errors = Vec::new();
    collect_and_verify_refs(root, evidence, &mut ref_errors);
    if !ref_errors.is_empty() {
        return Err(ref_errors.join("; "));
    }
    let declared = string(aggregate, "evidence_payload_digest")?;
    let actual = receipt_digest(evidence, "evidence_payload_digest")?;
    if declared != actual {
        return Err("aggregate payload digest mismatch".to_owned());
    }
    let recomputed = aggregate_state(stages)?;
    if aggregate.get("aggregate_state").and_then(Value::as_str) != Some(recomputed) {
        return Err("aggregate state mismatch".to_owned());
    }
    let verification = aggregate
        .get("verification_receipt")
        .ok_or("verification receipt missing")?;
    let verification_object = object(verification, "verification receipt")?;
    if string(verification_object, "schema_version")? != "evf.verification-receipt/v1"
        || string(verification_object, "verdict")? != "passed"
        || string(verification_object, "authority_effect")? != "none"
        || !bool_value(verification_object, "all_refs_current")?
        || !bool_value(verification_object, "replay_equal")?
        || string(verification_object, "recomputed_aggregate_state")?
            != aggregate_state(&stages[..PROVISIONAL_STAGE_IDS.len()])?
        || receipt_digest(verification, "receipt_payload_digest")?
            != string(verification_object, "receipt_payload_digest")?
    {
        return Err("embedded independent verification receipt is invalid".to_owned());
    }
    Ok(json!({
        "schema_version": "evf.final-verification-result/v1",
        "verdict": "passed",
        "aggregate_state": recomputed,
        "evidence_payload_digest": declared,
        "verified_stage_ids": ALL_STAGE_IDS,
        "authority_effect": "none"
    }))
}

fn arg(args: &[String], flag: &str) -> Result<PathBuf, String> {
    let index = args
        .iter()
        .position(|value| value == flag)
        .ok_or_else(|| format!("missing {flag}"))?;
    args.get(index + 1)
        .map(PathBuf::from)
        .ok_or_else(|| format!("missing value for {flag}"))
}

fn run() -> Result<Value, String> {
    let args: Vec<String> = env::args().skip(1).collect();
    let root = fs::canonicalize(arg(&args, "--repo-root")?).map_err(|error| error.to_string())?;
    if args.iter().any(|value| value == "--bundle") {
        let bundle = arg(&args, "--bundle")?;
        let value: Value =
            serde_json::from_slice(&fs::read(bundle).map_err(|error| error.to_string())?)
                .map_err(|error| error.to_string())?;
        verification_receipt(&root, &value)
    } else {
        let evidence = arg(&args, "--evidence")?;
        let value: Value =
            serde_json::from_slice(&fs::read(evidence).map_err(|error| error.to_string())?)
                .map_err(|error| error.to_string())?;
        verify_final(&root, &value)
    }
}

fn main() {
    match run() {
        Ok(value) => println!("{}", serde_json::to_string(&value).unwrap()),
        Err(error) => {
            eprintln!(
                "{}",
                serde_json::to_string(&json!({
                    "verdict": "failed",
                    "reason": error,
                    "authority_effect": "none"
                }))
                .unwrap()
            );
            std::process::exit(2);
        }
    }
}
