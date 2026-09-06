import type { ExactRefResolver } from "../contracts/exact-ref.js";
import type {
  MappingStatus,
  MetaTypeAdmissionV2,
  MetaTypeDescriptorV2,
  MetaTypeMaturity,
  RealizationMode,
} from "../contracts/meta-type-descriptor-v2.js";
import {
  createValidatedHandle,
  type ExactRefIdentity,
  type ValidatedHandle,
} from "../contracts/validated-handle.js";
import {
  decodeExactRef,
  exactKeys,
  fail,
  isRecord,
  parseRecord,
  recomputeDocumentDigest,
  sha256,
  unique,
  validateExactRef,
} from "./codec-support.js";

const ADMISSION_KEYS = [
  "schema_version",
  "meta_type_ref",
  "maturity",
  "mapping_status",
  "architecture_type_ref",
  "admitted_profile_ref",
  "admission_sha256",
  "authority_effect",
] as const;
const DESCRIPTOR_KEYS = [
  "schema_version",
  "descriptor_id",
  "meta_type_ref",
  "maturity",
  "criterion_schema_ref",
  "architecture_type_ref",
  "admitted_profile_ref",
  "modes",
  "supported_relation_refs",
  "provider_refs",
  "family_ref",
  "target_ref",
  "realization_ref",
  "claim_ceiling",
  "descriptor_sha256",
  "authority_effect",
] as const;
const PROVIDER_KEYS = [
  "projector",
  "definition_or_binding",
  "obligations",
  "evaluator",
  "mutations",
] as const;
const MATURITIES: readonly MetaTypeMaturity[] = [
  "active",
  "candidate",
  "deferred",
  "superseded",
];
const MAPPINGS: readonly MappingStatus[] = [
  "mapped",
  "candidate-mapped",
  "profiled-unmapped",
  "unsupported",
  "blocked",
];
const MODES: readonly RealizationMode[] = [
  "generate-and-observe",
  "bind-and-observe",
  "trace-and-evaluate",
];
const META_TYPE_REF = /^DS-D1\.[0-9]+$/u;

const decodeAdmission = (bytes: string): MetaTypeAdmissionV2 => {
  const value = parseRecord(bytes, "FACTORY_ADMISSION_SCHEMA_INVALID");
  if (!exactKeys(value, ADMISSION_KEYS) ||
      value.schema_version !== "MetaTypeAdmission/v2" ||
      typeof value.meta_type_ref !== "string" ||
      !META_TYPE_REF.test(value.meta_type_ref) ||
      !MATURITIES.includes(value.maturity as MetaTypeMaturity) ||
      !MAPPINGS.includes(value.mapping_status as MappingStatus) ||
      !(typeof value.architecture_type_ref === "string" ||
        value.architecture_type_ref === null) ||
      !(isRecord(value.admitted_profile_ref) ||
        value.admitted_profile_ref === null) ||
      typeof value.admission_sha256 !== "string" ||
      value.authority_effect !== "none") {
    return fail("FACTORY_ADMISSION_SCHEMA_INVALID");
  }
  if (recomputeDocumentDigest(value, "admission_sha256") !==
      value.admission_sha256) {
    return fail("FACTORY_ADMISSION_DIGEST_STALE");
  }
  if (value.admitted_profile_ref !== null) {
    decodeExactRef(value.admitted_profile_ref);
  }
  return value as MetaTypeAdmissionV2;
};

const refIdentity = (value: unknown): string => {
  const ref = decodeExactRef(value);
  return `${ref.id}\u0000${ref.schema_version}\u0000${ref.sha256}`;
};

export const admitMetaTypeDescriptorV2 = async (
  bytes: string,
  admissionBytes: string,
  resolveRef: ExactRefResolver,
): Promise<ValidatedHandle<MetaTypeDescriptorV2>> => {
  const admission = decodeAdmission(admissionBytes);
  const value = parseRecord(bytes, "FACTORY_DESCRIPTOR_SCHEMA_INVALID");
  if (!exactKeys(value, DESCRIPTOR_KEYS) ||
      value.schema_version !== "MetaTypeDescriptor/v2" ||
      typeof value.descriptor_id !== "string" || value.descriptor_id.length === 0 ||
      typeof value.meta_type_ref !== "string" ||
      !META_TYPE_REF.test(value.meta_type_ref) ||
      !MATURITIES.includes(value.maturity as MetaTypeMaturity) ||
      typeof value.architecture_type_ref !== "string" ||
      value.architecture_type_ref.length === 0 ||
      !Array.isArray(value.modes) || value.modes.length === 0 ||
      !value.modes.every((mode) => MODES.includes(mode as RealizationMode)) ||
      !unique(value.modes as string[]) ||
      !Array.isArray(value.supported_relation_refs) ||
      !value.supported_relation_refs.every((ref) =>
        typeof ref === "string" && ref.length > 0) ||
      !unique(value.supported_relation_refs as string[]) ||
      !isRecord(value.provider_refs) ||
      !exactKeys(value.provider_refs, PROVIDER_KEYS) ||
      typeof value.claim_ceiling !== "string" || value.claim_ceiling.length === 0 ||
      typeof value.descriptor_sha256 !== "string" ||
      value.authority_effect !== "none") {
    return fail("FACTORY_DESCRIPTOR_SCHEMA_INVALID");
  }
  for (const ref of [
    value.criterion_schema_ref,
    value.admitted_profile_ref,
    value.family_ref,
    value.target_ref,
    value.realization_ref,
    ...Object.values(value.provider_refs),
  ]) {
    decodeExactRef(ref);
  }
  if (recomputeDocumentDigest(value, "descriptor_sha256") !==
      value.descriptor_sha256) {
    return fail("FACTORY_DESCRIPTOR_DIGEST_STALE");
  }
  if (value.meta_type_ref !== admission.meta_type_ref ||
      value.maturity !== admission.maturity ||
      admission.maturity !== "active") {
    return fail("FACTORY_DESCRIPTOR_MATURITY_INFLATION");
  }
  if ((admission.mapping_status !== "mapped" &&
       admission.mapping_status !== "candidate-mapped") ||
      admission.architecture_type_ref === null ||
      admission.admitted_profile_ref === null) {
    return fail("FACTORY_DESCRIPTOR_MAPPING_MISSING");
  }
  if (value.architecture_type_ref !== admission.architecture_type_ref ||
      refIdentity(value.admitted_profile_ref) !==
        refIdentity(admission.admitted_profile_ref)) {
    return fail("FACTORY_DESCRIPTOR_ADMISSION_MISMATCH");
  }
  const axes = [
    refIdentity(value.family_ref),
    refIdentity(value.target_ref),
    refIdentity(value.realization_ref),
  ];
  if (!unique(axes)) return fail("FACTORY_DESCRIPTOR_AXIS_COLLAPSE");
  const providerIdentities = Object.values(value.provider_refs).map(refIdentity);
  if (!unique(providerIdentities)) {
    return fail("FACTORY_DESCRIPTOR_PROVIDER_DUPLICATE");
  }
  const refs = [
    value.criterion_schema_ref,
    value.admitted_profile_ref,
    value.family_ref,
    value.target_ref,
    value.realization_ref,
    ...Object.values(value.provider_refs),
  ];
  const validatedRefs: ExactRefIdentity[] = [];
  for (const ref of refs) {
    validatedRefs.push(await validateExactRef(ref, resolveRef));
  }
  return createValidatedHandle({
    value: value as MetaTypeDescriptorV2,
    source_sha256: sha256(bytes),
    validated_refs: validatedRefs,
  });
};
