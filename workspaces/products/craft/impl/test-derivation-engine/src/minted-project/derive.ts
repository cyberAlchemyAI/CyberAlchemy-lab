import { createHash } from "node:crypto";
import { readFileSync, statSync } from "node:fs";
import { resolve } from "node:path";

import {
  EVF_PATHS,
  fail,
  type EnforcesEdge,
  type ExactRef,
  type GeneratedObligation,
  type JsonRecord,
  type KeyDoorBindingContract,
  type KeyDoorInputSet,
  type KeyDoorRuntimeContract,
  type PredicateSource,
} from "./types.js";

export interface EvfS1Bundle {
  readonly predicate: PredicateSource;
  readonly fixtures: KeyDoorInputSet;
  readonly binding: KeyDoorBindingContract;
  readonly runtimeContract: KeyDoorRuntimeContract;
  readonly ospec: { readonly obligations: readonly GeneratedObligation[] };
}

export interface DerivationOverrides {
  readonly edge?: Readonly<{
    edge_id: string;
    relationship: string;
    source_node_id: string;
    target_node_id: string;
  }>;
  readonly signature?: Readonly<{
    source_type: string;
    target_type: string;
    direction: string;
    status: string;
  }>;
}

export function sha256Bytes(bytes: string | Buffer): string {
  return createHash("sha256").update(bytes).digest("hex");
}

export function exactRef(repoRoot: string, path: string): ExactRef {
  const absolute = resolve(repoRoot, path);
  const bytes = readFileSync(absolute);
  return { path, sha256: sha256Bytes(bytes), size_bytes: bytes.byteLength };
}

export function assertExactRef(
  repoRoot: string,
  ref: ExactRef,
  code: "BINDING_STALE" | "SOURCE_DIGEST_STALE" | "GENERATED_GRAPH_STALE",
): void {
  let observed: ExactRef;
  try {
    observed = exactRef(repoRoot, ref.path);
  } catch {
    fail(code, `missing exact ref ${ref.path}`);
  }
  if (observed.sha256 !== ref.sha256 || observed.size_bytes !== ref.size_bytes) {
    fail(code, `stale exact ref ${ref.path}`);
  }
}

function json(repoRoot: string, path: string): unknown {
  try {
    return JSON.parse(readFileSync(resolve(repoRoot, path), "utf8")) as unknown;
  } catch (error) {
    fail(
      "PREDICATE_SCHEMA_INVALID",
      `cannot load JSON ${path}: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
}

function object(value: unknown, label: string): JsonRecord {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    fail("PREDICATE_SCHEMA_INVALID", `${label} must be an object`);
  }
  return value as JsonRecord;
}

export function loadEvfS1Bundle(repoRoot: string): EvfS1Bundle {
  const predicateRaw = object(json(repoRoot, EVF_PATHS.predicate), "predicate source");
  if (
    predicateRaw.schema_version !== "evf.key-door-predicate-source/v1" ||
    predicateRaw.source_id !== "evf.key-door.predicate-source.v1" ||
    predicateRaw.swu_id !== "SWU-GCP-001"
  ) {
    fail("PREDICATE_SCHEMA_INVALID", "predicate source identity is invalid");
  }
  const authority = object(predicateRaw.authority, "predicate authority");
  if (
    authority.kind !== "owner-selectable-evf-local-semantic-source" ||
    authority.admission_basis !== "DEC-GCP-001-R1:option-a" ||
    authority.claim_ceiling !== "EVF-local-SWU-GCP-001-proof-only" ||
    authority.schema_validation_grants_authority !== false
  ) {
    fail("SEMANTIC_SOURCE_UNADMITTED", "predicate source is not the selected EVF-local option");
  }
  const predicateBody = object(predicateRaw.predicate, "predicate");
  if (!predicateBody.ast) fail("FORMAL_PREDICATE_MISSING", "predicate AST is absent");

  const fixtureRaw = object(json(repoRoot, EVF_PATHS.fixture), "fixture set");
  if (!Array.isArray(fixtureRaw.cases)) {
    fail("FIXTURE_INPUT_INVALID", "fixture cases are absent");
  }
  const bindingRaw = object(json(repoRoot, EVF_PATHS.binding), "binding");
  const runtimeRaw = object(json(repoRoot, EVF_PATHS.runtimeContract), "runtime contract");
  const ospecRaw = object(json(repoRoot, EVF_PATHS.ospec), "O_spec");
  if (!Array.isArray(ospecRaw.obligations)) {
    fail("OBLIGATION_COUNT_MISMATCH", "O_spec obligations are absent");
  }

  const binding = bindingRaw as unknown as KeyDoorBindingContract;
  assertExactRef(repoRoot, binding.predicate_ref, "BINDING_STALE");
  assertExactRef(repoRoot, binding.fixture_ref, "BINDING_STALE");
  assertExactRef(repoRoot, binding.runtime_contract_ref, "BINDING_STALE");
  assertExactRef(repoRoot, binding.ospec_ref, "BINDING_STALE");

  return {
    predicate: predicateRaw as unknown as PredicateSource,
    fixtures: fixtureRaw as unknown as KeyDoorInputSet,
    binding,
    runtimeContract: runtimeRaw as unknown as KeyDoorRuntimeContract,
    ospec: ospecRaw as unknown as { readonly obligations: readonly GeneratedObligation[] },
  };
}

function normalized(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(normalized).join(",")}]`;
  if (value !== null && typeof value === "object") {
    const record = value as JsonRecord;
    return `{${Object.keys(record)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${normalized(record[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

export function deriveEnforcesObligations(
  repoRoot: string,
  bundle = loadEvfS1Bundle(repoRoot),
  overrides: DerivationOverrides = {},
): readonly GeneratedObligation[] {
  const binding = bundle.binding;
  assertExactRef(repoRoot, binding.lineage_refs.relationship_registry, "SOURCE_DIGEST_STALE");
  assertExactRef(repoRoot, binding.lineage_refs.rule_source, "SOURCE_DIGEST_STALE");
  assertExactRef(repoRoot, binding.lineage_refs.generated_graph, "GENERATED_GRAPH_STALE");
  assertExactRef(repoRoot, binding.lineage_refs.generated_source_manifest, "GENERATED_GRAPH_STALE");

  const source = object(json(repoRoot, binding.lineage_refs.rule_source.path), "raw Rule source");
  const connections = Array.isArray(source.connections) ? source.connections : [];
  const rawConnection = connections.find(
    (item) => object(item, "raw connection").edge_id === binding.edge.edge_id,
  );
  if (!rawConnection) fail("EDGE_ENDPOINT_MISMATCH", "raw enforces edge is absent");
  const connection = object(rawConnection, "raw connection");
  const admittedEdge = overrides.edge ?? {
    edge_id: String(connection.edge_id),
    relationship: String(connection.type),
    source_node_id: String(source.node_id),
    target_node_id: String(connection.to),
  };
  if (
    admittedEdge.source_node_id === binding.edge.target_node_id &&
    admittedEdge.target_node_id === binding.edge.source_node_id
  ) {
    fail("EDGE_DIRECTION_MISMATCH", "enforces edge direction is reversed");
  }
  if (
    admittedEdge.edge_id !== binding.edge.edge_id ||
    admittedEdge.source_node_id !== binding.edge.source_node_id ||
    admittedEdge.target_node_id !== binding.edge.target_node_id
  ) {
    fail("EDGE_ENDPOINT_MISMATCH", "enforces edge endpoints do not match the admitted binding");
  }
  if (admittedEdge.relationship !== "enforces") {
    fail("RELATIONSHIP_SIGNATURE_MISMATCH", "edge does not use the enforces signature");
  }

  const registry = object(
    json(repoRoot, binding.lineage_refs.relationship_registry.path),
    "relationship registry",
  );
  const signatures = Array.isArray(registry.signatures) ? registry.signatures : [];
  const signatureRaw = signatures.find((item) => object(item, "signature").id === "enforces");
  if (!signatureRaw) fail("RELATIONSHIP_SIGNATURE_MISMATCH", "enforces signature is absent");
  const registrySignature = object(signatureRaw, "enforces signature");
  const signature = overrides.signature ?? {
    source_type: String(registrySignature.source_type),
    target_type: String(registrySignature.target_type),
    direction: String(registrySignature.direction),
    status: String(registrySignature.status),
  };
  if (
    signature.source_type !== "Rule" ||
    signature.target_type !== "Operation" ||
    signature.direction !== "canonical" ||
    signature.status !== "active" ||
    source.kind !== "Rule"
  ) {
    fail("RELATIONSHIP_SIGNATURE_MISMATCH", "enforces is not active Rule-to-Operation canonical");
  }

  const graph = object(json(repoRoot, binding.lineage_refs.generated_graph.path), "generated graph");
  const graphEdges = Array.isArray(graph.edges) ? graph.edges : [];
  const graphEdge = graphEdges.find((item) => object(item, "graph edge").edge_id === binding.edge.edge_id);
  if (!graphEdge) fail("GENERATED_GRAPH_STALE", "generated graph omits the admitted edge");
  const graphEdgeRecord = object(graphEdge, "graph edge");
  if (
    graphEdgeRecord.type !== "enforces" ||
    graphEdgeRecord.from !== binding.edge.source_node_id ||
    graphEdgeRecord.to !== binding.edge.target_node_id
  ) {
    fail("GENERATED_GRAPH_STALE", "generated graph edge differs from raw source");
  }
  const graphNodes = Array.isArray(graph.nodes) ? graph.nodes : [];
  const target = graphNodes.find((item) => object(item, "graph node").node_id === binding.edge.target_node_id);
  if (!target || object(target, "target node").kind !== "Operation") {
    fail("RELATIONSHIP_SIGNATURE_MISMATCH", "enforces target is not an Operation");
  }

  const manifest = object(
    json(repoRoot, binding.lineage_refs.generated_source_manifest.path),
    "source manifest",
  );
  const records = Array.isArray(manifest.records) ? manifest.records : [];
  const lineage = records.find((item) => {
    const entry = object(item, "manifest record");
    return entry.record_type === "edge" && entry.graph_id === binding.edge.edge_id;
  });
  if (!lineage) fail("GENERATED_GRAPH_STALE", "source manifest omits edge lineage");
  const lineageRecord = object(lineage, "edge lineage");
  if (
    lineageRecord.source_digest !== binding.lineage_refs.rule_source.sha256 ||
    !binding.lineage_refs.rule_source.path.endsWith(String(lineageRecord.source_path))
  ) {
    fail("SOURCE_DIGEST_STALE", "source manifest does not join to the raw Rule bytes");
  }

  const obligation: GeneratedObligation = {
    obligation_id: "evf.s1.enforces.has-key.unlock-door.v1",
    edge_id: binding.edge.edge_id,
    relationship: "enforces",
    source_node_id: binding.edge.source_node_id,
    target_node_id: binding.edge.target_node_id,
    predicate_id: bundle.predicate.predicate.predicate_id,
    binding_id: binding.binding_id,
  };
  const generated = [obligation] as const;
  if (generated.length !== 1) fail("OBLIGATION_COUNT_MISMATCH", "O_gen must contain exactly one obligation");
  if (bundle.ospec.obligations.length !== 1) {
    fail("OBLIGATION_COUNT_MISMATCH", "O_spec must contain exactly one obligation");
  }
  if (bundle.ospec.obligations[0]?.obligation_id !== obligation.obligation_id) {
    fail("OBLIGATION_ID_MISMATCH", "O_spec and O_gen obligation identities differ");
  }
  if (normalized(bundle.ospec.obligations) !== normalized(generated)) {
    fail("OSPEC_OGEN_MISMATCH", "O_spec and O_gen are not exact-set equal");
  }
  return generated;
}

export function assertRuntimeSourcePresent(repoRoot: string, binding: KeyDoorBindingContract): ExactRef {
  const path = binding.runtime_source_binding.path;
  try {
    const stat = statSync(resolve(repoRoot, path));
    if (!stat.isFile()) fail("RUNTIME_TARGET_UNADMITTED", "runtime binding is not a file");
  } catch {
    fail("RUNTIME_TARGET_UNADMITTED", `runtime source is absent: ${path}`);
  }
  return exactRef(repoRoot, path);
}
