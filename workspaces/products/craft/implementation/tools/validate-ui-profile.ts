#!/usr/bin/env tsx

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  type SyntheticCorpusReport,
  validateSyntheticCorpus,
} from "./lib/ui-profile-synthetic";

export const UI_PROFILE_SCHEMA_VERSION = "domainspec-ui-profile/v0.1";
export const UI_PROFILE_REPRESENTATIONS = [
  "node",
  "role",
  "relationship",
  "projection",
  "alias",
  "split",
] as const;

export const UI_PROFILE_VIOLATION_CODES = [
  "PROFILE-PARSE-ERROR",
  "PROFILE-SCHEMA-VERSION",
  "PROFILE-AUTHORITY-LEAK",
  "PROFILE-ID-DUPLICATE",
  "PROFILE-ID-MISSING",
  "PROFILE-ID-UNEXPECTED",
  "PROFILE-TERM-MISMATCH",
  "PROFILE-AVAILABILITY-INVALID",
  "PROFILE-REPRESENTATION-UNKNOWN",
  "PROFILE-CONFIDENCE-INVALID",
  "PROFILE-CONCEPT-SHAPE-INVALID",
  "PROFILE-FORMATION-CONTRACT-MISSING",
  "PROFILE-ALIAS-TARGET-INVALID",
  "PROFILE-ALIAS-CYCLE",
  "PROFILE-SPLIT-BRANCH-INVALID",
  "PROFILE-BINDING-CONSTRAINT-INVALID",
  "PROFILE-DESIGN-MISMATCH",
] as const;

export type UiProfileViolationCode = (typeof UI_PROFILE_VIOLATION_CODES)[number];
type JsonRecord = Record<string, unknown>;

type Target = { id: string; term: string };
type Branch = {
  branch_id: string;
  term: string;
  representation: string;
  target: Target;
};

export type UiProfileConcept = {
  id: string;
  term: string;
  availability: string;
  representation: string;
  confidence: string;
  authority_status: string;
  formation_contract?: string;
  constraints?: string[];
  node_condition?: string;
  canonical_target?: Target;
  alias_semantics?: string;
  branches?: Branch[];
};

export type UiProfile = {
  schema_version: string;
  profile_id: string;
  status: string;
  authority_effect: string;
  design_source: string;
  representation_vocabulary: string[];
  concepts: UiProfileConcept[];
};

export type UiProfileValidation = {
  profile: UiProfile;
  digest: string;
  conceptCount: number;
  representationCounts: Record<string, number>;
};

export class UiProfileValidationError extends Error {
  constructor(
    readonly code: UiProfileViolationCode,
    message: string,
  ) {
    super(`${code}: ${message}`);
    this.name = "UiProfileValidationError";
  }
}

const EXPECTED_TERMS = new Map<string, string>([
  ["DS-D1.15", "Page"],
  ["DS-D1.16", "Layout"],
  ["DS-D1.17", "Component"],
  ["DS-D1.18", "View Model"],
  ["DS-D1.19", "Hook"],
  ["DS-D1.20", "Form"],
  ["DS-D1.21", "Action"],
  ["DS-D1.22", "Guard"],
  ["DS-D1.23", "Binding"],
  ["DS-D1.24", "Adapter"],
  ["DS-D1.25", "State Indicator"],
]);

const CONFIDENCE_VALUES = new Set([
  "unmeasured",
  "mechanically-supported",
  "empirically-provisional",
  "empirically-supported",
]);
const REPRESENTATIONS = new Set<string>(UI_PROFILE_REPRESENTATIONS);
const PROFILE_REPRESENTATIONS = new Set(["node", "alias", "split"]);
const BRANCH_REPRESENTATIONS = new Set(["role", "relationship", "projection"]);
const BASE_KEYS = [
  "id",
  "term",
  "availability",
  "representation",
  "confidence",
  "authority_status",
];

export function parseUiProfile(raw: string, where = "profile.yml"): UiProfile {
  try {
    return JSON.parse(raw) as UiProfile;
  } catch (error) {
    fail(
      "PROFILE-PARSE-ERROR",
      `${where} must be JSON-formatted YAML: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
}

export function loadActiveMetaTypes(path: string): Map<string, string> {
  const raw = readFileSync(path, "utf8");
  const active = new Map<string, string>();
  const starts = [...raw.matchAll(/^  - id: (DS-D1\.[0-9]+)\s*$/gm)];
  for (let index = 0; index < starts.length; index += 1) {
    const match = starts[index]!;
    const id = match[1] ?? "";
    const start = (match.index ?? 0) + match[0].length;
    const end = starts[index + 1]?.index ?? raw.length;
    const body = raw.slice(start, end);
    const term = body.match(/^    term: (.+?)\s*$/m)?.[1];
    const status = body.match(/^    status: (.+?)\s*$/m)?.[1];
    if (id && term && status === "active") active.set(id, term);
  }
  return active;
}

export function validateUiProfile(
  input: unknown,
  options: { activeMetaTypes: Map<string, string>; design?: unknown },
): UiProfileValidation {
  const root = record(input, "profile");
  assertAllowedKeys(
    root,
    [
      "schema_version",
      "profile_id",
      "status",
      "authority_effect",
      "design_source",
      "representation_vocabulary",
      "concepts",
    ],
    "profile",
  );
  if (root.schema_version !== UI_PROFILE_SCHEMA_VERSION) {
    fail("PROFILE-SCHEMA-VERSION", `expected ${UI_PROFILE_SCHEMA_VERSION}`);
  }
  if (
    root.profile_id !== "ui-development" ||
    root.status !== "development-only" ||
    root.authority_effect !== "none"
  ) {
    fail(
      "PROFILE-AUTHORITY-LEAK",
      "profile must remain ui-development, development-only, with authority_effect=none",
    );
  }
  if (typeof root.design_source !== "string" || root.design_source.trim() === "") {
    fail("PROFILE-CONCEPT-SHAPE-INVALID", "design_source must be nonempty");
  }

  const vocabulary = stringArray(root.representation_vocabulary, "representation_vocabulary");
  const vocabularySet = new Set(vocabulary);
  if (
    vocabulary.length !== UI_PROFILE_REPRESENTATIONS.length ||
    vocabularySet.size !== vocabulary.length ||
    UI_PROFILE_REPRESENTATIONS.some((item) => !vocabularySet.has(item))
  ) {
    fail(
      "PROFILE-REPRESENTATION-UNKNOWN",
      `representation_vocabulary must be exactly ${UI_PROFILE_REPRESENTATIONS.join(", ")}`,
    );
  }

  if (!Array.isArray(root.concepts)) {
    fail("PROFILE-CONCEPT-SHAPE-INVALID", "concepts must be an array");
  }
  const concepts = root.concepts.map((value, index) =>
    validateConcept(value, index, options.activeMetaTypes),
  );
  const ids = concepts.map((concept) => concept.id);
  const duplicates = [...new Set(ids.filter((id, index) => ids.indexOf(id) !== index))];
  if (duplicates.length > 0) {
    fail("PROFILE-ID-DUPLICATE", `duplicate concept IDs: ${duplicates.join(", ")}`);
  }
  const missing = [...EXPECTED_TERMS.keys()].filter((id) => !ids.includes(id));
  if (missing.length > 0) {
    fail("PROFILE-ID-MISSING", `missing required concept IDs: ${missing.join(", ")}`);
  }
  const unexpected = ids.filter((id) => !EXPECTED_TERMS.has(id));
  if (unexpected.length > 0) {
    fail("PROFILE-ID-UNEXPECTED", `unexpected concept IDs: ${unexpected.join(", ")}`);
  }

  const conceptMap = new Map(concepts.map((concept) => [concept.id, concept]));
  validateAliasTargets(concepts, conceptMap, options.activeMetaTypes);
  validateSplitTargets(concepts, conceptMap, options.activeMetaTypes);

  const profile = root as unknown as UiProfile;
  if (options.design !== undefined) validateDesignAgreement(profile, options.design);

  const representationCounts: Record<string, number> = {};
  for (const concept of concepts) {
    representationCounts[concept.representation] =
      (representationCounts[concept.representation] ?? 0) + 1;
  }
  return {
    profile,
    digest: digestUiProfile(profile),
    conceptCount: concepts.length,
    representationCounts,
  };
}

function validateConcept(
  input: unknown,
  index: number,
  activeMetaTypes: Map<string, string>,
): UiProfileConcept {
  const where = `concepts[${index}]`;
  const concept = record(input, where);
  const representation = textField(concept, "representation", where);
  if (!REPRESENTATIONS.has(representation) || !PROFILE_REPRESENTATIONS.has(representation)) {
    fail("PROFILE-REPRESENTATION-UNKNOWN", `${where} has unknown profile representation ${representation}`);
  }
  const allowed =
    representation === "node"
      ? [...BASE_KEYS, "formation_contract", "constraints", "node_condition"]
      : representation === "alias"
        ? [...BASE_KEYS, "canonical_target", "alias_semantics"]
        : [...BASE_KEYS, "branches"];
  assertAllowedKeys(concept, allowed, where);

  const id = textField(concept, "id", where);
  const term = textField(concept, "term", where);
  const availability = textField(concept, "availability", where);
  const confidence = textField(concept, "confidence", where);
  const authorityStatus = textField(concept, "authority_status", where);
  const expectedTerm = EXPECTED_TERMS.get(id);
  if (expectedTerm !== undefined && term !== expectedTerm) {
    fail("PROFILE-TERM-MISMATCH", `${id} must be named ${expectedTerm}, got ${term}`);
  }
  if (availability !== "required-by-design") {
    fail("PROFILE-AVAILABILITY-INVALID", `${id} must remain required-by-design`);
  }
  if (!CONFIDENCE_VALUES.has(confidence)) {
    fail("PROFILE-CONFIDENCE-INVALID", `${id} has unknown confidence ${confidence}`);
  }
  if (authorityStatus !== "development-only") {
    fail("PROFILE-AUTHORITY-LEAK", `${id} authority_status must remain development-only`);
  }

  if (representation === "node") {
    const formation = concept.formation_contract;
    if (
      typeof formation !== "string" ||
      !/^spec\/meta-types\/ui\/.+\.schema\.yml$/.test(formation)
    ) {
      fail("PROFILE-FORMATION-CONTRACT-MISSING", `${id} must name a UI formation contract`);
    }
    if (concept.constraints !== undefined) {
      const constraints = stringArray(concept.constraints, `${where}.constraints`);
      if (constraints.length !== new Set(constraints).size) {
        fail("PROFILE-CONCEPT-SHAPE-INVALID", `${id} constraints must be unique`);
      }
    }
    if (id === "DS-D1.23" && concept.node_condition !== "durable-record-required") {
      fail(
        "PROFILE-BINDING-CONSTRAINT-INVALID",
        "Binding may be a node only when node_condition=durable-record-required",
      );
    }
  }
  if (representation === "alias") {
    target(concept.canonical_target, `${where}.canonical_target`);
    textField(concept, "alias_semantics", where);
  }
  if (representation === "split") {
    validateBranches(concept.branches, where);
  }

  void activeMetaTypes;
  return concept as unknown as UiProfileConcept;
}

function validateBranches(input: unknown, where: string): Branch[] {
  if (!Array.isArray(input) || input.length < 2) {
    fail("PROFILE-SPLIT-BRANCH-INVALID", `${where}.branches must contain at least two branches`);
  }
  const branches = input.map((value, index) => {
    const branchWhere = `${where}.branches[${index}]`;
    const branch = record(value, branchWhere);
    assertAllowedKeys(branch, ["branch_id", "term", "representation", "target"], branchWhere);
    const branchId = textField(branch, "branch_id", branchWhere);
    if (!/^[a-z][a-z0-9-]*$/.test(branchId)) {
      fail("PROFILE-SPLIT-BRANCH-INVALID", `${branchWhere}.branch_id is invalid`);
    }
    const representation = textField(branch, "representation", branchWhere);
    if (!BRANCH_REPRESENTATIONS.has(representation)) {
      fail("PROFILE-SPLIT-BRANCH-INVALID", `${branchWhere} has invalid branch representation ${representation}`);
    }
    return {
      branch_id: branchId,
      term: textField(branch, "term", branchWhere),
      representation,
      target: target(branch.target, `${branchWhere}.target`),
    };
  });
  for (const key of [
    (branch: Branch) => branch.branch_id,
    (branch: Branch) => branch.term,
  ]) {
    const values = branches.map(key);
    if (new Set(values).size !== values.length) {
      fail("PROFILE-SPLIT-BRANCH-INVALID", `${where}.branches must have unique IDs and terms`);
    }
  }
  return branches;
}

function validateAliasTargets(
  concepts: UiProfileConcept[],
  conceptMap: Map<string, UiProfileConcept>,
  activeMetaTypes: Map<string, string>,
): void {
  const aliases = new Map(
    concepts
      .filter((concept) => concept.representation === "alias")
      .map((concept) => [concept.id, concept.canonical_target as Target]),
  );
  for (const [start, initialTarget] of aliases) {
    const seen = new Set([start]);
    let current = initialTarget;
    while (aliases.has(current.id)) {
      if (seen.has(current.id)) {
        fail("PROFILE-ALIAS-CYCLE", `alias cycle detected from ${start} through ${current.id}`);
      }
      seen.add(current.id);
      current = aliases.get(current.id) as Target;
    }
    const activeTerm = activeMetaTypes.get(current.id);
    if (activeTerm === undefined || activeTerm !== current.term) {
      const profileTarget = conceptMap.get(current.id);
      const detail = profileTarget
        ? `${current.id} ${current.term} is profile-local but not an active canonical kind`
        : `${current.id} ${current.term} is not an active canonical kind`;
      fail("PROFILE-ALIAS-TARGET-INVALID", detail);
    }
  }
}

function validateSplitTargets(
  concepts: UiProfileConcept[],
  conceptMap: Map<string, UiProfileConcept>,
  activeMetaTypes: Map<string, string>,
): void {
  for (const concept of concepts.filter((entry) => entry.representation === "split")) {
    for (const branch of concept.branches ?? []) {
      const profileTerm = conceptMap.get(branch.target.id)?.term;
      const activeTerm = activeMetaTypes.get(branch.target.id);
      if (profileTerm !== branch.target.term && activeTerm !== branch.target.term) {
        fail(
          "PROFILE-SPLIT-BRANCH-INVALID",
          `${concept.id} branch ${branch.branch_id} target ${branch.target.id} ${branch.target.term} is unresolved`,
        );
      }
    }
  }
}

export function validateDesignAgreement(profile: UiProfile, designInput: unknown): void {
  const design = record(designInput, "design");
  if (!Array.isArray(design.concepts)) {
    fail("PROFILE-DESIGN-MISMATCH", "design concepts must be an array");
  }
  const designById = new Map(
    design.concepts.map((value, index) => {
      const item = record(value, `design.concepts[${index}]`);
      return [textField(item, "id", `design.concepts[${index}]`), item] as const;
    }),
  );
  for (const concept of profile.concepts) {
    const expected = designById.get(concept.id);
    if (expected === undefined) {
      fail("PROFILE-DESIGN-MISMATCH", `${concept.id} is missing from the approved design`);
    }
    const pairs: Array<[string, unknown, unknown]> = [
      ["term", concept.term, expected.term],
      ["availability", concept.availability, expected.availability],
      ["representation", concept.representation, expected.representation_proposal],
      ["confidence", concept.confidence, expected.confidence],
    ];
    for (const [field, actual, wanted] of pairs) {
      if (actual !== wanted) {
        fail(
          "PROFILE-DESIGN-MISMATCH",
          `${concept.id} ${field} differs: profile=${String(actual)} design=${String(wanted)}`,
        );
      }
    }
    if (concept.representation === "alias") {
      const actual = `${concept.canonical_target?.id} ${concept.canonical_target?.term}`;
      if (actual !== expected.canonical_target) {
        fail("PROFILE-DESIGN-MISMATCH", `${concept.id} canonical target differs from design`);
      }
    }
    if (concept.representation === "split") {
      const expectedBranches = Array.isArray(expected.branches) ? expected.branches : [];
      const wanted = expectedBranches
        .map((value, index) => {
          const branch = record(value, `design.${concept.id}.branches[${index}]`);
          return `${branch.term}|${branch.representation}|${branch.target}`;
        })
        .sort();
      const actual = (concept.branches ?? [])
        .map(
          (branch) =>
            `${branch.term}|${branch.representation}|${branch.target.id} ${branch.target.term}`,
        )
        .sort();
      if (JSON.stringify(actual) !== JSON.stringify(wanted)) {
        fail("PROFILE-DESIGN-MISMATCH", `${concept.id} split branches differ from design`);
      }
    }
  }
}

export function digestUiProfile(profile: UiProfile): string {
  const semantic = {
    ...profile,
    representation_vocabulary: [...profile.representation_vocabulary].sort(),
    concepts: [...profile.concepts]
      .map((concept) => ({
        ...concept,
        constraints: concept.constraints ? [...concept.constraints].sort() : undefined,
        branches: concept.branches
          ? [...concept.branches].sort((left, right) => left.branch_id.localeCompare(right.branch_id))
          : undefined,
      }))
      .sort((left, right) => left.id.localeCompare(right.id)),
  };
  return createHash("sha256").update(canonicalJson(semantic)).digest("hex");
}

export function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (value !== null && typeof value === "object") {
    const entries = Object.entries(value as JsonRecord)
      .filter(([, item]) => item !== undefined)
      .sort(([left], [right]) => left.localeCompare(right));
    return `{${entries.map(([key, item]) => `${JSON.stringify(key)}:${canonicalJson(item)}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

function target(input: unknown, where: string): Target {
  const value = record(input, where);
  assertAllowedKeys(value, ["id", "term"], where);
  const id = textField(value, "id", where);
  if (!/^DS-D1\.[0-9]+$/.test(id)) {
    fail("PROFILE-CONCEPT-SHAPE-INVALID", `${where}.id must be a DS-D1 ID`);
  }
  return { id, term: textField(value, "term", where) };
}

function record(input: unknown, where: string): JsonRecord {
  if (input === null || typeof input !== "object" || Array.isArray(input)) {
    fail("PROFILE-CONCEPT-SHAPE-INVALID", `${where} must be an object`);
  }
  return input as JsonRecord;
}

function textField(value: JsonRecord, key: string, where: string): string {
  const field = value[key];
  if (typeof field !== "string" || field.trim() === "") {
    fail("PROFILE-CONCEPT-SHAPE-INVALID", `${where}.${key} must be a nonempty string`);
  }
  return field;
}

function stringArray(input: unknown, where: string): string[] {
  if (!Array.isArray(input) || input.some((item) => typeof item !== "string" || item.trim() === "")) {
    fail("PROFILE-CONCEPT-SHAPE-INVALID", `${where} must be an array of nonempty strings`);
  }
  return input as string[];
}

function assertAllowedKeys(value: JsonRecord, allowed: string[], where: string): void {
  const extras = Object.keys(value).filter((key) => !allowed.includes(key));
  if (extras.length > 0) {
    fail(
      "PROFILE-CONCEPT-SHAPE-INVALID",
      `${where} contains unsupported fields ${extras.join(", ")}; confidence cannot control placement`,
    );
  }
}

function fail(code: UiProfileViolationCode, message: string): never {
  throw new UiProfileValidationError(code, message);
}

function getArg(args: string[], name: string): string | undefined {
  const index = args.indexOf(name);
  return index < 0 ? undefined : args[index + 1];
}

export function runUiProfileCli(
  args = process.argv.slice(2),
): UiProfileValidation & { synthetic?: SyntheticCorpusReport } {
  const profilePath = resolve(process.cwd(), getArg(args, "--profile") ?? "spec/ui-profile/profile.yml");
  const designPath = resolve(
    process.cwd(),
    getArg(args, "--design") ?? "../development/ui-profile-implementation/UI-PROFILE-DESIGN.json",
  );
  const metaTypesPath = resolve(
    process.cwd(),
    getArg(args, "--meta-types") ?? "../definitions/meta-types/meta-types.yml",
  );
  const profile = parseUiProfile(readFileSync(profilePath, "utf8"), profilePath);
  const design = JSON.parse(readFileSync(designPath, "utf8")) as unknown;
  const validated = validateUiProfile(profile, {
    activeMetaTypes: loadActiveMetaTypes(metaTypesPath),
    design,
  });
  const fixtures = getArg(args, "--fixtures");
  if (fixtures === undefined) return validated;
  const schemaRoot = resolve(
    process.cwd(),
    getArg(args, "--ui-schema-dir") ?? "spec/meta-types/ui",
  );
  return {
    ...validated,
    synthetic: validateSyntheticCorpus(resolve(process.cwd(), fixtures), validated.profile, schemaRoot),
  };
}

const invokedPath = process.argv[1] ? resolve(process.argv[1]) : "";
if (invokedPath === fileURLToPath(import.meta.url)) {
  try {
    const result = runUiProfileCli();
    const synthetic = result.synthetic
      ? {
          corpus_id: result.synthetic.corpus_id,
          corpus_kind: result.synthetic.corpus_kind,
          concepts: result.synthetic.concepts,
          fixture_classes: result.synthetic.fixture_classes,
          cells: result.synthetic.cells,
          accepted: result.synthetic.accepted,
          rejected: result.synthetic.rejected,
          mismatches: result.synthetic.mismatches,
          digest: `sha256:${result.synthetic.digest}`,
        }
      : undefined;
    console.log(
      JSON.stringify(
        {
          validator: UI_PROFILE_SCHEMA_VERSION,
          status: "PASS",
          profile_id: result.profile.profile_id,
          concepts: result.conceptCount,
          representations: result.representationCounts,
          digest: `sha256:${result.digest}`,
          synthetic,
        },
        null,
        2,
      ),
    );
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  }
}
