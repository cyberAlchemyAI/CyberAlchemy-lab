import {execFile} from "node:child_process";
import {createHash} from "node:crypto";
import {mkdir, writeFile} from "node:fs/promises";
import {resolve} from "node:path";
import {promisify} from "node:util";

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
} from "../../../../families/read-model/index.js";
import {
  inspectRustQueryClosedSubset,
  RUST_QUERY_HOSTILE_IDS,
  rustQueryHostileSource,
} from "./closed-subset.js";

type JsonObject = Record<string, unknown>;
type ExactRef = Readonly<{path: string; sha256: string}>;
type TraceEntry = Readonly<{
  target_id: string;
  channel: "filesystem";
  outcome: "success";
}>;
type NativeTraceEntry = Readonly<TraceEntry & {
  settlement_id: string;
}>;
type RustExecution = Readonly<{
  pid: number;
  trace: readonly NativeTraceEntry[];
  result: Readonly<{
    settlement_id: string;
    settlement_status: string;
    gross_amount_minor: number;
    payout_id: string;
    payout_status: string;
  }>;
}>;

export const RUST_QUERY_RAW_PATHS = Object.freeze({
  definition:
    "projects/domainspec-v2/impl/architecture-conformance/families/read-model/fixtures/complete-settlement/definition.json",
  denominator:
    "projects/domainspec-v2/impl/architecture-conformance/families/read-model/fixtures/complete-settlement/denominator.json",
  mutations:
    "projects/domainspec-v2/impl/architecture-conformance/families/read-model/fixtures/complete-settlement/mutants.json",
  descriptor:
    "projects/domainspec-v2/development/remaining-meta-types/admissions/query/cross-language-realization-descriptor.json",
  source:
    "projects/domainspec-v2/impl/architecture-conformance/targets/rust/src/remaining_types/query_v1.rs",
  observer:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/query/rust/read-model-v1/closed-subset.ts",
  proof_builder:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/query/rust/read-model-v1/index.ts",
  provider:
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/rust-query-v1.ts",
  family_api:
    "projects/domainspec-v2/impl/architecture-conformance/families/read-model/index.ts",
  kernel_api:
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/effect-observation/index.ts",
  binding:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/query/rust/read-model-v1/rust-binding.json",
});

export type RustQueryRawInputs = Readonly<Record<
keyof typeof RUST_QUERY_RAW_PATHS, string
>>;

type RustQueryBindingV1 = Readonly<{
  schema_version: "RustQueryBinding/v1";
  binding_id: "rust.complete-settlement.bound-query/v1";
  target_id: "query.rust.complete-settlement/v1";
  protocol_id: "rust.bound-query/v1";
  output_concept_id: "settlement.CompleteSettlementView";
  definition_ref: ExactRef;
  denominator_ref: ExactRef;
  mutation_catalogue_ref: ExactRef;
  descriptor_ref: ExactRef;
  source_ref: ExactRef;
  observer_ref: ExactRef;
  proof_builder_ref: ExactRef;
  provider_ref: ExactRef;
  family_api_ref: ExactRef;
  kernel_api_ref: ExactRef;
  observer_id: "observer.rust-query-closed-subset/v1";
  observer_owner_ref: "rust-query-proof-harness";
  symbol_name: "COMPLETE_SETTLEMENT_QUERY";
  proof_mechanism: "exact-source-compiled-runner-two-fresh-processes";
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
const parseObject = (bytes: string, code: string): JsonObject => {
  try {
    const value: unknown = JSON.parse(bytes);
    return isObject(value) ? value : fail(code);
  } catch (error: unknown) {
    if (isObject(error) && error.code === code) throw error;
    return fail(code);
  }
};
const decodeRef = (value: unknown, path: string): ExactRef => {
  if (!isObject(value)) return fail("RUST_QUERY_BINDING_REF_INVALID", path);
  exactKeys(value, ["path", "sha256"], "RUST_QUERY_BINDING_REF_INVALID");
  if (value.path !== path || typeof value.sha256 !== "string" ||
      !/^[a-f0-9]{64}$/u.test(value.sha256)) {
    return fail("RUST_QUERY_BINDING_REF_INVALID", path);
  }
  return Object.freeze({path, sha256: value.sha256});
};
const bindingBody = (binding: RustQueryBindingV1): unknown => {
  const {binding_sha256: _digest, ...body} = binding;
  return body;
};

const decodeBinding = (
  bytes: string,
  raw: RustQueryRawInputs,
): RustQueryBindingV1 => {
  const value = parseObject(bytes, "RUST_QUERY_BINDING_JSON_INVALID");
  exactKeys(value, [
    "schema_version", "binding_id", "target_id", "protocol_id",
    "output_concept_id", "definition_ref", "denominator_ref",
    "mutation_catalogue_ref", "descriptor_ref", "source_ref",
    "observer_ref", "proof_builder_ref", "provider_ref", "family_api_ref",
    "kernel_api_ref", "observer_id", "observer_owner_ref", "symbol_name",
    "proof_mechanism", "authority_effect", "binding_sha256",
  ], "RUST_QUERY_BINDING_SHAPE_INVALID");
  if (value.schema_version !== "RustQueryBinding/v1" ||
      value.binding_id !== "rust.complete-settlement.bound-query/v1" ||
      value.target_id !== "query.rust.complete-settlement/v1" ||
      value.protocol_id !== "rust.bound-query/v1" ||
      value.output_concept_id !== "settlement.CompleteSettlementView" ||
      value.observer_id !== "observer.rust-query-closed-subset/v1" ||
      value.observer_owner_ref !== "rust-query-proof-harness" ||
      value.symbol_name !== "COMPLETE_SETTLEMENT_QUERY" ||
      value.proof_mechanism !==
        "exact-source-compiled-runner-two-fresh-processes" ||
      value.authority_effect !== "none" ||
      typeof value.binding_sha256 !== "string") {
    return fail("RUST_QUERY_BINDING_POLICY_INVALID");
  }
  const binding = Object.freeze({
    schema_version: "RustQueryBinding/v1" as const,
    binding_id: "rust.complete-settlement.bound-query/v1" as const,
    target_id: "query.rust.complete-settlement/v1" as const,
    protocol_id: "rust.bound-query/v1" as const,
    output_concept_id: "settlement.CompleteSettlementView" as const,
    definition_ref: decodeRef(value.definition_ref,
      RUST_QUERY_RAW_PATHS.definition),
    denominator_ref: decodeRef(value.denominator_ref,
      RUST_QUERY_RAW_PATHS.denominator),
    mutation_catalogue_ref: decodeRef(value.mutation_catalogue_ref,
      RUST_QUERY_RAW_PATHS.mutations),
    descriptor_ref: decodeRef(value.descriptor_ref,
      RUST_QUERY_RAW_PATHS.descriptor),
    source_ref: decodeRef(value.source_ref, RUST_QUERY_RAW_PATHS.source),
    observer_ref: decodeRef(value.observer_ref, RUST_QUERY_RAW_PATHS.observer),
    proof_builder_ref: decodeRef(value.proof_builder_ref,
      RUST_QUERY_RAW_PATHS.proof_builder),
    provider_ref: decodeRef(value.provider_ref, RUST_QUERY_RAW_PATHS.provider),
    family_api_ref: decodeRef(value.family_api_ref,
      RUST_QUERY_RAW_PATHS.family_api),
    kernel_api_ref: decodeRef(value.kernel_api_ref,
      RUST_QUERY_RAW_PATHS.kernel_api),
    observer_id: "observer.rust-query-closed-subset/v1" as const,
    observer_owner_ref: "rust-query-proof-harness" as const,
    symbol_name: "COMPLETE_SETTLEMENT_QUERY" as const,
    proof_mechanism:
      "exact-source-compiled-runner-two-fresh-processes" as const,
    authority_effect: "none" as const,
    binding_sha256: value.binding_sha256,
  }) satisfies RustQueryBindingV1;
  if (sha256ReadModelQueryBytes(canonicalReadModelQueryJson(
    bindingBody(binding),
  )) !== binding.binding_sha256) fail("RUST_QUERY_BINDING_DIGEST_STALE");
  const roles = Object.freeze({
    definition_ref: "definition",
    denominator_ref: "denominator",
    mutation_catalogue_ref: "mutations",
    descriptor_ref: "descriptor",
    source_ref: "source",
    observer_ref: "observer",
    proof_builder_ref: "proof_builder",
    provider_ref: "provider",
    family_api_ref: "family_api",
    kernel_api_ref: "kernel_api",
  } as const);
  for (const [refName, role] of Object.entries(roles) as readonly [
    keyof typeof roles,
    keyof RustQueryRawInputs,
  ][]) {
    if (sha256(raw[role]) !== binding[refName].sha256) {
      return fail("RUST_QUERY_BINDING_INPUT_STALE", role);
    }
  }
  return binding;
};

const runnerSource = (sourcePath: string): string => {
  if (sourcePath.includes('"#')) return fail("RUST_QUERY_RUNNER_PATH_INVALID");
  return `#[path = r#"${sourcePath}"#]
mod query_v1;

use query_v1::{
    CompleteSettlementInput, CompleteSettlementReadPort,
    CompleteSettlementView, PayoutRecord, SettlementRecord,
    COMPLETE_SETTLEMENT_QUERY,
};

struct OwnerReadFixture {
    trace: Vec<(&'static str, String)>,
    settlement_status: String,
    gross_amount_minor: i64,
    payout_id: String,
    payout_status: String,
}

impl CompleteSettlementReadPort for OwnerReadFixture {
    fn read_settlement_by_id(
        &mut self,
        target_id: &'static str,
        settlement_id: &str,
    ) -> SettlementRecord {
        self.trace.push((target_id, settlement_id.to_owned()));
        SettlementRecord {
            settlement_id: settlement_id.to_owned(),
            settlement_status: self.settlement_status.clone(),
            gross_amount_minor: self.gross_amount_minor,
        }
    }

    fn read_payout_by_settlement(
        &mut self,
        target_id: &'static str,
        settlement_id: &str,
    ) -> PayoutRecord {
        self.trace.push((target_id, settlement_id.to_owned()));
        PayoutRecord {
            payout_id: self.payout_id.clone(),
            payout_status: self.payout_status.clone(),
        }
    }
}

fn main() {
    let arguments: Vec<String> = std::env::args().skip(1).collect();
    if arguments.len() != 5 {
        std::process::exit(21);
    }
    let gross_amount_minor: i64 = arguments[2].parse().expect("gross-i64");
    let mut reads = OwnerReadFixture {
        trace: Vec::new(),
        settlement_status: arguments[1].clone(),
        gross_amount_minor,
        payout_id: arguments[3].clone(),
        payout_status: arguments[4].clone(),
    };
    let result: CompleteSettlementView = COMPLETE_SETTLEMENT_QUERY(
        &CompleteSettlementInput { settlement_id: &arguments[0] },
        &mut reads,
    );
    println!("{}", std::process::id());
    for (target_id, settlement_id) in reads.trace {
        println!("{}\\t{}", target_id, settlement_id);
    }
    println!(
        "{}\\t{}\\t{}\\t{}\\t{}",
        result.settlement_id,
        result.settlement_status,
        result.gross_amount_minor,
        result.payout_id,
        result.payout_status,
    );
}
`;
};

const safeArgument = (value: unknown, code: string): string => {
  if (typeof value !== "string" || value.length === 0 || /[\t\r\n]/u.test(value)) {
    return fail(code);
  }
  return value;
};
const parseExecution = (stdout: string, stderr: string): RustExecution => {
  if (stderr.length > 0) return fail("RUST_QUERY_EXECUTION_STDERR", stderr);
  const lines = stdout.endsWith("\n")
    ? stdout.slice(0, -1).split("\n")
    : stdout.split("\n");
  if (lines.length !== 4) return fail("RUST_QUERY_EXECUTION_OUTPUT_INVALID");
  const pid = Number(lines[0]);
  if (!Number.isSafeInteger(pid) || pid <= 0) {
    return fail("RUST_QUERY_EXECUTION_OUTPUT_INVALID");
  }
  const trace = Object.freeze(lines.slice(1, 3).map((line) => {
    const fields = line.split("\t");
    if (fields.length !== 2) return fail("RUST_QUERY_EXECUTION_OUTPUT_INVALID");
    return Object.freeze({
      target_id: fields[0] ?? fail("RUST_QUERY_EXECUTION_OUTPUT_INVALID"),
      settlement_id: fields[1] ?? fail("RUST_QUERY_EXECUTION_OUTPUT_INVALID"),
    });
  }));
  const fields = lines[3]?.split("\t") ?? [];
  if (fields.length !== 5) return fail("RUST_QUERY_EXECUTION_OUTPUT_INVALID");
  const gross = Number(fields[2]);
  if (!Number.isSafeInteger(gross)) return fail("RUST_QUERY_EXECUTION_OUTPUT_INVALID");
  return Object.freeze({
    pid,
    trace: Object.freeze(trace.map(({target_id: targetId, settlement_id}) => Object.freeze({
      target_id: targetId,
      settlement_id,
      channel: "filesystem" as const,
      outcome: "success" as const,
    }))),
    result: Object.freeze({
      settlement_id: fields[0] ?? fail("RUST_QUERY_EXECUTION_OUTPUT_INVALID"),
      settlement_status: fields[1] ?? fail("RUST_QUERY_EXECUTION_OUTPUT_INVALID"),
      gross_amount_minor: gross,
      payout_id: fields[3] ?? fail("RUST_QUERY_EXECUTION_OUTPUT_INVALID"),
      payout_status: fields[4] ?? fail("RUST_QUERY_EXECUTION_OUTPUT_INVALID"),
    }),
  });
};

const portableTrace = (
  trace: readonly NativeTraceEntry[],
): readonly TraceEntry[] => Object.freeze(trace.map(({target_id}) => Object.freeze({
  target_id,
  channel: "filesystem" as const,
  outcome: "success" as const,
})));

export const assertRustQueryReadKeys = (
  trace: readonly Readonly<{settlement_id: string}>[],
  expectedSettlementId: string,
): void => {
  if (trace.length !== 2 || trace.some(
    ({settlement_id: observedId}) => observedId !== expectedSettlementId,
  )) {
    fail("RUST_QUERY_NATIVE_READ_KEY_INVALID");
  }
};

const runPair = async (
  binary: string,
  args: readonly string[],
): Promise<readonly [RustExecution, RustExecution]> => {
  const execute = async (): Promise<RustExecution> => {
    const {stdout, stderr} = await executeFile(binary, args, {
      env: {},
      timeout: 10_000,
      maxBuffer: 1_048_576,
    }).catch((error: unknown) => fail(
      "RUST_QUERY_EXECUTION_FAILED",
      error instanceof Error ? error.message : String(error),
    ));
    return parseExecution(stdout, stderr);
  };
  const [first, second] = await Promise.all([execute(), execute()]);
  if (first.pid === second.pid) return fail("RUST_QUERY_PROCESS_ISOLATION_FAILED");
  if (canonicalReadModelQueryJson({trace: first.trace, result: first.result}) !==
      canonicalReadModelQueryJson({trace: second.trace, result: second.result})) {
    return fail("RUST_QUERY_PROCESS_REPLAY_MISMATCH");
  }
  return Object.freeze([first, second] as const);
};

export const assertRustQueryAdapterBoundary = (input: Readonly<{
  observation_json: string;
  expected_target_id: string;
  expected_source_sha256: string;
  expected_protocol_id: string;
  expected_output_concept_id: string;
  observed_output_concept_id: string;
  lifecycle_basis: string;
}>): ReadModelQueryObservationV1 => {
  const observation = decodeReadModelQueryObservationV1(input.observation_json);
  if (observation.target.target_id !== input.expected_target_id ||
      observation.target.target_sha256 !== input.expected_source_sha256 ||
      observation.target.language !== "rust" ||
      observation.target.protocol_id !== input.expected_protocol_id ||
      input.observed_output_concept_id !== input.expected_output_concept_id ||
      observation.read_lifecycle_observation.declared_read_attempts.some(
        ({outcome}) => outcome !== "success",
      ) || input.lifecycle_basis !==
        "synchronous-return-plus-owned-plain-data-static-exclusion") {
    return fail("RUST_QUERY_ADAPTER_PREFLIGHT_FAILED");
  }
  return observation;
};

export const buildRustQueryProof = async (input: Readonly<{
  raw_inputs: RustQueryRawInputs;
  workspace: string;
  rustc: string;
}>) => {
  const raw = input.raw_inputs;
  const binding = decodeBinding(raw.binding, raw);
  const definition = decodeReadModelQueryDefinitionV1(
    raw.definition,
    RUST_QUERY_RAW_PATHS.descriptor,
    raw.descriptor,
  );
  const denominator = decodeReadModelQueryDenominatorV1(
    raw.denominator,
    raw.definition,
    definition,
    RUST_QUERY_RAW_PATHS.definition,
  );
  const mutationCatalogue = decodeReadModelQueryMutationCatalogueV1(
    raw.mutations,
    denominator,
  );
  const subset = inspectRustQueryClosedSubset(raw.source);
  if (subset.source_sha256 !== binding.source_ref.sha256 ||
      canonicalReadModelQueryJson(subset.declared_read_targets) !==
        canonicalReadModelQueryJson(definition.read_targets.map(
          ({target_id: targetId}) => targetId,
        )) || definition.output_concept.concept_id !== binding.output_concept_id) {
    return fail("RUST_QUERY_CLOSED_SUBSET_BINDING_STALE");
  }
  const ownerCase = definition.cases[0] ?? fail("RUST_QUERY_OWNER_CASE_MISSING");
  const settlementId = safeArgument(ownerCase.inputs.settlement_id,
    "RUST_QUERY_OWNER_INPUT_INVALID");
  const settlementStatus = safeArgument(ownerCase.expected_result.settlement_status,
    "RUST_QUERY_OWNER_RESULT_INVALID");
  const gross = ownerCase.expected_result.gross_amount_minor;
  if (typeof gross !== "number" || !Number.isSafeInteger(gross)) {
    return fail("RUST_QUERY_OWNER_RESULT_INVALID");
  }
  const payoutId = safeArgument(ownerCase.expected_result.payout_id,
    "RUST_QUERY_OWNER_RESULT_INVALID");
  const payoutStatus = safeArgument(ownerCase.expected_result.payout_status,
    "RUST_QUERY_OWNER_RESULT_INVALID");
  const proofWorkspace = resolve(input.workspace, ".domainspec-rust-query-proof");
  const buildDirectory = resolve(proofWorkspace, "build");
  await mkdir(buildDirectory, {recursive: true});
  const targetPath = resolve(input.workspace, RUST_QUERY_RAW_PATHS.source);
  const runnerPath = resolve(proofWorkspace, "runner.rs");
  const binaryPath = resolve(buildDirectory, "query-runner");
  await writeFile(runnerPath, runnerSource(targetPath), {
    encoding: "utf8",
    flag: "wx",
  });
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
    "RUST_QUERY_COMPILE_FAILED",
    error instanceof Error ? error.message : String(error),
  ));
  const [first] = await runPair(binaryPath, [
    settlementId,
    settlementStatus,
    String(gross),
    payoutId,
    payoutStatus,
  ]);
  const observedTrace = portableTrace(first.trace);
  assertRustQueryReadKeys(first.trace, settlementId);
  if (canonicalReadModelQueryJson(first.result) !==
      canonicalReadModelQueryJson(ownerCase.expected_result) ||
      canonicalReadModelQueryJson(first.trace.map(({target_id: id}) => id)) !==
        canonicalReadModelQueryJson(subset.declared_read_targets)) {
    return fail("RUST_QUERY_NATIVE_OBSERVATION_INVALID");
  }
  const sourceHostiles = RUST_QUERY_HOSTILE_IDS.map((hostileId) => {
    const hostile = rustQueryHostileSource(raw.source, hostileId);
    try {
      inspectRustQueryClosedSubset(hostile);
      return fail("RUST_QUERY_SOURCE_HOSTILE_SURVIVED", hostileId);
    } catch (error: unknown) {
      if (!isObject(error) ||
          error.code !== "RUST_QUERY_CLOSED_SUBSET_SOURCE_MISMATCH") throw error;
    }
    return Object.freeze({
      hostile_id: hostileId,
      evidence_kind: "rust-source-byte-hostile" as const,
      status: "killed" as const,
      error_code: "RUST_QUERY_CLOSED_SUBSET_SOURCE_MISMATCH" as const,
    });
  });
  const lockedObserver: LockedEffectObserverRefV1 = Object.freeze({
    role: "independent-effect-observer" as const,
    observer_id: binding.observer_id,
    observer_sha256: binding.observer_ref.sha256,
    owner_ref: binding.observer_owner_ref,
    provider_id: "rust-query-v1",
    provider_sha256: binding.provider_ref.sha256,
  });
  const targetRef = Object.freeze({
    target_id: binding.target_id,
    target_sha256: binding.source_ref.sha256,
  });
  const effectObservation = mintEffectObservationV1({
    schema_version: "EffectObservation/v1",
    observation_id: "observation.effect.query.rust.complete-settlement/v1",
    source_kind: "independent-owner-observation",
    target_ref: targetRef,
    observer_ref: lockedObserver,
    channels: EFFECT_CHANNELS.map((channel) => ({
      channel,
      coverage: "supported" as const,
      read_count: channel === "filesystem" ? observedTrace.length : 0,
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
    observation_id: "observation.declared-read.query.rust.complete-settlement/v1",
    source_kind: "independent-owner-observation",
    target_ref: targetRef,
    observer_ref: lockedObserver,
    declared_read_attempts: observedTrace.map((entry, ordinal) => ({
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
    observation_id: "observation.query.rust.complete-settlement/v1",
    source_kind: "target-observation",
    target: {...targetRef, language: "rust", protocol_id: binding.protocol_id},
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
      result: first.result,
      result_sha256: sha256ReadModelQueryValue(first.result),
      declared_failure: null,
    },
    read_lifecycle_observation: lifecycleObservation,
    authority_effect: "none",
  });
  const observation = assertRustQueryAdapterBoundary({
    observation_json: canonicalReadModelQueryJson(minted),
    expected_target_id: binding.target_id,
    expected_source_sha256: binding.source_ref.sha256,
    expected_protocol_id: binding.protocol_id,
    expected_output_concept_id: binding.output_concept_id,
    observed_output_concept_id: definition.output_concept.concept_id,
    lifecycle_basis: subset.lifecycle_basis,
  });
  const familyEvaluation = evaluateReadModelQuery({
    definition,
    denominator,
    observation,
    locked_observer_ref: lockedObserver,
    locked_target_ref: targetRef,
  });
  if (familyEvaluation.verdict !== "pass") {
    return fail("RUST_QUERY_FAMILY_EVALUATION_BLOCKED",
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
      if (!killed) return fail("RUST_QUERY_FAMILY_CONTROL_SURVIVED",
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
    schema_version: "RustQueryProof/v1" as const,
    target: Object.freeze({
      target_id: binding.target_id,
      target_sha256: binding.source_ref.sha256,
      language: "rust" as const,
      protocol_id: binding.protocol_id,
      output_concept_id: binding.output_concept_id,
    }),
    binding: Object.freeze({
      binding_id: binding.binding_id,
      binding_sha256: binding.binding_sha256,
    }),
    observation,
    family_evaluation: familyEvaluation,
    closed_subset: subset,
    process_evidence: Object.freeze({
      executions: 2,
      distinct_pids: 2,
      pids_redacted_from_semantic_proof: true,
      semantic_replay_equal: true,
      trace_sha256: sha256ReadModelQueryValue(observedTrace),
      native_trace_sha256: sha256ReadModelQueryValue(first.trace),
      read_keys_observed: first.trace.length,
      read_keys_matching_owner_input: first.trace.filter(
        ({settlement_id: observedId}) => observedId === settlementId,
      ).length,
      read_keys_validated: first.trace.length,
      result_sha256: sha256ReadModelQueryValue(first.result),
      input_materialization: "owned-rust-values" as const,
      read_fixtures: "owned-rust-values" as const,
      lifecycle_basis: subset.lifecycle_basis,
      quiescence_basis: "exact-source-sync-subset-plus-successful-child-exit" as const,
    }),
    accounting: Object.freeze({
      positives: Object.freeze({declared: 4, passed: 4}),
      source_hostiles: Object.freeze({
        declared: sourceHostiles.length,
        killed: sourceHostiles.length,
      }),
      predecessor_family_controls: Object.freeze({
        declared_classes: familyControls.length,
        killed_classes: familyControls.length,
      }),
    }),
    source_hostiles: Object.freeze(sourceHostiles),
    predecessor_family_controls: Object.freeze(familyControls),
    claim_ceiling:
      "owner-fixture Rust exact-source Query proof over owned inert inputs and fixtures, overflow-checked compilation, two fresh native processes, an actual ordered read-port trace, a closed owned scalar result, and static exclusion of unsupported lifecycle and effect surfaces; no arbitrary Rust or generated source, universal runtime or OS interception, failure-path behavior, business correctness beyond the fixture, parity, registration, promotion, release, deployment, or production claim",
    authority_effect: "none" as const,
  });
};
