import { createHash } from "node:crypto";
import { realpathSync } from "node:fs";
import { isAbsolute, relative, resolve } from "node:path";

import { exactRef } from "./derive.js";

import {
  ACCEPTANCE_VECTOR,
  EXECUTION_CARDINALITY,
  fail,
  type EvfFailureCode,
  type ExactRef,
  type RuntimeObservation,
} from "./types.js";

export interface NegativeControlReceipt {
  readonly schema_version: "evf.evolvable-validation-receipt/v2";
  readonly receipt_id: string;
  readonly receipt_class: "negative-control";
  readonly swu_id: "SWU-GCP-001";
  readonly exact_refs: readonly ExactRef[];
  readonly positive_receipt_issued: false;
  readonly mutant_id: string;
  readonly stable_code: EvfFailureCode;
  readonly release_admission: "not-granted";
  readonly claim_ceiling: "candidate-local-SWU-GCP-001-causal-proof-only";
  readonly result: "killed";
}

export interface PositiveProofReceipt {
  readonly schema_version: "evf.evolvable-validation-receipt/v2";
  readonly receipt_id: "evf.s1.positive-proof.v2";
  readonly receipt_class: "positive-proof";
  readonly swu_id: "SWU-GCP-001";
  readonly exact_refs: readonly ExactRef[];
  readonly positive_receipt_issued: true;
  readonly acceptance_vector: typeof ACCEPTANCE_VECTOR;
  readonly execution_cardinality: typeof EXECUTION_CARDINALITY;
  readonly runtime_observations: readonly [RuntimeObservation, RuntimeObservation];
  readonly release_admission: "not-granted";
  readonly claim_ceiling: "candidate-local-SWU-GCP-001-causal-proof-only";
  readonly result: "pass";
}

export type EvolvableValidationReceipt = NegativeControlReceipt | PositiveProofReceipt;

export function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (value !== null && typeof value === "object") {
    const record = value as Record<string, unknown>;
    return `{${Object.keys(record)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonicalJson(record[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

export function receiptDigest(receipt: EvolvableValidationReceipt): string {
  return createHash("sha256").update(canonicalJson(receipt)).digest("hex");
}

export function buildNegativeReceipt(input: {
  mutantId: string;
  stableCode: EvfFailureCode;
  exactRefs: readonly ExactRef[];
}): NegativeControlReceipt {
  return {
    schema_version: "evf.evolvable-validation-receipt/v2",
    receipt_id: `evf.s1.negative-control.${input.mutantId}.v2`,
    receipt_class: "negative-control",
    swu_id: "SWU-GCP-001",
    exact_refs: input.exactRefs,
    positive_receipt_issued: false,
    mutant_id: input.mutantId,
    stable_code: input.stableCode,
    release_admission: "not-granted",
    claim_ceiling: "candidate-local-SWU-GCP-001-causal-proof-only",
    result: "killed",
  };
}

export function buildPositiveReceipt(input: {
  exactRefs: readonly ExactRef[];
  observations: readonly [RuntimeObservation, RuntimeObservation];
}): PositiveProofReceipt {
  return {
    schema_version: "evf.evolvable-validation-receipt/v2",
    receipt_id: "evf.s1.positive-proof.v2",
    receipt_class: "positive-proof",
    swu_id: "SWU-GCP-001",
    exact_refs: input.exactRefs,
    positive_receipt_issued: true,
    acceptance_vector: ACCEPTANCE_VECTOR,
    execution_cardinality: EXECUTION_CARDINALITY,
    runtime_observations: input.observations,
    release_admission: "not-granted",
    claim_ceiling: "candidate-local-SWU-GCP-001-causal-proof-only",
    result: "pass",
  };
}

function validRef(value: ExactRef): boolean {
  return (
    typeof value.path === "string" &&
    value.path.length > 0 &&
    /^[a-f0-9]{64}$/.test(value.sha256) &&
    Number.isInteger(value.size_bytes) &&
    value.size_bytes >= 0
  );
}

export function verifyReceipt(
  receipt: EvolvableValidationReceipt,
  expectedDigest?: string,
): void {
  if (expectedDigest && receiptDigest(receipt) !== expectedDigest) {
    fail("RECEIPT_TAMPERED", "receipt digest does not match the independently retained digest");
  }
  if (
    receipt.schema_version !== "evf.evolvable-validation-receipt/v2" ||
    receipt.swu_id !== "SWU-GCP-001" ||
    receipt.release_admission !== "not-granted" ||
    receipt.claim_ceiling !== "candidate-local-SWU-GCP-001-causal-proof-only" ||
    receipt.exact_refs.length === 0 ||
    !receipt.exact_refs.every(validRef)
  ) {
    fail("RECEIPT_TAMPERED", "receipt base contract is invalid");
  }
  if (receipt.receipt_class === "positive-proof") {
    if (
      !receipt.positive_receipt_issued ||
      receipt.result !== "pass" ||
      canonicalJson(receipt.acceptance_vector) !== canonicalJson(ACCEPTANCE_VECTOR) ||
      canonicalJson(receipt.execution_cardinality) !== canonicalJson(EXECUTION_CARDINALITY) ||
      receipt.runtime_observations.length !== 2
    ) {
      fail("RECEIPT_TAMPERED", "positive receipt contract is invalid");
    }
  } else if (
    receipt.positive_receipt_issued ||
    receipt.result !== "killed" ||
    !/^M(0[1-9]|1[0-6])-[a-z0-9-]+$/.test(receipt.mutant_id) ||
    !/^[A-Z][A-Z0-9_]+$/.test(receipt.stable_code)
  ) {
    fail("RECEIPT_TAMPERED", "negative receipt contract is invalid");
  }
}

function within(root: string, target: string): boolean {
  const rel = relative(root, target);
  return rel === "" || (rel !== ".." && !rel.startsWith("../") && !isAbsolute(rel));
}

export function verifyReceiptCurrent(
  receipt: EvolvableValidationReceipt,
  repoRoot: string,
  expectedRefs: readonly ExactRef[],
  expectedObservations?: readonly [RuntimeObservation, RuntimeObservation],
  outputRoot?: string,
): void {
  verifyReceipt(receipt);
  if (
    expectedRefs.length === 0 ||
    canonicalJson(receipt.exact_refs) !== canonicalJson(expectedRefs) ||
    (receipt.receipt_class === "positive-proof" &&
      (!expectedObservations ||
        canonicalJson(receipt.runtime_observations) !== canonicalJson(expectedObservations)))
  ) {
    fail("RECEIPT_TAMPERED", "receipt does not match the independently selected S1 evidence");
  }
  const sourceRoot = realpathSync(resolve(repoRoot));
  const evidenceRoot = outputRoot ? realpathSync(resolve(outputRoot)) : undefined;
  for (const ref of receipt.exact_refs) {
    if (isAbsolute(ref.path)) fail("ARTIFACT_STALE", "absolute receipt ref is forbidden");
    const target = resolve(sourceRoot, ref.path);
    let realTarget: string;
    try {
      realTarget = realpathSync(target);
    } catch {
      fail("ARTIFACT_STALE", `receipt ref is missing: ${ref.path}`);
    }
    if (!within(sourceRoot, realTarget) && (!evidenceRoot || !within(evidenceRoot, realTarget))) {
      fail("ARTIFACT_STALE", `receipt ref escapes selected roots: ${ref.path}`);
    }
    let observed: ExactRef;
    try {
      observed = exactRef(sourceRoot, ref.path);
    } catch {
      fail("ARTIFACT_STALE", `receipt ref is missing: ${ref.path}`);
    }
    if (observed.sha256 !== ref.sha256 || observed.size_bytes !== ref.size_bytes) {
      fail("ARTIFACT_STALE", `receipt ref is stale: ${ref.path}`);
    }
  }
}
