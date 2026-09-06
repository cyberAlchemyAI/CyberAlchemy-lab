#!/usr/bin/env tsx

import { createHash } from "node:crypto";
import {
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { dirname, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const TERM = "Saga";
const TERM_PATTERN = /\bSaga\b/gi;
const DEFAULT_ALLOWED_MANIFEST_CLASSES = new Set([
  "historical-research",
  "superseded-decision",
  "telemetry-or-receipt",
]);
const DEFAULT_GUARD_OWNED_PATHS = new Set([
  "projects/domainspec-v2/impl/tools/audit-retired-orchestration-references.ts",
  "projects/domainspec-v2/impl/tools/tests/audit-retired-orchestration-references.test.ts",
  "projects/domainspec-v2/impl/tools/retired-orchestration-reference-allowlist.json",
]);
const REMOVAL_PACKAGE_PREFIX = "projects/domainspec-v2/development/saga-removal/";

export type MatchRecord = {
  path: string;
  matchCount: number;
  matchedLines: string[];
  matchDigest: string;
};

type ManifestEntry = {
  path: string;
  match_count: number;
  classification: string;
  reason: string;
  planned_action?: string;
};

type ReferenceManifest = {
  schema_version: string;
  swu_id: string;
  source_revision?: string;
  entries: ManifestEntry[];
};

export type ExceptionEntry = {
  path: string;
  disposition:
    | "reviewed-current-plan-reference"
    | "post-manifest-historical-reference"
    | "negative-proof";
  reason: string;
  expected_match_count: number;
  match_digest: string;
};

type ReferenceAllowlist = {
  schema_version: string;
  guard_id: string;
  manifest: string;
  exceptions: ExceptionEntry[];
};

export type AuditViolation = {
  path: string;
  code:
    | "active-classification"
    | "unclassified"
    | "manifest-count-drift"
    | "manifest-reason-missing"
    | "exception-count-drift"
    | "exception-digest-drift"
    | "exception-reason-missing"
    | "unused-exception"
    | "missing-exception-path";
  detail: string;
};

export type AuditEntry = {
  path: string;
  match_count: number;
  source_classification: string;
  effective_disposition: string;
  reason: string;
  status: "allowed" | "violation";
};

export type AuditReport = {
  schema_version: "1.0.0";
  guard_id: "domainspec-v2-zero-active-saga-reference-guard";
  term: string;
  case_insensitive: true;
  whole_word: true;
  project_root: string;
  manifest: string;
  allowlist: string;
  source_revision: string | null;
  summary: {
    result: "pass" | "fail";
    matching_files: number;
    total_matches: number;
    allowed_files: number;
    violations: number;
  };
  entries: AuditEntry[];
  violations: AuditViolation[];
};

export type AuditOptions = {
  repoRoot: string;
  projectRoot: string;
  manifestPath: string;
  allowlistPath: string;
  guardOwnedPaths?: Set<string>;
};

export function auditReferences(options: AuditOptions): AuditReport {
  const repoRoot = resolve(options.repoRoot);
  const projectRoot = resolve(options.projectRoot);
  const manifestPath = resolve(options.manifestPath);
  const allowlistPath = resolve(options.allowlistPath);
  const guardOwnedPaths = options.guardOwnedPaths ?? DEFAULT_GUARD_OWNED_PATHS;
  const manifest = readJson<ReferenceManifest>(manifestPath);
  const allowlist = readJson<ReferenceAllowlist>(allowlistPath);
  const manifestByPath = new Map(manifest.entries.map((entry) => [entry.path, entry]));
  const exceptionsByPath = new Map(allowlist.exceptions.map((entry) => [entry.path, entry]));
  const usedExceptions = new Set<string>();
  const matches = collectReferenceMatches(repoRoot, projectRoot);
  const entries: AuditEntry[] = [];
  const violations: AuditViolation[] = [];

  for (const match of matches) {
    const manifestEntry = manifestByPath.get(match.path);
    const exception = exceptionsByPath.get(match.path);
    let violation: AuditViolation | undefined;
    let effectiveDisposition = manifestEntry?.classification || "unclassified";
    let reason = manifestEntry?.reason || "";

    if (guardOwnedPaths.has(match.path)) {
      effectiveDisposition = "guard-owned";
      reason = "Exact implementation surface required to define and test the reference guard.";
    } else if (match.path.startsWith(REMOVAL_PACKAGE_PREFIX)) {
      effectiveDisposition = "removal-package";
      reason = "Saga-removal planning, execution, validation, or receipt evidence.";
    } else if (exception) {
      usedExceptions.add(exception.path);
      effectiveDisposition = exception.disposition;
      reason = exception.reason;
      if (!exception.reason.trim()) {
        violation = makeViolation(match.path, "exception-reason-missing", "Reviewed exception has no reason.");
      } else if (match.matchCount !== exception.expected_match_count) {
        violation = makeViolation(
          match.path,
          "exception-count-drift",
          `Expected ${exception.expected_match_count} match(es), found ${match.matchCount}.`,
        );
      } else if (match.matchDigest !== exception.match_digest) {
        violation = makeViolation(
          match.path,
          "exception-digest-drift",
          `Matched-line digest changed: expected ${exception.match_digest}, found ${match.matchDigest}.`,
        );
      }
    } else if (!manifestEntry) {
      violation = makeViolation(match.path, "unclassified", "Matching file is absent from the frozen manifest and exception allowlist.");
    } else if (!manifestEntry.reason?.trim()) {
      violation = makeViolation(match.path, "manifest-reason-missing", "Manifest classification has no reason.");
    } else if (!DEFAULT_ALLOWED_MANIFEST_CLASSES.has(manifestEntry.classification)) {
      violation = makeViolation(
        match.path,
        "active-classification",
        `Manifest classification '${manifestEntry.classification}' is not allowed by the zero-active guard.`,
      );
    } else if (match.matchCount !== manifestEntry.match_count) {
      violation = makeViolation(
        match.path,
        "manifest-count-drift",
        `Frozen manifest expected ${manifestEntry.match_count} match(es), found ${match.matchCount}.`,
      );
    }

    if (violation) violations.push(violation);
    entries.push({
      path: match.path,
      match_count: match.matchCount,
      source_classification: manifestEntry?.classification || "unclassified",
      effective_disposition: effectiveDisposition,
      reason,
      status: violation ? "violation" : "allowed",
    });
  }

  for (const exception of allowlist.exceptions) {
    const absolute = resolve(repoRoot, exception.path);
    if (!existsSync(absolute) || !statSync(absolute).isFile()) {
      violations.push(makeViolation(exception.path, "missing-exception-path", "Reviewed exception path does not exist."));
    } else if (!usedExceptions.has(exception.path)) {
      violations.push(makeViolation(exception.path, "unused-exception", "Reviewed exception exists but has no live whole-word match."));
    }
  }

  entries.sort((a, b) => a.path.localeCompare(b.path));
  violations.sort((a, b) => a.path.localeCompare(b.path) || a.code.localeCompare(b.code));
  return {
    schema_version: "1.0.0",
    guard_id: "domainspec-v2-zero-active-saga-reference-guard",
    term: TERM,
    case_insensitive: true,
    whole_word: true,
    project_root: toRepoPath(repoRoot, projectRoot),
    manifest: toRepoPath(repoRoot, manifestPath),
    allowlist: toRepoPath(repoRoot, allowlistPath),
    source_revision: manifest.source_revision || null,
    summary: {
      result: violations.length === 0 ? "pass" : "fail",
      matching_files: matches.length,
      total_matches: matches.reduce((sum, match) => sum + match.matchCount, 0),
      allowed_files: entries.filter((entry) => entry.status === "allowed").length,
      violations: violations.length,
    },
    entries,
    violations,
  };
}

export function collectReferenceMatches(repoRootInput: string, projectRootInput: string): MatchRecord[] {
  const repoRoot = resolve(repoRootInput);
  const projectRoot = resolve(projectRootInput);
  const records: MatchRecord[] = [];
  for (const file of walkTextFiles(projectRoot)) {
    const raw = readFileSync(file, "utf8");
    const matchedLines: string[] = [];
    let matchCount = 0;
    for (const line of raw.split(/\r?\n/)) {
      const count = [...line.matchAll(TERM_PATTERN)].length;
      if (count > 0) {
        matchCount += count;
        matchedLines.push(`${count}\t${line.trim()}`);
      }
    }
    if (matchCount > 0) {
      records.push({
        path: toRepoPath(repoRoot, file),
        matchCount,
        matchedLines,
        matchDigest: digestMatchedLines(matchedLines),
      });
    }
  }
  return records.sort((a, b) => a.path.localeCompare(b.path));
}

export function digestMatchedLines(lines: string[]): string {
  return createHash("sha256").update(JSON.stringify(lines)).digest("hex");
}

export function renderSummary(report: AuditReport): string {
  const lines = [
    "# Zero-Active Saga Reference Audit",
    "",
    `- Result: **${report.summary.result.toUpperCase()}**`,
    `- Matching files: ${report.summary.matching_files}`,
    `- Whole-word matches: ${report.summary.total_matches}`,
    `- Allowed files: ${report.summary.allowed_files}`,
    `- Violations: ${report.summary.violations}`,
    `- Manifest: \`${report.manifest}\``,
    `- Allowlist: \`${report.allowlist}\``,
  ];
  if (report.violations.length > 0) {
    lines.push("", "## Violations", "");
    for (const violation of report.violations) {
      lines.push(`- \`${violation.path}\` [${violation.code}]: ${violation.detail}`);
    }
  }
  return `${lines.join("\n")}\n`;
}

function walkTextFiles(root: string): string[] {
  const out: string[] = [];
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    if (entry.name === "node_modules" || entry.name === ".git") continue;
    const path = resolve(root, entry.name);
    if (entry.isDirectory()) out.push(...walkTextFiles(path));
    else if (entry.isFile() && isTextFile(path)) out.push(path);
  }
  return out;
}

function isTextFile(path: string): boolean {
  const sample = readFileSync(path).subarray(0, 8192);
  return !sample.includes(0);
}

function readJson<T>(path: string): T {
  if (!existsSync(path)) throw new Error(`required JSON file not found: ${path}`);
  return JSON.parse(readFileSync(path, "utf8")) as T;
}

function makeViolation(path: string, code: AuditViolation["code"], detail: string): AuditViolation {
  return { path, code, detail };
}

function toRepoPath(repoRoot: string, path: string): string {
  return relative(repoRoot, path).replace(/\\/g, "/");
}

function getArg(args: string[], name: string): string | undefined {
  const index = args.indexOf(name);
  return index < 0 ? undefined : args[index + 1];
}

function writeOutput(path: string, content: string): void {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, content, "utf8");
}

function runCli(): void {
  const args = process.argv.slice(2);
  const implRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
  const projectRoot = resolve(getArg(args, "--project-root") || resolve(implRoot, ".."));
  const repoRoot = resolve(getArg(args, "--repo-root") || resolve(projectRoot, "../.."));
  const manifestPath = resolve(
    getArg(args, "--manifest") ||
      resolve(projectRoot, "development/saga-removal/runs/SWU-SGRM-001/ACTIVE-REFERENCE-MANIFEST.json"),
  );
  const allowlistPath = resolve(
    getArg(args, "--allowlist") || resolve(implRoot, "tools/retired-orchestration-reference-allowlist.json"),
  );
  const report = auditReferences({ repoRoot, projectRoot, manifestPath, allowlistPath });
  const json = `${JSON.stringify(report, null, 2)}\n`;
  const summary = renderSummary(report);
  const jsonOutput = getArg(args, "--json-output");
  const summaryOutput = getArg(args, "--summary-output");
  if (jsonOutput) writeOutput(resolve(jsonOutput), json);
  if (summaryOutput) writeOutput(resolve(summaryOutput), summary);
  process.stdout.write(summary);
  process.exitCode = report.summary.result === "pass" ? 0 : 1;
}

const invokedPath = process.argv[1] ? resolve(process.argv[1]) : "";
if (invokedPath === fileURLToPath(import.meta.url)) runCli();
