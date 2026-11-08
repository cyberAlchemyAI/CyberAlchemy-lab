import {
  existsSync,
  mkdirSync,
  readFileSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { dirname, isAbsolute, relative, resolve } from "node:path";

import { sha256, stableJson } from "./canonical-json.js";
import { fail, type ExactRef, type L2ErrorCode } from "./types.js";

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
  if (
    path.length === 0 ||
    isAbsolute(path) ||
    path.split(/[\\/]/u).includes("..")
  ) {
    fail("TARGET_BASELINE_DRIFT", "admission", `unsafe repository path: ${path}`, 2);
  }
  const absolute = resolve(repoRoot, path);
  const fromRoot = relative(repoRoot, absolute);
  if (fromRoot.startsWith("..") || isAbsolute(fromRoot)) {
    fail("TARGET_BASELINE_DRIFT", "admission", `repository path escapes root: ${path}`, 2);
  }
  return absolute;
}

export function exactRef(repoRoot: string, path: string): ExactRef {
  const absolute = safeRepositoryPath(repoRoot, path);
  if (!existsSync(absolute) || !statSync(absolute).isFile()) {
    fail("TARGET_BASELINE_DRIFT", "admission", `exact-ref target absent: ${path}`, 2);
  }
  const bytes = readFileSync(absolute);
  return {
    path: path.replaceAll("\\", "/"),
    sha256: sha256(bytes),
    size_bytes: bytes.length,
  };
}

export function assertExactRef(
  repoRoot: string,
  expected: ExactRef,
  code: L2ErrorCode = "TARGET_BASELINE_DRIFT",
): ExactRef {
  const observed = exactRef(repoRoot, expected.path);
  if (
    observed.sha256 !== expected.sha256 ||
    observed.size_bytes !== expected.size_bytes
  ) {
    fail(code, "admission", `exact ref drift: ${expected.path}`, code === "TARGET_BASELINE_DRIFT" ? 2 : 1);
  }
  return observed;
}

export function readJson<T>(repoRoot: string, path: string): T {
  try {
    return JSON.parse(readFileSync(safeRepositoryPath(repoRoot, path), "utf8")) as T;
  } catch (error) {
    fail(
      "TARGET_BASELINE_DRIFT",
      "admission",
      `invalid JSON ${path}: ${error instanceof Error ? error.message : String(error)}`,
      2,
    );
  }
}

export function writeStableJson(
  repoRoot: string,
  path: string,
  value: unknown,
  created: string[] = [],
): ExactRef {
  return writeStableText(repoRoot, path, stableJson(value), created);
}

export function writeStableText(
  repoRoot: string,
  path: string,
  bytes: string,
  created: string[] = [],
): ExactRef {
  const absolute = safeRepositoryPath(repoRoot, path);
  if (!bytes.endsWith("\n") || bytes.startsWith("\uFEFF")) {
    fail("UNDECLARED_WRITE", "closure", `invalid text envelope for ${path}`);
  }
  mkdirSync(dirname(absolute), { recursive: true });
  if (existsSync(absolute)) {
    if (!statSync(absolute).isFile() || readFileSync(absolute, "utf8") !== bytes) {
      fail("TARGET_BASELINE_DRIFT", "admission", `create target collision: ${path}`, 2);
    }
  } else {
    writeFileSync(absolute, bytes, "utf8");
    created.push(absolute);
  }
  return exactRef(repoRoot, path);
}
