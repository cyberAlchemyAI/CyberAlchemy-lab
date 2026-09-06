export const BTE_DIAGNOSTICS = [
  { code: "BTE_SCHEMA_INVALID", precedence: 10, stage: "shape" },
  { code: "BTE_SCHEMA_UNSUPPORTED_KEYWORD", precedence: 20, stage: "shape" },
  { code: "BTE_LOGICAL_ID_MISSING", precedence: 30, stage: "identity" },
  { code: "BTE_LOGICAL_ID_EXTRA", precedence: 40, stage: "identity" },
  { code: "BTE_LOGICAL_ID_DUPLICATE", precedence: 50, stage: "identity" },
  { code: "BTE_DIGEST_MALFORMED", precedence: 60, stage: "digest" },
  { code: "BTE_DIGEST_MISMATCH", precedence: 70, stage: "digest" },
  { code: "BTE_CONTRACT_STALE", precedence: 80, stage: "provenance" },
  { code: "BTE_PRODUCER_MISMATCH", precedence: 90, stage: "provenance" },
  { code: "BTE_AUTHORITY_FORGED", precedence: 100, stage: "authority" },
  { code: "BTE_AUTHORITY_SUBSTITUTED", precedence: 110, stage: "authority" },
  { code: "BTE_PATH_ABSOLUTE", precedence: 120, stage: "containment" },
  { code: "BTE_PATH_TRAVERSAL", precedence: 130, stage: "containment" },
  { code: "BTE_PATH_SYMLINK_ESCAPE", precedence: 140, stage: "containment" },
  { code: "BTE_ROOT_UNDECLARED", precedence: 150, stage: "containment" },
  { code: "BTE_OUTPUT_OVERWRITE", precedence: 160, stage: "write" },
  { code: "BTE_EXACT_SET_EMPTY", precedence: 170, stage: "recomposition" },
  { code: "BTE_EXACT_SET_DUPLICATE", precedence: 180, stage: "recomposition" },
  { code: "BTE_RECOMPOSITION_MISSING", precedence: 190, stage: "recomposition" },
  { code: "BTE_RECOMPOSITION_EXTRA", precedence: 200, stage: "recomposition" },
  { code: "BTE_RECOMPOSITION_OVERLAP", precedence: 210, stage: "recomposition" },
  { code: "BTE_DIAGNOSTIC_UNKNOWN", precedence: 220, stage: "diagnostic" },
  { code: "BTE_DIAGNOSTIC_PRECEDENCE", precedence: 230, stage: "diagnostic" },
  { code: "BTE_EXPECTATION_SELF_AUTHORED", precedence: 240, stage: "expectation" },
  { code: "BTE_EXPECTATION_REWRITTEN", precedence: 250, stage: "expectation" },
] as const;

export type BteDiagnosticCode = (typeof BTE_DIAGNOSTICS)[number]["code"];
export type BteDiagnosticStage = (typeof BTE_DIAGNOSTICS)[number]["stage"];

export const BTE_DIAGNOSTIC_CODES = BTE_DIAGNOSTICS.map(({ code }) => code);

