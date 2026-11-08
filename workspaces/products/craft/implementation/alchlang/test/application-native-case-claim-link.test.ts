import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import test from "node:test";
import { finalizeApplicationExecutionRequest } from "../src/application-execution-request.js";
import { joinApplicationEvfCaseClaims } from "../src/application-evf-case-claims.js";
import { linkApplicationNativeCaseClaims } from "../src/application-native-case-claim-link.js";
import { observeApplicationNativeCases } from "../src/application-native-case-observation.js";

type Ref = { path: string; sha256: string; size_bytes: number; current: true };
const sha = (value: string | Buffer) => createHash("sha256").update(value).digest("hex");
const canonical = (value: unknown): string => {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value && typeof value === "object") {
    const item = value as Record<string, unknown>;
    return `{${Object.keys(item).sort().map(key => `${JSON.stringify(key)}:${canonical(item[key])}`).join(",")}}`;
  }
  return JSON.stringify(value) ?? "null";
};
const executableBytes = readFileSync(process.execPath);
const localExecutable: Ref = { path: process.execPath, sha256: sha(executableBytes), size_bytes: executableBytes.length, current: true };
const adapterScript = (first: boolean, mode = "normal") => `let text="";
process.stdin.on("data", chunk => text += chunk);
process.stdin.on("end", () => {
  const row = JSON.parse(text);
  if (${JSON.stringify(mode)} === "incomplete" && row.case_id === "case-2") process.exit(7);
  const run = () => {
    const value = ${mode === "nondeterministic" ? "Math.random()" : `(row.case_id === "case-1" ? ${first} : true)`};
    process.stdout.write(JSON.stringify({ case_id: row.case_id, native_output: value }));
  };
  if (${JSON.stringify(mode)} === "slow") setTimeout(run, 200); else run();
});
`;

function fixture(reportedFirst = true, localFirst = true, mode = "normal") {
  const sources = new Map<string, Buffer>();
  const putBytes = (path: string, bytes: Buffer): Ref => {
    sources.set(path, bytes);
    return { path, sha256: sha(bytes), size_bytes: bytes.length, current: true };
  };
  const put = (path: string, value: unknown): Ref => putBytes(path, Buffer.from(`${JSON.stringify(value)}\n`));
  const claim = put("fixture/claim.json", { schema_version: "synthetic-claim", claim_id: "claim-1" });
  const derivationProfile = put("fixture/derivation-profile.json", { id: "synthetic-profile" });
  const route = put("fixture/route.json", { route_id: "route:tde" });
  const providerProfile = put("fixture/provider.json", { provider_owner: "fixture-owner", provider_id: "fixture-provider", provider_version: "1" });
  const policy = put("fixture/capability-policy.json", { policy_id: "synthetic-policy" });
  const capability = put("fixture/capability.json", {
    schema_version: "domainspec-v2.formal-claim-capability-assessment/v1-candidate", assessment_id: "synthetic-capability",
    owner: "validation-governance", formal_claim_ref: claim, policy_ref: policy, classification: "executable-bounded",
    needs_formal_reasons: [], admitted_for_tde_execution: true, provider_route: "tde", currentness: "current",
    authority_effect: "none", claim_ceiling: "classification-and-routing-only-no-execution-claim",
  });
  const runtime = put("fixture/runtime.json", {
    schema_version: "domainspec-v2.provider-runtime-binding/v1-candidate", runtime_binding_id: "runtime-1",
    provider_owner: "fixture-owner", provider_id: "fixture-provider", provider_version: "1",
    provider_digest: sha("synthetic-provider"), profile_ref: providerProfile, input_artifact_ref: route,
    command: ["synthetic-provider"], working_directory: "run", environment_allowlist: [], fixture_refs: [],
    limits: { timeout_ms: 1000, memory_ceiling_bytes: 1000000, max_output_bytes: 10000 }, network: "forbidden",
    supported_outcomes: ["passed", "failed"], currentness: "current", authority_effect: "none",
    claim_ceiling: "runtime-binding-only-no-execution-claim",
  });
  const context = put("fixture/context.json", {
    schema_version: "domainspec-v2.evaluation-context/v1-candidate", context_id: "synthetic-context", version: "1",
    status: "accepted", formal_claim_ref: claim, interpretation_model_ref: null, route_binding_ref: route,
    provider_profile_ref: providerProfile, runtime_ref: runtime, assumptions: [], limits: ["synthetic finite cases"],
    context_ceiling: "synthetic only", authority_effect: "none",
  });
  const base = put("fixture/base-request.json", {
    schema_version: "alchlang.verification-request/v1-candidate", request_id: "synthetic-request", request_state: "ready",
    formal_claim_ref: claim, evaluation_context_ref: context, route_binding_ref: route, provider_profile_ref: providerProfile,
    runtime_ref: runtime, execution_policy: { timeout_ms: 1000, memory_ceiling_bytes: 1000000,
      max_output_bytes: 10000, network: "forbidden", working_directory: "run", environment_allowlist: [] },
    authority_effect: "none", release_admission: "not-granted", claim_ceiling: "synthetic only", residue: [],
  });
  const rows = ["case-1", "case-2"].map((caseId, index) => ({
    obligation_id: "O-1", case_id: caseId, kind: "property", normalized_inputs: { value: index + 1 },
    expected_relation_or_oracle: "holds", source_basis: ["synthetic-claim"], case_class: "positive",
    status: "ready", claim_ceiling: "synthetic only",
  }));
  const set = put("fixture/obligation-set.json", {
    schema_version: "domainspec-v2.neutral-obligation-set/v1-candidate", obligation_set_id: "synthetic-set", owner: "TDE",
    formal_claim_ref: claim, capability_assessment_ref: capability, projection_ref: null, derivation_profile_ref: derivationProfile,
    derivation_status: "derived", obligations: rows, residue: [],
    determinism: { algorithm_ref: derivationProfile, input_digest: sha("in"), output_digest: sha("out") },
    authority_effect: "none", claim_ceiling: "synthetic only",
  });
  const projection = put("fixture/projection.json", {
    schema_version: "domainspec-v2.formalization-projection/v1-candidate", projection_id: "synthetic-projection",
    owner: "synthetic-formalization", formal_claim_ref: claim, capability_assessment_ref: capability,
    obligation_set_ref: set, purpose: "tde-executable-slice", target_profile_ref: derivationProfile,
    source_semantics_digest: sha("source"), projected_semantics_digest: sha("projected"),
    domain_and_bound: "two synthetic cases", preservation_kind: "exact-equivalent", currentness: "current",
    authority_effect: "none", claim_ceiling: "synthetic only",
  });
  const preservation = put("fixture/preservation.json", {
    schema_version: "domainspec-v2.preservation-binding/v1-candidate", binding_id: "synthetic-preservation",
    owner: "synthetic-formalization", projection_ref: projection, direction: "bidirectional", kind: "review-backed",
    preserved_semantics: ["synthetic finite cases"], known_losses: [], unsupported_constructs: [],
    validation_method: "synthetic fixture", certificate_ref: null, status: "preserved", authority_effect: "none",
    claim_ceiling: "synthetic only",
  });
  const selection = { base_request_ref: base, obligation_set_ref: set, projection_ref: projection,
    preservation_binding_ref: preservation };
  const finalized = finalizeApplicationExecutionRequest(selection, sources);
  const request = put("fixture/finalized-request.json", finalized);
  const caseClaims = rows.map((row, index) => {
    const witness = { obligation_id: row.obligation_id, case_id: row.case_id,
      normalized_inputs: row.normalized_inputs, expected_relation_or_oracle: row.expected_relation_or_oracle };
    const body = { schema_version: "alchlang.evf-case-claim-artifact/v1-candidate", evaluation_request_ref: request,
      obligation_id: row.obligation_id, case_id: row.case_id, witness_input_digest: sha(canonical(witness)),
      reported_native_output: index === 0 ? reportedFirst : true,
      reported_normalized_outcome: "passed", reported_oracle_evaluation: "matched" };
    const artifactRef = put(`fixture/${row.case_id}-claim.json`, body);
    const { schema_version: _schema, evaluation_request_ref: _request, ...claimRow } = body;
    return { ...claimRow, artifact_ref: artifactRef };
  });
  const scope = { formal_claim_ref: claim, evaluation_context_ref: context, interpretation_model_ref: null,
    obligation_set_ref: set, projection_ref: projection, preservation_binding_ref: preservation,
    case_domain_sha256: finalized.case_domain_sha256, witness_input_set_sha256: finalized.witness_input_set_sha256,
    domain_and_bound_sha256: finalized.domain_and_bound_sha256 };
  const provider = { owner: "fixture-owner", id: "fixture-provider", version: "1" };
  const comparability = { same_claim: true, same_evaluation_request: true, same_domain: true, same_result_semantics: true };
  const outcome = put("fixture/provider-outcome.json", {
    schema_version: "alchlang.evf-provider-outcome/v3-candidate", route_kind: "execution-evidence", provider,
    reported_causal_outcome: "pass", cause: "synthetic reported pass", evaluation_request_ref: request,
    comparability, result_semantics: "synthetic result only", finalized_scope: scope, case_claims: caseClaims,
    case_evidence_verification: "unverified",
  });
  const caseClaimInput: any = {
    schema_version: "alchlang.evf-evidence-input/v2-candidate", join_id: "synthetic-v3", provider,
    reported_causal_outcome: "pass", cause: "synthetic reported pass", evaluation_request_ref: request,
    provider_outcome_ref: outcome, comparability, result_semantics: "synthetic result only", claim_ceiling: "synthetic only",
    bindings: { formal_claim_ref: claim, capability_assessment_ref: capability,
      obligation_ref: put("fixture/obligation.json", { obligation_id: "O-1" }), obligation_set_ref: set,
      projection_ref: projection, preservation_binding_ref: preservation,
      native_source_bundle_ref: put("fixture/source-bundle.json", { synthetic: true }),
      runtime_binding_ref: runtime, profile_ref: providerProfile,
      environment_refs: [put("fixture/environment.json", { environment_id: "synthetic" })] },
    case_claims: caseClaims,
  };
  const adapter = putBytes("fixture/local-adapter.py", Buffer.from(adapterScript(localFirst, mode)));
  const nativeInput = { opt_in: "trusted-local-native-case-observation" as const, selection,
    finalized_request_ref: request, local_adapter_ref: adapter, local_executable_ref: localExecutable };
  return { sources, caseClaimInput, nativeInput, request, set, runtime };
}

async function linked(candidate: ReturnType<typeof fixture>) {
  const native_receipt = await observeApplicationNativeCases(candidate.nativeInput, candidate.sources);
  const input = { case_claim_input: candidate.caseClaimInput, native_input: candidate.nativeInput, native_receipt };
  return { input, result: await linkApplicationNativeCaseClaims(input, candidate.sources) };
}

test("matching two-case local output is consistent but permanently BLOCKED", async () => {
  const candidate = fixture();
  assert.equal(joinApplicationEvfCaseClaims(candidate.caseClaimInput, candidate.sources).causal_join.domain_join_status, "BLOCKED");
  const { result } = await linked(candidate);
  assert.equal(result.comparison_status, "claim-vs-local-output-consistent");
  assert.deepEqual(result.rows.map(row => row.case_id), ["case-1", "case-2"]);
  assert.deepEqual(result.conflicting_case_ids, []);
  assert.equal(result.domain_join_status, "BLOCKED");
  assert.equal(result.can_satisfy_obligation, false);
  assert.equal(result.provider_pass_established, false);
  assert.equal(result.evf_artifact_emitted, false);
  assert.equal(result.runtime_guarantees_observed, false);
  assert.equal(result.provider_equivalence, "unverified");
});

test("self-consistent reported claim contradicted by local output is diagnostic, not input error", async () => {
  const candidate = fixture(false, true);
  assert.equal(joinApplicationEvfCaseClaims(candidate.caseClaimInput, candidate.sources).causal_join.domain_join_status, "BLOCKED");
  const { result } = await linked(candidate);
  assert.equal(result.comparison_status, "contradicted");
  assert.deepEqual(result.conflicting_case_ids, ["case-1"]);
  assert.equal(result.can_satisfy_obligation, false);
});

test("matching false claim remains non-satisfying", async () => {
  const { result } = await linked(fixture(false, false));
  assert.equal(result.comparison_status, "claim-vs-local-output-consistent");
  assert.equal(result.domain_join_status, "BLOCKED");
  assert.equal(result.executable_oracle, "unverified");
  assert.equal(result.provider_pass_established, false);
});

test("replayed partial execution is incomplete and BLOCKED", async () => {
  const { result } = await linked(fixture(true, true, "incomplete"));
  assert.equal(result.comparison_status, "incomplete");
  assert.equal(result.observed_case_count, 1);
  assert.deepEqual(result.incomplete_case, { case_id: "case-2", kind: "nonzero-exit" });
  assert.equal(result.can_satisfy_obligation, false);
});

test("an observed contradiction takes precedence over later incomplete execution", async () => {
  const { result } = await linked(fixture(false, true, "incomplete"));
  assert.equal(result.comparison_status, "contradicted");
  assert.deepEqual(result.conflicting_case_ids, ["case-1"]);
  assert.deepEqual(result.incomplete_case, { case_id: "case-2", kind: "nonzero-exit" });
  assert.equal(result.domain_join_status, "BLOCKED");
});

test("changed request, case and witness bindings are errors, not comparison results", async () => {
  const request = fixture();
  const observedRequest = await observeApplicationNativeCases(request.nativeInput, request.sources);
  const requestInput = { case_claim_input: request.caseClaimInput, native_input: request.nativeInput,
    native_receipt: observedRequest };
  request.caseClaimInput.evaluation_request_ref = { ...request.request, path: "different-request" };
  await assert.rejects(linkApplicationNativeCaseClaims(requestInput, request.sources), /APPLICATION_EVF_CASE_|APPLICATION_NATIVE_/);
  const witness = fixture();
  const observedWitness = await observeApplicationNativeCases(witness.nativeInput, witness.sources);
  witness.caseClaimInput.case_claims[0].witness_input_digest = "0".repeat(64);
  await assert.rejects(linkApplicationNativeCaseClaims({ case_claim_input: witness.caseClaimInput,
    native_input: witness.nativeInput, native_receipt: observedWitness }, witness.sources), /APPLICATION_EVF_CASE_/);
  const changedCase = fixture();
  const observedCase = await observeApplicationNativeCases(changedCase.nativeInput, changedCase.sources);
  changedCase.caseClaimInput.case_claims[0].case_id = "changed";
  await assert.rejects(linkApplicationNativeCaseClaims({ case_claim_input: changedCase.caseClaimInput,
    native_input: changedCase.nativeInput, native_receipt: observedCase }, changedCase.sources), /APPLICATION_EVF_CASE_/);
});

test("forged receipt and nondeterministic replay are errors", async () => {
  const forged = fixture();
  const receipt: any = await observeApplicationNativeCases(forged.nativeInput, forged.sources);
  receipt.observations[0].native_output = "forged";
  const { receipt_sha256: _digest, ...body } = receipt;
  receipt.receipt_sha256 = sha(canonical(body));
  await assert.rejects(linkApplicationNativeCaseClaims({ case_claim_input: forged.caseClaimInput,
    native_input: forged.nativeInput, native_receipt: receipt }, forged.sources), /APPLICATION_NATIVE_REPLAY/);
  const nondeterministic = fixture(true, true, "nondeterministic");
  const first = await observeApplicationNativeCases(nondeterministic.nativeInput, nondeterministic.sources);
  await assert.rejects(linkApplicationNativeCaseClaims({ case_claim_input: nondeterministic.caseClaimInput,
    native_input: nondeterministic.nativeInput, native_receipt: first }, nondeterministic.sources), /APPLICATION_NATIVE_REPLAY/);
});

test("mutable source bytes and caller input changed during replay are errors", async () => {
  const changedSource = fixture(true, true, "slow");
  const sourceReceipt = await observeApplicationNativeCases(changedSource.nativeInput, changedSource.sources);
  const sourceInput = { case_claim_input: changedSource.caseClaimInput, native_input: changedSource.nativeInput,
    native_receipt: sourceReceipt };
  setTimeout(() => { changedSource.sources.get("fixture/claim.json")![3] ^= 1; }, 50);
  await assert.rejects(linkApplicationNativeCaseClaims(sourceInput, changedSource.sources), /APPLICATION_NATIVE_LINK_SOURCE_MUTATED|APPLICATION_NATIVE_SOURCE_MUTATED/);
  const changedInput = fixture(true, true, "slow");
  const inputReceipt = await observeApplicationNativeCases(changedInput.nativeInput, changedInput.sources);
  const mutableInput = { case_claim_input: changedInput.caseClaimInput, native_input: changedInput.nativeInput,
    native_receipt: inputReceipt };
  setTimeout(() => { mutableInput.case_claim_input.cause = "mutated"; }, 50);
  await assert.rejects(linkApplicationNativeCaseClaims(mutableInput, changedInput.sources), /APPLICATION_NATIVE_LINK_INPUT_MUTATED/);
});
