import { appendFileSync, cpSync, mkdtempSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import {
  HISTORICAL_BACKEND_ROOT,
  importHistoricalPokerTeamBackendModule,
  verifyHistoricalPokerTeamBackend,
} from "./historical-backend.js";

function copyBackend(): { root: string; cleanup(): void } {
  const temp = mkdtempSync(join(tmpdir(), "tde-poker-backend-"));
  const root = join(temp, "backend-fixture");
  cpSync(HISTORICAL_BACKEND_ROOT, root, { recursive: true });
  return { root, cleanup: () => rmSync(temp, { recursive: true, force: true }) };
}

const selected = "backend/src/domain/settlement/settlement.service.ts";

describe("historical P4/R4 backend source import", () => {
  it("verifies the pinned 18-file closure before import", () => {
    expect(verifyHistoricalPokerTeamBackend()).toBe(join(HISTORICAL_BACKEND_ROOT, "backend", "src"));
  });

  it.each(["byte edit", "deletion", "extra file", "symlink", "manifest edit"])("rejects %s", async (mutation) => {
    const copy = copyBackend();
    try {
      const target = join(copy.root, selected);
      if (mutation === "byte edit") appendFileSync(target, "\nchanged\n");
      else if (mutation === "deletion") rmSync(target);
      else if (mutation === "extra file") writeFileSync(join(copy.root, "backend/src/domain/settlement/extra.ts"), "extra\n");
      else if (mutation === "symlink") symlinkSync(target, join(copy.root, "backend/src/domain/settlement/extra-link.ts"));
      else appendFileSync(join(copy.root, "IMPORT-MANIFEST.json"), " ");
      expect(() => verifyHistoricalPokerTeamBackend(copy.root))
        .toThrowError(expect.objectContaining({ code: "HISTORICAL_BACKEND_DRIFT" }));
      await expect(importHistoricalPokerTeamBackendModule("r4-settlement", copy.root))
        .rejects.toMatchObject({ code: "HISTORICAL_BACKEND_DRIFT" });
    } finally {
      copy.cleanup();
    }
  });
});
