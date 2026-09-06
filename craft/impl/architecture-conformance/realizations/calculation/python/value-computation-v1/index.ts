import {createHash} from "node:crypto";

import {
  EFFECT_CHANNELS,
  mintEffectObservationV1,
  type LockedEffectObserverRefV1,
} from "../../../../kernel/evidence/effect-observation/index.js";
import {
  applyValueComputationMutant,
  canonicalValueComputationJson,
  decodeValueComputationDefinitionV1,
  decodeValueComputationDenominatorV1,
  decodeValueComputationMutationCatalogueV1,
  evaluateValueComputation,
  mintValueComputationObservationV1,
  sha256CalculationInputs,
  sha256CalculationValue,
  sha256ValueComputationBytes,
  type ValueComputationFindingCode,
} from "../../../../families/value-computation/index.js";

type JsonObject = Record<string, unknown>;
type ExactRef = Readonly<{path: string; sha256: string}>;

export const PYTHON_CALCULATION_RAW_PATHS = Object.freeze({
  definition:
    "projects/domainspec-v2/impl/architecture-conformance/families/value-computation/fixtures/net-settlement/definition.json",
  denominator:
    "projects/domainspec-v2/impl/architecture-conformance/families/value-computation/fixtures/net-settlement/denominator.json",
  mutations:
    "projects/domainspec-v2/impl/architecture-conformance/families/value-computation/fixtures/net-settlement/mutants.json",
  descriptor:
    "projects/domainspec-v2/development/remaining-meta-types/admissions/calculation/cross-language-realization-descriptor.json",
  source:
    "projects/domainspec-v2/impl/architecture-conformance/targets/python/remaining_types/calculation_v1.py",
  observer:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/calculation/python/value-computation-v1/observe_python_calculation_case.py",
  supervisor:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/calculation/python/value-computation-v1/run_python_calculation_proof.py",
  proof_builder:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/calculation/python/value-computation-v1/index.ts",
  provider:
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/python-calculation-v1.ts",
  binding:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/calculation/python/value-computation-v1/python-binding.json",
});

export type PythonCalculationRawInputs = Readonly<Record<
keyof typeof PYTHON_CALCULATION_RAW_PATHS, string
>>;

type PythonCalculationBindingV1 = Readonly<{
  schema_version: "PythonCalculationBinding/v1";
  binding_id: "python.net-settlement.bound-calculation/v1";
  target_id: "calculation.python.net-settlement/v1";
  protocol_id: "python.bound-calculation/v1";
  definition_ref: ExactRef;
  denominator_ref: ExactRef;
  mutation_catalogue_ref: ExactRef;
  descriptor_ref: ExactRef;
  source_ref: ExactRef;
  observer_ref: ExactRef;
  supervisor_ref: ExactRef;
  proof_builder_ref: ExactRef;
  provider_ref: ExactRef;
  observer_id: "observer.python-calculation-closed-subset/v1";
  observer_owner_ref: "python-calculation-proof-harness";
  symbol_name: "calculate_net_settlement";
  proof_mechanism: "exact-ast-bytecode-audit-plus-two-fresh-processes";
  authority_effect: "none";
  binding_sha256: string;
}>;

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const isObject = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const sha256 = (value: string | Uint8Array): string => createHash("sha256")
  .update(value)
  .digest("hex");
const fail = (code: string, detail?: string): never => {
  throw Object.assign(new Error(detail === undefined ? code : `${code}:${detail}`), {code});
};
const exactKeys = (
  value: JsonObject,
  expected: readonly string[],
  code: string,
): void => {
  const actual = Object.keys(value).sort(compareUtf8);
  const keys = [...expected].sort(compareUtf8);
  if (JSON.stringify(actual) !== JSON.stringify(keys)) fail(code);
};
const parseObject = (bytes: string, code: string): JsonObject => {
  try {
    const value: unknown = JSON.parse(bytes);
    return isObject(value) ? value : fail(code);
  } catch (error) {
    if (isObject(error) && error.code === code) throw error;
    return fail(code);
  }
};
const decodeRef = (value: unknown, path: string): ExactRef => {
  if (!isObject(value)) return fail("PY_CALC_BINDING_REF_INVALID", path);
  exactKeys(value, ["path", "sha256"], "PY_CALC_BINDING_REF_INVALID");
  if (value.path !== path || typeof value.sha256 !== "string"
      || !/^[a-f0-9]{64}$/u.test(value.sha256)) {
    return fail("PY_CALC_BINDING_REF_INVALID", path);
  }
  return Object.freeze({path, sha256: value.sha256});
};
const bindingBody = (binding: PythonCalculationBindingV1): unknown => {
  const {binding_sha256: _digest, ...body} = binding;
  return body;
};
const decodeBinding = (
  bytes: string,
  raw: PythonCalculationRawInputs,
): PythonCalculationBindingV1 => {
  const value = parseObject(bytes, "PY_CALC_BINDING_JSON_INVALID");
  exactKeys(value, [
    "schema_version", "binding_id", "target_id", "protocol_id", "definition_ref",
    "denominator_ref", "mutation_catalogue_ref", "descriptor_ref", "source_ref",
    "observer_ref", "supervisor_ref", "proof_builder_ref", "provider_ref",
    "observer_id", "observer_owner_ref", "symbol_name", "proof_mechanism",
    "authority_effect", "binding_sha256",
  ], "PY_CALC_BINDING_SHAPE_INVALID");
  if (value.schema_version !== "PythonCalculationBinding/v1"
      || value.binding_id !== "python.net-settlement.bound-calculation/v1"
      || value.target_id !== "calculation.python.net-settlement/v1"
      || value.protocol_id !== "python.bound-calculation/v1"
      || value.observer_id !== "observer.python-calculation-closed-subset/v1"
      || value.observer_owner_ref !== "python-calculation-proof-harness"
      || value.symbol_name !== "calculate_net_settlement"
      || value.proof_mechanism !== "exact-ast-bytecode-audit-plus-two-fresh-processes"
      || value.authority_effect !== "none"
      || typeof value.binding_sha256 !== "string") {
    return fail("PY_CALC_BINDING_POLICY_INVALID");
  }
  const binding = Object.freeze({
    schema_version: "PythonCalculationBinding/v1" as const,
    binding_id: "python.net-settlement.bound-calculation/v1" as const,
    target_id: "calculation.python.net-settlement/v1" as const,
    protocol_id: "python.bound-calculation/v1" as const,
    definition_ref: decodeRef(value.definition_ref, PYTHON_CALCULATION_RAW_PATHS.definition),
    denominator_ref: decodeRef(value.denominator_ref, PYTHON_CALCULATION_RAW_PATHS.denominator),
    mutation_catalogue_ref: decodeRef(
      value.mutation_catalogue_ref,
      PYTHON_CALCULATION_RAW_PATHS.mutations,
    ),
    descriptor_ref: decodeRef(value.descriptor_ref, PYTHON_CALCULATION_RAW_PATHS.descriptor),
    source_ref: decodeRef(value.source_ref, PYTHON_CALCULATION_RAW_PATHS.source),
    observer_ref: decodeRef(value.observer_ref, PYTHON_CALCULATION_RAW_PATHS.observer),
    supervisor_ref: decodeRef(value.supervisor_ref, PYTHON_CALCULATION_RAW_PATHS.supervisor),
    proof_builder_ref: decodeRef(
      value.proof_builder_ref,
      PYTHON_CALCULATION_RAW_PATHS.proof_builder,
    ),
    provider_ref: decodeRef(value.provider_ref, PYTHON_CALCULATION_RAW_PATHS.provider),
    observer_id: "observer.python-calculation-closed-subset/v1" as const,
    observer_owner_ref: "python-calculation-proof-harness" as const,
    symbol_name: "calculate_net_settlement" as const,
    proof_mechanism: "exact-ast-bytecode-audit-plus-two-fresh-processes" as const,
    authority_effect: "none" as const,
    binding_sha256: value.binding_sha256,
  }) satisfies PythonCalculationBindingV1;
  if (sha256ValueComputationBytes(canonicalValueComputationJson(bindingBody(binding)))
      !== binding.binding_sha256) fail("PY_CALC_BINDING_DIGEST_STALE");
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
  } as const);
  for (const [refName, role] of Object.entries(roles) as readonly [
    keyof typeof roles,
    keyof PythonCalculationRawInputs,
  ][]) {
    if (sha256(raw[role]) !== binding[refName].sha256) {
      return fail("PY_CALC_BINDING_INPUT_STALE", role);
    }
  }
  return binding;
};

type NativeCaseRecord = Readonly<{
  case_id: string;
  inputs: Readonly<Record<string, string | number | null>>;
  first: JsonObject;
  second: JsonObject;
}>;

const decodeNativeProof = (value: unknown, binding: PythonCalculationBindingV1) => {
  if (!isObject(value)
      || value.schema_version !== "PythonCalculationNativeProof/v1"
      || value.result !== "pass" || value.authority_effect !== "none"
      || !isObject(value.target) || !isObject(value.binding)
      || !isObject(value.closed_subset) || !isObject(value.runtime_proof)
      || !Array.isArray(value.cases) || !Array.isArray(value.hostile_probes)
      || !isObject(value.hostile_accounting)) {
    return fail("PY_CALC_NATIVE_PROOF_INVALID");
  }
  if (value.target.target_id !== binding.target_id
      || value.target.language !== "python"
      || value.target.protocol_id !== binding.protocol_id
      || value.binding.binding_id !== binding.binding_id
      || value.binding.binding_sha256 !== binding.binding_sha256
      || value.binding.descriptor_sha256 !== binding.descriptor_ref.sha256
      || value.binding.provider_sha256 !== binding.provider_ref.sha256
      || value.binding.observer_sha256 !== binding.observer_ref.sha256
      || value.binding.supervisor_sha256 !== binding.supervisor_ref.sha256
      || value.binding.proof_builder_sha256 !== binding.proof_builder_ref.sha256
      || JSON.stringify(value.closed_subset.supported_effect_channels)
        !== JSON.stringify(EFFECT_CHANNELS)
      || value.runtime_proof.cases_executed !== 4
      || value.runtime_proof.fresh_processes_executed !== 8
      || value.runtime_proof.distinct_pid_pairs !== 4
      || value.runtime_proof.result_kind !== "primitive-number"
      || value.hostile_accounting.declared !== EFFECT_CHANNELS.length
      || value.hostile_accounting.killed !== EFFECT_CHANNELS.length) {
    return fail("PY_CALC_NATIVE_PROOF_BINDING_INVALID");
  }
  const hostiles = value.hostile_probes;
  if (hostiles.length !== EFFECT_CHANNELS.length) {
    return fail("PY_CALC_NATIVE_HOSTILES_INVALID");
  }
  for (const [index, channel] of EFFECT_CHANNELS.entries()) {
    const hostile = hostiles[index];
    if (!isObject(hostile) || hostile.channel !== channel
        || hostile.status !== "killed" || typeof hostile.error_code !== "string"
        || !hostile.error_code.startsWith("PY_CALC_CLOSED_SUBSET_")) {
      return fail("PY_CALC_NATIVE_HOSTILES_INVALID", channel);
    }
  }
  return Object.freeze({
    cases: value.cases as unknown as readonly NativeCaseRecord[],
    closed_subset: Object.freeze({...value.closed_subset}),
    runtime_proof: Object.freeze({...value.runtime_proof}),
    hostile_probes: Object.freeze(hostiles.map((item) => Object.freeze({...item}))),
  });
};

const validateCaseObservation = (
  value: JsonObject,
  caseId: string,
  binding: PythonCalculationBindingV1,
): Readonly<{pid: number; result: number; resultSha256: string; channels: unknown}> => {
  if (value.schema_version !== "PythonCalculationCaseObservation/v1"
      || value.case_id !== caseId || value.source_sha256 !== binding.source_ref.sha256
      || value.result_kind !== "number" || !Number.isSafeInteger(value.result_value)
      || typeof value.result_sha256 !== "string" || !Array.isArray(value.audit_events)
      || value.audit_events.length !== 0 || !Number.isSafeInteger(value.pid)
      || value.result_consumption !== "complete"
      || value.mutable_alias_observed !== false
      || value.quiescence_observed !== true || value.pending_count !== 0
      || value.mechanism !== "exact-ast-bytecode-subset-plus-python-audit-hook"
      || value.authority_effect !== "none" || !Array.isArray(value.effect_channels)
      || sha256CalculationValue(value.result_value) !== value.result_sha256) {
    return fail("PY_CALC_NATIVE_CASE_INVALID", caseId);
  }
  const channels = value.effect_channels;
  if (channels.length !== EFFECT_CHANNELS.length) {
    return fail("PY_CALC_NATIVE_EFFECTS_INVALID", caseId);
  }
  for (const [index, channel] of EFFECT_CHANNELS.entries()) {
    const item = channels[index];
    if (!isObject(item) || item.channel !== channel || item.coverage !== "supported"
        || item.read_count !== 0 || item.write_count !== 0
        || item.escape_count !== 0 || item.deferred_count !== 0) {
      return fail("PY_CALC_NATIVE_EFFECTS_INVALID", `${caseId}:${channel}`);
    }
  }
  return Object.freeze({
    pid: value.pid as number,
    result: value.result_value as number,
    resultSha256: value.result_sha256,
    channels,
  });
};

export const composePythonCalculationProof = (input: Readonly<{
  raw_inputs: PythonCalculationRawInputs;
  native_proof: unknown;
}>) => {
  const {raw_inputs: raw} = input;
  const binding = decodeBinding(raw.binding, raw);
  const definition = decodeValueComputationDefinitionV1(
    raw.definition,
    PYTHON_CALCULATION_RAW_PATHS.descriptor,
    raw.descriptor,
  );
  const denominator = decodeValueComputationDenominatorV1(
    raw.denominator,
    raw.definition,
    definition,
    PYTHON_CALCULATION_RAW_PATHS.definition,
  );
  const mutationCatalogue = decodeValueComputationMutationCatalogueV1(
    raw.mutations,
    denominator,
  );
  const native = decodeNativeProof(input.native_proof, binding);
  if (native.cases.length !== definition.cases.length) {
    return fail("PY_CALC_NATIVE_CASE_SET_INVALID");
  }
  const observedCases = definition.cases.map((testCase, index) => {
    const nativeCase = native.cases[index];
    if (!isObject(nativeCase) || nativeCase.case_id !== testCase.case_id
        || canonicalValueComputationJson(nativeCase.inputs)
          !== canonicalValueComputationJson(testCase.inputs)
        || !isObject(nativeCase.first) || !isObject(nativeCase.second)) {
      return fail("PY_CALC_NATIVE_CASE_SET_INVALID", testCase.case_id);
    }
    const first = validateCaseObservation(nativeCase.first, testCase.case_id, binding);
    const second = validateCaseObservation(nativeCase.second, testCase.case_id, binding);
    if (first.pid === second.pid || first.result !== second.result
        || first.resultSha256 !== second.resultSha256) {
      return fail("PY_CALC_NATIVE_DETERMINISM_INVALID", testCase.case_id);
    }
    return Object.freeze({
      case_id: testCase.case_id,
      input_sha256: sha256CalculationInputs(testCase.inputs),
      result_kind: "number" as const,
      result_value: first.result,
      result_sha256: first.resultSha256,
      fresh_process_result_sha256: second.resultSha256,
      process_isolation: "separate-process" as const,
    });
  });
  const lockedObserver: LockedEffectObserverRefV1 = Object.freeze({
    role: "independent-effect-observer" as const,
    observer_id: binding.observer_id,
    observer_sha256: binding.observer_ref.sha256,
    owner_ref: binding.observer_owner_ref,
    provider_id: "python-calculation-v1",
    provider_sha256: binding.provider_ref.sha256,
  });
  const effectObservation = mintEffectObservationV1({
    schema_version: "EffectObservation/v1",
    observation_id: "observation.effect.python.net-settlement/v1",
    source_kind: "independent-owner-observation",
    target_ref: {target_id: binding.target_id, target_sha256: binding.source_ref.sha256},
    observer_ref: lockedObserver,
    channels: EFFECT_CHANNELS.map((channel) => ({
      channel,
      coverage: "supported" as const,
      read_count: 0,
      write_count: 0,
      escape_count: 0,
      deferred_count: 0,
    })),
    result: {consumption: "complete", mutable_alias_observed: false},
    quiescence: {observed: true, pending_count: 0},
    authority_effect: "none",
  });
  const observation = mintValueComputationObservationV1({
    schema_version: "ValueComputationObservation/v1",
    observation_id: "observation.calculation.python.net-settlement/v1",
    source_kind: "target-observation",
    target: {
      target_id: binding.target_id,
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
    cases: observedCases,
    effect_observation: effectObservation,
    authority_effect: "none",
  });
  const familyEvaluation = evaluateValueComputation({
    definition,
    denominator,
    observation,
    locked_observer_ref: lockedObserver,
  });
  if (familyEvaluation.verdict !== "pass") {
    return fail(
      "PY_CALC_FAMILY_EVALUATION_BLOCKED",
      familyEvaluation.findings.map(({code}) => code).join(","),
    );
  }
  const mutations = mutationCatalogue.mutations.map((mutation) => {
    const evaluation = evaluateValueComputation({
      definition,
      denominator,
      observation: applyValueComputationMutant(observation, mutation),
      locked_observer_ref: lockedObserver,
    });
    const observed = [...new Set(evaluation.findings.map(({code}) => code))]
      .sort(compareUtf8);
    const expected = [...mutation.expected_finding_codes].sort(compareUtf8);
    if (evaluation.verdict !== "fail"
        || JSON.stringify(observed) !== JSON.stringify(expected)) {
      return fail("PY_CALC_MUTANT_SURVIVED", mutation.mutation_id);
    }
    return Object.freeze({
      mutation_id: mutation.mutation_id,
      status: "killed" as const,
      finding_codes: Object.freeze(observed as ValueComputationFindingCode[]),
    });
  });
  return Object.freeze({
    schema_version: "PythonCalculationComposedProof/v1" as const,
    result: "pass" as const,
    target: Object.freeze({
      target_id: binding.target_id,
      language: "python" as const,
      protocol_id: binding.protocol_id,
      source_sha256: binding.source_ref.sha256,
    }),
    binding: Object.freeze({
      binding_id: binding.binding_id,
      binding_sha256: binding.binding_sha256,
      descriptor_sha256: binding.descriptor_ref.sha256,
      provider_sha256: binding.provider_ref.sha256,
      observer_sha256: binding.observer_ref.sha256,
      supervisor_sha256: binding.supervisor_ref.sha256,
      proof_builder_sha256: binding.proof_builder_ref.sha256,
    }),
    native_mechanism: Object.freeze({
      closed_subset: native.closed_subset,
      runtime_proof: native.runtime_proof,
      hostile_probes: native.hostile_probes,
      process_identity_evidence:
        "distinct-pairs-observed-redacted-from-semantic-output" as const,
    }),
    observation,
    family_evaluation: familyEvaluation,
    mutations: Object.freeze(mutations),
    accounting: Object.freeze({
      positives: Object.freeze({
        declared: familyEvaluation.positive_decision_accounting.declared,
        passed: familyEvaluation.positive_decision_accounting.passed,
      }),
      mutants: Object.freeze({declared: mutations.length, killed: mutations.length}),
      native_hostiles: Object.freeze({
        declared: EFFECT_CHANNELS.length,
        killed: EFFECT_CHANNELS.length,
      }),
    }),
    claim_ceiling: "one candidate-local Python descriptor-bound Calculation proven for four owner-authored exact-integer inputs within an exact AST and bytecode subset by process-separated harness execution, Python audit rejection, complete primitive consumption, and twelve executed native channel hostiles; not arbitrary Python, boolean inputs, overloaded arithmetic, or an operating-system sandbox",
    authority_effect: "none" as const,
  });
};
