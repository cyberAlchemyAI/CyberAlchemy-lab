import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

import { decodeFactoryRunRequestV1 } from "../codecs/decode-factory-run-request-v1.js";
import { repositoryRoot } from "../cli/index.js";
import { executeFactoryRun } from "../pipeline/execute-factory-run.js";
import { planFactoryRun } from "../pipeline/plan-factory-run.js";

describe("RMT-FND-001 locked-child result path", () => {
  it("returns the Rule semantic result instead of empty child stdout", async () => {
    const outputParent = await mkdtemp(resolve(tmpdir(), "domainspec-factory-empty-stdout-red-"));
    try {
      const request = decodeFactoryRunRequestV1(JSON.parse(await readFile(resolve(
        repositoryRoot,
        "projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/rule-only.request.json",
      ), "utf8")));
      const plan = await planFactoryRun({ repositoryRoot, request });

      await expect(executeFactoryRun({ repositoryRoot, outputParent, plan })).resolves.toMatchObject({
        result: "pass",
        authority_effect: "none",
      });
    } finally {
      await rm(outputParent, { recursive: true, force: true });
    }
  }, 70_000);
});
