import { CompilationRejected } from "./model.js";
import { digest, json, symbol } from "./domainspec-profile.js";
import { finalizeApplicationExecutionRequest } from "./application-execution-request.js";

type JsonObject = Record<string, unknown>;
export type ApplicationEvfCausalOutcome =
  | "pass" | "fail" | "unknown" | "timeout" | "malformed" | "stale" | "unavailable" | "not-evaluable";
export type ApplicationEvfRouteKind = "execution-evidence" | "theorem-evidence";
export interface ApplicationEvfExactRef { path: string; sha256: string; size_bytes: number; current: boolean }

const causalOutcomes = new Set<ApplicationEvfCausalOutcome>([
  "pass", "fail", "unknown", "timeout", "malformed", "stale", "unavailable", "not-evaluable",
]);
const canonical = (value: unknown): string => {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value && typeof value === "object") return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical((value as JsonObject)[key])}`).join(",")}}`;
  return JSON.stringify(value);
};
const fail = (code: string, path: string, message: string): never => {
  throw new CompilationRejected([{ code, path, message }]);
};
const object = (value: unknown, path: string): JsonObject => {
  if (!value || typeof value !== "object" || Array.isArray(value)) fail("APPLICATION_EVF_INPUT", path, "expected object");
  return value as JsonObject;
};
const exactKeys = (value: unknown, keys: string[], path: string): JsonObject => {
  const result = object(value, path);
  if (canonical(Object.keys(result).sort()) !== canonical([...keys].sort())) fail("APPLICATION_EVF_INPUT", path, "unexpected or missing property");
  return result;
};
const text = (value: unknown, path: string): string => {
  if (typeof value !== "string" || !value.trim()) fail("APPLICATION_EVF_INPUT", path, "expected nonempty text");
  return value as string;
};
const currentRef = (path: string, bytes: string): ApplicationEvfExactRef => ({
  path, sha256: digest(bytes), size_bytes: Buffer.byteLength(bytes), current: true,
});
const sameRef = (left: ApplicationEvfExactRef, right: ApplicationEvfExactRef): boolean => canonical(left) === canonical(right);

function resolveRef(value: unknown, sources: ReadonlyMap<string, Buffer>, path: string): ApplicationEvfExactRef {
  const ref = exactKeys(value, ["path", "sha256", "size_bytes", "current"], path);
  const refPath = text(ref.path, `${path}/path`);
  const sha256 = text(ref.sha256, `${path}/sha256`);
  if (!/^[a-f0-9]{64}$/.test(sha256) || !Number.isInteger(ref.size_bytes) || (ref.size_bytes as number) < 0 || typeof ref.current !== "boolean") {
    fail("APPLICATION_EVF_EXACT_REF", path, "reference digest, size or currentness is invalid");
  }
  const bytes = sources.get(refPath);
  if (!bytes) fail("APPLICATION_EVF_EVIDENCE_MISSING", path, `exact evidence bytes are missing for ${refPath}`);
  const resolvedBytes = bytes as Buffer;
  if (digest(resolvedBytes) !== sha256 || resolvedBytes.length !== ref.size_bytes) fail("APPLICATION_EVF_EVIDENCE_STALE", path, `exact evidence bytes differ for ${refPath}`);
  return { path: refPath, sha256, size_bytes: ref.size_bytes as number, current: ref.current as boolean };
}

function resolveRefs(value: unknown, sources: ReadonlyMap<string, Buffer>, path: string): ApplicationEvfExactRef[] {
  if (!Array.isArray(value)) fail("APPLICATION_EVF_INPUT", path, "expected exact reference array");
  const values = value as unknown[];
  if (!values.length) fail("APPLICATION_EVF_INPUT", path, "expected at least one exact reference");
  const refs = values.map((item: unknown, index: number) => resolveRef(item, sources, `${path}/${index}`));
  if (new Set(refs.map(ref => ref.path)).size !== refs.length) fail("APPLICATION_EVF_INPUT", path, "reference paths must be unique");
  return refs;
}

/** The bounded outcome projection is checked against exact receipt bytes; it
 * does not authenticate the provider or interpret a provider-native protocol. */
function validateReceiptProjection(
  ref: ApplicationEvfExactRef,
  sources: ReadonlyMap<string, Buffer>,
  expected: { routeKind: ApplicationEvfRouteKind; provider: JsonObject; outcome: ApplicationEvfCausalOutcome;
    cause: string; requestRef: ApplicationEvfExactRef; comparability: JsonObject; resultSemantics: string;
    finalizedScope?: JsonObject; caseResults?: JsonObject[] },
): void {
  let decoded: unknown;
  try { decoded = JSON.parse((sources.get(ref.path) as Buffer).toString("utf8")); }
  catch { fail("APPLICATION_EVF_RECEIPT", "$evidence/provider_receipt_ref", "receipt projection is not JSON"); }
  const receipt = exactKeys(decoded, ["schema_version", "route_kind", "provider", "causal_outcome", "cause",
    "evaluation_request_ref", "comparability", "result_semantics", ...(expected.finalizedScope ? ["finalized_scope", "case_results"] : [])], "$evidence/provider_receipt");
  if (receipt.schema_version !== (expected.finalizedScope ? "alchlang.evf-provider-outcome/v2-candidate" : "alchlang.evf-provider-outcome/v1-candidate") ||
      receipt.route_kind !== expected.routeKind || canonical(receipt.provider) !== canonical(expected.provider) ||
      receipt.causal_outcome !== expected.outcome || receipt.cause !== expected.cause ||
      canonical(receipt.evaluation_request_ref) !== canonical(expected.requestRef) ||
      canonical(receipt.comparability) !== canonical(expected.comparability) ||
      (expected.finalizedScope && canonical(receipt.finalized_scope) !== canonical(expected.finalizedScope)) ||
      (expected.caseResults && canonical(receipt.case_results) !== canonical(expected.caseResults)) ||
      receipt.result_semantics !== expected.resultSemantics) {
    fail("APPLICATION_EVF_RECEIPT_MISMATCH", "$evidence/provider_receipt_ref", "exact receipt projection contradicts the declared provider, request, outcome or comparison");
  }
}

const outcomeMap = {
  pass: { executionStatus: "completed", executionNormalized: "passed", theoremNative: "checked", theoremNormalized: "passed", evidenceStatus: "current", joinStatus: "PASS_BOUNDED", revisionRoute: "none" },
  fail: { executionStatus: "completed", executionNormalized: "failed", theoremNative: "rejected", theoremNormalized: "failed", evidenceStatus: "current", joinStatus: "NON_PASS", revisionRoute: "formal-claim" },
  unknown: { executionStatus: "completed", executionNormalized: "indeterminate", theoremNative: "unknown", theoremNormalized: "indeterminate", evidenceStatus: "current", joinStatus: "INDETERMINATE", revisionRoute: "provider" },
  timeout: { executionStatus: "timeout", executionNormalized: "timeout", theoremNative: "not-run", theoremNormalized: "timeout", evidenceStatus: "current", joinStatus: "FAILED", revisionRoute: "runtime-binding" },
  malformed: { executionStatus: "failed", executionNormalized: "malformed", theoremNative: "not-run", theoremNormalized: "provider-error", evidenceStatus: "invalid", joinStatus: "FAILED", revisionRoute: "provider" },
  stale: { executionStatus: "stale", executionNormalized: "stale", theoremNative: "not-run", theoremNormalized: "stale", evidenceStatus: "stale", joinStatus: "STALE", revisionRoute: "evf-join" },
  unavailable: { executionStatus: "blocked", executionNormalized: "blocked", theoremNative: "not-run", theoremNormalized: "blocked", evidenceStatus: "missing", joinStatus: "MISSING", revisionRoute: "provider" },
  "not-evaluable": { executionStatus: "blocked", executionNormalized: "unsupported", theoremNative: "not-run", theoremNormalized: "blocked", evidenceStatus: "current", joinStatus: "UNSUPPORTED", revisionRoute: "capability-assessment" },
} as const;

/**
 * Joins already-observed provider evidence into the current DomainSpec EVF
 * bridge. It is construction-only: no provider is selected, executed or retried.
 */
export function joinApplicationEvfEvidence(input: unknown, sources: ReadonlyMap<string, Buffer>) {
  const root = exactKeys(input, ["schema_version", "join_id", "route_kind", "provider", "causal_outcome", "cause",
    "evaluation_request_ref", "provider_receipt_ref", "comparability", "result_semantics", "claim_ceiling", "bindings"], "$evidence");
  if (root.schema_version !== "alchlang.evf-evidence-input/v1") fail("APPLICATION_EVF_INPUT", "$evidence/schema_version", "unsupported evidence input version");
  const joinId = text(root.join_id, "$evidence/join_id");
  const routeKind = root.route_kind;
  if (routeKind !== "execution-evidence" && routeKind !== "theorem-evidence") fail("APPLICATION_EVF_INPUT", "$evidence/route_kind", "unsupported EVF route kind");
  const causalOutcome = root.causal_outcome;
  if (typeof causalOutcome !== "string" || !causalOutcomes.has(causalOutcome as ApplicationEvfCausalOutcome)) {
    fail("APPLICATION_EVF_INPUT", "$evidence/causal_outcome", "unsupported causal outcome");
  }
  const outcome = causalOutcome as ApplicationEvfCausalOutcome;
  const mapping = outcomeMap[outcome];
  const cause = text(root.cause, "$evidence/cause");
  const resultSemantics = text(root.result_semantics, "$evidence/result_semantics");
  const inputCeiling = text(root.claim_ceiling, "$evidence/claim_ceiling");
  const provider = exactKeys(root.provider, ["owner", "id", "version"], "$evidence/provider");
  const providerOwner = text(provider.owner, "$evidence/provider/owner");
  const providerId = text(provider.id, "$evidence/provider/id");
  const providerVersion = text(provider.version, "$evidence/provider/version");
  const comparabilityInput = exactKeys(root.comparability, ["same_claim", "same_evaluation_request", "same_domain", "same_result_semantics"], "$evidence/comparability");
  for (const key of Object.keys(comparabilityInput)) {
    if (typeof comparabilityInput[key] !== "boolean") fail("APPLICATION_EVF_INPUT", `$evidence/comparability/${key}`, "comparability values must be Boolean");
  }
  const evaluationRequestRef = resolveRef(root.evaluation_request_ref, sources, "$evidence/evaluation_request_ref");
  const providerReceiptRef = resolveRef(root.provider_receipt_ref, sources, "$evidence/provider_receipt_ref");
  const bindings = object(root.bindings, "$evidence/bindings");
  let evidenceBinding: JsonObject;
  let joinBindings: JsonObject;
  let evidenceRefs: ApplicationEvfExactRef[];
  let finalizedScope: JsonObject | undefined;
  let caseResults: JsonObject[] | undefined;
  let effectiveCeiling = inputCeiling;

  if (routeKind === "execution-evidence") {
    const values = exactKeys(bindings, ["formal_claim_ref", "capability_assessment_ref", "obligation_ref", "obligation_set_ref", "projection_ref",
      "preservation_binding_ref", "native_source_bundle_ref", "runtime_binding_ref", "profile_ref", "environment_refs"], "$evidence/bindings");
    const formalClaimRef = resolveRef(values.formal_claim_ref, sources, "$evidence/bindings/formal_claim_ref");
    const capabilityAssessmentRef = resolveRef(values.capability_assessment_ref, sources, "$evidence/bindings/capability_assessment_ref");
    const obligationRef = resolveRef(values.obligation_ref, sources, "$evidence/bindings/obligation_ref");
    const obligationSetRef = resolveRef(values.obligation_set_ref, sources, "$evidence/bindings/obligation_set_ref");
    const projectionRef = resolveRef(values.projection_ref, sources, "$evidence/bindings/projection_ref");
    const preservationBindingRef = resolveRef(values.preservation_binding_ref, sources, "$evidence/bindings/preservation_binding_ref");
    const nativeSourceBundleRef = resolveRef(values.native_source_bundle_ref, sources, "$evidence/bindings/native_source_bundle_ref");
    const runtimeBindingRef = resolveRef(values.runtime_binding_ref, sources, "$evidence/bindings/runtime_binding_ref");
    const profileRef = resolveRef(values.profile_ref, sources, "$evidence/bindings/profile_ref");
    const environmentRefs = resolveRefs(values.environment_refs, sources, "$evidence/bindings/environment_refs");
    if (outcome === "pass") {
      let selectedRequest: JsonObject = {};
      try { selectedRequest = object(JSON.parse((sources.get(evaluationRequestRef.path) as Buffer).toString("utf8")), "$evidence/evaluation_request_ref"); }
      catch { fail("APPLICATION_EVF_REQUEST", "$evidence/evaluation_request_ref", "finalized execution request must be JSON"); }
      if (selectedRequest.schema_version !== "alchlang.finalized-execution-request/v1-candidate") {
        fail("APPLICATION_EVF_REQUEST", "$evidence/evaluation_request_ref", "PASS_BOUNDED requires a post-TDE finalized execution request");
      }
      const selected = {
        base_request_ref: selectedRequest.base_request_ref,
        obligation_set_ref: selectedRequest.obligation_set_ref,
        projection_ref: selectedRequest.projection_ref,
        preservation_binding_ref: selectedRequest.preservation_binding_ref,
      };
      const expectedRequest = finalizeApplicationExecutionRequest(selected, sources);
      if (canonical(selectedRequest) !== canonical(expectedRequest) ||
          !sameRef(expectedRequest.formal_claim_ref, formalClaimRef) ||
          !sameRef(expectedRequest.obligation_set_ref, obligationSetRef) ||
          !sameRef(expectedRequest.projection_ref, projectionRef) ||
          !sameRef(expectedRequest.preservation_binding_ref, preservationBindingRef) ||
          !sameRef(expectedRequest.runtime_ref as ApplicationEvfExactRef, runtimeBindingRef) ||
          !sameRef(expectedRequest.provider_profile_ref as ApplicationEvfExactRef, profileRef)) {
        fail("APPLICATION_EVF_REQUEST_MISMATCH", "$evidence/evaluation_request_ref", "finalized request differs from current TDE and provider bindings");
      }
      const selectedSet = object(JSON.parse((sources.get(obligationSetRef.path) as Buffer).toString("utf8")), "$evidence/bindings/obligation_set_ref");
      const selectedCapability = object(selectedSet.capability_assessment_ref, "$evidence/bindings/obligation_set_ref/capability_assessment_ref");
      if (selectedCapability.current === false ||
          !sameRef({ path: selectedCapability.path, sha256: selectedCapability.sha256,
            size_bytes: selectedCapability.size_bytes, current: true } as ApplicationEvfExactRef, capabilityAssessmentRef)) {
        fail("APPLICATION_EVF_REQUEST_MISMATCH", "$evidence/bindings/capability_assessment_ref", "capability assessment differs from selected TDE set");
      }
      const runtime = object(JSON.parse((sources.get(runtimeBindingRef.path) as Buffer).toString("utf8")), "$evidence/bindings/runtime_binding_ref");
      const profile = object(JSON.parse((sources.get(profileRef.path) as Buffer).toString("utf8")), "$evidence/bindings/profile_ref");
      if (runtime.schema_version !== "domainspec-v2.provider-runtime-binding/v1-candidate" ||
          runtime.provider_owner !== providerOwner || runtime.provider_id !== providerId ||
          runtime.provider_version !== providerVersion || runtime.currentness !== "current" ||
          profile.provider_owner !== providerOwner || profile.provider_id !== providerId || profile.provider_version !== providerVersion ||
          !sameRef(runtime.profile_ref as ApplicationEvfExactRef, profileRef)) {
        fail("APPLICATION_EVF_PROVIDER", "$evidence/provider", "declared provider identity differs from the selected runtime and profile binding");
      }
      const selectedObligation = object(JSON.parse((sources.get(obligationRef.path) as Buffer).toString("utf8")), "$evidence/bindings/obligation_ref");
      const selectedObligationId = text(selectedObligation.obligation_id, "$evidence/bindings/obligation_ref/obligation_id");
      if (!Array.isArray(selectedSet.obligations)) fail("APPLICATION_EVF_CASES", "$evidence/bindings/obligation_set_ref", "selected TDE cases are missing");
      const rows = (selectedSet.obligations as unknown[]).map((value, index) => {
        const row = object(value, `$evidence/bindings/obligation_set_ref/obligations/${index}`);
        return { obligation_id: text(row.obligation_id, `$evidence/bindings/obligation_set_ref/obligations/${index}/obligation_id`),
          case_id: text(row.case_id, `$evidence/bindings/obligation_set_ref/obligations/${index}/case_id`) };
      }).sort((left, right) => left.case_id.localeCompare(right.case_id));
      if (!rows.some(row => row.obligation_id === selectedObligationId)) {
        fail("APPLICATION_EVF_CASES", "$evidence/bindings/obligation_ref", "selected obligation is not in the finalized TDE case domain");
      }
      caseResults = rows.map(row => ({ ...row, normalized_outcome: "passed" }));
      effectiveCeiling = `Bounded by every exact selected artifact ceiling ${canonical({
        request: expectedRequest.claim_ceilings,
        cases: (selectedSet.obligations as JsonObject[]).map(row => ({ case_id: row.case_id, claim_ceiling: row.claim_ceiling })),
      })}; receipt projection only; no provider authentication, runtime guarantee, release or authority claim`;
      finalizedScope = {
        formal_claim_ref: formalClaimRef, evaluation_context_ref: expectedRequest.evaluation_context_ref,
        interpretation_model_ref: expectedRequest.interpretation_model_ref,
        obligation_set_ref: obligationSetRef, projection_ref: projectionRef, preservation_binding_ref: preservationBindingRef,
        case_domain_sha256: expectedRequest.case_domain_sha256,
        witness_input_set_sha256: expectedRequest.witness_input_set_sha256,
        domain_and_bound_sha256: expectedRequest.domain_and_bound_sha256,
      };
    }
    evidenceRefs = [evaluationRequestRef, providerReceiptRef, formalClaimRef, capabilityAssessmentRef, obligationRef, obligationSetRef, projectionRef,
      preservationBindingRef, nativeSourceBundleRef, runtimeBindingRef, profileRef, ...environmentRefs];
    evidenceBinding = { schema_version: finalizedScope ? "domainspec-v2.provider-evidence-binding/v2-candidate" : "domainspec-v2.provider-evidence-binding/v1-candidate",
      binding_id: `ProviderEvidence:${joinId}`, provider_owner: providerOwner, provider_id: providerId, provider_version: providerVersion,
      formal_claim_ref: formalClaimRef, obligation_ref: obligationRef, projection_ref: projectionRef,
      ...(finalizedScope ? { evaluation_request_ref: evaluationRequestRef, finalized_scope: finalizedScope } : {}),
      native_source_bundle_ref: nativeSourceBundleRef, runtime_binding_ref: runtimeBindingRef,
      environment_ref: environmentRefs[0]!, provider_receipt_ref: providerReceiptRef,
      execution_status: mapping.executionStatus, native_outcome: outcome, normalized_outcome: mapping.executionNormalized,
      evidence_status: mapping.evidenceStatus, residue: outcome === "pass" ? [] : [`causal-outcome:${outcome}`, `cause:${cause}`],
      authority_effect: "none", claim_ceiling: `Provider evidence binding only within: ${effectiveCeiling}` };
    joinBindings = { formal_claim_ref: formalClaimRef, capability_assessment_ref: capabilityAssessmentRef,
      obligation_set_ref: obligationSetRef, projection_ref: projectionRef, preservation_binding_ref: preservationBindingRef,
      ...(finalizedScope ? { evaluation_request_ref: evaluationRequestRef, finalized_scope: finalizedScope } : {}),
      native_source_bundle_ref: nativeSourceBundleRef, runtime_binding_ref: runtimeBindingRef, profile_ref: profileRef,
      provider_evidence_refs: [] as ApplicationEvfExactRef[], environment_refs: environmentRefs, result_semantics: resultSemantics };
  } else {
    const values = exactKeys(bindings, ["formal_claim_ref", "capability_assessment_ref", "formal_claim_lean_binding_ref", "theorem_request_ref",
      "runtime_binding_ref", "profile_ref", "environment_refs"], "$evidence/bindings");
    const formalClaimRef = resolveRef(values.formal_claim_ref, sources, "$evidence/bindings/formal_claim_ref");
    const capabilityAssessmentRef = resolveRef(values.capability_assessment_ref, sources, "$evidence/bindings/capability_assessment_ref");
    const formalClaimLeanBindingRef = resolveRef(values.formal_claim_lean_binding_ref, sources, "$evidence/bindings/formal_claim_lean_binding_ref");
    const theoremRequestRef = resolveRef(values.theorem_request_ref, sources, "$evidence/bindings/theorem_request_ref");
    if (!sameRef(evaluationRequestRef, theoremRequestRef)) fail("APPLICATION_EVF_REQUEST_MISMATCH", "$evidence/evaluation_request_ref", "theorem route must bind the exact theorem request as its evaluation request");
    const runtimeBindingRef = resolveRef(values.runtime_binding_ref, sources, "$evidence/bindings/runtime_binding_ref");
    const profileRef = resolveRef(values.profile_ref, sources, "$evidence/bindings/profile_ref");
    const environmentRefs = resolveRefs(values.environment_refs, sources, "$evidence/bindings/environment_refs");
    evidenceRefs = [evaluationRequestRef, providerReceiptRef, formalClaimRef, capabilityAssessmentRef, formalClaimLeanBindingRef,
      theoremRequestRef, runtimeBindingRef, profileRef, ...environmentRefs];
    evidenceBinding = { schema_version: "domainspec-v2.theorem-evidence-binding/v1-candidate",
      binding_id: `TheoremEvidence:${joinId}`, provider_owner: providerOwner, provider_id: providerId, provider_version: providerVersion,
      theorem_request_ref: theoremRequestRef, formal_claim_lean_binding_ref: formalClaimLeanBindingRef,
      runtime_binding_ref: runtimeBindingRef, theorem_provider_receipt_ref: providerReceiptRef,
      execution_status: mapping.executionStatus, native_outcome: mapping.theoremNative, normalized_outcome: mapping.theoremNormalized,
      evidence_status: mapping.evidenceStatus, residue: outcome === "pass" ? [] : [`causal-outcome:${outcome}`, `cause:${cause}`],
      authority_effect: "none", claim_ceiling: "theorem-in-exact-lean-model-only-no-runtime-or-release-claim" };
    joinBindings = { formal_claim_ref: formalClaimRef, capability_assessment_ref: capabilityAssessmentRef,
      formal_claim_lean_binding_ref: formalClaimLeanBindingRef, theorem_request_ref: theoremRequestRef,
      theorem_evidence_refs: [] as ApplicationEvfExactRef[], runtime_binding_ref: runtimeBindingRef, profile_ref: profileRef,
      environment_refs: environmentRefs, result_semantics: resultSemantics };
  }

  validateReceiptProjection(providerReceiptRef, sources, { routeKind: routeKind as ApplicationEvfRouteKind, provider, outcome, cause,
    requestRef: evaluationRequestRef, comparability: comparabilityInput, resultSemantics, finalizedScope, caseResults });
  const allCurrent = evidenceRefs.every(ref => ref.current);
  if (outcome === "stale" ? allCurrent : !allCurrent) {
    fail("APPLICATION_EVF_CURRENTNESS", "$evidence", outcome === "stale" ? "stale outcome requires at least one explicitly stale input reference" : "only the stale outcome may consume a non-current input reference");
  }
  const comparable = Object.values(comparabilityInput).every(value => value === true);
  if (outcome === "pass" && !comparable) fail("APPLICATION_EVF_PASS_GUARD", "$evidence/comparability", "pass requires complete semantic comparability");
  // A v2 receipt only echoes caller-supplied aggregate and case projections.
  // It cannot establish that a provider actually observed any selected case.
  if (routeKind === "execution-evidence" && outcome === "pass") {
    fail("APPLICATION_EVF_CASE_OBSERVATION_REQUIRED", "$evidence/provider_receipt_ref",
      "aggregate pass and echoed case results cannot satisfy an obligation without runner-verified case observations");
  }

  const prefix = `formalization/evf-joins/${symbol(joinId)}`;
  const files: Record<string, string> = {};
  const evidenceBindingPath = `${prefix}/${routeKind === "execution-evidence" ? "provider" : "theorem"}-evidence-binding.json`;
  const evidenceBindingBytes = json(evidenceBinding); files[evidenceBindingPath] = evidenceBindingBytes;
  const evidenceBindingRef = currentRef(evidenceBindingPath, evidenceBindingBytes);
  if (routeKind === "execution-evidence") (joinBindings.provider_evidence_refs as ApplicationEvfExactRef[]).push(evidenceBindingRef);
  else (joinBindings.theorem_evidence_refs as ApplicationEvfExactRef[]).push(evidenceBindingRef);
  const comparability = { same_claim: comparabilityInput.same_claim, same_evaluation_request: comparabilityInput.same_evaluation_request,
    same_domain: comparabilityInput.same_domain, same_result_semantics: comparabilityInput.same_result_semantics,
    route_bindings_complete: true, all_current: allCurrent };
  const revisionRoute = mapping.revisionRoute;
  const residue = outcome === "pass" ? [] : [`causal-outcome:${outcome}`, `cause:${cause}`, `revision-route:${revisionRoute}`];
  const boundedConclusion = outcome === "pass"
    ? `Exact current ${routeKind} satisfies only the selected bounded obligation under its declared ceiling.`
    : `${routeKind} did not satisfy the selected obligation: ${outcome}; ${cause}`;
  const evfJoin = { schema_version: finalizedScope ? "domainspec-v2.evf-evidence-join/v2-candidate" : "domainspec-v2.evf-evidence-join/v1-candidate", join_id: joinId, owner: "EVF",
    route_kind: routeKind, bindings: joinBindings, comparability, join_status: mapping.joinStatus,
    bounded_conclusion: boundedConclusion, residue, revision_route: revisionRoute, authority_effect: "none",
    claim_ceiling: `EVF evidence join only within: ${effectiveCeiling}; no product approval, release, runtime or authority claim` };
  const evfJoinPath = `${prefix}/evf-evidence-join.json`; const evfJoinBytes = json(evfJoin); files[evfJoinPath] = evfJoinBytes;
  const evfJoinRef = currentRef(evfJoinPath, evfJoinBytes);
  const causalJoin = { schema_version: "alchlang.evf-causal-join/v1-candidate", join_id: joinId, route_kind: routeKind,
    causal_outcome: outcome, cause, evaluation_request_ref: evaluationRequestRef, provider_receipt_ref: providerReceiptRef,
    evidence_binding_ref: evidenceBindingRef, evf_join_ref: evfJoinRef, domain_join_status: mapping.joinStatus,
    can_satisfy_obligation: outcome === "pass", revision_route: revisionRoute, residue,
    provider_execution_by_join: false, provider_result_consumed: !["unavailable", "not-evaluable"].includes(outcome),
    evidence_omitted: false, non_pass_promoted_to_pass: false, authority_effect: "none",
    claim_ceiling: `Causal EVF construction only within: ${effectiveCeiling}; no proof, product approval, release or operational authority` };
  const causalJoinPath = `${prefix}/causal-join.json`; const causalJoinBytes = json(causalJoin); files[causalJoinPath] = causalJoinBytes;
  const causalJoinRef = currentRef(causalJoinPath, causalJoinBytes);
  const trace = { schema_version: "alchlang.evf-evidence-trace/v1-candidate", join_id: joinId, route_kind: routeKind,
    input_sha256: digest(canonical(input)), causal_outcome: outcome, evidence_binding_ref: evidenceBindingRef,
    evf_join_ref: evfJoinRef, causal_join_ref: causalJoinRef, exact_input_ref_count: evidenceRefs.length,
    all_inputs_current: allCurrent, can_satisfy_obligation: outcome === "pass", provider_execution_by_join: false,
    evidence_omitted: false, non_pass_promoted_to_pass: false, authority_effect: "none" };
  const tracePath = `${prefix}/trace.json`; files[tracePath] = json(trace);
  return { evidence_binding: evidenceBinding, evf_join: evfJoin, causal_join: causalJoin, files, trace };
}

export function assertApplicationEvfEvidenceCurrent(
  input: unknown,
  sources: ReadonlyMap<string, Buffer>,
  candidate: unknown,
): void {
  if (json(candidate) !== json(joinApplicationEvfEvidence(input, sources))) {
    fail("APPLICATION_EVF_STALE", "$candidate", "evidence join differs from exact current input, causal mapping or referenced bytes");
  }
}
