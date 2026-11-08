#!/usr/bin/env node
import {createHash} from "node:crypto";
import {lstatSync, readFileSync} from "node:fs";
import {resolve} from "node:path";
import {pathToFileURL} from "node:url";

const defaultCandidateRoot = import.meta.dirname;
const defaultExtensionRoot = resolve(defaultCandidateRoot, "..");
const defaultRepositoryRoot = resolve(defaultExtensionRoot, "../../../../../../..");
const sha256 = (path) => createHash("sha256").update(readFileSync(path)).digest("hex");
const readJson = (path) => JSON.parse(readFileSync(path, "utf8"));

export function validateModulePortGovernanceCandidate({
  candidateRoot = defaultCandidateRoot,
  extensionRoot = defaultExtensionRoot,
  repositoryRoot = defaultRepositoryRoot,
} = {}) {
  const checks = [];
  const check = (checkId, condition, detail) => checks.push({check_id: checkId,
    outcome: condition ? "PASS" : "BLOCK", ...(detail ? {detail} : {})});
  let manifest;
  let compatibility;
  let degraded;
  let ownership;
  let evidence;
  let product;
  let adoption;
  let admission;
  let bindingEvidence;
  let bindingAdmission;
  let operationalAuthorization;
  let activation;
  let cutoverEvidence;
  let packagedVerifierEvidence;
  let signedEnvelopeEvidence;
  let constitution;
  try {
    manifest = readJson(resolve(candidateRoot, "manifest.json"));
    compatibility = readJson(resolve(candidateRoot, "compatibility-retirement-policy.json"));
    degraded = readJson(resolve(candidateRoot, "degraded-mode-policy.json"));
    ownership = readJson(resolve(candidateRoot, "ownership-boundaries.json"));
    evidence = readJson(resolve(candidateRoot, "conformance-evidence.json"));
    product = readJson(resolve(candidateRoot, "product-approval-request.json"));
    adoption = readJson(resolve(candidateRoot, "adoption-request.json"));
    admission = readJson(resolve(candidateRoot, "runtime-admission-request.json"));
    bindingEvidence = readJson(resolve(candidateRoot, "rust-binding-conformance.json"));
    bindingAdmission = readJson(resolve(candidateRoot, "rust-binding-admission-request.json"));
    operationalAuthorization = readJson(resolve(candidateRoot, "operational-authorization.json"));
    activation = readJson(resolve(candidateRoot, "activation-request.json"));
    cutoverEvidence = readJson(resolve(candidateRoot, "cutover-realization-evidence.json"));
    packagedVerifierEvidence = readJson(resolve(candidateRoot, "packaged-verifier-evidence.json"));
    signedEnvelopeEvidence = readJson(resolve(candidateRoot, "signed-distribution-envelope-evidence.json"));
    constitution = readFileSync(resolve(candidateRoot, "MODULE-PORT-CONSTITUTION.md"), "utf8");
  } catch (error) {
    return {schema_version: "are.module-port-governance-validation/v1", overall: "BLOCK",
      checks: [{check_id: "candidate-files-readable", outcome: "BLOCK", detail: error.message}],
      product_approved: false, constitution_adopted: false, runtime_admitted: false,
      enforcement_active: false, governed_conformance_status: "not_evaluable", authority_effect: "none"};
  }

  for (const row of manifest.candidate_files ?? []) {
    let observed = null;
    try { observed = sha256(resolve(candidateRoot, row.path)); } catch {}
    check(`digest:candidate:${row.path}`, observed === row.sha256, `expected ${row.sha256}; observed ${observed}`);
  }
  for (const row of manifest.dependency_files ?? []) {
    const base = row.base === "extension" ? extensionRoot : repositoryRoot;
    let observed = null;
    try { observed = sha256(resolve(base, row.path)); } catch {}
    check(`digest:${row.base}:${row.path}`, observed === row.sha256, `expected ${row.sha256}; observed ${observed}`);
  }

  let alchSource = "";
  try { alchSource = readFileSync(resolve(extensionRoot, "module-port.alch"), "utf8"); } catch {}
  check("alch-constitution-id", /constitution-ref "ARE-MODULE-PORT-CONSTITUTION-CANDIDATE"/.test(alchSource));
  check("alch-constitution-candidate", /status candidate/.test(alchSource) && /adopted false/.test(alchSource));
  check("alch-authority-none", /authority-effect none/.test(alchSource));

  check("constitution-status", constitution.includes("Status: candidate"));
  check("constitution-selector", constitution.includes("Selectors: `profile:semantic-contract-v1/domain:are-module-port`"));
  for (let index = 1; index <= 8; index += 1) check(`constitution-rule-ARE-MPC-${index}`,
    constitution.includes(`ARE-MPC-${index}.`));

  check("compatibility-exact", compatibility.identity_basis === "exact-alch-source-compiled-manifest-implementation-and-adapter-manifests");
  check("compatibility-new-version", compatibility.breaking_change_action === "issue-new-contract-version-or-separate-architecture");
  check("compatibility-no-silent", compatibility.silent_compatibility_assumption === false);
  check("compatibility-retirement", compatibility.retirement_triggers.length >= 6);
  check("compatibility-authority-none", compatibility.constitution_adopted === false && compatibility.authority_effect === "none");

  check("degraded-no-partial-port", degraded.configuration_failure_posture === "complete-module-set-unavailable-no-partial-port"
    && degraded.partial_composition_allowed === false);
  check("degraded-no-fallback", degraded.silent_fallback_allowed === false && degraded.host_reimplementation_allowed === false);
  check("degraded-no-hot-reload", degraded.hot_reload_allowed === false);
  check("degraded-not-enforced", degraded.implemented_as_governance_enforcement === false
    && degraded.constitution_adopted === false && degraded.runtime_admitted === false);

  check("ownership-complete", ownership.owners.length === 5 && ownership.conflicts.length === 0);
  check("ownership-no-transfer", ownership.forbidden_transfers.length >= 5);
  check("ownership-authority-none", ownership.review_status === "candidate-unselected" && ownership.authority_effect === "none");

  check("evidence-local-pass", evidence.local_validation_status === "PASS"
    && evidence.validation_runs.every((row) => row.status === "PASS" && row.failed === 0));
  check("evidence-product-review-only", evidence.product_approval_request_eligible === true
    && evidence.product_approved === false);
  check("governed-conformance-not-evaluable", evidence.governed_conformance_status === "not_evaluable"
    && evidence.conformance_blockers.length >= 5);
  check("evidence-no-authority", evidence.constitution_adopted === false && evidence.runtime_admitted === false
    && evidence.enforcement_active === false && evidence.effect_authorized === false && evidence.authority_effect === "none");

  check("product-approved-exactly", product.decision_state === "selected"
    && product.selected_option_id === "ARE-MP-PRODUCT-APPROVE" && product.product_approved === true
    && product.selection_source?.kind === "explicit-current-user-decision"
    && product.selection_source?.raw_request === "approved"
    && product.selection_source?.request_id === "approve-l3-product-002");
  check("product-exact-evidence", product.conformance_evidence_sha256 === sha256(resolve(candidateRoot, "conformance-evidence.json")));
  check("product-option-closure", JSON.stringify(product.options.map((row) => row.option_id))
    === JSON.stringify(["ARE-MP-PRODUCT-APPROVE", "ARE-MP-PRODUCT-DEFER", "ARE-MP-PRODUCT-REJECT"]));
  check("product-grants-no-authority", product.constitution_adopted === false && product.runtime_admitted === false
    && product.effect_authorized === false && product.authority_effect === "none");

  check("adoption-selected-exactly", adoption.decision_state === "selected"
    && adoption.selected_option_id === "ARE-MPC-ADOPT"
    && adoption.product_approved === true && adoption.constitution_adopted === true
    && adoption.selection_source?.kind === "explicit-current-user-decision"
    && adoption.selection_source?.raw_request === "adopt"
    && adoption.selection_source?.request_id === "adopt-module-port-constitution-003"
    && adoption.selection_source?.effect_digest === "2f09bca1b1da1c2d1577a14f6b550bdc2bd45563c5f9b3799753f1d060deeb37");
  check("adoption-exact-candidate", adoption.constitution_sha256 === sha256(resolve(candidateRoot, "MODULE-PORT-CONSTITUTION.md"))
    && adoption.compatibility_policy_sha256 === sha256(resolve(candidateRoot, "compatibility-retirement-policy.json"))
    && adoption.degraded_mode_policy_sha256 === sha256(resolve(candidateRoot, "degraded-mode-policy.json"))
    && adoption.ownership_boundaries_sha256 === sha256(resolve(candidateRoot, "ownership-boundaries.json"))
    && adoption.conformance_evidence_sha256 === sha256(resolve(candidateRoot, "conformance-evidence.json")));
  check("adoption-grants-no-runtime-authority", adoption.runtime_admitted === false
    && adoption.effect_authorized === false && adoption.authority_effect === "none");
  let runtimeEvidence = null;
  let runtimeConfigurationDigest = null;
  let runtimeEvidenceDigest = null;
  try { runtimeEvidence = readJson(resolve(extensionRoot, admission.conformance_evidence_ref)); } catch {}
  try { runtimeConfigurationDigest = sha256(resolve(extensionRoot, admission.subject_configuration_ref)); } catch {}
  try { runtimeEvidenceDigest = sha256(resolve(extensionRoot, admission.conformance_evidence_ref)); } catch {}
  check("admission-selected-exactly", admission.decision_state === "selected"
    && admission.selected_option_id === "ARE-MP-RUNTIME-ADMIT"
    && admission.selection_source?.kind === "explicit-current-user-decision"
    && admission.selection_source?.raw_request === "admited"
    && admission.selection_source?.request_id === "admit-module-port-runtime-005"
    && admission.selection_source?.effect_digest === "2273bb7c59efb5988c32d58b7a065303e1d77cf0d41822d5f850bbd70eae9bc3"
    && admission.reference_base === "module-port-extension-root"
    && admission.subject_configuration_digest === runtimeConfigurationDigest
    && admission.conformance_evidence_sha256 === runtimeEvidenceDigest
    && runtimeEvidence?.status === "PASS" && runtimeEvidence?.runtime_admitted === false
    && admission.product_approved === true && admission.constitution_adopted === true
    && JSON.stringify(admission.satisfied_prerequisites) === JSON.stringify(admission.prerequisites)
    && admission.blocking_prerequisites.length === 0);
  check("admission-option-closure", JSON.stringify(admission.options.map((row) => row.option_id))
    === JSON.stringify(["ARE-MP-RUNTIME-ADMIT", "ARE-MP-RUNTIME-DEFER", "ARE-MP-RUNTIME-REJECT"]));
  check("admission-grants-no-activation", admission.runtime_admitted === true
    && admission.enforcement_active === false && admission.effect_authorized === false
    && admission.authority_effect === "none");

  check("rust-binding-evidence-pass", bindingEvidence.binding_id === "ARE-MODULE-PORT-RUST-BINDING-001-CANDIDATE"
    && bindingEvidence.validation?.status === "PASS" && bindingEvidence.validation?.passed === 6
    && bindingEvidence.validation?.failed === 0 && bindingEvidence.candidate_execution?.disposition === "PASS"
    && bindingEvidence.binding_admission_request_eligible === true);
  check("rust-binding-source-digests", bindingEvidence.source_files.every((row) => {
    let observed = null;
    try { observed = sha256(resolve(repositoryRoot, row.path)); } catch {}
    return observed === row.sha256;
  }));
  check("rust-binding-input-closure", JSON.stringify(bindingEvidence.bound_inputs.map((row) => row.sha256))
    === JSON.stringify([
      sha256(resolve(candidateRoot, "MODULE-PORT-CONSTITUTION.md")),
      sha256(resolve(candidateRoot, "adoption-request.json")),
      sha256(resolve(candidateRoot, "runtime-admission-request.json")),
      runtimeConfigurationDigest,
      runtimeEvidenceDigest,
      sha256(resolve(repositoryRoot, "implementation/agent-reasoning-engine/packages/module-port/alch-semantic-adapter.mjs")),
    ]));
  check("rust-binding-evidence-no-authority", bindingEvidence.binding_admitted === false
    && bindingEvidence.enforcement_active === false && bindingEvidence.effect_authorized === false
    && bindingEvidence.authority_effect === "none");
  check("rust-binding-admission-selected-exactly", bindingAdmission.decision_state === "selected"
    && bindingAdmission.decision_id === "ARE-MODULE-PORT-RUST-BINDING-ADMISSION-001"
    && bindingAdmission.subject_binding_id === bindingEvidence.binding_id
    && bindingAdmission.conformance_evidence_sha256 === sha256(resolve(candidateRoot, "rust-binding-conformance.json"))
    && bindingAdmission.subject_configuration_sha256 === runtimeConfigurationDigest
    && bindingAdmission.selected_option_id === "ARE-MP-RUST-BINDING-ADMIT"
    && bindingAdmission.selection_source?.kind === "explicit-current-user-decision"
    && bindingAdmission.selection_source?.raw_request === "admited"
    && bindingAdmission.selection_source?.request_id === "admit-module-port-rust-binding-007"
    && bindingAdmission.selection_source?.request_digest === "aa70880b2f1ecf53f33592ec85343184ac1292a74b1f02787a098cf1e4289dd5"
    && bindingAdmission.selection_source?.effect_digest === "3e70e4f314bfd24c389d64a4dfde6c571d71dc53798480be736f189f0f40bf6e"
    && bindingAdmission.blocking_prerequisites.length === 0);
  check("rust-binding-admission-source-digests", bindingAdmission.subject_files.every((row) => {
    let observed = null;
    try { observed = sha256(resolve(repositoryRoot, row.path)); } catch {}
    return observed === row.sha256;
  }));
  check("rust-binding-admission-option-closure", JSON.stringify(bindingAdmission.options.map((row) => row.option_id))
    === JSON.stringify(["ARE-MP-RUST-BINDING-ADMIT", "ARE-MP-RUST-BINDING-DEFER", "ARE-MP-RUST-BINDING-REJECT"]));
  check("rust-binding-admission-grants-no-enforcement", bindingAdmission.runtime_admitted === true
    && bindingAdmission.binding_admitted === true && bindingAdmission.enforcement_active === false
    && bindingAdmission.effect_authorized === false && bindingAdmission.authority_effect === "none");

  check("operational-authorization-selected-exactly", operationalAuthorization.decision_state === "selected"
    && operationalAuthorization.decision_id === "ARE-MODULE-PORT-OPERATIONAL-AUTHORIZATION-001"
    && operationalAuthorization.subject_runtime_admission_decision_id === admission.decision_id
    && operationalAuthorization.subject_runtime_admission_sha256 === sha256(resolve(candidateRoot, "runtime-admission-request.json"))
    && operationalAuthorization.subject_binding_admission_decision_id === bindingAdmission.decision_id
    && operationalAuthorization.subject_binding_admission_sha256 === sha256(resolve(candidateRoot, "rust-binding-admission-request.json"))
    && operationalAuthorization.subject_configuration_sha256 === runtimeConfigurationDigest
    && operationalAuthorization.authorized_scope === "make-the-exact-admitted-subject-eligible-for-a-separate-activation-decision"
    && operationalAuthorization.selected_option_id === "ARE-MP-OPERATION-AUTHORIZE"
    && operationalAuthorization.selection_source?.kind === "explicit-current-user-decision"
    && operationalAuthorization.selection_source?.raw_request === "so authorized"
    && operationalAuthorization.selection_source?.request_id === "authorize-module-port-operation-011"
    && operationalAuthorization.selection_source?.request_digest === "31326738281c1187335a7fd633e2ad9ea8c118d4ba18949926217278569b2f63"
    && operationalAuthorization.selection_source?.effect_digest === "8bcf2b3bbab86afb91b601c123c28370b35e0918ce1e4d6af311089c79d546dc"
    && JSON.stringify(operationalAuthorization.satisfied_prerequisites) === JSON.stringify(operationalAuthorization.prerequisites)
    && operationalAuthorization.blocking_prerequisites.length === 0);
  check("operational-authorization-option-closure", JSON.stringify(operationalAuthorization.options.map((row) => row.option_id))
    === JSON.stringify(["ARE-MP-OPERATION-AUTHORIZE", "ARE-MP-OPERATION-DEFER", "ARE-MP-OPERATION-REJECT"]));
  check("operational-authorization-grants-no-activation", operationalAuthorization.operational_authorized === true
    && operationalAuthorization.activation_eligible === true && operationalAuthorization.activation_selected === false
    && operationalAuthorization.enforcement_active === false && operationalAuthorization.effect_authorized === false
    && operationalAuthorization.authority_effect === "none");

  check("activation-prerequisites-satisfied", activation.subject_configuration_digest === admission.subject_configuration_digest
    && activation.subject_binding_admission_decision_id === bindingAdmission.decision_id
    && activation.subject_operational_authorization_decision_id === operationalAuthorization.decision_id
    && activation.satisfied_prerequisites.includes("runtime admission selected for exact configuration")
    && activation.satisfied_prerequisites.includes("exact Rust governance binding admission selected")
    && activation.satisfied_prerequisites.includes("separate operational authorization")
    && JSON.stringify(activation.satisfied_prerequisites) === JSON.stringify(activation.prerequisites)
    && activation.blocking_prerequisites.length === 0);
  check("activation-option-closure", JSON.stringify(activation.options.map((row) => row.option_id))
    === JSON.stringify(["ARE-MP-ACTIVATE", "ARE-MP-ACTIVATION-DEFER", "ARE-MP-ACTIVATION-REJECT"]));
  check("activation-selected-exactly", activation.decision_state === "selected-active"
    && activation.selected_option_id === "ARE-MP-ACTIVATE"
    && activation.selection_source?.kind === "explicit-current-user-decision"
    && activation.selection_source?.raw_request === "do it"
    && activation.selection_source?.request_id === "activate-module-port-012"
    && activation.selection_source?.request_digest === "0dab87bc01e413ab06bf36da2ae02ab5305f5de349e681defbf89250660708c1"
    && activation.selection_source?.effect_digest === "55e9b3777208eb31ec3cf17e2b2241d8562431e48216821012d823df482671ae"
    && activation.runtime_admitted === true
    && activation.operational_authorized === true && activation.activation_eligible === true
    && activation.activation_selected === true);
  check("activation-realized-without-effect-authority", activation.cutover_completed === true
    && activation.enforcement_active === true && activation.effect_authorized === false
    && activation.authority_effect === "none");

  check("cutover-evidence-exact-subject", cutoverEvidence.status === "PASS"
    && cutoverEvidence.subject_activation_decision_id === activation.decision_id
    && cutoverEvidence.subject_activation_sha256 === sha256(resolve(candidateRoot, "activation-request.json"))
    && cutoverEvidence.subject_configuration_id === activation.subject_configuration_id
    && cutoverEvidence.subject_configuration_sha256 === runtimeConfigurationDigest
    && cutoverEvidence.module_set_digest === "f87d8f92824c2b1fab2635742f71d630ce3121c155b509fa13ce4fe0c6e1a926");
  check("cutover-alch-compiled", cutoverEvidence.alch_contract?.fixture_status === "PASS"
    && cutoverEvidence.alch_contract?.fixture_passed === 4
    && cutoverEvidence.alch_contract?.fixture_failed === 0
    && cutoverEvidence.alch_contract?.source_sha256 === sha256(resolve(repositoryRoot, cutoverEvidence.alch_contract.source_path))
    && cutoverEvidence.alch_contract?.compiled_manifest_sha256 === sha256(resolve(repositoryRoot, cutoverEvidence.alch_contract.compiled_manifest_path)));
  check("cutover-source-digests", cutoverEvidence.source_files.every((row) => {
    let observed = null;
    try { observed = sha256(resolve(repositoryRoot, row.path)); } catch {}
    return observed === row.sha256;
  }));
  check("cutover-validation-pass", cutoverEvidence.validation_runs.length >= 2
    && cutoverEvidence.validation_runs.every((row) => row.status === "PASS" && row.failed === 0)
    && cutoverEvidence.runtime_receipt?.disposition === "active"
    && /^[0-9a-f]{64}$/.test(cutoverEvidence.runtime_receipt?.rust_receipt_digest ?? "")
    && /^[0-9a-f]{64}$/.test(cutoverEvidence.runtime_receipt?.composition_digest ?? "")
    && /^[0-9a-f]{64}$/.test(cutoverEvidence.runtime_receipt?.cutover_receipt_digest ?? "")
    && cutoverEvidence.runtime_receipt?.verifier_delivery === "packaged-artifact"
    && cutoverEvidence.runtime_receipt?.verifier_artifact_id === packagedVerifierEvidence.artifact_id
    && cutoverEvidence.runtime_receipt?.verifier_artifact_sha256 === packagedVerifierEvidence.binary.sha256);
  check("cutover-grants-no-effects", cutoverEvidence.activation_selected === true
    && cutoverEvidence.cutover_completed === true && cutoverEvidence.enforcement_active === true
    && cutoverEvidence.effect_authorized === false && cutoverEvidence.authority_effect === "none");

  let artifactManifest = null;
  let artifactMetadata = null;
  try { artifactManifest = readJson(resolve(repositoryRoot, packagedVerifierEvidence.artifact_manifest.path)); } catch {}
  try { artifactMetadata = lstatSync(resolve(repositoryRoot, packagedVerifierEvidence.binary.path)); } catch {}
  check("packaged-verifier-exact-subject", packagedVerifierEvidence.status === "PASS"
    && packagedVerifierEvidence.artifact_id === "ARE-MODULE-PORT-PACKAGED-VERIFIER-LINUX-X64-001-CANDIDATE"
    && packagedVerifierEvidence.binding_id === bindingEvidence.binding_id
    && packagedVerifierEvidence.platform === "linux" && packagedVerifierEvidence.architecture === "x64"
    && packagedVerifierEvidence.target_triple === "x86_64-unknown-linux-gnu");
  check("packaged-verifier-alch-compiled", packagedVerifierEvidence.alch_contract?.fixture_status === "PASS"
    && packagedVerifierEvidence.alch_contract?.fixture_passed === 4
    && packagedVerifierEvidence.alch_contract?.fixture_failed === 0
    && packagedVerifierEvidence.alch_contract?.source_sha256 === sha256(resolve(repositoryRoot, packagedVerifierEvidence.alch_contract.source_path))
    && packagedVerifierEvidence.alch_contract?.compiled_manifest_sha256 === sha256(resolve(repositoryRoot, packagedVerifierEvidence.alch_contract.compiled_manifest_path)));
  check("packaged-verifier-builder-bound", packagedVerifierEvidence.builder?.sha256
    === sha256(resolve(repositoryRoot, packagedVerifierEvidence.builder.path)));
  check("packaged-verifier-manifest-bound", packagedVerifierEvidence.artifact_manifest?.sha256
    === sha256(resolve(repositoryRoot, packagedVerifierEvidence.artifact_manifest.path))
    && artifactManifest?.artifact_id === packagedVerifierEvidence.artifact_id
    && artifactManifest?.binding_id === packagedVerifierEvidence.binding_id
    && artifactManifest?.binary_path === packagedVerifierEvidence.binary.path
    && artifactManifest?.binary_sha256 === packagedVerifierEvidence.binary.sha256
    && artifactManifest?.binary_size === packagedVerifierEvidence.binary.size
    && artifactManifest?.source_files.every((row) => sha256(resolve(repositoryRoot, row.path)) === row.sha256));
  check("packaged-verifier-binary-bound", packagedVerifierEvidence.binary?.sha256
    === sha256(resolve(repositoryRoot, packagedVerifierEvidence.binary.path))
    && artifactMetadata?.isFile() === true && artifactMetadata?.isSymbolicLink() === false
    && `0${(artifactMetadata?.mode & 0o777).toString(8)}` === packagedVerifierEvidence.binary.mode);
  check("packaged-verifier-validation-pass", packagedVerifierEvidence.validation_runs.length === 3
    && packagedVerifierEvidence.validation_runs.every((row) => row.status === "PASS")
    && packagedVerifierEvidence.validation_runs[0].artifact_digest_distinct_count === 1
    && packagedVerifierEvidence.validation_runs[0].manifest_digest_distinct_count === 1
    && packagedVerifierEvidence.validation_runs[1].passed === 9
    && packagedVerifierEvidence.validation_runs[1].failed === 0
    && packagedVerifierEvidence.validation_runs[2].route === "CA2-ROUTE-UNDERSTAND"
    && packagedVerifierEvidence.validation_runs[2].module_set_digest === "f87d8f92824c2b1fab2635742f71d630ce3121c155b509fa13ce4fe0c6e1a926");
  check("packaged-verifier-no-runtime-toolchain-or-effects", packagedVerifierEvidence.runtime_compiler_required === false
    && packagedVerifierEvidence.runtime_package_manager_required === false
    && packagedVerifierEvidence.fallback_allowed === false
    && packagedVerifierEvidence.installed_externally === false
    && packagedVerifierEvidence.published === false && packagedVerifierEvidence.released === false
    && packagedVerifierEvidence.deployed === false && packagedVerifierEvidence.effect_authorized === false
    && packagedVerifierEvidence.authority_effect === "none");

  let distributionDecision = null;
  let distributionBundle = null;
  let distributionSignature = null;
  try { distributionDecision = readJson(resolve(repositoryRoot, signedEnvelopeEvidence.decision.path)); } catch {}
  try { distributionBundle = readJson(resolve(repositoryRoot, signedEnvelopeEvidence.bundle_manifest.path)); } catch {}
  try { distributionSignature = readJson(resolve(repositoryRoot, signedEnvelopeEvidence.signature.path)); } catch {}
  check("signed-envelope-exact-selection", signedEnvelopeEvidence.status === "PASS"
    && signedEnvelopeEvidence.envelope_id === "ARE-MODULE-PORT-DISTRIBUTION-ENVELOPE-LINUX-X64-001-CANDIDATE"
    && signedEnvelopeEvidence.artifact_id === packagedVerifierEvidence.artifact_id
    && signedEnvelopeEvidence.platform === "linux" && signedEnvelopeEvidence.architecture === "x64"
    && signedEnvelopeEvidence.decision.sha256 === sha256(resolve(repositoryRoot, signedEnvelopeEvidence.decision.path))
    && distributionDecision?.decision_state === "selected"
    && distributionDecision?.selected_option_id === "signed-distribution-envelope"
    && distributionDecision?.selection_source?.raw_request === "1"
    && distributionDecision?.selection_source?.request_id === "implement-signed-envelope-018"
    && distributionDecision?.effect_authorized === false && distributionDecision?.authority_effect === "none");
  check("signed-envelope-alch-compiled", signedEnvelopeEvidence.alch_contract?.fixture_status === "PASS"
    && signedEnvelopeEvidence.alch_contract?.fixture_passed === 4
    && signedEnvelopeEvidence.alch_contract?.fixture_failed === 0
    && signedEnvelopeEvidence.alch_contract?.source_sha256 === sha256(resolve(repositoryRoot, signedEnvelopeEvidence.alch_contract.source_path))
    && signedEnvelopeEvidence.alch_contract?.compiled_manifest_sha256 === sha256(resolve(repositoryRoot, signedEnvelopeEvidence.alch_contract.compiled_manifest_path)));
  check("signed-envelope-source-digests", signedEnvelopeEvidence.source_files.every((row) => {
    let observed = null;
    try { observed = sha256(resolve(repositoryRoot, row.path)); } catch {}
    return observed === row.sha256;
  }));
  check("signed-envelope-bytes-bound", signedEnvelopeEvidence.bundle_manifest.sha256
    === sha256(resolve(repositoryRoot, signedEnvelopeEvidence.bundle_manifest.path))
    && signedEnvelopeEvidence.signature.sha256 === sha256(resolve(repositoryRoot, signedEnvelopeEvidence.signature.path))
    && distributionBundle?.envelope_id === signedEnvelopeEvidence.envelope_id
    && distributionBundle?.artifact_id === signedEnvelopeEvidence.artifact_id
    && distributionBundle?.release_eligible === false && distributionBundle?.effect_authorized === false
    && distributionSignature?.envelope_id === signedEnvelopeEvidence.envelope_id
    && distributionSignature?.payload_sha256 === signedEnvelopeEvidence.bundle_manifest.sha256
    && distributionSignature?.key_id === signedEnvelopeEvidence.signature.key_id
    && distributionSignature?.trust_posture === "test-only-deterministic-fixture"
    && distributionSignature?.release_eligible === false && distributionSignature?.effect_authorized === false);
  check("signed-envelope-verification-pass", signedEnvelopeEvidence.validation_runs.length === 3
    && signedEnvelopeEvidence.validation_runs.every((row) => row.status === "PASS" && row.failed === 0)
    && signedEnvelopeEvidence.validation_runs[0].passed === 4
    && signedEnvelopeEvidence.validation_runs[1].passed === 9
    && signedEnvelopeEvidence.validation_runs[2].passed === 807
    && signedEnvelopeEvidence.verification_receipt?.disposition === "verified-local-candidate"
    && signedEnvelopeEvidence.verification_receipt?.signature_verified === true
    && signedEnvelopeEvidence.verification_receipt?.bundle_sha256 === signedEnvelopeEvidence.bundle_manifest.sha256
    && signedEnvelopeEvidence.verification_receipt?.signature_sha256 === signedEnvelopeEvidence.signature.sha256
    && /^[0-9a-f]{64}$/.test(signedEnvelopeEvidence.verification_receipt?.receipt_digest ?? ""));
  check("signed-envelope-no-release-or-effects", signedEnvelopeEvidence.offline_verification === true
    && signedEnvelopeEvidence.private_release_key_present === false
    && signedEnvelopeEvidence.signature.trust_posture === "test-only-deterministic-fixture"
    && signedEnvelopeEvidence.release_eligible === false && signedEnvelopeEvidence.published === false
    && signedEnvelopeEvidence.installed_externally === false && signedEnvelopeEvidence.deployed === false
    && signedEnvelopeEvidence.effect_authorized === false && signedEnvelopeEvidence.authority_effect === "none");

  check("manifest-state-ceiling", manifest.decision_state === "signed-envelope-candidate-verified-local"
    && manifest.product_approved === true && manifest.constitution_adopted === true
    && manifest.runtime_admitted === true && manifest.binding_admitted === true
    && manifest.operational_authorized === true && manifest.activation_eligible === true
    && manifest.activation_selected === true && manifest.cutover_completed === true
    && manifest.enforcement_active === true && manifest.effect_authorized === false
    && manifest.authority_effect === "none");
  const blocked = checks.filter((row) => row.outcome === "BLOCK").length;
  return {schema_version: "are.module-port-governance-validation/v1", candidate_id: manifest.candidate_id,
    overall: blocked === 0 ? "PASS" : "BLOCK", checks,
    local_validation_status: blocked === 0 ? "PASS" : "BLOCK",
    governed_conformance_status: "not_evaluable", product_approved: true,
    constitution_adopted: true, runtime_admitted: true, binding_admitted: true,
    operational_authorized: true, activation_eligible: true, activation_selected: true,
    cutover_completed: blocked === 0, enforcement_active: blocked === 0,
    distribution_envelope_verified: blocked === 0, release_eligible: false,
    published: false, installed_externally: false, deployed: false, effect_authorized: false,
    authority_effect: "none"};
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const result = validateModulePortGovernanceCandidate();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  process.exitCode = result.overall === "PASS" ? 0 : 1;
}
