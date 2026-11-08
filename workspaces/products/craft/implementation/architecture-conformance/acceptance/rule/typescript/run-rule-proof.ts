import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  createValidatedHandle,
  readValidatedHandle,
} from "../../../kernel/contracts/validated-handle.js";
import { writeEvidenceBundleV2 } from "../../../kernel/evidence/write-evidence-bundle-v2.js";
import {
  createGenericReplayManifestV2,
  replayFromRawInputsV2,
} from "../../../kernel/evidence/generic-replay-v2.js";
import { evaluateProofAccountingV2 } from "../../../kernel/pipeline/proof-accounting-v2.js";
import { evaluateRule } from "../../../families/outcome-function/evaluator/evaluate-rule.js";
import {
  decodeRuleBindingV1,
  decodeRuleCaseCatalogueV1,
  decodeRuleDefinitionV1,
  normalizeRulePackageV1,
} from "../../../families/outcome-function/providers/decode-rule-contracts.js";
import {
  decodeRuleMutationCatalogueV1,
  decodeRuleObligationCatalogueV1,
} from "../../../families/outcome-function/providers/decode-rule-obligations.js";
import { executeTypeScriptRuleProofSession } from
  "../../../typescript/compiler/rule/index.js";
import { mutateTypeScriptRuleSource } from "../../../typescript/mutations/rule/index.js";

const here = dirname(fileURLToPath(import.meta.url));
export const repositoryRoot = resolve(here, "../../../../../../..");
const sha256 = (value: string | Uint8Array): string =>
  createHash("sha256").update(value).digest("hex");
const json = (value: unknown): string => `${JSON.stringify(value, null, 2)}\n`;

export const ruleRawPaths = Object.freeze({
  definition: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/rule-definition.json",
  binding: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/typescript-binding.json",
  cases: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/cases.json",
  obligations: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/obligations.json",
  mutants: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/mutants.json",
  source: "projects/domainspec-v2/impl/architecture-conformance/realizations/rule/typescript/bound-arrow-function-v1/fixtures/can-settle-payout.ts",
});

export type TypeScriptRuleRawInputs = Readonly<Record<keyof typeof ruleRawPaths, string>>;

export const loadTypeScriptRuleRawInputs = async (
  root = repositoryRoot,
): Promise<TypeScriptRuleRawInputs> => Object.fromEntries(await Promise.all(
  Object.entries(ruleRawPaths).map(async ([name, path]) =>
    [name, await readFile(resolve(root, path), "utf8")] as const),
)) as TypeScriptRuleRawInputs;

export const buildTypeScriptRuleProof = async (
  raw: TypeScriptRuleRawInputs,
) => {
  const definition = decodeRuleDefinitionV1(raw.definition);
  const binding = await decodeRuleBindingV1(raw.binding, definition, async () => raw.source);
  const cases = decodeRuleCaseCatalogueV1(raw.cases, definition);
  const rule = normalizeRulePackageV1(definition, binding, cases);
  const normalized = readValidatedHandle(rule);
  const obligations = decodeRuleObligationCatalogueV1(raw.obligations, rule);
  const mutants = readValidatedHandle(decodeRuleMutationCatalogueV1(raw.mutants, rule));
  const preparedMutants = mutants.mutations.map((mutant) => Object.freeze({
    mutant,
    source: mutateTypeScriptRuleSource({
      modulePath: normalized.binding.source_ref.path,
      source: raw.source,
      symbolName: normalized.binding.symbol_name,
      mutant,
    }),
  }));
  const proofSession = await executeTypeScriptRuleProofSession({
    rule,
    baseSource: raw.source,
    variants: Object.freeze([
      Object.freeze({ variantId: "positive" }),
      ...preparedMutants.map(({ mutant, source }) => Object.freeze({
        variantId: mutant.mutation_id,
        executionSource: source,
        mutationId: mutant.mutation_id,
      })),
    ]),
  });
  const expectedVariantIds = [
    "positive",
    ...mutants.mutations.map(({ mutation_id: id }) => id),
  ];
  if (JSON.stringify(proofSession.variants.map(({ variant_id: id }) => id)) !==
      JSON.stringify(expectedVariantIds)) {
    throw Object.assign(new Error("TS_RULE_PROOF_SESSION_ORDER_MISMATCH"), {
      code: "TS_RULE_PROOF_SESSION_ORDER_MISMATCH",
    });
  }
  if (proofSession.result !== "pass") {
    const failedVariantIds = new Set(proofSession.diagnostics.map(({ variant_id: id }) => id));
    const code = failedVariantIds.has(null)
      ? "TS_RULE_PROOF_SESSION_FAILED"
      : failedVariantIds.has("positive")
        ? "TS_RULE_PROOF_POSITIVE_EXECUTION_FAILED"
        : "TS_RULE_PROOF_MUTANT_EXECUTION_FAILED";
    throw Object.assign(new Error(code), { code });
  }
  const positiveExecution = proofSession.variants[0]?.execution;
  if (positiveExecution === undefined) {
    throw Object.assign(new Error("TS_RULE_PROOF_SESSION_RESULT_MISSING"), {
      code: "TS_RULE_PROOF_SESSION_RESULT_MISSING",
    });
  }
  if (positiveExecution.exit_status !== 0 || positiveExecution.observation === null) {
    throw Object.assign(new Error("TS_RULE_PROOF_POSITIVE_EXECUTION_FAILED"), {
      code: "TS_RULE_PROOF_POSITIVE_EXECUTION_FAILED",
    });
  }
  const positiveEvaluation = evaluateRule({
    rule,
    obligations,
    observation: createValidatedHandle({
      value: positiveExecution.observation,
      source_sha256: positiveExecution.observation.observation_sha256,
      validated_refs: [],
    }),
  });
  const positiveResults = normalized.cases.cases.map((item) => {
    const observed = positiveExecution.observation!.case_observations.find(
      ({ case_id: id }) => id === item.case_id,
    );
    return Object.freeze({
      case_id: item.case_id,
      status: observed?.outcome === item.expected_outcome &&
          observed.observed_effect_count === 0 && positiveEvaluation.verdict === "pass"
        ? "passed" as const : "failed" as const,
    });
  });
  const mutationEvidence = preparedMutants.map(({ mutant }, index) => {
    const execution = proofSession.variants[index + 1]?.execution;
    if (execution === undefined) {
      throw Object.assign(new Error("TS_RULE_PROOF_SESSION_RESULT_MISSING"), {
        code: "TS_RULE_PROOF_SESSION_RESULT_MISSING",
      });
    }
    if (execution.exit_status !== 0 || execution.observation === null) {
      throw Object.assign(new Error("TS_RULE_PROOF_MUTANT_EXECUTION_FAILED"), {
        code: "TS_RULE_PROOF_MUTANT_EXECUTION_FAILED",
      });
    }
    const evaluation = evaluateRule({
      rule,
      obligations,
      observation: createValidatedHandle({
        value: execution.observation,
        source_sha256: execution.observation.observation_sha256,
        validated_refs: [],
      }),
    });
    const exact = evaluation.findings.length === 1 &&
      evaluation.findings[0]?.code === mutant.expected_finding_code &&
      evaluation.findings[0]?.case_id === mutant.case_id;
    return Object.freeze({
      mutation_id: mutant.mutation_id,
      expected_finding_code: mutant.expected_finding_code,
      case_id: mutant.case_id,
      status: exact ? "killed" as const : "survived" as const,
      observed_findings: evaluation.findings,
      execution_source_sha256: execution.execution_source_sha256,
      execution,
    });
  });
  const accounting = evaluateProofAccountingV2({
    schema_version: "ProofAccountingInput/v2",
    declared_positive_case_ids: normalized.cases.cases.map(({ case_id: id }) => id),
    positive_results: positiveResults,
    declared_mutation_ids: mutants.mutations.map(({ mutation_id: id }) => id),
    mutation_results: mutationEvidence.map((item) => ({
      mutation_id: item.mutation_id,
      status: item.status,
      finding_code: item.observed_findings[0]?.code ?? null,
    })),
    authority_effect: "none",
  });
  const summary = Object.freeze({
    schema_version: "RuleProofSummary/v1" as const,
    rule_id: normalized.definition.rule_id,
    target_id: "typescript" as const,
    realization_id: normalized.binding.realization_id,
    positive: Object.freeze(positiveResults.map(({ case_id, status }) =>
      Object.freeze({ case_id, status }))),
    mutations: Object.freeze(mutationEvidence.map((item) => Object.freeze({
      mutation_id: item.mutation_id,
      case_id: item.case_id,
      finding_code: item.observed_findings[0]?.code ?? null,
      status: item.status,
    }))),
    accounting,
    claim_ceiling: "one candidate-local handwritten TypeScript Rule in the admitted bound-arrow subset",
    authority_effect: "none" as const,
  });
  if (positiveEvaluation.verdict !== "pass" || accounting.result !== "pass") {
    throw Object.assign(new Error("TS_RULE_PROOF_ACCOUNTING_BLOCKED"), {
      code: "TS_RULE_PROOF_ACCOUNTING_BLOCKED",
    });
  }
  return Object.freeze({
    summary,
    summary_sha256: sha256(JSON.stringify(summary)),
    positiveExecution,
    positiveEvaluation,
    mutationEvidence: Object.freeze(mutationEvidence),
  });
};

export const publishTypeScriptRuleProof = async (input: Readonly<{
  evidenceRoot: string;
  runId: string;
  rawInputs?: TypeScriptRuleRawInputs;
}>) => {
  const raw = input.rawInputs ?? await loadTypeScriptRuleRawInputs();
  const proof = await buildTypeScriptRuleProof(raw);
  const childEntryPath =
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/rule/typescript/replay-child.ts";
  const manifest = await createGenericReplayManifestV2({
    repositoryRoot,
    childEntryPath,
    componentPaths: {
      runner: "projects/domainspec-v2/impl/architecture-conformance/acceptance/rule/typescript/run-rule-proof.ts",
      evaluator: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/evaluator/evaluate-rule.ts",
      compiler: "projects/domainspec-v2/impl/architecture-conformance/typescript/compiler/rule/index.ts",
      adapter: "projects/domainspec-v2/impl/architecture-conformance/typescript/adapter/rule/index.ts",
      runtime: "projects/domainspec-v2/impl/architecture-conformance/typescript/runtime/rule/index.ts",
      mutator: "projects/domainspec-v2/impl/architecture-conformance/typescript/mutations/rule/index.ts",
    },
    configPaths: {
      replay: "projects/domainspec-v2/impl/architecture-conformance/acceptance/rule/typescript/replay-config.json",
    },
    expectedOutputSha256: proof.summary_sha256,
  });
  const publication = await writeEvidenceBundleV2({
    root: input.evidenceRoot,
    runId: input.runId,
    rawInputs: Object.fromEntries(Object.entries(raw).map(([name, value]) =>
      [`${name}.raw`, value])),
    artifacts: {
      "proof-summary.json": json(proof.summary),
      "positive-execution.json": json(proof.positiveExecution),
      "positive-evaluation.json": json(proof.positiveEvaluation),
      "mutation-evidence.json": json(proof.mutationEvidence),
      "replay-manifest.json": json(manifest),
    },
  });
  return Object.freeze({ proof, manifest, publication });
};

if (process.argv.includes("--write")) {
  const rootIndex = process.argv.indexOf("--evidence-root");
  const runIndex = process.argv.indexOf("--run-id");
  const evidenceRoot = rootIndex >= 0 ? process.argv[rootIndex + 1] : undefined;
  const runId = runIndex >= 0 ? process.argv[runIndex + 1] : undefined;
  if (evidenceRoot === undefined || runId === undefined) {
    throw Object.assign(new Error("TS_RULE_PROOF_EXPLICIT_OUTPUT_REQUIRED"), {
      code: "TS_RULE_PROOF_EXPLICIT_OUTPUT_REQUIRED",
    });
  }
  publishTypeScriptRuleProof({ evidenceRoot, runId }).then(async ({ proof, manifest, publication }) => {
    const replay = await replayFromRawInputsV2({
      repositoryRoot,
      runPath: publication.runPath,
      rawIndex: publication.index,
      rawIndexSha256: publication.indexSha256,
      manifest,
    });
    process.stdout.write(`${JSON.stringify({
      status: "pass",
      run_path: publication.runPath,
      raw_index_sha256: publication.indexSha256,
      summary_sha256: proof.summary_sha256,
      replay: {
        status: replay.status,
        child_pid: replay.child_pid,
        result_sha256: replay.result_sha256,
        claims: replay.claims,
      },
      authority_effect: "none",
    })}\n`);
  }).catch((error: unknown) => {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = 1;
  });
}
