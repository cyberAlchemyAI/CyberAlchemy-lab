export type MappingField = Readonly<{source: string; target: string; required: boolean}>;
export type DirectionalMappingDescriptor = Readonly<{
  schema_version: "domainspec.directional-mapping/v1";
  descriptor_id: string;
  source_contract_id: string;
  target_contract_id: string;
  direction: "forward" | "reverse" | "bidirectional";
  correspondence: readonly MappingField[];
  required_source_fields: readonly string[];
  allowed_source_fields: readonly string[];
  totality: "total" | "partial-fallible";
  failure_contract_id: string;
  coercion_policy: "reject-silent";
  effect_policy: "none" | "declared-read-only";
  admission_status: "candidate";
  authority_effect: "none";
}>;
export type DirectionalMappingObservation = Readonly<{
  source_contract_id: string;
  target_contract_id: string;
  direction: DirectionalMappingDescriptor["direction"];
  observed_correspondence: readonly MappingField[];
  missing_required_fields: readonly string[];
  undeclared_extra_fields: readonly string[];
  totality: DirectionalMappingDescriptor["totality"];
  coercions: readonly string[];
  effect_policy: DirectionalMappingDescriptor["effect_policy"];
  effects: readonly string[];
  failure_outcome: Readonly<{status: "failure" | "success"; code: string | null; details: readonly string[]}>;
}>;
export type MappingRelationAssertion = Readonly<{
  contract_id: "mapping/maps-source-to-maps-from" | "mapping/maps-target-to-maps-to";
  mode: "blueprint-only" | "materialized";
  owner_evidence_sha256: string;
  current_owner_evidence_sha256: string;
  source_type: string;
  target_type: string;
  exact_assertion_id: string | null;
}>;
export type MappingFindingCode =
  | "RMT_MAP_SOURCE_TARGET_SWAP" | "RMT_MAP_DIRECTION_FLIP" | "RMT_MAP_MISSING_REQUIRED_FIELD"
  | "RMT_MAP_UNDECLARED_EXTRA_FIELD" | "RMT_MAP_CORRESPONDENCE_DRIFT" | "RMT_MAP_TOTALITY_OVERCLAIM"
  | "RMT_MAP_SILENT_COERCION" | "RMT_MAP_EFFECT_POLICY_VIOLATION" | "RMT_MAP_FAILURE_AS_SUCCESS"
  | "RMT_MAP_FAILURE_DETAIL_LOSS" | "RMT_RELATION_OWNER_EVIDENCE_STALE"
  | "RMT_RELATION_SOURCE_ENDPOINT_MISMATCH" | "RMT_RELATION_TARGET_ENDPOINT_MISMATCH" | "RMT_RELATION_ASSERTION_REQUIRED";
export type MappingEvaluation = Readonly<{
  schema_version: "domainspec.directional-mapping-evaluation/v1";
  descriptor_id: string;
  verdict: "pass" | "reject";
  findings: readonly Readonly<{code: MappingFindingCode; expected: unknown; observed: unknown}>[];
  authority_effect: "none";
}>;
