#!/usr/bin/env tsx

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { verifyCurrentFinancialSettlementTerminal } from "../test-derivation-engine/src/bte/current-financial-settlement-terminal.js";
import { NODE_PROJECTION_ADMISSION_VERSION, NODE_PROOF_CONTEXT_VERSION, projectNodeLogic } from "../test-derivation-engine/src/sfol/node-source/index.js";
import { typecheckLogicModule } from "../test-derivation-engine/src/sfol/language/typecheck.js";
import { canonicalJson } from "../test-derivation-engine/src/sfol/language/contracts.js";
import { buildMintedProjectViews, verifyMintedProjectBuild } from "./minted-project/views.js";

const implRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const projectRoot = resolve(implRoot, "spec/features/financial-settlement");
const defaultGeneratedRoot = resolve(projectRoot, "generated-current-20261002");
const registryPath = resolve(implRoot, "spec/sfol-profile/minted-project-profile.json");
const proposalPath = resolve(projectRoot, "sfol/source-proposal.json");
const expected = [
  { clause_id: "C3", node_id: "financial-settlement.DealSplitCalculation", module_id: "financial-settlement.deal-split" },
  { clause_id: "P4", node_id: "financial-settlement.GenerateSettlement", module_id: "financial-settlement.generate-settlement-effects" },
] as const;

type Json = Record<string, any>;
type Terminal = ReturnType<typeof verifyCurrentFinancialSettlementTerminal>;

function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

function digest(value: unknown): string {
  return sha256(canonicalJson(value));
}

function requireCondition(value: unknown, code: string): asserts value {
  if (!value) throw new Error(`SFOL_CURRENT_JOIN_INVALID:${code}`);
}

function readJson(path: string): Json {
  return JSON.parse(readFileSync(path, "utf8")) as Json;
}

export function verifyCurrentFinancialSettlementSfolJoin(options: {
  generatedRoot?: string;
  suppliedTerminal?: Terminal;
} = {}) {
  // The current active-source terminal is always executed. A supplied terminal is
  // useful for consumers that carry a receipt; it must be byte-identical to fresh evidence.
  const terminal = verifyCurrentFinancialSettlementTerminal();
  if (options.suppliedTerminal) {
    requireCondition(options.suppliedTerminal.reportBytes === terminal.reportBytes, "bte-report-substitution");
    requireCondition(options.suppliedTerminal.receiptBytes === terminal.receiptBytes, "bte-receipt-substitution");
  }
  requireCondition(terminal.report.result === "pass" && terminal.receipt.result === "pass", "bte-result");
  requireCondition(terminal.report.admission === "candidate-structural-only" && terminal.receipt.admission === "candidate-structural-only", "bte-admission");
  requireCondition(sha256(terminal.reportBytes) === terminal.receipt.report_sha256, "bte-report-digest");
  requireCondition(terminal.report.source_set_digest === terminal.receipt.source_set_digest, "bte-source-set");

  const minted = buildMintedProjectViews(projectRoot, {
    developmentProfileRegistry: { path: registryPath, handle: "sfol-development-explicit-v0.1" },
  });
  const verified = verifyMintedProjectBuild(projectRoot, minted);
  requireCondition(verified.status === "pass", `minted:${verified.codes.join(",")}`);
  const generatedRoot = options.generatedRoot ?? defaultGeneratedRoot;
  const generated = new Map([
    ["graph.json", minted.graphBytes],
    ["source-manifest.json", minted.sourceManifestBytes],
    ["build-receipt.json", minted.buildReceiptBytes],
    ["markdown-view.json", minted.markdownViewBytes],
    ["SPEC.md", minted.markdownBytes],
  ]);
  for (const [name, currentBytes] of generated) {
    requireCondition(readFileSync(resolve(generatedRoot, name), "utf8") === currentBytes, `generated-drift:${name}`);
    requireCondition(terminal.report.generated[name] === sha256(currentBytes), `bte-generated:${name}`);
  }
  requireCondition(terminal.report.source_set_digest === minted.sourceManifest.source_set_digest, "source-set-drift");
  requireCondition(terminal.report.source_manifest_sha256 === sha256(minted.sourceManifestBytes), "bte-manifest-drift");
  requireCondition(terminal.report.minted_build_receipt_sha256 === sha256(minted.buildReceiptBytes), "bte-build-drift");

  const projection = projectNodeLogic({
    schema_version: NODE_PROOF_CONTEXT_VERSION,
    route: "canonical-minted-project-build",
    graph_bytes: minted.graphBytes,
    source_manifest_bytes: minted.sourceManifestBytes,
    build_receipt_bytes: minted.buildReceiptBytes,
  }, {
    schema_version: NODE_PROJECTION_ADMISSION_VERSION,
    profile_id: "sfol-development",
    profile_version: "0.1",
    logic_schema_versions: ["domainspec-node-logic/v1"],
    admitted_node_ids: expected.map(({ node_id }) => node_id),
  });
  requireCondition(projection.ok, `projection:${projection.ok ? "" : JSON.stringify(projection.diagnostics)}`);
  const receiptBytes = readFileSync(resolve(generatedRoot, "sfol-projection-receipt.json"), "utf8");
  const receipt = JSON.parse(receiptBytes) as Json;
  const { receipt_digest: receiptDigest, ...unsigned } = receipt;
  requireCondition(receipt.schema_version === "financial-settlement-sfol-build-projection-receipt/v1" && receipt.status === "pass", "projection-receipt-version");
  requireCondition(receipt.authority === "experimental-test-lane-evidence" && receipt.authority_effect === "none" && receipt.release_admission === "not-granted" && receipt.formal_owner_approval === false, "projection-authority");
  requireCondition(receipt.deterministic_double_build === true && receipt.build_verification === "pass", "projection-build-verification");
  requireCondition(receiptDigest === digest(unsigned), "projection-receipt-digest");
  requireCondition(receipt.project_id === "financial-settlement" && receipt.profile_handle === "sfol-development-explicit-v0.1", "projection-identity");
  requireCondition(receipt.profile_registry.path === "spec/sfol-profile/minted-project-profile.json" && receipt.source_proposal.path === "spec/features/financial-settlement/sfol/source-proposal.json", "projection-source-paths");
  requireCondition(receipt.profile_registry.sha256 === sha256(readFileSync(registryPath)), "profile-drift");
  requireCondition(receipt.source_proposal.sha256 === sha256(readFileSync(proposalPath)), "proposal-drift");
  requireCondition(receipt.proof_context.source_set_digest === minted.sourceManifest.source_set_digest, "projection-source-set");
  for (const [name, field] of [
    ["graph.json", "graph"], ["source-manifest.json", "source_manifest"],
    ["build-receipt.json", "build_receipt"], ["markdown-view.json", "markdown_view"], ["SPEC.md", "markdown"],
  ] as const) {
    requireCondition(receipt.artifacts[field] === sha256(generated.get(name)!), `projection-artifact:${name}`);
  }
  requireCondition(receipt.proof_context.graph_digest === receipt.artifacts.graph && receipt.proof_context.manifest_digest === receipt.artifacts.source_manifest && receipt.proof_context.build_receipt_digest === receipt.artifacts.build_receipt, "projection-proof-context");
  requireCondition(canonicalJson(receipt.proof_context) === canonicalJson(projection.value[0]?.proof_context), "projection-context-replay");

  const proposal = readJson(proposalPath);
  requireCondition(Array.isArray(receipt.modules) && receipt.modules.length === 2 && projection.value.length === 2, "module-count");
  const modules = expected.map(({ clause_id, node_id, module_id }) => {
    const module = receipt.modules.find((entry: Json) => entry.node_id === node_id);
    const envelope = projection.value.find((entry) => entry.node.node_id === node_id);
    const clause = proposal.clauses.find((entry: Json) => entry.clause_id === clause_id);
    requireCondition(module && envelope && clause, `module-missing:${clause_id}`);
    const typed = typecheckLogicModule(envelope.logic);
    requireCondition(typed.ok, `module-type:${clause_id}`);
    const projectedClause = envelope.logic.clauses[0];
    requireCondition(envelope.logic.clauses.length === 1 && projectedClause, `clause-count:${clause_id}`);
    const manifestNode = minted.sourceManifest.records.find((entry) => entry.record_type === "node" && entry.graph_id === node_id);
    requireCondition(manifestNode, `manifest-node:${clause_id}`);
    requireCondition(module.module_id === module_id && envelope.module_id === module_id && module.clause_id === clause_id && module.projected_clause_id === `financial-settlement.${clause_id}` && projectedClause.clause_id === module.projected_clause_id, `module-identity:${clause_id}`);
    requireCondition(module.node_digest === envelope.node.node_digest && module.node_digest === manifestNode.source_digest && module.source_path === envelope.node.source_path && module.source_path === manifestNode.source_path, `module-provenance:${clause_id}`);
    requireCondition(module.module_digest === envelope.logic_digest && module.typed_module_digest === digest(typed.value) && module.materialized_clause_digest === digest(projectedClause), `module-digest:${clause_id}`);
    requireCondition(module.proposed_ast_digest === digest(clause.proposed_ast) && clause.ast_digest === module.proposed_ast_digest && module.projected_proposal_ast_digest === module.proposed_ast_digest, `proposal-ast:${clause_id}`);
    requireCondition(module.proposed_semantic_digest === digest(clause.normalized_semantic) && clause.semantic_digest === module.proposed_semantic_digest && module.projected_semantic_digest === module.proposed_semantic_digest, `proposal-semantic:${clause_id}`);
    requireCondition(module.source_status === "candidate" && projectedClause.status === "candidate", `module-status:${clause_id}`);
    return { clause_id, node_id, module_id, module_digest: module.module_digest, typed_module_digest: module.typed_module_digest, materialized_clause_digest: module.materialized_clause_digest };
  });
  requireCondition(new Set(receipt.modules.map((entry: Json) => entry.node_id)).size === 2, "module-duplicate");

  const report = {
    schema_version: "financial-settlement-sfol-current-structural-join-report/v1",
    project_id: "financial-settlement",
    result: "pass",
    admission: "candidate-structural-only",
    behavioral_adoption: "not-run",
    authority_effect: "none",
    source_set_digest: minted.sourceManifest.source_set_digest,
    bte: { report_sha256: sha256(terminal.reportBytes), receipt_sha256: sha256(terminal.receiptBytes), result: terminal.report.result },
    sfol: { projection_receipt_sha256: sha256(receiptBytes), projection_receipt_digest: receiptDigest, modules },
    open_questions: ["Application behavior, side effects, and SFOL behavioral adoption remain unverified."],
  } as const;
  return { report, reportBytes: `${JSON.stringify(report, null, 2)}\n` };
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    process.stdout.write(verifyCurrentFinancialSettlementSfolJoin().reportBytes);
  } catch (error) {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = 1;
  }
}
