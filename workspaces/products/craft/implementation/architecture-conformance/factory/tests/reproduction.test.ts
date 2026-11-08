import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

import { decodeFactoryRunRequestV1 } from "../codecs/decode-factory-run-request-v1.js";
import { repositoryRoot } from "../cli/index.js";
import { reproduceReferenceSuite } from "../pipeline/reproduce-reference-suite.js";

describe("reference reproduction", () => {
  it("produces equal semantic receipts in isolated roots", async () => {
    const parent = await mkdtemp(resolve(tmpdir(), "domainspec-factory-reproduce-"));
    try {
      const request = decodeFactoryRunRequestV1(JSON.parse(await readFile(resolve(
        repositoryRoot,
        "projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/reference-suite.request.json",
      ), "utf8")));
      const result = await reproduceReferenceSuite({
        repositoryRoot,
        request,
        outputRoot: resolve(parent, "result"),
      });
      const receipt = JSON.parse(await readFile(result.reproduction_receipt, "utf8"));
      expect(result.result).toBe("pass");
      expect(receipt.runs).toHaveLength(2);
      expect(new Set(receipt.process_observation_sha256).size).toBe(2);
    } finally {
      await rm(parent, { recursive: true, force: true });
    }
  }, 900_000);
});
