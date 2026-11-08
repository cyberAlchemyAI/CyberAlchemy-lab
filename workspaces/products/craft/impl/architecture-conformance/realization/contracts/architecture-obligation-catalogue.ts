export type ExactSourceRef = Readonly<{
  path: string;
  sha256: string;
}>;

export type EnumMemberExpectation = Readonly<{
  member_id: string;
  semantic_value: string;
}>;

export type EnumMemberBijectionPayload = Readonly<{
  concept_id: string;
  composition_kind: "direct";
  order_semantics: "none";
  members: readonly EnumMemberExpectation[];
}>;

export type ArchitectureObligation = Readonly<{
  obligation_key: "enum.member-bijection@1";
  contract_version: "1";
  subject_ref: string;
  operator: "member-bijection";
  expected_payload: EnumMemberBijectionPayload;
  failure_codes: readonly string[];
}>;

export type ArchitectureObligationCatalogue = Readonly<{
  schema_version: "ArchitectureObligationCatalogue/v1";
  catalogue_id: string;
  catalogue_version: "1";
  definition_ref: ExactSourceRef & Readonly<{
    definition_id: string;
    definition_version: "1";
    authority_status: "candidate-fixture";
  }>;
  ontology_ref: ExactSourceRef & Readonly<{
    ontology_id: string;
    schema_version: string;
  }>;
  profile_ref: ExactSourceRef & Readonly<{
    profile_id: string;
    schema_version: string;
    extends: readonly (ExactSourceRef & Readonly<{
      profile_id: string;
      schema_version: string;
    }>)[];
  }>;
  obligations: readonly ArchitectureObligation[];
  catalogue_sha256: string;
  owner_ref: "architecture-obligation-catalogue-owner";
  authority_effect: "none";
}>;

export type ArchitectureObligationDiagnostic = Readonly<{
  code: string;
  detail?: Readonly<Record<string, unknown>>;
}>;
