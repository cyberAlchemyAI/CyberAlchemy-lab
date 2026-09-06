import fs from "node:fs";
import path from "node:path";

import { buildSourceManifest, type SourceInput, type SourceManifestV1, type SourceType } from "./source-manifest.js";

const ID_PATTERN = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;

export class ProjectRootError extends Error {
  readonly exitCode = 22;

  constructor(
    readonly code: string,
    readonly pointer: string,
    message: string
  ) {
    super(message);
    this.name = "ProjectRootError";
  }
}

interface ReadSource {
  readonly value: Record<string, unknown>;
  readonly input: SourceInput;
}

function fail(code: string, pointer: string, message: string): never {
  throw new ProjectRootError(code, pointer, message);
}

function isObject(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function requireExactKeys(value: unknown, keys: readonly string[], pointer: string): asserts value is Record<string, unknown> {
  if (!isObject(value)) fail("SFC_INPUT_SCHEMA", pointer, "expected object");
  const actual = Object.keys(value).sort();
  const expected = [...keys].sort();
  if (JSON.stringify(actual) !== JSON.stringify(expected)) fail("SFC_INPUT_SCHEMA", pointer, "unexpected or missing member");
}

function requireId(value: unknown, pointer: string): string {
  if (typeof value !== "string" || !ID_PATTERN.test(value)) fail("SFC_INPUT_ID", pointer, "invalid identifier");
  return value;
}

function requireIdArray(value: unknown, pointer: string): string[] {
  if (!Array.isArray(value)) fail("SFC_INPUT_SCHEMA", pointer, "expected identifier array");
  const ids = value.map((entry, index) => requireId(entry, `${pointer}/${index}`));
  if (new Set(ids).size !== ids.length) fail("SFC_INPUT_DUPLICATE", pointer, "duplicate identifier");
  return ids;
}

function requireString(value: unknown, pointer: string): string {
  if (typeof value !== "string" || value.length === 0) fail("SFC_INPUT_SCHEMA", pointer, "expected nonempty string");
  return value;
}

function ensureContained(root: string, candidate: string, pointer: string): string {
  const relative = path.relative(root, candidate);
  if (relative.startsWith("..") || path.isAbsolute(relative)) fail("SFC_INPUT_PATH_ESCAPE", pointer, "path escapes project root");
  return relative.split(path.sep).join("/");
}

function readSource(root: string, relativePath: string, sourceType: SourceType, sourceId: string, featureId: string | null): ReadSource {
  const absolute = path.resolve(root, relativePath);
  const normalizedRelative = ensureContained(root, absolute, `/${relativePath}`);
  let lstat: fs.Stats;
  try {
    lstat = fs.lstatSync(absolute);
  } catch {
    fail("SFC_INPUT_MISSING", `/${normalizedRelative}`, "declared source is missing");
  }
  if (lstat.isSymbolicLink()) fail("SFC_INPUT_SYMLINK", `/${normalizedRelative}`, "symbolic links are unsupported");
  if (!lstat.isFile()) fail("SFC_INPUT_NOT_FILE", `/${normalizedRelative}`, "declared source is not a regular file");
  const real = fs.realpathSync(absolute);
  if (real !== absolute) fail("SFC_INPUT_SYMLINK", `/${normalizedRelative}`, "declared source path cannot traverse a symbolic link");
  ensureContained(root, real, `/${normalizedRelative}`);
  const bytes = fs.readFileSync(real);
  let value: unknown;
  try {
    value = JSON.parse(bytes.toString("utf8"));
  } catch {
    fail("SFC_INPUT_JSON", `/${normalizedRelative}`, "declared source is not valid JSON");
  }
  if (!isObject(value)) fail("SFC_INPUT_SCHEMA", `/${normalizedRelative}`, "declared source must be an object");
  return {
    value,
    input: { sourceType, sourceId, featureId, relativePath: normalizedRelative, bytes }
  };
}

function normalizeProjectRoot(projectRoot: unknown): string {
  if (typeof projectRoot !== "string" || projectRoot.length === 0 || !path.isAbsolute(projectRoot)) {
    fail("SFC_INPUT_EXPLICIT_ROOT_REQUIRED", "/project-root", "an explicit absolute project root is required");
  }
  const lexicalRoot = path.resolve(projectRoot);
  let lstat: fs.Stats;
  try {
    lstat = fs.lstatSync(lexicalRoot);
  } catch {
    fail("SFC_INPUT_ROOT_MISSING", "/project-root", "project root does not exist");
  }
  if (lstat.isSymbolicLink()) fail("SFC_INPUT_SYMLINK", "/project-root", "project root cannot be a symbolic link");
  if (!lstat.isDirectory()) fail("SFC_INPUT_ROOT_NOT_DIRECTORY", "/project-root", "project root is not a directory");
  const realRoot = fs.realpathSync(lexicalRoot);
  if (realRoot !== lexicalRoot) fail("SFC_INPUT_SYMLINK", "/project-root", "project root cannot traverse a symbolic link");
  return realRoot;
}

export function resolveProjectRoot(projectRoot: unknown): SourceManifestV1 {
  const root = normalizeProjectRoot(projectRoot);
  const inputs: SourceInput[] = [];
  const project = readSource(root, "project.json", "project", "project", null);
  requireExactKeys(project.value, ["schema_version", "project_id", "features", "cross_feature_edges"], "/project.json");
  if (project.value.schema_version !== "domainspec.project/v1") fail("SFC_INPUT_SCHEMA", "/project.json/schema_version", "unsupported project schema");
  const projectId = requireId(project.value.project_id, "/project.json/project_id");
  const featureIds = requireIdArray(project.value.features, "/project.json/features");
  const crossEdgeIds = requireIdArray(project.value.cross_feature_edges, "/project.json/cross_feature_edges");
  inputs.push(project.input);

  const nodesByFeature = new Map<string, Set<string>>();
  for (const featureId of featureIds) {
    const featurePath = `specs/${featureId}/feature.json`;
    const feature = readSource(root, featurePath, "feature", featureId, featureId);
    requireExactKeys(feature.value, ["schema_version", "feature_id", "nodes", "edges"], `/${featurePath}`);
    if (feature.value.schema_version !== "domainspec.feature/v1") fail("SFC_INPUT_SCHEMA", `/${featurePath}/schema_version`, "unsupported feature schema");
    if (feature.value.feature_id !== featureId) fail("SFC_INPUT_WRONG_ROOT", `/${featurePath}/feature_id`, "feature identity does not match its directory");
    const nodeIds = requireIdArray(feature.value.nodes, `/${featurePath}/nodes`);
    const edgeIds = requireIdArray(feature.value.edges, `/${featurePath}/edges`);
    nodesByFeature.set(featureId, new Set(nodeIds));
    inputs.push(feature.input);

    for (const nodeId of nodeIds) {
      const nodePath = `specs/${featureId}/nodes/${nodeId}.json`;
      const node = readSource(root, nodePath, "node", `${featureId}:${nodeId}`, featureId);
      requireExactKeys(node.value, ["schema_version", "node_id", "feature_id", "kind", "body"], `/${nodePath}`);
      if (node.value.schema_version !== "domainspec.node/v1") fail("SFC_INPUT_SCHEMA", `/${nodePath}/schema_version`, "unsupported node schema");
      if (node.value.node_id !== nodeId || node.value.feature_id !== featureId) fail("SFC_INPUT_WRONG_ROOT", `/${nodePath}`, "node identity does not match its declared root");
      requireString(node.value.kind, `/${nodePath}/kind`);
      if (!isObject(node.value.body)) fail("SFC_INPUT_SCHEMA", `/${nodePath}/body`, "node body must be an object");
      inputs.push(node.input);
    }

    for (const edgeId of edgeIds) {
      const edgePath = `specs/${featureId}/edges/${edgeId}.json`;
      const edge = readSource(root, edgePath, "feature-edge", `${featureId}:${edgeId}`, featureId);
      requireExactKeys(edge.value, ["schema_version", "edge_id", "feature_id", "relationship", "source_node_id", "target_node_id", "scope"], `/${edgePath}`);
      if (edge.value.schema_version !== "domainspec.edge/v1" || edge.value.scope !== "feature") fail("SFC_INPUT_SCHEMA", `/${edgePath}`, "unsupported feature edge schema or scope");
      if (edge.value.edge_id !== edgeId || edge.value.feature_id !== featureId) fail("SFC_INPUT_WRONG_ROOT", `/${edgePath}`, "edge identity does not match its declared root");
      const source = requireId(edge.value.source_node_id, `/${edgePath}/source_node_id`);
      const target = requireId(edge.value.target_node_id, `/${edgePath}/target_node_id`);
      requireString(edge.value.relationship, `/${edgePath}/relationship`);
      if (!nodesByFeature.get(featureId)?.has(source) || !nodesByFeature.get(featureId)?.has(target)) fail("SFC_INPUT_ENDPOINT", `/${edgePath}`, "feature edge endpoint is outside its feature root");
      inputs.push(edge.input);
    }
  }

  for (const edgeId of crossEdgeIds) {
    const edgePath = `edges/${edgeId}.json`;
    const edge = readSource(root, edgePath, "project-edge", edgeId, null);
    requireExactKeys(edge.value, ["schema_version", "edge_id", "source_feature_id", "source_node_id", "target_feature_id", "target_node_id", "relationship", "scope"], `/${edgePath}`);
    if (edge.value.schema_version !== "domainspec.edge/v1" || edge.value.scope !== "project") fail("SFC_INPUT_SCHEMA", `/${edgePath}`, "unsupported project edge schema or scope");
    if (edge.value.edge_id !== edgeId) fail("SFC_INPUT_WRONG_ROOT", `/${edgePath}/edge_id`, "project edge identity does not match its filename");
    const sourceFeature = requireId(edge.value.source_feature_id, `/${edgePath}/source_feature_id`);
    const targetFeature = requireId(edge.value.target_feature_id, `/${edgePath}/target_feature_id`);
    const sourceNode = requireId(edge.value.source_node_id, `/${edgePath}/source_node_id`);
    const targetNode = requireId(edge.value.target_node_id, `/${edgePath}/target_node_id`);
    requireString(edge.value.relationship, `/${edgePath}/relationship`);
    if (sourceFeature === targetFeature) fail("SFC_INPUT_ENDPOINT", `/${edgePath}`, "project edge must cross feature roots");
    if (!nodesByFeature.get(sourceFeature)?.has(sourceNode) || !nodesByFeature.get(targetFeature)?.has(targetNode)) {
      fail("SFC_INPUT_ENDPOINT", `/${edgePath}`, "project edge endpoint is outside the declared project root");
    }
    inputs.push(edge.input);
  }

  try {
    return buildSourceManifest(projectId, inputs);
  } catch (error) {
    fail("SFC_INPUT_DUPLICATE", "/sources", error instanceof Error ? error.message : "duplicate source");
  }
}
