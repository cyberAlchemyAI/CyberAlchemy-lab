import { mkdtempSync, readFileSync, readdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import {
  CONTRACT_FILES,
  JSON_SCHEMA_DIALECT,
  SUPPORTED_SCHEMA_KEYWORDS,
  canonicalize,
  createContractPublicationReceipt,
  publicationReceiptBytes,
  validatePublishedSchema,
  verifyContractPublicationReceipt,
  writeContractPublicationArtifacts,
} from "./contract-publication.js";
import { BTE_DIAGNOSTICS } from "./validation/diagnostics.js";

describe("L0A contract publication", () => {
  it("publishes the exact nine contracts and a closed deterministic diagnostic registry", () => {
    const receipt = createContractPublicationReceipt();
    expect(receipt.receipt_kind).toBe("contract-publication");
    expect(receipt.schema_version).toBe("bte-contract-publication-receipt/v1");
    expect(receipt.admission).toBe("not-granted");
    expect(receipt.dialect).toBe(JSON_SCHEMA_DIALECT);
    expect(receipt.supported_keywords).toEqual(SUPPORTED_SCHEMA_KEYWORDS);
    expect(receipt.contracts.map(({ logical_identity }) => logical_identity.key)).toEqual(CONTRACT_FILES);
    expect(receipt.contracts).toHaveLength(9);
    expect(new Set(BTE_DIAGNOSTICS.map(({ code }) => code)).size).toBe(BTE_DIAGNOSTICS.length);
    expect(new Set(BTE_DIAGNOSTICS.map(({ precedence }) => precedence)).size).toBe(BTE_DIAGNOSTICS.length);
  });

  it("rejects a schema keyword outside the published Draft 2020-12 subset", () => {
    const schema = {
      $schema: JSON_SCHEMA_DIALECT,
      $id: "urn:domainspec-v2:bte:test:unsupported-keyword",
      type: "object",
      unevaluatedProperties: false,
    };
    const registry = new Map([[schema.$id, schema]]);
    expect(() => validatePublishedSchema(schema, registry)).toThrow("BTE_SCHEMA_UNSUPPORTED_KEYWORD");
  });

  it("recomputes exact handles instead of trusting a modified receipt", () => {
    const receipt = structuredClone(createContractPublicationReceipt());
    expect(verifyContractPublicationReceipt(receipt)).toEqual({ result: "pass", codes: [] });
    const firstContract = receipt.contracts[0];
    expect(firstContract).toBeDefined();
    if (!firstContract) throw new Error("expected the exact L0A contract set");
    firstContract.bytes += 1;
    expect(verifyContractPublicationReceipt(receipt)).toEqual({
      result: "fail",
      codes: ["BTE_DIGEST_MISMATCH"],
    });
  });

  it("produces byte-identical receipts over two invocations", () => {
    const first = publicationReceiptBytes();
    const second = publicationReceiptBytes();
    expect(first).toBe(second);
    expect(first).toBe(`${canonicalize(JSON.parse(first))}\n`);
  });

  it("writes only the two allowlisted L0A run artifacts and remains idempotent", () => {
    const root = mkdtempSync(resolve(tmpdir(), "domainspec-bte-l0a-"));
    try {
      const outputDir = resolve(root, "run/l0a");
      const first = writeContractPublicationArtifacts(outputDir);
      const second = writeContractPublicationArtifacts(outputDir);
      expect(second).toEqual(first);
      expect(readdirSync(outputDir).sort()).toEqual([
        "contract-publication-receipt.json",
        "output-write-manifest.json",
      ]);
      expect(readFileSync(resolve(outputDir, "contract-publication-receipt.json"), "utf8")).toBe(
        first.receiptBytes,
      );
      expect(JSON.parse(first.receiptBytes).schema_version).not.toBe("bte-validation-receipt/v1");
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });
});
