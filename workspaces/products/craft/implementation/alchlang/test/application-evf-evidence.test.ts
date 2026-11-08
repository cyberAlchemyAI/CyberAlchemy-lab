import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { assertApplicationEvfEvidenceCurrent, joinApplicationEvfEvidence, type ApplicationEvfCausalOutcome, type ApplicationEvfRouteKind } from "../src/application-evf-evidence.js";
import { lowerApplicationVerificationProfiles } from "../src/application-verification-profile.js";
import { finalizeApplicationExecutionRequest } from "../src/application-execution-request.js";
import { projectApplicationFormalClaimsToV2 } from "../src/formal-claim-v2-projection.js";
import { formalLoweringFixture, source as formalSource } from "./fixtures/formal-lowering-fixture.js";

const sha = (bytes: string | Buffer) => createHash("sha256").update(bytes).digest("hex");
const outcomes: ApplicationEvfCausalOutcome[] = ["pass", "fail", "unknown", "timeout", "malformed", "stale", "unavailable", "not-evaluable"];
const routes: ApplicationEvfRouteKind[] = ["execution-evidence", "theorem-evidence"];
const expected = {
  pass: ["PASS_BOUNDED", "passed", "passed"], fail: ["NON_PASS", "failed", "failed"],
  unknown: ["INDETERMINATE", "indeterminate", "indeterminate"], timeout: ["FAILED", "timeout", "timeout"],
  malformed: ["FAILED", "malformed", "provider-error"], stale: ["STALE", "stale", "stale"],
  unavailable: ["MISSING", "blocked", "blocked"], "not-evaluable": ["UNSUPPORTED", "unsupported", "blocked"],
} as const;

const profileBody = `
verification-profile EligibleVerification:
  claim EligibleClaim
  context EvaluationContext:eligible-evf version 1
  interpretation none
  route route:tde-execution
  provider provider:fixture
  runtime runtime:fixture
  timeout-ms 5000
  memory-ceiling-bytes 268435456
  max-output-bytes 1048576
  network forbidden
  working-directory sandbox/verification
  limit "Synthetic E03 fixture only."
  ceiling "Synthetic formal evidence only."
`;

function evidenceFixture(route: ApplicationEvfRouteKind, outcome: ApplicationEvfCausalOutcome, runtimeProviderId = "provider:fixture", extraCase = false, profileProviderId = "provider:fixture") {
  const fixture = formalLoweringFixture(); const source = formalSource + profileBody;
  const put = fixture.put;
  const routeRef = put("fixture/route.json", { route_id: "route:tde-execution" });
  const providerProfileRef = put("fixture/provider.json", {
    provider_owner: "fixture-provider-owner", provider_id: profileProviderId, provider_version: "1",
  });
  const runtimeRef = put("fixture/runtime.json", {
    schema_version: "domainspec-v2.provider-runtime-binding/v1-candidate", runtime_binding_id: "runtime:fixture",
    provider_owner: "fixture-provider-owner", provider_id: runtimeProviderId, provider_version: "1",
    provider_digest: sha("synthetic-provider"), profile_ref: providerProfileRef, input_artifact_ref: routeRef,
    command: ["fixture-provider"], working_directory: "sandbox/verification", environment_allowlist: [], fixture_refs: [],
    limits: { timeout_ms: 5000, memory_ceiling_bytes: 268435456, max_output_bytes: 1048576 },
    network: "forbidden", supported_outcomes: ["passed", "failed"], currentness: "current",
    authority_effect: "none", claim_ceiling: "runtime-binding-only-no-execution-claim",
  });
  const formalInput = { ...fixture.input, source_sha256: sha(source) };
  const verificationInput = { schema_version: "alchlang.verification-profile-bindings/v1", source_sha256: sha(source), owner: "fixture-owner",
    formal: formalInput, verification_profiles: { EligibleVerification: { interpretation: null,
      route: { selector: "route:tde-execution", ref: routeRef }, provider: { selector: "provider:fixture", ref: providerProfileRef },
      runtime: { selector: "runtime:fixture", ref: runtimeRef } } } };
  const verification = lowerApplicationVerificationProfiles(source, verificationInput, fixture.sources);
  const projection = projectApplicationFormalClaimsToV2(source, formalInput, fixture.sources);
  for (const [path, bytes] of Object.entries({ ...verification.formal.files, ...verification.files, ...projection.files })) fixture.sources.set(path, Buffer.from(bytes));
  const verificationTrace = verification.trace.declarations[0]! as any;
  const projectionTrace = projection.trace.declarations[0]! as any;
  const capabilityPolicyRef = put("fixture/capability-policy.json", { policy_id: "synthetic-capability-policy" });
  const capabilityRef = put("fixture/capability.json", {
    schema_version: "domainspec-v2.formal-claim-capability-assessment/v1-candidate", assessment_id: "fixture-capability",
    owner: "validation-governance", formal_claim_ref: verificationTrace.claim_ref, policy_ref: capabilityPolicyRef,
    classification: "executable-bounded", needs_formal_reasons: [], admitted_for_tde_execution: true,
    provider_route: "tde", currentness: "current", authority_effect: "none",
    claim_ceiling: "classification-and-routing-only-no-execution-claim",
  });
  const environmentRef = put("fixture/environment.json", { environment_id: "fixture-environment", route });
  const common: any = { schema_version: "alchlang.evf-evidence-input/v1", join_id: `fixture-${route}-${outcome}`, route_kind: route,
    provider: { owner: "fixture-provider-owner", id: route === "theorem-evidence" ? "lean" : "provider:fixture", version: "1" },
    causal_outcome: outcome, cause: `synthetic ${outcome} observation`,
    comparability: { same_claim: true, same_evaluation_request: true, same_domain: true, same_result_semantics: true },
    result_semantics: route === "theorem-evidence" ? "theorem in exact synthetic Lean model" : "synthetic provider result",
    claim_ceiling: "Synthetic E03 fixture only." };
  let finalizedScope: Record<string, unknown> | undefined;
  let caseResults: Record<string, unknown>[] | undefined;
  if (route === "execution-evidence") {
    let obligationSetRef: any = put("fixture/obligation-set.json", { obligations: ["fixture-obligation"] });
    let projectionRef: any = projectionTrace.target_ref;
    let preservationRef: any = projectionTrace.preservation_binding_ref;
    if (outcome === "pass") {
      const acceptedContextRef = put("fixture/accepted-evaluation-context.json", { ...verification.contexts[0], status: "accepted" });
      const baseRequestRef = put("fixture/accepted-base-request.json", { ...verification.requests[0], evaluation_context_ref: acceptedContextRef });
      const derivationProfileRef = put("fixture/derivation-profile.json", { profile_id: "synthetic-TDE" });
      obligationSetRef = put("fixture/finalized-obligation-set.json", {
        schema_version: "domainspec-v2.neutral-obligation-set/v1-candidate", obligation_set_id: "fixture-set", owner: "TDE",
        formal_claim_ref: verificationTrace.claim_ref,
        capability_assessment_ref: { path: capabilityRef.path, sha256: capabilityRef.sha256, size_bytes: capabilityRef.size_bytes },
        projection_ref: null,
        derivation_profile_ref: derivationProfileRef, derivation_status: "derived",
        obligations: [{ obligation_id: "fixture-obligation", case_id: "fixture-case", kind: "property",
          normalized_inputs: { order: "one" }, expected_relation_or_oracle: "holds", source_basis: ["FormalClaim:fixture"],
          case_class: "positive", status: "ready", claim_ceiling: "Synthetic E03 fixture only." },
          ...(extraCase ? [{ obligation_id: "fixture-obligation-2", case_id: "fixture-case-2", kind: "boundary",
            normalized_inputs: { order: "two" }, expected_relation_or_oracle: "holds", source_basis: ["FormalClaim:fixture"],
            case_class: "boundary", status: "ready", claim_ceiling: "Synthetic E03 fixture only." }] : [])],
        residue: [], determinism: { algorithm_ref: derivationProfileRef, input_digest: sha("input"), output_digest: sha("output") },
        authority_effect: "none", claim_ceiling: "Synthetic E03 fixture only.",
      });
      projectionRef = put("fixture/finalized-projection.json", {
        schema_version: "domainspec-v2.formalization-projection/v1-candidate", projection_id: "fixture-projection",
        owner: "projects/domainspec-v2/formalization", formal_claim_ref: verificationTrace.claim_ref,
        capability_assessment_ref: capabilityRef, obligation_set_ref: obligationSetRef,
        purpose: "tde-executable-slice", target_profile_ref: derivationProfileRef,
        source_semantics_digest: sha("source"), projected_semantics_digest: sha("projected"),
        domain_and_bound: extraCase ? "two finite synthetic cases" : "one finite synthetic case", preservation_kind: "exact-equivalent",
        currentness: "current", authority_effect: "none", claim_ceiling: "Synthetic E03 fixture only.",
      });
      preservationRef = put("fixture/finalized-preservation.json", {
        schema_version: "domainspec-v2.preservation-binding/v1-candidate", binding_id: "fixture-preservation",
        owner: "projects/domainspec-v2/formalization", projection_ref: { path: projectionRef.path, sha256: projectionRef.sha256,
          size_bytes: projectionRef.size_bytes }, direction: "bidirectional",
        kind: "review-backed", preserved_semantics: ["synthetic finite case"], known_losses: [], unsupported_constructs: [],
        validation_method: "synthetic fixture", certificate_ref: null, status: "preserved",
        authority_effect: "none", claim_ceiling: "Synthetic E03 fixture only.",
      });
      const finalized = finalizeApplicationExecutionRequest({ base_request_ref: baseRequestRef, obligation_set_ref: obligationSetRef,
        projection_ref: projectionRef, preservation_binding_ref: preservationRef }, fixture.sources);
      common.evaluation_request_ref = put("fixture/finalized-execution-request.json", finalized);
      finalizedScope = { formal_claim_ref: verificationTrace.claim_ref, evaluation_context_ref: finalized.evaluation_context_ref,
        interpretation_model_ref: finalized.interpretation_model_ref, obligation_set_ref: obligationSetRef,
        projection_ref: projectionRef, preservation_binding_ref: preservationRef,
        case_domain_sha256: finalized.case_domain_sha256,
        witness_input_set_sha256: finalized.witness_input_set_sha256,
        domain_and_bound_sha256: finalized.domain_and_bound_sha256 };
      caseResults = [{ obligation_id: "fixture-obligation", case_id: "fixture-case", normalized_outcome: "passed" }];
      if (extraCase) caseResults.push({ obligation_id: "fixture-obligation-2", case_id: "fixture-case-2", normalized_outcome: "passed" });
    } else common.evaluation_request_ref = verificationTrace.request_ref;
    common.bindings = { formal_claim_ref: verificationTrace.claim_ref, capability_assessment_ref: capabilityRef,
      obligation_ref: put("fixture/obligation.json", { obligation_id: "fixture-obligation" }),
      obligation_set_ref: obligationSetRef,
      projection_ref: projectionRef, preservation_binding_ref: preservationRef,
      native_source_bundle_ref: put("fixture/native-source-bundle.json", { files: ["fixture.native"] }),
      runtime_binding_ref: runtimeRef, profile_ref: providerProfileRef, environment_refs: [environmentRef] };
  } else {
    const leanBindingRef = put("fixture/lean-binding.json", { binding_id: "fixture-lean-binding" });
    const theoremRequestRef = put("fixture/theorem-request.json", { request_id: "fixture-theorem-request", formal_claim_lean_binding_ref: leanBindingRef });
    common.evaluation_request_ref = theoremRequestRef;
    common.bindings = { formal_claim_ref: verificationTrace.claim_ref, capability_assessment_ref: capabilityRef,
      formal_claim_lean_binding_ref: leanBindingRef, theorem_request_ref: theoremRequestRef,
      runtime_binding_ref: runtimeRef, profile_ref: providerProfileRef, environment_refs: [environmentRef] };
  }
  const receiptRef: any = put(`fixture/${route}-${outcome}-receipt.json`, {
    schema_version: finalizedScope ? "alchlang.evf-provider-outcome/v2-candidate" : "alchlang.evf-provider-outcome/v1-candidate", route_kind: route,
    provider: common.provider, causal_outcome: outcome, cause: common.cause,
    evaluation_request_ref: common.evaluation_request_ref,
    comparability: common.comparability, result_semantics: common.result_semantics,
    ...(finalizedScope ? { finalized_scope: finalizedScope, case_results: caseResults } : {}),
  });
  if (outcome === "stale") receiptRef.current = false;
  common.provider_receipt_ref = receiptRef;
  return { input: common, sources: fixture.sources };
}

function replaceReceipt(fixture: ReturnType<typeof evidenceFixture>, mutate: (value: any) => void): void {
  const ref = fixture.input.provider_receipt_ref;
  const value = JSON.parse((fixture.sources.get(ref.path) as Buffer).toString("utf8"));
  mutate(value);
  const bytes = Buffer.from(JSON.stringify(value));
  fixture.sources.set(ref.path, bytes);
  ref.sha256 = sha(bytes); ref.size_bytes = bytes.length;
}

test("preserves typed outcomes while execution aggregate pass fails closed", () => {
  for (const route of routes) for (const outcome of outcomes) {
    const fixture = evidenceFixture(route, outcome);
    if (route === "execution-evidence" && outcome === "pass") {
      assert.throws(() => joinApplicationEvfEvidence(fixture.input, fixture.sources), /APPLICATION_EVF_CASE_OBSERVATION_REQUIRED/);
      continue;
    }
    const result = joinApplicationEvfEvidence(fixture.input, fixture.sources);
    const [joinStatus, executionNormalized, theoremNormalized] = expected[outcome];
    assert.equal((result.evf_join as any).join_status, joinStatus, `${route}/${outcome}`);
    assert.equal((result.evidence_binding as any).normalized_outcome, route === "execution-evidence" ? executionNormalized : theoremNormalized, `${route}/${outcome}`);
    assert.equal((result.causal_join as any).causal_outcome, outcome);
    assert.equal((result.causal_join as any).can_satisfy_obligation, outcome === "pass");
    assert.equal((result.causal_join as any).evidence_omitted, false);
    assert.equal((result.causal_join as any).non_pass_promoted_to_pass, false);
    assert.equal((result.evf_join as any).residue.length, outcome === "pass" ? 0 : 3);
    assertApplicationEvfEvidenceCurrent(fixture.input, fixture.sources, result);
  }
});

test("all constructible route/outcome cells satisfy the provider, theorem, EVF and causal schemas", () => {
  const values = routes.flatMap(route => outcomes.filter(outcome => route !== "execution-evidence" || outcome !== "pass").map(outcome => {
    const fixture = evidenceFixture(route, outcome); const result = joinApplicationEvfEvidence(fixture.input, fixture.sources);
    return { route, evidence: result.evidence_binding, join: result.evf_join, causal: result.causal_join };
  }));
  const root = "../../../../../../../craft/projects/domainspec-v2/";
  const schemas = [
    fileURLToPath(new URL(`${root}formalization/schemas/provider-evidence-binding.schema.json`, import.meta.url)),
    fileURLToPath(new URL(`${root}formalization/schemas/theorem-evidence-binding.schema.json`, import.meta.url)),
    fileURLToPath(new URL(`${root}formalization/schemas/evf-evidence-join.schema.json`, import.meta.url)),
    fileURLToPath(new URL(`${root}development/authoring-to-runtime-v1/evf-causal-join.schema.json`, import.meta.url)),
    fileURLToPath(new URL(`${root}formalization/schemas/provider-evidence-binding.v2.schema.json`, import.meta.url)),
    fileURLToPath(new URL(`${root}formalization/schemas/evf-evidence-join.v2.schema.json`, import.meta.url)),
  ];
  const script = `import json,sys,jsonschema
p=json.load(sys.stdin); s=[json.load(open(x)) for x in sys.argv[1:]]
for x in p:
  is_v2=x['evidence']['schema_version']=='domainspec-v2.provider-evidence-binding/v2-candidate'
  jsonschema.Draft202012Validator(s[4] if is_v2 else s[0] if x['route']=='execution-evidence' else s[1]).validate(x['evidence'])
  jsonschema.Draft202012Validator(s[5] if is_v2 else s[2]).validate(x['join'])
  jsonschema.Draft202012Validator(s[3]).validate(x['causal'])`;
  const validation = spawnSync("python3", ["-c", script, ...schemas], { input: JSON.stringify(values), encoding: "utf8", timeout: 20000 });
  assert.equal(validation.status, 0, validation.stderr || String(validation.error));
});

test("historical post-TDE request and synthetic pass receipt satisfy their versioned schemas without proving execution", () => {
  const fixture = evidenceFixture("execution-evidence", "pass");
  const request = JSON.parse(fixture.sources.get(fixture.input.evaluation_request_ref.path)!.toString("utf8"));
  const receipt = JSON.parse(fixture.sources.get(fixture.input.provider_receipt_ref.path)!.toString("utf8"));
  const root = "../../../../../../../craft/projects/domainspec-v2/development/authoring-to-runtime-v1/";
  const schemas = [
    fileURLToPath(new URL(`${root}finalized-execution-request.schema.json`, import.meta.url)),
    fileURLToPath(new URL(`${root}evf-provider-outcome.v2.schema.json`, import.meta.url)),
  ];
  const script = "import json,sys,jsonschema\np=json.load(sys.stdin)\nfor schema,value in zip(sys.argv[1:],p): jsonschema.Draft202012Validator(json.load(open(schema))).validate(value)";
  const validation = spawnSync("python3", ["-c", script, ...schemas], { input: JSON.stringify([request, receipt]), encoding: "utf8", timeout: 20000 });
  assert.equal(validation.status, 0, validation.stderr || String(validation.error));
});

test("historical execution-pass input rejects legacy requests and changed finalized scope before the observation gate", () => {
  const legacy = evidenceFixture("execution-evidence", "pass");
  const baseBytes = legacy.sources.get("fixture/accepted-base-request.json")!;
  legacy.input.evaluation_request_ref = { path: "fixture/accepted-base-request.json", sha256: sha(baseBytes), size_bytes: baseBytes.length, current: true };
  assert.throws(() => joinApplicationEvfEvidence(legacy.input, legacy.sources), /APPLICATION_EVF_REQUEST/);

  for (const field of ["case_domain_sha256", "witness_input_set_sha256", "domain_and_bound_sha256"] as const) {
    const changed = evidenceFixture("execution-evidence", "pass");
    replaceReceipt(changed, receipt => { receipt.finalized_scope[field] = "0".repeat(64); });
    assert.throws(() => joinApplicationEvfEvidence(changed.input, changed.sources), /APPLICATION_EVF_RECEIPT_MISMATCH/, field);
  }
  for (const field of ["formal_claim_ref", "evaluation_context_ref", "obligation_set_ref", "projection_ref", "preservation_binding_ref"] as const) {
    const changed = evidenceFixture("execution-evidence", "pass");
    replaceReceipt(changed, receipt => { receipt.finalized_scope[field].sha256 = "0".repeat(64); });
    assert.throws(() => joinApplicationEvfEvidence(changed.input, changed.sources), /APPLICATION_EVF_RECEIPT_MISMATCH/, field);
  }
  for (const path of ["fixture/finalized-obligation-set.json", "fixture/finalized-projection.json", "fixture/finalized-preservation.json", "fixture/accepted-evaluation-context.json"] as const) {
    const changed = evidenceFixture("execution-evidence", "pass");
    changed.sources.set(path, Buffer.from(`${changed.sources.get(path)!.toString("utf8")} `));
    assert.throws(() => joinApplicationEvfEvidence(changed.input, changed.sources), /EXACT_REF|EVIDENCE_STALE|APPLICATION_EXECUTION_STALE/, path);
  }
  const changedRequest = evidenceFixture("execution-evidence", "pass");
  const ref = changedRequest.input.evaluation_request_ref;
  const request = JSON.parse(changedRequest.sources.get(ref.path)!.toString("utf8"));
  request.request_id = `FinalizedExecutionRequest:${"0".repeat(64)}`;
  const bytes = Buffer.from(JSON.stringify(request));
  changedRequest.sources.set(ref.path, bytes); ref.sha256 = sha(bytes); ref.size_bytes = bytes.length;
  replaceReceipt(changedRequest, receipt => { receipt.evaluation_request_ref = ref; });
  assert.throws(() => joinApplicationEvfEvidence(changedRequest.input, changedRequest.sources), /APPLICATION_EVF_REQUEST_MISMATCH/);
  const wrongProvider = evidenceFixture("execution-evidence", "pass", "other-provider");
  assert.throws(() => joinApplicationEvfEvidence(wrongProvider.input, wrongProvider.sources), /APPLICATION_EVF_PROVIDER/);
  const wrongProfile = evidenceFixture("execution-evidence", "pass", "provider:fixture", false, "other-provider");
  assert.throws(() => joinApplicationEvfEvidence(wrongProfile.input, wrongProfile.sources), /APPLICATION_EVF_PROVIDER/);
  const unrelated = evidenceFixture("execution-evidence", "pass");
  const unrelatedBytes = Buffer.from(JSON.stringify({ obligation_id: "unrelated" }));
  const unrelatedPath = "fixture/unrelated-obligation.json";
  unrelated.sources.set(unrelatedPath, unrelatedBytes);
  unrelated.input.bindings.obligation_ref = { path: unrelatedPath, sha256: sha(unrelatedBytes), size_bytes: unrelatedBytes.length, current: true };
  assert.throws(() => joinApplicationEvfEvidence(unrelated.input, unrelated.sources), /APPLICATION_EVF_CASES/);
  const missingCaseResult = evidenceFixture("execution-evidence", "pass");
  replaceReceipt(missingCaseResult, receipt => { receipt.case_results = []; });
  assert.throws(() => joinApplicationEvfEvidence(missingCaseResult.input, missingCaseResult.sources), /APPLICATION_EVF_RECEIPT_MISMATCH/);
  const uncoveredSecondCase = evidenceFixture("execution-evidence", "pass", "provider:fixture", true);
  assert.throws(() => joinApplicationEvfEvidence(uncoveredSecondCase.input, uncoveredSecondCase.sources), /APPLICATION_EVF_CASE_OBSERVATION_REQUIRED/);
  replaceReceipt(uncoveredSecondCase, receipt => { receipt.case_results.pop(); });
  assert.throws(() => joinApplicationEvfEvidence(uncoveredSecondCase.input, uncoveredSecondCase.sources), /APPLICATION_EVF_RECEIPT_MISMATCH/);
  const widened = evidenceFixture("execution-evidence", "pass");
  widened.input.claim_ceiling = "all production behavior";
  assert.throws(() => joinApplicationEvfEvidence(widened.input, widened.sources), /APPLICATION_EVF_CASE_OBSERVATION_REQUIRED/);
});

test("pass is impossible with semantic incomparability or a non-current input", () => {
  const incomparable = evidenceFixture("execution-evidence", "pass");
  incomparable.input.comparability.same_result_semantics = false;
  assert.throws(() => joinApplicationEvfEvidence(incomparable.input, incomparable.sources), /APPLICATION_EVF_RECEIPT_MISMATCH/);
  replaceReceipt(incomparable, receipt => { receipt.comparability.same_result_semantics = false; });
  assert.throws(() => joinApplicationEvfEvidence(incomparable.input, incomparable.sources), /APPLICATION_EVF_PASS_GUARD/);
  const stale = evidenceFixture("execution-evidence", "pass"); stale.input.provider_receipt_ref.current = false;
  assert.throws(() => joinApplicationEvfEvidence(stale.input, stale.sources), /APPLICATION_EVF_CURRENTNESS/);
});

test("a contradictory or malformed exact receipt cannot promote a caller-declared pass", () => {
  for (const route of routes) {
    const failed = evidenceFixture(route, "pass");
    replaceReceipt(failed, receipt => { receipt.causal_outcome = "fail"; });
    assert.throws(() => joinApplicationEvfEvidence(failed.input, failed.sources), /APPLICATION_EVF_RECEIPT_MISMATCH/);
    const wrongRequest = evidenceFixture(route, "pass");
    replaceReceipt(wrongRequest, receipt => { receipt.evaluation_request_ref.sha256 = "0".repeat(64); });
    assert.throws(() => joinApplicationEvfEvidence(wrongRequest.input, wrongRequest.sources), /APPLICATION_EVF_RECEIPT_MISMATCH/);
    const malformed = evidenceFixture(route, "pass");
    const ref = malformed.input.provider_receipt_ref;
    const bytes = Buffer.from("not-json"); malformed.sources.set(ref.path, bytes); ref.sha256 = sha(bytes); ref.size_bytes = bytes.length;
    assert.throws(() => joinApplicationEvfEvidence(malformed.input, malformed.sources), /APPLICATION_EVF_RECEIPT/);
  }
});

test("stale is exact and cannot be asserted over an all-current chain", () => {
  const fixture = evidenceFixture("theorem-evidence", "stale"); fixture.input.provider_receipt_ref.current = true;
  assert.throws(() => joinApplicationEvfEvidence(fixture.input, fixture.sources), /APPLICATION_EVF_CURRENTNESS/);
});

test("missing, changed, over-broad and mismatched evidence fails closed", () => {
  const missing = evidenceFixture("execution-evidence", "unknown"); missing.sources.delete(missing.input.provider_receipt_ref.path);
  assert.throws(() => joinApplicationEvfEvidence(missing.input, missing.sources), /APPLICATION_EVF_EVIDENCE_MISSING/);
  const changed = evidenceFixture("execution-evidence", "timeout"); changed.sources.set(changed.input.provider_receipt_ref.path, Buffer.from("changed"));
  assert.throws(() => joinApplicationEvfEvidence(changed.input, changed.sources), /APPLICATION_EVF_EVIDENCE_STALE/);
  const extra = evidenceFixture("execution-evidence", "malformed"); extra.input.join_status = "PASS_BOUNDED";
  assert.throws(() => joinApplicationEvfEvidence(extra.input, extra.sources), /APPLICATION_EVF_INPUT/);
  const theorem = evidenceFixture("theorem-evidence", "unknown"); theorem.input.evaluation_request_ref = theorem.input.bindings.formal_claim_ref;
  assert.throws(() => joinApplicationEvfEvidence(theorem.input, theorem.sources), /APPLICATION_EVF_REQUEST_MISMATCH/);
});

test("currentness rejects causal promotion, evidence omission and output mutation", () => {
  const fixture = evidenceFixture("execution-evidence", "unknown"); const result = joinApplicationEvfEvidence(fixture.input, fixture.sources);
  for (const mutate of [
    (value: any) => { value.causal_join.can_satisfy_obligation = true; },
    (value: any) => { value.causal_join.evidence_omitted = true; },
    (value: any) => { value.evf_join.join_status = "PASS_BOUNDED"; },
    (value: any) => { value.evidence_binding.normalized_outcome = "passed"; },
  ]) {
    const changed = structuredClone(result); mutate(changed);
    assert.throws(() => assertApplicationEvfEvidenceCurrent(fixture.input, fixture.sources, changed), /APPLICATION_EVF_STALE/);
  }
});
