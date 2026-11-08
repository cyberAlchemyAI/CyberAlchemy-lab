import { createHash } from "node:crypto";

import {
  evaluateEffectObservationV1,
  type EffectObservationDiagnostic,
  type LockedEffectObserverRefV1,
} from "../../../kernel/evidence/effect-observation/index.js";
import {
  VALUE_COMPUTATION_DECISIONS,
  type ValueComputationDecisionId,
  type ValueComputationDefinitionV1,
  type ValueComputationDenominatorV1,
  type ValueComputationEvaluationV1,
  type ValueComputationFindingCode,
  type ValueComputationFindingV1,
  type ValueComputationObservationV1,
} from "../contracts/value-computation-contracts.js";
import {
  canonicalValueComputationJson,
  sha256CalculationInputs,
  sha256CalculationValue,
} from "../providers/decode-value-computation.js";

export type EvaluateValueComputationInput = Readonly<{
  definition: ValueComputationDefinitionV1;
  denominator: ValueComputationDenominatorV1;
  observation: ValueComputationObservationV1 | null;
  locked_observer_ref: LockedEffectObserverRefV1;
}>;

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const sha256 = (value: unknown): string => createHash("sha256")
  .update(canonicalValueComputationJson(value), "utf8")
  .digest("hex");

const decisionForCode: Readonly<Record<ValueComputationFindingCode,
ValueComputationDecisionId>> = Object.freeze({
  FAMILY_CALC_TARGET_OBSERVATION_MISSING: "target-observation-present",
  FAMILY_CALC_DEFINITION_PROVENANCE_MISMATCH: "owner-definition-provenance",
  FAMILY_CALC_BINDING_MISMATCH: "exact-descriptor-provider-binding",
  FAMILY_CALC_CASE_MISSING: "exact-case-value",
  FAMILY_CALC_CASE_UNEXPECTED: "exact-case-value",
  FAMILY_CALC_VALUE_MISMATCH: "exact-case-value",
  FAMILY_CALC_BOOLEAN_VALUE: "non-boolean-value",
  FAMILY_CALC_NONDETERMINISTIC: "fresh-process-determinism",
  FAMILY_CALC_OBSERVER_NOT_INDEPENDENT: "independent-observer-binding",
  FAMILY_CALC_EFFECT_CHANNEL_UNSUPPORTED: "complete-effect-perimeter",
  FAMILY_CALC_AMBIENT_READ_OBSERVED: "zero-forbidden-effects",
  FAMILY_CALC_EFFECT_WRITE_OBSERVED: "zero-forbidden-effects",
  FAMILY_CALC_DEFERRED_OR_ESCAPE_OBSERVED: "zero-forbidden-effects",
  FAMILY_CALC_RESULT_INCOMPLETE: "complete-result-consumption",
  FAMILY_CALC_MUTABLE_OUTPUT_OBSERVED: "complete-result-consumption",
  FAMILY_CALC_QUIESCENCE_VIOLATION: "quiescence-after-consumption",
});

const finding = (
  code: ValueComputationFindingCode,
  details: Partial<Pick<ValueComputationFindingV1,
  "case_id" | "expected" | "observed">> = {},
): ValueComputationFindingV1 => Object.freeze({
  code,
  decision_id: decisionForCode[code],
  case_id: details.case_id ?? null,
  expected: details.expected ?? null,
  observed: details.observed ?? null,
});

const effectFindingFor = (
  diagnostic: EffectObservationDiagnostic,
): ValueComputationFindingCode => {
  if (diagnostic === "EFFECT_OBSERVER_BINDING_MISMATCH"
      || diagnostic === "EFFECT_OBSERVER_SELF_ISSUED") {
    return "FAMILY_CALC_OBSERVER_NOT_INDEPENDENT";
  }
  if (diagnostic === "EFFECT_CHANNEL_MISSING"
      || diagnostic === "EFFECT_CHANNEL_UNEXPECTED"
      || diagnostic === "EFFECT_CHANNEL_DUPLICATE"
      || diagnostic === "EFFECT_CHANNEL_UNSUPPORTED"
      || diagnostic === "EFFECT_QUIESCENCE_UNSUPPORTED") {
    return "FAMILY_CALC_EFFECT_CHANNEL_UNSUPPORTED";
  }
  if (diagnostic === "EFFECT_READ_OBSERVED") {
    return "FAMILY_CALC_AMBIENT_READ_OBSERVED";
  }
  if (diagnostic === "EFFECT_WRITE_OBSERVED") {
    return "FAMILY_CALC_EFFECT_WRITE_OBSERVED";
  }
  if (diagnostic === "EFFECT_ESCAPE_OBSERVED"
      || diagnostic === "EFFECT_DEFERRED_OBSERVED") {
    return "FAMILY_CALC_DEFERRED_OR_ESCAPE_OBSERVED";
  }
  if (diagnostic === "EFFECT_RESULT_INCOMPLETE") {
    return "FAMILY_CALC_RESULT_INCOMPLETE";
  }
  if (diagnostic === "EFFECT_MUTABLE_ALIAS_OBSERVED") {
    return "FAMILY_CALC_MUTABLE_OUTPUT_OBSERVED";
  }
  return "FAMILY_CALC_QUIESCENCE_VIOLATION";
};

const resultKind = (value: unknown): "number" | "string" | "null" | "boolean" =>
  value === null ? "null" : typeof value as "number" | "string" | "boolean";

export const evaluateValueComputation = (
  input: EvaluateValueComputationInput,
): ValueComputationEvaluationV1 => {
  const {definition, denominator, observation, locked_observer_ref: lockedObserver} = input;
  const findings: ValueComputationFindingV1[] = [];
  if (observation === null) {
    findings.push(finding("FAMILY_CALC_TARGET_OBSERVATION_MISSING", {
      expected: "current target observation",
      observed: "missing",
    }));
  } else {
    if (observation.definition_ref.definition_id
        !== denominator.owner_definition_ref.definition_id
        || observation.definition_ref.path !== denominator.owner_definition_ref.path
        || observation.definition_ref.sha256 !== denominator.owner_definition_ref.sha256) {
      findings.push(finding("FAMILY_CALC_DEFINITION_PROVENANCE_MISMATCH", {
        expected: `${denominator.owner_definition_ref.definition_id}`
          + `@${denominator.owner_definition_ref.sha256}`,
        observed: `${observation.definition_ref.definition_id}`
          + `@${observation.definition_ref.sha256}`,
      }));
    }
    const effectObserver = observation.effect_observation.observer_ref;
    if (observation.binding.descriptor_id !== definition.descriptor_ref.descriptor_id
        || observation.binding.descriptor_sha256 !== definition.descriptor_ref.sha256
        || effectObserver.provider_id !== observation.binding.provider_id
        || effectObserver.provider_sha256 !== observation.binding.provider_sha256
        || observation.effect_observation.target_ref.target_id
          !== observation.target.target_id) {
      findings.push(finding("FAMILY_CALC_BINDING_MISMATCH", {
        expected: `${definition.descriptor_ref.descriptor_id}`
          + `@${definition.descriptor_ref.sha256}`,
        observed: `${observation.binding.descriptor_id}`
          + `@${observation.binding.descriptor_sha256}`,
      }));
    }

    const observedByCase = new Map(observation.cases.map((item) => [item.case_id, item]));
    const expectedByCase = new Map(definition.cases.map((item) => [item.case_id, item]));
    for (const observed of observation.cases) {
      if (!expectedByCase.has(observed.case_id)) {
        findings.push(finding("FAMILY_CALC_CASE_UNEXPECTED", {
          case_id: observed.case_id,
          observed: observed.result_sha256,
        }));
      }
    }
    for (const expected of definition.cases) {
      const observed = observedByCase.get(expected.case_id);
      if (!observed) {
        findings.push(finding("FAMILY_CALC_CASE_MISSING", {
          case_id: expected.case_id,
        }));
        continue;
      }
      const expectedInputSha = sha256CalculationInputs(expected.inputs);
      const expectedResultSha = sha256CalculationValue(expected.expected_value);
      const observedValueSha = sha256CalculationValue(observed.result_value);
      if (observed.input_sha256 !== expectedInputSha
          || observed.result_kind !== resultKind(expected.expected_value)
          || observed.result_sha256 !== observedValueSha
          || observed.result_sha256 !== expectedResultSha) {
        findings.push(finding("FAMILY_CALC_VALUE_MISMATCH", {
          case_id: expected.case_id,
          expected: expectedResultSha,
          observed: observed.result_sha256,
        }));
      }
      if (observed.result_kind === "boolean"
          || typeof observed.result_value === "boolean") {
        findings.push(finding("FAMILY_CALC_BOOLEAN_VALUE", {
          case_id: expected.case_id,
          expected: definition.output_concept.value_kind,
          observed: "boolean",
        }));
      }
      if (observed.process_isolation !== "separate-process"
          || observed.fresh_process_result_sha256 !== observed.result_sha256) {
        findings.push(finding("FAMILY_CALC_NONDETERMINISTIC", {
          case_id: expected.case_id,
          expected: observed.result_sha256,
          observed: `${observed.process_isolation}:${observed.fresh_process_result_sha256}`,
        }));
      }
    }

    const effectEvaluation = evaluateEffectObservationV1({
      observation: observation.effect_observation,
      locked_observer_ref: lockedObserver,
    });
    for (const diagnostic of effectEvaluation.diagnostics) {
      const code = effectFindingFor(diagnostic);
      if (!findings.some((item) => item.code === code)) {
        findings.push(finding(code, {
          expected: "independent complete zero-effect quiescent observation",
          observed: diagnostic,
        }));
      }
    }
  }

  const normalized = Object.freeze([...findings].sort((left, right) => compareUtf8(
    `${left.code}\u0000${left.case_id ?? ""}\u0000${left.observed ?? ""}`,
    `${right.code}\u0000${right.case_id ?? ""}\u0000${right.observed ?? ""}`,
  )));
  const failedDecisions = observation === null
    ? new Set<ValueComputationDecisionId>(VALUE_COMPUTATION_DECISIONS)
    : new Set(normalized.map(({decision_id: id}) => id));
  const declared = VALUE_COMPUTATION_DECISIONS.length;
  const denominatorRef = Object.freeze({
    denominator_id: denominator.denominator_id,
    denominator_sha256: denominator.denominator_sha256,
  });
  const observationRef = Object.freeze({
    observation_id: observation?.observation_id ?? null,
    observation_sha256: observation?.observation_sha256 ?? null,
  });
  return Object.freeze({
    schema_version: "ValueComputationEvaluation/v1" as const,
    evaluation_id: `evaluation.value-computation.${sha256({
      denominatorRef,
      observationRef,
      findings: normalized,
    })}`,
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
    portable_claim: "owner-bound-deterministic-zero-effect-value-under-declared-perimeter" as const,
    authority_effect: "none" as const,
  });
};
