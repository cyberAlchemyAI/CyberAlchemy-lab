import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { join } from "node:path";

import { L1_PATHS } from "./derive.js";
import { exactRef, readJson, repositoryRoot } from "./exact-ref.js";
import { verifyHistoricalPokerTeamBackend } from "./historical-backend.js";
import { type ExactRef, type L1Obligation, R4_IDENTITY } from "./types.js";

type Binding = {
  readonly obligation_spec_ref: ExactRef;
  readonly runtime_source_ref: ExactRef;
};

/** Frozen v1 contract-only input; deliberately does not derive a current graph obligation. */
export function historicalR4Obligation(): L1Obligation {
  const repoRoot = repositoryRoot();
  const binding = readJson<Binding>(repoRoot, L1_PATHS.r4Binding);
  const obligationRef = exactRef(repoRoot, binding.obligation_spec_ref.path);
  if (JSON.stringify(obligationRef) !== JSON.stringify(binding.obligation_spec_ref)) {
    throw new Error("historical R4 obligation ref drifted");
  }
  const source = readFileSync(join(
    verifyHistoricalPokerTeamBackend(),
    "domain/settlement/settlement.service.ts",
  ));
  if (
    source.length !== binding.runtime_source_ref.size_bytes ||
    createHash("sha256").update(source).digest("hex") !== binding.runtime_source_ref.sha256 ||
    binding.runtime_source_ref.path !== "validation/poker-team/backend/src/domain/settlement/settlement.service.ts"
  ) throw new Error("historical R4 source binding drifted");
  const document = readJson<{ readonly obligation: L1Obligation }>(repoRoot, binding.obligation_spec_ref.path);
  const obligation = document.obligation;
  const rows = obligation.semantic_contract.truth_table;
  if (
    obligation.obligation_id !== R4_IDENTITY.obligation_id ||
    obligation.rule_id !== R4_IDENTITY.rule_id ||
    obligation.edge_id !== R4_IDENTITY.edge_id ||
    obligation.contract_kind !== "pure-decision-truth-table" ||
    !Array.isArray(rows) || rows.length !== 5
  ) throw new Error("historical R4 contract drifted");
  return obligation;
}
