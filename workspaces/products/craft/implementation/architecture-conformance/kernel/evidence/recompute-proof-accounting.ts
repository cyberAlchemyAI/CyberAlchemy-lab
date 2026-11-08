import { createHash } from "node:crypto";

import type {
  ProofDenominatorRefV1,
  ProofDenominatorV1,
  ProofEvidenceV1,
  VerifiedProofAccountingV1,
} from "../contracts/proof-denominator-v1.js";

const SHA256 = /^[a-f0-9]{64}$/u;
const IDENTIFIER = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/u;
const MAX_DENOMINATOR_BYTES = 1_048_576;

const isRecord = (value: unknown): value is Record<string, unknown> =>
  value !== null && typeof value === "object" && !Array.isArray(value);

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));

const exactKeys = (value: Record<string, unknown>, keys: readonly string[]): void => {
  const expected = [...keys].sort(compareUtf8);
  const observed = Object.keys(value).sort(compareUtf8);
  if (JSON.stringify(expected) !== JSON.stringify(observed)) {
    throw new Error("FACTORY_PROOF_EVIDENCE_INVALID:closed-shape");
  }
};

const canonicalValue = (value: unknown): unknown => {
  if (Array.isArray(value)) return value.map(canonicalValue);
  if (isRecord(value)) {
    return Object.fromEntries(Object.entries(value)
      .sort(([left], [right]) => compareUtf8(left, right))
      .map(([key, child]) => [key, canonicalValue(child)]));
  }
  return value;
};

const canonicalJson = (value: unknown): string => JSON.stringify(canonicalValue(value));
const sha256 = (value: string): string => createHash("sha256").update(value).digest("hex");

const safeRelativePath = (value: string): boolean =>
  value.length > 0 && !value.startsWith("/") && !value.includes("\\") &&
  !value.split("/").some((part) => part === "" || part === "." || part === "..");

const validIdentifier = (value: unknown): value is string =>
  typeof value === "string" && IDENTIFIER.test(value);

const duplicates = (values: readonly string[]): readonly string[] => {
  const seen = new Set<string>();
  const repeated = new Set<string>();
  for (const value of values) {
    if (seen.has(value)) repeated.add(value);
    seen.add(value);
  }
  return Object.freeze([...repeated].sort(compareUtf8));
};

export const decodeProofEvidenceV1 = (value: unknown): ProofEvidenceV1 => {
  if (!isRecord(value)) throw new Error("FACTORY_PROOF_EVIDENCE_INVALID:evidence");
  exactKeys(value, [
    "schema_version",
    "denominator_ref",
    "denominator_bytes",
    "producer_ref",
    "obligations",
    "mutants",
    "authority_effect",
  ]);
  if (value.schema_version !== "ProofEvidence/v1" || value.authority_effect !== "none" ||
      typeof value.denominator_bytes !== "string" ||
      Buffer.byteLength(value.denominator_bytes, "utf8") > MAX_DENOMINATOR_BYTES ||
      !validIdentifier(value.producer_ref) || !isRecord(value.denominator_ref) ||
      !Array.isArray(value.obligations) || !Array.isArray(value.mutants)) {
    throw new Error("FACTORY_PROOF_EVIDENCE_INVALID:evidence");
  }
  exactKeys(value.denominator_ref, ["role", "path", "sha256"]);
  if (value.denominator_ref.role !== "proof-denominator" ||
      typeof value.denominator_ref.path !== "string" ||
      !safeRelativePath(value.denominator_ref.path) ||
      typeof value.denominator_ref.sha256 !== "string" ||
      !SHA256.test(value.denominator_ref.sha256)) {
    throw new Error("FACTORY_PROOF_EVIDENCE_INVALID:denominator-ref");
  }
  for (const obligation of value.obligations) {
    if (!isRecord(obligation)) throw new Error("FACTORY_PROOF_EVIDENCE_INVALID:obligation");
    exactKeys(obligation, ["obligation_id", "status", "observation_sha256"]);
    if (!validIdentifier(obligation.obligation_id) ||
        (obligation.status !== "passed" && obligation.status !== "failed") ||
        typeof obligation.observation_sha256 !== "string" ||
        !SHA256.test(obligation.observation_sha256)) {
      throw new Error("FACTORY_PROOF_EVIDENCE_INVALID:obligation");
    }
  }
  for (const mutant of value.mutants) {
    if (!isRecord(mutant)) throw new Error("FACTORY_PROOF_EVIDENCE_INVALID:mutant");
    exactKeys(mutant, ["mutant_id", "status", "finding_code", "observation_sha256"]);
    if (!validIdentifier(mutant.mutant_id) ||
        (mutant.status !== "killed" && mutant.status !== "survived") ||
        (mutant.finding_code !== null && !validIdentifier(mutant.finding_code)) ||
        typeof mutant.observation_sha256 !== "string" ||
        !SHA256.test(mutant.observation_sha256)) {
      throw new Error("FACTORY_PROOF_EVIDENCE_INVALID:mutant");
    }
  }
  return value as unknown as ProofEvidenceV1;
};

const decodeDenominator = (bytes: string): ProofDenominatorV1 => {
  let decoded: unknown;
  try {
    decoded = JSON.parse(bytes);
  } catch {
    throw new Error("FACTORY_PROOF_DENOMINATOR_INVALID:json");
  }
  if (!isRecord(decoded)) throw new Error("FACTORY_PROOF_DENOMINATOR_INVALID:denominator");
  if (canonicalJson(decoded) !== bytes) {
    throw new Error("FACTORY_PROOF_DENOMINATOR_NON_CANONICAL");
  }
  exactKeys(decoded, [
    "schema_version",
    "denominator_id",
    "owner_ref",
    "obligation_ids",
    "mutants",
    "authority_effect",
  ]);
  if (decoded.schema_version !== "ProofDenominator/v1" ||
      decoded.authority_effect !== "none" || !validIdentifier(decoded.denominator_id) ||
      !validIdentifier(decoded.owner_ref) || !Array.isArray(decoded.obligation_ids) ||
      !Array.isArray(decoded.mutants) ||
      decoded.obligation_ids.some((id) => !validIdentifier(id))) {
    throw new Error("FACTORY_PROOF_DENOMINATOR_INVALID:denominator");
  }
  for (const mutant of decoded.mutants) {
    if (!isRecord(mutant)) throw new Error("FACTORY_PROOF_DENOMINATOR_INVALID:mutant");
    exactKeys(mutant, ["mutant_id", "expected_finding_code"]);
    if (!validIdentifier(mutant.mutant_id) ||
        !validIdentifier(mutant.expected_finding_code)) {
      throw new Error("FACTORY_PROOF_DENOMINATOR_INVALID:mutant");
    }
  }
  return decoded as unknown as ProofDenominatorV1;
};

export type ProofAccountingDiagnosticV1 =
  | "FACTORY_PROOF_DENOMINATOR_INVALID"
  | "FACTORY_PROOF_DENOMINATOR_NON_CANONICAL"
  | "FACTORY_PROOF_DENOMINATOR_DIGEST_MISMATCH"
  | "FACTORY_PROOF_DENOMINATOR_REF_MISMATCH"
  | "FACTORY_PROOF_EVIDENCE_INVALID"
  | "FACTORY_PROOF_OWNER_SELF_AUTHORED"
  | "FACTORY_PROOF_PRODUCER_MISMATCH"
  | "FACTORY_PROOF_OBLIGATION_MISSING"
  | "FACTORY_PROOF_MUTANT_MISSING"
  | "FACTORY_PROOF_OBLIGATION_DUPLICATE"
  | "FACTORY_PROOF_MUTANT_DUPLICATE"
  | "FACTORY_PROOF_OBLIGATION_UNEXPECTED"
  | "FACTORY_PROOF_MUTANT_UNEXPECTED"
  | "FACTORY_PROOF_OBLIGATION_UNACCOUNTED"
  | "FACTORY_PROOF_MUTANT_UNACCOUNTED"
  | "FACTORY_PROOF_OBLIGATION_FAILED"
  | "FACTORY_PROOF_MUTANT_SURVIVED"
  | "FACTORY_PROOF_FINDING_MISMATCH";

export type ProofAccountingRecomputationV1 = Readonly<{
  schema_version: "ProofAccountingRecomputation/v1";
  result: "pass" | "block";
  totals: Readonly<{
    positives_declared: number;
    positives_passed: number;
    mutants_declared: number;
    mutants_killed: number;
  }>;
  proof: VerifiedProofAccountingV1 | null;
  diagnostics: readonly ProofAccountingDiagnosticV1[];
  authority_effect: "none";
}>;

const blocked = (
  diagnostics: ReadonlySet<ProofAccountingDiagnosticV1>,
  totals: ProofAccountingRecomputationV1["totals"] = Object.freeze({
    positives_declared: 0,
    positives_passed: 0,
    mutants_declared: 0,
    mutants_killed: 0,
  }),
): ProofAccountingRecomputationV1 => Object.freeze({
  schema_version: "ProofAccountingRecomputation/v1" as const,
  result: "block" as const,
  totals,
  proof: null,
  diagnostics: Object.freeze([...diagnostics].sort(compareUtf8)),
  authority_effect: "none" as const,
});

const contractDiagnostic = (error: unknown): ProofAccountingDiagnosticV1 => {
  const message = error instanceof Error ? error.message : "";
  if (message.startsWith("FACTORY_PROOF_DENOMINATOR_NON_CANONICAL")) {
    return "FACTORY_PROOF_DENOMINATOR_NON_CANONICAL";
  }
  if (message.startsWith("FACTORY_PROOF_DENOMINATOR_INVALID")) {
    return "FACTORY_PROOF_DENOMINATOR_INVALID";
  }
  return "FACTORY_PROOF_EVIDENCE_INVALID";
};

export const recomputeProofAccounting = (input: Readonly<{
  locked_denominator_ref: ProofDenominatorRefV1;
  provider_id: string;
  evidence: unknown;
}>): ProofAccountingRecomputationV1 => {
  let evidence: ProofEvidenceV1;
  try {
    evidence = decodeProofEvidenceV1(input.evidence);
  } catch (error) {
    return blocked(new Set([contractDiagnostic(error)]));
  }

  const diagnostics = new Set<ProofAccountingDiagnosticV1>();
  if (evidence.denominator_ref.role !== input.locked_denominator_ref.role ||
      evidence.denominator_ref.path !== input.locked_denominator_ref.path ||
      evidence.denominator_ref.sha256 !== input.locked_denominator_ref.sha256) {
    diagnostics.add("FACTORY_PROOF_DENOMINATOR_REF_MISMATCH");
  }
  if (sha256(evidence.denominator_bytes) !== input.locked_denominator_ref.sha256) {
    diagnostics.add("FACTORY_PROOF_DENOMINATOR_DIGEST_MISMATCH");
  }
  if (evidence.producer_ref !== input.provider_id) {
    diagnostics.add("FACTORY_PROOF_PRODUCER_MISMATCH");
  }

  let denominator: ProofDenominatorV1;
  try {
    denominator = decodeDenominator(evidence.denominator_bytes);
  } catch (error) {
    diagnostics.add(contractDiagnostic(error));
    return blocked(diagnostics);
  }
  if (denominator.owner_ref === input.provider_id) {
    diagnostics.add("FACTORY_PROOF_OWNER_SELF_AUTHORED");
  }

  const denominatorObligations = denominator.obligation_ids;
  const denominatorMutants = denominator.mutants.map(({ mutant_id: id }) => id);
  const evidenceObligations = evidence.obligations.map(({ obligation_id: id }) => id);
  const evidenceMutants = evidence.mutants.map(({ mutant_id: id }) => id);
  const denominatorObligationSet = new Set(denominatorObligations);
  const denominatorMutantSet = new Set(denominatorMutants);
  const evidenceObligationSet = new Set(evidenceObligations);
  const evidenceMutantSet = new Set(evidenceMutants);

  if (denominatorObligations.length === 0) diagnostics.add("FACTORY_PROOF_OBLIGATION_MISSING");
  if (denominatorMutants.length === 0) diagnostics.add("FACTORY_PROOF_MUTANT_MISSING");
  if (duplicates(denominatorObligations).length > 0 ||
      duplicates(evidenceObligations).length > 0) {
    diagnostics.add("FACTORY_PROOF_OBLIGATION_DUPLICATE");
  }
  if (duplicates(denominatorMutants).length > 0 || duplicates(evidenceMutants).length > 0) {
    diagnostics.add("FACTORY_PROOF_MUTANT_DUPLICATE");
  }
  if (evidenceObligations.some((id) => !denominatorObligationSet.has(id))) {
    diagnostics.add("FACTORY_PROOF_OBLIGATION_UNEXPECTED");
  }
  if (evidenceMutants.some((id) => !denominatorMutantSet.has(id))) {
    diagnostics.add("FACTORY_PROOF_MUTANT_UNEXPECTED");
  }
  if (denominatorObligations.some((id) => !evidenceObligationSet.has(id))) {
    diagnostics.add("FACTORY_PROOF_OBLIGATION_UNACCOUNTED");
  }
  if (denominatorMutants.some((id) => !evidenceMutantSet.has(id))) {
    diagnostics.add("FACTORY_PROOF_MUTANT_UNACCOUNTED");
  }
  if (evidence.obligations.some(({ status }) => status === "failed")) {
    diagnostics.add("FACTORY_PROOF_OBLIGATION_FAILED");
  }
  if (evidence.mutants.some(({ status }) => status === "survived")) {
    diagnostics.add("FACTORY_PROOF_MUTANT_SURVIVED");
  }
  const expectedFinding = new Map(denominator.mutants.map((mutant) =>
    [mutant.mutant_id, mutant.expected_finding_code] as const));
  if (evidence.mutants.some((mutant) =>
    expectedFinding.has(mutant.mutant_id) &&
    mutant.finding_code !== expectedFinding.get(mutant.mutant_id))) {
    diagnostics.add("FACTORY_PROOF_FINDING_MISMATCH");
  }

  const totals = Object.freeze({
    positives_declared: denominatorObligationSet.size,
    positives_passed: evidence.obligations.filter(({ status, obligation_id: id }) =>
      status === "passed" && denominatorObligationSet.has(id)).length,
    mutants_declared: denominatorMutantSet.size,
    mutants_killed: evidence.mutants.filter(({ status, mutant_id: id }) =>
      status === "killed" && denominatorMutantSet.has(id)).length,
  });
  if (diagnostics.size > 0) return blocked(diagnostics, totals);

  const obligationById = new Map(evidence.obligations.map((item) =>
    [item.obligation_id, item] as const));
  const mutantById = new Map(evidence.mutants.map((item) => [item.mutant_id, item] as const));
  const proof: VerifiedProofAccountingV1 = Object.freeze({
    schema_version: "VerifiedProofAccounting/v1" as const,
    denominator_id: denominator.denominator_id,
    denominator_ref: Object.freeze({ ...evidence.denominator_ref }),
    owner_ref: denominator.owner_ref,
    producer_ref: evidence.producer_ref,
    obligations: Object.freeze(denominatorObligations.map((id) => {
      const item = obligationById.get(id)!;
      return Object.freeze({
        obligation_id: id,
        status: "passed" as const,
        observation_sha256: item.observation_sha256,
      });
    })),
    mutants: Object.freeze(denominator.mutants.map(({ mutant_id: id }) => {
      const item = mutantById.get(id)!;
      return Object.freeze({
        mutant_id: id,
        status: "killed" as const,
        finding_code: expectedFinding.get(id)!,
        observation_sha256: item.observation_sha256,
      });
    })),
    authority_effect: "none" as const,
  });
  return Object.freeze({
    schema_version: "ProofAccountingRecomputation/v1" as const,
    result: "pass" as const,
    totals,
    proof,
    diagnostics: Object.freeze([]),
    authority_effect: "none" as const,
  });
};
