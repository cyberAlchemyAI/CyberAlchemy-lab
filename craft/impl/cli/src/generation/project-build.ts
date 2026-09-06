import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

import { createCompiledProjectCertificate, type CompiledProjectCertificateV1 } from "../compilation/certificate.js";
import { createMetaTypeFormalizationProjection, formalizationProjectionSha256 } from "../formalization/projection.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import { loadCompiledProjectGraph, loadProjectNode } from "../input/project-model.js";
import type { SupportedLanguage } from "../meta-types/types.js";
import type { PlannedArtifact } from "./contracts.js";
import { planInstantiation } from "./plan-instantiation.js";

const RECEIPT_PATH = ".domainspec/project-build.json";

export interface ProjectBuildReceiptV1 {
  readonly schema_version: "domainspec.project-build-receipt/v1";
  readonly project_id: string;
  readonly language: SupportedLanguage;
  readonly source_manifest_sha256: string;
  readonly compiled_certificate: CompiledProjectCertificateV1;
  readonly formalization_projection_sha256: string;
  readonly node_selectors: readonly string[];
  readonly artifacts: readonly Omit<PlannedArtifact, "content">[];
  readonly authority_effect: "none";
  readonly receipt_sha256: string;
}

export interface ProjectBuildPlanV1 {
  readonly receipt: ProjectBuildReceiptV1;
  readonly artifacts: readonly PlannedArtifact[];
}

export class ProjectBuildError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) { super(message); this.name = "ProjectBuildError"; }
}

function fail(code: string, pointer: string, message: string): never { throw new ProjectBuildError(code, pointer, message); }

function assertTarget(targetRoot: unknown): { readonly target: string; readonly parent: string } {
  if (typeof targetRoot !== "string" || !path.isAbsolute(targetRoot) || path.resolve(targetRoot) !== targetRoot) fail("MTCLI_PROJECT_BUILD_ROOT", "/target-root", "target root must be a normalized absolute path");
  if (fs.existsSync(targetRoot)) fail("MTCLI_PROJECT_BUILD_EXISTS", "/target-root", "target root already exists");
  const parent = path.dirname(targetRoot);
  let stat: fs.Stats;
  try { stat = fs.lstatSync(parent); } catch { fail("MTCLI_PROJECT_BUILD_PARENT", "/target-root", "target parent does not exist"); }
  if (!stat.isDirectory() || stat.isSymbolicLink() || fs.realpathSync(parent) !== parent) fail("MTCLI_PROJECT_BUILD_PARENT", "/target-root", "target parent must be a real directory");
  return Object.freeze({ target: targetRoot, parent });
}

function writeExclusive(root: string, relativePath: string, content: string): void {
  if (path.isAbsolute(relativePath) || relativePath.includes("\\") || relativePath.split("/").some((part) => !part || part === "." || part === "..")) fail("MTCLI_PROJECT_BUILD_PATH", `/${relativePath}`, "artifact path is not normalized and contained");
  const target = path.join(root, relativePath);
  fs.mkdirSync(path.dirname(target), { recursive: true, mode: 0o755 });
  fs.writeFileSync(target, content, { encoding: "utf8", flag: "wx", mode: 0o644 });
}

export function planProjectBuild(sourceRoot: string, language: SupportedLanguage): ProjectBuildPlanV1 {
  const graph = loadCompiledProjectGraph(sourceRoot);
  const compiledCertificate = createCompiledProjectCertificate(graph);
  const formalizationProjection = createMetaTypeFormalizationProjection(graph);
  const artifacts: PlannedArtifact[] = [];
  const paths = new Set<string>();
  for (const node of graph.nodes) {
    const plan = planInstantiation(loadProjectNode(sourceRoot, node.selector), language);
    for (const artifact of plan.artifacts) {
      if (artifact.relative_path === "Cargo.toml") continue;
      if (paths.has(artifact.relative_path)) fail("MTCLI_PROJECT_BUILD_COLLISION", `/nodes/${node.selector}`, `artifact collision:${artifact.relative_path}`);
      paths.add(artifact.relative_path);
      artifacts.push(artifact);
    }
  }
  artifacts.sort((left, right) => left.relative_path.localeCompare(right.relative_path));
  const inventory = Object.freeze(artifacts.map(({ relative_path, size_bytes, sha256: digest }) => Object.freeze({ relative_path, size_bytes, sha256: digest })));
  const body = {
    schema_version: "domainspec.project-build-receipt/v1" as const,
    project_id: graph.project_id,
    language,
    source_manifest_sha256: graph.source_manifest.manifest_sha256,
    compiled_certificate: compiledCertificate,
    formalization_projection_sha256: formalizationProjectionSha256(formalizationProjection),
    node_selectors: Object.freeze(graph.nodes.map(({ selector }) => selector)),
    artifacts: inventory,
    authority_effect: "none" as const,
  };
  return Object.freeze({ artifacts: Object.freeze(artifacts), receipt: Object.freeze({ ...body, receipt_sha256: sha256(canonicalJson(body)) }) });
}

export function publishProjectBuild(plan: ProjectBuildPlanV1, targetRoot: unknown): Readonly<{ target_root: string; receipt_path: string; receipt: ProjectBuildReceiptV1 }> {
  const { target, parent } = assertTarget(targetRoot);
  const stage = path.join(parent, `.domainspec-project-${process.pid}-${crypto.randomUUID()}`);
  try {
    fs.mkdirSync(stage, { mode: 0o700 });
    for (const artifact of plan.artifacts) writeExclusive(stage, artifact.relative_path, artifact.content);
    writeExclusive(stage, RECEIPT_PATH, `${canonicalJson(plan.receipt)}\n`);
    if (fs.existsSync(target)) fail("MTCLI_PROJECT_BUILD_EXISTS", "/target-root", "target root appeared during publication");
    fs.renameSync(stage, target);
  } catch (error) {
    fs.rmSync(stage, { recursive: true, force: true });
    if (error instanceof ProjectBuildError) throw error;
    fail("MTCLI_PROJECT_BUILD_ATOMIC", "/target-root", error instanceof Error ? error.message : "atomic publication failed");
  }
  return Object.freeze({ target_root: target, receipt_path: RECEIPT_PATH, receipt: plan.receipt });
}

export interface ProjectBuildVerificationV1 {
  readonly schema_version: "domainspec.project-build-verification/v1";
  readonly result: "pass" | "fail";
  readonly checks: readonly Readonly<{ id: string; result: "pass" | "fail" }>[];
  readonly expected_receipt_sha256: string;
  readonly observed_receipt_sha256: string | null;
  readonly authority_effect: "none";
}

export function verifyProjectBuild(sourceRoot: string, language: SupportedLanguage, targetRoot: string): ProjectBuildVerificationV1 {
  const expected = planProjectBuild(sourceRoot, language);
  const checks: Array<{ id: string; result: "pass" | "fail" }> = [];
  let observedReceipt: ProjectBuildReceiptV1 | null = null;
  try { observedReceipt = JSON.parse(fs.readFileSync(path.join(targetRoot, RECEIPT_PATH), "utf8")) as ProjectBuildReceiptV1; } catch { /* recorded below */ }
  checks.push({ id: "receipt-current", result: observedReceipt !== null && canonicalJson(observedReceipt) === canonicalJson(expected.receipt) ? "pass" : "fail" });
  for (const artifact of expected.artifacts) {
    let current = false;
    try { const bytes = fs.readFileSync(path.join(targetRoot, artifact.relative_path)); current = bytes.length === artifact.size_bytes && sha256(bytes) === artifact.sha256; } catch { /* recorded below */ }
    checks.push({ id: `artifact:${artifact.relative_path}`, result: current ? "pass" : "fail" });
  }
  const expectedPaths = new Set([RECEIPT_PATH, ...expected.artifacts.map(({ relative_path }) => relative_path)]);
  const observedPaths: string[] = [];
  if (fs.existsSync(targetRoot)) {
    const walk = (directory: string): void => { for (const entry of fs.readdirSync(directory, { withFileTypes: true })) { const absolute = path.join(directory, entry.name); if (entry.isDirectory()) walk(absolute); else observedPaths.push(path.relative(targetRoot, absolute).split(path.sep).join("/")); } };
    walk(targetRoot);
  }
  checks.push({ id: "artifact-set-exact", result: observedPaths.length === expectedPaths.size && observedPaths.every((candidate) => expectedPaths.has(candidate)) ? "pass" : "fail" });
  return Object.freeze({
    schema_version: "domainspec.project-build-verification/v1",
    result: checks.every(({ result }) => result === "pass") ? "pass" : "fail",
    checks: Object.freeze(checks.map((check) => Object.freeze(check))),
    expected_receipt_sha256: expected.receipt.receipt_sha256,
    observed_receipt_sha256: observedReceipt?.receipt_sha256 ?? null,
    authority_effect: "none",
  });
}
