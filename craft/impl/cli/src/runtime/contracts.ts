import { canonicalJson, sha256 } from "../input/source-manifest.js";

export interface RuntimeStepV1 {
  readonly step_id: string;
  readonly selector: string;
  readonly input: Readonly<Record<string, unknown>>;
}

export interface RuntimeInvocationV1 {
  readonly schema_version: "domainspec.runtime-invocation/v1";
  readonly invocation_id: string;
  readonly provider: "in-memory-v1";
  readonly steps: readonly RuntimeStepV1[];
}

export interface RuntimeStepOutcomeV1 {
  readonly step_id: string;
  readonly selector: string;
  readonly meta_type_id: string;
  readonly kind: string;
  readonly output: unknown;
  readonly output_sha256: string;
}

export interface RuntimeCoverageV1 {
  readonly node_selectors: readonly string[];
  readonly meta_type_ids: readonly string[];
  readonly relationship_edge_ids: readonly string[];
  readonly relationship_ids: readonly string[];
  readonly complete_backend_types: boolean;
  readonly complete_backend_relationships: boolean;
}

export interface RuntimeReceiptV1 {
  readonly schema_version: "domainspec.runtime-receipt/v1";
  readonly invocation_id: string;
  readonly provider: "in-memory-v1";
  readonly project_id: string;
  readonly source_manifest_sha256: string;
  readonly compiled_certificate_sha256: string;
  readonly checked_interchange_sha256: string;
  readonly request_sha256: string;
  readonly outcomes: readonly RuntimeStepOutcomeV1[];
  readonly coverage: RuntimeCoverageV1;
  readonly authority_effect: "none";
  readonly receipt_sha256: string;
}

export class RuntimeContractError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) { super(message); this.name = "RuntimeContractError"; }
}

function fail(code: string, pointer: string, message: string): never { throw new RuntimeContractError(code, pointer, message); }
function object(value: unknown, pointer: string): Record<string, unknown> { if (value === null || typeof value !== "object" || Array.isArray(value)) fail("MTCLI_RUNTIME_SCHEMA", pointer, "expected object"); return value as Record<string, unknown>; }
function exact(value: unknown, keys: readonly string[], pointer: string): Record<string, unknown> { const item = object(value, pointer); if (JSON.stringify(Object.keys(item).sort()) !== JSON.stringify([...keys].sort())) fail("MTCLI_RUNTIME_SCHEMA", pointer, "unexpected or missing member"); return item; }
function id(value: unknown, pointer: string): string { if (typeof value !== "string" || !/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(value)) fail("MTCLI_RUNTIME_ID", pointer, "expected lowercase kebab-case identity"); return value; }
function selector(value: unknown, pointer: string): string { if (typeof value !== "string" || !/^[a-z][a-z0-9-]*:[a-z][a-z0-9-]*$/.test(value)) fail("MTCLI_RUNTIME_SELECTOR", pointer, "expected feature:node selector"); return value; }

export function decodeRuntimeInvocation(value: unknown): RuntimeInvocationV1 {
  const item = exact(value, ["schema_version", "invocation_id", "provider", "steps"], "$request");
  if (item.schema_version !== "domainspec.runtime-invocation/v1") fail("MTCLI_RUNTIME_SCHEMA", "/schema_version", "unsupported runtime invocation schema");
  if (item.provider !== "in-memory-v1") fail("MTCLI_RUNTIME_PROVIDER", "/provider", "unsupported runtime provider");
  if (!Array.isArray(item.steps) || item.steps.length === 0) fail("MTCLI_RUNTIME_SCHEMA", "/steps", "runtime invocation requires at least one step");
  const steps = item.steps.map((raw, index): RuntimeStepV1 => {
    const step = exact(raw, ["step_id", "selector", "input"], `/steps/${index}`);
    return Object.freeze({ step_id: id(step.step_id, `/steps/${index}/step_id`), selector: selector(step.selector, `/steps/${index}/selector`), input: Object.freeze(object(step.input, `/steps/${index}/input`)) });
  });
  if (new Set(steps.map(({ step_id }) => step_id)).size !== steps.length) fail("MTCLI_RUNTIME_DUPLICATE", "/steps", "step identities must be unique");
  return Object.freeze({ schema_version: "domainspec.runtime-invocation/v1", invocation_id: id(item.invocation_id, "/invocation_id"), provider: "in-memory-v1", steps: Object.freeze(steps) });
}

export function runtimeRequestSha256(request: RuntimeInvocationV1): string { return sha256(canonicalJson(request)); }
