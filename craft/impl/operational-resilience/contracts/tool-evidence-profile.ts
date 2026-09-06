export const TOOL_EVIDENCE_PROFILE_FAMILIES = Object.freeze([
  "telemetry",
  "health-failure",
  "workload",
  "fault",
  "canary-analysis",
  "deployment-observation",
  "rollback-observation",
] as const);

export const DEFERRED_TOOL_EVIDENCE_PROFILE_FAMILIES = Object.freeze([
  "infrastructure-plan",
  "compatibility",
] as const);

export const SELECTOR_VALUE_TYPES = Object.freeze([
  "string",
  "number",
  "boolean",
  "object",
  "array",
] as const);

export type ToolEvidenceProfileFamily =
  (typeof TOOL_EVIDENCE_PROFILE_FAMILIES)[number];
export type SelectorValueType = (typeof SELECTOR_VALUE_TYPES)[number];

export type DigestBoundReference = Readonly<{
  ref: string;
  version: string;
  sha256: string;
}>;

export type RoleBoundReference = DigestBoundReference &
  Readonly<{
    role: string;
  }>;

export type ToolEvidenceProfile = Readonly<{
  schema_version: "domainspec.orodi.tool-evidence-profile/v1";
  profile_id: string;
  profile_version: string;
  status: "candidate-local";
  family_id: string;
  family_inventory_ref: DigestBoundReference;
  attribute_policy_ref: DigestBoundReference;
  producer: RoleBoundReference;
  normalizer: RoleBoundReference &
    Readonly<{
      execution_mode: "offline-fixture-only";
      input_schema_ref: DigestBoundReference;
      output_schema_ref: DigestBoundReference;
      validation_receipt_schema_ref: DigestBoundReference;
    }>;
  mapping: Readonly<{
    selector: string;
    selector_value_type: SelectorValueType;
    normalized_kind: string;
    required_source_fields: readonly string[];
    required_attributes: readonly string[];
    attribute_value_templates: Readonly<Record<string, string>>;
    output_constraints: Readonly<{
      plane: "product";
      mode: "simulation" | "observation";
      allowed_normalized_fields: readonly string[];
      cardinality_budget: number;
      telemetry_accounting_required: boolean;
      independently_observed_required: boolean;
      deployment_effect_allowed: boolean;
    }>;
    missing_data_behavior: "reject";
    error_map: readonly Readonly<{
      condition: string;
      code: string;
    }>[];
    family_requirements: readonly string[];
  }>;
  admitted_control_refs: readonly string[];
  proposed_control_refs: readonly Readonly<{
    control_id: string;
    catalog_ref: DigestBoundReference;
  }>[];
  created_at: string;
  expires_at: string;
  invalidation_key_digest: string;
  execution_mode: "offline-fixture-only";
  runtime_admission: "denied";
  authority_effect: "none";
}>;

export type ToolEvidenceProfileFamilyInventory = Readonly<{
  schema_version: "domainspec.orodi.tool-evidence-profile-family-inventory/v1";
  inventory_id: "domainspec.orodi.tool-evidence-profile-families";
  inventory_version: "1.0.0-candidate-local";
  valid_families: readonly Readonly<{
    family_id: ToolEvidenceProfileFamily;
    allowed_normalized_kinds: readonly string[];
    required_safeguards: readonly string[];
    required_referent_roles: readonly string[];
    attribute_policy_sha256: string;
  }>[];
  deferred_extensions: readonly string[];
  authority_effect: "none";
}>;

export type ToolEvidenceProfileAttributePolicy = Readonly<{
  schema_version: "domainspec.orodi.tool-evidence-profile-attribute-policy/v1";
  policy_id: "domainspec.orodi.tool-evidence-profile-attributes";
  policy_version: "1.0.0-candidate-local";
  allowed_normalized_keys: readonly string[];
  forbidden_exact_keys: readonly string[];
  forbidden_prefixes: readonly string[];
  max_key_bytes: number;
  max_value_bytes: number;
  max_attribute_count: number;
  wildcards_allowed: false;
  authority_effect: "none";
}>;

export type ToolEvidenceProfileReferentInventory = Readonly<{
  schema_version: "domainspec.orodi.tool-evidence-profile-referent-inventory/v1";
  inventory_id: string;
  inventory_version: string;
  referents: readonly Readonly<{
    ref: string;
    role: string;
    name: string;
    version: string;
    sha256: string;
    bytes_utf8: string;
  }>[];
  authority_effect: "none";
}>;

export type ToolEvidenceProfileFinding = Readonly<{
  code: string;
  path: string;
  detail: string;
}>;

export type ToolEvidenceProfileValidationResult = Readonly<{
  schema_version: "domainspec.orodi.tool-evidence-profile-validation-result/v1";
  validator_id: "domainspec.orodi.tool-evidence-profile-validator";
  validator_version: "1.0.0-candidate-local";
  profile_id: string;
  profile_version: string;
  family_id: string;
  descriptor_sha256: string;
  family_inventory_sha256: string;
  attribute_policy_sha256: string;
  referent_inventory_sha256: string;
  evaluated_at: string;
  verdict: "pass" | "reject";
  profile_state: "structurally-valid" | "rejected";
  runtime_admission: "denied";
  referent_trust: "unverified";
  findings: readonly ToolEvidenceProfileFinding[];
  authority_effect: "none";
}>;

export type ToolEvidenceProfileValidationInputs = Readonly<{
  descriptor: Uint8Array | string;
  family_inventory: Uint8Array | string;
  attribute_policy: Uint8Array | string;
  referent_inventory: Uint8Array | string;
  evaluated_at: string;
}>;
