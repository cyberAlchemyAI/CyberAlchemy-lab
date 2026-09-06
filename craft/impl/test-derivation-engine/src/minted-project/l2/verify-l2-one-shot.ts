import { readJson, repositoryRoot } from "./exact-ref.js";
import { verifyC0 } from "./verify-c0.js";
import { verifyC1 } from "./verify-c1.js";
import { verifyC2 } from "./verify-c2.js";
import { verifyJoinReceipt } from "./join.js";
import {
  DEFAULT_EXECUTION_ENTRY,
  DEFAULT_INVENTORY,
  scanDeclaredTargets,
} from "./one-shot.js";
import { fail, type JoinReceipt } from "./types.js";

const C3_JOIN =
  "projects/domainspec-v2/development/evolvable-validation-framework/evidence/SWU-GCP-007-C3/attempt-001/join-receipt.json";

export function verifyL2OneShot(repoRoot = repositoryRoot()): {
  readonly status: "pass";
  readonly consistency_class:
    "counterexample-consistent" |
    "no-counterexample-consistent-under-declared-bounds";
  readonly facts_digest: string;
  readonly join_payload_digest: string;
  readonly product_target_count: 85;
  readonly claim_ceiling: "property-specific-consistency-over-one-exact-shared-fact-snapshot-only";
} {
  const c0 = verifyC0(repoRoot);
  const datalog = verifyC1(repoRoot);
  const alloy = verifyC2(repoRoot);
  const join = readJson<JoinReceipt>(repoRoot, C3_JOIN);
  verifyJoinReceipt(join, datalog, alloy);
  if (
    join.join_status !== "consistent" ||
    (join.consistency_class !== "counterexample-consistent" &&
      join.consistency_class !== "no-counterexample-consistent-under-declared-bounds")
  ) {
    fail("JOIN_RESULT_DISAGREEMENT", "replay", "L2 terminal join is not a completed consistency result");
  }
  if (
    join.facts_digest !== c0.facts_digest ||
    join.universe_digest !== c0.universe_digest ||
    join.scope_digest !== c0.scope_digest ||
    join.property_id !== "evf.l2.financial-settlement.rule-to-payout-event-reachability" ||
    join.property_version !== "1" ||
    join.authority_effect !== "none" ||
    join.release_admission !== "not-granted" ||
    join.claim_ceiling !== "property-specific-consistency-over-shared-facts-only"
  ) {
    fail("JOIN_CLAIM_INFLATION", "replay", "L2 replay or claim boundary drifted");
  }
  const scan = scanDeclaredTargets({
    repositoryRoot: repoRoot,
    inventoryPath: DEFAULT_INVENTORY,
    executionEntryPath: DEFAULT_EXECUTION_ENTRY,
    phase: "terminal-live",
    rejectExtraStagedFiles: false,
  });
  if (
    scan.authored_create_count !== 44 ||
    scan.runtime_generated_count !== 40 ||
    scan.update_count !== 1 ||
    scan.scanned_paths.length !== 85
  ) {
    fail("UNDECLARED_WRITE", "closure", "terminal target denominator is not 85");
  }
  return {
    status: "pass",
    consistency_class: join.consistency_class,
    facts_digest: join.facts_digest,
    join_payload_digest: join.join_payload_digest,
    product_target_count: 85,
    claim_ceiling: "property-specific-consistency-over-one-exact-shared-fact-snapshot-only",
  };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  try {
    process.stdout.write(`${JSON.stringify(verifyL2OneShot())}\n`);
  } catch (error) {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = typeof error === "object" && error !== null && "exitCode" in error
      ? Number((error as { readonly exitCode: number }).exitCode)
      : 1;
  }
}
