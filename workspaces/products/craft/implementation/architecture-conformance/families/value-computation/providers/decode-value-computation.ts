import { createHash } from "node:crypto";

import {
  decodeEffectObservationV1,
} from "../../../kernel/evidence/effect-observation/index.js";
import {
  VALUE_COMPUTATION_DECISIONS,
  VALUE_COMPUTATION_MUTATION_KINDS,
  type CalculationValueV1,
  type ValueComputationCaseV1,
  type ValueComputationDefinitionV1,
  type ValueComputationDenominatorV1,
  type ValueComputationFindingCode,
  type ValueComputationMutationCatalogueV1,
  type ValueComputationMutationKind,
  type ValueComputationMutationV1,
  type ValueComputationObservationV1,
  type ValueComputationObservedCaseV1,
} from "../contracts/value-computation-contracts.js";

type JsonObject = Record<string, unknown>;

const fail = (code: string): never => {
  const error = Object.assign(new Error(code), {code});
  error.name = "ValueComputationDecodeError";
  throw error;
};
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const isObject = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const expectObject = (value: unknown, code: string): JsonObject =>
  isObject(value) ? value : fail(code);
const expectString = (value: unknown, code: string): string =>
  typeof value === "string" && value.length > 0 ? value : fail(code);
const expectSha256 = (value: unknown, code: string): string => {
  const digest = expectString(value, code);
  return /^[a-f0-9]{64}$/u.test(digest) ? digest : fail(code);
};
const expectBoolean = (value: unknown, expected: boolean, code: string): boolean =>
  value === expected ? value : fail(code);
const exactKeys = (source: JsonObject, keys: readonly string[], code: string): void => {
  const actual = Object.keys(source).sort(compareUtf8);
  const expected = [...keys].sort(compareUtf8);
  if (actual.length !== expected.length
      || actual.some((key, index) => key !== expected[index])) fail(code);
};
const parseJson = (bytes: string, code: string): JsonObject => {
  try {
    return expectObject(JSON.parse(bytes), code);
  } catch (error) {
    if (isObject(error) && error.name === "ValueComputationDecodeError") throw error;
    return fail(code);
  }
};
const canonicalize = (value: unknown): unknown => Array.isArray(value)
  ? value.map(canonicalize)
  : isObject(value)
    ? Object.fromEntries(Object.entries(value)
      .sort(([left], [right]) => compareUtf8(left, right))
      .map(([key, child]) => [key, canonicalize(child)]))
    : value;

export const canonicalValueComputationJson = (value: unknown): string =>
  JSON.stringify(canonicalize(value));
export const sha256ValueComputationBytes = (bytes: string): string =>
  createHash("sha256").update(bytes, "utf8").digest("hex");
const sha256Json = (value: unknown): string =>
  sha256ValueComputationBytes(canonicalValueComputationJson(value));
export const sha256CalculationValue = (value: unknown): string => sha256Json(value);
export const sha256CalculationInputs = (
  value: Readonly<Record<string, CalculationValueV1>>,
): string => sha256Json(value);

const unique = (values: readonly string[], code: string): void => {
  if (new Set(values).size !== values.length) fail(code);
};
const decodeCalculationValue = (value: unknown, code: string): CalculationValueV1 =>
  value === null || typeof value === "string"
    || (typeof value === "number" && Number.isSafeInteger(value))
    ? value as CalculationValueV1
    : fail(code);
const decodeInputs = (value: unknown, code: string): Readonly<Record<string, CalculationValueV1>> => {
  const source = expectObject(value, code);
  if (Object.keys(source).length === 0) fail(code);
  return Object.freeze(Object.fromEntries(Object.entries(source).map(([key, child]) => [
    expectString(key, code),
    decodeCalculationValue(child, code),
  ])));
};
const decodeCase = (value: unknown): ValueComputationCaseV1 => {
  const source = expectObject(value, "FAMILY_CALC_DEFINITION_CASE_SHAPE_INVALID");
  exactKeys(source, ["case_id", "inputs", "expected_value"],
    "FAMILY_CALC_DEFINITION_CASE_SHAPE_INVALID");
  return Object.freeze({
    case_id: expectString(source.case_id, "FAMILY_CALC_DEFINITION_CASE_ID_INVALID"),
    inputs: decodeInputs(source.inputs, "FAMILY_CALC_DEFINITION_INPUT_INVALID"),
    expected_value: decodeCalculationValue(source.expected_value,
      "FAMILY_CALC_DEFINITION_VALUE_INVALID"),
  });
};

export const decodeValueComputationDefinitionV1 = (
  bytes: string,
  expectedDescriptorPath: string,
  descriptorBytes: string,
): ValueComputationDefinitionV1 => {
  const source = parseJson(bytes, "FAMILY_CALC_DEFINITION_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "definition_id", "status", "authorship", "derivation_policy",
    "descriptor_ref", "input_concepts", "output_concept", "cases", "authority_effect",
  ], "FAMILY_CALC_DEFINITION_SHAPE_INVALID");
  if (source.schema_version !== "ValueComputationDefinition/v1"
      || source.status !== "candidate-fixture"
      || source.authorship !== "owner-authored-admission-input"
      || source.derivation_policy
        !== "implementation-and-generated-results-forbidden-as-authority"
      || source.authority_effect !== "none") {
    return fail("FAMILY_CALC_DEFINITION_POLICY_INVALID");
  }
  const descriptor = expectObject(source.descriptor_ref,
    "FAMILY_CALC_DEFINITION_DESCRIPTOR_REF_INVALID");
  exactKeys(descriptor, ["descriptor_id", "path", "sha256"],
    "FAMILY_CALC_DEFINITION_DESCRIPTOR_REF_INVALID");
  if (descriptor.path !== expectedDescriptorPath
      || expectSha256(descriptor.sha256,
        "FAMILY_CALC_DEFINITION_DESCRIPTOR_REF_INVALID")
        !== sha256ValueComputationBytes(descriptorBytes)) {
    return fail("FAMILY_CALC_DEFINITION_DESCRIPTOR_REF_STALE");
  }
  if (!Array.isArray(source.input_concepts) || source.input_concepts.length === 0
      || !Array.isArray(source.cases) || source.cases.length < 2) {
    return fail("FAMILY_CALC_DEFINITION_POLICY_INVALID");
  }
  const inputConcepts = source.input_concepts.map((value) => {
    const item = expectObject(value, "FAMILY_CALC_DEFINITION_INPUT_CONCEPT_INVALID");
    exactKeys(item, ["name", "concept_id", "value_kind"],
      "FAMILY_CALC_DEFINITION_INPUT_CONCEPT_INVALID");
    if (item.value_kind !== "integer" && item.value_kind !== "string") {
      return fail("FAMILY_CALC_DEFINITION_INPUT_CONCEPT_INVALID");
    }
    return Object.freeze({
      name: expectString(item.name, "FAMILY_CALC_DEFINITION_INPUT_CONCEPT_INVALID"),
      concept_id: expectString(item.concept_id,
        "FAMILY_CALC_DEFINITION_INPUT_CONCEPT_INVALID"),
      value_kind: item.value_kind,
    });
  });
  unique(inputConcepts.map(({name}) => name), "FAMILY_CALC_DEFINITION_INPUT_DUPLICATE");
  const output = expectObject(source.output_concept,
    "FAMILY_CALC_DEFINITION_OUTPUT_CONCEPT_INVALID");
  exactKeys(output, ["concept_id", "value_kind", "boolean_forbidden"],
    "FAMILY_CALC_DEFINITION_OUTPUT_CONCEPT_INVALID");
  if ((output.value_kind !== "integer" && output.value_kind !== "string")
      || !expectBoolean(output.boolean_forbidden, true,
        "FAMILY_CALC_DEFINITION_OUTPUT_CONCEPT_INVALID")) {
    return fail("FAMILY_CALC_DEFINITION_OUTPUT_CONCEPT_INVALID");
  }
  const cases = source.cases.map(decodeCase);
  unique(cases.map(({case_id: id}) => id), "FAMILY_CALC_DEFINITION_CASE_DUPLICATE");
  const inputNames = inputConcepts.map(({name}) => name).sort(compareUtf8);
  for (const testCase of cases) {
    if (JSON.stringify(Object.keys(testCase.inputs).sort(compareUtf8))
      !== JSON.stringify(inputNames)) fail("FAMILY_CALC_DEFINITION_CASE_INPUT_SET_INVALID");
  }
  return Object.freeze({
    schema_version: "ValueComputationDefinition/v1" as const,
    definition_id: expectString(source.definition_id, "FAMILY_CALC_DEFINITION_ID_INVALID"),
    status: "candidate-fixture" as const,
    authorship: "owner-authored-admission-input" as const,
    derivation_policy: "implementation-and-generated-results-forbidden-as-authority" as const,
    descriptor_ref: Object.freeze({
      descriptor_id: expectString(descriptor.descriptor_id,
        "FAMILY_CALC_DEFINITION_DESCRIPTOR_REF_INVALID"),
      path: expectedDescriptorPath,
      sha256: expectSha256(descriptor.sha256,
        "FAMILY_CALC_DEFINITION_DESCRIPTOR_REF_INVALID"),
    }),
    input_concepts: Object.freeze(inputConcepts),
    output_concept: Object.freeze({
      concept_id: expectString(output.concept_id,
        "FAMILY_CALC_DEFINITION_OUTPUT_CONCEPT_INVALID"),
      value_kind: output.value_kind,
      boolean_forbidden: true as const,
    }),
    cases: Object.freeze(cases),
    authority_effect: "none" as const,
  });
};

const denominatorBody = (
  value: Omit<ValueComputationDenominatorV1, "denominator_sha256">,
): unknown => ({
  ...value,
  positive_decisions: [...value.positive_decisions].sort(compareUtf8),
});
export const computeValueComputationDenominatorSha256 = (
  value: Omit<ValueComputationDenominatorV1, "denominator_sha256">,
): string => sha256Json(denominatorBody(value));

export const decodeValueComputationDenominatorV1 = (
  bytes: string,
  ownerDefinitionBytes: string,
  ownerDefinition: ValueComputationDefinitionV1,
  expectedOwnerPath: string,
): ValueComputationDenominatorV1 => {
  const source = parseJson(bytes, "FAMILY_CALC_DENOMINATOR_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "denominator_id", "owner_definition_ref", "portable_contract",
    "positive_decisions", "authority_effect", "denominator_sha256",
  ], "FAMILY_CALC_DENOMINATOR_SHAPE_INVALID");
  if (source.schema_version !== "ValueComputationDenominator/v1"
      || source.authority_effect !== "none") {
    return fail("FAMILY_CALC_DENOMINATOR_POLICY_INVALID");
  }
  const ownerRef = expectObject(source.owner_definition_ref,
    "FAMILY_CALC_DENOMINATOR_OWNER_REF_INVALID");
  exactKeys(ownerRef, ["definition_id", "path", "sha256"],
    "FAMILY_CALC_DENOMINATOR_OWNER_REF_INVALID");
  const ownerSha = expectSha256(ownerRef.sha256,
    "FAMILY_CALC_DENOMINATOR_OWNER_REF_INVALID");
  if (ownerRef.definition_id !== ownerDefinition.definition_id
      || ownerRef.path !== expectedOwnerPath
      || ownerSha !== sha256ValueComputationBytes(ownerDefinitionBytes)) {
    return fail("FAMILY_CALC_DENOMINATOR_OWNER_REF_STALE");
  }
  const portable = expectObject(source.portable_contract,
    "FAMILY_CALC_DENOMINATOR_POLICY_INVALID");
  exactKeys(portable, [
    "return_semantics", "dependency_contract", "effect_contract", "determinism",
    "result_consumption", "quiescence", "observer_origin",
  ], "FAMILY_CALC_DENOMINATOR_POLICY_INVALID");
  if (portable.return_semantics !== "declared-non-boolean-value"
      || portable.dependency_contract !== "explicit-only"
      || portable.effect_contract !== "zero-observed-forbidden-effects"
      || portable.determinism !== "equal-results-across-two-fresh-processes"
      || portable.result_consumption !== "complete-before-close"
      || portable.quiescence !== "required-after-consumption"
      || portable.observer_origin !== "locked-harness-owned-not-provider") {
    return fail("FAMILY_CALC_DENOMINATOR_POLICY_INVALID");
  }
  if (!Array.isArray(source.positive_decisions)) {
    return fail("FAMILY_CALC_DENOMINATOR_DECISIONS_INVALID");
  }
  const decisions = source.positive_decisions.map((value) =>
    expectString(value, "FAMILY_CALC_DENOMINATOR_DECISIONS_INVALID"));
  const expected = [...VALUE_COMPUTATION_DECISIONS].sort(compareUtf8);
  if (JSON.stringify([...decisions].sort(compareUtf8)) !== JSON.stringify(expected)) {
    return fail("FAMILY_CALC_DENOMINATOR_DECISIONS_INVALID");
  }
  const withoutDigest = {
    schema_version: "ValueComputationDenominator/v1" as const,
    denominator_id: expectString(source.denominator_id,
      "FAMILY_CALC_DENOMINATOR_ID_INVALID"),
    owner_definition_ref: Object.freeze({
      definition_id: ownerDefinition.definition_id,
      path: expectedOwnerPath,
      sha256: ownerSha,
    }),
    portable_contract: Object.freeze({
      return_semantics: "declared-non-boolean-value" as const,
      dependency_contract: "explicit-only" as const,
      effect_contract: "zero-observed-forbidden-effects" as const,
      determinism: "equal-results-across-two-fresh-processes" as const,
      result_consumption: "complete-before-close" as const,
      quiescence: "required-after-consumption" as const,
      observer_origin: "locked-harness-owned-not-provider" as const,
    }),
    positive_decisions: Object.freeze([...VALUE_COMPUTATION_DECISIONS]),
    authority_effect: "none" as const,
  };
  const digest = expectSha256(source.denominator_sha256,
    "FAMILY_CALC_DENOMINATOR_DIGEST_INVALID");
  if (digest !== computeValueComputationDenominatorSha256(withoutDigest)) {
    return fail("FAMILY_CALC_DENOMINATOR_DIGEST_STALE");
  }
  return Object.freeze({...withoutDigest, denominator_sha256: digest});
};

const observationBody = (
  value: Omit<ValueComputationObservationV1, "observation_sha256">,
): unknown => ({
  ...value,
  cases: [...value.cases].sort((left, right) => compareUtf8(left.case_id, right.case_id)),
});
export const computeValueComputationObservationSha256 = (
  value: Omit<ValueComputationObservationV1, "observation_sha256">,
): string => sha256Json(observationBody(value));
export const mintValueComputationObservationV1 = (
  value: Omit<ValueComputationObservationV1, "observation_sha256">,
): ValueComputationObservationV1 => Object.freeze({
  ...value,
  target: Object.freeze({...value.target}),
  definition_ref: Object.freeze({...value.definition_ref}),
  binding: Object.freeze({...value.binding}),
  cases: Object.freeze(value.cases.map((item) => Object.freeze({...item}))),
  effect_observation: value.effect_observation,
  observation_sha256: computeValueComputationObservationSha256(value),
});

const decodeObservedCase = (value: unknown): ValueComputationObservedCaseV1 => {
  const source = expectObject(value, "FAMILY_CALC_OBSERVATION_CASE_SHAPE_INVALID");
  exactKeys(source, [
    "case_id", "input_sha256", "result_kind", "result_value", "result_sha256",
    "fresh_process_result_sha256", "process_isolation",
  ], "FAMILY_CALC_OBSERVATION_CASE_SHAPE_INVALID");
  if (!["number", "string", "null", "boolean"].includes(String(source.result_kind))
      || (source.process_isolation !== "separate-process"
        && source.process_isolation !== "same-process")) {
    return fail("FAMILY_CALC_OBSERVATION_CASE_POLICY_INVALID");
  }
  const resultValue = typeof source.result_value === "boolean"
    ? source.result_value
    : decodeCalculationValue(source.result_value,
      "FAMILY_CALC_OBSERVATION_CASE_VALUE_INVALID");
  return Object.freeze({
    case_id: expectString(source.case_id, "FAMILY_CALC_OBSERVATION_CASE_ID_INVALID"),
    input_sha256: expectSha256(source.input_sha256,
      "FAMILY_CALC_OBSERVATION_CASE_DIGEST_INVALID"),
    result_kind: source.result_kind as ValueComputationObservedCaseV1["result_kind"],
    result_value: resultValue,
    result_sha256: expectSha256(source.result_sha256,
      "FAMILY_CALC_OBSERVATION_CASE_DIGEST_INVALID"),
    fresh_process_result_sha256: expectSha256(source.fresh_process_result_sha256,
      "FAMILY_CALC_OBSERVATION_CASE_DIGEST_INVALID"),
    process_isolation: source.process_isolation,
  });
};

export const decodeValueComputationObservationV1 = (
  bytes: string,
): ValueComputationObservationV1 => {
  const source = parseJson(bytes, "FAMILY_CALC_OBSERVATION_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "observation_id", "source_kind", "target", "definition_ref",
    "binding", "cases", "effect_observation", "authority_effect", "observation_sha256",
  ], "FAMILY_CALC_OBSERVATION_SHAPE_INVALID");
  if (source.schema_version !== "ValueComputationObservation/v1"
      || !["independent-family-fixture", "target-observation",
        "mutated-family-observation"].includes(String(source.source_kind))
      || source.authority_effect !== "none" || !Array.isArray(source.cases)) {
    return fail("FAMILY_CALC_OBSERVATION_POLICY_INVALID");
  }
  const target = expectObject(source.target, "FAMILY_CALC_OBSERVATION_TARGET_INVALID");
  exactKeys(target, ["target_id", "language", "protocol_id"],
    "FAMILY_CALC_OBSERVATION_TARGET_INVALID");
  if (!["family-fixture", "typescript", "python", "rust"]
    .includes(String(target.language))) fail("FAMILY_CALC_OBSERVATION_TARGET_INVALID");
  const definitionRef = expectObject(source.definition_ref,
    "FAMILY_CALC_OBSERVATION_DEFINITION_REF_INVALID");
  exactKeys(definitionRef, ["definition_id", "path", "sha256"],
    "FAMILY_CALC_OBSERVATION_DEFINITION_REF_INVALID");
  const binding = expectObject(source.binding, "FAMILY_CALC_OBSERVATION_BINDING_INVALID");
  exactKeys(binding, ["descriptor_id", "descriptor_sha256", "provider_id", "provider_sha256"],
    "FAMILY_CALC_OBSERVATION_BINDING_INVALID");
  const cases = source.cases.map(decodeObservedCase);
  unique(cases.map(({case_id: id}) => id), "FAMILY_CALC_OBSERVATION_CASE_DUPLICATE");
  const withoutDigest = {
    schema_version: "ValueComputationObservation/v1" as const,
    observation_id: expectString(source.observation_id,
      "FAMILY_CALC_OBSERVATION_ID_INVALID"),
    source_kind: source.source_kind as ValueComputationObservationV1["source_kind"],
    target: Object.freeze({
      target_id: expectString(target.target_id, "FAMILY_CALC_OBSERVATION_TARGET_INVALID"),
      language: target.language as ValueComputationObservationV1["target"]["language"],
      protocol_id: expectString(target.protocol_id,
        "FAMILY_CALC_OBSERVATION_TARGET_INVALID"),
    }),
    definition_ref: Object.freeze({
      definition_id: expectString(definitionRef.definition_id,
        "FAMILY_CALC_OBSERVATION_DEFINITION_REF_INVALID"),
      path: expectString(definitionRef.path,
        "FAMILY_CALC_OBSERVATION_DEFINITION_REF_INVALID"),
      sha256: expectSha256(definitionRef.sha256,
        "FAMILY_CALC_OBSERVATION_DEFINITION_REF_INVALID"),
    }),
    binding: Object.freeze({
      descriptor_id: expectString(binding.descriptor_id,
        "FAMILY_CALC_OBSERVATION_BINDING_INVALID"),
      descriptor_sha256: expectSha256(binding.descriptor_sha256,
        "FAMILY_CALC_OBSERVATION_BINDING_INVALID"),
      provider_id: expectString(binding.provider_id,
        "FAMILY_CALC_OBSERVATION_BINDING_INVALID"),
      provider_sha256: expectSha256(binding.provider_sha256,
        "FAMILY_CALC_OBSERVATION_BINDING_INVALID"),
    }),
    cases: Object.freeze(cases),
    effect_observation: decodeEffectObservationV1(
      canonicalValueComputationJson(source.effect_observation),
    ),
    authority_effect: "none" as const,
  };
  const digest = expectSha256(source.observation_sha256,
    "FAMILY_CALC_OBSERVATION_DIGEST_INVALID");
  if (digest !== computeValueComputationObservationSha256(withoutDigest)) {
    return fail("FAMILY_CALC_OBSERVATION_DIGEST_STALE");
  }
  return Object.freeze({...withoutDigest, observation_sha256: digest});
};

const mutationBody = (
  value: Omit<ValueComputationMutationCatalogueV1, "catalogue_sha256">,
): unknown => ({
  ...value,
  mutations: [...value.mutations].sort((left, right) =>
    compareUtf8(left.mutation_id, right.mutation_id)),
});
export const computeValueComputationMutationCatalogueSha256 = (
  value: Omit<ValueComputationMutationCatalogueV1, "catalogue_sha256">,
): string => sha256Json(mutationBody(value));
export const decodeValueComputationMutationCatalogueV1 = (
  bytes: string,
  denominator: ValueComputationDenominatorV1,
): ValueComputationMutationCatalogueV1 => {
  const source = parseJson(bytes, "FAMILY_CALC_MUTATION_CATALOGUE_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "denominator_ref", "authorship",
    "target_code_may_read_expected_findings", "mutations", "authority_effect",
    "catalogue_sha256",
  ], "FAMILY_CALC_MUTATION_CATALOGUE_SHAPE_INVALID");
  if (source.schema_version !== "ValueComputationMutationCatalogue/v1"
      || source.authorship !== "independent-family-fixture"
      || source.target_code_may_read_expected_findings !== false
      || source.authority_effect !== "none" || !Array.isArray(source.mutations)) {
    return fail("FAMILY_CALC_MUTATION_CATALOGUE_POLICY_INVALID");
  }
  const denominatorRef = expectObject(source.denominator_ref,
    "FAMILY_CALC_MUTATION_DENOMINATOR_REF_INVALID");
  exactKeys(denominatorRef, ["denominator_id", "denominator_sha256"],
    "FAMILY_CALC_MUTATION_DENOMINATOR_REF_INVALID");
  if (denominatorRef.denominator_id !== denominator.denominator_id
      || denominatorRef.denominator_sha256 !== denominator.denominator_sha256) {
    return fail("FAMILY_CALC_MUTATION_DENOMINATOR_REF_STALE");
  }
  const mutations: ValueComputationMutationV1[] = source.mutations.map((value) => {
    const item = expectObject(value, "FAMILY_CALC_MUTATION_SHAPE_INVALID");
    exactKeys(item, ["mutation_id", "mutation_kind", "expected_finding_codes"],
      "FAMILY_CALC_MUTATION_SHAPE_INVALID");
    if (!VALUE_COMPUTATION_MUTATION_KINDS.includes(
      item.mutation_kind as ValueComputationMutationKind,
    ) || !Array.isArray(item.expected_finding_codes)
      || item.expected_finding_codes.length === 0) {
      return fail("FAMILY_CALC_MUTATION_POLICY_INVALID");
    }
    return Object.freeze({
      mutation_id: expectString(item.mutation_id, "FAMILY_CALC_MUTATION_ID_INVALID"),
      mutation_kind: item.mutation_kind as ValueComputationMutationKind,
      expected_finding_codes: Object.freeze(item.expected_finding_codes.map((code) => {
        return expectString(code, "FAMILY_CALC_MUTATION_FINDING_INVALID") as ValueComputationFindingCode;
      })),
    });
  });
  unique(mutations.map(({mutation_id: id}) => id), "FAMILY_CALC_MUTATION_DUPLICATE");
  const kinds = new Set(mutations.map(({mutation_kind: kind}) => kind));
  if (!VALUE_COMPUTATION_MUTATION_KINDS.every((kind) => kinds.has(kind))) {
    return fail("FAMILY_CALC_MUTATION_COVERAGE_INCOMPLETE");
  }
  const withoutDigest = {
    schema_version: "ValueComputationMutationCatalogue/v1" as const,
    denominator_ref: Object.freeze({
      denominator_id: denominator.denominator_id,
      denominator_sha256: denominator.denominator_sha256,
    }),
    authorship: "independent-family-fixture" as const,
    target_code_may_read_expected_findings: false as const,
    mutations: Object.freeze(mutations),
    authority_effect: "none" as const,
  };
  const digest = expectSha256(source.catalogue_sha256,
    "FAMILY_CALC_MUTATION_CATALOGUE_DIGEST_INVALID");
  if (digest !== computeValueComputationMutationCatalogueSha256(withoutDigest)) {
    return fail("FAMILY_CALC_MUTATION_CATALOGUE_DIGEST_STALE");
  }
  return Object.freeze({...withoutDigest, catalogue_sha256: digest});
};
