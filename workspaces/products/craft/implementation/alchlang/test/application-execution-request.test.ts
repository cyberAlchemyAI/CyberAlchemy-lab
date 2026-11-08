import assert from "node:assert/strict";
import crypto from "node:crypto";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { finalizeApplicationExecutionRequest } from "../src/application-execution-request.js";

type Ref = { path: string; sha256: string; size_bytes: number; current: true };
type Options = {
  caseInput?: string;
  extraCase?: boolean;
  bound?: string;
  interpretation?: string;
  preservationStatus?: string;
  losses?: string[];
  caseStatus?: string;
  duplicateCase?: boolean;
  sameObligation?: boolean;
  bindProjection?: boolean;
  capabilityAdmitted?: boolean;
  runtimeCurrentness?: string;
};
const sha256 = (value: string | Buffer) => crypto.createHash("sha256").update(value).digest("hex");

function fixture(options: Options = {}) {
  const sources = new Map<string, Buffer>();
  const put = (path: string, value: unknown): Ref => {
    const bytes = Buffer.from(`${JSON.stringify(value)}\n`);
    sources.set(path, bytes);
    return { path, sha256: sha256(bytes), size_bytes: bytes.length, current: true };
  };
  const claim = put("claim.json", { schema_version: "test-claim", claim_id: "claim-1" });
  const profile = put("derivation-profile.json", { schema_version: "test-derivation-profile" });
  const route = put("route.json", { schema_version: "test-route" });
  const provider = put("provider.json", { schema_version: "test-provider" });
  const capabilityPolicy = put("capability-policy.json", { schema_version: "test-capability-policy" });
  const capability = put("capability.json", {
    schema_version: "domainspec-v2.formal-claim-capability-assessment/v1-candidate", assessment_id: "assessment-1",
    owner: "validation-governance", formal_claim_ref: claim, policy_ref: capabilityPolicy,
    classification: options.capabilityAdmitted === false ? "unsupported" : "executable-bounded", needs_formal_reasons: [],
    admitted_for_tde_execution: options.capabilityAdmitted !== false,
    provider_route: "tde", currentness: "current", authority_effect: "none",
    claim_ceiling: "classification-and-routing-only-no-execution-claim",
  });
  const runtime = put("runtime.json", {
    schema_version: "domainspec-v2.provider-runtime-binding/v1-candidate", runtime_binding_id: "runtime-1",
    provider_owner: "fixture-owner", provider_id: "fixture-provider", provider_version: "1",
    provider_digest: sha256("fixture-provider"), profile_ref: provider, input_artifact_ref: route,
    command: ["fixture-provider"], working_directory: "run", environment_allowlist: [], fixture_refs: [],
    limits: { timeout_ms: 1000, memory_ceiling_bytes: 1000000, max_output_bytes: 10000 },
    network: "forbidden", supported_outcomes: ["passed", "failed"], currentness: options.runtimeCurrentness ?? "current",
    authority_effect: "none", claim_ceiling: "runtime-binding-only-no-execution-claim",
  });
  const interpretation = put("interpretation.json", { schema_version: "test-interpretation", version: options.interpretation ?? "one" });
  const context = put("context.json", {
    schema_version: "domainspec-v2.evaluation-context/v1-candidate", context_id: "context-1", version: "1",
    status: "accepted", formal_claim_ref: claim, interpretation_model_ref: interpretation,
    route_binding_ref: route, provider_profile_ref: provider, runtime_ref: runtime,
    assumptions: [], limits: ["finite synthetic cases"], context_ceiling: "synthetic only", authority_effect: "none",
  });
  const base = put("base-request.json", {
    schema_version: "alchlang.verification-request/v1-candidate", request_id: "VerificationRequest:one",
    request_state: "ready", formal_claim_ref: claim, evaluation_context_ref: context,
    route_binding_ref: route, provider_profile_ref: provider, runtime_ref: runtime,
    execution_policy: { timeout_ms: 1000, memory_ceiling_bytes: 1000000, max_output_bytes: 10000,
      network: "forbidden", working_directory: "run", environment_allowlist: [] },
    authority_effect: "none", release_admission: "not-granted", claim_ceiling: "synthetic only", residue: [],
  });
  const cases = [{ obligation_id: "O-1", case_id: "case-1", kind: "property", normalized_inputs: { value: options.caseInput ?? "one" },
    expected_relation_or_oracle: "holds", source_basis: ["claim-1"], case_class: "positive", status: options.caseStatus ?? "ready", claim_ceiling: "synthetic only" }];
  if (options.extraCase || options.duplicateCase) cases.push({ obligation_id: options.sameObligation ? "O-1" : "O-2", case_id: options.duplicateCase ? "case-1" : "case-2", kind: "property",
    normalized_inputs: { value: "two" }, expected_relation_or_oracle: "holds", source_basis: ["claim-1"], case_class: "positive", status: "ready", claim_ceiling: "synthetic only" });
  const obligations = put("obligations.json", {
    schema_version: "domainspec-v2.neutral-obligation-set/v1-candidate", obligation_set_id: "set-1", owner: "TDE",
    formal_claim_ref: claim, capability_assessment_ref: capability, projection_ref: null, derivation_profile_ref: profile,
    derivation_status: "derived", obligations: cases, residue: [],
    determinism: { algorithm_ref: profile, input_digest: sha256("in"), output_digest: sha256("out") },
    authority_effect: "none", claim_ceiling: "synthetic only",
  });
  const projection = put("projection.json", {
    schema_version: "domainspec-v2.formalization-projection/v1-candidate", projection_id: "projection-1",
    owner: "projects/domainspec-v2/formalization", formal_claim_ref: claim, capability_assessment_ref: capability,
    obligation_set_ref: options.bindProjection === false ? null : obligations,
    purpose: "tde-executable-slice", target_profile_ref: profile, source_semantics_digest: sha256("source"),
    projected_semantics_digest: sha256("projected"), domain_and_bound: options.bound ?? "two finite cases",
    preservation_kind: "exact-equivalent", currentness: "current", authority_effect: "none", claim_ceiling: "synthetic only",
  });
  const preservation = put("preservation.json", {
    schema_version: "domainspec-v2.preservation-binding/v1-candidate", binding_id: "preservation-1",
    owner: "projects/domainspec-v2/formalization", projection_ref: { path: projection.path, sha256: projection.sha256, size_bytes: projection.size_bytes }, direction: "bidirectional",
    kind: "review-backed", preserved_semantics: ["synthetic finite cases"], known_losses: options.losses ?? [],
    unsupported_constructs: [], validation_method: "synthetic fixture", certificate_ref: null,
    status: options.preservationStatus ?? "preserved", authority_effect: "none", claim_ceiling: "synthetic only",
  });
  const selection = { base_request_ref: base, obligation_set_ref: obligations, projection_ref: projection, preservation_binding_ref: preservation };
  return { sources, selection };
}

function rewriteSelected(candidate: ReturnType<typeof fixture>, field: keyof ReturnType<typeof fixture>["selection"], mutate: (value: any) => void) {
  const ref = candidate.selection[field];
  const value = JSON.parse(candidate.sources.get(ref.path)!.toString("utf8"));
  mutate(value);
  const bytes = Buffer.from(`${JSON.stringify(value)}\n`);
  candidate.sources.set(ref.path, bytes);
  ref.sha256 = sha256(bytes);
  ref.size_bytes = bytes.length;
}

test("post-TDE finalizer binds exact context, complete case domain, witness inputs and bound", () => {
  const { selection, sources } = fixture();
  const result = finalizeApplicationExecutionRequest(selection, sources);
  assert.equal(result.schema_version, "alchlang.finalized-execution-request/v1-candidate");
  assert.equal(result.request_state, "ready");
  assert.deepEqual(result.selected_case_ids, ["case-1"]);
  assert.equal(result.selected_case_count, 1);
  assert.equal(result.provider_execution_observed, false);
  assert.equal(result.authority_effect, "none");
  assert.equal(result.release_admission, "not-granted");
  assert.match(result.case_domain_sha256, /^[a-f0-9]{64}$/);
  assert.match(result.witness_input_set_sha256, /^[a-f0-9]{64}$/);
});

test("case-domain, witness inputs, bound and interpretation changes separate finalized requests", () => {
  const baseline = fixture();
  const before = finalizeApplicationExecutionRequest(baseline.selection, baseline.sources);
  const more = fixture({ extraCase: true });
  const withCase = finalizeApplicationExecutionRequest(more.selection, more.sources);
  assert.notEqual(withCase.case_domain_sha256, before.case_domain_sha256);
  assert.notEqual(withCase.witness_input_set_sha256, before.witness_input_set_sha256);
  assert.notEqual(withCase.request_id, before.request_id);
  const changedInput = fixture({ caseInput: "changed" });
  const withInput = finalizeApplicationExecutionRequest(changedInput.selection, changedInput.sources);
  assert.equal(withInput.case_domain_sha256, before.case_domain_sha256);
  assert.notEqual(withInput.witness_input_set_sha256, before.witness_input_set_sha256);
  assert.notEqual(withInput.request_id, before.request_id);
  const changedBound = fixture({ bound: "three finite cases" });
  const withBound = finalizeApplicationExecutionRequest(changedBound.selection, changedBound.sources);
  assert.notEqual(withBound.domain_and_bound_sha256, before.domain_and_bound_sha256);
  assert.notEqual(withBound.request_id, before.request_id);
  const changedInterpretation = fixture({ interpretation: "two" });
  const withInterpretation = finalizeApplicationExecutionRequest(changedInterpretation.selection, changedInterpretation.sources);
  assert.notDeepEqual(withInterpretation.interpretation_model_ref, before.interpretation_model_ref);
  assert.notDeepEqual(withInterpretation.evaluation_context_ref, before.evaluation_context_ref);
  assert.notEqual(withInterpretation.request_id, before.request_id);
  const changedPreservation = fixture();
  const original = JSON.parse(changedPreservation.sources.get("preservation.json")!.toString("utf8"));
  original.validation_method = "independent second review";
  const bytes = Buffer.from(`${JSON.stringify(original)}\n`);
  changedPreservation.sources.set("preservation.json", bytes);
  changedPreservation.selection.preservation_binding_ref.sha256 = sha256(bytes);
  changedPreservation.selection.preservation_binding_ref.size_bytes = bytes.length;
  const withPreservation = finalizeApplicationExecutionRequest(changedPreservation.selection, changedPreservation.sources);
  assert.notEqual(withPreservation.request_id, before.request_id);
  for (const changed of [withCase, withInput, withBound, withInterpretation, withPreservation]) {
    assert.deepEqual(changed.formal_claim_ref, before.formal_claim_ref,
      "evaluation freshness must not rewrite the immutable FormalClaim identity");
  }
});

test("one obligation may derive multiple distinct cases without collapsing the finalized domain", () => {
  const one = fixture();
  const two = fixture({ extraCase: true, sameObligation: true });
  const before = finalizeApplicationExecutionRequest(one.selection, one.sources);
  const result = finalizeApplicationExecutionRequest(two.selection, two.sources);
  assert.deepEqual(result.selected_case_ids, ["case-1", "case-2"]);
  assert.equal(result.selected_case_count, 2);
  assert.notEqual(result.case_domain_sha256, before.case_domain_sha256);
  assert.notEqual(result.witness_input_set_sha256, before.witness_input_set_sha256);
  assert.notEqual(result.request_id, before.request_id);
});

test("finalizer rejects stale selection, missing bytes, nonready or duplicate cases and weak preservation", () => {
  const stale = fixture();
  stale.sources.set("obligations.json", Buffer.from("{}\n"));
  assert.throws(() => finalizeApplicationExecutionRequest(stale.selection, stale.sources), /APPLICATION_EXECUTION_STALE/);
  const missing = fixture();
  missing.sources.delete("preservation.json");
  assert.throws(() => finalizeApplicationExecutionRequest(missing.selection, missing.sources), /APPLICATION_EXECUTION_MISSING/);
  for (const options of [{ caseStatus: "unsupported" }, { duplicateCase: true }, { duplicateCase: true, sameObligation: true }]) {
    const candidate = fixture(options);
    assert.throws(() => finalizeApplicationExecutionRequest(candidate.selection, candidate.sources), /APPLICATION_EXECUTION_CASES/);
  }
  for (const options of [{ preservationStatus: "partially-preserved" }, { losses: ["lost case"] }]) {
    const candidate = fixture(options);
    assert.throws(() => finalizeApplicationExecutionRequest(candidate.selection, candidate.sources), /APPLICATION_EXECUTION_PRESERVATION/);
  }
  const unbound = fixture({ bindProjection: false });
  assert.throws(() => finalizeApplicationExecutionRequest(unbound.selection, unbound.sources), /APPLICATION_EXECUTION_JOIN/);
  const unsupported = fixture({ capabilityAdmitted: false });
  assert.throws(() => finalizeApplicationExecutionRequest(unsupported.selection, unsupported.sources), /APPLICATION_EXECUTION_CAPABILITY/);
  const staleRuntime = fixture({ runtimeCurrentness: "stale" });
  assert.throws(() => finalizeApplicationExecutionRequest(staleRuntime.selection, staleRuntime.sources), /APPLICATION_EXECUTION_RUNTIME/);
});

test("finalizer rejects structurally invalid TDE rows, determinism, preservation and runtime policy", () => {
  const missingDeterminism = fixture();
  rewriteSelected(missingDeterminism, "obligation_set_ref", value => { delete value.determinism; });
  assert.throws(() => finalizeApplicationExecutionRequest(missingDeterminism.selection, missingDeterminism.sources), /APPLICATION_EXECUTION_INPUT/);
  const missingSourceBasis = fixture();
  rewriteSelected(missingSourceBasis, "obligation_set_ref", value => { delete value.obligations[0].source_basis; });
  assert.throws(() => finalizeApplicationExecutionRequest(missingSourceBasis.selection, missingSourceBasis.sources), /APPLICATION_EXECUTION_INPUT/);
  const unsupportedKind = fixture();
  rewriteSelected(unsupportedKind, "obligation_set_ref", value => { value.obligations[0].kind = "invented"; });
  assert.throws(() => finalizeApplicationExecutionRequest(unsupportedKind.selection, unsupportedKind.sources), /APPLICATION_EXECUTION_CASES/);
  const missingMethod = fixture();
  rewriteSelected(missingMethod, "preservation_binding_ref", value => { delete value.validation_method; });
  assert.throws(() => finalizeApplicationExecutionRequest(missingMethod.selection, missingMethod.sources), /APPLICATION_EXECUTION_INPUT/);
  for (const workingDirectory of ["../escape", "/absolute"]) {
    const unsafePolicy = fixture();
    rewriteSelected(unsafePolicy, "base_request_ref", value => { value.execution_policy.working_directory = workingDirectory; });
    assert.throws(() => finalizeApplicationExecutionRequest(unsafePolicy.selection, unsafePolicy.sources), /APPLICATION_EXECUTION_BASE/);
  }
  const duplicateEnvironment = fixture();
  rewriteSelected(duplicateEnvironment, "base_request_ref", value => { value.execution_policy.environment_allowlist = ["SAFE", "SAFE"]; });
  assert.throws(() => finalizeApplicationExecutionRequest(duplicateEnvironment.selection, duplicateEnvironment.sources), /APPLICATION_EXECUTION_INPUT/);
});

test("selected construction artifacts and finalized request satisfy their versioned schemas", () => {
  const candidate = fixture();
  const finalized = finalizeApplicationExecutionRequest(candidate.selection, candidate.sources);
  const root = "../../../../../../../craft/projects/domainspec-v2/";
  const schemas = [
    "development/authoring-to-runtime-v1/verification-request.schema.json",
    "formalization/schemas/evaluation-context.schema.json",
    "formalization/schemas/neutral-obligation-set.schema.json",
    "formalization/schemas/formalization-projection.schema.json",
    "formalization/schemas/preservation-binding.schema.json",
    "development/authoring-to-runtime-v1/finalized-execution-request.schema.json",
  ].map(name => fileURLToPath(new URL(`${root}${name}`, import.meta.url)));
  const selected = [candidate.selection.base_request_ref.path, "context.json", candidate.selection.obligation_set_ref.path,
    candidate.selection.projection_ref.path, candidate.selection.preservation_binding_ref.path]
    .map(name => JSON.parse(candidate.sources.get(name)!.toString("utf8")));
  const script = "import json,sys,jsonschema\np=json.load(sys.stdin)\nfor schema,value in zip(sys.argv[1:],p): jsonschema.Draft202012Validator(json.load(open(schema))).validate(value)";
  const validation = spawnSync("python3", ["-c", script, ...schemas], { input: JSON.stringify([...selected, finalized]), encoding: "utf8", timeout: 20000 });
  assert.equal(validation.status, 0, validation.stderr || String(validation.error));
});
