import { canonicalJson, sha256 } from "../input/source-manifest.js";
import type { RuntimeReceiptV1 } from "./contracts.js";

export interface IndependentRuntimeTarget {
  readonly target_id: string;
  readonly expected_outputs: Readonly<Record<string, unknown>>;
}

export interface RuntimeConformanceResultV1 {
  readonly schema_version: "domainspec.runtime-conformance/v1";
  readonly result: "pass" | "fail";
  readonly target_id: string;
  readonly runtime_receipt_sha256: string;
  readonly compared_step_ids: readonly string[];
  readonly mismatches: readonly string[];
  readonly authority_effect: "none";
}

export function compareIndependentRuntimeTarget(receipt: RuntimeReceiptV1, target: IndependentRuntimeTarget): RuntimeConformanceResultV1 {
  const outcomes = new Map(receipt.outcomes.map(({ step_id, output }) => [step_id, output]));
  const stepIds = Object.keys(target.expected_outputs).sort();
  const mismatches = stepIds.filter((stepId) => !outcomes.has(stepId) || sha256(canonicalJson(outcomes.get(stepId))) !== sha256(canonicalJson(target.expected_outputs[stepId])));
  return Object.freeze({ schema_version: "domainspec.runtime-conformance/v1", result: mismatches.length === 0 ? "pass" : "fail", target_id: target.target_id, runtime_receipt_sha256: receipt.receipt_sha256, compared_step_ids: Object.freeze(stepIds), mismatches: Object.freeze(mismatches), authority_effect: "none" });
}
