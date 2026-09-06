import {createHash} from "node:crypto";

import {
  decodeDeclaredReadLifecycleObservationV1,
} from "../../../kernel/evidence/effect-observation/index.js";
import {
  READ_MODEL_QUERY_DECISIONS,
  READ_MODEL_QUERY_MUTATION_KINDS,
  type ReadModelQueryCaseV1,
  type ReadModelQueryDefinitionV1,
  type ReadModelQueryDenominatorV1,
  type ReadModelQueryFindingCode,
  type ReadModelQueryMutationCatalogueV1,
  type ReadModelQueryMutationKind,
  type ReadModelQueryMutationV1,
  type ReadModelQueryMutationVariant,
  type ReadModelQueryObservationV1,
  type ReadModelQueryObservedResultV1,
  type ReadModelScalarV1,
  type ReadModelValueKindV1,
} from "../contracts/read-model-contracts.js";

type JsonObject = Record<string, unknown>;

const fail = (code: string): never => {
  const error = Object.assign(new Error(code), {code});
  error.name = "ReadModelQueryDecodeError";
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
const exactKeys = (
  source: JsonObject,
  keys: readonly string[],
  code: string,
): void => {
  const actual = Object.keys(source).sort(compareUtf8);
  const expected = [...keys].sort(compareUtf8);
  if (JSON.stringify(actual) !== JSON.stringify(expected)) fail(code);
};
const parseJson = (bytes: string, code: string): JsonObject => {
  try {
    return expectObject(JSON.parse(bytes), code);
  } catch (error) {
    if (isObject(error) && error.name === "ReadModelQueryDecodeError") {
      throw error;
    }
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

export const canonicalReadModelQueryJson = (value: unknown): string =>
  JSON.stringify(canonicalize(value));
export const sha256ReadModelQueryBytes = (bytes: string): string =>
  createHash("sha256").update(bytes, "utf8").digest("hex");
const sha256Json = (value: unknown): string =>
  sha256ReadModelQueryBytes(canonicalReadModelQueryJson(value));
export const sha256ReadModelQueryValue = (value: unknown): string =>
  sha256Json(value);

const unique = (values: readonly string[], code: string): void => {
  if (new Set(values).size !== values.length) fail(code);
};
const decodeScalar = (value: unknown, code: string): ReadModelScalarV1 =>
  value === null || typeof value === "string" || typeof value === "boolean" ||
    (typeof value === "number" && Number.isSafeInteger(value))
    ? value as ReadModelScalarV1
    : fail(code);
const decodeRecord = (
  value: unknown,
  code: string,
): Readonly<Record<string, ReadModelScalarV1>> => {
  const source = expectObject(value, code);
  if (Object.keys(source).length === 0) fail(code);
  return Object.freeze(Object.fromEntries(Object.entries(source)
    .map(([key, child]) => [key, decodeScalar(child, code)])));
};
const decodeCase = (value: unknown): ReadModelQueryCaseV1 => {
  const source = expectObject(value, "FAMILY_QUERY_DEFINITION_CASE_INVALID");
  exactKeys(source, ["case_id", "inputs", "expected_result"],
    "FAMILY_QUERY_DEFINITION_CASE_INVALID");
  return Object.freeze({
    case_id: expectString(source.case_id,
      "FAMILY_QUERY_DEFINITION_CASE_INVALID"),
    inputs: decodeRecord(source.inputs,
      "FAMILY_QUERY_DEFINITION_CASE_INVALID"),
    expected_result: decodeRecord(source.expected_result,
      "FAMILY_QUERY_DEFINITION_CASE_INVALID"),
  });
};
const matchesKind = (value: ReadModelScalarV1, kind: ReadModelValueKindV1): boolean =>
  kind === "string" ? typeof value === "string"
    : kind === "integer" ? typeof value === "number" && Number.isSafeInteger(value)
      : kind === "boolean" ? typeof value === "boolean"
        : value === null || typeof value === "string";

export const decodeReadModelQueryDefinitionV1 = (
  bytes: string,
  expectedDescriptorPath: string,
  descriptorBytes: string,
): ReadModelQueryDefinitionV1 => {
  const source = parseJson(bytes, "FAMILY_QUERY_DEFINITION_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "definition_id", "status", "authorship",
    "derivation_policy", "descriptor_ref", "input_concepts", "read_targets",
    "output_concept", "declared_failures", "cases", "authority_effect",
  ], "FAMILY_QUERY_DEFINITION_SHAPE_INVALID");
  if (source.schema_version !== "ReadModelQueryDefinition/v1" ||
      source.status !== "candidate-fixture" ||
      source.authorship !== "owner-authored-admission-input" ||
      source.derivation_policy !==
        "implementation-and-generated-results-forbidden-as-authority" ||
      source.authority_effect !== "none") {
    return fail("FAMILY_QUERY_DEFINITION_POLICY_INVALID");
  }
  const descriptor = expectObject(source.descriptor_ref,
    "FAMILY_QUERY_DEFINITION_DESCRIPTOR_INVALID");
  exactKeys(descriptor, ["descriptor_id", "path", "sha256"],
    "FAMILY_QUERY_DEFINITION_DESCRIPTOR_INVALID");
  if (descriptor.path !== expectedDescriptorPath ||
      descriptor.sha256 !== sha256ReadModelQueryBytes(descriptorBytes)) {
    return fail("FAMILY_QUERY_DEFINITION_DESCRIPTOR_STALE");
  }
  if (!Array.isArray(source.input_concepts) ||
      source.input_concepts.length === 0 ||
      !Array.isArray(source.read_targets) || source.read_targets.length === 0 ||
      !Array.isArray(source.declared_failures) ||
      source.declared_failures.length === 0 ||
      !Array.isArray(source.cases) || source.cases.length === 0) {
    return fail("FAMILY_QUERY_DEFINITION_POLICY_INVALID");
  }
  const inputConcepts = source.input_concepts.map((value) => {
    const item = expectObject(value, "FAMILY_QUERY_INPUT_CONCEPT_INVALID");
    exactKeys(item, ["name", "concept_id", "value_kind", "required"],
      "FAMILY_QUERY_INPUT_CONCEPT_INVALID");
    if ((item.value_kind !== "string" && item.value_kind !== "integer") ||
        item.required !== true) fail("FAMILY_QUERY_INPUT_CONCEPT_INVALID");
    return Object.freeze({
      name: expectString(item.name, "FAMILY_QUERY_INPUT_CONCEPT_INVALID"),
      concept_id: expectString(item.concept_id,
        "FAMILY_QUERY_INPUT_CONCEPT_INVALID"),
      value_kind: item.value_kind as "string" | "integer",
      required: true as const,
    });
  });
  unique(inputConcepts.map(({name}) => name),
    "FAMILY_QUERY_INPUT_CONCEPT_DUPLICATE");
  const allowedChannels = new Set([
    "clock", "random", "environment", "filesystem", "network", "process",
    "global-cache", "delayed-lazy", "callback", "iterator-future",
    "finalizer-drop", "mutable-output",
  ]);
  const readTargets = source.read_targets.map((value) => {
    const item = expectObject(value, "FAMILY_QUERY_READ_TARGET_INVALID");
    exactKeys(item, ["target_id", "concept_id", "channel"],
      "FAMILY_QUERY_READ_TARGET_INVALID");
    if (!allowedChannels.has(String(item.channel))) {
      fail("FAMILY_QUERY_READ_TARGET_INVALID");
    }
    return Object.freeze({
      target_id: expectString(item.target_id,
        "FAMILY_QUERY_READ_TARGET_INVALID"),
      concept_id: expectString(item.concept_id,
        "FAMILY_QUERY_READ_TARGET_INVALID"),
      channel: item.channel as ReadModelQueryDefinitionV1["read_targets"][number]["channel"],
    });
  });
  unique(readTargets.map(({target_id: id}) => id),
    "FAMILY_QUERY_READ_TARGET_DUPLICATE");
  const output = expectObject(source.output_concept,
    "FAMILY_QUERY_OUTPUT_CONCEPT_INVALID");
  exactKeys(output, ["concept_id", "fields", "additional_fields"],
    "FAMILY_QUERY_OUTPUT_CONCEPT_INVALID");
  if (!Array.isArray(output.fields) || output.fields.length === 0 ||
      output.additional_fields !== false) {
    return fail("FAMILY_QUERY_OUTPUT_CONCEPT_INVALID");
  }
  const fields = output.fields.map((value) => {
    const item = expectObject(value, "FAMILY_QUERY_OUTPUT_FIELD_INVALID");
    exactKeys(item, ["name", "value_kind", "required"],
      "FAMILY_QUERY_OUTPUT_FIELD_INVALID");
    if (!["string", "integer", "boolean", "nullable-string"]
      .includes(String(item.value_kind)) || item.required !== true) {
      fail("FAMILY_QUERY_OUTPUT_FIELD_INVALID");
    }
    return Object.freeze({
      name: expectString(item.name, "FAMILY_QUERY_OUTPUT_FIELD_INVALID"),
      value_kind: item.value_kind as ReadModelValueKindV1,
      required: true as const,
    });
  });
  unique(fields.map(({name}) => name), "FAMILY_QUERY_OUTPUT_FIELD_DUPLICATE");
  const declaredFailures = source.declared_failures.map((value) =>
    expectString(value, "FAMILY_QUERY_DECLARED_FAILURE_INVALID"));
  unique(declaredFailures, "FAMILY_QUERY_DECLARED_FAILURE_DUPLICATE");
  const cases = source.cases.map(decodeCase);
  unique(cases.map(({case_id: id}) => id), "FAMILY_QUERY_CASE_DUPLICATE");
  const inputNames = inputConcepts.map(({name}) => name).sort(compareUtf8);
  const fieldNames = fields.map(({name}) => name).sort(compareUtf8);
  for (const testCase of cases) {
    if (JSON.stringify(Object.keys(testCase.inputs).sort(compareUtf8)) !==
        JSON.stringify(inputNames) ||
        JSON.stringify(Object.keys(testCase.expected_result).sort(compareUtf8)) !==
        JSON.stringify(fieldNames)) {
      fail("FAMILY_QUERY_CASE_SHAPE_INVALID");
    }
    for (const field of fields) {
      if (!matchesKind(testCase.expected_result[field.name] ?? null,
        field.value_kind)) fail("FAMILY_QUERY_CASE_VALUE_KIND_INVALID");
    }
  }
  return Object.freeze({
    schema_version: "ReadModelQueryDefinition/v1" as const,
    definition_id: expectString(source.definition_id,
      "FAMILY_QUERY_DEFINITION_ID_INVALID"),
    status: "candidate-fixture" as const,
    authorship: "owner-authored-admission-input" as const,
    derivation_policy:
      "implementation-and-generated-results-forbidden-as-authority" as const,
    descriptor_ref: Object.freeze({
      descriptor_id: expectString(descriptor.descriptor_id,
        "FAMILY_QUERY_DEFINITION_DESCRIPTOR_INVALID"),
      path: expectedDescriptorPath,
      sha256: expectSha256(descriptor.sha256,
        "FAMILY_QUERY_DEFINITION_DESCRIPTOR_INVALID"),
    }),
    input_concepts: Object.freeze(inputConcepts),
    read_targets: Object.freeze(readTargets),
    output_concept: Object.freeze({
      concept_id: expectString(output.concept_id,
        "FAMILY_QUERY_OUTPUT_CONCEPT_INVALID"),
      fields: Object.freeze(fields),
      additional_fields: false as const,
    }),
    declared_failures: Object.freeze(declaredFailures),
    cases: Object.freeze(cases),
    authority_effect: "none" as const,
  });
};

const denominatorBody = (
  value: Omit<ReadModelQueryDenominatorV1, "denominator_sha256">,
): unknown => ({
  ...value,
  positive_decisions: [...value.positive_decisions].sort(compareUtf8),
});
export const computeReadModelQueryDenominatorSha256 = (
  value: Omit<ReadModelQueryDenominatorV1, "denominator_sha256">,
): string => sha256Json(denominatorBody(value));

export const decodeReadModelQueryDenominatorV1 = (
  bytes: string,
  ownerDefinitionBytes: string,
  ownerDefinition: ReadModelQueryDefinitionV1,
  expectedOwnerPath: string,
): ReadModelQueryDenominatorV1 => {
  const source = parseJson(bytes, "FAMILY_QUERY_DENOMINATOR_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "denominator_id", "owner_definition_ref",
    "portable_contract", "positive_decisions", "authority_effect",
    "denominator_sha256",
  ], "FAMILY_QUERY_DENOMINATOR_SHAPE_INVALID");
  const ownerRef = expectObject(source.owner_definition_ref,
    "FAMILY_QUERY_DENOMINATOR_OWNER_INVALID");
  exactKeys(ownerRef, ["definition_id", "path", "sha256"],
    "FAMILY_QUERY_DENOMINATOR_OWNER_INVALID");
  if (source.schema_version !== "ReadModelQueryDenominator/v1" ||
      source.authority_effect !== "none" ||
      ownerRef.definition_id !== ownerDefinition.definition_id ||
      ownerRef.path !== expectedOwnerPath ||
      ownerRef.sha256 !== sha256ReadModelQueryBytes(ownerDefinitionBytes)) {
    return fail("FAMILY_QUERY_DENOMINATOR_OWNER_STALE");
  }
  const portable = expectObject(source.portable_contract,
    "FAMILY_QUERY_DENOMINATOR_POLICY_INVALID");
  exactKeys(portable, [
    "return_semantics", "dependency_contract", "effect_contract",
    "result_consumption", "lifecycle_paths", "unsupported_coverage",
    "observer_origin",
  ], "FAMILY_QUERY_DENOMINATOR_POLICY_INVALID");
  if (portable.return_semantics !== "exact-owner-authored-read-model" ||
      portable.dependency_contract !==
        "exact-ordered-declared-read-targets-only" ||
      portable.effect_contract !== "declared-reads-and-zero-observed-writes" ||
      portable.result_consumption !==
        "complete-through-supported-lifecycle" ||
      portable.lifecycle_paths !==
        "return-await-cancel-close-dispose-finalizer-quiescence" ||
      portable.unsupported_coverage !== "fail-closed" ||
      portable.observer_origin !== "locked-harness-owned-not-provider" ||
      !Array.isArray(source.positive_decisions)) {
    return fail("FAMILY_QUERY_DENOMINATOR_POLICY_INVALID");
  }
  const decisions = source.positive_decisions.map((value) =>
    expectString(value, "FAMILY_QUERY_DENOMINATOR_DECISIONS_INVALID"));
  if (JSON.stringify([...decisions].sort(compareUtf8)) !==
      JSON.stringify([...READ_MODEL_QUERY_DECISIONS].sort(compareUtf8))) {
    return fail("FAMILY_QUERY_DENOMINATOR_DECISIONS_INVALID");
  }
  const withoutDigest = {
    schema_version: "ReadModelQueryDenominator/v1" as const,
    denominator_id: expectString(source.denominator_id,
      "FAMILY_QUERY_DENOMINATOR_ID_INVALID"),
    owner_definition_ref: Object.freeze({
      definition_id: ownerDefinition.definition_id,
      path: expectedOwnerPath,
      sha256: expectSha256(ownerRef.sha256,
        "FAMILY_QUERY_DENOMINATOR_OWNER_INVALID"),
    }),
    portable_contract: Object.freeze({
      return_semantics: "exact-owner-authored-read-model" as const,
      dependency_contract:
        "exact-ordered-declared-read-targets-only" as const,
      effect_contract: "declared-reads-and-zero-observed-writes" as const,
      result_consumption: "complete-through-supported-lifecycle" as const,
      lifecycle_paths:
        "return-await-cancel-close-dispose-finalizer-quiescence" as const,
      unsupported_coverage: "fail-closed" as const,
      observer_origin: "locked-harness-owned-not-provider" as const,
    }),
    positive_decisions: Object.freeze([...READ_MODEL_QUERY_DECISIONS]),
    authority_effect: "none" as const,
  };
  const digest = expectSha256(source.denominator_sha256,
    "FAMILY_QUERY_DENOMINATOR_DIGEST_INVALID");
  if (digest !== computeReadModelQueryDenominatorSha256(withoutDigest)) {
    return fail("FAMILY_QUERY_DENOMINATOR_DIGEST_STALE");
  }
  return Object.freeze({...withoutDigest, denominator_sha256: digest});
};

const observationBody = (
  value: Omit<ReadModelQueryObservationV1, "observation_sha256">,
): unknown => value;
export const computeReadModelQueryObservationSha256 = (
  value: Omit<ReadModelQueryObservationV1, "observation_sha256">,
): string => sha256Json(observationBody(value));
export const mintReadModelQueryObservationV1 = (
  value: Omit<ReadModelQueryObservationV1, "observation_sha256">,
): ReadModelQueryObservationV1 => Object.freeze({
  ...value,
  target: Object.freeze({...value.target}),
  definition_ref: Object.freeze({...value.definition_ref}),
  binding: Object.freeze({...value.binding}),
  observed_result: Object.freeze({
    ...value.observed_result,
    result: Object.freeze({...value.observed_result.result}),
  }),
  observation_sha256: computeReadModelQueryObservationSha256(value),
});

const decodeObservedResult = (value: unknown): ReadModelQueryObservedResultV1 => {
  const source = expectObject(value, "FAMILY_QUERY_OBSERVED_RESULT_INVALID");
  exactKeys(source, [
    "case_id", "input_sha256", "result", "result_sha256", "declared_failure",
  ], "FAMILY_QUERY_OBSERVED_RESULT_INVALID");
  if (source.declared_failure !== null &&
      typeof source.declared_failure !== "string") {
    return fail("FAMILY_QUERY_OBSERVED_RESULT_INVALID");
  }
  return Object.freeze({
    case_id: expectString(source.case_id,
      "FAMILY_QUERY_OBSERVED_RESULT_INVALID"),
    input_sha256: expectSha256(source.input_sha256,
      "FAMILY_QUERY_OBSERVED_RESULT_INVALID"),
    result: decodeRecord(source.result, "FAMILY_QUERY_OBSERVED_RESULT_INVALID"),
    result_sha256: expectSha256(source.result_sha256,
      "FAMILY_QUERY_OBSERVED_RESULT_INVALID"),
    declared_failure: source.declared_failure,
  });
};

export const decodeReadModelQueryObservationV1 = (
  bytes: string,
): ReadModelQueryObservationV1 => {
  const source = parseJson(bytes, "FAMILY_QUERY_OBSERVATION_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "observation_id", "source_kind", "target",
    "definition_ref", "binding", "observed_result",
    "read_lifecycle_observation", "authority_effect", "observation_sha256",
  ], "FAMILY_QUERY_OBSERVATION_SHAPE_INVALID");
  if (source.schema_version !== "ReadModelQueryObservation/v1" ||
      !["independent-family-fixture", "target-observation",
        "mutated-family-observation"].includes(String(source.source_kind)) ||
      source.authority_effect !== "none") {
    return fail("FAMILY_QUERY_OBSERVATION_POLICY_INVALID");
  }
  const target = expectObject(source.target, "FAMILY_QUERY_TARGET_INVALID");
  exactKeys(target, ["target_id", "target_sha256", "language", "protocol_id"],
    "FAMILY_QUERY_TARGET_INVALID");
  if (!["family-fixture", "typescript", "python", "rust"]
    .includes(String(target.language))) fail("FAMILY_QUERY_TARGET_INVALID");
  const definitionRef = expectObject(source.definition_ref,
    "FAMILY_QUERY_DEFINITION_REF_INVALID");
  exactKeys(definitionRef, ["definition_id", "path", "sha256"],
    "FAMILY_QUERY_DEFINITION_REF_INVALID");
  const binding = expectObject(source.binding, "FAMILY_QUERY_BINDING_INVALID");
  exactKeys(binding, [
    "descriptor_id", "descriptor_sha256", "provider_id", "provider_sha256",
  ], "FAMILY_QUERY_BINDING_INVALID");
  const withoutDigest = {
    schema_version: "ReadModelQueryObservation/v1" as const,
    observation_id: expectString(source.observation_id,
      "FAMILY_QUERY_OBSERVATION_ID_INVALID"),
    source_kind: source.source_kind as ReadModelQueryObservationV1["source_kind"],
    target: Object.freeze({
      target_id: expectString(target.target_id, "FAMILY_QUERY_TARGET_INVALID"),
      target_sha256: expectSha256(target.target_sha256,
        "FAMILY_QUERY_TARGET_INVALID"),
      language: target.language as ReadModelQueryObservationV1["target"]["language"],
      protocol_id: expectString(target.protocol_id,
        "FAMILY_QUERY_TARGET_INVALID"),
    }),
    definition_ref: Object.freeze({
      definition_id: expectString(definitionRef.definition_id,
        "FAMILY_QUERY_DEFINITION_REF_INVALID"),
      path: expectString(definitionRef.path,
        "FAMILY_QUERY_DEFINITION_REF_INVALID"),
      sha256: expectSha256(definitionRef.sha256,
        "FAMILY_QUERY_DEFINITION_REF_INVALID"),
    }),
    binding: Object.freeze({
      descriptor_id: expectString(binding.descriptor_id,
        "FAMILY_QUERY_BINDING_INVALID"),
      descriptor_sha256: expectSha256(binding.descriptor_sha256,
        "FAMILY_QUERY_BINDING_INVALID"),
      provider_id: expectString(binding.provider_id,
        "FAMILY_QUERY_BINDING_INVALID"),
      provider_sha256: expectSha256(binding.provider_sha256,
        "FAMILY_QUERY_BINDING_INVALID"),
    }),
    observed_result: decodeObservedResult(source.observed_result),
    read_lifecycle_observation: decodeDeclaredReadLifecycleObservationV1(
      canonicalReadModelQueryJson(source.read_lifecycle_observation),
    ),
    authority_effect: "none" as const,
  };
  const digest = expectSha256(source.observation_sha256,
    "FAMILY_QUERY_OBSERVATION_DIGEST_INVALID");
  if (digest !== computeReadModelQueryObservationSha256(withoutDigest)) {
    return fail("FAMILY_QUERY_OBSERVATION_DIGEST_STALE");
  }
  return Object.freeze({...withoutDigest, observation_sha256: digest});
};

const mutationBody = (
  value: Omit<ReadModelQueryMutationCatalogueV1, "catalogue_sha256">,
): unknown => ({
  ...value,
  mutations: [...value.mutations].sort((left, right) =>
    compareUtf8(left.mutation_id, right.mutation_id)),
});
export const computeReadModelQueryMutationCatalogueSha256 = (
  value: Omit<ReadModelQueryMutationCatalogueV1, "catalogue_sha256">,
): string => sha256Json(mutationBody(value));

export const decodeReadModelQueryMutationCatalogueV1 = (
  bytes: string,
  denominator: ReadModelQueryDenominatorV1,
): ReadModelQueryMutationCatalogueV1 => {
  const source = parseJson(bytes,
    "FAMILY_QUERY_MUTATION_CATALOGUE_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "denominator_ref", "authorship",
    "target_code_may_read_expected_findings", "mutations", "authority_effect",
    "catalogue_sha256",
  ], "FAMILY_QUERY_MUTATION_CATALOGUE_SHAPE_INVALID");
  const denominatorRef = expectObject(source.denominator_ref,
    "FAMILY_QUERY_MUTATION_DENOMINATOR_INVALID");
  exactKeys(denominatorRef, ["denominator_id", "denominator_sha256"],
    "FAMILY_QUERY_MUTATION_DENOMINATOR_INVALID");
  if (source.schema_version !== "ReadModelQueryMutationCatalogue/v1" ||
      source.authorship !== "independent-family-fixture" ||
      source.target_code_may_read_expected_findings !== false ||
      source.authority_effect !== "none" || !Array.isArray(source.mutations) ||
      denominatorRef.denominator_id !== denominator.denominator_id ||
      denominatorRef.denominator_sha256 !== denominator.denominator_sha256) {
    return fail("FAMILY_QUERY_MUTATION_CATALOGUE_POLICY_INVALID");
  }
  const variants = new Set([
    "default", "cancel", "close", "dispose", "finalizer", "quiescence",
  ]);
  const mutations: ReadModelQueryMutationV1[] = source.mutations.map((value) => {
    const item = expectObject(value, "FAMILY_QUERY_MUTATION_INVALID");
    exactKeys(item, [
      "mutation_id", "mutation_kind", "variants", "expected_finding_codes",
    ], "FAMILY_QUERY_MUTATION_INVALID");
    if (!READ_MODEL_QUERY_MUTATION_KINDS.includes(
      item.mutation_kind as ReadModelQueryMutationKind) ||
      !Array.isArray(item.variants) || item.variants.length === 0 ||
      !item.variants.every((variant) => variants.has(String(variant))) ||
      !Array.isArray(item.expected_finding_codes) ||
      item.expected_finding_codes.length === 0) {
      return fail("FAMILY_QUERY_MUTATION_INVALID");
    }
    return Object.freeze({
      mutation_id: expectString(item.mutation_id, "FAMILY_QUERY_MUTATION_INVALID"),
      mutation_kind: item.mutation_kind as ReadModelQueryMutationKind,
      variants: Object.freeze(item.variants as ReadModelQueryMutationVariant[]),
      expected_finding_codes: Object.freeze(item.expected_finding_codes.map(
        (code) => expectString(code,
          "FAMILY_QUERY_MUTATION_INVALID") as ReadModelQueryFindingCode,
      )),
    });
  });
  unique(mutations.map(({mutation_id: id}) => id),
    "FAMILY_QUERY_MUTATION_DUPLICATE");
  if (mutations.length !== 7 ||
      !READ_MODEL_QUERY_MUTATION_KINDS.every((kind) =>
        mutations.some(({mutation_kind: current}) => current === kind))) {
    return fail("FAMILY_QUERY_MUTATION_COVERAGE_INCOMPLETE");
  }
  const requiredLifecycleVariants = [
    "cancel", "close", "dispose", "finalizer", "quiescence",
  ].sort(compareUtf8);
  const coverage = mutations.find(({mutation_kind}) =>
    mutation_kind === "missing-observation-coverage");
  const deferred = mutations.find(({mutation_kind}) =>
    mutation_kind === "deferred-lazy-write");
  if (!coverage || JSON.stringify([...coverage.variants].sort(compareUtf8)) !==
      JSON.stringify(requiredLifecycleVariants) || !deferred ||
      JSON.stringify([...deferred.variants].sort(compareUtf8)) !==
        JSON.stringify(requiredLifecycleVariants)) {
    return fail("FAMILY_QUERY_LIFECYCLE_HOSTILES_INCOMPLETE");
  }
  const withoutDigest = {
    schema_version: "ReadModelQueryMutationCatalogue/v1" as const,
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
    "FAMILY_QUERY_MUTATION_CATALOGUE_DIGEST_INVALID");
  if (digest !== computeReadModelQueryMutationCatalogueSha256(withoutDigest)) {
    return fail("FAMILY_QUERY_MUTATION_CATALOGUE_DIGEST_STALE");
  }
  return Object.freeze({...withoutDigest, catalogue_sha256: digest});
};
