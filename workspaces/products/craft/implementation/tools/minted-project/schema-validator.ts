import { readFileSync } from "node:fs";
import { dirname, isAbsolute, resolve, win32 } from "node:path";

export type JsonObject = Record<string, any>;

export interface JsonSchemaViolation {
  keyword: string;
  path: string;
  detail: string;
}

function readSchema(path: string): JsonObject {
  return JSON.parse(readFileSync(path, "utf8")) as JsonObject;
}

function isObject(value: unknown): value is JsonObject {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function canonicalize(value: unknown): string {
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

function pathEscapes(value: string): boolean {
  return (
    isAbsolute(value) ||
    win32.isAbsolute(value) ||
    value.replaceAll("\\", "/").split("/").some((segment) => segment === "..")
  );
}

export function validateJsonSchema(
  schemaPath: string,
  value: unknown,
  instancePath = "$",
): JsonSchemaViolation[] {
  return validateValue(readSchema(schemaPath), value, instancePath, dirname(schemaPath));
}

function validateValue(
  schema: JsonObject,
  value: unknown,
  path: string,
  schemaDir: string,
): JsonSchemaViolation[] {
  if (typeof schema.$ref === "string") {
    const referenced = resolve(schemaDir, schema.$ref);
    return validateValue(readSchema(referenced), value, path, dirname(referenced));
  }

  const violations: JsonSchemaViolation[] = [];
  const fail = (keyword: string, detail: string): void => {
    violations.push({ keyword, path, detail });
  };

  if (Array.isArray(schema.allOf)) {
    for (const entry of schema.allOf) {
      if (isObject(entry)) {
        violations.push(...validateValue(entry, value, path, schemaDir));
      }
    }
  }
  if (isObject(schema.if) && isObject(schema.then)) {
    if (validateValue(schema.if, value, path, schemaDir).length === 0) {
      violations.push(...validateValue(schema.then, value, path, schemaDir));
    }
  }

  if (schema.type !== undefined) {
    const matches =
      (schema.type === "object" && isObject(value)) ||
      (schema.type === "array" && Array.isArray(value)) ||
      (schema.type === "string" && typeof value === "string") ||
      (schema.type === "boolean" && typeof value === "boolean") ||
      (schema.type === "number" && typeof value === "number") ||
      (schema.type === "integer" && Number.isInteger(value));
    if (!matches) {
      fail("type", `expected ${schema.type}`);
      return violations;
    }
  }
  if (schema.const !== undefined && !Object.is(value, schema.const)) {
    fail("const", `expected ${JSON.stringify(schema.const)}`);
  }
  if (Array.isArray(schema.enum) && !schema.enum.some((entry: unknown) => Object.is(entry, value))) {
    fail("enum", `expected one of ${JSON.stringify(schema.enum)}`);
  }

  if (typeof value === "string") {
    if (typeof schema.minLength === "number" && value.length < schema.minLength) {
      fail("minLength", `expected at least ${schema.minLength} characters`);
    }
    if (typeof schema.pattern === "string" && !new RegExp(schema.pattern).test(value)) {
      fail("pattern", `does not match ${schema.pattern}`);
    }
    if (schema["x-project-relative-path"] === true && pathEscapes(value)) {
      fail("x-project-relative-path", "path must remain below the project root");
    }
  }

  if (Array.isArray(value)) {
    if (typeof schema.minItems === "number" && value.length < schema.minItems) {
      fail("minItems", `expected at least ${schema.minItems} items`);
    }
    if (schema.uniqueItems === true) {
      const identities = value.map(canonicalize);
      if (new Set(identities).size !== identities.length) {
        fail("uniqueItems", "array contains duplicates");
      }
    }
    if (isObject(schema.items)) {
      value.forEach((entry, index) => {
        violations.push(...validateValue(schema.items, entry, `${path}[${index}]`, schemaDir));
      });
    }
    if (
      isObject(schema.contains) &&
      !value.some((entry) => validateValue(schema.contains, entry, path, schemaDir).length === 0)
    ) {
      fail("contains", "no item satisfies the required formation condition");
    }
  }

  if (isObject(value)) {
    if (typeof schema.minProperties === "number" && Object.keys(value).length < schema.minProperties) {
      fail("minProperties", `expected at least ${schema.minProperties} properties`);
    }
    if (Array.isArray(schema.required)) {
      for (const required of schema.required as string[]) {
        if (!(required in value)) {
          violations.push({ keyword: "required", path, detail: `missing ${required}` });
        }
      }
    }
    const properties = isObject(schema.properties) ? schema.properties : {};
    for (const [key, entry] of Object.entries(value)) {
      if (key in properties && isObject(properties[key])) {
        violations.push(...validateValue(properties[key], entry, `${path}.${key}`, schemaDir));
      } else if (schema.additionalProperties === false) {
        violations.push({ keyword: "additionalProperties", path, detail: `unexpected ${key}` });
      }
    }
  }

  return violations;
}
