import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { buildMintedProjectViews, verifyMintedProjectBuild } from "../../../tools/minted-project/views.js";
import { canonicalize } from "./contract-publication.js";
import { createCurrentFinancialSettlementDevelopmentProject } from "./current-financial-settlement.js";
import { collectDevelopmentProjectDiagnostics, type DevelopmentProject } from "./development-engine.js";
import { runDevelopmentBte, type DevelopmentBteRun } from "./development-pipeline.js";
import { CATALOGUE_IDS, collectDevelopmentInstanceConformance, replayDevelopmentCore } from "./proof-engine.js";
import { replayDevelopmentBuild } from "./development-engine.js";
import { replayDevelopmentConsumers, replayDevelopmentTerminal } from "./consumer-engine.js";
import { sha256 } from "./validation/validate-semantics.js";

const implRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
const sourceRoot = resolve(implRoot, "spec/features/financial-settlement");
const generatedRoot = resolve(sourceRoot, "generated-current-20261002");
const profileRegistry = resolve(implRoot, "spec/sfol-profile/minted-project-profile.json");

const EXPECTED_COUNTS = {
  "formation-criterion@1": 4,
  "formation-structure@1": 4,
  "node-kind-causality@1": 4,
  "node-instance-conformance@1": 5,
  "relationship-family-causality@1": 3,
  "edge-instance-conformance@1": 4,
} as const;

function requireCondition(condition: unknown, code: string): asserts condition {
  if (!condition) throw new Error(`BTE_CURRENT_TERMINAL_INVALID:${code}`);
}

function bytes(value: unknown): string {
  return `${canonicalize(value)}\n`;
}

export type CurrentFinancialSettlementTerminalReport = {
  schema_version: "bte-current-financial-settlement-terminal-report/v1";
  project_id: "financial-settlement";
  source_set_digest: string;
  source_manifest_sha256: string;
  minted_build_receipt_sha256: string;
  generated: Record<string, string>;
  source_input_count: number;
  source_record_count: number;
  catalogues: Array<{ catalogue_id: string; executed: number; passed: number; killed: number }>;
  executed: 24;
  passed: 24;
  negative_controls: ["invalid-edge-endpoint-rejected", "missing-node-rejected", "tampered-run-rejected"];
  bte_summary_sha256: string;
  result: "pass";
  admission: "candidate-structural-only";
  open_questions: ["Application behavior, side effects, and SFOL proof remain outside this terminal."];
};

export type CurrentFinancialSettlementTerminalReceipt = {
  schema_version: "bte-current-financial-settlement-terminal-receipt/v1";
  report_sha256: string;
  source_set_digest: string;
  build_sha256: string;
  core_sha256: string;
  consumers_sha256: string;
  terminal_sha256: string;
  result: "pass";
  admission: "candidate-structural-only";
};

export function verifyCurrentFinancialSettlementTerminal(
  suppliedRun?: DevelopmentBteRun,
): {
  report: CurrentFinancialSettlementTerminalReport;
  reportBytes: string;
  receipt: CurrentFinancialSettlementTerminalReceipt;
  receiptBytes: string;
} {
  const minted = buildMintedProjectViews(sourceRoot, {
    developmentProfileRegistry: { path: profileRegistry, handle: "sfol-development-explicit-v0.1" },
  });
  const verification = verifyMintedProjectBuild(sourceRoot, minted);
  requireCondition(verification.status === "pass", `minted:${verification.codes.join(",")}`);

  // Bind actual authored bytes and every current generated view used by this slice.
  for (const input of minted.sourceManifest.inputs) {
    requireCondition(
      sha256(readFileSync(resolve(sourceRoot, input.path))) === input.digest,
      `source-drift:${input.path}`,
    );
  }
  requireCondition(minted.sourceManifest.inputs.length === 7, "manifest-input-count");
  const generated: Record<string, string> = {};
  for (const [name, expected] of [
    ["graph.json", minted.graphBytes],
    ["source-manifest.json", minted.sourceManifestBytes],
    ["build-receipt.json", minted.buildReceiptBytes],
    ["markdown-view.json", minted.markdownViewBytes],
    ["SPEC.md", minted.markdownBytes],
  ] as const) {
    const actual = readFileSync(resolve(generatedRoot, name));
    requireCondition(actual.equals(Buffer.from(expected)), `generated-drift:${name}`);
    generated[name] = sha256(actual);
  }
  requireCondition(minted.sourceManifest.records.length === 9, "manifest-record-count");

  const project = createCurrentFinancialSettlementDevelopmentProject();
  const run = suppliedRun ?? runDevelopmentBte(project);
  requireCondition(replayDevelopmentBuild(project, run.build).result === "pass", "build-replay");
  requireCondition(replayDevelopmentCore(project, run.build, run.core).result === "pass", "core-replay");
  requireCondition(replayDevelopmentConsumers(run.build, run.core, run.consumers).result === "pass", "consumer-replay");
  requireCondition(replayDevelopmentTerminal(run.core, run.consumers, run.terminal).result === "pass", "terminal-replay");
  const fresh = runDevelopmentBte(project);
  requireCondition(bytes(run) === bytes(fresh), "run-recomposition");

  const catalogues = run.core.catalogueRuns.map(({ catalogue, executions, mutations }) => ({
    catalogue_id: catalogue.catalogue_id,
    executed: executions.length,
    passed: executions.filter(({ status }) => status === "pass").length,
    killed: mutations.filter(({ killed }) => killed).length,
  }));
  requireCondition(
    catalogues.length === CATALOGUE_IDS.length &&
      CATALOGUE_IDS.every((id) => {
        const entry = catalogues.find(({ catalogue_id }) => catalogue_id === id);
        return entry?.executed === EXPECTED_COUNTS[id] &&
          entry.passed === EXPECTED_COUNTS[id] && entry.killed === EXPECTED_COUNTS[id];
      }) &&
      catalogues.reduce((sum, entry) => sum + entry.executed, 0) === 24 &&
      new Set(run.core.catalogueRuns.flatMap(({ executions }) => executions.map(({ coverage_key }) => coverage_key))).size === 24,
    "catalogue-execution",
  );

  const badEdge: DevelopmentProject = structuredClone(project);
  badEdge.edges.find(({ family }) => family === "enforces")!.to = "financial-settlement.PayoutCreatedEvent";
  requireCondition(
    collectDevelopmentProjectDiagnostics(badEdge).diagnostics.some(({ code }) => code === "BTE_DEV_EDGE_ENDPOINT_KIND"),
    "negative-edge",
  );
  const missingNode: DevelopmentProject = structuredClone(project);
  missingNode.nodes.pop();
  requireCondition(
    collectDevelopmentProjectDiagnostics(missingNode).diagnostics.some(({ code }) => code === "BTE_DEV_EDGE_ENDPOINT_MISSING") &&
      collectDevelopmentInstanceConformance(missingNode).result === "fail",
    "negative-node",
  );
  const tampered: DevelopmentBteRun = structuredClone(run);
  tampered.core.aggregate.total_coverage_count = 23;
  requireCondition(replayDevelopmentCore(project, tampered.build, tampered.core).result === "fail", "negative-tamper");

  const report: CurrentFinancialSettlementTerminalReport = {
    schema_version: "bte-current-financial-settlement-terminal-report/v1",
    project_id: "financial-settlement",
    source_set_digest: minted.sourceManifest.source_set_digest,
    source_manifest_sha256: sha256(minted.sourceManifestBytes),
    minted_build_receipt_sha256: sha256(minted.buildReceiptBytes),
    generated,
    source_input_count: minted.sourceManifest.inputs.length,
    source_record_count: minted.sourceManifest.records.length,
    catalogues,
    executed: 24,
    passed: 24,
    negative_controls: ["invalid-edge-endpoint-rejected", "missing-node-rejected", "tampered-run-rejected"],
    bte_summary_sha256: sha256(run.summaryBytes),
    result: "pass",
    admission: "candidate-structural-only",
    open_questions: ["Application behavior, side effects, and SFOL proof remain outside this terminal."],
  };
  const reportBytes = bytes(report);
  const receipt: CurrentFinancialSettlementTerminalReceipt = {
    schema_version: "bte-current-financial-settlement-terminal-receipt/v1",
    report_sha256: sha256(reportBytes),
    source_set_digest: report.source_set_digest,
    build_sha256: run.summary.build_sha256,
    core_sha256: run.summary.core_sha256,
    consumers_sha256: run.summary.consumers_sha256,
    terminal_sha256: run.summary.terminal_sha256,
    result: "pass",
    admission: "candidate-structural-only",
  };
  return { report, reportBytes, receipt, receiptBytes: bytes(receipt) };
}

const thisFile = fileURLToPath(import.meta.url);
if (process.argv[1] && resolve(process.argv[1]) === thisFile) {
  try {
    const { report, receipt } = verifyCurrentFinancialSettlementTerminal();
    process.stdout.write(`${JSON.stringify({ report, receipt }, null, 2)}\n`);
  } catch (error) {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = 1;
  }
}
