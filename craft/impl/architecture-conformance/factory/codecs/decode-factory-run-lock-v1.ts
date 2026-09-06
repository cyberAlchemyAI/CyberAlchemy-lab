import { FACTORY_PURPOSES } from "../contracts/factory-run-request-v1.js";
import type {
  FactoryRunLockV1,
  LockedFactoryNodeV1,
  LockedFactoryRefV1,
  LockedFactoryToolV1,
} from "../contracts/factory-run-lock-v1.js";
import type { LockedFactoryArtifactV1 } from
  "../contracts/factory-locked-artifact-v1.js";
import {
  canonicalJson,
  exactKeys,
  fail,
  isRecord,
  safeRelativePath,
  sha256,
} from "../shared/canonical.js";

const SHA256 = /^[a-f0-9]{64}$/u;
const ID = /^[a-z0-9][a-z0-9._-]*$/u;
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));

const deepFreeze = <T>(value: T): T => {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    for (const child of Object.values(value as Record<string, unknown>)) deepFreeze(child);
    Object.freeze(value);
  }
  return value;
};

const string = (value: unknown, detail: string): string =>
  typeof value === "string" && value.length > 0 ? value : fail("FACTORY_LOCK_INVALID", detail);

const stringArray = (value: unknown, detail: string): readonly string[] => {
  if (!Array.isArray(value) || value.some((item) => typeof item !== "string")) {
    return fail("FACTORY_LOCK_INVALID", detail);
  }
  return Object.freeze([...(value as string[])]);
};

const decodeRef = (value: unknown): LockedFactoryRefV1 => {
  const record = isRecord(value) ? value : fail("FACTORY_LOCK_INVALID", "ref");
  exactKeys(record, ["role", "path", "sha256", "byte_length"], "FACTORY_LOCK_INVALID");
  const path = string(record.path, "ref-path");
  const digest = string(record.sha256, "ref-sha256");
  if (!safeRelativePath(path) || !SHA256.test(digest) ||
      !Number.isInteger(record.byte_length) || (record.byte_length as number) < 0) {
    fail("FACTORY_LOCK_INVALID", "ref");
  }
  return Object.freeze({
    role: string(record.role, "ref-role"),
    path,
    sha256: digest,
    byte_length: record.byte_length as number,
  });
};

const decodeTool = (value: unknown): LockedFactoryToolV1 => {
  const record = isRecord(value) ? value : fail("FACTORY_LOCK_INVALID", "tool");
  exactKeys(record, ["tool_id", "version", "executable_sha256"], "FACTORY_LOCK_INVALID");
  const toolId = string(record.tool_id, "tool-id");
  const digest = string(record.executable_sha256, "tool-sha256");
  if (!ID.test(toolId) || !SHA256.test(digest)) fail("FACTORY_LOCK_INVALID", "tool");
  return Object.freeze({
    tool_id: toolId,
    version: string(record.version, "tool-version"),
    executable_sha256: digest,
  });
};

const decodeArtifact = (value: unknown): LockedFactoryArtifactV1 => {
  const record = isRecord(value) ? value : fail("FACTORY_LOCK_INVALID", "artifact");
  exactKeys(record, ["schema_version", "artifact_id", "version", "sha256"],
    "FACTORY_LOCK_INVALID");
  const artifactId = string(record.artifact_id, "artifact-id");
  const digest = string(record.sha256, "artifact-sha256");
  if (record.schema_version !== "LockedFactoryArtifact/v1" || !ID.test(artifactId) ||
      !SHA256.test(digest)) fail("FACTORY_LOCK_INVALID", "artifact");
  return Object.freeze({
    schema_version: "LockedFactoryArtifact/v1",
    artifact_id: artifactId,
    version: string(record.version, "artifact-version"),
    sha256: digest,
  });
};

const decodeNode = (value: unknown): LockedFactoryNodeV1 => {
  const record = isRecord(value) ? value : fail("FACTORY_LOCK_INVALID", "node");
  const hasArtifacts = Object.prototype.hasOwnProperty.call(record, "artifacts");
  const hasTimeout = Object.prototype.hasOwnProperty.call(record, "execution_timeout_ms");
  if (hasArtifacts !== hasTimeout) fail("FACTORY_LOCK_INVALID", "historical-pair");
  exactKeys(record, [
    "node_id",
    "kind",
    "provider_id",
    "provider_version",
    "depends_on",
    "inputs",
    "components",
    "tools",
    ...(hasArtifacts ? ["artifacts", "execution_timeout_ms"] : []),
    "claim_ceiling",
  ], "FACTORY_LOCK_INVALID");
  if (!(record.kind === "direct-proof" || record.kind === "join-proof" ||
      record.kind === "projection")) fail("FACTORY_LOCK_INVALID", "node-kind");
  if (!Array.isArray(record.inputs) || !Array.isArray(record.components) ||
      !Array.isArray(record.tools) || (hasArtifacts && !Array.isArray(record.artifacts))) {
    fail("FACTORY_LOCK_INVALID", "node-arrays");
  }
  const tools = (record.tools as unknown[]).map(decodeTool);
  const artifacts = hasArtifacts
    ? (record.artifacts as unknown[]).map(decodeArtifact) : [];
  const toolIds = tools.map(({ tool_id: id }) => id);
  const artifactIds = artifacts.map(({ artifact_id: id }) => id);
  if (new Set(toolIds).size !== toolIds.length ||
      new Set(artifactIds).size !== artifactIds.length ||
      toolIds.some((id) => artifactIds.includes(id)) ||
      JSON.stringify([...toolIds].sort(compareUtf8)) !== JSON.stringify(toolIds) ||
      JSON.stringify([...artifactIds].sort(compareUtf8)) !== JSON.stringify(artifactIds)) {
    fail("FACTORY_RUNTIME_MATERIAL_DUPLICATE", String(record.node_id));
  }
  const timeout = hasTimeout ? record.execution_timeout_ms : 70_000;
  if (!Number.isInteger(timeout) || (timeout as number) < 1 || (timeout as number) > 300_000) {
    fail("FACTORY_PROVIDER_TIMEOUT_INVALID", String(record.node_id));
  }
  const nodeId = string(record.node_id, "node-id");
  const providerId = string(record.provider_id, "provider-id");
  if (!ID.test(nodeId) || !ID.test(providerId)) fail("FACTORY_LOCK_INVALID", "node-id");
  return Object.freeze({
    node_id: nodeId,
    kind: record.kind as LockedFactoryNodeV1["kind"],
    provider_id: providerId,
    provider_version: string(record.provider_version, "provider-version"),
    depends_on: stringArray(record.depends_on, "depends-on"),
    inputs: Object.freeze((record.inputs as unknown[]).map(decodeRef)),
    components: Object.freeze((record.components as unknown[]).map(decodeRef)),
    tools: Object.freeze(tools),
    artifacts: Object.freeze(artifacts),
    execution_timeout_ms: timeout as number,
    claim_ceiling: string(record.claim_ceiling, "claim-ceiling"),
  });
};

export const decodeFactoryRunLockV1 = (value: unknown): FactoryRunLockV1 => {
  const record = isRecord(value) ? value : fail("FACTORY_LOCK_INVALID");
  exactKeys(record, [
    "schema_version",
    "request_id",
    "suite_id",
    "purpose",
    "request_sha256",
    "ordered_node_ids",
    "nodes",
    "replay_policy",
    "claim_ceiling",
    "authority_effect",
    "lock_sha256",
  ], "FACTORY_LOCK_INVALID");
  if (record.schema_version !== "FactoryRunLock/v1" ||
      record.authority_effect !== "none" || typeof record.lock_sha256 !== "string" ||
      !SHA256.test(record.lock_sha256)) fail("FACTORY_LOCK_INVALID");
  const body = Object.fromEntries(Object.entries(record).filter(([key]) => key !== "lock_sha256"));
  if (sha256(canonicalJson(body)) !== record.lock_sha256) fail("FACTORY_LOCK_STALE");
  if (!Array.isArray(record.nodes) || !isRecord(record.replay_policy)) {
    fail("FACTORY_LOCK_INVALID", "root");
  }
  const nodes = (record.nodes as unknown[]).map(decodeNode);
  const orderedNodeIds = stringArray(record.ordered_node_ids, "ordered-nodes");
  const nodeIds = nodes.map(({ node_id: id }) => id);
  if (new Set(nodeIds).size !== nodeIds.length ||
      new Set(orderedNodeIds).size !== orderedNodeIds.length ||
      JSON.stringify([...nodeIds].sort(compareUtf8)) !==
        JSON.stringify([...orderedNodeIds].sort(compareUtf8))) {
    fail("FACTORY_LOCK_INVALID", "node-set");
  }
  const policy = isRecord(record.replay_policy)
    ? record.replay_policy : fail("FACTORY_LOCK_INVALID", "policy");
  exactKeys(policy, ["timeout_ms", "output_limit_bytes", "termination_grace_ms", "environment_keys"],
    "FACTORY_LOCK_INVALID");
  const environmentKeys = stringArray(policy.environment_keys, "environment-keys");
  if (!Number.isInteger(policy.timeout_ms) || (policy.timeout_ms as number) < 1 ||
      !Number.isInteger(policy.output_limit_bytes) || (policy.output_limit_bytes as number) < 1 ||
      !Number.isInteger(policy.termination_grace_ms) ||
      (policy.termination_grace_ms as number) < 0 ||
      new Set(environmentKeys).size !== environmentKeys.length ||
      !FACTORY_PURPOSES.includes(record.purpose as never)) {
    fail("FACTORY_LOCK_INVALID", "policy-or-purpose");
  }
  return deepFreeze({
    schema_version: "FactoryRunLock/v1",
    request_id: string(record.request_id, "request-id"),
    suite_id: string(record.suite_id, "suite-id"),
    purpose: record.purpose as FactoryRunLockV1["purpose"],
    request_sha256: string(record.request_sha256, "request-sha256"),
    ordered_node_ids: orderedNodeIds,
    nodes: Object.freeze(nodes),
    replay_policy: Object.freeze({
      timeout_ms: policy.timeout_ms as number,
      output_limit_bytes: policy.output_limit_bytes as number,
      termination_grace_ms: policy.termination_grace_ms as number,
      environment_keys: environmentKeys,
    }),
    claim_ceiling: string(record.claim_ceiling, "claim-ceiling"),
    authority_effect: "none",
    lock_sha256: record.lock_sha256 as string,
  });
};
