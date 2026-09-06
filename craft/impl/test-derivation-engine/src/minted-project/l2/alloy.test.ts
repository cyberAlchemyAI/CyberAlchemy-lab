import { describe, expect, it } from "vitest";

import {
  alloyArgv,
  mapAlloyOutcome,
  parseAlloyJson,
  typedAlloyEvidence,
} from "./alloy.js";

describe("EVF L2 Alloy CLI adapter", () => {
  const expected = {
    source: "check NoViolation for exactly 5 Node",
    scopes: ["exactly 5 Node"],
    solver: "sat4j" as const,
  };
  const command = {
    bitwidth: 4,
    expects: -1,
    maxprefix: -1,
    maxseq: -1,
    minprefix: -1,
    name: "NoViolation",
    overall: -1,
    scopes: expected.scopes,
    source: expected.source,
    type: "check",
  };
  const receipt = (entry: Record<string, unknown>) => JSON.stringify({
    commands: { NoViolation: { ...command, ...entry } },
    solver: "sat4j",
    timestamp: 1787312726984,
  });
  const solution = {
    duration: 47,
    incremental: true,
    instances: [{ values: { "0": {}, "N0$0": {} } }],
    localtime: "2026-08-21T11:45:27.157159082",
    timezone: "UTC",
    utctime: 1787312727156,
  };
  const solutionFile = JSON.stringify({
    ...solution,
    instances: [{ messages: [], skolems: {}, state: 0, values: { "0": {}, "N0$0": {} } }],
    loopstate: -1,
    sigs: {},
  });
  it("builds the exact Sat4j JSON check command", () => {
    expect(alloyArgv("/java", "/alloy.jar", "/output", "/model.als")).toEqual([
      "/java", "-jar", "/alloy.jar", "exec", "-q", "-f", "-s", "sat4j",
      "-t", "json", "-o", "/output", "-c", "NoViolation", "/model.als",
    ]);
  });

  it("maps SAT only with counterexample evidence", () => {
    const result = parseAlloyJson(
      receipt({ solution: [solution] }),
      [{ name: "NoViolation-solution-0.json", bytes: solutionFile }],
      expected,
    );
    expect(mapAlloyOutcome(result.outcome)).toBe("counterexample");
    expect(typedAlloyEvidence(result)).toMatchObject({
      present: true,
      command_label: "NoViolation",
    });
  });

  it("maps UNSAT only within the exact recorded scope", () => {
    const result = parseAlloyJson(receipt({}), [], expected);
    expect(mapAlloyOutcome(result.outcome)).toBe("no-counterexample");
    expect(typedAlloyEvidence(result)).toEqual({
      present: false,
      command_label: "NoViolation",
      reason: "unsat",
    });
  });

  it("maps unknown to unresolved with typed absence", () => {
    const result = parseAlloyJson(receipt({ status: "unknown" }), [], expected);
    expect(mapAlloyOutcome(result.outcome)).toBe("unresolved");
    expect(typedAlloyEvidence(result)).toEqual({
      present: false,
      command_label: "NoViolation",
      reason: "unknown",
    });
  });

  it.each([
    ["{}", []],
    [JSON.stringify({ commands: { Wrong: command }, solver: "sat4j" }), []],
    [JSON.stringify({ commands: { NoViolation: command }, solver: "other" }), []],
    [receipt({ source: "check NoViolation for 6 Node" }), []],
    [receipt({ solution: [] }), []],
    [
      receipt({ solution: [{ ...solution, instances: [] }] }),
      [{ name: "NoViolation-solution-0.json", bytes: JSON.stringify({ ...solution, instances: [] }) }],
    ],
    [receipt({ solution: [solution] }), []],
    [receipt({}), [{ name: "NoViolation-solution-0.json", bytes: solutionFile }]],
    [receipt({ solution: [solution] }), [{ name: "wrong.json", bytes: solutionFile }]],
    ["not-json", []],
  ] as const)("rejects malformed or contradictory Alloy output", (bytes, files) => {
    expect(() => parseAlloyJson(bytes, files, expected))
      .toThrowError(expect.objectContaining({ code: "PROVIDER_OUTPUT_INVALID" }));
  });
});
