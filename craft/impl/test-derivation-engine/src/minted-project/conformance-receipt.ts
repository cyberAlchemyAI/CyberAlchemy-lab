import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";

import {
  buildMintedProjectViews,
  verifyMintedProjectBuild,
} from "../../../tools/minted-project/views.js";

export type ConformanceCase = {
  case_id: string;
  source: string;
  expected_code: string;
  mode: "degraded";
};

export type ConformanceMatrix = {
  schema_version: "minted-project-conformance-matrix/v1";
  authority: "conformance-evidence";
  release_admission: "not-granted";
  cases: ConformanceCase[];
};

export type ConformanceCaseResult = {
  case_id: string;
  actual_code: string;
  status: "pass";
};

export type ConformanceFixtureInput = {
  id: string;
  path: string;
  root: string;
};

export type ConformanceFixtureEvidence = {
  id: string;
  path: string;
  source_set_digest: string;
  graph_digest: string;
  source_manifest_digest: string;
  markdown_digest: string;
  markdown_view_digest: string;
  build_receipt_digest: string;
  node_count: number;
  edge_count: number;
  navigation_join: "pass";
};

export type MintedProjectConformanceReceipt = {
  schema_version: "minted-project-conformance-receipt/v1";
  authority: "conformance-evidence";
  status: "pass";
  release_admission: "not-granted";
  matrix_digest: string;
  inherited_control_count: 10;
  degraded_case_count: number;
  fixtures: ConformanceFixtureEvidence[];
  case_results: ConformanceCaseResult[];
  repeat_digest: string;
};

export type ConformanceReceiptVerificationCode =
  | "RECEIPT_INVALID"
  | "CONTROL_MATRIX_MISMATCH"
  | "CONTROL_RESULT_MISMATCH"
  | "FIXTURE_UNAVAILABLE"
  | "FIXTURE_DIGEST_MISMATCH"
  | "REPEAT_DIGEST_MISMATCH";

export type ConformanceReceiptVerification = {
  status: "pass" | "fail";
  codes: ConformanceReceiptVerificationCode[];
};

function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

function canonicalize(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map(canonicalize).join(",")}]`;
  }
  if (value !== null && typeof value === "object") {
    const record = value as Record<string, unknown>;
    return `{${Object.keys(record)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonicalize(record[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

function readMatrix(path: string): { matrix: ConformanceMatrix; digest: string } {
  const bytes = readFileSync(path);
  const matrix = JSON.parse(bytes.toString("utf8")) as ConformanceMatrix;
  const ids = matrix.cases?.map((entry) => entry.case_id) ?? [];
  if (
    matrix.schema_version !== "minted-project-conformance-matrix/v1" ||
    matrix.authority !== "conformance-evidence" ||
    matrix.release_admission !== "not-granted" ||
    ids.length === 0 ||
    new Set(ids).size !== ids.length ||
    matrix.cases.some(
      (entry) =>
        entry.mode !== "degraded" ||
        typeof entry.expected_code !== "string" ||
        entry.expected_code.length === 0,
    )
  ) {
    throw new Error("conformance matrix is invalid");
  }
  return { matrix, digest: sha256(bytes) };
}

function fixtureEvidence(input: ConformanceFixtureInput): ConformanceFixtureEvidence {
  const built = buildMintedProjectViews(input.root);
  if (verifyMintedProjectBuild(input.root, built).status !== "pass") {
    throw new Error(`${input.id}: build verification failed`);
  }
  const graphIds = [
    ...built.graph.nodes.map((node) => node.node_id),
    ...built.graph.edges.map((edge) => edge.edge_id),
  ].sort();
  const manifestIds = built.sourceManifest.records.map((record) => record.graph_id).sort();
  if (JSON.stringify(graphIds) !== JSON.stringify(manifestIds)) {
    throw new Error(`${input.id}: graph-to-source navigation join failed`);
  }
  return {
    id: input.id,
    path: input.path,
    source_set_digest: built.graph.source_set_digest,
    graph_digest: sha256(built.graphBytes),
    source_manifest_digest: sha256(built.sourceManifestBytes),
    markdown_digest: sha256(built.markdownBytes),
    markdown_view_digest: sha256(built.markdownViewBytes),
    build_receipt_digest: sha256(built.buildReceiptBytes),
    node_count: built.graph.nodes.length,
    edge_count: built.graph.edges.length,
    navigation_join: "pass",
  };
}

function repeatDigest(
  matrixDigest: string,
  fixtures: ConformanceFixtureEvidence[],
  results: ConformanceCaseResult[],
): string {
  return sha256(canonicalize({ matrixDigest, fixtures, results }));
}

function orderedResults(
  matrix: ConformanceMatrix,
  results: ConformanceCaseResult[],
): ConformanceCaseResult[] {
  const resultById = new Map(results.map((entry) => [entry.case_id, entry]));
  return matrix.cases.map((entry) => {
    const result = resultById.get(entry.case_id);
    if (
      !result ||
      result.status !== "pass" ||
      result.actual_code !== entry.expected_code
    ) {
      throw new Error(`${entry.case_id}: conformance result does not match expected code`);
    }
    return result;
  });
}

export function createMintedProjectConformanceReceipt(input: {
  matrixPath: string;
  fixtures: ConformanceFixtureInput[];
  results: ConformanceCaseResult[];
}): MintedProjectConformanceReceipt {
  const { matrix, digest } = readMatrix(input.matrixPath);
  const inherited = matrix.cases.filter(
    (entry) => entry.source === "S06" || entry.source === "S08",
  ).length;
  if (inherited !== 10) {
    throw new Error(`expected 10 inherited controls, got ${inherited}`);
  }
  const fixtures = [...input.fixtures]
    .sort((left, right) => left.id.localeCompare(right.id))
    .map(fixtureEvidence);
  const results = orderedResults(matrix, input.results);
  return {
    schema_version: "minted-project-conformance-receipt/v1",
    authority: "conformance-evidence",
    status: "pass",
    release_admission: "not-granted",
    matrix_digest: digest,
    inherited_control_count: 10,
    degraded_case_count: matrix.cases.length,
    fixtures,
    case_results: results,
    repeat_digest: repeatDigest(digest, fixtures, results),
  };
}

export function verifyMintedProjectConformanceReceipt(
  receipt: MintedProjectConformanceReceipt,
  matrixPath: string,
  fixtureInputs: ConformanceFixtureInput[],
): ConformanceReceiptVerification {
  const codes = new Set<ConformanceReceiptVerificationCode>();
  if (
    receipt.schema_version !== "minted-project-conformance-receipt/v1" ||
    receipt.authority !== "conformance-evidence" ||
    receipt.status !== "pass" ||
    receipt.release_admission !== "not-granted" ||
    receipt.inherited_control_count !== 10
  ) {
    codes.add("RECEIPT_INVALID");
  }

  let matrix: ConformanceMatrix | undefined;
  let matrixDigest = "";
  try {
    const loaded = readMatrix(matrixPath);
    matrix = loaded.matrix;
    matrixDigest = loaded.digest;
    if (
      receipt.matrix_digest !== matrixDigest ||
      receipt.degraded_case_count !== matrix.cases.length
    ) {
      codes.add("CONTROL_MATRIX_MISMATCH");
    }
    try {
      orderedResults(matrix, receipt.case_results);
    } catch {
      codes.add("CONTROL_RESULT_MISMATCH");
    }
  } catch {
    codes.add("CONTROL_MATRIX_MISMATCH");
  }

  let fixtures: ConformanceFixtureEvidence[] = [];
  try {
    fixtures = [...fixtureInputs]
      .sort((left, right) => left.id.localeCompare(right.id))
      .map(fixtureEvidence);
    if (canonicalize(fixtures) !== canonicalize(receipt.fixtures)) {
      codes.add("FIXTURE_DIGEST_MISMATCH");
    }
  } catch {
    codes.add("FIXTURE_UNAVAILABLE");
  }

  if (
    matrix &&
    repeatDigest(matrixDigest, fixtures, receipt.case_results) !== receipt.repeat_digest
  ) {
    codes.add("REPEAT_DIGEST_MISMATCH");
  }
  return { status: codes.size === 0 ? "pass" : "fail", codes: [...codes].sort() };
}
