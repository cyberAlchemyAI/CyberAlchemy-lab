export type ProofStateName =
  | "prepared"
  | "generated"
  | "compiled"
  | "observed"
  | "evaluated"
  | "mutation-killed"
  | "replayed"
  | "proof-complete"
  | "blocked";

export type ArchitectureProofReceipt = Readonly<{
  schema_version: "ArchitectureProofReceipt/v1";
  proof_id: string;
  state: "proof-complete";
  case_sha256: string;
  raw_index_sha256: string;
  positive: Readonly<{ declared: 1; passed: 1; failed: 0; unaccounted: 0 }>;
  mutations: Readonly<{ declared: 1; killed: 1; survived: 0 }>;
  exact_mutation_failure: Readonly<{
    member_id: "status.paid";
    code: "ARCH_ENUM_MEMBER_MISSING";
  }>;
  replay: Readonly<{ status: "pass"; result_sha256: string }>;
  claim_ceiling: "one candidate-local direct TypeScript Enum proof";
  authority_effect: "none";
}>;
