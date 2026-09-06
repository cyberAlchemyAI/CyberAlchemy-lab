import fs from "node:fs";
import path from "node:path";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import { loadCompiledProjectGraph } from "../input/project-model.js";
import { createCompiledProjectCertificate } from "../compilation/certificate.js";
import { createCheckedInterchange } from "../assurance/checked-interchange.js";
import { RuntimeContractError, type RuntimeReceiptV1 } from "./contracts.js";
import type { DurableOperationReceiptV1 } from "./durable.js";

const SHA256 = /^[a-f0-9]{64}$/;
const ID = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
const SELECTOR = /^[a-z][a-z0-9-]*:[a-z][a-z0-9-]*$/;

function fail(code: string, pointer: string, message: string): never {
  throw new RuntimeContractError(code, pointer, message);
}

function object(value: unknown, pointer: string): Record<string, unknown> {
  if (value === null || typeof value !== "object" || Array.isArray(value)) fail("MTCLI_RUNTIME_RECEIPT_SCHEMA", pointer, "expected object");
  return value as Record<string, unknown>;
}

function exact(value: unknown, keys: readonly string[], pointer: string): Record<string, unknown> {
  const item = object(value, pointer);
  if (canonicalJson(Object.keys(item).sort()) !== canonicalJson([...keys].sort())) fail("MTCLI_RUNTIME_RECEIPT_SCHEMA", pointer, "unexpected or missing member");
  return item;
}

function text(value: unknown, pointer: string, pattern?: RegExp): string {
  if (typeof value !== "string" || value.length === 0 || (pattern && !pattern.test(value))) fail("MTCLI_RUNTIME_RECEIPT_SCHEMA", pointer, "invalid string");
  return value;
}

function stringArray(value: unknown, pointer: string, pattern?: RegExp): readonly string[] {
  if (!Array.isArray(value)) fail("MTCLI_RUNTIME_RECEIPT_SCHEMA", pointer, "expected array");
  const values = value.map((entry, index) => text(entry, `${pointer}/${index}`, pattern));
  if (new Set(values).size !== values.length) fail("MTCLI_RUNTIME_RECEIPT_SCHEMA", pointer, "array members must be unique");
  return values;
}

function decodeInMemoryReceipt(value: unknown, graph: ReturnType<typeof loadCompiledProjectGraph>): RuntimeReceiptV1 {
  const receipt = exact(value, ["schema_version", "invocation_id", "provider", "project_id", "source_manifest_sha256", "compiled_certificate_sha256", "checked_interchange_sha256", "request_sha256", "outcomes", "coverage", "authority_effect", "receipt_sha256"], "$receipt");
  if (receipt.schema_version !== "domainspec.runtime-receipt/v1" || receipt.provider !== "in-memory-v1" || receipt.authority_effect !== "none") fail("MTCLI_RUNTIME_RECEIPT_SCHEMA", "/schema_version", "invalid in-memory receipt identity or authority");
  text(receipt.invocation_id, "/invocation_id", ID);
  text(receipt.project_id, "/project_id", ID);
  for (const field of ["source_manifest_sha256", "compiled_certificate_sha256", "checked_interchange_sha256", "request_sha256", "receipt_sha256"] as const) text(receipt[field], `/${field}`, SHA256);
  if (!Array.isArray(receipt.outcomes) || receipt.outcomes.length === 0) fail("MTCLI_RUNTIME_RECEIPT_SCHEMA", "/outcomes", "receipt requires at least one outcome");
  const outcomes = receipt.outcomes.map((raw, index) => {
    const pointer = `/outcomes/${index}`;
    const outcome = exact(raw, ["step_id", "selector", "meta_type_id", "kind", "output", "output_sha256"], pointer);
    const stepId = text(outcome.step_id, `${pointer}/step_id`, ID);
    const selector = text(outcome.selector, `${pointer}/selector`, SELECTOR);
    const metaTypeId = text(outcome.meta_type_id, `${pointer}/meta_type_id`, /^DS-D1\.[0-9]+$/);
    const kind = text(outcome.kind, `${pointer}/kind`);
    const outputSha256 = text(outcome.output_sha256, `${pointer}/output_sha256`, SHA256);
    if (sha256(canonicalJson(outcome.output)) !== outputSha256) fail("MTCLI_RUNTIME_RECEIPT_OUTPUT", `${pointer}/output_sha256`, "outcome digest is stale");
    const node = graph.nodes.find((candidate) => candidate.selector === selector);
    if (!node || node.meta_type_id !== metaTypeId || node.kind !== kind) fail("MTCLI_RUNTIME_RECEIPT_OUTCOME", pointer, "outcome does not match the compiled node");
    return { stepId, selector, metaTypeId };
  });
  if (new Set(outcomes.map(({ stepId }) => stepId)).size !== outcomes.length) fail("MTCLI_RUNTIME_RECEIPT_SCHEMA", "/outcomes", "outcome step identities must be unique");
  const coverage = exact(receipt.coverage, ["node_selectors", "meta_type_ids", "relationship_edge_ids", "relationship_ids", "complete_backend_types", "complete_backend_relationships"], "/coverage");
  const nodeSelectors = stringArray(coverage.node_selectors, "/coverage/node_selectors", SELECTOR);
  const metaTypeIds = stringArray(coverage.meta_type_ids, "/coverage/meta_type_ids");
  const relationshipEdgeIds = stringArray(coverage.relationship_edge_ids, "/coverage/relationship_edge_ids", ID);
  const relationshipIds = stringArray(coverage.relationship_ids, "/coverage/relationship_ids", ID);
  if (typeof coverage.complete_backend_types !== "boolean" || typeof coverage.complete_backend_relationships !== "boolean") fail("MTCLI_RUNTIME_RECEIPT_SCHEMA", "/coverage", "coverage completion flags must be Boolean");
  const executed = new Set(outcomes.map(({ selector }) => selector));
  const edges = graph.relationships.filter(({ source, target }) => executed.has(`${source.feature_id}:${source.node_id}`) || executed.has(`${target.feature_id}:${target.node_id}`));
  const expectedCoverage = {
    node_selectors: [...executed].sort(),
    meta_type_ids: [...new Set(outcomes.map(({ metaTypeId }) => metaTypeId))].sort(),
    relationship_edge_ids: edges.map(({ edge_id }) => edge_id).sort(),
    relationship_ids: [...new Set(edges.map(({ relationship }) => relationship))].sort(),
    complete_backend_types: new Set(outcomes.map(({ metaTypeId }) => metaTypeId)).size === 13 && executed.size === graph.nodes.length,
    complete_backend_relationships: new Set(edges.map(({ relationship }) => relationship)).size === 17 && edges.length === graph.relationships.length,
  };
  if (canonicalJson({ node_selectors: nodeSelectors, meta_type_ids: metaTypeIds, relationship_edge_ids: relationshipEdgeIds, relationship_ids: relationshipIds, complete_backend_types: coverage.complete_backend_types, complete_backend_relationships: coverage.complete_backend_relationships }) !== canonicalJson(expectedCoverage)) fail("MTCLI_RUNTIME_RECEIPT_COVERAGE", "/coverage", "coverage does not match receipt outcomes and compiled graph");
  return value as RuntimeReceiptV1;
}

function decodeDurableReceipt(value: unknown, graph: ReturnType<typeof loadCompiledProjectGraph>): DurableOperationReceiptV1 {
  const receipt = exact(value, ["schema_version", "invocation_id", "provider", "provider_implementation_sha256", "project_id", "selector", "source_manifest_sha256", "compiled_certificate_sha256", "checked_interchange_sha256", "request_sha256", "semantic_output_sha256", "commit_status", "committed_version", "event_ids", "observed_guarantees", "authority_effect", "receipt_sha256"], "$receipt");
  if (receipt.schema_version !== "domainspec.durable-operation-receipt/v1" || !["sqlite-transactional-outbox-v1", "postgres-transactional-outbox-v1"].includes(String(receipt.provider)) || receipt.authority_effect !== "none") fail("MTCLI_RUNTIME_RECEIPT_SCHEMA", "/schema_version", "invalid durable receipt identity, provider, or authority");
  text(receipt.invocation_id, "/invocation_id");
  text(receipt.project_id, "/project_id");
  const selector = text(receipt.selector, "/selector", SELECTOR);
  const node = graph.nodes.find((candidate) => candidate.selector === selector);
  if (!node || node.kind !== "Operation") fail("MTCLI_RUNTIME_RECEIPT_OUTCOME", "/selector", "durable receipt entry is not a compiled Operation");
  for (const field of ["provider_implementation_sha256", "source_manifest_sha256", "compiled_certificate_sha256", "checked_interchange_sha256", "request_sha256", "semantic_output_sha256", "receipt_sha256"] as const) text(receipt[field], `/${field}`, SHA256);
  if (!["committed", "already-committed", "guard-rejected"].includes(String(receipt.commit_status))) fail("MTCLI_RUNTIME_RECEIPT_SCHEMA", "/commit_status", "invalid commit status");
  if (receipt.commit_status === "guard-rejected") {
    if (receipt.committed_version !== null) fail("MTCLI_RUNTIME_RECEIPT_SEMANTICS", "/committed_version", "guard rejection cannot have a committed version");
  } else if (!Number.isSafeInteger(receipt.committed_version) || Number(receipt.committed_version) < 0) fail("MTCLI_RUNTIME_RECEIPT_SEMANTICS", "/committed_version", "committed receipt requires a safe nonnegative version");
  stringArray(receipt.event_ids, "/event_ids");
  const guarantees = stringArray(receipt.observed_guarantees, "/observed_guarantees");
  const expectedGuarantees = receipt.commit_status === "guard-rejected" ? ["guard-before-persistence"] : ["atomic-state-and-outbox", ...(receipt.commit_status === "already-committed" ? ["idempotent-commit-reconciliation"] : [])];
  if (canonicalJson(guarantees) !== canonicalJson(expectedGuarantees)) fail("MTCLI_RUNTIME_RECEIPT_SEMANTICS", "/observed_guarantees", "observed guarantees do not match commit status");
  return value as DurableOperationReceiptV1;
}

export function materializeRuntimeReceipt<T extends RuntimeReceiptV1 | DurableOperationReceiptV1>(receipt: T, targetPath: string): T {
  if (!path.isAbsolute(targetPath) || path.resolve(targetPath) !== targetPath) throw new RuntimeContractError("MTCLI_RUNTIME_RECEIPT_PATH", "/receipt", "runtime receipt target must be a normalized absolute path");
  if (fs.existsSync(targetPath)) throw new RuntimeContractError("MTCLI_RUNTIME_RECEIPT_EXISTS", "/receipt", "runtime receipt target already exists");
  const parent = path.dirname(targetPath); let stats: fs.Stats;
  try { stats = fs.lstatSync(parent); } catch { throw new RuntimeContractError("MTCLI_RUNTIME_RECEIPT_PARENT", "/receipt", "runtime receipt parent does not exist"); }
  if (!stats.isDirectory() || stats.isSymbolicLink() || fs.realpathSync(parent) !== parent) throw new RuntimeContractError("MTCLI_RUNTIME_RECEIPT_PARENT", "/receipt", "runtime receipt parent must be a real directory");
  const temporary = path.join(parent, `.${path.basename(targetPath)}.${process.pid}.${Date.now()}.tmp`);
  try { fs.writeFileSync(temporary, `${canonicalJson(receipt)}\n`, { flag: "wx", mode: 0o644 }); fs.linkSync(temporary, targetPath); fs.unlinkSync(temporary); }
  catch (error) { fs.rmSync(temporary, { force: true }); if ((error as NodeJS.ErrnoException).code === "EEXIST") throw new RuntimeContractError("MTCLI_RUNTIME_RECEIPT_EXISTS", "/receipt", "runtime receipt target appeared during publication"); throw error; }
  return receipt;
}

export function validateRuntimeReceiptBinding(sourceRoot: string, value: unknown): RuntimeReceiptV1 | DurableOperationReceiptV1 {
  const receipt = object(value, "$receipt");
  if (receipt.schema_version !== "domainspec.runtime-receipt/v1" && receipt.schema_version !== "domainspec.durable-operation-receipt/v1") throw new RuntimeContractError("MTCLI_RUNTIME_RECEIPT_SCHEMA", "/schema_version", "unsupported runtime receipt");
  const graph = loadCompiledProjectGraph(sourceRoot);
  const decoded = receipt.schema_version === "domainspec.runtime-receipt/v1" ? decodeInMemoryReceipt(value, graph) : decodeDurableReceipt(value, graph);
  const certificate = createCompiledProjectCertificate(graph);
  const interchange = createCheckedInterchange(graph);
  if (receipt.project_id !== graph.project_id || receipt.source_manifest_sha256 !== graph.source_manifest.manifest_sha256) throw new RuntimeContractError("MTCLI_RUNTIME_RECEIPT_SOURCE", "/source_manifest_sha256", "runtime receipt belongs to another source graph");
  if (receipt.compiled_certificate_sha256 !== certificate.certificate_sha256) throw new RuntimeContractError("MTCLI_RUNTIME_RECEIPT_CERTIFICATE", "/compiled_certificate_sha256", "runtime receipt compiled certificate drifted");
  if (receipt.checked_interchange_sha256 !== interchange.interchange_sha256) throw new RuntimeContractError("MTCLI_RUNTIME_RECEIPT_INTERCHANGE", "/checked_interchange_sha256", "runtime receipt checked interchange drifted");
  if (typeof receipt.receipt_sha256 !== "string" || !/^[a-f0-9]{64}$/.test(receipt.receipt_sha256)) throw new RuntimeContractError("MTCLI_RUNTIME_RECEIPT_DIGEST", "/receipt_sha256", "runtime receipt digest is invalid");
  const { receipt_sha256: ignored, ...body } = receipt;
  if (sha256(canonicalJson(body)) !== receipt.receipt_sha256) throw new RuntimeContractError("MTCLI_RUNTIME_RECEIPT_DIGEST", "/receipt_sha256", "runtime receipt digest is stale");
  return decoded;
}
