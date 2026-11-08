import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  buildMintedProjectViews,
  verifyMintedProjectBuild,
} from "../../../tools/minted-project/views.js";
import type { MintedSourceManifest } from "../../../tools/minted-project/compiler.js";
import {
  BACKEND_KINDS,
  BACKEND_RELATIONSHIPS,
  collectDevelopmentProjectDiagnostics,
  type BackendKind,
  type BackendRelationship,
  type DevelopmentProject,
} from "./development-engine.js";

const implRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
const projectRoot = resolve(implRoot, "spec/features/financial-settlement");
const generatedRoot = resolve(projectRoot, "generated-current-20261002");
const profileRegistry = resolve(implRoot, "spec/sfol-profile/minted-project-profile.json");

function requireCondition(condition: unknown, code: string): asserts condition {
  if (!condition) throw new Error(`BTE_CURRENT_SOURCE_INVALID:${code}`);
}

function anchor(
  manifest: MintedSourceManifest,
  recordType: "node" | "edge",
  graphId: string,
): string {
  const matching = manifest.records.filter(
    (record) => record.record_type === recordType && record.graph_id === graphId,
  );
  requireCondition(matching.length === 1, `manifest-record:${recordType}:${graphId}`);
  const record = matching[0]!;
  requireCondition(
    manifest.inputs.some(
      (input) => input.path === record.source_path && input.digest === record.source_digest,
    ),
    `manifest-input:${recordType}:${graphId}`,
  );
  return `${record.source_path}@${record.source_digest}#${recordType}:${graphId}`;
}

/**
 * Adapts only the currently authored financial-settlement graph into BTE's
 * declared-subset structural profile. It does not verify application effects.
 */
export function createCurrentFinancialSettlementDevelopmentProject(): DevelopmentProject {
  const minted = buildMintedProjectViews(projectRoot, {
    developmentProfileRegistry: {
      path: profileRegistry,
      handle: "sfol-development-explicit-v0.1",
    },
  });
  const verification = verifyMintedProjectBuild(projectRoot, minted);
  requireCondition(
    verification.status === "pass",
    `minted-build:${verification.codes.join(",")}`,
  );
  requireCondition(
    minted.graphBytes === readFileSync(resolve(generatedRoot, "graph.json"), "utf8"),
    "generated-graph-drift",
  );
  requireCondition(
    minted.sourceManifestBytes ===
      readFileSync(resolve(generatedRoot, "source-manifest.json"), "utf8"),
    "generated-source-manifest-drift",
  );

  const { graph, sourceManifest } = minted;
  requireCondition(
    sourceManifest.records.length === graph.nodes.length + graph.edges.length,
    "manifest-denominator",
  );
  const nodes = graph.nodes.map((node) => {
    requireCondition(
      BACKEND_KINDS.includes(node.kind as BackendKind),
      `unsupported-kind:${node.node_id}:${node.kind}`,
    );
    return {
      ...node,
      kind: node.kind as BackendKind,
      source_anchor: anchor(sourceManifest, "node", node.node_id),
    };
  });
  const edges = graph.edges.map((edge) => {
    requireCondition(
      BACKEND_RELATIONSHIPS.includes(edge.type as BackendRelationship),
      `unsupported-relationship:${edge.edge_id}:${edge.type}`,
    );
    return {
      edge_id: edge.edge_id,
      family: edge.type as BackendRelationship,
      from: edge.from,
      to: edge.to,
      source_anchor: anchor(sourceManifest, "edge", edge.edge_id),
    };
  });
  const project: DevelopmentProject = {
    schema_version: "bte-development-project/v1",
    project_id: graph.project_id,
    profile_id: "feature-with-independent-node-and-edge-files@1-dev",
    coverage_mode: "declared-subset",
    nodes,
    edges,
  };
  const diagnostics = collectDevelopmentProjectDiagnostics(project);
  requireCondition(
    diagnostics.result === "pass",
    `development-project:${diagnostics.diagnostics.map(({ code }) => code).join(",")}`,
  );
  return project;
}
