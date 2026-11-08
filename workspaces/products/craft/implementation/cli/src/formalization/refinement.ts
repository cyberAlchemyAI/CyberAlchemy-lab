import crypto from "node:crypto";

import type { CompiledProjectGraph } from "../input/project-model.js";
import { canonicalJson } from "../input/source-manifest.js";
import { FROZEN_META_TYPE_CATALOG } from "../meta-types/catalog.js";
import { RELATIONSHIP_AUTHORITY_SHA256 } from "../relationships/authority.js";
import { CLI_PACKAGE_NAME, CLI_VERSION, SUPPORTED_NODE_VERSION } from "../version.js";

const SHA256_PATTERN = /^[a-f0-9]{64}$/;

export interface FormalizationSourceIdentity {
  readonly project_id: string;
  readonly source_manifest_sha256: string;
  readonly source_bytes_sha256: string;
}

export interface GraphBoundCertificate {
  readonly schema_version: "domainspec.graph-bound-certificate/v2";
  readonly graph_sha256: string;
  readonly source_identity: FormalizationSourceIdentity;
  readonly denominators: Readonly<{
    readonly node_count: number;
    readonly edge_count: number;
    readonly backend_meta_type_count: 13;
    readonly backend_relationship_count: 17;
    readonly applicable_obligation_count: number;
    readonly witness_count: number;
  }>;
  readonly applicable_obligation_ids: readonly string[];
  readonly witness_outcomes: readonly Readonly<{
    readonly witness_id: string;
    readonly obligation_id: string;
    readonly family: string;
    readonly outcome: "pass";
  }>[];
  readonly compiler: Readonly<{
    readonly package_name: typeof CLI_PACKAGE_NAME;
    readonly package_version: typeof CLI_VERSION;
    readonly supported_node_version: typeof SUPPORTED_NODE_VERSION;
    readonly baseline_id: string;
    readonly baseline_digest: string;
    readonly relationship_authority_sha256: string;
  }>;
  readonly authority_ceiling: "evidence-only-no-admission-acceptance-publication-release-deployment-or-external-effect";
}

export interface TypeScriptProjectionPayload {
  readonly project_id: string;
  readonly source_manifest_sha256: string;
  readonly source_bytes_sha256: string;
  readonly graph_sha256: string;
}

export interface CompilerRefinementOutput {
  readonly schema_version: "domainspec.compiler-refinement-output/v1";
  readonly certificate: GraphBoundCertificate;
  readonly typescript_projection: TypeScriptProjectionPayload;
  readonly authority_effect: "none";
}

export interface ClosedCompilerGraphProjection<Node, Edge> {
  readonly nodes: readonly Node[];
  readonly edges: readonly Edge[];
}

export class CompilerRefinementError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, message: string) { super(message); this.name = "CompilerRefinementError"; }
}

function fail(code: string, message: string): never { throw new CompilerRefinementError(code, message); }

export function sha256(text: string): string {
  return crypto.createHash("sha256").update(text).digest("hex");
}

function requireSha256(value: string, field: string): void {
  if (!SHA256_PATTERN.test(value)) throw new Error(`invalid SHA-256 for ${field}`);
}

export function createCompilerRefinementOutput<Node, Edge>(
  graph: CompiledProjectGraph,
  projectedGraph: ClosedCompilerGraphProjection<Node, Edge>,
): CompilerRefinementOutput {
  const projectedGraphBody = Object.freeze({
    project_id: graph.project_id,
    source_manifest_sha256: graph.source_manifest.manifest_sha256,
    source_bytes_sha256: graph.source_manifest.aggregate_sha256,
    nodes: projectedGraph.nodes,
    edges: projectedGraph.edges,
    obligation_applicability: graph.obligation_applicability,
    obligation_outcomes: graph.obligation_outcomes,
  });
  const graphSha256 = sha256(canonicalJson(projectedGraphBody));
  requireSha256(graphSha256, "graph_sha256");
  requireSha256(graph.source_manifest.manifest_sha256, "source_manifest_sha256");
  requireSha256(graph.source_manifest.aggregate_sha256, "source_bytes_sha256");
  const sourceIdentity = Object.freeze({
    project_id: graph.project_id,
    source_manifest_sha256: graph.source_manifest.manifest_sha256,
    source_bytes_sha256: graph.source_manifest.aggregate_sha256,
  });
  const applicableObligationIds = Object.freeze(graph.obligation_applicability.filter(({ classification }) => classification === "applicable").map(({ obligation_id }) => obligation_id).sort());
  const witnessOutcomes = Object.freeze(graph.obligation_outcomes.map((outcome) => Object.freeze({ ...outcome })).sort((left, right) => left.witness_id.localeCompare(right.witness_id)));
  const certificate = Object.freeze({
    schema_version: "domainspec.graph-bound-certificate/v2" as const,
    graph_sha256: graphSha256,
    source_identity: sourceIdentity,
    denominators: Object.freeze({
      node_count: graph.nodes.length,
      edge_count: graph.relationships.length,
      backend_meta_type_count: 13 as const,
      backend_relationship_count: 17 as const,
      applicable_obligation_count: applicableObligationIds.length,
      witness_count: witnessOutcomes.length,
    }),
    applicable_obligation_ids: applicableObligationIds,
    witness_outcomes: witnessOutcomes,
    compiler: Object.freeze({
      package_name: CLI_PACKAGE_NAME,
      package_version: CLI_VERSION,
      supported_node_version: SUPPORTED_NODE_VERSION,
      baseline_id: FROZEN_META_TYPE_CATALOG.baseline_id,
      baseline_digest: FROZEN_META_TYPE_CATALOG.baseline_digest,
      relationship_authority_sha256: RELATIONSHIP_AUTHORITY_SHA256,
    }),
    authority_ceiling: "evidence-only-no-admission-acceptance-publication-release-deployment-or-external-effect" as const,
  });
  return Object.freeze({
    schema_version: "domainspec.compiler-refinement-output/v1",
    certificate,
    typescript_projection: Object.freeze({
      project_id: sourceIdentity.project_id,
      source_manifest_sha256: sourceIdentity.source_manifest_sha256,
      source_bytes_sha256: sourceIdentity.source_bytes_sha256,
      graph_sha256: graphSha256,
    }),
    authority_effect: "none",
  });
}

export function validateGraphBoundCertificate<Node, Edge>(
  graph: CompiledProjectGraph,
  projectedGraph: ClosedCompilerGraphProjection<Node, Edge>,
  certificate: GraphBoundCertificate,
): GraphBoundCertificate {
  const expected = createCompilerRefinementOutput(graph, projectedGraph).certificate;
  if (canonicalJson(certificate) !== canonicalJson(expected)) fail("MTCLI_GRAPH_CERTIFICATE", "graph-bound certificate is incomplete, stale, or does not match the compiled graph");
  return certificate;
}
