import {
  OPERATION_FINDING_CODES,
  type OperationFindingCode,
  type OperationFindingV1,
  type OperationS1EvaluationV1,
  type OperationS1ResidueV1,
  type StateChangingActionDefinitionV1,
  type StateChangingActionDenominatorV1,
  type StateChangingActionEvaluationV1,
  type StateChangingActionObservationV1,
} from "../contracts/state-changing-action-contracts.js";
import {
  canonicalOperationJson,
  sha256OperationValue,
} from "../providers/decode-state-changing-action.js";

const same = (left: unknown, right: unknown): boolean =>
  canonicalOperationJson(left) === canonicalOperationJson(right);

const finding = (
  code: OperationFindingCode,
  expected: unknown = null,
  observed: unknown = null,
): OperationFindingV1 => Object.freeze({
  code,
  expected: expected === null ? null : canonicalOperationJson(expected),
  observed: observed === null ? null : canonicalOperationJson(observed),
});

const pushOnce = (
  findings: OperationFindingV1[],
  code: OperationFindingCode,
  expected: unknown = null,
  observed: unknown = null,
): void => {
  if (!findings.some((item) => item.code === code)) {
    findings.push(finding(code, expected, observed));
  }
};

const s1Reject = (scenario: string): never => {
  throw Object.assign(
    new Error(`RMT_OP_S1_RESIDUE_INCOHERENT:${scenario}`),
    {code: "RMT_OP_S1_RESIDUE_INCOHERENT"},
  );
};

const nonEmpty = (value: string | null): boolean =>
  typeof value === "string" && value.length > 0;

export const evaluateOperationS1Residue = (
  observed: OperationS1ResidueV1,
): OperationS1EvaluationV1 => {
  let code: OperationFindingCode | null = null;
  let residueObserved = false;
  if (observed.scenario === "normal") {
    residueObserved = nonEmpty(observed.transaction_id) &&
      nonEmpty(observed.occurrence_id) && !observed.transaction_aborted &&
      observed.state_write_attempted && observed.outbox_append_attempted &&
      observed.outbox_checkpoint_observed &&
      observed.state_durable && observed.outbox_occurrence_durable &&
      observed.commit_observed && !observed.rollback_requested &&
      !observed.history_erased && !observed.forward_recovery_required &&
      !observed.closed_rejection;
  } else if (observed.scenario === "before-state-write-failure") {
    code = "RMT_S1_BEFORE_STATE_WRITE_FAILURE";
    residueObserved = nonEmpty(observed.transaction_id) &&
      observed.occurrence_id === null && observed.transaction_aborted &&
      observed.state_write_attempted && !observed.outbox_append_attempted &&
      !observed.outbox_checkpoint_observed &&
      !observed.state_durable && !observed.outbox_occurrence_durable &&
      !observed.commit_observed && !observed.history_erased &&
      observed.closed_rejection;
  } else if (observed.scenario === "between-state-and-outbox-failure") {
    code = "RMT_S1_STATE_OUTBOX_ATOMICITY_BREACH";
    residueObserved = nonEmpty(observed.transaction_id) &&
      nonEmpty(observed.occurrence_id) && observed.transaction_aborted &&
      observed.state_write_attempted && !observed.outbox_append_attempted &&
      !observed.outbox_checkpoint_observed &&
      !observed.state_durable && !observed.outbox_occurrence_durable &&
      !observed.commit_observed && !observed.history_erased &&
      observed.closed_rejection;
  } else if (observed.scenario === "missing-member") {
    code = "RMT_S1_MISSING_MEMBER";
    residueObserved = (!nonEmpty(observed.transaction_id) ||
      !nonEmpty(observed.occurrence_id)) && observed.transaction_aborted &&
      !observed.state_write_attempted && !observed.outbox_append_attempted &&
      !observed.outbox_checkpoint_observed &&
      !observed.state_durable && !observed.outbox_occurrence_durable &&
      !observed.commit_observed && observed.closed_rejection;
  } else if (observed.scenario === "mixed-commit") {
    code = "RMT_S1_MIXED_COMMIT";
    residueObserved = observed.state_durable !==
      observed.outbox_occurrence_durable && observed.state_write_attempted &&
      observed.outbox_append_attempted &&
      !observed.outbox_checkpoint_observed && !observed.history_erased &&
      observed.closed_rejection;
  } else if (observed.scenario === "rollback-after-commit") {
    code = "RMT_S1_ROLLBACK_AFTER_COMMIT";
    residueObserved = observed.commit_observed && observed.state_durable &&
      observed.outbox_occurrence_durable && observed.rollback_requested &&
      observed.state_write_attempted && observed.outbox_append_attempted &&
      observed.outbox_checkpoint_observed &&
      !observed.history_erased && observed.forward_recovery_required &&
      observed.closed_rejection;
  }
  if (!residueObserved) s1Reject(observed.scenario);
  return Object.freeze({
    schema_version: "OperationS1Evaluation/v1" as const,
    verdict: code === null ? "pass" as const : "reject" as const,
    findings: Object.freeze(code === null ? [] : [finding(
      code,
      "required durable residue",
      observed,
    )]),
    required_residue_observed: true,
    authority_effect: "none" as const,
  });
};

const outputShapeValid = (
  definition: StateChangingActionDefinitionV1,
  observation: StateChangingActionObservationV1,
): boolean => {
  if (observation.outcome.exactly_once_distributed_delivery_claimed) {
    return false;
  }
  if (observation.outcome.kind !== "success" ||
      observation.outcome.value === null) {
    return true;
  }
  return same(
    Object.keys(observation.outcome.value).sort(),
    [...definition.outcome_contract.success_fields].sort(),
  );
};

const successFailureDisjoint = (
  definition: StateChangingActionDefinitionV1,
  observation: StateChangingActionObservationV1,
): boolean => {
  if (observation.outcome.kind === "success") {
    return observation.outcome.value !== null &&
      observation.outcome.failure_code === null;
  }
  return observation.outcome.value === null &&
    typeof observation.outcome.failure_code === "string" &&
    definition.outcome_contract.declared_failures.includes(
      observation.outcome.failure_code,
    );
};

export const evaluateStateChangingAction = (
  definition: StateChangingActionDefinitionV1,
  denominator: StateChangingActionDenominatorV1,
  observation: StateChangingActionObservationV1,
): StateChangingActionEvaluationV1 => {
  const findings: OperationFindingV1[] = [];
  const committedSuccess = observation.case_id === "committed-success";
  const expectedWrites = committedSuccess ? definition.declared_writes : [];
  const expectedEffects = committedSuccess
    ? definition.declared_external_effects
    : [];
  const expectedReads = committedSuccess ? definition.declared_reads : [];

  if (!same(observation.write_attempts, expectedWrites)) {
    pushOnce(
      findings,
      "RMT_OP_UNDECLARED_WRITE",
      expectedWrites,
      observation.write_attempts,
    );
  }
  if (!same(
    observation.external_effect_attempts,
    expectedEffects,
  )) {
    pushOnce(
      findings,
      "RMT_OP_UNDECLARED_EFFECT",
      expectedEffects,
      observation.external_effect_attempts,
    );
  }
  if (!same(observation.read_attempts, expectedReads)) {
    pushOnce(
      findings,
      "RMT_OP_READ_SET_DRIFT",
      expectedReads,
      observation.read_attempts,
    );
  }

  const guardsValid = definition.guards.every((declared) => {
    const observed = observation.guard_evaluations.find(
      ({guard_id}) => guard_id === declared.guard_id,
    );
    return observed?.invoked === true &&
      observed.decision === (committedSuccess ? "pass" : "fail") &&
      observed.current_state_version_observed === true &&
      same(observed.controlled_effects, declared.controlled_effects);
  }) && observation.guard_evaluations.length === definition.guards.length &&
    observation.transition_started ===
      (committedSuccess ? true : definition.guard_rejection.transition_started);
  if (!guardsValid) {
    pushOnce(
      findings,
      "RMT_OP_GUARD_BYPASS",
      definition.guards,
      observation.guard_evaluations,
    );
  }

  const expectedTrace = committedSuccess
    ? definition.ordered_steps
    : definition.guard_rejection.trace;
  if (!same(observation.trace, expectedTrace)) {
    pushOnce(
      findings,
      "RMT_OP_ORDER_SWAP",
      expectedTrace,
      observation.trace,
    );
  }

  if (observation.atomicity.mode !== definition.atomicity.mode ||
      observation.atomicity.outcome !==
        (committedSuccess ? "committed" : "rolled-back") ||
      definition.atomicity.partial_success !== false) {
    pushOnce(
      findings,
      "RMT_OP_ATOMICITY_REMOVED",
      definition.atomicity,
      observation.atomicity,
    );
  }

  if (!successFailureDisjoint(definition, observation)) {
    pushOnce(
      findings,
      "RMT_OP_SUCCESS_FAILURE_COLLAPSE",
      definition.outcome_contract,
      observation.outcome,
    );
  }

  const commitOrdinal = observation.trace.indexOf(definition.atomicity.commit_step);
  const eventsValid = committedSuccess
    ? commitOrdinal >= 0 &&
      observation.emitted_events.length === definition.emitted_events.length &&
      definition.emitted_events.every((declared) => {
        const observed = observation.emitted_events.find(
          ({event_type}) => event_type === declared.event_type,
        );
        return observed?.tense === declared.tense &&
          observed.trace_ordinal > commitOrdinal &&
          observation.trace[observed.trace_ordinal] ===
            `event:${declared.event_type}`;
      })
    : observation.emitted_events.length === 0;
  if (!eventsValid) {
    pushOnce(
      findings,
      "RMT_OP_EMITTED_BEFORE_COMMIT",
      definition.emitted_events,
      observation.emitted_events,
    );
  }

  if (observation.continuation.closure !== definition.continuation.closure ||
      observation.continuation.closed !== true ||
      observation.continuation.pending_effect_count !==
        definition.continuation.pending_effects_on_close) {
    pushOnce(
      findings,
      "RMT_OP_CONTINUATION_MISMATCH",
      definition.continuation,
      observation.continuation,
    );
  }

  if (!outputShapeValid(definition, observation)) {
    pushOnce(
      findings,
      "RMT_OP_OUTPUT_CONTRACT_OVERCLAIM",
      definition.outcome_contract,
      observation.outcome,
    );
  }

  for (const contract of definition.relation_contracts) {
    const assertion = observation.relation_assertions.find(
      ({contract_id}) => contract_id === contract.contract_id,
    );
    if (!assertion || assertion.exact_assertion !== true) {
      pushOnce(
        findings,
        "RMT_RELATION_ASSERTION_REQUIRED",
        contract.contract_id,
        assertion ?? "missing",
      );
      continue;
    }
    if (assertion.assertion_owner !== contract.assertion_owner ||
        assertion.owner_evidence_sha256 !==
          contract.owner_evidence_sha256) {
      pushOnce(
        findings,
        "RMT_RELATION_OWNER_EVIDENCE_STALE",
        {
          assertion_owner: contract.assertion_owner,
          owner_evidence_sha256: contract.owner_evidence_sha256,
        },
        {
          assertion_owner: assertion.assertion_owner,
          owner_evidence_sha256: assertion.owner_evidence_sha256,
        },
      );
    }
    if (!contract.source_types.includes(assertion.source_type)) {
      pushOnce(
        findings,
        "RMT_RELATION_SOURCE_ENDPOINT_MISMATCH",
        contract.source_types,
        assertion.source_type,
      );
    }
    if (!contract.target_types.includes(assertion.target_type)) {
      pushOnce(
        findings,
        "RMT_RELATION_TARGET_ENDPOINT_MISMATCH",
        contract.target_types,
        assertion.target_type,
      );
    }
  }
  if (observation.relation_assertions.length !==
      definition.relation_contracts.length) {
    pushOnce(
      findings,
      "RMT_RELATION_ASSERTION_REQUIRED",
      definition.relation_contracts.length,
      observation.relation_assertions.length,
    );
  }

  const orderedFindings = Object.freeze([...findings].sort((left, right) =>
    OPERATION_FINDING_CODES.indexOf(left.code) -
    OPERATION_FINDING_CODES.indexOf(right.code)));
  return Object.freeze({
    schema_version: "StateChangingActionEvaluation/v1" as const,
    evaluation_id: `evaluation.operation.${sha256OperationValue({
      definition_id: definition.definition_id,
      denominator_id: denominator.denominator_id,
      observation_sha256: observation.observation_sha256,
      findings: orderedFindings,
    })}`,
    definition_id: definition.definition_id,
    denominator_id: denominator.denominator_id,
    observation_id: observation.observation_id,
    verdict: orderedFindings.length === 0 ? "pass" as const : "fail" as const,
    findings: orderedFindings,
    accounting: Object.freeze({
      semantic_controls: 10 as const,
      relation_controls: 4 as const,
      total_controls: 14 as const,
      failed_controls: orderedFindings.length,
      unaccounted: 0 as const,
    }),
    portable_claim:
      "declared-state-change-observed-through-continuation-closure" as const,
    authority_effect: "none" as const,
  });
};
