export type JsonRecord = Record<string, unknown>;

export type EvfFailureCode =
  | "SEMANTIC_SOURCE_UNADMITTED"
  | "FORMAL_PREDICATE_MISSING"
  | "PREDICATE_SCHEMA_INVALID"
  | "RUNTIME_TARGET_UNADMITTED"
  | "TARGET_BASELINE_DRIFT"
  | "EDGE_ENDPOINT_MISMATCH"
  | "EDGE_DIRECTION_MISMATCH"
  | "RELATIONSHIP_SIGNATURE_MISMATCH"
  | "SOURCE_DIGEST_STALE"
  | "GENERATED_GRAPH_STALE"
  | "OBLIGATION_COUNT_MISMATCH"
  | "OBLIGATION_ID_MISMATCH"
  | "OSPEC_OGEN_MISMATCH"
  | "PREDICATE_TYPE_INVALID"
  | "PREDICATE_OPERATOR_UNSUPPORTED"
  | "FIXTURE_INPUT_INVALID"
  | "BINDING_MISSING"
  | "BINDING_DUPLICATE"
  | "BINDING_AMBIGUOUS"
  | "BINDING_STALE"
  | "STRICT_ASSERTION_COUNT_MISMATCH"
  | "STRICT_GAP_PRESENT"
  | "RUNTIME_EXPORT_MISSING"
  | "RUNTIME_EXECUTION_FAILED"
  | "RUNTIME_OUTPUT_INVALID"
  | "RUNTIME_RESULT_MISMATCH"
  | "RESULT_ID_MISMATCH"
  | "ARTIFACT_STALE"
  | "RECEIPT_TAMPERED"
  | "SEMANTIC_BYPASS_MUTANT_SURVIVED"
  | "STRUCTURAL_MUTANT_SURVIVED"
  | "STALE_ARTIFACT_MUTANT_SURVIVED"
  | "VERIFIER_TARGET_OMITTED"
  | "S1_ACCEPTANCE_VECTOR_MISMATCH";

const FAILURE_META: Readonly<Record<EvfFailureCode, { phase: string; exit: 1 | 2 }>> = {
  SEMANTIC_SOURCE_UNADMITTED: { phase: "admission-source", exit: 2 },
  FORMAL_PREDICATE_MISSING: { phase: "admission-source", exit: 2 },
  PREDICATE_SCHEMA_INVALID: { phase: "admission-source", exit: 1 },
  RUNTIME_TARGET_UNADMITTED: { phase: "admission-source", exit: 2 },
  TARGET_BASELINE_DRIFT: { phase: "admission-source", exit: 2 },
  EDGE_ENDPOINT_MISMATCH: { phase: "structural-lineage", exit: 1 },
  EDGE_DIRECTION_MISMATCH: { phase: "structural-lineage", exit: 1 },
  RELATIONSHIP_SIGNATURE_MISMATCH: { phase: "structural-lineage", exit: 1 },
  SOURCE_DIGEST_STALE: { phase: "structural-lineage", exit: 1 },
  GENERATED_GRAPH_STALE: { phase: "structural-lineage", exit: 1 },
  OBLIGATION_COUNT_MISMATCH: { phase: "obligation-denominator", exit: 1 },
  OBLIGATION_ID_MISMATCH: { phase: "obligation-denominator", exit: 1 },
  OSPEC_OGEN_MISMATCH: { phase: "obligation-denominator", exit: 1 },
  PREDICATE_TYPE_INVALID: { phase: "typed-predicate", exit: 1 },
  PREDICATE_OPERATOR_UNSUPPORTED: { phase: "typed-predicate", exit: 1 },
  FIXTURE_INPUT_INVALID: { phase: "typed-predicate", exit: 1 },
  BINDING_MISSING: { phase: "binding", exit: 1 },
  BINDING_DUPLICATE: { phase: "binding", exit: 1 },
  BINDING_AMBIGUOUS: { phase: "binding", exit: 1 },
  BINDING_STALE: { phase: "binding", exit: 1 },
  STRICT_ASSERTION_COUNT_MISMATCH: { phase: "strict-generation", exit: 1 },
  STRICT_GAP_PRESENT: { phase: "strict-generation", exit: 1 },
  RUNTIME_EXPORT_MISSING: { phase: "execution", exit: 1 },
  RUNTIME_EXECUTION_FAILED: { phase: "execution", exit: 1 },
  RUNTIME_OUTPUT_INVALID: { phase: "execution", exit: 1 },
  RUNTIME_RESULT_MISMATCH: { phase: "execution", exit: 1 },
  RESULT_ID_MISMATCH: { phase: "execution", exit: 1 },
  ARTIFACT_STALE: { phase: "receipt-replay", exit: 1 },
  RECEIPT_TAMPERED: { phase: "receipt-replay", exit: 1 },
  SEMANTIC_BYPASS_MUTANT_SURVIVED: { phase: "mutants", exit: 1 },
  STRUCTURAL_MUTANT_SURVIVED: { phase: "mutants", exit: 1 },
  STALE_ARTIFACT_MUTANT_SURVIVED: { phase: "mutants", exit: 1 },
  VERIFIER_TARGET_OMITTED: { phase: "aggregate", exit: 1 },
  S1_ACCEPTANCE_VECTOR_MISMATCH: { phase: "aggregate", exit: 1 },
};

export class EvfS1Error extends Error {
  readonly code: EvfFailureCode;
  readonly phase: string;
  readonly exitCode: 1 | 2;

  constructor(code: EvfFailureCode, message: string) {
    super(message);
    this.name = "EvfS1Error";
    this.code = code;
    this.phase = FAILURE_META[code].phase;
    this.exitCode = FAILURE_META[code].exit;
  }
}

export function fail(code: EvfFailureCode, message: string): never {
  throw new EvfS1Error(code, message);
}

export interface ExactRef {
  readonly path: string;
  readonly sha256: string;
  readonly size_bytes: number;
}

export interface BooleanVariableNode {
  readonly kind: "variable";
  readonly name: "has_key";
  readonly value_type: "boolean";
}

export interface BooleanLiteralNode {
  readonly kind: "literal";
  readonly value_type: "boolean";
  readonly value: boolean;
}

export interface BooleanEqualityNode {
  readonly kind: "eq";
  readonly left: BooleanVariableNode;
  readonly right: BooleanLiteralNode;
}

export interface PredicateSource {
  readonly schema_version: "evf.key-door-predicate-source/v1";
  readonly source_id: "evf.key-door.predicate-source.v1";
  readonly swu_id: "SWU-GCP-001";
  readonly authority: {
    readonly kind: "owner-selectable-evf-local-semantic-source";
    readonly admission_basis: "DEC-GCP-001-R1:option-a";
    readonly claim_ceiling: "EVF-local-SWU-GCP-001-proof-only";
    readonly schema_validation_grants_authority: false;
  };
  readonly predicate: {
    readonly predicate_id: "evf.key-door.has-key.v1";
    readonly result_type: "boolean";
    readonly ast: BooleanEqualityNode;
  };
}

export interface KeyDoorCase {
  readonly case_id: "has-key-locked" | "no-key-locked-control";
  readonly vars: { readonly has_key: boolean };
  readonly call_arg: KeyDoorInput;
}

export interface KeyDoorInputSet {
  readonly schema_version: "evf.key-door-input-set/v1";
  readonly fixture_set_id: "evf.key-door.input-set.v1";
  readonly authority: "expected-free-input-only";
  readonly cases: readonly [KeyDoorCase, KeyDoorCase];
}

export interface KeyDoorInput {
  readonly has_key: boolean;
  readonly door_locked: true;
}

export interface KeyDoorOutput {
  readonly status: "unlocked" | "denied";
  readonly door_locked: boolean;
}

export interface EnforcesEdge {
  readonly edge_id: "key-and-door.edge.has-key-rule-enforces-unlock-door";
  readonly relationship: "enforces";
  readonly source_node_id: "key-and-door.HasKeyRule";
  readonly target_node_id: "key-and-door.UnlockDoor";
}

export interface KeyDoorBindingContract {
  readonly schema_version: "evf.key-door-binding-contract/v1";
  readonly binding_id: "evf.key-door.binding.v1";
  readonly obligation_id: "evf.s1.enforces.has-key.unlock-door.v1";
  readonly edge: EnforcesEdge;
  readonly predicate_ref: ExactRef;
  readonly fixture_ref: ExactRef;
  readonly runtime_contract_ref: ExactRef;
  readonly ospec_ref: ExactRef;
  readonly lineage_refs: {
    readonly relationship_registry: ExactRef;
    readonly rule_source: ExactRef;
    readonly generated_graph: ExactRef;
    readonly generated_source_manifest: ExactRef;
  };
  readonly runtime_source_binding: {
    readonly path: string;
    readonly export: "attemptUnlock";
    readonly version: 1;
    readonly pre_state: "absent";
    readonly postimage_digest_owner: "task-session-material-reconciliation";
    readonly postimage_digest_required_before_execution: true;
  };
  readonly cardinality: "exactly-one-binding-per-obligation";
}

export interface KeyDoorRuntimeContract {
  readonly schema_version: "evf.key-door-runtime-contract/v1";
  readonly runtime_id: "evf.key-door.runtime-adapter.v1";
  readonly scope: "SWU-GCP-001";
  readonly target: { readonly path: string; readonly export: "attemptUnlock"; readonly version: 1 };
  readonly transition_contract: readonly unknown[];
  readonly claim_ceiling: "harness-only-causal-proof-not-application-runtime";
}

export interface GeneratedObligation extends EnforcesEdge {
  readonly obligation_id: "evf.s1.enforces.has-key.unlock-door.v1";
  readonly predicate_id: "evf.key-door.has-key.v1";
  readonly binding_id: "evf.key-door.binding.v1";
}

export interface RuntimeObservation {
  readonly case_id: KeyDoorCase["case_id"];
  readonly expected_boolean: boolean;
  readonly observed_boolean: boolean;
  readonly output: KeyDoorOutput;
}

export const ACCEPTANCE_VECTOR = {
  O_spec: 1,
  O_gen: 1,
  T_gen: 1,
  E_run: 1,
  runtime_observations: 2,
  aggregate_assertions: 1,
  skips: 0,
  todos: 0,
  needs_formal: 0,
  orphans: 0,
  unrunnable: 0,
  mutants_required: 16,
  mutants_killed: 16,
  negative_receipts: 16,
} as const;

export const EXECUTION_CARDINALITY = {
  generated_test_id: "evf.s1.generated-test.has-key-unlock-door.v1",
  child_result_id: "evf.s1.child-result.has-key-unlock-door.v1",
  runtime_observation_case_ids: ["has-key-locked", "no-key-locked-control"],
  runtime_function_call_count: 2,
  aggregate_assertion_id: "evf.s1.aggregate.has-key-unlock-door.v1",
  aggregate_assertion_count: 1,
  aggregate_assertion_kind: "vitest-deep-equality-observed-vector-to-independent-expected-vector",
  T_gen_count_basis: "one-generated-vitest-test-id",
  E_run_count_basis: "one-joined-child-test-result-envelope-id-not-runtime-call-count",
} as const;

export const EVF_RELATIVE_ROOT =
  "projects/domainspec-v2/development/evolvable-validation-framework";

export const EVF_PATHS = {
  predicate: `${EVF_RELATIVE_ROOT}/semantic-source/key-door-predicate.v1.json`,
  fixture: `${EVF_RELATIVE_ROOT}/fixtures/SWU-GCP-001/key-door-input.v1.json`,
  binding: `${EVF_RELATIVE_ROOT}/fixtures/SWU-GCP-001/key-door-binding.v1.json`,
  runtimeContract: `${EVF_RELATIVE_ROOT}/contracts/key-door-runtime.v1.json`,
  ospec: `${EVF_RELATIVE_ROOT}/contracts/key-door-obligations.v1.json`,
  receiptSchema: `${EVF_RELATIVE_ROOT}/contracts/evolvable-validation-receipt.v1.schema.json`,
  validationContract:
    `${EVF_RELATIVE_ROOT}/refreshes/20260820T104601Z-option-b-postimage-materialization/` +
    `staging/${EVF_RELATIVE_ROOT}/work-pack/validation-contract.s1.json`,
} as const;
