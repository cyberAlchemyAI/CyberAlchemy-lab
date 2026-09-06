import { lstat, readFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { beforeAll, describe, expect, it } from "vitest";

import {
  createValidatedHandle,
  readValidatedHandle,
  type ValidatedHandle,
} from "../../../kernel/contracts/validated-handle.js";
import { evaluateRule } from "../../../families/outcome-function/evaluator/evaluate-rule.js";
import {
  decodeRuleBindingV1,
  decodeRuleCaseCatalogueV1,
  decodeRuleDefinitionV1,
  normalizeRulePackageV1,
  type NormalizedRulePackageV1,
} from "../../../families/outcome-function/providers/decode-rule-contracts.js";
import {
  decodeRuleMutationCatalogueV1,
  decodeRuleObligationCatalogueV1,
} from "../../../families/outcome-function/providers/decode-rule-obligations.js";
import { inspectTypeScriptRuleSource } from "../../adapter/rule/index.js";
import {
  executeTypeScriptRule,
  executeTypeScriptRuleProofSession,
} from "../../compiler/rule/index.js";
import { mutateTypeScriptRuleSource } from "../../mutations/rule/index.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../..");
const fixtureRoot = resolve(here,
  "../../../families/outcome-function/fixtures/can-settle-payout");
let rule: ValidatedHandle<NormalizedRulePackageV1>;
let source: string;
let obligationBytes: string;
let mutationBytes: string;

beforeAll(async () => {
  const [definitionBytes, bindingBytes, caseBytes, obligations, mutants] =
    await Promise.all([
      readFile(resolve(fixtureRoot, "rule-definition.json"), "utf8"),
      readFile(resolve(fixtureRoot, "typescript-binding.json"), "utf8"),
      readFile(resolve(fixtureRoot, "cases.json"), "utf8"),
      readFile(resolve(fixtureRoot, "obligations.json"), "utf8"),
      readFile(resolve(fixtureRoot, "mutants.json"), "utf8"),
    ]);
  const definition = decodeRuleDefinitionV1(definitionBytes);
  const binding = await decodeRuleBindingV1(
    bindingBytes,
    definition,
    (path) => readFile(resolve(repositoryRoot, path)),
  );
  const cases = decodeRuleCaseCatalogueV1(caseBytes, definition);
  rule = normalizeRulePackageV1(definition, binding, cases);
  source = await readFile(resolve(repositoryRoot,
    readValidatedHandle(binding).source_ref.path), "utf8");
  obligationBytes = obligations;
  mutationBytes = mutants;
});

describe("TypeScript bound-arrow Rule realization", () => {
  it("admits and executes the handwritten positive Rule", async () => {
    const inspected = inspectTypeScriptRuleSource({
      modulePath: "can-settle-payout.ts", source, symbolName: "canSettlePayout",
    });
    expect(inspected.supported).toBe(true);
    const execution = await executeTypeScriptRule({ rule, baseSource: source });
    const session = await executeTypeScriptRuleProofSession({
      rule,
      baseSource: source,
      variants: [Object.freeze({ variantId: "positive" })],
    });
    const sessionExecution = session.variants[0]!.execution;
    expect(execution.exit_status).toBe(0);
    expect(execution.workspace).toMatchObject({
      isolation_scope: "proof-session", isolated: true, symlinks: false, cleaned: true,
    });
    expect(session.result).toBe("pass");
    expect(sessionExecution).toEqual({
      ...execution,
      workspace: sessionExecution.workspace,
    });
    expect(sessionExecution.workspace.workspace_id).not.toBe(execution.workspace.workspace_id);
    expect(execution.observation?.case_observations).toEqual([
      { case_id: "duplicate-payout-denied", outcome: false, observed_effect_count: 0 },
      { case_id: "first-payout-allowed", outcome: true, observed_effect_count: 0 },
      { case_id: "zero-amount-denied", outcome: false, observed_effect_count: 0 },
    ]);
    await expect(lstat(resolve(tmpdir(), session.workspace.workspace_id)))
      .rejects.toMatchObject({ code: "ENOENT" });
  }, 15_000);

  it("kills every source-level mutant through the independent evaluator", async () => {
    const obligations = decodeRuleObligationCatalogueV1(obligationBytes, rule);
    const mutants = readValidatedHandle(decodeRuleMutationCatalogueV1(mutationBytes, rule));
    const prepared = mutants.mutations.map((mutant) => Object.freeze({
      mutant,
      mutated: mutateTypeScriptRuleSource({
        modulePath: "can-settle-payout.ts", source,
        symbolName: "canSettlePayout", mutant,
      }),
    }));
    const variants = Object.freeze([
      Object.freeze({ variantId: "positive" }),
      ...prepared.map(({ mutant, mutated }) => Object.freeze({
        variantId: mutant.mutation_id,
        executionSource: mutated,
        mutationId: mutant.mutation_id,
      })),
    ]);
    const first = await executeTypeScriptRuleProofSession({ rule, baseSource: source, variants });
    const second = await executeTypeScriptRuleProofSession({ rule, baseSource: source, variants });
    const semanticProjection = (session: typeof first) => session.variants.map((variant) => ({
      variant_id: variant.variant_id,
      execution_source_sha256: variant.execution.execution_source_sha256,
      mutation_id: variant.execution.mutation_id,
      exit_status: variant.execution.exit_status,
      diagnostics: variant.execution.diagnostics,
      observation: variant.execution.observation,
    }));
    expect(first.result).toBe("pass");
    expect(first.diagnostics).toEqual([]);
    expect(first.variants.map(({ variant_id: id }) => id)).toEqual([
      "positive",
      ...mutants.mutations.map(({ mutation_id: id }) => id),
    ]);
    expect(new Set(first.variants.map(({ execution }) =>
      execution.execution_source_sha256)).size).toBe(first.variants.length);
    expect(new Set(first.variants.map(({ execution }) =>
      execution.workspace.workspace_id))).toEqual(new Set([first.workspace.workspace_id]));
    expect(first.variants.every(({ execution }) =>
      execution.workspace.isolation_scope === "proof-session")).toBe(true);
    expect(first.compiler.tool_sha256).toMatch(/^[a-f0-9]{64}$/u);
    expect(semanticProjection(second)).toEqual(semanticProjection(first));
    expect(second.workspace.workspace_id).not.toBe(first.workspace.workspace_id);
    await Promise.all([first, second].map(async (session) =>
      expect(lstat(resolve(tmpdir(), session.workspace.workspace_id)))
        .rejects.toMatchObject({ code: "ENOENT" })));
    for (const [index, { mutant }] of prepared.entries()) {
      const execution = first.variants[index + 1]!.execution;
      expect(execution.exit_status).toBe(0);
      expect(execution.execution_source_sha256).not.toBe(execution.base_source_sha256);
      expect(execution.observation).not.toBeNull();
      const evaluation = evaluateRule({
        rule,
        obligations,
        observation: createValidatedHandle({
          value: execution.observation!,
          source_sha256: execution.observation!.observation_sha256,
          validated_refs: [],
        }),
      });
      expect(evaluation.findings).toHaveLength(1);
      expect(evaluation.findings[0]).toMatchObject({
        code: mutant.expected_finding_code,
        case_id: mutant.case_id,
      });
    }
  }, 15_000);

  it("blocks emission atomically and attributes the exact hostile variant", async () => {
    const hostileId = "../path-shaped-hostile";
    const session = await executeTypeScriptRuleProofSession({
      rule,
      baseSource: source,
      variants: Object.freeze([
        Object.freeze({ variantId: "good" }),
        Object.freeze({
          variantId: hostileId,
          executionSource: `${source}\n)`,
          mutationId: "syntactic-hostile",
        }),
      ]),
    });
    expect(session.result).toBe("block");
    expect(session.variants.map(({ variant_id: id }) => id)).toEqual(["good", hostileId]);
    expect(session.variants.every(({ execution }) =>
      execution.exit_status === 1 && execution.observation === null)).toBe(true);
    expect(session.variants[0]!.execution.diagnostics).toEqual([{
      code: "TS_RULE_PROOF_SESSION_ATOMIC_BLOCKED",
      message: "another proof-session variant blocked atomic emission",
    }]);
    expect(session.diagnostics).toEqual([
      expect.objectContaining({ variant_id: hostileId, code: expect.stringMatching(/^TS\d+$/u) }),
    ]);
    await expect(lstat(resolve(tmpdir(), session.workspace.workspace_id)))
      .rejects.toMatchObject({ code: "ENOENT" });
    await expect(executeTypeScriptRuleProofSession({
      rule,
      baseSource: source,
      variants: Object.freeze([
        Object.freeze({ variantId: "duplicate" }),
        Object.freeze({ variantId: "duplicate" }),
      ]),
    })).rejects.toThrow("TS_RULE_PROOF_SESSION_VARIANT_INVALID");
  });

  it.each([
    ["default function", "export default function canSettlePayout(): boolean { return true; }", "TS_RULE_MODULE_SHAPE_UNSUPPORTED"],
    ["async arrow", "export const canSettlePayout = async (input: {}): Promise<boolean> => true;", "TS_RULE_ARROW_SHAPE_UNSUPPORTED"],
    ["block body", "export const canSettlePayout = (input: {}): boolean => { return true; };", "TS_RULE_ARROW_SHAPE_UNSUPPORTED"],
    ["call expression", "export const canSettlePayout = (input: { amount: number }): boolean => Boolean(input.amount);", "TS_RULE_EXPRESSION_UNSUPPORTED"],
    ["trailing syntax error", "export const canSettlePayout = (input: {}): boolean => true; )", "TS_RULE_PARSE_DIAGNOSTIC"],
  ])("fails closed for unsupported %s", (_name, hostile, code) => {
    const inspection = inspectTypeScriptRuleSource({
      modulePath: "hostile.ts", source: hostile, symbolName: "canSettlePayout",
    });
    expect(inspection.supported).toBe(false);
    expect(inspection.diagnostics.map(({ code: observed }) => observed)).toContain(code);
  });
});
