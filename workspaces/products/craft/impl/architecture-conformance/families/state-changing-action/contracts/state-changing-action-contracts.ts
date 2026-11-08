export const OPERATION_HOSTILE_IDS = Object.freeze([
  "op/undeclared-write",
  "op/undeclared-effect",
  "op/guard-bypass",
  "op/order-swap",
  "op/atomicity-removed",
  "op/success-failure-collapse",
  "op/emitted-before-commit",
  "op/continuation-mismatch",
  "op/read-set-drift",
  "op/output-contract-overclaim",
  "op/relation-owner-evidence-stale",
  "op/relation-source-endpoint-mismatch",
  "op/relation-target-endpoint-mismatch",
  "op/materialized-without-exact-assertion",
] as const);

export type OperationHostileId = (typeof OPERATION_HOSTILE_IDS)[number];

export const OPERATION_S1_HOSTILE_IDS = Object.freeze([
  "s1/before-state-write-failure",
  "s1/between-state-and-outbox-failure",
  "s1/missing-member",
  "s1/mixed-commit",
  "s1/rollback-after-commit",
] as const);

export type OperationS1HostileId =
  (typeof OPERATION_S1_HOSTILE_IDS)[number];
export type OperationAnyHostileId = OperationHostileId | OperationS1HostileId;

export const OPERATION_FINDING_CODES = Object.freeze([
  "RMT_OP_UNDECLARED_WRITE",
  "RMT_OP_UNDECLARED_EFFECT",
  "RMT_OP_GUARD_BYPASS",
  "RMT_OP_ORDER_SWAP",
  "RMT_OP_ATOMICITY_REMOVED",
  "RMT_OP_SUCCESS_FAILURE_COLLAPSE",
  "RMT_OP_EMITTED_BEFORE_COMMIT",
  "RMT_OP_CONTINUATION_MISMATCH",
  "RMT_OP_READ_SET_DRIFT",
  "RMT_OP_OUTPUT_CONTRACT_OVERCLAIM",
  "RMT_RELATION_OWNER_EVIDENCE_STALE",
  "RMT_RELATION_SOURCE_ENDPOINT_MISMATCH",
  "RMT_RELATION_TARGET_ENDPOINT_MISMATCH",
  "RMT_RELATION_ASSERTION_REQUIRED",
  "RMT_S1_BEFORE_STATE_WRITE_FAILURE",
  "RMT_S1_STATE_OUTBOX_ATOMICITY_BREACH",
  "RMT_S1_MISSING_MEMBER",
  "RMT_S1_MIXED_COMMIT",
  "RMT_S1_ROLLBACK_AFTER_COMMIT",
] as const);

export type OperationFindingCode = (typeof OPERATION_FINDING_CODES)[number];

export const OPERATION_MUTATION_KIND = Object.freeze({
  "op/undeclared-write": "add-undeclared-write",
  "op/undeclared-effect": "add-undeclared-effect",
  "op/guard-bypass": "start-rejected-transition",
  "op/order-swap": "swap-read-write-order",
  "op/atomicity-removed": "remove-single-commit",
  "op/success-failure-collapse": "attach-success-value-to-failure",
  "op/emitted-before-commit": "move-event-before-commit",
  "op/continuation-mismatch": "mismatch-continuation-closure",
  "op/read-set-drift": "add-undeclared-read",
  "op/output-contract-overclaim": "claim-exactly-once-delivery",
  "op/relation-owner-evidence-stale": "stale-owner-evidence",
  "op/relation-source-endpoint-mismatch": "replace-source-endpoint",
  "op/relation-target-endpoint-mismatch": "replace-target-endpoint",
  "op/materialized-without-exact-assertion": "remove-exact-assertion",
} as const satisfies Readonly<Record<OperationHostileId, string>>);

export type OperationMutationKind =
  (typeof OPERATION_MUTATION_KIND)[OperationHostileId];

export const OPERATION_S1_MUTATION_KIND = Object.freeze({
  "s1/before-state-write-failure": "observe-before-state-write-failure",
  "s1/between-state-and-outbox-failure": "observe-state-outbox-gap",
  "s1/missing-member": "remove-required-member",
  "s1/mixed-commit": "observe-mixed-commit",
  "s1/rollback-after-commit": "request-rollback-after-commit",
} as const satisfies Readonly<Record<OperationS1HostileId, string>>);

export type OperationS1MutationKind =
  (typeof OPERATION_S1_MUTATION_KIND)[OperationS1HostileId];

export const OPERATION_EXPECTED_DIAGNOSTIC = Object.freeze({
  "op/undeclared-write": "RMT_OP_UNDECLARED_WRITE",
  "op/undeclared-effect": "RMT_OP_UNDECLARED_EFFECT",
  "op/guard-bypass": "RMT_OP_GUARD_BYPASS",
  "op/order-swap": "RMT_OP_ORDER_SWAP",
  "op/atomicity-removed": "RMT_OP_ATOMICITY_REMOVED",
  "op/success-failure-collapse": "RMT_OP_SUCCESS_FAILURE_COLLAPSE",
  "op/emitted-before-commit": "RMT_OP_EMITTED_BEFORE_COMMIT",
  "op/continuation-mismatch": "RMT_OP_CONTINUATION_MISMATCH",
  "op/read-set-drift": "RMT_OP_READ_SET_DRIFT",
  "op/output-contract-overclaim": "RMT_OP_OUTPUT_CONTRACT_OVERCLAIM",
  "op/relation-owner-evidence-stale": "RMT_RELATION_OWNER_EVIDENCE_STALE",
  "op/relation-source-endpoint-mismatch":
    "RMT_RELATION_SOURCE_ENDPOINT_MISMATCH",
  "op/relation-target-endpoint-mismatch":
    "RMT_RELATION_TARGET_ENDPOINT_MISMATCH",
  "op/materialized-without-exact-assertion":
    "RMT_RELATION_ASSERTION_REQUIRED",
  "s1/before-state-write-failure":
    "RMT_S1_BEFORE_STATE_WRITE_FAILURE",
  "s1/between-state-and-outbox-failure":
    "RMT_S1_STATE_OUTBOX_ATOMICITY_BREACH",
  "s1/missing-member": "RMT_S1_MISSING_MEMBER",
  "s1/mixed-commit": "RMT_S1_MIXED_COMMIT",
  "s1/rollback-after-commit": "RMT_S1_ROLLBACK_AFTER_COMMIT",
} as const satisfies Readonly<Record<OperationAnyHostileId, OperationFindingCode>>);

export type OperationRelationContractV1 = Readonly<{
  contract_id: string;
  architecture_relation_id: string;
  source_types: readonly string[];
  target_types: readonly string[];
  assertion_owner: string;
  owner_evidence_sha256: string;
}>;

export type StateChangingActionDefinitionV1 = Readonly<{
  schema_version: "StateChangingActionDefinition/v1";
  definition_id: string;
  status: "candidate-fixture";
  authorship: "owner-authored-admission-input";
  admission_ref: Readonly<{
    path: string;
    sha256: string;
  }>;
  operation_id: string;
  architecture_type_id: "architecture.OperationImplementation";
  input_contract: Readonly<{
    required: readonly string[];
    additional_inputs: false;
  }>;
  declared_reads: readonly string[];
  declared_writes: readonly string[];
  declared_external_effects: readonly string[];
  guards: readonly Readonly<{
    guard_id: string;
    current_state_version_required: true;
    controlled_effects: readonly string[];
  }>[];
  ordered_steps: readonly string[];
  atomicity: Readonly<{
    mode: "all-or-nothing";
    commit_step: string;
    partial_success: false;
  }>;
  outcome_contract: Readonly<{
    success_fields: readonly string[];
    declared_failures: readonly string[];
    success_and_failure_disjoint: true;
    exactly_once_distributed_delivery: false;
  }>;
  emitted_events: readonly Readonly<{
    event_type: string;
    tense: "past-tense";
    checkpoint: "after-commit";
  }>[];
  continuation: Readonly<{
    closure: "return-await-cancel-close-dispose-finalizer-quiescence";
    pending_effects_on_close: 0;
  }>;
  guard_rejection: Readonly<{
    failure_code: string;
    transition_started: false;
    trace: readonly string[];
  }>;
  relation_contracts: readonly OperationRelationContractV1[];
  authority_effect: "none";
}>;

export type StateChangingActionDenominatorV1 = Readonly<{
  schema_version: "StateChangingActionDenominator/v1";
  denominator_id: string;
  definition_ref: Readonly<{
    definition_id: string;
    path: string;
    sha256: string;
  }>;
  portable_contract: Readonly<{
    input_semantics: "exact-declared-input-contract";
    read_semantics: "exact-ordered-declared-reads";
    write_semantics: "exact-ordered-declared-writes";
    external_effect_semantics: "exact-declared-effects-after-commit";
    guard_semantics: "invoked-current-state-decision-controls-effects";
    atomicity_semantics: "all-or-nothing-no-partial-success";
    outcome_semantics: "typed-disjoint-success-or-failure";
    event_semantics: "past-tense-facts-after-commit";
    continuation_semantics:
      "return-await-cancel-close-dispose-finalizer-quiescence";
    observer_origin: "independent-family-fixture-not-product-target";
  }>;
  semantic_hostile_count: 10;
  relation_hostile_count: 4;
  relation_contract_count: 4;
  authority_effect: "none";
}>;

export type OperationRelationAssertionV1 = Readonly<{
  contract_id: string;
  architecture_relation_id: string;
  source_type: string;
  target_type: string;
  assertion_owner: string;
  owner_evidence_sha256: string;
  exact_assertion: boolean;
}>;

export type StateChangingActionObservationV1 = Readonly<{
  schema_version: "StateChangingActionObservation/v1";
  observation_id: string;
  case_id: "committed-success" | "guard-rejected";
  source_kind:
    | "independent-family-fixture"
    | "mutated-family-observation"
    | "target-observation";
  definition_ref: StateChangingActionDenominatorV1["definition_ref"];
  denominator_ref: Readonly<{
    denominator_id: string;
    sha256: string;
  }>;
  observer: Readonly<{
    observer_id: string;
    ownership: "independent-proof-harness";
  }>;
  operation_id: string;
  transition_started: boolean;
  inputs: Readonly<Record<string, string | number | boolean | null>>;
  read_attempts: readonly string[];
  write_attempts: readonly string[];
  external_effect_attempts: readonly string[];
  guard_evaluations: readonly Readonly<{
    guard_id: string;
    invoked: boolean;
    decision: "pass" | "fail";
    current_state_version_observed: boolean;
    controlled_effects: readonly string[];
  }>[];
  trace: readonly string[];
  atomicity: Readonly<{
    mode: "all-or-nothing" | "best-effort";
    outcome: "committed" | "rolled-back" | "partial";
  }>;
  outcome: Readonly<{
    kind: "success" | "failure";
    value: Readonly<Record<string, string | number | boolean | null>> | null;
    failure_code: string | null;
    exactly_once_distributed_delivery_claimed: boolean;
  }>;
  emitted_events: readonly Readonly<{
    event_type: string;
    tense: "past-tense" | "imperative";
    trace_ordinal: number;
  }>[];
  continuation: Readonly<{
    closure: string;
    closed: boolean;
    pending_effect_count: number;
  }>;
  relation_assertions: readonly OperationRelationAssertionV1[];
  authority_effect: "none";
  observation_sha256: string;
}>;

export type StateChangingActionObservationSetV1 = Readonly<{
  schema_version: "StateChangingActionPositiveObservations/v1";
  observations: readonly StateChangingActionObservationV1[];
  authority_effect: "none";
}>;

export type OperationBaseHostileFixtureV1 = Readonly<{
  schema_version: "StateChangingActionHostile/v1";
  hostile_id: OperationHostileId;
  hostile_class: "type-semantic" | "rel-a-evidence";
  mutation_kind: OperationMutationKind;
  expected_code: OperationFindingCode;
  fixture_owner_swu: "RMT-OP-002";
  proof_owner_swu: "RMT-OP-006" | "RMT-OP-008";
  non_noop_required: true;
  authority_effect: "none";
}>;

export type OperationS1ResidueV1 = Readonly<{
  schema_version: "OperationS1Residue/v1";
  scenario:
    | "normal"
    | "before-state-write-failure"
    | "between-state-and-outbox-failure"
    | "missing-member"
    | "mixed-commit"
    | "rollback-after-commit";
  transaction_id: string | null;
  occurrence_id: string | null;
  state_write_attempted: boolean;
  outbox_append_attempted: boolean;
  outbox_checkpoint_observed: boolean;
  transaction_aborted: boolean;
  state_durable: boolean;
  outbox_occurrence_durable: boolean;
  commit_observed: boolean;
  rollback_requested: boolean;
  history_erased: boolean;
  forward_recovery_required: boolean;
  closed_rejection: boolean;
}>;

export type OperationS1HostileFixtureV1 = Readonly<{
  schema_version: "StateChangingActionS1Hostile/v1";
  hostile_id: OperationS1HostileId;
  hostile_class: "s1-cross-boundary";
  mutation_kind: OperationS1MutationKind;
  expected_code: OperationFindingCode;
  fixture_owner_swu: "RMT-OP-002";
  proof_owner_swu: "RMT-OP-006";
  non_noop_required: true;
  category:
    | "fault-matrix:S1-F01"
    | "fault-matrix:S1-F02"
    | "decode-contract"
    | "atomicity-contract"
    | "recovery-contract";
  required_observation: string;
  required_outcome: string;
  baseline: OperationS1ResidueV1;
  mutation: Readonly<Partial<OperationS1ResidueV1>>;
  authority_effect: "none";
}>;

export type OperationHostileFixtureV1 =
  | OperationBaseHostileFixtureV1
  | OperationS1HostileFixtureV1;

export type OperationS1EvaluationV1 = Readonly<{
  schema_version: "OperationS1Evaluation/v1";
  verdict: "pass" | "reject";
  findings: readonly OperationFindingV1[];
  required_residue_observed: boolean;
  authority_effect: "none";
}>;

export type OperationFindingV1 = Readonly<{
  code: OperationFindingCode;
  expected: string | null;
  observed: string | null;
}>;

export type StateChangingActionEvaluationV1 = Readonly<{
  schema_version: "StateChangingActionEvaluation/v1";
  evaluation_id: string;
  definition_id: string;
  denominator_id: string;
  observation_id: string;
  verdict: "pass" | "fail";
  findings: readonly OperationFindingV1[];
  accounting: Readonly<{
    semantic_controls: 10;
    relation_controls: 4;
    total_controls: 14;
    failed_controls: number;
    unaccounted: 0;
  }>;
  portable_claim:
    "declared-state-change-observed-through-continuation-closure";
  authority_effect: "none";
}>;
