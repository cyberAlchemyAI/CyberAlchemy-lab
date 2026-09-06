import { createHash } from "node:crypto";

import {
  FINITE_VOCABULARY_DECISIONS,
  FINITE_VOCABULARY_MUTATION_KINDS,
  type FiniteVocabularyDenominatorV1,
  type FiniteVocabularyFindingCode,
  type FiniteVocabularyMutationCatalogueV1,
  type FiniteVocabularyMutationKind,
  type FiniteVocabularyMutationV1,
  type FiniteVocabularyObservationV1,
  type FiniteVocabularyObservedMemberV1,
  type OwnerEnumCatalogueV1,
  type OwnerEnumMemberV1,
} from "../contracts/finite-vocabulary-contracts.js";

type JsonObject = Record<string, unknown>;

export class FiniteVocabularyDecodeError extends Error {
  readonly code: string;

  constructor(code: string) {
    super(code);
    this.name = "FiniteVocabularyDecodeError";
    this.code = code;
  }
}

const fail = (code: string): never => {
  throw new FiniteVocabularyDecodeError(code);
};
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const isObject = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const expectObject = (value: unknown, code: string): JsonObject =>
  isObject(value) ? value : fail(code);
const expectString = (value: unknown, code: string): string =>
  typeof value === "string" && value.length > 0 ? value : fail(code);
const expectSha256 = (value: unknown, code: string): string => {
  const digest = expectString(value, code);
  return /^[a-f0-9]{64}$/u.test(digest) ? digest : fail(code);
};
const exactKeys = (source: JsonObject, keys: readonly string[], code: string): void => {
  const actual = Object.keys(source).sort(compareUtf8);
  const expected = [...keys].sort(compareUtf8);
  if (actual.length !== expected.length
      || actual.some((key, index) => key !== expected[index])) fail(code);
};
const parseJson = (bytes: string, code: string): JsonObject => {
  try {
    return expectObject(JSON.parse(bytes), code);
  } catch (error) {
    if (error instanceof FiniteVocabularyDecodeError) throw error;
    return fail(code);
  }
};
const canonicalize = (value: unknown): unknown => Array.isArray(value)
  ? value.map(canonicalize)
  : isObject(value)
    ? Object.fromEntries(Object.entries(value)
      .sort(([left], [right]) => compareUtf8(left, right))
      .map(([key, child]) => [key, canonicalize(child)]))
    : value;

export const canonicalFiniteVocabularyJson = (value: unknown): string =>
  JSON.stringify(canonicalize(value));
export const sha256FiniteVocabularyBytes = (bytes: string): string =>
  createHash("sha256").update(bytes, "utf8").digest("hex");
const sha256Json = (value: unknown): string =>
  sha256FiniteVocabularyBytes(canonicalFiniteVocabularyJson(value));

const unique = (values: readonly string[], code: string): void => {
  if (new Set(values).size !== values.length) fail(code);
};

const decodeOwnerMember = (value: unknown): OwnerEnumMemberV1 => {
  const source = expectObject(value, "FAMILY_ENUM_OWNER_MEMBER_SHAPE_INVALID");
  exactKeys(source, ["member_id", "member_key", "wire_value"],
    "FAMILY_ENUM_OWNER_MEMBER_SHAPE_INVALID");
  return Object.freeze({
    member_id: expectString(source.member_id, "FAMILY_ENUM_OWNER_MEMBER_ID_INVALID"),
    member_key: expectString(source.member_key, "FAMILY_ENUM_OWNER_MEMBER_KEY_INVALID"),
    wire_value: expectString(source.wire_value, "FAMILY_ENUM_OWNER_WIRE_INVALID"),
  });
};

export const decodeOwnerEnumCatalogueV1 = (bytes: string): OwnerEnumCatalogueV1 => {
  const source = parseJson(bytes, "FAMILY_ENUM_OWNER_CATALOGUE_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "catalogue_id", "catalogue_status", "concept_id",
    "definition_id", "definition_version", "authorship", "derivation_policy",
    "source_refs", "members", "member_order_semantics", "uniqueness",
    "wire_contract", "canonical_product_authority", "selection_assumption",
    "claim_ceiling", "authority_effect",
  ], "FAMILY_ENUM_OWNER_CATALOGUE_SHAPE_INVALID");
  if (source.schema_version !== "domainspec.enum-owner-member-wire-catalogue/v1"
      || source.catalogue_status !== "candidate-fixture"
      || source.authorship !== "owner-authored-admission-input"
      || source.derivation_policy !== "runtime-and-generated-members-forbidden-as-authority"
      || source.member_order_semantics !== "none"
      || source.canonical_product_authority !== false
      || source.authority_effect !== "none"
      || !Array.isArray(source.source_refs)) {
    return fail("FAMILY_ENUM_OWNER_CATALOGUE_POLICY_INVALID");
  }
  if (!Array.isArray(source.members) || source.members.length === 0) {
    return fail("FAMILY_ENUM_OWNER_CATALOGUE_MEMBERS_INVALID");
  }
  const members = source.members.map(decodeOwnerMember);
  unique(members.map(({ member_id: value }) => value), "FAMILY_ENUM_OWNER_MEMBER_ID_DUPLICATE");
  unique(members.map(({ member_key: value }) => value), "FAMILY_ENUM_OWNER_MEMBER_KEY_DUPLICATE");
  unique(members.map(({ wire_value: value }) => value), "FAMILY_ENUM_OWNER_WIRE_DUPLICATE");
  const uniqueness = expectObject(source.uniqueness,
    "FAMILY_ENUM_OWNER_CATALOGUE_POLICY_INVALID");
  exactKeys(uniqueness, ["member_ids", "member_keys", "wire_values"],
    "FAMILY_ENUM_OWNER_CATALOGUE_POLICY_INVALID");
  const wire = expectObject(source.wire_contract,
    "FAMILY_ENUM_OWNER_CATALOGUE_POLICY_INVALID");
  exactKeys(wire, [
    "wire_type", "member_to_wire", "wire_to_member", "unknown_wire_value",
    "aliases", "domain_wire_equality_collapse",
  ], "FAMILY_ENUM_OWNER_CATALOGUE_POLICY_INVALID");
  if (uniqueness.member_ids !== "required"
      || uniqueness.member_keys !== "required"
      || uniqueness.wire_values !== "required"
      || wire.wire_type !== "string"
      || wire.member_to_wire !== "explicit-total-one-to-one"
      || wire.wire_to_member !== "explicit-fallible"
      || wire.unknown_wire_value !== "structured-failure"
      || wire.aliases !== "forbidden"
      || wire.domain_wire_equality_collapse !== "forbidden") {
    return fail("FAMILY_ENUM_OWNER_CATALOGUE_POLICY_INVALID");
  }
  return Object.freeze({
    schema_version: "domainspec.enum-owner-member-wire-catalogue/v1" as const,
    catalogue_id: expectString(source.catalogue_id, "FAMILY_ENUM_OWNER_ID_INVALID"),
    catalogue_status: "candidate-fixture" as const,
    concept_id: expectString(source.concept_id, "FAMILY_ENUM_OWNER_ID_INVALID"),
    definition_id: expectString(source.definition_id, "FAMILY_ENUM_OWNER_ID_INVALID"),
    definition_version: expectString(source.definition_version,
      "FAMILY_ENUM_OWNER_ID_INVALID"),
    authorship: "owner-authored-admission-input" as const,
    derivation_policy: "runtime-and-generated-members-forbidden-as-authority" as const,
    members: Object.freeze(members),
    member_order_semantics: "none" as const,
    uniqueness: Object.freeze({
      member_ids: "required" as const,
      member_keys: "required" as const,
      wire_values: "required" as const,
    }),
    wire_contract: Object.freeze({
      wire_type: "string" as const,
      member_to_wire: "explicit-total-one-to-one" as const,
      wire_to_member: "explicit-fallible" as const,
      unknown_wire_value: "structured-failure" as const,
      aliases: "forbidden" as const,
      domain_wire_equality_collapse: "forbidden" as const,
    }),
    authority_effect: "none" as const,
  });
};

const denominatorBody = (
  value: Omit<FiniteVocabularyDenominatorV1, "denominator_sha256">,
) => ({
  ...value,
  positive_decisions: [...value.positive_decisions].sort(compareUtf8),
});

export const computeFiniteVocabularyDenominatorSha256 = (
  value: Omit<FiniteVocabularyDenominatorV1, "denominator_sha256">,
): string => sha256Json(denominatorBody(value));

export const decodeFiniteVocabularyDenominatorV1 = (
  bytes: string,
  ownerCatalogueBytes: string,
  expectedOwnerPath: string,
): Readonly<{
  denominator: FiniteVocabularyDenominatorV1;
  owner_catalogue: OwnerEnumCatalogueV1;
}> => {
  const ownerCatalogue = decodeOwnerEnumCatalogueV1(ownerCatalogueBytes);
  const source = parseJson(bytes, "FAMILY_ENUM_DENOMINATOR_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "denominator_id", "owner_catalogue_ref", "portable_contract",
    "native_identity_policy", "positive_decisions", "authority_effect",
    "denominator_sha256",
  ], "FAMILY_ENUM_DENOMINATOR_SHAPE_INVALID");
  if (source.schema_version !== "FiniteVocabularyDenominator/v1"
      || source.authority_effect !== "none") {
    return fail("FAMILY_ENUM_DENOMINATOR_POLICY_INVALID");
  }
  const ownerRef = expectObject(source.owner_catalogue_ref,
    "FAMILY_ENUM_DENOMINATOR_OWNER_REF_INVALID");
  exactKeys(ownerRef, ["catalogue_id", "path", "sha256"],
    "FAMILY_ENUM_DENOMINATOR_OWNER_REF_INVALID");
  const ownerPath = expectString(ownerRef.path, "FAMILY_ENUM_DENOMINATOR_OWNER_REF_INVALID");
  const ownerSha = expectSha256(ownerRef.sha256,
    "FAMILY_ENUM_DENOMINATOR_OWNER_REF_INVALID");
  if (ownerPath !== expectedOwnerPath
      || ownerRef.catalogue_id !== ownerCatalogue.catalogue_id
      || ownerSha !== sha256FiniteVocabularyBytes(ownerCatalogueBytes)) {
    return fail("FAMILY_ENUM_DENOMINATOR_OWNER_REF_STALE");
  }
  const portable = expectObject(source.portable_contract,
    "FAMILY_ENUM_DENOMINATOR_POLICY_INVALID");
  exactKeys(portable, [
    "catalogue_origin", "member_set", "member_keys", "member_to_wire",
    "wire_to_member", "unknown_wire", "member_order",
  ], "FAMILY_ENUM_DENOMINATOR_POLICY_INVALID");
  if (portable.catalogue_origin !== "owner-authored-only"
      || portable.member_set !== "closed-exact"
      || portable.member_keys !== "unique-no-aliases"
      || portable.member_to_wire !== "explicit-total-one-to-one"
      || portable.wire_to_member !== "explicit-fallible-round-trip"
      || portable.unknown_wire !== "structured-failure"
      || portable.member_order !== "non-semantic") {
    return fail("FAMILY_ENUM_DENOMINATOR_POLICY_INVALID");
  }
  const nativePolicy = expectObject(source.native_identity_policy,
    "FAMILY_ENUM_NATIVE_POLICY_INVALID");
  exactKeys(nativePolicy, ["comparison", "allowed_diagnostics"],
    "FAMILY_ENUM_NATIVE_POLICY_INVALID");
  if (nativePolicy.comparison !== "preserve-as-diagnostic-not-portable-parity"
      || !Array.isArray(nativePolicy.allowed_diagnostics)
      || JSON.stringify(nativePolicy.allowed_diagnostics)
        !== JSON.stringify(["collapsed-literal", "nominal", "not-observed"])) {
    return fail("FAMILY_ENUM_NATIVE_POLICY_INVALID");
  }
  if (!Array.isArray(source.positive_decisions)) {
    return fail("FAMILY_ENUM_DECISIONS_INVALID");
  }
  const decisions = source.positive_decisions.map((value) =>
    expectString(value, "FAMILY_ENUM_DECISIONS_INVALID"));
  const expectedDecisions = [...FINITE_VOCABULARY_DECISIONS].sort(compareUtf8);
  const actualDecisions = [...decisions].sort(compareUtf8);
  if (actualDecisions.length !== expectedDecisions.length
      || actualDecisions.some((decision, index) => decision !== expectedDecisions[index])) {
    return fail("FAMILY_ENUM_DECISIONS_INVALID");
  }
  const withoutDigest = {
    schema_version: "FiniteVocabularyDenominator/v1" as const,
    denominator_id: expectString(source.denominator_id, "FAMILY_ENUM_DENOMINATOR_ID_INVALID"),
    owner_catalogue_ref: Object.freeze({
      catalogue_id: ownerCatalogue.catalogue_id,
      path: ownerPath,
      sha256: ownerSha,
    }),
    portable_contract: Object.freeze({
      catalogue_origin: "owner-authored-only" as const,
      member_set: "closed-exact" as const,
      member_keys: "unique-no-aliases" as const,
      member_to_wire: "explicit-total-one-to-one" as const,
      wire_to_member: "explicit-fallible-round-trip" as const,
      unknown_wire: "structured-failure" as const,
      member_order: "non-semantic" as const,
    }),
    native_identity_policy: Object.freeze({
      comparison: "preserve-as-diagnostic-not-portable-parity" as const,
      allowed_diagnostics: Object.freeze([
        "collapsed-literal", "nominal", "not-observed",
      ] as const),
    }),
    positive_decisions: Object.freeze([...FINITE_VOCABULARY_DECISIONS]),
    authority_effect: "none" as const,
  };
  const digest = expectSha256(source.denominator_sha256,
    "FAMILY_ENUM_DENOMINATOR_DIGEST_INVALID");
  if (digest !== computeFiniteVocabularyDenominatorSha256(withoutDigest)) {
    return fail("FAMILY_ENUM_DENOMINATOR_DIGEST_STALE");
  }
  return Object.freeze({
    denominator: Object.freeze({ ...withoutDigest, denominator_sha256: digest }),
    owner_catalogue: ownerCatalogue,
  });
};

const canonicalObservationBody = (
  value: Omit<FiniteVocabularyObservationV1, "observation_sha256">,
) => ({
  ...value,
  members: [...value.members]
    .map((member) => ({
      ...member,
      native_keys: [...member.native_keys].sort(compareUtf8),
    }))
    .sort((left, right) => compareUtf8(
      `${left.member_id}\u0000${left.native_keys.join("\u0000")}\u0000${left.emitted_wire}`,
      `${right.member_id}\u0000${right.native_keys.join("\u0000")}\u0000${right.emitted_wire}`,
    )),
});

export const computeFiniteVocabularyObservationSha256 = (
  value: Omit<FiniteVocabularyObservationV1, "observation_sha256">,
): string => sha256Json(canonicalObservationBody(value));

export const mintFiniteVocabularyObservationV1 = (
  value: Omit<FiniteVocabularyObservationV1, "observation_sha256">,
): FiniteVocabularyObservationV1 => Object.freeze({
  ...value,
  target: Object.freeze({ ...value.target }),
  owner_catalogue_ref: Object.freeze({ ...value.owner_catalogue_ref }),
  members: Object.freeze(value.members.map((member) => Object.freeze({
    ...member,
    native_keys: Object.freeze([...member.native_keys]),
  }))),
  unknown_wire: Object.freeze({ ...value.unknown_wire }),
  native_identity_diagnostic: Object.freeze({ ...value.native_identity_diagnostic }),
  observation_sha256: computeFiniteVocabularyObservationSha256(value),
});

const decodeObservedMember = (value: unknown): FiniteVocabularyObservedMemberV1 => {
  const source = expectObject(value, "FAMILY_ENUM_OBSERVATION_MEMBER_SHAPE_INVALID");
  exactKeys(source, ["member_id", "native_keys", "emitted_wire", "parsed_member_id"],
    "FAMILY_ENUM_OBSERVATION_MEMBER_SHAPE_INVALID");
  if (!Array.isArray(source.native_keys) || source.native_keys.length === 0) {
    return fail("FAMILY_ENUM_OBSERVATION_NATIVE_KEYS_INVALID");
  }
  return Object.freeze({
    member_id: expectString(source.member_id, "FAMILY_ENUM_OBSERVATION_MEMBER_ID_INVALID"),
    native_keys: Object.freeze(source.native_keys.map((key) =>
      expectString(key, "FAMILY_ENUM_OBSERVATION_NATIVE_KEYS_INVALID"))),
    emitted_wire: expectString(source.emitted_wire,
      "FAMILY_ENUM_OBSERVATION_WIRE_INVALID"),
    parsed_member_id: expectString(source.parsed_member_id,
      "FAMILY_ENUM_OBSERVATION_PARSE_INVALID"),
  });
};

export const decodeFiniteVocabularyObservationV1 = (
  bytes: string,
): FiniteVocabularyObservationV1 => {
  const source = parseJson(bytes, "FAMILY_ENUM_OBSERVATION_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "observation_id", "source_kind", "target",
    "owner_catalogue_ref", "catalogue_origin", "member_order_semantics", "members",
    "unknown_wire", "native_identity_diagnostic", "authority_effect",
    "observation_sha256",
  ], "FAMILY_ENUM_OBSERVATION_SHAPE_INVALID");
  if (source.schema_version !== "FiniteVocabularyObservation/v1"
      || (source.source_kind !== "independent-owner-bound-positive"
        && source.source_kind !== "mutated-family-observation")
      || (source.catalogue_origin !== "owner-authored-admission-input"
        && source.catalogue_origin !== "implementation-observed")
      || (source.member_order_semantics !== "none"
        && source.member_order_semantics !== "declaration")
      || source.authority_effect !== "none"
      || !Array.isArray(source.members)) {
    return fail("FAMILY_ENUM_OBSERVATION_POLICY_INVALID");
  }
  const target = expectObject(source.target, "FAMILY_ENUM_OBSERVATION_TARGET_INVALID");
  exactKeys(target, ["target_id", "language", "protocol_id"],
    "FAMILY_ENUM_OBSERVATION_TARGET_INVALID");
  if (!["family-fixture", "typescript", "python", "rust"].includes(String(target.language))) {
    return fail("FAMILY_ENUM_OBSERVATION_TARGET_INVALID");
  }
  const ownerRef = expectObject(source.owner_catalogue_ref,
    "FAMILY_ENUM_OBSERVATION_OWNER_REF_INVALID");
  exactKeys(ownerRef, ["catalogue_id", "path", "sha256"],
    "FAMILY_ENUM_OBSERVATION_OWNER_REF_INVALID");
  const unknown = expectObject(source.unknown_wire,
    "FAMILY_ENUM_OBSERVATION_UNKNOWN_WIRE_INVALID");
  exactKeys(unknown, ["wire_value", "outcome", "error_code", "parsed_member_id"],
    "FAMILY_ENUM_OBSERVATION_UNKNOWN_WIRE_INVALID");
  if (unknown.outcome !== "structured-failure" && unknown.outcome !== "member") {
    return fail("FAMILY_ENUM_OBSERVATION_UNKNOWN_WIRE_INVALID");
  }
  if (unknown.error_code !== null && typeof unknown.error_code !== "string") {
    return fail("FAMILY_ENUM_OBSERVATION_UNKNOWN_WIRE_INVALID");
  }
  if (unknown.parsed_member_id !== null && typeof unknown.parsed_member_id !== "string") {
    return fail("FAMILY_ENUM_OBSERVATION_UNKNOWN_WIRE_INVALID");
  }
  const native = expectObject(source.native_identity_diagnostic,
    "FAMILY_ENUM_NATIVE_DIAGNOSTIC_INVALID");
  exactKeys(native, ["relation", "claim_scope"], "FAMILY_ENUM_NATIVE_DIAGNOSTIC_INVALID");
  if (!["collapsed-literal", "nominal", "not-observed"].includes(String(native.relation))
      || native.claim_scope !== "native-diagnostic-only") {
    return fail("FAMILY_ENUM_NATIVE_DIAGNOSTIC_INVALID");
  }
  const withoutDigest = {
    schema_version: "FiniteVocabularyObservation/v1" as const,
    observation_id: expectString(source.observation_id,
      "FAMILY_ENUM_OBSERVATION_ID_INVALID"),
    source_kind: source.source_kind,
    target: Object.freeze({
      target_id: expectString(target.target_id, "FAMILY_ENUM_OBSERVATION_TARGET_INVALID"),
      language: target.language,
      protocol_id: expectString(target.protocol_id,
        "FAMILY_ENUM_OBSERVATION_TARGET_INVALID"),
    }),
    owner_catalogue_ref: Object.freeze({
      catalogue_id: expectString(ownerRef.catalogue_id,
        "FAMILY_ENUM_OBSERVATION_OWNER_REF_INVALID"),
      path: expectString(ownerRef.path, "FAMILY_ENUM_OBSERVATION_OWNER_REF_INVALID"),
      sha256: expectSha256(ownerRef.sha256, "FAMILY_ENUM_OBSERVATION_OWNER_REF_INVALID"),
    }),
    catalogue_origin: source.catalogue_origin,
    member_order_semantics: source.member_order_semantics,
    members: Object.freeze(source.members.map(decodeObservedMember)),
    unknown_wire: Object.freeze({
      wire_value: expectString(unknown.wire_value,
        "FAMILY_ENUM_OBSERVATION_UNKNOWN_WIRE_INVALID"),
      outcome: unknown.outcome,
      error_code: unknown.error_code,
      parsed_member_id: unknown.parsed_member_id,
    }),
    native_identity_diagnostic: Object.freeze({
      relation: native.relation,
      claim_scope: "native-diagnostic-only" as const,
    }),
    authority_effect: "none" as const,
  } as Omit<FiniteVocabularyObservationV1, "observation_sha256">;
  const digest = expectSha256(source.observation_sha256,
    "FAMILY_ENUM_OBSERVATION_DIGEST_INVALID");
  if (digest !== computeFiniteVocabularyObservationSha256(withoutDigest)) {
    return fail("FAMILY_ENUM_OBSERVATION_DIGEST_STALE");
  }
  return Object.freeze({ ...withoutDigest, observation_sha256: digest });
};

const mutationCatalogueBody = (
  value: Omit<FiniteVocabularyMutationCatalogueV1, "catalogue_sha256">,
) => ({
  ...value,
  mutations: [...value.mutations]
    .map((mutation) => ({
      ...mutation,
      expected_finding_codes: [...mutation.expected_finding_codes].sort(compareUtf8),
    }))
    .sort((left, right) => compareUtf8(left.mutation_id, right.mutation_id)),
});

export const computeFiniteVocabularyMutationCatalogueSha256 = (
  value: Omit<FiniteVocabularyMutationCatalogueV1, "catalogue_sha256">,
): string => sha256Json(mutationCatalogueBody(value));

export const decodeFiniteVocabularyMutationCatalogueV1 = (
  bytes: string,
  denominator: FiniteVocabularyDenominatorV1,
): FiniteVocabularyMutationCatalogueV1 => {
  const source = parseJson(bytes, "FAMILY_ENUM_MUTATION_CATALOGUE_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "denominator_ref", "authorship",
    "target_code_may_read_expected_findings", "mutations", "authority_effect",
    "catalogue_sha256",
  ], "FAMILY_ENUM_MUTATION_CATALOGUE_SHAPE_INVALID");
  if (source.schema_version !== "FiniteVocabularyMutationCatalogue/v1"
      || source.authorship !== "independent-family-fixture"
      || source.target_code_may_read_expected_findings !== false
      || source.authority_effect !== "none"
      || !Array.isArray(source.mutations)) {
    return fail("FAMILY_ENUM_MUTATION_CATALOGUE_POLICY_INVALID");
  }
  const denominatorRef = expectObject(source.denominator_ref,
    "FAMILY_ENUM_MUTATION_DENOMINATOR_REF_INVALID");
  exactKeys(denominatorRef, ["denominator_id", "denominator_sha256"],
    "FAMILY_ENUM_MUTATION_DENOMINATOR_REF_INVALID");
  if (denominatorRef.denominator_id !== denominator.denominator_id
      || denominatorRef.denominator_sha256 !== denominator.denominator_sha256) {
    return fail("FAMILY_ENUM_MUTATION_DENOMINATOR_REF_STALE");
  }
  const mutations: FiniteVocabularyMutationV1[] = source.mutations.map((value) => {
    const mutation = expectObject(value, "FAMILY_ENUM_MUTATION_SHAPE_INVALID");
    exactKeys(mutation, ["mutation_id", "mutation_kind", "expected_finding_codes"],
      "FAMILY_ENUM_MUTATION_SHAPE_INVALID");
    if (!FINITE_VOCABULARY_MUTATION_KINDS.includes(
      mutation.mutation_kind as FiniteVocabularyMutationKind,
    ) || !Array.isArray(mutation.expected_finding_codes)
      || mutation.expected_finding_codes.length === 0) {
      return fail("FAMILY_ENUM_MUTATION_SHAPE_INVALID");
    }
    return Object.freeze({
      mutation_id: expectString(mutation.mutation_id, "FAMILY_ENUM_MUTATION_ID_INVALID"),
      mutation_kind: mutation.mutation_kind as FiniteVocabularyMutationKind,
      expected_finding_codes: Object.freeze(mutation.expected_finding_codes.map(
        (code): FiniteVocabularyFindingCode => {
          const decoded = expectString(code, "FAMILY_ENUM_MUTATION_EXPECTATION_INVALID");
          return decoded as FiniteVocabularyFindingCode;
        },
      )),
    });
  });
  unique(mutations.map(({ mutation_id: value }) => value), "FAMILY_ENUM_MUTATION_ID_DUPLICATE");
  const actualKinds = mutations.map(({ mutation_kind: value }) => value).sort(compareUtf8);
  const expectedKinds = [...FINITE_VOCABULARY_MUTATION_KINDS].sort(compareUtf8);
  if (actualKinds.length !== expectedKinds.length
      || actualKinds.some((kind, index) => kind !== expectedKinds[index])) {
    return fail("FAMILY_ENUM_MUTATION_CLASSES_INCOMPLETE");
  }
  const withoutDigest = {
    schema_version: "FiniteVocabularyMutationCatalogue/v1" as const,
    denominator_ref: Object.freeze({
      denominator_id: denominator.denominator_id,
      denominator_sha256: denominator.denominator_sha256,
    }),
    authorship: "independent-family-fixture" as const,
    target_code_may_read_expected_findings: false as const,
    mutations: Object.freeze(mutations),
    authority_effect: "none" as const,
  };
  const digest = expectSha256(source.catalogue_sha256,
    "FAMILY_ENUM_MUTATION_CATALOGUE_DIGEST_INVALID");
  if (digest !== computeFiniteVocabularyMutationCatalogueSha256(withoutDigest)) {
    return fail("FAMILY_ENUM_MUTATION_CATALOGUE_DIGEST_STALE");
  }
  return Object.freeze({ ...withoutDigest, catalogue_sha256: digest });
};
