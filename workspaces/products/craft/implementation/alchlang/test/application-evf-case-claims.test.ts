import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { finalizeApplicationExecutionRequest } from "../src/application-execution-request.js";
import { assertApplicationEvfCaseClaimsCurrent, joinApplicationEvfCaseClaims } from "../src/application-evf-case-claims.js";

type Ref = { path: string; sha256: string; size_bytes: number; current: true };
const sha = (value: string | Buffer) => createHash("sha256").update(value).digest("hex");
const canonical = (value: unknown): string => {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value !== null && typeof value === "object") {
    const item = value as Record<string, unknown>;
    return `{${Object.keys(item).sort().map(key => `${JSON.stringify(key)}:${canonical(item[key])}`).join(",")}}`;
  }
  return JSON.stringify(value) ?? "null";
};

function fixture(reportedOutput: unknown = true) {
  const sources = new Map<string, Buffer>();
  const put = (path: string, value: unknown): Ref => {
    const bytes = Buffer.from(`${JSON.stringify(value)}\n`);
    sources.set(path, bytes);
    return { path, sha256: sha(bytes), size_bytes: bytes.length, current: true };
  };
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
    command: ["fixture-provider"], working_directory: "run", environment_allowlist: [], fixture_refs: [],
    limits: { timeout_ms: 1000, memory_ceiling_bytes: 1000000, max_output_bytes: 10000 },
    network: "forbidden", supported_outcomes: ["passed", "failed"], currentness: "current",
    authority_effect: "none", claim_ceiling: "runtime-binding-only-no-execution-claim",
  });
  const context = put("fixture/context.json", {
    schema_version: "domainspec-v2.evaluation-context/v1-candidate", context_id: "synthetic-context", version: "1",
    status: "accepted", formal_claim_ref: claim, interpretation_model_ref: null, route_binding_ref: route,
    provider_profile_ref: providerProfile, runtime_ref: runtime, assumptions: [], limits: ["synthetic finite cases"],
    context_ceiling: "synthetic only", authority_effect: "none",
  });
  const base = put("fixture/base-request.json", {
    schema_version: "alchlang.verification-request/v1-candidate", request_id: "synthetic-request",
    request_state: "ready", formal_claim_ref: claim, evaluation_context_ref: context,
    route_binding_ref: route, provider_profile_ref: providerProfile, runtime_ref: runtime,
    execution_policy: { timeout_ms: 1000, memory_ceiling_bytes: 1000000, max_output_bytes: 10000,
      network: "forbidden", working_directory: "run", environment_allowlist: [] },
    authority_effect: "none", release_admission: "not-granted", claim_ceiling: "synthetic only", residue: [],
  });
  const rows = ["case-1", "case-2"].map((caseId, index) => ({
    obligation_id: "O-1", case_id: caseId, kind: "property", normalized_inputs: { value: index + 1 },
    expected_relation_or_oracle: "holds", source_basis: ["synthetic-claim"], case_class: "positive",
    status: "ready", claim_ceiling: "synthetic only",
  }));
  const set = put("fixture/obligation-set.json", {
    schema_version: "domainspec-v2.neutral-obligation-set/v1-candidate", obligation_set_id: "synthetic-set",
    owner: "TDE", formal_claim_ref: claim, capability_assessment_ref: capability, projection_ref: null,
    derivation_profile_ref: derivationProfile, derivation_status: "derived", obligations: rows, residue: [],
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
    validation_method: "synthetic fixture", certificate_ref: null, status: "preserved",
    authority_effect: "none", claim_ceiling: "synthetic only",
  });
  const finalized = finalizeApplicationExecutionRequest({ base_request_ref: base, obligation_set_ref: set,
    projection_ref: projection, preservation_binding_ref: preservation }, sources);
  const request = put("fixture/finalized-request.json", finalized);
  const caseClaims = rows.map((row, index) => {
    const witness = { obligation_id: row.obligation_id, case_id: row.case_id,
      normalized_inputs: row.normalized_inputs, expected_relation_or_oracle: row.expected_relation_or_oracle };
    const body = { schema_version: "alchlang.evf-case-claim-artifact/v1-candidate", evaluation_request_ref: request,
      obligation_id: row.obligation_id, case_id: row.case_id, witness_input_digest: sha(canonical(witness)),
      reported_native_output: index === 0 ? reportedOutput : true,
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
  const input: any = {
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
  return { input, sources, rows, finalized };
}

test("complete reported pass is structurally joined but BLOCKED, including a self-consistent false output", () => {
  for (const reportedOutput of [true, false]) {
    const candidate = fixture(reportedOutput);
    const result = joinApplicationEvfCaseClaims(candidate.input, candidate.sources);
    assert.equal(result.evf_join.join_status, "BLOCKED");
    assert.equal(result.causal_join.can_satisfy_obligation, false);
    assert.equal(result.causal_join.provider_result_consumed, false);
    assert.equal(result.provider_binding.execution_status, "not-observed");
    assert.equal(result.provider_binding.case_evidence_verification, "unverified");
    assert.equal(result.trace.case_claim_refs.length, 2);
    assertApplicationEvfCaseClaimsCurrent(candidate.input, candidate.sources, result);
  }
});

test("v3 rejects incomplete, duplicate, reordered, mismatched and stale case claims", () => {
  for (const mutate of [
    (value: any) => { value.case_claims.pop(); },
    (value: any) => { value.case_claims.push(value.case_claims[0]); },
    (value: any) => { value.case_claims[1] = value.case_claims[0]; },
    (value: any) => { value.case_claims.reverse(); },
    (value: any) => { value.case_claims[0].obligation_id = "O-2"; },
    (value: any) => { value.case_claims[0].witness_input_digest = "0".repeat(64); },
    (value: any) => { value.case_claims[0].reported_native_output = false; },
    (value: any) => { value.case_claims[0].reported_oracle_evaluation = "mismatched"; },
    (value: any) => { value.case_claims[0].artifact_ref = value.case_claims[1].artifact_ref; },
    (value: any) => { value.comparability.same_domain = false; },
  ]) {
    const candidate = fixture(); mutate(candidate.input);
    assert.throws(() => joinApplicationEvfCaseClaims(candidate.input, candidate.sources), /APPLICATION_EVF_CASE_/);
  }
  const stale = fixture(); stale.sources.set(stale.input.case_claims[0].artifact_ref.path, Buffer.from("changed"));
  assert.throws(() => joinApplicationEvfCaseClaims(stale.input, stale.sources), /APPLICATION_EVF_CASE_STALE/);
  const missing = fixture(); missing.sources.delete(missing.input.case_claims[0].artifact_ref.path);
  assert.throws(() => joinApplicationEvfCaseClaims(missing.input, missing.sources), /APPLICATION_EVF_CASE_MISSING/);
  const noncurrent = fixture(); noncurrent.input.case_claims[0].artifact_ref.current = false;
  assert.throws(() => joinApplicationEvfCaseClaims(noncurrent.input, noncurrent.sources), /APPLICATION_EVF_CASE_REF/);
});

test("v3 rejects changed selected request, provider identity and caller-upgraded output", () => {
  const request = fixture(); request.sources.set(request.input.evaluation_request_ref.path, Buffer.from("{}\n"));
  assert.throws(() => joinApplicationEvfCaseClaims(request.input, request.sources), /APPLICATION_EVF_CASE_STALE/);
  const provider = fixture(); provider.input.provider.id = "different-provider";
  assert.throws(() => joinApplicationEvfCaseClaims(provider.input, provider.sources), /APPLICATION_EVF_CASE_PROVIDER|APPLICATION_EVF_CASE_OUTCOME/);
  const current = fixture(); const result = joinApplicationEvfCaseClaims(current.input, current.sources);
  const altered = structuredClone(result); altered.causal_join.can_satisfy_obligation = true;
  assert.throws(() => assertApplicationEvfCaseClaimsCurrent(current.input, current.sources, altered), /APPLICATION_EVF_CASE_STALE/);
});

test("v3 input, case artifacts, provider outcome and all four outputs satisfy exact schemas", () => {
  const candidate = fixture(); const result = joinApplicationEvfCaseClaims(candidate.input, candidate.sources);
  const root = "../../../../../../../craft/projects/domainspec-v2/";
  const names = [
    "development/authoring-to-runtime-v1/evf-evidence-input.v2.schema.json",
    "development/authoring-to-runtime-v1/evf-case-claim-artifact.v1.schema.json",
    "development/authoring-to-runtime-v1/evf-provider-outcome.v3.schema.json",
    "formalization/schemas/provider-evidence-binding.v3.schema.json",
    "formalization/schemas/evf-evidence-join.v3.schema.json",
    "development/authoring-to-runtime-v1/evf-causal-join.v2.schema.json",
    "development/authoring-to-runtime-v1/evf-evidence-trace.v2.schema.json",
  ];
  const schemaPaths = names.map(name => fileURLToPath(new URL(`${root}${name}`, import.meta.url)));
  const values = [candidate.input, ...candidate.input.case_claims.map((row: any) =>
    JSON.parse(candidate.sources.get(row.artifact_ref.path)!.toString("utf8"))),
    JSON.parse(candidate.sources.get(candidate.input.provider_outcome_ref.path)!.toString("utf8")),
    result.provider_binding, result.evf_join, result.causal_join, result.trace];
  const indexes = [0, 1, 1, 2, 3, 4, 5, 6];
  const script = `import json,sys,jsonschema
p=json.load(sys.stdin); s=[json.load(open(x)) for x in sys.argv[1:]]
for schema_index,value in zip(${JSON.stringify(indexes)},p): jsonschema.Draft202012Validator(s[schema_index]).validate(value)`;
  const validation = spawnSync("python3", ["-c", script, ...schemaPaths],
    { input: JSON.stringify(values), encoding: "utf8", timeout: 20000 });
  assert.equal(validation.status, 0, validation.stderr || String(validation.error));
});
