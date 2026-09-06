import {createHash} from "node:crypto";
import ts from "typescript";

import {EFFECT_CHANNELS} from
  "../../../../kernel/evidence/effect-observation/index.js";

const REQUIRED_FACTS = Object.freeze([
  "amount_minor",
  "expedite_limit_minor",
  "expedite_requested",
  "manual_review_required",
] as const);
const REQUIRED_IDENTITIES = Object.freeze([
  "settlement.route.standard",
  "settlement.route.expedited",
  "settlement.route.manual-review",
] as const);
const FORBIDDEN_IDENTIFIERS = new Set([
  "Date", "Math", "performance", "process", "globalThis", "fetch",
  "WebSocket", "Promise", "setTimeout", "setInterval", "queueMicrotask",
  "FinalizationRegistry", "WeakRef", "require", "eval", "Function",
]);
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const sha256 = (value: string): string => createHash("sha256")
  .update(value, "utf8")
  .digest("hex");
const fail = (code: string): never => {
  throw Object.assign(new Error(code), {code});
};

export const inspectTypeScriptPolicyClosedSubset = (source: string) => {
  const file = ts.createSourceFile(
    "policy-v1.ts",
    source,
    ts.ScriptTarget.ES2022,
    true,
    ts.ScriptKind.TS,
  );
  const parseDiagnostics = (file as ts.SourceFile & {
    parseDiagnostics?: readonly ts.Diagnostic[];
  }).parseDiagnostics ?? [];
  if (parseDiagnostics.length !== 0) fail("TS_POLICY_SOURCE_PARSE_FAILED");
  if (file.statements.some((statement) =>
    ts.isImportDeclaration(statement) || ts.isExportDeclaration(statement))) {
    fail("TS_POLICY_IMPORT_OR_REEXPORT_FORBIDDEN");
  }
  const exportedVariables = file.statements.filter(ts.isVariableStatement)
    .filter((statement) => statement.modifiers?.some((modifier) =>
      modifier.kind === ts.SyntaxKind.ExportKeyword));
  const statement = exportedVariables[0];
  if (exportedVariables.length !== 1 || !statement ||
      statement.declarationList.declarations.length !== 1) {
    fail("TS_POLICY_EXACT_ONE_EXPORTED_CALLABLE_REQUIRED");
  }
  const declaration = statement.declarationList.declarations[0];
  if (!declaration || !ts.isIdentifier(declaration.name) ||
      declaration.name.text !== "selectSettlementRoute") {
    fail("TS_POLICY_CALLABLE_SHAPE_INVALID");
  }
  const initializer = declaration.initializer;
  if (!initializer || !ts.isArrowFunction(initializer) ||
      initializer.modifiers?.some((modifier) =>
        modifier.kind === ts.SyntaxKind.AsyncKeyword) ||
      initializer.parameters.length !== 1 ||
      !ts.isIdentifier(initializer.parameters[0]?.name) ||
      ts.isBlock(initializer.body)) {
    fail("TS_POLICY_CALLABLE_SHAPE_INVALID");
  }
  const arrow = initializer as ts.ArrowFunction;
  const parameter = arrow.parameters[0];
  const parameterName = (parameter.name as ts.Identifier).text;
  if (parameterName !== "input" || parameter.questionToken ||
      parameter.dotDotDotToken || !parameter.type ||
      arrow.questionToken || arrow.asteriskToken) {
    fail("TS_POLICY_PARAMETER_SHAPE_INVALID");
  }

  const facts = new Set<string>();
  const identities = new Set<string>();
  let conditionalCount = 0;
  let callCount = 0;
  const inspect = (node: ts.Node): void => {
    if (ts.isIdentifier(node) && FORBIDDEN_IDENTIFIERS.has(node.text)) {
      fail("TS_POLICY_FORBIDDEN_AMBIENT_IDENTIFIER");
    }
    if (ts.isCallExpression(node) || ts.isNewExpression(node) ||
        ts.isAwaitExpression(node) || ts.isYieldExpression(node) ||
        ts.isFunctionExpression(node) || ts.isClassExpression(node) ||
        ts.isDeleteExpression(node) || ts.isPostfixUnaryExpression(node) ||
        ts.isPrefixUnaryExpression(node)) {
      if (ts.isCallExpression(node)) callCount += 1;
      fail("TS_POLICY_EFFECT_OR_EXECUTION_SYNTAX_FORBIDDEN");
    }
    if (ts.isConditionalExpression(node)) conditionalCount += 1;
    if (ts.isPropertyAccessExpression(node) &&
        ts.isIdentifier(node.expression) && node.expression.text === parameterName) {
      if (node.questionDotToken) fail("TS_POLICY_OPTIONAL_ACCESS_FORBIDDEN");
      facts.add(node.name.text);
    }
    if (ts.isElementAccessExpression(node)) {
      fail("TS_POLICY_ELEMENT_ACCESS_FORBIDDEN");
    }
    if (ts.isStringLiteral(node) && node.text.startsWith("settlement.route.")) {
      identities.add(node.text);
    }
    ts.forEachChild(node, inspect);
  };
  inspect(arrow.body);
  const observedFacts = [...facts].sort(compareUtf8);
  const observedIdentities = [...identities].sort(compareUtf8);
  if (JSON.stringify(observedFacts) !==
      JSON.stringify([...REQUIRED_FACTS].sort(compareUtf8))) {
    fail("TS_POLICY_EXPLICIT_INPUT_COVERAGE_INVALID");
  }
  if (JSON.stringify(observedIdentities) !==
      JSON.stringify([...REQUIRED_IDENTITIES].sort(compareUtf8))) {
    fail("TS_POLICY_STRATEGY_IDENTITY_SET_INVALID");
  }
  if (conditionalCount !== 2 || callCount !== 0) {
    fail("TS_POLICY_BRANCH_OR_EXECUTION_SHAPE_INVALID");
  }
  return Object.freeze({
    schema_version: "TypeScriptPolicyClosedSubsetProof/v1" as const,
    source_sha256: sha256(source),
    exported_symbol: "selectSettlementRoute" as const,
    callable_form: "one-exported-synchronous-arrow-expression" as const,
    explicit_input_facts: Object.freeze(observedFacts),
    strategy_identities: Object.freeze(observedIdentities),
    conditional_branches: conditionalCount,
    target_call_expressions: callCount,
    supported_effect_channels: EFFECT_CHANNELS,
    proof_mechanism:
      "closed-selector-expression-static-rejection-plus-two-fresh-processes" as const,
    claim_ceiling:
      "exact admitted synchronous TypeScript selector expression over inert JSON owner cases; no arbitrary TypeScript, arbitrary callers, or OS interception claim" as const,
    authority_effect: "none" as const,
  });
};
