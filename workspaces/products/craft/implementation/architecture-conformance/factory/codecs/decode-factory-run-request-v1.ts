import {
  FACTORY_PURPOSES,
  type FactoryRunNodeRequestV1,
  type FactoryRunRequestV1,
} from "../contracts/factory-run-request-v1.js";
import { exactKeys, fail, isRecord, safeRelativePath } from "../shared/canonical.js";

const idPattern = /^[a-z0-9][a-z0-9._-]*$/u;
const rolePattern = /^[A-Za-z][A-Za-z0-9._-]*$/u;
const historicalRoots = Object.freeze([
  "projects/domainspec-v2/development/meta-type-realization-factory/runs/",
  "projects/domainspec-v2/development/meta-type-realization-factory/receipts/",
]);

const string = (value: unknown, code = "FACTORY_REQUEST_INVALID"): string => {
  return typeof value === "string" && value.length > 0 ? value : fail(code, "string");
};

const decodeNode = (value: unknown): FactoryRunNodeRequestV1 => {
  const record = isRecord(value) ? value : fail("FACTORY_REQUEST_INVALID", "node");
  exactKeys(record, ["node_id", "kind", "provider_id", "depends_on", "input_refs", "claim_ceiling"]);
  const nodeId = string(record.node_id);
  const providerId = string(record.provider_id);
  if (!idPattern.test(nodeId) || !idPattern.test(providerId)) fail("FACTORY_REQUEST_INVALID", "id");
  if (!(["direct-proof", "join-proof", "projection"] as unknown[]).includes(record.kind)) {
    fail("FACTORY_REQUEST_INVALID", "kind");
  }
  const dependsOn = Array.isArray(record.depends_on)
    ? record.depends_on : fail("FACTORY_REQUEST_INVALID", "depends_on");
  if (dependsOn.some((id: unknown) =>
    typeof id !== "string" || !idPattern.test(id))) fail("FACTORY_REQUEST_INVALID", "depends_on");
  const inputRefValues = Array.isArray(record.input_refs)
    ? record.input_refs : fail("FACTORY_REQUEST_INVALID", "input_refs");
  const inputRefs = inputRefValues.map((item: unknown) => {
    const inputRef = isRecord(item) ? item : fail("FACTORY_REQUEST_INVALID", "input_ref");
    exactKeys(inputRef, ["role", "ref"]);
    const sourceRef = isRecord(inputRef.ref)
      ? inputRef.ref : fail("FACTORY_REQUEST_INVALID", "source_ref");
    const refKeys = Object.keys(sourceRef);
    if (refKeys.length < 1 || refKeys.length > 2 || !refKeys.includes("path") ||
        refKeys.some((key) => key !== "path" && key !== "sha256")) {
      fail("FACTORY_REQUEST_INVALID", "source_ref");
    }
    const path = string(sourceRef.path);
    const role = string(inputRef.role);
    if (!rolePattern.test(role) || !safeRelativePath(path)) {
      fail("FACTORY_REQUEST_INVALID", "unsafe-path-or-role");
    }
    if (historicalRoots.some((root) => path.startsWith(root))) {
      fail("FACTORY_HISTORICAL_EVIDENCE_DEPENDENCY", path);
    }
    const expectedSha256 = sourceRef.sha256 === undefined ? undefined
      : typeof sourceRef.sha256 === "string" && /^[a-f0-9]{64}$/u.test(sourceRef.sha256)
        ? sourceRef.sha256 : fail("FACTORY_REQUEST_INVALID", "sha256");
    return Object.freeze({ role, ref: Object.freeze({ path, ...(expectedSha256 === undefined
      ? {} : { sha256: expectedSha256 }) }) });
  });
  return Object.freeze({
    node_id: nodeId,
    kind: record.kind as FactoryRunNodeRequestV1["kind"],
    provider_id: providerId,
    depends_on: Object.freeze([...(dependsOn as string[])]),
    input_refs: Object.freeze(inputRefs),
    claim_ceiling: string(record.claim_ceiling),
  });
};

export const decodeFactoryRunRequestV1 = (value: unknown): FactoryRunRequestV1 => {
  const record = isRecord(value) ? value : fail("FACTORY_REQUEST_INVALID", "root");
  exactKeys(record, ["schema_version", "request_id", "suite_id", "purpose", "nodes", "claim_ceiling", "authority_effect"]);
  const nodeValues = Array.isArray(record.nodes)
    ? record.nodes : fail("FACTORY_REQUEST_INVALID", "nodes");
  if (record.schema_version !== "FactoryRunRequest/v1" || record.authority_effect !== "none" ||
      !FACTORY_PURPOSES.includes(record.purpose as never) ||
      nodeValues.length === 0) fail("FACTORY_REQUEST_INVALID", "header");
  const nodes = nodeValues.map(decodeNode);
  const nodeIds = nodes.map(({ node_id: id }) => id);
  if (new Set(nodeIds).size !== nodeIds.length) fail("FACTORY_GRAPH_INVALID", "duplicate-node");
  return Object.freeze({
    schema_version: "FactoryRunRequest/v1",
    request_id: string(record.request_id),
    suite_id: string(record.suite_id),
    purpose: record.purpose as FactoryRunRequestV1["purpose"],
    nodes: Object.freeze(nodes),
    claim_ceiling: string(record.claim_ceiling),
    authority_effect: "none",
  });
};
