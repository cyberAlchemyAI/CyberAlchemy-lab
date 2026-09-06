import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import {
  copyFeatureFixture,
  projectFeatureDirectory,
} from "./feature-projector.js";

const featureRoot = resolve(
  dirname(fileURLToPath(import.meta.url)),
  "../../../../../../validation/poker-team/docs/features/financial-settlement",
);

describe("Financial Settlement feature projector", () => {
  it("projects the exact contained source census and preserves the known mapping red", () => {
    const projection = projectFeatureDirectory(featureRoot);
    expect(projection.census).toEqual({
      nodes: 10,
      kinds: 9,
      edges: 7,
      families: 6,
    });
    expect(projection.diagnostics).toEqual([]);
    expect(
      projection.project.nodes.every(({ source_anchor }) =>
        source_anchor?.includes(".md#"),
      ),
    ).toBe(true);
    expect(
      projection.project.edges.every(({ source_anchor }) =>
        source_anchor?.includes(".md#"),
      ),
    ).toBe(true);
    expect(
      projection.conformance_diagnostics.map(({ code, subject }) => ({
        code,
        subject,
      })),
    ).toEqual([
      {
        code: "BTE_DEV_EDGE_ENDPOINT_KIND",
        subject: "financial-settlement.edge.007.maps",
      },
    ]);
  });

  it("keeps sibling graph rows when one evidence anchor is missing", () => {
    const root = mkdtempSync(resolve(tmpdir(), "fstg-projector-anchor-"));
    copyFeatureFixture(featureRoot, root);
    const specPath = resolve(root, "SPEC.md");
    const source = readFileSync(specPath, "utf8");
    writeFileSync(
      specPath,
      source.replace(
        "interfaces.md#external-settlementapi-rest",
        "interfaces.md#missing-anchor",
      ),
    );
    const projection = projectFeatureDirectory(root);
    expect(projection.project.edges).toHaveLength(7);
    expect(projection.diagnostics).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ code: "BTE_PROJECT_ANCHOR_MISSING" }),
      ]),
    );
  });

  it("rejects evidence path escape without dropping the graph row", () => {
    const root = mkdtempSync(resolve(tmpdir(), "fstg-projector-escape-"));
    copyFeatureFixture(featureRoot, root);
    const specPath = resolve(root, "SPEC.md");
    const source = readFileSync(specPath, "utf8");
    writeFileSync(
      specPath,
      source.replace(
        "interfaces.md#external-settlementapi-rest",
        "../../../../outside.md#escape",
      ),
    );
    const projection = projectFeatureDirectory(root);
    expect(projection.project.edges).toHaveLength(7);
    expect(projection.diagnostics).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          code: "BTE_PROJECT_ANCHOR_MISSING",
          detail: "referenced file does not exist",
        }),
      ]),
    );
  });
});
