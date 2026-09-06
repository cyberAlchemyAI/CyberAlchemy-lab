import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import {
  deriveEnforcesObligations,
  loadEvfS1Bundle,
  type EvfS1Bundle,
} from "./derive.js";
import { EvfS1Error, type EvfFailureCode } from "./types.js";

const REPO_ROOT = fileURLToPath(new URL("../../../../../..", import.meta.url));

function expectEvfCode(action: () => unknown, code: EvfFailureCode): void {
  try {
    action();
  } catch (error) {
    expect(error).toBeInstanceOf(EvfS1Error);
    expect((error as EvfS1Error).code).toBe(code);
    return;
  }
  throw new Error(`expected EVF failure ${code}`);
}

describe("EVF S1 enforces obligation derivation", () => {
  it("derives one lineage-bound obligation exactly equal to O_spec", () => {
    const bundle = loadEvfS1Bundle(REPO_ROOT);
    const generated = deriveEnforcesObligations(REPO_ROOT, bundle);

    expect(generated).toHaveLength(1);
    expect(bundle.ospec.obligations).toHaveLength(1);
    expect(generated).toEqual(bundle.ospec.obligations);
    expect(generated[0]).toEqual({
      obligation_id: "evf.s1.enforces.has-key.unlock-door.v1",
      edge_id: "key-and-door.edge.has-key-rule-enforces-unlock-door",
      relationship: "enforces",
      source_node_id: "key-and-door.HasKeyRule",
      target_node_id: "key-and-door.UnlockDoor",
      predicate_id: "evf.key-door.has-key.v1",
      binding_id: "evf.key-door.binding.v1",
    });
  });

  it("rejects wrong endpoints, reversed direction, and a wrong signature", () => {
    const bundle = loadEvfS1Bundle(REPO_ROOT);

    expectEvfCode(
      () => deriveEnforcesObligations(REPO_ROOT, bundle, {
        edge: { ...bundle.binding.edge, target_node_id: "key-and-door.DoorUnlocked" },
      }),
      "EDGE_ENDPOINT_MISMATCH",
    );
    expectEvfCode(
      () => deriveEnforcesObligations(REPO_ROOT, bundle, {
        edge: {
          ...bundle.binding.edge,
          source_node_id: bundle.binding.edge.target_node_id,
          target_node_id: bundle.binding.edge.source_node_id,
        },
      }),
      "EDGE_DIRECTION_MISMATCH",
    );
    expectEvfCode(
      () => deriveEnforcesObligations(REPO_ROOT, bundle, {
        signature: {
          source_type: "Operation",
          target_type: "Rule",
          direction: "canonical",
          status: "active",
        },
      }),
      "RELATIONSHIP_SIGNATURE_MISMATCH",
    );
  });

  it("rejects stale generated-graph lineage", () => {
    const bundle = loadEvfS1Bundle(REPO_ROOT);
    const staleBundle: EvfS1Bundle = {
      ...bundle,
      binding: {
        ...bundle.binding,
        lineage_refs: {
          ...bundle.binding.lineage_refs,
          generated_graph: {
            ...bundle.binding.lineage_refs.generated_graph,
            sha256: "0".repeat(64),
          },
        },
      },
    };

    expectEvfCode(
      () => deriveEnforcesObligations(REPO_ROOT, staleBundle),
      "GENERATED_GRAPH_STALE",
    );
  });
});
