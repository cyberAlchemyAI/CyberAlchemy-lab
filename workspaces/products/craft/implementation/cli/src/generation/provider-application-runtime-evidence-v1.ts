import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { canonicalJson, sha256 } from "../input/source-manifest.js";
import type { IntegrationGenerationSourceV2 } from "../system-integration/generation-v2.js";
import { composeProviderApplicationV1 } from "./provider-application-v1.js";
import { createProviderApplicationReceiptV1, verifyProviderApplicationV1 } from "./provider-application-output-v1.js";
import type { SelectedReconciledCompilation } from "./selected-reconciled-project.js";
import { planWholeApplicationV1 } from "./whole-application-v1.js";

const RUNTIME_EVIDENCE_TIMEOUT_MS = 10 * 60_000;
const MAX_SUBPROCESS_OUTPUT_BYTES = 32 * 1024 * 1024;
const SCENARIO = Object.freeze({
  typescript: "typescript-webhook.mjs",
  python: "python-webhook.py",
  rust: "rust-webhook.rs",
} as const);

export interface ProviderApplicationRuntimeEvidenceOptionsV1 {
  readonly target_root: string;
  readonly temporary_parent: string;
  readonly receipt_path: string;
  readonly node_executable?: string;
  readonly npm_executable?: string;
  readonly python_executable?: string;
  readonly docker_executable?: string;
  readonly python_image?: string;
  readonly cargo_executable?: string;
}

interface ScenarioObservation {
  readonly language: "typescript" | "python" | "rust";
  readonly startup: "http-listener" | "asgi-http-listener" | "axum-http-listener";
  readonly invalid_status: 401;
  readonly valid_status: 202;
  readonly handler_invocations: 1;
  readonly result: "pass";
}

export class ProviderApplicationRuntimeEvidenceError extends Error {
  constructor(readonly code: string, readonly pointer: string, message: string, readonly exitCode: 1 | 22 = 22) {
    super(`${code}:${pointer}:${message}`);
    this.name = "ProviderApplicationRuntimeEvidenceError";
  }
}

function fail(code: string, pointer: string, message: string, exitCode: 1 | 22 = 22): never {
  throw new ProviderApplicationRuntimeEvidenceError(code, pointer, message, exitCode);
}

function freeze<T>(value: T): T {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const child of Object.values(value as Record<string, unknown>)) freeze(child);
  }
  return value;
}

function normalizedAbsolute(value: unknown, pointer: string): string {
  if (typeof value !== "string" || !path.isAbsolute(value) || path.resolve(value) !== value) {
    fail("DS_PROVIDER_RUNTIME_PATH", pointer, "normalized absolute path required");
  }
  return value;
}

function existingDirectory(value: unknown, pointer: string): string {
  const directory = normalizedAbsolute(value, pointer);
  try {
    const stat = fs.lstatSync(directory);
    if (!stat.isDirectory() || stat.isSymbolicLink() || fs.realpathSync(directory) !== directory) throw new Error("not a real directory");
  } catch {
    fail("DS_PROVIDER_RUNTIME_DIRECTORY", pointer, "existing real directory required");
  }
  return directory;
}

function isWithin(root: string, candidate: string): boolean {
  const relative = path.relative(root, candidate);
  return relative === "" || (!path.isAbsolute(relative) && relative !== ".." && !relative.startsWith(`..${path.sep}`));
}

function requireOutsideTarget(target: string, candidate: string, pointer: string): void {
  if (isWithin(target, candidate)) {
    fail("DS_PROVIDER_RUNTIME_TARGET_BOUNDARY", pointer, "path must be outside the generated target");
  }
}

function executable(value: unknown, pointer: string): string {
  const file = normalizedAbsolute(value, pointer);
  try {
    const stat = fs.statSync(file);
    if (!stat.isFile()) throw new Error("not a file");
    fs.accessSync(file, fs.constants.X_OK);
  } catch {
    fail("DS_PROVIDER_RUNTIME_EXECUTABLE", pointer, "existing executable file required");
  }
  return file;
}

function run(executablePath: string, args: readonly string[], cwd: string, env: NodeJS.ProcessEnv, pointer: string) {
  const result = spawnSync(executablePath, [...args], {
    cwd,
    env,
    encoding: "utf8",
    timeout: RUNTIME_EVIDENCE_TIMEOUT_MS,
    maxBuffer: MAX_SUBPROCESS_OUTPUT_BYTES,
  });
  if (result.status !== 0) {
    const detail = (result.error?.message || result.stderr || result.stdout || `subprocess exited ${result.status}`).trim().slice(0, 4_096);
    fail("DS_PROVIDER_RUNTIME_SUBPROCESS", pointer, detail || `subprocess exited ${result.status}`, 1);
  }
  return result.stdout.trim();
}

function scenarioRoot(): string {
  return path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../examples/reconciled-commerce/scenarios");
}

function decodeScenario(stdout: string, language: "typescript" | "python" | "rust"): ScenarioObservation {
  let value: unknown;
  try { value = JSON.parse(stdout); } catch { fail("DS_PROVIDER_RUNTIME_SCENARIO", "/scenario/stdout", "scenario must emit one JSON observation", 1); }
  const candidate = value as Partial<ScenarioObservation>;
  const expectedStartup = language === "typescript" ? "http-listener" : language === "python" ? "asgi-http-listener" : "axum-http-listener";
  if (candidate.language !== language || candidate.startup !== expectedStartup || candidate.invalid_status !== 401 || candidate.valid_status !== 202 || candidate.handler_invocations !== 1 || candidate.result !== "pass") {
    fail("DS_PROVIDER_RUNTIME_SCENARIO", "/scenario", "exact signed loopback webhook observation required", 1);
  }
  return freeze(candidate as ScenarioObservation);
}

interface RuntimeObservation {
  readonly scenario: ScenarioObservation;
  readonly execution_environment: Readonly<{ kind: "local-toolchain" | "container"; identifier: string }>;
}

function typescriptObservation(workspace: string, temporary: string, options: ProviderApplicationRuntimeEvidenceOptionsV1): RuntimeObservation {
  const node = executable(options.node_executable, "/node-executable");
  const npm = executable(options.npm_executable, "/npm-executable");
  const env = { ...process.env, npm_config_cache: path.join(temporary, "npm-cache") };
  run(npm, ["ci", "--ignore-scripts", "--no-audit", "--no-fund"], workspace, env, "/dependency-installation");
  const compiler = path.join(workspace, "node_modules/typescript/bin/tsc");
  if (!fs.existsSync(compiler)) fail("DS_PROVIDER_RUNTIME_COMPILER", "/native-compilation", "locked TypeScript compiler was not installed", 1);
  run(node, [compiler, "--project", path.join(workspace, "tsconfig.json"), "--noEmit", "--pretty", "false"], workspace, env, "/native-compilation");
  run(node, [compiler, "--project", path.join(workspace, "tsconfig.json"), "--noEmit", "false", "--outDir", path.join(workspace, "dist"), "--pretty", "false"], workspace, env, "/native-compilation");
  return freeze({ scenario: decodeScenario(run(node, [path.join(scenarioRoot(), SCENARIO.typescript), workspace], workspace, env, "/scenario"), "typescript"), execution_environment: freeze({ kind: "local-toolchain" as const, identifier: "node+npm" }) });
}

function pythonObservation(workspace: string, temporary: string, options: ProviderApplicationRuntimeEvidenceOptionsV1): RuntimeObservation {
  if (options.docker_executable !== undefined) {
    const docker = executable(options.docker_executable, "/docker-executable");
    const image = options.python_image;
    if (!image || image.startsWith("-") || /\s/.test(image)) fail("DS_PROVIDER_RUNTIME_IMAGE", "/python-image", "non-empty container image reference required");
    const scenario = path.join(scenarioRoot(), SCENARIO.python);
    const cidFile = path.join(temporary, "python-container.cid");
    const script = "PYTHONPYCACHEPREFIX=/tmp/bytecode python -m compileall -q /application/src && python -m pip install --disable-pip-version-check --no-input --no-cache-dir --quiet --target /tmp/dependencies -r /application/requirements.lock >/tmp/pip.log && PYTHONPATH=/tmp/dependencies:/application/src python /scenario.py /application";
    let stdout: string;
    try {
      stdout = run(docker, ["run", "--rm", "--cidfile", cidFile, "--platform", "linux/amd64", "--mount", `type=bind,src=${workspace},dst=/application,readonly`, "--mount", `type=bind,src=${scenario},dst=/scenario.py,readonly`, "--env", "PYTHONDONTWRITEBYTECODE=1", image, "/bin/sh", "-ceu", script], workspace, process.env, "/python-container");
    } catch (error) {
      try {
        const containerId = fs.readFileSync(cidFile, "utf8").trim();
        if (/^[0-9a-f]{12,64}$/.test(containerId)) spawnSync(docker, ["rm", "--force", containerId], { encoding: "utf8", timeout: 30_000 });
      } catch { /* container did not start or already exited */ }
      throw error;
    }
    return freeze({ scenario: decodeScenario(stdout, "python"), execution_environment: freeze({ kind: "container" as const, identifier: image }) });
  }
  const python = executable(options.python_executable, "/python-executable");
  const dependencies = path.join(temporary, "python-dependencies");
  const env = { ...process.env, PYTHONPYCACHEPREFIX: path.join(temporary, "python-bytecode"), PYTHONPATH: `${dependencies}${path.delimiter}${path.join(workspace, "src")}` };
  run(python, ["-m", "pip", "install", "--disable-pip-version-check", "--no-input", "--no-cache-dir", "--target", dependencies, "-r", path.join(workspace, "requirements.lock")], workspace, env, "/dependency-installation");
  run(python, ["-m", "compileall", "-q", path.join(workspace, "src")], workspace, env, "/native-compilation");
  return freeze({ scenario: decodeScenario(run(python, [path.join(scenarioRoot(), SCENARIO.python), workspace], workspace, env, "/scenario"), "python"), execution_environment: freeze({ kind: "local-toolchain" as const, identifier: "python+pip" }) });
}

function rustObservation(workspace: string, temporary: string, options: ProviderApplicationRuntimeEvidenceOptionsV1): RuntimeObservation {
  const cargo = executable(options.cargo_executable, "/cargo-executable");
  const scenarioTarget = path.join(workspace, "src/bin/domainspec-runtime-evidence.rs");
  fs.mkdirSync(path.dirname(scenarioTarget), { recursive: true });
  fs.copyFileSync(path.join(scenarioRoot(), SCENARIO.rust), scenarioTarget, fs.constants.COPYFILE_EXCL);
  const env = {
    ...process.env,
    CARGO_TARGET_DIR: path.join(temporary, "cargo-target"),
    RUSTFLAGS: "-Dwarnings",
  };
  run(cargo, ["check", "--locked", "--quiet"], workspace, env, "/native-compilation");
  return freeze({ scenario: decodeScenario(run(cargo, ["run", "--locked", "--quiet", "--bin", "domainspec-runtime-evidence"], workspace, env, "/scenario"), "rust"), execution_environment: freeze({ kind: "local-toolchain" as const, identifier: "cargo" }) });
}

function writeReceipt(file: string, value: unknown): void {
  const receiptPath = normalizedAbsolute(file, "/receipt");
  const parent = existingDirectory(path.dirname(receiptPath), "/receipt/parent");
  if (path.dirname(receiptPath) !== parent || fs.existsSync(receiptPath)) fail("DS_PROVIDER_RUNTIME_RECEIPT_EXISTS", "/receipt", "new receipt path required");
  const descriptor = fs.openSync(receiptPath, fs.constants.O_WRONLY | fs.constants.O_CREAT | fs.constants.O_EXCL | fs.constants.O_NOFOLLOW, 0o600);
  let complete = false;
  try { fs.writeFileSync(descriptor, `${canonicalJson(value)}\n`); fs.fsyncSync(descriptor); complete = true; } finally {
    fs.closeSync(descriptor);
    if (!complete) try { fs.unlinkSync(receiptPath); } catch { /* no partial receipt remains when cleanup is possible */ }
  }
}

export function verifyProviderApplicationRuntimeV1(
  projectRoot: string,
  compilationSelection: SelectedReconciledCompilation,
  integrationSource: IntegrationGenerationSourceV2,
  providerSelection: unknown,
  options: ProviderApplicationRuntimeEvidenceOptionsV1,
) {
  const target = existingDirectory(options.target_root, "/target-root");
  const temporaryParent = existingDirectory(options.temporary_parent, "/temporary-parent");
  const receiptPath = normalizedAbsolute(options.receipt_path, "/receipt");
  existingDirectory(path.dirname(receiptPath), "/receipt/parent");
  requireOutsideTarget(target, temporaryParent, "/temporary-parent");
  requireOutsideTarget(target, receiptPath, "/receipt");
  if (fs.existsSync(receiptPath)) fail("DS_PROVIDER_RUNTIME_RECEIPT_EXISTS", "/receipt", "new receipt path required");

  const formationBefore = verifyProviderApplicationV1(projectRoot, compilationSelection, integrationSource, providerSelection, target);
  if (formationBefore.result !== "pass") fail("DS_PROVIDER_RUNTIME_FORMATION", "/target-root", "current provider application required", 1);
  const whole = planWholeApplicationV1(projectRoot, compilationSelection, integrationSource);
  const plan = composeProviderApplicationV1(whole, providerSelection, integrationSource);
  const formationReceipt = createProviderApplicationReceiptV1(plan);
  const temporary = fs.mkdtempSync(path.join(temporaryParent, ".domainspec-runtime-evidence-"));
  let observation: RuntimeObservation;
  try {
    const workspace = path.join(temporary, "application");
    fs.cpSync(target, workspace, { recursive: true, errorOnExist: true, force: false });
    observation = plan.language === "typescript"
      ? typescriptObservation(workspace, temporary, options)
      : plan.language === "python"
        ? pythonObservation(workspace, temporary, options)
        : rustObservation(workspace, temporary, options);
  } finally {
    fs.rmSync(temporary, { recursive: true, force: true });
  }

  const formationAfter = verifyProviderApplicationV1(projectRoot, compilationSelection, integrationSource, providerSelection, target);
  if (formationAfter.result !== "pass") fail("DS_PROVIDER_RUNTIME_TARGET_MUTATED", "/target-root", "provider application changed during runtime verification", 1);
  const body = {
    schema_version: "domainspec.provider-application-runtime-evidence/v1-candidate" as const,
    evidence_scope: "native-compilation-and-bounded-loopback-http" as const,
    project_id: plan.project_id,
    language: plan.language,
    domain_source_manifest_sha256: plan.domain_source_manifest_sha256,
    integration_source_sha256: plan.integration_source_sha256,
    compilation_selection_sha256: plan.compilation_selection_sha256,
    provider_selection_sha256: plan.provider_selection_sha256,
    provider_application_plan_sha256: plan.plan_sha256,
    formation_receipt_sha256: formationReceipt.receipt_sha256,
    formation_currentness: freeze({ observed: true as const, before: "pass" as const, after: "pass" as const }),
    dependency_installation: freeze({ observed: true as const, result: "pass" as const, boundary: "task-owned-temporary-copy" as const, cache_boundary: plan.language === "rust" ? "caller-managed" as const : "task-owned-temporary" as const }),
    native_compilation: freeze({ observed: true as const, result: "pass" as const }),
    execution_environment: observation.execution_environment,
    listener_startup: freeze({ observed: true as const, result: "pass" as const, boundary: "loopback-only" as const, kind: observation.scenario.startup }),
    signed_webhook_behavior: freeze({ observed: true as const, result: "pass" as const, invalid_signature_status: observation.scenario.invalid_status, valid_signature_status: observation.scenario.valid_status, handler_invocations: observation.scenario.handler_invocations }),
    provider_dependencies: freeze({ postgresql: "not-observed" as const, nats: "not-observed" as const, outbound_http: "not-observed" as const }),
    transport_delivery_observed: false as const,
    consumer_completion_observed: false as const,
    production_runtime_guarantees_observed: false as const,
    target_mutated: false as const,
    temporary_resources_removed: true as const,
    authority_effect: "none" as const,
  };
  const receipt = freeze({ ...body, receipt_sha256: sha256(canonicalJson(body)) });
  writeReceipt(receiptPath, receipt);
  return freeze({
    schema_version: "domainspec.provider-application-runtime-command-result/v1-candidate" as const,
    result: "pass" as const,
    receipt_path: receiptPath,
    receipt,
    authority_effect: "none" as const,
  });
}
