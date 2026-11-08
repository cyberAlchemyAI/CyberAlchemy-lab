import { createHash } from "node:crypto";
import {
  existsSync,
  mkdirSync,
  readFileSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { dirname, isAbsolute, relative, resolve } from "node:path";

import { fail, type ExactRef, type L1ErrorCode } from "./types.js";

function normalize(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(normalize);
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>)
        .sort(([left], [right]) => left < right ? -1 : left > right ? 1 : 0)
        .map(([key, entry]) => [key, normalize(entry)]),
    );
  }
  if (typeof value === "number" && (!Number.isFinite(value) || !Number.isSafeInteger(value))) {
    fail("TARGET_BASELINE_DRIFT", "admission", "canonical payload contains a non-safe integer");
  }
  return value;
}

export function canonicalJson(value: unknown): string {
  return JSON.stringify(normalize(value));
}

export function digestValue(value: unknown): string {
  return sha256(Buffer.from(canonicalJson(value), "utf8"));
}

export function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

export function stableBytes(value: unknown): string {
  return `${JSON.stringify(value, null, 2)}\n`;
}

export function repositoryRoot(start = process.cwd()): string {
  let cursor = resolve(start);
  for (;;) {
    if (
      existsSync(resolve(cursor, "AGENTS.md")) &&
      existsSync(resolve(cursor, "projects/domainspec-v2"))
    ) return cursor;
    const parent = dirname(cursor);
    if (parent === cursor) {
      fail("TARGET_BASELINE_DRIFT", "admission", "repository root could not be resolved", 2);
    }
    cursor = parent;
  }
}

export function safeRepositoryPath(repoRoot: string, path: string): string {
  if (isAbsolute(path) || path.split(/[\\/]/u).includes("..")) {
    fail("TARGET_BASELINE_DRIFT", "admission", `unsafe repository path: ${path}`, 2);
  }
  const absolute = resolve(repoRoot, path);
  const fromRoot = relative(repoRoot, absolute);
  if (fromRoot.startsWith("..") || isAbsolute(fromRoot)) {
    fail("TARGET_BASELINE_DRIFT", "admission", `path escapes repository: ${path}`, 2);
  }
  return absolute;
}

export function exactRef(repoRoot: string, path: string): ExactRef {
  const absolute = safeRepositoryPath(repoRoot, path);
  if (!existsSync(absolute) || !statSync(absolute).isFile()) {
    fail("TARGET_BASELINE_DRIFT", "admission", `exact-ref target is absent: ${path}`, 2);
  }
  const bytes = readFileSync(absolute);
  return { path: path.replaceAll("\\", "/"), sha256: sha256(bytes), size_bytes: bytes.length };
}

export function assertExactRef(
  repoRoot: string,
  ref: ExactRef,
  code: L1ErrorCode = "TARGET_BASELINE_DRIFT",
): ExactRef {
  const actual = exactRef(repoRoot, ref.path);
  if (actual.sha256 !== ref.sha256 || actual.size_bytes !== ref.size_bytes) {
    fail(code, "binding", `exact ref drift: ${ref.path}`);
  }
  return actual;
}

export function readJson<T>(repoRoot: string, path: string): T {
  const absolute = safeRepositoryPath(repoRoot, path);
  try {
    return JSON.parse(readFileSync(absolute, "utf8")) as T;
  } catch (error) {
    fail(
      "TARGET_BASELINE_DRIFT",
      "admission",
      `invalid JSON ${path}: ${error instanceof Error ? error.message : String(error)}`,
      2,
    );
  }
}

export function assertCanonicalEqual(left: unknown, right: unknown, message: string): void {
  if (canonicalJson(left) !== canonicalJson(right)) {
    fail("OBLIGATION_MISMATCH", "derivation", message);
  }
}

export function writeStableJson(
  repoRoot: string,
  path: string,
  value: unknown,
  created: string[] = [],
): ExactRef {
  const absolute = safeRepositoryPath(repoRoot, path);
  const bytes = stableBytes(value);
  mkdirSync(dirname(absolute), { recursive: true });
  if (existsSync(absolute)) {
    if (readFileSync(absolute, "utf8") !== bytes) {
      fail("CREATE_TARGET_COLLISION", "admission", `existing candidate evidence differs: ${path}`, 2);
    }
  } else {
    writeFileSync(absolute, bytes, "utf8");
    created.push(absolute);
  }
  return exactRef(repoRoot, path);
}
