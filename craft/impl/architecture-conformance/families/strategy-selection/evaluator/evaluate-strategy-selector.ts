import {
  evaluateEffectObservationV1,
  type EffectObservationDiagnostic,
} from "../../../kernel/evidence/effect-observation/index.js";
import {
  STRATEGY_SELECTION_DECISIONS,
  type LockedStrategyExecutionObserverRefV1,
  type StrategyExecutionObservationV1,
  type StrategySelectionDecisionId,
  type StrategySelectionEvaluationInputV1,
  type StrategySelectionEvaluationV1,
  type StrategySelectionFindingCode,
  type StrategySelectionFindingV1,
} from "../contracts/strategy-selection-contracts.js";
import {
  canonicalStrategySelectionJson,
  sha256StrategySelectionBytes,
} from "../providers/decode-strategy-selection.js";
import {
  computeStrategyExecutionObservationSha256,
  computeStrategySelectionDefinitionSha256,
  computeStrategySelectionDenominatorSha256,
  sha256SelectedStrategyIdentity,
  sha256StrategySelectionInputs,
} from "../providers/decode-strategy-selector.js";

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const same = (left: unknown, right: unknown): boolean =>
  canonicalStrategySelectionJson(left) === canonicalStrategySelectionJson(right);
const withoutDefinitionDigest = (
  value: StrategySelectionEvaluationInputV1["definition"],
) => {
  const {definition_sha256: _digest, ...body} = value;
  return body;
};
const withoutDenominatorDigest = (
  value: StrategySelectionEvaluationInputV1["denominator"],
) => {
  const {denominator_sha256: _digest, ...body} = value;
  return body;
};
const withoutExecutionDigest = (
  value: StrategyExecutionObservationV1,
) => {
  const {observation_sha256: _digest, ...body} = value;
  return body;
};

const decisionForCode: Readonly<Record<StrategySelectionFindingCode,
StrategySelectionDecisionId>> = Object.freeze({
  FAMILY_POLICY_SELECTOR_DEFINITION_PROVENANCE_INVALID:
    "owner-selector-definition-provenance",
  FAMILY_POLICY_SELECTOR_DEFINITION_BINDING_STALE:
    "owner-selector-definition-provenance",
  FAMILY_POLICY_SELECTOR_CATALOGUE_BINDING_STALE:
    "exact-current-catalogue-binding",
  FAMILY_POLICY_SELECTOR_INPUT_CONTRACT_INVALID:
    "explicit-input-facts-only",
  FAMILY_POLICY_SELECTOR_CASE_MISSING:
    "complete-owner-case-coverage",
  FAMILY_POLICY_SELECTOR_CASE_UNEXPECTED:
    "complete-owner-case-coverage",
  FAMILY_POLICY_SELECTOR_INPUT_MISMATCH:
    "explicit-input-facts-only",
  FAMILY_POLICY_SELECTOR_BRANCH_MISMATCH:
    "complete-owner-case-coverage",
  FAMILY_POLICY_SELECTOR_INPUT_IGNORED:
    "input-sensitive-branch-selection",
  FAMILY_POLICY_SELECTOR_BOOLEAN_COLLAPSE:
    "strategy-identity-not-boolean",
  FAMILY_POLICY_SELECTOR_UNKNOWN_STRATEGY:
    "owner-declared-strategy-identity",
  FAMILY_POLICY_SELECTOR_OBSERVER_NOT_INDEPENDENT:
    "independent-effect-observer-binding",
  FAMILY_POLICY_SELECTOR_EFFECT_PERIMETER_INCOMPLETE:
    "complete-effect-perimeter",
  FAMILY_POLICY_SELECTOR_AMBIENT_READ_OBSERVED:
    "zero-forbidden-effects",
  FAMILY_POLICY_SELECTOR_EFFECT_WRITE_OBSERVED:
    "zero-forbidden-effects",
  FAMILY_POLICY_SELECTOR_DEFERRED_OR_ESCAPE_OBSERVED:
    "zero-forbidden-effects",
  FAMILY_POLICY_SELECTOR_RESULT_INCOMPLETE:
    "complete-result-consumption",
  FAMILY_POLICY_SELECTOR_MUTABLE_OUTPUT_OBSERVED:
    "complete-result-consumption",
  FAMILY_POLICY_SELECTOR_QUIESCENCE_VIOLATION:
    "quiescence-after-selection",
  FAMILY_POLICY_SELECTOR_EXECUTION_TRAP_NOT_INDEPENDENT:
    "independent-strategy-execution-trap",
  FAMILY_POLICY_SELECTOR_EXECUTION_TRAP_INCOMPLETE:
    "independent-strategy-execution-trap",
  FAMILY_POLICY_SELECTOR_STRATEGY_EXECUTION_OBSERVED:
    "zero-selected-strategy-execution",
});

const finding = (
  code: StrategySelectionFindingCode,
  details: Partial<Pick<StrategySelectionFindingV1,
  "case_id" | "expected" | "observed">> = {},
): StrategySelectionFindingV1 => Object.freeze({
  code,
  decision_id: decisionForCode[code],
  case_id: details.case_id ?? null,
  expected: details.expected ?? null,
  observed: details.observed ?? null,
});

const effectFindingFor = (
  diagnostic: EffectObservationDiagnostic,
): StrategySelectionFindingCode => {
  if (diagnostic === "EFFECT_OBSERVER_BINDING_MISMATCH" ||
      diagnostic === "EFFECT_OBSERVER_SELF_ISSUED") {
    return "FAMILY_POLICY_SELECTOR_OBSERVER_NOT_INDEPENDENT";
  }
  if (diagnostic === "EFFECT_CHANNEL_MISSING" ||
      diagnostic === "EFFECT_CHANNEL_UNEXPECTED" ||
      diagnostic === "EFFECT_CHANNEL_DUPLICATE" ||
      diagnostic === "EFFECT_CHANNEL_UNSUPPORTED" ||
      diagnostic === "EFFECT_QUIESCENCE_UNSUPPORTED") {
    return "FAMILY_POLICY_SELECTOR_EFFECT_PERIMETER_INCOMPLETE";
  }
  if (diagnostic === "EFFECT_READ_OBSERVED") {
    return "FAMILY_POLICY_SELECTOR_AMBIENT_READ_OBSERVED";
  }
  if (diagnostic === "EFFECT_WRITE_OBSERVED") {
    return "FAMILY_POLICY_SELECTOR_EFFECT_WRITE_OBSERVED";
  }
  if (diagnostic === "EFFECT_ESCAPE_OBSERVED" ||
      diagnostic === "EFFECT_DEFERRED_OBSERVED") {
    return "FAMILY_POLICY_SELECTOR_DEFERRED_OR_ESCAPE_OBSERVED";
  }
  if (diagnostic === "EFFECT_RESULT_INCOMPLETE") {
    return "FAMILY_POLICY_SELECTOR_RESULT_INCOMPLETE";
  }
  if (diagnostic === "EFFECT_MUTABLE_ALIAS_OBSERVED") {
    return "FAMILY_POLICY_SELECTOR_MUTABLE_OUTPUT_OBSERVED";
  }
  return "FAMILY_POLICY_SELECTOR_QUIESCENCE_VIOLATION";
};

const executionObserverMatches = (
  locked: LockedStrategyExecutionObserverRefV1,
  observed: LockedStrategyExecutionObserverRefV1,
): boolean => same(locked, observed);

export const evaluateStrategySelector = (
  input: StrategySelectionEvaluationInputV1,
): StrategySelectionEvaluationV1 => {
  const {
    catalogue,
    definition,
    denominator,
    observation,
    locked_effect_observer_ref: lockedEffectObserver,
    locked_execution_observer_ref: lockedExecutionObserver,
    locked_selector_target_ref: lockedTarget,
  } = input;
  const findings: StrategySelectionFindingV1[] = [];
  if (definition.authorship !== "owner-authored-admission-input" ||
      definition.derivation_policy !==
        "implementation-and-generated-selections-forbidden-as-authority" ||
      computeStrategySelectionDefinitionSha256(withoutDefinitionDigest(definition)) !==
        definition.definition_sha256) {
    findings.push(finding("FAMILY_POLICY_SELECTOR_DEFINITION_PROVENANCE_INVALID"));
  }
  if (computeStrategySelectionDenominatorSha256(withoutDenominatorDigest(denominator)) !==
      denominator.denominator_sha256 ||
      denominator.owner_definition_ref.definition_id !== definition.definition_id ||
      denominator.owner_definition_ref.definition_sha256 !== definition.definition_sha256) {
    findings.push(finding("FAMILY_POLICY_SELECTOR_DEFINITION_BINDING_STALE"));
  }
  if (definition.catalogue_ref.catalogue_id !== catalogue.catalogue_id ||
      definition.catalogue_ref.catalogue_sha256 !== catalogue.catalogue_sha256 ||
      !same(denominator.owner_catalogue_ref, definition.catalogue_ref)) {
    findings.push(finding("FAMILY_POLICY_SELECTOR_CATALOGUE_BINDING_STALE"));
  }
  if (definition.branch_contract.dependency_contract !== "explicit-inputs-only" ||
      definition.input_facts.length === 0 ||
      new Set(definition.input_facts.map(({name}) => name)).size !==
        definition.input_facts.length) {
    findings.push(finding("FAMILY_POLICY_SELECTOR_INPUT_CONTRACT_INVALID"));
  }

  if (observation === null) {
    for (const decision of STRATEGY_SELECTION_DECISIONS) {
      const code = Object.entries(decisionForCode)
        .find(([, candidate]) => candidate === decision)?.[0] as
        StrategySelectionFindingCode | undefined;
      if (code && !findings.some((item) => item.decision_id === decision)) {
        findings.push(finding(code, {expected: "current selector observation", observed: "missing"}));
      }
    }
  } else {
    if (observation.definition_ref.definition_id !== definition.definition_id ||
        observation.definition_ref.definition_sha256 !== definition.definition_sha256 ||
        observation.binding.descriptor_id !== definition.descriptor_ref.descriptor_id ||
        observation.binding.descriptor_sha256 !== definition.descriptor_ref.sha256 ||
        !same(observation.target, {
          ...lockedTarget,
          language: observation.target.language,
          protocol_id: observation.target.protocol_id,
        })) {
      findings.push(finding("FAMILY_POLICY_SELECTOR_DEFINITION_BINDING_STALE"));
    }
    if (observation.catalogue_ref.catalogue_id !== definition.catalogue_ref.catalogue_id ||
        observation.catalogue_ref.catalogue_sha256 !==
          definition.catalogue_ref.catalogue_sha256) {
      findings.push(finding("FAMILY_POLICY_SELECTOR_CATALOGUE_BINDING_STALE"));
    }
    const expectedByCase = new Map(definition.cases.map((item) => [item.case_id, item]));
    const observedByCase = new Map(observation.cases.map((item) => [item.case_id, item]));
    for (const observed of observation.cases) {
      if (!expectedByCase.has(observed.case_id)) {
        findings.push(finding("FAMILY_POLICY_SELECTOR_CASE_UNEXPECTED", {
          case_id: observed.case_id,
        }));
      }
    }
    const inputFactNames = definition.input_facts.map(({name}) => name).sort(compareUtf8);
    const ownerDeclaredStrategyIds = new Set(
      definition.cases.map(({expected_strategy_id: strategyId}) => strategyId),
    );
    for (const expected of definition.cases) {
      const observed = observedByCase.get(expected.case_id);
      if (!observed) {
        findings.push(finding("FAMILY_POLICY_SELECTOR_CASE_MISSING", {
          case_id: expected.case_id,
        }));
        continue;
      }
      const expectedInputSha = sha256StrategySelectionInputs(expected.inputs);
      if (observed.input_sha256 !== expectedInputSha ||
          !same([...observed.consumed_input_facts].sort(compareUtf8), inputFactNames)) {
        findings.push(finding("FAMILY_POLICY_SELECTOR_INPUT_MISMATCH", {
          case_id: expected.case_id,
          expected: expectedInputSha,
          observed: observed.input_sha256,
        }));
      }
      if (observed.branch_id !== expected.expected_branch_id ||
          observed.selected_sha256 !==
            sha256SelectedStrategyIdentity(observed.selected_strategy_id)) {
        findings.push(finding("FAMILY_POLICY_SELECTOR_BRANCH_MISMATCH", {
          case_id: expected.case_id,
          expected: expected.expected_branch_id,
          observed: observed.branch_id,
        }));
      }
      if (observed.selected_kind === "boolean" ||
          typeof observed.selected_strategy_id === "boolean") {
        findings.push(finding("FAMILY_POLICY_SELECTOR_BOOLEAN_COLLAPSE", {
          case_id: expected.case_id,
          expected: expected.expected_strategy_id,
          observed: String(observed.selected_strategy_id),
        }));
      } else if (observed.selected_strategy_id !== expected.expected_strategy_id ||
          !ownerDeclaredStrategyIds.has(observed.selected_strategy_id)) {
        findings.push(finding("FAMILY_POLICY_SELECTOR_UNKNOWN_STRATEGY", {
          case_id: expected.case_id,
          expected: expected.expected_strategy_id,
          observed: observed.selected_strategy_id,
        }));
      }
    }
    for (const pair of definition.sensitivity_pairs) {
      const left = observedByCase.get(pair.left_case_id);
      const right = observedByCase.get(pair.right_case_id);
      if (!left || !right ||
          left.selected_strategy_id === right.selected_strategy_id) {
        findings.push(finding("FAMILY_POLICY_SELECTOR_INPUT_IGNORED", {
          expected: `${pair.changed_input_fact}:selection-change`,
          observed: left && right
            ? `${String(left.selected_strategy_id)}:${String(right.selected_strategy_id)}`
            : "missing-controlled-pair",
        }));
      }
    }

    const effect = observation.effect_observation;
    if (!same(effect.target_ref, lockedTarget) ||
        effect.observer_ref.provider_id !== observation.binding.provider_id ||
        effect.observer_ref.provider_sha256 !== observation.binding.provider_sha256) {
      findings.push(finding("FAMILY_POLICY_SELECTOR_OBSERVER_NOT_INDEPENDENT"));
    }
    const effectEvaluation = evaluateEffectObservationV1({
      locked_observer_ref: lockedEffectObserver,
      observation: effect,
    });
    for (const diagnostic of effectEvaluation.diagnostics) {
      const code = effectFindingFor(diagnostic);
      if (!findings.some((item) => item.code === code)) {
        findings.push(finding(code, {
          expected: "complete independent zero-effect quiescent observation",
          observed: diagnostic,
        }));
      }
    }

    const execution = observation.strategy_execution_observation;
    if (computeStrategyExecutionObservationSha256(withoutExecutionDigest(execution)) !==
        execution.observation_sha256 ||
        !executionObserverMatches(lockedExecutionObserver, execution.observer_ref) ||
        execution.observer_ref.owner_ref === execution.observer_ref.provider_id ||
        execution.observer_ref.provider_id !== observation.binding.provider_id ||
        execution.observer_ref.provider_sha256 !== observation.binding.provider_sha256 ||
        !same(execution.target_ref, lockedTarget)) {
      findings.push(finding("FAMILY_POLICY_SELECTOR_EXECUTION_TRAP_NOT_INDEPENDENT"));
    }
    const expectedCovered = [...new Set(
      definition.cases.map(({expected_strategy_id: strategyId}) => strategyId),
    )].sort(compareUtf8);
    if (execution.coverage !== "all-owner-declared-strategies" ||
        !same([...execution.covered_strategy_ids].sort(compareUtf8), expectedCovered)) {
      findings.push(finding("FAMILY_POLICY_SELECTOR_EXECUTION_TRAP_INCOMPLETE", {
        expected: expectedCovered.join(","),
        observed: execution.covered_strategy_ids.join(","),
      }));
    }
    if (execution.attempt_count !== 0 || execution.completion_count !== 0 ||
        execution.attempted_strategy_ids.length !== 0) {
      findings.push(finding("FAMILY_POLICY_SELECTOR_STRATEGY_EXECUTION_OBSERVED", {
        expected: "zero-attempts-and-zero-completions",
        observed: `${execution.attempt_count}:${execution.completion_count}:` +
          execution.attempted_strategy_ids.join(","),
      }));
    }
  }

  const normalized = Object.freeze([...findings].sort((left, right) => compareUtf8(
    `${left.code}\u0000${left.case_id ?? ""}\u0000${left.observed ?? ""}`,
    `${right.code}\u0000${right.case_id ?? ""}\u0000${right.observed ?? ""}`,
  )));
  const failedDecisions = new Set(normalized.map(({decision_id: id}) => id));
  const declared = STRATEGY_SELECTION_DECISIONS.length;
  const denominatorRef = Object.freeze({
    denominator_id: denominator.denominator_id,
    denominator_sha256: denominator.denominator_sha256,
  });
  const observationRef = Object.freeze({
    observation_id: observation?.observation_id ?? null,
    observation_sha256: observation?.observation_sha256 ?? null,
  });
  const evaluationCore = {
    schema_version: "StrategySelectionEvaluation/v1" as const,
    denominator_ref: denominatorRef,
    observation_ref: observationRef,
    verdict: normalized.length === 0 ? "pass" as const : "fail" as const,
    findings: normalized,
    positive_decision_accounting: Object.freeze({
      declared,
      passed: declared - failedDecisions.size,
      failed: failedDecisions.size,
      unaccounted: 0 as const,
    }),
    portable_claim:
      "owner-bound-input-sensitive-zero-effect-strategy-identity-selection-without-strategy-execution" as const,
    authority_effect: "none" as const,
  };
  return Object.freeze({
    ...evaluationCore,
    evaluation_id: `evaluation.strategy-selector.${sha256StrategySelectionBytes(
      canonicalStrategySelectionJson(evaluationCore),
    )}`,
  });
};
