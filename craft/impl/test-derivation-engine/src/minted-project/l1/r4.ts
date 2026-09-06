import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

import { digestValue, repositoryRoot } from "./exact-ref.js";
import { fail, R4_IDENTITY, type L1Obligation } from "./types.js";

type Transaction = { readonly type: string; readonly date: string };
type DecisionInput = {
  readonly existingTransactions: readonly Transaction[];
  readonly periodEnd: string;
  readonly totalAppliedMakeup: number;
  readonly totalPayout: number;
};
type R4Case = {
  readonly case_id: string;
  readonly control_class: "truth-table" | "other-date" | "other-type";
  readonly input: DecisionInput;
};

export type R4FixtureDocument = {
  readonly schema_version: "evf.financial-settlement-r4-input/v1";
  readonly fixture_id: "evf.l1.financial-settlement.r4.fixture.v1";
  readonly cases: readonly R4Case[];
  readonly expected_values_forbidden: true;
};

export type R4Observation = {
  readonly case_id: string;
  readonly control_class: R4Case["control_class"];
  readonly input_digest: string;
  readonly actual: boolean;
  readonly expected: boolean;
};

export type R4Execution = {
  readonly schema_version: "evf.financial-settlement-r4-execution/v1";
  readonly execution_id: typeof R4_IDENTITY.execution_id;
  readonly fixture_id: "evf.l1.financial-settlement.r4.fixture.v1";
  readonly observations: readonly R4Observation[];
  readonly observations_digest: string;
  readonly side_effect_observation: "none-pure-decision-only";
  readonly status: "pass";
};

type Decision = (input: DecisionInput) => boolean;

const settlementModuleUrl = pathToFileURL(resolve(
  repositoryRoot(),
  "validation/poker-team/backend/src/domain/settlement/settlement.service.ts",
)).href;
const { decideSettlementSideEffects } = await import(settlementModuleUrl) as {
  decideSettlementSideEffects(input: DecisionInput): {
    readonly shouldCreateMakeupAppliedEvent: boolean;
  };
};

function sameDateMakeupCount(input: DecisionInput): number {
  return input.existingTransactions.filter(
    (entry) => entry.type === "MAKEUP_APPLIED" && entry.date === input.periodEnd,
  ).length;
}

function decisionFor(mutantId?: string): Decision {
  if (!mutantId) {
    return (input) => decideSettlementSideEffects({
      existingTransactions: [...input.existingTransactions],
      periodEnd: input.periodEnd,
      totalAppliedMakeup: input.totalAppliedMakeup,
      totalPayout: input.totalPayout,
    }).shouldCreateMakeupAppliedEvent;
  }
  switch (mutantId) {
    case "R4-M01-always-false":
      return () => false;
    case "R4-M02-always-true":
      return () => true;
    case "R4-M03-wrong-date-filter":
      return (input) => input.totalAppliedMakeup > 0 && !input.existingTransactions.some(
        (entry) => entry.type === "MAKEUP_APPLIED" && entry.date !== input.periodEnd,
      );
    case "R4-M04-wrong-type-filter":
      return (input) => input.totalAppliedMakeup > 0 && !input.existingTransactions.some(
        (entry) => entry.type !== "MAKEUP_APPLIED" && entry.date === input.periodEnd,
      );
    case "R4-M05-wrong-count-threshold":
      return (input) => input.totalAppliedMakeup > 0 && sameDateMakeupCount(input) <= 1;
    case "R4-M06-count-all-dates":
      return (input) => input.totalAppliedMakeup > 0 && !input.existingTransactions.some(
        (entry) => entry.type === "MAKEUP_APPLIED",
      );
    case "R4-M07-count-all-types":
      return (input) => input.totalAppliedMakeup > 0 && !input.existingTransactions.some(
        (entry) => entry.date === input.periodEnd,
      );
    default:
      fail("TARGET_BASELINE_DRIFT", "mutation", `unknown R4 decision mutant: ${mutantId}`);
  }
}

function expectedByCase(obligation: L1Obligation): Map<string, boolean> {
  const semantic = obligation.semantic_contract as { readonly truth_table?: readonly { readonly case_id?: unknown; readonly expected?: unknown }[] };
  const rows = semantic.truth_table;
  if (!rows || rows.length !== 5) {
    fail("OBLIGATION_MISMATCH", "derivation", "R4 O_spec truth table is not exactly five cases");
  }
  const expected = new Map<string, boolean>();
  for (const row of rows) {
    if (typeof row.case_id !== "string" || typeof row.expected !== "boolean" || expected.has(row.case_id)) {
      fail("OBLIGATION_MISMATCH", "derivation", "R4 O_spec truth-table row is invalid");
    }
    expected.set(row.case_id, row.expected);
  }
  return expected;
}

export function validateR4Execution(execution: R4Execution): void {
  if (execution.observations_digest !== digestValue(execution.observations)) {
    fail("OBSERVATION_TAMPERED", "execution", "R4 observation digest is invalid");
  }
  if (
    execution.observations.length !== 5 ||
    new Set(execution.observations.map((entry) => entry.case_id)).size !== 5
  ) {
    fail("OBSERVATION_TAMPERED", "execution", "R4 observation denominator is not exactly five");
  }
  for (const observation of execution.observations) {
    if (observation.actual !== observation.expected) {
      const code = observation.control_class === "truth-table" ? "R4_RESULT_MISMATCH" : "R4_CONTROL_MISMATCH";
      fail(code, "execution", `R4 case mismatch: ${observation.case_id}`);
    }
  }
  if (execution.side_effect_observation !== "none-pure-decision-only") {
    fail("CLAIM_INFLATION", "execution", "R4 execution claims a side effect");
  }
}

export function runR4(
  fixture: R4FixtureDocument,
  obligation: L1Obligation,
  mutantId?: string,
): R4Execution {
  if (
    fixture.fixture_id !== "evf.l1.financial-settlement.r4.fixture.v1" ||
    fixture.expected_values_forbidden !== true ||
    fixture.cases.length !== 5 ||
    new Set(fixture.cases.map((entry) => entry.case_id)).size !== 5
  ) {
    fail("FIXTURE_DIGEST_STALE", "binding", "R4 fixture identity or denominator is invalid");
  }
  const expected = expectedByCase(obligation);
  const decide = decisionFor(mutantId);
  const observations = fixture.cases.map((entry): R4Observation => {
    const expectedValue = expected.get(entry.case_id);
    if (expectedValue === undefined) {
      fail("OBLIGATION_MISMATCH", "derivation", `R4 fixture case is absent from O_spec: ${entry.case_id}`);
    }
    if (!Number.isSafeInteger(entry.input.totalAppliedMakeup) || entry.input.totalAppliedMakeup <= 0) {
      fail("FIXTURE_DIGEST_STALE", "binding", "R4 fixed otherwise-eligible premise is invalid");
    }
    return {
      case_id: entry.case_id,
      control_class: entry.control_class,
      input_digest: digestValue(entry.input),
      actual: decide(entry.input),
      expected: expectedValue,
    };
  });
  const execution: R4Execution = {
    schema_version: "evf.financial-settlement-r4-execution/v1",
    execution_id: R4_IDENTITY.execution_id,
    fixture_id: "evf.l1.financial-settlement.r4.fixture.v1",
    observations,
    observations_digest: digestValue(observations),
    side_effect_observation: "none-pure-decision-only",
    status: "pass",
  };
  validateR4Execution(execution);
  return execution;
}
