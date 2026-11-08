import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import type { ArchitectureRealizationSpec } from "../../../realization/contracts/architecture-realization-spec.js";
import {
  computeEnumRealizationIrSha256,
  normalizeEnumRealization,
} from "../../../realization/enum/normalize-enum-realization.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../..");
const readJson = async <Value>(path: string): Promise<Value> =>
  JSON.parse(await readFile(resolve(repositoryRoot, path), "utf8")) as Value;

describe("EnumRealizationIR/v1", () => {
  it("exact-joins the definition and ontology-derived spec into portable IR", async () => {
    const definition = await readJson<Record<string, unknown>>(
      "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/definition.snapshot.json",
    );
    definition.members = [...definition.members as unknown[]].reverse();
    const spec = await readJson<ArchitectureRealizationSpec>(
      "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/realization-spec.expected.json",
    );
    const ir = normalizeEnumRealization(definition, spec);
    expect(ir.members).toEqual([
      { member_id: "status.paid", semantic_value: "paid" },
      { member_id: "status.pending", semantic_value: "pending" },
    ]);
    const { ir_sha256: _, ...withoutDigest } = ir;
    expect(ir.ir_sha256).toBe(computeEnumRealizationIrSha256(withoutDigest));
    expect(ir).not.toHaveProperty("module_path");
    expect(ir).not.toHaveProperty("export_name");
    expect(ir.members.every((member) => Object.keys(member).length === 2)).toBe(true);
  });

  it("rejects a stale meta-type or composition contract", async () => {
    const definition = await readJson<Record<string, unknown>>(
      "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/definition.snapshot.json",
    );
    const spec = await readJson<ArchitectureRealizationSpec>(
      "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/realization-spec.expected.json",
    );
    expect(() => normalizeEnumRealization(definition, {
      ...spec,
      definition_type_ref: "DS-UNKNOWN",
    })).toThrowError(expect.objectContaining({ code: "ARCH_ENUM_IR_REALIZATION_SPEC_INVALID" }));
  });
});
