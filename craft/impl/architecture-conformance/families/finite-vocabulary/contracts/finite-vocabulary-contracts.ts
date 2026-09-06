export const FINITE_VOCABULARY_DECISIONS = Object.freeze([
  "owner-catalogue-provenance",
  "exact-member-set",
  "unique-member-observation",
  "one-native-key-per-member",
  "unique-native-keys",
  "exact-member-wire",
  "unique-emitted-wires",
  "known-wire-round-trip",
  "unknown-wire-structured-failure",
  "order-is-non-semantic",
] as const);

export type FiniteVocabularyDecisionId =
  (typeof FINITE_VOCABULARY_DECISIONS)[number];

export type OwnerEnumMemberV1 = Readonly<{
  member_id: string;
  member_key: string;
  wire_value: string;
}>;

export type OwnerEnumCatalogueV1 = Readonly<{
  schema_version: "domainspec.enum-owner-member-wire-catalogue/v1";
  catalogue_id: string;
  catalogue_status: "candidate-fixture";
  concept_id: string;
  definition_id: string;
  definition_version: string;
  authorship: "owner-authored-admission-input";
  derivation_policy: "runtime-and-generated-members-forbidden-as-authority";
  members: readonly OwnerEnumMemberV1[];
  member_order_semantics: "none";
  uniqueness: Readonly<{
    member_ids: "required";
    member_keys: "required";
    wire_values: "required";
  }>;
  wire_contract: Readonly<{
    wire_type: "string";
    member_to_wire: "explicit-total-one-to-one";
    wire_to_member: "explicit-fallible";
    unknown_wire_value: "structured-failure";
    aliases: "forbidden";
    domain_wire_equality_collapse: "forbidden";
  }>;
  authority_effect: "none";
}>;

export type FiniteVocabularyDenominatorV1 = Readonly<{
  schema_version: "FiniteVocabularyDenominator/v1";
  denominator_id: string;
  owner_catalogue_ref: Readonly<{
    catalogue_id: string;
    path: string;
    sha256: string;
  }>;
  portable_contract: Readonly<{
    catalogue_origin: "owner-authored-only";
    member_set: "closed-exact";
    member_keys: "unique-no-aliases";
    member_to_wire: "explicit-total-one-to-one";
    wire_to_member: "explicit-fallible-round-trip";
    unknown_wire: "structured-failure";
    member_order: "non-semantic";
  }>;
  native_identity_policy: Readonly<{
    comparison: "preserve-as-diagnostic-not-portable-parity";
    allowed_diagnostics: readonly ["collapsed-literal", "nominal", "not-observed"];
  }>;
  positive_decisions: readonly FiniteVocabularyDecisionId[];
  authority_effect: "none";
  denominator_sha256: string;
}>;

export type FiniteVocabularyObservedMemberV1 = Readonly<{
  member_id: string;
  native_keys: readonly string[];
  emitted_wire: string;
  parsed_member_id: string;
}>;

export type FiniteVocabularyUnknownWireObservationV1 = Readonly<{
  wire_value: string;
  outcome: "structured-failure" | "member";
  error_code: string | null;
  parsed_member_id: string | null;
}>;

export type FiniteVocabularyObservationV1 = Readonly<{
  schema_version: "FiniteVocabularyObservation/v1";
  observation_id: string;
  source_kind: "independent-owner-bound-positive" | "mutated-family-observation";
  target: Readonly<{
    target_id: string;
    language: "family-fixture" | "typescript" | "python" | "rust";
    protocol_id: string;
  }>;
  owner_catalogue_ref: FiniteVocabularyDenominatorV1["owner_catalogue_ref"];
  catalogue_origin: "owner-authored-admission-input" | "implementation-observed";
  member_order_semantics: "none" | "declaration";
  members: readonly FiniteVocabularyObservedMemberV1[];
  unknown_wire: FiniteVocabularyUnknownWireObservationV1;
  native_identity_diagnostic: Readonly<{
    relation: "collapsed-literal" | "nominal" | "not-observed";
    claim_scope: "native-diagnostic-only";
  }>;
  authority_effect: "none";
  observation_sha256: string;
}>;

export type FiniteVocabularyFindingCode =
  | "FAMILY_ENUM_PROVENANCE_MISMATCH"
  | "FAMILY_ENUM_MEMBER_MISSING"
  | "FAMILY_ENUM_MEMBER_UNEXPECTED"
  | "FAMILY_ENUM_MEMBER_DUPLICATE"
  | "FAMILY_ENUM_ALIAS_OBSERVED"
  | "FAMILY_ENUM_MEMBER_KEY_MISMATCH"
  | "FAMILY_ENUM_NATIVE_KEY_COLLISION"
  | "FAMILY_ENUM_WIRE_MISMATCH"
  | "FAMILY_ENUM_WIRE_COLLISION"
  | "FAMILY_ENUM_ROUND_TRIP_CYCLE"
  | "FAMILY_ENUM_UNKNOWN_WIRE_ACCEPTED"
  | "FAMILY_ENUM_UNKNOWN_PROBE_INVALID"
  | "FAMILY_ENUM_ORDER_BECAME_SEMANTIC";

export type FiniteVocabularyFindingV1 = Readonly<{
  code: FiniteVocabularyFindingCode;
  decision_id: FiniteVocabularyDecisionId;
  member_id: string | null;
  expected: string | null;
  observed: string | null;
}>;

export type FiniteVocabularyEvaluationV1 = Readonly<{
  schema_version: "FiniteVocabularyEvaluation/v1";
  evaluation_id: string;
  denominator_ref: Readonly<{
    denominator_id: string;
    denominator_sha256: string;
  }>;
  observation_ref: Readonly<{
    observation_id: string;
    observation_sha256: string;
  }>;
  verdict: "pass" | "fail";
  findings: readonly FiniteVocabularyFindingV1[];
  positive_decision_accounting: Readonly<{
    declared: number;
    passed: number;
    failed: number;
    unaccounted: 0;
  }>;
  portable_claim: "owner-bound-finite-member-wire-bijection";
  native_identity_diagnostic: FiniteVocabularyObservationV1["native_identity_diagnostic"];
  authority_effect: "none";
}>;

export const FINITE_VOCABULARY_MUTATION_KINDS = Object.freeze([
  "missing-member",
  "extra-member",
  "duplicate-member",
  "alias",
  "round-trip-cycle",
  "wire-collision",
  "order-authority",
  "implementation-provenance",
  "unknown-wire-accepted",
] as const);

export type FiniteVocabularyMutationKind =
  (typeof FINITE_VOCABULARY_MUTATION_KINDS)[number];

export type FiniteVocabularyMutationV1 = Readonly<{
  mutation_id: string;
  mutation_kind: FiniteVocabularyMutationKind;
  expected_finding_codes: readonly FiniteVocabularyFindingCode[];
}>;

export type FiniteVocabularyMutationCatalogueV1 = Readonly<{
  schema_version: "FiniteVocabularyMutationCatalogue/v1";
  denominator_ref: Readonly<{
    denominator_id: string;
    denominator_sha256: string;
  }>;
  authorship: "independent-family-fixture";
  target_code_may_read_expected_findings: false;
  mutations: readonly FiniteVocabularyMutationV1[];
  authority_effect: "none";
  catalogue_sha256: string;
}>;
