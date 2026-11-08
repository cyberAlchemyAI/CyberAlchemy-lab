import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { join, resolve } from "node:path";

import type { UiProfile, UiProfileConcept } from "../validate-ui-profile";

type JsonRecord = Record<string, unknown>;

export const UI_SYNTHETIC_SCHEMA_VERSION = "domainspec-ui-synthetic-corpus/v0.1";
export const UI_SYNTHETIC_FIXTURE_CLASSES = [
  "positive",
  "nearest-neighbor",
  "malformed",
  "label-erased",
  "criterion-erased",
  "changed-consequence",
] as const;

export type SyntheticFixtureClass = (typeof UI_SYNTHETIC_FIXTURE_CLASSES)[number];
export type SyntheticOutcomeCode =
  | "ACCEPTED"
  | "ATTRIBUTE-MISSING"
  | "ATTRIBUTE-EMPTY"
  | "ATTRIBUTE-WHITESPACE"
  | "FIXED-VALUE-MISMATCH"
  | "PLACEMENT-INVALID"
  | "CONSEQUENCE-MISMATCH"
  | "LABEL-MISMATCH"
  | "LABEL-MISSING";

type SyntheticCase = {
  case_id: string;
  fixture_class: SyntheticFixtureClass;
  expected: "accept" | "reject";
  expected_code: SyntheticOutcomeCode;
  payload: JsonRecord;
};

type SyntheticSpecimen = {
  schema_version: string;
  concept_id: string;
  term: string;
  representation: string;
  cases: SyntheticCase[];
};

type SyntheticManifest = {
  schema_version: string;
  corpus_id: string;
  corpus_kind: string;
  evidence_claim: string;
  generator_provenance: JsonRecord;
  concepts: Array<{ id: string; file: string }>;
};

export type SyntheticMatrixCell = {
  concept_id: string;
  term: string;
  fixture_class: SyntheticFixtureClass;
  case_id: string;
  expected: "accept" | "reject";
  expected_code: SyntheticOutcomeCode;
  actual: "accept" | "reject";
  actual_code: SyntheticOutcomeCode;
  match: boolean;
};

export type SyntheticCorpusReport = {
  schema_version: typeof UI_SYNTHETIC_SCHEMA_VERSION;
  corpus_id: string;
  corpus_kind: "synthetic-calibration";
  concepts: number;
  fixture_classes: number;
  cells: number;
  accepted: number;
  rejected: number;
  mismatches: number;
  digest: string;
  matrix: SyntheticMatrixCell[];
};

export class SyntheticCorpusError extends Error {
  constructor(readonly code: string, message: string) {
    super(`${code}: ${message}`);
    this.name = "SyntheticCorpusError";
  }
}

type Criterion = { rule: string; key: string; value?: string };

export function validateSyntheticCorpus(
  root: string,
  profile: UiProfile,
  schemaRoot: string,
): SyntheticCorpusReport {
  const manifest = parseJson<SyntheticManifest>(join(root, "manifest.json"));
  if (manifest.schema_version !== UI_SYNTHETIC_SCHEMA_VERSION) {
    fail("SYNTHETIC-MANIFEST-INVALID", `unknown schema_version ${manifest.schema_version}`);
  }
  if (
    manifest.corpus_kind !== "synthetic-calibration" ||
    manifest.evidence_claim !== "mechanical-calibration-only"
  ) {
    fail(
      "SYNTHETIC-PROVENANCE-INVALID",
      "corpus must declare synthetic-calibration and mechanical-calibration-only",
    );
  }
  const provenance = record(manifest.generator_provenance, "generator_provenance");
  if (provenance.kind !== "preregistered-synthetic" || typeof provenance.source !== "string") {
    fail("SYNTHETIC-PROVENANCE-INVALID", "generator provenance must be explicit and local");
  }
  if (!Array.isArray(manifest.concepts)) {
    fail("SYNTHETIC-MANIFEST-INVALID", "manifest concepts must be an array");
  }

  const profileById = new Map(profile.concepts.map((concept) => [concept.id, concept]));
  const manifestIds = manifest.concepts.map((entry) => entry.id);
  if (
    manifestIds.length !== profile.concepts.length ||
    new Set(manifestIds).size !== manifestIds.length ||
    profile.concepts.some((concept) => !manifestIds.includes(concept.id))
  ) {
    fail("SYNTHETIC-CENSUS-MISMATCH", "manifest must cover each profile concept exactly once");
  }

  const matrix: SyntheticMatrixCell[] = [];
  const caseIds = new Set<string>();
  for (const entry of manifest.concepts) {
    if (!entry.file || entry.file.includes("..") || resolve(root, entry.file) === resolve(root)) {
      fail("SYNTHETIC-MANIFEST-INVALID", `${entry.id} has an invalid specimen path`);
    }
    const concept = profileById.get(entry.id);
    if (concept === undefined) fail("SYNTHETIC-CENSUS-MISMATCH", `${entry.id} is not in the profile`);
    const specimen = parseJson<SyntheticSpecimen>(join(root, entry.file));
    validateSpecimenHeader(specimen, concept);
    const classes = specimen.cases.map((item) => item.fixture_class);
    if (
      classes.length !== UI_SYNTHETIC_FIXTURE_CLASSES.length ||
      new Set(classes).size !== classes.length ||
      UI_SYNTHETIC_FIXTURE_CLASSES.some((fixtureClass) => !classes.includes(fixtureClass))
    ) {
      fail("SYNTHETIC-CLASS-MISSING", `${concept.id} must contain each fixture class exactly once`);
    }
    for (const fixture of specimen.cases) {
      if (caseIds.has(fixture.case_id) || !fixture.case_id.startsWith(`${concept.id}.`)) {
        fail(
          "SYNTHETIC-EVIDENCE-POOLING",
          `${fixture.case_id} is reused or not owned by ${concept.id}`,
        );
      }
      caseIds.add(fixture.case_id);
      const actualCode = validateFixture(fixture, concept, schemaRoot);
      const actual = actualCode === "ACCEPTED" ? "accept" : "reject";
      const match = actual === fixture.expected && actualCode === fixture.expected_code;
      matrix.push({
        concept_id: concept.id,
        term: concept.term,
        fixture_class: fixture.fixture_class,
        case_id: fixture.case_id,
        expected: fixture.expected,
        expected_code: fixture.expected_code,
        actual,
        actual_code: actualCode,
        match,
      });
    }
  }

  const mismatches = matrix.filter((cell) => !cell.match);
  if (mismatches.length > 0) {
    const first = mismatches[0]!;
    fail(
      "SYNTHETIC-EXPECTATION-MISMATCH",
      `${first.case_id} expected ${first.expected}/${first.expected_code} got ${first.actual}/${first.actual_code}`,
    );
  }
  const digest = createHash("sha256").update(canonicalJson(matrix)).digest("hex");
  return {
    schema_version: UI_SYNTHETIC_SCHEMA_VERSION,
    corpus_id: manifest.corpus_id,
    corpus_kind: "synthetic-calibration",
    concepts: profile.concepts.length,
    fixture_classes: UI_SYNTHETIC_FIXTURE_CLASSES.length,
    cells: matrix.length,
    accepted: matrix.filter((cell) => cell.actual === "accept").length,
    rejected: matrix.filter((cell) => cell.actual === "reject").length,
    mismatches: 0,
    digest,
    matrix,
  };
}

function validateSpecimenHeader(specimen: SyntheticSpecimen, concept: UiProfileConcept): void {
  if (
    specimen.schema_version !== UI_SYNTHETIC_SCHEMA_VERSION ||
    specimen.concept_id !== concept.id ||
    specimen.term !== concept.term ||
    specimen.representation !== concept.representation ||
    !Array.isArray(specimen.cases)
  ) {
    fail("SYNTHETIC-CENSUS-MISMATCH", `${concept.id} specimen header disagrees with profile`);
  }
}

function validateFixture(
  fixture: SyntheticCase,
  concept: UiProfileConcept,
  schemaRoot: string,
): SyntheticOutcomeCode {
  if (!fixture || typeof fixture !== "object" || !UI_SYNTHETIC_FIXTURE_CLASSES.includes(fixture.fixture_class)) {
    fail("SYNTHETIC-MANIFEST-INVALID", `${concept.id} contains a malformed case`);
  }
  const payload = record(fixture.payload, fixture.case_id);
  const declaredTerm = payload.declared_term;
  if (declaredTerm === undefined) {
    if (fixture.fixture_class !== "label-erased") return "LABEL-MISSING";
  } else if (declaredTerm !== concept.term) {
    return "LABEL-MISMATCH";
  }

  let code: SyntheticOutcomeCode;
  if (concept.representation === "node") {
    const schema = resolve(schemaRoot, `${slug(concept.term)}.schema.yml`);
    code = validateNodeAttributes(payload.attributes, loadCriteria(schema));
  } else if (concept.representation === "alias") {
    code = validateAdapter(payload.attributes);
  } else if (concept.representation === "split") {
    code = validateStateSplit(payload.branches);
  } else {
    code = "PLACEMENT-INVALID";
  }
  if (code !== "ACCEPTED") return code;
  const expectedConsequence =
    concept.representation === "node"
      ? `construct:${concept.term}`
      : concept.representation === "alias"
        ? "normalize:Mapping"
        : "emit:domain-state-projection+async-request-component-role";
  return payload.consequence === expectedConsequence ? "ACCEPTED" : "CONSEQUENCE-MISMATCH";
}

function validateNodeAttributes(input: unknown, criteria: Criterion[]): SyntheticOutcomeCode {
  const attributes = input !== null && typeof input === "object" && !Array.isArray(input)
    ? (input as JsonRecord)
    : {};
  for (const criterion of criteria) {
    if (!Object.hasOwn(attributes, criterion.key)) return "ATTRIBUTE-MISSING";
    const value = attributes[criterion.key];
    if (typeof value !== "string") return "ATTRIBUTE-EMPTY";
    if (value.length === 0) return "ATTRIBUTE-EMPTY";
    if (value.trim().length === 0) return "ATTRIBUTE-WHITESPACE";
    if (
      criterion.rule === "attribute-equals" &&
      value.trim().toLowerCase() !== (criterion.value ?? "").toLowerCase()
    ) {
      return "FIXED-VALUE-MISMATCH";
    }
  }
  return "ACCEPTED";
}

function validateAdapter(input: unknown): SyntheticOutcomeCode {
  const attributes = input !== null && typeof input === "object" && !Array.isArray(input)
    ? (input as JsonRecord)
    : {};
  for (const key of ["source_shape", "target_shape", "direction", "field_mapping"]) {
    if (!Object.hasOwn(attributes, key)) return "ATTRIBUTE-MISSING";
    const value = attributes[key];
    if (typeof value !== "string" || value.trim() === "") return "ATTRIBUTE-EMPTY";
  }
  return attributes.direction === "outbound" ? "ACCEPTED" : "PLACEMENT-INVALID";
}

function validateStateSplit(input: unknown): SyntheticOutcomeCode {
  if (!Array.isArray(input) || input.length !== 2) return "PLACEMENT-INVALID";
  const normalized = input
    .map((value) => {
      const branch = value !== null && typeof value === "object" ? (value as JsonRecord) : {};
      return `${branch.branch_id}|${branch.representation}|${branch.target}`;
    })
    .sort();
  const expected = [
    "async-request-indicator|role|DS-D1.17",
    "domain-state-indicator|projection|DS-D1.14",
  ];
  return JSON.stringify(normalized) === JSON.stringify(expected) ? "ACCEPTED" : "PLACEMENT-INVALID";
}

function loadCriteria(path: string): Criterion[] {
  const lines = readFileSync(path, "utf8").split(/\r?\n/);
  const criteria: Criterion[] = [];
  let inCriteria = false;
  let current: Partial<Criterion> | undefined;
  for (const line of lines) {
    if (line === "criterion:") {
      inCriteria = true;
      continue;
    }
    if (inCriteria && /^\S/.test(line) && line.trim() !== "") break;
    if (!inCriteria) continue;
    const criterionName = line.match(/^  ([a-z_]+):\s*$/)?.[1];
    if (criterionName) {
      if (current?.rule && current.key) criteria.push(current as Criterion);
      current = {};
      continue;
    }
    const field = line.match(/^    (rule|key|value):\s*(.+?)\s*$/);
    if (field && current) current[field[1] as "rule" | "key" | "value"] = unquote(field[2]!);
  }
  if (current?.rule && current.key) criteria.push(current as Criterion);
  return criteria;
}

function slug(term: string): string {
  return term.toLowerCase().replace(/\s+/g, "-");
}

function parseJson<T>(path: string): T {
  try {
    return JSON.parse(readFileSync(path, "utf8")) as T;
  } catch (error) {
    fail(
      "SYNTHETIC-MANIFEST-INVALID",
      `${path} is not valid JSON-formatted YAML: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
}

function record(value: unknown, where: string): JsonRecord {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    fail("SYNTHETIC-MANIFEST-INVALID", `${where} must be an object`);
  }
  return value as JsonRecord;
}

function unquote(value: string): string {
  return (value.startsWith('"') && value.endsWith('"')) ||
    (value.startsWith("'") && value.endsWith("'"))
    ? value.slice(1, -1)
    : value;
}

function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (value !== null && typeof value === "object") {
    return `{${Object.entries(value as JsonRecord)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([key, item]) => `${JSON.stringify(key)}:${canonicalJson(item)}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

function fail(code: string, message: string): never {
  throw new SyntheticCorpusError(code, message);
}
