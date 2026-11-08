import type { SupportedLanguage } from "../meta-types/types.js";

export interface SystemIntegrationLanguageProfileV1 {
  readonly schema_version: "domainspec.system-integration-language-profile/v1";
  readonly language_profile_id: string;
  readonly system_profile_ref: "domainspec.system-integration-profile/provider-neutral-v1";
  readonly language: SupportedLanguage;
  readonly status: "canonical-target";
  readonly implementation_state: string;
  readonly record_form: string;
  readonly dependency_contract_form: string;
  readonly composition_boundary: string;
  readonly domain_interface_mapping: string;
  readonly generated_extension: "ts" | "py" | "rs";
  readonly forbidden_abstractions: readonly string[];
  readonly semantic_obligations: readonly string[];
  readonly authority_effect: "none";
}

export interface SystemIntegrationProfileV1 {
  readonly schema_version: "domainspec.system-integration-profile/v1";
  readonly profile_id: "domainspec.system-integration-profile/provider-neutral-v1";
  readonly status: "canonical-target";
  readonly implementation_state: string;
  readonly architecture: { readonly architecture_id: "domainspec-durable-recovery@2"; readonly path: string; readonly sha256: string };
  readonly owner_admission: { readonly decision_id: string; readonly path: string; readonly sha256: string };
  readonly definition_ids: readonly string[];
  readonly contract_kinds: readonly { readonly kind: string; readonly definition_id: string; readonly schema_ref: string }[];
  readonly language_profile_refs: readonly string[];
  readonly invariants: readonly string[];
  readonly claim_ceiling: Readonly<Record<string, boolean>>;
  readonly authority_effect: "none";
}

export interface FrozenSystemIntegrationProfileV1 {
  readonly profile: SystemIntegrationProfileV1;
  readonly profile_digest: string;
  readonly language_profiles: Readonly<Record<SupportedLanguage, { readonly value: SystemIntegrationLanguageProfileV1; readonly digest: string }>>;
}

export interface SystemIntegrationBindingManifestV1 {
  readonly schema_version: "domainspec.system-integration-binding-manifest/v1";
  readonly binding_set_id: string;
  readonly subject_ref: string;
  readonly profile: {
    readonly profile_id: "domainspec.system-integration-profile/provider-neutral-v1";
    readonly profile_digest: string;
    readonly language_profile_id: string;
    readonly language_profile_digest: string;
    readonly architecture_id: "domainspec-durable-recovery@2";
    readonly architecture_sha256: string;
  };
  readonly language: SupportedLanguage;
  readonly source_digest: string;
  readonly canonical_bindings: Readonly<Record<string, unknown>>;
  readonly runtime_guarantees_observed: false;
  readonly authority_effect: "none";
  readonly binding_digest: string;
}

export interface SystemIntegrationSelectionV1 {
  readonly profile_selector: "provider-neutral-v1";
  readonly binding_source: { readonly relative_path: string; readonly sha256: string };
  readonly manifest: SystemIntegrationBindingManifestV1;
  readonly generated_relative_path: string;
  readonly generated_content: string;
}

export interface SystemIntegrationReceiptBindingV1 {
  readonly profile_selector: "provider-neutral-v1";
  readonly binding_source: { readonly relative_path: string; readonly sha256: string };
  readonly manifest: SystemIntegrationBindingManifestV1;
  readonly generated_relative_path: string;
}
