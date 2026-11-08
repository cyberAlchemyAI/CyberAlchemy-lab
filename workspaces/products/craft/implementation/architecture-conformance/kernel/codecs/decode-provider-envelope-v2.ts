import type { ExactRefResolver } from "../contracts/exact-ref.js";
import type { ProviderEnvelopeV2 } from "../contracts/provider-envelope-v2.js";
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

const ENVELOPE_KEYS = [
  "schema_version",
  "provider_id",
  "provider_version",
  "provider_config_sha256",
  "input_refs",
  "output_schema_version",
  "output",
  "output_sha256",
  "unsupported_residue",
  "claim_ceiling",
  "envelope_sha256",
  "authority_effect",
] as const;
const SHA256 = /^[a-f0-9]{64}$/u;

export const decodeProviderEnvelopeV2 = async <T>(
  bytes: string,
  resolveRef: ExactRefResolver,
): Promise<ValidatedHandle<ProviderEnvelopeV2<T>>> => {
  const value = parseRecord(bytes, "FACTORY_PROVIDER_SCHEMA_INVALID");
  if (!exactKeys(value, ENVELOPE_KEYS) ||
      value.schema_version !== "ProviderEnvelope/v2" ||
      typeof value.provider_id !== "string" || value.provider_id.length === 0 ||
      typeof value.provider_version !== "string" ||
      value.provider_version.length === 0 ||
      typeof value.provider_config_sha256 !== "string" ||
      !SHA256.test(value.provider_config_sha256) ||
      !Array.isArray(value.input_refs) ||
      typeof value.output_schema_version !== "string" ||
      value.output_schema_version.length === 0 ||
      !isRecord(value.output) ||
      typeof value.output_sha256 !== "string" ||
      !SHA256.test(value.output_sha256) ||
      !Array.isArray(value.unsupported_residue) ||
      !value.unsupported_residue.every((item) => typeof item === "string") ||
      typeof value.claim_ceiling !== "string" || value.claim_ceiling.length === 0 ||
      typeof value.envelope_sha256 !== "string" ||
      !SHA256.test(value.envelope_sha256) ||
      value.authority_effect !== "none") {
    return fail("FACTORY_PROVIDER_SCHEMA_INVALID");
  }
  const refs = value.input_refs.map(decodeExactRef);
  if (!unique(refs.map((ref) => `${ref.id}\u0000${ref.sha256}`))) {
    return fail("FACTORY_PROVIDER_INPUT_REF_DUPLICATE");
  }
  if (sha256(JSON.stringify(value.output)) !== value.output_sha256) {
    return fail("FACTORY_PROVIDER_OUTPUT_DIGEST_STALE");
  }
  if (recomputeDocumentDigest(value, "envelope_sha256") !==
      value.envelope_sha256) {
    return fail("FACTORY_PROVIDER_ENVELOPE_DIGEST_STALE");
  }
  const validatedRefs: ExactRefIdentity[] = [];
  for (const ref of refs) {
    validatedRefs.push(await validateExactRef(ref, resolveRef));
  }
  return createValidatedHandle({
    value: value as ProviderEnvelopeV2<T>,
    source_sha256: sha256(bytes),
    validated_refs: validatedRefs,
  });
};
