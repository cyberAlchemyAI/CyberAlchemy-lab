import { createHash } from "node:crypto";
import {
  existsSync,
  lstatSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  realpathSync,
  renameSync,
  rmdirSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import {
  basename,
  dirname,
  isAbsolute,
  posix,
  relative,
  resolve,
  win32,
} from "node:path";
import { fileURLToPath } from "node:url";

import { buildMintedProjectViews, MINTED_PROJECT_GENERATOR_VERSION } from "./views";

export const MINTED_PROJECT_MINTER_ERROR_CODES = [
  "PROJECT_ID_INVALID",
  "DESTINATION_PARENT_INVALID",
  "DESTINATION_EXISTS",
  "DESTINATION_NOT_DIRECTORY",
  "DESTINATION_NOT_EMPTY",
  "GENERATED_ROOT_INVALID",
  "GENERATED_ROOT_ESCAPE",
  "GENERATED_ROOT_CONFLICT",
  "LANGUAGE_UNSUPPORTED",
  "DEVELOPMENT_PROFILE_INVALID",
  "PACKAGE_UNAVAILABLE",
  "STAGING_BUILD_FAILED",
  "LEAKAGE_DETECTED",
  "PROMOTION_FAILED",
  "MINT_FAILED",
] as const;

export type MintedProjectMinterErrorCode =
  (typeof MINTED_PROJECT_MINTER_ERROR_CODES)[number];

export class MintedProjectMinterError extends Error {
  readonly code: MintedProjectMinterErrorCode;

  constructor(code: MintedProjectMinterErrorCode, detail: string, options?: ErrorOptions) {
    super(`${code}:${detail}`, options);
    this.name = "MintedProjectMinterError";
    this.code = code;
  }
}

export interface MintedProjectMintOptions {
  destination: string;
  projectId: string;
  generatedRoot?: string;
  profile?: { id: string; version: string };
  developmentProfileRegistry?: { path: string; handle: string };
  acceptExistingEmpty?: boolean;
}

export interface MintedProjectMinterHooks {
  afterStageWrite?: (stagingRoot: string) => void;
}

export interface MintedProjectMintReceipt {
  schema_version: "minted-project-mint-receipt/v1";
  status: "pass";
  project_id: string;
  generated_root: string;
  language: {
    profile_id: string;
    profile_version: string;
    profile_digest: string;
    kinds_digest: string;
    relationships_digest: string;
  };
  template_digest: string;
  schema_handles: Array<{ id: string; digest: string }>;
  tool_handles: Array<{ id: string; version: string; digest: string }>;
  created_paths: string[];
  build_receipt_digest: string;
}

export interface MintedProjectMintResult {
  projectRoot: string;
  receipt: MintedProjectMintReceipt;
}

type SupportedProfileRegistry = {
  schema_version?: string;
  authority?: string | Record<string, unknown>;
  release_admission?: string;
  handle?: string;
  registry_bindings: {
    kinds: { sha256: string };
    relationships: { sha256: string };
  };
  profiles: Array<{ id: string; version: string; status: string }>;
};

type ContractManifest = {
  schemas: Array<{ file: string; schema_id: string }>;
};

const thisFile = fileURLToPath(import.meta.url);
const toolRoot = dirname(thisFile);
const implRoot = resolve(toolRoot, "../..");
const domainspecRoot = resolve(implRoot, "..");
const templateRoot = resolve(toolRoot, "templates/project");
const profilePath = resolve(domainspecRoot, "definitions/minted-project/supported-profiles.yml");
const schemaRoot = resolve(implRoot, "spec/minted-project");
const contractManifestPath = resolve(schemaRoot, "contract-manifest.json");

const forbiddenContent = [
  "key-and-door",
  "financial-settlement",
  "agent-execution-orchestrator",
  "domainspec-core",
  "cyberalchemy-v2",
  "authority spine",
  "three pillars",
  "saturn",
];

function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

function sha256File(path: string): string {
  return sha256(readFileSync(path));
}

function jsonBytes(value: unknown): string {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function contained(root: string, candidate: string): boolean {
  const delta = relative(root, candidate);
  return delta === "" || (!delta.startsWith("..") && !isAbsolute(delta));
}

function filesBelow(root: string): string[] {
  const visit = (directory: string): string[] => readdirSync(directory, { withFileTypes: true })
    .flatMap((entry) => {
      const path = resolve(directory, entry.name);
      return entry.isDirectory() ? visit(path) : [relative(root, path).replaceAll("\\", "/")];
    });
  return visit(root).sort();
}

function templateDigest(): string {
  const hash = createHash("sha256");
  for (const path of filesBelow(templateRoot)) {
    hash.update(path);
    hash.update("\0");
    hash.update(readFileSync(resolve(templateRoot, path)));
    hash.update("\0");
  }
  return hash.digest("hex");
}

function copyTemplate(
  destination: string,
  replacements: Record<string, string>,
): string[] {
  const created: string[] = [];
  for (const templatePath of filesBelow(templateRoot)) {
    const outputPath = templatePath.endsWith(".template")
      ? templatePath.slice(0, -".template".length)
      : templatePath;
    const target = resolve(destination, outputPath);
    mkdirSync(dirname(target), { recursive: true });
    let content = readFileSync(resolve(templateRoot, templatePath), "utf8");
    for (const [token, value] of Object.entries(replacements)) {
      content = content.replaceAll(`{{${token}}}`, value);
    }
    writeFileSync(target, content);
    created.push(outputPath);
  }
  return created.sort();
}

function validateGeneratedRoot(projectRoot: string, input: string): { path: string; value: string } {
  if (
    input.length === 0 ||
    input.includes("\\") ||
    isAbsolute(input) ||
    win32.isAbsolute(input)
  ) {
    throw new MintedProjectMinterError(
      "GENERATED_ROOT_INVALID",
      "generated_root must be a non-empty portable project-relative path",
    );
  }
  const segments = input.split("/");
  if (segments.some((segment) => segment === "..")) {
    throw new MintedProjectMinterError(
      "GENERATED_ROOT_ESCAPE",
      "generated_root cannot contain parent traversal",
    );
  }
  const value = posix.normalize(input);
  if (value === "." || value.startsWith("../") || value === "..") {
    throw new MintedProjectMinterError(
      "GENERATED_ROOT_ESCAPE",
      "generated_root must be a nested project directory",
    );
  }
  if (value === "specs" || value.startsWith("specs/")) {
    throw new MintedProjectMinterError(
      "GENERATED_ROOT_CONFLICT",
      "generated_root cannot overlap canonical source roots",
    );
  }
  const path = resolve(projectRoot, ...value.split("/"));
  if (!contained(projectRoot, path)) {
    throw new MintedProjectMinterError(
      "GENERATED_ROOT_ESCAPE",
      "resolved generated_root escapes the project",
    );
  }
  return { path, value };
}

function readResources(
  development?: { path: string; handle: string },
): {
  registry: SupportedProfileRegistry;
  profileDigest: string;
  manifest: ContractManifest;
} {
  try {
    const selectedPath = development ? resolve(development.path) : profilePath;
    const registry = JSON.parse(readFileSync(selectedPath, "utf8")) as SupportedProfileRegistry;
    if (
      development &&
      (registry.schema_version !== "domainspec-development-minted-profile/v0.1" ||
        registry.authority !== "implementation-owned-development-profile" ||
        registry.release_admission !== "not-granted" ||
        registry.handle !== development.handle)
    ) {
      throw new MintedProjectMinterError(
        "DEVELOPMENT_PROFILE_INVALID",
        "development registry contract or handle does not match",
      );
    }
    return {
      registry,
      profileDigest: sha256File(selectedPath),
      manifest: JSON.parse(readFileSync(contractManifestPath, "utf8")) as ContractManifest,
    };
  } catch (error) {
    if (error instanceof MintedProjectMinterError) throw error;
    throw new MintedProjectMinterError(
      "PACKAGE_UNAVAILABLE",
      "minted-project profile or schema package is unavailable",
      { cause: error },
    );
  }
}

function leakageViolations(root: string): string[] {
  const violations: string[] = [];
  for (const path of filesBelow(root)) {
    const content = readFileSync(resolve(root, path), "utf8");
    const lower = content.toLowerCase();
    for (const token of forbiddenContent) {
      if (lower.includes(token)) {
        violations.push(`${path}:${token}`);
      }
    }
    if (/\/home\//i.test(content) || /[a-z]:\\\\/i.test(content)) {
      violations.push(`${path}:local-checkout-path`);
    }
  }
  return violations.sort();
}

function inspectDestination(
  destination: string,
  acceptExistingEmpty: boolean,
): { existedEmpty: boolean } {
  if (!existsSync(destination)) {
    return { existedEmpty: false };
  }
  const entry = lstatSync(destination);
  if (!entry.isDirectory() || entry.isSymbolicLink()) {
    throw new MintedProjectMinterError(
      "DESTINATION_NOT_DIRECTORY",
      "destination exists and is not a real directory",
    );
  }
  if (readdirSync(destination).length > 0) {
    throw new MintedProjectMinterError(
      "DESTINATION_NOT_EMPTY",
      "destination contains existing entries",
    );
  }
  if (!acceptExistingEmpty) {
    throw new MintedProjectMinterError(
      "DESTINATION_EXISTS",
      "destination already exists; explicit empty-directory acceptance is required",
    );
  }
  return { existedEmpty: true };
}

export function mintMintedProject(
  options: MintedProjectMintOptions,
  hooks: MintedProjectMinterHooks = {},
): MintedProjectMintResult {
  if (!/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(options.projectId)) {
    throw new MintedProjectMinterError(
      "PROJECT_ID_INVALID",
      "projectId must be a lowercase kebab-case identity",
    );
  }

  const requestedDestination = resolve(options.destination);
  let parent: string;
  try {
    parent = realpathSync(dirname(requestedDestination));
    if (!statSync(parent).isDirectory()) {
      throw new Error("not a directory");
    }
  } catch (error) {
    throw new MintedProjectMinterError(
      "DESTINATION_PARENT_INVALID",
      "destination parent must be an existing directory",
      { cause: error },
    );
  }
  const destination = resolve(parent, basename(requestedDestination));
  const { existedEmpty } = inspectDestination(
    destination,
    options.acceptExistingEmpty ?? false,
  );
  const generatedRootInput = options.generatedRoot ?? ".domainspec/generated";
  const resources = readResources(options.developmentProfileRegistry);
  const selectedProfile = options.profile ?? {
    id: "feature-with-independent-node-files",
    version: "1",
  };
  const profile = resources.registry.profiles.find(
    (candidate) =>
      candidate.id === selectedProfile.id &&
      candidate.version === selectedProfile.version &&
      candidate.status ===
        (options.developmentProfileRegistry ? "development-only" : "experimental"),
  );
  if (!profile) {
    throw new MintedProjectMinterError(
      "LANGUAGE_UNSUPPORTED",
      `${selectedProfile.id}@${selectedProfile.version}`,
    );
  }

  const stagingRoot = mkdtempSync(resolve(parent, `.${basename(destination)}.staging-`));
  let promoted = false;
  try {
    const generated = validateGeneratedRoot(stagingRoot, generatedRootInput);
    const createdPaths = copyTemplate(stagingRoot, {
      PROJECT_ID: options.projectId,
      GENERATED_ROOT: generated.value,
      PROFILE_ID: profile.id,
      PROFILE_VERSION: profile.version,
      GENERATOR_VERSION: MINTED_PROJECT_GENERATOR_VERSION,
    });
    const project = {
      schema_version: "minted-project/v1",
      project_id: options.projectId,
      language: {
        profile: {
          id: profile.id,
          version: profile.version,
          digest: resources.profileDigest,
        },
        registries: {
          kinds_digest: resources.registry.registry_bindings.kinds.sha256,
          relationships_digest: resources.registry.registry_bindings.relationships.sha256,
        },
      },
      features: [],
      generated_root: generated.value,
    };
    writeFileSync(resolve(stagingRoot, "project.json"), jsonBytes(project));
    createdPaths.push("project.json");

    let build;
    try {
      build = buildMintedProjectViews(
        stagingRoot,
        options.developmentProfileRegistry
          ? { developmentProfileRegistry: options.developmentProfileRegistry }
          : {},
      );
    } catch (error) {
      throw new MintedProjectMinterError(
        "STAGING_BUILD_FAILED",
        "staging project failed contract compile/view validation",
        { cause: error },
      );
    }
    mkdirSync(generated.path, { recursive: true });
    const generatedFiles: Array<[string, string]> = [
      ["graph.json", build.graphBytes],
      ["source-manifest.json", build.sourceManifestBytes],
      ["SPEC.md", build.markdownBytes],
      ["markdown-view.json", build.markdownViewBytes],
      ["build-receipt.json", build.buildReceiptBytes],
    ];
    for (const [name, content] of generatedFiles) {
      writeFileSync(resolve(generated.path, name), content);
      createdPaths.push(posix.join(generated.value, name));
    }

    hooks.afterStageWrite?.(stagingRoot);
    const leakage = leakageViolations(stagingRoot);
    if (leakage.length > 0) {
      throw new MintedProjectMinterError("LEAKAGE_DETECTED", leakage.join(","));
    }

    const schemaHandles = resources.manifest.schemas
      .map((schema) => ({ id: schema.schema_id, digest: sha256File(resolve(schemaRoot, schema.file)) }))
      .sort((left, right) => left.id.localeCompare(right.id));
    const toolHandles = [
      { id: "compiler", version: MINTED_PROJECT_GENERATOR_VERSION, digest: sha256File(resolve(toolRoot, "compiler.ts")) },
      { id: "minter", version: MINTED_PROJECT_GENERATOR_VERSION, digest: sha256File(thisFile) },
      { id: "views", version: MINTED_PROJECT_GENERATOR_VERSION, digest: sha256File(resolve(toolRoot, "views.ts")) },
    ];
    const receipt: MintedProjectMintReceipt = {
      schema_version: "minted-project-mint-receipt/v1",
      status: "pass",
      project_id: options.projectId,
      generated_root: generated.value,
      language: {
        profile_id: profile.id,
        profile_version: profile.version,
        profile_digest: resources.profileDigest,
        kinds_digest: resources.registry.registry_bindings.kinds.sha256,
        relationships_digest: resources.registry.registry_bindings.relationships.sha256,
      },
      template_digest: templateDigest(),
      schema_handles: schemaHandles,
      tool_handles: toolHandles,
      created_paths: [...createdPaths].sort(),
      build_receipt_digest: sha256(build.buildReceiptBytes),
    };

    if (existedEmpty) {
      rmdirSync(destination);
    }
    try {
      renameSync(stagingRoot, destination);
      promoted = true;
    } catch (error) {
      if (existedEmpty && !existsSync(destination)) {
        mkdirSync(destination);
      }
      throw new MintedProjectMinterError(
        "PROMOTION_FAILED",
        "staging project could not be atomically promoted",
        { cause: error },
      );
    }
    return { projectRoot: destination, receipt };
  } catch (error) {
    if (error instanceof MintedProjectMinterError) {
      throw error;
    }
    throw new MintedProjectMinterError("MINT_FAILED", "mint interrupted before promotion", {
      cause: error,
    });
  } finally {
    if (!promoted && existsSync(stagingRoot)) {
      rmSync(stagingRoot, { force: true, recursive: true });
    }
  }
}
