import {execFile} from "node:child_process";
import {createHash} from "node:crypto";
import {mkdir, writeFile} from "node:fs/promises";
import {resolve} from "node:path";
import {promisify} from "node:util";

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
import {
  inspectRustCalculationClosedSubset,
  rustCalculationHostileSource,
} from "./closed-subset.js";

type JsonObject = Record<string, unknown>;
type ExactRef = Readonly<{path: string; sha256: string}>;

export const RUST_CALCULATION_RAW_PATHS = Object.freeze({
  definition:
    "projects/domainspec-v2/impl/architecture-conformance/families/value-computation/fixtures/net-settlement/definition.json",
  denominator:
    "projects/domainspec-v2/impl/architecture-conformance/families/value-computation/fixtures/net-settlement/denominator.json",
  mutations:
    "projects/domainspec-v2/impl/architecture-conformance/families/value-computation/fixtures/net-settlement/mutants.json",
  descriptor:
    "projects/domainspec-v2/development/remaining-meta-types/admissions/calculation/cross-language-realization-descriptor.json",
  source:
    "projects/domainspec-v2/impl/architecture-conformance/targets/rust/src/remaining_types/calculation_v1.rs",
  observer:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/calculation/rust/value-computation-v1/closed-subset.ts",
  proof_builder:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/calculation/rust/value-computation-v1/index.ts",
  provider:
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/rust-calculation-v1.ts",
  binding:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/calculation/rust/value-computation-v1/rust-binding.json",
});

export type RustCalculationRawInputs = Readonly<Record<
keyof typeof RUST_CALCULATION_RAW_PATHS, string
>>;

type RustCalculationBindingV1 = Readonly<{
  schema_version: "RustCalculationBinding/v1";
  binding_id: "rust.net-settlement.bound-calculation/v1";
  target_id: "calculation.rust.net-settlement/v1";
  protocol_id: "rust.bound-calculation/v1";
  definition_ref: ExactRef;
  denominator_ref: ExactRef;
  mutation_catalogue_ref: ExactRef;
  descriptor_ref: ExactRef;
  source_ref: ExactRef;
  observer_ref: ExactRef;
  proof_builder_ref: ExactRef;
  provider_ref: ExactRef;
  observer_id: "observer.rust-calculation-closed-subset/v1";
  observer_owner_ref: "rust-calculation-proof-harness";
  symbol_name: "NET_SETTLEMENT";
  proof_mechanism: "exact-source-subset-overflow-checked-two-fresh-processes";
  authority_effect: "none";
  binding_sha256: string;
}>;

const executeFile = promisify(execFile);
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
  if (!isObject(value)) return fail("RUST_CALC_BINDING_REF_INVALID", path);
  exactKeys(value, ["path", "sha256"], "RUST_CALC_BINDING_REF_INVALID");
  if (value.path !== path || typeof value.sha256 !== "string"
      || !/^[a-f0-9]{64}$/u.test(value.sha256)) {
    return fail("RUST_CALC_BINDING_REF_INVALID", path);
  }
  return Object.freeze({path, sha256: value.sha256});
};
const bindingBody = (binding: RustCalculationBindingV1): unknown => {
  const {binding_sha256: _digest, ...body} = binding;
  return body;
};
const decodeBinding = (
  bytes: string,
  raw: RustCalculationRawInputs,
): RustCalculationBindingV1 => {
  const value = parseObject(bytes, "RUST_CALC_BINDING_JSON_INVALID");
  exactKeys(value, [
    "schema_version", "binding_id", "target_id", "protocol_id", "definition_ref",
    "denominator_ref", "mutation_catalogue_ref", "descriptor_ref", "source_ref",
    "observer_ref", "proof_builder_ref", "provider_ref", "observer_id",
    "observer_owner_ref", "symbol_name", "proof_mechanism", "authority_effect",
    "binding_sha256",
  ], "RUST_CALC_BINDING_SHAPE_INVALID");
  if (value.schema_version !== "RustCalculationBinding/v1"
      || value.binding_id !== "rust.net-settlement.bound-calculation/v1"
      || value.target_id !== "calculation.rust.net-settlement/v1"
      || value.protocol_id !== "rust.bound-calculation/v1"
      || value.observer_id !== "observer.rust-calculation-closed-subset/v1"
      || value.observer_owner_ref !== "rust-calculation-proof-harness"
      || value.symbol_name !== "NET_SETTLEMENT"
      || value.proof_mechanism
        !== "exact-source-subset-overflow-checked-two-fresh-processes"
      || value.authority_effect !== "none"
      || typeof value.binding_sha256 !== "string") {
    return fail("RUST_CALC_BINDING_POLICY_INVALID");
  }
  const binding = Object.freeze({
    schema_version: "RustCalculationBinding/v1" as const,
    binding_id: "rust.net-settlement.bound-calculation/v1" as const,
    target_id: "calculation.rust.net-settlement/v1" as const,
    protocol_id: "rust.bound-calculation/v1" as const,
    definition_ref: decodeRef(value.definition_ref, RUST_CALCULATION_RAW_PATHS.definition),
    denominator_ref: decodeRef(value.denominator_ref, RUST_CALCULATION_RAW_PATHS.denominator),
    mutation_catalogue_ref: decodeRef(
      value.mutation_catalogue_ref,
      RUST_CALCULATION_RAW_PATHS.mutations,
    ),
    descriptor_ref: decodeRef(value.descriptor_ref, RUST_CALCULATION_RAW_PATHS.descriptor),
    source_ref: decodeRef(value.source_ref, RUST_CALCULATION_RAW_PATHS.source),
    observer_ref: decodeRef(value.observer_ref, RUST_CALCULATION_RAW_PATHS.observer),
    proof_builder_ref: decodeRef(
      value.proof_builder_ref,
      RUST_CALCULATION_RAW_PATHS.proof_builder,
    ),
    provider_ref: decodeRef(value.provider_ref, RUST_CALCULATION_RAW_PATHS.provider),
    observer_id: "observer.rust-calculation-closed-subset/v1" as const,
    observer_owner_ref: "rust-calculation-proof-harness" as const,
    symbol_name: "NET_SETTLEMENT" as const,
    proof_mechanism:
      "exact-source-subset-overflow-checked-two-fresh-processes" as const,
    authority_effect: "none" as const,
    binding_sha256: value.binding_sha256,
  }) satisfies RustCalculationBindingV1;
  if (sha256ValueComputationBytes(canonicalValueComputationJson(bindingBody(binding)))
      !== binding.binding_sha256) fail("RUST_CALC_BINDING_DIGEST_STALE");
  const roles = Object.freeze({
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
    keyof RustCalculationRawInputs,
  ][]) {
    if (sha256(raw[role]) !== binding[refName].sha256) {
      return fail("RUST_CALC_BINDING_INPUT_STALE", role);
    }
  }
  return binding;
};

const runnerSource = (sourcePath: string): string => {
  if (sourcePath.includes('"#')) return fail("RUST_CALC_RUNNER_PATH_INVALID");
  return `#[path = r#"${sourcePath}"#]
mod calculation_v1;

use calculation_v1::{NetSettlementInput, NET_SETTLEMENT};

fn main() {
    let mut arguments = std::env::args().skip(1);
    let gross_amount_minor: i64 = arguments.next().expect("gross").parse().expect("gross-i64");
    let fee_amount_minor: i64 = arguments.next().expect("fee").parse().expect("fee-i64");
    if arguments.next().is_some() {
        std::process::exit(22);
    }
    let input = NetSettlementInput { gross_amount_minor, fee_amount_minor };
    let result = NET_SETTLEMENT(&input);
    println!("{}:{}", std::process::id(), result);
}
`;
};

const parseExecution = (
  stdout: string,
  stderr: string,
): Readonly<{pid: number; result: number}> => {
  if (stderr.length > 0) return fail("RUST_CALC_EXECUTION_STDERR", stderr);
  const match = /^(\d+):(-?\d+)\n?$/u.exec(stdout);
  if (!match) return fail("RUST_CALC_EXECUTION_OUTPUT_INVALID");
  const pid = Number(match[1]);
  const result = Number(match[2]);
  if (!Number.isSafeInteger(pid) || !Number.isSafeInteger(result)) {
    return fail("RUST_CALC_EXECUTION_OUTPUT_INVALID");
  }
  return Object.freeze({pid, result});
};

const runPair = async (
  binary: string,
  gross: number,
  fee: number,
): Promise<readonly [Readonly<{pid: number; result: number}>, Readonly<{
  pid: number;
  result: number;
}>]> => {
  if (!Number.isSafeInteger(gross) || !Number.isSafeInteger(fee)) {
    return fail("RUST_CALC_INPUT_OUTSIDE_SHARED_INTEGER_RANGE");
  }
  const execute = async () => {
    const {stdout, stderr} = await executeFile(binary, [String(gross), String(fee)], {
      env: {},
      timeout: 10_000,
      maxBuffer: 1_048_576,
    }).catch((error: unknown) => fail(
      "RUST_CALC_EXECUTION_FAILED",
      error instanceof Error ? error.message : String(error),
    ));
    return parseExecution(stdout, stderr);
  };
  const [first, second] = await Promise.all([execute(), execute()]);
  if (first.pid === second.pid) return fail("RUST_CALC_PROCESS_ISOLATION_FAILED");
  return Object.freeze([first, second] as const);
};

export const buildRustCalculationProof = async (input: Readonly<{
  raw_inputs: RustCalculationRawInputs;
  workspace: string;
  rustc: string;
}>) => {
  const {raw_inputs: raw} = input;
  const binding = decodeBinding(raw.binding, raw);
  const definition = decodeValueComputationDefinitionV1(
    raw.definition,
    RUST_CALCULATION_RAW_PATHS.descriptor,
    raw.descriptor,
  );
  const denominator = decodeValueComputationDenominatorV1(
    raw.denominator,
    raw.definition,
    definition,
    RUST_CALCULATION_RAW_PATHS.definition,
  );
  const mutationCatalogue = decodeValueComputationMutationCatalogueV1(
    raw.mutations,
    denominator,
  );
  const subset = inspectRustCalculationClosedSubset(raw.source);
  if (subset.source_sha256 !== binding.source_ref.sha256
      || JSON.stringify(subset.supported_effect_channels)
        !== JSON.stringify(EFFECT_CHANNELS)) {
    return fail("RUST_CALC_CLOSED_SUBSET_BINDING_STALE");
  }
  const proofWorkspace = resolve(input.workspace, ".domainspec-rust-calculation-proof");
  const buildDirectory = resolve(proofWorkspace, "build");
  await mkdir(buildDirectory, {recursive: true});
  const sourcePath = resolve(input.workspace, RUST_CALCULATION_RAW_PATHS.source);
  const runnerPath = resolve(proofWorkspace, "runner.rs");
  const binaryPath = resolve(buildDirectory, "calculation-runner");
  await writeFile(runnerPath, runnerSource(sourcePath), {encoding: "utf8", flag: "wx"});
  await executeFile(input.rustc, [
    runnerPath,
    "--edition=2021",
    "-C", "overflow-checks=yes",
    "-C", "debuginfo=0",
    "-o", binaryPath,
  ], {
    cwd: buildDirectory,
    env: {PATH: process.env.PATH ?? ""},
    timeout: 60_000,
    maxBuffer: 1_048_576,
  }).catch((error: unknown) => fail(
    "RUST_CALC_COMPILE_FAILED",
    error instanceof Error ? error.message : String(error),
  ));
  const observedCases = [];
  for (const testCase of definition.cases) {
    const gross = testCase.inputs.gross_amount_minor;
    const fee = testCase.inputs.fee_amount_minor;
    if (typeof gross !== "number" || typeof fee !== "number") {
      return fail("RUST_CALC_INPUT_INVALID", testCase.case_id);
    }
    const [first, second] = await runPair(binaryPath, gross, fee);
    if (first.result !== second.result) {
      return fail("RUST_CALC_NONDETERMINISTIC", testCase.case_id);
    }
    observedCases.push(Object.freeze({
      case_id: testCase.case_id,
      input_sha256: sha256CalculationInputs(testCase.inputs),
      result_kind: "number" as const,
      result_value: first.result,
      result_sha256: sha256CalculationValue(first.result),
      fresh_process_result_sha256: sha256CalculationValue(second.result),
      process_isolation: "separate-process" as const,
    }));
  }
  const nativeHostiles = EFFECT_CHANNELS.map((channel) => {
    const hostile = rustCalculationHostileSource(raw.source, channel);
    try {
      inspectRustCalculationClosedSubset(hostile);
      return fail("RUST_CALC_HOSTILE_SURVIVED", channel);
    } catch (error) {
      if (!isObject(error) || error.code !== "RUST_CALC_CLOSED_SUBSET_SOURCE_MISMATCH") {
        throw error;
      }
    }
    return Object.freeze({
      channel,
      status: "killed" as const,
      error_code: "RUST_CALC_CLOSED_SUBSET_SOURCE_MISMATCH" as const,
    });
  });
  const lockedObserver: LockedEffectObserverRefV1 = Object.freeze({
    role: "independent-effect-observer" as const,
    observer_id: binding.observer_id,
    observer_sha256: binding.observer_ref.sha256,
    owner_ref: binding.observer_owner_ref,
    provider_id: "rust-calculation-v1",
    provider_sha256: binding.provider_ref.sha256,
  });
  const effectObservation = mintEffectObservationV1({
    schema_version: "EffectObservation/v1",
    observation_id: "observation.effect.rust.net-settlement/v1",
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
    observation_id: "observation.calculation.rust.net-settlement/v1",
    source_kind: "target-observation",
    target: {
      target_id: binding.target_id,
      language: "rust",
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
      "RUST_CALC_FAMILY_EVALUATION_BLOCKED",
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
      return fail("RUST_CALC_MUTANT_SURVIVED", mutation.mutation_id);
    }
    return Object.freeze({
      mutation_id: mutation.mutation_id,
      status: "killed" as const,
      finding_codes: Object.freeze(observed as ValueComputationFindingCode[]),
    });
  });
  return Object.freeze({
    schema_version: "RustCalculationComposedProof/v1" as const,
    result: "pass" as const,
    target: Object.freeze({
      target_id: binding.target_id,
      language: "rust" as const,
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
    native_mechanism: Object.freeze({
      closed_subset: subset,
      compiler: Object.freeze({
        edition: "2021" as const,
        overflow_checks: "enabled" as const,
        debuginfo: "disabled" as const,
      }),
      runtime_proof: Object.freeze({
        cases_executed: observedCases.length,
        fresh_processes_executed: observedCases.length * 2,
        distinct_pid_pairs: observedCases.length,
        result_kind: "primitive-i64" as const,
        process_identity_evidence:
          "distinct-pairs-observed-redacted-from-semantic-output" as const,
        quiescence_basis: "closed-subset-plus-successful-child-exit" as const,
      }),
      hostile_probes: Object.freeze(nativeHostiles),
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
        declared: nativeHostiles.length,
        killed: nativeHostiles.length,
      }),
    }),
    claim_ceiling: "one candidate-local Rust descriptor-bound Calculation proven for four owner-authored i64 cases within one exact source-byte subset by overflow-checked compilation, two fresh processes per owner case, complete primitive consumption, and twelve executed static source hostiles; not arbitrary Rust, operating-system interception, overflow behavior outside owner cases, or the full integer domain",
    authority_effect: "none" as const,
  });
};
