import {execFile} from "node:child_process";
import {createHash} from "node:crypto";
import {promisify} from "node:util";
import ts from "typescript";

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
import {inspectTypeScriptValueObjectClosedSubset} from "./closed-subset.js";

type JsonObject = Record<string, unknown>;
type ExactRef = Readonly<{path: string; sha256: string}>;

export const TYPESCRIPT_VALUE_OBJECT_RAW_PATHS = Object.freeze({
  definition: "projects/domainspec-v2/impl/architecture-conformance/families/complete-value/fixtures/settlement-value/definition.json",
  denominator: "projects/domainspec-v2/impl/architecture-conformance/families/complete-value/fixtures/settlement-value/denominator.json",
  mutations: "projects/domainspec-v2/impl/architecture-conformance/families/complete-value/fixtures/settlement-value/mutants.json",
  descriptor: "projects/domainspec-v2/development/remaining-meta-types/admissions/value-object/cross-language-realization-descriptor.json",
  source: "projects/domainspec-v2/impl/architecture-conformance/targets/typescript/value-object-v1.ts",
  observer: "projects/domainspec-v2/impl/architecture-conformance/realizations/value-object/typescript/complete-value-v1/closed-subset.ts",
  proof_builder: "projects/domainspec-v2/impl/architecture-conformance/realizations/value-object/typescript/complete-value-v1/index.ts",
  provider: "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/typescript-value-object-v1.ts",
  family_api: "projects/domainspec-v2/impl/architecture-conformance/families/complete-value/index.ts",
  kernel_api: "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/construction-observation/index.ts",
  typescript_compiler: "projects/domainspec-v2/impl/node_modules/typescript/lib/typescript.js",
  binding: "projects/domainspec-v2/impl/architecture-conformance/realizations/value-object/typescript/complete-value-v1/typescript-binding.json",
});
export type TypeScriptValueObjectRawInputs = Readonly<Record<
keyof typeof TYPESCRIPT_VALUE_OBJECT_RAW_PATHS, string>>;

type Binding = Readonly<{
  schema_version: "TypeScriptValueObjectBinding/v1";
  binding_id: string;
  target_id: string;
  protocol_id: "typescript.owned-value-object-factory/v1";
  definition_ref: ExactRef;
  denominator_ref: ExactRef;
  mutation_catalogue_ref: ExactRef;
  descriptor_ref: ExactRef;
  source_ref: ExactRef;
  observer_ref: ExactRef;
  proof_builder_ref: ExactRef;
  provider_ref: ExactRef;
  family_api_ref: ExactRef;
  kernel_api_ref: ExactRef;
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
const snapshotRaw = (raw: TypeScriptValueObjectRawInputs):
TypeScriptValueObjectRawInputs => Object.freeze(Object.fromEntries(
  Object.keys(TYPESCRIPT_VALUE_OBJECT_RAW_PATHS).map((role) => {
    const value = raw[role as keyof TypeScriptValueObjectRawInputs];
    if (typeof value !== "string") return fail("TS_VALUE_OBJECT_RAW_INPUT_MISSING", role);
    return [role, `${value}`];
  }),
)) as TypeScriptValueObjectRawInputs;
const decodeBinding = (bytes: string, raw: TypeScriptValueObjectRawInputs): Binding => {
  const value = parse(bytes, "TS_VALUE_OBJECT_BINDING_JSON_INVALID");
  exactKeys(value, ["schema_version", "binding_id", "target_id", "protocol_id",
    "definition_ref", "denominator_ref", "mutation_catalogue_ref",
    "descriptor_ref", "source_ref", "observer_ref", "proof_builder_ref",
    "provider_ref", "family_api_ref", "kernel_api_ref",
    "typescript_compiler_ref", "typescript_version", "observer_id",
    "observer_owner_ref", "proof_mechanism", "authority_effect",
    "binding_sha256"], "TS_VALUE_OBJECT_BINDING_SHAPE_INVALID");
  const roles = Object.freeze({
    definition_ref: "definition", denominator_ref: "denominator",
    mutation_catalogue_ref: "mutations", descriptor_ref: "descriptor",
    source_ref: "source", observer_ref: "observer",
    proof_builder_ref: "proof_builder", provider_ref: "provider",
    family_api_ref: "family_api", kernel_api_ref: "kernel_api",
    typescript_compiler_ref: "typescript_compiler",
  } as const);
  if (value.schema_version !== "TypeScriptValueObjectBinding/v1"
      || value.binding_id !== "typescript.settlement-value.complete-value/v1"
      || value.target_id !== "value-object.typescript.settlement-value/v1"
      || value.protocol_id !== "typescript.owned-value-object-factory/v1"
      || value.typescript_version !== ts.version
      || value.observer_id !== "observer.typescript-value-object-closed-subset/v1"
      || value.observer_owner_ref !== "typescript-value-object-proof-harness"
      || value.proof_mechanism
        !== "exact-source-static-binding-plus-two-fresh-process-runtime-observation"
      || value.authority_effect !== "none" || typeof value.binding_sha256 !== "string") {
    return fail("TS_VALUE_OBJECT_BINDING_POLICY_INVALID");
  }
  for (const [refName, role] of Object.entries(roles)) {
    const ref = value[refName];
    const path = TYPESCRIPT_VALUE_OBJECT_RAW_PATHS[
      role as keyof typeof TYPESCRIPT_VALUE_OBJECT_RAW_PATHS];
    if (!isObject(ref)) return fail("TS_VALUE_OBJECT_BINDING_REF_INVALID", role);
    exactKeys(ref, ["path", "sha256"], "TS_VALUE_OBJECT_BINDING_REF_INVALID");
    if (ref.path !== path || typeof ref.sha256 !== "string"
        || !/^[a-f0-9]{64}$/u.test(ref.sha256)
        || ref.sha256 !== sha256(raw[
          role as keyof TypeScriptValueObjectRawInputs])) {
      return fail("TS_VALUE_OBJECT_BINDING_INPUT_STALE", role);
    }
  }
  const {binding_sha256: digest, ...body} = value;
  if (digest !== sha256(canonicalConstructionObservationJson(body))) {
    return fail("TS_VALUE_OBJECT_BINDING_DIGEST_STALE");
  }
  return value as Binding;
};

const CHILD_SCRIPT = `
const source = Buffer.from(process.env.DS_VO_SOURCE ?? "", "base64").toString("utf8");
const payload = JSON.parse(Buffer.from(process.env.DS_VO_CASES ?? "", "base64").toString("utf8"));
const target = await import("data:text/javascript;base64," + Buffer.from(source).toString("base64"));
const baseFactory = target.createSettlementValueFactory("base");
const factory = baseFactory.extendWithAccountActive();
if (!factory || factory.extendWithAccountActive !== null) process.exit(41);
const validatorRefs = value => value.validators.map(({validator_id, validator_sha256, origin}) => ({validator_id, validator_sha256, origin}));
const baseValidators = validatorRefs(baseFactory);
const extensionValidators = validatorRefs(factory);
const results = [];
const formed = new Map();
for (const entry of payload.cases) {
  const owned = {account_ref: entry.case_id, active: true};
  const input = {
    currency: {...entry.components.currency},
    minor_units: {...entry.components.minor_units},
    settlement_account: {...entry.components.settlement_account, owned_value: owned},
  };
  const baseResult = baseFactory.create(input);
  const result = factory.create(input);
  const observedBindings = [
    {component_name: "currency", ...input.currency, nested_value_object: false},
    {component_name: "minor_units", ...input.minor_units, nested_value_object: false},
    {component_name: "settlement_account", protocol_id: input.settlement_account.protocol_id,
      protocol_sha256: input.settlement_account.protocol_sha256,
      normalized_value_sha256: input.settlement_account.normalized_value_sha256,
      nested_value_object: true},
  ];
  owned.account_ref = "mutated-after-formation";
  let nestedMutationObserved = false;
  if (result.ok) {
    const before = result.value.settlement_account.account_ref;
    try { result.value.settlement_account.account_ref = "direct-mutation"; } catch {}
    nestedMutationObserved = result.value.settlement_account.account_ref !== before;
    formed.set(entry.case_id, result.value);
  }
  results.push({case_id: entry.case_id, input_class: entry.input_class,
    ok: result.ok, object_created: result.value !== null,
    failure_codes: result.failure_codes,
    validator_trace: result.validator_trace,
    tuple: result.ok ? result.value.tuple : null,
    component_bindings: result.ok ? result.value.component_bindings : observedBindings,
    hash: result.ok ? result.value.hash() : null,
    frozen: result.ok ? Object.isFrozen(result.value) : false,
    nested_frozen: result.ok ? Object.isFrozen(result.value.settlement_account) : false,
    nested_alias: result.ok ? result.value.settlement_account.account_ref !== entry.case_id : false,
    nested_mutation: nestedMutationObserved,
    formation_ordinal: result.ok ? result.validator_trace.length : null,
    base_ok: baseResult.ok,
    base_tuple: baseResult.ok ? baseResult.value.tuple : null,
    base_hash: baseResult.ok ? baseResult.value.hash() : null,
    base_component_bindings: baseResult.ok ? baseResult.value.component_bindings : null,
    base_frozen: baseResult.ok ? Object.isFrozen(baseResult.value) : false,
    base_nested_frozen: baseResult.ok
      ? Object.isFrozen(baseResult.value.settlement_account) : false,
    base_equals_extended: baseResult.ok && result.ok
      ? baseResult.value.equals(result.value) : null,
    extended_equals_base: baseResult.ok && result.ok
      ? result.value.equals(baseResult.value) : null});
}
const equality_probes = payload.probes.map(probe => {
  const left = formed.get(probe.left_case_id);
  const right = formed.get(probe.right_case_id);
  if (!left || !right) process.exit(42);
  return {probe_id: probe.probe_id, left_case_id: probe.left_case_id,
    right_case_id: probe.right_case_id, relation: probe.relation,
    varied_component_name: probe.varied_component_name,
    references_distinct: left !== right,
    observed_equal: left.equals(right),
    left_hash: left.hash(), right_hash: right.hash()};
});
const nestedLeft = formed.get(payload.nested_probe.left_case_id)?.settlement_account;
const nestedRight = formed.get(payload.nested_probe.right_case_id)?.settlement_account;
const nestedVariant = formed.get(payload.nested_probe.variant_case_id)?.settlement_account;
if (!nestedLeft || !nestedRight || !nestedVariant) process.exit(43);
const nested_probe = {
  component_name: payload.nested_probe.component_name,
  protocol_id: nestedLeft.protocol_id,
  protocol_sha256: nestedLeft.protocol_sha256,
  equal_observed: nestedLeft.equals(nestedRight),
  equal_hash_congruent: nestedLeft.hash() === nestedRight.hash(),
  variant_unequal_observed: !nestedLeft.equals(nestedVariant),
  variant_hashes: [nestedLeft.hash(), nestedVariant.hash()],
};
const extension = {
  base_factory_ref: baseFactory.factory_ref,
  extension_factory_ref: factory.factory_ref,
  base_validators: baseValidators,
  extension_validators: extensionValidators,
  base_preserved: JSON.stringify(extensionValidators.slice(0, baseValidators.length)) === JSON.stringify(baseValidators),
  added_validators: extensionValidators.slice(baseValidators.length),
  tuple_and_hash_preserved: results.filter(item => item.ok).every(item =>
    JSON.stringify(item.tuple) === JSON.stringify(item.base_tuple) && item.hash === item.base_hash),
  component_bindings_and_normalization_preserved: results.filter(item => item.ok)
    .every(item => JSON.stringify(item.component_bindings)
      === JSON.stringify(item.base_component_bindings)),
  equality_preserved: results.filter(item => item.ok)
    .every(item => item.base_equals_extended && item.extended_equals_base),
  recursive_immutability_preserved: results.filter(item => item.ok)
    .every(item => item.frozen && item.nested_frozen
      && item.base_frozen && item.base_nested_frozen
      && !item.nested_alias && !item.nested_mutation),
  concept_binding_preserved:
    baseFactory.factory_ref.concept_id === factory.factory_ref.concept_id,
  extension_is_terminal: factory.extendWithAccountActive === null,
};
const extensionInput = JSON.parse(JSON.stringify(payload.cases[0]));
const extensionOwned = {account_ref: extensionInput.case_id, active: false};
const extensionTargetInput = {
  currency: extensionInput.components.currency,
  minor_units: extensionInput.components.minor_units,
  settlement_account: {...extensionInput.components.settlement_account,
    owned_value: extensionOwned},
};
const baseExtensionProbe = baseFactory.create(extensionTargetInput);
const extendedExtensionProbe = factory.create(extensionTargetInput);
extension.validation_probe = {
  base_ok: baseExtensionProbe.ok,
  extended_ok: extendedExtensionProbe.ok,
  extended_object_created: extendedExtensionProbe.value !== null,
  extended_failure_codes: extendedExtensionProbe.failure_codes,
  extended_validator_trace: extendedExtensionProbe.validator_trace,
};
process.stdout.write(JSON.stringify({pid: process.pid, results,
  equality_probes, nested_probe, extension}));
`;

const compile = (source: string): string => {
  const result = ts.transpileModule(source, {compilerOptions: {
    target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022,
    strict: true, isolatedModules: true,
  }, fileName: "value-object-v1.ts", reportDiagnostics: true});
  if ((result.diagnostics ?? []).some((item) =>
    item.category === ts.DiagnosticCategory.Error)) return fail("TS_VALUE_OBJECT_COMPILE_FAILED");
  return result.outputText;
};

const run = async (source: string, cases: unknown): Promise<JsonObject> => {
  const {stdout, stderr} = await executeFile(process.execPath,
    ["--input-type=module", "--eval", CHILD_SCRIPT], {env: {
      DS_VO_SOURCE: Buffer.from(source, "utf8").toString("base64"),
      DS_VO_CASES: Buffer.from(JSON.stringify(cases), "utf8").toString("base64"),
    }, timeout: 10_000, maxBuffer: 1_048_576});
  if (stderr.length > 0) return fail("TS_VALUE_OBJECT_CHILD_STDERR");
  return parse(stdout, "TS_VALUE_OBJECT_CHILD_OUTPUT_INVALID");
};

const SOURCE_BINDING_CONTROLS = Object.freeze([
  ["reference-identity", (source: string) => source.replace(
    "settlementAccount.equals(other.settlement_account)",
    "settlementAccount === other.settlement_account")],
  ["partial-tuple", (source: string) => source.replace(
    "&& tuple[1] === other.tuple[1]", "&& true")],
  ["mutable-nested", (source: string) => source.replace(
    "return Object.freeze({\n    protocol_id: protocolId",
    "return ({\n    protocol_id: protocolId")],
  ["alias-nested", (source: string) => source.replace(
    "account_ref: input.owned_value.account_ref", "...input.owned_value")],
  ["validator-bypass", (source: string) => source.replace("for (const validator of validators)", "for (const validator of [])")],
  ["tuple-change", (source: string) => source.replace("...baseValidators, accountValidator", "accountValidator")],
  ["protocol-bypass", (source: string) => source.replace("&& observed.protocol_sha256 === expected.protocol_sha256", "")],
  ["invalid-forms", (source: string) => source.replaceAll(
    "ok: false as const", "ok: true as const")],
] as const);

export const buildTypeScriptValueObjectProof = async (
  incoming: TypeScriptValueObjectRawInputs,
) => {
  const raw = snapshotRaw(incoming);
  const binding = decodeBinding(raw.binding, raw);
  const definition = decodeCompleteValueDefinitionV1(raw.definition,
    TYPESCRIPT_VALUE_OBJECT_RAW_PATHS.descriptor, raw.descriptor);
  const denominator = decodeCompleteValueDenominatorV1(raw.denominator,
    raw.definition, definition, TYPESCRIPT_VALUE_OBJECT_RAW_PATHS.definition);
  const catalogue = decodeCompleteValueMutationCatalogueV1(raw.mutations,
    denominator, definition);
  const subset = inspectTypeScriptValueObjectClosedSubset(raw.source);
  if (subset.source_sha256 !== binding.source_ref.sha256) {
    return fail("TS_VALUE_OBJECT_SOURCE_BINDING_STALE");
  }
  const cases = definition.cases.map((testCase) => ({
    case_id: testCase.case_id, input_class: testCase.input_class,
    components: Object.fromEntries(definition.components.map((component) => [
      component.component_name, {...component,
        normalized_value_sha256:
          testCase.normalized_component_values[component.component_name]},
    ])),
  }));
  const probes = [
    {...definition.equality_contract.equal_probe, relation: "equal-tuple" as const,
      varied_component_name: null},
    ...definition.equality_contract.component_variants.map((variant) => ({...variant,
      relation: "component-variant" as const,
      varied_component_name: variant.component_name})),
  ];
  const nestedVariant = definition.equality_contract.component_variants.find(
    (variant) => definition.components.some((component) =>
      component.nested_value_object
      && component.component_name === variant.component_name));
  if (!nestedVariant) return fail("TS_VALUE_OBJECT_NESTED_PROBE_MISSING");
  const payload = Object.freeze({cases, probes, nested_probe: Object.freeze({
    component_name: nestedVariant.component_name,
    left_case_id: definition.equality_contract.equal_probe.left_case_id,
    right_case_id: definition.equality_contract.equal_probe.right_case_id,
    variant_case_id: nestedVariant.right_case_id,
  })});
  const compiled = compile(raw.source);
  const first = await run(compiled, payload);
  const second = await run(compiled, payload);
  const semanticChild = (value: JsonObject): JsonObject => {
    const {pid: _pid, ...semantic} = value;
    return semantic;
  };
  const same = (left: unknown, right: unknown): boolean =>
    canonicalConstructionObservationJson(left)
      === canonicalConstructionObservationJson(right);
  if (first.pid === second.pid || !same(semanticChild(first), semanticChild(second))) {
    return fail("TS_VALUE_OBJECT_REPLAY_MISMATCH");
  }
  if (!Array.isArray(first.results) || first.results.length !== definition.cases.length
      || !Array.isArray(first.equality_probes)
      || !isObject(first.nested_probe) || !isObject(first.extension)) {
    return fail("TS_VALUE_OBJECT_RESULTS_INVALID");
  }
  const rows = first.results as JsonObject[];
  if (new Set(rows.map((row) => row.case_id)).size !== rows.length
      || !same(rows.map((row) => row.case_id), definition.cases.map(
        (testCase) => testCase.case_id))) {
    return fail("TS_VALUE_OBJECT_CASE_LEDGER_MISMATCH");
  }
  const rowById = new Map(rows.map((row) => [row.case_id, row]));
  const observer: LockedConstructionObserverRefV1 = Object.freeze({
    role: "independent-construction-observer", observer_id: String(binding.observer_id),
    observer_sha256: binding.observer_ref.sha256,
    owner_ref: String(binding.observer_owner_ref), provider_id: "typescript-value-object-v1",
    provider_sha256: binding.provider_ref.sha256,
  });
  const attempts = definition.cases.map((testCase) => {
    const row = rowById.get(testCase.case_id);
    if (!row || row.input_class !== testCase.input_class
        || !Array.isArray(row.validator_trace)
        || !Array.isArray(row.component_bindings)
        || !Array.isArray(row.failure_codes)) {
      return fail("TS_VALUE_OBJECT_CASE_INVALID", testCase.case_id);
    }
    const validatorTrace = row.validator_trace;
    const expectedBindings = definition.components.map((component) => ({
      ...component,
      normalized_value_sha256:
        testCase.normalized_component_values[component.component_name]!,
    }));
    if (!same(row.component_bindings, expectedBindings)) {
      return fail("TS_VALUE_OBJECT_COMPONENT_BINDING_MISMATCH", testCase.case_id);
    }
    const expectedTraceLength = testCase.input_class === "valid"
      ? definition.validators.length
      : definition.validators.findIndex(({validator_id: validatorId}) =>
        validatorId === "rule.settlement-value.nonnegative-minor-units/v1") + 1;
    const expectedTrace = definition.validators.slice(0, expectedTraceLength)
      .map(({validator_id: validatorId, validator_sha256: validatorSha256}) =>
        `${validatorId}@${validatorSha256}`);
    const expectedOk = testCase.input_class === "valid";
    const expectedTuple = expectedOk ? expectedBindings.map(
      ({normalized_value_sha256: value}) => value) : null;
    if (row.ok !== expectedOk || row.object_created !== expectedOk
        || !same(row.failure_codes, testCase.expected_failure_codes)
        || !same(validatorTrace, expectedTrace)
        || !same(row.tuple, expectedTuple)
        || row.formation_ordinal !== (expectedOk ? expectedTrace.length : null)
        || (expectedOk && (row.frozen !== true || row.nested_frozen !== true
          || row.nested_alias !== false || row.nested_mutation !== false))) {
      return fail("TS_VALUE_OBJECT_CASE_BEHAVIOR_MISMATCH", testCase.case_id);
    }
    const bindings = (row.component_bindings as JsonObject[]).map((component) => ({
      component_name: String(component.component_name),
      protocol_id: String(component.protocol_id),
      protocol_sha256: String(component.protocol_sha256),
      normalized_value_sha256: String(component.normalized_value_sha256),
      nested_value_object: component.nested_value_object === true,
    }));
    return {
      case_id: testCase.case_id, input_class: testCase.input_class,
      component_bindings: bindings,
      validator_trace: validatorTrace.map((entry, ordinal) => {
        const [validator_id, validator_sha256] = String(entry).split("@");
        const owner = definition.validators.find((item) => item.validator_id === validator_id);
        if (!owner || owner.validator_sha256 !== validator_sha256) {
          return fail("TS_VALUE_OBJECT_VALIDATOR_BINDING_MISMATCH");
        }
        return {validator_id: validator_id!, validator_sha256: validator_sha256!,
          origin: owner.origin, ordinal,
          outcome: row.ok ? "pass" as const
            : ordinal === validatorTrace.length - 1 ? "fail" as const : "pass" as const};
      }),
      formation_ordinal: row.formation_ordinal as number | null,
      result: row.ok ? {status: "formed" as const,
        object_created: row.object_created === true,
        failure_codes: row.failure_codes as string[]} : {
        status: "validation-failure" as const,
        object_created: row.object_created === true,
        failure_codes: row.failure_codes as string[]},
      normalized_tuple: row.ok ? bindings.map(({component_name,
        normalized_value_sha256}) => ({component_name, normalized_value_sha256})) : null,
      immutability: {formed_value_frozen: row.frozen === true,
        recursively_owned_components_frozen: row.nested_frozen === true,
        nested_alias_observed: row.nested_alias === true,
        nested_mutation_observed: row.nested_mutation === true},
    };
  });
  const observedProbes = first.equality_probes as JsonObject[];
  if (observedProbes.length !== probes.length
      || !same(observedProbes.map(({probe_id: probeId}) => probeId),
        probes.map(({probe_id: probeId}) => probeId))) {
    return fail("TS_VALUE_OBJECT_EQUALITY_PROBE_LEDGER_MISMATCH");
  }
  const equalityProbes = observedProbes.map((probe, index) => {
    const owner = probes[index]!;
    if (probe.left_case_id !== owner.left_case_id
        || probe.right_case_id !== owner.right_case_id
        || probe.relation !== owner.relation
        || probe.varied_component_name !== owner.varied_component_name
        || probe.references_distinct !== true
        || typeof probe.observed_equal !== "boolean"
        || typeof probe.left_hash !== "string"
        || typeof probe.right_hash !== "string") {
      return fail("TS_VALUE_OBJECT_EQUALITY_PROBE_INVALID", owner.probe_id);
    }
    return {
      probe_id: owner.probe_id,
      left_case_id: owner.left_case_id,
      right_case_id: owner.right_case_id,
      relation: owner.relation,
      varied_component_name: owner.varied_component_name,
      references_distinct: probe.references_distinct,
      observed_equal: probe.observed_equal,
      left_hash_sha256: sha256(probe.left_hash),
      right_hash_sha256: sha256(probe.right_hash),
    };
  });
  const nested = first.nested_probe;
  if (nested.component_name !== nestedVariant.component_name
      || nested.protocol_id !== definition.components.find(
        ({component_name: name}) => name === nestedVariant.component_name)?.protocol_id
      || nested.protocol_sha256 !== definition.components.find(
        ({component_name: name}) => name === nestedVariant.component_name)?.protocol_sha256
      || nested.equal_observed !== true || nested.equal_hash_congruent !== true
      || nested.variant_unequal_observed !== true || !Array.isArray(nested.variant_hashes)
      || nested.variant_hashes.length !== 2) {
    return fail("TS_VALUE_OBJECT_NESTED_PROTOCOL_BEHAVIOR_MISMATCH");
  }
  const extension = first.extension;
  const expectedBaseValidators = definition.validators.filter(
    ({origin}) => origin === "base");
  const expectedExtensionValidators = definition.validators;
  if (!same(extension.base_factory_ref, definition.factories.base)
      || !same(extension.extension_factory_ref, definition.factories.extension)
      || !same(extension.base_validators, expectedBaseValidators)
      || !same(extension.extension_validators, expectedExtensionValidators)
      || !same(extension.added_validators, definition.validators.filter(
        ({origin}) => origin === "extension"))
      || extension.base_preserved !== true
      || extension.tuple_and_hash_preserved !== true
      || extension.component_bindings_and_normalization_preserved !== true
      || extension.equality_preserved !== true
      || extension.recursive_immutability_preserved !== true
      || extension.concept_binding_preserved !== true
      || extension.extension_is_terminal !== true
      || !isObject(extension.validation_probe)
      || extension.validation_probe.base_ok !== true
      || extension.validation_probe.extended_ok !== false
      || extension.validation_probe.extended_object_created !== false
      || !same(extension.validation_probe.extended_failure_codes,
        ["INACTIVE_SETTLEMENT_ACCOUNT"])
      || !same(extension.validation_probe.extended_validator_trace,
        expectedExtensionValidators.map(({validator_id: validatorId,
          validator_sha256: validatorSha256}) => `${validatorId}@${validatorSha256}`))) {
    return fail("TS_VALUE_OBJECT_EXTENSION_BEHAVIOR_MISMATCH");
  }
  const observation = mintConstructionObservationV1({
    schema_version: "ConstructionObservation/v1",
    observation_id: "observation.value-object.typescript.settlement-value/v1",
    source_kind: "target-observation", observer_ref: observer,
    definition_ref: denominator.owner_definition_ref,
    factory_ref: extension.base_factory_ref as typeof definition.factories.base,
    attempts,
    equality_probes: equalityProbes,
    nested_delegations: [{
      component_name: String(nested.component_name),
      protocol_id: String(nested.protocol_id),
      protocol_sha256: String(nested.protocol_sha256),
      equality_delegated: nested.equal_observed === true
        && nested.variant_unequal_observed === true,
      hash_delegated: nested.equal_hash_congruent === true,
    }],
    extension: {
      base_factory_ref: extension.base_factory_ref as typeof definition.factories.base,
      extension_factory_ref:
        extension.extension_factory_ref as typeof definition.factories.extension,
      added_validators: extension.added_validators as typeof definition.validators,
      altered_facets: [],
      cycle_detected: extension.extension_is_terminal !== true,
    },
    claim: "transport-observation-only-no-native-runtime-claim",
    collision_freedom_claim: false, authority_effect: "none",
  });
  const family = evaluateCompleteValue({definition, denominator, observation,
    locked_observer_ref: observer});
  if (family.verdict !== "pass") return fail("TS_VALUE_OBJECT_FAMILY_BLOCKED",
    family.findings.map((item) => item.code).join(","));
  const familyControls = catalogue.mutations.map((mutation) => {
    const result = evaluateCompleteValue({definition, denominator,
      observation: applyCompleteValueMutant(observation, mutation),
      locked_observer_ref: observer});
    const found = new Set(result.findings.map((item) => item.code));
    if (result.verdict !== "fail" || !mutation.expected_finding_codes.every((code) =>
      found.has(code as CompleteValueFindingCode))) return fail("TS_VALUE_OBJECT_CONTROL_SURVIVED");
    return Object.freeze({mutation_id: mutation.mutation_id, status: "killed" as const});
  });
  const staticBindingControls = SOURCE_BINDING_CONTROLS.map(
    ([controlId, mutate]) => {
      const mutated = mutate(raw.source);
      if (mutated === raw.source) {
        return fail("TS_VALUE_OBJECT_STATIC_CONTROL_NOOP", controlId);
      }
      try { inspectTypeScriptValueObjectClosedSubset(mutated); }
      catch { return Object.freeze({control_id: controlId,
        evidence_kind: "static-binding-control" as const,
        status: "rejected" as const}); }
      return fail("TS_VALUE_OBJECT_STATIC_CONTROL_SURVIVED", controlId);
    });
  return Object.freeze({
    schema_version: "TypeScriptValueObjectProof/v1" as const, result: "pass" as const,
    target: Object.freeze({target_id: binding.target_id,
      target_sha256: binding.source_ref.sha256, language: "typescript" as const,
      protocol_id: binding.protocol_id}), binding: Object.freeze({
      binding_id: binding.binding_id, binding_sha256: binding.binding_sha256}),
    observation, family_evaluation: family, closed_subset: subset,
    toolchain: Object.freeze({typescript_version: binding.typescript_version,
      compiler_path: binding.typescript_compiler_ref.path,
      compiler_sha256: binding.typescript_compiler_ref.sha256}),
    process_evidence: Object.freeze({executions: 2, distinct_pids: 2,
      semantic_replay_sha256: sha256(canonicalConstructionObservationJson(
        semanticChild(first))),
      input_materialization: "json-inert-owner-cases" as const,
      process_ids_excluded_from_semantic_digest: true}),
    accounting: Object.freeze({positives: Object.freeze({declared: 7, passed: 7}),
      static_binding_controls: Object.freeze({declared: staticBindingControls.length,
        rejected: staticBindingControls.length}), predecessor_family_controls: Object.freeze({
        declared: familyControls.length, killed: familyControls.length})}),
    static_binding_controls: Object.freeze(staticBindingControls),
    predecessor_family_controls: Object.freeze(familyControls),
    claim_ceiling: "one exact hash-locked candidate-local TypeScript Settlement Value Object over owner JSON cases, two fresh processes, complete normalized tuple equality, owned congruent hash, recursive owned immutability, exact bound validators and component protocols, additive validation-only extension, and independent family evaluation; no arbitrary TypeScript, getter or Proxy inputs, OS interception, business correctness beyond the owner fixture, collision freedom, cross-language hash bytes, parity, registration, promotion, publication, deployment, or production claim",
    authority_effect: "none" as const,
  });
};
