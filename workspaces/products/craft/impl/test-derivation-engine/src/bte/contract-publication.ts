import { createHash } from "node:crypto";
import {
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  writeFileSync,
} from "node:fs";
import { basename, dirname, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { BTE_DIAGNOSTICS } from "./validation/diagnostics.js";

type JsonObject = Record<string, unknown>;
type SchemaRegistry = Map<string, JsonObject>;

export const JSON_SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema";

export const SUPPORTED_SCHEMA_KEYWORDS = [
  "$defs",
  "$id",
  "$ref",
  "$schema",
  "additionalProperties",
  "allOf",
  "anyOf",
  "const",
  "description",
  "enum",
  "items",
  "minimum",
  "minItems",
  "minLength",
  "oneOf",
  "pattern",
  "properties",
  "required",
  "title",
  "type",
  "uniqueItems",
] as const;

export const CONTRACT_FILES = [
  "artifact-handle.v1.schema.json",
  "logical-identity.v1.schema.json",
  "authority-class.v1.schema.json",
  "diagnostic.v1.schema.json",
  "exact-set.v1.schema.json",
  "red-fixture-manifest.v1.schema.json",
  "red-fixture-freeze-receipt.v1.schema.json",
  "validation-receipt.v1.schema.json",
  "contract-publication-receipt.v1.schema.json",
] as const;

const thisFile = fileURLToPath(import.meta.url);
const thisDir = dirname(thisFile);
const engineRoot = resolve(thisDir, "../..");
const implRoot = resolve(engineRoot, "..");
const contractsDir = resolve(thisDir, "contracts");
const fixturesDir = resolve(thisDir, "fixtures/positive-contracts");
const diagnosticsPath = resolve(thisDir, "validation/diagnostics.ts");
const SESSION_OUTPUT_DIR = resolve(
  implRoot,
  "../development/first-production-release/backend-type-test-engine-completeness/runs/20260723T020759Z/l0a",
);

function isObject(value: unknown): value is JsonObject {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

export function canonicalize(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map(canonicalize).join(",")}]`;
  }
  if (isObject(value)) {
    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonicalize(value[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

function canonicalJsonBytes(value: unknown): string {
  return `${canonicalize(value)}\n`;
}

function prettyJsonBytes(value: unknown): string {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function uniqueStrings(value: unknown): value is string[] {
  return (
    Array.isArray(value) &&
    value.every((entry) => typeof entry === "string") &&
    new Set(value).size === value.length
  );
}

function walkSchemaKeywords(schema: unknown, location = "$"): void {
  if (!isObject(schema)) {
    throw new Error(`BTE_SCHEMA_INVALID: ${location} must be an object schema`);
  }
  const supported = new Set<string>(SUPPORTED_SCHEMA_KEYWORDS);
  for (const [keyword, value] of Object.entries(schema)) {
    if (!supported.has(keyword)) {
      throw new Error(`BTE_SCHEMA_UNSUPPORTED_KEYWORD: ${location}.${keyword}`);
    }
    if (keyword === "properties" || keyword === "$defs") {
      if (!isObject(value)) {
        throw new Error(`BTE_SCHEMA_INVALID: ${location}.${keyword} must be an object`);
      }
      for (const [name, child] of Object.entries(value)) {
        walkSchemaKeywords(child, `${location}.${keyword}.${name}`);
      }
    } else if (keyword === "items" || (keyword === "additionalProperties" && isObject(value))) {
      walkSchemaKeywords(value, `${location}.${keyword}`);
    } else if (keyword === "allOf" || keyword === "anyOf" || keyword === "oneOf") {
      if (!Array.isArray(value)) {
        throw new Error(`BTE_SCHEMA_INVALID: ${location}.${keyword} must be an array`);
      }
      value.forEach((child, index) => walkSchemaKeywords(child, `${location}.${keyword}[${index}]`));
    }
  }
}

function resolveReference(reference: string, root: JsonObject, registry: SchemaRegistry): JsonObject {
  if (reference.startsWith("#/$defs/")) {
    const name = reference.slice("#/$defs/".length);
    const definitions = root.$defs;
    if (!isObject(definitions) || !isObject(definitions[name])) {
      throw new Error(`BTE_SCHEMA_INVALID: unresolved local reference ${reference}`);
    }
    return definitions[name];
  }
  const resolved = registry.get(reference);
  if (!resolved) {
    throw new Error(`BTE_SCHEMA_INVALID: unresolved contract reference ${reference}`);
  }
  return resolved;
}

function validateSchemaNode(
  schema: JsonObject,
  root: JsonObject,
  registry: SchemaRegistry,
  location = "$",
): void {
  if (schema.$ref !== undefined) {
    if (typeof schema.$ref !== "string") {
      throw new Error(`BTE_SCHEMA_INVALID: ${location}.$ref must be a string`);
    }
    resolveReference(schema.$ref, root, registry);
  }
  if (schema.type !== undefined) {
    const allowedTypes = new Set(["object", "array", "string", "integer", "number", "boolean", "null"]);
    if (typeof schema.type !== "string" || !allowedTypes.has(schema.type)) {
      throw new Error(`BTE_SCHEMA_INVALID: ${location}.type is unsupported`);
    }
  }
  if (schema.required !== undefined && !uniqueStrings(schema.required)) {
    throw new Error(`BTE_SCHEMA_INVALID: ${location}.required must contain unique strings`);
  }
  if (schema.enum !== undefined) {
    if (!Array.isArray(schema.enum) || schema.enum.length === 0) {
      throw new Error(`BTE_SCHEMA_INVALID: ${location}.enum must be nonempty`);
    }
    const encoded = schema.enum.map(canonicalize);
    if (new Set(encoded).size !== encoded.length) {
      throw new Error(`BTE_SCHEMA_INVALID: ${location}.enum must be unique`);
    }
  }
  for (const integerKeyword of ["minimum", "minItems", "minLength"] as const) {
    const value = schema[integerKeyword];
    if (value !== undefined && (!Number.isInteger(value) || (value as number) < 0)) {
      throw new Error(`BTE_SCHEMA_INVALID: ${location}.${integerKeyword} must be a nonnegative integer`);
    }
  }
  if (schema.uniqueItems !== undefined && typeof schema.uniqueItems !== "boolean") {
    throw new Error(`BTE_SCHEMA_INVALID: ${location}.uniqueItems must be boolean`);
  }
  if (
    schema.additionalProperties !== undefined &&
    typeof schema.additionalProperties !== "boolean" &&
    !isObject(schema.additionalProperties)
  ) {
    throw new Error(`BTE_SCHEMA_INVALID: ${location}.additionalProperties is invalid`);
  }
  if (schema.pattern !== undefined) {
    if (typeof schema.pattern !== "string") {
      throw new Error(`BTE_SCHEMA_INVALID: ${location}.pattern must be a string`);
    }
    try {
      new RegExp(schema.pattern);
    } catch {
      throw new Error(`BTE_SCHEMA_INVALID: ${location}.pattern is invalid`);
    }
  }
  if (schema.properties !== undefined) {
    if (!isObject(schema.properties)) {
      throw new Error(`BTE_SCHEMA_INVALID: ${location}.properties must be an object`);
    }
    for (const [name, child] of Object.entries(schema.properties)) {
      if (!isObject(child)) {
        throw new Error(`BTE_SCHEMA_INVALID: ${location}.properties.${name} must be a schema`);
      }
      validateSchemaNode(child, root, registry, `${location}.properties.${name}`);
    }
  }
  if (schema.$defs !== undefined) {
    if (!isObject(schema.$defs)) {
      throw new Error(`BTE_SCHEMA_INVALID: ${location}.$defs must be an object`);
    }
    for (const [name, child] of Object.entries(schema.$defs)) {
      if (!isObject(child)) {
        throw new Error(`BTE_SCHEMA_INVALID: ${location}.$defs.${name} must be a schema`);
      }
      validateSchemaNode(child, root, registry, `${location}.$defs.${name}`);
    }
  }
  if (schema.items !== undefined) {
    if (!isObject(schema.items)) {
      throw new Error(`BTE_SCHEMA_INVALID: ${location}.items must be a schema`);
    }
    validateSchemaNode(schema.items, root, registry, `${location}.items`);
  }
  if (isObject(schema.additionalProperties)) {
    validateSchemaNode(schema.additionalProperties, root, registry, `${location}.additionalProperties`);
  }
  for (const composition of ["allOf", "anyOf", "oneOf"] as const) {
    if (schema[composition] !== undefined) {
      const entries = schema[composition];
      if (!Array.isArray(entries) || entries.length === 0 || entries.some((entry) => !isObject(entry))) {
        throw new Error(`BTE_SCHEMA_INVALID: ${location}.${composition} must contain schemas`);
      }
      entries.forEach((entry, index) =>
        validateSchemaNode(entry as JsonObject, root, registry, `${location}.${composition}[${index}]`),
      );
    }
  }
}

export function validatePublishedSchema(schema: unknown, registry: SchemaRegistry): void {
  if (!isObject(schema)) {
    throw new Error("BTE_SCHEMA_INVALID: contract must be an object schema");
  }
  if (schema.$schema !== JSON_SCHEMA_DIALECT) {
    throw new Error("BTE_SCHEMA_INVALID: contract must declare Draft 2020-12");
  }
  if (typeof schema.$id !== "string" || schema.$id.length === 0) {
    throw new Error("BTE_SCHEMA_INVALID: contract must declare a nonempty $id");
  }
  walkSchemaKeywords(schema);
  validateSchemaNode(schema, schema, registry);
}

function typeMatches(type: string, value: unknown): boolean {
  switch (type) {
    case "object": return isObject(value);
    case "array": return Array.isArray(value);
    case "string": return typeof value === "string";
    case "integer": return typeof value === "number" && Number.isInteger(value);
    case "number": return typeof value === "number" && Number.isFinite(value);
    case "boolean": return typeof value === "boolean";
    case "null": return value === null;
    default: return false;
  }
}

function validationErrors(
  schema: JsonObject,
  value: unknown,
  root: JsonObject,
  registry: SchemaRegistry,
  location = "$",
): string[] {
  if (typeof schema.$ref === "string") {
    const target = resolveReference(schema.$ref, root, registry);
    return validationErrors(target, value, target, registry, location);
  }
  const errors: string[] = [];
  if (typeof schema.type === "string" && !typeMatches(schema.type, value)) {
    return [`${location}: expected ${schema.type}`];
  }
  if (schema.const !== undefined && canonicalize(schema.const) !== canonicalize(value)) {
    errors.push(`${location}: const mismatch`);
  }
  if (Array.isArray(schema.enum) && !schema.enum.some((entry) => canonicalize(entry) === canonicalize(value))) {
    errors.push(`${location}: value is outside enum`);
  }
  if (typeof value === "string") {
    if (typeof schema.minLength === "number" && value.length < schema.minLength) {
      errors.push(`${location}: shorter than minLength`);
    }
    if (typeof schema.pattern === "string" && !new RegExp(schema.pattern).test(value)) {
      errors.push(`${location}: pattern mismatch`);
    }
  }
  if (typeof value === "number" && typeof schema.minimum === "number" && value < schema.minimum) {
    errors.push(`${location}: smaller than minimum`);
  }
  if (Array.isArray(value)) {
    if (typeof schema.minItems === "number" && value.length < schema.minItems) {
      errors.push(`${location}: fewer than minItems`);
    }
    if (schema.uniqueItems === true) {
      const members = value.map(canonicalize);
      if (new Set(members).size !== members.length) {
        errors.push(`${location}: duplicate array member`);
      }
    }
    if (isObject(schema.items)) {
      value.forEach((entry, index) => errors.push(...validationErrors(schema.items as JsonObject, entry, root, registry, `${location}[${index}]`)));
    }
  }
  if (isObject(value)) {
    const properties = isObject(schema.properties) ? schema.properties : {};
    if (Array.isArray(schema.required)) {
      for (const key of schema.required) {
        if (typeof key === "string" && !Object.prototype.hasOwnProperty.call(value, key)) {
          errors.push(`${location}.${key}: required property missing`);
        }
      }
    }
    for (const [key, childValue] of Object.entries(value)) {
      const childSchema = properties[key];
      if (isObject(childSchema)) {
        errors.push(...validationErrors(childSchema, childValue, root, registry, `${location}.${key}`));
      } else if (schema.additionalProperties === false) {
        errors.push(`${location}.${key}: additional property forbidden`);
      } else if (isObject(schema.additionalProperties)) {
        errors.push(...validationErrors(schema.additionalProperties, childValue, root, registry, `${location}.${key}`));
      }
    }
  }
  for (const composition of ["allOf", "anyOf", "oneOf"] as const) {
    const entries = schema[composition];
    if (!Array.isArray(entries)) continue;
    const results = entries.map((entry) => validationErrors(entry as JsonObject, value, root, registry, location));
    if (composition === "allOf") results.forEach((result) => errors.push(...result));
    if (composition === "anyOf" && results.every((result) => result.length > 0)) errors.push(`${location}: anyOf failed`);
    if (composition === "oneOf" && results.filter((result) => result.length === 0).length !== 1) errors.push(`${location}: oneOf failed`);
  }
  return errors;
}

export function validateContractInstance(
  schema: JsonObject,
  value: unknown,
  registry: SchemaRegistry,
): void {
  const errors = validationErrors(schema, value, schema, registry);
  if (errors.length > 0) {
    throw new Error(`BTE_SCHEMA_INVALID: ${errors.join("; ")}`);
  }
}

type LoadedContract = {
  file: (typeof CONTRACT_FILES)[number];
  path: string;
  bytes: Buffer;
  schema: JsonObject;
};

function loadContracts(): { contracts: LoadedContract[]; registry: SchemaRegistry } {
  const contracts = CONTRACT_FILES.map((file) => {
    const path = resolve(contractsDir, file);
    const bytes = readFileSync(path);
    const schema = JSON.parse(bytes.toString("utf8")) as JsonObject;
    if (!bytes.toString("utf8").endsWith("\n") || bytes.toString("utf8").includes("\r")) {
      throw new Error(`BTE_SCHEMA_INVALID: ${file} must use LF bytes and a trailing newline`);
    }
    return { file, path, bytes, schema };
  });
  const registry: SchemaRegistry = new Map();
  for (const contract of contracts) {
    if (typeof contract.schema.$id !== "string" || registry.has(contract.schema.$id)) {
      throw new Error(`BTE_SCHEMA_INVALID: duplicate or missing $id in ${contract.file}`);
    }
    registry.set(contract.schema.$id, contract.schema);
  }
  return { contracts, registry };
}

function fixtureFile(contractFile: string): string {
  return contractFile.replace(".schema.json", ".json");
}

function verifyDiagnosticClosure(contracts: LoadedContract[]): void {
  const diagnosticSchema = contracts.find(({ file }) => file === "diagnostic.v1.schema.json")?.schema;
  const properties = diagnosticSchema && isObject(diagnosticSchema.properties) ? diagnosticSchema.properties : undefined;
  const codeSchema = properties && isObject(properties.code) ? properties.code : undefined;
  const stageSchema = properties && isObject(properties.stage) ? properties.stage : undefined;
  const schemaCodes = codeSchema?.enum;
  const schemaStages = stageSchema?.enum;
  const registryCodes = BTE_DIAGNOSTICS.map(({ code }) => code);
  const registryStages = [...new Set(BTE_DIAGNOSTICS.map(({ stage }) => stage))];
  const precedence = BTE_DIAGNOSTICS.map(({ precedence }) => precedence);
  if (
    !uniqueStrings(schemaCodes) ||
    canonicalize(schemaCodes) !== canonicalize(registryCodes) ||
    !uniqueStrings(schemaStages) ||
    canonicalize(schemaStages) !== canonicalize(registryStages) ||
    new Set(precedence).size !== precedence.length ||
    precedence.some((value, index) => {
      const previous = precedence[index - 1];
      return previous !== undefined && value <= previous;
    })
  ) {
    throw new Error("BTE_DIAGNOSTIC_PRECEDENCE: schema and registry are not one closed ordered set");
  }
}

type LogicalIdentity = {
  schema_version: "bte-logical-identity/v1";
  domain: string;
  namespace: string;
  kind: string;
  key: string;
  version: number;
};

type ArtifactHandle = {
  schema_version: "bte-artifact-handle/v1";
  root_id: string;
  path: string;
  schema_id: string;
  logical_identity: LogicalIdentity;
  sha256: string;
  bytes: number;
  producer: { id: string; version: string; digest: string };
  authority: {
    schema_version: "bte-authority-class/v1";
    class: "evidence";
    owner: LogicalIdentity;
    owner_digest: string;
  };
};

export type ContractPublicationReceipt = {
  schema_version: "bte-contract-publication-receipt/v1";
  receipt_kind: "contract-publication";
  receipt_id: LogicalIdentity;
  dialect: typeof JSON_SCHEMA_DIALECT;
  supported_keywords: string[];
  contracts: ArtifactHandle[];
  diagnostics_registry: ArtifactHandle;
  admission: "not-granted";
};

function identity(kind: string, key: string): LogicalIdentity {
  return {
    schema_version: "bte-logical-identity/v1",
    domain: "domainspec-v2",
    namespace: "bte",
    kind,
    key,
    version: 1,
  };
}

function artifactHandle(input: {
  path: string;
  schemaId: string;
  key: string;
  bytes: Buffer;
  publisherDigest: string;
}): ArtifactHandle {
  return {
    schema_version: "bte-artifact-handle/v1",
    root_id: "domainspec-v2-impl",
    path: input.path,
    schema_id: input.schemaId,
    logical_identity: identity("contract-artifact", input.key),
    sha256: sha256(input.bytes),
    bytes: input.bytes.byteLength,
    producer: {
      id: "bte-contract-publisher",
      version: "1.0.0",
      digest: input.publisherDigest,
    },
    authority: {
      schema_version: "bte-authority-class/v1",
      class: "evidence",
      owner: identity("producer", "bte-contract-publisher"),
      owner_digest: input.publisherDigest,
    },
  };
}

export function createContractPublicationReceipt(): ContractPublicationReceipt {
  const { contracts, registry } = loadContracts();
  for (const contract of contracts) {
    validatePublishedSchema(contract.schema, registry);
    const fixturePath = resolve(fixturesDir, fixtureFile(contract.file));
    const fixture = JSON.parse(readFileSync(fixturePath, "utf8")) as unknown;
    validateContractInstance(contract.schema, fixture, registry);
  }
  verifyDiagnosticClosure(contracts);
  const publisherDigest = sha256(readFileSync(thisFile));
  const contractHandles = contracts.map((contract) =>
    artifactHandle({
      path: relative(implRoot, contract.path),
      schemaId: contract.schema.$id as string,
      key: contract.file,
      bytes: contract.bytes,
      publisherDigest,
    }),
  );
  const diagnosticBytes = readFileSync(diagnosticsPath);
  const receipt: ContractPublicationReceipt = {
    schema_version: "bte-contract-publication-receipt/v1",
    receipt_kind: "contract-publication",
    receipt_id: identity("receipt", "l0a-contract-publication"),
    dialect: JSON_SCHEMA_DIALECT,
    supported_keywords: [...SUPPORTED_SCHEMA_KEYWORDS],
    contracts: contractHandles,
    diagnostics_registry: artifactHandle({
      path: relative(implRoot, diagnosticsPath),
      schemaId: "urn:domainspec-v2:bte:diagnostic-registry:v1",
      key: "diagnostics.ts",
      bytes: diagnosticBytes,
      publisherDigest,
    }),
    admission: "not-granted",
  };
  const publicationSchema = registry.get("urn:domainspec-v2:bte:contract-publication-receipt:v1");
  if (!publicationSchema) throw new Error("BTE_SCHEMA_INVALID: publication receipt schema missing");
  validateContractInstance(publicationSchema, receipt, registry);
  return receipt;
}

export function publicationReceiptBytes(receipt = createContractPublicationReceipt()): string {
  return canonicalJsonBytes(receipt);
}

export function verifyContractPublicationReceipt(receipt: unknown): {
  result: "pass" | "fail";
  codes: string[];
} {
  try {
    const { registry } = loadContracts();
    const publicationSchema = registry.get("urn:domainspec-v2:bte:contract-publication-receipt:v1");
    if (!publicationSchema) throw new Error("publication schema missing");
    validateContractInstance(publicationSchema, receipt, registry);
    const expected = createContractPublicationReceipt();
    if (canonicalize(receipt) !== canonicalize(expected)) {
      return { result: "fail", codes: ["BTE_DIGEST_MISMATCH"] };
    }
    return { result: "pass", codes: [] };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    const code = BTE_DIAGNOSTICS.find(({ code }) => message.includes(code))?.code ?? "BTE_SCHEMA_INVALID";
    return { result: "fail", codes: [code] };
  }
}

function stableWrite(path: string, bytes: string): void {
  if (existsSync(path)) {
    const current = readFileSync(path, "utf8");
    if (current !== bytes) {
      throw new Error(`BTE_OUTPUT_OVERWRITE: refusing to replace different bytes at ${path}`);
    }
    return;
  }
  writeFileSync(path, bytes);
}

export function writeContractPublicationArtifacts(outputDir: string): {
  receiptBytes: string;
  manifestBytes: string;
} {
  mkdirSync(outputDir, { recursive: true });
  const allowed = new Set(["contract-publication-receipt.json", "output-write-manifest.json"]);
  const extras = readdirSync(outputDir).filter((entry) => !allowed.has(entry));
  if (extras.length > 0) {
    throw new Error(`BTE_OUTPUT_OVERWRITE: output directory contains undeclared paths: ${extras.join(", ")}`);
  }
  const first = publicationReceiptBytes();
  const second = publicationReceiptBytes();
  if (first !== second) {
    throw new Error("BTE_DIGEST_MISMATCH: publication bytes changed across two invocations");
  }
  const receiptPath = resolve(outputDir, "contract-publication-receipt.json");
  const manifestPath = resolve(outputDir, "output-write-manifest.json");
  stableWrite(receiptPath, first);
  const manifest = {
    schema_version: "bte-output-write-manifest/v1",
    swu_id: "SWU-BTE-L0A-001",
    run_id: basename(dirname(outputDir)),
    allowed_paths: ["contract-publication-receipt.json", "output-write-manifest.json"],
    content_writes: [
      {
        path: "contract-publication-receipt.json",
        sha256: sha256(first),
        bytes: Buffer.byteLength(first),
      },
    ],
    admission: "not-granted",
  };
  const manifestBytes = canonicalJsonBytes(manifest);
  stableWrite(manifestPath, manifestBytes);
  const actual = readdirSync(outputDir).sort();
  if (canonicalize(actual) !== canonicalize([...allowed].sort())) {
    throw new Error("BTE_OUTPUT_OVERWRITE: actual output set differs from the allowlist");
  }
  const parsedReceipt = JSON.parse(readFileSync(receiptPath, "utf8"));
  if (verifyContractPublicationReceipt(parsedReceipt).result !== "pass") {
    throw new Error("BTE_DIGEST_MISMATCH: written publication receipt did not independently recompute");
  }
  return { receiptBytes: first, manifestBytes };
}

function runCli(): void {
  const outputFlag = process.argv.indexOf("--output-dir");
  const requested = outputFlag >= 0 ? process.argv[outputFlag + 1] : undefined;
  const outputDir = requested ? resolve(process.cwd(), requested) : SESSION_OUTPUT_DIR;
  if (outputDir !== SESSION_OUTPUT_DIR) {
    throw new Error(`BTE_OUTPUT_OVERWRITE: CLI output must equal ${SESSION_OUTPUT_DIR}`);
  }
  const output = writeContractPublicationArtifacts(outputDir);
  process.stdout.write(
    `${canonicalize({
      result: "pass",
      swu_id: "SWU-BTE-L0A-001",
      receipt_sha256: sha256(output.receiptBytes),
      manifest_sha256: sha256(output.manifestBytes),
      admission: "not-granted",
    })}\n`,
  );
}

if (process.argv[1] && resolve(process.argv[1]) === thisFile) {
  runCli();
}
