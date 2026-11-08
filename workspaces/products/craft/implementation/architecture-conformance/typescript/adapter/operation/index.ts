import { createHash } from "node:crypto";

import ts from "typescript";

export type OperationSourceInspectionV1 = Readonly<{
  supported: boolean;
  source_sha256: string;
  diagnostics: readonly string[];
  body_span: Readonly<{ start: number; length: number }> | null;
  observed_action_order: readonly string[];
}>;

const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");

export const inspectTypeScriptOperationSource = (input: Readonly<{
  source: string;
  modulePath: string;
  symbolName: string;
}>): OperationSourceInspectionV1 => {
  const file = ts.createSourceFile(input.modulePath, input.source,
    ts.ScriptTarget.ESNext, true, ts.ScriptKind.TS);
  const parseDiagnostics = (file as ts.SourceFile & {
    parseDiagnostics: readonly ts.Diagnostic[];
  }).parseDiagnostics;
  const diagnostics: string[] = parseDiagnostics.length > 0
    ? ["TS_OPERATION_PARSE_DIAGNOSTIC"] : [];
  const executable = file.statements.filter((item) => !ts.isTypeAliasDeclaration(item));
  const selected = executable.flatMap((statement) => {
    if (!ts.isVariableStatement(statement) ||
        !statement.modifiers?.some(({ kind }) => kind === ts.SyntaxKind.ExportKeyword) ||
        (statement.declarationList.flags & ts.NodeFlags.Const) === 0) return [];
    return statement.declarationList.declarations.filter((declaration) =>
      ts.isIdentifier(declaration.name) && declaration.name.text === input.symbolName);
  });
  let body: ts.Block | null = null;
  if (executable.length !== 1 || selected.length !== 1 ||
      !selected[0]?.initializer || !ts.isArrowFunction(selected[0].initializer) ||
      selected[0].initializer.parameters.length !== 2 ||
      !ts.isBlock(selected[0].initializer.body)) {
    diagnostics.push("TS_OPERATION_ARROW_SHAPE_UNSUPPORTED");
  } else {
    body = selected[0].initializer.body;
  }
  const actions: string[] = [];
  if (body) {
    for (const statement of body.statements) {
      if (!ts.isExpressionStatement(statement) || !ts.isCallExpression(statement.expression) ||
          !ts.isPropertyAccessExpression(statement.expression.expression) ||
          statement.expression.expression.name.text !== "push" ||
          !ts.isPropertyAccessExpression(statement.expression.expression.expression) ||
          !ts.isIdentifier(statement.expression.expression.expression.expression) ||
          statement.expression.expression.expression.expression.text !== "state") {
        diagnostics.push("TS_OPERATION_EFFECT_SHAPE_UNSUPPORTED");
        continue;
      }
      actions.push(statement.expression.expression.expression.name.text);
    }
    if (JSON.stringify(actions) !== JSON.stringify(["payouts", "events"])) {
      diagnostics.push("TS_OPERATION_EFFECT_ORDER_UNSUPPORTED");
    }
  }
  return Object.freeze({
    supported: diagnostics.length === 0,
    source_sha256: sha256(input.source),
    diagnostics: Object.freeze(diagnostics),
    body_span: body ? Object.freeze({
      start: body.getStart(file) + 1,
      length: body.getWidth(file) - 2,
    }) : null,
    observed_action_order: Object.freeze(actions),
  });
};

export const mutateTypeScriptOperationSource = (input: Readonly<{
  source: string;
  modulePath: string;
  symbolName: string;
  mutationId: "no-op" | "read-only";
}>): string => {
  const inspection = inspectTypeScriptOperationSource(input);
  if (!inspection.supported || !inspection.body_span) {
    throw Object.assign(new Error("TS_OPERATION_MUTATION_BASE_UNSUPPORTED"), {
      code: "TS_OPERATION_MUTATION_BASE_UNSUPPORTED",
    });
  }
  const replacement = input.mutationId === "no-op" ? "" :
    "\n  void state.payouts.length;\n  void state.events.length;\n";
  const { start, length } = inspection.body_span;
  return `${input.source.slice(0, start)}${replacement}${input.source.slice(start + length)}`;
};
