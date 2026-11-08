import {
  evaluateDeclaredReadLifecycleObservationV1,
  type DeclaredReadLifecycleDiagnostic,
} from "../../../kernel/evidence/effect-observation/index.js";
import {
  READ_MODEL_QUERY_DECISIONS,
  type ReadModelQueryDecisionId,
  type ReadModelQueryEvaluationInputV1,
  type ReadModelQueryEvaluationV1,
  type ReadModelQueryFindingCode,
  type ReadModelQueryFindingV1,
} from "../contracts/read-model-contracts.js";
import {
  canonicalReadModelQueryJson,
  sha256ReadModelQueryBytes,
  sha256ReadModelQueryValue,
} from "../providers/decode-read-model.js";

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));

const decisionForCode: Readonly<Record<ReadModelQueryFindingCode,
ReadModelQueryDecisionId>> = Object.freeze({
  FAMILY_QUERY_TARGET_OBSERVATION_MISSING: "independent-complete-observation",
  FAMILY_QUERY_DEFINITION_PROVENANCE_MISMATCH: "exact-declared-read-ledger",
  FAMILY_QUERY_BINDING_MISMATCH: "independent-complete-observation",
  FAMILY_QUERY_READ_LEDGER_MISMATCH: "exact-declared-read-ledger",
  FAMILY_QUERY_RESULT_SHAPE_MISMATCH: "exact-closed-result-shape",
  FAMILY_QUERY_DECLARED_FAILURE_MISMATCH: "exact-closed-result-shape",
  FAMILY_QUERY_OBSERVER_NOT_INDEPENDENT: "independent-complete-observation",
  FAMILY_QUERY_OBSERVATION_COVERAGE_UNSUPPORTED:
    "independent-complete-observation",
  FAMILY_QUERY_WRITE_OBSERVED: "zero-writes-through-complete-lifecycle",
  FAMILY_QUERY_WRITE_RESTORE_OBSERVED:
    "zero-writes-through-complete-lifecycle",
  FAMILY_QUERY_DEFERRED_WRITE_OBSERVED:
    "zero-writes-through-complete-lifecycle",
  FAMILY_QUERY_RESULT_CONSUMPTION_INCOMPLETE:
    "zero-writes-through-complete-lifecycle",
  FAMILY_QUERY_SOURCE_UNSUPPORTED: "independent-complete-observation",
});

const finding = (
  code: ReadModelQueryFindingCode,
  expected: string | null = null,
  observed: string | null = null,
): ReadModelQueryFindingV1 => Object.freeze({
  code,
  decision_id: decisionForCode[code],
  expected,
  observed,
});

const diagnosticFinding = (
  diagnostic: DeclaredReadLifecycleDiagnostic,
): ReadModelQueryFindingCode => {
  if (diagnostic === "DECLARED_READ_LEDGER_MISMATCH" ||
      diagnostic === "DECLARED_READ_COUNT_MISMATCH") {
    return "FAMILY_QUERY_READ_LEDGER_MISMATCH";
  }
  if (diagnostic === "DECLARED_READ_OBSERVER_BINDING_MISMATCH" ||
      diagnostic === "DECLARED_READ_OBSERVER_SELF_ISSUED" ||
      diagnostic === "DECLARED_READ_TARGET_BINDING_MISMATCH") {
    return "FAMILY_QUERY_OBSERVER_NOT_INDEPENDENT";
  }
  if (diagnostic === "DECLARED_READ_WRITE_OBSERVED") {
    return "FAMILY_QUERY_WRITE_OBSERVED";
  }
  if (diagnostic === "DECLARED_READ_WRITE_THEN_RESTORE_OBSERVED") {
    return "FAMILY_QUERY_WRITE_RESTORE_OBSERVED";
  }
  if (diagnostic === "DECLARED_READ_DEFERRED_OBSERVED" ||
      diagnostic === "DECLARED_READ_ESCAPE_OBSERVED") {
    return "FAMILY_QUERY_DEFERRED_WRITE_OBSERVED";
  }
  if (diagnostic === "DECLARED_READ_RESULT_INCOMPLETE" ||
      diagnostic === "DECLARED_READ_MUTABLE_ALIAS_OBSERVED" ||
      diagnostic === "DECLARED_READ_QUIESCENCE_VIOLATION") {
    return "FAMILY_QUERY_RESULT_CONSUMPTION_INCOMPLETE";
  }
  if (diagnostic === "DECLARED_READ_SOURCE_UNSUPPORTED") {
    return "FAMILY_QUERY_SOURCE_UNSUPPORTED";
  }
  return "FAMILY_QUERY_OBSERVATION_COVERAGE_UNSUPPORTED";
};

export const evaluateReadModelQuery = (
  input: ReadModelQueryEvaluationInputV1,
): ReadModelQueryEvaluationV1 => {
  const {definition, denominator, observation, locked_observer_ref: observer,
    locked_target_ref: target} = input;
  const findings: ReadModelQueryFindingV1[] = [];
  if (observation === null) {
    findings.push(finding("FAMILY_QUERY_TARGET_OBSERVATION_MISSING",
      "current target observation", "missing"));
  } else {
    if (observation.definition_ref.definition_id !==
        denominator.owner_definition_ref.definition_id ||
        observation.definition_ref.path !==
        denominator.owner_definition_ref.path ||
        observation.definition_ref.sha256 !==
        denominator.owner_definition_ref.sha256) {
      findings.push(finding("FAMILY_QUERY_DEFINITION_PROVENANCE_MISMATCH"));
    }
    if (observation.binding.descriptor_id !==
        definition.descriptor_ref.descriptor_id ||
        observation.binding.descriptor_sha256 !==
        definition.descriptor_ref.sha256 ||
        observation.binding.provider_id !== observer.provider_id ||
        observation.binding.provider_sha256 !== observer.provider_sha256 ||
        observation.target.target_id !== target.target_id ||
        observation.target.target_sha256 !== target.target_sha256) {
      findings.push(finding("FAMILY_QUERY_BINDING_MISMATCH"));
    }

    const ownerCase = definition.cases.find(({case_id}) =>
      case_id === observation.observed_result.case_id);
    if (!ownerCase ||
        observation.observed_result.input_sha256 !==
          sha256ReadModelQueryValue(ownerCase?.inputs ?? null) ||
        observation.observed_result.result_sha256 !==
          sha256ReadModelQueryValue(observation.observed_result.result) ||
        observation.observed_result.result_sha256 !==
          sha256ReadModelQueryValue(ownerCase?.expected_result ?? null) ||
        canonicalReadModelQueryJson(observation.observed_result.result) !==
          canonicalReadModelQueryJson(ownerCase?.expected_result ?? null)) {
      findings.push(finding("FAMILY_QUERY_RESULT_SHAPE_MISMATCH"));
    }
    // RMT-QUERY-002's family denominator contains owner-authored successful
    // cases. The declared failure vocabulary is bound, but failure-path runtime
    // observations belong to later target SWUs and cannot pass as a success case.
    if (observation.observed_result.declared_failure !== null) {
      findings.push(finding("FAMILY_QUERY_DECLARED_FAILURE_MISMATCH"));
    }

    const lifecycle = evaluateDeclaredReadLifecycleObservationV1({
      locked_observer_ref: observer,
      locked_target_ref: target,
      declared_read_targets: definition.read_targets.map(({target_id, channel}) =>
        ({target_id, channel})),
      observation: observation.read_lifecycle_observation,
    });
    for (const diagnostic of lifecycle.diagnostics) {
      const code = diagnosticFinding(diagnostic);
      if (!findings.some(({code: current}) => current === code)) {
        findings.push(finding(code,
          "exact declared reads and zero writes through complete lifecycle",
          diagnostic));
      }
    }
  }

  const normalized = Object.freeze([...findings].sort((left, right) =>
    compareUtf8(`${left.code}\u0000${left.observed ?? ""}`,
      `${right.code}\u0000${right.observed ?? ""}`)));
  const failedDecisions = observation === null
    ? new Set<ReadModelQueryDecisionId>(READ_MODEL_QUERY_DECISIONS)
    : new Set(normalized.map(({decision_id}) => decision_id));
  const denominatorRef = Object.freeze({
    denominator_id: denominator.denominator_id,
    denominator_sha256: denominator.denominator_sha256,
  });
  const observationRef = Object.freeze({
    observation_id: observation?.observation_id ?? null,
    observation_sha256: observation?.observation_sha256 ?? null,
  });
  return Object.freeze({
    schema_version: "ReadModelQueryEvaluation/v1" as const,
    evaluation_id: `evaluation.read-model-query.${sha256ReadModelQueryBytes(
      canonicalReadModelQueryJson({denominatorRef, observationRef, normalized}),
    )}`,
    denominator_ref: denominatorRef,
    observation_ref: observationRef,
    verdict: normalized.length === 0 ? "pass" as const : "fail" as const,
    findings: normalized,
    positive_decision_accounting: Object.freeze({
      declared: 4 as const,
      passed: 4 - failedDecisions.size,
      failed: failedDecisions.size,
      unaccounted: 0 as const,
    }),
    portable_claim:
      "owner-bound-exact-read-model-under-declared-observed-lifecycle" as const,
    authority_effect: "none" as const,
  });
};
