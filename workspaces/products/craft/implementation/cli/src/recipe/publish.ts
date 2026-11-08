import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

import { canonicalJson, sha256 } from "../input/source-manifest.js";
import { plannedRecipeArtifact, recipeFail, type DeploymentRecipePlanV1, type DeploymentRecipeReceiptV1, type DeploymentRecipeRequestV1 } from "./contracts.js";
import { planDeploymentRecipe } from "./plan.js";

export interface DeploymentRecipePublicationV1 {
  readonly target_root: string;
  readonly receipt_path: ".domainspec/deployment-recipe-receipt.json";
  readonly receipt: DeploymentRecipeReceiptV1;
}

export interface DeploymentRecipeVerificationV1 {
  readonly schema_version: "domainspec.deployment-recipe-verification/v1";
  readonly result: "pass" | "fail";
  readonly checks: readonly Readonly<{ id: string; result: "pass" | "fail" }>[];
  readonly expected_plan_sha256: string;
  readonly observed_receipt_sha256: string | null;
  readonly authority_effect: "none";
}

function targetRoot(value: string, mustExist: boolean): { readonly target: string; readonly parent: string } {
  if (!path.isAbsolute(value) || path.resolve(value) !== value) recipeFail("MTCLI_RECIPE_TARGET_ROOT", "/target-root", "target root must be normalized and absolute");
  const parent = path.dirname(value);
  let parentStats: fs.Stats;
  try { parentStats = fs.lstatSync(parent); } catch { recipeFail("MTCLI_RECIPE_TARGET_ROOT", "/target-root", "target parent does not exist"); }
  if (!parentStats.isDirectory() || parentStats.isSymbolicLink() || fs.realpathSync(parent) !== parent) recipeFail("MTCLI_RECIPE_TARGET_ROOT", "/target-root", "target parent must be one real directory");
  if (mustExist) {
    let stats: fs.Stats;
    try { stats = fs.lstatSync(value); } catch { recipeFail("MTCLI_RECIPE_TARGET_ROOT", "/target-root", "target root does not exist"); }
    if (!stats.isDirectory() || stats.isSymbolicLink() || fs.realpathSync(value) !== value) recipeFail("MTCLI_RECIPE_TARGET_ROOT", "/target-root", "target root must be one real directory");
  } else if (fs.existsSync(value)) recipeFail("MTCLI_RECIPE_TARGET_EXISTS", "/target-root", "target root already exists");
  return Object.freeze({ target: value, parent });
}

function validatePlan(plan: DeploymentRecipePlanV1): void {
  const paths = new Set<string>();
  for (const artifact of plan.artifacts) {
    plannedRecipeArtifact(artifact.relative_path, artifact.content);
    if (artifact.mode !== 0o644 || Buffer.byteLength(artifact.content) !== artifact.size_bytes || sha256(artifact.content) !== artifact.sha256) recipeFail("MTCLI_RECIPE_PLAN_DRIFT", `/artifacts/${artifact.relative_path}`, "planned artifact bytes differ from inventory");
    if (paths.has(artifact.relative_path)) recipeFail("MTCLI_RECIPE_COLLISION", `/artifacts/${artifact.relative_path}`, "planned artifact path is duplicated");
    paths.add(artifact.relative_path);
  }
  const receiptArtifact = plan.artifacts.find(({ relative_path }) => relative_path === ".domainspec/deployment-recipe-receipt.json");
  if (!receiptArtifact || receiptArtifact.content !== `${canonicalJson(plan.receipt)}\n`) recipeFail("MTCLI_RECIPE_RECEIPT", "/receipt", "plan receipt artifact is absent or stale");
}

function writeArtifact(root: string, relativePath: string, content: string): void {
  const absolute = path.join(root, relativePath);
  const relative = path.relative(root, absolute);
  if (relative.startsWith("..") || path.isAbsolute(relative)) recipeFail("MTCLI_RECIPE_PATH", `/artifacts/${relativePath}`, "artifact escapes target root");
  fs.mkdirSync(path.dirname(absolute), { recursive: true, mode: 0o755 });
  fs.writeFileSync(absolute, content, { encoding: "utf8", flag: "wx", mode: 0o644 });
}

export function publishDeploymentRecipe(plan: DeploymentRecipePlanV1, targetRootValue: string): DeploymentRecipePublicationV1 {
  validatePlan(plan);
  const { target, parent } = targetRoot(targetRootValue, false);
  const stage = path.join(parent, `.domainspec-recipe-${process.pid}-${crypto.randomUUID()}`);
  try {
    fs.mkdirSync(stage, { mode: 0o700 });
    for (const artifact of plan.artifacts) writeArtifact(stage, artifact.relative_path, artifact.content);
    if (fs.existsSync(target)) recipeFail("MTCLI_RECIPE_TARGET_EXISTS", "/target-root", "target root appeared during publication");
    fs.renameSync(stage, target);
  } catch (error) {
    fs.rmSync(stage, { recursive: true, force: true });
    if (error instanceof Error && "code" in error && String((error as { code?: unknown }).code).startsWith("MTCLI_")) throw error;
    recipeFail("MTCLI_RECIPE_ATOMIC", "/target-root", error instanceof Error ? error.message : "atomic recipe publication failed");
  }
  return Object.freeze({ target_root: target, receipt_path: ".domainspec/deployment-recipe-receipt.json", receipt: plan.receipt });
}

function observedFiles(root: string): readonly string[] {
  const files: string[] = [];
  const walk = (directory: string): void => {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true }).sort((left, right) => left.name.localeCompare(right.name))) {
      const absolute = path.join(directory, entry.name);
      if (entry.isSymbolicLink()) { files.push(`${path.relative(root, absolute).split(path.sep).join("/")}#symlink`); continue; }
      if (entry.isDirectory()) walk(absolute); else files.push(path.relative(root, absolute).split(path.sep).join("/"));
    }
  };
  walk(root);
  return Object.freeze(files.sort());
}

export function verifyDeploymentRecipe(sourceRoot: string, request: DeploymentRecipeRequestV1, consumerRoot: string, targetRootValue: string): DeploymentRecipeVerificationV1 {
  const { target } = targetRoot(targetRootValue, true);
  const expected = planDeploymentRecipe(sourceRoot, request, consumerRoot);
  const checks: Array<{ id: string; result: "pass" | "fail" }> = [];
  for (const artifact of expected.artifacts) {
    let current = false;
    try { const bytes = fs.readFileSync(path.join(target, artifact.relative_path)); current = bytes.length === artifact.size_bytes && sha256(bytes) === artifact.sha256; } catch { /* represented as a failed check */ }
    checks.push({ id: `artifact:${artifact.relative_path}`, result: current ? "pass" : "fail" });
  }
  const expectedPaths = expected.artifacts.map(({ relative_path }) => relative_path).sort();
  checks.push({ id: "artifact-set-exact", result: canonicalJson(observedFiles(target)) === canonicalJson(expectedPaths) ? "pass" : "fail" });
  let observedReceiptSha: string | null = null;
  try {
    const observed = JSON.parse(fs.readFileSync(path.join(target, ".domainspec/deployment-recipe-receipt.json"), "utf8")) as { receipt_sha256?: unknown };
    if (typeof observed.receipt_sha256 === "string") observedReceiptSha = observed.receipt_sha256;
  } catch { /* represented by receipt-current */ }
  checks.push({ id: "receipt-current", result: observedReceiptSha === expected.receipt.receipt_sha256 ? "pass" : "fail" });
  return Object.freeze({ schema_version: "domainspec.deployment-recipe-verification/v1", result: checks.every(({ result }) => result === "pass") ? "pass" : "fail", checks: Object.freeze(checks.map((check) => Object.freeze(check))), expected_plan_sha256: expected.plan_sha256, observed_receipt_sha256: observedReceiptSha, authority_effect: "none" });
}

export function validateDeploymentRecipeReceipt(sourceRoot: string, request: DeploymentRecipeRequestV1, consumerRoot: string, value: unknown): DeploymentRecipeReceiptV1 {
  const expected = planDeploymentRecipe(sourceRoot, request, consumerRoot).receipt;
  if (canonicalJson(value) !== canonicalJson(expected)) recipeFail("MTCLI_RECIPE_RECEIPT", "/receipt", "deployment recipe receipt is invalid, stale, or bound to another input");
  return expected;
}
