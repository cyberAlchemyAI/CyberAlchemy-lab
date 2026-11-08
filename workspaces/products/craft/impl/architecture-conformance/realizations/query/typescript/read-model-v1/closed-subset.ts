import {createHash} from "node:crypto";
import ts from "typescript";

import {
  DECLARED_READ_LIFECYCLE_PATHS,
  EFFECT_CHANNELS,
  type DeclaredReadLifecyclePathV1,
  type EffectChannelV1,
} from "../../../../kernel/evidence/effect-observation/index.js";

export type TypeScriptQueryClosedSubsetProofV1 = Readonly<{
  schema_version: "TypeScriptQueryClosedSubsetProof/v1";
  result: "pass";
  symbol_name: "readCompleteSettlement";
  source_sha256: string;
  ordered_read_targets: readonly [
    "settlement.read.settlement-by-id",
    "settlement.read.payout-by-settlement",
  ];
  output_fields: readonly [
    "settlement_id",
    "settlement_status",
    "gross_amount_minor",
    "payout_id",
    "payout_status",
  ];
  supported_effect_channels: readonly EffectChannelV1[];
  supported_lifecycle_paths: readonly DeclaredReadLifecyclePathV1[];
  lifecycle_basis:
    "native-promise-await-plus-closed-plain-data-result-static-exclusion";
  mechanism: "exact-ast-closed-subset-static-exclusion";
  authority_effect: "none";
}>;

export class TypeScriptQuerySubsetError extends Error {
  readonly code: string;

  constructor(code: string) {
    super(code);
    this.name = "TypeScriptQuerySubsetError";
    this.code = code;
  }
}

const fail = (code: string): never => {
  throw new TypeScriptQuerySubsetError(code);
};
const sha256 = (value: string): string => createHash("sha256")
  .update(value, "utf8")
  .digest("hex");
const hasModifier = (node: ts.Node, kind: ts.SyntaxKind): boolean =>
  ts.canHaveModifiers(node) &&
  (ts.getModifiers(node) ?? []).some((modifier) => modifier.kind === kind);
const identifier = (node: ts.Node | undefined, expected: string): void => {
  if (!node || !ts.isIdentifier(node) || node.text !== expected) {
    fail("TS_QUERY_CLOSED_SUBSET_IDENTIFIER");
  }
};
const settlementIdAccess = (
  node: ts.Expression,
  receiver: string,
): void => {
  if (!ts.isPropertyAccessExpression(node) ||
      ts.isPropertyAccessChain(node) ||
      !ts.isIdentifier(node.expression) || node.expression.text !== receiver ||
      node.name.text !== "settlement_id") {
    fail("TS_QUERY_CLOSED_SUBSET_AMBIENT_REFERENCE");
  }
};
const readStatement = (
  statement: ts.Statement,
  localName: string,
  targetId: string,
): void => {
  if (!ts.isVariableStatement(statement)) {
    fail("TS_QUERY_CLOSED_SUBSET_READ_STATEMENT");
  }
  const declarationList = (statement as ts.VariableStatement).declarationList;
  if ((declarationList.flags & ts.NodeFlags.Const) === 0 ||
      declarationList.declarations.length !== 1) {
    fail("TS_QUERY_CLOSED_SUBSET_READ_STATEMENT");
  }
  const declaration = declarationList.declarations[0];
  const initializer = declaration?.initializer;
  if (!declaration || declaration.type || !initializer) {
    fail("TS_QUERY_CLOSED_SUBSET_READ_STATEMENT");
  }
  identifier(declaration.name, localName);
  const initializerNode = initializer as ts.Expression;
  if (!ts.isAwaitExpression(initializerNode)) {
    fail("TS_QUERY_CLOSED_SUBSET_READ_CALL");
  }
  const awaited = initializerNode as ts.AwaitExpression;
  if (!ts.isCallExpression(awaited.expression)) {
    fail("TS_QUERY_CLOSED_SUBSET_READ_CALL");
  }
  const call = awaited.expression as ts.CallExpression;
  identifier(call.expression, "read");
  if (call.typeArguments || call.arguments.length !== 2 ||
      !ts.isStringLiteral(call.arguments[0]!) ||
      call.arguments[0]!.text !== targetId) {
    fail("TS_QUERY_CLOSED_SUBSET_READ_CALL");
  }
  settlementIdAccess(call.arguments[1]!, "input");
};
const outputAccess = (
  expression: ts.Expression,
  receiver: string,
  property: string,
): void => {
  if (!ts.isPropertyAccessExpression(expression) ||
      ts.isPropertyAccessChain(expression) ||
      !ts.isIdentifier(expression.expression) ||
      expression.expression.text !== receiver ||
      expression.name.text !== property) {
    fail("TS_QUERY_CLOSED_SUBSET_OUTPUT_EXPRESSION");
  }
};

export const inspectTypeScriptQueryClosedSubset = (
  source: string,
): TypeScriptQueryClosedSubsetProofV1 => {
  const file = ts.createSourceFile(
    "query-v1.ts",
    source,
    ts.ScriptTarget.ES2022,
    true,
    ts.ScriptKind.TS,
  );
  const parseDiagnostics = (file as ts.SourceFile & {
    readonly parseDiagnostics?: readonly ts.Diagnostic[];
  }).parseDiagnostics ?? [];
  if (parseDiagnostics.length > 0 || file.statements.length !== 1) {
    return fail("TS_QUERY_CLOSED_SUBSET_SOURCE_SHAPE");
  }
  const statement = file.statements[0];
  if (!statement || !ts.isVariableStatement(statement) ||
      !hasModifier(statement, ts.SyntaxKind.ExportKeyword) ||
      statement.declarationList.flags !== ts.NodeFlags.Const ||
      statement.declarationList.declarations.length !== 1) {
    return fail("TS_QUERY_CLOSED_SUBSET_EXPORT_SHAPE");
  }
  const declaration = statement.declarationList.declarations[0];
  if (!declaration || !ts.isIdentifier(declaration.name) ||
      declaration.name.text !== "readCompleteSettlement" ||
      !declaration.initializer ||
      !ts.isArrowFunction(declaration.initializer)) {
    return fail("TS_QUERY_CLOSED_SUBSET_CALLABLE_SHAPE");
  }
  const arrow = declaration.initializer;
  if (!hasModifier(arrow, ts.SyntaxKind.AsyncKeyword) ||
      arrow.parameters.length !== 2 || !ts.isBlock(arrow.body) ||
      arrow.body.statements.length !== 3) {
    return fail("TS_QUERY_CLOSED_SUBSET_SIGNATURE");
  }
  const [inputParameter, readParameter] = arrow.parameters;
  if (!inputParameter || !readParameter ||
      inputParameter.dotDotDotToken || inputParameter.questionToken ||
      inputParameter.initializer || readParameter.dotDotDotToken ||
      readParameter.questionToken || readParameter.initializer) {
    return fail("TS_QUERY_CLOSED_SUBSET_PARAMETER");
  }
  identifier(inputParameter.name, "input");
  identifier(readParameter.name, "read");
  readStatement(
    arrow.body.statements[0]!,
    "settlement",
    "settlement.read.settlement-by-id",
  );
  readStatement(
    arrow.body.statements[1]!,
    "payout",
    "settlement.read.payout-by-settlement",
  );
  const returnStatement = arrow.body.statements[2];
  if (!returnStatement || !ts.isReturnStatement(returnStatement) ||
      !returnStatement.expression ||
      !ts.isObjectLiteralExpression(returnStatement.expression) ||
      returnStatement.expression.properties.length !== 5) {
    return fail("TS_QUERY_CLOSED_SUBSET_OUTPUT_SHAPE");
  }
  const expected = [
    ["settlement_id", "input", "settlement_id"],
    ["settlement_status", "settlement", "settlement_status"],
    ["gross_amount_minor", "settlement", "gross_amount_minor"],
    ["payout_id", "payout", "payout_id"],
    ["payout_status", "payout", "payout_status"],
  ] as const;
  for (const [index, [name, receiver, property]] of expected.entries()) {
    const output = returnStatement.expression.properties[index];
    if (!output || !ts.isPropertyAssignment(output) ||
        !ts.isIdentifier(output.name) || output.name.text !== name) {
      return fail("TS_QUERY_CLOSED_SUBSET_OUTPUT_SHAPE");
    }
    outputAccess(output.initializer, receiver, property);
  }
  return Object.freeze({
    schema_version: "TypeScriptQueryClosedSubsetProof/v1" as const,
    result: "pass" as const,
    symbol_name: "readCompleteSettlement" as const,
    source_sha256: sha256(source),
    ordered_read_targets: Object.freeze([
      "settlement.read.settlement-by-id",
      "settlement.read.payout-by-settlement",
    ] as const),
    output_fields: Object.freeze([
      "settlement_id",
      "settlement_status",
      "gross_amount_minor",
      "payout_id",
      "payout_status",
    ] as const),
    supported_effect_channels: EFFECT_CHANNELS,
    supported_lifecycle_paths: DECLARED_READ_LIFECYCLE_PATHS,
    lifecycle_basis:
      "native-promise-await-plus-closed-plain-data-result-static-exclusion" as const,
    mechanism: "exact-ast-closed-subset-static-exclusion" as const,
    authority_effect: "none" as const,
  });
};
