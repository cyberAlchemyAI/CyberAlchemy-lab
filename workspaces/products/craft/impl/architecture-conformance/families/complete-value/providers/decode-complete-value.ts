import {createHash} from "node:crypto";

import {
  canonicalConstructionObservationJson,
  decodeConstructionObservationV1,
  type ConstructionFactoryRefV1,
  type ConstructionValidatorRefV1,
} from "../../../kernel/evidence/construction-observation/index.js";
import {
  COMPLETE_VALUE_DECISIONS,
  COMPLETE_VALUE_HOSTILE_CLASSES,
  COMPLETE_VALUE_MUTATION_BLUEPRINT,
  COMPLETE_VALUE_MUTATION_KINDS,
  type CompleteValueDefinitionV1,
  type CompleteValueDenominatorV1,
  type CompleteValueFindingCode,
  type CompleteValueHostileClass,
  type CompleteValueMutationCatalogueV1,
  type CompleteValueMutationKind,
  type CompleteValueMutationV1,
  type CompleteValueObservationV1,
} from "../contracts/complete-value-contracts.js";

type JsonObject = Record<string, unknown>;
const SHA256 = /^[a-f0-9]{64}$/u;
const IDENTIFIER = /^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$/u;
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const isRecord = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const fail = (code: string): never => {
  const error = Object.assign(new Error(code), {code});
  error.name = "CompleteValueDecodeError";
  throw error;
};
const exactKeys = (source: JsonObject, keys: readonly string[], code: string): void => {
  const actual = Object.keys(source).sort(compareUtf8);
  const expected = [...keys].sort(compareUtf8);
  if (JSON.stringify(actual) !== JSON.stringify(expected)) fail(code);
};
const expectObject = (value: unknown, code: string): JsonObject =>
  isRecord(value) ? value : fail(code);
const expectArray = (value: unknown, code: string): readonly unknown[] =>
  Array.isArray(value) ? value : fail(code);
const expectString = (value: unknown, code: string): string =>
  typeof value === "string" && IDENTIFIER.test(value) ? value : fail(code);
const expectSha = (value: unknown, code: string): string =>
  typeof value === "string" && SHA256.test(value) ? value : fail(code);
const parseJson = (bytes: string, code: string): JsonObject => {
  try {
    return expectObject(JSON.parse(bytes), code);
  } catch (error) {
    if (error instanceof Error && error.name === "CompleteValueDecodeError") throw error;
    return fail(code);
  }
};
const sha256 = (bytes: string): string =>
  createHash("sha256").update(bytes, "utf8").digest("hex");
const canonicalSha256 = (value: unknown): string =>
  sha256(canonicalConstructionObservationJson(value));
const same = (left: unknown, right: unknown): boolean =>
  canonicalConstructionObservationJson(left) ===
    canonicalConstructionObservationJson(right);
const exactSet = (values: readonly string[], expected: readonly string[]): boolean =>
  new Set(values).size === values.length
    && same([...values].sort(compareUtf8), [...expected].sort(compareUtf8));

const decodeFactory = (value: unknown): ConstructionFactoryRefV1 => {
  const source = expectObject(value, "FAMILY_VALUE_DEFINITION_FACTORY_INVALID");
  exactKeys(source, ["factory_id", "factory_sha256", "concept_id"],
    "FAMILY_VALUE_DEFINITION_FACTORY_SHAPE_INVALID");
  return Object.freeze({
    factory_id: expectString(source.factory_id,
      "FAMILY_VALUE_DEFINITION_FACTORY_INVALID"),
    factory_sha256: expectSha(source.factory_sha256,
      "FAMILY_VALUE_DEFINITION_FACTORY_INVALID"),
    concept_id: expectString(source.concept_id,
      "FAMILY_VALUE_DEFINITION_FACTORY_INVALID"),
  });
};

const decodeValidator = (value: unknown): ConstructionValidatorRefV1 => {
  const source = expectObject(value, "FAMILY_VALUE_DEFINITION_VALIDATOR_INVALID");
  exactKeys(source, ["validator_id", "validator_sha256", "origin"],
    "FAMILY_VALUE_DEFINITION_VALIDATOR_SHAPE_INVALID");
  if (source.origin !== "base" && source.origin !== "extension") {
    return fail("FAMILY_VALUE_DEFINITION_VALIDATOR_INVALID");
  }
  return Object.freeze({
    validator_id: expectString(source.validator_id,
      "FAMILY_VALUE_DEFINITION_VALIDATOR_INVALID"),
    validator_sha256: expectSha(source.validator_sha256,
      "FAMILY_VALUE_DEFINITION_VALIDATOR_INVALID"),
    origin: source.origin,
  });
};

export const decodeCompleteValueDefinitionV1 = (
  bytes: string,
  expectedDescriptorPath: string,
  descriptorBytes: string,
): CompleteValueDefinitionV1 => {
  const source = parseJson(bytes, "FAMILY_VALUE_DEFINITION_JSON_INVALID");
  exactKeys(source, ["schema_version", "definition_id", "status", "authorship",
    "derivation_policy", "descriptor_ref", "concept_id", "factories",
    "components", "validators", "cases", "equality_contract", "authority_effect"],
  "FAMILY_VALUE_DEFINITION_SHAPE_INVALID");
  if (source.schema_version !== "CompleteValueDefinition/v1"
      || source.status !== "candidate-fixture"
      || source.authorship !== "owner-authored-admission-input"
      || source.derivation_policy
        !== "implementation-and-generated-results-forbidden-as-authority"
      || source.authority_effect !== "none") {
    return fail("FAMILY_VALUE_DEFINITION_POLICY_INVALID");
  }
  const descriptorRef = expectObject(source.descriptor_ref,
    "FAMILY_VALUE_DEFINITION_DESCRIPTOR_REF_INVALID");
  exactKeys(descriptorRef, ["descriptor_id", "path", "sha256"],
    "FAMILY_VALUE_DEFINITION_DESCRIPTOR_REF_SHAPE_INVALID");
  const descriptor = parseJson(descriptorBytes,
    "FAMILY_VALUE_DEFINITION_DESCRIPTOR_JSON_INVALID");
  if (descriptorRef.path !== expectedDescriptorPath
      || descriptorRef.sha256 !== sha256(descriptorBytes)
      || descriptorRef.descriptor_id !== descriptor.descriptor_id) {
    return fail("FAMILY_VALUE_DEFINITION_DESCRIPTOR_REF_STALE");
  }
  const conceptId = expectString(source.concept_id,
    "FAMILY_VALUE_DEFINITION_CONCEPT_INVALID");
  const factories = expectObject(source.factories,
    "FAMILY_VALUE_DEFINITION_FACTORIES_INVALID");
  exactKeys(factories, ["base", "extension"],
    "FAMILY_VALUE_DEFINITION_FACTORIES_SHAPE_INVALID");
  const base = decodeFactory(factories.base);
  const extension = decodeFactory(factories.extension);
  if (base.concept_id !== conceptId || extension.concept_id !== conceptId
      || base.factory_id === extension.factory_id) {
    return fail("FAMILY_VALUE_DEFINITION_FACTORY_INVALID");
  }
  const components = expectArray(source.components,
    "FAMILY_VALUE_DEFINITION_COMPONENTS_INVALID").map((value) => {
    const component = expectObject(value, "FAMILY_VALUE_DEFINITION_COMPONENT_INVALID");
    exactKeys(component, ["component_name", "protocol_id", "protocol_sha256",
      "nested_value_object"], "FAMILY_VALUE_DEFINITION_COMPONENT_SHAPE_INVALID");
    if (typeof component.nested_value_object !== "boolean") {
      return fail("FAMILY_VALUE_DEFINITION_COMPONENT_INVALID");
    }
    return Object.freeze({
      component_name: expectString(component.component_name,
        "FAMILY_VALUE_DEFINITION_COMPONENT_INVALID"),
      protocol_id: expectString(component.protocol_id,
        "FAMILY_VALUE_DEFINITION_COMPONENT_INVALID"),
      protocol_sha256: expectSha(component.protocol_sha256,
        "FAMILY_VALUE_DEFINITION_COMPONENT_INVALID"),
      nested_value_object: component.nested_value_object,
    });
  });
  const componentNames = components.map(({component_name}) => component_name);
  if (components.length < 2 || new Set(componentNames).size !== components.length
      || !components.some(({nested_value_object}) => nested_value_object)) {
    return fail("FAMILY_VALUE_DEFINITION_COMPONENTS_INVALID");
  }
  const validators = expectArray(source.validators,
    "FAMILY_VALUE_DEFINITION_VALIDATORS_INVALID").map(decodeValidator);
  const validatorIds = validators.map(({validator_id}) => validator_id);
  const firstExtension = validators.findIndex(({origin}) => origin === "extension");
  if (validators.length < 2 || new Set(validatorIds).size !== validators.length
      || firstExtension <= 0
      || validators.slice(firstExtension).some(({origin}) => origin !== "extension")) {
    return fail("FAMILY_VALUE_DEFINITION_VALIDATORS_INVALID");
  }
  const cases = expectArray(source.cases,
    "FAMILY_VALUE_DEFINITION_CASES_INVALID").map((value) => {
    const testCase = expectObject(value, "FAMILY_VALUE_DEFINITION_CASE_INVALID");
    exactKeys(testCase, ["case_id", "input_class", "normalized_component_values",
      "expected_failure_codes"], "FAMILY_VALUE_DEFINITION_CASE_SHAPE_INVALID");
    if (testCase.input_class !== "valid" && testCase.input_class !== "invalid") {
      return fail("FAMILY_VALUE_DEFINITION_CASE_INVALID");
    }
    const values = expectObject(testCase.normalized_component_values,
      "FAMILY_VALUE_DEFINITION_CASE_VALUES_INVALID");
    if (!exactSet(Object.keys(values), componentNames)) {
      return fail("FAMILY_VALUE_DEFINITION_CASE_VALUES_INVALID");
    }
    const normalizedValues = Object.fromEntries(componentNames.map((name) =>
      [name, expectSha(values[name], "FAMILY_VALUE_DEFINITION_CASE_VALUES_INVALID")]));
    const failures = expectArray(testCase.expected_failure_codes,
      "FAMILY_VALUE_DEFINITION_CASE_FAILURES_INVALID").map((item) =>
      expectString(item, "FAMILY_VALUE_DEFINITION_CASE_FAILURES_INVALID"));
    if ((testCase.input_class === "valid" && failures.length !== 0)
        || (testCase.input_class === "invalid" && failures.length === 0)) {
      return fail("FAMILY_VALUE_DEFINITION_CASE_FAILURES_INVALID");
    }
    return Object.freeze({
      case_id: expectString(testCase.case_id,
        "FAMILY_VALUE_DEFINITION_CASE_INVALID"),
      input_class: testCase.input_class,
      normalized_component_values: Object.freeze(normalizedValues),
      expected_failure_codes: Object.freeze(failures),
    });
  });
  const caseIds = cases.map(({case_id}) => case_id);
  if (new Set(caseIds).size !== cases.length
      || cases.filter(({input_class}) => input_class === "valid").length
        < components.length + 2
      || !cases.some(({input_class}) => input_class === "invalid")) {
    return fail("FAMILY_VALUE_DEFINITION_CASES_INVALID");
  }
  const equality = expectObject(source.equality_contract,
    "FAMILY_VALUE_DEFINITION_EQUALITY_INVALID");
  exactKeys(equality, ["equal_probe", "component_variants", "collision_freedom_claim"],
    "FAMILY_VALUE_DEFINITION_EQUALITY_SHAPE_INVALID");
  if (equality.collision_freedom_claim !== false) {
    return fail("FAMILY_VALUE_DEFINITION_EQUALITY_INVALID");
  }
  const equalProbe = expectObject(equality.equal_probe,
    "FAMILY_VALUE_DEFINITION_EQUAL_PROBE_INVALID");
  exactKeys(equalProbe, ["probe_id", "left_case_id", "right_case_id"],
    "FAMILY_VALUE_DEFINITION_EQUAL_PROBE_SHAPE_INVALID");
  const decodedEqualProbe = Object.freeze({
    probe_id: expectString(equalProbe.probe_id,
      "FAMILY_VALUE_DEFINITION_EQUAL_PROBE_INVALID"),
    left_case_id: expectString(equalProbe.left_case_id,
      "FAMILY_VALUE_DEFINITION_EQUAL_PROBE_INVALID"),
    right_case_id: expectString(equalProbe.right_case_id,
      "FAMILY_VALUE_DEFINITION_EQUAL_PROBE_INVALID"),
  });
  const caseById = new Map(cases.map((item) => [item.case_id, item]));
  const equalLeft = caseById.get(decodedEqualProbe.left_case_id);
  const equalRight = caseById.get(decodedEqualProbe.right_case_id);
  if (!equalLeft || !equalRight || equalLeft.input_class !== "valid"
      || equalRight.input_class !== "valid"
      || !same(equalLeft.normalized_component_values,
        equalRight.normalized_component_values)) {
    return fail("FAMILY_VALUE_DEFINITION_EQUAL_PROBE_INVALID");
  }
  const variants = expectArray(equality.component_variants,
    "FAMILY_VALUE_DEFINITION_VARIANTS_INVALID").map((value) => {
    const variant = expectObject(value, "FAMILY_VALUE_DEFINITION_VARIANT_INVALID");
    exactKeys(variant, ["probe_id", "component_name", "left_case_id",
      "right_case_id"], "FAMILY_VALUE_DEFINITION_VARIANT_SHAPE_INVALID");
    const decoded = Object.freeze({
      probe_id: expectString(variant.probe_id,
        "FAMILY_VALUE_DEFINITION_VARIANT_INVALID"),
      component_name: expectString(variant.component_name,
        "FAMILY_VALUE_DEFINITION_VARIANT_INVALID"),
      left_case_id: expectString(variant.left_case_id,
        "FAMILY_VALUE_DEFINITION_VARIANT_INVALID"),
      right_case_id: expectString(variant.right_case_id,
        "FAMILY_VALUE_DEFINITION_VARIANT_INVALID"),
    });
    const left = caseById.get(decoded.left_case_id);
    const right = caseById.get(decoded.right_case_id);
    const changed = componentNames.filter((name) =>
      left?.normalized_component_values[name]
        !== right?.normalized_component_values[name]);
    if (!componentNames.includes(decoded.component_name) || !left || !right
        || left.input_class !== "valid" || right.input_class !== "valid"
        || !same(changed, [decoded.component_name])) {
      return fail("FAMILY_VALUE_DEFINITION_VARIANT_INVALID");
    }
    return decoded;
  });
  if (!exactSet(variants.map(({component_name}) => component_name), componentNames)
      || new Set([decodedEqualProbe.probe_id,
        ...variants.map(({probe_id}) => probe_id)]).size !== variants.length + 1) {
    return fail("FAMILY_VALUE_DEFINITION_VARIANTS_INVALID");
  }
  return Object.freeze({
    schema_version: "CompleteValueDefinition/v1" as const,
    definition_id: expectString(source.definition_id,
      "FAMILY_VALUE_DEFINITION_ID_INVALID"),
    status: "candidate-fixture" as const,
    authorship: "owner-authored-admission-input" as const,
    derivation_policy:
      "implementation-and-generated-results-forbidden-as-authority" as const,
    descriptor_ref: Object.freeze({
      descriptor_id: expectString(descriptorRef.descriptor_id,
        "FAMILY_VALUE_DEFINITION_DESCRIPTOR_REF_INVALID"),
      path: expectedDescriptorPath,
      sha256: expectSha(descriptorRef.sha256,
        "FAMILY_VALUE_DEFINITION_DESCRIPTOR_REF_INVALID"),
    }),
    concept_id: conceptId,
    factories: Object.freeze({base, extension}),
    components: Object.freeze(components),
    validators: Object.freeze(validators),
    cases: Object.freeze(cases),
    equality_contract: Object.freeze({
      equal_probe: decodedEqualProbe,
      component_variants: Object.freeze(variants),
      collision_freedom_claim: false as const,
    }),
    authority_effect: "none" as const,
  });
};

const denominatorBody = (
  value: Omit<CompleteValueDenominatorV1, "denominator_sha256">,
): unknown => ({
  ...value,
  positive_decisions: [...value.positive_decisions].sort(compareUtf8),
  semantic_hostile_classes: [...value.semantic_hostile_classes].sort(compareUtf8),
});
export const computeCompleteValueDenominatorSha256 = (
  value: Omit<CompleteValueDenominatorV1, "denominator_sha256">,
): string => canonicalSha256(denominatorBody(value));

export const decodeCompleteValueDenominatorV1 = (
  bytes: string,
  ownerDefinitionBytes: string,
  ownerDefinition: CompleteValueDefinitionV1,
  expectedOwnerPath: string,
): CompleteValueDenominatorV1 => {
  const source = parseJson(bytes, "FAMILY_VALUE_DENOMINATOR_JSON_INVALID");
  exactKeys(source, ["schema_version", "denominator_id", "owner_definition_ref",
    "portable_contract", "positive_decisions", "semantic_hostile_classes",
    "authority_effect", "denominator_sha256"],
  "FAMILY_VALUE_DENOMINATOR_SHAPE_INVALID");
  if (source.schema_version !== "CompleteValueDenominator/v1"
      || source.authority_effect !== "none") {
    return fail("FAMILY_VALUE_DENOMINATOR_POLICY_INVALID");
  }
  const ownerRef = expectObject(source.owner_definition_ref,
    "FAMILY_VALUE_DENOMINATOR_OWNER_REF_INVALID");
  exactKeys(ownerRef, ["definition_id", "path", "sha256"],
    "FAMILY_VALUE_DENOMINATOR_OWNER_REF_SHAPE_INVALID");
  if (ownerRef.definition_id !== ownerDefinition.definition_id
      || ownerRef.path !== expectedOwnerPath
      || ownerRef.sha256 !== sha256(ownerDefinitionBytes)) {
    return fail("FAMILY_VALUE_DENOMINATOR_OWNER_REF_STALE");
  }
  const portable = expectObject(source.portable_contract,
    "FAMILY_VALUE_DENOMINATOR_POLICY_INVALID");
  exactKeys(portable, ["component_admission", "validator_order",
    "formation_failure", "equality", "hash", "immutability", "extension",
    "evidence_origin"], "FAMILY_VALUE_DENOMINATOR_POLICY_INVALID");
  if (portable.component_admission
      !== "exact-current-owner-protocol-identity-and-digest"
      || portable.validator_order !== "base-before-extension-before-formation"
      || portable.formation_failure !== "structured-failure-no-object"
      || portable.equality !== "complete-normalized-tuple"
      || portable.hash
        !== "same-normalized-complete-tuple-congruent-not-collision-free"
      || portable.immutability !== "formed-and-recursive-owned-components"
      || portable.extension !== "additive-validation-only-acyclic"
      || portable.evidence_origin !== "locked-independent-owner-not-provider") {
    return fail("FAMILY_VALUE_DENOMINATOR_POLICY_INVALID");
  }
  const decisions = expectArray(source.positive_decisions,
    "FAMILY_VALUE_DENOMINATOR_DECISIONS_INVALID").map((item) =>
    expectString(item, "FAMILY_VALUE_DENOMINATOR_DECISIONS_INVALID"));
  const hostiles = expectArray(source.semantic_hostile_classes,
    "FAMILY_VALUE_DENOMINATOR_HOSTILES_INVALID").map((item) =>
    expectString(item, "FAMILY_VALUE_DENOMINATOR_HOSTILES_INVALID"));
  if (!exactSet(decisions, COMPLETE_VALUE_DECISIONS)
      || !exactSet(hostiles, COMPLETE_VALUE_HOSTILE_CLASSES)) {
    return fail("FAMILY_VALUE_DENOMINATOR_SCOPE_INVALID");
  }
  const withoutDigest = {
    schema_version: "CompleteValueDenominator/v1" as const,
    denominator_id: expectString(source.denominator_id,
      "FAMILY_VALUE_DENOMINATOR_ID_INVALID"),
    owner_definition_ref: Object.freeze({
      definition_id: ownerDefinition.definition_id,
      path: expectedOwnerPath,
      sha256: expectSha(ownerRef.sha256,
        "FAMILY_VALUE_DENOMINATOR_OWNER_REF_INVALID"),
    }),
    portable_contract: Object.freeze({
      component_admission:
        "exact-current-owner-protocol-identity-and-digest" as const,
      validator_order: "base-before-extension-before-formation" as const,
      formation_failure: "structured-failure-no-object" as const,
      equality: "complete-normalized-tuple" as const,
      hash: "same-normalized-complete-tuple-congruent-not-collision-free" as const,
      immutability: "formed-and-recursive-owned-components" as const,
      extension: "additive-validation-only-acyclic" as const,
      evidence_origin: "locked-independent-owner-not-provider" as const,
    }),
    positive_decisions: Object.freeze([...COMPLETE_VALUE_DECISIONS]),
    semantic_hostile_classes: Object.freeze([...COMPLETE_VALUE_HOSTILE_CLASSES]),
    authority_effect: "none" as const,
  };
  const digest = expectSha(source.denominator_sha256,
    "FAMILY_VALUE_DENOMINATOR_DIGEST_INVALID");
  if (digest !== computeCompleteValueDenominatorSha256(withoutDigest)) {
    return fail("FAMILY_VALUE_DENOMINATOR_DIGEST_STALE");
  }
  return Object.freeze({...withoutDigest, denominator_sha256: digest});
};

const FINDING_CODES = new Set<CompleteValueFindingCode>([
  "FAMILY_VALUE_TARGET_OBSERVATION_MISSING",
  "FAMILY_VALUE_DEFINITION_PROVENANCE_MISMATCH",
  "FAMILY_VALUE_EVIDENCE_NOT_INDEPENDENT",
  "FAMILY_VALUE_FACTORY_BINDING_MISMATCH",
  "FAMILY_VALUE_REFERENCE_IDENTITY",
  "FAMILY_VALUE_PARTIAL_TUPLE_EQUALITY",
  "FAMILY_VALUE_INCONGRUENT_HASH",
  "FAMILY_VALUE_MUTABLE_NESTED_COMPONENT",
  "FAMILY_VALUE_VALIDATOR_BYPASS",
  "FAMILY_VALUE_TUPLE_CHANGING_EXTENSION",
  "FAMILY_VALUE_COMPONENT_PROTOCOL_MISMATCH",
  "FAMILY_VALUE_INVALID_INPUT_FORMED",
  "FAMILY_VALUE_NESTED_DELEGATION_MISMATCH",
  "FAMILY_VALUE_CASE_LEDGER_MISMATCH",
]);
const catalogueBody = (
  value: Omit<CompleteValueMutationCatalogueV1, "catalogue_sha256">,
): unknown => value;
export const computeCompleteValueCatalogueSha256 = (
  value: Omit<CompleteValueMutationCatalogueV1, "catalogue_sha256">,
): string => canonicalSha256(catalogueBody(value));

export const decodeCompleteValueMutationCatalogueV1 = (
  bytes: string,
  denominator: CompleteValueDenominatorV1,
  definition: CompleteValueDefinitionV1,
): CompleteValueMutationCatalogueV1 => {
  const source = parseJson(bytes, "FAMILY_VALUE_MUTATION_CATALOGUE_JSON_INVALID");
  exactKeys(source, ["schema_version", "denominator_ref", "authorship",
    "target_code_may_read_expected_findings", "mutations", "authority_effect",
    "catalogue_sha256"], "FAMILY_VALUE_MUTATION_CATALOGUE_SHAPE_INVALID");
  if (source.schema_version !== "CompleteValueMutationCatalogue/v1"
      || source.authorship !== "independent-family-fixture"
      || source.target_code_may_read_expected_findings !== false
      || source.authority_effect !== "none") {
    return fail("FAMILY_VALUE_MUTATION_CATALOGUE_POLICY_INVALID");
  }
  const denominatorRef = expectObject(source.denominator_ref,
    "FAMILY_VALUE_MUTATION_CATALOGUE_DENOMINATOR_REF_INVALID");
  exactKeys(denominatorRef, ["denominator_id", "denominator_sha256"],
    "FAMILY_VALUE_MUTATION_CATALOGUE_DENOMINATOR_REF_SHAPE_INVALID");
  if (denominatorRef.denominator_id !== denominator.denominator_id
      || denominatorRef.denominator_sha256 !== denominator.denominator_sha256) {
    return fail("FAMILY_VALUE_MUTATION_CATALOGUE_DENOMINATOR_REF_STALE");
  }
  const mutations = expectArray(source.mutations,
    "FAMILY_VALUE_MUTATION_CATALOGUE_MUTATIONS_INVALID").map((value) => {
    const mutation = expectObject(value, "FAMILY_VALUE_MUTATION_INVALID");
    exactKeys(mutation, ["mutation_id", "hostile_class", "mutation_kind",
      "component_name", "expected_finding_codes"],
    "FAMILY_VALUE_MUTATION_SHAPE_INVALID");
    if (!COMPLETE_VALUE_HOSTILE_CLASSES.includes(
      mutation.hostile_class as CompleteValueHostileClass,
    ) || !COMPLETE_VALUE_MUTATION_KINDS.includes(
      mutation.mutation_kind as CompleteValueMutationKind,
    )) {
      return fail("FAMILY_VALUE_MUTATION_KIND_INVALID");
    }
    const componentName = mutation.component_name === null ? null
      : expectString(mutation.component_name, "FAMILY_VALUE_MUTATION_COMPONENT_INVALID");
    if (componentName !== null
        && !definition.components.some(({component_name}) =>
          component_name === componentName)) {
      return fail("FAMILY_VALUE_MUTATION_COMPONENT_INVALID");
    }
    const expectedCodes = expectArray(mutation.expected_finding_codes,
      "FAMILY_VALUE_MUTATION_FINDINGS_INVALID").map((item) => {
      const code = expectString(
        item,
        "FAMILY_VALUE_MUTATION_FINDINGS_INVALID",
      ) as CompleteValueFindingCode;
      return FINDING_CODES.has(code) ? code
        : fail("FAMILY_VALUE_MUTATION_FINDINGS_INVALID");
    });
    if (expectedCodes.length === 0 || new Set(expectedCodes).size !== expectedCodes.length) {
      return fail("FAMILY_VALUE_MUTATION_FINDINGS_INVALID");
    }
    return Object.freeze({
      mutation_id: expectString(mutation.mutation_id,
        "FAMILY_VALUE_MUTATION_ID_INVALID"),
      hostile_class: mutation.hostile_class as CompleteValueHostileClass,
      mutation_kind: mutation.mutation_kind as CompleteValueMutationKind,
      component_name: componentName,
      expected_finding_codes: Object.freeze(expectedCodes),
    }) satisfies CompleteValueMutationV1;
  });
  if (new Set(mutations.map(({mutation_id}) => mutation_id)).size
      !== mutations.length
      || !exactSet([...new Set(mutations.map(({hostile_class}) => hostile_class))],
        COMPLETE_VALUE_HOSTILE_CLASSES)) {
    return fail("FAMILY_VALUE_MUTATION_CATALOGUE_SCOPE_INVALID");
  }
  const observedBlueprint = mutations.map((mutation) => ({
    mutation_id: mutation.mutation_id,
    hostile_class: mutation.hostile_class,
    mutation_kind: mutation.mutation_kind,
    component_name: mutation.component_name,
  }));
  if (!same(observedBlueprint, COMPLETE_VALUE_MUTATION_BLUEPRINT)) {
    return fail("FAMILY_VALUE_MUTATION_CATALOGUE_BLUEPRINT_INVALID");
  }
  const partialComponents = mutations
    .filter(({mutation_kind}) => mutation_kind === "partial-tuple-equality")
    .map(({component_name}) => component_name)
    .filter((value): value is string => value !== null);
  if (!exactSet(partialComponents,
    definition.components.map(({component_name}) => component_name))) {
    return fail("FAMILY_VALUE_MUTATION_COMPONENT_COVERAGE_INVALID");
  }
  const nestedNames = definition.components.filter(({nested_value_object}) =>
    nested_value_object).map(({component_name}) => component_name);
  for (const nested of nestedNames) {
    for (const kind of ["nested-mutation", "nested-alias"] as const) {
      if (!mutations.some((mutation) => mutation.mutation_kind === kind
          && mutation.component_name === nested)) {
        return fail("FAMILY_VALUE_MUTATION_NESTED_COVERAGE_INVALID");
      }
    }
  }
  for (const kind of ["component-protocol-identity-missing",
    "component-protocol-digest-stale"] as const) {
    if (!mutations.some((mutation) => mutation.mutation_kind === kind)) {
      return fail("FAMILY_VALUE_MUTATION_PROTOCOL_COVERAGE_INVALID");
    }
  }
  const withoutDigest = {
    schema_version: "CompleteValueMutationCatalogue/v1" as const,
    denominator_ref: Object.freeze({
      denominator_id: denominator.denominator_id,
      denominator_sha256: denominator.denominator_sha256,
    }),
    authorship: "independent-family-fixture" as const,
    target_code_may_read_expected_findings: false as const,
    mutations: Object.freeze(mutations),
    authority_effect: "none" as const,
  };
  const digest = expectSha(source.catalogue_sha256,
    "FAMILY_VALUE_MUTATION_CATALOGUE_DIGEST_INVALID");
  if (digest !== computeCompleteValueCatalogueSha256(withoutDigest)) {
    return fail("FAMILY_VALUE_MUTATION_CATALOGUE_DIGEST_STALE");
  }
  return Object.freeze({...withoutDigest, catalogue_sha256: digest});
};

export const decodeCompleteValueObservationV1 = (
  bytes: string,
): CompleteValueObservationV1 => decodeConstructionObservationV1(bytes);

export const sha256CompleteValueBytes = sha256;
