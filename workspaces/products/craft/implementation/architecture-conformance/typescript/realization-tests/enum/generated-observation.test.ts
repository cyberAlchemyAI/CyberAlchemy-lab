import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import type { ArchitectureRealizationSpec } from "../../../realization/contracts/architecture-realization-spec.js";
import { validateEnumDefinitionSnapshot } from "../../../realization/contracts/enum-definition-snapshot.js";
import { validateTypeScriptTargetBinding } from "../../../realization/contracts/typescript-target-binding.js";
import { normalizeEnumRealization } from "../../../realization/enum/normalize-enum-realization.js";
import { observeGeneratedTypeScriptEnum } from "../../adapter/enum/index.js";
import { emitTypeScriptEnum } from "../../generator/enum/emit-enum.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../..");
const readJson = async <Value>(path: string): Promise<Value> =>
  JSON.parse(await readFile(resolve(repositoryRoot, path), "utf8")) as Value;

const inputs = async () => {
  const definition = validateEnumDefinitionSnapshot(await readJson(
    "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/definition.snapshot.json",
  ));
  const spec = await readJson<ArchitectureRealizationSpec>(
    "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/realization-spec.expected.json",
  );
  const binding = validateTypeScriptTargetBinding(await readJson(
    "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/typescript.binding.json",
  ), definition);
  const generated = emitTypeScriptEnum(normalizeEnumRealization(definition, spec), binding);
  const providerSource = await readFile(resolve(
    repositoryRoot,
    "projects/domainspec-v2/impl/architecture-conformance/typescript/runtime/enum/index.ts",
  ), "utf8");
  return { generated, providerSource, providerSha256: binding.provider_ref.sha256 } as const;
};

describe("generated TypeScript Enum observation", () => {
  it("reports only source-derived member records with exact provenance", async () => {
    const { generated, providerSource, providerSha256 } = await inputs();
    const observation = observeGeneratedTypeScriptEnum({
      source: generated.source,
      manifest: generated.manifest,
      providerSource,
      admittedProviderSha256: providerSha256,
    });

    expect(observation.facts.map(({ target_identifier, runtime_value }) =>
      [target_identifier, runtime_value])).toEqual([
      ["Paid", "paid"],
      ["Pending", "pending"],
    ]);
    expect(observation.unsupported).toEqual([]);
    expect(observation.authority_effect).toBe("none");
    expect(JSON.stringify(observation)).not.toMatch(/expectedValues|expected_values|catalogue/u);
  });

  it("rejects stale source and provider handles and fails closed on unsupported syntax", async () => {
    const { generated, providerSource, providerSha256 } = await inputs();
    expect(() => observeGeneratedTypeScriptEnum({
      source: `${generated.source}\n`,
      manifest: generated.manifest,
      providerSource,
      admittedProviderSha256: providerSha256,
    })).toThrowError(expect.objectContaining({ code: "ARCH_ENUM_OBSERVATION_SOURCE_STALE" }));
    expect(() => observeGeneratedTypeScriptEnum({
      source: generated.source,
      manifest: generated.manifest,
      providerSource: `${providerSource}\n`,
      admittedProviderSha256: providerSha256,
    })).toThrowError(expect.objectContaining({ code: "ARCH_ENUM_OBSERVATION_PROVIDER_STALE" }));
  });

  it("rejects parse diagnostics and additional public source outside the selected Enum", async () => {
    const { generated, providerSource, providerSha256 } = await inputs();
    const withSource = (source: string) => ({
      ...generated.manifest,
      source_sha256: createHash("sha256").update(source).digest("hex"),
      source_byte_length: Buffer.byteLength(source, "utf8"),
    });
    const invalid = `${generated.source}\nexport const Broken = ;\n`;
    expect(() => observeGeneratedTypeScriptEnum({
      source: invalid,
      manifest: withSource(invalid),
      providerSource,
      admittedProviderSha256: providerSha256,
    })).toThrowError(expect.objectContaining({
      code: "ARCH_ENUM_OBSERVATION_PARSE_DIAGNOSTIC",
    }));

    const secondPublicCallable = `${generated.source}\nexport const Other = () => true;\n`;
    expect(() => observeGeneratedTypeScriptEnum({
      source: secondPublicCallable,
      manifest: withSource(secondPublicCallable),
      providerSource,
      admittedProviderSha256: providerSha256,
    })).toThrowError(expect.objectContaining({
      code: "ARCH_ENUM_OBSERVATION_SOURCE_SCOPE_UNSUPPORTED",
    }));
  });
});
