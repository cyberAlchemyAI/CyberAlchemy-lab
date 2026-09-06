import { createHash } from "node:crypto";
import { writeFileSync } from "node:fs";
import { cp, mkdtemp, mkdir, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";

import type { ArchitectureObligationCatalogueV2 } from "../contracts/architecture-obligation-catalogue-v2.js";
import type { ArchitectureRealizationSpec } from "../contracts/architecture-realization-spec.js";
import type { ReplayRawIndex, ReplayResult } from "../contracts/replay-result.js";
import { createEnumTypeScriptRegistrationV2 } from "../../realizations/enum/typescript/owned-const-object-v1/registration.js";
import { validateReplayEnvironment } from "./replay-environment.js";

const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");
const digestObject = (value: unknown): string => sha256(JSON.stringify(value));
type Request = Readonly<{
  repositoryRoot: string;
  rawRoot: string;
  rawIndex: ReplayRawIndex;
  parentPid: number;
}>;

const execute = async (): Promise<ReplayResult> => {
  const requestPath = process.argv[2];
  if (!requestPath) throw new Error("ARCH_REPLAY_REQUEST_MISSING");
  const request = JSON.parse(await readFile(requestPath, "utf8")) as Request;
  await validateReplayEnvironment(
    request.repositoryRoot,
    request.rawIndex.environment,
  );
  const registration = await createEnumTypeScriptRegistrationV2(
    request.repositoryRoot,
  );
  const { family, target, realization, projector, definition_or_binding: definitions } =
    registration.providers;
  const raw = async (name: keyof ReplayRawIndex["inputs"]): Promise<string> => {
    const ref = request.rawIndex.inputs[name];
    const value = await readFile(resolve(request.rawRoot, ref.path), "utf8");
    if (sha256(value) !== ref.sha256) throw new Error("ARCH_REPLAY_RAW_INPUT_TAMPERED");
    return value;
  };
  const [ontologyJson, baseProfileJson, typescriptProfileJson, definitionJson, expectedSpecJson,
    catalogueJson, bindingJson, providerSource] = await Promise.all([
    raw("ontology"), raw("base_profile"), raw("typescript_profile"), raw("definition"),
    raw("realization_spec"), raw("catalogue"), raw("binding"), raw("provider"),
  ]);
  const expectedSpec = JSON.parse(expectedSpecJson) as ArchitectureRealizationSpec;
  const spec = projector.derive({
    spec_id: expectedSpec.spec_id,
    ontology_json: ontologyJson,
    base_profile_json: baseProfileJson,
    typescript_profile_json: typescriptProfileJson,
    expected_source_digests: {
      ontology_sha256: expectedSpec.ontology_ref.sha256,
      base_profile_sha256: expectedSpec.profile_ref.extends[0]!.sha256,
      typescript_profile_sha256: expectedSpec.profile_ref.sha256,
    },
  });
  if (projector.render(spec) !== expectedSpecJson) {
    throw new Error("ARCH_REPLAY_REALIZATION_SPEC_MISMATCH");
  }
  const definition = definitions.definition(JSON.parse(definitionJson));
  const binding = definitions.binding(JSON.parse(bindingJson), definition);
  const catalogue = JSON.parse(catalogueJson) as ArchitectureObligationCatalogueV2;
  const generated = realization.emit(family.normalize(definition, spec), binding);
  const compileExpectation = await target.compileExpectation();
  const workspace = await mkdtemp(join(tmpdir(), "domainspec-enum-replay-"));
  try {
    const providerTarget = resolve(workspace, binding.provider_ref.path);
    await mkdir(dirname(providerTarget), { recursive: true });
    const rawProvider = resolve(request.rawRoot, request.rawIndex.inputs.provider.path);
    await cp(rawProvider, providerTarget, { force: false });
    const compilePositive = await target.compile({
      repositoryRoot: workspace,
      generated,
      binding,
      expectedTypeValues: definition.members.map(({ semantic_value: value }) => value),
    });
    const observationPositive = realization.observe({
      source: generated.source,
      manifest: generated.manifest,
      providerSource,
      admittedProviderSha256: binding.provider_ref.sha256,
    });
    const evaluationPositive = family.evaluate({
      definition,
      catalogue, binding, sourceManifest: generated.manifest,
      compileExpectation,
      compileResult: compilePositive, observation: observationPositive,
    });
    const mutationResult = realization.mutate(generated, binding, "status.paid");
    const compileMutation = await target.compile({
      repositoryRoot: workspace,
      generated: mutationResult.child,
      binding,
    });
    const observationMutation = realization.observe({
      source: mutationResult.child.source,
      manifest: mutationResult.child.manifest,
      providerSource,
      admittedProviderSha256: binding.provider_ref.sha256,
    });
    const evaluationMutation = family.evaluate({
      definition,
      catalogue, binding, sourceManifest: mutationResult.child.manifest,
      compileExpectation,
      compileResult: compileMutation, observation: observationMutation,
    });
    const recomputed = {
      realization_spec_sha256: spec.spec_sha256,
      source_sha256: generated.manifest.source_sha256,
      positive_evaluation_sha256: digestObject(evaluationPositive),
      mutation_sha256: digestObject(mutationResult.mutation),
      mutation_evaluation_sha256: digestObject(evaluationMutation),
    };
    const diagnostics: string[] = [];
    if (evaluationPositive.verdict !== "pass") diagnostics.push("ARCH_REPLAY_POSITIVE_FAILED");
    if (evaluationMutation.findings.length !== 1
        || evaluationMutation.findings[0]?.code !== "ARCH_ENUM_MEMBER_MISSING"
        || evaluationMutation.findings[0]?.member_id !== "status.paid") {
      diagnostics.push("ARCH_REPLAY_MUTATION_NOT_KILLED");
    }
    if (recomputed.positive_evaluation_sha256 !== request.rawIndex.expected.positive_evaluation_sha256
        || recomputed.mutation_sha256 !== request.rawIndex.expected.mutation_sha256
        || recomputed.mutation_evaluation_sha256
          !== request.rawIndex.expected.mutation_evaluation_sha256) {
      diagnostics.push("ARCH_REPLAY_OUTPUT_MISMATCH");
    }
    const body = {
      schema_version: "ReplayResult/v2" as const,
      status: diagnostics.length === 0 ? "pass" as const : "fail" as const,
      child_pid: process.pid,
      workspace_id: workspace.split("/").at(-1) ?? workspace,
      recomputed,
      diagnostics: Object.freeze(diagnostics),
      claims: Object.freeze({
        semantic_recomposition:
          diagnostics.length === 0 ? "pass" as const : "fail" as const,
        process_isolation:
          process.pid !== request.parentPid ? "pass" as const : "fail" as const,
        byte_identity: "not-claimed" as const,
      }),
      authority_effect: "none" as const,
    };
    return Object.freeze({ ...body, result_sha256: digestObject(body) });
  } finally {
    await rm(workspace, { recursive: true, force: true });
  }
};

try {
  const result = await execute();
  writeFileSync(process.stdout.fd, JSON.stringify(result), "utf8");
} catch (error: unknown) {
  process.stderr.write(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
}
