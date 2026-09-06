import { createCompiledProjectCertificate } from "../compilation/certificate.js";
import { createCheckedInterchange } from "../assurance/checked-interchange.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import { loadCompiledProjectGraph } from "../input/project-model.js";
import { runInMemoryProject } from "./in-memory.js";
import { RuntimeContractError } from "./contracts.js";

export interface DurableOutboxMessageV1 { readonly messageId: string; readonly eventType: string; readonly payload: Readonly<Record<string, unknown>>; readonly occurredAt: string; readonly maxAttempts?: number }
export interface DurableCommitRequestV1 { readonly aggregateType: string; readonly aggregateId: string; readonly state: Readonly<Record<string, unknown>>; readonly expectedVersion: number; readonly messages: readonly DurableOutboxMessageV1[] }
export interface TransactionalOutboxPortV1 {
  readonly provider_id: "sqlite-transactional-outbox-v1" | "postgres-transactional-outbox-v1";
  readonly implementation_sha256: string;
  commit(request: DurableCommitRequestV1, failpoint?: "after-state-write"): { readonly status: "committed" | "already-committed"; readonly version: number };
}
export interface DurableOperationInvocationV1 {
  readonly schema_version: "domainspec.durable-operation-invocation/v1";
  readonly invocation_id: string;
  readonly selector: string;
  readonly operation_input: Readonly<Record<string, unknown>>;
  readonly transaction: Readonly<{ aggregate_type: string; aggregate_id: string; expected_version: number; occurred_at: string; event_ids: Readonly<Record<string, string>>; event_payloads: Readonly<Record<string, Readonly<Record<string, unknown>>>>; max_attempts: number }>;
}
export interface DurableOperationReceiptV1 {
  readonly schema_version: "domainspec.durable-operation-receipt/v1";
  readonly invocation_id: string;
  readonly provider: "sqlite-transactional-outbox-v1" | "postgres-transactional-outbox-v1";
  readonly provider_implementation_sha256: string;
  readonly project_id: string;
  readonly selector: string;
  readonly source_manifest_sha256: string;
  readonly compiled_certificate_sha256: string;
  readonly checked_interchange_sha256: string;
  readonly request_sha256: string;
  readonly semantic_output_sha256: string;
  readonly commit_status: "committed" | "already-committed" | "guard-rejected";
  readonly committed_version: number | null;
  readonly event_ids: readonly string[];
  readonly observed_guarantees: readonly string[];
  readonly authority_effect: "none";
  readonly receipt_sha256: string;
}

function fail(code: string, pointer: string, message: string): never { throw new RuntimeContractError(code, pointer, message); }
function object(value: unknown, pointer: string): Record<string, unknown> { if (value === null || typeof value !== "object" || Array.isArray(value)) fail("MTCLI_DURABLE_SCHEMA", pointer, "expected object"); return value as Record<string, unknown>; }
function text(value: unknown, pointer: string): string { if (typeof value !== "string" || value.length === 0) fail("MTCLI_DURABLE_SCHEMA", pointer, "expected nonempty string"); return value; }
function exact(value: unknown, keys: readonly string[], pointer: string): Record<string, unknown> { const item = object(value, pointer); if (JSON.stringify(Object.keys(item).sort()) !== JSON.stringify([...keys].sort())) fail("MTCLI_DURABLE_SCHEMA", pointer, "unexpected or missing member"); return item; }
function decode(value: unknown): DurableOperationInvocationV1 {
  const item = exact(value, ["schema_version", "invocation_id", "selector", "operation_input", "transaction"], "$request");
  if (item.schema_version !== "domainspec.durable-operation-invocation/v1") fail("MTCLI_DURABLE_SCHEMA", "/schema_version", "unsupported durable invocation schema");
  const transaction = exact(item.transaction, ["aggregate_type", "aggregate_id", "expected_version", "occurred_at", "event_ids", "event_payloads", "max_attempts"], "/transaction");
  if (!Number.isSafeInteger(transaction.expected_version) || Number(transaction.expected_version) < 0) fail("MTCLI_DURABLE_SCHEMA", "/transaction/expected_version", "expected version must be a safe UInt64");
  if (!Number.isSafeInteger(transaction.max_attempts) || Number(transaction.max_attempts) < 1) fail("MTCLI_DURABLE_SCHEMA", "/transaction/max_attempts", "max attempts must be positive");
  const occurredAt = text(transaction.occurred_at, "/transaction/occurred_at"); if (Number.isNaN(Date.parse(occurredAt))) fail("MTCLI_DURABLE_SCHEMA", "/transaction/occurred_at", "invalid timestamp");
  const selector = text(item.selector, "/selector"); if (!/^[a-z][a-z0-9-]*:[a-z][a-z0-9-]*$/.test(selector)) fail("MTCLI_DURABLE_SCHEMA", "/selector", "invalid selector");
  return Object.freeze({ schema_version: "domainspec.durable-operation-invocation/v1", invocation_id: text(item.invocation_id, "/invocation_id"), selector, operation_input: Object.freeze(object(item.operation_input, "/operation_input")), transaction: Object.freeze({ aggregate_type: text(transaction.aggregate_type, "/transaction/aggregate_type"), aggregate_id: text(transaction.aggregate_id, "/transaction/aggregate_id"), expected_version: Number(transaction.expected_version), occurred_at: occurredAt, event_ids: Object.freeze(object(transaction.event_ids, "/transaction/event_ids") as Record<string, string>), event_payloads: Object.freeze(object(transaction.event_payloads, "/transaction/event_payloads") as Record<string, Readonly<Record<string, unknown>>>), max_attempts: Number(transaction.max_attempts) }) });
}

export function runDurableOperation(sourceRoot: string, requestValue: unknown, port: TransactionalOutboxPortV1, failpoint?: "after-state-write"): DurableOperationReceiptV1 {
  const request = decode(requestValue); if (!["sqlite-transactional-outbox-v1", "postgres-transactional-outbox-v1"].includes(port.provider_id) || !/^[a-f0-9]{64}$/.test(port.implementation_sha256)) fail("MTCLI_DURABLE_BINDING", "/provider", "provider identity or implementation digest is invalid");
  const graph = loadCompiledProjectGraph(sourceRoot); const node = graph.nodes.find(({ selector }) => selector === request.selector);
  if (!node || node.kind !== "Operation") fail("MTCLI_DURABLE_ENTRY", "/selector", "durable entry must select a compiled Operation");
  const semantic = runInMemoryProject(sourceRoot, { schema_version: "domainspec.runtime-invocation/v1", invocation_id: request.invocation_id, provider: "in-memory-v1", steps: [{ step_id: "operation", selector: request.selector, input: request.operation_input }] });
  const output = object(semantic.outcomes[0]!.output, "/output"); const accepted = output.ok === true;
  const producedEdges = graph.relationships.filter(({ relationship, source }) => relationship === "produces" && `${source.feature_id}:${source.node_id}` === request.selector);
  if (accepted && producedEdges.length === 0) fail("MTCLI_DURABLE_EVENT", "/selector", "durable Operation must produce at least one Event");
  const messages = producedEdges.map(({ target }) => {
    const selector = `${target.feature_id}:${target.node_id}`; const event = graph.nodes.find((candidate) => candidate.selector === selector);
    if (!event || event.kind !== "Event") fail("MTCLI_DURABLE_EVENT", "/selector", `produces target is not an Event:${selector}`);
    const messageId = text(request.transaction.event_ids[selector], `/transaction/event_ids/${selector}`); const payload = object(request.transaction.event_payloads[selector], `/transaction/event_payloads/${selector}`);
    return Object.freeze({ messageId, eventType: String(event.body.event_type), payload: Object.freeze({ ...payload }), occurredAt: request.transaction.occurred_at, maxAttempts: request.transaction.max_attempts });
  });
  const suppliedEvents = Object.keys(request.transaction.event_ids).sort(); const expectedEvents = producedEdges.map(({ target }) => `${target.feature_id}:${target.node_id}`).sort();
  if (canonicalJson(suppliedEvents) !== canonicalJson(expectedEvents) || canonicalJson(Object.keys(request.transaction.event_payloads).sort()) !== canonicalJson(expectedEvents)) fail("MTCLI_DURABLE_EVENT", "/transaction", "event identities and payloads must exactly match compiled produces edges");
  let commitStatus: DurableOperationReceiptV1["commit_status"] = "guard-rejected"; let version: number | null = null;
  if (accepted) { const state = object(output.state, "/output/state"); const committed = port.commit({ aggregateType: request.transaction.aggregate_type, aggregateId: request.transaction.aggregate_id, state, expectedVersion: request.transaction.expected_version, messages }, failpoint); commitStatus = committed.status; version = committed.version; }
  const certificate = createCompiledProjectCertificate(graph); const interchange = createCheckedInterchange(graph); const body = { schema_version: "domainspec.durable-operation-receipt/v1" as const, invocation_id: request.invocation_id, provider: port.provider_id, provider_implementation_sha256: port.implementation_sha256, project_id: graph.project_id, selector: request.selector, source_manifest_sha256: graph.source_manifest.manifest_sha256, compiled_certificate_sha256: certificate.certificate_sha256, checked_interchange_sha256: interchange.interchange_sha256, request_sha256: sha256(canonicalJson(request)), semantic_output_sha256: semantic.outcomes[0]!.output_sha256, commit_status: commitStatus, committed_version: version, event_ids: Object.freeze(messages.map(({ messageId }) => messageId).sort()), observed_guarantees: Object.freeze(accepted ? ["atomic-state-and-outbox", ...(commitStatus === "already-committed" ? ["idempotent-commit-reconciliation"] : [])] : ["guard-before-persistence"]), authority_effect: "none" as const };
  return Object.freeze({ ...body, receipt_sha256: sha256(canonicalJson(body)) });
}
