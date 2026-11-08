export const NODE_LOGIC_SCHEMA_VERSION = "domainspec-node-logic/v1" as const;
export const DS_SFOL_LANGUAGE_VERSION = "domainspec-sfol/v1" as const;

export type NodeLogicSchemaVersion = typeof NODE_LOGIC_SCHEMA_VERSION;
export type SfolLanguageVersion = typeof DS_SFOL_LANGUAGE_VERSION;

export interface SourcePosition {
  readonly line: number;
  readonly column: number;
}

export interface SourceSpan {
  readonly source_id: string;
  readonly path: string;
  readonly start: SourcePosition;
  readonly end: SourcePosition;
}

export type PrimitiveSortName =
  | "boolean"
  | "string"
  | "integer"
  | "rational";

export type SortRef =
  | {
      readonly tag: "primitive";
      readonly name: PrimitiveSortName;
    }
  | {
      readonly tag: "named";
      readonly declaration_id: string;
    }
  | {
      readonly tag: "list";
      readonly element: SortRef;
    }
  | {
      readonly tag: "set";
      readonly element: SortRef;
    };

export type LogicScalar =
  | {
      readonly tag: "boolean";
      readonly value: boolean;
    }
  | {
      readonly tag: "string";
      readonly value: string;
    }
  | {
      readonly tag: "integer";
      readonly value: string;
    }
  | {
      readonly tag: "rational";
      readonly numerator: string;
      readonly denominator: string;
    };

interface TermBase {
  readonly span: SourceSpan;
}

export interface LiteralTerm extends TermBase {
  readonly tag: "literal";
  readonly value: LogicScalar;
}

export interface VariableTerm extends TermBase {
  readonly tag: "variable";
  readonly name: string;
}

export interface FieldTerm extends TermBase {
  readonly tag: "field";
  readonly target: LogicTerm;
  readonly field: string;
}

export interface RecordTerm extends TermBase {
  readonly tag: "record";
  readonly declaration_id: string;
  readonly fields: readonly {
    readonly name: string;
    readonly value: LogicTerm;
  }[];
}

export interface ListTerm extends TermBase {
  readonly tag: "list";
  readonly items: readonly LogicTerm[];
}

export interface SetTerm extends TermBase {
  readonly tag: "set";
  readonly items: readonly LogicTerm[];
}

export interface EnumTerm extends TermBase {
  readonly tag: "enum";
  readonly declaration_id: string;
  readonly member: string;
}

export type ArithmeticOperator = "add" | "subtract" | "multiply" | "divide";

export interface ArithmeticTerm extends TermBase {
  readonly tag: "arithmetic";
  readonly operator: ArithmeticOperator;
  readonly left: LogicTerm;
  readonly right: LogicTerm;
}

export interface NegateTerm extends TermBase {
  readonly tag: "negate";
  readonly operand: LogicTerm;
}

export type ComparisonOperator = "eq" | "neq" | "lt" | "lte" | "gt" | "gte";

export interface ComparisonTerm extends TermBase {
  readonly tag: "comparison";
  readonly operator: ComparisonOperator;
  readonly left: LogicTerm;
  readonly right: LogicTerm;
}

export type BooleanOperator = "and" | "or";

export interface BooleanTerm extends TermBase {
  readonly tag: "boolean";
  readonly operator: BooleanOperator;
  readonly operands: readonly LogicTerm[];
}

export interface NotTerm extends TermBase {
  readonly tag: "not";
  readonly operand: LogicTerm;
}

export interface ConditionalTerm extends TermBase {
  readonly tag: "conditional";
  readonly condition: LogicTerm;
  readonly when_true: LogicTerm;
  readonly when_false: LogicTerm;
}

export type FoldOperator = "sum" | "product" | "minimum" | "maximum" | "count";

export interface FoldTerm extends TermBase {
  readonly tag: "fold";
  readonly operator: FoldOperator;
  readonly collection: LogicTerm;
  readonly item_name: string;
  readonly expression: LogicTerm | null;
}

export type QuantifierOperator = "exists" | "forall";

export interface QuantifierTerm extends TermBase {
  readonly tag: "quantifier";
  readonly operator: QuantifierOperator;
  readonly universe_id: string;
  readonly variable_name: string;
  readonly variable_sort: SortRef;
  readonly predicate: LogicTerm;
}

export interface CallTerm extends TermBase {
  readonly tag: "call";
  readonly declaration_id: string;
  readonly arguments: readonly LogicTerm[];
}

export type LogicTerm =
  | LiteralTerm
  | VariableTerm
  | FieldTerm
  | RecordTerm
  | ListTerm
  | SetTerm
  | EnumTerm
  | ArithmeticTerm
  | NegateTerm
  | ComparisonTerm
  | BooleanTerm
  | NotTerm
  | ConditionalTerm
  | FoldTerm
  | QuantifierTerm
  | CallTerm;

export type LogicTermTag = LogicTerm["tag"];

export interface ParameterDeclaration {
  readonly name: string;
  readonly sort: SortRef;
  readonly span: SourceSpan;
}

export interface EnumDeclaration {
  readonly tag: "enum";
  readonly declaration_id: string;
  readonly members: readonly string[];
  readonly span: SourceSpan;
}

export interface RecordDeclaration {
  readonly tag: "record";
  readonly declaration_id: string;
  readonly fields: readonly {
    readonly name: string;
    readonly sort: SortRef;
    readonly required: boolean;
    readonly span: SourceSpan;
  }[];
  readonly span: SourceSpan;
}

export interface FunctionDeclaration {
  readonly tag: "function";
  readonly declaration_id: string;
  readonly parameters: readonly ParameterDeclaration[];
  readonly result: SortRef;
  readonly body: LogicTerm;
  readonly span: SourceSpan;
}

export interface PredicateDeclaration {
  readonly tag: "predicate";
  readonly declaration_id: string;
  readonly parameters: readonly ParameterDeclaration[];
  readonly body: LogicTerm;
  readonly span: SourceSpan;
}

export interface FixtureUniverseDeclaration {
  readonly tag: "fixture-universe";
  readonly declaration_id: string;
  readonly element_sort: SortRef;
  readonly admits_empty: boolean;
  readonly span: SourceSpan;
}

export type LogicDeclaration =
  | EnumDeclaration
  | RecordDeclaration
  | FunctionDeclaration
  | PredicateDeclaration
  | FixtureUniverseDeclaration;

export type LogicDeclarationTag = LogicDeclaration["tag"];

export type LogicClauseKind =
  | "function"
  | "predicate"
  | "invariant"
  | "precondition"
  | "postcondition"
  | "transition"
  | "effect-relation";

export type LogicClauseStatus = "candidate" | "admitted";

export interface LogicClause {
  readonly clause_id: string;
  readonly kind: LogicClauseKind;
  readonly status: LogicClauseStatus;
  readonly inputs: readonly ParameterDeclaration[];
  readonly result_sort: SortRef;
  readonly expression: LogicTerm;
  readonly observation_sort: SortRef | null;
  readonly span: SourceSpan;
}

export interface LogicModuleSourceIdentity {
  readonly feature_id: string;
  readonly node_id: string;
  readonly source_id: string;
  readonly source_path: string;
}

export interface NodeLogicModuleV1 {
  readonly schema_version: NodeLogicSchemaVersion;
  readonly language_version: SfolLanguageVersion;
  readonly module_id: string;
  readonly source: LogicModuleSourceIdentity;
  readonly declarations: readonly LogicDeclaration[];
  readonly clauses: readonly LogicClause[];
}

export type NodeLogicModule = NodeLogicModuleV1;
