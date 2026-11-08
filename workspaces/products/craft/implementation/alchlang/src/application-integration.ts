import { CompilationRejected } from "./model.js";
import type { ApplicationSourceSection } from "./formal-claim.js";

export const applicationIntegrationKinds = new Set([
  "subscription", "publication", "inbound-endpoint", "outbound-call", "outbound-write", "persistence",
]);

interface Located { id: string; source_line: number }
export interface IntegrationReference { ref: string; source_line: number }
export interface IntegrationChannel extends IntegrationReference { kind: "queue" | "topic" | "stream" }
export interface ApplicationSubscription extends Located {
  kind: "subscription";
  channel: IntegrationChannel;
  message: IntegrationReference;
  mapping: IntegrationReference;
  operation: IntegrationReference;
  acknowledge: { condition: "application-committed" | "consumer-handler-returned"; source_line: number };
  deduplicate: { key_path: string[]; source_line: number };
  dead_letter: IntegrationReference;
}
export interface ApplicationPublication extends Located {
  kind: "publication";
  event: IntegrationReference;
  mapping: IntegrationReference;
  message: IntegrationReference;
  channel: IntegrationChannel;
}
export interface ApplicationInboundEndpoint extends Located {
  kind: "inbound-endpoint";
  protocol: { kind: "HTTP"; method: string; path: string; source_line: number };
  request: IntegrationReference;
  operation: IntegrationReference;
  response: IntegrationReference;
}
export interface ApplicationOutboundCall extends Located {
  kind: "outbound-call";
  operation: IntegrationReference;
  request: IntegrationReference;
  external_api: IntegrationReference;
  response: IntegrationReference;
  /** Optional explicit projection from a provider response into the existing Operation input. */
  decision_mapping: IntegrationReference | null;
}
/** Authored write intent only. Native custody and execution belong to Craft. */
export interface ApplicationOutboundWrite extends Located {
  kind: "outbound-write";
  operation: IntegrationReference;
  interface: IntegrationReference;
  write: IntegrationReference;
  inspect: IntegrationReference;
  request_mapping: IntegrationReference;
  inspect_request_mapping: IntegrationReference;
  response_mapping: IntegrationReference;
  on_unknown: { action: "inspect"; source_line: number };
  on_unresolved: { action: "pending"; source_line: number };
  on_conflict: { action: "reject"; source_line: number };
}
export interface ApplicationPersistence extends Located {
  kind: "persistence";
  entity: IntegrationReference;
  queries: IntegrationReference[];
  operations: IntegrationReference[];
  transaction: { scope: "single-resource-local"; source_line: number };
}
export type ApplicationIntegration = ApplicationSubscription | ApplicationPublication
  | ApplicationInboundEndpoint | ApplicationOutboundCall | ApplicationOutboundWrite | ApplicationPersistence;

const name = "[A-Za-z_][\\w.-]*";
type Row = ApplicationSourceSection["rows"][number];
function fail(code: string, line: number, message: string): never {
  throw new CompilationRejected([{ code, path: `$line:${line}`, message }]);
}

/** Decode existing scanner sections into graph intent, never executable steps. */
export function normalizeApplicationIntegrations(sections: ApplicationSourceSection[]): ApplicationIntegration[] {
  return sections.map(section => {
    const { rows } = section;
    const located = { id: section.id, source_line: section.line };
    if (!applicationIntegrationKinds.has(section.kind)) fail("INTEGRATION_KIND", section.line, "unknown integration kind");
    const base = rows[0]?.indent ?? 0;
    if (!rows.length || base <= 0) fail("INTEGRATION_PATH", section.line, "integration requires an indented declaration body");
    const rowAt = (index: number): Row => rows[index] ?? fail("INTEGRATION_PATH", section.line, "incomplete integration path");
    const level = (row: Row, arrow: boolean): void => {
      const expected = arrow ? rows[1]?.indent : base;
      if ((row.indent ?? 0) !== expected || (arrow && (expected ?? 0) <= base)) {
        fail("INTEGRATION_INDENT", row.line, "path arrows share one deeper level; clauses use the body level");
      }
    };
    const ref = (index: number, roles: string[], arrow = index > 0): IntegrationReference & { role: string } => {
      const row = rowAt(index); level(row, arrow);
      const match = new RegExp(`^${arrow ? "->\\s+" : ""}(${roles.join("|")})\\s+(${name})$`).exec(row.text);
      if (!match) fail("INTEGRATION_PATH", row.line, `expected ${arrow ? "-> " : ""}${roles.join(" or ")} <reference>`);
      return { role: match![1]!, ref: match![2]!, source_line: row.line };
    };
    const reference = (index: number, role: string, arrow = index > 0): IntegrationReference => {
      const value = ref(index, [role], arrow); return { ref: value.ref, source_line: value.source_line };
    };
    const channel = (index: number): IntegrationChannel => {
      const value = ref(index, ["queue", "topic", "stream"]);
      return { kind: value.role as IntegrationChannel["kind"], ref: value.ref, source_line: value.source_line };
    };
    const count = (expected: number): void => {
      if (rows.length !== expected) fail("INTEGRATION_PATH", rows[expected]?.line ?? section.line, `expected ${expected} clauses, found ${rows.length}`);
    };
    if (section.kind === "subscription") {
      count(7);
      const source = channel(0); const message = reference(1, "message");
      const mapping = reference(2, "map"); const operation = reference(3, "operation");
      const ackRow = rowAt(4); level(ackRow, false);
      const ack = /^acknowledge after (application-commit|handler-return)$/.exec(ackRow.text);
      if (!ack) fail("INTEGRATION_ACK", ackRow.line, "declare application-commit or handler-return acknowledgement explicitly");
      const dedupRow = rowAt(5); level(dedupRow, false);
      const dedup = /^deduplicate by ([A-Za-z_][\w-]*(?:\.[A-Za-z_][\w-]*)*)$/.exec(dedupRow.text);
      if (!dedup) fail("INTEGRATION_DEDUP", dedupRow.line, "deduplication requires an explicit field path, not an expression");
      const failureRow = rowAt(6); level(failureRow, false);
      const failure = new RegExp(`^failure -> dead-letter (${name})$`).exec(failureRow.text);
      if (!failure) fail("INTEGRATION_FAILURE", failureRow.line, "declare the dead-letter channel explicitly");
      return { ...located, kind: "subscription", channel: source, message, mapping, operation,
        acknowledge: { condition: ack![1] === "application-commit" ? "application-committed" : "consumer-handler-returned", source_line: ackRow.line },
        deduplicate: { key_path: dedup![1]!.split("."), source_line: dedupRow.line },
        dead_letter: { ref: failure![1]!, source_line: failureRow.line } };
    }
    if (section.kind === "publication") {
      count(4);
      return { ...located, kind: "publication", event: reference(0, "event"), mapping: reference(1, "map"),
        message: reference(2, "message"), channel: channel(3) };
    }
    if (section.kind === "inbound-endpoint") {
      count(4); const row = rowAt(0); level(row, false);
      const http = /^HTTP (GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS) ("(?:[^"\\]|\\.)*")$/.exec(row.text);
      if (!http) fail("INTEGRATION_HTTP", row.line, "expected HTTP <method> <quoted absolute route path>");
      let path: string;
      try { path = JSON.parse(http![2]!); } catch { return fail("INTEGRATION_HTTP", row.line, "invalid quoted route path"); }
      if (!path.startsWith("/") || path.startsWith("//") || /[\s\\?#\u0000-\u001f\u007f]/.test(path)) {
        fail("INTEGRATION_HTTP", row.line, "route must be a local absolute path without query, fragment or control characters");
      }
      return { ...located, kind: "inbound-endpoint", protocol: { kind: "HTTP", method: http![1]!, path, source_line: row.line },
        request: reference(1, "request"), operation: reference(2, "operation"), response: reference(3, "response") };
    }
    if (section.kind === "outbound-call") {
      if (rows.length !== 4 && rows.length !== 5) fail("INTEGRATION_PATH", section.line, "outbound call requires four clauses and optionally one decision map");
      return { ...located, kind: "outbound-call", operation: reference(0, "operation"), request: reference(1, "request"),
        external_api: reference(2, "external-api"), response: reference(3, "response"),
        decision_mapping: rows.length === 5 ? reference(4, "map") : null };
    }
    if (section.kind === "outbound-write") {
      count(10);
      const operation = reference(0, "operation");
      const boundary = reference(1, "interface");
      const write = reference(2, "write");
      const inspect = reference(3, "inspect");
      const request_mapping = reference(4, "request-map");
      const inspect_request_mapping = reference(5, "inspect-request-map");
      const response_mapping = reference(6, "response-map");
      for (const [index, expected] of [[7, "on-unknown inspect"], [8, "on-unresolved pending"], [9, "on-conflict reject"]] as const) {
        const row = rowAt(index); level(row, false);
        if (row.text !== expected) fail("INTEGRATION_WRITE_OUTCOME", row.line, `expected ${expected}`);
      }
      if (write.ref === inspect.ref) fail("INTEGRATION_WRITE_PAIR", inspect.source_line, "write and inspect must select distinct Interface members");
      return { ...located, kind: "outbound-write", operation, interface: boundary, write, inspect,
        request_mapping, inspect_request_mapping, response_mapping,
        on_unknown: { action: "inspect", source_line: rowAt(7).line },
        on_unresolved: { action: "pending", source_line: rowAt(8).line },
        on_conflict: { action: "reject", source_line: rowAt(9).line } };
    }
    const entity = reference(0, "stores", false);
    const queries: IntegrationReference[] = []; const operations: IntegrationReference[] = [];
    let transaction: ApplicationPersistence["transaction"] | undefined;
    for (const row of rows.slice(1)) {
      level(row, false);
      const match = new RegExp(`^(serves|accepts-writes-from) (${name})$`).exec(row.text);
      if (match) {
        const target = match[1] === "serves" ? queries : operations;
        if (target.some(r => r.ref === match[2])) fail("INTEGRATION_DUPLICATE", row.line, "duplicate integration reference");
        target.push({ ref: match[2]!, source_line: row.line });
      } else if (row.text === "transaction local" && !transaction) {
        transaction = { scope: "single-resource-local", source_line: row.line };
      } else fail("INTEGRATION_PERSISTENCE", row.line, "expected serves, accepts-writes-from or one transaction local clause");
    }
    if ((!queries.length && !operations.length) || !transaction) fail("INTEGRATION_PERSISTENCE", section.line, "persistence requires an explicit query or write operation and local transaction scope");
    return { ...located, kind: "persistence", entity, queries, operations, transaction: transaction! };
  });
}
