import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { datalogNativeResult, mapDatalogOutcome } from "./datalog.js";
import { buildProviderReceipt, verifyProviderReceipt } from "./provider-receipt.js";
import type { ExactRef, ProviderReceipt } from "./types.js";

const PROVIDER_RECEIPT_SCHEMA = fileURLToPath(new URL(
  "../../../../../development/evolvable-validation-framework/contracts/graph-law-provider-receipt.v1.schema.json",
  import.meta.url,
));

function validateAgainstProviderSchema(value: unknown): void {
  execFileSync("python3", [
    "-c",
    [
      "import json,sys",
      "from jsonschema import Draft202012Validator, FormatChecker",
      "schema=json.load(open(sys.argv[1], encoding='utf-8'))",
      "Draft202012Validator(schema, format_checker=FormatChecker()).validate(json.load(sys.stdin))",
    ].join("\n"),
    PROVIDER_RECEIPT_SCHEMA,
  ], {
    input: `${JSON.stringify(value)}\n`,
    stdio: ["pipe", "pipe", "pipe"],
    env: { PATH: process.env.PATH ?? "/usr/bin:/bin", LANG: "C", LC_ALL: "C" },
  });
}

const ref = (path: string, fill = "a"): ExactRef => ({
  path,
  sha256: fill.repeat(64),
  size_bytes: 1,
});

export function fixtureDatalogReceipt(): ProviderReceipt {
  const rowsRef = ref("Violation.csv", "b");
  const outcome = mapDatalogOutcome([], true);
  return buildProviderReceipt({
    receipt_id: "evf.l2.datalog.receipt.fixture.v1",
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
      run_id: "evf.l2.datalog.run.fixture.v1",
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
    normalized_outcome: outcome,
    evidence_refs: [rowsRef],
  });
}

describe("EVF L2 provider receipt", () => {
  it("validates the built receipt against the accepted JSON Schema", () => {
    expect(() => validateAgainstProviderSchema(fixtureDatalogReceipt())).not.toThrow();
  });

  it("replays a completed exact Datalog receipt", () => {
    const receipt = fixtureDatalogReceipt();
    expect(() => verifyProviderReceipt(receipt)).not.toThrow();
    expect(receipt.normalized_result.outcome).toBe("no-counterexample");
    expect(receipt.receipt_family).toBe("graph-relation");
    expect(receipt.claim_ceiling).toBe("exact-finite-corpus-relation-result-only");
    expect(receipt.release_admission).toBe("not-granted");
  });

  it("rejects digest-consistent Datalog result-mapping inversion", () => {
    const original = fixtureDatalogReceipt();
    expect(() => buildProviderReceipt({
      receipt_id: original.receipt_id,
      request_id: original.request_id,
      request_ref: original.request_ref,
      fact_manifest_ref: original.fact_manifest_ref,
      property_definition_ref: original.property_definition_ref,
      comparison_contract_ref: original.comparison_contract_ref,
      scope_contract_ref: original.scope_contract_ref,
      facts_digest: original.facts_digest,
      universe_digest: original.universe_digest,
      selected_relation_digest: original.selected_relation_digest,
      scope_digest: original.scope_digest,
      property_id: original.property_id,
      property_version: original.property_version,
      provider: original.provider,
      translation: original.translation,
      execution: original.execution,
      native_result: original.native_result,
      normalized_outcome: "counterexample",
      evidence_refs: original.normalized_result.evidence_refs,
    })).not.toThrow();
    const inverted = buildProviderReceipt({
      receipt_id: original.receipt_id,
      request_id: original.request_id,
      request_ref: original.request_ref,
      fact_manifest_ref: original.fact_manifest_ref,
      property_definition_ref: original.property_definition_ref,
      comparison_contract_ref: original.comparison_contract_ref,
      scope_contract_ref: original.scope_contract_ref,
      facts_digest: original.facts_digest,
      universe_digest: original.universe_digest,
      selected_relation_digest: original.selected_relation_digest,
      scope_digest: original.scope_digest,
      property_id: original.property_id,
      property_version: original.property_version,
      provider: original.provider,
      translation: original.translation,
      execution: original.execution,
      native_result: original.native_result,
      normalized_outcome: "counterexample",
      evidence_refs: original.normalized_result.evidence_refs,
    });
    expect(() => verifyProviderReceipt(inverted))
      .toThrowError(expect.objectContaining({ code: "PROVIDER_RESULT_UNMAPPED" }));
  });

  it("rejects semantic digest tamper", () => {
    const receipt = structuredClone(fixtureDatalogReceipt()) as unknown as ProviderReceipt & {
      semantic_result_digest: string;
    };
    receipt.semantic_result_digest = "0".repeat(64);
    expect(() => verifyProviderReceipt(receipt))
      .toThrowError(expect.objectContaining({ code: "PROVIDER_RECEIPT_TAMPERED" }));
  });

  it("rejects a receipt-family value outside the schema/provider mapping", () => {
    const receipt = structuredClone(fixtureDatalogReceipt()) as unknown as {
      receipt_family: string;
    };
    receipt.receipt_family = "datalog-evaluation";
    expect(() => validateAgainstProviderSchema(receipt)).toThrow();
    expect(() => verifyProviderReceipt(receipt as unknown as ProviderReceipt))
      .toThrowError(expect.objectContaining({ code: "PROVIDER_RECEIPT_TAMPERED" }));
  });

  it("rejects a non-completed execution before semantic mapping", () => {
    const fixture = fixtureDatalogReceipt();
    expect(() => buildProviderReceipt({
      receipt_id: fixture.receipt_id,
      request_id: fixture.request_id,
      request_ref: fixture.request_ref,
      fact_manifest_ref: fixture.fact_manifest_ref,
      property_definition_ref: fixture.property_definition_ref,
      comparison_contract_ref: fixture.comparison_contract_ref,
      scope_contract_ref: fixture.scope_contract_ref,
      facts_digest: fixture.facts_digest,
      universe_digest: fixture.universe_digest,
      selected_relation_digest: fixture.selected_relation_digest,
      scope_digest: fixture.scope_digest,
      property_id: fixture.property_id,
      property_version: fixture.property_version,
      provider: fixture.provider,
      translation: fixture.translation,
      execution: { ...fixture.execution, exit_code: 1 } as unknown as ProviderReceipt["execution"],
      native_result: fixture.native_result,
      normalized_outcome: fixture.normalized_result.outcome,
      evidence_refs: fixture.normalized_result.evidence_refs,
    })).toThrowError(expect.objectContaining({ code: "PROVIDER_EXECUTION_FAILED" }));
  });
});
