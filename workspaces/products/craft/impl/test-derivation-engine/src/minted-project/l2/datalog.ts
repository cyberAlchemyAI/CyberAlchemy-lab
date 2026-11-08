import { digestValue, utf16Compare } from "./canonical-json.js";
import { fail, type NormalizedOutcome } from "./types.js";

export const VIOLATION_ROW_SCHEMA_DIGEST = digestValue({
  relation_name: "Violation",
  columns: [{ name: "rule_id", type: "symbol" }],
  canonical_sort: ["rule_id"],
});

export function datalogArgv(
  executable: string,
  factsDirectory: string,
  outputDirectory: string,
  queryPath: string,
): readonly string[] {
  if ([executable, factsDirectory, outputDirectory, queryPath].some((entry) => entry.length === 0)) {
    fail("PROVIDER_INPUT_DIGEST_MISMATCH", "execution", "empty Souffle invocation field");
  }
  return [executable, "-j", "1", "-F", factsDirectory, "-D", outputDirectory, queryPath];
}

export function parseViolationCsv(bytes: string): readonly string[] {
  if (bytes.startsWith("\uFEFF") || bytes.includes("\r")) {
    fail("PROVIDER_OUTPUT_INVALID", "mapping", "Violation.csv is not canonical UTF-8/LF text");
  }
  const rows = bytes.length === 0
    ? []
    : bytes.endsWith("\n")
      ? bytes.slice(0, -1).split("\n")
      : bytes.split("\n");
  if (rows.some((row) => row.length === 0 || row.includes("\t") || row.includes(","))) {
    fail("PROVIDER_OUTPUT_INVALID", "mapping", "Violation.csv row schema is invalid");
  }
  if (new Set(rows).size !== rows.length) {
    fail("PROVIDER_OUTPUT_INVALID", "mapping", "Violation.csv contains duplicate rows");
  }
  const sorted = [...rows].sort(utf16Compare);
  if (rows.some((row, index) => row !== sorted[index])) {
    fail("PROVIDER_OUTPUT_INVALID", "mapping", "Violation.csv is not canonically sorted");
  }
  return rows;
}

export function mapDatalogOutcome(
  rows: readonly string[],
  complete: boolean,
): NormalizedOutcome {
  if (!complete) return "unresolved";
  return rows.length === 0 ? "no-counterexample" : "counterexample";
}

export function datalogNativeResult(
  rows: readonly string[],
  rowsRef: { readonly path: string; readonly sha256: string; readonly size_bytes: number },
) {
  const canonicalRows = [...rows].sort(utf16Compare);
  if (new Set(canonicalRows).size !== canonicalRows.length) {
    fail("PROVIDER_OUTPUT_INVALID", "mapping", "duplicate Datalog violation row");
  }
  return {
    kind: "violation-relation" as const,
    relation_name: "Violation" as const,
    row_schema_digest: VIOLATION_ROW_SCHEMA_DIGEST,
    row_count: canonicalRows.length,
    rows_digest: digestValue(canonicalRows),
    rows_ref: rowsRef,
    complete: true as const,
  };
}
