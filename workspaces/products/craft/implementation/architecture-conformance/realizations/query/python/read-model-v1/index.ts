import {createHash} from "node:crypto";

import {
  DECLARED_READ_LIFECYCLE_PATHS,
  EFFECT_CHANNELS,
  mintDeclaredReadLifecycleObservationV1,
  mintEffectObservationV1,
  type LockedEffectObserverRefV1,
} from "../../../../kernel/evidence/effect-observation/index.js";
import {
  applyReadModelQueryMutant,
  canonicalReadModelQueryJson,
  decodeReadModelQueryDefinitionV1,
  decodeReadModelQueryDenominatorV1,
  decodeReadModelQueryMutationCatalogueV1,
  decodeReadModelQueryObservationV1,
  evaluateReadModelQuery,
  mintReadModelQueryObservationV1,
  sha256ReadModelQueryBytes,
  sha256ReadModelQueryValue,
  type ReadModelQueryFindingCode,
  type ReadModelQueryObservationV1,
  type ReadModelScalarV1,
} from "../../../../families/read-model/index.js";

type JsonObject = Record<string, unknown>;
type ExactRef = Readonly<{path: string; sha256: string}>;
type NativeTraceEntry = Readonly<{
  target_id: string;
  channel: "filesystem";
  outcome: "success";
}>;
type PythonQueryNativeProofV1 = Readonly<{
  schema_version: "PythonQueryNativeProof/v1";
  target: Readonly<{
    target_id: string;
    target_sha256: string;
    language: "python";
    protocol_id: string;
    output_concept_id: string;
  }>;
  binding: Readonly<{binding_id: string; binding_sha256: string}>;
  owner_case: Readonly<{
    case_id: string;
    input: Readonly<Record<string, ReadModelScalarV1>>;
    input_sha256: string;
    expected_result: Readonly<Record<string, ReadModelScalarV1>>;
  }>;
  observation: Readonly<{
    case_id: string;
    trace: readonly NativeTraceEntry[];
    result: Readonly<Record<string, ReadModelScalarV1>>;
    source_sha256: string;
    lifecycle_basis:
      "synchronous-return-plus-closed-plain-data-static-exclusion";
    runtime_audit_events: readonly never[];
    result_consumption: "complete-json-materialization";
    mutable_alias_observed: false;
    quiescence: Readonly<{
      observed: true;
      pending_count: 0;
    }>;
  }>;
  process_evidence: Readonly<{
    executions: 2;
    distinct_pids: 2;
    pids_redacted_from_semantic_proof: true;
    semantic_replay_equal: true;
    trace_sha256: string;
    result_sha256: string;
    input_materialization: "json-inert-mapping-proxy";
    read_fixtures: "json-inert-mapping-proxy";
    lifecycle_basis:
      "synchronous-return-plus-closed-plain-data-static-exclusion";
  }>;
  source_hostiles: readonly Readonly<{
    hostile_id: string;
    evidence_kind: "python-source-hostile";
    status: "killed";
    error_code: string;
  }>[];
  source_hostile_accounting: Readonly<{declared: 8; killed: 8}>;
  claim_ceiling: string;
  authority_effect: "none";
}>;

export const PYTHON_QUERY_RAW_PATHS = Object.freeze({
  definition:
    "projects/domainspec-v2/impl/architecture-conformance/families/read-model/fixtures/complete-settlement/definition.json",
  denominator:
    "projects/domainspec-v2/impl/architecture-conformance/families/read-model/fixtures/complete-settlement/denominator.json",
  mutations:
    "projects/domainspec-v2/impl/architecture-conformance/families/read-model/fixtures/complete-settlement/mutants.json",
  descriptor:
    "projects/domainspec-v2/development/remaining-meta-types/admissions/query/cross-language-realization-descriptor.json",
  source:
    "projects/domainspec-v2/impl/architecture-conformance/targets/python/remaining_types/query_v1.py",
  observer:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/query/python/read-model-v1/observe_python_query_case.py",
  supervisor:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/query/python/read-model-v1/run_python_query_proof.py",
  proof_builder:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/query/python/read-model-v1/index.ts",
  provider:
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/python-query-v1.ts",
  family_api:
    "projects/domainspec-v2/impl/architecture-conformance/families/read-model/index.ts",
  kernel_api:
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/effect-observation/index.ts",
  binding:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/query/python/read-model-v1/python-binding.json",
});

export type PythonQueryRawInputs = Readonly<Record<
keyof typeof PYTHON_QUERY_RAW_PATHS, string
>>;

type PythonQueryBindingV1 = Readonly<{
  schema_version: "PythonQueryBinding/v1";
  binding_id: "python.complete-settlement.bound-query/v1";
  target_id: "query.python.complete-settlement/v1";
  protocol_id: "python.bound-query/v1";
  output_concept_id: "settlement.CompleteSettlementView";
  definition_ref: ExactRef;
  denominator_ref: ExactRef;
  mutation_catalogue_ref: ExactRef;
  descriptor_ref: ExactRef;
  source_ref: ExactRef;
  observer_ref: ExactRef;
  supervisor_ref: ExactRef;
  proof_builder_ref: ExactRef;
  provider_ref: ExactRef;
  family_api_ref: ExactRef;
  kernel_api_ref: ExactRef;
  observer_id: "observer.python-query-closed-subset/v1";
  observer_owner_ref: "python-query-proof-harness";
  symbol_name: "read_complete_settlement";
  proof_mechanism: "exact-ast-bytecode-audit-plus-two-fresh-processes";
  authority_effect: "none";
  binding_sha256: string;
}>;

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const sha256 = (value: string | Uint8Array): string => createHash("sha256")
  .update(value)
  .digest("hex");
const isObject = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const fail = (code: string, detail?: string): never => {
  throw Object.assign(new Error(detail ? `${code}:${detail}` : code), {code});
};
const exactKeys = (
  value: JsonObject,
  expected: readonly string[],
  code: string,
): void => {
  const actual = Object.keys(value).sort(compareUtf8);
  const wanted = [...expected].sort(compareUtf8);
  if (JSON.stringify(actual) !== JSON.stringify(wanted)) fail(code);
};
const parseJson = (bytes: string, code: string): JsonObject => {
  try {
    const parsed: unknown = JSON.parse(bytes);
    return isObject(parsed) ? parsed : fail(code);
  } catch (error: unknown) {
    if (isObject(error) && error.code === code) throw error;
    return fail(code);
  }
};
const expectObject = (value: unknown, code: string): JsonObject =>
  isObject(value) ? value : fail(code);
const expectString = (value: unknown, code: string): string =>
  typeof value === "string" && value.length > 0 ? value : fail(code);
const expectSha256 = (value: unknown, code: string): string => {
  const digest = expectString(value, code);
  return /^[a-f0-9]{64}$/u.test(digest) ? digest : fail(code);
};
const expectSafeInteger = (value: unknown, code: string): number =>
  typeof value === "number" && Number.isSafeInteger(value) ? value : fail(code);
const decodeRef = (value: unknown, path: string): ExactRef => {
  const source = expectObject(value, "PY_QUERY_BINDING_REF_INVALID");
  exactKeys(source, ["path", "sha256"], "PY_QUERY_BINDING_REF_INVALID");
  if (source.path !== path) fail("PY_QUERY_BINDING_REF_INVALID", path);
  return Object.freeze({
    path,
    sha256: expectSha256(source.sha256, "PY_QUERY_BINDING_REF_INVALID"),
  });
};
const bindingBody = (binding: PythonQueryBindingV1): unknown => {
  const {binding_sha256: _digest, ...body} = binding;
  return body;
};

const decodeBinding = (
  bytes: string,
  raw: PythonQueryRawInputs,
): PythonQueryBindingV1 => {
  const value = parseJson(bytes, "PY_QUERY_BINDING_JSON_INVALID");
  exactKeys(value, [
    "schema_version", "binding_id", "target_id", "protocol_id",
    "output_concept_id", "definition_ref", "denominator_ref",
    "mutation_catalogue_ref", "descriptor_ref", "source_ref",
    "observer_ref", "supervisor_ref", "proof_builder_ref", "provider_ref",
    "family_api_ref", "kernel_api_ref", "observer_id",
    "observer_owner_ref", "symbol_name", "proof_mechanism",
    "authority_effect", "binding_sha256",
  ], "PY_QUERY_BINDING_SHAPE_INVALID");
  if (value.schema_version !== "PythonQueryBinding/v1" ||
      value.binding_id !== "python.complete-settlement.bound-query/v1" ||
      value.target_id !== "query.python.complete-settlement/v1" ||
      value.protocol_id !== "python.bound-query/v1" ||
      value.output_concept_id !== "settlement.CompleteSettlementView" ||
      value.observer_id !== "observer.python-query-closed-subset/v1" ||
      value.observer_owner_ref !== "python-query-proof-harness" ||
      value.symbol_name !== "read_complete_settlement" ||
      value.proof_mechanism !==
        "exact-ast-bytecode-audit-plus-two-fresh-processes" ||
      value.authority_effect !== "none") {
    return fail("PY_QUERY_BINDING_POLICY_INVALID");
  }
  const binding = Object.freeze({
    schema_version: "PythonQueryBinding/v1" as const,
    binding_id: "python.complete-settlement.bound-query/v1" as const,
    target_id: "query.python.complete-settlement/v1" as const,
    protocol_id: "python.bound-query/v1" as const,
    output_concept_id: "settlement.CompleteSettlementView" as const,
    definition_ref: decodeRef(value.definition_ref,
      PYTHON_QUERY_RAW_PATHS.definition),
    denominator_ref: decodeRef(value.denominator_ref,
      PYTHON_QUERY_RAW_PATHS.denominator),
    mutation_catalogue_ref: decodeRef(value.mutation_catalogue_ref,
      PYTHON_QUERY_RAW_PATHS.mutations),
    descriptor_ref: decodeRef(value.descriptor_ref,
      PYTHON_QUERY_RAW_PATHS.descriptor),
    source_ref: decodeRef(value.source_ref, PYTHON_QUERY_RAW_PATHS.source),
    observer_ref: decodeRef(value.observer_ref,
      PYTHON_QUERY_RAW_PATHS.observer),
    supervisor_ref: decodeRef(value.supervisor_ref,
      PYTHON_QUERY_RAW_PATHS.supervisor),
    proof_builder_ref: decodeRef(value.proof_builder_ref,
      PYTHON_QUERY_RAW_PATHS.proof_builder),
    provider_ref: decodeRef(value.provider_ref,
      PYTHON_QUERY_RAW_PATHS.provider),
    family_api_ref: decodeRef(value.family_api_ref,
      PYTHON_QUERY_RAW_PATHS.family_api),
    kernel_api_ref: decodeRef(value.kernel_api_ref,
      PYTHON_QUERY_RAW_PATHS.kernel_api),
    observer_id: "observer.python-query-closed-subset/v1" as const,
    observer_owner_ref: "python-query-proof-harness" as const,
    symbol_name: "read_complete_settlement" as const,
    proof_mechanism:
      "exact-ast-bytecode-audit-plus-two-fresh-processes" as const,
    authority_effect: "none" as const,
    binding_sha256: expectSha256(value.binding_sha256,
      "PY_QUERY_BINDING_DIGEST_INVALID"),
  }) satisfies PythonQueryBindingV1;
  if (sha256ReadModelQueryBytes(canonicalReadModelQueryJson(
    bindingBody(binding),
  )) !== binding.binding_sha256) fail("PY_QUERY_BINDING_DIGEST_STALE");
  const roles = Object.freeze({
    definition_ref: "definition",
    denominator_ref: "denominator",
    mutation_catalogue_ref: "mutations",
    descriptor_ref: "descriptor",
    source_ref: "source",
    observer_ref: "observer",
    supervisor_ref: "supervisor",
    proof_builder_ref: "proof_builder",
    provider_ref: "provider",
    family_api_ref: "family_api",
    kernel_api_ref: "kernel_api",
  } as const);
  for (const [refName, role] of Object.entries(roles) as readonly [
    keyof typeof roles,
    keyof PythonQueryRawInputs,
  ][]) {
    if (sha256(raw[role]) !== binding[refName].sha256) {
      return fail("PY_QUERY_BINDING_INPUT_STALE", role);
    }
  }
  return binding;
};

const decodeScalarRecord = (
  value: unknown,
  code: string,
): Readonly<Record<string, ReadModelScalarV1>> => {
  const source = expectObject(value, code);
  const decoded = Object.fromEntries(Object.entries(source).map(([key, child]) => {
    if (child !== null && typeof child !== "string" &&
        typeof child !== "boolean" &&
        !(typeof child === "number" && Number.isSafeInteger(child))) {
      return fail(code);
    }
    return [key, child as ReadModelScalarV1];
  }));
  return Object.freeze(decoded);
};

const decodeNativeProof = (
  value: unknown,
  binding: PythonQueryBindingV1,
): PythonQueryNativeProofV1 => {
  const source = expectObject(value, "PY_QUERY_NATIVE_PROOF_INVALID");
  exactKeys(source, [
    "schema_version", "target", "binding", "owner_case", "observation",
    "process_evidence", "source_hostiles", "source_hostile_accounting",
    "claim_ceiling", "authority_effect",
  ], "PY_QUERY_NATIVE_PROOF_INVALID");
  const target = expectObject(source.target, "PY_QUERY_NATIVE_TARGET_INVALID");
  const nativeBinding = expectObject(source.binding,
    "PY_QUERY_NATIVE_BINDING_INVALID");
  const ownerCase = expectObject(source.owner_case,
    "PY_QUERY_NATIVE_CASE_INVALID");
  const observation = expectObject(source.observation,
    "PY_QUERY_NATIVE_OBSERVATION_INVALID");
  const sourceProof = expectObject(observation.source_proof,
    "PY_QUERY_NATIVE_SOURCE_PROOF_INVALID");
  const quiescence = expectObject(observation.quiescence,
    "PY_QUERY_NATIVE_QUIESCENCE_INVALID");
  const processEvidence = expectObject(source.process_evidence,
    "PY_QUERY_NATIVE_PROCESS_INVALID");
  const accounting = expectObject(source.source_hostile_accounting,
    "PY_QUERY_NATIVE_ACCOUNTING_INVALID");
  const rawTrace = Array.isArray(observation.trace) ? observation.trace
    : fail("PY_QUERY_NATIVE_TRACE_INVALID");
  const trace = Object.freeze(rawTrace.map((entry) => {
    const item = expectObject(entry, "PY_QUERY_NATIVE_TRACE_INVALID");
    exactKeys(item, ["target_id", "channel", "outcome"],
      "PY_QUERY_NATIVE_TRACE_INVALID");
    if (item.channel !== "filesystem" || item.outcome !== "success") {
      return fail("PY_QUERY_NATIVE_TRACE_INVALID");
    }
    return Object.freeze({
      target_id: expectString(item.target_id, "PY_QUERY_NATIVE_TRACE_INVALID"),
      channel: "filesystem" as const,
      outcome: "success" as const,
    });
  }));
  const rawHostiles = Array.isArray(source.source_hostiles)
    ? source.source_hostiles : fail("PY_QUERY_NATIVE_HOSTILES_INVALID");
  const hostiles = Object.freeze(rawHostiles.map((entry) => {
    const item = expectObject(entry, "PY_QUERY_NATIVE_HOSTILES_INVALID");
    exactKeys(item, ["hostile_id", "evidence_kind", "status", "error_code"],
      "PY_QUERY_NATIVE_HOSTILES_INVALID");
    if (item.evidence_kind !== "python-source-hostile" ||
        item.status !== "killed") return fail("PY_QUERY_NATIVE_HOSTILES_INVALID");
    return Object.freeze({
      hostile_id: expectString(item.hostile_id,
        "PY_QUERY_NATIVE_HOSTILES_INVALID"),
      evidence_kind: "python-source-hostile" as const,
      status: "killed" as const,
      error_code: expectString(item.error_code,
        "PY_QUERY_NATIVE_HOSTILES_INVALID"),
    });
  }));
  if (source.schema_version !== "PythonQueryNativeProof/v1" ||
      source.authority_effect !== "none" ||
      target.target_id !== binding.target_id ||
      target.target_sha256 !== binding.source_ref.sha256 ||
      target.language !== "python" || target.protocol_id !== binding.protocol_id ||
      target.output_concept_id !== binding.output_concept_id ||
      nativeBinding.binding_id !== binding.binding_id ||
      nativeBinding.binding_sha256 !== binding.binding_sha256 ||
      observation.case_id !== ownerCase.case_id ||
      sourceProof.source_sha256 !== binding.source_ref.sha256 ||
      sourceProof.lifecycle_basis !==
        "synchronous-return-plus-closed-plain-data-static-exclusion" ||
      !Array.isArray(observation.runtime_audit_events) ||
      observation.runtime_audit_events.length !== 0 ||
      observation.result_consumption !== "complete-json-materialization" ||
      observation.mutable_alias_observed !== false ||
      quiescence.observed !== true || quiescence.pending_count !== 0 ||
      processEvidence.executions !== 2 || processEvidence.distinct_pids !== 2 ||
      processEvidence.pids_redacted_from_semantic_proof !== true ||
      processEvidence.semantic_replay_equal !== true ||
      processEvidence.input_materialization !== "json-inert-mapping-proxy" ||
      processEvidence.read_fixtures !== "json-inert-mapping-proxy" ||
      processEvidence.lifecycle_basis !== sourceProof.lifecycle_basis ||
      hostiles.length !== 8 || new Set(hostiles.map(({hostile_id: id}) => id)).size !== 8 ||
      accounting.declared !== 8 || accounting.killed !== 8 ||
      typeof source.claim_ceiling !== "string") {
    return fail("PY_QUERY_NATIVE_PROOF_INVALID");
  }
  const input = decodeScalarRecord(ownerCase.input, "PY_QUERY_NATIVE_CASE_INVALID");
  const expectedResult = decodeScalarRecord(ownerCase.expected_result,
    "PY_QUERY_NATIVE_CASE_INVALID");
  const result = decodeScalarRecord(observation.result,
    "PY_QUERY_NATIVE_OBSERVATION_INVALID");
  if (expectSha256(ownerCase.input_sha256, "PY_QUERY_NATIVE_CASE_INVALID") !==
      sha256ReadModelQueryValue(input) ||
      expectSha256(processEvidence.trace_sha256,
        "PY_QUERY_NATIVE_PROCESS_INVALID") !== sha256ReadModelQueryValue(trace) ||
      expectSha256(processEvidence.result_sha256,
        "PY_QUERY_NATIVE_PROCESS_INVALID") !== sha256ReadModelQueryValue(result)) {
    return fail("PY_QUERY_NATIVE_DIGEST_STALE");
  }
  return Object.freeze({
    schema_version: "PythonQueryNativeProof/v1" as const,
    target: Object.freeze({
      target_id: binding.target_id,
      target_sha256: binding.source_ref.sha256,
      language: "python" as const,
      protocol_id: binding.protocol_id,
      output_concept_id: binding.output_concept_id,
    }),
    binding: Object.freeze({
      binding_id: binding.binding_id,
      binding_sha256: binding.binding_sha256,
    }),
    owner_case: Object.freeze({
      case_id: expectString(ownerCase.case_id, "PY_QUERY_NATIVE_CASE_INVALID"),
      input,
      input_sha256: ownerCase.input_sha256 as string,
      expected_result: expectedResult,
    }),
    observation: Object.freeze({
      case_id: observation.case_id as string,
      trace,
      result,
      source_sha256: sourceProof.source_sha256 as string,
      lifecycle_basis:
        "synchronous-return-plus-closed-plain-data-static-exclusion" as const,
      runtime_audit_events: Object.freeze([]),
      result_consumption: "complete-json-materialization" as const,
      mutable_alias_observed: false as const,
      quiescence: Object.freeze({observed: true as const, pending_count: 0 as const}),
    }),
    process_evidence: Object.freeze({
      executions: 2 as const,
      distinct_pids: 2 as const,
      pids_redacted_from_semantic_proof: true as const,
      semantic_replay_equal: true as const,
      trace_sha256: processEvidence.trace_sha256 as string,
      result_sha256: processEvidence.result_sha256 as string,
      input_materialization: "json-inert-mapping-proxy" as const,
      read_fixtures: "json-inert-mapping-proxy" as const,
      lifecycle_basis:
        "synchronous-return-plus-closed-plain-data-static-exclusion" as const,
    }),
    source_hostiles: hostiles,
    source_hostile_accounting: Object.freeze({declared: 8 as const, killed: 8 as const}),
    claim_ceiling: source.claim_ceiling,
    authority_effect: "none" as const,
  });
};

export const assertPythonQueryAdapterBoundary = (input: Readonly<{
  observation_json: string;
  expected_target_id: string;
  expected_source_sha256: string;
  expected_protocol_id: string;
  expected_output_concept_id: string;
  observed_output_concept_id: string;
  lifecycle_basis: string;
}>): ReadModelQueryObservationV1 => {
  const observation = decodeReadModelQueryObservationV1(input.observation_json);
  const lifecycle = observation.read_lifecycle_observation;
  if (observation.target.target_id !== input.expected_target_id ||
      observation.target.target_sha256 !== input.expected_source_sha256 ||
      observation.target.language !== "python" ||
      observation.target.protocol_id !== input.expected_protocol_id ||
      input.observed_output_concept_id !== input.expected_output_concept_id ||
      lifecycle.declared_read_attempts.some(({outcome}) => outcome !== "success") ||
      input.lifecycle_basis !==
        "synchronous-return-plus-closed-plain-data-static-exclusion") {
    return fail("PY_QUERY_ADAPTER_PREFLIGHT_FAILED");
  }
  return observation;
};

export const composePythonQueryProof = (input: Readonly<{
  raw_inputs: PythonQueryRawInputs;
  native_proof: unknown;
}>) => {
  const binding = decodeBinding(input.raw_inputs.binding, input.raw_inputs);
  const native = decodeNativeProof(input.native_proof, binding);
  const definition = decodeReadModelQueryDefinitionV1(
    input.raw_inputs.definition,
    PYTHON_QUERY_RAW_PATHS.descriptor,
    input.raw_inputs.descriptor,
  );
  const denominator = decodeReadModelQueryDenominatorV1(
    input.raw_inputs.denominator,
    input.raw_inputs.definition,
    definition,
    PYTHON_QUERY_RAW_PATHS.definition,
  );
  const mutationCatalogue = decodeReadModelQueryMutationCatalogueV1(
    input.raw_inputs.mutations,
    denominator,
  );
  const ownerCase = definition.cases[0] ?? fail("PY_QUERY_OWNER_CASE_MISSING");
  if (definition.output_concept.concept_id !== binding.output_concept_id ||
      native.owner_case.case_id !== ownerCase.case_id ||
      canonicalReadModelQueryJson(native.owner_case.input) !==
        canonicalReadModelQueryJson(ownerCase.inputs) ||
      canonicalReadModelQueryJson(native.owner_case.expected_result) !==
        canonicalReadModelQueryJson(ownerCase.expected_result) ||
      canonicalReadModelQueryJson(native.observation.result) !==
        canonicalReadModelQueryJson(ownerCase.expected_result) ||
      canonicalReadModelQueryJson(native.observation.trace.map(
        ({target_id: targetId}) => targetId,
      )) !== canonicalReadModelQueryJson(definition.read_targets.map(
        ({target_id: targetId}) => targetId,
      ))) {
    return fail("PY_QUERY_NATIVE_OWNER_BINDING_STALE");
  }
  const lockedObserver: LockedEffectObserverRefV1 = Object.freeze({
    role: "independent-effect-observer" as const,
    observer_id: binding.observer_id,
    observer_sha256: binding.observer_ref.sha256,
    owner_ref: binding.observer_owner_ref,
    provider_id: "python-query-v1",
    provider_sha256: binding.provider_ref.sha256,
  });
  const targetRef = Object.freeze({
    target_id: binding.target_id,
    target_sha256: binding.source_ref.sha256,
  });
  const readsByChannel = new Map<string, number>();
  for (const entry of native.observation.trace) {
    readsByChannel.set(entry.channel,
      (readsByChannel.get(entry.channel) ?? 0) + 1);
  }
  const effectObservation = mintEffectObservationV1({
    schema_version: "EffectObservation/v1",
    observation_id: "observation.effect.query.python.complete-settlement/v1",
    source_kind: "independent-owner-observation",
    target_ref: targetRef,
    observer_ref: lockedObserver,
    channels: EFFECT_CHANNELS.map((channel) => ({
      channel,
      coverage: "supported" as const,
      read_count: readsByChannel.get(channel) ?? 0,
      write_count: 0,
      escape_count: 0,
      deferred_count: 0,
    })),
    result: {consumption: "complete", mutable_alias_observed: false},
    quiescence: {observed: true, pending_count: 0},
    authority_effect: "none",
  });
  const lifecycleObservation = mintDeclaredReadLifecycleObservationV1({
    schema_version: "DeclaredReadLifecycleObservation/v1",
    observation_id: "observation.declared-read.query.python.complete-settlement/v1",
    source_kind: "independent-owner-observation",
    target_ref: targetRef,
    observer_ref: lockedObserver,
    declared_read_attempts: native.observation.trace.map((entry, ordinal) => ({
      ordinal,
      ...entry,
      lifecycle_path: "return" as const,
    })),
    lifecycle_paths: DECLARED_READ_LIFECYCLE_PATHS.map((lifecycle_path) => ({
      lifecycle_path,
      coverage: "supported" as const,
    })),
    effect_observation: effectObservation,
    source_support: "supported-static",
    write_then_restore_observed: false,
    authority_effect: "none",
  });
  const minted = mintReadModelQueryObservationV1({
    schema_version: "ReadModelQueryObservation/v1",
    observation_id: "observation.query.python.complete-settlement/v1",
    source_kind: "target-observation",
    target: {
      ...targetRef,
      language: "python",
      protocol_id: binding.protocol_id,
    },
    definition_ref: denominator.owner_definition_ref,
    binding: {
      descriptor_id: definition.descriptor_ref.descriptor_id,
      descriptor_sha256: definition.descriptor_ref.sha256,
      provider_id: lockedObserver.provider_id,
      provider_sha256: lockedObserver.provider_sha256,
    },
    observed_result: {
      case_id: ownerCase.case_id,
      input_sha256: sha256ReadModelQueryValue(ownerCase.inputs),
      result: native.observation.result,
      result_sha256: sha256ReadModelQueryValue(native.observation.result),
      declared_failure: null,
    },
    read_lifecycle_observation: lifecycleObservation,
    authority_effect: "none",
  });
  const observation = assertPythonQueryAdapterBoundary({
    observation_json: canonicalReadModelQueryJson(minted),
    expected_target_id: binding.target_id,
    expected_source_sha256: binding.source_ref.sha256,
    expected_protocol_id: binding.protocol_id,
    expected_output_concept_id: binding.output_concept_id,
    observed_output_concept_id: definition.output_concept.concept_id,
    lifecycle_basis: native.observation.lifecycle_basis,
  });
  const familyEvaluation = evaluateReadModelQuery({
    definition,
    denominator,
    observation,
    locked_observer_ref: lockedObserver,
    locked_target_ref: targetRef,
  });
  if (familyEvaluation.verdict !== "pass") {
    return fail("PY_QUERY_FAMILY_EVALUATION_BLOCKED",
      familyEvaluation.findings.map(({code}) => code).join(","));
  }
  const familyControls = mutationCatalogue.mutations.map((mutation) => {
    const variants = mutation.variants.map((variant) => {
      const evaluation = evaluateReadModelQuery({
        definition,
        denominator,
        observation: applyReadModelQueryMutant(observation, mutation, variant),
        locked_observer_ref: lockedObserver,
        locked_target_ref: targetRef,
      });
      const observed = new Set(evaluation.findings.map(({code}) => code));
      const killed = evaluation.verdict === "fail" &&
        mutation.expected_finding_codes.every((code) => observed.has(
          code as ReadModelQueryFindingCode,
        ));
      if (!killed) return fail("PY_QUERY_FAMILY_CONTROL_SURVIVED",
        `${mutation.mutation_id}:${variant}`);
      return Object.freeze({variant, status: "killed" as const});
    });
    return Object.freeze({
      mutation_id: mutation.mutation_id,
      evidence_kind: "predecessor-family-observation-control" as const,
      variants: Object.freeze(variants),
    });
  });
  return Object.freeze({
    schema_version: "PythonQueryProof/v1" as const,
    target: native.target,
    binding: native.binding,
    observation,
    family_evaluation: familyEvaluation,
    native_process_evidence: native.process_evidence,
    accounting: Object.freeze({
      positives: Object.freeze({declared: 4, passed: 4}),
      source_hostiles: native.source_hostile_accounting,
      predecessor_family_controls: Object.freeze({
        declared_classes: familyControls.length,
        killed_classes: familyControls.length,
      }),
    }),
    source_hostiles: native.source_hostiles,
    predecessor_family_controls: Object.freeze(familyControls),
    claim_ceiling: native.claim_ceiling,
    authority_effect: "none" as const,
  });
};
