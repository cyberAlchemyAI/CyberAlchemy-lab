import fs from "node:fs";

export const MAX_SOURCE_FILE_BYTES = 8 * 1024 * 1024;
export const MAX_PROJECT_SOURCES = 10_000;
export const MAX_PROJECT_NODES = 10_000;
export const MAX_PROJECT_RELATIONSHIPS = 50_000;
export const MAX_JSON_DEPTH = 128;
export const SUBPROCESS_TIMEOUT_MS = 120_000;

export function readBoundedFileSync(file: string, limit = MAX_SOURCE_FILE_BYTES): Buffer {
  const size = fs.statSync(file).size;
  if (size > limit) throw new RangeError(`input exceeds ${limit} bytes:${file}`);
  return fs.readFileSync(file);
}

export function assertBoundedJsonDepth(value: unknown, limit = MAX_JSON_DEPTH): void {
  const pending: Array<{ readonly value: unknown; readonly depth: number }> = [{ value, depth: 0 }];
  while (pending.length > 0) {
    const current = pending.pop()!;
    if (current.depth > limit) throw new RangeError(`JSON nesting exceeds ${limit}`);
    if (Array.isArray(current.value)) {
      for (const entry of current.value) pending.push({ value: entry, depth: current.depth + 1 });
    } else if (current.value !== null && typeof current.value === "object") {
      for (const entry of Object.values(current.value as Record<string, unknown>)) pending.push({ value: entry, depth: current.depth + 1 });
    }
  }
}
