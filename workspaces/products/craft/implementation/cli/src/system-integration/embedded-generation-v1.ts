import type { PlannedArtifact } from "../generation/contracts.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import {
  planIntegrationProjectV2,
  type IntegrationGenerationSourceV2,
  type IntegrationSemanticManifestV1,
} from "./generation-v2.js";
import type { IntegrationGenerationLanguage } from "./integration-project-layout-v1.js";

export interface RootManifestContributionV1 {
  readonly manifest_kind: "typescript" | "python" | "rust";
  readonly dependencies: readonly string[];
  readonly source_globs: readonly string[];
}

export interface EmbeddedIntegrationContributionV1 {
  readonly schema_version: "domainspec.embedded-integration-contribution/v1-candidate";
  readonly language: IntegrationGenerationLanguage;
  readonly source_id: string;
  readonly source_sha256: string;
  readonly standalone_plan_sha256: string;
  readonly semantic_manifest: IntegrationSemanticManifestV1;
  readonly owned_artifacts: readonly PlannedArtifact[];
  readonly root_manifest_contribution: RootManifestContributionV1;
  readonly module_contributions: readonly Readonly<{ relative_path: string; sha256: string }>[];
  readonly runtime_guarantees_observed: false;
  readonly authority_effect: "none";
  readonly contribution_sha256: string;
}

export class EmbeddedIntegrationGenerationError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(`${code}:${pointer}:${message}`);
    this.name = "EmbeddedIntegrationGenerationError";
  }
}

const contributions = new WeakMap<EmbeddedIntegrationContributionV1, string>();

function fail(code: string, pointer: string, message: string): never {
  throw new EmbeddedIntegrationGenerationError(code, pointer, message);
}

function freeze<T>(value: T): T {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const child of Object.values(value as Record<string, unknown>)) freeze(child);
  }
  return value;
}

function artifact(relativePath: string, content: string): PlannedArtifact {
  return freeze({ relative_path: relativePath, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content) });
}

function embeddedArtifact(value: PlannedArtifact, language: IntegrationGenerationLanguage): PlannedArtifact {
  if (language !== "typescript" || value.relative_path !== "src/features/integration/application/contracts.ts") return value;
  const content = `import type {ApplicationInput,ApplicationResult} from "../../../integrations/domain-bindings.js";\n${value.content.replaceAll("Readonly<Record<string, unknown>>", "ApplicationInput").replaceAll("Promise<unknown>", "Promise<ApplicationResult>")}`;
  return artifact(value.relative_path, content);
}

function rootPath(language: IntegrationGenerationLanguage): string {
  return language === "typescript" ? "tsconfig.json" : language === "python" ? "pyproject.toml" : "Cargo.toml";
}

function manifestContribution(language: IntegrationGenerationLanguage): RootManifestContributionV1 {
  return freeze({
    manifest_kind: language,
    dependencies: Object.freeze([]),
    source_globs: Object.freeze(language === "typescript" ? ["src/**/*.ts", "migrations/**/*.ts"] : language === "python" ? ["src/**/*.py", "migrations/**/*.py"] : ["src/**/*.rs", "migrations/**/*.rs"]),
  });
}

export function assertEmbeddedIntegrationContribution(value: unknown): asserts value is EmbeddedIntegrationContributionV1 {
  if (value === null || typeof value !== "object" || contributions.get(value as EmbeddedIntegrationContributionV1) !== sha256(canonicalJson(value))) {
    fail("DS_EMBEDDED_INTEGRATION_SNAPSHOT", "/contribution", "contribution was not formed by the current process or has changed");
  }
}

export function planEmbeddedIntegrationContributionV1(source: IntegrationGenerationSourceV2, language: IntegrationGenerationLanguage): EmbeddedIntegrationContributionV1 {
  const standalone = planIntegrationProjectV2(source, language);
  const root = rootPath(language);
  const ownedArtifacts = Object.freeze(standalone.artifacts.filter(item => item.relative_path !== root).map(item => embeddedArtifact(item, language)));
  if (ownedArtifacts.some(item => item.relative_path === "runtime" || item.relative_path.startsWith("runtime/"))) {
    fail("DS_EMBEDDED_INTEGRATION_RUNTIME_DIRECTORY", "/owned_artifacts", "generic runtime directory is forbidden");
  }
  if (ownedArtifacts.length !== standalone.artifacts.length - 1) {
    fail("DS_EMBEDDED_INTEGRATION_ROOT_MANIFEST", "/owned_artifacts", `expected exactly one standalone root manifest:${root}`);
  }
  const body = {
    schema_version: "domainspec.embedded-integration-contribution/v1-candidate" as const,
    language,
    source_id: source.source_id,
    source_sha256: sha256(canonicalJson(source)),
    standalone_plan_sha256: standalone.plan_digest,
    semantic_manifest: standalone.semantic_manifest,
    owned_artifacts: ownedArtifacts,
    root_manifest_contribution: manifestContribution(language),
    module_contributions: Object.freeze(ownedArtifacts.filter(item => item.relative_path.endsWith(language === "typescript" ? ".ts" : language === "python" ? ".py" : ".rs")).map(item => Object.freeze({ relative_path: item.relative_path, sha256: item.sha256 }))),
    runtime_guarantees_observed: false as const,
    authority_effect: "none" as const,
  };
  const result = freeze({ ...body, contribution_sha256: sha256(canonicalJson(body)) });
  contributions.set(result, sha256(canonicalJson(result)));
  return result;
}
