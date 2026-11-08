import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import type { ArchitectureObligationCatalogueV2 } from "../../../realization/contracts/architecture-obligation-catalogue-v2.js";
import type { ArchitectureRealizationSpec } from "../../../realization/contracts/architecture-realization-spec.js";
import { validateEnumDefinitionSnapshot } from "../../../realization/contracts/enum-definition-snapshot.js";
import { validateTypeScriptTargetBinding } from "../../../realization/contracts/typescript-target-binding.js";
import { evaluateEnumBijection } from "../../../realization/evaluator/evaluate-enum-bijection.js";
import { normalizeEnumRealization } from "../../../realization/enum/normalize-enum-realization.js";
import { removeEnumMember } from "../../../realization/mutation/remove-enum-member.js";
import { observeGeneratedTypeScriptEnum } from "../../adapter/enum/index.js";
import {
  compileGeneratedEnum,
  getTypeScriptCompileExpectation,
} from "../../compiler/enum/compile-generated-enum.js";
import { emitTypeScriptEnum } from "../../generator/enum/emit-enum.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../..");
const readJson = async <Value>(path: string): Promise<Value> =>
  JSON.parse(await readFile(resolve(repositoryRoot, path), "utf8")) as Value;

describe("causal Enum member-removal mutation", () => {
  it("removes only Paid, stays compile-green, and dies on the exact obligation", async () => {
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
    const parent = emitTypeScriptEnum(normalizeEnumRealization(definition, spec), binding);
    const { child, mutation } = removeEnumMember(parent, binding, "status.paid");
    expect(mutation.delta).toMatchObject({
      operation: "remove-enum-member",
      member_id: "status.paid",
      target_identifier: "Paid",
      deleted_nodes: 1,
      inserted_nodes: 0,
    });
    expect(child.source).not.toContain("Paid: \"paid\"");
    expect(child.source).toContain("Pending: \"pending\"");

    const compileResult = await compileGeneratedEnum({ repositoryRoot, generated: child, binding });
    expect(compileResult.exit_status).toBe(0);
    expect(compileResult.type_witness.mode).toBe("compile-only");
    const providerSource = await readFile(resolve(repositoryRoot, binding.provider_ref.path), "utf8");
    const observation = observeGeneratedTypeScriptEnum({
      source: child.source,
      manifest: child.manifest,
      providerSource,
      admittedProviderSha256: binding.provider_ref.sha256,
    });
    const evaluation = evaluateEnumBijection({
      definition,
      catalogue,
      binding,
      sourceManifest: child.manifest,
      compileExpectation: await getTypeScriptCompileExpectation(),
      compileResult,
      observation,
    });
    expect(evaluation.findings).toEqual([expect.objectContaining({
      code: "ARCH_ENUM_MEMBER_MISSING",
      member_id: "status.paid",
    })]);
  });

  it("blocks missing and multiply matched mutation targets", async () => {
    const definition = validateEnumDefinitionSnapshot(await readJson(
      "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/definition.snapshot.json",
    ));
    const spec = await readJson<ArchitectureRealizationSpec>(
      "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/realization-spec.expected.json",
    );
    const binding = validateTypeScriptTargetBinding(await readJson(
      "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/typescript.binding.json",
    ), definition);
    const parent = emitTypeScriptEnum(normalizeEnumRealization(definition, spec), binding);
    expect(() => removeEnumMember(parent, binding, "status.unknown"))
      .toThrowError(expect.objectContaining({ code: "ARCH_ENUM_MUTATION_BINDING_MISSING" }));
    const duplicateSource = parent.source.replace(
      "Paid: \"paid\"",
      "Paid: \"paid\", Paid: \"paid-again\"",
    );
    const duplicate = {
      ...parent,
      source: duplicateSource,
      manifest: {
        ...parent.manifest,
        source_sha256: createHash("sha256").update(duplicateSource).digest("hex"),
        source_byte_length: Buffer.byteLength(duplicateSource),
      },
    };
    expect(() => removeEnumMember(duplicate, binding, "status.paid"))
      .toThrowError(expect.objectContaining({ code: "ARCH_ENUM_MUTATION_TARGET_CARDINALITY" }));
  });
});
