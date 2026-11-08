import { createHash } from "node:crypto";
import { mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import { pathToFileURL, fileURLToPath } from "node:url";

import ts from "typescript";

import type {
  EnforcesObservationV1,
  EnforcesRelationDefinitionV1,
} from "../../../families/enforces-relation/contracts/enforces-contracts.js";
import { evaluateEnforces } from "../../../families/enforces-relation/evaluator/evaluate-enforces.js";
import {
  inspectEnforcesCompositionSource,
  mutateEnforcesCompositionSource,
} from "../../../typescript/adapter/relation/index.js";
import {
  createGenericReplayManifestV2,
  replayFromRawInputsV2,
} from "../../../kernel/evidence/generic-replay-v2.js";
import { writeEvidenceBundleV2 } from "../../../kernel/evidence/write-evidence-bundle-v2.js";

type JsonRecord = Record<string, unknown>;
const here = dirname(fileURLToPath(import.meta.url));
export const repositoryRoot = resolve(here, "../../../../../../..");
const sha256 = (value: string | Uint8Array): string =>
  createHash("sha256").update(value).digest("hex");
const json = (value: unknown): string => `${JSON.stringify(value, null, 2)}\n`;
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

export type CompositionRawInputs = Readonly<{
  relationDefinition: string;
  relationBinding: string;
  relationMutants: string;
  useCaseSource: string;
  ruleSource: string;
  operationSource: string;
  ruleDirectProof: string;
  operationDirectProof: string;
}>;

export const compositionRawPaths = Object.freeze({
  relationDefinition: "projects/domainspec-v2/impl/architecture-conformance/families/enforces-relation/fixtures/settlement-rule-operation/relation-definition.json",
  relationBinding: "projects/domainspec-v2/impl/architecture-conformance/families/enforces-relation/fixtures/settlement-rule-operation/typescript-binding.json",
  relationMutants: "projects/domainspec-v2/impl/architecture-conformance/families/enforces-relation/fixtures/settlement-rule-operation/mutants.json",
  useCaseSource: "projects/domainspec-v2/impl/architecture-conformance/realizations/relation/typescript/direct-rule-operation-v1/fixtures/settle-payout.ts",
  ruleSource: "projects/domainspec-v2/impl/architecture-conformance/realizations/rule/typescript/bound-arrow-function-v1/fixtures/can-settle-payout.ts",
  operationSource: "projects/domainspec-v2/impl/architecture-conformance/realizations/operation/typescript/state-event-arrow-v1/fixtures/complete-settlement.ts",
});

export const loadCompositionRawInputs = async (input: Readonly<{
  ruleDirectProof: string;
  operationDirectProof: string;
  root?: string;
}>): Promise<CompositionRawInputs> => Object.freeze({
  ...Object.fromEntries(await Promise.all(Object.entries(compositionRawPaths)
    .map(async ([name, path]) => [
      name,
      await readFile(resolve(input.root ?? repositoryRoot, path), "utf8"),
    ] as const))),
  ruleDirectProof: input.ruleDirectProof,
  operationDirectProof: input.operationDirectProof,
}) as CompositionRawInputs;

const modulePaths = Object.freeze({
  useCase: compositionRawPaths.useCaseSource,
  rule: compositionRawPaths.ruleSource,
  operation: compositionRawPaths.operationSource,
});

const executeComposition = async (input: Readonly<{
  raw: CompositionRawInputs;
  useCaseSource: string;
  existingSettlementId: string | null;
  mutationId: string | null;
  definition: EnforcesRelationDefinitionV1;
}>): Promise<Readonly<{
  observation: EnforcesObservationV1;
  outcome: boolean;
  payout_ids: readonly string[];
  events: readonly string[];
}>> => {
  const workspace = await mkdtemp(resolve(tmpdir(), "domainspec-enforces-ts-"));
  try {
    const sources = {
      [modulePaths.useCase]: input.useCaseSource,
      [modulePaths.rule]: input.raw.ruleSource,
      [modulePaths.operation]: input.raw.operationSource,
    };
    for (const [path, source] of Object.entries(sources)) {
      const target = resolve(workspace, path);
      await mkdir(dirname(target), { recursive: true });
      await writeFile(target, source, { encoding: "utf8", flag: "wx" });
    }
    await writeFile(resolve(workspace, "package.json"), "{\"type\":\"module\"}\n", { flag: "wx" });
    const outputRoot = resolve(workspace, "dist");
    const rootNames = Object.keys(sources).map((path) => resolve(workspace, path));
    const program = ts.createProgram(rootNames, {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.NodeNext,
      moduleResolution: ts.ModuleResolutionKind.NodeNext,
      strict: true,
      noEmitOnError: true,
      rootDir: workspace,
      outDir: outputRoot,
    });
    const diagnostics = ts.getPreEmitDiagnostics(program);
    const emitted = diagnostics.length === 0 ? program.emit() : { emitSkipped: true };
    if (diagnostics.length > 0 || emitted.emitSkipped) {
      throw Object.assign(new Error("TS_RELATION_COMPILE_FAILED"), {
        code: "TS_RELATION_COMPILE_FAILED",
      });
    }
    const load = async (path: string) => import(`${pathToFileURL(
      resolve(outputRoot, path.replace(/\.ts$/u, ".js")),
    ).href}?run=${Date.now()}`) as Promise<Record<string, unknown>>;
    const [useCaseModule, ruleModule, operationModule] = await Promise.all([
      load(modulePaths.useCase), load(modulePaths.rule), load(modulePaths.operation),
    ]);
    const useCase = useCaseModule.settlePayout;
    const rule = ruleModule.canSettlePayout;
    const operation = operationModule.completeSettlement;
    if (typeof useCase !== "function" || typeof rule !== "function" || typeof operation !== "function") {
      throw new Error("TS_RELATION_EXPORT_MISSING");
    }
    const trace: EnforcesObservationV1["architecture_facts"]["trace"][number][] = [];
    const payouts: string[] = [];
    const events: string[] = [];
    const state = {
      payouts: new Proxy(payouts, { get(target, property, receiver) {
        if (property === "push") return (...items: string[]) => {
          trace.push("payout-write"); return target.push(...items);
        };
        return Reflect.get(target, property, receiver);
      }}),
      events: new Proxy(events, { get(target, property, receiver) {
        if (property === "push") return (...items: string[]) => {
          trace.push("payout-created-event"); return target.push(...items);
        };
        return Reflect.get(target, property, receiver);
      }}),
    };
    let ruleCalls = 0;
    let operationCalls = 0;
    const wrappedRule = (candidate: unknown) => {
      ruleCalls += 1; trace.push("rule-call"); return rule(candidate);
    };
    const wrappedOperation = (candidateState: unknown, candidateInput: unknown) => {
      operationCalls += 1; trace.push("operation-call");
      return operation(candidateState, candidateInput);
    };
    const outcome = useCase(state, {
      requestId: "request-001", amount: 12500,
      existingSettlementId: input.existingSettlementId,
    }, wrappedRule, wrappedOperation);
    return Object.freeze({
      observation: Object.freeze({
        schema_version: "EnforcesObservation/v1" as const,
        semantic_edge: input.definition.semantic_edge,
        architecture_facts: Object.freeze({
          rule_call_count: ruleCalls,
          operation_call_count: operationCalls,
          trace: Object.freeze(trace),
        }),
        mutation_id: input.mutationId,
        authority_effect: "none" as const,
      }),
      outcome: outcome === true,
      payout_ids: Object.freeze(payouts),
      events: Object.freeze(events),
    });
  } finally {
    await rm(workspace, { recursive: true, force: true });
  }
};

export const buildCompositionProof = async (raw: CompositionRawInputs) => {
  const definition = JSON.parse(raw.relationDefinition) as EnforcesRelationDefinitionV1;
  const binding = JSON.parse(raw.relationBinding) as JsonRecord & {
    binding_sha256: string; source_ref: { sha256: string };
    relation_ref: { relation_id: string; definition_sha256: string };
    rule_binding_ref: { source_sha256: string };
    operation_binding_ref: { source_sha256: string };
  };
  const mutants = JSON.parse(raw.relationMutants) as JsonRecord & {
    catalogue_sha256: string;
    mutations: Array<{ mutation_id: string; defect: "bypass-rule" | "mutation-before-rule"; expected_finding_code: string }>;
  };
  const ruleDirect = JSON.parse(raw.ruleDirectProof) as JsonRecord;
  const operationDirect = JSON.parse(raw.operationDirectProof) as JsonRecord;
  if (documentDigest(definition as unknown as JsonRecord, "definition_sha256") !== definition.definition_sha256 ||
      documentDigest(binding, "binding_sha256") !== binding.binding_sha256 ||
      documentDigest(mutants, "catalogue_sha256") !== mutants.catalogue_sha256 ||
      binding.relation_ref.relation_id !== definition.relation_id ||
      binding.relation_ref.definition_sha256 !== definition.definition_sha256 ||
      binding.source_ref.sha256 !== sha256(raw.useCaseSource) ||
      binding.rule_binding_ref.source_sha256 !== sha256(raw.ruleSource) ||
      binding.operation_binding_ref.source_sha256 !== sha256(raw.operationSource) ||
      (ruleDirect.accounting as JsonRecord).result !== "pass" || operationDirect.result !== "pass") {
    throw new Error("RELATION_PROOF_INPUT_STALE");
  }
  const inspection = inspectEnforcesCompositionSource(raw.useCaseSource);
  if (!inspection.supported) throw new Error(inspection.diagnostics[0]);
  const positive = await executeComposition({
    raw, useCaseSource: raw.useCaseSource, existingSettlementId: null,
    mutationId: null, definition,
  });
  const positiveEvaluation = evaluateEnforces({ definition, observation: positive.observation });
  const denied = await executeComposition({
    raw, useCaseSource: raw.useCaseSource, existingSettlementId: "settlement-001",
    mutationId: null, definition,
  });
  const mutationEvidence = [];
  for (const mutant of mutants.mutations) {
    const mutated = mutateEnforcesCompositionSource(raw.useCaseSource, mutant.defect);
    const execution = await executeComposition({
      raw, useCaseSource: mutated, existingSettlementId: null,
      mutationId: mutant.mutation_id, definition,
    });
    const evaluation = evaluateEnforces({ definition, observation: execution.observation });
    mutationEvidence.push(Object.freeze({
      mutation_id: mutant.mutation_id,
      status: evaluation.findings.some(({ code }) => code === mutant.expected_finding_code)
        ? "killed" as const : "survived" as const,
      trace: execution.observation.architecture_facts.trace,
      findings: evaluation.findings,
      source_sha256: sha256(mutated),
    }));
  }
  if (positiveEvaluation.verdict !== "pass" || !positive.outcome ||
      denied.outcome || denied.payout_ids.length !== 0 ||
      !mutationEvidence.every(({ status }) => status === "killed")) {
    throw new Error("RELATION_COMPOSITION_PROOF_BLOCKED");
  }
  const summary = Object.freeze({
    schema_version: "EnforcesCompositionSummary/v1" as const,
    relation_id: definition.relation_id,
    direct_proofs: Object.freeze({
      rule: Object.freeze({ status: "pass" as const, sha256: sha256(raw.ruleDirectProof) }),
      operation: Object.freeze({ status: "pass" as const, sha256: sha256(raw.operationDirectProof) }),
    }),
    positive: Object.freeze({
      outcome: positive.outcome,
      trace: positive.observation.architecture_facts.trace,
      verdict: positiveEvaluation.verdict,
    }),
    denied_guard: Object.freeze({
      outcome: denied.outcome,
      trace: denied.observation.architecture_facts.trace,
      payout_count: denied.payout_ids.length,
    }),
    mutations: Object.freeze(mutationEvidence.map((item) => Object.freeze({
      mutation_id: item.mutation_id, status: item.status,
      finding_codes: item.findings.map(({ code }) => code), trace: item.trace,
    }))),
    claim_ceiling: "one candidate-local TypeScript Rule enforces Operation composition witness",
    authority_effect: "none" as const,
  });
  return Object.freeze({
    summary,
    summary_sha256: sha256(JSON.stringify(summary)),
    positive,
    positiveEvaluation,
    denied,
    mutationEvidence: Object.freeze(mutationEvidence),
  });
};

export const publishCompositionProof = async (options: Readonly<{
  evidenceRoot: string;
  runId: string;
  rawInputs: CompositionRawInputs;
}>) => {
  const raw = options.rawInputs;
  const proof = await buildCompositionProof(raw);
  const manifest = await createGenericReplayManifestV2({
    repositoryRoot,
    childEntryPath: "projects/domainspec-v2/impl/architecture-conformance/acceptance/relation/typescript/replay-child.ts",
    componentPaths: {
      runner: "projects/domainspec-v2/impl/architecture-conformance/acceptance/relation/typescript/run-composition-proof.ts",
      evaluator: "projects/domainspec-v2/impl/architecture-conformance/families/enforces-relation/evaluator/evaluate-enforces.ts",
      adapter: "projects/domainspec-v2/impl/architecture-conformance/typescript/adapter/relation/index.ts",
    },
    configPaths: {
      replay: "projects/domainspec-v2/impl/architecture-conformance/acceptance/relation/typescript/replay-config.json",
    },
    expectedOutputSha256: proof.summary_sha256,
  });
  const publication = await writeEvidenceBundleV2({
    root: options.evidenceRoot,
    runId: options.runId,
    rawInputs: Object.fromEntries(Object.entries(raw).map(([name, value]) =>
      [`${name}.raw`, value])),
    artifacts: {
      "composition-summary.json": json(proof.summary),
      "positive.json": json({ execution: proof.positive, evaluation: proof.positiveEvaluation }),
      "denied.json": json(proof.denied),
      "mutations.json": json(proof.mutationEvidence),
      "replay-manifest.json": json(manifest),
    },
  });
  return Object.freeze({ proof, manifest, publication });
};

if (process.argv.includes("--write")) {
  throw Object.assign(new Error("RELATION_COMPOSITION_EXPLICIT_INPUT_OUTPUT_REQUIRED"), {
    code: "RELATION_COMPOSITION_EXPLICIT_INPUT_OUTPUT_REQUIRED",
  });
}
