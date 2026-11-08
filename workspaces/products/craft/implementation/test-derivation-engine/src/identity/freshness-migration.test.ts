import { describe, expect, it } from "vitest";
import { obligationKey } from "../keys/index.js";
import type { ConceptGraph } from "../ir/types.js";
import { derive } from "../rules/index.js";
import { allocateIds, detectIdDrift, emptyIdMap } from "./human-id.js";

describe("historical obligation id-map migration", () => {
  it("keeps a legacy key as retired history and never promotes its id to a current derivation", () => {
    const graph: ConceptGraph = { nodes: [{ id: "calc#1", source_anchor: "calc#1", type: "Calculation",
      fields: { id: "C1", formula: "sum(records.profit)" } }], edges: [] };
    const current = derive(graph);
    expect(current).toHaveLength(1);
    const old = { ...current[0]!, obligation_key: obligationKey(current[0]!.source_anchor,
      current[0]!.rule_type, current[0]!.canonical_params) };
    expect(old.obligation_key).not.toBe(current[0]!.obligation_key);
    const committed = allocateIds([old], emptyIdMap("fixture")).map;
    const drift = detectIdDrift(current, committed);
    expect(drift.ok).toBe(false);
    expect(drift.unmapped).toEqual([current[0]!.obligation_key]);
    expect(drift.dangling).toEqual([committed.entries[0]!.id]);

    const migration = allocateIds(current, committed);
    expect(migration.tombstoned).toEqual([committed.entries[0]!.id]);
    expect(migration.map.tombstones).toContainEqual({ id: committed.entries[0]!.id, retired_key: old.obligation_key });
    expect(migration.idByKey.get(current[0]!.obligation_key)).not.toBe(committed.entries[0]!.id);
    expect(migration.map.entries.some((entry) => entry.key === old.obligation_key)).toBe(false);
  });
});
