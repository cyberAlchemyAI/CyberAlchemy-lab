import {createHash} from "node:crypto";

import {
  applyCompleteValueMutant,
  decodeCompleteValueDefinitionV1,
  decodeCompleteValueDenominatorV1,
  decodeCompleteValueMutationCatalogueV1,
  evaluateCompleteValue,
  type CompleteValueFindingCode,
} from "../../../../families/complete-value/index.js";
import {
  canonicalConstructionObservationJson,
  mintConstructionObservationV1,
  type LockedConstructionObserverRefV1,
} from "../../../../kernel/evidence/construction-observation/index.js";

type JsonObject = Record<string, unknown>;
type ExactRef = Readonly<{path: string; sha256: string}>;

export const PYTHON_VALUE_OBJECT_RAW_PATHS = Object.freeze({
  definition:
    "projects/domainspec-v2/impl/architecture-conformance/families/complete-value/fixtures/settlement-value/definition.json",
  denominator:
    "projects/domainspec-v2/impl/architecture-conformance/families/complete-value/fixtures/settlement-value/denominator.json",
  mutations:
    "projects/domainspec-v2/impl/architecture-conformance/families/complete-value/fixtures/settlement-value/mutants.json",
  descriptor:
    "projects/domainspec-v2/development/remaining-meta-types/admissions/value-object/cross-language-realization-descriptor.json",
  source:
    "projects/domainspec-v2/impl/architecture-conformance/targets/python/remaining_types/value_object_v1.py",
  observer:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/value-object/python/complete-value-v1/observe_python_value_object.py",
  supervisor:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/value-object/python/complete-value-v1/run_python_value_object_proof.py",
  proof_builder:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/value-object/python/complete-value-v1/index.ts",
  provider:
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/python-value-object-v1.ts",
  family_api:
    "projects/domainspec-v2/impl/architecture-conformance/families/complete-value/index.ts",
  kernel_api:
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/construction-observation/index.ts",
  binding:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/value-object/python/complete-value-v1/python-binding.json",
});

export type PythonValueObjectRawInputs = Readonly<Record<
keyof typeof PYTHON_VALUE_OBJECT_RAW_PATHS, string
>>;

type PythonValueObjectBindingV1 = Readonly<{
  schema_version: "PythonValueObjectBinding/v1";
  binding_id: "python.settlement-value.complete-value/v1";
  target_id: "value-object.python.settlement-value/v1";
  protocol_id: "python.owned-value-object-factory/v1";
  definition_ref: ExactRef;
  denominator_ref: ExactRef;
  mutation_catalogue_ref: ExactRef;
  descriptor_ref: ExactRef;
  source_ref: ExactRef;
  observer_ref: ExactRef;
  supervisor_ref: ExactRef;
  proof_builder_ref: ExactRef;
  provider_ref: ExactRef;
  family_api_ref: ExactRef;
  kernel_api_ref: ExactRef;
  observer_id: "observer.python-value-object-closed-subset/v1";
  observer_owner_ref: "python-value-object-proof-harness";
  proof_mechanism: "exact-source-ast-bytecode-plus-two-fresh-processes";
  python_version: string;
  python_executable_path: string;
  python_executable_sha256: string;
  authority_effect: "none";
  binding_sha256: string;
}>;

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const sha256 = (value: string | Uint8Array): string => createHash("sha256")
  .update(value).digest("hex");
const isObject = (value: unknown): value is JsonObject => value !== null
  && typeof value === "object" && !Array.isArray(value);
const fail = (code: string, detail?: string): never => {
  throw Object.assign(new Error(detail ? `${code}:${detail}` : code), {code});
};
const exactKeys = (value: JsonObject, expected: readonly string[], code: string): void => {
  if (JSON.stringify(Object.keys(value).sort(compareUtf8))
      !== JSON.stringify([...expected].sort(compareUtf8))) fail(code);
};
const parseJson = (bytes: string, code: string): JsonObject => {
  try {
    const value: unknown = JSON.parse(bytes);
    return isObject(value) ? value : fail(code);
  } catch (error: unknown) {
    if (isObject(error) && error.code === code) throw error;
    return fail(code);
  }
};
const expectObject = (value: unknown, code: string): JsonObject =>
  isObject(value) ? value : fail(code);
const expectArray = (value: unknown, code: string): unknown[] =>
  Array.isArray(value) ? value : fail(code);
const expectString = (value: unknown, code: string): string =>
  typeof value === "string" && value.length > 0 ? value : fail(code);
const expectSha256 = (value: unknown, code: string): string => {
  const digest = expectString(value, code);
  return /^[a-f0-9]{64}$/u.test(digest) ? digest : fail(code);
};
const same = (left: unknown, right: unknown): boolean =>
  canonicalConstructionObservationJson(left)
    === canonicalConstructionObservationJson(right);
const decodeRef = (value: unknown, path: string): ExactRef => {
  const source = expectObject(value, "PY_VALUE_OBJECT_BINDING_REF_INVALID");
  exactKeys(source, ["path", "sha256"], "PY_VALUE_OBJECT_BINDING_REF_INVALID");
  if (source.path !== path) fail("PY_VALUE_OBJECT_BINDING_REF_INVALID", path);
  return Object.freeze({
    path,
    sha256: expectSha256(source.sha256, "PY_VALUE_OBJECT_BINDING_REF_INVALID"),
  });
};

const snapshotRaw = (
  incoming: Readonly<Record<string, string>>,
): PythonValueObjectRawInputs => Object.freeze(Object.fromEntries(
  (Object.keys(PYTHON_VALUE_OBJECT_RAW_PATHS) as readonly (
    keyof typeof PYTHON_VALUE_OBJECT_RAW_PATHS
  )[]).map((role) => {
    const value = incoming[role];
    return [role, typeof value === "string"
      ? `${value}` : fail("PY_VALUE_OBJECT_RAW_INPUT_MISSING", role)];
  }),
)) as PythonValueObjectRawInputs;

const decodeBinding = (
  bytes: string,
  raw: PythonValueObjectRawInputs,
): PythonValueObjectBindingV1 => {
  const source = parseJson(bytes, "PY_VALUE_OBJECT_BINDING_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "binding_id", "target_id", "protocol_id",
    "definition_ref", "denominator_ref", "mutation_catalogue_ref",
    "descriptor_ref", "source_ref", "observer_ref", "supervisor_ref",
    "proof_builder_ref", "provider_ref", "family_api_ref", "kernel_api_ref",
    "observer_id", "observer_owner_ref", "proof_mechanism", "python_version",
    "python_executable_path", "python_executable_sha256", "authority_effect",
    "binding_sha256",
  ], "PY_VALUE_OBJECT_BINDING_SHAPE_INVALID");
  if (source.schema_version !== "PythonValueObjectBinding/v1"
      || source.binding_id !== "python.settlement-value.complete-value/v1"
      || source.target_id !== "value-object.python.settlement-value/v1"
      || source.protocol_id !== "python.owned-value-object-factory/v1"
      || source.observer_id !== "observer.python-value-object-closed-subset/v1"
      || source.observer_owner_ref !== "python-value-object-proof-harness"
      || source.proof_mechanism
        !== "exact-source-ast-bytecode-plus-two-fresh-processes"
      || source.authority_effect !== "none") {
    return fail("PY_VALUE_OBJECT_BINDING_POLICY_INVALID");
  }
  const binding = Object.freeze({
    schema_version: "PythonValueObjectBinding/v1" as const,
    binding_id: "python.settlement-value.complete-value/v1" as const,
    target_id: "value-object.python.settlement-value/v1" as const,
    protocol_id: "python.owned-value-object-factory/v1" as const,
    definition_ref: decodeRef(source.definition_ref,
      PYTHON_VALUE_OBJECT_RAW_PATHS.definition),
    denominator_ref: decodeRef(source.denominator_ref,
      PYTHON_VALUE_OBJECT_RAW_PATHS.denominator),
    mutation_catalogue_ref: decodeRef(source.mutation_catalogue_ref,
      PYTHON_VALUE_OBJECT_RAW_PATHS.mutations),
    descriptor_ref: decodeRef(source.descriptor_ref,
      PYTHON_VALUE_OBJECT_RAW_PATHS.descriptor),
    source_ref: decodeRef(source.source_ref, PYTHON_VALUE_OBJECT_RAW_PATHS.source),
    observer_ref: decodeRef(source.observer_ref,
      PYTHON_VALUE_OBJECT_RAW_PATHS.observer),
    supervisor_ref: decodeRef(source.supervisor_ref,
      PYTHON_VALUE_OBJECT_RAW_PATHS.supervisor),
    proof_builder_ref: decodeRef(source.proof_builder_ref,
      PYTHON_VALUE_OBJECT_RAW_PATHS.proof_builder),
    provider_ref: decodeRef(source.provider_ref,
      PYTHON_VALUE_OBJECT_RAW_PATHS.provider),
    family_api_ref: decodeRef(source.family_api_ref,
      PYTHON_VALUE_OBJECT_RAW_PATHS.family_api),
    kernel_api_ref: decodeRef(source.kernel_api_ref,
      PYTHON_VALUE_OBJECT_RAW_PATHS.kernel_api),
    observer_id: "observer.python-value-object-closed-subset/v1" as const,
    observer_owner_ref: "python-value-object-proof-harness" as const,
    proof_mechanism:
      "exact-source-ast-bytecode-plus-two-fresh-processes" as const,
    python_version: expectString(source.python_version,
      "PY_VALUE_OBJECT_BINDING_TOOLCHAIN_INVALID"),
    python_executable_path: expectString(source.python_executable_path,
      "PY_VALUE_OBJECT_BINDING_TOOLCHAIN_INVALID"),
    python_executable_sha256: expectSha256(source.python_executable_sha256,
      "PY_VALUE_OBJECT_BINDING_TOOLCHAIN_INVALID"),
    authority_effect: "none" as const,
    binding_sha256: expectSha256(source.binding_sha256,
      "PY_VALUE_OBJECT_BINDING_DIGEST_INVALID"),
  }) satisfies PythonValueObjectBindingV1;
  const {binding_sha256: _digest, ...body} = binding;
  if (sha256(canonicalConstructionObservationJson(body))
      !== binding.binding_sha256) fail("PY_VALUE_OBJECT_BINDING_DIGEST_STALE");
  const roles = Object.freeze({
    definition_ref: "definition", denominator_ref: "denominator",
    mutation_catalogue_ref: "mutations", descriptor_ref: "descriptor",
    source_ref: "source", observer_ref: "observer", supervisor_ref: "supervisor",
    proof_builder_ref: "proof_builder", provider_ref: "provider",
    family_api_ref: "family_api", kernel_api_ref: "kernel_api",
  } as const);
  for (const [refName, role] of Object.entries(roles) as readonly [
    keyof typeof roles, keyof PythonValueObjectRawInputs,
  ][]) {
    if (sha256(raw[role]) !== binding[refName].sha256) {
      return fail("PY_VALUE_OBJECT_BINDING_INPUT_STALE", role);
    }
  }
  return binding;
};

const pythonProtocol = (value: string): string =>
  value.replace(/^typescript\./u, "python.");

export const composePythonValueObjectProof = (input: Readonly<{
  raw_inputs: Readonly<Record<string, string>>;
  native_proof: unknown;
}>) => {
  const raw = snapshotRaw(input.raw_inputs);
  const binding = decodeBinding(raw.binding, raw);
  const definition = decodeCompleteValueDefinitionV1(raw.definition,
    PYTHON_VALUE_OBJECT_RAW_PATHS.descriptor, raw.descriptor);
  const denominator = decodeCompleteValueDenominatorV1(raw.denominator,
    raw.definition, definition, PYTHON_VALUE_OBJECT_RAW_PATHS.definition);
  const catalogue = decodeCompleteValueMutationCatalogueV1(raw.mutations,
    denominator, definition);
  const native = expectObject(input.native_proof,
    "PY_VALUE_OBJECT_NATIVE_PROOF_INVALID");
  exactKeys(native, [
    "schema_version", "target", "binding", "runtime_observation",
    "process_evidence", "static_binding_controls", "static_binding_accounting",
    "claim_ceiling", "authority_effect",
  ], "PY_VALUE_OBJECT_NATIVE_PROOF_INVALID");
  const target = expectObject(native.target, "PY_VALUE_OBJECT_NATIVE_TARGET_INVALID");
  const nativeBinding = expectObject(native.binding,
    "PY_VALUE_OBJECT_NATIVE_BINDING_INVALID");
  const runtime = expectObject(native.runtime_observation,
    "PY_VALUE_OBJECT_NATIVE_OBSERVATION_INVALID");
  const sourceProof = expectObject(runtime.source_proof,
    "PY_VALUE_OBJECT_NATIVE_SOURCE_INVALID");
  const toolchain = expectObject(runtime.toolchain,
    "PY_VALUE_OBJECT_NATIVE_TOOLCHAIN_INVALID");
  const process = expectObject(native.process_evidence,
    "PY_VALUE_OBJECT_NATIVE_PROCESS_INVALID");
  const staticAccounting = expectObject(native.static_binding_accounting,
    "PY_VALUE_OBJECT_NATIVE_CONTROLS_INVALID");
  const staticControls = expectArray(native.static_binding_controls,
    "PY_VALUE_OBJECT_NATIVE_CONTROLS_INVALID").map((item) => {
    const value = expectObject(item, "PY_VALUE_OBJECT_NATIVE_CONTROLS_INVALID");
    if (value.evidence_kind !== "python-static-binding-control"
        || value.status !== "rejected") {
      return fail("PY_VALUE_OBJECT_NATIVE_CONTROLS_INVALID");
    }
    return Object.freeze({control_id: expectString(value.control_id,
      "PY_VALUE_OBJECT_NATIVE_CONTROLS_INVALID"),
    evidence_kind: "python-static-binding-control" as const,
    status: "rejected" as const,
    error_code: expectString(value.error_code,
      "PY_VALUE_OBJECT_NATIVE_CONTROLS_INVALID")});
  });
  if (native.schema_version !== "PythonValueObjectNativeProof/v1"
      || native.authority_effect !== "none"
      || target.target_id !== binding.target_id
      || target.target_sha256 !== binding.source_ref.sha256
      || target.language !== "python" || target.protocol_id !== binding.protocol_id
      || nativeBinding.binding_id !== binding.binding_id
      || nativeBinding.binding_sha256 !== binding.binding_sha256
      || runtime.schema_version !== "PythonValueObjectRuntimeObservation/v1"
      || runtime.authority_effect !== "none"
      || sourceProof.source_sha256 !== binding.source_ref.sha256
      || toolchain.python_version !== binding.python_version
      || toolchain.executable_path !== binding.python_executable_path
      || toolchain.executable_sha256 !== binding.python_executable_sha256
      || process.executions !== 2 || process.distinct_pids !== 2
      || process.pids_redacted_from_semantic_proof !== true
      || process.semantic_replay_equal !== true
      || process.input_materialization !== "json-inert-owner-cases"
      || expectSha256(process.semantic_replay_sha256,
        "PY_VALUE_OBJECT_NATIVE_PROCESS_INVALID")
        !== sha256(canonicalConstructionObservationJson(runtime))
      || staticControls.length !== 8
      || new Set(staticControls.map(({control_id: id}) => id)).size !== 8
      || staticAccounting.declared !== 8 || staticAccounting.rejected !== 8
      || typeof native.claim_ceiling !== "string") {
    return fail("PY_VALUE_OBJECT_NATIVE_PROOF_INVALID");
  }
  const rows = expectArray(runtime.results,
    "PY_VALUE_OBJECT_NATIVE_RESULTS_INVALID").map((item) =>
    expectObject(item, "PY_VALUE_OBJECT_NATIVE_RESULTS_INVALID"));
  if (rows.length !== definition.cases.length
      || !same(rows.map(({case_id: id}) => id),
        definition.cases.map(({case_id: id}) => id))) {
    return fail("PY_VALUE_OBJECT_NATIVE_CASE_LEDGER_MISMATCH");
  }
  const observer: LockedConstructionObserverRefV1 = Object.freeze({
    role: "independent-construction-observer",
    observer_id: binding.observer_id,
    observer_sha256: binding.observer_ref.sha256,
    owner_ref: binding.observer_owner_ref,
    provider_id: "python-value-object-v1",
    provider_sha256: binding.provider_ref.sha256,
  });
  const attempts = definition.cases.map((testCase, index) => {
    const row = rows[index]!;
    const expectedOk = testCase.input_class === "valid";
    const nativeBindings = expectArray(row.component_bindings,
      "PY_VALUE_OBJECT_NATIVE_COMPONENTS_INVALID").map((item) =>
      expectObject(item, "PY_VALUE_OBJECT_NATIVE_COMPONENTS_INVALID"));
    const expectedNativeBindings = definition.components.map((component) => ({
      component_name: component.component_name,
      protocol_id: pythonProtocol(component.protocol_id),
      protocol_sha256: component.protocol_sha256,
      normalized_value_sha256:
        testCase.normalized_component_values[component.component_name],
      nested_value_object: component.nested_value_object,
    }));
    const trace = expectArray(row.validator_trace,
      "PY_VALUE_OBJECT_NATIVE_TRACE_INVALID").map(String);
    const expectedTraceLength = expectedOk ? definition.validators.length : 2;
    const expectedTrace = definition.validators.slice(0, expectedTraceLength)
      .map(({validator_id: id, validator_sha256: digest}) => `${id}@${digest}`);
    const expectedTuple = expectedOk ? expectedNativeBindings.map(
      ({normalized_value_sha256: value}) => value) : null;
    if (row.case_id !== testCase.case_id
        || row.input_class !== testCase.input_class || row.ok !== expectedOk
        || row.object_created !== expectedOk
        || !same(row.failure_codes, testCase.expected_failure_codes)
        || !same(trace, expectedTrace) || !same(nativeBindings, expectedNativeBindings)
        || !same(row.tuple, expectedTuple)
        || row.formation_ordinal !== (expectedOk ? trace.length : null)
        || (expectedOk && (row.frozen !== true || row.nested_frozen !== true
          || row.nested_alias !== false || row.nested_mutation !== false))) {
      return fail("PY_VALUE_OBJECT_NATIVE_CASE_INVALID", testCase.case_id);
    }
    const portableBindings = nativeBindings.map((component, componentIndex) => ({
      component_name: expectString(component.component_name,
        "PY_VALUE_OBJECT_NATIVE_COMPONENTS_INVALID"),
      protocol_id: definition.components[componentIndex]!.protocol_id,
      protocol_sha256: expectSha256(component.protocol_sha256,
        "PY_VALUE_OBJECT_NATIVE_COMPONENTS_INVALID"),
      normalized_value_sha256: expectSha256(component.normalized_value_sha256,
        "PY_VALUE_OBJECT_NATIVE_COMPONENTS_INVALID"),
      nested_value_object: component.nested_value_object === true,
    }));
    return {
      case_id: testCase.case_id,
      input_class: testCase.input_class,
      component_bindings: portableBindings,
      validator_trace: trace.map((entry, ordinal) => {
        const [validatorId, validatorSha256] = entry.split("@");
        const owner = definition.validators.find(({validator_id: id}) =>
          id === validatorId);
        if (!owner || owner.validator_sha256 !== validatorSha256) {
          return fail("PY_VALUE_OBJECT_NATIVE_VALIDATOR_INVALID");
        }
        return {validator_id: validatorId!, validator_sha256: validatorSha256!,
          origin: owner.origin, ordinal, outcome: row.ok ? "pass" as const
            : ordinal === trace.length - 1 ? "fail" as const : "pass" as const};
      }),
      formation_ordinal: row.formation_ordinal as number | null,
      result: row.ok ? {status: "formed" as const, object_created: true,
        failure_codes: [] as readonly string[]} : {
        status: "validation-failure" as const, object_created: false,
        failure_codes: expectArray(row.failure_codes,
          "PY_VALUE_OBJECT_NATIVE_FAILURE_INVALID").map(String)},
      normalized_tuple: row.ok ? portableBindings.map(({component_name,
        normalized_value_sha256}) => ({component_name, normalized_value_sha256}))
        : null,
      immutability: {formed_value_frozen: row.frozen === true,
        recursively_owned_components_frozen: row.nested_frozen === true,
        nested_alias_observed: row.nested_alias === true,
        nested_mutation_observed: row.nested_mutation === true},
    };
  });
  const ownerProbes = [
    {...definition.equality_contract.equal_probe,
      relation: "equal-tuple" as const, varied_component_name: null},
    ...definition.equality_contract.component_variants.map((variant) => ({
      ...variant, relation: "component-variant" as const,
      varied_component_name: variant.component_name,
    })),
  ];
  const nativeProbes = expectArray(runtime.equality_probes,
    "PY_VALUE_OBJECT_NATIVE_PROBES_INVALID").map((item) =>
    expectObject(item, "PY_VALUE_OBJECT_NATIVE_PROBES_INVALID"));
  if (nativeProbes.length !== ownerProbes.length) {
    return fail("PY_VALUE_OBJECT_NATIVE_PROBES_INVALID");
  }
  const equalityProbes = ownerProbes.map((owner, index) => {
    const observed = nativeProbes[index]!;
    if (observed.probe_id !== owner.probe_id
        || observed.left_case_id !== owner.left_case_id
        || observed.right_case_id !== owner.right_case_id
        || observed.relation !== owner.relation
        || observed.varied_component_name !== owner.varied_component_name
        || observed.references_distinct !== true
        || typeof observed.observed_equal !== "boolean"
        || typeof observed.left_hash !== "string"
        || !/^-?[0-9]+$/u.test(observed.left_hash)
        || typeof observed.right_hash !== "string"
        || !/^-?[0-9]+$/u.test(observed.right_hash)) {
      return fail("PY_VALUE_OBJECT_NATIVE_PROBES_INVALID", owner.probe_id);
    }
    return {probe_id: owner.probe_id,
      left_case_id: owner.left_case_id,
      right_case_id: owner.right_case_id,
      relation: owner.relation,
      varied_component_name: owner.varied_component_name,
      references_distinct: true,
      observed_equal: observed.observed_equal,
      left_hash_sha256: sha256(observed.left_hash),
      right_hash_sha256: sha256(observed.right_hash)};
  });
  const nested = expectObject(runtime.nested_probe,
    "PY_VALUE_OBJECT_NATIVE_NESTED_INVALID");
  const nativeNestedComponent = definition.components.find(
    ({nested_value_object: nestedValue}) => nestedValue);
  if (!nativeNestedComponent || nested.component_name !== nativeNestedComponent.component_name
      || nested.protocol_id !== pythonProtocol(nativeNestedComponent.protocol_id)
      || nested.protocol_sha256 !== nativeNestedComponent.protocol_sha256
      || nested.equal_observed !== true || nested.equal_hash_congruent !== true
      || nested.variant_unequal_observed !== true) {
    return fail("PY_VALUE_OBJECT_NATIVE_NESTED_INVALID");
  }
  const extension = expectObject(runtime.extension,
    "PY_VALUE_OBJECT_NATIVE_EXTENSION_INVALID");
  const baseValidators = definition.validators.filter(({origin}) => origin === "base");
  const validationProbe = expectObject(extension.validation_probe,
    "PY_VALUE_OBJECT_NATIVE_EXTENSION_INVALID");
  if (!same(extension.base_factory_ref, definition.factories.base)
      || !same(extension.extension_factory_ref, definition.factories.extension)
      || !same(extension.base_validators, baseValidators)
      || !same(extension.extension_validators, definition.validators)
      || !same(extension.added_validators,
        definition.validators.filter(({origin}) => origin === "extension"))
      || extension.base_preserved !== true
      || extension.tuple_and_hash_preserved !== true
      || extension.component_bindings_and_normalization_preserved !== true
      || extension.equality_preserved !== true
      || extension.recursive_immutability_preserved !== true
      || extension.concept_binding_preserved !== true
      || extension.extension_is_terminal !== true
      || validationProbe.base_ok !== true || validationProbe.extended_ok !== false
      || validationProbe.extended_object_created !== false
      || !same(validationProbe.extended_failure_codes,
        ["INACTIVE_SETTLEMENT_ACCOUNT"])
      || !same(validationProbe.extended_validator_trace,
        definition.validators.map(({validator_id: id,
          validator_sha256: digest}) => `${id}@${digest}`))) {
    return fail("PY_VALUE_OBJECT_NATIVE_EXTENSION_INVALID");
  }
  const observation = mintConstructionObservationV1({
    schema_version: "ConstructionObservation/v1",
    observation_id: "observation.value-object.python.settlement-value/v1",
    source_kind: "target-observation",
    observer_ref: observer,
    definition_ref: denominator.owner_definition_ref,
    factory_ref: definition.factories.base,
    attempts,
    equality_probes: equalityProbes,
    nested_delegations: [{component_name: nativeNestedComponent.component_name,
      protocol_id: nativeNestedComponent.protocol_id,
      protocol_sha256: nativeNestedComponent.protocol_sha256,
      equality_delegated: true, hash_delegated: true}],
    extension: {base_factory_ref: definition.factories.base,
      extension_factory_ref: definition.factories.extension,
      added_validators: definition.validators.filter(({origin}) =>
        origin === "extension"), altered_facets: [], cycle_detected: false},
    claim: "transport-observation-only-no-native-runtime-claim",
    collision_freedom_claim: false,
    authority_effect: "none",
  });
  const family = evaluateCompleteValue({definition, denominator, observation,
    locked_observer_ref: observer});
  if (family.verdict !== "pass") return fail("PY_VALUE_OBJECT_FAMILY_BLOCKED",
    family.findings.map(({code}) => code).join(","));
  const familyControls = catalogue.mutations.map((mutation) => {
    const result = evaluateCompleteValue({definition, denominator,
      observation: applyCompleteValueMutant(observation, mutation),
      locked_observer_ref: observer});
    const codes = new Set(result.findings.map(({code}) => code));
    if (result.verdict !== "fail"
        || !mutation.expected_finding_codes.every((code) =>
          codes.has(code as CompleteValueFindingCode))) {
      return fail("PY_VALUE_OBJECT_FAMILY_CONTROL_SURVIVED", mutation.mutation_id);
    }
    return Object.freeze({mutation_id: mutation.mutation_id,
      status: "killed" as const});
  });
  return Object.freeze({
    schema_version: "PythonValueObjectProof/v1" as const,
    result: "pass" as const,
    target: Object.freeze({target_id: binding.target_id,
      target_sha256: binding.source_ref.sha256, language: "python" as const,
      protocol_id: binding.protocol_id}),
    binding: Object.freeze({binding_id: binding.binding_id,
      binding_sha256: binding.binding_sha256}),
    native_runtime_observation: runtime,
    portable_protocol_projection: Object.freeze({
      from_prefix: "python.owned-value-component",
      to_owner_family_prefix: "typescript.owned-value-component",
      mapping_basis: "exact-component-name-and-protocol-digest",
    }),
    observation,
    family_evaluation: family,
    process_evidence: process,
    toolchain: Object.freeze({python_version: binding.python_version,
      executable_path: binding.python_executable_path,
      executable_sha256: binding.python_executable_sha256}),
    accounting: Object.freeze({positives: Object.freeze({declared: 7, passed: 7}),
      static_binding_controls: Object.freeze({declared: 8, rejected: 8}),
      predecessor_family_controls: Object.freeze({declared: familyControls.length,
        killed: familyControls.length})}),
    static_binding_controls: Object.freeze(staticControls),
    predecessor_family_controls: Object.freeze(familyControls),
    claim_ceiling: native.claim_ceiling as string,
    authority_effect: "none" as const,
  });
};
