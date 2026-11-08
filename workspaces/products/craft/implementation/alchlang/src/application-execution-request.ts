import { CompilationRejected } from "./model.js";
import { digest } from "./domainspec-profile.js";

type JsonObject = Record<string, unknown>;
export interface ExactExecutionSourceRef {
  path: string;
  sha256: string;
  size_bytes: number;
  current: true;
}
export interface ExecutionRequestSelection {
  base_request_ref: ExactExecutionSourceRef;
  obligation_set_ref: ExactExecutionSourceRef;
  projection_ref: ExactExecutionSourceRef;
  preservation_binding_ref: ExactExecutionSourceRef;
}

const canonical = (value: unknown): string => {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value !== null && typeof value === "object") {
    const item = value as JsonObject;
    return `{${Object.keys(item).sort().map(key => `${JSON.stringify(key)}:${canonical(item[key])}`).join(",")}}`;
  }
  return JSON.stringify(value) ?? "null";
};
const fail = (code: string, where: string, message: string): never => {
  throw new CompilationRejected([{ code, path: where, message }]);
};
const object = (value: unknown, where: string): JsonObject => {
  if (!value || typeof value !== "object" || Array.isArray(value)) fail("APPLICATION_EXECUTION_INPUT", where, "expected object");
  return value as JsonObject;
};
const text = (value: unknown, where: string): string => {
  if (typeof value !== "string" || !value.trim()) fail("APPLICATION_EXECUTION_INPUT", where, "expected nonempty text");
  return value as string;
};
const array = (value: unknown, where: string): unknown[] => {
  if (!Array.isArray(value)) fail("APPLICATION_EXECUTION_INPUT", where, "expected array");
  return value as unknown[];
};
const equal = (left: unknown, right: unknown) => canonical(left) === canonical(right);
const exactKeys = (value: unknown, keys: readonly string[], where: string): JsonObject => {
  const item = object(value, where);
  if (!equal(Object.keys(item).sort(), [...keys].sort())) fail("APPLICATION_EXECUTION_INPUT", where, "unexpected or missing property");
  return item;
};
const digestText = (value: unknown, where: string): string => {
  if (typeof value !== "string" || !/^[a-f0-9]{64}$/.test(value)) fail("APPLICATION_EXECUTION_INPUT", where, "expected SHA-256 digest");
  return value as string;
};
const textSet = (value: unknown, where: string): string[] => {
  const values = array(value, where).map((item, index) => text(item, `${where}/${index}`));
  if (new Set(values).size !== values.length) fail("APPLICATION_EXECUTION_INPUT", where, "values must be unique");
  return values;
};

function ref(value: unknown, where: string, requireCurrent: boolean): ExactExecutionSourceRef {
  const item = object(value, where);
  const keys = Object.keys(item).sort();
  if (!equal(keys, requireCurrent ? ["current", "path", "sha256", "size_bytes"] :
      item.current === undefined ? ["path", "sha256", "size_bytes"] : ["current", "path", "sha256", "size_bytes"])) {
    fail("APPLICATION_EXECUTION_REF", where, "unexpected or missing exact reference member");
  }
  const path = text(item.path, `${where}/path`);
  if (!/^[a-f0-9]{64}$/.test(String(item.sha256)) || !Number.isInteger(item.size_bytes) || (item.size_bytes as number) < 1 ||
      (item.current !== undefined && item.current !== true) || (requireCurrent && item.current !== true)) {
    fail("APPLICATION_EXECUTION_REF", where, "reference must name nonempty current bytes with exact SHA-256 and size");
  }
  return { path, sha256: item.sha256 as string, size_bytes: item.size_bytes as number, current: true };
}

function sameRef(left: unknown, right: ExactExecutionSourceRef, where: string): void {
  if (!equal(ref(left, where, false), right)) fail("APPLICATION_EXECUTION_JOIN", where, "exact selected reference differs");
}

function decode(selected: ExactExecutionSourceRef, sources: ReadonlyMap<string, Buffer>, where: string): JsonObject {
  const bytes = sources.get(selected.path);
  if (bytes === undefined) return fail("APPLICATION_EXECUTION_MISSING", where, `selected bytes missing for ${selected.path}`);
  if (bytes.length !== selected.size_bytes || digest(bytes) !== selected.sha256) {
    fail("APPLICATION_EXECUTION_STALE", where, `selected bytes differ for ${selected.path}`);
  }
  try { return object(JSON.parse(bytes.toString("utf8")), where); }
  catch { return fail("APPLICATION_EXECUTION_INPUT", where, "selected artifact is not JSON object"); }
}

/** Finalizes a request only after TDE has materialized the selected neutral
 * obligation set. This constructs no provider result or runtime observation. */
export function finalizeApplicationExecutionRequest(input: unknown, sources: ReadonlyMap<string, Buffer>) {
  const selection = exactKeys(input, ["base_request_ref", "obligation_set_ref", "preservation_binding_ref", "projection_ref"], "$selection");
  const baseRef = ref(selection.base_request_ref, "$selection/base_request_ref", true);
  const obligationsRef = ref(selection.obligation_set_ref, "$selection/obligation_set_ref", true);
  const projectionRef = ref(selection.projection_ref, "$selection/projection_ref", true);
  const preservationRef = ref(selection.preservation_binding_ref, "$selection/preservation_binding_ref", true);
  const base = exactKeys(decode(baseRef, sources, "$base"), ["schema_version", "request_id", "request_state",
    "formal_claim_ref", "evaluation_context_ref", "route_binding_ref", "provider_profile_ref", "runtime_ref",
    "execution_policy", "authority_effect", "release_admission", "claim_ceiling", "residue"], "$base");
  if (base.schema_version !== "alchlang.verification-request/v1-candidate" || base.request_state !== "ready" ||
      base.authority_effect !== "none" || base.release_admission !== "not-granted" || !equal(base.residue, [])) {
    fail("APPLICATION_EXECUTION_BASE", "$base", "base request is not a ready, nonauthorizing v1 request");
  }
  const claimRef = ref(base.formal_claim_ref, "$base/formal_claim_ref", true);
  decode(claimRef, sources, "$claim");
  const contextRef = ref(base.evaluation_context_ref, "$base/evaluation_context_ref", true);
  const context = exactKeys(decode(contextRef, sources, "$context"), ["schema_version", "context_id", "version", "status",
    "formal_claim_ref", "interpretation_model_ref", "route_binding_ref", "provider_profile_ref", "runtime_ref",
    "assumptions", "limits", "context_ceiling", "authority_effect"], "$context");
  if (context.schema_version !== "domainspec-v2.evaluation-context/v1-candidate" || context.authority_effect !== "none" ||
      !["reviewed", "accepted"].includes(String(context.status))) {
    fail("APPLICATION_EXECUTION_CONTEXT", "$context", "evaluation context must be reviewed or accepted and nonauthorizing");
  }
  sameRef(context.formal_claim_ref, claimRef, "$context/formal_claim_ref");
  text(context.context_id, "$context/context_id");
  text(context.version, "$context/version");
  textSet(context.assumptions, "$context/assumptions");
  textSet(context.limits, "$context/limits");
  for (const field of ["route_binding_ref", "provider_profile_ref", "runtime_ref"] as const) {
    const selected = ref(base[field], `$base/${field}`, true);
    sameRef(context[field], selected, `$context/${field}`);
    decode(selected, sources, `$${field}`);
  }
  const policy = exactKeys(base.execution_policy, ["timeout_ms", "memory_ceiling_bytes", "max_output_bytes", "network",
    "working_directory", "environment_allowlist"], "$base/execution_policy");
  if (policy.network !== "forbidden" || !Number.isSafeInteger(policy.timeout_ms) || (policy.timeout_ms as number) < 1 ||
      !Number.isSafeInteger(policy.memory_ceiling_bytes) || (policy.memory_ceiling_bytes as number) < 1 ||
      !Number.isSafeInteger(policy.max_output_bytes) || (policy.max_output_bytes as number) < 1 ||
      !Array.isArray(policy.environment_allowlist)) {
    fail("APPLICATION_EXECUTION_BASE", "$base/execution_policy", "bounded execution policy is invalid");
  }
  text(policy.working_directory, "$base/execution_policy/working_directory");
  if (!/^(?!\/)(?!.*(?:^|\/)\.\.?(?:\/|$))[A-Za-z0-9_.-]+(?:\/[A-Za-z0-9_.-]+)*$/.test(policy.working_directory as string)) {
    fail("APPLICATION_EXECUTION_BASE", "$base/execution_policy/working_directory", "working directory must be a bounded relative path");
  }
  const environmentAllowlist = textSet(policy.environment_allowlist, "$base/execution_policy/environment_allowlist");
  if (environmentAllowlist.some(name => !/^[A-Z][A-Z0-9_]*$/.test(name))) {
    fail("APPLICATION_EXECUTION_BASE", "$base/execution_policy/environment_allowlist", "invalid environment name");
  }
  const providerProfileRef = ref(base.provider_profile_ref, "$base/provider_profile_ref", true);
  const runtimeRef = ref(base.runtime_ref, "$base/runtime_ref", true);
  const runtime = exactKeys(decode(runtimeRef, sources, "$runtime"), ["schema_version", "runtime_binding_id", "provider_owner",
    "provider_id", "provider_version", "provider_digest", "profile_ref", "input_artifact_ref", "command",
    "working_directory", "environment_allowlist", "fixture_refs", "limits", "network", "supported_outcomes",
    "currentness", "authority_effect", "claim_ceiling"], "$runtime");
  if (runtime.schema_version !== "domainspec-v2.provider-runtime-binding/v1-candidate" || runtime.currentness !== "current" ||
      runtime.authority_effect !== "none" || runtime.network !== "forbidden" ||
      runtime.claim_ceiling !== "runtime-binding-only-no-execution-claim") {
    fail("APPLICATION_EXECUTION_RUNTIME", "$runtime", "current nonauthorizing provider runtime binding is required");
  }
  for (const field of ["runtime_binding_id", "provider_owner", "provider_id", "provider_version"] as const) text(runtime[field], `$runtime/${field}`);
  digestText(runtime.provider_digest, "$runtime/provider_digest");
  sameRef(runtime.profile_ref, providerProfileRef, "$runtime/profile_ref");
  decode(ref(runtime.input_artifact_ref, "$runtime/input_artifact_ref", true), sources, "$runtime/input_artifact");
  array(runtime.command, "$runtime/command").forEach((item, index) => text(item, `$runtime/command/${index}`));
  if (!array(runtime.command, "$runtime/command").length ||
      runtime.working_directory !== policy.working_directory ||
      !equal([...textSet(runtime.environment_allowlist, "$runtime/environment_allowlist")].sort(), [...environmentAllowlist].sort()) ||
      !equal(exactKeys(runtime.limits, ["timeout_ms", "memory_ceiling_bytes", "max_output_bytes"], "$runtime/limits"),
        { timeout_ms: policy.timeout_ms, memory_ceiling_bytes: policy.memory_ceiling_bytes, max_output_bytes: policy.max_output_bytes }) ||
      !textSet(runtime.supported_outcomes, "$runtime/supported_outcomes").includes("passed")) {
    fail("APPLICATION_EXECUTION_RUNTIME", "$runtime", "runtime command, limits, environment or outcomes differ from the bounded request");
  }
  array(runtime.fixture_refs, "$runtime/fixture_refs").forEach((item, index) =>
    decode(ref(item, `$runtime/fixture_refs/${index}`, true), sources, `$runtime/fixture_refs/${index}`));
  const interpretationRef = context.interpretation_model_ref === null ? null : ref(context.interpretation_model_ref, "$context/interpretation_model_ref", true);
  if (interpretationRef) decode(interpretationRef, sources, "$interpretation");
  const obligationSet = exactKeys(decode(obligationsRef, sources, "$obligation_set"), ["schema_version", "obligation_set_id", "owner",
    "formal_claim_ref", "capability_assessment_ref", "projection_ref", "derivation_profile_ref", "derivation_status",
    "obligations", "residue", "determinism", "authority_effect", "claim_ceiling"], "$obligation_set");
  if (obligationSet.schema_version !== "domainspec-v2.neutral-obligation-set/v1-candidate" || obligationSet.owner !== "TDE" ||
      obligationSet.derivation_status !== "derived" || obligationSet.authority_effect !== "none") {
    fail("APPLICATION_EXECUTION_OBLIGATIONS", "$obligation_set", "TDE obligation set is not derived and current");
  }
  sameRef(obligationSet.formal_claim_ref, claimRef, "$obligation_set/formal_claim_ref");
  text(obligationSet.obligation_set_id, "$obligation_set/obligation_set_id");
  const capabilityRef = ref(obligationSet.capability_assessment_ref, "$obligation_set/capability_assessment_ref", false);
  const capability = exactKeys(decode(capabilityRef, sources, "$capability_assessment"), ["schema_version", "assessment_id", "owner",
    "formal_claim_ref", "policy_ref", "classification", "needs_formal_reasons", "admitted_for_tde_execution",
    "provider_route", "currentness", "authority_effect", "claim_ceiling"], "$capability_assessment");
  if (capability.schema_version !== "domainspec-v2.formal-claim-capability-assessment/v1-candidate" ||
      capability.owner !== "validation-governance" || capability.classification !== "executable-bounded" ||
      capability.admitted_for_tde_execution !== true || capability.provider_route !== "tde" ||
      capability.currentness !== "current" || capability.authority_effect !== "none" ||
      capability.claim_ceiling !== "classification-and-routing-only-no-execution-claim" ||
      !equal(capability.needs_formal_reasons, [])) {
    fail("APPLICATION_EXECUTION_CAPABILITY", "$capability_assessment", "current admitted executable-bounded TDE assessment is required");
  }
  text(capability.assessment_id, "$capability_assessment/assessment_id");
  sameRef(capability.formal_claim_ref, claimRef, "$capability_assessment/formal_claim_ref");
  decode(ref(capability.policy_ref, "$capability_assessment/policy_ref", false), sources, "$capability_policy");
  const derivationProfileRef = ref(obligationSet.derivation_profile_ref, "$obligation_set/derivation_profile_ref", false);
  decode(derivationProfileRef, sources, "$derivation_profile");
  const determinism = exactKeys(obligationSet.determinism, ["algorithm_ref", "input_digest", "output_digest"], "$obligation_set/determinism");
  const algorithmRef = ref(determinism.algorithm_ref, "$obligation_set/determinism/algorithm_ref", false);
  decode(algorithmRef, sources, "$derivation_algorithm");
  digestText(determinism.input_digest, "$obligation_set/determinism/input_digest");
  digestText(determinism.output_digest, "$obligation_set/determinism/output_digest");
  if (obligationSet.projection_ref !== null) sameRef(obligationSet.projection_ref, projectionRef, "$obligation_set/projection_ref");
  const residue = array(obligationSet.residue, "$obligation_set/residue");
  if (residue.some((item, index) => {
    const entry = exactKeys(item, ["code", "message", "blocking"], `$obligation_set/residue/${index}`);
    text(entry.code, `$obligation_set/residue/${index}/code`);
    text(entry.message, `$obligation_set/residue/${index}/message`);
    if (typeof entry.blocking !== "boolean") fail("APPLICATION_EXECUTION_INPUT", `$obligation_set/residue/${index}/blocking`, "expected Boolean");
    return entry.blocking;
  })) {
    fail("APPLICATION_EXECUTION_OBLIGATIONS", "$obligation_set/residue", "blocking TDE residue remains");
  }
  const obligations = array(obligationSet.obligations, "$obligation_set/obligations");
  if (!obligations.length) fail("APPLICATION_EXECUTION_CASES", "$obligation_set/obligations", "at least one selected case is required");
  const rows = obligations.map((value, index) => {
    const where = `$obligation_set/obligations/${index}`;
    const item = exactKeys(value, ["obligation_id", "case_id", "kind", "normalized_inputs", "expected_relation_or_oracle",
      "source_basis", "case_class", "status", "claim_ceiling"], where);
    const obligationId = text(item.obligation_id, `${where}/obligation_id`);
    const caseId = text(item.case_id, `${where}/case_id`);
    if (item.status !== "ready") fail("APPLICATION_EXECUTION_CASES", where, "every selected TDE case must be ready");
    const inputs = object(item.normalized_inputs, `${where}/normalized_inputs`);
    const oracle = text(item.expected_relation_or_oracle, `${where}/expected_relation_or_oracle`);
    const kind = text(item.kind, `${where}/kind`);
    const caseClass = text(item.case_class, `${where}/case_class`);
    if (!["property", "witness", "counterexample", "boundary", "vacuity", "runtime-conformance"].includes(kind) ||
        !["positive", "negative", "boundary", "vacuity"].includes(caseClass)) {
      fail("APPLICATION_EXECUTION_CASES", where, "unsupported obligation kind or case class");
    }
    textSet(item.source_basis, `${where}/source_basis`);
    text(item.claim_ceiling, `${where}/claim_ceiling`);
    return { obligation_id: obligationId, case_id: caseId, kind, case_class: caseClass,
      normalized_inputs: inputs, expected_relation_or_oracle: oracle };
  });
  if (new Set(rows.map(item => item.case_id)).size !== rows.length) {
    fail("APPLICATION_EXECUTION_CASES", "$obligation_set/obligations", "case identities must be unique; one obligation may have multiple cases");
  }
  const projection = exactKeys(decode(projectionRef, sources, "$projection"), ["schema_version", "projection_id", "owner",
    "formal_claim_ref", "capability_assessment_ref", "obligation_set_ref", "purpose", "target_profile_ref",
    "source_semantics_digest", "projected_semantics_digest", "domain_and_bound", "preservation_kind", "currentness",
    "authority_effect", "claim_ceiling"], "$projection");
  if (projection.schema_version !== "domainspec-v2.formalization-projection/v1-candidate" || projection.currentness !== "current" ||
      projection.purpose !== "tde-executable-slice" || projection.preservation_kind !== "exact-equivalent" || projection.authority_effect !== "none") {
    fail("APPLICATION_EXECUTION_PROJECTION", "$projection", "current exact-equivalent TDE projection is required");
  }
  sameRef(projection.formal_claim_ref, claimRef, "$projection/formal_claim_ref");
  sameRef(projection.capability_assessment_ref, capabilityRef, "$projection/capability_assessment_ref");
  sameRef(projection.target_profile_ref, derivationProfileRef, "$projection/target_profile_ref");
  text(projection.projection_id, "$projection/projection_id");
  digestText(projection.source_semantics_digest, "$projection/source_semantics_digest");
  digestText(projection.projected_semantics_digest, "$projection/projected_semantics_digest");
  if (projection.obligation_set_ref !== null) sameRef(projection.obligation_set_ref, obligationsRef, "$projection/obligation_set_ref");
  if (obligationSet.projection_ref === null && projection.obligation_set_ref === null) {
    fail("APPLICATION_EXECUTION_JOIN", "$projection/obligation_set_ref", "projection and obligation set must bind in at least one direction");
  }
  const domainAndBound = text(projection.domain_and_bound, "$projection/domain_and_bound");
  const preservation = exactKeys(decode(preservationRef, sources, "$preservation"), ["schema_version", "binding_id", "owner",
    "projection_ref", "direction", "kind", "preserved_semantics", "known_losses", "unsupported_constructs",
    "validation_method", "certificate_ref", "status", "authority_effect", "claim_ceiling"], "$preservation");
  if (preservation.schema_version !== "domainspec-v2.preservation-binding/v1-candidate" || preservation.status !== "preserved" ||
      preservation.direction !== "bidirectional" || preservation.authority_effect !== "none" ||
      !equal(preservation.known_losses, []) || !equal(preservation.unsupported_constructs, [])) {
    fail("APPLICATION_EXECUTION_PRESERVATION", "$preservation", "complete bidirectional preservation is required");
  }
  sameRef(preservation.projection_ref, projectionRef, "$preservation/projection_ref");
  text(preservation.binding_id, "$preservation/binding_id");
  text(preservation.validation_method, "$preservation/validation_method");
  if (!["syntactic-by-construction", "certificate-backed", "review-backed"].includes(String(preservation.kind)) ||
      !textSet(preservation.preserved_semantics, "$preservation/preserved_semantics").length) {
    fail("APPLICATION_EXECUTION_PRESERVATION", "$preservation", "preservation kind and covered semantics must be explicit");
  }
  textSet(preservation.known_losses, "$preservation/known_losses");
  textSet(preservation.unsupported_constructs, "$preservation/unsupported_constructs");
  if (preservation.kind === "certificate-backed") {
    const certificateRef = ref(preservation.certificate_ref, "$preservation/certificate_ref", false);
    decode(certificateRef, sources, "$preservation_certificate");
  } else if (preservation.certificate_ref !== null) {
    fail("APPLICATION_EXECUTION_PRESERVATION", "$preservation/certificate_ref", "non-certificate preservation cannot imply a certificate");
  }
  const caseDomain = rows.map(({ obligation_id, case_id, kind, case_class }) => ({ obligation_id, case_id, kind, case_class }))
    .sort((left, right) => left.case_id.localeCompare(right.case_id));
  const witnessInputs = rows.map(({ obligation_id, case_id, normalized_inputs, expected_relation_or_oracle }) =>
    ({ obligation_id, case_id, normalized_inputs, expected_relation_or_oracle }))
    .sort((left, right) => left.case_id.localeCompare(right.case_id));
  const body = {
    schema_version: "alchlang.finalized-execution-request/v1-candidate" as const,
    base_request_id: text(base.request_id, "$base/request_id"), request_state: "ready" as const,
    base_request_ref: baseRef, formal_claim_ref: claimRef, evaluation_context_ref: contextRef,
    interpretation_model_ref: interpretationRef, obligation_set_ref: obligationsRef, projection_ref: projectionRef,
    preservation_binding_ref: preservationRef, route_binding_ref: base.route_binding_ref,
    provider_profile_ref: base.provider_profile_ref, runtime_ref: base.runtime_ref,
    execution_policy: base.execution_policy, selected_case_ids: caseDomain.map(item => item.case_id),
    case_domain_sha256: digest(canonical(caseDomain)), witness_input_set_sha256: digest(canonical(witnessInputs)),
    domain_and_bound: domainAndBound, domain_and_bound_sha256: digest(domainAndBound),
    selected_case_count: rows.length, provider_execution_observed: false as const,
    release_admission: "not-granted" as const, authority_effect: "none" as const,
    claim_ceilings: {
      base_request: text(base.claim_ceiling, "$base/claim_ceiling"),
      evaluation_context: text(context.context_ceiling, "$context/context_ceiling"),
      capability_assessment: text(capability.claim_ceiling, "$capability_assessment/claim_ceiling"),
      obligation_set: text(obligationSet.claim_ceiling, "$obligation_set/claim_ceiling"),
      projection: text(projection.claim_ceiling, "$projection/claim_ceiling"),
      preservation_binding: text(preservation.claim_ceiling, "$preservation/claim_ceiling"),
    },
    claim_ceiling: "Intersection of exact selected artifact ceilings; request construction only, with no provider result, proof, runtime guarantee, release or authority claim",
  };
  return { ...body, request_id: `FinalizedExecutionRequest:${digest(canonical(body))}` };
}
