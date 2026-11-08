import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {describe, expect, it} from "vitest";

import {calculateNetSettlement} from "./calculation-v1.js";

const here = dirname(fileURLToPath(import.meta.url));

describe("TypeScript bound Calculation target", () => {
  it.each([
    [125000, 2500, 122500],
    [5000, 0, 5000],
    [0, 0, 0],
    [1000000000, 125000, 999875000],
  ])("returns the declared non-boolean value", (gross, fee, expected) => {
    const result = calculateNetSettlement({
      gross_amount_minor: gross,
      fee_amount_minor: fee,
    });
    expect(result).toBe(expected);
    expect(typeof result).toBe("number");
  });

  it("is one exported synchronous arrow over explicit inputs", async () => {
    const source = await readFile(resolve(here, "calculation-v1.ts"), "utf8");
    expect(source).toContain("export const calculateNetSettlement = (");
    expect(source).not.toMatch(/\bfunction\b/u);
    expect(source).not.toMatch(/\basync\b/u);
    expect(source).not.toMatch(/\b(?:Date|Math|process|globalThis|fetch|Promise)\b/u);
    expect(source).not.toMatch(/\b(?:import|require|new)\b/u);
  });
});
