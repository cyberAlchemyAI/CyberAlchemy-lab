import fs from "node:fs";
import path from "node:path";

import { canonicalJson, sha256 } from "../input/source-manifest.js";
import { MAX_JSON_DEPTH, MAX_SOURCE_FILE_BYTES, readBoundedFileSync } from "../input/limits.js";

export const DEPLOYMENT_RECIPE_TARGET = "aws-ecs-fargate-postgres-v1" as const;

export interface DeploymentRecipeRequestV1 {
  readonly schema_version: "domainspec.deployment-recipe-request/v1";
  readonly request_id: string;
  readonly target: typeof DEPLOYMENT_RECIPE_TARGET;
  readonly application: Readonly<{
    language: "typescript";
    source_root: string;
    lockfile: string;
    base_image: string;
    api: Readonly<{ entrypoint: readonly string[]; port: number; health_path: string }>;
    worker: Readonly<{ entrypoint: readonly string[] }>;
    consumer: Readonly<{ entrypoint: readonly string[] }>;
    domain_migrations_root: string;
  }>;
  readonly integration_binding_ids: readonly string[];
  readonly environment: Readonly<{ name_variable: string; aws_region_variable: string }>;
  readonly authority_effect: "none";
}

export interface DeploymentRecipeArtifactV1 {
  readonly relative_path: string;
  readonly size_bytes: number;
  readonly sha256: string;
}

export interface PlannedDeploymentRecipeArtifactV1 extends DeploymentRecipeArtifactV1 {
  readonly content: string;
  readonly mode: 0o644;
}

export interface DeploymentRecipeComponentV1 {
  readonly component: "api" | "outbox-worker" | "postgresql" | "transactional-outbox" | "message-channel" | "message-publisher" | "message-consumer";
  readonly evidence_refs: readonly string[];
}

export interface DeploymentRecipeMessageV1 {
  readonly transport_binding_id: string;
  readonly event_ref: string;
  readonly publisher_operation_ref: string;
  readonly consumer_operation_refs: readonly string[];
  readonly channel_id: string;
  readonly dead_letter_channel_id: string;
  readonly visibility_timeout_seconds: number;
  readonly retention_seconds: number;
  readonly max_receive_count: number;
  readonly publish_max_attempts: number;
  readonly envelope_profile_ref: "envelope:domainspec-event-json-v1";
  readonly deduplication_owner_ref: "consumer:inbox-message-id";
}

export interface DeploymentRecipeBindingV1 {
  readonly binding_set_id: string;
  readonly binding_digest: string;
}

export interface DeploymentRecipeManifestV1 {
  readonly schema_version: "domainspec.deployment-recipe-manifest/v1";
  readonly request_id: string;
  readonly target: typeof DEPLOYMENT_RECIPE_TARGET;
  readonly project_id: string;
  readonly source_manifest_sha256: string;
  readonly compiled_certificate_sha256: string;
  readonly checked_interchange_sha256: string;
  readonly request_sha256: string;
  readonly target_implementation_sha256: string;
  readonly selected_node_selectors: readonly string[];
  readonly selected_relationship_edge_ids: readonly string[];
  readonly selected_binding_ids: readonly string[];
  readonly selected_bindings: readonly DeploymentRecipeBindingV1[];
  readonly components: readonly DeploymentRecipeComponentV1["component"][];
  readonly input_artifacts: readonly DeploymentRecipeArtifactV1[];
  readonly artifacts: readonly DeploymentRecipeArtifactV1[];
  readonly authority_effect: "none";
  readonly manifest_sha256: string;
}

export interface DeploymentRecipeReceiptV1 {
  readonly schema_version: "domainspec.deployment-recipe-receipt/v1";
  readonly request_id: string;
  readonly target: typeof DEPLOYMENT_RECIPE_TARGET;
  readonly project_id: string;
  readonly source_manifest_sha256: string;
  readonly compiled_certificate_sha256: string;
  readonly checked_interchange_sha256: string;
  readonly request_sha256: string;
  readonly target_implementation_sha256: string;
  readonly manifest_sha256: string;
  readonly plan_sha256: string;
  readonly artifact_count: number;
  readonly authority_effect: "none";
  readonly receipt_sha256: string;
}

export interface DeploymentRecipePlanV1 {
  readonly schema_version: "domainspec.deployment-recipe-plan/v1";
  readonly request: DeploymentRecipeRequestV1;
  readonly consumer_root: string;
  readonly components: readonly DeploymentRecipeComponentV1[];
  readonly messaging: DeploymentRecipeMessageV1;
  readonly manifest: DeploymentRecipeManifestV1;
  readonly receipt: DeploymentRecipeReceiptV1;
  readonly artifacts: readonly PlannedDeploymentRecipeArtifactV1[];
  readonly plan_sha256: string;
  readonly authority_effect: "none";
}

export class DeploymentRecipeError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(message);
    this.name = "DeploymentRecipeError";
  }
}

export function recipeFail(code: string, pointer: string, message: string): never {
  throw new DeploymentRecipeError(code, pointer, message);
}

function record(value: unknown, pointer: string): Record<string, unknown> {
  if (value === null || typeof value !== "object" || Array.isArray(value)) recipeFail("MTCLI_RECIPE_SCHEMA", pointer, "expected object");
  return value as Record<string, unknown>;
}

function exact(value: unknown, keys: readonly string[], pointer: string): Record<string, unknown> {
  const selected = record(value, pointer);
  if (canonicalJson(Object.keys(selected).sort()) !== canonicalJson([...keys].sort())) recipeFail("MTCLI_RECIPE_SCHEMA", pointer, "unexpected or missing member");
  return selected;
}

function text(value: unknown, pointer: string, maximum = 512): string {
  if (typeof value !== "string" || value.length === 0 || value.length > maximum || /[\0\r\n]/.test(value)) recipeFail("MTCLI_RECIPE_SCHEMA", pointer, "expected bounded single-line string");
  return value;
}

function identity(value: unknown, pointer: string): string {
  const selected = text(value, pointer, 128);
  if (!/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(selected)) recipeFail("MTCLI_RECIPE_ID", pointer, "expected lowercase kebab-case identity");
  return selected;
}

export function deploymentRecipeRelativePath(value: unknown, pointer: string): string {
  const selected = text(value, pointer);
  if (path.posix.isAbsolute(selected) || selected.includes("\\") || selected.split("/").some((part) => part === "" || part === "." || part === "..") || !/^[A-Za-z0-9._/-]+$/.test(selected)) {
    recipeFail("MTCLI_RECIPE_PATH", pointer, "path must be normalized, relative, portable, and contained");
  }
  return selected;
}

function entrypoint(value: unknown, pointer: string): readonly string[] {
  if (!Array.isArray(value) || value.length < 1 || value.length > 32) recipeFail("MTCLI_RECIPE_ENTRYPOINT", pointer, "entrypoint requires one through 32 arguments");
  return Object.freeze(value.map((item, index) => text(item, `${pointer}/${index}`)));
}

function environmentVariable(value: unknown, pointer: string): string {
  const selected = text(value, pointer, 128);
  if (!/^[a-z][a-z0-9_]*$/.test(selected)) recipeFail("MTCLI_RECIPE_VARIABLE", pointer, "expected lowercase Terraform variable identity");
  return selected;
}

export function decodeDeploymentRecipeRequest(value: unknown): DeploymentRecipeRequestV1 {
  const root = exact(value, ["schema_version", "request_id", "target", "application", "integration_binding_ids", "environment", "authority_effect"], "$request");
  if (root.schema_version !== "domainspec.deployment-recipe-request/v1") recipeFail("MTCLI_RECIPE_SCHEMA", "/schema_version", "unsupported deployment recipe request schema");
  if (root.target !== DEPLOYMENT_RECIPE_TARGET) recipeFail("MTCLI_RECIPE_TARGET", "/target", "unsupported deployment recipe target");
  if (root.authority_effect !== "none") recipeFail("MTCLI_RECIPE_AUTHORITY", "/authority_effect", "deployment recipe requests cannot authorize effects");
  const application = exact(root.application, ["language", "source_root", "lockfile", "base_image", "api", "worker", "consumer", "domain_migrations_root"], "/application");
  if (application.language !== "typescript") recipeFail("MTCLI_RECIPE_LANGUAGE", "/application/language", "the first recipe target supports TypeScript only");
  const baseImage = text(application.base_image, "/application/base_image");
  if (!/^[a-z0-9./_-]+:[A-Za-z0-9._-]+@sha256:[a-f0-9]{64}$/.test(baseImage)) recipeFail("MTCLI_RECIPE_IMAGE", "/application/base_image", "base image must include an immutable sha256 digest");
  const api = exact(application.api, ["entrypoint", "port", "health_path"], "/application/api");
  if (!Number.isInteger(api.port) || Number(api.port) < 1 || Number(api.port) > 65535) recipeFail("MTCLI_RECIPE_PORT", "/application/api/port", "port must be an integer from 1 through 65535");
  const healthPath = text(api.health_path, "/application/api/health_path", 256);
  if (!/^\/[A-Za-z0-9._~!$&'()*+,;=:@%/-]*$/.test(healthPath) || healthPath.includes("//")) recipeFail("MTCLI_RECIPE_HEALTH", "/application/api/health_path", "health path must be one normalized absolute URL path");
  const worker = exact(application.worker, ["entrypoint"], "/application/worker");
  const consumer = exact(application.consumer, ["entrypoint"], "/application/consumer");
  if (!Array.isArray(root.integration_binding_ids) || root.integration_binding_ids.length < 1 || root.integration_binding_ids.length > 64) recipeFail("MTCLI_RECIPE_BINDINGS", "/integration_binding_ids", "one through 64 integration binding IDs are required");
  const bindingIds = root.integration_binding_ids.map((item, index) => identity(item, `/integration_binding_ids/${index}`));
  if (new Set(bindingIds).size !== bindingIds.length) recipeFail("MTCLI_RECIPE_BINDINGS", "/integration_binding_ids", "integration binding IDs must be unique");
  const environment = exact(root.environment, ["name_variable", "aws_region_variable"], "/environment");
  const requestId = identity(root.request_id, "/request_id");
  if (requestId.length > 30) recipeFail("MTCLI_RECIPE_ID", "/request_id", "request identity must be at most 30 characters for the selected AWS target");
  const sourceRoot = deploymentRecipeRelativePath(application.source_root, "/application/source_root");
  const lockfile = deploymentRecipeRelativePath(application.lockfile, "/application/lockfile");
  if (lockfile !== "package-lock.json") recipeFail("MTCLI_RECIPE_APPLICATION", "/application/lockfile", "the TypeScript recipe requires package-lock.json at the application root");
  const migrationsRoot = deploymentRecipeRelativePath(application.domain_migrations_root, "/application/domain_migrations_root");
  if (sourceRoot === migrationsRoot || sourceRoot.startsWith(`${migrationsRoot}/`) || migrationsRoot.startsWith(`${sourceRoot}/`)) recipeFail("MTCLI_RECIPE_PATH_OVERLAP", "/application", "application and migration roots must not overlap");
  const nameVariable = environmentVariable(environment.name_variable, "/environment/name_variable");
  const regionVariable = environmentVariable(environment.aws_region_variable, "/environment/aws_region_variable");
  if (nameVariable === regionVariable) recipeFail("MTCLI_RECIPE_VARIABLE", "/environment", "environment and AWS region variable identities must be distinct");
  return Object.freeze({
    schema_version: "domainspec.deployment-recipe-request/v1",
    request_id: requestId,
    target: DEPLOYMENT_RECIPE_TARGET,
    application: Object.freeze({
      language: "typescript",
      source_root: sourceRoot,
      lockfile,
      base_image: baseImage,
      api: Object.freeze({ entrypoint: entrypoint(api.entrypoint, "/application/api/entrypoint"), port: Number(api.port), health_path: healthPath }),
      worker: Object.freeze({ entrypoint: entrypoint(worker.entrypoint, "/application/worker/entrypoint") }),
      consumer: Object.freeze({ entrypoint: entrypoint(consumer.entrypoint, "/application/consumer/entrypoint") }),
      domain_migrations_root: migrationsRoot,
    }),
    integration_binding_ids: Object.freeze([...bindingIds].sort()),
    environment: Object.freeze({ name_variable: nameVariable, aws_region_variable: regionVariable }),
    authority_effect: "none",
  });
}

class StrictJsonParser {
  private index = 0;
  constructor(private readonly source: string) {}

  parse(): unknown {
    const value = this.value("$", 0);
    this.space();
    if (this.index !== this.source.length) recipeFail("MTCLI_RECIPE_JSON", "$", `unexpected JSON token at byte ${this.index}`);
    return value;
  }

  private space(): void { while (/\s/.test(this.source[this.index] ?? "")) this.index++; }
  private value(pointer: string, depth: number): unknown {
    if (depth > MAX_JSON_DEPTH) recipeFail("MTCLI_RECIPE_JSON_DEPTH", pointer, `JSON nesting exceeds ${MAX_JSON_DEPTH}`);
    this.space();
    const token = this.source[this.index];
    if (token === "{") return this.object(pointer, depth + 1);
    if (token === "[") return this.array(pointer, depth + 1);
    if (token === '"') return this.string(pointer);
    for (const [literal, value] of [["true", true], ["false", false], ["null", null]] as const) {
      if (this.source.startsWith(literal, this.index)) { this.index += literal.length; return value; }
    }
    const match = this.source.slice(this.index).match(/^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/);
    if (match) { this.index += match[0].length; return Number(match[0]); }
    recipeFail("MTCLI_RECIPE_JSON", pointer, `invalid JSON value at byte ${this.index}`);
  }
  private object(pointer: string, depth: number): Record<string, unknown> {
    this.index++; this.space();
    const result = Object.create(null) as Record<string, unknown>;
    const keys = new Set<string>();
    if (this.source[this.index] === "}") { this.index++; return result; }
    while (true) {
      this.space();
      if (this.source[this.index] !== '"') recipeFail("MTCLI_RECIPE_JSON", pointer, "object key must be a JSON string");
      const key = this.string(pointer);
      if (keys.has(key)) recipeFail("MTCLI_RECIPE_DUPLICATE_KEY", `${pointer}/${key}`, `duplicate JSON member:${key}`);
      keys.add(key); this.space();
      if (this.source[this.index] !== ":") recipeFail("MTCLI_RECIPE_JSON", pointer, "object member requires a colon");
      this.index++;
      result[key] = this.value(`${pointer}/${key.replaceAll("~", "~0").replaceAll("/", "~1")}`, depth);
      this.space();
      if (this.source[this.index] === "}") { this.index++; return result; }
      if (this.source[this.index] !== ",") recipeFail("MTCLI_RECIPE_JSON", pointer, "object members require a comma");
      this.index++;
    }
  }
  private array(pointer: string, depth: number): unknown[] {
    this.index++; this.space();
    const result: unknown[] = [];
    if (this.source[this.index] === "]") { this.index++; return result; }
    while (true) {
      result.push(this.value(`${pointer}/${result.length}`, depth)); this.space();
      if (this.source[this.index] === "]") { this.index++; return result; }
      if (this.source[this.index] !== ",") recipeFail("MTCLI_RECIPE_JSON", pointer, "array members require a comma");
      this.index++;
    }
  }
  private string(pointer: string): string {
    const start = this.index++;
    let escaped = false;
    while (this.index < this.source.length) {
      const character = this.source[this.index++]!;
      if (!escaped && character === '"') {
        try { return JSON.parse(this.source.slice(start, this.index)) as string; }
        catch { recipeFail("MTCLI_RECIPE_JSON", pointer, "invalid JSON string"); }
      }
      if (!escaped && character.charCodeAt(0) < 0x20) recipeFail("MTCLI_RECIPE_JSON", pointer, "unescaped control character in JSON string");
      if (!escaped && character === "\\") escaped = true; else escaped = false;
    }
    recipeFail("MTCLI_RECIPE_JSON", pointer, "unterminated JSON string");
  }
}

export function parseDeploymentRecipeRequestJson(source: string): DeploymentRecipeRequestV1 {
  return decodeDeploymentRecipeRequest(new StrictJsonParser(source).parse());
}

export function readDeploymentRecipeRequest(file: string): DeploymentRecipeRequestV1 {
  if (!path.isAbsolute(file) || path.resolve(file) !== file) recipeFail("MTCLI_RECIPE_REQUEST_PATH", "/request", "request path must be normalized and absolute");
  let stats: fs.Stats;
  try { stats = fs.lstatSync(file); } catch { recipeFail("MTCLI_RECIPE_REQUEST_PATH", "/request", "request file does not exist"); }
  if (!stats.isFile() || stats.isSymbolicLink() || fs.realpathSync(file) !== file) recipeFail("MTCLI_RECIPE_REQUEST_PATH", "/request", "request must be one real regular file");
  let bytes: Buffer;
  try { bytes = readBoundedFileSync(file, MAX_SOURCE_FILE_BYTES); } catch { recipeFail("MTCLI_RECIPE_REQUEST_SIZE", "/request", `request exceeds ${MAX_SOURCE_FILE_BYTES} bytes`); }
  return parseDeploymentRecipeRequestJson(bytes.toString("utf8"));
}

export function deploymentRecipeRequestSha256(request: DeploymentRecipeRequestV1): string {
  return sha256(canonicalJson(request));
}

export function plannedRecipeArtifact(relativePath: string, content: string): PlannedDeploymentRecipeArtifactV1 {
  deploymentRecipeRelativePath(relativePath, `/artifacts/${relativePath}`);
  return Object.freeze({ relative_path: relativePath, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content), mode: 0o644 as const });
}

export function recipeArtifactInventory(artifacts: readonly PlannedDeploymentRecipeArtifactV1[]): readonly DeploymentRecipeArtifactV1[] {
  return Object.freeze(artifacts.map(({ relative_path, size_bytes, sha256: digest }) => Object.freeze({ relative_path, size_bytes, sha256: digest })));
}
