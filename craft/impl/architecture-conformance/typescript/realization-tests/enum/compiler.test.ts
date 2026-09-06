import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import type { ArchitectureRealizationSpec } from "../../../realization/contracts/architecture-realization-spec.js";
import { validateEnumDefinitionSnapshot } from "../../../realization/contracts/enum-definition-snapshot.js";
import { validateTypeScriptTargetBinding } from "../../../realization/contracts/typescript-target-binding.js";
import { normalizeEnumRealization } from "../../../realization/enum/normalize-enum-realization.js";
import { compileGeneratedEnum } from "../../compiler/enum/compile-generated-enum.js";
import { emitTypeScriptEnum } from "../../generator/enum/emit-enum.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../..");
const readJson = async <Value>(path: string): Promise<Value> =>
  JSON.parse(await readFile(resolve(repositoryRoot, path), "utf8")) as Value;
const build = async () => {
  const definition = validateEnumDefinitionSnapshot(await readJson(
    "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/definition.snapshot.json",
  ));
  const spec = await readJson<ArchitectureRealizationSpec>(
    "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/realization-spec.expected.json",
  );
  const binding = validateTypeScriptTargetBinding(await readJson(
    "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/typescript.binding.json",
  ), definition);
  return {
    definition,
    binding,
    generated: emitTypeScriptEnum(normalizeEnumRealization(definition, spec), binding),
  } as const;
};

describe("isolated generated Enum compiler", () => {
  it("proves exact literal union, runtime values, and owned runtime freeze", async () => {
    const { definition, binding, generated } = await build();
    const result = await compileGeneratedEnum({
      repositoryRoot,
      generated,
      binding,
      expectedTypeValues: definition.members.map(({ semantic_value: value }) => value),
    });
    expect(result.exit_status).toBe(0);
    expect(result.diagnostics).toEqual([]);
    expect(result.type_witness).toMatchObject({
      mode: "definition-exact",
      expected_union: ["paid", "pending"],
      passed: true,
    });
    expect(result.runtime_values).toEqual(["paid", "pending"]);
    expect(result.runtime_frozen).toBe(true);
    expect(result.compiler).toMatchObject({
      name: "typescript",
      version: expect.stringMatching(/^5\./u),
      tool_sha256: expect.stringMatching(/^[a-f0-9]{64}$/u),
      config_sha256: expect.stringMatching(/^[a-f0-9]{64}$/u),
    });
    expect(result.workspace).toMatchObject({ isolated: true, symlinks: false, cleaned: true });
  });

  it("fails before compilation when provider or source bytes are stale", async () => {
    const { binding, generated } = await build();
    await expect(compileGeneratedEnum({
      repositoryRoot,
      generated: {
        ...generated,
        source: `${generated.source}\n`,
      },
      binding,
    })).rejects.toMatchObject({ code: "ARCH_ENUM_COMPILE_SOURCE_STALE" });
    await expect(compileGeneratedEnum({
      repositoryRoot,
      generated,
      binding: {
        ...binding,
        provider_ref: { ...binding.provider_ref, sha256: "0".repeat(64) },
      },
    })).rejects.toMatchObject({ code: "ARCH_ENUM_COMPILE_PROVIDER_STALE" });
  });
});
