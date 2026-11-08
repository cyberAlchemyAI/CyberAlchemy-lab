import type { ExactRef } from "./exact-ref.js";

export type MetaTypeMaturity =
  | "active"
  | "candidate"
  | "deferred"
  | "superseded";

export type MappingStatus =
  | "mapped"
  | "candidate-mapped"
  | "profiled-unmapped"
  | "unsupported"
  | "blocked";

export type MetaTypeAdmissionV2 = Readonly<{
  schema_version: "MetaTypeAdmission/v2";
  meta_type_ref: `DS-D1.${number}`;
  maturity: MetaTypeMaturity;
  mapping_status: MappingStatus;
  architecture_type_ref: string | null;
  admitted_profile_ref: ExactRef | null;
  admission_sha256: string;
  authority_effect: "none";
}>;

export type RealizationMode =
  | "generate-and-observe"
  | "bind-and-observe"
  | "trace-and-evaluate";

export type MetaTypeDescriptorV2 = Readonly<{
  schema_version: "MetaTypeDescriptor/v2";
  descriptor_id: string;
  meta_type_ref: `DS-D1.${number}`;
  maturity: MetaTypeMaturity;
  criterion_schema_ref: ExactRef;
  architecture_type_ref: string;
  admitted_profile_ref: ExactRef;
  modes: readonly RealizationMode[];
  supported_relation_refs: readonly string[];
  provider_refs: Readonly<{
    projector: ExactRef;
    definition_or_binding: ExactRef;
    obligations: ExactRef;
    evaluator: ExactRef;
    mutations: ExactRef;
  }>;
  family_ref: ExactRef;
  target_ref: ExactRef;
  realization_ref: ExactRef;
  claim_ceiling: string;
  descriptor_sha256: string;
  authority_effect: "none";
}>;
