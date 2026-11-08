import crypto from "node:crypto";

const ID_PATTERN = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
const SOURCE_ID_PATTERN = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*(?::[a-z][a-z0-9]*(?:-[a-z0-9]+)*)?$/;
const RELATIVE_PATH_PATTERN = /^(?:project\.json|edges\/[a-z][a-z0-9]*(?:-[a-z0-9]+)*\.json|specs\/[a-z][a-z0-9]*(?:-[a-z0-9]+)*\/(?:feature\.json|(?:nodes|edges)\/[a-z][a-z0-9]*(?:-[a-z0-9]+)*\.json))$/;

export type SourceType =
  | "project"
  | "feature"
  | "node"
  | "feature-edge"
  | "project-edge";

export interface SourceInput {
  readonly sourceType: SourceType;
  readonly sourceId: string;
  readonly featureId: string | null;
  readonly relativePath: string;
  readonly bytes: Buffer;
}

export interface SourceManifestEntry {
  readonly source_type: SourceType;
  readonly source_id: string;
  readonly feature_id: string | null;
  readonly relative_path: string;
  readonly size_bytes: number;
  readonly sha256: string;
}

export interface SourceManifestV1 {
  readonly schema_version: "domainspec.stable-foundation-cli.source-manifest/v1";
  readonly project_id: string;
  readonly source_count: number;
  readonly total_size_bytes: number;
  readonly sources: readonly SourceManifestEntry[];
  readonly aggregate_sha256: string;
  readonly authority_effect: "none";
  readonly manifest_sha256: string;
}

export class SourceManifestError extends Error {
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(message);
    this.name = "SourceManifestError";
  }
}

export function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (value !== null && typeof value === "object") {
    const record = value as Record<string, unknown>;
    return `{${Object.keys(record).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(record[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

export function sha256(bytes: string | Buffer): string {
  return crypto.createHash("sha256").update(bytes).digest("hex");
}

function isObject(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function exactKeys(value: unknown, expected: readonly string[], pointer: string): asserts value is Record<string, unknown> {
  if (!isObject(value)) throw new SourceManifestError("SFC_SOURCE_MANIFEST_SCHEMA", pointer, "expected object");
  const actual = Object.keys(value).sort();
  const wanted = [...expected].sort();
  if (JSON.stringify(actual) !== JSON.stringify(wanted)) {
    throw new SourceManifestError("SFC_SOURCE_MANIFEST_SCHEMA", pointer, "unexpected or missing member");
  }
}

function requireSha(value: unknown, pointer: string): asserts value is string {
  if (typeof value !== "string" || !/^[0-9a-f]{64}$/.test(value)) {
    throw new SourceManifestError("SFC_SOURCE_MANIFEST_SCHEMA", pointer, "expected SHA-256");
  }
}

function requireSourceIdentity(entry: Record<string, unknown>, pointer: string): {
  sourceId: string;
  featureId: string | null;
  relativePath: string;
} {
  if (typeof entry.source_id !== "string" || !SOURCE_ID_PATTERN.test(entry.source_id)) {
    throw new SourceManifestError("SFC_SOURCE_MANIFEST_IDENTITY", `${pointer}/source_id`, "invalid source identity");
  }
  if (entry.feature_id !== null && (typeof entry.feature_id !== "string" || !ID_PATTERN.test(entry.feature_id))) {
    throw new SourceManifestError("SFC_SOURCE_MANIFEST_IDENTITY", `${pointer}/feature_id`, "invalid feature identity");
  }
  if (typeof entry.relative_path !== "string" || !RELATIVE_PATH_PATTERN.test(entry.relative_path)) {
    throw new SourceManifestError("SFC_SOURCE_MANIFEST_PATH", `${pointer}/relative_path`, "relative path is not canonical");
  }

  const sourceType = entry.source_type;
  const sourceId = entry.source_id;
  const featureId = entry.feature_id as string | null;
  let expectedPath: string;
  if (sourceType === "project") {
    if (sourceId !== "project" || featureId !== null) throw new SourceManifestError("SFC_SOURCE_MANIFEST_IDENTITY", pointer, "project source identity is invalid");
    expectedPath = "project.json";
  } else if (sourceType === "feature") {
    if (featureId !== sourceId || !ID_PATTERN.test(sourceId)) throw new SourceManifestError("SFC_SOURCE_MANIFEST_IDENTITY", pointer, "feature source identity is invalid");
    expectedPath = `specs/${sourceId}/feature.json`;
  } else if (sourceType === "node" || sourceType === "feature-edge") {
    const [identityFeature, localId, extra] = sourceId.split(":");
    if (extra !== undefined || featureId === null || identityFeature !== featureId || !ID_PATTERN.test(identityFeature) || !ID_PATTERN.test(localId ?? "")) {
      throw new SourceManifestError("SFC_SOURCE_MANIFEST_IDENTITY", pointer, "feature-owned source identity is invalid");
    }
    const directory = sourceType === "node" ? "nodes" : "edges";
    expectedPath = `specs/${featureId}/${directory}/${localId}.json`;
  } else {
    if (featureId !== null || !ID_PATTERN.test(sourceId)) throw new SourceManifestError("SFC_SOURCE_MANIFEST_IDENTITY", pointer, "project-edge source identity is invalid");
    expectedPath = `edges/${sourceId}.json`;
  }
  if (entry.relative_path !== expectedPath) {
    throw new SourceManifestError("SFC_SOURCE_MANIFEST_PATH", `${pointer}/relative_path`, "relative path does not match source identity");
  }
  return { sourceId, featureId, relativePath: entry.relative_path };
}

export function validateSourceManifest(value: unknown): SourceManifestV1 {
  exactKeys(value, ["schema_version", "project_id", "source_count", "total_size_bytes", "sources", "aggregate_sha256", "authority_effect", "manifest_sha256"], "$");
  if (value.schema_version !== "domainspec.stable-foundation-cli.source-manifest/v1") throw new SourceManifestError("SFC_SOURCE_MANIFEST_SCHEMA", "/schema_version", "unsupported schema");
  if (typeof value.project_id !== "string" || !ID_PATTERN.test(value.project_id)) throw new SourceManifestError("SFC_SOURCE_MANIFEST_IDENTITY", "/project_id", "invalid project id");
  if (!Number.isSafeInteger(value.source_count) || (value.source_count as number) < 1) throw new SourceManifestError("SFC_SOURCE_MANIFEST_SCHEMA", "/source_count", "invalid source count");
  if (!Number.isSafeInteger(value.total_size_bytes) || (value.total_size_bytes as number) < 1) throw new SourceManifestError("SFC_SOURCE_MANIFEST_SCHEMA", "/total_size_bytes", "invalid total size");
  if (!Array.isArray(value.sources) || value.sources.length !== value.source_count) throw new SourceManifestError("SFC_SOURCE_MANIFEST_SCHEMA", "/sources", "source count mismatch");
  requireSha(value.aggregate_sha256, "/aggregate_sha256");
  requireSha(value.manifest_sha256, "/manifest_sha256");
  if (value.authority_effect !== "none") throw new SourceManifestError("SFC_SOURCE_MANIFEST_AUTHORITY", "/authority_effect", "authority growth is forbidden");

  const paths = new Set<string>();
  const identities = new Set<string>();
  let totalSize = 0;
  let priorPath = "";
  let projectSources = 0;
  const featureSources = new Set<string>();
  const featureReferences = new Set<string>();
  const rows: string[] = [];
  for (const [index, entryValue] of value.sources.entries()) {
    const pointer = `/sources/${index}`;
    exactKeys(entryValue, ["source_type", "source_id", "feature_id", "relative_path", "size_bytes", "sha256"], pointer);
    if (!["project", "feature", "node", "feature-edge", "project-edge"].includes(String(entryValue.source_type))) throw new SourceManifestError("SFC_SOURCE_MANIFEST_SCHEMA", `${pointer}/source_type`, "unknown source type");
    const { sourceId, featureId, relativePath } = requireSourceIdentity(entryValue, pointer);
    if (entryValue.source_type === "project") projectSources += 1;
    if (entryValue.source_type === "feature") featureSources.add(sourceId);
    if ((entryValue.source_type === "node" || entryValue.source_type === "feature-edge") && featureId !== null) featureReferences.add(featureId);
    if (!Number.isSafeInteger(entryValue.size_bytes) || (entryValue.size_bytes as number) < 1) throw new SourceManifestError("SFC_SOURCE_MANIFEST_SCHEMA", `${pointer}/size_bytes`, "invalid source size");
    requireSha(entryValue.sha256, `${pointer}/sha256`);
    if (priorPath && priorPath.localeCompare(relativePath) > 0) throw new SourceManifestError("SFC_SOURCE_MANIFEST_ORDER", `${pointer}/relative_path`, "sources are not sorted");
    priorPath = relativePath;
    if (paths.has(relativePath)) throw new SourceManifestError("SFC_SOURCE_MANIFEST_DUPLICATE", `${pointer}/relative_path`, "duplicate source path");
    paths.add(relativePath);
    const identity = `${entryValue.source_type}:${sourceId}`;
    if (identities.has(identity)) throw new SourceManifestError("SFC_SOURCE_MANIFEST_DUPLICATE", `${pointer}/source_id`, "duplicate source identity");
    identities.add(identity);
    totalSize += entryValue.size_bytes as number;
    rows.push(`${entryValue.source_type}\t${entryValue.source_id}\t${entryValue.feature_id ?? "-"}\t${entryValue.relative_path}\t${entryValue.size_bytes}\t${entryValue.sha256}\n`);
  }
  if (projectSources !== 1) throw new SourceManifestError("SFC_SOURCE_MANIFEST_IDENTITY", "/sources", "exactly one project source is required");
  for (const featureId of featureReferences) {
    if (!featureSources.has(featureId)) throw new SourceManifestError("SFC_SOURCE_MANIFEST_IDENTITY", "/sources", `missing feature source ${featureId}`);
  }
  if (totalSize !== value.total_size_bytes) throw new SourceManifestError("SFC_SOURCE_MANIFEST_SIZE", "/total_size_bytes", "total source size is stale");
  if (sha256(rows.join("")) !== value.aggregate_sha256) throw new SourceManifestError("SFC_SOURCE_MANIFEST_DIGEST", "/aggregate_sha256", "aggregate digest is stale");
  const { manifest_sha256: ignored, ...body } = value;
  if (sha256(canonicalJson(body)) !== value.manifest_sha256) throw new SourceManifestError("SFC_SOURCE_MANIFEST_DIGEST", "/manifest_sha256", "manifest digest is stale");
  return value as unknown as SourceManifestV1;
}

export function buildSourceManifest(projectId: string, inputs: readonly SourceInput[]): SourceManifestV1 {
  const sources = inputs
    .map((input): SourceManifestEntry => ({
      source_type: input.sourceType,
      source_id: input.sourceId,
      feature_id: input.featureId,
      relative_path: input.relativePath,
      size_bytes: input.bytes.length,
      sha256: sha256(input.bytes)
    }))
    .sort((left, right) => left.relative_path.localeCompare(right.relative_path) || left.source_id.localeCompare(right.source_id));

  const relativePaths = new Set<string>();
  const identities = new Set<string>();
  for (const source of sources) {
    if (relativePaths.has(source.relative_path)) throw new Error(`duplicate source path ${source.relative_path}`);
    relativePaths.add(source.relative_path);
    const identity = `${source.source_type}:${source.source_id}`;
    if (identities.has(identity)) throw new Error(`duplicate source identity ${identity}`);
    identities.add(identity);
  }

  const aggregateRows = sources.map((source) =>
    `${source.source_type}\t${source.source_id}\t${source.feature_id ?? "-"}\t${source.relative_path}\t${source.size_bytes}\t${source.sha256}\n`
  );
  const body = {
    schema_version: "domainspec.stable-foundation-cli.source-manifest/v1" as const,
    project_id: projectId,
    source_count: sources.length,
    total_size_bytes: sources.reduce((total, source) => total + source.size_bytes, 0),
    sources,
    aggregate_sha256: sha256(aggregateRows.join("")),
    authority_effect: "none" as const
  };
  return { ...body, manifest_sha256: sha256(canonicalJson(body)) };
}
