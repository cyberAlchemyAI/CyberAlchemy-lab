import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { digestValue, sha256, utf16Compare } from "./canonical-json.js";
import { exactRef, readJson } from "./exact-ref.js";
import { isSelectedPredicate, validateProperty } from "./property.js";
import {
  fail,
  type EdgeFact,
  type FactProjection,
  type MintedGraph,
  type NodeFact,
  type PropertyDefinition,
  type SourceManifest,
} from "./types.js";

export const REQUEST_ID =
  "evf.l2.financial-settlement.rule-to-payout-event-reachability.request.v1";

export const L2_PATHS = {
  graph:
    "projects/domainspec-v2/impl/spec/features/financial-settlement/generated/graph.json",
  graphSchema:
    "projects/domainspec-v2/impl/spec/minted-project/graph.schema.json",
  sourceManifest:
    "projects/domainspec-v2/impl/spec/features/financial-settlement/generated/source-manifest.json",
  sourceManifestSchema:
    "projects/domainspec-v2/impl/spec/minted-project/source-manifest.schema.json",
  featureRoot:
    "projects/domainspec-v2/impl/spec/features/financial-settlement",
  project:
    "projects/domainspec-v2/impl/spec/features/financial-settlement/project.json",
  profile:
    "projects/domainspec-v2/impl/spec/sfol-profile/minted-project-profile.json",
  kinds: "projects/domainspec-v2/definitions/meta-types/meta-types.yml",
  relationships:
    "projects/domainspec-v2/definitions/relationships/relationships.yml",
  l1Receipt:
    "projects/domainspec-v2/development/evolvable-validation-framework/evidence/L1-GCP-COMPOSITE/attempt-001/composite-validation-receipt.json",
  property:
    "projects/domainspec-v2/development/evolvable-validation-framework/contracts/rule-to-payout-event-reachability.v1.json",
  comparison:
    "projects/domainspec-v2/development/evolvable-validation-framework/contracts/reachability-comparison.v1.json",
  canonicalization:
    "projects/domainspec-v2/development/evolvable-validation-framework/contracts/evf-canonical-json.v1.json",
  scope:
    "projects/domainspec-v2/development/evolvable-validation-framework/contracts/exact-instance-scope.v1.json",
  runtimeManifest:
    "projects/domainspec-v2/development/evolvable-validation-framework/contracts/provider-runtime-manifest.v1.json",
} as const;

function compareNode(left: NodeFact, right: NodeFact): number {
  return (
    utf16Compare(left.node_id, right.node_id) ||
    utf16Compare(left.feature_id, right.feature_id) ||
    utf16Compare(left.kind, right.kind)
  );
}

function compareEdge(left: EdgeFact, right: EdgeFact): number {
  return (
    utf16Compare(left.edge_id, right.edge_id) ||
    utf16Compare(left.predicate, right.predicate) ||
    utf16Compare(left.from, right.from) ||
    utf16Compare(left.to, right.to)
  );
}

function assertUnique(values: readonly string[], kind: "node" | "edge"): void {
  if (new Set(values).size !== values.length) {
    fail(
      kind === "node" ? "FACT_NODE_ID_DUPLICATE" : "FACT_EDGE_ID_DUPLICATE",
      "projection",
      `duplicate ${kind} identity`,
    );
  }
}

export function extractFacts(
  graph: MintedGraph,
  inputProperty: PropertyDefinition,
  requestId = REQUEST_ID,
): FactProjection {
  const property = validateProperty(inputProperty);
  if (
    graph.schema_version !== "minted-graph/v1" ||
    graph.authority !== "generated-semantic-read-model" ||
    graph.project_id !== "financial-settlement"
  ) {
    fail("GRAPH_AUTHORITY_MISMATCH", "projection", "graph identity or authority is invalid");
  }
  assertUnique(graph.nodes.map((node) => node.node_id), "node");
  assertUnique(graph.edges.map((edge) => edge.edge_id), "edge");

  const nodeIds = new Set(graph.nodes.map((node) => node.node_id));
  for (const edge of graph.edges) {
    if (!nodeIds.has(edge.from) || !nodeIds.has(edge.to)) {
      fail("FACT_ENDPOINT_MISSING", "projection", `edge endpoint missing: ${edge.edge_id}`);
    }
  }

  const nodes = graph.nodes
    .map(({ node_id, feature_id, kind }) => ({ node_id, feature_id, kind }))
    .sort(compareNode);
  const edges = graph.edges
    .map(({ edge_id, type, from, to }) => ({
      edge_id,
      predicate: type,
      from,
      to,
    }))
    .sort(compareEdge);
  const factsDigest = digestValue({ nodes, edges });
  const universe = nodes.map((node) => node.node_id);
  const universeDigest = digestValue(universe);
  const selected = edges
    .filter((edge) => isSelectedPredicate(edge.predicate))
    .map((edge) => [edge.from, edge.to] as const);
  const selectedKeys = new Set(selected.map(([from, to]) => `${from}\u0000${to}`));
  const selectedEdges = [...selectedKeys]
    .map((key) => key.split("\u0000") as [string, string])
    .sort((left, right) => utf16Compare(left[0], right[0]) || utf16Compare(left[1], right[1]));
  const atomMap = Object.fromEntries(universe.map((id, index) => [id, `N${index}`]));
  const scopeDigest = digestValue({
    request_id: requestId,
    facts_digest: factsDigest,
    universe_digest: universeDigest,
    selected_relation_digest: property.selected_relation_digest,
    canonical_atom_map: atomMap,
    canonical_selected_edge_tuples: selectedEdges,
  });
  return {
    nodes,
    edges,
    facts_digest: factsDigest,
    universe_digest: universeDigest,
    selected_edges: selectedEdges,
    selected_relation_digest: property.selected_relation_digest,
    scope_digest: scopeDigest,
    atom_map: atomMap,
  };
}

export function validateLiveSourceBindings(repoRoot: string): {
  readonly graph: MintedGraph;
  readonly manifest: SourceManifest;
  readonly property: PropertyDefinition;
} {
  const graph = readJson<MintedGraph>(repoRoot, L2_PATHS.graph);
  const manifest = readJson<SourceManifest>(repoRoot, L2_PATHS.sourceManifest);
  const property = readJson<PropertyDefinition>(repoRoot, L2_PATHS.property);
  if (
    manifest.schema_version !== "minted-source-manifest/v1" ||
    manifest.authority !== "generated-provenance-read-model" ||
    manifest.project_id !== graph.project_id ||
    manifest.source_set_digest !== graph.source_set_digest
  ) {
    fail("SOURCE_MANIFEST_MISSING", "admission", "source manifest does not join the graph", 2);
  }
  for (const input of manifest.inputs) {
    const absolute = resolve(repoRoot, L2_PATHS.featureRoot, input.path);
    if (sha256(readFileSync(absolute)) !== input.digest) {
      fail("SOURCE_DIGEST_STALE", "admission", `source input drift: ${input.path}`, 2);
    }
  }
  const profile = exactRef(repoRoot, L2_PATHS.profile);
  const kinds = exactRef(repoRoot, L2_PATHS.kinds);
  const relationships = exactRef(repoRoot, L2_PATHS.relationships);
  if (
    graph.language.profile_digest !== profile.sha256 ||
    graph.language.kinds_digest !== kinds.sha256 ||
    graph.language.relationships_digest !== relationships.sha256
  ) {
    fail("REGISTRY_DIGEST_STALE", "admission", "graph registry binding is stale", 2);
  }
  validateProperty(property);
  return { graph, manifest, property };
}
