import {execFile} from "node:child_process";
import {createHash} from "node:crypto";
import {promisify} from "node:util";
import ts from "typescript";

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
  type LockedConstructionObserverRefV1,
} from "../../../../kernel/evidence/construction-observation/index.js";
import {inspectTypeScriptEntityClosedSubset} from "./closed-subset.js";

type JsonObject = Record<string, unknown>;
type ExactRef = Readonly<{path: string; sha256: string}>;

export const TYPESCRIPT_ENTITY_RAW_PATHS = Object.freeze({
  definition: "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/fixtures/settlement-entity/definition.json",
  denominator: "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/fixtures/settlement-entity/denominator.json",
  mutations: "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/fixtures/settlement-entity/mutants.json",
  descriptor: "projects/domainspec-v2/development/remaining-meta-types/admissions/entity/cross-language-realization-descriptor.json",
  source: "projects/domainspec-v2/impl/architecture-conformance/targets/typescript/entity-v1.ts",
  observer: "projects/domainspec-v2/impl/architecture-conformance/realizations/entity/typescript/identity-lifecycle-v1/closed-subset.ts",
  proof_builder: "projects/domainspec-v2/impl/architecture-conformance/realizations/entity/typescript/identity-lifecycle-v1/index.ts",
  provider: "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/typescript-entity-v1.ts",
  family_api: "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/index.ts",
  family_evaluator: "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/evaluator/evaluate-identity-lifecycle.ts",
  kernel_api: "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/construction-observation/index.ts",
  kernel_evaluator: "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/construction-observation/entity-lifecycle-construction-observation.ts",
  typescript_compiler: "projects/domainspec-v2/impl/node_modules/typescript/lib/typescript.js",
  binding: "projects/domainspec-v2/impl/architecture-conformance/realizations/entity/typescript/identity-lifecycle-v1/typescript-binding.json",
});
export type TypeScriptEntityRawInputs = Readonly<Record<
keyof typeof TYPESCRIPT_ENTITY_RAW_PATHS, string>>;

type Binding = Readonly<{
  schema_version: "TypeScriptEntityBinding/v1";
  binding_id: string;
  target_id: string;
  protocol_id: "typescript.validated-extensible-entity-factory/v1";
  definition_ref: ExactRef;
  denominator_ref: ExactRef;
  mutation_catalogue_ref: ExactRef;
  descriptor_ref: ExactRef;
  source_ref: ExactRef;
  observer_ref: ExactRef;
  proof_builder_ref: ExactRef;
  provider_ref: ExactRef;
  family_api_ref: ExactRef;
  family_evaluator_ref: ExactRef;
  kernel_api_ref: ExactRef;
  kernel_evaluator_ref: ExactRef;
  typescript_compiler_ref: ExactRef;
  typescript_version: "5.9.3";
  observer_id: string;
  observer_owner_ref: string;
  proof_mechanism: string;
  authority_effect: "none";
  binding_sha256: string;
}>;

const executeFile = promisify(execFile);
const sha256 = (value: string): string => createHash("sha256")
  .update(value, "utf8").digest("hex");
const fail = (code: string, detail?: string): never => {
  throw Object.assign(new Error(detail ? `${code}:${detail}` : code), {code});
};
const isObject = (value: unknown): value is JsonObject => value !== null
  && typeof value === "object" && !Array.isArray(value);
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const exactKeys = (value: JsonObject, expected: readonly string[], code: string): void => {
  if (JSON.stringify(Object.keys(value).sort(compareUtf8))
      !== JSON.stringify([...expected].sort(compareUtf8))) return fail(code);
};
const parse = (bytes: string, code: string): JsonObject => {
  try {
    const value: unknown = JSON.parse(bytes);
    return isObject(value) ? value : fail(code);
  } catch (error) {
    if (isObject(error) && error.code === code) throw error;
    return fail(code);
  }
};
const same = (left: unknown, right: unknown): boolean =>
  canonicalConstructionObservationJson(left)
    === canonicalConstructionObservationJson(right);

const snapshotRaw = (raw: TypeScriptEntityRawInputs):
TypeScriptEntityRawInputs => Object.freeze(Object.fromEntries(
  Object.keys(TYPESCRIPT_ENTITY_RAW_PATHS).map((role) => {
    const value = raw[role as keyof TypeScriptEntityRawInputs];
    if (typeof value !== "string") return fail("TS_ENTITY_RAW_INPUT_MISSING", role);
    return [role, `${value}`];
  }),
)) as TypeScriptEntityRawInputs;

const decodeBinding = (bytes: string, raw: TypeScriptEntityRawInputs): Binding => {
  const value = parse(bytes, "TS_ENTITY_BINDING_JSON_INVALID");
  exactKeys(value, ["schema_version", "binding_id", "target_id", "protocol_id",
    "definition_ref", "denominator_ref", "mutation_catalogue_ref",
    "descriptor_ref", "source_ref", "observer_ref", "proof_builder_ref",
    "provider_ref", "family_api_ref", "family_evaluator_ref", "kernel_api_ref",
    "kernel_evaluator_ref", "typescript_compiler_ref", "typescript_version",
    "observer_id", "observer_owner_ref", "proof_mechanism", "authority_effect",
    "binding_sha256"], "TS_ENTITY_BINDING_SHAPE_INVALID");
  const roles = Object.freeze({
    definition_ref: "definition", denominator_ref: "denominator",
    mutation_catalogue_ref: "mutations", descriptor_ref: "descriptor",
    source_ref: "source", observer_ref: "observer",
    proof_builder_ref: "proof_builder", provider_ref: "provider",
    family_api_ref: "family_api", family_evaluator_ref: "family_evaluator",
    kernel_api_ref: "kernel_api", kernel_evaluator_ref: "kernel_evaluator",
    typescript_compiler_ref: "typescript_compiler",
  } as const);
  if (value.schema_version !== "TypeScriptEntityBinding/v1"
      || value.binding_id !== "typescript.settlement-entity.identity-lifecycle/v1"
      || value.target_id !== "entity.typescript.settlement/v1"
      || value.protocol_id !== "typescript.validated-extensible-entity-factory/v1"
      || value.typescript_version !== ts.version
      || value.observer_id !== "observer.typescript-entity-closed-subset/v1"
      || value.observer_owner_ref !== "typescript-entity-proof-harness"
      || value.proof_mechanism
        !== "exact-source-static-binding-plus-two-fresh-process-runtime-observation"
      || value.authority_effect !== "none" || typeof value.binding_sha256 !== "string") {
    return fail("TS_ENTITY_BINDING_POLICY_INVALID");
  }
  for (const [refName, role] of Object.entries(roles)) {
    const ref = value[refName];
    const path = TYPESCRIPT_ENTITY_RAW_PATHS[
      role as keyof typeof TYPESCRIPT_ENTITY_RAW_PATHS];
    if (!isObject(ref)) return fail("TS_ENTITY_BINDING_REF_INVALID", role);
    exactKeys(ref, ["path", "sha256"], "TS_ENTITY_BINDING_REF_INVALID");
    if (ref.path !== path || typeof ref.sha256 !== "string"
        || !/^[a-f0-9]{64}$/u.test(ref.sha256)
        || ref.sha256 !== sha256(raw[role as keyof TypeScriptEntityRawInputs])) {
      return fail("TS_ENTITY_BINDING_INPUT_STALE", role);
    }
  }
  const {binding_sha256: digest, ...body} = value;
  if (digest !== sha256(canonicalConstructionObservationJson(body))) {
    return fail("TS_ENTITY_BINDING_DIGEST_STALE");
  }
  return value as Binding;
};

const CHILD_SCRIPT = `
const source = Buffer.from(process.env.DS_ENTITY_SOURCE ?? "", "base64").toString("utf8");
const payload = JSON.parse(Buffer.from(process.env.DS_ENTITY_CASES ?? "", "base64").toString("utf8"));
const target = await import("data:text/javascript;base64," + Buffer.from(source).toString("base64"));
const baseFactory = target.createSettlementEntityFactory("base");
const factory = baseFactory.extendWithDuplicateBlocked();
if (!factory || factory.extendWithDuplicateBlocked !== null) process.exit(41);
if (baseFactory.directConstructor !== null || factory.directConstructor !== null) process.exit(42);
const validators = value => value.validators.map(item => ({...item}));
const baseValidators = validators(baseFactory);
const extensionValidators = validators(factory);
const toInput = snapshot => ({entity_case_id: snapshot.entity_case_id,
  snapshot_id: snapshot.snapshot_id, sequence: snapshot.sequence,
  predecessor_snapshot_id: snapshot.predecessor_snapshot_id,
  organization_id: {...payload.identity_components[0],
    normalized_value_sha256: snapshot.identity_values.organization_id},
  settlement_id: {...payload.identity_components[1],
    normalized_value_sha256: snapshot.identity_values.settlement_id},
  owner_id: snapshot.identity_values.organization_id,
  amount_minor_units: 100, duplicate: false, state_sha256: snapshot.state_sha256});
const ownerById = new Map(payload.snapshots.map(item => [item.snapshot_id, item]));
const createdOwner = ownerById.get("snapshot.settlement-a.created");
const reconstructedOwner = ownerById.get("snapshot.settlement-a.reconstructed");
const completedOwner = ownerById.get("snapshot.settlement-a.completed");
const distinctOwner = ownerById.get("snapshot.settlement-b.created");
if (!createdOwner || !reconstructedOwner || !completedOwner || !distinctOwner) process.exit(43);
const created = factory.create(toInput(createdOwner));
const reconstructed = factory.reconstruct(toInput(reconstructedOwner));
const distinct = factory.create(toInput(distinctOwner));
if (!created.ok || !reconstructed.ok || !distinct.ok) process.exit(44);
const transitioned = factory.transition(created.value, {
  snapshot_id: completedOwner.snapshot_id, state_sha256: completedOwner.state_sha256,
  amount_minor_units: 100, duplicate: false});
if (!transitioned.ok) process.exit(45);
const formed = [created, reconstructed, transitioned, distinct];
const outputs = formed.map((result, index) => {
  const value = result.value;
  const before = value.state_sha256;
  try { value.state_sha256 = "0".repeat(64); } catch {}
  return {route_id: result.trace.route_id, trace: result.trace,
    snapshot: {snapshot_id: value.snapshot_id, entity_case_id: value.entity_case_id,
      sequence: value.sequence, predecessor_snapshot_id: value.predecessor_snapshot_id,
      route_id: result.trace.route_id,
      identity: value.identity, state_sha256: value.state_sha256,
      frozen: Object.isFrozen(value) && Object.isFrozen(value.identity)
        && value.identity.every(Object.isFrozen),
      mutation_observed: value.state_sha256 !== before},
    hash: value.hash(), index};
});
const invalidInput = {...toInput(createdOwner), amount_minor_units: 0};
const invalid = factory.create(invalidInput);
const equality = [
  {probe_id: "probe.settlement.same-identity-different-state/v1",
    left_snapshot_id: created.value.snapshot_id,
    right_snapshot_id: transitioned.value.snapshot_id,
    relation: "same-identity-different-state", observed_equal: created.value.equals(transitioned.value),
    left_hash: created.value.hash(), right_hash: transitioned.value.hash()},
  {probe_id: "probe.settlement.distinct-identity/v1",
    left_snapshot_id: created.value.snapshot_id, right_snapshot_id: distinct.value.snapshot_id,
    relation: "distinct-identity", observed_equal: created.value.equals(distinct.value),
    left_hash: created.value.hash(), right_hash: distinct.value.hash()},
];
process.stdout.write(JSON.stringify({pid: process.pid, outputs, equality,
  invalid: {ok: invalid.ok, value_is_null: invalid.value === null,
    failure_codes: invalid.failure_codes, trace: invalid.trace},
  extension: {base_factory_ref: baseFactory.factory_ref,
    extension_factory_ref: factory.factory_ref, base_validators: baseValidators,
    extension_validators: extensionValidators,
    base_preserved: JSON.stringify(extensionValidators.slice(0, baseValidators.length))
      === JSON.stringify(baseValidators),
    added_validators: extensionValidators.slice(baseValidators.length),
    identity_resolver_preserved:
      JSON.stringify(baseFactory.identity_resolver_ref)
      === JSON.stringify(factory.identity_resolver_ref), terminal: true},
  direct_constructor: {base_null: baseFactory.directConstructor === null,
    extension_null: factory.directConstructor === null}}));
`;

const compile = (source: string): string => {
  const result = ts.transpileModule(source, {compilerOptions: {
    target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022,
    strict: true, isolatedModules: true,
  }, fileName: "entity-v1.ts", reportDiagnostics: true});
  if ((result.diagnostics ?? []).some((item) =>
    item.category === ts.DiagnosticCategory.Error)) return fail("TS_ENTITY_COMPILE_FAILED");
  return result.outputText;
};

const run = async (source: string, cases: unknown): Promise<JsonObject> => {
  const {stdout, stderr} = await executeFile(process.execPath,
    ["--input-type=module", "--eval", CHILD_SCRIPT], {env: {
      DS_ENTITY_SOURCE: Buffer.from(source, "utf8").toString("base64"),
      DS_ENTITY_CASES: Buffer.from(JSON.stringify(cases), "utf8").toString("base64"),
    }, timeout: 10_000, maxBuffer: 1_048_576});
  if (stderr.length > 0) return fail("TS_ENTITY_CHILD_STDERR");
  return parse(stdout, "TS_ENTITY_CHILD_OUTPUT_INVALID");
};

const SOURCE_CONTROLS = Object.freeze([
  ["validator-loop-bypass", (source: string) => source.replace(
    "for (const validator of validators)", "for (const validator of [])")],
  ["base-validator-removal", (source: string) => source.replace(
    "ownerMatchesValidator,\n  amountValidValidator", "amountValidValidator")],
  ["identity-resolver-replacement", (source: string) => source.replace(
    "const identity = resolveIdentity(input)",
    "const identity = resolveIdentity({...input, settlement_id: input.organization_id})")],
  ["extension-cycle", (source: string) => source.replace(
    "? () => createSettlementEntityFactory(\"with-duplicate-blocked\") : null",
    "? () => createSettlementEntityFactory(\"with-duplicate-blocked\") : () => createSettlementEntityFactory(\"base\")")],
  ["invalid-snapshot", (source: string) => source.replace(
    "value: null,\n        failure_codes: Object.freeze([failure])",
    "value: formSnapshot(input, resolveIdentity(input)),\n        failure_codes: Object.freeze([failure])")],
  ["freeze-removal", (source: string) => source.replace(
    "return Object.freeze({\n    entity_case_id: input.entity_case_id",
    "return ({\n    entity_case_id: input.entity_case_id")],
  ["complete-field-equality", (source: string) => source.replace(
    "key === identityKey(other.identity)",
    "key === identityKey(other.identity) && input.state_sha256 === other.state_sha256")],
  ["stateful-hash", (source: string) => source.replace(
    "hash: (): string => key", "hash: (): string => key + input.state_sha256")],
  ["reconstruction-bypass", (source: string) => source.replace(
    "executeRoute(\"deserialization-reconstruction\", validators, input)",
    "executeRoute(\"deserialization-reconstruction\", [], input)")],
  ["transition-identity-replacement", (source: string) => source.replace(
    "organization_id: previous.identity[0]",
    "organization_id: {...previous.identity[0], normalized_value_sha256: next.state_sha256}")],
] as const);

const childSemantic = (value: JsonObject): unknown => {
  const {pid: _pid, ...body} = value;
  return body;
};

const validateChild = (value: JsonObject): void => {
  const outputs = Array.isArray(value.outputs) ? value.outputs : fail("TS_ENTITY_CHILD_SHAPE");
  if (outputs.length !== 4 || !isObject(value.direct_constructor)
      || value.direct_constructor.base_null !== true
      || value.direct_constructor.extension_null !== true
      || !isObject(value.invalid) || value.invalid.ok !== false
      || value.invalid.value_is_null !== true
      || !same(value.invalid.failure_codes, ["AMOUNT_INVALID"])
      || !isObject(value.extension) || value.extension.base_preserved !== true
      || value.extension.identity_resolver_preserved !== true
      || value.extension.terminal !== true) return fail("TS_ENTITY_CHILD_BEHAVIOR_MISMATCH");
  const routes = outputs.map((entry) => isObject(entry) ? entry.route_id : null);
  if (!same(routes, ["factory", "deserialization-reconstruction",
    "lifecycle-transition", "factory"])) return fail("TS_ENTITY_ROUTE_BEHAVIOR_MISMATCH");
  for (const entry of outputs) {
    if (!isObject(entry) || !isObject(entry.snapshot)
        || entry.snapshot.frozen !== true || entry.snapshot.mutation_observed !== false) {
      return fail("TS_ENTITY_IMMUTABILITY_BEHAVIOR_MISMATCH");
    }
  }
  const probes = Array.isArray(value.equality) ? value.equality : [];
  if (probes.length !== 2 || !isObject(probes[0]) || !isObject(probes[1])
      || probes[0].observed_equal !== true
      || probes[0].left_hash !== probes[0].right_hash
      || probes[1].observed_equal !== false) {
    return fail("TS_ENTITY_IDENTITY_BEHAVIOR_MISMATCH");
  }
};

export const buildTypeScriptEntityProof = async (
  incoming: TypeScriptEntityRawInputs,
) => {
  const raw = snapshotRaw(incoming);
  const binding = decodeBinding(raw.binding, raw);
  const definition = decodeIdentityLifecycleDefinitionV1(raw.definition,
    TYPESCRIPT_ENTITY_RAW_PATHS.descriptor, raw.descriptor);
  const denominator = decodeIdentityLifecycleDenominatorV1(raw.denominator,
    raw.definition, definition, TYPESCRIPT_ENTITY_RAW_PATHS.definition);
  const catalogue = decodeIdentityLifecycleMutationCatalogueV1(raw.mutations,
    denominator);
  const subset = inspectTypeScriptEntityClosedSubset(raw.source);
  if (subset.source_sha256 !== binding.source_ref.sha256) {
    return fail("TS_ENTITY_SOURCE_BINDING_STALE");
  }
  const compiled = compile(raw.source);
  const ownerCases = Object.freeze({identity_components: definition.identity_components,
    snapshots: definition.snapshots});
  const [first, second] = await Promise.all([
    run(compiled, ownerCases), run(compiled, ownerCases),
  ]);
  validateChild(first);
  validateChild(second);
  if (first.pid === second.pid || !same(childSemantic(first), childSemantic(second))) {
    return fail("TS_ENTITY_PROCESS_REPLAY_MISMATCH");
  }
  const outputs = first.outputs as JsonObject[];
  const outputBySnapshot = new Map(outputs.map((entry) => {
    const snapshot = entry.snapshot as JsonObject;
    return [String(snapshot.snapshot_id), entry];
  }));
  const traceFor = (snapshotId: string) => {
    const entry = outputBySnapshot.get(snapshotId) ?? fail("TS_ENTITY_SNAPSHOT_MISSING");
    return entry.trace as JsonObject;
  };
  const observer: LockedConstructionObserverRefV1 = Object.freeze({
    role: "independent-construction-observer" as const,
    observer_id: binding.observer_id,
    observer_sha256: binding.observer_ref.sha256,
    owner_ref: binding.observer_owner_ref,
    provider_id: "typescript-entity-v1",
    provider_sha256: binding.provider_ref.sha256,
  });
  const routeTraces = definition.construction_routes.map((routeId) => {
    if (routeId === "language-visible-direct-constructor") return {
      route_id: routeId, input_class: "valid" as const,
      normalization_ordinal: null, validator_trace: [],
      identity_resolution_ordinal: null, construction_ordinal: null,
      immutability_ordinal: null, direct_constructor_policy: "private-inaccessible" as const,
      result: {status: "constructor-inaccessible" as const,
        snapshot_created: false, snapshot_id: null},
    };
    const owner = definition.snapshots.find(({route_id: ownerRoute}) =>
      ownerRoute === routeId) ?? fail("TS_ENTITY_ROUTE_OWNER_MISSING", routeId);
    const trace = traceFor(owner.snapshot_id);
    return {...trace, input_class: "valid" as const,
      direct_constructor_policy: "not-applicable" as const,
      result: {status: "formed" as const, snapshot_created: true,
        snapshot_id: owner.snapshot_id}};
  });
  const snapshots = definition.snapshots.map((owner) => {
    const entry = outputBySnapshot.get(owner.snapshot_id)
      ?? fail("TS_ENTITY_SNAPSHOT_MISSING", owner.snapshot_id);
    const snapshot = entry.snapshot as JsonObject;
    const expectedKeys = ["snapshot_id", "entity_case_id", "sequence", "route_id",
      "predecessor_snapshot_id", "identity", "state_sha256", "frozen",
      "mutation_observed"];
    if (JSON.stringify(Object.keys(snapshot).sort(compareUtf8))
        !== JSON.stringify(expectedKeys.sort(compareUtf8))) {
      return fail("TS_ENTITY_SNAPSHOT_SHAPE", Object.keys(snapshot).join(","));
    }
    return snapshot as never;
  });
  const probes = (first.equality as JsonObject[]).map((probe) => ({
    probe_id: String(probe.probe_id),
    left_snapshot_id: String(probe.left_snapshot_id),
    right_snapshot_id: String(probe.right_snapshot_id),
    relation: probe.relation as "same-identity-different-state" | "distinct-identity",
    comparison_basis: "canonical-identity-only" as const,
    observed_equal: probe.observed_equal === true,
    left_hash_sha256: sha256(String(probe.left_hash)),
    right_hash_sha256: sha256(String(probe.right_hash)),
  }));
  const invalid = first.invalid as JsonObject;
  const invalidTrace = invalid.trace as JsonObject;
  const extension = first.extension as JsonObject;
  const observation = mintEntityLifecycleConstructionObservationV1({
    schema_version: "EntityLifecycleConstructionObservation/v1",
    observation_id: "observation.entity.typescript.settlement/v1",
    source_kind: "target-observation", observer_ref: observer,
    definition_ref: denominator.owner_definition_ref,
    factory_ref: definition.factories.base,
    route_traces: routeTraces as never,
    validation_failure_probe: {
      probe_id: definition.validation_failure.probe_id, route_id: "factory",
      validator_trace: invalidTrace.validator_trace as never,
      identity_resolution_ordinal: null, construction_ordinal: null,
      result: {status: "validation-failure", snapshot_created: false,
        failure_codes: invalid.failure_codes as string[]},
    },
    snapshots, equality_probes: probes,
    extension: {
      base_factory_ref: extension.base_factory_ref as never,
      extension_factory_ref: extension.extension_factory_ref as never,
      base_validators_preserved: extension.base_preserved === true,
      added_validators: extension.added_validators as never,
      identity_resolver_preserved: extension.identity_resolver_preserved === true,
      altered_facets: [], cycle_detected: extension.terminal !== true,
    },
    per_call_validator_supplied: false,
    claim: "transport-observation-only-no-native-runtime-claim",
    collision_freedom_claim: false, authority_effect: "none",
  });
  const family = evaluateIdentityLifecycle({definition, denominator, observation,
    locked_observer_ref: observer});
  if (family.verdict !== "pass") return fail("TS_ENTITY_FAMILY_BLOCKED",
    family.findings.map(({code}) => code).join(","));
  const familyControls = catalogue.mutations.map((mutation) => {
    const result = evaluateIdentityLifecycle({definition, denominator,
      observation: applyIdentityLifecycleMutant(observation, mutation),
      locked_observer_ref: observer});
    const found = new Set(result.findings.map(({code}) => code));
    if (result.verdict !== "fail" || !mutation.expected_finding_codes.every((code) =>
      found.has(code as IdentityLifecycleFindingCode))) {
      return fail("TS_ENTITY_FAMILY_CONTROL_SURVIVED", mutation.mutation_id);
    }
    return Object.freeze({mutation_id: mutation.mutation_id, status: "killed" as const});
  });
  const sourceControls = SOURCE_CONTROLS.map(([controlId, mutate]) => {
    const mutated = mutate(raw.source);
    if (mutated === raw.source) return fail("TS_ENTITY_SOURCE_CONTROL_NOOP", controlId);
    try { inspectTypeScriptEntityClosedSubset(mutated); }
    catch { return Object.freeze({control_id: controlId,
      evidence_kind: "target-source-control" as const,
      status: "rejected" as const}); }
    return fail("TS_ENTITY_SOURCE_CONTROL_SURVIVED", controlId);
  });
  return Object.freeze({
    schema_version: "TypeScriptEntityProof/v1" as const,
    result: "pass" as const,
    target: Object.freeze({target_id: binding.target_id,
      target_sha256: binding.source_ref.sha256, language: "typescript" as const,
      protocol_id: binding.protocol_id}),
    binding: Object.freeze({binding_id: binding.binding_id,
      binding_sha256: binding.binding_sha256}),
    observation, family_evaluation: family, closed_subset: subset,
    toolchain: Object.freeze({typescript_version: binding.typescript_version,
      compiler_path: binding.typescript_compiler_ref.path,
      compiler_sha256: binding.typescript_compiler_ref.sha256}),
    process_evidence: Object.freeze({executions: 2, distinct_pids: 2,
      semantic_replay_sha256: sha256(canonicalConstructionObservationJson(
        childSemantic(first))), input_materialization: "json-inert-owner-cases" as const,
      process_ids_excluded_from_semantic_digest: true}),
    accounting: Object.freeze({positives: Object.freeze({declared: 5, passed: 5}),
      construction_routes: Object.freeze({declared: 4, observed: 4}),
      source_controls: Object.freeze({declared: sourceControls.length,
        rejected: sourceControls.length}),
      predecessor_family_controls: Object.freeze({declared: familyControls.length,
        killed: familyControls.length})}),
    source_controls: Object.freeze(sourceControls),
    predecessor_family_controls: Object.freeze(familyControls),
    claim_ceiling: "one exact hash-locked candidate-local TypeScript Settlement Entity over inert owner JSON inputs and two fresh child processes, exact typed composite identity, immutable lifecycle snapshots, identity-only equality and congruent hash, owner-bound base-before-extension validation, structured no-snapshot failure, factory reconstruction transition and inaccessible direct-constructor routes, additive acyclic base-and-identity-preserving extension, 10 target source controls, and independent 5/5 7/7 4/4 family evaluation; no arbitrary TypeScript, getters, Proxy, OS interception, collision freedom, cross-language hash bytes, parity, registration, promotion, publication, deployment, or production claim",
    authority_effect: "none" as const,
  });
};
