import { createHash } from "node:crypto";
import { lstatSync, readFileSync, readdirSync, realpathSync, statSync } from "node:fs";
import { isAbsolute, join, relative } from "node:path";

import { canonicalSfolJson, digestSfolValue } from "../cases/index.js";
import type { SelectedSfolRef } from "./index.js";
import { assessSelectedSfolProofContext, type SelectedSfolProofContextSources } from "./proof-context.js";
import { validateSourceManifest } from "../../../../cli/src/input/source-manifest.js";

const SHA = /^[a-f0-9]{64}$/;
const AUTH_SOURCE_ROOT = "auth-foundation/implementation/command-boundary-source";
const AUTH_SCAFFOLD = "auth-foundation/development/auth-service-d65-r2-plan/completion-v1/graph-scaffolds/command-boundary-source.json";
const ELIGIBLE = /^(?:project\.json|compositions\/[a-z][a-z0-9]*(?:-[a-z0-9]+)*\.json|edges\/[a-z][a-z0-9]*(?:-[a-z0-9]+)*\.json|specs\/[a-z][a-z0-9]*(?:-[a-z0-9]+)*\/(?:feature\.json|(?:nodes|edges)\/[a-z][a-z0-9]*(?:-[a-z0-9]+)*\.json))$/;
const CEILING = "selected local source bytes only; historical build drift and DomainSpec v4/F5 admission remain blocked" as const;

export type SelectedSfolProofContextV2Selection = Readonly<{
  historical: SelectedSfolProofContextSources;
  scaffold: SelectedSfolRef;
  source_root: string;
}>;
export type SelectedSfolProofContextV2Assessment = Readonly<{
  schema_version: "tde.selected-sfol-proof-context/v2-candidate";
  selection: SelectedSfolProofContextV2Selection;
  manifest_sha256: string;
  aggregate_sha256: string;
  selected_source_count: number;
  eligible_source_count: number;
  source_alignment: "match";
  graph_status: "match";
  profile_status: "match";
  build_status: "match" | "drift" | "unavailable";
  status: "incomplete-or-drifted";
  f5_eligibility: "blocked-missing-domainspec-v4-chain";
  neutral_set_eligible: false;
  authority_effect: "none";
  claim_ceiling: typeof CEILING;
  assessment_digest: string;
}>;

export class SelectedSfolProofContextV2Error extends Error {
  constructor(readonly code: "INVALID_SELECTION" | "SOURCE_DRIFT" | "INVALID_MANIFEST" | "REPLAY_MISMATCH", detail: string) {
    super(`${code}:${detail}`);
    this.name = "SelectedSfolProofContextV2Error";
  }
}
function fail(code: SelectedSfolProofContextV2Error["code"], detail: string): never {
  throw new SelectedSfolProofContextV2Error(code, detail);
}
function object(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}
function exactPath(value: unknown): string {
  if (typeof value !== "string" || !value || isAbsolute(value) || value.includes("\\") ||
      value.split("/").some(part => !part || part === "." || part === ".."))
    fail("INVALID_SELECTION", "noncanonical relative path");
  return value;
}
function sha(bytes: Buffer): string { return createHash("sha256").update(bytes).digest("hex"); }
function rootPath(root: string, subpath: string): string {
  const base = realpathSync(root);
  let path = base;
  for (const part of exactPath(subpath).split("/")) {
    path = join(path, part);
    if (lstatSync(path).isSymbolicLink()) fail("SOURCE_DRIFT", `symlink: ${subpath}`);
  }
  if (relative(base, path).startsWith("..") || realpathSync(path) !== path)
    fail("SOURCE_DRIFT", `escape: ${subpath}`);
  return path;
}
function exactBytes(root: string, ref: SelectedSfolRef): Buffer {
  if (!object(ref) || Object.keys(ref).sort().join(",") !== "path,sha256,size_bytes" ||
      typeof ref.sha256 !== "string" || !SHA.test(ref.sha256) ||
      !Number.isSafeInteger(ref.size_bytes) || ref.size_bytes < 1 || ref.size_bytes > 16 * 1024 * 1024)
    fail("INVALID_SELECTION", "invalid exact reference");
  let path: string;
  try { path = rootPath(root, ref.path); }
  catch (error) { if (error instanceof SelectedSfolProofContextV2Error) throw error; return fail("SOURCE_DRIFT", `unavailable: ${ref.path}`); }
  const before = statSync(path);
  if (!before.isFile() || before.size !== ref.size_bytes) fail("SOURCE_DRIFT", `size/type: ${ref.path}`);
  const bytes = readFileSync(path);
  const after = statSync(path);
  if (before.dev !== after.dev || before.ino !== after.ino || before.mtimeMs !== after.mtimeMs ||
      bytes.length !== ref.size_bytes || sha(bytes) !== ref.sha256)
    fail("SOURCE_DRIFT", `bytes: ${ref.path}`);
  return bytes;
}
function eligiblePaths(sourceRoot: string): string[] {
  const found: string[] = [];
  function walk(dir: string, prefix: string): void {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const rel = prefix ? `${prefix}/${entry.name}` : entry.name;
      const path = join(dir, entry.name);
      const stat = lstatSync(path);
      if (stat.isSymbolicLink()) fail("SOURCE_DRIFT", `symlink in source tree: ${rel}`);
      if (stat.isDirectory()) walk(path, rel);
      else if (ELIGIBLE.test(rel)) {
        if (!stat.isFile()) fail("SOURCE_DRIFT", `non-file semantic input: ${rel}`);
        found.push(rel);
      }
    }
  }
  walk(sourceRoot, "");
  return found.sort();
}

/** Diagnostic only: exact local alignment cannot repin a historical build or admit v4/F5. */
export function assessSelectedSfolProofContextV2(root: string, selection: SelectedSfolProofContextV2Selection): SelectedSfolProofContextV2Assessment {
  if (!object(selection) || Object.keys(selection).sort().join(",") !== "historical,scaffold,source_root")
    fail("INVALID_SELECTION", "selection requires historical, scaffold and source_root");
  if (selection.source_root !== AUTH_SOURCE_ROOT || selection.scaffold?.path !== AUTH_SCAFFOLD ||
      selection.historical?.source_manifest !== null)
    fail("INVALID_SELECTION", "Auth source root/scaffold must be selected and no separate historical manifest may be hidden");
  const sourceRoot = rootPath(root, selection.source_root);
  if (!statSync(sourceRoot).isDirectory()) fail("INVALID_SELECTION", "source root is not a directory");
  const scaffoldBytes = exactBytes(root, selection.scaffold);
  let scaffold: unknown;
  try { scaffold = JSON.parse(scaffoldBytes.toString("utf8")); }
  catch { fail("INVALID_MANIFEST", "scaffold is not JSON"); }
  if (!object(scaffold) || !object(scaffold.graph) || !object(scaffold.graph.source_manifest))
    fail("INVALID_MANIFEST", "missing graph.source_manifest");
  let manifest;
  try { manifest = validateSourceManifest(scaffold.graph.source_manifest); }
  catch (error) { fail("INVALID_MANIFEST", `original source-manifest grammar/digest: ${String(error)}`); }
  if (manifest.project_id !== scaffold.graph.project_id)
    fail("INVALID_MANIFEST", "selected source project mismatch");

  const historical = assessSelectedSfolProofContext(root, selection.historical);
  const clause = JSON.parse(exactBytes(root, selection.historical.clause_manifest).toString("utf8")) as Record<string, unknown>;
  const context = clause.proof_context;
  if (!object(context) || context.manifest_digest !== manifest.manifest_sha256 ||
      context.source_set_digest !== manifest.manifest_sha256)
    fail("INVALID_MANIFEST", "historical clause source-manifest pin mismatch");
  const graph = JSON.parse(exactBytes(root, selection.historical.graph).toString("utf8")) as Record<string, unknown>;
  if (graph.source_manifest_sha256 !== manifest.manifest_sha256)
    fail("INVALID_MANIFEST", "compiled graph/source manifest binding mismatch");
  const graphStatus = historical.checks.find(c => c.role === "graph")?.status;
  const profileStatus = historical.checks.find(c => c.role === "profile")?.status;
  const buildStatus = historical.checks.find(c => c.role === "build")?.status;
  if (graphStatus !== "match" || profileStatus !== "match" || !buildStatus)
    fail("SOURCE_DRIFT", "selected graph or SFOL profile differs");

  const expected = manifest.sources.map(source => source.relative_path);
  const eligible = eligiblePaths(sourceRoot);
  if (canonicalSfolJson(eligible) !== canonicalSfolJson(expected))
    fail("SOURCE_DRIFT", `eligible semantic source set differs: ${eligible.filter(path => !expected.includes(path)).join(",")}`);
  for (const source of manifest.sources) {
    exactBytes(sourceRoot, { path: source.relative_path, size_bytes: source.size_bytes, sha256: source.sha256 });
  }
  const unsigned = {
    schema_version: "tde.selected-sfol-proof-context/v2-candidate" as const,
    selection, manifest_sha256: manifest.manifest_sha256, aggregate_sha256: manifest.aggregate_sha256,
    selected_source_count: manifest.source_count, eligible_source_count: eligible.length,
    source_alignment: "match" as const, graph_status: "match" as const, profile_status: "match" as const,
    build_status: buildStatus, status: "incomplete-or-drifted" as const,
    f5_eligibility: "blocked-missing-domainspec-v4-chain" as const,
    neutral_set_eligible: false as const, authority_effect: "none" as const, claim_ceiling: CEILING,
  };
  return { ...unsigned, assessment_digest: digestSfolValue(unsigned) };
}

export function replaySelectedSfolProofContextV2(root: string, selection: SelectedSfolProofContextV2Selection,
  held: SelectedSfolProofContextV2Assessment): SelectedSfolProofContextV2Assessment {
  const current = assessSelectedSfolProofContextV2(root, selection);
  if (canonicalSfolJson(current) !== canonicalSfolJson(held))
    fail("REPLAY_MISMATCH", "held assessment differs from current selected bytes");
  return current;
}
