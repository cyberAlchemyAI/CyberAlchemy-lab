import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  compileMintedProject,
  type MintedGraph,
  type MintedProjectCompileOptions,
  type MintedSourceManifest,
} from "./compiler";
import {
  resolveMintedProjectSources,
  type ResolvedMintedProjectSources,
} from "./resolver";
import { validateJsonSchema, type JsonObject } from "./schema-validator";

export const MINTED_PROJECT_GENERATOR_VERSION = "minted-project-tools/v1";

export const MINTED_PROJECT_VERIFICATION_CODES = [
  "SOURCE_UNAVAILABLE",
  "STALE_SOURCE",
  "STALE_GRAPH",
  "STALE_SOURCE_MANIFEST",
  "STALE_MARKDOWN_VIEW",
  "STALE_MARKDOWN",
  "GRAPH_INVALID",
  "SOURCE_MANIFEST_INVALID",
  "MARKDOWN_VIEW_INVALID",
  "BUILD_RECEIPT_INVALID",
  "PROVENANCE_INVALID",
  "LANGUAGE_BINDING_INVALID",
] as const;

export type MintedProjectVerificationCode =
  (typeof MINTED_PROJECT_VERIFICATION_CODES)[number];

export type MintedMarkdownView = {
  schema_version: "minted-markdown-view/v1";
  authority: "generated-human-read-model";
  output_path: "SPEC.md";
  graph_digest: string;
  content_digest: string;
  generator_version: string;
};

export type MintedBuildReceipt = {
  schema_version: "minted-build-receipt/v1";
  authority: "generated-verification-evidence";
  status: "pass" | "degraded";
  project_id: string;
  language: {
    profile_id: string;
    profile_version: string;
    profile_digest: string;
    kinds_digest: string;
    relationships_digest: string;
  };
  source_set_digest: string;
  artifacts: {
    graph_digest: string;
    source_manifest_digest: string;
    markdown_view_digest: string;
    markdown_content_digest: string;
  };
  generator_version: string;
};

export interface MintedProjectBuildArtifacts {
  graph: MintedGraph;
  sourceManifest: MintedSourceManifest;
  markdownView: MintedMarkdownView;
  buildReceipt: MintedBuildReceipt;
  graphBytes: string;
  sourceManifestBytes: string;
  markdownBytes: string;
  markdownViewBytes: string;
  buildReceiptBytes: string;
}

export interface MintedProjectVerificationResult {
  status: "pass" | "fail";
  codes: MintedProjectVerificationCode[];
}

function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

function bytes(value: unknown): string {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function title(projectId: string): string {
  return projectId
    .split("-")
    .map((part) => part.length === 0 ? part : `${part[0]!.toUpperCase()}${part.slice(1)}`)
    .join(" ");
}

export function renderMintedProjectMarkdown(graph: MintedGraph, graphDigest: string): string {
  const lines = [
    `# ${title(graph.project_id)} Specification`,
    "",
    "Generated human view. Canonical semantics live in the project-local machine sources.",
    `Graph digest: \`${graphDigest}\`.`,
    "",
    "## Nodes",
    "",
    "| Node | Kind | Intent |",
    "| --- | --- | --- |",
    ...graph.nodes.map(
      (node) => `| \`${node.node_id}\` | ${node.kind} | ${node.intent.replaceAll("|", "\\|")} |`,
    ),
    "",
    "## Edges",
    "",
    "| Edge | From | Type | To |",
    "| --- | --- | --- | --- |",
    ...graph.edges.map(
      (edge) =>
        `| \`${edge.edge_id}\` | \`${edge.from}\` | \`${edge.type}\` | \`${edge.to}\` |`,
    ),
    "",
    "This file is generated; edit machine sources and rebuild.",
    "",
  ];
  return lines.join("\n");
}

export function buildMintedProjectViews(
  projectRoot: string,
  options: MintedProjectCompileOptions = {},
): MintedProjectBuildArtifacts {
  const compiled = compileMintedProject(projectRoot, options);
  const graphDigest = sha256(compiled.graphBytes);
  const markdownBytes = renderMintedProjectMarkdown(compiled.graph, graphDigest);
  const markdownView: MintedMarkdownView = {
    schema_version: "minted-markdown-view/v1",
    authority: "generated-human-read-model",
    output_path: "SPEC.md",
    graph_digest: graphDigest,
    content_digest: sha256(markdownBytes),
    generator_version: MINTED_PROJECT_GENERATOR_VERSION,
  };
  const markdownViewBytes = bytes(markdownView);
  const project = JSON.parse(readFileSync(resolve(projectRoot, "project.json"), "utf8")) as JsonObject;
  const buildReceipt: MintedBuildReceipt = {
    schema_version: "minted-build-receipt/v1",
    authority: "generated-verification-evidence",
    status: "pass",
    project_id: compiled.graph.project_id,
    language: {
      profile_id: project.language.profile.id,
      profile_version: project.language.profile.version,
      profile_digest: compiled.graph.language.profile_digest,
      kinds_digest: compiled.graph.language.kinds_digest,
      relationships_digest: compiled.graph.language.relationships_digest,
    },
    source_set_digest: compiled.graph.source_set_digest,
    artifacts: {
      graph_digest: graphDigest,
      source_manifest_digest: sha256(compiled.sourceManifestBytes),
      markdown_view_digest: sha256(markdownViewBytes),
      markdown_content_digest: markdownView.content_digest,
    },
    generator_version: MINTED_PROJECT_GENERATOR_VERSION,
  };
  return {
    ...compiled,
    markdownView,
    buildReceipt,
    markdownBytes,
    markdownViewBytes,
    buildReceiptBytes: bytes(buildReceipt),
  };
}

function parse<T>(value: string): T | undefined {
  try {
    return JSON.parse(value) as T;
  } catch {
    return undefined;
  }
}

export function verifyMintedProjectBuild(
  projectRoot: string,
  artifacts: MintedProjectBuildArtifacts,
): MintedProjectVerificationResult {
  const codes = new Set<MintedProjectVerificationCode>();
  const graph = parse<MintedGraph>(artifacts.graphBytes);
  const sourceManifest = parse<MintedSourceManifest>(artifacts.sourceManifestBytes);
  const markdownView = parse<MintedMarkdownView>(artifacts.markdownViewBytes);
  const buildReceipt = parse<MintedBuildReceipt>(artifacts.buildReceiptBytes);

  if (!graph || validateJsonSchema(resolveSchema("graph.schema.json"), graph).length > 0) {
    codes.add("GRAPH_INVALID");
  }
  if (
    !sourceManifest ||
    validateJsonSchema(resolveSchema("source-manifest.schema.json"), sourceManifest).length > 0
  ) {
    codes.add("SOURCE_MANIFEST_INVALID");
  }
  if (
    !markdownView ||
    validateJsonSchema(resolveSchema("markdown-view.schema.json"), markdownView).length > 0
  ) {
    codes.add("MARKDOWN_VIEW_INVALID");
  }
  if (
    !buildReceipt ||
    validateJsonSchema(resolveSchema("build-receipt.schema.json"), buildReceipt).length > 0
  ) {
    codes.add("BUILD_RECEIPT_INVALID");
  }
  if (!buildReceipt) {
    return { status: "fail", codes: [...codes].sort() };
  }

  if (sha256(artifacts.graphBytes) !== buildReceipt.artifacts.graph_digest) {
    codes.add("STALE_GRAPH");
  }
  if (sha256(artifacts.sourceManifestBytes) !== buildReceipt.artifacts.source_manifest_digest) {
    codes.add("STALE_SOURCE_MANIFEST");
  }
  if (sha256(artifacts.markdownViewBytes) !== buildReceipt.artifacts.markdown_view_digest) {
    codes.add("STALE_MARKDOWN_VIEW");
  }
  if (sha256(artifacts.markdownBytes) !== buildReceipt.artifacts.markdown_content_digest) {
    codes.add("STALE_MARKDOWN");
  }

  let current: ResolvedMintedProjectSources | undefined;
  try {
    current = resolveMintedProjectSources(projectRoot);
  } catch {
    codes.add("SOURCE_UNAVAILABLE");
  }
  if (current && current.sourceSetDigest !== buildReceipt.source_set_digest) {
    codes.add("STALE_SOURCE");
  }

  if (graph && markdownView && markdownView.graph_digest !== sha256(artifacts.graphBytes)) {
    codes.add("STALE_MARKDOWN_VIEW");
  }
  if (markdownView && markdownView.content_digest !== sha256(artifacts.markdownBytes)) {
    codes.add("STALE_MARKDOWN");
  }
  if (
    graph &&
    (graph.language.profile_digest !== buildReceipt.language.profile_digest ||
      graph.language.kinds_digest !== buildReceipt.language.kinds_digest ||
      graph.language.relationships_digest !== buildReceipt.language.relationships_digest)
  ) {
    codes.add("LANGUAGE_BINDING_INVALID");
  }

  if (graph && sourceManifest) {
    const graphIds = [
      ...graph.nodes.map((node) => node.node_id),
      ...graph.edges.map((edge) => edge.edge_id),
    ].sort();
    const manifestIds = sourceManifest.records.map((record) => record.graph_id).sort();
    const inputByPath = new Map(sourceManifest.inputs.map((input) => [input.path, input.digest]));
    const currentByPath = new Map(current?.records.map((input) => [input.path, input.digest]) ?? []);
    if (
      JSON.stringify(graphIds) !== JSON.stringify(manifestIds) ||
      new Set(manifestIds).size !== manifestIds.length ||
      sourceManifest.records.some(
        (record) =>
          inputByPath.get(record.source_path) !== record.source_digest ||
          (current !== undefined && currentByPath.get(record.source_path) !== record.source_digest),
      )
    ) {
      codes.add("PROVENANCE_INVALID");
    }
  }

  return { status: codes.size === 0 ? "pass" : "fail", codes: [...codes].sort() };
}

function resolveSchema(file: string): string {
  return resolve(
    new URL("../../spec/minted-project/", import.meta.url).pathname,
    file,
  );
}
