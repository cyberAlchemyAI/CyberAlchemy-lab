import { readFileSync, realpathSync } from "node:fs";
import { isAbsolute, relative, resolve } from "node:path";
import ts from "typescript";

import { L1_PATHS } from "./derive.js";
import { assertExactRef, canonicalJson, safeRepositoryPath, sha256 } from "./exact-ref.js";
import { fail, type ExactRef } from "./types.js";
import type { StandalonePayoutPorts, StandalonePayoutPrestate } from "./standalone-payout-effects.js";

export const P4_STANDALONE_CONTRACT =
  "projects/domainspec-v2/development/evolvable-validation-framework/contracts/financial-settlement-p4-runtime.v2.json";
export const P4_STANDALONE_SOURCE =
  "projects/domainspec-v2/impl/test-derivation-engine/src/minted-project/l1/standalone-payout-effects.ts";
export const P4_STANDALONE_CONTRACT_REF: ExactRef = {
  path: P4_STANDALONE_CONTRACT,
  sha256: "45c2457bb90169abaca177d4e80159ee62597c1b581989eadf1a5e32602f6234",
  size_bytes: 1522,
};

export type StandaloneP4Contract = Readonly<{
  schema_version: string;
  runtime_id: string;
  unit_id: string;
  mode: string;
  runtime_source_ref: ExactRef;
  semantic_ref: ExactRef;
  fixture_ref: ExactRef;
  observation_contract: Readonly<{
    function: string;
    antecedent: string;
    ordered_effects: readonly string[];
    observed_at_port_invocation: boolean;
    manufactured_trace_forbidden: boolean;
  }>;
  network: string;
  authority_effect: string;
  release_admission: string;
  claim_ceiling: string;
}>;

export type StandaloneP4Executor = (
  prestate: StandalonePayoutPrestate,
  ports: StandalonePayoutPorts,
) => Promise<void>;

const OBSERVATION_CONTRACT = {
  function: "executeStandalonePayoutEffects",
  antecedent: "totalPayout > 0 and existingPayoutCountForEndDate = 0",
  ordered_effects: ["write:PAYOUT", "event:PayoutCreated"],
  observed_at_port_invocation: true,
  manufactured_trace_forbidden: true,
} as const;

function selectedContractSnapshot(repoRoot: string): StandaloneP4Contract {
  const bytes = readFileSync(safeRepositoryPath(repoRoot, P4_STANDALONE_CONTRACT));
  if (sha256(bytes) !== P4_STANDALONE_CONTRACT_REF.sha256 ||
      bytes.length !== P4_STANDALONE_CONTRACT_REF.size_bytes) {
    fail("BINDING_DIGEST_STALE", "binding", "selected P4 runtime contract bytes changed");
  }
  try {
    return JSON.parse(bytes.toString("utf8")) as StandaloneP4Contract;
  } catch {
    fail("BINDING_DIGEST_STALE", "binding", "selected P4 runtime contract is not JSON");
  }
}

function assertContractAgainstSelected(
  repoRoot: string,
  contract: StandaloneP4Contract,
  selected: StandaloneP4Contract,
): void {
  if (canonicalJson(contract) !== canonicalJson(selected) ||
      contract.schema_version !== "evf.financial-settlement-p4-standalone-runtime/v2" ||
      contract.runtime_id !== "evf.l1.financial-settlement.p4.standalone-candidate.v2" ||
      contract.unit_id !== "SWU-GCP-002-P4" ||
      contract.mode !== "candidate-standalone-observed-ports" ||
      contract.runtime_source_ref?.path !== P4_STANDALONE_SOURCE ||
      contract.semantic_ref?.path !== L1_PATHS.p4Semantic ||
      contract.fixture_ref?.path !== L1_PATHS.p4Fixture ||
      canonicalJson(contract.observation_contract) !== canonicalJson(OBSERVATION_CONTRACT) ||
      contract.network !== "forbidden" ||
      contract.authority_effect !== "none" ||
      contract.release_admission !== "not-granted" ||
      contract.claim_ceiling !== "candidate-local-p4-rule-slice-only-not-application-runtime-or-transaction-atomicity") {
    fail("BINDING_DIGEST_STALE", "binding", "standalone P4 runtime contract is not selected");
  }
  assertExactRef(repoRoot, contract.runtime_source_ref, "BINDING_DIGEST_STALE");
  assertExactRef(repoRoot, contract.semantic_ref, "PREDICATE_DIGEST_STALE");
  assertExactRef(repoRoot, contract.fixture_ref, "FIXTURE_DIGEST_STALE");
}

export function assertStandaloneP4Contract(repoRoot: string, contract: StandaloneP4Contract): void {
  assertContractAgainstSelected(repoRoot, contract, selectedContractSnapshot(repoRoot));
}

function sourceSnapshot(repoRoot: string, ref: ExactRef): string {
  const root = realpathSync(repoRoot);
  const target = realpathSync(resolve(root, ref.path));
  const rel = relative(root, target);
  if (rel === ".." || rel.startsWith("../") || isAbsolute(rel)) {
    fail("BINDING_DIGEST_STALE", "binding", "runtime source escapes selected root");
  }
  const bytes = readFileSync(target);
  if (sha256(bytes) !== ref.sha256 || bytes.length !== ref.size_bytes) {
    fail("BINDING_DIGEST_STALE", "binding", "runtime source changed before execution");
  }
  return bytes.toString("utf8");
}

export async function loadStandaloneP4Executor(
  repoRoot: string,
  contract?: StandaloneP4Contract,
): Promise<StandaloneP4Executor> {
  const selected = selectedContractSnapshot(repoRoot);
  const current = contract ?? selected;
  assertContractAgainstSelected(repoRoot, current, selected);
  const source = sourceSnapshot(repoRoot, current.runtime_source_ref);
  const compiled = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
    reportDiagnostics: true,
    fileName: P4_STANDALONE_SOURCE,
  });
  if (compiled.diagnostics?.some(entry => entry.category === ts.DiagnosticCategory.Error)) {
    fail("BINDING_DIGEST_STALE", "binding", "runtime source cannot be transpiled");
  }
  const moduleUrl = `data:text/javascript;base64,${Buffer.from(compiled.outputText).toString("base64")}`;
  const module = await import(moduleUrl) as { executeStandalonePayoutEffects?: StandaloneP4Executor };
  if (typeof module.executeStandalonePayoutEffects !== "function") {
    fail("BINDING_DIGEST_STALE", "binding", "standalone P4 runtime export is absent");
  }
  return module.executeStandalonePayoutEffects;
}
