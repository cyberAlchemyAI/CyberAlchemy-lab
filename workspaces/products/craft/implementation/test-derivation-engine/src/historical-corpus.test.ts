import { appendFileSync, cpSync, mkdtempSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import { HISTORICAL_CORPUS_ROOT, verifyHistoricalPokerTeamCorpus } from "./historical-corpus.js";

function copyCorpus(): { root: string; cleanup(): void } {
  const temp = mkdtempSync(join(tmpdir(), "tde-poker-corpus-"));
  const root = join(temp, "corpus");
  cpSync(HISTORICAL_CORPUS_ROOT, root, { recursive: true });
  return { root, cleanup: () => rmSync(temp, { recursive: true, force: true }) };
}

const selected = "docs/features/auth-access-control/states.md";

describe("historical poker-team corpus import", () => {
  it("verifies the pinned 63-file source before parser use", () => {
    expect(verifyHistoricalPokerTeamCorpus()).toBe(join(HISTORICAL_CORPUS_ROOT, "docs", "features"));
  });

  it.each(["byte edit", "deletion", "extra file", "symlink", "manifest edit"])("rejects %s", (mutation) => {
    const copy = copyCorpus();
    try {
      const target = join(copy.root, selected);
      if (mutation === "byte edit") appendFileSync(target, "\nchanged\n");
      else if (mutation === "deletion") rmSync(target);
      else if (mutation === "extra file") writeFileSync(join(copy.root, "docs/features/auth-access-control/rules.md"), "extra\n");
      else if (mutation === "symlink") symlinkSync(target, join(copy.root, "docs/features/auth-access-control/extra-link.md"));
      else appendFileSync(join(copy.root, "IMPORT-MANIFEST.json"), " ");
      expect(() => verifyHistoricalPokerTeamCorpus(copy.root))
        .toThrowError(expect.objectContaining({ code: "HISTORICAL_CORPUS_DRIFT" }));
    } finally {
      copy.cleanup();
    }
  });
});
