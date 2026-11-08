import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

import { SUBPROCESS_TIMEOUT_MS } from "../input/limits.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import type { DeploymentRecipeRequestV1 } from "../recipe/contracts.js";
import {
  RECIPE_QUALIFICATION_ADAPTER_PROTOCOL,
  RECIPE_QUALIFICATION_REQUIRED_CHECKS,
  qualificationFail,
  type RecipeQualificationCertificateV1,
  type RecipeQualificationObservationV1,
  type RecipeQualificationPlanV1,
  type RecipeQualificationProfileV1,
  type RecipeQualificationRawEvidenceV1,
  type RecipeQualificationResult,
  type RecipeQualificationRunReceiptV1,
  type RecipeQualificationToolIdentityV1,
} from "./contracts.js";
import { planRecipeQualification } from "./plan.js";

export interface RecipeQualificationToolBindings {
  readonly terraformExecutable?: string;
  readonly dockerExecutable?: string;
}

export interface RecipeQualificationPublicationV1 {
  readonly qualification_root: string;
  readonly plan: RecipeQualificationPlanV1;
  readonly certificate: RecipeQualificationCertificateV1;
  readonly receipt: RecipeQualificationRunReceiptV1;
}

export interface RecipeQualificationVerificationV1 {
  readonly schema_version: "domainspec.recipe-qualification-verification/v1";
  readonly result: "pass" | "fail";
  readonly checks: readonly Readonly<{ id: string; result: "pass" | "fail" }>[];
  readonly expected_plan_sha256: string;
  readonly observed_certificate_sha256: string | null;
  readonly authority_effect: "none";
}

interface CapturedRun {
  readonly stdout: string;
  readonly stderr: string;
  readonly exitCode: number | null;
  readonly termination: RecipeQualificationRawEvidenceV1["termination"];
}

interface ToolProbe {
  readonly executable: string | null;
  readonly identity: RecipeQualificationToolIdentityV1 | null;
  readonly available: boolean;
  readonly versionMatch: boolean;
  readonly detail: string;
}

function executableFromPath(name: string): string | null {
  const overrideName = name === "terraform" ? "DOMAINSPEC_TERRAFORM_ADAPTER" : "DOMAINSPEC_DOCKER_ADAPTER";
  const override = process.env[overrideName];
  if (override !== undefined) {
    if (!path.isAbsolute(override) || path.resolve(override) !== override) qualificationFail("MTCLI_QUALIFICATION_TOOL_PATH", `/environment/${overrideName}`, "adapter override must be one normalized absolute path");
    try { const overrideStats = fs.statSync(override); if (overrideStats.isFile() && (overrideStats.mode & 0o111) !== 0) return override; } catch { /* fail below */ }
    qualificationFail("MTCLI_QUALIFICATION_TOOL_PATH", `/environment/${overrideName}`, "adapter override must be executable");
  }
  const bundled = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..", "tools", "recipe-qualification", name);
  try {
    const bundledStats = fs.statSync(bundled);
    if (bundledStats.isFile() && (bundledStats.mode & 0o111) !== 0) return bundled;
  } catch { /* fall back to an explicitly installed adapter */ }
  for (const directory of (process.env.PATH ?? "").split(path.delimiter)) {
    if (directory.length === 0) continue;
    const candidate = path.resolve(directory, name);
    try {
      const stats = fs.statSync(candidate);
      if (stats.isFile() && (stats.mode & 0o111) !== 0) return candidate;
    } catch { /* continue searching */ }
  }
  return null;
}

function selectedExecutable(value: string | undefined, name: string): string | null {
  if (value === undefined) return executableFromPath(name);
  if (!path.isAbsolute(value) || path.resolve(value) !== value) qualificationFail("MTCLI_QUALIFICATION_TOOL_PATH", `/tools/${name}`, "tool binding must be one normalized absolute path");
  try {
    const stats = fs.statSync(value);
    if (!stats.isFile() || (stats.mode & 0o111) === 0) qualificationFail("MTCLI_QUALIFICATION_TOOL_PATH", `/tools/${name}`, "tool binding must be executable");
    return value;
  } catch { qualificationFail("MTCLI_QUALIFICATION_TOOL_PATH", `/tools/${name}`, "tool binding does not exist"); }
}

function run(executable: string, args: readonly string[], cwd: string): CapturedRun {
  const result = spawnSync(executable, [...args], { cwd, encoding: "utf8", timeout: SUBPROCESS_TIMEOUT_MS, maxBuffer: 4 * 1024 * 1024, env: { ...process.env, TF_IN_AUTOMATION: "1", CHECKPOINT_DISABLE: "1" } });
  if (result.error && (result.error as NodeJS.ErrnoException).code === "ETIMEDOUT") return Object.freeze({ stdout: result.stdout ?? "", stderr: result.stderr ?? "", exitCode: null, termination: "timeout" as const });
  if (result.error) return Object.freeze({ stdout: result.stdout ?? "", stderr: `${result.stderr ?? ""}${result.error.message}\n`, exitCode: null, termination: "unavailable" as const });
  return Object.freeze({ stdout: result.stdout ?? "", stderr: result.stderr ?? "", exitCode: result.status, termination: "exited" as const });
}

function toolIdentity(tool: RecipeQualificationToolIdentityV1["tool"], version: string, secondaryVersion: string | null, executable: string, image: RecipeQualificationToolIdentityV1["image"]): RecipeQualificationToolIdentityV1 {
  const real = fs.realpathSync(executable);
  const body = Object.freeze({ tool, version, secondary_version: secondaryVersion, adapter_protocol: RECIPE_QUALIFICATION_ADAPTER_PROTOCOL, image, executable_sha256: sha256(fs.readFileSync(real)) });
  return Object.freeze({ ...body, identity_sha256: sha256(canonicalJson(body)) });
}

function adapterIdentity(executable: string, expectedImage: string): boolean {
  const observed = run(executable, ["domainspec-adapter-identity"], process.cwd());
  if (observed.termination !== "exited" || observed.exitCode !== 0) return false;
  try {
    const decoded = JSON.parse(observed.stdout) as { adapter_protocol?: unknown; image?: unknown };
    return decoded.adapter_protocol === RECIPE_QUALIFICATION_ADAPTER_PROTOCOL && decoded.image === expectedImage && canonicalJson(Object.keys(decoded).sort()) === canonicalJson(["adapter_protocol", "image"]);
  } catch { return false; }
}

function terraformProbe(profile: RecipeQualificationProfileV1, binding?: string): ToolProbe {
  const executable = selectedExecutable(binding, "terraform");
  if (executable === null) return Object.freeze({ executable: null, identity: null, available: false, versionMatch: false, detail: "terraform-unavailable" });
  if (!adapterIdentity(executable, profile.toolchain.terraform.image)) return Object.freeze({ executable, identity: null, available: false, versionMatch: false, detail: "terraform-adapter-identity-mismatch" });
  const observed = run(executable, ["version", "-json"], process.cwd());
  if (observed.termination !== "exited" || observed.exitCode !== 0) return Object.freeze({ executable, identity: null, available: false, versionMatch: false, detail: "terraform-version-probe-failed" });
  let version = "";
  try { const decoded = JSON.parse(observed.stdout) as { terraform_version?: unknown }; if (typeof decoded.terraform_version === "string") version = decoded.terraform_version; } catch { /* handled below */ }
  if (version.length === 0) return Object.freeze({ executable, identity: null, available: false, versionMatch: false, detail: "terraform-version-invalid" });
  const identity = toolIdentity("terraform", version, null, executable, profile.toolchain.terraform.image);
  return Object.freeze({ executable, identity, available: true, versionMatch: version === profile.toolchain.terraform.version, detail: version === profile.toolchain.terraform.version ? "terraform-version-exact" : "terraform-version-mismatch" });
}

function dockerProbe(profile: RecipeQualificationProfileV1, binding?: string): ToolProbe {
  const executable = selectedExecutable(binding, "docker");
  if (executable === null) return Object.freeze({ executable: null, identity: null, available: false, versionMatch: false, detail: "docker-unavailable" });
  if (!adapterIdentity(executable, profile.toolchain.docker.image)) return Object.freeze({ executable, identity: null, available: false, versionMatch: false, detail: "docker-adapter-identity-mismatch" });
  const docker = run(executable, ["version", "--format", "{{.Client.Version}}"], process.cwd());
  const buildx = run(executable, ["buildx", "version"], process.cwd());
  if (docker.termination !== "exited" || docker.exitCode !== 0 || buildx.termination !== "exited" || buildx.exitCode !== 0) return Object.freeze({ executable, identity: null, available: false, versionMatch: false, detail: "docker-buildx-version-probe-failed" });
  const version = docker.stdout.trim();
  const buildxMatch = buildx.stdout.match(/v?([0-9]+\.[0-9]+\.[0-9]+)/);
  if (version.length === 0 || !buildxMatch?.[1]) return Object.freeze({ executable, identity: null, available: false, versionMatch: false, detail: "docker-buildx-version-invalid" });
  const buildxVersion = buildxMatch[1];
  const identity = toolIdentity("docker-buildx", version, buildxVersion, executable, profile.toolchain.docker.image);
  const versionMatch = version === profile.toolchain.docker.version && buildxVersion === profile.toolchain.docker.buildx_version;
  return Object.freeze({ executable, identity, available: true, versionMatch, detail: versionMatch ? "docker-buildx-version-exact" : "docker-buildx-version-mismatch" });
}

function copyDirectory(source: string, target: string): void {
  fs.mkdirSync(target, { recursive: true, mode: 0o700 });
  for (const entry of fs.readdirSync(source, { withFileTypes: true }).sort((left, right) => left.name.localeCompare(right.name))) {
    const from = path.join(source, entry.name);
    const to = path.join(target, entry.name);
    if (entry.isSymbolicLink()) qualificationFail("MTCLI_QUALIFICATION_RECIPE_PATH", "/target-root", "recipe inputs cannot contain symlinks");
    if (entry.isDirectory()) copyDirectory(from, to);
    else if (entry.isFile()) fs.copyFileSync(from, to);
  }
}

function aggregate(observations: readonly RecipeQualificationObservationV1[]): RecipeQualificationResult {
  if (observations.some(({ result }) => result === "fail")) return "fail";
  if (observations.some(({ result }) => result === "not_evaluable")) return "not_evaluable";
  return "pass";
}

function certificateSha(value: Omit<RecipeQualificationCertificateV1, "certificate_sha256">): string { return sha256(canonicalJson(value)); }
function receiptSha(value: Omit<RecipeQualificationRunReceiptV1, "receipt_sha256">): string { return sha256(canonicalJson(value)); }

function observation(plan: RecipeQualificationPlanV1, checkId: RecipeQualificationObservationV1["check_id"], result: RecipeQualificationResult, detailCode: string, toolIdentitySha: string | null, providerLockSha: string | null, blockers: readonly string[]): RecipeQualificationObservationV1 {
  const check = plan.checks.find(({ check_id }) => check_id === checkId);
  if (!check) qualificationFail("MTCLI_QUALIFICATION_PLAN", `/checks/${checkId}`, "required check is absent from plan");
  return Object.freeze({ check_id: check.check_id, adapter_id: check.adapter_id, predicate_id: check.predicate_id, input_sha256: check.input_sha256, result, detail_code: detailCode, tool_identity_sha256: toolIdentitySha, provider_lock_sha256: providerLockSha, causal_blockers: Object.freeze([...blockers]) });
}

function synthetic(detail: string, termination: CapturedRun["termination"] = "blocked"): CapturedRun { return Object.freeze({ stdout: "", stderr: `${detail}\n`, exitCode: null, termination }); }

function processResult(probe: ToolProbe, captured: CapturedRun): RecipeQualificationResult {
  if (!probe.available || captured.termination === "unavailable" || captured.termination === "timeout") return "not_evaluable";
  if (!probe.versionMatch || captured.exitCode !== 0) return "fail";
  return "pass";
}

function evidence(checkId: RecipeQualificationRawEvidenceV1["check_id"], captured: CapturedRun): RecipeQualificationRawEvidenceV1 {
  const stdoutPath = `evidence/${checkId}.stdout.txt`;
  const stderrPath = `evidence/${checkId}.stderr.txt`;
  return Object.freeze({ check_id: checkId, stdout_path: stdoutPath, stdout_sha256: sha256(captured.stdout), stderr_path: stderrPath, stderr_sha256: sha256(captured.stderr), exit_code: captured.exitCode, termination: captured.termination });
}

function outputRoot(value: string, mustExist: boolean): { target: string; parent: string } {
  if (!path.isAbsolute(value) || path.resolve(value) !== value) qualificationFail("MTCLI_QUALIFICATION_ROOT", "/qualification-root", "qualification root must be normalized and absolute");
  const parent = path.dirname(value);
  try { const stats = fs.lstatSync(parent); if (!stats.isDirectory() || stats.isSymbolicLink() || fs.realpathSync(parent) !== parent) throw new Error(); } catch { qualificationFail("MTCLI_QUALIFICATION_ROOT", "/qualification-root", "qualification parent must be one real directory"); }
  if (mustExist) {
    try { const stats = fs.lstatSync(value); if (!stats.isDirectory() || stats.isSymbolicLink() || fs.realpathSync(value) !== value) throw new Error(); } catch { qualificationFail("MTCLI_QUALIFICATION_ROOT", "/qualification-root", "qualification root must be one real directory"); }
  } else if (fs.existsSync(value)) qualificationFail("MTCLI_QUALIFICATION_ROOT_EXISTS", "/qualification-root", "qualification root already exists");
  return { target: value, parent };
}

export function qualifyDeploymentRecipe(sourceRoot: string, request: DeploymentRecipeRequestV1, consumerRoot: string, targetRoot: string, profile: RecipeQualificationProfileV1, qualificationRoot: string, bindings: RecipeQualificationToolBindings = {}): RecipeQualificationPublicationV1 {
  const plan = planRecipeQualification(sourceRoot, request, consumerRoot, targetRoot, profile);
  const destination = outputRoot(qualificationRoot, false);
  const terraform = terraformProbe(profile, bindings.terraformExecutable);
  const docker = dockerProbe(profile, bindings.dockerExecutable);
  const scratch = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-recipe-qualification-"));
  const terraformRoot = path.join(scratch, "terraform");
  const captures = new Map<RecipeQualificationObservationV1["check_id"], CapturedRun>();
  const observations: RecipeQualificationObservationV1[] = [];
  let providerLockSha: string | null = null;
  try {
    copyDirectory(path.join(targetRoot, "infrastructure", "terraform"), terraformRoot);
    const lockPath = path.join(terraformRoot, ".terraform.lock.hcl");
    if (fs.existsSync(lockPath)) providerLockSha = sha256(fs.readFileSync(lockPath));
    captures.set("recipe-byte-verify", Object.freeze({ stdout: "recipe target exactly matches deterministic plan\n", stderr: "", exitCode: 0, termination: "exited" }));
    observations.push(observation(plan, "recipe-byte-verify", "pass", "recipe-bytes-current", null, null, []));

    const terraformUnavailable = !terraform.available ? synthetic(terraform.detail, "unavailable") : !terraform.versionMatch ? synthetic(terraform.detail) : null;
    const fmt = terraformUnavailable ?? run(terraform.executable!, ["fmt", "-check", "-recursive", "-diff"], terraformRoot);
    captures.set("terraform-fmt-check", fmt);
    observations.push(observation(plan, "terraform-fmt-check", processResult(terraform, fmt), terraform.versionMatch ? (fmt.exitCode === 0 ? "terraform-format-current" : "terraform-format-drift") : terraform.detail, terraform.identity?.identity_sha256 ?? null, null, []));

    const init = terraformUnavailable ?? (providerLockSha === null ? synthetic("terraform-provider-lock-missing") : run(terraform.executable!, ["init", "-backend=false", "-input=false", "-no-color", "-lockfile=readonly"], terraformRoot));
    captures.set("terraform-init-backendless", init);
    const initResult = processResult(terraform, init);
    const lockAfterInit = fs.existsSync(lockPath) ? sha256(fs.readFileSync(lockPath)) : null;
    const effectiveInitResult: RecipeQualificationResult = initResult === "pass" && providerLockSha !== null && lockAfterInit === providerLockSha ? "pass" : initResult === "not_evaluable" ? "not_evaluable" : "fail";
    observations.push(observation(plan, "terraform-init-backendless", effectiveInitResult, effectiveInitResult === "pass" ? "terraform-provider-lock-current" : providerLockSha === null ? "terraform-provider-lock-missing" : lockAfterInit !== providerLockSha ? "terraform-provider-lock-drift" : terraform.versionMatch ? "terraform-init-failed" : terraform.detail, terraform.identity?.identity_sha256 ?? null, providerLockSha, []));

    const validate = effectiveInitResult === "pass" ? run(terraform.executable!, ["validate", "-no-color"], terraformRoot) : synthetic("blocked-by:terraform-init-backendless");
    captures.set("terraform-validate", validate);
    const validateResult = effectiveInitResult === "pass" ? processResult(terraform, validate) : "not_evaluable";
    observations.push(observation(plan, "terraform-validate", validateResult, validateResult === "pass" ? "terraform-configuration-valid" : validateResult === "fail" ? "terraform-validation-failed" : "terraform-validation-blocked", terraform.identity?.identity_sha256 ?? null, providerLockSha, effectiveInitResult === "pass" ? [] : ["terraform-init-backendless"]));

    const dockerUnavailable = !docker.available ? synthetic(docker.detail, "unavailable") : !docker.versionMatch ? synthetic(docker.detail) : null;
    const bake = dockerUnavailable ?? run(docker.executable!, ["buildx", "bake", "--file", "images/docker-bake.hcl", "--check"], targetRoot);
    captures.set("docker-buildx-bake-check", bake);
    observations.push(observation(plan, "docker-buildx-bake-check", processResult(docker, bake), docker.versionMatch ? (bake.exitCode === 0 ? "docker-build-targets-valid" : "docker-build-check-failed") : docker.detail, docker.identity?.identity_sha256 ?? null, null, []));
  } finally {
    fs.rmSync(scratch, { recursive: true, force: true });
  }

  const frozenObservations = Object.freeze(observations);
  const result = aggregate(frozenObservations);
  const certificateBody = Object.freeze({ schema_version: "domainspec.recipe-qualification-certificate/v1" as const, subject: plan.subject, profile_id: profile.profile_id, profile_sha256: profile.profile_sha256, plan_sha256: plan.plan_sha256, toolchain: Object.freeze([terraform.identity, docker.identity].filter((item): item is RecipeQualificationToolIdentityV1 => item !== null)), observations: frozenObservations, result, denied_claims: Object.freeze(["release", "publication", "deployment", "runtime-conformance"] as const), authority_effect: "none" as const });
  const certificate = Object.freeze({ ...certificateBody, certificate_sha256: certificateSha(certificateBody) });
  const rawEvidence = Object.freeze(RECIPE_QUALIFICATION_REQUIRED_CHECKS.map((checkId) => evidence(checkId, captures.get(checkId) ?? synthetic("missing-capture"))));
  const receiptBody = Object.freeze({ schema_version: "domainspec.recipe-qualification-run-receipt/v1" as const, certificate_sha256: certificate.certificate_sha256, evidence: rawEvidence, result, authority_effect: "none" as const });
  const receipt = Object.freeze({ ...receiptBody, receipt_sha256: receiptSha(receiptBody) });
  const stage = path.join(destination.parent, `.domainspec-qualification-${process.pid}-${crypto.randomUUID()}`);
  try {
    fs.mkdirSync(path.join(stage, "evidence"), { recursive: true, mode: 0o700 });
    fs.writeFileSync(path.join(stage, "qualification-plan.json"), `${canonicalJson(plan)}\n`, { flag: "wx" });
    fs.writeFileSync(path.join(stage, "qualification-certificate.json"), `${canonicalJson(certificate)}\n`, { flag: "wx" });
    fs.writeFileSync(path.join(stage, "qualification-run-receipt.json"), `${canonicalJson(receipt)}\n`, { flag: "wx" });
    for (const item of rawEvidence) {
      const capture = captures.get(item.check_id) ?? synthetic("missing-capture");
      fs.writeFileSync(path.join(stage, item.stdout_path), capture.stdout, { flag: "wx" });
      fs.writeFileSync(path.join(stage, item.stderr_path), capture.stderr, { flag: "wx" });
    }
    if (fs.existsSync(destination.target)) qualificationFail("MTCLI_QUALIFICATION_ROOT_EXISTS", "/qualification-root", "qualification root appeared during publication");
    fs.renameSync(stage, destination.target);
  } catch (error) {
    fs.rmSync(stage, { recursive: true, force: true });
    if (error instanceof Error && "code" in error && String((error as { code?: unknown }).code).startsWith("MTCLI_")) throw error;
    qualificationFail("MTCLI_QUALIFICATION_ATOMIC", "/qualification-root", error instanceof Error ? error.message : "atomic qualification publication failed");
  }
  return Object.freeze({ qualification_root: destination.target, plan, certificate, receipt });
}

function jsonFile(root: string, name: string): unknown { try { return JSON.parse(fs.readFileSync(path.join(root, name), "utf8")); } catch { return null; } }
function without<T extends Record<string, unknown>>(value: T, key: string): Record<string, unknown> { const copy = { ...value }; delete copy[key]; return copy; }
function exactKeys(value: unknown, keys: readonly string[]): boolean { return value !== null && typeof value === "object" && !Array.isArray(value) && canonicalJson(Object.keys(value as Record<string, unknown>).sort()) === canonicalJson([...keys].sort()); }

export function verifyRecipeQualification(sourceRoot: string, request: DeploymentRecipeRequestV1, consumerRoot: string, targetRoot: string, profile: RecipeQualificationProfileV1, qualificationRoot: string): RecipeQualificationVerificationV1 {
  const root = outputRoot(qualificationRoot, true).target;
  const expectedPlan = planRecipeQualification(sourceRoot, request, consumerRoot, targetRoot, profile);
  const plan = jsonFile(root, "qualification-plan.json") as RecipeQualificationPlanV1 | null;
  const certificate = jsonFile(root, "qualification-certificate.json") as RecipeQualificationCertificateV1 | null;
  const receipt = jsonFile(root, "qualification-run-receipt.json") as RecipeQualificationRunReceiptV1 | null;
  const checks: Array<{ id: string; result: "pass" | "fail" }> = [];
  checks.push({ id: "plan-shape-closed", result: exactKeys(plan, ["schema_version", "subject", "profile_id", "profile_sha256", "checks", "authority_effect", "plan_sha256"]) ? "pass" : "fail" });
  checks.push({ id: "plan-current", result: canonicalJson(plan) === canonicalJson(expectedPlan) ? "pass" : "fail" });
  checks.push({ id: "certificate-shape-closed", result: exactKeys(certificate, ["schema_version", "subject", "profile_id", "profile_sha256", "plan_sha256", "toolchain", "observations", "result", "denied_claims", "authority_effect", "certificate_sha256"]) ? "pass" : "fail" });
  const certificateHash = certificate && typeof certificate === "object" ? certificateSha(without(certificate as unknown as Record<string, unknown>, "certificate_sha256") as Omit<RecipeQualificationCertificateV1, "certificate_sha256">) : null;
  checks.push({ id: "certificate-self-digest", result: certificate !== null && certificateHash === certificate.certificate_sha256 ? "pass" : "fail" });
  checks.push({ id: "certificate-plan-link", result: certificate?.plan_sha256 === expectedPlan.plan_sha256 && certificate?.profile_sha256 === profile.profile_sha256 && canonicalJson(certificate?.subject) === canonicalJson(expectedPlan.subject) ? "pass" : "fail" });
  const observedIds = certificate?.observations?.map(({ check_id }) => check_id) ?? [];
  checks.push({ id: "certificate-check-set-exact", result: canonicalJson(observedIds) === canonicalJson(RECIPE_QUALIFICATION_REQUIRED_CHECKS) ? "pass" : "fail" });
  const observationBindingsCurrent = certificate?.observations?.every((item, index) => {
    const planned = expectedPlan.checks[index];
    return exactKeys(item, ["check_id", "adapter_id", "predicate_id", "input_sha256", "result", "detail_code", "tool_identity_sha256", "provider_lock_sha256", "causal_blockers"]) && planned !== undefined && item.check_id === planned.check_id && item.adapter_id === planned.adapter_id && item.predicate_id === planned.predicate_id && item.input_sha256 === planned.input_sha256 && ["pass", "fail", "not_evaluable"].includes(item.result) && Array.isArray(item.causal_blockers);
  }) ?? false;
  checks.push({ id: "certificate-observation-bindings", result: observationBindingsCurrent ? "pass" : "fail" });
  const toolIdentitiesCurrent = certificate?.toolchain?.every((item) => exactKeys(item, ["tool", "version", "secondary_version", "adapter_protocol", "image", "executable_sha256", "identity_sha256"]) && item.adapter_protocol === RECIPE_QUALIFICATION_ADAPTER_PROTOCOL && item.identity_sha256 === sha256(canonicalJson(without(item as unknown as Record<string, unknown>, "identity_sha256")))) ?? false;
  checks.push({ id: "certificate-tool-identities", result: toolIdentitiesCurrent ? "pass" : "fail" });
  const terraformIdentity = certificate?.toolchain?.find(({ tool }) => tool === "terraform")?.identity_sha256 ?? null;
  const dockerIdentity = certificate?.toolchain?.find(({ tool }) => tool === "docker-buildx")?.identity_sha256 ?? null;
  const toolReferencesCurrent = certificate?.observations?.every((item) => item.check_id === "recipe-byte-verify"
    ? item.tool_identity_sha256 === null
    : item.check_id === "docker-buildx-bake-check"
      ? item.tool_identity_sha256 === dockerIdentity && (item.result !== "pass" || dockerIdentity !== null)
      : item.tool_identity_sha256 === terraformIdentity && (item.result !== "pass" || terraformIdentity !== null)) ?? false;
  checks.push({ id: "certificate-tool-references", result: toolReferencesCurrent ? "pass" : "fail" });
  const initLock = certificate?.observations?.find(({ check_id }) => check_id === "terraform-init-backendless")?.provider_lock_sha256 ?? null;
  const lockReferencesCurrent = certificate?.observations?.every((item) => item.check_id === "terraform-init-backendless" || item.check_id === "terraform-validate" ? item.provider_lock_sha256 === initLock && (item.result !== "pass" || initLock !== null) : item.provider_lock_sha256 === null) ?? false;
  checks.push({ id: "certificate-provider-lock-references", result: lockReferencesCurrent ? "pass" : "fail" });
  checks.push({ id: "certificate-claim-ceiling", result: certificate?.authority_effect === "none" && canonicalJson(certificate.denied_claims) === canonicalJson(["release", "publication", "deployment", "runtime-conformance"]) ? "pass" : "fail" });
  const observedAggregate = certificate?.observations ? aggregate(certificate.observations) : null;
  checks.push({ id: "certificate-aggregate", result: observedAggregate !== null && certificate?.result === observedAggregate ? "pass" : "fail" });
  const receiptHash = receipt && typeof receipt === "object" ? receiptSha(without(receipt as unknown as Record<string, unknown>, "receipt_sha256") as Omit<RecipeQualificationRunReceiptV1, "receipt_sha256">) : null;
  checks.push({ id: "receipt-shape-closed", result: exactKeys(receipt, ["schema_version", "certificate_sha256", "evidence", "result", "authority_effect", "receipt_sha256"]) ? "pass" : "fail" });
  checks.push({ id: "receipt-self-digest", result: receipt !== null && receiptHash === receipt.receipt_sha256 ? "pass" : "fail" });
  checks.push({ id: "receipt-certificate-link", result: receipt?.certificate_sha256 === certificate?.certificate_sha256 && receipt?.result === certificate?.result ? "pass" : "fail" });
  checks.push({ id: "receipt-claim-ceiling", result: receipt?.schema_version === "domainspec.recipe-qualification-run-receipt/v1" && receipt?.authority_effect === "none" ? "pass" : "fail" });
  const expectedFiles = ["qualification-certificate.json", "qualification-plan.json", "qualification-run-receipt.json", ...RECIPE_QUALIFICATION_REQUIRED_CHECKS.flatMap((id) => [`evidence/${id}.stderr.txt`, `evidence/${id}.stdout.txt`])].sort();
  const observedFiles: string[] = [];
  const walk = (directory: string): void => { for (const entry of fs.readdirSync(directory, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) { const absolute = path.join(directory, entry.name); const relative = path.relative(root, absolute).split(path.sep).join("/"); if (entry.isSymbolicLink()) observedFiles.push(`${relative}#symlink`); else if (entry.isDirectory()) walk(absolute); else observedFiles.push(relative); } };
  walk(root);
  checks.push({ id: "artifact-set-exact", result: canonicalJson(observedFiles.sort()) === canonicalJson(expectedFiles) ? "pass" : "fail" });
  let evidenceCurrent = receipt !== null && Array.isArray(receipt.evidence) && receipt.evidence.length === RECIPE_QUALIFICATION_REQUIRED_CHECKS.length;
  if (evidenceCurrent) for (const [index, item] of receipt!.evidence.entries()) {
    const checkId = RECIPE_QUALIFICATION_REQUIRED_CHECKS[index]!;
    const stdoutPath = `evidence/${checkId}.stdout.txt`; const stderrPath = `evidence/${checkId}.stderr.txt`;
    evidenceCurrent = evidenceCurrent && exactKeys(item, ["check_id", "stdout_path", "stdout_sha256", "stderr_path", "stderr_sha256", "exit_code", "termination"]) && item.check_id === checkId && item.stdout_path === stdoutPath && item.stderr_path === stderrPath && ["exited", "unavailable", "timeout", "blocked"].includes(item.termination);
    try { evidenceCurrent = evidenceCurrent && sha256(fs.readFileSync(path.join(root, stdoutPath))) === item.stdout_sha256 && sha256(fs.readFileSync(path.join(root, stderrPath))) === item.stderr_sha256; } catch { evidenceCurrent = false; }
  }
  checks.push({ id: "evidence-digests-current", result: evidenceCurrent ? "pass" : "fail" });
  return Object.freeze({ schema_version: "domainspec.recipe-qualification-verification/v1", result: checks.every(({ result }) => result === "pass") ? "pass" : "fail", checks: Object.freeze(checks.map((item) => Object.freeze(item))), expected_plan_sha256: expectedPlan.plan_sha256, observed_certificate_sha256: certificate?.certificate_sha256 ?? null, authority_effect: "none" });
}
