import { createHash } from "node:crypto";

import {
  decodeFiniteVocabularyDenominatorV1,
  evaluateFiniteVocabulary,
  mintFiniteVocabularyObservationV1,
  type FiniteVocabularyEvaluationV1,
  type FiniteVocabularyObservationV1,
} from "../../../../families/finite-vocabulary/index.js";

export const RUST_ENUM_OWNER_PATH =
  "projects/domainspec-v2/development/remaining-meta-types/admissions/enum/owner-member-wire-catalogue.json";

const NATIVE_PROPERTY_IDS = Object.freeze([
  "exact_unit_variant_set",
  "required_traits_satisfied",
  "explicit_total_member_mappings",
  "known_emit_parse_total",
] as const);

const HOSTILE_PROBE_IDS = Object.freeze([
  "non_exhaustive_match_rejected",
  "payload_constructor_rejected",
  "wrong_type_emit_rejected",
  "unknown_wire_structured_failure",
] as const);

const COMPILER_PROBE_CODES = Object.freeze({
  non_exhaustive_match_rejected: "E0004",
  payload_constructor_rejected: "E0618",
  wrong_type_emit_rejected: "E0308",
} as const);

const PROPERTY_EVIDENCE = Object.freeze({
  exact_unit_variant_set: "owner-derived-source-inspection-and-exhaustive-compile",
  required_traits_satisfied: "compile-bound-trait-assertion",
  explicit_total_member_mappings: "owner-derived-source-inspection-and-native-runtime",
  known_emit_parse_total: "native-runtime-observation",
} as const);

type NativePropertyId = (typeof NATIVE_PROPERTY_IDS)[number];
type HostileProbeId = (typeof HOSTILE_PROBE_IDS)[number];
type CompilerProbeId = keyof typeof COMPILER_PROBE_CODES;

type NativeMember = Readonly<{
  member_id: string;
  native_keys: readonly string[];
  emitted_wire: string;
  parsed_member_id: string;
}>;

type CompilerProbe = Readonly<{
  probe_id: string;
  expected_code: string;
  observed_codes: readonly string[];
  rejected: boolean;
}>;

export type RustEnumNativeProofV1 = Readonly<{
  schema_version: "RustEnumNativeProof/v1";
  result: "pass" | "block";
  target: Readonly<{
    target_id: "rust.shipment-priority.unit-variant-enum-v1";
    language: "rust";
    protocol_id: "rust.nominal-enum-explicit-wire/v1";
  }>;
  owner_catalogue_ref: Readonly<{
    catalogue_id: string;
    path: string;
    sha256: string;
  }>;
  denominator_ref: Readonly<{
    denominator_id: string;
    path: string;
    sha256: string;
    denominator_sha256: string;
  }>;
  source_ref: Readonly<{ path: string; sha256: string }>;
  catalogue_origin: "owner-authored-admission-input";
  member_order_semantics: "none";
  members: readonly NativeMember[];
  unknown_wire: FiniteVocabularyObservationV1["unknown_wire"];
  native_identity_diagnostic: Readonly<{
    relation: "nominal";
    claim_scope: "native-diagnostic-only";
  }>;
  native_properties: Readonly<Record<NativePropertyId, boolean>>;
  native_property_evidence: typeof PROPERTY_EVIDENCE;
  hostile_probes: Readonly<Record<HostileProbeId, boolean>>;
  structured_failure: Readonly<{
    code: "DOMAINSPEC_ENUM_UNKNOWN_WIRE";
    enum_id: string;
    wire_value: string;
  }>;
  compiler: Readonly<{
    rustc_version: string;
    diagnostic_format: "rustc-json";
    probes: Readonly<Record<CompilerProbeId, CompilerProbe>>;
  }>;
  native_workspace: Readonly<{
    isolated: true;
    cleaned: true;
    symlinks: false;
  }>;
  authority_effect: "none";
}>;

export type RustEnumComposedProofV1 = Readonly<{
  schema_version: "RustEnumComposedProof/v1";
  result: "pass";
  observation: FiniteVocabularyObservationV1;
  family_evaluation: FiniteVocabularyEvaluationV1;
  native_proof: RustEnumNativeProofV1;
  accounting: Readonly<{
    portable_decisions: Readonly<{ declared: number; passed: number }>;
    native_properties: Readonly<{ declared: number; passed: number }>;
    hostile_probes: Readonly<{ declared: number; killed: number }>;
  }>;
  claim_ceiling: string;
  authority_effect: "none";
}>;

export class RustEnumCompositionError extends Error {
  readonly code: string;

  constructor(code: string, detail?: string) {
    super(detail === undefined ? code : `${code}:${detail}`);
    this.name = "RustEnumCompositionError";
    this.code = code;
  }
}

const fail = (code: string, detail?: string): never => {
  throw new RustEnumCompositionError(code, detail);
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  value !== null && typeof value === "object" && !Array.isArray(value);

const sameKeys = (value: Record<string, unknown>, expected: readonly string[]): boolean => {
  const actual = Object.keys(value).sort();
  const wanted = [...expected].sort();
  return actual.length === wanted.length
    && actual.every((key, index) => key === wanted[index]);
};

const sha256 = (bytes: string): string =>
  createHash("sha256").update(bytes, "utf8").digest("hex");

const decodeCompilerProbes = (value: unknown): boolean => {
  if (!isRecord(value) || !sameKeys(value, Object.keys(COMPILER_PROBE_CODES))) {
    return false;
  }
  return Object.entries(COMPILER_PROBE_CODES).every(([probeId, expectedCode]) => {
    const probe = value[probeId];
    return isRecord(probe)
      && probe.probe_id === probeId
      && probe.expected_code === expectedCode
      && probe.rejected === true
      && Array.isArray(probe.observed_codes)
      && probe.observed_codes.includes(expectedCode);
  });
};

const decodeNativeProof = (value: unknown): RustEnumNativeProofV1 => {
  if (!isRecord(value)
      || value.schema_version !== "RustEnumNativeProof/v1"
      || value.result !== "pass"
      || value.catalogue_origin !== "owner-authored-admission-input"
      || value.member_order_semantics !== "none"
      || value.authority_effect !== "none"
      || !isRecord(value.target)
      || value.target.target_id !== "rust.shipment-priority.unit-variant-enum-v1"
      || value.target.language !== "rust"
      || value.target.protocol_id !== "rust.nominal-enum-explicit-wire/v1"
      || !isRecord(value.native_identity_diagnostic)
      || value.native_identity_diagnostic.relation !== "nominal"
      || value.native_identity_diagnostic.claim_scope !== "native-diagnostic-only"
      || !isRecord(value.native_properties)
      || !isRecord(value.native_property_evidence)
      || !isRecord(value.hostile_probes)
      || !Array.isArray(value.members)
      || !isRecord(value.owner_catalogue_ref)
      || !isRecord(value.denominator_ref)
      || !isRecord(value.source_ref)
      || !isRecord(value.unknown_wire)
      || !isRecord(value.structured_failure)
      || !isRecord(value.compiler)
      || value.compiler.diagnostic_format !== "rustc-json"
      || typeof value.compiler.rustc_version !== "string"
      || value.compiler.rustc_version.length === 0
      || !decodeCompilerProbes(value.compiler.probes)
      || !isRecord(value.native_workspace)
      || value.native_workspace.isolated !== true
      || value.native_workspace.cleaned !== true
      || value.native_workspace.symlinks !== false) {
    return fail("RUST_ENUM_NATIVE_PROOF_INVALID");
  }
  const nativeProperties = value.native_properties as Record<string, unknown>;
  const nativePropertyEvidence = value.native_property_evidence as Record<string, unknown>;
  const hostileProbes = value.hostile_probes as Record<string, unknown>;
  if (!sameKeys(nativeProperties, NATIVE_PROPERTY_IDS)
      || !sameKeys(nativePropertyEvidence, NATIVE_PROPERTY_IDS)
      || !sameKeys(hostileProbes, HOSTILE_PROBE_IDS)
      || NATIVE_PROPERTY_IDS.some((id) => nativeProperties[id] !== true)
      || NATIVE_PROPERTY_IDS.some(
        (id) => nativePropertyEvidence[id] !== PROPERTY_EVIDENCE[id],
      )
      || HOSTILE_PROBE_IDS.some((id) => hostileProbes[id] !== true)) {
    return fail("RUST_ENUM_NATIVE_PROOF_BLOCKED");
  }
  return value as RustEnumNativeProofV1;
};

export const composeRustEnumFamilyProof = (input: Readonly<{
  owner_catalogue_bytes: string;
  denominator_bytes: string;
  native_proof: unknown;
}>): RustEnumComposedProofV1 => {
  const nativeProof = decodeNativeProof(input.native_proof);
  const { denominator, owner_catalogue: ownerCatalogue } =
    decodeFiniteVocabularyDenominatorV1(
      input.denominator_bytes,
      input.owner_catalogue_bytes,
      RUST_ENUM_OWNER_PATH,
    );
  if (nativeProof.owner_catalogue_ref.catalogue_id !== ownerCatalogue.catalogue_id
      || nativeProof.owner_catalogue_ref.path !== denominator.owner_catalogue_ref.path
      || nativeProof.owner_catalogue_ref.sha256 !== denominator.owner_catalogue_ref.sha256
      || nativeProof.owner_catalogue_ref.sha256 !== sha256(input.owner_catalogue_bytes)
      || nativeProof.denominator_ref.denominator_id !== denominator.denominator_id
      || nativeProof.denominator_ref.denominator_sha256
        !== denominator.denominator_sha256
      || nativeProof.denominator_ref.sha256 !== sha256(input.denominator_bytes)) {
    return fail("RUST_ENUM_NATIVE_OWNER_BINDING_STALE");
  }

  const observation = mintFiniteVocabularyObservationV1({
    schema_version: "FiniteVocabularyObservation/v1",
    observation_id: "rust.shipment-priority.unit-variant-enum-v1",
    source_kind: "independent-owner-bound-positive",
    target: nativeProof.target,
    owner_catalogue_ref: nativeProof.owner_catalogue_ref,
    catalogue_origin: nativeProof.catalogue_origin,
    member_order_semantics: nativeProof.member_order_semantics,
    members: nativeProof.members,
    unknown_wire: nativeProof.unknown_wire,
    native_identity_diagnostic: nativeProof.native_identity_diagnostic,
    authority_effect: "none",
  });
  const familyEvaluation = evaluateFiniteVocabulary({
    denominator,
    owner_catalogue: ownerCatalogue,
    observation,
  });
  if (familyEvaluation.verdict !== "pass") {
    return fail(
      "RUST_ENUM_FAMILY_EVALUATION_BLOCKED",
      familyEvaluation.findings.map(({ code }) => code).join(","),
    );
  }
  const nativePassed = NATIVE_PROPERTY_IDS.filter(
    (id) => nativeProof.native_properties[id],
  ).length;
  const hostilesKilled = HOSTILE_PROBE_IDS.filter(
    (id) => nativeProof.hostile_probes[id],
  ).length;
  return Object.freeze({
    schema_version: "RustEnumComposedProof/v1" as const,
    result: "pass" as const,
    observation,
    family_evaluation: familyEvaluation,
    native_proof: nativeProof,
    accounting: Object.freeze({
      portable_decisions: Object.freeze({
        declared: familyEvaluation.positive_decision_accounting.declared,
        passed: familyEvaluation.positive_decision_accounting.passed,
      }),
      native_properties: Object.freeze({
        declared: NATIVE_PROPERTY_IDS.length,
        passed: nativePassed,
      }),
      hostile_probes: Object.freeze({
        declared: HOSTILE_PROBE_IDS.length,
        killed: hostilesKilled,
      }),
    }),
    claim_ceiling: "one candidate-local Rust unit-variant Enum composed with the owner-bound finite-vocabulary family; compiler diagnostics and nominal identity remain Rust-native evidence",
    authority_effect: "none" as const,
  });
};
