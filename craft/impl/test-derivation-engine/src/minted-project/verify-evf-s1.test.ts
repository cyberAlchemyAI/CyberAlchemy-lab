import { spawnSync } from "node:child_process";
import {
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { assertRequiredTestTargets } from "./verify-evf-s1.js";
import {
  ACCEPTANCE_VECTOR,
  EVF_PATHS,
  EvfS1Error,
} from "./types.js";

const REPO_ROOT = fileURLToPath(new URL("../../../../../..", import.meta.url));
const TSX = resolve(REPO_ROOT, "projects/domainspec-v2/impl/node_modules/.bin/tsx");
const VERIFIER = resolve(
  REPO_ROOT,
  "projects/domainspec-v2/impl/test-derivation-engine/src/minted-project/verify-evf-s1.ts",
);

type ValidationContract = {
  readonly required_test_targets: readonly string[];
};

describe("EVF S1 terminal verifier", () => {
  it("runs as a subprocess and writes the exact bounded evidence denominator", () => {
    const outputRoot = mkdtempSync(join(tmpdir(), "domainspec-evf-s1-"));
    try {
      const child = spawnSync(TSX, [VERIFIER, "--output-root", outputRoot], {
        cwd: REPO_ROOT,
        encoding: "utf8",
        timeout: 300_000,
        maxBuffer: 16 * 1024 * 1024,
        env: { ...process.env, NO_COLOR: "1" },
      });
      if (child.error || child.status !== 0) {
        throw new Error(
          `terminal verifier failed (${child.status ?? "spawn"}): ${child.stderr || child.stdout}`,
        );
      }

      const result = JSON.parse(child.stdout.trim()) as {
        status: string;
        acceptance_vector: unknown;
        mutant_kills: number;
        negative_receipts: number;
        positive_receipt_issued: boolean;
        release_admission: string;
      };
      const negativeFiles = readdirSync(join(outputRoot, "negative"))
        .filter((name) => name.endsWith(".receipt.json"));
      const inventory = JSON.parse(
        readFileSync(join(outputRoot, "target-result-inventory.json"), "utf8"),
      ) as { target_count: number; targets: readonly unknown[] };

      expect(result).toMatchObject({
        status: "pass",
        acceptance_vector: ACCEPTANCE_VECTOR,
        mutant_kills: 16,
        negative_receipts: 16,
        positive_receipt_issued: true,
        release_admission: "not-granted",
      });
      expect(negativeFiles).toHaveLength(16);
      expect(inventory.target_count).toBe(21);
      expect(inventory.targets).toHaveLength(20);
    } finally {
      rmSync(outputRoot, { recursive: true, force: true });
    }
  }, 300_000);

  it("rejects an omitted or reordered required test target", () => {
    const contract = JSON.parse(
      readFileSync(resolve(REPO_ROOT, EVF_PATHS.validationContract), "utf8"),
    ) as ValidationContract;
    const required = contract.required_test_targets;

    expect(() => assertRequiredTestTargets(required, required)).not.toThrow();
    for (const actual of [required.slice(0, -1), [...required].reverse()]) {
      try {
        assertRequiredTestTargets(actual, required);
      } catch (error) {
        expect(error).toBeInstanceOf(EvfS1Error);
        expect((error as EvfS1Error).code).toBe("VERIFIER_TARGET_OMITTED");
        continue;
      }
      throw new Error("expected verifier-target omission rejection");
    }
  });
});
