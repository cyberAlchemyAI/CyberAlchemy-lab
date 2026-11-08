import type {
  LogicTerm,
  LogicTermTag,
  SourceSpan,
} from "./ast.js";

export type SfolLanguageDiagnosticCode =
  | "SFOL_LANGUAGE_UNKNOWN_VERSION"
  | "SFOL_LANGUAGE_UNKNOWN_TAG"
  | "SFOL_LANGUAGE_NON_JSON_VALUE"
  | "SFOL_LANGUAGE_CYCLIC_VALUE";

export interface SfolLanguageDiagnostic {
  readonly code: SfolLanguageDiagnosticCode;
  readonly stage: "contract";
  readonly path: string;
  readonly detail: string;
  readonly span?: SourceSpan;
}

export type SfolContractResult<T> =
  | {
      readonly ok: true;
      readonly value: T;
    }
  | {
      readonly ok: false;
      readonly diagnostics: readonly SfolLanguageDiagnostic[];
    };

export class SfolLanguageContractError extends Error {
  readonly diagnostic: SfolLanguageDiagnostic;

  constructor(diagnostic: SfolLanguageDiagnostic) {
    super(`${diagnostic.code} at ${diagnostic.path}: ${diagnostic.detail}`);
    this.name = "SfolLanguageContractError";
    this.diagnostic = diagnostic;
  }
}

export function contractSuccess<T>(value: T): SfolContractResult<T> {
  return Object.freeze({ ok: true, value });
}

export function contractFailure<T>(
  diagnostic: SfolLanguageDiagnostic,
): SfolContractResult<T> {
  return Object.freeze({
    ok: false,
    diagnostics: Object.freeze([Object.freeze(diagnostic)]),
  });
}

export function logicTermTag(term: LogicTerm): LogicTermTag {
  switch (term.tag) {
    case "literal":
    case "variable":
    case "field":
    case "record":
    case "list":
    case "set":
    case "enum":
    case "arithmetic":
    case "negate":
    case "comparison":
    case "boolean":
    case "not":
    case "conditional":
    case "fold":
    case "quantifier":
    case "call":
      return term.tag;
    default:
      return failUnknownTag(term);
  }
}

export function canonicalJson(value: unknown): string {
  const seen = new Set<object>();
  return JSON.stringify(canonicalize(value, "$", seen));
}

function canonicalize(
  value: unknown,
  path: string,
  seen: Set<object>,
): unknown {
  if (
    value === null ||
    typeof value === "string" ||
    typeof value === "boolean"
  ) {
    return value;
  }
  if (typeof value === "number") {
    if (Number.isFinite(value)) {
      return value;
    }
    throw contractError(
      "SFOL_LANGUAGE_NON_JSON_VALUE",
      path,
      "non-finite numbers are not deterministic JSON values",
    );
  }
  if (Array.isArray(value)) {
    enter(value, path, seen);
    const result = value.map((item, index) =>
      canonicalize(item, `${path}[${index}]`, seen),
    );
    seen.delete(value);
    return result;
  }
  if (isRecord(value)) {
    enter(value, path, seen);
    const result: Record<string, unknown> = {};
    for (const key of Object.keys(value).sort()) {
      result[key] = canonicalize(value[key], `${path}.${key}`, seen);
    }
    seen.delete(value);
    return result;
  }
  throw contractError(
    "SFOL_LANGUAGE_NON_JSON_VALUE",
    path,
    `unsupported JSON value type ${typeof value}`,
  );
}

function enter(value: object, path: string, seen: Set<object>): void {
  if (seen.has(value)) {
    throw contractError(
      "SFOL_LANGUAGE_CYCLIC_VALUE",
      path,
      "cyclic values cannot be serialized",
    );
  }
  seen.add(value);
}

function isRecord(value: unknown): value is Readonly<Record<string, unknown>> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function failUnknownTag(value: never): never {
  const unknownValue: unknown = value;
  const tag =
    isRecord(unknownValue) && typeof unknownValue.tag === "string"
      ? unknownValue.tag
      : "<missing>";
  throw contractError(
    "SFOL_LANGUAGE_UNKNOWN_TAG",
    "$.tag",
    `unsupported DS-SFOL v1 term tag ${tag}`,
  );
}

function contractError(
  code: SfolLanguageDiagnosticCode,
  path: string,
  detail: string,
): SfolLanguageContractError {
  return new SfolLanguageContractError({
    code,
    stage: "contract",
    path,
    detail,
  });
}
