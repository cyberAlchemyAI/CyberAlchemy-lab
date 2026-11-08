import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

import { canonicalJson, sha256 } from "../input/source-manifest.js";
import type { ProjectInstantiationPlanV1 } from "./project-instantiation.js";
import { publishReconciledInstantiation, type ReconciledProjectInstantiationPlan, type ReconciledInstantiationPublication } from "./reconciled-instantiation.js";

export interface ProjectPublicationReceiptV1 {
  readonly schema_version: "domainspec.project-publication-receipt/v1";
  readonly project_id: string;
  readonly source_manifest_sha256: string;
  readonly languages: readonly string[];
  readonly node_count: number;
  readonly plan_count: number;
  readonly project_plan_sha256: string;
  readonly graph_certificate: ProjectInstantiationPlanV1["graph_certificate"];
  readonly artifacts: readonly Readonly<{ relative_path: string; size_bytes: number; sha256: string }>[];
  readonly authority_effect: "none";
  readonly receipt_sha256: string;
}

export interface ProjectPublicationResult { readonly target_root: string; readonly receipt_path: ".domainspec/project-publication.json"; readonly receipt: ProjectPublicationReceiptV1; }

interface ProjectPublicationHooks {
  readonly before_claim?: (stagingDirectory: string, targetDirectory: string) => void;
  readonly after_receipt?: (receiptPath: string) => void;
}

function fail(code: string, pointer: string, message: string): never {
  const error = new Error(message) as Error & { code: string; pointer: string; exitCode: number };
  error.code = code; error.pointer = pointer; error.exitCode = 22; throw error;
}

function relative(value: string): void {
  if (path.isAbsolute(value) || value.includes("\\") || value.split("/").some((part) => !part || part === "." || part === "..")) fail("MTCLI_PROJECT_PUBLISH_PATH", "/artifacts", `invalid artifact path:${value}`);
}

function publishProjectInstantiationWithHooks(plan: ProjectInstantiationPlanV1, targetRoot: string, hooks: ProjectPublicationHooks = {}): ProjectPublicationResult {
  if (!path.isAbsolute(targetRoot) || path.resolve(targetRoot) !== targetRoot) fail("MTCLI_PROJECT_PUBLISH_ROOT", "/target-root", "target root must be normalized and absolute");
  if (fs.existsSync(targetRoot)) fail("MTCLI_PROJECT_PUBLISH_EXISTS", "/target-root", "target already exists");
  const parent = path.dirname(targetRoot);
  const parentStats = fs.lstatSync(parent);
  if (!parentStats.isDirectory() || parentStats.isSymbolicLink() || fs.realpathSync(parent) !== parent) fail("MTCLI_PROJECT_PUBLISH_PARENT", "/target-root", "target parent must be a real directory");
  const { project_plan_sha256: claimedPlanSha256, ...planBody } = plan;
  if (sha256(canonicalJson(planBody)) !== claimedPlanSha256) fail("MTCLI_PROJECT_PLAN_DRIFT", "/project_plan_sha256", "project plan content does not match its digest");
  const receiptBody = Object.freeze({ schema_version: "domainspec.project-publication-receipt/v1" as const, project_id: plan.project_id, source_manifest_sha256: plan.source_manifest.manifest_sha256, languages: plan.languages, node_count: plan.node_count, plan_count: plan.plan_count, project_plan_sha256: plan.project_plan_sha256, graph_certificate: plan.graph_certificate, artifacts: Object.freeze(plan.artifacts.map(({ relative_path, size_bytes, sha256: digest }) => Object.freeze({ relative_path, size_bytes, sha256: digest }))), authority_effect: "none" as const });
  const receipt = Object.freeze({ ...receiptBody, receipt_sha256: sha256(canonicalJson(receiptBody)) });
  const receiptPath = ".domainspec/project-publication.json" as const;
  const stage = path.join(parent, `.domainspec-project-staging-${process.pid}-${crypto.randomUUID()}`);
  let ownedTarget: Readonly<{ dev: number; ino: number }> | null = null;
  let ownedClaim: Readonly<{ path: string; dev: number; ino: number }> | null = null;
  const targetIsOwned = (): boolean => {
    if (ownedTarget === null) return false;
    try {
      const current = fs.lstatSync(targetRoot);
      if (!current.isDirectory() || current.isSymbolicLink() || current.dev !== ownedTarget.dev || current.ino !== ownedTarget.ino) return false;
      if (ownedClaim === null) return true;
      const claim = fs.lstatSync(ownedClaim.path);
      return claim.isFile() && !claim.isSymbolicLink() && claim.dev === ownedClaim.dev && claim.ino === ownedClaim.ino;
    }
    catch { return false; }
  };
  try {
    fs.mkdirSync(stage, { mode: 0o700 });
    for (const artifact of plan.artifacts) {
      relative(artifact.relative_path);
      if (Buffer.byteLength(artifact.content) !== artifact.size_bytes || sha256(artifact.content) !== artifact.sha256) fail("MTCLI_PROJECT_PLAN_DRIFT", `/artifacts/${artifact.relative_path}`, "artifact content does not match plan");
      const target = path.join(stage, artifact.relative_path);
      fs.mkdirSync(path.dirname(target), { recursive: true, mode: 0o755 });
      fs.writeFileSync(target, artifact.content, { encoding: "utf8", flag: "wx", mode: 0o644 });
    }
    const receiptTarget = path.join(stage, receiptPath);
    fs.mkdirSync(path.dirname(receiptTarget), { recursive: true, mode: 0o755 });
    fs.writeFileSync(receiptTarget, `${canonicalJson(receipt)}\n`, { encoding: "utf8", flag: "wx", mode: 0o644 });
    hooks.before_claim?.(stage, targetRoot);
    // mkdir is the atomic no-replace claim. POSIX rename may replace a
    // competing empty directory, so it is not a valid publication claim.
    fs.mkdirSync(targetRoot, { mode: 0o700 });
    const targetIdentity = fs.lstatSync(targetRoot);
    ownedTarget = Object.freeze({ dev: targetIdentity.dev, ino: targetIdentity.ino });
    const claimPath = path.join(targetRoot, `.domainspec-project-claim-${crypto.randomUUID()}`);
    fs.writeFileSync(claimPath, "private publication claim\n", { encoding: "utf8", flag: "wx", mode: 0o600 });
    const claimIdentity = fs.lstatSync(claimPath);
    ownedClaim = Object.freeze({ path: claimPath, dev: claimIdentity.dev, ino: claimIdentity.ino });
    for (const artifact of plan.artifacts) {
      if (!targetIsOwned()) fail("MTCLI_PROJECT_PUBLISH_RACE", "/target-root", "claimed project target changed during publication");
      const target = path.join(targetRoot, artifact.relative_path);
      fs.mkdirSync(path.dirname(target), { recursive: true, mode: 0o755 });
      fs.linkSync(path.join(stage, artifact.relative_path), target);
    }
    if (!targetIsOwned()) fail("MTCLI_PROJECT_PUBLISH_RACE", "/target-root", "claimed project target changed before receipt publication");
    const stagedReceiptIdentity = fs.lstatSync(receiptTarget);
    const publicReceipt = path.join(targetRoot, receiptPath);
    fs.mkdirSync(path.dirname(publicReceipt), { recursive: true, mode: 0o755 });
    if (!targetIsOwned()) fail("MTCLI_PROJECT_PUBLISH_RACE", "/target-root", "claimed project target changed before receipt publication");
    fs.linkSync(receiptTarget, publicReceipt);
    hooks.after_receipt?.(publicReceipt);
    if (!targetIsOwned()) fail("MTCLI_PROJECT_PUBLISH_RACE", "/target-root", "claimed project target changed after receipt publication");
    const publicReceiptIdentity = fs.lstatSync(publicReceipt);
    if (publicReceiptIdentity.dev !== stagedReceiptIdentity.dev || publicReceiptIdentity.ino !== stagedReceiptIdentity.ino || fs.readFileSync(publicReceipt, "utf8") !== `${canonicalJson(receipt)}\n`) {
      fail("MTCLI_PROJECT_PUBLISH_RACE", `/${receiptPath}`, "project publication receipt changed during publication");
    }
    fs.rmSync(stage, { recursive: true });
    fs.unlinkSync(claimPath);
    ownedClaim = null;
  } catch (error) {
    if (fs.existsSync(stage)) fs.rmSync(stage, { recursive: true, force: true });
    // Never clean the public target after claiming it: a competing writer may
    // have replaced a descendant while preserving the directory and claim
    // inodes. Failure therefore leaves an incomplete, receipt-invalid target.
    if (["EEXIST", "ENOTEMPTY", "EISDIR"].includes((error as NodeJS.ErrnoException).code ?? "")) fail("MTCLI_PROJECT_PUBLISH_EXISTS", "/target-root", "target or artifact already exists");
    if ((error as { code?: string }).code?.startsWith("MTCLI_")) throw error;
    fail("MTCLI_PROJECT_PUBLISH_ATOMIC", "/target-root", error instanceof Error ? error.message : "project publication failed");
  }
  return Object.freeze({ target_root: targetRoot, receipt_path: receiptPath, receipt });
}

export function publishProjectInstantiation(plan: ReconciledProjectInstantiationPlan, targetRoot: string): ReconciledInstantiationPublication;
export function publishProjectInstantiation(plan: ProjectInstantiationPlanV1, targetRoot: string): ProjectPublicationResult;
export function publishProjectInstantiation(plan: ProjectInstantiationPlanV1 | ReconciledProjectInstantiationPlan, targetRoot: string): ProjectPublicationResult | ReconciledInstantiationPublication;
export function publishProjectInstantiation(plan: ProjectInstantiationPlanV1 | ReconciledProjectInstantiationPlan, targetRoot: string): ProjectPublicationResult | ReconciledInstantiationPublication {
  if (plan.schema_version !== 'domainspec.project-instantiation-plan/v1' || 'project' in plan || 'instantiation_scope' in plan || 'definition_sha256' in plan) return publishReconciledInstantiation(plan, targetRoot, 'project');
  return publishProjectInstantiationWithHooks(plan, targetRoot);
}

/** Internal hostile-race seam; not exported by the package root. */
export function publishProjectInstantiationForTest(plan: ProjectInstantiationPlanV1, targetRoot: string, hooks: ProjectPublicationHooks): ProjectPublicationResult {
  return publishProjectInstantiationWithHooks(plan, targetRoot, hooks);
}
