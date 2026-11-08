import {execFile} from "node:child_process";
import {createHash} from "node:crypto";
import {readFile, writeFile} from "node:fs/promises";
import {resolve} from "node:path";
import {promisify} from "node:util";

import {
  applyIdentityLifecycleMutant,
  decodeIdentityLifecycleDefinitionV1,
  decodeIdentityLifecycleDenominatorV1,
  decodeIdentityLifecycleMutationCatalogueV1,
  evaluateIdentityLifecycle,
  type IdentityLifecycleDefinitionV1,
  type IdentityLifecycleFindingCode,
} from "../../../../families/identity-lifecycle/index.js";
import {
  canonicalConstructionObservationJson,
  mintEntityLifecycleConstructionObservationV1,
  type EntityConstructionRouteTraceV1,
  type EntityConstructionRouteV1,
  type EntityLifecycleSnapshotV1,
  type LockedConstructionObserverRefV1,
} from "../../../../kernel/evidence/construction-observation/index.js";
import {
  inspectRustEntityClosedSubset,
  RUST_ENTITY_SOURCE_CONTROL_IDS,
  rustEntitySourceControl,
} from "./closed-subset.js";

type JsonObject = Record<string, unknown>;
type ExactRef = Readonly<{path: string; sha256: string}>;
type Validator = Readonly<{
  validator_id: string;
  validator_sha256: string;
  origin: "base" | "extension";
  ordinal: number;
  outcome: "pass" | "fail";
}>;
type NativeSnapshot = Readonly<{
  label: string;
  route: Exclude<EntityConstructionRouteV1,
    "language-visible-direct-constructor">;
  snapshot_id: string;
  entity_case_id: string;
  sequence: number;
  predecessor_snapshot_id: string | null;
  organization_id: string;
  settlement_id: string;
  state_sha256: string;
  native_hash: string;
  validator_trace: readonly Validator[];
  normalization_ordinal: number;
  identity_resolution_ordinal: number;
  construction_ordinal: number;
  immutability_ordinal: number;
}>;
type NativeExecution = Readonly<{
  pid: number;
  base_factory_id: string;
  base_factory_sha256: string;
  base_validators: readonly Omit<Validator, "ordinal" | "outcome">[];
  extension_factory_id: string;
  extension_factory_sha256: string;
  extension_validators: readonly Omit<Validator, "ordinal" | "outcome">[];
  extension_cycle_blocked: boolean;
  snapshots: readonly NativeSnapshot[];
  invalid: Readonly<{
    failure_codes: readonly string[];
    validator_trace: readonly Validator[];
  }>;
}>;

export const RUST_ENTITY_RAW_PATHS = Object.freeze({
  definition:
    "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/fixtures/settlement-entity/definition.json",
  denominator:
    "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/fixtures/settlement-entity/denominator.json",
  mutations:
    "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/fixtures/settlement-entity/mutants.json",
  descriptor:
    "projects/domainspec-v2/development/remaining-meta-types/admissions/entity/cross-language-realization-descriptor.json",
  source:
    "projects/domainspec-v2/impl/architecture-conformance/targets/rust/src/remaining_types/entity_v1.rs",
  observer:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/entity/rust/identity-lifecycle-v1/closed-subset.ts",
  proof_builder:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/entity/rust/identity-lifecycle-v1/index.ts",
  provider:
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/rust-entity-v1.ts",
  family_api:
    "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/index.ts",
  family_evaluator:
    "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/evaluator/evaluate-identity-lifecycle.ts",
  kernel_api:
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/construction-observation/index.ts",
  kernel_evaluator:
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/construction-observation/entity-lifecycle-construction-observation.ts",
  binding:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/entity/rust/identity-lifecycle-v1/rust-binding.json",
});

export type RustEntityRawInputs = Readonly<Record<
keyof typeof RUST_ENTITY_RAW_PATHS, string
>>;

type RustEntityBindingV1 = Readonly<{
  schema_version: "RustEntityBinding/v1";
  binding_id: "rust.settlement-entity.identity-lifecycle/v1";
  target_id: "entity.rust.settlement/v1";
  protocol_id: "rust.validated-extensible-entity-factory/v1";
  definition_ref: ExactRef;
  denominator_ref: ExactRef;
  mutation_catalogue_ref: ExactRef;
  descriptor_ref: ExactRef;
  source_ref: ExactRef;
  observer_ref: ExactRef;
  proof_builder_ref: ExactRef;
  provider_ref: ExactRef;
  family_api_ref: ExactRef;
  family_evaluator_ref: ExactRef;
  kernel_api_ref: ExactRef;
  kernel_evaluator_ref: ExactRef;
  observer_id: "observer.rust-entity-native/v1";
  observer_owner_ref: "rust-entity-proof-harness";
  proof_mechanism:
    "exact-source-compiled-runner-two-fresh-processes-plus-compile-negative-constructor";
  rustc_version: string;
  rustc_launcher_path: string;
  rustc_launcher_sha256: string;
  authority_effect: "none";
  binding_sha256: string;
}>;

const executeFile = promisify(execFile);
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const sha256 = (value: string | Uint8Array): string => createHash("sha256")
  .update(value)
  .digest("hex");
const isObject = (value: unknown): value is JsonObject => value !== null &&
  typeof value === "object" && !Array.isArray(value);
const fail = (code: string, detail?: string): never => {
  throw Object.assign(new Error(detail ? `${code}:${detail}` : code), {code});
};
const exactKeys = (value: JsonObject, expected: readonly string[],
  code: string): void => {
  if (JSON.stringify(Object.keys(value).sort(compareUtf8)) !==
      JSON.stringify([...expected].sort(compareUtf8))) fail(code);
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
const expectString = (value: unknown, code: string): string =>
  typeof value === "string" && value.length > 0 ? value : fail(code);
const expectSha = (value: unknown, code: string): string => {
  const digest = expectString(value, code);
  return /^[a-f0-9]{64}$/u.test(digest) ? digest : fail(code);
};
const decodeRef = (value: unknown, path: string): ExactRef => {
  if (!isObject(value)) return fail("RUST_ENTITY_BINDING_REF_INVALID", path);
  exactKeys(value, ["path", "sha256"], "RUST_ENTITY_BINDING_REF_INVALID");
  if (value.path !== path) return fail("RUST_ENTITY_BINDING_REF_INVALID", path);
  return Object.freeze({path, sha256: expectSha(value.sha256,
    "RUST_ENTITY_BINDING_REF_INVALID")});
};
const snapshotRaw = (
  incoming: Readonly<Record<string, string>>,
): RustEntityRawInputs => Object.freeze(Object.fromEntries(
  (Object.keys(RUST_ENTITY_RAW_PATHS) as readonly (
    keyof typeof RUST_ENTITY_RAW_PATHS
  )[]).map((role) => [role, typeof incoming[role] === "string"
    ? `${incoming[role]}` : fail("RUST_ENTITY_RAW_INPUT_MISSING", role)]),
)) as RustEntityRawInputs;

const decodeBinding = (
  bytes: string,
  raw: RustEntityRawInputs,
): RustEntityBindingV1 => {
  const value = parseObject(bytes, "RUST_ENTITY_BINDING_JSON_INVALID");
  exactKeys(value, [
    "schema_version", "binding_id", "target_id", "protocol_id",
    "definition_ref", "denominator_ref", "mutation_catalogue_ref",
    "descriptor_ref", "source_ref", "observer_ref", "proof_builder_ref",
    "provider_ref", "family_api_ref", "family_evaluator_ref",
    "kernel_api_ref", "kernel_evaluator_ref", "observer_id",
    "observer_owner_ref", "proof_mechanism", "rustc_version",
    "rustc_launcher_path", "rustc_launcher_sha256", "authority_effect",
    "binding_sha256",
  ], "RUST_ENTITY_BINDING_SHAPE_INVALID");
  if (value.schema_version !== "RustEntityBinding/v1" ||
      value.binding_id !== "rust.settlement-entity.identity-lifecycle/v1" ||
      value.target_id !== "entity.rust.settlement/v1" ||
      value.protocol_id !== "rust.validated-extensible-entity-factory/v1" ||
      value.observer_id !== "observer.rust-entity-native/v1" ||
      value.observer_owner_ref !== "rust-entity-proof-harness" ||
      value.proof_mechanism !==
        "exact-source-compiled-runner-two-fresh-processes-plus-compile-negative-constructor" ||
      value.authority_effect !== "none") {
    return fail("RUST_ENTITY_BINDING_POLICY_INVALID");
  }
  const binding = Object.freeze({
    schema_version: "RustEntityBinding/v1" as const,
    binding_id: "rust.settlement-entity.identity-lifecycle/v1" as const,
    target_id: "entity.rust.settlement/v1" as const,
    protocol_id: "rust.validated-extensible-entity-factory/v1" as const,
    definition_ref: decodeRef(value.definition_ref,
      RUST_ENTITY_RAW_PATHS.definition),
    denominator_ref: decodeRef(value.denominator_ref,
      RUST_ENTITY_RAW_PATHS.denominator),
    mutation_catalogue_ref: decodeRef(value.mutation_catalogue_ref,
      RUST_ENTITY_RAW_PATHS.mutations),
    descriptor_ref: decodeRef(value.descriptor_ref,
      RUST_ENTITY_RAW_PATHS.descriptor),
    source_ref: decodeRef(value.source_ref, RUST_ENTITY_RAW_PATHS.source),
    observer_ref: decodeRef(value.observer_ref, RUST_ENTITY_RAW_PATHS.observer),
    proof_builder_ref: decodeRef(value.proof_builder_ref,
      RUST_ENTITY_RAW_PATHS.proof_builder),
    provider_ref: decodeRef(value.provider_ref, RUST_ENTITY_RAW_PATHS.provider),
    family_api_ref: decodeRef(value.family_api_ref,
      RUST_ENTITY_RAW_PATHS.family_api),
    family_evaluator_ref: decodeRef(value.family_evaluator_ref,
      RUST_ENTITY_RAW_PATHS.family_evaluator),
    kernel_api_ref: decodeRef(value.kernel_api_ref,
      RUST_ENTITY_RAW_PATHS.kernel_api),
    kernel_evaluator_ref: decodeRef(value.kernel_evaluator_ref,
      RUST_ENTITY_RAW_PATHS.kernel_evaluator),
    observer_id: "observer.rust-entity-native/v1" as const,
    observer_owner_ref: "rust-entity-proof-harness" as const,
    proof_mechanism:
      "exact-source-compiled-runner-two-fresh-processes-plus-compile-negative-constructor" as const,
    rustc_version: expectString(value.rustc_version,
      "RUST_ENTITY_BINDING_TOOLCHAIN_INVALID"),
    rustc_launcher_path: expectString(value.rustc_launcher_path,
      "RUST_ENTITY_BINDING_TOOLCHAIN_INVALID"),
    rustc_launcher_sha256: expectSha(value.rustc_launcher_sha256,
      "RUST_ENTITY_BINDING_TOOLCHAIN_INVALID"),
    authority_effect: "none" as const,
    binding_sha256: expectSha(value.binding_sha256,
      "RUST_ENTITY_BINDING_DIGEST_INVALID"),
  }) satisfies RustEntityBindingV1;
  const {binding_sha256: _digest, ...body} = binding;
  if (sha256(canonicalConstructionObservationJson(body)) !==
      binding.binding_sha256) return fail("RUST_ENTITY_BINDING_DIGEST_STALE");
  const roles = Object.freeze({
    definition_ref: "definition", denominator_ref: "denominator",
    mutation_catalogue_ref: "mutations", descriptor_ref: "descriptor",
    source_ref: "source", observer_ref: "observer",
    proof_builder_ref: "proof_builder", provider_ref: "provider",
    family_api_ref: "family_api", family_evaluator_ref: "family_evaluator",
    kernel_api_ref: "kernel_api", kernel_evaluator_ref: "kernel_evaluator",
  } as const);
  for (const [refName, role] of Object.entries(roles) as readonly [
    keyof typeof roles, keyof RustEntityRawInputs,
  ][]) {
    if (sha256(raw[role]) !== binding[refName].sha256) {
      return fail("RUST_ENTITY_BINDING_INPUT_STALE", role);
    }
  }
  return binding;
};

const rustString = (value: string): string => JSON.stringify(value);
const runnerSource = (sourcePath: string): string => {
  if (sourcePath.includes('"#')) return fail("RUST_ENTITY_RUNNER_PATH_INVALID");
  return `#[path = r#"${sourcePath}"#]
mod entity_v1;

use std::hash::{Hash, Hasher};
use entity_v1::*;

struct StableHasher(u64);
impl StableHasher { fn new() -> Self { Self(0xcbf29ce484222325) } }
impl Hasher for StableHasher {
    fn finish(&self) -> u64 { self.0 }
    fn write(&mut self, bytes: &[u8]) {
        for byte in bytes {
            self.0 ^= u64::from(*byte);
            self.0 = self.0.wrapping_mul(0x100000001b3);
        }
    }
}
fn stable_hash<T: Hash>(value: &T) -> String {
    let mut hasher = StableHasher::new();
    value.hash(&mut hasher);
    format!("{:016x}", hasher.finish())
}
fn validators(values: &[ValidatorRef]) -> String {
    values.iter().map(|item| format!("{},{},{}", item.validator_id,
        item.validator_sha256, item.origin)).collect::<Vec<_>>().join(";")
}
fn trace(values: &[ValidatorTraceEntry]) -> String {
    values.iter().map(|item| format!("{},{},{},{},{}",
        item.validator.validator_id, item.validator.validator_sha256,
        item.validator.origin, item.ordinal, item.outcome))
        .collect::<Vec<_>>().join(";")
}
fn input(snapshot: &str, case_id: &str, settlement: &str) -> SettlementEntityInput {
    SettlementEntityInput {
        snapshot_id: snapshot.to_owned(), entity_case_id: case_id.to_owned(),
        sequence: 0, predecessor_snapshot_id: None,
        organization_id_sha256: ${rustString("6666666666666666666666666666666666666666666666666666666666666666")}.to_owned(),
        settlement_id_sha256: settlement.to_owned(),
        state_sha256: ${rustString("8888888888888888888888888888888888888888888888888888888888888888")}.to_owned(),
        owner_matches: true, amount_valid: true, duplicate_exists: false,
    }
}
fn emit(label: &str, result: EntityResult) -> SettlementEntitySnapshot {
    match result {
        EntityResult::Formed { snapshot, trace: route } => {
            println!("SNAP\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}",
                label, route.route.as_str(), snapshot.snapshot_id(),
                snapshot.entity_case_id(), snapshot.sequence(),
                snapshot.predecessor_snapshot_id().unwrap_or("-"),
                snapshot.identity().organization_id().normalized_value_sha256(),
                snapshot.identity().settlement_id().normalized_value_sha256(),
                snapshot.state_sha256(), stable_hash(&snapshot),
                trace(&route.validator_trace), route.normalization_ordinal,
                route.identity_resolution_ordinal, route.construction_ordinal,
                route.immutability_ordinal);
            snapshot
        }
        EntityResult::Invalid(failure) => panic!("unexpected:{:?}", failure),
    }
}
fn main() {
    println!("PID\\t{}", std::process::id());
    let base = SettlementEntityFactory::base();
    let extension = base.extend_with_duplicate_blocked().expect("extension");
    println!("FACTORY\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}",
        base.factory_id(), base.factory_sha256(), validators(base.validators()),
        extension.factory_id(), extension.factory_sha256(),
        validators(extension.validators()),
        extension.extend_with_duplicate_blocked().is_none());
    let created = emit("created", extension.create(&input(
        "snapshot.settlement-a.created", "settlement-a",
        ${rustString("7777777777777777777777777777777777777777777777777777777777777777")})));
    let _reconstructed = emit("reconstructed", extension.reconstruct(&input(
        "snapshot.settlement-a.reconstructed", "settlement-a",
        ${rustString("7777777777777777777777777777777777777777777777777777777777777777")})));
    let _completed = emit("completed", extension.transition(&created,
        "snapshot.settlement-a.completed",
        ${rustString("9999999999999999999999999999999999999999999999999999999999999999")}));
    let _distinct = emit("distinct", extension.create(&input(
        "snapshot.settlement-b.created", "settlement-b",
        ${rustString("cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc")})));
    let mut invalid = input("snapshot.invalid", "settlement-invalid",
        ${rustString("7777777777777777777777777777777777777777777777777777777777777777")});
    invalid.amount_valid = false;
    match extension.create(&invalid) {
        EntityResult::Invalid(failure) => println!("INVALID\\t{}\\t{}",
            failure.failure_codes.join(","), trace(&failure.validator_trace)),
        EntityResult::Formed { .. } => panic!("invalid-formed"),
    }
}
`;
};

const constructorProbeSource = (sourcePath: string): string =>
  `#[path = r#"${sourcePath}"#]\nmod entity_v1;\nfn main() {\n    let _constructor = entity_v1::SettlementEntitySnapshot::new;\n}\n`;

const parseValidator = (value: string, traced: boolean): Validator => {
  const parts = value.split(",");
  if (parts.length !== (traced ? 5 : 3)) {
    return fail("RUST_ENTITY_EXECUTION_OUTPUT_INVALID");
  }
  const ordinal = traced ? Number(parts[3]) : 0;
  const outcome = traced ? parts[4] : "pass";
  if (traced && (!Number.isSafeInteger(ordinal) || ordinal < 1 ||
      (outcome !== "pass" && outcome !== "fail"))) {
    return fail("RUST_ENTITY_EXECUTION_OUTPUT_INVALID");
  }
  const origin = parts[2];
  if (origin !== "base" && origin !== "extension") {
    return fail("RUST_ENTITY_EXECUTION_OUTPUT_INVALID");
  }
  return Object.freeze({
    validator_id: parts[0] ?? fail("RUST_ENTITY_EXECUTION_OUTPUT_INVALID"),
    validator_sha256: expectSha(parts[1],
      "RUST_ENTITY_EXECUTION_OUTPUT_INVALID"),
    origin,
    ordinal,
    outcome: outcome as "pass" | "fail",
  });
};
const parseValidators = (value: string, traced: boolean): readonly Validator[] =>
  Object.freeze(value.length === 0 ? [] : value.split(";")
    .map((item) => parseValidator(item, traced)));
const parseNatural = (value: string | undefined): number => {
  const parsed = Number(value);
  return Number.isSafeInteger(parsed) && parsed >= 0
    ? parsed : fail("RUST_ENTITY_EXECUTION_OUTPUT_INVALID");
};

const parseExecution = (stdout: string, stderr: string): NativeExecution => {
  if (stderr.length > 0) return fail("RUST_ENTITY_EXECUTION_STDERR", stderr);
  const lines = stdout.endsWith("\n") ? stdout.slice(0, -1).split("\n")
    : stdout.split("\n");
  if (lines.length !== 7) return fail("RUST_ENTITY_EXECUTION_OUTPUT_INVALID");
  const pidFields = lines[0]?.split("\t") ?? [];
  const pid = Number(pidFields[1]);
  if (pidFields[0] !== "PID" || !Number.isSafeInteger(pid) || pid < 1) {
    return fail("RUST_ENTITY_EXECUTION_OUTPUT_INVALID");
  }
  const factory = lines[1]?.split("\t") ?? [];
  if (factory.length !== 8 || factory[0] !== "FACTORY") {
    return fail("RUST_ENTITY_EXECUTION_OUTPUT_INVALID");
  }
  const snapshots = lines.slice(2, 6).map((line): NativeSnapshot => {
    const fields = line.split("\t");
    if (fields.length !== 16 || fields[0] !== "SNAP" ||
        (fields[2] !== "factory" &&
          fields[2] !== "deserialization-reconstruction" &&
          fields[2] !== "lifecycle-transition")) {
      return fail("RUST_ENTITY_EXECUTION_OUTPUT_INVALID");
    }
    return Object.freeze({
      label: fields[1]!,
      route: fields[2],
      snapshot_id: fields[3]!,
      entity_case_id: fields[4]!,
      sequence: parseNatural(fields[5]),
      predecessor_snapshot_id: fields[6] === "-" ? null : fields[6]!,
      organization_id: expectSha(fields[7],
        "RUST_ENTITY_EXECUTION_OUTPUT_INVALID"),
      settlement_id: expectSha(fields[8],
        "RUST_ENTITY_EXECUTION_OUTPUT_INVALID"),
      state_sha256: expectSha(fields[9],
        "RUST_ENTITY_EXECUTION_OUTPUT_INVALID"),
      native_hash: expectString(fields[10],
        "RUST_ENTITY_EXECUTION_OUTPUT_INVALID"),
      validator_trace: parseValidators(fields[11]!, true),
      normalization_ordinal: parseNatural(fields[12]),
      identity_resolution_ordinal: parseNatural(fields[13]),
      construction_ordinal: parseNatural(fields[14]),
      immutability_ordinal: parseNatural(fields[15]),
    });
  });
  const invalid = lines[6]?.split("\t") ?? [];
  if (invalid.length !== 3 || invalid[0] !== "INVALID") {
    return fail("RUST_ENTITY_EXECUTION_OUTPUT_INVALID");
  }
  return Object.freeze({
    pid,
    base_factory_id: factory[1]!,
    base_factory_sha256: expectSha(factory[2],
      "RUST_ENTITY_EXECUTION_OUTPUT_INVALID"),
    base_validators: Object.freeze(parseValidators(factory[3]!, false)
      .map(({ordinal: _ordinal, outcome: _outcome, ...item}) => item)),
    extension_factory_id: factory[4]!,
    extension_factory_sha256: expectSha(factory[5],
      "RUST_ENTITY_EXECUTION_OUTPUT_INVALID"),
    extension_validators: Object.freeze(parseValidators(factory[6]!, false)
      .map(({ordinal: _ordinal, outcome: _outcome, ...item}) => item)),
    extension_cycle_blocked: factory[7] === "true",
    snapshots: Object.freeze(snapshots),
    invalid: Object.freeze({
      failure_codes: Object.freeze(invalid[1]!.split(",")),
      validator_trace: parseValidators(invalid[2]!, true),
    }),
  });
};

const semanticExecution = (value: NativeExecution): unknown => ({
  base_factory_id: value.base_factory_id,
  base_factory_sha256: value.base_factory_sha256,
  base_validators: value.base_validators,
  extension_factory_id: value.extension_factory_id,
  extension_factory_sha256: value.extension_factory_sha256,
  extension_validators: value.extension_validators,
  extension_cycle_blocked: value.extension_cycle_blocked,
  snapshots: value.snapshots,
  invalid: value.invalid,
});

const compileAndRun = async (input: Readonly<{
  rustc: string;
  workspace: string;
  sourcePath: string;
}>): Promise<Readonly<{
  executions: readonly [NativeExecution, NativeExecution];
  direct_constructor_inaccessible: true;
}>> => {
  const runnerPath = resolve(input.workspace, "entity-native-runner.rs");
  const binaryPath = resolve(input.workspace, "entity-native-runner");
  await writeFile(runnerPath, runnerSource(input.sourcePath), {
    encoding: "utf8", flag: "wx",
  });
  await executeFile(input.rustc, ["--edition=2021", runnerPath, "-o", binaryPath], {
    env: {PATH: process.env.PATH ?? ""}, timeout: 30_000,
    maxBuffer: 1_048_576,
  }).catch((error: unknown) => fail("RUST_ENTITY_COMPILE_FAILED",
    error instanceof Error ? error.message : String(error)));
  const execute = async (): Promise<NativeExecution> => {
    const {stdout, stderr} = await executeFile(binaryPath, [], {
      env: {}, timeout: 10_000, maxBuffer: 1_048_576,
    }).catch((error: unknown) => fail("RUST_ENTITY_EXECUTION_FAILED",
      error instanceof Error ? error.message : String(error)));
    return parseExecution(stdout, stderr);
  };
  const [first, second] = await Promise.all([execute(), execute()]);
  if (first.pid === second.pid) return fail("RUST_ENTITY_PROCESS_ISOLATION_FAILED");
  if (canonicalConstructionObservationJson(semanticExecution(first)) !==
      canonicalConstructionObservationJson(semanticExecution(second))) {
    return fail("RUST_ENTITY_PROCESS_REPLAY_MISMATCH");
  }
  const probePath = resolve(input.workspace, "entity-constructor-probe.rs");
  const probeBinary = resolve(input.workspace, "entity-constructor-probe");
  await writeFile(probePath, constructorProbeSource(input.sourcePath), {
    encoding: "utf8", flag: "wx",
  });
  const probe = await executeFile(input.rustc,
    ["--edition=2021", probePath, "-o", probeBinary], {
      env: {PATH: process.env.PATH ?? ""}, timeout: 30_000,
      maxBuffer: 1_048_576,
    }).then(() => ({passed: true, stderr: ""})).catch((error: unknown) => {
      const stderr = isObject(error) && typeof error.stderr === "string"
        ? error.stderr : "";
      return {passed: false, stderr};
    });
  if (probe.passed || !probe.stderr.includes("private associated function")) {
    return fail("RUST_ENTITY_DIRECT_CONSTRUCTOR_ACCESSIBLE");
  }
  return Object.freeze({executions: Object.freeze([first, second] as const),
    direct_constructor_inaccessible: true as const});
};

const validatorCore = (value: Validator): Readonly<{
  validator_id: string;
  validator_sha256: string;
  origin: "base" | "extension";
}> => Object.freeze({validator_id: value.validator_id,
  validator_sha256: value.validator_sha256, origin: value.origin});

const buildObservation = (
  execution: NativeExecution,
  definition: IdentityLifecycleDefinitionV1,
  binding: RustEntityBindingV1,
) => {
  const byLabel = new Map(execution.snapshots.map((item) => [item.label, item]));
  const expectedLabels = ["created", "reconstructed", "completed", "distinct"];
  if (expectedLabels.some((label) => !byLabel.has(label))) {
    return fail("RUST_ENTITY_NATIVE_SNAPSHOT_MISSING");
  }
  const lockedObserver: LockedConstructionObserverRefV1 = Object.freeze({
    role: "independent-construction-observer" as const,
    observer_id: binding.observer_id,
    observer_sha256: binding.observer_ref.sha256,
    owner_ref: binding.observer_owner_ref,
    provider_id: "observer.rustc-subprocess/v1",
    provider_sha256: binding.rustc_launcher_sha256,
  });
  const traces: EntityConstructionRouteTraceV1[] = execution.snapshots
    .filter(({label}) => label !== "distinct")
    .map((item) => Object.freeze({
      route_id: item.route,
      input_class: "valid" as const,
      normalization_ordinal: item.normalization_ordinal,
      validator_trace: Object.freeze(item.validator_trace.map((validator) =>
        Object.freeze({...validatorCore(validator), ordinal: validator.ordinal,
          outcome: "pass" as const}))),
      identity_resolution_ordinal: item.identity_resolution_ordinal,
      construction_ordinal: item.construction_ordinal,
      immutability_ordinal: item.immutability_ordinal,
      direct_constructor_policy: "not-applicable" as const,
      result: Object.freeze({status: "formed" as const, snapshot_created: true,
        snapshot_id: item.snapshot_id}),
    }));
  traces.push(Object.freeze({
    route_id: "language-visible-direct-constructor" as const,
    input_class: "valid" as const,
    normalization_ordinal: null,
    validator_trace: Object.freeze([]),
    identity_resolution_ordinal: null,
    construction_ordinal: null,
    immutability_ordinal: null,
    direct_constructor_policy: "private-inaccessible" as const,
    result: Object.freeze({status: "constructor-inaccessible" as const,
      snapshot_created: false, snapshot_id: null}),
  }));
  const snapshots: EntityLifecycleSnapshotV1[] = execution.snapshots.map((item) =>
    Object.freeze({
      snapshot_id: item.snapshot_id,
      entity_case_id: item.entity_case_id,
      sequence: item.sequence,
      route_id: item.route,
      predecessor_snapshot_id: item.predecessor_snapshot_id,
      identity: Object.freeze(definition.identity_components.map((component) =>
        Object.freeze({...component, normalized_value_sha256:
          component.component_name === "organization_id"
            ? item.organization_id : item.settlement_id}))),
      state_sha256: item.state_sha256,
      frozen: true,
      mutation_observed: false,
    }));
  const byId = new Map(execution.snapshots.map((item) => [item.snapshot_id, item]));
  const equalityProbes = definition.equality_probes.map((probe) => {
    const left = byId.get(probe.left_snapshot_id) ??
      fail("RUST_ENTITY_EQUALITY_PROBE_SNAPSHOT_MISSING");
    const right = byId.get(probe.right_snapshot_id) ??
      fail("RUST_ENTITY_EQUALITY_PROBE_SNAPSHOT_MISSING");
    const observedEqual = left.organization_id === right.organization_id &&
      left.settlement_id === right.settlement_id;
    return Object.freeze({
      probe_id: probe.probe_id,
      left_snapshot_id: probe.left_snapshot_id,
      right_snapshot_id: probe.right_snapshot_id,
      relation: probe.relation,
      comparison_basis: "canonical-identity-only" as const,
      observed_equal: observedEqual,
      left_hash_sha256: sha256(left.native_hash),
      right_hash_sha256: sha256(right.native_hash),
    });
  });
  const invalidTrace = execution.invalid.validator_trace.map((validator) =>
    Object.freeze({...validatorCore(validator), ordinal: validator.ordinal,
      outcome: validator.outcome}));
  const observation = mintEntityLifecycleConstructionObservationV1({
    schema_version: "EntityLifecycleConstructionObservation/v1",
    observation_id: "observation.entity.rust.settlement/v1",
    source_kind: "target-observation",
    observer_ref: lockedObserver,
    definition_ref: definition === undefined ? fail("RUST_ENTITY_DEFINITION_MISSING")
      : Object.freeze({definition_id: definition.definition_id,
        path: RUST_ENTITY_RAW_PATHS.definition,
        sha256: binding.definition_ref.sha256}),
    factory_ref: definition.factories.base,
    route_traces: Object.freeze(traces),
    validation_failure_probe: Object.freeze({
      probe_id: definition.validation_failure.probe_id,
      route_id: "factory" as const,
      validator_trace: Object.freeze(invalidTrace),
      identity_resolution_ordinal: null,
      construction_ordinal: null,
      result: Object.freeze({status: "validation-failure" as const,
        snapshot_created: false,
        failure_codes: Object.freeze(execution.invalid.failure_codes)}),
    }),
    snapshots: Object.freeze(snapshots),
    equality_probes: Object.freeze(equalityProbes),
    extension: Object.freeze({
      base_factory_ref: definition.factories.base,
      extension_factory_ref: definition.factories.extension,
      base_validators_preserved: execution.extension_validators.slice(0, 2)
        .every((validator, index) => canonicalConstructionObservationJson(validator)
          === canonicalConstructionObservationJson(execution.base_validators[index])),
      added_validators: Object.freeze(execution.extension_validators.slice(2)),
      identity_resolver_preserved: true,
      altered_facets: Object.freeze([]),
      cycle_detected: !execution.extension_cycle_blocked,
    }),
    per_call_validator_supplied: false,
    claim: "transport-observation-only-no-native-runtime-claim",
    collision_freedom_claim: false,
    authority_effect: "none",
  });
  return Object.freeze({observation, lockedObserver});
};

export const buildRustEntityProof = async (input: Readonly<{
  raw_inputs: RustEntityRawInputs;
  workspace: string;
  rustc: string;
}>) => {
  const raw = snapshotRaw(input.raw_inputs);
  const binding = decodeBinding(raw.binding, raw);
  const definition = decodeIdentityLifecycleDefinitionV1(raw.definition,
    RUST_ENTITY_RAW_PATHS.descriptor, raw.descriptor);
  const denominator = decodeIdentityLifecycleDenominatorV1(raw.denominator,
    raw.definition, definition, RUST_ENTITY_RAW_PATHS.definition);
  const mutations = decodeIdentityLifecycleMutationCatalogueV1(raw.mutations,
    denominator);
  const subset = inspectRustEntityClosedSubset(raw.source);
  if (subset.source_sha256 !== binding.source_ref.sha256) {
    return fail("RUST_ENTITY_CLOSED_SUBSET_BINDING_STALE");
  }
  const rustcVersion = (await executeFile(input.rustc, ["--version"], {
    env: {}, timeout: 10_000, maxBuffer: 1_048_576,
  })).stdout.trim();
  const rustcLauncherSha256 = sha256(await readFile(input.rustc));
  if (rustcVersion !== binding.rustc_version ||
      input.rustc !== binding.rustc_launcher_path ||
      rustcLauncherSha256 !== binding.rustc_launcher_sha256) {
    return fail("RUST_ENTITY_TOOLCHAIN_BINDING_STALE");
  }
  const sourcePath = resolve(input.workspace, RUST_ENTITY_RAW_PATHS.source);
  const native = await compileAndRun({rustc: input.rustc,
    workspace: input.workspace, sourcePath});
  const {observation, lockedObserver} = buildObservation(native.executions[0],
    definition, binding);
  const evaluation = evaluateIdentityLifecycle({definition, denominator,
    observation, locked_observer_ref: lockedObserver});
  if (evaluation.verdict !== "pass" ||
      evaluation.positive_obligation_accounting.passed !== 5 ||
      evaluation.construction_route_accounting.conforming !== 4) {
    return fail("RUST_ENTITY_POSITIVE_PROOF_FAILED",
      canonicalConstructionObservationJson({findings: evaluation.findings,
        positives: evaluation.positive_obligation_accounting,
        routes: evaluation.construction_route_accounting}));
  }
  const familyControls = mutations.mutations.map((mutation) => {
    const mutated = applyIdentityLifecycleMutant(observation, mutation);
    const result = evaluateIdentityLifecycle({definition, denominator,
      observation: mutated, locked_observer_ref: lockedObserver});
    const actual = [...new Set(result.findings.map(({code}) => code))]
      .sort(compareUtf8);
    const expected = [...mutation.expected_finding_codes].sort(compareUtf8);
    if (canonicalConstructionObservationJson(actual) !==
        canonicalConstructionObservationJson(expected)) {
      return fail("RUST_ENTITY_FAMILY_CONTROL_SURVIVED", mutation.mutation_id);
    }
    return Object.freeze({mutation_id: mutation.mutation_id,
      hostile_class: mutation.hostile_class,
      expected_finding_codes: Object.freeze(expected as IdentityLifecycleFindingCode[]),
      actual_finding_codes: Object.freeze(actual), status: "killed" as const,
      mechanism: "portable-observation-mutation" as const});
  });
  const sourceControls = RUST_ENTITY_SOURCE_CONTROL_IDS.map((controlId) => {
    const hostile = rustEntitySourceControl(raw.source, controlId);
    if (hostile === raw.source) return fail("RUST_ENTITY_SOURCE_CONTROL_NOOP");
    let rejected = false;
    try {
      inspectRustEntityClosedSubset(hostile);
    } catch (error: unknown) {
      rejected = isObject(error) &&
        error.code === "RUST_ENTITY_CLOSED_SUBSET_SOURCE_MISMATCH";
    }
    if (!rejected) return fail("RUST_ENTITY_SOURCE_CONTROL_SURVIVED", controlId);
    return Object.freeze({control_id: controlId, status: "killed" as const,
      mechanism: "non-noop-source-mutation-exact-byte-static-rejection" as const,
      hostile_sha256: sha256(hostile)});
  });
  const semanticDigest = sha256(canonicalConstructionObservationJson({
    execution: semanticExecution(native.executions[0]),
    observation_sha256: observation.observation_sha256,
    evaluation_id: evaluation.evaluation_id,
  }));
  return Object.freeze({
    schema_version: "RustEntityProof/v1" as const,
    result: "pass" as const,
    target: Object.freeze({target_id: binding.target_id, language: "rust" as const,
      protocol_id: binding.protocol_id, source_sha256: binding.source_ref.sha256,
      form: subset.form}),
    native_runtime: Object.freeze({compiled: true, executed: true,
      process_count: 2, distinct_processes:
        native.executions[0].pid !== native.executions[1].pid,
      replay_semantic_digest_sha256: semanticDigest,
      pid_and_workspace_redacted_from_semantic_digest: true,
      direct_constructor_inaccessible:
        native.direct_constructor_inaccessible}),
    observation,
    evaluation,
    source_controls: Object.freeze(sourceControls),
    predecessor_family_controls: Object.freeze(familyControls),
    accounting: Object.freeze({
      positives: Object.freeze({declared: 5, passed: 5}),
      construction_routes: Object.freeze({declared: 4, conforming: 4}),
      source_hostiles: Object.freeze({declared: sourceControls.length,
        killed: sourceControls.length,
        mechanism: "static-exact-source-rejection" as const}),
      predecessor_family_controls: Object.freeze({declared: familyControls.length,
        killed: familyControls.length,
        mechanism: "portable-observation-evaluation" as const}),
    }),
    binding: Object.freeze({binding_id: binding.binding_id,
      binding_sha256: binding.binding_sha256,
      rustc_version: binding.rustc_version,
      rustc_launcher_path: binding.rustc_launcher_path,
      rustc_launcher_sha256: binding.rustc_launcher_sha256}),
    claim_ceiling: "Candidate-local exact hash-bound Rust Settlement Entity target compiled and executed in two fresh native processes with private typed composite identity, identity-only equality and hashing, immutable owned lifecycle snapshots, base-before-extension validators, structured no-snapshot failure, additive acyclic factory composition, factory/reconstruction/transition convergence, compile-negative direct-constructor inaccessibility, 5/5 portable positives, 4/4 routes, 12/12 non-noop static source-hostile rejections, and 7/7 predecessor observation controls under the current bound files and rustc. Source hostile controls are exact-byte static rejections, not executed mutant behavior. This does not prove collision freedom, cross-language parity, registration, candidate projection, promotion, publication, release, deployment, or production behavior.",
    authority_effect: "none" as const,
  });
};
