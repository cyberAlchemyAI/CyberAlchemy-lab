import {
  DS_SFOL_LANGUAGE_VERSION,
  NODE_LOGIC_SCHEMA_VERSION,
  type LogicClause,
  type LogicClauseKind,
  type LogicClauseStatus,
  type LogicDeclaration,
  type LogicScalar,
  type LogicTerm,
  type NodeLogicModuleV1,
  type ParameterDeclaration,
  type SortRef,
  type SourcePosition,
  type SourceSpan,
} from "./ast.js";
import { resolveSfolLanguageProfile } from "./profiles.js";

export type SfolDecodeDiagnosticCode =
  | "SFOL_DECODE_STRUCTURED_INPUT_REQUIRED"
  | "SFOL_DECODE_EXPECTED_OBJECT"
  | "SFOL_DECODE_EXPECTED_ARRAY"
  | "SFOL_DECODE_EXPECTED_STRING"
  | "SFOL_DECODE_EXPECTED_BOOLEAN"
  | "SFOL_DECODE_EXPECTED_INTEGER"
  | "SFOL_DECODE_MISSING_FIELD"
  | "SFOL_DECODE_UNKNOWN_FIELD"
  | "SFOL_DECODE_UNKNOWN_TAG"
  | "SFOL_DECODE_UNKNOWN_SCHEMA_VERSION"
  | "SFOL_DECODE_UNKNOWN_LANGUAGE_VERSION"
  | "SFOL_DECODE_DUPLICATE_ID"
  | "SFOL_DECODE_INVALID_SOURCE_PATH"
  | "SFOL_DECODE_SOURCE_ID_MISMATCH"
  | "SFOL_DECODE_INVALID_LITERAL"
  | "SFOL_DECODE_RESOURCE_LIMIT";

export interface SfolDecodeDiagnostic {
  readonly code: SfolDecodeDiagnosticCode;
  readonly stage: "decode";
  readonly path: string;
  readonly detail: string;
}

export type SfolDecodeResult =
  | {
      readonly ok: true;
      readonly value: NodeLogicModuleV1;
    }
  | {
      readonly ok: false;
      readonly diagnostics: readonly SfolDecodeDiagnostic[];
    };

const MAX_TERM_DEPTH = 128;
const IDENTIFIER = /^[A-Za-z0-9][A-Za-z0-9._-]*$/;
const INTEGER = /^-?(?:0|[1-9][0-9]*)$/;
const CLAUSE_KINDS: readonly LogicClauseKind[] = [
  "function",
  "predicate",
  "invariant",
  "precondition",
  "postcondition",
  "transition",
  "effect-relation",
];
const CLAUSE_STATUSES: readonly LogicClauseStatus[] = ["candidate", "admitted"];

class DecodeAbort extends Error {
  readonly diagnostic: SfolDecodeDiagnostic;

  constructor(diagnostic: SfolDecodeDiagnostic) {
    super(`${diagnostic.code} at ${diagnostic.path}: ${diagnostic.detail}`);
    this.name = "DecodeAbort";
    this.diagnostic = diagnostic;
  }
}

export function decodeNodeLogicModule(input: unknown): SfolDecodeResult {
  try {
    if (typeof input === "string") {
      fail(
        "SFOL_DECODE_STRUCTURED_INPUT_REQUIRED",
        "$",
        "DS-SFOL v1 accepts structured node logic, not prose or code strings",
      );
    }
    const record = exactRecord(input, "$", [
      "schema_version",
      "language_version",
      "module_id",
      "source",
      "declarations",
      "clauses",
    ]);
    const schemaVersion = requiredString(record, "schema_version", "$");
    if (schemaVersion !== NODE_LOGIC_SCHEMA_VERSION) {
      fail(
        "SFOL_DECODE_UNKNOWN_SCHEMA_VERSION",
        "$.schema_version",
        `unsupported node-logic schema version ${schemaVersion}`,
      );
    }
    const languageVersion = requiredString(record, "language_version", "$");
    const profileResult = resolveSfolLanguageProfile(languageVersion);
    if (!profileResult.ok) {
      fail(
        "SFOL_DECODE_UNKNOWN_LANGUAGE_VERSION",
        "$.language_version",
        profileResult.diagnostics[0]?.detail ??
          `unsupported DS-SFOL language version ${languageVersion}`,
      );
    }
    const moduleId = identifier(
      requiredString(record, "module_id", "$"),
      "$.module_id",
    );
    const source = decodeSource(required(record, "source", "$"), "$.source");
    const declarations = decodeArray(
      required(record, "declarations", "$"),
      "$.declarations",
      (item, path) => decodeDeclaration(item, path, source.source_id),
    );
    const clauses = decodeArray(
      required(record, "clauses", "$"),
      "$.clauses",
      (item, path) => decodeClause(item, path, source.source_id),
    );

    assertUnique(
      declarations.map(({ declaration_id }) => declaration_id),
      "$.declarations",
      "declaration_id",
    );
    assertUnique(
      clauses.map(({ clause_id }) => clause_id),
      "$.clauses",
      "clause_id",
    );

    return Object.freeze({
      ok: true,
      value: deepFreeze({
        schema_version: NODE_LOGIC_SCHEMA_VERSION,
        language_version: DS_SFOL_LANGUAGE_VERSION,
        module_id: moduleId,
        source,
        declarations: [...declarations].sort((left, right) =>
          left.declaration_id.localeCompare(right.declaration_id),
        ),
        clauses: [...clauses].sort((left, right) =>
          left.clause_id.localeCompare(right.clause_id),
        ),
      }),
    });
  } catch (error) {
    if (error instanceof DecodeAbort) {
      return Object.freeze({
        ok: false,
        diagnostics: Object.freeze([Object.freeze(error.diagnostic)]),
      });
    }
    throw error;
  }
}

function decodeSource(
  input: unknown,
  path: string,
): NodeLogicModuleV1["source"] {
  const record = exactRecord(input, path, [
    "feature_id",
    "node_id",
    "source_id",
    "source_path",
  ]);
  const sourcePath = requiredString(record, "source_path", path);
  if (
    sourcePath.length === 0 ||
    sourcePath.startsWith("/") ||
    /^[A-Za-z]:[\\/]/.test(sourcePath) ||
    sourcePath.split(/[\\/]/).includes("..")
  ) {
    fail(
      "SFOL_DECODE_INVALID_SOURCE_PATH",
      `${path}.source_path`,
      "source_path must be a non-empty node-local relative path",
    );
  }
  return {
    feature_id: identifier(
      requiredString(record, "feature_id", path),
      `${path}.feature_id`,
    ),
    node_id: identifier(
      requiredString(record, "node_id", path),
      `${path}.node_id`,
    ),
    source_id: identifier(
      requiredString(record, "source_id", path),
      `${path}.source_id`,
    ),
    source_path: sourcePath,
  };
}

function decodeDeclaration(
  input: unknown,
  path: string,
  sourceId: string,
): LogicDeclaration {
  const tagged = taggedRecord(input, path);
  switch (tagged.tag) {
    case "enum": {
      const record = exactRecord(input, path, [
        "tag",
        "declaration_id",
        "members",
        "span",
      ]);
      const members = decodeArray(
        required(record, "members", path),
        `${path}.members`,
        (item, memberPath) => stringValue(item, memberPath),
      );
      assertUnique(members, `${path}.members`, "member");
      return {
        tag: "enum",
        declaration_id: declarationId(record, path),
        members,
        span: decodeSpan(required(record, "span", path), `${path}.span`, sourceId),
      };
    }
    case "record": {
      const record = exactRecord(input, path, [
        "tag",
        "declaration_id",
        "fields",
        "span",
      ]);
      const fields = decodeArray(
        required(record, "fields", path),
        `${path}.fields`,
        (item, fieldPath) => {
          const field = exactRecord(item, fieldPath, [
            "name",
            "sort",
            "required",
            "span",
          ]);
          return {
            name: identifier(
              requiredString(field, "name", fieldPath),
              `${fieldPath}.name`,
            ),
            sort: decodeSort(
              required(field, "sort", fieldPath),
              `${fieldPath}.sort`,
            ),
            required: booleanValue(
              required(field, "required", fieldPath),
              `${fieldPath}.required`,
            ),
            span: decodeSpan(
              required(field, "span", fieldPath),
              `${fieldPath}.span`,
              sourceId,
            ),
          };
        },
      );
      assertUnique(
        fields.map(({ name }) => name),
        `${path}.fields`,
        "field name",
      );
      return {
        tag: "record",
        declaration_id: declarationId(record, path),
        fields,
        span: decodeSpan(required(record, "span", path), `${path}.span`, sourceId),
      };
    }
    case "function": {
      const record = exactRecord(input, path, [
        "tag",
        "declaration_id",
        "parameters",
        "result",
        "body",
        "span",
      ]);
      return {
        tag: "function",
        declaration_id: declarationId(record, path),
        parameters: decodeParameters(
          required(record, "parameters", path),
          `${path}.parameters`,
          sourceId,
        ),
        result: decodeSort(required(record, "result", path), `${path}.result`),
        body: decodeTerm(
          required(record, "body", path),
          `${path}.body`,
          sourceId,
          0,
        ),
        span: decodeSpan(required(record, "span", path), `${path}.span`, sourceId),
      };
    }
    case "predicate": {
      const record = exactRecord(input, path, [
        "tag",
        "declaration_id",
        "parameters",
        "body",
        "span",
      ]);
      return {
        tag: "predicate",
        declaration_id: declarationId(record, path),
        parameters: decodeParameters(
          required(record, "parameters", path),
          `${path}.parameters`,
          sourceId,
        ),
        body: decodeTerm(
          required(record, "body", path),
          `${path}.body`,
          sourceId,
          0,
        ),
        span: decodeSpan(required(record, "span", path), `${path}.span`, sourceId),
      };
    }
    case "fixture-universe": {
      const record = exactRecord(input, path, [
        "tag",
        "declaration_id",
        "element_sort",
        "admits_empty",
        "span",
      ]);
      return {
        tag: "fixture-universe",
        declaration_id: declarationId(record, path),
        element_sort: decodeSort(
          required(record, "element_sort", path),
          `${path}.element_sort`,
        ),
        admits_empty: booleanValue(
          required(record, "admits_empty", path),
          `${path}.admits_empty`,
        ),
        span: decodeSpan(required(record, "span", path), `${path}.span`, sourceId),
      };
    }
    default:
      fail(
        "SFOL_DECODE_UNKNOWN_TAG",
        `${path}.tag`,
        `unsupported DS-SFOL v1 declaration tag ${tagged.tag}`,
      );
  }
}

function decodeClause(
  input: unknown,
  path: string,
  sourceId: string,
): LogicClause {
  const record = exactRecord(input, path, [
    "clause_id",
    "kind",
    "status",
    "inputs",
    "result_sort",
    "expression",
    "observation_sort",
    "span",
  ]);
  const observation = required(record, "observation_sort", path);
  return {
    clause_id: identifier(
      requiredString(record, "clause_id", path),
      `${path}.clause_id`,
    ),
    kind: enumValue(
      requiredString(record, "kind", path),
      CLAUSE_KINDS,
      `${path}.kind`,
      "clause kind",
    ),
    status: enumValue(
      requiredString(record, "status", path),
      CLAUSE_STATUSES,
      `${path}.status`,
      "clause status",
    ),
    inputs: decodeParameters(
      required(record, "inputs", path),
      `${path}.inputs`,
      sourceId,
    ),
    result_sort: decodeSort(
      required(record, "result_sort", path),
      `${path}.result_sort`,
    ),
    expression: decodeTerm(
      required(record, "expression", path),
      `${path}.expression`,
      sourceId,
      0,
    ),
    observation_sort:
      observation === null
        ? null
        : decodeSort(observation, `${path}.observation_sort`),
    span: decodeSpan(required(record, "span", path), `${path}.span`, sourceId),
  };
}

function decodeParameters(
  input: unknown,
  path: string,
  sourceId: string,
): readonly ParameterDeclaration[] {
  const parameters = decodeArray(input, path, (item, parameterPath) => {
    const record = exactRecord(item, parameterPath, ["name", "sort", "span"]);
    return {
      name: identifier(
        requiredString(record, "name", parameterPath),
        `${parameterPath}.name`,
      ),
      sort: decodeSort(
        required(record, "sort", parameterPath),
        `${parameterPath}.sort`,
      ),
      span: decodeSpan(
        required(record, "span", parameterPath),
        `${parameterPath}.span`,
        sourceId,
      ),
    };
  });
  assertUnique(
    parameters.map(({ name }) => name),
    path,
    "parameter name",
  );
  return parameters;
}

function decodeTerm(
  input: unknown,
  path: string,
  sourceId: string,
  depth: number,
): LogicTerm {
  if (depth > MAX_TERM_DEPTH) {
    fail(
      "SFOL_DECODE_RESOURCE_LIMIT",
      path,
      `term nesting exceeds ${MAX_TERM_DEPTH}`,
    );
  }
  const next = depth + 1;
  const tagged = taggedRecord(input, path);
  switch (tagged.tag) {
    case "literal": {
      const record = exactRecord(input, path, ["tag", "value", "span"]);
      return {
        tag: "literal",
        value: decodeScalar(required(record, "value", path), `${path}.value`),
        span: decodeSpan(required(record, "span", path), `${path}.span`, sourceId),
      };
    }
    case "variable": {
      const record = exactRecord(input, path, ["tag", "name", "span"]);
      return {
        tag: "variable",
        name: identifier(
          requiredString(record, "name", path),
          `${path}.name`,
        ),
        span: decodeSpan(required(record, "span", path), `${path}.span`, sourceId),
      };
    }
    case "field": {
      const record = exactRecord(input, path, [
        "tag",
        "target",
        "field",
        "span",
      ]);
      return {
        tag: "field",
        target: decodeTerm(
          required(record, "target", path),
          `${path}.target`,
          sourceId,
          next,
        ),
        field: identifier(
          requiredString(record, "field", path),
          `${path}.field`,
        ),
        span: decodeSpan(required(record, "span", path), `${path}.span`, sourceId),
      };
    }
    case "record": {
      const record = exactRecord(input, path, [
        "tag",
        "declaration_id",
        "fields",
        "span",
      ]);
      const fields = decodeArray(
        required(record, "fields", path),
        `${path}.fields`,
        (item, fieldPath) => {
          const field = exactRecord(item, fieldPath, ["name", "value"]);
          return {
            name: identifier(
              requiredString(field, "name", fieldPath),
              `${fieldPath}.name`,
            ),
            value: decodeTerm(
              required(field, "value", fieldPath),
              `${fieldPath}.value`,
              sourceId,
              next,
            ),
          };
        },
      );
      assertUnique(
        fields.map(({ name }) => name),
        `${path}.fields`,
        "record field",
      );
      return {
        tag: "record",
        declaration_id: identifier(
          requiredString(record, "declaration_id", path),
          `${path}.declaration_id`,
        ),
        fields: [...fields].sort((left, right) =>
          left.name.localeCompare(right.name),
        ),
        span: decodeSpan(required(record, "span", path), `${path}.span`, sourceId),
      };
    }
    case "list":
    case "set": {
      const record = exactRecord(input, path, ["tag", "items", "span"]);
      return {
        tag: tagged.tag,
        items: decodeArray(
          required(record, "items", path),
          `${path}.items`,
          (item, itemPath) => decodeTerm(item, itemPath, sourceId, next),
        ),
        span: decodeSpan(required(record, "span", path), `${path}.span`, sourceId),
      };
    }
    case "enum": {
      const record = exactRecord(input, path, [
        "tag",
        "declaration_id",
        "member",
        "span",
      ]);
      return {
        tag: "enum",
        declaration_id: identifier(
          requiredString(record, "declaration_id", path),
          `${path}.declaration_id`,
        ),
        member: identifier(
          requiredString(record, "member", path),
          `${path}.member`,
        ),
        span: decodeSpan(required(record, "span", path), `${path}.span`, sourceId),
      };
    }
    case "arithmetic": {
      const record = exactRecord(input, path, [
        "tag",
        "operator",
        "left",
        "right",
        "span",
      ]);
      return {
        tag: "arithmetic",
        operator: enumValue(
          requiredString(record, "operator", path),
          ["add", "subtract", "multiply", "divide"] as const,
          `${path}.operator`,
          "arithmetic operator",
        ),
        left: decodeTerm(
          required(record, "left", path),
          `${path}.left`,
          sourceId,
          next,
        ),
        right: decodeTerm(
          required(record, "right", path),
          `${path}.right`,
          sourceId,
          next,
        ),
        span: decodeSpan(required(record, "span", path), `${path}.span`, sourceId),
      };
    }
    case "negate":
    case "not": {
      const record = exactRecord(input, path, ["tag", "operand", "span"]);
      return {
        tag: tagged.tag,
        operand: decodeTerm(
          required(record, "operand", path),
          `${path}.operand`,
          sourceId,
          next,
        ),
        span: decodeSpan(required(record, "span", path), `${path}.span`, sourceId),
      };
    }
    case "comparison": {
      const record = exactRecord(input, path, [
        "tag",
        "operator",
        "left",
        "right",
        "span",
      ]);
      return {
        tag: "comparison",
        operator: enumValue(
          requiredString(record, "operator", path),
          ["eq", "neq", "lt", "lte", "gt", "gte"] as const,
          `${path}.operator`,
          "comparison operator",
        ),
        left: decodeTerm(
          required(record, "left", path),
          `${path}.left`,
          sourceId,
          next,
        ),
        right: decodeTerm(
          required(record, "right", path),
          `${path}.right`,
          sourceId,
          next,
        ),
        span: decodeSpan(required(record, "span", path), `${path}.span`, sourceId),
      };
    }
    case "boolean": {
      const record = exactRecord(input, path, [
        "tag",
        "operator",
        "operands",
        "span",
      ]);
      return {
        tag: "boolean",
        operator: enumValue(
          requiredString(record, "operator", path),
          ["and", "or"] as const,
          `${path}.operator`,
          "Boolean operator",
        ),
        operands: decodeArray(
          required(record, "operands", path),
          `${path}.operands`,
          (item, itemPath) => decodeTerm(item, itemPath, sourceId, next),
        ),
        span: decodeSpan(required(record, "span", path), `${path}.span`, sourceId),
      };
    }
    case "conditional": {
      const record = exactRecord(input, path, [
        "tag",
        "condition",
        "when_true",
        "when_false",
        "span",
      ]);
      return {
        tag: "conditional",
        condition: decodeTerm(
          required(record, "condition", path),
          `${path}.condition`,
          sourceId,
          next,
        ),
        when_true: decodeTerm(
          required(record, "when_true", path),
          `${path}.when_true`,
          sourceId,
          next,
        ),
        when_false: decodeTerm(
          required(record, "when_false", path),
          `${path}.when_false`,
          sourceId,
          next,
        ),
        span: decodeSpan(required(record, "span", path), `${path}.span`, sourceId),
      };
    }
    case "fold": {
      const record = exactRecord(input, path, [
        "tag",
        "operator",
        "collection",
        "item_name",
        "expression",
        "span",
      ]);
      const expression = required(record, "expression", path);
      return {
        tag: "fold",
        operator: enumValue(
          requiredString(record, "operator", path),
          ["sum", "product", "minimum", "maximum", "count"] as const,
          `${path}.operator`,
          "fold operator",
        ),
        collection: decodeTerm(
          required(record, "collection", path),
          `${path}.collection`,
          sourceId,
          next,
        ),
        item_name: identifier(
          requiredString(record, "item_name", path),
          `${path}.item_name`,
        ),
        expression:
          expression === null
            ? null
            : decodeTerm(expression, `${path}.expression`, sourceId, next),
        span: decodeSpan(required(record, "span", path), `${path}.span`, sourceId),
      };
    }
    case "quantifier": {
      const record = exactRecord(input, path, [
        "tag",
        "operator",
        "universe_id",
        "variable_name",
        "variable_sort",
        "predicate",
        "span",
      ]);
      return {
        tag: "quantifier",
        operator: enumValue(
          requiredString(record, "operator", path),
          ["exists", "forall"] as const,
          `${path}.operator`,
          "quantifier operator",
        ),
        universe_id: identifier(
          requiredString(record, "universe_id", path),
          `${path}.universe_id`,
        ),
        variable_name: identifier(
          requiredString(record, "variable_name", path),
          `${path}.variable_name`,
        ),
        variable_sort: decodeSort(
          required(record, "variable_sort", path),
          `${path}.variable_sort`,
        ),
        predicate: decodeTerm(
          required(record, "predicate", path),
          `${path}.predicate`,
          sourceId,
          next,
        ),
        span: decodeSpan(required(record, "span", path), `${path}.span`, sourceId),
      };
    }
    case "call": {
      const record = exactRecord(input, path, [
        "tag",
        "declaration_id",
        "arguments",
        "span",
      ]);
      return {
        tag: "call",
        declaration_id: identifier(
          requiredString(record, "declaration_id", path),
          `${path}.declaration_id`,
        ),
        arguments: decodeArray(
          required(record, "arguments", path),
          `${path}.arguments`,
          (item, itemPath) => decodeTerm(item, itemPath, sourceId, next),
        ),
        span: decodeSpan(required(record, "span", path), `${path}.span`, sourceId),
      };
    }
    default:
      fail(
        "SFOL_DECODE_UNKNOWN_TAG",
        `${path}.tag`,
        `unsupported DS-SFOL v1 term tag ${tagged.tag}`,
      );
  }
}

function decodeSort(input: unknown, path: string): SortRef {
  const tagged = taggedRecord(input, path);
  switch (tagged.tag) {
    case "primitive": {
      const record = exactRecord(input, path, ["tag", "name"]);
      return {
        tag: "primitive",
        name: enumValue(
          requiredString(record, "name", path),
          ["boolean", "string", "integer", "rational"] as const,
          `${path}.name`,
          "primitive sort",
        ),
      };
    }
    case "named": {
      const record = exactRecord(input, path, ["tag", "declaration_id"]);
      return {
        tag: "named",
        declaration_id: identifier(
          requiredString(record, "declaration_id", path),
          `${path}.declaration_id`,
        ),
      };
    }
    case "list":
    case "set": {
      const record = exactRecord(input, path, ["tag", "element"]);
      return {
        tag: tagged.tag,
        element: decodeSort(required(record, "element", path), `${path}.element`),
      };
    }
    default:
      fail(
        "SFOL_DECODE_UNKNOWN_TAG",
        `${path}.tag`,
        `unsupported DS-SFOL v1 sort tag ${tagged.tag}`,
      );
  }
}

function decodeScalar(input: unknown, path: string): LogicScalar {
  const tagged = taggedRecord(input, path);
  switch (tagged.tag) {
    case "boolean": {
      const record = exactRecord(input, path, ["tag", "value"]);
      return {
        tag: "boolean",
        value: booleanValue(required(record, "value", path), `${path}.value`),
      };
    }
    case "string": {
      const record = exactRecord(input, path, ["tag", "value"]);
      return {
        tag: "string",
        value: stringValue(required(record, "value", path), `${path}.value`),
      };
    }
    case "integer": {
      const record = exactRecord(input, path, ["tag", "value"]);
      const value = stringValue(required(record, "value", path), `${path}.value`);
      if (!INTEGER.test(value)) {
        fail(
          "SFOL_DECODE_INVALID_LITERAL",
          `${path}.value`,
          "integer literals must be canonical base-10 strings",
        );
      }
      return { tag: "integer", value };
    }
    case "rational": {
      const record = exactRecord(input, path, [
        "tag",
        "numerator",
        "denominator",
      ]);
      const numerator = stringValue(
        required(record, "numerator", path),
        `${path}.numerator`,
      );
      const denominator = stringValue(
        required(record, "denominator", path),
        `${path}.denominator`,
      );
      if (
        !INTEGER.test(numerator) ||
        !/^[1-9][0-9]*$/.test(denominator)
      ) {
        fail(
          "SFOL_DECODE_INVALID_LITERAL",
          path,
          "rational literals require a canonical integer numerator and positive denominator",
        );
      }
      return { tag: "rational", numerator, denominator };
    }
    default:
      fail(
        "SFOL_DECODE_UNKNOWN_TAG",
        `${path}.tag`,
        `unsupported DS-SFOL v1 scalar tag ${tagged.tag}`,
      );
  }
}

function decodeSpan(
  input: unknown,
  path: string,
  sourceId: string,
): SourceSpan {
  const record = exactRecord(input, path, [
    "source_id",
    "path",
    "start",
    "end",
  ]);
  const actualSourceId = requiredString(record, "source_id", path);
  if (actualSourceId !== sourceId) {
    fail(
      "SFOL_DECODE_SOURCE_ID_MISMATCH",
      `${path}.source_id`,
      `expected ${sourceId}; received ${actualSourceId}`,
    );
  }
  const localPath = requiredString(record, "path", path);
  if (
    !/^body\.logic(?:\.|\[|$)/.test(localPath) ||
    localPath.includes("..") ||
    localPath.startsWith("/")
  ) {
    fail(
      "SFOL_DECODE_INVALID_SOURCE_PATH",
      `${path}.path`,
      "span path must stay under body.logic",
    );
  }
  const start = decodePosition(required(record, "start", path), `${path}.start`);
  const end = decodePosition(required(record, "end", path), `${path}.end`);
  if (
    end.line < start.line ||
    (end.line === start.line && end.column < start.column)
  ) {
    fail(
      "SFOL_DECODE_INVALID_SOURCE_PATH",
      `${path}.end`,
      "span end must not precede span start",
    );
  }
  return {
    source_id: actualSourceId,
    path: localPath,
    start,
    end,
  };
}

function decodePosition(input: unknown, path: string): SourcePosition {
  const record = exactRecord(input, path, ["line", "column"]);
  return {
    line: positiveInteger(required(record, "line", path), `${path}.line`),
    column: positiveInteger(
      required(record, "column", path),
      `${path}.column`,
    ),
  };
}

function declarationId(
  record: Readonly<Record<string, unknown>>,
  path: string,
): string {
  return identifier(
    requiredString(record, "declaration_id", path),
    `${path}.declaration_id`,
  );
}

function taggedRecord(
  input: unknown,
  path: string,
): Readonly<Record<string, unknown>> & { readonly tag: string } {
  const record = recordValue(input, path);
  requiredString(record, "tag", path);
  return record as Readonly<Record<string, unknown>> & {
    readonly tag: string;
  };
}

function exactRecord(
  input: unknown,
  path: string,
  keys: readonly string[],
): Readonly<Record<string, unknown>> {
  const record = recordValue(input, path);
  for (const key of keys) {
    if (!Object.hasOwn(record, key)) {
      fail(
        "SFOL_DECODE_MISSING_FIELD",
        `${path}.${key}`,
        `required field ${key} is missing`,
      );
    }
  }
  const unknownKeys = Object.keys(record)
    .filter((key) => !keys.includes(key))
    .sort();
  if (unknownKeys[0] !== undefined) {
    fail(
      "SFOL_DECODE_UNKNOWN_FIELD",
      `${path}.${unknownKeys[0]}`,
      `unsupported field ${unknownKeys[0]}`,
    );
  }
  return record;
}

function recordValue(
  input: unknown,
  path: string,
): Readonly<Record<string, unknown>> {
  if (
    typeof input !== "object" ||
    input === null ||
    Array.isArray(input)
  ) {
    fail(
      "SFOL_DECODE_EXPECTED_OBJECT",
      path,
      "expected a structured object",
    );
  }
  return input as Readonly<Record<string, unknown>>;
}

function required(
  record: Readonly<Record<string, unknown>>,
  key: string,
  path: string,
): unknown {
  if (!Object.hasOwn(record, key)) {
    fail(
      "SFOL_DECODE_MISSING_FIELD",
      `${path}.${key}`,
      `required field ${key} is missing`,
    );
  }
  return record[key];
}

function requiredString(
  record: Readonly<Record<string, unknown>>,
  key: string,
  path: string,
): string {
  return stringValue(required(record, key, path), `${path}.${key}`);
}

function stringValue(input: unknown, path: string): string {
  if (typeof input !== "string") {
    fail("SFOL_DECODE_EXPECTED_STRING", path, "expected a string");
  }
  return input;
}

function booleanValue(input: unknown, path: string): boolean {
  if (typeof input !== "boolean") {
    fail("SFOL_DECODE_EXPECTED_BOOLEAN", path, "expected a Boolean");
  }
  return input;
}

function positiveInteger(input: unknown, path: string): number {
  if (!Number.isInteger(input) || typeof input !== "number" || input < 1) {
    fail(
      "SFOL_DECODE_EXPECTED_INTEGER",
      path,
      "expected a positive integer",
    );
  }
  return input;
}

function identifier(input: string, path: string): string {
  if (!IDENTIFIER.test(input)) {
    fail(
      "SFOL_DECODE_EXPECTED_STRING",
      path,
      "expected a non-empty stable identifier",
    );
  }
  return input;
}

function decodeArray<T>(
  input: unknown,
  path: string,
  decode: (item: unknown, path: string) => T,
): readonly T[] {
  if (!Array.isArray(input)) {
    fail("SFOL_DECODE_EXPECTED_ARRAY", path, "expected an array");
  }
  return input.map((item, index) => decode(item, `${path}[${index}]`));
}

function assertUnique(
  values: readonly string[],
  path: string,
  label: string,
): void {
  const seen = new Set<string>();
  for (let index = 0; index < values.length; index += 1) {
    const value = values[index];
    if (value !== undefined && seen.has(value)) {
      fail(
        "SFOL_DECODE_DUPLICATE_ID",
        `${path}[${index}]`,
        `duplicate ${label} ${value}`,
      );
    }
    if (value !== undefined) {
      seen.add(value);
    }
  }
}

function enumValue<const Values extends readonly string[]>(
  value: string,
  values: Values,
  path: string,
  label: string,
): Values[number] {
  if (!values.includes(value)) {
    fail(
      "SFOL_DECODE_UNKNOWN_TAG",
      path,
      `unsupported ${label} ${value}`,
    );
  }
  return value;
}

function fail(
  code: SfolDecodeDiagnosticCode,
  path: string,
  detail: string,
): never {
  throw new DecodeAbort({ code, stage: "decode", path, detail });
}

function deepFreeze<T>(value: T): T {
  if (typeof value !== "object" || value === null || Object.isFrozen(value)) {
    return value;
  }
  for (const child of Object.values(value)) {
    deepFreeze(child);
  }
  return Object.freeze(value);
}
