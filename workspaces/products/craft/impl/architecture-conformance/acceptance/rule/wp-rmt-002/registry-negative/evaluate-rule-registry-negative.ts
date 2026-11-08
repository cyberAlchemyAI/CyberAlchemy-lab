import {createHash} from "node:crypto";

type JsonObject = Record<string, any>;
type ProviderSpec = Readonly<{
  provider_id: string;
  export_name: string;
  source_role: string;
  module_name?: string;
}>;

const expectedNew: readonly ProviderSpec[] = Object.freeze([
  Object.freeze({provider_id: "rule-typescript-v1",
    export_name: "ruleTypeScriptV1Provider", source_role: "new_provider_typescript"}),
  Object.freeze({provider_id: "rule-python-v1",
    export_name: "rulePythonV1Provider", source_role: "new_provider_python"}),
  Object.freeze({provider_id: "rule-rust-v1",
    export_name: "ruleRustV1Provider", source_role: "new_provider_rust"}),
]);
const expectedPredecessors: readonly ProviderSpec[] = Object.freeze([
  Object.freeze({provider_id: "typescript-rule-v1",
    export_name: "typeScriptRuleV1Provider", module_name: "typescript-rule-v1",
    source_role: "predecessor_provider_typescript"}),
  Object.freeze({provider_id: "python-rule-v1",
    export_name: "pythonRuleV1Provider", module_name: "python-rule-v1",
    source_role: "predecessor_provider_python"}),
  Object.freeze({provider_id: "rust-rule-v1",
    export_name: "rustRuleV1Provider", module_name: "rust-rule-v1",
    source_role: "predecessor_provider_rust"}),
]);
const canonicalValue = (value: unknown): unknown => Array.isArray(value)
  ? value.map(canonicalValue)
  : value !== null && typeof value === "object"
    ? Object.fromEntries(Object.entries(value as JsonObject)
      .sort(([left], [right]) => Buffer.from(left).compare(Buffer.from(right)))
      .map(([key, child]) => [key, canonicalValue(child)]))
    : value;
export const canonicalJson = (value: unknown): string =>
  JSON.stringify(canonicalValue(value));
export const sha256Bytes = (value: string): string =>
  createHash("sha256").update(value).digest("hex");
export const computeBindingSha256 = (binding: JsonObject): string => {
  const {binding_sha256: _ignored, ...body} = binding;
  return sha256Bytes(canonicalJson(body));
};
const fail = (code: string): never => {
  throw Object.assign(new Error(code), {code});
};

export type RuleRegistryNegativeInput = Readonly<{
  binding_raw: string;
  raw_inputs: Readonly<Record<string, string>>;
  registry_before: string;
  registry_after: string;
  runtime_provider_ids: readonly string[];
  predecessor_identity_exact: Readonly<Record<string, boolean>>;
  new_provider_errors: Readonly<Record<string, string>>;
}>;

export const evaluateRuleRegistryNegative = (
  input: RuleRegistryNegativeInput,
) => {
  const binding = JSON.parse(input.binding_raw) as JsonObject;
  if (binding.schema_version !== "RuleWpRmt002RegistryNegativeBinding/v1" ||
      binding.binding_sha256 !== computeBindingSha256(binding) ||
      binding.authority_effect !== "none" ||
      canonicalJson(binding.new_providers) !== canonicalJson(expectedNew) ||
      canonicalJson(binding.predecessor_providers) !==
      canonicalJson(expectedPredecessors)) {
    return fail("RMT_RULE_REGISTRY_BINDING_INVALID");
  }
  if (!Array.isArray(binding.sources) || binding.sources.length !== 8 ||
      Object.keys(input.raw_inputs).length !== 8) {
    return fail("RMT_RULE_REGISTRY_SOURCE_SET_INVALID");
  }
  for (const source of binding.sources as JsonObject[]) {
    const raw = input.raw_inputs[String(source.role)];
    if (raw === undefined || sha256Bytes(raw) !== source.sha256 ||
        Buffer.byteLength(raw, "utf8") !== source.size_bytes) {
      return fail("RMT_RULE_REGISTRY_SOURCE_DRIFT");
    }
  }
  if (input.registry_before !== input.raw_inputs.canonical_registry ||
      input.registry_after !== input.registry_before ||
      sha256Bytes(input.registry_before) !== binding.registry_snapshot.sha256 ||
      Buffer.byteLength(input.registry_before, "utf8") !==
      binding.registry_snapshot.size_bytes) {
    return fail("RMT_RULE_CANONICAL_REGISTRY_CHANGED");
  }
  const dependency = JSON.parse(
    input.raw_inputs.rmt_rule_008_candidate_proof!) as JsonObject;
  if (dependency.swu_id !== "RMT-RULE-008" || dependency.result !== "pass" ||
      dependency.execution_mode !== "candidate-local-fast-lane" ||
      dependency.authority_effect !== "none" ||
      dependency.lifecycle?.registered !== false ||
      dependency.lifecycle?.promoted !== false) {
    return fail("RMT_RULE_REGISTRY_DEPENDENCY_INVALID");
  }
  const runtimeIds = new Set(input.runtime_provider_ids);
  for (const provider of expectedNew) {
    const source = input.raw_inputs[provider.source_role]!;
    if (!source.includes(`provider_id: "${provider.provider_id}"`) ||
        runtimeIds.has(provider.provider_id) ||
        input.new_provider_errors[provider.provider_id] !==
        `FACTORY_PROVIDER_UNKNOWN:${provider.provider_id}`) {
      return fail("RMT_RULE_NEW_PROVIDER_REGISTERED_OR_DRIFTED");
    }
  }
  const registry = input.raw_inputs.canonical_registry!;
  for (const provider of expectedPredecessors) {
    const source = input.raw_inputs[provider.source_role]!;
    const importNeedle = `from "./providers/${provider.module_name}.js"`;
    const symbolPattern = new RegExp(
      `\\b${provider.export_name}\\b[\\s\\S]*from \\\"\\./providers/${provider.module_name}\\.js\\\"`);
    const arrayStart = registry.indexOf("const providers = Object.freeze([");
    const arrayEnd = registry.indexOf("] as const);", arrayStart);
    const providerArray = arrayStart >= 0 && arrayEnd > arrayStart
      ? registry.slice(arrayStart, arrayEnd) : "";
    if (!source.includes(`provider_id: "${provider.provider_id}"`) ||
        !registry.includes(importNeedle) || !symbolPattern.test(registry) ||
        !providerArray.includes(provider.export_name) ||
        !runtimeIds.has(provider.provider_id) ||
        input.predecessor_identity_exact[provider.provider_id] !== true) {
      return fail("RMT_RULE_PREDECESSOR_PROVIDER_NOT_REGISTERED_EXACTLY");
    }
  }
  const projection = Object.freeze({
    schema_version: "RuleWpRmt002RegistryNegativeProof/v1" as const,
    result: "pass" as const,
    provider_files_exact: true,
    canonical_registry_snapshot_exact: true,
    new_provider_ids_absent: true,
    predecessor_provider_ids_present: true,
    predecessor_runtime_identity_exact: true,
    no_registration_write: true,
    checked_new_provider_ids: Object.freeze(expectedNew.map(
      ({provider_id: id}) => id)),
    checked_predecessor_provider_ids: Object.freeze(expectedPredecessors.map(
      ({provider_id: id}) => id)),
    authority_effect: "none" as const,
  });
  return Object.freeze({...projection,
    proof_sha256: sha256Bytes(canonicalJson(projection))});
};
