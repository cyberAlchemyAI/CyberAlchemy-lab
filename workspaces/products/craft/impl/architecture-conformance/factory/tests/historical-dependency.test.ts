import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

const forbiddenHistoricalEvidenceRoots = Object.freeze([
  "development/meta-type-realization-factory/runs",
  "development/meta-type-realization-factory/receipts",
]);
const architectureRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");

describe("fresh factory inputs", () => {
  it("do not depend on historical meta-type realization evidence", async () => {
    const source = await readFile(resolve(
      architectureRoot,
      "acceptance/rule/typescript/run-rule-proof.ts",
    ), "utf8");
    const historicalDependency = forbiddenHistoricalEvidenceRoots.find((root) =>
      source.includes(root)
    );

    expect(
      historicalDependency,
      "FACTORY_HISTORICAL_EVIDENCE_DEPENDENCY",
    ).toBeUndefined();
  });
});
