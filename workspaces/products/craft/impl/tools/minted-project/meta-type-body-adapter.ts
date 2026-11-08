import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  evaluateCriteria,
  loadMetaTypeSchemas,
  parseMetaTypeYaml,
  preflightCriteria,
  type Criterion,
  type CriterionRule,
  type CriterionSubject,
  type MetaTypeSchema,
} from "../lib/meta-type-criteria";
import type { JsonObject, JsonSchemaViolation } from "./schema-validator";

export const MINTED_NODE_BODY_ADAPTER_VERSION = "minted-node-body-adapter/v1";

export type MintedNodeFormationOptions = {
  schemaPath?: string;
  expectedSchemaSha256?: string;
};

export type ResolvedMintedNodeFormationSchema = {
  path: string;
  sha256: string;
  schema: MetaTypeSchema;
};

export interface MintedNodeFormationViolation extends JsonSchemaViolation {
  adapterVersion: typeof MINTED_NODE_BODY_ADAPTER_VERSION;
  schemaPath: string;
  criterionId: string;
  rule: CriterionRule | "binding";
  code: string;
  subjectPath: string;
}

const implRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const canonicalSchemaRoot = resolve(implRoot, "spec/meta-types");
const canonicalSchemas = new Map(
  loadMetaTypeSchemas(canonicalSchemaRoot).map((entry) => [entry.schema.meta_type, entry]),
);

function sha256(raw: string): string {
  return createHash("sha256").update(raw).digest("hex");
}

function isObject(value: unknown): value is JsonObject {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function isScalar(value: unknown): boolean {
  return value === null || ["string", "number", "boolean"].includes(typeof value);
}

const fieldColumnAliases: Record<string, string> = {
  name: "Field",
  type: "Type",
  required: "Required",
  identity: "Identity",
  description: "Description",
};

function fieldColumnName(key: string): string {
  return fieldColumnAliases[key.trim().toLowerCase()] ?? key;
}

function loadExplicitSchema(path: string): ResolvedMintedNodeFormationSchema {
  const raw = readFileSync(path, "utf8");
  const schema = parseMetaTypeYaml(raw, path) as MetaTypeSchema;
  preflightCriteria(schema.criterion, path);
  return { path, sha256: sha256(raw), schema };
}

export function resolveMintedNodeFormationSchema(
  metaType: string,
  schemaPath?: string,
): ResolvedMintedNodeFormationSchema | undefined {
  if (schemaPath) {
    return loadExplicitSchema(schemaPath);
  }
  const loaded = canonicalSchemas.get(metaType);
  if (!loaded) {
    return undefined;
  }
  return {
    path: loaded.path,
    sha256: sha256(readFileSync(loaded.path, "utf8")),
    schema: loaded.schema,
  };
}

export function mintedNodeBodyToCriterionSubject(
  body: JsonObject,
  sourcePath: string,
): CriterionSubject {
  const fields = Array.isArray(body.fields) ? body.fields.filter(isObject) : [];
  const fieldColumns = [
    ...new Set(fields.flatMap((field) => Object.keys(field).map(fieldColumnName))),
  ].sort();
  const columns = Object.fromEntries(
    fieldColumns.map((column) => [
      column,
      fields.map((field) => {
        const key = Object.keys(field)
          .sort()
          .find((candidate) => fieldColumnName(candidate) === column);
        return key === undefined ? undefined : field[key];
      }),
    ]),
  );

  const values = Array.isArray(body.values) ? body.values : undefined;
  const table = values
    ? {
        columns: ["Value"],
        rows: values.map((value) => [isObject(value) && Object.hasOwn(value, "value") ? value.value : value]),
      }
    : undefined;

  const attributes = Object.entries(body)
    .filter(([key, value]) => key !== "fields" && key !== "values" && isScalar(value))
    .map(([key, value]) => ({ key, value }));

  return {
    kind: "normalized",
    path: `${sourcePath}#$.body`,
    text: typeof body.equality === "string" ? body.equality : undefined,
    table,
    attributes,
    columns,
  };
}

function criterionBodyPath(criterionId: string, criterion: Criterion): string {
  if (
    criterion.rule === "attribute-equals" ||
    criterion.rule === "attribute-present" ||
    criterion.rule === "attribute-one-of" ||
    criterion.rule === "attribute-nonempty/v1"
  ) {
    return `$.body.${criterion.key}`;
  }
  if (criterion.rule === "table-has-column") {
    return "$.body.values";
  }
  if (criterion.rule === "section-contains") {
    return `$.body.${criterionId}`;
  }
  return "$.body.fields";
}

function bindingViolation(
  sourcePath: string,
  schemaPath: string,
  code: string,
  detail: string,
): MintedNodeFormationViolation {
  return {
    keyword: `criterion-binding:${code}`,
    path: "$.body",
    detail,
    adapterVersion: MINTED_NODE_BODY_ADAPTER_VERSION,
    schemaPath,
    criterionId: "$binding",
    rule: "binding",
    code,
    subjectPath: `${sourcePath}#$.body`,
  };
}

export function validateMintedNodeFormation(
  metaType: string,
  body: JsonObject,
  sourcePath: string,
  options: MintedNodeFormationOptions = {},
): MintedNodeFormationViolation[] {
  let resolved: ResolvedMintedNodeFormationSchema | undefined;
  try {
    resolved = resolveMintedNodeFormationSchema(metaType, options.schemaPath);
  } catch (error) {
    return [
      bindingViolation(
        sourcePath,
        options.schemaPath ?? canonicalSchemaRoot,
        "SCHEMA-INVALID",
        error instanceof Error ? error.message : String(error),
      ),
    ];
  }

  if (!resolved) {
    return [
      bindingViolation(
        sourcePath,
        options.schemaPath ?? canonicalSchemaRoot,
        "SCHEMA-MISSING",
        `no canonical YAML criterion schema for ${metaType}`,
      ),
    ];
  }
  if (resolved.schema.meta_type !== metaType) {
    return [
      bindingViolation(
        sourcePath,
        resolved.path,
        "SCHEMA-META-TYPE-MISMATCH",
        `schema declares ${resolved.schema.meta_type}; expected ${metaType}`,
      ),
    ];
  }
  if (
    options.expectedSchemaSha256 &&
    resolved.sha256 !== options.expectedSchemaSha256.toLowerCase()
  ) {
    return [
      bindingViolation(
        sourcePath,
        resolved.path,
        "SCHEMA-DIGEST-MISMATCH",
        `schema sha256 ${resolved.sha256} does not match ${options.expectedSchemaSha256.toLowerCase()}`,
      ),
    ];
  }

  const criteria = resolved.schema.criterion ?? {};
  const subject = mintedNodeBodyToCriterionSubject(body, sourcePath);
  return evaluateCriteria(resolved.path, criteria, subject).map((violation) => {
    const criterion = criteria[violation.criterionId]!;
    return {
      keyword: `criterion:${violation.criterionId}:${violation.code}`,
      path: criterionBodyPath(violation.criterionId, criterion),
      detail: violation.message,
      adapterVersion: MINTED_NODE_BODY_ADAPTER_VERSION,
      schemaPath: violation.schemaPath,
      criterionId: violation.criterionId,
      rule: violation.rule,
      code: violation.code,
      subjectPath: violation.subjectPath,
    };
  });
}
