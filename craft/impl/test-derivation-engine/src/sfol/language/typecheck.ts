import type {
  LogicClause,
  LogicDeclaration,
  LogicTerm,
  LogicTermTag,
  NodeLogicModuleV1,
  ParameterDeclaration,
  SortRef,
  SourceSpan,
} from "./ast.js";

export type SfolTypeDiagnosticCode =
  | "SFOL_TYPE_UNKNOWN_NAMED_SORT"
  | "SFOL_TYPE_UNKNOWN_VARIABLE"
  | "SFOL_TYPE_UNKNOWN_FIELD"
  | "SFOL_TYPE_UNKNOWN_DECLARATION"
  | "SFOL_TYPE_UNKNOWN_ENUM_MEMBER"
  | "SFOL_TYPE_MISMATCH"
  | "SFOL_TYPE_EXPECTED_NUMERIC"
  | "SFOL_TYPE_EXPECTED_BOOLEAN"
  | "SFOL_TYPE_EXPECTED_COLLECTION"
  | "SFOL_TYPE_AMBIGUOUS_COLLECTION"
  | "SFOL_TYPE_INCOMPATIBLE_COMPARISON"
  | "SFOL_TYPE_UNKNOWN_UNIVERSE"
  | "SFOL_TYPE_UNIVERSE_MISMATCH"
  | "SFOL_TYPE_CALL_ARITY"
  | "SFOL_TYPE_RECORD_FIELD_MISSING"
  | "SFOL_TYPE_RECURSION_FORBIDDEN"
  | "SFOL_TYPE_INVALID_EFFECT_CONTRACT";

export interface SfolTypeDiagnostic {
  readonly code: SfolTypeDiagnosticCode;
  readonly stage: "type";
  readonly path: string;
  readonly detail: string;
  readonly span?: SourceSpan;
}

export interface TypeJudgment {
  readonly path: string;
  readonly term_tag: LogicTermTag;
  readonly inferred_sort: SortRef;
  readonly effective_sort: SortRef;
  readonly coercion: "none" | "integer-to-rational";
}

export interface ClauseTypeJudgment {
  readonly clause_id: string;
  readonly kind: LogicClause["kind"];
  readonly result_sort: SortRef;
  readonly observation_sort: SortRef | null;
}

export interface TypedLogicModule {
  readonly source: NodeLogicModuleV1;
  readonly environment: {
    readonly named_sorts: readonly string[];
    readonly callables: readonly string[];
    readonly fixture_universes: readonly string[];
  };
  readonly term_judgments: readonly TypeJudgment[];
  readonly clause_judgments: readonly ClauseTypeJudgment[];
}

export type SfolTypecheckResult =
  | {
      readonly ok: true;
      readonly value: TypedLogicModule;
    }
  | {
      readonly ok: false;
      readonly diagnostics: readonly SfolTypeDiagnostic[];
    };

interface RecordSortEntry {
  readonly kind: "record";
  readonly fields: ReadonlyMap<
    string,
    {
      readonly sort: SortRef;
      readonly required: boolean;
    }
  >;
}

interface EnumSortEntry {
  readonly kind: "enum";
  readonly members: ReadonlySet<string>;
}

type NamedSortEntry = RecordSortEntry | EnumSortEntry;

interface CallableEntry {
  readonly kind: "function" | "predicate";
  readonly parameters: readonly ParameterDeclaration[];
  readonly result: SortRef;
  readonly body: LogicTerm;
  readonly span: SourceSpan;
}

interface TypeEnvironment {
  readonly named: ReadonlyMap<string, NamedSortEntry>;
  readonly callables: ReadonlyMap<string, CallableEntry>;
  readonly universes: ReadonlyMap<string, SortRef>;
}

class TypeAbort extends Error {
  readonly diagnostic: SfolTypeDiagnostic;

  constructor(diagnostic: SfolTypeDiagnostic) {
    super(`${diagnostic.code} at ${diagnostic.path}: ${diagnostic.detail}`);
    this.name = "TypeAbort";
    this.diagnostic = diagnostic;
  }
}

export function typecheckLogicModule(
  module: NodeLogicModuleV1,
): SfolTypecheckResult {
  try {
    const environment = buildEnvironment(module.declarations);
    rejectRecursiveDefinitions(environment);
    const judgments: TypeJudgment[] = [];

    for (const declaration of module.declarations) {
      validateDeclaration(declaration, environment, judgments);
    }

    const clauseJudgments = module.clauses.map((clause) =>
      validateClause(clause, environment, judgments),
    );

    return Object.freeze({
      ok: true,
      value: deepFreeze({
        source: module,
        environment: {
          named_sorts: [...environment.named.keys()].sort(),
          callables: [...environment.callables.keys()].sort(),
          fixture_universes: [...environment.universes.keys()].sort(),
        },
        term_judgments: judgments,
        clause_judgments: clauseJudgments,
      }),
    });
  } catch (error) {
    if (error instanceof TypeAbort) {
      return Object.freeze({
        ok: false,
        diagnostics: Object.freeze([Object.freeze(error.diagnostic)]),
      });
    }
    throw error;
  }
}

function buildEnvironment(
  declarations: readonly LogicDeclaration[],
): TypeEnvironment {
  const named = new Map<string, NamedSortEntry>();
  const callableHeaders = new Map<string, CallableEntry>();
  const universeHeaders = new Map<string, SortRef>();

  for (const declaration of declarations) {
    switch (declaration.tag) {
      case "enum":
        named.set(declaration.declaration_id, {
          kind: "enum",
          members: new Set(declaration.members),
        });
        break;
      case "record":
        named.set(declaration.declaration_id, {
          kind: "record",
          fields: new Map(
            declaration.fields.map((field) => [
              field.name,
              { sort: field.sort, required: field.required },
            ]),
          ),
        });
        break;
      case "function":
        callableHeaders.set(declaration.declaration_id, {
          kind: "function",
          parameters: declaration.parameters,
          result: declaration.result,
          body: declaration.body,
          span: declaration.span,
        });
        break;
      case "predicate":
        callableHeaders.set(declaration.declaration_id, {
          kind: "predicate",
          parameters: declaration.parameters,
          result: primitive("boolean"),
          body: declaration.body,
          span: declaration.span,
        });
        break;
      case "fixture-universe":
        universeHeaders.set(
          declaration.declaration_id,
          declaration.element_sort,
        );
        break;
    }
  }

  const environment: TypeEnvironment = {
    named,
    callables: callableHeaders,
    universes: universeHeaders,
  };

  for (const declaration of declarations) {
    switch (declaration.tag) {
      case "record":
        for (const field of declaration.fields) {
          validateClosedSort(field.sort, environment, field.span.path);
        }
        break;
      case "function":
        for (const parameter of declaration.parameters) {
          validateClosedSort(parameter.sort, environment, parameter.span.path);
        }
        validateClosedSort(
          declaration.result,
          environment,
          declaration.span.path,
        );
        break;
      case "predicate":
        for (const parameter of declaration.parameters) {
          validateClosedSort(parameter.sort, environment, parameter.span.path);
        }
        break;
      case "fixture-universe":
        validateClosedSort(
          declaration.element_sort,
          environment,
          declaration.span.path,
        );
        break;
      case "enum":
        break;
    }
  }

  return environment;
}

function validateDeclaration(
  declaration: LogicDeclaration,
  environment: TypeEnvironment,
  judgments: TypeJudgment[],
): void {
  if (declaration.tag !== "function" && declaration.tag !== "predicate") {
    return;
  }
  const variables = variableEnvironment(declaration.parameters);
  typeTerm(
    declaration.body,
    environment,
    variables,
    declaration.tag === "predicate"
      ? primitive("boolean")
      : declaration.result,
    judgments,
  );
}

function validateClause(
  clause: LogicClause,
  environment: TypeEnvironment,
  judgments: TypeJudgment[],
): ClauseTypeJudgment {
  validateClosedSort(clause.result_sort, environment, clause.span.path);
  if (clause.observation_sort !== null) {
    validateClosedSort(
      clause.observation_sort,
      environment,
      clause.span.path,
    );
  }
  for (const input of clause.inputs) {
    validateClosedSort(input.sort, environment, input.span.path);
  }

  if (
    clause.kind === "effect-relation" &&
    clause.observation_sort === null
  ) {
    typeFail(
      "SFOL_TYPE_INVALID_EFFECT_CONTRACT",
      clause.span.path,
      "effect-relation clauses require an explicit observation_sort",
      clause.span,
    );
  }

  const BooleanKinds: readonly LogicClause["kind"][] = [
    "predicate",
    "invariant",
    "precondition",
    "postcondition",
    "transition",
    "effect-relation",
  ];
  if (
    BooleanKinds.includes(clause.kind) &&
    !sortEquals(clause.result_sort, primitive("boolean"))
  ) {
    typeFail(
      "SFOL_TYPE_EXPECTED_BOOLEAN",
      clause.span.path,
      `${clause.kind} clauses must declare a Boolean result`,
      clause.span,
    );
  }

  const variables = variableEnvironment(clause.inputs);
  typeTerm(
    clause.expression,
    environment,
    variables,
    clause.result_sort,
    judgments,
  );

  return {
    clause_id: clause.clause_id,
    kind: clause.kind,
    result_sort: clause.result_sort,
    observation_sort: clause.observation_sort,
  };
}

function typeTerm(
  term: LogicTerm,
  environment: TypeEnvironment,
  variables: ReadonlyMap<string, SortRef>,
  expected: SortRef | null,
  judgments: TypeJudgment[],
): SortRef {
  let inferred: SortRef;

  switch (term.tag) {
    case "literal":
      inferred =
        term.value.tag === "boolean"
          ? primitive("boolean")
          : term.value.tag === "string"
            ? primitive("string")
            : term.value.tag === "integer"
              ? primitive("integer")
              : primitive("rational");
      break;

    case "variable": {
      const resolved = variables.get(term.name);
      if (resolved === undefined) {
        typeFail(
          "SFOL_TYPE_UNKNOWN_VARIABLE",
          term.span.path,
          `unknown variable ${term.name}`,
          term.span,
        );
      }
      inferred = resolved;
      break;
    }

    case "field": {
      const target = typeTerm(
        term.target,
        environment,
        variables,
        null,
        judgments,
      );
      if (target.tag !== "named") {
        typeFail(
          "SFOL_TYPE_UNKNOWN_FIELD",
          term.span.path,
          `field ${term.field} requires a named record target`,
          term.span,
        );
      }
      const entry = environment.named.get(target.declaration_id);
      if (entry?.kind !== "record") {
        typeFail(
          "SFOL_TYPE_UNKNOWN_FIELD",
          term.span.path,
          `${target.declaration_id} is not a record`,
          term.span,
        );
      }
      const field = entry.fields.get(term.field);
      if (field === undefined) {
        typeFail(
          "SFOL_TYPE_UNKNOWN_FIELD",
          term.span.path,
          `record ${target.declaration_id} has no field ${term.field}`,
          term.span,
        );
      }
      inferred = field.sort;
      break;
    }

    case "record": {
      const entry = environment.named.get(term.declaration_id);
      if (entry?.kind !== "record") {
        typeFail(
          "SFOL_TYPE_UNKNOWN_NAMED_SORT",
          term.span.path,
          `unknown record sort ${term.declaration_id}`,
          term.span,
        );
      }
      const supplied = new Set(term.fields.map(({ name }) => name));
      for (const [name, field] of entry.fields) {
        if (field.required && !supplied.has(name)) {
          typeFail(
            "SFOL_TYPE_RECORD_FIELD_MISSING",
            term.span.path,
            `required field ${name} is missing from ${term.declaration_id}`,
            term.span,
          );
        }
      }
      for (const field of term.fields) {
        const target = entry.fields.get(field.name);
        if (target === undefined) {
          typeFail(
            "SFOL_TYPE_UNKNOWN_FIELD",
            term.span.path,
            `record ${term.declaration_id} has no field ${field.name}`,
            term.span,
          );
        }
        typeTerm(
          field.value,
          environment,
          variables,
          target.sort,
          judgments,
        );
      }
      inferred = { tag: "named", declaration_id: term.declaration_id };
      break;
    }

    case "list":
    case "set": {
      const expectedElement =
        expected?.tag === term.tag ? expected.element : null;
      if (term.items.length === 0 && expectedElement === null) {
        typeFail(
          "SFOL_TYPE_AMBIGUOUS_COLLECTION",
          term.span.path,
          `empty ${term.tag} requires an explicit contextual element sort`,
          term.span,
        );
      }
      let element = expectedElement;
      if (element === null) {
        for (const item of term.items) {
          const itemSort = typeTerm(
            item,
            environment,
            variables,
            null,
            [],
          );
          element =
            element === null
              ? itemSort
              : commonSort(element, itemSort, item.span);
        }
      }
      for (const item of term.items) {
        typeTerm(item, environment, variables, element, judgments);
      }
      inferred = {
        tag: term.tag,
        element: element ?? primitive("boolean"),
      };
      break;
    }

    case "enum": {
      const entry = environment.named.get(term.declaration_id);
      if (entry?.kind !== "enum") {
        typeFail(
          "SFOL_TYPE_UNKNOWN_NAMED_SORT",
          term.span.path,
          `unknown enum sort ${term.declaration_id}`,
          term.span,
        );
      }
      if (!entry.members.has(term.member)) {
        typeFail(
          "SFOL_TYPE_UNKNOWN_ENUM_MEMBER",
          term.span.path,
          `enum ${term.declaration_id} has no member ${term.member}`,
          term.span,
        );
      }
      inferred = { tag: "named", declaration_id: term.declaration_id };
      break;
    }

    case "arithmetic": {
      const left = typeTerm(
        term.left,
        environment,
        variables,
        null,
        [],
      );
      const right = typeTerm(
        term.right,
        environment,
        variables,
        null,
        [],
      );
      requireNumeric(left, term.left.span);
      requireNumeric(right, term.right.span);
      inferred =
        term.operator === "divide" ||
        left.name === "rational" ||
        right.name === "rational"
          ? primitive("rational")
          : primitive("integer");
      typeTerm(term.left, environment, variables, inferred, judgments);
      typeTerm(term.right, environment, variables, inferred, judgments);
      break;
    }

    case "negate": {
      const operand = typeTerm(
        term.operand,
        environment,
        variables,
        null,
        judgments,
      );
      requireNumeric(operand, term.operand.span);
      inferred = operand;
      break;
    }

    case "comparison": {
      const left = typeTerm(
        term.left,
        environment,
        variables,
        null,
        [],
      );
      const right = typeTerm(
        term.right,
        environment,
        variables,
        null,
        [],
      );
      if (term.operator === "eq" || term.operator === "neq") {
        if (!sortsCompatible(left, right) && !sortsCompatible(right, left)) {
          incompatibleComparison(left, right, term.span);
        }
      } else {
        if (!isNumeric(left) || !isNumeric(right)) {
          incompatibleComparison(left, right, term.span);
        }
      }
      const operandSort =
        isNumeric(left) && isNumeric(right)
          ? commonSort(left, right, term.span)
          : left;
      typeTerm(term.left, environment, variables, operandSort, judgments);
      typeTerm(term.right, environment, variables, operandSort, judgments);
      inferred = primitive("boolean");
      break;
    }

    case "boolean":
      if (term.operands.length === 0) {
        typeFail(
          "SFOL_TYPE_EXPECTED_BOOLEAN",
          term.span.path,
          `${term.operator} requires at least one operand`,
          term.span,
        );
      }
      for (const operand of term.operands) {
        typeTerm(
          operand,
          environment,
          variables,
          primitive("boolean"),
          judgments,
        );
      }
      inferred = primitive("boolean");
      break;

    case "not":
      typeTerm(
        term.operand,
        environment,
        variables,
        primitive("boolean"),
        judgments,
      );
      inferred = primitive("boolean");
      break;

    case "conditional": {
      typeTerm(
        term.condition,
        environment,
        variables,
        primitive("boolean"),
        judgments,
      );
      const branchSort =
        expected ??
        commonSort(
          typeTerm(term.when_true, environment, variables, null, []),
          typeTerm(term.when_false, environment, variables, null, []),
          term.span,
        );
      typeTerm(
        term.when_true,
        environment,
        variables,
        branchSort,
        judgments,
      );
      typeTerm(
        term.when_false,
        environment,
        variables,
        branchSort,
        judgments,
      );
      inferred = branchSort;
      break;
    }

    case "fold": {
      const collection = typeTerm(
        term.collection,
        environment,
        variables,
        null,
        judgments,
      );
      if (collection.tag !== "list" && collection.tag !== "set") {
        typeFail(
          "SFOL_TYPE_EXPECTED_COLLECTION",
          term.span.path,
          "fold requires a list or set collection",
          term.span,
        );
      }
      const nested = new Map(variables);
      nested.set(term.item_name, collection.element);
      if (term.operator === "count") {
        if (term.expression !== null) {
          typeFail(
            "SFOL_TYPE_MISMATCH",
            term.span.path,
            "count fold must use a null expression",
            term.span,
          );
        }
        inferred = primitive("integer");
      } else {
        if (term.expression === null) {
          typeFail(
            "SFOL_TYPE_MISMATCH",
            term.span.path,
            `${term.operator} fold requires an expression`,
            term.span,
          );
        }
        const expression = typeTerm(
          term.expression,
          environment,
          nested,
          null,
          judgments,
        );
        requireNumeric(expression, term.expression.span);
        inferred = expression;
      }
      break;
    }

    case "quantifier": {
      const universe = environment.universes.get(term.universe_id);
      if (universe === undefined) {
        typeFail(
          "SFOL_TYPE_UNKNOWN_UNIVERSE",
          term.span.path,
          `unknown finite fixture universe ${term.universe_id}`,
          term.span,
        );
      }
      validateClosedSort(
        term.variable_sort,
        environment,
        term.span.path,
      );
      if (!sortEquals(universe, term.variable_sort)) {
        typeFail(
          "SFOL_TYPE_UNIVERSE_MISMATCH",
          term.span.path,
          `universe ${term.universe_id} has ${sortKey(universe)}, not ${sortKey(term.variable_sort)}`,
          term.span,
        );
      }
      const nested = new Map(variables);
      nested.set(term.variable_name, term.variable_sort);
      typeTerm(
        term.predicate,
        environment,
        nested,
        primitive("boolean"),
        judgments,
      );
      inferred = primitive("boolean");
      break;
    }

    case "call": {
      const callable = environment.callables.get(term.declaration_id);
      if (callable === undefined) {
        typeFail(
          "SFOL_TYPE_UNKNOWN_DECLARATION",
          term.span.path,
          `unknown callable ${term.declaration_id}`,
          term.span,
        );
      }
      if (term.arguments.length !== callable.parameters.length) {
        typeFail(
          "SFOL_TYPE_CALL_ARITY",
          term.span.path,
          `call ${term.declaration_id} expects ${callable.parameters.length} arguments; received ${term.arguments.length}`,
          term.span,
        );
      }
      term.arguments.forEach((argument, index) => {
        const parameter = callable.parameters[index];
        if (parameter !== undefined) {
          typeTerm(
            argument,
            environment,
            variables,
            parameter.sort,
            judgments,
          );
        }
      });
      inferred = callable.result;
      break;
    }
  }

  return recordJudgment(term, inferred, expected, judgments);
}

function recordJudgment(
  term: LogicTerm,
  inferred: SortRef,
  expected: SortRef | null,
  judgments: TypeJudgment[],
): SortRef {
  const effective = expected ?? inferred;
  if (expected !== null && !sortsCompatible(expected, inferred)) {
    typeFail(
      expected.tag === "primitive" && expected.name === "boolean"
        ? "SFOL_TYPE_EXPECTED_BOOLEAN"
        : "SFOL_TYPE_MISMATCH",
      term.span.path,
      `expected ${sortKey(expected)}; inferred ${sortKey(inferred)}`,
      term.span,
    );
  }
  judgments.push({
    path: term.span.path,
    term_tag: term.tag,
    inferred_sort: inferred,
    effective_sort: effective,
    coercion:
      expected?.tag === "primitive" &&
      expected.name === "rational" &&
      inferred.tag === "primitive" &&
      inferred.name === "integer"
        ? "integer-to-rational"
        : "none",
  });
  return effective;
}

function variableEnvironment(
  parameters: readonly ParameterDeclaration[],
): ReadonlyMap<string, SortRef> {
  return new Map(parameters.map(({ name, sort }) => [name, sort]));
}

function validateClosedSort(
  sort: SortRef,
  environment: TypeEnvironment,
  path: string,
): void {
  switch (sort.tag) {
    case "primitive":
      return;
    case "named":
      if (!environment.named.has(sort.declaration_id)) {
        typeFail(
          "SFOL_TYPE_UNKNOWN_NAMED_SORT",
          path,
          `unknown named sort ${sort.declaration_id}`,
        );
      }
      return;
    case "list":
    case "set":
      validateClosedSort(sort.element, environment, path);
  }
}

function rejectRecursiveDefinitions(environment: TypeEnvironment): void {
  const graph = new Map<string, readonly string[]>();
  for (const [id, callable] of environment.callables) {
    graph.set(
      id,
      [...collectCalls(callable.body)].filter((target) =>
        environment.callables.has(target),
      ),
    );
  }
  const visited = new Set<string>();
  const active = new Set<string>();

  const visit = (id: string): void => {
    if (active.has(id)) {
      const callable = environment.callables.get(id);
      typeFail(
        "SFOL_TYPE_RECURSION_FORBIDDEN",
        callable?.span.path ?? id,
        `recursive callable cycle includes ${id}`,
        callable?.span,
      );
    }
    if (visited.has(id)) return;
    active.add(id);
    for (const target of graph.get(id) ?? []) {
      visit(target);
    }
    active.delete(id);
    visited.add(id);
  };

  for (const id of [...graph.keys()].sort()) {
    visit(id);
  }
}

function collectCalls(term: LogicTerm, calls = new Set<string>()): Set<string> {
  switch (term.tag) {
    case "call":
      calls.add(term.declaration_id);
      term.arguments.forEach((child) => collectCalls(child, calls));
      break;
    case "field":
      collectCalls(term.target, calls);
      break;
    case "record":
      term.fields.forEach(({ value }) => collectCalls(value, calls));
      break;
    case "list":
    case "set":
      term.items.forEach((child) => collectCalls(child, calls));
      break;
    case "arithmetic":
    case "comparison":
      collectCalls(term.left, calls);
      collectCalls(term.right, calls);
      break;
    case "negate":
    case "not":
      collectCalls(term.operand, calls);
      break;
    case "boolean":
      term.operands.forEach((child) => collectCalls(child, calls));
      break;
    case "conditional":
      collectCalls(term.condition, calls);
      collectCalls(term.when_true, calls);
      collectCalls(term.when_false, calls);
      break;
    case "fold":
      collectCalls(term.collection, calls);
      if (term.expression !== null) collectCalls(term.expression, calls);
      break;
    case "quantifier":
      collectCalls(term.predicate, calls);
      break;
    case "literal":
    case "variable":
    case "enum":
      break;
  }
  return calls;
}

function requireNumeric(
  sort: SortRef,
  span: SourceSpan,
): asserts sort is SortRef & {
  readonly tag: "primitive";
  readonly name: "integer" | "rational";
} {
  if (!isNumeric(sort)) {
    typeFail(
      "SFOL_TYPE_EXPECTED_NUMERIC",
      span.path,
      `expected a numeric sort; received ${sortKey(sort)}`,
      span,
    );
  }
}

function isNumeric(
  sort: SortRef,
): sort is SortRef & {
  readonly tag: "primitive";
  readonly name: "integer" | "rational";
} {
  return (
    sort.tag === "primitive" &&
    (sort.name === "integer" || sort.name === "rational")
  );
}

function incompatibleComparison(
  left: SortRef,
  right: SortRef,
  span: SourceSpan,
): never {
  typeFail(
    "SFOL_TYPE_INCOMPATIBLE_COMPARISON",
    span.path,
    `cannot compare ${sortKey(left)} with ${sortKey(right)}`,
    span,
  );
}

function commonSort(
  left: SortRef,
  right: SortRef,
  span: SourceSpan,
): SortRef {
  if (sortEquals(left, right)) return left;
  if (isNumeric(left) && isNumeric(right)) return primitive("rational");
  typeFail(
    "SFOL_TYPE_MISMATCH",
    span.path,
    `no common sort for ${sortKey(left)} and ${sortKey(right)}`,
    span,
  );
}

function sortsCompatible(expected: SortRef, actual: SortRef): boolean {
  return (
    sortEquals(expected, actual) ||
    (expected.tag === "primitive" &&
      expected.name === "rational" &&
      actual.tag === "primitive" &&
      actual.name === "integer")
  );
}

function sortEquals(left: SortRef, right: SortRef): boolean {
  if (left.tag !== right.tag) return false;
  switch (left.tag) {
    case "primitive":
      return right.tag === "primitive" && left.name === right.name;
    case "named":
      return (
        right.tag === "named" &&
        left.declaration_id === right.declaration_id
      );
    case "list":
      return right.tag === "list" && sortEquals(left.element, right.element);
    case "set":
      return right.tag === "set" && sortEquals(left.element, right.element);
  }
}

function sortKey(sort: SortRef): string {
  switch (sort.tag) {
    case "primitive":
      return sort.name;
    case "named":
      return `named(${sort.declaration_id})`;
    case "list":
      return `list(${sortKey(sort.element)})`;
    case "set":
      return `set(${sortKey(sort.element)})`;
  }
}

function primitive(
  name: "boolean" | "string" | "integer" | "rational",
): SortRef & { readonly tag: "primitive" } {
  return { tag: "primitive", name };
}

function typeFail(
  code: SfolTypeDiagnosticCode,
  path: string,
  detail: string,
  span?: SourceSpan,
): never {
  throw new TypeAbort({
    code,
    stage: "type",
    path,
    detail,
    ...(span === undefined ? {} : { span }),
  });
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
