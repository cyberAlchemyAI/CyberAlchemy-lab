import { createHash } from "node:crypto";

import { fail } from "./types.js";

function compareUtf16(left: string, right: string): number {
  return left < right ? -1 : left > right ? 1 : 0;
}

function normalize(value: unknown, seen: Set<object>): unknown {
  if (
    value === undefined ||
    typeof value === "bigint" ||
    typeof value === "function" ||
    typeof value === "symbol"
  ) {
    fail("CANONICALIZATION_UNSUPPORTED", "projection", "canonical JSON received a non-JSON value");
  }
  if (typeof value === "number" && (!Number.isFinite(value) || !Number.isSafeInteger(value))) {
    fail("CANONICALIZATION_UNSUPPORTED", "projection", "canonical JSON numbers must be safe integers");
  }
  if (value === null || typeof value !== "object") return value;
  if (seen.has(value)) {
    fail("CANONICALIZATION_UNSUPPORTED", "projection", "canonical JSON cannot contain cycles");
  }
  seen.add(value);
  try {
    if (Array.isArray(value)) return value.map((entry) => normalize(entry, seen));
    const record = value as Record<string, unknown>;
    return Object.fromEntries(
      Object.keys(record)
        .sort(compareUtf16)
        .map((key) => [key, normalize(record[key], seen)]),
    );
  } finally {
    seen.delete(value);
  }
}

export function canonicalJson(value: unknown): string {
  return JSON.stringify(normalize(value, new Set()));
}

export function stableJson(value: unknown): string {
  return `${JSON.stringify(value, null, 2)}\n`;
}

export function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

export function digestValue(value: unknown): string {
  return sha256(Buffer.from(canonicalJson(value), "utf8"));
}

export function assertCanonicalEqual(left: unknown, right: unknown, message: string): void {
  if (canonicalJson(left) !== canonicalJson(right)) {
    fail("FACT_PROJECTION_DRIFT", "projection", message);
  }
}

export const utf16Compare = compareUtf16;
