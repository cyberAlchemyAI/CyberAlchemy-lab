import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

import { decodeFactoryRunRequestV1 } from "../codecs/decode-factory-run-request-v1.js";
import { repositoryRoot } from "../cli/index.js";

const fixturePath = resolve(
  repositoryRoot,
  "projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/reference-suite.request.json",
);
const fixture = async () => JSON.parse(await readFile(fixturePath, "utf8"));

describe("FactoryRunRequest/v1", () => {
  it("decodes the closed reference request", async () => {
    const request = decodeFactoryRunRequestV1(await fixture());
    expect(request).toMatchObject({
      purpose: "reference-reproduction",
      authority_effect: "none",
    });
    expect(request.nodes).toHaveLength(9);
  });

  it("rejects unknown fields and unsafe paths", async () => {
    const unknown = { ...await fixture(), invented: true };
    expect(() => decodeFactoryRunRequestV1(unknown)).toThrow("FACTORY_REQUEST_INVALID");
    const unsafe = await fixture();
    unsafe.nodes[0].input_refs[0].ref.path = "../outside.json";
    expect(() => decodeFactoryRunRequestV1(unsafe)).toThrow("FACTORY_REQUEST_INVALID");
  });

  it("rejects historical MTF evidence as a fresh input", async () => {
    const historical = await fixture();
    historical.nodes[0].input_refs[0].ref.path =
      "projects/domainspec-v2/development/meta-type-realization-factory/runs/MTF-021/proof.json";
    expect(() => decodeFactoryRunRequestV1(historical))
      .toThrow("FACTORY_HISTORICAL_EVIDENCE_DEPENDENCY");
  });
});
