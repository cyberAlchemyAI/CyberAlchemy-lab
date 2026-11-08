export const LEAF_NODES = ["fact_ref", "literal", "entity_ref", "actor_ref", "state_ref"] as const;
export const UNARY_OPERATORS = ["not", "exists", "absent"] as const;
export const BINARY_OPERATORS = ["eq", "neq", "lt", "lte", "gt", "gte", "in", "contains", "and", "or"] as const;
export const SFOL_PROFILE = "sfol-v1" as const;

export type ScalarType = "string" | "integer" | "decimal" | "boolean" | "identifier" | "timestamp" | "duration" | "enum" | "reference" | "list" | "record";
export type SfolTerm =
  | { node: "fact_ref" | "entity_ref" | "actor_ref" | "state_ref"; ref: string }
  | { node: "literal"; value_type: ScalarType; value: unknown };
export type SfolFormula = SfolTerm | { operator: string; operands: SfolFormula[] };
/** @deprecated Use SfolFormula. Retained for carrier-v2 API compatibility. */
export type Expression = SfolFormula;

export interface CompilerIssue {
  code: string;
  path: string;
  message: string;
}

export class CompilationRejected extends Error {
  constructor(readonly issues: CompilerIssue[]) {
    super(issues.map((issue) => `${issue.code} at ${issue.path}: ${issue.message}`).join("\n"));
    this.name = "CompilationRejected";
  }
}

export interface NormalizedFact { id: string; subject_ref: string | null; type: ScalarType; required: boolean; owner: string }
export interface NormalizedValueObject { id: string; fields: NormalizedFact[]; equality_fields: string[]; source_refs: string[] }
export interface NormalizedEnumValue { id: string; description: string }
export interface NormalizedEnum { id: string; values: NormalizedEnumValue[]; source_refs: string[] }
export interface NormalizedRule { id: string; condition: SfolFormula | { legacy_predicate: string }; owner: string; source_refs: string[] }
export interface NormalizedEvent { id: string; payload_facts: string[]; authority_boundary_ref: string | null }
export interface NormalizedTransition { id: string; subject_ref: string; from_state_ref: string; to_state_ref: string; trigger_ref: string | null; guard_rule_refs: string[]; resulting_event_refs: string[]; authority_boundary_ref: string | null }
export interface NormalizedEffect { id: string; pattern_ref: string; integration_binding_ref: string; write_refs: string[]; event_refs: string[]; guarantee: string; failure_continuation: string; authority_boundary_ref: string }
export interface NormalizedAction { id: string; declaration_kind: "action" | "operation"; actor_refs: string[]; subject_refs: string[]; input_facts: string[]; read_refs: string[]; write_refs: string[]; effect_refs: string[]; precondition_rule_refs: string[]; permission_refs: string[]; outcome_refs: string[]; performs: Array<{ effect_ref: string; integration_binding_ref: string }>; authority_boundary_ref: string }
export interface NormalizedPermission { id: string; actor_refs: string[]; action_refs: string[]; condition: SfolFormula | { legacy_condition: string }; authority_boundary_ref: string }
export interface NormalizedExample { id: string; kind: string; expected: string; affected_rule_refs: string[] }
export type SfolUInt64Term =
  | { node: "uint64_literal"; value: string }
  | { node: "input_ref"; ref: string }
  | { operator: "add" | "subtract" | "multiply" | "divide"; operands: [SfolUInt64Term, SfolUInt64Term] };
/** @deprecated Use SfolUInt64Term. Retained for carrier-v2 API compatibility. */
export type UInt64Expression = SfolUInt64Term;
export interface NormalizedQuery { id: string; source_ref: string; input_facts: string[]; predicate: SfolFormula | null; order_by: Array<{ field_ref: string; direction: "asc" | "desc" }>; limit: number | null; projection: string[]; source_refs: string[] }
export interface NormalizedCalculation { id: string; input_facts: string[]; expression: SfolUInt64Term; rounding: "floor" | "ceil" | "reject"; source_refs: string[] }
export interface NormalizedMappingClause { target_field: string; source_field: string | null; default_value: { value_type: ScalarType; value: unknown } | null }
export interface NormalizedMapping { id: string; source_ref: string; target_ref: string; total: boolean; clauses: NormalizedMappingClause[]; source_refs: string[] }
export interface NormalizedPolicyCase { predicate: SfolFormula; target_ref: string }
export interface NormalizedPolicy { id: string; input_facts: string[]; cases: NormalizedPolicyCase[]; default_target_ref: string; source_refs: string[] }
export interface NormalizedWorkflow { id: string; scope: "intra-feature" | "cross-feature"; step_refs: string[]; source_refs: string[] }
export interface NormalizedInterface { id: string; interface_kind: "internal" | "external"; exposure_refs: string[]; source_refs: string[] }

export interface NormalizedDomain {
  schema_version: string;
  logic_profile: typeof SFOL_PROFILE | "legacy-opaque-predicate";
  domain_id: string;
  title: string;
  owners: string[];
  terms: Array<{ id: string; kind: string; meaning: string }>;
  edges: Array<{ id: string; type: string; source: string; target: string }>;
  facts: NormalizedFact[];
  value_objects: NormalizedValueObject[];
  enums: NormalizedEnum[];
  rules: NormalizedRule[];
  events: NormalizedEvent[];
  states: Array<{ id: string; subject_ref: string }>;
  transitions: NormalizedTransition[];
  effects: NormalizedEffect[];
  actions: NormalizedAction[];
  permissions: NormalizedPermission[];
  queries: NormalizedQuery[];
  calculations: NormalizedCalculation[];
  mappings: NormalizedMapping[];
  policies: NormalizedPolicy[];
  workflows: NormalizedWorkflow[];
  interfaces: NormalizedInterface[];
  examples: NormalizedExample[];
  authority_boundaries: string[];
  authority_effect: "none";
  residue: Array<{ code: string; subject_ref: string; owner_route: string; detail: string }>;
  metadata: Record<string, unknown>;
}

export interface CompilationPlan {
  model: NormalizedDomain;
  type_model: Array<{ id: string; fields: NormalizedFact[] }>;
  value_object_contracts: NormalizedValueObject[];
  enum_contracts: NormalizedEnum[];
  sfol_logic_model: { profile: typeof SFOL_PROFILE | "legacy-opaque-predicate"; formulas: NormalizedRule[]; terms: NormalizedCalculation[] };
  predicate_model: NormalizedRule[];
  event_contracts: NormalizedEvent[];
  state_machines: Array<{ subject_ref: string; states: string[]; transitions: NormalizedTransition[] }>;
  effect_contracts: NormalizedEffect[];
  action_ports: NormalizedAction[];
  operation_contracts: NormalizedAction[];
  permission_guards: NormalizedPermission[];
  query_contracts: NormalizedQuery[];
  calculation_contracts: NormalizedCalculation[];
  mapping_contracts: NormalizedMapping[];
  policy_contracts: NormalizedPolicy[];
  workflow_contracts: NormalizedWorkflow[];
  interface_contracts: NormalizedInterface[];
  test_obligations: Array<{ id: string; kind: string; expected: string; rule_refs: string[] }>;
  documentation_model: { title: string; term_count: number; rule_count: number; claim_ceiling: string };
  graph_model: { nodes: Array<{ id: string; kind: string }>; edges: Array<{ id: string; type: string; source: string; target: string }> };
  trace_ledger: Array<{ output_ref: string; source_refs: string[] }>;
  unsupported_residue: NormalizedDomain["residue"];
}

export interface CompilationResult {
  plan: CompilationPlan;
  files: Record<string, string>;
  source_digest: string;
  plan_digest: string;
  authority_effect: "none";
}
