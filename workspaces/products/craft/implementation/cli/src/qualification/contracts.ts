import fs from "node:fs";
import path from "node:path";

import { MAX_JSON_DEPTH, MAX_SOURCE_FILE_BYTES, readBoundedFileSync } from "../input/limits.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import { DEPLOYMENT_RECIPE_TARGET, type DeploymentRecipeArtifactV1 } from "../recipe/contracts.js";

export const RECIPE_QUALIFICATION_LEVEL = "recipe-executable-v1" as const;
export const RECIPE_QUALIFICATION_ONTOLOGY = "domainspec.recipe-qualification-ontology@1" as const;
export const RECIPE_QUALIFICATION_ADAPTER_PROTOCOL = "domainspec.oci-tool-adapter/v1" as const;
export const RECIPE_QUALIFICATION_TERRAFORM_IMAGE = "hashicorp/terraform:1.16.0@sha256:fb5ea091b84f35e111e3a83eb8a6cdeb264bba11687c2eebc52253ade183022f" as const;
export const RECIPE_QUALIFICATION_DOCKER_IMAGE = "docker:28.0.1-cli@sha256:043c259759666d273afa94a9c9175a87a11f16cde2f613f4c527e4395b703a1f" as const;
export const RECIPE_QUALIFICATION_REQUIRED_CHECKS = Object.freeze([
  "recipe-byte-verify",
  "terraform-fmt-check",
  "terraform-init-backendless",
  "terraform-validate",
  "docker-buildx-bake-check",
] as const);

export type RecipeQualificationCheckId = typeof RECIPE_QUALIFICATION_REQUIRED_CHECKS[number];
export type RecipeQualificationResult = "pass" | "fail" | "not_evaluable";
export type RecipeQualificationAdapterId =
  | "recipe-byte-verify-v1"
  | "terraform-fmt-check-v1"
  | "terraform-init-backendless-v1"
  | "terraform-validate-v1"
  | "docker-buildx-bake-check-v1";

export interface RecipeQualificationProfileV1 {
  readonly schema_version: "domainspec.recipe-qualification-profile/v1";
  readonly profile_id: string;
  readonly ontology_id: typeof RECIPE_QUALIFICATION_ONTOLOGY;
  readonly qualification_level: typeof RECIPE_QUALIFICATION_LEVEL;
  readonly recipe_target: typeof DEPLOYMENT_RECIPE_TARGET;
  readonly required_checks: readonly RecipeQualificationCheckId[];
  readonly optional_checks: readonly [];
  readonly toolchain: Readonly<{
    terraform: Readonly<{ version: string; adapter_protocol: typeof RECIPE_QUALIFICATION_ADAPTER_PROTOCOL; image: typeof RECIPE_QUALIFICATION_TERRAFORM_IMAGE }>;
    docker: Readonly<{ version: string; buildx_version: string; adapter_protocol: typeof RECIPE_QUALIFICATION_ADAPTER_PROTOCOL; image: typeof RECIPE_QUALIFICATION_DOCKER_IMAGE }>;
  }>;
  readonly network_policy: "provider-registry-read-only";
  readonly normalization_profile: "domainspec.recipe-qualification-normalization/v1";
  readonly effect_ceiling: "no-external-effect";
  readonly authority_effect: "none";
  readonly profile_sha256: string;
}

export interface RecipeQualificationSubjectV1 {
  readonly request_id: string;
  readonly target: typeof DEPLOYMENT_RECIPE_TARGET;
  readonly project_id: string;
  readonly source_manifest_sha256: string;
  readonly compiled_certificate_sha256: string;
  readonly checked_interchange_sha256: string;
  readonly request_sha256: string;
  readonly target_implementation_sha256: string;
  readonly manifest_sha256: string;
  readonly recipe_plan_sha256: string;
  readonly recipe_receipt_sha256: string;
  readonly artifact_inventory_sha256: string;
}

export interface RecipeQualificationPlannedCheckV1 {
  readonly check_id: RecipeQualificationCheckId;
  readonly adapter_id: RecipeQualificationAdapterId;
  readonly predicate_id: string;
  readonly effect_class: "pure" | "bounded-local-cache" | "network-read-only";
  readonly input_sha256: string;
  readonly required: true;
}

export interface RecipeQualificationPlanV1 {
  readonly schema_version: "domainspec.recipe-qualification-plan/v1";
  readonly subject: RecipeQualificationSubjectV1;
  readonly profile_id: string;
  readonly profile_sha256: string;
  readonly checks: readonly RecipeQualificationPlannedCheckV1[];
  readonly authority_effect: "none";
  readonly plan_sha256: string;
}

export interface RecipeQualificationToolIdentityV1 {
  readonly tool: "terraform" | "docker-buildx";
  readonly version: string;
  readonly secondary_version: string | null;
  readonly adapter_protocol: typeof RECIPE_QUALIFICATION_ADAPTER_PROTOCOL;
  readonly image: typeof RECIPE_QUALIFICATION_TERRAFORM_IMAGE | typeof RECIPE_QUALIFICATION_DOCKER_IMAGE;
  readonly executable_sha256: string;
  readonly identity_sha256: string;
}

export interface RecipeQualificationObservationV1 {
  readonly check_id: RecipeQualificationCheckId;
  readonly adapter_id: RecipeQualificationAdapterId;
  readonly predicate_id: string;
  readonly input_sha256: string;
  readonly result: RecipeQualificationResult;
  readonly detail_code: string;
  readonly tool_identity_sha256: string | null;
  readonly provider_lock_sha256: string | null;
  readonly causal_blockers: readonly string[];
}

export interface RecipeQualificationCertificateV1 {
  readonly schema_version: "domainspec.recipe-qualification-certificate/v1";
  readonly subject: RecipeQualificationSubjectV1;
  readonly profile_id: string;
  readonly profile_sha256: string;
  readonly plan_sha256: string;
  readonly toolchain: readonly RecipeQualificationToolIdentityV1[];
  readonly observations: readonly RecipeQualificationObservationV1[];
  readonly result: RecipeQualificationResult;
  readonly denied_claims: readonly ["release", "publication", "deployment", "runtime-conformance"];
  readonly authority_effect: "none";
  readonly certificate_sha256: string;
}

export interface RecipeQualificationRawEvidenceV1 {
  readonly check_id: RecipeQualificationCheckId;
  readonly stdout_path: string;
  readonly stdout_sha256: string;
  readonly stderr_path: string;
  readonly stderr_sha256: string;
  readonly exit_code: number | null;
  readonly termination: "exited" | "unavailable" | "timeout" | "blocked";
}

export interface RecipeQualificationRunReceiptV1 {
  readonly schema_version: "domainspec.recipe-qualification-run-receipt/v1";
  readonly certificate_sha256: string;
  readonly evidence: readonly RecipeQualificationRawEvidenceV1[];
  readonly result: RecipeQualificationResult;
  readonly authority_effect: "none";
  readonly receipt_sha256: string;
}

export class RecipeQualificationError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(message);
    this.name = "RecipeQualificationError";
  }
}

export function qualificationFail(code: string, pointer: string, message: string): never {
  throw new RecipeQualificationError(code, pointer, message);
}

function record(value: unknown, pointer: string): Record<string, unknown> {
  if (value === null || typeof value !== "object" || Array.isArray(value)) qualificationFail("MTCLI_QUALIFICATION_SCHEMA", pointer, "expected object");
  return value as Record<string, unknown>;
}

function exact(value: unknown, keys: readonly string[], pointer: string): Record<string, unknown> {
  const selected = record(value, pointer);
  if (canonicalJson(Object.keys(selected).sort()) !== canonicalJson([...keys].sort())) qualificationFail("MTCLI_QUALIFICATION_SCHEMA", pointer, "unexpected or missing member");
  return selected;
}

function string(value: unknown, pointer: string, maximum = 256): string {
  if (typeof value !== "string" || value.length < 1 || value.length > maximum || /[\0\r\n]/.test(value)) qualificationFail("MTCLI_QUALIFICATION_SCHEMA", pointer, "expected bounded single-line string");
  return value;
}

function digest(value: unknown, pointer: string): string {
  const selected = string(value, pointer, 64);
  if (!/^[a-f0-9]{64}$/.test(selected)) qualificationFail("MTCLI_QUALIFICATION_DIGEST", pointer, "expected lowercase sha256");
  return selected;
}

function identity(value: unknown, pointer: string): string {
  const selected = string(value, pointer, 128);
  if (!/^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*$/.test(selected)) qualificationFail("MTCLI_QUALIFICATION_ID", pointer, "expected bounded lowercase identity");
  return selected;
}

export function recipeQualificationProfileSha256(value: Omit<RecipeQualificationProfileV1, "profile_sha256">): string {
  return sha256(canonicalJson(value));
}

export function createRecipeQualificationProfile(value: Omit<RecipeQualificationProfileV1, "profile_sha256">): RecipeQualificationProfileV1 {
  return Object.freeze({ ...value, profile_sha256: recipeQualificationProfileSha256(value) });
}

export function decodeRecipeQualificationProfile(value: unknown): RecipeQualificationProfileV1 {
  const root = exact(value, ["schema_version", "profile_id", "ontology_id", "qualification_level", "recipe_target", "required_checks", "optional_checks", "toolchain", "network_policy", "normalization_profile", "effect_ceiling", "authority_effect", "profile_sha256"], "$profile");
  if (root.schema_version !== "domainspec.recipe-qualification-profile/v1" || root.ontology_id !== RECIPE_QUALIFICATION_ONTOLOGY || root.qualification_level !== RECIPE_QUALIFICATION_LEVEL || root.recipe_target !== DEPLOYMENT_RECIPE_TARGET) qualificationFail("MTCLI_QUALIFICATION_PROFILE", "$profile", "unsupported qualification profile identity");
  if (canonicalJson(root.required_checks) !== canonicalJson(RECIPE_QUALIFICATION_REQUIRED_CHECKS) || !Array.isArray(root.optional_checks) || root.optional_checks.length !== 0) qualificationFail("MTCLI_QUALIFICATION_CHECK_SET", "/required_checks", "qualification check set must be exact");
  if (root.network_policy !== "provider-registry-read-only" || root.normalization_profile !== "domainspec.recipe-qualification-normalization/v1" || root.effect_ceiling !== "no-external-effect" || root.authority_effect !== "none") qualificationFail("MTCLI_QUALIFICATION_EFFECT_CEILING", "$profile", "qualification profile exceeds the supported effect ceiling");
  const toolchain = exact(root.toolchain, ["terraform", "docker"], "/toolchain");
  const terraform = exact(toolchain.terraform, ["version", "adapter_protocol", "image"], "/toolchain/terraform");
  const docker = exact(toolchain.docker, ["version", "buildx_version", "adapter_protocol", "image"], "/toolchain/docker");
  if (terraform.adapter_protocol !== RECIPE_QUALIFICATION_ADAPTER_PROTOCOL || docker.adapter_protocol !== RECIPE_QUALIFICATION_ADAPTER_PROTOCOL || terraform.image !== RECIPE_QUALIFICATION_TERRAFORM_IMAGE || docker.image !== RECIPE_QUALIFICATION_DOCKER_IMAGE) qualificationFail("MTCLI_QUALIFICATION_TOOLCHAIN", "/toolchain", "qualification toolchain must bind the exact OCI adapter protocol and images");
  if (terraform.version !== "1.16.0" || docker.version !== "28.0.1" || docker.buildx_version !== "0.21.3") qualificationFail("MTCLI_QUALIFICATION_TOOLCHAIN", "/toolchain", "qualification toolchain versions must match the supported L1 profile");
  const withoutDigest = Object.freeze({
    schema_version: "domainspec.recipe-qualification-profile/v1" as const,
    profile_id: identity(root.profile_id, "/profile_id"),
    ontology_id: RECIPE_QUALIFICATION_ONTOLOGY,
    qualification_level: RECIPE_QUALIFICATION_LEVEL,
    recipe_target: DEPLOYMENT_RECIPE_TARGET,
    required_checks: RECIPE_QUALIFICATION_REQUIRED_CHECKS,
    optional_checks: Object.freeze([]) as readonly [],
    toolchain: Object.freeze({ terraform: Object.freeze({ version: string(terraform.version, "/toolchain/terraform/version", 32), adapter_protocol: RECIPE_QUALIFICATION_ADAPTER_PROTOCOL, image: RECIPE_QUALIFICATION_TERRAFORM_IMAGE }), docker: Object.freeze({ version: string(docker.version, "/toolchain/docker/version", 32), buildx_version: string(docker.buildx_version, "/toolchain/docker/buildx_version", 32), adapter_protocol: RECIPE_QUALIFICATION_ADAPTER_PROTOCOL, image: RECIPE_QUALIFICATION_DOCKER_IMAGE }) }),
    network_policy: "provider-registry-read-only" as const,
    normalization_profile: "domainspec.recipe-qualification-normalization/v1" as const,
    effect_ceiling: "no-external-effect" as const,
    authority_effect: "none" as const,
  });
  const observed = digest(root.profile_sha256, "/profile_sha256");
  const expected = recipeQualificationProfileSha256(withoutDigest);
  if (observed !== expected) qualificationFail("MTCLI_QUALIFICATION_PROFILE_DIGEST", "/profile_sha256", "qualification profile digest is stale");
  return Object.freeze({ ...withoutDigest, profile_sha256: expected });
}

class StrictJsonParser {
  private index = 0;
  constructor(private readonly source: string) {}
  parse(): unknown { const value = this.value("$", 0); this.space(); if (this.index !== this.source.length) qualificationFail("MTCLI_QUALIFICATION_JSON", "$", `unexpected token at byte ${this.index}`); return value; }
  private space(): void { while (/\s/.test(this.source[this.index] ?? "")) this.index++; }
  private value(pointer: string, depth: number): unknown {
    if (depth > MAX_JSON_DEPTH) qualificationFail("MTCLI_QUALIFICATION_JSON_DEPTH", pointer, `JSON nesting exceeds ${MAX_JSON_DEPTH}`);
    this.space(); const token = this.source[this.index];
    if (token === "{") return this.object(pointer, depth + 1);
    if (token === "[") return this.array(pointer, depth + 1);
    if (token === '"') return this.quoted(pointer);
    for (const [literal, value] of [["true", true], ["false", false], ["null", null]] as const) if (this.source.startsWith(literal, this.index)) { this.index += literal.length; return value; }
    const match = this.source.slice(this.index).match(/^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/); if (match) { this.index += match[0].length; return Number(match[0]); }
    qualificationFail("MTCLI_QUALIFICATION_JSON", pointer, `invalid JSON value at byte ${this.index}`);
  }
  private object(pointer: string, depth: number): Record<string, unknown> {
    this.index++; this.space(); const result = Object.create(null) as Record<string, unknown>; const keys = new Set<string>(); if (this.source[this.index] === "}") { this.index++; return result; }
    while (true) { this.space(); if (this.source[this.index] !== '"') qualificationFail("MTCLI_QUALIFICATION_JSON", pointer, "object key must be a string"); const key = this.quoted(pointer); if (keys.has(key)) qualificationFail("MTCLI_QUALIFICATION_DUPLICATE_KEY", `${pointer}/${key}`, `duplicate member:${key}`); keys.add(key); this.space(); if (this.source[this.index] !== ":") qualificationFail("MTCLI_QUALIFICATION_JSON", pointer, "object member requires a colon"); this.index++; result[key] = this.value(`${pointer}/${key.replaceAll("~", "~0").replaceAll("/", "~1")}`, depth); this.space(); if (this.source[this.index] === "}") { this.index++; return result; } if (this.source[this.index] !== ",") qualificationFail("MTCLI_QUALIFICATION_JSON", pointer, "object members require a comma"); this.index++; }
  }
  private array(pointer: string, depth: number): unknown[] { this.index++; this.space(); const result: unknown[] = []; if (this.source[this.index] === "]") { this.index++; return result; } while (true) { result.push(this.value(`${pointer}/${result.length}`, depth)); this.space(); if (this.source[this.index] === "]") { this.index++; return result; } if (this.source[this.index] !== ",") qualificationFail("MTCLI_QUALIFICATION_JSON", pointer, "array members require a comma"); this.index++; } }
  private quoted(pointer: string): string { const start = this.index++; let escaped = false; while (this.index < this.source.length) { const character = this.source[this.index++]!; if (!escaped && character === '"') { try { return JSON.parse(this.source.slice(start, this.index)) as string; } catch { qualificationFail("MTCLI_QUALIFICATION_JSON", pointer, "invalid JSON string"); } } if (!escaped && character.charCodeAt(0) < 0x20) qualificationFail("MTCLI_QUALIFICATION_JSON", pointer, "unescaped control character"); if (!escaped && character === "\\") escaped = true; else escaped = false; } qualificationFail("MTCLI_QUALIFICATION_JSON", pointer, "unterminated JSON string"); }
}

export function parseRecipeQualificationProfileJson(source: string): RecipeQualificationProfileV1 {
  return decodeRecipeQualificationProfile(new StrictJsonParser(source).parse());
}

export function readRecipeQualificationProfile(file: string): RecipeQualificationProfileV1 {
  if (!path.isAbsolute(file) || path.resolve(file) !== file) qualificationFail("MTCLI_QUALIFICATION_PROFILE_PATH", "/profile", "profile path must be normalized and absolute");
  let stats: fs.Stats; try { stats = fs.lstatSync(file); } catch { qualificationFail("MTCLI_QUALIFICATION_PROFILE_PATH", "/profile", "profile does not exist"); }
  if (!stats.isFile() || stats.isSymbolicLink() || fs.realpathSync(file) !== file) qualificationFail("MTCLI_QUALIFICATION_PROFILE_PATH", "/profile", "profile must be one real regular file");
  let bytes: Buffer; try { bytes = readBoundedFileSync(file, MAX_SOURCE_FILE_BYTES); } catch { qualificationFail("MTCLI_QUALIFICATION_PROFILE_SIZE", "/profile", `profile exceeds ${MAX_SOURCE_FILE_BYTES} bytes`); }
  return parseRecipeQualificationProfileJson(bytes.toString("utf8"));
}

export function qualificationArtifactInventorySha256(artifacts: readonly DeploymentRecipeArtifactV1[]): string {
  return sha256(canonicalJson(artifacts.map(({ relative_path, size_bytes, sha256: artifactSha }) => ({ relative_path, size_bytes, sha256: artifactSha }))));
}
