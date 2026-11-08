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
import {
  inspectRustPolicyClosedSubset,
  rustPolicyHostileSource,
} from "./closed-subset.js";

type JsonObject = Record<string, unknown>;
type ExactRef = Readonly<{path: string; sha256: string}>;

export const RUST_POLICY_RAW_PATHS = Object.freeze({
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
    "projects/domainspec-v2/impl/architecture-conformance/targets/rust/src/remaining_types/policy_v1.rs",
  observer:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/policy/rust/strategy-selection-v1/closed-subset.ts",
  proof_builder:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/policy/rust/strategy-selection-v1/index.ts",
  provider:
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/rust-policy-v1.ts",
  binding:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/policy/rust/strategy-selection-v1/rust-binding.json",
});

export type RustPolicyRawInputs = Readonly<Record<
keyof typeof RUST_POLICY_RAW_PATHS, string
>>;

type RustPolicyBindingV1 = Readonly<{
  schema_version: "RustPolicyBinding/v1";
  binding_id: "rust.settlement-routing.bound-policy/v1";
  target_id: "policy.rust.settlement-routing/v1";
  protocol_id: "rust.bound-policy/v1";
  catalogue_ref: ExactRef;
  definition_ref: ExactRef;
  denominator_ref: ExactRef;
  mutation_catalogue_ref: ExactRef;
  descriptor_ref: ExactRef;
  source_ref: ExactRef;
  observer_ref: ExactRef;
  proof_builder_ref: ExactRef;
  provider_ref: ExactRef;
  effect_observer_id: "observer.rust-policy-closed-subset/v1";
  execution_observer_id: "observer.rust-policy-strategy-call-proof/v1";
  observer_owner_ref: "rust-policy-proof-harness";
  symbol_name: "SETTLEMENT_ROUTING_POLICY";
  proof_mechanism: "exact-source-subset-two-fresh-processes";
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
  if (!isObject(value)) return fail("RUST_POLICY_BINDING_REF_INVALID", path);
  exactKeys(value, ["path", "sha256"], "RUST_POLICY_BINDING_REF_INVALID");
  if (value.path !== path || typeof value.sha256 !== "string" ||
      !/^[a-f0-9]{64}$/u.test(value.sha256)) {
    return fail("RUST_POLICY_BINDING_REF_INVALID", path);
  }
  return Object.freeze({path, sha256: value.sha256});
};
const bindingBody = (binding: RustPolicyBindingV1): unknown => {
  const {binding_sha256: _digest, ...body} = binding;
  return body;
};
const decodeBinding = (
  bytes: string,
  raw: RustPolicyRawInputs,
): RustPolicyBindingV1 => {
  const value = parseJson(bytes, "RUST_POLICY_BINDING_JSON_INVALID");
  exactKeys(value, [
    "schema_version", "binding_id", "target_id", "protocol_id",
    "catalogue_ref", "definition_ref", "denominator_ref",
    "mutation_catalogue_ref", "descriptor_ref", "source_ref", "observer_ref",
    "proof_builder_ref", "provider_ref", "effect_observer_id",
    "execution_observer_id", "observer_owner_ref", "symbol_name",
    "proof_mechanism", "authority_effect", "binding_sha256",
  ], "RUST_POLICY_BINDING_SHAPE_INVALID");
  if (value.schema_version !== "RustPolicyBinding/v1" ||
      value.binding_id !== "rust.settlement-routing.bound-policy/v1" ||
      value.target_id !== "policy.rust.settlement-routing/v1" ||
      value.protocol_id !== "rust.bound-policy/v1" ||
      value.effect_observer_id !== "observer.rust-policy-closed-subset/v1" ||
      value.execution_observer_id !== "observer.rust-policy-strategy-call-proof/v1" ||
      value.observer_owner_ref !== "rust-policy-proof-harness" ||
      value.symbol_name !== "SETTLEMENT_ROUTING_POLICY" ||
      value.proof_mechanism !== "exact-source-subset-two-fresh-processes" ||
      value.authority_effect !== "none" || typeof value.binding_sha256 !== "string") {
    return fail("RUST_POLICY_BINDING_POLICY_INVALID");
  }
  const binding = Object.freeze({
    schema_version: "RustPolicyBinding/v1" as const,
    binding_id: "rust.settlement-routing.bound-policy/v1" as const,
    target_id: "policy.rust.settlement-routing/v1" as const,
    protocol_id: "rust.bound-policy/v1" as const,
    catalogue_ref: decodeRef(value.catalogue_ref, RUST_POLICY_RAW_PATHS.catalogue),
    definition_ref: decodeRef(value.definition_ref, RUST_POLICY_RAW_PATHS.definition),
    denominator_ref: decodeRef(value.denominator_ref, RUST_POLICY_RAW_PATHS.denominator),
    mutation_catalogue_ref: decodeRef(
      value.mutation_catalogue_ref,
      RUST_POLICY_RAW_PATHS.mutations,
    ),
    descriptor_ref: decodeRef(value.descriptor_ref, RUST_POLICY_RAW_PATHS.descriptor),
    source_ref: decodeRef(value.source_ref, RUST_POLICY_RAW_PATHS.source),
    observer_ref: decodeRef(value.observer_ref, RUST_POLICY_RAW_PATHS.observer),
    proof_builder_ref: decodeRef(
      value.proof_builder_ref,
      RUST_POLICY_RAW_PATHS.proof_builder,
    ),
    provider_ref: decodeRef(value.provider_ref, RUST_POLICY_RAW_PATHS.provider),
    effect_observer_id: "observer.rust-policy-closed-subset/v1" as const,
    execution_observer_id: "observer.rust-policy-strategy-call-proof/v1" as const,
    observer_owner_ref: "rust-policy-proof-harness" as const,
    symbol_name: "SETTLEMENT_ROUTING_POLICY" as const,
    proof_mechanism: "exact-source-subset-two-fresh-processes" as const,
    authority_effect: "none" as const,
    binding_sha256: value.binding_sha256,
  }) satisfies RustPolicyBindingV1;
  if (sha256StrategySelectionBytes(canonicalStrategySelectionJson(bindingBody(binding))) !==
      binding.binding_sha256) fail("RUST_POLICY_BINDING_DIGEST_STALE");
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
    keyof RustPolicyRawInputs,
  ][]) {
    if (sha256(raw[role]) !== binding[refName].sha256) {
      return fail("RUST_POLICY_BINDING_INPUT_STALE", role);
    }
  }
  return binding;
};

const runnerSource = (sourcePath: string): string => {
  if (sourcePath.includes('"#')) return fail("RUST_POLICY_RUNNER_PATH_INVALID");
  return `#[path = r#"${sourcePath}"#]
mod policy_v1;

use policy_v1::{SettlementRoutingInput, SETTLEMENT_ROUTING_POLICY};

fn main() {
    let mut arguments = std::env::args().skip(1);
    let amount_minor: i64 = arguments.next().expect("amount").parse().expect("amount-i64");
    let expedite_limit_minor: i64 = arguments.next().expect("limit").parse().expect("limit-i64");
    let expedite_requested: bool = arguments.next().expect("expedite").parse().expect("expedite-bool");
    let manual_review_required: bool = arguments.next().expect("manual").parse().expect("manual-bool");
    if arguments.next().is_some() {
        std::process::exit(22);
    }
    let input = SettlementRoutingInput {
        amount_minor,
        expedite_limit_minor,
        expedite_requested,
        manual_review_required,
    };
    let selected = SETTLEMENT_ROUTING_POLICY(&input);
    println!("{}:{}", std::process::id(), selected.as_wire());
}
`;
};

const parseExecution = (
  stdout: string,
  stderr: string,
): Readonly<{pid: number; selected: string}> => {
  if (stderr.length > 0) return fail("RUST_POLICY_EXECUTION_STDERR", stderr);
  const match = /^(\d+):(settlement\.route\.[a-z-]+)\n?$/u.exec(stdout);
  if (!match) return fail("RUST_POLICY_EXECUTION_OUTPUT_INVALID");
  const pid = Number(match[1]);
  if (!Number.isSafeInteger(pid)) return fail("RUST_POLICY_EXECUTION_OUTPUT_INVALID");
  return Object.freeze({pid, selected: match[2]});
};

const runPair = async (
  binary: string,
  inputs: Readonly<Record<string, string | number | boolean | null>>,
): Promise<readonly [Readonly<{pid: number; selected: string}>, Readonly<{
  pid: number;
  selected: string;
}>]> => {
  const amount = inputs.amount_minor;
  const limit = inputs.expedite_limit_minor;
  const expedite = inputs.expedite_requested;
  const manual = inputs.manual_review_required;
  if (!Number.isSafeInteger(amount) || !Number.isSafeInteger(limit) ||
      typeof expedite !== "boolean" || typeof manual !== "boolean") {
    return fail("RUST_POLICY_INPUT_INVALID");
  }
  const execute = async () => {
    const {stdout, stderr} = await executeFile(binary, [
      String(amount), String(limit), String(expedite), String(manual),
    ], {
      env: {},
      timeout: 10_000,
      maxBuffer: 1_048_576,
    }).catch((error: unknown) => fail(
      "RUST_POLICY_EXECUTION_FAILED",
      error instanceof Error ? error.message : String(error),
    ));
    return parseExecution(stdout, stderr);
  };
  const [first, second] = await Promise.all([execute(), execute()]);
  if (first.pid === second.pid) return fail("RUST_POLICY_PROCESS_ISOLATION_FAILED");
  return Object.freeze([first, second] as const);
};

export const buildRustPolicyProof = async (input: Readonly<{
  raw_inputs: RustPolicyRawInputs;
  workspace: string;
  rustc: string;
}>) => {
  const raw = input.raw_inputs;
  const binding = decodeBinding(raw.binding, raw);
  const decoded = decodeStrategySelectionDenominatorV1(
    raw.denominator,
    raw.definition,
    RUST_POLICY_RAW_PATHS.definition,
    raw.catalogue,
    RUST_POLICY_RAW_PATHS.catalogue,
    RUST_POLICY_RAW_PATHS.descriptor,
    raw.descriptor,
  );
  const mutationCatalogue = decodeStrategySelectionMutationCatalogueV1(raw.mutations);
  const closedSubset = inspectRustPolicyClosedSubset(raw.source);
  if (closedSubset.source_sha256 !== binding.source_ref.sha256 ||
      JSON.stringify(closedSubset.supported_effect_channels) !==
        JSON.stringify(EFFECT_CHANNELS)) {
    return fail("RUST_POLICY_CLOSED_SUBSET_BINDING_STALE");
  }
  const proofWorkspace = resolve(input.workspace, ".domainspec-rust-policy-proof");
  const buildDirectory = resolve(proofWorkspace, "build");
  await mkdir(buildDirectory, {recursive: true});
  const sourcePath = resolve(input.workspace, RUST_POLICY_RAW_PATHS.source);
  const runnerPath = resolve(proofWorkspace, "runner.rs");
  const binaryPath = resolve(buildDirectory, "policy-runner");
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
    "RUST_POLICY_COMPILE_FAILED",
    error instanceof Error ? error.message : String(error),
  ));
  const observedCases = [];
  let distinctPidPairs = 0;
  for (const testCase of decoded.definition.cases) {
    const [first, second] = await runPair(binaryPath, testCase.inputs);
    if (first.selected !== second.selected) return fail("RUST_POLICY_NONDETERMINISTIC");
    distinctPidPairs += 1;
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
  const nativeHostiles = EFFECT_CHANNELS.map((channel) => {
    const hostile = rustPolicyHostileSource(raw.source, channel);
    try {
      inspectRustPolicyClosedSubset(hostile);
      return fail("RUST_POLICY_HOSTILE_SURVIVED", channel);
    } catch (error: unknown) {
      if (!isObject(error) || error.code !== "RUST_POLICY_CLOSED_SUBSET_SOURCE_MISMATCH") {
        throw error;
      }
    }
    return Object.freeze({
      channel,
      status: "killed" as const,
      error_code: "RUST_POLICY_CLOSED_SUBSET_SOURCE_MISMATCH" as const,
    });
  });
  const lockedEffectObserver: LockedEffectObserverRefV1 = Object.freeze({
    role: "independent-effect-observer",
    observer_id: binding.effect_observer_id,
    observer_sha256: binding.observer_ref.sha256,
    owner_ref: binding.observer_owner_ref,
    provider_id: "rust-policy-v1",
    provider_sha256: binding.provider_ref.sha256,
  });
  const lockedExecutionObserver: LockedStrategyExecutionObserverRefV1 = Object.freeze({
    role: "independent-strategy-execution-observer",
    observer_id: binding.execution_observer_id,
    observer_sha256: binding.observer_ref.sha256,
    owner_ref: binding.observer_owner_ref,
    provider_id: "rust-policy-v1",
    provider_sha256: binding.provider_ref.sha256,
  });
  const targetRef = Object.freeze({
    target_id: binding.target_id,
    target_sha256: binding.source_ref.sha256,
  });
  const effectObservation = mintEffectObservationV1({
    schema_version: "EffectObservation/v1",
    observation_id: "observation.effect.rust.settlement-routing/v1",
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
    observation_id: "observation.execution.rust.settlement-routing/v1",
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
    attempt_count: 0,
    attempted_strategy_ids: [],
    completion_count: 0,
    authority_effect: "none",
  });
  const observation = mintStrategySelectionObservationV1({
    schema_version: "StrategySelectionObservation/v1",
    observation_id: "observation.policy.rust.settlement-routing/v1",
    source_kind: "target-observation",
    target: {...targetRef, language: "rust", protocol_id: binding.protocol_id},
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
  const evaluationInput = {
    catalogue: decoded.catalogue,
    definition: decoded.definition,
    denominator: decoded.denominator,
    locked_effect_observer_ref: lockedEffectObserver,
    locked_execution_observer_ref: lockedExecutionObserver,
    locked_selector_target_ref: targetRef,
  } as const;
  const familyEvaluation = evaluateStrategySelector({...evaluationInput, observation});
  if (familyEvaluation.verdict !== "pass") {
    return fail("RUST_POLICY_FAMILY_EVALUATION_BLOCKED",
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
      return fail("RUST_POLICY_MUTANT_SURVIVED", mutation.mutation_id);
    }
    return Object.freeze({
      mutation_id: mutation.mutation_id,
      status: "killed" as const,
      finding_codes: Object.freeze(codes as StrategySelectionFindingCode[]),
    });
  });
  return Object.freeze({
    schema_version: "RustPolicyComposedProof/v1" as const,
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
      closed_subset: closedSubset,
      compiler: Object.freeze({
        edition: "2021" as const,
        overflow_checks: "enabled" as const,
        debuginfo: "disabled" as const,
      }),
      runtime_proof: Object.freeze({
        cases_executed: observedCases.length,
        fresh_processes_executed: observedCases.length * 2,
        distinct_pid_pairs: distinctPidPairs,
        result_kind: "typed-unit-variant-strategy-identity" as const,
        strategy_execution_attempts: 0,
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
    claim_ceiling: "one candidate-local Rust descriptor-bound Policy selector proven for five owner-authored inert inputs within an exact source-byte subset by native compilation, two fresh processes per owner case, typed unit-variant identity results, zero selector call sites, and twelve executed static source hostiles; not arbitrary Rust, operating-system interception, current-membership join, business correctness, selected-strategy correctness, promotion, publication, release, deployment, or production readiness",
    authority_effect: "none" as const,
  });
};
