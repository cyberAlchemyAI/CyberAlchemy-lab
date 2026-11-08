import {createHash} from "node:crypto";

import {
  applyIdentityLifecycleMutant,
  decodeIdentityLifecycleDefinitionV1,
  decodeIdentityLifecycleDenominatorV1,
  decodeIdentityLifecycleMutationCatalogueV1,
  evaluateIdentityLifecycle,
  type IdentityLifecycleFindingCode,
} from "../../../../families/identity-lifecycle/index.js";
import {
  canonicalConstructionObservationJson,
  mintEntityLifecycleConstructionObservationV1,
  type EntityConstructionRouteV1,
  type EntityLifecycleConstructionObservationV1,
  type LockedConstructionObserverRefV1,
} from "../../../../kernel/evidence/construction-observation/index.js";

type JsonObject = Record<string, unknown>;
type ExactRef = Readonly<{path: string; sha256: string}>;

export const PYTHON_ENTITY_RAW_PATHS = Object.freeze({
  definition:
    "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/fixtures/settlement-entity/definition.json",
  denominator:
    "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/fixtures/settlement-entity/denominator.json",
  mutations:
    "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/fixtures/settlement-entity/mutants.json",
  descriptor:
    "projects/domainspec-v2/development/remaining-meta-types/admissions/entity/cross-language-realization-descriptor.json",
  source:
    "projects/domainspec-v2/impl/architecture-conformance/targets/python/remaining_types/entity_v1.py",
  observer:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/entity/python/identity-lifecycle-v1/observe_python_entity.py",
  supervisor:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/entity/python/identity-lifecycle-v1/run_python_entity_proof.py",
  proof_builder:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/entity/python/identity-lifecycle-v1/index.ts",
  provider:
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/python-entity-v1.ts",
  family_api:
    "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/index.ts",
  family_decoder:
    "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/providers/decode-identity-lifecycle.ts",
  family_evaluator:
    "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/evaluator/evaluate-identity-lifecycle.ts",
  family_mutator:
    "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/mutations/apply-identity-lifecycle-mutant.ts",
  kernel_api:
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/construction-observation/index.ts",
  kernel_contracts:
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/construction-observation/entity-lifecycle-contracts.ts",
  kernel_evaluator:
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/construction-observation/entity-lifecycle-construction-observation.ts",
  binding:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/entity/python/identity-lifecycle-v1/python-binding.json",
});

export type PythonEntityRawInputs = Readonly<Record<
keyof typeof PYTHON_ENTITY_RAW_PATHS, string
>>;

type PythonEntityBindingV1 = Readonly<{
  schema_version: "PythonEntityBinding/v1";
  binding_id: "python.settlement-entity.identity-lifecycle/v1";
  target_id: "entity.python.settlement/v1";
  protocol_id: "python.validated-extensible-entity-factory/v1";
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
  family_decoder_ref: ExactRef;
  family_evaluator_ref: ExactRef;
  family_mutator_ref: ExactRef;
  kernel_api_ref: ExactRef;
  kernel_contracts_ref: ExactRef;
  kernel_evaluator_ref: ExactRef;
  observer_id: "observer.python-entity-closed-subset/v1";
  observer_owner_ref: "python-entity-proof-harness";
  proof_mechanism:
    "hash-locked-source-ast-bytecode-runtime-plus-two-fresh-processes";
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
const object = (value: unknown, code: string): JsonObject =>
  isObject(value) ? value : fail(code);
const array = (value: unknown, code: string): unknown[] =>
  Array.isArray(value) ? value : fail(code);
const string = (value: unknown, code: string): string =>
  typeof value === "string" && value.length > 0 ? value : fail(code);
const sha = (value: unknown, code: string): string => {
  const digest = string(value, code);
  return /^[a-f0-9]{64}$/u.test(digest) ? digest : fail(code);
};
const same = (left: unknown, right: unknown): boolean =>
  canonicalConstructionObservationJson(left)
    === canonicalConstructionObservationJson(right);

const snapshotRaw = (
  incoming: Readonly<Record<string, string>>,
): PythonEntityRawInputs => Object.freeze(Object.fromEntries(
  (Object.keys(PYTHON_ENTITY_RAW_PATHS) as readonly (
    keyof typeof PYTHON_ENTITY_RAW_PATHS
  )[]).map((role) => {
    const value = incoming[role];
    return [role, typeof value === "string"
      ? `${value}` : fail("PY_ENTITY_RAW_INPUT_MISSING", role)];
  }),
)) as PythonEntityRawInputs;

const decodeRef = (value: unknown, path: string): ExactRef => {
  const source = object(value, "PY_ENTITY_BINDING_REF_INVALID");
  exactKeys(source, ["path", "sha256"], "PY_ENTITY_BINDING_REF_INVALID");
  if (source.path !== path) fail("PY_ENTITY_BINDING_REF_INVALID", path);
  return Object.freeze({path,
    sha256: sha(source.sha256, "PY_ENTITY_BINDING_REF_INVALID")});
};

const decodeBinding = (
  bytes: string,
  raw: PythonEntityRawInputs,
): PythonEntityBindingV1 => {
  const source = parseJson(bytes, "PY_ENTITY_BINDING_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "binding_id", "target_id", "protocol_id",
    "definition_ref", "denominator_ref", "mutation_catalogue_ref",
    "descriptor_ref", "source_ref", "observer_ref", "supervisor_ref",
    "proof_builder_ref", "provider_ref", "family_api_ref",
    "family_decoder_ref", "family_evaluator_ref", "family_mutator_ref",
    "kernel_api_ref", "kernel_contracts_ref", "kernel_evaluator_ref",
    "observer_id", "observer_owner_ref", "proof_mechanism", "python_version",
    "python_executable_path", "python_executable_sha256", "authority_effect",
    "binding_sha256",
  ], "PY_ENTITY_BINDING_SHAPE_INVALID");
  if (source.schema_version !== "PythonEntityBinding/v1"
      || source.binding_id !== "python.settlement-entity.identity-lifecycle/v1"
      || source.target_id !== "entity.python.settlement/v1"
      || source.protocol_id !== "python.validated-extensible-entity-factory/v1"
      || source.observer_id !== "observer.python-entity-closed-subset/v1"
      || source.observer_owner_ref !== "python-entity-proof-harness"
      || source.proof_mechanism
        !== "hash-locked-source-ast-bytecode-runtime-plus-two-fresh-processes"
      || source.authority_effect !== "none") {
    return fail("PY_ENTITY_BINDING_POLICY_INVALID");
  }
  const binding = Object.freeze({
    schema_version: "PythonEntityBinding/v1" as const,
    binding_id: "python.settlement-entity.identity-lifecycle/v1" as const,
    target_id: "entity.python.settlement/v1" as const,
    protocol_id: "python.validated-extensible-entity-factory/v1" as const,
    definition_ref: decodeRef(source.definition_ref,
      PYTHON_ENTITY_RAW_PATHS.definition),
    denominator_ref: decodeRef(source.denominator_ref,
      PYTHON_ENTITY_RAW_PATHS.denominator),
    mutation_catalogue_ref: decodeRef(source.mutation_catalogue_ref,
      PYTHON_ENTITY_RAW_PATHS.mutations),
    descriptor_ref: decodeRef(source.descriptor_ref,
      PYTHON_ENTITY_RAW_PATHS.descriptor),
    source_ref: decodeRef(source.source_ref, PYTHON_ENTITY_RAW_PATHS.source),
    observer_ref: decodeRef(source.observer_ref, PYTHON_ENTITY_RAW_PATHS.observer),
    supervisor_ref: decodeRef(source.supervisor_ref,
      PYTHON_ENTITY_RAW_PATHS.supervisor),
    proof_builder_ref: decodeRef(source.proof_builder_ref,
      PYTHON_ENTITY_RAW_PATHS.proof_builder),
    provider_ref: decodeRef(source.provider_ref, PYTHON_ENTITY_RAW_PATHS.provider),
    family_api_ref: decodeRef(source.family_api_ref,
      PYTHON_ENTITY_RAW_PATHS.family_api),
    family_decoder_ref: decodeRef(source.family_decoder_ref,
      PYTHON_ENTITY_RAW_PATHS.family_decoder),
    family_evaluator_ref: decodeRef(source.family_evaluator_ref,
      PYTHON_ENTITY_RAW_PATHS.family_evaluator),
    family_mutator_ref: decodeRef(source.family_mutator_ref,
      PYTHON_ENTITY_RAW_PATHS.family_mutator),
    kernel_api_ref: decodeRef(source.kernel_api_ref,
      PYTHON_ENTITY_RAW_PATHS.kernel_api),
    kernel_contracts_ref: decodeRef(source.kernel_contracts_ref,
      PYTHON_ENTITY_RAW_PATHS.kernel_contracts),
    kernel_evaluator_ref: decodeRef(source.kernel_evaluator_ref,
      PYTHON_ENTITY_RAW_PATHS.kernel_evaluator),
    observer_id: "observer.python-entity-closed-subset/v1" as const,
    observer_owner_ref: "python-entity-proof-harness" as const,
    proof_mechanism:
      "hash-locked-source-ast-bytecode-runtime-plus-two-fresh-processes" as const,
    python_version: string(source.python_version,
      "PY_ENTITY_BINDING_TOOLCHAIN_INVALID"),
    python_executable_path: string(source.python_executable_path,
      "PY_ENTITY_BINDING_TOOLCHAIN_INVALID"),
    python_executable_sha256: sha(source.python_executable_sha256,
      "PY_ENTITY_BINDING_TOOLCHAIN_INVALID"),
    authority_effect: "none" as const,
    binding_sha256: sha(source.binding_sha256, "PY_ENTITY_BINDING_DIGEST_INVALID"),
  }) satisfies PythonEntityBindingV1;
  const {binding_sha256: _digest, ...body} = binding;
  if (sha256(canonicalConstructionObservationJson(body))
      !== binding.binding_sha256) fail("PY_ENTITY_BINDING_DIGEST_STALE");
  const roles = Object.freeze({
    definition_ref: "definition", denominator_ref: "denominator",
    mutation_catalogue_ref: "mutations", descriptor_ref: "descriptor",
    source_ref: "source", observer_ref: "observer", supervisor_ref: "supervisor",
    proof_builder_ref: "proof_builder", provider_ref: "provider",
    family_api_ref: "family_api", family_decoder_ref: "family_decoder",
    family_evaluator_ref: "family_evaluator", family_mutator_ref: "family_mutator",
    kernel_api_ref: "kernel_api", kernel_contracts_ref: "kernel_contracts",
    kernel_evaluator_ref: "kernel_evaluator",
  } as const);
  for (const [refName, role] of Object.entries(roles) as readonly [
    keyof typeof roles, keyof PythonEntityRawInputs,
  ][]) {
    if (sha256(raw[role]) !== binding[refName].sha256) {
      return fail("PY_ENTITY_BINDING_INPUT_STALE", role);
    }
  }
  return binding;
};

const SOURCE_CONTROL_IDS = Object.freeze([
  "per-call-validator-bypass", "remove-base-validator",
  "replace-identity-resolver", "allow-extension-cycle",
  "invalid-input-forms-snapshot", "mutable-snapshot",
  "complete-field-equality", "reconstruction-bypass",
  "transition-identity-replacement", "constructor-exposure",
  "route-whitelist-bypass",
] as const);

export const composePythonEntityProof = (input: Readonly<{
  raw_inputs: Readonly<Record<string, string>>;
  native_proof: unknown;
}>) => {
  const raw = snapshotRaw(input.raw_inputs);
  const binding = decodeBinding(raw.binding, raw);
  const definition = decodeIdentityLifecycleDefinitionV1(raw.definition,
    PYTHON_ENTITY_RAW_PATHS.descriptor, raw.descriptor);
  const denominator = decodeIdentityLifecycleDenominatorV1(raw.denominator,
    raw.definition, definition, PYTHON_ENTITY_RAW_PATHS.definition);
  const catalogue = decodeIdentityLifecycleMutationCatalogueV1(raw.mutations,
    denominator);
  const native = object(input.native_proof, "PY_ENTITY_NATIVE_PROOF_INVALID");
  exactKeys(native, [
    "schema_version", "target", "binding", "runtime_observation",
    "process_evidence", "target_source_controls", "target_source_accounting",
    "claim_ceiling", "authority_effect",
  ], "PY_ENTITY_NATIVE_PROOF_INVALID");
  const target = object(native.target, "PY_ENTITY_NATIVE_TARGET_INVALID");
  const nativeBinding = object(native.binding, "PY_ENTITY_NATIVE_BINDING_INVALID");
  const runtime = object(native.runtime_observation,
    "PY_ENTITY_NATIVE_OBSERVATION_INVALID");
  const sourceProof = object(runtime.source_proof,
    "PY_ENTITY_NATIVE_SOURCE_INVALID");
  const toolchain = object(runtime.toolchain,
    "PY_ENTITY_NATIVE_TOOLCHAIN_INVALID");
  const process = object(native.process_evidence,
    "PY_ENTITY_NATIVE_PROCESS_INVALID");
  const sourceAccounting = object(native.target_source_accounting,
    "PY_ENTITY_NATIVE_CONTROLS_INVALID");
  const sourceControls = array(native.target_source_controls,
    "PY_ENTITY_NATIVE_CONTROLS_INVALID").map((item) => {
    const control = object(item, "PY_ENTITY_NATIVE_CONTROLS_INVALID");
    if (control.evidence_kind !== "python-target-source-control"
        || control.status !== "rejected") {
      return fail("PY_ENTITY_NATIVE_CONTROLS_INVALID");
    }
    return Object.freeze({
      control_id: string(control.control_id, "PY_ENTITY_NATIVE_CONTROLS_INVALID"),
      evidence_kind: "python-target-source-control" as const,
      status: "rejected" as const,
      error_code: string(control.error_code, "PY_ENTITY_NATIVE_CONTROLS_INVALID"),
    });
  });
  if (native.schema_version !== "PythonEntityNativeProof/v1"
      || native.authority_effect !== "none"
      || target.target_id !== binding.target_id
      || target.target_sha256 !== binding.source_ref.sha256
      || target.language !== "python" || target.protocol_id !== binding.protocol_id
      || nativeBinding.binding_id !== binding.binding_id
      || nativeBinding.binding_sha256 !== binding.binding_sha256
      || runtime.schema_version !== "PythonEntityRuntimeObservation/v1"
      || runtime.authority_effect !== "none"
      || runtime.direct_constructor_inaccessible !== true
      || runtime.raw_constructor_helper_exposed !== false
      || !same(runtime.rejected_route_ids,
        ["language-visible-direct-constructor", "undeclared-route"])
      || runtime.per_call_validator_supplied !== false
      || sourceProof.source_sha256 !== binding.source_ref.sha256
      || sourceProof.mechanism
        !== "hash-locked-source-ast-bytecode-plus-runtime-observation"
      || toolchain.python_version !== binding.python_version
      || toolchain.executable_path !== binding.python_executable_path
      || toolchain.executable_sha256 !== binding.python_executable_sha256
      || process.executions !== 2 || process.distinct_pids !== 2
      || process.pids_redacted_from_semantic_proof !== true
      || process.semantic_replay_equal !== true
      || process.input_materialization !== "json-inert-owner-cases"
      || sha(process.semantic_replay_sha256,
        "PY_ENTITY_NATIVE_PROCESS_INVALID")
        !== sha256(canonicalConstructionObservationJson(runtime))
      || sourceAccounting.declared !== 11 || sourceAccounting.rejected !== 11
      || !same(sourceControls.map(({control_id}) => control_id), SOURCE_CONTROL_IDS)
      || typeof native.claim_ceiling !== "string") {
    return fail("PY_ENTITY_NATIVE_PROOF_INVALID");
  }
  const observer: LockedConstructionObserverRefV1 = Object.freeze({
    role: "independent-construction-observer",
    observer_id: binding.observer_id,
    observer_sha256: binding.observer_ref.sha256,
    owner_ref: binding.observer_owner_ref,
    provider_id: "python-entity-v1",
    provider_sha256: binding.provider_ref.sha256,
  });
  const nativeSnapshots = array(runtime.snapshots,
    "PY_ENTITY_NATIVE_SNAPSHOTS_INVALID").map((item) =>
    object(item, "PY_ENTITY_NATIVE_SNAPSHOT_INVALID"));
  if (nativeSnapshots.length !== definition.snapshots.length) {
    return fail("PY_ENTITY_NATIVE_SNAPSHOT_LEDGER_MISMATCH");
  }
  const snapshots = definition.snapshots.map((expected, index) => {
    const observed = nativeSnapshots[index]!;
    const identity = array(observed.identity, "PY_ENTITY_NATIVE_IDENTITY_INVALID")
      .map((item) => object(item, "PY_ENTITY_NATIVE_IDENTITY_INVALID"));
    const expectedIdentity = definition.identity_components.map((component) => ({
      ...component,
      normalized_value_sha256: expected.identity_values[component.component_name],
    }));
    if (observed.snapshot_id !== expected.snapshot_id
        || observed.entity_case_id !== expected.entity_case_id
        || observed.sequence !== expected.sequence
        || observed.route_id !== expected.route_id
        || observed.predecessor_snapshot_id !== expected.predecessor_snapshot_id
        || observed.state_sha256 !== expected.state_sha256
        || observed.frozen !== true || observed.mutation_observed !== false
        || !same(identity, expectedIdentity)
        || !/^-?[0-9]+$/u.test(string(observed.hash,
          "PY_ENTITY_NATIVE_HASH_INVALID"))) {
      return fail("PY_ENTITY_NATIVE_SNAPSHOT_INVALID", expected.snapshot_id);
    }
    return Object.freeze({
      snapshot_id: expected.snapshot_id,
      entity_case_id: expected.entity_case_id,
      sequence: expected.sequence,
      route_id: expected.route_id,
      predecessor_snapshot_id: expected.predecessor_snapshot_id,
      identity: expectedIdentity,
      state_sha256: expected.state_sha256,
      frozen: true,
      mutation_observed: false,
    });
  });
  const nativeProbes = array(runtime.equality_probes,
    "PY_ENTITY_NATIVE_EQUALITY_INVALID").map((item) =>
    object(item, "PY_ENTITY_NATIVE_EQUALITY_INVALID"));
  const equalityProbes = definition.equality_probes.map((expected, index) => {
    const observed = nativeProbes[index]!;
    const leftHash = string(observed.left_hash, "PY_ENTITY_NATIVE_HASH_INVALID");
    const rightHash = string(observed.right_hash, "PY_ENTITY_NATIVE_HASH_INVALID");
    if (observed.probe_id !== expected.probe_id
        || observed.left_snapshot_id !== expected.left_snapshot_id
        || observed.right_snapshot_id !== expected.right_snapshot_id
        || observed.relation !== expected.relation
        || observed.comparison_basis !== "canonical-identity-only"
        || observed.references_distinct !== true
        || observed.observed_equal !== expected.expected_equal
        || !/^-?[0-9]+$/u.test(leftHash) || !/^-?[0-9]+$/u.test(rightHash)
        || (expected.expected_equal && leftHash !== rightHash)) {
      return fail("PY_ENTITY_NATIVE_EQUALITY_INVALID", expected.probe_id);
    }
    return Object.freeze({
      probe_id: expected.probe_id,
      left_snapshot_id: expected.left_snapshot_id,
      right_snapshot_id: expected.right_snapshot_id,
      relation: expected.relation,
      comparison_basis: "canonical-identity-only" as const,
      observed_equal: expected.expected_equal,
      left_hash_sha256: sha256(leftHash),
      right_hash_sha256: sha256(rightHash),
    });
  });
  const routeTraces = array(runtime.route_traces,
    "PY_ENTITY_NATIVE_ROUTES_INVALID") as unknown as
    EntityLifecycleConstructionObservationV1["route_traces"];
  const failure = object(runtime.validation_failure_probe,
    "PY_ENTITY_NATIVE_FAILURE_INVALID") as unknown as
    EntityLifecycleConstructionObservationV1["validation_failure_probe"];
  const extension = object(runtime.extension,
    "PY_ENTITY_NATIVE_EXTENSION_INVALID") as unknown as
    EntityLifecycleConstructionObservationV1["extension"];
  const observation = mintEntityLifecycleConstructionObservationV1({
    schema_version: "EntityLifecycleConstructionObservation/v1",
    observation_id: "observation.entity.python.settlement/v1",
    source_kind: "target-observation",
    observer_ref: observer,
    definition_ref: denominator.owner_definition_ref,
    factory_ref: definition.factories.base,
    route_traces: routeTraces,
    validation_failure_probe: failure,
    snapshots,
    equality_probes: equalityProbes,
    extension,
    per_call_validator_supplied: false,
    claim: "transport-observation-only-no-native-runtime-claim",
    collision_freedom_claim: false,
    authority_effect: "none",
  });
  const family = evaluateIdentityLifecycle({definition, denominator, observation,
    locked_observer_ref: observer});
  if (family.verdict !== "pass") return fail("PY_ENTITY_FAMILY_BLOCKED",
    family.findings.map(({code}) => code).join(","));
  const familyControls = catalogue.mutations.map((mutation) => {
    const result = evaluateIdentityLifecycle({definition, denominator,
      observation: applyIdentityLifecycleMutant(observation, mutation),
      locked_observer_ref: observer});
    const codes = new Set(result.findings.map(({code}) => code));
    if (result.verdict !== "fail"
        || !mutation.expected_finding_codes.every((code) =>
          codes.has(code as IdentityLifecycleFindingCode))) {
      return fail("PY_ENTITY_FAMILY_CONTROL_SURVIVED", mutation.mutation_id);
    }
    return Object.freeze({mutation_id: mutation.mutation_id,
      status: "killed" as const});
  });
  return Object.freeze({
    schema_version: "PythonEntityProof/v1" as const,
    result: "pass" as const,
    target: Object.freeze({target_id: binding.target_id,
      target_sha256: binding.source_ref.sha256, language: "python" as const,
      protocol_id: binding.protocol_id}),
    binding: Object.freeze({binding_id: binding.binding_id,
      binding_sha256: binding.binding_sha256}),
    native_runtime_observation: runtime,
    observation,
    family_evaluation: family,
    process_evidence: process,
    toolchain: Object.freeze({python_version: binding.python_version,
      executable_path: binding.python_executable_path,
      executable_sha256: binding.python_executable_sha256}),
    accounting: Object.freeze({
      positives: Object.freeze({declared: 5, passed: 5}),
      construction_routes: Object.freeze({declared: 4, passed: 4}),
      target_source_controls: Object.freeze({declared: 11, rejected: 11}),
      predecessor_family_controls: Object.freeze({declared: familyControls.length,
        killed: familyControls.length}),
    }),
    target_source_controls: Object.freeze(sourceControls),
    predecessor_family_controls: Object.freeze(familyControls),
    claim_ceiling: native.claim_ceiling as string,
    authority_effect: "none" as const,
  });
};
