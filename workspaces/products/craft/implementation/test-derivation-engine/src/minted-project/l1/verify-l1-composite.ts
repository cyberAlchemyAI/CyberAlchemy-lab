import { existsSync, readFileSync, rmSync } from "node:fs";
import { isAbsolute, resolve } from "node:path";
import { pathToFileURL } from "node:url";

import { assertExactRef, exactRef, readJson, repositoryRoot, writeStableJson } from "./exact-ref.js";
import {
  buildCompositeReceipt,
  verifyCompositeReceipt,
  verifyUnitReceipt,
} from "./receipt.js";
import { fail, L1Error, type ExactRef, type UnitReceipt } from "./types.js";
import { schemaValidate } from "./verify-p4.js";

const DEFAULT_P4 =
  "projects/domainspec-v2/development/evolvable-validation-framework/evidence/" +
  "SWU-GCP-002-P4/attempt-001/validation-receipt.json";
const DEFAULT_R4 =
  "projects/domainspec-v2/development/evolvable-validation-framework/evidence/" +
  "SWU-GCP-003-R4/attempt-001/validation-receipt.json";
const DEFAULT_OUTPUT =
  "projects/domainspec-v2/development/evolvable-validation-framework/evidence/" +
  "L1-GCP-COMPOSITE/attempt-001/composite-validation-receipt.json";

type ValidationReceipt = {
  readonly unit_id: "SWU-GCP-002-P4" | "SWU-GCP-003-R4";
  readonly status: "pass";
  readonly mode: "candidate-local-fast-lane";
  readonly receipt_ref: ExactRef;
  readonly graph_handle: { readonly handle_digest: string };
  readonly authority_effect: "none";
  readonly release_admission: "not-granted";
};

function arg(argv: readonly string[], name: string, fallback: string): string {
  const index = argv.indexOf(name);
  return index >= 0 ? argv[index + 1] ?? fallback : fallback;
}

function loadUnit(
  repoRoot: string,
  validationPath: string,
  expectedUnit: ValidationReceipt["unit_id"],
): { readonly validation: ValidationReceipt; readonly receipt: UnitReceipt } {
  const validation = readJson<ValidationReceipt>(repoRoot, validationPath);
  if (
    validation.unit_id !== expectedUnit ||
    validation.status !== "pass" ||
    validation.mode !== "candidate-local-fast-lane" ||
    validation.authority_effect !== "none" ||
    validation.release_admission !== "not-granted"
  ) {
    fail("RECEIPT_TAMPERED", "aggregate", `${expectedUnit} validation receipt is not terminal candidate-local PASS`);
  }
  assertExactRef(repoRoot, validation.receipt_ref, "RECEIPT_TAMPERED");
  const receipt = readJson<UnitReceipt>(repoRoot, validation.receipt_ref.path);
  verifyUnitReceipt(repoRoot, receipt);
  if (validation.graph_handle.handle_digest !== receipt.graph_handle.handle_digest) {
    fail("SOURCE_GRAPH_DIGEST_STALE", "aggregate", `${expectedUnit} validation/receipt graph handle mismatch`);
  }
  return { validation, receipt };
}

export function runCompositeVerification(options: {
  readonly repoRoot?: string;
  readonly p4?: string;
  readonly r4?: string;
  readonly output?: string;
} = {}): Record<string, unknown> {
  const repoRoot = options.repoRoot ? resolve(options.repoRoot) : repositoryRoot();
  const p4Path = options.p4 ?? DEFAULT_P4;
  const r4Path = options.r4 ?? DEFAULT_R4;
  const output = options.output ?? DEFAULT_OUTPUT;
  if (isAbsolute(output)) fail("UNDECLARED_WRITE", "admission", "composite output must be repository-relative", 2);
  const created: string[] = [];
  try {
    const p4 = loadUnit(repoRoot, p4Path, "SWU-GCP-002-P4");
    const r4 = loadUnit(repoRoot, r4Path, "SWU-GCP-003-R4");
    const receipt = buildCompositeReceipt({
      p4: p4.receipt,
      r4: r4.receipt,
      p4Ref: exactRef(repoRoot, p4Path),
      r4Ref: exactRef(repoRoot, r4Path),
    });
    verifyCompositeReceipt(receipt);
    writeStableJson(repoRoot, output, receipt, created);
    schemaValidate(
      repoRoot,
      "projects/domainspec-v2/development/evolvable-validation-framework/contracts/financial-settlement-l1-composite-receipt.v1.schema.json",
      output,
    );
    return {
      status: "pass",
      receipt_id: receipt.receipt_id,
      receipt_ref: exactRef(repoRoot, output),
      shared_handle_digest: receipt.shared_handle_digest,
      distinct_identity_classes: 7,
      claim_ceiling: receipt.claim_ceiling,
      authority_effect: "none",
      release_admission: "not-granted",
    };
  } catch (error) {
    for (const absolute of created.reverse()) if (existsSync(absolute)) rmSync(absolute);
    throw error;
  }
}

const invokedDirectly =
  process.argv[1] !== undefined && import.meta.url === pathToFileURL(resolve(process.argv[1])).href;
if (invokedDirectly) {
  const argv = process.argv.slice(2);
  try {
    const result = runCompositeVerification({
      p4: arg(argv, "--p4", DEFAULT_P4),
      r4: arg(argv, "--r4", DEFAULT_R4),
      output: arg(argv, "--output", DEFAULT_OUTPUT),
    });
    process.stdout.write(`${JSON.stringify(result)}\n`);
  } catch (error) {
    const failure = error instanceof L1Error
      ? { status: "blocked-or-failed", code: error.code, phase: error.phase, message: error.message }
      : { status: "blocked-or-failed", code: "TARGET_BASELINE_DRIFT", phase: "aggregate", message: error instanceof Error ? error.message : String(error) };
    process.stderr.write(`${JSON.stringify(failure)}\n`);
    process.exitCode = error instanceof L1Error ? error.exitCode : 1;
  }
}
