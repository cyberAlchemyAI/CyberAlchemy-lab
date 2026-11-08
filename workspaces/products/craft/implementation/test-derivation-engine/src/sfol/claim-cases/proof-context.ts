import { createHash } from "node:crypto";
import { lstatSync, readFileSync, realpathSync, statSync } from "node:fs";
import { isAbsolute, join, relative } from "node:path";

import { canonicalSfolJson, digestSfolValue } from "../cases/index.js";
import type { SelectedSfolRef } from "./index.js";

const SHA256 = /^[a-f0-9]{64}$/;
const CEILING = "exact selected proof-context bytes only; missing source manifest and changed build remain unresolved; no upstream proof, v4 neutral set, EVF pass or F5 satisfaction" as const;
type Role = "clause_manifest" | "graph" | "build" | "profile" | "source_manifest";
type Check = Readonly<{ role: Role; status: "match" | "drift" | "unavailable"; expected_sha256: string; observed_sha256: string | null; path: string | null }>;

export type SelectedSfolProofContextSources = Readonly<{
  clause_manifest: SelectedSfolRef;
  graph: SelectedSfolRef;
  build: SelectedSfolRef;
  profile: SelectedSfolRef;
  source_manifest: SelectedSfolRef | null;
}>;
export type SelectedSfolProofContextAssessment = Readonly<{
  schema_version: "tde.selected-sfol-proof-context/v1-candidate";
  selection: SelectedSfolProofContextSources;
  checks: readonly Check[];
  status: "matched-selected-context" | "incomplete-or-drifted";
  f5_eligibility: "blocked-missing-domainspec-v4-chain";
  authority_effect: "none";
  claim_ceiling: typeof CEILING;
  assessment_digest: string;
}>;

export class SelectedSfolProofContextError extends Error {
  constructor(readonly code: "INVALID_SELECTION" | "SOURCE_DRIFT" | "INVALID_MANIFEST" | "REPLAY_MISMATCH", detail: string) {
    super(`${code}:${detail}`);
    this.name = "SelectedSfolProofContextError";
  }
}
function fail(code: SelectedSfolProofContextError["code"], detail: string): never {
  throw new SelectedSfolProofContextError(code, detail);
}
function isObject(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === "object" && !Array.isArray(value);
}
function readExact(root: string, ref: SelectedSfolRef): Buffer | null {
  if (!isObject(ref) || Object.keys(ref).sort().join(",") !== "path,sha256,size_bytes" ||
      typeof ref.path !== "string" || !ref.path || isAbsolute(ref.path) || ref.path.includes("\\") ||
      ref.path.split("/").some(part => !part || part === "." || part === "..") ||
      typeof ref.sha256 !== "string" || !SHA256.test(ref.sha256) ||
      !Number.isSafeInteger(ref.size_bytes) || ref.size_bytes < 1 || ref.size_bytes > 2 * 1024 * 1024)
    fail("INVALID_SELECTION", "invalid exact source reference");
  const base = realpathSync(root);
  let path = base;
  for (const part of ref.path.split("/")) {
    path = join(path, part);
    try { if (lstatSync(path).isSymbolicLink()) fail("SOURCE_DRIFT", `symlink: ${ref.path}`); }
    catch (error) {
      if (isObject(error) && error.code === "ENOENT") return null;
      throw error;
    }
  }
  const rel = relative(base, path);
  if (rel === ".." || rel.startsWith("../") || isAbsolute(rel) || realpathSync(path) !== path)
    fail("SOURCE_DRIFT", `source escapes selected root: ${ref.path}`);
  const before = statSync(path);
  if (!before.isFile() || before.size !== ref.size_bytes) fail("SOURCE_DRIFT", `source size changed: ${ref.path}`);
  const bytes = readFileSync(path);
  const after = statSync(path);
  const digest = createHash("sha256").update(bytes).digest("hex");
  if (before.ino !== after.ino || before.dev !== after.dev || before.mtimeMs !== after.mtimeMs ||
      bytes.length !== ref.size_bytes || digest !== ref.sha256)
    fail("SOURCE_DRIFT", `source bytes changed: ${ref.path}`);
  return bytes;
}
function digest(bytes: Buffer): string { return createHash("sha256").update(bytes).digest("hex"); }
function json(bytes: Buffer): Record<string, unknown> {
  try { const value: unknown = JSON.parse(bytes.toString("utf8")); if (isObject(value)) return value; }
  catch { /* reported below */ }
  return fail("INVALID_MANIFEST", "clause manifest is not a JSON object");
}

/** A separate diagnostic: it deliberately does not mutate or upgrade a case set. */
export function assessSelectedSfolProofContext(root: string, selection: SelectedSfolProofContextSources): SelectedSfolProofContextAssessment {
  if (!isObject(selection) || Object.keys(selection).sort().join(",") !== "build,clause_manifest,graph,profile,source_manifest")
    fail("INVALID_SELECTION", "all proof-context roles must be explicit");
  const manifestBytes = readExact(root, selection.clause_manifest);
  if (!manifestBytes) fail("SOURCE_DRIFT", "selected clause manifest unavailable");
  const manifest = json(manifestBytes);
  const context = manifest.proof_context;
  if (manifest.schema_version !== "domainspec-sfol-clause-admission-manifest/v1" || !isObject(context) ||
      !SHA256.test(String(context.graph_digest)) || !SHA256.test(String(context.build_digest)) ||
      !SHA256.test(String(context.profile_digest)) || !SHA256.test(String(context.manifest_digest)) ||
      context.source_set_digest !== context.manifest_digest ||
      context.profile_id !== "domainspec-sfol" || context.profile_version !== "domainspec-sfol/v1")
    fail("INVALID_MANIFEST", "unsupported or incomplete proof context");
  const graphBytes = readExact(root, selection.graph);
  const buildBytes = readExact(root, selection.build);
  const profileBytes = readExact(root, selection.profile);
  const sourceBytes = selection.source_manifest === null ? null : readExact(root, selection.source_manifest);
  const sources = [
    ["graph", selection.graph, graphBytes, context.graph_digest],
    ["build", selection.build, buildBytes, context.build_digest],
    ["profile", selection.profile, profileBytes, context.profile_digest],
    ["source_manifest", selection.source_manifest, sourceBytes, context.manifest_digest],
  ] as const;
  const checks: Check[] = sources.map(([role, ref, bytes, expected]) => ({
    role, path: ref?.path ?? null, expected_sha256: expected as string,
    observed_sha256: bytes ? digest(bytes) : null,
    status: bytes ? (digest(bytes) === expected ? "match" : "drift") : "unavailable",
  }));
  const graph = graphBytes ? json(graphBytes) : null;
  if (graph && (graph.graph_id !== context.graph_id || graph.source_manifest_sha256 !== context.manifest_digest))
    fail("INVALID_MANIFEST", "graph identity or source-manifest binding differs");
  const unsigned = {
    schema_version: "tde.selected-sfol-proof-context/v1-candidate" as const,
    selection, checks,
    status: checks.every(check => check.status === "match") ? "matched-selected-context" as const : "incomplete-or-drifted" as const,
    f5_eligibility: "blocked-missing-domainspec-v4-chain" as const,
    authority_effect: "none" as const, claim_ceiling: CEILING,
  };
  return { ...unsigned, assessment_digest: digestSfolValue(unsigned) };
}

export function replaySelectedSfolProofContext(root: string, selection: SelectedSfolProofContextSources,
  candidate: SelectedSfolProofContextAssessment): SelectedSfolProofContextAssessment {
  const current = assessSelectedSfolProofContext(root, selection);
  if (canonicalSfolJson(current) !== canonicalSfolJson(candidate))
    fail("REPLAY_MISMATCH", "assessment differs from current selected sources");
  return current;
}
