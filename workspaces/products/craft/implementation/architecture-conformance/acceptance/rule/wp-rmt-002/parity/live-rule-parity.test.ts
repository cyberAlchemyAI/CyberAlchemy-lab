import {describe, expect, it} from "vitest";

import {evaluateWpRmt002RuleParity} from "./evaluate-rule-parity.js";

describe("RMT-RULE-006 live candidate parity", () => {
  it("proves three adapters, ten semantic controls, and separate native evidence", async () => {
    const result = await evaluateWpRmt002RuleParity();
    expect(result).toMatchObject({
      result: "pass",
      provider_ids: [
        "rule-typescript-v1", "rule-python-v1", "rule-rust-v1",
      ],
      portable_parity: {
        result: "pass",
        targets: ["typescript", "python", "rust"],
      },
      semantic_controls: {declared: 10, killed: 10},
      native_evidence: {
        separated: true,
        native_hash_byte_comparison: false,
      },
      authority_effect: "none",
    });
    expect(result.native_evidence.records).toHaveLength(3);
    expect(new Set(result.native_evidence.records.map(({target}) => target)))
      .toEqual(new Set(["typescript", "python", "rust"]));
    expect(result.semantic_controls.controls).toHaveLength(10);
  }, 120_000);
});
