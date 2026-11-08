import {
  decodeFiniteVocabularyDenominatorV1,
  evaluateFiniteVocabulary,
  mintFiniteVocabularyObservationV1,
  type FiniteVocabularyEvaluationV1,
  type FiniteVocabularyObservationV1,
} from "../../../../families/finite-vocabulary/index.js";

export const PYTHON_ENUM_OWNER_PATH =
  "projects/domainspec-v2/development/remaining-meta-types/admissions/enum/owner-member-wire-catalogue.json";

const NATIVE_PROPERTY_IDS = Object.freeze([
  "str_mixin_absent",
  "aliases_absent",
  "raw_string_equality_false",
  "known_emit_parse_total",
] as const);

const HOSTILE_PROBE_IDS = Object.freeze([
  "unknown_constructor_rejected",
  "unknown_wire_structured_failure",
  "extension_rejected",
  "invalid_member_emit_rejected",
] as const);

type NativePropertyId = (typeof NATIVE_PROPERTY_IDS)[number];
type HostileProbeId = (typeof HOSTILE_PROBE_IDS)[number];

type NativeMember = Readonly<{
  member_id: string;
  native_keys: readonly string[];
  emitted_wire: string;
  parsed_member_id: string;
}>;

export type PythonEnumNativeProofV1 = Readonly<{
  schema_version: "PythonEnumNativeProof/v1";
  result: "pass" | "block";
  target: Readonly<{
    target_id: "python.shipment-priority.nominal-enum-v1";
    language: "python";
    protocol_id: "python.nominal-enum-explicit-wire/v1";
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
  hostile_probes: Readonly<Record<HostileProbeId, boolean>>;
  structured_failure: Readonly<{
    code: "DOMAINSPEC_ENUM_UNKNOWN_WIRE";
    enum_id: string;
    wire_value: string;
  }> | null;
  authority_effect: "none";
}>;

type ComposedProofV1 = Readonly<{
  schema_version: "PythonEnumComposedProof/v1";
  result: "pass";
  observation: FiniteVocabularyObservationV1;
  family_evaluation: FiniteVocabularyEvaluationV1;
  native_proof: PythonEnumNativeProofV1;
  accounting: Readonly<{
    portable_decisions: Readonly<{ declared: number; passed: number }>;
    native_properties: Readonly<{ declared: number; passed: number }>;
    hostile_probes: Readonly<{ declared: number; killed: number }>;
  }>;
  claim_ceiling: string;
  authority_effect: "none";
}>;

export class PythonEnumCompositionError extends Error {
  readonly code: string;

  constructor(code: string, detail?: string) {
    super(detail === undefined ? code : `${code}:${detail}`);
    this.name = "PythonEnumCompositionError";
    this.code = code;
  }
}

const fail = (code: string, detail?: string): never => {
  throw new PythonEnumCompositionError(code, detail);
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  value !== null && typeof value === "object" && !Array.isArray(value);

const decodeNativeProof = (value: unknown): PythonEnumNativeProofV1 => {
  if (!isRecord(value)
      || value.schema_version !== "PythonEnumNativeProof/v1"
      || (value.result !== "pass" && value.result !== "block")
      || value.catalogue_origin !== "owner-authored-admission-input"
      || value.member_order_semantics !== "none"
      || value.authority_effect !== "none"
      || !isRecord(value.target)
      || value.target.target_id !== "python.shipment-priority.nominal-enum-v1"
      || value.target.language !== "python"
      || value.target.protocol_id !== "python.nominal-enum-explicit-wire/v1"
      || !isRecord(value.native_identity_diagnostic)
      || value.native_identity_diagnostic.relation !== "nominal"
      || value.native_identity_diagnostic.claim_scope !== "native-diagnostic-only"
      || !isRecord(value.native_properties)
      || !isRecord(value.hostile_probes)
      || !Array.isArray(value.members)
      || !isRecord(value.owner_catalogue_ref)
      || !isRecord(value.denominator_ref)
      || !isRecord(value.source_ref)
      || !isRecord(value.unknown_wire)) {
    return fail("PY_ENUM_NATIVE_PROOF_INVALID");
  }
  const nativeProperties = value.native_properties;
  const hostileProbes = value.hostile_probes;
  const propertyKeys = Object.keys(nativeProperties).sort();
  const probeKeys = Object.keys(hostileProbes).sort();
  if (JSON.stringify(propertyKeys) !== JSON.stringify([...NATIVE_PROPERTY_IDS].sort())
      || JSON.stringify(probeKeys) !== JSON.stringify([...HOSTILE_PROBE_IDS].sort())
      || NATIVE_PROPERTY_IDS.some((id) => nativeProperties[id] !== true)
      || HOSTILE_PROBE_IDS.some((id) => hostileProbes[id] !== true)
      || value.result !== "pass") {
    return fail("PY_ENUM_NATIVE_PROOF_BLOCKED");
  }
  return value as PythonEnumNativeProofV1;
};

export const composePythonEnumFamilyProof = (input: Readonly<{
  owner_catalogue_bytes: string;
  denominator_bytes: string;
  native_proof: unknown;
}>): ComposedProofV1 => {
  const nativeProof = decodeNativeProof(input.native_proof);
  const { denominator, owner_catalogue: ownerCatalogue } =
    decodeFiniteVocabularyDenominatorV1(
      input.denominator_bytes,
      input.owner_catalogue_bytes,
      PYTHON_ENUM_OWNER_PATH,
    );
  if (nativeProof.owner_catalogue_ref.catalogue_id !== ownerCatalogue.catalogue_id
      || nativeProof.owner_catalogue_ref.path !== denominator.owner_catalogue_ref.path
      || nativeProof.owner_catalogue_ref.sha256 !== denominator.owner_catalogue_ref.sha256
      || nativeProof.denominator_ref.denominator_id !== denominator.denominator_id
      || nativeProof.denominator_ref.denominator_sha256
        !== denominator.denominator_sha256) {
    return fail("PY_ENUM_NATIVE_OWNER_BINDING_STALE");
  }

  const observation = mintFiniteVocabularyObservationV1({
    schema_version: "FiniteVocabularyObservation/v1",
    observation_id: "python.shipment-priority.nominal-enum-v1",
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
      "PY_ENUM_FAMILY_EVALUATION_BLOCKED",
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
    schema_version: "PythonEnumComposedProof/v1" as const,
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
    claim_ceiling: "one candidate-local Python nominal Enum composed with the owner-bound finite-vocabulary family; nominal identity remains a native diagnostic",
    authority_effect: "none" as const,
  });
};
