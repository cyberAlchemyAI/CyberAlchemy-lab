use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::{SystemTime, UNIX_EPOCH};

pub mod w3;
pub mod w4;
pub mod remaining_types;

#[derive(Debug)]
pub struct RuleProofError(pub &'static str);

fn sha256(bytes: impl AsRef<[u8]>) -> String {
    format!("{:x}", Sha256::digest(bytes.as_ref()))
}

fn document_digest(value: &Value, field: &str) -> Result<String, RuleProofError> {
    let mut body = value.clone();
    body.as_object_mut()
        .ok_or(RuleProofError("RUST_RULE_JSON_SCHEMA_INVALID"))?
        .remove(field);
    Ok(sha256(serde_json::to_vec(&body).map_err(|_| RuleProofError("RUST_RULE_JSON_INVALID"))?))
}

pub fn inspect_source(source: &str) -> Result<(), RuleProofError> {
    let forbidden = ["macro_rules!", "include!", "env!", "option_env!", "#[", "extern crate", "mod ", "use "];
    if forbidden.iter().any(|token| source.contains(token)) {
        return Err(RuleProofError("RUST_RULE_MACRO_OR_GENERATION_UNSUPPORTED"));
    }
    if source.matches("pub fn ").count() != 1
        || !source.contains("pub fn can_settle_payout(input: &CanSettlePayoutInput<'_>) -> bool")
        || !source.contains("input.amount > 0 && input.existing_settlement_id == None")
        || source.contains("unsafe")
    {
        return Err(RuleProofError("RUST_RULE_ITEM_SUBSET_UNSUPPORTED"));
    }
    Ok(())
}

pub fn mutate_source(source: &str, defect: &str) -> Result<String, RuleProofError> {
    inspect_source(source)?;
    let expression = "input.amount > 0 && input.existing_settlement_id == None";
    let replacement = match defect {
        "wrong-result" => "false && input.existing_settlement_id == None".to_string(),
        "bypass-check" => "input.amount > 0".to_string(),
        "observable-effect" => format!(
            "if {expression} {{ EFFECT_COUNT.fetch_add(1, std::sync::atomic::Ordering::SeqCst); true }} else {{ false }}"
        ),
        _ => return Err(RuleProofError("RUST_RULE_MUTATION_UNKNOWN")),
    };
    if source.matches(expression).count() != 1 {
        return Err(RuleProofError("RUST_RULE_MUTATION_NOT_APPLICABLE"));
    }
    Ok(source.replacen(expression, &replacement, 1))
}

#[derive(Debug, Clone)]
struct Case {
    id: String,
    request_id: String,
    amount: i64,
    existing: Option<String>,
    expected: bool,
}

#[derive(Debug)]
struct Observation {
    outcome: bool,
    effects: u64,
}

fn parse_cases(value: &Value) -> Result<Vec<Case>, RuleProofError> {
    value["cases"].as_array().ok_or(RuleProofError("RUST_RULE_CASES_INVALID"))?
        .iter().map(|item| Ok(Case {
            id: item["case_id"].as_str().ok_or(RuleProofError("RUST_RULE_CASE_INVALID"))?.to_string(),
            request_id: item["input"]["requestId"].as_str().ok_or(RuleProofError("RUST_RULE_CASE_INVALID"))?.to_string(),
            amount: item["input"]["amount"].as_i64().ok_or(RuleProofError("RUST_RULE_CASE_INVALID"))?,
            existing: item["input"]["existingSettlementId"].as_str().map(str::to_string),
            expected: item["expected_outcome"].as_bool().ok_or(RuleProofError("RUST_RULE_CASE_INVALID"))?,
        })).collect()
}

fn rust_string(value: &str) -> String {
    format!("{value:?}")
}

fn rustc_path() -> Result<String, RuleProofError> {
    let resolved = Command::new("rustup").args(["which", "rustc"]).output()
        .map_err(|_| RuleProofError("RUST_RULE_COMPILER_MISSING"))?;
    if !resolved.status.success() {
        return Err(RuleProofError("RUST_RULE_COMPILER_MISSING"));
    }
    let path = String::from_utf8(resolved.stdout)
        .map_err(|_| RuleProofError("RUST_RULE_COMPILER_MISSING"))?;
    Ok(path.trim().to_string())
}

fn execute_source(source: &str, cases: &[Case]) -> Result<BTreeMap<String, Observation>, RuleProofError> {
    let nonce = SystemTime::now().duration_since(UNIX_EPOCH)
        .map_err(|_| RuleProofError("RUST_RULE_CLOCK_INVALID"))?.as_nanos();
    let workspace = std::env::temp_dir().join(format!("domainspec-rule-rust-{}-{nonce}", std::process::id()));
    fs::create_dir(&workspace).map_err(|_| RuleProofError("RUST_RULE_WORKSPACE_FAILED"))?;
    let result = (|| {
        let mut harness = String::from(source);
        harness.push_str("\nstatic EFFECT_COUNT: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);\nfn main() {\n");
        for case in cases {
            let existing = case.existing.as_ref()
                .map(|value| format!("Some({})", rust_string(value)))
                .unwrap_or_else(|| "None".to_string());
            harness.push_str(&format!(
                "EFFECT_COUNT.store(0, std::sync::atomic::Ordering::SeqCst); let input = CanSettlePayoutInput {{ request_id: {}, amount: {}, existing_settlement_id: {} }}; let outcome = can_settle_payout(&input); println!(\"{}|{{}}|{{}}\", outcome, EFFECT_COUNT.load(std::sync::atomic::Ordering::SeqCst));\n",
                rust_string(&case.request_id), case.amount, existing, case.id,
            ));
        }
        harness.push_str("}\n");
        let source_path = workspace.join("candidate.rs");
        let binary_path = workspace.join("candidate");
        fs::write(&source_path, harness).map_err(|_| RuleProofError("RUST_RULE_WORKSPACE_FAILED"))?;
        let compiler = rustc_path()?;
        let compiled = Command::new(&compiler)
            .args(["--edition=2021", "-C", "opt-level=0", "-o"])
            .arg(&binary_path).arg(&source_path)
            .env_clear()
            .env("PATH", std::env::var_os("PATH").unwrap_or_default())
            .output().map_err(|_| RuleProofError("RUST_RULE_COMPILER_MISSING"))?;
        if !compiled.status.success() {
            return Err(RuleProofError("RUST_RULE_COMPILE_FAILED"));
        }
        let executed = Command::new(&binary_path).env_clear().output()
            .map_err(|_| RuleProofError("RUST_RULE_RUNTIME_FAILED"))?;
        if !executed.status.success() {
            return Err(RuleProofError("RUST_RULE_RUNTIME_FAILED"));
        }
        let stdout = String::from_utf8(executed.stdout).map_err(|_| RuleProofError("RUST_RULE_RUNTIME_OUTPUT_INVALID"))?;
        let mut observations = BTreeMap::new();
        for line in stdout.lines() {
            let fields: Vec<_> = line.split('|').collect();
            if fields.len() != 3 {
                return Err(RuleProofError("RUST_RULE_RUNTIME_OUTPUT_INVALID"));
            }
            observations.insert(fields[0].to_string(), Observation {
                outcome: fields[1] == "true",
                effects: fields[2].parse().map_err(|_| RuleProofError("RUST_RULE_RUNTIME_OUTPUT_INVALID"))?,
            });
        }
        Ok(observations)
    })();
    fs::remove_dir_all(&workspace).map_err(|_| RuleProofError("RUST_RULE_WORKSPACE_CLEANUP_FAILED"))?;
    result
}

fn read_json(path: &Path) -> Result<Value, RuleProofError> {
    serde_json::from_slice(&fs::read(path).map_err(|_| RuleProofError("RUST_RULE_INPUT_MISSING"))?)
        .map_err(|_| RuleProofError("RUST_RULE_JSON_INVALID"))
}

fn exact_rule_ref(definition: &Value) -> Value {
    json!({
        "definition_sha256": definition["definition_sha256"],
        "rule_id": definition["rule_id"],
    })
}

pub fn build_proof(root: &Path) -> Result<Value, RuleProofError> {
    let common = root.join("projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout");
    let target = root.join("projects/domainspec-v2/impl/architecture-conformance/targets/rust/fixtures");
    let definition = read_json(&common.join("rule-definition.json"))?;
    let cases_json = read_json(&common.join("cases.json"))?;
    let obligations = read_json(&common.join("obligations.json"))?;
    let mutants = read_json(&common.join("mutants.json"))?;
    let binding = read_json(&target.join("rust-binding.json"))?;
    for (value, field) in [
        (&definition, "definition_sha256"), (&cases_json, "catalogue_sha256"),
        (&obligations, "catalogue_sha256"), (&mutants, "catalogue_sha256"),
        (&binding, "binding_sha256"),
    ] {
        if document_digest(value, field)? != value[field].as_str().ok_or(RuleProofError("RUST_RULE_DIGEST_INVALID"))? {
            return Err(RuleProofError("RUST_RULE_DIGEST_STALE"));
        }
    }
    let rule_ref = exact_rule_ref(&definition);
    if cases_json["rule_ref"] != rule_ref || obligations["rule_ref"] != rule_ref
        || mutants["rule_ref"] != rule_ref || binding["rule_ref"] != rule_ref
        || obligations["case_catalogue_sha256"] != cases_json["catalogue_sha256"]
        || binding["target_id"] != "rust" || binding["current"] != true
    {
        return Err(RuleProofError("RUST_RULE_BINDING_STALE"));
    }
    let source_path = root.join(binding["source_ref"]["path"].as_str().ok_or(RuleProofError("RUST_RULE_SOURCE_REF_INVALID"))?);
    let source_bytes = fs::read(&source_path).map_err(|_| RuleProofError("RUST_RULE_SOURCE_MISSING"))?;
    if sha256(&source_bytes) != binding["source_ref"]["sha256"].as_str().ok_or(RuleProofError("RUST_RULE_SOURCE_REF_INVALID"))? {
        return Err(RuleProofError("RUST_RULE_SOURCE_STALE"));
    }
    let source = String::from_utf8(source_bytes).map_err(|_| RuleProofError("RUST_RULE_SOURCE_ENCODING_INVALID"))?;
    inspect_source(&source)?;
    let cases = parse_cases(&cases_json)?;
    let positive_observations = execute_source(&source, &cases)?;
    let normalized_observations: Vec<Value> = cases.iter().map(|case| {
        let item = positive_observations.get(&case.id);
        json!({
            "case_id": case.id,
            "outcome": item.map(|value| value.outcome),
            "observed_effect_count": item.map(|value| value.effects),
        })
    }).collect();
    let positives: Vec<Value> = cases.iter().map(|case| {
        let passed = positive_observations.get(&case.id)
            .map(|item| item.outcome == case.expected && item.effects == 0).unwrap_or(false);
        json!({"case_id": case.id, "status": if passed { "passed" } else { "failed" }})
    }).collect();
    let obligation_items = obligations["obligations"].as_array().ok_or(RuleProofError("RUST_RULE_OBLIGATIONS_INVALID"))?;
    let mut mutation_results = Vec::new();
    for mutant in mutants["mutations"].as_array().ok_or(RuleProofError("RUST_RULE_MUTANTS_INVALID"))? {
        let defect = mutant["defect"].as_str().ok_or(RuleProofError("RUST_RULE_MUTANT_INVALID"))?;
        let mutated = mutate_source(&source, defect)?;
        let observed = execute_source(&mutated, &cases)?;
        let mut findings = Vec::new();
        for obligation in obligation_items {
            let Some(kind) = obligation["kind"].as_str() else { return Err(RuleProofError("RUST_RULE_OBLIGATION_INVALID")); };
            if kind == "binding-current" { continue; }
            let case_id = obligation["case_id"].as_str().ok_or(RuleProofError("RUST_RULE_OBLIGATION_INVALID"))?;
            let item = observed.get(case_id).ok_or(RuleProofError("RUST_RULE_OBSERVATION_INCOMPLETE"))?;
            if kind == "case-outcome-exact" && item.outcome != obligation["expected_outcome"].as_bool().ok_or(RuleProofError("RUST_RULE_OBLIGATION_INVALID"))? {
                findings.push(("RULE_OUTCOME_MISMATCH", case_id));
            } else if kind == "effect-free" && item.effects != 0 {
                findings.push(("RULE_EFFECT_OBSERVED", case_id));
            }
        }
        findings.sort();
        findings.dedup();
        let expected_code = mutant["expected_finding_code"].as_str().ok_or(RuleProofError("RUST_RULE_MUTANT_INVALID"))?;
        let expected_case = mutant["case_id"].as_str().ok_or(RuleProofError("RUST_RULE_MUTANT_INVALID"))?;
        let killed = findings == vec![(expected_code, expected_case)];
        mutation_results.push(json!({
            "mutation_id": mutant["mutation_id"],
            "case_id": mutant["case_id"],
            "finding_code": if killed { Value::String(expected_code.to_string()) } else { Value::Null },
            "status": if killed { "killed" } else { "survived" },
        }));
    }
    let passed = positives.iter().filter(|item| item["status"] == "passed").count();
    let killed = mutation_results.iter().filter(|item| item["status"] == "killed").count();
    let summary = json!({
        "schema_version": "RuleProofSummary/v1",
        "rule_id": definition["rule_id"],
        "target_id": "rust",
        "realization_id": binding["realization_id"],
        "positive": positives,
        "mutations": mutation_results,
        "accounting": {
            "result": if passed == cases.len() && killed == 3 { "pass" } else { "block" },
            "positive": {"declared": cases.len(), "passed": passed, "failed": cases.len() - passed, "unaccounted": 0},
            "mutations": {"declared": 3, "killed": killed, "survived": 3 - killed, "unaccounted": 0},
        },
        "claim_ceiling": "one candidate-local handwritten Rust Rule in the admitted macro-free function subset",
        "authority_effect": "none",
    });
    if summary["accounting"]["result"] != "pass" {
        return Err(RuleProofError("RUST_RULE_PROOF_ACCOUNTING_BLOCKED"));
    }
    let rustc = Command::new("rustc").arg("--version").output().map_err(|_| RuleProofError("RUST_RULE_COMPILER_MISSING"))?;
    Ok(json!({
        "summary_sha256": sha256(serde_json::to_vec(&summary).map_err(|_| RuleProofError("RUST_RULE_JSON_INVALID"))?),
        "summary": summary,
        "static": {"subset": "macro-free-item-use-v1", "supported": true, "source_sha256": binding["source_ref"]["sha256"]},
        "runtime": {"isolated_workspace": true, "cleaned": true, "symlinks": false, "observations": normalized_observations},
        "toolchain": {"rustc": String::from_utf8_lossy(&rustc.stdout).trim()},
        "authority_effect": "none",
    }))
}

pub fn repository_root_from_manifest() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).ancestors().nth(6).unwrap().to_path_buf()
}
