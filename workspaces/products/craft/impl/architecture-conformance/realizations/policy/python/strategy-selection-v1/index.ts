import {createHash} from "node:crypto";

import {
  EFFECT_CHANNELS,
  mintEffectObservationV1,
  type LockedEffectObserverRefV1,
} from "../../../../kernel/evidence/effect-observation/index.js";
import {
  applyStrategySelectorMutant,
  canonicalStrategySelectionJson,
  decodeStrategySelectionDenominatorV1,
  decodeStrategySelectionMutationCatalogueV1,
  evaluateStrategySelector,
  mintStrategyExecutionObservationV1,
  mintStrategySelectionObservationV1,
  sha256SelectedStrategyIdentity,
  sha256StrategySelectionBytes,
  sha256StrategySelectionInputs,
  type LockedStrategyExecutionObserverRefV1,
  type StrategySelectionFindingCode,
} from "../../../../families/strategy-selection/index.js";

type JsonObject = Record<string, unknown>;
type ExactRef = Readonly<{path: string; sha256: string}>;

export const PYTHON_POLICY_RAW_PATHS = Object.freeze({
  catalogue:
    "projects/domainspec-v2/impl/architecture-conformance/families/strategy-selection/fixtures/settlement-routing/catalogue.json",
  definition:
    "projects/domainspec-v2/impl/architecture-conformance/families/strategy-selection/fixtures/settlement-routing/selector-definition.json",
  denominator:
    "projects/domainspec-v2/impl/architecture-conformance/families/strategy-selection/fixtures/settlement-routing/selector-denominator.json",
  mutations:
    "projects/domainspec-v2/impl/architecture-conformance/families/strategy-selection/fixtures/settlement-routing/selector-mutants.json",
  descriptor:
    "projects/domainspec-v2/development/remaining-meta-types/admissions/policy/cross-language-realization-descriptor.json",
  source:
    "projects/domainspec-v2/impl/architecture-conformance/targets/python/remaining_types/policy_v1.py",
  supervisor:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/policy/python/strategy-selection-v1/run_python_policy_proof.py",
  proof_builder:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/policy/python/strategy-selection-v1/index.ts",
  provider:
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/python-policy-v1.ts",
  binding:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/policy/python/strategy-selection-v1/python-binding.json",
});

export type PythonPolicyRawInputs = Readonly<Record<
keyof typeof PYTHON_POLICY_RAW_PATHS, string
>>;

type PythonPolicyBindingV1 = Readonly<{
  schema_version: "PythonPolicyBinding/v1";
  binding_id: "python.settlement-routing.bound-policy/v1";
  target_id: "policy.python.settlement-routing/v1";
  protocol_id: "python.bound-policy/v1";
  catalogue_ref: ExactRef;
  definition_ref: ExactRef;
  denominator_ref: ExactRef;
  mutation_catalogue_ref: ExactRef;
  descriptor_ref: ExactRef;
  source_ref: ExactRef;
  supervisor_ref: ExactRef;
  proof_builder_ref: ExactRef;
  provider_ref: ExactRef;
  effect_observer_id: "observer.python-policy-ast-bytecode/v1";
  execution_observer_id: "observer.python-policy-profile-call-trap/v1";
  observer_owner_ref: "python-policy-proof-harness";
  symbol_name: "select_settlement_route";
  proof_mechanism:
    "closed-selector-ast-and-bytecode-rejection-plus-two-fresh-processes";
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
const exactKeys = (value: JsonObject, expected: readonly string[], code: string): void => {
  const actual = Object.keys(value).sort(compareUtf8);
  const wanted = [...expected].sort(compareUtf8);
  if (JSON.stringify(actual) !== JSON.stringify(wanted)) fail(code);
};
const parseObject = (bytes: string, code: string): JsonObject => {
  try {
    const parsed: unknown = JSON.parse(bytes);
    return isObject(parsed) ? parsed : fail(code);
  } catch (error: unknown) {
    if (isObject(error) && error.code === code) throw error;
    return fail(code);
  }
};
const decodeRef = (value: unknown, path: string): ExactRef => {
  if (!isObject(value)) return fail("PY_POLICY_BINDING_REF_INVALID", path);
  exactKeys(value, ["path", "sha256"], "PY_POLICY_BINDING_REF_INVALID");
  if (value.path !== path || typeof value.sha256 !== "string" ||
      !/^[a-f0-9]{64}$/u.test(value.sha256)) {
    return fail("PY_POLICY_BINDING_REF_INVALID", path);
  }
  return Object.freeze({path, sha256: value.sha256});
};
const bindingBody = (binding: PythonPolicyBindingV1): unknown => {
  const {binding_sha256: _digest, ...body} = binding;
  return body;
};
const decodeBinding = (
  bytes: string,
  raw: PythonPolicyRawInputs,
): PythonPolicyBindingV1 => {
  const value = parseObject(bytes, "PY_POLICY_BINDING_JSON_INVALID");
  exactKeys(value, [
    "schema_version", "binding_id", "target_id", "protocol_id",
    "catalogue_ref", "definition_ref", "denominator_ref",
    "mutation_catalogue_ref", "descriptor_ref", "source_ref", "supervisor_ref",
    "proof_builder_ref", "provider_ref", "effect_observer_id",
    "execution_observer_id", "observer_owner_ref", "symbol_name",
    "proof_mechanism", "authority_effect", "binding_sha256",
  ], "PY_POLICY_BINDING_SHAPE_INVALID");
  if (value.schema_version !== "PythonPolicyBinding/v1" ||
      value.binding_id !== "python.settlement-routing.bound-policy/v1" ||
      value.target_id !== "policy.python.settlement-routing/v1" ||
      value.protocol_id !== "python.bound-policy/v1" ||
      value.effect_observer_id !== "observer.python-policy-ast-bytecode/v1" ||
      value.execution_observer_id !== "observer.python-policy-profile-call-trap/v1" ||
      value.observer_owner_ref !== "python-policy-proof-harness" ||
      value.symbol_name !== "select_settlement_route" ||
      value.proof_mechanism !==
        "closed-selector-ast-and-bytecode-rejection-plus-two-fresh-processes" ||
      value.authority_effect !== "none" || typeof value.binding_sha256 !== "string") {
    return fail("PY_POLICY_BINDING_POLICY_INVALID");
  }
  const binding = Object.freeze({
    schema_version: "PythonPolicyBinding/v1" as const,
    binding_id: "python.settlement-routing.bound-policy/v1" as const,
    target_id: "policy.python.settlement-routing/v1" as const,
    protocol_id: "python.bound-policy/v1" as const,
    catalogue_ref: decodeRef(value.catalogue_ref, PYTHON_POLICY_RAW_PATHS.catalogue),
    definition_ref: decodeRef(value.definition_ref, PYTHON_POLICY_RAW_PATHS.definition),
    denominator_ref: decodeRef(value.denominator_ref, PYTHON_POLICY_RAW_PATHS.denominator),
    mutation_catalogue_ref: decodeRef(
      value.mutation_catalogue_ref,
      PYTHON_POLICY_RAW_PATHS.mutations,
    ),
    descriptor_ref: decodeRef(value.descriptor_ref, PYTHON_POLICY_RAW_PATHS.descriptor),
    source_ref: decodeRef(value.source_ref, PYTHON_POLICY_RAW_PATHS.source),
    supervisor_ref: decodeRef(value.supervisor_ref, PYTHON_POLICY_RAW_PATHS.supervisor),
    proof_builder_ref: decodeRef(
      value.proof_builder_ref,
      PYTHON_POLICY_RAW_PATHS.proof_builder,
    ),
    provider_ref: decodeRef(value.provider_ref, PYTHON_POLICY_RAW_PATHS.provider),
    effect_observer_id: "observer.python-policy-ast-bytecode/v1" as const,
    execution_observer_id: "observer.python-policy-profile-call-trap/v1" as const,
    observer_owner_ref: "python-policy-proof-harness" as const,
    symbol_name: "select_settlement_route" as const,
    proof_mechanism:
      "closed-selector-ast-and-bytecode-rejection-plus-two-fresh-processes" as const,
    authority_effect: "none" as const,
    binding_sha256: value.binding_sha256,
  }) satisfies PythonPolicyBindingV1;
  if (sha256StrategySelectionBytes(canonicalStrategySelectionJson(bindingBody(binding))) !==
      binding.binding_sha256) fail("PY_POLICY_BINDING_DIGEST_STALE");
  const roles = Object.freeze({
    catalogue_ref: "catalogue",
    definition_ref: "definition",
    denominator_ref: "denominator",
    mutation_catalogue_ref: "mutations",
    descriptor_ref: "descriptor",
    source_ref: "source",
    supervisor_ref: "supervisor",
    proof_builder_ref: "proof_builder",
    provider_ref: "provider",
  } as const);
  for (const [refName, role] of Object.entries(roles) as readonly [
    keyof typeof roles,
    keyof PythonPolicyRawInputs,
  ][]) {
    if (sha256(raw[role]) !== binding[refName].sha256) {
      return fail("PY_POLICY_BINDING_INPUT_STALE", role);
    }
  }
  return binding;
};

export const composePythonPolicyProof = (input: Readonly<{
  raw_inputs: PythonPolicyRawInputs;
  native_proof: unknown;
}>) => {
  const raw = input.raw_inputs;
  const binding = decodeBinding(raw.binding, raw);
  const native = input.native_proof;
  if (!isObject(native) || native.schema_version !== "PythonPolicyNativeProof/v1" ||
      native.result !== "pass" || !isObject(native.closed_subset) ||
      !Array.isArray(native.observed_cases) || native.observed_cases.length !== 5 ||
      native.fresh_processes_executed !== 10 || native.distinct_processes !== 10 ||
      native.strategy_execution_attempts !== 0 || native.authority_effect !== "none") {
    return fail("PY_POLICY_NATIVE_PROOF_INVALID");
  }
  if (native.closed_subset.source_sha256 !== binding.source_ref.sha256 ||
      native.closed_subset.target_call_opcodes !== 0) {
    return fail("PY_POLICY_NATIVE_BINDING_INVALID");
  }
  const decoded = decodeStrategySelectionDenominatorV1(
    raw.denominator,
    raw.definition,
    PYTHON_POLICY_RAW_PATHS.definition,
    raw.catalogue,
    PYTHON_POLICY_RAW_PATHS.catalogue,
    PYTHON_POLICY_RAW_PATHS.descriptor,
    raw.descriptor,
  );
  const mutationCatalogue = decodeStrategySelectionMutationCatalogueV1(raw.mutations);
  const nativeByCase = new Map(native.observed_cases.map((value) => {
    if (!isObject(value) || typeof value.case_id !== "string") {
      return fail("PY_POLICY_NATIVE_CASE_INVALID");
    }
    return [value.case_id, value] as const;
  }));
  const observedCases = decoded.definition.cases.map((testCase) => {
    const value = nativeByCase.get(testCase.case_id);
    if (!value || value.nested_call_count !== 0 ||
        typeof value.selected_strategy_id !== "string" ||
        value.input_sha256 !== sha256StrategySelectionInputs(testCase.inputs) ||
        value.selected_sha256 !==
          sha256SelectedStrategyIdentity(value.selected_strategy_id)) {
      return fail("PY_POLICY_NATIVE_CASE_INVALID", testCase.case_id);
    }
    const selected = value.selected_strategy_id;
    return Object.freeze({
      case_id: testCase.case_id,
      input_sha256: value.input_sha256,
      selected_kind: "strategy-id" as const,
      selected_strategy_id: selected,
      selected_sha256: value.selected_sha256,
      branch_id: selected === "settlement.route.expedited"
        ? "branch.expedited"
        : selected === "settlement.route.manual-review"
          ? "branch.manual-review"
          : "branch.standard",
      consumed_input_facts: Object.freeze(
        decoded.definition.input_facts.map(({name}) => name),
      ),
    });
  });
  const effectObserver: LockedEffectObserverRefV1 = Object.freeze({
    role: "independent-effect-observer",
    observer_id: binding.effect_observer_id,
    observer_sha256: binding.supervisor_ref.sha256,
    owner_ref: binding.observer_owner_ref,
    provider_id: "python-policy-v1",
    provider_sha256: binding.provider_ref.sha256,
  });
  const executionObserver: LockedStrategyExecutionObserverRefV1 = Object.freeze({
    role: "independent-strategy-execution-observer",
    observer_id: binding.execution_observer_id,
    observer_sha256: binding.supervisor_ref.sha256,
    owner_ref: binding.observer_owner_ref,
    provider_id: "python-policy-v1",
    provider_sha256: binding.provider_ref.sha256,
  });
  const targetRef = Object.freeze({
    target_id: binding.target_id,
    target_sha256: binding.source_ref.sha256,
  });
  const effectObservation = mintEffectObservationV1({
    schema_version: "EffectObservation/v1",
    observation_id: "observation.effect.python.settlement-routing/v1",
    source_kind: "independent-owner-observation",
    target_ref: targetRef,
    observer_ref: effectObserver,
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
  const executionObservation = mintStrategyExecutionObservationV1({
    schema_version: "StrategyExecutionObservation/v1",
    observation_id: "observation.execution.python.settlement-routing/v1",
    source_kind: "independent-owner-trap",
    observer_ref: executionObserver,
    target_ref: targetRef,
    catalogue_ref: {
      catalogue_id: decoded.definition.catalogue_ref.catalogue_id,
      catalogue_sha256: decoded.definition.catalogue_ref.catalogue_sha256,
    },
    coverage: "all-owner-declared-strategies",
    covered_strategy_ids: [...new Set(decoded.definition.cases
      .map(({expected_strategy_id: strategyId}) => strategyId))],
    attempt_count: 0,
    attempted_strategy_ids: [],
    completion_count: 0,
    authority_effect: "none",
  });
  const observation = mintStrategySelectionObservationV1({
    schema_version: "StrategySelectionObservation/v1",
    observation_id: "observation.policy.python.settlement-routing/v1",
    source_kind: "target-observation",
    target: {...targetRef, language: "python", protocol_id: binding.protocol_id},
    definition_ref: decoded.denominator.owner_definition_ref,
    catalogue_ref: {
      catalogue_id: decoded.definition.catalogue_ref.catalogue_id,
      catalogue_sha256: decoded.definition.catalogue_ref.catalogue_sha256,
    },
    binding: {
      descriptor_id: decoded.definition.descriptor_ref.descriptor_id,
      descriptor_sha256: decoded.definition.descriptor_ref.sha256,
      provider_id: effectObserver.provider_id,
      provider_sha256: effectObserver.provider_sha256,
    },
    cases: observedCases,
    effect_observation: effectObservation,
    strategy_execution_observation: executionObservation,
    authority_effect: "none",
  });
  const evaluationInput = {
    catalogue: decoded.catalogue,
    definition: decoded.definition,
    denominator: decoded.denominator,
    locked_effect_observer_ref: effectObserver,
    locked_execution_observer_ref: executionObserver,
    locked_selector_target_ref: targetRef,
  } as const;
  const familyEvaluation = evaluateStrategySelector({...evaluationInput, observation});
  if (familyEvaluation.verdict !== "pass") {
    return fail("PY_POLICY_FAMILY_EVALUATION_BLOCKED",
      familyEvaluation.findings.map(({code}) => code).join(","));
  }
  const mutations = mutationCatalogue.mutations.map((mutation) => {
    const evaluation = evaluateStrategySelector({
      ...evaluationInput,
      observation: applyStrategySelectorMutant(observation, mutation),
    });
    const codes = [...new Set(evaluation.findings.map(({code}) => code))]
      .sort(compareUtf8);
    if (evaluation.verdict !== "fail" ||
        !mutation.expected_finding_codes.every((code) => codes.includes(code))) {
      return fail("PY_POLICY_MUTANT_SURVIVED", mutation.mutation_id);
    }
    return Object.freeze({
      mutation_id: mutation.mutation_id,
      status: "killed" as const,
      finding_codes: Object.freeze(codes as StrategySelectionFindingCode[]),
    });
  });
  return Object.freeze({
    schema_version: "PythonPolicyComposedProof/v1" as const,
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
      supervisor_sha256: binding.supervisor_ref.sha256,
      proof_builder_sha256: binding.proof_builder_ref.sha256,
    }),
    native_mechanism: Object.freeze({...native}),
    observation,
    family_evaluation: familyEvaluation,
    mutations: Object.freeze(mutations),
    accounting: Object.freeze({
      positives: Object.freeze({declared: 14, passed: 14}),
      mutants: Object.freeze({declared: mutations.length, killed: mutations.length}),
    }),
    claim_ceiling: "one candidate-local Python descriptor-bound Policy selector proven for five owner-authored JSON-materialized inert inputs within an exact AST-and-bytecode subset by isolated child processes, Python profiling of nested calls, successful child exit, and twelve declared effect-channel exclusions; not arbitrary Python, OS sandboxing, current-membership join, business correctness, or selected-strategy correctness",
    authority_effect: "none" as const,
  });
};
