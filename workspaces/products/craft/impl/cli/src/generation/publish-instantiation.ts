import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

import { createInstantiationReceipt, receiptRelativePath, type InstantiationReceiptV1 } from "../conformance/receipt.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import type { InstantiationPlanV1, PlannedArtifact } from "./contracts.js";

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

function writeExclusive(root: string, relativePath: string, content: string): void {
  validateRelativePath(relativePath, `/${relativePath}`);
  const absolute = path.join(root, relativePath);
  const relative = path.relative(root, absolute);
  if (relative.startsWith("..") || path.isAbsolute(relative)) fail("MTCLI_PUBLISH_PATH", `/${relativePath}`, "output escapes staging root");
  fs.mkdirSync(path.dirname(absolute), { recursive: true, mode: 0o755 });
  fs.writeFileSync(absolute, content, { encoding: "utf8", flag: "wx", mode: 0o644 });
}

export interface PublicationResult {
  readonly target_root: string;
  readonly receipt_path: string;
  readonly receipt: InstantiationReceiptV1;
}

export function publishInstantiation(plan: InstantiationPlanV1, targetRoot: unknown): PublicationResult {
  const { target, parent } = validateTargetRoot(targetRoot);
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
  const stage = path.join(parent, `.domainspec-staging-${process.pid}-${crypto.randomUUID()}`);
  try {
    fs.mkdirSync(stage, { mode: 0o700 });
    for (const artifact of plan.artifacts) writeExclusive(stage, artifact.relative_path, artifact.content);
    writeExclusive(stage, receiptPath, `${canonicalJson(receipt)}\n`);
    if (fs.existsSync(target)) fail("MTCLI_PUBLISH_EXISTS", "/target-root", "target root appeared during publication");
    fs.renameSync(stage, target);
  } catch (error) {
    if (fs.existsSync(stage)) fs.rmSync(stage, { recursive: true, force: true });
    if (error instanceof PublicationError) throw error;
    fail("MTCLI_PUBLISH_ATOMIC", "/target-root", error instanceof Error ? error.message : "atomic publication failed");
  }
  return Object.freeze({ target_root: target, receipt_path: receiptPath, receipt });
}
