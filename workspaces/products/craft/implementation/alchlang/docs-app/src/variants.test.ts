import { describe, expect, it } from "vitest";
import { experimentVariants, variantClassName, variantFromSearch } from "./variants";

describe("Pareto experiment variants", () => {
  it("declares one stable baseline and three isolated treatments", () => {
    expect(experimentVariants).toEqual(["baseline", "compact-spacing", "progressive-reference", "task-first"]);
  });

  it("selects a declared query variant and fails closed to baseline", () => {
    expect(variantFromSearch("?variant=task-first")).toBe("task-first");
    expect(variantFromSearch("?variant=unknown")).toBe("baseline");
    expect(variantFromSearch("")).toBe("baseline");
  });

  it("produces a scoped treatment class", () => {
    expect(variantClassName("progressive-reference")).toBe("experiment-progressive-reference");
  });
});
