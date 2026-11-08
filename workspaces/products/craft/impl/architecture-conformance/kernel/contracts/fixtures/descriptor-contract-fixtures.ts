import { createHash } from "node:crypto";

import type { ExactRef } from "../exact-ref.js";
import type {
  MetaTypeAdmissionV2,
  MetaTypeDescriptorV2,
} from "../meta-type-descriptor-v2.js";
import type { ProviderEnvelopeV2 } from "../provider-envelope-v2.js";

const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");
export const contractBytes = (value: unknown): string => JSON.stringify(value);

export const referenceBytes = Object.freeze({
  criterion: '{"schema_version":"CriterionSchema/v1","id":"finite-vocabulary"}',
  profile: '{"schema_version":"ArchitectureProfile/v1","id":"typescript-strict"}',
  projector: '{"schema_version":"ProjectorProvider/v1","id":"enum-projector"}',
  definition: '{"schema_version":"DefinitionProvider/v1","id":"enum-definition"}',
  obligations: '{"schema_version":"ObligationProvider/v1","id":"enum-obligations"}',
  evaluator: '{"schema_version":"EvaluatorProvider/v1","id":"enum-evaluator"}',
  mutations: '{"schema_version":"MutationProvider/v1","id":"enum-mutations"}',
  family: '{"schema_version":"FamilyProvider/v1","id":"finite-vocabulary"}',
  target: '{"schema_version":"TargetProvider/v1","id":"typescript"}',
  realization: '{"schema_version":"RealizationProvider/v1","id":"owned-const-object"}',
});

const ref = (
  id: keyof typeof referenceBytes,
  schemaVersion: string,
): ExactRef => Object.freeze({
  id,
  schema_version: schemaVersion,
  sha256: sha256(referenceBytes[id]),
});

export const refs = Object.freeze({
  criterion: ref("criterion", "CriterionSchema/v1"),
  profile: ref("profile", "ArchitectureProfile/v1"),
  projector: ref("projector", "ProjectorProvider/v1"),
  definition: ref("definition", "DefinitionProvider/v1"),
  obligations: ref("obligations", "ObligationProvider/v1"),
  evaluator: ref("evaluator", "EvaluatorProvider/v1"),
  mutations: ref("mutations", "MutationProvider/v1"),
  family: ref("family", "FamilyProvider/v1"),
  target: ref("target", "TargetProvider/v1"),
  realization: ref("realization", "RealizationProvider/v1"),
});

const admission = (
  body: Omit<MetaTypeAdmissionV2, "admission_sha256">,
): MetaTypeAdmissionV2 => Object.freeze({
  ...body,
  admission_sha256: sha256(contractBytes(body)),
});

export const activeAdmission = admission({
  schema_version: "MetaTypeAdmission/v2",
  meta_type_ref: "DS-D1.3",
  maturity: "active",
  mapping_status: "candidate-mapped",
  architecture_type_ref: "architecture.Enum",
  admitted_profile_ref: refs.profile,
  authority_effect: "none",
});

export const candidateAdmission = admission({
  schema_version: "MetaTypeAdmission/v2",
  meta_type_ref: "DS-D1.15",
  maturity: "candidate",
  mapping_status: "candidate-mapped",
  architecture_type_ref: null,
  admitted_profile_ref: null,
  authority_effect: "none",
});

export const missingMappingAdmission = admission({
  schema_version: "MetaTypeAdmission/v2",
  meta_type_ref: "DS-D1.3",
  maturity: "active",
  mapping_status: "profiled-unmapped",
  architecture_type_ref: null,
  admitted_profile_ref: refs.profile,
  authority_effect: "none",
});

const descriptor = (
  body: Omit<MetaTypeDescriptorV2, "descriptor_sha256">,
): MetaTypeDescriptorV2 => Object.freeze({
  ...body,
  descriptor_sha256: sha256(contractBytes(body)),
});

const descriptorBody: Omit<MetaTypeDescriptorV2, "descriptor_sha256"> = {
  schema_version: "MetaTypeDescriptor/v2",
  descriptor_id: "finite-vocabulary.typescript.owned-const-object-v1",
  meta_type_ref: "DS-D1.3",
  maturity: "active",
  criterion_schema_ref: refs.criterion,
  architecture_type_ref: "architecture.Enum",
  admitted_profile_ref: refs.profile,
  modes: ["generate-and-observe"],
  supported_relation_refs: [],
  provider_refs: {
    projector: refs.projector,
    definition_or_binding: refs.definition,
    obligations: refs.obligations,
    evaluator: refs.evaluator,
    mutations: refs.mutations,
  },
  family_ref: refs.family,
  target_ref: refs.target,
  realization_ref: refs.realization,
  claim_ceiling: "one candidate-local finite-vocabulary TypeScript realization",
  authority_effect: "none",
};

export const validDescriptor = descriptor(descriptorBody);
export const collapsedAxesDescriptor = descriptor({
  ...descriptorBody,
  target_ref: refs.family,
  realization_ref: refs.family,
});
export const maturityInflatedDescriptor = descriptor({
  ...descriptorBody,
  meta_type_ref: "DS-D1.15",
  maturity: "active",
});

type ExamplePayload = Readonly<{ member_ids: readonly string[] }>;
const output: ExamplePayload = Object.freeze({ member_ids: ["paid", "pending"] });
const providerBody = {
  schema_version: "ProviderEnvelope/v2" as const,
  provider_id: "finite-vocabulary.definition",
  provider_version: "1.0.0",
  provider_config_sha256: sha256("finite-vocabulary.definition/config/v1"),
  input_refs: [refs.criterion],
  output_schema_version: "FiniteVocabularyDefinition/v1",
  output,
  output_sha256: sha256(contractBytes(output)),
  unsupported_residue: [],
  claim_ceiling: "one candidate-local definition",
  authority_effect: "none" as const,
};

export const validProviderEnvelope: ProviderEnvelopeV2<ExamplePayload> =
  Object.freeze({
    ...providerBody,
    envelope_sha256: sha256(contractBytes(providerBody)),
  });

const staleProviderBody = {
  ...providerBody,
  output_sha256: "0".repeat(64),
};
export const staleProviderEnvelope: ProviderEnvelopeV2<ExamplePayload> =
  Object.freeze({
    ...staleProviderBody,
    envelope_sha256: sha256(contractBytes(staleProviderBody)),
  });
