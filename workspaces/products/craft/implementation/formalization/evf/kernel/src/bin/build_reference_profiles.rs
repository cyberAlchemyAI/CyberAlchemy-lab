use std::collections::BTreeMap;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};

use evf_production_kernel::EvfError;
use evf_production_kernel::execute::validate_profile;
use evf_production_kernel::identity::{canonical_digest, exact_ref, repository_root};
use evf_production_kernel::model::{
    CheckSpec, CompositionSpec, EnforcementProfile, ExactRef, IsolationSpec, MutationSpec,
    ProducerSpec, Route, RuntimeSpec, STAGE_IDS, StageRequirement, VerifierSpec,
};
use serde::Serialize;
use serde_json::{Value, json};

const BASE: &str = "projects/domainspec-v2/development/evolvable-validation-framework/production";

struct Arguments {
    root: PathBuf,
    output: PathBuf,
    candidate_manifest: PathBuf,
    consumer: PathBuf,
    lean: PathBuf,
    souffle: PathBuf,
    unshare: PathBuf,
}

fn value(args: &[String], flag: &str) -> Result<PathBuf, EvfError> {
    let index = args
        .iter()
        .position(|item| item == flag)
        .ok_or_else(|| EvfError::message("ARGUMENT_MISSING", flag))?;
    args.get(index + 1)
        .map(PathBuf::from)
        .ok_or_else(|| EvfError::message("ARGUMENT_VALUE_MISSING", flag))
}

fn arguments() -> Result<Arguments, EvfError> {
    let args: Vec<String> = env::args().skip(1).collect();
    let root = repository_root(&value(&args, "--repo-root")?)?;
    let output = value(&args, "--output-dir")?;
    Ok(Arguments {
        root,
        output,
        candidate_manifest: value(&args, "--candidate-manifest")?,
        consumer: value(&args, "--consumer")?,
        lean: value(&args, "--lean")?,
        souffle: value(&args, "--souffle")?,
        unshare: value(&args, "--unshare")?,
    })
}

fn repo(root: &Path, relative: &str) -> PathBuf {
    root.join(relative)
}

fn reference(root: &Path, relative: &str) -> Result<ExactRef, EvfError> {
    exact_ref(root, &repo(root, relative))
}

fn stages() -> Vec<StageRequirement> {
    STAGE_IDS
        .iter()
        .map(|stage_id| StageRequirement {
            stage_id: (*stage_id).to_owned(),
            required: true,
        })
        .collect()
}

fn environment() -> BTreeMap<String, String> {
    BTreeMap::from([
        ("LANG".to_owned(), "C".to_owned()),
        ("LC_ALL".to_owned(), "C".to_owned()),
    ])
}

fn runtime(
    executable_ref: ExactRef,
    tool_refs: Vec<ExactRef>,
    argv: Vec<String>,
    unshare_ref: ExactRef,
) -> RuntimeSpec {
    RuntimeSpec {
        executable_ref,
        tool_refs,
        argv,
        working_directory: ".".to_owned(),
        environment: environment(),
        timeout_ms: 30_000,
        max_output_bytes: 1_048_576,
        network: "forbidden".to_owned(),
        isolation: IsolationSpec {
            mechanism: "linux-user-and-network-namespace".to_owned(),
            unshare_ref,
        },
    }
}

fn executable_profile(
    root: &Path,
    target: &Path,
    verifier: &Path,
    unshare: &Path,
) -> Result<EnforcementProfile, EvfError> {
    let positive = reference(root, &format!("{BASE}/fixtures/key-door/positive.v1.json"))?;
    let mutant = reference(
        root,
        &format!("{BASE}/fixtures/key-door/mutant-always-allow.v1.json"),
    )?;
    let provider = exact_ref(root, &target.join("evf-provider-key-door"))?;
    Ok(EnforcementProfile {
        schema_version: "evf.enforcement-profile/v1".to_owned(),
        profile_id: "evf.reference.key-door.executable.v1".to_owned(),
        subject: "Reference executable key-door authorization property".to_owned(),
        route: Route::Executable,
        stages: stages(),
        semantic_refs: vec![reference(
            root,
            &format!("{BASE}/fixtures/key-door/source.v1.json"),
        )?],
        obligation_ids: vec!["key-door.allow-only-key-holder".to_owned()],
        obligation_denominator: 1,
        binding_refs: vec![reference(
            root,
            &format!("{BASE}/fixtures/key-door/binding.v1.json"),
        )?],
        checks: vec![CheckSpec {
            check_id: "key-door-positive".to_owned(),
            provider_id: "rust-key-door-runtime".to_owned(),
            runtime: runtime(
                provider,
                vec![],
                vec!["--input".to_owned(), "{input}".to_owned()],
                exact_ref(root, unshare)?,
            ),
            input_ref: positive,
            expected_output: json!({
                "provider_id": "rust-key-door-runtime",
                "native_outcome": "checked",
                "all_cases_match": true,
                "failed_case_ids": []
            }),
        }],
        mutations: vec![MutationSpec {
            mutant_id: "key-door-always-allow".to_owned(),
            check_id: "key-door-positive".to_owned(),
            input_ref: mutant,
            expected_output: json!({
                "provider_id": "rust-key-door-runtime",
                "native_outcome": "checked",
                "all_cases_match": false,
                "failed_case_ids": ["no-key-locked-control"]
            }),
            expected_rejection_code: "UNAUTHORIZED_TRANSITION_SURVIVED".to_owned(),
        }],
        composition: CompositionSpec {
            mode: "single".to_owned(),
            provider_ids: vec!["rust-key-door-runtime".to_owned()],
            compare_fields: vec![],
            comparability_refs: vec![reference(
                root,
                &format!("{BASE}/fixtures/key-door/binding.v1.json"),
            )?],
        },
        producer: ProducerSpec {
            executable_ref: exact_ref(root, &target.join("evf-run"))?,
        },
        verifier: VerifierSpec {
            executable_ref: exact_ref(root, verifier)?,
        },
        repetitions: 2,
        claim_ceiling: "The exact reference executable distinguishes the declared positive and always-allow mutant cases; no production authorization behavior is claimed.".to_owned(),
        authority_effect: "none".to_owned(),
    })
}

fn theorem_profile(
    root: &Path,
    target: &Path,
    verifier: &Path,
    unshare: &Path,
    lean: &Path,
) -> Result<EnforcementProfile, EvfError> {
    let valid_path = repo(
        root,
        "projects/domainspec-v2/formalization/EVFProductionMetaTypeReference.lean",
    );
    let invalid_path = repo(
        root,
        "projects/domainspec-v2/formalization/EVFProductionMetaTypeInvalid.lean",
    );
    let dependency_path = repo(
        root,
        "projects/domainspec-v2/formalization/DomainSpecMetaTypeKernel.lean",
    );
    let binding = reference(root, &format!("{BASE}/fixtures/meta-type/binding.v1.json"))?;
    let lean_ref = exact_ref(root, lean)?;
    let provider = exact_ref(root, &target.join("evf-provider-lean"))?;
    let expected_declaration =
        "DomainSpec.EVFProductionMetaTypeReference.certificate_sound_for_reference";
    let runtime = runtime(
        provider,
        vec![lean_ref, exact_ref(root, &dependency_path)?],
        vec![
            "--input".to_owned(),
            "{input}".to_owned(),
            "--lean".to_owned(),
            fs::canonicalize(lean)
                .map_err(|error| EvfError::new("LEAN_UNAVAILABLE", error))?
                .to_string_lossy()
                .into_owned(),
            "--dependency".to_owned(),
            fs::canonicalize(&dependency_path)
                .map_err(|error| EvfError::new("LEAN_DEPENDENCY_UNAVAILABLE", error))?
                .to_string_lossy()
                .into_owned(),
            "--expected".to_owned(),
            expected_declaration.to_owned(),
        ],
        exact_ref(root, unshare)?,
    );
    Ok(EnforcementProfile {
        schema_version: "evf.enforcement-profile/v1".to_owned(),
        profile_id: "evf.reference.meta-type.theorem.v1".to_owned(),
        subject: "Reference DomainSpec meta-type certificate theorem".to_owned(),
        route: Route::Theorem,
        stages: stages(),
        semantic_refs: vec![exact_ref(root, &valid_path)?],
        obligation_ids: vec!["meta-type.reference-certificate-sound".to_owned()],
        obligation_denominator: 1,
        binding_refs: vec![binding.clone()],
        checks: vec![CheckSpec {
            check_id: "meta-type-theorem-positive".to_owned(),
            provider_id: "lean4-core-typechecker".to_owned(),
            runtime,
            input_ref: exact_ref(root, &valid_path)?,
            expected_output: json!({
                "provider_id": "lean4-core-typechecker",
                "native_outcome": "checked",
                "expected_declaration_present": true
            }),
        }],
        mutations: vec![MutationSpec {
            mutant_id: "meta-type-false-theorem".to_owned(),
            check_id: "meta-type-theorem-positive".to_owned(),
            input_ref: exact_ref(root, &invalid_path)?,
            expected_output: json!({
                "provider_id": "lean4-core-typechecker",
                "native_outcome": "rejected",
                "expected_declaration_present": true
            }),
            expected_rejection_code: "LEAN_FALSE_THEOREM_REJECTED".to_owned(),
        }],
        composition: CompositionSpec {
            mode: "single".to_owned(),
            provider_ids: vec!["lean4-core-typechecker".to_owned()],
            compare_fields: vec![],
            comparability_refs: vec![binding],
        },
        producer: ProducerSpec {
            executable_ref: exact_ref(root, &target.join("evf-run"))?,
        },
        verifier: VerifierSpec {
            executable_ref: exact_ref(root, verifier)?,
        },
        repetitions: 2,
        claim_ceiling: "Lean type-checks the exact reference theorem under its imported model and rejects the exact false control; no runtime or business truth is claimed.".to_owned(),
        authority_effect: "none".to_owned(),
    })
}

fn reachability_profile(
    root: &Path,
    target: &Path,
    verifier: &Path,
    unshare: &Path,
    souffle: &Path,
) -> Result<EnforcementProfile, EvfError> {
    let positive = reference(
        root,
        &format!("{BASE}/fixtures/reachability/facts-positive.v1.json"),
    )?;
    let mutant = reference(
        root,
        &format!("{BASE}/fixtures/reachability/facts-mutant-disconnected.v1.json"),
    )?;
    let program_path = repo(
        root,
        &format!("{BASE}/fixtures/reachability/reachability.v1.dl"),
    );
    let souffle_path =
        fs::canonicalize(souffle).map_err(|error| EvfError::new("SOUFFLE_UNAVAILABLE", error))?;
    let program_absolute = fs::canonicalize(&program_path)
        .map_err(|error| EvfError::new("SOUFFLE_PROGRAM_UNAVAILABLE", error))?;
    let unshare_ref = exact_ref(root, unshare)?;
    let rust_runtime = runtime(
        exact_ref(root, &target.join("evf-provider-reachability-rust"))?,
        vec![],
        vec!["--input".to_owned(), "{input}".to_owned()],
        unshare_ref.clone(),
    );
    let souffle_runtime = runtime(
        exact_ref(root, &target.join("evf-provider-reachability-souffle"))?,
        vec![
            exact_ref(root, &souffle_path)?,
            exact_ref(root, &program_absolute)?,
        ],
        vec![
            "--input".to_owned(),
            "{input}".to_owned(),
            "--souffle".to_owned(),
            souffle_path.to_string_lossy().into_owned(),
            "--program".to_owned(),
            program_absolute.to_string_lossy().into_owned(),
        ],
        unshare_ref,
    );
    let checks = vec![
        CheckSpec {
            check_id: "reachability-rust-positive".to_owned(),
            provider_id: "rust-bfs-reachability".to_owned(),
            runtime: rust_runtime,
            input_ref: positive.clone(),
            expected_output: json!({
                "provider_id": "rust-bfs-reachability",
                "native_outcome": "checked",
                "reachable": true
            }),
        },
        CheckSpec {
            check_id: "reachability-souffle-positive".to_owned(),
            provider_id: "souffle-2.5-reachability".to_owned(),
            runtime: souffle_runtime,
            input_ref: positive,
            expected_output: json!({
                "provider_id": "souffle-2.5-reachability",
                "native_outcome": "checked",
                "reachable": true
            }),
        },
    ];
    let mutations = vec![
        MutationSpec {
            mutant_id: "reachability-rust-disconnected".to_owned(),
            check_id: "reachability-rust-positive".to_owned(),
            input_ref: mutant.clone(),
            expected_output: json!({
                "provider_id": "rust-bfs-reachability",
                "native_outcome": "checked",
                "reachable": false
            }),
            expected_rejection_code: "REACHABILITY_PATH_REMOVED".to_owned(),
        },
        MutationSpec {
            mutant_id: "reachability-souffle-disconnected".to_owned(),
            check_id: "reachability-souffle-positive".to_owned(),
            input_ref: mutant,
            expected_output: json!({
                "provider_id": "souffle-2.5-reachability",
                "native_outcome": "checked",
                "reachable": false
            }),
            expected_rejection_code: "REACHABILITY_PATH_REMOVED".to_owned(),
        },
    ];
    Ok(EnforcementProfile {
        schema_version: "evf.enforcement-profile/v1".to_owned(),
        profile_id: "evf.reference.reachability.multi-provider.v1".to_owned(),
        subject: "Shared-facts reachability agreement across Rust BFS and Souffle".to_owned(),
        route: Route::MultiProvider,
        stages: stages(),
        semantic_refs: vec![reference(
            root,
            &format!("{BASE}/fixtures/reachability/property.v1.json"),
        )?],
        obligation_ids: vec!["reachability.rule-to-payout-event".to_owned()],
        obligation_denominator: 1,
        binding_refs: vec![reference(
            root,
            &format!("{BASE}/fixtures/reachability/binding.v1.json"),
        )?],
        checks,
        mutations,
        composition: CompositionSpec {
            mode: "all_equal".to_owned(),
            provider_ids: vec![
                "rust-bfs-reachability".to_owned(),
                "souffle-2.5-reachability".to_owned(),
            ],
            compare_fields: vec!["reachable".to_owned()],
            comparability_refs: vec![reference(
                root,
                &format!("{BASE}/fixtures/reachability/comparability.v1.json"),
            )?],
        },
        producer: ProducerSpec {
            executable_ref: exact_ref(root, &target.join("evf-run"))?,
        },
        verifier: VerifierSpec {
            executable_ref: exact_ref(root, verifier)?,
        },
        repetitions: 2,
        claim_ceiling: "The two exact providers agree on the reachable field for the exact shared positive facts and reject the exact disconnected controls; no broader graph or runtime authorization claim is made.".to_owned(),
        authority_effect: "none".to_owned(),
    })
}

struct HostileCase<'a> {
    profile_id: &'a str,
    input_name: &'a str,
    timeout_ms: u64,
    max_output_bytes: u64,
    mutation_survives: bool,
}

fn hostile_profile(
    root: &Path,
    target: &Path,
    verifier: &Path,
    unshare: &Path,
    case: HostileCase<'_>,
) -> Result<EnforcementProfile, EvfError> {
    let binding = reference(root, &format!("{BASE}/fixtures/hostile/binding.v1.json"))?;
    let mut hostile_runtime = runtime(
        exact_ref(root, &target.join("evf-provider-hostile-probe"))?,
        vec![],
        vec!["--input".to_owned(), "{input}".to_owned()],
        exact_ref(root, unshare)?,
    );
    hostile_runtime.timeout_ms = case.timeout_ms;
    hostile_runtime.max_output_bytes = case.max_output_bytes;
    let mutation_probe = if case.mutation_survives {
        "survived"
    } else {
        "mutation-killed"
    };
    Ok(EnforcementProfile {
        schema_version: "evf.enforcement-profile/v1".to_owned(),
        profile_id: case.profile_id.to_owned(),
        subject: format!("Hostile provider boundary case {}", case.input_name),
        route: Route::Executable,
        stages: stages(),
        semantic_refs: vec![reference(
            root,
            &format!("{BASE}/fixtures/hostile/source.v1.json"),
        )?],
        obligation_ids: vec!["hostile.provider-boundary".to_owned()],
        obligation_denominator: 1,
        binding_refs: vec![binding.clone()],
        checks: vec![CheckSpec {
            check_id: "hostile-positive".to_owned(),
            provider_id: "rust-hostile-probe".to_owned(),
            runtime: hostile_runtime,
            input_ref: reference(
                root,
                &format!("{BASE}/fixtures/hostile/{}.v1.json", case.input_name),
            )?,
            expected_output: json!({
                "provider_id": "rust-hostile-probe",
                "native_outcome": "checked",
                "probe": "pass",
                "ambient_secret_present": false,
                "network_escape": false
            }),
        }],
        mutations: vec![MutationSpec {
            mutant_id: "hostile-declared-mutation".to_owned(),
            check_id: "hostile-positive".to_owned(),
            input_ref: reference(
                root,
                &format!("{BASE}/fixtures/hostile/mutation.v1.json"),
            )?,
            expected_output: json!({
                "provider_id": "rust-hostile-probe",
                "native_outcome": "checked",
                "probe": mutation_probe,
                "ambient_secret_present": false,
                "network_escape": false
            }),
            expected_rejection_code: "HOSTILE_MUTATION_KILLED".to_owned(),
        }],
        composition: CompositionSpec {
            mode: "single".to_owned(),
            provider_ids: vec!["rust-hostile-probe".to_owned()],
            compare_fields: vec![],
            comparability_refs: vec![binding],
        },
        producer: ProducerSpec {
            executable_ref: exact_ref(root, &target.join("evf-run"))?,
        },
        verifier: VerifierSpec {
            executable_ref: exact_ref(root, verifier)?,
        },
        repetitions: 2,
        claim_ceiling: "This hostile profile establishes only the typed terminal behavior of one exact provider-boundary case under the exact local isolation contract.".to_owned(),
        authority_effect: "none".to_owned(),
    })
}

fn disagreement_profile(
    root: &Path,
    target: &Path,
    verifier: &Path,
    unshare: &Path,
    souffle: &Path,
) -> Result<EnforcementProfile, EvfError> {
    let mut profile = reachability_profile(root, target, verifier, unshare, souffle)?;
    profile.profile_id = "evf.hostile.reachability.provider-disagreement.v1".to_owned();
    profile.subject = "Hostile multi-provider disagreement over exact divergent facts".to_owned();
    profile.checks[1].input_ref = reference(
        root,
        &format!("{BASE}/fixtures/reachability/facts-mutant-disconnected.v1.json"),
    )?;
    profile.checks[1].expected_output = json!({
        "provider_id": "souffle-2.5-reachability",
        "native_outcome": "checked",
        "reachable": false
    });
    profile.claim_ceiling = "This hostile profile establishes only that exact divergent provider results terminate as failed composition rather than an inflated pass.".to_owned();
    Ok(profile)
}

fn write_profile<T: Serialize>(path: &Path, value: &T) -> Result<(), EvfError> {
    let mut bytes = serde_json::to_vec_pretty(value)
        .map_err(|error| EvfError::new("PROFILE_SERIALIZATION_FAILED", error))?;
    bytes.push(b'\n');
    fs::write(path, bytes).map_err(|error| EvfError::new("PROFILE_WRITE_FAILED", error))
}

fn references(root: &Path, paths: &[&str]) -> Result<Vec<ExactRef>, EvfError> {
    paths.iter().map(|path| reference(root, path)).collect()
}

fn build_candidate_manifest(
    args: &Arguments,
    target: &Path,
) -> Result<serde_json::Value, EvfError> {
    let governance = references(
        &args.root,
        &[
            "projects/domainspec-v2/development/evolvable-validation-framework/PRODUCTION-STABILITY-PLAN.md",
            "projects/domainspec-v2/development/evolvable-validation-framework/production-stability-dag.v1-candidate.json",
            "projects/domainspec-v2/development/evolvable-validation-framework/PRODUCTION-STABILITY-DEFINITIONS.v1-candidate.json",
            "projects/domainspec-v2/development/evolvable-validation-framework/decisions/2026-09-03-production-stability/DECISION-GATE.md",
            "projects/domainspec-v2/development/evolvable-validation-framework/decisions/2026-09-03-production-stability/SELECTION.json",
        ],
    )?;
    let contracts = references(
        &args.root,
        &[
            "projects/domainspec-v2/development/evolvable-validation-framework/contracts/evolvable-validation-receipt.v1.schema.json",
            "projects/domainspec-v2/development/evolvable-validation-framework/contracts/evf-stage-receipt.v1.schema.json",
            "projects/domainspec-v2/development/evolvable-validation-framework/contracts/evf-verification-receipt.v1.schema.json",
            "projects/domainspec-v2/development/evolvable-validation-framework/contracts/evf-enforcement-profile.v1.schema.json",
            "projects/domainspec-v2/development/evolvable-validation-framework/contracts/evf-product-candidate-manifest.v1.schema.json",
            "projects/domainspec-v2/development/evolvable-validation-framework/contracts/legacy/evolvable-validation-receipt.v1.key-door.preimage-ref.json",
        ],
    )?;
    let ontology = references(
        &args.root,
        &[
            "projects/domainspec-v2/development/evolvable-validation-framework/ontology/production-stability-scaffold.v1-candidate.json",
        ],
    )?;
    let implementation = references(
        &args.root,
        &[
            &format!("{BASE}/rust/Cargo.toml"),
            &format!("{BASE}/rust/Cargo.lock"),
            &format!("{BASE}/rust/kernel/Cargo.toml"),
            &format!("{BASE}/rust/kernel/src/lib.rs"),
            &format!("{BASE}/rust/kernel/src/model.rs"),
            &format!("{BASE}/rust/kernel/src/identity.rs"),
            &format!("{BASE}/rust/kernel/src/store.rs"),
            &format!("{BASE}/rust/kernel/src/execute.rs"),
            &format!("{BASE}/rust/kernel/src/bin/evf_run.rs"),
            &format!("{BASE}/rust/kernel/src/bin/build_reference_profiles.rs"),
            &format!("{BASE}/rust/kernel/tests/contracts.rs"),
            &format!("{BASE}/rust/providers/Cargo.toml"),
            &format!("{BASE}/rust/providers/src/bin/key_door.rs"),
            &format!("{BASE}/rust/providers/src/bin/hostile_probe.rs"),
            &format!("{BASE}/rust/providers/src/bin/lean.rs"),
            &format!("{BASE}/rust/providers/src/bin/reachability_rust.rs"),
            &format!("{BASE}/rust/providers/src/bin/reachability_souffle.rs"),
            &format!("{BASE}/rust/verifier/Cargo.toml"),
            &format!("{BASE}/rust/verifier/src/main.rs"),
        ],
    )?;
    let profiles = references(
        &args.root,
        &[
            &format!("{BASE}/profiles/key-door-executable.v1.json"),
            &format!("{BASE}/profiles/meta-type-theorem.v1.json"),
            &format!("{BASE}/profiles/reachability-multi-provider.v1.json"),
            &format!("{BASE}/profiles/hostile-isolation-pass.v1.json"),
            &format!("{BASE}/profiles/hostile-timeout.v1.json"),
            &format!("{BASE}/profiles/hostile-oversized-output.v1.json"),
            &format!("{BASE}/profiles/hostile-malformed-output.v1.json"),
            &format!("{BASE}/profiles/hostile-nonzero-exit.v1.json"),
            &format!("{BASE}/profiles/hostile-surviving-mutant.v1.json"),
            &format!("{BASE}/profiles/hostile-provider-disagreement.v1.json"),
        ],
    )?;
    let fixtures = references(
        &args.root,
        &[
            &format!("{BASE}/fixtures/key-door/source.v1.json"),
            &format!("{BASE}/fixtures/key-door/binding.v1.json"),
            &format!("{BASE}/fixtures/key-door/positive.v1.json"),
            &format!("{BASE}/fixtures/key-door/mutant-always-allow.v1.json"),
            &format!("{BASE}/fixtures/hostile/source.v1.json"),
            &format!("{BASE}/fixtures/hostile/binding.v1.json"),
            &format!("{BASE}/fixtures/hostile/pass.v1.json"),
            &format!("{BASE}/fixtures/hostile/mutation.v1.json"),
            &format!("{BASE}/fixtures/hostile/timeout.v1.json"),
            &format!("{BASE}/fixtures/hostile/oversized.v1.json"),
            &format!("{BASE}/fixtures/hostile/malformed.v1.json"),
            &format!("{BASE}/fixtures/hostile/nonzero.v1.json"),
            &format!("{BASE}/fixtures/meta-type/binding.v1.json"),
            &format!("{BASE}/fixtures/reachability/property.v1.json"),
            &format!("{BASE}/fixtures/reachability/binding.v1.json"),
            &format!("{BASE}/fixtures/reachability/comparability.v1.json"),
            &format!("{BASE}/fixtures/reachability/facts-positive.v1.json"),
            &format!("{BASE}/fixtures/reachability/facts-mutant-disconnected.v1.json"),
            &format!("{BASE}/fixtures/reachability/reachability.v1.dl"),
        ],
    )?;
    let formalization = references(
        &args.root,
        &[
            "projects/domainspec-v2/formalization/DomainSpecMetaTypeKernel.lean",
            "projects/domainspec-v2/formalization/EVFProductionMetaTypeReference.lean",
            "projects/domainspec-v2/formalization/EVFProductionMetaTypeInvalid.lean",
        ],
    )?;
    let consumer = references(
        &args.root,
        &[
            "projects/domainspec-v2/development/evf-reference-consumer/README.md",
            "projects/domainspec-v2/development/evf-reference-consumer/rust/Cargo.toml",
            "projects/domainspec-v2/development/evf-reference-consumer/rust/Cargo.lock",
            "projects/domainspec-v2/development/evf-reference-consumer/rust/src/main.rs",
        ],
    )?;
    let selection = reference(
        &args.root,
        "projects/domainspec-v2/development/evolvable-validation-framework/decisions/2026-09-03-production-stability/SELECTION.json",
    )?;
    let runtime_refs = vec![
        exact_ref(&args.root, &target.join("evf-run"))?,
        exact_ref(&args.root, &target.join("evf-independent-verifier"))?,
        exact_ref(&args.root, &target.join("evf-provider-key-door"))?,
        exact_ref(&args.root, &target.join("evf-provider-hostile-probe"))?,
        exact_ref(&args.root, &target.join("evf-provider-lean"))?,
        exact_ref(&args.root, &target.join("evf-provider-reachability-rust"))?,
        exact_ref(
            &args.root,
            &target.join("evf-provider-reachability-souffle"),
        )?,
        exact_ref(&args.root, &args.consumer)?,
        exact_ref(&args.root, &args.lean)?,
        exact_ref(&args.root, &args.souffle)?,
        exact_ref(&args.root, &args.unshare)?,
    ];
    let mut manifest = json!({
        "schema_version": "evf.product-candidate-manifest/v1",
        "candidate_id": "evf.production-stability.reference.v3-candidate",
        "selected_decisions": {
            "EVF-DEC-001": "B",
            "EVF-DEC-002": "A",
            "EVF-DEC-003": "C",
            "selection_ref": selection
        },
        "artifact_groups": {
            "governance": governance,
            "contracts": contracts,
            "ontology": ontology,
            "implementation": implementation,
            "profiles": profiles,
            "fixtures": fixtures,
            "formalization": formalization,
            "consumer": consumer
        },
        "runtime_refs": runtime_refs,
        "candidate_payload_digest": "",
        "claim_ceiling": "This immutable manifest identifies one locally built EVF production-stability candidate and its exact test dependencies. It grants no product approval, adoption, enforcement, authorization, publication, release, or deployment authority.",
        "authority_effect": "none"
    });
    let mut digest_payload = manifest.clone();
    digest_payload
        .as_object_mut()
        .expect("candidate manifest object")
        .remove("candidate_payload_digest");
    manifest["candidate_payload_digest"] = Value::String(canonical_digest(&digest_payload)?);
    Ok(manifest)
}

fn run() -> Result<(), EvfError> {
    let args = arguments()?;
    fs::create_dir_all(&args.output)
        .map_err(|error| EvfError::new("PROFILE_OUTPUT_CREATE_FAILED", error))?;
    let target = repo(&args.root, &format!("{BASE}/rust/target/debug"));
    let verifier = target.join("evf-independent-verifier");
    let profiles = vec![
        (
            "key-door-executable.v1.json",
            executable_profile(&args.root, &target, &verifier, &args.unshare)?,
        ),
        (
            "meta-type-theorem.v1.json",
            theorem_profile(&args.root, &target, &verifier, &args.unshare, &args.lean)?,
        ),
        (
            "reachability-multi-provider.v1.json",
            reachability_profile(&args.root, &target, &verifier, &args.unshare, &args.souffle)?,
        ),
        (
            "hostile-isolation-pass.v1.json",
            hostile_profile(
                &args.root,
                &target,
                &verifier,
                &args.unshare,
                HostileCase {
                    profile_id: "evf.hostile.isolation-pass.v1",
                    input_name: "pass",
                    timeout_ms: 1_000,
                    max_output_bytes: 1_024,
                    mutation_survives: false,
                },
            )?,
        ),
        (
            "hostile-timeout.v1.json",
            hostile_profile(
                &args.root,
                &target,
                &verifier,
                &args.unshare,
                HostileCase {
                    profile_id: "evf.hostile.timeout.v1",
                    input_name: "timeout",
                    timeout_ms: 50,
                    max_output_bytes: 1_024,
                    mutation_survives: false,
                },
            )?,
        ),
        (
            "hostile-oversized-output.v1.json",
            hostile_profile(
                &args.root,
                &target,
                &verifier,
                &args.unshare,
                HostileCase {
                    profile_id: "evf.hostile.oversized-output.v1",
                    input_name: "oversized",
                    timeout_ms: 1_000,
                    max_output_bytes: 256,
                    mutation_survives: false,
                },
            )?,
        ),
        (
            "hostile-malformed-output.v1.json",
            hostile_profile(
                &args.root,
                &target,
                &verifier,
                &args.unshare,
                HostileCase {
                    profile_id: "evf.hostile.malformed-output.v1",
                    input_name: "malformed",
                    timeout_ms: 1_000,
                    max_output_bytes: 1_024,
                    mutation_survives: false,
                },
            )?,
        ),
        (
            "hostile-nonzero-exit.v1.json",
            hostile_profile(
                &args.root,
                &target,
                &verifier,
                &args.unshare,
                HostileCase {
                    profile_id: "evf.hostile.nonzero-exit.v1",
                    input_name: "nonzero",
                    timeout_ms: 1_000,
                    max_output_bytes: 1_024,
                    mutation_survives: false,
                },
            )?,
        ),
        (
            "hostile-surviving-mutant.v1.json",
            hostile_profile(
                &args.root,
                &target,
                &verifier,
                &args.unshare,
                HostileCase {
                    profile_id: "evf.hostile.surviving-mutant.v1",
                    input_name: "pass",
                    timeout_ms: 1_000,
                    max_output_bytes: 1_024,
                    mutation_survives: true,
                },
            )?,
        ),
        (
            "hostile-provider-disagreement.v1.json",
            disagreement_profile(&args.root, &target, &verifier, &args.unshare, &args.souffle)?,
        ),
    ];
    for (name, profile) in profiles {
        validate_profile(&profile)?;
        write_profile(&args.output.join(name), &profile)?;
    }
    if let Some(parent) = args.candidate_manifest.parent() {
        fs::create_dir_all(parent)
            .map_err(|error| EvfError::new("CANDIDATE_OUTPUT_CREATE_FAILED", error))?;
    }
    let manifest = build_candidate_manifest(&args, &target)?;
    write_profile(&args.candidate_manifest, &manifest)?;
    println!(
        "{}",
        serde_json::to_string(&json!({
            "status": "profiles-generated",
            "count": 10,
            "output_dir": args.output,
            "candidate_manifest": args.candidate_manifest,
            "candidate_payload_digest": manifest["candidate_payload_digest"],
            "authority_effect": "none"
        }))
        .unwrap()
    );
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("{}: {}", error.code, error.message);
        std::process::exit(2);
    }
}
