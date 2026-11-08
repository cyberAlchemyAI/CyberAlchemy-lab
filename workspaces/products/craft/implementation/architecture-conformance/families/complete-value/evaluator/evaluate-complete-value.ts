import {createHash} from "node:crypto";

import {
  canonicalConstructionObservationJson,
  evaluateConstructionObservationV1,
  type ConstructionObservationDiagnostic,
  type DeclaredConstructionContractV1,
  type LockedConstructionObserverRefV1,
} from "../../../kernel/evidence/construction-observation/index.js";
import {
  COMPLETE_VALUE_DECISIONS,
  COMPLETE_VALUE_HOSTILE_CLASSES,
  type CompleteValueDecisionId,
  type CompleteValueDefinitionV1,
  type CompleteValueDenominatorV1,
  type CompleteValueEvaluationV1,
  type CompleteValueFindingCode,
  type CompleteValueFindingV1,
  type CompleteValueObservationV1,
} from "../contracts/complete-value-contracts.js";

export type EvaluateCompleteValueInput = Readonly<{
  definition: CompleteValueDefinitionV1;
  denominator: CompleteValueDenominatorV1;
  observation: CompleteValueObservationV1 | null;
  locked_observer_ref: LockedConstructionObserverRefV1;
}>;

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const sha256 = (value: unknown): string => createHash("sha256")
  .update(canonicalConstructionObservationJson(value), "utf8").digest("hex");

const DECISION_BY_CODE: Readonly<Partial<Record<CompleteValueFindingCode,
CompleteValueDecisionId>>> = Object.freeze({
  FAMILY_VALUE_FACTORY_BINDING_MISMATCH: "extension-preserves-contract",
  FAMILY_VALUE_REFERENCE_IDENTITY: "equal-tuples-equal-and-hash-equally",
  FAMILY_VALUE_PARTIAL_TUPLE_EQUALITY: "every-component-participates",
  FAMILY_VALUE_INCONGRUENT_HASH: "equal-tuples-equal-and-hash-equally",
  FAMILY_VALUE_MUTABLE_NESTED_COMPONENT: "recursive-owned-immutability",
  FAMILY_VALUE_VALIDATOR_BYPASS: "validators-before-formation",
  FAMILY_VALUE_TUPLE_CHANGING_EXTENSION: "extension-preserves-contract",
  FAMILY_VALUE_COMPONENT_PROTOCOL_MISMATCH:
    "exact-component-protocol-identity-and-digest",
  FAMILY_VALUE_INVALID_INPUT_FORMED: "validators-before-formation",
  FAMILY_VALUE_NESTED_DELEGATION_MISMATCH:
    "nested-values-delegate-owned-protocol",
  FAMILY_VALUE_CASE_LEDGER_MISMATCH: "every-component-participates",
});

const finding = (
  code: CompleteValueFindingCode,
  details: Partial<Pick<CompleteValueFindingV1, "case_id" | "component_name"
  | "expected" | "observed">> = {},
): CompleteValueFindingV1 => Object.freeze({
  code,
  decision_id: DECISION_BY_CODE[code] ?? null,
  case_id: details.case_id ?? null,
  component_name: details.component_name ?? null,
  expected: details.expected ?? null,
  observed: details.observed ?? null,
});

const codeForDiagnostic = (
  diagnostic: ConstructionObservationDiagnostic,
): CompleteValueFindingCode => {
  if (diagnostic === "CONSTRUCTION_OBSERVER_BINDING_MISMATCH"
      || diagnostic === "CONSTRUCTION_OBSERVER_SELF_ISSUED") {
    return "FAMILY_VALUE_EVIDENCE_NOT_INDEPENDENT";
  }
  if (diagnostic === "CONSTRUCTION_DEFINITION_BINDING_MISMATCH") {
    return "FAMILY_VALUE_DEFINITION_PROVENANCE_MISMATCH";
  }
  if (diagnostic === "CONSTRUCTION_FACTORY_BINDING_MISMATCH"
      || diagnostic === "CONSTRUCTION_EXTENSION_BINDING_MISMATCH") {
    return "FAMILY_VALUE_FACTORY_BINDING_MISMATCH";
  }
  if (diagnostic === "CONSTRUCTION_REFERENCE_IDENTITY_OBSERVED"
      || diagnostic === "CONSTRUCTION_EQUAL_TUPLE_UNEQUAL") {
    return "FAMILY_VALUE_REFERENCE_IDENTITY";
  }
  if (diagnostic === "CONSTRUCTION_COMPONENT_VARIANT_EQUAL"
      || diagnostic === "CONSTRUCTION_TUPLE_INCOMPLETE") {
    return "FAMILY_VALUE_PARTIAL_TUPLE_EQUALITY";
  }
  if (diagnostic === "CONSTRUCTION_EQUAL_HASH_INCONGRUENT") {
    return "FAMILY_VALUE_INCONGRUENT_HASH";
  }
  if (diagnostic === "CONSTRUCTION_RECURSIVE_IMMUTABILITY_VIOLATION") {
    return "FAMILY_VALUE_MUTABLE_NESTED_COMPONENT";
  }
  if (diagnostic === "CONSTRUCTION_VALIDATOR_ORDER_MISMATCH"
      || diagnostic === "CONSTRUCTION_FORMATION_ORDER_MISMATCH"
      || diagnostic === "CONSTRUCTION_VALID_INPUT_NOT_FORMED") {
    return "FAMILY_VALUE_VALIDATOR_BYPASS";
  }
  if (diagnostic === "CONSTRUCTION_EXTENSION_NOT_ADDITIVE"
      || diagnostic === "CONSTRUCTION_EXTENSION_CYCLE") {
    return "FAMILY_VALUE_TUPLE_CHANGING_EXTENSION";
  }
  if (diagnostic === "CONSTRUCTION_COMPONENT_PROTOCOL_MISMATCH") {
    return "FAMILY_VALUE_COMPONENT_PROTOCOL_MISMATCH";
  }
  if (diagnostic === "CONSTRUCTION_INVALID_INPUT_FORMED"
      || diagnostic === "CONSTRUCTION_FAILURE_CODE_MISMATCH") {
    return "FAMILY_VALUE_INVALID_INPUT_FORMED";
  }
  if (diagnostic === "CONSTRUCTION_NESTED_DELEGATION_MISMATCH") {
    return "FAMILY_VALUE_NESTED_DELEGATION_MISMATCH";
  }
  return "FAMILY_VALUE_CASE_LEDGER_MISMATCH";
};

const declaredContract = (
  definition: CompleteValueDefinitionV1,
): DeclaredConstructionContractV1 => Object.freeze({
  factory_ref: definition.factories.base,
  components: definition.components,
  validators: definition.validators,
  cases: Object.freeze(definition.cases.map((testCase) => Object.freeze({
    case_id: testCase.case_id,
    input_class: testCase.input_class,
    expected_components: Object.freeze(definition.components.map((component) =>
      Object.freeze({
        component_name: component.component_name,
        normalized_value_sha256:
          testCase.normalized_component_values[component.component_name]!,
      }))),
    expected_failure_codes: Object.freeze([...testCase.expected_failure_codes]),
  }))),
  equal_probe_ids: Object.freeze([definition.equality_contract.equal_probe.probe_id]),
  component_variant_probe_ids: Object.freeze(Object.fromEntries(
    definition.equality_contract.component_variants.map((variant) =>
      [variant.component_name, variant.probe_id]),
  )),
  nested_component_names: Object.freeze(definition.components
    .filter(({nested_value_object}) => nested_value_object)
    .map(({component_name}) => component_name)),
  extension_factory_ref: definition.factories.extension,
});

export const evaluateCompleteValue = (
  input: EvaluateCompleteValueInput,
): CompleteValueEvaluationV1 => {
  const {definition, denominator, observation,
    locked_observer_ref: lockedObserver} = input;
  const findings: CompleteValueFindingV1[] = [];
  if (observation === null) {
    findings.push(finding("FAMILY_VALUE_TARGET_OBSERVATION_MISSING", {
      expected: "current target observation",
      observed: "missing",
    }));
  } else {
    const expectedDefinitionRef = denominator.owner_definition_ref;
    if (canonicalConstructionObservationJson(observation.definition_ref)
        !== canonicalConstructionObservationJson(expectedDefinitionRef)) {
      findings.push(finding("FAMILY_VALUE_DEFINITION_PROVENANCE_MISMATCH", {
        expected: `${expectedDefinitionRef.definition_id}@${expectedDefinitionRef.sha256}`,
        observed: `${observation.definition_ref.definition_id}`
          + `@${observation.definition_ref.sha256}`,
      }));
    }
    const transport = evaluateConstructionObservationV1({
      locked_observer_ref: lockedObserver,
      locked_definition_ref: expectedDefinitionRef,
      declared_contract: declaredContract(definition),
      observation,
    });
    for (const diagnostic of transport.diagnostics) {
      const code = codeForDiagnostic(diagnostic);
      if (!findings.some((item) => item.code === code)) {
        findings.push(finding(code, {
          expected: "owner-declared complete-value construction contract",
          observed: diagnostic,
        }));
      }
    }
  }
  const normalized = Object.freeze([...findings].sort((left, right) => compareUtf8(
    `${left.code}\u0000${left.case_id ?? ""}\u0000${left.component_name ?? ""}`,
    `${right.code}\u0000${right.case_id ?? ""}\u0000${right.component_name ?? ""}`,
  )));
  const failedDecisions = observation === null
    ? new Set<CompleteValueDecisionId>(COMPLETE_VALUE_DECISIONS)
    : new Set(normalized.flatMap(({decision_id}) =>
      decision_id === null ? [] : [decision_id]));
  const denominatorRef = Object.freeze({
    denominator_id: denominator.denominator_id,
    denominator_sha256: denominator.denominator_sha256,
  });
  const observationRef = Object.freeze({
    observation_id: observation?.observation_id ?? null,
    observation_sha256: observation?.observation_sha256 ?? null,
  });
  return Object.freeze({
    schema_version: "CompleteValueEvaluation/v1" as const,
    evaluation_id: `evaluation.complete-value.${sha256({
      denominatorRef,
      observationRef,
      findings: normalized,
    })}`,
    denominator_ref: denominatorRef,
    observation_ref: observationRef,
    verdict: normalized.length === 0 ? "pass" as const : "fail" as const,
    findings: normalized,
    positive_decision_accounting: Object.freeze({
      declared: 7 as const,
      passed: COMPLETE_VALUE_DECISIONS.length - failedDecisions.size,
      failed: failedDecisions.size,
      unaccounted: 0 as const,
    }),
    hostile_class_accounting: Object.freeze({
      declared: 8 as const,
      represented: new Set(denominator.semantic_hostile_classes).size,
      unrepresented: COMPLETE_VALUE_HOSTILE_CLASSES.length
        - new Set(denominator.semantic_hostile_classes).size,
    }),
    portable_claim: "owner-bound-complete-immutable-value-transport-proof" as const,
    native_runtime_claim: false as const,
    collision_freedom_claim: false as const,
    authority_effect: "none" as const,
  });
};
