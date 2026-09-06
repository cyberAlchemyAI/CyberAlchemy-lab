import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import {
  existsSync,
  lstatSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { resolve } from "node:path";

const OWNER_PATH =
  "projects/domainspec-v2/development/remaining-meta-types/admissions/enum/owner-member-wire-catalogue.json";
const DENOMINATOR_PATH =
  "projects/domainspec-v2/impl/architecture-conformance/families/finite-vocabulary/fixtures/shipment-priority/denominator.json";
const BINDING_PATH =
  "projects/domainspec-v2/impl/architecture-conformance/realizations/enum/rust/unit-variant-enum-v1/rust-binding.json";
const EXPECTED_ERROR_CODE = "DOMAINSPEC_ENUM_UNKNOWN_WIRE";

type JsonObject = Record<string, unknown>;

type OwnerMember = Readonly<{
  member_id: string;
  member_key: string;
  wire_value: string;
}>;

type CommandResult = Readonly<{
  status: number | null;
  stdout: string;
  stderr: string;
  error: string | null;
}>;

export class RustEnumProofError extends Error {
  readonly code: string;

  constructor(code: string, detail?: string) {
    super(detail === undefined ? code : `${code}:${detail}`);
    this.name = "RustEnumProofError";
    this.code = code;
  }
}

const fail = (code: string, detail?: string): never => {
  throw new RustEnumProofError(code, detail);
};

const isObject = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);

const asObject = (value: unknown, code: string): JsonObject =>
  isObject(value) ? value : fail(code);

const asString = (value: unknown, code: string): string =>
  typeof value === "string" && value.length > 0 ? value : fail(code);

const canonicalize = (value: unknown): unknown => Array.isArray(value)
  ? value.map(canonicalize)
  : isObject(value)
    ? Object.fromEntries(Object.entries(value)
      .sort(([left], [right]) => Buffer.from(left).compare(Buffer.from(right)))
      .map(([key, child]) => [key, canonicalize(child)]))
    : value;

const canonicalJson = (value: unknown): string => JSON.stringify(canonicalize(value));

const sha256 = (value: string | Buffer): string =>
  createHash("sha256").update(value).digest("hex");

const documentDigest = (value: JsonObject, field: string): string => sha256(
  canonicalJson(Object.fromEntries(Object.entries(value)
    .filter(([key]) => key !== field))),
);

const readRegularBytes = (root: string, relative: string): Buffer => {
  const path = resolve(root, relative);
  if (!existsSync(path)) return fail("RUST_ENUM_INPUT_MISSING", relative);
  const stat = lstatSync(path);
  if (!stat.isFile() || stat.isSymbolicLink()) {
    return fail("RUST_ENUM_INPUT_NOT_REGULAR", relative);
  }
  return readFileSync(path);
};

const parseJsonObject = (bytes: Buffer, code: string): JsonObject => {
  try {
    return asObject(JSON.parse(bytes.toString("utf8")), code);
  } catch (error) {
    if (error instanceof RustEnumProofError) throw error;
    return fail(code);
  }
};

const expectRef = (value: unknown, code: string): Readonly<{
  path: string;
  sha256: string;
}> => {
  const source = asObject(value, code);
  if (Object.keys(source).sort().join(",") !== "path,sha256") return fail(code);
  const path = asString(source.path, code);
  const digest = asString(source.sha256, code);
  if (!/^[a-f0-9]{64}$/u.test(digest)) return fail(code);
  return Object.freeze({ path, sha256: digest });
};

const ownerMembers = (owner: JsonObject): readonly OwnerMember[] => {
  if (owner.authorship !== "owner-authored-admission-input"
      || owner.derivation_policy
        !== "runtime-and-generated-members-forbidden-as-authority"
      || !Array.isArray(owner.members)
      || owner.members.length === 0) {
    return fail("RUST_ENUM_OWNER_CATALOGUE_POLICY_INVALID");
  }
  const members = owner.members.map((value): OwnerMember => {
    const source = asObject(value, "RUST_ENUM_OWNER_MEMBER_INVALID");
    const member = Object.freeze({
      member_id: asString(source.member_id, "RUST_ENUM_OWNER_MEMBER_INVALID"),
      member_key: asString(source.member_key, "RUST_ENUM_OWNER_MEMBER_INVALID"),
      wire_value: asString(source.wire_value, "RUST_ENUM_OWNER_MEMBER_INVALID"),
    });
    if (!/^[A-Z][A-Za-z0-9_]*$/u.test(member.member_key)
        || !/^[A-Za-z0-9._:/-]+$/u.test(member.member_id)
        || !/^[A-Za-z0-9._:/-]+$/u.test(member.wire_value)) {
      return fail("RUST_ENUM_OWNER_MEMBER_UNSAFE_FOR_NATIVE_PROBE");
    }
    return member;
  });
  for (const values of [
    members.map(({ member_id: value }) => value),
    members.map(({ member_key: value }) => value),
    members.map(({ wire_value: value }) => value),
  ]) {
    if (new Set(values).size !== values.length) {
      return fail("RUST_ENUM_OWNER_MEMBER_DUPLICATE");
    }
  }
  return Object.freeze(members);
};

const extractBlock = (source: string, marker: string): string => {
  const markerAt = source.indexOf(marker);
  if (markerAt < 0) return fail("RUST_ENUM_SOURCE_SHAPE_INVALID", marker);
  const blockAt = source.indexOf("{", markerAt + marker.length);
  if (blockAt < 0) return fail("RUST_ENUM_SOURCE_SHAPE_INVALID", marker);
  let depth = 0;
  for (let index = blockAt; index < source.length; index += 1) {
    if (source[index] === "{") depth += 1;
    if (source[index] === "}") {
      depth -= 1;
      if (depth === 0) return source.slice(blockAt + 1, index);
    }
  }
  return fail("RUST_ENUM_SOURCE_SHAPE_INVALID", marker);
};

const escapeRegExp = (value: string): string =>
  value.replace(/[.*+?^${}()|[\]\\]/gu, "\\$&");

const inspectTargetSource = (
  source: string,
  members: readonly OwnerMember[],
  symbols: Readonly<{ emit: string; memberId: string; parse: string }>,
): void => {
  const enumBody = extractBlock(source, "pub enum ShipmentPriority");
  const variants = enumBody.split(",").map((value) => value.trim()).filter(Boolean);
  if (variants.join(",") !== members.map(({ member_key: value }) => value).join(",")) {
    return fail("RUST_ENUM_UNIT_VARIANT_SET_INVALID");
  }

  const emitBody = extractBlock(source, `pub fn ${symbols.emit}`);
  const memberIdBody = extractBlock(source, `pub fn ${symbols.memberId}`);
  const parseBody = extractBlock(source, `pub fn ${symbols.parse}`);
  for (const body of [emitBody, memberIdBody]) {
    if (/_\s*=>/u.test(body)) return fail("RUST_ENUM_MEMBER_MATCH_WILDCARD_FORBIDDEN");
  }
  for (const member of members) {
    const variant = `ShipmentPriority::${member.member_key}`;
    const emitPattern = new RegExp(
      `${escapeRegExp(variant)}\\s*=>\\s*${escapeRegExp(JSON.stringify(member.wire_value))}`,
      "u",
    );
    const idPattern = new RegExp(
      `${escapeRegExp(variant)}\\s*=>\\s*${escapeRegExp(JSON.stringify(member.member_id))}`,
      "u",
    );
    const parsePattern = new RegExp(
      `${escapeRegExp(JSON.stringify(member.wire_value))}\\s*=>\\s*Ok\\(${escapeRegExp(variant)}\\)`,
      "u",
    );
    if (!emitPattern.test(emitBody)
        || !idPattern.test(memberIdBody)
        || !parsePattern.test(parseBody)) {
      return fail("RUST_ENUM_EXPLICIT_MAPPING_INVALID", member.member_key);
    }
  }
  if (!/unknown\s*=>\s*Err\s*\(/u.test(parseBody)) {
    return fail("RUST_ENUM_FALLIBLE_PARSE_INVALID");
  }
};

const invoke = (executable: string, args: readonly string[]): CommandResult => {
  const result = spawnSync(executable, args, {
    encoding: "utf8",
    env: { PATH: process.env.PATH ?? "" },
    maxBuffer: 1_048_576,
  });
  return Object.freeze({
    status: result.status,
    stdout: result.stdout ?? "",
    stderr: result.stderr ?? "",
    error: result.error?.message ?? null,
  });
};

const rustString = (value: string): string => JSON.stringify(value);

const positiveHarness = (
  sourcePath: string,
  members: readonly OwnerMember[],
  unknownWire: string,
): string => {
  const matchArms = members.map(({ member_key: key }) =>
    `        ShipmentPriority::${key} => ${rustString(key)},`).join("\n");
  const observations = members.map((member) => `
    {
        let value = ShipmentPriority::${member.member_key};
        let emitted = emit_shipment_priority(value);
        let parsed = parse_shipment_priority(emitted).expect("known wire must parse");
        println!("MEMBER\\t{}\\t{}\\t{}\\t{}", ${rustString(member.member_id)}, exact_native_key(value), emitted, shipment_priority_member_id(parsed));
    }`).join("\n");
  return `#[path = ${rustString(sourcePath)}]
mod enum_v1;

use enum_v1::{
    emit_shipment_priority,
    parse_shipment_priority,
    shipment_priority_member_id,
    ShipmentPriority,
};
use std::fmt::Debug;
use std::hash::Hash;

fn assert_traits<T: Debug + Copy + Clone + PartialEq + Eq + Hash>() {}

fn exact_native_key(value: ShipmentPriority) -> &'static str {
    match value {
${matchArms}
    }
}

fn main() {
    assert_traits::<ShipmentPriority>();
${observations}
    match parse_shipment_priority(${rustString(unknownWire)}) {
        Ok(value) => println!("UNKNOWN\\tmember\\t{}\\t\\t", shipment_priority_member_id(value)),
        Err(error) => println!("UNKNOWN\\tstructured-failure\\t{}\\t{}\\t{}", error.code, error.enum_id, error.wire_value),
    }
}
`;
};

const negativeHarnesses = (
  sourcePath: string,
  members: readonly OwnerMember[],
): Readonly<Record<string, string>> => {
  const pathLine = `#[path = ${rustString(sourcePath)}]\nmod enum_v1;`;
  const first = members[0]?.member_key
    ?? fail("RUST_ENUM_OWNER_CATALOGUE_MEMBERS_INVALID");
  return Object.freeze({
    non_exhaustive_match_rejected: `${pathLine}
use enum_v1::ShipmentPriority;
fn inspect(value: ShipmentPriority) {
    match value {
        ShipmentPriority::${first} => (),
    }
}
fn main() {}
`,
    payload_constructor_rejected: `${pathLine}
use enum_v1::ShipmentPriority;
fn main() {
    let _value = ShipmentPriority::${first}("payload");
}
`,
    wrong_type_emit_rejected: `${pathLine}
use enum_v1::emit_shipment_priority;
fn main() {
    let _wire = emit_shipment_priority("deferred");
}
`,
  });
};

const diagnosticCodes = (stderr: string): readonly string[] => Object.freeze(
  [...new Set(stderr.split("\n").flatMap((line): string[] => {
    if (line.trim().length === 0) return [];
    try {
      const value = JSON.parse(line) as unknown;
      if (!isObject(value) || !isObject(value.code) || typeof value.code.code !== "string") {
        return [];
      }
      return [value.code.code];
    } catch {
      return [];
    }
  }))].sort(),
);

const compileNegativeProbe = (input: Readonly<{
  rustc: string;
  workspace: string;
  probeId: string;
  source: string;
  expectedCode: string;
}>): Readonly<{
  probe_id: string;
  expected_code: string;
  observed_codes: readonly string[];
  rejected: boolean;
}> => {
  const path = resolve(input.workspace, `${input.probeId}.rs`);
  writeFileSync(path, input.source, { encoding: "utf8", flag: "wx" });
  const result = invoke(input.rustc, [
    "--edition", "2021",
    "--crate-name", input.probeId,
    "--emit", "metadata",
    "--error-format", "json",
    "--out-dir", input.workspace,
    path,
  ]);
  const observedCodes = diagnosticCodes(result.stderr);
  return Object.freeze({
    probe_id: input.probeId,
    expected_code: input.expectedCode,
    observed_codes: observedCodes,
    rejected: result.status !== 0 && observedCodes.includes(input.expectedCode),
  });
};

const parseMemberObservation = (line: string): Readonly<{
  member_id: string;
  native_keys: readonly string[];
  emitted_wire: string;
  parsed_member_id: string;
}> => {
  const fields = line.split("\t");
  if (fields.length !== 5 || fields[0] !== "MEMBER") {
    return fail("RUST_ENUM_NATIVE_MEMBER_OUTPUT_INVALID");
  }
  return Object.freeze({
    member_id: fields[1] ?? fail("RUST_ENUM_NATIVE_MEMBER_OUTPUT_INVALID"),
    native_keys: Object.freeze([
      fields[2] ?? fail("RUST_ENUM_NATIVE_MEMBER_OUTPUT_INVALID"),
    ]),
    emitted_wire: fields[3] ?? fail("RUST_ENUM_NATIVE_MEMBER_OUTPUT_INVALID"),
    parsed_member_id: fields[4] ?? fail("RUST_ENUM_NATIVE_MEMBER_OUTPUT_INVALID"),
  });
};

const buildProof = (input: Readonly<{
  repositoryRoot: string;
  rustc: string;
  workspace: string;
}>): JsonObject => {
  const bindingBytes = readRegularBytes(input.repositoryRoot, BINDING_PATH);
  const binding = parseJsonObject(bindingBytes, "RUST_ENUM_BINDING_JSON_INVALID");
  if (binding.schema_version !== "RustEnumBinding/v1"
      || documentDigest(binding, "binding_sha256") !== binding.binding_sha256) {
    return fail("RUST_ENUM_BINDING_STALE");
  }

  const ownerRef = expectRef(binding.owner_catalogue_ref, "RUST_ENUM_OWNER_REF_INVALID");
  if (ownerRef.path !== OWNER_PATH) return fail("RUST_ENUM_OWNER_REF_INVALID");
  const ownerBytes = readRegularBytes(input.repositoryRoot, OWNER_PATH);
  if (sha256(ownerBytes) !== ownerRef.sha256) {
    return fail("RUST_ENUM_OWNER_CATALOGUE_STALE");
  }
  const owner = parseJsonObject(ownerBytes, "RUST_ENUM_OWNER_CATALOGUE_JSON_INVALID");
  const members = ownerMembers(owner);

  const denominatorRef = expectRef(
    binding.denominator_ref,
    "RUST_ENUM_DENOMINATOR_REF_INVALID",
  );
  if (denominatorRef.path !== DENOMINATOR_PATH) {
    return fail("RUST_ENUM_DENOMINATOR_REF_INVALID");
  }
  const denominatorBytes = readRegularBytes(input.repositoryRoot, DENOMINATOR_PATH);
  if (sha256(denominatorBytes) !== denominatorRef.sha256) {
    return fail("RUST_ENUM_DENOMINATOR_INPUT_STALE");
  }
  const denominator = parseJsonObject(
    denominatorBytes,
    "RUST_ENUM_DENOMINATOR_JSON_INVALID",
  );
  const denominatorBody = Object.fromEntries(Object.entries(denominator)
    .filter(([key]) => key !== "denominator_sha256"));
  if (Array.isArray(denominatorBody.positive_decisions)) {
    denominatorBody.positive_decisions = [...denominatorBody.positive_decisions]
      .sort((left, right) => Buffer.from(String(left)).compare(Buffer.from(String(right))));
  }
  if (sha256(canonicalJson(denominatorBody)) !== denominator.denominator_sha256) {
    return fail("RUST_ENUM_DENOMINATOR_DIGEST_STALE");
  }
  const denominatorOwner = asObject(
    denominator.owner_catalogue_ref,
    "RUST_ENUM_DENOMINATOR_OWNER_REF_INVALID",
  );
  if (denominatorOwner.path !== OWNER_PATH
      || denominatorOwner.sha256 !== ownerRef.sha256
      || denominatorOwner.catalogue_id !== owner.catalogue_id) {
    return fail("RUST_ENUM_DENOMINATOR_OWNER_REF_STALE");
  }

  const sourceRef = expectRef(binding.source_ref, "RUST_ENUM_SOURCE_REF_INVALID");
  const sourceBytes = readRegularBytes(input.repositoryRoot, sourceRef.path);
  if (sha256(sourceBytes) !== sourceRef.sha256) return fail("RUST_ENUM_SOURCE_STALE");
  const source = sourceBytes.toString("utf8");
  const emitSymbol = asString(binding.emit_symbol, "RUST_ENUM_BINDING_SYMBOL_INVALID");
  const parseSymbol = asString(binding.parse_symbol, "RUST_ENUM_BINDING_SYMBOL_INVALID");
  const memberIdSymbol = asString(
    binding.member_id_symbol,
    "RUST_ENUM_BINDING_SYMBOL_INVALID",
  );
  inspectTargetSource(source, members, {
    emit: emitSymbol,
    parse: parseSymbol,
    memberId: memberIdSymbol,
  });

  const unknownWire = asString(binding.unknown_wire_probe, "RUST_ENUM_UNKNOWN_PROBE_INVALID");
  if (!/^[A-Za-z0-9._:/-]+$/u.test(unknownWire)
      || members.some(({ wire_value: value }) => value === unknownWire)) {
    return fail("RUST_ENUM_UNKNOWN_PROBE_INVALID");
  }
  const sourcePath = resolve(input.repositoryRoot, sourceRef.path);
  const harnessPath = resolve(input.workspace, "positive.rs");
  const binaryPath = resolve(input.workspace, "positive-proof");
  writeFileSync(harnessPath, positiveHarness(sourcePath, members, unknownWire), {
    encoding: "utf8",
    flag: "wx",
  });
  const compile = invoke(input.rustc, [
    "--edition", "2021",
    "--crate-name", "rust_enum_positive_proof",
    "--error-format", "json",
    harnessPath,
    "-o", binaryPath,
  ]);
  if (compile.status !== 0) {
    return fail("RUST_ENUM_POSITIVE_COMPILE_FAILED", diagnosticCodes(compile.stderr).join(","));
  }
  const runtime = invoke(binaryPath, []);
  if (runtime.status !== 0 || runtime.error !== null) {
    return fail("RUST_ENUM_POSITIVE_RUNTIME_FAILED", runtime.error ?? String(runtime.status));
  }
  const lines = runtime.stdout.trim().split("\n").filter(Boolean);
  const memberLines = lines.filter((line) => line.startsWith("MEMBER\t"));
  const unknownLine = lines.find((line) => line.startsWith("UNKNOWN\t"));
  if (memberLines.length !== members.length || unknownLine === undefined) {
    return fail("RUST_ENUM_NATIVE_OUTPUT_INCOMPLETE");
  }
  const observedMembers = memberLines.map(parseMemberObservation)
    .sort((left, right) => left.member_id.localeCompare(right.member_id));
  const unknownFields = unknownLine.split("\t");
  if (unknownFields.length !== 5) return fail("RUST_ENUM_UNKNOWN_OUTPUT_INVALID");
  const structuredFailure = Object.freeze({
    code: unknownFields[2] ?? "",
    enum_id: unknownFields[3] ?? "",
    wire_value: unknownFields[4] ?? "",
  });

  const compilerProbes = asObject(
    binding.compiler_probes,
    "RUST_ENUM_COMPILER_PROBES_INVALID",
  );
  const harnesses = negativeHarnesses(sourcePath, members);
  const diagnosticProbes = Object.freeze(Object.fromEntries(
    Object.entries(harnesses).map(([probeId, probeSource]) => {
      const expectedCode = asString(
        compilerProbes[probeId],
        "RUST_ENUM_COMPILER_PROBES_INVALID",
      );
      return [probeId, compileNegativeProbe({
        rustc: input.rustc,
        workspace: input.workspace,
        probeId,
        source: probeSource,
        expectedCode,
      })];
    }),
  ));

  const expectedById = new Map(members.map((member) => [member.member_id, member]));
  const nativeProperties = Object.freeze({
    exact_unit_variant_set: compile.status === 0,
    required_traits_satisfied: compile.status === 0,
    explicit_total_member_mappings: true,
    known_emit_parse_total: observedMembers.length === members.length
      && observedMembers.every((observed) => {
        const expected = expectedById.get(observed.member_id);
        return expected !== undefined
          && observed.native_keys.length === 1
          && observed.native_keys[0] === expected.member_key
          && observed.emitted_wire === expected.wire_value
          && observed.parsed_member_id === expected.member_id;
      }),
  });
  const hostileProbes = Object.freeze({
    non_exhaustive_match_rejected:
      diagnosticProbes.non_exhaustive_match_rejected?.rejected === true,
    payload_constructor_rejected:
      diagnosticProbes.payload_constructor_rejected?.rejected === true,
    wrong_type_emit_rejected:
      diagnosticProbes.wrong_type_emit_rejected?.rejected === true,
    unknown_wire_structured_failure:
      unknownFields[1] === "structured-failure"
      && structuredFailure.code === EXPECTED_ERROR_CODE
      && structuredFailure.enum_id === owner.concept_id
      && structuredFailure.wire_value === unknownWire,
  });
  const result = Object.values(nativeProperties).every(Boolean)
    && Object.values(hostileProbes).every(Boolean) ? "pass" : "block";
  const rustcVersion = invoke(input.rustc, ["--version"]);
  if (rustcVersion.status !== 0) return fail("RUST_ENUM_COMPILER_VERSION_UNAVAILABLE");

  return {
    schema_version: "RustEnumNativeProof/v1",
    result,
    target: {
      target_id: "rust.shipment-priority.unit-variant-enum-v1",
      language: "rust",
      protocol_id: "rust.nominal-enum-explicit-wire/v1",
    },
    owner_catalogue_ref: {
      catalogue_id: owner.catalogue_id,
      path: OWNER_PATH,
      sha256: ownerRef.sha256,
    },
    denominator_ref: {
      denominator_id: denominator.denominator_id,
      path: DENOMINATOR_PATH,
      sha256: denominatorRef.sha256,
      denominator_sha256: denominator.denominator_sha256,
    },
    source_ref: sourceRef,
    catalogue_origin: "owner-authored-admission-input",
    member_order_semantics: "none",
    members: observedMembers,
    unknown_wire: {
      wire_value: unknownWire,
      outcome: hostileProbes.unknown_wire_structured_failure
        ? "structured-failure" : "member",
      error_code: hostileProbes.unknown_wire_structured_failure
        ? structuredFailure.code : null,
      parsed_member_id: null,
    },
    native_identity_diagnostic: {
      relation: "nominal",
      claim_scope: "native-diagnostic-only",
    },
    native_properties: nativeProperties,
    native_property_evidence: {
      exact_unit_variant_set: "owner-derived-source-inspection-and-exhaustive-compile",
      required_traits_satisfied: "compile-bound-trait-assertion",
      explicit_total_member_mappings: "owner-derived-source-inspection-and-native-runtime",
      known_emit_parse_total: "native-runtime-observation",
    },
    hostile_probes: hostileProbes,
    structured_failure: structuredFailure,
    compiler: {
      rustc_version: rustcVersion.stdout.trim(),
      diagnostic_format: "rustc-json",
      probes: diagnosticProbes,
    },
    authority_effect: "none",
  };
};

export const runRustEnumNativeProof = (input: Readonly<{
  repositoryRoot: string;
  output: string;
  rustc: string;
}>): JsonObject => {
  const workspace = mkdtempSync(resolve(tmpdir(), "domainspec-rust-enum-native-"));
  let proof: JsonObject;
  try {
    proof = buildProof({ ...input, workspace });
  } finally {
    rmSync(workspace, { recursive: true, force: true });
  }
  if (existsSync(workspace)) return fail("RUST_ENUM_NATIVE_WORKSPACE_NOT_CLEANED");
  proof.native_workspace = Object.freeze({ isolated: true, cleaned: true, symlinks: false });
  writeFileSync(input.output, `${JSON.stringify(proof, null, 2)}\n`, {
    encoding: "utf8",
    flag: "wx",
  });
  if (proof.result !== "pass") return fail("RUST_ENUM_NATIVE_PROOF_BLOCKED");
  return Object.freeze(proof);
};
