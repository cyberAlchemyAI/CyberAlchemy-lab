import { describe, expect, it } from "vitest";

import { runCompleteDevelopmentBte } from "./development-pipeline.js";

describe("complete BTE development pipeline", () => {
  it("runs all backend kinds, relationships, catalogues, and consumers in one go", () => {
    const run = runCompleteDevelopmentBte();
    expect(run.summary).toEqual(
      expect.objectContaining({
        kind_count: 13,
        relationship_count: 17,
        catalogue_count: 6,
        coverage_count: 91,
        consumer_count: 2,
        result: "pass",
        admission: "development-only",
      }),
    );
  });

  it("is byte-stable across two complete invocations", () => {
    expect(runCompleteDevelopmentBte().summaryBytes).toBe(
      runCompleteDevelopmentBte().summaryBytes,
    );
  });
});
