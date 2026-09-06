import crypto from "node:crypto";

import type { CompiledProjectGraph } from "../input/project-model.js";
import { canonicalJson } from "../input/source-manifest.js";

const SHA256_PATTERN = /^[a-f0-9]{64}$/;

export interface FormalizationSourceIdentity {
  readonly project_id: string;
  readonly source_manifest_sha256: string;
  readonly source_bytes_sha256: string;
}

export interface GraphBoundCertificate {
  readonly graph_sha256: string;
  readonly source_identity: FormalizationSourceIdentity;
}

export interface TypeScriptProjectionPayload {
  readonly project_id: string;
  readonly source_manifest_sha256: string;
  readonly source_bytes_sha256: string;
  readonly graph_sha256: string;
}

export interface CompilerRefinementOutput {
  readonly schema_version: "domainspec.compiler-refinement-output/v1-candidate";
  readonly certificate: GraphBoundCertificate;
  readonly typescript_projection: TypeScriptProjectionPayload;
  readonly authority_effect: "none";
}

export interface ClosedCompilerGraphProjection<Node, Edge> {
  readonly nodes: readonly Node[];
  readonly edges: readonly Edge[];
}

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
  const certificate = Object.freeze({ graph_sha256: graphSha256, source_identity: sourceIdentity });
  return Object.freeze({
    schema_version: "domainspec.compiler-refinement-output/v1-candidate",
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
