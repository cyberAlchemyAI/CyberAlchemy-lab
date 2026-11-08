import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import { deriveUnit, L1_PATHS } from "./derive.js";
import { exactRef, repositoryRoot } from "./exact-ref.js";
import { buildUnitReceipt, verifyUnitReceipt } from "./receipt.js";
import { L1Error, type UnitReceipt } from "./types.js";
import { assertExactTargetList, schemaValidate } from "./verify-p4.js";

const repoRoot = repositoryRoot();

function writeJson(path: string, value: unknown): void {
  writeFileSync(path, `${JSON.stringify(value)}\n`, "utf8");
}

function receipt(): UnitReceipt {
  const derivation = deriveUnit(repoRoot, "P4");
  return buildUnitReceipt({
    unit: "P4",
    graphHandle: derivation.graph_handle,
    evidenceRefs: [
      exactRef(repoRoot, L1_PATHS.p4Semantic),
      exactRef(repoRoot, L1_PATHS.p4Obligation),
      exactRef(repoRoot, L1_PATHS.p4Runtime),
      exactRef(repoRoot, L1_PATHS.p4Fixture),
      exactRef(repoRoot, L1_PATHS.p4Binding),
    ],
    acceptanceVector: { mutants_required: 16, mutants_killed: 16, writes: 1, events: 1 },
  });
}

describe("EVF L1 P4 receipt", () => {
  it("replays a bounded non-admitting receipt", () => {
    const candidate = receipt();
    expect(() => verifyUnitReceipt(repoRoot, candidate)).not.toThrow();
    expect(candidate.release_admission).toBe("not-granted");
    expect(candidate.authority_effect).toBe("none");
  });

  it("rejects a digest-preserving claim mutation", () => {
    const candidate = structuredClone(receipt()) as UnitReceipt & { claim_ceiling: string };
    candidate.claim_ceiling = "full-financial-settlement-correctness";
    try {
      verifyUnitReceipt(repoRoot, candidate);
      throw new Error("tampered receipt survived");
    } catch (error) {
      expect(error).toBeInstanceOf(L1Error);
      expect((error as L1Error).code).toBe("CLAIM_INFLATION");
    }
  });

  it("rejects an omitted verifier target", () => {
    expect(() => assertExactTargetList(["a"], ["a", "b"])).toThrowError(
      expect.objectContaining({ code: "VERIFIER_TARGET_OMITTED" }),
    );
  });

  it("validates the exact P4 fixture against its local schema", () => {
    const fixtureRoot =
      "projects/domainspec-v2/development/evolvable-validation-framework/fixtures/SWU-GCP-002-P4";
    expect(() => schemaValidate(
      repoRoot,
      `${fixtureRoot}/financial-settlement-p4-input.v1.schema.json`,
      `${fixtureRoot}/financial-settlement-p4-input.v1.json`,
    )).not.toThrow();
  });

  it("maps an $id-scoped relative ref to the exact local schema", () => {
    const tempRoot = mkdtempSync(join(tmpdir(), "evf-p4-schema-"));
    try {
      mkdirSync(join(tempRoot, "semantic-source"));
      mkdirSync(join(tempRoot, "contracts"));
      writeJson(join(tempRoot, "semantic-source", "rule.schema.json"), {
        $schema: "https://json-schema.org/draft/2020-12/schema",
        $id: "https://example.invalid/evf/rule/v1",
        $ref: "../contracts/obligation.schema.json#/$defs/obligation",
      });
      writeJson(join(tempRoot, "contracts", "obligation.schema.json"), {
        $schema: "https://json-schema.org/draft/2020-12/schema",
        $id: "https://example.invalid/evf/obligation/v1",
        $defs: {
          obligation: {
            type: "object",
            required: ["kind"],
            properties: { kind: { const: "p4" } },
            additionalProperties: false,
          },
        },
      });
      writeJson(join(tempRoot, "document.json"), { kind: "p4" });
      expect(() => schemaValidate(tempRoot, "semantic-source/rule.schema.json", "document.json")).not.toThrow();
    } finally {
      rmSync(tempRoot, { recursive: true, force: true });
    }
  });

  it("fails closed before an unregistered remote schema can be fetched", () => {
    const tempRoot = mkdtempSync(join(tmpdir(), "evf-p4-schema-"));
    try {
      writeJson(join(tempRoot, "rule.schema.json"), {
        $schema: "https://json-schema.org/draft/2020-12/schema",
        $id: "https://example.invalid/evf/rule/v1",
        $ref: "https://example.invalid/unregistered.schema.json",
      });
      writeJson(join(tempRoot, "document.json"), {});
      expect(() => schemaValidate(tempRoot, "rule.schema.json", "document.json")).toThrowError(
        expect.objectContaining({
          code: "TARGET_BASELINE_DRIFT",
          message: expect.stringContaining("unregistered schema retrieval forbidden"),
        }),
      );
    } finally {
      rmSync(tempRoot, { recursive: true, force: true });
    }
  });
});
