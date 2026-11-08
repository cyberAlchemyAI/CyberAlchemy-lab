import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import { findDomainSpecSourceRoot } from "./repository-root.js";

describe("DomainSpec source-root discovery", () => {
  it("resolves the original same-directory layout", () => {
    const root = mkdtempSync(join(tmpdir(), "domainspec-root-"));
    try {
      writeFileSync(join(root, "AGENTS.md"), "original layout\n");
      const nested = join(root, "projects", "domainspec-v2", "impl");
      mkdirSync(nested, { recursive: true });
      expect(findDomainSpecSourceRoot(nested)).toBe(root);
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });

  it("resolves the standalone checkout to craft without requiring a sibling", () => {
    const root = mkdtempSync(join(tmpdir(), "domainspec-root-"));
    try {
      writeFileSync(join(root, "AGENTS.md"), "standalone layout\n");
      const nested = join(root, "craft", "projects", "domainspec-v2", "impl");
      mkdirSync(nested, { recursive: true });
      writeFileSync(join(root, "craft", "README.md"), "active source\n");
      expect(findDomainSpecSourceRoot(nested)).toBe(join(root, "craft"));
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });

  it("does not infer a root from an unrelated projects directory", () => {
    const root = mkdtempSync(join(tmpdir(), "domainspec-root-"));
    try {
      const nested = join(root, "projects", "domainspec-v2");
      mkdirSync(nested, { recursive: true });
      expect(findDomainSpecSourceRoot(nested)).toBeNull();
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });
});
