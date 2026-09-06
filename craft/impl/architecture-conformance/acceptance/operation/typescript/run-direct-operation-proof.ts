import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { evaluateOperation } from "../../../families/state-change/evaluator/evaluate-operation.js";
import {
  inspectTypeScriptOperationSource,
  mutateTypeScriptOperationSource,
} from "../../../typescript/adapter/operation/index.js";
import { observeTypeScriptOperation } from "../../../typescript/runtime/operation/index.js";

type JsonRecord = Record<string, unknown>;
const here = dirname(fileURLToPath(import.meta.url));
export const repositoryRoot = resolve(here, "../../../../../../..");
const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");
const canonical = (value: unknown): string => JSON.stringify(
  Array.isArray(value) ? value.map((item) => JSON.parse(canonical(item))) :
    value !== null && typeof value === "object"
      ? Object.fromEntries(Object.entries(value as JsonRecord).sort(([a], [b]) =>
          Buffer.from(a).compare(Buffer.from(b))).map(([key, child]) =>
          [key, JSON.parse(canonical(child))]))
      : value,
);
const documentDigest = (value: JsonRecord, field: string): string => sha256(canonical(
  Object.fromEntries(Object.entries(value).filter(([key]) => key !== field)),
));

export const operationRawPaths = Object.freeze({
  definition: "projects/domainspec-v2/impl/architecture-conformance/families/state-change/fixtures/complete-settlement/operation-definition.json",
  binding: "projects/domainspec-v2/impl/architecture-conformance/families/state-change/fixtures/complete-settlement/typescript-binding.json",
  source: "projects/domainspec-v2/impl/architecture-conformance/realizations/operation/typescript/state-event-arrow-v1/fixtures/complete-settlement.ts",
});

export type DirectOperationRawInputs = Readonly<Record<keyof typeof operationRawPaths, string>>;

export const loadDirectOperationRawInputs = async (
  root = repositoryRoot,
): Promise<DirectOperationRawInputs> => Object.fromEntries(await Promise.all(
  Object.entries(operationRawPaths).map(async ([name, path]) =>
    [name, await readFile(resolve(root, path), "utf8")] as const),
)) as DirectOperationRawInputs;

export const buildDirectOperationProof = async (
  raw?: DirectOperationRawInputs,
) => {
  const inputs = raw ?? await loadDirectOperationRawInputs();
  const definitionBytes = inputs.definition;
  const bindingBytes = inputs.binding;
  const definition = JSON.parse(definitionBytes) as JsonRecord;
  const binding = JSON.parse(bindingBytes) as JsonRecord & {
    binding_id: string; symbol_name: string; binding_sha256: string;
    operation_ref: { operation_id: string; definition_sha256: string };
    source_ref: { path: string; sha256: string };
  };
  const source = inputs.source;
  if (documentDigest(definition, "definition_sha256") !== definition.definition_sha256 ||
      documentDigest(binding, "binding_sha256") !== binding.binding_sha256 ||
      binding.operation_ref.operation_id !== definition.operation_id ||
      binding.operation_ref.definition_sha256 !== definition.definition_sha256 ||
      sha256(source) !== binding.source_ref.sha256) {
    throw Object.assign(new Error("OPERATION_DIRECT_BINDING_STALE"), {
      code: "OPERATION_DIRECT_BINDING_STALE",
    });
  }
  const inspection = inspectTypeScriptOperationSource({
    source, modulePath: binding.source_ref.path, symbolName: binding.symbol_name,
  });
  if (!inspection.supported) throw new Error(inspection.diagnostics[0]);
  const observe = (candidate: string, mutationId: string | null) =>
    observeTypeScriptOperation({
      source: candidate, bindingId: binding.binding_id,
      bindingSourceSha256: binding.source_ref.sha256,
      symbolName: binding.symbol_name, mutationId,
      requestId: "request-001", amount: 12500,
    });
  const positiveObservation = await observe(source, null);
  const positiveEvaluation = evaluateOperation({
    observation: positiveObservation,
    expectedBindingId: binding.binding_id,
    expectedBindingSourceSha256: binding.source_ref.sha256,
    requestId: "request-001",
  });
  const mutations = [];
  for (const mutationId of ["no-op", "read-only"] as const) {
    const mutatedSource = mutateTypeScriptOperationSource({
      source, modulePath: binding.source_ref.path,
      symbolName: binding.symbol_name, mutationId,
    });
    const observation = await observe(mutatedSource, mutationId);
    const evaluation = evaluateOperation({
      observation,
      expectedBindingId: binding.binding_id,
      expectedBindingSourceSha256: binding.source_ref.sha256,
      requestId: "request-001",
    });
    mutations.push(Object.freeze({
      mutation_id: mutationId,
      status: evaluation.findings.some(({ code }) => code === "OP_STATE_CHANGE_MISSING")
        ? "killed" as const : "survived" as const,
      observation,
      evaluation,
    }));
  }
  const result = positiveEvaluation.verdict === "pass" &&
    mutations.every(({ status }) => status === "killed") ? "pass" : "block";
  const body = Object.freeze({
    schema_version: "DirectOperationProof/v1" as const,
    result,
    operation_id: definition.operation_id,
    binding_id: binding.binding_id,
    definition_sha256: definition.definition_sha256,
    binding_sha256: binding.binding_sha256,
    inspection,
    positive: Object.freeze({ observation: positiveObservation, evaluation: positiveEvaluation }),
    mutations: Object.freeze(mutations),
    claim_ceiling: "one candidate-local direct TypeScript Operation state-change proof",
    authority_effect: "none" as const,
  });
  if (result !== "pass") throw new Error("OPERATION_DIRECT_PROOF_BLOCKED");
  return Object.freeze({ ...body, proof_sha256: sha256(JSON.stringify(body)) });
};

if (process.argv.includes("--write")) {
  const outputIndex = process.argv.indexOf("--output");
  const outputArgument = outputIndex >= 0 ? process.argv[outputIndex + 1] : undefined;
  if (outputArgument === undefined) {
    throw Object.assign(new Error("OPERATION_DIRECT_EXPLICIT_OUTPUT_REQUIRED"), {
      code: "OPERATION_DIRECT_EXPLICIT_OUTPUT_REQUIRED",
    });
  }
  buildDirectOperationProof().then(async (proof) => {
    const output = resolve(outputArgument);
    await mkdir(dirname(output), { recursive: true });
    await writeFile(output, `${JSON.stringify(proof, null, 2)}\n`, {
      encoding: "utf8", flag: "wx",
    });
    process.stdout.write(`${JSON.stringify({
      status: "pass", output, proof_sha256: proof.proof_sha256,
      authority_effect: "none",
    })}\n`);
  }).catch((error: unknown) => {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = 1;
  });
}
