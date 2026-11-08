import { readJson, repositoryRoot } from "./exact-ref.js";
import { verifyProviderReceipt } from "./provider-receipt.js";
import { fail, type ProviderReceipt } from "./types.js";

const DEFAULT_RECEIPT =
  "projects/domainspec-v2/development/evolvable-validation-framework/evidence/SWU-GCP-006-C2/attempt-001/provider-receipt.json";

export function verifyC2(repoRoot = repositoryRoot(), receiptPath = DEFAULT_RECEIPT): ProviderReceipt {
  const receipt = readJson<ProviderReceipt>(repoRoot, receiptPath);
  verifyProviderReceipt(receipt);
  if (
    receipt.provider.kind !== "alloy" ||
    receipt.provider.id !== "alloy" ||
    receipt.provider.version !== "6.2.0" ||
    receipt.provider.solver_id !== "sat4j" ||
    receipt.native_result.kind !== "alloy-command" ||
    receipt.native_result.command_label !== "NoViolation" ||
    receipt.claim_ceiling !== "bounded-static-model-result-only"
  ) {
    fail("PROVIDER_RECEIPT_TAMPERED", "mapping", "C2 provider identity, scope, or claim ceiling drifted");
  }
  if (
    receipt.native_result.outcome === "sat" &&
    receipt.native_result.instance_or_counterexample_ref === null
  ) {
    fail("PROVIDER_OUTPUT_INVALID", "mapping", "SAT C2 receipt lacks counterexample evidence");
  }
  if (
    receipt.native_result.outcome !== "sat" &&
    receipt.native_result.instance_or_counterexample_ref !== null
  ) {
    fail("PROVIDER_OUTPUT_INVALID", "mapping", "non-SAT C2 receipt claims counterexample evidence");
  }
  return receipt;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  try {
    const receipt = verifyC2();
    process.stdout.write(`${JSON.stringify({ status: "pass", semantic_result_digest: receipt.semantic_result_digest })}\n`);
  } catch (error) {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = typeof error === "object" && error !== null && "exitCode" in error
      ? Number((error as { exitCode: number }).exitCode)
      : 1;
  }
}
