import type { EnumDefinitionMember } from "./enum-definition-snapshot.js";

export type EnumRealizationIR = Readonly<{
  schema_version: "EnumRealizationIR/v1";
  definition_ref: Readonly<{
    definition_id: string;
    definition_version: string;
    definition_sha256: string;
  }>;
  realization_spec_ref: Readonly<{
    spec_id: string;
    spec_sha256: string;
  }>;
  concept_id: string;
  composition_kind: "direct";
  order_semantics: "none";
  members: readonly EnumDefinitionMember[];
  ir_sha256: string;
  authority_effect: "none";
}>;
