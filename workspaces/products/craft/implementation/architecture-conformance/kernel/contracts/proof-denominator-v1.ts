export type ProofDenominatorMutantV1 = Readonly<{
  mutant_id: string;
  expected_finding_code: string;
}>;

export type ProofDenominatorV1 = Readonly<{
  schema_version: "ProofDenominator/v1";
  denominator_id: string;
  owner_ref: string;
  obligation_ids: readonly string[];
  mutants: readonly ProofDenominatorMutantV1[];
  authority_effect: "none";
}>;

export type ProofDenominatorRefV1 = Readonly<{
  role: "proof-denominator";
  path: string;
  sha256: string;
}>;

export type ProofObligationEvidenceV1 = Readonly<{
  obligation_id: string;
  status: "passed" | "failed";
  observation_sha256: string;
}>;

export type ProofMutantEvidenceV1 = Readonly<{
  mutant_id: string;
  status: "killed" | "survived";
  finding_code: string | null;
  observation_sha256: string;
}>;

export type ProofEvidenceV1 = Readonly<{
  schema_version: "ProofEvidence/v1";
  denominator_ref: ProofDenominatorRefV1;
  denominator_bytes: string;
  producer_ref: string;
  obligations: readonly ProofObligationEvidenceV1[];
  mutants: readonly ProofMutantEvidenceV1[];
  authority_effect: "none";
}>;

export type VerifiedProofAccountingV1 = Readonly<{
  schema_version: "VerifiedProofAccounting/v1";
  denominator_id: string;
  denominator_ref: ProofDenominatorRefV1;
  owner_ref: string;
  producer_ref: string;
  obligations: readonly Readonly<{
    obligation_id: string;
    status: "passed";
    observation_sha256: string;
  }>[];
  mutants: readonly Readonly<{
    mutant_id: string;
    status: "killed";
    finding_code: string;
    observation_sha256: string;
  }>[];
  authority_effect: "none";
}>;
