import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { beforeAll, describe, expect, it } from "vitest";

import type { ArchitectureObligationCatalogueV2 } from "../../../realization/contracts/architecture-obligation-catalogue-v2.js";
import type { ArchitectureRealizationSpec } from "../../../realization/contracts/architecture-realization-spec.js";
import { validateEnumDefinitionSnapshot } from "../../../realization/contracts/enum-definition-snapshot.js";
import { validateTypeScriptTargetBinding } from "../../../realization/contracts/typescript-target-binding.js";
import { evaluateEnumBijection } from "../../../realization/evaluator/evaluate-enum-bijection.js";
import { normalizeEnumRealization } from "../../../realization/enum/normalize-enum-realization.js";
import { observeGeneratedTypeScriptEnum } from "../../adapter/enum/index.js";
import {
  compileGeneratedEnum,
  getTypeScriptCompileExpectation,
} from "../../compiler/enum/compile-generated-enum.js";
import { emitTypeScriptEnum } from "../../generator/enum/emit-enum.js";

type JsonObject = Record<string, unknown>;

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../..");
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const canonicalize = (value: unknown): unknown => Array.isArray(value)
  ? value.map(canonicalize)
  : value !== null && typeof value === "object"
    ? Object.fromEntries(Object.entries(value as JsonObject)
      .sort(([left], [right]) => compareUtf8(left, right))
      .map(([key, child]) => [key, canonicalize(child)]))
    : value;
const catalogueDigest = (catalogue: ArchitectureObligationCatalogueV2): string => {
  const { catalogue_sha256: _digest, ...payload } = catalogue;
  return createHash("sha256").update(JSON.stringify(canonicalize(payload))).digest("hex");
};
const readJson = async <Value>(path: string): Promise<Value> =>
  JSON.parse(await readFile(resolve(repositoryRoot, path), "utf8")) as Value;

let baseline: Parameters<typeof evaluateEnumBijection>[0];
let removeMemberId: string;

beforeAll(async () => {
  const definition = validateEnumDefinitionSnapshot(await readJson(
    "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/definition.snapshot.json",
  ));
  const spec = await readJson<ArchitectureRealizationSpec>(
    "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/realization-spec.expected.json",
  );
  const catalogue = await readJson<ArchitectureObligationCatalogueV2>(
    "projects/domainspec-v2/development/architecture-realization-compiler/catalogues/order-status.member-bijection.v2.json",
  );
  const binding = validateTypeScriptTargetBinding(await readJson(
    "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/typescript.binding.json",
  ), definition);
  const fixture = await readJson<{ remove_member_id: string }>(
    "projects/domainspec-v2/impl/architecture-conformance/typescript/fixtures/enum/catalogue-member-removed.json",
  );
  removeMemberId = fixture.remove_member_id;
  const generated = emitTypeScriptEnum(normalizeEnumRealization(definition, spec), binding);
  const providerSource = await readFile(resolve(repositoryRoot, binding.provider_ref.path), "utf8");
  const compileResult = await compileGeneratedEnum({
    repositoryRoot,
    generated,
    binding,
    expectedTypeValues: definition.members.map(({ semantic_value: value }) => value),
  });
  const observation = observeGeneratedTypeScriptEnum({
    source: generated.source,
    manifest: generated.manifest,
    providerSource,
    admittedProviderSha256: binding.provider_ref.sha256,
  });
  const compileExpectation = await getTypeScriptCompileExpectation();
  baseline = {
    definition,
    catalogue,
    binding,
    sourceManifest: generated.manifest,
    compileExpectation,
    compileResult,
    observation,
  };
});

describe("Enum catalogue-to-definition denominator", () => {
  it("fails when one catalogue member disappears while binding and source remain unchanged", () => {
    const obligation = baseline.catalogue.obligations[0]!;
    const weakenedWithoutDigest = {
      ...baseline.catalogue,
      obligations: [{
        ...obligation,
        expected_payload: {
          ...obligation.expected_payload,
          members: obligation.expected_payload.members.filter(
            ({ member_id: memberId }) => memberId !== removeMemberId,
          ),
        },
      }],
    } as ArchitectureObligationCatalogueV2;
    const weakened = {
      ...weakenedWithoutDigest,
      catalogue_sha256: catalogueDigest(weakenedWithoutDigest),
    } as ArchitectureObligationCatalogueV2;
    const result = evaluateEnumBijection({ ...baseline, catalogue: weakened });
    if (result.verdict === "pass") throw new Error("CATALOGUE_JOIN_UNENFORCED");
    expect(result.findings.map(({ code }) => code)).toEqual([
      "ARCH_ENUM_CATALOGUE_DEFINITION_MISMATCH",
    ]);
  });
});
