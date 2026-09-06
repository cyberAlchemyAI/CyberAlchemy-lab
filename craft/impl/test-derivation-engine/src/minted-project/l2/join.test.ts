import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { alloyNativeResult, type AlloyCliResult } from "./alloy.js";
import { datalogNativeResult, mapDatalogOutcome } from "./datalog.js";
import { buildJoinReceipt, verifyJoinReceipt } from "./join.js";
import { buildProviderReceipt } from "./provider-receipt.js";
import type { ExactRef, JoinReceipt, NormalizedOutcome, ProviderReceipt } from "./types.js";

const ref = (path: string, fill = "c"): ExactRef => ({
  path,
  sha256: fill.repeat(64),
  size_bytes: 1,
});

const JOIN_SCHEMA = fileURLToPath(new URL(
  "../../../../../development/evolvable-validation-framework/contracts/graph-law-join-receipt.v1.schema.json",
  import.meta.url,
));

function validateJoinSchema(value: unknown): void {
  execFileSync("python3", [
    "-c",
    "import json,sys; from jsonschema import Draft202012Validator; Draft202012Validator(json.load(open(sys.argv[1], encoding='utf-8'))).validate(json.load(sys.stdin))",
    JOIN_SCHEMA,
  ], { input: `${JSON.stringify(value)}\n`, stdio: ["pipe", "pipe", "pipe"] });
}

function fixtureDatalogReceipt(): ProviderReceipt {
  const rowsRef = ref("Violation.csv", "b");
  return buildProviderReceipt({
    receipt_id: "evf.l2.datalog.receipt.join-fixture.v1",
    request_id: "evf.l2.request.fixture.v1",
    request_ref: ref("request.json"),
    fact_manifest_ref: ref("facts.json"),
    property_definition_ref: ref("property.json"),
    comparison_contract_ref: ref("comparison.json"),
    scope_contract_ref: ref("scope.json"),
    facts_digest: "1".repeat(64),
    universe_digest: "2".repeat(64),
    selected_relation_digest: "3".repeat(64),
    scope_digest: "4".repeat(64),
    property_id: "evf.l2.financial-settlement.rule-to-payout-event-reachability",
    property_version: "1",
    provider: {
      kind: "datalog",
      id: "souffle",
      version: "2.5",
      runtime_ref: ref("souffle"),
      adapter_ref: ref("datalog.ts"),
      query_or_model_ref: ref("reachability.dl"),
      invocation_contract_ref: ref("runtime.json"),
      solver_id: null,
      solver_version: null,
      options_digest: "5".repeat(64),
    },
    translation: {
      provider_input_ref: ref("Edge.facts"),
      source_facts_digest: "1".repeat(64),
      projection_receipt_ref: ref("projection.json"),
      omitted_fact_count: 0,
      invented_fact_count: 0,
      translation_digest: "6".repeat(64),
    },
    execution: {
      run_id: "evf.l2.datalog.run.join-fixture.v1",
      status: "completed",
      exit_code: 0,
      timed_out: false,
      started_at: "2026-08-21T00:00:00.000Z",
      finished_at: "2026-08-21T00:00:01.000Z",
      stdout_ref: ref("stdout.log"),
      stderr_ref: ref("stderr.log"),
      raw_output_ref: ref("raw-output.json"),
      exact_command: ["/tool/souffle", "-j", "1"],
    },
    native_result: datalogNativeResult([], rowsRef),
    normalized_outcome: mapDatalogOutcome([], true),
    evidence_refs: [rowsRef],
  });
}

function alloyReceipt(outcome: NormalizedOutcome = "no-counterexample"): ProviderReceipt {
  const datalog = fixtureDatalogReceipt();
  const nativeOutcome: AlloyCliResult["outcome"] = outcome === "counterexample"
    ? "sat"
    : outcome === "no-counterexample"
      ? "unsat"
      : "unknown";
  const result = {
    command_label: "NoViolation" as const,
    outcome: nativeOutcome,
    solution_count: nativeOutcome === "sat" ? 1 : nativeOutcome === "unsat" ? 0 : null,
    counterexample: nativeOutcome === "sat" ? { atoms: ["N0"] } : null,
    raw: {},
  };
  const nativeEvidence = nativeOutcome === "sat" ? ref("instance.json", "d") : null;
  return buildProviderReceipt({
    receipt_id: "evf.l2.alloy.receipt.fixture.v1",
    request_id: datalog.request_id,
    request_ref: datalog.request_ref,
    fact_manifest_ref: datalog.fact_manifest_ref,
    property_definition_ref: datalog.property_definition_ref,
    comparison_contract_ref: datalog.comparison_contract_ref,
    scope_contract_ref: datalog.scope_contract_ref,
    facts_digest: datalog.facts_digest,
    universe_digest: datalog.universe_digest,
    selected_relation_digest: datalog.selected_relation_digest,
    scope_digest: datalog.scope_digest,
    property_id: datalog.property_id,
    property_version: datalog.property_version,
    provider: {
      kind: "alloy",
      id: "alloy",
      version: "6.2.0",
      runtime_ref: ref("alloy.jar"),
      adapter_ref: ref("alloy.ts"),
      query_or_model_ref: ref("model.als"),
      invocation_contract_ref: ref("runtime.json"),
      solver_id: "sat4j",
      solver_version: "bundled-6.2.0",
      options_digest: "5".repeat(64),
    },
    translation: { ...datalog.translation, provider_input_ref: ref("model.als") },
    execution: { ...datalog.execution, run_id: "evf.l2.alloy.run.fixture.v1" },
    native_result: alloyNativeResult(
      result,
      { Node: 5 },
      datalog.scope_digest,
      ref("alloy-cli.json"),
      nativeEvidence,
    ),
    normalized_outcome: outcome,
    evidence_refs: [ref("instance-or-counterexample.json")],
  });
}

function joined(datalog = fixtureDatalogReceipt(), alloy = alloyReceipt()) {
  return buildJoinReceipt({
    joinReceiptId: "evf.l2.join.fixture.v1",
    datalog,
    alloy,
    datalogRef: ref("datalog-receipt.json"),
    alloyRef: ref("alloy-receipt.json"),
  });
}

describe("EVF L2 non-inflating join", () => {
  it("emits consistency only for equal comparable completed outcomes", () => {
    const datalog = fixtureDatalogReceipt();
    const alloy = alloyReceipt();
    const receipt = joined(datalog, alloy);
    expect(receipt.join_status).toBe("consistent");
    expect(receipt.consistency_class).toBe("no-counterexample-consistent-under-declared-bounds");
    expect(() => verifyJoinReceipt(receipt, datalog, alloy)).not.toThrow();
    expect(() => validateJoinSchema(receipt)).not.toThrow();
  });

  it("emits unresolved rather than voting on disagreement", () => {
    const receipt = joined(fixtureDatalogReceipt(), alloyReceipt("counterexample"));
    expect(receipt.join_status).toBe("unresolved");
    expect(receipt.consistency_class).toBe("provider-disagreement");
  });

  it("blocks mismatched facts, request, property, mapping, or scope", () => {
    const datalog = fixtureDatalogReceipt();
    const alloy = structuredClone(alloyReceipt()) as ProviderReceipt & { scope_digest: string };
    alloy.scope_digest = "0".repeat(64);
    const receipt = joined(datalog, alloy);
    expect(receipt.join_status).toBe("blocked");
    expect(receipt.consistency_class).toBe("not-comparable");
  });

  it("rejects claim inflation and receipt tamper", () => {
    const datalog = fixtureDatalogReceipt();
    const alloy = alloyReceipt();
    const receipt = joined(datalog, alloy);
    const tampered = structuredClone(receipt) as unknown as { claim_ceiling: string };
    tampered.claim_ceiling = "unbounded-theorem";
    expect(() => verifyJoinReceipt(tampered as unknown as JoinReceipt, datalog, alloy))
      .toThrowError(expect.objectContaining({ code: "JOIN_RECEIPT_TAMPERED" }));
  });
});
