import { CompilationRejected } from "./model.js";
import { digest, json, symbol } from "./domainspec-profile.js";

type JsonObject = Record<string, unknown>;
export interface ApplicationRuntimeExactRef { path: string; sha256: string; size_bytes: number; current: boolean }
export type ApplicationRuntimeStageKey = "application_commit" | "provider_acceptance" | "transport_delivery" | "business_completion";

const stageMap = {
  application_commit: "application-committed",
  provider_acceptance: "provider-accepted",
  transport_delivery: "transport-delivered",
  business_completion: "business-completed",
} as const;
const stageKeys = Object.keys(stageMap) as ApplicationRuntimeStageKey[];
const receiptKeys = ["receipt_id", "binding_ref", "operation_ref", "observed_at", "observed_stage", "outcome", "provider_evidence_ref", "correlation_ref", "claim_ceiling", "authority_effect"];
const observationKeys = ["schema_version", "observation_id", "source_receipt_digest", "binding_ref", "operation_ref", "stage", "outcome", "observed_at", "duration_ms", "correlation_ref", "sanitized_attributes", "evidence_refs", "claim_ceiling", "orodi_binding_ref", "immutable", "authority_effect"];
const orodiKeys = ["binding_id", "observation_selector", "projection_mapper_ref", "orodi_adapter_ref", "evaluator_ref", "disclosure_policy_ref", "edge_sequence", "return_edge", "runtime_control_capabilities", "evidence_boundary", "authority_effect"];

const canonical = (value: unknown): string => {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value && typeof value === "object") return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical((value as JsonObject)[key])}`).join(",")}}`;
  return JSON.stringify(value);
};
const fail = (code: string, path: string, message: string): never => { throw new CompilationRejected([{ code, path, message }]); };
const object = (value: unknown, path: string): JsonObject => {
  if (!value || typeof value !== "object" || Array.isArray(value)) fail("APPLICATION_RUNTIME_OBSERVATION_INPUT", path, "expected object");
  return value as JsonObject;
};
const exactKeys = (value: unknown, keys: string[], path: string): JsonObject => {
  const result = object(value, path);
  if (canonical(Object.keys(result).sort()) !== canonical([...keys].sort())) fail("APPLICATION_RUNTIME_OBSERVATION_INPUT", path, "unexpected or missing property");
  return result;
};
const text = (value: unknown, path: string): string => {
  if (typeof value !== "string" || !value.trim()) fail("APPLICATION_RUNTIME_OBSERVATION_INPUT", path, "expected nonempty text");
  return value as string;
};
const nullableText = (value: unknown, path: string): string | null => value === null ? null : text(value, path);
const same = (left: unknown, right: unknown): boolean => canonical(left) === canonical(right);
const currentRef = (path: string, bytes: string): ApplicationRuntimeExactRef => ({ path, sha256: digest(bytes), size_bytes: Buffer.byteLength(bytes), current: true });

function resolveRef(value: unknown, sources: ReadonlyMap<string, Buffer>, path: string): ApplicationRuntimeExactRef {
  const ref = exactKeys(value, ["path", "sha256", "size_bytes", "current"], path);
  const refPath = text(ref.path, `${path}/path`); const sha256 = text(ref.sha256, `${path}/sha256`);
  if (!/^[a-f0-9]{64}$/.test(sha256) || !Number.isInteger(ref.size_bytes) || (ref.size_bytes as number) < 0 || typeof ref.current !== "boolean") {
    fail("APPLICATION_RUNTIME_OBSERVATION_REF", path, "invalid exact reference");
  }
  if (ref.current !== true) fail("APPLICATION_RUNTIME_OBSERVATION_CURRENTNESS", path, "runtime join requires current exact evidence");
  const bytes = sources.get(refPath);
  if (!bytes) fail("APPLICATION_RUNTIME_OBSERVATION_MISSING", path, `missing exact bytes for ${refPath}`);
  const resolved = bytes as Buffer;
  if (digest(resolved) !== sha256 || resolved.length !== ref.size_bytes) fail("APPLICATION_RUNTIME_OBSERVATION_STALE", path, `exact bytes differ for ${refPath}`);
  return { path: refPath, sha256, size_bytes: ref.size_bytes as number, current: true };
}

function resolveRefs(value: unknown, sources: ReadonlyMap<string, Buffer>, path: string): ApplicationRuntimeExactRef[] {
  if (!Array.isArray(value) || value.length === 0) fail("APPLICATION_RUNTIME_OBSERVATION_INPUT", path, "expected at least one exact reference");
  const refs = (value as unknown[]).map((item, index) => resolveRef(item, sources, `${path}/${index}`));
  if (new Set(refs.map(ref => ref.path)).size !== refs.length) fail("APPLICATION_RUNTIME_OBSERVATION_INPUT", path, "reference paths must be unique");
  return refs;
}

function parsed(ref: ApplicationRuntimeExactRef, sources: ReadonlyMap<string, Buffer>, path: string): JsonObject {
  try { return object(JSON.parse((sources.get(ref.path) as Buffer).toString("utf8")), path); }
  catch { return fail("APPLICATION_RUNTIME_OBSERVATION_JSON", path, `referenced bytes are not a JSON object: ${ref.path}`); }
}

function validateOrodiBinding(ref: ApplicationRuntimeExactRef, sources: ReadonlyMap<string, Buffer>): JsonObject {
  const value = exactKeys(parsed(ref, sources, "$orodi_binding"), orodiKeys, "$orodi_binding");
  if (!same(value.edge_sequence, ["runtime", "observer", "orodi-adapter", "orodi-evaluator"]) || value.return_edge !== "prohibited") {
    fail("APPLICATION_RUNTIME_OBSERVATION_ORODI_EDGE", "$orodi_binding", "ORODI must have one forward observation edge and no return edge");
  }
  const capabilities = exactKeys(value.runtime_control_capabilities, ["select_retries", "write_provider_state", "call_apis", "deploy", "enact_business_effects"], "$orodi_binding/runtime_control_capabilities");
  if (Object.values(capabilities).some(item => item !== false)) fail("APPLICATION_RUNTIME_OBSERVATION_ORODI_CONTROL", "$orodi_binding/runtime_control_capabilities", "ORODI runtime control is forbidden");
  if (value.authority_effect !== "none") fail("APPLICATION_RUNTIME_OBSERVATION_AUTHORITY", "$orodi_binding/authority_effect", "authority growth is forbidden");
  for (const field of ["binding_id", "observation_selector", "projection_mapper_ref", "orodi_adapter_ref", "evaluator_ref", "disclosure_policy_ref", "evidence_boundary"]) {
    text(value[field], `$orodi_binding/${field}`);
  }
  return value;
}

function validateCleanup(ref: ApplicationRuntimeExactRef, sources: ReadonlyMap<string, Buffer>): JsonObject {
  const value = exactKeys(parsed(ref, sources, "$cleanup"), ["schema_version", "run_id", "cleanup_observed", "temporary_resources_removed", "owned_residue", "authority_effect", "claim_ceiling"], "$cleanup");
  if (value.schema_version !== "alchlang.runtime-cleanup-report/v1-candidate" || value.cleanup_observed !== true || value.temporary_resources_removed !== true ||
      !Array.isArray(value.owned_residue) || value.owned_residue.length !== 0 || value.authority_effect !== "none") {
    fail("APPLICATION_RUNTIME_OBSERVATION_CLEANUP", "$cleanup", "cleanup must be observed, remove all owned resources and retain no authority effect");
  }
  text(value.run_id, "$cleanup/run_id"); text(value.claim_ceiling, "$cleanup/claim_ceiling");
  return value;
}

function validateStage(
  key: ApplicationRuntimeStageKey,
  value: unknown,
  sources: ReadonlyMap<string, Buffer>,
  orodiBindingId: string,
  runId: string,
) {
  const path = `$stages/${key}`;
  const stage = exactKeys(value, ["runtime_receipt_ref", "observation_ref"], path);
  if (stage.runtime_receipt_ref === null || stage.observation_ref === null) {
    if (stage.runtime_receipt_ref !== null || stage.observation_ref !== null) fail("APPLICATION_RUNTIME_OBSERVATION_PAIR", path, "receipt and observation must both be present or both be null");
    return { stage_key: key, domain_stage: stageMap[key], status: "not-observed", runtime_receipt_ref: null, observation_ref: null,
      outcome: null, receipt_id: null, observation_id: null };
  }
  const receiptRef = resolveRef(stage.runtime_receipt_ref, sources, `${path}/runtime_receipt_ref`);
  const observationRef = resolveRef(stage.observation_ref, sources, `${path}/observation_ref`);
  const receipt = exactKeys(parsed(receiptRef, sources, `${path}/receipt`), receiptKeys, `${path}/receipt`);
  const observation = exactKeys(parsed(observationRef, sources, `${path}/observation`), observationKeys, `${path}/observation`);
  const expectedStage = stageMap[key];
  if (receipt.observed_stage !== expectedStage || receipt.claim_ceiling !== expectedStage || observation.stage !== expectedStage || observation.claim_ceiling !== expectedStage) {
    fail("APPLICATION_RUNTIME_OBSERVATION_STAGE", path, `receipt and observation must both be bounded to ${expectedStage}`);
  }
  if (receipt.authority_effect !== "none" || observation.schema_version !== "domainspec.integration-observation/v1-candidate" ||
      observation.immutable !== true || observation.authority_effect !== "none") {
    fail("APPLICATION_RUNTIME_OBSERVATION_CONTRACT", path, "receipt or observation contract is invalid");
  }
  const outcome = text(receipt.outcome, `${path}/receipt/outcome`);
  if (!["accepted", "rejected", "failed", "unknown"].includes(outcome) || observation.outcome !== outcome) fail("APPLICATION_RUNTIME_OBSERVATION_OUTCOME", path, "receipt and observation outcomes differ or are invalid");
  const observedAt = text(receipt.observed_at, `${path}/receipt/observed_at`);
  if (!Number.isFinite(Date.parse(observedAt)) || observation.observed_at !== observedAt ||
      observation.binding_ref !== receipt.binding_ref || observation.operation_ref !== receipt.operation_ref ||
      observation.correlation_ref !== receipt.correlation_ref) fail("APPLICATION_RUNTIME_OBSERVATION_IDENTITY", path, "observation does not preserve exact receipt identity");
  if (receipt.correlation_ref !== runId) fail("APPLICATION_RUNTIME_OBSERVATION_RUN", path, "stage receipt is not correlated to the cleanup run");
  if (observation.source_receipt_digest !== digest(canonical(receipt))) fail("APPLICATION_RUNTIME_OBSERVATION_DIGEST", path, "observation source receipt digest differs");
  if (observation.orodi_binding_ref !== orodiBindingId) fail("APPLICATION_RUNTIME_OBSERVATION_ORODI_BINDING", path, "observation points to a different ORODI binding");
  return { stage_key: key, domain_stage: expectedStage, status: "observed", runtime_receipt_ref: receiptRef, observation_ref: observationRef,
    outcome, receipt_id: text(receipt.receipt_id, `${path}/receipt/receipt_id`), observation_id: text(observation.observation_id, `${path}/observation/observation_id`) };
}

/** Forms an exact, construction-only join over independent runtime observations. */
export function joinApplicationRuntimeObservations(input: unknown, sources: ReadonlyMap<string, Buffer>) {
  const root = exactKeys(input, ["schema_version", "join_id", "source_ref", "compiled_graph_ref", "provider_selection_ref", "generated_artifact_refs",
    "runtime_environment_ref", "orodi_binding_ref", "cleanup_report_ref", "stages", "claim_ceiling"], "$runtime_observations");
  if (root.schema_version !== "alchlang.runtime-observation-bindings/v1") fail("APPLICATION_RUNTIME_OBSERVATION_INPUT", "$runtime_observations/schema_version", "unsupported binding version");
  const joinId = text(root.join_id, "$runtime_observations/join_id"); const inputCeiling = text(root.claim_ceiling, "$runtime_observations/claim_ceiling");
  const sourceRef = resolveRef(root.source_ref, sources, "$runtime_observations/source_ref");
  const compiledGraphRef = resolveRef(root.compiled_graph_ref, sources, "$runtime_observations/compiled_graph_ref");
  const providerSelectionRef = resolveRef(root.provider_selection_ref, sources, "$runtime_observations/provider_selection_ref");
  const generatedArtifactRefs = resolveRefs(root.generated_artifact_refs, sources, "$runtime_observations/generated_artifact_refs");
  const runtimeEnvironmentRef = resolveRef(root.runtime_environment_ref, sources, "$runtime_observations/runtime_environment_ref");
  const orodiBindingRef = resolveRef(root.orodi_binding_ref, sources, "$runtime_observations/orodi_binding_ref");
  const cleanupReportRef = resolveRef(root.cleanup_report_ref, sources, "$runtime_observations/cleanup_report_ref");
  const orodi = validateOrodiBinding(orodiBindingRef, sources);
  const cleanup = validateCleanup(cleanupReportRef, sources);
  const runId = cleanup.run_id as string;
  const stagesInput = exactKeys(root.stages, stageKeys, "$runtime_observations/stages");
  const stages = Object.fromEntries(stageKeys.map(key => [key, validateStage(key, stagesInput[key], sources, orodi.binding_id as string, runId)])) as Record<ApplicationRuntimeStageKey, ReturnType<typeof validateStage>>;
  const observedStages = stageKeys.filter(key => stages[key].status === "observed");
  const stageEvidenceRefs = observedStages.flatMap(key => [stages[key].runtime_receipt_ref, stages[key].observation_ref]);
  const prefix = `runtime-observations/${symbol(joinId)}`;
  const join = { schema_version: "alchlang.runtime-observation-join/v1-candidate", join_id: joinId,
    source_ref: sourceRef, compiled_graph_ref: compiledGraphRef, provider_selection_ref: providerSelectionRef,
    generated_artifact_refs: generatedArtifactRefs, runtime_environment_ref: runtimeEnvironmentRef,
    orodi_binding_ref: orodiBindingRef, cleanup_report_ref: cleanupReportRef, stages,
    observed_stage_count: observedStages.length, all_stages_independently_observed: observedStages.length === stageKeys.length,
    stage_inference_used: false, orodi_projection: { edge_sequence: orodi.edge_sequence, return_edge: "prohibited",
      runtime_control_capabilities: orodi.runtime_control_capabilities }, temporary_resources_removed: true,
    authority_effect: "none", claim_ceiling: `Exact stage-separated runtime evidence only within: ${inputCeiling}; no production, delivery, completion or authority inference beyond an observed stage` };
  const joinPath = `${prefix}/runtime-observation-join.json`; const joinBytes = json(join);
  const files: Record<string, string> = { [joinPath]: joinBytes };
  const joinRef = currentRef(joinPath, joinBytes);
  const trace = { schema_version: "alchlang.runtime-observation-trace/v1-candidate", join_id: joinId,
    input_sha256: digest(canonical(input)), join_ref: joinRef, exact_static_ref_count: 6 + generatedArtifactRefs.length,
    exact_stage_evidence_ref_count: stageEvidenceRefs.length, observed_stages: observedStages,
    stage_inference_used: false, orodi_return_edge: false, orodi_runtime_control: false,
    runtime_executed_by_join: false, cleanup_verified: true, authority_effect: "none" };
  const tracePath = `${prefix}/trace.json`; files[tracePath] = json(trace);
  return { join, files, trace };
}

export function assertApplicationRuntimeObservationsCurrent(input: unknown, sources: ReadonlyMap<string, Buffer>, candidate: unknown): void {
  if (json(candidate) !== json(joinApplicationRuntimeObservations(input, sources))) {
    fail("APPLICATION_RUNTIME_OBSERVATION_STALE", "$candidate", "runtime observation join differs from exact inputs or stage-separation rules");
  }
}
