import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join, relative } from "node:path";

import {
  assertCriterionPreflight as assertUiCriterionPreflight,
  assertNoDuplicateSchemaKey,
  attributeNonemptyViolation,
  uiRepairViolation,
} from "./ui-repair-rule-contract";

export const META_TYPE_CRITERIA_REGISTRY = "meta-type-criteria/v1";

export const META_TYPE_CRITERIA_RULES = [
  "at-least-one",
  "none",
  "all-nonempty",
  "section-contains",
  "table-has-column",
  "attribute-equals",
  "attribute-present",
  "attribute-one-of",
  "attribute-nonempty/v1",
] as const;

export type CriterionRule = (typeof META_TYPE_CRITERIA_RULES)[number];

export type Criterion = {
  rule: CriterionRule;
  column?: string;
  truthy?: string[];
  pattern?: string;
  key?: string;
  value?: unknown;
  values?: string[];
};

export type MetaTypeSchema = {
  meta_type: string;
  required_structure?: Record<string, unknown>;
  criterion?: Record<string, Criterion>;
  [key: string]: unknown;
};

export type LoadedMetaTypeSchema<TSchema extends MetaTypeSchema = MetaTypeSchema> = {
  path: string;
  schema: TSchema;
};

export type CriterionAttribute = {
  key: string;
  value: unknown;
};

export type CriterionTable = {
  columns: string[];
  rows: unknown[][];
};

export type CriterionSubject = {
  kind: "markdown" | "instance" | "normalized";
  path: string;
  text?: string;
  table?: CriterionTable;
  attributes?: CriterionAttribute[];
  columns?: Record<string, unknown[]>;
};

export type CriterionViolationCode =
  | "SECTION-PATTERN-MISSING"
  | "TABLE-MISSING"
  | "TABLE-COLUMN-MISSING"
  | "TABLE-EMPTY"
  | "ATTRIBUTE-TABLE-MISSING"
  | "ATTRIBUTE-MISSING"
  | "ATTRIBUTE-EMPTY"
  | "ATTRIBUTE-WHITESPACE"
  | "ATTRIBUTE-NONSTRING"
  | "ATTRIBUTE-VALUE-MISMATCH"
  | "ATTRIBUTE-VALUE-NOT-ALLOWED"
  | "COLUMN-MISSING"
  | "AT-LEAST-ONE-UNSATISFIED"
  | "NONE-VIOLATED"
  | "ALL-NONEMPTY-VIOLATED";

export type CriterionViolation = {
  schemaPath: string;
  criterionId: string;
  rule: CriterionRule;
  subjectPath: string;
  code: CriterionViolationCode;
  message: string;
};

type CriteriaContractErrorCode =
  | "YAML-INDENTATION"
  | "YAML-SYNTAX"
  | "YAML-UNSUPPORTED"
  | "CRITERION-REQUIRED-FIELD"
  | "CRITERION-OPTIONS"
  | "META-TYPE-MISSING"
  | "META-TYPE-DUPLICATE";

export class MetaTypeCriteriaError extends Error {
  readonly code: CriteriaContractErrorCode;

  constructor(code: CriteriaContractErrorCode, detail: string) {
    super(`[${META_TYPE_CRITERIA_REGISTRY}:${code}] ${detail}`);
    this.name = "MetaTypeCriteriaError";
    this.code = code;
  }
}

export function loadMetaTypeSchemas<TSchema extends MetaTypeSchema = MetaTypeSchema>(
  dir: string,
): Array<LoadedMetaTypeSchema<TSchema>> {
  if (!existsSync(dir)) {
    return [];
  }

  const loaded = walk(dir)
    .filter((path) => path.endsWith(".schema.yml"))
    .sort()
    .map((path) => {
      const where = toRelative(path);
      const schema = parseMetaTypeYaml(readFileSync(path, "utf-8"), where) as TSchema;
      preflightCriteria(schema.criterion, where);
      if (typeof schema.meta_type !== "string" || schema.meta_type.trim() === "") {
        throw new MetaTypeCriteriaError(
          "META-TYPE-MISSING",
          `${where}: schema is missing a non-empty 'meta_type'`,
        );
      }
      return { path: where, schema };
    });

  const owners = new Map<string, string>();
  for (const entry of loaded) {
    const normalized = normalizeToken(entry.schema.meta_type);
    const previous = owners.get(normalized);
    if (previous) {
      throw new MetaTypeCriteriaError(
        "META-TYPE-DUPLICATE",
        `${entry.path}: meta_type '${entry.schema.meta_type}' duplicates ${previous}`,
      );
    }
    owners.set(normalized, entry.path);
  }

  return loaded;
}

export function parseMetaTypeYaml(raw: string, where: string): Record<string, unknown> {
  const root: Record<string, unknown> = {};
  const stack: Array<{ indent: number; node: Record<string, unknown> }> = [
    { indent: -2, node: root },
  ];
  const lines = raw.split(/\r?\n/);

  for (let index = 0; index < lines.length; index += 1) {
    const rawLine = lines[index] ?? "";
    const line = index + 1;
    if (rawLine.trim() === "" || rawLine.trim().startsWith("#")) {
      continue;
    }
    if (rawLine.includes("\t")) {
      throw new MetaTypeCriteriaError(
        "YAML-INDENTATION",
        `${where}:${line}: tabs are not allowed`,
      );
    }

    const indent = rawLine.length - rawLine.trimStart().length;
    if (indent % 2 !== 0) {
      throw new MetaTypeCriteriaError(
        "YAML-INDENTATION",
        `${where}:${line}: indentation must use two-space steps`,
      );
    }

    const content = rawLine.trim();
    if (content.startsWith("-")) {
      throw new MetaTypeCriteriaError(
        "YAML-UNSUPPORTED",
        `${where}:${line}: block sequences are not supported`,
      );
    }

    const colon = content.indexOf(":");
    if (colon <= 0) {
      throw new MetaTypeCriteriaError(
        "YAML-SYNTAX",
        `${where}:${line}: expected a non-empty 'key:' entry; got "${content}"`,
      );
    }
    const key = content.slice(0, colon).trim();
    if (!/^[A-Za-z0-9_-]+$/.test(key)) {
      throw new MetaTypeCriteriaError(
        "YAML-UNSUPPORTED",
        `${where}:${line}: unsupported key '${key}'`,
      );
    }
    const rest = content.slice(colon + 1).trim();

    while (stack.length > 1 && (stack[stack.length - 1]?.indent ?? -2) >= indent) {
      stack.pop();
    }
    const parentFrame = stack[stack.length - 1];
    if (!parentFrame || indent !== parentFrame.indent + 2) {
      throw new MetaTypeCriteriaError(
        "YAML-INDENTATION",
        `${where}:${line}: malformed indentation at '${key}'`,
      );
    }

    assertNoDuplicateSchemaKey(parentFrame.node, key, where, line);
    if (rest === "") {
      const child: Record<string, unknown> = {};
      parentFrame.node[key] = child;
      stack.push({ indent, node: child });
    } else {
      parentFrame.node[key] = parseScalarOrFlowList(rest, where, line);
    }
  }

  return root;
}

export function preflightCriteria(
  criteria: unknown,
  schemaPath: string,
): Record<string, Criterion> {
  assertUiCriterionPreflight(criteria, schemaPath);
  if (criteria === undefined) {
    return {};
  }

  const typed = criteria as Record<string, Criterion>;
  for (const [criterionId, criterion] of Object.entries(typed)) {
    switch (criterion.rule) {
      case "at-least-one":
      case "none":
        requireNonEmptyString(criterion, "column", criterionId, schemaPath);
        requireNonEmptyStringArray(criterion.truthy, "truthy", criterionId, schemaPath);
        break;
      case "all-nonempty":
      case "table-has-column":
        requireNonEmptyString(criterion, "column", criterionId, schemaPath);
        break;
      case "section-contains":
        requireNonEmptyString(criterion, "pattern", criterionId, schemaPath);
        break;
      case "attribute-equals":
        requireNonEmptyString(criterion, "key", criterionId, schemaPath);
        if (!Object.hasOwn(criterion, "value")) {
          throw requiredFieldError(schemaPath, criterionId, "value");
        }
        if (!isScalar(criterion.value)) {
          throw new MetaTypeCriteriaError(
            "CRITERION-REQUIRED-FIELD",
            `${schemaPath}: criterion '${criterionId}' requires scalar 'value'`,
          );
        }
        break;
      case "attribute-present":
      case "attribute-nonempty/v1":
        requireNonEmptyString(criterion, "key", criterionId, schemaPath);
        break;
      case "attribute-one-of":
        requireNonEmptyString(criterion, "key", criterionId, schemaPath);
        requireNonEmptyStringArray(criterion.values, "values", criterionId, schemaPath);
        break;
    }
  }

  return typed;
}

export function evaluateCriteria(
  schemaPath: string,
  criteria: unknown,
  subject: CriterionSubject,
): CriterionViolation[] {
  const typed = preflightCriteria(criteria, schemaPath);
  const violations: CriterionViolation[] = [];
  for (const [criterionId, criterion] of Object.entries(typed)) {
    const violation = evaluateCriterion(schemaPath, criterionId, criterion, subject);
    if (violation) {
      violations.push(violation);
    }
  }
  return violations;
}

function evaluateCriterion(
  schemaPath: string,
  criterionId: string,
  criterion: Criterion,
  subject: CriterionSubject,
): CriterionViolation | null {
  const fail = (
    code: CriterionViolationCode,
    message: string,
  ): CriterionViolation => ({
    schemaPath,
    criterionId,
    rule: criterion.rule,
    subjectPath: subject.path,
    code,
    message: `criterion '${criterionId}': ${message}`,
  });

  if (criterion.rule === "section-contains") {
    if (!normalizeToken(subject.text ?? "").includes(normalizeToken(criterion.pattern ?? ""))) {
      return fail(
        "SECTION-PATTERN-MISSING",
        subject.kind === "instance"
          ? `instance has no text containing '${criterion.pattern}'`
          : `concept section does not contain '${criterion.pattern}'`,
      );
    }
    return null;
  }

  if (criterion.rule === "table-has-column") {
    if (!subject.table) {
      return fail(
        "TABLE-MISSING",
        subject.kind === "instance"
          ? `instance has no non-empty '${normalizeToken(criterion.column ?? "")}' list`
          : "no table found in the concept section",
      );
    }
    const wanted = normalizeToken(criterion.column ?? "");
    if (!subject.table.columns.some((column) => normalizeToken(column) === wanted)) {
      return fail("TABLE-COLUMN-MISSING", `table has no '${criterion.column}' column`);
    }
    if (subject.table.rows.length === 0) {
      return fail("TABLE-EMPTY", `column '${criterion.column}' present but the table has no rows`);
    }
    return null;
  }

  if (isAttributeRule(criterion.rule)) {
    const requiredColumns = criterion.rule === "attribute-present" ? ["attribute"] : ["attribute", "value"];
    if (
      subject.kind === "markdown" &&
      (!subject.table ||
        requiredColumns.some(
          (required) =>
            !subject.table?.columns.some((column) => normalizeToken(column) === required),
        ))
    ) {
      return fail("ATTRIBUTE-TABLE-MISSING", 'expected an "Attribute | Value" table');
    }

    const match = findAttribute(subject.attributes, criterion.key ?? "");
    if (!match) {
      return fail(
        "ATTRIBUTE-MISSING",
        uiRepairViolation(
          "ATTRIBUTE-MISSING",
          `attribute '${criterion.key}' is not declared`,
        ),
      );
    }
    if (criterion.rule === "attribute-present") {
      return null;
    }

    if (criterion.rule === "attribute-nonempty/v1") {
      const code = attributeNonemptyViolation(true, match.value);
      if (!code) {
        return null;
      }
      const violationCode: CriterionViolationCode =
        code === "NONSTRING-VALUE"
          ? "ATTRIBUTE-NONSTRING"
          : code === "ATTRIBUTE-EMPTY" ||
              code === "ATTRIBUTE-WHITESPACE" ||
              code === "ATTRIBUTE-MISSING"
            ? code
            : "ATTRIBUTE-NONSTRING";
      return fail(
        violationCode,
        uiRepairViolation(
          code,
          `attribute '${criterion.key}' must contain non-whitespace text`,
        ),
      );
    }

    const emptyCode = scalarEmptyCode(match.value);
    if (emptyCode) {
      return fail(
        emptyCode,
        uiRepairViolation(
          emptyCode,
          `attribute '${criterion.key}' must contain its fixed value`,
        ),
      );
    }
    if (!isScalar(match.value)) {
      return fail(
        "ATTRIBUTE-NONSTRING",
        uiRepairViolation(
          "NONSTRING-VALUE",
          `attribute '${criterion.key}' must contain a scalar value`,
        ),
      );
    }

    const actual = normalizeValue(match.value);
    if (criterion.rule === "attribute-equals") {
      if (actual !== normalizeValue(criterion.value)) {
        return fail(
          "ATTRIBUTE-VALUE-MISMATCH",
          uiRepairViolation(
            "FIXED-VALUE-MISMATCH",
            `attribute '${criterion.key}'='${actual}' (expected '${String(criterion.value)}')`,
          ),
        );
      }
      return null;
    }

    const allowed = (criterion.values ?? []).map(normalizeValue);
    if (!allowed.includes(actual)) {
      return fail(
        "ATTRIBUTE-VALUE-NOT-ALLOWED",
        `attribute '${criterion.key}'='${actual}' (expected one of [${(criterion.values ?? []).join(", ")}])`,
      );
    }
    return null;
  }

  const column = findColumn(subject.columns, criterion.column ?? "");
  if (!column) {
    return fail(
      "COLUMN-MISSING",
      subject.kind === "instance"
        ? `instance has no 'field_${normalizeToken(criterion.column ?? "")}' array`
        : `required column '${criterion.column}' missing from the table`,
    );
  }

  if (criterion.rule === "all-nonempty") {
    const emptyCount = column.filter(isEmpty).length;
    if (emptyCount > 0) {
      return fail(
        "ALL-NONEMPTY-VIOLATED",
        subject.kind === "instance"
          ? `an entry in field_${normalizeToken(criterion.column ?? "")} is empty`
          : `${emptyCount} field(s) have an empty '${criterion.column}' cell`,
      );
    }
    return null;
  }

  const truthy = (criterion.truthy ?? []).map(normalizeValue);
  const hits = column.filter((value) => truthy.includes(normalizeValue(value))).length;
  if (criterion.rule === "at-least-one" && hits === 0) {
    return fail(
      "AT-LEAST-ONE-UNSATISFIED",
      subject.kind === "instance"
        ? `no '${criterion.column}' flagged in field_${normalizeToken(criterion.column ?? "")}`
        : `no field flagged in column '${criterion.column}' (need >=1 of [${(criterion.truthy ?? []).join(", ")}])`,
    );
  }
  if (criterion.rule === "none" && hits > 0) {
    return fail(
      "NONE-VIOLATED",
      subject.kind === "instance"
        ? `a '${criterion.column}' is flagged in field_${normalizeToken(criterion.column ?? "")} but none allowed`
        : `${hits} field(s) flagged in column '${criterion.column}' but none are allowed`,
    );
  }
  return null;
}

function parseScalarOrFlowList(value: string, where: string, line: number): string | string[] {
  if (value.startsWith("{") || value.endsWith("}")) {
    throw new MetaTypeCriteriaError(
      "YAML-UNSUPPORTED",
      `${where}:${line}: flow maps are not supported`,
    );
  }
  if (["|", ">"].includes(value) || /^[&*!]/.test(value)) {
    throw new MetaTypeCriteriaError(
      "YAML-UNSUPPORTED",
      `${where}:${line}: anchors, tags, aliases, and multiline scalars are not supported`,
    );
  }
  if (value.startsWith("[") !== value.endsWith("]")) {
    throw new MetaTypeCriteriaError(
      "YAML-SYNTAX",
      `${where}:${line}: malformed flow list`,
    );
  }
  if (value.startsWith("[")) {
    const inner = value.slice(1, -1).trim();
    if (inner === "") {
      return [];
    }
    return splitFlowList(inner, where, line).map((item) => parseScalar(item, where, line));
  }
  return parseScalar(value, where, line);
}

function splitFlowList(value: string, where: string, line: number): string[] {
  const items: string[] = [];
  let current = "";
  let quote: "'" | '"' | null = null;
  for (const char of value) {
    if ((char === "'" || char === '"') && quote === null) {
      quote = char;
      current += char;
    } else if (char === quote) {
      quote = null;
      current += char;
    } else if (char === "," && quote === null) {
      if (current.trim() === "") {
        throw new MetaTypeCriteriaError(
          "YAML-SYNTAX",
          `${where}:${line}: empty flow-list item`,
        );
      }
      items.push(current.trim());
      current = "";
    } else {
      current += char;
    }
  }
  if (quote !== null || current.trim() === "") {
    throw new MetaTypeCriteriaError(
      "YAML-SYNTAX",
      `${where}:${line}: malformed quoted flow-list item`,
    );
  }
  items.push(current.trim());
  return items;
}

function parseScalar(value: string, where: string, line: number): string {
  const startsQuote = value.startsWith('"') || value.startsWith("'");
  const endsQuote = value.endsWith('"') || value.endsWith("'");
  if (startsQuote || endsQuote) {
    if (
      value.length < 2 ||
      !((value.startsWith('"') && value.endsWith('"')) ||
        (value.startsWith("'") && value.endsWith("'")))
    ) {
      throw new MetaTypeCriteriaError(
        "YAML-SYNTAX",
        `${where}:${line}: unmatched scalar quote`,
      );
    }
    return value.slice(1, -1);
  }
  return value;
}

function requireNonEmptyString(
  criterion: Criterion,
  field: "column" | "pattern" | "key",
  criterionId: string,
  schemaPath: string,
): void {
  const value = criterion[field];
  if (typeof value !== "string" || value.trim() === "") {
    throw requiredFieldError(schemaPath, criterionId, field);
  }
}

function requireNonEmptyStringArray(
  value: unknown,
  field: "truthy" | "values",
  criterionId: string,
  schemaPath: string,
): void {
  if (
    !Array.isArray(value) ||
    value.length === 0 ||
    value.some((entry) => typeof entry !== "string" || entry.trim() === "")
  ) {
    throw new MetaTypeCriteriaError(
      "CRITERION-OPTIONS",
      `${schemaPath}: criterion '${criterionId}' requires a non-empty '${field}' string array`,
    );
  }
}

function requiredFieldError(
  schemaPath: string,
  criterionId: string,
  field: string,
): MetaTypeCriteriaError {
  return new MetaTypeCriteriaError(
    "CRITERION-REQUIRED-FIELD",
    `${schemaPath}: criterion '${criterionId}' requires a non-empty '${field}'`,
  );
}

function isAttributeRule(rule: CriterionRule): boolean {
  return [
    "attribute-equals",
    "attribute-present",
    "attribute-one-of",
    "attribute-nonempty/v1",
  ].includes(rule);
}

function findAttribute(
  attributes: CriterionAttribute[] | undefined,
  key: string,
): CriterionAttribute | undefined {
  const wanted = normalizeToken(key);
  return attributes?.find((attribute) => normalizeToken(attribute.key) === wanted);
}

function findColumn(
  columns: Record<string, unknown[]> | undefined,
  key: string,
): unknown[] | undefined {
  const wanted = normalizeToken(key);
  const entry = Object.entries(columns ?? {}).find(
    ([column]) => normalizeToken(column) === wanted,
  );
  return entry?.[1];
}

function scalarEmptyCode(value: unknown): "ATTRIBUTE-EMPTY" | "ATTRIBUTE-WHITESPACE" | null {
  if (value === "") return "ATTRIBUTE-EMPTY";
  if (typeof value === "string" && value.trim() === "") return "ATTRIBUTE-WHITESPACE";
  return null;
}

function isEmpty(value: unknown): boolean {
  return value === undefined || value === null || (typeof value === "string" && value.trim() === "");
}

function isScalar(value: unknown): value is string | number | boolean {
  return typeof value === "string" || typeof value === "number" || typeof value === "boolean";
}

function normalizeToken(value: string): string {
  return value.trim().toLowerCase();
}

function normalizeValue(value: unknown): string {
  return String(value).trim().toLowerCase();
}

function walk(root: string): string[] {
  const paths: string[] = [];
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    const path = join(root, entry.name);
    if (entry.isDirectory()) {
      paths.push(...walk(path));
    } else if (entry.isFile()) {
      paths.push(path);
    }
  }
  return paths;
}

function toRelative(path: string): string {
  return relative(process.cwd(), path).replace(/\\/g, "/");
}
