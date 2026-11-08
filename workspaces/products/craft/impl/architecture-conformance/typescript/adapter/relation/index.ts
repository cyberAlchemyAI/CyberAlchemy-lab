import ts from "typescript";

const RULE_IMPORT = "../../../../rule/typescript/bound-arrow-function-v1/fixtures/can-settle-payout.js";
const OPERATION_IMPORT = "../../../../operation/typescript/state-event-arrow-v1/fixtures/complete-settlement.js";

export const inspectEnforcesCompositionSource = (source: string): Readonly<{
  supported: boolean;
  diagnostics: readonly string[];
}> => {
  const file = ts.createSourceFile("settle-payout.ts", source,
    ts.ScriptTarget.ESNext, true, ts.ScriptKind.TS);
  const diagnostics: string[] = (file as ts.SourceFile & {
    parseDiagnostics: readonly ts.Diagnostic[];
  }).parseDiagnostics.length > 0 ? ["TS_RELATION_PARSE_DIAGNOSTIC"] : [];
  const imports = file.statements.filter(ts.isImportDeclaration)
    .map((item) => ts.isStringLiteral(item.moduleSpecifier)
      ? item.moduleSpecifier.text : "");
  if (JSON.stringify(imports) !== JSON.stringify([RULE_IMPORT, OPERATION_IMPORT])) {
    diagnostics.push("TS_RELATION_DIRECT_IMPORTS_UNSUPPORTED");
  }
  const selected = file.statements.flatMap((statement) => {
    if (!ts.isVariableStatement(statement) ||
        !statement.modifiers?.some(({ kind }) => kind === ts.SyntaxKind.ExportKeyword)) return [];
    return statement.declarationList.declarations.filter((item) =>
      ts.isIdentifier(item.name) && item.name.text === "settlePayout");
  });
  const arrow = selected[0]?.initializer;
  if (selected.length !== 1 || !arrow || !ts.isArrowFunction(arrow) || !ts.isBlock(arrow.body) ||
      arrow.parameters.length !== 4) {
    diagnostics.push("TS_RELATION_ARROW_SHAPE_UNSUPPORTED");
  } else {
    const body = arrow.body.getText(file).replaceAll(/\s+/gu, " ");
    const guard = body.indexOf("if (!rule(input)) return false;");
    const operation = body.indexOf("operation(state, input);");
    const returned = body.indexOf("return true;");
    if (guard < 0 || operation < 0 || returned < 0 || !(guard < operation && operation < returned)) {
      diagnostics.push("TS_RELATION_CALL_ORDER_UNSUPPORTED");
    }
  }
  return Object.freeze({ supported: diagnostics.length === 0, diagnostics: Object.freeze(diagnostics) });
};

export const mutateEnforcesCompositionSource = (
  source: string,
  defect: "bypass-rule" | "mutation-before-rule",
): string => {
  const inspection = inspectEnforcesCompositionSource(source);
  if (!inspection.supported) throw new Error("TS_RELATION_MUTATION_BASE_UNSUPPORTED");
  const guard = "  if (!rule(input)) return false;\n";
  if (source.split(guard).length !== 2) throw new Error("TS_RELATION_MUTATION_NOT_APPLICABLE");
  if (defect === "bypass-rule") return source.replace(guard, "");
  const operation = "  operation(state, input);\n";
  return source.replace(`${guard}${operation}`, `${operation}${guard}`);
};
