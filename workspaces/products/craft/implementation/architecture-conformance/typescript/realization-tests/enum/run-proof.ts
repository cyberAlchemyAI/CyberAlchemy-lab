import { createHash } from "node:crypto";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import type { ArchitectureObligationCatalogueV2 } from "../../../realization/contracts/architecture-obligation-catalogue-v2.js";
import type { ArchitectureProofReceipt } from "../../../realization/contracts/architecture-proof-receipt.js";
import type { ArchitectureRealizationCase } from "../../../realization/contracts/architecture-realization-case.js";
import type { ArchitectureRealizationSpec } from "../../../realization/contracts/architecture-realization-spec.js";
import type { ReplayRawIndex } from "../../../realization/contracts/replay-result.js";
import { advanceProofState, createProofState } from "../../../realization/evidence/proof-state.js";
import { writeProofRun } from "../../../realization/evidence/write-proof-run.js";
import { replayEnumProof } from "../../../realization/replay/replay-enum-proof.js";
import { createReplayEnvironment } from "../../../realization/replay/replay-environment.js";
import { createEnumTypeScriptRegistrationV2 } from "../../../realizations/enum/typescript/owned-const-object-v1/registration.js";
import { typescriptCompilerConfigSha256 } from "../../compiler/enum/compile-generated-enum.js";

const here = dirname(fileURLToPath(import.meta.url));
export const repositoryRoot = resolve(here, "../../../../../../..");
const sha256 = (value: string): string => createHash("sha256").update(value).digest("hex");
const digestObject = (value: unknown): string => sha256(JSON.stringify(value));
const json = (value: unknown): string => `${JSON.stringify(value, null, 2)}\n`;
export const enumOrderStatusRawPaths = {
  ontology: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/semantic-slices/legacy-whole-file-snapshots/enum-v1/ontology.json",
  base_profile: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/semantic-slices/legacy-whole-file-snapshots/enum-v1/base-domain.profile.json",
  typescript_profile: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/semantic-slices/legacy-whole-file-snapshots/enum-v1/typescript-strict.profile.json",
  definition: "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/definition.snapshot.json",
  realization_spec: "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/realization-spec.expected.json",
  catalogue: "projects/domainspec-v2/development/architecture-realization-compiler/catalogues/order-status.member-bijection.v2.json",
  catalogue_predecessor: "projects/domainspec-v2/development/architecture-realization-compiler/catalogues/order-status.member-bijection.v1.json",
  binding: "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/typescript.binding.json",
  provider: "projects/domainspec-v2/impl/architecture-conformance/typescript/runtime/enum/index.ts",
} as const;

export type EnumOrderStatusRawInputs = Readonly<Record<keyof typeof enumOrderStatusRawPaths, string>>;

export const buildOrderStatusProof = async (rawInputs?: EnumOrderStatusRawInputs) => {
  const bytes = rawInputs ?? Object.fromEntries(await Promise.all(
    Object.entries(enumOrderStatusRawPaths).map(
      async ([name, path]) => [name, await readFile(resolve(repositoryRoot, path), "utf8")] as const,
    ),
  )) as EnumOrderStatusRawInputs;
  const registration = await createEnumTypeScriptRegistrationV2(repositoryRoot);
  const { family, target, realization, projector, definition_or_binding: definitions } =
    registration.providers;
  const expectedSpec = JSON.parse(bytes.realization_spec) as ArchitectureRealizationSpec;
  const spec = projector.derive({
    spec_id: expectedSpec.spec_id,
    ontology_json: bytes.ontology,
    base_profile_json: bytes.base_profile,
    typescript_profile_json: bytes.typescript_profile,
    expected_source_digests: {
      ontology_sha256: expectedSpec.ontology_ref.sha256,
      base_profile_sha256: expectedSpec.profile_ref.extends[0]!.sha256,
      typescript_profile_sha256: expectedSpec.profile_ref.sha256,
    },
  });
  const renderedSpec = projector.render(spec);
  if (renderedSpec !== bytes.realization_spec) throw new Error("ARCH_PROOF_SPEC_NOT_REPRODUCIBLE");
  const definition = definitions.definition(JSON.parse(bytes.definition));
  const catalogue = JSON.parse(bytes.catalogue) as ArchitectureObligationCatalogueV2;
  const binding = definitions.binding(JSON.parse(bytes.binding), definition);
  const compileExpectation = await target.compileExpectation();
  const realizationCase: ArchitectureRealizationCase = Object.freeze({
    schema_version: "ArchitectureRealizationCase/v1",
    case_id: "order-status-v1",
    refs: Object.freeze({
      definition_sha256: definition.definition_sha256,
      ontology_sha256: sha256(bytes.ontology),
      realization_spec_sha256: spec.spec_sha256,
      catalogue_sha256: catalogue.catalogue_sha256,
      catalogue_predecessor_sha256: sha256(bytes.catalogue_predecessor),
      binding_sha256: binding.binding_sha256,
      profile_sha256: sha256(bytes.typescript_profile),
      provider_sha256: sha256(bytes.provider),
      emitter_config_sha256: binding.emitter_config_digest,
      compiler_config_sha256: typescriptCompilerConfigSha256,
    }),
    claim_ceiling: "one candidate-local direct TypeScript Enum proof",
    authority_effect: "none",
  });
  let state = createProofState();
  const ir = family.normalize(definition, spec);
  const generated = realization.emit(ir, binding);
  state = advanceProofState(state, "generated");
  const compilePositive = await target.compile({
    repositoryRoot, generated, binding,
    expectedTypeValues: definition.members.map(({ semantic_value: value }) => value),
  });
  if (compilePositive.exit_status !== 0 || !compilePositive.type_witness.passed
      || !compilePositive.runtime_frozen) throw new Error("ARCH_PROOF_POSITIVE_COMPILE_FAILED");
  state = advanceProofState(state, "compiled");
  const observationPositive = realization.observe({
    source: generated.source, manifest: generated.manifest,
    providerSource: bytes.provider, admittedProviderSha256: binding.provider_ref.sha256,
  });
  state = advanceProofState(state, "observed");
  const evaluationPositive = family.evaluate({
    definition,
    catalogue, binding, sourceManifest: generated.manifest,
    compileExpectation,
    compileResult: compilePositive, observation: observationPositive,
  });
  if (evaluationPositive.verdict !== "pass") throw new Error("ARCH_PROOF_POSITIVE_EVALUATION_FAILED");
  state = advanceProofState(state, "evaluated");
  const mutationResult = realization.mutate(generated, binding, "status.paid");
  const compileMutation = await target.compile({
    repositoryRoot, generated: mutationResult.child, binding,
  });
  const observationMutation = realization.observe({
    source: mutationResult.child.source, manifest: mutationResult.child.manifest,
    providerSource: bytes.provider, admittedProviderSha256: binding.provider_ref.sha256,
  });
  const evaluationMutation = family.evaluate({
    definition,
    catalogue, binding, sourceManifest: mutationResult.child.manifest,
    compileExpectation,
    compileResult: compileMutation, observation: observationMutation,
  });
  if (compileMutation.exit_status !== 0 || evaluationMutation.findings.length !== 1
      || evaluationMutation.findings[0]?.code !== "ARCH_ENUM_MEMBER_MISSING"
      || evaluationMutation.findings[0]?.member_id !== "status.paid") {
    throw new Error("ARCH_PROOF_MUTATION_NOT_CAUSAL");
  }
  state = advanceProofState(state, "mutation-killed");

  const rawRoot = await mkdtemp(join(tmpdir(), "domainspec-enum-proof-raw-"));
  let replay;
  let replayIndex: ReplayRawIndex;
  try {
    const replayNames = ["ontology", "base_profile", "typescript_profile", "definition",
      "realization_spec", "catalogue", "binding", "provider"] as const;
    for (const name of replayNames) {
      await writeFile(resolve(rawRoot, `${name}.raw`), bytes[name], { flag: "wx" });
    }
    replayIndex = {
      schema_version: "ReplayRawIndex/v2",
      inputs: Object.fromEntries(replayNames.map((name) => [name, {
        path: `${name}.raw`, sha256: sha256(bytes[name]),
      }])) as ReplayRawIndex["inputs"],
      environment: await createReplayEnvironment(repositoryRoot),
      expected: {
        positive_evaluation_sha256: digestObject(evaluationPositive),
        mutation_sha256: digestObject(mutationResult.mutation),
        mutation_evaluation_sha256: digestObject(evaluationMutation),
      },
      authority_effect: "none",
    };
    replay = await replayEnumProof({ repositoryRoot, rawRoot, rawIndex: replayIndex });
  } finally {
    await rm(rawRoot, { recursive: true, force: true });
  }
  state = advanceProofState(state, "replayed");
  const coreArtifacts: Record<string, string> = {
    "case.json": json(realizationCase),
    "realization-spec.json": renderedSpec,
    "ir.json": json(ir),
    "source/order-status.ts": generated.source,
    "source/order-status.mutant.ts": mutationResult.child.source,
    "source-manifest.json": json(generated.manifest),
    "compile.positive.json": json(compilePositive),
    "compile.mutant.json": json(compileMutation),
    "observation.positive.json": json(observationPositive),
    "observation.mutant.json": json(observationMutation),
    "evaluation.positive.json": json(evaluationPositive),
    "evaluation.mutant.json": json(evaluationMutation),
    "mutation.json": json(mutationResult.mutation),
    "replay-index.json": json(replayIndex),
    "replay.json": json(replay),
  };
  const rawIndexBody = {
    schema_version: "ArchitectureProofRawIndex/v1" as const,
    external_inputs: Object.entries(enumOrderStatusRawPaths).map(([name, path]) => ({
      name, path, sha256: sha256(bytes[name as keyof typeof enumOrderStatusRawPaths]),
    })),
    artifacts: Object.entries(coreArtifacts).map(([path, value]) => ({
      path, sha256: sha256(value), byte_length: Buffer.byteLength(value, "utf8"),
    })),
    tools: {
      emitter: { name: "domainspec-typescript-enum-emitter", version: binding.emitter_version,
        config_sha256: binding.emitter_config_digest },
      compiler: { name: "typescript", version: compilePositive.compiler.version,
        config_sha256: compilePositive.compiler.config_sha256 },
      mutator: mutationResult.mutation.tool,
    },
    authority_effect: "none" as const,
  };
  const rawIndexText = json(rawIndexBody);
  const proofReceipt: ArchitectureProofReceipt = Object.freeze({
    schema_version: "ArchitectureProofReceipt/v1",
    proof_id: `proof.order-status.${sha256(rawIndexText)}`,
    state: "proof-complete",
    case_sha256: sha256(coreArtifacts["case.json"]!),
    raw_index_sha256: sha256(rawIndexText),
    positive: Object.freeze({ declared: 1, passed: 1, failed: 0, unaccounted: 0 }),
    mutations: Object.freeze({ declared: 1, killed: 1, survived: 0 }),
    exact_mutation_failure: Object.freeze({
      member_id: "status.paid",
      code: "ARCH_ENUM_MEMBER_MISSING",
    }),
    replay: Object.freeze({ status: "pass", result_sha256: replay.result_sha256 }),
    claim_ceiling: "one candidate-local direct TypeScript Enum proof",
    authority_effect: "none",
  });
  state = advanceProofState(state, "proof-complete");
  if (state.current !== "proof-complete") throw new Error("ARCH_PROOF_STATE_INCOMPLETE");
  const artifacts = Object.freeze({
    ...coreArtifacts,
    "raw-index.json": rawIndexText,
    "proof-receipt.json": json(proofReceipt),
  });
  return Object.freeze({
    state,
    realizationCase,
    ir,
    positive: Object.freeze({ compile: compilePositive, observation: observationPositive,
      evaluation: evaluationPositive }),
    mutation: Object.freeze({ ...mutationResult, compile: compileMutation,
      observation: observationMutation, evaluation: evaluationMutation }),
    replay,
    proofReceipt,
    artifacts,
  });
};

export const publishOrderStatusProof = async () => {
  const proof = await buildOrderStatusProof();
  const root = resolve(
    repositoryRoot,
    "projects/domainspec-v2/development/architecture-realization-compiler/runs",
  );
  const publication = await writeProofRun({
    root,
    runId: "order-status-v1",
    artifacts: proof.artifacts,
    validate: async (temporary) => {
      for (const path of Object.keys(proof.artifacts).filter((path) => path.endsWith(".json"))) {
        JSON.parse(await readFile(resolve(temporary, path), "utf8"));
      }
    },
  });
  return Object.freeze({ proof, publication });
};

if (process.argv.includes("--write")) {
  publishOrderStatusProof().then(({ publication }) => {
    process.stdout.write(`${JSON.stringify({
      status: "pass",
      run_path: publication.runPath,
      artifact_count: publication.index.artifacts.length,
      publication_index_sha256: publication.indexSha256,
      authority_effect: "none",
    })}\n`);
  }).catch((error: unknown) => {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = 1;
  });
}
