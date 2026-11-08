import { createHash } from "node:crypto";
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

type JsonRecord = Record<string, unknown>;
const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));

const records = (value: unknown): JsonRecord[] => Array.isArray(value)
  ? value.filter((item): item is JsonRecord => item !== null && typeof item === "object" && !Array.isArray(item))
  : [];
const normalizedObservations = (value: unknown) => records(value).map((item) => ({
  case_id: item.case_id,
  outcome: item.outcome,
  observed_effect_count: item.observed_effect_count,
})).sort((left, right) => compareUtf8(String(left.case_id), String(right.case_id)));
const normalizedSummary = (value: JsonRecord) => ({
  rule_id: value.rule_id,
  positive: records(value.positive).map((item) => ({
    case_id: item.case_id,
    status: item.status,
  })).sort((left, right) => compareUtf8(String(left.case_id), String(right.case_id))),
  mutations: records(value.mutations).map((item) => ({
    mutation_id: item.mutation_id,
    case_id: item.case_id,
    finding_code: item.finding_code,
    status: item.status,
  })).sort((left, right) => compareUtf8(String(left.mutation_id), String(right.mutation_id))),
});

export type RuleParityInput = Readonly<{
  typescript: Readonly<{ summary: JsonRecord; observations: unknown; semantic_sha256: string }>;
  python: Readonly<{ summary: JsonRecord; observations: unknown; semantic_sha256: string }>;
  rust: Readonly<{ summary: JsonRecord; observations: unknown; semantic_sha256: string }>;
}>;

export const evaluateRuleParity = async (input: RuleParityInput) => {
  const summaries = {
    typescript: normalizedSummary(input.typescript.summary),
    python: normalizedSummary(input.python.summary),
    rust: normalizedSummary(input.rust.summary),
  };
  const observations = {
    typescript: normalizedObservations(input.typescript.observations),
    python: normalizedObservations(input.python.observations),
    rust: normalizedObservations(input.rust.observations),
  };
  const baselineSummary = JSON.stringify(summaries.typescript);
  const baselineObservations = JSON.stringify(observations.typescript);
  const diagnostics: string[] = [];
  if (Object.values(summaries).some((summary) => JSON.stringify(summary) !== baselineSummary)) {
    diagnostics.push("RULE_PARITY_SEMANTIC_SUMMARY_MISMATCH");
  }
  if (Object.values(observations).some((items) => JSON.stringify(items) !== baselineObservations)) {
    diagnostics.push("RULE_PARITY_OBSERVATION_MISMATCH");
  }
  const semanticProjection = Object.freeze({
    rule_id: summaries.typescript.rule_id,
    cases: observations.typescript,
    mutations: summaries.typescript.mutations,
  });
  const body = Object.freeze({
    schema_version: "RuleSemanticParity/v1" as const,
    result: diagnostics.length === 0 ? "pass" as const : "block" as const,
    targets: Object.freeze(["typescript", "python", "rust"] as const),
    semantic_projection: semanticProjection,
    source_receipts: Object.freeze(Object.entries(input).map(([id, value]) =>
      Object.freeze({ id, semantic_sha256: value.semantic_sha256 }))),
    excluded_target_diagnostics: Object.freeze([
      "compiler paths and versions",
      "workspace identifiers",
      "source and binding digests",
      "language-specific unsupported diagnostics",
      "realization identifiers",
    ]),
    diagnostics: Object.freeze(diagnostics),
    claim_ceiling: "semantic parity for one candidate Rule across three admitted language subsets",
    authority_effect: "none" as const,
  });
  return Object.freeze({
    ...body,
    parity_sha256: sha256(JSON.stringify(body)),
  });
};

if (process.argv.includes("--write")) {
  throw Object.assign(new Error("RULE_PARITY_EXPLICIT_INPUT_OUTPUT_REQUIRED"), {
    code: "RULE_PARITY_EXPLICIT_INPUT_OUTPUT_REQUIRED",
  });
}
