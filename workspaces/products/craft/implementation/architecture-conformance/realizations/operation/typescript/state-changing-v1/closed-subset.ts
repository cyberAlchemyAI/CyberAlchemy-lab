import {createHash} from "node:crypto";
import ts from "typescript";

import type {OperationFindingCode} from
  "../../../../families/state-changing-action/contracts/state-changing-action-contracts.js";

export const TYPESCRIPT_OPERATION_OBSERVER_ID =
  "observer.typescript-operation-ports/v1" as const;

export type TypeScriptOperationSourceControlV1 = Readonly<{
  control_id: string;
  expected_code: OperationFindingCode;
}>;

export const TYPESCRIPT_OPERATION_SOURCE_CONTROLS:
readonly TypeScriptOperationSourceControlV1[] = Object.freeze([
  {control_id: "ts-op/undeclared-write",
    expected_code: "RMT_OP_UNDECLARED_WRITE"},
  {control_id: "ts-op/undeclared-effect",
    expected_code: "RMT_OP_UNDECLARED_EFFECT"},
  {control_id: "ts-op/guard-bypass",
    expected_code: "RMT_OP_GUARD_BYPASS"},
  {control_id: "ts-op/order-swap",
    expected_code: "RMT_OP_ORDER_SWAP"},
  {control_id: "ts-op/atomicity-removed",
    expected_code: "RMT_OP_ATOMICITY_REMOVED"},
  {control_id: "ts-op/success-failure-collapse",
    expected_code: "RMT_OP_SUCCESS_FAILURE_COLLAPSE"},
  {control_id: "ts-op/emitted-before-commit",
    expected_code: "RMT_OP_EMITTED_BEFORE_COMMIT"},
  {control_id: "ts-op/continuation-mismatch",
    expected_code: "RMT_OP_CONTINUATION_MISMATCH"},
  {control_id: "ts-op/read-set-drift",
    expected_code: "RMT_OP_READ_SET_DRIFT"},
  {control_id: "ts-op/output-contract-overclaim",
    expected_code: "RMT_OP_OUTPUT_CONTRACT_OVERCLAIM"},
]);

export type TypeScriptOperationClosedSubsetProofV1 = Readonly<{
  schema_version: "TypeScriptOperationClosedSubsetProof/v1";
  result: "pass";
  symbol_name: "completeSettlementOperation";
  source_sha256: string;
  observer_id: typeof TYPESCRIPT_OPERATION_OBSERVER_ID;
  admitted_form:
    "exported-async-arrow-with-explicit-input-and-injected-operation-ports";
  source_control_count: 10;
  ambient_dependencies: readonly [];
  authority_effect: "none";
}>;

export class TypeScriptOperationSubsetError extends Error {
  readonly code: string;

  constructor(code: string) {
    super(code);
    this.name = "TypeScriptOperationSubsetError";
    this.code = code;
  }
}

const fail = (code: string): never => {
  throw new TypeScriptOperationSubsetError(code);
};
const sha256 = (value: string): string => createHash("sha256")
  .update(value, "utf8").digest("hex");
const hasModifier = (
  node: ts.Node,
  kind: ts.SyntaxKind,
): boolean => ts.canHaveModifiers(node) &&
  (ts.getModifiers(node) ?? []).some((modifier) => modifier.kind === kind);

export const inspectTypeScriptOperationClosedSubset = (
  source: string,
): TypeScriptOperationClosedSubsetProofV1 => {
  const file = ts.createSourceFile(
    "operation-v1.ts",
    source,
    ts.ScriptTarget.ES2022,
    true,
    ts.ScriptKind.TS,
  );
  const parseDiagnostics = (file as ts.SourceFile & {
    readonly parseDiagnostics?: readonly ts.Diagnostic[];
  }).parseDiagnostics ?? [];
  if (parseDiagnostics.length > 0 ||
      file.statements.some((statement) =>
        ts.isImportDeclaration(statement) ||
        ts.isExportDeclaration(statement))) {
    return fail("TS_OP_CLOSED_SUBSET_SOURCE_SHAPE");
  }
  let target: ts.ArrowFunction | null = null;
  for (const statement of file.statements) {
    if (!ts.isVariableStatement(statement) ||
        !hasModifier(statement, ts.SyntaxKind.ExportKeyword)) continue;
    for (const declaration of statement.declarationList.declarations) {
      if (ts.isIdentifier(declaration.name) &&
          declaration.name.text === "completeSettlementOperation" &&
          declaration.initializer &&
          ts.isArrowFunction(declaration.initializer)) {
        target = declaration.initializer;
      }
    }
  }
  if (!target || !hasModifier(target, ts.SyntaxKind.AsyncKeyword) ||
      target.parameters.length !== 2 || !ts.isBlock(target.body)) {
    return fail("TS_OP_CLOSED_SUBSET_CALLABLE_SHAPE");
  }
  const banned = new Set([
    "Date", "eval", "fetch", "globalThis", "process", "require", "setInterval",
    "setTimeout", "WeakRef",
  ]);
  let bannedObserved = false;
  const visit = (node: ts.Node): void => {
    if (ts.isIdentifier(node) && banned.has(node.text)) bannedObserved = true;
    if (ts.isPropertyAccessExpression(node) &&
        ts.isIdentifier(node.expression) &&
        node.expression.text === "Math" && node.name.text === "random") {
      bannedObserved = true;
    }
    ts.forEachChild(node, visit);
  };
  visit(file);
  if (bannedObserved) return fail("TS_OP_CLOSED_SUBSET_AMBIENT_DEPENDENCY");
  for (const required of [
    "rule.can-settle-payout",
    "settlement.read.settlement-by-id",
    "settlement.read.payout-account",
    "settlement.write.payout-record",
    "settlement.write.settlement-status",
    "event-store.append.PayoutCreated",
    "return-await-cancel-close-dispose-finalizer-quiescence",
  ]) {
    if (!source.includes(required)) {
      return fail("TS_OP_CLOSED_SUBSET_DECLARED_PORT_MISSING");
    }
  }
  return Object.freeze({
    schema_version: "TypeScriptOperationClosedSubsetProof/v1" as const,
    result: "pass" as const,
    symbol_name: "completeSettlementOperation" as const,
    source_sha256: sha256(source),
    observer_id: TYPESCRIPT_OPERATION_OBSERVER_ID,
    admitted_form:
      "exported-async-arrow-with-explicit-input-and-injected-operation-ports" as const,
    source_control_count: 10 as const,
    ambient_dependencies: Object.freeze([]) as readonly [],
    authority_effect: "none" as const,
  });
};

const replaceOnce = (
  source: string,
  needle: string,
  replacement: string,
  controlId: string,
): string => {
  const first = source.indexOf(needle);
  if (first < 0 || source.indexOf(needle, first + needle.length) >= 0) {
    return fail(`TS_OP_SOURCE_CONTROL_TARGET_INVALID:${controlId}`);
  }
  return source.slice(0, first) + replacement +
    source.slice(first + needle.length);
};

export const applyTypeScriptOperationSourceControl = (
  source: string,
  controlId: string,
): string => {
  let mutated: string;
  if (controlId === "ts-op/undeclared-write") {
    const commit = "    await transaction.commit();";
    mutated = replaceOnce(source, commit, `    await transaction.write(
      "settlement.write.undeclared-audit-row" as never,
      {settlement_id: input.settlement_id},
    );
${commit}`, controlId);
  } else if (controlId === "ts-op/undeclared-effect") {
    const close = `  await ports.close(
    "return-await-cancel-close-dispose-finalizer-quiescence",
    null,
  );`;
    mutated = replaceOnce(source, close, `  await ports.externalEffect(
    "network.send.undeclared-webhook" as never,
    {event_type: "PayoutCreated", settlement_id: input.settlement_id,
      payout_id: payoutId},
  );
${close}`, controlId);
  } else if (controlId === "ts-op/guard-bypass") {
    mutated = replaceOnce(
      source,
      "  if (!guard.allowed) {",
      "  if (false && !guard.allowed) {",
      controlId,
    );
  } else if (controlId === "ts-op/order-swap") {
    const first = `    settlement = await ports.read(
      "settlement.read.settlement-by-id",
      input.settlement_id,
    );`;
    const second = `    payoutAccount = await ports.read(
      "settlement.read.payout-account",
      input.settlement_id,
    );`;
    mutated = replaceOnce(source, first, "__TS_OP_READ_ONE__", controlId);
    mutated = replaceOnce(mutated, second, first, controlId);
    mutated = replaceOnce(mutated, "__TS_OP_READ_ONE__", second, controlId);
  } else if (controlId === "ts-op/atomicity-removed") {
    mutated = replaceOnce(
      source,
      "    await transaction.commit();",
      "    await transaction.commit(\"best-effort\");",
      controlId,
    );
  } else if (controlId === "ts-op/success-failure-collapse") {
    mutated = replaceOnce(
      source,
      '    return failure("guard-rejected");',
      `    return Object.freeze({
      kind: "failure",
      value: {settlement_id: input.settlement_id,
        payout_id: "forbidden", status: "committed"},
      failure_code: "guard-rejected",
      exactly_once_distributed_delivery_claimed: false,
    }) as never;`,
      controlId,
    );
  } else if (controlId === "ts-op/emitted-before-commit") {
    const commit = "    await transaction.commit();";
    mutated = replaceOnce(source, commit, `    await ports.externalEffect(
      "event-store.append.PayoutCreated",
      {event_type: "PayoutCreated", settlement_id: input.settlement_id,
        payout_id: payoutId},
    );
${commit}`, controlId);
  } else if (controlId === "ts-op/continuation-mismatch") {
    const closure = "return-await-cancel-close-dispose-finalizer-quiescence";
    mutated = source.split(closure).join(`${closure}-mismatch`);
  } else if (controlId === "ts-op/read-set-drift") {
    const begin = "  const transaction = await ports.beginAtomic();";
    mutated = replaceOnce(source, begin, `  await ports.read(
    "settlement.read.undeclared-audit-log" as never,
    input.settlement_id,
  );
${begin}`, controlId);
  } else if (controlId === "ts-op/output-contract-overclaim") {
    mutated = source.split(
      "exactly_once_distributed_delivery_claimed: false",
    ).join("exactly_once_distributed_delivery_claimed: true");
  } else {
    return fail(`TS_OP_SOURCE_CONTROL_UNKNOWN:${controlId}`);
  }
  if (sha256(mutated) === sha256(source)) {
    return fail(`TS_OP_SOURCE_CONTROL_NOOP:${controlId}`);
  }
  return mutated;
};
