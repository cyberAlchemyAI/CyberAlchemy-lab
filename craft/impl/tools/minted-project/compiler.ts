import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, posix, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  resolveMintedProjectSources,
  type MintedProjectSourceRecord,
} from "./resolver";
import { validateMintedNodeFormation } from "./meta-type-body-adapter";
import { validateJsonSchema, type JsonObject, type JsonSchemaViolation } from "./schema-validator";

export const MINTED_PROJECT_COMPILER_ERROR_CODES = [
  "PROJECT_SCHEMA_INVALID",
  "FEATURE_SCHEMA_INVALID",
  "NODE_SCHEMA_INVALID",
  "DEVELOPMENT_PROFILE_HANDLE_REQUIRED",
  "DEVELOPMENT_PROFILE_HANDLE_INVALID",
  "DEVELOPMENT_PROFILE_REGISTRY_INVALID",
  "PROFILE_UNSUPPORTED",
  "PROFILE_DIGEST_MISMATCH",
  "REGISTRY_DIGEST_MISMATCH",
  "PROFILE_RELATIONSHIP_INVALID",
  "KIND_UNSUPPORTED",
  "FORMATION_INVALID",
  "NODE_LOGIC_PROFILE_UNSUPPORTED",
  "NODE_LOGIC_KIND_UNSUPPORTED",
  "NODE_LOGIC_VERSION_UNSUPPORTED",
  "NODE_LOGIC_SCHEMA_BINDING_INVALID",
  "NODE_LOGIC_SCHEMA_INVALID",
  "NODE_FEATURE_MISMATCH",
  "NODE_ID_DUPLICATE",
  "EDGE_ID_DUPLICATE",
  "EDGE_TYPE_UNKNOWN",
  "EDGE_TYPE_GENERATED",
  "EDGE_TYPE_DEPRECATED",
  "EDGE_TYPE_DEFERRED",
  "EDGE_TYPE_UNSUPPORTED_PROFILE",
  "EDGE_ENDPOINT_MISSING",
  "EDGE_ENDPOINT_KIND_MISMATCH",
  "EDGE_FEATURE_SCOPE_MISMATCH",
  "EDGE_SOURCE_EFFECT_MISMATCH",
  "EDGE_MULTIPLICITY_VIOLATION",
  "GENERATED_PROJECTION_AUTHORED",
  "CROSS_FEATURE_UNSUPPORTED",
  "GENERATED_GRAPH_INVALID",
  "GENERATED_MANIFEST_INVALID",
] as const;

export type MintedProjectCompilerErrorCode =
  (typeof MINTED_PROJECT_COMPILER_ERROR_CODES)[number];

export class MintedProjectCompilerError extends Error {
  readonly code: MintedProjectCompilerErrorCode;
  readonly sourcePath: string;

  constructor(code: MintedProjectCompilerErrorCode, sourcePath: string, detail: string) {
    super(`${code}:${sourcePath}:${detail}`);
    this.name = "MintedProjectCompilerError";
    this.code = code;
    this.sourcePath = sourcePath;
  }
}

type RelationshipSignature = {
  id: string;
  status?: string;
  source_type?: string;
  source_types?: string[];
  target_type?: string;
  target_types?: string[];
  feature_scope?: Array<"same-feature" | "cross-feature" | "ui" | "ui-backend">;
  multiplicity?: "one_to_one" | "one_to_many" | "one_to_many_ordered" | "many_to_one" | "many_to_many";
  generated_source_projection?: {
    attribute: string;
    value_shape: "concept-reference-set";
    derivation: "outgoing-targets";
    authorship: "forbidden";
  };
};

export type RelationshipRegistrySlice = {
  signatures: RelationshipSignature[];
  generated_views?: Array<{ id: string }>;
  deprecated?: Array<{ id: string; replacement?: string; reason?: string }>;
};

type ProfileRelationship = {
  id: string;
  source_kind: string;
  target_kind: string;
  registry_status: string;
};

type SupportedProfile = {
  id: string;
  version: string;
  status: string;
  source_layout: string;
  kinds: string[];
  formation_schemas?: Record<string, string>;
  formation_contracts?: Record<
    string,
    { validator: "json-schema" | "attribute-map"; path: string }
  >;
  logic_contract?: {
    schema_versions: string[];
    node_kinds: string[];
    envelope_schema: {
      validator: "json-schema";
      path: string;
      sha256: string;
    };
  };
  relationships: ProfileRelationship[];
};

type ProfileRegistry = {
  schema_version?: string;
  authority?: string | { owner: string; role: string; release_admission: string };
  release_admission?: string;
  handle?: string;
  profile_binding?: { path: string; sha256: string; semantic_digest: string };
  registry_bindings: {
    kinds: { path: string; sha256: string };
    relationships: { path: string; sha256: string };
  };
  profiles: SupportedProfile[];
};

type SourceNode = {
  schema_version: string;
  node_id: string;
  feature_id: string;
  kind: string;
  intent: string;
  body: JsonObject;
  connections: Array<{ edge_id: string; type: string; to: string }>;
};

export interface MintedGraph {
  schema_version: "minted-graph/v1";
  authority: "generated-semantic-read-model";
  project_id: string;
  language: {
    profile_digest: string;
    kinds_digest: string;
    relationships_digest: string;
  };
  source_set_digest: string;
  nodes: Array<Omit<SourceNode, "schema_version" | "connections">>;
  edges: Array<{ edge_id: string; type: string; from: string; to: string }>;
}

export interface MintedSourceManifest {
  schema_version: "minted-source-manifest/v1";
  authority: "generated-provenance-read-model";
  project_id: string;
  source_set_digest: string;
  inputs: MintedProjectSourceRecord[];
  records: Array<{
    record_type: "node" | "edge";
    graph_id: string;
    source_path: string;
    source_digest: string;
  }>;
}

export interface CompiledMintedProject {
  graph: MintedGraph;
  sourceManifest: MintedSourceManifest;
  graphBytes: string;
  sourceManifestBytes: string;
}

export interface MintedProjectCompileOptions {
  developmentProfileRegistry?: {
    path: string;
    handle: string;
  };
}

const implRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const domainspecRoot = resolve(implRoot, "..");

function readJson<T>(path: string): T {
  return JSON.parse(readFileSync(path, "utf8")) as T;
}

function sha256File(path: string): string {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

function failSchema(
  code: MintedProjectCompilerErrorCode,
  sourcePath: string,
  violations: JsonSchemaViolation[],
): never {
  throw new MintedProjectCompilerError(code, sourcePath, JSON.stringify(violations));
}

function sourcePath(declaringPath: string, reference: string): string {
  return posix.normalize(posix.join(posix.dirname(declaringPath), reference.replaceAll("\\", "/")));
}

function signatureTypes(signature: RelationshipSignature, side: "source" | "target"): string[] {
  const singular = side === "source" ? signature.source_type : signature.target_type;
  const plural = side === "source" ? signature.source_types : signature.target_types;
  return singular ? [singular] : plural ?? [];
}

function validateFormation(
  profile: SupportedProfile,
  node: SourceNode,
  nodePath: string,
): JsonSchemaViolation[] {
  const development = profile.formation_contracts?.[node.kind];
  const formationBody =
    profile.logic_contract && Object.hasOwn(node.body, "logic")
      ? Object.fromEntries(Object.entries(node.body).filter(([key]) => key !== "logic"))
      : node.body;
  return validateMintedNodeFormation(node.kind, formationBody, nodePath, {
    schemaPath:
      development?.validator === "attribute-map"
        ? resolve(domainspecRoot, development.path)
        : undefined,
  });
}

function validateNodeLogic(
  profile: SupportedProfile,
  node: SourceNode,
  nodePath: string,
): void {
  if (!Object.hasOwn(node.body, "logic")) {
    return;
  }
  const contract = profile.logic_contract;
  if (!contract) {
    throw new MintedProjectCompilerError(
      "NODE_LOGIC_PROFILE_UNSUPPORTED",
      nodePath,
      `${profile.id}@${profile.version} does not admit body.logic`,
    );
  }
  if (!contract.node_kinds.includes(node.kind)) {
    throw new MintedProjectCompilerError(
      "NODE_LOGIC_KIND_UNSUPPORTED",
      nodePath,
      `${node.kind} is not admitted for body.logic`,
    );
  }
  const logic = node.body.logic;
  if (
    typeof logic !== "object" ||
    logic === null ||
    Array.isArray(logic) ||
    typeof (logic as JsonObject).schema_version !== "string"
  ) {
    throw new MintedProjectCompilerError(
      "NODE_LOGIC_VERSION_UNSUPPORTED",
      nodePath,
      "body.logic must declare an admitted schema_version",
    );
  }
  const schemaVersion = (logic as JsonObject).schema_version as string;
  if (!contract.schema_versions.includes(schemaVersion)) {
    throw new MintedProjectCompilerError(
      "NODE_LOGIC_VERSION_UNSUPPORTED",
      nodePath,
      schemaVersion,
    );
  }
  const schemaPath = resolve(domainspecRoot, contract.envelope_schema.path);
  if (sha256File(schemaPath) !== contract.envelope_schema.sha256) {
    throw new MintedProjectCompilerError(
      "NODE_LOGIC_SCHEMA_BINDING_INVALID",
      nodePath,
      contract.envelope_schema.path,
    );
  }
  const violations = validateJsonSchema(schemaPath, logic, "$.body.logic");
  if (violations.length > 0) {
    failSchema("NODE_LOGIC_SCHEMA_INVALID", nodePath, violations);
  }
}

function loadProfileSelection(
  project: JsonObject,
  projectPath: string,
  options: MintedProjectCompileOptions,
): { path: string; registry: ProfileRegistry; digest: string; development: boolean } {
  const development = options.developmentProfileRegistry;
  if (!development) {
    if (project.language.profile.id === "ui-development") {
      throw new MintedProjectCompilerError(
        "DEVELOPMENT_PROFILE_HANDLE_REQUIRED",
        projectPath,
        "ui-development requires an explicit registry path and handle",
      );
    }
    const path = resolve(domainspecRoot, "definitions/minted-project/supported-profiles.yml");
    return { path, registry: readJson<ProfileRegistry>(path), digest: sha256File(path), development: false };
  }

  const path = resolve(development.path);
  let registry: ProfileRegistry;
  try {
    registry = readJson<ProfileRegistry>(path);
  } catch (error) {
    throw new MintedProjectCompilerError(
      "DEVELOPMENT_PROFILE_REGISTRY_INVALID",
      projectPath,
      error instanceof Error ? error.message : String(error),
    );
  }
  if (
    registry.schema_version !== "domainspec-development-minted-profile/v0.1" ||
    registry.authority !== "implementation-owned-development-profile" ||
    registry.release_admission !== "not-granted" ||
    registry.handle !== development.handle
  ) {
    throw new MintedProjectCompilerError(
      "DEVELOPMENT_PROFILE_HANDLE_INVALID",
      projectPath,
      "development registry contract or handle does not match",
    );
  }
  const binding = registry.profile_binding;
  if (
    !binding ||
    sha256File(resolve(domainspecRoot, binding.path)) !== binding.sha256
  ) {
    throw new MintedProjectCompilerError(
      "DEVELOPMENT_PROFILE_REGISTRY_INVALID",
      projectPath,
      "development profile binding does not match profile bytes",
    );
  }
  return { path, registry, digest: sha256File(path), development: true };
}

export function classifyRelationshipType(
  type: string,
  registry: RelationshipRegistrySlice,
  profileRelationships: ProfileRelationship[],
): MintedProjectCompilerErrorCode | "active-profile" {
  if ((registry.generated_views ?? []).some((entry) => entry.id === type)) {
    return "EDGE_TYPE_GENERATED";
  }
  if ((registry.deprecated ?? []).some((entry) => entry.id === type)) {
    return "EDGE_TYPE_DEPRECATED";
  }
  const signatures = registry.signatures.filter((entry) => entry.id === type);
  if (signatures.length === 0) {
    return "EDGE_TYPE_UNKNOWN";
  }
  if (signatures.some((entry) => entry.status === "deprecated")) {
    return "EDGE_TYPE_DEPRECATED";
  }
  if (signatures.some((entry) => entry.status === "deferred")) {
    return "EDGE_TYPE_DEFERRED";
  }
  if (!profileRelationships.some((entry) => entry.id === type)) {
    return "EDGE_TYPE_UNSUPPORTED_PROFILE";
  }
  return "active-profile";
}

export function compileMintedProject(
  projectRoot: string,
  options: MintedProjectCompileOptions = {},
): CompiledMintedProject {
  const resolution = resolveMintedProjectSources(projectRoot);
  const project = readJson<JsonObject>(resolve(resolution.projectRoot, resolution.projectPath));
  const projectViolations = validateJsonSchema(
    resolve(implRoot, "spec/minted-project/project.schema.json"),
    project,
  );
  if (projectViolations.length > 0) {
    failSchema("PROJECT_SCHEMA_INVALID", resolution.projectPath, projectViolations);
  }
  const selection = loadProfileSelection(project, resolution.projectPath, options);
  const profilePath = selection.path;
  const profileRegistry = selection.registry;
  const relationshipsPath = resolve(
    domainspecRoot,
    profileRegistry.registry_bindings.relationships.path,
  );
  const kindsPath = resolve(domainspecRoot, profileRegistry.registry_bindings.kinds.path);
  const relationships = readJson<RelationshipRegistrySlice>(relationshipsPath);
  if (
    sha256File(kindsPath) !== profileRegistry.registry_bindings.kinds.sha256 ||
    sha256File(relationshipsPath) !== profileRegistry.registry_bindings.relationships.sha256
  ) {
    throw new MintedProjectCompilerError(
      "REGISTRY_DIGEST_MISMATCH",
      resolution.projectPath,
      "supported-profile registry bindings do not match authority bytes",
    );
  }

  const profile = profileRegistry.profiles.find(
    (entry) =>
      entry.id === project.language.profile.id && entry.version === project.language.profile.version,
  );
  if (!profile) {
    throw new MintedProjectCompilerError(
      "PROFILE_UNSUPPORTED",
      resolution.projectPath,
      `${project.language.profile.id}@${project.language.profile.version}`,
    );
  }
  if (selection.development && profile.status !== "development-only") {
    throw new MintedProjectCompilerError(
      "DEVELOPMENT_PROFILE_REGISTRY_INVALID",
      resolution.projectPath,
      "explicit registry did not select a development-only profile",
    );
  }
  const profileDigest = selection.digest;
  if (project.language.profile.digest !== profileDigest) {
    throw new MintedProjectCompilerError(
      "PROFILE_DIGEST_MISMATCH",
      resolution.projectPath,
      "project profile digest does not match evaluated registry",
    );
  }
  if (
    project.language.registries.kinds_digest !== profileRegistry.registry_bindings.kinds.sha256 ||
    project.language.registries.relationships_digest !==
      profileRegistry.registry_bindings.relationships.sha256
  ) {
    throw new MintedProjectCompilerError(
      "REGISTRY_DIGEST_MISMATCH",
      resolution.projectPath,
      "project registry digests do not match the supported profile",
    );
  }

  for (const admitted of profile.relationships) {
    const signatures = relationships.signatures.filter(
      (entry) => entry.id === admitted.id && entry.status !== "deprecated" && entry.status !== "deferred",
    );
    if (
      !signatures.some(
        (signature) =>
          signatureTypes(signature, "source").includes(admitted.source_kind) &&
          signatureTypes(signature, "target").includes(admitted.target_kind),
      )
    ) {
      throw new MintedProjectCompilerError(
        "PROFILE_RELATIONSHIP_INVALID",
        profilePath,
        `${admitted.source_kind}-${admitted.id}->${admitted.target_kind}`,
      );
    }
  }

  const inputByPath = new Map(resolution.records.map((record) => [record.path, record]));
  const nodeById = new Map<string, { node: SourceNode; path: string }>();
  for (const featureReference of project.features as string[]) {
    const featurePath = sourcePath(resolution.projectPath, featureReference);
    const feature = readJson<JsonObject>(resolve(resolution.projectRoot, featurePath));
    const featureViolations = validateJsonSchema(
      resolve(implRoot, "spec/minted-project/feature.schema.json"),
      feature,
    );
    if (featureViolations.length > 0) {
      failSchema("FEATURE_SCHEMA_INVALID", featurePath, featureViolations);
    }
    for (const nodeReference of feature.node_sources as string[]) {
      const nodePath = sourcePath(featurePath, nodeReference);
      const node = readJson<SourceNode>(resolve(resolution.projectRoot, nodePath));
      assertNoAuthoredGeneratedProjection(node, nodePath, relationships);
      const baseViolations = validateJsonSchema(
        resolve(implRoot, "spec/minted-project/node.schema.json"),
        node,
      );
      if (!profile.kinds.includes(node.kind)) {
        throw new MintedProjectCompilerError("KIND_UNSUPPORTED", nodePath, node.kind);
      }
      validateNodeLogic(profile, node, nodePath);
      const formationViolations = validateFormation(profile, node, nodePath);
      if (formationViolations.length > 0) {
        failSchema("FORMATION_INVALID", nodePath, formationViolations);
      }
      const nonFormationViolations = baseViolations.filter(
        (violation) => !violation.path.startsWith("$.body"),
      );
      if (nonFormationViolations.length > 0) {
        failSchema("NODE_SCHEMA_INVALID", nodePath, nonFormationViolations);
      }
      if (node.feature_id !== feature.feature_id) {
        throw new MintedProjectCompilerError(
          "NODE_FEATURE_MISMATCH",
          nodePath,
          `${node.feature_id} != ${feature.feature_id}`,
        );
      }
      if (nodeById.has(node.node_id)) {
        throw new MintedProjectCompilerError("NODE_ID_DUPLICATE", nodePath, node.node_id);
      }
      nodeById.set(node.node_id, { node, path: nodePath });
    }
  }

  const edges: MintedGraph["edges"] = [];
  const edgeIds = new Set<string>();
  for (const { node, path } of nodeById.values()) {
    for (const connection of node.connections) {
      if (edgeIds.has(connection.edge_id)) {
        throw new MintedProjectCompilerError("EDGE_ID_DUPLICATE", path, connection.edge_id);
      }
      edgeIds.add(connection.edge_id);
      const classification = classifyRelationshipType(
        connection.type,
        relationships,
        profile.relationships,
      );
      if (classification !== "active-profile") {
        throw new MintedProjectCompilerError(classification, path, connection.type);
      }
      const target = nodeById.get(connection.to);
      if (!target) {
        throw new MintedProjectCompilerError("EDGE_ENDPOINT_MISSING", path, connection.to);
      }
      const admitted = profile.relationships.some(
        (entry) =>
          entry.id === connection.type &&
          entry.source_kind === node.kind &&
          entry.target_kind === target.node.kind,
      );
      if (
        !admitted
      ) {
        throw new MintedProjectCompilerError(
          "EDGE_ENDPOINT_KIND_MISMATCH",
          path,
          `${node.kind}-${connection.type}->${target.node.kind}`,
        );
      }
      const authoritySignature = relationships.signatures.find(
        (signature) =>
          signature.id === connection.type &&
          signature.status !== "deprecated" &&
          signature.status !== "deferred" &&
          signatureTypes(signature, "source").includes(node.kind) &&
          signatureTypes(signature, "target").includes(target.node.kind),
      );
      if (!authoritySignature) {
        throw new MintedProjectCompilerError(
          "EDGE_ENDPOINT_KIND_MISMATCH",
          path,
          `${node.kind}-${connection.type}->${target.node.kind}`,
        );
      }
      const scope =
        node.feature_id === target.node.feature_id ? "same-feature" : "cross-feature";
      if (!admitsFeatureLocation(authoritySignature, scope)) {
        throw new MintedProjectCompilerError(
          "EDGE_FEATURE_SCOPE_MISMATCH",
          path,
          `${node.node_id}-${connection.type}->${target.node.node_id}:${scope}`,
        );
      }
      edges.push({
        edge_id: connection.edge_id,
        type: connection.type,
        from: node.node_id,
        to: connection.to,
      });
    }
  }

  assertDeclaredMultiplicity(edges, nodeById, relationships);

  const nodes = [...nodeById.values()]
    .map(({ node }) => ({
      node_id: node.node_id,
      feature_id: node.feature_id,
      kind: node.kind,
      intent: node.intent,
      body: withGeneratedRelationshipProjections(node, edges, relationships),
    }))
    .sort((left, right) => left.node_id.localeCompare(right.node_id));
  edges.sort((left, right) => left.edge_id.localeCompare(right.edge_id));

  const graph: MintedGraph = {
    schema_version: "minted-graph/v1",
    authority: "generated-semantic-read-model",
    project_id: project.project_id,
    language: {
      profile_digest: profileDigest,
      kinds_digest: profileRegistry.registry_bindings.kinds.sha256,
      relationships_digest: profileRegistry.registry_bindings.relationships.sha256,
    },
    source_set_digest: resolution.sourceSetDigest,
    nodes,
    edges,
  };
  const records: MintedSourceManifest["records"] = [];
  for (const { node, path } of nodeById.values()) {
    const input = inputByPath.get(path);
    if (!input) {
      throw new MintedProjectCompilerError("GENERATED_MANIFEST_INVALID", path, "missing input digest");
    }
    records.push({
      record_type: "node",
      graph_id: node.node_id,
      source_path: path,
      source_digest: input.digest,
    });
    for (const connection of node.connections) {
      records.push({
        record_type: "edge",
        graph_id: connection.edge_id,
        source_path: path,
        source_digest: input.digest,
      });
    }
  }
  records.sort((left, right) =>
    left.record_type.localeCompare(right.record_type) || left.graph_id.localeCompare(right.graph_id),
  );
  const sourceManifest: MintedSourceManifest = {
    schema_version: "minted-source-manifest/v1",
    authority: "generated-provenance-read-model",
    project_id: project.project_id,
    source_set_digest: resolution.sourceSetDigest,
    inputs: resolution.records,
    records,
  };

  const graphViolations = validateJsonSchema(
    resolve(implRoot, "spec/minted-project/graph.schema.json"),
    graph,
  );
  if (graphViolations.length > 0) {
    failSchema("GENERATED_GRAPH_INVALID", "graph.json", graphViolations);
  }
  const manifestViolations = validateJsonSchema(
    resolve(implRoot, "spec/minted-project/source-manifest.schema.json"),
    sourceManifest,
  );
  if (manifestViolations.length > 0) {
    failSchema("GENERATED_MANIFEST_INVALID", "source-manifest.json", manifestViolations);
  }

  return {
    graph,
    sourceManifest,
    graphBytes: `${JSON.stringify(graph, null, 2)}\n`,
    sourceManifestBytes: `${JSON.stringify(sourceManifest, null, 2)}\n`,
  };
}

function admitsFeatureLocation(
  signature: RelationshipSignature,
  location: "same-feature" | "cross-feature",
): boolean {
  const declared = signature.feature_scope ?? [];
  if (location === "cross-feature") {
    return declared.includes("cross-feature");
  }
  return declared.some((scope) =>
    scope === "same-feature" || scope === "ui" || scope === "ui-backend"
  );
}

function assertNoAuthoredGeneratedProjection(
  node: SourceNode,
  nodePath: string,
  relationships: RelationshipRegistrySlice,
): void {
  for (const signature of relationships.signatures) {
    const projection = signature.generated_source_projection;
    if (
      !projection ||
      signature.status === "deprecated" ||
      signature.status === "deferred" ||
      !signatureTypes(signature, "source").includes(node.kind)
    ) {
      continue;
    }
    if (Object.prototype.hasOwnProperty.call(node.body, projection.attribute)) {
      throw new MintedProjectCompilerError(
        "GENERATED_PROJECTION_AUTHORED",
        nodePath,
        `${node.node_id}.${projection.attribute} is generated from outgoing ${signature.id} edges`,
      );
    }
  }
}

function assertDeclaredMultiplicity(
  edges: MintedGraph["edges"],
  nodeById: Map<string, { node: SourceNode; path: string }>,
  relationships: RelationshipRegistrySlice,
): void {
  for (const signature of relationships.signatures) {
    if (
      signature.status === "deprecated" ||
      signature.status === "deferred" ||
      signature.multiplicity !== "one_to_one"
    ) {
      continue;
    }
    const relevant = edges.filter((edge) => {
      if (edge.type !== signature.id) {
        return false;
      }
      const source = nodeById.get(edge.from)?.node;
      const target = nodeById.get(edge.to)?.node;
      return Boolean(
        source &&
        target &&
        signatureTypes(signature, "source").includes(source.kind) &&
        signatureTypes(signature, "target").includes(target.kind),
      );
    });
    const bySource = groupGraphEdges(relevant, (edge) => edge.from);
    for (const [source, grouped] of bySource) {
      if (grouped.length > 1) {
        throw new MintedProjectCompilerError(
          "EDGE_MULTIPLICITY_VIOLATION",
          nodeById.get(source)?.path ?? source,
          `${signature.id} source ${source} has ${grouped.length} outgoing edges; one_to_one permits at most one`,
        );
      }
    }
    const byTarget = groupGraphEdges(relevant, (edge) => edge.to);
    for (const [target, grouped] of byTarget) {
      if (grouped.length > 1) {
        throw new MintedProjectCompilerError(
          "EDGE_MULTIPLICITY_VIOLATION",
          nodeById.get(grouped[1]!.from)?.path ?? grouped[1]!.from,
          `${signature.id} target ${target} has ${grouped.length} incoming edges; one_to_one permits at most one`,
        );
      }
    }
  }
}

function groupGraphEdges(
  edges: MintedGraph["edges"],
  key: (edge: MintedGraph["edges"][number]) => string,
): Map<string, MintedGraph["edges"]> {
  const grouped = new Map<string, MintedGraph["edges"]>();
  for (const edge of edges) {
    const value = key(edge);
    grouped.set(value, [...(grouped.get(value) ?? []), edge]);
  }
  return grouped;
}

function withGeneratedRelationshipProjections(
  node: SourceNode,
  edges: MintedGraph["edges"],
  relationships: RelationshipRegistrySlice,
): JsonObject {
  const body: JsonObject = { ...node.body };
  for (const signature of relationships.signatures) {
    const projection = signature.generated_source_projection;
    if (
      !projection ||
      signature.status === "deprecated" ||
      signature.status === "deferred" ||
      !signatureTypes(signature, "source").includes(node.kind)
    ) {
      continue;
    }
    const targets = edges
      .filter((edge) => edge.type === signature.id && edge.from === node.node_id)
      .map((edge) => edge.to)
      .sort();
    if (targets.length > 0) {
      body[projection.attribute] = targets;
    }
  }
  return body;
}
