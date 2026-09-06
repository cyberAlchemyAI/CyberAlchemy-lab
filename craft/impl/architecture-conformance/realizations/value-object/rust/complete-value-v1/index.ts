import {execFile} from "node:child_process";
import {createHash} from "node:crypto";
import {readFile, writeFile} from "node:fs/promises";
import {resolve} from "node:path";
import {promisify} from "node:util";

import {
  applyCompleteValueMutant,
  decodeCompleteValueDefinitionV1,
  decodeCompleteValueDenominatorV1,
  decodeCompleteValueMutationCatalogueV1,
  evaluateCompleteValue,
  type CompleteValueFindingCode,
} from "../../../../families/complete-value/index.js";
import {
  canonicalConstructionObservationJson,
  mintConstructionObservationV1,
  type LockedConstructionObserverRefV1,
} from "../../../../kernel/evidence/construction-observation/index.js";
import {
  inspectRustValueObjectClosedSubset,
  RUST_VALUE_OBJECT_STATIC_CONTROL_IDS,
  rustValueObjectStaticControlSource,
} from "./closed-subset.js";

type JsonObject = Record<string, unknown>;
type ExactRef = Readonly<{path: string; sha256: string}>;

export const RUST_VALUE_OBJECT_RAW_PATHS = Object.freeze({
  definition:
    "projects/domainspec-v2/impl/architecture-conformance/families/complete-value/fixtures/settlement-value/definition.json",
  denominator:
    "projects/domainspec-v2/impl/architecture-conformance/families/complete-value/fixtures/settlement-value/denominator.json",
  mutations:
    "projects/domainspec-v2/impl/architecture-conformance/families/complete-value/fixtures/settlement-value/mutants.json",
  descriptor:
    "projects/domainspec-v2/development/remaining-meta-types/admissions/value-object/cross-language-realization-descriptor.json",
  source:
    "projects/domainspec-v2/impl/architecture-conformance/targets/rust/src/remaining_types/value_object_v1.rs",
  observer:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/value-object/rust/complete-value-v1/closed-subset.ts",
  proof_builder:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/value-object/rust/complete-value-v1/index.ts",
  provider:
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/rust-value-object-v1.ts",
  family_api:
    "projects/domainspec-v2/impl/architecture-conformance/families/complete-value/index.ts",
  kernel_api:
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/construction-observation/index.ts",
  binding:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/value-object/rust/complete-value-v1/rust-binding.json",
});

export type RustValueObjectRawInputs = Readonly<Record<
keyof typeof RUST_VALUE_OBJECT_RAW_PATHS, string
>>;

type RustValueObjectBindingV1 = Readonly<{
  schema_version: "RustValueObjectBinding/v1";
  binding_id: "rust.settlement-value.complete-value/v1";
  target_id: "value-object.rust.settlement-value/v1";
  protocol_id: "rust.owned-value-object-factory/v1";
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
  observer_id: "observer.rust-value-object-exact-source/v1";
  observer_owner_ref: "rust-value-object-proof-harness";
  proof_mechanism: "exact-source-compiled-runner-two-fresh-processes";
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
const isObject = (value: unknown): value is JsonObject => value !== null
  && typeof value === "object" && !Array.isArray(value);
const fail = (code: string, detail?: string): never => {
  throw Object.assign(new Error(detail ? `${code}:${detail}` : code), {code});
};
const exactKeys = (value: JsonObject, expected: readonly string[], code: string): void => {
  if (JSON.stringify(Object.keys(value).sort(compareUtf8))
      !== JSON.stringify([...expected].sort(compareUtf8))) fail(code);
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
const expectSha256 = (value: unknown, code: string): string => {
  const digest = expectString(value, code);
  return /^[a-f0-9]{64}$/u.test(digest) ? digest : fail(code);
};
const same = (left: unknown, right: unknown): boolean =>
  canonicalConstructionObservationJson(left)
    === canonicalConstructionObservationJson(right);
const decodeRef = (value: unknown, path: string): ExactRef => {
  if (!isObject(value)) return fail("RUST_VALUE_OBJECT_BINDING_REF_INVALID", path);
  exactKeys(value, ["path", "sha256"],
    "RUST_VALUE_OBJECT_BINDING_REF_INVALID");
  if (value.path !== path) return fail("RUST_VALUE_OBJECT_BINDING_REF_INVALID", path);
  return Object.freeze({path, sha256: expectSha256(value.sha256,
    "RUST_VALUE_OBJECT_BINDING_REF_INVALID")});
};

const snapshotRaw = (
  incoming: Readonly<Record<string, string>>,
): RustValueObjectRawInputs => Object.freeze(Object.fromEntries(
  (Object.keys(RUST_VALUE_OBJECT_RAW_PATHS) as readonly (
    keyof typeof RUST_VALUE_OBJECT_RAW_PATHS
  )[]).map((role) => [role, typeof incoming[role] === "string"
    ? `${incoming[role]}` : fail("RUST_VALUE_OBJECT_RAW_INPUT_MISSING", role)]),
)) as RustValueObjectRawInputs;

const decodeBinding = (
  bytes: string,
  raw: RustValueObjectRawInputs,
): RustValueObjectBindingV1 => {
  const source = parseObject(bytes, "RUST_VALUE_OBJECT_BINDING_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "binding_id", "target_id", "protocol_id",
    "definition_ref", "denominator_ref", "mutation_catalogue_ref",
    "descriptor_ref", "source_ref", "observer_ref", "proof_builder_ref",
    "provider_ref", "family_api_ref", "kernel_api_ref", "observer_id",
    "observer_owner_ref", "proof_mechanism", "rustc_version",
    "rustc_launcher_path", "rustc_launcher_sha256", "authority_effect",
    "binding_sha256",
  ], "RUST_VALUE_OBJECT_BINDING_SHAPE_INVALID");
  if (source.schema_version !== "RustValueObjectBinding/v1"
      || source.binding_id !== "rust.settlement-value.complete-value/v1"
      || source.target_id !== "value-object.rust.settlement-value/v1"
      || source.protocol_id !== "rust.owned-value-object-factory/v1"
      || source.observer_id !== "observer.rust-value-object-exact-source/v1"
      || source.observer_owner_ref !== "rust-value-object-proof-harness"
      || source.proof_mechanism
        !== "exact-source-compiled-runner-two-fresh-processes"
      || source.authority_effect !== "none") {
    return fail("RUST_VALUE_OBJECT_BINDING_POLICY_INVALID");
  }
  const binding = Object.freeze({
    schema_version: "RustValueObjectBinding/v1" as const,
    binding_id: "rust.settlement-value.complete-value/v1" as const,
    target_id: "value-object.rust.settlement-value/v1" as const,
    protocol_id: "rust.owned-value-object-factory/v1" as const,
    definition_ref: decodeRef(source.definition_ref,
      RUST_VALUE_OBJECT_RAW_PATHS.definition),
    denominator_ref: decodeRef(source.denominator_ref,
      RUST_VALUE_OBJECT_RAW_PATHS.denominator),
    mutation_catalogue_ref: decodeRef(source.mutation_catalogue_ref,
      RUST_VALUE_OBJECT_RAW_PATHS.mutations),
    descriptor_ref: decodeRef(source.descriptor_ref,
      RUST_VALUE_OBJECT_RAW_PATHS.descriptor),
    source_ref: decodeRef(source.source_ref, RUST_VALUE_OBJECT_RAW_PATHS.source),
    observer_ref: decodeRef(source.observer_ref,
      RUST_VALUE_OBJECT_RAW_PATHS.observer),
    proof_builder_ref: decodeRef(source.proof_builder_ref,
      RUST_VALUE_OBJECT_RAW_PATHS.proof_builder),
    provider_ref: decodeRef(source.provider_ref,
      RUST_VALUE_OBJECT_RAW_PATHS.provider),
    family_api_ref: decodeRef(source.family_api_ref,
      RUST_VALUE_OBJECT_RAW_PATHS.family_api),
    kernel_api_ref: decodeRef(source.kernel_api_ref,
      RUST_VALUE_OBJECT_RAW_PATHS.kernel_api),
    observer_id: "observer.rust-value-object-exact-source/v1" as const,
    observer_owner_ref: "rust-value-object-proof-harness" as const,
    proof_mechanism:
      "exact-source-compiled-runner-two-fresh-processes" as const,
    rustc_version: expectString(source.rustc_version,
      "RUST_VALUE_OBJECT_BINDING_TOOLCHAIN_INVALID"),
    rustc_launcher_path: expectString(source.rustc_launcher_path,
      "RUST_VALUE_OBJECT_BINDING_TOOLCHAIN_INVALID"),
    rustc_launcher_sha256: expectSha256(source.rustc_launcher_sha256,
      "RUST_VALUE_OBJECT_BINDING_TOOLCHAIN_INVALID"),
    authority_effect: "none" as const,
    binding_sha256: expectSha256(source.binding_sha256,
      "RUST_VALUE_OBJECT_BINDING_DIGEST_INVALID"),
  }) satisfies RustValueObjectBindingV1;
  const {binding_sha256: _digest, ...body} = binding;
  if (sha256(canonicalConstructionObservationJson(body))
      !== binding.binding_sha256) {
    return fail("RUST_VALUE_OBJECT_BINDING_DIGEST_STALE");
  }
  const roles = Object.freeze({
    definition_ref: "definition", denominator_ref: "denominator",
    mutation_catalogue_ref: "mutations", descriptor_ref: "descriptor",
    source_ref: "source", observer_ref: "observer",
    proof_builder_ref: "proof_builder", provider_ref: "provider",
    family_api_ref: "family_api", kernel_api_ref: "kernel_api",
  } as const);
  for (const [refName, role] of Object.entries(roles) as readonly [
    keyof typeof roles, keyof RustValueObjectRawInputs,
  ][]) {
    if (sha256(raw[role]) !== binding[refName].sha256) {
      return fail("RUST_VALUE_OBJECT_BINDING_INPUT_STALE", role);
    }
  }
  return binding;
};

const rustString = (value: string): string => JSON.stringify(value);

const runnerSource = (
  sourcePath: string,
  definition: ReturnType<typeof decodeCompleteValueDefinitionV1>,
): string => {
  const cases = definition.cases.map((item) => {
    const values = item.normalized_component_values;
    return `        (${rustString(item.case_id)}, ${rustString(item.input_class)}, owner_input(
            ${rustString(values.currency!)},
            ${rustString(values.minor_units!)},
            ${rustString(values.settlement_account!)},
            ${item.input_class === "invalid" ? "true" : "false"},
            true,
            ${rustString(`account-ref-${item.case_id}`)},
        )),`;
  }).join("\n");
  const probes = [
    {...definition.equality_contract.equal_probe, relation: "equal-tuple",
      component_name: null},
    ...definition.equality_contract.component_variants.map((item) => ({
      ...item, relation: "component-variant",
    })),
  ].map((item) => `        (${rustString(item.probe_id)},
            ${rustString(item.left_case_id)}, ${rustString(item.right_case_id)},
            ${rustString(item.relation)}, ${rustString(item.component_name ?? "-")}),`)
    .join("\n");
  if (sourcePath.includes('"#')) return fail("RUST_VALUE_OBJECT_RUNNER_PATH_INVALID");
  return `#[path = r#"${sourcePath}"#]
mod value_object_v1;

use std::collections::BTreeMap;
use std::hash::{Hash, Hasher};
use value_object_v1::*;

struct StableHasher(u64);

impl StableHasher {
    fn new() -> Self { Self(0xcbf29ce484222325) }
}

impl Hasher for StableHasher {
    fn finish(&self) -> u64 { self.0 }
    fn write(&mut self, bytes: &[u8]) {
        for byte in bytes {
            self.0 ^= u64::from(*byte);
            self.0 = self.0.wrapping_mul(0x100000001b3);
        }
    }
}

fn stable_hash<T: Hash>(value: &T) -> u64 {
    let mut hasher = StableHasher::new();
    value.hash(&mut hasher);
    hasher.finish()
}

fn component(id: &str, digest: &str, value: &str) -> ComponentInput {
    ComponentInput {
        protocol_id: id.to_owned(),
        protocol_sha256: digest.to_owned(),
        normalized_value_sha256: value.to_owned(),
    }
}

fn owner_input(
    currency: &str,
    minor: &str,
    account: &str,
    negative: bool,
    active: bool,
    account_ref: &str,
) -> SettlementValueInput {
    SettlementValueInput {
        currency: component(CURRENCY_PROTOCOL_ID, CURRENCY_PROTOCOL_SHA256, currency),
        minor_units: component(
            MINOR_UNITS_PROTOCOL_ID,
            MINOR_UNITS_PROTOCOL_SHA256,
            minor,
        ),
        minor_units_negative: negative,
        settlement_account: SettlementAccountInput {
            component: component(
                SETTLEMENT_ACCOUNT_PROTOCOL_ID,
                SETTLEMENT_ACCOUNT_PROTOCOL_SHA256,
                account,
            ),
            account_ref: account_ref.to_owned(),
            active,
        },
    }
}

fn encode_validators(values: &[ValidatorRef]) -> String {
    values.iter().map(|item| format!(
        "{}@{}@{}",
        item.validator_id, item.validator_sha256, item.origin,
    )).collect::<Vec<_>>().join(",")
}

fn encode_bindings(values: &[ComponentBinding; 3]) -> String {
    values.iter().map(|item| format!(
        "{},{},{},{},{}",
        item.component_name,
        item.protocol_id,
        item.protocol_sha256,
        item.normalized_value_sha256,
        item.nested_value_object,
    )).collect::<Vec<_>>().join(";")
}

fn main() {
    println!("PID\\t{}", std::process::id());
    let base = SettlementValueFactory::base();
    let extension = base.extend_with_account_active().expect("extension");
    println!(
        "FACTORY\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}",
        base.factory_id(),
        base.factory_sha256(),
        encode_validators(base.validators()),
        extension.factory_id(),
        extension.factory_sha256(),
        encode_validators(extension.validators()),
        extension.extend_with_account_active().is_none(),
    );

    let cases = vec![
${cases}
    ];
    let mut values: BTreeMap<&str, SettlementValue> = BTreeMap::new();
    for (case_id, input_class, input) in &cases {
        let base_result = base.create(input);
        let extension_result = extension.create(input);
        match (base_result, extension_result) {
            (
                FormationResult::Formed { value: base_value, .. },
                FormationResult::Formed { value, validator_trace },
            ) => {
                let bindings = encode_bindings(value.component_bindings());
                let tuple = value.normalized_tuple().join(",");
                let hash = stable_hash(&value);
                let base_hash = stable_hash(&base_value);
                println!(
                    "CASE\\t{}\\t{}\\ttrue\\t-\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}",
                    case_id,
                    input_class,
                    validator_trace.join(","),
                    bindings,
                    tuple,
                    hash,
                    base_hash,
                    value == base_value,
                    value.settlement_account().account_ref(),
                );
                values.insert(case_id, value);
            }
            (
                FormationResult::Invalid(base_failure),
                FormationResult::Invalid(failure),
            ) => {
                println!(
                    "CASE\\t{}\\t{}\\tfalse\\t{}\\t{}\\t-\\t-\\t-\\t-\\t{}\\t-",
                    case_id,
                    input_class,
                    failure.failure_codes.join(","),
                    failure.validator_trace.join(","),
                    base_failure.failure_codes == failure.failure_codes,
                );
            }
            _ => panic!("base-extension-result-divergence"),
        }
    }

    let probes = vec![
${probes}
    ];
    for (probe_id, left_id, right_id, relation, component_name) in probes {
        let left = values.get(left_id).expect("left value");
        let right = values.get(right_id).expect("right value");
        println!(
            "PROBE\\t{}\\t{}\\t{}\\t{}\\t{}\\ttrue\\t{}\\t{}\\t{}",
            probe_id,
            left_id,
            right_id,
            relation,
            component_name,
            left == right,
            stable_hash(left),
            stable_hash(right),
        );
    }

    let left = values.get("settlement-base").expect("base").settlement_account();
    let equal = values.get("settlement-equal-copy")
        .expect("equal").settlement_account();
    let variant = values.get("settlement-account-variant")
        .expect("variant").settlement_account();
    println!(
        "NESTED\\tsettlement_account\\t{}\\t{}\\t{}\\t{}\\t{}",
        left.protocol_id(),
        left.protocol_sha256(),
        left == equal,
        stable_hash(left) == stable_hash(equal),
        left != variant,
    );

    let valid = &cases[0].2;
    let base_value = match base.create(valid) {
        FormationResult::Formed { value, .. } => value,
        FormationResult::Invalid(_) => panic!("base valid failure"),
    };
    let extended_value = match extension.create(valid) {
        FormationResult::Formed { value, .. } => value,
        FormationResult::Invalid(_) => panic!("extension valid failure"),
    };
    let mut inactive = valid.clone();
    inactive.settlement_account.active = false;
    let base_inactive_ok = matches!(base.create(&inactive), FormationResult::Formed { .. });
    let (extension_inactive_ok, failure_codes, validator_trace) =
        match extension.create(&inactive) {
            FormationResult::Invalid(failure) => (
                false,
                failure.failure_codes.join(","),
                failure.validator_trace.join(","),
            ),
            FormationResult::Formed { .. } => (true, "-".to_owned(), "-".to_owned()),
        };
    println!(
        "EXTENSION\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}",
        base_inactive_ok,
        extension_inactive_ok,
        failure_codes,
        validator_trace,
        base_value == extended_value,
        stable_hash(&base_value) == stable_hash(&extended_value),
        extension.extend_with_account_active().is_none(),
    );
    let mut alias_input = cases[0].2.clone();
    let alias_value = match base.create(&alias_input) {
        FormationResult::Formed { value, .. } => value,
        FormationResult::Invalid(_) => panic!("alias owner case failed"),
    };
    let owned_account_ref = alias_value.settlement_account().account_ref().to_owned();
    alias_input.settlement_account.account_ref.push_str("-caller-mutated");
    println!(
        "OWNERSHIP\\t{}",
        alias_value.settlement_account().account_ref() == owned_account_ref,
    );
}
`;
};

const parseBoolean = (value: string, code: string): boolean => {
  if (value === "true") return true;
  if (value === "false") return false;
  return fail(code);
};
const splitList = (value: string): string[] => value === "-" || value === ""
  ? [] : value.split(",");

const parseExecution = (stdout: string): Readonly<{
  pid: number;
  semantic: JsonObject;
}> => {
  const lines = stdout.trimEnd().split("\n").map((line) => line.split("\t"));
  const pidLine = lines.find(([kind]) => kind === "PID");
  const factoryLine = lines.find(([kind]) => kind === "FACTORY");
  const nestedLine = lines.find(([kind]) => kind === "NESTED");
  const extensionLine = lines.find(([kind]) => kind === "EXTENSION");
  const ownershipLine = lines.find(([kind]) => kind === "OWNERSHIP");
  if (!pidLine || pidLine.length !== 2 || !factoryLine
      || factoryLine.length !== 8 || !nestedLine || nestedLine.length !== 7
      || !extensionLine || extensionLine.length !== 8
      || !ownershipLine || ownershipLine.length !== 2) {
    return fail("RUST_VALUE_OBJECT_NATIVE_OUTPUT_INVALID");
  }
  const pid = Number(pidLine[1]);
  if (!Number.isSafeInteger(pid) || pid <= 0) {
    return fail("RUST_VALUE_OBJECT_NATIVE_PID_INVALID");
  }
  const cases = lines.filter(([kind]) => kind === "CASE").map((fields) => {
    if (fields.length !== 12) return fail("RUST_VALUE_OBJECT_NATIVE_CASE_INVALID");
    const bindings = fields[6] === "-" ? [] : fields[6]!.split(";").map((item) => {
      const parts = item.split(",");
      if (parts.length !== 5) return fail("RUST_VALUE_OBJECT_NATIVE_BINDING_INVALID");
      return Object.freeze({component_name: parts[0]!, protocol_id: parts[1]!,
        protocol_sha256: parts[2]!, normalized_value_sha256: parts[3]!,
        nested_value_object: parseBoolean(parts[4]!,
          "RUST_VALUE_OBJECT_NATIVE_BINDING_INVALID")});
    });
    return Object.freeze({case_id: fields[1]!, input_class: fields[2]!,
      ok: parseBoolean(fields[3]!, "RUST_VALUE_OBJECT_NATIVE_CASE_INVALID"),
      failure_codes: splitList(fields[4]!), validator_trace: splitList(fields[5]!),
      component_bindings: bindings, tuple: fields[7] === "-" ? null
        : fields[7]!.split(","), hash: fields[8] === "-" ? null : fields[8]!,
      base_hash: fields[9] === "-" ? null : fields[9]!,
      base_equal: parseBoolean(fields[10]!,
        "RUST_VALUE_OBJECT_NATIVE_CASE_INVALID"),
      account_ref: fields[11] === "-" ? null : fields[11]!});
  });
  const probes = lines.filter(([kind]) => kind === "PROBE").map((fields) => {
    if (fields.length !== 10) return fail("RUST_VALUE_OBJECT_NATIVE_PROBE_INVALID");
    return Object.freeze({probe_id: fields[1]!, left_case_id: fields[2]!,
      right_case_id: fields[3]!, relation: fields[4]!,
      varied_component_name: fields[5] === "-" ? null : fields[5]!,
      references_distinct: parseBoolean(fields[6]!,
        "RUST_VALUE_OBJECT_NATIVE_PROBE_INVALID"),
      observed_equal: parseBoolean(fields[7]!,
        "RUST_VALUE_OBJECT_NATIVE_PROBE_INVALID"),
      left_hash: fields[8]!, right_hash: fields[9]!});
  });
  const parseValidators = (value: string) => splitList(value).map((item) => {
    const [validator_id, validator_sha256, origin] = item.split("@");
    return Object.freeze({validator_id, validator_sha256, origin});
  });
  return Object.freeze({pid, semantic: Object.freeze({
    cases: Object.freeze(cases),
    probes: Object.freeze(probes),
    factory: Object.freeze({base_factory_id: factoryLine[1]!,
      base_factory_sha256: factoryLine[2]!,
      base_validators: Object.freeze(parseValidators(factoryLine[3]!)),
      extension_factory_id: factoryLine[4]!,
      extension_factory_sha256: factoryLine[5]!,
      extension_validators: Object.freeze(parseValidators(factoryLine[6]!)),
      extension_terminal: parseBoolean(factoryLine[7]!,
        "RUST_VALUE_OBJECT_NATIVE_FACTORY_INVALID")}),
    nested: Object.freeze({component_name: nestedLine[1]!,
      protocol_id: nestedLine[2]!, protocol_sha256: nestedLine[3]!,
      equal_observed: parseBoolean(nestedLine[4]!,
        "RUST_VALUE_OBJECT_NATIVE_NESTED_INVALID"),
      equal_hash_congruent: parseBoolean(nestedLine[5]!,
        "RUST_VALUE_OBJECT_NATIVE_NESTED_INVALID"),
      variant_unequal_observed: parseBoolean(nestedLine[6]!,
        "RUST_VALUE_OBJECT_NATIVE_NESTED_INVALID")}),
    extension: Object.freeze({base_inactive_ok: parseBoolean(extensionLine[1]!,
      "RUST_VALUE_OBJECT_NATIVE_EXTENSION_INVALID"),
    extension_inactive_ok: parseBoolean(extensionLine[2]!,
      "RUST_VALUE_OBJECT_NATIVE_EXTENSION_INVALID"),
    failure_codes: Object.freeze(splitList(extensionLine[3]!)),
    validator_trace: Object.freeze(splitList(extensionLine[4]!)),
    preserved_equal: parseBoolean(extensionLine[5]!,
      "RUST_VALUE_OBJECT_NATIVE_EXTENSION_INVALID"),
    preserved_hash: parseBoolean(extensionLine[6]!,
      "RUST_VALUE_OBJECT_NATIVE_EXTENSION_INVALID"),
    terminal: parseBoolean(extensionLine[7]!,
      "RUST_VALUE_OBJECT_NATIVE_EXTENSION_INVALID")}),
    ownership: Object.freeze({defensive_nested_ownership: parseBoolean(
      ownershipLine[1]!, "RUST_VALUE_OBJECT_NATIVE_OWNERSHIP_INVALID")}),
  })});
};

const provePrivateImmutability = async (
  workspace: string,
  rustc: string,
  sourcePath: string,
): Promise<Readonly<{rejected_private_mutations: 2; diagnostic_code: "E0616"}>> => {
  const probePath = resolve(workspace, "rust-value-object-immutability-probe.rs");
  const outputPath = resolve(workspace, "rust-value-object-immutability-probe.rmeta");
  await writeFile(probePath, `#[path = r#"${sourcePath}"#]
mod value_object_v1;
use value_object_v1::{SettlementAccountValue, SettlementValue};
fn mutate_outer(mut value: SettlementValue) {
    value.currency_sha256 = String::new();
}
fn mutate_nested(mut value: SettlementAccountValue) {
    value.protocol_id = String::new();
}
fn main() {}
`, {encoding: "utf8", flag: "wx"});
  const rejected: unknown = await executeFile(rustc, ["--edition=2021",
    "--emit=metadata", probePath, "-o", outputPath], {
    cwd: workspace, timeout: 20_000, maxBuffer: 2_097_152,
  }).then(() => null).catch((error: unknown) => error);
  if (rejected === null || !isObject(rejected)
      || typeof rejected.stderr !== "string"
      || (rejected.stderr.match(/error\[E0616\]/gu) ?? []).length !== 2) {
    return fail("RUST_VALUE_OBJECT_PRIVATE_IMMUTABILITY_UNPROVEN");
  }
  return Object.freeze({rejected_private_mutations: 2 as const,
    diagnostic_code: "E0616" as const});
};

const rustProtocol = (value: string): string => value.replace(
  /^typescript\.owned-value-component/u,
  "rust.eq-hash-value-component",
);

export const buildRustValueObjectProof = async (input: Readonly<{
  raw_inputs: Readonly<Record<string, string>>;
  workspace: string;
  rustc: string;
}>) => {
  const raw = snapshotRaw(input.raw_inputs);
  const binding = decodeBinding(raw.binding, raw);
  const definition = decodeCompleteValueDefinitionV1(raw.definition,
    RUST_VALUE_OBJECT_RAW_PATHS.descriptor, raw.descriptor);
  const denominator = decodeCompleteValueDenominatorV1(raw.denominator,
    raw.definition, definition, RUST_VALUE_OBJECT_RAW_PATHS.definition);
  const catalogue = decodeCompleteValueMutationCatalogueV1(raw.mutations,
    denominator, definition);
  const sourceProof = inspectRustValueObjectClosedSubset(raw.source);
  if (sourceProof.source_sha256 !== binding.source_ref.sha256) {
    return fail("RUST_VALUE_OBJECT_NATIVE_SOURCE_STALE");
  }
  const rustcVersion = (await executeFile(input.rustc, ["--version"], {
    timeout: 10_000,
  })).stdout.trim();
  const rustcLauncherSha256 = sha256(await readFile(input.rustc));
  if (rustcVersion !== binding.rustc_version
      || input.rustc !== binding.rustc_launcher_path
      || rustcLauncherSha256 !== binding.rustc_launcher_sha256) {
    return fail("RUST_VALUE_OBJECT_TOOLCHAIN_STALE");
  }
  const runnerPath = resolve(input.workspace, "rust-value-object-runner.rs");
  const binaryPath = resolve(input.workspace, "rust-value-object-runner");
  await writeFile(runnerPath, runnerSource(
    resolve(input.workspace, RUST_VALUE_OBJECT_RAW_PATHS.source), definition,
  ), {encoding: "utf8", flag: "wx"});
  await executeFile(input.rustc, ["--edition=2021", runnerPath, "-o", binaryPath], {
    cwd: input.workspace, timeout: 30_000, maxBuffer: 2_097_152,
  });
  const immutabilityProof = await provePrivateImmutability(input.workspace,
    input.rustc, resolve(input.workspace, RUST_VALUE_OBJECT_RAW_PATHS.source));
  const executions = await Promise.all([0, 1].map(async () => parseExecution(
    (await executeFile(binaryPath, [], {cwd: input.workspace, timeout: 20_000,
      maxBuffer: 2_097_152})).stdout,
  )));
  if (executions[0]!.pid === executions[1]!.pid
      || !same(executions[0]!.semantic, executions[1]!.semantic)) {
    return fail("RUST_VALUE_OBJECT_PROCESS_REPLAY_MISMATCH");
  }
  const runtime = executions[0]!.semantic;
  const ownership = runtime.ownership as JsonObject;
  if (ownership.defensive_nested_ownership !== true
      || immutabilityProof.rejected_private_mutations !== 2) {
    return fail("RUST_VALUE_OBJECT_NATIVE_OWNERSHIP_INVALID");
  }
  const rows = runtime.cases as readonly JsonObject[];
  if (rows.length !== definition.cases.length) {
    return fail("RUST_VALUE_OBJECT_NATIVE_CASE_LEDGER_MISMATCH");
  }
  const observer: LockedConstructionObserverRefV1 = Object.freeze({
    role: "independent-construction-observer",
    observer_id: binding.observer_id,
    observer_sha256: binding.observer_ref.sha256,
    owner_ref: binding.observer_owner_ref,
    provider_id: "rust-value-object-v1",
    provider_sha256: binding.provider_ref.sha256,
  });
  const attempts = definition.cases.map((testCase, index) => {
    const row = rows[index]!;
    const expectedOk = testCase.input_class === "valid";
    const expectedNativeBindings = definition.components.map((component) => ({
      component_name: component.component_name,
      protocol_id: rustProtocol(component.protocol_id),
      protocol_sha256: component.protocol_sha256,
      normalized_value_sha256:
        testCase.normalized_component_values[component.component_name],
      nested_value_object: component.nested_value_object,
    }));
    const trace = row.validator_trace as readonly string[];
    const expectedTraceLength = expectedOk ? definition.validators.length : 2;
    const expectedTrace = definition.validators.slice(0, expectedTraceLength)
      .map(({validator_id: id, validator_sha256: digest}) => `${id}@${digest}`);
    if (row.case_id !== testCase.case_id
        || row.input_class !== testCase.input_class || row.ok !== expectedOk
        || !same(row.failure_codes, testCase.expected_failure_codes)
        || !same(trace, expectedTrace)
        || !same(row.component_bindings, expectedOk ? expectedNativeBindings : [])
        || !same(row.tuple, expectedOk ? expectedNativeBindings.map(
          ({normalized_value_sha256: value}) => value) : null)
        || row.base_equal !== true
        || (expectedOk && (typeof row.hash !== "string"
          || !/^[0-9]+$/u.test(row.hash) || row.hash !== row.base_hash
          || row.account_ref !== `account-ref-${testCase.case_id}`))) {
      return fail("RUST_VALUE_OBJECT_NATIVE_CASE_INVALID", testCase.case_id);
    }
    const portableBindings = expectedNativeBindings.map((component) => ({
      ...component,
      protocol_id: definition.components.find(({component_name: name}) =>
        name === component.component_name)!.protocol_id,
    }));
    return {
      case_id: testCase.case_id,
      input_class: testCase.input_class,
      component_bindings: portableBindings,
      validator_trace: trace.map((entry, ordinal) => {
        const [validatorId, validatorSha256] = entry.split("@");
        const owner = definition.validators.find(({validator_id: id}) =>
          id === validatorId);
        if (!owner || owner.validator_sha256 !== validatorSha256) {
          return fail("RUST_VALUE_OBJECT_NATIVE_VALIDATOR_INVALID");
        }
        return {validator_id: validatorId!, validator_sha256: validatorSha256!,
          origin: owner.origin, ordinal, outcome: expectedOk ? "pass" as const
            : ordinal === trace.length - 1 ? "fail" as const : "pass" as const};
      }),
      formation_ordinal: expectedOk ? trace.length : null,
      result: expectedOk ? {status: "formed" as const, object_created: true,
        failure_codes: [] as readonly string[]} : {
        status: "validation-failure" as const, object_created: false,
        failure_codes: row.failure_codes as readonly string[]},
      normalized_tuple: expectedOk ? portableBindings.map(({component_name,
        normalized_value_sha256}) => ({component_name, normalized_value_sha256}))
        : null,
      immutability: {formed_value_frozen: expectedOk
          && immutabilityProof.rejected_private_mutations === 2,
        recursively_owned_components_frozen: expectedOk
          && immutabilityProof.rejected_private_mutations === 2,
        nested_alias_observed: false, nested_mutation_observed: false},
    };
  });
  const ownerProbes = [
    {...definition.equality_contract.equal_probe, relation: "equal-tuple" as const,
      varied_component_name: null},
    ...definition.equality_contract.component_variants.map((item) => ({
      probe_id: item.probe_id, left_case_id: item.left_case_id,
      right_case_id: item.right_case_id, relation: "component-variant" as const,
      varied_component_name: item.component_name,
    })),
  ];
  const nativeProbes = runtime.probes as readonly JsonObject[];
  if (nativeProbes.length !== ownerProbes.length) {
    return fail("RUST_VALUE_OBJECT_NATIVE_PROBES_INVALID");
  }
  const equalityProbes = ownerProbes.map((owner, index) => {
    const observed = nativeProbes[index]!;
    const expectedEqual = owner.relation === "equal-tuple";
    if (observed.probe_id !== owner.probe_id
        || observed.left_case_id !== owner.left_case_id
        || observed.right_case_id !== owner.right_case_id
        || observed.relation !== owner.relation
        || observed.varied_component_name !== owner.varied_component_name
        || observed.references_distinct !== true
        || observed.observed_equal !== expectedEqual
        || typeof observed.left_hash !== "string"
        || !/^[0-9]+$/u.test(observed.left_hash)
        || typeof observed.right_hash !== "string"
        || !/^[0-9]+$/u.test(observed.right_hash)
        || (expectedEqual && observed.left_hash !== observed.right_hash)) {
      return fail("RUST_VALUE_OBJECT_NATIVE_PROBES_INVALID", owner.probe_id);
    }
    return {...owner, references_distinct: true,
      observed_equal: expectedEqual,
      left_hash_sha256: sha256(observed.left_hash),
      right_hash_sha256: sha256(observed.right_hash)};
  });
  const nested = runtime.nested as JsonObject;
  const nestedComponent = definition.components.find(
    ({nested_value_object: nestedValue}) => nestedValue);
  if (!nestedComponent || nested.component_name !== nestedComponent.component_name
      || nested.protocol_id !== rustProtocol(nestedComponent.protocol_id)
      || nested.protocol_sha256 !== nestedComponent.protocol_sha256
      || nested.equal_observed !== true || nested.equal_hash_congruent !== true
      || nested.variant_unequal_observed !== true) {
    return fail("RUST_VALUE_OBJECT_NATIVE_NESTED_INVALID");
  }
  const factory = runtime.factory as JsonObject;
  const extension = runtime.extension as JsonObject;
  const baseValidators = definition.validators.filter(({origin}) => origin === "base");
  if (factory.base_factory_id !== definition.factories.base.factory_id
      || factory.base_factory_sha256 !== definition.factories.base.factory_sha256
      || factory.extension_factory_id !== definition.factories.extension.factory_id
      || factory.extension_factory_sha256
        !== definition.factories.extension.factory_sha256
      || !same(factory.base_validators, baseValidators)
      || !same(factory.extension_validators, definition.validators)
      || factory.extension_terminal !== true
      || extension.base_inactive_ok !== true
      || extension.extension_inactive_ok !== false
      || !same(extension.failure_codes, ["INACTIVE_SETTLEMENT_ACCOUNT"])
      || !same(extension.validator_trace, definition.validators.map(
        ({validator_id: id, validator_sha256: digest}) => `${id}@${digest}`))
      || extension.preserved_equal !== true || extension.preserved_hash !== true
      || extension.terminal !== true) {
    return fail("RUST_VALUE_OBJECT_NATIVE_EXTENSION_INVALID");
  }
  const staticControls = RUST_VALUE_OBJECT_STATIC_CONTROL_IDS.map((controlId) => {
    const mutated = rustValueObjectStaticControlSource(raw.source, controlId);
    try {
      inspectRustValueObjectClosedSubset(mutated);
      return fail("RUST_VALUE_OBJECT_STATIC_CONTROL_SURVIVED", controlId);
    } catch (error: unknown) {
      if (!isObject(error)
          || error.code !== "RUST_VALUE_OBJECT_CLOSED_SUBSET_SOURCE_MISMATCH") {
        throw error;
      }
      return Object.freeze({control_id: controlId,
        evidence_kind: "rust-static-source-binding-control" as const,
        status: "rejected" as const,
        error_code: error.code});
    }
  });
  const observation = mintConstructionObservationV1({
    schema_version: "ConstructionObservation/v1",
    observation_id: "observation.value-object.rust.settlement-value/v1",
    source_kind: "target-observation",
    observer_ref: observer,
    definition_ref: denominator.owner_definition_ref,
    factory_ref: definition.factories.base,
    attempts,
    equality_probes: equalityProbes,
    nested_delegations: [{component_name: nestedComponent.component_name,
      protocol_id: nestedComponent.protocol_id,
      protocol_sha256: nestedComponent.protocol_sha256,
      equality_delegated: true, hash_delegated: true}],
    extension: {base_factory_ref: definition.factories.base,
      extension_factory_ref: definition.factories.extension,
      added_validators: definition.validators.filter(({origin}) =>
        origin === "extension"), altered_facets: [], cycle_detected: false},
    claim: "transport-observation-only-no-native-runtime-claim",
    collision_freedom_claim: false,
    authority_effect: "none",
  });
  const family = evaluateCompleteValue({definition, denominator, observation,
    locked_observer_ref: observer});
  if (family.verdict !== "pass") {
    return fail("RUST_VALUE_OBJECT_FAMILY_BLOCKED",
      family.findings.map(({code}) => code).join(","));
  }
  const familyControls = catalogue.mutations.map((mutation) => {
    const result = evaluateCompleteValue({definition, denominator,
      observation: applyCompleteValueMutant(observation, mutation),
      locked_observer_ref: observer});
    const codes = new Set(result.findings.map(({code}) => code));
    if (result.verdict !== "fail"
        || !mutation.expected_finding_codes.every((code) =>
          codes.has(code as CompleteValueFindingCode))) {
      return fail("RUST_VALUE_OBJECT_FAMILY_CONTROL_SURVIVED",
        mutation.mutation_id);
    }
    return Object.freeze({mutation_id: mutation.mutation_id,
      status: "killed" as const});
  });
  return Object.freeze({
    schema_version: "RustValueObjectProof/v1" as const,
    result: "pass" as const,
    target: Object.freeze({target_id: binding.target_id,
      target_sha256: binding.source_ref.sha256, language: "rust" as const,
      protocol_id: binding.protocol_id}),
    binding: Object.freeze({binding_id: binding.binding_id,
      binding_sha256: binding.binding_sha256}),
    source_proof: sourceProof,
    immutability_proof: immutabilityProof,
    native_runtime_observation: runtime,
    portable_protocol_projection: Object.freeze({
      from_prefix: "rust.eq-hash-value-component",
      to_owner_family_prefix: "typescript.owned-value-component",
      mapping_basis: "exact-component-name-and-protocol-digest",
    }),
    observation,
    family_evaluation: family,
    process_evidence: Object.freeze({executions: 2, distinct_pids: 2,
      pids_redacted_from_semantic_proof: true, semantic_replay_equal: true,
      semantic_replay_sha256: sha256(
        canonicalConstructionObservationJson(runtime)),
      input_materialization: "compiled-owner-cases" as const}),
    toolchain: Object.freeze({rustc_version: binding.rustc_version,
      rustc_launcher_path: binding.rustc_launcher_path,
      rustc_launcher_sha256: binding.rustc_launcher_sha256}),
    accounting: Object.freeze({positives: Object.freeze({declared: 7, passed: 7}),
      static_binding_controls: Object.freeze({declared: staticControls.length,
        rejected: staticControls.length}),
      predecessor_family_controls: Object.freeze({declared: familyControls.length,
        killed: familyControls.length})}),
    static_binding_controls: Object.freeze(staticControls),
    predecessor_family_controls: Object.freeze(familyControls),
    claim_ceiling: "one exact hash-locked candidate-local Rust Settlement Value Object over compiled owner cases, exact-source admission, one compiled runner and two fresh processes, complete tuple Eq plus Hash, recursively owned private nested value, exact component protocols and validators, structured no-object failures, and one-way additive validation-only extension; no arbitrary Rust or macros, OS interception, business correctness beyond the owner fixture, collision freedom, cross-language hash bytes, parity, registration, promotion, publication, deployment, or production claim",
    authority_effect: "none" as const,
  });
};
