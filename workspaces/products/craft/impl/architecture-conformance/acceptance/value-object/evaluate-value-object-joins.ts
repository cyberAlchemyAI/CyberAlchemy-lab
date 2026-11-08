import type {FactoryUpstreamResultV1} from
  "../../factory/contracts/factory-node-provider-v1.js";
import {
  decodeCompleteValueDefinitionV1,
  decodeCompleteValueDenominatorV1,
  decodeCompleteValueMutationCatalogueV1,
  decodeCompleteValueObservationV1,
  sha256CompleteValueBytes,
  type CompleteValueDefinitionV1,
} from "../../families/complete-value/index.js";
import {canonicalConstructionObservationJson} from
  "../../kernel/evidence/construction-observation/index.js";

type JsonObject = Record<string, unknown>;

export const VALUE_OBJECT_DIRECT_HANDLES = Object.freeze([
  Object.freeze({
    node_id: "value-object.typescript.settlement-value",
    provider_id: "typescript-value-object-v1",
    language: "typescript",
    proof_schema: "TypeScriptValueObjectProof/v1",
    target_id: "value-object.typescript.settlement-value/v1",
    target_sha256: "4dd0f4ffdb9d90f4a18806343e9f39ffb2a48ce2f6056fc6cf9df90b5bee6c0d",
    protocol_id: "typescript.owned-value-object-factory/v1",
    binding_id: "typescript.settlement-value.complete-value/v1",
    binding_sha256: "e892750df568d73e9ab3bd11b586cdf827c17139c1c1673d6186928a05e2ed30",
    observer_sha256: "a8ca7ee86a77cc94a881a975f19d8f408c38709d1ed0b7c9e6d8b6d70047c112",
    provider_sha256: "f6b3f6778b50e03d774e3751b54e38ff287b0e52c9c1c5c0ce22e801ea25fb62",
  }),
  Object.freeze({
    node_id: "value-object.python.settlement-value",
    provider_id: "python-value-object-v1",
    language: "python",
    proof_schema: "PythonValueObjectProof/v1",
    target_id: "value-object.python.settlement-value/v1",
    target_sha256: "f91cc9b5efe90f94051434b79641229a34af34d7f6b4c17ab2141b014dbc6406",
    protocol_id: "python.owned-value-object-factory/v1",
    binding_id: "python.settlement-value.complete-value/v1",
    binding_sha256: "537cb0373799838985f8ca28b51de2e433836a828f38c500d1c67b523ad490b2",
    observer_sha256: "e197440b95c0321475138a88ed07a89c21bc68d6ef1e8c1a5f3d0c42f0cfbfcc",
    provider_sha256: "b3bbab440c4140d2227e6e7e77dc3265de3a6b8ee6f5d9e62a1a1d6fdba063fd",
  }),
  Object.freeze({
    node_id: "value-object.rust.settlement-value",
    provider_id: "rust-value-object-v1",
    language: "rust",
    proof_schema: "RustValueObjectProof/v1",
    target_id: "value-object.rust.settlement-value/v1",
    target_sha256: "7ca45e0d5c38a60cb274fdb6658679a58d1019bb719a24addebc5ea1fbe736fb",
    protocol_id: "rust.owned-value-object-factory/v1",
    binding_id: "rust.settlement-value.complete-value/v1",
    binding_sha256: "626ed3335e8f31f4a90c79eb36bdf88098a86f0d6cf75ee569efbd127168ad30",
    observer_sha256: "0445e0139fafd4ab12c9b4f5e436add7da46e2c9789a5d83e664603fd7a47d2d",
    provider_sha256: "f749629a22cd0a6f4ce683b24aadde79bc46abf08155191d07bf8b066af93b6a",
  }),
] as const);

export const VALUE_OBJECT_PARITY_HANDLE = Object.freeze({
  node_id: "value-object.parity.settlement-value",
  provider_id: "value-object-parity-v1",
  proof_schema: "ValueObjectParityProof/v1",
});

const DEFINITION_PATH =
  "projects/domainspec-v2/impl/architecture-conformance/families/complete-value/fixtures/settlement-value/definition.json";
const DENOMINATOR_PATH =
  "projects/domainspec-v2/impl/architecture-conformance/families/complete-value/fixtures/settlement-value/denominator.json";
const MUTATIONS_PATH =
  "projects/domainspec-v2/impl/architecture-conformance/families/complete-value/fixtures/settlement-value/mutants.json";
const DESCRIPTOR_PATH =
  "projects/domainspec-v2/development/remaining-meta-types/admissions/value-object/cross-language-realization-descriptor.json";
const ADMISSION_PATH =
  "projects/domainspec-v2/development/remaining-meta-types/admissions/value-object/protocol-admission.json";
const ONTOLOGY_PATH =
  "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/ontology.json";

export const VALUE_OBJECT_PARITY_RAW_PATHS = Object.freeze({
  definition: DEFINITION_PATH,
  denominator: DENOMINATOR_PATH,
  mutations: MUTATIONS_PATH,
  descriptor: DESCRIPTOR_PATH,
});

export const VALUE_OBJECT_RELATION_RAW_PATHS = Object.freeze({
  ...VALUE_OBJECT_PARITY_RAW_PATHS,
  protocol_admission: ADMISSION_PATH,
  ontology: ONTOLOGY_PATH,
});

const PARITY_OBLIGATION_IDS = Object.freeze([
  "exact-direct-handle-set",
  "exact-provider-target-language-protocol-schema",
  "shared-owner-definition",
  "shared-descriptor-denominator-and-mutation-catalogue",
  "exact-owner-case-ledger",
  "complete-normalized-component-tuples",
  "exact-validator-order-and-structured-failure",
  "distinct-reference-equality",
  "every-component-participates-in-equality",
  "own-language-equality-hash-congruence",
  "cross-language-hash-bytes-not-compared",
  "recursive-owned-immutability",
  "nested-owned-protocol-delegation",
  "additive-validation-only-terminal-extension",
  "family-seven-of-seven",
  "native-and-control-evidence-retained",
  "authority-effect-none",
] as const);

const RELATION_OBLIGATION_IDS = Object.freeze([
  "exact-direct-plus-parity-closure",
  "parity-proof-recomputed-not-totals-only",
  "descriptor-and-admission-bound",
  "ontology-relation-definitions-bound",
  "constructed-by-exact-endpoints",
  "validated-by-exact-endpoints",
  "owner-validator-identities-and-order",
  "extends-factory-exact-endpoints",
  "additive-validation-only-policy",
  "acyclic-terminal-extension",
  "authority-effect-none",
] as const);

export type ValueObjectParityFindingCode =
  | "VALUE_OBJECT_PARITY_HANDLE_SET_MISMATCH"
  | "VALUE_OBJECT_PARITY_PROVIDER_MISMATCH"
  | "VALUE_OBJECT_PARITY_PROOF_INVALID"
  | "VALUE_OBJECT_PARITY_TARGET_MISMATCH"
  | "VALUE_OBJECT_PARITY_OWNER_MATERIAL_INVALID"
  | "VALUE_OBJECT_PARITY_CASE_INVALID"
  | "VALUE_OBJECT_PARITY_VALIDATOR_INVALID"
  | "VALUE_OBJECT_PARITY_EQUALITY_INVALID"
  | "VALUE_OBJECT_PARITY_HASH_CONGRUENCE_INVALID"
  | "VALUE_OBJECT_PARITY_IMMUTABILITY_INVALID"
  | "VALUE_OBJECT_PARITY_NESTED_INVALID"
  | "VALUE_OBJECT_PARITY_EXTENSION_INVALID"
  | "VALUE_OBJECT_PARITY_FAMILY_INVALID"
  | "VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING"
  | "VALUE_OBJECT_PARITY_PORTABLE_DRIFT"
  | "VALUE_OBJECT_PARITY_RAW_INPUT_INVALID";

export type ValueObjectRelationFindingCode =
  | "VALUE_OBJECT_RELATION_HANDLE_SET_MISMATCH"
  | "VALUE_OBJECT_RELATION_PARITY_INVALID"
  | "VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID"
  | "VALUE_OBJECT_RELATION_CONSTRUCTED_BY_INVALID"
  | "VALUE_OBJECT_RELATION_VALIDATED_BY_INVALID"
  | "VALUE_OBJECT_RELATION_EXTENDS_FACTORY_INVALID"
  | "VALUE_OBJECT_RELATION_AUTHORITY_INVALID";

type Handle = (typeof VALUE_OBJECT_DIRECT_HANDLES)[number];
type OwnerInputs = ReturnType<typeof decodeOwnerInputs>;
type DirectProjection = Readonly<{
  handle: Handle;
  semantic_sha256: string;
  portable: JsonObject;
  native_evidence: JsonObject;
}>;

export type ValueObjectParityProofV1 = Readonly<{
  schema_version: "ValueObjectParityProof/v1";
  result: "pass";
  composed_from: readonly Readonly<{
    node_id: string;
    provider_id: string;
    semantic_sha256: string;
    target_id: string;
    target_sha256: string;
    language: string;
    protocol_id: string;
    binding_sha256: string;
  }>[];
  owner_refs: Readonly<{
    definition_id: string;
    definition_sha256: string;
    denominator_id: string;
    denominator_sha256: string;
    descriptor_id: string;
    descriptor_sha256: string;
    mutation_catalogue_sha256: string;
  }>;
  portable_projection: JsonObject;
  native_evidence_by_language: readonly Readonly<{
    language: string;
    evidence: JsonObject;
  }>[];
  obligations: readonly Readonly<{
    obligation_id: (typeof PARITY_OBLIGATION_IDS)[number];
    status: "passed";
  }>[];
  hostile_mutations: readonly Readonly<{
    mutation_id: string;
    status: "killed";
    finding_code: ValueObjectParityFindingCode;
  }>[];
  claim_ceiling: string;
  authority_effect: "none";
}>;

export type ValueObjectRelationsProofV1 = Readonly<{
  schema_version: "ValueObjectRelationsProof/v1";
  result: "pass";
  composed_from: readonly Readonly<{
    node_id: string;
    provider_id: string;
    semantic_sha256: string;
  }>[];
  relation_rows: readonly Readonly<{
    language: string;
    relation_id: "architecture.constructed_by" | "architecture.validated_by" |
      "architecture.extends_factory";
    source_id: string;
    source_type: string;
    target_id: string;
    target_type: string;
    ordinal: number | null;
    cycle_policy: "not-applicable" | "acyclic";
  }>[];
  obligations: readonly Readonly<{
    obligation_id: (typeof RELATION_OBLIGATION_IDS)[number];
    status: "passed";
  }>[];
  hostile_mutations: readonly Readonly<{
    mutation_id: string;
    status: "killed";
    finding_code: ValueObjectRelationFindingCode;
  }>[];
  claim_ceiling: string;
  authority_effect: "none";
}>;

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const isObject = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const object = <Code extends string>(value: unknown, code: Code): JsonObject =>
  isObject(value) ? value : fail(code);
const array = <Code extends string>(value: unknown, code: Code): unknown[] =>
  Array.isArray(value) ? value : fail(code);
const string = <Code extends string>(value: unknown, code: Code): string =>
  typeof value === "string" && value.length > 0 ? value : fail(code);
const sha256String = <Code extends string>(value: unknown, code: Code): string => {
  const digest = string(value, code);
  return /^[a-f0-9]{64}$/u.test(digest) ? digest : fail(code);
};
const fail = <Code extends string>(code: Code, detail?: string): never => {
  throw Object.assign(new Error(detail === undefined ? code : `${code}:${detail}`), {
    code,
  });
};
const same = (left: unknown, right: unknown): boolean =>
  canonicalConstructionObservationJson(left) ===
    canonicalConstructionObservationJson(right);
const exactSet = (observed: readonly string[], expected: readonly string[]): boolean =>
  new Set(observed).size === observed.length &&
  same([...observed].sort(compareUtf8), [...expected].sort(compareUtf8));
const parseObject = <Code extends string>(raw: string | undefined, code: Code):
JsonObject => {
  if (raw === undefined) return fail(code);
  try {
    return object(JSON.parse(raw), code);
  } catch (error: unknown) {
    if (isObject(error) && error.code === code) throw error;
    return fail(code);
  }
};
const clone = <T>(value: T): T => structuredClone(value);

const decodeOwnerInputs = (rawInputs: Readonly<Record<string, string>>) => {
  if (!exactSet(Object.keys(rawInputs), Object.keys(VALUE_OBJECT_PARITY_RAW_PATHS))) {
    return fail("VALUE_OBJECT_PARITY_RAW_INPUT_INVALID", "roles");
  }
  const descriptor = parseObject(rawInputs.descriptor,
    "VALUE_OBJECT_PARITY_RAW_INPUT_INVALID");
  try {
    const definition = decodeCompleteValueDefinitionV1(
      rawInputs.definition!, DESCRIPTOR_PATH, rawInputs.descriptor!);
    const denominator = decodeCompleteValueDenominatorV1(
      rawInputs.denominator!, rawInputs.definition!, definition, DEFINITION_PATH);
    const mutations = decodeCompleteValueMutationCatalogueV1(
      rawInputs.mutations!, denominator, definition);
    const portable = object(descriptor.portable_architecture,
      "VALUE_OBJECT_PARITY_RAW_INPUT_INVALID");
    if (descriptor.descriptor_id !== definition.descriptor_ref.descriptor_id ||
        descriptor.descriptor_protocol_id !==
          "domainspec.owned-value-object-factory/v1" ||
        descriptor.authority_effect !== "none" ||
        portable.type_id !== "architecture.ValueObjectImplementation" ||
        portable.factory_provider_type_id !==
          "architecture.ValueObjectFactoryProvider" ||
        definition.components.length !== 3 || definition.validators.length !== 3 ||
        definition.cases.length !== 6 ||
        denominator.positive_decisions.length !== 7 ||
        denominator.semantic_hostile_classes.length !== 8 ||
        mutations.mutations.length !== 12) {
      return fail("VALUE_OBJECT_PARITY_RAW_INPUT_INVALID", "owner-shape");
    }
    return Object.freeze({
      definition,
      denominator,
      mutations,
      descriptor,
      definition_sha256: sha256CompleteValueBytes(rawInputs.definition!),
      descriptor_sha256: sha256CompleteValueBytes(rawInputs.descriptor!),
      mutation_catalogue_sha256: sha256CompleteValueBytes(rawInputs.mutations!),
    });
  } catch (error: unknown) {
    if (isObject(error) && typeof error.code === "string" &&
        String(error.code).startsWith("VALUE_OBJECT_PARITY_")) throw error;
    return fail("VALUE_OBJECT_PARITY_RAW_INPUT_INVALID",
      error instanceof Error ? error.message : String(error));
  }
};

const expectedAttempt = (
  definition: CompleteValueDefinitionV1,
  index: number,
): JsonObject => {
  const testCase = definition.cases[index]!;
  const valid = testCase.input_class === "valid";
  const validators = definition.validators.slice(0, valid
    ? definition.validators.length : 2);
  const components = definition.components.map((component) => Object.freeze({
    component_name: component.component_name,
    protocol_id: component.protocol_id,
    protocol_sha256: component.protocol_sha256,
    normalized_value_sha256:
      testCase.normalized_component_values[component.component_name],
    nested_value_object: component.nested_value_object,
  }));
  return Object.freeze({
    case_id: testCase.case_id,
    input_class: testCase.input_class,
    component_bindings: Object.freeze(components),
    validator_trace: Object.freeze(validators.map((validator, ordinal) =>
      Object.freeze({...validator, ordinal, outcome: valid || ordinal === 0
        ? "pass" as const : "fail" as const}))),
    formation_ordinal: valid ? validators.length : null,
    result: Object.freeze(valid ? {
      status: "formed" as const,
      object_created: true,
      failure_codes: Object.freeze([]),
    } : {
      status: "validation-failure" as const,
      object_created: false,
      failure_codes: Object.freeze([...testCase.expected_failure_codes]),
    }),
    normalized_tuple: valid ? Object.freeze(components.map(({component_name,
      normalized_value_sha256}) => Object.freeze({component_name,
      normalized_value_sha256}))) : null,
  });
};

const portableCases = (
  observation: JsonObject,
  owner: OwnerInputs,
  language: string,
): readonly JsonObject[] => {
  const attempts = array(observation.attempts, "VALUE_OBJECT_PARITY_CASE_INVALID");
  if (attempts.length !== owner.definition.cases.length) {
    return fail("VALUE_OBJECT_PARITY_CASE_INVALID", language);
  }
  return Object.freeze(attempts.map((item, index) => {
    const attempt = object(item, "VALUE_OBJECT_PARITY_CASE_INVALID");
    const immutability = object(attempt.immutability,
      "VALUE_OBJECT_PARITY_IMMUTABILITY_INVALID");
    const expected = expectedAttempt(owner.definition, index);
    const projected = Object.freeze({
      case_id: attempt.case_id,
      input_class: attempt.input_class,
      component_bindings: attempt.component_bindings,
      validator_trace: attempt.validator_trace,
      formation_ordinal: attempt.formation_ordinal,
      result: attempt.result,
      normalized_tuple: attempt.normalized_tuple,
    });
    if (!same(projected, expected)) {
      const expectedValidators = object(expected, "VALUE_OBJECT_PARITY_CASE_INVALID")
        .validator_trace;
      if (!same(attempt.validator_trace, expectedValidators)) {
        return fail("VALUE_OBJECT_PARITY_VALIDATOR_INVALID",
          `${language}:${String(attempt.case_id)}`);
      }
      return fail("VALUE_OBJECT_PARITY_CASE_INVALID",
        `${language}:${String(attempt.case_id)}`);
    }
    const valid = attempt.input_class === "valid";
    if (valid && (immutability.formed_value_frozen !== true ||
        immutability.recursively_owned_components_frozen !== true ||
        immutability.nested_alias_observed !== false ||
        immutability.nested_mutation_observed !== false)) {
      return fail("VALUE_OBJECT_PARITY_IMMUTABILITY_INVALID",
        `${language}:${String(attempt.case_id)}`);
    }
    return Object.freeze({...projected,
      immutability: Object.freeze({
        formed_value_frozen: valid,
        recursively_owned_components_frozen: valid,
        nested_alias_observed: false,
        nested_mutation_observed: false,
      })});
  }));
};

const portableEquality = (
  observation: JsonObject,
  owner: OwnerInputs,
  language: string,
): readonly JsonObject[] => {
  const probes = array(observation.equality_probes,
    "VALUE_OBJECT_PARITY_EQUALITY_INVALID");
  const expected = [
    Object.freeze({...owner.definition.equality_contract.equal_probe,
      relation: "equal-tuple" as const, varied_component_name: null}),
    ...owner.definition.equality_contract.component_variants.map((variant) =>
      Object.freeze({...variant, relation: "component-variant" as const,
        varied_component_name: variant.component_name})),
  ];
  if (probes.length !== expected.length) {
    return fail("VALUE_OBJECT_PARITY_EQUALITY_INVALID", language);
  }
  return Object.freeze(probes.map((item, index) => {
    const probe = object(item, "VALUE_OBJECT_PARITY_EQUALITY_INVALID");
    const expectedProbe = expected[index]!;
    const equal = expectedProbe.relation === "equal-tuple";
    if (probe.probe_id !== expectedProbe.probe_id ||
        probe.left_case_id !== expectedProbe.left_case_id ||
        probe.right_case_id !== expectedProbe.right_case_id ||
        probe.relation !== expectedProbe.relation ||
        probe.varied_component_name !== expectedProbe.varied_component_name ||
        probe.references_distinct !== true || probe.observed_equal !== equal ||
        !/^[a-f0-9]{64}$/u.test(String(probe.left_hash_sha256)) ||
        !/^[a-f0-9]{64}$/u.test(String(probe.right_hash_sha256))) {
      return fail("VALUE_OBJECT_PARITY_EQUALITY_INVALID",
        `${language}:${String(probe.probe_id)}`);
    }
    if (equal && probe.left_hash_sha256 !== probe.right_hash_sha256) {
      return fail("VALUE_OBJECT_PARITY_HASH_CONGRUENCE_INVALID", language);
    }
    return Object.freeze({
      probe_id: probe.probe_id,
      left_case_id: probe.left_case_id,
      right_case_id: probe.right_case_id,
      relation: probe.relation,
      varied_component_name: probe.varied_component_name,
      references_distinct: true,
      observed_equal: equal,
      own_language_equal_tuple_hash_congruent: equal ? true : null,
      native_hash_bytes_compared_cross_language: false,
    });
  }));
};

const exactControls = (
  proof: JsonObject,
  language: string,
): Readonly<{
  static_controls: readonly unknown[];
  family_controls: readonly unknown[];
}> => {
  const staticControls = array(proof.static_binding_controls,
    "VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING");
  const familyControls = array(proof.predecessor_family_controls,
    "VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING");
  const staticIds = staticControls.map((item) => {
    const control = object(item, "VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING");
    if (control.status !== "rejected") {
      return fail("VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING", language);
    }
    return string(control.control_id,
      "VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING");
  });
  const familyIds = familyControls.map((item) => {
    const control = object(item, "VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING");
    if (control.status !== "killed") {
      return fail("VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING", language);
    }
    return string(control.mutation_id,
      "VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING");
  });
  if (staticControls.length !== 8 || new Set(staticIds).size !== 8 ||
      familyControls.length !== 12 || new Set(familyIds).size !== 12) {
    return fail("VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING", language);
  }
  return Object.freeze({static_controls: Object.freeze(staticControls),
    family_controls: Object.freeze(familyControls)});
};

const projectDirect = (
  upstream: FactoryUpstreamResultV1,
  handle: Handle,
  owner: OwnerInputs,
): DirectProjection => {
  if (upstream.node_id !== handle.node_id ||
      upstream.provider_id !== handle.provider_id) {
    return fail("VALUE_OBJECT_PARITY_PROVIDER_MISMATCH", handle.node_id);
  }
  const semanticSha256 = sha256String(upstream.semantic_sha256,
    "VALUE_OBJECT_PARITY_PROOF_INVALID");
  const output = object(upstream.semantic_output,
    "VALUE_OBJECT_PARITY_PROOF_INVALID");
  const proof = object(output.proof, "VALUE_OBJECT_PARITY_PROOF_INVALID");
  if (proof.schema_version !== handle.proof_schema || proof.result !== "pass" ||
      proof.authority_effect !== "none") {
    return fail("VALUE_OBJECT_PARITY_PROOF_INVALID", handle.language);
  }
  const target = object(proof.target, "VALUE_OBJECT_PARITY_TARGET_MISMATCH");
  const binding = object(proof.binding, "VALUE_OBJECT_PARITY_PROOF_INVALID");
  if (target.target_id !== handle.target_id ||
      target.target_sha256 !== handle.target_sha256 ||
      target.language !== handle.language ||
      target.protocol_id !== handle.protocol_id ||
      !/^[a-f0-9]{64}$/u.test(handle.target_sha256)) {
    return fail("VALUE_OBJECT_PARITY_TARGET_MISMATCH", handle.language);
  }
  if (binding.binding_id !== handle.binding_id ||
      binding.binding_sha256 !== handle.binding_sha256 ||
      !/^[a-f0-9]{64}$/u.test(handle.binding_sha256)) {
    return fail("VALUE_OBJECT_PARITY_PROOF_INVALID", `${handle.language}:binding`);
  }
  const observation = object(proof.observation,
    "VALUE_OBJECT_PARITY_PROOF_INVALID");
  const definitionRef = object(observation.definition_ref,
    "VALUE_OBJECT_PARITY_OWNER_MATERIAL_INVALID");
  const factoryRef = object(observation.factory_ref,
    "VALUE_OBJECT_PARITY_OWNER_MATERIAL_INVALID");
  const observer = object(observation.observer_ref,
    "VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING");
  if (observation.schema_version !== "ConstructionObservation/v1" ||
      observation.source_kind !== "target-observation" ||
      observation.authority_effect !== "none" ||
      observation.collision_freedom_claim !== false ||
      definitionRef.definition_id !== owner.definition.definition_id ||
      definitionRef.path !== DEFINITION_PATH ||
      definitionRef.sha256 !== owner.definition_sha256 ||
      !same(factoryRef, owner.definition.factories.base)) {
    return fail("VALUE_OBJECT_PARITY_OWNER_MATERIAL_INVALID", handle.language);
  }
  if (observer.role !== "independent-construction-observer" ||
      observer.provider_id !== handle.provider_id ||
      observer.owner_ref === handle.provider_id ||
      observer.observer_sha256 !== handle.observer_sha256 ||
      observer.provider_sha256 !== handle.provider_sha256 ||
      !/^[a-f0-9]{64}$/u.test(handle.observer_sha256) ||
      !/^[a-f0-9]{64}$/u.test(handle.provider_sha256)) {
    return fail("VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING",
      `${handle.language}:observer`);
  }
  const cases = portableCases(observation, owner, handle.language);
  const equality = portableEquality(observation, owner, handle.language);
  const nested = array(observation.nested_delegations,
    "VALUE_OBJECT_PARITY_NESTED_INVALID");
  const expectedNested = owner.definition.components.filter(
    ({nested_value_object: nestedValue}) => nestedValue).map((component) => ({
      component_name: component.component_name,
      protocol_id: component.protocol_id,
      protocol_sha256: component.protocol_sha256,
      equality_delegated: true,
      hash_delegated: true,
    }));
  if (!same(nested, expectedNested)) {
    return fail("VALUE_OBJECT_PARITY_NESTED_INVALID", handle.language);
  }
  const extension = object(observation.extension,
    "VALUE_OBJECT_PARITY_EXTENSION_INVALID");
  const expectedExtension = {
    base_factory_ref: owner.definition.factories.base,
    extension_factory_ref: owner.definition.factories.extension,
    added_validators: owner.definition.validators.filter(({origin}) =>
      origin === "extension"),
    altered_facets: [],
    cycle_detected: false,
  };
  if (!same(extension, expectedExtension)) {
    return fail("VALUE_OBJECT_PARITY_EXTENSION_INVALID", handle.language);
  }
  const family = object(proof.family_evaluation,
    "VALUE_OBJECT_PARITY_FAMILY_INVALID");
  const familyAccounting = object(family.positive_decision_accounting,
    "VALUE_OBJECT_PARITY_FAMILY_INVALID");
  const familyDenominator = object(family.denominator_ref,
    "VALUE_OBJECT_PARITY_FAMILY_INVALID");
  if (family.verdict !== "pass" || family.authority_effect !== "none" ||
      family.collision_freedom_claim !== false ||
      array(family.findings, "VALUE_OBJECT_PARITY_FAMILY_INVALID").length !== 0 ||
      familyAccounting.declared !== 7 || familyAccounting.passed !== 7 ||
      familyAccounting.failed !== 0 || familyAccounting.unaccounted !== 0 ||
      familyDenominator.denominator_id !== owner.denominator.denominator_id ||
      familyDenominator.denominator_sha256 !==
        owner.denominator.denominator_sha256) {
    return fail("VALUE_OBJECT_PARITY_FAMILY_INVALID", handle.language);
  }
  const accounting = object(proof.accounting, "VALUE_OBJECT_PARITY_FAMILY_INVALID");
  const positives = object(accounting.positives,
    "VALUE_OBJECT_PARITY_FAMILY_INVALID");
  const staticAccounting = object(accounting.static_binding_controls,
    "VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING");
  const familyControlAccounting = object(accounting.predecessor_family_controls,
    "VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING");
  if (positives.declared !== 7 || positives.passed !== 7 ||
      staticAccounting.declared !== 8 || staticAccounting.rejected !== 8 ||
      familyControlAccounting.declared !== 12 ||
      familyControlAccounting.killed !== 12) {
    return fail("VALUE_OBJECT_PARITY_FAMILY_INVALID",
      `${handle.language}:accounting`);
  }
  const controls = exactControls(proof, handle.language);
  const processEvidence = object(proof.process_evidence,
    "VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING");
  if (processEvidence.executions !== 2 ||
      processEvidence.distinct_pids !== 2 ||
      ("semantic_replay_equal" in processEvidence &&
        processEvidence.semantic_replay_equal !== true) ||
      ("pids_redacted_from_semantic_proof" in processEvidence &&
        processEvidence.pids_redacted_from_semantic_proof !== true) ||
      !/^[a-f0-9]{64}$/u.test(String(processEvidence.semantic_replay_sha256))) {
    return fail("VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING", handle.language);
  }
  const nativeEvidence = Object.freeze({
    process_evidence: processEvidence,
    toolchain: object(proof.toolchain,
      "VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING"),
    static_binding_controls: controls.static_controls,
    predecessor_family_controls: controls.family_controls,
    native_runtime_observation: handle.language === "typescript" ? null
      : object(proof.native_runtime_observation,
        "VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING"),
    closed_subset: handle.language === "typescript"
      ? object(proof.closed_subset, "VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING")
      : null,
    source_proof: handle.language === "rust"
      ? object(proof.source_proof, "VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING")
      : null,
    immutability_proof: handle.language === "rust"
      ? object(proof.immutability_proof,
        "VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING") : null,
  });
  try {
    decodeCompleteValueObservationV1(
      canonicalConstructionObservationJson(observation));
  } catch (error: unknown) {
    return fail("VALUE_OBJECT_PARITY_PROOF_INVALID",
      error instanceof Error ? error.message : String(error));
  }
  return Object.freeze({
    handle,
    semantic_sha256: semanticSha256,
    portable: Object.freeze({
      definition_id: owner.definition.definition_id,
      definition_sha256: owner.definition_sha256,
      descriptor_id: owner.definition.descriptor_ref.descriptor_id,
      descriptor_sha256: owner.descriptor_sha256,
      concept_id: owner.definition.concept_id,
      base_factory: owner.definition.factories.base,
      extension_factory: owner.definition.factories.extension,
      components: owner.definition.components,
      validators: owner.definition.validators,
      cases,
      equality,
      nested_delegations: Object.freeze(expectedNested),
      extension: Object.freeze(expectedExtension),
      family: Object.freeze({verdict: "pass" as const,
        positive_decisions: Object.freeze({declared: 7, passed: 7})}),
      authority_effect: "none" as const,
    }),
    native_evidence: nativeEvidence,
  });
};

export const evaluateValueObjectParity = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
  rawInputs: Readonly<Record<string, string>>,
) => {
  const expectedKeys = VALUE_OBJECT_DIRECT_HANDLES.map(({node_id: nodeId}) =>
    nodeId);
  if (!exactSet(Object.keys(upstream), expectedKeys)) {
    return fail("VALUE_OBJECT_PARITY_HANDLE_SET_MISMATCH");
  }
  const owner = decodeOwnerInputs(rawInputs);
  const direct = VALUE_OBJECT_DIRECT_HANDLES.map((handle) =>
    projectDirect(upstream[handle.node_id]!, handle, owner));
  const reference = direct[0]!.portable;
  for (const projection of direct.slice(1)) {
    if (!same(projection.portable, reference)) {
      return fail("VALUE_OBJECT_PARITY_PORTABLE_DRIFT",
        projection.handle.language);
    }
  }
  return Object.freeze({owner, direct, portable_projection: reference});
};

const directProof = (upstream: any, index = 0): any =>
  upstream[VALUE_OBJECT_DIRECT_HANDLES[index]!.node_id].semantic_output.proof;

const parityHostiles = Object.freeze([
  Object.freeze({id: "join/missing-handle", code: "VALUE_OBJECT_PARITY_HANDLE_SET_MISMATCH", apply: (u: any) => { delete u[VALUE_OBJECT_DIRECT_HANDLES[0]!.node_id]; }}),
  Object.freeze({id: "join/wrong-provider", code: "VALUE_OBJECT_PARITY_PROVIDER_MISMATCH", apply: (u: any) => { u[VALUE_OBJECT_DIRECT_HANDLES[0]!.node_id].provider_id = "wrong-provider"; }}),
  Object.freeze({id: "join/proof-schema", code: "VALUE_OBJECT_PARITY_PROOF_INVALID", apply: (u: any) => { directProof(u).schema_version = "WrongProof/v1"; }}),
  Object.freeze({id: "join/wrong-target", code: "VALUE_OBJECT_PARITY_TARGET_MISMATCH", apply: (u: any) => { directProof(u).target.target_sha256 = "0".repeat(64); }}),
  Object.freeze({id: "join/wrong-protocol", code: "VALUE_OBJECT_PARITY_TARGET_MISMATCH", apply: (u: any) => { directProof(u).target.protocol_id = "wrong-protocol/v1"; }}),
  Object.freeze({id: "join/wrong-binding", code: "VALUE_OBJECT_PARITY_PROOF_INVALID", apply: (u: any) => { directProof(u).binding.binding_sha256 = "0".repeat(64); }}),
  Object.freeze({id: "join/stale-definition", code: "VALUE_OBJECT_PARITY_OWNER_MATERIAL_INVALID", apply: (u: any) => { directProof(u).observation.definition_ref.sha256 = "0".repeat(64); }}),
  Object.freeze({id: "join/totals-only", code: "VALUE_OBJECT_PARITY_PROOF_INVALID", apply: (u: any) => { u[VALUE_OBJECT_DIRECT_HANDLES[0]!.node_id].semantic_output = {accounting: {positives_declared: 7, positives_passed: 7}}; }}),
  Object.freeze({id: "join/case-tuple", code: "VALUE_OBJECT_PARITY_CASE_INVALID", apply: (u: any) => { directProof(u).observation.attempts[0].normalized_tuple[0].normalized_value_sha256 = "0".repeat(64); }}),
  Object.freeze({id: "join/validator-reorder", code: "VALUE_OBJECT_PARITY_VALIDATOR_INVALID", apply: (u: any) => { directProof(u).observation.attempts[0].validator_trace.reverse(); }}),
  Object.freeze({id: "join/reference-identity", code: "VALUE_OBJECT_PARITY_EQUALITY_INVALID", apply: (u: any) => { directProof(u).observation.equality_probes[0].references_distinct = false; }}),
  Object.freeze({id: "join/equal-hash-incongruent", code: "VALUE_OBJECT_PARITY_HASH_CONGRUENCE_INVALID", apply: (u: any) => { directProof(u).observation.equality_probes[0].right_hash_sha256 = "0".repeat(64); }}),
  Object.freeze({id: "join/immutability", code: "VALUE_OBJECT_PARITY_IMMUTABILITY_INVALID", apply: (u: any) => { directProof(u).observation.attempts[0].immutability.formed_value_frozen = false; }}),
  Object.freeze({id: "join/nested-delegation", code: "VALUE_OBJECT_PARITY_NESTED_INVALID", apply: (u: any) => { directProof(u).observation.nested_delegations[0].hash_delegated = false; }}),
  Object.freeze({id: "join/extension-cycle", code: "VALUE_OBJECT_PARITY_EXTENSION_INVALID", apply: (u: any) => { directProof(u).observation.extension.cycle_detected = true; }}),
  Object.freeze({id: "join/family-count", code: "VALUE_OBJECT_PARITY_FAMILY_INVALID", apply: (u: any) => { directProof(u).family_evaluation.positive_decision_accounting.passed = 6; }}),
  Object.freeze({id: "join/static-controls-erased", code: "VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING", apply: (u: any) => { directProof(u).static_binding_controls = []; }}),
  Object.freeze({id: "join/native-evidence-erased", code: "VALUE_OBJECT_PARITY_NATIVE_EVIDENCE_MISSING", apply: (u: any) => { delete directProof(u).process_evidence; }}),
] as const);

export const proveValueObjectParity = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
  rawInputs: Readonly<Record<string, string>>,
): ValueObjectParityProofV1 => {
  const evaluated = evaluateValueObjectParity(upstream, rawInputs);
  const hostileMutations = parityHostiles.map(({id, code, apply}) => {
    const mutated = clone(upstream);
    apply(mutated);
    try {
      evaluateValueObjectParity(mutated, rawInputs);
    } catch (error: unknown) {
      if (isObject(error) && error.code === code) return Object.freeze({
        mutation_id: id,
        status: "killed" as const,
        finding_code: code as ValueObjectParityFindingCode,
      });
      throw error;
    }
    return fail("VALUE_OBJECT_PARITY_PORTABLE_DRIFT", `survived:${id}`);
  });
  return Object.freeze({
    schema_version: "ValueObjectParityProof/v1" as const,
    result: "pass" as const,
    composed_from: Object.freeze(evaluated.direct.map(({handle, semantic_sha256}) =>
      Object.freeze({node_id: handle.node_id, provider_id: handle.provider_id,
        semantic_sha256, target_id: handle.target_id,
        target_sha256: handle.target_sha256,
        language: handle.language, protocol_id: handle.protocol_id,
        binding_sha256: handle.binding_sha256}))),
    owner_refs: Object.freeze({
      definition_id: evaluated.owner.definition.definition_id,
      definition_sha256: evaluated.owner.definition_sha256,
      denominator_id: evaluated.owner.denominator.denominator_id,
      denominator_sha256: evaluated.owner.denominator.denominator_sha256,
      descriptor_id: string(evaluated.owner.descriptor.descriptor_id,
        "VALUE_OBJECT_PARITY_RAW_INPUT_INVALID"),
      descriptor_sha256: evaluated.owner.descriptor_sha256,
      mutation_catalogue_sha256: evaluated.owner.mutation_catalogue_sha256,
    }),
    portable_projection: evaluated.portable_projection,
    native_evidence_by_language: Object.freeze(evaluated.direct.map(
      ({handle, native_evidence: evidence}) => Object.freeze({
        language: handle.language, evidence}),
    )),
    obligations: Object.freeze(PARITY_OBLIGATION_IDS.map((obligationId) =>
      Object.freeze({obligation_id: obligationId, status: "passed" as const}))),
    hostile_mutations: Object.freeze(hostileMutations),
    claim_ceiling: "same-host same-oracle portable Value Object parity over the exact locked TypeScript, Python, and Rust Settlement Value Object handles and owner cases; complete tuple, equality outcome, own-language hash congruence, validation, structured no-object failure, recursive immutability, nested delegation, and additive extension are compared while native hash bytes and mechanisms remain separate; no arbitrary-language equivalence, cross-language hash-byte equality, collision freedom, candidate projection, promotion, publication, release, deployment, or production claim",
    authority_effect: "none" as const,
  });
};

const exactRelation = (
  value: unknown,
  relationId: string,
  sourceType: string,
  targetType: string,
  cyclePolicy: string,
): boolean => {
  if (!isObject(value)) return false;
  return value.relation_id === relationId && value.source_type === sourceType &&
    value.target_type === targetType && value.cycle_policy === cyclePolicy;
};

const relationOwnerInputs = (
  rawInputs: Readonly<Record<string, string>>,
) => {
  if (!exactSet(Object.keys(rawInputs), Object.keys(VALUE_OBJECT_RELATION_RAW_PATHS))) {
    return fail("VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID", "roles");
  }
  const parityRaw = Object.freeze(Object.fromEntries(
    Object.keys(VALUE_OBJECT_PARITY_RAW_PATHS).map((role) =>
      [role, rawInputs[role]!])));
  let owner: OwnerInputs;
  try {
    owner = decodeOwnerInputs(parityRaw);
  } catch (error: unknown) {
    return fail("VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID",
      error instanceof Error ? error.message : String(error));
  }
  const descriptor = owner.descriptor;
  const admission = parseObject(rawInputs.protocol_admission,
    "VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID");
  const ontology = parseObject(rawInputs.ontology,
    "VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID");
  const portable = object(descriptor.portable_architecture,
    "VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID");
  const descriptorRelations = array(portable.relations,
    "VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID");
  const admissionRelations = array(admission.selected_relations,
    "VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID");
  const ontologyRelations = array(ontology.relation_definitions,
    "VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID");
  const expected = [
    ["architecture.constructed_by", "architecture.ValueObjectImplementation",
      "architecture.ValueObjectFactoryProvider", "not-applicable"],
    ["architecture.validated_by", "architecture.ValueObjectFactoryProvider",
      "architecture.RuleImplementation", "not-applicable"],
    ["architecture.extends_factory", "architecture.ValueObjectFactoryProvider",
      "architecture.ValueObjectFactoryProvider", "acyclic"],
  ] as const;
  const exact = (relations: unknown[]) => expected.every(([id, source, target, cycle]) =>
    relations.filter((row) => exactRelation(row, id, source, target, cycle)).length === 1);
  const expectedOntology = [
    {
      id: "architecture.constructed_by",
      sourceTypes: ["architecture.ValueObjectImplementation",
        "architecture.EntityImplementation"],
      targetTypes: ["architecture.ValueObjectFactoryProvider",
        "architecture.EntityFactoryProvider"],
      pairs: [
        ["architecture.ValueObjectImplementation",
          "architecture.ValueObjectFactoryProvider"],
        ["architecture.EntityImplementation",
          "architecture.EntityFactoryProvider"],
      ],
      cycle: "not-applicable",
    },
    {
      id: "architecture.validated_by",
      sourceTypes: ["architecture.ValueObjectFactoryProvider",
        "architecture.EntityFactoryProvider"],
      targetTypes: ["architecture.RuleImplementation"],
      pairs: [
        ["architecture.ValueObjectFactoryProvider",
          "architecture.RuleImplementation"],
        ["architecture.EntityFactoryProvider",
          "architecture.RuleImplementation"],
      ],
      cycle: "not-applicable",
    },
    {
      id: "architecture.extends_factory",
      sourceTypes: ["architecture.ValueObjectFactoryProvider",
        "architecture.EntityFactoryProvider"],
      targetTypes: ["architecture.ValueObjectFactoryProvider",
        "architecture.EntityFactoryProvider"],
      pairs: [
        ["architecture.ValueObjectFactoryProvider",
          "architecture.ValueObjectFactoryProvider"],
        ["architecture.EntityFactoryProvider",
          "architecture.EntityFactoryProvider"],
      ],
      cycle: "acyclic",
    },
  ] as const;
  const exactStringSet = (value: unknown, expectedValues: readonly string[]):
  boolean => Array.isArray(value) && value.every((item) => typeof item === "string") &&
    exactSet(value, expectedValues);
  const exactPairSet = (value: unknown, expectedPairs: readonly (
  readonly [string, string])[]): boolean => {
    if (!Array.isArray(value)) return false;
    const observed = value.map((pair) => {
      if (!isObject(pair) ||
          !exactSet(Object.keys(pair), ["source_type", "target_type"]) ||
          typeof pair.source_type !== "string" ||
          typeof pair.target_type !== "string") return null;
      return `${pair.source_type}\u0000${pair.target_type}`;
    });
    return observed.every((pair): pair is string => pair !== null) &&
      exactSet(observed, expectedPairs.map(([source, target]) =>
        `${source}\u0000${target}`));
  };
  const exactOntology = (relations: unknown[]) => expectedOntology.every(
    ({id, sourceTypes, targetTypes, pairs, cycle}) => {
      const matching = relations.filter((row) =>
        isObject(row) && row.relation_id === id);
      if (matching.length !== 1 || !isObject(matching[0])) return false;
      const row = matching[0]!;
      return exactStringSet(row.source_types, sourceTypes) &&
        exactStringSet(row.target_types, targetTypes) &&
        exactPairSet(row.allowed_type_pairs, pairs) &&
        row.cycle_policy === cycle && row.authority_effect === "none";
    },
  );
  if (!exact(descriptorRelations) || !exact(admissionRelations) ||
      !exactOntology(ontologyRelations) || admission.result !== "pass" ||
      admission.authority_effect !== "none" || ontology.authority_effect !== "none") {
    return fail("VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID", "relations");
  }
  const properties = object(portable.properties,
    "VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID");
  if (properties["creation.extension_policy"] !== "additive-validation-only" ||
      properties["creation.validator_count"] !==
        "zero-or-more-exact-owner-bound-rule-validators") {
    return fail("VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID", "properties");
  }
  return Object.freeze({owner, admission, ontology, parityRaw});
};

export const evaluateValueObjectRelations = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
  rawInputs: Readonly<Record<string, string>>,
) => {
  const directKeys = VALUE_OBJECT_DIRECT_HANDLES.map(({node_id: nodeId}) => nodeId);
  const expectedKeys = [...directKeys, VALUE_OBJECT_PARITY_HANDLE.node_id];
  if (!exactSet(Object.keys(upstream), expectedKeys)) {
    return fail("VALUE_OBJECT_RELATION_HANDLE_SET_MISMATCH");
  }
  const relationOwner = relationOwnerInputs(rawInputs);
  const directUpstream = Object.freeze(Object.fromEntries(directKeys.map((nodeId) =>
    [nodeId, upstream[nodeId]!]))) as Readonly<Record<string,
      FactoryUpstreamResultV1>>;
  const expectedParity = proveValueObjectParity(directUpstream,
    relationOwner.parityRaw);
  const parityUpstream = upstream[VALUE_OBJECT_PARITY_HANDLE.node_id]!;
  if (parityUpstream.node_id !== VALUE_OBJECT_PARITY_HANDLE.node_id ||
      parityUpstream.provider_id !== VALUE_OBJECT_PARITY_HANDLE.provider_id ||
      !/^[a-f0-9]{64}$/u.test(parityUpstream.semantic_sha256)) {
    return fail("VALUE_OBJECT_RELATION_PARITY_INVALID", "handle");
  }
  const parityOutput = object(parityUpstream.semantic_output,
    "VALUE_OBJECT_RELATION_PARITY_INVALID");
  const parityProof = object(parityOutput.proof,
    "VALUE_OBJECT_RELATION_PARITY_INVALID");
  if (!same(parityProof, expectedParity)) {
    return fail("VALUE_OBJECT_RELATION_PARITY_INVALID", "proof");
  }
  const rows = VALUE_OBJECT_DIRECT_HANDLES.flatMap((handle) => {
    const base = relationOwner.owner.definition.factories.base;
    const extension = relationOwner.owner.definition.factories.extension;
    return [
      Object.freeze({language: handle.language,
        relation_id: "architecture.constructed_by" as const,
        source_id: handle.target_id,
        source_type: "architecture.ValueObjectImplementation",
        target_id: base.factory_id,
        target_type: "architecture.ValueObjectFactoryProvider",
        ordinal: null, cycle_policy: "not-applicable" as const}),
      ...relationOwner.owner.definition.validators.map((validator, ordinal) =>
        Object.freeze({language: handle.language,
          relation_id: "architecture.validated_by" as const,
          source_id: validator.origin === "base" ? base.factory_id
            : extension.factory_id,
          source_type: "architecture.ValueObjectFactoryProvider",
          target_id: validator.validator_id,
          target_type: "architecture.RuleImplementation",
          ordinal, cycle_policy: "not-applicable" as const})),
      Object.freeze({language: handle.language,
        relation_id: "architecture.extends_factory" as const,
        source_id: extension.factory_id,
        source_type: "architecture.ValueObjectFactoryProvider",
        target_id: base.factory_id,
        target_type: "architecture.ValueObjectFactoryProvider",
        ordinal: null, cycle_policy: "acyclic" as const}),
    ];
  });
  if (rows.filter(({relation_id}) => relation_id ===
      "architecture.constructed_by").length !== 3) {
    return fail("VALUE_OBJECT_RELATION_CONSTRUCTED_BY_INVALID");
  }
  if (rows.filter(({relation_id}) => relation_id ===
      "architecture.validated_by").length !== 9) {
    return fail("VALUE_OBJECT_RELATION_VALIDATED_BY_INVALID");
  }
  const extensions = rows.filter(({relation_id}) => relation_id ===
    "architecture.extends_factory");
  if (extensions.length !== 3 || extensions.some(({source_id, target_id}) =>
    source_id === target_id)) {
    return fail("VALUE_OBJECT_RELATION_EXTENDS_FACTORY_INVALID");
  }
  return Object.freeze({relationOwner, directUpstream, expectedParity,
    parityUpstream, relation_rows: Object.freeze(rows)});
};

const parityProofFrom = (upstream: any): any =>
  upstream[VALUE_OBJECT_PARITY_HANDLE.node_id].semantic_output.proof;

type RelationHostile = Readonly<{
  id: string;
  code: ValueObjectRelationFindingCode;
  apply: (upstream: any, raw: Record<string, string>) => void;
}>;

const relationHostiles: readonly RelationHostile[] = Object.freeze([
  Object.freeze({id: "relation/missing-direct", code: "VALUE_OBJECT_RELATION_HANDLE_SET_MISMATCH", apply: (u: any) => { delete u[VALUE_OBJECT_DIRECT_HANDLES[0]!.node_id]; }}),
  Object.freeze({id: "relation/missing-parity", code: "VALUE_OBJECT_RELATION_HANDLE_SET_MISMATCH", apply: (u: any) => { delete u[VALUE_OBJECT_PARITY_HANDLE.node_id]; }}),
  Object.freeze({id: "relation/wrong-parity-provider", code: "VALUE_OBJECT_RELATION_PARITY_INVALID", apply: (u: any) => { u[VALUE_OBJECT_PARITY_HANDLE.node_id].provider_id = "wrong-provider"; }}),
  Object.freeze({id: "relation/totals-only-parity", code: "VALUE_OBJECT_RELATION_PARITY_INVALID", apply: (u: any) => { u[VALUE_OBJECT_PARITY_HANDLE.node_id].semantic_output = {accounting: {positives: 17}}; }}),
  Object.freeze({id: "relation/parity-proof-drift", code: "VALUE_OBJECT_RELATION_PARITY_INVALID", apply: (u: any) => { parityProofFrom(u).portable_projection.concept_id = "wrong.Concept"; }}),
  Object.freeze({id: "relation/descriptor-constructed-target", code: "VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID", apply: (_u: any, r: Record<string, string>) => { const x = JSON.parse(r.descriptor!); x.portable_architecture.relations[0].target_type = "wrong.Factory"; r.descriptor = JSON.stringify(x); }}),
  Object.freeze({id: "relation/descriptor-validator-target", code: "VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID", apply: (_u: any, r: Record<string, string>) => { const x = JSON.parse(r.descriptor!); x.portable_architecture.relations[1].target_type = "wrong.Rule"; r.descriptor = JSON.stringify(x); }}),
  Object.freeze({id: "relation/descriptor-extension-cycle", code: "VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID", apply: (_u: any, r: Record<string, string>) => { const x = JSON.parse(r.descriptor!); x.portable_architecture.relations[2].cycle_policy = "not-applicable"; r.descriptor = JSON.stringify(x); }}),
  Object.freeze({id: "relation/descriptor-extension-policy", code: "VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID", apply: (_u: any, r: Record<string, string>) => { const x = JSON.parse(r.descriptor!); x.portable_architecture.properties["creation.extension_policy"] = "replacement"; r.descriptor = JSON.stringify(x); }}),
  Object.freeze({id: "relation/admission-missing-relation", code: "VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID", apply: (_u: any, r: Record<string, string>) => { const x = JSON.parse(r.protocol_admission!); x.selected_relations.pop(); r.protocol_admission = JSON.stringify(x); }}),
  Object.freeze({id: "relation/admission-authority", code: "VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID", apply: (_u: any, r: Record<string, string>) => { const x = JSON.parse(r.protocol_admission!); x.authority_effect = "promote"; r.protocol_admission = JSON.stringify(x); }}),
  Object.freeze({id: "relation/ontology-constructed-endpoint", code: "VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID", apply: (_u: any, r: Record<string, string>) => { const x = JSON.parse(r.ontology!); x.relation_definitions.find((v: any) => v.relation_id === "architecture.constructed_by").target_types = ["wrong.Factory"]; r.ontology = JSON.stringify(x); }}),
  Object.freeze({id: "relation/ontology-validated-endpoint", code: "VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID", apply: (_u: any, r: Record<string, string>) => { const x = JSON.parse(r.ontology!); x.relation_definitions.find((v: any) => v.relation_id === "architecture.validated_by").target_types = ["wrong.Rule"]; r.ontology = JSON.stringify(x); }}),
  Object.freeze({id: "relation/ontology-extension-cycle", code: "VALUE_OBJECT_RELATION_OWNER_MATERIAL_INVALID", apply: (_u: any, r: Record<string, string>) => { const x = JSON.parse(r.ontology!); x.relation_definitions.find((v: any) => v.relation_id === "architecture.extends_factory").cycle_policy = "not-applicable"; r.ontology = JSON.stringify(x); }}),
]);

export const proveValueObjectRelations = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
  rawInputs: Readonly<Record<string, string>>,
): ValueObjectRelationsProofV1 => {
  const evaluated = evaluateValueObjectRelations(upstream, rawInputs);
  const hostileMutations = relationHostiles.map(({id, code, apply}) => {
    const mutatedUpstream = clone(upstream);
    const mutatedRaw = clone(rawInputs) as Record<string, string>;
    apply(mutatedUpstream, mutatedRaw);
    try {
      evaluateValueObjectRelations(mutatedUpstream, mutatedRaw);
    } catch (error: unknown) {
      if (isObject(error) && error.code === code) return Object.freeze({
        mutation_id: id, status: "killed" as const, finding_code: code,
      });
      throw error;
    }
    return fail("VALUE_OBJECT_RELATION_AUTHORITY_INVALID", `survived:${id}`);
  });
  return Object.freeze({
    schema_version: "ValueObjectRelationsProof/v1" as const,
    result: "pass" as const,
    composed_from: Object.freeze([
      ...VALUE_OBJECT_DIRECT_HANDLES.map((handle) => Object.freeze({
        node_id: handle.node_id,
        provider_id: handle.provider_id,
        semantic_sha256: upstream[handle.node_id]!.semantic_sha256,
      })),
      Object.freeze({node_id: VALUE_OBJECT_PARITY_HANDLE.node_id,
        provider_id: VALUE_OBJECT_PARITY_HANDLE.provider_id,
        semantic_sha256:
          upstream[VALUE_OBJECT_PARITY_HANDLE.node_id]!.semantic_sha256}),
    ]),
    relation_rows: evaluated.relation_rows,
    obligations: Object.freeze(RELATION_OBLIGATION_IDS.map((obligationId) =>
      Object.freeze({obligation_id: obligationId, status: "passed" as const}))),
    hostile_mutations: Object.freeze(hostileMutations),
    claim_ceiling: "exact candidate-local constructed_by, validated_by, and acyclic extends_factory relation proof over the three locked Settlement Value Object direct proofs and their recomputed parity proof, current owner descriptor, protocol admission, and ontology endpoints; this proves owner-bound base-before-extension validators and additive-validation-only structure, not arbitrary factories, runtime interception, business correctness beyond the fixture, candidate projection, promotion, publication, release, deployment, or production",
    authority_effect: "none" as const,
  });
};
