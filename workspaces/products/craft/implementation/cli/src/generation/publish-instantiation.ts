import {publishAtomicDirectory} from './atomic-publication.js';
import fs from "node:fs";
import path from "node:path";

import { createInstantiationReceipt, receiptRelativePath, type InstantiationReceiptV1 } from "../conformance/receipt.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import type { InstantiationPlanV1, PlannedArtifact } from "./contracts.js";
import { publishReconciledInstantiation, type ReconciledNodeInstantiationPlan, type ReconciledInstantiationPublication } from "./reconciled-instantiation.js";

export class PublicationError extends Error {
  readonly exitCode = 22;

  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(message);
    this.name = "PublicationError";
  }
}

function fail(code: string, pointer: string, message: string): never {
  throw new PublicationError(code, pointer, message);
}

function validateRelativePath(relativePath: string, pointer: string): void {
  if (path.isAbsolute(relativePath) || relativePath.includes("\\") || relativePath.split("/").some((segment) => segment === "" || segment === "." || segment === "..")) {
    fail("MTCLI_PUBLISH_PATH", pointer, "output path is not relative, normalized, and contained");
  }
}

function validateArtifact(artifact: PlannedArtifact, index: number): void {
  validateRelativePath(artifact.relative_path, `/artifacts/${index}/relative_path`);
  if (Buffer.byteLength(artifact.content) !== artifact.size_bytes || sha256(artifact.content) !== artifact.sha256) {
    fail("MTCLI_PUBLISH_PLAN_DRIFT", `/artifacts/${index}`, "planned artifact content does not match its inventory");
  }
}

function validateTargetRoot(targetRoot: unknown): { target: string; parent: string } {
  if (typeof targetRoot !== "string" || !path.isAbsolute(targetRoot) || path.resolve(targetRoot) !== targetRoot) fail("MTCLI_PUBLISH_EXPLICIT_ROOT", "/target-root", "target root must be an explicit normalized absolute path");
  const target = targetRoot;
  if (fs.existsSync(target)) fail("MTCLI_PUBLISH_EXISTS", "/target-root", "target root already exists");
  const parent = path.dirname(target);
  let stats: fs.Stats;
  try {
    stats = fs.lstatSync(parent);
  } catch {
    fail("MTCLI_PUBLISH_PARENT", "/target-root", "target parent does not exist");
  }
  if (stats.isSymbolicLink() || !stats.isDirectory() || fs.realpathSync(parent) !== parent) fail("MTCLI_PUBLISH_SYMLINK", "/target-root", "target parent cannot be or traverse a symbolic link");
  return { target, parent };
}

export interface PublicationResult {
  readonly target_root: string;
  readonly receipt_path: string;
  readonly receipt: InstantiationReceiptV1;
}

export function publishInstantiation(plan: ReconciledNodeInstantiationPlan, targetRoot: unknown): ReconciledInstantiationPublication;
export function publishInstantiation(plan: InstantiationPlanV1, targetRoot: unknown): PublicationResult;
export function publishInstantiation(plan: InstantiationPlanV1 | ReconciledNodeInstantiationPlan, targetRoot: unknown): PublicationResult | ReconciledInstantiationPublication;
export function publishInstantiation(plan: InstantiationPlanV1 | ReconciledNodeInstantiationPlan, targetRoot: unknown): PublicationResult | ReconciledInstantiationPublication {
  if (plan.schema_version !== 'domainspec.instantiation-plan/v1' || 'project' in plan || 'instantiation_scope' in plan || 'definition_sha256' in plan) return publishReconciledInstantiation(plan, targetRoot, 'node');
  const { target } = validateTargetRoot(targetRoot);
  if (plan.artifacts.length === 0) fail("MTCLI_PUBLISH_PLAN", "/artifacts", "plan has no artifacts");
  const paths = new Set<string>();
  plan.artifacts.forEach((artifact, index) => {
    validateArtifact(artifact, index);
    if (paths.has(artifact.relative_path)) fail("MTCLI_PUBLISH_PATH", `/artifacts/${index}/relative_path`, "duplicate output path");
    paths.add(artifact.relative_path);
  });
  const receipt = createInstantiationReceipt(plan);
  const receiptPath = receiptRelativePath(plan.input.feature_id, plan.input.node_id);
  if (paths.has(receiptPath)) fail("MTCLI_PUBLISH_PATH", "/receipt", "receipt collides with a generated artifact");
  try {
    publishAtomicDirectory(target,[...plan.artifacts,{relative_path:receiptPath,content:`${canonicalJson(receipt)}\n`}],'.domainspec-staging-');
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code==='DS_ATOMIC_EXISTS')fail("MTCLI_PUBLISH_EXISTS", "/target-root", "target root appeared during publication");
    if ((error as NodeJS.ErrnoException).code==='DS_NATIVE_PERMISSION')fail("MTCLI_PUBLISH_UNAVAILABLE", "/target-root", (error as Error).message);
    if (error instanceof PublicationError) throw error;
    fail("MTCLI_PUBLISH_ATOMIC", "/target-root", error instanceof Error ? error.message : "atomic publication failed");
  }
  return Object.freeze({ target_root: target, receipt_path: receiptPath, receipt });
}
