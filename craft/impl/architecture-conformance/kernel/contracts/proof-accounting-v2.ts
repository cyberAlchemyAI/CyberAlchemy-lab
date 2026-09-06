export type PositiveCaseResultV2 = Readonly<{
  case_id: string;
  status: "passed" | "failed" | "unaccounted";
}>;

export type MutationResultV2 = Readonly<{
  mutation_id: string;
  status: "killed" | "survived" | "unaccounted";
  finding_code: string | null;
}>;

export type ProofAccountingInputV2 = Readonly<{
  schema_version: "ProofAccountingInput/v2";
  declared_positive_case_ids: readonly string[];
  positive_results: readonly PositiveCaseResultV2[];
  declared_mutation_ids: readonly string[];
  mutation_results: readonly MutationResultV2[];
  authority_effect: "none";
}>;

export type ProofAccountingDiagnostic =
  | "FACTORY_ACCOUNTING_POSITIVE_MISSING"
  | "FACTORY_ACCOUNTING_MUTATION_MISSING"
  | "FACTORY_ACCOUNTING_POSITIVE_DUPLICATE"
  | "FACTORY_ACCOUNTING_MUTATION_DUPLICATE"
  | "FACTORY_ACCOUNTING_POSITIVE_UNEXPECTED"
  | "FACTORY_ACCOUNTING_MUTATION_UNEXPECTED"
  | "FACTORY_ACCOUNTING_POSITIVE_UNACCOUNTED"
  | "FACTORY_ACCOUNTING_MUTATION_UNACCOUNTED"
  | "FACTORY_ACCOUNTING_POSITIVE_FAILED"
  | "FACTORY_ACCOUNTING_MUTATION_SURVIVED";

export type ProofAccountingV2 = Readonly<{
  schema_version: "ProofAccounting/v2";
  result: "pass" | "block";
  positive: Readonly<{
    declared: number;
    passed: number;
    failed: number;
    unaccounted: number;
  }>;
  mutations: Readonly<{
    declared: number;
    killed: number;
    survived: number;
    unaccounted: number;
  }>;
  diagnostics: readonly ProofAccountingDiagnostic[];
  authority_effect: "none";
}>;
