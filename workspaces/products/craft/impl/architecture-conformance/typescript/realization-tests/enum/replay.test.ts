import { createHash } from "node:crypto";
import { mkdtemp, readFile, rm, unlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import type { ArchitectureObligationCatalogueV2 } from "../../../realization/contracts/architecture-obligation-catalogue-v2.js";
import type { ArchitectureRealizationSpec } from "../../../realization/contracts/architecture-realization-spec.js";
import { validateEnumDefinitionSnapshot } from "../../../realization/contracts/enum-definition-snapshot.js";
import type { ReplayRawIndex } from "../../../realization/contracts/replay-result.js";
import { validateTypeScriptTargetBinding } from "../../../realization/contracts/typescript-target-binding.js";
import { evaluateEnumBijection } from "../../../realization/evaluator/evaluate-enum-bijection.js";
import { normalizeEnumRealization } from "../../../realization/enum/normalize-enum-realization.js";
import { removeEnumMember } from "../../../realization/mutation/remove-enum-member.js";
import { replayEnumProof } from "../../../realization/replay/replay-enum-proof.js";
import { createReplayEnvironment } from "../../../realization/replay/replay-environment.js";
import { observeGeneratedTypeScriptEnum } from "../../adapter/enum/index.js";
import {
  compileGeneratedEnum,
  getTypeScriptCompileExpectation,
} from "../../compiler/enum/compile-generated-enum.js";
import { emitTypeScriptEnum } from "../../generator/enum/emit-enum.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../..");
const sha256 = (value: string): string => createHash("sha256").update(value).digest("hex");
const digestObject = (value: unknown): string => sha256(JSON.stringify(value));
const sources = {
  ontology: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/semantic-slices/legacy-whole-file-snapshots/enum-v1/ontology.json",
  base_profile: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/semantic-slices/legacy-whole-file-snapshots/enum-v1/base-domain.profile.json",
  typescript_profile: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/semantic-slices/legacy-whole-file-snapshots/enum-v1/typescript-strict.profile.json",
  definition: "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/definition.snapshot.json",
  realization_spec: "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/realization-spec.expected.json",
  catalogue: "projects/domainspec-v2/development/architecture-realization-compiler/catalogues/order-status.member-bijection.v2.json",
  binding: "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/typescript.binding.json",
  provider: "projects/domainspec-v2/impl/architecture-conformance/typescript/runtime/enum/index.ts",
} as const;

const prepare = async () => {
  const rawRoot = await mkdtemp(join(tmpdir(), "domainspec-enum-replay-raw-"));
  const bytes = Object.fromEntries(await Promise.all(Object.entries(sources).map(async ([name, path]) => {
    const value = await readFile(resolve(repositoryRoot, path), "utf8");
    await writeFile(resolve(rawRoot, `${name}.raw`), value, { flag: "wx" });
    return [name, value] as const;
  }))) as Record<keyof typeof sources, string>;
  const definition = validateEnumDefinitionSnapshot(JSON.parse(bytes.definition));
  const spec = JSON.parse(bytes.realization_spec) as ArchitectureRealizationSpec;
  const binding = validateTypeScriptTargetBinding(JSON.parse(bytes.binding), definition);
  const catalogue = JSON.parse(bytes.catalogue) as ArchitectureObligationCatalogueV2;
  const generated = emitTypeScriptEnum(normalizeEnumRealization(definition, spec), binding);
  const compileExpectation = await getTypeScriptCompileExpectation();
  const compilePositive = await compileGeneratedEnum({
    repositoryRoot, generated, binding,
    expectedTypeValues: definition.members.map(({ semantic_value: value }) => value),
  });
  const observationPositive = observeGeneratedTypeScriptEnum({
    source: generated.source, manifest: generated.manifest,
    providerSource: bytes.provider, admittedProviderSha256: binding.provider_ref.sha256,
  });
  const evaluationPositive = evaluateEnumBijection({
    definition,
    catalogue, binding, sourceManifest: generated.manifest,
    compileExpectation,
    compileResult: compilePositive, observation: observationPositive,
  });
  const mutation = removeEnumMember(generated, binding, "status.paid");
  const compileMutation = await compileGeneratedEnum({
    repositoryRoot, generated: mutation.child, binding,
  });
  const observationMutation = observeGeneratedTypeScriptEnum({
    source: mutation.child.source, manifest: mutation.child.manifest,
    providerSource: bytes.provider, admittedProviderSha256: binding.provider_ref.sha256,
  });
  const evaluationMutation = evaluateEnumBijection({
    definition,
    catalogue, binding, sourceManifest: mutation.child.manifest,
    compileExpectation,
    compileResult: compileMutation, observation: observationMutation,
  });
  const inputs = Object.fromEntries(Object.keys(sources).map((name) => [name, {
    path: `${name}.raw`,
    sha256: sha256(bytes[name as keyof typeof sources]),
  }])) as ReplayRawIndex["inputs"];
  const rawIndex: ReplayRawIndex = {
    schema_version: "ReplayRawIndex/v2",
    inputs,
    environment: await createReplayEnvironment(repositoryRoot),
    expected: {
      positive_evaluation_sha256: digestObject(evaluationPositive),
      mutation_sha256: digestObject(mutation.mutation),
      mutation_evaluation_sha256: digestObject(evaluationMutation),
    },
    authority_effect: "none",
  };
  return { rawRoot, rawIndex } as const;
};

describe("separate-process Enum proof replay", () => {
  it("reconstructs source, compilation, observation, evaluation, and mutation in another process", async () => {
    const { rawRoot, rawIndex } = await prepare();
    try {
      const result = await replayEnumProof({ repositoryRoot, rawRoot, rawIndex });
      expect(result.status).toBe("pass");
      expect(result.child_pid).not.toBe(process.pid);
      expect(result.workspace_id).toMatch(/^domainspec-enum-replay-/u);
      expect(result.diagnostics).toEqual([]);
      expect(result.claims).toEqual({
        semantic_recomposition: "pass",
        process_isolation: "pass",
        byte_identity: "not-claimed",
      });
    } finally {
      await rm(rawRoot, { recursive: true, force: true });
    }
  }, 40_000);

  it("blocks missing, tampered, and receipt-only raw input", async () => {
    const missing = await prepare();
    try {
      await unlink(resolve(missing.rawRoot, missing.rawIndex.inputs.definition.path));
      await expect(replayEnumProof({ repositoryRoot, ...missing }))
        .rejects.toMatchObject({ code: "ARCH_REPLAY_RAW_INPUT_MISSING" });
    } finally {
      await rm(missing.rawRoot, { recursive: true, force: true });
    }
    const tampered = await prepare();
    try {
      await writeFile(resolve(tampered.rawRoot, tampered.rawIndex.inputs.binding.path), "{}\n");
      await expect(replayEnumProof({ repositoryRoot, ...tampered }))
        .rejects.toMatchObject({ code: "ARCH_REPLAY_RAW_INPUT_TAMPERED" });
      const receiptOnly = {
        ...tampered.rawIndex,
        inputs: { ...tampered.rawIndex.inputs, evaluation_receipt: tampered.rawIndex.inputs.catalogue },
      } as unknown as ReplayRawIndex;
      await expect(replayEnumProof({ repositoryRoot, rawRoot: tampered.rawRoot, rawIndex: receiptOnly }))
        .rejects.toMatchObject({ code: "ARCH_REPLAY_RECEIPT_ONLY_FORBIDDEN" });
    } finally {
      await rm(tampered.rawRoot, { recursive: true, force: true });
    }
  }, 20_000);

  it.each(["generator", "adapter", "evaluator", "compiler", "mutator"] as const)(
    "blocks changed %s code under replay",
    async (component) => {
      const prepared = await prepare();
      try {
        const rawIndex: ReplayRawIndex = {
          ...prepared.rawIndex,
          environment: {
            ...prepared.rawIndex.environment,
            components: {
              ...prepared.rawIndex.environment.components,
              [component]: {
                ...prepared.rawIndex.environment.components[component],
                sha256: "0".repeat(64),
              },
            },
          },
        };
        await expect(
          replayEnumProof({
            repositoryRoot,
            rawRoot: prepared.rawRoot,
            rawIndex,
          }),
        ).rejects.toMatchObject({ code: "ARCH_REPLAY_COMPONENT_TAMPERED" });
      } finally {
        await rm(prepared.rawRoot, { recursive: true, force: true });
      }
    },
    20_000,
  );

  it("blocks changed toolchain and config pins", async () => {
    const prepared = await prepare();
    try {
      const toolchainTampered: ReplayRawIndex = {
        ...prepared.rawIndex,
        environment: {
          ...prepared.rawIndex.environment,
          toolchain: {
            ...prepared.rawIndex.environment.toolchain,
            node: {
              ...prepared.rawIndex.environment.toolchain.node,
              sha256: "0".repeat(64),
            },
          },
        },
      };
      await expect(
        replayEnumProof({
          repositoryRoot,
          rawRoot: prepared.rawRoot,
          rawIndex: toolchainTampered,
        }),
      ).rejects.toMatchObject({ code: "ARCH_REPLAY_TOOLCHAIN_TAMPERED" });

      const configTampered: ReplayRawIndex = {
        ...prepared.rawIndex,
        environment: {
          ...prepared.rawIndex.environment,
          config: {
            ...prepared.rawIndex.environment.config,
            compiler_sha256: "0".repeat(64),
          },
        },
      };
      await expect(
        replayEnumProof({
          repositoryRoot,
          rawRoot: prepared.rawRoot,
          rawIndex: configTampered,
        }),
      ).rejects.toMatchObject({ code: "ARCH_REPLAY_CONFIG_TAMPERED" });
    } finally {
      await rm(prepared.rawRoot, { recursive: true, force: true });
    }
  }, 20_000);
});
