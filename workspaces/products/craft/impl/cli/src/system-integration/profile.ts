import { FROZEN_SYSTEM_INTEGRATION_PROFILE } from "./frozen-profile.generated.js";
import type { SupportedLanguage } from "../meta-types/types.js";
import type { FrozenSystemIntegrationProfileV1 } from "./types.js";

const SHA = /^[a-f0-9]{64}$/;
const DEFINITIONS = ["domainspec-v2-D45", "domainspec-v2-D46", "domainspec-v2-D47", "domainspec-v2-D48", "domainspec-v2-D49"] as const;

export class SystemIntegrationProfileError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(message);
    this.name = "SystemIntegrationProfileError";
  }
}

function fail(code: string, pointer: string, message: string): never {
  throw new SystemIntegrationProfileError(code, pointer, message);
}

export function validateFrozenSystemIntegrationProfile(value: FrozenSystemIntegrationProfileV1 = FROZEN_SYSTEM_INTEGRATION_PROFILE): FrozenSystemIntegrationProfileV1 {
  if (value.profile.profile_id !== "domainspec.system-integration-profile/provider-neutral-v1" || value.profile.status !== "canonical-target" || value.profile.authority_effect !== "none") fail("SIC_PROFILE_UNRESOLVED", "/profile", "unsupported frozen system-integration profile");
  if (JSON.stringify(value.profile.definition_ids) !== JSON.stringify(DEFINITIONS) || value.profile.contract_kinds.length !== 5) fail("SIC_PROFILE_UNRESOLVED", "/profile/definition_ids", "D45-D49 denominator drift");
  if (!SHA.test(value.profile_digest) || !SHA.test(value.profile.architecture.sha256)) fail("SIC_PROFILE_UNRESOLVED", "/profile", "profile digest is invalid");
  if (value.profile.claim_ceiling.provider_selected_by_domainspec !== false || value.profile.claim_ceiling.runtime_guarantees_observed !== false || value.profile.claim_ceiling.durable_dispatch !== false) fail("SIC_PROFILE_UNRESOLVED", "/profile/claim_ceiling", "provider-neutral claim ceiling inflated");
  for (const language of ["typescript", "python", "rust"] as const) {
    const row = value.language_profiles[language];
    if (row.value.language !== language || row.value.system_profile_ref !== value.profile.profile_id || row.value.status !== "canonical-target" || row.value.authority_effect !== "none" || !SHA.test(row.digest)) fail("SIC_PROFILE_UNRESOLVED", `/language_profiles/${language}`, "language profile mismatch");
    if (JSON.stringify(row.value.semantic_obligations) !== JSON.stringify(DEFINITIONS)) fail("SIC_PROFILE_UNRESOLVED", `/language_profiles/${language}/semantic_obligations`, "language obligation drift");
  }
  return value;
}

export const FROZEN_SYSTEM_INTEGRATION = validateFrozenSystemIntegrationProfile();

export function languageProfile(language: SupportedLanguage) {
  return FROZEN_SYSTEM_INTEGRATION.language_profiles[language];
}
