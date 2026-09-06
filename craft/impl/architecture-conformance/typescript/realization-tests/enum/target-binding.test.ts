import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import {
  computeTypeScriptTargetBindingSha256,
  validateTypeScriptTargetBinding,
} from "../../../realization/contracts/typescript-target-binding.js";
import { validateEnumDefinitionSnapshot } from "../../../realization/contracts/enum-definition-snapshot.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../..");
const readJson = async (path: string): Promise<Record<string, unknown>> =>
  JSON.parse(await readFile(resolve(repositoryRoot, path), "utf8")) as Record<string, unknown>;
const paths = {
  definition: "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/definition.snapshot.json",
  binding: "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/typescript.binding.json",
} as const;
const codeOf = (operation: () => unknown): string => {
  try {
    operation();
    return "NO_ERROR";
  } catch (error) {
    return String((error as { code?: string }).code);
  }
};
const withDigest = (value: Record<string, unknown>): Record<string, unknown> => {
  const copy = structuredClone(value);
  delete copy.binding_sha256;
  return { ...copy, binding_sha256: computeTypeScriptTargetBindingSha256(copy as never) };
};

describe("TypeScriptTargetBinding/v1", () => {
  it("admits one total injective safe mapping", async () => {
    const definition = validateEnumDefinitionSnapshot(await readJson(paths.definition));
    const binding = validateTypeScriptTargetBinding(await readJson(paths.binding), definition);
    expect(binding.member_names).toEqual({
      "status.paid": "Paid",
      "status.pending": "Pending",
    });
    expect(binding.authority_effect).toBe("none");
  });

  it("kills path, mapping, identifier, and provider attacks exactly", async () => {
    const definition = validateEnumDefinitionSnapshot(await readJson(paths.definition));
    const positive = await readJson(paths.binding);
    const cases: Array<readonly [string, Record<string, unknown>]> = [
      ["ARCH_TS_BINDING_PATH_INVALID", withDigest({ ...positive, module_path: "../escape.ts" })],
      ["ARCH_TS_BINDING_PATH_INVALID", withDigest({ ...positive, module_path: "/tmp/escape.ts" })],
      ["ARCH_TS_BINDING_MEMBER_MAPPING_INCOMPLETE", withDigest({
        ...positive,
        member_names: { "status.paid": "Paid" },
      })],
      ["ARCH_TS_BINDING_IDENTIFIER_DUPLICATE", withDigest({
        ...positive,
        member_names: { "status.paid": "Same", "status.pending": "Same" },
      })],
      ["ARCH_TS_BINDING_IDENTIFIER_INVALID", withDigest({
        ...positive,
        member_names: { "status.paid": "class", "status.pending": "Pending" },
      })],
      ["ARCH_TS_BINDING_PROVIDER_UNADMITTED", withDigest({
        ...positive,
        provider_module_specifier: "evil-provider",
      })],
    ];
    for (const [expected, candidate] of cases) {
      expect(codeOf(() => validateTypeScriptTargetBinding(candidate, definition))).toBe(expected);
    }
  });

  it("rejects stale binding bytes after a semantic change", async () => {
    const definition = validateEnumDefinitionSnapshot(await readJson(paths.definition));
    const positive = await readJson(paths.binding);
    expect(codeOf(() => validateTypeScriptTargetBinding({
      ...positive,
      export_name: "Changed",
    }, definition))).toBe("ARCH_TS_BINDING_DIGEST_STALE");
  });
});
