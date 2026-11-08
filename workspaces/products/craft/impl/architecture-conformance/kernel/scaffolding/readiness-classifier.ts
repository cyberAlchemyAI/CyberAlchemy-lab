import type {
  MetaTypeAdmissionV2,
  MetaTypeDescriptorV2,
} from "../contracts/meta-type-descriptor-v2.js";
import {
  readValidatedHandle,
  type ValidatedHandle,
} from "../contracts/validated-handle.js";
import { recomputeDocumentDigest } from "../codecs/codec-support.js";

export type FactoryReadinessCode =
  | "READY"
  | "REFUSED_UNMAPPED"
  | "REFUSED_CANDIDATE_MAPPING"
  | "REFUSED_CANDIDATE"
  | "REFUSED_DEFERRED"
  | "REFUSED_SUPERSEDED"
  | "REFUSED_STALE";

export type FactoryReadinessV1 = Readonly<{
  schema_version: "FactoryReadiness/v1";
  meta_type_ref: string;
  result: "ready" | "refused";
  code: FactoryReadinessCode;
  descriptor_id: string | null;
  authority_effect: "none";
}>;

const result = (
  admission: MetaTypeAdmissionV2,
  code: FactoryReadinessCode,
  descriptorId: string | null = null,
): FactoryReadinessV1 => Object.freeze({
  schema_version: "FactoryReadiness/v1" as const,
  meta_type_ref: admission.meta_type_ref,
  result: code === "READY" ? "ready" as const : "refused" as const,
  code,
  descriptor_id: descriptorId,
  authority_effect: "none" as const,
});

export const classifyFactoryReadiness = (input: Readonly<{
  admission: MetaTypeAdmissionV2;
  descriptor: ValidatedHandle<MetaTypeDescriptorV2>;
}>): FactoryReadinessV1 => {
  if (recomputeDocumentDigest(
    input.admission as unknown as Record<string, unknown>,
    "admission_sha256",
  ) !== input.admission.admission_sha256) {
    return result(input.admission, "REFUSED_STALE");
  }
  if (input.admission.maturity === "candidate") {
    return result(input.admission, "REFUSED_CANDIDATE");
  }
  if (input.admission.maturity === "deferred") {
    return result(input.admission, "REFUSED_DEFERRED");
  }
  if (input.admission.maturity === "superseded") {
    return result(input.admission, "REFUSED_SUPERSEDED");
  }
  if (input.admission.mapping_status === "candidate-mapped") {
    return result(input.admission, "REFUSED_CANDIDATE_MAPPING");
  }
  if (input.admission.mapping_status !== "mapped" ||
      input.admission.architecture_type_ref === null ||
      input.admission.admitted_profile_ref === null) {
    return result(input.admission, "REFUSED_UNMAPPED");
  }
  const descriptor = readValidatedHandle(input.descriptor);
  if (recomputeDocumentDigest(
    descriptor as unknown as Record<string, unknown>,
    "descriptor_sha256",
  ) !== descriptor.descriptor_sha256 ||
      descriptor.meta_type_ref !== input.admission.meta_type_ref ||
      descriptor.maturity !== input.admission.maturity ||
      descriptor.architecture_type_ref !== input.admission.architecture_type_ref ||
      descriptor.admitted_profile_ref.id !== input.admission.admitted_profile_ref.id ||
      descriptor.admitted_profile_ref.sha256 !== input.admission.admitted_profile_ref.sha256) {
    return result(input.admission, "REFUSED_STALE", descriptor.descriptor_id);
  }
  return result(input.admission, "READY", descriptor.descriptor_id);
};
