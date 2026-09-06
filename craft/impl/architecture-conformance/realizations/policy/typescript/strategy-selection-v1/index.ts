import {execFile} from "node:child_process";
import {createHash} from "node:crypto";
import {promisify} from "node:util";
import ts from "typescript";

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
import {inspectTypeScriptPolicyClosedSubset} from "./closed-subset.js";

type JsonObject = Record<string, unknown>;

export const TYPESCRIPT_POLICY_RAW_PATHS = Object.freeze({
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
    "projects/domainspec-v2/impl/architecture-conformance/targets/typescript/policy-v1.ts",
  observer:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/policy/typescript/strategy-selection-v1/closed-subset.ts",
  proof_builder:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/policy/typescript/strategy-selection-v1/index.ts",
  provider:
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/typescript-policy-v1.ts",
  binding:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/policy/typescript/strategy-selection-v1/typescript-binding.json",
});

export type TypeScriptPolicyRawInputs = Readonly<Record<
keyof typeof TYPESCRIPT_POLICY_RAW_PATHS, string
>>;

type ExactRef = Readonly<{path: string; sha256: string}>;
type TypeScriptPolicyBindingV1 = Readonly<{
  schema_version: "TypeScriptPolicyBinding/v1";
  binding_id: "typescript.settlement-routing.bound-policy/v1";
  target_id: "policy.typescript.settlement-routing/v1";
  protocol_id: "typescript.bound-policy/v1";
  catalogue_ref: ExactRef;
  definition_ref: ExactRef;
  denominator_ref: ExactRef;
  mutation_catalogue_ref: ExactRef;
  descriptor_ref: ExactRef;
  source_ref: ExactRef;
  observer_ref: ExactRef;
  proof_builder_ref: ExactRef;
  provider_ref: ExactRef;
  effect_observer_id: "observer.typescript-policy-closed-subset/v1";
  execution_observer_id: "observer.typescript-policy-strategy-call-trap/v1";
  observer_owner_ref: "typescript-policy-proof-harness";
  symbol_name: "selectSettlementRoute";
  proof_mechanism:
    "closed-selector-expression-static-rejection-plus-two-fresh-processes";
  authority_effect: "none";
  binding_sha256: string;
}>;

const executeFile = promisify(execFile);
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
const decodeRef = (value: unknown, path: string): ExactRef => {
  if (!isObject(value)) return fail("TS_POLICY_BINDING_REF_INVALID", path);
  exactKeys(value, ["path", "sha256"], "TS_POLICY_BINDING_REF_INVALID");
  if (value.path !== path || typeof value.sha256 !== "string" ||
      !/^[a-f0-9]{64}$/u.test(value.sha256)) {
    return fail("TS_POLICY_BINDING_REF_INVALID", path);
  }
  return Object.freeze({path, sha256: value.sha256});
};
const bindingBody = (binding: TypeScriptPolicyBindingV1): unknown => {
  const {binding_sha256: _digest, ...body} = binding;
  return body;
};
const decodeBinding = (
  bytes: string,
  raw: TypeScriptPolicyRawInputs,
): TypeScriptPolicyBindingV1 => {
  const value = parseJson(bytes, "TS_POLICY_BINDING_JSON_INVALID");
  exactKeys(value, [
    "schema_version", "binding_id", "target_id", "protocol_id",
    "catalogue_ref", "definition_ref", "denominator_ref",
    "mutation_catalogue_ref", "descriptor_ref", "source_ref", "observer_ref",
    "proof_builder_ref", "provider_ref", "effect_observer_id",
    "execution_observer_id", "observer_owner_ref", "symbol_name",
    "proof_mechanism", "authority_effect", "binding_sha256",
  ], "TS_POLICY_BINDING_SHAPE_INVALID");
  if (value.schema_version !== "TypeScriptPolicyBinding/v1" ||
      value.binding_id !== "typescript.settlement-routing.bound-policy/v1" ||
      value.target_id !== "policy.typescript.settlement-routing/v1" ||
      value.protocol_id !== "typescript.bound-policy/v1" ||
      value.effect_observer_id !== "observer.typescript-policy-closed-subset/v1" ||
      value.execution_observer_id !==
        "observer.typescript-policy-strategy-call-trap/v1" ||
      value.observer_owner_ref !== "typescript-policy-proof-harness" ||
      value.symbol_name !== "selectSettlementRoute" ||
      value.proof_mechanism !==
        "closed-selector-expression-static-rejection-plus-two-fresh-processes" ||
      value.authority_effect !== "none" || typeof value.binding_sha256 !== "string") {
    return fail("TS_POLICY_BINDING_POLICY_INVALID");
  }
  const binding = Object.freeze({
    schema_version: "TypeScriptPolicyBinding/v1" as const,
    binding_id: "typescript.settlement-routing.bound-policy/v1" as const,
    target_id: "policy.typescript.settlement-routing/v1" as const,
    protocol_id: "typescript.bound-policy/v1" as const,
    catalogue_ref: decodeRef(value.catalogue_ref, TYPESCRIPT_POLICY_RAW_PATHS.catalogue),
    definition_ref: decodeRef(value.definition_ref, TYPESCRIPT_POLICY_RAW_PATHS.definition),
    denominator_ref: decodeRef(
      value.denominator_ref,
      TYPESCRIPT_POLICY_RAW_PATHS.denominator,
    ),
    mutation_catalogue_ref: decodeRef(
      value.mutation_catalogue_ref,
      TYPESCRIPT_POLICY_RAW_PATHS.mutations,
    ),
    descriptor_ref: decodeRef(value.descriptor_ref, TYPESCRIPT_POLICY_RAW_PATHS.descriptor),
    source_ref: decodeRef(value.source_ref, TYPESCRIPT_POLICY_RAW_PATHS.source),
    observer_ref: decodeRef(value.observer_ref, TYPESCRIPT_POLICY_RAW_PATHS.observer),
    proof_builder_ref: decodeRef(
      value.proof_builder_ref,
      TYPESCRIPT_POLICY_RAW_PATHS.proof_builder,
    ),
    provider_ref: decodeRef(value.provider_ref, TYPESCRIPT_POLICY_RAW_PATHS.provider),
    effect_observer_id: "observer.typescript-policy-closed-subset/v1" as const,
    execution_observer_id:
      "observer.typescript-policy-strategy-call-trap/v1" as const,
    observer_owner_ref: "typescript-policy-proof-harness" as const,
    symbol_name: "selectSettlementRoute" as const,
    proof_mechanism:
      "closed-selector-expression-static-rejection-plus-two-fresh-processes" as const,
    authority_effect: "none" as const,
    binding_sha256: value.binding_sha256,
  }) satisfies TypeScriptPolicyBindingV1;
  if (sha256StrategySelectionBytes(canonicalStrategySelectionJson(bindingBody(binding))) !==
      binding.binding_sha256) fail("TS_POLICY_BINDING_DIGEST_STALE");
  const roles = Object.freeze({
    catalogue_ref: "catalogue",
    definition_ref: "definition",
    denominator_ref: "denominator",
    mutation_catalogue_ref: "mutations",
    descriptor_ref: "descriptor",
    source_ref: "source",
    observer_ref: "observer",
    proof_builder_ref: "proof_builder",
    provider_ref: "provider",
  } as const);
  for (const [refName, role] of Object.entries(roles) as readonly [
    keyof typeof roles,
    keyof TypeScriptPolicyRawInputs,
  ][]) {
    if (sha256(raw[role]) !== binding[refName].sha256) {
      return fail("TS_POLICY_BINDING_INPUT_STALE", role);
    }
  }
  return binding;
};

const CHILD_SCRIPT = `
const source = Buffer.from(process.env.DS_POLICY_SOURCE ?? "", "base64").toString("utf8");
const input = JSON.parse(Buffer.from(process.env.DS_POLICY_INPUT ?? "", "base64").toString("utf8"));
const moduleUrl = "data:text/javascript;base64," + Buffer.from(source).toString("base64");
const target = await import(moduleUrl);
let callCount = 0;
const strategyTrap = new Proxy(Object.create(null), {get(){callCount += 1; throw new Error("STRATEGY_EXECUTED");}});
const selected = target.selectSettlementRoute(input, strategyTrap);
if (typeof selected !== "string" || !selected.startsWith("settlement.route.")) process.exit(23);
process.stdout.write(JSON.stringify({pid: process.pid, selected, callCount}));
`;

const compileTarget = (source: string): string => {
  const result = ts.transpileModule(source, {
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.ES2022,
      strict: true,
      isolatedModules: true,
    },
    fileName: "policy-v1.ts",
    reportDiagnostics: true,
  });
  if ((result.diagnostics ?? []).some((item) =>
    item.category === ts.DiagnosticCategory.Error)) {
    return fail("TS_POLICY_COMPILE_FAILED");
  }
  return result.outputText;
};
const runFreshProcess = async (
  compiled: string,
  input: Readonly<Record<string, string | number | boolean | null>>,
): Promise<Readonly<{pid: number; selected: string; callCount: number}>> => {
  const {stdout, stderr} = await executeFile(process.execPath, [
    "--input-type=module",
    "--eval",
    CHILD_SCRIPT,
  ], {
    env: {
      DS_POLICY_SOURCE: Buffer.from(compiled, "utf8").toString("base64"),
      DS_POLICY_INPUT: Buffer.from(JSON.stringify(input), "utf8").toString("base64"),
    },
    timeout: 10_000,
    maxBuffer: 1_048_576,
  }).catch((error: unknown) => fail(
    "TS_POLICY_FRESH_PROCESS_FAILED",
    error instanceof Error ? error.message : String(error),
  ));
  if (stderr.length !== 0) fail("TS_POLICY_FRESH_PROCESS_STDERR", stderr);
  const value = parseJson(stdout, "TS_POLICY_FRESH_PROCESS_OUTPUT_INVALID");
  if (!Number.isSafeInteger(value.pid) || typeof value.selected !== "string" ||
      !Number.isSafeInteger(value.callCount)) {
    return fail("TS_POLICY_FRESH_PROCESS_OUTPUT_INVALID");
  }
  return Object.freeze({
    pid: value.pid as number,
    selected: value.selected,
    callCount: value.callCount as number,
  });
};

export const buildTypeScriptPolicyProof = async (
  raw: TypeScriptPolicyRawInputs,
) => {
  const binding = decodeBinding(raw.binding, raw);
  const decoded = decodeStrategySelectionDenominatorV1(
    raw.denominator,
    raw.definition,
    TYPESCRIPT_POLICY_RAW_PATHS.definition,
    raw.catalogue,
    TYPESCRIPT_POLICY_RAW_PATHS.catalogue,
    TYPESCRIPT_POLICY_RAW_PATHS.descriptor,
    raw.descriptor,
  );
  const mutationCatalogue = decodeStrategySelectionMutationCatalogueV1(raw.mutations);
  const closedSubset = inspectTypeScriptPolicyClosedSubset(raw.source);
  if (closedSubset.source_sha256 !== binding.source_ref.sha256 ||
      JSON.stringify(closedSubset.supported_effect_channels) !==
        JSON.stringify(EFFECT_CHANNELS)) {
    return fail("TS_POLICY_CLOSED_SUBSET_BINDING_STALE");
  }
  const compiled = compileTarget(raw.source);
  const observedCases = [];
  const enteredStrategyIds: string[] = [];
  let distinctPidPairs = 0;
  let strategyCallAttempts = 0;
  for (const testCase of decoded.definition.cases) {
    const first = await runFreshProcess(compiled, testCase.inputs);
    const second = await runFreshProcess(compiled, testCase.inputs);
    if (first.pid === second.pid) fail("TS_POLICY_PROCESS_ISOLATION_FAILED");
    distinctPidPairs += 1;
    strategyCallAttempts += first.callCount + second.callCount;
    if (first.callCount !== 0 || second.callCount !== 0) {
      enteredStrategyIds.push(first.selected, second.selected);
    }
    if (first.selected !== second.selected) fail("TS_POLICY_NONDETERMINISTIC");
    observedCases.push(Object.freeze({
      case_id: testCase.case_id,
      input_sha256: sha256StrategySelectionInputs(testCase.inputs),
      selected_kind: "strategy-id" as const,
      selected_strategy_id: first.selected,
      selected_sha256: sha256SelectedStrategyIdentity(first.selected),
      branch_id: first.selected === "settlement.route.expedited"
        ? "branch.expedited"
        : first.selected === "settlement.route.manual-review"
          ? "branch.manual-review"
          : "branch.standard",
      consumed_input_facts: Object.freeze(
        decoded.definition.input_facts.map(({name}) => name),
      ),
    }));
  }
  const lockedEffectObserver: LockedEffectObserverRefV1 = Object.freeze({
    role: "independent-effect-observer",
    observer_id: binding.effect_observer_id,
    observer_sha256: binding.observer_ref.sha256,
    owner_ref: binding.observer_owner_ref,
    provider_id: "typescript-policy-v1",
    provider_sha256: binding.provider_ref.sha256,
  });
  const lockedExecutionObserver: LockedStrategyExecutionObserverRefV1 = Object.freeze({
    role: "independent-strategy-execution-observer",
    observer_id: binding.execution_observer_id,
    observer_sha256: binding.observer_ref.sha256,
    owner_ref: binding.observer_owner_ref,
    provider_id: "typescript-policy-v1",
    provider_sha256: binding.provider_ref.sha256,
  });
  const targetRef = Object.freeze({
    target_id: binding.target_id,
    target_sha256: binding.source_ref.sha256,
  });
  const effectObservation = mintEffectObservationV1({
    schema_version: "EffectObservation/v1",
    observation_id: "observation.effect.typescript.settlement-routing/v1",
    source_kind: "independent-owner-observation",
    target_ref: targetRef,
    observer_ref: lockedEffectObserver,
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
  const strategyExecutionObservation = mintStrategyExecutionObservationV1({
    schema_version: "StrategyExecutionObservation/v1",
    observation_id: "observation.execution.typescript.settlement-routing/v1",
    source_kind: "independent-owner-trap",
    observer_ref: lockedExecutionObserver,
    target_ref: targetRef,
    catalogue_ref: {
      catalogue_id: decoded.definition.catalogue_ref.catalogue_id,
      catalogue_sha256: decoded.definition.catalogue_ref.catalogue_sha256,
    },
    coverage: "all-owner-declared-strategies",
    covered_strategy_ids: [...new Set(decoded.definition.cases
      .map(({expected_strategy_id: strategyId}) => strategyId))],
    attempt_count: strategyCallAttempts,
    attempted_strategy_ids: enteredStrategyIds,
    completion_count: 0,
    authority_effect: "none",
  });
  const observation = mintStrategySelectionObservationV1({
    schema_version: "StrategySelectionObservation/v1",
    observation_id: "observation.policy.typescript.settlement-routing/v1",
    source_kind: "target-observation",
    target: {
      ...targetRef,
      language: "typescript",
      protocol_id: binding.protocol_id,
    },
    definition_ref: decoded.denominator.owner_definition_ref,
    catalogue_ref: {
      catalogue_id: decoded.definition.catalogue_ref.catalogue_id,
      catalogue_sha256: decoded.definition.catalogue_ref.catalogue_sha256,
    },
    binding: {
      descriptor_id: decoded.definition.descriptor_ref.descriptor_id,
      descriptor_sha256: decoded.definition.descriptor_ref.sha256,
      provider_id: lockedEffectObserver.provider_id,
      provider_sha256: lockedEffectObserver.provider_sha256,
    },
    cases: observedCases,
    effect_observation: effectObservation,
    strategy_execution_observation: strategyExecutionObservation,
    authority_effect: "none",
  });
  const familyEvaluation = evaluateStrategySelector({
    catalogue: decoded.catalogue,
    definition: decoded.definition,
    denominator: decoded.denominator,
    observation,
    locked_effect_observer_ref: lockedEffectObserver,
    locked_execution_observer_ref: lockedExecutionObserver,
    locked_selector_target_ref: targetRef,
  });
  if (familyEvaluation.verdict !== "pass") {
    return fail("TS_POLICY_FAMILY_EVALUATION_BLOCKED",
      familyEvaluation.findings.map(({code}) => code).join(","));
  }
  const mutationResults = mutationCatalogue.mutations.map((mutation) => {
    const evaluation = evaluateStrategySelector({
      catalogue: decoded.catalogue,
      definition: decoded.definition,
      denominator: decoded.denominator,
      observation: applyStrategySelectorMutant(observation, mutation),
      locked_effect_observer_ref: lockedEffectObserver,
      locked_execution_observer_ref: lockedExecutionObserver,
      locked_selector_target_ref: targetRef,
    });
    const observed = [...new Set(evaluation.findings.map(({code}) => code))]
      .sort(compareUtf8);
    const expected = [...mutation.expected_finding_codes].sort(compareUtf8);
    if (evaluation.verdict !== "fail" ||
        !expected.every((code) => observed.includes(code))) {
      return fail("TS_POLICY_MUTANT_SURVIVED", mutation.mutation_id);
    }
    return Object.freeze({
      mutation_id: mutation.mutation_id,
      status: "killed" as const,
      finding_codes: Object.freeze(observed as StrategySelectionFindingCode[]),
    });
  });
  return Object.freeze({
    schema_version: "TypeScriptPolicyComposedProof/v1" as const,
    result: "pass" as const,
    target: Object.freeze({
      target_id: binding.target_id,
      language: "typescript" as const,
      protocol_id: binding.protocol_id,
      source_sha256: binding.source_ref.sha256,
    }),
    binding: Object.freeze({
      binding_id: binding.binding_id,
      binding_sha256: binding.binding_sha256,
      descriptor_sha256: binding.descriptor_ref.sha256,
      provider_sha256: binding.provider_ref.sha256,
      observer_sha256: binding.observer_ref.sha256,
      proof_builder_sha256: binding.proof_builder_ref.sha256,
    }),
    closed_subset_proof: closedSubset,
    runtime_proof: Object.freeze({
      cases_executed: observedCases.length,
      fresh_processes_executed: observedCases.length * 2,
      distinct_pid_pairs: distinctPidPairs,
      result_kind: "primitive-strategy-identity" as const,
      strategy_execution_attempts: strategyCallAttempts,
      quiescence_basis: "closed-subset-plus-successful-child-exit" as const,
    }),
    observation,
    family_evaluation: familyEvaluation,
    mutations: Object.freeze(mutationResults),
    accounting: Object.freeze({
      positives: Object.freeze({
        declared: familyEvaluation.positive_decision_accounting.declared,
        passed: familyEvaluation.positive_decision_accounting.passed,
      }),
      mutants: Object.freeze({
        declared: mutationResults.length,
        killed: mutationResults.length,
      }),
    }),
    claim_ceiling: "one candidate-local TypeScript descriptor-bound Policy selector proven for five owner-authored JSON-materialized inert input objects within an exact synchronous closed-expression subset by harness-owned source rejection, two fresh processes per owner case, a zero-call strategy trap, complete primitive identity consumption, and twelve declared effect-channel exclusions; not arbitrary callers, arbitrary TypeScript, OS-level interception, current-membership join, business correctness, or selected-strategy correctness",
    authority_effect: "none" as const,
  });
};
