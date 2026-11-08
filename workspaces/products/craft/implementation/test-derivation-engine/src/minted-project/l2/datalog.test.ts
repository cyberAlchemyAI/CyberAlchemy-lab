import { describe, expect, it } from "vitest";

import {
  datalogArgv,
  mapDatalogOutcome,
  parseViolationCsv,
} from "./datalog.js";

describe("EVF L2 Souffle adapter", () => {
  it("builds the exact one-worker interpreter argv", () => {
    expect(datalogArgv("/tool/souffle", "/facts", "/output", "/query.dl")).toEqual([
      "/tool/souffle",
      "-j",
      "1",
      "-F",
      "/facts",
      "-D",
      "/output",
      "/query.dl",
    ]);
  });

  it("maps a complete empty relation to no-counterexample", () => {
    expect(parseViolationCsv("")).toEqual([]);
    expect(mapDatalogOutcome([], true)).toBe("no-counterexample");
  });

  it("maps a complete sorted relation to counterexample", () => {
    const rows = parseViolationCsv(
      "financial-settlement.NoDuplicateMakeupRule\nfinancial-settlement.PayoutEligibilityRule\n",
    );
    expect(rows).toHaveLength(2);
    expect(mapDatalogOutcome(rows, true)).toBe("counterexample");
  });

  it.each([
    "b\na\n",
    "a\na\n",
    "a\tb\n",
    "\uFEFFa\n",
    "a\r\n",
  ])("rejects malformed, duplicate, or noncanonical output", (bytes) => {
    expect(() => parseViolationCsv(bytes))
      .toThrowError(expect.objectContaining({ code: "PROVIDER_OUTPUT_INVALID" }));
  });

  it("never maps incomplete native evidence to a property result", () => {
    expect(mapDatalogOutcome([], false)).toBe("unresolved");
  });
});
