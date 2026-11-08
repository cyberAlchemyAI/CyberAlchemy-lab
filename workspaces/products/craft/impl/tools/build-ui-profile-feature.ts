#!/usr/bin/env tsx

import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, relative, resolve } from "node:path";

import { buildMintedProjectViews, verifyMintedProjectBuild } from "./minted-project/views";

type JsonRecord = Record<string, any>;

const args = process.argv.slice(2);
const implRoot = resolve(new URL("..", import.meta.url).pathname);
const projectRoot = resolve(
  process.cwd(),
  getArg("--project") ?? "spec/features/ui-profile-create-player",
);
const registryPath = resolve(
  process.cwd(),
  getArg("--registry") ?? "spec/ui-profile/minted-project-profile.json",
);
const handle = getArg("--handle") ?? "ui-development-explicit-v0.1";
const outRoot = resolve(projectRoot, getArg("--out") ?? "generated");

if (outRoot === projectRoot || relative(projectRoot, outRoot).startsWith("..")) {
  throw new Error("UI_PROFILE_OUTPUT_INVALID: generated output must remain below the feature project");
}

const options = {
  developmentProfileRegistry: { path: registryPath, handle },
};
const first = buildMintedProjectViews(projectRoot, options);
const second = buildMintedProjectViews(projectRoot, options);
for (const key of [
  "graphBytes",
  "sourceManifestBytes",
  "markdownBytes",
  "markdownViewBytes",
  "buildReceiptBytes",
] as const) {
  if (first[key] !== second[key]) {
    throw new Error(`UI_PROFILE_NONDETERMINISTIC:${key}`);
  }
}
const verification = verifyMintedProjectBuild(projectRoot, first);
if (verification.status !== "pass") {
  throw new Error(`UI_PROFILE_VERIFICATION_FAILED:${verification.codes.join(",")}`);
}

const traceability = json(resolve(projectRoot, "traceability.json"));
const residueSource = json(resolve(projectRoot, "residue.json"));
const graphDigest = sha256(first.graphBytes);
const traversal = buildTraversal(first.graph, traceability, projectRoot, graphDigest);
const residue = {
  schema_version: "domainspec-ui-generated-residue/v0.1",
  authority: "generated-development-read-model",
  graph_digest: graphDigest,
  source_digest: sha256(readFileSync(resolve(projectRoot, "residue.json"))),
  items: residueSource.items,
};

rmSync(outRoot, { recursive: true, force: true });
mkdirSync(resolve(outRoot, "nodes"), { recursive: true });
const artifacts: Array<[string, string]> = [
  ["graph.json", first.graphBytes],
  ["source-manifest.json", first.sourceManifestBytes],
  ["SPEC.md", first.markdownBytes],
  ["markdown-view.json", first.markdownViewBytes],
  ["build-receipt.json", first.buildReceiptBytes],
  ["traversal.json", bytes(traversal)],
  ["residue.json", bytes(residue)],
];
for (const [path, content] of artifacts) {
  write(resolve(outRoot, path), content);
}
for (const node of first.graph.nodes) {
  const outgoing = first.graph.edges.filter((edge) => edge.from === node.node_id);
  const incoming = first.graph.edges.filter((edge) => edge.to === node.node_id);
  write(
    resolve(outRoot, "nodes", `${slug(node.node_id.split(".").at(-1) ?? node.node_id)}.json`),
    bytes({
      schema_version: "domainspec-ui-generated-node/v0.1",
      authority: "generated-development-read-model",
      graph_digest: graphDigest,
      node,
      outgoing_edges: outgoing,
      incoming_edges: incoming,
    }),
  );
}

console.log(
  JSON.stringify(
    {
      status: "PASS",
      project_id: first.graph.project_id,
      profile_handle: handle,
      graph_digest: `sha256:${graphDigest}`,
      nodes: first.graph.nodes.length,
      edges: first.graph.edges.length,
      generated_node_records: first.graph.nodes.length,
      required_concepts: traversal.required_coverage.length,
      orphan_required_concepts: traversal.orphan_required_concepts,
      residue: residue.items.length,
      output: relative(implRoot, outRoot).replaceAll("\\", "/"),
    },
    null,
    2,
  ),
);

function buildTraversal(
  graph: typeof first.graph,
  trace: JsonRecord,
  root: string,
  graphDigest: string,
): JsonRecord {
  const byId = new Map(graph.nodes.map((node) => [node.node_id, node]));
  const pageRoots = graph.nodes.filter((node) => node.kind === "Page").map((node) => node.node_id);
  const backendRoots = graph.nodes
    .filter((node) => ["Operation", "Query", "Interface"].includes(node.kind))
    .map((node) => node.node_id)
    .sort();
  const roots = [...pageRoots, ...backendRoots];
  const traversals = roots.map((nodeId) => ({
    root: nodeId,
    kind: byId.get(nodeId)?.kind,
    outgoing_reachable: reachable(graph, nodeId, false),
    connected_reachable: reachable(graph, nodeId, true),
  }));
  const requiredCoverage = (trace.concepts as JsonRecord[]).map((concept) => {
    const records = concept.records as string[];
    const graphRecords = records.filter((record) => byId.has(record));
    const representationRecords = records.filter((record) => !byId.has(record));
    const handles = representationRecords.map((record) => ({
      path: record,
      digest: sha256(readFileSync(resolve(root, record))),
    }));
    return {
      concept_id: concept.id,
      term: concept.term,
      representation: concept.representation,
      graph_records: graphRecords,
      representation_handles: handles,
      covered: graphRecords.length > 0 || handles.length > 0,
    };
  });
  return {
    schema_version: "domainspec-ui-traversal/v0.1",
    authority: "generated-development-read-model",
    graph_digest: graphDigest,
    traversal_semantics: {
      outgoing_reachable: "follow canonical edge direction",
      connected_reachable: "follow canonical edges in either direction for learning-map connectivity",
    },
    roots: traversals,
    required_coverage: requiredCoverage,
    orphan_required_concepts: requiredCoverage
      .filter((entry) => !entry.covered)
      .map((entry) => entry.concept_id),
  };
}

function reachable(graph: typeof first.graph, root: string, undirected: boolean): string[] {
  const adjacency = new Map<string, Set<string>>();
  for (const node of graph.nodes) adjacency.set(node.node_id, new Set());
  for (const edge of graph.edges) {
    adjacency.get(edge.from)?.add(edge.to);
    if (undirected) adjacency.get(edge.to)?.add(edge.from);
  }
  const seen = new Set([root]);
  const queue = [root];
  while (queue.length > 0) {
    const current = queue.shift()!;
    for (const next of [...(adjacency.get(current) ?? [])].sort()) {
      if (!seen.has(next)) {
        seen.add(next);
        queue.push(next);
      }
    }
  }
  return [...seen].sort();
}

function json(path: string): JsonRecord {
  return JSON.parse(readFileSync(path, "utf8")) as JsonRecord;
}

function write(path: string, content: string): void {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, content);
}

function bytes(value: unknown): string {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

function slug(value: string): string {
  return value.replace(/([a-z0-9])([A-Z])/g, "$1-$2").toLowerCase();
}

function getArg(name: string): string | undefined {
  const index = args.indexOf(name);
  return index < 0 ? undefined : args[index + 1];
}
