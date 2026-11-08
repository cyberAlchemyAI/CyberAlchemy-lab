export type ArchitectureRealizationCase = Readonly<{
  schema_version: "ArchitectureRealizationCase/v1";
  case_id: string;
  refs: Readonly<{
    definition_sha256: string;
    ontology_sha256: string;
    realization_spec_sha256: string;
    catalogue_sha256: string;
    catalogue_predecessor_sha256: string;
    binding_sha256: string;
    profile_sha256: string;
    provider_sha256: string;
    emitter_config_sha256: string;
    compiler_config_sha256: string;
  }>;
  claim_ceiling: "one candidate-local direct TypeScript Enum proof";
  authority_effect: "none";
}>;
