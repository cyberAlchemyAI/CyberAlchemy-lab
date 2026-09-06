import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { beforeAll, describe, expect, it } from "vitest";

import {
  computeArchitectureObligationCatalogueV2Sha256,
  type ArchitectureObligationCatalogueV2,
} from "../../../realization/contracts/architecture-obligation-catalogue-v2.js";
import type { ArchitectureRealizationSpec } from "../../../realization/contracts/architecture-realization-spec.js";
import { validateEnumDefinitionSnapshot } from "../../../realization/contracts/enum-definition-snapshot.js";
import type { EnumObservation } from "../../../realization/contracts/architecture-evaluation.js";
import { validateTypeScriptTargetBinding } from "../../../realization/contracts/typescript-target-binding.js";
import { evaluateEnumBijection } from "../../../realization/evaluator/evaluate-enum-bijection.js";
import { assertEvaluatorImportBoundary } from "../../../realization/evaluator/forbidden-imports.js";
import { normalizeEnumRealization } from "../../../realization/enum/normalize-enum-realization.js";
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
let baseline: Parameters<typeof evaluateEnumBijection>[0];

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
  const generated = emitTypeScriptEnum(normalizeEnumRealization(definition, spec), binding);
  const providerPath = resolve(repositoryRoot, binding.provider_ref.path);
  const providerSource = await readFile(providerPath, "utf8");
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

const withFacts = (facts: EnumObservation["facts"]): EnumObservation => ({
  ...baseline.observation,
  facts,
  observation_sha256: "f".repeat(64),
});
const withObservedRuntime = (facts: EnumObservation["facts"]) => ({
  observation: withFacts(facts),
  compileResult: {
    ...baseline.compileResult,
    runtime_values: facts.map(({ runtime_value: runtimeValue }) => runtimeValue),
  },
});

describe("independent Enum member-bijection evaluator", () => {
  it("accounts for the one positive obligation exactly", () => {
    const result = evaluateEnumBijection(baseline);
    expect(result.verdict).toBe("pass");
    expect(result.findings).toEqual([]);
    expect(result.obligation_accounting).toEqual({ declared: 1, passed: 1, failed: 0, unaccounted: 0 });
  });

  it.each([
    ["missing", (facts: EnumObservation["facts"]) => facts.slice(1), ["ARCH_ENUM_MEMBER_MISSING"]],
    ["unexpected", (facts: EnumObservation["facts"]) => [...facts, {
      ...facts[0]!, target_identifier: "Other", runtime_value: "other",
    }], ["ARCH_ENUM_MEMBER_UNEXPECTED"]],
    ["changed", (facts: EnumObservation["facts"]) => [{ ...facts[0]!, runtime_value: "wrong" }, ...facts.slice(1)], ["ARCH_ENUM_VALUE_MISMATCH"]],
    ["duplicate", (facts: EnumObservation["facts"]) => [...facts, facts[0]!], ["ARCH_ENUM_MEMBER_DUPLICATE"]],
  ])("fails %s observations with the exact semantic code", (_name, mutate, codes) => {
    const facts = mutate(baseline.observation.facts);
    const result = evaluateEnumBijection({ ...baseline, ...withObservedRuntime(facts) });
    expect([...new Set(result.findings.map(({ code }) => code))]).toEqual(codes);
    expect(result.obligation_accounting.unaccounted).toBe(0);
  });

  it("rejects ambiguous bindings, unsupported observations, and stale handles", () => {
    const ambiguous = evaluateEnumBijection({
      ...baseline,
      binding: { ...baseline.binding, member_names: { "status.paid": "Paid", "status.pending": "Paid" } },
    });
    expect(ambiguous.findings.some(({ code }) => code === "ARCH_ENUM_BINDING_AMBIGUOUS")).toBe(true);
    const unsupported = evaluateEnumBijection({
      ...baseline,
      observation: { ...baseline.observation, unsupported: [{ code: "X", reason: "unsupported" }] },
    });
    expect(unsupported.findings.map(({ code }) => code)).toContain("ARCH_ENUM_OBSERVATION_UNSUPPORTED");
    const stale = evaluateEnumBijection({
      ...baseline,
      compileResult: { ...baseline.compileResult, source_sha256: "0".repeat(64) },
    });
    expect(stale.findings.map(({ code }) => code)).toContain("ARCH_REALIZATION_HANDLE_STALE");
  });

  it("fails stale catalogue, definition, and binding joins with exact trust diagnostics", () => {
    const staleDigest = evaluateEnumBijection({
      ...baseline,
      catalogue: { ...baseline.catalogue, catalogue_sha256: "0".repeat(64) },
    });
    expect(staleDigest.findings.map(({ code }) => code)).toEqual([
      "ARCH_ENUM_CATALOGUE_DIGEST_STALE",
    ]);

    const obligation = baseline.catalogue.obligations[0]!;
    const wrongDefinitionWithoutDigest = {
      ...baseline.catalogue,
      obligations: [{
        ...obligation,
        expected_payload: { ...obligation.expected_payload, concept_id: "candidate.wrong" },
      }],
    } as ArchitectureObligationCatalogueV2;
    const wrongDefinition = evaluateEnumBijection({
      ...baseline,
      catalogue: {
        ...wrongDefinitionWithoutDigest,
        catalogue_sha256: computeArchitectureObligationCatalogueV2Sha256(
          wrongDefinitionWithoutDigest,
        ),
      },
    });
    expect(wrongDefinition.findings.map(({ code }) => code)).toEqual([
      "ARCH_ENUM_CATALOGUE_DEFINITION_MISMATCH",
    ]);

    const wrongBinding = evaluateEnumBijection({
      ...baseline,
      binding: {
        ...baseline.binding,
        member_names: { "status.paid": "Paid" },
      },
    });
    expect(wrongBinding.findings.map(({ code }) => code)).toEqual([
      "ARCH_ENUM_CATALOGUE_BINDING_MISMATCH",
    ]);
  });

  it.each([
    ["execution", (input: typeof baseline.compileResult) => ({ ...input, exit_status: 1 as const }),
      "ARCH_ENUM_COMPILE_EXECUTION_INVALID"],
    ["tool", (input: typeof baseline.compileResult) => ({
      ...input,
      compiler: { ...input.compiler, tool_sha256: "0".repeat(64) },
    }), "ARCH_ENUM_COMPILE_TOOL_INVALID"],
    ["type witness", (input: typeof baseline.compileResult) => ({
      ...input,
      type_witness: { ...input.type_witness, passed: false },
    }), "ARCH_ENUM_COMPILE_TYPE_WITNESS_INVALID"],
    ["runtime values", (input: typeof baseline.compileResult) => ({
      ...input,
      runtime_values: ["wrong"],
    }), "ARCH_ENUM_COMPILE_RUNTIME_VALUES_INVALID"],
    ["runtime freeze", (input: typeof baseline.compileResult) => ({
      ...input,
      runtime_frozen: false,
    }), "ARCH_ENUM_COMPILE_RUNTIME_FREEZE_INVALID"],
  ])("makes corrupted %s evidence causally fail", (_name, mutate, code) => {
    const result = evaluateEnumBijection({
      ...baseline,
      compileResult: mutate(baseline.compileResult),
    });
    expect(result.findings.map(({ code: findingCode }) => findingCode)).toEqual([code]);
  });

  it("has no transitive dependency on emitters, compilers, adapters, or fixtures", async () => {
    const files = await assertEvaluatorImportBoundary(resolve(
      repositoryRoot,
      "projects/domainspec-v2/impl/architecture-conformance/realization/evaluator/evaluate-enum-bijection.ts",
    ));
    expect(files.some((path) => path.endsWith("architecture-evaluation.ts"))).toBe(true);
  });
});
