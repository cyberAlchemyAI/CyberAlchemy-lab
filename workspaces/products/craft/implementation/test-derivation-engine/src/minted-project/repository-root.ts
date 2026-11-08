import { existsSync } from "node:fs";
import { dirname, resolve } from "node:path";

/** Return the source root for exact DomainSpec-relative refs, not the Git root. */
export function findDomainSpecSourceRoot(start = process.cwd()): string | null {
  let cursor = resolve(start);
  for (;;) {
    if (existsSync(resolve(cursor, "AGENTS.md"))) {
      // Original DomainSpec layout remains valid for historical local runs.
      if (existsSync(resolve(cursor, "projects/domainspec-v2"))) return cursor;
      // The standalone checkout keeps the active, unchanged relative tree in craft/.
      if (
        existsSync(resolve(cursor, "craft/README.md")) &&
        existsSync(resolve(cursor, "craft/projects/domainspec-v2"))
      ) return resolve(cursor, "craft");
    }
    const parent = dirname(cursor);
    if (parent === cursor) return null;
    cursor = parent;
  }
}
