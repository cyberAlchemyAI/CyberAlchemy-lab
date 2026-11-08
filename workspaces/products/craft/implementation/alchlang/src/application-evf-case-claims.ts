import { CompilationRejected } from "./model.js";
import { digest, json, symbol } from "./domainspec-profile.js";
import { finalizeApplicationExecutionRequest } from "./application-execution-request.js";

type RecordValue = Record<string, unknown>;
export type CaseClaimRef = { path: string; sha256: string; size_bytes: number; current: true };

const canonical = (value: unknown): string => {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value !== null && typeof value === "object") {
    const item = value as RecordValue;
    return `{${Object.keys(item).sort().map(key => `${JSON.stringify(key)}:${canonical(item[key])}`).join(",")}}`;
  }
  return JSON.stringify(value) ?? "null";
};
const same = (left: unknown, right: unknown) => canonical(left) === canonical(right);
const reject = (code: string, path: string, message: string): never => {
  throw new CompilationRejected([{ code, path, message }]);
};
const object = (value: unknown, path: string): RecordValue => {
  if (!value || typeof value !== "object" || Array.isArray(value)) reject("APPLICATION_EVF_CASE_INPUT", path, "expected object");
  return value as RecordValue;
};
const exact = (value: unknown, keys: readonly string[], path: string): RecordValue => {
  const item = object(value, path);
  if (!same(Object.keys(item).sort(), [...keys].sort())) reject("APPLICATION_EVF_CASE_INPUT", path, "unexpected or missing property");
  return item;
};
const text = (value: unknown, path: string): string => {
  if (typeof value !== "string" || !value.trim()) reject("APPLICATION_EVF_CASE_INPUT", path, "expected nonempty text");
  return value as string;
};
const currentRef = (value: unknown, sources: ReadonlyMap<string, Buffer>, path: string): CaseClaimRef => {
  const item = exact(value, ["path", "sha256", "size_bytes", "current"], path);
  const refPath = text(item.path, `${path}/path`);
  if (!/^[a-f0-9]{64}$/.test(String(item.sha256)) || !Number.isSafeInteger(item.size_bytes) || (item.size_bytes as number) < 1 || item.current !== true)
    reject("APPLICATION_EVF_CASE_REF", path, "expected current nonempty exact reference");
  const bytes = sources.get(refPath);
  if (!bytes) reject("APPLICATION_EVF_CASE_MISSING", path, `selected bytes missing for ${refPath}`);
  const selectedBytes = bytes as Buffer;
  if (selectedBytes.length !== item.size_bytes || digest(selectedBytes) !== item.sha256)
    reject("APPLICATION_EVF_CASE_STALE", path, `selected bytes differ for ${refPath}`);
  return { path: refPath, sha256: item.sha256 as string, size_bytes: item.size_bytes as number, current: true };
};
const read = (ref: CaseClaimRef, sources: ReadonlyMap<string, Buffer>, path: string): RecordValue => {
  try { return object(JSON.parse((sources.get(ref.path) as Buffer).toString("utf8")), path); }
  catch { return reject("APPLICATION_EVF_CASE_JSON", path, "selected artifact is not a JSON object"); }
};
const generatedRef = (path: string, body: string): CaseClaimRef => ({
  path, sha256: digest(body), size_bytes: Buffer.byteLength(body), current: true,
});

/** Constructs an unverified case-claim bridge. It never runs or authenticates a provider. */
export function joinApplicationEvfCaseClaims(input: unknown, sources: ReadonlyMap<string, Buffer>) {
  const root = exact(input, ["schema_version", "join_id", "provider", "reported_causal_outcome", "cause",
    "evaluation_request_ref", "provider_outcome_ref", "comparability", "result_semantics", "claim_ceiling",
    "bindings", "case_claims"], "$case_input");
  if (root.schema_version !== "alchlang.evf-evidence-input/v2-candidate" || root.reported_causal_outcome !== "pass")
    reject("APPLICATION_EVF_CASE_INPUT", "$case_input", "only isolated v3 reported-pass input is supported");
  const joinId = text(root.join_id, "$case_input/join_id");
  const cause = text(root.cause, "$case_input/cause");
  const resultSemantics = text(root.result_semantics, "$case_input/result_semantics");
  const inputCeiling = text(root.claim_ceiling, "$case_input/claim_ceiling");
  const provider = exact(root.provider, ["owner", "id", "version"], "$case_input/provider");
  const providerOwner = text(provider.owner, "$case_input/provider/owner");
  const providerId = text(provider.id, "$case_input/provider/id");
  const providerVersion = text(provider.version, "$case_input/provider/version");
  const comparability = exact(root.comparability,
    ["same_claim", "same_evaluation_request", "same_domain", "same_result_semantics"], "$case_input/comparability");
  if (Object.values(comparability).some(value => value !== true))
    reject("APPLICATION_EVF_CASE_COMPARABILITY", "$case_input/comparability", "reported pass requires all four declared comparability flags");
  const bindings = exact(root.bindings, ["formal_claim_ref", "capability_assessment_ref", "obligation_ref",
    "obligation_set_ref", "projection_ref", "preservation_binding_ref", "native_source_bundle_ref",
    "runtime_binding_ref", "profile_ref", "environment_refs"], "$case_input/bindings");
  const refs = Object.fromEntries(Object.entries(bindings).filter(([key]) => key !== "environment_refs")
    .map(([key, value]) => [key, currentRef(value, sources, `$case_input/bindings/${key}`)])) as Record<string, CaseClaimRef>;
  if (!Array.isArray(bindings.environment_refs) || bindings.environment_refs.length < 1)
    reject("APPLICATION_EVF_CASE_INPUT", "$case_input/bindings/environment_refs", "at least one environment is required");
  const environments = (bindings.environment_refs as unknown[]).map((value, index) =>
    currentRef(value, sources, `$case_input/bindings/environment_refs/${index}`));
  if (new Set(environments.map(value => value.path)).size !== environments.length)
    reject("APPLICATION_EVF_CASE_INPUT", "$case_input/bindings/environment_refs", "environment paths must be unique");
  const requestRef = currentRef(root.evaluation_request_ref, sources, "$case_input/evaluation_request_ref");
  const outcomeRef = currentRef(root.provider_outcome_ref, sources, "$case_input/provider_outcome_ref");
  const selectedRequest = read(requestRef, sources, "$request");
  if (selectedRequest.schema_version !== "alchlang.finalized-execution-request/v1-candidate")
    reject("APPLICATION_EVF_CASE_REQUEST", "$request", "post-TDE finalized request required");
  const selected = {
    base_request_ref: selectedRequest.base_request_ref,
    obligation_set_ref: selectedRequest.obligation_set_ref,
    projection_ref: selectedRequest.projection_ref,
    preservation_binding_ref: selectedRequest.preservation_binding_ref,
  };
  const finalized = finalizeApplicationExecutionRequest(selected, sources);
  if (!same(selectedRequest, finalized) || !same(finalized.formal_claim_ref, refs.formal_claim_ref) ||
      !same(finalized.obligation_set_ref, refs.obligation_set_ref) || !same(finalized.projection_ref, refs.projection_ref) ||
      !same(finalized.preservation_binding_ref, refs.preservation_binding_ref) ||
      !same(finalized.runtime_ref, refs.runtime_binding_ref) || !same(finalized.provider_profile_ref, refs.profile_ref))
    reject("APPLICATION_EVF_CASE_REQUEST", "$request", "finalized request differs from exact selected bindings");
  const selectedSet = read(refs.obligation_set_ref!, sources, "$obligation_set");
  const selectedRows = selectedSet.obligations;
  if (!Array.isArray(selectedRows) || !selectedRows.length)
    reject("APPLICATION_EVF_CASE_DOMAIN", "$obligation_set/obligations", "selected case domain is empty");
  const capabilityRaw = object(selectedSet.capability_assessment_ref, "$obligation_set/capability_assessment_ref");
  if (capabilityRaw.current === false || !same({ ...capabilityRaw, current: true }, refs.capability_assessment_ref))
    reject("APPLICATION_EVF_CASE_BINDING", "$case_input/bindings/capability_assessment_ref", "capability differs from selected set");
  const selectedObligation = read(refs.obligation_ref!, sources, "$obligation");
  const obligationId = text(selectedObligation.obligation_id, "$obligation/obligation_id");
  if (!(selectedRows as RecordValue[]).some(row => row.obligation_id === obligationId))
    reject("APPLICATION_EVF_CASE_BINDING", "$obligation", "selected obligation is absent from TDE set");
  const runtime = read(refs.runtime_binding_ref!, sources, "$runtime");
  const profile = read(refs.profile_ref!, sources, "$profile");
  if (runtime.schema_version !== "domainspec-v2.provider-runtime-binding/v1-candidate" || runtime.currentness !== "current" ||
      runtime.provider_owner !== providerOwner || runtime.provider_id !== providerId || runtime.provider_version !== providerVersion ||
      profile.provider_owner !== providerOwner || profile.provider_id !== providerId || profile.provider_version !== providerVersion ||
      !same(runtime.profile_ref, refs.profile_ref))
    reject("APPLICATION_EVF_CASE_PROVIDER", "$case_input/provider", "provider identity differs from runtime or profile");
  const expectedRows = (selectedRows as RecordValue[]).map((item, index) => {
    const row = exact(item, ["obligation_id", "case_id", "kind", "normalized_inputs", "expected_relation_or_oracle",
      "source_basis", "case_class", "status", "claim_ceiling"], `$obligation_set/obligations/${index}`);
    const witness = { obligation_id: row.obligation_id, case_id: row.case_id,
      normalized_inputs: row.normalized_inputs, expected_relation_or_oracle: row.expected_relation_or_oracle };
    return { obligation_id: text(row.obligation_id, `$obligation_set/obligations/${index}/obligation_id`),
      case_id: text(row.case_id, `$obligation_set/obligations/${index}/case_id`), witness_input_digest: digest(canonical(witness)) };
  }).sort((left, right) => left.case_id.localeCompare(right.case_id));
  if (!same(expectedRows.map(row => row.case_id), finalized.selected_case_ids))
    reject("APPLICATION_EVF_CASE_DOMAIN", "$request/selected_case_ids", "finalized case domain differs");
  const rawClaims = root.case_claims;
  if (!Array.isArray(rawClaims) || rawClaims.length !== expectedRows.length)
    reject("APPLICATION_EVF_CASE_DOMAIN", "$case_input/case_claims", "one claim per selected case is required");
  const claims = (rawClaims as unknown[]).map((value: unknown, index: number) => {
    const path = `$case_input/case_claims/${index}`;
    const item = exact(value, ["obligation_id", "case_id", "witness_input_digest", "reported_native_output",
      "reported_normalized_outcome", "reported_oracle_evaluation", "artifact_ref"], path);
    const expected = expectedRows[index]!;
    if (item.obligation_id !== expected.obligation_id || item.case_id !== expected.case_id ||
        item.witness_input_digest !== expected.witness_input_digest)
      reject("APPLICATION_EVF_CASE_DOMAIN", path, "case identity, order or witness digest differs from finalized domain");
    if (item.reported_normalized_outcome !== "passed" || item.reported_oracle_evaluation !== "matched" ||
        item.reported_native_output === undefined)
      reject("APPLICATION_EVF_CASE_AGGREGATE", path, "reported aggregate pass contradicts a case claim");
    const artifactRef = currentRef(item.artifact_ref, sources, `${path}/artifact_ref`);
    const artifact = exact(read(artifactRef, sources, `${path}/artifact`), ["schema_version", "evaluation_request_ref",
      "obligation_id", "case_id", "witness_input_digest", "reported_native_output", "reported_normalized_outcome",
      "reported_oracle_evaluation"], `${path}/artifact`);
    if (artifact.schema_version !== "alchlang.evf-case-claim-artifact/v1-candidate" ||
        !same(artifact.evaluation_request_ref, requestRef) ||
        !same({ obligation_id: artifact.obligation_id, case_id: artifact.case_id,
          witness_input_digest: artifact.witness_input_digest, reported_native_output: artifact.reported_native_output,
          reported_normalized_outcome: artifact.reported_normalized_outcome,
          reported_oracle_evaluation: artifact.reported_oracle_evaluation },
        { obligation_id: item.obligation_id, case_id: item.case_id,
          witness_input_digest: item.witness_input_digest, reported_native_output: item.reported_native_output,
          reported_normalized_outcome: item.reported_normalized_outcome,
          reported_oracle_evaluation: item.reported_oracle_evaluation }))
      reject("APPLICATION_EVF_CASE_ARTIFACT", path, "case artifact contradicts the selected request or envelope");
    return { ...item, artifact_ref: artifactRef };
  });
  const claimRefs = claims.map(row => row.artifact_ref);
  if (new Set(claimRefs.map(ref => ref.path)).size !== claimRefs.length)
    reject("APPLICATION_EVF_CASE_DOMAIN", "$case_input/case_claims", "case artifact paths must be unique");
  const scope = { formal_claim_ref: refs.formal_claim_ref, evaluation_context_ref: finalized.evaluation_context_ref,
    interpretation_model_ref: finalized.interpretation_model_ref, obligation_set_ref: refs.obligation_set_ref,
    projection_ref: refs.projection_ref, preservation_binding_ref: refs.preservation_binding_ref,
    case_domain_sha256: finalized.case_domain_sha256, witness_input_set_sha256: finalized.witness_input_set_sha256,
    domain_and_bound_sha256: finalized.domain_and_bound_sha256 };
  const expectedOutcome = { schema_version: "alchlang.evf-provider-outcome/v3-candidate", route_kind: "execution-evidence",
    provider, reported_causal_outcome: "pass", cause, evaluation_request_ref: requestRef,
    comparability, result_semantics: resultSemantics, finalized_scope: scope, case_claims: claims,
    case_evidence_verification: "unverified" };
  if (!same(read(outcomeRef, sources, "$provider_outcome"), expectedOutcome))
    reject("APPLICATION_EVF_CASE_OUTCOME", "$provider_outcome", "reported provider outcome differs from exact case claims");
  const residue = ["case-evidence-verification:unverified", "provider-execution:not-observed", "oracle-truth:not-checked"];
  const ceiling = `Unverified case claims within ${inputCeiling}; no provider execution, oracle truth, runtime guarantee or authority claim`;
  const prefix = `formalization/evf-joins/${symbol(joinId)}/case-claims-v3`;
  const files: Record<string, string> = {};
  const providerBinding = { schema_version: "domainspec-v2.provider-evidence-binding/v3-candidate",
    binding_id: `ProviderCaseClaims:${joinId}`, provider_owner: providerOwner, provider_id: providerId,
    provider_version: providerVersion, formal_claim_ref: refs.formal_claim_ref, obligation_ref: refs.obligation_ref,
    projection_ref: refs.projection_ref, evaluation_request_ref: requestRef, finalized_scope: scope,
    native_source_bundle_ref: refs.native_source_bundle_ref, runtime_binding_ref: refs.runtime_binding_ref,
    environment_ref: environments[0], provider_outcome_ref: outcomeRef, case_claim_refs: claimRefs,
    reported_causal_outcome: "pass", execution_status: "not-observed", normalized_outcome: "blocked",
    evidence_status: "unverified", case_evidence_verification: "unverified", residue,
    authority_effect: "none", claim_ceiling: ceiling };
  const bindingPath = `${prefix}/provider-evidence-binding.json`;
  files[bindingPath] = json(providerBinding);
  const bindingRef = generatedRef(bindingPath, files[bindingPath]!);
  const evfJoin = { schema_version: "domainspec-v2.evf-evidence-join/v3-candidate", join_id: joinId,
    owner: "EVF", route_kind: "execution-evidence", bindings: { formal_claim_ref: refs.formal_claim_ref,
      capability_assessment_ref: refs.capability_assessment_ref, obligation_set_ref: refs.obligation_set_ref,
      projection_ref: refs.projection_ref, preservation_binding_ref: refs.preservation_binding_ref,
      evaluation_request_ref: requestRef, finalized_scope: scope, native_source_bundle_ref: refs.native_source_bundle_ref,
      runtime_binding_ref: refs.runtime_binding_ref, profile_ref: refs.profile_ref,
      provider_evidence_refs: [bindingRef], environment_refs: environments,
      case_claim_refs: claimRefs, result_semantics: resultSemantics },
    declared_comparability: comparability, comparability_verification: "unverified",
    case_evidence_verification: "unverified", join_status: "BLOCKED",
    bounded_conclusion: "Reported case claims are structurally consistent but do not satisfy an obligation without runner and oracle verification.",
    residue, revision_route: "provider", authority_effect: "none", claim_ceiling: ceiling };
  const joinPath = `${prefix}/evf-evidence-join.json`;
  files[joinPath] = json(evfJoin);
  const joinRef = generatedRef(joinPath, files[joinPath]!);
  const causalJoin = { schema_version: "alchlang.evf-causal-join/v2-candidate", join_id: joinId,
    route_kind: "execution-evidence", reported_causal_outcome: "pass", cause,
    evaluation_request_ref: requestRef, provider_outcome_ref: outcomeRef, evidence_binding_ref: bindingRef,
    evf_join_ref: joinRef, domain_join_status: "BLOCKED", can_satisfy_obligation: false,
    case_evidence_verification: "unverified", revision_route: "provider", residue,
    provider_execution_by_join: false, provider_result_consumed: false, evidence_omitted: false,
    non_pass_promoted_to_pass: false, authority_effect: "none", claim_ceiling: ceiling };
  const causalPath = `${prefix}/causal-join.json`;
  files[causalPath] = json(causalJoin);
  const causalRef = generatedRef(causalPath, files[causalPath]!);
  const trace = { schema_version: "alchlang.evf-evidence-trace/v2-candidate", join_id: joinId,
    route_kind: "execution-evidence", input_sha256: digest(canonical(input)), reported_causal_outcome: "pass",
    provider_outcome_ref: outcomeRef, case_claim_refs: claimRefs,
    evidence_binding_ref: bindingRef, evf_join_ref: joinRef, causal_join_ref: causalRef,
    case_evidence_verification: "unverified", domain_join_status: "BLOCKED",
    can_satisfy_obligation: false, provider_execution_by_join: false,
    authority_effect: "none", claim_ceiling: ceiling };
  files[`${prefix}/trace.json`] = json(trace);
  return { provider_binding: providerBinding, evf_join: evfJoin, causal_join: causalJoin, trace, files };
}

export function assertApplicationEvfCaseClaimsCurrent(input: unknown, sources: ReadonlyMap<string, Buffer>, candidate: unknown): void {
  if (json(candidate) !== json(joinApplicationEvfCaseClaims(input, sources)))
    reject("APPLICATION_EVF_CASE_STALE", "$candidate", "case-claim bridge differs from exact current selected bytes");
}
