import { readJson, repositoryRoot } from "./exact-ref.js";
import { verifyProviderReceipt } from "./provider-receipt.js";
import { fail, type ProviderReceipt } from "./types.js";

const DEFAULT_RECEIPT =
  "projects/domainspec-v2/development/evolvable-validation-framework/evidence/SWU-GCP-005-C1/attempt-001/provider-receipt.json";

export function verifyC1(repoRoot = repositoryRoot(), receiptPath = DEFAULT_RECEIPT): ProviderReceipt {
  const receipt = readJson<ProviderReceipt>(repoRoot, receiptPath);
  verifyProviderReceipt(receipt);
  if (
    receipt.provider.kind !== "datalog" ||
    receipt.provider.id !== "souffle" ||
    receipt.provider.version !== "2.5" ||
    receipt.claim_ceiling !== "exact-finite-corpus-relation-result-only"
  ) {
    fail("PROVIDER_RECEIPT_TAMPERED", "mapping", "C1 provider identity or claim ceiling drifted");
  }
  return receipt;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  try {
    const receipt = verifyC1();
    process.stdout.write(`${JSON.stringify({ status: "pass", semantic_result_digest: receipt.semantic_result_digest })}\n`);
  } catch (error) {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = typeof error === "object" && error !== null && "exitCode" in error
      ? Number((error as { exitCode: number }).exitCode)
      : 1;
  }
}
