import { describe, expect, it } from "vitest";

import type { ProofAccountingInputV2 } from "../contracts/proof-accounting-v2.js";
import { evaluateProofAccountingV2 } from "./proof-accounting-v2.js";
import {
  advanceProofStateV2,
  createProofStateV2,
  type ProofStateNameV2,
} from "./proof-state-v2.js";

const completeInput = (): ProofAccountingInputV2 => ({
  schema_version: "ProofAccountingInput/v2",
  declared_positive_case_ids: ["positive/one"],
  positive_results: [{ case_id: "positive/one", status: "passed" }],
  declared_mutation_ids: ["mutation/one"],
  mutation_results: [{
    mutation_id: "mutation/one",
    status: "killed",
    finding_code: "EXACT_CAUSAL_FINDING",
  }],
  authority_effect: "none",
});

describe("generic proof state and complete accounting", () => {
  it("advances through the only legal mode-neutral lifecycle", () => {
    const accounting = evaluateProofAccountingV2(completeInput());
    expect(accounting).toEqual(expect.objectContaining({
      result: "pass",
      positive: { declared: 1, passed: 1, failed: 0, unaccounted: 0 },
      mutations: { declared: 1, killed: 1, survived: 0, unaccounted: 0 },
      diagnostics: [],
    }));
    let state = createProofStateV2("proof/example");
    for (const next of [
      "providers-validated",
      "positive-evaluated",
      "mutations-evaluated",
      "accounted",
      "evidence-written",
      "replayed",
      "proof-complete",
    ] as const satisfies readonly ProofStateNameV2[]) {
      state = advanceProofStateV2(
        state,
        next,
        next === "accounted" ? accounting : undefined,
      );
    }
    expect(state.current).toBe("proof-complete");
    expect(state.diagnostics).toEqual([]);
  });

  it("blocks an illegal transition and remains terminal", () => {
    const state = advanceProofStateV2(
      createProofStateV2("proof/example"),
      "positive-evaluated",
    );
    expect(state).toEqual(expect.objectContaining({
      current: "blocked",
      diagnostics: [
        "FACTORY_PROOF_STATE_TRANSITION_INVALID:prepared->positive-evaluated",
      ],
    }));
    expect(advanceProofStateV2(state, "providers-validated")).toBe(state);
  });

  it.each([
    ["missing positive", (input: ProofAccountingInputV2) => ({
      ...input,
      declared_positive_case_ids: [],
      positive_results: [],
    }), "FACTORY_ACCOUNTING_POSITIVE_MISSING"],
    ["missing mutation", (input: ProofAccountingInputV2) => ({
      ...input,
      declared_mutation_ids: [],
      mutation_results: [],
    }), "FACTORY_ACCOUNTING_MUTATION_MISSING"],
    ["duplicate positive", (input: ProofAccountingInputV2) => ({
      ...input,
      declared_positive_case_ids: ["positive/one", "positive/one"],
    }), "FACTORY_ACCOUNTING_POSITIVE_DUPLICATE"],
    ["duplicate mutation", (input: ProofAccountingInputV2) => ({
      ...input,
      mutation_results: [...input.mutation_results, input.mutation_results[0]!],
    }), "FACTORY_ACCOUNTING_MUTATION_DUPLICATE"],
    ["unaccounted positive", (input: ProofAccountingInputV2) => ({
      ...input,
      declared_positive_case_ids: ["positive/one", "positive/two"],
    }), "FACTORY_ACCOUNTING_POSITIVE_UNACCOUNTED"],
    ["unaccounted mutation", (input: ProofAccountingInputV2) => ({
      ...input,
      declared_mutation_ids: ["mutation/one", "mutation/two"],
    }), "FACTORY_ACCOUNTING_MUTATION_UNACCOUNTED"],
  ] as const)("blocks %s accounting", (_name, mutate, code) => {
    const accounting = evaluateProofAccountingV2(mutate(completeInput()));
    expect(accounting.result).toBe("block");
    expect(accounting.diagnostics).toContain(code);
    let state = createProofStateV2("proof/example");
    state = advanceProofStateV2(state, "providers-validated");
    state = advanceProofStateV2(state, "positive-evaluated");
    state = advanceProofStateV2(state, "mutations-evaluated");
    state = advanceProofStateV2(state, "accounted", accounting);
    expect(state.current).toBe("blocked");
    expect(state.diagnostics).toContain("FACTORY_PROOF_ACCOUNTING_INCOMPLETE");
  });

  it("blocks failed positives, surviving mutants, and unexpected results", () => {
    const input = completeInput();
    const accounting = evaluateProofAccountingV2({
      ...input,
      positive_results: [
        { case_id: "positive/one", status: "failed" },
        { case_id: "positive/unexpected", status: "passed" },
      ],
      mutation_results: [
        { mutation_id: "mutation/one", status: "survived", finding_code: null },
        { mutation_id: "mutation/unexpected", status: "killed", finding_code: "X" },
      ],
    });
    expect(accounting.result).toBe("block");
    expect(accounting.diagnostics).toEqual(expect.arrayContaining([
      "FACTORY_ACCOUNTING_POSITIVE_FAILED",
      "FACTORY_ACCOUNTING_MUTATION_SURVIVED",
      "FACTORY_ACCOUNTING_POSITIVE_UNEXPECTED",
      "FACTORY_ACCOUNTING_MUTATION_UNEXPECTED",
    ]));
  });
});
