import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import type { ArchitectureRealizationSpec } from "../../../realization/contracts/architecture-realization-spec.js";
import { validateEnumDefinitionSnapshot } from "../../../realization/contracts/enum-definition-snapshot.js";
import { validateTypeScriptTargetBinding } from "../../../realization/contracts/typescript-target-binding.js";
import { normalizeEnumRealization } from "../../../realization/enum/normalize-enum-realization.js";
import { emitTypeScriptEnum } from "../../generator/enum/emit-enum.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../..");
const readJson = async <Value>(path: string): Promise<Value> =>
  JSON.parse(await readFile(resolve(repositoryRoot, path), "utf8")) as Value;
const buildInputs = async () => {
  const definition = validateEnumDefinitionSnapshot(await readJson(
    "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/definition.snapshot.json",
  ));
  const spec = await readJson<ArchitectureRealizationSpec>(
    "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/realization-spec.expected.json",
  );
  const binding = validateTypeScriptTargetBinding(await readJson(
    "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/typescript.binding.json",
  ), definition);
  return { ir: normalizeEnumRealization(definition, spec), binding } as const;
};

describe("owned const-object TypeScript emitter", () => {
  it("emits, reparses, and repeats exact safe source bytes", async () => {
    const { ir, binding } = await buildInputs();
    const first = emitTypeScriptEnum(ir, binding);
    const second = emitTypeScriptEnum(ir, binding);
    expect(first).toEqual(second);
    expect(first.source).toContain("defineEnum({");
    expect(first.source).toContain("Paid: \"paid\"");
    expect(first.source).toContain("Pending: \"pending\"");
    expect(first.source).toContain("EnumValue<typeof OrderStatus>");
    expect(first.source).not.toMatch(/\benum\s+OrderStatus\b/u);
    expect(first.source).not.toMatch(/catalogue|expected_payload|expectedValues/u);
    expect(first.manifest.source_byte_length).toBe(Buffer.byteLength(first.source));
  });

  it("blocks hostile names, paths, providers, and semantic control characters", async () => {
    const { ir, binding } = await buildInputs();
    expect(() => emitTypeScriptEnum(ir, {
      ...binding,
      member_names: { ...binding.member_names, "status.paid": "__proto__" },
    })).toThrowError(expect.objectContaining({ code: "ARCH_ENUM_EMITTER_IDENTIFIER_INVALID" }));
    expect(() => emitTypeScriptEnum(ir, {
      ...binding,
      module_path: "../escape.ts",
    })).toThrowError(expect.objectContaining({ code: "ARCH_ENUM_EMITTER_PATH_UNSAFE" }));
    expect(() => emitTypeScriptEnum(ir, {
      ...binding,
      provider_module_specifier: "evil-provider",
    })).toThrowError(expect.objectContaining({ code: "ARCH_ENUM_EMITTER_PATH_UNSAFE" }));
    expect(() => emitTypeScriptEnum({
      ...ir,
      members: [{ ...ir.members[0]!, semantic_value: "paid\n); attack();" }, ir.members[1]!],
    }, binding)).toThrowError(expect.objectContaining({ code: "ARCH_ENUM_EMITTER_VALUE_UNSAFE" }));
  });
});
