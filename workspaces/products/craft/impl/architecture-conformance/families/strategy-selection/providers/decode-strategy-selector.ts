import {
  STRATEGY_SELECTION_DECISIONS,
  STRATEGY_SELECTION_MUTATION_KINDS,
  type LockedStrategyExecutionObserverRefV1,
  type StrategyCatalogueV1,
  type StrategyExecutionObservationV1,
  type StrategySelectionCaseV1,
  type StrategySelectionDefinitionV1,
  type StrategySelectionDenominatorV1,
  type StrategySelectionInputValueV1,
  type StrategySelectionMutationCatalogueV1,
  type StrategySelectionMutationKind,
  type StrategySelectionObservationV1,
} from "../contracts/strategy-selection-contracts.js";
import {
  canonicalStrategySelectionJson,
  decodeStrategyCatalogueV1,
  sha256StrategySelectionBytes,
} from "./decode-strategy-selection.js";
import {
  decodeEffectObservationV1,
} from "../../../kernel/evidence/effect-observation/index.js";

type JsonObject = Record<string, unknown>;

const SHA256 = /^[a-f0-9]{64}$/u;
const IDENTIFIER = /^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$/u;
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const fail = (code: string): never => {
  throw new Error(code);
};
const isObject = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const object = (value: unknown, code: string): JsonObject =>
  isObject(value) ? value : fail(code);
const string = (value: unknown, code: string): string =>
  typeof value === "string" && value.length > 0 ? value : fail(code);
const identifier = (value: unknown, code: string): string => {
  const result = string(value, code);
  return IDENTIFIER.test(result) ? result : fail(code);
};
const sha = (value: unknown, code: string): string => {
  const result = string(value, code);
  return SHA256.test(result) ? result : fail(code);
};
const count = (value: unknown, code: string): number =>
  Number.isSafeInteger(value) && Number(value) >= 0 ? Number(value) : fail(code);
const exactKeys = (
  source: JsonObject,
  expected: readonly string[],
  code: string,
): void => {
  const actual = Object.keys(source).sort(compareUtf8);
  const wanted = [...expected].sort(compareUtf8);
  if (actual.length !== wanted.length ||
      actual.some((value, index) => value !== wanted[index])) fail(code);
};
const parse = (bytes: string, code: string): JsonObject => {
  try {
    return object(JSON.parse(bytes), code);
  } catch (error: unknown) {
    if (error instanceof Error && error.message.startsWith("FAMILY_POLICY_")) {
      throw error;
    }
    return fail(code);
  }
};
const sha256Json = (value: unknown): string =>
  sha256StrategySelectionBytes(canonicalStrategySelectionJson(value));
const unique = (values: readonly string[]): boolean =>
  new Set(values).size === values.length;
const inputValue = (
  value: unknown,
  code: string,
): StrategySelectionInputValueV1 => {
  if (value === null || typeof value === "string" || typeof value === "boolean") {
    return value;
  }
  if (typeof value === "number" && Number.isSafeInteger(value)) return value;
  return fail(code);
};

const definitionBody = (
  value: Omit<StrategySelectionDefinitionV1, "definition_sha256">,
): unknown => value;
export const computeStrategySelectionDefinitionSha256 = (
  value: Omit<StrategySelectionDefinitionV1, "definition_sha256">,
): string => sha256Json(definitionBody(value));

export const decodeStrategySelectionDefinitionV1 = (
  bytes: string,
  catalogueBytes: string,
  expectedCataloguePath: string,
  descriptorPath: string,
  descriptorBytes: string,
): Readonly<{
  catalogue: StrategyCatalogueV1;
  definition: StrategySelectionDefinitionV1;
}> => {
  const catalogue = decodeStrategyCatalogueV1(
    catalogueBytes,
    descriptorPath,
    descriptorBytes,
  );
  const source = parse(bytes, "FAMILY_POLICY_SELECTOR_DEFINITION_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "definition_id", "status", "authorship",
    "derivation_policy", "descriptor_ref", "catalogue_ref", "input_facts",
    "branch_contract", "cases", "sensitivity_pairs", "authority_effect",
    "definition_sha256",
  ], "FAMILY_POLICY_SELECTOR_DEFINITION_SHAPE_INVALID");
  if (source.schema_version !== "StrategySelectionDefinition/v1" ||
      source.status !== "candidate-fixture" ||
      source.authorship !== "owner-authored-admission-input" ||
      source.derivation_policy !==
        "implementation-and-generated-selections-forbidden-as-authority" ||
      source.authority_effect !== "none") {
    return fail("FAMILY_POLICY_SELECTOR_DEFINITION_POLICY_INVALID");
  }
  const descriptor = object(
    source.descriptor_ref,
    "FAMILY_POLICY_SELECTOR_DESCRIPTOR_REF_INVALID",
  );
  exactKeys(descriptor, ["descriptor_id", "path", "sha256"],
    "FAMILY_POLICY_SELECTOR_DESCRIPTOR_REF_INVALID");
  if (descriptor.path !== descriptorPath ||
      sha(descriptor.sha256, "FAMILY_POLICY_SELECTOR_DESCRIPTOR_REF_INVALID") !==
        sha256StrategySelectionBytes(descriptorBytes)) {
    return fail("FAMILY_POLICY_SELECTOR_DESCRIPTOR_REF_STALE");
  }
  const catalogueRef = object(
    source.catalogue_ref,
    "FAMILY_POLICY_SELECTOR_CATALOGUE_REF_INVALID",
  );
  exactKeys(catalogueRef, ["catalogue_id", "path", "sha256", "catalogue_sha256"],
    "FAMILY_POLICY_SELECTOR_CATALOGUE_REF_INVALID");
  if (catalogueRef.catalogue_id !== catalogue.catalogue_id ||
      catalogueRef.path !== expectedCataloguePath ||
      sha(catalogueRef.sha256, "FAMILY_POLICY_SELECTOR_CATALOGUE_REF_INVALID") !==
        sha256StrategySelectionBytes(catalogueBytes) ||
      catalogueRef.catalogue_sha256 !== catalogue.catalogue_sha256) {
    return fail("FAMILY_POLICY_SELECTOR_CATALOGUE_REF_STALE");
  }
  if (!Array.isArray(source.input_facts) || source.input_facts.length === 0) {
    return fail("FAMILY_POLICY_SELECTOR_INPUT_FACTS_INVALID");
  }
  const inputFacts = source.input_facts.map((value) => {
    const fact = object(value, "FAMILY_POLICY_SELECTOR_INPUT_FACT_INVALID");
    exactKeys(fact, ["name", "value_kind", "required"],
      "FAMILY_POLICY_SELECTOR_INPUT_FACT_INVALID");
    if (!["integer", "boolean", "string"].includes(String(fact.value_kind)) ||
        fact.required !== true) {
      return fail("FAMILY_POLICY_SELECTOR_INPUT_FACT_INVALID");
    }
    return Object.freeze({
      name: identifier(fact.name, "FAMILY_POLICY_SELECTOR_INPUT_FACT_INVALID"),
      value_kind: fact.value_kind as "integer" | "boolean" | "string",
      required: true as const,
    });
  });
  const factNames = inputFacts.map(({name}) => name);
  if (!unique(factNames)) return fail("FAMILY_POLICY_SELECTOR_INPUT_FACT_DUPLICATE");
  const branch = object(
    source.branch_contract,
    "FAMILY_POLICY_SELECTOR_BRANCH_CONTRACT_INVALID",
  );
  exactKeys(branch, [
    "return_semantics", "dependency_contract", "boolean_forbidden",
    "selected_strategy_execution",
  ], "FAMILY_POLICY_SELECTOR_BRANCH_CONTRACT_INVALID");
  if (branch.return_semantics !== "one-current-strategy-identity" ||
      branch.dependency_contract !== "explicit-inputs-only" ||
      branch.boolean_forbidden !== true ||
      branch.selected_strategy_execution !== "forbidden-during-selection") {
    return fail("FAMILY_POLICY_SELECTOR_BRANCH_CONTRACT_INVALID");
  }
  if (!Array.isArray(source.cases) || source.cases.length < 2) {
    return fail("FAMILY_POLICY_SELECTOR_CASES_INVALID");
  }
  const cases = source.cases.map((value): StrategySelectionCaseV1 => {
    const item = object(value, "FAMILY_POLICY_SELECTOR_CASE_INVALID");
    exactKeys(item, ["case_id", "inputs", "expected_strategy_id", "expected_branch_id"],
      "FAMILY_POLICY_SELECTOR_CASE_INVALID");
    const inputs = object(item.inputs, "FAMILY_POLICY_SELECTOR_CASE_INPUTS_INVALID");
    const inputKeys = Object.keys(inputs).sort(compareUtf8);
    if (canonicalStrategySelectionJson(inputKeys) !==
        canonicalStrategySelectionJson([...factNames].sort(compareUtf8))) {
      return fail("FAMILY_POLICY_SELECTOR_CASE_INPUTS_INVALID");
    }
    const decodedInputs = Object.fromEntries(Object.entries(inputs)
      .map(([key, input]) => [key, inputValue(
        input,
        "FAMILY_POLICY_SELECTOR_CASE_INPUTS_INVALID",
      )]));
    for (const fact of inputFacts) {
      const observed = decodedInputs[fact.name];
      if ((fact.value_kind === "integer" &&
            !(typeof observed === "number" && Number.isSafeInteger(observed))) ||
          (fact.value_kind === "boolean" && typeof observed !== "boolean") ||
          (fact.value_kind === "string" && typeof observed !== "string")) {
        return fail("FAMILY_POLICY_SELECTOR_CASE_INPUTS_INVALID");
      }
    }
    return Object.freeze({
      case_id: identifier(item.case_id, "FAMILY_POLICY_SELECTOR_CASE_INVALID"),
      inputs: Object.freeze(decodedInputs),
      expected_strategy_id: identifier(
        item.expected_strategy_id,
        "FAMILY_POLICY_SELECTOR_CASE_INVALID",
      ),
      expected_branch_id: identifier(
        item.expected_branch_id,
        "FAMILY_POLICY_SELECTOR_CASE_INVALID",
      ),
    });
  });
  if (!unique(cases.map(({case_id}) => case_id))) {
    return fail("FAMILY_POLICY_SELECTOR_CASE_ID_DUPLICATE");
  }
  if (!Array.isArray(source.sensitivity_pairs) ||
      source.sensitivity_pairs.length === 0) {
    return fail("FAMILY_POLICY_SELECTOR_SENSITIVITY_INVALID");
  }
  const caseById = new Map(cases.map((item) => [item.case_id, item]));
  const sensitivityPairs = source.sensitivity_pairs.map((value) => {
    const pair = object(value, "FAMILY_POLICY_SELECTOR_SENSITIVITY_INVALID");
    exactKeys(pair, ["left_case_id", "right_case_id", "changed_input_fact"],
      "FAMILY_POLICY_SELECTOR_SENSITIVITY_INVALID");
    const leftCaseId = identifier(
      pair.left_case_id,
      "FAMILY_POLICY_SELECTOR_SENSITIVITY_INVALID",
    );
    const rightCaseId = identifier(
      pair.right_case_id,
      "FAMILY_POLICY_SELECTOR_SENSITIVITY_INVALID",
    );
    const changedInputFact = identifier(
      pair.changed_input_fact,
      "FAMILY_POLICY_SELECTOR_SENSITIVITY_INVALID",
    );
    const left = caseById.get(leftCaseId);
    const right = caseById.get(rightCaseId);
    if (!left || !right || !factNames.includes(changedInputFact) ||
        left.expected_strategy_id === right.expected_strategy_id) {
      return fail("FAMILY_POLICY_SELECTOR_SENSITIVITY_INVALID");
    }
    const changed = factNames.filter((name) =>
      canonicalStrategySelectionJson(left.inputs[name]) !==
      canonicalStrategySelectionJson(right.inputs[name]));
    if (changed.length !== 1 || changed[0] !== changedInputFact) {
      return fail("FAMILY_POLICY_SELECTOR_SENSITIVITY_INVALID");
    }
    return Object.freeze({
      left_case_id: leftCaseId,
      right_case_id: rightCaseId,
      changed_input_fact: changedInputFact,
    });
  });
  if (new Set(sensitivityPairs.map(({changed_input_fact: fact}) => fact)).size !==
      factNames.length) {
    return fail("FAMILY_POLICY_SELECTOR_SENSITIVITY_INCOMPLETE");
  }
  const withoutDigest = Object.freeze({
    schema_version: "StrategySelectionDefinition/v1" as const,
    definition_id: identifier(
      source.definition_id,
      "FAMILY_POLICY_SELECTOR_DEFINITION_ID_INVALID",
    ),
    status: "candidate-fixture" as const,
    authorship: "owner-authored-admission-input" as const,
    derivation_policy:
      "implementation-and-generated-selections-forbidden-as-authority" as const,
    descriptor_ref: Object.freeze({
      descriptor_id: identifier(
        descriptor.descriptor_id,
        "FAMILY_POLICY_SELECTOR_DESCRIPTOR_REF_INVALID",
      ),
      path: descriptorPath,
      sha256: sha(descriptor.sha256, "FAMILY_POLICY_SELECTOR_DESCRIPTOR_REF_INVALID"),
    }),
    catalogue_ref: Object.freeze({
      catalogue_id: catalogue.catalogue_id,
      path: expectedCataloguePath,
      sha256: sha(catalogueRef.sha256, "FAMILY_POLICY_SELECTOR_CATALOGUE_REF_INVALID"),
      catalogue_sha256: catalogue.catalogue_sha256,
    }),
    input_facts: Object.freeze(inputFacts),
    branch_contract: Object.freeze({
      return_semantics: "one-current-strategy-identity" as const,
      dependency_contract: "explicit-inputs-only" as const,
      boolean_forbidden: true as const,
      selected_strategy_execution: "forbidden-during-selection" as const,
    }),
    cases: Object.freeze(cases),
    sensitivity_pairs: Object.freeze(sensitivityPairs),
    authority_effect: "none" as const,
  });
  const digest = sha(
    source.definition_sha256,
    "FAMILY_POLICY_SELECTOR_DEFINITION_DIGEST_INVALID",
  );
  if (digest !== computeStrategySelectionDefinitionSha256(withoutDigest)) {
    return fail("FAMILY_POLICY_SELECTOR_DEFINITION_DIGEST_STALE");
  }
  return Object.freeze({
    catalogue,
    definition: Object.freeze({...withoutDigest, definition_sha256: digest}),
  });
};

const denominatorBody = (
  value: Omit<StrategySelectionDenominatorV1, "denominator_sha256">,
): unknown => ({
  ...value,
  positive_decisions: [...value.positive_decisions].sort(compareUtf8),
});
export const computeStrategySelectionDenominatorSha256 = (
  value: Omit<StrategySelectionDenominatorV1, "denominator_sha256">,
): string => sha256Json(denominatorBody(value));

export const decodeStrategySelectionDenominatorV1 = (
  bytes: string,
  definitionBytes: string,
  expectedDefinitionPath: string,
  catalogueBytes: string,
  expectedCataloguePath: string,
  descriptorPath: string,
  descriptorBytes: string,
): Readonly<{
  catalogue: StrategyCatalogueV1;
  definition: StrategySelectionDefinitionV1;
  denominator: StrategySelectionDenominatorV1;
}> => {
  const {catalogue, definition} = decodeStrategySelectionDefinitionV1(
    definitionBytes,
    catalogueBytes,
    expectedCataloguePath,
    descriptorPath,
    descriptorBytes,
  );
  const source = parse(bytes, "FAMILY_POLICY_SELECTOR_DENOMINATOR_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "denominator_id", "owner_definition_ref",
    "owner_catalogue_ref", "portable_contract", "positive_decisions",
    "authority_effect", "denominator_sha256",
  ], "FAMILY_POLICY_SELECTOR_DENOMINATOR_SHAPE_INVALID");
  if (source.schema_version !== "StrategySelectionDenominator/v1" ||
      source.authority_effect !== "none" || !Array.isArray(source.positive_decisions)) {
    return fail("FAMILY_POLICY_SELECTOR_DENOMINATOR_POLICY_INVALID");
  }
  const definitionRef = object(
    source.owner_definition_ref,
    "FAMILY_POLICY_SELECTOR_DEFINITION_REF_INVALID",
  );
  exactKeys(definitionRef, ["definition_id", "path", "sha256", "definition_sha256"],
    "FAMILY_POLICY_SELECTOR_DEFINITION_REF_INVALID");
  if (definitionRef.definition_id !== definition.definition_id ||
      definitionRef.path !== expectedDefinitionPath ||
      sha(definitionRef.sha256, "FAMILY_POLICY_SELECTOR_DEFINITION_REF_INVALID") !==
        sha256StrategySelectionBytes(definitionBytes) ||
      definitionRef.definition_sha256 !== definition.definition_sha256) {
    return fail("FAMILY_POLICY_SELECTOR_DEFINITION_REF_STALE");
  }
  const catalogueRef = object(
    source.owner_catalogue_ref,
    "FAMILY_POLICY_SELECTOR_DENOMINATOR_CATALOGUE_REF_INVALID",
  );
  exactKeys(catalogueRef, ["catalogue_id", "path", "sha256", "catalogue_sha256"],
    "FAMILY_POLICY_SELECTOR_DENOMINATOR_CATALOGUE_REF_INVALID");
  if (canonicalStrategySelectionJson(catalogueRef) !==
      canonicalStrategySelectionJson(definition.catalogue_ref)) {
    return fail("FAMILY_POLICY_SELECTOR_DENOMINATOR_CATALOGUE_REF_STALE");
  }
  const contract = object(
    source.portable_contract,
    "FAMILY_POLICY_SELECTOR_DENOMINATOR_POLICY_INVALID",
  );
  exactKeys(contract, [
    "return_semantics", "dependency_contract", "effect_contract",
    "strategy_execution", "result_consumption", "quiescence", "observer_origin",
  ], "FAMILY_POLICY_SELECTOR_DENOMINATOR_POLICY_INVALID");
  if (contract.return_semantics !== "current-strategy-identity" ||
      contract.dependency_contract !== "explicit-inputs-only" ||
      contract.effect_contract !== "zero-observed-forbidden-effects" ||
      contract.strategy_execution !== "zero-attempts-during-selection" ||
      contract.result_consumption !== "complete-before-close" ||
      contract.quiescence !== "required-after-selection" ||
      contract.observer_origin !== "locked-harness-owned-not-provider") {
    return fail("FAMILY_POLICY_SELECTOR_DENOMINATOR_POLICY_INVALID");
  }
  const decisions = source.positive_decisions.map((value) =>
    string(value, "FAMILY_POLICY_SELECTOR_DENOMINATOR_DECISIONS_INVALID"));
  if (canonicalStrategySelectionJson([...decisions].sort(compareUtf8)) !==
      canonicalStrategySelectionJson([...STRATEGY_SELECTION_DECISIONS]
        .sort(compareUtf8))) {
    return fail("FAMILY_POLICY_SELECTOR_DENOMINATOR_DECISIONS_INVALID");
  }
  const withoutDigest = Object.freeze({
    schema_version: "StrategySelectionDenominator/v1" as const,
    denominator_id: identifier(
      source.denominator_id,
      "FAMILY_POLICY_SELECTOR_DENOMINATOR_ID_INVALID",
    ),
    owner_definition_ref: Object.freeze({
      definition_id: definition.definition_id,
      path: expectedDefinitionPath,
      sha256: sha(definitionRef.sha256, "FAMILY_POLICY_SELECTOR_DEFINITION_REF_INVALID"),
      definition_sha256: definition.definition_sha256,
    }),
    owner_catalogue_ref: Object.freeze({...definition.catalogue_ref}),
    portable_contract: Object.freeze({
      return_semantics: "current-strategy-identity" as const,
      dependency_contract: "explicit-inputs-only" as const,
      effect_contract: "zero-observed-forbidden-effects" as const,
      strategy_execution: "zero-attempts-during-selection" as const,
      result_consumption: "complete-before-close" as const,
      quiescence: "required-after-selection" as const,
      observer_origin: "locked-harness-owned-not-provider" as const,
    }),
    positive_decisions: Object.freeze([...STRATEGY_SELECTION_DECISIONS]),
    authority_effect: "none" as const,
  });
  const digest = sha(
    source.denominator_sha256,
    "FAMILY_POLICY_SELECTOR_DENOMINATOR_DIGEST_INVALID",
  );
  if (digest !== computeStrategySelectionDenominatorSha256(withoutDigest)) {
    return fail("FAMILY_POLICY_SELECTOR_DENOMINATOR_DIGEST_STALE");
  }
  return Object.freeze({
    catalogue,
    definition,
    denominator: Object.freeze({...withoutDigest, denominator_sha256: digest}),
  });
};

export const sha256StrategySelectionInputs = (
  inputs: Readonly<Record<string, StrategySelectionInputValueV1>>,
): string => sha256Json(inputs);
export const sha256SelectedStrategyIdentity = (
  value: string | boolean,
): string => sha256Json(value);

const executionBody = (
  value: Omit<StrategyExecutionObservationV1, "observation_sha256">,
): unknown => value;
export const computeStrategyExecutionObservationSha256 = (
  value: Omit<StrategyExecutionObservationV1, "observation_sha256">,
): string => sha256Json(executionBody(value));
export const mintStrategyExecutionObservationV1 = (
  value: Omit<StrategyExecutionObservationV1, "observation_sha256">,
): StrategyExecutionObservationV1 => Object.freeze({
  ...value,
  observer_ref: Object.freeze({...value.observer_ref}),
  target_ref: Object.freeze({...value.target_ref}),
  catalogue_ref: Object.freeze({...value.catalogue_ref}),
  covered_strategy_ids: Object.freeze([...value.covered_strategy_ids]),
  attempted_strategy_ids: Object.freeze([...value.attempted_strategy_ids]),
  observation_sha256: computeStrategyExecutionObservationSha256(value),
});

const decodeExecutionObserverRef = (
  value: unknown,
): LockedStrategyExecutionObserverRefV1 => {
  const ref = object(value, "FAMILY_POLICY_SELECTOR_EXECUTION_OBSERVER_REF_INVALID");
  exactKeys(ref, [
    "role", "observer_id", "observer_sha256", "owner_ref", "provider_id",
    "provider_sha256",
  ], "FAMILY_POLICY_SELECTOR_EXECUTION_OBSERVER_REF_INVALID");
  if (ref.role !== "independent-strategy-execution-observer") {
    return fail("FAMILY_POLICY_SELECTOR_EXECUTION_OBSERVER_REF_INVALID");
  }
  return Object.freeze({
    role: "independent-strategy-execution-observer" as const,
    observer_id: identifier(
      ref.observer_id,
      "FAMILY_POLICY_SELECTOR_EXECUTION_OBSERVER_REF_INVALID",
    ),
    observer_sha256: sha(
      ref.observer_sha256,
      "FAMILY_POLICY_SELECTOR_EXECUTION_OBSERVER_REF_INVALID",
    ),
    owner_ref: identifier(
      ref.owner_ref,
      "FAMILY_POLICY_SELECTOR_EXECUTION_OBSERVER_REF_INVALID",
    ),
    provider_id: identifier(
      ref.provider_id,
      "FAMILY_POLICY_SELECTOR_EXECUTION_OBSERVER_REF_INVALID",
    ),
    provider_sha256: sha(
      ref.provider_sha256,
      "FAMILY_POLICY_SELECTOR_EXECUTION_OBSERVER_REF_INVALID",
    ),
  });
};

export const decodeStrategyExecutionObservationV1 = (
  bytes: string,
): StrategyExecutionObservationV1 => {
  const source = parse(bytes, "FAMILY_POLICY_SELECTOR_EXECUTION_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "observation_id", "source_kind", "observer_ref",
    "target_ref", "catalogue_ref", "coverage", "covered_strategy_ids",
    "attempt_count", "attempted_strategy_ids", "completion_count",
    "authority_effect", "observation_sha256",
  ], "FAMILY_POLICY_SELECTOR_EXECUTION_SHAPE_INVALID");
  if (source.schema_version !== "StrategyExecutionObservation/v1" ||
      !["independent-owner-trap", "mutated-strategy-execution-trap"]
        .includes(String(source.source_kind)) ||
      !["all-owner-declared-strategies", "partial"].includes(String(source.coverage)) ||
      source.authority_effect !== "none" ||
      !Array.isArray(source.covered_strategy_ids) ||
      !Array.isArray(source.attempted_strategy_ids)) {
    return fail("FAMILY_POLICY_SELECTOR_EXECUTION_POLICY_INVALID");
  }
  const target = object(source.target_ref, "FAMILY_POLICY_SELECTOR_TARGET_REF_INVALID");
  exactKeys(target, ["target_id", "target_sha256"],
    "FAMILY_POLICY_SELECTOR_TARGET_REF_INVALID");
  const catalogueRef = object(
    source.catalogue_ref,
    "FAMILY_POLICY_SELECTOR_EXECUTION_CATALOGUE_REF_INVALID",
  );
  exactKeys(catalogueRef, ["catalogue_id", "catalogue_sha256"],
    "FAMILY_POLICY_SELECTOR_EXECUTION_CATALOGUE_REF_INVALID");
  const withoutDigest = Object.freeze({
    schema_version: "StrategyExecutionObservation/v1" as const,
    observation_id: identifier(
      source.observation_id,
      "FAMILY_POLICY_SELECTOR_EXECUTION_ID_INVALID",
    ),
    source_kind: source.source_kind as StrategyExecutionObservationV1["source_kind"],
    observer_ref: decodeExecutionObserverRef(source.observer_ref),
    target_ref: Object.freeze({
      target_id: identifier(target.target_id, "FAMILY_POLICY_SELECTOR_TARGET_REF_INVALID"),
      target_sha256: sha(target.target_sha256, "FAMILY_POLICY_SELECTOR_TARGET_REF_INVALID"),
    }),
    catalogue_ref: Object.freeze({
      catalogue_id: identifier(
        catalogueRef.catalogue_id,
        "FAMILY_POLICY_SELECTOR_EXECUTION_CATALOGUE_REF_INVALID",
      ),
      catalogue_sha256: sha(
        catalogueRef.catalogue_sha256,
        "FAMILY_POLICY_SELECTOR_EXECUTION_CATALOGUE_REF_INVALID",
      ),
    }),
    coverage: source.coverage as StrategyExecutionObservationV1["coverage"],
    covered_strategy_ids: Object.freeze(source.covered_strategy_ids.map((value) =>
      identifier(value, "FAMILY_POLICY_SELECTOR_EXECUTION_STRATEGY_ID_INVALID"))),
    attempt_count: count(
      source.attempt_count,
      "FAMILY_POLICY_SELECTOR_EXECUTION_COUNT_INVALID",
    ),
    attempted_strategy_ids: Object.freeze(source.attempted_strategy_ids.map((value) =>
      identifier(value, "FAMILY_POLICY_SELECTOR_EXECUTION_STRATEGY_ID_INVALID"))),
    completion_count: count(
      source.completion_count,
      "FAMILY_POLICY_SELECTOR_EXECUTION_COUNT_INVALID",
    ),
    authority_effect: "none" as const,
  });
  const digest = sha(
    source.observation_sha256,
    "FAMILY_POLICY_SELECTOR_EXECUTION_DIGEST_INVALID",
  );
  if (digest !== computeStrategyExecutionObservationSha256(withoutDigest)) {
    return fail("FAMILY_POLICY_SELECTOR_EXECUTION_DIGEST_STALE");
  }
  return Object.freeze({...withoutDigest, observation_sha256: digest});
};

const observationBody = (
  value: Omit<StrategySelectionObservationV1, "observation_sha256">,
): unknown => value;
export const computeStrategySelectionObservationSha256 = (
  value: Omit<StrategySelectionObservationV1, "observation_sha256">,
): string => sha256Json(observationBody(value));
export const mintStrategySelectionObservationV1 = (
  value: Omit<StrategySelectionObservationV1, "observation_sha256">,
): StrategySelectionObservationV1 => Object.freeze({
  ...value,
  target: Object.freeze({...value.target}),
  definition_ref: Object.freeze({...value.definition_ref}),
  catalogue_ref: Object.freeze({...value.catalogue_ref}),
  binding: Object.freeze({...value.binding}),
  cases: Object.freeze(value.cases.map((item) => Object.freeze({
    ...item,
    consumed_input_facts: Object.freeze([...item.consumed_input_facts]),
  }))),
  observation_sha256: computeStrategySelectionObservationSha256(value),
});

export const decodeStrategySelectionObservationV1 = (
  bytes: string,
): StrategySelectionObservationV1 => {
  const source = parse(bytes, "FAMILY_POLICY_SELECTOR_OBSERVATION_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "observation_id", "source_kind", "target",
    "definition_ref", "catalogue_ref", "binding", "cases",
    "effect_observation", "strategy_execution_observation", "authority_effect",
    "observation_sha256",
  ], "FAMILY_POLICY_SELECTOR_OBSERVATION_SHAPE_INVALID");
  if (source.schema_version !== "StrategySelectionObservation/v1" ||
      !["independent-family-fixture", "target-observation", "mutated-family-observation"]
        .includes(String(source.source_kind)) ||
      source.authority_effect !== "none" || !Array.isArray(source.cases)) {
    return fail("FAMILY_POLICY_SELECTOR_OBSERVATION_POLICY_INVALID");
  }
  const target = object(source.target, "FAMILY_POLICY_SELECTOR_TARGET_INVALID");
  exactKeys(target, ["target_id", "target_sha256", "language", "protocol_id"],
    "FAMILY_POLICY_SELECTOR_TARGET_INVALID");
  if (!["family-fixture", "typescript", "python", "rust"]
    .includes(String(target.language))) {
    return fail("FAMILY_POLICY_SELECTOR_TARGET_INVALID");
  }
  const definitionRef = object(
    source.definition_ref,
    "FAMILY_POLICY_SELECTOR_OBSERVATION_DEFINITION_REF_INVALID",
  );
  exactKeys(definitionRef, ["definition_id", "path", "sha256", "definition_sha256"],
    "FAMILY_POLICY_SELECTOR_OBSERVATION_DEFINITION_REF_INVALID");
  const catalogueRef = object(
    source.catalogue_ref,
    "FAMILY_POLICY_SELECTOR_OBSERVATION_CATALOGUE_REF_INVALID",
  );
  exactKeys(catalogueRef, ["catalogue_id", "catalogue_sha256"],
    "FAMILY_POLICY_SELECTOR_OBSERVATION_CATALOGUE_REF_INVALID");
  const binding = object(source.binding, "FAMILY_POLICY_SELECTOR_BINDING_INVALID");
  exactKeys(binding, [
    "descriptor_id", "descriptor_sha256", "provider_id", "provider_sha256",
  ], "FAMILY_POLICY_SELECTOR_BINDING_INVALID");
  const cases = source.cases.map((value) => {
    const item = object(value, "FAMILY_POLICY_SELECTOR_OBSERVED_CASE_INVALID");
    exactKeys(item, [
      "case_id", "input_sha256", "selected_kind", "selected_strategy_id",
      "selected_sha256", "branch_id", "consumed_input_facts",
    ], "FAMILY_POLICY_SELECTOR_OBSERVED_CASE_INVALID");
    if (!["strategy-id", "boolean"].includes(String(item.selected_kind)) ||
        (typeof item.selected_strategy_id !== "string" &&
          typeof item.selected_strategy_id !== "boolean") ||
        !Array.isArray(item.consumed_input_facts)) {
      return fail("FAMILY_POLICY_SELECTOR_OBSERVED_CASE_INVALID");
    }
    return Object.freeze({
      case_id: identifier(item.case_id, "FAMILY_POLICY_SELECTOR_OBSERVED_CASE_INVALID"),
      input_sha256: sha(
        item.input_sha256,
        "FAMILY_POLICY_SELECTOR_OBSERVED_CASE_INVALID",
      ),
      selected_kind: item.selected_kind as "strategy-id" | "boolean",
      selected_strategy_id: item.selected_strategy_id as string | boolean,
      selected_sha256: sha(
        item.selected_sha256,
        "FAMILY_POLICY_SELECTOR_OBSERVED_CASE_INVALID",
      ),
      branch_id: identifier(item.branch_id, "FAMILY_POLICY_SELECTOR_OBSERVED_CASE_INVALID"),
      consumed_input_facts: Object.freeze(item.consumed_input_facts.map((value) =>
        identifier(value, "FAMILY_POLICY_SELECTOR_OBSERVED_CASE_INVALID"))),
    });
  });
  const withoutDigest = Object.freeze({
    schema_version: "StrategySelectionObservation/v1" as const,
    observation_id: identifier(
      source.observation_id,
      "FAMILY_POLICY_SELECTOR_OBSERVATION_ID_INVALID",
    ),
    source_kind: source.source_kind as StrategySelectionObservationV1["source_kind"],
    target: Object.freeze({
      target_id: identifier(target.target_id, "FAMILY_POLICY_SELECTOR_TARGET_INVALID"),
      target_sha256: sha(target.target_sha256, "FAMILY_POLICY_SELECTOR_TARGET_INVALID"),
      language: target.language as StrategySelectionObservationV1["target"]["language"],
      protocol_id: identifier(target.protocol_id, "FAMILY_POLICY_SELECTOR_TARGET_INVALID"),
    }),
    definition_ref: Object.freeze({
      definition_id: identifier(
        definitionRef.definition_id,
        "FAMILY_POLICY_SELECTOR_OBSERVATION_DEFINITION_REF_INVALID",
      ),
      path: string(
        definitionRef.path,
        "FAMILY_POLICY_SELECTOR_OBSERVATION_DEFINITION_REF_INVALID",
      ),
      sha256: sha(
        definitionRef.sha256,
        "FAMILY_POLICY_SELECTOR_OBSERVATION_DEFINITION_REF_INVALID",
      ),
      definition_sha256: sha(
        definitionRef.definition_sha256,
        "FAMILY_POLICY_SELECTOR_OBSERVATION_DEFINITION_REF_INVALID",
      ),
    }),
    catalogue_ref: Object.freeze({
      catalogue_id: identifier(
        catalogueRef.catalogue_id,
        "FAMILY_POLICY_SELECTOR_OBSERVATION_CATALOGUE_REF_INVALID",
      ),
      catalogue_sha256: sha(
        catalogueRef.catalogue_sha256,
        "FAMILY_POLICY_SELECTOR_OBSERVATION_CATALOGUE_REF_INVALID",
      ),
    }),
    binding: Object.freeze({
      descriptor_id: identifier(
        binding.descriptor_id,
        "FAMILY_POLICY_SELECTOR_BINDING_INVALID",
      ),
      descriptor_sha256: sha(
        binding.descriptor_sha256,
        "FAMILY_POLICY_SELECTOR_BINDING_INVALID",
      ),
      provider_id: identifier(binding.provider_id, "FAMILY_POLICY_SELECTOR_BINDING_INVALID"),
      provider_sha256: sha(
        binding.provider_sha256,
        "FAMILY_POLICY_SELECTOR_BINDING_INVALID",
      ),
    }),
    cases: Object.freeze(cases),
    effect_observation: decodeEffectObservationV1(
      canonicalStrategySelectionJson(source.effect_observation),
    ),
    strategy_execution_observation: decodeStrategyExecutionObservationV1(
      canonicalStrategySelectionJson(source.strategy_execution_observation),
    ),
    authority_effect: "none" as const,
  });
  const digest = sha(
    source.observation_sha256,
    "FAMILY_POLICY_SELECTOR_OBSERVATION_DIGEST_INVALID",
  );
  if (digest !== computeStrategySelectionObservationSha256(withoutDigest)) {
    return fail("FAMILY_POLICY_SELECTOR_OBSERVATION_DIGEST_STALE");
  }
  return Object.freeze({...withoutDigest, observation_sha256: digest});
};

export const decodeStrategySelectionMutationCatalogueV1 = (
  bytes: string,
): StrategySelectionMutationCatalogueV1 => {
  const source = parse(bytes, "FAMILY_POLICY_SELECTOR_MUTATIONS_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "denominator_ref", "authorship",
    "target_code_may_read_expected_findings", "mutations", "authority_effect",
    "catalogue_sha256",
  ], "FAMILY_POLICY_SELECTOR_MUTATIONS_SHAPE_INVALID");
  if (source.schema_version !== "StrategySelectionMutationCatalogue/v1" ||
      source.authorship !== "independent-family-fixture" ||
      source.target_code_may_read_expected_findings !== false ||
      source.authority_effect !== "none" || !Array.isArray(source.mutations)) {
    return fail("FAMILY_POLICY_SELECTOR_MUTATIONS_POLICY_INVALID");
  }
  const ref = object(source.denominator_ref,
    "FAMILY_POLICY_SELECTOR_MUTATIONS_REF_INVALID");
  exactKeys(ref, ["denominator_id", "denominator_sha256"],
    "FAMILY_POLICY_SELECTOR_MUTATIONS_REF_INVALID");
  const mutations = source.mutations.map((value) => {
    const mutation = object(value, "FAMILY_POLICY_SELECTOR_MUTATION_INVALID");
    exactKeys(mutation, ["mutation_id", "mutation_kind", "expected_finding_codes"],
      "FAMILY_POLICY_SELECTOR_MUTATION_INVALID");
    if (!STRATEGY_SELECTION_MUTATION_KINDS.includes(mutation.mutation_kind as never) ||
        !Array.isArray(mutation.expected_finding_codes) ||
        mutation.expected_finding_codes.length === 0) {
      return fail("FAMILY_POLICY_SELECTOR_MUTATION_INVALID");
    }
    return Object.freeze({
      mutation_id: identifier(
        mutation.mutation_id,
        "FAMILY_POLICY_SELECTOR_MUTATION_INVALID",
      ),
      mutation_kind: mutation.mutation_kind as StrategySelectionMutationKind,
      expected_finding_codes: Object.freeze(mutation.expected_finding_codes.map((item) =>
        string(item, "FAMILY_POLICY_SELECTOR_MUTATION_INVALID"))) as any,
    });
  });
  if (mutations.length !== STRATEGY_SELECTION_MUTATION_KINDS.length ||
      !unique(mutations.map(({mutation_kind: kind}) => kind))) {
    return fail("FAMILY_POLICY_SELECTOR_MUTATIONS_POLICY_INVALID");
  }
  const body = Object.freeze({
    schema_version: "StrategySelectionMutationCatalogue/v1" as const,
    denominator_ref: Object.freeze({
      denominator_id: identifier(
        ref.denominator_id,
        "FAMILY_POLICY_SELECTOR_MUTATIONS_REF_INVALID",
      ),
      denominator_sha256: sha(
        ref.denominator_sha256,
        "FAMILY_POLICY_SELECTOR_MUTATIONS_REF_INVALID",
      ),
    }),
    authorship: "independent-family-fixture" as const,
    target_code_may_read_expected_findings: false as const,
    mutations: Object.freeze(mutations),
    authority_effect: "none" as const,
  });
  const digest = sha(
    source.catalogue_sha256,
    "FAMILY_POLICY_SELECTOR_MUTATIONS_DIGEST_INVALID",
  );
  if (digest !== sha256Json(body)) {
    return fail("FAMILY_POLICY_SELECTOR_MUTATIONS_DIGEST_STALE");
  }
  return Object.freeze({...body, catalogue_sha256: digest});
};
