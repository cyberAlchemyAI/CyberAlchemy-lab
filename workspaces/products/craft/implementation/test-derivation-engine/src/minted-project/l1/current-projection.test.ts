import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { deriveUnit, L1_CURRENT_PROJECTION, loadFinancialSettlementGraph } from "./derive.js";
import { L1Error } from "./types.js";

const repoRoot = fileURLToPath(new URL("../../../../../../..", import.meta.url));

describe("current financial-settlement projection", () => {
  it("derives P4 and R4 on one exact current graph handle", () => {
    const p4 = deriveUnit(repoRoot, "P4", { projection: L1_CURRENT_PROJECTION });
    const r4 = deriveUnit(repoRoot, "R4", { projection: L1_CURRENT_PROJECTION });
    expect(p4.O_gen).toEqual(p4.O_spec);
    expect(r4.O_gen).toEqual(r4.O_spec);
    expect(p4.graph_handle).toEqual(r4.graph_handle);
    expect(p4.graph_handle.graph_ref.path).toBe(L1_CURRENT_PROJECTION.graph);
    expect(p4.graph_handle.source_manifest_ref.path).toBe(L1_CURRENT_PROJECTION.sourceManifest);
  });

  it("rejects a predecessor registry digest even when candidate bytes are current", () => {
    const graph = loadFinancialSettlementGraph(repoRoot, L1_CURRENT_PROJECTION);
    const stale = {
      ...graph,
      language: {
        ...graph.language,
        relationships_digest: "82c55ea1ad031d3135c5b8a85162e44b4e85f296b54057fda0dc38131ab376a1",
      },
    };
    try {
      deriveUnit(repoRoot, "R4", { graph: stale, projection: L1_CURRENT_PROJECTION });
    } catch (error) {
      expect(error).toBeInstanceOf(L1Error);
      expect((error as L1Error).code).toBe("SOURCE_GRAPH_DIGEST_STALE");
      return;
    }
    throw new Error("expected predecessor registry rejection");
  });

  it("never returns a disk graph handle for changed in-memory graph bytes", () => {
    const graph = loadFinancialSettlementGraph(repoRoot, L1_CURRENT_PROJECTION);
    const changed = {
      ...graph,
      nodes: graph.nodes.map((node, index) =>
        index === 0 ? { ...node, body: { ...node.body, unbound_marker: true } } : node,
      ),
    };
    try {
      deriveUnit(repoRoot, "R4", { graph: changed, projection: L1_CURRENT_PROJECTION });
    } catch (error) {
      expect(error).toBeInstanceOf(L1Error);
      expect((error as L1Error).code).toBe("SOURCE_GRAPH_DIGEST_STALE");
      return;
    }
    throw new Error("expected mismatched in-memory graph rejection");
  });
});
