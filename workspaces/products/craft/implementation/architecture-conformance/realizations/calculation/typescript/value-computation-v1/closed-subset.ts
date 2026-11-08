import {createHash} from "node:crypto";
import ts from "typescript";

import {EFFECT_CHANNELS, type EffectChannelV1} from
  "../../../../kernel/evidence/effect-observation/index.js";

export type TypeScriptCalculationClosedSubsetProofV1 = Readonly<{
  schema_version: "TypeScriptCalculationClosedSubsetProof/v1";
  result: "pass";
  symbol_name: "calculateNetSettlement";
  source_sha256: string;
  parameter_name: string;
  input_fields: readonly ["gross_amount_minor", "fee_amount_minor"];
  operator: "subtract";
  output_kind: "primitive-number";
  supported_effect_channels: readonly EffectChannelV1[];
  mechanism: "closed-expression-static-rejection";
  authority_effect: "none";
}>;

export class TypeScriptCalculationSubsetError extends Error {
  readonly code: string;

  constructor(code: string) {
    super(code);
    this.name = "TypeScriptCalculationSubsetError";
    this.code = code;
  }
}

const fail = (code: string): never => {
  throw new TypeScriptCalculationSubsetError(code);
};
const sha256 = (value: string): string => createHash("sha256")
  .update(value, "utf8")
  .digest("hex");
const hasModifier = (
  node: ts.Node,
  kind: ts.SyntaxKind,
): boolean => ts.canHaveModifiers(node)
  && (ts.getModifiers(node) ?? []).some((modifier) => modifier.kind === kind);

export const inspectTypeScriptCalculationClosedSubset = (
  source: string,
): TypeScriptCalculationClosedSubsetProofV1 => {
  const file = ts.createSourceFile(
    "calculation-v1.ts",
    source,
    ts.ScriptTarget.ES2022,
    true,
    ts.ScriptKind.TS,
  );
  const parseDiagnostics = (file as ts.SourceFile & {
    readonly parseDiagnostics?: readonly ts.Diagnostic[];
  }).parseDiagnostics ?? [];
  if (parseDiagnostics.length > 0 || file.statements.length !== 1) {
    return fail("TS_CALC_CLOSED_SUBSET_SOURCE_SHAPE");
  }
  const statement = file.statements[0];
  if (!statement || !ts.isVariableStatement(statement)
      || !hasModifier(statement, ts.SyntaxKind.ExportKeyword)
      || statement.declarationList.flags !== ts.NodeFlags.Const
      || statement.declarationList.declarations.length !== 1) {
    return fail("TS_CALC_CLOSED_SUBSET_EXPORT_SHAPE");
  }
  const declaration = statement.declarationList.declarations[0];
  if (!declaration || !ts.isIdentifier(declaration.name)
      || declaration.name.text !== "calculateNetSettlement"
      || !declaration.initializer || !ts.isArrowFunction(declaration.initializer)) {
    return fail("TS_CALC_CLOSED_SUBSET_CALLABLE_SHAPE");
  }
  const arrow = declaration.initializer;
  if (hasModifier(arrow, ts.SyntaxKind.AsyncKeyword)
      || arrow.parameters.length !== 1 || !arrow.type
      || arrow.type.kind !== ts.SyntaxKind.NumberKeyword
      || ts.isBlock(arrow.body)) {
    return fail("TS_CALC_CLOSED_SUBSET_SIGNATURE");
  }
  const parameter = arrow.parameters[0];
  if (!parameter || !ts.isIdentifier(parameter.name) || !parameter.type
      || parameter.dotDotDotToken || parameter.questionToken || parameter.initializer) {
    return fail("TS_CALC_CLOSED_SUBSET_PARAMETER");
  }
  const parameterType = parameter.type;
  if (!ts.isTypeReferenceNode(parameterType)
      || !ts.isIdentifier(parameterType.typeName)
      || parameterType.typeName.text !== "Readonly"
      || parameterType.typeArguments?.length !== 1) {
    return fail("TS_CALC_CLOSED_SUBSET_PARAMETER_TYPE");
  }
  const inputShape = parameterType.typeArguments[0];
  if (!inputShape || !ts.isTypeLiteralNode(inputShape)
      || inputShape.members.length !== 2) {
    return fail("TS_CALC_CLOSED_SUBSET_PARAMETER_TYPE");
  }
  const expectedFields = ["gross_amount_minor", "fee_amount_minor"] as const;
  for (const [index, member] of inputShape.members.entries()) {
    if (!ts.isPropertySignature(member) || !member.type
        || member.type.kind !== ts.SyntaxKind.NumberKeyword
        || member.questionToken
        || (member.modifiers?.length ?? 0) !== 0
        || !ts.isIdentifier(member.name) || member.name.text !== expectedFields[index]) {
      return fail("TS_CALC_CLOSED_SUBSET_PARAMETER_TYPE");
    }
  }
  const parameterName = parameter.name.text;
  const body = arrow.body;
  if (!ts.isBinaryExpression(body)
      || body.operatorToken.kind !== ts.SyntaxKind.MinusToken) {
    return fail("TS_CALC_CLOSED_SUBSET_EXPRESSION");
  }
  const readField = (expression: ts.Expression): string => {
    if (!ts.isPropertyAccessExpression(expression)
        || ts.isPropertyAccessChain(expression)
        || !ts.isIdentifier(expression.expression)
        || expression.expression.text !== parameterName) {
      return fail("TS_CALC_CLOSED_SUBSET_AMBIENT_REFERENCE");
    }
    return expression.name.text;
  };
  const fields = [readField(body.left), readField(body.right)] as const;
  if (fields[0] !== "gross_amount_minor" || fields[1] !== "fee_amount_minor") {
    return fail("TS_CALC_CLOSED_SUBSET_INPUT_FIELD");
  }
  return Object.freeze({
    schema_version: "TypeScriptCalculationClosedSubsetProof/v1" as const,
    result: "pass" as const,
    symbol_name: "calculateNetSettlement" as const,
    source_sha256: sha256(source),
    parameter_name: parameterName,
    input_fields: Object.freeze([
      "gross_amount_minor",
      "fee_amount_minor",
    ] as const),
    operator: "subtract" as const,
    output_kind: "primitive-number" as const,
    supported_effect_channels: EFFECT_CHANNELS,
    mechanism: "closed-expression-static-rejection" as const,
    authority_effect: "none" as const,
  });
};
