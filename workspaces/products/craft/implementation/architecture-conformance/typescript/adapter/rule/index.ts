import { createHash } from "node:crypto";

import ts from "typescript";

export type TypeScriptRuleSourceInspectionV1 = Readonly<{
  schema_version: "TypeScriptRuleSourceInspection/v1";
  source_sha256: string;
  symbol_name: string;
  supported: boolean;
  diagnostics: readonly Readonly<{ code: string; message: string }>[];
  expression_span: Readonly<{ start: number; length: number }> | null;
  authority_effect: "none";
}>;

const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");
const diagnostic = (code: string, message: string) => Object.freeze({ code, message });

const parseDiagnostics = (sourceFile: ts.SourceFile): readonly ts.Diagnostic[] =>
  (sourceFile as ts.SourceFile & {
    readonly parseDiagnostics: readonly ts.Diagnostic[];
  }).parseDiagnostics;

const isPureExpression = (node: ts.Expression, parameterName: string): boolean => {
  if (ts.isParenthesizedExpression(node)) return isPureExpression(node.expression, parameterName);
  if (ts.isIdentifier(node)) return node.text === parameterName;
  if (ts.isPropertyAccessExpression(node)) {
    return isPureExpression(node.expression, parameterName);
  }
  if (ts.isStringLiteral(node) || ts.isNumericLiteral(node) ||
      node.kind === ts.SyntaxKind.TrueKeyword || node.kind === ts.SyntaxKind.FalseKeyword ||
      node.kind === ts.SyntaxKind.NullKeyword) return true;
  if (ts.isPrefixUnaryExpression(node)) {
    return node.operator === ts.SyntaxKind.ExclamationToken &&
      isPureExpression(node.operand, parameterName);
  }
  if (ts.isBinaryExpression(node)) {
    const admitted = new Set([
      ts.SyntaxKind.AmpersandAmpersandToken,
      ts.SyntaxKind.BarBarToken,
      ts.SyntaxKind.EqualsEqualsEqualsToken,
      ts.SyntaxKind.ExclamationEqualsEqualsToken,
      ts.SyntaxKind.GreaterThanToken,
      ts.SyntaxKind.GreaterThanEqualsToken,
      ts.SyntaxKind.LessThanToken,
      ts.SyntaxKind.LessThanEqualsToken,
    ]);
    return admitted.has(node.operatorToken.kind) &&
      isPureExpression(node.left, parameterName) &&
      isPureExpression(node.right, parameterName);
  }
  return false;
};

export const inspectTypeScriptRuleSource = (input: Readonly<{
  modulePath: string;
  source: string;
  symbolName: string;
}>): TypeScriptRuleSourceInspectionV1 => {
  const sourceFile = ts.createSourceFile(
    input.modulePath,
    input.source,
    ts.ScriptTarget.ESNext,
    true,
    ts.ScriptKind.TS,
  );
  const diagnostics: Array<Readonly<{ code: string; message: string }>> = [];
  for (const item of parseDiagnostics(sourceFile)) {
    diagnostics.push(diagnostic(
      "TS_RULE_PARSE_DIAGNOSTIC",
      `TS${item.code}: ${ts.flattenDiagnosticMessageText(item.messageText, " ")}`,
    ));
  }
  const executable = sourceFile.statements.filter((statement) =>
    !ts.isTypeAliasDeclaration(statement) && !ts.isInterfaceDeclaration(statement));
  const selected = executable.flatMap((statement) => {
    if (!ts.isVariableStatement(statement) ||
        !statement.modifiers?.some(({ kind }) => kind === ts.SyntaxKind.ExportKeyword) ||
        (statement.declarationList.flags & ts.NodeFlags.Const) === 0) return [];
    return statement.declarationList.declarations.filter((declaration) =>
      ts.isIdentifier(declaration.name) && declaration.name.text === input.symbolName);
  });
  let body: ts.Expression | null = null;
  if (executable.length !== 1 || selected.length !== 1) {
    diagnostics.push(diagnostic(
      "TS_RULE_MODULE_SHAPE_UNSUPPORTED",
      "module must contain only type declarations and one selected exported const",
    ));
  } else {
    const initializer = selected[0]?.initializer;
    if (!initializer || !ts.isArrowFunction(initializer) ||
        initializer.modifiers?.some(({ kind }) => kind === ts.SyntaxKind.AsyncKeyword) ||
        initializer.parameters.length !== 1 ||
        !ts.isIdentifier(initializer.parameters[0]!.name) ||
        initializer.type?.kind !== ts.SyntaxKind.BooleanKeyword ||
        ts.isBlock(initializer.body)) {
      diagnostics.push(diagnostic(
        "TS_RULE_ARROW_SHAPE_UNSUPPORTED",
        "selected export must be a synchronous one-parameter arrow with explicit boolean return and expression body",
      ));
    } else {
      body = initializer.body;
      const parameter = initializer.parameters[0]!.name;
      if (!isPureExpression(body, parameter.text)) {
        diagnostics.push(diagnostic(
          "TS_RULE_EXPRESSION_UNSUPPORTED",
          "Rule expression must use only its input, property reads, literals, boolean comparisons, and boolean operators",
        ));
      }
    }
  }
  return Object.freeze({
    schema_version: "TypeScriptRuleSourceInspection/v1" as const,
    source_sha256: sha256(input.source),
    symbol_name: input.symbolName,
    supported: diagnostics.length === 0,
    diagnostics: Object.freeze(diagnostics),
    expression_span: body === null ? null : Object.freeze({
      start: body.getStart(sourceFile),
      length: body.getWidth(sourceFile),
    }),
    authority_effect: "none" as const,
  });
};
