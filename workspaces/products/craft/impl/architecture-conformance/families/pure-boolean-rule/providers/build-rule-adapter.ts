import {createHash} from "node:crypto";

import type {
  FactoryNodeProviderV1,
  FactoryNodeSemanticResultV1,
} from "../../../factory/contracts/factory-node-provider-v1.js";

type JsonObject = Record<string, unknown>;
type AdapterRole =
  | "target_source"
  | "observer_source"
  | "provider_source"
  | "predecessor_provider_source";
type ExactRef = Readonly<{path: string; sha256: string}>;

export type RuleAdapterBindingV1 = Readonly<{
  schema_version: "RuleAdapterBinding/v1";
  realization_id: string;
  target_id: "typescript" | "python" | "rust";
  provider_id: string;
  predecessor_provider_id: string;
  refs: Readonly<Record<AdapterRole, ExactRef>>;
  binding_sha256: string;
  authority_effect: "none";
}>;

const sha256 = (value: string | Uint8Array): string =>
  createHash("sha256").update(value).digest("hex");
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const isRecord = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const canonical = (value: unknown): unknown => Array.isArray(value)
  ? value.map(canonical)
  : isRecord(value)
    ? Object.fromEntries(Object.entries(value)
      .sort(([left], [right]) => compareUtf8(left, right))
      .map(([key, child]) => [key, canonical(child)]))
    : value;
const exactKeys = (value: JsonObject, expected: readonly string[]): boolean => {
  const actual = Object.keys(value).sort(compareUtf8);
  const wanted = [...expected].sort(compareUtf8);
  return actual.length === wanted.length &&
    actual.every((key, index) => key === wanted[index]);
};
const fail = (code: string, detail?: string): never => {
  throw Object.assign(new Error(detail === undefined ? code : `${code}:${detail}`),
    {code, detail: detail ?? null});
};
const SHA256 = /^[a-f0-9]{64}$/u;
const ADAPTER_ROLES = Object.freeze([
  "target_source",
  "observer_source",
  "provider_source",
  "predecessor_provider_source",
] as const);

const decodeBinding = (input: Readonly<{
  bytes: string;
  expected: Readonly<{
    realization_id: string;
    target_id: "typescript" | "python" | "rust";
    provider_id: string;
    predecessor_provider_id: string;
    ref_paths: Readonly<Record<AdapterRole, string>>;
  }>;
  raw_inputs: Readonly<Record<string, string>>;
}>): RuleAdapterBindingV1 => {
  let value: unknown;
  try {
    value = JSON.parse(input.bytes);
  } catch {
    return fail("RMT_RULE_ADAPTER_BINDING_JSON_INVALID");
  }
  if (!isRecord(value) || !exactKeys(value, [
    "schema_version", "realization_id", "target_id", "provider_id",
    "predecessor_provider_id", "refs", "binding_sha256", "authority_effect",
  ]) || value.schema_version !== "RuleAdapterBinding/v1" ||
      value.realization_id !== input.expected.realization_id ||
      value.target_id !== input.expected.target_id ||
      value.provider_id !== input.expected.provider_id ||
      value.predecessor_provider_id !== input.expected.predecessor_provider_id ||
      value.authority_effect !== "none" || !isRecord(value.refs) ||
      !exactKeys(value.refs, ADAPTER_ROLES) ||
      typeof value.binding_sha256 !== "string" ||
      !SHA256.test(value.binding_sha256)) {
    return fail("RMT_RULE_ADAPTER_BINDING_POLICY_INVALID");
  }
  for (const role of ADAPTER_ROLES) {
    const ref = value.refs[role];
    if (!isRecord(ref) || !exactKeys(ref, ["path", "sha256"]) ||
        ref.path !== input.expected.ref_paths[role] ||
        typeof ref.sha256 !== "string" || !SHA256.test(ref.sha256)) {
      return fail("RMT_RULE_ADAPTER_REF_INVALID", role);
    }
    if (sha256(input.raw_inputs[role] ?? "") !== ref.sha256) {
      return fail("RMT_RULE_ADAPTER_REF_STALE", role);
    }
  }
  const {binding_sha256: _digest, ...body} = value;
  if (sha256(JSON.stringify(canonical(body))) !== value.binding_sha256) {
    return fail("RMT_RULE_ADAPTER_BINDING_DIGEST_STALE");
  }
  return value as RuleAdapterBindingV1;
};
export const executeRuleAdapter = async (input: Readonly<{
  raw_inputs: Readonly<Record<string, string>>;
  raw_paths: Readonly<Record<string, string>>;
  predecessor: FactoryNodeProviderV1;
  expected: Readonly<{
    realization_id: string;
    target_id: "typescript" | "python" | "rust";
    provider_id: string;
    predecessor_provider_id: string;
    ref_paths: Readonly<Record<AdapterRole, string>>;
  }>;
}>): Promise<FactoryNodeSemanticResultV1> => {
  const expectedRoles = Object.keys(input.raw_paths).sort(compareUtf8);
  const actualRoles = Object.keys(input.raw_inputs).sort(compareUtf8);
  if (JSON.stringify(actualRoles) !== JSON.stringify(expectedRoles)) {
    return fail("RMT_RULE_ADAPTER_INPUT_ROLES_INVALID");
  }
  const snapshot = Object.freeze(Object.fromEntries(expectedRoles.map((role) =>
    [role, `${input.raw_inputs[role]}`]))) as Readonly<Record<string, string>>;
  const binding = decodeBinding({
    bytes: snapshot.adapter_binding ?? fail(
      "RMT_RULE_ADAPTER_INPUT_ROLES_INVALID", "adapter_binding"),
    expected: input.expected,
    raw_inputs: snapshot,
  });
  if (input.predecessor.provider_id !== input.expected.predecessor_provider_id) {
    return fail("RMT_RULE_ADAPTER_PREDECESSOR_ID_INVALID");
  }
  const predecessorInputs = Object.freeze(Object.fromEntries(
    input.predecessor.required_input_roles.map((role) => [
      role,
      snapshot[role] ?? fail("RMT_RULE_ADAPTER_PREDECESSOR_INPUT_MISSING", role),
    ]),
  ));
  const predecessorResult = await input.predecessor.execute({
    raw_inputs: predecessorInputs,
    upstream: {},
  });
  if (predecessorResult.result !== "pass" ||
      predecessorResult.provider_id !== input.expected.predecessor_provider_id ||
      predecessorResult.authority_effect !== "none") {
    return fail("RMT_RULE_ADAPTER_PREDECESSOR_RESULT_INVALID");
  }
  const predecessorOutput = predecessorResult.semantic_output as Readonly<{
    summary?: unknown;
    observations?: unknown;
  }>;
  if (predecessorOutput.summary === undefined ||
      predecessorOutput.observations === undefined) {
    return fail("RMT_RULE_ADAPTER_PREDECESSOR_OUTPUT_INVALID");
  }
  return Object.freeze({
    schema_version: "FactoryNodeSemanticResult/v1" as const,
    result: "pass" as const,
    provider_id: input.expected.provider_id,
    semantic_output: Object.freeze({
      summary: predecessorOutput.summary,
      observations: predecessorOutput.observations,
      adapter_binding: binding,
      native_evidence: Object.freeze({
        target_id: input.expected.target_id,
        predecessor_provider_id: input.expected.predecessor_provider_id,
        predecessor_result_provider_id: predecessorResult.provider_id,
        target_source_sha256: binding.refs.target_source.sha256,
        observer_source_sha256: binding.refs.observer_source.sha256,
        provider_source_sha256: binding.refs.provider_source.sha256,
        native_hash_byte_comparison: false,
      }),
    }),
    accounting: predecessorResult.accounting,
    claim_ceiling: `one hash-bound candidate-local ${input.expected.target_id} Rule adapter delegating to ${input.expected.predecessor_provider_id}; no registration, admission, promotion, publication, deployment, or production claim`,
    authority_effect: "none" as const,
  });
};
