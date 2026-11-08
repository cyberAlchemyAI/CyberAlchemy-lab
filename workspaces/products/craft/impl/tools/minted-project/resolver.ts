import { createHash } from "node:crypto";
import {
  readFileSync,
  realpathSync,
  statSync,
} from "node:fs";
import {
  dirname,
  extname,
  isAbsolute,
  posix,
  relative,
  resolve,
  win32,
} from "node:path";

export const MINTED_PROJECT_RESOLVER_ERROR_CODES = [
  "PROJECT_ROOT_INVALID",
  "SOURCE_PATH_ABSOLUTE",
  "SOURCE_PATH_ESCAPE",
  "SOURCE_PATH_DUPLICATE",
  "SOURCE_PATH_CASE_COLLISION",
  "SOURCE_PATH_ALIAS",
  "SOURCE_PATH_SYMLINK_ESCAPE",
  "SOURCE_MISSING",
  "SOURCE_NOT_FILE",
  "SOURCE_UNREADABLE",
  "SOURCE_EXTENSION_UNSUPPORTED",
  "SOURCE_JSON_INVALID",
  "SOURCE_VERSION_UNSUPPORTED",
  "SOURCE_SHAPE_INVALID",
] as const;

export type MintedProjectResolverErrorCode =
  (typeof MINTED_PROJECT_RESOLVER_ERROR_CODES)[number];

export class MintedProjectResolverError extends Error {
  readonly code: MintedProjectResolverErrorCode;
  readonly sourcePath: string;

  constructor(
    code: MintedProjectResolverErrorCode,
    sourcePath: string,
    detail: string,
    options?: ErrorOptions,
  ) {
    super(`${code}:${sourcePath}:${detail}`, options);
    this.name = "MintedProjectResolverError";
    this.code = code;
    this.sourcePath = sourcePath;
  }
}

export interface MintedProjectSourceRecord {
  path: string;
  digest: string;
}

export interface ResolvedMintedProjectSources {
  projectRoot: string;
  projectPath: string;
  records: MintedProjectSourceRecord[];
  sourceSetDigest: string;
}

interface LoadedSource {
  path: string;
  bytes: Buffer;
}

interface ProjectEnvelope {
  schema_version?: unknown;
  features?: unknown;
}

interface FeatureEnvelope {
  schema_version?: unknown;
  node_sources?: unknown;
}

function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

function canonicalize(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map(canonicalize).join(",")}]`;
  }
  if (value !== null && typeof value === "object") {
    const record = value as Record<string, unknown>;
    return `{${Object.keys(record)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonicalize(record[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

function isContained(root: string, candidate: string): boolean {
  const delta = relative(root, candidate);
  return delta === "" || (!delta.startsWith("..") && !isAbsolute(delta));
}

function errorCode(error: unknown): string | undefined {
  if (typeof error !== "object" || error === null || !("code" in error)) {
    return undefined;
  }
  return String((error as { code: unknown }).code);
}

function parseEnvelope<T>(source: LoadedSource): T {
  try {
    return JSON.parse(source.bytes.toString("utf8")) as T;
  } catch (error) {
    throw new MintedProjectResolverError(
      "SOURCE_JSON_INVALID",
      source.path,
      "source is not valid JSON",
      { cause: error },
    );
  }
}

function stringArray(value: unknown, path: string, field: string): string[] {
  if (!Array.isArray(value) || value.some((entry) => typeof entry !== "string" || entry.length === 0)) {
    throw new MintedProjectResolverError(
      "SOURCE_SHAPE_INVALID",
      path,
      `${field} must be an array of non-empty strings`,
    );
  }
  return value as string[];
}

export function resolveMintedProjectSources(
  projectRootInput: string,
  projectManifestPath = "project.json",
): ResolvedMintedProjectSources {
  let projectRoot: string;
  try {
    projectRoot = realpathSync(projectRootInput);
    if (!statSync(projectRoot).isDirectory()) {
      throw new Error("not a directory");
    }
  } catch (error) {
    throw new MintedProjectResolverError(
      "PROJECT_ROOT_INVALID",
      projectRootInput,
      "project root must be an existing readable directory",
      { cause: error },
    );
  }

  const records: MintedProjectSourceRecord[] = [];
  const logicalPaths = new Map<string, string>();
  const realPaths = new Map<string, string>();

  const load = (reference: string, declaringPath = ""): LoadedSource => {
    const portableReference = reference.replaceAll("\\", "/");
    if (
      isAbsolute(reference) ||
      win32.isAbsolute(reference) ||
      portableReference.startsWith("//")
    ) {
      throw new MintedProjectResolverError(
        "SOURCE_PATH_ABSOLUTE",
        reference,
        "source references must be project-relative",
      );
    }
    if (
      portableReference.length === 0 ||
      portableReference.split("/").some((segment) => segment === "..")
    ) {
      throw new MintedProjectResolverError(
        "SOURCE_PATH_ESCAPE",
        reference,
        "source references cannot escape the declaring directory",
      );
    }

    const declaringDirectory = declaringPath === "" ? "" : posix.dirname(declaringPath);
    const projectRelativePath = posix.normalize(posix.join(declaringDirectory, portableReference));
    if (
      projectRelativePath === "." ||
      projectRelativePath.startsWith("../") ||
      projectRelativePath === ".."
    ) {
      throw new MintedProjectResolverError(
        "SOURCE_PATH_ESCAPE",
        reference,
        "normalized source path escapes the project root",
      );
    }
    if (extname(projectRelativePath) !== ".json") {
      throw new MintedProjectResolverError(
        "SOURCE_EXTENSION_UNSUPPORTED",
        projectRelativePath,
        "v1 sources must use the lowercase .json extension",
      );
    }

    const lexicalPath = resolve(projectRoot, ...projectRelativePath.split("/"));
    if (!isContained(projectRoot, lexicalPath)) {
      throw new MintedProjectResolverError(
        "SOURCE_PATH_ESCAPE",
        projectRelativePath,
        "resolved source path escapes the project root",
      );
    }

    let realPath: string;
    try {
      realPath = realpathSync(lexicalPath);
    } catch (error) {
      const code = errorCode(error);
      throw new MintedProjectResolverError(
        code === "ENOENT" ? "SOURCE_MISSING" : "SOURCE_UNREADABLE",
        projectRelativePath,
        code === "ENOENT" ? "declared source does not exist" : "declared source cannot be resolved",
        { cause: error },
      );
    }
    if (!isContained(projectRoot, realPath)) {
      throw new MintedProjectResolverError(
        "SOURCE_PATH_SYMLINK_ESCAPE",
        projectRelativePath,
        "source symlink resolves outside the project root",
      );
    }
    try {
      if (!statSync(realPath).isFile()) {
        throw new MintedProjectResolverError(
          "SOURCE_NOT_FILE",
          projectRelativePath,
          "declared source is not a regular file",
        );
      }
    } catch (error) {
      if (error instanceof MintedProjectResolverError) {
        throw error;
      }
      throw new MintedProjectResolverError(
        "SOURCE_UNREADABLE",
        projectRelativePath,
        "declared source metadata cannot be read",
        { cause: error },
      );
    }

    const foldedPath = projectRelativePath.toLocaleLowerCase("en-US");
    const priorLogical = logicalPaths.get(foldedPath);
    if (priorLogical !== undefined) {
      throw new MintedProjectResolverError(
        priorLogical === projectRelativePath
          ? "SOURCE_PATH_DUPLICATE"
          : "SOURCE_PATH_CASE_COLLISION",
        projectRelativePath,
        `source collides with ${priorLogical}`,
      );
    }
    const priorReal = realPaths.get(realPath);
    if (priorReal !== undefined) {
      throw new MintedProjectResolverError(
        "SOURCE_PATH_ALIAS",
        projectRelativePath,
        `source aliases ${priorReal}`,
      );
    }

    let bytes: Buffer;
    try {
      bytes = readFileSync(realPath);
    } catch (error) {
      throw new MintedProjectResolverError(
        "SOURCE_UNREADABLE",
        projectRelativePath,
        "declared source bytes cannot be read",
        { cause: error },
      );
    }
    logicalPaths.set(foldedPath, projectRelativePath);
    realPaths.set(realPath, projectRelativePath);
    records.push({ path: projectRelativePath, digest: sha256(bytes) });
    return { path: projectRelativePath, bytes };
  };

  const projectSource = load(projectManifestPath);
  const project = parseEnvelope<ProjectEnvelope>(projectSource);
  if (project.schema_version !== "minted-project/v1") {
    throw new MintedProjectResolverError(
      "SOURCE_VERSION_UNSUPPORTED",
      projectSource.path,
      `expected minted-project/v1, got ${String(project.schema_version)}`,
    );
  }

  for (const featureReference of stringArray(project.features, projectSource.path, "features")) {
    const featureSource = load(featureReference, projectSource.path);
    const feature = parseEnvelope<FeatureEnvelope>(featureSource);
    if (feature.schema_version !== "minted-feature/v1") {
      throw new MintedProjectResolverError(
        "SOURCE_VERSION_UNSUPPORTED",
        featureSource.path,
        `expected minted-feature/v1, got ${String(feature.schema_version)}`,
      );
    }
    for (const nodeReference of stringArray(feature.node_sources, featureSource.path, "node_sources")) {
      load(nodeReference, featureSource.path);
    }
  }

  const orderedRecords = [...records].sort((left, right) => left.path.localeCompare(right.path));
  return {
    projectRoot,
    projectPath: projectSource.path,
    records: orderedRecords,
    sourceSetDigest: sha256(`${canonicalize(orderedRecords)}\n`),
  };
}
