import { readFileSync, realpathSync } from "node:fs";
import { isAbsolute, relative, resolve } from "node:path";
import ts from "typescript";

import { L1_PATHS } from "./derive.js";
import { assertExactRef, canonicalJson, safeRepositoryPath, sha256 } from "./exact-ref.js";
import { fail, type ExactRef } from "./types.js";
import type { SettlementDecisionInput } from "./standalone-settlement-decision.js";

export const R4_STANDALONE_CONTRACT =
  "projects/domainspec-v2/development/evolvable-validation-framework/contracts/financial-settlement-r4-runtime.v2.json";
export const R4_STANDALONE_SOURCE =
  "projects/domainspec-v2/impl/test-derivation-engine/src/minted-project/l1/standalone-settlement-decision.ts";
export const R4_STANDALONE_CONTRACT_REF: ExactRef = {
  path: R4_STANDALONE_CONTRACT,
  sha256: "f08aa3180be53c590a03e8be7dafe2e0094cb52afaf3c0357dee5167392d4536",
  size_bytes: 1474,
};

export type StandaloneR4Contract = Readonly<{
  schema_version: string;
  runtime_id: string;
  unit_id: string;
  mode: string;
  runtime_source_ref: ExactRef;
  semantic_ref: ExactRef;
  fixture_ref: ExactRef;
  observation_contract: Readonly<{ function: string; decision_field: string; truth_table_cases: number }>;
  network: string;
  authority_effect: string;
  release_admission: string;
  claim_ceiling: string;
}>;

export type StandaloneR4Decision =
  (input: SettlementDecisionInput) => boolean;

const OBSERVATION_CONTRACT = {
  function: "decideStandaloneMakeupApplied",
  decision_field: "shouldCreateMakeupAppliedEvent",
  truth_table_cases: 5,
  fixed_premise: "totalAppliedMakeup > 0",
  writes_observed: false,
  events_observed: false,
} as const;

function selectedContractSnapshot(repoRoot: string): StandaloneR4Contract {
  const bytes = readFileSync(safeRepositoryPath(repoRoot, R4_STANDALONE_CONTRACT));
  if (
    sha256(bytes) !== R4_STANDALONE_CONTRACT_REF.sha256 ||
    bytes.length !== R4_STANDALONE_CONTRACT_REF.size_bytes
  ) {
    fail("BINDING_DIGEST_STALE", "binding", "selected R4 runtime contract bytes changed");
  }
  try {
    return JSON.parse(bytes.toString("utf8")) as StandaloneR4Contract;
  } catch {
    fail("BINDING_DIGEST_STALE", "binding", "selected R4 runtime contract is not JSON");
  }
}

function assertContractAgainstSelected(
  repoRoot: string,
  contract: StandaloneR4Contract,
  selected: StandaloneR4Contract,
): void {
  if (
    canonicalJson(contract) !== canonicalJson(selected) ||
    contract.schema_version !== "evf.financial-settlement-r4-standalone-runtime/v2" ||
    contract.runtime_id !== "evf.l1.financial-settlement.r4.standalone-candidate.v2" ||
    contract.unit_id !== "SWU-GCP-003-R4" ||
    contract.mode !== "candidate-standalone-pure-decision" ||
    contract.runtime_source_ref?.path !== R4_STANDALONE_SOURCE ||
    contract.semantic_ref?.path !== L1_PATHS.r4Semantic ||
    contract.fixture_ref?.path !== L1_PATHS.r4Fixture ||
    canonicalJson(contract.observation_contract) !== canonicalJson(OBSERVATION_CONTRACT) ||
    contract.network !== "forbidden" ||
    contract.authority_effect !== "none" ||
    contract.release_admission !== "not-granted" ||
    contract.claim_ceiling !== "candidate-local-pure-decision-only-not-application-runtime"
  ) {
    fail("BINDING_DIGEST_STALE", "binding", "standalone R4 runtime contract is not selected");
  }
  assertExactRef(repoRoot, contract.runtime_source_ref, "BINDING_DIGEST_STALE");
  assertExactRef(repoRoot, contract.semantic_ref, "PREDICATE_DIGEST_STALE");
  assertExactRef(repoRoot, contract.fixture_ref, "FIXTURE_DIGEST_STALE");
}

export function assertStandaloneR4Contract(
  repoRoot: string,
  contract: StandaloneR4Contract,
): void {
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

export async function loadStandaloneR4Decision(
  repoRoot: string,
  contract?: StandaloneR4Contract,
): Promise<StandaloneR4Decision> {
  const selected = selectedContractSnapshot(repoRoot);
  const current = contract ?? selected;
  assertContractAgainstSelected(repoRoot, current, selected);
  const source = sourceSnapshot(repoRoot, current.runtime_source_ref);
  const compiled = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
    reportDiagnostics: true,
    fileName: R4_STANDALONE_SOURCE,
  });
  if (compiled.diagnostics?.some((entry) => entry.category === ts.DiagnosticCategory.Error)) {
    fail("BINDING_DIGEST_STALE", "binding", "runtime source cannot be transpiled");
  }
  const moduleUrl = `data:text/javascript;base64,${Buffer.from(compiled.outputText).toString("base64")}`;
  const module = await import(moduleUrl) as {
    decideStandaloneMakeupApplied?: StandaloneR4Decision;
  };
  if (typeof module.decideStandaloneMakeupApplied !== "function") {
    fail("BINDING_DIGEST_STALE", "binding", "standalone R4 runtime export is absent");
  }
  return module.decideStandaloneMakeupApplied;
}
