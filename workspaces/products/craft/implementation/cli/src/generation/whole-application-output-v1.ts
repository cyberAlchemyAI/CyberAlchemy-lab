import fs from "node:fs";
import path from "node:path";

import { MAX_SOURCE_FILE_BYTES } from "../input/limits.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import type { IntegrationGenerationSourceV2 } from "../system-integration/generation-v2.js";
import { publishAtomicDirectory } from "./atomic-publication.js";
import type { SelectedReconciledCompilation } from "./selected-reconciled-project.js";
import { assertWholeApplicationPlan, planWholeApplicationV1, type WholeApplicationPlanV1 } from "./whole-application-v1.js";

export const WHOLE_APPLICATION_RECEIPT_PATH = ".domainspec/whole-application.json" as const;
export const WHOLE_APPLICATION_OUTPUT_DEFINITION = "domainspec.whole-application-output/v1-candidate" as const;

export class WholeApplicationOutputError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(`${code}:${pointer}:${message}`);
    this.name = "WholeApplicationOutputError";
  }
}

function fail(code: string, pointer: string, message: string): never {
  throw new WholeApplicationOutputError(code, pointer, message);
}

function freeze<T>(value: T): T {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const child of Object.values(value as Record<string, unknown>)) freeze(child);
  }
  return value;
}

function absoluteTarget(value: unknown): string {
  if (typeof value !== "string" || !path.isAbsolute(value) || path.resolve(value) !== value) fail("DS_WHOLE_APPLICATION_OUTPUT_PATH", "/target-root", "normalized absolute target root required");
  return value;
}

function readRegular(file: string, limit: number): Buffer {
  const fd = fs.openSync(file, fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW | fs.constants.O_NONBLOCK);
  try {
    const stat = fs.fstatSync(fd);
    if (!stat.isFile() || stat.size > limit) fail("DS_WHOLE_APPLICATION_OUTPUT_FILE", `/${file}`, "bounded regular file required");
    const value = Buffer.alloc(stat.size);
    let offset = 0;
    while (offset < value.length) {
      const count = fs.readSync(fd, value, offset, value.length - offset, null);
      if (count === 0) break;
      offset += count;
    }
    if (offset !== stat.size) fail("DS_WHOLE_APPLICATION_OUTPUT_FILE", `/${file}`, "file changed while reading");
    return value;
  } finally {
    fs.closeSync(fd);
  }
}

export function createWholeApplicationReceiptV1(plan: WholeApplicationPlanV1) {
  assertWholeApplicationPlan(plan);
  const body = {
    schema_version: "domainspec.whole-application-publication-receipt/v1-candidate" as const,
    output_definition: WHOLE_APPLICATION_OUTPUT_DEFINITION,
    project_id: plan.project_id,
    language: plan.language,
    domain_source_manifest_sha256: plan.domain_source_manifest_sha256,
    integration_source_sha256: plan.integration_source_sha256,
    integration_semantic_manifest_sha256: plan.integration_semantic_manifest_sha256,
    selection_sha256: plan.selection_sha256,
    binding_sha256: plan.binding_sha256,
    application_plan_sha256: plan.application_plan_sha256,
    integration_plan_sha256: plan.integration_plan_sha256,
    integration_contribution_sha256: plan.integration_contribution_sha256,
    whole_application_plan_sha256: plan.plan_sha256,
    artifacts: Object.freeze(plan.artifacts.map(({ relative_path, size_bytes, sha256: digest }) => freeze({ relative_path, size_bytes, sha256: digest }))),
    verification_scope: "exact-source-and-artifact-currentness" as const,
    native_compilation: "not-performed" as const,
    runtime_guarantees_observed: false as const,
    authority_effect: "none" as const,
  };
  return freeze({ ...body, receipt_sha256: sha256(canonicalJson(body)) });
}

export function publishWholeApplicationV1(plan: WholeApplicationPlanV1, targetRoot: unknown) {
  assertWholeApplicationPlan(plan);
  const target = absoluteTarget(targetRoot);
  if (fs.existsSync(target)) fail("DS_WHOLE_APPLICATION_OUTPUT_EXISTS", "/target-root", "target already exists");
  const receipt = createWholeApplicationReceiptV1(plan);
  try {
    publishAtomicDirectory(target, [...plan.artifacts, { relative_path: WHOLE_APPLICATION_RECEIPT_PATH, content: `${canonicalJson(receipt)}\n` }], ".domainspec-whole-application-");
  } catch (error) {
    const code = (error as NodeJS.ErrnoException).code;
    if (code === "DS_ATOMIC_EXISTS") fail("DS_WHOLE_APPLICATION_OUTPUT_EXISTS", "/target-root", "target appeared during publication");
    fail("DS_WHOLE_APPLICATION_OUTPUT_ATOMIC", "/target-root", error instanceof Error ? error.message : "atomic publication failed");
  }
  return freeze({ target_root: target, receipt_path: WHOLE_APPLICATION_RECEIPT_PATH, receipt });
}

export function verifyWholeApplicationV1(projectRoot: string, selection: SelectedReconciledCompilation, integrationSource: IntegrationGenerationSourceV2, targetRoot: unknown) {
  const plan = planWholeApplicationV1(projectRoot, selection, integrationSource);
  const target = absoluteTarget(targetRoot);
  const expectedReceipt = createWholeApplicationReceiptV1(plan);
  const expectedReceiptBytes = `${canonicalJson(expectedReceipt)}\n`;
  const checks: { id: string; result: "pass" | "fail" }[] = [];
  let real = false;
  try {
    const stat = fs.lstatSync(target);
    real = stat.isDirectory() && !stat.isSymbolicLink() && fs.realpathSync(target) === target;
  } catch { /* absent target */ }
  checks.push({ id: "real-target-directory", result: real ? "pass" : "fail" });
  let observedReceipt: Record<string, unknown> | null = null;
  if (real) try { observedReceipt = JSON.parse(readRegular(path.join(target, WHOLE_APPLICATION_RECEIPT_PATH), MAX_SOURCE_FILE_BYTES).toString("utf8")) as Record<string, unknown>; } catch { /* invalid receipt */ }
  const receiptField = (id: string, field: string, expected: unknown): void => { checks.push({ id, result: observedReceipt?.[field] === expected ? "pass" : "fail" }); };
  receiptField("domain-source-current", "domain_source_manifest_sha256", plan.domain_source_manifest_sha256);
  receiptField("integration-source-current", "integration_source_sha256", plan.integration_source_sha256);
  receiptField("selection-current", "selection_sha256", plan.selection_sha256);
  receiptField("layout-and-plan-current", "whole_application_plan_sha256", plan.plan_sha256);
  checks.push({ id: "receipt-current", result: observedReceipt !== null && `${canonicalJson(observedReceipt)}\n` === expectedReceiptBytes ? "pass" : "fail" });
  for (const item of plan.artifacts) {
    let current = false;
    if (real) try {
      const value = readRegular(path.join(target, item.relative_path), item.size_bytes);
      current = value.length === item.size_bytes && sha256(value) === item.sha256;
    } catch { /* absent or hostile artifact */ }
    checks.push({ id: `artifact:${item.relative_path}`, result: current ? "pass" : "fail" });
  }
  const expectedFiles = new Set([WHOLE_APPLICATION_RECEIPT_PATH, ...plan.artifacts.map(item => item.relative_path)]);
  const expectedPaths = new Set(expectedFiles);
  for (const file of expectedFiles) {
    let parent = path.posix.dirname(file);
    while (parent !== ".") { expectedPaths.add(parent); parent = path.posix.dirname(parent); }
  }
  let inventory = real;
  const observed = new Set<string>();
  const walk = (folder: string): void => {
    for (const entry of fs.readdirSync(folder, { withFileTypes: true })) {
      const file = path.join(folder, entry.name);
      const relative = path.relative(target, file).split(path.sep).join("/");
      const stat = fs.lstatSync(file);
      observed.add(relative);
      if (stat.isSymbolicLink() || !expectedPaths.has(relative)) { inventory = false; continue; }
      if (stat.isDirectory()) walk(file);
      else if (!stat.isFile() || !expectedFiles.has(relative)) inventory = false;
    }
  };
  if (real) try { walk(target); } catch { inventory = false; }
  checks.push({ id: "exact-path-inventory", result: inventory && observed.size === expectedPaths.size ? "pass" : "fail" });
  const result = checks.every(item => item.result === "pass") ? "pass" as const : "fail" as const;
  return freeze({ schema_version: "domainspec.whole-application-verification/v1-candidate" as const, result, checks: Object.freeze(checks), expected_receipt_sha256: expectedReceipt.receipt_sha256, whole_application_plan_sha256: plan.plan_sha256, native_compilation: "not-performed" as const, runtime_guarantees_observed: false as const, authority_effect: "none" as const });
}
