import type {
  FixtureUniverseDeclaration,
  FunctionDeclaration,
  LogicTerm,
  PredicateDeclaration,
  SourceSpan,
} from "../language/ast.js";
import type { TypedLogicModule } from "../language/typecheck.js";

export interface BooleanValue {
  readonly tag: "boolean";
  readonly value: boolean;
}

export interface StringValue {
  readonly tag: "string";
  readonly value: string;
}

export interface IntegerValue {
  readonly tag: "integer";
  readonly value: string;
}

export interface RationalValue {
  readonly tag: "rational";
  readonly numerator: string;
  readonly denominator: string;
}

export interface EnumValue {
  readonly tag: "enum";
  readonly declaration_id: string;
  readonly member: string;
}

export interface RecordValue {
  readonly tag: "record";
  readonly declaration_id: string;
  readonly fields: Readonly<Record<string, SemanticValue>>;
}

export interface ListValue {
  readonly tag: "list";
  readonly items: readonly SemanticValue[];
}

export interface SetValue {
  readonly tag: "set";
  readonly items: readonly SemanticValue[];
}

export type SemanticValue =
  | BooleanValue
  | StringValue
  | IntegerValue
  | RationalValue
  | EnumValue
  | RecordValue
  | ListValue
  | SetValue;

export interface EvaluationEnvironment {
  readonly variables?: Readonly<Record<string, SemanticValue>>;
  readonly universes?: Readonly<
    Record<string, readonly SemanticValue[]>
  >;
}

export interface EvaluationOptions {
  readonly max_steps?: number;
}

export type SfolEvaluationDiagnosticCode =
  | "SFOL_EVAL_UNBOUND_VARIABLE"
  | "SFOL_EVAL_UNBOUND_UNIVERSE"
  | "SFOL_EVAL_EMPTY_UNIVERSE"
  | "SFOL_EVAL_INVALID_NUMERIC"
  | "SFOL_EVAL_DIVISION_BY_ZERO"
  | "SFOL_EVAL_EMPTY_FOLD"
  | "SFOL_EVAL_UNKNOWN_DECLARATION"
  | "SFOL_EVAL_CALL_ARITY"
  | "SFOL_EVAL_RECURSIVE_CALL"
  | "SFOL_EVAL_EXPECTED_BOOLEAN"
  | "SFOL_EVAL_EXPECTED_COLLECTION"
  | "SFOL_EVAL_EXPECTED_RECORD"
  | "SFOL_EVAL_UNKNOWN_FIELD"
  | "SFOL_EVAL_EXPECTED_NUMERIC"
  | "SFOL_EVAL_INCOMPATIBLE_VALUES"
  | "SFOL_EVAL_RESOURCE_LIMIT"
  | "SFOL_EVAL_INVALID_TYPED_INPUT";

export interface SfolEvaluationDiagnostic {
  readonly code: SfolEvaluationDiagnosticCode;
  readonly stage: "evaluation";
  readonly path: string;
  readonly detail: string;
  readonly span: SourceSpan;
}

export type TermEvaluationResult =
  | {
      readonly status: "value";
      readonly value: SemanticValue;
    }
  | {
      readonly status: "indeterminate";
      readonly diagnostic: SfolEvaluationDiagnostic;
    };

export type PredicateEvaluationResult =
  | {
      readonly status: "value";
      readonly value: boolean;
    }
  | {
      readonly status: "indeterminate";
      readonly diagnostic: SfolEvaluationDiagnostic;
    };

interface ExactRational {
  readonly numerator: bigint;
  readonly denominator: bigint;
}

type CallableDeclaration = FunctionDeclaration | PredicateDeclaration;

interface EvaluationContext {
  readonly typed: TypedLogicModule;
  readonly variables: ReadonlyMap<string, SemanticValue>;
  readonly universes: Readonly<Record<string, readonly SemanticValue[]>>;
  readonly callables: ReadonlyMap<string, CallableDeclaration>;
  readonly universeDeclarations: ReadonlyMap<
    string,
    FixtureUniverseDeclaration
  >;
  readonly activeCalls: ReadonlySet<string>;
  readonly budget: {
    remaining: number;
  };
}

const DEFAULT_MAX_STEPS = 10_000;

class EvaluationAbort extends Error {
  readonly diagnostic: SfolEvaluationDiagnostic;

  constructor(diagnostic: SfolEvaluationDiagnostic) {
    super(`${diagnostic.code} at ${diagnostic.path}: ${diagnostic.detail}`);
    this.name = "EvaluationAbort";
    this.diagnostic = diagnostic;
  }
}

export function evaluateTerm(
  typed: TypedLogicModule,
  term: LogicTerm,
  environment: EvaluationEnvironment = {},
  options: EvaluationOptions = {},
): TermEvaluationResult {
  try {
    const context = createContext(typed, environment, options);
    return Object.freeze({
      status: "value",
      value: evaluate(term, context),
    });
  } catch (error: unknown) {
    if (error instanceof EvaluationAbort) {
      return Object.freeze({
        status: "indeterminate",
        diagnostic: Object.freeze(error.diagnostic),
      });
    }
    return Object.freeze({
      status: "indeterminate",
      diagnostic: Object.freeze({
        code: "SFOL_EVAL_INVALID_TYPED_INPUT",
        stage: "evaluation",
        path: term.span.path,
        detail: "the typed evaluator received structurally invalid input",
        span: term.span,
      }),
    });
  }
}

export function evaluatePredicate(
  typed: TypedLogicModule,
  term: LogicTerm,
  environment: EvaluationEnvironment = {},
  options: EvaluationOptions = {},
): PredicateEvaluationResult {
  const result = evaluateTerm(typed, term, environment, options);
  if (result.status === "indeterminate") {
    return result;
  }
  if (result.value.tag !== "boolean") {
    return Object.freeze({
      status: "indeterminate",
      diagnostic: Object.freeze({
        code: "SFOL_EVAL_EXPECTED_BOOLEAN",
        stage: "evaluation",
        path: term.span.path,
        detail: `predicate evaluation produced ${result.value.tag}, not boolean`,
        span: term.span,
      }),
    });
  }
  return Object.freeze({ status: "value", value: result.value.value });
}

export function integerValue(value: string): IntegerValue {
  const parsed = parseInteger(value);
  if (parsed === null) {
    throw new Error(`invalid exact integer ${value}`);
  }
  return Object.freeze({ tag: "integer", value: parsed.toString() });
}

export function rationalValue(
  numerator: string,
  denominator: string,
): RationalValue {
  const parsedNumerator = parseInteger(numerator);
  const parsedDenominator = parseInteger(denominator);
  if (parsedNumerator === null || parsedDenominator === null) {
    throw new Error(`invalid exact rational ${numerator}/${denominator}`);
  }
  const normalized = normalizeRational(
    parsedNumerator,
    parsedDenominator,
  );
  if (normalized === null) {
    throw new Error("exact rational denominator cannot be zero");
  }
  return rationalSemanticValue(normalized);
}

function createContext(
  typed: TypedLogicModule,
  environment: EvaluationEnvironment,
  options: EvaluationOptions,
): EvaluationContext {
  const callables = new Map<string, CallableDeclaration>();
  const universeDeclarations = new Map<
    string,
    FixtureUniverseDeclaration
  >();

  for (const declaration of typed.source.declarations) {
    if (declaration.tag === "function" || declaration.tag === "predicate") {
      callables.set(declaration.declaration_id, declaration);
    } else if (declaration.tag === "fixture-universe") {
      universeDeclarations.set(declaration.declaration_id, declaration);
    }
  }

  const configuredSteps = options.max_steps;
  const maxSteps =
    configuredSteps !== undefined &&
    Number.isSafeInteger(configuredSteps) &&
    configuredSteps > 0
      ? configuredSteps
      : DEFAULT_MAX_STEPS;

  return {
    typed,
    variables: new Map(Object.entries(environment.variables ?? {})),
    universes: environment.universes ?? {},
    callables,
    universeDeclarations,
    activeCalls: new Set(),
    budget: { remaining: maxSteps },
  };
}

function evaluate(term: LogicTerm, context: EvaluationContext): SemanticValue {
  consumeStep(term, context);
  let result: SemanticValue;

  switch (term.tag) {
    case "literal":
      result = evaluateLiteral(term.value, term.span);
      break;

    case "variable": {
      const value = context.variables.get(term.name);
      if (value === undefined) {
        fail(
          "SFOL_EVAL_UNBOUND_VARIABLE",
          term,
          `variable ${term.name} is absent from the finite environment`,
        );
      }
      result = cloneValue(value, term);
      break;
    }

    case "field": {
      const target = evaluate(term.target, context);
      if (target.tag !== "record") {
        fail(
          "SFOL_EVAL_EXPECTED_RECORD",
          term,
          `field ${term.field} requires a record value`,
        );
      }
      const field = target.fields[term.field];
      if (field === undefined) {
        fail(
          "SFOL_EVAL_UNKNOWN_FIELD",
          term,
          `record ${target.declaration_id} has no value for ${term.field}`,
        );
      }
      result = field;
      break;
    }

    case "record": {
      const fields: Record<string, SemanticValue> = {};
      for (const field of [...term.fields].sort((left, right) =>
        left.name.localeCompare(right.name),
      )) {
        fields[field.name] = evaluate(field.value, context);
      }
      result = Object.freeze({
        tag: "record",
        declaration_id: term.declaration_id,
        fields: Object.freeze(fields),
      });
      break;
    }

    case "list":
      result = Object.freeze({
        tag: "list",
        items: Object.freeze(
          term.items.map((item) => evaluate(item, context)),
        ),
      });
      break;

    case "set": {
      const unique = new Map<string, SemanticValue>();
      for (const item of term.items) {
        const value = evaluate(item, context);
        unique.set(semanticKey(value), value);
      }
      result = Object.freeze({
        tag: "set",
        items: Object.freeze(
          [...unique.entries()]
            .sort(([left], [right]) => left.localeCompare(right))
            .map(([, value]) => value),
        ),
      });
      break;
    }

    case "enum":
      result = Object.freeze({
        tag: "enum",
        declaration_id: term.declaration_id,
        member: term.member,
      });
      break;

    case "arithmetic": {
      const leftValue = evaluate(term.left, context);
      const rightValue = evaluate(term.right, context);
      const left = requireNumeric(leftValue, term.left);
      const right = requireNumeric(rightValue, term.right);
      const exact =
        term.operator === "add"
          ? add(left, right)
          : term.operator === "subtract"
            ? subtract(left, right)
            : term.operator === "multiply"
              ? multiply(left, right)
              : divide(left, right);
      if (exact === null) {
        fail(
          "SFOL_EVAL_DIVISION_BY_ZERO",
          term,
          "exact rational division by zero is indeterminate",
        );
      }
      const bothInteger =
        term.operator !== "divide" &&
        leftValue.tag === "integer" &&
        rightValue.tag === "integer";
      result = bothInteger
        ? integerSemanticValue(exact.numerator / exact.denominator)
        : rationalSemanticValue(exact);
      break;
    }

    case "negate": {
      const operandValue = evaluate(term.operand, context);
      const operand = requireNumeric(operandValue, term.operand);
      const exact = normalizeRational(
        -operand.numerator,
        operand.denominator,
      );
      if (exact === null) {
        fail(
          "SFOL_EVAL_INVALID_NUMERIC",
          term,
          "cannot normalize the numeric operand",
        );
      }
      result =
        operandValue.tag === "integer"
          ? integerSemanticValue(exact.numerator)
          : rationalSemanticValue(exact);
      break;
    }

    case "comparison": {
      const left = evaluate(term.left, context);
      const right = evaluate(term.right, context);
      const comparison =
        isNumericValue(left) && isNumericValue(right)
          ? compareRationals(
              requireNumeric(left, term.left),
              requireNumeric(right, term.right),
            )
          : semanticKey(left) === semanticKey(right)
            ? 0
            : null;
      if (
        comparison === null &&
        term.operator !== "eq" &&
        term.operator !== "neq"
      ) {
        fail(
          "SFOL_EVAL_INCOMPATIBLE_VALUES",
          term,
          `${term.operator} cannot order ${left.tag} and ${right.tag}`,
        );
      }
      const value =
        term.operator === "eq"
          ? comparison === 0
          : term.operator === "neq"
            ? comparison !== 0
            : term.operator === "lt"
              ? comparison !== null && comparison < 0
              : term.operator === "lte"
                ? comparison !== null && comparison <= 0
                : term.operator === "gt"
                  ? comparison !== null && comparison > 0
                  : comparison !== null && comparison >= 0;
      result = Object.freeze({ tag: "boolean", value });
      break;
    }

    case "boolean": {
      const and = term.operator === "and";
      let aggregate = and;
      for (const operand of term.operands) {
        const value = requireBoolean(evaluate(operand, context), operand);
        if (and && !value) {
          aggregate = false;
          break;
        }
        if (!and && value) {
          aggregate = true;
          break;
        }
      }
      result = Object.freeze({ tag: "boolean", value: aggregate });
      break;
    }

    case "not":
      result = Object.freeze({
        tag: "boolean",
        value: !requireBoolean(
          evaluate(term.operand, context),
          term.operand,
        ),
      });
      break;

    case "conditional":
      result = requireBoolean(
        evaluate(term.condition, context),
        term.condition,
      )
        ? evaluate(term.when_true, context)
        : evaluate(term.when_false, context);
      break;

    case "fold": {
      const collection = evaluate(term.collection, context);
      if (collection.tag !== "list" && collection.tag !== "set") {
        fail(
          "SFOL_EVAL_EXPECTED_COLLECTION",
          term,
          "fold requires a list or set value",
        );
      }
      if (term.operator === "count") {
        result = integerSemanticValue(BigInt(collection.items.length));
        break;
      }
      if (collection.items.length === 0) {
        if (term.operator === "sum") {
          result = integerSemanticValue(0n);
          break;
        }
        if (term.operator === "product") {
          result = integerSemanticValue(1n);
          break;
        }
        fail(
          "SFOL_EVAL_EMPTY_FOLD",
          term,
          `${term.operator} has no value for an empty collection`,
        );
      }
      if (term.expression === null) {
        fail(
          "SFOL_EVAL_INVALID_TYPED_INPUT",
          term,
          `${term.operator} requires a fold expression`,
        );
      }
      let accumulated: SemanticValue | null = null;
      for (const item of collection.items) {
        const nested = withVariable(context, term.item_name, item);
        const nextValue = evaluate(term.expression, nested);
        const next = requireNumeric(nextValue, term.expression);
        if (accumulated === null) {
          accumulated = nextValue;
          continue;
        }
        const current = requireNumeric(accumulated, term.expression);
        const combined =
          term.operator === "sum"
            ? add(current, next)
            : term.operator === "product"
              ? multiply(current, next)
              : compareRationals(current, next) <= 0
                ? current
                : next;
        const selected =
          term.operator === "maximum" &&
          compareRationals(current, next) < 0
            ? next
            : combined;
        accumulated =
          accumulated.tag === "rational" || nextValue.tag === "rational"
            ? rationalSemanticValue(selected)
            : integerSemanticValue(
                selected.numerator / selected.denominator,
              );
      }
      if (accumulated === null) {
        fail(
          "SFOL_EVAL_EMPTY_FOLD",
          term,
          `${term.operator} produced no value`,
        );
      }
      result = accumulated;
      break;
    }

    case "quantifier": {
      const universe = context.universes[term.universe_id];
      if (universe === undefined) {
        fail(
          "SFOL_EVAL_UNBOUND_UNIVERSE",
          term,
          `finite universe ${term.universe_id} is absent`,
        );
      }
      const declaration = context.universeDeclarations.get(
        term.universe_id,
      );
      if (universe.length === 0 && declaration?.admits_empty !== true) {
        fail(
          "SFOL_EVAL_EMPTY_UNIVERSE",
          term,
          `finite universe ${term.universe_id} does not admit empty input`,
        );
      }
      let aggregate = term.operator === "forall";
      for (const member of universe) {
        const nested = withVariable(
          context,
          term.variable_name,
          cloneValue(member, term),
        );
        const predicate = requireBoolean(
          evaluate(term.predicate, nested),
          term.predicate,
        );
        if (term.operator === "forall" && !predicate) {
          aggregate = false;
          break;
        }
        if (term.operator === "exists" && predicate) {
          aggregate = true;
          break;
        }
      }
      result = Object.freeze({ tag: "boolean", value: aggregate });
      break;
    }

    case "call": {
      const declaration = context.callables.get(term.declaration_id);
      if (declaration === undefined) {
        fail(
          "SFOL_EVAL_UNKNOWN_DECLARATION",
          term,
          `callable ${term.declaration_id} is absent`,
        );
      }
      if (declaration.parameters.length !== term.arguments.length) {
        fail(
          "SFOL_EVAL_CALL_ARITY",
          term,
          `callable ${term.declaration_id} expects ${declaration.parameters.length} arguments; received ${term.arguments.length}`,
        );
      }
      if (context.activeCalls.has(term.declaration_id)) {
        fail(
          "SFOL_EVAL_RECURSIVE_CALL",
          term,
          `recursive call to ${term.declaration_id} is forbidden`,
        );
      }
      const variables = new Map(context.variables);
      for (let index = 0; index < declaration.parameters.length; index += 1) {
        const parameter = declaration.parameters[index];
        const argument = term.arguments[index];
        if (parameter === undefined || argument === undefined) {
          fail(
            "SFOL_EVAL_CALL_ARITY",
            term,
            `callable ${term.declaration_id} has an incomplete argument vector`,
          );
        }
        variables.set(parameter.name, evaluate(argument, context));
      }
      const activeCalls = new Set(context.activeCalls);
      activeCalls.add(term.declaration_id);
      result = evaluate(declaration.body, {
        ...context,
        variables,
        activeCalls,
      });
      break;
    }
  }

  return applyEffectiveSort(term, result, context.typed);
}

function evaluateLiteral(
  value:
    | { readonly tag: "boolean"; readonly value: boolean }
    | { readonly tag: "string"; readonly value: string }
    | { readonly tag: "integer"; readonly value: string }
    | {
        readonly tag: "rational";
        readonly numerator: string;
        readonly denominator: string;
      },
  span: SourceSpan,
): SemanticValue {
  if (value.tag === "boolean" || value.tag === "string") {
    return Object.freeze({ ...value });
  }
  const numerator = parseInteger(
    value.tag === "integer" ? value.value : value.numerator,
  );
  const denominator =
    value.tag === "integer" ? 1n : parseInteger(value.denominator);
  if (numerator === null || denominator === null) {
    throw new EvaluationAbort({
      code: "SFOL_EVAL_INVALID_NUMERIC",
      stage: "evaluation",
      path: span.path,
      detail: "numeric literals require canonical signed integer components",
      span,
    });
  }
  const exact = normalizeRational(numerator, denominator);
  if (exact === null) {
    throw new EvaluationAbort({
      code: "SFOL_EVAL_DIVISION_BY_ZERO",
      stage: "evaluation",
      path: span.path,
      detail: "a rational literal cannot use a zero denominator",
      span,
    });
  }
  return value.tag === "integer"
    ? integerSemanticValue(exact.numerator)
    : rationalSemanticValue(exact);
}

function applyEffectiveSort(
  term: LogicTerm,
  value: SemanticValue,
  typed: TypedLogicModule,
): SemanticValue {
  if (value.tag !== "integer") {
    return value;
  }
  const judgments = typed.term_judgments.filter(
    (judgment) =>
      judgment.path === term.span.path && judgment.term_tag === term.tag,
  );
  const requiresRational = judgments.some(
    (judgment) =>
      judgment.effective_sort.tag === "primitive" &&
      judgment.effective_sort.name === "rational",
  );
  return requiresRational
    ? rationalValue(value.value, "1")
    : value;
}

function applyNumeric(
  numerator: bigint,
  denominator: bigint,
): ExactRational {
  const result = normalizeRational(numerator, denominator);
  if (result === null) {
    throw new Error("unexpected zero denominator");
  }
  return result;
}

function add(left: ExactRational, right: ExactRational): ExactRational {
  return applyNumeric(
    left.numerator * right.denominator +
      right.numerator * left.denominator,
    left.denominator * right.denominator,
  );
}

function subtract(
  left: ExactRational,
  right: ExactRational,
): ExactRational {
  return applyNumeric(
    left.numerator * right.denominator -
      right.numerator * left.denominator,
    left.denominator * right.denominator,
  );
}

function multiply(
  left: ExactRational,
  right: ExactRational,
): ExactRational {
  return applyNumeric(
    left.numerator * right.numerator,
    left.denominator * right.denominator,
  );
}

function divide(
  left: ExactRational,
  right: ExactRational,
): ExactRational | null {
  return normalizeRational(
    left.numerator * right.denominator,
    left.denominator * right.numerator,
  );
}

function compareRationals(
  left: ExactRational,
  right: ExactRational,
): -1 | 0 | 1 {
  const leftScaled = left.numerator * right.denominator;
  const rightScaled = right.numerator * left.denominator;
  return leftScaled < rightScaled ? -1 : leftScaled > rightScaled ? 1 : 0;
}

function normalizeRational(
  numerator: bigint,
  denominator: bigint,
): ExactRational | null {
  if (denominator === 0n) {
    return null;
  }
  let normalizedNumerator = numerator;
  let normalizedDenominator = denominator;
  if (normalizedDenominator < 0n) {
    normalizedNumerator = -normalizedNumerator;
    normalizedDenominator = -normalizedDenominator;
  }
  const divisor = gcd(normalizedNumerator, normalizedDenominator);
  return Object.freeze({
    numerator: normalizedNumerator / divisor,
    denominator: normalizedDenominator / divisor,
  });
}

function gcd(left: bigint, right: bigint): bigint {
  let x = left < 0n ? -left : left;
  let y = right < 0n ? -right : right;
  while (y !== 0n) {
    const remainder = x % y;
    x = y;
    y = remainder;
  }
  return x === 0n ? 1n : x;
}

function parseInteger(value: string): bigint | null {
  return /^-?(?:0|[1-9][0-9]*)$/.test(value) ? BigInt(value) : null;
}

function integerSemanticValue(value: bigint): IntegerValue {
  return Object.freeze({ tag: "integer", value: value.toString() });
}

function rationalSemanticValue(value: ExactRational): RationalValue {
  return Object.freeze({
    tag: "rational",
    numerator: value.numerator.toString(),
    denominator: value.denominator.toString(),
  });
}

function requireNumeric(
  value: SemanticValue,
  term: LogicTerm,
): ExactRational {
  if (value.tag === "integer") {
    const parsed = parseInteger(value.value);
    if (parsed !== null) {
      return Object.freeze({ numerator: parsed, denominator: 1n });
    }
  } else if (value.tag === "rational") {
    const numerator = parseInteger(value.numerator);
    const denominator = parseInteger(value.denominator);
    if (numerator !== null && denominator !== null) {
      const exact = normalizeRational(numerator, denominator);
      if (exact !== null) {
        return exact;
      }
    }
  }
  fail(
    "SFOL_EVAL_EXPECTED_NUMERIC",
    term,
    `expected an exact numeric value; received ${value.tag}`,
  );
}

function requireBoolean(value: SemanticValue, term: LogicTerm): boolean {
  if (value.tag !== "boolean") {
    fail(
      "SFOL_EVAL_EXPECTED_BOOLEAN",
      term,
      `expected boolean; received ${value.tag}`,
    );
  }
  return value.value;
}

function isNumericValue(
  value: SemanticValue,
): value is IntegerValue | RationalValue {
  return value.tag === "integer" || value.tag === "rational";
}

function withVariable(
  context: EvaluationContext,
  name: string,
  value: SemanticValue,
): EvaluationContext {
  const variables = new Map(context.variables);
  variables.set(name, value);
  return { ...context, variables };
}

function cloneValue(value: SemanticValue, term: LogicTerm): SemanticValue {
  switch (value.tag) {
    case "boolean":
    case "string":
      return Object.freeze({ ...value });
    case "integer": {
      const parsed = parseInteger(value.value);
      if (parsed === null) {
        fail(
          "SFOL_EVAL_INVALID_NUMERIC",
          term,
          `environment integer ${value.value} is not canonical`,
        );
      }
      return integerSemanticValue(parsed);
    }
    case "rational": {
      const numerator = parseInteger(value.numerator);
      const denominator = parseInteger(value.denominator);
      if (numerator === null || denominator === null) {
        fail(
          "SFOL_EVAL_INVALID_NUMERIC",
          term,
          "environment rational components must be canonical integers",
        );
      }
      const exact = normalizeRational(numerator, denominator);
      if (exact === null) {
        fail(
          "SFOL_EVAL_DIVISION_BY_ZERO",
          term,
          "environment rational denominator cannot be zero",
        );
      }
      return rationalSemanticValue(exact);
    }
    case "enum":
      return Object.freeze({ ...value });
    case "record": {
      const fields: Record<string, SemanticValue> = {};
      for (const name of Object.keys(value.fields).sort()) {
        const field = value.fields[name];
        if (field === undefined) {
          fail(
            "SFOL_EVAL_INVALID_TYPED_INPUT",
            term,
            `record field ${name} is absent`,
          );
        }
        fields[name] = cloneValue(field, term);
      }
      return Object.freeze({
        tag: "record",
        declaration_id: value.declaration_id,
        fields: Object.freeze(fields),
      });
    }
    case "list":
      return Object.freeze({
        tag: "list",
        items: Object.freeze(
          value.items.map((item) => cloneValue(item, term)),
        ),
      });
    case "set": {
      const unique = new Map<string, SemanticValue>();
      for (const item of value.items) {
        const cloned = cloneValue(item, term);
        unique.set(semanticKey(cloned), cloned);
      }
      return Object.freeze({
        tag: "set",
        items: Object.freeze(
          [...unique.entries()]
            .sort(([left], [right]) => left.localeCompare(right))
            .map(([, item]) => item),
        ),
      });
    }
  }
}

function semanticKey(value: SemanticValue): string {
  switch (value.tag) {
    case "boolean":
      return `boolean:${value.value ? "1" : "0"}`;
    case "string":
      return `string:${JSON.stringify(value.value)}`;
    case "integer":
    case "rational": {
      const exact =
        value.tag === "integer"
          ? { numerator: BigInt(value.value), denominator: 1n }
          : {
              numerator: BigInt(value.numerator),
              denominator: BigInt(value.denominator),
            };
      const normalized = normalizeRational(
        exact.numerator,
        exact.denominator,
      );
      return normalized === null
        ? "numeric:invalid"
        : `numeric:${normalized.numerator}/${normalized.denominator}`;
    }
    case "enum":
      return `enum:${value.declaration_id}:${value.member}`;
    case "record":
      return `record:${value.declaration_id}:{${Object.keys(value.fields)
        .sort()
        .map((name) => `${JSON.stringify(name)}:${semanticKey(value.fields[name]!)}`)
        .join(",")}}`;
    case "list":
      return `list:[${value.items.map(semanticKey).join(",")}]`;
    case "set":
      return `set:{${value.items.map(semanticKey).sort().join(",")}}`;
  }
}

function consumeStep(term: LogicTerm, context: EvaluationContext): void {
  context.budget.remaining -= 1;
  if (context.budget.remaining < 0) {
    fail(
      "SFOL_EVAL_RESOURCE_LIMIT",
      term,
      "the deterministic evaluation step budget was exhausted",
    );
  }
}

function fail(
  code: SfolEvaluationDiagnosticCode,
  term: LogicTerm,
  detail: string,
): never {
  throw new EvaluationAbort({
    code,
    stage: "evaluation",
    path: term.span.path,
    detail,
    span: term.span,
  });
}
