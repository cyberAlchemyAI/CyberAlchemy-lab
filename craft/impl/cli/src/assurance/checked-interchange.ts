import type { CompiledProjectGraph } from "../input/project-model.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import {
  createCompiledProjectCertificate,
  createCompiledSemanticGraph,
  validateCompiledProjectCertificate,
  type CompiledProjectCertificateV1,
} from "../compilation/certificate.js";
import {
  createMetaTypeFormalizationProjection,
  type FormalizationRenderPayload,
} from "../formalization/projection.js";

export interface CheckedInterchangeV1 {
  readonly schema_version: "domainspec.checked-interchange/v1-candidate";
  readonly project_id: string;
  readonly source_identity: Readonly<{
    readonly source_manifest_sha256: string;
    readonly source_bytes_sha256: string;
  }>;
  readonly compiled_graph: Omit<CompiledProjectGraph, "project_root">;
  readonly compiled_certificate: CompiledProjectCertificateV1;
  readonly formalization_payload: FormalizationRenderPayload;
  readonly denominators: Readonly<{
    readonly node_count: number;
    readonly edge_count: number;
    readonly obligation_count: number;
    readonly applicable_witness_count: number;
  }>;
  readonly claim_scope: "exact-finite-compiled-project-projection";
  readonly authority_effect: "none";
  readonly interchange_sha256: string;
}

export class CheckedInterchangeError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(message);
    this.name = "CheckedInterchangeError";
  }
}

function fail(code: string, pointer: string, message: string): never {
  throw new CheckedInterchangeError(code, pointer, message);
}

function isObject(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function exactKeys(value: unknown, keys: readonly string[], pointer: string): asserts value is Record<string, unknown> {
  if (!isObject(value)) fail("MTCLI_INTERCHANGE_SCHEMA", pointer, "expected object");
  const actual = Object.keys(value).sort();
  const expected = [...keys].sort();
  if (canonicalJson(actual) !== canonicalJson(expected)) fail("MTCLI_INTERCHANGE_SCHEMA", pointer, "unexpected or missing member");
}

function requireSha256(value: unknown, pointer: string): asserts value is string {
  if (typeof value !== "string" || !/^[a-f0-9]{64}$/.test(value)) fail("MTCLI_INTERCHANGE_SCHEMA", pointer, "expected SHA-256");
}

function body(value: Omit<CheckedInterchangeV1, "interchange_sha256">): Omit<CheckedInterchangeV1, "interchange_sha256"> {
  return value;
}

export function createCheckedInterchange(graph: CompiledProjectGraph): CheckedInterchangeV1 {
  const projection = createMetaTypeFormalizationProjection(graph);
  const candidate = body({
    schema_version: "domainspec.checked-interchange/v1-candidate",
    project_id: graph.project_id,
    source_identity: Object.freeze({
      source_manifest_sha256: graph.source_manifest.manifest_sha256,
      source_bytes_sha256: graph.source_manifest.aggregate_sha256,
    }),
    compiled_graph: createCompiledSemanticGraph(graph),
    compiled_certificate: createCompiledProjectCertificate(graph),
    formalization_payload: projection.render_payload,
    denominators: Object.freeze({
      node_count: graph.nodes.length,
      edge_count: graph.relationships.length,
      obligation_count: projection.obligation_catalog.length,
      applicable_witness_count: projection.applicable_witnesses.length,
    }),
    claim_scope: "exact-finite-compiled-project-projection",
    authority_effect: "none",
  });
  return Object.freeze({ ...candidate, interchange_sha256: sha256(canonicalJson(candidate)) });
}

export function validateCheckedInterchange(value: unknown, graph: CompiledProjectGraph): CheckedInterchangeV1 {
  exactKeys(value, ["schema_version", "project_id", "source_identity", "compiled_graph", "compiled_certificate", "formalization_payload", "denominators", "claim_scope", "authority_effect", "interchange_sha256"], "$");
  if (value.schema_version !== "domainspec.checked-interchange/v1-candidate") fail("MTCLI_INTERCHANGE_SCHEMA", "/schema_version", "unsupported checked interchange");
  if (value.project_id !== graph.project_id) fail("MTCLI_INTERCHANGE_SOURCE", "/project_id", "project identity does not match compiled graph");
  exactKeys(value.source_identity, ["source_manifest_sha256", "source_bytes_sha256"], "/source_identity");
  if (value.source_identity.source_manifest_sha256 !== graph.source_manifest.manifest_sha256) fail("MTCLI_INTERCHANGE_SOURCE", "/source_identity/source_manifest_sha256", "source manifest identity drifted");
  if (value.source_identity.source_bytes_sha256 !== graph.source_manifest.aggregate_sha256) fail("MTCLI_INTERCHANGE_SOURCE", "/source_identity/source_bytes_sha256", "source byte identity drifted");
  exactKeys(value.denominators, ["node_count", "edge_count", "obligation_count", "applicable_witness_count"], "/denominators");
  if (value.claim_scope !== "exact-finite-compiled-project-projection" || value.authority_effect !== "none") fail("MTCLI_INTERCHANGE_AUTHORITY", "/claim_scope", "interchange claim or authority grew");
  requireSha256(value.interchange_sha256, "/interchange_sha256");

  const expected = createCheckedInterchange(graph);
  validateCompiledProjectCertificate(graph, value.compiled_certificate as unknown as CompiledProjectCertificateV1);
  const { interchange_sha256: ignored, ...candidateBody } = value;
  if (sha256(canonicalJson(candidateBody)) !== value.interchange_sha256) fail("MTCLI_INTERCHANGE_DIGEST", "/interchange_sha256", "interchange digest is stale");
  if (canonicalJson(value.formalization_payload) !== canonicalJson(expected.formalization_payload)) fail("MTCLI_INTERCHANGE_PROJECTION", "/formalization_payload", "node, edge, obligation, predicate, or witness projection drifted");
  if (canonicalJson(value.denominators) !== canonicalJson(expected.denominators)) fail("MTCLI_INTERCHANGE_DENOMINATOR", "/denominators", "projection denominator drifted");
  if (canonicalJson(value) !== canonicalJson(expected)) fail("MTCLI_INTERCHANGE_EXACT", "$", "checked interchange differs from the compiled graph projection");
  return value as unknown as CheckedInterchangeV1;
}
