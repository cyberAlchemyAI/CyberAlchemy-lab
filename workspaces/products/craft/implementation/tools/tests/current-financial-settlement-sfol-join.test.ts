import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { cpSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { verifyCurrentFinancialSettlementTerminal } from "../../test-derivation-engine/src/bte/current-financial-settlement-terminal.js";
import { canonicalJson } from "../../test-derivation-engine/src/sfol/language/contracts.js";
import { verifyCurrentFinancialSettlementSfolJoin } from "../current-financial-settlement-sfol-join.js";

const implRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const currentRoot = resolve(implRoot, "spec/features/financial-settlement/generated-current-20261002");

function fixture(): { root: string; cleanup: () => void } {
  const root = mkdtempSync(resolve(tmpdir(), "sfol-current-join-"));
  cpSync(currentRoot, root, { recursive: true });
  return { root, cleanup: () => rmSync(root, { recursive: true, force: true }) };
}

function mutate(root: string, file: string, edit: (value: any) => void): void {
  const path = resolve(root, file);
  const value = JSON.parse(readFileSync(path, "utf8"));
  edit(value);
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`);
}

function reseal(receipt: any): void {
  const { receipt_digest: ignored, ...unsigned } = receipt;
  void ignored;
  receipt.receipt_digest = createHash("sha256").update(canonicalJson(unsigned)).digest("hex");
}

test("current SFOL join binds fresh BTE and exactly C3/P4 as structural candidate", () => {
  const first = verifyCurrentFinancialSettlementSfolJoin();
  const second = verifyCurrentFinancialSettlementSfolJoin();
  assert.equal(first.reportBytes, second.reportBytes);
  assert.equal(first.report.result, "pass");
  assert.equal(first.report.admission, "candidate-structural-only");
  assert.equal(first.report.behavioral_adoption, "not-run");
  assert.equal(first.report.authority_effect, "none");
  assert.deepEqual(first.report.sfol.modules.map(({ clause_id }) => clause_id), ["C3", "P4"]);
});

test("join rejects stale current generated graph, manifest, and build receipt", () => {
  for (const file of ["graph.json", "source-manifest.json", "build-receipt.json"]) {
    const { root, cleanup } = fixture();
    try {
      mutate(root, file, (value) => { value.project_id = "substituted"; });
      assert.throws(() => verifyCurrentFinancialSettlementSfolJoin({ generatedRoot: root }), /generated-drift/);
    } finally { cleanup(); }
  }
});

test("join rejects substituted BTE report, receipt, and source set", () => {
  const base = verifyCurrentFinancialSettlementTerminal();
  for (const substitution of [
    { ...base, reportBytes: `${base.reportBytes} ` },
    { ...base, receiptBytes: `${base.receiptBytes} ` },
    { ...base, report: { ...base.report, source_set_digest: "0".repeat(64) }, reportBytes: "substituted-source-set" },
  ]) {
    assert.throws(() => verifyCurrentFinancialSettlementSfolJoin({ suppliedTerminal: substitution as typeof base }), /bte-(report|receipt)-substitution/);
  }
});

test("join rejects stale projection artifact and source-set digests", () => {
  for (const edit of [
    (receipt: any) => { receipt.artifacts.graph = "0".repeat(64); },
    (receipt: any) => { receipt.proof_context.source_set_digest = "0".repeat(64); },
  ]) {
    const { root, cleanup } = fixture();
    try {
      mutate(root, "sfol-projection-receipt.json", (receipt) => { edit(receipt); reseal(receipt); });
      assert.throws(() => verifyCurrentFinancialSettlementSfolJoin({ generatedRoot: root }), /projection-(artifact|source-set)/);
    } finally { cleanup(); }
  }
});

test("join rejects a resealed projection with substituted source paths or build claims", () => {
  for (const edit of [
    (receipt: any) => { receipt.profile_registry.path = "spec/other-profile.json"; },
    (receipt: any) => { receipt.source_proposal.path = "spec/other-proposal.json"; },
    (receipt: any) => { receipt.deterministic_double_build = false; },
  ]) {
    const { root, cleanup } = fixture();
    try {
      mutate(root, "sfol-projection-receipt.json", (receipt) => { edit(receipt); reseal(receipt); });
      assert.throws(() => verifyCurrentFinancialSettlementSfolJoin({ generatedRoot: root }), /projection-(source-paths|build-verification)/);
    } finally { cleanup(); }
  }
});

test("join rejects swapped, missing, and duplicated C3/P4 modules", () => {
  const edits = [
    (receipt: any) => { receipt.modules.reverse(); receipt.modules[0].node_id = "financial-settlement.DealSplitCalculation"; receipt.modules[1].node_id = "financial-settlement.GenerateSettlement"; },
    (receipt: any) => { receipt.modules.pop(); },
    (receipt: any) => { receipt.modules[1] = structuredClone(receipt.modules[0]); },
  ];
  for (const edit of edits) {
    const { root, cleanup } = fixture();
    try {
      mutate(root, "sfol-projection-receipt.json", (receipt) => { edit(receipt); reseal(receipt); });
      assert.throws(() => verifyCurrentFinancialSettlementSfolJoin({ generatedRoot: root }), /module-(identity|count|duplicate|provenance|missing)/);
    } finally { cleanup(); }
  }
});
