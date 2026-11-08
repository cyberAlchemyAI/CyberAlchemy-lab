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
import {inspectTypeScriptCalculationClosedSubset} from "./closed-subset.js";

type JsonObject = Record<string, unknown>;

export const TYPESCRIPT_CALCULATION_RAW_PATHS = Object.freeze({
  definition:
    "projects/domainspec-v2/impl/architecture-conformance/families/value-computation/fixtures/net-settlement/definition.json",
  denominator:
    "projects/domainspec-v2/impl/architecture-conformance/families/value-computation/fixtures/net-settlement/denominator.json",
  mutations:
    "projects/domainspec-v2/impl/architecture-conformance/families/value-computation/fixtures/net-settlement/mutants.json",
  descriptor:
    "projects/domainspec-v2/development/remaining-meta-types/admissions/calculation/cross-language-realization-descriptor.json",
  source:
    "projects/domainspec-v2/impl/architecture-conformance/targets/typescript/calculation-v1.ts",
  observer:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/calculation/typescript/value-computation-v1/closed-subset.ts",
  proof_builder:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/calculation/typescript/value-computation-v1/index.ts",
  provider:
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/typescript-calculation-v1.ts",
  binding:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/calculation/typescript/value-computation-v1/typescript-binding.json",
});

export type TypeScriptCalculationRawInputs = Readonly<Record<
keyof typeof TYPESCRIPT_CALCULATION_RAW_PATHS, string
>>;

type ExactRef = Readonly<{path: string; sha256: string}>;
type TypeScriptCalculationBindingV1 = Readonly<{
  schema_version: "TypeScriptCalculationBinding/v1";
  binding_id: "typescript.net-settlement.bound-calculation/v1";
  target_id: "calculation.typescript.net-settlement/v1";
  protocol_id: "typescript.bound-calculation/v1";
  definition_ref: ExactRef;
  denominator_ref: ExactRef;
  mutation_catalogue_ref: ExactRef;
  descriptor_ref: ExactRef;
  source_ref: ExactRef;
  observer_ref: ExactRef;
  proof_builder_ref: ExactRef;
  provider_ref: ExactRef;
  observer_id: "observer.typescript-calculation-closed-subset/v1";
  observer_owner_ref: "typescript-calculation-proof-harness";
  symbol_name: "calculateNetSettlement";
  proof_mechanism: "closed-expression-static-rejection-plus-two-fresh-processes";
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
const parseJson = (bytes: string, code: string): JsonObject => {
  try {
    const value: unknown = JSON.parse(bytes);
    return isObject(value) ? value : fail(code);
  } catch (error) {
    if (isObject(error) && error.code === code) throw error;
    return fail(code);
  }
};
const decodeRef = (value: unknown, path: string): ExactRef => {
  if (!isObject(value)) return fail("TS_CALC_BINDING_REF_INVALID", path);
  exactKeys(value, ["path", "sha256"], "TS_CALC_BINDING_REF_INVALID");
  if (value.path !== path || typeof value.sha256 !== "string"
      || !/^[a-f0-9]{64}$/u.test(value.sha256)) {
    return fail("TS_CALC_BINDING_REF_INVALID", path);
  }
  return Object.freeze({path, sha256: value.sha256});
};
const bindingBody = (value: TypeScriptCalculationBindingV1): unknown => {
  const {binding_sha256: _digest, ...body} = value;
  return body;
};
const decodeBinding = (
  bytes: string,
  raw: TypeScriptCalculationRawInputs,
): TypeScriptCalculationBindingV1 => {
  const value = parseJson(bytes, "TS_CALC_BINDING_JSON_INVALID");
  exactKeys(value, [
    "schema_version", "binding_id", "target_id", "protocol_id", "definition_ref",
    "denominator_ref", "mutation_catalogue_ref", "descriptor_ref", "source_ref",
    "observer_ref", "proof_builder_ref", "provider_ref", "observer_id", "observer_owner_ref",
    "symbol_name", "proof_mechanism", "authority_effect", "binding_sha256",
  ], "TS_CALC_BINDING_SHAPE_INVALID");
  if (value.schema_version !== "TypeScriptCalculationBinding/v1"
      || value.binding_id !== "typescript.net-settlement.bound-calculation/v1"
      || value.target_id !== "calculation.typescript.net-settlement/v1"
      || value.protocol_id !== "typescript.bound-calculation/v1"
      || value.observer_id !== "observer.typescript-calculation-closed-subset/v1"
      || value.observer_owner_ref !== "typescript-calculation-proof-harness"
      || value.symbol_name !== "calculateNetSettlement"
      || value.proof_mechanism
        !== "closed-expression-static-rejection-plus-two-fresh-processes"
      || value.authority_effect !== "none" || typeof value.binding_sha256 !== "string") {
    return fail("TS_CALC_BINDING_POLICY_INVALID");
  }
  const binding = Object.freeze({
    ...value,
    schema_version: "TypeScriptCalculationBinding/v1" as const,
    binding_id: "typescript.net-settlement.bound-calculation/v1" as const,
    target_id: "calculation.typescript.net-settlement/v1" as const,
    protocol_id: "typescript.bound-calculation/v1" as const,
    definition_ref: decodeRef(value.definition_ref, TYPESCRIPT_CALCULATION_RAW_PATHS.definition),
    denominator_ref: decodeRef(value.denominator_ref, TYPESCRIPT_CALCULATION_RAW_PATHS.denominator),
    mutation_catalogue_ref: decodeRef(value.mutation_catalogue_ref,
      TYPESCRIPT_CALCULATION_RAW_PATHS.mutations),
    descriptor_ref: decodeRef(value.descriptor_ref, TYPESCRIPT_CALCULATION_RAW_PATHS.descriptor),
    source_ref: decodeRef(value.source_ref, TYPESCRIPT_CALCULATION_RAW_PATHS.source),
    observer_ref: decodeRef(value.observer_ref, TYPESCRIPT_CALCULATION_RAW_PATHS.observer),
    proof_builder_ref: decodeRef(
      value.proof_builder_ref,
      TYPESCRIPT_CALCULATION_RAW_PATHS.proof_builder,
    ),
    provider_ref: decodeRef(value.provider_ref, TYPESCRIPT_CALCULATION_RAW_PATHS.provider),
    observer_id: "observer.typescript-calculation-closed-subset/v1" as const,
    observer_owner_ref: "typescript-calculation-proof-harness" as const,
    symbol_name: "calculateNetSettlement" as const,
    proof_mechanism: "closed-expression-static-rejection-plus-two-fresh-processes" as const,
    authority_effect: "none" as const,
    binding_sha256: value.binding_sha256,
  }) as TypeScriptCalculationBindingV1;
  if (sha256ValueComputationBytes(canonicalValueComputationJson(bindingBody(binding)))
      !== binding.binding_sha256) fail("TS_CALC_BINDING_DIGEST_STALE");
  const roleByRef = Object.freeze({
    definition_ref: "definition",
    denominator_ref: "denominator",
    mutation_catalogue_ref: "mutations",
    descriptor_ref: "descriptor",
    source_ref: "source",
    observer_ref: "observer",
    proof_builder_ref: "proof_builder",
    provider_ref: "provider",
  } as const);
  for (const [refName, role] of Object.entries(roleByRef) as readonly [
    keyof typeof roleByRef,
    keyof TypeScriptCalculationRawInputs,
  ][]) {
    if (sha256(raw[role]) !== binding[refName].sha256) {
      return fail("TS_CALC_BINDING_INPUT_STALE", role);
    }
  }
  return binding;
};

const CHILD_SCRIPT = `
const source = Buffer.from(process.env.DS_CALC_SOURCE ?? "", "base64").toString("utf8");
const input = JSON.parse(Buffer.from(process.env.DS_CALC_INPUT ?? "", "base64").toString("utf8"));
const moduleUrl = "data:text/javascript;base64," + Buffer.from(source).toString("base64");
const target = await import(moduleUrl);
const value = target.calculateNetSettlement(input);
if (typeof value !== "number" || !Number.isSafeInteger(value)) process.exit(23);
process.stdout.write(JSON.stringify({pid: process.pid, value}));
`;

const compileTarget = (source: string): string => {
  const result = ts.transpileModule(source, {
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.ES2022,
      strict: true,
      isolatedModules: true,
    },
    fileName: "calculation-v1.ts",
    reportDiagnostics: true,
  });
  if ((result.diagnostics ?? []).some((item) => item.category === ts.DiagnosticCategory.Error)) {
    return fail("TS_CALC_COMPILE_FAILED");
  }
  return result.outputText;
};
const runFreshProcess = async (
  compiledSource: string,
  input: Readonly<Record<string, string | number | null>>,
): Promise<Readonly<{pid: number; value: number}>> => {
  const {stdout, stderr} = await executeFile(process.execPath, [
    "--input-type=module",
    "--eval",
    CHILD_SCRIPT,
  ], {
    env: {
      DS_CALC_SOURCE: Buffer.from(compiledSource, "utf8").toString("base64"),
      DS_CALC_INPUT: Buffer.from(JSON.stringify(input), "utf8").toString("base64"),
    },
    timeout: 10_000,
    maxBuffer: 1_048_576,
  }).catch((error: unknown) => fail(
    "TS_CALC_FRESH_PROCESS_FAILED",
    error instanceof Error ? error.message : String(error),
  ));
  if (stderr.length > 0) fail("TS_CALC_FRESH_PROCESS_STDERR", stderr);
  const value = parseJson(stdout, "TS_CALC_FRESH_PROCESS_OUTPUT_INVALID");
  if (!Number.isSafeInteger(value.pid) || !Number.isSafeInteger(value.value)) {
    return fail("TS_CALC_FRESH_PROCESS_OUTPUT_INVALID");
  }
  return Object.freeze({pid: value.pid as number, value: value.value as number});
};

export const buildTypeScriptCalculationProof = async (
  raw: TypeScriptCalculationRawInputs,
) => {
  const binding = decodeBinding(raw.binding, raw);
  const definition = decodeValueComputationDefinitionV1(
    raw.definition,
    TYPESCRIPT_CALCULATION_RAW_PATHS.descriptor,
    raw.descriptor,
  );
  const denominator = decodeValueComputationDenominatorV1(
    raw.denominator,
    raw.definition,
    definition,
    TYPESCRIPT_CALCULATION_RAW_PATHS.definition,
  );
  const mutationCatalogue = decodeValueComputationMutationCatalogueV1(
    raw.mutations,
    denominator,
  );
  const closedSubset = inspectTypeScriptCalculationClosedSubset(raw.source);
  if (closedSubset.source_sha256 !== binding.source_ref.sha256
      || JSON.stringify(closedSubset.supported_effect_channels)
        !== JSON.stringify(EFFECT_CHANNELS)) {
    return fail("TS_CALC_CLOSED_SUBSET_BINDING_STALE");
  }
  const compiled = compileTarget(raw.source);
  const observedCases = [];
  let distinctPidPairs = 0;
  for (const testCase of definition.cases) {
    const first = await runFreshProcess(compiled, testCase.inputs);
    const second = await runFreshProcess(compiled, testCase.inputs);
    if (first.pid === second.pid) fail("TS_CALC_PROCESS_ISOLATION_FAILED");
    distinctPidPairs += 1;
    observedCases.push(Object.freeze({
      case_id: testCase.case_id,
      input_sha256: sha256CalculationInputs(testCase.inputs),
      result_kind: "number" as const,
      result_value: first.value,
      result_sha256: sha256CalculationValue(first.value),
      fresh_process_result_sha256: sha256CalculationValue(second.value),
      process_isolation: "separate-process" as const,
    }));
  }
  const lockedObserver: LockedEffectObserverRefV1 = Object.freeze({
    role: "independent-effect-observer" as const,
    observer_id: binding.observer_id,
    observer_sha256: binding.observer_ref.sha256,
    owner_ref: binding.observer_owner_ref,
    provider_id: "typescript-calculation-v1",
    provider_sha256: binding.provider_ref.sha256,
  });
  const effectObservation = mintEffectObservationV1({
    schema_version: "EffectObservation/v1",
    observation_id: "observation.effect.typescript.net-settlement/v1",
    source_kind: "independent-owner-observation",
    target_ref: {
      target_id: binding.target_id,
      target_sha256: binding.source_ref.sha256,
    },
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
    observation_id: "observation.calculation.typescript.net-settlement/v1",
    source_kind: "target-observation",
    target: {
      target_id: binding.target_id,
      language: "typescript",
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
    return fail("TS_CALC_FAMILY_EVALUATION_BLOCKED",
      familyEvaluation.findings.map(({code}) => code).join(","));
  }
  const mutationResults = mutationCatalogue.mutations.map((mutation) => {
    const mutated = applyValueComputationMutant(observation, mutation);
    const evaluation = evaluateValueComputation({
      definition,
      denominator,
      observation: mutated,
      locked_observer_ref: lockedObserver,
    });
    const observed = [...new Set(evaluation.findings.map(({code}) => code))]
      .sort(compareUtf8);
    const expected = [...mutation.expected_finding_codes].sort(compareUtf8);
    if (evaluation.verdict !== "fail"
        || JSON.stringify(observed) !== JSON.stringify(expected)) {
      return fail("TS_CALC_MUTANT_SURVIVED", mutation.mutation_id);
    }
    return Object.freeze({
      mutation_id: mutation.mutation_id,
      status: "killed" as const,
      finding_codes: Object.freeze(observed as ValueComputationFindingCode[]),
    });
  });
  return Object.freeze({
    schema_version: "TypeScriptCalculationComposedProof/v1" as const,
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
      result_kind: "primitive-number" as const,
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
    claim_ceiling: "one candidate-local TypeScript descriptor-bound Calculation proven for four owner-authored JSON-materialized inert input objects within an exact closed-expression subset by harness-owned source rejection, two fresh processes per owner case, complete primitive consumption, and twelve declared effect-channel exclusions; not arbitrary callers, getter or Proxy inputs, arbitrary TypeScript, or OS-level interception proof",
    authority_effect: "none" as const,
  });
};
